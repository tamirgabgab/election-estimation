"""Build cleaned, unified election tables from the raw Central Elections Committee files.

Reads data/raw/*, validates the files, and writes:
  data/processed/knesset_<N>/ballots.csv       - one row per ballot box (counts)
  data/processed/knesset_<N>/settlements.csv   - one row per settlement (counts)
  data/processed/knesset_<N>/national.csv      - national votes, shares and seats per party
  data/processed/knesset_<N>_<year>.xlsx       - Excel workbook with tables and formulas
  data/processed/ballots_long.csv.gz           - all elections, one row per (ballot, party)
  reports/*.html                               - via scripts/build_reports.py

Usage:
  python scripts/build_data.py
"""

import io
import re
from datetime import datetime
from pathlib import Path

import pandas as pd
from xlsxwriter.utility import xl_col_to_name

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PARTIES = ROOT / "data" / "parties"
PROCESSED = ROOT / "data" / "processed"

# Settlement codes of the "outer envelopes" pseudo-settlement (soldiers, diplomats,
# prisoners, hospitals, etc.). It has no geography and no registered voters.
# 9999 from Knesset 22 on, 99999 in Knesset 21.
ENVELOPES_CODES = {9999, 99999}

# surplus_agreements: only agreements between lists that passed the threshold matter.
# Each list is verified to reproduce the official seat allocation; it may omit
# agreements that did not change any seat.
ELECTIONS = {
    21: {
        "year": 2019,
        "date": "2019-04-09",
        "threshold": 0.0325,
        "seats": 120,
        "surplus_agreements": [("מחל", "טב"), ("שס", "ג"), ("אמת", "מרצ")],
    },
    22: {
        "year": 2019,
        "date": "2019-09-17",
        "threshold": 0.0325,
        "seats": 120,
        "surplus_agreements": [("מחל", "טב"), ("פה", "ל"), ("אמת", "מרצ"), ("שס", "ג")],
    },
    23: {
        "year": 2020,
        "date": "2020-03-02",
        "threshold": 0.0325,
        "seats": 120,
        "surplus_agreements": [("מחל", "טב"), ("פה", "אמת"), ("שס", "ג")],
    },
    24: {
        "year": 2021,
        "date": "2021-03-23",
        "threshold": 0.0325,
        "seats": 120,
        "surplus_agreements": [("פה", "ל"), ("אמת", "מרצ"), ("שס", "ג")],
    },
    25: {
        "year": 2022,
        "date": "2022-11-01",
        "threshold": 0.0325,
        "seats": 120,
        "surplus_agreements": [("מחל", "ט"), ("פה", "ל")],
    },
}

COLUMN_NAMES = {
    "סמל ועדה": "committee_code",
    "ברזל": "ballot_uid",
    "שם ישוב": "settlement_name",
    "סמל ישוב": "settlement_code",
    "קלפי": "ballot_id",
    "מספר קלפי": "ballot_id",  # Knesset 21 and earlier
    "ריכוז": "concentration",
    "שופט": "judge",
    "בזב": "registered",
    "מצביעים": "voters",
    "פסולים": "invalid",
    "כשרים": "valid",
}
BASE_ORDER = list(dict.fromkeys(COLUMN_NAMES.values()))
BASE_COLUMNS = set(BASE_ORDER)
# Not published in older files (Knesset 21 and earlier); added as empty columns.
OPTIONAL_SETTLEMENT_COLUMNS = ["committee_code"]
OPTIONAL_BALLOT_COLUMNS = ["committee_code", "ballot_uid", "concentration", "judge"]


