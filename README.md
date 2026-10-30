# election-estimation
Estimating Israeli Knesset election results from a small sample of ballot boxes.

## Goal

Pick a minimal set of ballot boxes (or settlements) whose results, combined by a model,
estimate the final national result with a small L1 error. A regularization term
penalizes the number of sampled ballot boxes.

## Data

See [data/README.md](data/README.md). Build the processed tables with:

```bash
pip install -r requirements.txt
python scripts/build_data.py
```
