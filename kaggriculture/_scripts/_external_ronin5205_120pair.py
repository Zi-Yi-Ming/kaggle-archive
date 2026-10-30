# -*- coding: utf-8 -*-
"""Ronin5205 vs v11E: 120-seed × 2-seat = 240-game benchmark.

Fixed loader via importlib.util.spec_from_file_location with unique module names.
No v11E modification. No Ronin5205 modification. Pure benchmark.
"""
import sys, os, json, statistics, math, traceback, importlib.util
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kaggle_environments import make
from _pm_pool import load_agent as load_pool_agent

BASE = os.path.dirname(os.path.abspath(__file__))

# ------------------------------------------------------------------ loaders --
RONIN_KEY = "ronin5205"
RONIN_WRAPPER_PATH = os.path.join(BASE, "_external", "ronin5205", "wrapper.py")
RONIN_MODULE_NAME = "external_ronin5205_wrapper_unique"
V11E_KEY = "v11E"

def load_ronin():
    if not os.path.isfile(RONIN_WRAPPER_PATH):
        raise FileNotFoundError(RONIN_WRAPPER_PATH)
    spec = importlib.util.spec_from_file_location(RONIN_MODULE_NAME, RONIN_WRAPPER_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

# ------------------------------------------------------------------ smoke --
SMOKE_SEEDS = [1, 2]
MIN_STEPS = 50

def _minimal_obs():
    return {
        "farms": [[{"money": 500, "crops": [], "animals": [], "structures": []}]],
        "day": 0,
        "season": 0,
        "year": 1,
        "town": {"shops": []},
        "market": {},
    }

def run_smoke():
    print("=== SMOKE ===")
    mod = load_ronin()
    agent_fn = mod.agent
    mod_name = getattr(mod, "__name__", RONIN_MODULE_NAME)
    mod_file = os.path.abspath(getattr(mod, "__file__", RONIN_WRAPPER_PATH))

    rec = {
        "candidate": RONIN_KEY,
        "module_name": mod_name,
        "module_file": mod_file,
        "load_ok": True,
        "action_ok": False,
        "steps_executed": 0,
        "runtime_error": None,
        "observation_test": None,
    }

    # 1) action schema on synthetic obs
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

    # 2) real game to confirm runtime compatibility + obs/step behavior
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
            # Inspect obs structure at first step to detect step dependency
            first = env.steps[0]
            obs0 = first[0]["observation"]
            obs1 = first[1]["observation"]
            rec["observation_test"] = {
                "seed": seed,
                "obs0_keys": sorted([k for k in obs0.keys() if not k.startswith("_")]),
                "obs1_keys": sorted([k for k in obs1.keys() if not k.startswith("_")]),
                "has_step_key": "step" in obs0,
                "step_value": obs0.get("step"),
            }
        except Exception as e:
            rec["runtime_error"] = f"game crash seed={seed}: {e}"
            return rec

    return rec

# ----------------------------------------------------------- benchmark helpers --
SEEDS = list(range(1, 121))

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
            "turns": len(env.steps),
        }
    except Exception as e:
        return {
            "status": "crash",
            "bank_seat0": None,
            "bank_seat1": None,
            "invalid_actions": 0,
            "sell_failures": 0,
            "error": str(e),
            "turns": len(getattr(e, 'env', {}).get('steps', [])) if False else 0,
        }

