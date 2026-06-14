# pred-1 (Predictive Mining 1)

This folder holds the first predictive-mining work and the body-text
prediction notebook it follows from. Both read the cleaned tables under
`eda-5/clean/`.

## How solid are the behavioural groups?

`pred1_group_certainty.ipynb` stress-tests the week-five clustering before the
prediction work leans on it. It rebuilds the same twelve-feature Ward
clustering, then pushes on two soft spots. First, whether the eight-person
broadcaster/exec group is a group we can actually name: it checks each member's
silhouette, how often each returns to the broadcaster cluster across six hundred
80% resamples, and whether the eight survive k-means and deeper Ward cuts. The
eight-person core is stable (each returns in at least 95% of resamples and the
eight stay together under every method), but the two CEOs are its least typical
members, it is not the executive suite, and the boundary is soft, with a
rotating fringe joining about half the time. Second, which features do the
separating: an eta-squared per feature shows the split runs on recipients per
message and broadcast share, while weekend share, thread-opening and deletion
rate barely move between groups. That also exposes the week-five profile
heatmap, whose standardisation across three group means flattened every feature
to about one standard deviation and made the weak ones look as defining as the
strong ones. Figures land in `pred-1/plots/` (the `pc*` files):

```
uv run --with jupyter --with pandas --with pyarrow --with scikit-learn \
  --with scipy --with plotly --with "kaleido==0.2.1" --with pillow \
  --with matplotlib jupyter lab pred-1/pred1_group_certainty.ipynb
```

## Body-to-group and body-to-person prediction

`enron_eda_week6.ipynb` works on the cleaned message body alone. It labels each
body with its author's behavioural group and trains a linear classifier over
three text representations (a sparse TF-IDF vector, a 200-dimension
truncated-SVD embedding, and character three/four-grams), then asks two
questions: which behavioural group the author belongs to, scored on held-out
people so the model cannot win by memorising authors, and which person wrote
the message. The group is not recoverable from the body for an unseen author
(every representation lands at or below the majority baseline once whole people
are held out), but the individual is highly recognisable (about three quarters
accuracy among ten candidates). A person-embedding content map and a per-person
distinctive-words chart show what the body does encode: topic and desk, not the
behavioural role.

`WEEK6_REPORT.md` is the written page; figures land in `pred-1/plots/` (the
`w6_*` files):

```
uv run --with jupyter --with pandas --with pyarrow --with scikit-learn \
  --with scipy --with plotly --with "kaleido==0.2.1" --with pillow \
  jupyter lab pred-1/enron_eda_week6.ipynb
```
