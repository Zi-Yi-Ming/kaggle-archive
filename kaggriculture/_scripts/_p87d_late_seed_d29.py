# -*- coding: utf-8 -*-
"""P87d: probe seeds/tiles + late-seed buy + d29 stagger gates."""
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
OUTJSON = PROJ / "_research/p87d_late_seed_d29.json"
DIAGJSON = PROJ / "_research/p87d_seed_probe.json"


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


def probe_seeds():
    print("=== SEED/TILE PROBE Metav4 ===", flush=True)
    parent = load_full(METAV4, "mv_probe")
    shop = load_full(SHOPV7, "shop_probe")
    rows = []

    def wrap(fn, seat, store):
        def agent(obs, configuration=None):
            st = int((obs or {}).get("step", 0))
            if st in (0, 1, 2, 5, 6, 10, 24, 48):
                try:
                    priv = obs.get("private") or {}
                    seeds = dict(priv.get("seeds") or {})
                    shed = dict(priv.get("shed") or {})
                    farm = obs["farms"][seat]
                    tiles = farm.get("tiles") or []
                    t24 = tiles[4][2] if len(tiles) > 4 and len(tiles[4]) > 2 else None
                    hands_pos = [list(p) for p in farm.get("hands") or []]
                    store.append({
                        "step": st, "seat": seat,
                        "seeds": seeds, "shed": shed,
                        "tile_4_2": t24, "hands_pos": hands_pos,
                        "farmer": list(farm.get("farmer") or []),
                        "money": float(farm.get("money") or 0),
                    })
                except Exception as e:
                    store.append({"step": st, "seat": seat, "error": str(e)[:120]})
            return call_parent(fn, obs, configuration)

        return agent

    store = []
    env = p79.make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = 1
    env.run([wrap(parent, 0, store), wrap(shop, 1, store)])
    f = env.steps[-1]
    print(f"final money s0={f[0]['observation']['farms'][0]['money']:.0f} s1={f[1]['observation']['farms'][1]['money']:.0f}", flush=True)
    for r in store:
        if r.get("seat") == 0:
            print(f"  MV {r}", flush=True)
    rows.extend(store)
    # pipe16 for comparison
    store2 = []
    pipe = load_full(PIPE16, "pipe_probe")
    env = p79.make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = 1
    env.run([wrap(pipe, 0, store2), wrap(shop, 1, store2)])
    for r in store2:
        if r.get("seat") == 0:
            print(f"  P16 {r}", flush=True)
    rows.extend([{**r, "agent": "pipe16"} for r in store2 if r.get("seat") == 0])
    DIAGJSON.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    print("wrote", DIAGJSON, flush=True)


# ---------------------------------------------------------------------------
# Inventions
# ---------------------------------------------------------------------------
_DAY0_H1 = {2: ["WEST"], 3: ["WEST"], 4: ["WEST"], 5: ["PLANT", "WHEAT"], 6: ["WATER"]}
_DAY2_SAFE = {49: ["WEST"], 50: ["WEST"], 51: ["WEST"], 52: ["WATER"], 53: ["HARVEST"]}


