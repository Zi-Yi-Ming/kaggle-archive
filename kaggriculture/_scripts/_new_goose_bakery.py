# -*- coding: utf-8 -*-
"""Minimal Goose/Egg bakery economy — structurally different from R2 8C/6S.

Hypothesis: daily egg production + bakery demand is a different cash path
than cow-milk / sheep-wool shop-router. May not beat R2 on every map, but
tests a genuinely new policy family (not a tape patch).

Failure: eggs glut, feed starvation, too slow vs 8C/6S mid-game.
"""
from __future__ import annotations


def agent(obs, configuration=None):
    try:
        me = int(obs.get("player") or 0)
        step = int(obs.get("step") or 0)
        day = step // 24
        farm = (obs.get("farms") or [])[me]
        private = obs.get("private") or {}
        money = float(farm.get("money") or 0)
        quads = set(farm.get("unlocked_quadrants") or [])
        tiles = farm.get("tiles") or []
        hands = farm.get("hands") or []
        shed = private.get("shed") or {}
        seeds = private.get("seeds") or {}
        inv0 = (private.get("inventories") or [{}])[0] or {}
        prices = ((obs.get("market") or {}).get("prices") or {})
        shops = (obs.get("town") or {}).get("unlocked_shops") or []

        def count_animals():
            from collections import Counter
            c = Counter()
            for row in tiles:
                for t in row or []:
                    if isinstance(t, dict) and t.get("animal"):
                        c[t["animal"]] += 1
            return c

        an = count_animals()
        n_hands = len(hands)
        market = []

        # Land: expand to 3 quads when cash allows
        if len(quads) < 3 and money > 3500:
            market.append(["BUY_LAND"])

        # Hire 4-6 hands for logistics
        if n_hands < 5 and money > 200:
            market.append(["HIRE"])
            if n_hands < 3 and money > 400:
                market.append(["HIRE"])

        # Animal targets: goose-first bakery line, then cows
        # Goose $300 → egg; bakery wants EGG+WHEAT
        if an["GOOSE"] < 8 and money > 700:
            market.append(["BUY_ANIMAL", "GOOSE", 1])
        elif an["COW"] < 4 and money > 900:
            market.append(["BUY_ANIMAL", "COW", 1])

        # Buy wheat seed for feed + bakery demand
        if day >= 1 and seeds.get("WHEAT", 0) < 10 and money > 80:
            market.append(["BUY_SEED", "WHEAT", 5])

        # Sell eggs aggressively (bakery), wheat surplus, milk if any
        egg_shed = int(shed.get("EGG") or 0)
        wheat_shed = int(shed.get("WHEAT") or 0)
        milk_shed = int(shed.get("MILK") or 0)
        egg_px = int(prices.get("EGG") or 1)
        wheat_px = int(prices.get("WHEAT") or 1)
        milk_px = int(prices.get("MILK") or 1)
        if egg_shed >= 4 and egg_px >= 20:
            market.append(["SELL", "EGG", min(egg_shed, 8)])
        if wheat_shed >= 12 and wheat_px >= 20:
            market.append(["SELL", "WHEAT", min(wheat_shed - 8, 6)])
        if milk_shed >= 6 and milk_px >= 40:
            market.append(["SELL", "MILK", min(milk_shed, 6)])
        # late dump
        if step >= 710:
            for item, q in (("EGG", egg_shed), ("MILK", milk_shed), ("WOOL", int(shed.get("WOOL") or 0)),
                            ("STRAWBERRY", int(shed.get("STRAWBERRY") or 0)), ("WHEAT", wheat_shed),
                            ("FERTILIZER", int(shed.get("FERTILIZER") or 0))):
                if q > 0 and len(market) < 10:
                    market.append(["SELL", item, q])

        market = market[:10]

        # Farmer: place animals, feed, collect fert, plant wheat
        x, y = farm.get("farmer") or [4, 4]
        farmer = ["PASS"]
        # place goose/cow from inventory
        for a in ("GOOSE", "COW"):
            if inv0.get(a, 0) > 0:
                farmer = ["PLACE", a]
                break
        else:
            # pickup animal from shed
            for a in ("GOOSE", "COW"):
                if shed.get(a, 0) > 0:
                    farmer = ["PICKUP", a, 1]
                    break
            else:
                # feed/care/collect on animal tile
                acted = False
                for yy, row in enumerate(tiles):
                    for xx, t in enumerate(row or []):
                        if not (isinstance(t, dict) and t.get("animal")):
                            continue
                        if xx == x and yy == y:
                            if not t.get("fed_today") and (inv0.get("WHEAT", 0) > 0 or shed.get("WHEAT", 0) > 0):
                                if inv0.get("WHEAT", 0) == 0:
                                    farmer = ["PICKUP", "WHEAT", 1]
                                else:
                                    farmer = ["FEED"]
                            elif not t.get("cared_today"):
                                farmer = ["CARE"]
                            elif t.get("fertilizer_available"):
                                farmer = ["COLLECT_FERTILIZER"]
                            elif t.get("yield_units"):
                                farmer = ["HARVEST"]
                            acted = True
                            break
                    if acted:
                        break
                if not acted:
                    # plant wheat on empty tile
                    tile = tiles[y][x] if y < len(tiles) and x < len(tiles[0]) else None
                    if tile is None and seeds.get("WHEAT", 0) > 0:
                        farmer = ["PLANT", "WHEAT"]
                    elif isinstance(tile, dict) and tile.get("kind") == "PLANT" and not tile.get("watered_today"):
                        farmer = ["WATER"]
                    elif isinstance(tile, dict) and tile.get("kind") == "PLANT" and (obs.get("day") - tile.get("planted_day", 0)) >= 2:
                        farmer = ["HARVEST"]
                    elif inv0.get("WHEAT", 0) < 3 and shed.get("WHEAT", 0) > 0:
                        farmer = ["PICKUP", "WHEAT", 1]
                    else:
                        # move toward nearest animal needing feed or empty tile
                        farmer = ["EAST"] if x < 9 else ["WEST"]

        # Hands: simple roles
        hand_cmds = []
        for i, hxhy in enumerate(hands):
            hx, hy = hxhy
            # hand 0-1: feed/care loop; others: water/harvest wheat
            if i < 2:
                cmd = ["PASS"]
                for yy, row in enumerate(tiles):
                    for xx, t in enumerate(row or []):
                        if isinstance(t, dict) and t.get("animal") and xx == hx and yy == hy:
                            if not t.get("fed_today") and inv0.get("WHEAT", 0) + shed.get("WHEAT", 0) > 0:
                                cmd = ["FEED"] if inv0.get("WHEAT", 0) else ["PICKUP", "WHEAT", 1]
                            elif not t.get("cared_today"):
                                cmd = ["CARE"]
                            elif t.get("fertilizer_available"):
                                cmd = ["COLLECT_FERTILIZER"]
                            elif t.get("yield_units"):
                                cmd = ["HARVEST"]
                if cmd == ["PASS"]:
                    cmd = ["NORTH"] if hy > 0 else ["SOUTH"]
                hand_cmds.append(cmd)
            else:
                # wheat maintenance
                tile = tiles[hy][hx] if hy < len(tiles) and hx < len(tiles[0]) else None
                if isinstance(tile, dict) and tile.get("kind") == "PLANT" and not tile.get("watered_today"):
                    hand_cmds.append(["WATER"])
                elif isinstance(tile, dict) and tile.get("kind") == "WEED":
                    hand_cmds.append(["DIG"])
                else:
                    hand_cmds.append(["WEST"] if hx > 0 else ["EAST"])

        return {"farmer": farmer, "hands": hand_cmds, "market": market}
    except Exception:
        return {"farmer": ["PASS"], "hands": [], "market": []}
