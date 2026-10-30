"""Rolling held-out evaluation of panel methods.

For every test election t, a method sees only elections before t, returns a
panel (units and weights), and is scored on t. Units are settlements, base
boxes or (later) statistical areas; the unit is a parameter.

Two ways of reading a panel on election night are scored:
  "unit"       - the whole unit is counted;
  "single_box" - one random regular box of each panel unit is counted (M9).
"""

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
import pandas as pd

from election_estimation.data import KNESSETS, bloc_of, load_ballots, party_columns
from election_estimation.elections import seat_rules
from election_estimation.metrics import bader_ofer, to_blocs
from election_estimation.selection import greedy_selection

UNITS = {
    "settlement": lambda b: b["settlement_code"].astype(str),
    "base_box": lambda b: b["base_box"],
}


@dataclass
class Election:
    knesset: int
    parties: list[str]          # every list letter
    boxes: pd.DataFrame         # regular boxes: "unit" + party vote counts
    units: pd.DataFrame         # party vote counts per unit (regular boxes)
    national: pd.Series         # national votes per list, double envelopes included
    seats: pd.Series            # official seats per list
    blocs: dict[str, str]       # list -> bloc

    @property
    def shares(self) -> pd.Series:
        return self.national / self.national.sum()


def load_election(knesset: int, unit: str = "settlement") -> Election:
    ballots = load_ballots(knesset)
    parties = party_columns(ballots)
    regular = ballots[~ballots["is_envelopes"] & (ballots["valid"] > 0)].copy()
    regular["unit"] = UNITS[unit](regular)
    national = ballots[parties].sum()
    return Election(
        knesset=knesset,
        parties=parties,
        boxes=regular[["unit"] + parties].reset_index(drop=True),
        units=regular.groupby("unit")[parties].sum(),
        national=national,
        seats=bader_ofer(national, **seat_rules(knesset)),
        blocs=bloc_of(knesset),
    )


def load_all(unit: str = "settlement") -> dict[int, Election]:
    return {k: load_election(k, unit) for k in KNESSETS}


# --- scoring -----------------------------------------------------------------

def score(pred_votes: pd.Series, e: Election) -> dict[str, float]:
    """Metrics of a predicted vote vector (any scale) against election e."""
    pred = pred_votes.reindex(e.parties, fill_value=0.0)
    pred = pred / pred.sum()
    true = e.shares
    pred_seats = bader_ofer(pred, **seat_rules(e.knesset))
    threshold = seat_rules(e.knesset)["threshold"]
    true_blocs, pred_blocs = to_blocs(true, e.blocs), to_blocs(pred, e.blocs)
    return {
        "share_L1": float((pred - true).abs().sum() * 100),
        "max_list_error": float((pred - true).abs().max() * 100),
        "seat_L1": float((pred_seats - e.seats).abs().sum()),
        "threshold_errors": int(((pred >= threshold) != (true >= threshold)).sum()),
        "bloc_share_L1": float((pred_blocs - true_blocs).abs().sum() * 100),
        "bloc_seat_L1": float((to_blocs(pred_seats, e.blocs)
                               - to_blocs(e.seats, e.blocs)).abs().sum()),
    }


@dataclass
class Panel:
    units: list[str]
    weights: np.ndarray | None  # None = pool the counted votes

    def predict(self, e: Election, reading: str, rng: np.random.Generator) -> pd.Series | None:
        present = [u for u in self.units if u in e.units.index]
        if not present:
            return None
        if reading == "unit":
            counts = e.units.loc[present]
        else:
            boxes = e.boxes[e.boxes["unit"].isin(present)]
            pick = boxes.groupby("unit").sample(n=1, random_state=rng)
            counts = pick.set_index("unit")[e.parties].loc[present]
        if self.weights is None:
            return counts.sum()
        w = pd.Series(self.weights, index=self.units).loc[present]
        shares = counts.div(counts.sum(axis=1), axis=0)
        return (shares.mul(w / w.sum(), axis=0)).sum()


