# Handoff

Last updated: 2026-10-30. Branch: `claude/stoic-tesla-h2fa2d`.

## Goal

A statistical model that selects a minimal number of sample ballot boxes and estimates
the national result with minimal L1 error, with a regularization penalty `λ` on the
number of boxes. Details in [docs/METHODOLOGY.md](docs/METHODOLOGY.md).

## Done

- **Election data** in `data/raw/`, byte-identical to the committee's files:
  Knesset 23 (2020, `expb_3`/`expc_3`, Windows-1255), Knesset 24 (2021, `expb_2`/`expc_2`,
  Windows-1255) and Knesset 25 (2022, `expb_1`/`expc_1`, UTF-8).
- **Build pipeline** `scripts/build_data.py`:
  - validates `voters = invalid + valid`, party sums = `valid`, unique ballot ids,
    and ballots summed per settlement = settlements file;
  - reads UTF-8 and Windows-1255 files, drops empty trailing columns;
  - standardizes column names to English, keeps `ballot_id` as text;
  - flags double envelopes (`settlement_code = 9999`) with `is_envelopes`;
  - computes national shares and seats (threshold + Bader-Ofer with surplus
    agreements), reproducing the official result of all three elections;
  - writes per-election CSVs, an Excel workbook with tables and formulas (checked
    in LibreOffice, no errors), and `ballots_long.csv.gz` for all elections.
- **Party tables** `data/parties/knesset_{23,24,25}_parties.csv`: lists that passed the
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
| 23 | 2020-03-02 | 6,453,255 | 71.52% | 4,590,062 | 10,631 | 548 | 327,702 (7.14%) | 1,584 | 30 / 8 | 1.76 |
| 24 | 2021-03-23 | 6,578,084 | 67.44% | 4,410,052 | 12,127 | 799 | 421,619 (9.56%) | 8,842 | 39 / 13 | 1.86 |
| 25 | 2022-11-01 | 6,788,804 | 70.63% | 4,764,742 | 11,707 | 838 | 458,714 (9.63%) | 7,342 | 40 / 10 | 2.18 |

Envelope bias examples (regular boxes vs. envelopes):
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
- Names of the small lists (Knesset 23-25).
- Bloc assignment is a judgement call (e.g. Yisrael Beiteinu and New Hope as right); the
  user may want to change it in `data/parties/`.
- Surplus agreements in `ELECTIONS` are the ones that reproduce the official seats; other
  agreements that changed no seat may be missing.
- Sample unit: ballot box or settlement (current plan: ballot box).

## Next steps

1. **Data** - add `expb` / `expc` for Knesset 16-22, and Knesset 26 once final
   (expected around 2026-11-04), following the procedure in `CLAUDE.md`.
2. **First held-out pairs** - Knesset 23 → 24 and 24 → 25 are available: run the
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
