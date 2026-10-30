# -*- coding: utf-8 -*-
"""Head-to-head smoke: v11E vs each external candidate.

8 games per candidate (seeds 1-4, both seats).
Same seeds/seats across matchups for fair comparison.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kaggle_environments import make
from _pm_pool import load_agent as load_pool_agent
from reference_agents.closer_cleo import agent as closer_cleo_agent

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_external", "sey_v21"))
import wrapper as seya_wrapper
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_external", "gytdrop_v5"))
import wrapper as gyt_wrapper
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_external", "cok_v10"))
import wrapper as cok_wrapper

SEEDS = [1, 2, 3, 4]
SEATS = [0, 1]  # 0 = v11E first, 1 = candidate first

CANDIDATES = {
    "sey_v21": (lambda: seya_wrapper.agent, seya_wrapper.reset),
    "gyt_v5": (lambda: gyt_wrapper.agent, gyt_wrapper.reset),
    "cok_v10": (lambda: cok_wrapper.agent, cok_wrapper.reset),
}

def run_game(agent_a, agent_b, seed, seat_a_first):
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    a0, a1 = (agent_a, agent_b) if seat_a_first else (agent_b, agent_a)
    try:
        env.run([a0, a1])
        fin = env.steps[-1]
        b0 = fin[0]["observation"]["farms"][0]["money"]
        b1 = fin[1]["observation"]["farms"][1]["money"]
        if seat_a_first:
            return {"status": "ok", "bank_v11e": b0, "bank_opp": b1, "v11e_win": 1 if b0 > b1 else (0 if b1 > b0 else "tie")}
        else:
            return {"status": "ok", "bank_v11e": b1, "bank_opp": b0, "v11e_win": 1 if b1 > b0 else (0 if b0 > b1 else "tie")}
    except Exception as e:
        return {"status": "crash", "error": str(e), "bank_v11e": None, "bank_opp": None, "v11e_win": None}

def main():
    results = []
    for cname, (loader, reset_fn) in CANDIDATES.items():
        for seed in SEEDS:
            for seat in SEATS:
                if reset_fn:
                    reset_fn()
                v11e_agent = load_pool_agent("v11E")
                cand_agent = loader()
                res = run_game(v11e_agent, cand_agent, seed, seat == 0)
                res["candidate"] = cname
                res["seed"] = seed
                res["seat_v11e_first"] = (seat == 0)
                results.append(res)
                print(f"v11E vs {cname} seed={seed} v11e_first={seat==0} -> {res}", flush=True)

    print("\n=== HEAD-TO-HEAD SUMMARY ===")
    for cname in CANDIDATES:
        subset = [r for r in results if r["candidate"] == cname]
        n = len(subset)
        ok = sum(1 for r in subset if r["status"] == "ok")
        crash = sum(1 for r in subset if r["status"] == "crash")
        v11e_wins = sum(1 for r in subset if r["v11e_win"] == 1)
        cand_wins = sum(1 for r in subset if r["v11e_win"] == 0)
        ties = sum(1 for r in subset if r["v11e_win"] == "tie")
        margins = [r["bank_v11e"] - r["bank_opp"] for r in subset if r["status"] == "ok"]
        avg_margin = sum(margins) / len(margins) if margins else 0
        print(f"v11E vs {cname}: n={n} ok={ok} crash={crash} v11e_W={v11e_wins} cand_W={cand_wins} T={ties} avg_margin(v11e-cand)={avg_margin:+.1f}")

    with open("_external_vs_v11e_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
