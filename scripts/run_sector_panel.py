"""Held-out backtest of the sector ratio model (decisions M30-M35).

For every test election t in 22-26 and budget (share of the previous valid
votes), DRAWS panels of statistical areas are drawn (one random box read per
area) and scored on t. The prior uses only t-1 and the box counts of t; the
Neyman allocation uses transitions up to t-1. Variants:

- sector_neyman: sectors, Neyman allocation, turnout per sector (the model);
- sector_prop: sectors, allocation by size only;
- no_turnout: as sector_neyman, turnout taken as unchanged;
- national: one sector (the same estimator without sectors).

Writes reports/sector_panel.csv (one row per draw) and reports/sector_panel.md.

Usage:
    PYTHONPATH=src python scripts/run_sector_panel.py [draws] [tests...]
"""

import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd

from election_estimation.evaluate import score
from election_estimation.sector import allocate, area_election, draw, predict, prior_for, read_boxes

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "sector_panel"
BUDGETS = [0.01, 0.015, 0.02]
SEED = 0
VARIANTS = ["sector_neyman", "sector_prop", "no_turnout", "national"]


def run(t: int, draws: int) -> pd.DataFrame:
    train = [area_election(k) for k in range(19, t)]
    prev, cur = train[-1], area_election(t)
    base = prior_for(prev, cur)
    one = replace(base, sector=pd.Series("all", index=base.sector.index))
    rng = np.random.default_rng(SEED + t)
    rows = []
    for budget in BUDGETS:
        alloc = {"sector_neyman": allocate(base, train, budget),
                 "sector_prop": allocate(base, train, budget, neyman=False),
                 "national": allocate(one, train, budget, neyman=False)}
        alloc["no_turnout"] = alloc["sector_neyman"]
        for d in range(draws):
            for v in VARIANTS:
                prior = one if v == "national" else base
                panel = draw(prior, alloc[v], rng)
                counted = read_boxes(cur, panel.index, rng)
                pred = predict(prior, panel, counted, turnout=v != "no_turnout")
                cost = float(prior.cost[panel.index].mul(panel).sum()
                             / prev.units.values.sum())
                rows.append({"test": t, "budget": budget, "variant": v, "draw": d,
                             "areas": int(len(panel)), "votes_share": cost,
                             **score(pred, cur)})
    return pd.DataFrame(rows)


def report(r: pd.DataFrame) -> str:
    r = r.assign(within_2=(r["seats_moved"] <= 2).astype(float))
    per = r.groupby(["variant", "budget", "test"])[["seats_moved", "within_2"]].mean()
    g = per.groupby(["variant", "budget"]).agg(
        seats_moved=("seats_moved", "mean"), worst_election=("seats_moved", "max"),
        within_2=("within_2", "mean"))
    g = g.join(r.groupby(["variant", "budget"])[["areas", "votes_share", "share_L1"]].mean())
    tests = per["seats_moved"].unstack("test")
    return "\n".join([
        "# Sector ratio model, held-out (K22-K26)", "",
        f"`scripts/run_sector_panel.py`, {r['draw'].nunique()} draws per test, budget and "
        f"variant, seed {SEED}+t, one random box per area. `within_2`: share of draws with "
        "at most 2 seats moved; `worst_election`: the worst test's mean.", "",
        g.round(3).to_markdown(), "", "## Mean seats moved per test", "",
        tests.round(2).to_markdown(), ""])


def main(draws: int, tests: list[int]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for t in tests:
        run(t, draws).to_csv(OUT / f"draws_{t}.csv", index=False)
        print(f"K{t} done", flush=True)
    r = pd.concat(pd.read_csv(p) for p in sorted(OUT.glob("draws_*.csv")))
    text = report(r)
    (ROOT / "reports" / "sector_panel.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    args = [int(a) for a in sys.argv[1:]]
    main(args[0] if args else 100, args[1:] or [22, 23, 24, 25, 26])
