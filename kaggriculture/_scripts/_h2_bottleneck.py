# -*- coding: utf-8 -*-
"""H2 Phase 1: decision bottleneck / option-set proxy on R2 trajectories.

Uses live R2 replays (WIN/LOSS) + optional local R2-vs-finn.
Does not modify any agent.
"""
from __future__ import annotations

import csv
import json
import statistics as st
from collections import Counter
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
REP = ROOT / "_external" / "replays"


def farm_snapshot(farm):
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
        "an_total": sum(an.values()),
        "plants": sum(pl.values()),
        "straw": pl.get("STRAWBERRY", 0),
        "wheat": pl.get("WHEAT", 0),
        "melon": pl.get("MELON", 0),
    }


def option_proxy(snap, shops_n):
    """Heuristic option count 0-5. Higher = more viable future routes.

    Not a true game-theoretic option set — documented proxy.
    """
    score = 0
    # cash headroom
    if snap["money"] >= 2000:
        score += 1
    if snap["money"] >= 5000:
        score += 1
    # land still expandable
    if snap["quads"] < 3:
        score += 1
    # empty tiles still available for new crops/animals
    if snap["empty"] >= 15:
        score += 1
    # not fully specialized yet (mixed or still building)
    kinds = sum(1 for k in ("goose", "cow", "sheep") if snap[k] > 0)
    if kinds <= 2 and snap["an_total"] < 14:
        score += 1
    # shop info still arriving
    if shops_n < 6:
        score += 1
    return min(score, 6)


