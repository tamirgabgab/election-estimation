"""Panels of whole settlements (k = 20-50 settlements, counted in full).

Same target and goal as run_budget_curve.py (regular boxes, at most 2 seats
moved in the mean and in the worst test election), but the unit is the
settlement and k counts settlements, not boxes; `boxes` reports what counting
them costs.

`--oracle` also fits panels on each test election itself. That is in-sample
(the test result is used to choose the panel), so it is not model quality: it
only shows how small a panel can be when chosen in hindsight.

Usage:
    PYTHONPATH=src python scripts/run_settlement_panel.py
    PYTHONPATH=src python scripts/run_settlement_panel.py --oracle
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from election_estimation.evaluate import (evaluate, greedy_regularized, greedy_weighted,
                                          load_all, random_pps, score, stacked, _panel)
from election_estimation.selection import greedy_selection

REPORTS_DIR = Path(__file__).resolve().parents[1] / "reports"
UNIT = "settlement"
TARGET = "regular"
TESTS = [22, 23, 24, 25, 26]
KS = (20, 30, 35, 40, 50)
SEED = 0
DECAY = 0.7
DRAWS = 30
TUNE = 35
GOAL = 2.0
METRICS = ["boxes", "seats_moved", "share_L1", "max_list_error", "bloc_seat_L1",
           "threshold_errors"]
ORACLE_KS = {"base_box": (10, 20, 40, 80), "settlement": (5, 10, 20, 40)}


def methods() -> dict:
    greedy = greedy_weighted(decay=DECAY, candidates=40)
    greedy.readings = ("unit",)

    def tuned(grid: dict, candidates: int):
        return greedy_regularized(grid, decay=DECAY, candidates=candidates, tune_budget=TUNE,
                                  inner_folds=2, ks=KS, nested=True, by_count=True)
    return {
        "greedy": greedy,
        "weight_prior": tuned({"mu": [0.003, 0.01, 0.03]}, candidates=40),
        "calibration": tuned({"calibration": [0.3, 1.0]}, candidates=10),
        "random_pps": random_pps,
    }


def run() -> None:
    elections = load_all(UNIT, target=TARGET)
    results = evaluate(elections, methods(), list(KS), TESTS, draws=DRAWS, seed=SEED)
    results = results[(results["method"] != "all_boxes")
                      & ~((results["method"] == "random_pps") & (results["reading"] != "unit"))]
    results.to_csv(REPORTS_DIR / "settlement_panel.csv", index=False)
    by = ["method", "k"]
    table = pd.concat([results.groupby(by)[METRICS].mean(),
                       results.groupby(by)["seats_moved"].max().rename("worst_seats_moved")],
                      axis=1).round(2)
    moved = results.pivot_table(index=by, columns="test", values="seats_moved").round(1)
    lines = [
        f"# Panels of whole settlements - target: regular boxes",
        "",
        f"Held-out test elections {TESTS[0]}-{TESTS[-1]}; `k` = settlements in the panel, each",
        "counted in full (`boxes` = what that costs). `seats_moved` = seat L1 / 2; goal: at",
        f"most {GOAL:g} in the mean and in the worst election. Seed {SEED}, decay {DECAY},",
        f"strengths by inner validation (2 folds, {TUNE} settlements); random PPS over {DRAWS}",
        "draws.",
        "",
        "## Mean over test elections, worst election",
        "",
        table.to_markdown(),
        "",
        "## Seats moved per test election",
        "",
        moved.to_markdown(),
        "",
    ]
    out = REPORTS_DIR / "settlement_panel.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out}")


def oracle() -> None:
    """In-sample: the panel is chosen on the test election itself."""
    rows = []
    for unit, ks in ORACLE_KS.items():
        elections = load_all(unit, target=TARGET)
        for t in TESTS:
            e = elections[t]
            units = list(e.units.index)
            X, y = stacked([e], units, decay=1.0)
            history = greedy_selection(X, y, max_boxes=max(ks), candidates=40)
            by_k = {h["k"]: h for h in history}
            for k in ks:
                panel = _panel(units, by_k.get(k, history[-1]))
                rows.append({"unit": unit, "k": k, "test": t,
                             "boxes": panel.boxes(e, "unit"),
                             **score(panel.predict(e, "unit", np.random.default_rng(SEED)), e)})
    r = pd.DataFrame(rows)
    r.to_csv(REPORTS_DIR / "oracle_panel.csv", index=False)
    print(r.pivot_table(index=["unit", "k"], columns="test", values="seats_moved").to_string())
    print(r.groupby(["unit", "k"])[["boxes", "share_L1"]].mean().round(2).to_string())


if __name__ == "__main__":
    oracle() if sys.argv[1:] == ["--oracle"] else run()
