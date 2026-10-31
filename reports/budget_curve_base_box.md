# Seat error by box budget - unit: base_box, target: regular boxes

Held-out test elections 22-26. The target is the total of the
regular boxes (double envelopes excluded), so counting every box gives 0 error.
`seats_moved` = seat L1 / 2 (seats that moved between lists); goal: at most
2 in the mean and in the worst test election. `k` = budget N in boxes
(greedy panels; `boxes` = actually counted) or panel units (random / stratified,
averaged over
30 draws). Seed 0, decay 0.7; regularization strengths chosen by inner
validation (2 folds, 60 boxes); greedy panels nested.

## Smallest N that meets the goal

None of the methods meets the goal.

## Mean over test elections, worst election

|                                    |   boxes |   seats_moved |   share_L1 |   max_list_error |   bloc_seat_L1 |   threshold_errors |   worst_seats_moved |
|:-----------------------------------|--------:|--------------:|-----------:|-----------------:|---------------:|-------------------:|--------------------:|
| ('calibration', 'unit', 40)        |   38.4  |          8.2  |      11.83 |             2.97 |          12.4  |               0.6  |               18    |
| ('calibration', 'unit', 60)        |   58.2  |          7.2  |      10.54 |             2.63 |          10.4  |               0.4  |               14    |
| ('calibration', 'unit', 80)        |   76.2  |          5.8  |       9.16 |             2.36 |           8.4  |               0.2  |               13    |
| ('calibration', 'unit', 100)       |   96.6  |          5.4  |       8.12 |             1.8  |           7.6  |               0.2  |               12    |
| ('calibration', 'unit', 120)       |  116    |          5.6  |       7.71 |             1.72 |           8.4  |               0.4  |               12    |
| ('calibration', 'unit', 140)       |  136    |          5.8  |       8.22 |             1.84 |           7.6  |               0.2  |               12    |
| ('calibration', 'unit', 160)       |  158.4  |          6.4  |       8.08 |             1.72 |           8.4  |               0.4  |               13    |
| ('calibration_prior', 'unit', 40)  |   39.8  |          5.4  |       7.66 |             1.56 |           7.2  |               0.4  |               10    |
| ('calibration_prior', 'unit', 60)  |   60.8  |          4.2  |       6.8  |             1.51 |           5.6  |               0.2  |                7    |
| ('calibration_prior', 'unit', 80)  |   82.8  |          4.4  |       7.36 |             1.85 |           7.2  |               0    |                8    |
| ('calibration_prior', 'unit', 100) |  102.6  |          4    |       6.91 |             1.65 |           7.2  |               0    |                9    |
| ('calibration_prior', 'unit', 120) |  121    |          4.4  |       6.45 |             1.65 |           5.6  |               0.4  |                8    |
| ('calibration_prior', 'unit', 140) |  144    |          5    |       6.75 |             1.65 |           7.2  |               0.4  |                9    |
| ('calibration_prior', 'unit', 160) |  165.6  |          4.8  |       6.49 |             1.57 |           7.2  |               0.4  |                8    |
| ('greedy_budget', 'unit', 40)      |   41.2  |          7    |       9.32 |             1.82 |           9.2  |               0.6  |               12    |
| ('greedy_budget', 'unit', 60)      |   63.8  |          4.6  |       7.69 |             1.64 |           6    |               0    |                7    |
| ('greedy_budget', 'unit', 80)      |   84.8  |          4.2  |       7.19 |             1.48 |           6.4  |               0    |                6    |
| ('greedy_budget', 'unit', 100)     |  104.6  |          4.4  |       6.93 |             1.36 |           6.8  |               0    |                7    |
| ('greedy_budget', 'unit', 120)     |  115.6  |          4.8  |       6.77 |             1.35 |           7.6  |               0.2  |                8    |
| ('greedy_budget', 'unit', 140)     |  122    |          4.6  |       6.63 |             1.39 |           7.2  |               0.2  |                7    |
| ('greedy_budget', 'unit', 160)     |  128.2  |          4.8  |       6.8  |             1.44 |           7.2  |               0.2  |                8    |
| ('random_pps', 'single_box', 40)   |   32.61 |         13.14 |      18.46 |             4.79 |          21.57 |               1    |               15.83 |
| ('random_pps', 'single_box', 60)   |   49.12 |         11.03 |      15.77 |             4.09 |          18.41 |               0.83 |               14.17 |
| ('random_pps', 'single_box', 80)   |   65.25 |          9.15 |      12.91 |             3.29 |          15.43 |               0.71 |               11.97 |
| ('random_pps', 'single_box', 100)  |   80.89 |          8.05 |      11.35 |             2.92 |          13.37 |               0.6  |               10.9  |
| ('random_pps', 'single_box', 120)  |   97.54 |          8.21 |      11.45 |             2.87 |          13.95 |               0.57 |               10.73 |
| ('random_pps', 'single_box', 140)  |  113.69 |          7.54 |      10.37 |             2.74 |          12.64 |               0.59 |               10.77 |
| ('random_pps', 'single_box', 160)  |  129.81 |          6.95 |       9.86 |             2.44 |          11.63 |               0.45 |                9.13 |
| ('random_pps', 'unit', 40)         |   64.77 |         12.91 |      18.33 |             4.76 |          21.43 |               0.99 |               15.63 |
| ('random_pps', 'unit', 60)         |   98.38 |         10.93 |      15.65 |             4.06 |          18.29 |               0.8  |               13.83 |
| ('random_pps', 'unit', 80)         |  127.73 |          9.14 |      12.8  |             3.27 |          15.24 |               0.72 |               12.03 |
| ('random_pps', 'unit', 100)        |  159.27 |          7.96 |      11.27 |             2.91 |          13.27 |               0.57 |               10.5  |
| ('random_pps', 'unit', 120)        |  194.75 |          8.16 |      11.33 |             2.86 |          14.09 |               0.61 |               10.97 |
| ('random_pps', 'unit', 140)        |  225.91 |          7.53 |      10.31 |             2.74 |          12.64 |               0.6  |               11.07 |
| ('random_pps', 'unit', 160)        |  255.55 |          6.93 |       9.8  |             2.42 |          11.49 |               0.45 |                9.17 |
| ('stratified', 'single_box', 40)   |   32.63 |          9.39 |      13.18 |             3.06 |          11.97 |               0.77 |               13.17 |
| ('stratified', 'single_box', 60)   |   48.66 |          7.69 |      10.82 |             2.5  |          10.28 |               0.59 |               11.07 |
| ('stratified', 'single_box', 80)   |   65.05 |          6.79 |       9.57 |             2.25 |           9.2  |               0.53 |               10.53 |
| ('stratified', 'single_box', 100)  |   81.55 |          6.47 |       9.09 |             2.21 |           9.51 |               0.48 |                9.83 |
| ('stratified', 'single_box', 120)  |   97.23 |          6.33 |       8.52 |             2.1  |           9.19 |               0.51 |                9.3  |
| ('stratified', 'single_box', 140)  |  113.96 |          5.42 |       7.78 |             1.9  |           7.52 |               0.37 |                7.8  |
| ('stratified', 'single_box', 160)  |  130.43 |          5.31 |       7.36 |             1.74 |           7.76 |               0.41 |                8.3  |
| ('stratified', 'unit', 40)         |   65.01 |          9.19 |      12.81 |             3.02 |          11.83 |               0.77 |               12.87 |
| ('stratified', 'unit', 60)         |   95.68 |          7.59 |      10.76 |             2.48 |          10.24 |               0.56 |               10.83 |
| ('stratified', 'unit', 80)         |  129.48 |          6.73 |       9.36 |             2.22 |           9.35 |               0.54 |               10.23 |
| ('stratified', 'unit', 100)        |  160.73 |          6.45 |       8.97 |             2.2  |           9.63 |               0.49 |                9.83 |
| ('stratified', 'unit', 120)        |  192.06 |          6.17 |       8.38 |             2.08 |           9.07 |               0.47 |                8.9  |
| ('stratified', 'unit', 140)        |  224.92 |          5.39 |       7.65 |             1.87 |           7.61 |               0.35 |                7.8  |
| ('stratified', 'unit', 160)        |  257.86 |          5.25 |       7.26 |             1.74 |           7.84 |               0.43 |                8.33 |
| ('weight_prior', 'unit', 40)       |   44    |          5.8  |       9.24 |             2.2  |           8.8  |               0.2  |                9    |
| ('weight_prior', 'unit', 60)       |   64.4  |          5.4  |       7.22 |             1.71 |           7.6  |               0.4  |               10    |
| ('weight_prior', 'unit', 80)       |   84.2  |          4.2  |       6.65 |             1.5  |           5.6  |               0.2  |                8    |
| ('weight_prior', 'unit', 100)      |  103.2  |          3.6  |       5.97 |             1.43 |           5.2  |               0    |                5    |
| ('weight_prior', 'unit', 120)      |  126.4  |          3.4  |       5.39 |             1.25 |           4.8  |               0    |                5    |
| ('weight_prior', 'unit', 140)      |  147.2  |          4    |       5.4  |             1.3  |           5.6  |               0.2  |                6    |
| ('weight_prior', 'unit', 160)      |  167    |          3.2  |       5.19 |             1.3  |           5.2  |               0    |                6    |

