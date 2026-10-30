# -*- coding: utf-8 -*-
"""P27: re-evaluate R2 local neighborhood under pinned episode seed (P26 harness).

1) R2 reference across seeds
2) P25-style 2-step mutations (subset)
3) P24-style day-window replacement (subset)
All vs fallow_finn. Δ = bank(mut) - bank(T0 same seed).
"""
from __future__ import annotations

import copy
import csv
import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from p26_harness import load_r2, load_pool, run_game  # noqa: E402


def mutate_action(action, kind):
    a = copy.deepcopy(action) if action else {"farmer": ["PASS"], "hands": [], "market": []}
    market = [o for o in (a.get("market") or []) if o]
    if kind == "DROP_SELL":
        a["market"] = [o for o in market if o[0] != "SELL"]
    elif kind == "SKIP_HIRE":
        a["market"] = [o for o in market if o[0] != "HIRE"]
    elif kind == "NO_WORK":
        a["farmer"] = ["PASS"]
        a["hands"] = []
    elif kind == "DROP_BUY":
        a["market"] = [o for o in market if o[0] not in ("BUY_SEED", "BUY_PRODUCT", "BUY_ANIMAL", "BUY_LAND")]
    return a


def make_perturbed(r2_agent, day, n_steps, kind):
    state = {"left": n_steps}

    def agent(obs, configuration=None):
        action = r2_agent(obs, configuration)
        step = int(obs.get("step") or 0)
        d = step // 24
        if d == day and state["left"] > 0:
            state["left"] -= 1
            return mutate_action(action, kind)
        return action

    return agent


def setup_our():
    import p13_1_melon, p13_3_water, p14_1_on, p14_2_on, p16_branch, p17_1_library
    import p18_selector as sel
    p13_1_melon.set_enabled(False)
    p13_3_water.set_enabled(True)
    p14_1_on.set_enabled(True)
    p14_2_on.set_enabled(False)
    p16_branch.set_branch_mode("off")
    p17_1_library.set_enabled(False)
    sel.set_selector("S0")
    from p11_planner import planner as pmod
    pmod._PLANNER = None
    return pmod.agent


def make_window_mutant(r2_agent, our_agent, day_lo, day_hi):
    def agent(obs, configuration=None):
        step = int(obs.get("step") or 0)
        day = step // 24
        if day_lo <= day < day_hi:
            return our_agent(obs, configuration)
        return r2_agent(obs, configuration)
    return agent


def main():
    finn = load_pool("fallow_finn")
    rows = []

    # --- 1) R2 reference ---
    print("=== R2 reference (pinned seed) ===")
    t0 = {}
    for seed in (1, 2, 3, 4, 5):
        r = run_game(load_r2(), finn, seed)
        t0[seed] = r["bank0"]
        rows.append({"phase": "T0", "seed": seed, "kind": "BASE", "day": "",
                     "bank": r["bank0"], "delta": 0, "hash0": r["hash0"],
                     "shops": str(r["shops"])})
        print(f"  seed{seed}: bank={r['bank0']:.0f} hash={r['hash0']} shops={r['shops']}", flush=True)

    # determinism check seed1 repeat
    r = run_game(load_r2(), finn, 1)
    print(f"  seed1 repeat: bank={r['bank0']:.0f} hash={r['hash0']} "
          f"match={r['bank0']==t0[1] and r['hash0']==rows[0]['hash0']}", flush=True)

    # --- 2) P25 subset mutations ---
    print("\n=== P25 mutations (pinned) ===")
    kinds = ("DROP_SELL", "SKIP_HIRE", "NO_WORK")
    days = (7, 10, 14, 25)
    for seed in (1, 2, 3):
        for day in days:
            for kind in kinds:
                own = make_perturbed(load_r2(), day, 2, kind)
                r = run_game(own, finn, seed)
                delta = r["bank0"] - t0[seed]
                rows.append({"phase": "P25", "seed": seed, "kind": kind, "day": day,
                             "bank": r["bank0"], "delta": delta, "hash0": r["hash0"],
                             "shops": str(r["shops"])})
                print(f"  s{seed} d{day} {kind:10s} bank={r['bank0']:.0f} Δ={delta:+.0f} "
                      f"hash0={r['hash0']}", flush=True)

    # --- 3) P24 window replacement ---
    print("\n=== P24 window replacement (pinned) ===")
    for seed in (1, 2, 3):
        our = setup_our()
        own = make_window_mutant(load_r2(), our, 9, 12)
        r = run_game(own, finn, seed)
        delta = r["bank0"] - t0[seed]
        rows.append({"phase": "P24", "seed": seed, "kind": "R2+d9_12_OUR", "day": "9-12",
                     "bank": r["bank0"], "delta": delta, "hash0": r["hash0"],
                     "shops": str(r["shops"])})
        print(f"  s{seed} T1 bank={r['bank0']:.0f} Δ={delta:+.0f}", flush=True)

        our2 = setup_our()
        own2 = make_window_mutant(load_r2(), our2, 0, 5)
        r2 = run_game(own2, finn, seed)
        delta2 = r2["bank0"] - t0[seed]
        rows.append({"phase": "P24", "seed": seed, "kind": "R2+d0_5_OUR", "day": "0-5",
                     "bank": r2["bank0"], "delta": delta2, "hash0": r2["hash0"],
                     "shops": str(r2["shops"])})
        print(f"  s{seed} T2 bank={r2['bank0']:.0f} Δ={delta2:+.0f}", flush=True)

    out = ROOT / "p27_pinned_rerun.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # summary P25
    p25 = [r for r in rows if r["phase"] == "P25"]
    deltas = [r["delta"] for r in p25]
    pos = sum(1 for d in deltas if d > 0)
    n = len(deltas)
    print("\n=== P25 PINNED DENSITY ===")
    print(f"  n={n} positive={pos}/{n} ({100*pos/n:.0f}%)")
    if n:
        print(f"  meanΔ={sum(deltas)/n:+.0f} medianΔ={sorted(deltas)[n//2]:+.0f} "
              f"best={max(deltas):+.0f} worst={min(deltas):+.0f}")
    print("  by kind:")
    for kind in kinds:
        ds = [r["delta"] for r in p25 if r["kind"] == kind]
        p = sum(1 for d in ds if d > 0)
        print(f"    {kind:10s} pos={p}/{len(ds)} mean={sum(ds)/len(ds):+.0f}")

    # shop consistency: T0 vs mut same seed should share shops if mutation after d144? 
    # shops drawn through game; report if mut shops differ from T0
    print("\n=== shop consistency vs T0 ===")
    t0_shops = {r["seed"]: r["shops"] for r in rows if r["phase"] == "T0"}
    mism = 0
    for r in p25:
        if r["shops"] != t0_shops.get(r["seed"]):
            mism += 1
    print(f"  P25 shop mismatch vs T0: {mism}/{len(p25)}")

    print("wrote", out.name)


if __name__ == "__main__":
    main()
