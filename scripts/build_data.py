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
OFFICIAL = ROOT / "data" / "official"

# The "outer envelopes" pseudo-settlement (soldiers, diplomats, prisoners, hospitals,
# etc.). It has no geography and no registered voters. Older files use other codes
# (see envelopes_codes below); they are normalized to this code and name.
ENVELOPES_CODE = 9999
ENVELOPES_NAME = "מעטפות חיצוניות"

# surplus_agreements: only agreements between lists that passed the threshold matter.
# Each list is verified to reproduce the official seat allocation; it may omit
# agreements that did not change any seat.
# envelopes_codes: raw settlement code of the envelopes row in each file, when not 9999;
#   None means the file has no envelopes row (it is then summed from the ballots file).
# unsuffixed_split_boxes: split ballot boxes share one ballot number (no ".1", ".2").
# source "yoavfried": one ballots file from the Yoavfried/Israel-Elections-Map project
#   (no settlements file; settlements are summed from the ballots).
# source "regular_boxes_only": a committee-layout ballots file without envelope votes; an
#   envelopes row is added from data/official/knesset_<N>_totals.csv.
ELECTIONS = {
    16: {
        "year": 2003,
        "date": "2003-01-28",
        "threshold": 0.015,
        "seats": 120,
        # The six published agreements; Shinui + Greens had no effect (Greens failed).
        "surplus_agreements": [("אמת", "מרצ"), ("יש", "רק"), ("ל", "כן"), ("ב", "ם"), ("שס", "ג"), ("ו", "ד")],
        # harelc/elections-vote-transfer ballot16.csv: regular boxes only.
        "source": "regular_boxes_only",
    },
    17: {
        "year": 2006,
        "date": "2006-03-28",
        "threshold": 0.02,
        "seats": 120,
        "surplus_agreements": [("אמת", "מרצ"), ("שס", "ג"), ("מחל", "טב")],
        "source": "yoavfried",
    },
    18: {
        "year": 2009,
        "date": "2009-02-10",
        "threshold": 0.02,
        "seats": 120,
        "surplus_agreements": [("מחל", "ט"), ("אמת", "מרצ"), ("שס", "ג")],
        "source": "yoavfried",
    },
    19: {
        "year": 2013,
        "date": "2013-01-22",
        "threshold": 0.02,
        "seats": 120,
        "surplus_agreements": [("מחל", "טב"), ("אמת", "מרץ"), ("שס", "ג")],
        # The settlements file leaves out the envelope votes (code 875 in the ballots file).
        "envelopes_codes": {"ballots": 875, "settlements": None},
    },
    20: {
        "year": 2015,
        "date": "2015-03-17",
        "threshold": 0.0325,
        "seats": 120,
        # Kulanu needs an agreement to get its official 10 seats, but its partner is not
        # known: Shas, UTJ, Yisrael Beiteinu, Meretz, Yesh Atid or Zionist Union all give
        # the official result. Yisrael Beiteinu is a placeholder (HANDOFF question D7).
        "surplus_agreements": [("מחל", "טב"), ("אמת", "מרצ"), ("כ", "ל")],
        "envelopes_codes": {"ballots": 875, "settlements": 0},
        "unsuffixed_split_boxes": True,
    },
    21: {
        "year": 2019,
        "date": "2019-04-09",
        "threshold": 0.0325,
        "seats": 120,
        "surplus_agreements": [("מחל", "טב"), ("שס", "ג"), ("אמת", "מרצ")],
        "envelopes_codes": {"ballots": 99999, "settlements": 99999},
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
    # Knesset 16 ends with a DOS end-of-file marker (\x1a) parsed as an empty row.
    eof = df["settlement_code"] == "\x1a"
    assert eof.sum() <= 1 and (df.loc[eof].drop(columns=["settlement_name", "settlement_code", "ballot_id"],
                                                 errors="ignore").fillna("0") == "0").all().all()
    df = df[~eof]
    for col in df.columns:
        if col not in ("settlement_name", "ballot_id"):
            # A list with no votes is written as "0.0" in Knesset 16.
            df[col] = df[col].str.replace(r"^(\d+)\.0$", r"\1", regex=True).astype(int)
    optional = OPTIONAL_BALLOT_COLUMNS if "ballot_id" in df else OPTIONAL_SETTLEMENT_COLUMNS
    for col in optional:
        if col not in df:
            df[col] = pd.Series(pd.NA, index=df.index, dtype="Int64")
    base = [c for c in BASE_ORDER if c in df]
    return df[base + [c for c in df.columns if c not in BASE_COLUMNS]]


def party_columns(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if c not in BASE_COLUMNS]


YOAVFRIED_COLUMNS = {
    "source_locality_code": "settlement_code",
    "source_locality_name": "settlement_name",
    "source_kalpi": "ballot_id",
    "eligible_voters": "registered",
    "actual_voters": "voters",
    "invalid_votes": "invalid",
    "valid_votes": "valid",
}


def read_yoavfried(path: Path) -> pd.DataFrame:
    """Read a ballots file of the Yoavfried/Israel-Elections-Map project (Knesset 17-18).

    Party letter columns sit between `is_envelope` and the geography columns. Envelope
    rows are marked by `is_envelope` (their locality code is blank or 0); they get code
    9999 and 0 registered voters, as in the committee's own files.
    """
    df = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    cols = list(df.columns)
    parties = cols[cols.index("is_envelope") + 1:cols.index("geography_assignment_status")]
    envelopes = df["is_envelope"] == "True"
    assert envelopes.any() and df["is_envelope"].isin(["True", "False"]).all()
    df = df.rename(columns=YOAVFRIED_COLUMNS)[list(YOAVFRIED_COLUMNS.values()) + parties]
    df.loc[envelopes, ["settlement_code", "settlement_name", "registered"]] = \
        [str(ENVELOPES_CODE), ENVELOPES_NAME, "0"]
    df = df.apply(lambda col: col.str.strip())
    for col in df.columns:
        if col not in ("settlement_name", "ballot_id"):
            df[col] = df[col].astype(int)
    for col in OPTIONAL_BALLOT_COLUMNS:
        df[col] = pd.Series(pd.NA, index=df.index, dtype="Int64")
    return df[[c for c in BASE_ORDER if c in df] + parties]


def add_envelopes_from_official(ballots: pd.DataFrame, path: Path) -> tuple[pd.DataFrame, list[str]]:
    """Append an envelopes row = official national totals minus the regular boxes.

    For sources that publish regular boxes only. `path` lists official voters, invalid
    and valid votes and the votes of each list it knows. The envelope votes of lists
    missing from it are the remainder, split in proportion to their regular votes
    (largest remainder); those letters are returned so they can be reported.
    """
    official = pd.read_csv(path, dtype={"key": str, "count": int}).set_index("key")["count"]
    parties = party_columns(ballots)
    regular = ballots[["voters", "invalid", "valid", *parties]].sum()
    row = {c: int(official[c] - regular[c]) for c in ("voters", "invalid", "valid")}
    assert row["voters"] == row["invalid"] + row["valid"] and min(row.values()) >= 0
    known = [p for p in parties if p in official.index]
    assert set(official.index) - {"voters", "invalid", "valid"} <= set(parties), "unknown letters"
    for p in known:
        row[p] = int(official[p] - regular[p])
        assert row[p] >= 0, f"official votes of {p} below its regular boxes"
    estimated = [p for p in parties if p not in known]
    rest = row["valid"] - sum(row[p] for p in known)
    assert rest >= 0
    weights = regular[estimated] / regular[estimated].sum() * rest
    shares = weights.astype(int)
    shares[(weights - shares).sort_values(ascending=False).index[:rest - shares.sum()]] += 1
    row.update({p: int(shares[p]) for p in estimated})
    row.update(settlement_code=ENVELOPES_CODE, settlement_name=ENVELOPES_NAME, ballot_id="1", registered=0)
    added = pd.DataFrame([row]).reindex(columns=ballots.columns).astype(ballots.dtypes.to_dict())
    return pd.concat([ballots, added], ignore_index=True), estimated


def settlements_from_ballots(ballots: pd.DataFrame) -> pd.DataFrame:
    """Sum ballot rows per settlement, for sources without a settlements file."""
    counts = ["registered", "voters", "invalid", "valid", *party_columns(ballots)]
    grouped = ballots.groupby("settlement_code", sort=False)
    settlements = grouped[counts].sum().reset_index()
    settlements.insert(0, "settlement_name", grouped["settlement_name"].first().values)
    settlements.insert(0, "committee_code", pd.Series(pd.NA, index=settlements.index, dtype="Int64"))
    return settlements


def normalize_envelopes(ballots: pd.DataFrame, settlements: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Give the envelopes rows code 9999 in both files; returns the settlements table."""
    codes = cfg.get("envelopes_codes", {"ballots": ENVELOPES_CODE, "settlements": ENVELOPES_CODE})
    for df, code in ((ballots, codes["ballots"]), (settlements, codes["settlements"])):
        if code is None:
            continue
        rows = df["settlement_code"] == code
        assert rows.any(), f"no envelopes rows with code {code}"
        df.loc[rows, "settlement_code"] = ENVELOPES_CODE
        df.loc[rows, "settlement_name"] = ENVELOPES_NAME
    if codes["settlements"] is None:
        assert not (settlements["settlement_code"] == ENVELOPES_CODE).any()
        envelopes = ballots[ballots["settlement_code"] == ENVELOPES_CODE]
        assert len(envelopes), "no envelopes rows in the ballots file"
        row = envelopes[[c for c in settlements.columns if c not in ("settlement_name", "settlement_code",
                                                                       "committee_code")]].sum()
        row["settlement_name"], row["settlement_code"] = ENVELOPES_NAME, ENVELOPES_CODE
        settlements["committee_code"] = settlements["committee_code"].astype("Int64")  # NA for the new row
        added = pd.DataFrame([row]).reindex(columns=settlements.columns).astype(settlements.dtypes.to_dict())
        settlements = pd.concat([settlements, added], ignore_index=True)
    return settlements


def validate(ballots: pd.DataFrame, settlements: pd.DataFrame, parties: list[str], cfg: dict) -> None:
    for name, df in (("ballots", ballots), ("settlements", settlements)):
        assert (df["voters"] == df["invalid"] + df["valid"]).all(), f"{name}: voters != invalid + valid"
        assert (df[parties].sum(axis=1) == df["valid"]).all(), f"{name}: party votes != valid"
    if not cfg.get("unsuffixed_split_boxes"):
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
    key = ballots["settlement_code"].astype(str) + "_" + ballots["ballot_id"]
    # Split boxes published under one number get "-1", "-2", ... in file order.
    repeated = key.duplicated(keep=False)
    key[repeated] += "-" + (key[repeated].groupby(key[repeated]).cumcount() + 1).astype(str)
    assert key.is_unique
    ballots.insert(0, "ballot_key", key)
    for df in (ballots, settlements):
        df["is_envelopes"] = df["settlement_code"] == ENVELOPES_CODE
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
    if cfg.get("source") == "yoavfried":
        ballots = read_yoavfried(RAW / f"{stem}_ballots.csv")
        settlements = settlements_from_ballots(ballots)
    elif cfg.get("source") == "regular_boxes_only":
        ballots, estimated = add_envelopes_from_official(read_raw(RAW / f"{stem}_ballots.csv"),
                                                         OFFICIAL / f"knesset_{knesset}_totals.csv")
        print(f"  envelope votes estimated for {len(estimated)} small lists: {' '.join(estimated)}")
        settlements = settlements_from_ballots(ballots)
    else:
        ballots = read_raw(RAW / f"{stem}_ballots.csv")
        settlements = read_raw(RAW / f"{stem}_settlements.csv")
    parties = party_columns(ballots)
    assert parties == party_columns(settlements), "party columns differ between files"
    settlements = normalize_envelopes(ballots, settlements, cfg)
    validate(ballots, settlements, parties, cfg)

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
