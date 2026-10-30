# -*- coding: utf-8 -*-
"""Seal farm_v4 before submit."""
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

SRC = ROOT / "_external" / "p62c_main" / "farming_score_v4_a_better_shop.py"
FINN = ROOT / "reference_agents" / "fallow_finn.py"


def load_quiet(path, tag):
    spec = importlib.util.spec_from_file_location(tag, str(path))
    m = importlib.util.module_from_spec(spec)
    with redirect_stdout(io.StringIO()):
        spec.loader.exec_module(m)
    return m.agent if hasattr(m, "agent") else m.build_agent({})


def main():
    text = SRC.read_bytes()
    print("bytes", len(text))
    print("sha256", hashlib.sha256(text).hexdigest())
    fn = load_quiet(SRC, "seal_fv")
    print("arity", getattr(getattr(fn, "__code__", None), "co_argcount", None))

    keys = []

    def wrap(obs, configuration=None):
        a = fn(obs, configuration)
        keys.append(json.dumps({"m": a.get("market"), "f": a.get("farmer"), "h": a.get("hands")},
                               sort_keys=True, default=str))
        return a

    finn = load_quiet(FINN, "seal_fn")
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.info = {"seed": 1}
    env.run([wrap, finn])
    st0 = env.steps[-1][0]["status"]
    bank0 = float(env.steps[-1][0]["observation"]["farms"][0]["money"])
    h1 = hashlib.md5("\n".join(keys).encode()).hexdigest()[:16]
    print(f"seat0 s1 bank={bank0:.0f} status={st0} hash={h1} n={len(keys)}")

    keys2 = []

    def wrap2(obs, configuration=None):
        a = fn(obs, configuration)
        keys2.append(json.dumps({"m": a.get("market"), "f": a.get("farmer"), "h": a.get("hands")},
                                sort_keys=True, default=str))
        return a

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.info = {"seed": 1}
    env.run([wrap2, load_quiet(FINN, "seal_fn2")])
    h2 = hashlib.md5("\n".join(keys2).encode()).hexdigest()[:16]
    bank2 = float(env.steps[-1][0]["observation"]["farms"][0]["money"])
    det = h1 == h2 and abs(bank0 - bank2) < 1e-6
    print(f"det match={det} hash2={h2}")

    fn1 = load_quiet(SRC, "seal_fv1")
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.info = {"seed": 1}
    env.run([load_quiet(FINN, "seal_fn3"), fn1])
    st1 = env.steps[-1][1]["status"]
    bank1 = float(env.steps[-1][1]["observation"]["farms"][1]["money"])
    print(f"seat1 s1 bank={bank1:.0f} status={st1}")

    ok = st0 == "DONE" and st1 == "DONE" and det and bank0 > 100000 and bank1 > 100000
    print("SEAL", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
