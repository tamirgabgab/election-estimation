"""Swing model: the previous result of every box plus the change measured in a panel.

On election night the full result of the previous election is known. The panel
measures how each bloc changed in its units; the national bloc shares are
estimated as

    B_t = B_{t-1} + sum_u w_u (b_t(u) - b_{t-1}(u)),   w >= 0, sum(w) = 1

with b(u) the bloc shares of unit u. Blocs exist in every election, so new
lists need no lineage; the split of a bloc into its lists is read from the panel
(weighted list shares within the bloc). The weights are chosen so that the
weighted unit swings reproduce the national bloc swings of past consecutive
elections (plus, optionally, the national list shares, see `stacked_swing`).
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from election_estimation.evaluate import (Election, Method, Panel, candidate_units,
                                          recency_weights, score, stacked)
from election_estimation.metrics import to_blocs
from election_estimation.selection import greedy_selection

BLOCS = ["right", "haredi", "center_left", "arab", "other"]


def unit_blocs(e: Election, units: list[str]) -> pd.DataFrame:
    """Bloc vote shares of the given units of e (rows: units, columns: BLOCS)."""
    counts = e.units.loc[units]
    blocs = counts.T.groupby(pd.Index([e.blocs.get(c, "other") for c in counts.columns])).sum().T
    blocs = blocs.reindex(columns=BLOCS, fill_value=0)
    return blocs.div(blocs.sum(axis=1), axis=0)


def national_blocs(e: Election) -> pd.Series:
    return to_blocs(e.shares, e.blocs).reindex(BLOCS, fill_value=0.0)


@dataclass
class SwingPanel(Panel):
    previous: Election | None = None  # the election before the one predicted

    def predict(self, e: Election, reading: str, rng: np.random.Generator) -> pd.Series | None:
        assert reading == "unit", "the swing panel counts whole units"
        present = [u for u in self.units
                   if u in e.units.index and u in self.previous.units.index]
        if not present:
            return None
        w = pd.Series(self.weights, index=self.units).loc[present]
        w = w / w.sum()
        swing = (unit_blocs(e, present) - unit_blocs(self.previous, present)).mul(w, axis=0).sum()
        blocs = (national_blocs(self.previous) + swing).clip(lower=0)
        counts = e.units.loc[present]
        lists = counts.div(counts.sum(axis=1), axis=0).mul(w, axis=0).sum()
        bloc = pd.Series({p: e.blocs.get(p, "other") for p in e.parties})
        within = (lists / lists.groupby(bloc).transform("sum")).fillna(0.0)
        return within * bloc.map(blocs)


def stacked_swing(train: list[Election], units: list[str], decay: float,
                  level: float = 0.0) -> tuple[np.ndarray, np.ndarray]:
    """Target rows: for every consecutive pair of training elections, the weighted
    unit bloc swings should equal the national bloc swing (pairs weighted by the
    recency of their later election). With `level` > 0, the national list-share
    rows of `evaluate.stacked`, scaled by `level`, are added so that the panel
    also splits the blocs into lists correctly."""
    rho = recency_weights(train[1:], decay)
    X_rows, y_rows = [], []
    for prev, cur, r in zip(train[:-1], train[1:], rho):
        X = (unit_blocs(cur, units) - unit_blocs(prev, units)).values.T
        y = (national_blocs(cur) - national_blocs(prev)).values
        X_rows.append(X * r)
        y_rows.append(y * r)
    if level > 0:
        X, y = stacked(train, units, decay)
        X_rows.append(X * level)
        y_rows.append(y * level)
    return np.vstack(X_rows), np.concatenate(y_rows)


def swing_panel(
    grid: dict[str, list[float]],
    decay: float = 0.7,
    candidates: int = 40,
    tune_k: int = 35,
    inner_folds: int = 2,
    ks: tuple[int, ...] = (20, 30, 35, 40, 50),
) -> Method:
    """Swing panels of k units (every unit costs 1), nested across k.

    `grid` maps "mu" (pull of the weights towards size-proportional weights) and
    "level" (weight of the list-share rows) to candidate values, chosen by inner
    validation: each of the last `inner_folds` training elections is predicted
    from the ones before it with `tune_k` units, lowest mean seat L1 wins (ties:
    lower share L1). The test election is never used.
    """
    names = list(grid)
    settings = [dict(zip(names, values)) for values in np.array(np.meshgrid(
        *[grid[n] for n in names])).T.reshape(-1, len(names))]

    def fit(train, budgets, setting) -> dict[int, SwingPanel]:
        units = candidate_units(train)
        sizes = train[-1].units.loc[units].sum(axis=1).values.astype(float)
        X, y = stacked_swing(train, units, decay, level=setting.get("level", 0.0))
        history = greedy_selection(X, y, max_boxes=max(budgets), candidates=candidates,
                                   sizes=sizes, mu=setting.get("mu", 0.0))
        panels = {}
        for k in budgets:
            h = [h for h in history if h["k"] <= k][-1]
            panels[k] = SwingPanel([units[i] for i in h["boxes"]], np.asarray(h["weights"]),
                                   info=dict(setting), previous=train[-1])
        return panels

    def method(train, budgets, rng) -> dict[int, SwingPanel]:
        best = None
        for setting in settings:
            scores = []
            for v in range(len(train) - inner_folds, len(train)):
                if v < 3:  # at least two training pairs
                    continue
                panel = fit(train[:v], [tune_k], setting)[tune_k]
                result = score(panel.predict(train[v], "unit", rng), train[v])
                scores.append((result["seat_L1"], result["share_L1"]))
            key = tuple(np.mean(scores, axis=0)) if scores else (0.0, 0.0)
            if best is None or key < best[0]:
                best = (key, setting)
        return fit(train, budgets, best[1])
    method.readings = ("unit",)
    method.ks = ks
    return method