## Seats moved per test election

|                                    |   22 |   23 |   24 |   25 |   26 |
|:-----------------------------------|-----:|-----:|-----:|-----:|-----:|
| ('calibration', 'unit', 40)        |  4   |  3   | 18   | 11   |  5   |
| ('calibration', 'unit', 60)        |  4   |  2   | 14   | 11   |  5   |
| ('calibration', 'unit', 80)        |  3   |  2   | 13   |  7   |  4   |
| ('calibration', 'unit', 100)       |  3   |  1   | 12   |  6   |  5   |
| ('calibration', 'unit', 120)       |  3   |  1   | 12   |  7   |  5   |
| ('calibration', 'unit', 140)       |  3   |  1   | 12   |  7   |  6   |
| ('calibration', 'unit', 160)       |  3   |  2   | 13   |  8   |  6   |
| ('calibration_prior', 'unit', 40)  |  3   |  3   | 10   |  8   |  3   |
| ('calibration_prior', 'unit', 60)  |  1   |  3   |  7   |  6   |  4   |
| ('calibration_prior', 'unit', 80)  |  3   |  2   |  8   |  5   |  4   |
| ('calibration_prior', 'unit', 100) |  1   |  2   |  9   |  4   |  4   |
| ('calibration_prior', 'unit', 120) |  2   |  2   |  6   |  8   |  4   |
| ('calibration_prior', 'unit', 140) |  2   |  2   |  9   |  8   |  4   |
| ('calibration_prior', 'unit', 160) |  1   |  3   |  8   |  8   |  4   |
| ('greedy_budget', 'unit', 40)      |  2   |  3   | 12   | 12   |  6   |
| ('greedy_budget', 'unit', 60)      |  2   |  3   |  7   |  7   |  4   |
| ('greedy_budget', 'unit', 80)      |  3   |  4   |  6   |  5   |  3   |
| ('greedy_budget', 'unit', 100)     |  3   |  3   |  7   |  6   |  3   |
| ('greedy_budget', 'unit', 120)     |  3   |  3   |  6   |  8   |  4   |
| ('greedy_budget', 'unit', 140)     |  3   |  3   |  6   |  7   |  4   |
| ('greedy_budget', 'unit', 160)     |  3   |  3   |  6   |  8   |  4   |
| ('random_pps', 'single_box', 40)   | 10.9 | 10.4 | 15.8 | 14.3 | 14.3 |
| ('random_pps', 'single_box', 60)   |  8.5 |  8.3 | 13.1 | 14.2 | 11.1 |
| ('random_pps', 'single_box', 80)   |  6.9 |  7   | 11.2 | 12   |  8.7 |
| ('random_pps', 'single_box', 100)  |  6.5 |  5.3 |  9.5 | 10.9 |  8   |
| ('random_pps', 'single_box', 120)  |  6.7 |  5.5 | 10.3 | 10.7 |  7.9 |
| ('random_pps', 'single_box', 140)  |  6.3 |  5.1 |  8.4 | 10.8 |  7.2 |
| ('random_pps', 'single_box', 160)  |  5.2 |  5.3 |  8   |  9.1 |  7.1 |
| ('random_pps', 'unit', 40)         | 10.9 | 10.2 | 15.6 | 13.8 | 14.1 |
| ('random_pps', 'unit', 60)         |  8.6 |  8.5 | 12.6 | 13.8 | 11.1 |
| ('random_pps', 'unit', 80)         |  6.8 |  6.9 | 11.1 | 12   |  8.8 |
| ('random_pps', 'unit', 100)        |  6.6 |  5.4 |  9.4 | 10.5 |  8   |
| ('random_pps', 'unit', 120)        |  6.6 |  5.6 | 10   | 11   |  7.7 |
| ('random_pps', 'unit', 140)        |  6.3 |  5.1 |  7.9 | 11.1 |  7.2 |
| ('random_pps', 'unit', 160)        |  5.2 |  5.3 |  7.7 |  9.2 |  7.3 |
| ('stratified', 'single_box', 40)   |  5.5 |  6   | 13.1 | 13.2 |  9.2 |
| ('stratified', 'single_box', 60)   |  5.2 |  4.8 | 10.5 | 11.1 |  7   |
| ('stratified', 'single_box', 80)   |  4.3 |  4.1 |  9.2 | 10.5 |  5.8 |
| ('stratified', 'single_box', 100)  |  3.9 |  3.6 |  9.8 |  9   |  6.1 |
| ('stratified', 'single_box', 120)  |  3.7 |  3.7 |  8.6 |  9.3 |  6.4 |
| ('stratified', 'single_box', 140)  |  3.4 |  2.9 |  7.7 |  7.8 |  5.3 |
| ('stratified', 'single_box', 160)  |  3.4 |  3.1 |  6.8 |  8.3 |  4.9 |
| ('stratified', 'unit', 40)         |  5.6 |  5.5 | 12.9 | 12.8 |  9.3 |
| ('stratified', 'unit', 60)         |  5   |  4.7 | 10.8 | 10.5 |  6.9 |
| ('stratified', 'unit', 80)         |  4.2 |  4.1 |  9   | 10.2 |  6.1 |
| ('stratified', 'unit', 100)        |  3.8 |  3.7 |  9.8 |  9   |  6   |
| ('stratified', 'unit', 120)        |  3.7 |  3.7 |  8.2 |  8.9 |  6.4 |
| ('stratified', 'unit', 140)        |  3.5 |  3   |  7.2 |  7.8 |  5.4 |
| ('stratified', 'unit', 160)        |  3.2 |  3   |  6.8 |  8.3 |  5   |
| ('weight_prior', 'unit', 40)       |  3   |  3   |  7   |  9   |  7   |
| ('weight_prior', 'unit', 60)       |  3   |  3   |  6   | 10   |  5   |
| ('weight_prior', 'unit', 80)       |  1   |  3   |  4   |  8   |  5   |
| ('weight_prior', 'unit', 100)      |  1   |  3   |  5   |  4   |  5   |
| ('weight_prior', 'unit', 120)      |  1   |  3   |  5   |  3   |  5   |
| ('weight_prior', 'unit', 140)      |  1   |  3   |  6   |  5   |  5   |
| ('weight_prior', 'unit', 160)      |  1   |  2   |  6   |  3   |  4   |
