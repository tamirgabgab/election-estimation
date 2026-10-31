"""Compares the calculator in reports/knesset_27_panels.html with the Python model.

Runs scripts/check_panels_site.js (Chromium) and, for every panel, predicts the
page's example (the K26 votes of each area's recommended box) with
`sector.predict`. The page merges lists under 1% into one list, so small share
differences are possible; the direct seats must match.

Usage:
    PYTHONPATH=src python scripts/check_panels_site.py <screenshot_dir>
"""

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

from election_estimation.data import load_ballots
from election_estimation.elections import seat_rules
from election_estimation.evaluate import _areas
from election_estimation.metrics import bader_ofer
from election_estimation.sector import area_election, make_prior, predict

ROOT = Path(__file__).resolve().parents[1]


def python_forecast(data: dict, p: dict, prior, regular: pd.DataFrame) -> pd.Series:
    panel = pd.Series({u["id"]: u["mult"] for u in p["units"]})
    rows = {}
    for u in p["units"]:
        box = regular[(regular["unit"] == u["id"])
                      & (regular["ballot_id"] == u["recommended"][0]["ballot"])].iloc[0]
        rows[u["id"]] = box[prior.lists].astype(float)
    votes = predict(prior, panel, pd.DataFrame(rows).T)
    return bader_ofer(votes / votes.sum(), **seat_rules(data["base"]))


def main(out_dir: str) -> None:
    run = subprocess.run(["node", str(ROOT / "scripts" / "check_panels_site.js"), out_dir],
                         capture_output=True, text=True, check=True)
    page = json.loads(run.stdout.strip().splitlines()[-1])
    print("console errors:", page["errors"] or "none")
    print("horizontal overflow:", page["overflow"])
    ok = not page["errors"] and not any(page["overflow"].values())
    data = json.loads((ROOT / "reports" / "k27_panels" / "sector_final.json").read_text(encoding="utf-8"))
    base = data["base"]
    prev = area_election(base)
    settlement = prev.boxes.groupby("unit")["settlement"].agg(lambda s: s.mode().iloc[0])
    prior = make_prior(prev, prev.unit_boxes, settlement, prev.parties, {l: l for l in prev.parties})
    ballots = load_ballots(base)
    regular = ballots[~ballots["is_envelopes"] & (ballots["valid"] > 0)].copy()
    regular["unit"] = _areas(regular, base)
    for i, js in page["forecasts"].items():
        seats = python_forecast(data, data["panels"][int(i)], prior, regular)
        diff = sum(abs(js["direct"].get(l, 0) - int(s)) for l, s in seats.items()) / 2
        print(f"{js['panel']} | direct seats moved JS vs Python {diff:g}")
        ok &= diff == 0
    print("ok" if ok else "FAIL")


if __name__ == "__main__":
    main(sys.argv[1])