# ------------------------------------------------------------------- main ---
def main():
    # ----------------------- smoke -----------------------
    smoke = run_smoke()
    print(f"candidate={smoke['candidate']} module={smoke['module_name']} file={smoke['module_file']}")
    print(f"load_ok={smoke['load_ok']} action_ok={smoke['action_ok']} steps={smoke['steps_executed']} err={smoke['runtime_error']}")
    if smoke["module_file"] != os.path.abspath(RONIN_WRAPPER_PATH):
        print(f"STOP: module file mismatch: {smoke['module_file']}")
        return
    if not smoke["load_ok"] or not smoke["action_ok"] or smoke["runtime_error"] is not None:
        print("STOP: smoke test failed.")
        return

    # ----------------------- benchmark --------------------
    print("\n=== 240-GAME BENCHMARK ===")
    results = []
    ron_mod = load_ronin()
    ron_agent = ron_mod.agent
    for seed in SEEDS:
        v11e = load_pool_agent("v11E")
        # Game A: Ronin5205 seat0, v11E seat1
        resA = run_game(ron_agent, v11e, seed)
        extA = resA["bank_seat0"]
        v11A = resA["bank_seat1"]
        marginA = (extA - v11A) if (extA is not None and v11A is not None) else None
        winnerA = None
        if marginA is not None:
            winnerA = RONIN_KEY if marginA > 0 else ("v11E" if marginA < 0 else "tie")
        recA = {
            "candidate": RONIN_KEY,
            "module_name": ron_mod.__name__,
            "module_file": os.path.abspath(ron_mod.__file__),
            "seed": seed,
            "ronin_seat": 0,
            "v11e_seat": 1,
            "winner": winnerA,
            "ronin_final_bank": extA,
            "v11e_final_bank": v11A,
            "margin": marginA,
            "invalid_actions": resA["invalid_actions"],
            "sell_failures": resA["sell_failures"],
            "completed": resA["status"] == "ok",
            "runtime_error": resA["error"],
            "turns": resA["turns"],
        }
        results.append(recA)
        print(f"{RONIN_KEY} seed={seed} seat=0 -> "
              f"ronin={extA} v11e={v11A} margin={marginA} "
              f"ok={recA['completed']} err={resA['error']}", flush=True)

        # Game B: v11E seat0, Ronin5205 seat1
        v11e = load_pool_agent("v11E")
        resB = run_game(v11e, ron_agent, seed)
        v11B = resB["bank_seat0"]
        extB = resB["bank_seat1"]
        marginB = (extB - v11B) if (extB is not None and v11B is not None) else None
        winnerB = None
        if marginB is not None:
            winnerB = RONIN_KEY if marginB > 0 else ("v11E" if marginB < 0 else "tie")
        recB = {
            "candidate": RONIN_KEY,
            "module_name": ron_mod.__name__,
            "module_file": os.path.abspath(ron_mod.__file__),
            "seed": seed,
            "ronin_seat": 1,
            "v11e_seat": 0,
            "winner": winnerB,
            "ronin_final_bank": extB,
            "v11e_final_bank": v11B,
            "margin": marginB,
            "invalid_actions": resB["invalid_actions"],
            "sell_failures": resB["sell_failures"],
            "completed": resB["status"] == "ok",
            "runtime_error": resB["error"],
            "turns": resB["turns"],
        }
        results.append(recB)
        print(f"{RONIN_KEY} seed={seed} seat=1 -> "
              f"ronin={extB} v11e={v11B} margin={marginB} "
              f"ok={recB['completed']} err={resB['error']}", flush=True)

    # ----------------------- summary ---------------------
    ok = [r for r in results if r["completed"]]
    wins = sum(1 for r in ok if r["margin"] is not None and r["margin"] > 0)
    losses = sum(1 for r in ok if r["margin"] is not None and r["margin"] < 0)
    ties = sum(1 for r in ok if r["margin"] == 0)
    margins = [r["margin"] for r in ok if r["margin"] is not None]
    mean_margin = statistics.mean(margins) if margins else None
    median_margin = statistics.median(margins) if margins else None
    std_margin = statistics.pstdev(margins) if margins else None
    min_margin = min(margins) if margins else None
    max_margin = max(margins) if margins else None
    win_rate = wins / len(ok) if ok else 0

    seat0 = [r for r in ok if r["ronin_seat"] == 0]
    seat1 = [r for r in ok if r["ronin_seat"] == 1]
    seat0_wins = sum(1 for r in seat0 if r["margin"] is not None and r["margin"] > 0)
    seat1_wins = sum(1 for r in seat1 if r["margin"] is not None and r["margin"] > 0)
    seat0_margins = [r["margin"] for r in seat0 if r["margin"] is not None]
    seat1_margins = [r["margin"] for r in seat1 if r["margin"] is not None]

    # Wilson CI for win rate (standard 95%)
    n = len(ok)
    z = 1.959963984540054
    if n > 0 and wins >= 0:
        phat = wins / n
        wilson_center = (phat + (z**2) / (2 * n)) / (1 + (z**2) / n)
        wilson_half = (z * math.sqrt((phat * (1 - phat) + (z**2) / (4 * n)) / n)) / (1 + (z**2) / n)
        wilson_ci = [max(0.0, wilson_center - wilson_half), min(1.0, wilson_center + wilson_half)]
    else:
        wilson_ci = [None, None]

    # Mean margin CI (normal approx, n=240 large enough)
    if mean_margin is not None and std_margin is not None and n > 0:
        margin_se = std_margin / math.sqrt(n)
        margin_ci = [mean_margin - 1.96 * margin_se, mean_margin + 1.96 * margin_se]
    else:
        margin_ci = [None, None]

    # Seed variance: per-seed net margin (seat0 + seat1 for same seed)
    seed_margins = {}
    for r in ok:
        seed_margins.setdefault(r["seed"], []).append(r["margin"])
    seed_net = {s: sum(v) for s, v in seed_margins.items() if len(v) == 2}
    seed_net_margins = list(seed_net.values())
    mean_seed_net = statistics.mean(seed_net_margins) if seed_net_margins else None
    std_seed_net = statistics.pstdev(seed_net_margins) if seed_net_margins else None

    summary = {
        "candidate": RONIN_KEY,
        "engine": "kaggle-environments 1.32.7",
        "baseline": "v11E frozen",
        "loader": "importlib.util.spec_from_file_location (unique module names)",
        "candidate_provenance": {
            "repo_path": os.path.abspath(os.path.join(BASE, "_external", "ronin5205")),
            "wrapper_file": os.path.abspath(RONIN_WRAPPER_PATH),
            "module_name": ron_mod.__name__,
        },
        "smoke": smoke,
        "overall": {
            "games": n,
            "wins": wins,
            "losses": losses,
            "ties": ties,
            "win_rate": win_rate,
            "mean_margin": mean_margin,
            "median_margin": median_margin,
            "std_margin": std_margin,
            "min_margin": min_margin,
            "max_margin": max_margin,
            "win_rate_wilson_ci_95": wilson_ci,
            "mean_margin_ci_95": margin_ci,
        },
        "seat_split": {
            "ronin_seat0": {
                "games": len(seat0),
                "wins": seat0_wins,
                "losses": len(seat0) - seat0_wins - sum(1 for r in seat0 if r["margin"] == 0),
                "ties": sum(1 for r in seat0 if r["margin"] == 0),
                "win_rate": seat0_wins / len(seat0) if seat0 else 0,
                "mean_margin": statistics.mean(seat0_margins) if seat0_margins else None,
                "median_margin": statistics.median(seat0_margins) if seat0_margins else None,
            },
            "ronin_seat1": {
                "games": len(seat1),
                "wins": seat1_wins,
                "losses": len(seat1) - seat1_wins - sum(1 for r in seat1 if r["margin"] == 0),
                "ties": sum(1 for r in seat1 if r["margin"] == 0),
                "win_rate": seat1_wins / len(seat1) if seat1 else 0,
                "mean_margin": statistics.mean(seat1_margins) if seat1_margins else None,
                "median_margin": statistics.median(seat1_margins) if seat1_margins else None,
            },
        },
        "seed_variance": {
            "seed_net_margins_mean": mean_seed_net,
            "seed_net_margins_std": std_seed_net,
            "seed_net_margins_min": min(seed_net_margins) if seed_net_margins else None,
            "seed_net_margins_max": max(seed_net_margins) if seed_net_margins else None,
        },
        "runtime_stats": {
            "total_runtime_errors": sum(1 for r in results if r["runtime_error"] is not None),
            "total_invalid_actions": sum(r["invalid_actions"] for r in ok),
            "games_with_invalid_actions": sum(1 for r in ok if r["invalid_actions"] > 0),
        },
        "step_dependency": smoke.get("observation_test", {}).get("has_step_key", "UNKNOWN"),
        "verdict": None,
        "anomalies": [],
    }

    # Anomalies
    anomalies = [r for r in results if not r["completed"] or r["runtime_error"] or r["invalid_actions"] > 0]
    if anomalies:
        summary["anomalies"] = anomalies

    # Verdict logic
    if wins >= 120:
        summary["verdict"] = "PASS"
    elif wins <= 80:
        summary["verdict"] = "FAIL"
    else:
        # BORDERLINE zone 81-119
        if mean_margin is not None and mean_margin > 0 and std_margin is not None and mean_margin / (std_margin + 1e-9) > 0.15:
            summary["verdict"] = "BORDERLINE"
        else:
            summary["verdict"] = "FAIL"

    # Save results
    results_path = "_external_ronin5205_120pair_results.json"
    summary_path = "_external_ronin5205_120pair_summary.md"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump({
            "results": results,
            "summary": summary,
            "config": {
                "seeds": SEEDS,
                "engine": "kaggle-environments 1.32.7",
                "baseline": "v11E frozen",
                "candidate": RONIN_KEY,
                "loader": "importlib.util.spec_from_file_location (unique module names)",
            },
        }, f, ensure_ascii=False, indent=2)

    # Write markdown summary
    md = []
    md.append("# Ronin5205 120-Pair Benchmark Summary\n")
    md.append(f"**Date:** 2026-09-11  ")
    md.append(f"**Engine:** kaggle-environments 1.32.7  ")
    md.append(f"**Baseline:** v11E frozen  ")
    md.append(f"**Candidate:** {RONIN_KEY}  ")
    md.append(f"**Repo:** `{os.path.abspath(os.path.join(BASE, '_external', 'ronin5205'))}`  ")
    md.append(f"**Wrapper:** `{os.path.abspath(RONIN_WRAPPER_PATH)}`  ")
    md.append(f"**Module name:** `{ron_mod.__name__}`\n")
    md.append("## Experiment Configuration\n")
    md.append("- Seeds: 1-120 (n=120 independent seeds)  ")
    md.append("- 2 games per seed (Ronin5205 seat0 vs v11E seat1; v11E seat0 vs Ronin5205 seat1)  ")
    md.append("- Total games: 240  ")
    md.append("- Episode steps: 720  ")
    md.append("- Loader: importlib.util.spec_from_file_location with unique module names\n")
    md.append("## Smoke Test\n")
    md.append(f"- load_ok: {smoke['load_ok']}  ")
    md.append(f"- action_ok: {smoke['action_ok']}  ")
    md.append(f"- steps_executed: {smoke['steps_executed']}  ")
    md.append(f"- runtime_error: {smoke['runtime_error']}  ")
    md.append(f"- observation_test: {smoke.get('observation_test')}\n")
    md.append("## Overall\n")
    md.append(f"- games = {n}  ")
    md.append(f"- Ronin5205 wins = {wins}  ")
    md.append(f"- v11E wins = {losses}  ")
    md.append(f"- ties = {ties}  ")
    md.append(f"- win rate = {win_rate:.4%}  ")
    md.append(f"- 95% Wilson CI = [{wilson_ci[0]:.4%}, {wilson_ci[1]:.4%}]  ")
    md.append(f"- mean margin = {mean_margin:+,.2f}  ")
    md.append(f"- median margin = {median_margin:+,.2f}  ")
    md.append(f"- std margin = {std_margin:+,.2f}  ")
    md.append(f"- min margin = {min_margin:+,.2f}  ")
    md.append(f"- max margin = {max_margin:+,.2f}  ")
    md.append(f"- 95% mean-margin CI = [{margin_ci[0]:+,.2f}, {margin_ci[1]:+,.2f}]\n")
    md.append("## Seat Split\n")
    s0 = summary["seat_split"]["ronin_seat0"]
    s1 = summary["seat_split"]["ronin_seat1"]
    md.append(f"### Ronin5205 seat 0 (n={s0['games']})  ")
    md.append(f"- W-L-T = {s0['wins']}-{s0['losses']}-{s0['ties']}  ")
    md.append(f"- win_rate = {s0['win_rate']:.4%}  ")
    md.append(f"- mean margin = {s0['mean_margin']:+,.2f}  ")
    md.append(f"- median margin = {s0['median_margin']:+,.2f}\n")
    md.append(f"### Ronin5205 seat 1 (n={s1['games']})  ")
    md.append(f"- W-L-T = {s1['wins']}-{s1['losses']}-{s1['ties']}  ")
    md.append(f"- win_rate = {s1['win_rate']:.4%}  ")
    md.append(f"- mean margin = {s1['mean_margin']:+,.2f}  ")
    md.append(f"- median margin = {s1['median_margin']:+,.2f}\n")
    md.append("## Seed Variance\n")
    md.append(f"- seed-net-margin mean = {mean_seed_net:+,.2f}  ")
    md.append(f"- seed-net-margin std = {std_seed_net:+,.2f}  ")
    md.append(f"- seed-net-margin min = {min(seed_net_margins):+,.2f}  ")
    md.append(f"- seed-net-margin max = {max(seed_net_margins):+,.2f}\n")
    md.append("## Runtime / Invalid-Action Statistics\n")
    md.append(f"- total_runtime_errors = {summary['runtime_stats']['total_runtime_errors']}  ")
    md.append(f"- total_invalid_actions = {summary['runtime_stats']['total_invalid_actions']}  ")
    md.append(f"- games_with_invalid_actions = {summary['runtime_stats']['games_with_invalid_actions']}\n")
    md.append(f"## STEP_DEPENDENCY = {summary['step_dependency']}\n")
    md.append("## Final Verdict\n")
    md.append(f"**{summary['verdict']}**\n")
    if summary["verdict"] == "PASS":
        md.append("Ronin5205 demonstrates a clear and statistically meaningful advantage over v11E.\n")
    elif summary["verdict"] == "FAIL":
        md.append("Ronin5205 does not demonstrate a meaningful advantage over v11E.\n")
    else:
        md.append("Ronin5205 is competitive with v11E but the advantage is not decisive.\n")

    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    print("\n=== FINAL SUMMARY ===")
    print(f"games={n} wins={wins} losses={losses} ties={ties} win_rate={win_rate:.2%}")
    print(f"mean_margin={mean_margin:+,.2f} median={median_margin:+,.2f} std={std_margin:+,.2f}")
    print(f"Wilson CI=[{wilson_ci[0]:.2%}, {wilson_ci[1]:.2%}]")
    print(f"margin CI=[{margin_ci[0]:+,.2f}, {margin_ci[1]:+,.2f}]")
    print(f"seat0={s0['wins']}-{s0['losses']}-{s0['ties']} seat1={s1['wins']}-{s1['losses']}-{s1['ties']}")
    print(f"runtime_errors={summary['runtime_stats']['total_runtime_errors']} invalid_actions={summary['runtime_stats']['total_invalid_actions']}")
    print(f"STEP_DEPENDENCY={summary['step_dependency']}")
    print(f"Verdict={summary['verdict']}")
    print(f"Wrote {results_path}")
    print(f"Wrote {summary_path}")

if __name__ == "__main__":
    main()
