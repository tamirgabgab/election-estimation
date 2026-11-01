# How the Knesset 27 estimate is made: theory, algorithms and formulas

This document explains, end to end, how the recommended ballot-box panels for Knesset 27
are chosen and how the election-night forecast is computed from them: the statistical
theory behind each step, the algorithms, the exact formulas, how everything was
validated, and what it assumes. The code is in `src/election_estimation/sector.py`
(model), `scripts/recommend_sector_panels.py` (panels), `scripts/templates/panels.html`
(election-night calculator, a JavaScript mirror of the model) and
`scripts/match_k27_boxes.py` (linking the K27 polling stations). Results are in
`reports/sector_*.md`. Decision numbers (M*, D*) refer to `HANDOFF.md`.

Contents:

1. The problem
2. Data and units
3. Why a fixed weighted panel is not enough
4. The sector ratio model in one page
5. Before election day: the prior
6. Sectors: weighted k-means
7. The panel: stratified PPS sampling
8. How many areas per sector: Neyman allocation under a vote budget
9. The box to count in each area
10. On the night: the estimator
11. From votes to seats: Bader-Ofer
12. Uncertainty: the within-sector bootstrap, intervals, P(pass), P(61)
13. The seat point near the threshold: the medoid
14. Validation: how the numbers were measured
15. What did not help
16. The Knesset 27 pipeline in practice
17. Assumptions and limitations
18. Symbols

---

## 1. The problem

On election night, the boxes of a small, pre-chosen panel are counted first. From their
votes we want the final seat distribution of the 120 seats.

- **Target.** The total of the *regular* ballot boxes. Double envelopes (soldiers,
  diplomats, prisoners, hospitals; settlement code 9999) are about 10% of the votes but
  have no place, so no panel can sample them (M10). The seats are computed from the
  regular-box total.
- **Budget.** At most 2% of the valid votes of the last election (K26: 104,827 votes),
  so that the panel is small enough to be counted and reported early. Panels are also
  given at 1% and 1.5%.
- **Main metric: seats moved.** For a predicted seat vector `ŝ` and the true `s`,

  ```
  seats moved = ½ Σ_l |ŝ_l − s_l|
  ```

  the number of seats that would have to move between lists to reach the truth. The
  goal set by the user is at most 2.
- **Secondary metric:** share L1, `Σ_l |p̂_l − p_l|` in percentage points.

## 2. Data and units

- **Results** per ballot box from the Central Elections Committee, Knesset 16-26
  (`data/raw`, built by `scripts/build_data.py`). Knesset 26 is provisional (D14).
- **Statistical areas.** Every regular box is placed in a CBS 2011 statistical area
  (`data/processed/ballot_areas.csv`, `scripts/build_areas.py`): K19-K25 from the
  Israel-Elections-Map project; K26 through K25 - first the K25 box with the same
  settlement and number, then the same polling center (`ריכוז`), else the whole
  settlement (`loc:<code>`) (M41). On K25 linked through K24, where the true areas are
  known, the number is right for 99.8% of the boxes it covers, the center for 72.5%.
- **Why areas.** Box numbers change between elections, settlements are too coarse (a city
  is one unit), while an area is small (about 4-5 boxes), stable across elections and
  homogeneous. About 2,600 areas cover the country.
- **Lists across elections.** Each list has a `family` (`data/parties/`); a list
  *continues* a previous one when its family ran as exactly one list in both elections
  and had at least 1% before (`swing.continuing`). Other lists are *new*.

## 3. Why a fixed weighted panel is not enough

The first approach (sections 1-6 of `docs/METHODOLOGY.md`) chose boxes `S` and weights
`w ≥ 0`, `Σw = 1` so that `Σ_{i∈S} w_i x_i` reproduces the national shares of past
elections (LP / greedy / MILP), and then applied the same weights to the next election.

- With `d` lists, Carathéodory's theorem guarantees an exact fit on any one election with
  at most `d` boxes, so in-sample error says nothing.
- Held out (fit on elections before `t`, test on `t`), those panels moved 2.4-3.8 seats
  on average and 5-8 in the worst election (`reports/archive/`).
- The fit on past elections does not carry over: among 100 candidate panels, the
  correlation between the error on the two previous transitions and the error on the
  next election was about 0 (`reports/sector_select.md`, M37).

So the panel is treated as a **probability sample**: its quality comes from the design
(stratification, allocation, size) and from an estimator that uses everything known
before election day, not from a fit to the past.

## 4. The sector ratio model in one page

