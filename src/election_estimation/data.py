"""Loading and normalizing Central Elections Committee result files.

The CEC publishes two CSV files per Knesset election:
  expb.csv - one row per ballot box (קלפי)
  expc.csv - one row per locality (יישוב); an exact aggregation of expb.csv

Every column that is not a metadata column holds the vote count of one party
list, keyed by its ballot letters (e.g. "מחל", "פה", "שס").
"""

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"

# Locality code the CEC uses for double envelopes (soldiers, prisoners,
# hospitals, diplomats). These votes belong to no geographic place.
DOUBLE_ENVELOPES_CODE = 9999

COLUMN_NAMES = {
    "סמל ועדה": "committee_id",
    "ברזל": "iron_id",
    "שם ישוב": "locality_name",
    "סמל ישוב": "locality_id",
    "קלפי": "box",
    "ריכוז": "center_id",
    "שופט": "judge",
    "בזב": "eligible",
    "מצביעים": "voters",
    "פסולים": "invalid",
    "כשרים": "valid",
    "חיצוניות": "external",
    "קלפי אחרת": "other_box",
}
DERIVED_COLUMNS = ["is_double_envelope", "base_box", "is_split"]
META_COLUMNS = list(COLUMN_NAMES.values()) + DERIVED_COLUMNS


def _read(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8-sig")
    # Trailing commas in the CEC files produce an empty "Unnamed" column.
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
    return df.rename(columns=COLUMN_NAMES)


def party_columns(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if c not in META_COLUMNS]


def load_ballots(knesset: int) -> pd.DataFrame:
    """Ballot-box results with English metadata columns and party columns."""
    df = _read(DATA_DIR / f"knesset_{knesset}" / "expb.csv")
    df["is_double_envelope"] = df["locality_id"] == DOUBLE_ENVELOPES_CODE
    # Large boxes are split alphabetically into sub-boxes 283.1, 283.2, ...
    # The integer part identifies the original box.
    df["base_box"] = df["box"].astype(float).astype(int)
    df["is_split"] = df["box"].astype(float) != df["base_box"]
    return df


def load_localities(knesset: int) -> pd.DataFrame:
    return _read(DATA_DIR / f"knesset_{knesset}" / "expc.csv")


def validate(ballots: pd.DataFrame, localities: pd.DataFrame) -> dict[str, bool]:
    parties = party_columns(ballots)
    by_locality = ballots.groupby("locality_id")[parties].sum().sort_index()
    loc = localities.set_index("locality_id")[parties].sort_index()
    regular = ballots[~ballots["is_double_envelope"]]
    return {
        "valid_equals_party_sum": bool((ballots[parties].sum(axis=1) == ballots["valid"]).all()),
        "voters_equal_valid_plus_invalid": bool(
            (ballots["voters"] == ballots["valid"] + ballots["invalid"]).all()
        ),
        "no_turnout_above_100pct": bool((regular["voters"] <= regular["eligible"]).all()),
        "localities_file_is_ballot_aggregate": bool(
            by_locality.index.equals(loc.index) and (by_locality.values == loc.values).all()
        ),
    }


def share_matrix(
    ballots: pd.DataFrame, parties: list[str], min_national_share: float = 0.01
) -> tuple[pd.DataFrame, pd.Series]:
    """Per-box vote shares and the national share vector.

    Parties below `min_national_share` nationally are merged into "other".
    The national vector includes double envelopes; box rows do not.
    """
    national = ballots[parties].sum()
    national = national / national.sum()
    major = national[national >= min_national_share].sort_values(ascending=False).index.tolist()
    minor = [p for p in parties if p not in major]

    def collapse(votes: pd.DataFrame) -> pd.DataFrame:
        out = votes[major].copy()
        out["other"] = votes[minor].sum(axis=1)
        return out

    regular = ballots[~ballots["is_double_envelope"] & (ballots["valid"] > 0)]
    counts = collapse(regular[parties])
    shares = counts.div(counts.sum(axis=1), axis=0)
    target = collapse(ballots[parties].sum().to_frame().T).iloc[0]
    return shares, target / target.sum()
