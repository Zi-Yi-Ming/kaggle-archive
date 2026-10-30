# -*- coding: utf-8 -*-
import json
from pathlib import Path

import pandas as pd

ASHOK = Path(r"D:\桌面\Kaggle\kaggriculture\_external\public_data\ashok_top10\replays_2026-08-03.parquet")
df = pd.read_parquet(ASHOK)


def feat(steps, player, prod):
    tot_q = rev = 0
    first = None
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
        if int(obs.get("player") or player) != player:
            continue
        prices = ((obs.get("market") or {}).get("prices") or {})
        px = int(prices.get(prod) or 0)
        for o in act.get("market") or []:
            if o and o[0] == "SELL" and o[1] == prod and len(o) >= 3:
                q = int(o[2] or 0)
                if q > 0:
                    tot_q += q
                    rev += q * px
                    if first is None:
                        first = step
    return tot_q, rev, (rev / tot_q if tot_q else None), (first // 24 if first is not None else None)


for prod in ("STRAWBERRY", "MILK", "WOOL"):
    rows = []
    for i in range(len(df)):
        try:
            data = json.loads(df.iloc[i]["replay_json"])
        except Exception:
            continue
        rew = data.get("rewards") or [0, 0]
        try:
            r0, r1 = float(rew[0]), float(rew[1])
        except Exception:
            continue
        if min(r0, r1) < 100000:
            continue
        w = 0 if r0 >= r1 else 1
        l = 1 - w
        steps = data.get("steps") or []
        wq, wr, wp, wf = feat(steps, w, prod)
        lq, lr, lp, lf = feat(steps, l, prod)
        rows.append((abs(r0 - r1), wq, wr, wp, wf, lq, lr, lp, lf))
    d = pd.DataFrame(rows, columns=["margin", "wq", "wr", "wp", "wf", "lq", "lr", "lp", "lf"])
    d["dq"] = d.wq - d.lq
    d["drev"] = d.wr - d.lr
    d["dpx"] = d.wp - d.lp
    d["dfirst"] = d.wf - d.lf
    print(f"=== {prod} n={len(d)} ===")
    print(f"  win  q={d.wq.mean():.0f} rev={d.wr.mean():.0f} px={d.wp.mean():.1f} first={d.wf.mean():.2f}")
    print(f"  lose q={d.lq.mean():.0f} rev={d.lr.mean():.0f} px={d.lp.mean():.1f} first={d.lf.mean():.2f}")
    for c in ("dq", "drev", "dpx", "dfirst"):
        print(f"  corr(margin,{c})={d.margin.corr(d[c], method='spearman'):.3f}")
    print("  win first-day top5:", d.wf.value_counts().head(5).to_dict())
    print("  lose first-day top5:", d.lf.value_counts().head(5).to_dict())
