# pred-2 (Predictive Mining 2)

This folder follows pred-1. `pred2_external_prediction.ipynb` reads the cleaned
tables under `eda-5/clean/` and runs in one pass; its figures land in
`pred-2/plots/` (the `pp*` files).

## Why a second notebook

pred-1 predicted the three behavioural groups from the twelve metadata features
and reported about 94% on a held-out person. That figure is circular. The groups
were produced by clustering those same features, so the classifier only has to
re-draw a boundary that already exists. Refitting on all 142 people scores 97%
and leaving one out scores 94%, a gap far too small for real generalisation, and
the cluster label is not even stable: drop one person, re-cluster the other 141,
and only 82% of held-out labels come back the same.

Predicting something honestly needs a target from outside the feature pipeline.
The job-title layer in `people_roles.parquet` (Shetty-Adibi, joined after the
fact) is exactly that. Nothing in the email features ever saw it, so the scaler
sits inside every cross-validation fold and a permutation null decides whether
each result could have come up by chance.

## What the notebook finds

- **The 94% measures separability.** pp1 puts the held-out score next to the
  refit score and the baseline and adds the re-clustering stability check. The
  number says how cleanly the partition splits its own feature space, which is a
  geometric property of the clustering, computed from the same features that built it.
- **Executive status predicts from metadata.** A balanced logistic model reaches
  an AUC of 0.80 (balanced accuracy 0.75) on whether a person is an executive.
  A permutation null over a thousand label shuffles centres on 0.50 and never
  reaches the observed value (p = 0.001), so the signal is genuine.
- **Seniority rank predicts too.** Treated as an ordinal target and scored by
  the rank correlation between prediction and truth, it comes back at a
  cross-validated Spearman of 0.47 against the same kind of null (p = 0.001).
- **The signal is in who writes to whom.** The standardised weights point at a
  high in-degree (many distinct people writing in) and more recipients per
  message, with mass-broadcasting pulling the other way. That is why seniority
  sat across the broadcast-driven three-way split in week five and only shows up
  once it is asked for directly.

pp3 puts the four targets on one axis, each scaled from chance to perfect: the
circular cluster label looks easiest, executive status and seniority carry real
but smaller signal, and the week-five message-body classifier lands below chance.

```
uv run --with jupyter --with pandas --with pyarrow --with scikit-learn \
  --with scipy --with plotly --with "kaleido==0.2.1" --with pillow \
  jupyter lab pred-2/pred2_external_prediction.ipynb
```

## Summarizing the threads with an LLM

The second strand annotates every genuine conversation in the corpus. From the
163,883 reconstructed threads, the summarizable set is the 21,803 genuine
multi-party exchanges (at least two distinct senders and at least two messages
that are not empty, boilerplate, or automated by the pipeline's own flags). Each
becomes one structured row through a fixed schema, and an LLM fills only the
content fields.

The pipeline is four steps:

- `build_threads.py` selects the 21,803 threads, assembles each as model-ready
  text in `thread_position` order, attaches the deterministic meta (executive
  involvement, outcome-free counts, generic-subject and truncation flags), and
  shards them under `work/shards/`.
- A pool of subagents annotates each shard against `ANNOTATION_SCHEMA.md`,
  writing one JSON object per thread. The run was paced in batches against the
  account's five-hour usage window.
- `validate_annotations.py` gates every shard with the Pydantic model in
  `annotation_model.py`: malformed JSON, a wrong enum, a missing field, or a
  thread_id that does not belong to the shard all fail it, and each annotator
  fixes its output until the gate passes.
- `merge_annotations.py` re-validates every line and folds in the meta, writing
  the 21,803-row `thread_annotations.parquet`. One row per thread: category,
  one-line and short summary, request/decision flags, outcome, participants with
  roles, entities, topics, plus the meta columns.

`pred2_thread_mining.ipynb` mines that table (figures `tm*` under `plots/`):

- **What Enron emailed about.** Deals and contracts and internal administration
  lead the volume; the substantive categories (deals, the California crisis,
  legal) are the ones most often left open, since the mailboxes catch them
  mid-flight.
- **Where the executives sit.** Crossing the category with the executive flag
  splits sharply: executives appear in 36% of threads overall but 73% of the
  California-crisis threads and about half of scheduling and legal, against only
  ~18% of deal-contract and trading. The deal and trading engine runs below the
  executive layer. This is the content-side echo of the metadata prediction
  above, seniority showing up in which conversations a person joins.
- **Asks and decisions.** Almost three quarters of threads carry a request, so
  the corpus is a working inbox; decisions are rarer and concentrate in the
  operational categories.

```
uv run --with jupyter --with pandas --with pyarrow --with plotly \
  --with "kaleido==0.2.1" --with pillow jupyter lab pred-2/pred2_thread_mining.ipynb
```
