# -*- coding: utf-8 -*-
"""P36: initial→tape audit. No training. Pin harness.

L0: does initial/seed distinguish elite trajectory class?
L1: given first K steps, how well can we match rest of same tape?
L2: tape uniqueness / family clustering across seeds.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

ELITES = {
    "R2": ROOT / "_push_medal" / "main.py",
    "kaito_v27": ROOT / "_external" / "public_nb" / "kaito_v27" / "main.py",
    "qeinstein": ROOT / "_external" / "git" / "qeinstein" / "dist" / "sub-009-moev2" / "main.py",
    "rayk_rank": ROOT / "_external" / "public_nb" / "rayk_rank" / "main.py",
}
SEEDS = (1, 2, 3, 4, 5)


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
    return load_mod(ROOT / "reference_agents" / "fallow_finn.py", "finn_p36").agent


def run_tape(agent_fn, seed):
    finn = load_finn()
    tape = []  # per-step action keys
    shops_at = {}
    init_money = None

    def wrap(inner):
        def agent(obs, configuration=None):
            a = inner(obs, configuration)
            step = int(obs.get("step") or 0)
            key = json.dumps(
                {"m": a.get("market"), "f": a.get("farmer"), "h": a.get("hands")},
                sort_keys=True, default=str,
            )
            tape.append(key)
            if step == 0:
                farm = (obs.get("farms") or [])[0]
                init_money = float(farm.get("money") or 0)
            if step in (0, 144, 288, 432):
                shops_at[step] = tuple((obs.get("town") or {}).get("unlocked_shops") or [])
            return a
        return agent

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    env.run([wrap(agent_fn), finn])
    f = env.steps[-1]
    bank = float(f[0]["observation"]["farms"][0]["money"])
    h = hashlib.md5("\n".join(tape).encode()).hexdigest()[:16]
    return {
        "tape": tape, "bank": bank, "hash": h, "n": len(tape),
        "shops": shops_at, "init_money": init_money,
    }


def prefix_match(a, b, k):
    n = min(len(a), len(b), k)
    if n == 0:
        return 0.0
    return sum(1 for i in range(n) if a[i] == b[i]) / n


def suffix_match(a, b, k):
    """Match on steps after k."""
    if len(a) <= k or len(b) <= k:
        return 0.0
    n = min(len(a), len(b)) - k
    if n <= 0:
        return 0.0
    return sum(1 for i in range(k, k + n) if a[i] == b[i]) / n


def main():
    # record all
    tapes = {}  # (policy, seed) -> result
    for name, path in ELITES.items():
        if not path.exists():
            print("SKIP", name, flush=True)
            continue
        fn = get_agent(load_mod(path, f"p36_{name}"))
        for seed in SEEDS:
            r = run_tape(fn, seed)
            tapes[(name, seed)] = r
            print(f"  {name} s{seed}: bank={r['bank']:.0f} hash={r['hash']} "
                  f"shops144={r['shops'].get(144)}", flush=True)

    # --- L2: tape uniqueness ---
    print("\n=== L2 TAPE HASHES ===")
    by_hash = defaultdict(list)
    for (name, seed), r in tapes.items():
        by_hash[r["hash"]].append(f"{name}:s{seed}")
    print(f"  unique tapes: {len(by_hash)} / {len(tapes)}")
    for h, members in by_hash.items():
        if len(members) > 1:
            print(f"  SAME {h}: {members}")

    # same-policy different-seed tape similarity
    print("\n=== same-policy cross-seed prefix/suffix match ===")
    rows_sim = []
    for name in ELITES:
        seeds = [s for s in SEEDS if (name, s) in tapes]
        if len(seeds) < 2:
            continue
        for i in range(len(seeds)):
            for j in range(i + 1, len(seeds)):
                a = tapes[(name, seeds[i])]
                b = tapes[(name, seeds[j])]
                p50 = prefix_match(a["tape"], b["tape"], 50)
                p144 = prefix_match(a["tape"], b["tape"], 144)
                s144 = suffix_match(a["tape"], b["tape"], 144)
                full = prefix_match(a["tape"], b["tape"], 720)
                rows_sim.append({
                    "policy": name, "seed_a": seeds[i], "seed_b": seeds[j],
                    "same_hash": int(a["hash"] == b["hash"]),
                    "match_0_50": p50, "match_0_144": p144,
                    "match_after_144": s144, "match_full": full,
                    "shops144_a": str(a["shops"].get(144)),
                    "shops144_b": str(b["shops"].get(144)),
                })
                print(f"  {name} s{seeds[i]}x{seeds[j]}: full={full:.3f} "
                      f"after144={s144:.3f} same_shops={a['shops'].get(144)==b['shops'].get(144)}")

    out = ROOT / "p36_tape_similarity.csv"

    # --- L0: initial shops at day0 don't exist; use first shop unlock ---
    # Predict policy from shops@144 (env realization)
    print("\n=== L0 shops@144 → policy class ===")
    shop_to_pol = defaultdict(Counter)
    for (name, seed), r in tapes.items():
        s144 = r["shops"].get(144)
        shop_to_pol[str(s144)][name] += 1
    for s, c in shop_to_pol.items():
        print(f"  {s}: {dict(c)}")

    # --- L1: prefix K → suffix identity ---
    print("\n=== L1 prefix→suffix within same tape (self) vs cross ===")
    # self: split one tape, trivial
    # cross: if two tapes share prefix of length K, do they share suffix?
    for K in (1, 6, 24, 72, 144):
        same_suf = 0
        diff_suf = 0
        for (n1, s1), r1 in list(tapes.items()):
            for (n2, s2), r2 in list(tapes.items()):
                if (n1, s1) >= (n2, s2):
                    continue
                if prefix_match(r1["tape"], r2["tape"], K) >= 0.99:
                    sm = suffix_match(r1["tape"], r2["tape"], K)
                    if sm >= 0.9:
                        same_suf += 1
                    else:
                        diff_suf += 1
        print(f"  K={K}: near-identical prefix pairs with matching suffix={same_suf} mismatch={diff_suf}")

    # write sim csv
    if rows_sim:
        with open(out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows_sim[0].keys()))
            w.writeheader()
            w.writerows(rows_sim)
        print("wrote", out.name)

    # summary banks
    print("\n=== BANKS ===")
    for name in ELITES:
        vals = [tapes[(name, s)]["bank"] for s in SEEDS if (name, s) in tapes]
        if vals:
            print(f"  {name}: mean={sum(vals)/len(vals):.0f} min={min(vals):.0f} max={max(vals):.0f}")


if __name__ == "__main__":
    main()
