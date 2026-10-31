"""Joint level + swing settlement panels (decisions M16-M19).

One panel, one set of weights, two predictions mixed as
alpha * level + (1 - alpha) * swing; the swing splits blocs into lists by
family swing where the family continues (`joint_family`) or by the panel only
(`joint_bloc`, the ablation). `mu`, `level` and `alpha` are chosen by inner
validation on share L1 over the last 3 training elections. Panels of 20-150
settlements, counted in full, no box cap.

Each method writes reports/joint_panel/<method>.csv (they can run in
parallel); `--report` merges them with the earlier level and swing results
into reports/joint_panel.md.

Usage:
    PYTHONPATH=src python scripts/run_joint_panel.py joint_family
    PYTHONPATH=src python scripts/run_joint_panel.py joint_bloc
    PYTHONPATH=src python scripts/run_joint_panel.py --report
"""

import sys
from pathlib import Path

import pandas as pd

from election_estimation.evaluate import evaluate, load_all
from election_estimation.swing import swing_panel

REPORTS_DIR = Path(__file__).resolve().parents[1] / "reports"
PARTS_DIR = REPORTS_DIR / "joint_panel"
UNIT = "settlement"
TARGET = "regular"
TESTS = [22, 23, 24, 25, 26]
KS = (20, 30, 35, 40, 50, 70, 100, 150)
SEED = 0
DECAY = 0.7
TUNE = 35
INNER_FOLDS = 3
SELECT_BY = "share_L1"
GRID = {"mu": [0.003, 0.01, 0.03], "level": [0.1, 0.3, 1.0]}
ALPHAS = (0.0, 0.25, 0.5, 0.75, 1.0)
GOAL = 2.0
METRICS = ["boxes", "seats_moved", "share_L1", "max_list_error", "bloc_seat_L1",
           "bloc_share_L1", "threshold_errors"]


def methods() -> dict:
    def joint(family: bool):
        return swing_panel(GRID, decay=DECAY, tune_k=TUNE, inner_folds=INNER_FOLDS, ks=KS,
                           family=family, alphas=ALPHAS, select_by=SELECT_BY)
    return {"joint_family": joint(True), "joint_bloc": joint(False)}


def run(names: list[str]) -> None:
    elections = load_all(UNIT, target=TARGET)
    available = methods()
    PARTS_DIR.mkdir(parents=True, exist_ok=True)
    for name in names:
        results = evaluate(elections, {name: available[name]}, list(KS), TESTS, draws=1,
                           seed=SEED)
        results = results[results["method"] != "all_boxes"]
        results.to_csv(PARTS_DIR / f"{name}.csv", index=False)
        print(f"Wrote {PARTS_DIR / f'{name}.csv'}")


def report() -> None:
    parts = [pd.read_csv(p) for p in sorted(PARTS_DIR.glob("*.csv"))]
    earlier = pd.read_csv(REPORTS_DIR / "swing_panel.csv")
    earlier = earlier[earlier["method"].isin(["swing", "level_weight_prior"])]
    results = pd.concat(parts + [earlier])
    by = ["method", "k"]
    table = pd.concat([results.groupby(by)[METRICS].mean(),
                       results.groupby(by)["seats_moved"].max().rename("worst_seats_moved")],
                      axis=1).round(2)
    moved = results.pivot_table(index=by, columns="test", values="seats_moved").round(1)
    params = ["param_mu", "param_level", "param_alpha"]
    chosen = (pd.concat(parts).query("k == @TUNE").set_index(["method", "test"])[params])
    lines = [
        "# Joint level + swing settlement panels - target: regular boxes",
        "",
        f"Held-out test elections {TESTS[0]}-{TESTS[-1]}; `k` = settlements, counted in full",
        "(`boxes` = what that costs). One panel and one set of weights give a level and a",
        "swing prediction, mixed as alpha * level + (1 - alpha) * swing. `joint_family`:",
        "lists of a family that ran as one list in both elections get their previous share",
        "plus the panel's swing, other lists the panel's part of their bloc; `joint_bloc`:",
        "blocs split by the panel only. Weights fit past bloc swings (+ family swings),",
        "plus list-share rows scaled by `level`, pulled to size-proportional weights by",
        f"`mu`. Grid {GRID}, alpha in {list(ALPHAS)}, chosen by inner validation on",
        f"{SELECT_BY} ({INNER_FOLDS} folds, {TUNE} settlements). `swing` and",
        "`level_weight_prior`: the earlier separate models (`swing_panel.md`).",
        f"`seats_moved` = seat L1 / 2; goal: at most {GOAL:g} in the mean and the worst",
        f"election. Seed {SEED}, decay {DECAY}.",
        "",
        "## Mean over test elections, worst election",
        "",
        table.to_markdown(),
        "",
        "## Seats moved per test election",
        "",
        moved.to_markdown(),
        "",
        f"## Chosen setting per test election ({TUNE} settlements)",
        "",
        chosen.to_markdown(),
        "",
    ]
    out = REPORTS_DIR / "joint_panel.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    if sys.argv[1:] == ["--report"]:
        report()
    else:
        run(sys.argv[1:])
