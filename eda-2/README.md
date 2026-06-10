# eda-2 (week 2): first exploration

`enron_eda.ipynb` is the original exploratory notebook. It builds the cached
parquet tables under `eda-2/cache/` and writes plots to `eda-2/plots/`. Every
later report reads from that same cache, so it has to run first, and it needs
the unpacked maildir (see the Dataset section of the top-level README).

The script `inspect_enron.py` in the repo root is a separate sanity pass over
the unpacked maildir; it prints message counts, threading-header coverage,
declared charsets, the largest folders, and frequent sender domains.

```
python inspect_enron.py
jupyter lab eda-2/enron_eda.ipynb
```
