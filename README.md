# dm-lab-ss26-enron

Code and notebooks for the Enron email corpus, used as the project dataset in
the Data Mining practical course, Summer Semester 2026.

## Dataset

CMU Enron release: https://www.cs.cmu.edu/~enron/. The corpus has about 517k
message files from 150 mailbox owners. The 423 MB tarball is too large for git
and ships as an asset on the
[`dataset-v1`](https://github.com/HardMax71/dm-lab-ss26-enron/releases/tag/dataset-v1)
release of this repo. Unpacking gives an `./enron_mail/` tree of roughly
2.6 GB.

After downloading `enron_mail_20150507.tar.gz` into the repo root:

```
tar -xzf enron_mail_20150507.tar.gz
python inspect_enron.py
jupyter lab eda-2/enron_eda.ipynb
```

The cleaned, deduplicated version of the corpus (the parquet tables built
under `eda-5/clean/`), now alongside the pred-2 thread annotations, is published
as the
[`dataset-v4`](https://github.com/HardMax71/dm-lab-ss26-enron/releases/tag/dataset-v4)
release, the current latest. Most analysis from week four on only needs those
tables, not the raw tarball.

## Layout

The folders are numbered by the session they belong to, and each one carries
its own README with the details and run commands.

`eda/` is week one: team matching and dataset selection, no analysis.

`eda-2/` holds the original exploratory notebook. It builds the cached parquet
tables under `eda-2/cache/` that every later report reads, so it runs first.

`eda-3/` is the written first-week report: the variables, the main
distributions, and a closer look at deleted mail.

`eda-4/` extends that report along the week-2 review: activity rhythm, sender
domains, the social graph, the `california` and `ees` content drill, and
deletion statistics.

`eda-5/` covers weeks four and five: the cleaning pipeline that turns the raw
corpus into the deduplicated, thread-aware tables under `eda-5/clean/`, the
completeness audit, and the behavioural clustering of the mailbox owners.

`pred-1/` stress-tests the week-five groups and adds a body-text notebook asking
what a message alone reveals about its writer: the person is easy to name, the
behavioural group is not.

`pred-2/` predicts an external label the pipeline never clustered on, the
Shetty-Adibi titles, reaching AUC 0.80 for executive status and a Spearman of 0.47
for seniority. It also annotates all 21,803 threads with an LLM into one
schema-checked table, where what a person discusses predicts their rank almost as
well as how they email. That annotation layer ships in the `dataset-v4` release.

`pred-3/` fuses the two windows. Joined on 135 people they lift executive prediction
from 0.79 to 0.83 AUC, a gain that survives shuffling the content, though the fine
seniority ladder is already saturated by metadata alone. A companion notebook turns
the same fusion on identity: word and character n-grams name the writer of a message
two times in three out of 110, and the misses fall on close colleagues.

`pred-3-extra/` carries two follow-ups. One collapses the title ladder to three
tiers and finds metadata places a person at 0.52 balanced accuracy, with the
middle-management band the hard part. The other swaps the authorship word features
for a MiniLM embedding, which names the writer 36 percent of the time against the
words' 68, since a general encoder reads for meaning and misses the spelling that
fingerprints a person.

`WHOS_WHO.md` is a short reference for the people who keep appearing in the
notebooks: company shape, divisions, executive hierarchy, profiles for the
named mailbox owners, and a collapse timeline.

## Schedule

Intended SS26 schedule. Past sessions are ticked.

| Done | Date    | Topic                                          | Done | Date    | Topic                  |
|:----:|---------|------------------------------------------------|:----:|---------|------------------------|
| [x]  | Apr 15  | Kick-off                                       | [x]  | Jun 3   | Descriptive Mining 5   |
| [x]  | Apr 22  | No class                                       | [x]  | Jun 10  | Descriptive Mining 6   |
| [x]  | Apr 29  | Data Set Presentation                          | [x]  | Jun 17  | Predictive Mining 1    |
| [x]  | May 6   | Data Set Selection / Group Formation / EDA 1   | [x]  | Jun 24  | Predictive Mining 2    |
| [x]  | May 13  | Descriptive Mining 2                           | [x]  | Jul 1   | Predictive Mining 3    |
| [x]  | May 20  | Descriptive Mining 3                           | **[x]**  | Jul 8   | Final Presentation 1   |
| [x]  | May 27  | Descriptive Mining 4                           | [ ]  | Jul 15  | Final Presentation 2   |
