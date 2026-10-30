# Baselines - unit: settlement

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
| ('greedy', 'single_box', '10')         |     48.75 |      34.89 |          37.6  |           26.56 |               1.81 |             9.28 |
| ('greedy', 'single_box', '20')         |     38.71 |      27.83 |          30.81 |           21.79 |               1.33 |             7.33 |
| ('greedy', 'single_box', '35')         |     27.55 |      20.14 |          21.35 |           15.2  |               0.78 |             5.12 |
| ('greedy', 'single_box', '50')         |     23    |      17.29 |          18.21 |           13.41 |               0.65 |             4.32 |
| ('greedy', 'single_box', '70')         |     21.4  |      15.97 |          16.88 |           12.67 |               0.61 |             4.01 |
| ('greedy', 'single_box', '100')        |     17.11 |      13.38 |          13.68 |           10.45 |               0.35 |             3.31 |
| ('greedy', 'unit', '10')               |      8.4  |       6.5  |           6    |            4.67 |               0    |             1.51 |
| ('greedy', 'unit', '20')               |      6.4  |       5.24 |           4.8  |            3.86 |               0    |             1.38 |
| ('greedy', 'unit', '35')               |      6    |       4.91 |           4    |            3.31 |               0    |             1.18 |
| ('greedy', 'unit', '50')               |      7.6  |       4.54 |           6    |            3.44 |               0.2  |             1.15 |
| ('greedy', 'unit', '70')               |      6.4  |       4.6  |           5.6  |            3.67 |               0.2  |             1.25 |
| ('greedy', 'unit', '100')              |      6    |       4.57 |           5.2  |            3.42 |               0.2  |             1.28 |
| ('random_pooled', 'single_box', '10')  |     69    |      49.79 |          55.69 |           39.96 |               3.57 |            11.11 |
| ('random_pooled', 'single_box', '20')  |     60.52 |      42.67 |          49.17 |           34.21 |               3.02 |             9.17 |
| ('random_pooled', 'single_box', '35')  |     56.49 |      39.1  |          45.36 |           30.82 |               2.72 |             8.27 |
| ('random_pooled', 'single_box', '50')  |     54.84 |      37.94 |          41.01 |           27.53 |               2.72 |             7.65 |
| ('random_pooled', 'single_box', '70')  |     53.37 |      36.53 |          39.67 |           26.4  |               2.57 |             6.8  |
| ('random_pooled', 'single_box', '100') |     52.04 |      35.32 |          37.47 |           24.68 |               2.52 |             6.39 |
| ('random_pooled', 'unit', '10')        |     82.01 |      59.84 |          71.49 |           52.33 |               3.73 |            19.49 |
| ('random_pooled', 'unit', '20')        |     66.81 |      47.7  |          58.04 |           41.62 |               2.88 |            14.02 |
| ('random_pooled', 'unit', '35')        |     51.13 |      36.26 |          44.61 |           31.64 |               2.05 |            10.69 |
| ('random_pooled', 'unit', '50')        |     48.29 |      33.91 |          42.44 |           29.71 |               2.03 |             9.72 |
| ('random_pooled', 'unit', '70')        |     42.4  |      29.97 |          38.04 |           26.59 |               1.7  |             8.5  |
| ('random_pooled', 'unit', '100')       |     39.33 |      28.21 |          35.65 |           25.27 |               1.27 |             7.48 |
| ('random_pps', 'single_box', '10')     |     44.33 |      31.94 |          34.49 |           24.9  |               2.01 |             8.14 |
| ('random_pps', 'single_box', '20')     |     31.83 |      22.83 |          26.32 |           18.57 |               1.35 |             6.05 |
| ('random_pps', 'single_box', '35')     |     24.43 |      17.58 |          20.8  |           14.47 |               0.82 |             4.53 |
| ('random_pps', 'single_box', '50')     |     21.95 |      16.05 |          18.39 |           13.28 |               0.61 |             4.35 |
| ('random_pps', 'single_box', '70')     |     19.45 |      14.58 |          16.72 |           12.25 |               0.47 |             4.02 |
| ('random_pps', 'single_box', '100')    |     20.67 |      15.36 |          18.09 |           13.27 |               0.49 |             4.4  |
| ('random_pps', 'unit', '10')           |     37.99 |      27.31 |          31.53 |           22.57 |               1.57 |             7.43 |
| ('random_pps', 'unit', '20')           |     27.49 |      19.33 |          23.88 |           16.5  |               1.11 |             5.54 |
| ('random_pps', 'unit', '35')           |     21.27 |      15.52 |          18.49 |           13.16 |               0.62 |             4.28 |
| ('random_pps', 'unit', '50')           |     19.57 |      14.26 |          16.72 |           12.03 |               0.53 |             4    |
| ('random_pps', 'unit', '70')           |     17.77 |      13.33 |          15.64 |           11.63 |               0.35 |             3.81 |
| ('random_pps', 'unit', '100')          |     19.88 |      14.88 |          17.69 |           13.12 |               0.39 |             4.28 |

## Mean over all test elections (17-26)

