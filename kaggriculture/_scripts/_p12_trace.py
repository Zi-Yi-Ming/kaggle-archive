# -*- coding: utf-8 -*-
"""P12: instrument R2 and P11 for day-by-day economic decomposition."""
from __future__ import annotations

import csv
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402


def load_r2():
    spec = importlib.util.spec_from_file_location(
        "r2_p12_" + str(id(object())), str(ROOT / "_push_medal" / "main.py")
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def tile_stats(tiles):
    stats = {
        "empty": 0, "locked": 0, "weed": 0, "plant": 0,
        "coop": 0, "pasture": 0,
        "animal_cow": 0, "animal_sheep": 0, "animal_goose": 0,
        "plant_ready": 0, "hungry": 0, "uncared": 0,
        "yield_units": 0, "fert_ready": 0, "dry_plant": 0,
    }
    for row in tiles or []:
        for t in row:
            if t is None:
                stats["empty"] += 1
            elif t == "LOCKED":
                stats["locked"] += 1
            elif isinstance(t, dict):
                kind = t.get("kind")
                if kind == "WEED":
                    stats["weed"] += 1
                elif kind == "PLANT":
                    stats["plant"] += 1
                    if int(t.get("yield_units") or 0) > 0:
                        stats["plant_ready"] += 1
                    if not t.get("watered_today"):
                        stats["dry_plant"] += 1
                elif kind == "COOP":
                    stats["coop"] += 1
                    if t.get("animal"):
                        stats["animal_goose"] += 1
                elif kind == "PASTURE":
                    stats["pasture"] += 1
                    a = t.get("animal")
                    if a == "COW":
                        stats["animal_cow"] += 1
                    elif a == "SHEEP":
                        stats["animal_sheep"] += 1
                a = t.get("animal")
                if a:
                    if not t.get("fed_today"):
                        stats["hungry"] += 1
                    elif not t.get("cared_today"):
                        stats["uncared"] += 1
                    stats["yield_units"] += int(t.get("yield_units") or 0)
                    if t.get("fertilizer_available"):
                        stats["fert_ready"] += 1
    return stats


def snapshot(obs):
    """Snapshot from THIS player's observation (private is own)."""
    player = int(obs.get("player") or 0)
    farms = obs.get("farms") or []
    farm = farms[player] if player < len(farms) else {}
    private = obs.get("private") or {}
    shed = dict(private.get("shed") or {})
    seeds = dict(private.get("seeds") or {})
    inventories = list(private.get("inventories") or [])
    tiles = farm.get("tiles") or []
    ts = tile_stats(tiles)
    hands = farm.get("hands") or []
    inv_total = {}
    for inv in inventories:
        for k, v in (inv or {}).items():
            inv_total[k] = inv_total.get(k, 0) + int(v or 0)
    return {
        "money": float(farm.get("money") or 0),
        "hands": len(hands),
        "hires_today": int(farm.get("hires_today") or 0),
        "unlocked": len(farm.get("unlocked_quadrants") or []),
        "shed_total": sum(int(v or 0) for v in shed.values()),
        "shed": shed,
        "seeds": seeds,
        "inv_total": inv_total,
        **ts,
    }


def market_stats(action):
    sells = {}
    buys = {}
    hires = 0
    land = 0
    for o in action.get("market") or []:
        if not o:
            continue
        op = o[0]
        if op == "SELL" and len(o) >= 3:
            sells[o[1]] = sells.get(o[1], 0) + int(o[2] or 0)
        elif op == "HIRE":
            hires += 1
        elif op == "BUY_LAND":
            land += 1
        elif op in ("BUY_ANIMAL", "BUY_PRODUCT", "BUY_SEED") and len(o) >= 3:
            key = f"{op}:{o[1]}"
            buys[key] = buys.get(key, 0) + int(o[2] or 0)
    return sells, buys, hires, land


def worker_op_stats(action):
    ops = Counter()
    cmds = [action.get("farmer") or ["PASS"]] + list(action.get("hands") or [])
    for c in cmds:
        if c:
            ops[c[0]] += 1
    return ops


def run_traced(own_factory, opp_factory, seed, own_seat, label):
    own_agent = own_factory()
    opp_agent = opp_factory()
    agents = [None, None]
    agents[own_seat] = own_agent
    agents[1 - own_seat] = opp_agent

    day_acc = {}
    day_snaps = {}

    def wrap(inner, is_own):
        def wrapped(obs, configuration=None):
            step = int(obs.get("step") or 0)
            day = step // 24
            action = inner(obs, configuration)
            if is_own:
                acc = day_acc.setdefault(day, {
                    "sell_req": {}, "buy_req": {}, "hires": 0, "land": 0, "ops": {},
                })
                sells, buys, hires, land = market_stats(action)
                for k, v in sells.items():
                    acc["sell_req"][k] = acc["sell_req"].get(k, 0) + v
                for k, v in buys.items():
                    acc["buy_req"][k] = acc["buy_req"].get(k, 0) + v
                acc["hires"] += hires
                acc["land"] += land
                ops = worker_op_stats(action)
                for k, v in ops.items():
                    acc["ops"][k] = acc["ops"].get(k, 0) + v
                if True:
                    # keep latest snapshot per day (covers last agent-called step)
                    day_snaps[day] = snapshot(obs)
            return action
        return wrapped

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run([
        wrap(agents[0], own_seat == 0),
        wrap(agents[1], own_seat == 1),
    ])

    f = env.steps[-1]
    final_my = float(f[own_seat]["observation"]["farms"][own_seat]["money"])
    final_opp = float(f[own_seat]["observation"]["farms"][1 - own_seat]["money"])

    opp_money = {}
    for idx, s in enumerate(env.steps):
        rec = s[own_seat]
        if not rec:
            continue
        obs = rec.get("observation") or {}
        step = int(obs.get("step") or idx)
        farms = obs.get("farms") or []
        if len(farms) >= 2:
            opp_money[step // 24] = float(farms[1 - own_seat].get("money") or 0)

    rows = []
    for day in range(30):
        snap = day_snaps.get(day) or {}
        acc = day_acc.get(day) or {}
        prev = day_snaps.get(day - 1) or {}
        cash_delta = None
        if day > 0 and snap.get("money") is not None and prev.get("money") is not None:
            cash_delta = snap["money"] - prev["money"]
        om = opp_money.get(day)
        rows.append({
            "label": label, "seed": seed, "seat": own_seat, "day": day,
            "money": snap.get("money"), "cash_delta": cash_delta,
            "opp_money": om,
            "gap": (snap["money"] - om) if snap.get("money") is not None and om is not None else None,
            "hands": snap.get("hands"), "unlocked": snap.get("unlocked"),
            "shed_total": snap.get("shed_total"), "plant": snap.get("plant"),
            "empty": snap.get("empty"), "weed": snap.get("weed"),
            "coop": snap.get("coop"), "pasture": snap.get("pasture"),
            "animal_cow": snap.get("animal_cow"), "animal_sheep": snap.get("animal_sheep"),
            "animal_goose": snap.get("animal_goose"),
            "hungry": snap.get("hungry"), "uncared": snap.get("uncared"),
            "yield_units": snap.get("yield_units"), "fert_ready": snap.get("fert_ready"),
            "dry_plant": snap.get("dry_plant"),
            "shed": json.dumps(snap.get("shed") or {}, ensure_ascii=False),
            "seeds": json.dumps(snap.get("seeds") or {}, ensure_ascii=False),
            "inv": json.dumps(snap.get("inv_total") or {}, ensure_ascii=False),
            "sell_req": json.dumps(acc.get("sell_req") or {}, ensure_ascii=False),
            "buy_req": json.dumps(acc.get("buy_req") or {}, ensure_ascii=False),
            "hires_req": acc.get("hires"), "land_req": acc.get("land"),
            "ops": json.dumps(acc.get("ops") or {}, ensure_ascii=False),
        })

    meta = {
        "label": label, "seed": seed, "seat": own_seat,
        "final_my": final_my, "final_opp": final_opp, "margin": final_my - final_opp,
    }
    return rows, meta


def p11_factory():
    from p11_planner import planner as pmod
    pmod._PLANNER = None
    return pmod.agent


def main():
    all_rows = []
    metas = []
    for seat in (0, 1):
        for seed in (1, 2, 3):
            rows, meta = run_traced(p11_factory, load_r2, seed, seat, "P11")
            all_rows.extend(rows)
            metas.append(meta)
            print(f"P11 s{seed} seat{seat}: {meta['final_my']:.0f} vs {meta['final_opp']:.0f} m={meta['margin']:+.0f}", flush=True)

            rows, meta = run_traced(load_r2, p11_factory, seed, seat, "R2")
            all_rows.extend(rows)
            metas.append(meta)
            print(f"R2  s{seed} seat{seat}: {meta['final_my']:.0f} vs {meta['final_opp']:.0f} m={meta['margin']:+.0f}", flush=True)

    out = ROOT / "p12_day_traces.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        w.writeheader()
        w.writerows(all_rows)
    out2 = ROOT / "p12_run_meta.csv"
    with open(out2, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(metas[0].keys()))
        w.writeheader()
        w.writerows(metas)
    print("wrote", out.name, out2.name, "rows", len(all_rows))


if __name__ == "__main__":
    main()
