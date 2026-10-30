# -*- coding: utf-8 -*-
"""H3 Phase 1: opponent-visible production → future economics.

Uses 33 live R2 episodes. No agent change.
Predicts: own money at d20/d25 and money_gap d20 from features at d10/d12/d15.
"""
from __future__ import annotations

import csv
import json
import statistics as st
from collections import Counter
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
REP = ROOT / "_external" / "replays"


def snap_farm(farm):
    an = Counter()
    pl = Counter()
    empty = 0
    for row in farm.get("tiles") or []:
        for t in row or []:
            if t is None:
                empty += 1
            elif isinstance(t, dict):
                if t.get("animal"):
                    an[t["animal"]] += 1
                elif t.get("kind") == "PLANT" and t.get("crop"):
                    pl[t["crop"]] += 1
    return {
        "money": float(farm.get("money") or 0),
        "quads": len(farm.get("unlocked_quadrants") or []),
        "empty": empty,
        "goose": an.get("GOOSE", 0),
        "cow": an.get("COW", 0),
        "sheep": an.get("SHEEP", 0),
        "an": sum(an.values()),
        "plants": sum(pl.values()),
        "straw": pl.get("STRAWBERRY", 0),
        "wheat": pl.get("WHEAT", 0),
        "melon": pl.get("MELON", 0),
        "tomato": pl.get("TOMATO", 0),
        "carrot": pl.get("CARROT", 0),
    }


def extract(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    teams = (data.get("info") or {}).get("TeamNames") or []
    if "ZiYiMing" not in teams:
        return None
    me = teams.index("ZiYiMing")
    opp = 1 - me
    rew = data.get("rewards") or [0, 0]
    my, op = float(rew[me]), float(rew[opp])
    steps = data.get("steps") or []
    days = {}
    # plant rate: new plants between day boundaries
    prev_plants = None
    prev_an = None
    for idx, snap in enumerate(steps):
        if me >= len(snap):
            continue
        rec = snap[me] or {}
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
        mine = snap_farm(farms[me] or {})
        theirs = snap_farm(farms[opp] or {})
        shops_n = len((obs.get("town") or {}).get("unlocked_shops") or [])
        plant_rate_o = None
        an_rate_o = None
        if prev_plants is not None:
            plant_rate_o = theirs["plants"] - prev_plants[1]
            an_rate_o = theirs["an"] - prev_an[1]
        days[day] = {
            "gap": mine["money"] - theirs["money"],
            "my_money": mine["money"],
            "opp_money": theirs["money"],
            "my_an": mine["an"], "opp_an": theirs["an"],
            "my_straw": mine["straw"], "opp_straw": theirs["straw"],
            "my_wheat": mine["wheat"], "opp_wheat": theirs["wheat"],
            "my_melon": mine["melon"], "opp_melon": theirs["melon"],
            "my_cow": mine["cow"], "opp_cow": theirs["cow"],
            "my_goose": mine["goose"], "opp_goose": theirs["goose"],
            "my_sheep": mine["sheep"], "opp_sheep": theirs["sheep"],
            "my_plants": mine["plants"], "opp_plants": theirs["plants"],
            "opp_plant_rate": plant_rate_o,
            "opp_an_rate": an_rate_o,
            "shops_n": shops_n,
        }
        prev_plants = (mine["plants"], theirs["plants"])
        prev_an = (mine["an"], theirs["an"])
    return {
        "file": path.name,
        "win": my > op,
        "margin": my - op,
        "days": days,
    }


def rank_corr(xs, ys):
    """Spearman via ranks; None if constant."""
    n = len(xs)
    if n < 4:
        return None
    if len(set(xs)) <= 1 or len(set(ys)) <= 1:
        return None
    def ranks(v):
        order = sorted(range(n), key=lambda i: v[i])
        r = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j + 1 < n and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    rx, ry = ranks(xs), ranks(ys)
    mx, my_ = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my_) for a, b in zip(rx, ry))
    dx = sum((a - mx) ** 2 for a in rx) ** 0.5
    dy = sum((b - my_) ** 2 for b in ry) ** 0.5
    if dx == 0 or dy == 0:
        return None
    return num / (dx * dy)


