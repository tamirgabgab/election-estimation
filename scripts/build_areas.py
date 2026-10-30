"""Builds data/processed/ballot_areas.csv: the statistical area of every regular ballot box.

Inputs:
  data/raw/geography/knesset_<N>_<year>_ballot_areas.csv  - Yoavfried/Israel-Elections-Map
      ballot files (K19-K25), byte-for-byte; `stat_area_id` uses the CBS 2011 areas.
  data/processed/knesset_<N>/ballots.csv                    - built by build_data.py

Output columns: knesset, ballot_key, area_id, method.
  area_id - "stat2011:<code>" for a statistical area, "loc:<settlement_code>" when the
            box has no area (the whole settlement is then one unit).
  method  - how the area was found: "yoavfried" (K19-K25), "k25_center" / "k25_ballot"
            (K26 through the K25 polling center or ballot of the same settlement and
            number), or "settlement" (no area).

Run by build_data.py; can also be run alone after it:
    python scripts/build_areas.py
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "geography"
PROCESSED = ROOT / "data" / "processed"
SOURCE_KNESSETS = range(19, 26)
LINKED_KNESSET = 26  # no area file; linked through Knesset 25
AREA_VINTAGE = "stat2011:"


def read_regular_ballots(knesset: int) -> pd.DataFrame:
    df = pd.read_csv(PROCESSED / f"knesset_{knesset}" / "ballots.csv", encoding="utf-8-sig",
                     dtype={"ballot_id": str, "ballot_key": str}, low_memory=False)
    df = df[df["is_envelopes"].astype(str).str.lower() != "true"].copy()
    df["match_key"] = df["settlement_code"].astype(str) + "_" + df["ballot_id"]
    # Knesset 20 publishes split boxes under one number; both sources keep file order.
    df["match_order"] = df.groupby("match_key").cumcount()
    return df


def source_areas(knesset: int) -> pd.DataFrame:
    """Area of every regular ballot box of a K19-K25 election."""
    path = next(RAW.glob(f"knesset_{knesset}_*_ballot_areas.csv"))
    src = pd.read_csv(path, encoding="utf-8-sig", dtype={"source_kalpi": str}, low_memory=False)
    src = src[src["is_envelope"].astype(str) != "True"].copy()
    src["match_key"] = src["source_locality_code"].astype(int).astype(str) + "_" + src["source_kalpi"]
    src["match_order"] = src.groupby("match_key").cumcount()
    vintages = src["stat_area_id"].dropna().str.split(":").str[0].unique()
    assert set(vintages) <= {AREA_VINTAGE[:-1]}, f"K{knesset}: unexpected area vintages {vintages}"

    ballots = read_regular_ballots(knesset)
    merged = ballots.merge(src[["match_key", "match_order", "stat_area_id", "valid_votes"]],
                           on=["match_key", "match_order"], how="left", validate="one_to_one")
    assert merged["valid_votes"].notna().all(), f"K{knesset}: ballots missing from the area file"
    assert (merged["valid_votes"] == merged["valid"]).mean() > 0.98, f"K{knesset}: votes differ"
    has_area = merged["stat_area_id"].notna()
    return pd.DataFrame({
        "knesset": knesset,
        "ballot_key": merged["ballot_key"],
        "settlement_code": merged["settlement_code"],
        "concentration": merged["concentration"],
        "match_key": merged["match_key"],
        "area_id": merged["stat_area_id"].where(has_area, "loc:" + merged["settlement_code"].astype(str)),
        "method": has_area.map({True: "yoavfried", False: "settlement"}),
    })


def linked_areas(knesset: int, reference: pd.DataFrame) -> pd.DataFrame:
    """Areas for an election without an area file, through the reference election.

    First by polling center (same settlement and `ריכוז` code; the center's most
    common area), then by ballot number in the same settlement, else the settlement.
    """
    ref = reference[reference["method"] == "yoavfried"]
    by_center = (ref.dropna(subset=["concentration"])
                 .groupby(["settlement_code", "concentration"])["area_id"]
                 .agg(lambda s: s.value_counts().index[0]))
    by_ballot = ref.drop_duplicates("match_key").set_index("match_key")["area_id"]

    ballots = read_regular_ballots(knesset)
    center_key = pd.MultiIndex.from_frame(ballots[["settlement_code", "concentration"]])
    area_center = pd.Series(by_center.reindex(center_key).values, index=ballots.index)
    area_ballot = ballots["match_key"].map(by_ballot)
    settlement = "loc:" + ballots["settlement_code"].astype(str)
    area = area_center.fillna(area_ballot).fillna(settlement)
    method = pd.Series("settlement", index=ballots.index)
    method[area_ballot.notna()] = "k25_ballot"
    method[area_center.notna()] = "k25_center"
    return pd.DataFrame({"knesset": knesset, "ballot_key": ballots["ballot_key"],
                         "area_id": area, "method": method})


def main() -> None:
    parts = {k: source_areas(k) for k in SOURCE_KNESSETS}
    parts[LINKED_KNESSET] = linked_areas(LINKED_KNESSET, parts[max(SOURCE_KNESSETS)])
    out = pd.concat([p[["knesset", "ballot_key", "area_id", "method"]] for p in parts.values()])
    assert not out.duplicated(["knesset", "ballot_key"]).any()
    out.to_csv(PROCESSED / "ballot_areas.csv", index=False, encoding="utf-8-sig")
    summary = out.groupby(["knesset", "method"]).size().unstack(fill_value=0)
    summary["areas"] = out.groupby("knesset")["area_id"].nunique()
    print("ballot_areas.csv:", len(out), "rows")
    print(summary.to_string())


if __name__ == "__main__":
    main()
