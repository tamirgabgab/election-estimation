# Panels of whole settlements - target: regular boxes

Held-out test elections 22-26; `k` = settlements in the panel, each
counted in full (`boxes` = what that costs). `seats_moved` = seat L1 / 2; goal: at
most 2 in the mean and in the worst election. Seed 0, decay 0.7,
strengths by inner validation (2 folds, 35 settlements); random PPS over 30
draws.

## Mean over test elections, worst election

|                      |   boxes |   seats_moved |   share_L1 |   max_list_error |   bloc_seat_L1 |   threshold_errors |   worst_seats_moved |
|:---------------------|--------:|--------------:|-----------:|-----------------:|---------------:|-------------------:|--------------------:|
| ('calibration', 20)  | 1177.4  |          3.6  |       5.04 |             1.2  |           5.6  |               0.2  |                5    |
| ('calibration', 30)  | 1583.6  |          3.6  |       5.3  |             1.58 |           5.6  |               0.2  |                6    |
| ('calibration', 35)  | 1750.8  |          4    |       5.63 |             1.56 |           5.6  |               0.2  |                5    |
| ('calibration', 40)  | 1993.2  |          3.4  |       5.59 |             1.5  |           4.8  |               0    |                5    |
| ('calibration', 50)  | 2226.6  |          3.4  |       5.21 |             1.41 |           4.8  |               0.2  |                5    |
| ('greedy', 20)       |  653    |          3    |       5.1  |             1.45 |           4    |               0    |                5    |
| ('greedy', 30)       |  764.4  |          3.6  |       4.52 |             1.37 |           5.6  |               0.2  |                5    |
| ('greedy', 35)       |  787    |          3    |       4.46 |             1.43 |           5.6  |               0.2  |                5    |
| ('greedy', 40)       |  843.8  |          3.2  |       4.44 |             1.42 |           5.2  |               0.2  |                5    |
| ('greedy', 50)       |  979.6  |          3.4  |       4.48 |             1.33 |           5.6  |               0.2  |                5    |
| ('random_pps', 20)   | 3267.55 |         13.87 |      19.74 |             5.43 |          24.09 |               1.03 |               15.03 |
| ('random_pps', 30)   | 4243.37 |         10.97 |      15.96 |             4.26 |          18.25 |               0.63 |               12.63 |
| ('random_pps', 35)   | 4711.42 |         10.75 |      15.08 |             4.3  |          18.21 |               0.7  |               12.8  |
| ('random_pps', 40)   | 5100.35 |          9.65 |      13.81 |             3.87 |          16.85 |               0.53 |               11.2  |
| ('random_pps', 50)   | 5728.77 |          9.43 |      13.62 |             3.85 |          16.48 |               0.46 |               12.67 |
| ('weight_prior', 20) |  341.4  |          4    |       5.29 |             1.65 |           6.4  |               0.2  |                5    |
| ('weight_prior', 30) |  413.8  |          3.2  |       5.17 |             1.48 |           4.4  |               0    |                6    |
| ('weight_prior', 35) |  430    |          2.8  |       4.94 |             1.5  |           4.4  |               0    |                6    |
| ('weight_prior', 40) |  474.2  |          2.8  |       4.64 |             1.36 |           4.4  |               0    |                5    |
| ('weight_prior', 50) |  502.2  |          2.8  |       4.76 |             1.34 |           4.4  |               0    |                5    |

## Seats moved per test election

|                      |   22 |   23 |   24 |   25 |   26 |
|:---------------------|-----:|-----:|-----:|-----:|-----:|
| ('calibration', 20)  |  2   |  3   |  3   |  5   |  5   |
| ('calibration', 30)  |  2   |  3   |  3   |  4   |  6   |
| ('calibration', 35)  |  2   |  4   |  4   |  5   |  5   |
| ('calibration', 40)  |  2   |  3   |  4   |  3   |  5   |
| ('calibration', 50)  |  1   |  3   |  4   |  4   |  5   |
| ('greedy', 20)       |  2   |  2   |  4   |  2   |  5   |
| ('greedy', 30)       |  1   |  3   |  5   |  5   |  4   |
| ('greedy', 35)       |  1   |  3   |  3   |  5   |  3   |
| ('greedy', 40)       |  1   |  3   |  3   |  5   |  4   |
| ('greedy', 50)       |  1   |  3   |  4   |  5   |  4   |
| ('random_pps', 20)   | 13.3 | 13.3 | 12.8 | 15   | 15   |
| ('random_pps', 30)   |  9.8 |  9.1 | 12.3 | 12.6 | 11.1 |
| ('random_pps', 35)   |  9.1 |  8.8 | 12   | 12.8 | 11.1 |
| ('random_pps', 40)   |  8.5 |  8.5 | 10.5 | 11.2 |  9.6 |
| ('random_pps', 50)   |  7.2 |  8.3 | 10.3 | 12.7 |  8.6 |
| ('weight_prior', 20) |  4   |  2   |  5   |  4   |  5   |
| ('weight_prior', 30) |  2   |  2   |  4   |  2   |  6   |
| ('weight_prior', 35) |  1   |  2   |  3   |  2   |  6   |
| ('weight_prior', 40) |  1   |  2   |  4   |  2   |  5   |
| ('weight_prior', 50) |  1   |  2   |  4   |  2   |  5   |