1. **Prior** (before election day): every area has its K26 shares and its expected votes.
2. **Sectors:** the areas are grouped into 12 clusters of similar voting (k-means).
3. **Allocation:** each sector gets a number of areas, more where past changes varied
   more (Neyman), within the vote budget.
4. **Draw:** in each sector, areas are drawn with probability proportional to their
   expected votes (systematic sampling); in each, one box is counted.
5. **Estimate:** in each sector, the panel gives the turnout change and, for each list,
   the proportional change of its votes; every area of the sector is assumed to change
   the same way; summing over areas gives national votes.
6. **Seats and uncertainty:** Bader-Ofer; the panel is resampled within sectors to get
   intervals, P(pass the threshold), P(61); the seats shown are the medoid of the
   resamples.

Held out on K22-K26 at 2% (about 217 boxes): 2.21 seats moved on average, 2 or fewer in
67% of the panels, worst election 2.9; 90% intervals hold the true seats of 97% of the
lists (`reports/sector_model.md`).

## 5. Before election day: the prior

For the new election `t` and the previous one `t−1`, for every area `a` of `t`:

```
n_a        = number of regular boxes of a in election t        (polling station list)
c_{a,l}    = votes of list l in a in t−1
V_a        = Σ_l c_{a,l}                     (previous valid votes)
b_a        = boxes of a in t−1
v̄_a        = V_a / b_a                       (previous votes per box)
m_a        = n_a · v̄_a                       (expected votes of a in t)
p_{a,l}    = c_{a,l} / V_a                   (previous shares)
```

- An area of `t` that did not exist in `t−1` takes the shares and votes per box of all
  previous areas of its settlement; if the settlement is new, the national ones.
- For Knesset 27, `n_a` should come from the K27 polling station list; until it is
  published, the K26 box counts stand in (D17). `scripts/match_k27_boxes.py` links that
  list when it arrives (section 16).
- Shares are carried in the list space of the new election: `p_{a,l}` is the previous
  share of the list that `l` continues, and 0 for a new list.

Sector aggregates (for a sector `s` of areas `𝒜_s`):

```
M_s     = Σ_{a∈𝒜_s} m_a                       (expected votes)
P_{s,l} = Σ_{a∈𝒜_s} m_a p_{a,l} / M_s          (previous shares, weighted by expected votes)
```

## 6. Sectors: weighted k-means

The areas are clustered on their previous voting profile:

```
x_a = ( p_{a,l} for the lists l with at least 1% nationally ,  1 − Σ those )
```

**Weighted k-means** with `k = 12` minimises

```
Σ_a m_a ‖x_a − μ_{g(a)}‖²
```

over the assignment `g` and the centres `μ_j` (`sector.kmeans`): start with k-means++
(the first centre drawn with probability ∝ `m_a`, each next one ∝ `m_a · D(a)²`, the
squared distance to the nearest centre), then alternate *assign each area to the nearest
centre* and *move each centre to the weighted mean of its areas* until the centres stop
moving (at most 100 rounds). The seed is fixed (0), so the sectors are reproducible.

Clusters with less than 2% of the expected votes are merged into one "small" sector. Each
sector is named by its two largest lists and their shares (e.g. `רע"מ 81% · הרשימה
המשותפת 15%`).

Why clusters and not blocs: sectors by dominant bloc (right / Haredi / center-left /
Arab, pure at 60%) moved 2.41 seats at 2%; k-means sectors with the ratio estimator 2.23
(`reports/sector_variants.md`, M40). 8, 16 or 20 clusters were within the noise of 12.

## 7. The panel: stratified PPS sampling

Inside each sector the panel is a **systematic sample with probability proportional to
size (PPS)**, size = expected votes `m_a`:

1. Sort the areas of the sector by the previous share of the sector's main bloc (implicit
   stratification: the draw is spread from one end of the sector to the other).
2. Lay the areas on a line, area `a` taking a segment of length `m_a`; total `M_s`.
3. With `n_s` areas to draw, step `Δ = M_s / n_s`; draw a start `u ~ U(0, Δ)`; take the
   areas under the points `u, u + Δ, u + 2Δ, …`.

The inclusion probability of area `a` is

```
π_a = n_s · m_a / M_s
```

(an area longer than `Δ` can be hit twice; it then counts twice). With PPS, the plain
mean over the drawn areas of any per-vote quantity `z_a` is an unbiased estimate of its
expected-vote-weighted sector mean:

```
E[ (1/n_s) Σ_{a∈A_s} z_a ] = Σ_{a∈𝒜_s} (m_a / M_s) z_a
```

(Hansen-Hurwitz). This is why the estimator below uses unweighted panel means.

