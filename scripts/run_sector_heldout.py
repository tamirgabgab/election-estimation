"""Held-out results of the chosen sector model (sector.MODEL) for the site.

For every test election t in 22-26 and budget: DRAWS panels (one random box
per area) scored with the direct point; the first BOOT of them also with the
within-sector bootstrap (REPS replicates): the medoid point, 90% interval
coverage, seats outside the interval and the P(pass) Brier score. The prior
uses t-1 and the box counts of t; the allocation uses transitions up to t-1.
Writes reports/sector_model/draws_<t>.csv and reports/sector_model.md.

Usage:
    PYTHONPATH=src python scripts/run_sector_heldout.py [draws] [boot] [tests...]
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from election_estimation.elections import seat_rules
from election_estimation.metrics import bader_ofer
from election_estimation.sector import (MODEL, allocate, area_election, bootstrap, draw,
                                        medoid_seats, predict, prior_for, read_boxes)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "sector_model"
BUDGETS = [0.01, 0.015, 0.02]
REPS = 200
SEED = 6


def seats_of(votes: pd.Series, t: int) -> pd.Series:
    return bader_ofer(votes / votes.sum(), **seat_rules(t))


def run(t: int, draws: int, boot: int) -> pd.DataFrame:
    train = [area_election(k) for k in range(19, t)]
    cur = area_election(t)
    prior = prior_for(train[-1], cur, sectors=MODEL["sectors"], k=MODEL["k"])
    est = MODEL["estimator"]
    thr = seat_rules(t)["threshold"]
    true = cur.seats
    rng = np.random.default_rng(SEED + t)
    rows = []
    for budget in BUDGETS:
        n = allocate(prior, train, budget, spread=MODEL["spread"])
        for d in range(draws):
            panel = draw(prior, n, rng)
            counted = read_boxes(cur, panel.index, rng)
            direct = seats_of(predict(prior, panel, counted, estimator=est), t)
            row = {"test": t, "budget": budget, "draw": d, "areas": int(len(panel)),
                   "direct": float((direct - true).abs().sum() / 2)}
            if d < boot:
                b = bootstrap(prior, panel, counted, rng, REPS, estimator=est)
                seats = pd.DataFrame([seats_of(v, t) for _, v in b.iterrows()])
                medoid = medoid_seats(seats)
                low, high = seats.quantile(0.05), seats.quantile(0.95)
                p_pass = (b.div(b.sum(axis=1), axis=0) >= thr).mean()
                passed = (cur.shares >= thr).astype(float)
                keep = (true > 0) | (high > 0)
                out = (low - true).clip(lower=0) + (true - high).clip(lower=0)
                row |= {"medoid": float((medoid - true).abs().sum() / 2),
                        "coverage": float(((true >= low) & (true <= high))[keep].mean()),
                        "outside": float(out.sum() / 2), "width": float((high - low)[keep].mean()),
                        "brier": float(((p_pass - passed) ** 2)[(p_pass > 0) | (passed > 0)].sum())}
            rows.append(row)
    return pd.DataFrame(rows)


def main(draws: int, boot: int, tests: list[int]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for t in tests:
        run(t, draws, boot).to_csv(OUT / f"draws_{t}.csv", index=False)
        print(f"K{t} done", flush=True)
    r = pd.concat(pd.read_csv(p) for p in sorted(OUT.glob("draws_*.csv")))
    r["direct_2"] = (r["direct"] <= 2).astype(float)
    r["medoid_2"] = (r["medoid"] <= 2).where(r["medoid"].notna())
    g = r.groupby("budget")[["areas", "direct", "direct_2", "medoid", "medoid_2", "coverage",
                             "outside", "width", "brier"]].mean()
    per = r.groupby(["budget", "test"])[["direct", "medoid", "coverage"]].mean()
    g["worst_election"] = per["direct"].groupby("budget").max()
    text = "\n".join([
        "# Chosen sector model, held-out (K22-K26)", "",
        f"`scripts/run_sector_heldout.py`, model {MODEL}: {r['draw'].nunique()} panels per test "
        f"and budget (direct point), the first {int(r['medoid'].notna().groupby(r['draw']).any().sum())} "
        f"also with {REPS} within-sector bootstrap replicates (medoid, 90% intervals), seed "
        f"{SEED}+t, one random box per area. `*_2`: share of panels within 2 seats.", "",
        g.round(3).to_markdown(), "", "## Per test", "", per.round(2).to_markdown(), ""])
    (ROOT / "reports" / "sector_model.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    args = [int(a) for a in sys.argv[1:]]
    main(args[0] if args else 100, args[1] if len(args) > 1 else 20, args[2:] or [22, 23, 24, 25, 26])
