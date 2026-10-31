"""Swing model: the previous result of every box plus the change measured in a panel.

On election night the full result of the previous election is known. The panel
measures how each bloc changed in its units; the national bloc shares are
estimated as

    B_t = B_{t-1} + sum_u w_u (b_t(u) - b_{t-1}(u)),   w >= 0, sum(w) = 1

with b(u) the bloc shares of unit u. Blocs exist in every election, so new
lists need no lineage. Within a bloc (decision M16):
- without `family`, the bloc is split into its lists by the panel's weighted
  list shares;
- with `family`, a list whose party family ran as exactly one list in both
  elections (and had at least MIN_SHARE before) gets its previous national
  share plus the panel's weighted swing; the other lists of the bloc (new lists,
  merged or split families) get the panel's estimate of their part of the bloc,
  and the continuing lists are scaled to fill the rest of the bloc.

A joint panel (M17) also predicts the level (the panel's weighted list shares)
with the same units and weights, and mixes: alpha * level + (1 - alpha) * swing.

Within-bloc rows (M20) ask the panel to reproduce how every bloc splits into its
lists. Seat intervals (M21-M22) come from the panel's own errors on past
elections (inner validation), scaled by sqrt(share), separately for continuing
and new lists.
"""

from dataclasses import dataclass
from functools import lru_cache

import numpy as np
import pandas as pd

from election_estimation.data import load_parties
from election_estimation.elections import seat_rules
from election_estimation.evaluate import (Election, Method, Panel, candidate_units,
                                          recency_weights, score, stacked)
from election_estimation.metrics import bader_ofer, to_blocs
from election_estimation.selection import greedy_selection

BLOCS = ["right", "haredi", "center_left", "arab", "other"]
MIN_SHARE = 0.01


def unit_shares(e: Election, units: list[str]) -> pd.DataFrame:
    counts = e.units.loc[units]
    return counts.div(counts.sum(axis=1), axis=0)


def unit_blocs(e: Election, units: list[str]) -> pd.DataFrame:
    """Bloc vote shares of the given units of e (rows: units, columns: BLOCS)."""
    counts = e.units.loc[units]
    blocs = counts.T.groupby(pd.Index([e.blocs.get(c, "other") for c in counts.columns])).sum().T
    blocs = blocs.reindex(columns=BLOCS, fill_value=0)
    return blocs.div(blocs.sum(axis=1), axis=0)


def national_blocs(e: Election) -> pd.Series:
    return to_blocs(e.shares, e.blocs).reindex(BLOCS, fill_value=0.0)


@lru_cache(maxsize=None)
def families(knesset: int) -> dict[str, str]:
    """List letter -> party family (a list without a family is its own)."""
    family = load_parties(knesset)["family"]
    return {letter: f if f else f"_{knesset}_{letter}" for letter, f in family.items()}


def continuing(prev: Election, cur: Election) -> dict[str, str]:
    """Lists of cur whose family ran as exactly one list in both elections and had
    at least MIN_SHARE in prev: letter in cur -> letter in prev."""
    fp = pd.Series(families(prev.knesset)).reindex(prev.parties).dropna()
    fc = pd.Series(families(cur.knesset)).reindex(cur.parties).dropna()
    once_prev = {f: letter for letter, f in fp[~fp.duplicated(keep=False)].items()}
    once_cur = fc[~fc.duplicated(keep=False)]
    return {letter: once_prev[f] for letter, f in once_cur.items()
            if f in once_prev and prev.shares[once_prev[f]] >= MIN_SHARE}


@dataclass
class SwingPanel(Panel):
    previous: Election | None = None  # the election before the one predicted
    family: bool = False              # family swing within blocs
    alpha: float = 0.0                # weight of the level prediction
    errors: dict | None = None        # error scale per list type, see `list_errors`

    def predict(self, e: Election, reading: str, rng: np.random.Generator) -> pd.Series | None:
        assert reading == "unit", "the swing panel counts whole units"
        prev = self.previous
        present = [u for u in self.units if u in e.units.index and u in prev.units.index]
        if not present:
            return None
        w = pd.Series(self.weights, index=self.units).loc[present]
        w = w / w.sum()
        cur_s, prev_s = unit_shares(e, present), unit_shares(prev, present)
        level = cur_s.mul(w, axis=0).sum()
        if self.alpha >= 1:
            return level
        swing = (unit_blocs(e, present) - unit_blocs(prev, present)).mul(w, axis=0).sum()
        blocs = (national_blocs(prev) + swing).clip(lower=0)
        bloc = pd.Series({p: e.blocs.get(p, "other") for p in e.parties})
        fixed = pd.Series(dtype=float)
        if self.family:
            fixed = pd.Series({l: prev.shares[lp] + (cur_s[l] - prev_s[lp]) @ w
                               for l, lp in continuing(prev, e).items()}).clip(lower=0)
        pred = pd.Series(0.0, index=e.parties)
        for b, total in blocs.items():
            members = bloc.index[bloc == b]
            fx = [l for l in members if l in fixed.index]
            rest = [l for l in members if l not in fixed.index]
            in_bloc = level[members].sum()
            if in_bloc <= 0:
                continue
            rest_total = total * level[rest].sum() / in_bloc
            pred[rest] = total * level[rest] / in_bloc
            if fx:
                pred[fx] = (fixed[fx] / fixed[fx].sum() * (total - rest_total)
                            if fixed[fx].sum() > 0 else total * level[fx] / in_bloc)
        pred = pred / pred.sum()
        return self.alpha * level + (1 - self.alpha) * pred


