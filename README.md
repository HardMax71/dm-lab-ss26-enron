# DM Lab SS26 — Enron Email Dataset

Practical course in data mining, Summer Semester 2026. We work with the [Enron email
corpus](https://www.cs.cmu.edu/~enron/) (~500k messages, 150 mailboxes from former Enron
executives, released as part of the FERC investigation).

## Dataset

- **Source:** https://www.cs.cmu.edu/~enron/
- **Tarball:** `enron_mail_20150507.tar.gz` (~423 MB) — attached as a
  [release asset](../../releases/latest), not stored in git
- **Unpacked:** `./enron_mail/` (~2.6 GB on disk, ~517k files)

To get going locally:

```bash
# download the tarball from the release page into the repo root, then:
tar -xzf enron_mail_20150507.tar.gz   # creates ./enron_mail/
python inspect_enron.py               # sanity-check the maildir
jupyter lab eda/enron_eda.ipynb       # open the EDA notebook
```

## Repository contents

- `eda/enron_eda.ipynb` — exploratory data analysis notebook
- `eda/cache/` — cached intermediate parquet files (regenerable from the raw maildir)
- `eda/plots/` — PNG and interactive HTML plots produced by the notebook
- `inspect_enron.py` — quick verification script for dataset claims (threading, encodings,
  folder landscape, sender domains, attachment refs)

## Schedule

Intended schedule for SS26. Boxes are ticked as we complete each session.

| Done | Date    | Topic                                              | Done | Date    | Topic                  |
|:----:|---------|----------------------------------------------------|:----:|---------|------------------------|
| [x]  | Apr 15  | Kick-off                                           | [ ]  | Jun 3   | Descriptive Mining 5   |
| [x]  | Apr 22  | No class                                           | [ ]  | Jun 10  | Descriptive Mining 6 (?) |
| [x]  | Apr 29  | Data Set Presentation                              | [ ]  | Jun 17  | Predictive Mining 1    |
| [x]  | May 6   | Data Set Selection / Group Formation / EDA 1       | [ ]  | Jun 24  | Predictive Mining 2    |
| [ ]  | May 13  | Descriptive Mining 2                               | [ ]  | Jul 1   | Predictive Mining 3    |
| [ ]  | May 20  | Descriptive Mining 3                               | [ ]  | Jul 8   | Final Presentation 1   |
| [ ]  | May 27  | Descriptive Mining 4                               | [ ]  | Jul 15  | Final Presentation 2   |
