# -*- coding: utf-8 -*-
"""P87c bold inventions after diag.

Finding: Metav4 hand1 is PASS on day0-2; day1 has BUILD_PASTURE on hand2.
Pipe-16 rewrites BUILD_PASTURE→WATER and dies vs shop_router.
Inventions isolate pasture-safe hybrid + market fingerprint + D29 stagger.
NOT submit. Dual gate vs Metav4 AND shop_v7.
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
OUTJSON = PROJ / "_research/p87c_inventions.json"


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


_DAY0_H1 = {2: ["WEST"], 3: ["WEST"], 4: ["WEST"], 5: ["PLANT", "WHEAT"], 6: ["WATER"]}
# Day2 harvest+restore uses hand0 only if we planted; KEEP pasture build on hand2.
_DAY2_SAFE = {49: ["WEST"], 50: ["WEST"], 51: ["WEST"], 52: ["WATER"], 53: ["HARVEST"]}


def _shops(obs):
    return list((obs.get("town") or {}).get("unlocked_shops") or [])


def _mkt(obs):
    inv = (obs.get("market") or {}).get("inventory") or {}
    px = (obs.get("market") or {}).get("prices") or {}
    return {k: int(inv.get(k, 0) or 0) for k in inv}, {k: int(px.get(k, 0) or 0) for k in px}


def wrap_diag_count(parent, label):
    """Wrap parent and count fires; used for one smoke game."""

    def agent(obs, configuration=None):
        action = call_parent(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            player = int((obs or {}).get("player", 0))
            if step == 0:
                agent._fires = 0
                agent._samples = []
            hands = action.get("hands") if isinstance(action, dict) else None
            if step in (2, 5, 29, 49) and hands is not None:
                h1 = hands[1] if len(hands) > 1 else None
                h0 = hands[0] if hands else None
                h2 = hands[2] if len(hands) > 2 else None
                agent._samples.append({
                    "step": step, "h0": h0, "h1": h1, "h2": h2,
                    "h1_pass": is_pass(h1), "h0_pass": is_pass(h0),
                })
                if step in _DAY0_H1 and len(hands) >= 2 and is_pass(h1):
                    agent._fires += 1
        except Exception:
            pass
        return action

    agent.label = label
    return agent


def wrap_pasture_safe(parent):
    """C6: HybridOpening field on idle hand1 day0-2 ONLY.
    NEVER touch day1 BUILD_PASTURE (hypothesis: that rewrite kills vs shop).
    Day2: only walk/water/harvest on idle hand0; do not rebuild pasture (parent keeps it).
    Extra wheat sell at day2 only if harvest produced stock and parent not already selling enough.
    """

    def agent(obs, configuration=None):
        action = call_parent(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            player = int((obs or {}).get("player", 0))
            if step == 0:
                agent._st = getattr(agent, "_st", {})
            st = getattr(agent, "_st", {}).get(player)
            if st is None:
                st = {"planted": False, "fires": 0}
                if not hasattr(agent, "_st"):
                    agent._st = {}
                agent._st[player] = st
            if not isinstance(action, dict):
                return action
            hands = [list(h) if h else ["PASS"] for h in (action.get("hands") or [])]
            changed = False
            # Day0 idle hand1 only
            if step in _DAY0_H1 and len(hands) >= 2 and is_pass(hands[1]):
                hands[1] = list(_DAY0_H1[step])
                changed = True
                st["fires"] = st.get("fires", 0) + 1
                if step == 5:
                    st["planted"] = True
            # Day2 idle hand0: harvest path, no pasture rewrite
            if st.get("planted") and step in _DAY2_SAFE and hands and is_pass(hands[0]):
                hands[0] = list(_DAY2_SAFE[step])
                changed = True
            # Late sell only after harvest, market only
            if step == 57 and st.get("planted") and hands and hands[0] == ["HARVEST"]:
                # harvest is step53; step57 parent hand0 is PASS on Metav4
                pass
            if step == 57 and st.get("planted"):
                try:
                    farm = (obs.get("farms") or [])[player]
                    shed = (obs.get("private") or {}).get("shed") or {}
                    inv = (obs.get("private") or {}).get("inventories") or []
                    # wheat in any inventory + shed
                    wheat = int(shed.get("WHEAT", 0) or 0)
                    for iv in inv:
                        if isinstance(iv, dict):
                            wheat += int(iv.get("WHEAT", 0) or 0)
                    m = [list(o) for o in (action.get("market") or [])]
                    sold = sum(int(o[2] or 0) for o in m if len(o) >= 3 and o[0] == "SELL" and o[1] == "WHEAT")
                    extra = max(0, min(wheat, 8) - sold)  # cap extra to 8, avoid flood
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
                action = dict(action, hands=hands, farmer=action.get("farmer") or ["PASS"])
            return action
        except Exception:
            return action

    return agent


def wrap_mkt_fp(parent):
    """C7: enable pasture-safe hybrid only when market fingerprint looks tape-mirror-like.

    Signal: after step0, if shared wheat inventory moved in a tight band consistent with
    BUY 20 / SELL 15 round-trip from BOTH sides, treat as Metav4-like and allow hybrid.
    If wheat inventory is already abnormal (shop-router shock), stay pure Metav4.
    """

    def agent(obs, configuration=None):
        action = call_parent(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            player = int((obs or {}).get("player", 0))
            if step == 0:
                agent._st = getattr(agent, "_st", {})
                inv, _ = _mkt(obs)
                agent._st["_inv0"] = dict(inv)
            st = getattr(agent, "_st", {}).get(player)
            if st is None:
                st = {"planted": False, "enabled": None, "fires": 0}
                if not hasattr(agent, "_st"):
                    agent._st = {}
                agent._st[player] = st
            inv0 = getattr(agent, "_st", {}).get("_inv0") or {}
            inv, px = _mkt(obs)
            # decide at step 1-2 using wheat inventory delta + shop unlock
            if step in (1, 2, 3) and st["enabled"] is None:
                w0 = int(inv0.get("WHEAT", 10000) or 10000)
                w1 = int(inv.get("WHEAT", w0) or w0)
                dw = w1 - w0
                yarn = _shops(obs).count("YARN_STORE")
                # Metav4 opening: each side BUY 20 SELL 15 → net -5 wheat per side if both mirror
                # shop-router may dump/buy differently; large |dw| => not safe mirror
                if yarn >= 2:
                    st["enabled"] = False
                elif abs(dw) > 40:
                    st["enabled"] = False
                else:
                    st["enabled"] = True
            enable = bool(st.get("enabled")) or st.get("planted", False)
            if not enable or not isinstance(action, dict):
                return action
            # reuse pasture-safe inject
            hands = [list(h) if h else ["PASS"] for h in (action.get("hands") or [])]
            changed = False
            if step in _DAY0_H1 and len(hands) >= 2 and is_pass(hands[1]):
                hands[1] = list(_DAY0_H1[step])
                changed = True
                st["fires"] = st.get("fires", 0) + 1
                if step == 5:
                    st["planted"] = True
            if st.get("planted") and step in _DAY2_SAFE and hands and is_pass(hands[0]):
                hands[0] = list(_DAY2_SAFE[step])
                changed = True
            if step == 57 and st.get("planted"):
                try:
                    shed = (obs.get("private") or {}).get("shed") or {}
                    invs = (obs.get("private") or {}).get("inventories") or []
                    wheat = int(shed.get("WHEAT", 0) or 0)
                    for iv in invs:
                        if isinstance(iv, dict):
                            wheat += int(iv.get("WHEAT", 0) or 0)
                    m = [list(o) for o in (action.get("market") or [])]
                    sold = sum(int(o[2] or 0) for o in m if len(o) >= 3 and o[0] == "SELL" and o[1] == "WHEAT")
                    extra = max(0, min(wheat, 8) - sold)
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
                action = dict(action, hands=hands, farmer=action.get("farmer") or ["PASS"])
            return action
        except Exception:
            return action

    return agent


def wrap_d29_stagger(parent):
    """C8 original: D29 / terminal large SELL split — from P80 loss autopsy.
    If parent market has SELL qty >= 400 of a product on day29 (step>=696) or step>=700,
    cap this-turn SELL to 250 and leave the rest to later hours / terminal auto path.
    Never touches opening. Pure market-order rewrite.
    """

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
            if changed:
                return dict(action, market=m)
            return action
        except Exception:
            return action

    return agent


def wrap_safe_plus_d29(parent):
    """C9: pasture-safe hybrid + d29 stagger."""

    return wrap_d29_stagger(wrap_pasture_safe(parent))


def wrap_mktfp_plus_d29(parent):
    """C10: market-fp hybrid + d29 stagger."""

    return wrap_d29_stagger(wrap_mkt_fp(parent))


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


def smoke_fires():
    print("=== SMOKE fire counts (seed1 seat0) ===", flush=True)
    parent = load_full(METAV4, "mv_smoke")
    for label, wrapfn in [
        ("diag_wrap", lambda p: wrap_diag_count(p, "diag")),
        ("C6_pasture_safe", wrap_pasture_safe),
        ("C7_mkt_fp", wrap_mkt_fp),
    ]:
        c = wrapfn(load_full(METAV4, f"smoke_{label}"))
        o = load_full(SHOPV7, f"smoke_opp_{label}")
        b0, b1, stt, sec = p79.run(c, o, 1)
        fires = getattr(c, "_fires", None)
        samples = getattr(c, "_samples", None)
        st = getattr(c, "_st", {})
        print(f"{label}: c={b0:.0f} o={b1:.0f} m={b0-b1:.0f} fires={fires} samples={samples} st={st}", flush=True)
        # also vs metav4
        o2 = load_full(METAV4, f"smoke_mv_{label}")
        b0, b1, stt, sec = p79.run(c, o2, 1)
        print(f"  vs metav4: c={b0:.0f} o={b1:.0f} m={b0-b1:.0f} fires={getattr(c,'_fires',None)} st0={list((getattr(c,'_st',{}) or {}).items())[:3]}", flush=True)


def run_gates():
    print("\n=== P87c GATES ===", flush=True)

    def fac_wrap(wrapfn):
        def f(tag):
            return wrapfn(load_full(METAV4, tag))

        return f

    variants = [
        ("C0_metav4", lambda tag: load_full(METAV4, tag)),
        ("C6_pasture_safe", fac_wrap(wrap_pasture_safe)),
        ("C7_mkt_fp", fac_wrap(wrap_mkt_fp)),
        ("C8_d29_stagger", fac_wrap(wrap_d29_stagger)),
        ("C9_safe_plus_d29", fac_wrap(wrap_safe_plus_d29)),
        ("C10_mktfp_plus_d29", fac_wrap(wrap_mktfp_plus_d29)),
        ("P16_control", lambda tag: load_full(PIPE16, tag)),
    ]
    seeds = (1, 2, 3)
    payload = {"variants": {}, "note": "P87c pasture-safe / mkt-fp / d29 stagger; no submit"}
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
            "vs_metav4": s_mv, "vs_shop_v7": s_sp, "vs_thomas": s_th,
            "rows": r_mv + r_sp + r_th,
        }
        OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        wr_mv = s_mv.get("win_rate") or 0
        wr_sp = s_sp.get("win_rate") or 0
        dual = wr_mv >= 0.6 and wr_sp >= 0.5
        print(f"DUAL_CHECK {label}: mv={wr_mv} shop={wr_sp} thomas={s_th.get('win_rate')} dual={dual}", flush=True)
        if dual:
            print("ESCALATE", label, flush=True)
            r2, s2 = series(fac, METAV4, "metav4_h", (4, 5, 6, 7), label)
            r3, s3 = series(fac, SHOPV7, "shop_h", (4, 5, 6, 7), label)
            payload["variants"][label]["hold_mv"] = s2
            payload["variants"][label]["hold_sp"] = s3
            payload["variants"][label]["holdout_dual"] = (s2.get("win_rate") or 0) >= 0.6 and (s3.get("win_rate") or 0) >= 0.5
            OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n==== P87c TABLE ====", flush=True)
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
    if mode in ("all", "smoke"):
        smoke_fires()
    if mode in ("all", "gates"):
        run_gates()


if __name__ == "__main__":
    main()
