# Model plan: a fixed panel of representative ballot boxes

Status: agreed design, not yet implemented. Last updated 2026-10-30.

## 1. Goal

Choose a fixed panel of about 50–70 base ballot boxes (order of sqrt of the
number of localities, 1,215) and a weight per box, such that the weighted
average of the panel's vote shares predicts the national result of a
**future** election as closely as possible, both in party shares and in
Knesset seats. On election night only the panel boxes need to be counted.

Deliverable: a table `(settlement_code, base_box, weight)` plus a report of the
expected error on held-out elections.

## 2. Decisions taken

| Decision | Choice | Reason |
|---|---|---|
| Unit of selection | CBS statistical area, or the settlement where there are no areas (M7) | Base boxes are renumbered in K24 and do not persist; areas are stable geography |
| Usage scenario | Fixed panel chosen in advance | Must generalize to elections not seen in training |
| Prediction form | Fixed weight per box, convex combination | Transparent, works for new parties, robust with ~10 training elections |
| Loss | L1 on party shares + α·L1 on seats + β·L1 on bloc shares + L0 penalty on panel size; seats weigh most (M8) | Seats per list are the primary target; shares and blocs stabilize training |
| Party handling | No cross-election party mapping for the main model; blocs for the bloc terms | Weights belong to boxes, not parties |
| Double envelopes | Part of the national target, never selectable | The model compensates through its box weights |

## 3. Data

All eleven elections, Knesset 16 (2003) to Knesset 26 (2026), are in the
repo. Raw files are in `data/raw/`, and `scripts/build_data.py` validates them
and writes `data/processed/knesset_<N>/{ballots,settlements,national}.csv`.
Sources, layouts and caveats are in [data/README.md](../data/README.md);
`election_estimation.data` loads the processed tables for modelling.

| Knesset | Status |
|---|---|
| 16 | Regular boxes only; envelopes row = official totals minus boxes |
| 17–18 | From the Yoavfried project (built from the official package) |
| 19–25 | Official committee files |
| 26 | Provisional; replace with the certified files (expected ~4 Nov 2026) |

Thresholds differ: 1.5% (K16), 2% (K17–19), 3.25% (K20 onward). The
threshold and surplus agreements of each election are in `ELECTIONS` in
`scripts/build_data.py`, and the seat allocation reproduces the official
result of every election.

### 3.1 Box matching across elections

The weakest assumption in the design is that a base box keeps its identity.
Matching key: `(settlement_code, base box number)`, the `base_box` column of
`election_estimation.data.load_ballots`. Required measurements before
modelling:

- Survival rate of base boxes between consecutive elections.
- Size drift: change in eligible voters for matched boxes.
- Fallback for unmatched boxes: aggregate to settlement level.

If survival is poor, switch the unit to the settlement for small settlements
and to CBS statistical areas for large cities.

Findings (2026-10-30, `reports/box_matching.md`, `election_estimation.matching`):

- Keys survive well from K16 to K23 (87–99% of votes per consecutive pair).
  Knesset 16–17 number boxes ten times larger (61, 62 = box 6 split), which the
  loader normalizes.
- K24 (2021) reorganized the numbering: base boxes fell from 9,388 to 5,614,
  and a base box became a group of alphabetical sub-boxes (about 1,170
  registered voters on average instead of about 690). K23→K24 vote survival is
  56%, K24→K25 74%, K25→K26 84%.
- Matched keys usually name the same place, but not always: after removing
  the national bloc swing, a box is closer to its namesake than to a random box
  of the same settlement in 74–88% of pairs.
- A box key present in every election of a long window is rare: base boxes
  that exist in all of K16–K25 hold 42% of K25's votes, and for K26 the figure
  is 31%.
- Settlement codes survive almost completely (99–100% of votes).

Conclusion: the base box is not a stable unit across the whole period, and its
size changes after K23.

Decision (M7): the sampling unit is the CBS statistical area (2022 areas),
and the whole settlement where a settlement has no areas. Ballot boxes of
K16–K25 are mapped to areas by the Yoavfried/Israel-Elections-Map project;
K26 boxes are mapped through their K25 namesakes. On election night one
representative ballot box is counted per panel area (M9), so held-out
evaluation must simulate reading a single box of each area, not the area
total. Note: the K17–K18 files already carry statistical areas of their own
vintage (1995, 2008), with about 5% of boxes unresolved; areas of different
vintages need the project's crosswalk to the 2022 areas.

### 3.2 Party metadata per election

