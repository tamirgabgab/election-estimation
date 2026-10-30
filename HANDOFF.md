# Handoff

Last updated: 2026-10-30. Branch: `claude/stoic-tesla-h2fa2d`.

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
| B1 | Scheme: ideological blocs, or coalition blocs (Netanyahu bloc vs. the rest)? | Ideological: right, haredi, center-left, arab, other | Keep; switch; or add a second column `coalition_bloc` and let the report choose |
| B2 | Split center-left into "center" and "left"? | One bloc | Keep; split (center = Blue and White, Yesh Atid, National Unity, Kulanu?; left = Labor, Meretz, Democratic Union) |
| B3 | Yisrael Beiteinu (K20-25): secular right, but outside the Netanyahu bloc since 2019 | right | right; center-left |
| B4 | New Hope (K24): right-wing party in the anti-Netanyahu coalition | right | right; center-left |
| B5 | Kulanu (K20-21): center-right, sat in the Likud-led coalition | right | right; center-left |
| B6 | Blue and White (K21-23, joint list with Telem's right-leaning members; K24 Gantz only) | center-left | center-left; split center/left (see B2) |
| B7 | National Unity (K25): Blue and White + New Hope + Eisenkot | center-left | center-left; center (see B2) |
| B8 | Labor-Gesher (K22): Gesher was center-right | center-left | center-left |
| B9 | Yamina (K24) and Ra'am (K24) joined the Bennett-Lapid coalition | right / arab | keep ideological; only matters under B1 |
| B10 | Arab bloc: keep Ra'am (Islamist, joined a coalition) with Hadash-Ta'al and Balad? | arab | keep; split "arab" into two |
| B11 | Zionist Union (K20, Labor + Hatnua) | center-left | center-left |
| B12 | Likud-Yisrael Beiteinu (K19, joint list) | right | right |
| B13 | Hatnua (K19, Livni) and Kadima (K17-19): centrist lists | center-left | center-left; center (see B2) |
| B14 | Gil Pensioners (K17, 7 seats, in the Kadima-led coalition) | other | other; center-left |
| B15 | National Union (K16, K18) and National Union-NRP (K17) | right | right |
| B16 | Shinui (K16, secular liberal) and One Nation (K16, Amir Peretz, later merged into Labor) | center-left | center-left; center (see B2) |
| B18 | Beyachad (K26, Bennett), in the anti-Netanyahu opposition | right | right; center-left |
| B19 | Yashar! (K26, Eisenkot) | center-left | center-left; center (see B2) |
| B20 | Otzma Yehudit (K26, own list; part of Religious Zionism in K25) | right | right |
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
| D15 | Knesset 26 letters of new lists (`דרך` Yashar!, `רק` Beyachad, `ודם` Joint List, `ב` Otzma Yehudit) were matched by their seat counts to the reported results, not read from an official list | Used | Confirm against the committee's list of candidate lists |
| D16 | Knesset 26 ballots file has two new columns, `חיצוניות` and `קלפי אחרת` (kept as `external`, `other_ballot`; all zero) | Kept, meaning unknown | User explains; drop them |
| D13 | Knesset 14-15 (1996, 1999): no ballot-level file found; maybe on odata.org.il | Not added | User downloads from odata.org.il; skip |
| D10 | Source for K16-18: official data.gov.il / odata files downloaded by the user, or the GitHub copies | Yoavfried for K17-18 (added); replace with official files if the user gets them | Keep; switch to official |
| D7 | Knesset 20: Kulanu needs a surplus agreement to reach its official 10 seats; the partner is unknown (Shas, UTJ, Yisrael Beiteinu, Meretz, Yesh Atid or Zionist Union all work) | Placeholder: Kulanu + Yisrael Beiteinu | User confirms the real partner |
| D8 | Knesset 20 split boxes share one number; their order (`-1`, `-2`) follows the file | File order | Keep; ignore the difference (merge, see M5) |
| D9 | Knesset 19 settlements file leaves out the envelope votes; the build adds an envelopes row summed from the ballots file | Derived row | Keep |

### Modeling

| ID | Question | Current value | Options |
|----|----------|---------------|---------|
| M1 | Sample unit | Ballot box | Ballot box; settlement |
| M2 | Target metric | L1 on shares of valid votes (pp) | Also seat error; also bloc error |
| M3 | Double envelopes (5.5%-9.6% of valid votes, growing) | Model them as a separate term from past elections | Ignore; separate term |
| M4 | Budget: a maximum number of sample boxes, or only the `λ` trade-off? | `λ` trade-off, chosen on the Pareto curve | Fixed maximum (e.g. 100 boxes); `λ` only |
| M5 | Split boxes (`283.1`, `283.2`): one sampling unit or separate? | Not decided | Merge per base number; keep separate |
| M6 | Training window: all past elections, or only the last few? | Not decided | All; last k; weighted by recency |

### Decisions

None yet.

## Next steps

1. **Data** - replace Knesset 26 with the certified files (D14); Knesset 14-15 if files are found (D13), and Knesset 26 once final
   (expected around 2026-11-04), following the procedure in `CLAUDE.md`.
2. **First held-out pairs** - Knesset 16 → 17 through 25 → 26 are available: run the
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
