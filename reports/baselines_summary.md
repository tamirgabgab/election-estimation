# Baselines at equal counting budgets

Mean over held-out test elections 22-26. `k` is the budget in ballot
boxes; `boxes` is what was actually counted (budget methods estimate unit costs from
the last training election, so they can overshoot slightly). Only configurations that
count about k boxes are shown: one box per panel unit (`single_box`) or whole units
under a box budget (`*_budget`). Seats in seats, shares in percentage points.

Floor - counting every regular box: 2.8 seats, 1.95 pp (the double-envelope gap).

## Budget 35 boxes

|                                               |   boxes |   seat_L1 |   share_L1 |   bloc_seat_L1 |   threshold_errors |
|:----------------------------------------------|--------:|----------:|-----------:|---------------:|-------------------:|
| ('area', 'greedy_budget', 'unit')             |   38.6  |      8.4  |       6.45 |           5.6  |               0.2  |
| ('settlement', 'greedy_budget', 'unit')       |   35.8  |     11.6  |       7.49 |           6.4  |               0.6  |
| ('base_box', 'greedy_budget', 'unit')         |   34.6  |     13.6  |      10.51 |          11.6  |               0.4  |
| ('base_box', 'greedy', 'single_box')          |   31    |     15.47 |       9.82 |          10.21 |               0.82 |
| ('area', 'stratified', 'single_box')          |   34.4  |     15.88 |      11.23 |           9.4  |               0.59 |
| ('area', 'greedy', 'single_box')              |   34    |     16.76 |      11.93 |          12.55 |               0.65 |
| ('settlement', 'stratified', 'single_box')    |   34.99 |     17.41 |      12.76 |          12.03 |               0.55 |
| ('base_box', 'stratified', 'single_box')      |   29    |     19.21 |      13.38 |          12.33 |               0.92 |
| ('settlement', 'random_pps', 'single_box')    |   34.98 |     24.43 |      17.58 |          20.8  |               0.82 |
| ('area', 'random_pps', 'single_box')          |   34.15 |     24.69 |      17.68 |          20.09 |               0.86 |
| ('settlement', 'greedy', 'single_box')        |   35    |     27.55 |      20.14 |          21.35 |               0.78 |
| ('base_box', 'random_pooled', 'single_box')   |   29.53 |     28.37 |      20.34 |          23.65 |               1.19 |
| ('base_box', 'random_pps', 'single_box')      |   28.51 |     28.68 |      20.29 |          23.92 |               1.18 |
| ('area', 'random_pooled', 'single_box')       |   34.07 |     30.75 |      22.01 |          26.56 |               1.43 |
| ('settlement', 'random_pooled', 'single_box') |   34.99 |     56.49 |      39.1  |          45.36 |               2.72 |

## Budget 50 boxes

|                                               |   boxes |   seat_L1 |   share_L1 |   bloc_seat_L1 |   threshold_errors |
|:----------------------------------------------|--------:|----------:|-----------:|---------------:|-------------------:|
| ('base_box', 'milp_budget', 'unit')           |   47.6  |      8    |       7.31 |           5.6  |               0    |
| ('settlement', 'milp_budget', 'unit')         |   51.4  |     10.4  |       8.17 |           6.4  |               0.2  |
| ('base_box', 'greedy_budget', 'unit')         |   48.8  |     10.4  |       8.52 |           8.4  |               0.2  |
| ('area', 'greedy_budget', 'unit')             |   55.2  |     11.2  |       7.6  |           7.6  |               0.4  |
| ('area', 'milp_budget', 'unit')               |   55.2  |     11.2  |       7.6  |           7.6  |               0.4  |
| ('area', 'stratified', 'single_box')          |   48.85 |     13.12 |       9.83 |           8.32 |               0.36 |
| ('settlement', 'greedy_budget', 'unit')       |   51.4  |     13.2  |      10.26 |           8.8  |               0    |
| ('base_box', 'greedy', 'single_box')          |   43.8  |     14.16 |       8.54 |          10.48 |               0.89 |
| ('settlement', 'stratified', 'single_box')    |   49.97 |     14.39 |      10.29 |           9.84 |               0.5  |
| ('area', 'greedy', 'single_box')              |   47.4  |     15.56 |      10.36 |          10.88 |               0.77 |
| ('base_box', 'stratified', 'single_box')      |   41.44 |     16.33 |      11.52 |          10.43 |               0.67 |
| ('area', 'random_pps', 'single_box')          |   48.99 |     20.28 |      14.49 |          16.29 |               0.68 |
| ('settlement', 'random_pps', 'single_box')    |   49.99 |     21.95 |      16.05 |          18.39 |               0.61 |
| ('settlement', 'greedy', 'single_box')        |   50    |     23    |      17.29 |          18.21 |               0.65 |
| ('base_box', 'random_pooled', 'single_box')   |   42.15 |     24.87 |      17.59 |          20.96 |               1.07 |
| ('base_box', 'random_pps', 'single_box')      |   40.61 |     24.97 |      17.65 |          20.89 |               0.98 |
| ('area', 'random_pooled', 'single_box')       |   48.66 |     30.87 |      21.65 |          26.15 |               1.35 |
| ('settlement', 'random_pooled', 'single_box') |   49.93 |     54.84 |      37.94 |          41.01 |               2.72 |

