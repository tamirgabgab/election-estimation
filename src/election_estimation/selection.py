"""Choosing a small set of ballot boxes whose weighted shares match a target.

The estimate is a convex combination of box share vectors:
    y_hat = sum_i w_i * x_i,   w_i >= 0,   sum_i w_i = 1
and the loss is the L1 distance ||y - y_hat||_1.
"""

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, linprog, milp
from scipy.sparse import csr_matrix, hstack, identity, vstack


def l1(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.abs(np.asarray(a) - np.asarray(b)).sum())


def fit_weights(X: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, float, np.ndarray]:
    """Optimal convex weights for the columns of X (parties x boxes).

    Returns the weights, the L1 loss, and the duals of the party rows, which
    column generation uses to price boxes that are not yet selected.
    """
    m, k = X.shape
    # Variables: w (k), e_plus (m), e_minus (m).  X w - e_plus + e_minus = y.
    c = np.concatenate([np.zeros(k), np.ones(2 * m)])
    A_eq = np.block([
        [X, -np.eye(m), np.eye(m)],
        [np.ones((1, k)), np.zeros((1, 2 * m))],
    ])
    b_eq = np.concatenate([y, [1.0]])
    res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=(0, None), method="highs")
    if res.status != 0:
        raise RuntimeError(res.message)
    duals = res.eqlin.marginals
    return res.x[:k], float(res.fun), duals


def greedy_selection(
    X: np.ndarray,
    y: np.ndarray,
    max_boxes: int,
    candidates: int = 200,
    costs: np.ndarray | None = None,
    budget: float | None = None,
) -> list[dict]:
    """Forward selection guided by column generation.

    At each step the `candidates` columns with the most negative reduced cost
    under the current LP duals are each tried with a full refit, and the one
    that lowers the loss the most is added. With `costs` and `budget`, the
    shortlist and the choice use loss decrease per unit of cost, and columns
    that no longer fit in the budget are skipped.
    """
    n = X.shape[1]
    costs = np.ones(n) if costs is None else np.asarray(costs, dtype=float)
    budget = float(max_boxes) if budget is None else float(budget)
    affordable = np.flatnonzero(costs <= budget)
    assert len(affordable), "no column fits in the budget"
    dist = np.abs(X[:, affordable] - y[:, None]).sum(axis=0)
    selected = [int(affordable[np.argmin(dist)])]
    spent = costs[selected[0]]
    history = []
    w, loss, duals = fit_weights(X[:, selected], y)
    while True:
        history.append({"k": len(selected), "cost": spent, "loss": loss,
                        "boxes": list(selected), "weights": w})
        if loss < 1e-9 or len(selected) >= max_boxes:
            break
        pi, mu = duals[:-1], duals[-1]
        reduced_cost = -(pi @ X + mu) / costs
        reduced_cost[selected] = np.inf
        reduced_cost[costs > budget - spent] = np.inf
        shortlist = [j for j in np.argsort(reduced_cost)[:candidates] if np.isfinite(reduced_cost[j])]
        if not shortlist:
            break
        best = None
        for j in shortlist:
            trial = fit_weights(X[:, selected + [int(j)]], y)
            gain = (loss - trial[1]) / costs[j]
            if best is None or gain > best[0]:
                best = (gain, int(j), trial)
        selected.append(best[1])
        spent += costs[best[1]]
        w, loss, duals = best[2]
    return history


def exact_selection(
    X: np.ndarray,
    y: np.ndarray,
    k: float,
    time_limit: float = 60.0,
    costs: np.ndarray | None = None,
) -> dict:
    """Best set of columns with total cost at most k (default cost 1 each:
    at most k columns), solved as a MILP with HiGHS."""
    m, n = X.shape
    # Variables: w (n), z (n, binary), e_plus (m), e_minus (m).
    c = np.concatenate([np.zeros(2 * n), np.ones(2 * m)])
    Xs = csr_matrix(X)
    zeros_mn = csr_matrix((m, n))
    fit = hstack([Xs, zeros_mn, -identity(m), identity(m)])
    total = hstack([csr_matrix(np.ones((1, n))), csr_matrix((1, n + 2 * m))])
    link = hstack([identity(n), -identity(n), csr_matrix((n, 2 * m))])  # w_i <= z_i
    costs = np.ones(n) if costs is None else np.asarray(costs, dtype=float)
    card = hstack([csr_matrix((1, n)), csr_matrix(costs[None, :]), csr_matrix((1, 2 * m))])
    A = vstack([fit, total, link, card]).tocsr()
    lb = np.concatenate([y, [1.0], np.full(n, -np.inf), [0]])
    ub = np.concatenate([y, [1.0], np.zeros(n), [k]])
    integrality = np.concatenate([np.zeros(n), np.ones(n), np.zeros(2 * m)])
    upper = np.concatenate([np.ones(2 * n), np.full(2 * m, np.inf)])
    res = milp(
        c,
        constraints=LinearConstraint(A, lb, ub),
        integrality=integrality,
        bounds=Bounds(np.zeros(2 * n + 2 * m), upper),
        options={"time_limit": time_limit, "disp": False},
    )
    if res.x is None:
        raise RuntimeError(res.message)
    w = res.x[:n]
    boxes = np.flatnonzero(w > 1e-9)
    return {
        "k": k,
        "loss": float(res.fun),
        "boxes": boxes.tolist(),
        "weights": w[boxes],
        "optimal": res.status == 0,
        "gap": getattr(res, "mip_gap", None),
    }


def random_baseline(
    counts: np.ndarray, y: np.ndarray, k: int, trials: int = 500, seed: int = 0
) -> np.ndarray:
    """L1 loss of pooling k random boxes (counts is boxes x parties)."""
    rng = np.random.default_rng(seed)
    losses = np.empty(trials)
    for t in range(trials):
        idx = rng.choice(len(counts), size=k, replace=False)
        pooled = counts[idx].sum(axis=0)
        losses[t] = l1(pooled / pooled.sum(), y)
    return losses
