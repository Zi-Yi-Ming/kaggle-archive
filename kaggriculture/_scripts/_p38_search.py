# -*- coding: utf-8 -*-
"""P38 v2 staged search. Pin seed. NEVER wrap finn (arity artifact)."""
from __future__ import annotations

import csv
import importlib.util
import json
import sys
import time
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402
from p38_program.compiler import compile_program, program_hash  # noqa: E402

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
    return load_mod(ROOT / "reference_agents" / "fallow_finn.py", "finn_p38v2").agent


def wrap_candidate(inner, keys):
    """Wrap OUR agent only. Match arity so kaggle-env doesn't break the call."""
    n = getattr(getattr(inner, "__code__", None), "co_argcount", 2)

    if n <= 1:
        def agent(obs):
            a = inner(obs)
            keys.append(json.dumps(
                {"m": a.get("market"), "f": a.get("farmer"), "h": a.get("hands")},
                sort_keys=True, default=str,
            ))
            return a
    else:
        def agent(obs, configuration=None):
            a = inner(obs, configuration)
            keys.append(json.dumps(
                {"m": a.get("market"), "f": a.get("farmer"), "h": a.get("hands")},
                sort_keys=True, default=str,
            ))
            return a
    return agent


def run_vs_finn(agent_fn, seed, collect_keys=False):
    """Pinned harness matching P32/P37: finn UNWRAPPED, only candidate wrapped."""
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
    import hashlib
    h = hashlib.md5("\n".join(keys).encode()).hexdigest()[:16] if keys else ""
    return bank, keys, h


def sim(a, b):
    n = min(len(a), len(b))
    if n == 0:
        return 0.0
    return sum(1 for i in range(n) if a[i] == b[i]) / n


def setup_b():
    import p13_1_melon, p13_3_water, p14_1_on, p14_2_on, p16_branch, p17_1_library, p18_selector
    p13_1_melon.set_enabled(False)
    p13_3_water.set_enabled(True)
    p14_1_on.set_enabled(True)
    p14_2_on.set_enabled(False)
    p16_branch.set_branch_mode("off")
    p17_1_library.set_enabled(False)
    p18_selector.set_selector("S0")
    from p11_planner import planner as pmod
    pmod._PLANNER = None


def main():
    t_all = time.time()
    setup_b()

    # elite tapes seed1 for novelty
    elite_keys = {}
    elite_banks = {}
    for name, path in ELITES.items():
        fn = get_agent(load_mod(path, f"p38e2_{name}"))
        bank, keys, h = run_vs_finn(fn, 1, collect_keys=True)
        elite_keys[name] = keys
        elite_banks[name] = bank
        print(f"elite {name}: bank={bank:.0f} hash={h}", flush=True)

    # also re-eval R2 mean on seeds 1,2,3 for Level-4 reference
    r2 = get_agent(load_mod(ELITES["R2"], "p38e2_R2ref"))
    r2_banks = []
    for s in (1, 2, 3):
        b, _, _ = run_vs_finn(r2, s)
        r2_banks.append(b)
    r2_mean = sum(r2_banks) / 3
    print(f"R2 mean3={r2_mean:.0f} banks={r2_banks}", flush=True)

    from p38_program.compiler import enumerate_programs
    progs = enumerate_programs()
    print(f"grid size={len(progs)}", flush=True)

    # p11 baseline (same worker substrate)
    setup_b()
    from p11_planner import planner as pmod
    pmod._PLANNER = None
    pl = pmod.StrategicPlanner()

    def p11_agent(obs, configuration=None):
        return pl.act(obs)

    b_p11, _, _ = run_vs_finn(p11_agent, 1)
    print(f"p11_baseline_s1={b_p11:.0f}", flush=True)

    # Stage1: seed 1
    stage1 = []
    for i, p in enumerate(progs):
        setup_b()
        agent = compile_program(p)
        try:
            bank, keys, h = run_vs_finn(agent, 1, collect_keys=True)
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
        }
        stage1.append(rec)
        if (i + 1) % 10 == 0 or bank >= 80000:
            print(f"  [{i}] {rec['prog']} bank={bank:.0f} nearest={nearest}:{sims[nearest]:.3f}", flush=True)

    stage1.sort(key=lambda r: -r["bank_s1"])
    out1 = ROOT / "p38_stage1.csv"
    with open(out1, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(stage1[0].keys()))
        w.writeheader()
        w.writerows(stage1)
    print(f"stage1 best={stage1[0]['bank_s1']:.0f} median={stage1[len(stage1)//2]['bank_s1']:.0f} "
          f"wrote {out1.name} dt={time.time()-t_all:.0f}s", flush=True)

    # Stage2: top 12, seeds 2,3
    top = stage1[:12]
    print("\n=== STAGE2 top12 ===", flush=True)
    stage2 = []
    for rec in top:
        p = json.loads(rec["spec"])
        banks = []
        for seed in (2, 3):
            setup_b()
            agent = compile_program(p)
            b, _, _ = run_vs_finn(agent, seed)
            banks.append(b)
        mean3 = (rec["bank_s1"] + banks[0] + banks[1]) / 3
        rec2 = dict(rec)
        rec2["bank_s2"] = banks[0]
        rec2["bank_s3"] = banks[1]
        rec2["mean3"] = mean3
        stage2.append(rec2)
        print(f"  {rec['prog']}: s1={rec['bank_s1']:.0f} s2={banks[0]:.0f} s3={banks[1]:.0f} "
              f"mean={mean3:.0f} simR2={rec['sim_R2']:.3f}", flush=True)

    stage2.sort(key=lambda r: -r["mean3"])
    out2 = ROOT / "p38_stage2.csv"
    with open(out2, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(stage2[0].keys()))
        w.writeheader()
        w.writerows(stage2)

    print("\n=== DISCOVERY CRITERIA ===", flush=True)
    print(f"R2_mean3_reference={r2_mean:.0f}", flush=True)
    for r in stage2:
        novelty = r["nearest_sim"] < 0.5
        lvl = (
            "L4_ge_R2" if r["mean3"] >= r2_mean * 0.97 else
            "L3_160k" if r["mean3"] >= 160000 else
            "L2_150k" if r["mean3"] >= 150000 else
            "L1_100k" if r["mean3"] >= 100000 else
            "BELOW"
        )
        flag = "NEW" if novelty and r["mean3"] >= 100000 else ("REHASH" if not novelty else "weak")
        print(f"  {r['prog']} mean={r['mean3']:.0f} {lvl} {flag} "
              f"nearest={r['nearest']}:{r['nearest_sim']:.3f}", flush=True)

    print("wrote", out1.name, out2.name, f"total_dt={time.time()-t_all:.0f}s")


if __name__ == "__main__":
    main()
