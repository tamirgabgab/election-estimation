"""Where does the sector model's error come from? Held-out K22-K26, 2% budget.

For every test election:
- census: every area read in full (weights = expected votes), the model's own
  bias with no sampling;
- area_mean: the drawn panels read through the mean box of each area (no
  single-box noise);
- single_box: the drawn panels read through one random box (as on election
  night);
- bias: the seats moved of the mean prediction over the single-box draws.
Also the share of the single-box squared error (in seat units) each sector and
each list carries.

Writes reports/sector_diagnosis.md.

Usage:
    PYTHONPATH=src python scripts/diagnose_sector.py [draws] [tests...]
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from election_estimation.data import load_parties
from election_estimation.evaluate import score
from election_estimation.sector import allocate, area_election, draw, predict, prior_for, read_boxes

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "sector_diagnosis.md"
BUDGET = 0.02
SEED = 3


def truth_by_sector(prior, cur) -> pd.DataFrame:
    return cur.units.reindex(columns=prior.lists, fill_value=0).groupby(prior.sector).sum()


def run(t: int, draws: int) -> tuple[dict, pd.Series, pd.Series]:
    train = [area_election(k) for k in range(19, t)]
    cur = area_election(t)
    prior = prior_for(train[-1], cur)
    mean_box = cur.units.div(cur.unit_boxes, axis=0)
    census = predict(prior, prior.expected, mean_box.loc[prior.expected.index])
    n = allocate(prior, train, BUDGET)
    rng = np.random.default_rng(SEED + t)
    true_s = truth_by_sector(prior, cur)
    total = true_s.values.sum()
    single, area, preds, err_sector, err_list = [], [], [], [], []
    for _ in range(draws):
        panel = draw(prior, n, rng)
        by_s = predict(prior, panel, read_boxes(cur, panel.index, rng), by_sector=True)
        pred = by_s.sum()
        single.append(score(pred, cur)["seats_moved"])
        area.append(score(predict(prior, panel, mean_box.loc[panel.index]), cur)["seats_moved"])
        preds.append(pred / pred.sum())
        e = (by_s / by_s.values.sum() - true_s.reindex(by_s.index) / total) * 120
        err_sector.append((e ** 2).sum(axis=1))
        err_list.append(((pred / pred.sum() - cur.shares.reindex(prior.lists)) * 120) ** 2)
    mean_pred = pd.concat(preds, axis=1).mean(axis=1)
    row = {"test": t, "census": score(census, cur)["seats_moved"],
           "bias": score(mean_pred, cur)["seats_moved"],
           "area_mean": float(np.mean(area)), "single_box": float(np.mean(single)),
           "within_2": float(np.mean(np.array(single) <= 2))}
    names = load_parties(t)["name_he"]
    lists = pd.concat(err_list, axis=1).mean(axis=1)
    lists.index = [f"{names.get(l, l)} ({t})" for l in lists.index]
    return row, pd.concat(err_sector, axis=1).mean(axis=1), lists


def main(draws: int, tests: list[int]) -> None:
    rows, sectors, lists = [], [], []
    for t in tests:
        r, s, l = run(t, draws)
        rows.append(r), sectors.append(s.rename(t)), lists.append(l)
        print(r, flush=True)
    r = pd.DataFrame(rows).set_index("test")
    s = pd.concat(sectors, axis=1).fillna(0)
    s_share = (s.sum(axis=1) / s.values.sum()).sort_values(ascending=False)
    l = pd.concat(lists).sort_values(ascending=False)
    l_share = (l / l.sum()).head(12)
    text = "\n".join([
        "# Sector model: where the error comes from (held-out, 2% budget)", "",
        f"`scripts/diagnose_sector.py`, {draws} panels per test, seed {SEED}+t. Seats moved of: "
        "`census` (every area read in full: the model's bias without sampling), `bias` (the mean "
        "prediction over the panels), `area_mean` (the panels read through each area's mean box: "
        "no single-box noise) and `single_box` (election night). `within_2`: share of panels "
        "within 2 seats.", "",
        r.round(2).to_markdown(), "", f"Mean: {r.mean().round(2).to_dict()}", "",
        "## Share of the squared error (seat units) by sector", "",
        s_share.round(3).to_frame("share").to_markdown(), "",
        "## Lists with the largest share of the squared error", "",
        l_share.round(3).to_frame("share").to_markdown(), ""])
    OUT.write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    args = [int(a) for a in sys.argv[1:]]
    main(args[0] if args else 50, args[1:] or [22, 23, 24, 25, 26])
