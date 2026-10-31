"""Held-out evaluation of the swing model on settlement panels (decisions M13-M15).

The national bloc shares are the previous election's (all regular boxes) plus
the weighted bloc swing of the panel settlements; lists within a bloc are split
by the panel's weighted shares (`election_estimation.swing`). Compared with the
level panels of run_settlement_panel.py (reports/settlement_panel.csv).

Usage:
    PYTHONPATH=src python scripts/run_swing_panel.py
"""

from pathlib import Path

import pandas as pd

from election_estimation.evaluate import evaluate, load_all
from election_estimation.swing import swing_panel

REPORTS_DIR = Path(__file__).resolve().parents[1] / "reports"
UNIT = "settlement"
TARGET = "regular"
TESTS = [22, 23, 24, 25, 26]
KS = (20, 30, 35, 40, 50)
SEED = 0
DECAY = 0.7
TUNE = 35
INNER_FOLDS = 2
GRID = {"mu": [0.003, 0.01, 0.03], "level": [0.1, 0.3, 1.0]}
GOAL = 2.0
METRICS = ["boxes", "seats_moved", "share_L1", "max_list_error", "bloc_seat_L1",
           "bloc_share_L1", "threshold_errors"]


def main() -> None:
    elections = load_all(UNIT, target=TARGET)
    methods = {"swing": swing_panel(GRID, decay=DECAY, tune_k=TUNE, inner_folds=INNER_FOLDS,
                                    ks=KS)}
    results = evaluate(elections, methods, list(KS), TESTS, draws=1, seed=SEED)
    results = results[results["method"] != "all_boxes"]
    level = pd.read_csv(REPORTS_DIR / "settlement_panel.csv")
    level = level[level["method"].isin(["greedy", "weight_prior"])]
    results = pd.concat([results, level.assign(method="level_" + level["method"])])
    results.to_csv(REPORTS_DIR / "swing_panel.csv", index=False)

    by = ["method", "k"]
    table = pd.concat([results.groupby(by)[METRICS].mean(),
                       results.groupby(by)["seats_moved"].max().rename("worst_seats_moved")],
                      axis=1).round(2)
    moved = results.pivot_table(index=by, columns="test", values="seats_moved").round(1)
    params = [c for c in results.columns if c.startswith("param_")]
    chosen = (results[(results["method"] == "swing") & (results["k"] == TUNE)]
              .set_index("test")[params])
    lines = [
        "# Swing model on settlement panels - target: regular boxes",
        "",
        f"Held-out test elections {TESTS[0]}-{TESTS[-1]}; `k` = settlements in the panel, counted",
        "in full (`boxes` = what that costs). `swing`: previous national bloc shares plus the",
        "panel's weighted bloc swing, lists split within blocs by the panel; weights fit to",
        "past national bloc swings plus list-share rows scaled by `level`, pulled towards",
        "size-proportional weights by `mu`. `level_*`: the level panels of",
        "`settlement_panel.md`. `seats_moved` = seat L1 / 2; goal: at most",
        f"{GOAL:g} in the mean and in the worst election. Seed {SEED}, decay {DECAY}; grid",
        f"{GRID} chosen by inner validation ({INNER_FOLDS} folds, {TUNE} settlements).",
        "",
        "## Mean over test elections, worst election",
        "",
        table.to_markdown(),
        "",
        "## Seats moved per test election",
        "",
        moved.to_markdown(),
        "",
        f"## Chosen setting per test election (swing, {TUNE} settlements)",
        "",
        chosen.to_markdown(),
        "",
    ]
    out = REPORTS_DIR / "swing_panel.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
