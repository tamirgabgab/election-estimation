"""Compares the calculator in reports/knesset_27_panels.html with the Python model.

Runs scripts/check_panels_site.js (Chromium) and, for the panel the page shows
first for each type, predicts the same example (base-election votes of the
panel's units; for areas the recommended box) with `swing.SwingPanel`. The
page merges lists under 1% into one list, so small differences in shares are
expected; seats must match.

Usage:
    PYTHONPATH=src python scripts/check_panels_site.py <screenshot_dir>
"""

import json
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import pandas as pd

from election_estimation.elections import seat_rules
from election_estimation.evaluate import load_election
from election_estimation.metrics import bader_ofer
from election_estimation.swing import SwingPanel

ROOT = Path(__file__).resolve().parents[1]


def shown_panel(panels: list[dict]) -> dict:
    """The page opens on the best P(at most 2) at the largest budget."""
    top = max(p["budget"] for p in panels)
    return max((p for p in panels if p["budget"] == top), key=lambda p: p["prob_sim"])


def python_forecast(unit: str, data: dict) -> tuple[pd.Series, pd.Series]:
    p = shown_panel(data["panels"])
    base = load_election(data["base"], unit, target="regular")
    ids = [u["id"] for u in p["units"]]
    cur = base
    if unit == "area":
        counts = base.units.copy()
        boxes = base.boxes
        from election_estimation.data import load_ballots
        ballots = load_ballots(data["base"])
        for u in p["units"]:
            r = u["recommended"][0]
            box = ballots[(ballots["settlement_code"] == u["settlement_code"])
                          & (ballots["ballot_id"] == r["ballot"])].iloc[0]
            counts.loc[u["id"]] = box[base.parties].astype(float).values
        cur = replace(base, units=counts, boxes=boxes)
    panel = SwingPanel(ids, [u["weight"] for u in p["units"]], previous=base, family=True,
                       alpha=p["alpha"], errors=p["errors"])
    share = panel.predict(cur, "unit", None).reindex(base.parties, fill_value=0.0)
    share = share / share.sum()
    return share, bader_ofer(share, **seat_rules(data["base"]))


def main(out_dir: str) -> None:
    run = subprocess.run(["node", str(ROOT / "scripts" / "check_panels_site.js"), out_dir],
                         capture_output=True, text=True, check=True)
    page = json.loads(run.stdout.strip().splitlines()[-1])
    print("console errors:", page["errors"] or "none")
    print("horizontal overflow:", page["overflow"])
    ok = not page["errors"] and not any(page["overflow"].values())
    for unit, js in page["forecasts"].items():
        data = json.loads((ROOT / "reports" / "k27_panels" / f"{unit}_final.json")
                          .read_text(encoding="utf-8"))
        share, seats = python_forecast(unit, data)
        diff_seats = sum(abs(js["seats"].get(l, 0) - int(s)) for l, s in seats.items()
                         if l in js["seats"] or s) / 2
        diff_share = max(abs(js["shares"].get(l, 0) - 100 * share[l]) for l in js["shares"]
                         if l in share.index)
        print(f"{unit}: {js['panel']} | seats moved JS vs Python {diff_seats:g}, "
              f"max share gap {diff_share:.2f} pp")
        ok &= diff_seats == 0
    print("ok" if ok else "FAIL")


if __name__ == "__main__":
    main(sys.argv[1])
