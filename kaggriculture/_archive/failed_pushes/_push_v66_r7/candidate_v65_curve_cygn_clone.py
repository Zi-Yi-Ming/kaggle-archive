# Modified by mohui666 in 2026; see NOTICE for the change summary.
"""Local v65 probe: Curve-q1 plus a YARN/PIZZA cygn clone-route split."""

from __future__ import annotations

import importlib.util
from pathlib import Path


_SOURCE_FILE = globals().get("__file__")
_HERE = (
    Path(_SOURCE_FILE).resolve().parent
    if _SOURCE_FILE
    else Path.cwd() / "reference" / "live_meta"
)


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, _HERE / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_V65 = _load("_v65_cygn_base", "candidate_v65_local_combined.py")
_BASE = _V65._BASE
_CLONE = _BASE._v51_build_policy(_BASE._V58_CLONE_ROUTE, _BASE._V54_CONFIG)
_CYGN_SHOPS = ("YARN_STORE", "PIZZA_SHOP")


__version__ = "local-v65-curve-cygn-clone-step144"


def kaggle_agent_v65_curve_cygn_clone(obs, configuration=None):
    selected = _V65.kaggle_agent_v65_local_combined(obs, configuration)
    visible = _BASE._v56_visible_configuration(configuration)
    clone_action = _CLONE(obs, visible)
    step = _BASE._v59_step(obs)
    seat = _BASE._v58_seat(obs)
    shops = tuple(_BASE._v58_shops(obs)[:2])
    curve_active = bool(_V65._CURVE_STATE[seat].get("active"))
    if not (curve_active and step >= 144 and shops == _CYGN_SHOPS):
        return selected
    action = _BASE._v60_seed_trim(obs, clone_action, step)
    capacity = _BASE._v60_int((configuration or {}).get("shedCapacity", 100)) or 100
    return _BASE._v60_shed_guard(obs, action, capacity)


kaggle_submission_agent = kaggle_agent_v65_curve_cygn_clone
agent = kaggle_agent_v65_curve_cygn_clone
