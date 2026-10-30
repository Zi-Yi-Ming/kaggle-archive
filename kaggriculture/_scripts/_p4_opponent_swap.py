# -*- coding: utf-8 -*-
"""P4: matched-state opponent swap.

Control: same seed, same R2 policy/seat, same env config.
Treatment: only opponent policy changes.
O1 = R2 mirror
O2 = cow-heavy no-goose scripted bot
O3 = 3-goose + cow + sheep scripted bot (live-loss signature)

We cannot freeze early trajectory; we freeze seed+R2+seat only.
That is the closest legal matched-state design.
"""
from __future__ import annotations

import csv
import importlib.util
import json
import os
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make
from _pm_pool import load_agent as load_pool

R2_PATH = ROOT / "_push_medal" / "main.py"


def load_r2(tag):
    spec = importlib.util.spec_from_file_location(f"r2_{tag}", str(R2_PATH))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def cow_bot(obs):
    """O2: expand land, buy/place COWs, feed, never goose."""
    me = int(obs.get("player") or 0)
    farm = (obs.get("farms") or [])[me]
    private = obs.get("private") or {}
    money = float(farm.get("money") or 0)
    quads = set(farm.get("unlocked_quadrants") or [])
    tiles = farm.get("tiles") or []
    hands = farm.get("hands") or []
    shed = private.get("shed") or {}
    inv0 = (private.get("inventories") or [{}])[0] or {}

    def count_animals():
        c = Counter()
        for row in tiles:
            for t in row or []:
                if isinstance(t, dict) and t.get("animal"):
                    c[t["animal"]] += 1
        return c

    an = count_animals()
    market = []
    if len(quads) < 3 and money > 5000:
        market.append(["BUY_LAND"])
    if an["COW"] < 9 and money > 800:
        market.append(["BUY_ANIMAL", "COW", 1])
    # feed from shed
    farmer = ["PASS"]
    x, y = farm.get("farmer") or [4, 4]
    # find cow tile without feed
    for yy, row in enumerate(tiles):
        for xx, t in enumerate(row or []):
            if isinstance(t, dict) and t.get("animal") == "COW" and not t.get("fed_today"):
                if abs(xx - x) + abs(yy - y) == 0:
                    if inv0.get("WHEAT", 0) > 0 or shed.get("WHEAT", 0) > 0:
                        if shed.get("WHEAT", 0) > 0 and inv0.get("WHEAT", 0) == 0:
                            farmer = ["PICKUP", "WHEAT", 1]
                        else:
                            farmer = ["FEED"]
                else:
                    farmer = "NORTH" if yy < y else ("SOUTH" if yy > y else ("WEST" if xx < x else "EAST"))
                break
        else:
            continue
        break
    else:
        # place cow if holding
        if inv0.get("COW", 0) > 0:
            farmer = ["PLACE", "COW"]
        elif shed.get("COW", 0) > 0:
            farmer = ["PICKUP", "COW", 1]
    return {"farmer": [farmer] if isinstance(farmer, str) else farmer, "hands": [], "market": market[:10]}


def mixed_bot(obs):
    """O3: target 3 goose + 8 cow + 6 sheep-ish mix."""
    me = int(obs.get("player") or 0)
    farm = (obs.get("farms") or [])[me]
    private = obs.get("private") or {}
    money = float(farm.get("money") or 0)
    quads = set(farm.get("unlocked_quadrants") or [])
    tiles = farm.get("tiles") or []
    shed = private.get("shed") or {}
    inv0 = (private.get("inventories") or [{}])[0] or {}

    def count_animals():
        c = Counter()
        for row in tiles:
            for t in row or []:
                if isinstance(t, dict) and t.get("animal"):
                    c[t["animal"]] += 1
        return c

    an = count_animals()
    market = []
    if len(quads) < 3 and money > 5000:
        market.append(["BUY_LAND"])
    if an["GOOSE"] < 3 and money > 600:
        market.append(["BUY_ANIMAL", "GOOSE", 1])
    elif an["COW"] < 8 and money > 800:
        market.append(["BUY_ANIMAL", "COW", 1])
    elif an["SHEEP"] < 6 and money > 900:
        market.append(["BUY_ANIMAL", "SHEEP", 1])
    # place any held animal
    farmer = ["PASS"]
    for a in ("GOOSE", "COW", "SHEEP"):
        if inv0.get(a, 0) > 0:
            farmer = ["PLACE", a]
            break
    else:
        if shed.get("COW", 0) > 0:
            farmer = ["PICKUP", "COW", 1]
        elif shed.get("GOOSE", 0) > 0:
            farmer = ["PICKUP", "GOOSE", 1]
        elif shed.get("SHEEP", 0) > 0:
            farmer = ["PICKUP", "SHEEP", 1]
    return {"farmer": farmer, "hands": [], "market": market[:10]}


