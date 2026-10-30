"""Print a Markdown table of key facts per election, for HANDOFF.md.

Usage:
  python scripts/summarize_elections.py
"""

import pandas as pd

from build_data import BASE_COLUMNS, ELECTIONS, PROCESSED


def facts(knesset: int) -> dict:
    ballots = pd.read_csv(PROCESSED / f"knesset_{knesset}" / "ballots.csv",
                          dtype={"ballot_id": str}, encoding="utf-8-sig")
    national = pd.read_csv(PROCESSED / f"knesset_{knesset}" / "national.csv", encoding="utf-8-sig")
    parties = [c for c in ballots.columns if c not in BASE_COLUMNS | {"ballot_key", "is_envelopes"}]
    regular = ballots[~ballots["is_envelopes"]]
    envelopes = ballots[ballots["is_envelopes"]]

    national_share = ballots[parties].sum() / ballots["valid"].sum()
    regular_share = regular[parties].sum() / regular["valid"].sum()
    return {
        "Knesset": knesset,
        "Date": ELECTIONS[knesset]["date"],
        "Registered": f"{ballots['registered'].sum():,}",
        "Turnout": f"{ballots['voters'].sum() / ballots['registered'].sum():.2%}",
        "Valid": f"{ballots['valid'].sum():,}",
        "Regular boxes": f"{len(regular):,}",
        "Envelope rows": f"{len(envelopes):,}",
        "Envelope votes": f"{envelopes['valid'].sum():,} ({envelopes['valid'].sum() / ballots['valid'].sum():.2%})",
        # "283.1" style ids, or repeated ids keyed "283-1" (Knesset 20).
        "Split box ids": f"{(ballots['ballot_id'].str.contains('.', regex=False) | ballots['ballot_key'].str.contains('-', regex=False)).sum():,}",
        "Lists / passed": f"{len(parties)} / {national['passed_threshold'].sum()}",
        "Regular vs national L1 (pp)": f"{(regular_share - national_share).abs().sum() * 100:.2f}",
    }


def main() -> None:
    rows = [facts(k) for k in sorted(ELECTIONS)]
    print("| " + " | ".join(rows[0]) + " |")
    print("|" + "---|" * len(rows[0]))
    for row in rows:
        print("| " + " | ".join(str(v) for v in row.values()) + " |")


if __name__ == "__main__":
    main()
