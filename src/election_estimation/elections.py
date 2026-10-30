"""Per-election configuration (threshold, seats, surplus agreements).

The single source of truth is `ELECTIONS` in `scripts/build_data.py`; this
module loads it so modelling code uses the same values as the data build.
"""

import importlib.util
from functools import cache

from election_estimation.data import ROOT


@cache
def elections() -> dict[int, dict]:
    path = ROOT / "scripts" / "build_data.py"
    spec = importlib.util.spec_from_file_location("build_data", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.ELECTIONS


def seat_rules(knesset: int) -> dict:
    """Keyword arguments for `metrics.bader_ofer` in this election."""
    config = elections()[knesset]
    return {
        "threshold": config["threshold"],
        "total": config["seats"],
        "agreements": list(config["surplus_agreements"]),
    }