File `data/parties/knesset_<N>_parties.csv`, one row per list, hand-maintained:

```
letter, name_he, name_en, family, bloc, verified, leader_he
```

- `letter`: ballot letters, the column name in the committee files.
- `family`: the same party across elections.
- `bloc`: one of `right`, `center_left`, `arab`, `haredi`, `other`.

Bloc decisions and open bloc questions are tracked in `HANDOFF.md`.

## 4. Blocs

Blocs are the only party-level concept that is stable across 20 years, so
they serve four purposes.

1. **Loss term.** Bloc shares and bloc seats are predicted by aggregating
   the party prediction, and their L1 error enters the loss with weight β.
   This pushes the panel to get the right/center-left/arab/haredi balance
   right even when individual party errors cancel.
2. **Evaluation.** Every report shows party-level, bloc-level and seat
   errors side by side.
3. **Stratification.** The stratified baseline samples boxes by their bloc
   profile (dominant bloc, bloc entropy), by settlement size and by district.
4. **Diagnostics.** The chosen panel is described by its bloc composition
   and compared with the national one.

Assignment rules (decided):

- Lists are assigned by **ideology** on the right/left axis, not by the
  coalition camp they joined in a given election. Example: Yisrael Beiteinu
  is `right` although it sat in the anti-Netanyahu camp in 2022.
- National Unity (Gantz, K25) is `center_left`; Yashar! (Eisenkot, K26,
  letters `דרך`) is `center_left`.
- Lists under 1% nationally are not assigned individually; they fall into
  `other`.

Bloc schemes are configurable. Two schemes are evaluated from the start:

- `four_blocs`: right, center_left, arab, haredi.
- `three_blocs`: haredi merged into right.

Switching schemes changes only the aggregation matrix, not the model or the
party files. A list can be re-assigned per election if its camp changes.

## 5. Model

Notation per election e: `X_e` is boxes x parties_e (shares, base boxes,
double envelopes excluded), `y_e` is the national share vector including
double envelopes, `B_e` is the parties_e x blocs aggregation matrix.

Shared parameters, one per box i, used for every election:

```
g_i ∈ [0,1]   selection gate (Hard-Concrete relaxation of a Bernoulli)
a_i ∈ R       weight logit
```

Prediction:

```
w_i   = g_i * softmax(a)_i / Σ_j g_j * softmax(a)_j
ŷ_e   = Σ_i w_i * x_{i,e}
```

Loss, summed over training elections with recency weights ρ_e (M6; recent
elections weigh more, decay tuned in validation):

```
L = Σ_e ρ_e [ ‖y_e − ŷ_e‖₁
        + α · ‖seats_soft(y_e) − seats_soft(ŷ_e)‖₁
        + β · ‖B_eᵀ y_e − B_eᵀ ŷ_e‖₁
        + γ · ‖seats_soft(B_eᵀ y_e) − seats_soft(B_eᵀ ŷ_e)‖₁ ]
  + λ · E[Σ_i g_i]            expected panel size (L0 penalty)
  + μ · Σ_i w_i²              discourages one box carrying most weight
```

`seats_soft` is a differentiable approximation: a steep sigmoid at the
3.25% threshold and proportional allocation (`metrics.soft_seats`).
Evaluation always uses the exact Bader-Ofer allocation (`metrics.bader_ofer`,
verified on K25) with the surplus agreements of each election.

After training: gates are hardened (g_i > 0.5), and the weights of the
retained boxes are refit with the exact L1 linear program
(`selection.fit_weights`) on the training elections. The network is the
search procedure; the deliverable is the weight table.

Why no mapping is needed: `x_{i,e}` and `y_e` live in the same per-election
party space, and the parameters are indexed by box only. New or vanished
parties need no special treatment. Only the bloc terms need `B_e`, which
comes from the per-election party file.

## 6. Baselines

All baselines run under the same validation protocol and panel size.

1. **Random**: k random base boxes, votes pooled. In-sample on K25,
   60 boxes give roughly 15 percentage points L1.
2. **Stratified**: k boxes sampled proportionally across strata built from
   bloc profile, settlement size and district; votes pooled.
3. **Greedy column generation** (`selection.greedy_selection`): cheap upper
   bound on the optimizable error.
4. **MILP** (`selection.exact_selection`): same objective without the
   seat/bloc terms, solved by HiGHS. Strongest classical competitor;
   restricted to a candidate pool and a time limit.

The network must beat 1–3 clearly on held-out elections and be at least
comparable with 4 to justify its complexity.

