# pred-3-extra

Two follow-ups to pred-3, the last experiments before the final deck. Each reuses a
pred-3 pipeline and sharpens a question pred-3 left open. The first coarsens the rank
target so the top of the hierarchy is reachable. The second replaces the hand-made
word features with a learned encoder.

## Three tiers instead of seven rungs

`three_tier_seniority.ipynb` reuses the pred-3 rank builder without change: the same
135 mailbox owners, the same twelve metadata features and sixteen content features,
the same external job titles. pred-3 read the full one-to-seven title ladder and
could order the middle of it but never the top, because only about a dozen people
sit above vice president and the senior rungs are nearly empty. This collapses the
ladder to three tiers, workers (rank 1, 56 people), management (ranks 2 and 3, 39),
and executives (ranks 4 to 7, 40). The top tier is exactly the pred-3 executive
group, so the coarse question nests inside the binary one that week already answered.

How a person emails places them in the right tier with a balanced accuracy of 0.52,
well above a label-shuffling ceiling near 0.41, and what they discuss adds nothing
once fused, the same result pred-3 found on the fine ladder. The three-by-three
confusion shows where that skill sits. Workers and executives are recovered 54 and
60 percent of the time and almost never trade places, only 11 percent of people land
two tiers off. The soft spot is the middle: management is caught just 36 percent of
the time and leaks both ways. The executive tier that the seven-rung model compressed
toward the middle comes back here as a class you can actually call.

## The author from a learned encoder

`authorship_embeddings.ipynb` reuses the pred-3 authorship setup: 110 authors with at
least 120 keepable messages, up to 600 sampled each, and a thread-grouped split so a
test message never shares a conversation with a training one. pred-3 named the writer
from word and character n-grams, a stylistic fingerprint built by hand, and reached
about 68 percent. This swaps that fingerprint for a 384-dimensional MiniLM embedding
of each message body, run through fastembed (ONNX, no GPU needed), and classifies the
author from the vector.

The encoder names 36 percent of messages, forty times chance but only half of what
the words reach, and fusing the two adds nothing. A general-purpose encoder places
text by meaning and smooths over the spelling and spacing that give a writer away, so
for identity the characters win. The encoder is still reading something real, just not
identity. Mapped to one point per author, its space does not sort people by rank, but
the pairs the word model most often confuses sit closer in it than a typical pair does,
0.18 against 0.22. People who work the same desk write about the same things, crowd
the same corner of encoder space, and are the ones mistaken for each other.

## Running

From the repo root. The three-tier notebook needs no encoder:

    uv run --with pandas --with pyarrow --with scikit-learn --with scipy \
      --with plotly --with kaleido --with pillow --with nbconvert --with ipykernel \
      jupyter nbconvert --to notebook --execute --inplace \
      pred-3-extra/three_tier_seniority.ipynb

    uv run --with fastembed --with pandas --with pyarrow --with scikit-learn --with scipy \
      --with plotly --with kaleido --with pillow --with nbconvert --with ipykernel \
      jupyter nbconvert --to notebook --execute --inplace \
      pred-3-extra/authorship_embeddings.ipynb

The first run of the authorship notebook encodes about 48,000 message bodies with
MiniLM and caches the result under `pred-3-extra/work/`, so later runs reload it in
seconds. The words baseline is read from the pred-3 score cache at
`pred-3/work/auth_scores.pkl`; if that file is absent the notebook refits it. The
`work/` directory holds only caches and is not tracked.
