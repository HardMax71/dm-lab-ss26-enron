# dm-lab-ss26-enron

Code and notebooks for the Enron email corpus, used as the project dataset in
the Data Mining practical course, Summer Semester 2026.

## Dataset

CMU Enron release: https://www.cs.cmu.edu/~enron/. The corpus has about 517k
message files from 150 mailbox owners. The 423 MB tarball is too large for git
and ships as an asset on the latest release of this repo. Unpacking gives an
`./enron_mail/` tree of roughly 2.6 GB.

After downloading `enron_mail_20150507.tar.gz` into the repo root:

```
tar -xzf enron_mail_20150507.tar.gz
python inspect_enron.py
jupyter lab eda-2/enron_eda.ipynb
```

The cleaned, deduplicated version of the corpus (the parquet tables built
under `eda-5/clean/`) is published separately as the `dataset-v2` release.

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

`eda-6/` is the week-six prediction work, asking what the message body alone
gives away about its writer. The person is easy to name and the behavioural
group is not.

`WHOS_WHO.md` is a short reference for the people who keep appearing in the
notebooks: company shape, divisions, executive hierarchy, profiles for the
named mailbox owners, and a collapse timeline.

## Schedule

Intended SS26 schedule. Past sessions are ticked.

| Done | Date    | Topic                                          | Done | Date    | Topic                  |
|:----:|---------|------------------------------------------------|:----:|---------|------------------------|
| [x]  | Apr 15  | Kick-off                                       | [x]  | Jun 3   | Descriptive Mining 5   |
| [x]  | Apr 22  | No class                                       | [x]  | Jun 10  | Descriptive Mining 6   |
| [x]  | Apr 29  | Data Set Presentation                          | [ ]  | Jun 17  | Predictive Mining 1    |
| [x]  | May 6   | Data Set Selection / Group Formation / EDA 1   | [ ]  | Jun 24  | Predictive Mining 2    |
| [x]  | May 13  | Descriptive Mining 2                           | [ ]  | Jul 1   | Predictive Mining 3    |
| [x]  | May 20  | Descriptive Mining 3                           | [ ]  | Jul 8   | Final Presentation 1   |
| [x]  | May 27  | Descriptive Mining 4                           | [ ]  | Jul 15  | Final Presentation 2   |
