"""Recommended panels for Knesset 27 and their backtest (decisions M24-M31).

Two panel types, each under a vote budget of 1%, 1.5% and 2% of the valid votes
of the last known election, with 3 alternatives per budget:
- settlement: settlements counted in full;
- area: CBS statistical areas, one ballot box counted in each (the K26 box most
  like its area is recommended, with two backups).

Targets:
- a test election 22-26: the whole procedure (inner validation, alternatives,
  panels) runs on the elections before it and the panels are scored on it
  (single-box readings averaged over READINGS draws) ->
  reports/archive/k27_panels/<unit>_backtest_<t>.csv;
- 27: the panels for the next election, fit on every election, with their
  simulated probability of at most 2 seats moved, the in-sample fit of the same
  panel on past elections, and the data the election-night calculator needs ->
  reports/archive/k27_panels/<unit>_final.json.

Usage (targets can run in separate processes):
    PYTHONPATH=src python scripts/recommend_panels.py settlement 22 23 24 25 26 27
    PYTHONPATH=src python scripts/recommend_panels.py area 26
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from election_estimation.data import load_ballots, load_parties
from election_estimation.evaluate import UNITS, load_all, score
from election_estimation.recommend import panel_probability, recommend
from election_estimation.swing import BLOCS, MIN_SHARE, SwingPanel, continuing, seat_intervals

OUT_DIR = Path(__file__).resolve().parents[1] / "reports" / "archive" / "k27_panels"  # superseded by the sector model
TARGET = "regular"
TESTS = [22, 23, 24, 25, 26]
NEXT = 27
BUDGETS = [0.01, 0.015, 0.02]
ALPHAS = (0.0, 0.25, 0.5, 0.75)
ALTERNATIVES = 3
PENALTY = 3.0
SEED = 0
READINGS = 20      # single-box readings per test election
SIM_DRAWS = 1000   # draws for P(at most 2 seats moved)
INTERVAL = 0.9
# Areas are about 2,600 units and a fit takes minutes, so their search is smaller.
CONFIG = {
    "settlement": {"reading": "unit", "candidates": 20, "inner_folds": 3,
                   "grid": {"mu": [0.003, 0.01, 0.03], "level": [0.1, 0.3], "within": [1.0]}},
    "area": {"reading": "single_box", "candidates": 8, "inner_folds": 2,
             "grid": {"mu": [0.003, 0.01, 0.03], "level": [0.1], "within": [1.0]}},
}


def run_alternatives(unit: str, train: list, rng: np.random.Generator) -> list:
    cfg = CONFIG[unit]
    return recommend(train, BUDGETS, cfg["grid"], ALPHAS, cfg["reading"], rng,
                     alternatives=ALTERNATIVES, inner_folds=cfg["inner_folds"],
                     candidates=cfg["candidates"], penalty=PENALTY)


def score_readings(panel: SwingPanel, e, reading: str, rng: np.random.Generator,
                   draws: int, intervals: bool = True) -> dict:
    """Mean metrics over `draws` readings (1 for whole units)."""
    rows = []
    for _ in range(draws if reading == "single_box" else 1):
        pred = panel.predict(e, reading, rng)
        row = score(pred, e)
        if intervals:
            iv = seat_intervals(panel, e, rng, draws=300, level=INTERVAL, pred=pred)
            keep = (e.shares >= MIN_SHARE) | (iv["share"] >= MIN_SHARE)
            out = (iv["low"] - e.seats).clip(lower=0) + (e.seats - iv["high"]).clip(lower=0)
            row["interval_moved"] = float(out.sum() / 2)
            row["coverage"] = float(((e.seats >= iv["low"]) & (e.seats <= iv["high"]))[keep].mean())
        row["within_2"] = float(row["seats_moved"] <= 2)
        rows.append(row)
    return pd.DataFrame(rows).mean().to_dict()


def backtest(unit: str, t: int) -> None:
    reading = CONFIG[unit]["reading"]
    elections = load_all(unit, target=TARGET)
    train, e = [elections[k] for k in sorted(elections) if k < t], elections[t]
    rng = np.random.default_rng(SEED)
    rows = []
    for alt in run_alternatives(unit, train, rng):
        for b, panel in alt.panels.items():
            counted = (e.units.loc[[u for u in panel.units if u in e.units.index]].sum(axis=1)
                       / (e.unit_boxes.reindex(panel.units).dropna() if reading == "single_box"
                          else 1)).sum()
            rows.append({
                "unit": unit, "test": t, "rank": alt.rank, "budget": b, "alpha": alt.alpha,
                **{f"param_{k}": v for k, v in alt.setting.items()},
                "validation_share_L1": alt.validation,
                "error_continuing": panel.errors["continuing"], "error_new": panel.errors["new"],
                "n_units": len(panel.units), "boxes": panel.boxes(e, reading),
                "votes_share": float(counted / e.units.values.sum()),
                "prob_sim": panel_probability(panel, train, rng, draws=SIM_DRAWS),
                **score_readings(panel, e, reading, rng, READINGS),
            })
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT_DIR / f"{unit}_backtest_{t}.csv", index=False)
    print(f"Wrote {OUT_DIR / f'{unit}_backtest_{t}.csv'}")


# --- the panels for the next election ------------------------------------------

def last_ballots(unit: str, knesset: int) -> pd.DataFrame:
    """Regular boxes of `knesset` with their unit."""
    ballots = load_ballots(knesset)
    regular = ballots[~ballots["is_envelopes"] & (ballots["valid"] > 0)].copy()
    regular["unit"] = UNITS[unit](regular, knesset)
    return regular


def unit_rows(unit: str, panel: SwingPanel, e, regular: pd.DataFrame, major: list[str]) -> list:
    """One row per panel unit: label, weight, last-election data for the calculator
    and, for areas, the recommended box and two backups (the boxes whose shares are
    closest to the area's)."""
    w = pd.Series(panel.weights, index=panel.units)
    w = w / w.sum()
    rows = []
    for u in panel.units:
        counts = e.units.loc[u]
        boxes = regular[regular["unit"] == u]
        bloc_counts = counts.groupby(lambda p: e.blocs.get(p, "other")).sum().reindex(BLOCS,
                                                                                      fill_value=0)
        row = {
            "id": u, "weight": round(float(w[u]), 6),
            "settlement": " / ".join(sorted(boxes["settlement_name"].unique())),
            "settlement_code": int(boxes["settlement_code"].iloc[0]),
            "boxes": int(len(boxes)), "votes": int(counts.sum()),
            "prev": {p: int(counts[p]) for p in major},
            "prev_blocs": {b: int(v) for b, v in bloc_counts.items()},
        }
        if unit == "area":
            shares = boxes[e.parties].div(boxes["valid"], axis=0)
            dist = (shares - counts / counts.sum()).abs().sum(axis=1)
            order = boxes.assign(dist=dist.values).sort_values("dist")
            row["recommended"] = [{"ballot": str(r.ballot_id), "center": str(r.concentration),
                                   "votes": int(r.valid)} for r in order.head(3).itertuples()]
        rows.append(row)
    return rows


def final(unit: str) -> None:
    reading = CONFIG[unit]["reading"]
    elections = load_all(unit, target=TARGET)
    train = [elections[k] for k in sorted(elections)]
    last = train[-1]
    regular = last_ballots(unit, last.knesset)
    parties = load_parties(last.knesset)
    major = list(last.shares.index[last.shares >= MIN_SHARE])
    rng = np.random.default_rng(SEED)
    panels = []
    for alt in run_alternatives(unit, train, rng):
        for b, panel in alt.panels.items():
            history = {}
            for t in TESTS:
                past = SwingPanel(panel.units, panel.weights, previous=elections[t - 1],
                                  family=True, alpha=alt.alpha, errors=panel.errors)
                history[t] = round(score_readings(past, elections[t], reading, rng, 10,
                                                  intervals=False)["seats_moved"], 2)
            panels.append({
                "rank": alt.rank, "budget": b, "alpha": alt.alpha, "setting": alt.setting,
                "errors": panel.errors, "validation_share_L1": alt.validation,
                "prob_sim": panel_probability(panel, train, rng, draws=SIM_DRAWS),
                "votes_share": float(sum(
                    last.units.loc[u].sum() / (last.unit_boxes[u] if reading == "single_box" else 1)
                    for u in panel.units) / last.units.values.sum()),
                "insample_seats_moved": history,
                "units": unit_rows(unit, panel, last, regular, major),
            })
    data = {
        "unit": unit, "reading": reading, "next": NEXT, "base": last.knesset,
        "budgets": BUDGETS, "seed": SEED, "grid": CONFIG[unit]["grid"], "alphas": ALPHAS,
        "base_total_votes": int(last.units.values.sum()),
        "base_lists": [{"letter": p, "name": parties.loc[p, "name_he"],
                        "bloc": last.blocs.get(p, "other"), "share": float(last.shares[p]),
                        "seats": int(last.seats[p])} for p in major],
        "base_blocs": {b: float(v) for b, v in
                       last.shares.groupby(lambda p: last.blocs.get(p, "other")).sum()
                       .reindex(BLOCS, fill_value=0).items()},
        "continuing_in_base": continuing(train[-2], last),
        "panels": panels,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"{unit}_final.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    unit, targets = sys.argv[1], [int(a) for a in sys.argv[2:]]
    for t in targets:
        final(unit) if t == NEXT else backtest(unit, t)
