# Swing model on settlement panels - target: regular boxes

Held-out test elections 22-26; `k` = settlements in the panel, counted
in full (`boxes` = what that costs). `swing`: previous national bloc shares plus the
panel's weighted bloc swing, lists split within blocs by the panel; weights fit to
past national bloc swings plus list-share rows scaled by `level`, pulled towards
size-proportional weights by `mu`. `level_*`: the level panels of
`settlement_panel.md`. `seats_moved` = seat L1 / 2; goal: at most
2 in the mean and in the worst election. Seed 0, decay 0.7; grid
{'mu': [0.003, 0.01, 0.03], 'level': [0.1, 0.3, 1.0]} chosen by inner validation (2 folds, 35 settlements).

## Mean over test elections, worst election

|                            |   boxes |   seats_moved |   share_L1 |   max_list_error |   bloc_seat_L1 |   bloc_share_L1 |   threshold_errors |   worst_seats_moved |
|:---------------------------|--------:|--------------:|-----------:|-----------------:|---------------:|----------------:|-------------------:|--------------------:|
| ('level_greedy', 20)       |   653   |           3   |       5.1  |             1.45 |            4   |            3.71 |                0   |                   5 |
| ('level_greedy', 30)       |   764.4 |           3.6 |       4.52 |             1.37 |            5.6 |            3.48 |                0.2 |                   5 |
| ('level_greedy', 35)       |   787   |           3   |       4.46 |             1.43 |            5.6 |            3.45 |                0.2 |                   5 |
| ('level_greedy', 40)       |   843.8 |           3.2 |       4.44 |             1.42 |            5.2 |            3.47 |                0.2 |                   5 |
| ('level_greedy', 50)       |   979.6 |           3.4 |       4.48 |             1.33 |            5.6 |            3.43 |                0.2 |                   5 |
| ('level_weight_prior', 20) |   341.4 |           4   |       5.29 |             1.65 |            6.4 |            4.49 |                0.2 |                   5 |
| ('level_weight_prior', 30) |   413.8 |           3.2 |       5.17 |             1.48 |            4.4 |            4.06 |                0   |                   6 |
| ('level_weight_prior', 35) |   430   |           2.8 |       4.94 |             1.5  |            4.4 |            4.08 |                0   |                   6 |
| ('level_weight_prior', 40) |   474.2 |           2.8 |       4.64 |             1.36 |            4.4 |            4.1  |                0   |                   5 |
| ('level_weight_prior', 50) |   502.2 |           2.8 |       4.76 |             1.34 |            4.4 |            4.05 |                0   |                   5 |
| ('swing', 20)              |   498.6 |           3.4 |       5.54 |             1.61 |            3.6 |            3.14 |                0   |                   5 |
| ('swing', 30)              |   593   |           2.6 |       4.91 |             1.55 |            4   |            3.17 |                0.2 |                   4 |
| ('swing', 35)              |   623.2 |           3.2 |       4.92 |             1.54 |            4.8 |            3.21 |                0.2 |                   6 |
| ('swing', 40)              |   656.4 |           3   |       4.7  |             1.5  |            4   |            3.27 |                0.2 |                   6 |
| ('swing', 50)              |   777   |           2.6 |       4.32 |             1.36 |            4.4 |            3.36 |                0.2 |                   5 |

## Seats moved per test election

|                            |   22 |   23 |   24 |   25 |   26 |
|:---------------------------|-----:|-----:|-----:|-----:|-----:|
| ('level_greedy', 20)       |    2 |    2 |    4 |    2 |    5 |
| ('level_greedy', 30)       |    1 |    3 |    5 |    5 |    4 |
| ('level_greedy', 35)       |    1 |    3 |    3 |    5 |    3 |
| ('level_greedy', 40)       |    1 |    3 |    3 |    5 |    4 |
| ('level_greedy', 50)       |    1 |    3 |    4 |    5 |    4 |
| ('level_weight_prior', 20) |    4 |    2 |    5 |    4 |    5 |
| ('level_weight_prior', 30) |    2 |    2 |    4 |    2 |    6 |
| ('level_weight_prior', 35) |    1 |    2 |    3 |    2 |    6 |
| ('level_weight_prior', 40) |    1 |    2 |    4 |    2 |    5 |
| ('level_weight_prior', 50) |    1 |    2 |    4 |    2 |    5 |
| ('swing', 20)              |    4 |    1 |    5 |    3 |    4 |
| ('swing', 30)              |    1 |    2 |    3 |    4 |    3 |
| ('swing', 35)              |    1 |    3 |    3 |    6 |    3 |
| ('swing', 40)              |    0 |    3 |    3 |    6 |    3 |
| ('swing', 50)              |    0 |    2 |    3 |    5 |    3 |

## Chosen setting per test election (swing, 35 settlements)

|   test |   param_mu |   param_level |   param_calibration |
|-------:|-----------:|--------------:|--------------------:|
|     22 |      0.003 |           1   |                 nan |
|     23 |      0.003 |           0.3 |                 nan |
|     24 |      0.01  |           0.1 |                 nan |
|     25 |      0.003 |           1   |                 nan |
|     26 |      0.01  |           1   |                 nan |
