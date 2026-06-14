# pred-1 (Predictive Mining 1)

This folder holds the first predictive-mining work and the body-text
prediction notebook it follows from. Both read the cleaned tables under
`eda-5/clean/`.

## How solid are the behavioural groups?

`pred1_group_certainty.ipynb` corrects the week-five clustering, then
stress-tests it before the prediction work leans on it. Week five folded two
assistants' mail into the executives they work for (Rosalee Fleming into
`lay-k`, Sherri Sera into `skilling-j`), so it was partly clustering offices
rather than people. This notebook drops those delegate sends (from
`eda-5/refs/assistant_delegates.csv`) and re-clusters on genuine authorship:
Ken Lay then keeps only 22 of his 344 messages and falls below the floor, the
roster goes from 143 to 142, and the broadcaster group tightens from eight to
six (Liz Taylor's desk moves to the internal majority). The silhouette even
rises a little, to about 0.20.

It then pushes on two soft spots. First, whether the six-person broadcaster
group is one we can name: each member's silhouette, how often each returns to
the cluster across six hundred 80% resamples, and whether the six survive
k-means and deeper Ward cuts. The six are stable (every one returns in at least
97% of resamples and they stay together under every method), but only one of
them, Skilling, is a company executive, and he is the least typical member;
the rest are operational, legal and trading staff. The softest point is telling:
the non-member most often pulled in is Liz Taylor's desk, the executive office
the fix took out. Second, which features do the separating. It reproduces the
week-five profile heatmap (each group's mean feature value in standard
deviations from the three-group mean) and digs into the cells that fall within
0.1 of the mean: only two do, the broadcasters on tenure and the internal
majority on thread-opening, where a group sits at the midpoint. The heatmap is
a trap, though, because standardising over three group means flattens every
feature to about one standard deviation (weekend share reads minus 1.15 for the
broadcasters yet only minus 0.23 against the population). An eta-squared per
feature keeps the within-group spread and shows the truth: the split runs on
recipients per message and broadcast share, while weekend share, thread-opening
and active months barely move. Week five itself is left unchanged; this is the
corrected re-run. Figures land
in `pred-1/plots/` (the `pc*` files):

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
