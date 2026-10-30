# Baselines - unit: base_box

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
| ('greedy', 'single_box', '10')         |     9    |     21.44 |      14.94 |          15.83 |            9.22 |               1.27 |             3.06 |
| ('greedy', 'single_box', '20')         |    18.2  |     18.6  |      12.87 |          13.52 |            8.76 |               1.22 |             2.57 |
| ('greedy', 'single_box', '35')         |    31    |     15.47 |       9.82 |          10.21 |            6.05 |               0.82 |             1.86 |
| ('greedy', 'single_box', '50')         |    43.8  |     14.16 |       8.54 |          10.48 |            5.95 |               0.89 |             1.78 |
| ('greedy', 'single_box', '70')         |    60    |     13.03 |       7.7  |          10.19 |            5.74 |               0.76 |             1.57 |
| ('greedy', 'single_box', '100')        |    83.6  |     14.29 |       7.91 |          10.32 |            5.49 |               0.93 |             1.64 |
| ('greedy', 'unit', '10')               |    15.8  |     20.4  |      14.51 |          15.6  |            8.83 |               1.2  |             2.98 |
| ('greedy', 'unit', '20')               |    28.4  |     17.6  |      12.8  |          13.2  |            8.62 |               1.2  |             2.47 |
| ('greedy', 'unit', '35')               |    45.4  |     16    |       9.54 |          11.2  |            5.9  |               1    |             1.69 |
| ('greedy', 'unit', '50')               |    61.2  |     13.2  |       8.17 |           9.6  |            5.89 |               0.8  |             1.73 |
| ('greedy', 'unit', '70')               |    79.6  |     13.6  |       7.55 |          11.2  |            5.65 |               0.8  |             1.53 |
| ('greedy', 'unit', '100')              |   112.2  |     15.6  |       7.87 |          11.6  |            5.42 |               1    |             1.59 |
| ('greedy_budget', 'unit', '10')        |    12.4  |     21.6  |      16.05 |          16    |           12.01 |               0.8  |             3.35 |
| ('greedy_budget', 'unit', '20')        |    21.6  |     18    |      13.8  |          14.8  |           10.94 |               0.2  |             3.49 |
| ('greedy_budget', 'unit', '35')        |    34.6  |     13.6  |      10.51 |          11.6  |            8.03 |               0.4  |             2.55 |
| ('greedy_budget', 'unit', '50')        |    48.8  |     10.4  |       8.52 |           8.4  |            6.5  |               0.2  |             2.05 |
| ('greedy_budget', 'unit', '70')        |    68    |      8.4  |       6.63 |           6    |            4.63 |               0    |             1.67 |
| ('greedy_budget', 'unit', '100')       |    93.8  |      8    |       6.62 |           6    |            4.1  |               0.2  |             1.33 |
| ('milp_budget', 'unit', '50')          |    47.6  |      8    |       7.31 |           5.6  |            4.77 |               0    |             1.68 |
| ('milp_budget', 'unit', '70')          |    70    |      8.4  |       6.08 |           6    |            3.9  |               0.2  |             1.53 |
| ('random_pooled', 'single_box', '10')  |     8.39 |     50.41 |      36.6  |          40.93 |           30.03 |               2.46 |            10.23 |
| ('random_pooled', 'single_box', '20')  |    16.85 |     37.85 |      27.62 |          31.75 |           22.67 |               1.62 |             7.24 |
| ('random_pooled', 'single_box', '35')  |    29.53 |     28.37 |      20.34 |          23.65 |           16.37 |               1.19 |             5.35 |
| ('random_pooled', 'single_box', '50')  |    42.15 |     24.87 |      17.59 |          20.96 |           14.41 |               1.07 |             4.6  |
| ('random_pooled', 'single_box', '70')  |    58.61 |     20.87 |      14.59 |          17.53 |           11.76 |               0.85 |             3.75 |
| ('random_pooled', 'single_box', '100') |    84.36 |     18.05 |      12.45 |          15    |            9.89 |               0.71 |             3.34 |
| ('random_pooled', 'unit', '10')        |    12.75 |     54.48 |      39.45 |          45.35 |           32.91 |               2.59 |            11.14 |
| ('random_pooled', 'unit', '20')        |    24.03 |     40.97 |      29.78 |          34.53 |           24.8  |               1.7  |             7.89 |
| ('random_pooled', 'unit', '35')        |    43.23 |     31.27 |      22.34 |          26.11 |           18.34 |               1.25 |             5.89 |
| ('random_pooled', 'unit', '50')        |    61.65 |     28.84 |      19.83 |          25.24 |           17.03 |               1.27 |             5.27 |
| ('random_pooled', 'unit', '70')        |    84.91 |     23.23 |      16.43 |          19.77 |           13.82 |               0.84 |             4.37 |
| ('random_pooled', 'unit', '100')       |   121.95 |     20.09 |      13.81 |          17.29 |           11.49 |               0.74 |             3.5  |
| ('random_pps', 'single_box', '10')     |     8.13 |     49.55 |      36.34 |          40.75 |           30.13 |               2.34 |             9.53 |
| ('random_pps', 'single_box', '20')     |    15.94 |     35.07 |      25.77 |          29.01 |           21.28 |               1.57 |             6.76 |
| ('random_pps', 'single_box', '35')     |    28.51 |     28.68 |      20.29 |          23.92 |           16.44 |               1.18 |             5.19 |
| ('random_pps', 'single_box', '50')     |    40.61 |     24.97 |      17.65 |          20.89 |           14.35 |               0.98 |             4.47 |
| ('random_pps', 'single_box', '70')     |    57.24 |     20.71 |      14.33 |          17.04 |           11.35 |               0.85 |             3.62 |
| ('random_pps', 'single_box', '100')    |    81.49 |     16.65 |      11.68 |          13.56 |            9.11 |               0.64 |             3.04 |
| ('random_pps', 'unit', '10')           |    15.85 |     49.37 |      36.11 |          40.95 |           30.18 |               2.28 |             9.52 |
| ('random_pps', 'unit', '20')           |    31.89 |     34.57 |      25.55 |          28.88 |           21.21 |               1.49 |             6.74 |
| ('random_pps', 'unit', '35')           |    55.6  |     28.52 |      20.14 |          24.01 |           16.43 |               1.19 |             5.16 |
| ('random_pps', 'unit', '50')           |    79.37 |     24.87 |      17.61 |          20.71 |           14.38 |               0.97 |             4.46 |
| ('random_pps', 'unit', '70')           |   114.37 |     20.64 |      14.26 |          16.88 |           11.32 |               0.85 |             3.6  |
| ('random_pps', 'unit', '100')          |   161.92 |     16.28 |      11.51 |          13.49 |            9.05 |               0.6  |             2.99 |
| ('stratified', 'single_box', '10')     |     9.51 |     36.58 |      26.5  |          21.98 |           16.02 |               1.73 |             6.29 |
| ('stratified', 'single_box', '20')     |    16.57 |     28.45 |      20.23 |          17.63 |           12.49 |               1.37 |             4.57 |
| ('stratified', 'single_box', '35')     |    29    |     19.21 |      13.38 |          12.33 |            8.17 |               0.92 |             3.12 |
| ('stratified', 'single_box', '50')     |    41.44 |     16.33 |      11.52 |          10.43 |            6.92 |               0.67 |             2.66 |
| ('stratified', 'single_box', '70')     |    56.81 |     14.17 |      10.09 |          10.12 |            6.54 |               0.57 |             2.37 |
| ('stratified', 'single_box', '100')    |    81.75 |     12.29 |       8.48 |           8.31 |            5.31 |               0.49 |             1.95 |
| ('stratified', 'unit', '10')           |    17.99 |     35.86 |      25.94 |          21.48 |           15.83 |               1.71 |             6.19 |
| ('stratified', 'unit', '20')           |    32.1  |     27.77 |      19.86 |          17.61 |           12.37 |               1.29 |             4.51 |
| ('stratified', 'unit', '35')           |    56.81 |     18.79 |      13.15 |          12.47 |            8.21 |               0.84 |             3.07 |
| ('stratified', 'unit', '50')           |    82.67 |     16.2  |      11.36 |          10.2  |            6.87 |               0.67 |             2.6  |
| ('stratified', 'unit', '70')           |   111.73 |     14.2  |       9.94 |          10.17 |            6.46 |               0.59 |             2.32 |
| ('stratified', 'unit', '100')          |   161.87 |     12.05 |       8.29 |           8.17 |            5.23 |               0.46 |             1.94 |

