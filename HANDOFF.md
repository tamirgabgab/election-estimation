# Handoff

Last updated: 2026-10-30. Branch: `main` (merged from `claude/stoic-tesla-h2fa2d` and `claude/peaceful-cerf-knn9rl`).

## Goal

A statistical model that selects a minimal number of sample ballot boxes and estimates
the national result with minimal L1 error, with a regularization penalty `λ` on the
number of boxes. Details in [docs/METHODOLOGY.md](docs/METHODOLOGY.md).

## Done

- **Election data** in `data/raw/`, byte-identical to the committee's files:
  Knesset 16 (2003): `harelc/elections-vote-transfer` `ballot16.csv` (committee layout,
  regular boxes only); the envelopes row is official totals minus the regular boxes,
  from `data/official/knesset_16_totals.csv` (see D12),
  Knesset 17 (2006) and 18 (2009): one ballots file each from the Yoavfried/Israel-Elections-Map
  project (`public-data/v1/ballots/k17.csv`, `k18.csv`; envelopes included, totals equal the
  official ones; settlements are summed from the ballots),
  Knesset 19 (2013, `expbkalpi`/`expcity`, UTF-8, older column layout),
  Knesset 20 (2015, `expbkal20`/`expc-5`, UTF-8 / Windows-1255, older column layout),
  Knesset 21 (2019-04, `expb_5`/`expc_5`, Windows-1255, older column layout),
  Knesset 22 (2019-09, `expb_4`/`expc_4`, Windows-1255),
  Knesset 23 (2020, `expb_3`/`expc_3`, Windows-1255), Knesset 24 (2021, `expb_2`/`expc_2`,
  Windows-1255), Knesset 25 (2022, `expb_1`/`expc_1`, UTF-8) and Knesset 26 (2026,
  `expb`/`expc`, UTF-8, **provisional**: downloaded before the certified final results).
- **Build pipeline** `scripts/build_data.py`:
  - validates `voters = invalid + valid`, party sums = `valid`, unique ballot ids,
    and ballots summed per settlement = settlements file;
  - reads UTF-8 and Windows-1255 files, drops empty trailing columns;
  - for Knesset 16, adds the envelopes row with `add_envelopes_from_official`; read_raw
    skips its trailing DOS end-of-file row and its "0.0" counts;
  - reads the Yoavfried schema for Knesset 17-18 (`read_yoavfried`): envelope rows by
    `is_envelope`, their registered voters set to 0 (the project copies actual voters there
    in K18); settlements summed with `settlements_from_ballots`;
  - accepts the Knesset 19-21 layout (`מספר קלפי`, no committee / ברזל / ריכוז / שופט
    columns, which stay empty);
  - Knesset 20 publishes split boxes under one number (58 pairs); their `ballot_key`
    gets `-1` / `-2` in file order;
  - standardizes column names to English, keeps `ballot_id` as text;
  - normalizes the double-envelopes row to code 9999 (raw: 99999 in Knesset 21; 875 in
    the Knesset 20 ballots file and 0 with no name in its settlements file), flags it with
    `is_envelopes`, and asserts exactly one envelopes row per election; the Knesset 19
    settlements file has no envelopes row (its totals are regular votes only), so the row
    is summed from the ballots file (code 875 there);
  - computes national shares and seats (threshold + Bader-Ofer with surplus
    agreements), reproducing the official result of all eleven elections (Knesset 26 against the final seats reported in the press);
  - writes per-election CSVs, an Excel workbook with tables and formulas (checked
    in LibreOffice, no errors), and `ballots_long.csv.gz` for all elections.
- **Party tables** `data/parties/knesset_{16..26}_parties.csv`: lists that passed the
  threshold are named and have a `family` and a `bloc` (right, haredi, center-left, arab);
  small lists are marked `verified = no`, bloc `other`. `leader_he` = #1 on the list for
  all 124 lists that passed the threshold, found by web search (search snippets only;
  wikipedia / gov.il are blocked here), with source URL, confidence (74 high, 50 medium)
  and notes in `data/parties/leaders_sources.csv` (see D17).
