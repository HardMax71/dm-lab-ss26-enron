# eda-6 (week 6): body-to-group and body-to-person prediction

`enron_eda_week6.ipynb` is the week-six prediction notebook, on the cleaned
message body alone. It labels each body with its author's behavioural group
and trains a linear classifier over three text representations (a sparse
TF-IDF vector, a 200-dimension truncated-SVD embedding, and character
three/four-grams), then asks two questions: which behavioural group the author
belongs to, scored on held-out people so the model cannot win by memorising
authors, and which person wrote the message. The group is not recoverable from
the body for an unseen author (every representation lands at or below the
majority baseline once whole people are held out), but the individual is
highly recognisable (about three quarters accuracy among ten candidates). A
person-embedding content map and a per-person distinctive-words chart show
what the body does encode: topic and desk, not the behavioural role.

`WEEK6_REPORT.md` is the written page; figures land in `eda-6/plots/` (the
`w6_*` files):

```
uv run --with jupyter --with pandas --with pyarrow --with scikit-learn \
  --with scipy --with plotly --with "kaleido==0.2.1" --with pillow \
  jupyter lab eda-6/enron_eda_week6.ipynb
```
