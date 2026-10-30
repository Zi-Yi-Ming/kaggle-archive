# -*- coding: utf-8 -*-
"""P48 Stage1: record live R2 state→action, measure decision-table coverage."""
from __future__ import annotations

import csv
import importlib.util
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

R2_PATH = ROOT / "_push_medal" / "main.py"
FINN_PATH = ROOT / "reference_agents" / "fallow_finn.py"
SEEDS = (1, 2, 3, 4, 5, 11, 12, 13)
OUT = ROOT / "p48_traces"
OUT.mkdir(exist_ok=True)


def load_agent(path, tag):
    spec = importlib.util.spec_from_file_location(tag, str(path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent if hasattr(m, "agent") else m.build_agent({})


def snap(obs, action):
    player = int(obs.get("player") or 0)
    farms = obs.get("farms") or []
    farm = farms[player] if player < len(farms) else {}
    private = obs.get("private") or {}
    shed = dict(private.get("shed") or {})
    seeds = dict(private.get("seeds") or {})
    prices = dict((obs.get("market") or {}).get("prices") or {})
    shops = list((obs.get("town") or {}).get("unlocked_shops") or [])
    tiles = farm.get("tiles") or []
    plants = animals = empty = weeds = 0
    for row in tiles:
        for t in row:
            if t is None:
                empty += 1
            elif isinstance(t, dict):
                k = t.get("kind")
                if k == "PLANT":
                    plants += 1
                elif k == "WEED":
                    weeds += 1
                if t.get("animal"):
                    animals += 1
    step = int(obs.get("step") or 0)
    return {
        "step": step,
        "day": step // 24,
        "hour": step % 24,
        "money": float(farm.get("money") or 0),
        "hands": len(farm.get("hands") or []),
        "hires_today": int(farm.get("hires_today") or 0),
        "n_land": len(farm.get("unlocked_quadrants") or []),
        "plants": plants, "animals": animals, "empty": empty, "weeds": weeds,
        "shed": {k: int(v or 0) for k, v in shed.items()},
        "seeds_inv": {k: int(v or 0) for k, v in seeds.items()},
        "prices": {k: int(prices.get(k) or 0) for k in
                   ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON",
                    "EGG", "MILK", "WOOL", "FERTILIZER")},
        "shops": shops,
        "n_shops": len(shops),
        "action": {
            "market": action.get("market") or [],
            "farmer": action.get("farmer") or ["PASS"],
            "hands": action.get("hands") or [],
        },
    }


def record(seed):
    r2 = load_agent(R2_PATH, f"r2p48_{seed}")
    finn = load_agent(FINN_PATH, f"finn48_{seed}")
    rows = []

    def wrap(inner):
        def agent(obs, configuration=None):
            a = inner(obs, configuration)
            rows.append(snap(obs, a))
            return a
        return agent

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.info = {"seed": int(seed)}
    env.run([wrap(r2), finn])
    bank = float(env.steps[-1][0]["observation"]["farms"][0]["money"])
    return rows, bank


def akey(a):
    return json.dumps(a, sort_keys=True, default=str)


def mkey(a):
    return json.dumps(a.get("market"), sort_keys=True, default=str)


def wkey(a):
    return json.dumps({"f": a.get("farmer"), "h": a.get("hands")}, sort_keys=True, default=str)


def money_bucket(m):
    if m < 100:
        return "0-100"
    if m < 500:
        return "100-500"
    if m < 2000:
        return "500-2k"
    if m < 5000:
        return "2k-5k"
    if m < 20000:
        return "5k-20k"
    if m < 80000:
        return "20k-80k"
    return "80k+"


def shop_key(shops):
    return "|".join(shops) if shops else "NONE"


def plant_bucket(p):
    if p == 0:
        return "0"
    if p <= 10:
        return "1-10"
    if p <= 30:
        return "11-30"
    if p <= 50:
        return "31-50"
    return "51+"


def evaluate_coverage(all_rows):
    """For each key schema, majority-vote action; measure accuracy."""
    schemas = {
        "day_hour": lambda r: (r["day"], r["hour"]),
        "day_hour_shop": lambda r: (r["day"], r["hour"], shop_key(r["shops"])),
        "day_hour_nshop": lambda r: (r["day"], r["hour"], r["n_shops"]),
        "day_hour_shop_price": lambda r: (
            r["day"], r["hour"], shop_key(r["shops"]),
            r["prices"].get("WHEAT"), r["prices"].get("MELON"),
            r["prices"].get("MILK"), r["prices"].get("FERTILIZER"),
        ),
        "day_hour_shop_money": lambda r: (
            r["day"], r["hour"], shop_key(r["shops"]), money_bucket(r["money"]),
        ),
        "day_hour_shop_plants": lambda r: (
            r["day"], r["hour"], shop_key(r["shops"]), plant_bucket(r["plants"]),
        ),
        "day_hour_full": lambda r: (
            r["day"], r["hour"], shop_key(r["shops"]),
            money_bucket(r["money"]), plant_bucket(r["plants"]),
            r["hands"], r["n_land"],
            r["prices"].get("WHEAT"), r["prices"].get("MELON"),
            r["prices"].get("MILK"), r["prices"].get("FERTILIZER"),
        ),
    }
    results = {}
    for name, fn in schemas.items():
        # group by key → majority action
        groups = defaultdict(list)
        for r in all_rows:
            groups[fn(r)].append(r)
        correct = correct_m = correct_w = total = 0
        unique_keys = 0
        multi = 0
        for k, items in groups.items():
            unique_keys += 1
            n = len(items)
            total += n
            if n > 1:
                multi += 1
            am = Counter(mkey(r["action"]) for r in items)
            aw = Counter(wkey(r["action"]) for r in items)
            ma = am.most_common(1)[0][0]
            wa = aw.most_common(1)[0][0]
            for r in items:
                if mkey(r["action"]) == ma:
                    correct_m += 1
                if wkey(r["action"]) == wa:
                    correct_w += 1
                if mkey(r["action"]) == ma and wkey(r["action"]) == wa:
                    correct += 1
        results[name] = {
            "accuracy": correct / total if total else 0,
            "market_acc": correct_m / total if total else 0,
            "worker_acc": correct_w / total if total else 0,
            "n_keys": unique_keys,
            "n_multi_obs_keys": multi,
            "coverage_multi": multi / unique_keys if unique_keys else 0,
            "n_obs": total,
        }
    return results


def main():
    t0 = time.time()
    print("=== record live R2 traces ===", flush=True)
    all_rows = []
    banks = {}
    for seed in SEEDS:
        p = OUT / f"trace_seed{seed}.json"
        if p.exists():
            rows = json.loads(p.read_text(encoding="utf-8"))
            bank = rows[-1]["money"] if rows else None
            print(f"  seed={seed} loaded {len(rows)} (cached)", flush=True)
        else:
            rows, bank = record(seed)
            p.write_text(json.dumps(rows, default=str), encoding="utf-8")
            print(f"  seed={seed} bank={bank:.0f} n={len(rows)}", flush=True)
        banks[seed] = bank
        for r in rows:
            r["seed"] = seed
        all_rows.extend(rows)

    print(f"total observations={len(all_rows)}", flush=True)

    # equivalence classes / repeats
    print("\n=== state key repeats (can we generalize?) ===", flush=True)
    for label, fn in [
        ("(day,hour)", lambda r: (r["day"], r["hour"])),
        ("(day,hour,shop)", lambda r: (r["day"], r["hour"], shop_key(r["shops"]))),
        ("(hour,nshop)", lambda r: (r["hour"], r["n_shops"])),
        ("(day,nshop)", lambda r: (r["day"], r["n_shops"])),
    ]:
        c = Counter(fn(r) for r in all_rows)
        multi = sum(1 for v in c.values() if v > 1)
        print(f"  {label}: unique={len(c)} multi_obs={multi} "
              f"max_repeat={max(c.values()) if c else 0}", flush=True)

    print("\n=== decision-table coverage ===", flush=True)
    cov = evaluate_coverage(all_rows)
    for name, r in cov.items():
        print(f"  {name:22s} acc={r['accuracy']:.4f} mkt={r['market_acc']:.4f} "
              f"wkr={r['worker_acc']:.4f} keys={r['n_keys']} multi={r['n_multi_obs_keys']}", flush=True)

    # d6/d7 focused
    print("\n=== d6/d7 market accuracy ===", flush=True)
    for day in (5, 6, 7, 8, 9):
        sub = [r for r in all_rows if r["day"] == day]
        if not sub:
            continue
        groups = defaultdict(list)
        for r in sub:
            groups[(r["hour"], shop_key(r["shops"]))].append(r)
        corr = tot = 0
        for k, items in groups.items():
            am = Counter(mkey(r["action"]) for r in items)
            ma = am.most_common(1)[0][0]
            for r in items:
                tot += 1
                if mkey(r["action"]) == ma:
                    corr += 1
        print(f"  d{day}: n={tot} keys={len(groups)} "
              f"mkt_acc_by_(hour,shop)={corr/tot if tot else 0:.4f}", flush=True)

    # how unique are full actions?
    acts = Counter(akey(r["action"]) for r in all_rows)
    print(f"\nunique full actions: {len(acts)} / {len(all_rows)}", flush=True)
    print(f"top10 action freq: {acts.most_common(3)}", flush=True)

    # write coverage csv
    with open(ROOT / "p48_coverage.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "schema", "accuracy", "market_acc", "worker_acc",
            "n_keys", "n_multi_obs_keys", "coverage_multi", "n_obs",
        ])
        w.writeheader()
        for name, r in cov.items():
            w.writerow({"schema": name, **r})

    # Stage1 gate: best schema accuracy
    best = max(cov.items(), key=lambda x: x[1]["accuracy"])
    print(f"\nbest schema={best[0]} acc={best[1]['accuracy']:.4f}", flush=True)

    if best[1]["accuracy"] >= 0.95 and best[1]["n_multi_obs_keys"] >= 50:
        stage1 = "STAGE1_HIGH_FIDELITY"
    elif best[1]["accuracy"] >= 0.85:
        stage1 = "STAGE1_PARTIAL"
    else:
        stage1 = "STAGE1_LOW_FIDELITY"

    print(f"P48_STAGE1={stage1}", flush=True)
    summary = {
        "stage1": stage1,
        "best_schema": best[0],
        "best_acc": best[1]["accuracy"],
        "best_mkt": best[1]["market_acc"],
        "best_wkr": best[1]["worker_acc"],
        "coverage": cov,
        "banks": banks,
        "n_obs": len(all_rows),
        "unique_actions": len(acts),
        "dt": time.time() - t0,
    }
    (ROOT / "p48_stage1_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("wrote p48_coverage.csv p48_stage1_summary.json p48_traces/", flush=True)


if __name__ == "__main__":
    main()
