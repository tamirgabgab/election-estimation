# Model plan: a fixed panel of representative ballot boxes

Status: agreed design, not yet implemented. Last updated 2026-10-30.

## 1. Goal

Choose a fixed panel of about 50–70 base ballot boxes (order of sqrt of the
number of localities, 1,215) and a weight per box, such that the weighted
average of the panel's vote shares predicts the national result of a
**future** election as closely as possible, both in party shares and in
Knesset seats. On election night only the panel boxes need to be counted.

Deliverable: a table `(locality_id, base_box, weight)` plus a report of the
expected error on held-out elections.

## 2. Decisions taken

| Decision | Choice | Reason |
|---|---|---|
| Unit of selection | Base ballot box (sub-boxes 283.1, 283.2 merged into 283) | Alphabetical splits change between elections and carry surname bias; 6,306 base boxes in K25 |
| Usage scenario | Fixed panel chosen in advance | Must generalize to elections not seen in training |
| Prediction form | Fixed weight per box, convex combination | Transparent, works for new parties, robust with ~10 training elections |
| Loss | L1 on party shares + α·L1 on seats + β·L1 on bloc shares + L0 penalty on panel size | Shares, seats and blocs are all evaluation targets |
| Party handling | No cross-election party mapping for the main model; blocs for the bloc terms | Weights belong to boxes, not parties |
| Double envelopes | Part of the national target, never selectable | The model compensates through its box weights |

## 3. Data

Source: Central Elections Committee files per Knesset, `expb.csv` (boxes)
and `expc.csv` (localities), stored under `data/raw/knesset_NN/`.

| Knesset | Year | Status |
|---|---|---|
| 16–24 | 2003–2021 | To download (data.gov.il / votesNN.bechirot.gov.il) |
| 25 | 2022 | In repo, validated |
| 26 | 2026 | Provisional only; wait for the final files (expected ~4 Nov 2026) |

Checks run on every file (already in `election_estimation.data.validate`):
party sum equals valid votes, voters equal valid plus invalid, turnout at
most 100%, locality file equals the box aggregate.

### 3.1 Box matching across elections

The weakest assumption in the design is that a base box keeps its identity.
Matching key: `(locality_id, base_box)`. Required measurements before
modelling:

- Survival rate of base boxes between consecutive elections.
- Size drift: change in eligible voters for matched boxes.
- Fallback for unmatched boxes: aggregate to locality level.

If survival is poor, switch the unit to the locality for small localities
and to CBS statistical areas for large cities.

### 3.2 Party metadata per election

File `data/parties/knesset_NN.csv`, one row per list, hand-maintained:

```
letters, name_he, name_en, bloc, surplus_partner, notes
```

- `letters`: ballot letters, the column name in the CEC files.
- `bloc`: one of `right`, `center_left`, `arab`, `haredi`, `other`.
- `surplus_partner`: letters of the list sharing a surplus-vote agreement.

The K25 file exists as a draft and needs review of ambiguous assignments
(Yisrael Beiteinu in particular).

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
   profile (dominant bloc, bloc entropy), by locality size and by district.
4. **Diagnostics.** The chosen panel is described by its bloc composition
   and compared with the national one.

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

Loss, summed over training elections:

```
L = Σ_e [ ‖y_e − ŷ_e‖₁
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
   bloc profile, locality size and district; votes pooled.
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
election. The final output is a Pareto curve of held-out error against
panel size; λ is chosen where the panel has 50–70 boxes.

Expectation: 2–4 percentage points party L1 and 2–5 seats on unseen
elections would be a strong result with ~60 boxes. Much lower numbers are a
sign of leakage.

## 8. Implementation steps

1. **Data ingestion** – download K16–K24, run `validate` on each, record
   file provenance in `data/raw/README.md`.
2. **Box matching** – `election_estimation/matching.py`: merge sub-boxes,
   build the cross-election box index, report survival and drift.
3. **Party files** – `data/parties/knesset_NN.csv` for every election,
   including surplus agreements; a loader in `data.py` that produces `B_e`.
4. **Metrics** – `metrics.py` (exists): L1, Bader-Ofer, soft seats, bloc
   aggregation. Add a test that Bader-Ofer reproduces official seats for
   every election with a party file.
5. **Evaluation harness** – `election_estimation/evaluate.py`: rolling
   folds, metric table, Pareto curve plotting. Everything downstream plugs
   into it.
6. **Baselines** – random, stratified, greedy, MILP through the harness.
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
data/raw/knesset_NN/expb.csv, expc.csv   CEC files
data/parties/knesset_NN.csv              lists, blocs, surplus agreements
src/election_estimation/
    data.py        loading, validation, share matrices        (exists)
    metrics.py     L1, Bader-Ofer, soft seats, blocs           (exists)
    selection.py   LP weights, greedy, MILP, random            (exists)
    matching.py    cross-election box index
    evaluate.py    rolling validation harness
    panel_net.py   gated selection network
scripts/
    explore_knesset.py                   per-election report   (exists)
    run_baselines.py, train_panel.py, make_report.py
reports/                                 generated markdown
```

## 10. Risks and open questions

- Box survival across 20 years may be low; fallback units are described
  in 3.1.
- Bloc assignment is a political judgement (e.g. Yisrael Beiteinu); keep
  it explicit in the party files and test sensitivity to the scheme.
- Double-envelope composition changes (wartime elections have more
  soldiers' votes); check the panel's compensation per fold.
- K26 files are provisional until the official publication.
- With 10 training elections the MILP may match the network; the network's
  advantage is the seat and bloc terms, so the comparison must include them.
