"""EXP-8 Phase A1/A2: executed-ledger reconstruction (accounting fix).

Replays the engine 1.32.7 market processing per step using the ENGINE'S OWN
primitives (_parse_order/_commit_unit/market_price/_do_hire/_do_buy_land/
_refresh_prices + MARKET_PARAMS), so fill prices and failure rules are exact
by construction. Pre-market state per step = obs(s-1) + step-s unit effects
(DROP/PICKUP/PLACE on the shed; PLANT seed consumption; day-boundary
auto-deposit of carried inventory), reconstructed for BOTH players.

Validation: the replay's post-market money/shed/seeds/market-inventory must
equal obs(s); any mismatch is reported as a ledger gap (never tolerated).

OBS SEMANTICS (EXP-4 probe): observation at step s is the POST-action state
of step s -> obs(s-1) is the pre-step-s state; the step-s action record is
what ran during step s. Unit actions never change money.
"""
import copy
import importlib.util
import os

_ENGINE_PATH = os.path.join(
    os.path.expanduser("~"), ".conda", "envs", "kaggle", "Lib", "site-packages",
    "kaggle_environments", "envs", "kaggriculture", "kaggriculture.py")
_spec = importlib.util.spec_from_file_location("kaggriculture_engine", _ENGINE_PATH)
eng = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(eng)

_MOVES = {"NORTH": (0, -1), "SOUTH": (0, 1), "WEST": (-1, 0), "EAST": (1, 0)}
SHED_CAP = 100
INITIAL_BANK = 3000.0
MAX_ORDERS = 10
FARM_HAND_MULT = getattr(eng, "FARM_HAND_COST_MULT", 100)


def _params(market_obs):
    p = market_obs.get("params")
    return p if isinstance(p, dict) else eng.MARKET_PARAMS


def _board_of(farm_obs):
    try:
        return len(farm_obs.get("tiles") or [])
    except Exception:
        return 10


def _is_shed_adj(x, y, board):
    half = board // 2
    return (x, y) in {(half - 1, half - 1), (half, half - 1), (half - 1, half), (half, half)}


