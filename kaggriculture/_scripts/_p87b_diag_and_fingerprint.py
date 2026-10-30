# -*- coding: utf-8 -*-
"""P87b bold: diagnose why M4 never fires + invent opponent-fingerprint HybridOpening.

NOT submit. Dual gate vs Metav4 AND shop_router v7.
Also invent late-only layers that never touch step0 market.
"""
from __future__ import annotations

import importlib.util
import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "p79", r"D:\桌面\Kaggle\kaggriculture\_scripts\_p79_mass_gate_vs_thomas.py"
)
p79 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p79)

PROJ = Path(r"D:\桌面\Kaggle\kaggriculture")
METAV4 = PROJ / "_push_metav4_v13" / "main.py"
PIPE16 = PROJ / "_push_pipe16" / "main.py"
SHOPV7 = PROJ / "_external/p70_extracted/kaggriculture_shop_router_reactive_v7__0.py"
THOMAS = PROJ / "_push_thomas_2945" / "main.py"
OUTJSON = PROJ / "_research/p87b_fingerprint.json"
DIAGJSON = PROJ / "_research/p87b_diag.json"


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


# ---------------------------------------------------------------------------
# A. DIAG: what does Metav4 actually output at HybridOpening steps?
# ---------------------------------------------------------------------------
DIAG_STEPS = (0, 2, 5, 6, 29, 49, 53, 57)


