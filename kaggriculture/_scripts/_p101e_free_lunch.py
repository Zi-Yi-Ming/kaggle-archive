# -*- coding: utf-8 -*-
"""P101e: quantify gold 'free lunch' — animal products vs crops, sell timing vs price."""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

OUT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\p101_replays")
RESEARCH = Path(r"D:\桌面\Kaggle\kaggriculture\_research")
GOLD = "吃白饭的大肥鱼"
H3 = "ZiYiMing"
ANIMAL_P = ("EGG", "MILK", "WOOL")
CROP_P = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON")


def analyze(path: Path, my_team: str, meta_agents=None):
    data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    steps = data.get("steps") or []
    # determine my index: match team name from meta or by reward side
    my_ai = 0
    opp_ai = 1
    # meta_agents: list of dicts with teamName and index
    if meta_agents:
        for a in meta_agents:
            if a.get("teamName") == my_team and "index" in a:
                my_ai = int(a["index"])
                opp_ai = 1 - my_ai
    else:
        # fallback: first step observation player field should equal index
        if steps and isinstance(steps[0], list):
            # use higher reward? no - use team from filename meta
            pass

    def stream(ai):
        sells = []  # step, item, qty
        buys = Counter()
        hire_n = 0
        invalid = 0
        empty_mkt = 0
        prices_at_sell = []
        money = []
        for si, st in enumerate(steps):
            if not isinstance(st, list) or ai >= len(st):
                continue
            ag = st[ai]
            if not isinstance(ag, dict):
                continue
            act = ag.get("action") or {}
            obs = ag.get("observation") or {}
            mkt = act.get("market") or []
            if not mkt:
                empty_mkt += 1
            px = ((obs.get("market") or {}).get("prices") or {})
            for o in mkt:
                if not isinstance(o, (list, tuple)) or not o:
                    continue
                op = o[0]
                if op == "INVALID":
                    invalid += 1
                elif op == "HIRE":
                    hire_n += 1
                elif op == "SELL" and len(o) >= 3:
                    item, q = o[1], int(o[2] or 0)
                    sells.append((si, item, q))
                    prices_at_sell.append((si, item, float(px.get(item) or 0), q))
                elif op.startswith("BUY") and len(o) >= 3:
                    buys[f"{op}:{o[1]}"] += 1
            farms = obs.get("farms") or []
            me = obs.get("player") if obs.get("player") is not None else ai
            if isinstance(farms, list) and 0 <= me < len(farms) and isinstance(farms[me], dict):
                money.append(float(farms[me].get("money") or 0))
        return sells, buys, hire_n, invalid, empty_mkt, prices_at_sell, money

    sells, buys, hire_n, invalid, empty_mkt, pxs, money = stream(my_ai)
    o_sells, o_buys, o_hire, o_inv, o_empty, _, o_money = stream(opp_ai)

    def split(sells):
        by = Counter()
        qty = Counter()
        for _, item, q in sells:
            by[item] += 1
            qty[item] += q
        return by, qty

    by, qty = split(sells)
    anim_rev_proxy = sum(qty[i] for i in ANIMAL_P)
    crop_rev_proxy = sum(qty[i] for i in CROP_P)
    # sell timing buckets
    buckets = {"d0-8": 0, "d9-16": 0, "d17-23": 0, "d24-27": 0, "d28+": 0}
    for si, _, q in sells:
        day = si // 24
        if day <= 8:
            buckets["d0-8"] += q
        elif day <= 16:
            buckets["d9-16"] += q
        elif day <= 23:
            buckets["d17-23"] += q
        elif day <= 27:
            buckets["d24-27"] += q
        else:
            buckets["d28+"] += q

    return {
        "file": path.name,
        "my_ai": my_ai,
        "my_reward": (data.get("rewards") or [None, None])[my_ai],
        "opp_reward": (data.get("rewards") or [None, None])[opp_ai],
        "n_sells": len(sells),
        "sell_qty": dict(qty),
        "animal_qty": anim_rev_proxy,
        "crop_qty": crop_rev_proxy,
        "animal_share": anim_rev_proxy / max(anim_rev_proxy + crop_rev_proxy, 1),
        "hire_n": hire_n,
        "invalid": invalid,
        "empty_mkt_steps": empty_mkt,
        "buys": dict(buys.most_common(20)),
        "sell_buckets": buckets,
        "first_sell": sells[0][0] if sells else None,
        "money_end": money[-1] if money else None,
        "opp_invalid": o_inv,
        "opp_animal_qty": sum(split(o_sells)[1][i] for i in ANIMAL_P),
    }


def main():
    gold_meta = json.loads((OUT / "gold_meta.json").read_text(encoding="utf-8"))
    # map episode -> gold index
    gold_index = {}
    for row in gold_meta:
        for a in row.get("agents") or []:
            if a.get("teamName") == GOLD:
                gold_index[row["episode_id"]] = a.get("index", 0)

    rows = []
    for p in sorted((OUT / "gold").glob("episode-*-replay.json"))[:10]:
        eid = int(p.name.split("-")[1])
        try:
            r = analyze(p, GOLD)
            r["tag"] = "gold"
            rows.append(r)
            print("GOLD", r["file"], "my_ai", r["my_ai"], "anim_share", round(r["animal_share"], 2),
                  "hires", r["hire_n"], "sells", r["n_sells"], "buckets", r["sell_buckets"],
                  "opp_invalid", r["opp_invalid"], flush=True)
        except Exception as e:
            print("err", p, e, flush=True)

    h3_meta = json.loads((OUT / "h3_meta.json").read_text(encoding="utf-8"))
    for p in sorted((OUT / "h3").glob("episode-*-replay.json"))[:8]:
        try:
            r = analyze(p, H3)
            r["tag"] = "h3"
            rows.append(r)
            print("H3  ", r["file"], "my_ai", r["my_ai"], "anim_share", round(r["animal_share"], 2),
                  "hires", r["hire_n"], "sells", r["n_sells"], "buckets", r["sell_buckets"],
                  "opp_invalid", r["opp_invalid"], flush=True)
        except Exception as e:
            print("err", p, e, flush=True)

    # aggregate
    for tag in ("gold", "h3"):
        rs = [r for r in rows if r.get("tag") == tag]
        if not rs:
            continue
        print(f"\n== {tag} n={len(rs)} ==", flush=True)
        print("  mean animal_share", sum(r["animal_share"] for r in rs) / len(rs), flush=True)
        print("  mean hires", sum(r["hire_n"] for r in rs) / len(rs), flush=True)
        print("  mean sells", sum(r["n_sells"] for r in rs) / len(rs), flush=True)
        print("  mean first_sell step", sum(r["first_sell"] or 0 for r in rs) / len(rs), flush=True)

    (RESEARCH / "p101e_free_lunch.json").write_text(
        json.dumps(rows, indent=2, ensure_ascii=False, default=str), encoding="utf-8"
    )
    print("WROTE p101e_free_lunch.json", flush=True)


if __name__ == "__main__":
    main()