def main():
    eps = []
    for p in sorted(REP.glob("episode-*.json")):
        try:
            e = extract(p)
        except Exception as ex:
            print("fail", p.name, ex)
            continue
        if e:
            eps.append(e)
    print(f"episodes={len(eps)} W={sum(1 for e in eps if e['win'])} L={sum(1 for e in eps if not e['win'])}")

    # Feature tables at day 10 and 12, targets gap20 / my_money20 / my_money25
    rows = []
    for e in eps:
        d10 = e["days"].get(10)
        d12 = e["days"].get(12)
        d20 = e["days"].get(20)
        d25 = e["days"].get(25)
        if not (d10 and d12 and d20):
            continue
        row = {
            "file": e["file"], "win": e["win"], "margin": e["margin"],
            "t_gap20": d20["gap"], "t_my20": d20["my_money"],
            "t_my25": d25["my_money"] if d25 else None,
            "t_opp20": d20["opp_money"],
        }
        for src, d in (("d10", d10), ("d12", d12)):
            for k, v in d.items():
                if k in ("gap", "my_money", "opp_money"):
                    row[f"{src}_{k}"] = v
                else:
                    row[f"{src}_{k}"] = v
        rows.append(row)

    print(f"usable rows={len(rows)}")

    # Predictive: rank corr of each feature at d10/d12 with gap20 and my_money20
    print("\n=== rank corr with gap20 (all episodes) ===")
    feats = []
    for src in ("d10", "d12"):
        for k in ("opp_an", "opp_straw", "opp_wheat", "opp_melon", "opp_cow", "opp_goose",
                  "opp_sheep", "opp_plants", "opp_plant_rate", "my_an", "my_straw",
                  "my_plants", "my_money", "gap", "shops_n"):
            key = f"{src}_{k}"
            if key not in rows[0]:
                continue
            xs = [r[key] for r in rows if r.get(key) is not None]
            ys = [r["t_gap20"] for r in rows if r.get(key) is not None]
            if len(xs) != len(ys) or len(xs) < 8:
                continue
            # align
            pairs = [(r[key], r["t_gap20"]) for r in rows if r.get(key) is not None]
            xs = [a for a, b in pairs]
            ys = [b for a, b in pairs]
            rho = rank_corr(xs, ys)
            if rho is not None:
                feats.append({"feature": key, "target": "gap20", "rho": rho, "n": len(xs)})
                print(f"  {key:22s} rho={rho:+.3f} n={len(xs)}")

    print("\n=== rank corr with my_money20 ===")
    for src in ("d10", "d12"):
        for k in ("opp_an", "opp_straw", "opp_plants", "opp_plant_rate", "my_an", "my_plants", "my_money"):
            key = f"{src}_{k}"
            pairs = [(r[key], r["t_my20"]) for r in rows if r.get(key) is not None]
            if len(pairs) < 8:
                continue
            xs, ys = zip(*pairs)
            rho = rank_corr(list(xs), list(ys))
            if rho is not None:
                feats.append({"feature": key, "target": "my_money20", "rho": rho, "n": len(xs)})
                print(f"  {key:22s} rho={rho:+.3f} n={len(xs)}")

    # Incremental: does opp feature improve over own-only?
    # Compare |rho| of best own vs best opp vs combined proxy
    def best_abs(target):
        own = [f for f in feats if f["target"] == target and f["feature"].split("_", 1)[1].startswith("my_") or (f["target"] == target and "gap" in f["feature"] and f["feature"].startswith("d1"))]
        opp = [f for f in feats if f["target"] == target and "_opp_" in f["feature"]]
        # fix own filter
        own = [f for f in feats if f["target"] == target and any(f["feature"].endswith(s) for s in
               ("_my_an", "_my_straw", "_my_plants", "_my_money", "_gap", "_shops_n"))]
        opp = [f for f in feats if f["target"] == target and "_opp_" in f["feature"]]
        bo = max((abs(f["rho"]), f) for f in own) if own else None
        bp = max((abs(f["rho"]), f) for f in opp) if opp else None
        return bo, bp

    print("\n=== best |rho| own vs opp ===")
    for target in ("gap20", "my_money20"):
        bo, bp = best_abs(target)
        print(f"  {target}: own={bo} opp={bp}")

    # WIN vs LOSS mean opponent features at d10/d12
    print("\n=== WIN vs LOSS opponent features ===")
    wins = [r for r in rows if r["win"]]
    losses = [r for r in rows if not r["win"]]
    for key in ("d10_opp_straw", "d10_opp_an", "d10_opp_plants", "d10_opp_plant_rate",
                "d12_opp_straw", "d12_opp_an", "d12_opp_cow", "d12_opp_goose",
                "d10_my_straw", "d10_my_an", "d10_gap"):
        if key not in rows[0]:
            continue
        wv = [r[key] for r in wins if r.get(key) is not None]
        lv = [r[key] for r in losses if r.get(key) is not None]
        if wv and lv:
            print(f"  {key:22s} win={st.mean(wv):8.1f} lose={st.mean(lv):8.1f} d={st.mean(wv)-st.mean(lv):+8.1f}")

    # lagged: opp_straw d10 → gap d20 already in corr
    # counterfactual candidates: only if |rho|>0.4 for opp features
    cands = [f for f in feats if "_opp_" in f["feature"] and abs(f["rho"]) >= 0.4]
    print(f"\n=== counterfactual candidates |rho|>=0.4: {len(cands)} ===")
    for c in cands:
        print(" ", c)

    # CSVs
    with open(ROOT / "h3_opponent_features.csv", "w", newline="", encoding="utf-8") as f:
        keys = sorted(rows[0].keys())
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    with open(ROOT / "h3_predictive_signal.csv", "w", newline="", encoding="utf-8") as f:
        if feats:
            w = csv.DictWriter(f, fieldnames=["feature", "target", "rho", "n"])
            w.writeheader()
            w.writerows(feats)
    with open(ROOT / "h3_counterfactual_candidates.csv", "w", newline="", encoding="utf-8") as f:
        if cands:
            w = csv.DictWriter(f, fieldnames=["feature", "target", "rho", "n"])
            w.writeheader()
            w.writerows(cands)
        else:
            f.write("feature,target,rho,n\n")
    print("wrote 3 CSVs")


if __name__ == "__main__":
    main()
