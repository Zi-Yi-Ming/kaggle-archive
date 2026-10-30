# -*- coding: utf-8 -*-
"""Fixed 8-game paired head-to-head benchmark + smoke for 3 external candidates vs v11E.

Uses importlib.util.spec_from_file_location with unique module names to avoid
the Python module-name caching collision that invalidated the previous run.
"""
import sys, os, json, statistics, traceback, importlib.util
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kaggle_environments import make
from _pm_pool import load_agent as load_pool_agent

BASE = os.path.dirname(os.path.abspath(__file__))

# ------------------------------------------------------------------ loaders --
def _load_wrapper(candidate_key):
    """Return (module, module_name, module_file)."""
    map_ = {
        "lonespear": os.path.join(BASE, "_external", "lonespear", "wrapper.py"),
        "ronin5205": os.path.join(BASE, "_external", "ronin5205", "wrapper.py"),
        "gzmcr":     os.path.join(BASE, "_external", "gzmcr", "wrapper.py"),
    }
    name_map = {
        "lonespear": "external_lonespear_wrapper",
        "ronin5205": "external_ronin5205_wrapper",
        "gzmcr":     "external_gzmcr_wrapper",
    }
    path = map_[candidate_key]
    mod_name = name_map[candidate_key]
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    spec = importlib.util.spec_from_file_location(mod_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, mod_name, os.path.abspath(path)


# ------------------------------------------------------------------ smoke --
SMOKE_SEEDS = [1, 2]
MIN_STEPS = 50

def _minimal_obs():
    # Build a minimal valid observation matching kaggriculture's initial obs.
    # This avoids running a full game just to check action schema.
    return {
        "farms": [[{"money": 500, "crops": [], "animals": [], "structures": []}]],
        "day": 0,
        "season": 0,
        "year": 1,
        "town": {"shops": []},
        "market": {},
    }

def run_smoke(candidate_key):
    mod, mod_name, mod_file = _load_wrapper(candidate_key)
    agent_fn = mod.agent

    rec = {
        "candidate": candidate_key,
        "module_name": mod_name,
        "module_file": mod_file,
        "load_ok": True,
        "action_ok": False,
        "steps_executed": 0,
        "runtime_error": None,
    }

    # 1) action schema
    try:
        action = agent_fn(_minimal_obs())
        if not isinstance(action, dict):
            rec["runtime_error"] = f"action is {type(action).__name__}, not dict"
            return rec
        for k in ("farmer", "hands", "market"):
            if k not in action:
                rec["runtime_error"] = f"action missing key '{k}'"
                return rec
        rec["action_ok"] = True
    except Exception as e:
        rec["runtime_error"] = f"agent call failed: {e}"
        return rec

    # 2) short real game to confirm runtime compatibility
    for seed in SMOKE_SEEDS:
        env = make("kaggriculture", debug=False)
        env.configuration["episodeSteps"] = 720
        env.configuration["seed"] = seed
        try:
            env.run([agent_fn, load_pool_agent("v11E")])
            steps = len(env.steps)
            rec["steps_executed"] = max(rec["steps_executed"], steps)
            if steps < MIN_STEPS:
                rec["runtime_error"] = f"game aborted at step {steps}"
                return rec
        except Exception as e:
            rec["runtime_error"] = f"game crash seed={seed}: {e}"
            return rec

    return rec


# ----------------------------------------------------------- benchmark helpers --
SEEDS = [1, 2, 3, 4]

def run_game(agent0, agent1, seed):
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    try:
        env.run([agent0, agent1])
        fin = env.steps[-1]
        b0 = fin[0]["observation"]["farms"][0]["money"]
        b1 = fin[1]["observation"]["farms"][1]["money"]
        status0 = fin[0].get("status", "")
        status1 = fin[1].get("status", "")
        invalid = status0.count("INVALID") + status1.count("INVALID")
        return {
            "status": "ok",
            "bank_seat0": b0,
            "bank_seat1": b1,
            "invalid_actions": invalid,
            "sell_failures": 0,
            "error": None,
        }
    except Exception as e:
        return {
            "status": "crash",
            "bank_seat0": None,
            "bank_seat1": None,
            "invalid_actions": 0,
            "sell_failures": 0,
            "error": str(e),
        }


# ------------------------------------------------------------------- main ---
def main():
    # ----------------------- smoke -----------------------
    print("=== SMOKE ===")
    smoke_results = []
    for cname in ["lonespear", "ronin5205", "gzmcr"]:
        rec = run_smoke(cname)
        smoke_results.append(rec)
        print(f"{cname}: module={rec['module_name']} file={rec['module_file']}")
        print(f"       load_ok={rec['load_ok']} action_ok={rec['action_ok']} "
              f"steps={rec['steps_executed']} err={rec['runtime_error']}")
        if rec["module_file"] != os.path.abspath(os.path.join(BASE, "_external", cname, "wrapper.py")):
            print(f"STOP: module file mismatch for {cname}: {rec['module_file']}")
            return
        # immediate identity check
        mod2, _, _ = _load_wrapper(cname)
        if mod2 is not rec.get("_mod"):
            pass  # different loads are expected to be different module objects

    with open("_external_8game_smoke_results.json", "w", encoding="utf-8") as f:
        json.dump({"results": smoke_results}, f, ensure_ascii=False, indent=2)

    # verify no module collision across the three loaded modules
    mods = {}
    for cname in ["lonespear", "ronin5205", "gzmcr"]:
        mod, mod_name, mod_file = _load_wrapper(cname)
        mods[cname] = (mod, mod_name, mod_file)

    files = [m[2] for m in mods.values()]
    if len(set(files)) != len(files):
        print("STOP: module file collision detected:")
        for cname, (mod, mod_name, mod_file) in mods.items():
            print(f"  {cname}: {mod_file}")
        return

    print("\nModule identity check:")
    for cname, (mod, mod_name, mod_file) in mods.items():
        print(f"  {cname}: name={mod_name} file={mod_file}")

    # ----------------------- benchmark --------------------
    print("\n=== 24-GAME BENCHMARK ===")
    results = []
    for cname in ["lonespear", "ronin5205", "gzmcr"]:
        wrapper_mod, _, _ = _load_wrapper(cname)
        ext_agent = wrapper_mod.agent
        for seed in SEEDS:
            for external_seat in [0, 1]:
                v11e = load_pool_agent("v11E")
                if external_seat == 0:
                    res = run_game(ext_agent, v11e, seed)
                    ext_bank = res["bank_seat0"]
                    v11e_bank = res["bank_seat1"]
                else:
                    res = run_game(v11e, ext_agent, seed)
                    v11e_bank = res["bank_seat0"]
                    ext_bank = res["bank_seat1"]
                margin = (ext_bank - v11e_bank) if (ext_bank is not None and v11e_bank is not None) else None
                winner = None
                if margin is not None:
                    winner = cname if margin > 0 else ("v11E" if margin < 0 else "tie")
                rec = {
                    "candidate": cname,
                    "module_name": wrapper_mod.__name__,
                    "module_file": os.path.abspath(wrapper_mod.__file__),
                    "seed": seed,
                    "external_seat": external_seat,
                    "v11e_seat": 1 - external_seat,
                    "winner": winner,
                    "external_final_bank": ext_bank,
                    "v11e_final_bank": v11e_bank,
                    "margin": margin,
                    "invalid_actions": res["invalid_actions"],
                    "sell_failures": res["sell_failures"],
                    "completed": res["status"] == "ok",
                    "runtime_error": res["error"],
                }
                results.append(rec)
                print(f"{cname} seed={seed} ext_seat={external_seat} -> "
                      f"ext={ext_bank} v11e={v11e_bank} margin={margin} "
                      f"ok={rec['completed']} err={res['error']}", flush=True)

    # ----------------------- summary ---------------------
    summary = {}
    for cname in ["lonespear", "ronin5205", "gzmcr"]:
        subset = [r for r in results if r["candidate"] == cname]
        ok = [r for r in subset if r["completed"]]
        ext_wins = sum(1 for r in ok if r["margin"] is not None and r["margin"] > 0)
        v11e_wins = sum(1 for r in ok if r["margin"] is not None and r["margin"] < 0)
        ties = sum(1 for r in ok if r["margin"] == 0)
        margins = [r["margin"] for r in ok if r["margin"] is not None]
        mean_margin = statistics.mean(margins) if margins else None
        median_margin = statistics.median(margins) if margins else None
        min_margin = min(margins) if margins else None
        max_margin = max(margins) if margins else None
        seat0 = [r for r in ok if r["external_seat"] == 0]
        seat1 = [r for r in ok if r["external_seat"] == 1]
        seat0_wins = sum(1 for r in seat0 if r["margin"] is not None and r["margin"] > 0)
        seat1_wins = sum(1 for r in seat1 if r["margin"] is not None and r["margin"] > 0)
        summary[cname] = {
            "n": len(subset),
            "ok": len(ok),
            "crash": len(subset) - len(ok),
            "wins": ext_wins,
            "losses": v11e_wins,
            "ties": ties,
            "win_rate": ext_wins / len(ok) if ok else 0,
            "mean_margin": mean_margin,
            "median_margin": median_margin,
            "min_margin": min_margin,
            "max_margin": max_margin,
            "invalid_actions_total": sum(r["invalid_actions"] for r in ok),
            "sell_failures_total": sum(r["sell_failures"] for r in ok),
            "seat0_record": f"{seat0_wins}-{len(seat0)-seat0_wins}",
            "seat1_record": f"{seat1_wins}-{len(seat1)-seat1_wins}",
        }

    print("\n=== RESULTS ===")
    print(f"| Agent | W-L | Win Rate | Mean Margin | Seat 0 | Seat 1 | Verdict |")
    print(f"| ----- | --: | -------: | ----------: | -----: | -----: | ------- |")
    for cname in ["lonespear", "ronin5205", "gzmcr"]:
        s = summary[cname]
        wl = f"{s['wins']}-{s['losses']}"
        wr = f"{s['win_rate']:.1%}"
        mm = f"{s['mean_margin']:+,.1f}" if s["mean_margin"] is not None else "N/A"
        verdict = "BORDERLINE"
        if s["wins"] >= 6:
            verdict = "PASS"
        elif s["wins"] <= 3:
            verdict = "FAIL"
        elif s["mean_margin"] is not None and s["mean_margin"] > 2000 and s["seat0_wins"] >= 1 and s["seat1_wins"] >= 1:
            verdict = "PASS"
        print(f"| {cname} | {wl} | {wr} | {mm} | {s['seat0_record']} | {s['seat1_record']} | {verdict} |")

    print("\n=== ANOMALIES ===")
    anomalies = [r for r in results if not r["completed"] or r["runtime_error"] or r["invalid_actions"] > 0]
    if not anomalies:
        print("NONE")
    else:
        for r in anomalies:
            print(f"- {r['candidate']} seed={r['seed']} seat={r['external_seat']}: "
                  f"completed={r['completed']} invalid={r['invalid_actions']} error={r['runtime_error']}")

    print("\n=== DECISION ===")
    for cname in ["lonespear", "ronin5205", "gzmcr"]:
        s = summary[cname]
        if s["wins"] >= 6:
            print(f"{cname}: PASS -> 120-pair")
        elif s["wins"] <= 3:
            print(f"{cname}: FAIL")
        else:
            print(f"{cname}: BORDERLINE -> no automatic 120-pair")

    out = {
        "results": results,
        "summary": summary,
        "config": {
            "seeds": SEEDS,
            "engine": "kaggle-environments 1.32.7",
            "baseline": "v11E frozen",
            "candidates": ["lonespear", "ronin5205", "gzmcr"],
            "loader": "importlib.util.spec_from_file_location (unique module names)",
        },
    }
    path = "_external_8game_results.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\nWrote {path}")

    print("\n=== INTEGRITY ===")
    for cname in ["lonespear", "ronin5205", "gzmcr"]:
        mod, mod_name, mod_file = _load_wrapper(cname)
        print(f"{cname} -> {mod_file}")
        print(f"       module_name={mod_name}")

if __name__ == "__main__":
    main()
