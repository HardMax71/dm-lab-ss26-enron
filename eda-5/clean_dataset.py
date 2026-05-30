# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "pyarrow", "numpy"]
# ///
"""Clean and streamline the Enron corpus into deduplicated parquet tables.

Run from the repo root:

    uv run eda-5/clean_dataset.py

Reads the raw maildir (enron_mail/) and the cached header tables in
eda-2/cache/, writes:

    eda-5/clean/messages_clean.parquet     one row per unique message
    eda-5/clean/recipients_clean.parquet   one row per (message, recipient)
    eda-5/clean/clean_stats.json           machine-readable run statistics

Pipeline stages, each printed as it runs:
  1. dedup 517k files to unique messages, choose a canonical copy
  2. parse + clean the canonical message bodies from the raw maildir
  3. rebuild a clean recipient list (To/Cc only; Bcc is a parser artifact)
  4. reconstruct conversation threads (headers for this are gone)
  5. assemble streamlined tables and write them out
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from email import policy
from email.parser import BytesParser
from multiprocessing import Pool

import numpy as np
import pandas as pd

ROOT = None
for base in [os.getcwd()] + list(map(os.path.dirname, [os.getcwd()])):
    if os.path.exists(os.path.join(base, "eda-2", "cache", "rich_header_features.parquet")):
        ROOT = base
        break
if ROOT is None:
    sys.exit("run from the repo root (needs eda-2/cache/)")

MAILDIR = os.path.join(ROOT, "enron_mail")
CACHE = os.path.join(ROOT, "eda-2", "cache")
OUT = os.path.join(ROOT, "eda-5", "clean")
os.makedirs(OUT, exist_ok=True)

STATS: dict = {}


def banner(msg: str) -> None:
    print(f"\n{'='*70}\n{msg}\n{'='*70}", flush=True)


# --------------------------------------------------------------------------- #
# Body cleaning                                                                #
# --------------------------------------------------------------------------- #

# Lotus Notes / CP1252 control bytes that leak in as smart punctuation.
_NOTES = {
    "\x91": "'", "\x92": "'", "\x93": '"', "\x94": '"', "\x95": "*",
    "\x96": "-", "\x97": "-", "\xa0": " ", "\x85": "...",
}

# Once any of these is seen the rest of the message is prior-thread history
# pasted below, and is dropped. Each marks the START of a quoted block, so we
# cut from the marker to the end of the message. Anchored at line start so a
# block that wraps across lines (e.g. a long "Forwarded by ... on <date>"
# line) is still caught.
_CUT = re.compile(
    "|".join([
        r"-{2,}\s*Original Message\b",                  # dash-prefixed, any pos
        r"^[\s-]*Original Message\s*[-:]",              # colon/dash form, line start
        r"-{2,}\s*Forwarded by\b",                      # dash-prefixed, any pos
        r"^[\s-]*Forwarded by\b",                       # line start fallback
        # Outlook / Notes header block: a "From:" line followed within the next
        # few lines by another header field (Sent/Sent by/To/Date/Subject/
        # Reply-To). Requiring a SECOND field means a memo body line like
        # "From: Stu Smith, VP" on its own is NOT mistaken for a quote boundary.
        r"^\s*From:.*(?:\n.*){0,3}?\n\s*(Sent by|Sent|To|Date|Subject|Reply-To)\s*:",
        r"^\s*\S+@\S+\s+on\s+\d{1,2}/\d{1,2}/\d{2,4}",   # Notes "x@y on date"
        r"^\s*\S.{0,90}?\bwrote:\s*$",                   # "On ... X wrote:"
        r"-{3,}\s*(Inline attachment follows|Attachment follows)",  # Notes marker
        r"_{4,}\s*Reply Separator\s*_{4,}",             # Outlook reply separator
    ]),
    re.IGNORECASE | re.MULTILINE,
)

# Literal quoted-printable leftovers in the handful of messages whose transfer
# encoding was not declared, so get_body() never decoded them.
_QP_SOFT = re.compile(r"=\r?\n")
_QP_HEX = re.compile(r"=[0-9A-F]{2}")


def _qp_repl(m: re.Match) -> str:
    try:
        return bytes.fromhex(m.group()[1:]).decode("latin-1")
    except Exception:
        return m.group()

_DISCLAIMER = re.compile(
    r"(\*{3,}.*?\*{3,}|This (e-?mail|message|communication|transmission)\b"
    r".{0,500}?(confidential|privileged|intended (solely |only )?for|"
    r"unauthorized (use|review|disclosure)|delete (this|the) (e-?mail|message)))",
    re.IGNORECASE | re.DOTALL,
)

_PARSER = BytesParser(policy=policy.default)

# Attachment placeholders left in the text by the mail client; no readable
# content of their own.
_ATTACH = re.compile(
    r"\(See attached file:[^)]*\)|<<[^>]{1,80}>>|\[IMAGE\]",
    re.IGNORECASE | re.DOTALL)

# Some "plain-text" parts are actually raw HTML (the message was HTML-only and
# the decoder handed back the markup). Detect that and reduce it to text.
import html as _html

_HTML_HINT = re.compile(r"<(html|body|table|td|tr|div|p|br|font|head|style)\b",
                        re.IGNORECASE)
_HTML_DROP = re.compile(r"(?is)<(script|style|head)\b.*?</\1>")
_HTML_BLOCK = re.compile(r"(?i)</(p|div|tr|table|h[1-6]|li|ul|ol)>|<br\s*/?>")
_HTML_TAG = re.compile(r"<[^>]+>")


def strip_html(t: str) -> str:
    t = _HTML_DROP.sub(" ", t)          # remove script/style/head contents
    t = _HTML_BLOCK.sub("\n", t)        # block ends -> newlines
    t = _HTML_TAG.sub("", t)            # remaining tags
    t = _html.unescape(t)               # &nbsp; &amp; etc.
    return t


def fix_chars(t: str) -> str:
    # undo any quoted-printable that survived undecoded
    if "=" in t and (_QP_SOFT.search(t) or _QP_HEX.search(t)):
        t = _QP_SOFT.sub("", t)
        t = _QP_HEX.sub(_qp_repl, t)
    for k, v in _NOTES.items():
        t = t.replace(k, v)
    t = re.sub(r"\x01.", "'", t)            # Notes 2-byte control escapes
    t = "".join(c for c in t if c in "\n\t" or ord(c) >= 32)
    return t


def clean_body(raw: str) -> tuple[str, bool]:
    """Return (cleaned_text, was_trimmed). was_trimmed marks that quoted
    history or a disclaimer was cut, so the message is not verbatim."""
    fixed = fix_chars(raw)
    trimmed = False

    if _HTML_HINT.search(fixed):        # HTML leaked into the text part
        fixed = strip_html(fixed)
        trimmed = True

    cut = _CUT.search(fixed)
    body = fixed[:cut.start()] if cut else fixed
    if cut:
        trimmed = True

    body, n = _DISCLAIMER.subn("", body)
    if n:
        trimmed = True

    # attachment placeholders carry no readable content
    body, na = _ATTACH.subn("", body)
    if na:
        trimmed = True

    # drop residual ">" quote lines
    lines = [ln for ln in body.splitlines() if not ln.lstrip().startswith(">")]
    if len(lines) != len(body.splitlines()):
        trimmed = True
    body = "\n".join(lines)

    body = re.sub(r"[ \t]+", " ", body)
    body = re.sub(r" *\n", "\n", body)
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body.strip(), trimmed


def read_clean(rel_path: str) -> tuple[str, str, int, int, bool]:
    """Worker: parse one raw file, return (rel_path, body, raw_len, clean_len,
    trimmed). Body decoding handles quoted-printable / base64 transparently."""
    path = os.path.join(MAILDIR, rel_path)
    try:
        with open(path, "rb") as fh:
            msg = _PARSER.parse(fh)
        part = msg.get_body(preferencelist=("plain",))
        raw = part.get_content() if part is not None else ""
    except Exception:
        try:
            with open(path, "rb") as fh:
                raw = fh.read().split(b"\n\n", 1)[-1].decode("latin-1", "replace")
        except Exception:
            raw = ""
    clean, trimmed = clean_body(raw)
    return rel_path, clean, len(raw), len(clean), trimmed


# --------------------------------------------------------------------------- #
# Subject normalisation + threading                                           #
# --------------------------------------------------------------------------- #

_PREFIX = re.compile(r"^\s*(re|fw|fwd|aw|wg)\s*(\[\d+\])?\s*:\s*", re.IGNORECASE)


def norm_addr(a: str) -> str:
    """Canonical address: lowercase, strip wrapping quotes/spaces, collapse the
    repeated and leading dots that the FERC name-mangling left in local parts
    (".kaminski", "j..kaminski" -> "j.kaminski" / "kaminski"). Returns "" for
    blank/sentinel addresses so they can be flagged rather than counted."""
    a = (a or "").strip().strip("'\"").lower()
    if not a or "@" not in a:
        return ""
    loc, _, dom = a.partition("@")
    loc = re.sub(r"\.{2,}", ".", loc).strip(".")
    dom = dom.strip().strip(".")
    if not loc or not dom or "@" in dom:        # malformed (double-@ etc.)
        return ""
    if "no_address" in loc or loc == "no.address":
        return ""
    return f"{loc}@{dom}"


def addr_is_valid(a: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", a or ""))


def canon_subject(s: str) -> str:
    s = (s or "").strip()
    prev = None
    while s and s != prev:                  # strip stacked "Re: Fw: Re:"
        prev = s
        s = _PREFIX.sub("", s).strip()
    return re.sub(r"\s+", " ", s).lower()


class UnionFind:
    def __init__(self, n: int):
        self.p = list(range(n))

    def find(self, x: int) -> int:
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a: int, b: int) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[ra] = rb


# --------------------------------------------------------------------------- #
def main() -> None:
    t0 = time.time()

    # ---- Stage 1: dedup + canonical selection ---------------------------- #
    banner("Stage 1/5  deduplicate files -> unique messages")
    rich = pd.read_parquet(
        os.path.join(CACHE, "rich_header_features.parquet"),
        columns=["rel_path", "user", "folder_group", "file_size", "date",
                 "date_plausible", "from_addr", "from_domain",
                 "is_internal_sender", "subject", "to_count", "cc_count"],
    )
    hdr = pd.read_parquet(
        os.path.join(CACHE, "headers.parquet"),
        columns=["rel_path", "message_id"],
    )
    rich = rich.merge(hdr, on="rel_path", how="left")
    n_files = len(rich)
    STATS["n_files"] = int(n_files)

    rich["key"] = (
        rich["from_addr"].fillna("") + "|" + rich["subject"].fillna("") + "|"
        + rich["date"].astype("int64").astype(str) + "|"
        + rich["to_count"].astype(str) + "|" + rich["cc_count"].astype(str)
    )
    # rank for canonical choice: sent folder wins, then inbox, then rest;
    # tie-break deterministically by rel_path
    rank = {"sent": 0, "inbox": 1, "discussion": 2, "topic/project": 3,
            "calendar": 4, "deleted": 5}
    rich["_rank"] = rich["folder_group"].map(rank).fillna(9).astype(int)
    rich = rich.sort_values(["key", "_rank", "rel_path"])

    grp = rich.groupby("key", sort=False)
    canon = grp.head(1).copy()
    agg = grp.agg(
        n_copies=("rel_path", "size"),
        n_mailboxes=("user", "nunique"),
        in_sent=("folder_group", lambda s: bool((s == "sent").any())),
    ).reset_index()
    canon = canon.merge(agg, on="key", how="left")

    STATS["n_unique"] = int(len(canon))
    STATS["redundant_copies"] = int(n_files - len(canon))
    STATS["redundancy_pct"] = round((n_files - len(canon)) / n_files * 100, 2)
    print(f"  files                {n_files:>9,}")
    print(f"  unique messages      {len(canon):>9,}")
    print(f"  redundant copies     {n_files - len(canon):>9,} "
          f"({STATS['redundancy_pct']}%)")

    # ---- Stage 2: parse + clean bodies ----------------------------------- #
    banner("Stage 2/5  parse + clean canonical bodies from the maildir")
    rels = canon["rel_path"].tolist()
    t = time.time()
    results = {}
    nproc = max(1, (os.cpu_count() or 2) - 2)
    with Pool(nproc) as pool:
        for i, (rel, body, rawlen, clen, trim) in enumerate(
                pool.imap_unordered(read_clean, rels, chunksize=256), 1):
            results[rel] = (body, rawlen, clen, trim)
            if i % 50000 == 0:
                print(f"  {i:>7,} / {len(rels):,} parsed", flush=True)
    print(f"  parsed {len(results):,} bodies in {time.time()-t:.0f}s "
          f"on {nproc} procs")

    canon["body"] = canon["rel_path"].map(lambda r: results[r][0])
    canon["body_raw_chars"] = canon["rel_path"].map(lambda r: results[r][1])
    canon["body_chars"] = canon["rel_path"].map(lambda r: results[r][2])
    canon["body_was_trimmed"] = canon["rel_path"].map(lambda r: results[r][3])
    canon["body_empty_after_clean"] = (canon["body_chars"] == 0)

    STATS["bodies_trimmed"] = int(canon["body_was_trimmed"].sum())
    STATS["bodies_empty_after_clean"] = int(canon["body_empty_after_clean"].sum())
    STATS["body_chars_saved_pct"] = round(
        (1 - canon["body_chars"].sum() / max(canon["body_raw_chars"].sum(), 1))
        * 100, 2)
    print(f"  messages with quoted history/disclaimer trimmed: "
          f"{STATS['bodies_trimmed']:,}")
    print(f"  empty after cleaning (pure forwards/quotes): "
          f"{STATS['bodies_empty_after_clean']:,}")
    print(f"  body text volume reduced by {STATS['body_chars_saved_pct']}%")

    # ---- Stage 2b: normalise sender address + quality flags -------------- #
    banner("Stage 2b/5  normalise sender addresses, flag data-quality issues")
    raw_from = canon["from_addr"].fillna("")
    canon["from_addr_norm"] = raw_from.map(norm_addr)
    canon["from_addr_mangled"] = raw_from.str.contains(r"\.\.|^\.", regex=True)
    canon["from_addr_valid"] = canon["from_addr_norm"].map(addr_is_valid)
    STATS["from_mangled_dots"] = int(canon["from_addr_mangled"].sum())
    STATS["from_unresolvable"] = int((~canon["from_addr_valid"]).sum())
    merged_senders = raw_from[raw_from != ""].nunique() - \
        canon.loc[canon["from_addr_norm"] != "", "from_addr_norm"].nunique()
    STATS["sender_identities_merged_by_norm"] = int(merged_senders)
    print(f"  senders with mangled dots:      {STATS['from_mangled_dots']:,}")
    print(f"  senders unresolvable to an addr:{STATS['from_unresolvable']:,}")
    print(f"  sender identities merged by dot-normalisation: {merged_senders:,}")

    # ---- Stage 2c: near-duplicate bodies + sender-attribution flags ------ #
    banner("Stage 2c/5  flag near-duplicate bodies and sender attribution")
    # Exact dedup (stage 1) keys on sender+subject+time, so the SAME text resent
    # under a different subject or by a different person survives as separate
    # rows: signature blocks, boilerplate disclaimers, recurring newsletters.
    # We hash the whitespace-normalised body and count how many distinct
    # messages share it. body_is_boilerplate marks text shared by >=5 messages,
    # which a topic/text model should treat as a stopword-like block.
    norm_body = (canon["body"].fillna("").str.lower()
                 .str.replace(r"\s+", " ", regex=True).str.strip())
    dup_count = norm_body.map(norm_body.value_counts())
    canon["body_dup_count"] = dup_count.where(canon["body_chars"] > 0, 0).astype(int)
    # Boilerplate = substantial text (>=120 chars) that recurs across >=5 distinct
    # messages: signature blocks, legal disclaimers, recurring newsletters. The
    # length floor keeps short repeated content ("FYI", "thanks") out of it,
    # since that is real content, not a reused block.
    canon["body_is_boilerplate"] = (
        (canon["body_chars"] >= 120) & (canon["body_dup_count"] >= 5))
    longrec = norm_body[(canon["body_chars"] >= 120)]
    STATS["body_recurring_texts"] = int((longrec.value_counts() >= 5).sum())
    STATS["body_boilerplate_msgs"] = int(canon["body_is_boilerplate"].sum())
    print(f"  distinct long texts recurring >=5x: {STATS['body_recurring_texts']:,}")
    print(f"  messages carrying such boilerplate: {STATS['body_boilerplate_msgs']:,}")

    # Sent mail whose from-address does not contain the mailbox owner's surname:
    # assistants sending on an executive's behalf, or shared role mailboxes.
    surname = canon["user"].str.split("-").str[0]
    fa_local = canon["from_addr_norm"].fillna("").str.split("@").str[0]
    owner_in_addr = np.array(
        [bool(s) and (s in l) for s, l in zip(surname, fa_local)])
    canon["sent_not_by_owner"] = (
        canon["folder_group"].eq("sent").to_numpy() & ~owner_in_addr)
    STATS["sent_not_by_owner"] = int(canon["sent_not_by_owner"].sum())
    print(f"  sent messages not from the mailbox owner: "
          f"{STATS['sent_not_by_owner']:,}")

    # Verified-clean spot checks (recorded in stats, no action needed):
    bod = canon["body"].fillna("")
    STATS["bodies_nonascii"] = int(bod.str.contains(r"[^\x00-\x7f]", regex=True).sum())
    STATS["bodies_mojibake"] = int(
        bod.str.contains(r"Ã|â€|�", regex=True).sum())
    STATS["empty_subject_and_body"] = int(
        ((canon["subject"].fillna("").str.strip() == "")
         & canon["body_empty_after_clean"]).sum())
    STATS["bigfile_tinybody"] = int(
        ((canon["file_size"] > 50000) & (canon["body_chars"] < 200)).sum())
    print(f"  [check] non-ASCII bodies {STATS['bodies_nonascii']:,}, "
          f"mojibake {STATS['bodies_mojibake']:,}, "
          f"empty subject+body {STATS['empty_subject_and_body']:,}, "
          f"big-file/tiny-body {STATS['bigfile_tinybody']:,}")

    # ---- Stage 3: clean recipient list ----------------------------------- #
    banner("Stage 3/5  rebuild recipient list (To/Cc only; Bcc is an artifact)")
    edges = pd.read_parquet(
        os.path.join(CACHE, "recipient_edges.parquet"),
        columns=["rel_path", "from_addr", "recipient_addr", "recipient_domain",
                 "channel", "is_internal_recipient"],
    )
    canon_rels = set(canon["rel_path"])
    edges = edges[edges["rel_path"].isin(canon_rels)]

    # Verify the Bcc-is-a-copy-of-Cc claim before discarding Bcc: for every
    # message that has both, are the address sets identical?
    _cc = (edges[edges.channel == "cc"].groupby("rel_path")["recipient_addr"]
           .agg(frozenset))
    _bcc = (edges[edges.channel == "bcc"].groupby("rel_path")["recipient_addr"]
            .agg(frozenset))
    _both = pd.concat([_cc.rename("cc"), _bcc.rename("bcc")], axis=1).dropna()
    STATS["bcc_cc_both_present"] = int(len(_both))
    STATS["bcc_cc_identical_pct"] = (
        round((_both["cc"] == _both["bcc"]).mean() * 100, 2) if len(_both) else None)
    print(f"  Bcc=Cc check: {STATS['bcc_cc_both_present']:,} msgs have both, "
          f"{STATS['bcc_cc_identical_pct']}% identical -> Bcc dropped as artifact")

    edges = edges[edges["channel"].isin(["to", "cc"])]
    edges = edges[edges["recipient_addr"].notna()
                  & (edges["recipient_addr"] != "")]
    edges = edges.drop_duplicates(["rel_path", "recipient_addr", "channel"])
    # normalise recipient address + flag the malformed/DN-leak ones
    edges["recipient_addr_norm"] = edges["recipient_addr"].map(norm_addr)
    edges["recipient_addr_valid"] = edges["recipient_addr_norm"].map(addr_is_valid)
    STATS["recipient_malformed"] = int((~edges["recipient_addr_valid"]).sum())
    STATS["recipient_identities_merged_by_norm"] = int(
        edges.loc[edges["recipient_addr"] != "", "recipient_addr"].nunique()
        - edges.loc[edges["recipient_addr_norm"] != "", "recipient_addr_norm"].nunique())

    # distribution-list / role addresses: a single such recipient stands for
    # many real people, so the network graph cannot expand it. Flag, do not drop.
    edges["recipient_is_list"] = edges["recipient_addr_norm"].str.contains(
        r"\bdl[._-]|[._-]dl\b|^all[._.]|[._.]all@|\.all\b|_list\b|listserv|"
        r"everyone|announcement|distribution|\.team@|notesaddr",
        regex=True, na=False)
    STATS["recipient_list_edges"] = int(edges["recipient_is_list"].sum())

    # self-addressed: recipient is the sender (to-self note, or self-CC)
    rel2from = dict(zip(canon["rel_path"], canon["from_addr_norm"]))
    edges["is_self"] = (
        (edges["recipient_addr_norm"] != "")
        & (edges["recipient_addr_norm"] == edges["rel_path"].map(rel2from)))
    STATS["recipient_self_edges"] = int(edges["is_self"].sum())

    # message_id per rel_path for the recipients table
    rel2mid = dict(zip(canon["rel_path"], canon["message_id"]))
    edges["message_id"] = edges["rel_path"].map(rel2mid)

    rc = edges.groupby("rel_path")
    canon["recipient_count"] = canon["rel_path"].map(
        rc["recipient_addr"].nunique()).fillna(0).astype(int)
    canon["to_count_clean"] = canon["rel_path"].map(
        edges[edges.channel == "to"].groupby("rel_path").size()).fillna(0).astype(int)
    canon["cc_count_clean"] = canon["rel_path"].map(
        edges[edges.channel == "cc"].groupby("rel_path").size()).fillna(0).astype(int)
    canon["external_recipient_count"] = canon["rel_path"].map(
        edges[~edges.is_internal_recipient].groupby("rel_path")["recipient_addr"]
        .nunique()).fillna(0).astype(int)
    canon["has_external_recipient"] = canon["external_recipient_count"] > 0
    canon["list_recipient_count"] = canon["rel_path"].map(
        edges[edges.recipient_is_list].groupby("rel_path").size()).fillna(0).astype(int)
    canon["has_list_recipient"] = canon["list_recipient_count"] > 0
    STATS["recipient_edges"] = int(len(edges))
    print(f"  clean recipient edges: {len(edges):,}")
    print(f"  distribution-list recipient edges: {STATS['recipient_list_edges']:,}")
    print(f"  self-addressed edges: {STATS['recipient_self_edges']:,}")

    # ---- Stage 4: thread reconstruction ---------------------------------- #
    banner("Stage 4/5  reconstruct threads (no In-Reply-To/References exist)")
    canon = canon.reset_index(drop=True)
    canon["canon_subject"] = canon["subject"].map(canon_subject)

    # participants per message = sender + recipients (normalised addresses)
    parts = (edges.groupby("rel_path")["recipient_addr_norm"]
             .agg(set).to_dict())

    # Two messages join a thread when they share a normalised subject AND a
    # participant AND are close in time. The time bound is the key safeguard:
    # without it, a generic subject like "fyi" chains 45 different people's
    # unrelated notes across three years into one bogus thread. We process each
    # subject group in date order and link a message only to a PRIOR message
    # (sharing a participant) sent within THREAD_GAP_DAYS; the "last seen index
    # per participant" is refreshed as we move forward, so a quiet gap of more
    # than the window starts a fresh conversation.
    THREAD_GAP_DAYS = 30
    gap = pd.Timedelta(days=THREAD_GAP_DAYS)

    uf = UnionFind(len(canon))
    order = canon.sort_values("date")
    for subj, grp in order.groupby("canon_subject", sort=False):
        if not subj or len(grp) == 1:        # empty subject -> no threading
            continue
        last: dict[str, tuple] = {}          # participant -> (idx, date)
        for i, d in zip(grp.index, grp["date"]):
            rel = canon.at[i, "rel_path"]
            who = set(parts.get(rel, set()))
            who.add(canon.at[i, "from_addr_norm"])
            who.discard("")
            for p in who:
                prev = last.get(p)
                if prev is not None and pd.notna(d) and pd.notna(prev[1]) \
                        and (d - prev[1]) <= gap:
                    uf.union(i, prev[0])
                last[p] = (i, d)

    roots = np.array([uf.find(i) for i in range(len(canon))])
    # map root -> compact thread id
    _, tid = np.unique(roots, return_inverse=True)
    canon["thread_id"] = tid
    tsize = canon.groupby("thread_id")["rel_path"].transform("size")
    canon["thread_size"] = tsize
    canon["thread_position"] = (
        canon.sort_values("date").groupby("thread_id").cumcount() + 1)
    canon["is_thread_root"] = canon["thread_position"] == 1

    # Flag threads that span more than a year: a real reply chain rarely does,
    # so these are most likely the heuristic over-merging a recurring subject.
    span = (canon.groupby("thread_id")["date"].transform("max")
            - canon.groupby("thread_id")["date"].transform("min"))
    canon["thread_span_days"] = (span.dt.total_seconds() / 86400).round().astype(int)
    canon["thread_maybe_overmerged"] = (
        (canon["thread_size"] > 1) & (canon["thread_span_days"] > 365))

    STATS["n_threads"] = int(canon["thread_id"].nunique())
    STATS["threads_multi"] = int((canon.groupby("thread_id").size() > 1).sum())
    STATS["largest_thread"] = int(canon["thread_size"].max())
    STATS["msgs_in_multi_threads"] = int((canon["thread_size"] > 1).sum())
    STATS["threads_maybe_overmerged"] = int(
        canon.loc[canon["thread_maybe_overmerged"], "thread_id"].nunique())
    print(f"  threads (incl singletons): {STATS['n_threads']:,}")
    print(f"  multi-message threads:     {STATS['threads_multi']:,}")
    print(f"  messages in real threads:  {STATS['msgs_in_multi_threads']:,}")
    print(f"  largest thread:            {STATS['largest_thread']:,} messages")
    print(f"  threads flagged maybe-over-merged (>365d): "
          f"{STATS['threads_maybe_overmerged']:,}")

    # ---- Stage 5: assemble + write --------------------------------------- #
    banner("Stage 5/5  assemble streamlined tables and write parquet")
    messages = canon[[
        "message_id", "date", "date_plausible",
        "from_addr", "from_addr_norm", "from_domain", "is_internal_sender",
        "from_addr_mangled", "from_addr_valid", "sent_not_by_owner",
        "subject", "canon_subject",
        "to_count_clean", "cc_count_clean", "recipient_count",
        "external_recipient_count", "has_external_recipient",
        "list_recipient_count", "has_list_recipient",
        "user", "folder_group", "file_size",
        "body", "body_chars", "body_was_trimmed", "body_empty_after_clean",
        "body_dup_count", "body_is_boilerplate",
        "n_copies", "n_mailboxes", "in_sent",
        "thread_id", "thread_size", "thread_position", "is_thread_root",
        "thread_span_days", "thread_maybe_overmerged",
    ]].rename(columns={"user": "mailbox_owner",
                       "to_count_clean": "to_count",
                       "cc_count_clean": "cc_count"})

    recipients = edges[[
        "message_id", "from_addr", "recipient_addr", "recipient_addr_norm",
        "recipient_domain", "recipient_addr_valid",
        "recipient_is_list", "is_self",
        "channel", "is_internal_recipient",
    ]].reset_index(drop=True)

    mpath = os.path.join(OUT, "messages_clean.parquet")
    rpath = os.path.join(OUT, "recipients_clean.parquet")
    messages.to_parquet(mpath, compression="zstd", index=False)
    recipients.to_parquet(rpath, compression="zstd", index=False)

    STATS["out_messages_rows"] = int(len(messages))
    STATS["out_messages_cols"] = int(messages.shape[1])
    STATS["out_recipients_rows"] = int(len(recipients))
    STATS["out_messages_mb"] = round(os.path.getsize(mpath) / 1e6, 1)
    STATS["out_recipients_mb"] = round(os.path.getsize(rpath) / 1e6, 1)
    STATS["src_cache_mb"] = round(sum(
        os.path.getsize(os.path.join(CACHE, f)) for f in os.listdir(CACHE)) / 1e6, 1)
    STATS["runtime_s"] = round(time.time() - t0, 1)

    print(f"  messages_clean.parquet   {len(messages):,} rows x "
          f"{messages.shape[1]} cols  ({STATS['out_messages_mb']} MB)")
    print(f"  recipients_clean.parquet {len(recipients):,} rows  "
          f"({STATS['out_recipients_mb']} MB)")

    with open(os.path.join(OUT, "clean_stats.json"), "w") as fh:
        json.dump(STATS, fh, indent=2)
    print(f"\n  total runtime {STATS['runtime_s']}s")
    print(f"  stats -> {os.path.join(OUT, 'clean_stats.json')}")


if __name__ == "__main__":
    main()
