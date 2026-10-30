# election-estimation

Estimate Israeli Knesset election results from a small sample of ballot boxes.

## Goal

Choose the smallest set of ballot boxes whose weighted results reproduce the final
national result:

```
min  || y - Σ_{i∈S} w_i · x_i ||_1  +  λ · |S|
```

L1 error on party shares, plus a penalty `λ` on the number of sampled boxes.
The selection is learned on past elections and tested on the next one.
Full write-up: [docs/METHODOLOGY.md](docs/METHODOLOGY.md).

## Repository

| Path | Content |
|------|---------|
| [`data/raw/`](data/raw) | Original Elections Committee files, `knesset_<N>_<year>_{ballots,settlements}.csv` |
| [`data/parties/`](data/parties) | Party letter → name table per Knesset |
| [`data/processed/`](data/processed) | Generated tables: CSV per election, Excel workbook, `ballots_long.csv.gz` for all elections |
| [`scripts/build_data.py`](scripts/build_data.py) | Validates raw files and builds `data/processed/` |
| [`scripts/check_excel.py`](scripts/check_excel.py) | Recalculates the workbooks in LibreOffice and checks for formula errors |
| [`scripts/summarize_elections.py`](scripts/summarize_elections.py) | Key facts table per election |
| [`reports/index.html`](reports/index.html) | Results of every election, comparison and averages by party or bloc |
| [`reports/`](reports) | One HTML results page per election, `knesset_<N>_<year>.html` |
| [`scripts/build_reports.py`](scripts/build_reports.py) | Builds the HTML reports (run by `build_data.py`) |
| [`scripts/check_reports.js`](scripts/check_reports.js) | Opens the reports in a headless browser and checks them |
| [`data/README.md`](data/README.md) | Columns, checks, data notes |
| [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) | Problem, pitfalls, models, handling changing parties, evaluation |
| [`HANDOFF.md`](HANDOFF.md) | Current status and next steps |
| [`CLAUDE.md`](CLAUDE.md) | Working rules for this project |

## Quick start

```bash
pip install -r requirements.txt
python scripts/build_data.py
```

## Approach in short

1. **Data** - ballot-level results (now Knesset 21-25, target 16-26), validated and unified.
2. **Baselines** - random sample, MILP / greedy selection of boxes.
3. **Swing model** - predict the change from the previous election.
4. **Neural model** - learnable per-box gates with an L0 (Hard-Concrete) penalty.
5. **Evaluation** - train on election `t`, test on `t+1`; L1 on shares and seat error.