## Mean over all test elections (17-26)

|                                        |    boxes |   seat_L1 |   share_L1 |   bloc_seat_L1 |   bloc_share_L1 |   threshold_errors |   max_list_error |
|:---------------------------------------|---------:|----------:|-----------:|---------------:|----------------:|-------------------:|-----------------:|
| ('all_boxes', 'unit', 'all')           | 10501.3  |      2.6  |       1.72 |           2    |            1.45 |               0    |             0.37 |
| ('greedy', 'single_box', '10')         |     9.5  |     20.32 |      14.75 |          13.31 |            8.09 |               1.24 |             2.99 |
| ('greedy', 'single_box', '20')         |    18.8  |     16.7  |      12.01 |          10.96 |            6.87 |               1.21 |             2.32 |
| ('greedy', 'single_box', '35')         |    30.3  |     16.13 |      10.47 |           9.71 |            5.54 |               1.11 |             2.04 |
| ('greedy', 'single_box', '50')         |    40.2  |     15.28 |       9.63 |          10.24 |            5.54 |               1.04 |             1.99 |
| ('greedy', 'single_box', '70')         |    51.2  |     14.83 |       9.31 |          10.09 |            5.51 |               0.98 |             1.86 |
| ('greedy', 'single_box', '100')        |    63.2  |     15.39 |       9.41 |          10.16 |            5.4  |               1.07 |             1.9  |
| ('greedy', 'unit', '10')               |    12.9  |     19.8  |      14.53 |          13.2  |            7.9  |               1.2  |             2.95 |
| ('greedy', 'unit', '20')               |    24    |     16.2  |      11.97 |          10.8  |            6.8  |               1.2  |             2.27 |
| ('greedy', 'unit', '35')               |    37.6  |     16.4  |      10.32 |          10.2  |            5.46 |               1.2  |             1.96 |
| ('greedy', 'unit', '50')               |    49    |     14.8  |       9.45 |           9.8  |            5.51 |               1    |             1.96 |
| ('greedy', 'unit', '70')               |    61.4  |     15    |       9.22 |          10.6  |            5.46 |               1    |             1.84 |
| ('greedy', 'unit', '100')              |    77.9  |     16    |       9.39 |          10.8  |            5.36 |               1.1  |             1.87 |
| ('greedy_budget', 'unit', '10')        |    11.1  |     19.8  |      15.1  |          13.6  |            9.45 |               1    |             3.19 |
| ('greedy_budget', 'unit', '20')        |    20.4  |     16    |      12.24 |          11.8  |            8.17 |               0.5  |             2.96 |
| ('greedy_budget', 'unit', '35')        |    32.2  |     13.4  |      10.13 |          10    |            6.45 |               0.6  |             2.25 |
| ('greedy_budget', 'unit', '50')        |    43.3  |     11.2  |       8.84 |           7.8  |            5.37 |               0.3  |             1.96 |
| ('greedy_budget', 'unit', '70')        |    55.7  |     10.2  |       8.07 |           6.6  |            4.38 |               0.2  |             1.78 |
| ('greedy_budget', 'unit', '100')       |    68.7  |     10.4  |       8.09 |           6.8  |            4.11 |               0.4  |             1.61 |
| ('milp_budget', 'unit', '50')          |    42.2  |     10    |       8.31 |           6.6  |            4.56 |               0.3  |             1.77 |
| ('milp_budget', 'unit', '70')          |    56.7  |     10.8  |       7.97 |           6.8  |            4.32 |               0.4  |             1.78 |
| ('random_pooled', 'single_box', '10')  |     9.05 |     48.34 |      34.96 |          38.99 |           28.31 |               2.66 |             9.32 |
| ('random_pooled', 'single_box', '20')  |    18.12 |     35.97 |      25.38 |          29.49 |           20.55 |               2    |             6.24 |
| ('random_pooled', 'single_box', '35')  |    31.75 |     27.71 |      19.3  |          22.92 |           15.53 |               1.48 |             4.84 |
| ('random_pooled', 'single_box', '50')  |    45.31 |     24.39 |      16.59 |          20.29 |           13.48 |               1.31 |             4.07 |
| ('random_pooled', 'single_box', '70')  |    63.3  |     20.17 |      13.73 |          16.65 |           10.97 |               1.02 |             3.35 |
| ('random_pooled', 'single_box', '100') |    90.62 |     17.3  |      11.66 |          14.17 |            9.23 |               0.82 |             2.95 |
| ('random_pooled', 'unit', '10')        |    11.4  |     50.41 |      36.44 |          41.38 |           29.89 |               2.73 |             9.83 |
| ('random_pooled', 'unit', '20')        |    22.02 |     37.68 |      26.62 |          31.14 |           21.79 |               2.04 |             6.6  |
| ('random_pooled', 'unit', '35')        |    39.1  |     29.39 |      20.49 |          24.33 |           16.65 |               1.53 |             5.18 |
| ('random_pooled', 'unit', '50')        |    55.75 |     26.46 |      17.71 |          22.47 |           14.79 |               1.41 |             4.41 |
| ('random_pooled', 'unit', '70')        |    77.39 |     21.64 |      14.71 |          17.97 |           12.08 |               1.05 |             3.7  |
| ('random_pooled', 'unit', '100')       |   110.63 |     18.59 |      12.44 |          15.56 |           10.12 |               0.87 |             3.08 |
| ('random_pps', 'single_box', '10')     |     8.89 |     46.52 |      33.75 |          37.16 |           26.98 |               2.68 |             8.42 |
| ('random_pps', 'single_box', '20')     |    17.68 |     33.03 |      23.63 |          26.67 |           18.88 |               1.84 |             5.85 |
| ('random_pps', 'single_box', '35')     |    31.26 |     27.79 |      19.37 |          22.77 |           15.4  |               1.4  |             4.74 |
| ('random_pps', 'single_box', '50')     |    44.55 |     23.35 |      16.3  |          18.85 |           12.9  |               1.1  |             4    |
| ('random_pps', 'single_box', '70')     |    62.57 |     19.66 |      13.38 |          16    |           10.58 |               0.95 |             3.25 |
| ('random_pps', 'single_box', '100')    |    89.33 |     16.52 |      11.39 |          13.23 |            8.96 |               0.76 |             2.79 |
| ('random_pps', 'unit', '10')           |    12.86 |     46.47 |      33.64 |          37.25 |           27.01 |               2.66 |             8.42 |
| ('random_pps', 'unit', '20')           |    25.89 |     32.81 |      23.51 |          26.63 |           18.84 |               1.81 |             5.85 |
| ('random_pps', 'unit', '35')           |    45.19 |     27.73 |      19.28 |          22.81 |           15.39 |               1.4  |             4.72 |
| ('random_pps', 'unit', '50')           |    64.52 |     23.27 |      16.28 |          18.75 |           12.92 |               1.1  |             3.99 |
| ('random_pps', 'unit', '70')           |    91.85 |     19.63 |      13.34 |          15.92 |           10.56 |               0.95 |             3.24 |
| ('random_pps', 'unit', '100')          |   130.74 |     16.38 |      11.31 |          13.22 |            8.93 |               0.74 |             2.77 |
| ('stratified', 'single_box', '10')     |    10.76 |     33.37 |      23.9  |          19.41 |           13.73 |               1.78 |             5.56 |
| ('stratified', 'single_box', '20')     |    18.38 |     25.35 |      17.76 |          14.81 |           10.12 |               1.39 |             3.89 |
| ('stratified', 'single_box', '35')     |    31.52 |     18.15 |      12.4  |          10.8  |            7.12 |               0.98 |             2.81 |
| ('stratified', 'single_box', '50')     |    44.95 |     15.4  |      10.68 |           9.19 |            6.04 |               0.76 |             2.38 |
| ('stratified', 'single_box', '70')     |    62.38 |     13.04 |       9.22 |           8.32 |            5.51 |               0.58 |             2.07 |
| ('stratified', 'single_box', '100')    |    89.5  |     11.53 |       7.89 |           7.31 |            4.65 |               0.51 |             1.74 |
| ('stratified', 'unit', '10')           |    15.17 |     33.07 |      23.63 |          19.19 |           13.64 |               1.77 |             5.51 |
| ('stratified', 'unit', '20')           |    26.43 |     25    |      17.57 |          14.83 |           10.06 |               1.35 |             3.86 |
| ('stratified', 'unit', '35')           |    45.79 |     17.91 |      12.27 |          10.85 |            7.13 |               0.94 |             2.79 |
| ('stratified', 'unit', '50')           |    66.03 |     15.29 |      10.59 |           9.05 |            6    |               0.76 |             2.35 |
| ('stratified', 'unit', '70')           |    90.75 |     13.03 |       9.15 |           8.33 |            5.47 |               0.59 |             2.05 |
| ('stratified', 'unit', '100')          |   130.7  |     11.45 |       7.8  |           7.23 |            4.61 |               0.51 |             1.73 |

