# -*- coding: utf-8 -*-
"""P100f: build a passive 'fat fish' dummy and measure fish-eater vs plain H3 against it."""
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
OUTJSON = PROJ / "_research/p100f_fatfish_lab.json"

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


def _shed(obs):
    return dict(((obs.get("private") or {}).get("shed") or {}))


def fat_fish(obs, configuration=None):
    """Passive hoarder: plant like Metav4 early, NEVER sell cash goods. Only tiny wheat dump."""
    # reuse Metav4 actions but strip SELL of cash (and most sells)
    # load static parent once
    return _fat_fish_impl(obs, configuration)


_fat_parent = {"fn": None}


def _fat_fish_impl(obs, configuration=None):
    if _fat_parent["fn"] is None:
        _fat_parent["fn"] = load_mv("fatbase")
    action = call(_fat_parent["fn"], obs, configuration)
    if not isinstance(action, dict):
        return {"market": [], "tiles": []}
    m = []
    for o in action.get("market") or []:
        if not isinstance(o, (list, tuple)) or len(o) < 2:
            continue
        # never SELL cash; allow tiny WHEAT sell only at very end
        if o[0] == "SELL":
            step = int((obs or {}).get("step") or 0)
            if o[1] == "WHEAT" and step >= 700:
                m.append(list(o)[:3])
            # drop all other sells → true fat fish
            continue
        m.append(list(o))
    out = dict(action, market=m)
    return out


def h3_cap60(tag):
    def call_fn(fn, obs, configuration=None):
        n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)
        return fn(obs, configuration) if n > 1 else fn(obs, obs and configuration)

    parent = load_mv(tag)

    def agent(obs, configuration=None):
        action = call_fn(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            if step < 648 or not isinstance(action, dict):
                return action
            m = [list(o) for o in (action.get("market") or [])]
            already = {o[1] for o in m if len(o) >= 2 and o[0] == "SELL"}
            for item, stock in _shed(obs).items():
                if item in INPUTS or item in already:
                    continue
                q = min(int(stock or 0), 60)
                if q > 0:
                    m.append(["SELL", item, q])
                    already.add(item)
            return dict(action, market=m) if m else action
        except Exception:
            return action

    return agent


def fish_eater(tag):
    def call_fn(fn, obs, configuration=None):
        n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)
        return fn(obs, configuration) if n > 1 else fn(obs, obs and configuration)

    parent = load_mv(tag)
    st = {"last_inv": None, "opp_sell": 0, "my_sell": 0}

    def agent(obs, configuration=None):
        action = call_fn(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            inv = ((obs.get("market") or {}).get("inventory") or {})
            if st["last_inv"] is not None:
                for k, v in inv.items():
                    d = int(v or 0) - int(st["last_inv"].get(k) or 0)
                    if d > 0 and k in CASH:
                        st["opp_sell"] += d
            st["last_inv"] = dict(inv)

            # FISH if opponent sold little cash by mid-late game
            mode = "NEUTRAL"
            if step >= 400:
                if st["opp_sell"] <= 30:
                    mode = "FISH"
                elif st["opp_sell"] >= 200:
                    mode = "SHARK"

            if not isinstance(action, dict):
                return action
            if step >= 648:
                cap = {"FISH": 120, "SHARK": 35, "NEUTRAL": 60}[mode]
                m = [list(o) for o in (action.get("market") or [])]
                already = {o[1] for o in m if len(o) >= 2 and o[0] == "SELL"}
                for item, stock in _shed(obs).items():
                    if item in INPUTS or item in already:
                        continue
                    q = min(int(stock or 0), cap)
                    if q > 0:
                        m.append(["SELL", item, q])
                        already.add(item)
                if m:
                    action = dict(action, market=m)
            elif mode == "FISH" and 540 <= step <= 671:
                m = [list(o) for o in (action.get("market") or [])]
                already = {o[1] for o in m if len(o) >= 2 and o[0] == "SELL"}
                for item, stock in _shed(obs).items():
                    if item in INPUTS or item in already:
                        continue
                    q = min(int(stock or 0), 50)
                    if q > 0:
                        m.append(["SELL", item, q])
                        already.add(item)
                if m:
                    action = dict(action, market=m)
            return action
        except Exception:
            return action

    return agent


def series(make_cand, opp_fn, seeds, label):
    wins = 0
    margins = []
    rows = []
    for seed in seeds:
        for seat0 in (True, False):
            try:
                c = make_cand(f"c_{label}_{seed}_{int(seat0)}")
                o = opp_fn(f"o_{label}_{seed}_{int(seat0)}")
                if seat0:
                    b0, b1, stt, sec = p79.run(c, o, seed)
                    cb, ob = b0, b1
                else:
                    b0, b1, stt, sec = p79.run(o, c, seed)
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


def main():
    payload = {}
    print("==== H3 vs FAT FISH ====", flush=True)
    rows, s_h3 = series(h3_cap60, lambda tag: fat_fish, (1, 2, 3, 4), "h3_fat")
    print("H3 vs fatfish", s_h3, flush=True)
    print("==== FISH EATER vs FAT FISH ====", flush=True)
    rows2, s_fe = series(fish_eater, lambda tag: fat_fish, (1, 2, 3, 4), "fe_fat")
    print("FE vs fatfish", s_fe, flush=True)

    # control: each vs metav4/shop to not regress
    print("==== H3 vs metav4 control ====", flush=True)
    rows3, s_h3mv = series(h3_cap60, lambda tag: p79.load_quiet(METAV4, tag), (1, 2), "h3_mv")
    print("==== FE vs metav4 control ====", flush=True)
    rows4, s_femv = series(fish_eater, lambda tag: p79.load_quiet(METAV4, tag), (1, 2), "fe_mv")

    payload = {
        "h3_vs_fatfish": {"rows": rows, "summary": s_h3},
        "fe_vs_fatfish": {"rows": rows2, "summary": s_fe},
        "h3_vs_metav4": {"rows": rows3, "summary": s_h3mv},
        "fe_vs_metav4": {"rows": rows4, "summary": s_femv},
    }
    # decision: FE must beat H3 vs fatfish AND not lose to metav4
    fe_edge = (s_fe.get("mean_margin") or 0) - (s_h3.get("mean_margin") or 0)
    payload["fe_edge_vs_h3_on_fatfish"] = fe_edge
    if fe_edge >= 400 and (s_femv.get("mean_margin") or -1e9) >= (s_h3mv.get("mean_margin") or 0) - 80:
        payload["verdict"] = "FISH LAYER WORKS — worth packaging as next submit candidate"
    elif fe_edge > 0:
        payload["verdict"] = f"weak fish edge {fe_edge}"
    else:
        payload["verdict"] = f"no fish edge {fe_edge}"
    print("EDGE", fe_edge, "VERDICT", payload["verdict"], flush=True)
    OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("WROTE", OUTJSON, flush=True)


if __name__ == "__main__":
    main()
