"""Rolling held-out evaluation of panel methods.

For every test election t, a method sees only elections before t, returns a
panel (units and weights), and is scored on t. Units are settlements, base
boxes or (later) statistical areas; the unit is a parameter.

Two ways of reading a panel on election night are scored:
  "unit"       - the whole unit is counted;
  "single_box" - one random regular box of each panel unit is counted (M9).
Every result records `boxes`, the number of ballot boxes actually counted, so
methods are compared at the same counting budget.
"""

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
import pandas as pd

from election_estimation.data import KNESSETS, PROCESSED_DIR, bloc_of, load_ballots, party_columns
from election_estimation.elections import seat_rules
from election_estimation.metrics import bader_ofer, to_blocs
from election_estimation.selection import exact_selection, greedy_selection

def _areas(ballots: pd.DataFrame, knesset: int) -> pd.Series:
    areas = pd.read_csv(PROCESSED_DIR / "ballot_areas.csv", encoding="utf-8-sig",
                        dtype={"ballot_key": str})
    areas = areas[areas["knesset"] == knesset].set_index("ballot_key")["area_id"]
    unit = ballots["ballot_key"].map(areas)
    assert unit.notna().all(), f"K{knesset}: ballots without an area"
    return unit


UNITS = {
    "settlement": lambda b, k: b["settlement_code"].astype(str),
    "base_box": lambda b, k: b["base_box"],
    "area": _areas,  # CBS 2011 statistical area, else the settlement (scripts/build_areas.py)
}
UNIT_KNESSETS = {"area": list(range(19, 27))}


@dataclass
class Election:
    knesset: int
    parties: list[str]          # every list letter
    boxes: pd.DataFrame         # regular boxes: "unit" + party vote counts
    units: pd.DataFrame         # party vote counts per unit (regular boxes)
    unit_boxes: pd.Series       # number of regular boxes per unit
    national: pd.Series         # target votes per list (see `load_election`)
    seats: pd.Series            # seats per list computed from `national`
    blocs: dict[str, str]       # list -> bloc

    @property
    def shares(self) -> pd.Series:
        return self.national / self.national.sum()


def load_election(knesset: int, unit: str = "settlement", target: str = "official") -> Election:
    """One election split into sampling units.

    `target` sets what the panel must predict: "official" - the national result,
    double envelopes included (the official seats); "regular" - the total of the
    regular boxes only, the most a box sample can recover.
    """
    assert target in ("official", "regular")
    ballots = load_ballots(knesset)
    parties = party_columns(ballots)
    regular = ballots[~ballots["is_envelopes"] & (ballots["valid"] > 0)].copy()
    regular["unit"] = UNITS[unit](regular, knesset)
    national = (ballots if target == "official" else regular)[parties].sum()
    return Election(
        knesset=knesset,
        parties=parties,
        boxes=regular[["unit"] + parties].reset_index(drop=True),
        units=regular.groupby("unit")[parties].sum(),
        unit_boxes=regular.groupby("unit").size(),
        national=national,
        seats=bader_ofer(national, **seat_rules(knesset)),
        blocs=bloc_of(knesset),
    )


def load_all(unit: str = "settlement", target: str = "official") -> dict[int, Election]:
    return {k: load_election(k, unit, target) for k in UNIT_KNESSETS.get(unit, KNESSETS)}


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
        "seats_moved": float((pred_seats - e.seats).abs().sum() / 2),
        "threshold_errors": int(((pred >= threshold) != (true >= threshold)).sum()),
        "bloc_share_L1": float((pred_blocs - true_blocs).abs().sum() * 100),
        "bloc_seat_L1": float((to_blocs(pred_seats, e.blocs)
                               - to_blocs(e.seats, e.blocs)).abs().sum()),
    }


@dataclass
class Panel:
    units: list[str]
    weights: np.ndarray | None  # None = pool the counted votes
    info: dict | None = None    # e.g. hyperparameters chosen by inner validation

    def boxes(self, e: Election, reading: str) -> int:
        """Ballot boxes counted in election e."""
        present = [u for u in self.units if u in e.units.index]
        return len(present) if reading == "single_box" else int(e.unit_boxes.loc[present].sum())

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


