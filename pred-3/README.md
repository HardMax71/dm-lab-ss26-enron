# pred-3 (Predictive Mining 3)

pred-3 takes the two-window idea from pred-2, how a person emails (metadata) and
what they write or discuss (content), and tests whether fusing the windows beats
either alone. It does this twice, in two notebooks that read the cleaned tables
under `eda-5/clean/` (and, for the first, the thread annotations from
`pred-2/thread_annotations.parquet`) and write their figures to `pred-3/plots/`.

- `pred3_content_metadata_fusion.ipynb` fuses the windows to predict **rank** (the
  `f*` figures).
- `pred3_authorship_fusion.ipynb` fuses them to predict the **author** of a single
  message (the `a*` figures).

## Predicting rank: content versus metadata

pred-2 ended with two separate readings of a person's rank. One came from
metadata, the way someone emails: how much they send, how many people they reach,
how many distinct people write back. That put executive status at AUC 0.80. The
other came from content, what they talk about, read off the LLM thread
annotations: the mix of conversation categories they take part in. On its own it
reached 0.73. The two look like they could be the same signal seen twice.

The notebook rebuilds the twelve metadata features unchanged and adds a
sixteen-feature content block taken only from the annotations (the eight-way
category mix, how often a person's threads name a regulator, a counterparty, an
Enron desk or a contract instrument, and the rate at which those threads carry a
request, reach a decision, or end resolved or open). Nothing in the content block
touches the job titles. Everything runs on one fixed set of 135 mailbox owners,
the scaler inside every fold, with the external Shetty-Adibi titles as the target.

- **The two windows are not the same.** On a common rank-skill scale (zero is
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
  down toward the middle, and the predicted axis never reaches the top two ranks
  (f3).

The common set is only 135 people, so the numbers are reported with the spread
from forty repeated cross-validation runs, and the headline gain (about four AUC
points) earns its place through the permutation test on the difference rather than
its size.

## Predicting the author: words versus the envelope

The second notebook points the same idea at identity, with the message as the unit
rather than the person. The content window is the message body as word one- and
two-grams plus character three- and four-grams (what someone writes, and how they
spell, space and punctuate it). The metadata window is the envelope of that one
message: recipients, carbon copies, outsiders, length, hour, thread position, and
nothing that names the sender. The target is the author, one of 110 people who
wrote at least 120 keepable messages, up to 600 each, on a thread-grouped split so
a test message never shares a thread, or its quoted text and signature, with a
training one. Both windows feed the same linear SVM, blended by their decision
margins.

- **The words carry most of the signal.** Word and character n-grams name the
  author of about 68% of messages out of 110 candidates, some seventy times
  chance, and 64% averaged evenly across authors (a1).
- **Most of it is style.** Redacting every owner's own name from the text drops the
  rate by roughly ten points, to the high fifties, so a name in the sign-off helps
  but the bulk is genuine writing, the vocabulary and the spelling habits the
  character n-grams catch (a1).
- **The envelope is weak alone but not redundant.** It names under a tenth of
  messages by itself, yet blended onto the words it still lifts the result by about
  a point and a half, fixing more than twice the messages it breaks (McNemar
  p around 1e-15). What it keys on is reach and length (a2).
- **The misses are structured.** Most authors are pinned down sharply; when the
  model slips, the wrong name is someone the true author actually emails far more
  often than chance would give (39% against 23%), and the most-confused pairs are
  desk colleagues (a3).

The contrast between the two notebooks is the point. For rank the windows were
complementary and joining them mattered; for identity the words dominate and the
envelope adds only a quiet second voice.

## Running

```
uv run --with jupyter --with pandas --with pyarrow --with numpy --with scikit-learn \
  --with scipy --with plotly --with "kaleido==0.2.1" --with pillow \
  jupyter lab pred-3/pred3_content_metadata_fusion.ipynb

uv run --with jupyter --with pandas --with pyarrow --with numpy --with scikit-learn \
  --with scipy --with plotly --with "kaleido==0.2.1" --with pillow \
  jupyter lab pred-3/pred3_authorship_fusion.ipynb
```
