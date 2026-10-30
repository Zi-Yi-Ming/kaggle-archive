# -*- coding: utf-8 -*-
"""P89 self-invention: mid-game idle labor + sell-guard + constant evolution.

Rules from P87/P88 diagnosis:
- NEVER touch step0 market (shop poison)
- NEVER steal pasture tile (2,4) / rewrite day1 BUILD_PASTURE
- NEVER redirect day0-2 cow/sheep workers
Edge space: mid-game idle PASS hands on unused tiles; sell timing when rival ripe yield high;
bounded constant mutations on Metav4 layers that are not opening.

NOT submit. Dual gate: vs Metav4 >=60% AND vs shop_v7 >=50%.
"""
from __future__ import annotations

import importlib.util
import io
import json
import random
import sys
import time
from contextlib import redirect_stdout
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
OUTJSON = PROJ / "_research/p89_self_invent.json"
PROBEJSON = PROJ / "_research/p89_idle_probe.json"


def load_full(path: Path, tag: str):
    code = path.read_text(encoding="utf-8", errors="ignore")
    ns = {"__name__": tag, "__file__": str(path), "__builtins__": __builtins__}
    with redirect_stdout(io.StringIO()):
        exec(compile(code, str(path), "exec"), ns)
    fn = ns.get("agent")
    if fn is None:
        for k, v in list(ns.items()):
            if callable(v) and "agent" in k.lower() and k not in ("load_agent",):
                fn = v
    if fn is None:
        raise RuntimeError(f"no_agent in {path}")
    n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)

    def agent(obs, configuration=None):
        return fn(obs) if n <= 1 else fn(obs, configuration)

    return agent


def argc(fn):
    return getattr(getattr(fn, "__code__", None), "co_argcount", 2)


def call_parent(fn, obs, configuration=None):
    return fn(obs, configuration) if argc(fn) > 1 else fn(obs)


def is_pass(cmd):
    if cmd is None:
        return True
    if isinstance(cmd, (list, tuple)):
        return len(cmd) == 0 or str(cmd[0]).upper() == "PASS"
    return str(cmd).upper() == "PASS"


