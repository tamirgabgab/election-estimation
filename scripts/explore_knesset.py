"""Exploratory analysis of one Knesset election and a first box-selection experiment.

Usage:
    PYTHONPATH=src python scripts/explore_knesset.py 25
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from election_estimation.data import (
    load_ballots,
    load_settlements,
    party_columns,
    share_matrix,
    validate,
)
from election_estimation.selection import exact_selection, greedy_selection, random_baseline

REPORTS_DIR = Path(__file__).resolve().parents[1] / "reports" / "archive"  # earlier experiments
RANDOM_SIZES = [1, 5, 10, 15, 30, 100, 300, 1000, 3000]
MILP_SIZES = [3, 5, 8]
MILP_POOL = 500


def md_table(df: pd.DataFrame) -> str:
    return df.to_markdown()


def main(knesset: int) -> None:
    ballots = load_ballots(knesset)
    settlements = load_settlements(knesset)
    parties = party_columns(ballots)
    double = ballots["is_envelopes"]
    lines = [f"# Knesset {knesset} - exploration", ""]

    lines += ["## Data checks", ""]
    lines += [f"- {k}: {v}" for k, v in validate(ballots).items()]
    totals = ballots[["registered", "voters", "invalid", "valid"]].sum()
    lines += [
        "",
        "## Overview",
        "",
        f"- Ballot rows: {len(ballots):,} ({(~double).sum():,} regular, {double.sum():,} double-envelope)",
        f"- Split sub-boxes (e.g. 283.1): {ballots['is_split'].sum():,}",
        f"- Settlements: {len(settlements):,}",
        f"- Party lists: {len(parties)}",
        f"- Registered: {totals['registered']:,}, voters: {totals['voters']:,}, "
        f"turnout: {totals['voters'] / totals['registered']:.2%}",
        f"- Valid: {totals['valid']:,}, invalid: {totals['invalid']:,}",
        f"- Double-envelope valid votes: {ballots.loc[double, 'valid'].sum():,} "
        f"({ballots.loc[double, 'valid'].sum() / totals['valid']:.2%})",
        "",
    ]

    national = ballots[parties].sum()
    geographic = ballots.loc[~double, parties].sum()
    envelopes = ballots.loc[double, parties].sum()
    shares = pd.DataFrame({
        "votes": national,
        "national_pct": national / national.sum() * 100,
        "regular_boxes_pct": geographic / geographic.sum() * 100,
        "double_envelopes_pct": envelopes / envelopes.sum() * 100,
    }).sort_values("votes", ascending=False)
    gap = (shares["regular_boxes_pct"] - shares["national_pct"]).abs().sum()
    lines += [
        "## National results",
        "",
        md_table(
            shares[shares["national_pct"] >= 0.3]
            .round(2)
            .assign(votes=lambda d: d["votes"].map("{:,}".format))
        ),
        "",
        f"L1 gap between regular boxes only and the national result: {gap:.2f} percentage points.",
        "",
    ]

    box_sizes = ballots.loc[~double, "valid"].describe().round(0)
    lines += ["## Valid votes per regular box", "", md_table(box_sizes.to_frame("valid")), ""]

    X_df, y = share_matrix(ballots, parties)
    X, yv = X_df.values.T, y.values
    counts = ballots.loc[X_df.index, parties]
    major = [p for p in X_df.columns if p != "other"]
    counts = np.column_stack([counts[major].values, counts.drop(columns=major).sum(axis=1).values])
    lines += [
        "## Box selection experiment (in-sample)",
        "",
        f"Features: {len(major)} lists with >= 1% nationally + 'other' "
        f"({len(X_df.columns)} dimensions). Loss: L1 distance in percentage points.",
        "",
    ]

    rows = []
    for k in RANDOM_SIZES:
        losses = random_baseline(counts, yv, k) * 100
        rows.append({"boxes": k, "mean": losses.mean(), "p10": np.percentile(losses, 10),
                     "p90": np.percentile(losses, 90)})
    lines += ["### Random boxes, pooled votes (500 trials)", "",
              md_table(pd.DataFrame(rows).set_index("boxes").round(2)), ""]

    history = greedy_selection(X, yv, max_boxes=len(X_df.columns) + 2)
    greedy = pd.DataFrame([{"boxes": h["k"], "greedy_L1": h["loss"] * 100} for h in history])
    dist = np.abs(X - yv[:, None]).sum(axis=0)
    pool = np.unique(np.concatenate([np.argsort(dist)[:MILP_POOL]] + [h["boxes"] for h in history]))
    milp_rows = []
    for k in MILP_SIZES:
        result = exact_selection(X[:, pool], yv, k, time_limit=90)
        milp_rows.append({"boxes": k, "milp_L1": result["loss"] * 100,
                          "proven_optimal": result["optimal"]})
    table = greedy.merge(pd.DataFrame(milp_rows), on="boxes", how="left").set_index("boxes")
    lines += ["### Optimized weights: greedy column generation vs MILP", "",
              f"MILP runs on a pool of {len(pool)} candidate boxes with a 90s limit.", "",
              md_table(table.round(3).astype(object).fillna("")), ""]

    exact = history[-1]
    chosen = ballots.loc[X_df.index[exact["boxes"]], ["settlement_name", "ballot_id", "valid"]].copy()
    chosen["weight_pct"] = exact["weights"] * 100
    chosen["L1_to_national"] = dist[exact["boxes"]] * 100
    lines += [f"### The {exact['k']} boxes that reproduce the national result", "",
              md_table(chosen.sort_values("weight_pct", ascending=False).round(2)), ""]

    REPORTS_DIR.mkdir(exist_ok=True)
    out = REPORTS_DIR / f"knesset_{knesset}_exploration.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 25)
