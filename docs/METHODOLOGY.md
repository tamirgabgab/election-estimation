# Methodology

## 1. Problem

Pick a small set of sample ballot boxes `S` and weights `w` so that their results
estimate the final national result.

```
min_{S, w}   || y - Σ_{i∈S} w_i · x_i ||_1   +   λ · |S|
s.t.         w_i ≥ 0
```

- `x_i` - party share vector of ballot box `i` (shares of valid votes).
- `y` - final national share vector.
- `||·||_1` - L1 error, reported in percentage points (pp).
- `λ` - regularization: the cost of adding one more ballot box to the sample.

## 2. Pitfalls found so far

1. **In-sample fitting is meaningless.** With `d` party dimensions, Carathéodory's
   theorem guarantees an exact fit with at most `d` ballot boxes. On Knesset 25
   (14 dimensions) the solver indeed reached 0 error with 14 boxes, all of them
   extreme, unrepresentative places. **Select on election `t`, evaluate on `t+1`.**
2. **LASSO does not give sparsity here.** If weights are non-negative and sum to 1,
   `Σ w_i = 1` is constant, so an L1 penalty on `w` does nothing. Use a binary
   selection variable per box (MILP), a greedy method, or an L0 relaxation.
3. **Double envelopes bias.** Soldiers, diplomats, prisoners and hospitals vote in
   "double envelopes" (settlement code 9999). They have no location, so they cannot
   be sampled, yet they are 9.6% of valid votes in Knesset 25 and vote differently
   (Religious Zionism 15.45% vs 10.35% in regular boxes). Summing all regular boxes
   already gives 2.18 pp L1 error. The model must estimate this part separately, e.g.
   `ŷ = (1 - α)·ŷ_regular + α·ŷ_envelopes`, with `α` and `ŷ_envelopes` from past elections.

## 3. Models, in order (the original plan; see section 7 for the model in use)

1. **Baselines** - random sample of `k` boxes; all regular boxes (lower bound of
   the envelope bias).
2. **Level model (MILP)** - binary `z_i` (box selected), continuous `w_i ≤ M·z_i`,
   L1 error linearized with auxiliary variables, penalty `λ·Σ z_i`. Greedy forward
   selection as a fast heuristic.
3. **Swing model** - predict the change from the previous election instead of the level.
   Usually generalizes much better:
   ```
   ŷ_{t+1} = y_t + Σ_{i∈S} w_i · (x_{i,t+1} - x_{i,t})
   ```
4. **Neural network** - per-box learnable gate with a Hard-Concrete (continuous L0)
   relaxation, so `λ · E[#open gates]` is differentiable. Input: results of the
   sampled boxes plus settlement features (size, region, past results). Output:
   national shares. Compare against the MILP and swing baselines.

## 4. Parties that change between elections

Lists merge, split, appear and disappear (Meretz is gone, new lists appear). Options,
from simplest to most advanced:

1. **Level model, no mapping** - weights belong to ballot boxes, not to parties, so
   each election can keep its own lists. What is needed instead is matching ballot
   boxes across elections.
2. **Lineage mapping per pair of elections** (for the swing model) - a small manual CSV
   linking lists of election `t` to lists of `t+1`. Each connected component of this
   bipartite graph becomes one merged category, e.g. {Blue and White, New Hope} →
   {National Unity}.
3. **Blocs** - right, center-left, Haredi, Arab, other. Coarse but stable over decades;
   a good robustness metric.
4. **Advanced** - learned vote transitions (ecological inference) or a latent space
   (PCA/NMF) shared by all elections.

## 5. Evaluation

- **Protocol** - select and fit on elections up to `t`, test on `t+1` (rolling).
- **Metrics** - L1 error on shares (pp), and also seat error after the threshold
  (3.25%) and Bader-Ofer allocation. Threshold effects matter: Meretz got 3.16% in
  Knesset 25 and won no seats.
- **Choosing λ** - plot the Pareto curve of test error vs. number of boxes and pick
  the knee.

## 6. Knesset 25 experiment (in-sample, for illustration only)

13 lists above 1% plus "other" (14 dimensions). Mean L1 error in pp:

