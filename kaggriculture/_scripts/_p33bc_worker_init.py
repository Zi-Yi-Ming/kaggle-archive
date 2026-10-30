# -*- coding: utf-8 -*-
"""P33-B/C: worker-action similarity across elites + initial-state predictability."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

ELITES = {
    "R2": ROOT / "_push_medal" / "main.py",
    "kaito_v27": ROOT / "_external" / "public_nb" / "kaito_v27" / "main.py",
    "qeinstein": ROOT / "_external" / "git" / "qeinstein" / "dist" / "sub-009-moev2" / "main.py",
    "rayk_rank": ROOT / "_external" / "public_nb" / "rayk_rank" / "main.py",
}


def load_mod(path, name):
    spec = importlib.util.spec_from_file_location(name, str(path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def get_agent(mod):
    if hasattr(mod, "agent"):
        return mod.agent
    return mod.build_agent({})


def record(name, agent_fn, seed):
    finn = load_mod(ROOT / "reference_agents" / "fallow_finn.py", f"fn_{name}_{seed}").agent
    recs = []

    def wrap(inner):
        def agent(obs, configuration=None):
            a = inner(obs, configuration)
            step = int(obs.get("step") or 0)
            farm = (obs.get("farms") or [])[0]
            private = obs.get("private") or {}
            tiles = farm.get("tiles") or []
            plants = melon = animals = empty = 0
            for row in tiles:
                for t in row:
                    if t is None:
                        empty += 1
                    elif isinstance(t, dict):
                        if t.get("kind") == "PLANT":
                            plants += 1
                            if t.get("crop") == "MELON":
                                melon += 1
                        if t.get("animal"):
                            animals += 1
            farmer = a.get("farmer") or []
            hands = a.get("hands") or []
            market = a.get("market") or []
            mkt_sig = "|".join(sorted({o[0] for o in market if o}))
            wk = json.dumps([farmer] + list(hands), default=str)
            recs.append({
                "policy": name, "seed": seed, "step": step, "day": step // 24, "hour": step % 24,
                "money": float(farm.get("money") or 0),
                "plants": plants, "melon": melon, "animals": animals, "empty": empty,
                "hands_n": len(hands),
                "farmer0": farmer[0] if farmer else "PASS",
                "worker_sig": hashlib.md5(wk.encode()).hexdigest()[:12],
                "market_sig": mkt_sig,
                "init_money": 3000,
            })
            return a
        return agent

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    env.run([wrap(agent_fn), finn])
    f = env.steps[-1]
    bank = float(f[0]["observation"]["farms"][0]["money"])
    return recs, bank


def sim_worker(keys_a, keys_b):
    n = min(len(keys_a), len(keys_b))
    if n == 0:
        return 0.0
    return sum(1 for i in range(n) if keys_a[i] == keys_b[i]) / n


def bucket_init(r):
    """Initial-ish features: day early + shop count trajectory proxy."""
    # use day0 state when available
    return (r["day"], min(r["animals"], 5), min(r["plants"] // 5, 4), min(r["hands_n"], 4))


def bucket_now(r):
    mb = 0 if r["money"] < 200 else (1 if r["money"] < 1000 else (2 if r["money"] < 5000 else 3))
    return (r["day"], r["hour"] // 6, mb, min(r["animals"], 5), min(r["plants"] // 5, 4))


def main():
    # record seed1 all elites
    traj = {}
    banks = {}
    for name, path in ELITES.items():
        fn = get_agent(load_mod(path, f"p33_{name}"))
        recs, bank = record(name, fn, 1)
        traj[name] = recs
        banks[name] = bank
        print(f"{name}: bank={bank:.0f} n={len(recs)}", flush=True)

    # B: worker sim vs R2
    print("\n=== WORKER / MARKET sim vs R2 (seed1) ===")
    r2_w = [r["worker_sig"] for r in traj["R2"]]
    r2_m = [r["market_sig"] for r in traj["R2"]]
    sim_rows = []
    for name in ELITES:
        ws = sim_worker([r["worker_sig"] for r in traj[name]], r2_w)
        ms = sim_worker([r["market_sig"] for r in traj[name]], r2_m)
        sim_rows.append({"policy": name, "bank": banks[name], "worker_sim": ws, "market_sim": ms})
        print(f"  {name:14s} bank={banks[name]:.0f} worker_sim={ws:.3f} market_sim={ms:.3f}", flush=True)

    outb = ROOT / "p33b_worker_similarity.csv"
    with open(outb, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(sim_rows[0].keys()))
        w.writeheader()
        w.writerows(sim_rows)

    # C: initial-state vs current-state predictability on R2
    # Use day/hour as "initial" proxy is weak. Better: use shops + day only (early plan)
    # True initial: seed. We only have one seed here — use shops trajectory as env realization.
    recs = traj["R2"]
    # M0 current: bucket_now -> market_sig
    # M_init: (shops_bucket, day, hour) -> market_sig  where shops_bucket from first unlock count
    # We didn't record shops in this script — add from n_shops if present else skip
    # Use day0 money path: initial cash always 3000; better feature = shop count at this step
    # Fall back: compare current vs (day, hour) only vs (day, hour, day0-features)

    def acc(key_fn):
        votes = defaultdict(Counter)
        for r in recs:
            votes[key_fn(r)][r["market_sig"]] += 1
        default = Counter(r["market_sig"] for r in recs).most_common(1)[0][0]
        lut = {k: c.most_common(1)[0][0] for k, c in votes.items()}
        hit = sum(1 for r in recs if lut.get(key_fn(r), default) == r["market_sig"])
        return hit / len(recs), len(votes)

    a_now, b_now = acc(bucket_now)
    a_day, b_day = acc(lambda r: (r["day"], r["hour"] // 6))
    a_dayh, b_dayh = acc(lambda r: (r["day"], r["hour"]))
    # open-loop proxy: (day, hour) is essentially step — if high acc, open-loop by time
    print("\n=== P33-C R2 predictability ===")
    print(f"  current-state bucket: acc={a_now:.3f} buckets={b_now}")
    print(f"  day+hourbin only:     acc={a_day:.3f} buckets={b_day}")
    print(f"  day+hour (open-loop): acc={a_dayh:.3f} buckets={b_dayh}")

    outc = ROOT / "p33c_initial_predictability.csv"
    with open(outc, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["model", "accuracy", "n_buckets"])
        w.writerow(["current_state", a_now, b_now])
        w.writerow(["day_hourbin", a_day, b_day])
        w.writerow(["day_hour_openloop", a_dayh, b_dayh])
    print("wrote", outb.name, outc.name)


if __name__ == "__main__":
    main()
