"""Held-out comparison of panel designs for the chosen sector model (K22-K26).

Designs (sector.MODEL, same vote budget):
- bloc: systematic draw sorted by the sector's main bloc (the site today);
- pc1: sorted by the first principal component of the previous list shares;
- snake: bins of the first component, the second inside them;
- two_boxes: half the areas per sector (sorted as bloc), two boxes read in each
  (one where the area has a single box);
- empirical: sorted as bloc, sector sizes from the simulated seat error of past
  transitions (`allocate(spread="empirical")`, Next steps A4).
DRAWS panels per test and budget, the same seed for every design. Writes
reports/sector_design/draws_<t>.csv and reports/sector_design.md.

Usage:
    PYTHONPATH=src python scripts/run_sector_design.py [empirical] [draws] [tests...]
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from election_estimation.evaluate import score
from election_estimation.sector import (MODEL, MIN_PER_SECTOR, allocate, area_election, draw,
                                        predict, prior_for, read_boxes)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "sector_design"
BUDGETS = [0.015, 0.02]
SEED = 8
DESIGNS = {"bloc": ("bloc", 1), "pc1": ("pc1", 1), "snake": ("snake", 1),
           "two_boxes": ("bloc", 2), "empirical": ("bloc", 1)}
# Only these run when the first argument is "empirical" (the others are in the report).
EMPIRICAL = ["empirical"]


def run(t: int, draws: int, names: list[str] | None = None) -> pd.DataFrame:
    train = [area_election(k) for k in range(19, t)]
    cur = area_election(t)
    prior = prior_for(train[-1], cur, sectors=MODEL["sectors"], k=MODEL["k"])
    rows = []
    for budget in BUDGETS:
        n = allocate(prior, train, budget, spread=MODEL["spread"])
        for name in names or [d for d in DESIGNS if d not in EMPIRICAL]:
            order, boxes = DESIGNS[name]
            if name == "empirical":
                n = allocate(prior, train, budget, spread="empirical")
            k = n if boxes == 1 else np.maximum(MIN_PER_SECTOR, n // boxes)
            rng = np.random.default_rng(SEED + t)
            for d in range(draws):
                panel = draw(prior, k, rng, order=order)
                counted = read_boxes(cur, panel.index, rng, boxes=boxes)
                pred = predict(prior, panel, counted, estimator=MODEL["estimator"])
                read = cur.unit_boxes[panel.index].clip(upper=boxes)
                rows.append({"test": t, "design": name, "budget": budget, "draw": d,
                             "areas": int(len(panel)), "boxes": int(read.sum()),
                             **score(pred, cur)})
    return pd.DataFrame(rows)


def main(draws: int, tests: list[int], empirical: bool = False) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for t in tests:
        run(t, draws, EMPIRICAL if empirical else None).to_csv(
            OUT / f"{'empirical' if empirical else 'draws'}_{t}.csv", index=False)
        print(f"K{t} done", flush=True)
    r = pd.concat(pd.read_csv(p) for p in sorted(OUT.glob("*_*.csv")))
    r["within_2"] = (r["seats_moved"] <= 2).astype(float)
    per = r.groupby(["design", "budget", "test"])["seats_moved"].mean()
    g = r.groupby(["design", "budget"])[["areas", "boxes", "seats_moved", "within_2",
                                         "share_L1"]].mean()
    g["worst_election"] = per.groupby(["design", "budget"]).max()
    text = "\n".join([
        "# Panel designs for the sector model, held-out (K22-K26)", "",
        f"`scripts/run_sector_design.py`: {r['draw'].nunique()} panels per test, budget and "
        f"design (same seed {SEED}+t), direct point, model {MODEL}.", "",
        g.round(3).to_markdown(), "", "## Mean seats moved per test", "",
        per.unstack("test").round(2).to_markdown(), ""])
    (ROOT / "reports" / "sector_design.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    empirical = sys.argv[1:2] == ["empirical"]
    args = [int(a) for a in sys.argv[1 + empirical:]]
    main(args[0] if args else 100, args[1:] or [22, 23, 24, 25, 26], empirical)
