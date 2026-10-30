# Knesset 25 - exploration

## Data checks

- valid_equals_party_sum: True
- voters_equal_valid_plus_invalid: True
- no_turnout_above_100pct: True
- unique_ballot_keys: True

## Overview

- Ballot rows: 12,545 (11,707 regular, 838 double-envelope)
- Split sub-boxes (e.g. 283.1): 7,342
- Settlements: 1,216
- Party lists: 40
- Registered: 6,788,804, voters: 4,794,593, turnout: 70.63%
- Valid: 4,764,742, invalid: 29,851
- Double-envelope valid votes: 458,714 (9.63%)

## National results

|     |     votes |   national_pct |   regular_boxes_pct |   double_envelopes_pct |
|:----|----------:|---------------:|--------------------:|-----------------------:|
| מחל | 1,115,336 |          23.41 |               23.4  |                  23.52 |
| פה  |   847,435 |          17.79 |               17.88 |                  16.93 |
| ט   |   516,470 |          10.84 |               10.35 |                  15.45 |
| כן  |   432,482 |           9.08 |                8.91 |                  10.65 |
| שס  |   392,964 |           8.25 |                8.4  |                   6.84 |
| ג   |   280,194 |           5.88 |                6.11 |                   3.74 |
| ל   |   213,687 |           4.48 |                4.36 |                   5.7  |
| עם  |   194,047 |           4.07 |                4.32 |                   1.75 |
| ום  |   178,735 |           3.75 |                3.97 |                   1.71 |
| אמת |   175,992 |           3.69 |                3.54 |                   5.12 |
| מרצ |   150,793 |           3.16 |                3.17 |                   3.13 |
| ד   |   138,617 |           2.91 |                3.05 |                   1.59 |
| ב   |    56,775 |           1.19 |                1.16 |                   1.48 |
| אצ  |    15,801 |           0.33 |                0.29 |                   0.76 |
| קץ  |    14,694 |           0.31 |                0.32 |                   0.23 |

L1 gap between regular boxes only and the national result: 2.18 percentage points.

## Valid votes per regular box

|       |   valid |
|:------|--------:|
| count |   11707 |
| mean  |     368 |
| std   |      94 |
| min   |      16 |
| 25%   |     304 |
| 50%   |     374 |
| 75%   |     437 |
| max   |     654 |

## Box selection experiment (in-sample)

Features: 13 lists with >= 1% nationally + 'other' (14 dimensions). Loss: L1 distance in percentage points.

### Random boxes, pooled votes (500 trials)

|   boxes |   mean |   p10 |    p90 |
|--------:|-------:|------:|-------:|
|       1 |  86.55 | 45.88 | 164.69 |
|       5 |  46.28 | 29.78 |  67.99 |
|      10 |  32.97 | 20.48 |  46.02 |
|      15 |  26.38 | 16.73 |  37.73 |
|      30 |  18.99 | 12.15 |  27.32 |
|     100 |  10.41 |  6.64 |  15.01 |
|     300 |   6.24 |  3.99 |   8.99 |
|    1000 |   3.82 |  2.56 |   5.22 |
|    3000 |   2.73 |  1.98 |   3.64 |

### Optimized weights: greedy column generation vs MILP

MILP runs on a pool of 513 candidate boxes with a 90s limit.

|   boxes |   greedy_L1 |   milp_L1 | proven_optimal   |
|--------:|------------:|----------:|:-----------------|
|       1 |      23.385 |           |                  |
|       2 |      14.062 |           |                  |
|       3 |       8.44  |     3.718 | False            |
|       4 |       6.066 |           |                  |
|       5 |       4.196 |     1.54  | False            |
|       6 |       2.257 |           |                  |
|       7 |       1.497 |           |                  |
|       8 |       1.03  |     0.172 | False            |
|       9 |       0.353 |           |                  |
|      10 |       0.192 |           |                  |
|      11 |       0.007 |           |                  |
|      12 |       0.002 |           |                  |
|      13 |       0.001 |           |                  |
|      14 |       0     |           |                  |

### The 14 boxes that reproduce the national result

|       | settlement_name   |   ballot_id |   valid |   weight_pct |   L1_to_national |
|------:|:------------------|------------:|--------:|-------------:|-----------------:|
|  8284 | נתניה             |       230.5 |     408 |        40.55 |            52.38 |
|  5121 | ירושלים           |       816.3 |     379 |        25.75 |            23.38 |
|  8548 | סחנין             |        27.3 |     409 |        10.06 |           176.58 |
|  5599 | כפר חרוב          |         1   |     268 |         7.42 |            98.83 |
|  4537 | יד בנימין         |         2   |     468 |         5.28 |           129.56 |
|  4240 | טבריה             |        57   |     590 |         4.53 |           165.3  |
|   345 | איבים             |         1   |      65 |         2.21 |            98.75 |
|  9045 | פלך               |         1   |      97 |         1.3  |           148.45 |
|  3748 | חיפה              |       343.2 |     408 |         1.3  |           148.53 |
|  2740 | גני טל            |         1   |     379 |         1.2  |           110.15 |
|  2861 | דייר חנא          |        10.3 |     353 |         0.38 |           171.74 |
| 12542 | תראבין אצאנע שבט  |         1   |      72 |         0.01 |           139.48 |
|  8495 | סאגור             |         2   |     364 |         0.01 |           128.36 |
|  2638 | גדיש              |         1   |     209 |         0.01 |           104.48 |