- **HTML reports** in `reports/` (built by `scripts/build_reports.py`): one results page
  per election (seats, vote shares, threshold pass/fail, blocs) and `index.html` with an
  election selector, a comparison tab averaging seats or shares by bloc or party, and a
  party lookup tab: ballot letters (`מחל`), party name or list leader → every election
  the party family ran in (letters, name, #1, votes, share, threshold, seats), other lists
  with the same letters, and share or votes per settlement in every election.
  Checked with `scripts/check_reports.js` (desktop and mobile, no errors).
- **Check scripts**: `scripts/check_excel.py` (LibreOffice recalculation, 0 errors in all
  workbooks) and `scripts/summarize_elections.py` (facts table below).
- **Procedure** for adding an election is fixed in `CLAUDE.md`.
- **Merged with the modelling branch** (2026-10-30): `docs/MODEL_PLAN.md` (agreed model
  design), `src/election_estimation/` (`data.py` loads the processed tables and adds
  base boxes; `metrics.py` L1, Bader-Ofer, soft seats, blocs; `selection.py` LP weights,
  greedy column generation, MILP, random baseline) and `scripts/explore_knesset.py`
  (K25 in-sample experiment: 14 boxes reproduce the national result exactly, so only
  held-out evaluation is meaningful).
- **Box matching diagnostics** (`src/election_estimation/matching.py`,
  `scripts/box_matching_report.py` → `reports/box_matching.md`): base-box keys survive
  well K16→K23 but K24 reorganized the numbering (base boxes 9,388 → 5,614, each now a
  group of sub-boxes); boxes present in all of K16–K25 hold only 42% of K25's votes.
  Knesset 16–17 ballot ids are ten times larger (61, 62 = box 6 split); `load_ballots`
  normalizes them. See `docs/MODEL_PLAN.md` section 3.1.
- **Seat tests** (`tests/test_metrics.py`, `python -m pytest -q tests`): the modelling
  Bader-Ofer (`metrics.py`, rules from `ELECTIONS` via `elections.py`) reproduces the
  official seats of all eleven elections.
- **Evaluation harness** (`src/election_estimation/evaluate.py`): rolling folds (test
  K17–K26, training = all earlier elections), unit as a parameter, whole-unit and
  single-box readings, share / seat / bloc / threshold metrics.
- **Baselines** (`scripts/run_baselines.py` → `reports/baselines_{settlement,base_box}.md`),
  mean over test elections K22–K26:

  | Method, unit, reading | Panel 50 | Panel 70 |
  |---|---|---|
  | All regular boxes (double-envelope gap, no sampling) | 1.95 pp, 2.8 seats | same |
  | Random PPS, base box | 17.6 pp, 24.9 seats | 14.3 pp, 20.6 seats |
  | Greedy, base box | 8.2 pp, 13.2 seats | 7.6 pp, 13.6 seats |
  | Greedy, settlement, whole settlement counted | 4.5 pp, 7.6 seats | 4.6 pp, 6.4 seats |
  | Greedy, settlement, one box per settlement | 17.3 pp, 23.0 seats | 16.0 pp, 21.4 seats |

  Takeaways: optimized panels beat random ones by about half; whole settlements are
  accurate but cost far more than 50–70 boxes (cities), and reading one box of a
  heterogeneous settlement destroys the gain. Small homogeneous units (statistical areas,
  M7) are needed for a 50–70 box budget.
- **Statistical areas** (D22 answered): the user uploaded the Israel-Elections-Map ballot
  files for K19–K25 (`data/raw/geography/`, CBS 2011 areas). `scripts/build_areas.py`
  (run by `build_data.py`) writes `data/processed/ballot_areas.csv`; K26 is linked through
  K25 polling centers. About 2,600 areas, 3–4 boxes each; 6–8% of boxes have no area and
  use their settlement. The area unit covers K19–K26 (K16–K18 dropped for areas).
- **Box budgets, stratified sampling and MILP** in the harness (`evaluate.py`): every
  result records the boxes counted; `stratified` (bloc strata, one box per unit),
  `greedy_budget` and `milp_budget` (whole units under a box budget; the MILP keeps the
  greedy solution when it finds nothing better in 45 s). `scripts/compare_baselines.py`
  → `reports/baselines_summary.md` compares units and methods at equal budgets.
  Mean over held-out K22–K26 (floor, all regular boxes: 2.8 seats, 1.95 pp):

  | Budget | Best optimized | Best probability sample | Random PPS (area) |
  |---|---|---|---|
  | 50 boxes | base box, MILP: 8.0 seats, 7.3 pp | area, stratified: 13.1 seats, 9.8 pp | 20.3 seats, 14.5 pp |
  | 70 boxes | base box, greedy/MILP: 8.4 seats, 6.1–6.6 pp | area, stratified: 11.3 seats, 8.5 pp | 17.8 seats, 12.9 pp |

  Caveats: only five test elections, so 1–2 seat differences are noise; the optimized
  methods interpolate the training targets (greedy reaches zero training loss with about
  as many units as stacked target rows, e.g. 42 units for 44 rows), so their weights
  overfit. Regularization is the next modelling step.
- **Weight regularization** (`scripts/run_regularization.py <unit>` →
  `reports/regularization_{area,base_box}.{csv,md}`): three options added to
  `greedy_budget`, each with its strength chosen per test election by inner validation
  (the last 2 training elections, 50 boxes, seat L1): `weight_prior` (L1 pull towards
  size-proportional weights, `mu` in 0.003/0.01/0.03), `calibration` (extra targets per
  bloc-profile stratum: dominant bloc x pure/mixed at 60%, weight 0.3/1.0) and `noise`
  (4 log-normal perturbed copies of each training election, sigma 0.1/0.3). Unit costs
  are now the most boxes in the last 2 training elections (`unit_costs`), which stopped
  budget overshoot. Seed 0, decay 0.7, 20 greedy candidates. Mean seat L1 / share L1
  over K22–K26:

  | Unit, budget | No regularization | weight_prior | calibration | noise |
  |---|---|---|---|---|
  | area, 35 | 15.2 / 10.3 | **12.4 / 8.6** | 14.0 / 9.0 | 14.0 / 10.4 |
  | area, 50 | 14.8 / 10.3 | 14.0 / 9.1 | **11.6 / 9.0** | 15.6 / 10.2 |
  | area, 70 | 18.0 / 11.1 | 18.0 / 10.0 | **11.2 / 8.2** | 14.4 / 9.9 |
  | base box, 35 | **8.8 / 7.4** | 11.6 / 9.1 | 12.8 / 10.4 | 18.8 / 12.8 |
  | base box, 50 | **8.4 / 7.7** | 10.4 / 7.9 | 10.8 / 9.2 | 13.6 / 10.0 |
  | base box, 70 | 9.6 / 8.4 | **9.6 / 7.6** | 12.4 / 9.7 | 10.0 / 8.2 |

  Findings: on areas, calibration targets help at 50–70 boxes, mostly by fixing K25
  (36 → 18 seats at 50); on base boxes no regularization beats plain greedy, which stays
  the best panel overall (8.4 seats at 50 boxes, floor 2.8). Per-election swings are
  large (seat L1 moves in steps of 2), so with five tests only the area-calibration gain
  at 70 boxes is clearly beyond noise. Noise replicates hurt base boxes. Inner validation
  picked calibration 1.0 in 4 of 5 folds; `mu` and sigma vary by fold.
- **Regular-box target and the 0–2 seat goal (M10–M12)**: `load_election(target="regular")`
  predicts the total of the regular boxes (counting every box = 0 error); `score` reports
  `seats_moved` (seat L1 / 2); greedy panels can be nested across budgets; `fit_weights`
  builds a sparse LP. Held-out K22–K26, mean (worst) seats moved:

  | Panel | Size | Boxes counted | Seats moved |
  |---|---|---|---|
  | base boxes, greedy | 100 boxes | 105 | 4.4 (7) |
  | base boxes, weight prior | 100 / 160 boxes | 103 / 167 | 3.6 (5) / 3.2 (6) |
  | base boxes, calibration + prior | 60 boxes | 61 | 4.2 |
  | base boxes, stratified sample | 160 boxes | 130 | 5.3 (8.3) |
  | settlements, greedy | 35 settlements | 787 | 3.0 (5) |
  | settlements, weight prior | 35–50 settlements | 430–500 | **2.8 (5–6)** |
  | settlements, random PPS | 50 settlements | 5,700 | 9.4 (12.7) |

  No method meets the goal (at most 2 in the mean and the worst election). Above about
  100 boxes more boxes barely help: plain greedy stops at about 128 boxes because it then
  fits the training elections exactly, and the remaining error is the change in voting
  between elections, not sample size. The worst elections are K26 (new lists) and K24.
  In hindsight (`run_settlement_panel.py --oracle`, panel chosen on the test election
  itself, not a model result) about 16 base boxes or 10 settlements give 0 seats moved
  in every election, so a precise panel exists for each election but differs between
  elections. A rough probe of a swing estimator (previous result + mean change in the
  sampled boxes, by party family, random boxes) lowered K25–K26 errors from about 7.5 to
  5.5 seats moved at 160 boxes and did not help K24. Reports:
  `reports/budget_curve_base_box.md`, `reports/settlement_panel.md`, `reports/oracle_panel.csv`.
- **Swing model (M13–M15)**: `election_estimation/swing.py`, `scripts/run_swing_panel.py`
  → `reports/swing_panel.md`. National bloc shares = previous election (all regular
  boxes) + the panel's weighted bloc swing; lists split within blocs by the panel; weights
  fit past national bloc swings plus list-share rows (`level`), weight prior `mu`, both by
  inner validation (2 folds, 35 settlements). Held-out K22–K26, seats moved mean (worst):
  30 settlements 2.6 (4), 50 settlements 2.6 (5); the level panel at 35–50 settlements
  2.8 (5–6). The swing fixes K26 (6 → 3) but loses K25 (2 → 6); bloc shares improve
  (bloc share L1 3.1–3.4 vs 4.0–4.5 pp). A probe averaging the level and swing
  predictions (two panels, about 960 boxes at 40 settlements each) gave 2.4 (4). The
  goal (at most 2 in the mean and the worst election) is still not met; the remaining
  error is mostly the split of a bloc into its lists (max list error about 1.4 pp).
- **Joint level + swing panels (M16–M19)**: `SwingPanel(family=True, alpha=...)`,
  `scripts/run_joint_panel.py` → `reports/joint_panel.md`. Held-out K22–K26, seats moved
  mean (worst), boxes counted:

  | Settlements | `joint_family` | `joint_bloc` (ablation) |
  |---|---|---|
  | 20 | **2.4 (4)**, 532 boxes | 3.8 (9), 639 |
  | 40 | 2.8 (5), 744 | 3.6 (9), 742 |
  | 70 | 2.6 (5), 931 | 3.0 (5), 867 |
  | 100 | **2.4 (5)**, 1,089 | 3.0 (5), 1,002 |
  | 150 | 2.6 (5), 1,283 | 2.8 (5), 1,116 |

  The family swing helps (mainly K25: 9 → 5). With `joint_family`, K22–K24 are at 1–3
  seats moved and K26 at 2–4 for most sizes; K25 stays at 5. The K25 miss is Balad: it
  ran alone for the first time (3.05%, below the 3.25% threshold), its share is split
  from the Arab bloc by the panel only, and an estimate of about 4% gives it 4–5 seats.
  Likud was also about 1.8 pp low. Inner validation chose `mu` 0.01, `level` 0.1 and
  `alpha` 0–0.5 (mostly 0.25). The goal (at most 2 in the mean and the worst election)
  is not met yet.
- **Docs**: `README.md`, `data/README.md`, `docs/METHODOLOGY.md`, `CLAUDE.md`.

## Key facts (from `python scripts/summarize_elections.py`)

| Knesset | Date | Registered | Turnout | Valid | Regular boxes | Envelope rows | Envelope votes | Split box ids | Lists / passed | Regular vs national L1 (pp) |
|---|---|---|---|---|---|---|---|---|---|---|
| 16 | 2003-01-28 | 4,720,075 | 67.81% | 3,148,364 | 7,736 | 1 | 155,933 (4.95%) | 0 | 28 / 13 | 1.66 |
| 17 | 2006-03-28 | 5,011,053 | 63.59% | 3,137,064 | 8,277 | 149 | 171,390 (5.46%) | 0 | 31 / 12 | 1.68 |
| 18 | 2009-02-10 | 5,278,985 | 64.72% | 3,373,490 | 9,263 | 1 | 184,391 (5.47%) | 6 | 34 / 12 | 1.28 |
| 19 | 2013-01-22 | 5,656,705 | 67.77% | 3,792,742 | 9,881 | 228 | 212,949 (5.61%) | 4 | 34 / 12 | 1.55 |
| 20 | 2015-03-17 | 5,881,696 | 72.34% | 4,210,884 | 10,119 | 295 | 232,681 (5.53%) | 116 | 26 / 10 | 1.55 |
| 21 | 2019-04-09 | 6,339,729 | 68.46% | 4,309,270 | 10,460 | 305 | 238,822 (5.54%) | 1,563 | 43 / 11 | 1.39 |
| 22 | 2019-09-17 | 6,391,218 | 69.86% | 4,436,806 | 10,539 | 362 | 280,216 (6.32%) | 1,725 | 32 / 9 | 1.56 |
| 23 | 2020-03-02 | 6,453,255 | 71.52% | 4,590,062 | 10,631 | 548 | 327,702 (7.14%) | 1,584 | 30 / 8 | 1.76 |
| 24 | 2021-03-23 | 6,578,084 | 67.44% | 4,410,052 | 12,127 | 799 | 421,619 (9.56%) | 8,842 | 39 / 13 | 1.86 |
| 25 | 2022-11-01 | 6,788,804 | 70.63% | 4,764,742 | 11,707 | 838 | 458,714 (9.63%) | 7,342 | 40 / 10 | 2.18 |
| 26 | 2026-10-27 | 7,331,981 | 77.97% | 5,690,685 | 12,018 | 908 | 449,358 (7.90%) | 4,373 | 38 / 11 | 2.38 |

Envelope bias examples (regular boxes vs. envelopes):
- Knesset 16: Shinui 12.00% vs 17.51%, Likud 29.15% vs 34.01%, UTJ 4.44% vs 1.48%, Shas 8.38% vs 5.28% (envelopes derived from official totals).
- Knesset 17: National Union-NRP 6.96% vs 10.32%, Kadima 21.94% vs 23.46%, Ra'am-Ta'al 3.16% vs 0.62%, UTJ 4.83% vs 2.30%.
- Knesset 18: Likud 21.41% vs 25.17%, Yisrael Beiteinu 11.60% vs 13.30%, Ra'am-Ta'al 3.53% vs 0.75%, Hadash 3.46% vs 0.94%.
- Knesset 19: Jewish Home 8.77% vs 15.11%, Yesh Atid 14.22% vs 16.23%, Ra'am-Ta'al 3.80% vs 1.14%, UTJ 5.33% vs 2.37%.
- Knesset 20: Joint List 11.04% vs 3.14%, UTJ 5.12% vs 2.69%, Likud 23.27% vs 25.65%, Jewish Home 6.41% vs 12.39%.
- Knesset 21: Hadash-Ta'al 4.65% vs 1.76%, UTJ 5.92% vs 3.38%, Blue and White 25.97% vs 28.77%, Likud 26.29% vs 29.34%.
- Knesset 22: Joint List 11.02% vs 4.27%, Yisrael Beiteinu 7.12% vs 5.00%, Yamina 5.67% vs 8.85%, Blue and White 25.66% vs 30.21%.
- Knesset 23: Joint List 13.22% vs 5.52%, UTJ 6.12% vs 4.09%, Likud 29.22% vs 32.67%, Blue and White 26.34% vs 29.85%.
- Knesset 24: Yamina 5.87% vs 9.41%, Labor 5.88% vs 8.13%, Ra'am 4.02% vs 1.57%, UTJ 5.88% vs 3.27%.
- Knesset 25: Religious Zionism 10.35% vs 15.45%, Ra'am 4.32% vs 1.75%, UTJ 6.11% vs 3.74%.
- Knesset 26 (provisional): Religious Zionism-Zehut 4.69% vs 9.91%, Beyachad 8.98% vs 13.48%, Joint List 9.27% vs 3.14%, Ra'am 6.20% vs 2.72%.

## Findings from an earlier session

A separate session (branch `claude/peaceful-cerf-knn9rl`, never committed, so its code
is **not** in this repo) ran in-sample selection experiments on Knesset 25. Results are
in [docs/METHODOLOGY.md §6](docs/METHODOLOGY.md#6-knesset-25-experiment-in-sample-for-illustration-only).
Main lessons: 14 boxes fit Knesset 25 exactly (overfitting), LASSO gives no sparsity
when weights sum to 1, MILP beats greedy.

Data source survey from that session:

| Knesset | Settlement level | Ballot level | Main source |
|---------|------------------|--------------|-------------|
| 13-15 (1992-1999) | probably | unknown | odata.org.il, GitHub projects |
| 16-20 (2003-2015) | yes | yes | data.gov.il (votes-knesset), odata.org.il |
| 21-25 (2019-2022) | yes | yes | votesNN.bechirot.gov.il, data.gov.il |
| 26 (Oct 2026) | yes, provisional | yes, provisional | votes26.bechirot.gov.il |

Decision: work with Knesset 16-26 (11 elections with ballot-level data). Useful
projects: `harelc/elections-vote-transfer` (ballot matching across elections),
`Yoavfried/israel-election-map` (mapping to 2022 statistical areas).

### Sources checked for Knesset 16-18 (2026-10-30)

data.gov.il, bechirot.gov.il and odata.org.il are blocked from the cloud container, so
the official files could not be opened here; GitHub copies were downloaded and checked.

| Knesset | Source | Envelopes | Checked totals |
|---------|--------|-----------|----------------|
| 18 (2009) | Yoavfried `public-data/v1/ballots/k18.csv` (normalized English schema, `is_envelope` column) | yes | valid 3,373,490; Kadima 22.47%, Likud 21.61% (= official) |
| 17 (2006) | Yoavfried `public-data/v1/ballots/k17.csv` | yes (149 rows) | valid 3,137,064 (= official); eligible voters per box recovered by the project from archived reports, not in the official file |
| 16-18 | harelc `ballot16.csv`, `ballot17.csv`, `ballot18.csv` (original CEC Hebrew layout) | **no** - regular boxes only | K18 valid 3,189,099 and K16 2,992,431 (official totals are higher by the envelope votes); K17 has `בזב = 0` in every row |
| 16-20 | data.gov.il package `26f9fa06-fcd7-4173-8df5-65797b63e857` (official, per Yoavfried's docs) | unknown | not reachable from here |
| 14-20 | odata.org.il dataset `elections` (e.g. K18 "לפי ישובים וקלפיות" xlsx) | unknown | not reachable from here |

None of these has a separate settlements file for K16-18 in the CEC layout; settlements
can be summed from the ballots (as done for the Knesset 19 envelopes row).

## Open questions for the user

Every open question is listed here with the value currently used, so work can go on
until the user decides. IDs are stable: refer to them (e.g. "B3") when answering, and
move answered items to "Decisions" below with the answer.

### Blocs (`bloc` column in `data/parties/`)

| ID | Question | Current value | Options |
|----|----------|---------------|---------|
| B4 | New Hope (K24): right-wing party in the anti-Netanyahu coalition | right | right; center-left |
| B5 | Kulanu (K20-21): center-right, sat in the Likud-led coalition | right | right; center-left |
| B6 | Blue and White (K21-23, joint list with Telem's right-leaning members; K24 Gantz only) | center-left | center-left; split center/left (see B2) |
| B8 | Labor-Gesher (K22): Gesher was center-right | center-left | center-left |
| B9 | Yamina (K24) and Ra'am (K24) joined the Bennett-Lapid coalition | right / arab | keep ideological; only matters under B1 |
| B10 | Arab bloc: keep Ra'am (Islamist, joined a coalition) with Hadash-Ta'al and Balad? | arab | keep; split "arab" into two |
| B11 | Zionist Union (K20, Labor + Hatnua) | center-left | center-left |
| B12 | Likud-Yisrael Beiteinu (K19, joint list) | right | right |
| B13 | Hatnua (K19, Livni) and Kadima (K17-19): centrist lists | center-left | center-left; center (see B2) |
| B14 | Gil Pensioners (K17, 7 seats, in the Kadima-led coalition) | other | other; center-left |
| B15 | National Union (K16, K18) and National Union-NRP (K17) | right | right |
| B16 | Shinui (K16, secular liberal) and One Nation (K16, Amir Peretz, later merged into Labor) | center-left | center-left; center (see B2) |
| B17 | Yisrael BaAliyah (K16, Sharansky, later merged into Likud) and NRP (K16) | right | right |

### Party families (`family` column; used for party averages in the report)

| ID | Question | Current value | Options |
|----|----------|---------------|---------|
| F1 | Labor-Gesher (K22) and Labor-Gesher-Meretz (K23) | Own families | Merge into Labor; keep |
| F2 | Democratic Union (K22) | Own family | Merge into Meretz; keep |
| F3 | Blue and White K21-23 (Gantz + Lapid) and K24 (Gantz only) | One family "Blue and White" | Keep; split K21-23 from K24 |
| F4 | National Unity (K25), led by Gantz | Own family | Merge into Blue and White; keep |
| F5 | Right-wing religious lists: Union of Right-Wing Parties (K21), Yamina (K22-24), Religious Zionism (K24-25), Jewish Home (K25) | Each name is its own family; Yamina K22-24 one family | Keep; build a lineage (e.g. URWP → Religious Zionism) |
| F6 | Arab lists: Hadash-Ta'al and Ra'am-Balad (K21), Joint List (K20, K22-24), Ra'am, Hadash-Ta'al, Balad (K25) | Each name is its own family | Keep; one "Joint List" family across all |
| F7 | Zionist Union (K20, Labor + Hatnua) | Own family | Merge into Labor; keep |
| F8 | Jewish Home (K19-20, under Bennett) and Jewish Home (K25, a much smaller list) | One family "Jewish Home" | Keep; split; link K19-20 to Yamina / New Right |
| F9 | Likud-Yisrael Beiteinu (K19) | Own family | Keep; count under Likud (and Yisrael Beiteinu is then missing in K19) |
| F10 | Hatnua (K19), later part of Zionist Union (K20) | Own family | Keep; link to Zionist Union |
| F17 | The Democrats (K26, Labor + Meretz merger) | Own family | Merge into Labor or Meretz; keep |
| F18 | Religious Zionism-Zehut (K26) | Family "Religious Zionism" (shared with K24-25) | Keep; split |
| F19 | Joint List (K26) | Family "Joint List" (shared with K20, K22-24) | Keep |
| F12 | Labor-Meimad (K16-17) | Own family | Merge into Labor; keep |
| F15 | United Arab List (K16) | Family "Ra'am" (shared with K24-25) | Keep; split |
| F16 | Hadash-Ta'al (K16) | Family "Hadash-Ta'al" (shared with K21, K25) | Keep; split |
| F13 | Meretz-Yachad (K17) and New Movement-Meretz (K18): Meretz under other names | Family "Meretz" | Keep; split |
| F14 | National Union-NRP (K17), National Union (K18), Jewish Home (K18-20) | Own families, Jewish Home shared with K19-20 and K25 | Keep; build a lineage (see F5, F8) |
| F11 | Hadash, Balad and Ra'am-Ta'al (K19) ran separately; Joint List (K20, K22-24) united them | Each name is its own family | Keep; see F6 |

### Data

| ID | Question | Current value | Options |
|----|----------|---------------|---------|
| D1 | Meaning of the `ריכוז` (`concentration`) and `שופט` (`judge`) columns | Kept as published | User explains; drop them |
| D2 | Names of small lists (below threshold), e.g. K21 `נ` (3.22%, 1,454 votes short, probably New Right), K20 `קץ` (2.97%, 11,696 votes short, probably Yachad) and K19 `נץ` (1.76%, threshold 2%) | Empty, `verified = no`, bloc other ("other" = 8.49% in K21) | User sends the official list names; leave empty |
| D3 | Surplus agreements: only those that reproduce the official seats are recorded | Partial list per election | User sends the official lists of agreements |
| D4 | Knesset 19-21 have no committee code / ballot uid / ריכוז / שופט | Empty | Fill committee code from K22 by settlement code; keep empty |
| D5 | Knesset 26 (October 2026) | Not added | Add provisional results now; wait for the final results (~2026-11-04) |
| D6 | How far back to go | Plan: Knesset 16-26 | K17-18 usable (Yoavfried, with envelopes; or official files if the user downloads them); K16 only without envelopes so far; K14-15 unknown |
| D11 | Knesset 17 eligible voters per box were recovered by the Yoavfried project from archived reports (total 5,011,053), not taken from the official file | Used as is | Keep; replace with official numbers if found |
| D12 | Knesset 16 envelopes row: official totals minus regular boxes. Official votes of the 17 largest lists and the totals come from Wikidata / IFES ElectionGuide (found by web search; Wikipedia itself is blocked here); the 1,707 envelope votes of the 11 smallest lists are split in proportion to their regular votes (estimate) | Added this way | Keep; replace with the official envelope file if found |
| D14 | Knesset 26 is provisional: the files were downloaded before the committee's certified results; seats match the final distribution reported in the press (Likud 27, Yashar 21, Beyachad 12, Joint List 11, Democrats 8, Ra'am 8, Yisrael Beiteinu 7, UTJ 7, Otzma Yehudit 7, Shas 6, Religious Zionism-Zehut 6) | `provisional: True` in `ELECTIONS`; report says "not final" | Replace the raw files with the certified ones and remove the flag |
| D16 | Knesset 26 ballots file has two new columns, `חיצוניות` and `קלפי אחרת` (kept as `external`, `other_ballot`; all zero) | Kept, meaning unknown | User explains; drop them |
| D17 | List leaders (`leader_he`, #1 on each list that passed): from search snippets, not from the committee's official candidate lists. 50 are "medium" (source names the party leader, not explicitly #1), e.g. most of K16-17, K21 Meretz (Zandberg), K18 Jewish Home (Hershkowitz). Notable #1s: K16 National Union = Liberman, K17 National Union-NRP = Elon, K19 Shas = Yishai, K22 Yamina = Shaked, K26 UTJ = Yaakov Asher, K26 Joint List = Yousef Jabareen | Used, sources in `data/parties/leaders_sources.csv` | Verify against the official lists (needs gov.il / knesset.gov.il access); keep |
| D18 | Small lists have no names or leaders, so the party lookup shows them as "רשימה <letters> (כנסת N)" (e.g. K26 `צדק`) | Unnamed | Name them from the committee's list of candidate lists per election; leave |
| D19 | Knesset 26: 38 lists were approved and two (Blue and White, Tnuat Achi) withdrew, leaving 36 on the ballot (per news sources); the ballots file has 38 letter columns, and exactly two have 0 votes everywhere: `כן` (Blue and White's letters in K24-25) and `צבי` | Kept as in the file (0 votes, unnamed) | Name them (likely Blue and White and Tnuat Achi); drop zero columns |
| D13 | Knesset 14-15 (1996, 1999): no ballot-level file found; maybe on odata.org.il | Not added | User downloads from odata.org.il; skip |
| D10 | Source for K16-18: official data.gov.il / odata files downloaded by the user, or the GitHub copies | Yoavfried for K17-18 (added); replace with official files if the user gets them | Keep; switch to official |
| D7 | Knesset 20: Kulanu needs a surplus agreement to reach its official 10 seats; the partner is unknown (Shas, UTJ, Yisrael Beiteinu, Meretz, Yesh Atid or Zionist Union all work) | Placeholder: Kulanu + Yisrael Beiteinu | User confirms the real partner |
| D8 | Knesset 20 split boxes share one number; their order (`-1`, `-2`) follows the file | File order | Keep; ignore the difference (merge, see M5) |
| D9 | Knesset 19 settlements file leaves out the envelope votes; the build adds an envelopes row summed from the ballots file | Derived row | Keep |
| D21 | Exact official name of K26 `די` (described by the user as the Reservists' and economic party of Yaron Zelekha and Yoaz Hendel) and its #1 | Name "המילואימניקים והמפלגה הכלכלית", leader empty | Confirm from the committee's list |

### Modeling

| ID | Question | Current value | Options |
|----|----------|---------------|---------|

### Decisions

Answered by the user on 2026-10-30.

| ID | Decision |
|----|----------|
| B1 | Blocs are ideological (right, center-left, arab, haredi, other), not coalition camps |
| B3 | Yisrael Beiteinu is `right` |
| B7 | National Unity (K25) is `center_left` |
| B18 | Beyachad (K26, Bennett, letters `רק`) is `right` |
| B19 | Yashar! (K26, Eisenkot, letters `דרך`) is `center_left` |
| B20 | Otzma Yehudit (K26, letters `ב`) is `right` |
| B21 | K26 `די` (the Reservists and the economic party, Zelekha and Hendel) and `ך` (Amcha Yisrael, Ofer Winter) are `right` |
| B22 | Haredi lists are a separate bloc for now; a three-bloc scheme (haredi merged into right) is evaluated alongside |
| B23 | Lists under 1% nationally are not assigned individually; they stay `other` |
| D15 | K26 letters confirmed by the user: `דרך` Yashar!, `רק` Beyachad, `ודם` Joint List, `ב` Otzma Yehudit, `ט` Religious Zionism, `אמת` The Democrats, `ל` Yisrael Beiteinu, `עם` Ra'am |
| M1, M5 | Sampling unit: base ballot box (sub-boxes `283.1`, `283.2` merged into `283`) |
| M2 | Loss and evaluation: L1 on party shares, L1 on seats (Bader-Ofer), L1 on bloc shares and bloc seats |
| M3 | Double envelopes are part of the national target, never candidates; the box weights compensate for them |
| M4 | Panel size about 50-70 boxes (order of sqrt of the number of settlements); scenario: a fixed panel chosen in advance, prediction = fixed weighted average |

| M6 | Training window: all elections before the test election, weighted towards recent ones (decay rate tuned in validation) |
| M7 | Sampling unit: CBS statistical area (2022 areas, mapping from the Yoavfried project), the whole settlement where there are no areas; replaces M1's base box |
| M8 | Main accuracy target: seats per list (including who passes the threshold); the seat term gets the largest weight in the loss and is the primary selection metric |
| D20 | The three boxes with more voters than registered are kept as published |
| M9 | On election night one representative ballot box is counted per panel area; evaluation must include the noise of reading a single box instead of the whole area |
| B2 | Center-left stays one bloc (no center / left split) |
| M10 | Accuracy target (2026-10-31): the total of the regular boxes (double envelopes excluded), so counting every box gives zero error; `load_election(..., target="regular")` |
| M11 | Goal: at most 2 seats moved between lists (`seats_moved` = seat L1 / 2) with a panel of N = 40–160 boxes; the user prefers more boxes over a larger error |
| M12 | Success = the goal holds in the mean over the test elections and in the worst one; unit for the budget curve: base box |
| M13 | Next model (2026-10-31): a swing model - previous result of all regular boxes plus the change measured in the panel (`election_estimation/swing.py`) |
| M14 | The swing is measured per bloc on settlement panels; new lists need no lineage, lists within a bloc are split by the panel |
| M15 | Swing panel weights are fit to reproduce past national bloc swings (with a weight prior), strengths by inner validation |
| M16 | Within a bloc, a list whose family ran as one list in both elections gets its previous share plus the panel's swing; new lists and merged / split families get the panel's part of the bloc |
| M17 | One joint panel for the level and swing predictions, mixed by `alpha` chosen in inner validation |
| M18 | Larger settlement panels: 70, 100, 150 settlements, no box cap |
| M19 | Inner validation selects on share L1 over the last 3 training elections (seats are measured only on the test) |
| D22 | Area mapping: the user uploaded the Israel-Elections-Map ballot files for K19–K25; the area unit starts at K19, and the files are kept byte-for-byte in `data/raw/geography/` |

The full model design is in [docs/MODEL_PLAN.md](docs/MODEL_PLAN.md).

## Next steps

The implementation plan is section 8 of [docs/MODEL_PLAN.md](docs/MODEL_PLAN.md).
In short:

1. **Reach the 0–2 seat goal** (M11) - best so far `joint_family`: 2.4 (worst 4) at 20
   settlements, 2.4 (worst 5) at 100. Remaining misses are lists near the threshold that
   are new in their form (K25 Balad). Options: stratify the panel so every bloc has enough
   settlements for the within-bloc split, a threshold-aware estimate (probability of
   passing from bootstrap of the panel), or report seat intervals instead of one number.
2. **Neural model** (user: later) - Hard-Concrete gates and softmax weights with the
   combined share / seat / bloc loss, recency weights and the calibration targets / weight prior,
   then LP refit.
3. **Hyperparameters** - λ, α, β, γ, μ, decay; seat L1 is the selection metric (M8).
4. **Analysis** - panel composition, stability across folds, bloc-scheme comparison.
5. **Data** - replace Knesset 26 with the certified files (D14); check the
   Israel-Elections-Map licence.
