# -*- coding: utf-8 -*-
"""8-game paired head-to-head benchmark: 3 external candidates vs v11E.

Seeds 1-4, both seats. Engine kaggle-environments 1.32.7.
"""
import sys, os, json, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kaggle_environments import make
from _pm_pool import load_agent as load_pool_agent

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_external", "lonespear"))
import wrapper as ls_wrapper
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_external", "ronin5205"))
import wrapper as ron_wrapper
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_external", "gzmcr"))
import wrapper as gz_wrapper

SEEDS = [1, 2, 3, 4]

CANDIDATES = {
    "lonespear": (lambda: ls_wrapper.agent, ls_wrapper.reset),
    "ronin5205": (lambda: ron_wrapper.agent, ron_wrapper.reset),
    "gzmcr": (lambda: gz_wrapper.agent, gz_wrapper.reset),
}

def run_game(agent0, agent1, seed):
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    try:
        env.run([agent0, agent1])
        fin = env.steps[-1]
        obs0 = fin[0]["observation"]
        obs1 = fin[1]["observation"]
        b0 = obs0["farms"][0]["money"]
        b1 = obs1["farms"][1]["money"]
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
        import traceback
        traceback.print_exc()
        return {
            "status": "crash",
            "bank_seat0": None,
            "bank_seat1": None,
            "invalid_actions": 0,
            "sell_failures": 0,
            "error": str(e),
        }

def main():
    results = []
    for cname, (loader, reset_fn) in CANDIDATES.items():
        for seed in SEEDS:
            for external_seat in [0, 1]:
                if reset_fn:
                    reset_fn()
                v11e = load_pool_agent("v11E")
                ext = loader()
                if external_seat == 0:
                    res = run_game(ext, v11e, seed)
                    ext_bank = res["bank_seat0"]
                    v11e_bank = res["bank_seat1"]
                else:
                    res = run_game(v11e, ext, seed)
                    v11e_bank = res["bank_seat0"]
                    ext_bank = res["bank_seat1"]
                margin = (ext_bank - v11e_bank) if (ext_bank is not None and v11e_bank is not None) else None
                rec = {
                    "candidate": cname,
                    "seed": seed,
                    "external_seat": external_seat,
                    "v11e_seat": 1 - external_seat,
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

    summary = {}
    for cname in CANDIDATES:
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
    for cname in CANDIDATES:
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
    for cname in CANDIDATES:
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
            "candidates": list(CANDIDATES.keys()),
        }
    }
    path = "_external_8game_results.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\nWrote {path}")

if __name__ == "__main__":
    main()
