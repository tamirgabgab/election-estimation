"""Builds reports/knesset_27_panels.html: the recommended Knesset 27 panels.

Reads reports/k27_panels/sector_final.json (from recommend_sector_panels.py)
and the template scripts/templates/panels.html. The page holds the panel
comparison with the held-out results, the chosen panel's sectors and areas, and
an election-night calculator that mirrors `sector.predict` in JavaScript (with
the within-sector bootstrap, the medoid seats and 90% intervals). Lists under
1% in the base election are merged into one "other" list that never passes.

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

from election_estimation.elections import seat_rules

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "reports" / "k27_panels" / "sector_final.json"
TEMPLATE = ROOT / "scripts" / "templates" / "panels.html"
OUT = ROOT / "reports" / "knesset_27_panels.html"
CAP = 0.02


def main(fragment: Path | None) -> None:
    assert DATA.exists(), "run scripts/recommend_sector_panels.py first"
    d = json.loads(DATA.read_text(encoding="utf-8"))
    data = {
        **d,
        "tests": [22, 23, 24, 25, 26],
        "cap_votes": int(round(CAP * d["base_total_votes"])),
        "built": date.today().isoformat(),
        "source": "scripts/recommend_sector_panels.py, scripts/build_panels_site.py",
        "default_agreements": [list(a) for a in seat_rules(d["base"])["agreements"]],
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
