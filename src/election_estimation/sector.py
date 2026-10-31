"""Sector ratio model (decisions M30-M35).

Every statistical area of the new election is predicted from its own previous
result plus the change its sector shows in the panel:

- sector: dominant bloc of the area in the previous election and whether that
  bloc has at least 60% (as `evaluate.strata`); sectors under SMALL_SECTOR of
  the votes are merged into "small";
- expected votes of an area: its number of boxes in the new election (known
  before election day) times its previous votes per box. A new area takes the
  per-box votes and shares of its settlement's previous areas;
- turnout: in each sector, the mean ratio of a counted box's votes to its area's
  previous votes per box;
- shares: in each sector, the previous shares plus the panel's mean change
  (difference estimator); a list whose family did not run alone before (new)
  starts from zero.

Panels are drawn per sector with probability proportional to expected votes
(systematic, sorted by the share of the sector's bloc, so the draw is spread
over the sector), one box counted per area. Sector sample sizes follow a Neyman
allocation under a vote budget: more areas where past changes varied more.
"""

from dataclasses import dataclass
from functools import lru_cache

import numpy as np
import pandas as pd

from election_estimation.data import load_ballots
from election_estimation.evaluate import Election, _areas, load_election
from election_estimation.swing import BLOCS, continuing

SMALL_SECTOR = 0.02
PURE = 0.6
MIN_PER_SECTOR = 3
RATIO_MIN = 0.005
# The model used for the Knesset 27 panels and the site (M40; reports/sector_variants.md).
MODEL = {"sectors": "cluster", "k": 12, "spread": "list", "estimator": "ratio"}


@lru_cache(maxsize=None)
def area_election(knesset: int) -> Election:
    """Regular boxes by statistical area, with a "settlement" column on the boxes."""
    e = load_election(knesset, "area", "regular")
    ballots = load_ballots(knesset)
    regular = ballots[~ballots["is_envelopes"] & (ballots["valid"] > 0)].copy()
    regular["unit"] = _areas(regular, knesset)
    assert (regular["unit"].values == e.boxes["unit"].values).all()
    e.boxes["settlement"] = regular["settlement_code"].astype(str).values
    return e


def bloc_counts(counts: pd.DataFrame, blocs: dict[str, str]) -> pd.DataFrame:
    cols = pd.Index([blocs.get(c, "other") for c in counts.columns])
    return counts.T.groupby(cols).sum().T.reindex(columns=BLOCS, fill_value=0)


def classify(counts: pd.DataFrame, blocs: dict[str, str]) -> pd.Series:
    """Sector name of every row (before merging small sectors)."""
    b = bloc_counts(counts, blocs)
    share = b.div(b.sum(axis=1), axis=0)
    return share.idxmax(axis=1) + np.where(share.max(axis=1) >= PURE, "_pure", "_mixed")


@dataclass
class Prior:
    """What is known about the new election before election day."""
    prev: Election
    lists: list[str]               # lists of the new election
    mapping: dict[str, str]        # new list -> previous list (continuing lists)
    sector: pd.Series              # area -> sector
    expected: pd.Series            # area -> expected votes (boxes x previous votes per box)
    per_box: pd.Series             # area -> previous votes per box
    prev_shares: pd.DataFrame      # area -> previous shares of the new lists (0 for new lists)
    prev_blocs: pd.DataFrame       # area -> previous bloc shares
    cost: pd.Series                # area -> votes of one box (previous)

    @property
    def sectors(self) -> list[str]:
        return sorted(self.sector.unique())


def kmeans(x: np.ndarray, w: np.ndarray, k: int, seed: int = 0, iters: int = 100) -> np.ndarray:
    """Weighted k-means (k-means++ start, fixed seed): cluster index per row."""
    rng = np.random.default_rng(seed)
    centers = [x[rng.choice(len(x), p=w / w.sum())]]
    for _ in range(1, k):
        d = np.min([((x - c) ** 2).sum(axis=1) for c in centers], axis=0)
        centers.append(x[rng.choice(len(x), p=w * d / (w * d).sum())])
    c = np.array(centers)
    for _ in range(iters):
        label = ((x[:, None, :] - c[None]) ** 2).sum(axis=2).argmin(axis=1)
        new = np.array([np.average(x[label == j], axis=0, weights=w[label == j])
                        if (label == j).any() else c[j] for j in range(k)])
        if np.allclose(new, c):
            break
        c = new
    return label


