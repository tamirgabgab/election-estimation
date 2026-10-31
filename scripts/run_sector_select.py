"""Does choosing a sector panel by its past fit help? Held-out (K22-K26).

For every test election t and budget, CANDIDATES panels are drawn (sector
model, Neyman allocation). Each is scored
- held out on t (mean over READINGS random box readings), and
- in replay on the two previous transitions (t-2 -> t-1 and t-3 -> t-2): the
  same areas read in t-1 / t-2 with the prior of the transition before.
The panel picked by its replay score is compared with a random candidate.
Writes reports/sector_panel/select_<t>.csv and reports/sector_select.md.

Usage:
    PYTHONPATH=src python scripts/run_sector_select.py [candidates] [tests...]
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from election_estimation.evaluate import score
from election_estimation.sector import allocate, area_election, draw, predict, prior_for, read_boxes

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "sector_panel"
BUDGETS = [0.015, 0.02]
READINGS = 3
SEED = 2


def moved(prior, panel: pd.Series, cur, rng: np.random.Generator) -> float:
    """Mean seats moved of `panel` (areas missing in `cur` dropped) over READINGS."""
    panel = panel[panel.index.isin(prior.sector.index) & panel.index.isin(cur.units.index)]
    out = []
    for _ in range(READINGS):
        counted = read_boxes(cur, panel.index, rng)
        out.append(score(predict(prior, panel, counted), cur)["seats_moved"])
    return float(np.mean(out))


def run(t: int, candidates: int) -> pd.DataFrame:
    e = {k: area_election(k) for k in range(19, t + 1)}
    train = [e[k] for k in range(19, t)]
    prior = prior_for(e[t - 1], e[t])
    replay = {k: prior_for(e[k - 1], e[k]) for k in (t - 1, t - 2) if k - 1 >= 19}
    rng = np.random.default_rng(SEED + t)
    rows = []
    for budget in BUDGETS:
        n = allocate(prior, train, budget)
        for c in range(candidates):
            panel = draw(prior, n, rng)
            rows.append({"test": t, "budget": budget, "candidate": c,
                         "held_out": moved(prior, panel, e[t], rng),
                         **{f"replay_{k}": moved(p, panel, e[k], rng) for k, p in replay.items()}})
    r = pd.DataFrame(rows)
    r["replay"] = r.filter(like="replay_").mean(axis=1)
    return r


def main(candidates: int, tests: list[int]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for t in tests:
        run(t, candidates).to_csv(OUT / f"select_{t}.csv", index=False)
        print(f"K{t} done", flush=True)
    r = pd.concat(pd.read_csv(p) for p in sorted(OUT.glob("select_*.csv")))
    rows = []
    for (b, t), g in r.groupby(["budget", "test"]):
        top = g.nsmallest(max(1, len(g) // 10), "replay")
        rows.append({"budget": b, "test": t, "random": g["held_out"].mean(),
                     "best_replay": g.loc[g["replay"].idxmin(), "held_out"],
                     "top10pct_replay": top["held_out"].mean(),
                     "spearman": g["replay"].corr(g["held_out"], method="spearman")})
    s = pd.DataFrame(rows)
    text = "\n".join([
        "# Choosing sector panels by their past fit (K22-K26)", "",
        f"`scripts/run_sector_select.py`: {r['candidate'].nunique()} candidate panels per test "
        f"and budget, {READINGS} box readings each, seed {SEED}+t. Held-out seats moved of a "
        "random candidate, of the best by replay on the two previous transitions, and of the "
        "best 10% by replay; Spearman correlation of replay and held-out.", "",
        s.groupby("budget")[["random", "best_replay", "top10pct_replay", "spearman"]].mean()
        .round(2).to_markdown(), "", "## Per test", "",
        s.set_index(["budget", "test"]).round(2).to_markdown(), ""])
    (ROOT / "reports" / "sector_select.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    args = [int(a) for a in sys.argv[1:]]
    main(args[0] if args else 100, args[1:] or [22, 23, 24, 25, 26])
