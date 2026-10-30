# Project instructions

Estimate Israeli Knesset results from a minimal sample of ballot boxes. Read
[HANDOFF.md](HANDOFF.md) first for status, and [docs/METHODOLOGY.md](docs/METHODOLOGY.md)
for the model design.

## Communication

- Chat with the user in Hebrew (RTL-safe, as in the global instructions). Code,
  comments, commit messages and docs are in English.
- Ask guiding questions before big changes (new model family, data layout changes).
- End each work round with a short summary by sections, and update `HANDOFF.md`
  (done, key facts, next steps) before committing.

## Data rules

- `data/raw/` is immutable: copy files byte-for-byte, only rename to
  `knesset_<N>_<year>_{ballots,settlements}.csv`. Never edit raw files.
- `data/processed/` is generated only by `python scripts/build_data.py`. Never edit it by
  hand; change the script and rebuild.
- A new election = raw files + an entry in `ELECTIONS` + `data/parties/knesset_<N>_parties.csv`.
  The build must pass all validation asserts and reproduce the official seat result.
- Read `ballot_id` as text (`3.10` is not `3.1`).
- Do not guess party names or facts. Mark unknowns (`verified = no`) and tell the user.
- Double envelopes (`settlement_code = 9999`, `is_envelopes`) are never sampling
  candidates, but they are part of the national target.

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

## Git

- Work on the session's designated branch; commit with clear messages and push.
- No pull requests unless the user asks.
