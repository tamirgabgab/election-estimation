"""Where do the seats moved come from? Decomposes the held-out seat error of the
within-bloc swing panels (reports/within_panel/lists_<t>.csv, settlements
20-150, test elections 22-26) into parts, by counterfactual steps from the
prediction towards the truth:

1. threshold - lists on the wrong side of the threshold are moved just across it
   (everything else stays predicted); the seats this step fixes;
2. bloc - each bloc is scaled to its true total, the split inside it kept;
3. within bloc - what is left: the true bloc totals with the predicted split.

Steps 2-3 together are the error with the right lists passing. Also reports the
"smooth" error (share L1 of passing lists in seat units, no rounding), the seat
error per bloc, and how much of the error the new lists carry.

Usage:
    PYTHONPATH=src python scripts/diagnose_errors.py
"""

from pathlib import Path

import pandas as pd

from election_estimation.data import load_parties
from election_estimation.elections import seat_rules
from election_estimation.metrics import bader_ofer
from election_estimation.swing import BLOCS, continuing

ROOT = Path(__file__).resolve().parents[1]
IN_DIR = ROOT / "reports" / "within_panel"
OUT = ROOT / "reports" / "error_decomposition.md"
OTHER = "_other"
EPS = 1e-6


def seats(share: pd.Series, rules: dict) -> pd.Series:
    """Seats of shares that cover only the listed lists (the rest is OTHER)."""
    s = pd.concat([share, pd.Series({OTHER: max(0.0, 1 - share.sum())})])
    return bader_ofer(s, never_pass=(OTHER,), **rules).drop(OTHER)


def moved(a: pd.Series, b: pd.Series) -> float:
    return float((a - b).abs().sum() / 2)


def decompose(g: pd.DataFrame, t: int) -> dict:
    rules = seat_rules(t)
    thr = rules["threshold"]
    g = g.set_index("letter")
    p, true = g["share"], g["true_share"]
    s_true = seats(true, rules)
    s_pred = seats(p, rules)
    assert (s_pred == g["seats"]).all(), "recomputed seats differ from the stored ones"
    # 1. threshold: move wrong-side lists just across it.
    fixed = p.copy()
    up = (true >= thr) & (p < thr)
    down = (true < thr) & (p >= thr)
    fixed[up] = thr + EPS
    fixed[down] = thr - EPS
    s_fixed = seats(fixed, rules)
    # 2. bloc totals to the truth, split kept.
    bloc = pd.Series(load_parties(t)["bloc"]).reindex(g.index).fillna("other")
    scaled = fixed * true.groupby(bloc).transform("sum") / fixed.groupby(bloc).transform("sum")
    scaled[up] = scaled[up].clip(lower=thr + EPS)
    scaled[down] = scaled[down].clip(upper=thr - EPS)
    s_scaled = seats(scaled, rules)
    passing = s_true.index[(true >= thr) | (p >= thr)]
    new = ~g.index.isin(list(continuing_lists(t)))
    per_bloc = (s_pred - s_true).groupby(bloc).sum()
    return {
        "test": t, "k": int(g["k"].iloc[0]),
        "seats_moved": moved(s_pred, s_true),
        "threshold": moved(s_pred, s_true) - moved(s_fixed, s_true),
        "bloc": moved(s_fixed, s_true) - moved(s_scaled, s_true),
        "within": moved(s_scaled, s_true),
        "smooth": float(120 * (p - true)[passing].abs().sum() / 2),
        "wrong_side": int(up.sum() + down.sum()),
        "new_lists_moved": float((s_pred - s_true)[new].abs().sum() / 2),
        **{f"bloc_{b}": float(per_bloc.get(b, 0)) for b in BLOCS},
    }


def continuing_lists(t: int) -> set:
    from election_estimation.evaluate import load_election
    return set(continuing(load_election(t - 1, "settlement", "regular"),
                          load_election(t, "settlement", "regular")))


def main() -> None:
    rows = []
    for path in sorted(IN_DIR.glob("lists_*.csv")):
        d = pd.read_csv(path)
        for (t, k), g in d.groupby(["test", "k"]):
            rows.append(decompose(g, int(t)))
    r = pd.DataFrame(rows)
    cols = ["seats_moved", "threshold", "bloc", "within", "smooth", "wrong_side",
            "new_lists_moved"]
    by_k = r.groupby("k")[cols].mean().round(2)
    by_t = r.groupby("test")[cols + [f"bloc_{b}" for b in BLOCS]].mean().round(2)
    share = (r[["threshold", "bloc", "within"]].sum() / r["seats_moved"].sum()).round(2)
    text = ["# Seat error decomposition (held-out within-bloc swing panels)", "",
            "Source: `reports/within_panel/lists_<t>.csv` (settlements 20-150, tests 22-26), "
            "built by `scripts/diagnose_errors.py`. Columns are seats moved; `smooth` is the "
            "share L1 of passing lists in seats (no rounding); `bloc_<b>` is the signed seat "
            "error of the bloc (prediction minus truth).", "",
            f"Share of all seats moved: threshold {share['threshold']:.0%}, "
            f"bloc totals {share['bloc']:.0%}, within bloc {share['within']:.0%}.", "",
            "## By panel size", "", by_k.to_markdown(), "",
            "## By test election (mean over sizes)", "", by_t.to_markdown(), ""]
    OUT.write_text("\n".join(text), encoding="utf-8")
    print("\n".join(text[6:]))


if __name__ == "__main__":
    main()
