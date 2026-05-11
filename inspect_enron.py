# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Verify claims about the Enron maildir: threads, encodings, folders, messiness."""
from __future__ import annotations

import os
import re
import sys
from collections import Counter
from email import policy
from email.parser import BytesHeaderParser, BytesParser
from pathlib import Path

ROOT = Path("/home/user/Desktop/possible_datasets/enron_mail")

LOGISTICS_HINTS = ("schedul", "logistic", "transport", "pipeline", "dispatch",
                   "deliver", "nomination", "gas_daily", "capacity")
RE_SUBJ = re.compile(r"^\s*(re|fw|fwd|aw|wg)\s*:\s*", re.I)
RE_ATTACH = re.compile(rb"<<\s*File\s*:", re.I)


def normalize_subject(s: str) -> str:
    prev = None
    while prev != s:
        prev = s
        s = RE_SUBJ.sub("", s)
    return s.strip().lower()


def walk_files(root: Path):
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            yield Path(dirpath) / name


def main() -> int:
    if not ROOT.exists():
        print(f"missing: {ROOT}", file=sys.stderr)
        return 1

    users = sorted(p.name for p in ROOT.iterdir() if p.is_dir())
    print(f"users (top-level dirs): {len(users)}")

    header_parser = BytesHeaderParser(policy=policy.compat32)
    full_parser = BytesParser(policy=policy.compat32)

    total = 0
    header_parse_errors = 0
    missing_msgid = 0
    msgid_counts: Counter[str] = Counter()
    charset_counts: Counter[str] = Counter()
    has_in_reply_to = 0
    has_references = 0
    subject_buckets: Counter[str] = Counter()
    folder_counts: Counter[str] = Counter()
    logistics_folders: Counter[str] = Counter()
    from_domains: Counter[str] = Counter()
    attachment_refs = 0
    decode_errors = 0
    body_sampled = 0

    BODY_SAMPLE_EVERY = 50  # parse body on ~2% of messages for speed

    for i, path in enumerate(walk_files(ROOT)):
        total += 1
        folder = path.parent.name
        folder_counts[folder] += 1
        if any(h in folder.lower() for h in LOGISTICS_HINTS):
            rel = path.relative_to(ROOT)
            logistics_folders[f"{rel.parts[0]}/{folder}"] += 1

        try:
            with path.open("rb") as fh:
                msg = header_parser.parse(fh)
        except Exception:
            header_parse_errors += 1
            continue

        mid = msg.get("Message-ID")
        if mid:
            msgid_counts[mid.strip()] += 1
        else:
            missing_msgid += 1

        if msg.get("In-Reply-To"):
            has_in_reply_to += 1
        if msg.get("References"):
            has_references += 1

        subj = msg.get("Subject", "") or ""
        subject_buckets[normalize_subject(subj)] += 1

        ct = msg.get("Content-Type", "") or ""
        m = re.search(r'charset="?([^";\s]+)', ct, re.I)
        charset_counts[(m.group(1) if m else "<none>").lower()] += 1

        frm = msg.get("From", "") or ""
        m = re.search(r"@([\w.-]+)", frm)
        if m:
            from_domains[m.group(1).lower()] += 1

        if i % BODY_SAMPLE_EVERY == 0:
            try:
                with path.open("rb") as fh:
                    full = full_parser.parse(fh)
                body_sampled += 1
                payload = full.get_payload(decode=True)
                if payload is None and full.is_multipart():
                    for part in full.walk():
                        if part.get_payload(decode=True):
                            payload = part.get_payload(decode=True)
                            break
                if payload is not None:
                    try:
                        text = payload.decode(
                            (m.group(1) if (m := re.search(r'charset="?([^";\s]+)', ct, re.I)) else "utf-8"),
                            errors="strict",
                        )
                    except (UnicodeDecodeError, LookupError):
                        decode_errors += 1
                        text = payload.decode("latin-1", errors="replace")
                    if RE_ATTACH.search(payload):
                        attachment_refs += 1
            except Exception:
                decode_errors += 1

    # Report
    print(f"\n=== totals ===")
    print(f"messages walked:        {total:,}")
    print(f"header parse errors:    {header_parse_errors}")
    print(f"missing Message-ID:     {missing_msgid}")
    unique_mids = len(msgid_counts)
    dup_mids = sum(c - 1 for c in msgid_counts.values() if c > 1)
    print(f"unique Message-IDs:     {unique_mids:,}")
    print(f"duplicate Message-IDs:  {dup_mids:,} (files sharing an ID with another)")

    print(f"\n=== threading signals ===")
    print(f"In-Reply-To present:    {has_in_reply_to:,} ({has_in_reply_to/total:.1%})")
    print(f"References present:     {has_references:,} ({has_references/total:.1%})")
    unique_subjects = len(subject_buckets)
    reused_subjects = sum(1 for c in subject_buckets.values() if c > 1)
    print(f"unique normalized subs: {unique_subjects:,}")
    print(f"subjects reused (>=2):  {reused_subjects:,}  -> subject-based threading is the fallback")
    print("top 5 subject threads:")
    for sub, c in subject_buckets.most_common(5):
        print(f"  {c:>6}  {sub[:70]!r}")

    print(f"\n=== encodings declared ===")
    for cs, c in charset_counts.most_common(10):
        print(f"  {c:>7}  {cs}")

    print(f"\n=== body sample ({body_sampled:,} msgs) ===")
    print(f"decode errors / parse exceptions: {decode_errors}")
    print(f"messages referencing << File: attachment: {attachment_refs}")

    print(f"\n=== folder landscape (top 15) ===")
    for f, c in folder_counts.most_common(15):
        print(f"  {c:>7}  {f}")

    print(f"\n=== logistics-ish folders (top 20) ===")
    for f, c in logistics_folders.most_common(20):
        print(f"  {c:>6}  {f}")

    print(f"\n=== from-domains (top 10) ===")
    for d, c in from_domains.most_common(10):
        print(f"  {c:>7}  {d}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
