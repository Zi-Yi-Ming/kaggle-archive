# -*- coding: utf-8 -*-
"""Eval extracted external agents: bank + similarity vs known elites."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import sys
import time
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

EXT = ROOT / "_external" / "p41_extracted"
CANDS = {
    "salem_2900": EXT / "salem_2900_main.py",
    "boatlee_v16": EXT / "boatlee_v16_main.py",
    "flexon_route": EXT / "flexon_route.py",
}
ELITES = {
    "R2": ROOT / "_push_medal" / "main.py",
    "kaito_v27": ROOT / "_external" / "public_nb" / "kaito_v27" / "main.py",
    "qeinstein": ROOT / "_external" / "git" / "qeinstein" / "dist" / "sub-009-moev2" / "main.py",
    "rayk_rank": ROOT / "_external" / "public_nb" / "rayk_rank" / "main.py",
}


def load_agent(path: Path, tag: str):
    spec = importlib.util.spec_from_file_location(tag, str(path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    if hasattr(m, "agent"):
        return m.agent
    if hasattr(m, "build_agent"):
        return m.build_agent({})
    raise RuntimeError(f"no agent {path}")


def load_finn():
    return load_agent(ROOT / "reference_agents" / "fallow_finn.py", "finn_p41b")


def wrap(inner, keys):
    n = getattr(getattr(inner, "__code__", None), "co_argcount", 2)
    if n <= 1:
        def agent(obs):
            a = inner(obs)
            keys.append(json.dumps({"m": a.get("market"), "f": a.get("farmer"), "h": a.get("hands")},
                                   sort_keys=True, default=str))
            return a
    else:
        def agent(obs, configuration=None):
            a = inner(obs, configuration)
            keys.append(json.dumps({"m": a.get("market"), "f": a.get("farmer"), "h": a.get("hands")},
                                   sort_keys=True, default=str))
            return a
    return agent


def run(fn, seed, collect=False):
    finn = load_finn()
    keys = []
    play = wrap(fn, keys) if collect else fn
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    env.run([play, finn])
    bank = float(env.steps[-1][0]["observation"]["farms"][0]["money"])
    h = hashlib.md5("\n".join(keys).encode()).hexdigest()[:16] if keys else ""
    return bank, keys, h


def sim(a, b):
    n = min(len(a), len(b))
    if n == 0:
        return 0.0
    return sum(1 for i in range(n) if a[i] == b[i]) / n


def main():
    t0 = time.time()
    elite_keys = {}
    print("=== ELITES ===", flush=True)
    for name, path in ELITES.items():
        fn = load_agent(path, f"e_{name}")
        bank, keys, h = run(fn, 1, collect=True)
        elite_keys[name] = keys
        print(f"  {name}: {bank:.0f}", flush=True)

    rows = []
    print("\n=== EXTERNAL ===", flush=True)
    for name, path in CANDS.items():
        if not path.exists():
            print(f"  missing {name}", flush=True)
            continue
        try:
            fn = load_agent(path, f"c_{name}")
        except Exception as e:
            print(f"  LOAD {name}: {e}", flush=True)
            rows.append({"name": name, "status": "load_fail", "error": str(e)[:180]})
            continue
        try:
            bank, keys, h = run(fn, 1, collect=True)
        except Exception as e:
            print(f"  RUN {name}: {e}", flush=True)
            rows.append({"name": name, "status": "run_fail", "error": str(e)[:180]})
            continue
        sims = {n: sim(keys, elite_keys[n]) for n in elite_keys}
        nearest = min(sims, key=sims.get)
        rec = {
            "name": name, "status": "ok", "bank_s1": bank, "tape_hash": h,
            "nearest": nearest, "nearest_sim": sims[nearest],
            "sim_R2": sims["R2"], "sim_kaito": sims["kaito_v27"],
            "sim_Q": sims["qeinstein"], "sim_rayk": sims["rayk_rank"],
            "error": "",
        }
        # multi-seed if strong
        if bank >= 80000:
            banks = [bank]
            for s in (2, 3):
                b, _, _ = run(fn, s)
                banks.append(b)
            rec["bank_s2"], rec["bank_s3"] = banks[1], banks[2]
            rec["mean3"] = sum(banks) / 3
        rows.append(rec)
        m3 = rec.get("mean3")
        print(f"  {name:16s} s1={bank:8.0f} mean3={m3 if m3 is None else round(m3)} "
              f"nearest={nearest}:{sims[nearest]:.3f}", flush=True)

    out = ROOT / "p41_external_eval.csv"
    fields = sorted({k for r in rows for k in r})
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print("wrote", out.name, f"dt={time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
