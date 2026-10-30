"""EXP-8 V2: v11E + multi-tape + route selector (per ROUTE_SPEC).

At step 0 of each game, decide route = route_for(obs) (pure function of
obs.town.unlocked_shops, ROUTE_SPEC section 4) per seat, LOCKED for the
whole game. If route == "B", swap the tape source BASE._TRACE = TAPE_B;
else keep the production tape A. Nothing else changes (no COK content).
Deterministic: route_for is a pure function of the seed-determined obs.
"""
import importlib.util
import json
import os

_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
_spec = importlib.util.spec_from_file_location("v11e_prod_v2", os.path.join(_ROOT, "kaggriculture", "main.py"))
BASE = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(BASE)

TAPE_A = BASE._TRACE  # production tape (original reference, never mutated)
with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tape_b.json"),
          encoding="utf-8") as _f:
    TAPE_B = json.load(_f)
assert len(TAPE_B) == 720 and len(TAPE_A) == 720

_LOCK = {0: None, 1: None}


def route_for(obs):
    """Pure function (ROUTE_SPEC section 4): unlocked_shops hash -> A/B."""
    shops = (obs.get("town") or {}).get("unlocked_shops", None)
    if not isinstance(shops, (list, tuple)) or len(shops) == 0:
        return "A"
    key = "|".join(sorted(str(s) for s in shops))
    h = 0
    for ch in key:
        h = (h * 31 + ord(ch)) & 0x7FFFFFFF
    return "A" if (h % 2) == 0 else "B"


def agent(obs, config=None):
    seat = int(obs.get("player", 0) or 0)
    step = int(obs.get("step", 0) or 0)
    if step == 0:
        _LOCK[seat] = None  # reset per game (undecided)
    if _LOCK[seat] is None:
        shops = (obs.get("town") or {}).get("unlocked_shops", None)
        if isinstance(shops, (list, tuple)) and len(shops) > 0:
            # first non-empty signature step (empirically step 72, day 3):
            # decide once and lock for the game (ROUTE_SPEC v2)
            _LOCK[seat] = route_for(obs)
    route = _LOCK[seat] if _LOCK[seat] is not None else "A"  # pre-signature steps run tape A
    if route == "B":
        BASE._TRACE = TAPE_B
    else:
        BASE._TRACE = TAPE_A
    return BASE.agent(obs, config)
