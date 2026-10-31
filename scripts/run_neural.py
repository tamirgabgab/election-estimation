"""Held-out test of the neural area model against the sector model (K22-K26).

For every test election t: the network is trained on simulated panels of the
transitions before t (k-1 -> k for k = 20 .. t-1; PANELS per budget, size
allocation), then DRAWS panels of t are drawn (sector.MODEL, Neyman allocation,
one random box per area) and both the sector model (ratio, direct point) and
the network predict the same counted boxes. Seeds fixed; torch on CPU.
Writes reports/neural/draws_<t>.csv and reports/neural.md.

Usage:
    PYTHONPATH=src python scripts/run_neural.py [draws] [tests...]
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from election_estimation.evaluate import score
from election_estimation.neural import make_batch, national, train, training_batches
from election_estimation.sector import (MODEL, allocate, area_election, draw, predict, prior_for,
                                        read_boxes)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "neural"
BUDGETS = [0.01, 0.015, 0.02]
PANELS = 8          # simulated panels per training transition and budget
EPOCHS = 30
SEED = 7
torch.set_num_threads(1)


def prior_of(prev, cur):
    return prior_for(prev, cur, sectors=MODEL["sectors"], k=MODEL["k"])


def new_lists(prior) -> set[str]:
    return set(prior.lists) - set(prior.mapping)


def run(t: int, draws: int) -> pd.DataFrame:
    rng = np.random.default_rng(SEED + t)
    batches = []
    for k in range(20, t):
        prev, cur = area_election(k - 1), area_election(k)
        prior = prior_of(prev, cur)
        for budget in BUDGETS:
            n = allocate(prior, [prev], budget, neyman=False)
            batches += training_batches(prior, cur, n, draw, PANELS, rng, new_lists(prior))
    net = train(batches, epochs=EPOCHS, seed=SEED + t)
    train_e = [area_election(k) for k in range(19, t)]
    cur = area_election(t)
    prior = prior_of(train_e[-1], cur)
    new = new_lists(prior)
    rows = []
    for budget in BUDGETS:
        n = allocate(prior, train_e, budget, spread=MODEL["spread"])
        for d in range(draws):
            panel = draw(prior, n, rng)
            counted = read_boxes(cur, panel.index, rng)
            sector = predict(prior, panel, counted, estimator=MODEL["estimator"])
            nn = pd.Series(national(net, make_batch(prior, panel, counted, cur.blocs, new)),
                           index=prior.lists)
            for name, pred in (("sector", sector), ("neural", nn)):
                rows.append({"test": t, "budget": budget, "draw": d, "model": name,
                             **score(pred, cur)})
    return pd.DataFrame(rows)


def main(draws: int, tests: list[int]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for t in tests:
        run(t, draws).to_csv(OUT / f"draws_{t}.csv", index=False)
        print(f"K{t} done", flush=True)
    r = pd.concat(pd.read_csv(p) for p in sorted(OUT.glob("draws_*.csv")))
    r["within_2"] = (r["seats_moved"] <= 2).astype(float)
    per = r.groupby(["model", "budget", "test"])["seats_moved"].mean()
    g = r.groupby(["model", "budget"])[["seats_moved", "within_2", "share_L1"]].mean()
    g["worst_election"] = per.groupby(["model", "budget"]).max()
    text = "\n".join([
        "# Neural area model vs the sector model, held-out (K22-K26)", "",
        f"`scripts/run_neural.py`: trained on {PANELS} simulated panels per budget of every "
        f"transition before the test election, {EPOCHS} epochs, seed {SEED}+t; "
        f"{r['draw'].nunique()} test panels per budget, both models on the same counted boxes.",
        "", g.round(3).to_markdown(), "", "## Mean seats moved per test", "",
        per.unstack("test").round(2).to_markdown(), ""])
    (ROOT / "reports" / "neural.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    args = [int(a) for a in sys.argv[1:]]
    main(args[0] if args else 100, args[1:] or [22, 23, 24, 25, 26])
