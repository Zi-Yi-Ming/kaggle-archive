# -*- coding: utf-8 -*-
"""P4.1: same-tier opponent swap vs R2.

Fixed: seed, R2 code, R2 seat, 720 steps.
Opponents: R2, tetsu_shape, v66, kaito58.
Metrics: money_gap d10/15/20/25, R2 listing d15-26, opp animals d20.
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


def load_file_agent(path, tag, chdir=False):
    pkg = os.path.dirname(path)
    if pkg not in sys.path:
        sys.path.insert(0, pkg)
    spec = importlib.util.spec_from_file_location(f"ag_{tag}", path)
    m = importlib.util.module_from_spec(spec)
    if chdir:
        old = os.getcwd()
        os.chdir(pkg)
        try:
            spec.loader.exec_module(m)
        finally:
            os.chdir(old)
    else:
        spec.loader.exec_module(m)
    return m.agent


def load_opp(kind, tag):
    if kind == "O1_R2":
        return load_file_agent(str(ROOT / "_push_medal" / "main.py"), tag)
    if kind == "O_shape":
        return load_file_agent(str(ROOT / "_external" / "public_nb" / "tetsu_shape" / "main.py"), tag)
    if kind == "O_v66":
        return load_file_agent(str(ROOT / "_external" / "git" / "v66" / "main.py"), tag, chdir=True)
    if kind == "O_kaito58":
        return load_file_agent(str(ROOT / "_external" / "public_nb" / "kaito_v58" / "main.py"), tag)
    raise KeyError(kind)


def money_curve(env, seat):
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
        mine = float((farms[seat] or {}).get("money") or 0)
        opp = float((farms[1 - seat] or {}).get("money") or 0)
        out[day] = {"mine": mine, "opp": opp, "gap": mine - opp}
    return out


def list_stats(env, seat, day_lo, day_hi):
    ev = qty = 0
    for idx, snap in enumerate(env.steps):
        rec = snap[seat] if seat < len(snap) else None
        if not rec:
            continue
        obs = rec.get("observation") or {}
        act = rec.get("action") or {}
        if not isinstance(obs, dict):
            continue
        step = obs.get("step")
        step = int(step) if step is not None else idx
        day = step // 24
        if not (day_lo <= day <= day_hi):
            continue
        if int(obs.get("player") or seat) != seat:
            continue
        for o in act.get("market") or []:
            if o and o[0] == "SELL" and len(o) >= 3 and int(o[2] or 0) > 0:
                ev += 1
                qty += int(o[2] or 0)
    return ev, qty


def animals_at(env, seat, day):
    for idx, snap in enumerate(env.steps):
        rec = snap[seat] if seat < len(snap) else None
        if not rec:
            continue
        obs = rec.get("observation") or {}
        if not isinstance(obs, dict):
            continue
        step = obs.get("step")
        step = int(step) if step is not None else idx
        if step // 24 == day and step % 24 == 0:
            farms = obs.get("farms") or []
            if len(farms) < 2:
                continue
            an = Counter()
            for row in (farms[1 - seat] or {}).get("tiles") or []:
                for t in row or []:
                    if isinstance(t, dict) and t.get("animal"):
                        an[t["animal"]] += 1
            return dict(an)
    return {}


def run_one(seed, r2_seat, kind):
    r2 = load_file_agent(str(ROOT / "_push_medal" / "main.py"), f"r2_{kind}_{seed}_{r2_seat}")
    opp = load_opp(kind, f"opp_{kind}_{seed}_{r2_seat}")
    agents = [r2, opp] if r2_seat == 0 else [opp, r2]
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run(agents)
    curve = money_curve(env, r2_seat)
    ev, q = list_stats(env, r2_seat, 15, 26)
    an20 = animals_at(env, r2_seat, 20)
    bank = curve.get(29, {}).get("mine")
    oppb = curve.get(29, {}).get("opp")
    return {
        "seed": seed,
        "r2_seat": r2_seat,
        "opp": kind,
        "gap10": curve.get(10, {}).get("gap"),
        "gap15": curve.get(15, {}).get("gap"),
        "gap20": curve.get(20, {}).get("gap"),
        "gap25": curve.get(25, {}).get("gap"),
        "margin": (bank - oppb) if bank is not None and oppb is not None else None,
        "r2_list_ev": ev,
        "r2_list_qty": q,
        "opp_an20": an20,
        "goose": an20.get("GOOSE", 0),
        "an_total": sum(an20.values()),
    }


def main():
    kinds = ["O1_R2", "O_shape", "O_v66", "O_kaito58"]
    rows = []
    for kind in kinds:
        for seat in (0, 1):
            for seed in range(1, 9):
                try:
                    r = run_one(seed, seat, kind)
                    rows.append(r)
                    print(f"{kind} seat{seat} s{seed}: gap15={r['gap15']} gap20={r['gap20']} "
                          f"m={r['margin']} ev={r['r2_list_ev']} an20={r['opp_an20']}", flush=True)
                except Exception as e:
                    import traceback
                    print("FAIL", kind, seat, seed, e)
                    traceback.print_exc()

    print("\n=== AGGREGATE ===")
    for kind in kinds:
        sub = [r for r in rows if r["opp"] == kind]
        if not sub:
            continue

        def m(k):
            vals = [r[k] for r in sub if r.get(k) is not None]
            return st.mean(vals) if vals else None

        neg20 = sum(1 for r in sub if (r.get("gap20") or 0) < -500)
        print(f"  {kind:12s} n={len(sub)} gap15={m('gap15'):.0f} gap20={m('gap20'):.0f} "
              f"gap25={m('gap25'):.0f} margin={m('margin'):.0f} n_gap20<-500={neg20} "
              f"list_ev={m('r2_list_ev'):.0f}")

    print("\n=== seat split margin ===")
    for kind in kinds:
        for seat in (0, 1):
            sub = [r for r in rows if r["opp"] == kind and r["r2_seat"] == seat]
            if not sub:
                continue
            ms = [r["margin"] for r in sub if r.get("margin") is not None]
            g20 = [r["gap20"] for r in sub if r.get("gap20") is not None]
            print(f"  {kind:12s} seat{seat}: m={st.mean(ms):.0f} gap20={st.mean(g20):.0f} "
                  f"neg20={sum(1 for x in g20 if x < -500)}/{len(g20)}")

    # live loss signature distance (from P3 means)
    # loss: gap20~-2117, goose~2.2, an~16.6, prem listing high
    # we only have gap20 and goose/an20 here
    print("\n=== distance to live LOSS signature (gap20, goose, an_total) ===")
    # live loss means: gap20=-2117, goose=2.2, an=16.6
    target = (-2117.0, 2.2, 16.6)
    for kind in kinds:
        sub = [r for r in rows if r["opp"] == kind]
        if not sub:
            continue
        dists = []
        for r in sub:
            g = r.get("gap20")
            if g is None:
                continue
            go = r.get("goose", 0)
            an = r.get("an_total", 0)
            d = ((g - target[0]) / 5000.0) ** 2 + ((go - target[1]) / 3.0) ** 2 + ((an - target[2]) / 5.0) ** 2
            dists.append(d ** 0.5)
        print(f"  {kind:12s} mean_sig_dist={st.mean(dists):.3f} min={min(dists):.3f}")

    # CSVs
    with open(ROOT / "p4_1_crossplay.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[k for k in rows[0].keys() if k != "opp_an20"])
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in w.fieldnames})
    print("wrote p4_1_crossplay.csv")


if __name__ == "__main__":
    main()
