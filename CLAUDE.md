# Project instructions

Estimate Israeli Knesset results from a minimal sample of ballot boxes. Read
[HANDOFF.md](HANDOFF.md) first for status, and [docs/METHODOLOGY.md](docs/METHODOLOGY.md)
for the model design.

## Communication

- Always answer the user in Hebrew (RTL-safe, as in the global instructions). This
  includes every text the user sees while work runs in the background: progress updates,
  "waiting for X" notes, task and command descriptions, and short status lines. Write
  any reasoning shown to the user in Hebrew too. Code, comments, commit messages and docs
  are in English.
- Ask guiding questions before big changes (new model family, data layout changes).
- End each work round with a short summary by sections, and update `HANDOFF.md`
  (done, key facts, next steps) before committing.
- Every open question (blocs, families, data, modeling) goes into the "Open questions for
  the user" tables in `HANDOFF.md`, with a stable ID, the value currently used and the
  options. Keep working with the current value; when the user answers, apply it and move
  the item to "Decisions".

## Data rules

- `data/raw/` is immutable: copy files byte-for-byte, only rename to
  `knesset_<N>_<year>_{ballots,settlements}.csv`. Never edit raw files.
- `data/processed/` is generated only by `python scripts/build_data.py`. Never edit it by
  hand; change the script and rebuild.
- A new election = raw files + an entry in `ELECTIONS` + `data/parties/knesset_<N>_parties.csv`.
  Follow the procedure below.
- Read `ballot_id` as text (`3.10` is not `3.1`).
- Do not guess party names or facts. Mark unknowns (`verified = no`) and tell the user.
- Double envelopes (`is_envelopes`, normalized to code 9999) are never sampling
  candidates, but they are part of the national target.

## Procedure: the user sends results of a Knesset election

Follow these steps every time, in this order, so every election is handled the same way.

1. **Identify** - `expb*.csv` = one row per ballot box (`ballots`), `expc*.csv` = one row
   per settlement (`settlements`). Knesset 17-18 come from the Yoavfried/Israel-Elections-Map
   project instead (one ballots file with an `is_envelope` column, `"source": "yoavfried"`
   in the config, settlements summed from the ballots); use that path for any other
   election that only has such a file. Knesset 16 has regular boxes only
   (`"source": "regular_boxes_only"`): its envelopes row is official totals
   (`data/official/knesset_<N>_totals.csv`) minus the regular boxes. Confirm the Knesset number, year and election date;
   ask the user if any of them is unclear. If only one of the two files arrived, ask for
   the other before building.
2. **Inspect** - encoding (UTF-8 or Windows-1255), header names vs. `COLUMN_NAMES` in
   `scripts/build_data.py`, row counts, trailing empty columns, the envelopes row in each
   file (`מעטפות חיצוניות`; code 9999, but 99999 in Knesset 21, 875 / 0 in Knesset 20, and
   875 / missing in Knesset 19), duplicate ballot ids, and that the national shares
   (envelopes included) match the official ones. New or renamed base columns → extend `COLUMN_NAMES`/`read_raw`;
   missing ones → `OPTIONAL_*_COLUMNS` (left empty); another envelopes code →
   `envelopes_codes` in the election's config (normalized to 9999; `None` for a settlements
   file without the envelopes row, which is then summed from the ballots); split boxes sharing one
   number → `unsuffixed_split_boxes` (keys get `-1`, `-2`). Never edit the raw file.
3. **Copy raw** - byte-for-byte to `data/raw/knesset_<N>_<year>_ballots.csv` and
   `data/raw/knesset_<N>_<year>_settlements.csv` (ballots only for a `yoavfried` source);
   verify with `cmp`.