def run_diag():
    print("=== DIAG Metav4 actions at HybridOpening steps ===", flush=True)
    parent = load_full(METAV4, "metav4_diag")
    pipe = load_full(PIPE16, "pipe16_diag")
    shop = load_full(SHOPV7, "shopv7_diag")
    rows = []

    def probe(label, a0, a1, seed, steps):
        env_steps = []
        orig_run = p79.make  # not used; wrap via custom run that records steps
        env = p79.make("kaggriculture", debug=False)
        env.configuration["episodeSteps"] = 720
        if env.info is None:
            env.info = {}
        env.info["seed"] = int(seed)
        # monkey-patch agents to log
        logs = {0: {}, 1: {}}

        def wrap(fn, seat):
            def agent(obs, configuration=None):
                act = call_parent(fn, obs, configuration)
                st = int((obs or {}).get("step", -1))
                if st in steps:
                    logs[seat][st] = {
                        "hands": act.get("hands") if isinstance(act, dict) else act,
                        "farmer": act.get("farmer") if isinstance(act, dict) else None,
                        "market": act.get("market") if isinstance(act, dict) else None,
                    }
                return act

            return agent

        env.run([wrap(a0, 0), wrap(a1, 1)])
        f = env.steps[-1]
        m0 = float(f[0]["observation"]["farms"][0]["money"])
        m1 = float(f[1]["observation"]["farms"][1]["money"])
        return logs, m0, m1

    for seed in (1, 2):
        logs, m0, m1 = probe("mv_vs_shop", parent, shop, seed, DIAG_STEPS)
        row = {"match": "metav4_vs_shop", "seed": seed, "mv_money": m0, "shop_money": m1,
               "mv_actions": {str(k): v for k, v in logs[0].items()},
               "shop_actions": {str(k): v for k, v in logs[1].items()}}
        rows.append(row)
        print(f"\n-- metav4 vs shop seed={seed} money mv={m0:.0f} shop={m1:.0f} --", flush=True)
        for st in DIAG_STEPS:
            a = logs[0].get(st)
            if a:
                print(f"  MV step{st}: hands={a['hands']} farmer={a['farmer']} market={a['market']}", flush=True)
        # opponent fingerprint at day1/2
        env = p79.make("kaggriculture", debug=False)
        env.configuration["episodeSteps"] = 720
        if env.info is None:
            env.info = {}
        env.info["seed"] = int(seed)
        fp = {}

        def wrapfp(fn, seat):
            def agent(obs, configuration=None):
                st = int((obs or {}).get("step", 0))
                if st in (0, 24, 48, 72):
                    try:
                        farms = obs["farms"]
                        me, opp = farms[seat], farms[1 - seat]
                        def farm_sig(f):
                            plants = 0
                            crops = {}
                            animals = 0
                            for row in f.get("tiles") or []:
                                for t in row:
                                    if isinstance(t, dict):
                                        if t.get("crop"):
                                            plants += 1
                                            crops[t["crop"]] = crops.get(t["crop"], 0) + 1
                                        if t.get("animal"):
                                            animals += 1
                            return {
                                "money": float(f.get("money") or 0),
                                "hands": len(f.get("hands") or []),
                                "plants": plants,
                                "crops": crops,
                                "animals": animals,
                                "quads": list(f.get("unlocked_quadrants") or []),
                            }
                        inv = (obs.get("market") or {}).get("inventory") or {}
                        prices = (obs.get("market") or {}).get("prices") or {}
                        shops = list((obs.get("town") or {}).get("unlocked_shops") or [])
                        fp[str(st)] = {
                            "me": farm_sig(me),
                            "opp": farm_sig(opp),
                            "mkt_inv": {k: int(inv.get(k, 0)) for k in ("WHEAT", "CARROT", "TOMATO", "MILK", "WOOL", "EGG", "FERTILIZER") if k in inv},
                            "mkt_px": {k: int(prices.get(k, 0)) for k in ("WHEAT", "CARROT", "TOMATO", "MILK", "WOOL", "EGG", "FERTILIZER") if k in prices},
                            "shops": shops[:6],
                        }
                    except Exception:
                        pass
                return call_parent(fn, obs, configuration)

            return agent

        env2 = p79.make("kaggriculture", debug=False)
        env2.configuration["episodeSteps"] = 720
        if env2.info is None:
            env2.info = {}
        env2.info["seed"] = int(seed)
        env2.run([wrapfp(parent, 0), wrapfp(shop, 1)])
        row["fp_mv0_shop1"] = fp
        print(f"  FP seed={seed}: {json.dumps(fp.get('48', {}), ensure_ascii=False)[:400]}", flush=True)

    # also pipe16 vs shop fingerprint (what breaks)
    for seed in (1,):
        logs, m0, m1 = probe("pipe_vs_shop", pipe, shop, seed, DIAG_STEPS)
        rows.append({"match": "pipe16_vs_shop", "seed": seed, "pipe_money": m0, "shop_money": m1,
                     "pipe_actions": {str(k): v for k, v in logs[0].items()}})
        print(f"\n-- pipe16 vs shop seed={seed} money pipe={m0:.0f} shop={m1:.0f} --", flush=True)
        for st in DIAG_STEPS:
            a = logs[0].get(st)
            if a:
                print(f"  P16 step{st}: hands={a['hands']} market={a['market']}", flush=True)

    # Metav4 self (mirror baseline)
    for seed in (1,):
        logs, m0, m1 = probe("mv_self", parent, parent, seed, DIAG_STEPS)
        rows.append({"match": "metav4_self", "seed": seed, "s0": m0, "s1": m1,
                     "s0_actions": {str(k): v for k, v in logs[0].items()}})
        print(f"\n-- metav4 self seed={seed} s0={m0:.0f} s1={m1:.0f} --", flush=True)
        for st in DIAG_STEPS:
            a = logs[0].get(st)
            if a:
                print(f"  SELF step{st}: hands={a['hands']} market={a['market']}", flush=True)

    DIAGJSON.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    print("DIAG written", DIAGJSON, flush=True)
    return rows


# ---------------------------------------------------------------------------
# B. Inventions: fingerprint-gated + late-only (never step0 market)
# ---------------------------------------------------------------------------
# Fingerprint signals from public obs that may distinguish shop-router family:
# shop_router often unlocks shops differently / plants differently / market inv differs.
# We invent several gates; dual-gate each.

_DAY0_H1 = {2: ["WEST"], 3: ["WEST"], 4: ["WEST"], 5: ["PLANT", "WHEAT"], 6: ["WATER"]}
_DAY2_H0 = {49: ["WEST"], 50: ["WEST"], 51: ["WEST"], 52: ["WATER"],
            53: ["HARVEST"], 54: ["BUILD_PASTURE"], 55: ["EAST"], 56: ["EAST"], 57: ["DROP"]}