def money_curve(env, seat):
    """Extract own/opp money at day boundaries for seat."""
    out = {}
    for idx, snap in enumerate(env.steps):
        rec = snap[seat] if seat < len(snap) else None
        if not rec:
            continue
        obs = rec.get("observation") or {}
        if not isinstance(obs, dict):
            continue
        step = obs.get("step")
        step = int(step) if step is not None else idx
        if step % 24 != 0:
            continue
        day = step // 24
        farms = obs.get("farms") or []
        if len(farms) < 2:
            continue
        mine = float((farms[seat] or {}).get("money") or 0)
        opp = float((farms[1 - seat] or {}).get("money") or 0)
        out[day] = {"mine": mine, "opp": opp, "gap": mine - opp}
    return out


def count_listings(env, seat, day_lo, day_hi):
    n_events = qty = 0
    for idx, snap in enumerate(env.steps):
        rec = snap[seat] if seat < len(snap) else None
        if not rec:
            continue
        obs = rec.get("observation") or {}
        act = rec.get("action") or {}
        if not isinstance(obs, dict):
            continue
        step = obs.get("step")
        step = int(step) if step is not None else idx
        day = step // 24
        if not (day_lo <= day <= day_hi):
            continue
        if int(obs.get("player") or seat) != seat:
            continue
        for o in act.get("market") or []:
            if o and o[0] == "SELL" and len(o) >= 3 and int(o[2] or 0) > 0:
                n_events += 1
                qty += int(o[2] or 0)
    return n_events, qty


def opp_animals(env, seat, day):
    for idx, snap in enumerate(env.steps):
        rec = snap[seat] if seat < len(snap) else None
        if not rec:
            continue
        obs = rec.get("observation") or {}
        if not isinstance(obs, dict):
            continue
        step = obs.get("step")
        step = int(step) if step is not None else idx
        if step // 24 == day and step % 24 == 0:
            farms = obs.get("farms") or []
            if len(farms) < 2:
                continue
            an = Counter()
            for row in (farms[1 - seat] or {}).get("tiles") or []:
                for t in row or []:
                    if isinstance(t, dict) and t.get("animal"):
                        an[t["animal"]] += 1
            return dict(an)
    return {}


def run_one(seed, r2_seat, opp_kind):
    if r2_seat == 0:
        r2 = load_r2(f"{opp_kind}{seed}a")
        if opp_kind == "O1":
            opp = load_r2(f"{opp_kind}{seed}b")
        elif opp_kind == "O2":
            opp = load_pool("rancher_rita")
        else:
            opp = mixed_bot
        agents = [r2, opp]
    else:
        r2 = load_r2(f"{opp_kind}{seed}a")
        if opp_kind == "O1":
            opp = load_r2(f"{opp_kind}{seed}b")
        elif opp_kind == "O2":
            opp = load_pool("rancher_rita")
        else:
            opp = mixed_bot
        agents = [opp, r2]
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run(agents)
    curve = money_curve(env, r2_seat)
    ev, q = count_listings(env, r2_seat, 15, 26)
    an20 = opp_animals(env, r2_seat, 20)
    bank = curve.get(29, {}).get("mine")
    oppb = curve.get(29, {}).get("opp")
    return {
        "seed": seed,
        "r2_seat": r2_seat,
        "opp_kind": opp_kind,
        "gap10": curve.get(10, {}).get("gap"),
        "gap15": curve.get(15, {}).get("gap"),
        "gap20": curve.get(20, {}).get("gap"),
        "gap25": curve.get(25, {}).get("gap"),
        "r2_bank": bank,
        "opp_bank": oppb,
        "margin": (bank - oppb) if bank is not None and oppb is not None else None,
        "r2_list_events_d15_26": ev,
        "r2_list_qty_d15_26": q,
        "opp_an_d20": an20,
        "curve": curve,
    }


