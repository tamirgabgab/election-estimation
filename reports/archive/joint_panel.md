# Joint level + swing settlement panels - target: regular boxes

Held-out test elections 22-26; `k` = settlements, counted in full
(`boxes` = what that costs). One panel and one set of weights give a level and a
swing prediction, mixed as alpha * level + (1 - alpha) * swing. `joint_family`:
lists of a family that ran as one list in both elections get their previous share
plus the panel's swing, other lists the panel's part of their bloc; `joint_bloc`:
blocs split by the panel only. Weights fit past bloc swings (+ family swings),
plus list-share rows scaled by `level`, pulled to size-proportional weights by
`mu`. Grid {'mu': [0.003, 0.01, 0.03], 'level': [0.1, 0.3, 1.0]}, alpha in [0.0, 0.25, 0.5, 0.75, 1.0], chosen by inner validation on
share_L1 (3 folds, 35 settlements). `swing` and
`level_weight_prior`: the earlier separate models (`swing_panel.md`).
`seats_moved` = seat L1 / 2; goal: at most 2 in the mean and the worst
election. Seed 0, decay 0.7.

## Mean over test elections, worst election

|                            |   boxes |   seats_moved |   share_L1 |   max_list_error |   bloc_seat_L1 |   bloc_share_L1 |   threshold_errors |   worst_seats_moved |
|:---------------------------|--------:|--------------:|-----------:|-----------------:|---------------:|----------------:|-------------------:|--------------------:|
| ('joint_bloc', 20)         |   639.2 |           3.8 |       4.5  |             1.16 |            5.6 |            3.03 |                0.4 |                   9 |
| ('joint_bloc', 30)         |   676.6 |           4   |       4.36 |             1.07 |            5.6 |            3.1  |                0.4 |                   9 |
| ('joint_bloc', 35)         |   710.4 |           3.6 |       4.16 |             1.07 |            4.8 |            2.97 |                0.4 |                   9 |
| ('joint_bloc', 40)         |   741.8 |           3.6 |       4.19 |             1.09 |            5.2 |            2.86 |                0.4 |                   9 |
| ('joint_bloc', 50)         |   796.4 |           3.6 |       3.97 |             1.08 |            4.8 |            2.81 |                0.4 |                   9 |
| ('joint_bloc', 70)         |   867.4 |           3   |       3.83 |             0.97 |            4.4 |            2.68 |                0.2 |                   5 |
| ('joint_bloc', 100)        |  1001.6 |           3   |       3.45 |             0.85 |            3.6 |            2.55 |                0.2 |                   5 |
| ('joint_bloc', 150)        |  1116.2 |           2.8 |       3.44 |             0.87 |            4   |            2.7  |                0.2 |                   5 |
| ('joint_family', 20)       |   532.4 |           2.4 |       4.99 |             1.24 |            3.2 |            3.49 |                0   |                   4 |
| ('joint_family', 30)       |   630.4 |           3   |       4.63 |             1.1  |            4.8 |            3.26 |                0.2 |                   5 |
| ('joint_family', 35)       |   645.4 |           3.4 |       4.7  |             1.14 |            4.8 |            3.24 |                0.4 |                   7 |
| ('joint_family', 40)       |   743.8 |           2.8 |       4.32 |             1.14 |            4.4 |            3.31 |                0.2 |                   5 |
| ('joint_family', 50)       |   806.8 |           3   |       4.4  |             1.16 |            4.8 |            3.31 |                0.2 |                   5 |
| ('joint_family', 70)       |   931   |           2.6 |       4.01 |             1.11 |            4.8 |            3.25 |                0.2 |                   5 |
| ('joint_family', 100)      |  1088.6 |           2.4 |       3.81 |             1.15 |            4.4 |            3    |                0.2 |                   5 |
| ('joint_family', 150)      |  1283.4 |           2.6 |       3.49 |             1.02 |            4   |            2.68 |                0.2 |                   5 |
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
| ('joint_bloc', 20)         |    2 |    3 |    2 |    9 |    3 |
| ('joint_bloc', 30)         |    3 |    3 |    2 |    9 |    3 |
| ('joint_bloc', 35)         |    3 |    2 |    1 |    9 |    3 |
| ('joint_bloc', 40)         |    3 |    3 |    1 |    9 |    2 |
| ('joint_bloc', 50)         |    1 |    4 |    2 |    9 |    2 |
| ('joint_bloc', 70)         |    3 |    2 |    3 |    5 |    2 |
| ('joint_bloc', 100)        |    3 |    2 |    3 |    5 |    2 |
| ('joint_bloc', 150)        |    3 |    2 |    2 |    5 |    2 |
| ('joint_family', 20)       |    2 |    1 |    3 |    2 |    4 |
| ('joint_family', 30)       |    2 |    2 |    2 |    5 |    4 |
| ('joint_family', 35)       |    2 |    2 |    2 |    7 |    4 |
| ('joint_family', 40)       |    2 |    2 |    2 |    5 |    3 |
| ('joint_family', 50)       |    2 |    2 |    3 |    5 |    3 |
| ('joint_family', 70)       |    1 |    2 |    3 |    5 |    2 |
| ('joint_family', 100)      |    1 |    1 |    3 |    5 |    2 |
| ('joint_family', 150)      |    1 |    1 |    3 |    5 |    3 |
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

## Chosen setting per test election (35 settlements)

|                      |   param_mu |   param_level |   param_alpha |
|:---------------------|-----------:|--------------:|--------------:|
| ('joint_bloc', 22)   |      0.03  |           0.3 |          1    |
| ('joint_bloc', 23)   |      0.01  |           0.1 |          0.75 |
| ('joint_bloc', 24)   |      0.003 |           0.3 |          0.75 |
| ('joint_bloc', 25)   |      0.003 |           0.3 |          0.75 |
| ('joint_bloc', 26)   |      0.003 |           0.1 |          0.5  |
| ('joint_family', 22) |      0.01  |           0.1 |          0.5  |
| ('joint_family', 23) |      0.01  |           0.1 |          0.25 |
| ('joint_family', 24) |      0.01  |           0.1 |          0.25 |
| ('joint_family', 25) |      0.01  |           1   |          0.25 |
| ('joint_family', 26) |      0.003 |           0.1 |          0    |
