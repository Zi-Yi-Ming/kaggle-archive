# -*- coding: utf-8 -*-
"""Local gate: strong candidates vs R2, 8 seeds both seats."""
from __future__ import annotations

import csv
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

EXT = ROOT / "_external" / "p51_extracted2"
CANDS = {
    "guru_dynamic": EXT / "kaggriculture_fully_dynamic_autonomous_agent.py",
    "alperen_meta": EXT / "kaggriculture_metacounter_r1_scored_agent.py",
    "lime_smart": EXT / "score2710_t23_kaggriculture_smart_harvest.py",
}
R2 = ROOT / "_push_medal" / "main.py"
SEEDS = (1, 2, 3, 4, 5, 11, 12, 13)


def load_quiet(path, tag):
    spec = importlib.util.spec_from_file_location(tag, str(path))
    m = importlib.util.module_from_spec(spec)
    with redirect_stdout(io.StringIO()):
        spec.loader.exec_module(m)
    return m.agent if hasattr(m, "agent") else m.build_agent({})


def run(a0, a1, seed, keys0=None):
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    p0 = a0
    if keys0 is not None:
        n = getattr(getattr(a0, "__code__", None), "co_argcount", 2)

        if n <= 1:
            def p0(obs):
                a = a0(obs)
                keys0.append(json.dumps({"m": a.get("market"), "f": a.get("farmer"), "h": a.get("hands")},
                                        sort_keys=True, default=str))
                return a
        else:
            def p0(obs, configuration=None):
                a = a0(obs, configuration)
                keys0.append(json.dumps({"m": a.get("market"), "f": a.get("farmer"), "h": a.get("hands")},
                                        sort_keys=True, default=str))
                return a
    env.run([p0, a1])
    f = env.steps[-1]
    return (
        float(f[0]["observation"]["farms"][0]["money"]),
        float(f[1]["observation"]["farms"][1]["money"]),
    )


def main():
    r2 = load_quiet(R2, "r2_gate")
    # tape hash of candidates on seed1
    hashes = {}
    for name, path in CANDS.items():
        keys = []
        fn = load_quiet(path, f"g_{name}")
        b0, b1 = run(fn, r2, 1, keys0=keys)
        h = hashlib.md5("\n".join(keys).encode()).hexdigest()[:16]
        hashes[name] = (h, b0, b1)
        print(f"hash {name} s1 us={b0:.0f} r2={b1:.0f} hash={h}", flush=True)

    print("\npairwise hash equal?", flush=True)
    names = list(hashes)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            same = hashes[names[i]][0] == hashes[names[j]][0]
            print(f"  {names[i]} vs {names[j]}: same_tape={same}", flush=True)

    rows = []
    print("\n=== 8-seed gate ===", flush=True)
    for name, path in CANDS.items():
        fn = load_quiet(path, f"gate_{name}")
        w = d = l = 0
        banks = []
        for seed in SEEDS:
            a0, a1 = run(fn, r2, seed)
            b0, b1 = run(r2, fn, seed)
            our = (a0 + b1) / 2
            theirs = (a1 + b0) / 2
            banks.append(our)
            if our > theirs + 1:
                w += 1
                res = "W"
            elif theirs > our + 1:
                l += 1
                res = "L"
            else:
                d += 1
                res = "D"
            print(f"  {name} s{seed}: us={our:.0f} r2={theirs:.0f} {res}", flush=True)
            rows.append({"name": name, "seed": seed, "our": our, "r2": theirs, "res": res})
        print(f"{name}: W-T-L {w}-{d}-{l} bank_mean={sum(banks)/len(banks):.0f} "
              f"gate={'PASS' if w>=5 else 'FAIL'}", flush=True)

    with open(ROOT / "p51_local_gate.csv", "w", newline="", encoding="utf-8") as f:
        wri = csv.DictWriter(f, fieldnames=["name", "seed", "our", "r2", "res"])
        wri.writeheader()
        wri.writerows(rows)
    print("wrote p51_local_gate.csv", flush=True)


if __name__ == "__main__":
    main()
