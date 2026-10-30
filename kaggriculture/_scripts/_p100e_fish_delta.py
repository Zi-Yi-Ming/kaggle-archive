# -*- coding: utf-8 -*-
"""P100e: track opponent SELLs via market inventory deltas → real fish/shark modes."""
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
OUTJSON = PROJ / "_research/p100e_fish_delta.json"

CASH = ("STRAWBERRY", "MELON", "MILK", "WOOL", "EGG", "TOMATO", "CARROT")
INPUTS = ("WHEAT", "FERTILIZER")
TRACK = CASH + INPUTS


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


def _mkt_inv(obs):
    inv = ((obs.get("market") or {}).get("inventory") or {})
    return {k: int(v or 0) for k, v in inv.items()}


def _mkt_px(obs):
    px = ((obs.get("market") or {}).get("prices") or {})
    return {k: float(v or 0) for k, v in px.items()}


def wrap_fish_delta(parent):
    """Track market inventory; infer opponent selling vs hoarding; switch caps."""
    st = {
        "last_inv": None,
        "last_px": None,
        "opp_sell": {k: 0 for k in TRACK},  # cumulative inferred opponent sells
        "my_sell": {k: 0 for k in TRACK},
        "mode": "NEUTRAL",
    }

    def agent(obs, configuration=None):
        action = call(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            inv = _mkt_inv(obs)
            px = _mkt_px(obs)
            # count our planned sells this turn
            my_now = {k: 0 for k in TRACK}
            if isinstance(action, dict):
                for o in action.get("market") or []:
                    if isinstance(o, (list, tuple)) and len(o) >= 3 and o[0] == "SELL":
                        item = o[1]
                        if item in my_now:
                            my_now[item] += int(o[2] or 0)

            if st["last_inv"] is not None and step > 0:
                for item in TRACK:
                    # inventory up => someone sold. Attribute beyond our last action to opp.
                    d = inv.get(item, 0) - st["last_inv"].get(item, 0)
                    if d > 0:
                        # d includes our previous turn sells already in last_inv transition
                        # crude: opponent inferred = max(0, d - 0) after we subtract our last
                        st["opp_sell"][item] += d
                for item in TRACK:
                    st["my_sell"][item] += st.pop("_last_my_" + item, 0)

            # stash our sells for next delta attribution
            for item in TRACK:
                st["_last_my_" + item] = my_now.get(item, 0)
            st["last_inv"] = inv
            st["last_px"] = px

            opp_total = sum(st["opp_sell"].values())
            my_total = sum(st["my_sell"].values())
            # FISH: we sold a lot relative to them (they're hoarding)
            # SHARK: they sold a lot (they're dumping / frontrunning)
            if step >= 400:
                if opp_total <= max(20, my_total * 0.35):
                    st["mode"] = "FISH"
                elif opp_total >= max(40, my_total * 1.4):
                    st["mode"] = "SHARK"
                else:
                    st["mode"] = "NEUTRAL"
            else:
                st["mode"] = "NEUTRAL"

            if not isinstance(action, dict):
                return action

            mode = st["mode"]
            if step >= 648:
                cap = {"FISH": 110, "SHARK": 35, "NEUTRAL": 60}[mode]
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
            elif mode == "FISH" and 560 <= step <= 671:
                m = [list(o) for o in (action.get("market") or [])]
                already = {o[1] for o in m if len(o) >= 2 and o[0] == "SELL"}
                for item, stock in _shed(obs).items():
                    if item in INPUTS or item in already:
                        continue
                    q = min(int(stock or 0), 40)
                    if q > 0:
                        m.append(["SELL", item, q])
                        already.add(item)
                if m:
                    action = dict(action, market=m)
            elif mode == "SHARK" and step >= 500:
                m = []
                changed = False
                for o in action.get("market") or []:
                    o = list(o)
                    if len(o) >= 3 and o[0] == "SELL" and o[1] in CASH:
                        q = int(o[2] or 0)
                        while q > 25:
                            m.append([o[0], o[1], 25])
                            q -= 25
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


def gate(name, make, payload):
    rec = payload.setdefault("variants", {}).setdefault(name, {})
    for opp_name, opp_path, seeds, key in (
        ("metav4", METAV4, (1, 2, 3, 4), "metav4"),
        ("shopv7", SHOPV7, (1, 2, 3, 4), "shop"),
    ):
        print(f"\n== {name} vs {opp_name} ==", flush=True)
        rows, summary = series(make, opp_path, seeds, f"{name}_{opp_name}")
        rec[key] = {"rows": rows, "summary": summary}
        print("SUM", name, key, summary, flush=True)
        if key == "shop" and summary.get("win_rate", 0) < 0.5:
            rec["verdict"] = f"NO shop {summary}"
            return rec
    mv = rec["metav4"]["summary"]
    sh = rec["shop"]["summary"]
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
    name = "fish_delta"
    if (payload.get("variants", {}).get(name, {}).get("verdict") or "").startswith(("DUAL", "NO")):
        print("skip", name, flush=True)
    else:
        gate(name, lambda tag: wrap_fish_delta(load_mv(tag)), payload)
        OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n==== SUMMARY ====", flush=True)
    for n, rec in payload.get("variants", {}).items():
        print(n, rec.get("verdict"), flush=True)
    OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("WROTE", OUTJSON, flush=True)


if __name__ == "__main__":
    main()
