"""EXP-6 wrapper: run Seyamalam V18S (repoA HEAD, main.py L4889 active agent =
_V18S_BASE_AGENT + _v18s_recovery_sweep) as a harness agent on engine 1.32.7.
ZERO policy change: only the call signature is adapted (env invokes
agent(obs, config); the original declares agent(obs)). No constants,
scheduler, market policy or embedded corpus touched.
"""
import importlib.util
import os

_REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "repoA", "main.py")
_spec = importlib.util.spec_from_file_location("seyamalam_v18s", _REPO)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

# sanity: the effective binding must be the last agent() def (L4889)
assert _mod.agent.__code__.co_firstlineno >= 4800, "agent binding mismatch"


def agent(obs, config=None):
    return _mod.agent(obs)
