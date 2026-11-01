"""Invariants of the sector ratio model and the Knesset 27 box linking."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from election_estimation.elections import seat_rules
from election_estimation.metrics import bader_ofer
from election_estimation.sector import (MODEL, allocate, area_election, bootstrap, calibrate, draw,
                                        kmeans, make_prior, medoid_seats, predict, read_boxes)

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from match_k27_boxes import link  # noqa: E402

BASE = 26


@pytest.fixture(scope="module")
def base():
    """K26 as both the previous election and the panel source (the site's setup)."""
    prev = area_election(BASE)
    settlement = prev.boxes.groupby("unit")["settlement"].agg(lambda s: s.mode().iloc[0])
    prior = make_prior(prev, prev.unit_boxes, settlement, prev.parties,
                       {l: l for l in prev.parties}, sectors=MODEL["sectors"], k=MODEL["k"])
    return prev, prior


def census(prev, prior):
    """Every area read through its mean box."""
    return prior.expected, prev.units.div(prev.unit_boxes, axis=0).loc[prior.expected.index]


@pytest.mark.parametrize("estimator", ["difference", "ratio", "greg", "greg_ratio"])
def test_census_of_the_previous_election_gives_it_back(base, estimator):
    prev, prior = base
    panel, counted = census(prev, prior)
    pred = predict(prior, panel, counted, estimator=estimator)
    pred = pred / pred.sum()
    assert np.allclose(pred.values, prev.shares.reindex(pred.index).values, atol=1e-9)


def test_by_sector_sums_to_national(base):
    prev, prior = base
    panel, counted = census(prev, prior)
    by_s = predict(prior, panel, counted, by_sector=True, estimator="ratio")
    assert set(by_s.index) == set(prior.sectors)
    assert np.allclose(by_s.sum().values, predict(prior, panel, counted, estimator="ratio").values)


def test_draw_takes_the_allocated_areas_and_offsets_barely_overlap(base):
    prev, prior = base
    train = [area_election(k) for k in range(19, BASE + 1)]
    n = allocate(prior, train, 0.02, spread=MODEL["spread"])
    assert (n >= 3).all()
    panels = [draw(prior, n, np.random.default_rng(1), offset=j / 3) for j in range(3)]
    for p in panels:
        got = p.groupby(prior.sector[p.index]).sum()
        assert (got.reindex(n.index) == n).all()
    ids = [set(p.index) for p in panels]
    assert len(ids[0] & ids[1]) / len(ids[0]) < 0.3


def test_read_boxes_mean_of_two(base):
    prev, _ = base
    areas = prev.unit_boxes[prev.unit_boxes >= 2].index[:20]
    rng = np.random.default_rng(0)
    one = read_boxes(prev, areas, rng)
    two = read_boxes(prev, areas, rng, boxes=2)
    assert list(one.index) == list(areas) and set(two.index) == set(areas)
    lo = prev.boxes.groupby("unit")[prev.parties].min().loc[areas]
    hi = prev.boxes.groupby("unit")[prev.parties].max().loc[areas]
    assert ((two.loc[areas] >= lo - 1e-9) & (two.loc[areas] <= hi + 1e-9)).all().all()


def test_calibrate_reaches_the_target_with_a_small_ridge():
    rng = np.random.default_rng(0)
    x = rng.dirichlet(np.ones(4), size=60)
    w0 = np.full(60, 1 / 60)
    target = x.mean(axis=0) * 0.9 + np.array([0.1, 0, 0, 0])
    w = calibrate(w0, x, target, mu=1e-9)
    assert abs(w.sum() - 1) < 1e-9 and (w >= 0).all()
    assert np.allclose(w @ x, target, atol=1e-3)
    assert np.allclose(calibrate(w0, x, w0 @ x, mu=1.0), w0)   # already calibrated


def test_kmeans_is_deterministic():
    rng = np.random.default_rng(0)
    x = np.vstack([rng.normal(0, 0.1, (30, 2)), rng.normal(3, 0.1, (30, 2))])
    w = np.ones(60)
    a, b = kmeans(x, w, 2), kmeans(x, w, 2)
    assert (a == b).all() and len(set(a[:30])) == 1 and a[0] != a[-1]


def test_bootstrap_and_medoid(base):
    prev, prior = base
    train = [area_election(k) for k in range(19, BASE + 1)]
    n = allocate(prior, train, 0.01, spread=MODEL["spread"])
    rng = np.random.default_rng(2)
    panel = draw(prior, n, rng)
    reps = bootstrap(prior, panel, read_boxes(prev, panel.index, rng), rng, reps=20,
                     estimator=MODEL["estimator"])
    assert reps.shape == (20, len(prior.lists)) and (reps.values >= 0).all()
    seats = pd.DataFrame([bader_ofer(r / r.sum(), **seat_rules(BASE)) for _, r in reps.iterrows()])
    m = medoid_seats(seats)
    assert m.sum() == 120 and any((seats == m).all(axis=1))
    same = pd.DataFrame([seats.iloc[0]] * 5)
    assert (medoid_seats(same) == seats.iloc[0]).all()


def test_link_prefers_the_ballot_number_then_the_center():
    ref = pd.DataFrame({"settlement_code": ["1", "1", "1", "1", "2"],
                        "ballot_id": ["1", "2", "3", "4", "1"],
                        "concentration": ["10", "10", "11", "10", "5"],
                        "area_id": ["a", "b", "c", "a", "d"]})
    new = pd.DataFrame({"settlement_code": ["1", "1", "1", "3"], "ballot_id": ["2", "9", "8", "1"],
                        "concentration": ["11", "10", "12", "1"]})
    out = link(new, ref)
    assert list(out["area_id"]) == ["b", "a", "loc:1", "loc:3"]
    assert list(out["method"]) == ["ballot", "center", "settlement", "settlement"]