|                                        |   seat_L1 |   share_L1 |   bloc_seat_L1 |   bloc_share_L1 |   threshold_errors |   max_list_error |
|:---------------------------------------|----------:|-----------:|---------------:|----------------:|-------------------:|-----------------:|
| ('all_boxes', 'unit', 'all')           |      2.6  |       1.72 |           2    |            1.45 |               0    |             0.37 |
| ('greedy', 'single_box', '10')         |     48.93 |      35.17 |          38.19 |           26.59 |               2.07 |             9.21 |
| ('greedy', 'single_box', '20')         |     38.32 |      27.74 |          30.09 |           21.01 |               1.52 |             7.01 |
| ('greedy', 'single_box', '35')         |     30.11 |      21.79 |          22.89 |           15.94 |               1.14 |             5.39 |
| ('greedy', 'single_box', '50')         |     26.37 |      19.22 |          19.77 |           13.89 |               1.05 |             4.65 |
| ('greedy', 'single_box', '70')         |     25.41 |      18.29 |          18.95 |           13.29 |               1.05 |             4.48 |
| ('greedy', 'single_box', '100')        |     23.73 |      17.17 |          17.57 |           12.29 |               0.94 |             4.05 |
| ('greedy', 'unit', '10')               |      9.8  |       7.02 |           6.8  |            4.33 |               0.4  |             1.53 |
| ('greedy', 'unit', '20')               |      7    |       6.08 |           5.2  |            3.74 |               0.2  |             1.42 |
| ('greedy', 'unit', '35')               |      7    |       5.74 |           4.2  |            3.1  |               0.2  |             1.19 |
| ('greedy', 'unit', '50')               |      7.6  |       5.57 |           5.2  |            3.13 |               0.3  |             1.24 |
| ('greedy', 'unit', '70')               |      8    |       5.54 |           5.6  |            3.26 |               0.5  |             1.31 |
| ('greedy', 'unit', '100')              |      8    |       5.48 |           5.6  |            3.14 |               0.5  |             1.28 |
| ('random_pooled', 'single_box', '10')  |     69.58 |      50.41 |          54.25 |           38.67 |               3.82 |            11.62 |
| ('random_pooled', 'single_box', '20')  |     60.99 |      43.48 |          48.94 |           34.02 |               3.21 |             9.8  |
| ('random_pooled', 'single_box', '35')  |     56.15 |      39.11 |          44.05 |           29.63 |               2.86 |             8.56 |
| ('random_pooled', 'single_box', '50')  |     54.5  |      37.54 |          41.07 |           27.04 |               2.93 |             7.93 |
| ('random_pooled', 'single_box', '70')  |     53.67 |      36.58 |          39.7  |           25.84 |               2.77 |             7.38 |
| ('random_pooled', 'single_box', '100') |     53.1  |      35.99 |          38.98 |           25.27 |               2.7  |             7.1  |
| ('random_pooled', 'unit', '10')        |     81.27 |      59.43 |          68.89 |           50.22 |               3.95 |            17.48 |
| ('random_pooled', 'unit', '20')        |     66.95 |      47.98 |          58.71 |           42.08 |               3.13 |            13.71 |
| ('random_pooled', 'unit', '35')        |     53.07 |      37.67 |          46.53 |           32.93 |               2.32 |            10.47 |
| ('random_pooled', 'unit', '50')        |     46.76 |      32.28 |          41.11 |           28.16 |               2.4  |             8.91 |
| ('random_pooled', 'unit', '70')        |     41.52 |      28.71 |          36.95 |           25.31 |               1.99 |             7.7  |
| ('random_pooled', 'unit', '100')       |     36.95 |      25.74 |          33.39 |           22.97 |               1.57 |             6.67 |
| ('random_pps', 'single_box', '10')     |     43.91 |      31.4  |          34.25 |           24.44 |               2.39 |             7.89 |
| ('random_pps', 'single_box', '20')     |     31.93 |      22.6  |          25.89 |           18    |               1.62 |             5.57 |
| ('random_pps', 'single_box', '35')     |     24.25 |      17.05 |          19.69 |           13.43 |               1.04 |             4.17 |
| ('random_pps', 'single_box', '50')     |     22.21 |      16.17 |          18.3  |           13.06 |               0.72 |             4.06 |
| ('random_pps', 'single_box', '70')     |     20.67 |      15.27 |          17.38 |           12.59 |               0.58 |             3.78 |
| ('random_pps', 'single_box', '100')    |     22.65 |      16.62 |          18.97 |           13.73 |               0.58 |             4.24 |
| ('random_pps', 'unit', '10')           |     37    |      26.1  |          30.49 |           21.4  |               1.91 |             6.83 |
| ('random_pps', 'unit', '20')           |     27.33 |      18.87 |          23.23 |           15.8  |               1.32 |             4.93 |
| ('random_pps', 'unit', '35')           |     21.13 |      14.83 |          17.69 |           12.26 |               0.82 |             3.82 |
| ('random_pps', 'unit', '50')           |     19.93 |      14.38 |          17.01 |           12.03 |               0.65 |             3.7  |
| ('random_pps', 'unit', '70')           |     18.79 |      13.99 |          16.31 |           12.09 |               0.4  |             3.58 |
| ('random_pps', 'unit', '100')          |     21.44 |      15.93 |          18.38 |           13.5  |               0.47 |             4.07 |

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
