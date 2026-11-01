# Baselines - unit: settlement

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
| ('greedy', 'single_box', '10')         |    10    |     48.75 |      34.89 |          37.6  |           26.56 |               1.81 |             9.28 |
| ('greedy', 'single_box', '20')         |    20    |     38.71 |      27.83 |          30.81 |           21.79 |               1.33 |             7.33 |
| ('greedy', 'single_box', '35')         |    35    |     27.55 |      20.14 |          21.35 |           15.2  |               0.78 |             5.12 |
| ('greedy', 'single_box', '50')         |    50    |     23    |      17.29 |          18.21 |           13.41 |               0.65 |             4.32 |
| ('greedy', 'single_box', '70')         |    70    |     21.4  |      15.97 |          16.88 |           12.67 |               0.61 |             4.01 |
| ('greedy', 'single_box', '100')        |   100    |     17.11 |      13.38 |          13.68 |           10.45 |               0.35 |             3.31 |
| ('greedy', 'unit', '10')               |   660.8  |      8.4  |       6.5  |           6    |            4.67 |               0    |             1.51 |
| ('greedy', 'unit', '20')               |   790.6  |      6.4  |       5.24 |           4.8  |            3.86 |               0    |             1.38 |
| ('greedy', 'unit', '35')               |   912.2  |      6    |       4.91 |           4    |            3.31 |               0    |             1.18 |
| ('greedy', 'unit', '50')               |  1048.6  |      7.6  |       4.54 |           6    |            3.44 |               0.2  |             1.15 |
| ('greedy', 'unit', '70')               |  1329.2  |      6.4  |       4.6  |           5.6  |            3.67 |               0.2  |             1.25 |
| ('greedy', 'unit', '100')              |  1972.4  |      6    |       4.57 |           5.2  |            3.42 |               0.2  |             1.28 |
| ('greedy_budget', 'unit', '10')        |    10.6  |     16.4  |      12.64 |          10.4  |            8.3  |               0.4  |             3.71 |
| ('greedy_budget', 'unit', '20')        |    20.2  |     16    |      10.2  |           8    |            4.92 |               0.8  |             2.1  |
| ('greedy_budget', 'unit', '35')        |    35.8  |     11.6  |       7.49 |           6.4  |            4.27 |               0.6  |             1.49 |
| ('greedy_budget', 'unit', '50')        |    51.4  |     13.2  |      10.26 |           8.8  |            7.33 |               0    |             2.22 |
| ('greedy_budget', 'unit', '70')        |    73.2  |     16    |      11.3  |           7.2  |            5.67 |               0.4  |             2.58 |
| ('greedy_budget', 'unit', '100')       |   105.2  |     12    |       8.93 |           6.8  |            5.93 |               0.4  |             2.26 |
| ('milp_budget', 'unit', '50')          |    51.4  |     10.4  |       8.17 |           6.4  |            5.29 |               0.2  |             2.13 |
| ('milp_budget', 'unit', '70')          |    72    |      9.6  |       7.78 |           6    |            4.88 |               0.2  |             1.82 |
| ('random_pooled', 'single_box', '10')  |    10    |     69    |      49.79 |          55.69 |           39.96 |               3.57 |            11.11 |
| ('random_pooled', 'single_box', '20')  |    19.99 |     60.52 |      42.67 |          49.17 |           34.21 |               3.02 |             9.17 |
| ('random_pooled', 'single_box', '35')  |    34.99 |     56.49 |      39.1  |          45.36 |           30.82 |               2.72 |             8.27 |
| ('random_pooled', 'single_box', '50')  |    49.93 |     54.84 |      37.94 |          41.01 |           27.53 |               2.72 |             7.65 |
| ('random_pooled', 'single_box', '70')  |    69.95 |     53.37 |      36.53 |          39.67 |           26.4  |               2.57 |             6.8  |
| ('random_pooled', 'single_box', '100') |    99.93 |     52.04 |      35.32 |          37.47 |           24.68 |               2.52 |             6.39 |
| ('random_pooled', 'unit', '10')        |    88.27 |     82.01 |      59.84 |          71.49 |           52.33 |               3.73 |            19.49 |
| ('random_pooled', 'unit', '20')        |   238.25 |     66.81 |      47.7  |          58.04 |           41.62 |               2.88 |            14.02 |
| ('random_pooled', 'unit', '35')        |   365.35 |     51.13 |      36.26 |          44.61 |           31.64 |               2.05 |            10.69 |
| ('random_pooled', 'unit', '50')        |   452.1  |     48.29 |      33.91 |          42.44 |           29.71 |               2.03 |             9.72 |
| ('random_pooled', 'unit', '70')        |   656.75 |     42.4  |      29.97 |          38.04 |           26.59 |               1.7  |             8.5  |
| ('random_pooled', 'unit', '100')       |  1014.99 |     39.33 |      28.21 |          35.65 |           25.27 |               1.27 |             7.48 |
| ('random_pps', 'single_box', '10')     |     9.99 |     44.33 |      31.94 |          34.49 |           24.9  |               2.01 |             8.14 |
| ('random_pps', 'single_box', '20')     |    19.99 |     31.83 |      22.83 |          26.32 |           18.57 |               1.35 |             6.05 |
| ('random_pps', 'single_box', '35')     |    34.98 |     24.43 |      17.58 |          20.8  |           14.47 |               0.82 |             4.53 |
| ('random_pps', 'single_box', '50')     |    49.99 |     21.95 |      16.05 |          18.39 |           13.28 |               0.61 |             4.35 |
| ('random_pps', 'single_box', '70')     |    69.97 |     19.45 |      14.58 |          16.72 |           12.25 |               0.47 |             4.02 |
| ('random_pps', 'single_box', '100')    |    99.95 |     20.67 |      15.36 |          18.09 |           13.27 |               0.49 |             4.4  |
| ('random_pps', 'unit', '10')           |  1775.03 |     37.99 |      27.31 |          31.53 |           22.57 |               1.57 |             7.43 |
| ('random_pps', 'unit', '20')           |  3075.8  |     27.49 |      19.33 |          23.88 |           16.5  |               1.11 |             5.54 |
| ('random_pps', 'unit', '35')           |  4655.22 |     21.27 |      15.52 |          18.49 |           13.16 |               0.62 |             4.28 |
| ('random_pps', 'unit', '50')           |  5757.7  |     19.57 |      14.26 |          16.72 |           12.03 |               0.53 |             4    |
| ('random_pps', 'unit', '70')           |  6771.39 |     17.77 |      13.33 |          15.64 |           11.63 |               0.35 |             3.81 |
| ('random_pps', 'unit', '100')          |  7681.04 |     19.88 |      14.88 |          17.69 |           13.12 |               0.39 |             4.28 |
| ('stratified', 'single_box', '10')     |    11.19 |     30.17 |      21.3  |          19.76 |           13.42 |               1.27 |             5.18 |
| ('stratified', 'single_box', '20')     |    19.99 |     23.96 |      17.19 |          16.16 |           11.09 |               0.95 |             4.15 |
| ('stratified', 'single_box', '35')     |    34.99 |     17.41 |      12.76 |          12.03 |            8.44 |               0.55 |             3.04 |
| ('stratified', 'single_box', '50')     |    49.97 |     14.39 |      10.29 |           9.84 |            6.54 |               0.5  |             2.4  |
| ('stratified', 'single_box', '70')     |    69.98 |     12.93 |       9.66 |           9.67 |            6.71 |               0.31 |             2.22 |
| ('stratified', 'single_box', '100')    |    99.97 |     12.21 |       9.15 |           8.61 |            5.97 |               0.27 |             2.01 |
| ('stratified', 'unit', '10')           |  1837.07 |     20.4  |      14.59 |          11.75 |            8.12 |               0.75 |             3.66 |
| ('stratified', 'unit', '20')           |  3188.61 |     14.99 |      11.04 |           9.19 |            6.37 |               0.49 |             2.76 |
| ('stratified', 'unit', '35')           |  4777.11 |     12.05 |       8.77 |           8.17 |            5.57 |               0.33 |             2.19 |
| ('stratified', 'unit', '50')           |  5848.33 |     11.05 |       7.95 |           7.55 |            5.03 |               0.33 |             1.94 |
| ('stratified', 'unit', '70')           |  6730.13 |     10.56 |       7.85 |           7.44 |            5.03 |               0.23 |             1.8  |
| ('stratified', 'unit', '100')          |  7713.74 |     10.92 |       8.09 |           7.55 |            5.04 |               0.26 |             1.75 |

