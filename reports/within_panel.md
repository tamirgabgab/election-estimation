# Joint panels with within-bloc rows and seat intervals - target: regular boxes

Held-out test elections 22-26; `k` = settlements, counted in full.
`joint_within`: `joint_family` (see `joint_panel.md`) plus rows asking the panel to
reproduce the split of every bloc into its lists. Grid
{'mu': [0.003, 0.01, 0.03], 'level': [0.1, 0.3, 1.0], 'within': [0.3, 1.0]}, alpha in [0.0, 0.25, 0.5, 0.75, 1.0], chosen by inner validation on share_L1
(3 folds, 35 settlements). Seed 0, decay 0.7.

Seat intervals: 90% central intervals from 1000 simulations of the
panel's own standardized errors in the inner validation folds, separately for
continuing and new lists. `interval_moved` = half the seats by which the true
result lies outside the intervals; `coverage` = share of lists (>= 1%) whose true
seats are inside; `width` = mean interval width. Goal for the point prediction:
at most 2 seats moved in the mean and the worst election.

## Mean over test elections, worst election

|                       |   boxes |   seats_moved |   share_L1 |   max_list_error |   threshold_errors |   interval_moved |   coverage |   width |   worst_seats_moved |   worst_interval_moved |
|:----------------------|--------:|--------------:|-----------:|-----------------:|-------------------:|-----------------:|-----------:|--------:|--------------------:|-----------------------:|
| ('joint_family', 20)  |   532.4 |           2.4 |       4.99 |             1.24 |                0   |            nan   |     nan    |  nan    |                   4 |                  nan   |
| ('joint_family', 30)  |   630.4 |           3   |       4.63 |             1.1  |                0.2 |            nan   |     nan    |  nan    |                   5 |                  nan   |
| ('joint_family', 35)  |   645.4 |           3.4 |       4.7  |             1.14 |                0.4 |            nan   |     nan    |  nan    |                   7 |                  nan   |
| ('joint_family', 40)  |   743.8 |           2.8 |       4.32 |             1.14 |                0.2 |            nan   |     nan    |  nan    |                   5 |                  nan   |
| ('joint_family', 50)  |   806.8 |           3   |       4.4  |             1.16 |                0.2 |            nan   |     nan    |  nan    |                   5 |                  nan   |
| ('joint_family', 70)  |   931   |           2.6 |       4.01 |             1.11 |                0.2 |            nan   |     nan    |  nan    |                   5 |                  nan   |
| ('joint_family', 100) |  1088.6 |           2.4 |       3.81 |             1.15 |                0.2 |            nan   |     nan    |  nan    |                   5 |                  nan   |
| ('joint_family', 150) |  1283.4 |           2.6 |       3.49 |             1.02 |                0.2 |            nan   |     nan    |  nan    |                   5 |                  nan   |
| ('joint_within', 20)  |   464   |           3.4 |       4.6  |             1.18 |                0.2 |              0.8 |       0.93 |    1.86 |                   6 |                    2   |
| ('joint_within', 30)  |   573.2 |           3.2 |       4.09 |             1.1  |                0.2 |              0.2 |       0.98 |    1.8  |                   5 |                    1   |
| ('joint_within', 35)  |   607.8 |           3.2 |       4.49 |             1.1  |                0.2 |              0.1 |       0.98 |    1.88 |                   5 |                    0.5 |
| ('joint_within', 40)  |   637   |           3.2 |       4.45 |             1.11 |                0.2 |              0.2 |       0.97 |    1.75 |                   5 |                    0.5 |
| ('joint_within', 50)  |   798.6 |           3.2 |       4.57 |             1.13 |                0.2 |              0.3 |       0.95 |    1.83 |                   5 |                    0.5 |
| ('joint_within', 70)  |   908.4 |           2.8 |       4.39 |             1.22 |                0.2 |              0.2 |       0.97 |    1.85 |                   5 |                    0.5 |
| ('joint_within', 100) |  1171   |           2.6 |       4.12 |             1.05 |                0.2 |              0.2 |       0.97 |    1.8  |                   5 |                    0.5 |
| ('joint_within', 150) |  1863.6 |           2.8 |       3.63 |             1.05 |                0.2 |              0.1 |       0.98 |    1.88 |                   5 |                    0.5 |

## Seats moved per test election

|                       |   22 |   23 |   24 |   25 |   26 |
|:----------------------|-----:|-----:|-----:|-----:|-----:|
| ('joint_family', 20)  |    2 |    1 |    3 |    2 |    4 |
| ('joint_family', 30)  |    2 |    2 |    2 |    5 |    4 |
| ('joint_family', 35)  |    2 |    2 |    2 |    7 |    4 |
| ('joint_family', 40)  |    2 |    2 |    2 |    5 |    3 |
| ('joint_family', 50)  |    2 |    2 |    3 |    5 |    3 |
| ('joint_family', 70)  |    1 |    2 |    3 |    5 |    2 |
| ('joint_family', 100) |    1 |    1 |    3 |    5 |    2 |
| ('joint_family', 150) |    1 |    1 |    3 |    5 |    3 |
| ('joint_within', 20)  |    2 |    2 |    3 |    6 |    4 |
| ('joint_within', 30)  |    1 |    2 |    4 |    5 |    4 |
| ('joint_within', 35)  |    1 |    2 |    5 |    5 |    3 |
| ('joint_within', 40)  |    2 |    1 |    4 |    5 |    4 |
| ('joint_within', 50)  |    2 |    1 |    4 |    5 |    4 |
| ('joint_within', 70)  |    1 |    1 |    3 |    5 |    4 |
| ('joint_within', 100) |    1 |    2 |    3 |    5 |    2 |
| ('joint_within', 150) |    2 |    1 |    3 |    5 |    3 |

## Chosen setting and error scales per test election (35 settlements)

|   test |   param_mu |   param_level |   param_within |   param_alpha |   error_continuing |   error_new |
|-------:|-----------:|--------------:|---------------:|--------------:|-------------------:|------------:|
|     22 |      0.01  |           0.3 |              1 |          0    |              0.014 |       0.019 |
|     23 |      0.003 |           0.1 |              1 |          0.5  |              0.015 |       0.018 |
|     24 |      0.003 |           0.1 |              1 |          0.5  |              0.01  |       0.021 |
|     25 |      0.003 |           0.1 |              1 |          0.5  |              0.013 |       0.016 |
|     26 |      0.01  |           0.3 |              1 |          0.25 |              0.013 |       0.019 |

## Lists with an uncertain threshold (35 settlements, 5% < P(pass) < 95%)

|   test | letter   |   share |   true_share |   p_pass |   seats |   low |   high |   true_seats |
|-------:|:---------|--------:|-------------:|---------:|--------:|------:|-------:|-------------:|
|     25 | אמת      |   0.036 |        0.035 |    0.931 |       4 |     0 |      5 |            4 |
|     25 | ד        |   0.037 |        0.03  |    0.916 |       4 |     0 |      5 |            0 |
|     25 | ום       |   0.038 |        0.04  |    0.933 |       5 |     0 |      5 |            5 |
