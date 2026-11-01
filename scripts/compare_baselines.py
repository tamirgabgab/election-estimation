"""Compares every unit and method at the same counting budget (ballot boxes).

Reads reports/baselines_<unit>.csv (from run_baselines.py) and keeps the
configurations that count about k boxes: single-box readings and the
budget methods. Writes reports/archive/baselines_summary.md.

Usage:
    PYTHONPATH=src python scripts/compare_baselines.py
"""

from pathlib import Path

import pandas as pd

REPORTS_DIR = Path(__file__).resolve().parents[1] / "reports" / "archive"  # earlier experiments
UNITS = ["settlement", "base_box", "area"]
TESTS = [22, 23, 24, 25, 26]
BUDGETS = [35, 50, 70, 100]
METRICS = ["boxes", "seat_L1", "share_L1", "bloc_seat_L1", "threshold_errors"]


def budget_rows(unit: str) -> pd.DataFrame:
    r = pd.read_csv(REPORTS_DIR / f"baselines_{unit}.csv")
    r = r[r["test"].isin(TESTS) & r["k"].isin(BUDGETS)]
    by_box = (r["reading"] == "single_box") | r["method"].str.endswith("_budget")
    r = r[by_box].assign(unit=unit)
    return r.groupby(["k", "unit", "method", "reading"])[METRICS].mean()


def main() -> None:
    table = pd.concat([budget_rows(u) for u in UNITS if (REPORTS_DIR / f"baselines_{u}.csv").exists()])
    floor = pd.read_csv(REPORTS_DIR / "baselines_settlement.csv")
    floor = floor[(floor["method"] == "all_boxes") & floor["test"].isin(TESTS)][METRICS].mean()
    lines = [
        "# Baselines at equal counting budgets",
        "",
        f"Mean over held-out test elections {TESTS[0]}-{TESTS[-1]}. `k` is the budget in ballot",
        "boxes; `boxes` is what was actually counted (budget methods estimate unit costs from",
        "the last training election, so they can overshoot slightly). Only configurations that",
        "count about k boxes are shown: one box per panel unit (`single_box`) or whole units",
        "under a box budget (`*_budget`). Seats in seats, shares in percentage points.",
        "",
        f"Floor - counting every regular box: {floor['seat_L1']:.1f} seats, "
        f"{floor['share_L1']:.2f} pp (the double-envelope gap).",
        "",
    ]
    for k in BUDGETS:
        sub = table.xs(k, level="k").sort_values("seat_L1")
        lines += [f"## Budget {k} boxes", "", sub.round(2).to_markdown(), ""]
    out = REPORTS_DIR / "baselines_summary.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
