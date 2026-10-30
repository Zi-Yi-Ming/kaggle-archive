# -*- coding: utf-8 -*-
"""P87 original experiments: conditional / partial HybridOpening on Metav4.

NOT submit. Dual gate: vs Metav4 AND vs shop_router v7.
Variants isolate market-only vs field-inject vs late-sell.
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
SHOPV7 = PROJ / "_external/p70_extracted/kaggriculture_shop_router_reactive_v7__0.py"
OUTJSON = PROJ / "_research/p87_conditional_hybrid.json"


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


# Pipe-16 field commands (conditional inject only if parent PASS)
_FIELD_DAY0_H1 = {2: ["WEST"], 3: ["WEST"], 4: ["WEST"], 5: ["PLANT", "WHEAT"], 6: ["WATER"]}
_FIELD_DAY2_H0 = {49: ["WEST"], 50: ["WEST"], 51: ["WEST"], 52: ["WATER"],
                 53: ["HARVEST"], 54: ["BUILD_PASTURE"], 55: ["EAST"], 56: ["EAST"], 57: ["DROP"]}


def wrap_market_wheat_only(parent):
    """M1: only step0 market + BUY_SEED WHEAT 1; never touch field tape."""

    def agent(obs, configuration=None):
        action = call_parent(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            if step == 0 and isinstance(action, dict):
                m = list(action.get("market") or [])
                if len(m) < 10:
                    m.append(["BUY_SEED", "WHEAT", 1])
                    return dict(action, market=m)
            return action
        except Exception:
            return action

    return agent


def wrap_conditional_field(parent):
    """M4: inject Pipe-16 idle-worker cmds ONLY if parent hands are PASS at that step.
    Day1 BUILD_PASTURE→WATER only if we already planted on day0 (state flag).
    Day57 extra wheat sell if hand at shed DROP and inv wheat>0.
    """

    def agent(obs, configuration=None):
        action = call_parent(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            player = int((obs or {}).get("player", 0))
            if not isinstance(action, dict):
                return action
            if step == 0:
                agent._st = getattr(agent, "_st", {})
                agent._st[player] = {"planted": False, "patched": False}
            st = getattr(agent, "_st", {}).get(player)
            if st is None:
                st = {"planted": False, "patched": False}
                if not hasattr(agent, "_st"):
                    agent._st = {}
                agent._st[player] = st
            hands = list(action.get("hands") or [])
            farmer = list(action.get("farmer") or ["PASS"])
            changed = False
            # Day0 idle hand1
            if step in _FIELD_DAY0_H1 and len(hands) >= 2:
                if hands[1] in (["PASS"], [], None) or hands[1] == ["PASS"]:
                    hands[1] = list(_FIELD_DAY0_H1[step])
                    changed = True
                    if step == 5:
                        st["planted"] = True
                    if st["planted"]:
                        st["patched"] = True
            # Day1 pasture→water only if we patched day0
            if step == 29 and st.get("patched") and len(hands) >= 3:
                if hands[2] and hands[2][0] == "BUILD_PASTURE":
                    hands[2] = ["WATER"]
                    changed = True
            # Day2 idle hand0 only if we planted
            if st.get("planted") and step in _FIELD_DAY2_H0 and hands:
                if hands[0] in (["PASS"], [], None):
                    hands[0] = list(_FIELD_DAY2_H0[step])
                    changed = True
            # Day2 late extra sell — market only, no field
            if step == 57 and len(hands) >= 1:
                farm = (obs.get("farms") or [])[player]
                shed = (obs.get("private") or {}).get("shed") or {}
                try:
                    if tuple(farm.get("hands") or [(None,)])[0] == (4, 4) and hands[0] == ["DROP"]:
                        n = int(shed.get("WHEAT", 0) or 0)
                        # only extra beyond 1 unit if we planted
                        if st.get("planted") and n > 0:
                            m = list(action.get("market") or [])
                            sold = 0
                            for o in m:
                                if len(o) >= 3 and o[0] == "SELL" and o[1] == "WHEAT":
                                    sold += int(o[2] or 0)
                            extra = max(0, n - sold)
                            if extra > 0:
                                if len(m) < 10:
                                    m.append(["SELL", "WHEAT", extra])
                                else:
                                    # bump first wheat sell
                                    for o in m:
                                        if len(o) >= 3 and o[0] == "SELL" and o[1] == "WHEAT":
                                            o[2] = int(o[2] or 0) + extra
                                            break
                                action = dict(action, market=m)
                                changed = True
                except Exception:
                    pass
            if changed:
                action = dict(action, farmer=farmer, hands=hands)
            return action
        except Exception:
            return action

    return agent


def wrap_late_sell_only(parent):
    """M3: only step57 extra wheat sell if planted tile [4][2] is WHEAT and DROP at shed."""

    def agent(obs, configuration=None):
        action = call_parent(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            player = int((obs or {}).get("player", 0))
            if step != 57 or not isinstance(action, dict):
                return action
            farm = (obs.get("farms") or [])[player]
            tiles = farm.get("tiles") or []
            site = tiles[4][2] if len(tiles) > 4 and len(tiles[4]) > 2 else None
            crop = site.get("crop") if isinstance(site, dict) else None
            hands = list(action.get("hands") or [])
            shed = (obs.get("private") or {}).get("shed") or {}
            if crop == "WHEAT" and hands and hands[0] == ["DROP"]:
                n = int(shed.get("WHEAT", 0) or 0)
                if n <= 0:
                    return action
                m = list(action.get("market") or [])
                sold = sum(int(o[2] or 0) for o in m if len(o) >= 3 and o[0] == "SELL" and o[1] == "WHEAT")
                extra = max(0, n - sold)
                if extra > 0:
                    if len(m) < 10:
                        m.append(["SELL", "WHEAT", extra])
                    else:
                        for o in m:
                            if len(o) >= 3 and o[0] == "SELL" and o[1] == "WHEAT":
                                o[2] = int(o[2] or 0) + extra
                                break
                    return dict(action, market=m)
            return action
        except Exception:
            return action

    return agent


def wrap_m1_plus_m4(parent):
    """Combined market wheat + conditional field."""

    inner = wrap_conditional_field(wrap_market_wheat_only(parent))
    return inner


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
                print(
                    f"{label} vs {opp_name} s={seed} seat0={seat0} "
                    f"c={cb:.0f} o={ob:.0f} m={m:.0f} win={win}",
                    flush=True,
                )
                rows.append({"seed": seed, "seat0": seat0, "margin": m, "win": win})
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


def main():
    print("load Metav4 parent...", flush=True)
    parent = load_full(METAV4, "metav4_parent")
    print("parent ok", parent, flush=True)

    def fac_wrap(wrapfn):
        def f(tag):
            return wrapfn(load_full(METAV4, tag))

        return f

    variants = [
        ("M0_metav4", lambda tag: load_full(METAV4, tag)),
        ("M1_market_wheat", fac_wrap(wrap_market_wheat_only)),
        ("M4_cond_field", fac_wrap(wrap_conditional_field)),
        ("M3_late_sell", fac_wrap(wrap_late_sell_only)),
        ("M14_combined", fac_wrap(wrap_m1_plus_m4)),
    ]
    seeds = (1, 2, 3)
    payload = {"variants": {}}
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
        payload["variants"][label] = {
            "vs_metav4": s_mv,
            "vs_shop_v7": s_sp,
            "rows": r_mv + r_sp,
        }
        OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        dual = (s_mv.get("wins") or 0) >= 2 and (s_sp.get("win_rate") or 0) >= 0.5
        print(
            f"DUAL_CHECK {label}: vs_mv={s_mv.get('win_rate')} vs_shop={s_sp.get('win_rate')} dual_pass={dual}",
            flush=True,
        )
        if dual:
            print("ESCALATE", label, flush=True)
            r2, s2 = series(fac, METAV4, "metav4_h", (4, 5, 6), label)
            r3, s3 = series(fac, SHOPV7, "shop_h", (4, 5, 6), label)
            payload["variants"][label]["hold_mv"] = s2
            payload["variants"][label]["hold_sp"] = s3
            OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n==== P87 TABLE ====", flush=True)
    for k, v in payload["variants"].items():
        print(
            k,
            "mv",
            v.get("vs_metav4", {}).get("win_rate"),
            v.get("vs_metav4", {}).get("mean_margin"),
            "shop",
            v.get("vs_shop_v7", {}).get("win_rate"),
            v.get("vs_shop_v7", {}).get("mean_margin"),
            flush=True,
        )


if __name__ == "__main__":
    main()
