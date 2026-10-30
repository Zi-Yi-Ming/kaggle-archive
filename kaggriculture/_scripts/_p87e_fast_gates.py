# -*- coding: utf-8 -*-
"""P87e fast dual-gate: D29 stagger + side-tile late-seed wheat.

Probe facts:
- Metav4 seeds.WHEAT=0 early; tile (2,4)=future PASTURE; money@day1 ~11-2853.
- Pipe-16 steals pasture tile + step0 BUY_SEED → dies vs shop.
Inventions:
- C8  D29 large SELL cap 250
- C8b D29 frontload non-input stock sells (cap 80)
- C13 side-tile wheat: late BUY_SEED at step1-2, plant on (3,4) NOT pasture (2,4),
  never rewrite day1 BUILD_PASTURE.
NOT submit.
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
OUTJSON = PROJ / "_research/p87e_fast_gates.json"


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


def wrap_d29_cap(parent):
    def agent(obs, configuration=None):
        action = call_parent(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            if step < 696 or not isinstance(action, dict):
                return action
            m = [list(o) for o in (action.get("market") or [])]
            changed = False
            for o in m:
                if len(o) >= 3 and o[0] == "SELL":
                    q = int(o[2] or 0)
                    if q >= 400:
                        o[2] = 250
                        changed = True
            return dict(action, market=m) if changed else action
        except Exception:
            return action

    return agent


def wrap_d29_front(parent):
    def agent(obs, configuration=None):
        action = call_parent(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            if not (696 <= step < 718) or not isinstance(action, dict):
                return action
            shed = (obs.get("private") or {}).get("shed") or {}
            m = [list(o) for o in (action.get("market") or [])]
            already = {o[1] for o in m if len(o) >= 2 and o[0] == "SELL"}
            added = False
            for item, n in sorted(shed.items(), key=lambda kv: -int(kv[1] or 0)):
                n = int(n or 0)
                if n <= 0 or item in already or item in ("WHEAT", "FERTILIZER"):
                    continue
                if len(m) >= 10:
                    break
                m.append(["SELL", item, min(n, 80)])
                added = True
            return dict(action, market=m) if added else action
        except Exception:
            return action

    return agent


def wrap_side_tile_wheat(parent):
    """C13: late seed + plant on side tile (3,4), preserve pasture (2,4) and day1 BUILD_PASTURE."""

    def agent(obs, configuration=None):
        action = call_parent(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            player = int((obs or {}).get("player", 0))
            if step == 0:
                agent._st = getattr(agent, "_st", {})
                inv = (obs.get("market") or {}).get("inventory") or {}
                agent._st["_w0"] = int(inv.get("WHEAT", 10000) or 10000)
            st = getattr(agent, "_st", {}).get(player)
            if st is None:
                st = {"phase": "init", "seed_bought": False, "planted": False, "fires": 0}
                if not hasattr(agent, "_st"):
                    agent._st = {}
                agent._st[player] = st
            if not isinstance(action, dict):
                return action
            priv = obs.get("private") or {}
            seeds = priv.get("seeds") or {}
            inv = (obs.get("market") or {}).get("inventory") or {}
            shops = list((obs.get("town") or {}).get("unlocked_shops") or [])
            w0 = getattr(agent, "_st", {}).get("_w0", 10000)
            dw = int(inv.get("WHEAT", w0) or w0) - int(w0)
            # abort if shop-router-like early
            if step in (1, 2, 3) and st["phase"] == "init":
                if shops.count("YARN_STORE") >= 2 or abs(dw) > 40:
                    st["phase"] = "off"
                else:
                    st["phase"] = "go"
            if st["phase"] != "go" and not st.get("planted"):
                return action
            # buy seed once at step1-2
            if step in (1, 2) and not st["seed_bought"] and int(seeds.get("WHEAT", 0) or 0) <= 0:
                money = float((obs.get("farms") or [])[player].get("money") or 0)
                if money >= 50:
                    m = [list(o) for o in (action.get("market") or [])]
                    if len(m) < 10:
                        m.append(["BUY_SEED", "WHEAT", 1])
                        action = dict(action, market=m)
                        st["seed_bought"] = True
            farm = (obs.get("farms") or [])[player]
            hands = [list(h) if h else ["PASS"] for h in (action.get("hands") or [])]
            if len(hands) < 2:
                return action
            # hand1 path: start ~ (5,4); target side tile (3,4)= tiles[4][3]
            # WEST WEST → (3,4); PLANT; WATER; later harvest without touching (2,4)
            TARGET = (3, 4)
            if step == 2 and is_pass(hands[1]):
                hands[1] = ["WEST"]
                st["fires"] = st.get("fires", 0) + 1
                return dict(action, hands=hands, farmer=action.get("farmer") or ["PASS"])
            if step in (3, 4) and st.get("fires") and is_pass(hands[1]):
                # continue walk if not yet at target
                try:
                    pos = tuple(farm["hands"][0])  # hand1 index0 in hands list
                except Exception:
                    pos = (5, 4)
                if pos[0] > TARGET[0]:
                    hands[1] = ["WEST"]
                elif pos[0] < TARGET[0]:
                    hands[1] = ["EAST"]
                elif pos[1] > TARGET[1]:
                    hands[1] = ["NORTH"]
                elif pos[1] < TARGET[1]:
                    hands[1] = ["SOUTH"]
                else:
                    hands[1] = ["PASS"]
                return dict(action, hands=hands, farmer=action.get("farmer") or ["PASS"])
            if step == 5 and st.get("fires") and is_pass(hands[1]):
                if int(seeds.get("WHEAT", 0) or 0) > 0 or st.get("seed_bought"):
                    hands[1] = ["PLANT", "WHEAT"]
                    st["planted"] = True
                else:
                    hands[1] = ["PASS"]
                return dict(action, hands=hands, farmer=action.get("farmer") or ["PASS"])
            if step == 6 and st.get("planted") and is_pass(hands[1]):
                hands[1] = ["WATER"]
                return dict(action, hands=hands, farmer=action.get("farmer") or ["PASS"])
            # day2: only water/harvest on side tile via idle hand0, no pasture ops
            if st.get("planted") and step in (49, 50, 51, 52, 53) and is_pass(hands[0]):
                try:
                    pos0 = tuple(farm["farmer"])
                except Exception:
                    pos0 = (4, 4)
                # hand0 starts near shed; walk toward (3,4) then water/harvest
                if step <= 51:
                    if pos0[0] < TARGET[0]:
                        hands[0] = ["EAST"]
                    elif pos0[0] > TARGET[0]:
                        hands[0] = ["WEST"]
                    elif pos0[1] < TARGET[1]:
                        hands[0] = ["SOUTH"]
                    elif pos0[1] > TARGET[1]:
                        hands[0] = ["NORTH"]
                    else:
                        hands[0] = ["PASS"]
                elif step == 52:
                    hands[0] = ["WATER"]
                elif step == 53:
                    hands[0] = ["HARVEST"]
                return dict(action, hands=hands, farmer=action.get("farmer") or ["PASS"])
            return action
        except Exception:
            return action

    return agent


def wrap_side_plus_d29(parent):
    return wrap_d29_cap(wrap_side_tile_wheat(parent))


def series(fac, opp_path, opp_name, seeds, label):
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
                rows.append({"seed": seed, "seat0": seat0, "error": str(e)[:200]})
    sm = {
        "label": label, "opp": opp_name, "n": n, "wins": wins,
        "win_rate": round(wins / n, 3) if n else None,
        "mean_margin": round(sum(margins) / len(margins), 1) if margins else None,
    }
    print("SUM", sm, flush=True)
    return rows, sm


def main():
    def fac_wrap(wrapfn):
        def f(tag):
            return wrapfn(load_full(METAV4, tag))

        return f

    # fast: seeds 1-2 only; escalate winners on 3-5
    variants = [
        ("C0_metav4", lambda tag: load_full(METAV4, tag)),
        ("C8_d29_cap", fac_wrap(wrap_d29_cap)),
        ("C8b_d29_front", fac_wrap(wrap_d29_front)),
        ("C13_side_tile", fac_wrap(wrap_side_tile_wheat)),
        ("C14_side_d29", fac_wrap(wrap_side_plus_d29)),
        ("P16_control", lambda tag: load_full(PIPE16, tag)),
    ]
    smoke = (1, 2)
    hold = (3, 4, 5)
    payload = {"variants": {}, "note": "P87e fast dual-gate; no submit"}
    if OUTJSON.exists():
        try:
            payload = json.loads(OUTJSON.read_text(encoding="utf-8"))
        except Exception:
            payload = {"variants": {}}
    payload.setdefault("variants", {})

    for label, fac in variants:
        print(f"\n===== {label} SMOKE =====", flush=True)
        r_mv, s_mv = series(fac, METAV4, "metav4", smoke, label)
        r_sp, s_sp = series(fac, SHOPV7, "shop_v7", smoke, label)
        r_th, s_th = series(fac, THOMAS, "thomas", (1,), label)
        payload["variants"][label] = {
            "vs_metav4": s_mv, "vs_shop_v7": s_sp, "vs_thomas": s_th,
            "rows": r_mv + r_sp + r_th,
        }
        OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        wr_mv = s_mv.get("win_rate") or 0
        wr_sp = s_sp.get("win_rate") or 0
        dual = wr_mv >= 0.6 and wr_sp >= 0.5
        print(f"DUAL_SMOKE {label}: mv={wr_mv}({s_mv.get('mean_margin')}) shop={wr_sp}({s_sp.get('mean_margin')}) th={s_th.get('win_rate')} dual={dual}", flush=True)
        if dual:
            print("ESCALATE HOLDOUT", label, flush=True)
            r2, s2 = series(fac, METAV4, "metav4_h", hold, label)
            r3, s3 = series(fac, SHOPV7, "shop_h", hold, label)
            payload["variants"][label]["hold_mv"] = s2
            payload["variants"][label]["hold_sp"] = s3
            payload["variants"][label]["holdout_dual"] = (s2.get("win_rate") or 0) >= 0.6 and (s3.get("win_rate") or 0) >= 0.5
            OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"HOLDOUT {label}: mv={s2.get('win_rate')} shop={s3.get('win_rate')} dual={payload['variants'][label]['holdout_dual']}", flush=True)

    print("\n==== P87e TABLE ====", flush=True)
    for k, v in payload["variants"].items():
        print(
            k,
            "mv", v.get("vs_metav4", {}).get("win_rate"), v.get("vs_metav4", {}).get("mean_margin"),
            "shop", v.get("vs_shop_v7", {}).get("win_rate"), v.get("vs_shop_v7", {}).get("mean_margin"),
            "thomas", v.get("vs_thomas", {}).get("win_rate"),
            "hold_dual", v.get("holdout_dual"),
            flush=True,
        )


if __name__ == "__main__":
    main()
