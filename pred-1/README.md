# pred-1 (Predictive Mining 1)

This folder holds the first predictive-mining work. `pred1_group_certainty.ipynb`
reads the cleaned tables under `eda-5/clean/` and runs in one pass; its figures
land in `pred-1/plots/` (the `pc*` files).

## How solid are the behavioural groups, and what predicts them?

Week five folded two assistants' mail into the executives they work for (Rosalee
Fleming into `lay-k`, Sherri Sera into `skilling-j`), so it was partly clustering
offices rather than people. The notebook drops those delegate sends (from
`eda-5/refs/assistant_delegates.csv`) and re-clusters on genuine authorship: Ken
Lay then keeps only 22 of his 344 messages and falls below the floor, the roster
goes from 143 to 142, and the broadcaster group tightens from eight to six (Liz
Taylor's desk moves to the internal majority). The silhouette rises a little, to
about 0.20. Week five itself is left unchanged; this is the corrected re-run.

It then runs four checks on that result.

- **Can we name the broadcasters?** Each member's silhouette, how often each
  returns across six hundred 80% resamples, and whether the six survive k-means
  and deeper Ward cuts. The six are stable (each returns in at least 97% of
  resamples), but only Skilling is a company executive and he is the least typical
  member; the rest are operational, legal and trading staff.
- **Which features separate the groups?** The week-five profile heatmap makes
  every feature look equally defining, which is an artefact of standardising over
  three group means. An eta-squared per feature keeps the within-group spread and
  shows the split runs on recipients per message and broadcast share, while
  weekend share, thread-opening and active months barely move.
- **Do the groups predict from metadata?** A logistic model on the features,
  added in eta-squared order and scored leave-one-person-out, places an unseen
  person in the right group at about 94% (and 90% from five features), where the
  message body never beat the baseline in week five. The group is a metadata
  fact, not a content one.
- **A week-five correlation re-examined.** The weekend-versus-recipients
  correlation was read in week five as a newsletter effect. Filtering newsletters
  leaves it unchanged (0.61 to 0.62), but a Pearson r of 0.61 against a rank
  correlation of 0.14 marks it as two outlier mailboxes, not newsletters.

```
uv run --with jupyter --with pandas --with pyarrow --with scikit-learn \
  --with scipy --with plotly --with "kaleido==0.2.1" --with pillow \
  --with matplotlib jupyter lab pred-1/pred1_group_certainty.ipynb
```
