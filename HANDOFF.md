# Handoff

Last updated: 2026-10-30. Branch: `claude/stoic-tesla-h2fa2d`.

## Goal

A statistical model that selects a minimal number of sample ballot boxes and estimates
the national result with minimal L1 error, with a regularization penalty `λ` on the
number of boxes. Details in [docs/METHODOLOGY.md](docs/METHODOLOGY.md).

## Done

- **Election data** in `data/raw/`, byte-identical to the committee's files:
  Knesset 21 (2019-04, `expb_5`/`expc_5`, Windows-1255, older column layout),
  Knesset 22 (2019-09, `expb_4`/`expc_4`, Windows-1255),
  Knesset 23 (2020, `expb_3`/`expc_3`, Windows-1255), Knesset 24 (2021, `expb_2`/`expc_2`,
  Windows-1255) and Knesset 25 (2022, `expb_1`/`expc_1`, UTF-8).
- **Build pipeline** `scripts/build_data.py`:
  - validates `voters = invalid + valid`, party sums = `valid`, unique ballot ids,
    and ballots summed per settlement = settlements file;
  - reads UTF-8 and Windows-1255 files, drops empty trailing columns;
  - accepts the Knesset 21 layout (`מספר קלפי`, no committee / ברזל / ריכוז / שופט
    columns, which stay empty);
  - standardizes column names to English, keeps `ballot_id` as text;
  - flags double envelopes (`settlement_code` 9999, or 99999 in Knesset 21) with
    `is_envelopes`, and asserts exactly one envelopes row per election;
  - computes national shares and seats (threshold + Bader-Ofer with surplus
    agreements), reproducing the official result of all five elections;
  - writes per-election CSVs, an Excel workbook with tables and formulas (checked
    in LibreOffice, no errors), and `ballots_long.csv.gz` for all elections.
- **Party tables** `data/parties/knesset_{21..25}_parties.csv`: lists that passed the
  threshold are named and have a `family` and a `bloc` (right, haredi, center-left, arab);
  small lists are marked `verified = no`, bloc `other`.
- **HTML reports** in `reports/` (built by `scripts/build_reports.py`): one results page
  per election (seats, vote shares, threshold pass/fail, blocs) and `index.html` with an
  election selector and a comparison tab averaging seats or shares by bloc or party.
  Checked with `scripts/check_reports.js` (desktop and mobile, no errors).
- **Check scripts**: `scripts/check_excel.py` (LibreOffice recalculation, 0 errors in all
  workbooks) and `scripts/summarize_elections.py` (facts table below).
- **Procedure** for adding an election is fixed in `CLAUDE.md`.
- **Docs**: `README.md`, `data/README.md`, `docs/METHODOLOGY.md`, `CLAUDE.md`.

## Key facts (from `python scripts/summarize_elections.py`)

| Knesset | Date | Registered | Turnout | Valid | Regular boxes | Envelope rows | Envelope votes | Split box ids | Lists / passed | Regular vs national L1 (pp) |
|---|---|---|---|---|---|---|---|---|---|---|
| 21 | 2019-04-09 | 6,339,729 | 68.46% | 4,309,270 | 10,460 | 305 | 238,822 (5.54%) | 1,563 | 43 / 11 | 1.39 |
| 22 | 2019-09-17 | 6,391,218 | 69.86% | 4,436,806 | 10,539 | 362 | 280,216 (6.32%) | 1,725 | 32 / 9 | 1.56 |
| 23 | 2020-03-02 | 6,453,255 | 71.52% | 4,590,062 | 10,631 | 548 | 327,702 (7.14%) | 1,584 | 30 / 8 | 1.76 |
| 24 | 2021-03-23 | 6,578,084 | 67.44% | 4,410,052 | 12,127 | 799 | 421,619 (9.56%) | 8,842 | 39 / 13 | 1.86 |
| 25 | 2022-11-01 | 6,788,804 | 70.63% | 4,764,742 | 11,707 | 838 | 458,714 (9.63%) | 7,342 | 40 / 10 | 2.18 |

Envelope bias examples (regular boxes vs. envelopes):
- Knesset 21: Hadash-Ta'al 4.65% vs 1.76%, UTJ 5.92% vs 3.38%, Blue and White 25.97% vs 28.77%, Likud 26.29% vs 29.34%.
- Knesset 22: Joint List 11.02% vs 4.27%, Yisrael Beiteinu 7.12% vs 5.00%, Yamina 5.67% vs 8.85%, Blue and White 25.66% vs 30.21%.
- Knesset 23: Joint List 13.22% vs 5.52%, UTJ 6.12% vs 4.09%, Likud 29.22% vs 32.67%, Blue and White 26.34% vs 29.85%.
- Knesset 24: Yamina 5.87% vs 9.41%, Labor 5.88% vs 8.13%, Ra'am 4.02% vs 1.57%, UTJ 5.88% vs 3.27%.
- Knesset 25: Religious Zionism 10.35% vs 15.45%, Ra'am 4.32% vs 1.75%, UTJ 6.11% vs 3.74%.

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

## Open questions

- Meaning of the `ריכוז` (`concentration`) and `שופט` (`judge`) columns.
- Names of the small lists (Knesset 21-25). Knesset 21 list `נ` got 3.22%, 1,454 votes
  short of the threshold (probably New Right, not verified); "other" is 8.49% of valid votes.
- Proposed blocs for lists new in Knesset 21: Union of Right-Wing Parties → right,
  Kulanu → right (center-right, sat in the Likud-led coalition), Ra'am-Balad → arab.
- Knesset 21 files have no committee code, ballot uid, `ריכוז` or `שופט`.
- Proposed blocs for lists new in Knesset 22: Labor-Gesher and Democratic Union →
  center-left (their own families, not merged with Labor / Meretz).
- Bloc assignment is a judgement call (e.g. Yisrael Beiteinu and New Hope as right); the
  user may want to change it in `data/parties/`.
- Surplus agreements in `ELECTIONS` are the ones that reproduce the official seats; other
  agreements that changed no seat may be missing.
- Sample unit: ballot box or settlement (current plan: ballot box).

## Next steps

1. **Data** - add `expb` / `expc` for Knesset 16-20, and Knesset 26 once final
   (expected around 2026-11-04), following the procedure in `CLAUDE.md`.
2. **First held-out pairs** - Knesset 21 → 22 through 24 → 25 are available: run the
   baselines with selection on `t` and evaluation on `t+1`.
3. **Ballot matching** - merge split boxes (`283.1` + `283.2` → `283`) and match boxes
   across elections by settlement + ballot number, or via statistical areas.
4. **Party lineage** - one mapping CSV per pair of consecutive elections, plus a bloc
   mapping (right, center-left, Haredi, Arab, other).
5. **Baselines** - random, greedy and MILP selection; envelope correction term.
6. **Validation** - select on `t`, test on `t+1`; choose `λ` from the error vs.
   number-of-boxes Pareto curve.
7. **Swing model**, then a **neural model** with Hard-Concrete gates for comparison.
8. **Seat metric** - evaluate seat error too, including the 3.25% threshold.