# --- methods -----------------------------------------------------------------
# A method gets the training elections (oldest first) and the panel sizes, and
# returns {k: Panel}. It must not look at the test election.

Method = Callable[[list[Election], list[int], np.random.Generator], dict[int, Panel]]


def recency_weights(train: list[Election], decay: float) -> np.ndarray:
    w = decay ** np.arange(len(train))[::-1]
    return w / w.sum()


def candidate_units(train: list[Election]) -> list[str]:
    """Units present in every training election."""
    common = train[0].units.index
    for e in train[1:]:
        common = common.intersection(e.units.index)
    return sorted(common)


def random_pooled(train, ks, rng) -> dict[int, Panel]:
    """k units drawn uniformly from the last training election; counted votes pooled."""
    pool = list(train[-1].units.index)
    return {k: Panel(list(rng.choice(pool, size=k, replace=False)), None) for k in ks}


def random_pps(train, ks, rng) -> dict[int, Panel]:
    """k units drawn with probability proportional to their valid votes in the last
    training election; the estimate is the plain mean of their shares."""
    sizes = train[-1].units.sum(axis=1)
    p = (sizes / sizes.sum()).values
    return {k: Panel(list(rng.choice(sizes.index, size=k, replace=False, p=p)), np.ones(k))
            for k in ks}


def greedy_weighted(decay: float = 0.7, candidates: int = 40, min_share: float = 0.01) -> Method:
    """Greedy column generation on the stacked training elections.

    Each training election contributes its lists with at least `min_share`
    nationally plus "other", scaled by its recency weight.
    """
    def method(train, ks, rng) -> dict[int, Panel]:
        units = candidate_units(train)
        rho = recency_weights(train, decay)
        X_rows, y_rows = [], []
        for e, r in zip(train, rho):
            major = e.shares[e.shares >= min_share].index
            counts = e.units.loc[units]
            X = pd.concat([counts[major], counts.drop(columns=major).sum(axis=1).rename("other")],
                          axis=1)
            X = X.div(X.sum(axis=1), axis=0)
            y = pd.concat([e.shares[major], pd.Series({"other": e.shares.drop(major).sum()})])
            X_rows.append(X.values.T * r)
            y_rows.append(y.values * r)
        history = greedy_selection(np.vstack(X_rows), np.concatenate(y_rows),
                                   max_boxes=max(ks), candidates=candidates)
        by_k = {h["k"]: h for h in history}
        last = history[-1]
        panels = {}
        for k in ks:
            h = by_k.get(k, last)
            panels[k] = Panel([units[i] for i in h["boxes"]], np.asarray(h["weights"]))
        return panels
    return method


# --- driver ------------------------------------------------------------------

def evaluate(
    elections: dict[int, Election],
    methods: dict[str, Method],
    ks: list[int],
    tests: list[int],
    draws: int = 30,
    seed: int = 0,
) -> pd.DataFrame:
    """Scores of every method, panel size, reading and test election.

    Random panels and single-box readings are averaged over `draws` draws.
    """
    rows = []
    for t in tests:
        train = [elections[k] for k in sorted(elections) if k < t]
        test = elections[t]
        rows.append({"test": t, "method": "all_boxes", "k": len(test.units),
                     "reading": "unit", **score(test.units.sum(), test)})
        for name, method in methods.items():
            rng = np.random.default_rng(seed)
            n_fits = draws if name.startswith("random") else 1
            fits = [method(train, ks, rng) for _ in range(n_fits)]
            for k in ks:
                for reading in ("unit", "single_box"):
                    results = []
                    for panels in fits:
                        reps = 1 if reading == "unit" or n_fits > 1 else draws
                        for _ in range(reps):
                            pred = panels[k].predict(test, reading, rng)
                            if pred is not None:
                                results.append(score(pred, test))
                    mean = pd.DataFrame(results).mean().to_dict()
                    rows.append({"test": t, "method": name, "k": k, "reading": reading, **mean})
    return pd.DataFrame(rows)