def within_rows(e: Election, units: list[str]) -> tuple[np.ndarray, np.ndarray]:
    """Rows asking the panel's within-bloc split to match the national one.

    For every list l with at least MIN_SHARE in bloc b, the ratio
    sum_u w_u s_u(l) / sum_u w_u s_u(b) should equal p(l|b), the list's national
    share of its bloc. Multiplied out this is linear in w:
    sum_u w_u (s_u(l) - p(l|b) s_u(b)) = 0.
    """
    shares, blocs = unit_shares(e, units), unit_blocs(e, units)
    nat_blocs = national_blocs(e)
    X, y = [], []
    for l in e.shares.index[e.shares >= MIN_SHARE]:
        b = e.blocs.get(l, "other")
        if nat_blocs[b] <= 0:
            continue
        X.append((shares[l] - e.shares[l] / nat_blocs[b] * blocs[b]).values)
        y.append(0.0)
    return np.vstack(X), np.array(y)


def stacked_swing(train: list[Election], units: list[str], decay: float,
                  level: float = 0.0, family: bool = False,
                  within: float = 0.0) -> tuple[np.ndarray, np.ndarray]:
    """Target rows: for every consecutive pair of training elections, the weighted
    unit bloc swings should equal the national bloc swing (pairs weighted by the
    recency of their later election). With `family`, rows for the swing of every
    continuing family are added. With `level` > 0, the national list-share rows
    of `evaluate.stacked`, scaled by `level`, are added so that the panel also
    splits the blocs into lists correctly; with `within` > 0, the within-bloc
    rows of every training election (`within_rows`), scaled by `within` and its
    recency weight."""
    rho = recency_weights(train[1:], decay)
    X_rows, y_rows = [], []
    for prev, cur, r in zip(train[:-1], train[1:], rho):
        X_rows.append((unit_blocs(cur, units) - unit_blocs(prev, units)).values.T * r)
        y_rows.append((national_blocs(cur) - national_blocs(prev)).values * r)
        if family:
            pairs = continuing(prev, cur)
            if pairs:
                cur_s, prev_s = unit_shares(cur, units), unit_shares(prev, units)
                X_rows.append(np.vstack([(cur_s[l] - prev_s[lp]).values
                                         for l, lp in pairs.items()]) * r)
                y_rows.append(np.array([cur.shares[l] - prev.shares[lp]
                                        for l, lp in pairs.items()]) * r)
    if level > 0:
        X, y = stacked(train, units, decay)
        X_rows.append(X * level)
        y_rows.append(y * level)
    if within > 0:
        for e, r in zip(train, recency_weights(train, decay)):
            X, y = within_rows(e, units)
            X_rows.append(X * r * within)
            y_rows.append(y * r * within)
    return np.vstack(X_rows), np.concatenate(y_rows)


def _settings(grid: dict[str, list[float]]) -> list[dict]:
    names = list(grid)
    return [dict(zip(names, values)) for values in np.array(np.meshgrid(
        *[grid[n] for n in names])).T.reshape(-1, len(names))]


