# -*- coding: utf-8 -*-
"""P18: mine R2 day-boundary states + inferred strategic mode into a library."""
from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402


def load_r2():
    spec = importlib.util.spec_from_file_location(
        "r2_p18_" + str(id(object())), str(ROOT / "_push_medal" / "main.py")
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def tile_stats(tiles):
    empty = plant = melon = wheat = straw = animals = 0
    for row in tiles or []:
        for t in row:
            if t is None:
                empty += 1
            elif isinstance(t, dict):
                if t.get("kind") == "PLANT":
                    plant += 1
                    c = t.get("crop")
                    if c == "MELON":
                        melon += 1
                    elif c == "WHEAT":
                        wheat += 1
                    elif c == "STRAWBERRY":
                        straw += 1
                if t.get("animal"):
                    animals += 1
    return empty, plant, melon, wheat, straw, animals


def run_mine(seed=1, seat=0):
    r2 = load_r2()
    from _pm_pool import load_agent
    finn = load_agent("fallow_finn")
    agents = [None, None]
    agents[seat] = r2
    agents[1 - seat] = finn

    days = {}  # day -> features
    day_sell = {}
    day_animal_buy = {}
    day_land = {}

    def wrap(inner, is_own):
        def agent(obs, configuration=None):
            step = int(obs.get("step") or 0)
            day = step // 24
            action = inner(obs, configuration)
            if not is_own:
                return action
            farm = (obs.get("farms") or [])[int(obs.get("player") or 0)]
            private = obs.get("private") or {}
            shed = dict(private.get("shed") or {})
            prices = dict((obs.get("market") or {}).get("prices") or {})
            tiles = farm.get("tiles") or []
            empty, plant, melon, wheat, straw, animals = tile_stats(tiles)
            sells = {}
            abuy = 0
            land = 0
            for o in action.get("market") or []:
                if not o:
                    continue
                if o[0] == "SELL" and len(o) >= 3:
                    sells[o[1]] = sells.get(o[1], 0) + int(o[2] or 0)
                elif o[0] == "BUY_ANIMAL":
                    abuy += int(o[2] or 1)
                elif o[0] == "BUY_LAND":
                    land += 1
            day_sell[day] = day_sell.get(day, 0) + sum(
                sells[k] * int(prices.get(k) or 1) for k in sells
            )
            day_animal_buy[day] = day_animal_buy.get(day, 0) + abuy
            day_land[day] = day_land.get(day, 0) + land
            if step % 24 == 0:
                shops = list((obs.get("town") or {}).get("unlocked_shops") or [])
                days[day] = {
                    "money": float(farm.get("money") or 0),
                    "hands": len(farm.get("hands") or []),
                    "n_land": len(farm.get("unlocked_quadrants") or []),
                    "empty": empty, "plant": plant, "melon": melon,
                    "wheat": wheat, "straw": straw, "animals": animals,
                    "shed_total": sum(int(v or 0) for v in shed.values()),
                    "n_shops": len(shops),
                    "px_melon": int(prices.get("MELON") or 0),
                    "px_milk": int(prices.get("MILK") or 0),
                    "px_wool": int(prices.get("WOOL") or 0),
                }
            return action
        return agent

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run([wrap(agents[0], seat == 0), wrap(agents[1], seat == 1)])

    # infer mode from forward 3-day window
    rows = []
    for day in range(0, 27):
        if day not in days:
            continue
        s = days[day]
        sell_fwd = sum(day_sell.get(d, 0) for d in range(day, min(day + 3, 30)))
        abuy_fwd = sum(day_animal_buy.get(d, 0) for d in range(day, min(day + 3, 30)))
        land_fwd = sum(day_land.get(d, 0) for d in range(day, min(day + 3, 30)))
        d1 = days.get(min(day + 1, 29), s)
        d2 = days.get(min(day + 2, 29), s)
        melon_drop = s["melon"] - d1.get("melon", s["melon"])
        money_jump = d1.get("money", s["money"]) - s["money"]
        animal_delta = d2.get("animals", s["animals"]) - s["animals"]
        plant_delta = d2.get("plant", s["plant"]) - s["plant"]
        if s["melon"] >= 5 and melon_drop >= 5 and money_jump > 500:
            mode = "CASH_WINDOW"
        elif animal_delta >= 1 or (abuy_fwd >= 2 and s["animals"] < 8):
            mode = "HERD_SCALE"
        elif land_fwd >= 1 or plant_delta >= 8:
            mode = "EXPAND"
        else:
            mode = "MAIN"
        rec = {"seed": seed, "seat": seat, "day": day, "mode": mode,
               "sell_fwd": sell_fwd, "abuy_fwd": abuy_fwd, "land_fwd": land_fwd,
               "melon_drop": melon_drop, "money_jump": money_jump,
               "animal_delta": animal_delta, "plant_delta": plant_delta, **s}
        rows.append(rec)
        print(f"d{day:02d} ${s['money']:.0f} mel={s['melon']} ani={s['animals']} "
              f"plant={s['plant']} dMel={melon_drop} dAni={animal_delta} mode={mode}", flush=True)
    return rows


def main():
    all_rows = []
    for seed in (1, 2):
        all_rows.extend(run_mine(seed=seed, seat=0))
    out = ROOT / "p18_trajectory_library.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        w.writeheader()
        w.writerows(all_rows)
    # mode histogram
    from collections import Counter
    print("modes", Counter(r["mode"] for r in all_rows))
    print("wrote", out.name)


if __name__ == "__main__":
    main()
