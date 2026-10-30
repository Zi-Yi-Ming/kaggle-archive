"""EXP-8 V1: v11E + multi-tape / fixed route.

Tape B (recorded v11E reference game, seed 42) is LOADED but the route is
FIXED to tape A (the production _TRACE). Selector disabled. Everything else
identical to production v11E -> expected action flow == V0 byte-for-byte
(the structural control for "multi-tape presence alone").
"""
import importlib.util
import json
import os

_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
_spec = importlib.util.spec_from_file_location("v11e_prod_v1", os.path.join(_ROOT, "kaggriculture", "main.py"))
BASE = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(BASE)

with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tape_b.json"),
          encoding="utf-8") as _f:
    TAPE_B = json.load(_f)
assert len(TAPE_B) == 720

_FIXED_ROUTE = "A"  # selector disabled; route fixed to tape A


def agent(obs, config=None):
    return BASE.agent(obs, config)
