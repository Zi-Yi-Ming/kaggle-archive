# -*- coding: utf-8 -*-
"""Pre-submit seal: smoke + determinism + arity. finn never wrapped."""
from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

CAND = ROOT / "_external" / "p51_extracted2" / "kaggriculture_metacounter_r1_scored_agent.py"
FINN = ROOT / "reference_agents" / "fallow_finn.py"


def load_quiet(path, tag):
    spec = importlib.util.spec_from_file_location(tag, str(path))
    m = importlib.util.module_from_spec(spec)
    with redirect_stdout(io.StringIO()):
        spec.loader.exec_module(m)
    return m.agent if hasattr(m, "agent") else m.build_agent({})


def run_seated(us, opp, seed):
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    env.run([us, opp])
    f = env.steps[-1]
    st = [s.get("status") for s in env.steps[-1]]
    bank = float(f[0]["observation"]["farms"][0]["money"])
    return bank, st


def main():
    text = CAND.read_text(encoding="utf-8")
    print("file_sha256", hashlib.sha256(text.encode()).hexdigest())
    print("bytes", len(text.encode()))

    fn = load_quiet(CAND, "seal_alperen")
    print("arity", getattr(getattr(fn, "__code__", None), "co_argcount", None))

    # both seats seed 1, collect action hash
    keys = []
    n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)
    if n <= 1:
        def wrap(obs):
            a = fn(obs)
            keys.append(json.dumps({"m": a.get("market"), "f": a.get("farmer"), "h": a.get("hands")},
                                   sort_keys=True, default=str))
            return a
    else:
        def wrap(obs, configuration=None):
            a = fn(obs, configuration)
            keys.append(json.dumps({"m": a.get("market"), "f": a.get("farmer"), "h": a.get("hands")},
                                   sort_keys=True, default=str))
            return a

    finn = load_quiet(FINN, "seal_finn")
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.info = {"seed": 1}
    env.run([wrap, finn])
    st0 = env.steps[-1][0]["status"]
    bank0 = float(env.steps[-1][0]["observation"]["farms"][0]["money"])
    h1 = hashlib.md5("\n".join(keys).encode()).hexdigest()[:16]
    print(f"seat0 seed1 bank={bank0:.0f} status={st0} tape_hash={h1} n_steps={len(keys)}")

    # determinism: rerun
    keys2 = []
    if n <= 1:
        def wrap2(obs):
            a = fn(obs)
            keys2.append(json.dumps({"m": a.get("market"), "f": a.get("farmer"), "h": a.get("hands")},
                                    sort_keys=True, default=str))
            return a
        play = wrap2
    else:
        def wrap2(obs, configuration=None):
            a = fn(obs, configuration)
            keys2.append(json.dumps({"m": a.get("market"), "f": a.get("farmer"), "h": a.get("hands")},
                                    sort_keys=True, default=str))
            return a
        play = wrap2
    finn2 = load_quiet(FINN, "seal_finn2")
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.info = {"seed": 1}
    env.run([play, finn2])
    h2 = hashlib.md5("\n".join(keys2).encode()).hexdigest()[:16]
    bank2 = float(env.steps[-1][0]["observation"]["farms"][0]["money"])
    print(f"det_rerun bank={bank2:.0f} hash={h2} match={h1==h2 and abs(bank0-bank2)<1e-6}")

    # seat 1
    fn1 = load_quiet(CAND, "seal_alperen1")
    finn3 = load_quiet(FINN, "seal_finn3")
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.info = {"seed": 1}
    env.run([finn3, fn1])
    st1 = env.steps[-1][1]["status"]
    bank1 = float(env.steps[-1][1]["observation"]["farms"][1]["money"])
    print(f"seat1 seed1 bank={bank1:.0f} status={st1}")

    ok = (
        st0 == "DONE" and st1 == "DONE"
        and bank0 > 100000 and bank1 > 100000
        and h1 == h2
    )
    print("PRE_SUBMIT_SEAL", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
