"""Knesset 27 panels from the sector ratio model (decisions M31-M37).

The previous election is the last known one (K26); its box counts per area
stand in for those of K27 until the polling station list is published (D17).
For each budget (share of the K26 valid votes) the sector sizes follow the
Neyman allocation (M33) and three alternatives are drawn with the same random
starts shifted by a third of the sampling step (valid samples that barely
overlap; M37: panels are not chosen by past fit). Each area gets the K26 box
closest to its shares as the box to count, with two backups.

Also collects the held-out results per budget (reports/sector_panel/draws_*.csv
and intervals_*.csv) and the per-sector data the election-night calculator
needs. Writes reports/k27_panels/sector_final.json.

Usage:
    PYTHONPATH=src python scripts/recommend_sector_panels.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from election_estimation.data import load_ballots, load_parties
from election_estimation.evaluate import _areas
from election_estimation.sector import allocate, area_election, draw, make_prior
from election_estimation.swing import BLOCS, MIN_SHARE

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "k27_panels" / "sector_final.json"
RESULTS = ROOT / "reports" / "sector_panel"
BASE, NEXT = 26, 27
BUDGETS = [0.01, 0.015, 0.02]
ALTERNATIVES = 3
SEED = 27
OTHER = "אחרות"


def held_out() -> dict:
    """Per budget: held-out mean / worst / within 2 of the direct point, per test,
    and (where run) the medoid point and the interval coverage."""
    d = pd.concat(pd.read_csv(p) for p in sorted(RESULTS.glob("draws_*.csv")))
    d = d[d["variant"] == "sector_neyman"]
    iv = pd.concat(pd.read_csv(p) for p in sorted(RESULTS.glob("intervals_*.csv")))
    out = {}
    for b, g in d.groupby("budget"):
        per = g.groupby("test")["seats_moved"].mean()
        row = {"seats_moved": float(g["seats_moved"].mean()), "worst": float(per.max()),
               "within_2": float((g["seats_moved"] <= 2).mean()),
               "per_test": {int(t): round(float(v), 2) for t, v in per.items()},
               "panels": int(g["draw"].nunique())}
        h = iv[np.isclose(iv["budget"], b)]
        if len(h):
            row |= {"medoid": float(h["medoid"].mean()),
                    "medoid_within_2": float((h["medoid"] <= 2).mean()),
                    "coverage": float(h["coverage"].mean()), "outside": float(h["outside"].mean())}
        out[f"{b:g}"] = row
    return out


def main() -> None:
    prev = area_election(BASE)
    train = [area_election(k) for k in range(19, BASE + 1)]
    settlement = prev.boxes.groupby("unit")["settlement"].agg(lambda s: s.mode().iloc[0])
    prior = make_prior(prev, prev.unit_boxes, settlement, prev.parties,
                       {l: l for l in prev.parties})
    parties = load_parties(BASE)
    major = list(prev.shares.index[prev.shares >= MIN_SHARE])
    minor = [l for l in prev.parties if l not in major]

    def merged(row: pd.Series) -> dict:
        return {**{l: float(row[l]) for l in major}, OTHER: float(row[minor].sum())}

    ballots = load_ballots(BASE)
    regular = ballots[~ballots["is_envelopes"] & (ballots["valid"] > 0)].copy()
    regular["unit"] = _areas(regular, BASE)
    total = int(prev.units.values.sum())
    sectors = []
    for s in prior.sectors:
        areas = prior.sector.index[prior.sector == s]
        m = float(prior.expected[areas].sum())
        share = prior.prev_shares.loc[areas].mul(prior.expected[areas], axis=0).sum() / m
        sectors.append({"id": s, "expected": m, "share_of_votes": m / prior.expected.sum(),
                        "areas": int(len(areas)), "prev_shares": merged(share)})
    panels = []
    for budget in BUDGETS:
        n = allocate(prior, train, budget)
        for j in range(ALTERNATIVES):
            panel = draw(prior, n, np.random.default_rng(SEED + int(1000 * budget)),
                         offset=j / ALTERNATIVES)
            units = []
            for a, mult in panel.sort_index().items():
                boxes = regular[regular["unit"] == a]
                counts = prev.units.loc[a]
                shares = boxes[prev.parties].div(boxes["valid"], axis=0)
                dist = (shares - counts / counts.sum()).abs().sum(axis=1)
                order = boxes.assign(dist=dist.values).sort_values("dist").head(3)
                rec = order.iloc[0]
                units.append({
                    "id": a, "mult": int(mult), "sector": prior.sector[a],
                    "settlement": " / ".join(sorted(boxes["settlement_name"].unique())),
                    "settlement_code": str(rec["settlement_code"]),
                    "boxes": int(len(boxes)), "per_box": float(prior.per_box[a]),
                    "prev_shares": merged(prior.prev_shares.loc[a]),
                    "recommended": [{"ballot": str(r.ballot_id), "center": str(r.concentration),
                                     "votes": int(r.valid), "settlement_code": str(r.settlement_code)}
                                    for r in order.itertuples()],
                    "example": {**{l: int(rec[l]) for l in major},
                                OTHER: int(rec[minor].sum())},
                })
            panels.append({
                "rank": j + 1, "budget": budget, "allocation": {k: int(v) for k, v in n.items()},
                "areas": int(len(panel)), "draws": int(panel.sum()),
                "votes_share": float(prior.cost[panel.index].mul(panel).sum() / total),
                "units": units,
            })
    for p in panels:
        same = [q for q in panels if q["budget"] == p["budget"] and q is not p]
        ids = {u["id"] for u in p["units"]}
        p["overlap"] = max(len(ids & {u["id"] for u in q["units"]}) / len(ids) for q in same)
    lists = [{"letter": l, "name": parties.loc[l, "name_he"], "bloc": prev.blocs.get(l, "other"),
              "share": float(prev.shares[l]), "seats": int(prev.seats[l])} for l in major]
    lists.append({"letter": OTHER, "name": "רשימות מתחת ל-1%", "bloc": "other",
                  "share": float(prev.shares[minor].sum()), "seats": 0, "never_pass": True})
    data = {"base": BASE, "next": NEXT, "seed": SEED, "budgets": BUDGETS, "base_total_votes": total,
            "base_lists": lists, "sectors": sectors, "held_out": held_out(), "panels": panels,
            "blocs": BLOCS}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Wrote {OUT}")
    for p in panels:
        print(p["budget"], p["rank"], p["areas"], f"{100 * p['votes_share']:.2f}%",
              f"overlap {p['overlap']:.0%}", p["allocation"])


if __name__ == "__main__":
    main()