**Alternatives.** The three alternatives of a budget use the same random starts shifted
by a third of the step (`u`, `u + Δ/3`, `u + 2Δ/3`, modulo `Δ`): each is a valid PPS
sample and they share only 2-12% of their areas (`sector.draw(offset=…)`).

Sorting by the first principal component of the list shares, or a two-component "snake",
did not improve on the bloc sort (`reports/sector_design.md`).

## 8. How many areas per sector: Neyman allocation under a vote budget

The cost of an area is the votes of the one box counted in it, `v̄_a`; the expected cost
of one draw in sector `s` is `c_s = Σ_a m_a v̄_a / M_s`. The budget is
`B = β · Σ_a V_a` (β = 1%, 1.5% or 2% of the previous valid votes).

The variance of the sector total estimated from `n_s` areas is about `M_s² σ_s² / n_s`,
where `σ_s²` is the variance contributed by one drawn area. Minimising `Σ_s M_s² σ_s² / n_s`
subject to `Σ_s n_s c_s = B` (Lagrange) gives the **Neyman allocation with costs**:

```
n_s = B · (M_s σ_s / √c_s) / Σ_r (M_r σ_r √c_r)
```

then `n_s` is floored, kept at least 3 and at most the number of areas of the sector.

**Estimating `σ_s`** (`sector.list_spread`). The current sector labels are applied to the
areas of every past transition `k−1 → k` (k ≤ t−1). For every box `i` of election `k` in
an area `a` of sector `s`:

```
r_i = votes_i / v̄_a                       (turnout ratio of the box)
z_i = r_i (q_i − p_a)                      (list changes, q_i the box's shares)
σ_s²(k) = Var_w(z_i) summed over lists  +  Var_w(r_i) · ‖P_s − P‖²
```

with vote-weighted variances inside the sector and `P` the national previous shares (a
turnout error matters in proportion to how different the sector is from the country).
`σ_s²` is the mean over transitions. An alternative that simulates the seat error of past
transitions directly (`allocate(spread="empirical")`) was also tested (section 15).

