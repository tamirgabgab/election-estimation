"""Election-night uncertainty of the sector ratio model, held-out (K22-K26).

For DRAWS panels per test election and budget (sector_neyman, one random box
per area): resample the panel within sectors (`sector.bootstrap`, REPS times),
and score
- the direct point (the panel as drawn) and the medoid point (the seat vector of
  a replicate with the least expected seats moved; `sector.medoid_seats`);
- the 90% seat interval per list (5th-95th percentile of the replicates):
  coverage and seats outside it;
- P(pass the threshold) per list: the Brier score.

Writes reports/sector_panel/intervals_<t>.csv and reports/sector_intervals.md.

Usage:
    PYTHONPATH=src python scripts/run_sector_intervals.py [draws] [tests...]
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from election_estimation.elections import seat_rules
from election_estimation.metrics import bader_ofer
from election_estimation.sector import (allocate, area_election, bootstrap, draw, medoid_seats,
                                        predict, prior_for, read_boxes)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "sector_panel"
BUDGETS = [0.015, 0.02]
REPS = 200
SEED = 1


def seats_of(votes: pd.Series, t: int) -> pd.Series:
    return bader_ofer(votes / votes.sum(), **seat_rules(t))


def run(t: int, draws: int) -> pd.DataFrame:
    train = [area_election(k) for k in range(19, t)]
    cur = area_election(t)
    prior = prior_for(train[-1], cur)
    thr = seat_rules(t)["threshold"]
    true = cur.seats
    rng = np.random.default_rng(SEED + t)
    rows = []
    for budget in BUDGETS:
        n = allocate(prior, train, budget)
        for d in range(draws):
            panel = draw(prior, n, rng)
            counted = read_boxes(cur, panel.index, rng)
            direct = seats_of(predict(prior, panel, counted), t)
            boot = bootstrap(prior, panel, counted, rng, REPS)
            seats = pd.DataFrame([seats_of(b, t) for _, b in boot.iterrows()])
            medoid = medoid_seats(seats)
            low, high = seats.quantile(0.05), seats.quantile(0.95)
            shares = boot.div(boot.sum(axis=1), axis=0)
            p_pass = (shares >= thr).mean()
            passed = (cur.shares >= thr).astype(float)
            out = (low - true).clip(lower=0) + (true - high).clip(lower=0)
            keep = (true > 0) | (high > 0)
            rows.append({
                "test": t, "budget": budget, "draw": d,
                "direct": float((direct - true).abs().sum() / 2),
                "medoid": float((medoid - true).abs().sum() / 2),
                "coverage": float(((true >= low) & (true <= high))[keep].mean()),
                "outside": float(out.sum() / 2),
                "width": float((high - low)[keep].mean()),
                "brier": float(((p_pass - passed) ** 2)[(p_pass > 0) | (passed > 0)].sum()),
            })
    return pd.DataFrame(rows)


def main(draws: int, tests: list[int]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for t in tests:
        run(t, draws).to_csv(OUT / f"intervals_{t}.csv", index=False)
        print(f"K{t} done", flush=True)
    r = pd.concat(pd.read_csv(p) for p in sorted(OUT.glob("intervals_*.csv")))
    cols = ["direct", "medoid", "coverage", "outside", "width", "brier"]
    within = r.assign(direct_2=r["direct"] <= 2, medoid_2=r["medoid"] <= 2)
    g = within.groupby("budget")[cols + ["direct_2", "medoid_2"]].mean()
    per = r.groupby(["budget", "test"])[["direct", "medoid", "coverage", "outside"]].mean()
    text = "\n".join([
        "# Sector model: point under the threshold and seat intervals (K22-K26)", "",
        f"`scripts/run_sector_intervals.py`: {r['draw'].nunique()} panels per test and budget "
        f"(sector_neyman), {REPS} within-sector bootstrap replicates, seed {SEED}+t. "
        "`direct` / `medoid`: seats moved of the point; `*_2`: share of panels within 2 "
        "seats; `coverage`: lists whose true seats are inside the 90% interval; "
        "`outside`: seats moved outside it; `brier`: sum over lists of the P(pass) "
        "squared error.", "",
        g.round(3).to_markdown(), "", "## Per test", "", per.round(2).to_markdown(), ""])
    (ROOT / "reports" / "sector_intervals.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    args = [int(a) for a in sys.argv[1:]]
    main(args[0] if args else 30, args[1:] or [22, 23, 24, 25, 26])
