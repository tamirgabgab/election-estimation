# Chosen sector model, held-out (K22-K26)

`scripts/run_sector_heldout.py`, model {'sectors': 'cluster', 'k': 12, 'spread': 'list', 'estimator': 'ratio'}: 100 panels per test and budget (direct point), the first 20 also with 200 within-sector bootstrap replicates (medoid, 90% intervals), seed 6+t, one random box per area. `*_2`: share of panels within 2 seats.

|   budget |   areas |   direct |   direct_2 |   medoid |   medoid_2 |   coverage |   outside |   width |   brier |   worst_election |
|---------:|--------:|---------:|-----------:|---------:|-----------:|-----------:|----------:|--------:|--------:|-----------------:|
|    0.01  | 103     |     3.2  |      0.445 |    3.4   |      0.45  |      0.964 |     0.174 |   2.505 |   0.208 |             4    |
|    0.015 | 154.245 |     2.68 |      0.62  |    2.5   |      0.625 |      0.981 |     0.1   |   2.097 |   0.168 |             3.38 |
|    0.02  | 206.785 |     2.42 |      0.6   |    2.325 |      0.7   |      0.973 |     0.137 |   1.777 |   0.121 |             2.9  |

## Per test

|             |   direct |   medoid |   coverage |
|:------------|---------:|---------:|-----------:|
| (0.01, 22)  |     2.4  |     2.35 |       0.96 |
| (0.01, 25)  |     4    |     4.45 |       0.97 |
| (0.015, 22) |     1.98 |     1.6  |       0.99 |
| (0.015, 25) |     3.38 |     3.4  |       0.97 |
| (0.02, 22)  |     1.94 |     1.65 |       0.97 |
| (0.02, 25)  |     2.9  |     3    |       0.97 |
