# election-estimation

Estimate Israeli Knesset election results from a small sample of ballot boxes.

## Goal

Predict the Knesset seats on election night from a small panel of ballot boxes (at most
2% of the votes), counted as soon as they report. The current model (the **sector ratio
model**, [docs/METHODOLOGY.md](docs/METHODOLOGY.md) section 7) groups the statistical
areas into 12 sectors by how they voted last time, draws a panel of areas in each sector
and counts one box per area. Every area in the country is then predicted from its own
previous result plus the turnout and the proportional change its sector shows in the
panel. Held out on Knesset 22-26, a 2% panel (about 217 boxes) moves 2.2 seats on
average (2 or fewer in 67% of the panels, worst election 2.9), and its 90% seat
intervals hold the true seats of 97% of the lists.

The recommended Knesset 27 panels, their held-out accuracy and an election-night
calculator are in [`reports/knesset_27_panels.html`](reports/knesset_27_panels.html).

## Repository

| Path | Content |
|------|---------|
| [`data/raw/`](data/raw) | Original Elections Committee files, `knesset_<N>_<year>_{ballots,settlements}.csv` |
| [`data/parties/`](data/parties) | Party letter → name table per Knesset |
| [`data/processed/`](data/processed) | Generated tables: CSV per election, Excel workbook, `ballots_long.csv.gz` for all elections |
| [`scripts/build_data.py`](scripts/build_data.py) | Validates raw files and builds `data/processed/` |
| [`scripts/check_excel.py`](scripts/check_excel.py) | Recalculates the workbooks in LibreOffice and checks for formula errors |
| [`scripts/summarize_elections.py`](scripts/summarize_elections.py) | Key facts table per election |
| [`reports/index.html`](reports/index.html) | Results of every election, comparison and averages by party or bloc, party lookup by ballot letters with results per settlement |
| [`reports/`](reports) | One HTML results page per election, `knesset_<N>_<year>.html` |
| [`scripts/build_reports.py`](scripts/build_reports.py) | Builds the HTML reports (run by `build_data.py`) |
| [`scripts/check_reports.js`](scripts/check_reports.js) | Opens the reports in a headless browser and checks them |
| [`data/README.md`](data/README.md) | Columns, checks, data notes |
| [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) | Problem, pitfalls, models, handling changing parties, evaluation |
| [`docs/MODEL_PLAN.md`](docs/MODEL_PLAN.md) | Agreed design of the fixed-panel model and its implementation steps |
| [`src/election_estimation/`](src/election_estimation) | Modelling code: data loading, metrics (L1, Bader-Ofer, blocs), the sector ratio model (`sector.py`), the neural area model (`neural.py`), earlier panel models (`selection.py`, `swing.py`, `recommend.py`) |
| [`reports/knesset_27_panels.html`](reports/knesset_27_panels.html) | Recommended Knesset 27 panels, held-out accuracy, election-night calculator (also reads the committee's per-box file) |
| [`scripts/recommend_sector_panels.py`](scripts/recommend_sector_panels.py), [`scripts/build_panels_site.py`](scripts/build_panels_site.py), [`scripts/check_panels_site.py`](scripts/check_panels_site.py) | Draw the Knesset 27 panels, build the site, check it (JS calculator = Python model) |
| [`scripts/match_k27_boxes.py`](scripts/match_k27_boxes.py) | Links the Knesset 27 polling station list to the areas when it is published |
| [`docs/ELECTION_NIGHT.md`](docs/ELECTION_NIGHT.md), [`scripts/rehearse_election_night.js`](scripts/rehearse_election_night.js) | Election-night checklist and a staged rehearsal of the calculator |
| `scripts/run_sector_*.py`, [`scripts/run_neural.py`](scripts/run_neural.py), [`scripts/diagnose_sector.py`](scripts/diagnose_sector.py) | Held-out experiments of the sector model, its variants, partial counts and the neural model (reports in `reports/*.md`) |
| [`scripts/explore_knesset.py`](scripts/explore_knesset.py) | Per-election exploration and in-sample selection experiment (`PYTHONPATH=src`) |
| [`HANDOFF.md`](HANDOFF.md) | Current status and next steps |
| [`CLAUDE.md`](CLAUDE.md) | Working rules for this project |
| [`.claude/skills/save-usage/`](.claude/skills/save-usage) | Skill for saving Claude usage, with the official limit rules and tips |

## Quick start

```bash
pip install -r requirements.txt
python scripts/build_data.py
```

## Approach in short

1. **Data** - ballot-level results (Knesset 16-26; Knesset 26 provisional), validated and
   unified; statistical areas for Knesset 19-26.
2. **Target** - the total of the regular boxes (double envelopes cannot be sampled).
3. **Earlier panel models** - fixed weighted panels (LP / greedy / MILP), swing and joint
   models: 2.4-3.8 seats moved held out, worst election 5-8.
4. **Sector ratio model** - sectors from past votes, turnout and proportional change per
   sector, Neyman allocation, within-sector bootstrap for intervals and a medoid seat
   point near the threshold: 2.2 seats moved at 2%.
5. **Neural area model** - a learned correction on top of the sector model; no gain held
   out, not used.
6. **Evaluation** - always held out: everything is chosen on the elections before `t`
   and scored on `t`; seats moved (half the seat L1) and share L1.

To build the site after a data change:

```bash
PYTHONPATH=src python scripts/run_sector_heldout.py
PYTHONPATH=src python scripts/recommend_sector_panels.py
PYTHONPATH=src python scripts/build_panels_site.py
PYTHONPATH=src python scripts/check_panels_site.py <screenshot_dir>
```
