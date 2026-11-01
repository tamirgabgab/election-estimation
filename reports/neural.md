# Neural area model vs the sector model, held-out (K22-K26)

`scripts/run_neural.py`: trained on 8 simulated panels per budget of every transition before the test election, 30 epochs, seed 7+t; 100 test panels per budget, both models on the same counted boxes.

|                     |   seats_moved |   within_2 |   share_L1 |   worst_election |
|:--------------------|--------------:|-----------:|-----------:|-----------------:|
| ('ensemble', 0.01)  |         2.996 |      0.4   |      4.246 |             3.9  |
| ('ensemble', 0.015) |         2.558 |      0.58  |      3.525 |             3.77 |
| ('ensemble', 0.02)  |         2.338 |      0.658 |      3.062 |             3.51 |
| ('neural', 0.01)    |         3.03  |      0.39  |      4.332 |             4.41 |
| ('neural', 0.015)   |         2.632 |      0.546 |      3.634 |             4.1  |
| ('neural', 0.02)    |         2.41  |      0.666 |      3.216 |             4.01 |
| ('sector', 0.01)    |         3.008 |      0.404 |      4.326 |             3.57 |
| ('sector', 0.015)   |         2.594 |      0.546 |      3.572 |             3.57 |
| ('sector', 0.02)    |         2.3   |      0.646 |      3.061 |             3.07 |

## Mean seats moved per test

|                     |   22 |   23 |   24 |   25 |   26 |
|:--------------------|-----:|-----:|-----:|-----:|-----:|
| ('ensemble', 0.01)  | 2.41 | 2.1  | 3.46 | 3.9  | 3.11 |
| ('ensemble', 0.015) | 2.03 | 1.76 | 2.77 | 3.77 | 2.46 |
| ('ensemble', 0.02)  | 1.82 | 1.7  | 2.3  | 3.51 | 2.36 |
| ('neural', 0.01)    | 2.38 | 1.9  | 3.46 | 4.41 | 3    |
| ('neural', 0.015)   | 2.14 | 1.64 | 2.85 | 4.1  | 2.43 |
| ('neural', 0.02)    | 1.94 | 1.53 | 2.3  | 4.01 | 2.27 |
| ('sector', 0.01)    | 2.52 | 2.26 | 3.54 | 3.57 | 3.15 |
| ('sector', 0.015)   | 2.04 | 1.9  | 2.86 | 3.57 | 2.6  |
| ('sector', 0.02)    | 1.74 | 1.79 | 2.35 | 3.07 | 2.55 |
