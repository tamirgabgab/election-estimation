"""Loading the processed election tables for modelling.

`scripts/build_data.py` turns the committee's raw files into
`data/processed/knesset_<N>/{ballots,settlements,national}.csv` with English
metadata columns. Every other column holds the valid votes of one list, keyed
by its ballot letters (e.g. "מחל", "פה", "שס"). See data/README.md.
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = ROOT / "data" / "processed"
PARTIES_DIR = ROOT / "data" / "parties"
KNESSETS = list(range(16, 27))
TENFOLD_BALLOT_IDS = {16, 17}
BLOC_SCHEMES = {
    "four_blocs": {},
    "three_blocs": {"haredi": "right"},
}

META_COLUMNS = [
    "ballot_key", "committee_code", "ballot_uid", "settlement_name", "settlement_code",
    "ballot_id", "concentration", "judge", "registered", "voters", "invalid", "valid",
    "is_envelopes", "external", "other_ballot",
    # Added by load_ballots.
    "base_box", "is_split",
]


def party_columns(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if c not in META_COLUMNS]


def load_ballots(knesset: int) -> pd.DataFrame:
    """One row per ballot box, including the double-envelopes rows."""
    df = pd.read_csv(
        PROCESSED_DIR / f"knesset_{knesset}" / "ballots.csv",
        encoding="utf-8-sig",
        dtype={"ballot_id": str, "ballot_key": str},
        low_memory=False,
    )
    df["is_envelopes"] = df["is_envelopes"].astype(str).str.lower() == "true"
    # Large boxes are split alphabetically into sub-boxes 283.1, 283.2, ...
    # The part before the dot identifies the original (base) box. Knesset 16-17
    # number boxes ten times larger, with the split in the last digit
    # (61, 62 = box 6 split in two), so their base number is id // 10.
    if knesset in TENFOLD_BALLOT_IDS:
        number = df["ballot_id"].astype(int)
        base = (number // 10).astype(str)
        df["is_split"] = number % 10 != 0
    else:
        base = df["ballot_id"].str.split(".").str[0]
        df["is_split"] = df["ballot_id"].str.contains(".", regex=False)
    df["base_box"] = df["settlement_code"].astype(str) + "_" + base
    return df


def load_settlements(knesset: int) -> pd.DataFrame:
    return pd.read_csv(PROCESSED_DIR / f"knesset_{knesset}" / "settlements.csv",
                       encoding="utf-8-sig", low_memory=False)


def load_parties(knesset: int) -> pd.DataFrame:
    """Party table: letter, name_he, name_en, family, bloc, verified, leader_he."""
    return pd.read_csv(PARTIES_DIR / f"knesset_{knesset}_parties.csv", dtype=str,
                       keep_default_na=False).set_index("letter")


def bloc_of(knesset: int, scheme: str = "four_blocs") -> dict[str, str]:
    """Ballot letters -> bloc under a bloc scheme (see BLOC_SCHEMES)."""
    merge = BLOC_SCHEMES[scheme]
    blocs = load_parties(knesset)["bloc"].replace("", "other")
    return {letter: merge.get(bloc, bloc) for letter, bloc in blocs.items()}


def bloc_votes(ballots: pd.DataFrame, knesset: int, scheme: str = "four_blocs") -> pd.DataFrame:
    """Vote counts per bloc for every row of `ballots`."""
    parties = party_columns(ballots)
    mapping = bloc_of(knesset, scheme)
    blocs = pd.Index([mapping.get(p, "other") for p in parties])
    return ballots[parties].T.groupby(blocs).sum().T


def base_boxes(knesset: int, scheme: str = "four_blocs") -> pd.DataFrame:
    """Regular boxes merged into base boxes, with totals and bloc vote counts."""
    ballots = load_ballots(knesset)
    regular = ballots[~ballots["is_envelopes"]]
    totals = regular.groupby("base_box").agg(
        settlement_code=("settlement_code", "first"),
        settlement_name=("settlement_name", "first"),
        sub_boxes=("ballot_id", "size"),
        registered=("registered", "sum"),
        valid=("valid", "sum"),
    )
    blocs = bloc_votes(regular, knesset, scheme).groupby(regular["base_box"]).sum()
    return totals.join(blocs)


def validate(ballots: pd.DataFrame) -> dict[str, bool]:
    parties = party_columns(ballots)
    regular = ballots[~ballots["is_envelopes"]]
    return {
        "valid_equals_party_sum": bool((ballots[parties].sum(axis=1) == ballots["valid"]).all()),
        "voters_equal_valid_plus_invalid": bool(
            (ballots["voters"] == ballots["valid"] + ballots["invalid"]).all()
        ),
        "no_turnout_above_100pct": bool((regular["voters"] <= regular["registered"]).all()),
        "unique_ballot_keys": bool(ballots["ballot_key"].is_unique),
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

    regular = ballots[~ballots["is_envelopes"] & (ballots["valid"] > 0)]
    counts = collapse(regular[parties])
    shares = counts.div(counts.sum(axis=1), axis=0)
    target = collapse(ballots[parties].sum().to_frame().T).iloc[0]
    return shares, target / target.sum()
