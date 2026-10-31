"""Held-out comparison of sector model variants (K22-K26).

Variants (sectors / Neyman spread / estimator):
- base: bloc sectors, bloc spread, difference (the current model);
- list_spread: bloc sectors, list-level spread, difference;
- ratio: bloc sectors, list-level spread, ratio estimator;
- cluster: k-means sectors (K clusters), list-level spread, difference;
- cluster_ratio: k-means sectors, list-level spread, ratio estimator.
DRAWS panels per test, budget and variant, one random box per area, the same
seed for every variant. Writes reports/sector_variants/draws_<t>.csv and
reports/sector_variants.md.

Usage:
    PYTHONPATH=src python scripts/run_sector_variants.py [draws] [tests...]
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
VARIANTS = {
    "base": ("bloc", "bloc", "difference"),
    "list_spread": ("bloc", "list", "difference"),
    "ratio": ("bloc", "list", "ratio"),
    "cluster": ("cluster", "list", "difference"),
    "cluster_ratio": ("cluster", "list", "ratio"),
}


def run(t: int, draws: int) -> pd.DataFrame:
    train = [area_election(k) for k in range(19, t)]
    cur = area_election(t)
    priors = {s: prior_for(train[-1], cur, sectors=s, k=K) for s in ("bloc", "cluster")}
    rows = []
    for name, (sectors, spread, estimator) in VARIANTS.items():
        prior = priors[sectors]
        for budget in BUDGETS:
            n = allocate(prior, train, budget, spread=spread)
            rng = np.random.default_rng(SEED + t)
            for d in range(draws):
                panel = draw(prior, n, rng)
                pred = predict(prior, panel, read_boxes(cur, panel.index, rng),
                               estimator=estimator)
                rows.append({"test": t, "variant": name, "budget": budget, "draw": d,
                             "areas": int(len(panel)), "sectors": int(len(n)),
                             **score(pred, cur)})
    return pd.DataFrame(rows)


def main(draws: int, tests: list[int]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for t in tests:
        run(t, draws).to_csv(OUT / f"draws_{t}.csv", index=False)
        print(f"K{t} done", flush=True)
    r = pd.concat(pd.read_csv(p) for p in sorted(OUT.glob("draws_*.csv")))
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
        f"with {K} clusters.", "", g.round(3).to_markdown(), "", "## Mean seats moved per test",
        "", per.unstack("test").round(2).to_markdown(), ""])
    (ROOT / "reports" / "sector_variants.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    args = [int(a) for a in sys.argv[1:]]
    main(args[0] if args else 100, args[1:] or [22, 23, 24, 25, 26])
