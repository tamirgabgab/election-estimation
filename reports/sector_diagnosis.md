# Sector model: where the error comes from (held-out, 2% budget)

`scripts/diagnose_sector.py`, 50 panels per test, seed 3+t. Seats moved of: `census` (every area read in full: the model's bias without sampling), `bias` (the mean prediction over the panels), `area_mean` (the panels read through each area's mean box: no single-box noise) and `single_box` (election night). `within_2`: share of panels within 2 seats.

|   test |   census |   bias |   area_mean |   single_box |   within_2 |
|-------:|---------:|-------:|------------:|-------------:|-----------:|
|     22 |        0 |      0 |        1.24 |         1.96 |       0.8  |
|     23 |        0 |      1 |        1.18 |         1.66 |       0.88 |
|     24 |        0 |      0 |        1.8  |         2.46 |       0.48 |
|     25 |        0 |      0 |        2.74 |         3.54 |       0.42 |
|     26 |        1 |      1 |        2.1  |         2.38 |       0.58 |

Mean: {'census': 0.2, 'bias': 0.4, 'area_mean': 1.81, 'single_box': 2.4, 'within_2': 0.63}

## Share of the squared error (seat units) by sector

|                   |   share |
|:------------------|--------:|
| right_pure        |   0.245 |
| center_left_pure  |   0.21  |
| arab_pure         |   0.164 |
| right_mixed       |   0.125 |
| center_left_mixed |   0.121 |
| haredi_pure       |   0.094 |
| small             |   0.041 |

## Lists with the largest share of the squared error

|                     |   share |
|:--------------------|--------:|
| הרשימה המשותפת (22) |   0.061 |
| הליכוד (26)         |   0.054 |
| כחול לבן (22)       |   0.049 |
| הרשימה המשותפת (26) |   0.048 |
| הציונות הדתית (24)  |   0.044 |
| ימינה (22)          |   0.042 |
| יש עתיד (24)        |   0.031 |
| כחול לבן (23)       |   0.03  |
| הליכוד (24)         |   0.027 |
| יש עתיד (25)        |   0.026 |
| הליכוד (22)         |   0.025 |
| הליכוד (25)         |   0.024 |
