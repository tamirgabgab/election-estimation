# Base ballot box matching across elections

Base box key: `<settlement_code>_<base number>`; sub-boxes (`283.1`, `283.2`) are
merged into `283`, and Knesset 16-17 ids are divided by ten. Double envelopes are
excluded.

## Base boxes per election

|    |   base_boxes |   split_base_boxes |   registered_per_base_box |
|---:|-------------:|-------------------:|--------------------------:|
| 16 |         7726 |                 10 |                       611 |
| 17 |         8237 |                 40 |                       608 |
| 18 |         9260 |                  3 |                       570 |
| 19 |         9879 |                  2 |                       573 |
| 20 |        10061 |                 58 |                       585 |
| 21 |         9243 |                346 |                       686 |
| 22 |         9198 |                384 |                       695 |
| 23 |         9388 |                341 |                       687 |
| 24 |         5614 |               2329 |                      1172 |
| 25 |         6306 |               1925 |                      1077 |
| 26 |         8690 |               1021 |                       844 |

## Consecutive elections

- `box_survival`, `vote_survival`: % of base boxes / valid votes of the earlier
  election whose key exists in the later one.
- `settlement_vote_survival`: the same at settlement level.
- `median_abs_log_ratio`, `within_25pct`: registered-voter drift of matched boxes.
- `matched_L1_median` vs `decoy_L1_median`: bloc-share L1 distance (pp, after removing
  the national bloc swing) between a box and its namesake, and between the box and a
  random other box of the same settlement. `matched_closer`: % of matched pairs closer
  than their decoy.

|          |   boxes |   box_survival |   vote_survival |   settlement_vote_survival |   median_abs_log_ratio |   within_25pct |   pairs |   matched_L1_median |   decoy_L1_median |   matched_closer |
|:---------|--------:|---------------:|----------------:|---------------------------:|-----------------------:|---------------:|--------:|--------------------:|------------------:|-----------------:|
| (16, 17) |    7726 |          98.89 |           99    |                      99.09 |                   0.05 |          91.7  |    6761 |               20.62 |             37.26 |            77.47 |
| (17, 18) |    8237 |          99.76 |           99.87 |                      99.89 |                   0.06 |          86.04 |    7466 |               18.61 |             35.65 |            79.25 |
| (18, 19) |    9260 |          99.2  |           99.37 |                     100    |                   0.05 |          91.3  |    8431 |               12.88 |             30.36 |            82.03 |
| (19, 20) |    9879 |          99.69 |           99.85 |                     100    |                   0.04 |          95.82 |    9079 |               17.96 |             33.18 |            80.03 |
| (20, 21) |   10061 |          87.05 |           87.45 |                     100    |                   0.06 |          88.32 |    7965 |               15.72 |             31.36 |            79.97 |
| (21, 22) |    9243 |          96.78 |           96.58 |                     100    |                   0.01 |          97.76 |    8136 |               13.05 |             30.17 |            84.3  |
| (22, 23) |    9198 |          97.28 |           96.87 |                     100    |                   0.01 |          97.11 |    8139 |                8.33 |             26.44 |            88.03 |
| (23, 24) |    9388 |          56.22 |           55.86 |                      99.99 |                   0.03 |          67.28 |    4426 |               11.92 |             27.2  |            82.26 |
| (24, 25) |    5614 |          81.97 |           73.67 |                      99.9  |                   0.03 |          84.68 |    3790 |               10.35 |             25.23 |            82.51 |
| (25, 26) |    6306 |          86.81 |           84.13 |                     100    |                   0.08 |          73.38 |    4701 |               22.22 |             30.42 |            73.9  |

## Survival matrix

Row t, column s: % of the valid votes of election t cast in base boxes whose key also
exists in election s.

|    |   16 |   17 |   18 |   19 |   20 |   21 |   22 |   23 |   24 |   25 |   26 |
|---:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|
| 16 |  100 |   99 |   99 |   99 |   99 |   86 |   85 |   86 |   48 |   54 |   71 |
| 17 |   93 |  100 |  100 |   99 |   99 |   86 |   85 |   86 |   48 |   54 |   71 |
| 18 |   83 |   90 |  100 |   99 |   99 |   86 |   85 |   86 |   48 |   54 |   71 |
| 19 |   77 |   83 |   93 |  100 |  100 |   87 |   86 |   87 |   48 |   54 |   71 |
| 20 |   75 |   81 |   91 |   98 |  100 |   87 |   86 |   87 |   48 |   54 |   72 |
| 21 |   71 |   76 |   86 |   93 |   95 |  100 |   97 |   96 |   56 |   60 |   76 |
| 22 |   70 |   75 |   85 |   92 |   94 |   97 |  100 |   97 |   56 |   60 |   77 |
| 23 |   69 |   74 |   84 |   91 |   93 |   95 |   95 |  100 |   56 |   60 |   77 |
| 24 |   64 |   69 |   78 |   86 |   89 |   90 |   90 |   93 |  100 |   74 |   80 |
| 25 |   62 |   67 |   77 |   85 |   87 |   87 |   87 |   89 |   67 |  100 |   84 |
| 26 |   62 |   66 |   75 |   81 |   83 |   81 |   80 |   82 |   52 |   62 |  100 |

## Fixed panel used in Knesset 25

Base boxes that exist in every election from `train_from` to the target, and the
share of the target's valid votes they hold.

|   train_from |   elections_in_window |   common_boxes |   target_vote_share |
|-------------:|----------------------:|---------------:|--------------------:|
|           16 |                    10 |           3192 |               0.418 |
|           17 |                     9 |           3381 |               0.449 |
|           18 |                     8 |           3767 |               0.51  |
|           19 |                     7 |           4020 |               0.562 |
|           20 |                     6 |           4090 |               0.577 |
|           21 |                     5 |           4279 |               0.61  |
|           22 |                     4 |           4327 |               0.619 |
|           23 |                     3 |           4414 |               0.639 |
|           24 |                     2 |           4602 |               0.667 |

## Fixed panel used in Knesset 26

Base boxes that exist in every election from `train_from` to the target, and the
share of the target's valid votes they hold.

|   train_from |   elections_in_window |   common_boxes |   target_vote_share |
|-------------:|----------------------:|---------------:|--------------------:|
|           16 |                    11 |           2948 |               0.311 |
|           17 |                    10 |           3112 |               0.331 |
|           18 |                     9 |           3456 |               0.37  |
|           19 |                     8 |           3679 |               0.396 |
|           20 |                     7 |           3741 |               0.404 |
|           21 |                     6 |           3896 |               0.42  |
|           22 |                     5 |           3930 |               0.423 |
|           23 |                     4 |           4001 |               0.433 |
|           24 |                     3 |           4139 |               0.447 |
|           25 |                     2 |           5474 |               0.619 |