def swing_panel(
    grid: dict[str, list[float]],
    decay: float = 0.7,
    candidates: int = 40,
    tune_k: int = 35,
    inner_folds: int = 2,
    ks: tuple[int, ...] = (20, 30, 35, 40, 50),
    family: bool = False,
    alphas: tuple[float, ...] = (0.0,),
    select_by: str = "seat_L1",
) -> Method:
    """Swing panels of k units (every unit costs 1), nested across k.

    `grid` maps "mu" (pull of the weights towards size-proportional weights) and
    "level" (weight of the list-share rows) to candidate values; `alphas` are the
    candidate mixing weights of the level prediction. The setting and alpha are
    chosen by inner validation: each of the last `inner_folds` training elections
    is predicted from the ones before it with `tune_k` units; the lowest mean
    `select_by` wins (ties: the other of seat L1 / share L1). The test election is
    never used.
    """
    other = "share_L1" if select_by == "seat_L1" else "seat_L1"

    def fit(train, budgets, setting, alpha) -> dict[int, SwingPanel]:
        units = candidate_units(train)
        sizes = train[-1].units.loc[units].sum(axis=1).values.astype(float)
        X, y = stacked_swing(train, units, decay, level=setting.get("level", 0.0),
                             family=family, within=setting.get("within", 0.0))
        history = greedy_selection(X, y, max_boxes=max(budgets), candidates=candidates,
                                   sizes=sizes, mu=setting.get("mu", 0.0))
        panels = {}
        for k in budgets:
            h = [h for h in history if h["k"] <= k][-1]
            panels[k] = SwingPanel([units[i] for i in h["boxes"]], np.asarray(h["weights"]),
                                   info={**setting, "alpha": alpha}, previous=train[-1],
                                   family=family, alpha=alpha)
        return panels

    def method(train, budgets, rng) -> dict[int, SwingPanel]:
        scores, errors = {}, {}
        for i, setting in enumerate(_settings(grid)):
            for v in range(len(train) - inner_folds, len(train)):
                if v < 3:  # at least two training pairs
                    continue
                panel = fit(train[:v], [tune_k], setting, 0.0)[tune_k]
                for alpha in alphas:
                    panel.alpha = alpha
                    pred = panel.predict(train[v], "unit", rng)
                    result = score(pred, train[v])
                    scores.setdefault((i, alpha), []).append((result[select_by], result[other]))
                    errors.setdefault((i, alpha), []).append(
                        list_errors(pred, train[v], train[v - 1]))
        settings = _settings(grid)
        if not scores:
            return fit(train, budgets, settings[0], alphas[0])
        (i, alpha), _ = min(scores.items(), key=lambda kv: tuple(np.mean(kv[1], axis=0)))
        panels = fit(train, budgets, settings[i], alpha)
        scale = error_scale(pd.concat(errors[(i, alpha)]))
        for panel in panels.values():
            panel.errors = scale
        return panels
    method.readings = ("unit",)
    method.ks = ks
    return method


# --- uncertainty ---------------------------------------------------------------

def list_errors(pred: pd.Series, e: Election, prev: Election) -> pd.DataFrame:
    """Standardized share errors of a prediction of e, per list with at least
    MIN_SHARE (true or predicted): (pred - true) / sqrt(pred), and whether the
    list is new (its family did not run as one list in prev)."""
    pred = pred.reindex(e.parties, fill_value=0.0)
    pred = pred / pred.sum()
    keep = (e.shares >= MIN_SHARE) | (pred >= MIN_SHARE)
    new = ~pd.Series(e.parties, index=e.parties).isin(list(continuing(prev, e)))
    z = (pred - e.shares) / np.sqrt(pred.clip(lower=MIN_SHARE))
    return pd.DataFrame({"z": z[keep], "new": new[keep]})


def error_scale(errors: pd.DataFrame) -> dict[str, float]:
    """RMS of the standardized errors for continuing and new lists (new lists fall
    back to the larger of the two when they have fewer than 3 errors)."""
    rms = lambda z: float(np.sqrt(np.mean(np.square(z)))) if len(z) else np.nan
    cont, new = rms(errors.loc[~errors["new"], "z"]), rms(errors.loc[errors["new"], "z"])
    if (errors["new"].sum() < 3) or np.isnan(new):
        new = max(cont, new) if not np.isnan(new) else cont
    return {"continuing": cont, "new": new}


def seat_intervals(panel: SwingPanel, e: Election, rng: np.random.Generator,
                   draws: int = 1000, level: float = 0.9) -> pd.DataFrame:
    """Point seats, a central `level` seat interval and the probability of passing
    the threshold for every list, by simulating the panel's past errors:
    share = pred + N(0, scale_type^2 * pred), clipped at 0 and renormalized."""
    pred = panel.predict(e, "unit", rng).reindex(e.parties, fill_value=0.0)
    pred = pred / pred.sum()
    rules = seat_rules(e.knesset)
    new = ~pd.Series(e.parties, index=e.parties).isin(list(continuing(panel.previous, e)))
    sd = np.sqrt(pred.clip(lower=MIN_SHARE)) * np.where(new, panel.errors["new"],
                                                        panel.errors["continuing"])
    sims = np.clip(pred.values + rng.normal(size=(draws, len(pred))) * sd.values, 0, None)
    seats = np.array([bader_ofer(pd.Series(s / s.sum(), index=e.parties), **rules).values
                      for s in sims])
    passed = sims / sims.sum(axis=1, keepdims=True) >= rules["threshold"]
    tail = (1 - level) / 2
    return pd.DataFrame({
        "share": pred,
        "seats": bader_ofer(pred, **rules),
        "low": np.quantile(seats, tail, axis=0, method="lower"),
        "high": np.quantile(seats, 1 - tail, axis=0, method="higher"),
        "p_pass": passed.mean(axis=0),
    }, index=e.parties)