def main():
    seeds = list(range(1, 9))
    rows = []
    for kind in ("O1", "O2", "O3"):
        for seat in (0, 1):
            for seed in seeds:
                try:
                    r = run_one(seed, seat, kind)
                    rows.append(r)
                    print(f"{kind} seat{seat} seed{seed}: gap20={r['gap20']} gap25={r['gap25']} "
                          f"m={r['margin']} ev={r['r2_list_events_d15_26']} an20={r['opp_an_d20']}", flush=True)
                except Exception as e:
                    import traceback
                    print("FAIL", kind, seat, seed, e)
                    traceback.print_exc()

    # aggregate
    print("\n=== AGGREGATE by opp_kind ===")
    import statistics as st
    for kind in ("O1", "O2", "O3"):
        sub = [r for r in rows if r["opp_kind"] == kind]
        if not sub:
            continue
        def col(k):
            vals = [r[k] for r in sub if r.get(k) is not None]
            return st.mean(vals) if vals else None
        w = sum(1 for r in sub if (r.get("margin") or 0) > 0)
        l = sum(1 for r in sub if (r.get("margin") or 0) < 0)
        t = sum(1 for r in sub if r.get("margin") == 0)
        print(f"  {kind}: n={len(sub)} WLT={w}-{l}-{t} "
              f"gap15={col('gap15')} gap20={col('gap20')} gap25={col('gap25')} "
              f"list_ev={col('r2_list_events_d15_26')} margin={col('margin')}")

    # seat split
    print("\n=== seat split margin ===")
    for kind in ("O1", "O2", "O3"):
        for seat in (0, 1):
            sub = [r for r in rows if r["opp_kind"] == kind and r["r2_seat"] == seat]
            if not sub:
                continue
            ms = [r["margin"] for r in sub if r.get("margin") is not None]
            g20 = [r["gap20"] for r in sub if r.get("gap20") is not None]
            print(f"  {kind} seat{seat}: mean_m={st.mean(ms) if ms else None} "
                  f"mean_gap20={st.mean(g20) if g20 else None} n={len(sub)}")

    # CSVs
    flat = []
    for r in rows:
        flat.append({k: v for k, v in r.items() if k != "curve" and k != "opp_an_d20"})
        flat[-1]["opp_an_d20"] = json.dumps(r.get("opp_an_d20"))
    with open(ROOT / "p4_matched_state.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(flat[0].keys()))
        w.writeheader()
        w.writerows(flat)
    # money gap summary
    with open(ROOT / "p4_money_gap.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["opp_kind", "r2_seat", "n", "mean_gap15", "mean_gap20", "mean_gap25", "mean_margin"])
        for kind in ("O1", "O2", "O3"):
            for seat in (None, 0, 1):
                sub = [r for r in rows if r["opp_kind"] == kind and (seat is None or r["r2_seat"] == seat)]
                if not sub:
                    continue
                def m(k):
                    vals = [r[k] for r in sub if r.get(k) is not None]
                    return st.mean(vals) if vals else None
                w.writerow([kind, seat if seat is not None else "both", len(sub),
                            m("gap15"), m("gap20"), m("gap25"), m("margin")])
    with open(ROOT / "p4_listing_behavior.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["opp_kind", "r2_seat", "mean_list_events_d15_26", "mean_list_qty_d15_26"])
        for kind in ("O1", "O2", "O3"):
            for seat in (0, 1):
                sub = [r for r in rows if r["opp_kind"] == kind and r["r2_seat"] == seat]
                if not sub:
                    continue
                ev = st.mean([r["r2_list_events_d15_26"] for r in sub])
                q = st.mean([r["r2_list_qty_d15_26"] for r in sub])
                w.writerow([kind, seat, ev, q])
    with open(ROOT / "p4_opponent_features.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["opp_kind", "seed", "r2_seat", "opp_an_d20"])
        for r in rows:
            w.writerow([r["opp_kind"], r["seed"], r["r2_seat"], json.dumps(r.get("opp_an_d20"))])
    print("wrote p4_*.csv")


if __name__ == "__main__":
    main()