def make_prior(prev: Election, cur_boxes: pd.Series, cur_settlement: pd.Series,
               lists: list[str], mapping: dict[str, str], sectors: str = "bloc",
               k: int = 12) -> Prior:
    """`cur_boxes`: boxes per area of the new election; `cur_settlement`: its settlement.

    `sectors`: "bloc" (dominant bloc, pure at 60%) or "cluster" (weighted k-means with
    `k` clusters on the previous shares of the lists with at least 1%, the rest summed)."""
    pb = area_election(prev.knesset).boxes
    prev_settlement = pb.groupby("unit")["settlement"].agg(lambda s: s.mode().iloc[0])
    counts = prev.units
    sett_counts = counts.groupby(prev_settlement.reindex(counts.index)).sum()
    sett_boxes = prev.unit_boxes.groupby(prev_settlement.reindex(counts.index)).sum()
    national = counts.sum()
    rows, per_box = {}, {}
    for a in cur_boxes.index:
        if a in counts.index:
            c, n = counts.loc[a], prev.unit_boxes[a]
        elif cur_settlement[a] in sett_counts.index:
            c, n = sett_counts.loc[cur_settlement[a]], sett_boxes[cur_settlement[a]]
        else:
            c, n = national, len(pb)
        rows[a] = c
        per_box[a] = c.sum() / n
    c = pd.DataFrame(rows).T[prev.parties]
    per_box = pd.Series(per_box)
    expected = cur_boxes * per_box
    if sectors == "bloc":
        sector = classify(c, prev.blocs)
    else:
        major = list(prev.shares.index[prev.shares >= 0.01])
        x = c[major].div(c.sum(axis=1), axis=0)
        x["_rest"] = 1 - x.sum(axis=1)
        label = kmeans(x.values, expected.values.astype(float), k)
        sector = pd.Series([f"c{j:02d}" for j in label], index=c.index)
    size = expected.groupby(sector).sum() / expected.sum()
    sector = sector.where(sector.map(size) >= SMALL_SECTOR, "small")
    shares = c.div(c.sum(axis=1), axis=0)
    prev_shares = pd.DataFrame({l: shares[mapping[l]] if l in mapping else 0.0 for l in lists},
                               index=c.index)
    b = bloc_counts(c, prev.blocs)
    return Prior(prev, lists, mapping, sector, expected, per_box, prev_shares,
                 b.div(b.sum(axis=1), axis=0), per_box)


def prior_for(prev: Election, cur: Election, **kwargs) -> Prior:
    """Prior of a past election (its box counts and lists are taken as known)."""
    cb = area_election(cur.knesset).boxes
    settlement = cb.groupby("unit")["settlement"].agg(lambda s: s.mode().iloc[0])
    return make_prior(prev, cur.unit_boxes, settlement, cur.parties, continuing(prev, cur),
                      **kwargs)


@lru_cache(maxsize=None)
def transition_prior(prev: int, cur: int) -> Prior:
    return prior_for(area_election(prev), area_election(cur))


# --- allocation -----------------------------------------------------------------

def transition_spread(prev: Election, cur: Election) -> pd.DataFrame:
    """Per sector of a past transition: the spread of what one counted box shows.

    For every box of `cur` in an area of `prev`: r = box votes / previous votes per
    box, and the bloc change q - p. Returns per sector the vote-weighted variance of
    r (q - p) summed over blocs, the variance of r, and the sector's size."""
    pr = prior_for(prev, cur)
    boxes = area_election(cur.knesset).boxes
    boxes = boxes[boxes["unit"].isin(prev.units.index)]
    votes = boxes[cur.parties].sum(axis=1)
    q = bloc_counts(boxes[cur.parties], cur.blocs).div(votes, axis=0)
    p = pr.prev_blocs.loc[boxes["unit"]].set_index(boxes.index)
    r = votes / pr.per_box.loc[boxes["unit"]].values
    sec = pr.sector.loc[boxes["unit"]].values
    rows = {}
    for s in pr.sectors:
        m = sec == s
        if m.sum() < 2:
            continue
        w = votes[m] / votes[m].sum()
        z = (q[m] - p[m]).mul(r[m], axis=0)
        var_z = float((((z - z.mul(w, axis=0).sum()) ** 2).mul(w, axis=0)).sum().sum())
        var_r = float((((r[m] - (r[m] * w).sum()) ** 2) * w).sum())
        rows[s] = {"var_change": var_z, "var_turnout": var_r}
    return pd.DataFrame(rows).T


