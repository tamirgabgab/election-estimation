"""Joint panels with within-bloc rows, and seat intervals (decisions M20-M23).

Method `joint_within`: the `joint_family` panel of run_joint_panel.py plus rows
asking the panel to reproduce how every bloc splits into its lists (`within`).
`mu`, `level`, `within` and `alpha` are chosen by inner validation on share L1
over the last 3 training elections.

Every prediction also gets a 90% seat interval and the probability of passing
the threshold per list, by simulating the panel's own standardized errors in
the inner validation folds (at 35 settlements), separately for continuing and
new lists (`swing.seat_intervals`). Scored per test election:
- seats_moved: the point prediction, as before;
- interval_moved: half the seats by which the true result lies outside the
  intervals (0 when every list's true seats are inside its interval);
- coverage: share of lists (at least 1% true or predicted) whose true seats
  are inside the interval; width: mean interval width in seats.

Test elections can run in separate processes; each writes
reports/archive/within_panel/test_<t>.csv and `--report` merges them into
reports/archive/within_panel.md.

Usage:
    PYTHONPATH=src python scripts/run_within_panel.py 22 23
    PYTHONPATH=src python scripts/run_within_panel.py --report
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from election_estimation.evaluate import load_all, score
from election_estimation.swing import MIN_SHARE, seat_intervals, swing_panel

REPORTS_DIR = Path(__file__).resolve().parents[1] / "reports" / "archive"  # earlier experiments
PARTS_DIR = REPORTS_DIR / "within_panel"
UNIT = "settlement"
TARGET = "regular"
TESTS = [22, 23, 24, 25, 26]
KS = (20, 30, 35, 40, 50, 70, 100, 150)
SEED = 0
DECAY = 0.7
TUNE = 35
INNER_FOLDS = 3
SELECT_BY = "share_L1"
GRID = {"mu": [0.003, 0.01, 0.03], "level": [0.1, 0.3, 1.0], "within": [0.3, 1.0]}
ALPHAS = (0.0, 0.25, 0.5, 0.75, 1.0)
DRAWS = 1000
INTERVAL = 0.9
GOAL = 2.0


def run(tests: list[int]) -> None:
    elections = load_all(UNIT, target=TARGET)
    method = swing_panel(GRID, decay=DECAY, tune_k=TUNE, inner_folds=INNER_FOLDS, ks=KS,
                         family=True, alphas=ALPHAS, select_by=SELECT_BY)
    PARTS_DIR.mkdir(parents=True, exist_ok=True)
    for t in tests:
        rng = np.random.default_rng(SEED)
        train = [elections[k] for k in sorted(elections) if k < t]
        e = elections[t]
        panels = method(train, list(KS), rng)
        rows, lists = [], []
        for k, panel in panels.items():
            iv = seat_intervals(panel, e, rng, draws=DRAWS, level=INTERVAL)
            iv["true_share"], iv["true_seats"] = e.shares, e.seats
            keep = (iv["true_share"] >= MIN_SHARE) | (iv["share"] >= MIN_SHARE)
            outside = (iv["low"] - iv["true_seats"]).clip(lower=0) \
                + (iv["true_seats"] - iv["high"]).clip(lower=0)
            inside = (iv["true_seats"] >= iv["low"]) & (iv["true_seats"] <= iv["high"])
            rows.append({"test": t, "method": "joint_within", "k": k,
                         "boxes": panel.boxes(e, "unit"),
                         **{f"param_{p}": v for p, v in panel.info.items()},
                         **{f"error_{p}": v for p, v in panel.errors.items()},
                         **score(panel.predict(e, "unit", rng), e),
                         "interval_moved": float(outside.sum() / 2),
                         "coverage": float(inside[keep].mean()),
                         "width": float((iv["high"] - iv["low"])[keep].mean())})
            lists.append(iv[keep].assign(test=t, k=k))
        pd.DataFrame(rows).to_csv(PARTS_DIR / f"test_{t}.csv", index=False)
        pd.concat(lists).rename_axis("letter").to_csv(PARTS_DIR / f"lists_{t}.csv")
        print(f"Wrote {PARTS_DIR / f'test_{t}.csv'}")


def report() -> None:
    new = pd.concat([pd.read_csv(p) for p in sorted(PARTS_DIR.glob("test_*.csv"))])
    earlier = pd.read_csv(REPORTS_DIR / "joint_panel" / "joint_family.csv")
    results = pd.concat([new, earlier])
    by = ["method", "k"]
    metrics = ["boxes", "seats_moved", "share_L1", "max_list_error", "threshold_errors",
               "interval_moved", "coverage", "width"]
    table = pd.concat([results.groupby(by)[metrics].mean(),
                       results.groupby(by)["seats_moved"].max().rename("worst_seats_moved"),
                       results.groupby(by)["interval_moved"].max().rename("worst_interval_moved")],
                      axis=1).round(2)
    moved = results.pivot_table(index=by, columns="test", values="seats_moved").round(1)
    chosen = new[new["k"] == TUNE].set_index("test")[
        [c for c in new.columns if c.startswith(("param_", "error_"))]].round(3)
    lists = pd.concat([pd.read_csv(p) for p in sorted(PARTS_DIR.glob("lists_*.csv"))])
    rules = lists[(lists["k"] == TUNE) & lists["p_pass"].between(0.05, 0.95)]
    near = rules[["test", "letter", "share", "true_share", "p_pass", "seats", "low", "high",
                  "true_seats"]].round(3)
    lines = [
        "# Joint panels with within-bloc rows and seat intervals - target: regular boxes",
        "",
        f"Held-out test elections {TESTS[0]}-{TESTS[-1]}; `k` = settlements, counted in full.",
        "`joint_within`: `joint_family` (see `joint_panel.md`) plus rows asking the panel to",
        "reproduce the split of every bloc into its lists. Grid",
        f"{GRID}, alpha in {list(ALPHAS)}, chosen by inner validation on {SELECT_BY}",
        f"({INNER_FOLDS} folds, {TUNE} settlements). Seed {SEED}, decay {DECAY}.",
        "",
        f"Seat intervals: {INTERVAL:.0%} central intervals from {DRAWS} simulations of the",
        "panel's own standardized errors in the inner validation folds, separately for",
        "continuing and new lists. `interval_moved` = half the seats by which the true",
        "result lies outside the intervals; `coverage` = share of lists (>= 1%) whose true",
        "seats are inside; `width` = mean interval width. Goal for the point prediction:",
        f"at most {GOAL:g} seats moved in the mean and the worst election.",
        "",
        "## Mean over test elections, worst election",
        "",
        table.to_markdown(),
        "",
        "## Seats moved per test election",
        "",
        moved.to_markdown(),
        "",
        f"## Chosen setting and error scales per test election ({TUNE} settlements)",
        "",
        chosen.to_markdown(),
        "",
        f"## Lists with an uncertain threshold ({TUNE} settlements, 5% < P(pass) < 95%)",
        "",
        near.to_markdown(index=False) if len(near) else "None.",
        "",
    ]
    out = REPORTS_DIR / "within_panel.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    if sys.argv[1:] == ["--report"]:
        report()
    else:
        run([int(a) for a in sys.argv[1:]] or TESTS)