def _farm_sig(obs, seat):
    farms = obs.get("farms") or []
    f = farms[seat] if seat < len(farms) else {}
    plants = animals = 0
    crops = {}
    for row in f.get("tiles") or []:
        for t in row:
            if isinstance(t, dict):
                if t.get("crop"):
                    plants += 1
                    crops[t["crop"]] = crops.get(t["crop"], 0) + 1
                if t.get("animal"):
                    animals += 1
    return {
        "money": float(f.get("money") or 0),
        "hands": len(f.get("hands") or []),
        "plants": plants,
        "animals": animals,
        "crops": crops,
        "quads": tuple(f.get("unlocked_quadrants") or []),
    }


def _shop_sig(obs):
    shops = list((obs.get("town") or {}).get("unlocked_shops") or [])
    inv = (obs.get("market") or {}).get("inventory") or {}
    prices = (obs.get("market") or {}).get("prices") or {}
    return {
        "shops": tuple(shops),
        "wheat_inv": int(inv.get("WHEAT", 0) or 0),
        "milk_inv": int(inv.get("MILK", 0) or 0),
        "wool_inv": int(inv.get("WOOL", 0) or 0),
        "wheat_px": int(prices.get("WHEAT", 0) or 0),
        "milk_px": int(prices.get("MILK", 0) or 0),
    }


def is_metav4_like_mirror(obs, seat, state):
    """Heuristic: opponent looks like Metav4/tape-family if:
    - early day money stays near ours (tape mirror)
    - opponent hands count tracks ours
    - opponent plant count stays low on day0-1 (Metav4 plants via cows, not field flood)
    - shop unlock pattern not dominated by YARN_STORE pair early (shop-router sheep)
    """
    opp = _farm_sig(obs, 1 - seat)
    me = _farm_sig(obs, seat)
    ss = _shop_sig(obs)
    step = int(obs.get("step", 0))
    day = step // 24
    yarn = ss["shops"].count("YARN_STORE")
    money_gap = abs(opp["money"] - me["money"])
    hands_gap = abs(opp["hands"] - me["hands"])
    # Metav4-like: money close, hands close, not early yarn store, not huge plant flood
    if day <= 2:
        if yarn >= 2:
            return False
        if hands_gap > 1:
            return False
        if money_gap > 800:
            return False
        if opp["plants"] >= 8 and day <= 1:
            return False
        return True
    # later: if yarn unlocked late or money still close, keep hybrid
    if yarn >= 2 and day >= 6:
        return False
    return money_gap < 1500


def is_shop_router_like(obs, seat, state):
    """Inverse: detect shop-router / V-lineage adversarial patterns."""
    ss = _shop_sig(obs)
    opp = _farm_sig(obs, 1 - seat)
    me = _farm_sig(obs, seat)
    step = int(obs.get("step", 0))
    day = step // 24
    shops = ss["shops"]
    # shop-router family: early multi-shop unlock, yarn/ice cream, wheat market activity
    yarn = shops.count("YARN_STORE")
    ice = shops.count("ICE_CREAM_SHOP")
    pizza = shops.count("PIZZA_SHOP")
    if day <= 3 and (yarn >= 2 or ice + pizza >= 2):
        return True
    if day <= 2 and ss["wheat_inv"] < 8000:
        # low wheat inv can mean aggressive market agent
        pass
    if opp["plants"] >= 6 and day <= 2:
        return True
    return False


