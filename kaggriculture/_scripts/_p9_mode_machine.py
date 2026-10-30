# -*- coding: utf-8 -*-
"""Architecture A: Two-Timescale Mode Machine.

Slow layer (day 0,6,12,18,24): select economic mode.
Fast layer (every step): execute mode-specific deterministic policy.

Modes: EXPAND, LIVESTOCK, CROP, SELL, RECOVER
Behavioral novelty: re-selects mode 5x per season; R2 never does.
"""
from __future__ import annotations

from collections import Counter

_MODES = ("EXPAND", "LIVESTOCK", "CROP", "SELL", "RECOVER")
_SELECT_DAYS = {0, 6, 12, 18, 24}


def _farm(obs):
    me = int(obs.get("player") or 0)
    farms = obs.get("farms") or []
    return me, (farms[me] if me < len(farms) else {})


def _counts(farm):
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
    return an, pl, empty


def _select_mode(obs, day, money, an, pl, empty, quads, shops, opp_an, opp_plants):
    """Slow layer: pick economic mode."""
    # Recovery: low cash mid-game
    if day >= 8 and money < 800:
        return "RECOVER"
    # Expand land early
    if day <= 8 and quads < 2 and money > 1200:
        return "EXPAND"
    if day <= 14 and quads < 3 and money > 3500:
        return "EXPAND"
    # Behind on livestock vs opponent → livestock push
    my_an = sum(an.values())
    if day >= 6 and my_an < opp_an - 2 and money > 400:
        return "LIVESTOCK"
    # Bakery / yarn → livestock; farmers / pizza → crop
    shop_set = set(shops or [])
    if "YARN_STORE" in shop_set or "BAKERY" in shop_set:
        if my_an < 14:
            return "LIVESTOCK"
        return "CROP"
    if "FARMERS_MARKET" in shop_set or "PIZZA_SHOP" in shop_set:
        return "CROP"
    # Late game sell-down
    if day >= 26:
        return "SELL"
    # Default: balanced livestock if cash ok else crop
    if money > 1500 and my_an < 12:
        return "LIVESTOCK"
    return "CROP"


_STATE = {}


