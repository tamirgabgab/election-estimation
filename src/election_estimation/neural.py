"""Neural area model on top of the sector ratio model (decision M42).

The sector model gives every area the same proportional change as the panel
areas of its sector. This model predicts the shares of every area from that
base prediction plus a learned correction:

    logit_{a,l} = log(base_{a,l} + EPS) + MLP(features_{a,l}),  shares = softmax over l

The features of (area a, list l) describe the area (its previous shares by
bloc), the list (previous national share, bloc, new or continuing) and what the
panel shows (the list's change in a's sector and nationally, the sector's
turnout and how many of its areas were counted), so the network can learn
where a change is larger than proportional, flows between lists, and how much
to trust a sector with few counted areas. Area votes come from the sector
turnout (as in the sector model). The network is trained on past transitions
with simulated panels (`training_rows`), weighted by area votes, with a
cross-entropy loss on the area shares; it never sees the test election.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd
import torch

from election_estimation.evaluate import Election
from election_estimation.sector import RATIO_MIN, Prior, read_boxes
from election_estimation.swing import BLOCS

EPS = 1e-4
N_FEATURES = 20


@dataclass
class Batch:
    x: torch.Tensor        # areas x lists x features
    base: torch.Tensor     # areas x lists, the sector model's area shares
    mask: torch.Tensor     # areas x lists, lists that exist
    votes: torch.Tensor    # areas, predicted votes (sector turnout)
    target: torch.Tensor | None = None   # areas x lists, true shares
    weight: torch.Tensor | None = None   # areas, true votes


def panel_stats(prior: Prior, panel: pd.Series, counted: pd.DataFrame) -> dict:
    """Per sector and nationally: turnout ratio, list ratio and difference, counts."""
    counted = counted.reindex(columns=prior.lists, fill_value=0).loc[panel.index]
    votes = counted.sum(axis=1)
    q = counted.div(votes, axis=0)
    r = votes / prior.per_box[panel.index]
    p = prior.prev_shares.loc[panel.index]
    w = panel.astype(float)
    sec = prior.sector[panel.index]

    def agg(k):
        ws = w[k] / w[k].sum()
        num = q[k].mul(r[k] * ws, axis=0).sum()
        den = p[k].mul(ws, axis=0).sum()
        R = float((r[k] * ws).sum())
        diff = (q[k] - p[k]).mul(r[k] * ws, axis=0).sum() / R
        ratio = (num / den.where(den > 0)) / R
        return R, ratio, diff, num / R

    out = {"sector": {}, "n": sec.value_counts()}
    for s in prior.sectors:
        k = (sec == s).values
        out["sector"][s] = agg(k) if k.any() else None
    out["national"] = agg(np.ones(len(panel), dtype=bool))
    return out


def make_batch(prior: Prior, panel: pd.Series, counted: pd.DataFrame,
               blocs: dict[str, str], new: set[str], cur: Election | None = None) -> Batch:
    """Features, the sector model's area shares and votes for every area of `prior`."""
    st = panel_stats(prior, panel, counted)
    lists = prior.lists
    L, A = len(lists), len(prior.sector)
    p = prior.prev_shares.values                         # A x L
    sector = prior.sector.values
    R_nat, ratio_nat, diff_nat, level_nat = st["national"]
    m = prior.expected
    P = prior.prev_shares.mul(m, axis=0).groupby(prior.sector).sum()
    P = P.div(m.groupby(prior.sector).sum(), axis=0)
    R = np.empty(A)
    ratio = np.empty((A, L))
    diff = np.empty((A, L))
    level = np.empty((A, L))
    n = np.empty(A)
    for s in prior.sectors:
        k = sector == s
        got = st["sector"][s]
        Rs, rs, ds, ls = got if got is not None else st["national"]
        R[k], ratio[k], diff[k], level[k] = Rs, rs.fillna(ratio_nat).fillna(1.0).values, \
            ds.values, ls.values
        n[k] = st["n"].get(s, 0)
    Ps = P.loc[sector].values
    is_new = np.array([l in new for l in lists], dtype=float)
    use_ratio = (Ps >= RATIO_MIN) & np.isfinite(ratio)
    base = np.where(use_ratio, p * ratio, np.maximum(0, p + diff))
    base = np.where(is_new[None, :] > 0, level, base)     # new lists: the sector's level
    base = np.clip(base, 0, None)
    base = base / np.clip(base.sum(axis=1, keepdims=True), EPS, None)
    nat_share = (prior.prev_shares.mul(m, axis=0).sum() / m.sum()).values
    lb = np.array([[blocs.get(l, "other") == b for b in BLOCS] for l in lists], dtype=float)
    ab = prior.prev_blocs.reindex(columns=BLOCS, fill_value=0).values  # A x 5
    feats = [
        np.log(base + EPS), p, Ps, np.broadcast_to(nat_share, (A, L)),
        np.log(np.clip(np.nan_to_num(ratio, nan=1.0), 0.05, 20)),
        np.log(np.clip(np.nan_to_num(ratio_nat.fillna(1.0).values, nan=1.0), 0.05, 20))[None].repeat(A, 0),
        diff, np.broadcast_to(diff_nat.values, (A, L)),
        np.broadcast_to(is_new, (A, L)),
        np.log(R)[:, None].repeat(L, 1), np.full((A, L), np.log(R_nat)),
        np.log1p(n)[:, None].repeat(L, 1),
    ]
    x = np.stack(feats, axis=2)                          # A x L x 12
    x = np.concatenate([x, np.broadcast_to(lb, (A, L, 5)),
                        ab[:, None, :3].repeat(L, 1)], axis=2)   # + 5 list blocs + 3 area blocs
    assert x.shape[2] == N_FEATURES
    votes = m.values * R
    batch = Batch(torch.tensor(np.nan_to_num(x), dtype=torch.float32),
                  torch.tensor(base, dtype=torch.float32),
                  torch.ones(A, L), torch.tensor(votes, dtype=torch.float32))
    if cur is not None:
        t = cur.units.reindex(index=prior.sector.index, columns=lists, fill_value=0)
        tv = t.sum(axis=1).values
        batch.target = torch.tensor(t.div(np.clip(tv, 1, None), axis=0).values, dtype=torch.float32)
        batch.weight = torch.tensor(tv, dtype=torch.float32)
    return batch


