# -*- coding: utf-8 -*-
"""P3: R2 live WIN vs LOSS — opponent behavior fingerprint + market context."""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
REP = ROOT / "_external" / "replays"
PREMIUM = ("STRAWBERRY", "MILK", "WOOL", "MELON", "EGG")


def farm_counts(farm):
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
    return empty, an, pl


def profile_player(steps, player):
    empty_d = {}
    an_d = {}
    pl_d = {}
    money_d = {}
    listed = Counter()
    listed_qty = Counter()
    listed_val = Counter()
    first_list = {}
    late_flood = 0  # qty listed d27-29
    mid_dense = 0   # events d15-26
    prem_events = 0
    for idx, snap in enumerate(steps):
        if player >= len(snap):
            continue
        rec = snap[player] or {}
        obs = rec.get("observation") or {}
        act = rec.get("action") or {}
        if not isinstance(obs, dict):
            continue
        step = obs.get("step")
        step = int(step) if step is not None else idx
        day = step // 24
        farms = obs.get("farms") or []
        if player < len(farms) and step % 24 == 0:
            e, an, pl = farm_counts(farms[player] or {})
            empty_d[day] = e
            an_d[day] = dict(an)
            pl_d[day] = dict(pl)
            money_d[day] = float((farms[player] or {}).get("money") or 0)
        if int(obs.get("player") or player) != player:
            continue
        prices = ((obs.get("market") or {}).get("prices") or {})
        for o in act.get("market") or []:
            if not o or o[0] != "SELL" or len(o) < 3:
                continue
            item, q = o[1], int(o[2] or 0)
            if q <= 0:
                continue
            px = int(prices.get(item) or 1)
            listed[item] += 1
            listed_qty[item] += q
            listed_val[item] += q * px
            if item not in first_list:
                first_list[item] = step
            if day >= 27:
                late_flood += q
            if 15 <= day <= 26:
                mid_dense += 1
            if item in PREMIUM:
                prem_events += 1
    an20 = an_d.get(20) or {}
    return {
        "empty_d10": empty_d.get(10),
        "empty_d15": empty_d.get(15),
        "an_d15": sum((an_d.get(15) or {}).values()),
        "an_d20": sum(an20.values()),
        "an_d20_dict": an20,
        "pl_d15": sum((pl_d.get(15) or {}).values()),
        "pl_d20": sum((pl_d.get(20) or {}).values()),
        "money_d15": money_d.get(15),
        "money_d20": money_d.get(20),
        "money_d25": money_d.get(25),
        "listed_events": sum(listed.values()),
        "prem_events": prem_events,
        "late_flood_qty": late_flood,
        "mid_dense_events": mid_dense,
        "straw_first": first_list.get("STRAWBERRY"),
        "milk_first": first_list.get("MILK"),
        "wool_first": first_list.get("WOOL"),
        "straw_qty": listed_qty.get("STRAWBERRY", 0),
        "milk_qty": listed_qty.get("MILK", 0),
        "wool_qty": listed_qty.get("WOOL", 0),
        "straw_val": listed_val.get("STRAWBERRY", 0),
        "milk_val": listed_val.get("MILK", 0),
        "wool_val": listed_val.get("WOOL", 0),
        "goose": an20.get("GOOSE", 0),
        "cow": an20.get("COW", 0),
        "sheep": an20.get("SHEEP", 0),
        "n_lists_top": dict(listed.most_common(8)),
    }


