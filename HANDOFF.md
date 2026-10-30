# Handoff

Last updated: 2026-10-30. Branch: `claude/stoic-tesla-h2fa2d`.

## Goal

A statistical model that selects a minimal number of sample ballot boxes and estimates
the national result with minimal L1 error, with a regularization penalty `λ` on the
number of boxes. Details in [docs/METHODOLOGY.md](docs/METHODOLOGY.md).

## Done

- **Knesset 25 data** (2022, final) in `data/raw/`, byte-identical to the committee's
  `expb_1.csv` (ballots) and `expc_1.csv` (settlements).
- **Build pipeline** `scripts/build_data.py`:
  - validates `voters = invalid + valid`, party sums = `valid`, unique ballot ids,
    and ballots summed per settlement = settlements file;
  - standardizes column names to English, keeps `ballot_id` as text;
  - flags double envelopes (`settlement_code = 9999`) with `is_envelopes`;
  - computes national shares and seats (threshold + Bader-Ofer with surplus
    agreements), reproducing the official result (Likud 32, Yesh Atid 24, ...);
  - writes per-election CSVs, an Excel workbook with tables and formulas (checked
    in LibreOffice, no errors), and `ballots_long.csv.gz` for all elections.
- **Party table** `data/parties/knesset_25_parties.csv`: 13 main lists named; small
  lists marked `verified = no`.
- **Docs**: `README.md`, `data/README.md`, `docs/METHODOLOGY.md`, `CLAUDE.md`.

## Key facts (Knesset 25, verified on the data in this repo)

- 6,788,804 registered, 70.63% turnout, 4,764,742 valid votes.
- 11,707 regular ballot boxes + 838 double-envelope rows (458,714 votes, 9.63% of valid).
- 7,342 ballot ids are split boxes (`283.1`, `283.2`, ...).
- All regular boxes summed vs. national result: 2.18 pp L1 (envelope bias).
  Religious Zionism 10.35% regular vs 15.45% envelopes; Ra'am 4.32% vs 1.75%.

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
- Names of the small Knesset 25 lists.
- Sample unit: ballot box or settlement (current plan: ballot box).

## Next steps

1. **Data** - add `expb` / `expc` for Knesset 16-24, and Knesset 26 once final
   (expected around 2026-11-04). Add each to `ELECTIONS` in `scripts/build_data.py`
   and a party table in `data/parties/`.
2. **Ballot matching** - merge split boxes (`283.1` + `283.2` → `283`) and match boxes
   across elections by settlement + ballot number, or via statistical areas.
3. **Party lineage** - one mapping CSV per pair of consecutive elections, plus a bloc
   mapping (right, center-left, Haredi, Arab, other).
4. **Baselines** - random, greedy and MILP selection; envelope correction term.
5. **Validation** - select on `t`, test on `t+1`; choose `λ` from the error vs.
   number-of-boxes Pareto curve.
6. **Swing model**, then a **neural model** with Hard-Concrete gates for comparison.
7. **Seat metric** - evaluate seat error too, including the 3.25% threshold.
