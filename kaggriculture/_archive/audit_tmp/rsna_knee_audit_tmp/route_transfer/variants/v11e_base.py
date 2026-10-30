"""EXP-8 V0: v11E baseline — production v11E unchanged, single tape.
agent(obs, config) delegates to the production agent with zero modification.
"""
import importlib.util
import os

_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
_spec = importlib.util.spec_from_file_location("v11e_prod_v0", os.path.join(_ROOT, "kaggriculture", "main.py"))
BASE = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(BASE)


def agent(obs, config=None):
    return BASE.agent(obs, config)