## Mean over all test elections (17-26)

|                                        |    boxes |   seat_L1 |   share_L1 |   bloc_seat_L1 |   bloc_share_L1 |   threshold_errors |   max_list_error |
|:---------------------------------------|---------:|----------:|-----------:|---------------:|----------------:|-------------------:|-----------------:|
| ('all_boxes', 'unit', 'all')           | 10501.3  |      2.6  |       1.72 |           2    |            1.45 |               0    |             0.37 |
| ('greedy', 'single_box', '10')         |    10    |     48.93 |      35.17 |          38.19 |           26.59 |               2.07 |             9.21 |
| ('greedy', 'single_box', '20')         |    19.6  |     38.32 |      27.74 |          30.09 |           21.01 |               1.52 |             7.01 |
| ('greedy', 'single_box', '35')         |    32.6  |     30.11 |      21.79 |          22.89 |           15.94 |               1.14 |             5.39 |
| ('greedy', 'single_box', '50')         |    43.9  |     26.37 |      19.22 |          19.77 |           13.89 |               1.05 |             4.65 |
| ('greedy', 'single_box', '70')         |    57.1  |     25.41 |      18.29 |          18.95 |           13.29 |               1.05 |             4.48 |
| ('greedy', 'single_box', '100')        |    73    |     23.73 |      17.17 |          17.57 |           12.29 |               0.94 |             4.05 |
| ('greedy', 'unit', '10')               |   436.6  |      9.8  |       7.02 |           6.8  |            4.33 |               0.4  |             1.53 |
| ('greedy', 'unit', '20')               |   521.5  |      7    |       6.08 |           5.2  |            3.74 |               0.2  |             1.42 |
| ('greedy', 'unit', '35')               |   601.5  |      7    |       5.74 |           4.2  |            3.1  |               0.2  |             1.19 |
| ('greedy', 'unit', '50')               |   687.3  |      7.6  |       5.57 |           5.2  |            3.13 |               0.3  |             1.24 |
| ('greedy', 'unit', '70')               |   846    |      8    |       5.54 |           5.6  |            3.26 |               0.5  |             1.31 |
| ('greedy', 'unit', '100')              |  1178.4  |      8    |       5.48 |           5.6  |            3.14 |               0.5  |             1.28 |
| ('greedy_budget', 'unit', '10')        |    10.9  |     21    |      14.95 |          13.4  |            9.06 |               1.2  |             3.71 |
| ('greedy_budget', 'unit', '20')        |    20.9  |     21    |      14.15 |          12.2  |            7.88 |               1.4  |             2.92 |
| ('greedy_budget', 'unit', '35')        |    36.9  |     13.6  |       8.99 |           7.8  |            4.9  |               0.9  |             1.85 |
| ('greedy_budget', 'unit', '50')        |    52.4  |     17.2  |      12    |          12    |            8.53 |               0.9  |             2.6  |
| ('greedy_budget', 'unit', '70')        |    71    |     15.8  |      10.91 |           8.8  |            5.95 |               0.7  |             2.3  |
| ('greedy_budget', 'unit', '100')       |    94.3  |     12.8  |       9.97 |           7.6  |            6.06 |               0.6  |             2.28 |
| ('milp_budget', 'unit', '50')          |    49.9  |     13.6  |       9.93 |           8    |            5.36 |               0.6  |             2.1  |
| ('milp_budget', 'unit', '70')          |    67.1  |     11.4  |       8.87 |           7.4  |            5.42 |               0.4  |             1.86 |
| ('random_pooled', 'single_box', '10')  |     9.98 |     69.58 |      50.41 |          54.25 |           38.67 |               3.82 |            11.62 |
| ('random_pooled', 'single_box', '20')  |    19.91 |     60.99 |      43.48 |          48.94 |           34.02 |               3.21 |             9.8  |
| ('random_pooled', 'single_box', '35')  |    34.87 |     56.15 |      39.11 |          44.05 |           29.63 |               2.86 |             8.56 |
| ('random_pooled', 'single_box', '50')  |    49.77 |     54.5  |      37.54 |          41.07 |           27.04 |               2.93 |             7.93 |
| ('random_pooled', 'single_box', '70')  |    69.67 |     53.67 |      36.58 |          39.7  |           25.84 |               2.77 |             7.38 |
| ('random_pooled', 'single_box', '100') |    99.53 |     53.1  |      35.99 |          38.98 |           25.27 |               2.7  |             7.1  |
| ('random_pooled', 'unit', '10')        |    78.09 |     81.27 |      59.43 |          68.89 |           50.22 |               3.95 |            17.48 |
| ('random_pooled', 'unit', '20')        |   200.16 |     66.95 |      47.98 |          58.71 |           42.08 |               3.13 |            13.71 |
| ('random_pooled', 'unit', '35')        |   326.27 |     53.07 |      37.67 |          46.53 |           32.93 |               2.32 |            10.47 |
| ('random_pooled', 'unit', '50')        |   437.39 |     46.76 |      32.28 |          41.11 |           28.16 |               2.4  |             8.91 |
| ('random_pooled', 'unit', '70')        |   614.53 |     41.52 |      28.71 |          36.95 |           25.31 |               1.99 |             7.7  |
| ('random_pooled', 'unit', '100')       |   921.65 |     36.95 |      25.74 |          33.39 |           22.97 |               1.57 |             6.67 |
| ('random_pps', 'single_box', '10')     |     9.99 |     43.91 |      31.4  |          34.25 |           24.44 |               2.39 |             7.89 |
| ('random_pps', 'single_box', '20')     |    19.97 |     31.93 |      22.6  |          25.89 |           18    |               1.62 |             5.57 |
| ('random_pps', 'single_box', '35')     |    34.95 |     24.25 |      17.05 |          19.69 |           13.43 |               1.04 |             4.17 |
| ('random_pps', 'single_box', '50')     |    49.91 |     22.21 |      16.17 |          18.3  |           13.06 |               0.72 |             4.06 |
| ('random_pps', 'single_box', '70')     |    69.87 |     20.67 |      15.27 |          17.38 |           12.59 |               0.58 |             3.78 |
| ('random_pps', 'single_box', '100')    |    99.75 |     22.65 |      16.62 |          18.97 |           13.73 |               0.58 |             4.24 |
| ('random_pps', 'unit', '10')           |  1712.94 |     37    |      26.1  |          30.49 |           21.4  |               1.91 |             6.83 |
| ('random_pps', 'unit', '20')           |  3037    |     27.33 |      18.87 |          23.23 |           15.8  |               1.32 |             4.93 |
| ('random_pps', 'unit', '35')           |  4495.64 |     21.13 |      14.83 |          17.69 |           12.26 |               0.82 |             3.82 |
| ('random_pps', 'unit', '50')           |  5440.9  |     19.93 |      14.38 |          17.01 |           12.03 |               0.65 |             3.7  |
| ('random_pps', 'unit', '70')           |  6367.68 |     18.79 |      13.99 |          16.31 |           12.09 |               0.4  |             3.58 |
| ('random_pps', 'unit', '100')          |  7189.17 |     21.44 |      15.93 |          18.38 |           13.5  |               0.47 |             4.07 |
| ('stratified', 'single_box', '10')     |    12.16 |     31.09 |      21.87 |          20.65 |           13.94 |               1.6  |             5.14 |
| ('stratified', 'single_box', '20')     |    20.47 |     24.77 |      17.42 |          16.01 |           10.97 |               1.27 |             4.03 |
| ('stratified', 'single_box', '35')     |    35.15 |     19.02 |      13.14 |          12.33 |            8.31 |               0.91 |             2.96 |
| ('stratified', 'single_box', '50')     |    50.03 |     15.45 |      10.63 |           9.98 |            6.59 |               0.68 |             2.41 |
| ('stratified', 'single_box', '70')     |    69.96 |     13.54 |       9.54 |           9.33 |            6.17 |               0.51 |             2.1  |
| ('stratified', 'single_box', '100')    |    99.82 |     12.93 |       9.01 |           8.33 |            5.5  |               0.43 |             1.94 |
| ('stratified', 'unit', '10')           |  1743.9  |     20.17 |      13.98 |          11.49 |            7.93 |               1.01 |             3.3  |
| ('stratified', 'unit', '20')           |  3067.8  |     16.35 |      11.21 |           9.09 |            6.14 |               0.83 |             2.6  |
| ('stratified', 'unit', '35')           |  4581.44 |     12.88 |       8.64 |           7.55 |            5    |               0.56 |             1.99 |
| ('stratified', 'unit', '50')           |  5567.87 |     11.31 |       7.7  |           7    |            4.54 |               0.46 |             1.75 |
| ('stratified', 'unit', '70')           |  6401.83 |     10.75 |       7.49 |           6.71 |            4.43 |               0.36 |             1.62 |
| ('stratified', 'unit', '100')          |  7268.11 |     10.85 |       7.57 |           6.72 |            4.34 |               0.34 |             1.59 |

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