def list_spread(prior: Prior, train: list[Election]) -> pd.Series:
    """Per sector of `prior` (its labels applied to past areas): the variance of what
    one counted box shows, summed over the lists, mean over past transitions.

    For every box of a past election in an area labelled by `prior`: r = box votes /
    previous votes per box and the list change q - p (new lists from 0); the
    vote-weighted variance of r (q - p) summed over lists, plus the variance of r
    times ||P_s - P||^2 of the sector's previous list shares."""
    m = prior.expected.groupby(prior.sector).sum()
    shares = prior.prev_shares.mul(prior.expected, axis=0).groupby(prior.sector).sum()
    shares = shares.div(m, axis=0)
    gap = ((shares - shares.mul(m / m.sum(), axis=0).sum()) ** 2).sum(axis=1)
    out = []
    for a, b in zip(train[:-1], train[1:]):
        pr = transition_prior(a.knesset, b.knesset)
        boxes = area_election(b.knesset).boxes
        boxes = boxes[boxes["unit"].isin(a.units.index) & boxes["unit"].isin(prior.sector.index)]
        votes = boxes[b.parties].sum(axis=1)
        q = boxes[b.parties].div(votes, axis=0)
        p = pr.prev_shares.loc[boxes["unit"]].set_index(boxes.index)[b.parties]
        r = votes / pr.per_box.loc[boxes["unit"]].values
        sec = prior.sector.loc[boxes["unit"]].values
        rows = {}
        for s in prior.sectors:
            k = sec == s
            if k.sum() < 2:
                continue
            w = votes[k] / votes[k].sum()
            z = (q[k] - p[k]).mul(r[k], axis=0)
            var_z = float((((z - z.mul(w, axis=0).sum()) ** 2).mul(w, axis=0)).sum().sum())
            var_r = float((((r[k] - (r[k] * w).sum()) ** 2) * w).sum())
            rows[s] = var_z + var_r * gap[s]
        out.append(pd.Series(rows))
    return pd.concat(out, axis=1).mean(axis=1)


def allocate(prior: Prior, train: list[Election], budget: float,
             neyman: bool = True, spread: str = "bloc") -> pd.Series:
    """Areas per sector under a vote budget (share of the previous valid votes).

    Neyman: n_s proportional to M_s sigma_s / sqrt(c_s), with sigma_s^2 the mean over
    past transitions of var_change + var_turnout * ||P_s - P||^2 (P_s the sector's
    bloc shares) and c_s the expected cost of one area. Otherwise proportional to
    M_s / sqrt(c_s). `spread` = "list" uses `list_spread` (the prior's own sector
    labels, changes per list) instead of the bloc changes of each transition's
    own sectors."""
    m = prior.expected.groupby(prior.sector).sum()
    cost = (prior.expected * prior.cost).groupby(prior.sector).sum() / m
    if neyman and spread == "list":
        var = list_spread(prior, train)
        sigma = np.sqrt(var.reindex(m.index).fillna(var.mean()))
    elif neyman:
        spreads = [transition_spread(a, b) for a, b in zip(train[:-1], train[1:])]
        blocs = prior.prev_blocs.mul(prior.expected, axis=0).groupby(prior.sector).sum()
        blocs = blocs.div(blocs.sum(axis=1), axis=0)
        gap = ((blocs - blocs.mul(m / m.sum(), axis=0).sum()) ** 2).sum(axis=1)
        var = pd.concat([(sp["var_change"] + sp["var_turnout"] * gap.reindex(sp.index))
                         for sp in spreads], axis=1).mean(axis=1)
        sigma = np.sqrt(var.reindex(m.index).fillna(var.mean()))
    else:
        sigma = pd.Series(1.0, index=m.index)
    raw = m * sigma / np.sqrt(cost)
    total = budget * prior.prev.units.values.sum()
    n = raw * (total / (raw * cost).sum())
    counts = prior.sector.value_counts().reindex(n.index)
    return np.clip(np.floor(n), MIN_PER_SECTOR, counts).astype(int)


# --- drawing and predicting ------------------------------------------------------

def draw(prior: Prior, n: pd.Series, rng: np.random.Generator,
         offset: float = 0.0) -> pd.Series:
    """Systematic PPS draw per sector: area -> number of times drawn. `offset` (a
    fraction of the sampling step) shifts the random start: draws with the same
    rng state and offsets 0, 1/3, 2/3 are valid samples that barely overlap."""
    picks = []
    for s, k in n.items():
        areas = prior.sector.index[prior.sector == s]
        main = prior.prev_blocs.loc[areas].mul(prior.expected[areas], axis=0).sum().idxmax()
        order = prior.prev_blocs.loc[areas, main].sort_values().index
        size = prior.expected[order].values
        cum = np.cumsum(size)
        step = cum[-1] / k
        points = (rng.uniform(0, step) + offset * step) % step + step * np.arange(k)
        picks.append(pd.Series(order[np.searchsorted(cum, points)]))
    return pd.concat(picks).value_counts()


