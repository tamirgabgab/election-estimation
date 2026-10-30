"""The modelling seat allocation must reproduce the official seats of every election."""

import pandas as pd
import pytest

from election_estimation.data import KNESSETS, PROCESSED_DIR, load_ballots, party_columns
from election_estimation.elections import seat_rules
from election_estimation.metrics import bader_ofer, soft_seats, to_blocs


def official_seats(knesset: int) -> pd.Series:
    national = pd.read_csv(PROCESSED_DIR / f"knesset_{knesset}" / "national.csv",
                           encoding="utf-8-sig")
    return national.set_index("letter")["seats"]


@pytest.mark.parametrize("knesset", KNESSETS)
def test_bader_ofer_reproduces_official_seats(knesset: int) -> None:
    ballots = load_ballots(knesset)
    votes = ballots[party_columns(ballots)].sum()
    seats = bader_ofer(votes, **seat_rules(knesset))
    expected = official_seats(knesset).reindex(seats.index, fill_value=0)
    assert seats.sum() == 120
    assert (seats == expected).all(), seats[seats != expected]


def test_soft_seats_sum_to_total() -> None:
    shares = pd.Series([0.3, 0.25, 0.2, 0.1, 0.1, 0.03, 0.02])
    assert abs(soft_seats(shares.values).sum() - 120) < 1e-9


def test_to_blocs_puts_unknown_lists_in_other() -> None:
    values = pd.Series({"a": 1.0, "b": 2.0, "c": 3.0})
    blocs = to_blocs(values, {"a": "right", "b": "right"})
    assert blocs.to_dict() == {"other": 3.0, "right": 3.0}
