"""Merge the annotator output shards with the precomputed meta into one table.
Every line is re-validated through the Pydantic model, so only clean rows land in
the parquet and anything malformed is counted and reported.

    uv run --with pandas --with pyarrow --with pydantic python pred-2/merge_annotations.py

Robust to missing out_*.jsonl shards (reports them), so it works on a partial run
for a progress check or at the end for the full 21,803-row table.
"""
import json
from pathlib import Path
import pandas as pd
from pydantic import ValidationError
from annotation_model import Annotation

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "pred-2" / "work"
SH = WORK / "shards"
OUT = ROOT / "pred-2" / "thread_annotations.parquet"
LISTCOLS = ("participants", "entities", "topics")

meta = {}
shard_files = sorted(SH.glob("shard_*.jsonl"))
for f in shard_files:
    for line in open(f):
        r = json.loads(line)
        meta[r["thread_id"]] = {"subject": r["subject"], **r["meta"]}

rows, missing, bad_json, invalid = [], [], 0, 0
for s in range(len(shard_files)):
    of = WORK / f"out_{s:03d}.jsonl"
    if not of.exists():
        missing.append(s); continue
    for line in open(of):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            bad_json += 1; continue
        try:
            a = Annotation.model_validate(obj)
        except ValidationError:
            invalid += 1; continue
        d = a.model_dump()
        m = meta.get(a.thread_id, {})
        row = {k: d[k] for k in d if k not in LISTCOLS}
        for c in LISTCOLS:
            row[c] = json.dumps(d[c], ensure_ascii=False)
        row["subject"] = m.get("subject")
        for k in ("n_messages", "n_real", "n_senders", "span_days", "date",
                  "involves_keep_owner", "involves_executive", "generic_subject",
                  "external_party", "truncated"):
            row[k] = m.get(k)
        rows.append(row)

df = pd.DataFrame(rows).drop_duplicates("thread_id").sort_values("thread_id").reset_index(drop=True)
df.to_parquet(OUT, index=False)
done = len(shard_files) - len(missing)
print(f"merged {len(df):,} valid annotations from {done}/{len(shard_files)} shards -> {OUT}")
if bad_json or invalid:
    print(f"  dropped {bad_json} unparseable + {invalid} schema-invalid line(s)")
if missing:
    print(f"  MISSING out files for {len(missing)} shards: {missing[:20]}{' ...' if len(missing) > 20 else ''}")
print("\ncategory counts:\n" + df["category"].value_counts().to_string())
print("\noutcome counts:\n" + df["outcome"].value_counts().to_string())
