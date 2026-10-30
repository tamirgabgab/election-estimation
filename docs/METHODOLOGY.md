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

## 3. Models, in order

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