At 2% this gives about 217 areas in 11 sectors (e.g. 49 in the Yashar! / Likud cluster,
32 in the Joint List / Ra'am cluster, 4 in the smallest).

## 9. The box to count in each area

In each drawn area one box is counted. The recommended box is the K26 box whose shares
are closest to its area's shares in L1,

```
box*(a) = argmin_{i ∈ a} Σ_l | q_{i,l} − p_{a,l} |
```

and the next two closest are the backups. When the K27 list is linked, the box with the
same number in the same area comes first, then boxes of the same polling center, then
the box closest in eligible voters (`match_k27_boxes.pick_boxes`). In the validation the
box is random (the conservative case), so the published accuracy does not rely on the
choice of the recommended box.

## 10. On the night: the estimator

For sector `s`, the counted areas `A_s` (each with multiplicity `w_a`, usually 1), and in
area `a` the counted box with valid votes `u_a` and shares `q_{a,l}`:

```
r_a = u_a / v̄_a                                   turnout ratio of the box
R_s = Σ_{A_s} w_a r_a / Σ_{A_s} w_a               turnout of the sector (vs. its previous votes per box)
```

**Ratio estimator** (lists with `P_{s,l} ≥ 0.5%`):

```
ŝ_{s,l} = P_{s,l} · ( Σ_{A_s} w_a r_a q_{a,l} ) / ( Σ_{A_s} w_a p_{a,l} )
```

the previous share of the list in the sector times the ratio of its current to its
previous strength in the panel areas. If a list has twice its previous share in the panel
areas, it is assumed to have twice its previous share in the whole sector. Under PPS the
numerator estimates `Y_{s,l} / M_s` (current votes of `l` per expected vote) and the
denominator `P_{s,l}`; the ratio cancels much of the area-to-area variation because a
list's current and previous strength are strongly correlated across areas.

**Difference estimator** (small lists, `P_{s,l} < 0.5%`, and new lists, `P_{s,l} = 0`):

```
ŝ_{s,l} = R_s P_{s,l} + Σ_{A_s} w_a r_a (q_{a,l} − p_{a,l}) / Σ_{A_s} w_a
```

the previous share plus the panel's mean change; for a new list this is its mean level
in the panel.

**Sector and national votes.** Negative values are set to 0 and the sector's shares are
normalised:

```
Ŷ_{s,l} = R_s · M_s · ŝ_{s,l} / Σ_l ŝ_{s,l}
Ŷ_l     = Σ_s Ŷ_{s,l}          p̂_l = Ŷ_l / Σ_l Ŷ_l
```

A sector with no counted area keeps its previous result, `Ŷ_{s,l} = M_s P_{s,l}`; the
calculator then warns (section 16).

**Why it works.** Two effects dominate the change between elections: turnout differs by
sector (e.g. in the Arab sector it moved by more than 20% between K21, K22 and K23), and
lists gain or lose roughly in proportion to their previous strength within a group of
similar areas. The model measures both per sector. Reading every area in full (a census)
leaves 0.2 seats of error, so the model's assumptions are nearly unbiased; the rest is
sampling (1.8 seats from which areas are drawn, 0.6 from reading one box per area;
`reports/sector_diagnosis.md`). Without the turnout term the error at 2% was 4.2 seats;
without sectors 4.7.

## 11. From votes to seats: Bader-Ofer

`metrics.bader_ofer` (reproduces the official seats of every election, `tests/test_metrics.py`):

1. **Threshold.** Lists with less than 3.25% of the valid votes (K20 onward) get no seats;
   "other" (lists under 1% merged) never passes.
2. **Surplus agreements.** Pairs of passing lists that signed an agreement are merged into
   one group.
3. **D'Hondt over groups.** 120 seats; each seat goes to the group with the largest
   quotient `votes / (seats so far + 1)`.
4. **Inside a pair.** The pair's seats are split again by D'Hondt.

## 12. Uncertainty: the within-sector bootstrap, intervals, P(pass), P(61)

The panel's own spread is estimated by the **bootstrap within sectors**: in each sector,
draw `|A_s|` areas with replacement from the counted ones (multiplicities expanded),
predict, and repeat 200 times (`sector.bootstrap`; the calculator uses the same scheme
with a fixed seed). Resampling inside sectors keeps the stratification, so the bootstrap
variance mimics the design variance.

From the replicates `b = 1…200`, with seats `s^{(b)}` and shares `p^{(b)}`:

```
90% interval of list l   = [5th, 95th percentile of s_l^{(b)}]
P(l passes)              = share of replicates with p_l^{(b)} ≥ 3.25%
P(set G has a majority)  = share of replicates with Σ_{l∈G} s_l^{(b)} ≥ 61
```

The calculator shows P(61) for every bloc, for right + Haredi and center-left + Arab, and
for any set of lists the user ticks (coalition builder).

Held out, the 90% intervals hold the true seats of 96-97% of the lists, with 0.15-0.18
seats outside them on average (`reports/sector_model.md`).

## 13. The seat point near the threshold: the medoid

A list near 3.25% makes the seat vector jump by about 4 seats. Instead of the seats of the
direct estimate, the forecast shows the **medoid** of the bootstrap seat vectors:

```
ŝ = argmin_{c ∈ {s^{(1)}, …, s^{(B)}}}  Σ_b ‖c − s^{(b)}‖₁
```

the replicate that minimises the expected seats moved against the resampling
distribution (a Bayes point under L1 loss, restricted to valid seat vectors so that it
always sums to 120). Held out at 2% it moved 2.21 seats against 2.28 for the direct
point; it helped most in K22 and K23 (1.94 → 1.65, 1.74 → 1.55) and was about even in the
other elections (with the earlier bloc sectors it helped most in K25, the election with
Balad near the threshold: 2.95 → 2.35).

## 14. Validation: how the numbers were measured

- **Rolling held-out protocol.** For each test election `t ∈ {22, …, 26}`: the prior uses
  `t−1` and the box counts of `t`; the sectors, the allocation and every choice use only
  elections before `t`; the panel is then read in `t`. Nothing about `t` other than its
  box counts is used.
- **Many panels.** 100 panels per test election and budget, each read through one random
  box per area; 20 of them also bootstrapped for the medoid and the intervals.
- **Reported numbers.** Mean seats moved, the share of panels with at most 2, the worst
  test election's mean, interval coverage, seats outside the interval.
- **Seeds** are fixed in every script; results are in `reports/sector_*.md` with their
  settings.

Results of the model in use (`reports/sector_model.md`):

| Budget | Boxes | Seats moved (medoid) | At most 2 | Worst election | 90% coverage |
|---|---|---|---|---|---|
| 1% | 108 | 3.16 | 38% | 4.0 | 96% |
| 1.5% | 162 | 2.43 | 61% | 3.4 | 97% |
| 2% | 217 | 2.21 | 67% | 2.9 | 97% |

Partial counts (`reports/sector_partial.md`, 2%, earlier bloc sectors): a random 90% /
70% / 50% of the panel gives 2.5 / 2.9 / 3.4 seats; half of the Arab-sector areas 2.7;
**no Arab-sector area at all 10 seats on average (up to 14)** - the reason for the
calculator's red warning.

## 15. What did not help

All held out on K22-K26, same seeds; numbers are seats moved at 2%.

| Idea | Result | Report |
|---|---|---|
| Fixed weighted panels (LP / greedy / MILP), swing, joint and within-bloc panels | 2.4-3.8, worst 5-8 | `reports/archive/` |
| Choosing a panel by its fit on past elections | correlation ≈ 0 | `sector_select.md` |
| Sectors by dominant bloc | 2.41 | `sector_variants.md` |
| List-level spread alone; ratio alone | 2.49; 2.42 | `sector_variants.md` |
| GREG calibration to all previous shares (+ ratio) | 2.31-2.36 (2.22) | `sector_variants.md` |
| Sorting by principal components, snake | 2.26, 2.32 (vs 2.24) | `sector_design.md` |
| Two boxes per area, half the areas | 2.59 | `sector_design.md` |
| Pooling other sectors for a missing one | 9.4 vs 10.1 | `sector_partial.md` |
| Neural area model (PyTorch correction on top) | 2.41 vs 2.30 | `neural.md` |

The pattern: the design and the estimator are near their limit at this budget; what is
left is mostly the sampling noise of about 200 areas.

## 16. The Knesset 27 pipeline in practice

```
data/raw (K19-K26) ──build_data.py──► data/processed + ballot_areas.csv
                                         │
K27 polling station list ──match_k27_boxes.py──► k27_boxes_linked.csv (D17)
                                         │
run_sector_heldout.py ──► reports/sector_model/ (held-out accuracy per budget)
                                         │
recommend_sector_panels.py ──► k27_panels/sector_final.json
   prior from K26 · k-means sectors · Neyman allocation · 3 budgets × 3 alternatives ·
   box + 2 backups per area · per-sector data for the calculator
                                         │
build_panels_site.py ──► reports/knesset_27_panels.html (+ private link)
check_panels_site.py / check_all.sh ──► JS seats = Python seats on every panel
```

**On the night** (`docs/ELECTION_NIGHT.md`): load the committee's per-box files into the
calculator (several files add up, later counts win); it picks each panel area's box or a
backup, merges lists under 1% into "other", adds new lists of 1% or more; computes
`R_s`, the ratio / difference estimates, the bootstrap, the medoid seats, intervals,
P(pass) and P(61); and shows the counted areas per sector with a red warning for a
sector with none and a note for a sector with fewer than half.

## 17. Assumptions and limitations

- **Within-sector homogeneity.** Every area of a sector is assumed to change like the
  panel areas of that sector (proportionally per list). Census error 0.2 seats says this
  held in K22-K26; a new kind of local shift (e.g. a party strong in a few towns that do
  not form a sector) would break it.
- **New lists** start from their panel level per sector, with no prior; a new list near
  the threshold is the hardest case (K25).
- **Box counts of K27** are taken from K26 until the polling station list is out (D17).
- **K26 is provisional** (D14) and is the base of everything for K27.
- **Double envelopes** are outside the target; the official result includes them.
- **The reporting order on the night** matters only through missing sectors; a random
  70% of the panel costs about 0.5 seats, a missing sector up to 14.
- **Five test elections** is a small sample of elections; the worst-election numbers carry
  that uncertainty.

## 18. Symbols

| Symbol | Meaning |
|---|---|
| `a`, `𝒜_s`, `A_s` | an area; all areas of sector `s`; the counted (panel) areas of `s` |
| `l` | a list of the new election |
| `n_a`, `b_a` | boxes of `a` in the new / previous election |
| `V_a`, `v̄_a` | previous valid votes of `a`; previous votes per box |
| `m_a`, `M_s` | expected votes of `a`; of sector `s` |
| `p_{a,l}`, `P_{s,l}`, `P` | previous shares of `a`; of sector `s`; national |
| `u_a`, `q_{a,l}` | votes and shares of the counted box of `a` |
| `r_a`, `R_s` | turnout ratio of the counted box; of the sector |
| `w_a` | times `a` was drawn (usually 1) |
| `ŝ_{s,l}`, `Ŷ_{s,l}`, `p̂_l` | estimated share and votes of `l` in `s`; national share |
| `n_s`, `c_s`, `σ_s`, `B` | areas drawn in `s`; cost per draw; spread per area; vote budget |
| `π_a` | inclusion probability `n_s m_a / M_s` |
| `s^{(b)}`, `ŝ` | seats of bootstrap replicate `b`; the medoid seats |