def agent(obs, configuration=None):
    try:
        me, farm = _farm(obs)
        step = int(obs.get("step") or 0)
        day = step // 24
        hour = step % 24
        money = float(farm.get("money") or 0)
        quads = list(farm.get("unlocked_quadrants") or [])
        tiles = farm.get("tiles") or []
        hands = farm.get("hands") or []
        private = obs.get("private") or {}
        shed = private.get("shed") or {}
        seeds = private.get("seeds") or {}
        inv0 = (private.get("inventories") or [{}])[0] or {}
        prices = ((obs.get("market") or {}).get("prices") or {})
        shops = list((obs.get("town") or {}).get("unlocked_shops") or [])
        farms = obs.get("farms") or []
        opp = farms[1 - me] if len(farms) > 1 else {}
        an, pl, empty = _counts(farm)
        opp_an_c, opp_pl_c, _ = _counts(opp)
        opp_an = sum(opp_an_c.values())
        opp_plants = sum(opp_pl_c.values())

        st = _STATE.get(me)
        if st is None or step <= st.get("last", -1):
            st = {"last": step, "mode": "CROP", "mode_log": [], "switches": 0}
            _STATE[me] = st
        st["last"] = step

        # --- SLOW LAYER ---
        if day in _SELECT_DAYS and hour == 0:
            new_mode = _select_mode(obs, day, money, an, pl, empty, quads, shops, opp_an, opp_plants)
            if new_mode != st["mode"]:
                st["switches"] += 1
                st["mode_log"].append((step, st["mode"], new_mode))
            st["mode"] = new_mode
        mode = st["mode"]

        # --- FAST LAYER ---
        market = []
        n_hands = len(hands)

        # Land in EXPAND
        if mode == "EXPAND" and len(quads) < 3 and money > (1000 if len(quads) == 1 else 3500):
            market.append(["BUY_LAND"])

        # Hire (all modes except pure RECOVER at low cash)
        hire_target = 6 if mode in ("LIVESTOCK", "CROP") else 4
        if mode != "RECOVER" and n_hands < hire_target and money > 80:
            market.append(["HIRE"])
            if n_hands < 2 and money > 200:
                market.append(["HIRE"])

        # Animals by mode
        if mode == "LIVESTOCK":
            if an["COW"] < 10 and money > 500:
                market.append(["BUY_ANIMAL", "COW", 1])
            elif an["SHEEP"] < 6 and money > 600:
                market.append(["BUY_ANIMAL", "SHEEP", 1])
        elif mode == "EXPAND":
            if an["COW"] < 4 and money > 500:
                market.append(["BUY_ANIMAL", "COW", 1])
        elif mode == "RECOVER":
            if an["COW"] < 6 and money > 600:
                market.append(["BUY_ANIMAL", "COW", 1])

        # Seeds by mode
        if mode == "CROP":
            if seeds.get("WHEAT", 0) < 8 and money > 40:
                market.append(["BUY_SEED", "WHEAT", 5])
            if "STRAWBERRY" not in pl and money > 200 and day >= 10:
                market.append(["BUY_SEED", "STRAWBERRY", 3])
        elif mode == "LIVESTOCK":
            if seeds.get("WHEAT", 0) < 12 and money > 40:
                market.append(["BUY_SEED", "WHEAT", 6])
        elif mode in ("EXPAND", "RECOVER"):
            if seeds.get("WHEAT", 0) < 6 and money > 30:
                market.append(["BUY_SEED", "WHEAT", 4])

        # Selling by mode
        def sell_if(item, qty, min_px, max_lot=8):
            q = int(shed.get(item) or 0)
            px = int(prices.get(item) or 1)
            if q >= qty and px >= min_px and len(market) < 10:
                market.append(["SELL", item, min(q, max_lot)])

        if mode == "SELL" or day >= 27:
            for item in ("MILK", "WOOL", "STRAWBERRY", "MELON", "EGG", "WHEAT", "FERTILIZER", "TOMATO", "CARROT"):
                q = int(shed.get(item) or 0)
                if q > 0 and len(market) < 10:
                    market.append(["SELL", item, q])
        elif mode == "RECOVER":
            sell_if("STRAWBERRY", 4, 80, 6)
            sell_if("MELON", 2, 150, 4)
            sell_if("MILK", 4, 40, 6)
        else:
            sell_if("MILK", 4, 30, 6)
            sell_if("WOOL", 3, 40, 5)
            sell_if("STRAWBERRY", 5, 80, 6)
            sell_if("EGG", 4, 25, 6)
            sell_if("WHEAT", 15, 25, 6)
            sell_if("FERTILIZER", 8, 15, 6)

        market = market[:10]

        # --- units ---
        x, y = farm.get("farmer") or [4, 4]
        farmer = ["PASS"]
        # place animals
        for a in ("COW", "SHEEP", "GOOSE"):
            if inv0.get(a, 0) > 0:
                farmer = ["PLACE", a]
                break
        else:
            for a in ("COW", "SHEEP", "GOOSE"):
                if shed.get(a, 0) > 0 and mode in ("LIVESTOCK", "EXPAND", "RECOVER"):
                    farmer = ["PICKUP", a, 1]
                    break
            else:
                tile = tiles[y][x] if y < len(tiles) and x < len(tiles[0]) else None
                if isinstance(tile, dict) and tile.get("animal"):
                    if not tile.get("fed_today") and (inv0.get("WHEAT", 0) or shed.get("WHEAT", 0)):
                        farmer = ["FEED"] if inv0.get("WHEAT", 0) else ["PICKUP", "WHEAT", 1]
                    elif not tile.get("cared_today"):
                        farmer = ["CARE"]
                    elif tile.get("fertilizer_available"):
                        farmer = ["COLLECT_FERTILIZER"]
                    elif tile.get("yield_units"):
                        farmer = ["HARVEST"]
                elif isinstance(tile, dict) and tile.get("kind") == "WEED":
                    farmer = ["DIG"]
                elif tile is None and seeds.get("WHEAT", 0) > 0:
                    farmer = ["PLANT", "WHEAT"]
                elif isinstance(tile, dict) and tile.get("kind") == "PLANT":
                    if not tile.get("watered_today"):
                        farmer = ["WATER"]
                    elif (day - tile.get("planted_day", 0)) >= 3 and tile.get("yield_units", 0) > 0:
                        farmer = ["HARVEST"]
                if farmer == ["PASS"]:
                    # walk toward shed for feed or empty
                    farmer = ["NORTH"] if y > 0 else ["SOUTH"]

        hand_cmds = []
        for i, pos in enumerate(hands):
            hx, hy = pos
            t = tiles[hy][hx] if hy < len(tiles) and hx < len(tiles[0]) else None
            cmd = ["PASS"]
            if isinstance(t, dict) and t.get("animal"):
                if not t.get("fed_today") and (inv0.get("WHEAT", 0) + shed.get("WHEAT", 0) > 0):
                    cmd = ["FEED"] if inv0.get("WHEAT", 0) else ["PICKUP", "WHEAT", 1]
                elif not t.get("cared_today"):
                    cmd = ["CARE"]
                elif t.get("fertilizer_available"):
                    cmd = ["COLLECT_FERTILIZER"]
                elif t.get("yield_units"):
                    cmd = ["HARVEST"]
            elif isinstance(t, dict) and t.get("kind") == "WEED":
                cmd = ["DIG"]
            elif t is None and seeds.get("WHEAT", 0) > 0 and mode != "SELL":
                cmd = ["PLANT", "WHEAT"]
            elif isinstance(t, dict) and t.get("kind") == "PLANT" and not t.get("watered_today"):
                cmd = ["WATER"]
            elif cmd == ["PASS"]:
                cmd = ["WEST"] if hx > 0 else ["EAST"]
            hand_cmds.append(cmd)

        action = {"farmer": farmer, "hands": hand_cmds, "market": market}
        # expose for behavior audit
        action["_mode"] = mode  # engine ignores unknown keys? safer not to add
        return {"farmer": farmer, "hands": hand_cmds, "market": market}
    except Exception:
        return {"farmer": ["PASS"], "hands": [], "market": []}


def debug_state():
    return {k: dict(v) for k, v in _STATE.items()}
