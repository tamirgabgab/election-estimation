# Baselines - unit: base_box

Held-out evaluation: for every test election t, panels are chosen on the elections
before t only. Errors: `seat_L1` and `bloc_seat_L1` in seats, the others in
percentage points of valid votes; `threshold_errors` counts lists whose
pass / fail is predicted wrongly.

Settings: seed 0, 30 draws for random panels and single-box readings,
greedy recency decay 0.7, 40 candidates per step, panel sizes [10, 20, 35, 50, 70, 100].
`unit` reading counts whole panel units; `single_box` counts one random box per unit.

Methods: `all_boxes` pools every regular box (no sampling; its error is the
double-envelope gap); `random_pooled` draws units uniformly and pools their votes;
`random_pps` draws units in proportion to size and averages their shares;
`greedy` is column generation with LP weights on the stacked training elections.

## Mean over recent test elections (22-26)

|                                        |   seat_L1 |   share_L1 |   bloc_seat_L1 |   bloc_share_L1 |   threshold_errors |   max_list_error |
|:---------------------------------------|----------:|-----------:|---------------:|----------------:|-------------------:|-----------------:|
| ('all_boxes', 'unit', 'all')           |      2.8  |       1.95 |           2.4  |            1.7  |               0    |             0.46 |
| ('greedy', 'single_box', '10')         |     21.44 |      14.94 |          15.83 |            9.22 |               1.27 |             3.06 |
| ('greedy', 'single_box', '20')         |     18.6  |      12.87 |          13.52 |            8.76 |               1.22 |             2.57 |
| ('greedy', 'single_box', '35')         |     15.47 |       9.82 |          10.21 |            6.05 |               0.82 |             1.86 |
| ('greedy', 'single_box', '50')         |     14.16 |       8.54 |          10.48 |            5.95 |               0.89 |             1.78 |
| ('greedy', 'single_box', '70')         |     13.03 |       7.7  |          10.19 |            5.74 |               0.76 |             1.57 |
| ('greedy', 'single_box', '100')        |     14.29 |       7.91 |          10.32 |            5.49 |               0.93 |             1.64 |
| ('greedy', 'unit', '10')               |     20.4  |      14.51 |          15.6  |            8.83 |               1.2  |             2.98 |
| ('greedy', 'unit', '20')               |     17.6  |      12.8  |          13.2  |            8.62 |               1.2  |             2.47 |
| ('greedy', 'unit', '35')               |     16    |       9.54 |          11.2  |            5.9  |               1    |             1.69 |
| ('greedy', 'unit', '50')               |     13.2  |       8.17 |           9.6  |            5.89 |               0.8  |             1.73 |
| ('greedy', 'unit', '70')               |     13.6  |       7.55 |          11.2  |            5.65 |               0.8  |             1.53 |
| ('greedy', 'unit', '100')              |     15.6  |       7.87 |          11.6  |            5.42 |               1    |             1.59 |
| ('random_pooled', 'single_box', '10')  |     50.41 |      36.6  |          40.93 |           30.03 |               2.46 |            10.23 |
| ('random_pooled', 'single_box', '20')  |     37.85 |      27.62 |          31.75 |           22.67 |               1.62 |             7.24 |
| ('random_pooled', 'single_box', '35')  |     28.37 |      20.34 |          23.65 |           16.37 |               1.19 |             5.35 |
| ('random_pooled', 'single_box', '50')  |     24.87 |      17.59 |          20.96 |           14.41 |               1.07 |             4.6  |
| ('random_pooled', 'single_box', '70')  |     20.87 |      14.59 |          17.53 |           11.76 |               0.85 |             3.75 |
| ('random_pooled', 'single_box', '100') |     18.05 |      12.45 |          15    |            9.89 |               0.71 |             3.34 |
| ('random_pooled', 'unit', '10')        |     54.48 |      39.45 |          45.35 |           32.91 |               2.59 |            11.14 |
| ('random_pooled', 'unit', '20')        |     40.97 |      29.78 |          34.53 |           24.8  |               1.7  |             7.89 |
| ('random_pooled', 'unit', '35')        |     31.27 |      22.34 |          26.11 |           18.34 |               1.25 |             5.89 |
| ('random_pooled', 'unit', '50')        |     28.84 |      19.83 |          25.24 |           17.03 |               1.27 |             5.27 |
| ('random_pooled', 'unit', '70')        |     23.23 |      16.43 |          19.77 |           13.82 |               0.84 |             4.37 |
| ('random_pooled', 'unit', '100')       |     20.09 |      13.81 |          17.29 |           11.49 |               0.74 |             3.5  |
| ('random_pps', 'single_box', '10')     |     49.55 |      36.34 |          40.75 |           30.13 |               2.34 |             9.53 |
| ('random_pps', 'single_box', '20')     |     35.07 |      25.77 |          29.01 |           21.28 |               1.57 |             6.76 |
| ('random_pps', 'single_box', '35')     |     28.68 |      20.29 |          23.92 |           16.44 |               1.18 |             5.19 |
| ('random_pps', 'single_box', '50')     |     24.97 |      17.65 |          20.89 |           14.35 |               0.98 |             4.47 |
| ('random_pps', 'single_box', '70')     |     20.71 |      14.33 |          17.04 |           11.35 |               0.85 |             3.62 |
| ('random_pps', 'single_box', '100')    |     16.65 |      11.68 |          13.56 |            9.11 |               0.64 |             3.04 |
| ('random_pps', 'unit', '10')           |     49.37 |      36.11 |          40.95 |           30.18 |               2.28 |             9.52 |
| ('random_pps', 'unit', '20')           |     34.57 |      25.55 |          28.88 |           21.21 |               1.49 |             6.74 |
| ('random_pps', 'unit', '35')           |     28.52 |      20.14 |          24.01 |           16.43 |               1.19 |             5.16 |
| ('random_pps', 'unit', '50')           |     24.87 |      17.61 |          20.71 |           14.38 |               0.97 |             4.46 |
| ('random_pps', 'unit', '70')           |     20.64 |      14.26 |          16.88 |           11.32 |               0.85 |             3.6  |
| ('random_pps', 'unit', '100')          |     16.28 |      11.51 |          13.49 |            9.05 |               0.6  |             2.99 |

