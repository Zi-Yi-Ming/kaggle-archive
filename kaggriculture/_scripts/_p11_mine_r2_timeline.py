# -*- coding: utf-8 -*-
"""P11 Phase0: mine R2 tape strategic events (no tape copy into planner)."""
from __future__ import annotations

import csv
import importlib.util
import json
from collections import Counter
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
R2_PATH = ROOT / "_push_medal" / "main.py"


def load_r2():
    spec = importlib.util.spec_from_file_location("r2_mine", str(R2_PATH))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def classify_market(orders):
    kinds = Counter()
    for o in orders or []:
        if not o:
            continue
        kinds[o[0]] += 1
    return kinds


def classify_worker(cmd):
    if not cmd:
        return "PASS"
    return cmd[0]


def mine_plan(m, plan_id=0):
    tape = m._POLICY.tapes[plan_id] if m._POLICY else None
    if tape is None:
        m._POLICY = m.Policy(ROOT / "_push_medal")
        tape = m._POLICY.tapes[plan_id]
    rows = []
    for step in range(len(tape)):
        a = tape[step] or {}
        day = step // 24
        hour = step % 24
        mk = classify_market(a.get("market"))
        farmers = [classify_worker(a.get("farmer"))] + [classify_worker(h) for h in (a.get("hands") or [])]
        buys = [o for o in (a.get("market") or []) if o and o[0] in ("BUY_ANIMAL", "BUY_LAND", "HIRE", "BUY_SEED", "BUY_PRODUCT")]
        sells = [o for o in (a.get("market") or []) if o and o[0] == "SELL"]
        rows.append({
            "plan": plan_id,
            "step": step,
            "day": day,
            "hour": hour,
            "n_orders": len(a.get("market") or []),
            "buy_animal": mk.get("BUY_ANIMAL", 0),
            "buy_land": mk.get("BUY_LAND", 0),
            "hire": mk.get("HIRE", 0),
            "buy_seed": mk.get("BUY_SEED", 0),
            "buy_product": mk.get("BUY_PRODUCT", 0),
            "sell": mk.get("SELL", 0),
            "sell_items": "|".join(o[1] for o in sells if len(o) > 1),
            "buy_detail": "|".join(f"{o[0]}:{o[1] if len(o)>1 else ''}x{o[2] if len(o)>2 else ''}" for o in buys),
            "worker_ops": "|".join(farmers),
            "has_plant": any(c == "PLANT" or (isinstance(c, list) and c and c[0] == "PLANT") for c in [a.get("farmer")] + list(a.get("hands") or [])),
            "has_build": any(isinstance(c, list) and c and c[0] in ("BUILD_COOP", "BUILD_PASTURE") for c in [a.get("farmer")] + list(a.get("hands") or [])),
            "has_feed": any(isinstance(c, list) and c and c[0] == "FEED" for c in [a.get("farmer")] + list(a.get("hands") or [])),
            "has_harvest": any(isinstance(c, list) and c and c[0] == "HARVEST" for c in [a.get("farmer")] + list(a.get("hands") or [])),
            "has_water": any(isinstance(c, list) and c and c[0] == "WATER" for c in [a.get("farmer")] + list(a.get("hands") or [])),
        })
    return rows


def summarize(rows, plan_id):
    events = {
        "first_buy_land": None,
        "first_hire": None,
        "first_buy_animal": None,
        "first_plant": None,
        "first_build": None,
        "first_sell": None,
        "first_feed": None,
        "n_hire": 0,
        "n_buy_land": 0,
        "buy_animal_detail": Counter(),
        "buy_seed_detail": Counter(),
        "n_sell_turns": 0,
        "n_plant_turns": 0,
        "n_build_turns": 0,
        "n_feed_turns": 0,
        "day_buy_events": [],
    }
    for r in rows:
        if r["buy_land"] and events["first_buy_land"] is None:
            events["first_buy_land"] = r["step"]
        if r["hire"] and events["first_hire"] is None:
            events["first_hire"] = r["step"]
        if r["buy_animal"] and events["first_buy_animal"] is None:
            events["first_buy_animal"] = r["step"]
        if r["has_plant"] and events["first_plant"] is None:
            events["first_plant"] = r["step"]
        if r["has_build"] and events["first_build"] is None:
            events["first_build"] = r["step"]
        if r["sell"] and events["first_sell"] is None:
            events["first_sell"] = r["step"]
        if r["has_feed"] and events["first_feed"] is None:
            events["first_feed"] = r["step"]
        events["n_hire"] += r["hire"]
        events["n_buy_land"] += r["buy_land"]
        events["n_sell_turns"] += 1 if r["sell"] else 0
        events["n_plant_turns"] += 1 if r["has_plant"] else 0
        events["n_build_turns"] += 1 if r["has_build"] else 0
        events["n_feed_turns"] += 1 if r["has_feed"] else 0
        if r["buy_detail"]:
            for part in r["buy_detail"].split("|"):
                if part.startswith("BUY_ANIMAL"):
                    events["buy_animal_detail"][part] += 1
                if part.startswith("BUY_SEED"):
                    events["buy_seed_detail"][part] += 1
            if r["buy_animal"] or r["buy_land"] or r["hire"]:
                events["day_buy_events"].append((r["step"], r["day"], r["buy_detail"]))
    return events


def main():
    m = load_r2()
    all_rows = []
    summaries = []
    for plan_id in range(13):
        rows = mine_plan(m, plan_id)
        all_rows.extend(rows)
        ev = summarize(rows, plan_id)
        summaries.append({
            "plan": plan_id,
            "first_buy_land": ev["first_buy_land"],
            "first_hire": ev["first_hire"],
            "first_buy_animal": ev["first_buy_animal"],
            "first_plant": ev["first_plant"],
            "first_build": ev["first_build"],
            "first_sell": ev["first_sell"],
            "first_feed": ev["first_feed"],
            "n_hire": ev["n_hire"],
            "n_buy_land": ev["n_buy_land"],
            "n_sell_turns": ev["n_sell_turns"],
            "n_plant_turns": ev["n_plant_turns"],
            "n_build_turns": ev["n_build_turns"],
            "n_feed_turns": ev["n_feed_turns"],
            "buy_animals": json.dumps(dict(ev["buy_animal_detail"]), ensure_ascii=False),
            "buy_seeds": json.dumps(dict(ev["buy_seed_detail"]), ensure_ascii=False),
            "expand_events": json.dumps(ev["day_buy_events"][:40], ensure_ascii=False),
        })
        print(f"plan{plan_id}: land@{ev['first_buy_land']} hire@{ev['first_hire']} "
              f"animal@{ev['first_buy_animal']} plant@{ev['first_plant']} "
              f"build@{ev['first_build']} sell@{ev['first_sell']} feed@{ev['first_feed']} "
              f"hires={ev['n_hire']} lands={ev['n_buy_land']} "
              f"sell_turns={ev['n_sell_turns']} plant_turns={ev['n_plant_turns']}", flush=True)

    out = ROOT / "p11_r2_tape_timeline.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        w.writeheader()
        w.writerows(all_rows)
    out2 = ROOT / "p11_r2_plan_summary.csv"
    with open(out2, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(summaries[0].keys()))
        w.writeheader()
        w.writerows(summaries)
    print("wrote", out, out2)


if __name__ == "__main__":
    main()