class AreaNet(torch.nn.Module):
    def __init__(self, hidden: int = 32):
        super().__init__()
        self.mlp = torch.nn.Sequential(
            torch.nn.Linear(N_FEATURES, hidden), torch.nn.Tanh(),
            torch.nn.Linear(hidden, hidden), torch.nn.Tanh(),
            torch.nn.Linear(hidden, 1))
        torch.nn.init.zeros_(self.mlp[-1].weight)
        torch.nn.init.zeros_(self.mlp[-1].bias)    # starts as the sector model

    def forward(self, b: Batch) -> torch.Tensor:
        logits = torch.log(b.base + EPS) + self.mlp(b.x).squeeze(-1)
        return torch.softmax(logits, dim=1)


def national(net: AreaNet, b: Batch) -> np.ndarray:
    """Predicted national votes per list."""
    with torch.no_grad():
        return (net(b) * b.votes[:, None]).sum(dim=0).numpy()


def train(batches: list[Batch], epochs: int = 30, lr: float = 3e-3, weight_decay: float = 1e-3,
          national_weight: float = 1.0, seed: int = 0) -> AreaNet:
    """Fit on simulated panels of past transitions: vote-weighted cross-entropy of the
    area shares plus `national_weight` x squared error of the national shares (in
    percentage points)."""
    torch.manual_seed(seed)
    net = AreaNet()
    opt = torch.optim.Adam(net.parameters(), lr=lr, weight_decay=weight_decay)
    order = np.random.default_rng(seed)
    for _ in range(epochs):
        for i in order.permutation(len(batches)):
            b = batches[i]
            s = net(b)
            w = b.weight / b.weight.sum()
            ce = -(w[:, None] * b.target * torch.log(s + 1e-8)).sum()
            nat = (s * b.votes[:, None]).sum(0)
            nat = nat / nat.sum()
            true = (b.target * b.weight[:, None]).sum(0) / b.weight.sum()
            loss = ce + national_weight * ((100 * (nat - true)) ** 2).sum() / 100
            opt.zero_grad()
            loss.backward()
            opt.step()
    return net


def training_batches(prior: Prior, cur: Election, n_alloc: pd.Series, draw_fn,
                     panels: int, rng: np.random.Generator, new: set[str]) -> list[Batch]:
    """Simulated panels of one past transition, with the true area results."""
    out = []
    for _ in range(panels):
        panel = draw_fn(prior, n_alloc, rng)
        counted = read_boxes(cur, panel.index, rng)
        out.append(make_batch(prior, panel, counted, cur.blocs, new, cur))
    return out
