"""Builds reports/knesset_27_panels.html: the recommended Knesset 27 panels.

Reads reports/k27_panels/<unit>_final.json and <unit>_backtest_<t>.csv (from
recommend_panels.py) and the template scripts/templates/panels.html. The page
holds the panel comparison, the chosen panel's units and backtest, and an
election-night calculator that mirrors `swing.SwingPanel.predict` in
JavaScript. Lists under 1% in the base election are merged into one "other"
list that never passes the threshold (the calculator works on these lists).

The template has two parts split by "<!--BODY-->"; the repository page wraps
them in a full document, `--fragment <path>` also writes them unwrapped (for
publishing as an artifact).

Usage:
    PYTHONPATH=src python scripts/build_panels_site.py [--fragment <path>]
"""

import json
import sys
from datetime import date
from pathlib import Path

import pandas as pd

from election_estimation.data import load_ballots
from election_estimation.elections import seat_rules
from election_estimation.swing import BLOCS

ROOT = Path(__file__).resolve().parents[1]
IN_DIR = ROOT / "reports" / "k27_panels"
TEMPLATE = ROOT / "scripts" / "templates" / "panels.html"
OUT = ROOT / "reports" / "knesset_27_panels.html"
TYPES = ["settlement", "area"]
OTHER = "אחרות"
CAP = 0.02


def summary(unit: str) -> dict:
    """Backtest of every (alternative rank, budget): mean and worst seats moved,
    share of readings within 2 seats, interval coverage, per test election."""
    parts = [pd.read_csv(p) for p in sorted(IN_DIR.glob(f"{unit}_backtest_*.csv"))]
    if not parts:
        return {}
    r = pd.concat(parts)
    out = {}
    for (rank, budget), g in r.groupby(["rank", "budget"]):
        out[f"{rank}_{budget}"] = {
            "seats_moved": float(g["seats_moved"].mean()), "worst": float(g["seats_moved"].max()),
            "within_2": float(g["within_2"].mean()), "coverage": float(g["coverage"].mean()),
            "interval_moved": float(g["interval_moved"].mean()),
            "per_test": {int(t): float(v) for t, v in zip(g["test"], g["seats_moved"])},
        }
    return out


def add_other(data: dict, ballots: pd.DataFrame) -> None:
    """Merge lists under 1% into OTHER, add the example counts (base-election votes:
    the whole settlement, or the recommended box of an area) and box counts."""
    major = [l["letter"] for l in data["base_lists"]]
    bloc = {l["letter"]: l["bloc"] for l in data["base_lists"]} | {OTHER: "other"}
    other_share = 1 - sum(l["share"] for l in data["base_lists"])
    data["base_lists"].append({"letter": OTHER, "name": "רשימות מתחת ל-1%", "bloc": "other",
                               "share": other_share, "seats": 0, "never_pass": True})
    data["base_blocs"] = {b: sum(l["share"] for l in data["base_lists"] if l["bloc"] == b)
                          for b in BLOCS}
    parties = [c for c in ballots.columns if c in major] + [OTHER]
    for p in data["panels"]:
        for u in p["units"]:
            u["prev"][OTHER] = u["votes"] - sum(u["prev"].values())
            u["prev_blocs"] = {b: sum(v for l, v in u["prev"].items() if bloc[l] == b)
                               for b in BLOCS}
            if data["unit"] == "area":
                r = u["recommended"][0]
                box = ballots[(ballots["settlement_code"] == u["settlement_code"])
                              & (ballots["ballot_id"] == r["ballot"])].iloc[0]
                ex = {l: int(box[l]) for l in major}
                ex[OTHER] = int(box["valid"]) - sum(ex.values())
                u["example"] = ex
            else:
                u["example"] = dict(u["prev"])
        p["n_boxes"] = (len(p["units"]) if data["unit"] == "area"
                        else sum(u["boxes"] for u in p["units"]))
    assert all(c in parties for c in major)


def main(fragment: Path | None) -> None:
    finals = {u: json.loads((IN_DIR / f"{u}_final.json").read_text(encoding="utf-8"))
              for u in TYPES if (IN_DIR / f"{u}_final.json").exists()}
    assert finals, "run scripts/recommend_panels.py <unit> 27 first"
    base = next(iter(finals.values()))["base"]
    ballots = load_ballots(base)
    ballots = ballots[~ballots["is_envelopes"] & (ballots["valid"] > 0)]
    for d in finals.values():
        add_other(d, ballots)
    first = next(iter(finals.values()))
    agreements = [list(a) for a in seat_rules(base)["agreements"]]
    data = {
        "base": base, "next": first["next"], "seed": first["seed"],
        "tests": [22, 23, 24, 25, 26],
        "cap_votes": int(round(CAP * first["base_total_votes"])),
        "built": date.today().isoformat(),
        "source": "scripts/recommend_panels.py, scripts/build_panels_site.py",
        "base_lists": first["base_lists"], "base_blocs": first["base_blocs"],
        "default_agreements": agreements,
        "types": {u: {"panels": d["panels"], "summary": summary(u)} for u, d in finals.items()},
    }
    head, body = TEMPLATE.read_text(encoding="utf-8").split("<!--BODY-->")
    body = body.replace("__DATA__", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    page = ('<!doctype html>\n<html lang="he" dir="rtl">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            + head + "</head>\n<body>\n" + body + "</body>\n</html>\n")
    OUT.write_text(page, encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size / 1e6:.2f} MB)")
    if fragment:
        fragment.write_text(head + body, encoding="utf-8")
        print(f"Wrote {fragment}")


if __name__ == "__main__":
    args = sys.argv[1:]
    main(Path(args[1]) if args[:1] == ["--fragment"] else None)
