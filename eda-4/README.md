# eda-4 (week 3): deeper pass after the review

`enron_eda_deeper.ipynb` extends the first-week report along the lines flagged
in the week-2 review: year-by-year activity rhythm, a readable sender-domain
plot, the round-trip and social-graph structure (with a BCC-is-a-copy-of-CC
data caveat), a content drill on the `california` and `ees` threads,
per-mailbox deletion statistics, and a per-mailbox feature correlation.
Figures land in `eda-4/plots/`:

```
uv run --with jupyter --with pandas --with pyarrow --with matplotlib \
  --with seaborn --with networkx jupyter lab eda-4/enron_eda_deeper.ipynb
```
