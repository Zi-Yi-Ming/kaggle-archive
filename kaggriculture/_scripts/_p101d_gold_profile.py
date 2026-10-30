# -*- coding: utf-8 -*-
"""P101d: reverse gold agent from live replay — full action stream profile."""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

OUT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\p101_replays")
RESEARCH = Path(r"D:\桌面\Kaggle\kaggriculture\_research")
GOLD_TEAM = "吃白饭的大肥鱼"


def profile_replay(path: Path, gold_is_index: int | None = None):
    data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    steps = data.get("steps") or []
    rewards = data.get("rewards")
    # identify gold index from rewards + team via meta later; default scan both
    n = len(steps)
    profiles = []
    for ai in range(2):
        op_counter = Counter()
        item_counter = Counter()
        sells = []  # (step, item, qty)
        buys = []
        hires = []
        collect_fert = 0
        animals_bought = Counter()
        farmer_ops = Counter()
        hands_len = []
        money_path = []
        market_orders_per_step = []
        for si, st in enumerate(steps):
            if not isinstance(st, list) or ai >= len(st):
                continue
            agent = st[ai]
            if not isinstance(agent, dict):
                continue
            act = agent.get("action") or {}
            obs = agent.get("observation") or {}
            mkt = act.get("market") or []
            market_orders_per_step.append(len(mkt))
            for o in mkt:
                if not isinstance(o, (list, tuple)) or not o:
                    continue
                op = o[0]
                op_counter[op] += 1
                if op == "SELL" and len(o) >= 3:
                    sells.append((si, o[1], int(o[2] or 0)))
                    item_counter[f"SELL:{o[1]}"] += 1
                elif op in ("BUY_PRODUCT", "BUY_SEED", "BUY_ANIMAL") and len(o) >= 3:
                    buys.append((si, op, o[1], int(o[2] or 0)))
                    item_counter[f"{op}:{o[1]}"] += 1
                    if op == "BUY_ANIMAL":
                        animals_bought[o[1]] += 1
                elif op == "HIRE":
                    hires.append(si)
                elif op == "COLLECT_FERTILIZER":
                    collect_fert += 1
                    item_counter["COLLECT_FERTILIZER"] += 1
            f = act.get("farmer") or []
            if isinstance(f, list) and f:
                farmer_ops[str(f[0]) if f else ""] += 1
            hands = act.get("hands") or []
            hands_len.append(len(hands) if isinstance(hands, list) else 0)
            farm = (obs.get("farms") or [])
            me = obs.get("player") or 0
            if isinstance(farm, list) and me < len(farm) and isinstance(farm[me], dict):
                money_path.append(float(farm[me].get("money") or 0))

        profiles.append({
            "ai": ai,
            "op_counter": dict(op_counter),
            "item_counter": dict(item_counter.most_common(40)),
            "n_sells": len(sells),
            "sell_by_item": dict(Counter(s[1] for s in sells)),
            "sell_qty_by_item": dict(Counter()),
            "first_sell_step": sells[0][0] if sells else None,
            "last_sell_step": sells[-1][0] if sells else None,
            "sells_after_600": sum(1 for s in sells if s[0] >= 600),
            "sells_after_648": sum(1 for s in sells if s[0] >= 648),
            "n_hires": len(hires),
            "hire_steps": hires[:12],
            "collect_fert": collect_fert,
            "animals_bought": dict(animals_bought),
            "farmer_ops": dict(farmer_ops),
            "avg_hands": (sum(hands_len) / len(hands_len)) if hands_len else 0,
            "money_start": money_path[0] if money_path else None,
            "money_mid": money_path[n // 2] if money_path else None,
            "money_end": money_path[-1] if money_path else None,
            "avg_mkt_orders": (sum(market_orders_per_step) / len(market_orders_per_step)) if market_orders_per_step else 0,
            "sell_samples": sells[:8] + sells[-8:],
            "buy_samples": buys[:15],
        })
        # sell qty
        sq = Counter()
        for _, item, q in sells:
            sq[item] += q
        profiles[-1]["sell_qty_by_item"] = dict(sq)

    return {"file": path.name, "rewards": rewards, "profiles": profiles}


def main():
    gold_files = sorted((OUT / "gold").glob("episode-*-replay.json"))[:8]
    h3_files = sorted((OUT / "h3").glob("episode-*-replay.json"))[:6]
    gold_profs = []
    h3_profs = []
    for p in gold_files:
        try:
            r = profile_replay(p)
            # pick index whose reward matches the larger or match gold meta
            gold_profs.append(r)
            print("GOLD", p.name, "r", r["rewards"], flush=True)
            for pr in r["profiles"]:
                print("  ai", pr["ai"], "hires", pr["n_hires"], "animals", pr["animals_bought"],
                      "fert", pr["collect_fert"], "sells", pr["n_sells"], "after648", pr["sells_after_648"],
                      "ops", pr["op_counter"], flush=True)
        except Exception as e:
            print("err", p, e, flush=True)
    for p in h3_files:
        try:
            r = profile_replay(p)
            h3_profs.append(r)
            print("H3", p.name, "r", r["rewards"], flush=True)
            for pr in r["profiles"]:
                print("  ai", pr["ai"], "hires", pr["n_hires"], "animals", pr["animals_bought"],
                      "fert", pr["collect_fert"], "sells", pr["n_sells"], "after648", pr["sells_after_648"],
                      "ops", pr["op_counter"], flush=True)
        except Exception as e:
            print("err", p, e, flush=True)

    out = {"gold": gold_profs, "h3": h3_profs}
    (RESEARCH / "p101d_gold_profile.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False, default=str), encoding="utf-8"
    )
    print("WROTE p101d_gold_profile.json", flush=True)


if __name__ == "__main__":
    main()