## All boxes per test election

|   test |   boxes |   seat_L1 |   share_L1 |   bloc_seat_L1 |   bloc_share_L1 |   threshold_errors |   max_list_error |
|-------:|--------:|----------:|-----------:|---------------:|----------------:|-------------------:|-----------------:|
|     17 |    8275 |         4 |       1.68 |              2 |            1.28 |                  0 |             0.23 |
|     18 |    9263 |         2 |       1.28 |              2 |            1.09 |                  0 |             0.21 |
|     19 |    9878 |         2 |       1.55 |              2 |            1.28 |                  0 |             0.36 |
|     20 |   10117 |         2 |       1.55 |              2 |            1.29 |                  0 |             0.44 |
|     21 |   10460 |         2 |       1.39 |              0 |            1.07 |                  0 |             0.23 |
|     22 |   10537 |         4 |       1.56 |              2 |            1.27 |                  0 |             0.43 |
|     23 |   10631 |         4 |       1.76 |              4 |            1.48 |                  0 |             0.55 |
|     24 |   12127 |         2 |       1.86 |              2 |            1.74 |                  0 |             0.34 |
|     25 |   11707 |         2 |       2.18 |              2 |            1.97 |                  0 |             0.49 |
|     26 |   12018 |         2 |       2.38 |              2 |            2.05 |                  0 |             0.48 |