def read_raw(path: Path) -> pd.DataFrame:
    # Older committee files are Windows-1255 and end every line with a trailing comma.
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("cp1255")
    # Read everything as text first: ballot ids such as "3.10" must not become floats.
    df = pd.read_csv(io.StringIO(text), dtype=str)
    df = df.loc[:, ~df.columns.str.startswith("Unnamed:")]
    df.columns = df.columns.str.strip()
    df = df.rename(columns=COLUMN_NAMES).apply(lambda col: col.str.strip())
    for col in df.columns:
        if col not in ("settlement_name", "ballot_id"):
            df[col] = df[col].astype(int)
    optional = OPTIONAL_BALLOT_COLUMNS if "ballot_id" in df else OPTIONAL_SETTLEMENT_COLUMNS
    for col in optional:
        if col not in df:
            df[col] = pd.Series(pd.NA, index=df.index, dtype="Int64")
    base = [c for c in BASE_ORDER if c in df]
    return df[base + [c for c in df.columns if c not in BASE_COLUMNS]]


def party_columns(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if c not in BASE_COLUMNS]


def validate(ballots: pd.DataFrame, settlements: pd.DataFrame, parties: list[str]) -> None:
    for name, df in (("ballots", ballots), ("settlements", settlements)):
        assert (df["voters"] == df["invalid"] + df["valid"]).all(), f"{name}: voters != invalid + valid"
        assert (df[parties].sum(axis=1) == df["valid"]).all(), f"{name}: party votes != valid"
    assert not ballots.duplicated(["settlement_code", "ballot_id"]).any(), "duplicate ballot ids"

    counts = ["registered", "voters", "invalid", "valid", *parties]
    from_ballots = ballots.groupby("settlement_code")[counts].sum().sort_index()
    from_settlements = settlements.set_index("settlement_code")[counts].sort_index()
    assert from_ballots.index.equals(from_settlements.index), "settlement codes differ between files"
    assert from_ballots.equals(from_settlements), "ballot totals do not match settlement totals"


def dhondt(votes: dict[str, int], seats: int) -> dict[str, int]:
    alloc = dict.fromkeys(votes, 0)
    for _ in range(seats):
        best = max(alloc, key=lambda k: votes[k] / (alloc[k] + 1))
        alloc[best] += 1
    return alloc


def bader_ofer(votes: pd.Series, threshold: float, seats: int, agreements) -> pd.Series:
    """Israeli seat allocation: threshold, then D'Hondt with surplus-vote agreements."""
    passed = votes[votes / votes.sum() >= threshold]
    units, members = {}, {}
    paired = set()
    for a, b in agreements:
        if a in passed and b in passed:
            units[f"{a}+{b}"] = passed[a] + passed[b]
            members[f"{a}+{b}"] = (a, b)
            paired |= {a, b}
    for p in passed.index:
        if p not in paired:
            units[p] = passed[p]
            members[p] = (p,)

    result = pd.Series(0, index=votes.index)
    for unit, unit_seats in dhondt(units, seats).items():
        split = dhondt({p: passed[p] for p in members[unit]}, unit_seats)
        for p, s in split.items():
            result[p] = s
    return result


def build_national(settlements, parties, names, cfg) -> pd.DataFrame:
    votes = settlements[parties].sum()
    national = pd.DataFrame({"letter": parties, "votes": votes.values})
    national = national.merge(names[["letter", "name_he", "name_en", "family", "bloc"]], on="letter", how="left")
    national["share"] = national["votes"] / national["votes"].sum()
    national["passed_threshold"] = national["share"] >= cfg["threshold"]
    seats = bader_ofer(votes, cfg["threshold"], cfg["seats"], cfg["surplus_agreements"])
    national["seats"] = seats.values
    national = national.sort_values("votes", ascending=False).reset_index(drop=True)
    return national[["letter", "name_he", "name_en", "family", "bloc", "votes", "share", "passed_threshold", "seats"]]


def add_keys(ballots: pd.DataFrame, settlements: pd.DataFrame) -> None:
    ballots.insert(0, "ballot_key", ballots["settlement_code"].astype(str) + "_" + ballots["ballot_id"])
    for df in (ballots, settlements):
        df["is_envelopes"] = df["settlement_code"].isin(ENVELOPES_CODES)
    envelopes = settlements[settlements["is_envelopes"]]
    assert len(envelopes) == 1 and (envelopes["registered"] == 0).all(), "expected one envelopes row"


