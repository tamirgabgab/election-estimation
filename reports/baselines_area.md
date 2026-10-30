# Baselines - unit: area

Held-out evaluation: for every test election t, panels are chosen on the elections
before t only. Errors: `seat_L1` and `bloc_seat_L1` in seats, the others in
percentage points of valid votes; `threshold_errors` counts lists whose
pass / fail is predicted wrongly.

Settings: seed 0, 30 draws for random panels and single-box readings,
recency decay 0.7, 40 greedy candidates per step, panel sizes [10, 20, 35, 50, 70, 100];
MILP: pool 400, time limit 45s, budgets [50, 70].
`unit` reading counts whole panel units; `single_box` counts one random box per unit.
`k` is the number of panel units, except for the `*_budget` methods, where it is the
budget in ballot boxes (unit cost = its boxes in the last training election).
`boxes` is the number of ballot boxes actually counted in the test election:
compare methods at equal `boxes`, not equal `k`.
Methods: `all_boxes` pools every regular box (no sampling; its error is the
double-envelope gap); `random_pooled` draws units uniformly and pools their votes;
`random_pps` draws units in proportion to size and averages their shares;
`stratified` draws by size within strata (dominant bloc, pure / mixed) and weights
strata by votes; `greedy` is column generation with LP weights on the stacked
training elections; `greedy_budget` and `milp_budget` select under a box budget
(MILP keeps the greedy solution when it finds nothing better in time).

## Mean over recent test elections (22-26)

