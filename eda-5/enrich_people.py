# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "pyarrow"]
# ///
"""Enrich the resolved mailbox owners with external job titles + a self-sourced id.

Run from the repo root, after clean_dataset.py:

    uv run eda-5/enrich_people.py

Joins three things, one row per mailbox owner:
  * identity        eda-5/clean/people.parquet      (corpus-derived)
  * job title       eda-5/refs/enron_employeelist.csv  (Shetty-Adibi, external)
  * Exchange CN id  parsed from the owner's own X-From header in the maildir
                    (self-sourced; best-effort, skipped if enron_mail/ absent)

Writes eda-5/clean/people_roles.parquet. Every title-derived column is tagged
with `title_source` so external annotation is never confused with corpus data.
The job title is an external label (point-in-time, partly hand-imputed); see
eda-5/refs/README.md for provenance and caveats.
"""
from __future__ import annotations

import os
import re
import sys

import pandas as pd

ROOT = None
for base in [os.getcwd()] + list(map(os.path.dirname, [os.getcwd()])):
    if os.path.exists(os.path.join(base, "eda-5", "clean", "people.parquet")):
        ROOT = base
        break
if ROOT is None:
    sys.exit("run from the repo root (needs eda-5/clean/people.parquet)")

CLEAN = os.path.join(ROOT, "eda-5", "clean")
REFS = os.path.join(ROOT, "eda-5", "refs")
MAILDIR = os.path.join(ROOT, "enron_mail")

TITLE_SOURCE = "shetty-adibi-2004 (ahr85/enron mirror)"

# Ordinal seniority on the management ladder. Trader and Employee are the
# rank-and-file floor; In House Lawyer is professional staff placed at the
# manager level; Vice President is taken above Managing Director, the common
# convention for this annotation. Unknown/N-A is left null, not guessed.
RANK = {
    "CEO": 7, "President": 6, "Vice President": 5, "Managing Director": 4,
    "Director": 3, "Manager": 2, "In House Lawyer": 2, "Trader": 1, "Employee": 1,
}
EXECUTIVE = {"CEO", "President", "Vice President", "Managing Director"}

_FROM = re.compile(rb"^From:\s*(.*)$", re.M)
_XFROM = re.compile(rb"^X-From:\s*(.*)$", re.M)
_CN = re.compile(rb"CN=([A-Za-z0-9]+)>?\s*$")


def cn_for_owner(owner: str, addrs: list[str], surname: str) -> str | None:
    """Best-effort Exchange CN id from a message the owner sent. Prefer a file
    whose From is the owner's surname-matching address, so assistant-run desks
    do not resolve to the assistant's id."""
    base = os.path.join(MAILDIR, owner)
    if not os.path.isdir(base):
        return None
    addr_set = {a.lower() for a in addrs if a}
    own = {a for a in addr_set if surname and surname in a.split("@")[0]}
    files = []
    for root, _, fs in os.walk(base):
        sent = "sent" in root.lower()
        for fn in fs:
            files.append((0 if sent else 1, os.path.join(root, fn)))
    files.sort()
    fallback = None
    for _, path in files[:600]:
        try:
            raw = open(path, "rb").read(4000)
        except Exception:
            continue
        mf = _FROM.search(raw)
        if not mf:
            continue
        sender = mf.group(1).strip().lower().decode("latin1", "ignore")
        if sender not in addr_set:
            continue
        mx = _XFROM.search(raw)
        cn = _CN.search(mx.group(1).strip()) if mx else None
        if cn is None:
            continue
        cid = cn.group(1).decode()
        if sender in own:                 # owner's own address -> take it
            return cid
        if fallback is None:              # otherwise remember the first hit
            fallback = cid
    return fallback


def main() -> None:
    ppl = pd.read_parquet(os.path.join(CLEAN, "people.parquet"))

    emp = pd.read_csv(os.path.join(REFS, "enron_employeelist.csv"), sep=";")
    emp.columns = [c.strip() for c in emp.columns]
    emp = emp.rename(columns={"Ordner": "folder"})
    emp["folder"] = emp["folder"].astype(str).str.strip()
    emp["first_name"] = emp["firstName"].astype(str).str.strip()
    emp["last_name"] = emp["lastName"].astype(str).str.strip()
    emp["title"] = emp["status"].fillna("N/A").astype(str).str.strip().replace("", "N/A")
    emp = emp[["folder", "first_name", "last_name", "title"]]

    miss = set(ppl["owner"]) - set(emp["folder"])
    if miss:
        print(f"  WARNING: {len(miss)} owners have no title row: {sorted(miss)}")

    df = ppl[["owner", "surname"]].merge(
        emp, left_on="owner", right_on="folder", how="left").drop(columns="folder")
    df["title"] = df["title"].fillna("N/A")
    df["display_name"] = (df["first_name"].fillna("") + " "
                          + df["last_name"].fillna("")).str.strip()
    df["seniority_rank"] = df["title"].map(RANK).astype("Int64")
    df["is_executive"] = df["title"].isin(EXECUTIVE)
    df["title_source"] = TITLE_SOURCE
    df["title_note"] = pd.NA

    # Layer corpus/web-sourced titles onto owners the external annotation left
    # N/A. Each row carries its own provenance and the evidence behind it; the
    # vetted Shetty-Adibi rows are never overwritten. See refs/title_supplement.csv.
    supp_path = os.path.join(REFS, "title_supplement.csv")
    filled = 0
    if os.path.exists(supp_path):
        supp = pd.read_csv(supp_path, sep=";")
        for _, row in supp.iterrows():
            mask = (df["owner"] == row["folder"]) & (df["title"] == "N/A")
            if mask.any():
                df.loc[mask, "title"] = row["title"]
                df.loc[mask, "seniority_rank"] = int(row["seniority_rank"])
                df.loc[mask, "is_executive"] = str(row["is_executive"]).strip().lower() == "true"
                df.loc[mask, "title_source"] = row["title_source"]
                df.loc[mask, "title_note"] = row["title_note"]
                filled += 1

    addrs = dict(zip(ppl["owner"], ppl["addresses"].fillna("").str.split(";")))
    surname = dict(zip(ppl["owner"], ppl["surname"]))
    prior_path = os.path.join(CLEAN, "people_roles.parquet")
    if os.path.isdir(MAILDIR):
        df["cn_id"] = [cn_for_owner(o, addrs.get(o, []), surname.get(o, ""))
                       for o in df["owner"]]
    elif os.path.exists(prior_path):
        prior = pd.read_parquet(prior_path)[["owner", "cn_id"]]
        df = df.merge(prior, on="owner", how="left")
        print("  note: enron_mail/ not found, reused cn_id from existing people_roles.parquet")
    else:
        print("  note: enron_mail/ not found, leaving cn_id null")
        df["cn_id"] = None

    out = df[["owner", "display_name", "first_name", "last_name", "cn_id",
              "title", "seniority_rank", "is_executive", "title_source", "title_note"]]
    path = os.path.join(CLEAN, "people_roles.parquet")
    out.to_parquet(path, compression="zstd", index=False)

    print(f"  people_roles.parquet  {len(out)} owners")
    print(f"  titles known (not N/A): {(out['title'] != 'N/A').sum()}")
    print(f"  filled from title_supplement.csv: {filled}")
    print(f"  executives (CEO/Pres/VP/MD): {int(out['is_executive'].sum())}")
    print(f"  cn_id resolved: {out['cn_id'].notna().sum()} / {len(out)}")
    print("\n  title distribution:")
    print(out["title"].value_counts().to_string().replace("\n", "\n    "))


if __name__ == "__main__":
    main()