def to_long(ballots: pd.DataFrame, parties: list[str], knesset: int) -> pd.DataFrame:
    ids = ["ballot_key", "settlement_code", "settlement_name", "ballot_id", "is_envelopes", "registered", "voters", "valid"]
    long = ballots[ids + parties].melt(id_vars=ids, var_name="party", value_name="votes")
    long["share"] = (long["votes"] / long["valid"]).where(long["valid"] > 0, 0.0).round(6)
    long.insert(0, "knesset", knesset)
    return long


def write_excel(path, ballots, settlements, national, names, parties, knesset, cfg) -> None:
    # Row formulas use plain A1 references (not [@column] table references) so the
    # workbook also calculates in LibreOffice and Google Sheets.
    with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
        wb = writer.book
        # Fixed creation date so rebuilding an unchanged election gives an identical file.
        wb.set_properties({"created": datetime.fromisoformat(cfg["date"])})
        count_fmt = wb.add_format({"num_format": "#,##0"})
        pct_fmt = wb.add_format({"num_format": "0.00%"})
        bold = wb.add_format({"bold": True})

        def table_sheet(name, df, formulas, widths=None):
            """Write df as an Excel table named like the sheet, plus formula columns.

            formulas: [(header, template, fmt)], where {column} in the template is
            replaced by that column's cell in the same row, e.g. "={voters}/{registered}".
            """
            ws = wb.add_worksheet(name)
            ws.right_to_left()
            cols = list(df.columns)
            letters = {c: xl_col_to_name(i) for i, c in enumerate(cols)}
            data = df.astype(object).where(df.notna(), None).values.tolist()
            for r, row in enumerate(data, start=2):
                row += [re.sub(r"\{([^}]+)\}", lambda m: f"{letters[m[1]]}{r}", t) for _, t, _ in formulas]
            columns = [{"header": c} for c in cols]
            columns += [{"header": h, "format": fmt} for h, _, fmt in formulas]
            ws.add_table(0, 0, len(df), len(columns) - 1, {
                "name": name,
                "data": data,
                "columns": columns,
                "style": "Table Style Medium 2",
            })
            ws.freeze_panes(1, 0)
            for i, c in enumerate(cols):
                if c in parties or c in ("registered", "voters", "invalid", "valid"):
                    ws.set_column(i, i, 9, count_fmt)
            for col, width in (widths or {}).items():
                ws.set_column(cols.index(col), cols.index(col), width)

        rate_formulas = [
            ("turnout", '=IFERROR({voters}/{registered},"")', pct_fmt),
            ("invalid_rate", '=IFERROR({invalid}/{voters},"")', pct_fmt),
        ]

        # National summary: every number is a formula over the Settlements table,
        # except seats (Bader-Ofer with surplus agreements is computed in Python).
        ws = wb.add_worksheet("National")
        ws.right_to_left()
        summary = [
            ("Knesset", knesset, None),
            ("Election date", cfg["date"], None),
            ("Registered", "=SUM(Settlements[registered])", count_fmt),
            ("Voters", "=SUM(Settlements[voters])", count_fmt),
            ("Invalid", "=SUM(Settlements[invalid])", count_fmt),
            ("Valid", "=SUM(Settlements[valid])", count_fmt),
            ("Turnout", "=B4/B3", pct_fmt),
            ("Threshold", cfg["threshold"], pct_fmt),
            ("Threshold votes", "=ROUNDUP(B6*B8,0)", count_fmt),
        ]
        for r, (label, value, fmt) in enumerate(summary):
            ws.write(r, 0, label, bold)
            ws.write(r, 1, value, fmt)
        ws.set_column(0, 0, 16)
        ws.set_column(1, 1, 16)
        ws.set_column(2, 2, 22)

        top = len(summary) + 1
        data = []
        for r, row in enumerate(national.itertuples(), start=top + 2):
            data.append([row.letter, row.name_he or None, row.name_en or None, row.seats,
                         f"=SUM(Settlements[{row.letter}])", f"=E{r}/$B$6", f"=F{r}>=$B$8"])
        ws.add_table(top, 0, top + len(data) + 1, 6, {
            "name": "National",
            "data": data,
            "columns": [
                {"header": "letter", "total_string": "Total"},
                {"header": "name_he"},
                {"header": "name_en"},
                {"header": "seats"},
                {"header": "votes", "format": count_fmt},
                {"header": "share", "format": pct_fmt},
                {"header": "passed_threshold"},
            ],
            "total_row": True,
            "style": "Table Style Medium 2",
        })
        first, last = top + 2, top + len(data) + 1
        for col, fmt in (("D", None), ("E", count_fmt), ("F", pct_fmt)):
            ws.write_formula(f"{col}{last + 1}", f"=SUM({col}{first}:{col}{last})", fmt)
        ws.freeze_panes(top + 1, 0)

        settlement_cols = ["committee_code", "settlement_code", "settlement_name", "is_envelopes",
                           "registered", "voters", "invalid", "valid", *parties]
        share_formulas = [(f"{p} %", f"=IFERROR({{{p}}}/{{valid}},0)", pct_fmt) for p in parties]
        table_sheet("Settlements", settlements[settlement_cols],
                    rate_formulas + share_formulas, {"settlement_name": 22})

        ballot_cols = ["ballot_key", "ballot_uid", "committee_code", "settlement_code", "settlement_name",
                       "ballot_id", "concentration", "judge", "is_envelopes",
                       "registered", "voters", "invalid", "valid", *parties]
        table_sheet("Ballots", ballots[ballot_cols], rate_formulas, {"settlement_name": 22})

        table_sheet("Parties", names, [], {"name_he": 18, "name_en": 22})