def inject_hybrid_field(obs, action, state, enable):
    """Inject Pipe-16 field cmds only when enable=True AND unit is idle PASS.
    Never touch market at step0. Late extra wheat sell only if planted.
    """
    if not enable:
        return action
    if not isinstance(action, dict):
        return action
    step = int(obs.get("step", 0))
    player = int(obs.get("player", 0))
    hands = [list(h) if h else ["PASS"] for h in (action.get("hands") or [])]
    farmer = list(action.get("farmer") or ["PASS"])
    changed = False
    st = state

    def is_pass(cmd):
        return (not cmd) or cmd in (["PASS"], ["pass"]) or (isinstance(cmd, list) and (not cmd or cmd[0] == "PASS"))

    if step in _DAY0_H1 and len(hands) >= 2:
        if is_pass(hands[1]):
            hands[1] = list(_DAY0_H1[step])
            changed = True
            if step == 5:
                st["planted"] = True
    if step == 29 and st.get("planted") and len(hands) >= 3:
        if hands[2] and hands[2][0] == "BUILD_PASTURE":
            hands[2] = ["WATER"]
            changed = True
    if st.get("planted") and step in _DAY2_H0 and hands:
        if is_pass(hands[0]):
            hands[0] = list(_DAY2_H0[step])
            changed = True
    if step == 57 and st.get("planted") and hands and hands[0] == ["DROP"]:
        try:
            shed = (obs.get("private") or {}).get("shed") or {}
            n = int(shed.get("WHEAT", 0) or 0)
            m = [list(o) for o in (action.get("market") or [])]
            sold = sum(int(o[2] or 0) for o in m if len(o) >= 3 and o[0] == "SELL" and o[1] == "WHEAT")
            extra = max(0, n - sold)
            if extra > 0:
                hit = False
                for o in m:
                    if len(o) >= 3 and o[0] == "SELL" and o[1] == "WHEAT":
                        o[2] = int(o[2] or 0) + extra
                        hit = True
                        break
                if not hit and len(m) < 10:
                    m.append(["SELL", "WHEAT", extra])
                action = dict(action, market=m)
                changed = True
        except Exception:
            pass
    if changed:
        action = dict(action, farmer=farmer, hands=hands)
    return action