## Budget 70 boxes

|                                               |   boxes |   seat_L1 |   share_L1 |   bloc_seat_L1 |   threshold_errors |
|:----------------------------------------------|--------:|----------:|-----------:|---------------:|-------------------:|
| ('base_box', 'greedy_budget', 'unit')         |   68    |      8.4  |       6.63 |           6    |               0    |
| ('base_box', 'milp_budget', 'unit')           |   70    |      8.4  |       6.08 |           6    |               0.2  |
| ('settlement', 'milp_budget', 'unit')         |   72    |      9.6  |       7.78 |           6    |               0.2  |
| ('area', 'stratified', 'single_box')          |   68.52 |     11.28 |       8.46 |           7.56 |               0.28 |
| ('area', 'milp_budget', 'unit')               |   72.4  |     12.4  |       8.49 |           6.4  |               0.4  |
| ('area', 'greedy_budget', 'unit')             |   72.4  |     12.4  |       8.49 |           6.4  |               0.4  |
| ('settlement', 'stratified', 'single_box')    |   69.98 |     12.93 |       9.66 |           9.67 |               0.31 |
| ('base_box', 'greedy', 'single_box')          |   60    |     13.03 |       7.7  |          10.19 |               0.76 |
| ('area', 'greedy', 'single_box')              |   58.8  |     14.17 |       9.66 |           9.95 |               0.68 |
| ('base_box', 'stratified', 'single_box')      |   56.81 |     14.17 |      10.09 |          10.12 |               0.57 |
| ('settlement', 'greedy_budget', 'unit')       |   73.2  |     16    |      11.3  |           7.2  |               0.4  |
| ('area', 'random_pps', 'single_box')          |   68.58 |     17.8  |      12.88 |          15.03 |               0.55 |
| ('settlement', 'random_pps', 'single_box')    |   69.97 |     19.45 |      14.58 |          16.72 |               0.47 |
| ('base_box', 'random_pps', 'single_box')      |   57.24 |     20.71 |      14.33 |          17.04 |               0.85 |
| ('base_box', 'random_pooled', 'single_box')   |   58.61 |     20.87 |      14.59 |          17.53 |               0.85 |
| ('settlement', 'greedy', 'single_box')        |   70    |     21.4  |      15.97 |          16.88 |               0.61 |
| ('area', 'random_pooled', 'single_box')       |   68.18 |     26.57 |      18.24 |          22.44 |               1.17 |
| ('settlement', 'random_pooled', 'single_box') |   69.95 |     53.37 |      36.53 |          39.67 |               2.57 |

## Budget 100 boxes

|                                               |   boxes |   seat_L1 |   share_L1 |   bloc_seat_L1 |   threshold_errors |
|:----------------------------------------------|--------:|----------:|-----------:|---------------:|-------------------:|
| ('base_box', 'greedy_budget', 'unit')         |   93.8  |      8    |       6.62 |           6    |               0.2  |
| ('area', 'stratified', 'single_box')          |   98.01 |     10.19 |       7.64 |           7.44 |               0.23 |
| ('settlement', 'greedy_budget', 'unit')       |  105.2  |     12    |       8.93 |           6.8  |               0.4  |
| ('settlement', 'stratified', 'single_box')    |   99.97 |     12.21 |       9.15 |           8.61 |               0.27 |
| ('area', 'greedy', 'single_box')              |   68.2  |     12.23 |       8.61 |           8.55 |               0.51 |
| ('base_box', 'stratified', 'single_box')      |   81.75 |     12.29 |       8.48 |           8.31 |               0.49 |
| ('area', 'greedy_budget', 'unit')             |   86    |     13.6  |       9.21 |           7.6  |               0.6  |
| ('base_box', 'greedy', 'single_box')          |   83.6  |     14.29 |       7.91 |          10.32 |               0.93 |
| ('area', 'random_pps', 'single_box')          |   97.91 |     15.33 |      11.05 |          13.31 |               0.5  |
| ('base_box', 'random_pps', 'single_box')      |   81.49 |     16.65 |      11.68 |          13.56 |               0.64 |
| ('settlement', 'greedy', 'single_box')        |  100    |     17.11 |      13.38 |          13.68 |               0.35 |
| ('base_box', 'random_pooled', 'single_box')   |   84.36 |     18.05 |      12.45 |          15    |               0.71 |
| ('settlement', 'random_pps', 'single_box')    |   99.95 |     20.67 |      15.36 |          18.09 |               0.49 |
| ('area', 'random_pooled', 'single_box')       |   97.41 |     25.17 |      17.18 |          21.53 |               1.15 |
| ('settlement', 'random_pooled', 'single_box') |   99.93 |     52.04 |      35.32 |          37.47 |               2.52 |