def _unit_state_effects(obs_prev, act_cur, seat, day_boundary):
    """Simulate step-s unit actions' effect on shed + seeds for one seat.

    Returns (shed_pre, seeds_pre) reconstructed from obs(s-1) + step-s actions:
      shed: DROP (+) / PICKUP (-) / PLACE (-, animals) + day-boundary
            auto-deposit of carried inventory (engine _drop_inventories_to_shed)
      seeds: PLANT consumption (engine PLANT op takes 1 seed per executed plant)
    """
    obs = obs_prev
    farms = obs.get("farms") or []
    farm = farms[seat] if len(farms) == 2 else {}
    tiles = farm.get("tiles") or []
    priv = obs.get("private") or {}
    shed = dict(priv.get("shed", {}) or {})
    seeds = dict(priv.get("seeds", {}) or {})
    inventories = [dict(x) for x in (priv.get("inventories") or [])]
    board = _board_of(farm)

    farmer = list(farm.get("farmer", [0, 0]))
    hands = [list(h) for h in farm.get("hands") or []]
    units_pos = [farmer] + hands
    units_act = [act_cur.get("farmer", ["PASS"])] + list(act_cur.get("hands") or [])

    # Pass 1: engine atomic PLANT validation (L920-933) — if total PLANT
    # requests for a crop exceed available seeds, ALL requests for that crop
    # are blocked (become PASS, consume nothing).
    plant_req = {}
    for op in units_act:
        if isinstance(op, (list, tuple)) and len(op) >= 2 and op[0] == "PLANT" and op[1] in eng.CROPS:
            plant_req[op[1]] = plant_req.get(op[1], 0) + 1
    blocked = {c for c, n in plant_req.items() if n > int(seeds.get(c, 0) or 0)}

    # Pass 2: apply shed/seed effects per unit (mutable tile copy so same-step
    # harvest -> plant sequences are simulated in order).
    tiles_m = [list(row) for row in tiles]
    for u in range(min(len(units_pos), len(units_act))):
        op = units_act[u]
        if not isinstance(op, (list, tuple)) or not op:
            continue
        fx, fy = int(units_pos[u][0]), int(units_pos[u][1])
        kind = op[0]
        if kind in _MOVES or kind == "MOVE":
            continue
        tt = tiles_m[fy][fx] if 0 <= fy < len(tiles_m) and 0 <= fx < len(tiles_m[fy]) else None
        inv = inventories[u] if u < len(inventories) else {}
        if kind == "DROP":
            if not _is_shed_adj(fx, fy, board):
                continue
            for item, n in list(inv.items()):
                if int(n or 0) <= 0:
                    continue
                room = max(0, SHED_CAP - sum(shed.values()))
                take = min(int(n), room)
                if take > 0:
                    shed[item] = shed.get(item, 0) + take
                del inv[item]
        elif kind == "PICKUP" and len(op) >= 2:
            if not _is_shed_adj(fx, fy, board):
                continue
            item = op[1]
            n = int(op[2]) if len(op) >= 3 else 1
            take = min(n, shed.get(item, 0))
            if take > 0:
                shed[item] -= take
        elif kind == "PLACE" and len(op) >= 2:
            item = op[1]
            # Engine PLACE (L377-406): animal placement takes from the unit's
            # CARRIED inventory (never the shed); the shed-adjacent branch is a
            # carried->shed drop (like DROP). No animal is ever removed from the
            # shed by PLACE.
            on_struct = (
                item in eng.ANIMALS
                and isinstance(tt, dict)
                and tt.get("kind") == eng.ANIMALS[item]["structure"]
                and "animal" not in tt
            )
            if _is_shed_adj(fx, fy, board) and not on_struct:
                # PLACE-as-drop (shed-adjacent, non-structure): carried -> shed.
                n = int(op[2]) if len(op) >= 3 else 1
                n = min(n, inv.get(item, 0))
                room = max(0, SHED_CAP - sum(shed.values()))
                n = min(n, room)
                if n > 0:
                    inv[item] -= n
                    shed[item] = shed.get(item, 0) + n
        elif kind == "PLANT" and len(op) >= 2:
            crop = op[1]
            if crop in eng.CROPS and crop not in blocked and tt is None:
                seeds[crop] = int(seeds.get(crop, 0) or 0) - 1
        elif kind == "HARVEST":
            # Same-step harvest adds the tile's pre-harvest yield to the unit's
            # carried inventory (matters for the end-of-day deposit and any
            # later same-step DROP room check); non-ongoing crops clear the
            # tile (affects a later same-step PLANT's tile check).
            if isinstance(tt, dict) and int(tt.get("yield_units", 0) or 0) > 0:
                harvested = int(tt["yield_units"])
                if tt.get("kind") == "PLANT" and tt.get("crop"):
                    inv[tt["crop"]] = inv.get(tt["crop"], 0) + harvested
                    if not eng.CROPS[tt["crop"]]["ongoing"]:
                        tiles_m[fy][fx] = None
                elif "animal" in tt:
                    inv[eng.ANIMALS[tt["animal"]]["product"]] = (
                        inv.get(eng.ANIMALS[tt["animal"]]["product"], 0) + harvested)
        elif kind == "COLLECT_FERTILIZER":
            if isinstance(tt, dict) and tt.get("fertilizer_available"):
                inv["FERTILIZER"] = inv.get("FERTILIZER", 0) + 1
                tiles_m[fy][fx] = dict(tt)
                tiles_m[fy][fx]["fertilizer_available"] = False
        elif kind == "FEED":
            # Engine FEED consumes 1 carried WHEAT (never the shed); the
            # animal's fed_today flag is set so a later same-step FEED of the
            # same animal fails.
            if (isinstance(tt, dict) and "animal" in tt and not tt.get("fed_today")
                    and int(inv.get("WHEAT", 0) or 0) > 0):
                inv["WHEAT"] -= 1
                tiles_m[fy][fx] = dict(tt)
                tiles_m[fy][fx]["fed_today"] = True
        elif kind == "FERTILIZE":
            # Engine FERTILIZE consumes 1 carried FERTILIZER.
            if (isinstance(tt, dict) and tt.get("kind") == "PLANT"
                    and int(inv.get("FERTILIZER", 0) or 0) > 0):
                inv["FERTILIZER"] -= 1

    if day_boundary:
        # (day-boundary deposit handled in replay_step AFTER the market replay,
        # matching the engine order units -> market -> consume -> end_of_day)
        pass
    return shed, seeds, inventories


