# -*- coding: utf-8 -*-
"""H3 final gate: single intervention — buy one fewer animal when opp_an(d10)>=13.

Wraps R2. Only removes one BUY_ANIMAL after trigger. No other changes.
"""
from __future__ import annotations

import csv
import importlib.util
import json
import os
import statistics as st
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make


def load_r2(tag):
    spec = importlib.util.spec_from_file_location(f"r2_{tag}", str(ROOT / "_push_medal" / "main.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def opp_animals_at_d10(obs):
    me = int(obs.get("player") or 0)
    farms = obs.get("farms") or []
    if me >= len(farms):
        return 0
    an = 0
    for row in (farms[1 - me] or {}).get("tiles") or []:
        for t in row or []:
            if isinstance(t, dict) and t.get("animal"):
                an += 1
    return an


def make_treatment(r2_agent):
    """R2 + suppress one BUY_ANIMAL after d10 if opp_an>=13 at d10."""
    state = {"triggered": False, "opp_d10": None, "blocked": False}

    def agent(obs, configuration=None):
        step = int(obs.get("step") or 0)
        day = step // 24
        if day == 10 and step % 24 == 0:
            state["opp_d10"] = opp_animals_at_d10(obs)
            if state["opp_d10"] >= 13:
                state["triggered"] = True
        action = r2_agent(obs) if r2_agent.__code__.co_argcount == 1 else r2_agent(obs, configuration)
        if not state["triggered"] or state["blocked"]:
            return action
        # suppress exactly one BUY_ANIMAL
        market = list(action.get("market") or [])
        new_m = []
        blocked = False
        for o in market:
            if (not blocked and isinstance(o, list) and len(o) >= 2 and o[0] == "BUY_ANIMAL"):
                blocked = True
                state["blocked"] = True
                continue
            new_m.append(o)
        if blocked:
            action = dict(action)
            action["market"] = new_m
        return action

    agent.state = state
    return agent


def snapshot(env, seat):
    """Money/animals/gap at day boundaries + final."""
    out = {}
    for idx, snap in enumerate(env.steps):
        rec = snap[seat] if seat < len(snap) else None
        if not rec:
            continue
        obs = rec.get("observation") or {}
        if not isinstance(obs, dict):
            continue
        step = obs.get("step")
        step = int(step) if step is not None else idx
        if step % 24 != 0:
            continue
        day = step // 24
        farms = obs.get("farms") or []
        if len(farms) < 2:
            continue

        def count_an(farm):
            n = 0
            for row in farm.get("tiles") or []:
                for t in row or []:
                    if isinstance(t, dict) and t.get("animal"):
                        n += 1
            return n

        my = float((farms[seat] or {}).get("money") or 0)
        op = float((farms[1 - seat] or {}).get("money") or 0)
        out[day] = {
            "my_money": my, "opp_money": op, "gap": my - op,
            "my_an": count_an(farms[seat] or {}),
            "opp_an": count_an(farms[1 - seat] or {}),
        }
    return out


def run_one(seed, seat, mode, opp_kind):
    r2 = load_r2(f"{mode}{opp_kind}{seed}{seat}")
    if mode == "T":
        a = make_treatment(r2)
        # wrap so env calls agent(obs) — kaggle may pass config
        def a_wrap(obs, configuration=None):
            return a(obs, configuration)
        a_wrap.state = a.state
        agent_r2 = a_wrap
    else:
        def agent_r2(obs, configuration=None):
            return r2(obs)
    if opp_kind == "R2":
        opp = load_r2(f"opp{mode}{seed}{seat}")
        def opp_wrap(obs, configuration=None):
            return opp(obs)
        opponent = opp_wrap
    else:
        # v66
        pkg = str(ROOT / "_external" / "git" / "v66")
        if pkg not in sys.path:
            sys.path.insert(0, pkg)
        old = os.getcwd()
        os.chdir(pkg)
        try:
            spec = importlib.util.spec_from_file_location(f"v66_{seed}{seat}", os.path.join(pkg, "main.py"))
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
        finally:
            os.chdir(old)
        v66a = m.agent

        def opponent(obs, configuration=None):
            return v66a(obs, configuration)

    agents = [agent_r2, opponent] if seat == 0 else [opponent, agent_r2]
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run(agents)
    snap = snapshot(env, seat)
    f = env.steps[-1]
    my = float(f[seat]["observation"]["farms"][seat]["money"])
    op = float(f[seat]["observation"]["farms"][1 - seat]["money"])
    rec = {
        "seed": seed, "seat": seat, "mode": mode, "opp": opp_kind,
        "my_final": my, "opp_final": op, "margin": my - op,
        "win": my > op, "tie": my == op,
        "opp_d10": snap.get(10, {}).get("opp_an"),
        "triggered": getattr(agent_r2, "state", {}).get("triggered") if mode == "T" else False,
        "blocked": getattr(agent_r2, "state", {}).get("blocked") if mode == "T" else False,
    }
    for d in (10, 15, 20, 25):
        s = snap.get(d) or {}
        rec[f"gap{d}"] = s.get("gap")
        rec[f"my{d}"] = s.get("my_money")
        rec[f"myan{d}"] = s.get("my_an")
        rec[f"oppan{d}"] = s.get("opp_an")
    return rec


def main():
    rows = []
    # Phase 1: R2 vs R2 (likely trigger), 4 seeds both modes both seats
    for opp_kind in ("R2",):
        for mode in ("C", "T"):
            for seat in (0, 1):
                for seed in (1, 2, 3, 4):
                    try:
                        r = run_one(seed, seat, mode, opp_kind)
                        rows.append(r)
                        print(f"{mode} {opp_kind} seat{seat} s{seed}: opp10={r['opp_d10']} "
                              f"trig={r['triggered']} blk={r['blocked']} "
                              f"gap10={r.get('gap10')} gap20={r.get('gap20')} gap25={r.get('gap25')} "
                              f"m={r['margin']:+.0f} W={r['win']}", flush=True)
                    except Exception as e:
                        import traceback
                        print("FAIL", mode, seat, seed, e)
                        traceback.print_exc()

    # Compare C vs T paired by seed+seat
    print("\n=== paired C vs T ===")
    by = {}
    for r in rows:
        by[(r["seed"], r["seat"], r["opp"])] = {}
    for r in rows:
        by[(r["seed"], r["seat"], r["opp"])][r["mode"]] = r
    dg20, dg25, dm, wl = [], [], [], []
    for k, m in by.items():
        if "C" not in m or "T" not in m:
            continue
        c, t = m["C"], m["T"]
        if c.get("gap20") is not None and t.get("gap20") is not None:
            dg20.append(t["gap20"] - c["gap20"])
        if c.get("gap25") is not None and t.get("gap25") is not None:
            dg25.append(t["gap25"] - c["gap25"])
        dm.append(t["margin"] - c["margin"])
        wl.append((c["win"], t["win"]))
        print(f"  s{k[0]} seat{k[1]}: C_gap20={c.get('gap20')} T_gap20={t.get('gap20')} "
              f"d={None if c.get('gap20') is None or t.get('gap20') is None else t['gap20']-c['gap20']:.0f} "
              f"C_m={c['margin']:+.0f} T_m={t['margin']:+.0f} trig={t.get('triggered')}")
    if dg20:
        print(f"\nmean d_gap20={st.mean(dg20):+.0f}  d_gap25={st.mean(dg25) if dg25 else None}  d_margin={st.mean(dm):+.0f}")
        print(f"T better gap20: {sum(1 for x in dg20 if x>0)}/{len(dg20)}")
        print(f"T better margin: {sum(1 for x in dm if x>0)}/{len(dm)}")

    with open(ROOT / "h3_action_counterfactual.csv", "w", newline="", encoding="utf-8") as f:
        keys = sorted({k for r in rows for k in r})
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    print("wrote h3_action_counterfactual.csv")


if __name__ == "__main__":
    main()
