# Earlier experiments (archived 2026-11-01)

Reports of the models that came before the sector ratio model (`docs/METHODOLOGY.md`
section 7, `reports/sector_*.md`). Kept for the record; the scripts that wrote them still
run and now write here.

| Report | Script | Content |
|---|---|---|
| `baselines_*.{md,csv}`, `baselines_summary.md` | `run_baselines.py`, `compare_baselines.py` | Random, all-boxes and greedy / MILP baselines per unit |
| `box_matching.md` | `box_matching_report.py` | Matching ballot boxes across elections |
| `budget_curve*/` | `run_budget_curve.py` | Fixed weighted panels of base boxes, 40-160 boxes |
| `regularization_*.{md,csv}` | `run_regularization.py` | Weight prior and recency for the fixed panels |
| `settlement_panel.*`, `oracle_panel.csv` | `run_settlement_panel.py` | Settlement panels and panels chosen in hindsight |
| `swing_panel.*` | `run_swing_panel.py` | Bloc / family swing panels |
| `joint_panel*/` | `run_joint_panel.py` | Level + swing panels |
| `within_panel*/` | `run_within_panel.py` | Within-bloc rows and seat intervals |
| `error_decomposition.md` | `diagnose_errors.py` | Threshold / bloc / within-bloc split of the within-bloc panels' error |
| `knesset_25_exploration.md` | `explore_knesset.py` | In-sample selection on Knesset 25 (illustration) |
| `k27_panels/{settlement,area}_*` | `recommend_panels.py` | The first Knesset 27 panels (swing model), replaced on the site by the sector model |