## Mean over all test elections (17-26)

|                                        |   seat_L1 |   share_L1 |   bloc_seat_L1 |   bloc_share_L1 |   threshold_errors |   max_list_error |
|:---------------------------------------|----------:|-----------:|---------------:|----------------:|-------------------:|-----------------:|
| ('all_boxes', 'unit', 'all')           |      2.6  |       1.72 |           2    |            1.45 |               0    |             0.37 |
| ('greedy', 'single_box', '10')         |     20.32 |      14.75 |          13.31 |            8.09 |               1.24 |             2.99 |
| ('greedy', 'single_box', '20')         |     16.7  |      12.01 |          10.96 |            6.87 |               1.21 |             2.32 |
| ('greedy', 'single_box', '35')         |     16.13 |      10.47 |           9.71 |            5.54 |               1.11 |             2.04 |
| ('greedy', 'single_box', '50')         |     15.28 |       9.63 |          10.24 |            5.54 |               1.04 |             1.99 |
| ('greedy', 'single_box', '70')         |     14.83 |       9.31 |          10.09 |            5.51 |               0.98 |             1.86 |
| ('greedy', 'single_box', '100')        |     15.39 |       9.41 |          10.16 |            5.4  |               1.07 |             1.9  |
| ('greedy', 'unit', '10')               |     19.8  |      14.53 |          13.2  |            7.9  |               1.2  |             2.95 |
| ('greedy', 'unit', '20')               |     16.2  |      11.97 |          10.8  |            6.8  |               1.2  |             2.27 |
| ('greedy', 'unit', '35')               |     16.4  |      10.32 |          10.2  |            5.46 |               1.2  |             1.96 |
| ('greedy', 'unit', '50')               |     14.8  |       9.45 |           9.8  |            5.51 |               1    |             1.96 |
| ('greedy', 'unit', '70')               |     15    |       9.22 |          10.6  |            5.46 |               1    |             1.84 |
| ('greedy', 'unit', '100')              |     16    |       9.39 |          10.8  |            5.36 |               1.1  |             1.87 |
| ('random_pooled', 'single_box', '10')  |     48.34 |      34.96 |          38.99 |           28.31 |               2.66 |             9.32 |
| ('random_pooled', 'single_box', '20')  |     35.97 |      25.38 |          29.49 |           20.55 |               2    |             6.24 |
| ('random_pooled', 'single_box', '35')  |     27.71 |      19.3  |          22.92 |           15.53 |               1.48 |             4.84 |
| ('random_pooled', 'single_box', '50')  |     24.39 |      16.59 |          20.29 |           13.48 |               1.31 |             4.07 |
| ('random_pooled', 'single_box', '70')  |     20.17 |      13.73 |          16.65 |           10.97 |               1.02 |             3.35 |
| ('random_pooled', 'single_box', '100') |     17.3  |      11.66 |          14.17 |            9.23 |               0.82 |             2.95 |
| ('random_pooled', 'unit', '10')        |     50.41 |      36.44 |          41.38 |           29.89 |               2.73 |             9.83 |
| ('random_pooled', 'unit', '20')        |     37.68 |      26.62 |          31.14 |           21.79 |               2.04 |             6.6  |
| ('random_pooled', 'unit', '35')        |     29.39 |      20.49 |          24.33 |           16.65 |               1.53 |             5.18 |
| ('random_pooled', 'unit', '50')        |     26.46 |      17.71 |          22.47 |           14.79 |               1.41 |             4.41 |
| ('random_pooled', 'unit', '70')        |     21.64 |      14.71 |          17.97 |           12.08 |               1.05 |             3.7  |
| ('random_pooled', 'unit', '100')       |     18.59 |      12.44 |          15.56 |           10.12 |               0.87 |             3.08 |
| ('random_pps', 'single_box', '10')     |     46.52 |      33.75 |          37.16 |           26.98 |               2.68 |             8.42 |
| ('random_pps', 'single_box', '20')     |     33.03 |      23.63 |          26.67 |           18.88 |               1.84 |             5.85 |
| ('random_pps', 'single_box', '35')     |     27.79 |      19.37 |          22.77 |           15.4  |               1.4  |             4.74 |
| ('random_pps', 'single_box', '50')     |     23.35 |      16.3  |          18.85 |           12.9  |               1.1  |             4    |
| ('random_pps', 'single_box', '70')     |     19.66 |      13.38 |          16    |           10.58 |               0.95 |             3.25 |
| ('random_pps', 'single_box', '100')    |     16.52 |      11.39 |          13.23 |            8.96 |               0.76 |             2.79 |
| ('random_pps', 'unit', '10')           |     46.47 |      33.64 |          37.25 |           27.01 |               2.66 |             8.42 |
| ('random_pps', 'unit', '20')           |     32.81 |      23.51 |          26.63 |           18.84 |               1.81 |             5.85 |
| ('random_pps', 'unit', '35')           |     27.73 |      19.28 |          22.81 |           15.39 |               1.4  |             4.72 |
| ('random_pps', 'unit', '50')           |     23.27 |      16.28 |          18.75 |           12.92 |               1.1  |             3.99 |
| ('random_pps', 'unit', '70')           |     19.63 |      13.34 |          15.92 |           10.56 |               0.95 |             3.24 |
| ('random_pps', 'unit', '100')          |     16.38 |      11.31 |          13.22 |            8.93 |               0.74 |             2.77 |

## All boxes per test election

|   test |   seat_L1 |   share_L1 |   bloc_seat_L1 |   bloc_share_L1 |   threshold_errors |   max_list_error |
|-------:|----------:|-----------:|---------------:|----------------:|-------------------:|-----------------:|
|     17 |         4 |       1.68 |              2 |            1.28 |                  0 |             0.23 |
|     18 |         2 |       1.28 |              2 |            1.09 |                  0 |             0.21 |
|     19 |         2 |       1.55 |              2 |            1.28 |                  0 |             0.36 |
|     20 |         2 |       1.55 |              2 |            1.29 |                  0 |             0.44 |
|     21 |         2 |       1.39 |              0 |            1.07 |                  0 |             0.23 |
|     22 |         4 |       1.56 |              2 |            1.27 |                  0 |             0.43 |
|     23 |         4 |       1.76 |              4 |            1.48 |                  0 |             0.55 |
|     24 |         2 |       1.86 |              2 |            1.74 |                  0 |             0.34 |
|     25 |         2 |       2.18 |              2 |            1.97 |                  0 |             0.49 |
|     26 |         2 |       2.38 |              2 |            2.05 |                  0 |             0.48 |
