# -*- coding: utf-8 -*-
"""Top-5 candidate smoke test + 16-game screening vs v11E.

Uses importlib.util.spec_from_file_location with unique module names
to avoid Python module-caching collisions.
"""
import sys
import os
import json
import math
import statistics
import traceback
import importlib.util
import types

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kaggle_environments import make
from _pm_pool import load_agent as load_pool_agent

# ------------------------------------------------------------------ config --
SCREEN_SEEDS = list(range(1, 9))          # 1..8
SMOKE_SEEDS = [1, 2]
MIN_STEPS = 50
Z_WILSON = 1.959963984540054              # 95% CI

# ------------------------------------------------------------------ candidates --
BASE = os.path.dirname(os.path.abspath(__file__))
EXT = os.path.join(BASE, "_external")

CANDIDATES = {
    "tetsu2131": {
        "module_file": os.path.join(EXT, "top5_notebooks", "tetsu2131", "wrapper.py"),
        "agent_name": "agent",
    },
    "prvsiyan": {
        "module_file": os.path.join(EXT, "top5_notebooks", "prvsiyan", "wrapper.py"),
        "agent_name": "agent",
    },
    "flexonafft": {
        "module_file": os.path.join(EXT, "top5_notebooks", "flexonafft", "wrapper.py"),
        "agent_name": "agent",
    },
    "salemali7": {
        "module_file": os.path.join(EXT, "top5_notebooks", "salemali7", "wrapper.py"),
        "agent_name": "agent",
    },
    "boatlee": {
        "module_file": os.path.join(EXT, "top5_notebooks", "boatlee", "wrapper.py"),
        "status": "BLOCKED_NO_ENTRY_POINT",
    },
}

