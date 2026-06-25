# pred-3 (Predictive Mining 3)

This folder builds straight on pred-2. `pred3_content_metadata_fusion.ipynb`
reads the cleaned tables under `eda-5/clean/` and the thread annotations from
`pred-2/thread_annotations.parquet`, runs in one pass, and writes its figures to
`pred-3/plots/` (the `f*` files).

## The question

pred-2 ended with two separate readings of a person's rank. One came from
metadata, the way someone emails: how much they send, how many people they
reach, how many distinct people write back. That put executive status at AUC
0.80. The other came from content, what they talk about, read off the LLM thread
annotations: the mix of conversation categories they take part in. On its own it
reached 0.73. The two look like they could be the same signal seen twice.

pred-3 tests that. It rebuilds the twelve metadata features unchanged and adds a
sixteen-feature content block taken only from the annotations (the eight-way
category mix, how often a person's threads name a regulator, a counterparty, an
Enron desk or a contract instrument, and the rate at which those threads carry a
request, reach a decision, or end resolved or open). Nothing in the content block
touches the job titles. Everything runs on one fixed set of 135 mailbox owners
so metadata, content and the fused block of both are scored on the same people,
with the scaler inside every fold and the external Shetty-Adibi titles as the
target.

## What the notebook finds

- **The two windows are not the same.** Put on a common rank-skill scale (zero is
  chance, one is perfect), metadata and content predict executive status about
  equally well alone, around 0.79 and 0.78 AUC, but the fused block reaches about
  0.83. The gain holds across every fold-shuffle (f1).
- **The extra signal is real, and it is about deciding.** Holding metadata fixed
  and shuffling the content rows a thousand times erases the gain, so it is not
  the larger model fitting noise (p around 0.001). The content the metadata never
  carried is an executive's place in threads that reach a decision or stay open,
  in legal and reporting traffic, set against the request-carrying trading and
  deal work that marks everyone else (f2).
- **The fine ordinal is a different story.** For the full one-to-seven title
  ladder, metadata already reaches a rank correlation near 0.49 and content adds
  nothing measurable (about +0.01). The lift is specific to the executive
  boundary, not the whole hierarchy.
- **The model places the middle and misses the summit.** Predicted seniority,
  snapped to the nearest of the seven ranks, lands within one rank of the truth
  for 70% of people, but the most senior names (Skilling, Delainey) are pulled
  down toward the middle. With a dozen people above vice president and a
  regression that pays for large errors, the top of the ladder stays out of reach
  (f3).

## Honesty

The common set is 135 people, 40 of them executives, so the numbers are read off
a small sample and reported with the spread from forty repeated cross-validation
runs rather than a single split. The headline gain (executive AUC, fused over
metadata) is small in absolute terms, about four points, and earns its place
through the permutation test on the difference, not its size. The seniority side
is reported as a near-zero result on purpose: fusing does not help there, and the
notebook says so.

```
uv run --with jupyter --with pandas --with pyarrow --with numpy --with scikit-learn \
  --with scipy --with plotly --with "kaleido==0.2.1" --with pillow \
  jupyter lab pred-3/pred3_content_metadata_fusion.ipynb
```
