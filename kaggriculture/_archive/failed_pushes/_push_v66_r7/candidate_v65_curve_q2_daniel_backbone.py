# Modified by mohui666 in 2026; see NOTICE for the change summary.
"""Local probe: Curve q2 repairs plus strict Daniel step-72 backbone split."""

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


_Q2 = _load(
    "_v65_curve_q2_daniel_base", "candidate_v65_curve_q2_known_yarn_repair.py"
)
_BASE = _Q2._BASE
_BACKBONE = _BASE._v51_build_policy(_BASE._V56_BACKBONE_ROUTE, _BASE._V54_CONFIG)
_DANIEL_STEP72 = (("SMOOTHIE_SHOP",),) + _Q2._CURVE_Q2_REPAIR_STEP72[1:]
_STATE = {
    0: {"last": -1, "daniel": False},
    1: {"last": -1, "daniel": False},
}


__version__ = "local-v65-curve-q2-repairs-daniel-backbone72"


def kaggle_agent_v65_curve_q2_daniel_backbone(obs, configuration=None):
    selected = _Q2.kaggle_agent_v65_curve_q2_known_yarn_repair(obs, configuration)
    visible = _BASE._v56_visible_configuration(configuration)
    backbone = _BACKBONE(obs, visible)
    step = _BASE._v59_step(obs)
    seat = _BASE._v58_seat(obs)
    state = _STATE[seat]
    if step == 0 or step <= int(state.get("last", -1)):
        state = {"last": step, "daniel": False}
        _STATE[seat] = state
    else:
        state["last"] = step
    curve_active = bool(_Q2._V65._CURVE_STATE[seat].get("active"))
    if step == 72 and curve_active:
        state["daniel"] = _Q2._public_signature(obs) == _DANIEL_STEP72
    if not state["daniel"]:
        return selected
    action = _BASE._v60_seed_trim(obs, backbone, step)
    capacity = _BASE._v60_int((configuration or {}).get("shedCapacity", 100)) or 100
    action = _BASE._v60_shed_guard(obs, action, capacity)
    if step == 718:
        action = _Q2._V65._curve_liquidate(obs, action)
    return action


kaggle_agent_v65_curve_q2_daniel_backbone.audit_state = _STATE
kaggle_submission_agent = kaggle_agent_v65_curve_q2_daniel_backbone
agent = kaggle_agent_v65_curve_q2_daniel_backbone
