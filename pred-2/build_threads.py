"""Select the summarizable threads, assemble each as model-ready text, and shard
them for the annotator subagents. Deterministic, no LLM. See ANNOTATION_SCHEMA.md.

    uv run --with pandas --with pyarrow python pred-2/build_threads.py
"""
import json, re
from pathlib import Path
import pandas as pd, numpy as np

ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "eda-5" / "clean"
REFS = ROOT / "eda-5" / "refs"
WORK = ROOT / "pred-2" / "work"
SHARDS = WORK / "shards"
SHARDS.mkdir(parents=True, exist_ok=True)

SHARD_SIZE = 100
CHAR_BUDGET = 24000          # ~6k tokens; longer threads get truncated + flagged

m = pd.read_parquet(CLEAN / "messages_clean.parquet", columns=[
    "thread_id", "thread_size", "thread_position", "from_addr_norm", "from_domain",
    "is_internal_sender", "has_list_recipient", "body_is_boilerplate",
    "body_empty_after_clean", "body", "canon_subject", "thread_span_days",
    "sender_person", "recipient_count", "date"])
roles = pd.read_parquet(CLEAN / "people_roles.parquet").set_index("owner")
NAME = {o: str(roles.loc[o, "display_name"]) for o in roles.index}
TITLE = {o: (None if pd.isna(roles.loc[o, "title"]) else str(roles.loc[o, "title"])) for o in roles.index}
EXEC = {o: bool(roles.loc[o, "is_executive"]) for o in roles.index}

# --- pc5 automated/newsletter classifier (verbatim from pred-1) -------------- #
AUTO = re.compile(r"(?:^|[._-])(?:noreply|no-?reply|donotreply|mailer|postmaster|root|daemon|bounce|"
    r"listserv|majordomo|arsystem|notification|notify|alerts?|updates?|news|newsletter|digest|info|"
    r"marketing|feedback|announce|automated|webmaster|service|press|editor|newsdesk|delivery|robot|"
    r"exchangeinfo|issuealert|strat_alert|crcommunications|fool|owner)(?:[._-]|@|$)")
loc = m["from_addr_norm"].fillna("").str.split("@").str[0]
dm = m["from_domain"].fillna("")
m["auto"] = ((~m["is_internal_sender"].fillna(True)) & (loc.str.contains(AUTO, na=False)
    | dm.str.contains(r"mailman|lists?\.|listserv", na=False) | loc.str.match(r".*-request$", na=False))) \
    | m["has_list_recipient"].fillna(False) | m["body_is_boilerplate"].fillna(False)
m["real"] = ~m["body_empty_after_clean"] & ~m["body_is_boilerplate"] & ~m["auto"]

# --- keep-set (the 142 profiled owners) + executives among them -------------- #
DEL = set(pd.read_csv(REFS / "assistant_delegates.csv", sep=";")["assistant_addr"])
au = m[m["sender_person"].notna() & ~m["from_addr_norm"].isin(DEL)]
KEEP = set(au.groupby("sender_person").size().pipe(lambda s: s[s >= 30]).index)
KEEP_EXEC = {o for o in KEEP if EXEC.get(o)}

# --- summarizable set: >=2 distinct senders AND >=2 real messages ------------ #
multi = m[m["thread_size"] >= 2]
g = multi.groupby("thread_id")
agg = g.agg(n_msg=("thread_position", "size"), n_real=("real", "sum"),
            n_send=("from_addr_norm", "nunique"), span=("thread_span_days", "max"),
            subj=("canon_subject", "first"))
sel = agg[(agg.n_send >= 2) & (agg.n_real >= 2)]
subj_threads = multi.groupby("canon_subject")["thread_id"].nunique()
GENERIC = set(subj_threads[subj_threads >= 10].index) | {s for s in subj_threads.index if len(str(s).split()) <= 1}

keep_ids = sorted(sel.index)
print(f"summarizable threads: {len(keep_ids):,}")

sub = multi[multi.thread_id.isin(set(keep_ids))].sort_values(["thread_id", "thread_position", "date"])

def sender_label(row):
    sp = row.sender_person
    if pd.notna(sp) and sp in NAME:
        t = TITLE.get(sp)
        return f"{NAME[sp]}" + (f" ({t})" if t else "")
    return str(row.from_addr_norm) or "unknown"

def build(tid, df):
    parts, used, truncated = [], 0, False
    for i, (_, r) in enumerate(df.iterrows(), 1):
        body = re.sub(r"[ \t]+", " ", str(r.body or "")).strip()
        if not body:
            body = "(forwarded or replied with no added text)"
        block = f"[{i}] {sender_label(r)} -> {int(r.recipient_count)} recipient(s):\n{body}"
        if used + len(block) > CHAR_BUDGET and parts:
            truncated = True
            break
        parts.append(block); used += len(block)
    people = set(df.sender_person.dropna())
    dates = pd.to_datetime(df.date, errors="coerce").dropna()
    a = agg.loc[tid]
    meta = {
        "n_messages": int(a.n_msg), "n_real": int(a.n_real), "n_senders": int(a.n_send),
        "span_days": int(a.span) if pd.notna(a.span) else None,
        "date": (str(dates.min().date()) if len(dates) else None),
        "involves_keep_owner": bool(people & KEEP),
        "involves_executive": bool(people & KEEP_EXEC),
        "generic_subject": bool(a.subj in GENERIC),
        "external_party": bool((~df.is_internal_sender.fillna(True)).any()),
        "truncated": truncated,
    }
    return {"thread_id": int(tid), "subject": str(a.subj), "meta": meta,
            "text": "\n\n".join(parts)}

records = [build(tid, df) for tid, df in sub.groupby("thread_id", sort=True)]
records.sort(key=lambda r: r["thread_id"])

n_shards = (len(records) + SHARD_SIZE - 1) // SHARD_SIZE
for s in range(n_shards):
    chunk = records[s * SHARD_SIZE:(s + 1) * SHARD_SIZE]
    with open(SHARDS / f"shard_{s:03d}.jsonl", "w") as f:
        for rec in chunk:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

manifest = {"n_threads": len(records), "n_shards": n_shards, "shard_size": SHARD_SIZE,
            "scope": ">=2 distinct senders AND >=2 real messages", "char_budget": CHAR_BUDGET,
            "truncated_threads": int(sum(r["meta"]["truncated"] for r in records)),
            "involves_executive": int(sum(r["meta"]["involves_executive"] for r in records)),
            "generic_subject": int(sum(r["meta"]["generic_subject"] for r in records))}
(WORK / "manifest.json").write_text(json.dumps(manifest, indent=2))
print(json.dumps(manifest, indent=2))
print(f"wrote {n_shards} shards to {SHARDS}")
