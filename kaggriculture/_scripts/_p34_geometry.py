# -*- coding: utf-8 -*-
"""P34: elite trajectory geometry — phases, landmarks, coupled motifs.

Not action similarity. Structural compression of 720-step trajectories.
Uses elite_corpus/ recorded + live re-record with worker ops.
Caveat: R2 acc(day,hour)=1.0 means R2 is open-loop; does NOT prove all elites are.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
CORPUS = ROOT / "elite_corpus"
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


def record_full(name, agent_fn, seed=1):
    finn = load_mod(ROOT / "reference_agents" / "fallow_finn.py", f"geo_{name}").agent
    steps = []

    def wrap(inner):
        def agent(obs, configuration=None):
            a = inner(obs, configuration)
            step = int(obs.get("step") or 0)
            farm = (obs.get("farms") or [])[0]
            private = obs.get("private") or {}
            shed = dict(private.get("shed") or {})
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
            market = a.get("market") or []
            m_hire = m_sell = m_buy = 0
            sell_val = 0.0
            prices = dict((obs.get("market") or {}).get("prices") or {})
            for o in market:
                if not o:
                    continue
                if o[0] == "HIRE":
                    m_hire += 1
                elif o[0] == "SELL" and len(o) >= 3:
                    m_sell += 1
                    sell_val += int(o[2] or 0) * int(prices.get(o[1]) or 0)
                elif o[0].startswith("BUY"):
                    m_buy += 1
            farmer = a.get("farmer") or []
            hands = a.get("hands") or []
            wk = Counter()
            for c in [farmer] + list(hands):
                if c:
                    wk[c[0]] += 1
            money = float(farm.get("money") or 0)
            steps.append({
                "policy": name, "seed": seed, "step": step, "day": step // 24, "hour": step % 24,
                "money": money, "plants": plants, "melon": melon, "animals": animals,
                "empty": empty, "hands_n": len(hands),
                "shed_total": sum(int(v or 0) for v in shed.values()),
                "m_hire": m_hire, "m_sell": m_sell, "m_buy": m_buy, "sell_val": sell_val,
                "wk": json.dumps(dict(wk)),
                "farmer0": farmer[0] if farmer else "PASS",
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
    return steps, bank


def day_rollup(steps):
    by = defaultdict(lambda: {
        "money": None, "plants": None, "animals": None, "melon": None,
        "empty": None, "shed": None, "hands": None,
        "hire": 0, "sell": 0, "buy": 0, "sell_val": 0.0,
        "wk": Counter(),
    })
    for s in steps:
        d = s["day"]
        b = by[d]
        b["money"] = s["money"]
        b["plants"] = s["plants"]
        b["animals"] = s["animals"]
        b["melon"] = s["melon"]
        b["empty"] = s["empty"]
        b["shed"] = s["shed_total"]
        b["hands"] = s["hands_n"]
        b["hire"] += s["m_hire"]
        b["sell"] += s["m_sell"]
        b["buy"] += s["m_buy"]
        b["sell_val"] += s["sell_val"]
        wk = json.loads(s["wk"])
        for k, v in wk.items():
            b["wk"][k] += v
    return by


def find_landmarks(daily):
    """Structural landmarks — allow different exact days."""
    lm = {}
    # first day animals >= 2
    for d in sorted(daily):
        if (daily[d]["animals"] or 0) >= 2:
            lm["first_animals2"] = d
            break
    for d in sorted(daily):
        if (daily[d]["animals"] or 0) >= 8:
            lm["animals8"] = d
            break
    for d in sorted(daily):
        if (daily[d]["melon"] or 0) >= 5:
            lm["melon5"] = d
            break
    # melon collapse (conversion)
    prev_m = 0
    for d in sorted(daily):
        m = daily[d]["melon"] or 0
        if prev_m >= 5 and m < prev_m - 3:
            lm["melon_convert"] = d
            break
        prev_m = max(prev_m, m)
    # first sell_val day > 2000
    for d in sorted(daily):
        if daily[d]["sell_val"] >= 2000:
            lm["sell_2k"] = d
            break
    # cash inflection: first day money > 5k then > 20k
    for d in sorted(daily):
        if (daily[d]["money"] or 0) >= 5000:
            lm["cash_5k"] = d
            break
    for d in sorted(daily):
        if (daily[d]["money"] or 0) >= 20000:
            lm["cash_20k"] = d
            break
    # plant fill: empty < 3
    for d in sorted(daily):
        if (daily[d]["empty"] or 99) <= 3:
            lm["field_filled"] = d
            break
    return lm


def phase_labels(daily):
    """Coarse phases from landmarks (not fixed days)."""
    lm = find_landmarks(daily)
    a2 = lm.get("first_animals2", 3)
    mel = lm.get("melon_convert", 11)
    c5 = lm.get("cash_5k", 12)
    return {
        "P0_BOOT": (0, max(1, a2)),
        "P1_EXPAND": (a2, mel),
        "P2_CONVERT": (mel, c5),
        "P3_SCALE": (c5, 26),
        "P4_END": (26, 29),
        "landmarks": lm,
    }


def worker_motif(daily):
    """Dominant worker op mix per phase."""
    out = {}
    for d, b in daily.items():
        wk = b["wk"]
        total = sum(wk.values()) or 1
        out[d] = {k: v / total for k, v in wk.most_common(6)}
    return out


def main():
    all_daily = {}
    all_bank = {}
    for name, path in ELITES.items():
        if not path.exists():
            print("SKIP", name, flush=True)
            continue
        fn = get_agent(load_mod(path, f"geo2_{name}"))
        steps, bank = record_full(name, fn, seed=1)
        daily = day_rollup(steps)
        all_daily[name] = daily
        all_bank[name] = bank
        print(f"{name}: bank={bank:.0f} days={len(daily)}", flush=True)

    # landmarks table
    lm_rows = []
    for name, daily in all_daily.items():
        lm = find_landmarks(daily)
        lm_rows.append({"policy": name, "bank": all_bank[name], **{k: lm.get(k, "") for k in
            ("first_animals2", "animals8", "melon5", "melon_convert", "sell_2k", "cash_5k", "cash_20k", "field_filled")}})
        print(f"\n{name} landmarks: {lm}", flush=True)

    out1 = ROOT / "p34_temporal_landmarks.csv"
    with open(out1, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(lm_rows[0].keys()))
        w.writeheader()
        w.writerows(lm_rows)

    # phase structure
    print("\n=== PHASE WINDOWS ===")
    for name, daily in all_daily.items():
        ph = phase_labels(daily)
        print(f"  {name}: {ph}", flush=True)

    # event density: hires/sells per day bin
    print("\n=== EVENT DENSITY (mean per day-bin) ===")
    bins = [(0, 5, "d0-5"), (6, 10, "d6-10"), (11, 15, "d11-15"), (16, 20, "d16-20"), (21, 29, "d21-29")]
    dens_rows = []
    for name, daily in all_daily.items():
        for lo, hi, tag in bins:
            hs = sum(daily[d]["hire"] for d in range(lo, hi + 1) if d in daily)
            ss = sum(daily[d]["sell"] for d in range(lo, hi + 1) if d in daily)
            bs = sum(daily[d]["buy"] for d in range(lo, hi + 1) if d in daily)
            sv = sum(daily[d]["sell_val"] for d in range(lo, hi + 1) if d in daily)
            dens_rows.append({"policy": name, "bin": tag, "hire": hs, "sell": ss, "buy": bs, "sell_val": sv})
            print(f"  {name:14s} {tag:8s} hire={hs:4d} sell={ss:4d} buy={bs:3d} sell_val={sv:8.0f}", flush=True)

    out2 = ROOT / "p34_event_density.csv"
    with open(out2, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(dens_rows[0].keys()))
        w.writeheader()
        w.writerows(dens_rows)

    # resource-flow motif: order of first milestones
    print("\n=== MOTIF ORDER ===")
    for name in all_daily:
        lm = find_landmarks(all_daily[name])
        order = sorted(((v, k) for k, v in lm.items() if isinstance(v, int)))
        print(f"  {name}: " + " → ".join(f"{k}@d{v}" for v, k in order), flush=True)

    # similarity of landmark day vectors (normalized)
    print("\n=== LANDMARK DAY DISTANCE (abs, R2 as ref) ===")
    keys = ["first_animals2", "animals8", "melon5", "melon_convert", "sell_2k", "cash_5k", "cash_20k", "field_filled"]
    ref = find_landmarks(all_daily["R2"])
    for name, daily in all_daily.items():
        lm = find_landmarks(daily)
        dist = sum(abs(int(lm.get(k, 0) or 0) - int(ref.get(k, 0) or 0)) for k in keys)
        print(f"  {name}: L1_landmark_dist={dist}", flush=True)

    # coupled motif: day with high sell_val AND high harvest/water
    print("\n=== COUPLED DAYS (sell_val>1k and WATER+HARVEST>20) ===")
    for name, daily in all_daily.items():
        days = []
        for d, b in sorted(daily.items()):
            wk = b["wk"]
            prod = wk.get("WATER", 0) + wk.get("HARVEST", 0)
            if b["sell_val"] >= 1000 and prod >= 20:
                days.append(d)
        print(f"  {name}: coupled_days={days[:15]} n={len(days)}", flush=True)

    out3 = ROOT / "p34_regimes.csv"
    with open(out3, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["policy", "bank", "phases", "landmark_order"])
        for name in all_daily:
            ph = phase_labels(all_daily[name])
            lm = find_landmarks(all_daily[name])
            order = sorted(((v, k) for k, v in lm.items() if isinstance(v, int)))
            w.writerow([name, all_bank[name], str({k: v for k, v in ph.items() if k != "landmarks"}),
                        "→".join(f"{k}@{v}" for v, k in order)])
    print("wrote", out1.name, out2.name, out3.name)


if __name__ == "__main__":
    main()
