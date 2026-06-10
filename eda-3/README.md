# eda-3 (week 2): written report

`enron_eda_report.ipynb` is the written first-week report. It reads top to
bottom, pairing each plot with what it shows, and covers the variables, the
main distributions, and a closer look at deleted mail. It reuses the cached
tables in `eda-2/cache/`, so it runs without the 2.6 GB maildir and writes its
figures to `eda-3/plots/`:

```
uv run --with jupyter --with pandas --with pyarrow --with matplotlib \
  --with seaborn jupyter lab eda-3/enron_eda_report.ipynb
```
