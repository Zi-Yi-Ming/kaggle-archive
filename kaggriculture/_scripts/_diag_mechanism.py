# -*- coding: utf-8 -*-
"""Focused mechanism diagnostics (high information, low runtime).

Q1 Absolute bank vs fallow_finn (no-op floor) for main agents
Q2 Structure snapshots: tetsu/prv vs v11E — what differs mid-game?
Q3 Critical cross-play pairs:
     tetsu vs prvsiyan     (do top candidates crush each other?)
     tetsu vs closer_cleo  (does the known v11E-killer also beat tetsu?)
     prvsiyan vs closer_cleo
     ronin5205 vs tetsu    (ronin is ~even vs v11E)
     flexonafft vs salemali7 (two other 16-0 candidates)
     flexonafft vs closer_cleo
"""
import os
import sys
import json
import importlib.util
import traceback
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from kaggle_environments import make
from _pm_pool import load_agent as load_pool_agent


def load_top5(name, tag):
    path = os.path.join(BASE, "_external", "top5_notebooks", name, "wrapper.py")
    spec = importlib.util.spec_from_file_location(f"top5_{name}_{tag}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent


def load_ronin(tag):
    for rel in (
        os.path.join(BASE, "_external", "ronin5205", "wrapper.py"),
        os.path.join(BASE, "_external", "ronin5205", "main.py"),
    ):
        if os.path.isfile(rel):
            spec = importlib.util.spec_from_file_location(f"ronin_{tag}", rel)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod.agent
    raise FileNotFoundError("ronin5205 not found")


def load_cleo(tag="x"):
    path = os.path.join(BASE, "reference_agents", "closer_cleo.py")
    spec = importlib.util.spec_from_file_location(f"cleo_{tag}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.agent


def load_named(name, tag):
    if name == "v11E":
        return load_pool_agent("v11E")
    if name == "closer_cleo":
        return load_cleo(tag)
    if name == "ronin5205":
        return load_ronin(tag)
    if name in ("tetsu2131", "prvsiyan", "flexonafft", "salemali7"):
        return load_top5(name, tag)
    return load_pool_agent(name)


def farm_structure(obs, player):
    farms = obs.get("farms") or []
    if player >= len(farms):
        return {}
    f = farms[player] or {}
    animals = Counter()
    plants = Counter()
    for row in f.get("tiles") or []:
        for tile in row or []:
            if not isinstance(tile, dict):
                continue
            if tile.get("animal"):
                animals[tile["animal"]] += 1
            elif tile.get("kind") == "PLANT" and tile.get("crop"):
                plants[tile["crop"]] += 1
    return {
        "money": float(f.get("money") or 0),
        "hands": len(f.get("hands") or []),
        "quads": len(f.get("unlocked_quadrants") or []),
        "animals": dict(animals),
        "plants": dict(plants),
        "animal_total": sum(animals.values()),
        "plant_total": sum(plants.values()),
    }


def run_game(seed, a0, a1, snapshot_days=(10, 15, 20, 25, 29)):
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run([a0, a1])
    steps = env.steps
    final = steps[-1]
    o0 = final[0]["observation"]
    o1 = final[1]["observation"]
    bank0 = float(o0["farms"][0]["money"])
    bank1 = float(o1["farms"][1]["money"])
    snaps = []
    for snap in steps:
        try:
            oo0 = snap[0]["observation"]
            if not isinstance(oo0, dict):
                continue
            step = int(oo0.get("step", -1))
            if step < 0 or step % 24 != 0:
                continue
            day = step // 24
            if day not in snapshot_days:
                continue
            oo1 = snap[1]["observation"]
            snaps.append({
                "day": day,
                "p0": farm_structure(oo0, 0),
                "p1": farm_structure(oo1, 1),
            })
        except Exception:
            continue
    return {
        "seed": seed,
        "bank0": bank0,
        "bank1": bank1,
        "margin0": bank0 - bank1,
        "snaps": snaps,
    }


def play_pair(A, B, seeds=(1, 2), both_seats=True):
    """Return list of games with margin_A (positive = A won)."""
    games = []
    seats = (0, 1) if both_seats else (0,)
    for seat in (0, 1):
        if not both_seats and seat == 1:
            continue
        for seed in seeds:
            tag = f"{A}_{B}_{seat}_{seed}_{id(object())}"
            a = load_named(A, tag + "a")
            b = load_named(B, tag + "b")
            if seat == 0:
                g = run_game(seed, a, b)
                margin_A = g["bank0"] - g["bank1"]
                bank_A, bank_B = g["bank0"], g["bank1"]
            else:
                g = run_game(seed, b, a)  # B first, A second
                margin_A = g["bank1"] - g["bank0"]
                bank_A, bank_B = g["bank1"], g["bank0"]
            games.append({
                "seed": seed, "A_seat": seat,
                "bank_A": bank_A, "bank_B": bank_B,
                "margin_A": margin_A,
                "snaps": g.get("snaps"),
            })
            print(f"  {A} vs {B} seed{seed} Aseat{seat}: "
                  f"A={bank_A:.0f} B={bank_B:.0f} m={margin_A:+.0f}", flush=True)
    return games


def summarize(games):
    wins_A = sum(1 for g in games if g["margin_A"] > 0)
    wins_B = sum(1 for g in games if g["margin_A"] < 0)
    ties = sum(1 for g in games if g["margin_A"] == 0)
    mean_m = sum(g["margin_A"] for g in games) / len(games) if games else 0
    return {
        "n": len(games),
        "wins_A": wins_A,
        "wins_B": wins_B,
        "ties": ties,
        "mean_margin_A": mean_m,
        "margins": [g["margin_A"] for g in games],
    }


def dump_struct(label, snaps, name0, name1):
    print(f"\n--- STRUCT {label} ---", flush=True)
    for s in snaps or []:
        p0, p1 = s["p0"], s["p1"]
        print(f"  day {s['day']}", flush=True)
        print(f"    {name0:12s}: $ {p0['money']:8.0f}  hands={p0['hands']} quads={p0['quads']} "
              f"an={p0['animal_total']}{p0['animals']} pl={p0['plant_total']}{p0['plants']}", flush=True)
        print(f"    {name1:12s}: $ {p1['money']:8.0f}  hands={p1['hands']} quads={p1['quads']} "
              f"an={p1['animal_total']}{p1['animals']} pl={p1['plant_total']}{p1['plants']}", flush=True)


def main():
    out = {"absolute": [], "pairs": {}, "structures": {}, "errors": []}

    # ---- Q1 absolute ----
    print("=== Q1 ABSOLUTE vs fallow_finn ===", flush=True)
    for name in ["v11E", "tetsu2131", "prvsiyan", "flexonafft", "salemali7", "closer_cleo", "ronin5205"]:
        banks = []
        try:
            for seed in (1, 2, 3):
                a = load_named(name, f"abs_{name}_{seed}")
                b = load_pool_agent("fallow_finn")
                g = run_game(seed, a, b, snapshot_days=())
                banks.append(g["bank0"])
                print(f"  {name:12s} vs finn seed{seed}: {g['bank0']:.0f}", flush=True)
            out["absolute"].append({
                "agent": name,
                "banks": banks,
                "mean": sum(banks) / len(banks),
            })
        except Exception:
            out["errors"].append({"abs": name, "err": traceback.format_exc()})
            print(f"  {name} ABS FAIL", flush=True)

    # ---- Q2 structures ----
    print("\n=== Q2 STRUCTURES ===", flush=True)
    try:
        a = load_named("tetsu2131", "st_a")
        b = load_named("v11E", "st_b")
        g = run_game(1, a, b)
        dump_struct("tetsu vs v11E seed1", g["snaps"], "tetsu", "v11E")
        out["structures"]["tetsu_vs_v11e"] = {
            "margin": g["margin0"], "banks": [g["bank0"], g["bank1"]],
            "snaps": g["snaps"],
        }
    except Exception:
        out["errors"].append({"struct": "tetsu", "err": traceback.format_exc()})

    try:
        a = load_named("prvsiyan", "st_pa")
        b = load_named("v11E", "st_pb")
        g = run_game(1, a, b)
        dump_struct("prvsiyan vs v11E seed1", g["snaps"], "prv", "v11E")
        out["structures"]["prv_vs_v11e"] = {
            "margin": g["margin0"], "banks": [g["bank0"], g["bank1"]],
            "snaps": g["snaps"],
        }
    except Exception:
        out["errors"].append({"struct": "prv", "err": traceback.format_exc()})

    # ---- Q3 critical pairs ----
    pairs = [
        ("tetsu2131", "prvsiyan"),
        ("tetsu2131", "closer_cleo"),
        ("prvsiyan", "closer_cleo"),
        ("ronin5205", "tetsu2131"),
        ("flexonafft", "salemali7"),
        ("flexonafft", "closer_cleo"),
        ("salemali7", "closer_cleo"),
    ]
    print("\n=== Q3 CRITICAL CROSS-PLAY ===", flush=True)
    for A, B in pairs:
        print(f"\n>> {A} vs {B}", flush=True)
        try:
            games = play_pair(A, B, seeds=(1, 2), both_seats=True)
            rec = summarize(games)
            rec["A"] = A
            rec["B"] = B
            out["pairs"][f"{A}__vs__{B}"] = rec
            print(f"  SUMMARY {A}-{B}: {rec['wins_A']}-{rec['wins_B']}-{rec['ties']} "
                  f"mean_m_A={rec['mean_margin_A']:+.0f}", flush=True)
        except Exception:
            out["errors"].append({"pair": f"{A} vs {B}", "err": traceback.format_exc()})
            print(f"  FAIL {A} vs {B}", flush=True)

    path = os.path.join(BASE, "_diag_mechanism.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2, default=str)
    print(f"\nWrote {path}", flush=True)

    print("\n=== ABS TABLE ===", flush=True)
    for r in out["absolute"]:
        print(f"  {r['agent']:12s} mean_vs_finn = {r['mean']:.0f}", flush=True)


if __name__ == "__main__":
    main()
