# eda-5 (weeks 4 and 5): cleaning, completeness, clustering

This folder holds the dataset cleaning pipeline and the week-four and
week-five analysis on top of it. `WEEK5_REPORT.md` is the written week-five
page and `DATASET_CLEANING.md` documents the cleaning step by step.

## The cleaning pipeline

`clean_dataset.py` turns the raw corpus into a deduplicated, body-cleaned,
thread-aware dataset under `eda-5/clean/`: `messages_clean.parquet` (one row
per unique message, with the cleaned body and quality flags),
`recipients_clean.parquet` (one row per To/Cc delivery), and `people.parquet`
(one row per mailbox owner with their resolved sending addresses). It drops
the 51% of files that are duplicate copies, strips quoted history from bodies,
rebuilds the recipient list, reconstructs conversation threads, and resolves
each sender and recipient address to a mailbox owner where one is known,
written out as the `sender_person` and `recipient_person` columns. The
resolution treats the Sent folder as authoritative, recovers the two owners
with no usable Sent folder (`harris-s`, `stokley-c`) from their
surname-matching modal sender, and folds the garbled duplicate folder
`phanis-s` into the real `panus-s` (both are Stephanie Panus's `spanus.pst`).

```
uv run eda-5/clean_dataset.py
```

`enrich_people.py` adds an external label layer on top of the resolved owners:
it joins the Shetty-Adibi job-title annotation (vendored under `eda-5/refs/`,
one row per folder, 1:1 with the 149 owners) and a self-sourced Exchange `CN`
id parsed from each owner's `X-From` header, writing
`eda-5/clean/people_roles.parquet` (`display_name`, `title`, `seniority_rank`,
`is_executive`, `cn_id`, `title_source`). The titles are kept strictly
separate from the corpus-derived tables and every title column is tagged with
its source.

```
uv run eda-5/enrich_people.py
```

The resulting tables also ship as the
[`dataset-v3`](https://github.com/HardMax71/dm-lab-ss26-enron/releases/tag/dataset-v3)
release of this repo, with the timestamp column stripped there because of the
timezone encoding fault described in the week-5 report, and with the completed,
corrected job-title layer.

## The week-four notebook

`enron_eda_week4.ipynb` works through the week-four review points: a
recoloured 24-hour activity plot (volume and per-year shape on separate honest
scales), a completeness audit (the 517k files are about 252k distinct
messages, with intact identity and timing headers but no threading headers and
only a fifth of internal recipients covered by a mailbox), address-to-person
resolution so the social plots count people not addresses, a reciprocal-cycle
search that surfaces the senior-executive clique, the California and EES word
charts on one shared scale, and a deletion analysis over time and by topic.
Figures land in `eda-5/plots/`:

```
uv run --with jupyter --with pandas --with pyarrow --with matplotlib \
  --with seaborn --with networkx --with adjusttext --with plotly \
  --with "kaleido==0.2.1" --with pillow jupyter lab eda-5/enron_eda_week4.ipynb
```

## The week-five clustering notebook

`enron_eda_week5.ipynb` clusters the people behind the 149 mailboxes. It
builds a twelve-feature behavioural vector per owner (volume, reach, external
share, thread-opening, tenure, deletion, in/out degree), picks the number of
groups by silhouette, and reads three roles off a Ward hierarchy: a small
broadcaster/executive group, an outward-facing dealmaker group, and a large
internal majority. It pairs the clustering scatter with the dendrogram, a
cluster-profile heatmap, and cross-tabs against the week-four social
communities (orthogonal) and the external job titles (only weakly aligned with
rank: the vice-presidents mostly sit in the internal majority), then contrasts
a TF-IDF content view that deliberately fails to separate the groups, setting
up the body-to-group prediction `pred-1/enron_eda_week6.ipynb` carries out.
Running the notebook regenerates its `p*` figures under `eda-5/plots/`:

```
uv run --with jupyter --with pandas --with pyarrow --with matplotlib \
  --with seaborn --with scikit-learn --with scipy --with networkx --with plotly \
  --with "kaleido==0.2.1" --with pillow jupyter lab eda-5/enron_eda_week5.ipynb
```
