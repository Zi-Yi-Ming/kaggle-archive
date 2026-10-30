# -*- coding: utf-8 -*-
"""P50 Stage0: baseline reproduction. finn never wrapped. pin env.info seed."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

AGENTS = {
    "R2": ROOT / "_push_medal" / "main.py",
    "V16": ROOT / "_external" / "p41_extracted" / "salem_2900_main.py",
    "kaito_v27": ROOT / "_external" / "public_nb" / "kaito_v27" / "main.py",
    "qeinstein": ROOT / "_external" / "git" / "qeinstein" / "dist" / "sub-009-moev2" / "main.py",
    "rayk_rank": ROOT / "_external" / "public_nb" / "rayk_rank" / "main.py",
}
FINN_PATH = ROOT / "reference_agents" / "fallow_finn.py"
SEEDS = (1, 2, 3)


def load_agent(path, tag):
    spec = importlib.util.spec_from_file_location(tag, str(path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent if hasattr(m, "agent") else m.build_agent({})


def wrap_record(inner, keys=None):
    n = getattr(getattr(inner, "__code__", None), "co_argcount", 2)

    def _rec(a):
        if keys is not None:
            keys.append(json.dumps(
                {"m": a.get("market"), "f": a.get("farmer"), "h": a.get("hands")},
                sort_keys=True, default=str))

    if n <= 1:
        def agent(obs):
            a = inner(obs)
            _rec(a)
            return a
    else:
        def agent(obs, configuration=None):
            a = inner(obs, configuration)
            _rec(a)
            return a
    return agent


def run_game(a0, a1, seed, keys0=None):
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    p0 = wrap_record(a0, keys0) if keys0 is not None else a0
    # never wrap a1 if it might be finn; caller passes unwrapped finn
    env.run([p0, a1])
    f = env.steps[-1]
    b0 = float(f[0]["observation"]["farms"][0]["money"])
    b1 = float(f[1]["observation"]["farms"][1]["money"])
    h = hashlib.md5("\n".join(keys0).encode()).hexdigest()[:16] if keys0 else ""
    return b0, b1, h


def eval_vs_finn(name, make_fn, seeds):
    rows = []
    banks = []
    w = d = l = 0
    arity = None
    for seed in seeds:
        keys = []
        fn = make_fn()
        arity = getattr(getattr(fn, "__code__", None), "co_argcount", None)
        finn = load_agent(FINN_PATH, f"finn50_{name}_{seed}_0")
        b0, b1, h = run_game(fn, finn, seed, keys0=keys)
        finn2 = load_agent(FINN_PATH, f"finn50_{name}_{seed}_1")
        fn2 = make_fn()
        env = make("kaggriculture", debug=False)
        env.configuration["episodeSteps"] = 720
        env.info = {"seed": int(seed)}
        env.run([finn2, fn2])
        f = env.steps[-1]
        fn_s1 = float(f[1]["observation"]["farms"][1]["money"])
        finn_s0 = float(f[0]["observation"]["farms"][0]["money"])
        our = (b0 + fn_s1) / 2
        opp = (b1 + finn_s0) / 2
        banks.append(our)
        res = "W" if our > opp + 1 else ("L" if opp > our + 1 else "D")
        if res == "W":
            w += 1
        elif res == "L":
            l += 1
        else:
            d += 1
        rows.append({
            "candidate": name, "opponent": "finn", "seed": seed,
            "our_mean": our, "opp_mean": opp, "result": res,
            "us_s0": b0, "us_s1": fn_s1, "hash_s0": h,
            "agent_arity": arity, "wrapper_status": "candidate_only",
            "env_seed_source": "env.info[seed]",
        })
        print(f"  {name} vs finn s{seed}: {our:.0f} {res}", flush=True)
    return {
        "name": name, "W": w, "D": d, "L": l, "W-L": w - l,
        "bank_mean": statistics.mean(banks),
        "bank_std": statistics.pstdev(banks) if len(banks) > 1 else 0,
        "arity": arity, "rows": rows,
    }


def make_live(name):
    return lambda: load_agent(AGENTS[name], f"p50_{name}_{id(object())}")


def main():
    t0 = time.time()
    print("=== P50 STAGE0 baselines vs finn ===", flush=True)
    results = []
    all_rows = []
    for name in AGENTS:
        if not AGENTS[name].exists():
            print(f"  UNAVAILABLE {name}", flush=True)
            continue
        try:
            r = eval_vs_finn(name, make_live(name), SEEDS)
        except Exception as e:
            print(f"  FAIL {name}: {e}", flush=True)
            continue
        results.append(r)
        all_rows.extend(r["rows"])
        print(f"  => {name} W-L={r['W-L']} bank={r['bank_mean']:.0f}±{r['bank_std']:.0f} "
              f"arity={r['arity']}", flush=True)

    # historical anchors (pinned vs finn seed1 from earlier research)
    anchors = {
        "R2": 181389,
        "kaito_v27": 174341,
        "qeinstein": 162690,
        "rayk_rank": 163494,
        "V16": 169294,
    }
    print("\n=== Stage0 gate (seed1 vs historical) ===", flush=True)
    stage0_pass = True
    for r in results:
        s1 = next((x["our_mean"] for x in r["rows"] if x["seed"] == 1), None)
        hist = anchors.get(r["name"])
        if hist and s1:
            ratio = s1 / hist
            ok = 0.7 <= ratio <= 1.3
            print(f"  {r['name']}: s1={s1:.0f} hist={hist} ratio={ratio:.3f} "
                  f"{'OK' if ok else 'DRIFT'}", flush=True)
            if not ok:
                stage0_pass = False
        if r["W"] + r["D"] == 0:
            print(f"  {r['name']}: all losses vs finn — SUSPECT", flush=True)
            stage0_pass = False

    # R2 must be strong
    r2 = next((r for r in results if r["name"] == "R2"), None)
    if r2 and r2["bank_mean"] < 100000:
        print("  R2 bank_mean < 100k — Stage0 FAIL", flush=True)
        stage0_pass = False

    print(f"\nSTAGE0_PASS={stage0_pass}", flush=True)

    with open(ROOT / "p50_baselines.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        w.writeheader()
        w.writerows(all_rows)

    summary = {
        "stage0_pass": stage0_pass,
        "baselines": [
            {"name": r["name"], "W-L": r["W-L"], "bank_mean": r["bank_mean"],
             "bank_std": r["bank_std"], "arity": r["arity"]} for r in results
        ],
        "dt": time.time() - t0,
    }
    (ROOT / "p50_stage0_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("wrote p50_baselines.csv p50_stage0_summary.json", flush=True)
    return stage0_pass, results


if __name__ == "__main__":
    main()