def _reconstruct_farm(farm_obs, money, hands_n=None):
    f = copy.deepcopy(dict(farm_obs or {}))
    f["money"] = money
    if hands_n is not None and isinstance(f.get("hands"), list):
        f["hands"] = f["hands"][:hands_n]
    return f


def replay_step(obs_prev, act_cur, obs_cur, seat, consume_step=None, obs_cur_other=None,
                obs_prev_other=None, return_states=False):
    """Replay one step's market processing for BOTH players.

    The observed transition obs(s-1) -> obs(s) pairs steps[s].action with the
    engine's _town_consume at step (s-1) (probe-verified: obs(1) contains both
    turn-1 order effects and the step-0 town consumption). The consume is
    applied AFTER the market replay (fill prices see the pre-consume
    inventory; the consume's inventory effect lands in obs(s)).

    obs_cur_other: the OPPONENT's obs at step s (validation for the opponent
    seat); obs_prev_other: the OPPONENT's obs at step s-1 (pre-market state
    reconstruction for the opponent seat — previously the candidate obs was
    wrongly reused for both seats).

    Returns (ledger, valid, detail):
      ledger: per-order executed ledger for `seat`
        {"SELL": [exec_qty, rev], "BUY_SEED": [exec_qty, cost],
         "BUY_PRODUCT": [exec_qty, cost], "BUY_ANIMAL": [exec_qty, cost],
         "HIRE": [exec_qty, cost], "BUY_LAND": [exec_qty, cost]}
        plus "issued" (the issued qty per type from the action stream)
      valid: post-replay money/shed/seeds/inventory == obs_cur
      detail: mismatch description when invalid
    """
    farms_p = obs_prev.get("farms") or []
    farms_c = obs_cur.get("farms") or []
    priv_p = obs_prev.get("private") or {}
    priv_c = obs_cur.get("private") or {}
    market_p = obs_prev.get("market") or {}
    market_c = obs_cur.get("market") or {}

    # Reconstruct pre-market state for both players (each from its OWN obs(s-1)
    # and its OWN step-s unit actions — the opponent's actions were previously
    # never applied to the opponent's reconstruction, the A6 root cause).
    day_boundary = int(obs_cur.get("day", 0) or 0) > int(obs_prev.get("day", 0) or 0)
    states = []
    act_other = _ACT_OTHER.get(seat) or {}
    for s in range(2):
        obs_p_s = obs_prev if s == seat else (obs_prev_other or obs_prev)
        act_s_s = act_cur if s == seat else act_other
        farm_o = (obs_p_s.get("farms") or [{}])[s]
        shed, seeds, carried = _unit_state_effects(obs_p_s, act_s_s, s, day_boundary)
        money = float(farm_o.get("money", 0) or 0)
        board = _board_of(farm_o)
        farm = _reconstruct_farm(farm_o, money)
        priv = {"shed": shed, "seeds": seeds,
                "inventories": [dict(x) for x in ((obs_p_s.get("private") or {}).get("inventories") or [])]}
        states.append({"farm": farm, "private": priv, "board": board, "carried": carried})

    market = {"inventory": dict(market_p.get("inventory", {}) or {}),
              "params": _params(market_p)}

    # Town consumption is applied AFTER the market replay (probe-verified:
    # market quotes see the PRE-consume inventory -> fills match exactly; the
    # consume's inventory effect lands in obs(s) -> state validation matches).
    # Applied before validation below via _town_consume inventory terms.

    # Both players' step-s queues (max 10 orders each, engine L560).
    act_other = _ACT_OTHER.get(seat) or {}
    aq = [list(o) for o in (act_cur.get("market") or []) if isinstance(o, (list, tuple))][:MAX_ORDERS]
    oq = [list(o) for o in (act_other.get("market") or []) if isinstance(o, (list, tuple))][:MAX_ORDERS]
    queues = [aq, oq] if seat == 0 else [oq, aq]

    ledger = {"SELL": [0, 0.0], "BUY_SEED": [0, 0.0], "BUY_PRODUCT": [0, 0.0],
              "BUY_ANIMAL": [0, 0.0], "HIRE": [0, 0.0], "BUY_LAND": [0, 0.0]}
    issued = {"SELL": 0, "BUY_SEED": 0, "BUY_PRODUCT": 0, "BUY_ANIMAL": 0, "HIRE": 0, "BUY_LAND": 0}
    for o in aq:
        if len(o) >= 3 and o[0] in issued:
            issued[o[0]] += int(o[2])
        elif len(o) >= 1 and o[0] in ("HIRE", "BUY_LAND"):
            issued[o[0]] += 1

    # Outer loop over queue positions (engine L562-569).
    max_len = max(len(queues[0]), len(queues[1]))
    for i in range(max_len):
        order_states = [
            eng._parse_order(queues[p][i]) if i < len(queues[p]) else None
            for p in range(2)
        ]

        # Atomic orders (HIRE, BUY_LAND): handle once, in player order (engine L571-581).
        for p in range(2):
            os_ = order_states[p]
            if os_ is None:
                continue
            st = states[p]
            if os_["type"] == "HIRE":
                before = st["farm"]["money"]
                eng._do_hire(st["farm"], st["private"], st["board"], FARM_HAND_MULT)
                if p == seat:
                    ledger["HIRE"][0] += 1
                    ledger["HIRE"][1] += before - st["farm"]["money"]
                order_states[p] = None
            elif os_["type"] == "BUY_LAND":
                before = st["farm"]["money"]
                eng._do_buy_land(st["farm"], st["board"])
                if p == seat:
                    ledger["BUY_LAND"][0] += 1
                    ledger["BUY_LAND"][1] += before - st["farm"]["money"]
                order_states[p] = None

        # Per-unit lockstep loop (engine L583-626).
        esc = 0
        while True:
            esc += 1
            if esc >= 100000:
                break
            quoted = [None, None]
            for p in range(2):
                os_ = order_states[p]
                if os_ is None or os_.get("remaining", 0) <= 0:
                    continue
                op, item = os_["type"], os_["item"]
                inv = market["inventory"].get(item, 0)
                if op == "SELL" and item in eng.PRODUCTS:
                    quoted[p] = ("SELL", item, eng.market_price(item, inv, market["params"]))
                elif op == "BUY_PRODUCT" and item in ("WHEAT", "FERTILIZER"):
                    quoted[p] = ("BUY_PRODUCT", item, eng.market_price(item, inv - 1, market["params"]))
                elif op == "BUY_SEED" and item in eng.CROPS:
                    quoted[p] = ("BUY_SEED", item, eng.CROPS[item]["seed"])
                elif op == "BUY_ANIMAL" and item in eng.ANIMALS:
                    quoted[p] = ("BUY_ANIMAL", item, eng.ANIMALS[item]["cost"])
                else:
                    order_states[p] = None
            if all(q is None for q in quoted):
                break
            committed = False
            for p in range(2):
                q = quoted[p]
                if q is None:
                    continue
                op, item, price = q
                st = states[p]
                ok = eng._commit_unit(op, item, price, st["farm"], st["private"], market, SHED_CAP)
                if ok:
                    order_states[p]["remaining"] -= 1
                    committed = True
                    if p == seat:
                        ledger[op][0] += 1
                        ledger[op][1] += price
                else:
                    order_states[p] = None
            if not committed:
                break

    # Town consumption (engine _town_consume at consume_step): applied AFTER
    # the market replay so the buy quotes see the pre-consume inventory
    # (money exact), while the consume's inventory reduction lands in the
    # post-replay state (validation matches obs(s)).
    if consume_step is not None:
        sh = (obs_prev.get("town") or {}).get("unlocked_shops") or ()
        if consume_step % 4 == 0:
            for shop_name in sh:
                prods = eng.SHOPS.get(shop_name, ())
                mult = 2 if len(prods) == 1 else 1
                for item in prods:
                    market["inventory"][item] = market["inventory"].get(item, 0) - mult
        if consume_step % 24 == 0:
            for item in getattr(eng, "TOWN_CENTER_PRODUCTS", ()):
                market["inventory"][item] = market["inventory"].get(item, 0) - 1

    # Day-boundary deposit (engine order: units -> market -> consume ->
    # _end_of_day -> _drop_inventories_to_shed, overflow discarded): applied
    # AFTER the market so the market's sell/buy checks see the pre-deposit shed.
    if day_boundary:
        for st in states:
            for inv in st["carried"]:
                for item, n in list(inv.items()):
                    if int(n or 0) <= 0:
                        continue
                    room = max(0, SHED_CAP - sum(st["private"]["shed"].values()))
                    take = min(int(n), room)
                    if take > 0:
                        st["private"]["shed"][item] = st["private"]["shed"].get(item, 0) + take

    # Validation vs obs_cur (candidate seat) and obs_cur_other (opponent seat).
    detail = []
    for s in range(2):
        obs_v = obs_cur if s == seat else (obs_cur_other or obs_cur)
        st = states[s]
        fc = (obs_v.get("farms") or [{}])[s] if s == seat else (obs_v.get("farms") or [{}])[s]
        pc = (obs_v.get("private") or {}).get("shed", {}) or {}
        sc = (obs_v.get("private") or {}).get("seeds", {}) or {}
        mc = (obs_v.get("market") or {}).get("inventory", {}) or {}
        if abs(st["farm"]["money"] - float(fc.get("money", 0) or 0)) > 0.01:
            detail.append(f"seat{s} money {st['farm']['money']:.1f} vs obs {fc.get('money')}")
        for k, v in st["private"]["shed"].items():
            if v != int(pc.get(k, 0) or 0):
                detail.append(f"seat{s} shed[{k}] {v} vs obs {pc.get(k)}")
        for k, v in st["private"]["seeds"].items():
            if v != int(sc.get(k, 0) or 0):
                detail.append(f"seat{s} seeds[{k}] {v} vs obs {sc.get(k)}")
        for k, v in market["inventory"].items():
            if v != int(mc.get(k, 0) or 0):
                detail.append(f"market[{k}] {v} vs obs {mc.get(k)}")

    ledger["issued"] = issued
    if return_states:
        return (ledger, (not detail), "; ".join(detail[:6]),
                {"states": states, "market": market})
    return ledger, (not detail), "; ".join(detail[:6])


