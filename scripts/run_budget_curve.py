"""Seat error as a function of the box budget N (decision M10-M12).

Target: the total of the regular boxes (double envelopes excluded, M10).
Success: at most 2 seats moved between lists (`seats_moved` = seat L1 / 2,
M11), in the mean over the test elections and in the worst one (M12).
Unit: base box. Greedy panels are nested: one run at the largest budget, the
panel for N is the prefix that fits in N boxes.

Each method runs separately (they can run in parallel) and writes
reports/archive/budget_curve/<method>.csv; `--report` merges them into
reports/archive/budget_curve_base_box.md.

Usage:
    PYTHONPATH=src python scripts/run_budget_curve.py greedy_budget weight_prior
    PYTHONPATH=src python scripts/run_budget_curve.py --report
"""

import sys
from pathlib import Path

import pandas as pd

from election_estimation.evaluate import (evaluate, greedy_budget, greedy_regularized,
                                          load_all, random_pps, stratified)

REPORTS_DIR = Path(__file__).resolve().parents[1] / "reports" / "archive"  # earlier experiments
PARTS_DIR = REPORTS_DIR / "budget_curve"
UNIT = "base_box"
TARGET = "regular"
TESTS = [22, 23, 24, 25, 26]
KS = tuple(range(40, 161, 20))
SEED = 0
DECAY = 0.7
DRAWS = 30
TUNE_BUDGET = 60
INNER_FOLDS = 2
GOAL = 2.0  # seats moved
METRICS = ["boxes", "seats_moved", "share_L1", "max_list_error", "bloc_seat_L1",
           "threshold_errors"]


def methods() -> dict:
    def tuned(grid: dict, candidates: int):
        return greedy_regularized(grid, decay=DECAY, candidates=candidates,
                                  tune_budget=TUNE_BUDGET, inner_folds=INNER_FOLDS, ks=KS,
                                  nested=True)
    return {
        "greedy_budget": greedy_budget(decay=DECAY, candidates=20, nested=True),
        "weight_prior": tuned({"mu": [0.003, 0.01, 0.03]}, candidates=20),
        "calibration": tuned({"calibration": [0.3, 1.0]}, candidates=8),
        "calibration_prior": tuned({"calibration": [1.0], "mu": [0.003, 0.01]}, candidates=8),
        "random_pps": random_pps,
        "stratified": stratified,
    }


def run(names: list[str]) -> None:
    elections = load_all(UNIT, target=TARGET)
    available = methods()
    PARTS_DIR.mkdir(parents=True, exist_ok=True)
    for name in names:
        results = evaluate(elections, {name: available[name]}, list(KS), TESTS,
                           draws=DRAWS, seed=SEED)
        results.to_csv(PARTS_DIR / f"{name}.csv", index=False)
        print(f"Wrote {PARTS_DIR / f'{name}.csv'}")


def report() -> None:
    results = pd.concat([pd.read_csv(p) for p in sorted(PARTS_DIR.glob("*.csv"))])
    results = results[results["method"] != "all_boxes"]
    results.to_csv(REPORTS_DIR / f"budget_curve_{UNIT}.csv", index=False)
    by = ["method", "reading", "k"]
    mean = results.groupby(by)[METRICS].mean()
    worst = results.groupby(by)["seats_moved"].max().rename("worst_seats_moved")
    table = pd.concat([mean, worst], axis=1).round(2)
    moved = results.pivot_table(index=by, columns="test", values="seats_moved").round(1)
    ok = table[(table["seats_moved"] <= GOAL) & (table["worst_seats_moved"] <= GOAL)]
    smallest = ok.reset_index().groupby(["method", "reading"])["k"].min()
    lines = [
        f"# Seat error by box budget - unit: {UNIT}, target: regular boxes",
        "",
        f"Held-out test elections {TESTS[0]}-{TESTS[-1]}. The target is the total of the",
        "regular boxes (double envelopes excluded), so counting every box gives 0 error.",
        "`seats_moved` = seat L1 / 2 (seats that moved between lists); goal: at most",
        f"{GOAL:g} in the mean and in the worst test election. `k` = budget N in boxes",
        "(greedy panels; `boxes` = actually counted) or panel units (random / stratified,",
        "averaged over",
        f"{DRAWS} draws). Seed {SEED}, decay {DECAY}; regularization strengths chosen by inner",
        f"validation ({INNER_FOLDS} folds, {TUNE_BUDGET} boxes); greedy panels nested.",
        "",
        "## Smallest N that meets the goal",
        "",
        smallest.to_markdown() if len(smallest) else "None of the methods meets the goal.",
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
    out = REPORTS_DIR / f"budget_curve_{UNIT}.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    if sys.argv[1:] == ["--report"]:
        report()
    else:
        run(sys.argv[1:])
