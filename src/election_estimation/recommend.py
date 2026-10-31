"""Recommended panels for a future election under a vote budget (decisions M24-M31).

A panel is a set of units with weights for the joint level + swing model of
`swing.py` (family swing, within-bloc rows). Units are settlements counted in
full, or statistical areas read through one ballot box each. The budget is a
share of the valid votes of the last training election; a unit costs its votes
(a settlement) or the votes of an average box of it (an area).

`recommend` runs inner validation over the grid, then builds `alternatives`
panels from the best distinct settings; each later alternative pays a penalty
for units used by the earlier ones, so the alternatives differ and can stand in
for each other. Panels of the same alternative are nested across budgets.
"""

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from election_estimation.evaluate import Election, candidate_units, score
from election_estimation.selection import greedy_selection
from election_estimation.swing import (SwingPanel, _settings, error_scale, list_errors,
                                       prob_within, stacked_swing)


@dataclass
class Alternative:
    rank: int                       # 1 = best setting in inner validation
    setting: dict                   # mu, level, within
    alpha: float                    # weight of the level prediction
    errors: dict                    # budget share -> error scales from inner validation
    validation: float               # its mean inner-validation share L1
    panels: dict = field(default_factory=dict)  # budget share -> SwingPanel


def unit_costs_votes(e: Election, units: list[str], reading: str) -> np.ndarray:
    """Votes counted for each unit in e: the whole unit, or an average box of it."""
    votes = e.units.loc[units].sum(axis=1)
    if reading == "single_box":
        votes = votes / e.unit_boxes.loc[units]
    return votes.values.astype(float)


def fit_budget(train: list[Election], budgets: list[float], setting: dict, alpha: float,
               reading: str, decay: float, candidates: int,
               used: set[str] = frozenset(), penalty: float = 3.0,
               max_unit_share: float = 0.5) -> dict[float, SwingPanel]:
    """Panels for every budget share in `budgets` (nested: one greedy run at the
    largest budget). Units in `used` cost `penalty` times more in the ranking.
    A unit may cost at most `max_unit_share` of the smallest budget."""
    total = float(train[-1].units.values.sum())
    units = candidate_units(train)
    costs = unit_costs_votes(train[-1], units, reading)
    small = costs <= max_unit_share * min(budgets) * total  # several units in every panel
    units, costs = [u for u, s in zip(units, small) if s], costs[small]
    rank = costs * np.where(np.isin(units, list(used)), penalty, 1.0)
    sizes = train[-1].units.loc[units].sum(axis=1).values.astype(float)
    X, y = stacked_swing(train, units, decay, level=setting.get("level", 0.0), family=True,
                         within=setting.get("within", 0.0))
    history = greedy_selection(X, y, max_boxes=len(units), candidates=candidates, costs=costs,
                               budget=max(budgets) * total, sizes=sizes,
                               mu=setting.get("mu", 0.0), rank_costs=rank)
    panels = {}
    for b in budgets:
        h = [h for h in history if h["cost"] <= b * total][-1]
        panels[b] = SwingPanel([units[i] for i in h["boxes"]], np.asarray(h["weights"]),
                               info={**setting, "alpha": alpha}, previous=train[-1],
                               family=True, alpha=alpha)
    return panels


def recommend(
    train: list[Election],
    budgets: list[float],
    grid: dict[str, list[float]],
    alphas: tuple[float, ...],
    reading: str,
    rng: np.random.Generator,
    alternatives: int = 3,
    inner_folds: int = 3,
    readings_per_fold: int = 3,
    decay: float = 0.7,
    candidates: int = 20,
    penalty: float = 3.0,
) -> list[Alternative]:
    """Inner validation on share L1: each of the last `inner_folds` training
    elections is predicted from the ones before it at every budget (nested
    panels, single-box readings averaged over `readings_per_fold` draws). A
    setting's score is its mean share L1 over folds and budgets; its error scales
    are kept per budget. Then one Alternative per distinct setting, best first.
    The election to predict is never used."""
    settings = _settings(grid)
    scores, errors = {}, {}
    for i, setting in enumerate(settings):
        for v in range(len(train) - inner_folds, len(train)):
            if v < 2:  # at least one training pair
                continue
            panels = fit_budget(train[:v], budgets, setting, 0.0, reading, decay, candidates)
            draws = readings_per_fold if reading == "single_box" else 1
            for b, panel in panels.items():
                for alpha in alphas:
                    panel.alpha = alpha
                    for _ in range(draws):
                        pred = panel.predict(train[v], reading, rng)
                        scores.setdefault((i, alpha), []).append(
                            score(pred, train[v])["share_L1"])
                        errors.setdefault((i, alpha, b), []).append(
                            list_errors(pred, train[v], train[v - 1]))
    if not scores:  # too few training elections: first setting, no validation
        scores = {(0, alphas[0]): [np.nan]}
    best_per_setting = {}
    for (i, alpha), s in scores.items():
        if i not in best_per_setting or np.mean(s) < best_per_setting[i][1]:
            best_per_setting[i] = (alpha, float(np.mean(s)))
    order = sorted(best_per_setting, key=lambda i: best_per_setting[i][1])[:alternatives]
    result, used = [], set()
    for rank, i in enumerate(order, start=1):
        alpha, val = best_per_setting[i]
        panels = fit_budget(train, budgets, settings[i], alpha, reading, decay, candidates,
                            used=used, penalty=penalty)
        scales = {}
        for b, p in panels.items():
            errs = errors.get((i, alpha, b))
            p.errors = (error_scale(pd.concat(errs)) if errs
                        else {"continuing": 0.02, "new": 0.03})
            scales[b] = p.errors
        used |= set(panels[max(budgets)].units)
        result.append(Alternative(rank, settings[i], alpha, scales, val, panels))
    return result


def panel_probability(panel: SwingPanel, train: list[Election], rng: np.random.Generator,
                      draws: int = 1000) -> float:
    """P(at most 2 seats moved) for the next election, simulated around the last
    training election with the panel's error scales."""
    return prob_within(panel.errors, train[-1], train[-2], rng, draws=draws)
