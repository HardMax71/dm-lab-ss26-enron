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

## Layout

The folders are numbered by the session they belong to. `eda/` is week one
(team matching and dataset selection); there is no analysis there.

`eda-2/enron_eda.ipynb` is the original exploratory notebook. It builds the
cached parquet tables under `eda-2/cache/` and writes plots to `eda-2/plots/`.
Every later report reads from that same cache, so it has to run first. The
script `inspect_enron.py` is a separate sanity pass over the unpacked maildir;
it prints message counts, threading-header coverage, declared charsets, the
largest folders, and frequent sender domains.

`eda-3/enron_eda_report.ipynb` is the written first-week report. It reads top to
bottom, pairing each plot with what it shows, and covers the variables, the main
distributions, and a closer look at deleted mail. It reuses the cached tables in
`eda-2/cache/`, so it runs without the 2.6 GB maildir and writes its figures to
`eda-3/plots/`:

```
uv run --with jupyter --with pandas --with pyarrow --with matplotlib \
  --with seaborn jupyter lab eda-3/enron_eda_report.ipynb
```

`eda-4/enron_eda_deeper.ipynb` extends the first-week report along the lines
flagged in the week-2 review: year-by-year activity rhythm, a readable
sender-domain plot, the round-trip and social-graph structure (with a
BCC-is-a-copy-of-CC data caveat), a content drill on the `california` and
`ees` threads, per-mailbox deletion statistics, and a per-mailbox feature
correlation. Figures land in `eda-4/plots/`:

```
uv run --with jupyter --with pandas --with pyarrow --with matplotlib \
  --with seaborn --with networkx jupyter lab eda-4/enron_eda_deeper.ipynb
```

`eda-5/enron_eda_week4.ipynb` works through the week-four review points: a
recoloured 24-hour activity plot (volume and per-year shape on separate honest
scales), a completeness audit (the 517k files are about 252k distinct messages,
with intact identity and timing headers but no threading headers and only a
fifth of internal recipients covered by a mailbox), address-to-person
resolution so the social plots count people not addresses, a reciprocal-cycle
search that surfaces the senior-executive clique, the California and EES word
charts on one shared scale, and a deletion analysis over time and by topic.
Figures land in `eda-5/plots/`:

```
uv run --with jupyter --with pandas --with pyarrow --with matplotlib \
  --with seaborn --with networkx jupyter lab eda-5/enron_eda_week4.ipynb
```

`eda-5/clean_dataset.py` turns the raw corpus into a deduplicated,
body-cleaned, thread-aware dataset under `eda-5/clean/`: `messages_clean.parquet`
(one row per unique message, with the cleaned body and quality flags) and
`recipients_clean.parquet` (one row per To/Cc delivery). It drops the 51% of
files that are duplicate copies, strips quoted history from bodies, rebuilds the
recipient list, and reconstructs conversation threads. `DATASET_CLEANING.md`
documents every step, the results, and the limitations. Run it with:

```
uv run eda-5/clean_dataset.py
```

`WHOS_WHO.md` is a short reference for the people who keep appearing in the
notebooks: company shape, divisions, executive hierarchy, profiles for the
named mailbox owners, and a collapse timeline. Worth a read before the
network and content sections of `eda-4/`.

## Schedule

Intended SS26 schedule. Past sessions are ticked.

| Done | Date    | Topic                                          | Done | Date    | Topic                  |
|:----:|---------|------------------------------------------------|:----:|---------|------------------------|
| [x]  | Apr 15  | Kick-off                                       | [x]  | Jun 3   | Descriptive Mining 5   |
| [x]  | Apr 22  | No class                                       | [ ]  | Jun 10  | Descriptive Mining 6 ? |
| [x]  | Apr 29  | Data Set Presentation                          | [ ]  | Jun 17  | Predictive Mining 1    |
| [x]  | May 6   | Data Set Selection / Group Formation / EDA 1   | [ ]  | Jun 24  | Predictive Mining 2    |
| [x]  | May 13  | Descriptive Mining 2                           | [ ]  | Jul 1   | Predictive Mining 3    |
| [x]  | May 20  | Descriptive Mining 3                           | [ ]  | Jul 8   | Final Presentation 1   |
| [x]  | May 27  | Descriptive Mining 4                           | [ ]  | Jul 15  | Final Presentation 2   |
