"""Links the Knesset 27 polling station list to the panel areas (data question D17).

Input: the committee's list of K27 ballot boxes as CSV (UTF-8 or Windows-1255)
with at least the settlement code and the ballot number, and if published the
polling center (`ריכוז`) and the eligible voters (`בזב`). Header names accepted:
  settlement: סמל ישוב | ballot: קלפי, מספר קלפי | center: ריכוז | registered: בזב,
  בעלי זכות בחירה.

Steps:
1. every K27 box gets a statistical area through K26: the area of the K26 box
   with the same settlement and number, else the most common area of the K26
   boxes of the same settlement and center, else the settlement (`loc:`);
   -> reports/k27_panels/k27_boxes_linked.csv;
2. scripts/recommend_sector_panels.py then takes the boxes per area from it
   (instead of the K26 counts) and, for every panel area, three K27 boxes to
   count (`pick_boxes`): the same number as the recommended K26 box if it is in
   the area, then the boxes of the same center, then the closest in eligible
   voters.

`--validate` runs step 1 on Knesset 25 as if it were new, linked through
Knesset 24, and reports how often the area is right (K25 has true areas).

Usage:
    PYTHONPATH=src python scripts/match_k27_boxes.py <k27_boxes.csv>
    PYTHONPATH=src python scripts/match_k27_boxes.py --validate
"""

import io
import json
import sys
from pathlib import Path

import pandas as pd

from election_estimation.data import PROCESSED_DIR, load_ballots

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "reports" / "k27_panels"
LINKED = OUT_DIR / "k27_boxes_linked.csv"
HEADERS = {"סמל ישוב": "settlement_code", "קלפי": "ballot_id", "מספר קלפי": "ballot_id",
           "ריכוז": "concentration", "בזב": "registered", "בעלי זכות בחירה": "registered"}


def read_list(path: Path) -> pd.DataFrame:
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("cp1255")
    df = pd.read_csv(io.StringIO(text), dtype=str)
    df.columns = df.columns.str.strip()
    df = df.rename(columns=HEADERS)
    assert {"settlement_code", "ballot_id"} <= set(df.columns), "need settlement code and ballot"
    df = df.apply(lambda c: c.str.strip())
    # Double envelopes (settlement code 9999, 99999 in K21) are not polling stations.
    df = df[df["settlement_code"].notna() & df["ballot_id"].notna()
            & ~df["settlement_code"].isin(["9999", "99999"])]
    return df[[c for c in ["settlement_code", "ballot_id", "concentration", "registered"]
               if c in df.columns]].reset_index(drop=True)


def reference(knesset: int) -> pd.DataFrame:
    """Regular boxes of a past election with their area."""
    b = load_ballots(knesset)
    b = b[~b["is_envelopes"]].copy()
    areas = pd.read_csv(PROCESSED_DIR / "ballot_areas.csv", encoding="utf-8-sig",
                        dtype={"ballot_key": str})
    areas = areas[areas["knesset"] == knesset].set_index("ballot_key")["area_id"]
    b["area_id"] = b["ballot_key"].map(areas)
    for c in ("settlement_code", "concentration"):
        b[c] = b[c].astype(str).str.replace(r"\.0$", "", regex=True)
    return b


def link(new: pd.DataFrame, ref: pd.DataFrame) -> pd.DataFrame:
    """Area and method for every box of `new`, through the boxes of `ref`."""
    ref = ref.dropna(subset=["area_id"])
    by_ballot = ref.drop_duplicates(["settlement_code", "ballot_id"]).set_index(
        ["settlement_code", "ballot_id"])["area_id"]
    key = pd.MultiIndex.from_frame(new[["settlement_code", "ballot_id"]])
    area_ballot = pd.Series(by_ballot.reindex(key).values, index=new.index)
    area_center = pd.Series(index=new.index, dtype=object)
    if "concentration" in new.columns:
        by_center = ref.groupby(["settlement_code", "concentration"])["area_id"].agg(
            lambda s: s.value_counts().index[0])
        ckey = pd.MultiIndex.from_frame(new[["settlement_code", "concentration"]])
        area_center = pd.Series(by_center.reindex(ckey).values, index=new.index)
    area = area_ballot.fillna(area_center).fillna("loc:" + new["settlement_code"])
    method = pd.Series("settlement", index=new.index)
    method[area_center.notna()] = "center"
    method[area_ballot.notna()] = "ballot"
    return new.assign(area_id=area, method=method)


def pick_boxes(linked: pd.DataFrame, ref: pd.DataFrame, panels: list[dict]) -> pd.DataFrame:
    """Three K27 boxes per panel area (see the module docstring): one row per
    (budget, rank, area, order)."""
    reg = ref.set_index(["settlement_code", "ballot_id"])["registered"]
    rows = []
    for p in panels:
        for u in p["units"]:
            r = u["recommended"][0]
            cand = linked[linked["area_id"] == u["id"]].copy()
            if cand.empty:
                rows.append({"budget": p["budget"], "rank": p["rank"], "id": u["id"], "order": 0,
                             "k26_ballot": r["ballot"], "k27_ballot": "", "how": "none"})
                continue
            same = (cand["settlement_code"] == r["settlement_code"]) & (cand["ballot_id"] == r["ballot"])
            center = (cand["concentration"] == r["center"]) if "concentration" in cand else False
            k26_reg = reg.get((r["settlement_code"], r["ballot"]), float("nan"))
            gap = ((pd.to_numeric(cand["registered"], errors="coerce") - k26_reg).abs()
                   if "registered" in cand else pd.Series(0.0, index=cand.index))
            cand = cand.assign(s=~same, c=~center, g=gap.fillna(1e9)).sort_values(["s", "c", "g"])
            for k, b in enumerate(cand.head(3).itertuples()):
                how = "same_number" if not b.s else "same_center" if not b.c else "closest_size"
                rows.append({"budget": p["budget"], "rank": p["rank"], "id": u["id"], "order": k,
                             "k26_ballot": r["ballot"], "settlement_code": b.settlement_code,
                             "k27_ballot": b.ballot_id, "how": how})
    return pd.DataFrame(rows)


def validate() -> None:
    new = reference(25)
    truth = new.set_index(new.index)["area_id"]
    linked = link(new[["settlement_code", "ballot_id", "concentration", "registered"]],
                  reference(24))
    right = linked["area_id"] == truth
    votes = new["valid"]
    print("K25 linked through K24 (true areas known):")
    print(f"  boxes with the right area: {right.mean():.1%}; by votes: "
          f"{votes[right].sum() / votes.sum():.1%}")
    print(linked.assign(right=right).groupby("method")["right"].agg(["size", "mean"]).round(3))
    counts_true = truth.value_counts()
    counts_link = linked["area_id"].value_counts().reindex(counts_true.index, fill_value=0)
    print(f"  areas with the right box count: {(counts_true == counts_link).mean():.1%}")


def main(path: Path) -> None:
    linked = link(read_list(path), reference(26))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    linked.to_csv(LINKED, index=False)
    print(linked["method"].value_counts().to_string())
    print(f"Wrote {LINKED}; now run scripts/recommend_sector_panels.py")


if __name__ == "__main__":
    if sys.argv[1:] == ["--validate"]:
        validate()
    else:
        main(Path(sys.argv[1]))
