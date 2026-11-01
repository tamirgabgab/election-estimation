# Weight regularization - unit: base_box

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
| (35, 'calibration')   |    33.6 |      12.8 |      10.42 |           10.4 |            7.04 |                0.2 |
| (35, 'greedy_budget') |    37.4 |       8.8 |       7.37 |            5.6 |            3.71 |                0   |
| (35, 'noise')         |    36.8 |      18.8 |      12.79 |           12.8 |            8.61 |                0.8 |
| (35, 'weight_prior')  |    38.2 |      11.6 |       9.14 |            6.8 |            5.18 |                0   |
| (50, 'calibration')   |    46.8 |      10.8 |       9.16 |            8.8 |            6.18 |                0.2 |
| (50, 'greedy_budget') |    53.4 |       8.4 |       7.67 |            6.8 |            4.71 |                0   |
| (50, 'noise')         |    51.4 |      13.6 |       9.97 |            8.4 |            6.7  |                0.4 |
| (50, 'weight_prior')  |    54.8 |      10.4 |       7.89 |            6.4 |            4.78 |                0   |
| (70, 'calibration')   |    67.2 |      12.4 |       9.65 |           10.4 |            7.01 |                0.2 |
| (70, 'greedy_budget') |    75.2 |       9.6 |       8.36 |            8   |            5.76 |                0   |
| (70, 'noise')         |    70.4 |      10   |       8.22 |            6.4 |            5.12 |                0.2 |
| (70, 'weight_prior')  |    73.6 |       9.6 |       7.56 |            6   |            4.7  |                0   |

## Chosen strength per test election (at 50 boxes)

|                      |   param_mu |   param_calibration |   param_noise |
|:---------------------|-----------:|--------------------:|--------------:|
| ('weight_prior', 22) |       0.03 |               nan   |         nan   |
| ('calibration', 22)  |     nan    |                 1   |         nan   |
| ('noise', 22)        |     nan    |               nan   |           0.1 |
| ('weight_prior', 23) |       0.03 |               nan   |         nan   |
| ('calibration', 23)  |     nan    |                 1   |         nan   |
| ('noise', 23)        |     nan    |               nan   |           0.3 |
| ('weight_prior', 24) |       0.03 |               nan   |         nan   |
| ('calibration', 24)  |     nan    |                 1   |         nan   |
| ('noise', 24)        |     nan    |               nan   |           0.3 |
| ('weight_prior', 25) |       0.01 |               nan   |         nan   |
| ('calibration', 25)  |     nan    |                 1   |         nan   |
| ('noise', 25)        |     nan    |               nan   |           0.1 |
| ('weight_prior', 26) |       0.01 |               nan   |         nan   |
| ('calibration', 26)  |     nan    |                 0.3 |         nan   |
| ('noise', 26)        |     nan    |               nan   |           0.3 |
