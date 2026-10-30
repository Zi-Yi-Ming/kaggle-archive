# -*- coding: utf-8 -*-
"""P50 Stage1: SELL-only ±1 mutations on elite R2 tape, H2H vs opponent pool."""
from __future__ import annotations

import copy
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

FINN = ROOT / "reference_agents" / "fallow_finn.py"
OPPONENTS = {
    "finn": FINN,
    "R2": ROOT / "_push_medal" / "main.py",
    "V16": ROOT / "_external" / "p41_extracted" / "salem_2900_main.py",
    "kaito_v27": ROOT / "_external" / "public_nb" / "kaito_v27" / "main.py",
}
SEEDS = (1, 2, 3)
REP = ROOT / "_external" / "p42_replays"
SELL_ITEMS = ("FERTILIZER", "WOOL", "MILK", "MELON", "STRAWBERRY", "EGG")


def load_agent(path, tag):
    spec = importlib.util.spec_from_file_location(tag, str(path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent if hasattr(m, "agent") else m.build_agent({})


def load_base_tape():
    """Highest live-reward R2 episode as elite trajectory."""
    meta = json.loads((REP / "meta.json").read_text(encoding="utf-8"))
    meta = [m for m in meta if m.get("our_reward") is not None]
    meta.sort(key=lambda m: -m["our_reward"])
    best = meta[0]
    d = json.loads(Path(best["path"]).read_text(encoding="utf-8"))
    seat = int(best.get("our_seat") or 0)
    tape = []
    for step in d["steps"]:
        a = step[seat].get("action") or {}
        tape.append({
            "market": a.get("market") or [],
            "farmer": a.get("farmer") or ["PASS"],
            "hands": a.get("hands") or [],
        })
    assert len(tape) == 720
    return tape, best


def find_first_sell(tape, item):
    for t, a in enumerate(tape):
        for o in a.get("market") or []:
            if o and o[0] == "SELL" and len(o) >= 3 and o[1] == item:
                return t
    return None


def shift_first_sell(tape, item, delta):
    t0 = find_first_sell(tape, item)
    if t0 is None:
        return None, []
    t1 = t0 + delta
    if t1 < 0 or t1 >= 720 or t1 == t0:
        return None, []
    new = copy.deepcopy(tape)
    moved = None
    mk0 = []
    for o in new[t0]["market"]:
        if moved is None and o and o[0] == "SELL" and len(o) >= 3 and o[1] == item:
            moved = list(o)
            continue
        mk0.append(o)
    if moved is None:
        return None, []
    new[t0]["market"] = mk0
    mk1 = list(new[t1]["market"])
    merged = False
    for o in mk1:
        if o and o[0] == "SELL" and len(o) >= 3 and o[1] == item:
            o[2] = int(o[2]) + int(moved[2])
            merged = True
            break
    if not merged:
        if len(mk1) >= 10:
            return None, []
        mk1.append(moved)
    new[t1]["market"] = mk1
    return new, [t0, t1]


def tape_agent(tape):
    def agent(observation, configuration=None):
        step = int((observation or {}).get("step") or 0)
        step = max(0, min(719, step))
        a = tape[step]
        return {"farmer": a["farmer"], "hands": a["hands"], "market": a["market"]}
    return agent


def run_pair(a0, a1, seed):
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    env.run([a0, a1])
    f = env.steps[-1]
    return (
        float(f[0]["observation"]["farms"][0]["money"]),
        float(f[1]["observation"]["farms"][1]["money"]),
    )


def eval_candidate_vs_pool(tape, seeds, opp_names):
    """Double-seat vs each opponent. Returns per-opp WDL and overall."""
    per_opp = {}
    all_rows = []
    for oname in opp_names:
        path = OPPONENTS[oname]
        w = d = l = 0
        banks = []
        for seed in seeds:
            # seat0: us, opp
            us0 = tape_agent(tape)
            opp0 = load_agent(path, f"p50o_{oname}_{seed}_0")
            b0, b1 = run_pair(us0, opp0, seed)
            # seat1: opp, us
            opp1 = load_agent(path, f"p50o_{oname}_{seed}_1")
            us1 = tape_agent(tape)
            c0, c1 = run_pair(opp1, us1, seed)
            our = (b0 + c1) / 2
            theirs = (b1 + c0) / 2
            banks.append(our)
            if our > theirs + 1:
                w += 1
                res = "W"
            elif theirs > our + 1:
                l += 1
                res = "L"
            else:
                d += 1
                res = "D"
            all_rows.append({
                "opponent": oname, "seed": seed,
                "our_mean": our, "opp_mean": theirs, "result": res,
            })
        per_opp[oname] = {
            "W": w, "D": d, "L": l, "W-L": w - l,
            "bank_mean": statistics.mean(banks) if banks else 0,
        }
    # aggregate WDL
    W = sum(x["W"] for x in per_opp.values())
    D = sum(x["D"] for x in per_opp.values())
    L = sum(x["L"] for x in per_opp.values())
    # BT proxy: win rate vs pool (ties = 0.5)
    games = W + D + L
    bt_proxy = (W + 0.5 * D) / games if games else 0
    return {
        "W": W, "D": D, "L": L, "W-L": W - L,
        "bt_proxy": bt_proxy,
        "per_opp": per_opp,
        "rows": all_rows,
    }


def main():
    t0 = time.time()
    tape, src = load_base_tape()
    print(f"base tape from ep={src['episode_id']} live_reward={src['our_reward']} "
          f"opp={src.get('opp_team')}", flush=True)

    opps = list(OPPONENTS.keys())
    print(f"opponent pool: {opps}", flush=True)

    # baseline
    print("\n=== BASELINE tape ===", flush=True)
    base = eval_candidate_vs_pool(tape, SEEDS, opps)
    print(f"BASE W-D-L {base['W']}-{base['D']}-{base['L']} W-L={base['W-L']} "
          f"bt={base['bt_proxy']:.3f}", flush=True)
    for o, s in base["per_opp"].items():
        print(f"  vs {o}: {s['W']}-{s['D']}-{s['L']} bank={s['bank_mean']:.0f}", flush=True)

    candidates = [("c00_baseline", tape, [], "none")]
    for item in SELL_ITEMS:
        t0s = find_first_sell(tape, item)
        if t0s is None:
            print(f"  SKIP {item}: no SELL", flush=True)
            continue
        for dlt in (-1, 1):
            nt, ch = shift_first_sell(tape, item, dlt)
            if nt is None:
                print(f"  SKIP {item} {dlt:+d}: cannot shift", flush=True)
                continue
            cid = f"c_{item.lower()}_d{dlt:+d}"
            candidates.append((cid, nt, ch, f"shift_first_{item}_{dlt:+d}"))
    print(f"n_candidates={len(candidates)}", flush=True)

    results = []
    all_h2h = []
    for cid, ctape, ch, mut in candidates:
        print(f"\n=== {cid} {mut} ===", flush=True)
        if cid == "c00_baseline":
            r = base
        else:
            r = eval_candidate_vs_pool(ctape, SEEDS, opps)
        r["id"] = cid
        r["mutation"] = mut
        r["changed"] = ch
        results.append(r)
        all_h2h.extend([{**row, "candidate": cid} for row in r["rows"]])
        print(f"  W-D-L {r['W']}-{r['D']}-{r['L']} W-L={r['W-L']} bt={r['bt_proxy']:.3f}", flush=True)

    # ranking
    results.sort(key=lambda r: (-r["W-L"], -r["bt_proxy"]))
    print("\n=== RANKING ===", flush=True)
    base_r = next(r for r in results if r["id"] == "c00_baseline")
    for r in results:
        print(f"  {r['id']:24s} W-L={r['W-L']:4d} bt={r['bt_proxy']:.3f} {r['mutation']}", flush=True)

    best = results[0]
    # cross-seed / cross-opponent improvement vs baseline
    wl_up = best["W-L"] > base_r["W-L"]
    bt_up = best["bt_proxy"] > base_r["bt_proxy"] + 1e-6
    # per-opp: must improve on majority of opponents, not just finn
    n_opp_better = 0
    n_opp = 0
    for o in opps:
        n_opp += 1
        if best["per_opp"][o]["W-L"] > base_r["per_opp"][o]["W-L"]:
            n_opp_better += 1
    # bank consistency
    bank_up = False
    if best["id"] != "c00_baseline":
        # mean bank across all rows
        bb = statistics.mean([r["our_mean"] for r in best["rows"]])
        base_b = statistics.mean([r["our_mean"] for r in base_r["rows"]])
        bank_up = bb > base_b + 500

    print(f"\nbest={best['id']} W-L={best['W-L']} vs base {base_r['W-L']}", flush=True)
    print(f"wl_up={wl_up} bt_up={bt_up} n_opp_better={n_opp_better}/{n_opp} bank_up={bank_up}", flush=True)

    # decision enum
    if best["id"] == "c00_baseline" or (not wl_up and not bt_up):
        if bank_up and not wl_up:
            decision = "P50_BANK_ONLY_NO_ELO"
        else:
            decision = "P50_STAGE1_NO_SIGNAL"
    elif wl_up and n_opp_better >= 2 and best["W"] >= base_r["W"]:
        # check not single-seed: count seeds where best beats base on avg
        decision = "P50_STAGE1_PASS"
    elif wl_up and n_opp_better <= 1:
        decision = "P50_SEED_OR_OPPONENT_SPECIFIC"
    else:
        decision = "P50_STAGE1_NO_SIGNAL"

    # refine: if only finn improves
    if decision == "P50_STAGE1_PASS" and best["per_opp"]["finn"]["W-L"] > base_r["per_opp"]["finn"]["W-L"]:
        elite_improve = sum(
            1 for o in opps if o != "finn"
            and best["per_opp"][o]["W-L"] > base_r["per_opp"][o]["W-L"]
        )
        if elite_improve == 0:
            decision = "P50_SEED_OR_OPPONENT_SPECIFIC"

    print(f"P50_DECISION={decision}", flush=True)

    # write
    with open(ROOT / "p50_candidates.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "id", "mutation", "changed", "W", "D", "L", "W-L", "bt_proxy",
            "vs_finn_WL", "vs_R2_WL", "vs_V16_WL", "vs_kaito_WL",
        ])
        w.writeheader()
        for r in results:
            w.writerow({
                "id": r["id"], "mutation": r["mutation"],
                "changed": "|".join(map(str, r["changed"])),
                "W": r["W"], "D": r["D"], "L": r["L"], "W-L": r["W-L"],
                "bt_proxy": r["bt_proxy"],
                "vs_finn_WL": r["per_opp"]["finn"]["W-L"],
                "vs_R2_WL": r["per_opp"]["R2"]["W-L"],
                "vs_V16_WL": r["per_opp"]["V16"]["W-L"],
                "vs_kaito_WL": r["per_opp"]["kaito_v27"]["W-L"],
            })

    with open(ROOT / "p50_h2h.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(all_h2h[0].keys()))
        w.writeheader()
        w.writerows(all_h2h)

    summary = {
        "decision": decision,
        "n_candidates": len(candidates),
        "base_wl": base_r["W-L"], "base_bt": base_r["bt_proxy"],
        "best_id": best["id"], "best_wl": best["W-L"], "best_bt": best["bt_proxy"],
        "n_opp_better": n_opp_better, "opps": opps,
        "base_tape_ep": src["episode_id"],
        "base_tape_live_reward": src["our_reward"],
    }
    (ROOT / "p50_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("wrote p50_candidates.csv p50_h2h.csv p50_summary.json", flush=True)
    print(f"dt={time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
