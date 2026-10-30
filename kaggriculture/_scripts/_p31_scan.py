# -*- coding: utf-8 -*-
"""P31: scan public/elite candidates under pinned harness.

Performance first: bank + action-fingerprint vs R2.
Thresholds: Bronze>80k Strong>120k Elite>150k mean bank.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, str(path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def get_agent(mod):
    for attr in ("agent", "build_agent"):
        if hasattr(mod, attr):
            fn = getattr(mod, attr)
            if callable(fn):
                # build_agent may need args
                if attr == "build_agent":
                    try:
                        return fn({})
                    except Exception:
                        try:
                            return fn()
                        except Exception:
                            continue
                return fn
    return None


CANDIDATES = {
    "R2": ROOT / "_push_medal" / "main.py",
    "tetsu_shape": ROOT / "_external" / "public_nb" / "tetsu_shape" / "main.py",
    "tetsu_msf": ROOT / "_external" / "public_nb" / "tetsu_msf" / "main.py",
    "boatlee_v20": ROOT / "_external" / "public_nb" / "boatlee_v20" / "main.py",
    "kaito_v58": ROOT / "_external" / "public_nb" / "kaito_v58" / "main.py",
    "kaito_v48": ROOT / "_external" / "public_nb" / "kaito_v48" / "main.py",
    "kaito_v43": ROOT / "_external" / "public_nb" / "kaito_v43" / "main.py",
    "kaito_v27": ROOT / "_external" / "public_nb" / "kaito_v27" / "main.py",
    "kaito_v21": ROOT / "_external" / "public_nb" / "kaito_v21" / "main.py",
    "prvsiyan_moon": ROOT / "_external" / "public_nb" / "prvsiyan_moon" / "main.py",
    "rayk_rank": ROOT / "_external" / "public_nb" / "rayk_rank" / "main.py",
    "v66": ROOT / "_external" / "git" / "v66" / "main.py",
    "danilchil": ROOT / "_external" / "git" / "danilchil" / "champ" / "main.py",
    "florian": ROOT / "_external" / "git" / "florian" / "main.py",
    "qeinstein": ROOT / "_external" / "git" / "qeinstein" / "dist" / "sub-009-moev2" / "main.py",
    "straf10": ROOT / "_external" / "git" / "straf10" / "main.py",
}


def load_finn():
    path = ROOT / "reference_agents" / "fallow_finn.py"
    return load_module(path, "finn_p31").agent


def run_candidate(agent_fn, seed):
    finn = load_finn()
    seq = []

    def wrap(inner):
        def agent(obs, configuration=None):
            a = inner(obs, configuration)
            seq.append(json.dumps(
                {"m": a.get("market"), "f": a.get("farmer"), "h": a.get("hands")},
                sort_keys=True, default=str,
            ))
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
    opp = float(f[0]["observation"]["farms"][1]["money"])
    h = hashlib.md5("\n".join(seq).encode()).hexdigest()[:16]
    return bank, opp, h, len(seq)


def jaccard_actions(hashes_a, hashes_b):
    """Not real jaccard of actions — use hash equality rate as proxy if same length.
    Better: collect per-step action keys."""
    return None


def run_with_keys(agent_fn, seed):
    finn = load_finn()
    keys = []

    def wrap(inner):
        def agent(obs, configuration=None):
            a = inner(obs, configuration)
            keys.append(json.dumps(
                {"m": a.get("market"), "f": a.get("farmer"), "h": a.get("hands")},
                sort_keys=True, default=str,
            ))
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
    return bank, keys


def action_similarity(keys_a, keys_b):
    """Fraction of steps with identical action JSON (min length)."""
    n = min(len(keys_a), len(keys_b))
    if n == 0:
        return 0.0
    same = sum(1 for i in range(n) if keys_a[i] == keys_b[i])
    return same / n


def main():
    SEEDS = (1, 2, 3)
    results = []
    r2_keys = {}

    for name, path in CANDIDATES.items():
        if not path.exists():
            print(f"SKIP {name}: missing {path}", flush=True)
            continue
        try:
            mod = load_module(path, f"cand_{name}")
            fn = get_agent(mod)
            if fn is None:
                print(f"SKIP {name}: no agent", flush=True)
                continue
        except Exception as e:
            print(f"SKIP {name}: load error {e}", flush=True)
            continue

        banks = []
        all_keys = []
        ok = True
        for seed in SEEDS:
            try:
                bank, keys = run_with_keys(fn, seed)
                banks.append(bank)
                all_keys.append(keys)
                if name == "R2":
                    r2_keys[seed] = keys
            except Exception as e:
                print(f"  {name} s{seed} RUN ERR {e}", flush=True)
                ok = False
                break
        if not ok or not banks:
            continue
        mean_bank = sum(banks) / len(banks)
        # similarity to R2 on seed1
        sim = 0.0
        if name != "R2" and 1 in r2_keys and all_keys:
            sim = action_similarity(all_keys[0], r2_keys[1])
        tier = (
            "ELITE" if mean_bank >= 150000 else
            "STRONG" if mean_bank >= 120000 else
            "BRONZE" if mean_bank >= 80000 else
            "WEAK"
        )
        rec = {
            "name": name, "mean_bank": mean_bank,
            "bank_s1": banks[0], "bank_s2": banks[1] if len(banks) > 1 else None,
            "bank_s3": banks[2] if len(banks) > 2 else None,
            "r2_action_sim": sim, "tier": tier,
        }
        results.append(rec)
        print(f"{name:16s} mean={mean_bank:8.0f} tier={tier:6s} sim={sim:.3f} "
              f"banks={[round(b) for b in banks]}", flush=True)

    # sort by bank
    results.sort(key=lambda r: -r["mean_bank"])
    out = ROOT / "p31_candidate_scan.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        w.writeheader()
        w.writerows(results)

    print("\n=== HIGH QUALITY + LOW SIM ===")
    for r in results:
        if r["mean_bank"] >= 80000 and r["r2_action_sim"] < 0.5:
            print(f"  ** {r['name']}: bank={r['mean_bank']:.0f} sim={r['r2_action_sim']:.3f} tier={r['tier']}")
    print("wrote", out.name)


if __name__ == "__main__":
    main()
