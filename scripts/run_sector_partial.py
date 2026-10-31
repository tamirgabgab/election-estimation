"""Election night with part of the panel counted: held-out K22-K26, 2% budget.

For DRAWS panels per test, the counted areas are thinned before predicting:
- full: every area;
- random_<p>: a random p of the areas (90%, 70%, 50%);
- arab_late: no area of the Arab sectors yet, every other area counted;
- arab_half: half of the Arab-sector areas, every other area counted.
A sector with no counted area either keeps its previous result ("prev") or takes
the turnout and change of all counted areas ("pooled"). Writes
reports/sector_partial/draws_<t>.csv and reports/sector_partial.md.

Usage:
    PYTHONPATH=src python scripts/run_sector_partial.py [draws] [tests...]
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from election_estimation.evaluate import score
from election_estimation.sector import allocate, area_election, draw, predict, prior_for, read_boxes

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "sector_partial"
BUDGET = 0.02
SEED = 5
SCENARIOS = ["full", "random_90", "random_70", "random_50", "arab_late", "arab_half"]


def thin(panel: pd.Series, sector: pd.Series, scenario: str,
         rng: np.random.Generator) -> pd.Series:
    if scenario == "full":
        return panel
    if scenario.startswith("random_"):
        keep = rng.random(len(panel)) < int(scenario.split("_")[1]) / 100
        return panel[keep] if keep.any() else panel.iloc[:1]
    arab = sector[panel.index].str.startswith("arab").values
    if scenario == "arab_late":
        return panel[~arab]
    return panel[~arab | (rng.random(len(panel)) < 0.5)]


def run(t: int, draws: int) -> pd.DataFrame:
    train = [area_election(k) for k in range(19, t)]
    cur = area_election(t)
    prior = prior_for(train[-1], cur)
    n = allocate(prior, train, BUDGET)
    rng = np.random.default_rng(SEED + t)
    rows = []
    for d in range(draws):
        panel = draw(prior, n, rng)
        counted = read_boxes(cur, panel.index, rng)
        for scenario in SCENARIOS:
            part = thin(panel, prior.sector, scenario, rng)
            for missing in ("prev", "pooled"):
                pred = predict(prior, part, counted.loc[part.index], missing=missing)
                rows.append({"test": t, "draw": d, "scenario": scenario, "missing": missing,
                             "counted": len(part) / len(panel), **score(pred, cur)})
    return pd.DataFrame(rows)


def main(draws: int, tests: list[int]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for t in tests:
        run(t, draws).to_csv(OUT / f"draws_{t}.csv", index=False)
        print(f"K{t} done", flush=True)
    r = pd.concat(pd.read_csv(p) for p in sorted(OUT.glob("draws_*.csv")))
    r["within_2"] = (r["seats_moved"] <= 2).astype(float)
    per = r.groupby(["scenario", "missing", "test"])["seats_moved"].mean()
    g = r.groupby(["scenario", "missing"]).agg(
        counted=("counted", "mean"), seats_moved=("seats_moved", "mean"),
        within_2=("within_2", "mean"))
    g["worst_election"] = per.groupby(["scenario", "missing"]).max()
    g = g.reindex(SCENARIOS, level=0)
    text = "\n".join([
        "# Sector model with part of the panel counted (held-out, 2% budget)", "",
        f"`scripts/run_sector_partial.py`: {r['draw'].nunique()} panels per test, seed {SEED}+t, "
        "one random box per area. `missing`: a sector with no counted area keeps its previous "
        "result (`prev`) or takes the turnout and change of all counted areas (`pooled`).", "",
        g.round(3).to_markdown(), "", "## Mean seats moved per test", "",
        per.unstack("test").reindex(SCENARIOS, level=0).round(2).to_markdown(), ""])
    (ROOT / "reports" / "sector_partial.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    args = [int(a) for a in sys.argv[1:]]
    main(args[0] if args else 100, args[1:] or [22, 23, 24, 25, 26])
