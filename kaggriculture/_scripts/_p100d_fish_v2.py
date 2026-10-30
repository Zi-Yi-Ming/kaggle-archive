# -*- coding: utf-8 -*-
"""P100d Fish Eater v2: fingerprint from farms[1-player], mode switch on H3 base."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "p79", r"D:\桌面\Kaggle\kaggriculture\_scripts\_p79_mass_gate_vs_thomas.py"
)
p79 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p79)

PROJ = Path(r"D:\桌面\Kaggle\kaggriculture")
METAV4 = PROJ / "_push_metav4_v13" / "main.py"
SHOPV7 = PROJ / "_external/p70_extracted/kaggriculture_shop_router_reactive_v7__0.py"
THOMAS = PROJ / "_push_thomas_2945" / "main.py"
PIPE16 = PROJ / "_push_pipe16" / "main.py"
OUTJSON = PROJ / "_research/p100d_fish_v2.json"

CASH = ("STRAWBERRY", "MELON", "MILK", "WOOL", "EGG", "TOMATO", "CARROT")
INPUTS = ("WHEAT", "FERTILIZER")


def load_mv(tag: str):
    code = METAV4.read_text(encoding="utf-8", errors="ignore")
    ns = {"__name__": tag, "__file__": str(METAV4), "__builtins__": __builtins__}
    exec(compile(code, str(METAV4), "exec"), ns)
    fn = ns.get("agent")
    n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)

    def agent(obs, configuration=None):
        return fn(obs) if n <= 1 else fn(obs, configuration)

    return agent


def call(fn, obs, configuration=None):
    n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)
    return fn(obs, configuration) if n > 1 else fn(obs, obs and configuration)


def _my_shed(obs):
    return dict(((obs.get("private") or {}).get("shed") or {}))


def _farm(obs, idx):
    farms = (obs.get("farms") or [])
    if 0 <= idx < len(farms) and isinstance(farms[idx], dict):
        return farms[idx]
    return {}


def _tile_stats(farm):
    plants = 0
    mature = 0
    pasture = 0
    crops = {}
    for row in farm.get("tiles") or []:
        if not isinstance(row, list):
            continue
        for cell in row:
            if not isinstance(cell, dict):
                continue
            kind = cell.get("kind")
            if kind == "PLANT":
                plants += 1
                crop = cell.get("crop")
                if crop:
                    crops[crop] = crops.get(crop, 0) + 1
                # mature proxy: planted_day old enough
                pd = cell.get("planted_day")
                if isinstance(pd, (int, float)) and (obs_day_safe(farm) - pd) >= 3:
                    mature += 1
            elif kind == "PASTURE":
                pasture += 1
    return plants, mature, pasture, crops


def obs_day_safe(farm):
    return 0


def fingerprint(obs):
    me = int((obs.get("player") if obs.get("player") is not None else 0))
    opp_idx = 1 - me
    of = _farm(obs, opp_idx)
    mf = _farm(obs, me)
    step = int((obs.get("step") or 0))
    day = int((obs.get("day") or step // 24))

    o_money = float(of.get("money") or 0)
    m_money = float(mf.get("money") or 0)
    o_hands = len(of.get("hands") or [])
    o_plants, o_mature, o_pasture, o_crops = _tile_stats(of)

    # FAT FISH: high inventory-value still planted / low money velocity
    # money high + many mature unconverted = hoarder
    # money low + many plants = still investing (not fish yet)
    # Use ratio: mature plants vs cash. If lots of crop sitting and cash not growing -> fish.
    crop_load = o_plants + o_pasture
    # passive: few hires, few hands late in game
    passive = 0.0
    if step >= 200 and o_hands <= 0:
        passive += 0.4
    if step >= 300 and o_money < m_money * 0.6:
        # behind on cash and still holding fields -> might dump or might be fish
        passive += 0.1
    if o_plants >= 15 and o_mature >= 8 and step >= 500:
        # lots of mature standing crop late = hoarding
        passive += 0.5
    if o_pasture >= 6 and step >= 400 and o_money < 5000:
        passive += 0.2
    passive = min(1.0, passive)

    # SHARK: money much higher mid-game (already cashing) or high money early
    shark = 0.0
    if step >= 300 and o_money > m_money * 1.25:
        shark += 0.5
    if step >= 500 and o_money > 20000:
        shark += 0.4
    shark = min(1.0, shark)

    return {
        "step": step,
        "mode_raw": {"passive": passive, "shark": shark, "o_money": o_money, "m_money": m_money,
                     "o_plants": o_plants, "o_mature": o_mature, "o_hands": o_hands},
    }


def mode_of(fp):
    p = fp["mode_raw"]
    if p["passive"] >= 0.55:
        return "FISH"
    if p["shark"] >= 0.55:
        return "SHARK"
    return "NEUTRAL"


def wrap_fish_v2(parent):
    def agent(obs, configuration=None):
        action = call(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            fp = fingerprint(obs)
            mode = mode_of(fp)
            if not isinstance(action, dict):
                return action

            if step >= 648:
                # FISH: greedy dump; SHARK: careful; NEUTRAL: H3 cap 60
                cap = {"FISH": 100, "SHARK": 40, "NEUTRAL": 60}[mode]
                m = [list(o) for o in (action.get("market") or [])]
                already = {o[1] for o in m if len(o) >= 2 and o[0] == "SELL"}
                for item, stock in _my_shed(obs).items():
                    if item in INPUTS or item in already:
                        continue
                    q = min(int(stock or 0), cap)
                    if q > 0:
                        m.append(["SELL", item, q])
                        already.add(item)
                if m:
                    action = dict(action, market=m)
            elif mode == "FISH" and 576 <= step <= 671:
                # advance lead tranche on hoarder
                m = [list(o) for o in (action.get("market") or [])]
                already = {o[1] for o in m if len(o) >= 2 and o[0] == "SELL"}
                for item, stock in _my_shed(obs).items():
                    if item in INPUTS or item in already:
                        continue
                    q = min(int(stock or 0), 35)
                    if q > 0:
                        m.append(["SELL", item, q])
                        already.add(item)
                if m:
                    action = dict(action, market=m)
            elif mode == "SHARK" and step >= 500:
                # split sells
                m = []
                changed = False
                for o in action.get("market") or []:
                    o = list(o)
                    if len(o) >= 3 and o[0] == "SELL" and o[1] in CASH:
                        q = int(o[2] or 0)
                        while q > 30:
                            m.append([o[0], o[1], 30])
                            q -= 30
                            changed = True
                        o[2] = q
                    m.append(o)
                if changed:
                    action = dict(action, market=m)
            return action
        except Exception:
            return action

    return agent


def series(make_cand, opp_path, seeds, label):
    wins = 0
    margins = []
    rows = []
    for seed in seeds:
        for seat0 in (True, False):
            try:
                c = make_cand(f"c_{label}_{seed}_{int(seat0)}")
                o = p79.load_quiet(opp_path, f"o_{label}_{seed}_{int(seat0)}")
                if seat0:
                    b0, b1, st, sec = p79.run(c, o, seed)
                    cb, ob = b0, b1
                else:
                    b0, b1, st, sec = p79.run(o, c, seed)
                    ob, cb = b0, b1
                margin = cb - ob
                win = cb > ob
                wins += int(win)
                margins.append(margin)
                rows.append({"seed": seed, "seat0": seat0, "cand": cb, "opp": ob, "margin": margin, "win": win})
                print(f"{label} s={seed} seat0={seat0} {cb:.0f}:{ob:.0f} m={margin:.0f} win={win} {sec}s", flush=True)
            except Exception as e:
                rows.append({"seed": seed, "seat0": seat0, "error": str(e)[:180]})
                print(f"FAIL {label} s={seed}: {e}", flush=True)
    n = len([r for r in rows if "win" in r])
    summary = {"n": n, "wins": wins, "win_rate": (wins / n) if n else 0,
               "mean_margin": (sum(margins) / len(margins)) if margins else None}
    return rows, summary


def gate(name, make, payload):
    rec = payload.setdefault("variants", {}).setdefault(name, {})
    for opp_name, opp_path, seeds, key in (
        ("metav4", METAV4, (1, 2, 3, 4), "metav4"),
        ("shopv7", SHOPV7, (1, 2, 3, 4), "shop"),
        ("thomas", THOMAS, (1, 2), "thomas"),
    ):
        if not opp_path.exists():
            print("skip missing", opp_name, flush=True)
            continue
        print(f"\n== {name} vs {opp_name} ==", flush=True)
        rows, summary = series(make, opp_path, seeds, f"{name}_{opp_name}")
        rec[key] = {"rows": rows, "summary": summary}
        print("SUM", name, key, summary, flush=True)
        if key == "shop" and summary.get("win_rate", 0) < 0.5:
            rec["verdict"] = f"NO shop {summary}"
            return rec
    mv = rec.get("metav4", {}).get("summary", {})
    sh = rec.get("shop", {}).get("summary", {})
    if mv.get("win_rate", 0) >= 0.7 and sh.get("win_rate", 0) >= 0.5 and (mv.get("mean_margin") or 0) > 300:
        rec["verdict"] = "DUAL PASS strong"
    elif mv.get("win_rate", 0) >= 0.6 and sh.get("win_rate", 0) >= 0.5:
        rec["verdict"] = "DUAL PASS weak"
    else:
        rec["verdict"] = f"NO mv={mv} sh={sh}"
    return rec


def main():
    payload = {}
    if OUTJSON.exists():
        try:
            payload = json.loads(OUTJSON.read_text(encoding="utf-8"))
        except Exception:
            payload = {}
    variants = {
        "fish_v2": lambda tag: wrap_fish_v2(load_mv(tag)),
    }
    for name, make in variants.items():
        if (payload.get("variants", {}).get(name, {}).get("verdict") or "").startswith(("DUAL", "NO")):
            print("skip", name, flush=True)
            continue
        gate(name, make, payload)
        OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n==== SUMMARY ====", flush=True)
    for name, rec in payload.get("variants", {}).items():
        print(name, rec.get("verdict"), flush=True)
    OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("WROTE", OUTJSON, flush=True)


if __name__ == "__main__":
    main()
