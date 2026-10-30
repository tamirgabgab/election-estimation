"""Build HTML result reports from data/processed.

Writes:
  reports/knesset_<N>_<year>.html  - final results of one election
  reports/index.html               - all elections: pick one, or compare and average
                                     by party family or by bloc

Each page is self-contained (data inlined, no external scripts). Party families and
blocs come from data/parties/knesset_<N>_parties.csv.

Usage:
  python scripts/build_reports.py
"""

import json
from pathlib import Path

import pandas as pd

from build_data import ELECTIONS, PROCESSED, ROOT

REPORTS = ROOT / "reports"
TEMPLATE = Path(__file__).resolve().parent / "templates" / "report.html"
BLOCS = {"right", "haredi", "center_left", "arab", "other"}


def election_data(knesset: int) -> dict:
    cfg = ELECTIONS[knesset]
    ballots = pd.read_csv(PROCESSED / f"knesset_{knesset}" / "ballots.csv",
                          dtype={"ballot_id": str}, encoding="utf-8-sig")
    national = pd.read_csv(PROCESSED / f"knesset_{knesset}" / "national.csv",
                           dtype={"name_he": str, "name_en": str, "family": str},
                           keep_default_na=False, encoding="utf-8-sig")
    assert set(national["bloc"]) <= BLOCS, f"unknown bloc in Knesset {knesset}"
    assert national["seats"].sum() == cfg["seats"]

    names = dict(zip(national["letter"], national["name_he"]))
    return {
        "knesset": knesset,
        "year": cfg["year"],
        "date": cfg["date"],
        "threshold": cfg["threshold"],
        "source": cfg.get("source", "committee"),
        "seats_total": cfg["seats"],
        "surplus_agreements": [[names[a] or a, names[b] or b] for a, b in cfg["surplus_agreements"]],
        "registered": int(ballots["registered"].sum()),
        "voters": int(ballots["voters"].sum()),
        "invalid": int(ballots["invalid"].sum()),
        "valid": int(ballots["valid"].sum()),
        "regular_boxes": int((~ballots["is_envelopes"]).sum()),
        "envelope_rows": int(ballots["is_envelopes"].sum()),
        "parties": [
            {
                "letter": r.letter,
                "name_he": r.name_he,
                "name_en": r.name_en,
                "family": r.family,
                "bloc": r.bloc,
                "votes": int(r.votes),
                "share": round(float(r.share), 6),
                "passed": bool(r.passed_threshold),
                "seats": int(r.seats),
            }
            for r in national.itertuples()
        ],
    }


def render(title: str, data: dict) -> str:
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = TEMPLATE.read_text(encoding="utf-8")
    return html.replace("__TITLE__", title).replace("/*__DATA__*/null", payload)


def main() -> None:
    REPORTS.mkdir(exist_ok=True)
    elections = [election_data(k) for k in sorted(ELECTIONS)]
    for el in elections:
        path = REPORTS / f"knesset_{el['knesset']}_{el['year']}.html"
        path.write_text(render(f"כנסת {el['knesset']} – תוצאות", {"multi": False, "elections": [el]}),
                        encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")
    index = REPORTS / "index.html"
    index.write_text(render("תוצאות הבחירות לכנסת", {"multi": True, "elections": elections}), encoding="utf-8")
    print(f"wrote {index.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