|                                        |    boxes |   seat_L1 |   share_L1 |   bloc_seat_L1 |   bloc_share_L1 |   threshold_errors |   max_list_error |
|:---------------------------------------|---------:|----------:|-----------:|---------------:|----------------:|-------------------:|-----------------:|
| ('all_boxes', 'unit', 'all')           | 11404    |      2.8  |       1.95 |           2.4  |            1.7  |               0    |             0.46 |
| ('greedy', 'single_box', '10')         |    10    |     24.07 |      18.26 |          19.16 |           13.97 |               0.47 |             4.4  |
| ('greedy', 'single_box', '20')         |    19.2  |     19.19 |      14.7  |          14.69 |           10.56 |               0.47 |             3.54 |
| ('greedy', 'single_box', '35')         |    34    |     16.76 |      11.93 |          12.55 |            8.91 |               0.65 |             3.03 |
| ('greedy', 'single_box', '50')         |    47.4  |     15.56 |      10.36 |          10.88 |            7.27 |               0.77 |             2.5  |
| ('greedy', 'single_box', '70')         |    58.8  |     14.17 |       9.66 |           9.95 |            6.65 |               0.68 |             2.39 |
| ('greedy', 'single_box', '100')        |    68.2  |     12.23 |       8.61 |           8.55 |            6.01 |               0.51 |             2.04 |
| ('greedy', 'unit', '10')               |    39.4  |     16    |      12.78 |          12    |            9.31 |               0.2  |             2.79 |
| ('greedy', 'unit', '20')               |    66.6  |     13.6  |      10.82 |           9.2  |            6.84 |               0.2  |             2.27 |
| ('greedy', 'unit', '35')               |   121.8  |     13.6  |       8.95 |           9.2  |            6.5  |               0.6  |             2.02 |
| ('greedy', 'unit', '50')               |   170.6  |     11.2  |       7.8  |           6.8  |            5.28 |               0.4  |             1.73 |
| ('greedy', 'unit', '70')               |   202.8  |     10.4  |       6.76 |           5.6  |            4.59 |               0.4  |             1.5  |
| ('greedy', 'unit', '100')              |   241.6  |      9.2  |       6.09 |           4.8  |            3.89 |               0.4  |             1.25 |
| ('greedy_budget', 'unit', '10')        |    10.6  |     23.6  |      17.55 |          19.6  |           14.25 |               0.8  |             3.73 |
| ('greedy_budget', 'unit', '20')        |    23.6  |     10    |       7.2  |           7.2  |            4.62 |               0.4  |             1.41 |
| ('greedy_budget', 'unit', '35')        |    38.6  |      8.4  |       6.45 |           5.6  |            3.91 |               0.2  |             1.34 |
| ('greedy_budget', 'unit', '50')        |    55.2  |     11.2  |       7.6  |           7.6  |            4.45 |               0.4  |             1.57 |
| ('greedy_budget', 'unit', '70')        |    72.4  |     12.4  |       8.49 |           6.4  |            4.4  |               0.4  |             1.83 |
| ('greedy_budget', 'unit', '100')       |    86    |     13.6  |       9.21 |           7.6  |            4.98 |               0.6  |             1.96 |
| ('milp_budget', 'unit', '50')          |    55.2  |     11.2  |       7.6  |           7.6  |            4.45 |               0.4  |             1.57 |
| ('milp_budget', 'unit', '70')          |    72.4  |     12.4  |       8.49 |           6.4  |            4.4  |               0.4  |             1.83 |
| ('random_pooled', 'single_box', '10')  |     9.75 |     49.51 |      36.33 |          40.68 |           29.73 |               2.45 |             8.98 |
| ('random_pooled', 'single_box', '20')  |    19.54 |     38.51 |      27.92 |          31.28 |           22.12 |               1.69 |             7.16 |
| ('random_pooled', 'single_box', '35')  |    34.07 |     30.75 |      22.01 |          26.56 |           18.48 |               1.43 |             5.56 |
| ('random_pooled', 'single_box', '50')  |    48.66 |     30.87 |      21.65 |          26.15 |           17.76 |               1.35 |             5.09 |
| ('random_pooled', 'single_box', '70')  |    68.18 |     26.57 |      18.24 |          22.44 |           14.67 |               1.17 |             4.19 |
| ('random_pooled', 'single_box', '100') |    97.41 |     25.17 |      17.18 |          21.53 |           14.19 |               1.15 |             3.93 |
| ('random_pooled', 'unit', '10')        |    41.17 |     57.73 |      41.9  |          50.79 |           36.98 |               2.65 |            11.98 |
| ('random_pooled', 'unit', '20')        |    85.06 |     43.77 |      31.57 |          38.16 |           27.64 |               1.73 |             9.84 |
| ('random_pooled', 'unit', '35')        |   150.03 |     36.35 |      26.13 |          32.21 |           22.85 |               1.45 |             7.86 |
| ('random_pooled', 'unit', '50')        |   203.85 |     28.51 |      20.28 |          24.51 |           17.11 |               1.08 |             5.66 |
| ('random_pooled', 'unit', '70')        |   294.89 |     23.55 |      17    |          20.68 |           14.8  |               0.74 |             5.02 |
| ('random_pooled', 'unit', '100')       |   417.19 |     20.29 |      14.26 |          17.85 |           12.38 |               0.67 |             4.32 |
| ('random_pps', 'single_box', '10')     |     9.79 |     46.05 |      33.69 |          37.65 |           27.57 |               2.09 |             8.78 |
| ('random_pps', 'single_box', '20')     |    19.57 |     31.79 |      22.88 |          26.39 |           18.81 |               1.31 |             6.02 |
| ('random_pps', 'single_box', '35')     |    34.15 |     24.69 |      17.68 |          20.09 |           14.1  |               0.86 |             4.6  |
| ('random_pps', 'single_box', '50')     |    48.99 |     20.28 |      14.49 |          16.29 |           11.36 |               0.68 |             3.75 |
| ('random_pps', 'single_box', '70')     |    68.58 |     17.8  |      12.88 |          15.03 |           10.42 |               0.55 |             3.28 |
| ('random_pps', 'single_box', '100')    |    97.91 |     15.33 |      11.05 |          13.31 |            9.28 |               0.5  |             2.9  |
| ('random_pps', 'unit', '10')           |    74.97 |     44.21 |      32.31 |          36.92 |           26.99 |               1.94 |             8.55 |
| ('random_pps', 'unit', '20')           |   147.79 |     30.43 |      21.89 |          25.89 |           18.46 |               1.23 |             5.83 |
| ('random_pps', 'unit', '35')           |   260.19 |     23.85 |      16.97 |          20    |           14.02 |               0.82 |             4.48 |
| ('random_pps', 'unit', '50')           |   375.29 |     19.57 |      13.75 |          16.24 |           11.14 |               0.7  |             3.6  |
| ('random_pps', 'unit', '70')           |   525.89 |     17.16 |      12.3  |          14.73 |           10.14 |               0.52 |             3.15 |
| ('random_pps', 'unit', '100')          |   738.21 |     14.59 |      10.56 |          12.84 |            8.99 |               0.42 |             2.85 |
| ('stratified', 'single_box', '10')     |    10.61 |     28.25 |      20.28 |          16.17 |           11.43 |               1.27 |             5.01 |
| ('stratified', 'single_box', '20')     |    19.58 |     21.35 |      15.4  |          10.96 |            7.58 |               0.82 |             3.57 |
| ('stratified', 'single_box', '35')     |    34.4  |     15.88 |      11.23 |           9.4  |            6.27 |               0.59 |             2.62 |
| ('stratified', 'single_box', '50')     |    48.85 |     13.12 |       9.83 |           8.32 |            5.84 |               0.36 |             2.39 |
| ('stratified', 'single_box', '70')     |    68.52 |     11.28 |       8.46 |           7.56 |            5.32 |               0.28 |             2.02 |
| ('stratified', 'single_box', '100')    |    98.01 |     10.19 |       7.64 |           7.44 |            5.12 |               0.23 |             1.86 |
| ('stratified', 'unit', '10')           |    79.23 |     25.05 |      17.7  |          14.16 |            9.93 |               1.11 |             4.38 |
| ('stratified', 'unit', '20')           |   144.28 |     19.39 |      13.73 |          10.59 |            7.06 |               0.74 |             3.26 |
| ('stratified', 'unit', '35')           |   258.67 |     14.12 |      10.08 |           8.44 |            5.73 |               0.47 |             2.39 |
| ('stratified', 'unit', '50')           |   369.29 |     11.89 |       8.8  |           7.45 |            5.18 |               0.33 |             2.19 |
| ('stratified', 'unit', '70')           |   513.41 |      9.92 |       7.55 |           7.2  |            4.91 |               0.25 |             1.86 |
| ('stratified', 'unit', '100')          |   757.26 |      9.37 |       6.95 |           7.03 |            4.85 |               0.21 |             1.73 |

