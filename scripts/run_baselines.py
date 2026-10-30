"""Held-out evaluation of the baseline panel methods.

Usage:
    PYTHONPATH=src python scripts/run_baselines.py settlement
    PYTHONPATH=src python scripts/run_baselines.py base_box
    PYTHONPATH=src python scripts/run_baselines.py base_box --report-only   # rewrite the .md from the .csv
"""

import sys
from pathlib import Path

import pandas as pd

from election_estimation.data import KNESSETS
from election_estimation.evaluate import (
    evaluate,
    greedy_weighted,
    load_all,
    random_pooled,
    random_pps,
)

REPORTS_DIR = Path(__file__).resolve().parents[1] / "reports"
KS = [10, 20, 35, 50, 70, 100]
TESTS = KNESSETS[1:]
RECENT = [22, 23, 24, 25, 26]
DRAWS = 30
SEED = 0
DECAY = 0.7
CANDIDATES = 40
METRICS = ["seat_L1", "share_L1", "bloc_seat_L1", "bloc_share_L1", "threshold_errors",
           "max_list_error"]


def summary(results: pd.DataFrame, tests: list[int]) -> pd.DataFrame:
    sub = results[results["test"].isin(tests)]
    sub = sub.assign(k=sub["k"].where(sub["method"] != "all_boxes", "all").astype(str))
    table = sub.groupby(["method", "reading", "k"])[METRICS].mean()
    return table.sort_index(key=lambda i: i.map(lambda v: int(v) if v.isdigit() else -1)
                            if i.name == "k" else i)


def main(unit: str, rerun: bool = True) -> None:
    csv = REPORTS_DIR / f"baselines_{unit}.csv"
    if rerun:
        elections = load_all(unit)
        methods = {
            "random_pooled": random_pooled,
            "random_pps": random_pps,
            "greedy": greedy_weighted(decay=DECAY, candidates=CANDIDATES),
        }
        results = evaluate(elections, methods, KS, TESTS, draws=DRAWS, seed=SEED)
        REPORTS_DIR.mkdir(exist_ok=True)
        results.to_csv(csv, index=False)
    else:
        results = pd.read_csv(csv)

    all_boxes = results[results["method"] == "all_boxes"].set_index("test")[METRICS]
    lines = [
        f"# Baselines - unit: {unit}",
        "",
        "Held-out evaluation: for every test election t, panels are chosen on the elections",
        "before t only. Errors: `seat_L1` and `bloc_seat_L1` in seats, the others in",
        "percentage points of valid votes; `threshold_errors` counts lists whose",
        "pass / fail is predicted wrongly.",
        "",
        f"Settings: seed {SEED}, {DRAWS} draws for random panels and single-box readings,",
        f"greedy recency decay {DECAY}, {CANDIDATES} candidates per step, panel sizes {KS}.",
        "`unit` reading counts whole panel units; `single_box` counts one random box per unit.",
        "",
        "Methods: `all_boxes` pools every regular box (no sampling; its error is the",
        "double-envelope gap); `random_pooled` draws units uniformly and pools their votes;",
        "`random_pps` draws units in proportion to size and averages their shares;",
        "`greedy` is column generation with LP weights on the stacked training elections.",
        "",
        f"## Mean over recent test elections ({RECENT[0]}-{RECENT[-1]})",
        "",
        summary(results, RECENT).round(2).to_markdown(),
        "",
        f"## Mean over all test elections ({TESTS[0]}-{TESTS[-1]})",
        "",
        summary(results, TESTS).round(2).to_markdown(),
        "",
        "## All boxes per test election",
        "",
        all_boxes.round(2).to_markdown(),
        "",
    ]
    out = REPORTS_DIR / f"baselines_{unit}.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "settlement", rerun="--report-only" not in sys.argv)
