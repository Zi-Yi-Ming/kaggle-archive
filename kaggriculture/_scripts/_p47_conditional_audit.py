# -*- coding: utf-8 -*-
"""P47: when/why does live R2 change trajectory? First-divergence attribution."""
from __future__ import annotations

import csv
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

R2_PATH = ROOT / "_push_medal" / "main.py"
FINN_PATH = ROOT / "reference_agents" / "fallow_finn.py"
TAPE_PATH = ROOT / "p44_distilled_tapes" / "r2_live_distilled.json"
SEEDS = (1, 2, 3, 4, 5, 11, 12, 13)


def load_agent(path, tag):
    spec = importlib.util.spec_from_file_location(tag, str(path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent if hasattr(m, "agent") else m.build_agent({})


def state_sig(obs, step):
    """Compact state signature at observation."""
    player = int(obs.get("player") or 0)
    farms = obs.get("farms") or []
    farm = farms[player] if player < len(farms) else {}
    private = obs.get("private") or {}
    shed = dict(private.get("shed") or {})
    seeds = dict(private.get("seeds") or {})
    prices = dict((obs.get("market") or {}).get("prices") or {})
    shops = tuple((obs.get("town") or {}).get("unlocked_shops") or [])
    tiles = farm.get("tiles") or []
    plants = animals = empty = 0
    for row in tiles:
        for t in row:
            if t is None:
                empty += 1
            elif isinstance(t, dict):
                if t.get("kind") == "PLANT":
                    plants += 1
                if t.get("animal"):
                    animals += 1
    return {
        "step": step,
        "day": step // 24,
        "hour": step % 24,
        "money": float(farm.get("money") or 0),
        "hands": len(farm.get("hands") or []),
        "hires_today": int(farm.get("hires_today") or 0),
        "n_land": len(farm.get("unlocked_quadrants") or []),
        "plants": plants, "animals": animals, "empty": empty,
        "shed_total": sum(int(v or 0) for v in shed.values()),
        "shed": {k: int(v or 0) for k, v in shed.items() if int(v or 0)},
        "seeds": {k: int(v or 0) for k, v in seeds.items() if int(v or 0)},
        "shops": shops,
        "n_shops": len(shops),
        "prices": {k: int(prices.get(k) or 0) for k in
                   ("WHEAT", "MELON", "MILK", "WOOL", "STRAWBERRY", "FERTILIZER")},
    }


def akey(a):
    return json.dumps({"m": a.get("market"), "f": a.get("farmer"), "h": a.get("hands")},
                      sort_keys=True, default=str)


def record_live_r2(seed):
    """Run live R2 vs finn, record every action + state + shops."""
    r2 = load_agent(R2_PATH, f"r2p47_{seed}")
    finn = load_agent(FINN_PATH, f"finn47_{seed}")
    actions, states = [], []

    def wrap(inner):
        def agent(obs, configuration=None):
            a = inner(obs, configuration)
            step = int(obs.get("step") or 0)
            actions.append({
                "market": a.get("market") or [],
                "farmer": a.get("farmer") or ["PASS"],
                "hands": a.get("hands") or [],
            })
            states.append(state_sig(obs, step))
            return a
        return agent

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.info = {"seed": int(seed)}
    env.run([wrap(r2), finn])
    bank = float(env.steps[-1][0]["observation"]["farms"][0]["money"])
    return actions, states, bank


def first_div(keys_a, keys_b):
    n = min(len(keys_a), len(keys_b))
    for i in range(n):
        if keys_a[i] != keys_b[i]:
            return i
    return None


def classify_div(a, b):
    ma, mb = json.dumps(a["market"], sort_keys=True, default=str), json.dumps(b["market"], sort_keys=True, default=str)
    if ma != mb:
        ops_a = {tuple(o[:2]) if o else () for o in a["market"]}
        ops_b = {tuple(o[:2]) if o else () for o in b["market"]}
        if any(o and o[0] == "SELL" for o in a["market"] + b["market"]):
            return "SELL"
        if ops_a != ops_b:
            return "BUY_HIRE"
        return "MARKET_QTY"
    fa = json.dumps({"f": a["farmer"], "h": a["hands"]}, sort_keys=True, default=str)
    fb = json.dumps({"f": b["farmer"], "h": b["hands"]}, sort_keys=True, default=str)
    if fa != fb:
        return "WORKER"
    return "OTHER"


def diff_states(sa, sb):
    """Which fields differ."""
    keys = []
    for k in ("money", "hands", "plants", "animals", "empty", "shed_total",
              "n_land", "n_shops", "hires_today"):
        if sa.get(k) != sb.get(k):
            keys.append(k)
    if sa.get("shops") != sb.get("shops"):
        keys.append("shops")
    if sa.get("prices") != sb.get("prices"):
        keys.append("prices")
    if sa.get("shed") != sb.get("shed"):
        keys.append("shed_detail")
    if sa.get("seeds") != sb.get("seeds"):
        keys.append("seeds_detail")
    return keys


def main():
    t0 = time.time()
    print("=== record live R2 trajectories ===", flush=True)
    corpus = {}
    banks = {}
    for seed in SEEDS:
        acts, st, bank = record_live_r2(seed)
        corpus[seed] = {"actions": acts, "states": st, "bank": bank,
                        "keys": [akey(a) for a in acts]}
        banks[seed] = bank
        print(f"  seed={seed} bank={bank:.0f} steps={len(acts)}", flush=True)

    # pairwise first divergence among live seeds
    print("\n=== pairwise first divergence (live R2 across seeds) ===", flush=True)
    pair_rows = []
    div_types = Counter()
    div_days = []
    state_diff_at_div = Counter()
    for i, sa in enumerate(SEEDS):
        for sb in SEEDS[i + 1:]:
            fd = first_div(corpus[sa]["keys"], corpus[sb]["keys"])
            if fd is None:
                pair_rows.append({"seed_a": sa, "seed_b": sb, "first_div": -1,
                                  "day": -1, "type": "NONE", "state_diff": ""})
                continue
            typ = classify_div(corpus[sa]["actions"][fd], corpus[sb]["actions"][fd])
            # state just before divergence
            st_a = corpus[sa]["states"][max(0, fd - 1)]
            st_b = corpus[sb]["states"][max(0, fd - 1)]
            # also compare shops at dawn of that day and previous
            day = fd // 24
            sdiff = diff_states(st_a, st_b)
            # shops at day-1 dawn if available
            prev_day = max(0, day - 1)
            # shops recorded in state at any step of that day — use state at day*24 if exists
            def shops_on(seed, d):
                idx = min(d * 24, len(corpus[seed]["states"]) - 1)
                return corpus[seed]["states"][idx]["shops"]
            shop_prev_diff = shops_on(sa, prev_day) != shops_on(sb, prev_day)
            shop_now_diff = shops_on(sa, day) != shops_on(sb, day)
            pair_rows.append({
                "seed_a": sa, "seed_b": sb,
                "first_div": fd, "day": day, "hour": fd % 24,
                "type": typ,
                "shop_prev_diff": int(shop_prev_diff),
                "shop_now_diff": int(shop_now_diff),
                "state_diff": "|".join(sdiff),
                "money_a": st_a["money"], "money_b": st_b["money"],
                "plants_a": st_a["plants"], "plants_b": st_b["plants"],
                "animals_a": st_a["animals"], "animals_b": st_b["animals"],
                "shed_a": st_a["shed_total"], "shed_b": st_b["shed_total"],
                "shops_a": "|".join(st_a["shops"]),
                "shops_b": "|".join(st_b["shops"]),
            })
            div_types[typ] += 1
            div_days.append(day)
            for s in sdiff:
                state_diff_at_div[s] += 1
            print(f"  {sa}x{sb}: fd={fd} d{day} {typ} shop_prev={shop_prev_diff} "
                  f"shop_now={shop_now_diff} state={sdiff}", flush=True)

    print(f"\ndiv_types={div_types.most_common()}", flush=True)
    print(f"div_day histogram={Counter(div_days).most_common()}", flush=True)
    print(f"state_diff_at_div={state_diff_at_div.most_common()}", flush=True)

    # shop signature vs first divergence day vs seed1
    print("\n=== shop signature (d3,d6) per seed ===", flush=True)
    sigs = {}
    for seed in SEEDS:
        st = corpus[seed]["states"]
        # shops at day 3 and day 6
        def shops_day(d):
            idx = min(d * 24, len(st) - 1)
            return st[idx]["shops"]
        sigs[seed] = (shops_day(3), shops_day(6))
        fd1 = first_div(corpus[1]["keys"], corpus[seed]["keys"]) if seed != 1 else None
        print(f"  s{seed}: bank={banks[seed]:.0f} fd_vs_s1={fd1} "
              f"d3={sigs[seed][0]} d6={sigs[seed][1]}", flush=True)

    # --- Experiment 3: branch compression ---
    # base = seed1 tape; add overrides from other seeds only at observed divergent windows
    print("\n=== branch compression test ===", flush=True)
    # For each other seed, first_div vs s1: record how many steps differ in [fd, fd+W)
    # Then evaluate base+overrides vs frozen and vs live
    W = 24  # one day window after first div
    n_override_steps = 0
    n_override_blocks = 0
    # Build hybrid: start from s1 actions; for each seed pair we can't mix in one agent
    # Instead: measure fraction of steps where ANY seed differs from s1 majority
    # and how many unique "branch points" (first-div days)
    unique_fd_days = sorted(set(r["day"] for r in pair_rows if r["day"] >= 0))
    print(f"unique first-div days across pairs: {unique_fd_days}", flush=True)
    print(f"n_pairwise={len(pair_rows)} n_with_div={sum(1 for r in pair_rows if r['first_div']>=0)}", flush=True)

    # agreement of live tapes
    print("\n=== live-live tape similarity ===", flush=True)
    sims = []
    for i, sa in enumerate(SEEDS):
        for sb in SEEDS[i + 1:]:
            ka, kb = corpus[sa]["keys"], corpus[sb]["keys"]
            n = min(len(ka), len(kb))
            s = sum(1 for t in range(n) if ka[t] == kb[t]) / n if n else 0
            sims.append(s)
    print(f"sim mean={statistics.mean(sims):.4f} min={min(sims):.4f} max={max(sims):.4f}", flush=True)

    # vs frozen majority tape
    td = json.loads(TAPE_PATH.read_text(encoding="utf-8"))
    frozen = td["tape"]
    fkeys = [akey(a) for a in frozen]
    print("\n=== live seed vs frozen majority first_div ===", flush=True)
    live_vs_frz = []
    for seed in SEEDS:
        fd = first_div(corpus[seed]["keys"], fkeys)
        typ = classify_div(corpus[seed]["actions"][fd], frozen[fd]) if fd is not None else "NONE"
        live_vs_frz.append({"seed": seed, "bank": banks[seed], "first_div": fd,
                            "day": (fd // 24) if fd is not None else -1, "type": typ})
        print(f"  s{seed}: bank={banks[seed]:.0f} fd={fd} d{(fd//24) if fd is not None else -1} {typ}", flush=True)

    # write
    with open(ROOT / "p47_divergence_pairs.csv", "w", newline="", encoding="utf-8") as f:
        fields = list(pair_rows[0].keys())
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(pair_rows)

    with open(ROOT / "p47_live_vs_frozen_div.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(live_vs_frz[0].keys()))
        w.writeheader()
        w.writerows(live_vs_frz)

    # attribution summary
    n_shop_prev = sum(1 for r in pair_rows if r.get("shop_prev_diff") == 1)
    n_shop_now = sum(1 for r in pair_rows if r.get("shop_now_diff") == 1)
    n_div = sum(1 for r in pair_rows if r["first_div"] >= 0)
    print(f"\nshop_prev_diff at div: {n_shop_prev}/{n_div}", flush=True)
    print(f"shop_now_diff at div:  {n_shop_now}/{n_div}", flush=True)

    decision = "AUDIT_COMPLETE"
    # branch complexity estimate: unique first-div days + unique shop sigs
    n_sigs = len(set(sigs.values()))
    print(f"unique shop sigs (d3,d6): {n_sigs} / {len(SEEDS)}", flush=True)
    if n_div > 0 and n_shop_prev / n_div >= 0.7:
        decision = "SHOP_CONDITIONED_BRANCH_SUPPORTED"
    elif n_div > 0 and state_diff_at_div.get("money", 0) / max(1, n_div) >= 0.7:
        decision = "CASH_STATE_CONDITIONED_SUPPORTED"
    else:
        decision = "MULTI_FACTOR_CONDITIONING"

    print(f"P47_DECISION={decision}", flush=True)

    summary = {
        "decision": decision,
        "n_seeds": len(SEEDS),
        "banks": banks,
        "live_sim_mean": statistics.mean(sims),
        "div_types": dict(div_types),
        "div_days": dict(Counter(div_days)),
        "state_diff_at_div": dict(state_diff_at_div),
        "shop_prev_frac": n_shop_prev / max(1, n_div),
        "shop_now_frac": n_shop_now / max(1, n_div),
        "unique_shop_sigs": n_sigs,
        "unique_fd_days": unique_fd_days,
        "dt": time.time() - t0,
    }
    (ROOT / "p47_summary.json").write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    print("wrote p47_divergence_pairs.csv p47_live_vs_frozen_div.csv p47_summary.json", flush=True)


if __name__ == "__main__":
    main()