def wrap_late_seed_hybrid(parent):
    """C11: do NOT touch step0 market.
    At step1-2, if seeds.WHEAT==0 and ΔWHEAT market looks calm, append BUY_SEED WHEAT 1.
    Then pasture-safe field inject on idle h1 (plant only if seed exists at step5).
    """

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
                st = {"planted": False, "seed_bought": False, "enabled": None, "fires": 0}
                if not hasattr(agent, "_st"):
                    agent._st = {}
                agent._st[player] = st
            if not isinstance(action, dict):
                return action
            priv = obs.get("private") or {}
            seeds = priv.get("seeds") or {}
            inv = (obs.get("market") or {}).get("inventory") or {}
            w0 = getattr(agent, "_st", {}).get("_w0", 10000)
            dw = int(inv.get("WHEAT", w0) or w0) - int(w0)
            shops = list((obs.get("town") or {}).get("unlocked_shops") or [])
            yarn = shops.count("YARN_STORE")
            if step in (1, 2) and st["enabled"] is None:
                st["enabled"] = (yarn < 2 and abs(dw) <= 40)
            # late seed buy at step1 or 2 only
            if step in (1, 2) and st["enabled"] and not st["seed_bought"]:
                if int(seeds.get("WHEAT", 0) or 0) <= 0:
                    m = [list(o) for o in (action.get("market") or [])]
                    if len(m) < 10 and not any(len(o) >= 2 and o[0] == "BUY_SEED" and o[1] == "WHEAT" for o in m):
                        m.append(["BUY_SEED", "WHEAT", 1])
                        action = dict(action, market=m)
                        st["seed_bought"] = True
            enable = bool(st.get("enabled")) or st.get("planted", False) or st.get("seed_bought", False)
            if not enable:
                return action
            hands = [list(h) if h else ["PASS"] for h in (action.get("hands") or [])]
            changed = False
            if step in _DAY0_H1 and len(hands) >= 2 and is_pass(hands[1]):
                # only plant if we will have seed
                cmd = list(_DAY0_H1[step])
                if step == 5 and int(seeds.get("WHEAT", 0) or 0) <= 0 and not st.get("seed_bought"):
                    cmd = ["PASS"]
                else:
                    hands[1] = cmd
                    changed = True
                    st["fires"] = st.get("fires", 0) + 1
                    if step == 5 and cmd[0] == "PLANT":
                        st["planted"] = True
                    if step != 5:
                        hands[1] = cmd
                        changed = True
            if st.get("planted") and step in _DAY2_SAFE and hands and is_pass(hands[0]):
                hands[0] = list(_DAY2_SAFE[step])
                changed = True
            if step == 57 and st.get("planted"):
                try:
                    shed = priv.get("shed") or {}
                    invs = priv.get("inventories") or []
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
    """C8: cap large D29 SELL orders to 250/turn."""

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


def wrap_d29_frontload(parent):
    """C8b invention from P80/sdy623: on day29, if parent plans large SELL later today,
    advance a capped amount NOW (when stock is in shed) — sale-advance without opening touch.
    Opposite direction of pure cap: try to win terminal money race vs Metav4 mirrors.
    """

    def agent(obs, configuration=None):
        action = call_parent(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            player = int((obs or {}).get("player", 0))
            if not (696 <= step < 718) or not isinstance(action, dict):
                return action
            priv = obs.get("private") or {}
            shed = priv.get("shed") or {}
            m = [list(o) for o in (action.get("market") or [])]
            already = {o[1] for o in m if len(o) >= 2 and o[0] == "SELL"}
            # products with stock not being sold this turn
            added = False
            for item, n in sorted(shed.items(), key=lambda kv: -int(kv[1] or 0)):
                n = int(n or 0)
                if n <= 0 or item in already:
                    continue
                if item in ("WHEAT", "FERTILIZER"):
                    continue  # keep input obligations
                if len(m) >= 10:
                    break
                m.append(["SELL", item, min(n, 80)])
                added = True
            if added:
                return dict(action, market=m)
            return action
        except Exception:
            return action

    return agent


def wrap_d29_cap_and_front(parent):
    return wrap_d29_frontload(wrap_d29_stagger(parent))


def wrap_late_seed_plus_d29(parent):
    return wrap_d29_stagger(wrap_late_seed_hybrid(parent))


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


def run_gates():
    print("\n=== P87d GATES ===", flush=True)

    def fac_wrap(wrapfn):
        def f(tag):
            return wrapfn(load_full(METAV4, tag))

        return f

    variants = [
        ("C0_metav4", lambda tag: load_full(METAV4, tag)),
        ("C11_late_seed", fac_wrap(wrap_late_seed_hybrid)),
        ("C8_d29_cap", fac_wrap(wrap_d29_stagger)),
        ("C8b_d29_front", fac_wrap(wrap_d29_frontload)),
        ("C8c_d29_both", fac_wrap(wrap_d29_cap_and_front)),
        ("C12_late_seed_d29", fac_wrap(wrap_late_seed_plus_d29)),
        ("P16_control", lambda tag: load_full(PIPE16, tag)),
    ]
    seeds = (1, 2, 3)
    payload = {"variants": {}, "note": "P87d late-seed + d29; no submit"}
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

    print("\n==== P87d TABLE ====", flush=True)
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
    if mode in ("all", "probe"):
        probe_seeds()
    if mode in ("all", "gates"):
        run_gates()


if __name__ == "__main__":
    main()
