# -*- coding: utf-8 -*-
"""P45: original replay vs global majority vs shop-conditioned majority."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import statistics
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

REP = ROOT / "_external" / "p42_replays"
FINN_PATH = ROOT / "reference_agents" / "fallow_finn.py"
OUT = ROOT / "p44_distilled_tapes"


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


def run_both_seats(tape, seed):
    fn = load_agent(FINN_PATH, f"finn45a_{seed}")
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.info = {"seed": int(seed)}
    env.run([tape_agent(tape), fn])
    f = env.steps[-1]
    us_s0 = float(f[0]["observation"]["farms"][0]["money"])
    fn_s1 = float(f[1]["observation"]["farms"][1]["money"])

    fn2 = load_agent(FINN_PATH, f"finn45b_{seed}")
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.info = {"seed": int(seed)}
    env.run([fn2, tape_agent(tape)])
    f = env.steps[-1]
    fn_s0 = float(f[0]["observation"]["farms"][0]["money"])
    us_s1 = float(f[1]["observation"]["farms"][1]["money"])

    our = (us_s0 + us_s1) / 2
    opp = (fn_s1 + fn_s0) / 2
    res = "W" if our > opp + 1 else ("L" if opp > our + 1 else "D")
    return our, opp, res


def parse_replays():
    meta = json.loads((REP / "meta.json").read_text(encoding="utf-8"))
    eps = []
    for m in meta:
        path = Path(m["path"])
        if not path.exists():
            continue
        d = json.loads(path.read_text(encoding="utf-8"))
        steps = d.get("steps") or []
        if len(steps) != 720:
            continue
        seat = int(m.get("our_seat") or 0)
        actions = []
        shops_by_day = []
        for i, step in enumerate(steps):
            a = step[seat].get("action") or {}
            actions.append({
                "market": a.get("market") or [],
                "farmer": a.get("farmer") or ["PASS"],
                "hands": a.get("hands") or [],
            })
            if i % 24 == 0:
                obs = step[seat].get("observation") or {}
                shops_by_day.append(tuple((obs.get("town") or {}).get("unlocked_shops") or []))
        # shop signature: shops at day 3 and day 6 (first two unlocks)
        sig = (shops_by_day[3] if len(shops_by_day) > 3 else (),
               shops_by_day[6] if len(shops_by_day) > 6 else ())
        eps.append({
            "episode_id": m["episode_id"],
            "opp": m["opp_team"],
            "seat": seat,
            "reward": m.get("our_reward"),
            "actions": actions,
            "shop_sig": sig,
            "shops_by_day": shops_by_day,
        })
    return eps


def canon(a, kind):
    if kind == "market":
        return json.dumps(a.get("market"), sort_keys=True, default=str)
    return json.dumps({"f": a.get("farmer"), "h": a.get("hands")}, sort_keys=True, default=str)


def majority_from_group(episodes):
    n = len(episodes)
    tape = []
    m_unan = w_unan = 0
    for t in range(720):
        mv, wv = Counter(), Counter()
        mex, wex = {}, {}
        for ep in episodes:
            a = ep["actions"][t]
            mk, wk = canon(a, "market"), canon(a, "worker")
            mv[mk] += 1
            wv[wk] += 1
            mex.setdefault(mk, a["market"])
            wex.setdefault(wk, (a["farmer"], a["hands"]))
        m_key = mv.most_common(1)[0][0]
        w_key = wv.most_common(1)[0][0]
        if mv[m_key] == n:
            m_unan += 1
        if wv[w_key] == n:
            w_unan += 1
        farmer, hands = wex[w_key]
        tape.append({"market": mex[m_key], "farmer": farmer, "hands": hands})
    return tape, {
        "n": n,
        "m_unan": m_unan / 720,
        "w_unan": w_unan / 720,
    }


def shop_conditioned_majority(episodes):
    """Stitch: for each step, majority among episodes that share that step's
    realized shop state (from the episode itself). Deterministic fallback:
    if group empty, use global majority at that step.
    """
    # global fallback
    g_tape, _ = majority_from_group(episodes)
    # group by shop signature at the day of the step
    # For step t, day = t//24, use shops_by_day[day] as condition
    by_shop_at_day = defaultdict(list)  # (day, shops) -> episodes
    for ep in episodes:
        for day, shops in enumerate(ep["shops_by_day"]):
            by_shop_at_day[(day, shops)].append(ep)

    tape = []
    used_cond = 0
    used_fallback = 0
    for t in range(720):
        day = t // 24
        # We cannot know shops at runtime for a synthetic tape without replaying.
        # Conditional majority here: use the modal shop-state for that day across
        # episodes, then majority among episodes that had that modal shop state.
        shop_counts = Counter(ep["shops_by_day"][day] for ep in episodes if day < len(ep["shops_by_day"]))
        if not shop_counts:
            tape.append(g_tape[t])
            used_fallback += 1
            continue
        modal_shops = shop_counts.most_common(1)[0][0]
        group = [ep for ep in episodes
                 if day < len(ep["shops_by_day"]) and ep["shops_by_day"][day] == modal_shops]
        if len(group) < 2:
            tape.append(g_tape[t])
            used_fallback += 1
            continue
        mv, wv = Counter(), Counter()
        mex, wex = {}, {}
        for ep in group:
            a = ep["actions"][t]
            mk, wk = canon(a, "market"), canon(a, "worker")
            mv[mk] += 1
            wv[wk] += 1
            mex.setdefault(mk, a["market"])
            wex.setdefault(wk, (a["farmer"], a["hands"]))
        m_key = mv.most_common(1)[0][0]
        w_key = wv.most_common(1)[0][0]
        farmer, hands = wex[w_key]
        tape.append({"market": mex[m_key], "farmer": farmer, "hands": hands})
        used_cond += 1
    return tape, {"used_cond": used_cond, "used_fallback": used_fallback}


def eval_label(tape, seeds, label):
    w = d = l = 0
    banks = []
    for seed in seeds:
        our, opp, res = run_both_seats(tape, seed)
        banks.append(our)
        if res == "W":
            w += 1
        elif res == "L":
            l += 1
        else:
            d += 1
        print(f"    {label} s{seed} our={our:.0f} opp={opp:.0f} {res}", flush=True)
    return {
        "label": label, "W": w, "D": d, "L": l, "W-L": w - l,
        "bank_mean": statistics.mean(banks),
        "bank_std": statistics.pstdev(banks) if len(banks) > 1 else 0,
        "banks": banks,
    }


def main():
    t0 = time.time()
    eps = parse_replays()
    print(f"n_episodes={len(eps)}", flush=True)
    seeds = (1, 2, 3)

    # shop signature clusters
    sigs = Counter(ep["shop_sig"] for ep in eps)
    print(f"unique shop_sig (d3,d6)={len(sigs)} top={sigs.most_common(5)}", flush=True)

    results = []

    # --- A/B: top individual replays by live reward ---
    ranked = sorted(eps, key=lambda e: -(e.get("reward") or 0))
    print("\n=== TOP individual live rewards ===", flush=True)
    for e in ranked[:5]:
        print(f"  {e['episode_id']} opp={e['opp'][:20]} reward={e['reward']}", flush=True)

    for i, e in enumerate(ranked[:3]):
        label = f"orig_top{i+1}_ep{e['episode_id']}"
        print(f"\n=== {label} live_reward={e['reward']} ===", flush=True)
        r = eval_label(e["actions"], seeds, label)
        r["live_reward"] = e["reward"]
        r["kind"] = "original"
        results.append(r)

    # also a median-reward replay
    med = ranked[len(ranked) // 2]
    label = f"orig_median_ep{med['episode_id']}"
    print(f"\n=== {label} live_reward={med['reward']} ===", flush=True)
    r = eval_label(med["actions"], seeds, label)
    r["live_reward"] = med["reward"]
    r["kind"] = "original"
    results.append(r)

    # --- C: global majority (P44 baseline) ---
    print("\n=== global majority ===", flush=True)
    g_tape, g_stats = majority_from_group(eps)
    print(f"  stats {g_stats}", flush=True)
    r = eval_label(g_tape, seeds, "global_majority")
    r["kind"] = "global_majority"
    results.append(r)

    # --- D: shop-conditioned majority ---
    print("\n=== shop-conditioned majority (modal shops per day) ===", flush=True)
    c_tape, c_stats = shop_conditioned_majority(eps)
    print(f"  stats {c_stats}", flush=True)
    r = eval_label(c_tape, seeds, "shop_cond_majority")
    r["kind"] = "shop_cond_majority"
    results.append(r)

    # --- extra: majority within largest shop cluster only ---
    print("\n=== largest-shop-cluster majority ===", flush=True)
    top_sig = sigs.most_common(1)[0][0]
    cluster = [ep for ep in eps if ep["shop_sig"] == top_sig]
    print(f"  cluster size={len(cluster)} sig={top_sig}", flush=True)
    if len(cluster) >= 3:
        cl_tape, cl_stats = majority_from_group(cluster)
        print(f"  stats {cl_stats}", flush=True)
        r = eval_label(cl_tape, seeds, "cluster_majority")
        r["kind"] = "cluster_majority"
        results.append(r)

    # --- sim: originals vs global majority ---
    print("\n=== similarity to global majority ===", flush=True)
    g_keys = [canon(a, "all") if False else json.dumps(a, sort_keys=True, default=str) for a in g_tape]

    def tape_sim(a, b):
        n = min(len(a), len(b))
        if n == 0:
            return 0.0
        return sum(1 for i in range(n)
                   if json.dumps(a[i], sort_keys=True, default=str)
                   == json.dumps(b[i], sort_keys=True, default=str)) / n

    for e in ranked[:5]:
        s = tape_sim(e["actions"], g_tape)
        print(f"  ep{e['episode_id']} sim_to_global={s:.4f} live={e['reward']}", flush=True)

    print("\n=== SUMMARY ===", flush=True)
    print(f"{'label':40s} {'W-D-L':8s} {'W-L':4s} {'bank':10s} kind")
    for r in results:
        print(f"{r['label'][:40]:40s} {r['W']}-{r['D']}-{r['L']:<5} {r['W-L']:4d} "
              f"{r['bank_mean']:10.0f} {r['kind']}")

    # decision logic
    orig_banks = [r["bank_mean"] for r in results if r["kind"] == "original"]
    g_bank = next(r["bank_mean"] for r in results if r["kind"] == "global_majority")
    c_bank = next((r["bank_mean"] for r in results if r["kind"] == "shop_cond_majority"), None)
    best_orig = max(orig_banks) if orig_banks else 0

    if best_orig >= 150000 and g_bank < best_orig * 0.75:
        if c_bank and c_bank >= g_bank * 1.25:
            decision = "DISTILLATION_LOSS_BRANCH_PRESERVE_HELPED"
        else:
            decision = "DISTILLATION_LOSS_BRANCH_NOT_RECOVERED"
    elif best_orig >= 150000 and g_bank >= best_orig * 0.85:
        decision = "DISTILLATION_NOT_PRIMARY_LOSS"
    else:
        decision = "ORIGINAL_REPLAYS_NOT_ELITE_VS_FINN"

    print(f"\nP45_DECISION={decision}", flush=True)
    print(f"best_orig_vs_finn={best_orig:.0f} global={g_bank:.0f} "
          f"shop_cond={c_bank if c_bank is not None else 'NA'}", flush=True)

    # write csv
    with open(ROOT / "p45_distill_compare.csv", "w", newline="", encoding="utf-8") as f:
        fields = ["label", "kind", "W", "D", "L", "W-L", "bank_mean", "bank_std",
                  "live_reward", "bank_s1", "bank_s2", "bank_s3"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in results:
            banks = r.get("banks") or [None, None, None]
            w.writerow({
                "label": r["label"], "kind": r["kind"],
                "W": r["W"], "D": r["D"], "L": r["L"], "W-L": r["W-L"],
                "bank_mean": r["bank_mean"], "bank_std": r["bank_std"],
                "live_reward": r.get("live_reward"),
                "bank_s1": banks[0] if len(banks) > 0 else None,
                "bank_s2": banks[1] if len(banks) > 1 else None,
                "bank_s3": banks[2] if len(banks) > 2 else None,
            })

    summary = {
        "decision": decision,
        "best_orig_vs_finn": best_orig,
        "global_majority": g_bank,
        "shop_cond_majority": c_bank,
        "n_episodes": len(eps),
        "shop_clusters": len(sigs),
        "dt": time.time() - t0,
    }
    (ROOT / "p45_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("wrote p45_distill_compare.csv p45_summary.json", flush=True)


if __name__ == "__main__":
    main()
