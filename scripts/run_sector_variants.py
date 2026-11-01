"""Held-out comparison of sector model variants (K22-K26).

Variants (sectors / Neyman spread / estimator):
- base: bloc sectors, bloc spread, difference (the current model);
- list_spread: bloc sectors, list-level spread, difference;
- ratio: bloc sectors, list-level spread, ratio estimator;
- cluster: k-means sectors (K clusters), list-level spread, difference;
- cluster_ratio: k-means sectors, list-level spread, ratio estimator;
- cluster_ratio_k<k>: the same with 8, 16 or 20 clusters;
- greg_mu<mu>: k-means sectors, weights calibrated to the previous shares of every
  list (ridge mu), level estimator; greg_ratio_mu1: calibrated, then ratio.
DRAWS panels per test, budget and variant, one random box per area, the same
seed for every variant. Writes reports/sector_variants/draws_<t>.csv and
reports/sector_variants.md.

Usage:
    PYTHONPATH=src python scripts/run_sector_variants.py [greg] [draws] [tests...]
(`greg` runs only the greg variants, into greg_<t>.csv.)
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from election_estimation.evaluate import score
from election_estimation.sector import allocate, area_election, draw, predict, prior_for, read_boxes

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "sector_variants"
BUDGETS = [0.015, 0.02]
K = 12
SEED = 4
VARIANTS = {  # name: sectors, spread, estimator, clusters
    "base": ("bloc", "bloc", "difference", K),
    "list_spread": ("bloc", "list", "difference", K),
    "ratio": ("bloc", "list", "ratio", K),
    "cluster": ("cluster", "list", "difference", K),
    "cluster_ratio": ("cluster", "list", "ratio", K),
    "cluster_ratio_k8": ("cluster", "list", "ratio", 8),
    "cluster_ratio_k16": ("cluster", "list", "ratio", 16),
    "cluster_ratio_k20": ("cluster", "list", "ratio", 20),
    "greg_mu0.3": ("cluster", "list", "greg", K, 0.3),
    "greg_mu1": ("cluster", "list", "greg", K, 1.0),
    "greg_mu3": ("cluster", "list", "greg", K, 3.0),
    "greg_ratio_mu1": ("cluster", "list", "greg_ratio", K, 1.0),
}
# Only these run when the first argument is "greg" (the others are in the report already).
# (each variant re-seeds per budget, so they see the same panels as cluster_ratio).
GREG = [v for v in VARIANTS if v.startswith("greg")]


def run(t: int, draws: int, names: list[str] | None = None) -> pd.DataFrame:
    train = [area_election(k) for k in range(19, t)]
    cur = area_election(t)
    names = names or list(VARIANTS)
    priors = {(v[0], v[3]): prior_for(train[-1], cur, sectors=v[0], k=v[3])
              for n, v in VARIANTS.items() if n in names}
    rows = []
    for name in names:
        sectors, spread, estimator, k, *mu = VARIANTS[name]
        prior = priors[(sectors, k)]
        for budget in BUDGETS:
            n = allocate(prior, train, budget, spread=spread)
            rng = np.random.default_rng(SEED + t)
            for d in range(draws):
                panel = draw(prior, n, rng)
                pred = predict(prior, panel, read_boxes(cur, panel.index, rng),
                               estimator=estimator, mu=mu[0] if mu else 1.0)
                rows.append({"test": t, "variant": name, "budget": budget, "draw": d,
                             "areas": int(len(panel)), "sectors": int(len(n)),
                             **score(pred, cur)})
    return pd.DataFrame(rows)


def main(draws: int, tests: list[int], greg: bool = False) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for t in tests:
        run(t, draws, GREG if greg else None).to_csv(
            OUT / f"{'greg' if greg else 'draws'}_{t}.csv", index=False)
        print(f"K{t} done", flush=True)
    r = pd.concat(pd.read_csv(p) for p in sorted(OUT.glob("*_*.csv")))
    r["within_2"] = (r["seats_moved"] <= 2).astype(float)
    per = r.groupby(["variant", "budget", "test"])["seats_moved"].mean()
    g = r.groupby(["variant", "budget"]).agg(
        seats_moved=("seats_moved", "mean"), within_2=("within_2", "mean"),
        share_L1=("share_L1", "mean"), areas=("areas", "mean"), sectors=("sectors", "mean"))
    g["worst_election"] = per.groupby(["variant", "budget"]).max()
    text = "\n".join([
        "# Sector model variants, held-out (K22-K26)", "",
        f"`scripts/run_sector_variants.py`: {r['draw'].nunique()} panels per test, budget and "
        f"variant (same seed {SEED}+t for every variant), one random box per area, k-means "
        f"with {K} clusters unless the name says otherwise.", "", g.round(3).to_markdown(), "", "## Mean seats moved per test",
        "", per.unstack("test").round(2).to_markdown(), ""])
    (ROOT / "reports" / "sector_variants.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    greg = sys.argv[1:2] == ["greg"]
    args = [int(a) for a in sys.argv[1 + greg:]]
    main(args[0] if args else 100, args[1:] or [22, 23, 24, 25, 26], greg)
