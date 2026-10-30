"""Matching base ballot boxes across elections.

A base box is identified by `<settlement_code>_<base number>` (see
`data.load_ballots`). The fixed-panel model assumes such a key names the same
polling place in every election. This module measures how far that holds:

- survival: share of base boxes (and of their votes) whose key reappears;
- size drift: change in registered voters of matched boxes;
- identity: whether a matched box votes like its namesake (bloc-share L1
  distance), compared with another box of the same settlement.
"""

import numpy as np
import pandas as pd

from election_estimation.data import KNESSETS, base_boxes

BLOCS = ["right", "center_left", "haredi", "arab", "other"]


def bloc_shares(boxes: pd.DataFrame) -> pd.DataFrame:
    cols = [b for b in BLOCS if b in boxes.columns]
    shares = boxes[cols].div(boxes["valid"].where(boxes["valid"] > 0), axis=0)
    return shares.reindex(columns=BLOCS, fill_value=0.0).fillna(0.0)


def load_all(knessets=KNESSETS, scheme: str = "four_blocs") -> dict[int, pd.DataFrame]:
    return {k: base_boxes(k, scheme) for k in knessets}


def survival(a: pd.DataFrame, b: pd.DataFrame) -> dict[str, float]:
    """Survival of the base boxes of election `a` into election `b`."""
    matched = a.index.isin(b.index)
    settlements = a["settlement_code"].isin(b["settlement_code"])
    return {
        "boxes": len(a),
        "box_survival": matched.mean(),
        "vote_survival": a.loc[matched, "valid"].sum() / a["valid"].sum(),
        "settlement_vote_survival": a.loc[settlements, "valid"].sum() / a["valid"].sum(),
    }


def drift(a: pd.DataFrame, b: pd.DataFrame) -> dict[str, float]:
    """Registered-voter change of matched boxes (b relative to a)."""
    keys = a.index.intersection(b.index)
    ra, rb = a.loc[keys, "registered"], b.loc[keys, "registered"]
    ok = (ra > 0) & (rb > 0)
    log_ratio = np.log(rb[ok] / ra[ok])
    return {
        "median_abs_log_ratio": float(np.median(np.abs(log_ratio))),
        "within_25pct": float((np.abs(np.exp(log_ratio) - 1) <= 0.25).mean()),
    }


def identity(a: pd.DataFrame, b: pd.DataFrame, seed: int = 0) -> dict[str, float]:
    """Bloc-share L1 distance of matched boxes vs. a same-settlement decoy.

    For every matched box in a settlement with at least two boxes in `b`, the
    decoy is a random other box of the same settlement in `b`. If keys name
    the same polling place, matched distances are much smaller than decoys.
    The national bloc swing between the elections is removed first (uniform
    swing), so it inflates neither distance.
    """
    rng = np.random.default_rng(seed)
    sa, sb = bloc_shares(a), bloc_shares(b)
    swing = (a[BLOCS].sum() / a["valid"].sum()) - (b[BLOCS].sum() / b["valid"].sum())
    sb = sb + swing
    by_settlement = b.groupby("settlement_code").groups
    matched, decoy = [], []
    for key in a.index.intersection(b.index):
        siblings = by_settlement[a.at[key, "settlement_code"]]
        if len(siblings) < 2:
            continue
        other = key
        while other == key:
            other = siblings[rng.integers(len(siblings))]
        matched.append(np.abs(sa.loc[key] - sb.loc[key]).sum())
        decoy.append(np.abs(sa.loc[key] - sb.loc[other]).sum())
    matched, decoy = np.array(matched) * 100, np.array(decoy) * 100
    return {
        "pairs": len(matched),
        "matched_L1_median": float(np.median(matched)),
        "decoy_L1_median": float(np.median(decoy)),
        "matched_closer": float((matched < decoy).mean()),
    }


def consecutive_report(boxes: dict[int, pd.DataFrame]) -> pd.DataFrame:
    ks = sorted(boxes)
    rows = []
    for t, s in zip(ks, ks[1:]):
        a, b = boxes[t], boxes[s]
        rows.append({"from": t, "to": s, **survival(a, b), **drift(a, b), **identity(a, b)})
    return pd.DataFrame(rows).set_index(["from", "to"])


def survival_matrix(boxes: dict[int, pd.DataFrame], weight: str = "valid") -> pd.DataFrame:
    """Share of the votes of election t (rows) cast in boxes whose key exists in s."""
    ks = sorted(boxes)
    out = pd.DataFrame(index=ks, columns=ks, dtype=float)
    for t in ks:
        a = boxes[t]
        for s in ks:
            matched = a.index.isin(boxes[s].index)
            out.loc[t, s] = a.loc[matched, weight].sum() / a[weight].sum()
    return out


def panel_window_survival(boxes: dict[int, pd.DataFrame], target: int) -> pd.DataFrame:
    """For a panel chosen on elections first..target-1 and used in `target`:
    share of target's votes in base boxes that exist in every election of the window."""
    ks = sorted(k for k in boxes if k < target)
    rows = []
    for first in ks:
        window = [k for k in ks if k >= first] + [target]
        common = boxes[target].index
        for k in window:
            common = common.intersection(boxes[k].index)
        t = boxes[target]
        rows.append({
            "train_from": first,
            "elections_in_window": len(window),
            "common_boxes": len(common),
            "target_vote_share": t.loc[common, "valid"].sum() / t["valid"].sum(),
        })
    return pd.DataFrame(rows).set_index("train_from")
