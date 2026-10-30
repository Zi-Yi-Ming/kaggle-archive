# -*- coding: utf-8 -*-
"""P46: live R2 policy vs frozen R2 tape, same seeds, finn unwrapped."""
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

R2_PATH = ROOT / "_push_medal" / "main.py"
FINN_PATH = ROOT / "reference_agents" / "fallow_finn.py"
TAPE_PATH = ROOT / "p44_distilled_tapes" / "r2_live_distilled.json"


def load_agent(path, tag):
    spec = importlib.util.spec_from_file_location(tag, str(path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent if hasattr(m, "agent") else m.build_agent({})


def tape_agent(tape):
    def agent(observation, configuration=None):
        step = int((observation or {}).get("step") or 0)
        step = max(0, min(len(tape) - 1, step))
        a = tape[step]
        return {
            "farmer": a.get("farmer") or ["PASS"],
            "hands": a.get("hands") or [],
            "market": a.get("market") or [],
        }
    return agent


def run_pair(agent0, agent1, seed):
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    env.run([agent0, agent1])
    f = env.steps[-1]
    b0 = float(f[0]["observation"]["farms"][0]["money"])
    b1 = float(f[1]["observation"]["farms"][1]["money"])
    shops = []
    try:
        shops = list((f[0]["observation"].get("town") or {}).get("unlocked_shops") or [])
    except Exception:
        pass
    return b0, b1, shops


def eval_agent(make_fn, seeds, label):
    """Both seats vs finn. Returns per-seed rows + summary."""
    rows = []
    our_banks = []
    w = d = l = 0
    for seed in seeds:
        # seat 0
        us0 = make_fn()
        finn0 = load_agent(FINN_PATH, f"finn46_{label}_{seed}_0")
        b0a, b1a, shops = run_pair(us0, finn0, seed)
        # seat 1
        finn1 = load_agent(FINN_PATH, f"finn46_{label}_{seed}_1")
        us1 = make_fn()
        b0b, b1b, _ = run_pair(finn1, us1, seed)

        our = (b0a + b1b) / 2
        opp = (b1a + b0b) / 2
        our_banks.append(our)
        if our > opp + 1:
            w += 1
            res = "W"
        elif opp > our + 1:
            l += 1
            res = "L"
        else:
            d += 1
            res = "D"
        rows.append({
            "label": label, "seed": seed,
            "us_s0": b0a, "finn_s1": b1a,
            "finn_s0": b0b, "us_s1": b1b,
            "our_mean": our, "opp_mean": opp, "result": res,
            "shops": "|".join(shops),
        })
        print(f"  {label} s{seed}: us={our:.0f} opp={opp:.0f} {res} shops={shops}", flush=True)
    return {
        "label": label, "W": w, "D": d, "L": l, "W-L": w - l,
        "bank_mean": statistics.mean(our_banks),
        "bank_std": statistics.pstdev(our_banks) if len(our_banks) > 1 else 0,
        "bank_min": min(our_banks), "bank_max": max(our_banks),
        "rows": rows,
        "banks": our_banks,
    }


def record_tape_hash(make_fn, seed=1):
    keys = []
    fn = make_fn()
    n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)
    finn = load_agent(FINN_PATH, f"finn_hash_{seed}")

    if n <= 1:
        def wrap(obs):
            a = fn(obs)
            keys.append(json.dumps({"m": a.get("market"), "f": a.get("farmer"), "h": a.get("hands")},
                                   sort_keys=True, default=str))
            return a
        play = wrap
    else:
        def wrap(obs, configuration=None):
            a = fn(obs, configuration)
            keys.append(json.dumps({"m": a.get("market"), "f": a.get("farmer"), "h": a.get("hands")},
                                   sort_keys=True, default=str))
            return a
        play = wrap

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.info = {"seed": int(seed)}
    env.run([play, finn])
    h = hashlib.md5("\n".join(keys).encode()).hexdigest()[:16]
    bank = float(env.steps[-1][0]["observation"]["farms"][0]["money"])
    return h, bank, len(keys)


def main():
    t0 = time.time()
    seeds = (1, 2, 3, 4, 5, 11, 12, 13)
    print(f"seeds={seeds}", flush=True)

    td = json.loads(TAPE_PATH.read_text(encoding="utf-8"))
    frozen_tape = td["tape"]
    print(f"frozen tape hash={td['tape_hash']} n={len(frozen_tape)}", flush=True)

    def make_live_r2():
        return load_agent(R2_PATH, f"r2live_{id(object())}")

    def make_frozen():
        return tape_agent(frozen_tape)

    print("\n=== TAPE HASHES seed1 ===", flush=True)
    h_live, b_live, n_live = record_tape_hash(make_live_r2, 1)
    h_frz, b_frz, n_frz = record_tape_hash(make_frozen, 1)
    print(f"  live_r2  hash={h_live} bank={b_live:.0f} steps={n_live}", flush=True)
    print(f"  frozen   hash={h_frz} bank={b_frz:.0f} steps={n_frz}", flush=True)
    print(f"  identical_tape={h_live == h_frz}", flush=True)

    print("\n=== LIVE R2 vs finn ===", flush=True)
    live = eval_agent(make_live_r2, seeds, "live_R2")
    print(f"LIVE mean={live['bank_mean']:.0f}±{live['bank_std']:.0f} "
          f"range={live['bank_min']:.0f}-{live['bank_max']:.0f} "
          f"W-L={live['W-L']} ({live['W']}-{live['D']}-{live['L']})", flush=True)

    print("\n=== FROZEN tape vs finn ===", flush=True)
    frz = eval_agent(make_frozen, seeds, "frozen_tape")
    print(f"FROZEN mean={frz['bank_mean']:.0f}±{frz['bank_std']:.0f} "
          f"range={frz['bank_min']:.0f}-{frz['bank_max']:.0f} "
          f"W-L={frz['W-L']} ({frz['W']}-{frz['D']}-{frz['L']})", flush=True)

    # paired per-seed gap
    print("\n=== PAIRED GAP (live - frozen) ===", flush=True)
    gaps = []
    for i, seed in enumerate(seeds):
        gap = live["banks"][i] - frz["banks"][i]
        gaps.append(gap)
        print(f"  s{seed}: live={live['banks'][i]:.0f} frozen={frz['banks'][i]:.0f} gap={gap:.0f}", flush=True)
    gap_mean = statistics.mean(gaps)
    gap_std = statistics.pstdev(gaps) if len(gaps) > 1 else 0
    print(f"gap mean={gap_mean:.0f}±{gap_std:.0f} "
          f"ratio_frozen/live={frz['bank_mean']/live['bank_mean']:.3f}", flush=True)

    # also frozen vs live head-to-head (not just vs finn)
    print("\n=== live R2 vs frozen tape (H2H, both seats) ===", flush=True)
    h2h_rows = []
    hw = hd = hl = 0
    for seed in seeds:
        # live seat0, frozen seat1
        live_a = make_live_r2()
        frz_a = make_frozen()
        b0, b1, _ = run_pair(live_a, frz_a, seed)
        # frozen seat0, live seat1
        frz_b = make_frozen()
        live_b = make_live_r2()
        c0, c1, _ = run_pair(frz_b, live_b, seed)
        live_mean = (b0 + c1) / 2
        frz_mean = (b1 + c0) / 2
        if live_mean > frz_mean + 1:
            hw += 1
            res = "LIVE"
        elif frz_mean > live_mean + 1:
            hl += 1
            res = "FROZEN"
        else:
            hd += 1
            res = "TIE"
        h2h_rows.append({
            "seed": seed, "live_mean": live_mean, "frozen_mean": frz_mean,
            "winner": res,
            "live_s0": b0, "frozen_s1": b1, "frozen_s0": c0, "live_s1": c1,
        })
        print(f"  s{seed}: live={live_mean:.0f} frozen={frz_mean:.0f} {res}", flush=True)
    print(f"H2H live W-T-L vs frozen: {hw}-{hd}-{hl}", flush=True)

    # decision
    if gap_mean >= 30000 and frz["bank_mean"] < live["bank_mean"] * 0.7:
        decision = "REPRESENTATION_GAP_CONFIRMED"
    elif gap_mean >= 15000:
        decision = "REPRESENTATION_GAP_PARTIAL"
    else:
        decision = "NO_REPRESENTATION_GAP"

    print(f"\nP46_DECISION={decision}", flush=True)

    # write artifacts
    all_rows = live["rows"] + frz["rows"]
    with open(ROOT / "p46_live_vs_frozen.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        w.writeheader()
        w.writerows(all_rows)

    with open(ROOT / "p46_h2h_live_frozen.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(h2h_rows[0].keys()))
        w.writeheader()
        w.writerows(h2h_rows)

    summary = {
        "decision": decision,
        "seeds": list(seeds),
        "live_mean": live["bank_mean"], "live_std": live["bank_std"],
        "live_wl": live["W-L"],
        "frozen_mean": frz["bank_mean"], "frozen_std": frz["bank_std"],
        "frozen_wl": frz["W-L"],
        "gap_mean": gap_mean, "gap_std": gap_std,
        "ratio": frz["bank_mean"] / live["bank_mean"],
        "h2h_live_w": hw, "h2h_tie": hd, "h2h_frozen_w": hl,
        "tape_hash_live": h_live, "tape_hash_frozen": h_frz,
        "dt": time.time() - t0,
    }
    (ROOT / "p46_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("wrote p46_live_vs_frozen.csv p46_h2h_live_frozen.csv p46_summary.json", flush=True)


if __name__ == "__main__":
    main()
