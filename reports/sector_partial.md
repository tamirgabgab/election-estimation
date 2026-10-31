# Sector model with part of the panel counted (held-out, 2% budget)

`scripts/run_sector_partial.py`: 100 panels per test, seed 5+t, one random box per area. `missing`: a sector with no counted area keeps its previous result (`prev`) or takes the turnout and change of all counted areas (`pooled`).

|                         |   counted |   seats_moved |   within_2 |   worst_election |
|:------------------------|----------:|--------------:|-----------:|-----------------:|
| ('full', 'pooled')      |     1     |         2.418 |      0.618 |             3.49 |
| ('full', 'prev')        |     1     |         2.418 |      0.618 |             3.49 |
| ('random_90', 'pooled') |     0.901 |         2.524 |      0.564 |             3.61 |
| ('random_90', 'prev')   |     0.901 |         2.524 |      0.564 |             3.61 |
| ('random_70', 'pooled') |     0.7   |         2.91  |      0.448 |             3.94 |
| ('random_70', 'prev')   |     0.7   |         2.91  |      0.448 |             3.94 |
| ('random_50', 'pooled') |     0.499 |         3.366 |      0.328 |             4.52 |
| ('random_50', 'prev')   |     0.499 |         3.362 |      0.332 |             4.52 |
| ('arab_late', 'pooled') |     0.864 |         9.428 |      0.008 |            13.1  |
| ('arab_late', 'prev')   |     0.864 |        10.132 |      0.034 |            14.25 |
| ('arab_half', 'pooled') |     0.932 |         2.666 |      0.556 |             3.91 |
| ('arab_half', 'prev')   |     0.932 |         2.666 |      0.556 |             3.91 |

## Mean seats moved per test

|                         |    22 |   23 |    24 |   25 |    26 |
|:------------------------|------:|-----:|------:|-----:|------:|
| ('full', 'pooled')      |  2.04 | 1.69 |  2.43 | 3.49 |  2.44 |
| ('full', 'prev')        |  2.04 | 1.69 |  2.43 | 3.49 |  2.44 |
| ('random_90', 'pooled') |  2.01 | 1.82 |  2.6  | 3.61 |  2.58 |
| ('random_90', 'prev')   |  2.01 | 1.82 |  2.6  | 3.61 |  2.58 |
| ('random_70', 'pooled') |  2.39 | 1.99 |  3.32 | 3.94 |  2.91 |
| ('random_70', 'prev')   |  2.39 | 1.99 |  3.32 | 3.94 |  2.91 |
| ('random_50', 'pooled') |  2.87 | 2.41 |  3.83 | 4.52 |  3.2  |
| ('random_50', 'prev')   |  2.87 | 2.41 |  3.82 | 4.52 |  3.19 |
| ('arab_late', 'pooled') | 12.46 | 3.79 | 11.02 | 6.77 | 13.1  |
| ('arab_late', 'prev')   | 12.97 | 3.2  | 14.25 | 6.22 | 14.02 |
| ('arab_half', 'pooled') |  2.06 | 1.86 |  2.89 | 3.91 |  2.61 |
| ('arab_half', 'prev')   |  2.06 | 1.86 |  2.89 | 3.91 |  2.61 |