def build_election(knesset: int, cfg: dict) -> pd.DataFrame:
    stem = f"knesset_{knesset}_{cfg['year']}"
    ballots = read_raw(RAW / f"{stem}_ballots.csv")
    settlements = read_raw(RAW / f"{stem}_settlements.csv")
    parties = party_columns(ballots)
    assert parties == party_columns(settlements), "party columns differ between files"
    validate(ballots, settlements, parties)

    names = pd.read_csv(PARTIES / f"knesset_{knesset}_parties.csv", dtype=str, keep_default_na=False)
    missing = set(parties) - set(names["letter"])
    assert not missing, f"parties missing from party table: {missing}"

    add_keys(ballots, settlements)
    national = build_national(settlements, parties, names, cfg)

    out = PROCESSED / f"knesset_{knesset}"
    out.mkdir(parents=True, exist_ok=True)
    ballots.to_csv(out / "ballots.csv", index=False, encoding="utf-8-sig")
    settlements.to_csv(out / "settlements.csv", index=False, encoding="utf-8-sig")
    national.to_csv(out / "national.csv", index=False, encoding="utf-8-sig")
    write_excel(PROCESSED / f"{stem}.xlsx", ballots, settlements, national, names, parties, knesset, cfg)

    winners = national[national["seats"] > 0]
    print(f"Knesset {knesset}: {len(ballots)} ballots, {len(settlements)} settlements, "
          f"{national['votes'].sum():,} valid votes")
    print("  seats: " + ", ".join(f"{r.letter}={r.seats}" for r in winners.itertuples()))
    return to_long(ballots, parties, knesset)


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    long = pd.concat([build_election(k, cfg) for k, cfg in ELECTIONS.items()], ignore_index=True)
    long.to_csv(PROCESSED / "ballots_long.csv.gz", index=False, encoding="utf-8")
    print(f"ballots_long.csv.gz: {len(long):,} rows")

    import build_reports  # imports this module, so import here to avoid a cycle

    build_reports.main()


if __name__ == "__main__":
    main()
