# -*- coding: utf-8 -*-
"""P99b: order-book / advance-sell overlay on Metav4/H3 (not V-series). Dual-gate."""
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
OUTJSON = PROJ / "_research/p99b_h3_book.json"

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


def _book(obs):
    """Return {item: [our_pending_sell_qty, opp_hint]} from market lists."""
    our = {}
    try:
        priv = (obs.get("private") or {})
        # market list is in private or market
        ml = priv.get("marketList") or priv.get("market_list") or (obs.get("market") or {}).get("list")
        if not ml:
            return our
        for o in ml or []:
            if not isinstance(o, (list, tuple)) or len(o) < 3:
                continue
            if o[0] == "SELL":
                our[o[1]] = our.get(o[1], 0) + int(o[2] or 0)
    except Exception:
        pass
    return our


def wrap_book_lead(parent, start=576, end=700, lead_frac=0.15, cap=60):
    """If our own pending SELL is large, sell a bit earlier to front-run crush."""

    def agent(obs, configuration=None):
        action = call(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            if not (start <= step <= end) or not isinstance(action, dict):
                return action
            m = [list(o) for o in (action.get("market") or [])]
            already = {o[1] for o in m if len(o) >= 2 and o[0] == "SELL"}
            book = _book(obs)
            shed = _shed(obs)
            for item, pending in book.items():
                if item in INPUTS or item in already:
                    continue
                stock = int(shed.get(item, 0) or 0)
                if stock <= 0:
                    continue
                # if we are a big seller, dump a lead tranche
                if pending >= 40:
                    q = min(stock, cap, max(1, int(pending * lead_frac)))
                    if q > 0:
                        m.append(["SELL", item, q])
                        already.add(item)
            return dict(action, market=m) if m else action
        except Exception:
            return action

    return agent


def wrap_split_crush(parent, start=624, max_lot=40):
    """Split large SELL orders to avoid self-crush (H1-like)."""

    def agent(obs, configuration=None):
        action = call(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            if step < start or not isinstance(action, dict):
                return action
            m = []
            changed = False
            for o in action.get("market") or []:
                o = list(o)
                if len(o) >= 3 and o[0] == "SELL" and o[1] in CASH:
                    q = int(o[2] or 0)
                    while q > max_lot:
                        m.append([o[0], o[1], max_lot])
                        q -= max_lot
                        changed = True
                    o[2] = q
                m.append(o)
            return dict(action, market=m) if changed else action
        except Exception:
            return action

    return agent


def wrap_term_greedy(parent, start=648, cap=60):
    def agent(obs, configuration=None):
        action = call(parent, obs, configuration)
        try:
            step = int((obs or {}).get("step", 0))
            if step < start or not isinstance(action, dict):
                return action
            m = [list(o) for o in (action.get("market") or [])]
            already = {o[1] for o in m if len(o) >= 2 and o[0] == "SELL"}
            for item, stock in _shed(obs).items():
                if item in INPUTS or item in already:
                    continue
                q = min(int(stock or 0), cap)
                if q > 0:
                    m.append(["SELL", item, q])
                    already.add(item)
            return dict(action, market=m) if m else action
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
    summary = {"n": n, "wins": wins, "win_rate": (wins / n) if n else 0, "mean_margin": (sum(margins)/len(margins)) if margins else None}
    return rows, summary


def gate_variant(name, make_cand, payload):
    rec = payload.setdefault("variants", {}).setdefault(name, {})
    for opp_name, opp_path, seeds, key in (
        ("metav4", METAV4, (1, 2, 3, 4), "metav4"),
        ("shopv7", SHOPV7, (1, 2, 3, 4), "shop"),
    ):
        print(f"\n== {name} vs {opp_name} ==", flush=True)
        rows, summary = series(make_cand, opp_path, seeds, f"{name}_{opp_name}")
        rec[key] = {"rows": rows, "summary": summary}
        print("SUM", name, opp_name, summary, flush=True)
        if key == "shop" and summary.get("win_rate", 0) < 0.5:
            rec["verdict"] = f"NO shop {summary}"
            return rec
    mv = rec.get("metav4", {}).get("summary", {})
    sh = rec.get("shop", {}).get("summary", {})
    if mv.get("win_rate", 0) >= 0.7 and sh.get("win_rate", 0) >= 0.5 and (mv.get("mean_margin") or 0) > 250:
        rec["verdict"] = "DUAL PASS strong"
    elif mv.get("win_rate", 0) >= 0.7 and sh.get("win_rate", 0) >= 0.5:
        rec["verdict"] = "DUAL PASS weak-edge"
    else:
        rec["verdict"] = f"NO metav4={mv} shop={sh}"
    return rec


def main():
    payload = {}
    if OUTJSON.exists():
        try:
            payload = json.loads(OUTJSON.read_text(encoding="utf-8"))
        except Exception:
            payload = {}
    variants = {
        "h3_book_lead": lambda tag: wrap_book_lead(wrap_term_greedy(load_mv(tag))),
        "h3_split": lambda tag: wrap_split_crush(wrap_term_greedy(load_mv(tag))),
        "book_only": lambda tag: wrap_book_lead(load_mv(tag)),
    }
    for name, make in variants.items():
        if (payload.get("variants", {}).get(name, {}).get("verdict", "") or "").startswith(("DUAL", "NO")):
            print("skip", name, flush=True)
            continue
        gate_variant(name, make, payload)
        OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n==== SUMMARY ====", flush=True)
    for name, rec in payload.get("variants", {}).items():
        print(name, rec.get("verdict"), flush=True)
    OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("WROTE", OUTJSON, flush=True)


if __name__ == "__main__":
    main()