# ------------------------------------------------------------------ helpers --
def _load_candidate_module(name, cfg):
    path = cfg["module_file"]
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    spec = importlib.util.spec_from_file_location(f"cand_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def _load_opponent():
    return load_pool_agent("v11E")

def _run_game(seed, cand_agent, opp_agent, cand_seat):
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    if cand_seat == 0:
        agents = [cand_agent, opp_agent]
    else:
        agents = [opp_agent, cand_agent]
    env.run(agents)
    steps = env.steps
    total_steps = len(steps)
    final = steps[-1]
    obs0 = final[0]["observation"]
    obs1 = final[1]["observation"]
    bank0 = obs0["farms"][0]["money"]
    bank1 = obs1["farms"][1]["money"]
    if cand_seat == 0:
        cand_bank = bank0
        opp_bank = bank1
        margin = bank0 - bank1
        winner = 0 if bank0 > bank1 else (1 if bank1 > bank0 else -1)
        first_obs = steps[1][0]["observation"] if total_steps > 1 else obs0
    else:
        cand_bank = bank1
        opp_bank = bank0
        margin = bank1 - bank0
        winner = 1 if bank1 > bank0 else (0 if bank0 > bank1 else -1)
        first_obs = steps[1][1]["observation"] if total_steps > 1 else obs1
    completed = all(s.get("status") in ("OK", "DONE") for s in final)
    runtime_error = next((s.get("error") for s in final if s.get("error")), None)
    return {
        "seed": seed,
        "cand_seat": cand_seat,
        "cand_bank": cand_bank,
        "opp_bank": opp_bank,
        "margin": margin,
        "winner": winner,
        "completed": completed,
        "runtime_error": runtime_error,
        "total_steps": total_steps,
        "observation": first_obs,
    }

# ------------------------------------------------------------------ smoke --
def run_smoke(name, cfg):
    rec = {
        "candidate": name,
        "module_file": cfg["module_file"],
        "load_ok": False,
        "action_ok": False,
        "steps_executed": 0,
        "runtime_error": None,
    }
    try:
        mod = _load_candidate_module(name, cfg)
        rec["load_ok"] = True
    except Exception as e:
        rec["runtime_error"] = f"load failed: {e}"
        return rec
    agent_fn = getattr(mod, cfg.get("agent_name", "agent"))
    opp = _load_opponent()
    for seed in SMOKE_SEEDS:
        try:
            res = _run_game(seed, agent_fn, opp, 0)
            rec["steps_executed"] = max(rec["steps_executed"], res["total_steps"])
            if not res["completed"] or res["runtime_error"]:
                rec["runtime_error"] = f"game crash seed={seed}: status={res['runtime_error']}"
                return rec
            action = agent_fn(res.get("observation"))
            if isinstance(action, dict):
                rec["action_ok"] = all(k in action for k in ("farmer", "hands", "market"))
            else:
                rec["runtime_error"] = f"action is {type(action).__name__}, not dict"
                return rec
        except Exception as e:
            rec["runtime_error"] = f"game crash seed={seed}: {e}"
            return rec
    return rec

# ------------------------------------------------------------------ screen --
def run_screen(name, cfg):
    opp = _load_opponent()
    mod = _load_candidate_module(name, cfg)
    agent_fn = getattr(mod, cfg.get("agent_name", "agent"))
    games = []
    for seat in (0, 1):
        for seed in SCREEN_SEEDS:
            try:
                g = _run_game(seed, agent_fn, opp, seat)
                g["candidate"] = name
                g["module_file"] = cfg["module_file"]
                games.append(g)
            except Exception as e:
                games.append({
                    "candidate": name,
                    "module_file": cfg["module_file"],
                    "seed": seed,
                    "cand_seat": seat,
                    "runtime_error": str(e),
                    "completed": False,
                })
    return games

def summarize_screen(name, games):
    wins = losses = ties = 0
    margins = []
    seat0_wins = seat0_losses = seat0_ties = 0
    seat1_wins = seat1_losses = seat1_ties = 0
    completed = 0
    for g in games:
        if not g.get("completed"):
            continue
        completed += 1
        m = g["margin"]
        margins.append(m)
        seat = g["cand_seat"]
        w = g["winner"]
        if w == -1:
            ties += 1
            if seat == 0:
                seat0_ties += 1
            else:
                seat1_ties += 1
        elif w == seat:
            wins += 1
            if seat == 0:
                seat0_wins += 1
            else:
                seat1_wins += 1
        else:
            losses += 1
            if seat == 0:
                seat0_losses += 1
            else:
                seat1_losses += 1
    n = completed
    wr = wins / n if n else 0.0
    mean_m = statistics.mean(margins) if margins else 0.0
    median_m = statistics.median(margins) if margins else 0.0
    std_m = statistics.pstdev(margins) if len(margins) > 1 else 0.0
    ci_lo = wr - Z_WILSON * math.sqrt(wr * (1 - wr) / n) if n else 0.0
    ci_hi = wr + Z_WILSON * math.sqrt(wr * (1 - wr) / n) if n else 0.0
    # verdict
    if wins >= 10 or (wins == 9 and mean_m > 500):
        verdict = "ADVANCE"
    elif wins == 8 or (wins == 9 and mean_m <= 500):
        verdict = "BORDERLINE"
    elif wins <= 7 or mean_m < 0:
        verdict = "FAIL"
    else:
        verdict = "BORDERLINE"
    # seat bias check
    seat0_total = seat0_wins + seat0_losses + seat0_ties
    seat1_total = seat1_wins + seat1_losses + seat1_ties
    seat0_wr = seat0_wins / seat0_total if seat0_total else 0.0
    seat1_wr = seat1_wins / seat1_total if seat1_total else 0.0
    seat_bias = abs(seat0_wr - seat1_wr) > 0.2
    if seat_bias:
        verdict = "FAIL"
    return {
        "candidate": name,
        "verdict": verdict,
        "completed_games": n,
        "wins": wins,
        "losses": losses,
        "ties": ties,
        "win_rate": wr,
        "wilson_ci_lo": ci_lo,
        "wilson_ci_hi": ci_hi,
        "mean_margin": mean_m,
        "median_margin": median_m,
        "std_margin": std_m,
        "seat0_wins": seat0_wins,
        "seat0_losses": seat0_losses,
        "seat0_ties": seat0_ties,
        "seat0_wr": seat0_wr,
        "seat1_wins": seat1_wins,
        "seat1_losses": seat1_losses,
        "seat1_ties": seat1_ties,
        "seat1_wr": seat1_wr,
        "seat_bias": seat_bias,
    }

# ------------------------------------------------------------------ main --
def main():
    results = []
    screen_results = []
    summaries = []
    for name, cfg in CANDIDATES.items():
        print(f"\n=== {name} ===", flush=True)
        if cfg.get("status") == "BLOCKED_NO_CHECKPOINT":
            print(f"[{name}] BLOCKED: no trained checkpoint found.")
            results.append({"candidate": name, "status": "BLOCKED_NO_CHECKPOINT"})
            continue
        if cfg.get("status") == "BLOCKED_NO_ENTRY_POINT":
            print(f"[{name}] BLOCKED: no agent entry point found.")
            results.append({"candidate": name, "status": "BLOCKED_NO_ENTRY_POINT"})
            continue
        # smoke
        smoke = run_smoke(name, cfg)
        results.append(smoke)
        print(f"[{name}] smoke: load_ok={smoke['load_ok']} action_ok={smoke['action_ok']} steps={smoke['steps_executed']}")
        if smoke["runtime_error"]:
            print(f"[{name}] SMOKE FAILED: {smoke['runtime_error']}")
            continue
        # 16-game screen
        games = run_screen(name, cfg)
        screen_results.extend(games)
        summary = summarize_screen(name, games)
        summaries.append(summary)
        print(f"[{name}] screen: {summary['wins']}-{summary['losses']}-{summary['ties']} "
              f"WR={summary['win_rate']:.2%} mean_margin={summary['mean_margin']:.1f} "
              f"verdict={summary['verdict']}")
    # write JSON
    out = {
        "smoke": results,
        "games": screen_results,
        "summaries": summaries,
    }
    out_path = os.path.join(BASE, "_external_top5_16game_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\nJSON written: {out_path}")
    # write markdown summary
    md_path = os.path.join(BASE, "_external_top5_16game_summary.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Top-5 External Candidate 16-Game Screening\n\n")
        f.write("## Blocked / Pre-check\n\n")
        f.write("| Candidate | Status | Reason |\n")
        f.write("|-----------|--------|--------|\n")
        for r in results:
            if r.get("status"):
                f.write(f"| {r['candidate']} | {r['status']} | see notes |\n")
        f.write("\n## Smoke Results\n\n")
        f.write("| Candidate | Load OK | Action OK | Steps | Error |\n")
        f.write("|-----------|---------|-----------|-------|-------|\n")
        for r in results:
            if r.get("status"):
                continue
            f.write(f"| {r['candidate']} | {r['load_ok']} | {r['action_ok']} | {r['steps_executed']} | {r['runtime_error'] or '-'} |\n")
        f.write("\n## 16-Game Summary\n\n")
        f.write("| Candidate | Verdict | W-L-T | WR | 95% CI | Mean Margin | Seat0 WR | Seat1 WR | Seat Bias |\n")
        f.write("|-----------|---------|-------|----|--------|-------------|----------|----------|-----------|\n")
        for s in summaries:
            f.write(f"| {s['candidate']} | {s['verdict']} | {s['wins']}-{s['losses']}-{s['ties']} | "
                    f"{s['win_rate']:.2%} | [{s['wilson_ci_lo']:.2%}, {s['wilson_ci_hi']:.2%}] | "
                    f"{s['mean_margin']:.1f} | {s['seat0_wr']:.2%} | {s['seat1_wr']:.2%} | "
                    f"{'YES' if s['seat_bias'] else 'no'} |\n")
        f.write("\n## Individual Games\n\n")
        for g in screen_results:
            status = "completed" if g.get("completed") else f"ERROR: {g.get('runtime_error')}"
            f.write(f"- **{g['candidate']}** seed={g['seed']} seat={g['cand_seat']}: "
                    f"cand={g.get('cand_bank', '?')} opp={g.get('opp_bank', '?')} "
                    f"margin={g.get('margin', '?')} winner={g.get('winner', '?')} "
                    f"status={status}\n")
        f.write("\n## Decision\n\n")
        advance = [s["candidate"] for s in summaries if s["verdict"] == "ADVANCE"]
        borderline = [s["candidate"] for s in summaries if s["verdict"] == "BORDERLINE"]
        fail = [s["candidate"] for s in summaries if s["verdict"] == "FAIL"]
        blocked = [r["candidate"] for r in results if r.get("status")]
        f.write(f"- **ADVANCE**: {', '.join(advance) if advance else 'none'}\n")
        f.write(f"- **BORDERLINE**: {', '.join(borderline) if borderline else 'none'}\n")
        f.write(f"- **FAIL**: {', '.join(fail) if fail else 'none'}\n")
        f.write(f"- **BLOCKED**: {', '.join(blocked) if blocked else 'none'}\n")
    print(f"Markdown written: {md_path}")

if __name__ == "__main__":
    main()