def analyze(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    info = data.get("info") or {}
    teams = info.get("TeamNames") or []
    rewards = data.get("rewards") or [0, 0]
    if "ZiYiMing" not in teams:
        return None
    me = teams.index("ZiYiMing")
    opp = 1 - me
    my, op = float(rewards[me]), float(rewards[opp])
    steps = data.get("steps") or []
    pf_me = profile_player(steps, me)
    pf_opp = profile_player(steps, opp)
    # mirror flag
    mirror = (pf_opp.get("goose", 0) >= 2 and pf_opp.get("cow", 0) >= 7
              and pf_opp.get("sheep", 0) >= 4)
    row = {
        "file": path.name,
        "opp_name": teams[opp] if opp < len(teams) else "?",
        "win": my > op,
        "margin": my - op,
        "my_bank": my,
        "opp_bank": op,
        "mirror": mirror,
    }
    for k, v in pf_opp.items():
        if k != "n_lists_top":
            row["opp_" + k] = v
    for k, v in pf_me.items():
        if k != "n_lists_top":
            row["my_" + k] = v
    # mid-game money gap at d20
    if pf_me.get("money_d20") is not None and pf_opp.get("money_d20") is not None:
        row["money_gap_d20"] = pf_me["money_d20"] - pf_opp["money_d20"]
    if pf_me.get("money_d25") is not None and pf_opp.get("money_d25") is not None:
        row["money_gap_d25"] = pf_me["money_d25"] - pf_opp["money_d25"]
    return row


def main():
    rows = []
    for p in sorted(REP.glob("episode-*.json")):
        try:
            r = analyze(p)
        except Exception as e:
            print("fail", p.name, e)
            continue
        if r:
            rows.append(r)
    d = pd.DataFrame(rows)
    print(f"n={len(d)} W={int(d.win.sum())} L={int((~d.win).sum())}")
    print("mirror among losses:", int(d.loc[~d.win, "mirror"].sum()), "/", int((~d.win).sum()))
    print("mirror among wins:", int(d.loc[d.win, "mirror"].sum()), "/", int(d.win.sum()))

    feats = [
        "opp_goose", "opp_cow", "opp_sheep", "opp_an_d20", "opp_pl_d20",
        "opp_listed_events", "opp_prem_events", "opp_late_flood_qty",
        "opp_mid_dense_events", "opp_straw_qty", "opp_milk_qty", "opp_wool_qty",
        "opp_straw_val", "opp_milk_val", "opp_wool_val",
        "my_listed_events", "my_straw_qty", "my_milk_qty",
        "money_gap_d20", "money_gap_d25", "margin",
    ]
    print("\n=== WIN vs LOSS means ===")
    diff_rows = []
    for f in feats:
        if f not in d.columns:
            continue
        w = d.loc[d.win, f]
        l = d.loc[~d.win, f]
        if w.isna().all() or l.isna().all():
            continue
        mw, ml = w.mean(), l.mean()
        print(f"  {f:22s} win={mw:10.1f} lose={ml:10.1f}  d={mw-ml:+10.1f}")
        diff_rows.append({"feature": f, "win_mean": mw, "lose_mean": ml, "delta": mw - ml})

    # only mirror games
    print("\n=== MIRROR-only W vs L ===")
    dm = d[d.mirror]
    print(f"  n={len(dm)} W={int(dm.win.sum())} L={int((~dm.win).sum())}")
    for f in feats:
        if f not in dm.columns:
            continue
        w = dm.loc[dm.win, f]
        l = dm.loc[~dm.win, f]
        if len(w) < 2 or len(l) < 2:
            continue
        if w.isna().all() or l.isna().all():
            continue
        mw, ml = w.mean(), l.mean()
        if abs(mw - ml) > 0.05 * max(abs(mw), abs(ml), 1):
            print(f"  {f:22s} win={mw:10.1f} lose={ml:10.1f}  d={mw-ml:+10.1f}")

    # list opponents in losses
    print("\n=== LOSS opponents ===")
    for _, r in d[~d.win].iterrows():
        print(f"  {r.opp_name[:24]:24s} m={r.margin:+8.0f} mirror={r.mirror} "
              f"G/C/S={r.opp_goose}/{r.opp_cow}/{r.opp_sheep} "
              f"gap20={r.get('money_gap_d20')} prem={r.opp_prem_events}")

    d.to_csv(ROOT / "p3_opponent_features.csv", index=False)
    pd.DataFrame(diff_rows).to_csv(ROOT / "p3_r2_win_loss_diff.csv", index=False)
    print("wrote p3_opponent_features.csv p3_r2_win_loss_diff.csv")


if __name__ == "__main__":
    main()
