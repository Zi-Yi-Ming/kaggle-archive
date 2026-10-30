# -*- coding: utf-8 -*-
"""Deep-dive one live LOSS: R2 vs opponent action streams d14-22."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

REP = Path(r"D:\桌面\Kaggle\kaggriculture\_external\\replays")


def cmd_key(cmd):
    if not cmd or not isinstance(cmd, list):
        return "PASS"
    return str(cmd[0])


def market_key(o):
    if not o or not isinstance(o, list):
        return "?"
    if o[0] == "SELL":
        return f"SELL_{o[1]}"
    if o[0] in ("BUY_SEED", "BUY_PRODUCT", "BUY_ANIMAL"):
        return f"{o[0]}_{o[1]}"
    return str(o[0])


def profile_range(steps, seat, day_lo, day_hi):
    cmds = Counter()
    mkt = Counter()
    money = {}
    hands = {}
    for idx, snap in enumerate(steps):
        if seat >= len(snap):
            continue
        rec = snap[seat] or {}
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
        cmds[cmd_key(act.get("farmer"))] += 1
        for h in act.get("hands") or []:
            cmds["H:" + cmd_key(h)] += 1
        for o in act.get("market") or []:
            mkt[market_key(o)] += 1
        if step % 24 == 0:
            farm = (obs.get("farms") or [None, None])[seat]
            if isinstance(farm, dict):
                money[day] = float(farm.get("money") or 0)
                hands[day] = len(farm.get("hands") or [])
    return cmds, mkt, money, hands


def analyze(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    teams = (data.get("info") or {}).get("TeamNames") or []
    if "ZiYiMing" not in teams:
        return
    me = teams.index("ZiYiMing")
    opp = 1 - me
    rewards = data.get("rewards") or [0, 0]
    my, op = float(rewards[me]), float(rewards[opp])
    if my >= op:
        return
    steps = data.get("steps") or []
    print("=" * 72)
    print(f"LOSS {path.name} vs {teams[opp]}  {my:.0f} vs {op:.0f} m={my-op:+.0f}")
    for day_lo, day_hi in ((14, 17), (18, 21), (22, 25)):
        c_me, m_me, mon_me, h_me = profile_range(steps, me, day_lo, day_hi)
        c_op, m_op, mon_op, h_op = profile_range(steps, opp, day_lo, day_hi)
        print(f"\n  --- day {day_lo}-{day_hi} ---")
        print(f"  money d{day_lo}: me={mon_me.get(day_lo)} opp={mon_op.get(day_lo)}")
        print(f"  hands d{day_lo}: me={h_me.get(day_lo)} opp={h_op.get(day_lo)}")
        print(f"  me farmer cmds top: {c_me.most_common(8)}")
        print(f"  op farmer cmds top: {c_op.most_common(8)}")
        print(f"  me market top: {m_me.most_common(8)}")
        print(f"  op market top: {m_op.most_common(8)}")


def main():
    losses = []
    for p in sorted(REP.glob("episode-*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        teams = (data.get("info") or {}).get("TeamNames") or []
        if "ZiYiMing" not in teams:
            continue
        me = teams.index("ZiYiMing")
        rew = data.get("rewards") or [0, 0]
        if float(rew[me]) < float(rew[1 - me]):
            losses.append(p)
    print(f"losses n={len(losses)}")
    for p in losses[:6]:
        analyze(p)


if __name__ == "__main__":
    main()