4. **Party table** - `data/parties/knesset_<N>_parties.csv` with columns
   `letter,name_he,name_en,family,bloc,verified,leader_he` and one row per letter column in
   the file. Name the lists that passed the threshold (`verified = yes` only when sure); all
   other letters get empty names, empty `family`, `bloc = other` and `verified = no`.
   - `leader_he` is the person in first place on the list in that election (shown in the
     party lookup of `index.html`). Fill it only from a source found for this election
     (#1 is not always the party chair); leave it empty when unconfirmed.
   - `family` groups the same party across elections in the reports. Use the `family`
     already used in earlier elections when it is the same party (e.g. Likud); a joint or
     new list gets its own family (default: `name_en`).
   - `bloc` is one of `right`, `haredi`, `center_left`, `arab`, `other`. Reuse the bloc of
     the same family in earlier elections; for a new list, propose one, tell the user and
     add it to the bloc / family questions in `HANDOFF.md`.
5. **Config** - add `ELECTIONS[<N>]` in `scripts/build_data.py`: `year`, `date`,
   `threshold`, `seats`, `surplus_agreements`. Thresholds: 1.5% up to Knesset 16 (2003),
   2% for Knesset 17-19 (2006-2013), 3.25% from Knesset 20 (2015). The surplus agreements
   must make the computed seats equal the official result; if the official seats cannot be
   confirmed, say so instead of guessing. When several sets of agreements reproduce the
   result and the real one is unknown, use a placeholder, comment it in `ELECTIONS` and add
   a data question to `HANDOFF.md`.
6. **Build** - `python scripts/build_data.py`. All validation asserts must pass and the
   printed seats must match the official result. This also rebuilds the HTML reports.
7. **Regression check** - `git diff --stat data/processed/` must show no change in other
   elections' files except `ballots_long.csv.gz`; in `reports/` only the new election's
   page and `index.html` may change.
8. **Excel check** - `python scripts/check_excel.py data/processed/knesset_<N>_<year>.xlsx`
   must report 0 error cells.
9. **Report check** - `node scripts/check_reports.js <scratchpad>/reports` must print `ok`
   for every page (for `index.html` this includes the party lookup and a check that each
   list's settlement votes add up to its national votes). Look at the screenshots of the new election's page and of `index.html`
   (desktop and mobile) for overlapping labels or broken layout.
10. **Docs** - run `python scripts/summarize_elections.py` and paste the table into
   `HANDOFF.md`; add the raw files to the table in `data/README.md`; update the HANDOFF
   status, open questions (unknown columns, unverified names) and next steps.
11. **Commit and push** - one commit, message `Add Knesset <N> (<year>) results`, listing
    the raw files, the party table, the report and any script change.
12. **Report to the user** in Hebrew, with these sections: files and names, checks
    passed, seats vs. official result, key facts (from the summary table), the report
    file, anything unusual or unverified (including proposed blocs for new lists).

## HTML reports

- Generated only by `scripts/build_reports.py` (called by `build_data.py`) from the
  template `scripts/templates/report.html`. Never edit `reports/*.html` by hand.
- `reports/knesset_<N>_<year>.html` - one per election: turnout and vote tiles, seats by
  bloc (with the 61 majority line), seats per list, and a table of every list with votes,
  share, a threshold marker, passed / not passed and seats.
- `reports/index.html` - all elections: a selector to view one election, and a comparison
  tab with seats or vote share by bloc or by party family per election, plus an average
  over the elections the user ticks (party averages only over elections the party ran in),
  and a party lookup tab: type ballot letters (`מחל`), a party name or a list leader, pick
  a suggestion, and see every election the party (`family`) ran in (letters, name, #1,
  votes, share, passed, seats), other lists with the same letters, and its share or votes
  in every settlement per election (filter, minimum size, sort by column). Only
  `index.html` carries the per-settlement data (about 1.2 MB).
- Pages are self-contained (data inlined, no external scripts), RTL Hebrew, work in light
  and dark mode and at phone width.
- Bloc colors are fixed per bloc (right, haredi, center-left, arab in that order, other
  gray); they were checked with the dataviz palette validator. Do not reorder them.

## Modeling rules

- Never report in-sample error as model quality. Select/fit on elections up to `t`,
  evaluate on `t+1`.
- Report L1 error in percentage points on shares of valid votes, and seat error where
  relevant.
- Always compare against baselines (random sample, all regular boxes, MILP/greedy).
- Fix random seeds; record solver time limits and `λ` with every result.

## Code

- Python, `pandas`; keep dependencies in `requirements.txt`.
- Library code in `src/election_estimation/`, runnable entry points in `scripts/`,
  generated reports in `reports/`.
- Match the style of `scripts/build_data.py`: short docstrings, type hints, asserts for
  data invariants.

## Usage limits

- Follow the `save-usage` skill (`.claude/skills/save-usage/`, generic, copied as is
  between projects) for heavy tasks: narrow reads, short output, background builds,
  subagents only when they pay off. It also holds the official limit rules (plans,
  Claude Code, API) as of 2026-10-30.
- `python scripts/build_data.py` takes over 2 minutes and rewrites all workbooks: run it
  once per change, in the background, and read only its summary lines. Report-only
  changes need just `python scripts/build_reports.py`.
- Never open `reports/index.html` (about 1.3 MB) or `data/processed/ballots_long.csv.gz`
  (about 56 MB) whole; query them with scripts.
- `scripts/check_excel.py` is slow: check only the workbooks that changed.
  `scripts/check_reports.js` prints a line per page: filter with `grep -c ": ok"` and
  `grep FAIL`.
- Read `HANDOFF.md` by section (`grep -n "^#"`, then `sed -n`).

## Git

- Work on the session's designated branch; commit with clear messages and push.
- No pull requests unless the user asks.