def analyze_episode(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    teams = (data.get("info") or {}).get("TeamNames") or []
    if "ZiYiMing" not in teams:
        return None
    me = teams.index("ZiYiMing")
    opp = 1 - me
    rew = data.get("rewards") or [0, 0]
    my, op = float(rew[me]), float(rew[opp])
    win = my > op
    steps = data.get("steps") or []
    days = {}
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
        mine = farm_snapshot(farms[me] or {})
        theirs = farm_snapshot(farms[opp] or {})
        shops_n = len((obs.get("town") or {}).get("unlocked_shops") or [])
        gap = mine["money"] - theirs["money"]
        days[day] = {
            "gap": gap,
            "cash": mine["money"],
            "opp_cash": theirs["money"],
            "quads": mine["quads"],
            "empty": mine["empty"],
            "goose": mine["goose"],
            "cow": mine["cow"],
            "sheep": mine["sheep"],
            "an": mine["an_total"],
            "plants": mine["plants"],
            "shops_n": shops_n,
            "option": option_proxy(mine, shops_n),
            "opp_an": theirs["an_total"],
            "opp_goose": theirs["goose"],
        }
    # first day gap permanently <= -1000 until end
    perm_neg = None
    for d in sorted(days):
        if days[d]["gap"] <= -1000:
            if all(days[x]["gap"] <= -1000 for x in sorted(days) if x >= d):
                perm_neg = d
                break
    # first day option proxy drops to <=1 and stays
    perm_opt = None
    for d in sorted(days):
        if days[d]["option"] <= 1:
            if all(days[x]["option"] <= 1 for x in sorted(days) if x >= d):
                perm_opt = d
                break
    return {
        "file": path.name,
        "opp": teams[opp] if opp < len(teams) else "?",
        "win": win,
        "margin": my - op,
        "days": days,
        "first_perm_neg_gap": perm_neg,
        "first_perm_low_option": perm_opt,
    }


def main():
    eps = []
    for p in sorted(REP.glob("episode-*.json")):
        try:
            e = analyze_episode(p)
        except Exception as ex:
            print("fail", p.name, ex)
            continue
        if e:
            eps.append(e)
    wins = [e for e in eps if e["win"]]
    losses = [e for e in eps if not e["win"]]
    print(f"episodes={len(eps)} W={len(wins)} L={len(losses)}")

    # timeline means
    print("\n=== mean by day: WIN vs LOSS ===")
    print(f"{'day':>4} {'W_gap':>8} {'L_gap':>8} {'W_opt':>6} {'L_opt':>6} {'W_cash':>8} {'L_cash':>8} {'W_an':>5} {'L_an':>5} {'W_shops':>7} {'L_shops':>7}")
    for day in range(0, 30):
        wg = [e["days"][day]["gap"] for e in wins if day in e["days"]]
        lg = [e["days"][day]["gap"] for e in losses if day in e["days"]]
        if not wg or not lg:
            continue
        wo = [e["days"][day]["option"] for e in wins if day in e["days"]]
        lo = [e["days"][day]["option"] for e in losses if day in e["days"]]
        wc = [e["days"][day]["cash"] for e in wins if day in e["days"]]
        lc = [e["days"][day]["cash"] for e in losses if day in e["days"]]
        wa = [e["days"][day]["an"] for e in wins if day in e["days"]]
        la = [e["days"][day]["an"] for e in losses if day in e["days"]]
        ws = [e["days"][day]["shops_n"] for e in wins if day in e["days"]]
        ls = [e["days"][day]["shops_n"] for e in losses if day in e["days"]]
        print(f"{day:4d} {st.mean(wg):8.0f} {st.mean(lg):8.0f} {st.mean(wo):6.2f} {st.mean(lo):6.2f} "
              f"{st.mean(wc):8.0f} {st.mean(lc):8.0f} {st.mean(wa):5.1f} {st.mean(la):5.1f} "
              f"{st.mean(ws):7.1f} {st.mean(ls):7.1f}")

    # permanent negative gap / low option
    print("\n=== first permanent gap<=-1000 ===")
    for label, grp in (("WIN", wins), ("LOSS", losses)):
        days = [e["first_perm_neg_gap"] for e in grp if e["first_perm_neg_gap"] is not None]
        print(f"  {label}: n={len(days)}/{len(grp)} values={days}")

    print("\n=== first permanent option<=1 ===")
    for label, grp in (("WIN", wins), ("LOSS", losses)):
        days = [e["first_perm_low_option"] for e in grp if e["first_perm_low_option"] is not None]
        print(f"  {label}: n={len(days)}/{len(grp)} values={days}")

    # d10 option distribution
    print("\n=== option proxy at d8/d10/d12/d15 ===")
    for day in (8, 10, 12, 15):
        wo = [e["days"][day]["option"] for e in wins if day in e["days"]]
        lo = [e["days"][day]["option"] for e in losses if day in e["days"]]
        print(f"  d{day}: WIN {wo}  LOSS {lo}")

    # CSVs
    with open(ROOT / "h2_win_loss_timeline.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["file", "win", "day", "gap", "cash", "option", "quads", "empty", "an", "goose", "cow", "sheep", "plants", "shops_n"])
        for e in eps:
            for day, d in sorted(e["days"].items()):
                w.writerow([e["file"], e["win"], day, d["gap"], d["cash"], d["option"], d["quads"],
                            d["empty"], d["an"], d["goose"], d["cow"], d["sheep"], d["plants"], d["shops_n"]])
    with open(ROOT / "h2_commitment_analysis.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["file", "win", "margin", "first_perm_neg_gap", "first_perm_low_option"])
        for e in eps:
            w.writerow([e["file"], e["win"], e["margin"], e["first_perm_neg_gap"], e["first_perm_low_option"]])
    with open(ROOT / "h2_option_set_by_day.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["day", "win_opt_mean", "loss_opt_mean", "win_gap_mean", "loss_gap_mean"])
        for day in range(0, 30):
            wo = [e["days"][day]["option"] for e in wins if day in e["days"]]
            lo = [e["days"][day]["option"] for e in losses if day in e["days"]]
            if not wo or not lo:
                continue
            wg = [e["days"][day]["gap"] for e in wins if day in e["days"]]
            lg = [e["days"][day]["gap"] for e in losses if day in e["days"]]
            w.writerow([day, st.mean(wo), st.mean(lo), st.mean(wg), st.mean(lg)])
    print("wrote 3 CSVs")


if __name__ == "__main__":
    main()