## Mean over all test elections (20-26)

|                                        |    boxes |   seat_L1 |   share_L1 |   bloc_seat_L1 |   bloc_share_L1 |   threshold_errors |   max_list_error |
|:---------------------------------------|---------:|----------:|-----------:|---------------:|----------------:|-------------------:|-----------------:|
| ('all_boxes', 'unit', 'all')           | 11085.3  |      2.57 |       1.81 |           2    |            1.55 |               0    |             0.42 |
| ('greedy', 'single_box', '10')         |     9.86 |     29.63 |      21.39 |          23.8  |           16.52 |               1.12 |             5.06 |
| ('greedy', 'single_box', '20')         |    18.71 |     25.16 |      18.05 |          20.35 |           13.82 |               1.05 |             4.26 |
| ('greedy', 'single_box', '35')         |    30.43 |     22.74 |      15.3  |          18.12 |           12.05 |               1.16 |             3.87 |
| ('greedy', 'single_box', '50')         |    40    |     21.24 |      13.73 |          16.17 |           10.28 |               1.22 |             3.3  |
| ('greedy', 'single_box', '70')         |    48.14 |     20.94 |      13.69 |          16.25 |           10.28 |               1.2  |             3.31 |
| ('greedy', 'single_box', '100')        |    54.86 |     19.22 |      12.63 |          14.76 |            9.63 |               1.06 |             3.06 |
| ('greedy', 'unit', '10')               |    34.14 |     20.29 |      15.34 |          16    |           11.4  |               0.71 |             3.34 |
| ('greedy', 'unit', '20')               |    59    |     17.43 |      12.96 |          13.43 |            9.35 |               0.57 |             2.73 |
| ('greedy', 'unit', '35')               |   100    |     16.86 |      10.81 |          12.86 |            8.46 |               0.86 |             2.49 |
| ('greedy', 'unit', '50')               |   134.86 |     15.14 |       9.99 |          11.14 |            7.59 |               0.71 |             2.28 |
| ('greedy', 'unit', '70')               |   157.86 |     14.57 |       9.24 |          10.29 |            7.1  |               0.71 |             2.12 |
| ('greedy', 'unit', '100')              |   185.57 |     13.71 |       8.77 |           9.71 |            6.6  |               0.71 |             1.93 |
| ('greedy_budget', 'unit', '10')        |     9.86 |     28.57 |      21.44 |          22.29 |           16.04 |               1.14 |             4.57 |
| ('greedy_budget', 'unit', '20')        |    22.57 |     16.86 |      12.43 |          12.57 |            7.88 |               0.86 |             1.93 |
| ('greedy_budget', 'unit', '35')        |    35.29 |     14.57 |      10.25 |          11.43 |            6.73 |               0.71 |             1.72 |
| ('greedy_budget', 'unit', '50')        |    47.14 |     16.57 |      11.07 |          12.86 |            7.12 |               0.86 |             1.89 |
| ('greedy_budget', 'unit', '70')        |    59.43 |     17.43 |      11.7  |          12    |            7.09 |               0.86 |             2.08 |
| ('greedy_budget', 'unit', '100')       |    69.14 |     18.29 |      12.22 |          12.86 |            7.5  |               1    |             2.17 |
| ('milp_budget', 'unit', '50')          |    47.14 |     16.57 |      11.07 |          12.86 |            7.12 |               0.86 |             1.89 |
| ('milp_budget', 'unit', '70')          |    59.43 |     17.43 |      11.7  |          12    |            7.09 |               0.86 |             2.08 |
| ('random_pooled', 'single_box', '10')  |     9.78 |     51.47 |      36.63 |          42.94 |           30.31 |               2.82 |             9.35 |
| ('random_pooled', 'single_box', '20')  |    19.56 |     39.36 |      27.27 |          32.04 |           21.76 |               2.08 |             7.01 |
| ('random_pooled', 'single_box', '35')  |    34.19 |     31.75 |      21.69 |          27.39 |           18.25 |               1.78 |             5.6  |
| ('random_pooled', 'single_box', '50')  |    48.8  |     31.52 |      21.03 |          26.47 |           17.23 |               1.68 |             4.98 |
| ('random_pooled', 'single_box', '70')  |    68.31 |     27.53 |      17.91 |          23.12 |           14.38 |               1.51 |             4.25 |
| ('random_pooled', 'single_box', '100') |    97.58 |     26.26 |      17.08 |          22.44 |           14.09 |               1.45 |             4.06 |
| ('random_pooled', 'unit', '10')        |    40.08 |     58.78 |      41.71 |          51.55 |           36.84 |               2.95 |            12.04 |
| ('random_pooled', 'unit', '20')        |    82.05 |     44.65 |      31.17 |          38.93 |           27.4  |               2.02 |             9.7  |
| ('random_pooled', 'unit', '35')        |   145.64 |     36.47 |      25.15 |          31.89 |           21.98 |               1.7  |             7.55 |
| ('random_pooled', 'unit', '50')        |   198.34 |     28.9  |      19.47 |          24.66 |           16.51 |               1.37 |             5.45 |
| ('random_pooled', 'unit', '70')        |   286.86 |     24.5  |      17.05 |          21.65 |           14.92 |               0.95 |             5.09 |
| ('random_pooled', 'unit', '100')       |   404.44 |     21.27 |      14.17 |          18.5  |           12.32 |               0.91 |             4.28 |
| ('random_pps', 'single_box', '10')     |     9.84 |     46.82 |      33.01 |          37.8  |           26.91 |               2.41 |             8.64 |
| ('random_pps', 'single_box', '20')     |    19.62 |     32.62 |      22.8  |          26.85 |           18.57 |               1.51 |             5.98 |
| ('random_pps', 'single_box', '35')     |    34.28 |     25.84 |      17.43 |          20.92 |           14.02 |               1.18 |             4.52 |
| ('random_pps', 'single_box', '50')     |    49.15 |     21.44 |      14.73 |          17.37 |           11.71 |               0.9  |             3.77 |
| ('random_pps', 'single_box', '70')     |    68.74 |     18.52 |      12.69 |          15.37 |           10.23 |               0.75 |             3.23 |
| ('random_pps', 'single_box', '100')    |    98.15 |     15.45 |      10.66 |          13.01 |            8.81 |               0.61 |             2.74 |
| ('random_pps', 'unit', '10')           |    70.81 |     45.05 |      31.8  |          37.14 |           26.43 |               2.25 |             8.43 |
| ('random_pps', 'unit', '20')           |   141.36 |     31.22 |      21.77 |          26.33 |           18.17 |               1.43 |             5.8  |
| ('random_pps', 'unit', '35')           |   247.74 |     24.86 |      16.72 |          20.71 |           13.82 |               1.1  |             4.4  |
| ('random_pps', 'unit', '50')           |   354.7  |     20.62 |      13.98 |          17.12 |           11.43 |               0.87 |             3.64 |
| ('random_pps', 'unit', '70')           |   499.11 |     17.9  |      12.17 |          15.1  |           10.04 |               0.72 |             3.12 |
| ('random_pps', 'unit', '100')          |   699.31 |     14.76 |      10.19 |          12.6  |            8.57 |               0.54 |             2.7  |
| ('stratified', 'single_box', '10')     |    11.4  |     28.36 |      19.39 |          16.46 |           11.04 |               1.5  |             4.74 |
| ('stratified', 'single_box', '20')     |    20.06 |     21.64 |      14.87 |          11.63 |            7.66 |               1.01 |             3.41 |
| ('stratified', 'single_box', '35')     |    34.43 |     16.41 |      10.98 |           9.54 |            6.22 |               0.75 |             2.5  |
| ('stratified', 'single_box', '50')     |    49.01 |     13.41 |       9.58 |           8.47 |            5.8  |               0.52 |             2.26 |
| ('stratified', 'single_box', '70')     |    68.76 |     11.62 |       8.24 |           7.75 |            5.16 |               0.42 |             1.93 |
| ('stratified', 'single_box', '100')    |    98.32 |     10.48 |       7.48 |           7.16 |            4.93 |               0.33 |             1.77 |
| ('stratified', 'unit', '10')           |    79.58 |     24.9  |      16.66 |          14.03 |            9.32 |               1.31 |             4.07 |
| ('stratified', 'unit', '20')           |   139.09 |     19.5  |      13.14 |          10.82 |            6.94 |               0.91 |             3.07 |
| ('stratified', 'unit', '35')           |   247.25 |     14.12 |       9.74 |           8.27 |            5.56 |               0.58 |             2.26 |
| ('stratified', 'unit', '50')           |   351.19 |     12.2  |       8.59 |           7.56 |            5.11 |               0.49 |             2.05 |
| ('stratified', 'unit', '70')           |   487.27 |     10.16 |       7.41 |           7.19 |            4.75 |               0.35 |             1.79 |
| ('stratified', 'unit', '100')          |   716.64 |      9.59 |       6.77 |           6.83 |            4.63 |               0.32 |             1.63 |

## All boxes per test election

|   test |   boxes |   seat_L1 |   share_L1 |   bloc_seat_L1 |   bloc_share_L1 |   threshold_errors |   max_list_error |
|-------:|--------:|----------:|-----------:|---------------:|----------------:|-------------------:|-----------------:|
|     20 |   10117 |         2 |       1.55 |              2 |            1.29 |                  0 |             0.44 |
|     21 |   10460 |         2 |       1.39 |              0 |            1.07 |                  0 |             0.23 |
|     22 |   10537 |         4 |       1.56 |              2 |            1.27 |                  0 |             0.43 |
|     23 |   10631 |         4 |       1.76 |              4 |            1.48 |                  0 |             0.55 |
|     24 |   12127 |         2 |       1.86 |              2 |            1.74 |                  0 |             0.34 |
|     25 |   11707 |         2 |       2.18 |              2 |            1.97 |                  0 |             0.49 |
|     26 |   12018 |         2 |       2.38 |              2 |            2.05 |                  0 |             0.48 |
