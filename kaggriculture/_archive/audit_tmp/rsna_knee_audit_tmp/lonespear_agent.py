"""EXP-6 wrapper: run lonespear V18 (repoB HEAD, main.py == main_v18.py) as a
harness agent on engine 1.32.7. ZERO policy change: only the call signature
is adapted (kaggle_environments invokes agent(obs, config); the original
declares agent(obs)). No constants, scheduler, market policy or tape touched.
"""
import importlib.util
import os

_REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "repoB", "main.py")
_spec = importlib.util.spec_from_file_location("lonespear_v18", _REPO)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

_HUNGARIAN = getattr(_mod, "_HUNGARIAN", None)  # must be True (scipy present)


def agent(obs, config=None):
    return _mod.agent(obs)
