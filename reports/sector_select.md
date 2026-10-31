# Choosing sector panels by their past fit (K22-K26)

`scripts/run_sector_select.py`: 100 candidate panels per test and budget, 3 box readings each, seed 2+t. Held-out seats moved of a random candidate, of the best by replay on the two previous transitions, and of the best 10% by replay; Spearman correlation of replay and held-out.

|   budget |   random |   best_replay |   top10pct_replay |   spearman |
|---------:|---------:|--------------:|------------------:|-----------:|
|    0.015 |     2.68 |          2.13 |              2.74 |       0.06 |
|    0.02  |     2.38 |          1.8  |              2.42 |      -0.03 |

## Per test

|             |   random |   best_replay |   top10pct_replay |   spearman |
|:------------|---------:|--------------:|------------------:|-----------:|
| (0.015, 22) |     2.35 |          2.33 |              2.23 |       0.08 |
| (0.015, 23) |     2.1  |          2    |              1.97 |      -0.08 |
| (0.015, 24) |     3.03 |          2.33 |              2.83 |       0.07 |
| (0.015, 25) |     3.37 |          2    |              4.17 |      -0.08 |
| (0.015, 26) |     2.57 |          2    |              2.5  |       0.3  |
| (0.02, 22)  |     2.01 |          1.33 |              1.77 |       0.12 |
| (0.02, 23)  |     1.74 |          1.67 |              1.83 |      -0.06 |
| (0.02, 24)  |     2.62 |          2.67 |              2.6  |      -0.08 |
| (0.02, 25)  |     3.18 |          2    |              3.57 |      -0.09 |
| (0.02, 26)  |     2.35 |          1.33 |              2.33 |      -0.04 |
