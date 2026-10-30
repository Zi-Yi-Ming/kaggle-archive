# -*- coding: utf-8 -*-
"""P40 Stage0+1: coupled program search. finn unwrapped. pin seed."""
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
from p40_program.compiler import compile_program, enumerate_programs, program_hash  # noqa: E402

ELITES = {
    "R2": ROOT / "_push_medal" / "main.py",
    "kaito_v27": ROOT / "_external" / "public_nb" / "kaito_v27" / "main.py",
    "qeinstein": ROOT / "_external" / "git" / "qeinstein" / "dist" / "sub-009-moev2" / "main.py",
    "rayk_rank": ROOT / "_external" / "public_nb" / "rayk_rank" / "main.py",
}


def load_mod(path, name):
    spec = importlib.util.spec_from_file_location(name, str(path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def get_agent(mod):
    if hasattr(mod, "agent"):
        return mod.agent
    return mod.build_agent({})


def load_finn():
    return load_mod(ROOT / "reference_agents" / "fallow_finn.py", "finn_p40").agent


def wrap_candidate(inner, keys):
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


def run_vs_finn(agent_fn, seed, collect_keys=False):
    finn = load_finn()
    keys = []
    play = wrap_candidate(agent_fn, keys) if collect_keys else agent_fn
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    env.run([play, finn])
    f = env.steps[-1]
    bank = float(f[0]["observation"]["farms"][0]["money"])
    shops = []
    try:
        shops = list((f[0]["observation"].get("town") or {}).get("unlocked_shops") or [])
    except Exception:
        pass
    h = hashlib.md5("\n".join(keys).encode()).hexdigest()[:16] if keys else ""
    return bank, keys, h, shops


def sim(a, b):
    n = min(len(a), len(b))
    if n == 0:
        return 0.0
    return sum(1 for i in range(n) if a[i] == b[i]) / n


def main():
    t_all = time.time()

    # Stage0: determinism
    print("=== STAGE0 determinism ===", flush=True)
    progs = enumerate_programs(limit=500)
    print(f"grid={len(progs)}", flush=True)
    p0 = progs[0]
    a1 = compile_program(p0)
    a2 = compile_program(p0)
    b1, k1, h1, _ = run_vs_finn(a1, 1, collect_keys=True)
    b2, k2, h2, _ = run_vs_finn(a2, 1, collect_keys=True)
    ok = (h1 == h2) and abs(b1 - b2) < 1e-6
    print(f"det_ok={ok} bank={b1:.0f}/{b2:.0f} hash={h1}/{h2}", flush=True)
    if not ok:
        print("STAGE0_FAIL", flush=True)
        return

    # elite tapes
    print("\n=== ELITE TAPES ===", flush=True)
    elite_keys = {}
    elite_banks = {}
    for name, path in ELITES.items():
        fn = get_agent(load_mod(path, f"p40e_{name}"))
        bank, keys, h, _ = run_vs_finn(fn, 1, collect_keys=True)
        elite_keys[name] = keys
        elite_banks[name] = bank
        print(f"elite {name}: bank={bank:.0f}", flush=True)

    r2 = get_agent(load_mod(ELITES["R2"], "p40e_R2ref"))
    r2_banks = []
    for s in (1, 2, 3):
        b, _, _, _ = run_vs_finn(r2, s)
        r2_banks.append(b)
    r2_mean = sum(r2_banks) / 3
    print(f"R2 mean3={r2_mean:.0f} {r2_banks}", flush=True)

    # Stage1 seed1
    print("\n=== STAGE1 seed1 ===", flush=True)
    stage1 = []
    best = 0.0
    for i, p in enumerate(progs):
        agent = compile_program(p)
        try:
            bank, keys, h, shops = run_vs_finn(agent, 1, collect_keys=True)
        except Exception as e:
            print(f"  [{i}] ERR {e}", flush=True)
            continue
        sims = {n: sim(keys, elite_keys[n]) for n in elite_keys}
        nearest = min(sims, key=sims.get)
        rec = {
            "prog": program_hash(p),
            "spec": json.dumps(p, sort_keys=True),
            "bank_s1": bank,
            "tape_hash": h,
            "sim_R2": sims["R2"],
            "sim_kaito": sims["kaito_v27"],
            "sim_Q": sims["qeinstein"],
            "sim_rayk": sims["rayk_rank"],
            "nearest": nearest,
            "nearest_sim": sims[nearest],
            "shops": "|".join(shops),
        }
        stage1.append(rec)
        if bank > best:
            best = bank
            print(f"  [{i}] NEWBEST {rec['prog']} bank={bank:.0f} nearest={nearest}:{sims[nearest]:.3f}", flush=True)
        elif bank >= 50000:
            print(f"  [{i}] {rec['prog']} bank={bank:.0f} nearest={nearest}:{sims[nearest]:.3f}", flush=True)
        elif (i + 1) % 50 == 0:
            print(f"  [{i}] bank={bank:.0f} best={best:.0f}", flush=True)

    stage1.sort(key=lambda r: -r["bank_s1"])
    out1 = ROOT / "p40_stage1.csv"
    with open(out1, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(stage1[0].keys()))
        w.writeheader()
        w.writerows(stage1)

    n100 = sum(1 for r in stage1 if r["bank_s1"] >= 100000)
    print(f"\nstage1 max={stage1[0]['bank_s1']:.0f} n>=100k={n100} "
          f"median={stage1[len(stage1)//2]['bank_s1']:.0f} dt={time.time()-t_all:.0f}s", flush=True)

    if n100 == 0:
        print("P40_STAGE1_FAIL — 0 candidates ≥100k. HARD STOP.", flush=True)
        return

    # Stage2 only if Stage1 has hits
    top = [r for r in stage1 if r["bank_s1"] >= 100000][:12]
    print(f"\n=== STAGE2 n={len(top)} ===", flush=True)
    stage2 = []
    for rec in top:
        p = json.loads(rec["spec"])
        banks = [rec["bank_s1"]]
        for seed in (2, 3):
            agent = compile_program(p)
            b, _, _, _ = run_vs_finn(agent, seed)
            banks.append(b)
        mean3 = sum(banks) / 3
        rec2 = dict(rec)
        rec2["bank_s2"] = banks[1]
        rec2["bank_s3"] = banks[2]
        rec2["mean3"] = mean3
        stage2.append(rec2)
        print(f"  {rec['prog']} mean3={mean3:.0f} {banks} simR2={rec['sim_R2']:.3f}", flush=True)

    stage2.sort(key=lambda r: -r["mean3"])
    out2 = ROOT / "p40_stage2.csv"
    with open(out2, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(stage2[0].keys()))
        w.writeheader()
        w.writerows(stage2)

    n120 = sum(1 for r in stage2 if r["mean3"] >= 120000 and r["nearest_sim"] < 0.8)
    print(f"stage2 n_mean3>=120k_novel={n120}", flush=True)
    print("wrote", out1.name, out2.name if n100 else "")


if __name__ == "__main__":
    main()
