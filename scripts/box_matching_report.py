"""Report on how well base ballot boxes match across elections.

Usage:
    PYTHONPATH=src python scripts/box_matching_report.py
"""

from pathlib import Path

import pandas as pd

from election_estimation.matching import (
    consecutive_report,
    load_all,
    panel_window_survival,
    survival_matrix,
)

REPORTS_DIR = Path(__file__).resolve().parents[1] / "reports" / "archive"  # earlier experiments
PCT_COLUMNS = ["box_survival", "vote_survival", "settlement_vote_survival", "within_25pct",
               "matched_closer"]


def main() -> None:
    boxes = load_all()
    counts = pd.DataFrame({
        "base_boxes": {k: len(v) for k, v in boxes.items()},
        "split_base_boxes": {k: int((v["sub_boxes"] > 1).sum()) for k, v in boxes.items()},
        "registered_per_base_box": {k: round(v["registered"].mean()) for k, v in boxes.items()},
    })
    pairs = consecutive_report(boxes)
    pairs[PCT_COLUMNS] = pairs[PCT_COLUMNS] * 100
    matrix = survival_matrix(boxes) * 100

    lines = [
        "# Base ballot box matching across elections",
        "",
        "Base box key: `<settlement_code>_<base number>`; sub-boxes (`283.1`, `283.2`) are",
        "merged into `283`, and Knesset 16-17 ids are divided by ten. Double envelopes are",
        "excluded.",
        "",
        "## Base boxes per election",
        "",
        counts.to_markdown(),
        "",
        "## Consecutive elections",
        "",
        "- `box_survival`, `vote_survival`: % of base boxes / valid votes of the earlier",
        "  election whose key exists in the later one.",
        "- `settlement_vote_survival`: the same at settlement level.",
        "- `median_abs_log_ratio`, `within_25pct`: registered-voter drift of matched boxes.",
        "- `matched_L1_median` vs `decoy_L1_median`: bloc-share L1 distance (pp, after removing",
        "  the national bloc swing) between a box and its namesake, and between the box and a",
        "  random other box of the same settlement. `matched_closer`: % of matched pairs closer",
        "  than their decoy.",
        "",
        pairs.round(2).to_markdown(),
        "",
        "## Survival matrix",
        "",
        "Row t, column s: % of the valid votes of election t cast in base boxes whose key also",
        "exists in election s.",
        "",
        matrix.round(0).astype(int).to_markdown(),
        "",
    ]
    for target in (25, 26):
        lines += [
            f"## Fixed panel used in Knesset {target}",
            "",
            "Base boxes that exist in every election from `train_from` to the target, and the",
            "share of the target's valid votes they hold.",
            "",
            panel_window_survival(boxes, target).round(3).to_markdown(),
            "",
        ]

    REPORTS_DIR.mkdir(exist_ok=True)
    out = REPORTS_DIR / "box_matching.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
