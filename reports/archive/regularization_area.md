# Weight regularization - unit: area

Held-out test elections 22-26; panels under a box budget `k`, whole
units counted. Each regularization's strength is chosen per test election by inner
validation (the last 2 training elections, each predicted from the ones
before it, at 50 boxes, lowest seat L1). Seed 0, recency decay 0.7,
20 greedy candidates per step, grids {'weight_prior': {'mu': [0.003, 0.01, 0.03]}, 'calibration': {'calibration': [0.3, 1.0]}, 'noise': {'noise': [0.1, 0.3]}}.

- `weight_prior`: L1 pull of the weights towards size-proportional weights (`mu`).
- `calibration`: extra targets per bloc-profile stratum (`calibration` = their weight).
- `noise`: perturbed copies of the training elections (`noise` = log-normal sigma).

## Mean over test elections

|                       |   boxes |   seat_L1 |   share_L1 |   bloc_seat_L1 |   bloc_share_L1 |   threshold_errors |
|:----------------------|--------:|----------:|-----------:|---------------:|----------------:|-------------------:|
| (35, 'calibration')   |    33.8 |      14   |       8.98 |            9.6 |            6.4  |                0.8 |
| (35, 'greedy_budget') |    36.4 |      15.2 |      10.27 |           11.2 |            6.79 |                0.6 |
| (35, 'noise')         |    37.6 |      14   |      10.38 |           10.4 |            7.43 |                0.4 |
| (35, 'weight_prior')  |    36   |      12.4 |       8.55 |            7.2 |            4.5  |                0.4 |
| (50, 'calibration')   |    50.6 |      11.6 |       9.04 |            6.8 |            6.36 |                0.2 |
| (50, 'greedy_budget') |    52   |      14.8 |      10.31 |           10.4 |            6.68 |                0.8 |
| (50, 'noise')         |    53.2 |      15.6 |      10.22 |           11.2 |            7.56 |                1   |
| (50, 'weight_prior')  |    51.2 |      14   |       9.06 |            7.6 |            5.34 |                0.8 |
| (70, 'calibration')   |    70.8 |      11.2 |       8.22 |            8   |            5.73 |                0.2 |
| (70, 'greedy_budget') |    70.4 |      18   |      11.05 |           12   |            6.69 |                1.2 |
| (70, 'noise')         |    73.4 |      14.4 |       9.87 |           10   |            6.71 |                1   |
| (70, 'weight_prior')  |    70.6 |      18   |      10.02 |           10.4 |            6.17 |                1.4 |

## Chosen strength per test election (at 50 boxes)

|                      |   param_mu |   param_calibration |   param_noise |
|:---------------------|-----------:|--------------------:|--------------:|
| ('weight_prior', 22) |      0.003 |               nan   |         nan   |
| ('calibration', 22)  |    nan     |                 1   |         nan   |
| ('noise', 22)        |    nan     |               nan   |           0.3 |
| ('weight_prior', 23) |      0.003 |               nan   |         nan   |
| ('calibration', 23)  |    nan     |                 1   |         nan   |
| ('noise', 23)        |    nan     |               nan   |           0.1 |
| ('weight_prior', 24) |      0.03  |               nan   |         nan   |
| ('calibration', 24)  |    nan     |                 1   |         nan   |
| ('noise', 24)        |    nan     |               nan   |           0.1 |
| ('weight_prior', 25) |      0.01  |               nan   |         nan   |
| ('calibration', 25)  |    nan     |                 1   |         nan   |
| ('noise', 25)        |    nan     |               nan   |           0.1 |
| ('weight_prior', 26) |      0.01  |               nan   |         nan   |
| ('calibration', 26)  |    nan     |                 0.3 |         nan   |
| ('noise', 26)        |    nan     |               nan   |           0.1 |