def read_boxes(cur: Election, areas: pd.Index, rng: np.random.Generator) -> pd.DataFrame:
    """One random regular box of each area (votes per list)."""
    boxes = cur.boxes[cur.boxes["unit"].isin(areas)]
    return boxes.groupby("unit").sample(n=1, random_state=rng).set_index("unit")[cur.parties]


def predict(prior: Prior, panel: pd.Series, counted: pd.DataFrame,
            turnout: bool = True, by_sector: bool = False,
            estimator: str = "difference", missing: str = "prev") -> pd.Series | pd.DataFrame:
    """National votes per list from the counted boxes of the panel areas.

    `panel`: area -> times drawn (or any weights); `counted`: area -> votes per list
    of the box. `by_sector`: return sectors x lists instead of the national sum.
    `estimator`: "difference" (previous share plus the mean change) or "ratio" (previous
    share times the panel's ratio of current to previous votes of the list, for lists
    with at least RATIO_MIN of the sector; the others by difference). `missing`: a sector
    with no counted area keeps its previous result ("prev") or takes the turnout and
    change of all counted areas ("pooled")."""
    counted = counted.reindex(columns=prior.lists, fill_value=0).loc[panel.index]
    votes = counted.sum(axis=1)
    q = counted.div(votes, axis=0)
    r = votes / prior.per_box[panel.index] if turnout else pd.Series(1.0, index=panel.index)
    p = prior.prev_shares.loc[panel.index]
    w = panel.astype(float)
    sec = prior.sector[panel.index]
    out = {}
    wa = w / w.sum()
    R_all = float((r * wa).sum())
    change_all = (q - p).mul(r * wa, axis=0).sum()
    for s in prior.sectors:
        areas = prior.sector.index[prior.sector == s]
        m_s = prior.expected[areas].sum()
        P_s = prior.prev_shares.loc[areas].mul(prior.expected[areas], axis=0).sum() / m_s
        k = sec == s
        if not k.any():
            if missing == "pooled":
                y = (R_all * P_s + change_all).clip(lower=0)
                out[s] = y / y.sum() * R_all * m_s
            else:
                out[s] = P_s * m_s
            continue
        ws = w[k] / w[k].sum()
        R = float((r[k] * ws).sum())
        change = (q[k] - p[k]).mul(r[k] * ws, axis=0).sum()
        y = (R * P_s + change).clip(lower=0)
        if estimator == "ratio":
            num = q[k].mul(r[k] * ws, axis=0).sum()
            den = p[k].mul(ws, axis=0).sum()
            use = (P_s >= RATIO_MIN) & (den > 0)
            y[use] = (num[use] / den[use] * P_s[use]).clip(lower=0)
        out[s] = y / y.sum() * R * m_s
    out = pd.DataFrame(out).T
    return out if by_sector else out.sum()


# --- uncertainty and the point under the threshold ------------------------------

def bootstrap(prior: Prior, panel: pd.Series, counted: pd.DataFrame,
              rng: np.random.Generator, reps: int = 200,
              estimator: str = "difference") -> pd.DataFrame:
    """Predicted votes of `reps` panels resampled with replacement within each
    sector (the election-night spread of the panel itself): reps x lists."""
    sec = prior.sector[panel.index]
    groups = [np.repeat(panel.index[sec.values == s].values,
                        panel[sec.values == s].values) for s in prior.sectors]
    out = []
    for _ in range(reps):
        pick = pd.Series(np.concatenate([rng.choice(g, len(g)) for g in groups if len(g)]))
        p = pick.value_counts()
        out.append(predict(prior, p, counted.loc[p.index], estimator=estimator))
    return pd.DataFrame(out).reset_index(drop=True)


def medoid_seats(seats: pd.DataFrame, candidates: pd.DataFrame | None = None) -> pd.Series:
    """The seat vector (among `candidates`, default all rows) with the least mean
    seats moved to the rows of `seats`: the point that minimizes the expected error
    when lists sit near the threshold."""
    cand = seats if candidates is None else candidates
    s = seats.values
    cost = [np.abs(s - c).sum(axis=1).mean() for c in cand.values]
    return cand.iloc[int(np.argmin(cost))]
