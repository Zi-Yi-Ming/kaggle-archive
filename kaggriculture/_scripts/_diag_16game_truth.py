# -*- coding: utf-8 -*-
"""Diagnostic: is the top5 16-0 result real, or a harness/state artifact?

High-info controls (not a full re-benchmark):
  C1  v11E vs closer_cleo  (known: v11E ~14% WR, margin ~-1.1k)
  C2  v11E self-play       (known: near 50%, small margins)
  C3  tetsu2131 vs v11E    FRESH load both agents every game
  C4  tetsu2131 vs v11E    REUSE agents across 8 games (screening style)
  C5  prvsiyan vs v11E     FRESH load (spot check)
  C6  bank trajectory at day boundaries for one decisive game

Run with: C:\\Users\\Lenovo\\.conda\\envs\\kaggle\\python.exe
"""
import os
import sys
import json
import importlib.util
import traceback

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from kaggle_environments import make
from _pm_pool import load_agent as load_pool_agent

PY = "C:\\Users\\Lenovo\\.conda\\envs\\kaggle\\python.exe"  # documentation only


def load_module_from_path(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_top5(name):
    path = os.path.join(BASE, "_external", "top5_notebooks", name, "wrapper.py")
    mod = load_module_from_path(path, f"fresh_{name}_{id(object())}")
    return mod.agent


def load_closer():
    path = os.path.join(BASE, "reference_agents", "closer_cleo.py")
    mod = load_module_from_path(path, f"fresh_cleo_{id(object())}")
    return mod.agent


def run_game(seed, a0, a1, snapshot_days=(5, 10, 15, 20, 25, 29)):
    """Run one 720-step game. Optionally snapshot banks on day boundaries.

    Returns dict with final banks and optional trajectory.
    """
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run([a0, a1])
    steps = env.steps
    final = steps[-1]
    obs0 = final[0]["observation"]
    obs1 = final[1]["observation"]
    bank0 = float(obs0["farms"][0]["money"])
    bank1 = float(obs1["farms"][1]["money"])
    traj = []
    for si, snap in enumerate(steps):
        try:
            o0 = snap[0]["observation"]
            if not isinstance(o0, dict):
                continue
            step = int(o0.get("step", -1))
            if step < 0:
                continue
            day = step // 24
            if step % 24 == 0 and day in snapshot_days:
                b0 = float(o0["farms"][0]["money"])
                # seat1 obs may not always be present the same way; try
                o1 = snap[1]["observation"]
                b1 = float(o1["farms"][1]["money"]) if isinstance(o1, dict) else float("nan")
                traj.append({"step": step, "day": day, "bank0": b0, "bank1": b1})
        except Exception:
            continue
    status = [s.get("status") for s in final]
    errors = [s.get("error") for s in final if s.get("error")]
    return {
        "seed": seed,
        "bank0": bank0,
        "bank1": bank1,
        "margin0": bank0 - bank1,
        "status": status,
        "errors": errors,
        "n_steps": len(steps),
        "traj": traj,
    }


def pair_stats(games, seat0_name="A", seat1_name="B"):
    """games: list of run_game results interpreted as seat0 vs seat1."""
    wins0 = wins1 = ties = 0
    margins = []
    for g in games:
        m = g["margin0"]
        margins.append(m)
        if m > 0:
            wins0 += 1
        elif m < 0:
            wins1 += 1
        else:
            ties += 1
    import statistics as st
    return {
        "n": len(games),
        "wins_seat0": wins0,
        "wins_seat1": wins1,
        "ties": ties,
        "mean_margin0": st.mean(margins) if margins else 0,
        "median_margin0": st.median(margins) if margins else 0,
        "margins": margins,
        "seat0": seat0_name,
        "seat1": seat1_name,
    }


def main():
    out = {"controls": {}, "games": {}, "errors": []}
    print("=== DIAG START ===", flush=True)

    # ---------- C1: closer_cleo seat0 vs v11E seat1, 4 seeds, fresh ----------
    print("[C1] closer_cleo vs v11E (fresh, 4 seeds, both seats)", flush=True)
    try:
        games = []
        for seat_swap in (0, 1):
            for seed in (1, 2, 3, 4):
                cleo = load_closer()
                v11e = load_pool_agent("v11E")
                if seat_swap == 0:
                    g = run_game(seed, cleo, v11e)
                    g["label"] = f"cleo_s0_seed{seed}"
                else:
                    g = run_game(seed, v11e, cleo)
                    g["label"] = f"v11e_s0_seed{seed}"
                    # flip so margin is always cleo - v11e
                    g["margin0"] = -g["margin0"]
                    g["cleo_bank"] = g["bank1"]
                    g["v11e_bank"] = g["bank0"]
                if seat_swap == 0:
                    g["cleo_bank"] = g["bank0"]
                    g["v11e_bank"] = g["bank1"]
                games.append(g)
                print(f"  C1 {g['label']}: cleo={g.get('cleo_bank')} v11e={g.get('v11e_bank')} "
                      f"margin={g['margin0']}", flush=True)
        margins = [g["margin0"] for g in games]
        cleo_wins = sum(1 for m in margins if m > 0)
        out["controls"]["C1_cleo_vs_v11e"] = {
            "n": len(games),
            "cleo_wins": cleo_wins,
            "v11e_wins": sum(1 for m in margins if m < 0),
            "ties": sum(1 for m in margins if m == 0),
            "mean_margin_cleo_minus_v11e": sum(margins) / len(margins),
            "margins": margins,
            "expected_from_PM_REPORT": "cleo ~86% WR, margin ~-1150 from v11E view",
        }
    except Exception as e:
        out["errors"].append({"control": "C1", "err": traceback.format_exc()})
        print("C1 FAIL", e, flush=True)

    # ---------- C2: v11E self-play 4 games fresh ----------
    print("[C2] v11E self-play (fresh, 4 games)", flush=True)
    try:
        games = []
        for seed in (1, 2, 3, 4):
            a = load_pool_agent("v11E")
            b = load_pool_agent("v11E")
            g = run_game(seed, a, b)
            games.append(g)
            print(f"  C2 seed{seed}: s0={g['bank0']} s1={g['bank1']} margin={g['margin0']}", flush=True)
        out["controls"]["C2_v11e_self"] = pair_stats(games, "v11E", "v11E")
    except Exception as e:
        out["errors"].append({"control": "C2", "err": traceback.format_exc()})
        print("C2 FAIL", e, flush=True)

    # ---------- C3: tetsu2131 vs v11E FRESH every game, 4 seeds both seats ----------
    print("[C3] tetsu2131 vs v11E FRESH every game", flush=True)
    try:
        games = []
        for cand_seat in (0, 1):
            for seed in (1, 2, 3, 4):
                cand = load_top5("tetsu2131")
                v11e = load_pool_agent("v11E")
                if cand_seat == 0:
                    g = run_game(seed, cand, v11e)
                    g["cand_bank"] = g["bank0"]
                    g["v11e_bank"] = g["bank1"]
                    g["margin_cand"] = g["bank0"] - g["bank1"]
                else:
                    g = run_game(seed, v11e, cand)
                    g["cand_bank"] = g["bank1"]
                    g["v11e_bank"] = g["bank0"]
                    g["margin_cand"] = g["bank1"] - g["bank0"]
                g["cand_seat"] = cand_seat
                games.append(g)
                print(f"  C3 seed{seed} seat{cand_seat}: cand={g['cand_bank']} "
                      f"v11e={g['v11e_bank']} margin={g['margin_cand']}", flush=True)
        out["controls"]["C3_tetsu_fresh"] = {
            "cand_wins": sum(1 for g in games if g["margin_cand"] > 0),
            "v11e_wins": sum(1 for g in games if g["margin_cand"] < 0),
            "ties": sum(1 for g in games if g["margin_cand"] == 0),
            "mean_margin": sum(g["margin_cand"] for g in games) / len(games),
            "margins": [g["margin_cand"] for g in games],
        }
        out["games"]["C3"] = [
            {k: g[k] for k in g if k != "traj"} for g in games
        ]
    except Exception as e:
        out["errors"].append({"control": "C3", "err": traceback.format_exc()})
        print("C3 FAIL", e, flush=True)

    # ---------- C4: tetsu2131 vs v11E REUSE agents (screening style), 8 games ----------
    print("[C4] tetsu2131 vs v11E REUSE agents across 8 games", flush=True)
    try:
        cand = load_top5("tetsu2131")
        v11e = load_pool_agent("v11E")
        games = []
        for cand_seat in (0, 1):
            for seed in (1, 2, 3, 4):
                if cand_seat == 0:
                    g = run_game(seed, cand, v11e)
                    g["cand_bank"] = g["bank0"]
                    g["v11e_bank"] = g["bank1"]
                    g["margin_cand"] = g["bank0"] - g["bank1"]
                else:
                    g = run_game(seed, v11e, cand)
                    g["cand_bank"] = g["bank1"]
                    g["v11e_bank"] = g["bank0"]
                    g["margin_cand"] = g["bank1"] - g["bank0"]
                g["cand_seat"] = cand_seat
                games.append(g)
                print(f"  C4 seed{seed} seat{cand_seat}: cand={g['cand_bank']} "
                      f"v11e={g['v11e_bank']} margin={g['margin_cand']}", flush=True)
        out["controls"]["C4_tetsu_reuse"] = {
            "cand_wins": sum(1 for g in games if g["margin_cand"] > 0),
            "v11e_wins": sum(1 for g in games if g["margin_cand"] < 0),
            "ties": sum(1 for g in games if g["margin_cand"] == 0),
            "mean_margin": sum(g["margin_cand"] for g in games) / len(games),
            "margins": [g["margin_cand"] for g in games],
        }
    except Exception as e:
        out["errors"].append({"control": "C4", "err": traceback.format_exc()})
        print("C4 FAIL", e, flush=True)

    # ---------- C5: prvsiyan FRESH, 2 seeds both seats ----------
    print("[C5] prvsiyan vs v11E FRESH (spot check)", flush=True)
    try:
        games = []
        for cand_seat in (0, 1):
            for seed in (1, 2):
                cand = load_top5("prvsiyan")
                v11e = load_pool_agent("v11E")
                if cand_seat == 0:
                    g = run_game(seed, cand, v11e)
                    g["margin_cand"] = g["bank0"] - g["bank1"]
                    g["cand_bank"] = g["bank0"]
                    g["v11e_bank"] = g["bank1"]
                else:
                    g = run_game(seed, v11e, cand)
                    g["margin_cand"] = g["bank1"] - g["bank0"]
                    g["cand_bank"] = g["bank1"]
                    g["v11e_bank"] = g["bank0"]
                games.append(g)
                print(f"  C5 seed{seed} seat{cand_seat}: cand={g['cand_bank']} "
                      f"v11e={g['v11e_bank']} margin={g['margin_cand']}", flush=True)
        out["controls"]["C5_prv_fresh"] = {
            "cand_wins": sum(1 for g in games if g["margin_cand"] > 0),
            "mean_margin": sum(g["margin_cand"] for g in games) / len(games),
        }
    except Exception as e:
        out["errors"].append({"control": "C5", "err": traceback.format_exc()})
        print("C5 FAIL", e, flush=True)

    # ---------- C6: trajectory on one tetsu vs v11e game ----------
    print("[C6] trajectory tetsu_s0 seed=1", flush=True)
    try:
        cand = load_top5("tetsu2131")
        v11e = load_pool_agent("v11E")
        g = run_game(1, cand, v11e, snapshot_days=(1, 3, 5, 8, 10, 15, 20, 25, 29))
        out["controls"]["C6_traj_tetsu_seed1"] = g
        print(f"  C6 final: cand={g['bank0']} v11e={g['bank1']} margin={g['margin0']}", flush=True)
        for t in g.get("traj") or []:
            print(f"    day={t['day']:2d} cand={t['bank0']:.0f} v11e={t['bank1']:.0f} "
                  f"diff={t['bank0']-t['bank1']:.0f}", flush=True)
    except Exception as e:
        out["errors"].append({"control": "C6", "err": traceback.format_exc()})
        print("C6 FAIL", e, flush=True)

    # ---------- C7: same trajectory for closer_cleo vs v11e ----------
    print("[C7] trajectory cleo_s0 seed=1", flush=True)
    try:
        cleo = load_closer()
        v11e = load_pool_agent("v11E")
        g = run_game(1, cleo, v11e, snapshot_days=(1, 3, 5, 8, 10, 15, 20, 25, 29))
        out["controls"]["C7_traj_cleo_seed1"] = g
        print(f"  C7 final: cleo={g['bank0']} v11e={g['bank1']} margin={g['margin0']}", flush=True)
        for t in g.get("traj") or []:
            print(f"    day={t['day']:2d} cleo={t['bank0']:.0f} v11e={t['bank1']:.0f} "
                  f"diff={t['bank0']-t['bank1']:.0f}", flush=True)
    except Exception as e:
        out["errors"].append({"control": "C7", "err": traceback.format_exc()})
        print("C7 FAIL", e, flush=True)

    out_path = os.path.join(BASE, "_diag_16game_truth.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2, default=str)
    print(f"\nWrote {out_path}", flush=True)

    # short interpretation
    print("\n=== INTERPRETATION HINTS ===", flush=True)
    c1 = out["controls"].get("C1_cleo_vs_v11e") or {}
    print(f"C1 cloe WR ~ {c1.get('cleo_wins')}/{c1.get('n')} mean_margin={c1.get('mean_margin_cleo_minus_v11e')}", flush=True)
    print("  If C1 is NOT ~cloe-dominant with small margin, harness/v11E load is broken.", flush=True)
    c3 = out["controls"].get("C3_tetsu_fresh") or {}
    c4 = out["controls"].get("C4_tetsu_reuse") or {}
    print(f"C3 tetsu FRESH  WR {c3.get('cand_wins')}/8 mean={c3.get('mean_margin')}", flush=True)
    print(f"C4 tetsu REUSE  WR {c4.get('cand_wins')}/8 mean={c4.get('mean_margin')}", flush=True)
    if c3 and c4:
        if c3.get("cand_wins", 0) >= 6 and c4.get("cand_wins", 0) >= 6:
            print("  → 16-0 looks REAL under both load policies (state-bleed not the cause).", flush=True)
        elif c3.get("cand_wins", 0) < c4.get("cand_wins", 0):
            print("  → REUSE inflates candidate wins; state contamination likely.", flush=True)
        elif c3.get("cand_wins", 0) == 0:
            print("  → FRESH kills the blowout; screening artifact suspected.", flush=True)


if __name__ == "__main__":
    main()
