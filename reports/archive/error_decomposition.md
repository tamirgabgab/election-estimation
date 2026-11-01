# Seat error decomposition (held-out within-bloc swing panels)

Source: `reports/within_panel/lists_<t>.csv` (settlements 20-150, tests 22-26), built by `scripts/diagnose_errors.py`. Columns are seats moved; `smooth` is the share L1 of passing lists in seats (no rounding); `bloc_<b>` is the signed seat error of the bloc (prediction minus truth).

Share of all seats moved: threshold 21%, bloc totals 29%, within bloc 50%.

## By panel size

|   k |   seats_moved |   threshold |   bloc |   within |   smooth |   wrong_side |   new_lists_moved |
|----:|--------------:|------------:|-------:|---------:|---------:|-------------:|------------------:|
|  20 |           3.4 |         0.8 |    1.2 |      1.4 |     2.48 |          0.2 |               1.2 |
|  30 |           3.2 |         0.6 |    1   |      1.6 |     2.19 |          0.2 |               1.1 |
|  35 |           3.2 |         0.6 |    0.6 |      2   |     2.43 |          0.2 |               1.2 |
|  40 |           3.2 |         0.6 |    0.8 |      1.8 |     2.39 |          0.2 |               1.3 |
|  50 |           3.2 |         0.4 |    0.8 |      2   |     2.47 |          0.2 |               1.4 |
|  70 |           2.8 |         0.6 |    1.2 |      1   |     2.36 |          0.2 |               1.1 |
| 100 |           2.6 |         0.8 |    0.6 |      1.2 |     2.18 |          0.2 |               1.1 |
| 150 |           2.8 |         0.8 |    0.8 |      1.2 |     1.96 |          0.2 |               1.1 |

## By test election (mean over sizes)

|   test |   seats_moved |   threshold |   bloc |   within |   smooth |   wrong_side |   new_lists_moved |   bloc_right |   bloc_haredi |   bloc_center_left |   bloc_arab |   bloc_other |
|-------:|--------------:|------------:|-------:|---------:|---------:|-------------:|------------------:|-------------:|--------------:|-------------------:|------------:|-------------:|
|     22 |          1.5  |        0    |   0.75 |     0.75 |     1.59 |            0 |              0.69 |         0.5  |         -0.12 |               0.62 |       -1    |            0 |
|     23 |          1.5  |        0    |   0.38 |     1.12 |     1.15 |            0 |              0.06 |         1.38 |         -0.38 |               0    |       -1    |            0 |
|     24 |          3.62 |        0    |   1.25 |     2.38 |     3.05 |            0 |              1.56 |        -0.62 |         -0.12 |              -1.25 |        2    |            0 |
|     25 |          5.12 |        3.25 |   0    |     1.88 |     2.5  |            1 |              2.25 |        -2.62 |         -1.38 |              -0.88 |        4.88 |            0 |
|     26 |          3.5  |        0    |   2    |     1.5  |     3.26 |            0 |              1.38 |         0.88 |          0.88 |               1    |       -2.75 |            0 |
