"""Evaluation metrics: L1 on shares, Knesset seat allocation, bloc aggregation."""

import numpy as np
import pandas as pd

THRESHOLD = 0.0325
TOTAL_SEATS = 120


def l1(a, b) -> float:
    return float(np.abs(np.asarray(a, dtype=float) - np.asarray(b, dtype=float)).sum())


def _dhondt(votes: pd.Series, n_seats: int) -> pd.Series:
    """Highest-averages allocation: the n_seats largest quotients votes / d."""
    if n_seats == 0:
        return pd.Series(0, index=votes.index, dtype=int)
    quotients = votes.to_numpy(dtype=float)[:, None] / np.arange(1, n_seats + 1)[None, :]
    top = np.argpartition(quotients.ravel(), -n_seats)[-n_seats:]
    seats = np.bincount(top // n_seats, minlength=len(votes))
    return pd.Series(seats, index=votes.index, dtype=int)


def bader_ofer(
    votes: pd.Series,
    agreements: list[tuple[str, str]] = (),
    threshold: float = THRESHOLD,
    total: int = TOTAL_SEATS,
    never_pass: tuple[str, ...] = (),
) -> pd.Series:
    """Seat allocation as used for the Knesset (D'Hondt with surplus agreements).

    `votes` maps list letters to vote counts or shares. Lists under the
    threshold get no seats. Each surplus agreement pairs two lists; both must
    pass the threshold for it to apply. Entries in `never_pass` (e.g. an
    aggregated "other") count towards the total but get no seats. Returns
    seats for every input list. Reproduces the official result of every
    election (tests/test_metrics.py).
    """
    passing = votes[(votes / votes.sum() >= threshold) & ~votes.index.isin(never_pass)]
    groups = {p: [p] for p in passing.index}
    for a, b in agreements:
        if a in groups and b in groups:
            groups[a] = groups[a] + groups.pop(b)
    group_votes = pd.Series({g: passing[m].sum() for g, m in groups.items()})
    group_seats = _dhondt(group_votes, total)
    seats = pd.Series(0, index=votes.index, dtype=int)
    for g, members in groups.items():
        if len(members) == 1:
            seats[g] = group_seats[g]
        else:
            seats[members] = _dhondt(passing[members], group_seats[g]).values
    return seats


def soft_seats(shares: np.ndarray, threshold: float = THRESHOLD, sharpness: float = 400.0,
               total: int = TOTAL_SEATS) -> np.ndarray:
    """Differentiable stand-in for seat allocation, for training only.

    A steep sigmoid replaces the threshold and seats are split proportionally
    among passing lists. Surplus agreements and rounding are ignored; the exact
    allocation is used for evaluation.
    """
    shares = np.asarray(shares, dtype=float)
    gate = 1.0 / (1.0 + np.exp(-sharpness * (shares - threshold)))
    passing = shares * gate
    return total * passing / passing.sum()


def to_blocs(values: pd.Series, bloc_of: dict[str, str]) -> pd.Series:
    """Aggregate per-list values (shares or seats) into blocs.

    Lists missing from `bloc_of` are counted as "other".
    """
    blocs = values.index.map(lambda p: bloc_of.get(p, "other"))
    return values.groupby(blocs).sum()