def wrap_fp_mirror_only(parent):
    """C1: HybridOpening field inject ONLY if opponent looks Metav4-like mirror."""

    def agent(obs, configuration=None):
        action = call_parent(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            player = int((obs or {}).get("player", 0))
            if step == 0:
                agent._st = getattr(agent, "_st", {})
            st = getattr(agent, "_st", {}).get(player)
            if st is None:
                st = {"planted": False, "enabled": True}
                if not hasattr(agent, "_st"):
                    agent._st = {}
                agent._st[player] = st
            if step <= 6:
                enable = is_metav4_like_mirror(obs, player, st)
                st["enabled"] = enable
            # once planted, keep the harvest path even if fingerprint flips
            enable = st.get("enabled", False) or st.get("planted", False)
            return inject_hybrid_field(obs, action, st, enable)
        except Exception:
            return action

    return agent


def wrap_fp_block_shop(parent):
    """C2: enable hybrid by default, but HARD DISABLE if shop-router-like signal."""

    def agent(obs, configuration=None):
        action = call_parent(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            player = int((obs or {}).get("player", 0))
            if step == 0:
                agent._st = getattr(agent, "_st", {})
            st = getattr(agent, "_st", {}).get(player)
            if st is None:
                st = {"planted": False, "enabled": True}
                if not hasattr(agent, "_st"):
                    agent._st = {}
                agent._st[player] = st
            if step <= 72:
                if is_shop_router_like(obs, player, st):
                    st["enabled"] = False
            enable = st.get("enabled", True) or st.get("planted", False)
            # if already planted before detection, finish the wheat cycle then stop
            return inject_hybrid_field(obs, action, st, enable)
        except Exception:
            return action

    return agent


def wrap_late_money_guard(parent):
    """C3 original invention: no opening field rewrite.
    Day12-18 route switch is heavy; instead: if day-end money lag vs opponent
    trajectory is large AND shops look Metav4-safe, free one idle hand to plant
    a late wheat on empty tile near shed. Bounded, reversible, never step0 market.
    """

    def agent(obs, configuration=None):
        action = call_parent(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            player = int((obs or {}).get("player", 0))
            day = step // 24
            hour = step % 24
            if step == 0:
                agent._st = getattr(agent, "_st", {})
            st = getattr(agent, "_st", {}).get(player)
            if st is None:
                st = {"mode": "off", "planted_tile": None, "phase": None}
                if not hasattr(agent, "_st"):
                    agent._st = {}
                agent._st[player] = st
            if not isinstance(action, dict):
                return action
            farms = obs.get("farms") or []
            if player >= len(farms):
                return action
            farm = farms[player]
            opp = farms[1 - player] if len(farms) > 1 else {}
            my_money = float(farm.get("money") or 0)
            opp_money = float(opp.get("money") or 0)
            lag = opp_money - my_money
            ss = _shop_sig(obs)
            yarn = ss["shops"].count("YARN_STORE")
            # Trigger window: day 10-16, lag > 800, not yarn-shop family
            if 10 <= day <= 16 and lag > 800 and yarn < 2 and st["mode"] == "off":
                st["mode"] = "plant"
                st["phase"] = "walk"
            if st["mode"] != "plant":
                return action
            hands = [list(h) if h else ["PASS"] for h in (action.get("hands") or [])]
            farmer = list(action.get("farmer") or ["PASS"])
            # find an empty non-locked tile near shed
            if st.get("planted_tile") is None:
                target = None
                for y in range(3, 7):
                    for x in range(3, 7):
                        t = farm["tiles"][y][x]
                        if t is None:
                            target = (x, y)
                            break
                    if target:
                        break
                st["planted_tile"] = target
            target = st.get("planted_tile")
            if target is None:
                st["mode"] = "off"
                return action
            # find first idle hand
            idle = None
            for i, h in enumerate(hands):
                if (not h) or h[0] == "PASS":
                    idle = i
                    break
            if idle is None:
                return action
            # position of that unit
            if idle == 0:
                pos = tuple(farm.get("farmer") or (4, 4))
            else:
                pos = tuple(farm["hands"][idle - 1]) if len(farm.get("hands") or []) >= idle else (4, 4)
            tx, ty = target
            px, py = pos
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
                seeds = (obs.get("private") or {}).get("seeds") or {}
                tile = farm["tiles"][ty][tx]
                if tile is None and int(seeds.get("WHEAT", 0) or 0) > 0:
                    cmd = ["PLANT", "WHEAT"]
                    st["phase"] = "planted"
                elif isinstance(tile, dict) and tile.get("crop") == "WHEAT":
                    if not tile.get("watered_today"):
                        cmd = ["WATER"]
                    elif int(tile.get("yield_units") or 0) > 0:
                        cmd = ["HARVEST"]
                    else:
                        cmd = ["PASS"]
                else:
                    cmd = ["PASS"]
            # only override if parent idle
            hands[idle] = cmd
            return dict(action, farmer=farmer, hands=hands)
        except Exception:
            return action

    return agent


def wrap_mirror_and_fp_shop(parent):
    """C4: both conditions must agree — mirror-like AND not shop-like."""

    def agent(obs, configuration=None):
        action = call_parent(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            player = int((obs or {}).get("player", 0))
            if step == 0:
                agent._st = getattr(agent, "_st", {})
            st = getattr(agent, "_st", {}).get(player)
            if st is None:
                st = {"planted": False, "enabled": True}
                if not hasattr(agent, "_st"):
                    agent._st = {}
                agent._st[player] = st
            if step <= 6:
                enable = is_metav4_like_mirror(obs, player, st) and (not is_shop_router_like(obs, player, st))
                st["enabled"] = enable
            enable = st.get("enabled", False) or st.get("planted", False)
            return inject_hybrid_field(obs, action, st, enable)
        except Exception:
            return action

    return agent


def series(fac, opp_path, opp_name, seeds, label, record_fp=False):
    rows = []
    wins = n = 0
    margins = []
    for seed in seeds:
        for seat0 in (True, False):
            tag = f"{label}_{opp_name}_{seed}_{int(seat0)}"
            try:
                c = fac(tag)
                try:
                    o = load_full(opp_path, f"o_{tag}")
                except Exception:
                    o = p79.load_quiet(opp_path, f"o_{tag}")
                if seat0:
                    b0, b1, stt, sec = p79.run(c, o, seed)
                    cb, ob = b0, b1
                else:
                    b0, b1, stt, sec = p79.run(o, c, seed)
                    cb, ob = b1, b0
                m = cb - ob
                win = cb > ob
                n += 1
                wins += int(win)
                margins.append(m)
                print(f"{label} vs {opp_name} s={seed} seat0={seat0} c={cb:.0f} o={ob:.0f} m={m:.0f} win={win}", flush=True)
                rows.append({"seed": seed, "seat0": seat0, "margin": m, "win": win, "cb": cb, "ob": ob})
            except Exception as e:
                print(f"FAIL {label} {opp_name} s={seed} seat0={seat0}: {e}", flush=True)
                rows.append({"seed": seed, "seat0": seat0, "error": str(e)[:180]})
    sm = {
        "label": label,
        "opp": opp_name,
        "n": n,
        "wins": wins,
        "win_rate": round(wins / n, 3) if n else None,
        "mean_margin": round(sum(margins) / len(margins), 1) if margins else None,
    }
    print("SUM", sm, flush=True)
    return rows, sm


def run_gates(diag_done=True):
    print("\n=== P87b GATES: fingerprint inventions ===", flush=True)

    def fac_wrap(wrapfn):
        def f(tag):
            return wrapfn(load_full(METAV4, tag))

        return f

    variants = [
        ("C0_metav4", lambda tag: load_full(METAV4, tag)),
        ("C1_fp_mirror", fac_wrap(wrap_fp_mirror_only)),
        ("C2_fp_block_shop", fac_wrap(wrap_fp_block_shop)),
        ("C4_mirror_and_not_shop", fac_wrap(wrap_mirror_and_fp_shop)),
        ("C5_late_money_guard", fac_wrap(wrap_late_money_guard)),
        ("P16_full_control", lambda tag: load_full(PIPE16, tag)),
    ]
    seeds = (1, 2, 3)
    payload = {"variants": {}, "note": "P87b fingerprint inventions; no submit"}
    if OUTJSON.exists():
        try:
            payload = json.loads(OUTJSON.read_text(encoding="utf-8"))
        except Exception:
            payload = {"variants": {}}
    payload.setdefault("variants", {})

    for label, fac in variants:
        print(f"\n===== {label} =====", flush=True)
        r_mv, s_mv = series(fac, METAV4, "metav4", seeds, label)
        r_sp, s_sp = series(fac, SHOPV7, "shop_v7", seeds, label)
        r_th, s_th = series(fac, THOMAS, "thomas", (1, 2), label)
        payload["variants"][label] = {
            "vs_metav4": s_mv,
            "vs_shop_v7": s_sp,
            "vs_thomas": s_th,
            "rows": r_mv + r_sp + r_th,
        }
        OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        dual = (s_mv.get("win_rate") or 0) >= 0.6 and (s_sp.get("win_rate") or 0) >= 0.5
        print(f"DUAL_CHECK {label}: vs_mv={s_mv.get('win_rate')} vs_shop={s_sp.get('win_rate')} vs_thomas={s_th.get('win_rate')} dual_pass={dual}", flush=True)
        if dual:
            print("ESCALATE HOLDOUT", label, flush=True)
            r2, s2 = series(fac, METAV4, "metav4_h", (4, 5, 6, 7), label)
            r3, s3 = series(fac, SHOPV7, "shop_h", (4, 5, 6, 7), label)
            payload["variants"][label]["hold_mv"] = s2
            payload["variants"][label]["hold_sp"] = s3
            payload["variants"][label]["holdout_dual"] = (s2.get("win_rate") or 0) >= 0.6 and (s3.get("win_rate") or 0) >= 0.5
            OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n==== P87b TABLE ====", flush=True)
    for k, v in payload["variants"].items():
        print(
            k,
            "mv", v.get("vs_metav4", {}).get("win_rate"), v.get("vs_metav4", {}).get("mean_margin"),
            "shop", v.get("vs_shop_v7", {}).get("win_rate"), v.get("vs_shop_v7", {}).get("mean_margin"),
            "thomas", v.get("vs_thomas", {}).get("win_rate"),
            "hold_dual", v.get("holdout_dual"),
            flush=True,
        )


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode in ("all", "diag"):
        run_diag()
    if mode in ("all", "gates"):
        run_gates()


if __name__ == "__main__":
    main()