# ---------------------------------------------------------------------------
# PROBE: when does Metav4 leave hands idle mid-game?
# ---------------------------------------------------------------------------
def probe_idle():
    print("=== IDLE HAND PROBE Metav4 ===", flush=True)
    parent = load_full(METAV4, "mv_idle")
    shop = load_full(SHOPV7, "shop_idle")
    rows = []

    def wrap(fn, seat, store):
        def agent(obs, configuration=None):
            action = call_parent(fn, obs, configuration)
            try:
                step = int((obs or {}).get("step", 0))
                if step % 6 == 0 and 24 <= step <= 600 and isinstance(action, dict):
                    farm = obs["farms"][seat]
                    priv = obs.get("private") or {}
                    seeds = priv.get("seeds") or {}
                    hands_cmd = [action.get("farmer") or ["PASS"]] + list(action.get("hands") or [])
                    pos = [tuple(farm.get("farmer") or (0, 0))] + [tuple(p) for p in farm.get("hands") or []]
                    idle = []
                    for i, cmd in enumerate(hands_cmd[: len(pos)]):
                        if is_pass(cmd):
                            idle.append({"i": i, "pos": list(pos[i]), "inv": dict((priv.get("inventories") or [{}])[i] if i < len(priv.get("inventories") or []) else {})})
                    # empty tiles not locked
                    empties = []
                    for y, row in enumerate(farm.get("tiles") or []):
                        for x, t in enumerate(row):
                            if t is None:
                                empties.append((x, y))
                    store.append({
                        "step": step, "seat": seat,
                        "idle": idle, "n_idle": len(idle),
                        "empties": empties[:12], "n_empty": len(empties),
                        "seeds": dict(seeds),
                        "money": float(farm.get("money") or 0),
                        "hands_n": len(farm.get("hands") or []),
                        "shed": dict(priv.get("shed") or {}),
                    })
            except Exception:
                pass
            return action

        return agent

    store = []
    env = p79.make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = 1
    env.run([wrap(parent, 0, store), wrap(shop, 1, store)])
    f = env.steps[-1]
    print(f"final mv={f[0]['observation']['farms'][0]['money']:.0f} shop={f[1]['observation']['farms'][1]['money']:.0f}", flush=True)
    # summarize idle by day
    by_day = {}
    for r in store:
        if r["seat"] != 0:
            continue
        day = r["step"] // 24
        by_day.setdefault(day, []).append(r)
    for day in sorted(by_day):
        rs = by_day[day]
        avg_idle = sum(x["n_idle"] for x in rs) / len(rs)
        avg_empty = sum(x["n_empty"] for x in rs) / len(rs)
        sample = rs[len(rs) // 2]
        print(f"  day{day}: avg_idle={avg_idle:.1f} avg_empty={avg_empty:.1f} sample_step={sample['step']} idle={sample['idle'][:3]} empties={sample['empties'][:6]} seeds={sample['seeds']} $={sample['money']:.0f}", flush=True)
    PROBEJSON.write_text(json.dumps(store, indent=2, ensure_ascii=False), encoding="utf-8")
    print("wrote", PROBEJSON, flush=True)


# ---------------------------------------------------------------------------
# INVENTION A: mid-game idle labor on empty tiles (days 4-16 only)
# Uses existing seeds or buys seed ONLY when money>=400 and seed==0,
# NEVER at step0-3, NEVER if yarn>=2 (shop-router), NEVER pasture tile.
# ---------------------------------------------------------------------------
PASTURE = (2, 4)  # tiles[y][x] with y=4,x=2 — reserved by Metav4


def wrap_midgame_idle(parent):
    """A1: days 4-16, if a hand is PASS and money healthy, walk to nearest empty
    non-pasture tile and PLANT WHEAT/CARROT if seeds exist; else buy 1 seed once
    (money>=400, step>=48). Water next day if still empty-ish. Never day0-3 market.
    """

    def agent(obs, configuration=None):
        action = call_parent(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            player = int((obs or {}).get("player", 0))
            day = step // 24
            if step == 0:
                agent._st = getattr(agent, "_st", {})
            st = getattr(agent, "_st", {}).get(player)
            if st is None:
                st = {"bought": False, "mode": "watch", "target": None, "worker": None, "fires": 0}
                if not hasattr(agent, "_st"):
                    agent._st = {}
                agent._st[player] = st
            if not isinstance(action, dict):
                return action
            # hard gates
            if step < 48 or day > 16:
                return action
            shops = list((obs.get("town") or {}).get("unlocked_shops") or [])
            if shops.count("YARN_STORE") >= 2:
                return action
            farms = obs.get("farms") or []
            if player >= len(farms):
                return action
            farm = farms[player]
            priv = obs.get("private") or {}
            seeds = priv.get("seeds") or {}
            money = float(farm.get("money") or 0)
            hands_cmd = [list(action.get("farmer") or ["PASS"])] + [list(h) if h else ["PASS"] for h in (action.get("hands") or [])]
            pos = [tuple(farm.get("farmer") or (4, 4))] + [tuple(p) for p in farm.get("hands") or []]
            # find empty non-pasture tile
            target = st.get("target")
            if target is None or step % 24 == 0:
                target = None
                empties = []
                for y, row in enumerate(farm.get("tiles") or []):
                    for x, t in enumerate(row):
                        if t is None and (x, y) != PASTURE:
                            # prefer NW-ish unlocked
                            empties.append((x, y))
                # score: closer to shed access
                access = ((4, 4), (5, 4), (4, 5), (5, 5))
                empties.sort(key=lambda xy: min(abs(xy[0] - a) + abs(xy[1] - b) for a, b in access))
                target = empties[0] if empties else None
                st["target"] = target
            if target is None:
                return action
            # pick idle worker (not farmer if farmer is busy — any PASS)
            wid = st.get("worker")
            if wid is None or wid >= len(hands_cmd) or not is_pass(hands_cmd[wid]):
                wid = None
                for i, cmd in enumerate(hands_cmd[: len(pos)]):
                    if is_pass(cmd):
                        wid = i
                        break
                st["worker"] = wid
            if wid is None:
                return action
            # ensure seed
            crop = "WHEAT" if int(seeds.get("WHEAT", 0) or 0) > 0 or int(seeds.get("CARROT", 0) or 0) <= 0 else "CARROT"
            if int(seeds.get(crop, 0) or 0) <= 0 and not st.get("bought"):
                if money >= 400 and step >= 48:
                    m = [list(o) for o in (action.get("market") or [])]
                    # don't add if already buying seeds this turn
                    if len(m) < 10 and not any(len(o) >= 2 and o[0] == "BUY_SEED" for o in m):
                        m.append(["BUY_SEED", "WHEAT", 1])
                        action = dict(action, market=m)
                        st["bought"] = True
                        crop = "WHEAT"
            if int(seeds.get(crop, 0) or 0) <= 0 and not st.get("bought"):
                return action
            # command idle worker toward target
            px, py = pos[wid] if wid < len(pos) else (4, 4)
            tx, ty = target
            tile = farm["tiles"][ty][tx] if ty < len(farm.get("tiles") or []) and tx < len(farm["tiles"][ty]) else "LOCKED"
            cmd = ["PASS"]
            if (px, py) != (tx, ty):
                if px < tx:
                    cmd = ["EAST"]
                elif px > tx:
                    cmd = ["WEST"]
                elif py < ty:
                    cmd = ["SOUTH"]
                elif py > ty:
                    cmd = ["NORTH"]
            else:
                if tile is None and int(seeds.get(crop, 0) or 0) > 0:
                    cmd = ["PLANT", crop]
                    st["fires"] = st.get("fires", 0) + 1
                elif isinstance(tile, dict) and tile.get("crop") == crop:
                    if not tile.get("watered_today"):
                        cmd = ["WATER"]
                    elif int(tile.get("yield_units") or 0) > 0 and day - int(tile.get("planted_day") or 0) >= 2:
                        cmd = ["HARVEST"]
                    else:
                        cmd = ["PASS"]
                else:
                    cmd = ["PASS"]
            # only override if currently PASS
            if is_pass(hands_cmd[wid]):
                hands_cmd[wid] = cmd
                action = dict(action, farmer=hands_cmd[0], hands=hands_cmd[1:])
                st["fires"] = st.get("fires", 0) + 1
            return action
        except Exception:
            return action

    return agent


def wrap_sell_guard(parent):
    """A2 original: before large SELL of cash products, if rival has high ripe
    visible yield of same product, split/delay this-turn qty (cap 80) to avoid
    self-crush. No opening change. Market list rewrite only.
    """

    def agent(obs, configuration=None):
        action = call_parent(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            player = int((obs or {}).get("player", 0))
            if step < 48 or step >= 718 or not isinstance(action, dict):
                return action
            farms = obs.get("farms") or []
            if len(farms) < 2:
                return action
            rival = farms[1 - player]
            ripe = {}
            for row in rival.get("tiles") or []:
                for t in row:
                    if not isinstance(t, dict):
                        continue
                    yld = int(t.get("yield_units") or 0)
                    if yld <= 0:
                        continue
                    item = t.get("crop")
                    if not item and t.get("animal"):
                        item = {"GOOSE": "EGG", "COW": "MILK", "SHEEP": "WOOL"}.get(t["animal"])
                    if item:
                        ripe[item] = ripe.get(item, 0) + yld
            if not ripe:
                return action
            m = [list(o) for o in (action.get("market") or [])]
            changed = False
            for o in m:
                if len(o) >= 3 and o[0] == "SELL":
                    item, q = o[1], int(o[2] or 0)
                    if q >= 30 and ripe.get(item, 0) >= 8:
                        o[2] = min(q, 80)
                        changed = True
            return dict(action, market=m) if changed else action
        except Exception:
            return action

    return agent


def wrap_idle_plus_guard(parent):
    return wrap_sell_guard(wrap_midgame_idle(parent))


def wrap_shop_adaptive_route(parent):
    """A3: day12-18 shop fingerprint — if yarn>=2 ensure we are not dumping wool
    early; if milk shops dominate, delay large MILK sell when rival milk ripe high.
    Bounded market-only. Keep parent field plan.
    """

    def agent(obs, configuration=None):
        action = call_parent(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            player = int((obs or {}).get("player", 0))
            day = step // 24
            if not (12 <= day <= 28) or not isinstance(action, dict):
                return action
            shops = list((obs.get("town") or {}).get("unlocked_shops") or [])
            yarn = shops.count("YARN_STORE")
            milk_shops = sum(s in ("PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP") for s in shops)
            farms = obs.get("farms") or []
            rival = farms[1 - player] if len(farms) > 1 else {}
            rival_wool = rival_milk = 0
            for row in rival.get("tiles") or []:
                for t in row:
                    if not isinstance(t, dict):
                        continue
                    y = int(t.get("yield_units") or 0)
                    if t.get("animal") == "SHEEP":
                        rival_wool += y
                    if t.get("animal") == "COW":
                        rival_milk += y
            m = [list(o) for o in (action.get("market") or [])]
            changed = False
            for o in m:
                if len(o) < 3 or o[0] != "SELL":
                    continue
                item, q = o[1], int(o[2] or 0)
                if yarn >= 2 and item == "WOOL" and rival_wool >= 6 and q >= 20:
                    o[2] = min(q, 40)
                    changed = True
                if milk_shops >= 2 and item == "MILK" and rival_milk >= 6 and q >= 20:
                    o[2] = min(q, 40)
                    changed = True
            return dict(action, market=m) if changed else action
        except Exception:
            return action

    return agent


# ---------------------------------------------------------------------------
# INVENTION B: constant evolution on market-only wrappers (no field rewrite)
# Search space: sell-guard thresholds, midgame trigger day, money gate
# ---------------------------------------------------------------------------
def make_evolved(th_sell_qty, rival_ripe, start_day, end_day, money_gate, seed_buy):
    def wrap(parent):
        def agent(obs, configuration=None):
            action = call_parent(parent, obs, configuration)
            try:
                step = int((obs or {}).get("step", 0))
                player = int((obs or {}).get("player", 0))
                day = step // 24
                if not isinstance(action, dict):
                    return action
                # sell guard
                if 48 <= step < 718:
                    farms = obs.get("farms") or []
                    if len(farms) >= 2:
                        rival = farms[1 - player]
                        ripe = {}
                        for row in rival.get("tiles") or []:
                            for t in row:
                                if not isinstance(t, dict):
                                    continue
                                yld = int(t.get("yield_units") or 0)
                                if yld <= 0:
                                    continue
                                item = t.get("crop") or {"GOOSE": "EGG", "COW": "MILK", "SHEEP": "WOOL"}.get(t.get("animal") or "")
                                if item:
                                    ripe[item] = ripe.get(item, 0) + yld
                        m = [list(o) for o in (action.get("market") or [])]
                        changed = False
                        for o in m:
                            if len(o) >= 3 and o[0] == "SELL" and int(o[2] or 0) >= th_sell_qty and ripe.get(o[1], 0) >= rival_ripe:
                                o[2] = max(20, th_sell_qty // 2)
                                changed = True
                        if changed:
                            action = dict(action, market=m)
                # midgame seed buy only (no field) — tests cash timing alone
                if seed_buy and start_day <= day <= end_day and step % 24 == 10:
                    priv = obs.get("private") or {}
                    seeds = priv.get("seeds") or {}
                    farm = (obs.get("farms") or [])[player]
                    money = float(farm.get("money") or 0)
                    if int(seeds.get("WHEAT", 0) or 0) <= 0 and money >= money_gate:
                        m = [list(o) for o in (action.get("market") or [])]
                        if len(m) < 10:
                            m.append(["BUY_SEED", "WHEAT", 1])
                            action = dict(action, market=m)
                return action
            except Exception:
                return action

        return agent

    return wrap


def series(fac, opp_path, opp_name, seeds, label):
    rows, margins, wins, n = [], [], 0, 0
    for seed in seeds:
        for seat0 in (True, False):
            tag = f"{label}_{opp_name}_{seed}_{int(seat0)}"
            try:
                c = fac(tag)
                o = load_full(opp_path, f"o_{tag}")
                if seat0:
                    b0, b1, st, sec = p79.run(c, o, seed)
                    cb, ob = b0, b1
                else:
                    b0, b1, st, sec = p79.run(o, c, seed)
                    cb, ob = b1, b0
                m = cb - ob
                win = cb > ob
                n += 1
                wins += int(win)
                margins.append(m)
                print(f"{label} vs {opp_name} s={seed} seat0={seat0} c={cb:.0f} o={ob:.0f} m={m:.0f} win={win}", flush=True)
                rows.append({"seed": seed, "seat0": seat0, "cb": cb, "ob": ob, "margin": m, "win": win})
            except Exception as e:
                print(f"FAIL {label} {opp_name} s={seed} seat0={seat0}: {e}", flush=True)
                rows.append({"seed": seed, "seat0": seat0, "error": str(e)[:200]})
    sm = {
        "label": label, "opp": opp_name, "n": n, "wins": wins,
        "win_rate": round(wins / n, 3) if n else None,
        "mean_margin": round(sum(margins) / len(margins), 1) if margins else None,
    }
    print("SUM", sm, flush=True)
    return rows, sm


def run_gates():
    print("\n=== P89 SELF-INVENT GATES ===", flush=True)

    def fac_wrap(wrapfn):
        def f(tag):
            return wrapfn(load_full(METAV4, tag))

        return f

    # evolved constants (pre-picked diverse set; full GA later if any signal)
    evo = [
        ("E1_sell30_ripe8", make_evolved(30, 8, 6, 14, 400, False)),
        ("E2_sell50_ripe12", make_evolved(50, 12, 6, 16, 500, False)),
        ("E3_sell20_ripe5_seed", make_evolved(20, 5, 5, 12, 350, True)),
    ]

    variants = [
        ("A0_metav4", lambda tag: load_full(METAV4, tag)),
        ("A1_midgame_idle", fac_wrap(wrap_midgame_idle)),
        ("A2_sell_guard", fac_wrap(wrap_sell_guard)),
        ("A3_shop_adaptive", fac_wrap(wrap_shop_adaptive_route)),
        ("A4_idle_plus_guard", fac_wrap(wrap_idle_plus_guard)),
        ("E1_sell30_ripe8", fac_wrap(evo[0][1])),
        ("E2_sell50_ripe12", fac_wrap(evo[1][1])),
        ("E3_sell20_ripe5_seed", fac_wrap(evo[2][1])),
        ("P16_ctrl", lambda tag: load_full(PIPE16, tag)),
    ]

    payload = {"variants": {}, "note": "P89 self-invention; no submit", "updated": time.strftime("%Y-%m-%dT%H:%M:%S")}
    if OUTJSON.exists():
        try:
            payload = json.loads(OUTJSON.read_text(encoding="utf-8"))
        except Exception:
            pass
    payload.setdefault("variants", {})

    for label, fac in variants:
        if (payload["variants"].get(label) or {}).get("vs_metav4", {}).get("n", 0) >= 4:
            print("SKIP", label, payload["variants"][label].get("vs_metav4"), flush=True)
            continue
        print(f"\n===== {label} =====", flush=True)
        r_mv, s_mv = series(fac, METAV4, "metav4", (1, 2), label)
        r_sp, s_sp = series(fac, SHOPV7, "shop_v7", (1, 2), label)
        r_th, s_th = series(fac, THOMAS, "thomas", (1,), label)
        payload["variants"][label] = {
            "vs_metav4": s_mv, "vs_shop_v7": s_sp, "vs_thomas": s_th,
            "rows": r_mv + r_sp + r_th,
        }
        payload["updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        wr_mv = s_mv.get("win_rate") or 0
        wr_sp = s_sp.get("win_rate") or 0
        dual = wr_mv >= 0.6 and wr_sp >= 0.5
        print(f"DUAL {label}: mv={wr_mv}({s_mv.get('mean_margin')}) shop={wr_sp}({s_sp.get('mean_margin')}) th={s_th.get('win_rate')} dual={dual}", flush=True)
        if dual:
            print("ESCALATE", label, flush=True)
            r2, s2 = series(fac, METAV4, "metav4_h", (3, 4, 5, 6), label)
            r3, s3 = series(fac, SHOPV7, "shop_h", (3, 4, 5, 6), label)
            payload["variants"][label]["hold_mv"] = s2
            payload["variants"][label]["hold_sp"] = s3
            payload["variants"][label]["holdout_dual"] = (s2.get("win_rate") or 0) >= 0.6 and (s3.get("win_rate") or 0) >= 0.5
            OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"HOLD {label}: mv={s2.get('win_rate')} shop={s3.get('win_rate')} dual={payload['variants'][label]['holdout_dual']}", flush=True)

    print("\n==== P89 TABLE ====", flush=True)
    for k, v in payload["variants"].items():
        print(k,
              "mv", (v.get("vs_metav4") or {}).get("win_rate"), (v.get("vs_metav4") or {}).get("mean_margin"),
              "shop", (v.get("vs_shop_v7") or {}).get("win_rate"), (v.get("vs_shop_v7") or {}).get("mean_margin"),
              "th", (v.get("vs_thomas") or {}).get("win_rate"),
              "hold", v.get("holdout_dual"), flush=True)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode in ("all", "probe"):
        probe_idle()
    if mode in ("all", "gates"):
        run_gates()


if __name__ == "__main__":
    main()