| Boxes | Random (500 draws) | Greedy | MILP (90 s limit) |
|------:|-------------------:|-------:|------------------:|
| 1     | 86.55 | - | - |
| 3     | - | 8.44 | 3.72 |
| 5     | - | 4.20 | 1.44-1.54 |
| 8     | - | 1.03 | 0.17 |
| 10    | 32.97 | - | - |
| 14    | - | 0.00 | - |
| 100   | 10.41 | - | - |
| 1000  | 3.82 | - | - |
| 3000  | 2.73 | - | - |

Random sampling flattens at about 2.2 pp because of the envelope bias. The optimized
selections are overfit (see pitfall 1) and are not expected to hold on another election.

## 7. The sector ratio model (in use since 2026-10-31)

The fixed weighted panels of sections 3-6 did not carry over between elections: held
out on Knesset 22-26 they moved 2.4-3.8 seats, the worst election 5-8, and choosing a
panel by how well it fit past elections did not help (the correlation between past and
future fit was about 0). The sector ratio model (`src/election_estimation/sector.py`)
takes a sampling view instead.

**Target.** The total of the regular boxes; double envelopes cannot be sampled (M10).

**Units and prior.** Statistical areas (CBS 2011; a settlement without areas is one
unit). Before election day every area has its previous result and its expected votes:
its number of boxes in the new election times its previous votes per box. A new area
takes its settlement's previous shares and votes per box.

**Sectors.** Weighted k-means (12 clusters) on the previous list shares of the areas
(lists of 1% or more, the rest summed); clusters under 2% of the votes are merged.
Each sector is named by its two largest lists.

**Panel.** In every sector, a systematic draw with probability proportional to the
expected votes, one box counted per area. Sector sample sizes follow a Neyman allocation
under a vote budget (cost of an area = the votes of one box): more areas where the
changes seen by one box varied more in past transitions (list-level variance plus
turnout variance times the sector's distance from the national mix). Three alternatives
per budget come from the same draw with the start shifted by a third of the step.

**Estimator.** In sector `s` with counted areas `A`, area `a` read through one box with
shares `q_a`, turnout ratio `r_a` (box votes / previous votes per box) and previous
shares `p_a`:

```
R_s     = mean_A r_a                                  (turnout of the sector)
share_l = P_{s,l} · (Σ_A r_a q_{a,l}) / (Σ_A p_{a,l}) (ratio, lists with P_{s,l} ≥ 0.5%)
share_l = R_s P_{s,l} + mean_A r_a (q_{a,l} - p_{a,l}) (difference, other and new lists)
votes_{s,l} = R_s · M_s · share_l / Σ_l share_l
```

`P_{s,l}` is the sector's previous share and `M_s` its expected votes. A new list starts
from zero (its panel level). A sector with no counted area keeps its previous result.

**Seats and uncertainty.** Bader-Ofer with the surplus agreements. The panel is
resampled within sectors (200 replicates) for 90% seat intervals and P(pass the
threshold); the seats shown are the medoid of the replicates (the seat vector with the
least mean distance to the others), which helps when a list is near the threshold.

**Held-out results** (`reports/sector_model.md`; 100 panels per test election and budget):

| Budget | Boxes | Seats moved (medoid) | Within 2 | Worst election | 90% coverage |
|---|---|---|---|---|---|
| 1% | 108 | 3.16 | 38% | 4.0 | 96% |
| 1.5% | 162 | 2.43 | 61% | 3.4 | 97% |
| 2% | 217 | 2.21 | 67% | 2.9 | 97% |

**Where the error comes from** (`reports/sector_diagnosis.md`, bloc sectors, 2%): reading
every area in full leaves 0.2 seats (the model's own bias); the choice of areas adds 1.8
and reading one box per area 0.6. Turnout per sector is the largest single gain over
the earlier models (without it 4.2 seats).

**Partial counts** (`reports/sector_partial.md`): a random 90% / 70% / 50% of the panel
gives 2.5 / 2.9 / 3.4 seats; with no Arab-sector area counted the error is 10 seats on
average, so the calculator warns when a sector has no counted area.

**Variants tried** (`reports/sector_variants.md`, `reports/neural.md`): sectors by
dominant bloc (2.41 seats at 2%), the difference estimator, 8-20 clusters (within the
noise of 12), and a neural correction per area (PyTorch; 2.41 vs 2.30 on the same
panels, worse in Knesset 25) - none better than the model above.