## 7. Validation protocol

In-sample numbers are meaningless: 14 boxes reproduce any single election
exactly (Carathéodory). Rolling-origin evaluation only:

| Train | Test |
|---|---|
| K16–K21 | K22 |
| K16–K22 | K23 |
| K16–K23 | K24 |
| K16–K24 | K25 |
| K16–K25 | K26 (once final) |

Metrics per fold: party L1 (percentage points), bloc L1 (both schemes),
seat L1 (Bader-Ofer), bloc seat L1, worst single-party error, and the
number of parties whose threshold status is predicted wrongly.

Hyperparameters (λ, α, β, γ, μ, learning rate, gate temperature) are tuned
with an inner split on the training elections only, never on the test
election. The primary selection metric is the seat L1 error per list (M8). The final output is a Pareto curve of held-out error against
panel size; λ is chosen where the panel has 50–70 boxes.

Expectation: 2–4 percentage points party L1 and 2–5 seats on unseen
elections would be a strong result with ~60 boxes. Much lower numbers are a
sign of leakage.

## 8. Implementation steps

1. **Data ingestion** – done for K16–K26 (`scripts/build_data.py`); replace
   K26 with the certified files when published.
2. **Box matching** – done: `election_estimation/matching.py` and
   `scripts/box_matching_report.py` (findings in 3.1). Next: decide the
   sampling unit (M7) and build the cross-election unit index for it.
3. **Party files** – done for every election (`data/parties/`); add a
   helper in `data.py` that produces `B_e` for a bloc scheme.
4. **Metrics** – done: `metrics.py` and `tests/test_metrics.py` (official
   seats of every election reproduced).
5. **Evaluation harness** – done: `evaluate.py` (rolling folds, unit as a
   parameter, whole-unit and single-box readings) and
   `scripts/run_baselines.py`; results in `reports/baselines_*.md`.
6. **Baselines** – done: random (uniform, PPS), stratified, greedy, and
   greedy / MILP under a box budget, for settlement, base-box and area units
   (`reports/baselines_summary.md`). Finding: optimized weights interpolate the
   training targets, so the network step needs weight regularization.
6b. **Regularization** – done: `weight_prior`, `calibration` and `noise` in
   `evaluate.py`, strengths by inner validation (`scripts/run_regularization.py`,
   `reports/regularization_*.md`). Bloc-profile calibration targets help area
   panels (11.2 vs 18.0 seats at 70 boxes); on base boxes plain greedy stays best
   (8.4 seats at 50 boxes). The network should use calibration targets.
7. **Network** – `election_estimation/panel_net.py` in PyTorch:
   Hard-Concrete gates, softmax weights, combined loss, hardening and LP
   refit. CPU is sufficient (6k parameters, 10 elections).
8. **Hyperparameter search** – inner validation, Pareto curve, choose λ.
9. **Analysis report** – panel composition by bloc, size and district;
   stability of the chosen panel across folds; how the panel compensates for
   double envelopes; comparison of bloc schemes.
10. **Optional extension** – swing model (predict change from the previous
    election) using a per-pair party lineage file, only if the level model
    is not accurate enough on held-out elections.

## 9. Repository layout (target)

```
data/raw/                                committee files (immutable)
data/processed/knesset_<N>/              built by scripts/build_data.py
data/parties/knesset_<N>_parties.csv     lists, families, blocs, leaders
src/election_estimation/
    data.py        loading, validation, share matrices        (exists)
    metrics.py     L1, Bader-Ofer, soft seats, blocs           (exists)
    selection.py   LP weights, greedy, MILP, random            (exists)
    matching.py    cross-election box matching diagnostics      (exists)
    evaluate.py    rolling validation harness                   (exists)
    panel_net.py   gated selection network
scripts/
    explore_knesset.py                   per-election report   (exists)
    run_baselines.py, train_panel.py, make_report.py
reports/                                 HTML results pages, model reports
```

## 10. Risks and open questions

- Box survival across 20 years may be low; fallback units are described
  in 3.1.
- Bloc assignment is a political judgement (e.g. Yisrael Beiteinu, assigned to right); keep
  it explicit in the party files and test sensitivity to the scheme.
- Double-envelope composition changes (wartime elections have more
  soldiers' votes); check the panel's compensation per fold.
- K26 files are provisional until the official publication.
- With 10 training elections the MILP may match the network; the network's
  advantage is the seat and bloc terms, so the comparison must include them.