_ACT_OTHER = {}


def replay_game(steps, seat, seed=None):
    """Reconstruct the full executed ledger for `seat` across an episode.

    steps: the kaggle_environments step array. Returns (agg, valid_count,
    total_steps, mismatches) where agg aggregates the per-step ledgers.
    """
    agg = {"SELL": [0, 0.0], "BUY_SEED": [0, 0.0], "BUY_PRODUCT": [0, 0.0],
           "BUY_ANIMAL": [0, 0.0], "HIRE": [0, 0.0], "BUY_LAND": [0, 0.0],
           "issued": {"SELL": 0, "BUY_SEED": 0, "BUY_PRODUCT": 0, "BUY_ANIMAL": 0, "HIRE": 0, "BUY_LAND": 0}}
    mismatches = []
    valid = 0
    n = 0
    for s in range(1, len(steps)):
        obs_p = steps[s - 1][seat].get("observation") or {}
        act_s = steps[s][seat].get("action") or {}
        obs_c = steps[s][seat].get("observation") or {}
        _ACT_OTHER[seat] = steps[s][1 - seat].get("action") or {}
        led, ok, det = replay_step(obs_p, act_s, obs_c, seat, consume_step=s - 1,
                                   obs_cur_other=steps[s][1 - seat].get("observation") or {},
                                   obs_prev_other=steps[s - 1][1 - seat].get("observation") or {})
        n += 1
        if ok:
            valid += 1
        else:
            mismatches.append((s, det))
        for t in agg:
            if t == "issued":
                for k in agg[t]:
                    agg[t][k] += led["issued"].get(k, 0)
            else:
                agg[t][0] += led[t][0]
                agg[t][1] += led[t][1]
    _ACT_OTHER.pop(seat, None)
    return agg, valid, n, mismatches