def unit_costs(train: list[Election], units: list[str], lookback: int = 2) -> np.ndarray:
    """Expected boxes of each unit: the most it had in the last `lookback` training
    elections (units grow and are renumbered, so the last election alone underestimates)."""
    counts = pd.concat([e.unit_boxes.reindex(units) for e in train[-lookback:]], axis=1)
    return counts.max(axis=1).fillna(1).values


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


def strata(e: Election) -> pd.Series:
    """Stratum of every unit of e: dominant bloc, and whether it has >= 60% of the votes."""
    blocs = e.units.T.groupby(pd.Index([e.blocs.get(c, "other") for c in e.units.columns])).sum().T
    shares = blocs.div(blocs.sum(axis=1), axis=0)
    return shares.idxmax(axis=1) + np.where(shares.max(axis=1) >= 0.6, "_pure", "_mixed")


def stacked(
    train: list[Election],
    units: list[str],
    decay: float,
    min_share: float = 0.01,
    calibration: float = 0.0,
    noise: float = 0.0,
    replicates: int = 4,
    rng: np.random.Generator | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Stacked target rows for the panel weights: X w should match y.

    Each training election contributes, scaled by its recency weight:
    - its national shares (lists with at least `min_share` plus "other");
    - with `calibration` > 0, the same rows within every stratum of the last
      training election (bloc profile): sum over the stratum's units of
      w_i x_i should equal the stratum's vote share times its list shares,
      plus a row for the stratum's total weight; these rows are scaled by
      `calibration`;
    - with `noise` > 0, `replicates` perturbed copies of the national rows:
      every unit's list shares are multiplied by exp(N(0, noise)) and
      renormalized, and the target is recomputed from the perturbed units, so
      weights cannot lean on exact values of single units.
    """
    rho = recency_weights(train, decay)
    groups = strata(train[-1]).reindex(units)
    X_rows, y_rows = [], []
    for e, r in zip(train, rho):
        major = e.shares[e.shares >= min_share].index
        counts = e.units.loc[units]
        C = pd.concat([counts[major], counts.drop(columns=major).sum(axis=1).rename("other")],
                      axis=1)
        X = C.div(C.sum(axis=1), axis=0)
        y = pd.concat([e.shares[major], pd.Series({"other": e.shares.drop(major).sum()})])
        X_rows.append(X.values.T * r)
        y_rows.append(y.values * r)
        if calibration > 0:
            all_counts = e.units
            all_groups = groups.reindex(all_counts.index)
            total = all_counts.values.sum()
            for g in groups.dropna().unique():
                inside = (groups == g).values
                g_counts = all_counts[all_groups == g]
                g_share = g_counts.values.sum() / total
                g_list = pd.concat([g_counts[major].sum(),
                                    pd.Series({"other": g_counts.drop(columns=major).values.sum()})])
                g_list = g_list / g_list.sum()
                Xg = X.values.T * inside[None, :]
                X_rows.append(np.vstack([Xg, inside[None, :].astype(float)]) * r * calibration)
                y_rows.append(np.concatenate([g_list.values * g_share, [g_share]]) * r * calibration)
        if noise > 0:
            size = C.sum(axis=1).values
            for _ in range(replicates):
                Xn = X.values * np.exp(rng.normal(0.0, noise, size=X.shape))
                Xn = Xn / Xn.sum(axis=1, keepdims=True)
                yn = (Xn * size[:, None]).sum(axis=0) / size.sum()
                yn = yn + (y.values - (X.values * size[:, None]).sum(axis=0) / size.sum())
                X_rows.append(Xn.T * r / replicates)
                y_rows.append(yn * r / replicates)
    return np.vstack(X_rows), np.concatenate(y_rows)


def greedy_weighted(decay: float = 0.7, candidates: int = 40) -> Method:
    """Greedy column generation; k = number of panel units."""
    def method(train, ks, rng) -> dict[int, Panel]:
        units = candidate_units(train)
        X, y = stacked(train, units, decay)
        history = greedy_selection(X, y, max_boxes=max(ks), candidates=candidates)
        by_k = {h["k"]: h for h in history}
        return {k: _panel(units, by_k.get(k, history[-1])) for k in ks}
    return method


def _budget_panels(X, y, units, costs, ks, candidates, nested, **kwargs) -> dict[int, Panel]:
    """Greedy panels for every budget in ks. With `nested`, one run at the largest
    budget; the panel for k is the last step whose cost fits in k (a prefix, so
    smaller panels are subsets of larger ones)."""
    if not nested:
        return {k: _panel(units, greedy_selection(X, y, max_boxes=k, candidates=candidates,
                                                  costs=costs, budget=k, **kwargs)[-1])
                for k in ks}
    history = greedy_selection(X, y, max_boxes=max(ks), candidates=candidates, costs=costs,
                               budget=max(ks), **kwargs)
    return {k: _panel(units, [h for h in history if h["cost"] <= k][-1]) for k in ks}


def greedy_budget(decay: float = 0.7, candidates: int = 40, nested: bool = False) -> Method:
    """Greedy column generation under a box budget; k = boxes to count.

    A unit costs its expected boxes (`unit_costs`), and is counted whole on
    election night (reading "unit").
    """
    def method(train, ks, rng) -> dict[int, Panel]:
        units = candidate_units(train)
        costs = unit_costs(train, units)
        X, y = stacked(train, units, decay)
        return _budget_panels(X, y, units, costs, ks, candidates, nested)
    method.readings = ("unit",)
    return method


def milp_budget(decay: float = 0.7, pool: int = 400, time_limit: float = 60.0,
                ks: tuple[int, ...] = (50, 70)) -> Method:
    """MILP under a box budget on a candidate pool; k = boxes to count.

    The pool holds the units of the greedy budget solution plus the
    affordable units closest to the stacked target. HiGHS stops after
    `time_limit` seconds with the best solution found; as scipy's HiGHS
    interface takes no starting solution, the greedy solution is kept when
    the MILP's training loss is not lower.
    """
    def method(train, ks, rng) -> dict[int, Panel]:
        units = candidate_units(train)
        costs = unit_costs(train, units)
        X, y = stacked(train, units, decay)
        dist = np.abs(X - y[:, None]).sum(axis=0)
        panels = {}
        for k in ks:
            greedy = greedy_selection(X, y, max_boxes=k, candidates=40, costs=costs,
                                      budget=k)[-1]
            affordable = np.flatnonzero(costs <= k)
            nearest = affordable[np.argsort(dist[affordable])[:pool]]
            idx = np.unique(np.concatenate([nearest, greedy["boxes"]]))
            result = exact_selection(X[:, idx], y, k, time_limit=time_limit, costs=costs[idx])
            if result["loss"] < greedy["loss"]:
                chosen = idx[result["boxes"]]
                panels[k] = Panel([units[i] for i in chosen], np.asarray(result["weights"]))
            else:
                panels[k] = _panel(units, greedy)
        return panels
    method.readings = ("unit",)
    method.ks = ks
    return method


def greedy_regularized(
    grid: dict[str, list[float]],
    decay: float = 0.7,
    candidates: int = 40,
    tune_budget: int = 50,
    inner_folds: int = 2,
    ks: tuple[int, ...] = (35, 50, 70),
    nested: bool = False,
) -> Method:
    """Greedy selection under a box budget with regularized weights.

    `grid` maps one or more of "mu" (pull towards size-proportional weights),
    "calibration" (stratum targets) and "noise" (perturbed copies) to candidate
    values. The value is chosen by inner validation: each of the last
    `inner_folds` training elections is predicted from the elections before it
    at `tune_budget` boxes, and the setting with the lowest mean seat L1 wins
    (ties: lower share L1). The test election is never used.
    """
    names = list(grid)
    settings = [dict(zip(names, values)) for values in np.array(np.meshgrid(
        *[grid[n] for n in names])).T.reshape(-1, len(names))]

    def fit(train, budgets, setting, rng) -> dict[int, Panel]:
        units = candidate_units(train)
        costs = unit_costs(train, units)
        sizes = train[-1].units.loc[units].sum(axis=1).values.astype(float)
        X, y = stacked(train, units, decay, calibration=setting.get("calibration", 0.0),
                       noise=setting.get("noise", 0.0), rng=rng)
        panels = _budget_panels(X, y, units, costs, budgets, candidates, nested,
                                sizes=sizes, mu=setting.get("mu", 0.0))
        for panel in panels.values():
            panel.info = dict(setting)
        return panels

    def method(train, budgets, rng) -> dict[int, Panel]:
        best = None
        for setting in settings:
            scores = []
            for v in range(len(train) - inner_folds, len(train)):
                if v < 1:
                    continue
                panel = fit(train[:v], [tune_budget], setting, rng)[tune_budget]
                pred = panel.predict(train[v], "unit", rng)
                result = score(pred, train[v])
                scores.append((result["seat_L1"], result["share_L1"]))
            key = tuple(np.mean(scores, axis=0)) if scores else (0.0, 0.0)
            if best is None or key < best[0]:
                best = (key, setting)
        return fit(train, budgets, best[1], rng)
    method.readings = ("unit",)
    method.ks = ks
    return method


def stratified(train, ks, rng) -> dict[int, Panel]:
    """Stratified random panel; k = units, read one box each.

    Strata come from the last training election: dominant bloc of the unit and
    whether that bloc has at least 60% of its votes. Units are allocated to
    strata in proportion to their votes (at least one per stratum while k
    allows) and drawn by size within a stratum. A unit's weight is its
    stratum's vote share divided by the stratum's sample size.
    """
    e = train[-1]
    stratum = strata(e)
    size = e.units.sum(axis=1)
    weight = size.groupby(stratum).sum() / size.sum()
    panels = {}
    for k in ks:
        raw = weight * k
        alloc = np.floor(raw).astype(int).clip(lower=1 if k >= len(weight) else 0)
        for h in (raw - np.floor(raw)).sort_values(ascending=False).index:
            if alloc.sum() >= k:
                break
            alloc[h] += 1
        chosen, w = [], []
        for h, n in alloc.items():
            members = size[stratum == h]
            n = min(n, len(members))
            if n == 0:
                continue
            pick = rng.choice(members.index, size=n, replace=False, p=(members / members.sum()).values)
            chosen += list(pick)
            w += [weight[h] / n] * n
        panels[k] = Panel(chosen, np.asarray(w))
    return panels


def _panel(units: list[str], h: dict) -> Panel:
    return Panel([units[i] for i in h["boxes"]], np.asarray(h["weights"]))


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
        rows.append({"test": t, "method": "all_boxes", "k": len(test.units), "reading": "unit",
                     "boxes": int(test.unit_boxes.sum()), **score(test.units.sum(), test)})
        for name, method in methods.items():
            rng = np.random.default_rng(seed)
            n_fits = draws if name.startswith(("random", "stratified")) else 1
            method_ks = list(getattr(method, "ks", ks))
            fits = [method(train, method_ks, rng) for _ in range(n_fits)]
            for k in method_ks:
                for reading in getattr(method, "readings", ("unit", "single_box")):
                    results = []
                    for panels in fits:
                        reps = 1 if reading == "unit" or n_fits > 1 else draws
                        for _ in range(reps):
                            pred = panels[k].predict(test, reading, rng)
                            if pred is not None:
                                results.append({"boxes": panels[k].boxes(test, reading),
                                                **score(pred, test)})
                    info = panels[k].info or {}
                    mean = pd.DataFrame(results).mean().to_dict()
                    rows.append({"test": t, "method": name, "k": k, "reading": reading,
                                 **{f"param_{p}": v for p, v in info.items()}, **mean})
    return pd.DataFrame(rows)
