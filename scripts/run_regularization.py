"""Held-out comparison of weight regularizations for budget panels.

Each regularization's strength is chosen by inner validation on the training
elections only (`evaluate.greedy_regularized`). Compared with the plain greedy
budget panel under the same settings.

Usage:
    PYTHONPATH=src python scripts/run_regularization.py area
    PYTHONPATH=src python scripts/run_regularization.py base_box
"""

import sys
from pathlib import Path

import pandas as pd

from election_estimation.evaluate import evaluate, greedy_budget, greedy_regularized, load_all

REPORTS_DIR = Path(__file__).resolve().parents[1] / "reports"
TESTS = [22, 23, 24, 25, 26]
KS = (35, 50, 70)
SEED = 0
DECAY = 0.7
CANDIDATES = 20
TUNE_BUDGET = 50
INNER_FOLDS = 2
GRIDS = {
    "weight_prior": {"mu": [0.003, 0.01, 0.03]},
    "calibration": {"calibration": [0.3, 1.0]},
    "noise": {"noise": [0.1, 0.3]},
}
METRICS = ["boxes", "seat_L1", "share_L1", "bloc_seat_L1", "bloc_share_L1", "threshold_errors"]


def main(unit: str) -> None:
    elections = load_all(unit)
    methods = {"greedy_budget": greedy_budget(decay=DECAY, candidates=CANDIDATES)}
    methods["greedy_budget"].ks = KS
    for name, grid in GRIDS.items():
        methods[name] = greedy_regularized(grid, decay=DECAY, candidates=CANDIDATES,
                                           tune_budget=TUNE_BUDGET, inner_folds=INNER_FOLDS, ks=KS)
    results = evaluate(elections, methods, list(KS), TESTS, draws=1, seed=SEED)
    REPORTS_DIR.mkdir(exist_ok=True)
    results.to_csv(REPORTS_DIR / f"regularization_{unit}.csv", index=False)

    sub = results[results["method"] != "all_boxes"]
    table = sub.groupby(["k", "method"])[METRICS].mean().round(2)
    params = [c for c in results.columns if c.startswith("param_")]
    chosen = sub[sub["k"] == TUNE_BUDGET].set_index(["method", "test"])[params].dropna(how="all")
    lines = [
        f"# Weight regularization - unit: {unit}",
        "",
        f"Held-out test elections {TESTS[0]}-{TESTS[-1]}; panels under a box budget `k`, whole",
        "units counted. Each regularization's strength is chosen per test election by inner",
        f"validation (the last {INNER_FOLDS} training elections, each predicted from the ones",
        f"before it, at {TUNE_BUDGET} boxes, lowest seat L1). Seed {SEED}, recency decay {DECAY},",
        f"{CANDIDATES} greedy candidates per step, grids {GRIDS}.",
        "",
        "- `weight_prior`: L1 pull of the weights towards size-proportional weights (`mu`).",
        "- `calibration`: extra targets per bloc-profile stratum (`calibration` = their weight).",
        "- `noise`: perturbed copies of the training elections (`noise` = log-normal sigma).",
        "",
        "## Mean over test elections",
        "",
        table.to_markdown(),
        "",
        f"## Chosen strength per test election (at {TUNE_BUDGET} boxes)",
        "",
        chosen.to_markdown(),
        "",
    ]
    out = REPORTS_DIR / f"regularization_{unit}.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "area")
