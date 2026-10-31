# Sector model: point under the threshold and seat intervals (K22-K26)

`scripts/run_sector_intervals.py`: 20 panels per test and budget (sector_neyman), 200 within-sector bootstrap replicates, seed 1+t. `direct` / `medoid`: seats moved of the point; `*_2`: share of panels within 2 seats; `coverage`: lists whose true seats are inside the 90% interval; `outside`: seats moved outside it; `brier`: sum over lists of the P(pass) squared error.

|   budget |   direct |   medoid |   coverage |   outside |   width |   brier |   direct_2 |   medoid_2 |
|---------:|---------:|---------:|-----------:|----------:|--------:|--------:|-----------:|-----------:|
|    0.015 |     2.76 |     2.77 |      0.961 |     0.194 |   1.965 |   0.079 |       0.49 |       0.49 |
|    0.02  |     2.44 |     2.37 |      0.969 |     0.159 |   1.785 |   0.056 |       0.58 |       0.64 |

## Per test

|             |   direct |   medoid |   coverage |   outside |
|:------------|---------:|---------:|-----------:|----------:|
| (0.015, 22) |     2.55 |     2.5  |       0.93 |      0.32 |
| (0.015, 23) |     1.85 |     1.75 |       0.94 |      0.22 |
| (0.015, 24) |     3.1  |     3.25 |       0.99 |      0.08 |
| (0.015, 25) |     3.15 |     3.25 |       0.97 |      0.15 |
| (0.015, 26) |     3.15 |     3.1  |       0.96 |      0.2  |
| (0.02, 22)  |     2.25 |     2.25 |       0.99 |      0.05 |
| (0.02, 23)  |     1.9  |     1.95 |       0.94 |      0.22 |
| (0.02, 24)  |     2.55 |     2.7  |       0.98 |      0.12 |
| (0.02, 25)  |     2.95 |     2.35 |       0.98 |      0.12 |
| (0.02, 26)  |     2.55 |     2.6  |       0.95 |      0.27 |
