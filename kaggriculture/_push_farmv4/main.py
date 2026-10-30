
"""Kaggriculture route-replay chassis (pure Python, stdlib only).

A *route* is a pre-computed tape of 719 Kaggle-format actions
``{"farmer": [op, ...], "hands": [[op, ...], ...], "market": [[order, item, qty], ...]}``.
The chassis replays the tape chosen by a caller-supplied ``router`` and wraps it
in small reactive layers (each independently switchable via ``settings``):

    hand_align            pad/truncate hands to the real hand count      (fieldbook_logic)
    weed_repair           DIG a weed that blocks PLANT/BUILD, replay      (tetsutani + task spec)
    sell_lead             sell next step's lots one step early            (fieldbook _lead_sale)
    front_run             sell before the opponent's scheduled SELL       (hook; opponent_plan)
    budget_guard          fund each 72-step block's purchases             (six_day_budget_guard.hpp)
    room_guard            keep shed <= 99 at hour 23                      (tetsutani)
    clamp_sells           trim SELL orders to the projected shed          (tetsutani)
    dead_stock            sell stock the route will never sell            (tetsutani)
    terminal_liquidation  step >= 718: sell the whole projected shed      (fieldbook _terminal_sale)

Engine facts (verified against kaggle_environments 1.32.7, env_1_32_7.py):
  observation["farms"][p] = {"money", "tiles"[y][x], "farmer"[x,y], "hands"[[x,y]..],
                             "unlocked_quadrants", "hires_today"}
  tiles: None (empty) | "LOCKED" | {"kind": WEED|COOP|PASTURE|PLANT, "crop"/"animal", ...}
  observation["private"] = {"shed": {item: n}, "seeds": {crop: n}, "inventories": [{}...]}
  observation["market"] = {"inventory": {...}, "prices": {...}}
  observation["town"] = {"unlocked_shops": [...]}
  Agents act on steps 0..718 (interpreter marks DONE once step >= episodeSteps-2).
"""
from __future__ import annotations

import copy

PRODUCTS = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER")
SEED_PRICE = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80}
ANIMAL_COST = {"GOOSE": 300, "COW": 400, "SHEEP": 500}
ANIMAL_STRUCTURE = {"GOOSE": "COOP", "COW": "PASTURE", "SHEEP": "PASTURE"}
LAND_PRICES = (1000, 2000, 4000)
MOVES = {"NORTH": (0, -1), "SOUTH": (0, 1), "EAST": (1, 0), "WEST": (-1, 0)}
FRONT_RUN_ITEMS = ("MILK", "WOOL", "STRAWBERRY", "MELON")
LAST_ACT_STEP = 718
PASS_ACTION = {"farmer": ["PASS"], "hands": [], "market": []}

DEFAULT_SETTINGS = {
    "hand_align": True,
    "weed_repair": True,
    "sell_lead": True,
    "front_run": True,
    "budget_guard": True,
    "room_guard": True,
    "clamp_sells": True,
    "dead_stock": True,
    "terminal_liquidation": True,
    # tunables
    "block_turns": 72,
    "shed_capacity": 100,
    "board_size": 10,
    "max_orders": 10,
    "turns_per_day": 24,
    "min_sell_price": 2,
}


# --------------------------------------------------------------------------- helpers
def _get(value, key, default=None):
    """Field access that works for dicts and Kaggle Struct/attribute objects."""
    if isinstance(value, dict):
        return value.get(key, default)
    getter = getattr(value, "get", None)
    if callable(getter):
        return getter(key, default)
    return getattr(value, key, default)


def _int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _fib(n):
    a, b = 1, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def _step_of(observation):
    raw = _get(observation, "step")
    if raw is not None:
        return _int(raw)
    return _int(_get(observation, "day", 0)) * 24 + _int(_get(observation, "hour", 0))


def _shed_adjacent(pos, board):
    if not isinstance(pos, (list, tuple)) or len(pos) < 2:
        return False
    half = board // 2
    return pos[0] in (half - 1, half) and pos[1] in (half - 1, half)


def _tile_at(tiles, pos):
    try:
        x, y = int(pos[0]), int(pos[1])
        return tiles[y][x]
    except (TypeError, ValueError, IndexError):
        return "LOCKED"


def _is_noop(act, tile, inv, seeds, pos, board):
    """True when the engine will certainly ignore ``act`` (mirrors _apply_unit_action)."""
    if not act:
        return True
    op = act[0]
    x, y = pos[0], pos[1]
    if op in MOVES:
        dx, dy = MOVES[op]
        return not (0 <= x + dx < board and 0 <= y + dy < board)
    if op == "PASS":
        return True
    adjacent = _shed_adjacent(pos, board)
    if op == "DROP":
        return (not adjacent) or (not inv)
    if op == "PICKUP":
        return not adjacent
    if op == "PLACE":
        item = act[1] if len(act) > 1 else None
        if item in ANIMAL_STRUCTURE and isinstance(tile, dict) \
                and _get(tile, "kind") == ANIMAL_STRUCTURE[item] and _get(tile, "animal") is None:
            return _int(_get(inv, item, 0)) <= 0
        return (not adjacent) or _int(_get(inv, item, 0)) <= 0
    if tile == "LOCKED":
        return True
    is_dict = isinstance(tile, dict)
    kind = _get(tile, "kind") if is_dict else None
    animal = is_dict and _get(tile, "animal") is not None
    if op == "PLANT":
        return tile is not None or _int(_get(seeds, act[1] if len(act) > 1 else None, 0)) <= 0
    if op == "WATER":
        return kind != "PLANT" or bool(_get(tile, "watered_today"))
    if op == "HARVEST":
        return (not is_dict) or _int(_get(tile, "yield_units", 0)) <= 0
    if op == "FERTILIZE":
        return kind != "PLANT" or _int(_get(inv, "FERTILIZER", 0)) <= 0
    if op == "DIG":
        return tile is None or animal
    if op in ("BUILD_COOP", "BUILD_PASTURE"):
        return tile is not None
    if op == "FEED":
        return (not animal) or bool(_get(tile, "fed_today")) or _int(_get(inv, "WHEAT", 0)) <= 0
    if op == "COLLECT_FERTILIZER":
        return (not animal) or (not _get(tile, "fertilizer_available"))
    if op == "CARE":
        return (not animal) or bool(_get(tile, "cared_today"))
    return True


class _View:
    """Cheap per-step snapshot of everything the layers read from the observation."""

    def __init__(self, observation, player, cfg):
        farms = list(_get(observation, "farms", []) or [])
        self.farm = farms[player] if player < len(farms) else {}
        self.rival = farms[1 - player] if len(farms) >= 2 and 1 - player < len(farms) else {}
        private = _get(observation, "private", {}) or {}
        self.shed = {k: max(0, _int(v)) for k, v in dict(_get(private, "shed", {}) or {}).items()}
        self.seeds = dict(_get(private, "seeds", {}) or {})
        self.invs = [dict(i or {}) for i in (_get(private, "inventories", []) or [])]
        market = _get(observation, "market", {}) or {}
        self.prices = {k: _int(v) for k, v in dict(_get(market, "prices", {}) or {}).items()}
        self.money = float(_get(self.farm, "money", 0.0) or 0.0)
        self.tiles = _get(self.farm, "tiles", []) or []
        self.board = len(self.tiles) or cfg["board_size"]
        self.positions = [_get(self.farm, "farmer", None)] + [list(p) for p in (_get(self.farm, "hands", []) or [])]
        self.hires_today = _int(_get(self.farm, "hires_today", 0))
        self.quadrants = len(list(_get(self.farm, "unlocked_quadrants", []) or []))

    def inv(self, idx):
        return self.invs[idx] if idx < len(self.invs) else {}

    def in_hands(self, item):
        return sum(max(0, _int(_get(inv, item, 0))) for inv in self.invs)


# --------------------------------------------------------------------------- chassis
class Chassis:
    """Replays ``routes[router(...)]`` with reactive safety/market layers.

    routes         : {route_id: list of >= 719 Kaggle action dicts}
    router         : callable(observation, step, state_dict) -> route_id, called every
                     step; ``state_dict`` is per-player and persists across the game.
    settings       : overrides for DEFAULT_SETTINGS (layer switches + tunables)
    opponent_plan  : optional list of the opponent's expected actions (front_run hook)
    """

    def __init__(self, routes, router=None, settings=None, opponent_plan=None):
        self.routes = {rid: list(tape) for rid, tape in routes.items()}
        self.router = router or (lambda observation, step, state: next(iter(self.routes)))
        self.cfg = dict(DEFAULT_SETTINGS)
        self.cfg.update(settings or {})
        self.opponent_plan = opponent_plan
        self.players = {}
        self.diagnostics = {"layer_fallbacks": 0, "entry_fallbacks": 0}
        self._future_sells = {}   # route id -> {item: [remaining planned SELL qty from step t]}

    # ---- state -----------------------------------------------------------------
    def _state(self, player, step):
        st = self.players.get(player)
        if st is None or step == 0 or step <= st["last_step"]:
            st = {"last_step": -1, "route": None, "router_state": {},
                  "pending": {}, "sell_state": {"due_step": -1, "suppress": {}}}
            self.players[player] = st
        st["last_step"] = step
        return st

    def _route_action(self, route, step):
        tape = self.routes[route]
        if 0 <= step < len(tape) and isinstance(tape[step], dict):
            return copy.deepcopy(tape[step])
        return copy.deepcopy(PASS_ACTION)

    def future_sells(self, route, item, step):
        """Planned SELL quantity of ``item`` in route steps >= ``step`` (suffix sums)."""
        table = self._future_sells.get(route)
        if table is None:
            tape = self.routes[route]
            n = len(tape)
            table = {p: [0] * (n + 1) for p in PRODUCTS}
            for t in range(n - 1, -1, -1):
                for p in PRODUCTS:
                    table[p][t] = table[p][t + 1]
                for o in (tape[t].get("market") or []) if isinstance(tape[t], dict) else []:
                    if o and o[0] == "SELL" and len(o) >= 3 and o[1] in table:
                        table[o[1]][t] += max(0, _int(o[2]))
            self._future_sells[route] = table
        col = table.get(item)
        return col[step] if col and 0 <= step < len(col) else 0

    # ---- main entry -----------------------------------------------------------
    def act(self, observation, configuration=None):
        if len(_get(observation, "farms", []) or []) < 2:
            raise ValueError("incomplete observation")  # factory falls back to tape
        step = _step_of(observation)
        player = _int(_get(observation, "player", 0))
        st = self._state(player, step)
        cfg = self.cfg
        view = _View(observation, player, cfg)

        route = self.router(observation, step, st["router_state"])
        if route not in self.routes:
            route = st["route"] if st["route"] in self.routes else next(iter(self.routes))
        st["route"] = route
        action = self._route_action(route, step)
        raw = copy.deepcopy(action)
        try:
            if cfg["hand_align"]:
                self._hand_align(action, view)
            if cfg["weed_repair"]:
                self._weed_repair(action, view, st, route, step)
            if cfg["sell_lead"] or cfg["front_run"]:
                self._apply_suppression(action, st["sell_state"], step)
            projected = self._projected_shed(action, view)
            lead_available = dict(projected)
            next_sup = {"due_step": -1, "suppress": {}, "r36_debts": st["sell_state"].get("r36_debts", {})}
            if cfg["sell_lead"]:
                self._sell_lead(action, view, lead_available, route, step, next_sup)
            if cfg["front_run"] and self.opponent_plan:
                self._front_run(action, view, lead_available, route, step, next_sup)
            st["sell_state"] = next_sup
            if cfg["budget_guard"]:
                self._budget_guard(action, view, route, step)
            if cfg["room_guard"]:
                self._room_guard(action, view, route, step)
            if cfg["clamp_sells"]:
                self._clamp_sells(action, projected)
            if cfg["dead_stock"]:
                self._dead_stock(action, view, projected, route, step)
            if cfg["terminal_liquidation"]:
                self._terminal_liquidation(action, projected, step)
            action["market"] = action["market"][: cfg["max_orders"]]
            return action
        except Exception:
            self.diagnostics["layer_fallbacks"] += 1
            return raw

    # ---- layer: hand_align ----------------------------------------------------
    def _hand_align(self, action, view):
        """Pad with PASS / truncate the tape's hand list to the real number of hands
        (fieldbook_logic.act). Extra hands would be ignored by the engine anyway;
        missing ones just idle, so alignment only tidies the action."""
        expected = max(0, len(view.positions) - 1)
        hands = list(action.get("hands") or [])
        hands.extend([["PASS"] for _ in range(max(0, expected - len(hands)))])
        action["hands"] = hands[:expected]

    # ---- layer: weed_repair ---------------------------------------------------
    def _weed_repair(self, action, view, st, route, step):
        """If a PLANT/BUILD_* target tile is a WEED, DIG now and queue the intended
        action for that unit; the queue replays on a later step when the unit still
        stands there and its tape action would be a no-op (the displaced no-op is
        queued behind it, so PLANT -> WATER chains survive). A PLANT is only replayed
        when the unit's next tape action is not a move, so the mandatory same-day
        WATER can follow; otherwise the seed is kept. A no-op turn spent on a weed
        is also converted to DIG (tetsutani weed_dig)."""
        units = [action.get("farmer") or ["PASS"]] + list(action.get("hands") or [])
        pending = st["pending"]
        tape = self.routes[route]
        nxt = tape[step + 1] if step + 1 < len(tape) and isinstance(tape[step + 1], dict) else {}
        next_units = [nxt.get("farmer") or ["PASS"]] + list(nxt.get("hands") or [])
        for i in range(min(len(units), len(view.positions))):
            pos = view.positions[i]
            if not isinstance(pos, (list, tuple)):
                continue
            pos = (int(pos[0]), int(pos[1]))
            tile = _tile_at(view.tiles, pos)
            act = list(units[i])
            queue = pending.get(i)
            if queue and queue[0][0] != pos:
                pending.pop(i, None)
                queue = None
            is_weed = isinstance(tile, dict) and _get(tile, "kind") == "WEED"
            noop = _is_noop(act, tile, view.inv(i), view.seeds, pos, view.board)
            next_op = next_units[i][0] if i < len(next_units) and next_units[i] else "PASS"
            if act and act[0] in ("PLANT", "BUILD_COOP", "BUILD_PASTURE") and is_weed:
                pending.setdefault(i, []).append((pos, act))
                act = ["DIG"]
            elif queue and noop:
                _, replay = queue[0]
                if replay[0] == "PLANT" and next_op in MOVES:
                    pending.pop(i, None)          # WATER could never follow: keep the seed
                else:
                    queue.pop(0)
                    if act and act[0] != "PASS" and act[0] not in MOVES:
                        queue.append((pos, act))
                    act = replay
                    if not queue:
                        pending.pop(i, None)
            elif is_weed and noop:
                act = ["DIG"]
            units[i] = act
        action["farmer"] = units[0]
        action["hands"] = units[1:]

    # ---- projected shed -------------------------------------------------------
    def _projected_shed(self, action, view):
        """Shed contents after this step's unit actions but before the market runs:
        PICKUP removes, DROP/PLACE(non-animal) near the shed adds up to capacity
        (fieldbook _projected_shed / tetsutani projected shed)."""
        cap = self.cfg["shed_capacity"]
        proj = {p: view.shed.get(p, 0) for p in PRODUCTS}
        for k, v in view.shed.items():
            proj.setdefault(k, v)
        total = sum(proj.values())
        units = [action.get("farmer") or ["PASS"]] + list(action.get("hands") or [])
        for i in range(min(len(units), len(view.positions))):
            if not _shed_adjacent(view.positions[i], view.board):
                continue
            act = units[i]
            op = act[0] if act else "PASS"
            inv = view.inv(i)
            if op == "PICKUP" and len(act) >= 2 and act[1] in proj:
                qty = min(proj[act[1]], max(0, _int(act[2]) if len(act) >= 3 else 1))
                proj[act[1]] -= qty
                total -= qty
            elif op == "DROP":
                for item, held in inv.items():
                    take = min(max(0, _int(held)), max(0, cap - total))
                    if take > 0:
                        proj[item] = proj.get(item, 0) + take
                        total += take
            elif op == "PLACE" and len(act) >= 2 and act[1] not in ANIMAL_STRUCTURE:
                item = act[1]
                take = min(max(0, _int(act[2]) if len(act) >= 3 else 1),
                           max(0, _int(_get(inv, item, 0))), max(0, cap - total))
                if take > 0:
                    proj[item] = proj.get(item, 0) + take
                    total += take
        return proj

    # ---- layer: sell_lead / front_run suppression ------------------------------
    @staticmethod
    def _apply_suppression(action, sell_state, step):
        """Remove from this step's SELLs the quantities already sold a step early."""
        if sell_state.get("due_step") != step:
            return
        remaining = dict(sell_state.get("suppress", {}))
        kept = []
        for order in action.get("market") or []:
            order = list(order)
            if order and order[0] == "SELL" and len(order) >= 3 and remaining.get(order[1], 0) > 0:
                removed = min(max(0, _int(order[2])), remaining[order[1]])
                order[2] = _int(order[2]) - removed
                remaining[order[1]] -= removed
                # A zero-quantity order keeps later market race slots intact.
            kept.append(order)
        action["market"] = kept

    @staticmethod
    def _add_sell(action, item, qty, max_orders, merge=True):
        market = action.setdefault("market", [])
        if merge:
            for order in market:
                if order and order[0] == "SELL" and order[1] == item:
                    order[2] = _int(order[2]) + qty
                    return True
        if len(market) >= max_orders:
            return False
        market.append(["SELL", item, qty])
        return True

    def _sell_lead(self, action, view, projected, route, step, next_sup):
        """fieldbook _lead_sale: when step % 4 != 0 (no town consumption between the
        two steps) sell the lots the tape plans to SELL next step now, for products
        other than WHEAT/FERTILIZER we already hold, and suppress them next step.
        Skipped at the last step, at shop-unlock boundaries and if a SELL for that
        product is already queued this step."""
        cfg = self.cfg
        nxt = step + 1
        unlock_period = 3 * cfg["turns_per_day"]
        if nxt > LAST_ACT_STEP or nxt % unlock_period == 0 or step % 4 == 0:
            return
        tape = self.routes[route]
        future = tape[nxt] if nxt < len(tape) and isinstance(tape[nxt], dict) else {}
        planned = {}
        for o in future.get("market") or []:
            if o and o[0] == "SELL" and len(o) >= 3 and o[1] in PRODUCTS:
                planned[o[1]] = planned.get(o[1], 0) + max(0, _int(o[2]))
        already = {o[1] for o in action.get("market") or [] if o and o[0] == "SELL" and len(o) > 1}
        for item in PRODUCTS:
            if item in ("WHEAT", "FERTILIZER") or planned.get(item, 0) <= 0 or item in already:
                continue
            qty = min(projected.get(item, 0), planned[item])
            if qty <= 0 or view.prices.get(item, 0) < cfg["min_sell_price"]:
                continue
            if not self._add_sell(action, item, qty, cfg["max_orders"], merge=False):
                break
            projected[item] -= qty
            next_sup["suppress"][item] = next_sup["suppress"].get(item, 0) + qty
        if next_sup["suppress"]:
            next_sup["due_step"] = nxt

    def _front_run(self, action, view, projected, route, step, next_sup):
        """Hook: if ``opponent_plan`` (their expected tape) schedules a SELL of
        MILK/WOOL/STRAWBERRY/MELON next step, sell what we hold of it now (before
        their supply depresses the price) and suppress our own SELL of that quantity
        next step. Bounded by our own remaining planned sales so it never dumps."""
        cfg = self.cfg
        nxt = step + 1
        plan = self.opponent_plan
        if nxt > LAST_ACT_STEP or nxt >= len(plan) or not isinstance(plan[nxt], dict):
            return
        already = {o[1] for o in action.get("market") or [] if o and o[0] == "SELL" and len(o) > 1}
        for o in plan[nxt].get("market") or []:
            if not (o and o[0] == "SELL" and len(o) >= 3 and o[1] in FRONT_RUN_ITEMS):
                continue
            item = o[1]
            if item in already or view.prices.get(item, 0) < cfg["min_sell_price"]:
                continue
            own_next = sum(max(0, _int(x[2])) for x in self.routes[route][nxt].get("market", [])
                           if len(x) >= 3 and x[0] == "SELL" and x[1] == item)
            qty = min(projected.get(item, 0), max(0, _int(o[2])), own_next)
            if qty <= 0:
                continue
            if not self._add_sell(action, item, qty, cfg["max_orders"], merge=False):
                break
            projected[item] -= qty
            already.add(item)
            next_sup["suppress"][item] = next_sup["suppress"].get(item, 0) + qty
        if next_sup["suppress"]:
            next_sup["due_step"] = nxt

    # ---- layer: budget_guard --------------------------------------------------
    def _block_requirements(self, view, route, start, end):
        """Planned purchase cost and item reserves for tape steps [start, end)
        (six_day_budget_guard.hpp calculate_six_day_requirements)."""
        tape = self.routes[route]
        budget = 0.0
        seed_bal, item_bal = {}, {}
        seed_need, item_need = {}, {}
        hires_by_day = {}
        quadrants = view.quadrants
        for t in range(start, min(end, len(tape))):
            a = tape[t] if isinstance(tape[t], dict) else {}
            for u in [a.get("farmer") or ["PASS"]] + list(a.get("hands") or []):
                if not u:
                    continue
                op = u[0]
                arg = u[1] if len(u) > 1 else None
                qty = max(1, _int(u[2]) if len(u) > 2 else 1)
                if op == "PLANT" and arg in SEED_PRICE:
                    seed_bal[arg] = seed_bal.get(arg, 0) - 1
                    seed_need[arg] = max(seed_need.get(arg, 0), -seed_bal[arg])
                elif op == "FEED":
                    item_bal["WHEAT"] = item_bal.get("WHEAT", 0) - 1
                    item_need["WHEAT"] = max(item_need.get("WHEAT", 0), -item_bal["WHEAT"])
                elif op == "FERTILIZE":
                    item_bal["FERTILIZER"] = item_bal.get("FERTILIZER", 0) - 1
                    item_need["FERTILIZER"] = max(item_need.get("FERTILIZER", 0), -item_bal["FERTILIZER"])
                elif op == "PLACE" and arg is not None:
                    item_bal[arg] = item_bal.get(arg, 0) - qty
                    item_need[arg] = max(item_need.get(arg, 0), -item_bal[arg])
            for o in a.get("market") or []:
                if not o:
                    continue
                op = o[0]
                item = o[1] if len(o) > 1 else None
                qty = max(1, _int(o[2]) if len(o) > 2 else 1)
                if op == "HIRE":
                    day = (t - start) // self.cfg["turns_per_day"]
                    hires_by_day[day] = hires_by_day.get(day, 0) + 1
                elif op == "BUY_LAND":
                    extra = quadrants - 1
                    if 0 <= extra < len(LAND_PRICES):
                        budget += LAND_PRICES[extra]
                        quadrants += 1
                elif op == "BUY_SEED" and item in SEED_PRICE:
                    budget += SEED_PRICE[item] * qty
                    seed_bal[item] = seed_bal.get(item, 0) + qty
                elif op == "BUY_PRODUCT" and item in ("WHEAT", "FERTILIZER"):
                    budget += view.prices.get(item, 0) * qty
                    item_bal[item] = item_bal.get(item, 0) + qty
                elif op == "BUY_ANIMAL" and item in ANIMAL_COST:
                    budget += ANIMAL_COST[item] * qty
                    item_bal[item] = item_bal.get(item, 0) + qty
        for day, n in hires_by_day.items():
            first = view.hires_today if day == 0 else 0
            for k in range(n):
                budget += _fib(first + k)
        return budget, item_need

    def _budget_guard(self, action, view, route, step):
        """At every block boundary (step % 72 == 0) make sure cash + the value of
        stock the block already plans to sell covers the block's purchases (hires,
        land, seeds, animals, products). A shortfall is covered by extra SELLs of
        unprotected shed stock, highest price first; SELLs are moved in front of
        the buys so the money is there when they execute."""
        cfg = self.cfg
        block = cfg["block_turns"]
        if block <= 0 or step % block != 0:
            return
        budget, item_need = self._block_requirements(view, route, step, step + block)
        market = action.setdefault("market", [])
        existing = {}
        for o in market:
            if o and o[0] == "SELL" and len(o) >= 3:
                existing[o[1]] = existing.get(o[1], 0) + max(0, _int(o[2]))
        cash = view.money
        for item in PRODUCTS:
            planned = max(existing.get(item, 0), self.future_sells(route, item, step)
                          - self.future_sells(route, item, step + block))
            cash += min(view.shed.get(item, 0), planned) * view.prices.get(item, 0)
        shortfall = budget - cash
        if shortfall <= 0:
            return
        candidates = []
        for item in PRODUCTS:
            price = view.prices.get(item, 0)
            if price < cfg["min_sell_price"]:
                continue
            protected = max(0, item_need.get(item, 0) - view.in_hands(item))
            avail = view.shed.get(item, 0) - protected - existing.get(item, 0)
            if avail > 0:
                candidates.append((-price, item, avail, price))
        candidates.sort()
        added = False
        for _, item, avail, price in candidates:
            if shortfall <= 0:
                break
            qty = min(avail, -(-int(shortfall) // price))
            if self._add_sell(action, item, qty, cfg["max_orders"]):
                shortfall -= qty * price
                added = True
        if added:
            sells = [o for o in market if o and o[0] == "SELL"]
            others = [o for o in market if not (o and o[0] == "SELL")]
            action["market"] = sells + others

    # ---- layer: room_guard ----------------------------------------------------
    def _room_guard(self, action, view, route, step):
        """tetsutani room_guard: at hour 23 the end-of-day drop pushes every unit's
        inventory into the shed and overflow is destroyed. Estimate the shed after
        this step (stock + carried + harvest/collect - feed/fertilize/place + buys -
        sells) and, if it exceeds capacity-1, add SELLs preferring products with no
        future planned sale, then highest price."""
        cfg = self.cfg
        if step % cfg["turns_per_day"] != cfg["turns_per_day"] - 1:
            return
        cap = cfg["shed_capacity"]
        units = [action.get("farmer") or ["PASS"]] + list(action.get("hands") or [])
        carried = sum(max(0, _int(n)) for inv in view.invs for n in inv.values())
        produced = consumed = 0
        for i in range(min(len(units), len(view.positions))):
            tile = _tile_at(view.tiles, view.positions[i])
            a = units[i]
            if not a:
                continue
            op = a[0]
            if op == "HARVEST" and isinstance(tile, dict):
                produced += max(0, _int(_get(tile, "yield_units", 0)))
            elif op == "COLLECT_FERTILIZER" and isinstance(tile, dict) and _get(tile, "fertilizer_available"):
                produced += 1
            elif op in ("FEED", "FERTILIZE"):
                consumed += 1
            elif op == "PLACE" and len(a) > 1 and a[1] in ANIMAL_STRUCTURE:
                consumed += 1
        market = action.setdefault("market", [])
        planned_sells, planned_buys = {}, 0
        for o in market:
            if not o:
                continue
            if o[0] == "SELL" and len(o) >= 3:
                planned_sells[o[1]] = planned_sells.get(o[1], 0) + max(0, _int(o[2]))
            elif o[0] in ("BUY_PRODUCT", "BUY_ANIMAL") and len(o) >= 3:
                planned_buys += max(0, _int(o[2]))
        shed_total = sum(view.shed.values())
        fillable = sum(min(view.shed.get(it, 0), n) for it, n in planned_sells.items())
        needed = shed_total + carried + produced - consumed + planned_buys - fillable - (cap - 1)
        if needed <= 0:
            return
        priority = sorted(PRODUCTS, key=lambda it: (self.future_sells(route, it, step + 1) > 0,
                                                   -view.prices.get(it, 0), it))
        for item in priority:
            avail = max(0, view.shed.get(item, 0) - planned_sells.get(item, 0))
            qty = min(needed, avail)
            if qty <= 0 or view.prices.get(item, 0) < 1:
                continue
            if not self._add_sell(action, item, qty, cfg["max_orders"]):
                continue
            planned_sells[item] = planned_sells.get(item, 0) + qty
            needed -= qty
            if needed <= 0:
                break

    # ---- layer: clamp_sells ---------------------------------------------------
    @staticmethod
    def _clamp_sells(action, projected):
        """Clamp against a sequential stock upper bound, retaining market slots.

        Earlier BUY_PRODUCT orders can fund a wheat wash's sell leg. Their full
        quantity is an upper bound; the engine enforces actual cash/capacity.
        Removing empty orders would change the later lockstep market races.
        """
        avail = dict(projected)
        kept = []
        for o in action.get("market") or []:
            if o and o[0] == "SELL" and len(o) >= 3:
                have = avail.get(o[1], 0)
                n = min(_int(o[2]), have)
                n = max(0, n)
                avail[o[1]] = have - n
                kept.append(["SELL", o[1], n])
            else:
                kept.append(o)
                if o and o[0] in ("BUY_PRODUCT", "BUY_ANIMAL") and len(o) >= 3:
                    avail[o[1]] = avail.get(o[1], 0) + max(0, _int(o[2]))
        action["market"] = kept

    # ---- layer: dead_stock ----------------------------------------------------
    def _dead_stock(self, action, view, projected, route, step):
        """tetsutani dead_stock: stock beyond everything the rest of the route still
        plans to SELL is dead; sell it now when price > 1 (on day 29 everything not
        already in this step's orders is dead). Highest value lots first."""
        planned = {}
        for o in action.get("market") or []:
            if o and o[0] == "SELL" and len(o) >= 3:
                planned[o[1]] = planned.get(o[1], 0) + _int(o[2])
        day = step // self.cfg["turns_per_day"]
        extra = []
        for item in PRODUCTS:
            have = projected.get(item, 0) - planned.get(item, 0)
            if have <= 0:
                continue
            surplus = have if day >= 29 else have - self.future_sells(route, item, step + 1)
            if surplus > 0 and view.prices.get(item, 0) > 1:
                extra.append(["SELL", item, surplus])
        extra.sort(key=lambda o: -view.prices.get(o[1], 0) * o[2])
        action["market"] = (action.get("market") or []) + extra

    # ---- layer: terminal_liquidation -----------------------------------------
    def _terminal_liquidation(self, action, projected, step):
        """fieldbook _terminal_sale: on the final acting step (>= 718) replace the
        market orders with a SELL of the whole projected shed."""
        if step < LAST_ACT_STEP:
            return
        action["market"] = [["SELL", item, qty] for item, qty in projected.items()
                            if qty > 0 and item in PRODUCTS][: self.cfg["max_orders"]]


# --------------------------------------------------------------------------- factory
def make_agent(routes, router=None, opponent_plan=None, **settings):
    """Build a Kaggle ``agent(observation, configuration)`` closure that never raises:
    a failure inside a layer falls back to the raw tape action, and a failure even
    before that falls back to PASS (with hands padded when possible)."""
    chassis = Chassis(routes, router, settings, opponent_plan)

    def agent(observation, configuration=None):
        try:
            return chassis.act(observation, configuration)
        except Exception:
            chassis.diagnostics["entry_fallbacks"] += 1
            try:
                step = _step_of(observation)
                player = _int(_get(observation, "player", 0))
                tape = chassis.routes.get(chassis.players.get(player, {}).get("route"),
                                          next(iter(chassis.routes.values())))
                if 0 <= step < len(tape):
                    return copy.deepcopy(tape[step])
            except Exception:
                pass
            try:
                farms = _get(observation, "farms", []) or []
                hands = _get(farms[_int(_get(observation, "player", 0))], "hands", []) or []
                return {"farmer": ["PASS"], "hands": [["PASS"] for _ in hands], "market": []}
            except Exception:
                return copy.deepcopy(PASS_ACTION)

    agent.chassis = chassis
    return agent


import base64
import json
import zlib
_PAYLOAD=json.loads(zlib.decompress(base64.b85decode('c-ri}U9TiZvLyCj_<SBJKPyvjJ;T}=VoCOZY;Iw7F&JD)S6Dz;LAbkb3;lO>_sOh}2y-*@$ZGOlXn_G(Q(dPjBGMzm-Q3*#e|-19{qukOm+$_UfBGNa{h$B*umAO5{`K?A@Ba4T*I&Q;``dT_<)8oW|Kq=Xe&h4Y|N77W`hWe)fB*dYpT7IkZ~yrpfBWU*_rLx5(|2#*UH^Ld@cF;p@b|ZW`tH}uk3W|0MIZnB|NHj%n?Ha2<<no|AGN=E`tmP-{o$9(ckYWXU-RMTAAb7q<p=)!@%r6cU%mb7UoV%xeffuC)W3fG?RnIn7w?BZ|Ht3{wtdx?FWOe~KE=mZ&!2vrbMZ^J555oO=_en)j{Vl3e*59a@Bi`nBcFczGIi(2-WT=h$BJ)}6a4YRpD)Jzs^?$)DgK@7<=0PNU;O!ln9}x1chzoRT&{b)7k<55zW@C1KV5$O_%kq(a=rKnKF|5*Pq%Li-YK4r8d6sdX<t}iO5oS_p<O?Gy8KeU`npVH+5f|rkv#pv{g3b8yf3z8tJW0X?cwQnZ%;H{>-%S(S1A3^YiqL>w*Juj`n5dar!O+s|Nd|FetP=d{T#05y?w#M@9jq<Sor;Pc^pAyP~PuW>s>$YdYQ}LSIaykmYF^8dbx{Fzhd3Nb7t%Q{^|4&m#)IMS@>T6ELm^8(b!d3PY^6DxIn()f|3Wi4M6>DVnOfU?JOv`k`66s`BSMcCSO;)X!3=g7di4UwVwm7Kkyj!4O0#jzSVGJ--osRoAE96{d@b{?Vp@4`S|0Hmp^~{$A7r|^67^kfB0X^BkuN1@PiqL7x?kPckZ4+@iyFdThQ|G(a-xm3S6qo<?^9?!uPARbX1)PE%E}R)#Wn{ei}^KIcxUaSO*v3IciKW{+((i+s>8y*L<5{g8h4Fytk9)-L_sl+WYBn<g5<%-2po%zx5%uvWDB`(6f2*O;<nR|2dTWZT~hZM5;R6CFCUUTZ*S>8>_Eg7HG4JD{>aqz07`3Uit_KV&5n2f-G<mb{<|{gpkPb*{iuZ1gX^oZsM`gTINc^`Gc!@)MccDm6JzsFBtCrg@66<%YSOaGsr66te_?MvX=Wc>;qw}{Tv?PAt#uXKJr2H22StO9S}QH@$&{Z#fTFRx9C8D1kX7JezY~12|a@WekhlfeIY=>H={6~6Ip<IoYD~?+v9gaBoeO4kcJ|pFT#=})~j45AoNDWja;Pz6X<{Tx02`Dt9}Q;MD+y|y=Z$3;K<0_y!D#b1HP}t(<Re(Nvda2Mdu2OMt9w_r44`2Jg0h&_?}Ipwe_|4n7P8!DzmcYRlpK>_g7@8+m74H!7r8*+z_wzOVHdblS#OY+(7ju=zTXt4VxUH!T%|Ca6pe}h&-a>jwOnlTIMhO@e)jecY1&u_#5N)a}6E@^TO`m8}e7=_uJ2AUtExgB)`^h?E|mP_@NdzF5;@B-MZ<JTjy98%kaDka-x3FH+Hj{ysO*pwNMNRk=1J)CvV!kt0Il|T9_pES=&G-@O>qYk@7(R2-4tJr7xG;ngdsadsQ!XXlqX-N}IGeDCioe88bH(LxPXn6Qwz|)?)&I0mMqcMBZL&KTl5*Wm%~yIfs0`2LlTM{Hz1XOafejA2M(rC;7_0&mDLkg-^_az?AjZ9aw$xJKz8E@o!nr1cU%nJDkOV&|`V>)}NQ##`eIRF9(mOaQ=FgPrm=+--RF9WA;tKm~PAfg41RHIyj}^?0FGtcqn^!`{R0vj{B(*>B+j?$RZ<n<gn9sJBsR+XhQgNk+Ej9-Y3n?DcJrG_xG=#e)(|y)8&_6{xh&`6db7EJ2o)@P>38{f+|)co)5G4-1&OMx7#GfjPqx&mtDQP{@llZe8w3!#hsD+Q&!3qJouO3EHP2{(Foc+7lv*(f|ikm`e)o`m<JQw5T9(I*#+}C#^GzqYm4%_RKc9({5T~s$Wvg~dq`&vyqIzb_va2XCz3y1jPQ0%8qDj|7Q20Mh!nj+UjUs8xt;j9GeUppt&y@`@6Fmn08_93P0jP}zJC1p`9HJahwp&&_6K+X59LwVAt>W}GN?H4xmBNjK0Llx6{`2YPDUR0r4Oc}T%Ow(1et>tDtv47w4?4I=K~xE!UtiG#BpJO?^sjX!6@r69hBLEaJ+x*#dQY>0#qvIKAD9_oqJutf~2PuOU&SVe5+o^L>Y8725>w%L=RR69hQT<`5{X^P;fhx^nAlnsjE-r4}*<IGZnJpR2Ry?!P6b64nOovi}TJ52Hq?_2a5^04{4KIe5<d|*{~`n^s3S58p;4bU`%(tptT22X>eJW!p?#x#TYqcD?a#=xsZ+40@IMwC-Rg4;re&~S%MP+F-ThWTkk%}u-a8VJDPd?y`CN3ba9B7pda)vjuG2(RZ&p(b`IoI9vwAt3futnn1cP}srP?x!K5qSv<|13@1)cJ{>_E5j%3|Zh;)q^Kb#;Je#_eNoCfc(yLzt=t~?O+7c79Ierx@tBy8Opfz{4s91ycOt9h5YLxGWwm4D)h5=#->jH|wP;@hTPGr>k=YjV$s6@kk=$_lA=XgJn00{4g5g<x+O6`Vf)4MJkUP2I;4uak5o={<^ml!`&AOFZlUJ8MLD)cbjjD#5~n@dVV}r_^P*YhIqWMev@ifMDST8qs|V`uV`F*@r|U2x~S~^xd}Eh<c391A^fnO8_TA*O;T7!Ilz_2+kI~XR-S<u#WPVY`qU@DKI<?yv1+gL|_cm0=)pLx_M&p74s3K11ZZg60Y$}^J@pADR3ZCEy^b{5>0^}=A1mmuk7*y|9IOYF)G{0nc(Q|<CwvM)+?48#m(zMKYdR*ZujX=Km7O~w}h1@sl+t)_pj;tFex>ofcd71noH!=dB8fw2hih60W}OZ?thHr6RjKxCDSQSTEWY8#_T?&a<8@k;^-=_w-0BGGb~P~LUV2c%PE50P!NDJdAy;$M5c}>S!S_RSmikQ5i$`-PJ^YYqi!AgrczRQD!fmrt7id@2_ck9$4X!=eCm7B!R;H^tjUm$JS7bsM&0g10)#5HN+nF#vP|`EcuZi&Tt~b{9;ens0sZ<a@MOZ800dsW%H->c1pHJn|L^wC?@!=mGyveoo214!Dm@(8h4vdMf06As;~x(TC4rhWq8_D7Z2P}A@<DNOEW8uhnEVk)U1{i~C4Sptm!emQdvUl*{9C8)+IXHIJELivVciIOT9qEoGx;-!R<g9SdgB>m=^1ae%u;$PpGRF<yHo|Zk9DM7A1j(GBoq~3ajgoqlmu{7IMocafH>)5hJrQnm-Nq^(SUdpyR|nzs@Q<vHpU7xS7<)b=c$@lK;{4d(djdjc;u>;fmuG$4;F(h!GxAvR4Z$4Ecps3@*>~vNlvN26rS~s3>1Qst4$rJ#9q<ZfszwLc?B<_B4hqU2GjEaGjlj>j_S5Z3o;!*<fxm7)DUXlUS7FiRq%Pw?)(f{H*X~#J5nAW_2TFv5kD-=^;@B=Rf)PL2(z%B$<2)u5kbw=jT3%mR+FJcw0Op6P^)<KW<0lBocTi1Z}6&&qGTwyTdU_wWAQN$Tr<$dA69<&a@Hw%!8Q=T?M3IozkK}o>qREhhQutA+O0I8of_ohp}Zex*!cU*2%J4W=*M_<?f?iD6%x4K*ZqLv5-xdV^#}a^kR_0$g0#I9Rpl3=&*B3e=u)Whk^0FX3vwZ3)6#=8;@K7r2ugT0i!T@e=SUSKM}<pKY9K>2XWH7v&4`$e`410&fH&62&*drVu5|zApt!3VFkK+@2lPvTYPd;r-+S+kyw@%`?5Dr`&0QY{4Ynwsxp&U<V2{nc>oe2}6x5<oQ_?f5doS0g&6FqWj_}A>?@o)Hl+8h}`Az$5<XoSaOio5!=OBV}@4X!I&mT((9O=W?RHkkHjGKKjff%lFQ4F2iX-rfG96TA}@~*{!@rt@x_EZIhBQDiLNJMR*y70Ym<B@9RtFH8Oo<w-C7|EMEQ4pNv_XF@Y<ig-+Yb$`Ds2Q;E<9(=WGo8PF)cZW|ryff^!x~LcCP$lBzOUR1nC~FgsFQg?U1=>gTj6fe8u4ZdZ!c?!TU2_uk49A{7B61#9GtegRKKhGH;@bckQTPEdhj|ga>a}iII2!~;jRVP&yYiq5~WB8!DCs5cHoQ40&Vb-WH)3~MJNdxWNE5*n5cSI%&UcyD&4|52mN^Pfs0pbgbi^ig)E1P2_q?H7%ed(tbqHyCQryh3Fy^=Hnvo0B<kcOXTgr;(!1^C%DY}>ea_Yzv5!#@w-`R&C)=M%=jpdY#8JU+!gE0Kb&SexD-`)g##&+dfG6ea$eePHmDFA)0OB+hu|uH*^Uz8qT#wZb0Nh+r;b~iGA?G3mb6YPb!-MoY)AKskI@Cwl4Ok9IGGIYC?+{j>e3Hmrp4sgbmOd-*ghk!>=3s?w>XeuJsa;%*)2{qILlRl-RUM3AkMjc-slhw|UaJuxOsdAJo6j-U*Dwy`&5G~iHbv@Xt!nI?OukM{#+~ZklvIeWTxu_uzsjaU__z)`JGQjEY@;Pw%^>B!#?K%nKW7%u)nNpcUXJHroXf{l6PP{FJ`0)CKsT~EAgf?(%A+U2zXg`jIUg`hiuj?KIp~A5QZSV@VoKmt5jWGz3vAiiKg5I%s%nv0hMKLQ7{egT<bRUgBtib=R#uRS2fUgDDpkZJKyjG@E%XP~^p&yI|Kt-?p*@3egO+X8+?VTX`d!#YC7oB&61;KKOJib(0d5K6de}tY`C03Po>4T>Wh8xDu0`wYGA=+fE^BRmO&Ur`r4qN{BtK7H=WeP2gMgbk$)PG$D)0crzWNXWBWvnV4Hm^Vx`+aqti*b`y@7<MCk3YT$6qmayMLw%G-=Jt%j(2H5uQ;fPbDXsQ~<%XTmMEq#<+ibZco@I$I?M&JklVGF3Uaq9T6wx8>II^j!E`VXXAbu8=-}%&>l0Q5O02245>9f>U?v&FEBI&^V3ooy-poAw!g6|Xix$o8vmG1kgGB|D$_upfDsSpyhch079|H!9=XwPWkm{zsV9zE$w?xrfPjYy*1}fZv)hLSq!F;A^nvcna8vM^nb&ctY2+){@!pNhP+MF>7pP#7X~i_*POzK<&ETh`&tTgP^*eS>iiwu!D<e;LWRkpjT@uR-Rf?bQ0-7&~dM>BO=q0wPva@Z2t=rj?nl@L?B^ETQ1ah)EEt&Ky2|<HzlJ2pS7sc`NBE@6BFH`iI9yKZKg5{i0r-3FYjVXFGhUMZBUXo8*gMExP#;QJfa)Pgn2rHS<=U)MUO0P=F?49y@n%?n+;JqFI2a}jb8g320Q@&DKF*tU^D$-u0Md0UQy)X<c&tbrMr@>=_dvDcPL1Sd|r+OtsAY_l9X+~p^_oY&yzcNl#oiNS>J49pmiY}xYBw~P#rY#Sd7ALXO3QV+$A!HmNomR#aspVz>#70VZR8woS&(dAl&nna0vc>fyOw{?1Sq#m36|8&&U>Fda*AR^>dR-@XP}9A-__499jNSJRKPW*}FDCTb-J!Vi-iCTfK*}6TmM!BFB{bm9rBTqsk?sh|d;=7-0SKYpBCg52wx=p*v|QwO=xw#Uy<j%9JhC(F9?E7o(@GGK&Jq(J1CSxZ^`)^T#R9|U%WMyQG!=PKm{OGfxa1$dWy9fS;~YC;#+RYlv9ngeBRAX9`cTGkc7OU&>&5WY#Em|E1VrAaujkt4|A@M7Z$a!P0^U(2TQ7h4%jS3f!9-m`0E{SvfnRUw0rJRpta2u6)vCHp9WYj(d#+`!^!&UWr6v4AH4a^YB2MRIO2bYOx9XbI(n89hn$mQ+90h3@RmaA)>;=W;s<ZHb3uHGZuGKD7izX_2?aS54Gc~7t!87;pa$}Cky>*{(@fhxxkWOSJj*(u>Yur&p+=ykVo*leQXNiO#!Fs+UFRuOxpYeTh-G|zgpVtC(kUUny;77o(f=bP%y0Hy__(b4Co`+40mXw^K24M9=Vo1-!Ofzfj$EP61qs2Eo1Kq+VB}kh*q3!6J$tz-1THuy`o0@A3DYjIf)W^NAkMjKwe*yc)68CBFOXy~1fxlEzYbz$SC1{?P$L%IAjvmn@^yTUC=ScwWAA1(9<Q2}VN&^qjdlG!@Ca|3zyehvh6EFl~<F4SNLcwCXgZ|O)zA`%o*a>`avc{-E|4P&V=FPb%+5rl&-+dhg<f5!m#@s8FoHJYHQEn-_;#kxRm*5_2I4D5seza<cJ^Vxzf;Dj2xNIsX4A^PF!~hedACMFP*G!^i4pHjM76UK^1ttOvhF!%gS;c(O3c;@gwp%AEc8T5D5f$j-Zo(H*NRWb2SV?(9h)k8Rt|m4DD|*#4q`^jW4>p#718XlR4FZzTi61aRmG2R?F7?i3cJ=}f^(yPzu}^9xogJlvMxT}EBC+k-M-4DD5<<V{D!Q?`L#;SUC}>?*vE0<lAKd3rOo37kiHeA>{EccF9<7J{&9m0WoT89{foC8UmlWerfzy~<J@%wH7E@TF-(bxEglLZmy=_)=s-Tj^^T?=Y9lW8kFZbwtgR`9f?j_yh0h5lVqQ^trZ&y%H%R!hIFe}361x*yc_I<lnAO__M&{^y9F?QsT9nPd3^Pb-J1=Gj@3z|n|_!=R)cR9f0co{$AWkn1LwvKAH@lD|uQ%#Kl3UyIKMYGTa4FQS%D+m>p%g+^GW3=fiQ|4xHWaE12Aki#N3(1RVE7rTzDA1pR7`$b0ESmw(IQF@)FY$}ixLARyqc`3b%$45CIfeg$E3PHW>?hFLprAUkbjmQJ^oedi`icU682hr~OY1_9v9O$iVneM#eJnss#Q+BVj7fLGUfz)Fu*Ukql(E?x;ACV~)}#;9DAt5&5((*fC#bMY3LlK@xTEMd(`aK2oLdcDiGf8t6|>Mqlny&<NgKer8Hbd-Z?G%d^bS~4d5Tq0Ga*OmD+V2U2>7OqqL4ZhVQG9f_n2V8IIWSbvkn<rrpSqKg>G6}o=P@kgzyL+6+#_Ul)m<mRRd-J?wd`3gWv>p|D_NV=CZ#b4re5w%KIE51cs&`2ANnYmxwkz4XSVN?^3UD-TaEQV3P{3N+}QE7$(=F{zplI+5hB@(pSSP>qQbojXxB^s5cRa(w`FyQ8RF}YQb+&XQn*fedVKc5vw;mOIJqeGTHw;MG;}oi~1LYxQT&;>Q(Egm<$b7{3RvYdPst<54n%N_7qrGQLpf=645lCF(us`S_P-7@N{7aL?wl!NJ(rm2TC=!{9uRWKDl3)Y+=S}ABhJ}du1HfbCf09tT~nl=^%H7D4{h{lxb3&Ayf&E{+bp{lV~U7T2o*hzzy<9<9w_}E(_g~a!G?Sdj{Y)$XSYg$YtPts2P{zy;kM{kBnJAOJm(U<M3*4Y8GhhPNQ^2z`Ab9Mx%xRyCXygA)p3dBMr$&bPmuq7d6!-rT`30GvD3<l1fJKLYF~c77#cykiHW`j69j)IhbZ&rDlz8!J?BLB;`bPsx^VQ&P||V9f>%cYL-!-k(0{Fk;Xh5*yF*5O-|MGNf$9b#t%H_!cIKDdagcF+PYS`FqOfzJ0xQ%DGl#C>;y;-A~yI#(HPlt!C*>2jDhDFNL+Q3KPjOVu>PZ#0O18owcBRMeOUTVP)M*TGOvq$Ds+sg0U{+n^uQd|(^Mr<y|#9lKkaRNL=0Q`!Dil%MKy=3hFA%-xR+oYWy}5_&4IAeXsM17&Z$v6gYiUUYzMBfT&lNGDGzKS{bLDFnIOiXaLXyzVl{e^%hBXLkrFpgB~k3Uh=*YH5|(?=tznKxH|e$|UfVxBM4||6A}x^OF3axOd6(%PNt}y7zJh83UW~3kWMefd1t$Pyf;}Wi(-E@%45K(r7@xM!MaV=59q;fl<hTcqo45)u`<zS)YZ1k0qtE&Tx#W@8x&vHW2pv1LfS4hK<fWw*N*Ju2C&e~2kiRn;L$YGOLuw8&fCQwoc??{4rg9O6B~ff5`B^m`12Xa}(RYKl&NM+;i$qhiqZy8^0x&1K@4k6-Ph0H4aB}9AA*`DsmD23pH&tQD0ohPqjIxBtfs{ZBwZz}ldIvFQ7=n+D`X+`lDr5*7McY*EhbDg;x-=;^G0fRY_9$RyUZlJ!^l<}KERlZUj8PW8^FqR?tQH)jk%V+CnK*>rTT6J|80E7b<a~WaH_;$Z_7Y!Suy3Rm86~V=kMXLkEO|DZhv6~H{-*#3L4_tU+Lg<c*i5BnY{7;>{TgT)ceXW|pn1<!29y{A%!$6Hy$LH#XT*Ja$q@PfM1}p5scnr6i0HBVVOF$N4LX8V`X5nPq*Q}Z)aPH_ynxN36DkE3*{j|T7}*7v&;Wged37V40G%;oNyps)O~5=djUXLR>EcL)r0x8GVt4s6*ie3l=)1L6HO2LZ>U<+R&|7^&6oRLLjEok;k7G$!5}=1FqHo?o?iaV@IT`q_tk=+@$F;@>X1PlOg?<$R^F<tiV=zy(8FhD&{`aeY;e9)}{DVPPXcF-_AL^xApI7vjp(kZq98-r0qO?2K(Gc9_)TmS&5K<N^&PP)lDF?u0L^&EO=Dom`W`Fat9IZv^aKTvvgF_1S?yu1p1vyylc@?s)Q1-E605$b-cUxbVmN30Y1f0A5){V}R@Kz#Ub3`4^Knu>m*#%5}prx0*cK!ei792g~FulIY{PR2u+7l$hEqY-O2ex-H23(2lqdWYjgQrd&U%|gmb{@evE<f{uQ$P~K&VlsIHb}@YGx{SpBof25TuPEs9d~fcob%UY?;&G{)<)hY^2?ADBI!y5XkXu?!Y>Wu-9<tn%a<zGh@y{K_x_EUvV8Vm=cTVyR~N)><U)EHiCy);@z@^8QBj_3a|JRKzxvct=XuGVfH$tnjW7-5D~lIIY1R|4P&bHu2TYKzNaO<vzEyA_L~11|5!$S*Na3S?YsO2q2a83p7$p1Oq-4}pcz_Ay6I!;OKPlY=yT`3t6C%n_5@-XxBB*;txUl3K?3NxwVoaepl3871iqD{b$X!cqBx{C4q$-7pqXx*U=^Q^@*8_Kn^cP#yTk#SiE^(4J443U$hI5Rs5yF^lDNv7!4PZi>iFL#|L(Wx?4@FvFr7S(h;f%IpiNLEia;D(P^zvSYex!DWFKxq9+@{Nzt^nd8LmOJD;0K5C#H1cbUSAO0AZa(sMJGVlK10!CY8l~RP!>C43`m!B`g?|A?y1>WTIwy{5JWKK?IIgkX*G4Zj6*w*LU21SM!VgX^s%LNO+8Xdcb03t2hY(NbFdhqc8x)Tlbjw*KD{wymr`A*);8`r=yhWe><-+Lg6lVs(imI7++%6JnHgbrJnQ*TJJN*SoQ80VAV<op)A7^vyZ2;Kf}^fZ=NJUr+}gjQ1Ph;;!W^_qaxog1P>zMw!Xi)sNl@Ro#1gq}o}e`Hrw!FPDaCZ&p+orqh8*IH_#h-B1Y9LR2&KfDMy-mgyH2(so@|Ot>T{lL;6T2UDQDpI79^-^PJP3X^|s0V#)^yiHuw7CEpd>`R$KZ0sRRe=<!t54uMG|2)U)v8W6Sud%-%KM3W`1*vopd=3(l<uoND!Hy?^N^=c38`O4K|J0;mgF6DtQcxN@9GULrI{o=+ZwkdZOk&3t7k-tyKS50Nx$9m$z(Gi|HxGc706sor!MO%$HyV&a(jpKlLA%Y8gb6U3luolfb=@JlE|^rL#@q$5HwRCW>?L1CgUH$EH72-rMss17<!Kr-fl(}_-MV~UcD{fyZEi?^8h%;_0-V=h&|g5iEUi(_Lbq~?+qNwc&2i{NGoA5o->oNBBv<QC{-e>UHmctKb!LULpX;H^7fC15A8?yg4at(|h=^eN{>JwS`IS`uG{r3XA+{1LmE39CVl1VXMcNkE9ohULq|q{mFzG=3UVcL{i72H4V6{>W6~qk;PJ8oBl`+%tWE;_=fL<ZIp2GwyZu{^(E5;i5|1)0__JmhjSe5%6E0m%99aWoo2;;mWI2V(Fexox*D(NloO4lNUKKhXpUJI_m0{__Sw1OhD6#hjTw1=|})+OTW>y<N{GrX542vcWTrJXwx~&=xhSR<^gUZ3fC<QT)9ZC(PDQ>q!DsBr_bN|%SUto?z?mQfTRTQ_G!v&VYIBDNH}^Cjy+TC7FVu95Lk7P==7GNEn%K*Bd9gN24+#2OmfXJaE>-6G@kVV_zq>Sf>4juR|0#;7;8$kqB|u}Kg`p5-pDN~`o%_Wa8!om7Nyq?&nn<6!mKGeRbbyrNhmZ=>}+`D2_Wz!1!4gMDBmLZVZ>(dUqDlN!7KehX$zS6onr#BA(HVeX)Jvl(}@-^5W(TyU$9Mh6XbACpCE<{0D;`!akrJeh2vuM<AU4;M*rggYBcrSmY{P0{aHvG#e_gq)Oz@cGz&gPiw4~}nOp!g$vmp#ohF*10+3b%*)Iro+io|Zi@eVzZR;u|sEhSrtGNUXErMv?jOtIo(#dFK?q<{H64H{X8f=iwfl5HE0;~$nzRou_j=4%=Ke#qN>HOPmWx|nD4C$+uA@KqXc<yKNsbmMR-Yag<z@>oDR07XTJb@afto2X8r7G^QyrIywPJ)D0i2Z2)T>KBj0tC(9qPbJ9gjpc+s!1BaE@Z}G2~FO-3!LIZ7E$50EA{7UlS6Y$ZR$6vutv*dXrRq@I+$I<tTIugX3fwTll@~o-ouEltm|WyvnDa~T%C`DYw;eyi+X8hkDr>pXnPQEO79|%B0<TGpp2lNpK`P1oCcs|YNJLE1963<tCQYCgv7_)n4!1N-+w#k(H=zz0*z7j@?r*02tg^qG)qKfWK<q<0h880HsJFXms~hF1!I<69i-)YaT>hC6|?an6EdbOndesBFt;gituP<!6~G*wfu9isBn#T5%$8>{Bpn#TCnc!>##vrD`2howOB#m7IdT%>9oI@mWy}=-6mXS1Zpo3j-RzgrqK?s$pHD>hfPT<9*C|5S3}eQHXoPCjtXqxx0}^}(xOSw|wNV$c9;HAq)!n9YfUAc!^i_iLoU#YjIG3f7?Pl#haFvi&fvVc#E-|%|n}|tLbLf(;Bx8|GB_hxWLU|A>laUq?Q>u3?2xl`m8g0}UiEYIpESp(sSMGuq()Cc7fvN#zj#f%?jR<MeB}-_jQ9K4f#;%bo$Arg9T%!NNr2n0o5Z1c+Y8@X$`Z&NTkdx#tCNFIBLv;1;wCm4%1ZncVP^||!<DBX*_V?hRX(<+aDXfuHY<UY>(rONu%ZhnzWs~3M1_bdih?KFu2NHy8t4yYA_t+}g*dW|qo_B+WRBl~n-&*6#uuN#u{F!#D4$t*-;!3)Y4`cZ9PH)Eqbd9Ksb!5F~??c{#;?*`vgw&8h{Z0^QR>A#CRqN{j(H6kT^p9b5iq}Z5rTT&*2j+nu&iX=UbeG@1(ihTqTOS}1)D&}_aiT?YZ>M#l+dRg4{CzTs<!S3N<>#o(KxF;jTK6EJ57kF5*2k*5L38c?m+<XU)rj>5OYKj7t=(JyiH%pOj>sNfUI(C-ON?lVur2i9PJ1MG8fm?NUO=l3^RL>jG|sI_q#U@2A8EFfs$gQQA9tnd15Qg6Iggfd?sy|4P<BTEIH|QD;3z<|F)u9*Rn~*KaiR~Z&^XVzfmK{TN5(>uEm&wdpWpASTWDcWq$BkH$q{!HaX6Y+qtG9CPoP4mN*+6u9$nqC)*PgDeO#K`VSGBB4irp#^<Y}VC7&_=GVbd6J-^B3SjM|^rX|lG(vgRxjKe5?PBcYkr~5k`(w``?jpRZ@+@w3U6s3YwJylo%%{YGb66Q}!++Hyzzc3Mt3QX{bi7oU5?)(4gw;z7|{vUt-xLs3TcV{WFSYL!>oxIenffKk|3B=W@^SixPccK?IaN43sK#{j|kplK+;>U?e2Y~EU{98Mbmls0QTPWd9Ap$Iy?KAV9sV17F)&#7qZMAo*Yc>uSXc8^sq)cVQO@0E&mL}^!K4%?W?!WZJ2<DPSGAWm-4!jys2e>bC;yx_TDSQ4NRDhyJSvYPtu&eglc<Pf9{$=ZHDc)l%WW$+wjw$QzO<SHB*t1e*i_gFOJQ!KQ=&;uHQ7}u&1h{NT^HjLaF;XY3)FH7jDKyCsA2`r#U3tTA7|n;B&|frzyy8@?YF+%QJC8)Q@HetAfDAk#3SVc3LSt|R((dO6H%)t40PkE^KgzGE`29D*h61xx;)9Wp#!Gfvm~VSD%rVk&tzSI-VXy}2{r3zXEhY0|UFWQv*FKaxvRM`D*Dr1#hF^7X6A}RFZc|Nq!5bB4{^r2Y)hc(qBz#CmRORLs4-_+HO_N$GjgGcDrjQTSa<b&F3nVM?q?pg(`WDxy03gS4;~65xA`qnG=hHYF`%AiFn%@BKQ8_dLmS8XZN}>^)nW6JpG{bKSKdMYLPhaN@jV7kxgJKR$_@Q<~(@)kir#G$|lxhPDoC(`C<X#o{(?XRgCr!&5x2x)VIHeF@dI7%i8aRdxthzbJoYOCCj&vH5X(F9eJ%b{N66_ulZQ~f$&9>3aAVHryMwP1MAgMlHXDA161MvB4IPyUFZOps8O`ICmR6UwW`)EhjLKGjcwV>t0bu3Vns5S(q&w<RRk3W6*^s)NzqwTNDlZSix@#D`VR1o>+4apKQNGd+2nM)*r#@4rtHjhXC#tN4U_wQhdnachDT;J0vNt~{ab$JVy*_nMn1V124Ze$()y)8Ki25ON_fOF;-xImcxf49=lDarRgM)mUSIs;!30@Vx%e15@rna=wE0cTFz6NsB;vGd?Ly;Lsx^Sj5^JhFN;+2>T}=db&J{`tTE@BigrKF{laeAj*X((|c(@(@J${1591nsii{6**+C8ej?PeHp<_*?3cX(c=5pFE0DZ?wlRZrRz@##F&n|>wCH`z36^r>DW9t_FsQ;Nmc39e4paiD{Je9PPt!+)O*g(x?xnf)a``unv}kO?bwO<5bO|uKp1jm+wYBh313&)yZzqOB6H7BcB6LJQoGs*xQYirR8wddBFU)v^6S${_w0PQS7ymqGxfGuv&s{T>7TPNkI(GOzx?>&=kISxnh!t!@Y9E{*VxDF!)I{rX5VI0uNGu~{9nE`z(UA96LmNNbJ_+ps59rC&-(cnKK&Mx8f!nI{xg(=?~&1r?oD1fEl~K6kp-Osr>|q0)R^|bV0&zFE3?P9>P0HvvCr@6ECvYZ$EYH+tS5bNUj-+iWHWpj)jT#3eHA9?mFYa_VtpOStREnnu+^Q4)vBWJ_1EwGx@N&Kztc9ddHKBrG`8Pcm7rFlLP6i8I2nIC=YRd{<?^@tVw_L8tKZk^$ZC5~k9-?!=gLMJJr8M>1^DgWRp?+2N2u}`B)q=<^3W!%p*oIc6&~3T$Aeuaf~zkl{1AKzPa`pJ=Zzj~=SfUj6|mek!TX*}^c%AEVz-gbIRpT&BXF21kSi3_OOAYy=hoS8pIQ?r?+Y$%#$#*n<zH;7P_z$N)m5m6!;1R~VTrQ-_3N<LBMc{|<`Z}+Vf?+ET3Td+?G<-MNvT{^%^zZyd+8b$kv-dB?ZUESu$q0#YPM<%fZrcfG9%7d+#e-VfwJSH%!3?ToLJDWr}DD#F5pj6Zr)|G`-Fi6rn0ek_khPe`wOQ!#5t0hy7Ni-WL3~vFBJ*N>)45N*1nElX$UYuB*cTd9F)4O?W@AL`81^xKcw|!FHw}Uq>f{x)DS(gwQEn*gsB_rhx^|P8!p1wbuje99dW`zS02A2PqU8sPJ^^7vv<F2KR#vJ29l1R$=hxF^_eBHdn+;%3fYt|Q^W@>Ro#bp^(-+AiB^Mb>~0)qnt2<Yc*qPlEt+e>zK4AZi{G^5*%L0?kT|}u94UN;x3R8nV_q6lSnG&r{-59PPp1QobzQ}!3o(4QLj9?GMXTM~O{UV;7^9Yxh~3Wq)cavMSA}nJm_toEu<UPoE`w{d(sRDLYTdjNNey^RTR7FP@F$a5_-(AyH?nt~D4>Et;M|x6%!eBFUP9lPQTOw!corrK_#2U{DXP7~V^xuFM13xEhQq@kw=LE-%8P<r>X9q4(p<W>?@oCSmOb7&%mI*Y6vy|SO1{+L*428*iWU(>LVc$)GW7ezTG0;lUTxRcG3IhN;PlEZp$Z@SZZwo+D}uvdubV^#T>rN3CY7`(-Sn44-2OnveV}u533=CtIi|N)2Jd|*(<LxUC+!xc!k|}?<|L{6ZgGpxKo_1%*hAVG;WmI(44}^I0(H9E@lhux{Gs%Uj3&F}xw3f<7y`!EwWWe(H2uvHqrUHLi7&b~JeXCQ`d>#fxb{X>zN_>)%!CmcrEN5$Wb{^0maC(s1pU||O^rn3mgIt=&j&`RQy+}_6SroHd0P)W)P*I07n<$r`*Wto%QHfj)fCZgIl9GdJW-#^*hkl$(yRt)+wfK?uq@7K!q+1&s0hcGfeoj|9Yc%zsd4Htb+(iQq{P&zRz~bq@nd0VL!amiz;}UfV1@5*k9BZ2Md;y+O+pnQ(@m9kKVR2uNFG(ZTRhtgW8Pts(GsC&dW3)|VgjR?8;BEizw!o43`cbKC7UvFB~_<s4Jd~tF<4#C`S=r4!wSN&PWxEp6>@I~*AUw}&vrch?uq6iXdOG3I89zKQ7z64#bfI8WbWLc4g}K>E8g#iaX3OlcV98ObrjN$;~_WMeFfqSw>82x&Z$kwjQjQpB$Txz1jC&ZN-k7jo`^OGiL=uA2ctZ@ENZ2E%=pQmExp~HbsOiBAEzl$U9T3)nIzIfMcE{C7=*4FmmCw2&ZZDBg9m}BA^YdwXEEXW_4~I%QX2Ses)vUD0KIqr1q7H{C7j#W^*ew(bw>B(Y9L$!6a59jL=_fjOovc;ItB1fy$w$z2#Y^#;vBGQVPnekff?u7bduf9d(6pLv|fyAT@Nk>4qT_v?k7uY%Fy)d(p0o<WOY)p)=qcPuQQtxje??%JAChx)~To<O%x(Qrg?BG&-PQJEa0%z6bW9FzH6a_F&R*1Z6<8Y+{d$bSCS1dEk3D}luLk$_PVtKCBCT%8jT}+aUv-0dHwi7Wmjxsn1y9uhP1jpp4EJEi`xP4FBC@VIZ`<Ed9myXbZ#>*LczBlOR(@!i}iZb&qKakpzTGnL^UXSsP4>VU-L0fE_iatP`)$Y(GZStA|%RQIY6^tpoAQ42RC^ILZynu-o;e5Db0y&fnr%o@+HNKfcFa=#waH<+c7x@Gyp;N(YN&GmmtFKe%HL%iF`sB0VgO*RlkBZT}VVc-|e&FPs?&WkvA#+PVq*Fn?SqiX~wk_qevudgURvkajXvw+cwf7&)uPJ5l41Z41lIg^xWGsu=lvKVBT=}(p2QT&1Uc|4Zy~^jU$a#HW1Sunz6Zjls(gwoHdjP*2$~5-$p(8{g%{~8sKD6*z6P=yGTHxz`=^Ocqa!ix|(w6_QADBfA${&@;u_;L=BnzDSZ~(xEEguygIZJaS5yWhAWe=2r%~d>etzWGmX`L*pabar%@PKA@IRHXQ@&|Rp03SgDljcA}*cXnWP>j1-ih<)aH(rgWN!W>0SSyavn6(#BR%Kl$r%o8T=N`l2M0;OpK?_r2*R+8+s`LRFWAMyVDwFGx}v}uz4_UcB831PkM%IgOv9!0M-!XYc(fyfw*wAQYg_P`!H<F__)I<*?CIK@<)?|mNlteJSpM_%QM9vq?M!?hTHSM>uT5eDdKS5;8}7_+~IP}e(3r}jd!#%=hqs^&<!m{a*&&q$0WDGj$*L2BSRb7Ab%jCd^vO(EfX*#@LOP%A@>CgXl|sjBOi%YtYk~1z*w7f3Vq0cK6zQxJIKm9rmig5Y!}Ik2jf}Y>NZ*?1Ka2ss%)n3GxSEhVv4D9XCG(#%mOBRHl0t5wyOuxUSn}`8cW8?K0{H&$1YO_;v@PHE5`~_DMLTl$iAq)0GSG}+DfnI5MAwLnaAcb&%y+h%L1+n)8cIVpYq|Z9hc*WY0yjT(a(8pC2w=0`=}-)L}jBxQA0@NXpkY(${myhQ^h<(vh|HTziZkq5vo#J6!9vqw){+jNp6J%)~XgYg`WA*Ht3*g@8Wg{!CR!LG0X`gS-^0OW*95izrr5rra-xon3`j>ky`f^Rs0&xB};dJdb8DB)HN5}XTxYuh@IW6f~<ZKy1~QLAPAd8g8T+@!w~dui?mq2IqEYE=S=5xpwf#1d8R7pRtiBpV`a^n0*)2vI4}%KNWO9}#obDIJfh5}(LW!W@H&KHKz|t*tvs*GQ2b-n+^q2o8BaEFlM3r-^PmfCGdf%9t8_Aou>x>y+OvW_gOJx!A4Ww5=54XO+cGYJ0ZrT>AXBHVKZHH5_V3z8J}7vfEZf7dK#Z5D%A$cgnZ>ZrLaM<4GxtYj70X7^c2S`j*#<f|jD9Nu)IwdwVxM%B+Awwmjo2ZU20@8}f(1>$mlRzEhgjz5)3!=h+Qv8m=#x=PsN;i+(V1l%<eIWv)g~=1Cln5BIyKrUbigRc4$MaS9U-S=&{dVBX9HL(%6Z5VgTOlXc_f}je0~GMTrfQiDN9WxHDLG`a~Y~{28%j28ZQW(sP|=1tH9_~2?RbXN%IlET1&PkCL3#Z-CWXFgIY7`<XPQ%4q7ptZ9y*9Mub+y#dsxn@KT9J-G@HM3Sa>~BW0LYn~?&3lIuKY=TMKXtf<R!4laNB%cg1iLTF;{+yJ*y5aPTNUV!2C)jOx^ynx#6FeeoL0ga|oe~RPqDfedU@;t|A^KhtN8+clE(c;s#pq<qN#hhUt8%7C4F95HIs5RCe9T?dpFNeFoAV#OiPSTACQx9O=b4J_e;naVeO~S)rX(Vf%&$f39yaOC6kbX$6$EL-uW5=?n+JlcET5qeMgEU;KUl6^WVEC(FByn}fDLJc$mF!W3Q`^(|)R1N@p2o#B7O27DaB{Y>c8O{MiiD6uS|V01B>n{W@5XZOHHh}Ow%`Bom-sAp44kmcT)+Q3*o1Gi2_L6JSkmoQPZ*B`178USUX;uULu*lVGrIU%@X>kFtS7ivV;yj~E585b<KL+0bT^t3AQM~n*)Q5a``g$U+>MKm9w~TA{q>si*Xr8D@EI8Nk~EGMOXgW1NAY_b>}sDfV1Xg%$ht#>cI00B%gNRn@QT3dO;>~HE$!OMad(iI_*hxE1oKdBj_TcJSL-7LHv2$&|M1{!M6Ky0C@GZB!p_LzDbVQ-EeMT6Wx|-Ft}Uwf^uo!aF*ftMHaG=HQxvZ;<Vb3qn&Pw^$tVP?r6YN226AqOGux_@_l&(LhayB9E;;x9MX?H_6~ix?WTnh5<ItEf1r7gU@td}S#n8gL>cr)}6ry!q6EcRThb7O}xQfMF>GkCHj7o&7D#cm{-oPCU{j{}9th3b~mw3XV%Xd-X_nNq1YmbYdi7Ai4Z&5j{gJ0jmeJ!6LV77kxR^=JG`MKW@0-Jw?<36~rFyOQjdD|o=Tcn2*$!Q^jStiRKQ^A8}?pn~A{n6nYL+67eR->z-Mwk7%w9?vL4}4YfahBW$l~K=dPEu#vBB~kW5QJPknAPLnfm^1W07+x*HRVH5Q(l)mT*-*M;x}5MqsbX#*^piJMkSP-0)tw@BY_~K1UjI3!#9GNj;GE>2Wb0wBBj*W<1QU>KPPkMeS-bVHjLQ32w+lusxtCQMY8I2Iz_Dg=YM+AVmj?N@K|(@uQwnsP^h(fAAhD7uokW5Ytfc__2P`FtxrI*Ju#v<ZngY2mBMkcv~RF9e(4XX8%HW^O0hVqq;!j{UbX_WSOK3ngwF??fke7m8?|!B7vk(L1XS04z;4#Gto0xD?3=2C7!*g5D8Hd~j8V?PgqJEj3z%kc8@RD3uJwt6wdInkT02G{a$CX@K7aEsAM3Y2ef;Uer;pk=-YRYL=Xbw8i1L%~dB*2AZ*ej;({1s)BWhfffq6@#s>gTxpxHk#p6)iMgDOoA$H_N<<;UTePLlxJ1(FjV5H`J|KZ?qaMIAEmr<wW(+2n3>AjLf#i`wMcu_c(_9l(IJM?>YA3S@)9&abVpC#~ADl1z%zF%CxK8VpGLjWp<zTPjLm+)E2XSmZNEDPDcW(ExB8<eHbQK<OaAJnR|V5jbV67djSI#zf2lFD|j%D-o(8GAv+>-M89y4fd>TtcA$OsjTDZi{)QcS4~l^`fOGx^tFo6=xhdeuh84Zu95SL8+EPCSd=SUDnzW$sxvAByt3DRdaY;?6+UDvY6#Pj;$IdVocGDi3E{bnWCGVzlrX#Ky1EVi?CuJ9)-!rOJ#@1;HO(RRaSm}T>ZZxg;pr$U2cV8=dOAc;W_|7L!?+DhJ)F-nJh7&eT^3qj;f;`3c#DMOYWDyu%CN0~M&5~@R$VM(mSszhMRhg_dSb$deb*V-KcE-}1uFnj8TUyIxqSl4M#BMuO<%{P6eIC&l=_#SPP1j7>UdZ(*y(9VZLfYo1bT`*Vp%F)V^O@;R^dz*09?O#ho@3XP<!HVn*U8BQDw<^qKemrqZn#!mc5FqW@o7)3JZ9j$VH9Qa;PjAR=+YCwrX6gg3FKUw#lq5lc`ZIPw*U^t6^Y0pBf5(YpN3?59SC3&X~K#lHdeoi3#hPbz$3J`#k3?F}#>T$7nUlczqsP>LXJHq@v!VL0#lF_%T-*NwQd+mz1pO2*jO$1^In(5F632uA-)HAR|u6d!W`;qq4A7ov`mqw$yq*pA*IJHet%td8$l3#MzizH|!HRQ1X7I03p&BXs)cyZehQK&nHxCAjbv}f{lC5G@-i>=a!<SJ2NFH)+X6Gp1amMPv9%4QU^e&A_WeaStQB}MAC=@Fp39d9HHmIF9-Hb9pZ&SGRIQWWQ5^;)yJIeaR0$)XcF~$8SnQIWh8ii4?WNR4NWxu-Rk4GsLef3i*k6tr;pndvXW;<D#h6Z=VT=@8E(DIjTwM~_GnbuZj*Vwk+;Jga(=)(`&{#;c9na<!TP$jcW<evs3$bSf^GCBW;^4LI;wBA6)mS%;6dHD!h;qCV+*abIRgmA-|zye;t}<?QFexnidiTW!nGqP6N68G8}x8UqM>%!qHGCm!=yXyjmzi{G%lSC<QZ&LgXj_g<DJB&h~bU|ctY4ILZpr;vxm6mb9qZqBwy!!xGF3lz`;e}*vl(au*ae}UL||DkO~$eu{5zI{Ro)Zk_gO#6$Yp<cS2K%)Nq5WsWv4HaEP~(sSsKoPI6o9d!VSK_hc0m>cG2JQK@qNjOvH5D*Tz8Qgt8zH-_YH+1g|==(Va!JE8Mf^AnUNo8No>qHhd#Hm#Xjxim>h)OC~VC1SX)x$?CL5=DfcODN%hTH{^vHv}xP*q_7Hc3f$lFLk=bKr&eU*_Ntg?cA<P$>7@1mnXQvWJSEAtiTpa5ye0}AKh6+2|S=0#61LP{-kD#oCsFL(G}LYB*1<!CUoXR-c?@UW@aX^HmmalXhC4zeA7wx?x4M;T3GH4Kt{CDCs{lXHUcm9zs5Z#%?6#p-By!cQhF^@QAUqy&CmuK)rFX9N^4Pm*zL%Wwdtf<Myf$Q{yRgej2HGb8EM4cCZ(WcN8ddu4)<+gp!a!oD(>~PEUBi&5iytgu;_B}Eu&wD8RFvPMld&qgLahyV9c%hk6TzU^>cGvZ+9uC1XkLeP?ic!y<OxUl7Z0&)B$3tSNc-XQ_);H4PV#C`Zqwar+&5RW5|q68e{Y6RC7its?Xr+_({oz)ljt+9pkh#h$6`v3!Y@pY6`l<AX_BJNwMp=3}#Apv8IfOl(%v~i_er-g&ljhSr56|T+!MN&`O&7{%ivr{lF!mQZF9`qq#&w&14Y}ibarJ#=B*WCIVi;Helr(G1x(*X#$poDK-Zdw;lHP8}WF}He&I5f8`gyuJ))=6ZHbG?agxs@NEKX!q#ar)K0;~(uyWLJIRW3+JCT$y$_16LpRU_(Whi#I@f4R&^rjs!zk9li8=O(E);wxT8&w~-iAT#(j?2rp<fP6J`B0IQ&64vZavwwPhhl@z^vP%)mPeu+JI3^&8A&f=4JYih)Aoxy`6-_8$FO_yF&KPZQ4R`U?DQ4r&CVq{2BI<tD<pKHyFp<ZlyF~`bqihN!Ed1NtXy)K7qC;O%>}-$@=drDVyZl8>|djZe&?IxmI!T03_w!r#wlaIEWt)scKQKs-V$hGS@zyS$C}R^#IiE55FTi3e$8@bL}bqoL&P2O-({;;Ovy>PYgpZ?!YB2ahgWAc{&XZ^L=Hlzc4i8w`r(s0;+6?pM>45B0b>!q@7eMUbBDVD2q`bLY{bieNE>Eyzln4yW2pTvpPXbTa&J7T3p$QK<U;^2ol}~j+4Kxi(w};cQLJP0u(%gRFX2)vjsj1t>ud+G#e#k4a)2c>$13(T6Jccy9Vy@-I-zABmv5lR%d9L&`4qKZRs+rmvAC3QX+>g>bPGH^We%cDJ}FzBnAi66s6}~)ycCMUm?rH!W?k5ajueI<uny#-4gNlFbRR;soR8Skz19&rdeI<4Dh`j1sc9%@e|C#Wh$)sx$x{1ypNe53+}*qY!n-&ea9?ix!u!HxDcqtHxnEIuxSFEvM2-xv0IC>2W!EXpq(e!7mzpjKE*`e^d{<sskSKldOU}#3)%cd6?wch6r!W9A<^%JV1*PP$sKh?wYjsK@Vo@B$efB$5un~t=b>>&392N~>}KK@RO@pi%4rbmwwJ~PL$FEjOl0~@&MLciYNMpqHy!Bkk=AxImrs?~MspEju2h8J8}XgW()6IN7J|VP*|GH5`jEtFe3?Se=2ooiT(-Eo6Apqp-dN3y@>W84iJ>)T=`v8FQmrx+m7VfH)dj-#y#C_rvPqYRX$&>B9Syv*s-ztn0);=5&F5&6jo_DH?2<1p{0u1D2Q4MpyCFzpEJLCQ5j^<THh;psr(k^?J}skTI!)yWOcoI^l92zKo66){5~aGQ9#B*W*ix?ncE@a=Mk3JlMem<maIT5W|Moxx&wV*NCRYcER-bI*le1?YWz3hww<#OqAx9PEn(&f?ZNRHaAFEz4couctgG`W{hiq&p>#6N*g6E@`>qn?nzNzG`N7_D-E@4GwYGnJeV2elgQ%9mMV*TjyvN`o`NuRvgJTZQv)A+DNp*y+`DIY1I&-xN4c7DX#)<vB<wV?1K)!@N{7Gg!RvTdHiwMAjNIG>=w7yV)@HtK^lTpdc4rk=WUn~l=XD6t1UCp0BbTBEobT_0*a+oH*KR!8oCQ+CNMxvSFFAukd7_quAHvE;5sYa{0%u_&&O84?@aSy#I)ak49>U~1K-u5}?hI<@GXIiCJ};_<z<sO|`kHJ>`4@QT1BrlijiEU&{r)fz1|(-^br_xbmJH4~MKv-DL2_bu5?U@i*Z>EKz|LKL)L!RfjUcl7l?e9wkxG3X9)LCInOY|W=BBWzC1q!Hla%?GZROdK$m{m{$X9Uj7VT+d5fLf#};^|O5gGFgD64!cOB$F*ehY4LTYMR?0pv3((Slhwiab-U@@_OguYuMo*8-AAb*Uq@N>+8_eO{u}mY=uZAqV-9XcgPX<FFp~CX)8$A-^~UkKcECs=lC<_muY!5-^ZA|B)Wstsso#Z|MeGlDM*TOZ4x!xz6r{L>z3l$Ro}Mo@E0hH(hY~nup?R`!W!i^rT<+I+N0|LjYy7B%x_MjbIdRqOKUiZaO=UTUG!gbV|HNUvxl6Vx7bw8P-oW%J&bOt1V{%ohegbUvviBLC*b_2Y=1{Jl+QQWlN($QW&fO{n{Lku&tv5^)RoZ94*_*FF`Avr7TKPBGDEcb9BiToD-yL>M6-iB8Ng4OZAt6t}79x#c=3Z90$B8_7f^dwKbs%)^tV&_h)sdR}p_OJXbgs-^t7*q6n#cIMqR06qWU#rP+}slf9Q^j2nQF-S6=)e1Et>neLH!H(Z&Z_;OOKlXV`^4sUlZnHa9T|f_0l^&K942eD7&?rA%9#UD&y9L&V|k#kqi*2MW&fS2W)EG??6c*3TI0O@N^W~C@~2oscSzM3UR>gG!?o4n3lO>a<qnd=v_O{bqtZF4lxr8=aF-}nbBa&rc!T%B`m-w4VVX*&)6v3$JEUz<i_T1EArk$(rp@(->}zIiROhm1d;LWWNwlH^YJu4z!t<VkLvnR`@nX7PK(Z@F;K&#<)5aS)uZ6^JS4IPo)cw)er9%HXC;UyvDz|3tl_MRh^h3S2mU=ashp({ow~qsyM-%i#KOn+F_2WFb0}=O6xE6P#mSbYR<KBM>}_rX!@D4T^BGX<`sfUyyr=YRSNxe|ib2Ze(G#t9?x@XBefCr(W;Knmp@SN}pJl3t9Xwv5_`u_u8uv2WkbdWxpxE~E>!%b8F1e*sO)lm_wh!Utl@K8nt#q_y8Hu}gibqLe@Bp>@uA^O1W0lsn=GpVOBzS7Ct+*`EwnBst0+}TmG^&ul{DV1slk{L@SK3!7E<$QXP`O;bGc{m!kK-nw%5=*08sYRK-Xxmd42)bF(P-g>I+%C5xv*SxAd2F-(zfUrdi8iWtD0Hw3c1yU89S3!QQ1NK&`u?KuBw>}!9Y;ztThO@f{KwJX0=$J_D<_E+#ak?nh<)dRf=_#*der7BCk&;GUbJ_z=aAL#$R-C9p7==0B2Y3%Igr9%w;BG?`^#2SEyUn$3bdaMD;fhCijq!1sZ<j09f*Lq58>JXV#;*cT&@j?C6NMQf`8^VG}r_%DC$6F%<1G9j+*rGoRdzLR&S-Fv}u}mOtSzx@MWj@WUY5jnNDjqO$6F?tN_vacb8vAUxB<Jb-T<2A=>xk(JaZg#8$o(WVr{+p`c1B-%{iu(#=RD%C}}{J=yen*`75!BiIzONSqfP6puMz!RkcjOY%`mz@h5D=cLD&{4s?f@>TlaAKOXx_$|uErFlvT_azEF|U3Oxzf#LDR~-rT6g$!;pOR62h3mJeV>Pv;d4%W_tCciYq{BUZR$2wgF{(+>BxcQro#pBXDJf)P_X(fpsKSh&|@X>F^IzHVlI!he}sx|*ZV{v+KRp0+C0%CFvSP<d9;^yKUJ#Jg$e<s)cI#eivKNF624C~Q<lK^rBb+*sFpYIwSrj<`?O}efJ}J2_p$xyw;z7|{vUt-xOH%@pEFb%^Y~nJ6R^j3Zh3sHe6gXm6Q{wa=Kc`nCo((HidDNhL4p8g0r>W{P>@i@PIju8&uflX4ZK-jTbPy47XN0HF>t84P#%1Sd6vKjqH$`I21N`h9GD^Bvy19jz}-47e~Y3nR36s0QMU=GECFw$*3frEDdR^vNOK`y$o%Ugw)Frke6`}IGLia$!Ieg(CD44vhQ2T|=|mM#T?tLF{*z5C#itl8W3svlF$KRn>Fnv9uwU7{NF+k=5>-tTDFH1>GGMjO4bh}vV8A9QoIe*acQf*WcvMn~fbi8lP-h$Int9B;`FvPbCy1-jLoRdz!PwZhX2k6&)!)4%w?X@Np5Q8Cz8sToa;e(eNc&9RKG3KBIbX7244^%1J!aA;0gQ9Vh{cd5I-5Ja4ODk|BEvRsy62^N_UiBG%R1W1U64BYK+SP+qo+R&rcDgroY$1-7I1F^`^y$~I?DRD55uqWOBTHO_;qZu>0)zZ#+&o>cy+UGjm_1F=TcIQWz&qp1kr|`-GkMka6WYzd5^r*xVR@Q>TMxRxDC9|2xSVFMGRL_se(MoxzIzS-OD+b9sVvA;}wD_+W@5k8qIQwNDX*lp>GAoHnj@R;5CAS1w(vF2><c~-5EXL&!;wjKWzx$FFnG@W1Y$QbZ&4BX^_I*!OZht+8jV`oy;Z;0upIuU6j0>Piw|4RO&B5nH+OoS!R`(#y<Y;lyVoX(oSTn!h0tx&LQFRv1*-j*V+Bf=;Vtt1TW0(L(Yj)m!eRaQaZ{0$Rt^$Oy6q2|G!Rg*oXamv2Ke7b8Y*2dZT7ysn-~-s1AXZlim&MQ?U%281aZ}kH1Culg@q4&i(zJk*$V`fE3Jgn{B-`_0}sQH%YCctI>7!a!mWQW-%>Qt_hwdOD*0$jwpjhsFbtdvx>%J<AhN+ZzWsa7`|Kyn8ZGX#odJ9O1{0o{>3dH7@MCi(R_-tpXL-0RS?1A>D^BsfBNw0WBG1Df_b!q%a0#_F5momRu@Bfw2seH>c7lp=#+{CDD(lgODR|-HDU;ps(Yx<!}+1Giu&?FO|2?9Qy-$XQ*iIY>m}OD`G0kW@Mf7ImC)q54t+w%<+cqN*Zk_%&Ju8Occ<Qm*d}aZzKZojX%*x)vYC?0hTpIHF>Vhy3}-*rSl7>>wvx=5L7&I$L`!{tkg^N4GtX}*n)}s?1N)<&Mpt)JHH&}L8KT0&=%e*vGtCVE5_7=02C`9Wu^ZyF`l&<yD$#i`DQq<q6)m7jnDa&Nao;!G+TErIGt8<t2k2K`x9nl1yG2#JIL3T(XPu-+7yGRAIcSO-`Wdh%?x4cyu*ZqR>U^KeS)mut`};YyH(QJw>VEmEH1)1H5BdC1&H4f74VWb_a=R@NIivgAl2104TDvszkWr%0guU`Uyn<N6>za9kXXK3YOWAH1&CUu(Lvw}48b2vO0JuNXB30>Wx`?!m&qN6`Rn^lSOSD-kP)rK$s=c!6banXup5|?(4_ouCth;JMR>r|+@xkf!Q6`3;^7oD5eD2Y|)hNaM63brp1ybexNTQ9=k>a#`=-v;Fd%WA{U@)B-Ie<t=T~(zSZ4Xm#&rw}z%zvkmWTIKQ<mcl|+&C%)1)3z5!wP~D79}uB&6DE)IOfC(u-n2O4m&~tJXly5j8RKj0$rr^L^&PDwLvJ9x2y-`M5U!07}J!1fSxUbcmEJv1aL(AqNdL%);RSonv!hI-LBk~l*+sA1JV%&EAJy)xvE>*sW=vv&|IG$bgtayl9Tj(B!d=VPqFUxJAPX;ut^*&|CvBCPE#8rOR}_7C3Zu9scppP9E$&bbWx%JbQMH-L3}6NV3N{vvfzQe@$G5Ksgk`<)2xv-fP$=(Z8cj!&f(O}4JQTZ-As#O9I*<;w41uzHJ_EFe~a*v$Kz^=Y_u-<^DF2VDpocX36=UuHL;wm8%k88q(r)=URC|@sw=B2qw<PFFHcXR<{oX+nw!1PhGI-G0am!7i{YmJ+{CDdB=V+SJ|)48;c)w!uYUg1xOv9#I--KDW>{PI<9;Ak<Z<q&C>cq1zAw>mN(9a}uARu~A#Xe-nS$=;qTR+b*gHrI05O`EyQ&VPdLI?3Te#qY5m{-5MmvhJz@+&9u&?DJLP&<UQ|Di*S4L|n)zdNHUz~_cIW(5<#}bxAV;SD%V@=7~4=srgQIWStX+b<xt3OY&+2=H_jXizA#qG7+s!RFEsrtor+D1B^Tzxg*#Wt{Vc)Kld(lArn=g=nvufzM`u!hhy4arQyps5|!pNzrH!EJ$+bhRdu*L^8QH(|`cOaS%7H68x7xF6*Oo&buF5Y|L4Xdyhu{*-$~+jtkZc_F2Gg<9Fli$+&~XpU7J=5v=&qJ-+Vl>^eyBH2~lTBvgDBuNp`8D^Z3rX((Q8G>r}X;$Y`n;@~JCBe}svdE(?sK@{pn@Rct?$R_%f)yyi_k|x>A#A2~>m1OSqZZhEj3jjy`G!r12XV?<kno>Mk_;~|D<$Vxvv)ZpwCMY)o%34e2K0$MrXT`McVMky(zbZ}40>j4i=w-xQ{))152~e#NgD9G3p5jd<k>5*<M8upD<MXC8KOBUatR^Nu--w1C>6Y>QG9|2Du`NU$_R|ozZyVB_Ib4B|0_eT`bF*<E3}SCm_@aSZ9zeYkU`g-<>LhMzN~H1L`)j9wl;W92LVq!*0qDr<tAos_jIHc>CQu{ro%I$w727w6W)0S&=#4KXN3w@OYEmwvT2<%5MTfXdJW*f$hFBlb$*Mt_-b!)3{QnB`aHqoHtQn;KWB`EmPYVM0dITIfdnZaqZW(X_?I+;%x@;af(jC57!8`a%=I?4)}!=5C6=Lbf1<@1Dd=rJg1F76E{VAHu^%Fc70|0bUV4(~5ckxB_%yg}Yhdb>B5M?5liuTenqJWbsjl0Wjv|@?YXIk+_(X~CG`9*0Q=Pgjv(|Rxwo#wm3>L<jtLjtNhPaQj4Q@?@9x}neo8~<`{Zt)Qc>Bm;_H_08yt=N<$#Lj{N}@B_OseaBW$!315=v|hPD?e)A+w-$&Z#CLQC*f?l;IvAg_a3j>ZBS8>l4neebj?kvdZ^HUfq-+P<ZNb;d1~$Xx*-48`hl8+B07c4i|i`HZ9UmC2Ck#S^ilW4HC>{HCWe}*bh5}n@wSQHIamdu||!l@5}yCKa%r4;5BpR*kW*|AXFq`+@BgS3@QO{9vL-z)4nFRk#`3p&&+87CZ(J!CNMJv#vMt{?>5x;X0)nXz|&~+L5NpHqUOd2mN)#H3{U%!rdo7RI=!Z+R6m(vGHt}*GA~D#`ypqXLx#^rsW)Sv^If%AjC#E|<x6m7q8`Kj*&iZ6b}L*uE{N@^nh+S-a%f~CHgZZv=q6KrbFZ#6ex@f<RXr4*O+%MLA?US@(m=2>)5I$53$h^Y^45$@P)DwDF1p~vNHC$jgLF|`ZI^JdHp9R#sGWFb(7*%VMmrtK4k2|bDvl&ua(GeaZLw#chhm*=4X%krp}h$d@pz%AY6pQ2GZXeS!uAK|bOU9r_hA>(S!Sm+2AiSU9O%rk+1O?@c6L#3D#Onng9~GYy1%im@iwXRt3<F~BbEgXM_sX0F)HICdA^m>y3vmH0zAb+<D`FgHxnLbEu@PYt!Yx8+d2Z4W6?BuqAl<O(wv&6SL*~v&Gnvl!E3tSf@Z!i>41ByPr?tjmT>8jiffN*OQMi%&9vjAEedv0MWH==3i3d-5ZK*ceb9m#O55Ig&PW?TUP6!||2pMe<n|P_{b8LrM7JY7sY?1Cb_!CAm{>jf+qVir7DMNMU+;fEU4-JA&TL;HOTn=0Il(u!+q1)8qC}hfx;w*y`%aMh4_5QYbe3z$?R3p)7aX@yKZYlPp0c$BX<vX{P1P2p4sM`#O<HU0^}@{6^qWr93$*W>$yHi+4y2%w9&fKFUvPDQ=j3|$<#+M(;mcQbqY(9dorv?-HSP)-FOx>Z_>hKwZSACefUDRRBxt83TBn|+o7B1UY)CVQ5`AovHqv9e>-pj+IkTVR;O}qu%ZHzT`02w}yZv~5_)H`kxGhNU>fL<#*5CxH-61N86wGNGko4jH^xF?Ve*cfpzwqg|3IHZeGwMG>er=D8W^~W3>Xd@H3r2D=nXcWWnx))&PH&Hm%W&^+)r(ZT<LWkclTsBiWyDI%=fS}c9yZW^?`FSys7k_;DlbF2yqjnJ0MUdAQ<tI5HP!d=d;Rr0h&3s|fvg`gvUzD@?>67A^O_eA_v)=_uaf6D;&#se`q#_lZ}-J0iW%kA@8fA%{EgNpZ-edJoEvLe0{+eU?OxO`S`J6pCne5<b_GZ!`NWo&(~z}eLsXi<Y6!vAm&?ipU&2E;Pa+u|Yv;)oN{+_6Z-VzdnINItvFJ9^8R{QJ78I-_YmgcINrVd+5*6y)I{R8)H7I#saA`B~Md>g9V&hTKK487uLY-mS%JVtZ2*|nJd9{b_b$P7#T7{PqaV@&#<U0`H+POdNn0K90{jHJ<vCF-54U5R0ZLoHs)*o2SzGXF?9bwVax<&TBhO;g<uGOI6l@D@kablTZ9Nz^>MNDkoWwMK0>ei3a#^T)r9{21o98DIO3Gx7*BTx41wh#s4li}GGH!%WBv@`^mAQIw1U5r_xORK12Ppt~ebWsd7en{)dUZT25t1>GP@5ZCt#?!UK(xHZ_^~3$|g$);B>}nJoaRF=4W;6fFHsE!%)y-<UoOvsU(V|n+U&miw*KFh0XQFr7^;TqNclKgMc)Cw*AL7-s#4t>>x=07JR(df8>xGsuHi{pntJK%6J{7v~dP~-|<M+yu!sm4x>*`i!)A+$!$3OzBKb>5$DQeK%)4dQQXDig7x>pp4*DkRs0s?82qWToLnEk2uLvYUFY;lf5<~3OMH$4|yPC$CeSGTPOQ*zS-9@7?1OCbHpWEOrK>-3H6T_**ws0qlgZX=xqq!+ep;_mPDVhL{ZRXn@Bwm?SA8XGA^--fWbJtcw?MB@0GqSI<ytZm&s6ueT8T-EdCQnP(`%6qHq@v^QQGG^~Pm1wC$tE=^p6$K)QdiqXfU+DLVwW7Kyx;nbwA7L&}15U5p5~@(K*Xjz0%rMyNCJ_MFzwNt8B`8Wa{Uy=0KhSX>=$w#Re_in1cjv57=pZUVB{Mz6;H>gyBKhnDZhhxRJv63Bh4<d{=uO>8nNyYqW{RaKlc96heXj^?vQDx=w$w~p(v|GHw!Cr>t}}(r^uS~2sqcHc$1rgbYqMpcMP^k8*#Vxk+^DKHiDO>+-oP|R+ccRltl}3?S`ir4)W~OONLzrnq{esOCrVqnekPaIs#@LLRQTfD@<I+sp4IOQF#=p3eR28=0c(lM7F-v-&?6uMr(C2r-&oVq36r=-IUQLLsBQ%-#sFNAnCAOFvZ4tYxIYsb`Yb9AYqJuE>CoAAmAu*I2ZNU!25dv0kR9V2$G1r)LcuI=7!o~~aC{;*7K-S=Y9_fz!E8p`0PKB~G}_oKWQQL{FZBowQ4|P9GyB4Abu28!A#x#d6vYn-b-7IVjP7G+>1f<sG~;7b8Wz5TX-r3!^!banp~~y#F0;`P!8`Uho__b#c@f5sol6D3I$Z(uzqL@qMOt;Yy}EPWdy@I`<Hw)BW^bVtR-ZD<$RGcJehI`utjenG>-sVDUw2!c@>B>(O*HtvMx0aid%Ud?oASKROUtoZ0%X9^scVE#3m?T2FP6=4(<Xj-Pg5e`sOL~$1&=m)4aI8iONFWi1Y4Xn6@C2qu<J)Z8DUmES&%GY@U)yzSgL8?DbwQfTnK{{6#3Qi<dh$vW~fy@R$-@#jR$3WORjsI9KyM3kn|2_N(=ttY0W3M-VgN*sjUy`Jw0^2s8Y7kV)5P-^hwQQz8UMbYr8%w>K)Qvhjkc2vEm4unWt9S{K3sSyutxf?C$sK=WR-JB5GDt3CW<K*%lz=44i}rF)1o6NhuQK?J-s4O8idFFTrNnFQj>~0dt_5M!K9K0QeQ$r=q6w`R17w2}<(o1yE4@ou9PHsL9O+ZAw;;Ca}(6a=hmglVM`pMq1>#J5u~~Xh(S}wEEff_6+Pjt}K{0$GS9C<!rMVd`qhbk=!`aXo>ETcv3fS!Ps1h{*H;BvQCe$Vx7Daxoy;wFWIZE)Bq5OLa4laW*j1&=Z03L2<>AHj;~n>XnXW${~;jH!*HE#EIZEI0^?bHEk4pBT+_@*krr1nwo@I({!TQv17{jz1=LQ`Q6cNXz>11o?m0`U2$gA}_YbmAC&9lcVhJoLW`;&arZ#sB{kd`U(!2gYh4gi1#m4LmzIZT|!B>lxx#gf&c5FO#V<TWYe!>r0QH?F-?zF}_*M6BAY#xl8-Dqmh7Y_<7uDo{v>;ndQwe&~1F+5mIG+L=_WaYA0ddv8@0fTotWV$SWbPjA;lVXFD5>KX@-QfpmIS7W~b{6ou+GKsjp=oF>oKiy$kAtD0)Pr?PbPPJb)<}kKXfcw5%;r2Mxeay{gRLDI;B<3PBOz5abeZB~FeI<>P*_3<1~fMkx{!}Vd7!qx8;`X~SjdMA=#!U~IYYO&++E(dp5ZewKMag#b@{uLd@9;nhQ*Ag?=$p9yke@Kac94=#Z!ujIux{ck4WW%4a`$MfF+lj$NOY@`!Z!9KJA1Vy3@5m_k)e>3lbvh??Q>ndOgD&Bw6OMxs;+X0p+sTwIaf$A@)Dz!(BTr#}AV!*<{b6IWLglZBE*Ht1Nc}rhj&8%8?;csw!(?7v6OR;l8nM9Neyi2q3w-dKFi@hCJUUiH8K%sut{e&-|+67GBsS`p#W&W%I(6x`71@*Jy^Za{Vjpk!}i<8;RwtsLtb)a`aGg?klDZXF6%$$VL<Su^F~LD(|ylv?s*Q?ogNvz6jmmVQNrtOCmubHUx$<<JdkbsQ%`t&oIcaiYvpwK%PkhrMqoCuFcB2D_H$`wplN_+4Zw~DehLv<B6KIY4#!W&xa<w4q+J3U&iYA&+9U%#=?zf$au1Wn^agw)&5IK(}yP@<<jV66k`S8+LUxopFzlLsSl&EFC310>tN%yjLV`y*A)oJ)T!$aVN;6zyS9<b{_bSi9)<;CJg7M$mcZ_ywzmY^W-;1w1Q2g?AB>iM2DUL-wt)@~uV8|KTBr?3?30eN<hr3umSF_6Hng_kZIlW4lA^0u-VE-zt&)|tF-`#bWU2$}_~2qlsc(Z^Q<kgxnxu>L!+}kwMmvQL7zNpZ*+{=5<dh6kr%acKEVJI{8U3jU@C57J=aG0C@%bHta>4X8q%1X&)PUh%%w?#)87%79XuKeBqTZK5tpcM{B@p<mBx>P)EfIhv?Tt0NZY~kRrq)baZ+Ts^3$$W7+u9UN_nX#i#dsxn@UqTY-G@HM3Sa>~BW0LYn~?&3l8ZHF=TMKXtoO=t4(^RbUkFXiog3g*1@fF%!V54w@riS)&I?G^4Rb=K7tm-bZG$)tpK@=uF3)p}HV=mytbnIgt6x2B3)%`bXpl9`W5XyxVLad!5uu~nqXQ$G<mGVp7sTik*-5$)Vd?>l+o;`xr~cz?5*`jqBU$Tww!K^69pF%bG%#>IHri%hFvyCkJ@^Qs^|lH+NQZ>_1yRBahQInn5?6<ulCyePXdOj3wLP6r4Qa;WX<S@mLFc8#$=Sx*C8`A|5<(7XiCDRi_!Hp28_T)ZAll>Fe*eQ?;<MN>aKbWk{r>Y{6TZ<Ve4GwpNw-@)VLU3Oga89CO6G*2(UhFeCSbT{h#s6L&3b}+75oTr4{k4R&7~tL$8PkNy_?v&&wkMc>m+TtHzoyb8<~{zqW*eK`D=A;V)zUUdPy2bizV|ckRz744R*Cp8L+?*bOfM1F`6X(YB||j16~mrY3>W@GHvpsLs7DJt8#y+EL?(ls9ptjCt!-5H&%QNOYa{ZoQ<d@hXf^s@>$p!Sv&<g-Ju1cai~n9PkMqsvT(9!jLq~f!)6MQrYK%x$Wdey?83Gyi2__iJCdhnAm?T{x-_oN*o$%~LbT!XWA9%C;&rc>b(>KpS?M$u2B9%y3L5^ya;OJ^VB{DlE<jm~bzKvxcBY4wQ2uXQ=~dm!E#az4vDSe%a0f#_ZS4~4Z1uP!o^a^$T~zqJCN9|8<05Ec%46{RObzSc*SBzA%O?o%1iZ|?9WBq$-AaA^V{HBrj{D%g!hq9C<ZY9fY>^&LB&UT8W|=H|Oa%{?xobf$)klYK44n^>SdFfR8eR75(n@Q0J@8e@$60b4af7k99Ooo;wk@KXK@I^J9X>&zmjSm-IRTQ!+H1;(qNcnqdAO1hdBtzELPwJ`#<HubYH&s<IRyr_ghv8FNC|X6^M*_scRY1AI$*VJw#&|5A8|h?bLM@5{mV9t*t`f}QtcWt@=8Ur>U26qto`SIdeUM#?KkjPw1BNQATLm;rDPv}rWddlt>tUcmV5Q$jH#_pK(akCqBw4~Iy9BSaj~>-urz+@52+hRDr|yo6IN2XMOH6cfmy78PaMMMgUvu9ttpLKx#J6Qb{7IRY<<9P)?BZPKk(T%RR=LBjv`Th2g?|voP!B3Rd^OK&0<CRaX2*+1#8PCRke1EK;*WBC4BzoUq04vfBN{-hfg21alBR9=FjhbeGug*-}8*mZ{Ff$YNp%bcSqE?C<F7BMpcjR_Cd2fPCVUhP6t(*9*&c50LzcVF`Xs>whJUDJ|Jv*M}HKRAB#F<;7>F453<R514pY#={CYiIJN}yy8{@I_GqX)Q-N$S*!i_J_VrQ8lp(K)tPvQy(N+Zm(lX}aT{<a_RJxyF+)E2XSmZNEDPDcW(ExB8<eHbQK<OaAJnR|V5jbV67djSI#zf2lFD|j%D-o(8GAv+>-M89y4fd>TtcA$OsjTDZi{-=J2A>zczMjnrg}zo18lBDH?iG65*fnx~aigxa8H;jdON9tx?kbN%`!)!5P_p*ZYekEw@F8PSLzs>f|FYoVyiYFE!80S7z%>;m%nr^5U|45&SHQEL(evq{o5iVV4zZ7Oh+|PVO?D1XM^QNdbxhOKA$l_FYi}RMZD8u*e3s#fHJ$9T(E18*gv7#IBqUe62Ut;tZ3Q&)PV}_uVi~h6TXHO_vq{hs6F%&_&cOZw#V{yX0g%eLPin~R6Hqo94iIemIwqwUiFc#azx;HXE&Ei*!;-;7IF0saCLk*j=qd7uWvO_LMe$l&g)=qwNPdT>Qc6&J;&7V(O(Rid$#|lQ*M*}PYHgOiimGO3sUiwX)VV%z7N+G;Sum`AWio8lxL5_3AJuJ>Sz9Jkqg<ZgIXG9tz<NG46#mv!Cq^F35el3!ca0^%3Ca=^)-~(Gw!!v!&RJr3F@uiLYLfB#JhaqDrV2<!y+?z($Zhart}>Eju{bX&S<?}SI{^#w`{E!rqF-G_P2E67oRarIt*b_5VXHb}-<NEu^?p7lir;O*l&SMnnR<w`@utt)L=Kd^UnxL{^aYwLYqML}FX8hE)f&jL0fb=Vo-<A8?!&pIXz9*O35vBzc8=$+waydx3aZor5UNOlLuM9<@&b`G;sA`|K^aHrdGO1DeN%^cVUWzR)HE4kcwhA~XFJ?~@EMv!y<W!qeMA`v-rqydvwuSqjeocLI4){)&(oqD9`NboHifL@*^x?dHo-YrNlb=YFLPrCprAb(Rkqt?o^RysaEF{9FwZ{Mys2H~UU0C!ZtdM$Dk|y;jj&)Fy@}b*_@j>MTWv+l=@ocT_pR`tMZwrY>uk;dLh(1efU0;z{cV(;VWVOe3Wad(2+G9Z)87U?9Fl0L9kwW2LfbIuPJ81r`U8ziCj)r~Th$=CM8J3_u_<D>BLSWec8U<GBg*U{uK8TvQWVM8c^|F{3kYy<5jghp3Ki_JD2`Xj9xkMUg-9$-Y)L-?X0{{(vtWe*D$JeGR3bIpAZw~k2?HGBtz;^MmWPwv7W*D3D(O901%*2Bu2od3oIj)bA*>32CZ|*#2*8aYxm&h2Sqyrus?tvAJl6aKrOD>^p1<fDgPl!lrdBRZQWACD<a&u1u4}G*ErLW5;pY-cIH1;em;4O@ODy*1Ftr_5TIWlhZZVJyR)4moDp@<Xt5Pz!HuU8QZZKI9?<gy<#Zp8u5YI<<R#5^Es0MKl0h&LlnIb2G6>)ThbuJ08AB+i|Igxjj7r2?339QZPJONq|SU2BvlD#`<Z>biRdjpUWZS+YN&x4J?i~X;0k4dvZXK=UGq?eRl%T$!nqgpexfkt&9rkc`Plpl6GGGuK!sg{vyP>=u4kSgPaeN9FhvA0PnDB00>Pm05RTNvnlUY&}2JuOSBX>ml%r9LdWTzt#u*I|aZIJptbjp3kOr2rUntN!B_7EJxz9M{`jiYbAWb|;jjLQ`)Sxrbz6^Z|8%Sn8F&RP<Cdmrldi^|Ag9Q0%E+ZTc88W0S_%d^**fQHts_xH^7PvSBq;ZAHg8Ee)bbvc`fZ*|VC0E-}a!335{GIxd5ml3lDRBO>Lk9MIx3<yB$F-fh-Ht~OV+wga@1=Dt7M07pM?NvPDzN5N<=(NHs41cYJ{WS8-7S)+-7SFjCOIY$h35NVo#WnqfVfyHfy{ryHfUbBr@yxw2=#jmS9YScu%z-xQ++yQ)>z?!ginhdp5FtN0v3C~Wl;+*y$tYYtjqU+ENG(q$!S(wf>+7k2*0`oA6b#P*ieWD8m--%XZR<E~VP`fnA@^R>w1CtL!F76am=e=7`HtiD_?IbYkwrKU0cA++46jQTl*Ohsh{v#sNs&8*6A@N2Jq}i^Jy>pwk5FA*DOzG*AlRAHfedMZW9MuiRF}GVOO_+XCK6{dN;8)Tm!j?~<?MYL`x>K_L`%20tx%LJtLzWv^)=sWf96SI?x%VkgQYa4M$3v=Gl&dOe^q9=Gk7w2$t9(5Gb^F8bh>pTE9n@TVia)2<06|le&>A>9CHfP?(2F~8NlToj(QTeiL&JPuS?ezh&G>B^Dw}{R8{#KncdJMbct2?;m5SHwpE$~56o`-~USD6+xdHFHeeLcxkmjsT(9+hVYnm2Ub|O%^brXVww}Ip2uj^vi3C&$hYnuQCk06z#O!aJmk3wtt;t9=030Z?OJHxsxuBBF;ndYv6dwh3h*fvRkGNsiSS|&77n0s5g%<3hah>MiSp^G~1m%}``a!g7K{Sk@50X0SGc~^DvEXG&JGO;iRTy31I<X1UOMOn8*{5?!Upm^#w;aTKX<*#X0*E$1yZ%2WK?^yf<vv8RTYkn>~I|c7!=Es6Na2^}QhH2k1OIdFBG!!lbYVpkkM*wV^0H-Vp!9ncSqU^z1@Fi&H3HAl#4Zcq?(Ko$`dSR+9%Dx`Y;p##*e^EsqZw-a$sB1{{dm&gM#Yb{ST~TfB>?S-ffh#hnB2)yZchq@k+);umNi@5e_yyJa+=y}-#JcUJF~JaQ(mNBGK9jS`?w#5wsr5|<I(($H-OS}v<+agVgqSN8A^1jor?NCXsH=rwFhzDOeYQR%aT;Hy(6hM}D?67h?(T$xppG|IGo!qf5ME+v%~`q(l&Dmz3`J$9JWzFkusyH8__}P;<zX5_O>IX5@2o0mhlW7m&t&sCnq(vRB^bNp%L_jP%JxA^N%n3C(iqE-C_)4ezO~JtaPKKtABRuN=$KAZIRcYK1dJr)|K_GL`Ibbf?x_b96#}-@Yk=J`+ozETbbZnL=N6o6BJ;mJ5W#a_&W_2|L88?soA~7HnMWD(W$|swhIq(PMY$%t<X{`{s?x`*7Yv?7UH2dp<mMq88_IfWJDcG7=;itmYL#y)dFzq3Pozs&QJEUqzAV_{k^R(>sEb%Xy1Z;oy<5^JZ#GYipXf9`EK%r=u0zU43h1-G#EG3Bv9@(lr%o*>yht^8@SufQk*sW+r*Lgim@dvIXz)e9*ouw%U=3G?Ql+V<?%Zah^fOBALC*<I$&=P7ZbsLKTF<s<vYpkD``?sZa!c;2v~|c!g#Nv*nrAGztI^uXIY=yu>tlw*Mt9cLZcCi(iYb^{wW(`e$c|1edS{NOKc9GfuPv%Of@966&L_MgFo`MYa|FxlFi^EdOU*RKtonWay<g2l<>D-T6~TQ=b`zM3!go4&7Pb%t?N@NRZo?gY{SV)>AzBQ&LtId@7yw)IY03zjQ!{A<xOnq{>m?Hh%w<3H@^*)ZupQU)5|@xS30D1V-+)XOAgRMH(&%w5*?d}jooNx?GF5C}h}~p$Fn--`I=8(n<N7N^a!U76YRK17R=qZeK(YUZy&1Zb|J0a+o6+EAF*S^&{n>OmQc=BeysjNE5{M+N{n4vn9{hZMCpC5P$VlpUA!ZT#gPl?T&8b6ZcL4<{E@3abzp<z1i_HpULCT>7j#+4)EL@rPVH=nGHQo_s|I->jYN2l4mU>QHHTw_NSV~h_&LK^NJ<dOISa0r<t;z)o@US;9eTwsK>ED=Km8zcro4xFPMkn@!OqMy6tEaYbb%c_FHoSAUN&)|~x?<}M(?pf_S#b8|>rZ}@;kZ`*O*V?Y%I-+^(cE{3T~kF;6IW8kJ#t9MQ?P|dBbd3DRqk;jPo5wgBV`>3oja>im~?fd=6-0UnG2mOv)5|caf;?KzOLwTehC?D?k6|*!~qAtJ!hsGa()F`Mn#L}er{0z0{$D-<mS@jCcv1Q)!EmCxfq;QQ$)S=j*rh{$v4Vw?PkaySBT2Eb)j>iGe;x?L~4;~X3znf8uvR;Qi#IYk^wv&g*Hk|LP_e{&xJx9a63(fE&!%wu9zIHVIF$d&T}0@q^U#9#KL*x+-_zx*s`hA+h7R`FiHdF0p>F{3imN}GYYw}x!a1o_mFg(#^g8bHC3W{p$<W0d^?$&WWanp%@42zvCE^nKGZ(2ouAX9GieOeFlqUxsb=*k_&g7Ztbyl5nV_GU9oSh3;z_Kw3=wNMt0H15{pW#yk4-9PDMY6(u-tCpiW;%-v3(3A)#w}wn=VClqJD9*rKuGxQXG4m+raQHNZ))0)Ve-8Ln!YlJ=+z3CYfT8vU&7GtDQS)GgO~FRf$<mV{GW4hVN&Y>R|_umnc5)xTeOv%r>Ooc_t{fz5Mzq#ez$2=~R=8xsdHcIC&*RNJT3hZCOU*uASmhk{CQd?Y`@1SJYUgwXJ#fJgSSm0ANg<CV0!>PW8c`GJ@h0qOgE+;kRe#?8|Sw|IY-+ZcQFJBBSLCm=1=lwxtoE&vxt<dI3dZ2JfF7jTYMbet%z-vt+YfFZqT5c5_?HB^jazTc1w-Bc=E5pS{7t1_&$5k_KDoefL(LmFQ2WVuw}TvxzQ53YENt)+e+mU*F!QJhX_*!;TW$l)vud{fEKHD%8jbJZVhott7T?vz(fgCvUBZ>N}u*ar-d*DjO6*7DMNMU+-<MK8Wu0`)E^zyd?#Pa-_@gmLRnZ!@!UKb3vZt8{3t6@s}u}j$fx3H@M>5o$@Wz>OnJt(#?WzFStIKD7OHTEfw4Rsq*4naOk#SsOl`G&c>)f5GW*azVG9ms8dZT^<shceKYMVvb3v;+#9PshtAva5xjd$LpL~#@yYe@%b#ca`TNE%U)7DG-^ue2A5JEB<CGN8?Ip25``6Y^+6TCbZBg4b;4IhwX62^3>7=Ql4~8^L?x!LiYb7Gm)2F&P%4*inVdM9=`{l#WKm7FJtKELQK70mWJKJT_O}*PF@XNObCs6GU74Ou@Bbd`RAnC*X>9-$#{Qe)Gf8o<_fgn3PIO;z`er=D8W^~W3>XZr<n<6<|v$V0Bq(aj+g8i{knBw+Uy-3A7ZmPYTRR27tl0#6a2L~fT0NAZ-9_?~LCD%*z6nQdg8_BF6Aet~y;f3XlVfXaM@AcR3>{o6#P{7=_MZ1yBw7cOeui5SQRG-3(D7(H%aU5|w=YRd{<?^@tVw_L8tKY}dviO_U)9TKh%eF9T2y-nAyFy!$sFyQ`qt0YVX{)XPscd0!)rqhU0n7?WFvPJ<I{z`BgRZ_bApm`emUxc5oi}={ohMgVSe1gl?@2Ag;>6PE#5>QB6HmAbXdQvW^vL5ue-hyWa^!<Nx6aDrL)o%hHNb7brOhM>7I69fMt{*hs85SyN^YgJ4X8Ef&VGMg-h(Y<eHC6xBmvfyf`q25S-riex{l9)V)ZnI%e{0Bi^!gBuy%f0u*=8|@-by8_uKCeb}2+H?tgofO!L5wk1`K(Y;j_lyf@zkiM}0Z^DYX~se|6yghCsOcMo{nv%hdk1{nM<WMct%jyzcvbk<8nLh?FxDzjZ+iI#={6GTEhsEaX6bZISX`>L=^7sXKHhg1mRS&}_<&dL^SBBR{K)4f3Kn$a)9AMSrIY`6$xSEHEADkT~+^(YPP&iC<->YAyeGGMPxO$m5PMqzgyf1yJyce`!Bj{W_6dp{#G^I95N<sh=xAjEcOiD5{zI;0kL>zP*cjZQpdhMO>6iXX5M8f{ZpZ0<_o3BNB~&KI^cOsi*j8|&(JuJX!8*g6I}w*BekwwyBfqpAYL&R}dS)StQ+^^+>xWRp-zgp)FEXRo!*06NB1n-UIlNLdHV{-)<LxJD~IXThjLw4#>9AJZ02`Q!d%G7G<rb^1p3t`h~AO$&0a+el}-DN<c_OI%`8<$|xGY6n_tpE1!&#sCeERn^r~u-&M@W^@?jwneTnrwzH}+cW3VwY`=HW2K59+#ssoGLG*%m3*ngt*iBrrJOE~g!)cpWXujoaD22+0|}*{i3xo-9PHknTtXE-_TA|AR<GcAYuzL&;QF_Hp^b%xHGYGL+aKt-4|Jxn#PB-==Y4lhGPuS7T{dJt9Fe^`ZBq_-(E&1(ovhQk^-hUX0f{TNTirJ1NE|azC5$eO=#njDpPu<<W3CCMt=vhYAE#N+n^@Xj<wj(L&0jgf7GSM=*QcVrdcluBUc}GOukvKox~7<axAh)e3Ipqx$hg%-RW(@Lv5m`+kXPfHZ0!+xp|}J>TffZ(A0wmugeQa&VW7L2wn2?S(ah?d^Yj_d_&gP(Z4}E<^OGV)N;80VujgC{iDDG-L$4C}etT7t-ntUyR4wFM40$;Dxnb~3zz`fBLYQC;&3Wj2%?YB@W!_q0Og7l0G{38~w{+q4IW)4>=w&Th-5NktU~Y}PHO3_*Tw73j<jbRr%|1-|;wXB+dV(iL_xe2+9wZCxDOMs@XXK}dZxZjOvq_Jy9t)TCHj@V-0y!*Aov$h--l}PD9ju3<B+@*m{VA_*V%#J(IR99$S)s1;d!)&W2zTsU+BbRONd}@vgvZq9spz>ur2quu!rhOzaX3PvcV98Gc))$`$I)&Ta%5<z_n#>!u#I!dsQg>5YYxYSD*N$p=S0D>a=N3>;v(9x?<yGO+2w#M?RUnm2EydjcLU>G^5dkQHY+J+8J~oYJ+5{v07j!U!(||MW6fNC{P^=mM=2fzCbsOKf1kyKp}YIHLP{O@Z7QvY{s6sq{{=+KvI<bQuj_aCd+Lma0o6db!W;SvqLQZ6RE_BnB2p)65&B7z9w-%^KWyS0uv%wh%JYF4=edBAo6nn=NzcDtjA~sEE(VUfrm>|fRj48L^s&0I7Hu0@TP2epu=jL7Wt!8x5B1L<KmH99_wn8*&1q3NohYMXv1oZJ&-PQJ9Okf47IoRJO;p1vlhKT(HWM~x?&I0JE6HV;7N3$ziakI*ex2>(J+#FH4UN!VoCqochP|W8y0qBDRNpFb8PeMPcvkbtEzJkIoxu2zRypVijZ_*~s*FrPG4|`!EEBzA`y4NPP1dP(2)3aP2l^AIUL*@_gOZKv&Rq62AM>4tpByrj=Nu09<b8~m1L|0>9H7}RuR@NtgPXhpp;D!8?@}<^lxBU?#65}v!HJMMO7SA#{Q`$EO7hKiOwIufK<}+UemTDcjd%CE=Ed%1NLVo71VteKD@fn-O78YqvA<=pp(xra{;s8)v6iWw4ZgUP(vUZVq`JGU0_)(CZ5wHk=k7=)_@NyY1E47rJ@@tu>^-h5nC8@UF%6r|;9DAijdL4E8to;MX$xhx)s%gdor6HC4xnxwU96L*7qE?b^1B+TD>cB$qOjR1m3EPU^K6%zajjf1x|#ss@)GRPpPO1s8NtcbYyk`Yls=1X+>0+vOxOpSUr#F5d1Bed0F3>;`Z;dK24lC5dR%suNnv1xJPG%lC2Nst*3tV1StzGsZR770bp(+V9iR)0Ol|I1_s9+Om)`aNDapX^&~dbZJDJMhH)sN}SzOn}u8=y9$82Zx+X^5n0$lynoz^J&(Jxbj&4Y2X8%^!`;z5DMP4pOHi+i=i*j*ql9IfAO#OpiK^l^t%vU8P|<&P!_Eo-uFXHvuu+Q20IAgzPNFx;O1U01tGQ3(ygPDz|=l4=bR9tT5FOL(Zm^Sgrm>x^XRh880^$j!=QlG|WMG1%IX0ZumuH4?g=Lzhuv0YgG{374QluanUmy1B8A1QsEL@kGYojmO%gvgktw^vTPT<e^hYDbt1)Y&KHW5HD9ltssa~L>JRg#liG_hTe!*Oet9I><2yYJZ(37Hl4bE7+*E9*I1mK#*(ov(NGj0vdff#__X>Ybf;^BE-D5YvX9kVNDvO$2Npbn8f2xK_YHkx-A8Q#%4NB@l?%e9A@)Dz!(BTr#}Ct>m)N79^U6@(=A>QXOPvQ``e#>6hnE3!woNUW5#4p!(nY@vymEeOBta=@#H+a4;yDQ>xfK#vt6J0>dggawos>aM&Bg6+g11OfYnYRDvVh?l%`jH3e}z5LO@VSFF*V2P>AsC!@oPAjEKzta0T+5~x}8#oVYDa2&hAj96}|}F;9+WzvrQsFAvOet6X>%<N;2OZ^%({kR&hx@7|1hC#B}S?$F*6R;DptzaGUjF%6&Yz$@FfeJRVWz)99ZMO?Vx`FrdGTi&mc3Whnl!YR%SohKwg0xJiX|wDnO%6Td$JsU1rvqZlgy*QOme=rag;E%jkEmg+LwVkLzcDs%$0po4%+ox1)IcIeu_Ya98X;C-@e55od6UZN_C2JU1Q!#;~q9lgNJ{ZU!PvQe~MRA@%FfesF%TZ{m;P*1ejCmp4zza2p%c8DcaP@<q<K@;#LMOUx9GwyL)B`a-XoB;Gm#7{)ng>lukL9QvwRZZTw`<+2#r&FVyLI;e3?7(cK-w|?323=LjBzfw!qMU~;F$k=4pGV?p#OJq9%mvfakh0W7Qo~S5!LC9WxJ+ZC@q)mKdS3>$3XD#bK;W~Iv`+D>wE!$>Z>-sMb4gbat}_+)A+2sb2d$VSuL6;LE1<*^fYZ_{Ls7~Haun)5^f^`l3-B2!!?fCr6!4Q=r8+x@dURz)U6ylj@3Q_vXkzZ%0Jl;T;=B@GfZ=Hjol|vQK&y9{6a5JQjiwTQisSGp_h#$zJjZDBaH!iHcv^MQ;?uUEec=PeoM9dtMhQeO0I!H>@zx$47}+E*hr7QZMyJS5(v1jH4`AGLM%(A%)PI~!!oy){Bx{||ws#A>0~{)lZceVp#%^O#^*zj%pfz4^tDu9li>hB_g*S(yhL09WTpe;s&gx+$yQ9<jKKi2c&Py{EPvhbm3)J9nI62!`yF|4BMMB6Sosy}wJFD%+a_%*V_PDm+|L~XiEOrc>u*_V)zo?mGgm1J7AE!fD((P7H7>@)4UkL_Yl*|c3Yf*GFdJtRiQBfubSx<1Uf*%3y!R^KOzkK{#ppCgL-e^jIOl;j}zi8u1RBbKy#-yNaBRi{+QGdOr{I$9^F?<FFy(EpJ#gcgzsJ8A16gjW<DFYT5f{sM)EVd)}+Fwq#)__+8R&Tl*L~m&}SB|@b#KgzS!X=o8YSL8iHoICMA+Xs8()))8XCrD&CqYS}d=_>_7EggrcW6Oq94ZsW9Cd9`y{8vW7LBo){$<!q0n!x3YYaJ(8mFc>Ek`nn{!P-6JT(J3H^Z52)yaFtUX()-q79dvd;g+Xh0%)PmrSx!W|whj%$S0P|FHNiXTf4<;azp&0+hvA*EJzyXnI(QCNym;y`Ee(|3tW|Qml304cx)dPg}dhI$O<si6<Pod`jehSQ8g)?Qsz_G37D%4K{~$@atQ+ujLa2cmiH#-;S1N=+^BmO-!Ca2aMxBxUVqav=VvSBqm#=hZD(ZA%j^a>-HKNxw{rLmVb2k#?bj7iPh+8sL^G=F0Hh7*8^Xbe4Hh>L1ol4oRieqwuov5IRqhB4`%haci@&OCqU9zdrkRJ)RfmH4_7iGulS8t=xB1rShkZ_om~kfr@)|=@JJvCDS-}X-tdiJrsJuz(E*0pGAX50XnG*xeop4h`vm)!Z5Xk65x}Hcz-Q!@ie%O4bc$H}&;RtK#dO+l;PIqdMe+iLTC4Z*XL<o^(OSM1ZMj!3POgb10m=5nh~l`_^4nAj$HmgV!P5ApKcsFPsjw-<;;53+EwXyq3e0Z*D|yJ_^TB2yk)GT}t=#d2IJ*l0)wLh6n>8(K{YO3frs^OD#Ze^c-CNJ=wmf2#b1>nh3eN(jS=<V4)Xh9?%OzE{c8oyewuB{o{^nmk)^C6M_|u0^AGLA3Rodpy?|yv{<tN|sjL&c0;$&*3+v0ae)VL@E^Oi<ckMH(Dvf^ZyJxq6-(?OM{hvVcM!1Cj8Os7eJ?E=Y(4+xvy(H}+S$D$4y_|r`NgKToQIgsKWjzw)U>zI29+puBUqoMLl1+u|l=hxQQlU8k6NhZbV7zd+q4F;tBMjCX<Efpm&?xlqxEb<wo6pu9rju&^$%T}OtkY6754DJY=GS&+niz;IxW`P%%ST1W@PGnfX7`tz^?HcS^*;osak5gI4(HG0Vs;-)%TJ_nig674#2#wBWaQ6zmZR{F3zqnD?+KffHvZX@A`m8#mGQcZ)?Wfm@7E$3t#-fHW9Vz~0!NGZ-+?)`e%Sa}0O+^W_i>|BN;Lq-^fM-3U=hH(si&N7aVjt%a$D(eU>>QqsqH+N0n5L&g^kml8-ad@mz|_O}EW;CPI@x8R^%dR-iG{aFNUnAdu%Zmx3TWh==xNo(GG<w}<XBW^lb|OieAsuLf&BxDVNkFFAeC{S)R5aJplmc8AlUSEOiD2l??$PA`RO!U_Nk7CC4-%whSc`z7et_^$Rn1e;x!h<Yi$+IWC6hSi+6Y`r3AGn4yXCwG!j*oj3=siT{w!N)@IqOsA_hWDx$D}_laE8I4y_Df?@S5lVPjI#VWY`sBW9g+A^6M<?;m2!MPd+*7K>M@VBNqG4f!JP~eQYYb*&)P?ngmu2~nh4Ytp7&Jx3m8FY+RlZ@Brp`|`DRX{50JsQ+SZi63lm60Ti#d%4|nvOu+30RQd7YDHs{pu=e>IO36l)MLOT{S8TTh$5szGO?S_wzYX{B9GbOr597)I*$&xpl)nkpm^~R|*g!eSzl6+UyqgOZa?3wFYu*03q18=S&m2`*3b4TDmh+f?{owo#VM{t@8xFf+}?Ygep?tkeNlIyg($4H~^z~P{t8@9{h4(-_#*q7$kEnHBCks-dBCh*$(#~e1;}bub1(DA5lhv_xI5A?BCEt<KL}5j*Hsd^Ry_32YmXtO(83JcBE3AO>j<D5|iQ9%iNd&C}@vHmF+f}=NoxD+#%-&%(KrmZ)#V$7aXjwTYLAGii&zdBP`fPZ(_DH{-~q+R$I|>dIcWTeJea@Q82d9I-4_qQ2Y%qpei0we;Z|I*r=F=LLpo`f-*7q^tV9|ha?(mhb_vM&^AoE)84p@{y^i>$v~dLRyBw&5is6KY>F7}NPs7Vogzf)h%$SKYd)8^6h-oN-iNEg0s<Ud1dhGDLIry)isMzXhYP7-AreayThfn!nJtOHELdTH3Uenkl}HUY$eL<X!T^VOE13$R<>4f^#l8oMN_tOLL7@)3YZa9$=g+8q2&=-M$thI_0&rtU?v|}h7K2`^s<ab2k2OC*X|nmf=P&xkU}w{ssg+BUltf)Oxn3fM>zXTHiy%=%__>4<4yZNWC4WP}5{vygOl`-N*7;JWTMQ(F)t_ytO4iQps+0__4Sjin8%$QjJIV@du@q4Z#PiXeRg}O3szKaCfaXtXrpSq4MI2pWol64j2V+8KPUKzX1#V_$0&BB6Pk<H#*3CDaWbY2zTdIZS-T-7o8-0?+^I#+JV*hL0W72HU8Qg6(=_RGtG8JX?sMZW^piy0jsiw3R<%ivl3|X5_s%4}a)Z@Q1q{?_<Uz3qW>}^sCN_O<!lj3mS76y8sSEu4$Ps@^OS{xB`sSk@T7vD1ab(kS8PHqHqV>oD6DFDXYs{go!1yesa$MtrXVoG48-3eu>(A3*S?jac%eLx)`mU^Wx6+IQrrPJ_reXM^26npAdn?8oj*rYKwpH4Mrl%o0!u8yCSY*-CdThTF2OM@tqtg+xp_N=C$OAN9_f}9k)j>}-CWEX47h)8)W2ekN1c~#i4cboN)tIZXy?EtN$x$n<5z|jv}5-RobQ81cIG}KHM0ijp~*=4+2)@UN&6>I}m&JlwhM4BdGS(svTU~$`Ff4>or*K8veulHAe@#|`j8Z}Wb@Y>!ycL3ieuqJGsCPVEMOf0Qv!n2dCIH&ywtJwRX=sI)*O%Q!b7N&EJwgkO{z&wm%9h{hBpXfrtccRsp)$45-)Gkf3d>s1az~sY_i#r9?dGFSfP5T5!I|<CXEn0o0U8oHh#nf!tb!A?r|A>gR>f75%NW9SlX|^k5@7$&>1P2x(Q+hh(q|TpVAGs<TM|Fd7%<Wc66Q-Y(&z@u*_?2{tu;mkId(u>~?v$+mzLK&@uD!v^kmW{}wUcWV2M<6}?tRLW6pDlR@sO$(<*EuAJtlMQ<C%5GDqjyk-Tv@9qN6ZP2Q}B8;?L<dK+x1Av<A*jiT=be^x_U&(h{d>bepHs&@kUu*7^%WGk%+f$|j)7hWJU?-73-p-cQ;|rQ$XFCyufh1tR2$*Vor{ZovC)U%R^vq&ce-w6rzpnx@5-od}d}-Gm_FZQwZh>$(_rLUR|>+9p83BS<AFQ$1VYqtIHuctW#LLe`+n&af_vYpGRdrnzh29^aiAwoMYCOlft7mI;j%=H8Yrvw8_9;vyw-=%SAM<uDJf9Fx*Qe?($%KuuA4-c_AEi}4k*Of1X+R~zRl`BhF+QPwRHe-D!oD4x1acow-;`D>chwax(F+fkt5I~G5|EL^6-nx6~LPQm+_`LW;*oX1A7VcK`hQkL624TTGVT6{CX5dfPez$uGDa1gt-D0{FLd<oilf_(vbgYQ#J^i6M~UYKf&vaiQ;xVn(dUsRFDTSFl_>KYRLUI<o5@sZq7S5%ujy9v)r;EK$t2o(Y99d#ZWca)$?63uQVenGW9H=>*dv2J^5OfUqS^v*=4&*ZGKd#5%^YJJmz4j*Z4H*@(^d2KWoA?8X&2)+^DsVq$o>S`evOpzT+pREr`oW_?a^lWa$%FbnryF1|^sN;>*%qVXqgqIjvbCxaxB`Vb_Ls8i&4^&+sY|ra2zAl?|d6>pfQ`^zNJF80Cp&?NCGueEOCfNvn3C1q@^1{!6vVG7}lD!*(G{!O{iV(qrZ*B7@+<OYv$Klg5I;PW9j=*FQ0V4_dzqzSQz9mtrd+Gs2g@7&f8en(K_Gu&nU0?M6xdrE%$oy{)MDW~~vtx2~kZASECO$cP=26CcS$vzaAs%v6QLYIuIoJlgs`Rny1%qc%*FDGtxp~OOhO(a8&L((1dbxgtTIHKc-g>0%6X_CGRHjC@FAKJKWIuHz>LS*UE-#x?@0Rq*o6QsBCpwJ}OBA}J>yYx10{W~kabo93tZiM?sZ$FIFH#L2JZK?SBrDtIDO_6=ri=3l8hp_&wqm0`Si{w!RB7s|JGa>={frWO&~rjl@}xD2o6+^5*0U{|Y-e@k{x@Zp+>*O0Z5{Fwp?|Nd<{3-wYP2?T4ibyv`j{cH(Vca*+Y%?cVhW~KZR%PVvZGUr-kIa+&nF(=Ym4fR;8^pi^9ipAOkzs<9KrHB3{<VrQZtP)tA3w<?^iQXxj0K-MR4De-2~>M@SP5xg)Kxu`xTt7+i*u;|HJoeh!%tH5Eqmz2Ef*Qnli%X)Jz%yF5Z0Lddb8AbJ-8Qyxrj;Y{&Jy#3kfSf>l4;Hz1P*Nb0bQG<sZ1HlG$>XIg}}OcmP~VmDbGj9<5#&TTKtxc&-}oYH-i8uE3NRj&;qQ0%{9Z-(yVKQ-pyW;D22ObsJxe>Po?R8(&quWJX41R_amfAlJt2S1<RNljfmGLrgTh*`w`U}w~SbLtS<T|hyKOW4cqZ|v#$VzWY7ka8%2V-}hx3s<In*v934jdz6E|Fp)BTBw`1rJfU4&HjTmmeN#~b4U|mkMmC))|<Ozt8#$?JnRijpW=L5`Zp$5rRpcZW-oi6(TP1FlVuL&>ZvVU9igP44e#8oQo#SLuGo6RG*P8}7M#8L`jg*eIIfj{lZ~RUvOAJ}H22+M*Hn?z#FdnBj~o*66l@{V2xjhOm3y4XlP3trNLdF$=gz7WCS4t=xgT0-=0fMn?6sP9oT7P*uPb_-UqS|(`^n8calpZE&zY%)oL_;KQPHBgpBvP_fd57{xw-VX2{5K+b@nx3E(WL76j3j|<Ky#K@{O`vyBYGw6{0e3UFcls%n``|ky>P$8Fav=#{CYI6rympWB^Y`p^XxgP?Ea#bD<Ci+)h)W3xH{vD<(&4n1|lA^IXReY3dL&v2Y$ax0@Lawrnc(Hdw*}jM9L4fccD#!hKBLj6!Z~?zSTDJtW<xG5HO9O_gX~s6!AL-%jQx889DD^8;)_?DD9t548_$=jXKOOd10<Oj`bFs#!e>KF>oUYv4IiCg^8o2X<D1coM5EL&O@+s)(3M|9RlwW0T5R3el+xEVo;@qDCxyY##$jH9CjFrb|(ss9&6HX=(+F6vy7?HZZ&k(l?(0wXToO5XyT>&vwP1Nv0U2Y#u$)YUhsH4Ao~(Rbp1t7#ljM;rm&pdf36^C5jI`uBmY^vkmEYo(YO=FTZ|DvEY(hI@RQ2E@b-<PF@KSQqf9BTb7ZyYo~aWBnA&qyYD*M6*X3AZEK!AkLqGC02mXe3EnceQ+@EKjG*|0C@i2{`0W`w`|=y_|1-g{Ta!nQ$Y}Wjrh_4?ZD|DPvmLvIUO<tU!TTpiqlNaq-`^MIEZJ<=OTHn1-Q3o4Nrvdb)~8edNa?-%XK%2u0m90%q`?+?-@TP*CHm8;*kM)oY@!R1LM3mZ^$9J?*SEJR4=v*Iu%pB_<*)mA|6y>l3N<nUPa2bYD~YY!ET<;r$y;lp`VOdH+&&Dy$_7P{#nAcR*L$0*528E$KH5|vZ%M(S9O-hrB}gs9F!1C5T#)DZ#&%_1{3S}L<JT$14X!wMr+f>wdeDrZbhF^w3$70)$}NCoOT{*Ss=PQC9J*~7sya)lvoR_V1PY0q@B4Ts>Qqxoy;z`q-%R_8EbXcy_r_|^q4Rcp1n(Zx&<ze_d~!Yf^5@xp{=VtUS9PQ4ck=whhm*<OI3)#idr2(N{<XD}_5rS9Thw+9ILr0FS-GihI%#U?gCWh5`>BY>T8W7C^r<e6vYPdC*!cbJe);h84?lhQYPTP+51+x;&UTq}Q|~qk{PL~A2~@j7#XB|f2<Eg6NcwPp`t64wzyHVQU-<M}Ajl36j{47#U)v+28QpWMI;BFzrby1#EN$#2snE2IV1H~BrntRTFH-T2n`-YS)jyA^<Pa3<!NEun0Cww|N4s25$@LOFMV^e>Ml$OMh$c)_cwsqX*ggI6d;Rr0`<2@b6fn1K(Qafj?QZzWYj*oR)u%8c%C2ux97o*F`CtEfx%}<E80S;&>i6-qEdHkTw7PTWvMr1n!dwf(uFzH_>gCMgs52Q-+Nvu+DqC1wbt0@o0J8!T3~_9e&VS73psO!U2tZ$=C7vU1=Zzj~=gAcoR;8ftds54=II%Q3@y;{k#1pOpT1Vh8J@R<apG3HT9Qh#6t+Vp@P`2z=4RBj<X){TJMHuP61GM|-{nmfc&Zy6iW7=+|*bS&Y=+1t}UEY-~<bf4_OC$=`l@f)f&{@6VsNRmxiDDHtg%iGX4U5R0ZLoHJqOi*d5b`l)N%-6E4|Z`xE%$$WluQM|j+inJa%^#Hncz3y1&K}`X!9-#<f+5p+Jr(Ii+2xr+_S%MN*EaYF63tcz>Yjw6^7PJMS}D?nkw^OV2PH7kQ2m4Jj{zxOyor@Yx}CO+!sYv<A+p8<5?m;br#E(a3Z7J#?!q({+bao!XNH`FSNJ_Y*(Ya%PKA!G8HNf4bb=Tj_R7J<1}EePL&CGN=B)79g(3!EqA+Zzm6k-d&55?R`Z%1Sp_1p`yfPnXNhV^{5m8Xb?ced_>E44WCoxxf{Guo5iD&}SZp>+;R(MlT+SD^R86aAcpK~L_OkK{N!U6D%C`OK|6}f3mRw1WTz}{+n2*TEvS+$%MrM+ZY^G&g-v9rL+ufDPA|v1cJd!1iSue_}>yYt|a5w<Jxkac9Myb+-*g1`3gvQ(OrV3NlGufn=5-X+5vvbsLX8<qbK2C`Tb4X$b!~R3}WpWp-d^rn_9U>a_4E~&6;gnJCcP2CNM_bD`t#_R|!2DW}g*{rj*kzJhAuf3mo4yx(6jg!H)(wr>STas%c&w^ApMw8JEjOdXAh#`Yr8;fMC10>Pm%tshVHguHf^dWQfXg_398@}{4Y%&rBuj%`90`qs%F&oLkzo61<pvT;zfu*(VY*n)JvoFbd>n__t+w6(^wzjZRKR`Tj+I*$YS#P>5x3va`E2NtH`qOQ`uH{{S{l5MgG`{nC>_K_HrL(bggR;Kv0?=hDrlSkC5CEF3y%iuZjtuLnegTKXcH5DQ^uQHXx%Pl<j49tb3TqkUvgMR)8CF5jpLZN6{N-KVK8e{KNu@3C9>YY#SbE^_MHp@=kNtQ&g$@Jp{zvVY-*Ru2C2wqUA5bw6V76_qlJs@E6kS)wJnNF_%>-67(YG7HRD6=Ekc&nOciYyN4t)2doJgyRny@Pr(M?$7H2eJ@R1(~qxQ35l~s_xW2ij^U7Wg2gRNBL6}EvDP&+ba!Rm9NRfa!s8?X>tx<m5BUZxt{SQ+?`O%cBE#U?>9Q9Hy*9DAH*djaHki?=qzn0J!Jdl+HUBLqYd6KKuSL7Zp;v!0b0wrKSYN;7dKtxDD#P-_31FiS1SZ%4qB8$sCCa<)}oA&-^a6Wcm-JKz50iRLP3od=gnO@8of_-JVQ(xx#_@6I*qLNE=n;`4r(rz^yC_a{ccjzZdbzVu9Xe?s;2Op*T4&XRG?=OjA*vNWuV>mU;}cS(qVmHAclw^*1O)-naHTwPwZ@>6GwWnlJAuR+kxE#FT1Y-TcDmNQADhvwaWFo4!5A8zU3`rw^>{PpMG4?;&Z5ttfs{{3e!DnVxZsgRTgzMI<Bp?`pW_w@}3FttRT$H$E)fLsQ{guiJBcTGe8f?%Qw3pBbzs62xLc*|(R(+I-ilT986Oh0UNdAZQzJey9k+j(Iy8H=`q(TwZG!N7rQnR_Zdg}zKLf7Xgs(YBF#rE09rdd_3X6nyz?>VN+H`43Ee$9ta?d_@v9Ax(lz^Waoo>{+8M;81*uD%ZA4RFWabVnCVgGGT4zZ#;W<CD{OF^GTgVE&(*|6>=l%Qi~26zMG>s5ft|v)?=!*UhxuBwV=dhNcHY<ua=uDcL%^fSbWI;8`N1wSl#Pj*&R@v_ZD?xMpA5_<AHCpUahwOXzFyK=5OkUq-Zq|Jv4Xbc8>X+Cl|at$WXp>x>)D-Ia&_LSEG6WExterJ+vL%<Q)i=5{rG>s~lZg64?U9vXtaYiWh;`FL*FUIhn<d$vL0_2(r&_ORs+kBJBC@S~fe8PY5I61VyRpchIJno!sq<;!jJtp2(Y2|E{M(u(p0(492yzr${7hgU-3-_uAl+Z5z2F*Wrqm`qGYy0npSET}QhI_8wO&m@-4O9EJ5}@>d#wjdL4EE?Q!&=;o`9&E=!)90XEK`nDW%HBO%5{%CdaD+Q@5HNeTDu-OqCyGX#g*kUd2KMPvdQV!kHS$6B!u5wLAaB~01ruJio8CX1<Z}!_9T8X%XX})<u7aIdG_V@1V?7^AFv>$e4Z0j_t1y&h+@RzgnEuubf^!`CB)S)77iu4NoNgSXHv`lU8*h|O_^taJ{|5MI`U-jZ@QFPLk$uD{&8Ff}=243qPtR0{K1Xodu-sSGJPTP!eD;;Ydw42>%YR^{_1qL@!w}TDt-7+|Lfw-`>ehCk+mPgm0JDie}r?hSVZj#WpC*6#TB7V@KAmJZUB`JpC&iwDb+d4l*9ER10IM*aqZXrAlrb>->scQ14EBw1w3tYkb+3cxj`CMde<<ZKcv9oAw`@{jyaSnGRTr#I2<8lI;1ilNjGGxVo1}&WgcUYI0X<4%3DbUs~PeUI}pffM!zLV74F(+ohbNi5tdC;ES)xA*xji?zKIwY8{qG>cD8Pj-`hXFywIZxVT_h#@Z)3&Y<?KKubr%`6?`7>4WK6cGAc%PQ23m@9;f*vOu^B1}dki+nFSZ2YtRH?jaoVx{})e=yT8E{pYE6!g3B_9ae5j&ntgLq=Me#yHod7G2gWUoCGz|vn`qZ+i3sip^|$CS)xs`P}NW;BfcOf0OFOGP}2yKPL9;Fw#%f;Fm@+R$5mAFOUM(DQw`)kN?Xsnmx#%OndjZgCD{<i>ZbN4hCc)+8qFSQXTdwkzfhXPN1@k&QF*W7DlmI!&|PA$E2%ZCU$6_za#(hgED6BMMO?(3}NF{gF${x8p(6B*Q9hHwOcG<~Nuw^!YqCJ1gvDl?FU|tt{r7=cTw?DZ@tyfI8pjQx}qlFbw!!#&VX|aha<B*%U(SJVWN24cw%{I$CI`A&`H~fb?ahol#sCfOymT7IY3m#!Gt`RocwQV0pJ?ERF#M-yk5<CbfSF>tUUrb+mj^z&{zbr)Gf|FQM0>fjjBNboN5}#DHb)x5|>yM$vYq-Hg@-Iyj8lECSR*70BW@=`3Ai><Ak1Ml5%N8U+Odnt(4Ux_akzXs@qTGSW822|%BWk3t(Cd>A!bjz;dOm8(jsrHzKdhLv0AI)x7~3bKP`Bi|h%+ho#uOH$1Nj1^@=WGO>noX0#8Pa{6RSYa-hE>miyCXyO3{EJx*%_oCFojVsV2%PBa%OG8W)+uoWJ}XIC5?{v!U`cypE$%ayRNSDenN<C3ZaoLBD64JN#R`m2y<Ch}f{B+NHR?X}*;fDy@VP2e*=?>0_)6{oo$W*0x>{?OWg~pmG=C#Bu?%j2+jt9c#tD~Zcs2Oe6pI4*;7&`z`yUW&8egb54llW1_72Z$jJ8adD!GB#YUPYC+k#eM54?1yW$tJtu)_e1BjV%OzUV;9io6`Y-V362iUuX05n<{9w0p_8{yd%f&%H^!a9A428t2u1-GbKv4i!kHB=^OpZLs5qWu@nXQxJ`}CG{YsnA#tR6Hn0m-Iq_?9db%;)kBSY6ydb%X}xu%8LQd&a2E@7=WsYVM_Y%4j({Q|<dBw#l?#c#0RHD<Sw{_`J&*0LfBCQYEOr(+VVSw_{&ljc;Aj&*cZcw&`&T_-JQ56iCm47orV|UT$Lr0g?`y$FYtgJHxL0F`aJVae{hy!zpmx;5Y?^}<Htvfr=Ro`0*ckj77au*+3YEUsTgqSW(<X+`K%=+h;^<k)JPYJ_fgg?C?NbH}Fa#Z0-H31<x!3-7vt0;0d04yYS`fXbkXzmE0TL6RHHTZ!4^;rE-EFpxA0e>W2^syvgR>E}+moQAP(BMgBdb}U-JN<68i&e+F-NUBYWMWU$)YhfGrm(H@(j{cvNnbsN%vFJww5Cqm6f%8NZz`EoX5ghY(L7cjJ*&_5uyz@qx<}z*q_mg;kQh(Qf8NNXv~;`#`|IO%ejKV(3ZUF#N|~MqH*0528ZSgOP;N<ip3l0{pMDaN`$K_#o7km;5it+)Ak`T&Q{@E@)8c8d><<O-V+yW`{E*KV(P`<7q6W5$=A2=x0X*3FpENcmpnt4MfWR3;N>6TxKGbl7;svNyrUDvw(sFYaw=pn1+;9MDjqC*t_4NgpC5d4`1l}+)#z$y(PdwkR<CyV1->g|Im?KH8mwnHC#kb-6KV$81Yu+kdiA__;FhU7K+;&J+I*_i=B?!6PFm!N->5=IlQZVJRJ*F0N+>xM2DODp0zpU#bU^clKL}<z-v%2UpoQs)$x>(ayL80;n#_5oc)uQAN5{vvZ6vX&5%8ocTV)KHswCF!c8l2jum9`Cz3Fz|%yU(5zTKEyxX`-$K7Y+9;4Z51>v5xd_u$N_BY}WtXTn5r-&(_NYM$d_Y~L_6z9fj~$&qiH@;HtZmah2fZ6mOV5%38`_<XRLNu&<8p`p7z5UV>7(2x5G)7jHT*#EA%?@|phh>jvuehKUtyIg_}Z%x=1Fwo+{ar3y#DB=%<5D^?{eS^6EsfB?_Ec?Z*JklT?rs#8}EcRKF?e-*+Vmm-0E@Wc4|NhDU^RxZ+Z$JO`%WpsR4*1bnzQ6wV&(&7{<!6%h^_LHjfbPX(@P{iVWt4vU$RVrgd;FnURx$4G(Wi^%RZnN;H{>Md>6%HE$TSETD?SBnZp(NzB{5ebY!Eas>l3oc-I_^?csW<X?Dq9e0M9S<268?P^K0rG4jQ|>*I<BDu*>>UDMHIU8TEWH8t>N^p+jz2NP%{5J@jai%pp3&_KKrX?$O9S@7aNJVZJu*71<IXZET}DR}yRD<bem5tlT?s=^-98ppC<KZM%;3tkzf$i;?qq=h?3za971fg;e)-S)useQsB|vOzvKxw~Z|j^p%}jXf#(^ZOej*m7jH5Wgv9+*q8S@Hc{6{Mj?k-BvC%I;9xyFw<KKmGJX-<P*Ua?WHH+6d3|<gb@vH8{h3;U9>ZDKo~BgCIHfvQGIFw)cy^AuBdCL$o)^)bxxe>5VpI=iv(9@No?+!?t7O|ty%Pxx@0E~i?jC8CD%}ck<Spr0_r<PmS@P&yiPcFM6!Tx~+s{aO0LCRhyim%j61K~I0#vkN1Hq<mqg0BTcy~+)w!K1YWxnj7>=b{bYp?x*_!U)Y)mk~<qElRYtdJ)Q_ilgq1guiVSj*X?<^MD`RV(NdqGlJMVqm?g0u~}~XQ(1Z5BNQC&zj42NhJ-%z|57dX%`c;`ElOSnZ2hoE$-#{zk_o%47HbAhYq^UV=yjdj$h%ldFWI~Cm3AJXV{d<9gQ9H6ud<9VnQKf86_k5O44u2MN@iOA%E#GTX{5o&Iv_HUW?PTk`kA|>k6zOzkm=TXZm6@y3`G<#Bl%!%*$Gw7S{9=>-!_CJU`FpgcpF#A2V&Qnx!5hZ|qq&ogKO00C1;}A+lTO78+-_u&-$J`Q;kgu>pi&<F1)%eP7LaByH)=O!=$zIhfAt&?|cdZw00N06a3H_sH}jp|%idBo4qR`j>Hpu9L5h_Ln-u3xo8IWiHC#%z%h7Mg)!E_a{+jopWoDze9Y2D=7*faf57M&k%O?Z+cQX!4-AKT0!?*u3QFyOd+ld$&}=d1C6tp)}%n2G`Ah*&fG%98a2erM`vDd_T!R(Y$DLlF;^3-zj%OPcl~)poUg9RsDQ9AD<0Di(c1<8sbi+suA=Ss4qR#YE?j9-aJaCLTQa~>{0VPhdR{Trn`J59NFzic6>iBvIUc<GN28}p&KK>&FUq>m>Q=gd;k?a$Lt{m1;Cf-3MMRefXm1glB8E*8APnKX2=6~)cpu`Ur)ucv;Ue-!+-w(6>);@84Cfu@;&bIWppr)1p9cH8SXSeb*aVi@mI&~I5eDcoe}twIvf&2VQ`KJ>a1n1M(|EN$oaDAR_dsP(;JH;O^nw=yqYm(Vj@n7s6^>0#sWuRR8$+_fY|FP8JlmB}QP^j;JO^cUXJc@Yft7nU?HQ?In*Jp8BjkD^8wJG<drlM>A+Cr|^bs0nphAQn`HKT;I?jHTzEe!Qs;NUS#;L(JUu<JgRy^;nd?W51Rgi*<P5KWwJ{D}S6b}uA`O#HY84ds@LtL?ere~laEQF9a=)&s61dtGhidN1X-sQb+CVqm|X4Uxs1s|*nvD{>(6k5rvhgRQ#Z$ultNUH*{5xBL&J+A0!mO~A$yp~gwa>pr^IRO&4p$#;vdooo5*kTm*UYg~m3UsPQJ^z0OU>QHy*JR|#`{<NHm>oC$q!r)yqC=nk8dNy!IfqgQkt^0Y?O`$G!d}Mi4inJT$&Ju&j1ryR4`4C(x@{iOLK&CtaNn*8P5H6379?lLylk=+sL+ot+U^1&9U1+BI%6z5QQy0}RMo!Iz;}D{e*^wq#@!~cp_OhDDZ3A_mbFUr0SxGlXG&HOhc>$Cq^EKvia~1>xyT~o6t0QkxyT`vqTaDYvLwrjQ%*+eL36<z(e%58C6td|PdUA?s5J<PE!~Bfjt0(tY?CM(Ag6*6ZK9@T@(&3ABA75^{^spO&dFErCx%Rj1W&-vFx~&a;PxjB{K`mP^^>@ofIsq^ul2pUsEMP3SBL1eB>T~UJ+anl8r4qT#9o&suv?@Go)&~`!t;wR`0yEM!tW(1mgnYp31SFAf*8p=I5FojQ5J;nM5|J+S8Os+PZcR?hwpN*<in_pKMI=j-c_`fvjel8K4#@FtwP@}8V43d>0a8cHZW5VMnqce?d{|&e$WGHu{FA1tf(VO2P;G-19h@Woj=prawS_w%EdS=ceUDtBPjjMi&UcDN!bqD(t*~CP058zQh|Oa!cFc6!i3OrBTMz>ZkX4dC`ys$br52nQhHVH^q>J|($_KW*>FvJdjSpin?DdIhf*&3z`ewu<vl=9=`w!<XQxDeVx)R=8!icrrOa+Mdm0+%3;kOE!Z7hax}g#dNLvxlgk3%)-Qe@2Eh<~Dc|&oO#aI#{!@Rw|%G!bVJwEn)Hjrw$PSDa<HLaA*HNFTehTWVYp?2Un`Ok4N)(K5-l)cXagGZ3c)TWtR@J69(!ni|=A!6&W%4b-Y#nRNiH)R<*Sj%6J8MaLlpiI5$3^x@TDJ-LHr)Cv*PQ*pZc+o{2&&y$%Ttg^jLjR1!;DDN<^t{YHnTz=y#!xKG0aqKRGx_?cQVGi?;_qP+0>x9e2~RZldXJSwUF!_+eH;ZEzGLwd%)(_f-uzs6eH47QnI8*o!+C5JFHHN6*=nKQOH;TxsYOW>Gy<?`0-UmvqJ!A2$6JKeL`)FY69kQjT3Ds6KRcZ$ZQsS$Fg+n<iIvv?b|c3@rEHHki^6!+#Ux7a5cH5DCb`3}QouX=3-?PPjqI5bx)ii~Y@IsynBZ3uXK`l8K^;jCcAbW`)^jfA1g)^kgH7cAOrk5hiP}X;S6{hMY$feCXAYl|>PCGLmb1zj;X4>mwah)x=t6jyVm+2;+!!)HjSo|J+R}@jt#uW`FA74S3634sD3c`woEUzy%0~pHF15}_k%X0pt}ZloX8JeZD^5OwnD0?nW!T`o*2v@GLZE<XvOXY9yAec_93AJX-X!Z@JUpPcAY3}hk`qybr-Z^0tc2duj3NS{czzsVZL_nMx<n1kyAhC<(1SSFmEx}?N|;YgP$VbpQGI}|zSzf;h=qNx{@1dpdx9KrOo(91Z>zK9+BnjxZB8EPY|f*k`nLIN%0_|6QAOz}T)1#Fcvl%_Rl)}MqE%1G9J+bP#tUV?^_@-deDvr52-wOO{Ct#lJ3BHYR#BZjIX*1d;?eqPLsJ*jetrY9K8>z0P~L1_#Q<U^`7}h~`*fdDkEVcO>-(qJDHLm4S88{<g2IbbqX|!jjSUaWUh@>ut>o?Ee1Z$Us^!}dR-abG-C<p6cB<RA#SoB2xj*=FLS6EFJF1(}eM9Z5?d)tPe&qf)J)K<PUX$4lsf%sBRRx+n#%Z%v-Kc7VQMSoBZ7iznbEd_>go5!Jz&}5RVz*0BCyRp$a#*`{w29?FM<M#n5~F9!jROdJg$`GMvgJ1T99x7|vGM^NBJ;{BG!^1fJ&i%J@$CQT3#h2Ko#px>=yu5x3QHx&r;TS}5U~w^2aW8}+}U>}@n1^BAwn0*3sjN;a<<$`#?75BlTHMUS6sM%Wa5hDw!j?N<Fx<}VH+pls+y3h>8iw*s$f04Lz#y`(vw~!^jUj1-*a0;(aa&-H>Ef6R>t%@SJY#ROZeap0i*hrD*g1^V6Gh-MCCZY!`>sq&7U>)j?Vazv(Oy|?0#>C9KEUCI9>%47;r?k+<xm7W&plEzmvKunq<lg3?VcUKNAN-iOxw(Xm<g-D{kj6E8(%(^9^%_J0fLsg7;duJXyd~Lc{u_JH}h!9`6*hYHSN%^^i*+ZC(;r(D{Wel+z^~y5!n$!VEW#DlS8^z`Fn;p7so;b8$v6{Wm6erm2;{dN1q4(T=?Uqjd`B?)gF79k-{pc(K@OyDVC;sw=tONL?gvpRH$a%JJrxY>rj_KV;eMyR0l_ALZk4`6;W&bm9ujJf|G`bP2W=DWbECQlB5^7v;&qp<7nH(YfO|$8{IT-V1=Yj8iXVUU+tym21;auV^~w_X#+cx6s&@vA9Vxj%4`7PBY5R<sC2_HDFrCrNhY#ya1^)IX7T8k;_!CR^Q*|!(ii@R`T`x`g%XMeA)5d+K_y@LR`nyxGt4v9<e_VIZ)>RK^ts3{hv@vWpHQPAMm^x+9)wwCh6|KRBm_Rfoi&q0XQym#pL)G%QU*{JXbeGE_H~ySV)oV+hZ9`wo5F1f3QplXr%!Zf#oxInh-LlHVWFYzS{=GU%~6qjpCO-Hchd)#E4)z{yJH@EX{mG&JV=}1I^>)KB+d?&d>SknS2YnFsYQ)bmn^Yw_c`1-oblBnXqA!&n;$Rw=I=e`Cb(xQyW7MK0K5ypUsx0dg=np?H2A168k*c$3W6q&*9o>S*?QuWNfOlEDjw5&!bJFU|1Psp1y){!x)_^l(LoX|BnAAnYNIofb@)OpL=u_QG@!Fs<i3G+)-H$-`FyJ#Ev2_`FvrzO6TroThuST69|Vt{`a>OfiJnqQ&m2e%9Idc?2XMLwd8c1a~c1<eJ0P67~w%|U%QT0i;X>K`-+n<v%2alNXA5Nf?pXltugqgj5hg#F>FBk{Noi&`{O%4|1;sTNAXLJ(P(o9=JFwx!!#!JiIu}fFQCY(;qxzNqqO+zb-haB-2Ee8?!YekYdun?Xky#bX?%W|e7)FyKurb&nxz`Uwy{57E3ZELpHHW!9oAG8Cmt6mobnND-_W4^`Rk+0Q;&5%te0_g`OkfPela*%h1VJZER9b6s5!JpFH4uN=A$-Kdk3^XJpLGdlns-h6+`>~HQq;GeOTS8X42<*`A8g2bxXJF1y5Q_iHRToYemT88{4(4@rNkE>TJ`H2Y|5-w|ot`w$Y6A^jN`<AGrIOP>KNinTFW@A_`wCUf$6RB`j0kbBsm=p+jO;{Mp_@AJvq-F9zt`H{~3Wt=}Q#tFqi{=zJU>!EdiQ1P6yPKDnO0`S;%b{&~wEA2rOPn#=1KUrsL%b4l6*kCJ?#-`CboIvco)ZPBi4z=Ll8pOvi|%1zTvpBB<0`J{@>tX-8z#iHiosD-${hmF5J?w4Qw{+GY~^5?q!d4KvFeC-^U$xueOQsN(<8k|7wbEx`Fi$#Jy9SxFixc~U)U;g^*|NH$Le*0%&HxCbv_Mf45?T8l5?4DcADHXa;MP|LGDsw2(ZR%*jIc*fCc>Jmzr0O?r@_i_(Iv{iWAt=<-10z8RI9Jy)+sZ^`Moioyd3x$-$)YC^b(nYzL*-;xRsQ*N{qb9U(Rl|c%q_}vF0zHzZhYr8dwid&!kDp~*EcDSBOd4c|Ni&K$3MOXW4-0BejiWE;&0j;Y*+`Ee__ZKa|IfQ$|sU|v$F?Bo5_$iT|)&@*|zDb&SDz^m|{!N#JR69z;iwaU43ba0QwMZU>&`7e$ZoWEv{{{Qk{P8N$nux#M0=*TNlWiC+r0@j^M%c%<Mt`B*Fz`%O`nmt?I>xvSkm&z+=GWnn_YF;PCrp45NL}o)*_k=xSFUphp;1zj`pQFc<Q`s#i+nUN+R`il!r5yS=C}kk5%?TAb?1y$v0M$mTW}J3lQrWSkOto3bSQ<NGIDF42}QcuXa;SFq!w%tX#Tk6312&UZngDhb-Wn}T%OptoH@;Tnr~518)7A2?-c489lgvj99tW>y8A?NE`Byp5geY!?`!ts}q$kq{5+V$2d<THD?~DlF4QG1PdHDi1%)9jMJ&*<Mqml}CGqHyC#_`bGG~<G%_UuEN;ekat<)qA8<L=_uxYws%(7OdFMf_3Efhz$_V}@HYNJhg$A-JH8#i_rHo48j+b-u*njL$V!S3+g&7vA<^oPS~Tn{)%eX$JY<HOFkXr$*a(e|E^Ib;rFsc}4qWanY}v0ibNFcM?$+h<gd}Vn0}I~qc5@4A8T?VD39&O6#|VwL;Z4=Ds%NrEC?y_EnP=yyZPWld#totp59W}>4u<`Q?#tvZTKRGoj5<Us>KXhwy}~Jf-0w_g;E%SJZ(8p<QGnUBAm@6tbg>IOwL)C-BsLu~_$aDkr>)Hz^T%Wi(C}DQHA@BCje2=The2*z<jRiPkW0S!bS_;xYRfSuUIgI=F)WvH{5YuOOB-(8tx1+nz&H{b2bGaAt2x2;(Gn9Rlzt^9jKg%XHhppkRroj#vs*d7f#a=llc<3Ez8x!HE!3>}8zOGMq4U|$CE?urzJPojWC{dE-XPYo+3G1)XA_HwgtS9F8V5h>p)o}&<oE3`!<)LYt^)05sbTPFrr8ah&mPB{TYTQPqD|MNvU0N3NRC5at~m(TnK?(g;V~RFj$?=GVJr-_#5$Q#oka7fg$^n>5IxN6w>Matv%NH#yT5N4>y*wIr3cexa}TOuWs%|0z{R)KhAW%-*9J7PC)(>KoeX&-9%TB*aqaQfgr0rvYKf!_?h}2qt24L9d#(mJorwh8^n-RsS8x`$f)!%`{zy#y{cKs~as=*AT>`q@ade^Q>B#3{It{kgl46a(-KZV0Fkq|Pir~g!BO&i~I%vsQx3V818!3!W#KuAq9T?3dKPl+VY%c(NA0-!UyewqpBt|*)NDfgH2wJoFrl)NzES>FhA#xPOSMEQwk(uzBR*CD4o3+gkiP0IM?+5`qhxGM>j;6}%=CRg$B6w&0&9{GfI=u?x=fS0ilOH^@L3Fs`HjR18dah9y;01W~o+s}-T_M}MKQU5yz>yy3*)CIZrD>?Vp=msDw6kO?3~;I-f3+Hx%{7Jtn!6-~&C22{`dciv4NJ>{R<15rT=~nh=QJ=mr}rXg=az3L^{!*mW0o08yte1vzVJY6l>fN&seQ0(KK}ai?+0zAng~pQIsg8%7nR7g{Zx2?gYTxMeCQvb-+g@pf{-nt>hW>o36qz>C`!;YgnPrGe?dSq<-=-phY*$qg=Cb`2J8{2%O{&W4wxp|=<;%*$9c}6<nVJ4O9rj&U^L@;aWHU5SmvIJSfSU{%b&FZT(oVZ2CEutv%L0LG6irxoBE$WfBpj#{PEr=^>>l%PROkwpFTL17kkzy*Etl_qC&#$5|xzCu^1?6yG&S{`5VvPT}d3MY(90Bh(dsFzXGOYnQ+lT!(DU~CxT+w!@5<qel1>Ns%DnB45@}c?$vU0CHx@Y02Uu|IR|C05vKP#Sat^#v%iI*m^l{P=Xl`TOk3+$a5QzgP%=67LsEzvNIRN4b34a;&KEy^d61#R>vXY9@N={rP|Qa409t$*7J6tqxXC*ZDkX{gw2V2rv?S6Bic2afrW7v%uV3(Bj8aOA9g}lF1JHn<-<Dqg5_I45-L-5sqo6(X+u(rK54*pE9KP)2ZeJ8jT#6D!CZ+m!Jq4Dvo$X@q%BAH-A{iWX&MimS2A6Ex$Q8K`R}|xyc2o?2rk3bB+C8xMxLU!KkfKF5tT&Ut(g19n+c<L360=A#Q$d6cyX>Rv3Bmx-3$$gct8wyt1&&r1zaEmhQUjbU3Y#5CwTlF-i%rhtp1PoQt+v7~5N5Z2?J7!T1Sj{8Y_dNlwt>a7`3A<#p_PbBn6jOht+6oxV}I|yn*cb|7;VyyjBPbawZJMH6aI3RTw3aFNADlBLLCO=rkJ<Tg~b87K+DwTj{T9`Kz|$E_dn%4_?0}a7LO-gnf%gDl6+@Xn}B&dwsw3*6kJ6udY8M?I?X}Gt#qt;&~A34sXbp!6d2q@EfO}kcgwWh1>(Zi`ejMH`XpU{?r=&@p3=7cyGcUZo^)s~iugeborHf#^|Ba-JM+K$ZmSs;$rx5t;#`wd35oDHm@3WTrP|P+PWSIyB-1eUERu`dtUM-pG<Ft^Z67k=(ak}PgumxBWE@*SlfZW&g;d0S0S#I@8Sk*hG84+!@7=hqU2cp%WI$(LN|&c$bHz=xj1k3WVgfyA&+ZDGs5(c~KMma;%(u@p8u5y08OtC0L9IMbIA!-{=wO=rU;}$8U%-;Ff6-K_3E5@JKzv$UFMLk73woSvWM8N>K&HY|a+#&(QbqozaqiZdR!cxVS!^+_c+!ydU-IFu9hc+DH0ULE>zBNPl(#u)efioC0xbR2HQhlAnQD1Z5=_Z^rb?06X{^IY&cu#OIc~(GxZ5T>2`0G}5?G^J$q&8d_rYo~N76G#c!;-1r8>;nKUu(Vi)I)jH@;&%(oKPKBQZ6{ss?|wUGZx;mrTEnY&4M{n{GwbX`1a0v9mjLbA>;I&)}(a*xn|Qpb#4Z%~^14A34r^JL)q{GOXg(c`%S?-ihfFrO#utvyxO+QNyFx$}YcoUW&Vw@_2;Ir}KS2b>Vdg!+`H)ELwRTm#O-nO$oQoGi1Kmz)dQwqa~6Wn)ufYNRL_C8O2xuxHhfKLFXXkwX}y(rNDd)mUmmm5*Sdb4gxZ5>iU<klGpiJN6RM#?~`GBY8Hs`5~?g3xRYK?XD?>kuL<I9?!@SN8DMP`Yi*!|!>B4FKrK`|Eq;^E(vzmcM}%Pn)I6hI!$&I<@Fhi8@4SNU^|eYy+Qv8m=##NeXybzqqyEg%$UU`kRWZ1<i&5CHa_d~D@Bv0acCc*ZyCdY3Oj=b*DpP>5qMU~;F$j$Fm`CDi#OIe;%mveBO0CpHQUiv6F_)qFWH6|6=i&u{6McOd)GE+AC4s<aB`LAutF-_uX>Y8>eddztA#^p9dZo>+=b#m3wavR&u@tI`i}6Y@@zRJ!-G@HM3Sa>~BV{VP%}4=X$=$58eP~-(E9$bGgRg4rZ-ge6!3}U52O-WY;Q|cLooh|$ynv_gv?S^n02)nW{uIaICHKqT;dzbGmg!PeIxt(UXz^uR(E9O#W6re99jyeW7l2npoFLm59cWpRm&4b4L9|Yho#ZnjOg(^hFBxy2r&IsAH;ESxOCwq1yxOl@@H)Vu0;&4szS!7pEL7i9rP_m25RJDb=pbdK+8>DDPSE__7fIY5a!PL1LnV6@;k4^%y>+A+tJ(N)7Yp>@a5y<fTZe>NfFdE}kd}y*3yHq~{^w#@M-8GqkL|C2`LFmab{05cnYr)&b+QTHXcInnhp?pkS3O}o5)6DN7<eU_6AP`!(aoq;Y{5rs(X1!9SHYKn=fUHLU;pRlKd9IBFq;-2g^l~-i#E{yHa3Q^vJa0Q>32%s>n-K4_h}QuXQ0tra&h#mWS#|b+{BN@?)E7I1{i{l#O^F!NA9)1-E6M`PXyL(x)wz5DN0wjdw|5mXJz3Q^g|VMYImEh)<+0zc0xw~@ZfAj?dc>aDU{E`&d6#OXm_U`gvOyVVa!o$i`qTCak6NP&5UouW-5@T60b4jNP3)_=CmBisQjwsL-N)Q<UAJ6V!KX$W$c9<iV$tM<=p27#V(9i48LWPl`^}GLu1AiG~N%}r6Nt*cvqdc0A(@8bx+tBnlG$GX{5f9-qpR_6RxThYa4ij=V16w+lRzBTSb7$OE`S;eW>tzPh7C=i;JL%sTYG^h;!N}U*E#tT0TL5C*WoF?W#OOmw5LJMBwEg;kZxFR~T?wiM*o|#Wv~TL~<%*FlDlAnkpVFd#(iq=${{abNKimiPh+8XwhX~msYQK_XWNy`#8&PgW9NPI47yIZ4+t+*#u!%4|?^yci@((J3!J{r>1<WH07=2;Z9oQiQlL~N0T$=y6n8F081!26$Z71M*=}e33Nd7hCc{qI^PBx9blL(vr_7;t(T6tUz0h@*}?H`8%Ati1Td+3RvCMxDp_^A-6Gch>;HQ3V!E9-@O+!Z2IK;T)~omVYeoTUQ7vDOx7@o2XHIQ>0+OAH5yf$9?YF5Fj*F#z!_fHBAEFyaE^NxNI8su&BCEHJz#>M#Cl2BB!Db+l+TDg$?)pHi?m$3y?I-MJPup7myXL-29mJqGibVM(zGIAX2|Bzr;aR{mi_5^xmAKX?3breksA}yPf!J+{mGJu~|Ig3%*T4Pz+b_TU)QjUs<8A)>+dn6w{>#ri<LfUUaWY+|$KVfF+_)$M^N~hX)A#s8vwmRQ-J?$zU7DVblW&0K=jobHlK|TVk`o^gHoarKiptNG4jH_snfnLX<Zf{w#XX!WZF2jtC79nAfB|WbhRZWG$OesF-m9@ErP{KVOp4PnPe$Py3`qNhH0Y39E=r)?TMt86<THpAuf5`E0C+TV&)Zg@bdWC(dj)p{P8s`!&XvlTm|5V#B`fz%jB1Dt3uxo;UE8i>J*zd=L*(OB)_L~L^6#purckTCE-MuJS|T*so5|fP^tQ1za=y4xYi;IAu57swu{x_xs|@hU9{ciM(;{ko$XL`6rX%8C796Z+=Q1VEGnNV5Q&Ga~qU!3=_|@GN@T_O_e0u0+acY`F9OE3~T<NCC&f)1OY6qZ>X?i+DGqb<<_F>!x<{r*_8J<|>X3Ij`E4&jD3vZE-T<soUl?>YoXyl#fdDX=>W?8o6T&c53&=V6r?7Pmu{sF}>5Uc=5Wj;GK<@O1XjfM>bo4$=nDMsSmDD5}DoMzkE)%mhzuv62JuD$jLV$f6N5o@V<i$!s*t-_fs0J#0(6P`*rL7j=ivizS$qH4)_LdEOCQ4F;<Wv@cj><m>zVFAA<c2RTLF3EzS`jy$RHSJ;wE<dU}I<xn5rbW3t!*g)1hJp2R>k$67R3}Cr%n=HlHV>VW-~?rf8S9$5u%oeKo^zIHUd*6lw3=kRzDzy($drIo=sh~zMIMcxbIM4P#p1lAq^2V<cLFQOuZx4&h`zdtE_DMLaU}17TUU$9!cui&eSc)7*5~=05Wm}mDbwevS?VFq#-4T4*^vv9_d5j$k-tE<vNpSgeF>jWsMbJ^4Il&?cg+-``)bZ3MN4;P%22G&vU6UCUY#d+D=4W0AXE{7L#7uAd4Wh8aR5f~po}AQoqRd4ztkaK7$kEnH%&$uK1Y4dtsVY;@EMxKy<W!qV?-GVet(9ZtA9fikAGKv9E;lA^R$w~13rCRrjSXV9jg>)6Rb%kF==i)%$*s4iuP!zY>&>o-pI${4mm%dpJT3gQ@_i-;9&i^wa?d5rKl$~!isJ5L-cmRf9kltwX0~my#o&#z6%f96pSsr&Xx=y6o0}SsESwI-)31EHWIT?D1>`QP$mZN{?X{^l0`%NV2iRPv<#E3v^Q_F-_Te(8Q3$}t_IO10@_=|rikH=1b9N&DZ-?VIJ1Yi=BvD=63MrDAMOeZ2yk!^IQH@m7wowb$E#!yH&VeyB$g+(q#uE0wj~0yV1xlG%paktL~6J}_Eeb?1~|l9$#e*<4=1@T&OJ~m={;Kog*x!6Rn)4S&rv%GyTYHzDb)r7aAQdBmhDXzgI>E*+6kY>mY<+J+5Fn`ANs~%XVae1%B4w4Lf1{Mmx$rI=j3Y<B#H<>AEAW<DvkG%zagN+;+%)lcU)<oFLk=bKr$Hp#kQ(s<=pPd$>82mmnXQvq$1vNR$zmrh+-g~kM68W0uQJLaSZ{QKWUjFH-Z&$bcIze39uiG39X#SyUPpQ%*+I<&8j>BN)T8#U%AQJ9kjMo56is+$cQ$2k>Yu<5xCg@9@m&O3v>o|TT6OL`L&cvMvt^+XamjaLQEB<wJ1OAc4Wv}xv7$os!`AXpCMJo5B4<~dBi?CrJ!WT-#uv#_q{OCXTJs&_j+EI)YIaMnM-?E47vE0(XYb{admPdm>a`Er%M4?%)S1PM_5qCr8};-s}xfLE3Hl_r9x%2MeZRP82y1dKrHu4-zvIP#ii5mb$hIT1BzY7-KLMBWo*(IyHBT<GfGi?23N;3B@0$V*H(0lQ)v)Ik~J1wWX);{y2Kz`WXMUe>sSU;l2xoJBO>)$x!}cT+N;8fy+^O7oHkdKwga@1?z%rm17|;QNx0O@sbDmhsHvGO0z$C}vdeh4tk6WjD>xdg9!Csz5NVo#Wnr4lfx+#E{ry5bUa^hXyxt%A&DYglUDU+Az$<(6S^@m%z@Av^G#P5AU}9@U6P_(naZc+GHnI0b({=a^G(q%|6sB{JwgkO{z&wm%9h{i+n5aU*ccN98)vIk7XqSqVkHdF4Sn^@W#UBODdGG4U%GrV0P6D%Pi&kA}7it5GqI56qR+*QnKO!Qn_V#uX5<lpHwAc#SFK*Kjf`b(zQ+hh(q|Tq|Y`GGRBi&#ebGu4u!t|5&*+uHW@1#nEZJ$8PlcvPFC8__u6WJv9-e59hxsj!Ia&O|`30TT~cDYESIEWulDYYnfRnX`$>FXHxY`CU;y#RIl%^!%5LMazL*Iwe!@*W_lbQ!IIvs0o!F$}%A4VSdUQf9Y!It>l;b!Dx8VR*(L-B8&Cq-=<1!md`4Zt!{17L|(E?4LNwVibswC*EFPW$nQG9v^!?8%S|hCur#_(pAdl+D-&cw{Aj^@HTLq{O7nB>xAYm%HC%{!6QgzDbvg?c%x7)U)-U^kdSpavooyA;#z9gnX(KW+~cpu4BI9NP^MmWhL;JA6qeDpF0*P0C*mSya_FLt=jE_Wt{s!|LVreLa6nB_dR|qX%*Ff;TP7CffUAvjm3);`sbt*}@%JzZf#Rv#glCa^oxjSWu5||ZK8^wn-?8`!X5lglYkn@gJ_<hD%#Q`P;XF2q7p8s3Y_;6(r77G9)Z&{7jsVy+0Zv&7!9ncS<Ltpo@Fi&H3HAl#4SsepQ8&GddSSXP%DNt};p#><f2AUiw}wJ=)HNjPy%4OB;v>1Eu2P#jy9xJ8;EL=~5jq02J8GReca)$?63=dCenGuH52Bm~u^xMAPA~+!{LVzC&*ZGKd#7ELboG@B6+Y75ZszbQd2Q4eVdhFr2)>E$R7=wXT`dHIDY9evvyCB%)A%rjo-Mst*;<#l`yw0!I^NjLjPh1Oc!{Akt9&w0qEhQJ6v<9`py~o)XI_8vec9xbhj|Qjl^qRUXN{yCE(8jHCX3I}BpbmmLE9x?Uc57)Z691I$=VG;8e^LhB1ACpy=DHy^PYnBarm^&&eG|UBQRS;z(_*x-&|LUzmh1`JvBj*5U@wD0d~h?pGG3k^-b?zOK|Rq%>OYVg6F=i&XQ|`M5|6Vd6Tm_k22=l=C3Im;vq*B<(hEG!O`GdrH@rD7~G3i_aGDG<{=v|l>OFsHo^1J%k?AFDqmFcQ6uf_$dFh?b!z1JuwaWv>!*!GUBvqN$;<jQx{^M5vw3Fx#HaCTh{EUSKBeAB0e#lDII;61*0!#6>U0H#7pVphp1cqnl9j#YDO_6#)5ZA&7kpJOwqc__t%kcpsnXO_w{MFf{frWO@a2TM<XLM}H>3N8+E?2&+0N?7{cqYXxstmkZ5{Fw;rm{z<{3-wZj?514ibyv`kW!L(Vcy_%MvH6VhW~KyVSKW<UqR?{bq@~zub6yuUFJ?1;<)$gHL!xU=nlE=LnWpVW26Emg;GYS&e7^M_<iE?cywd6~TQ=Rufn%;X7?S3tNbT_B%LTkLJ$4|A+swAzlo+LR=tO41lfWRx-xsbeVJlT)g<e{UZ|xEOkBf`gVthupQTPiA%_v1f#y%Hz2bGNcymgG<vKhTW*{0GcCef=8Ekbv74+8#;-e<&SNjjxc&~2ocj4FJ>=Ucs~sCepg6z7-VDRdpEdTt&3JILm>NdXes6{xsi@sJUeyj52}G9Ge(O~*557LXle(&SWGwZE5VMHigM*>}=F}myyMTifx3HJh-`MQ=X0yUska8%&!z^5$EL<sPvyIFB9`6XV{%MOJ^-wn-L%k%fn)3@=ETv19bIB9ojPq|C)?0>Tsd9k=JnaokpW=L5`fp6GN>fjO^<LIKqaAxeChHu^-E&*GJ4Q)C8Qx{srGfvduGn_NbWx>!7M#8L#+zScIM&MlkcFb}vO1D|G>^mOr>P>Ti7P4dJaS0LCD=lw5X>@4m3y4XlP3trNLd9!=gw*zCS4z?Wt@6x=ECR7thJhcI7R)K-zR!p-a-aj#^UClIN;!y=gg=fmv^9L)U;?Bmk#$Y@P4D7+}wKH1Q=7jT76HL4};TcnyA;W<Lmv{@`bW{s~Pg?3Q-wX7rInFbHp-0q!yWH25qqEaeo3Ol_{KU8Nky~Xrsg=l%%iyQaQwdXQ%1V1;Dh-6_cYiEYs+&^IXLcxzr(MV&OcpZ;xd(*|w?lwZRe=pp^#91D4O+Y23%$%_!u?`ffY&eubn*H;P}d*K~>ILLGw0`0HfpvH|n)G(W%=#4eBO`lNkeJ3r?|XVMtx!ld#~)6MGH@OhaMSp)A8WrBWYcHm?sh?&@J8zNS4Rz<|r`p*OZo{Lm2(uhu7V7cAG9W`R(WBV9Ly3silHZ4VUqJD9*rKuGxQk+Md+raQHNZ)(~)P^xSLn!Yl-P;}iO)|wGZS&}f);{j&nxX#eDJ5ppjk%+O8or-ps)rpsUZVKIbd}D%%r>N7c_t9se*EumDHdFEOQ(ulER}5^!pR#WLTXy+c*`;pcl#)wC5gcU)V_8dt%@4EwDuLxUS@T%R{)HO(*(aVxKm^BPZ>e+1yR_5T=>T;boR%0eEw&GV~-+_9FfuX1<VISs%>cm=(8P%jb1>JnZf5@&PECCbH9HM$|~7x_m6x*0K2%Y^(2|1iEU4(@tM;5^*;Lng$)o^mXZeB=>2@HygJd}Zq*KJs%H~lh!iUM2(52uQ2zY&(dDVfTpm`GIJ*4jK0dz~oUFo)jKGsdr+(DL)}xoD%X#uqny9@4+8-W&3_r>SMbL_&{r?*8qpv=Q?$rC}bA@~)1*f{D+x3zltqsG(kN>qI&+(1z+PwHflyJvyQ;Y{(u@1L<3AMJ-jG**b!H*xfKbVkP0Lzw!ZT_OXSSt?Q(F~=|QtoVw3Iu^dV(0tW-a;SMlu|DS=-fBu9FeWxRphI%+H2^193R1NuX*SOhcQ06p1%3_-v0i1>mMIA%%a}O>la^6CJ%E-8t9IaSfJn6)=oMbxQlJku4}+qZvUT^n;ObZQ$wE?(jvK^ig>J@h)7MJ=HjT;tiOkizdr7lU;h4=zy0#(y8U^7`Wt-h9GA&ZMz>JlAD<eWK<#s=`b~>Gf<7G$l5e>G_~&2#`s@Gu{TqJ!XJE(<503Vqp?B?w7R~IQTg@pIIyOaiwx+akDAJ+nXu&yc6sCCmsvV^2H*TtZD5`!QbIBnn)YAhaK>#>c*D~93L1ouV{1kaI>S)QLClGa*xbQ+bV^}@?`E&j8TYcqr2L;S6TXZh6g;qCw=QVqLpQ=-sF=f{`DUKr^=luWv_s7RSz6N8x<*t4oPs`$O+D~g(2bXPOXb5v942Q~Fk+_$$2S=O9kk(d11yb3@;;Is18v>XLNYKQ&&pQ7(pM$QxG$8<eh_-l+UOPYNv9=c1SXfCxKlh}zVR2$<bmFZG<ir!M0vbo~V0z~9pnnqK0<z_kJhxW$;zQZ8hZ^89;Bw6*2^Mhp{X&1yK4?#iYff&pwGGf3469#Xm)BqmSzpyFC9(h;YC}TP)~wxL)LqACKruZ{_2k}$jzMH|8;qTw7928mgS<^y%Kh>ElP!g4&HW!!$vhA2_$V`xbI&7|*?aR{kf_^%Ht(h&oi^xgmr%II;@tzLd+`TO*#Lv@g={PU&ykr`L1#NuBqVQRr#jmOhG^>uFhL~5gSr^AM3>gK_m2w8bWsd7o}|hM&$8@kb5^!t6KUnqp5YB<*NlD<e)0IP!iK9bb~nUamXv79=utY#ouBQU)iu*bWnjHJni4QehOoPhztEwUyWNg&$M5~G@_t5S=9M(E<RG%vAjEbTiD5{zI;0j2`$`pkvl9=Q;U<ii;t4iFqoWI(&0VQp!k+_|dkb40rp+8a+Pb@yt325V8^^%McD&u(l2ZnMR4G9048}1+<863TJ*n!MY!XU|aZ={lIcje+fR1t3ro@9eq^yHs|DpRbxr<i5oCTu}(TaKoe@?G(${+VTlNtD<t>v56yG|5fHZ91x9xYw$qDZammOP0~mkU0MsvKzRea1{H83QytR#jC`!FHnto6%vA+ZMUPoHpc=FVCDy*N)mAj7b$ixItXMWgI^aD*4ieTX$=crJXL0gvLQ-WXuXkuzj>n0|}*Hi3#H{U98@o96}X7j>GKMR&U^VYuqF%;J$Ci${PzcYyO6a+i&Q6Hgut}#Q43zIi-D$L&xdN$zJgP(p+zb@5QgXadvwH_?xdJtywx%2U7EKOlY**&*xUH+&fAuddF#U-Mf$td~4nnT4Q>J0o<Fe5+cXui-5o)Z9~ZY$Dmo3`yDIs?!N+sdxhi1d2m@J<Ok1@1m$dTo5noTCD$m&mdHx<R|{~Su5fhRpBNV<pjM3YY&#KOX&NdmV(OKSc9x8ZD9<qR#G>KiR>Mi4xl2M1p?m<Mzr`H=u&fhk<?2#Ql(i%yZvfvzntlWA-16<D1{X}Rzyiud>^$#w8XB}lSrY17=>+9J{`&Lp2ijdt1jfzJzyIt-#Z7NN6=v+fcT?vM^bgSQzP<tFd@O$Z@p0q%x-Nt9qG=k!4J6RNASMjTtjXvO$#V>X>NFOKsZyp3pKS6tU{VUB%gcox=TnW6`g7&s4F{tc*NcOJU&dwbF})8Z>MwuR^7hfTk<`s<tj*GPW65}5e>U|$fByUj<^|!sPikKwwyt1lLK;qRDlhh|QHn&!!$;9uyF_KCcr1q3b-PShoB12h-d#zkv}}IHn{dg1+~@2Uf2Z0tB@7FqQJe^hm;<fpYuanP#FQ<*xD2WEC+^j9bCo~976>dpWQ7Py&LI)l>tNX(P=ufs$z_^)w$Gy~ylu7cTIO^#b-GagEcHW@zaKEdnmhAEyDDLpRmkk+L55Js>0-&R=V&>|OpWRRwD{~z^w4&2lXoCgib?yaG(Ebs=$j_CKo9h6VP=}*Md0-d9*j}KbFpJ`4rl=O!1LSE>tBK;aK5{i%`TPF9{O!?KuZeT-@z$ac5=5bid-VO%z_hI{kxuGY1##AG3Y2#si(_uD<+LwiKGoK*|w1@aviP+O)l-I7ywNz(RIw%s8@SjtzcSH%C0vKdo%efEv`syZXCOId`M2wFEnFw`6xRFffUWCtxQ*qlP5<yT3vk8bakZ$I9U`nJ4y@}30N1K$;z#`K<nC!rCUY7ZvEQjTyF#?ceBD2_@{I(j&^SyWoSF%5|(x4-qtn-VC?VR7a@T&jS=JQ$k-;aRST?AKk}EelyFl^40`{d70R7hkM<ABwhM_j9iZz?h1Nx-$STm^M)&<s30l4Z@YVW|q$`u}{|;iam^R9;5K{INtex3+Ek&!SMelNVTBoLP+)Brq2kmAzn%eW#M1jFgSQxXxy<1+7E)W;C)^{`ZY>m7A+~Jgza}jL+Zj#WpCym{TB7W%F^1NKQZIyiHfA`%cK`S2<XvEIBCMoCH@Hm(%s`8}*a-Rm7?^`6(F!d~wi`=X{CV4b=7L9EmGT_n8L5+kh&@^O(o}fwKyFe>L?h9y;Jk%3!q&S|)ym#ZacA2>NkO7@}sd$(Mg_JVuIl*Ql<)-7|QXal^x?oKaRIe=(iJ5PoX*A*$(`kx7_Ja}|o^^!Xo58QR3t)18udz5ejU{8*^Q5cLvL$`DYI20n>2^U^^<f#Z&q|l$Oa)>eSnvq)-%r&BnZ`~#v~~%oCkwbL%oS&^|B?@P?YJCIra>>UTfgLm=icU|MJQ_-8Cd$OtJOsd*(_QM6nW8IR~2mS)Z;ReGg0v?;YK`)yRFSlFv+cuz#7%6605iTK3Ji)7JX@>@7x7fRbI`h#w}pDMKg?%8{e@W>83!rk(ioem5e;vuJ|>aOQzpOHk!zfO}7x!G|hI0*x4PLK*1lvXYf=y+_I8LP>2nI<^=N3NT~YlsLwRXu!=iwz(Af^uB0m)J&(=Kob0VyC`YfA%VzVu6n87-@d%ku=lgu>!s`%*0pH7EA>OBPnX3Qk)wtJZ$b7Sbn^ai$;gp#LQ!lNlXlE2-1>oA$(3j3Z$ZKg2qq(j}{#A6`xGiG|45)Ac0hu;+9ha^@KkI1uq~LurY){PsF<wHI)ltIxD8F>{Vpc~lSmu7KEU|19ZC47-Xl<Z_!!V;3pq8jTU%g3Z=^1KA(1;zvJX%6xBN)&Gd`Zz&Q3Cb)S|uZGW1Il=NyJYeKKL+ftB*$Rsg<j0Nbu)(29Yhd&UFeOU}oJ{xI=TKrAezQiJ>hRE6RDu5`(}vk9j1XMtpvCmRvAhrqoJJBsEyodBA0$6{3%}&Yg=F1WvrHxu#Zu))l*wI<5~xQXC3+0<fgLu@?84OH7C9Y9?ilyo$sXT2Umg0+D<hpoFU8V!RSe{HAgg>OS;2R;+flWTZ@GzfxbDo8V>p(6+8t)MYsbUqu|>2u&=58{j^N_y(_p3oyK*BWp_M1+2iPC1HOGXf%!GS{#R$+%J2F=QT!Krc1>vz-+am#g}bCoyY>moN1XmS_w=q0I#S$?4Th?*s>xohp+d7Xq_TE$!A2EdI0TSGTuH<r~Y$q5-%K<MzY3vwO_a3b$~+!Vixbd*l0;_!62(tdvFS(@wNmV#EriFf%xqN&EI{I#N8pM<W@aYvPTh4yPnotN1CykjSqLRKo1UwlXJ9nNT>xU5<(7XiCDRi_zU2FE|zuFAlmcT{`!~yiqB$affJUQ`|htabByqfHsN!32ur$u)f2`e!N7Ndfmf0_vCw)P-HZ}v7JO96<RI$_?p5$5;Cb-);bA)3`e+`5H=7n9g^l~-i#Ax*Uh8>dQqYc;t*T}8z1~v(dY?8id<Gi5B^O7}O6FOhc6CRf$hzC73>aVtIug6HcpbUd{&usy20RfMDWnSNGOq7H-R=Pr6Q7lZThI^X0dH4brPz6=;%nMQ|M1{!MD6J$C@GZB!p_KQ7HD^;9)!lBGKreh3I52&$)YhfGrkR*sX&@ayvC3t>2YeB({d!EvWJ%s$y+y&^H?~G?K=6Du@`bELbTzQbDtj+yD(ZY{FX^pIz?PTXv~;`#`|IOD_ViU(8jy!#04meF|K>U#?X9W$+MLfV>L#4SNC#HxT;dDZQu=_gW)@E9}?qi)ea*s;qb}#p~CMyaly7PE`lbeUJQQyo@t+aeG7kU`2+!;fS1{~tMUw88PYVu4wrv~<32rKVZdo6@{Ue)l%aq`aw=pnWwLHX^qD``g1VK@5575ke2~OybTzc-vad_4SG)TH-`8}h3or@PMm@thNu6z*P&3FT2)laFtLMD~w@lpulEykU<x{08ZzT_R(jrg%Min}moH5tcDplbqLdmHxs4YAa2trDr1DZGdK`_(#HrVKZRU+4xoxMNeeof{qX9vf(Z5Xk65x}G>OlItrs$|vec8gg1um9`Ci|KaWz;jhvv)zDPpwN2tK7Y+9U@fZU>+zO*_u$N_txrI*Gclq#Zms<`wZd_+v~L(1U;0CI<H&_gITlAsN>^m{wh>s|y7Tgo!{>v|Kq4jo46WStfmq#vfbQB)*v+1{wf=X_eV00jL2(p`s%qrfzAeuf<q~vwYr?bHu5EbOE6vlblPK7(T%xMAV+3NiC04@kpZq^R+h70o^KZZW_ERs8AC0&9>u>*@i25%-^Ng>*e8kCgnI3~bTyf)~49rIwRZZXH56$9zad(eCU36)BI!?X;mY=6<K1~8_7f4QgK-lz-@hU1mS2|?yo@VYJWRttaffV;}uC&SR!<JxvUjPQAJsK|0)F2x)c6qPHo|J0KS~4k4$2=K@YcL?~7t)|ZZn-Fdc5gilVUf=uQoQzxqXFR2$USdcfzm;~JnR+R5jbV+7dlreV`6532bZkeJ29#;i@hIh9KLJYb*yK##(Ic+oXR@SzFGcVRn-(~)z@W(LSIXSMtd{4dxhRMwnokuH)^fTJkNO-B35VBX_Wz9*<)YcYg$B&4;hOZ!gNIZ%YuXT?A($tp37J!a8E@Evx};$N8?v_SHQEL(evq{o5iVV4sncgh;yZzCOe0xqo^H#I;QFA5Y5c~-rI+98<=}I?`3#mm76UKZLjc7NG!ZXLUOfxfK@VVE1;2gqUTi?+n8n9l5?fbCP7b3_^|If1N#RQ!$7bCAeH&-)RfyNKsFjS5N!H3CZ!mOccZl5{BoLYXIJOTmcdR<L%R0bABaIul}D_l;w=`%wYCapvH;-rhfjDa<pgym4$Ja?8i}eU;|Ue73r8{3+LXNtRkJfx5rqZ(p4dgrWxFH`hU!;l!`8HmDY*Qo?&!?k)0r0K@(j<xxf%x6%dJEB+ftnvc`!#PaN0a{N`e!VC1$K^>cWo3j(N^mqIofcj?rq8@%l3L=p$1CQla<ga2I(re$FW)NfwLql9HN^z}yL}AipjSVk7$MD!SASWW<rY2X0+0Dho^1iS_-Fm0F+Yb3*)X6Q)d`r)H^#I2(J`O=m|gNZ#)hAVmHG-OAeR7WO54KA~CzIW~Y0Y}_?dgzl?3j}$H4nJGiDKFiK|9eQ=1;H{vf4uDWa1P+;AB;*AmX~Y2-#e*`A&~@_V!2VK)cwvytvD`EnVfY;NIk$HB`@v^u68Cx;?~f5>B>4RqdanKrO+5Zx^>Hj}bI;RC4iEVBahXCUd3LN)oK3JMmBggE?J##{04my}p|U+X^Lis6hdbo_fPRj-;!XW7_kx4<=hi-7OO>LY&<HEG(GStv1^=nz`qr+Z?e-2lX!tHXXj3q@@H$&EfKdDiZ=fn(aetd-W!Ol}LZJ}u9YL8Gy!%I^r%M(M?Sn1Kme4Xxy3*df&3;2;>11HfV7nSbmk4NY5t|~0I}+dtVW$X_I^xV8;+n7WmP#bw=6$#;EFi$aLEzZSJ6y2mN*u3}J={nI8<AL^*phw(mf4mF%z_aHs4#zorV^>)2H8_(N*Le}Zza<qv_72VwmA1drKI<46%^{gt5#8~az01xB<u=*CZ|*z2*8aYxm&h3SqysZN@*v29$S8b@?`UC&wuC}gPl!#Mk|*lDG6OSxn3fM>z<RZMUW^W{CtEK4yZKVNB)L@5{q*lO5bs%eZJJ`76Zv(^cUNzl9hA2D<^|{M_r!a29t_-$60|5mLiIQcs{zbDhWKG8pJgOX#S*SirffR#L*R2xg@}TFebEeBJVCQa5FO#tTwCi1SmmZ-F)RHYj@DvQavp94j?1i=tYX>!A9U>|9f0x(k##!+-)uCCFR#rDj7Y}nxPFes|ztzl-8pBu-lO#Yvra&Myf_V|9^&589&(9WaJV1=#+wz9e?+vIo$WcK%e~@RNU)%SyE4nD`qb3VKL<5TSmVQGsM-&jbLsJ2c0ejU@`alKOSL08JF(3-mX$i39Pg_p_B@h(H6OfWMK3M>Hx9aD}AfzQWcj@!`JPx{tYO08F!mLhL*8OW9&YiTFxj%^%-0p&y*}!4P9H&F;1mH6iL=taFI2uDd-Y|Y>^=+#jax+Oi5O;ri_TxYvqC$pJ}fOEA}3}o^sk;QQ8jBO1kU*91WcPz$M{QFQ<ahT%x9CvIq#pBFHY|-LgUx0k7a_uzDOZ*g>Re0+xkoHU|c`ANKbP@p#2HV)J@`<Tqbedv#G0_X4l%&1(hlqXT<lt<z+voq~z26-{`yNX0p=KiI_H7fsjUGtdOlOH!E5J=zlV4g&Kqigj>e&SRnq1>cEQVOFoUVW3?qQa%pf<zUH&As2rXH0QmmCo5+MW;+SYsx4Y|rCq2EEQ->-v|D9frv8YCwA$O-Nl5&l2hw6IWWTsgM+gp9h)n6}l#@DtrnBWrG>&wGam?*1r3uqd+GiK31HY3h5w?8-El-*f>z1Vc`%Yw&+<Sw`kmW{}+R43%gC}4q_u1tljp87FJf+m4+*LuN$E2@g+_T}D^7R7L?KgiQJ_@B=^jv$1Kg)Z7pweZu2F^~2{=_i!<~Cf?5=)ug;^{Or%-5B*{)OQge{@4-6OghYo(a2JMY_S~Nn2DZUbBDVD2q`bLY{bgeU-HX?|Xdg`D`G?S)HJzuSi!Zn`=7}INiDlLBiX>aq^$zVyqLIyC{2~0R@jBm8DEGx8RLJwR~}h7DGbT;mppkE{kiaU1!QNba0Qq9y4s4BtV&Z)frwUG*Vbb+q%rEC7g(hl*yrsI-ZxqGP!n4$_xD&iNOIiMd^7}but(8J8YR)m;<gh&Q<bNPNkA{OT^#9Bm|15ZWEqG?sfhui@Mes;QKfVG<?V6CzyrHD6ILp@cJnDY%@O=+=lbmC|;QM9kbPPyO*YLBT$QPCO86M(*!tWB?JetTaU8`E5VnbohR5AkT>|*#YEloF6xEpwkYd*yoReA+5DA?Jl+}#(NWissP{s!LW+;%j=D;1?(8PqFM%tvM@8re(C(;p>fBL+DoH%MnfV3v`aFno8pL|+r8&V6?D9JknLd-V%I=+ZQPR~{E>!qPd%Ky#r{uL!Uxb+}H6i#WzEdqt4|KH<45rAA<<B;TBu?YQ6neJwVr6Sx;_i!Z5a@VgH#5px3E?G%)~xc$K#5AN%TOdc<$<aTgq?Z)&G%)KPaftm)Kzvgc%3zpcDN8I{Fy91N0V#>zXWZUe0lNCfVO>br6g-N1Zj+IN{A4_#P^o@6VH1J*2m$~HaknFOOC*75dk9!y?=9EDgH{LRQJ>bMMA(Hy$0AFi+vi2K-V|De=WheCo=!Xgb1GdwmM6$4HB(7+2l>m<~+)nZ=1iSY>0;(Rg`POB?m`?ca=U?wP0{BTHS+8kei2WyioRA-`NDuM=#fpP^)}V$w!T}vm--d71gPc<HLe29<84?5_J*l=O-`g)96b2<jv-p@e`lMry&ZTqx+P4BL(zX-{Qp1k67Ef(y7xG6kennJb3a#Y)Dr2nx}AWB}^CR6I}3Bz1W70`m`GE4y8&{Pu;#PhV(N^?7^24>XK)zQQeI08){!|(_}lVBlo{)yW~plnzVJuON8%xt(s>nxw}!?$T>(XitBTR#71}a-7ZU<tcod^TJ2KTzK{d$TJ)PG?*4M)@x5MA!xbEBxeY$y6@f|2NuMKFUWI|CG+L^sF=jQM{U3cb6Sa%8{8a?^Em=)qsf6#e@hog14%+YFbUm6o`~DyP%Z7L{=n8RxWHA7?mRrdfo6}{|32^b^1NV<i9I({&(CgbB9>R89&m}G)ZxW39YTtm&79i=vF4E|+mTb9gzR$D>Z<#B$Z^Ul0IvBt1Tsn`vEaUn+L~`oqqx6t(qpWsp5P{<S4tp~UH-FaH12^Nr&0=a8N&CGSa-^bm<9Jm&U?dP(TKlb6!94i-{7&ks;*qh`A41F`eh&_Y{+m;W(Cz{bQryB`R)1r&=bOz6XF<xL1P`-td9rY&oXs{a_j|k}%=)J-e$+$Vd<^xHxN6QXY_XIsS<WR-gfq^+aaeB|lBLQ83h=ZyFnx;iZRx);xhhRP0oHq2`;2z%1(~dKD0k0o;qDkE1!Z`bVV4H}tGZ&_4bw%H_E~WD<{NK*k>OY?|3emvzRT)J_R%~Jm!GDJq$aMU%=5@0A(vnakwP%bC{^xpB2S(m93y2F2%S5tahP;{q?U2&rI`z#E3?*W`r#DyV}76Lad`_FY#EE2d*XnDU!F6ghFso(mQmB9Wn4Pkzrg#AdUA8?aT8!n^=kD!VLl8_t7)QMzmBi>W6KxH?yY9Xrz=EdTwUl=`OFc^0Fhc`o*A^krpNsWlvJj0wq*cMN1=@plTebr_Dkgu2cDg#Ll*$kGFMEF*04;YyUueJL*!D2n2Ck+$i6+6(PZ1E($@w{Sb$a<Fb`NhbEk11b2p=q8|%C6$omzN9^EK@!CuoPnhSLZBIB=<rOO7)$J6`(TM)ZEs_T>Xf$jX97oACCpbL}AKTS8QXT#@ZN@NYZN0bTrnc0Dpl^|wfw{3`6!C4g%Q|mtu{Ch4^xkw{Ab%Et}3wP9rjgRePAn8WuP}sB-)rtDW$(E*8ut;$pZEgd@yC8k@6;K<-=nSE}r*v<3{5Q!IgS5?~CtCZsqicrxv!|4pO*iI_3TpU%mZ=_g@OX*h3)59P_cGg%e&v}!Z2R%Qzol4k$t|5Ka<NpleF!ISj0mY|rQ<EjNZjqCc$Opv4^aEsb+jsK?9$p-JbRhd#a;n0CQcLl%HU3o!9QgL#TP_j19IUXuh7{a-|_jM364FAJaR-v+ZQk&45_xI5und@95#9ZMP>${e>oc^w9oziIVh`Sv)w=P1p(~hw$_tmiYB%_oyKQM@7Me62NX6ySXoLMY@_${wespjf4fyXtf`(&d?8Y(<Ri4cp+Wic*GHG99&>qEQR3+GpZoayVsNqwH!=cG8lC!46I+j7mM-VXM`@z=4rqUP{4x9}8x%n+hW7t!ypO*6Ai7iUqt6xckrbTjmTuQeg0waa6F>gfiaf_Rwrlg^4^hG$zfCb7aK$>@@+H*TMl*uaV+B8c;QnAjZUHP?8n*e1@?xzxbVoCkI!n2;F)9!Q3W=TXXL}2MR8va57@%|ClygM3epivN!fLOf^KpCxzrE(68yv>?<a+w%-+TM}=WTy{)G&*BC$C?8Ihj1nC262LN@9V2Ut2rrY~U`oMZ2y6XSw}<R&Hu2H%$$FT1boJek$Uzb|NA*eVU7-R<r&dHvam!Uw--fU;g&XpX>JL{poM;wR2o1LmAydfq#5za00c@q3Sm+@(B8LG)TVT{^Os2`RlL$@Aq%`?Vo`mJ3Khre}>+*BU&`Gdu}zSROr|g+1Z-X#-T`urlSStv{9Ji@vC-_s^7S&_MxcydCVn;pioZ_j06GTTwTj-%LSEPFY#04$*7|xi=IH#VdBCI<&0tV^ykm@$8YtO+Z_}zw`|e5$QD}N@SWG}@qMaJVaAkQ-=sK>c%1Y9``;fQ|M(h=^_IK(eLO9TziB_MVI5qyg`pwLl`tGCZ$;u>&K?|XCPP|V4HZab8;h$-gl!05Dj-1<=RWKF=X?&j`qG2|^dZ{fIeP8<pvT%;Tw`G+1^wKU+J?o6rO}DEE|3#XxC&?-!Gr0U$AkV!gbT=)Px9Pa)r${h%N}Zg$AHT<lO$Nc;r9#uMf;#VEv`Aa)z&sZYcQ;SeO+FIEo6OFuaw9FY^V(hO<S{edr@~Cp8>`6G}V)P8#)G&&22Dtep+zI*bVYFWhwW^_fNJIqBZw_OeOO?u;Zi5M9w{rSZ43dcR`|V2im-wf^^!Tw_QTv8jE)inC`_NIAsG2z8A8w06a%#Rt25yP?3<ljh*Uj7Z{?gBftca5D)5N%o1H%+ulDaEYn3X)OeCABRtEpr_EW}hE1fEM|*}hm|ZjaMfk<zzX}_!!r0vqb6HZNDWgZ}D0hCgcUIR-8<m0e>S#*9EE&S?HvU3~TJCl`z8$~!zsma=k(pQ0$dZG|T7wYVT_lDf(dv*|H0&!?^vzB@WQLnCUWzB!2#t;|Y&LhLdI^6HT<$Gwd6+hH_-O0yR<817BWxT4AKUSEb4yMc{86O<u`?LQ2#vSlP4%RzXR=8sCB{jaXXmKB%>X*aU7HdQ=8&=uhW&@`%j7Ov`EnMFIz%h#8T>iD!YO~;?@VUkkG7U?TJJhhfZ4Pl=X$hsv5O+LvRm>bHeD|GD5`Rxt@jx-tz-<)@K{w<Jq6p18f->~L2g^*3Uk_!OTIjFE?qlndoU(d1mOm8{g!e3IH=@H8*bgLNtSlHI1(BMm60(kAi?(0It?V0ekCT1!*sEFdvXX>_&5%;TU)(><E?R%sDS&v9V>4v)U5d%B5uE-^V!ga#uDSdAUGd~H7}KL1rO|9+{X6p;TEKD#-Zcp;6ya|e`y{%!$sp)@sPV^n58Dj7K>=SCA54ts<Mkxi9hVb{<iEfvaz6JIu0&~ZChcse`u2d8QL_CW4fszKZQxXEeSszUXH&0l1exn|I~0rgY~)i1=89HQ_0f!<*$76c+40bXro^_Kvo8MOKCLrxSS@}=MNQ(Xl?$&N$^UD_>6#{I|ks&>k%+_p1WW9>3sQ3i(8A8Hld|25j}9b!KO7M`=J?3sP3r`Df@L-Sx>}vyMVGNjiN}z!;*2Z!G{iEtn3>86?vEHjW-W2kC6P}c~GIF1h;9-a~pGwa*XIKYFBk&%+nQCru!3P9|mN)ah`4O`72FB#iUGy>e0@Uv5n@O5>6#Cd^_v+G-&RUP{1kYm*{Wt*%%h`1Fc+LQlT;vW^_H^bV~^rpq*R3oz&8ZY19~mn0N%wyG=X-tx+bl`c^vAupfW@`S&BgSxp4al%9Y8*^7c>y01@#91ZZ@)T;^o1N6H#nt6ULTZ*RR<Hi$DDTDDcZ5qNYgV4Vqwma(iZFGlZwg(kR6q!Y%+(tgx<Z-~nb4Hh!3q8)0OC;HoSH;nFpPRvG#`WT0;7F#-J!MWpQ<9fIYn57P+eos0HP&V^)3Ic#9eg(RKY#xG2WEoey-%tgB7KJ7<wN3Sa4IkMtWi>2sJuc^c)LU;H)t$Ib%S=9ur~8Ip1r%0$+5Ee94Epa1_IBsU;LeFR}nHy=SFcNC@Ll_Mp6qM;w7dEp@_?niaq0AEjL%|35?*t;zQ=QpvWka{k{&C-2p`bZF6_bMTPD2sP1~5Cx~#?Wx7!CGWA1Ju@!KDn>%wm$9&G0u6%irAqaoESmg0JS`N4fqj~@>K3^X_v>n{!9SD`uPJDU`99>%UO%oTr2o%gA7m4CU;Pne0j1k3Uv14)$XaK(0^V`zvUxF8QzPpyqE{+A@<|a6xMP%;pU=c1mx!V^-CzR?Hp#rG>T~B#T?R&Tw1VpLLmN$gtPP(<H+TfCH8@VFa;fl2I(vFG&(9{xLN4p319#<>aNNlDxZ%1z?f29G~IJa@+q9v|kVy1!!8+O@8**OTLh^1{U(rTPM0qW7};+M%#S89NhMPaj}y>pR(b+NSz+<XzVuFX8Vbz|(-uU)lDjNs&M))WN)l+MM`?yaNnct>2qvaY<EfsFwe`+N6gr{GLuRA@UgwrR`N0;}}y{N*eeBGd$l-alxCa_{Y<{ev=UL~?xx=mITMn>#kra0C5qbl?A!lIvT(U#$pCx-$6{KR|323kBE}LJB>DwKMxZ)o2y9=w0qk>r|1CTj^Nypxx|7Q+vLeC@{DQ(|R_zcgx+^1>(Zi`u_Evk$u;nJDie}B(!b+Zj#WpC#^h-B7RW*b@+!=ScPG@Gyl8qw(Lc5k74Nz&NWGSjfcm<REbkAl??r~M1J2QnTDxnkzC|v<uS>lv9oAw`;Y;TZVqZBjNqmrBkc!G0^bE%8FF7hgXE!}cq7H}MCQF4x3$Z*%ZCi;%u9{iG$^E$nT-lI+efU#jE76Pw$tf?Risdb&PWz)zI~?Ah*wN+LH^heiYj?#L3VEjzs5R%$^E^?;^Z`zjEycPU3Z)<>AO{hDSS@13%b&wFk~Ow1CSsbvJWhH1XWx~RfC$wP6Nz#38*IvxGKyQXRrT~4|naj98ab}FR@#{<gG@$%}L7+*TP}2^jFuN0WD;+OgYeCM|WLSqPx?9fsvevZ;KLc#G|;|ZVU+~xfK#vqgvJ8_LkoVE6v%WFKzUlyWpx?+c}>Q3m9(E3}fWRcdSRcDNt@Crsh~hf{(T<ehuf6>9>)MCh}v`Exk8Qv)v(fc89iq@Q3gjJe3ZA#3T|FVnd)gf#5%~Cir&LXPRVK#XXi_AkR#;(zWcK$7W}>ORVZwN3WHya`U_tcPr)b2$@gk`+Vxc>kx(k-^*d?^`~)}s{h%TD0H47^UVfsQeoYPQ&=2Ky)+}Fol%SxfNN6=cRB|lucbYVDh1|au)NzcmcW3TMi7u`Q`f(QC11|ZI$Az;i2p&eK#Z4AWzoQ$^kO=DF{`5&EOWnAmRL55wkw5Zv^LPeVU!;bpcX2!6TeAk=>%a%(1;ykDcoxm6bxtrzNF}?D0+Q;t&)+pF-`#bB;qF!AAA^v3XVqZsg<j$2Jz>229Yhd&UFeOU}mLnxI=TKrAezQiG?{BE6RDu5`(}vk9j1XMtpufu3Ru(rqoJJBsF087jqe!PX>cJcP?HKIMLUaL9GI<QxXV#RuV6MU#$gTNqb{0?lYIz%+u9O3fp-#=qt3MNL~dZ`8GfaRmH`4C7Ae4<tWsB=yR+97T_~drn1|N6!4YY_B7jvwsp0lF3UOiD%<-;Xkr=M0Qc2(NAgOz0K+RYwWf4l!2EGq5{B1+M$<T4#c_Da{jzs>USqUnx>UXh%vLK}eAyP%-!X8^nU=YumB91@@QT{Q4jO`lEi3YJ_<Aph)+w@+d`5(+2hi>%<L&cw>Oc1;@xozgBx{^k`*jOm2RKw9<w4vR8@r8#>U*kGdvFS(@wNmVr2a_z1M%Aln!o!ZiMvBi$*p>*WRD`8c0H}Pjx=L68yyyoV6$t|QYEJ2Y5|IbkV9G`RxTv|0{EYcWgRt$_B^(~{^h^ov)EbSgk|Qw`zy^HBYdMx_}m@BlI~yigz-o)@SR}bm1IsVv>rz{qo}0?A5}6r$a;c%6?_SJ9z1?{cw)AGsK?;VrUgi0<G%Q!4OXY!dfu26w4-IKY8id6x0Ju$r%eo>fkto1#nH2pc^0T$-4Q6V?)E7I1{i{lmbYwPa{Jld?Phxocp@-TIvdhuT;GAZ-2)^hJ}V2ipdYq_u3F_3JMUC{P21=n9-NJ+J)Hz4h4NY08ClH&?e5fr&^S~kj5%s;QM;!%P8N-^nelDdOa;<Z;x&dGNsm+0oR%XQm1VSiNZz`EoX5ghY}d)JjJ=RU5uy#ZocsKs*oD!G;kQh((ka^wLSx1hG~N%JU&9a#hBn?+CoVu)jB(u)HiqU4OP;N?{I)UDySkTq!c~=GZ3A!c91P!S`;ZuCt6C&^35QR<4;6mzi3_%UaS=2z^<wZVwoUuw>s$C+%O?o%1iZ|?U6p6(TEM0ecDVc_9QWz@3Ik3nk#}^W<jaddA~_W@m@-*5O%)H8J=cOt#m^7EIedJO#A<XkwCJ+0ORHDA`vTwBbg2t43DibC!#PQvZJS*-$iHFn2?AdkaLXi$`J9^asnV3Ul7~BKktcqm3LQ<(nCtq)s#GAM<Wv~c79I%%AtlfO%^Ut8nCW~QY;?dXif+r!-XC$lCUcgvgX7yajM%&gU{W=OGxkbVvg&rbMXdeT|MlX<bUSb0xhkgIZa^+jXuW!$zh)G$7S;0gc+0(eaOTw3Cm`9G7*QOz)_$8>;ka1ZHw=w0{UN$><ie&Liz6kaE3$gq2rOa*eBuy3A8ZB^De`J)<*pCJ>J9{S*M7oo_Oz|_ziaNh)Iki2qe#@}Yd!DV@{Ca~L5H^{JPVj+aSgV4x^)r-+m%aHwRVg^?6$;8`2Car=V$xt-+un>m*0Ns#qp!@Hh=x?pA%94<!7Gp^_P!0nJ&{~@P{jIT$F+NRp3-i-{TL>;(c*<k3L;=X?i+Nz5$k>r)xe<0&EvZPJBSv^p5c=DnC~`WbmG5?jK~6yTySN_i(PX$?e0IV18c!2BbY2F3;2;8#H!#ug0E~YRg(ODNe^c8HH;wAng~@phIrCD1mlwJq%%y&yXc*X>tQJa?jgVpmdNg4|@f71Wp<Ih0c}An3!4M!6hsAPK;`Z4GU=F@Lk)kV?C=i)<fjuRMvU+&GPT6s-{q@zAh^i`dT71+MCJUEA+OpHFCbVQEP4HO0I0V5V1O|POA*?${zdjUeh9Ke8^bT5T+yIUlts!XXloL@m$6-fqN=Sm|av|JsQ8dy8@o|jGj*q-7HQ`bBJS{L!2w!G}$>k9YyT`)G<v@hiGQ@_uf8?+rZqzc`w5gtK4i^XnTcsLSo@95|XRk1FVu^TLF!{6FslG*v2f&mYgefHVJxS!iRm=8Q4Fd7zTnB0IAGpr>5LK0kYAsfnd|OF)77Jyc?zc=9klKJG(kxwhVS^8q&4b{y+?Rsyt#X6>qU9uC-M-lLY{`KYYSdDJQ5iaaflB(@0b;8BeHqT{w!N)~4)LsG6OjiYP4L_rxx0F54wpFjT)X8@8rhOu^+xbw_9Rp3bx=muGkm&ebrmUTz)2-<Imc$b&gTfz#%pQxcq@EHPtUQx|qLcFc3m63vSlbc|M$jMtZ`M<1CIkP5v=hr7t5@pDcYNwQd+mz30W1m;d)1^IPx5F61~SJ9<zAR~_CJ#g!4QCV23POR^btkn8EpA+JDn=obiJT*%_#M#)hZaO=1LGpg503q@h=vLNdx3Dka^9j`&$gu&0VB@ZtB6MHPd8BCR&P*AK^;ve#>(Hz71aAc;bpV7aB5=s`A|WpjNh1!xC?1q?gszh>2lkgb#0!IDj^(Dw2*c;7&$+e3-w!@RlepK*cz=v2Bf;;_&~x=~XyWnjs*ht)n|q#Ca(KX}kINJ?$+KgX;%tI7sU#-NZHKut15nW(4VCTDnb#ZnINTxU2lR8y6>sWyxfdL)KezVzTB;QFghp7gjedyUF8EI!*SB^RZMS#eLBn_9L7RfHh1c1V0fgdDcmq}Oiu>CvE5k-&77B%M?+D7o;N3qOJzcVBXdi4*wuF{p(v|k+ZT1@)OD6++2HVvjx<o*Gi`Wz~+>roJ2s=fX)DdU)5Z8Q_w^SneHt)k-VF3XS4g$ws-r<5hSK@e;?BPZ#*oegP#Fq3Uu*|kZU>1xpK!y1uG?hpVH^`nUQ^Ej;cq^F>q4nV;x5c>!DkZ&VtDsN^UbTu^mGe1jCt+9kGdZQ&KmcwG$=$NO$zsrJS4unK^VsqelqZ{Cd;UY;80>7?Gg`ScNlECs$@LO3T=$%OErLW5;pZc?a6qN;KJqsNlvteeQ2LH5?enEhw-`tUqrcczm8_iGT{#)tJL>WTH<(n!JI)GhuoO`Y#PiXeRY~9h)gZ1RK=UUpQ{+alB95-G$|V8zgE66%6M1)eft#6`V6|D5CqM}T>*gyrS-XSQmg-@-cK{jDMlVu44>kf9``_allV*X=;BIS4FDbv4QpxC%)(mZ+SzU;!qO=y}huw}0St~bHGEz0_`TsMd%J{*)CL@p7N2e5&?D)GU&EdWm2KwyRpyFQ7%aVFpTrqQL4~roe-!l4jm?5rCZUl2<IOudK0E@ZT|M3V5%D8mL^>&qFN?@hc38hr1jJC)<Bm<*APzQ+RUg=v!m#VmQ8oq9i^>0A2%edS0F|>?L8e{kA)N)2Cs?Xr+c&22*YUtXEj&UjtqDZpFf{UzKO+l9!WQz<rDRv#pU`n!zHDyGkUMm;8_)L3MSh4r$^_0`*iqdv~R?=Pf=V;*U2QCShdN~!0<`OkElSM!%7D09y@0Jys2zUiYgVp1R!44u#6R<2yvpF!h{jk4Zh{r3o5u4ZhBft5&+N+D2xEFY3Z(b{aA05~eYn>)T?G#LGt!TotMJmo|{lO;ozG%7*pMfTbUXsFe?$MT@cMzC|QLKX#a~=~_DELma3bT5(4Fl~`k@9i)E(c3K47vEDpgHedJy|(BFxyFBR&CL$EA2vUU{RFrrQIs?GWAD9q}ATuPD0`bJ&+b#A^XK`Izn);LS#x$r<~OJGo3A0qH&}fjAL$BDNUGu(muOL9r&G8iLmVxXnE3<Shpng-*+OL<lY-hhAcO-)K2bA96SL_xz8>aX%q+X<0+*U<*o`EJtln}<DL!Il&=?{Zol~h@lhz{qUYL6{8`=u1eGqMHE?!H^e2X)H@D%EmRQQ{7Eh<4VZN@c^)C$1_@f&tn}C!J@l4p&D$)%;PuikV@tXY;M_G&l5%R>_>#M9Cc;Dk=&u0TE&guj$eMP!T*<9O+!0Faa2ol}~j+6f!7h|2!+(p^@3@CU6sVrrhxdm?&s^yD2v=|by4rg|Tby-|X?K)GIp@Vz;^_XGXBmv6QtIqH;p^?He+SX-OE#X95q)ZN7)bYF=mdUkaQeNoKNDL0BDN4_)s*|~x-(kzd!W?k5ajufDaw?UqTO$4*CLvHfb(`=ka<B7OS=6=80N=+^py4|fKfx?qMq$m*h1W;HXPf!4;5MAcM)AV5@0hKY+r2b}8-ZGUGr<u6n<l_1D<L?D-FlooSP8xa?L5K0fV{!aE+*=xcTq1)w?$dk<278}$mXw9<nh)}h>p63M7<Y+6;ga8chpsCb7wc<ehFNWJt{&+fObc%Q|FEnR7v95&CD;T*XKc$(;(JkFU<*tV3*&S$n=?<Rd(;Ri;}Lsa-qUU+S|<>J|(Y>`XbC+sR_Y1@ttaEdZ4R?U@%2?EPu8!Byk!arqHvc7b{!q5_eyOgFwd{yO~kmN(e78v}To021-<FU4|mrDGyX#AneTRZ@w>^eDW}lp{}x{!RxG%w8Mo!;m>68Ihtf6_$6q&<jae92DI&iD<xUGAxL9vQ$mCYCcd}KpLpI=us#l-w%J)aU2+6wiwGD==>41PO7T|`rMjmkC=vqp=rzFZSnShC1iHTI{c8!%J(2l8CPeVux7As4ZIEcy$tG`dHs?{seB1mrWkWpVsG?jGE;%?FysPxFss)34(dr&#g4{f0<At){`pzbJK6<%+gj(f`N<M0&ogEnxtEf(m93K{J@o4?Dk*JGUKR<a{pGH^GCvP^-jGy>4J`GX$9NnkX8!4dA`W7d4e#F|=l}??mpztEq;K7p@VnedB*F1%5D`C1gpWuS8>cuu})Th;OcPLewdg}IVF{GbSVh_HYP?tPwjp}A}-%$H%n<m>?9l8Ha+a*_W*QBjOULt(oYt=ks$=!|8M$SQEQCy!hBsRLU?{-<@WK~ST)M}Ty_Jtg1*P`Dnarc)SkMH%08m{12%Wd!puLw+HPWl|d@+u58rO{G7jWMh7?EmPinW$Zy<*y>RZ^>!`OC@}#jb~vCanODTr|Z$&+4ukOUpB;xL05<iB#QyCwcJX^*qkntPJoLSAGm*H;((>DhhE?A@DR4+dM<GZd6Qt&SNjHJwg5>Vc9BMpwPed}^L?g8c*|U|eIs_0)xr36=hAuXWf|AsA(B%+AEk$U8)da)g9sGoci5X@xcRfj9=I6~ZWdF+NZRkskRuhf8^^2K0V9FP(%Nsm3g*Gr=XX+96_1Ri{t#jo@q2JE^xvF1gmxEjkm45hvicjFJ>P6rI15q^C3u*H%aesG<!rWbx!>a*Vb(uw@uME<=3}Ur#8q>CVT+}7$#O1vBAjvljl+7&kStX$P=Kesf$3A6Z%hA;$yI6U39#PF+Gn(5FUVw_L%Dly3wOsTDJa9c47)V&U)2@cZkR5rw9kUGH{W>kiwwtF`5&@S^j%g*vXAC*xcoF#BsFm*Wu8Y43AqGYh!lcZMyYa-6M6Ck;TS2aK<M0Ajl-ntBejfEFU?%|T$#02(+{VpAM^V}kIP%gV9QwC+!F^J{PLU`HRSRRw2Yb-E#uPR{srD|)RUWAkDCBvs#mM;3G-oaT1^x6`gMH0A6vdqc5gL9K3yRy<LW|}%4d#P28h%m^UR<PHa+f7prkT|vn>O7Itp!+n1qt_wO=ZSIPmN=9l8LRmbqebw1#CG-F2R;7$TQC#7r!lNA~Tpj3(PQmA*Du!UD9?fO)|3nLCa9n7bK;+*sdjN8YcH^yo(M3-+2W(OjrQ5E*}+EL}EWKAz?W*n-&QQC*+34{Yb>yy#3C16`O@{%N{dJsUnRQzC2NJ)%s|&&&>-tOPL=yKO_n3eKvCm|FjN;NNqR%0(K{sS7N(Tezb}Y<z4V14%bJhr*_%s7}-`PPR0)f<=n+XmcAF-UaEKuYlSxMrR1+J*9iQ<G)F!7^H0;J<;079bGfjpFO3-Y`QUbR8YhBvrP4{gU3r0Uzo1axtH07^efK<V%v}Z{Vm0UOK#~@k&C6W?L#<uV?;<zD;;lHM&fQC#j_+ac!1j1uA@~^W0%&x;@QirF7^t5F>#vUR|a=#4E`x2D83*H8;}eCc!kdX_>Ry2OmOT`<dGvX+P;AKU`VwsjR1YN<FL^SC^9qn{L9%Wp?&W6&p}xwo9+IQF9={4x3!)mQ#7&d=`=o5dcWRhKcKJy!pc(8U>m)kua#FP`rEDAVNLaH;tP>NB_E;n4GqelzdpJ=^_a`UiV{bc|J=vt7lV^kxRDWf(&*HWn%H{uvUE95K1vg{cR>5Y<B#D-*`NqoF|_|*<9+ni2hp8+AAPQnkEGyKw{*K+5~Q_ZnE3I(R^&Opv0a-Ne~1$9_-%^ufGgJFmM@{!HkuKX9xM3q1NR3LatmPD(y+~6loxBop*xzP)LF`%jZuLhP)O{2KigaAqnc9c#Q>fArko?P^}C9E6;^u<osZ)q`0X_h-QY0BC)d+A|K8i*KX3ozqlPNXv;-Ot8VnirWRiK9WeHU$P5h&g3%zzgv|-U4f-h5j@~j6+o)5EV_fSPr04R<4r{)(&n$2O}x=lEd>ibetcFmBjpL_u~k+h?uzR|H#D%<cDF6(nJvD&IJ_u-)?{yl8}^>M%d^7p^|?Uz6A!2kaE_{RfH9m?REKr`bwnyv~2|3hT){n^6M#1>6GNch#C7GKe6!2lr44V5=|b3o{A1YYYDT3`+vPc1|PKl`=mIrH#8{`r@`{`&uZU$DRZlW0gI%Z;J3?yf(L`{zBsBieR6_?VCBchhsBVs|JDrhJn1$_9v;cYE%gYE3E=?*!Wvtt`xf5Qmj&vtKs@w+QF3q>M<PR=e$4$qvYNLA3G|!3|+7>uSYT*4kjFQ)9|th}$~Q`Sn^ibZ}3Cw4XUR8`^S7;SsfreP;atjsZJAgf*?npTy)(Py+cfnG}|7is@AAAo_J1#)u5Uuq5QOCMVabReOB9G?WAw<0L}2c8=?+=<?k$(RT-*`{fNDnQxrm^$pGGo7>HNmwB(i%Y^D-QPqSqrBgBy&2uBxTdtB#M|P|G6QT=v9b5{e%Rz2wMd5dkZb=dDs#((us=FV2@zhuBgM5{u2GH=Ny_X(=<$wOXf1N+;EEbs3MCTe8Gxt!m82mcv`7o@-&UE?}eE@{|*du?8Fhx#QrBw)ePP1vS_(c@ETBS%{@3^Dst8ZZoV~seSa<-WapA1XZ%@3LR@)E@M=6M^1@*JrMcIEE(g2E9ru@zm#+s&umM{8cvS*;62PWLvv3n5YA>Q_prtqm1c#2hx;fS*!+nN=HL#mQ&hHu-*D)uwb+QQTHuP3vs?aYa$N6Cc+RpBn^kDh{C~b1AdYf2waw-m^>;pmAR7dhS#R!K~tJAfv+G!SHO~Zs`^upnHE5MY>9|ji29JnZu^OH&HVbeDUy(C^nZ~eI-LYY?hA(2}?DPIg||<cSGJ>CrGDkO5u-0cp_a|xui0aBq$+c=4<>B2`A{h7%TeGdCNS!3VF!Z{JF5n^m2&L)ox#ga7o2>U^40aBBonJ5u8|HS7i)$br7?LG82r@y$>7=o7)EJV)b}yza|SmcPT8uh-HC;H2Q=>3*S1AjgjWN@tbwLspFl-Br39@{}Y8uZXSNTsoNn@=b=@^v<XD2(lX8{BaJ-XY^!f(x6xuf!OYbXyJlsNH$Sf(VFxTK@*TU`CgjUxzEGEu3M1}m?&;AYNq6ERI!1#=`EENNfh$s}ZvD6j2s$Av@X=l&B!|uQUA4J2L|g_kiuTaD3=V>$t()!DbI+HNpuvW@P<MOtb6Xt3js;;G4!uT6%T;D(ro3KGD2(36K{2V|cQpvibEJ-wj_5siiTpmDJs9nx?=&6TvmilE^k~#%2i!EM2C6G3F?%#Z0Y~gp{c(YrRj>&B%yASbjYF}Al|ToMT7z(y>$1a5YxlFY3pK`?GNk2ql}to2(&H>xbNSUz5<55(leA}3J5YzB<FF;j&y2xFSjhl+I36otzbUd6xSm1vnz%9Cis!QtBjfqbIU=2HW8F5@N~yi5JH~P7%LDRM4?9BhM*rtl8OQwllGoXUp!e(4HSc9-P$!oIz^VXK^7L!`23F+U#|B84hML)|aL>rl#*g@TQyBLoY~5l%aKJp#wHAV2pcQMLOyaF16PY}kv0YtE(nwGF+W1uA>a9KQee@D0+#^qMRu{r;@^tfqJut$c2`tGYvV7w-_+CcD|B<R!B>#V$Y+6+hlbeiBxGAPiz7@q1c-3`bs6|%P+(}I)IT#j?ws(Dg6O_ENmL7dH;V3r&)^k*W6isQ#`&6cwg{TX~>C@WFSLS6Q%+$3PV>}vb>uLeJ0d=If!|Kwk%h^&py>70*o+EL-Wirg~ie*uXcbo^8shs+Oh8AdXy|ihxjZ_#nkb0G8V(tXmJNx9QbR5>EuRK=x(Xu&F9mFM9qn~I%!ubeCOG^jFYE$(x<pG$>^U>BNQ+`!FmGS?_EwY@Qk4CQctJKESgW}sHIJS}zl|uc&)%f`9&%f8)4(7cfoP}B#iSbu3;p5RH0m9C^od^UCWKJV8G;4>inJnJ7&mNSU-2?QEsKG3|30n)PPjx1bb>>SlA8=mAVw4<1ZM-`vTRb4-NavI5^|V=&qr$X{tSkaF_YKnncNY9h^bc6cKo5b`<M8Nio^%&8znh*gDb&{($mjyduM>OMr|`8J+9+-NLySt-!KAnFqfbVmGy0}7j6#IvNs5p4Rng<K`3s>hhSnl&(2n@>am`9lBK->xc*RZ_!I4W+$D*QEu*jS|x#vNlHW1;Q9L?X%pc`#pl9TxQ^R^@H4Igcqn6hxR-X<u*r+EW}wyh_*z$EKrvH6JjA=+lANx?M$ItaZ`wXB!Hrv^~Rf_A62FHq&c<T9tKcW7mD0M~XX6yg+?@L*~YoOUlpt9hC7A`JSg&#m{LKY#us$!STR`t57uc1}Tu72C^W2Blc1i&f>H5fJt?TvR!c@U324-ora^uf`OM@CcVBuem6$S0#ArQB7-;*NH`;s#~jT_r<Eff+Jos!y^J?uKAnG3-S4zEQdqe|B;oIj>~SVQ*uK0#EXZ^s9hHz@(x^#-L)pli<;_!_C*rRx1*R$&FU%(kG7jiuF94nP4oR-{y~opjJE3}Eig`tLkrpV)q|}v%0PYS-BCiTAg7Ybpt=^^Y=gE5S1+#EVTy><lA|%=T3lT_xu>#4pZm@{HAjoe_OLzGan<tum82G|Yo~pSU>p#{fv2X!B5N+PvTp9m63I7pzfw;ZO*^t@NS4{4m1jvMQ7}jTqa(S_HswPVIVHh%0v0mkjx@KFyOt_<5VDqft8SX@X3Dh-#-U?nFJjej!2&h8Nu*TFH9;neY_e;mVG2sM%&2&X^5!DHfuP;9yUf6K0YDD)D)ZTNEmW0TQpG;6S{w*qi?%T>A>Y{(vABSwLWu}g=Fzb7))gnaN&2VAwp&QrTWvQUZKo!Vf8Z_&8^`6l_)?o9C96^zCODR%_Egp_ptRYGG-7FX4600KSvNp(3uxdVD8O(~UXhb2!P|&4^0YM8(bzG?4sPEgUuT?Pi-M5_eXb`D46iIY)xuxY=;ZY)C!5B1G-vK}B$p2gB$<#zK+wJ-RwI>uQ2Zlq7-+`w&Fjnz?BfQmMzs)UVd-j6g4Yqh(kqV`Un8O-JVKUdQ55aS(d4~HfZYr)y`X7H*FT#v-EMhVMgk>^h}s!J!7<6xZRpc$(D;J9(sJcd$)j?*jh%pHRvpCFWV{3>SCvV{j#PIm>MoL@oAc{a-XMSaZ@S6rTm(AZ%H>rWS3X9oG(6P7OfOfDNnSdgl|Q&=#6#0<wKZ#~A#G^v#Q2dV#B|#(EyCD1f!xiY6?@;x0!dvv{%gbXaFB-E)y0Jte%vBaubc&$Q{~^ns#tg0TxuYw<%c|4H@-0hp57bzPQ#S6yC{ju#fgH*f+lh_R$0?C!nGrC3d3WtKT6L#8r=Kd!_a8Za<$wIwb1h4i$+t|4m+r~(Ia%}plR6b;!Cb?B6Gl?mV`%(_B<K@E>NhTVb<Bn=Tc?7lBq?>%n(_)_S~h85@EDALl@V@ZVh=5rk3kC+B6oLNMu>hP|vTyw`rVw@)Rcs1I>ts<}jf)CO_3{p;NNYnZqcD{^1JLyQ8qN*uI+i+_LW+Vw=j>%~xJ9)P*Gs|Lx!-d^1aX7{&-gTa+wq={Y}TU1HR+jKsisR|R7fd&)I-d1|r<B^=i2=B_@H|AF@~vs1`jT+`q#M6^RZl(ZF=(Cu8+hCkXlzGI0(k1Vp&h-@Kze@&CE74dyusme(0pLl`#j+gXQwu~{2kt-c8pqCTXt})9@RJBL@0|U$IQ~oV6d=(#0Yfmtbggr2GixSE_{E7W$o<HN|Xjq$0ZLXII4sJe}*8I*hSj-WwYWH?FcXu%gkQHVn2svdbQ_tdjmd`eY59Z?m3l^qW>Q35T46ltHI_(MZvK28}54b6EVMjM=&&=cV^<|PU;b8z6XwsDDqrP$pO0Z&?RZqJv!Uy3z+t>%mT+`GHstlkQ8dGIy6U=2N-@1EYO5_uCWbrFFTBIgb@_=6v@w;};Yv5XJmppHITjK?~y>)?#P=!VPM|<{fSeR0eulPTaXHqYjd#W64yk(1~*n&HZii_<`l)+uFG!TRMtx>JP-B)F_7cg_}CU`AR@P;e7Ocz#i#!R9IG%%3a%BaP2j`L~@YYVcJ%w{UZ=GxOzqlD<qHj|EP%i_MQf%!(WMAc4WI2GMWtF0bOpjS4y%!;#w1G{zdnfP@HB6nKe6jzd*%5Eq3O(Y=!DX=_0Fe056Ug$<+1M_!b1GU)+f-y=W^DnsXkhpDFc8(M-SmN&WxQoI;n8Yhr)Wp<W(P^3N>@q9Z;m!|iu;;n<BrT|ZbM(ZI%pf?^+WctZ`YcW!T@PYft^{s=szZ>bqYjSQZk;#yk_h9Ti6~#a&sCYQIwHy~;*Qv19#|USNy5{BVyEbA#>_LvmGeoo+TxrV+a;(QB)|;{TTF|*WEEZ^*@)QIrB*PVT;BMRqz<ZhBGy~FLT7Sw=&J1o@)ONb!mNZ*fT(jKWYrjP?mDK{IP>hKgm`)h=VIP<>Rs|rWBR;0)VhaqR;2%Rxc;<fvz<WK-qd#F0TvP1#A%txYTeaj@OW8mMs`nHVi-w`gtdqlW4AeNwrk?;yLLu^lpVsH8i{Lbc>Y=UsEX@z0XE#T*!nSXPdzs3-hmET)MiE{k@8-)9k<)Ha_N-7M+0+(A+-x;8(i@}qr!p~v(Ys!%Wb?|{aj^<=$%6ky%37sCbz~4`=Y#5B~xt)gEQypyUlrU<}gSu-v!HTc3CCcc7R7{l-Xg_s(p3{*&_GS7g|SL!1Wk{#T^3F&ahK7SmLAr%d+Zd{HhQTR_Y~@xFF>?bc%o5GT!QKYBJ0<v^^q6YJ4E>9fRl>ZtcDN69c>(x(7~%#wk9+uQffqj`pcMq`0juammvU&vB7!HdsY5m19R#xFdY+D`y|3wsKPOV34JeWmh%Vgaj&$*?~@EDoRE02zWEG*J`j{2#u<8`=CP&R_b%2`qO&$=~kPAx0XTBmpA5#K<|b}H3La}G!A%7eBdfXV3gO6nqB@Hd{1p-&}`$jgXsuT2qC%wBOJZg`()a8T>w1fp^)>M9hG!t2O%O#tjssXC=D<scUe=We^gzo8@Zovb{WMy%FAoM`E-<M7tEDQ37ZRU2q8>`Df>EGW_G?|so;w*;V7*mm}@ty)5Z2y6d2F9xnrQsrv}jpQWvzNWwN9@MuPh>vNmt-Z|NNSZ?4==P{!Y~bRv70iW>;2`9S$*cJ%CLH`dHcfMV+uNaH^R<yz+3)=}H!PsrrE5R>_~_lR5=kG_??Gzy`-fki0%d4)x$u%FU^B}c0fo{yT~-7bz{a0z*=7zf``6xq=&?BTVx*8&cX3HZSZSsyK%x{VUNM-absyzl`ud-jnUAAcca`yZ*)6Y~T8I+Q<qV)(bTP+JrRJpU{L0s1O&pGn&61!e#Yx~La7YcymY)=t3|SU2sC7m76fQn6pA(>df@0vLhid~49*iL~;%W;%TQQ|U3x=9{(03_KC#PNi$hi9*}OW%<l7!52C`Sh*~4zy^2DIP@8X2y33_al+?|TK!tCFpp#EF&dIdWz?AR4oL@*mER2E51LC8<aq^au+Lg_)-E#&#Uliz*0LeTIXaqHdfiW%z0ln$1{zn?kihG3hK-eZ3}`+++o)C)SW9$@<l<pp?UK(3G+Ag~6ElgpHlE{x&3BVEzuCM-K)m2~z>H=WFiXJD?;4Z3;a!>z#M?b;IsV`^e^e-)r(5TiZT&*YG6DP5B6|=J;RH#h4uj9EnMjhE(k_$fqR;0MpxnL-IGL_leI^7y2wV%H6?TFvQpsraTGcH8HxF3tKxaUDn?qBulgK<3+ot#<OkgR~7KU(!!68`t%eNajwXI1Ge3&Vj)?B_Yp)01DHDO#M!P#l^!5Ae$0t62$Q>Eo@^R(yf`Va-h&xyT0dzDTvrWwrhE$^cS0STffr0Q5B&o>Y6-FkM#dLA<2QJ3C7@iTE&`AoNxQABLhseG1D%Jyb*HwBHdZFL6C>?he|^E~H$E?*JSxbQ2_CYtF_I`ZYcwwTm4o0*NOy<()E=fyWDPRV;X`z+%3k(&*)eRX#L=ju?hY+~7GWDxVbxjTUS|I$hmpg$bVmvrTM-rsv!umVxE>N&?`!;`1jNl~APAT*EBWe_5P?m<*}1F@ng;?2lc1;?=BI#YH(MmJ8O(6M)CH4$0O41yEmV^t5FuyP*iDEt$*(2}@jj7ywu{b;b2`Zs6bS?12n9m8%}Cs6HP8+Iw>Lh+Zp9I3O!>(SQbEfCRn)j^$$Z6I6O#`ri9BjQ-LvxNhOSa<~Rq%j_aEgxxcK@s~0jrUBOoiT#!vgg~}qDAbFn5;K!)^f`?t3|$PvpN$kagzs~1rJOivI$sOpvGzL=+hv(X!bF+g;~BO!{NoCLxEQ$4=UM<!ZL)jTR+QuGhQ+6=HkU4E}FwdQNdFDHH26}zB^o!DFB+fBo+#;w8F3ixxjmc^YgO$Tx^^F!+;czYc7+Y%jWRpUhn|&3S{Q$mx$-t9lP7gCh$1T5ZCa=7jb;BPuE*w@l(43uI@0F6=>X$Is{qD8?O>@(S{%?Xx?bgI5bT#*<{L)!5K&?BL&JpwKgG!79=eci!WN8v*vL;uYk7gQ2NZgZGTW#TF}IVY?Lq^Y{&EKMBh~+ye&tg-B1WrXil9jmT%=8gfNc{Hy53&%^eL>tuBk*#70ioqw*JG1}C7Gqq7UC>5W<N$M4wr^r&ox9Oo8TXc?2r+CPQor^H5TXQ57PWc)5{WK(dh@ReOM;7I%l-AbeuAZd+<Uy+ky49aL%a;2sa%xweH0d#?%f)?3ix0g8p$X+r23N6)hG;{Ww*$kwzIJfIdf);;{0BCR#n<GXM>~g~N$`^F(h(c3&54E`q&Q(V16K9JcQenE<xNn8Zi%6v`T#Ih$l;1|H1h|V{kB&vr6JXilJCg8GVYCI%bcMZ2PeQa~LlO#$jOufzZEWRK<asTr0G*eHphblFT!8jVc$OSBJfZH>hT4!o7c%?wkc$DLeH2HiOO^?CiBp8btl0|p0y~*1XQcL+#o-gtE2=GJly+sCWKNx=5q^jWDKS3*8F)AA%-kd;VfRHZQR<1;9$<)l?}|i@rZ2X6u_Y9Zt_t<+h(R+j+-v`t1X2Lrx)#=+(PdScBQeieKLZg-VnVBFORCfE&Pe7$^+o$`mj)5(i4XH&HHwG3Te;k1ku(0n>ETZk_J$@UmfO%#zuPP<YU7<(udGtrCjnXsTJ*EJ!BWasi)_NKGrVEuvyZl=uYCaZ{h*_sS7c(?&K}I~1C6vX%LVwT+|-rK86?~hB_@-67hJR&Jznewt)=K;#$Dmd1sqSSOIOTd`hpLuTekI44p9vju1oPvbTwF2Dnq7>l}*Y<B3l&MX!>x=Jlr_$<cN-9q72Eglwoi;68C229CP;m%sMcX!R7=r>wRgvlUTleh74usqycAkTNI)&$w+Pi^%8nbrv}O)xPQ22>SZW)iX}E*VwO$dfD9|9+bcvt$e6qyL8hFUkvd1?^^gOKsno_=(?MDo_x3CS=33A;9~xq8#qw~%dJxOJ#H;3Hc*Gpd-R($<N@tml4ki1Q+`ClvOF&dFL^VVho2Q~=t>sH)(bR6)7E5(n1t7<G@);ar_hU@$;~;dS0yR$4{91pHP5aU5{9DG!*D}J;dr90=z$k$Z!=K&Lfi-u!DdU{Tl4f1W>6SjHr}GswDk}=UOh|)lpWv%i@yfV#XGeXes;Bqm>9R0d8CM&~4Ap^<YL^Cgi~>x@=<ny~Z~v#+J!SOuGqBdVCw1yZV_r^~iE8;?V49@`wuT`bgz09#zn_pvgj;#U^n3hj4>!Ry*hdl3FqwiZ4C!!p`=gn;tC>bnImkFq?}@^(Y0CNHfanTdXs#TDiSv&Z&c3K3QK1BnEX}SMVAE9IbNh2{3tj8cdwyEn2Qf1RcJ%Y<`r@Fm{WK@vEY&kc&X{$SDIqJpx>h}nXSf{p#7YHA&wZ%U7h)2IkycG$36tEr8x_6NY5GJdl8#OyvF@8PvqUx%RR;UCGHjwc7O}agOOdY61==<xRyZ(}cn%vevc>44?Ms3g*8{CWkq%7M;6sC-Dc_WMluP$Q_Lxt)IuQ(L+Ap$CnZ>RMb#|bMbVW+erNVg)pU#G_t_>!sxQxj>?ARbGBPM4#+Pqy^<ne{4fs^`!?d7p|@&*AVf?L$F$uZqo+5s=pCl~^6)BkVo?RFf=k)+WVs*Cvlx$NCe^bRmHHJI&zt`7D|zIQ*}l@Uq>X>MlDQ0**G7lKMDkqjs4Zf<U#(pGU{5W8|{p8FdLFgJ)dj*jtH(0z>crbuv2!npp>@*X&3Zqf>7%IF?u?+$Nr1^%g6JJmbRem-cTInT2z>2EEc@b+rgJB&x?rL9p#Ykd|In~ev#Hb7F33vB;QrR9BJ+3q$l@<hPAwQ!JV$&FpYr8I#-sv{0n=Dm#`!NV(GPxgGkQvAi8(9*r3FBhp>KnGK@k}C4Hm%gEBuu8}Xsg49PkxXVTgRO{*v^nxEleh?z5EnVdJi0QVibqD9cWjbmlhrYOF8cHiJy5H2CL;tHI!Ivg=NvqZ%m&;^LB)bB8El4o7IhCZEb_T+H4eo>2AJ4s%M}+wN1p@a+t?i?4;bR3)qWCNDQ0mQ3fFzN%0M{8A98Vk@$V|;Nt}Q604P}6rVle0>P3vrB$i3rI`s;LeGu5K&^U^1TVW3BI#B;FJDU$3XTlY7NRFxFF@b0RK0Sg2F<QYf+Og5v8JGDR7ujdkjbV<b&_JpyY9uj(13*Z5+mnsaU6$rT9jQ$x##YqLs>B2YlP}KI*MD6=lJj0tN=iu}q5)JXwUPpj7YNEy=)uy>9l}B(<I7~zqB&xqfYPddh?i(9f`G5wF<O?W6SR<%A%7NLUh=*Lt|Wj(US41k6bGr$_``W&ZNC1l^cR?nWM0H2M0_fpC1?Ud{34|z`Jg!%0>Od7%c@a_I}(dH+$GFxV?wF~JZC2PE8N}I5OtdzduS@OWs=r_Dnb_Dp3Lmq2MaB71|F$WwA3O4n^HMZzzY%WenhX9Yd5|fe~%mVZENnlA<1*tH!$*g$!DTe!nXO=Bad?}X2z;Dcx}!x+&$B37Zn2HIn)J0GWQwjnGmmd<pI>*wH-^My4Zt1INd&ZChdK~s$u{iZ0^XOfa$esInTRP_O+QTtOk~$G*&yfW3*$+!)>eDe%P>OZbuioNYqr!7R{pE?%eAo%g{aD_c?P0K^s2as(3tXt1>V!4G<TSNLY#_N*rPRGOO1TSdHR_v$v?~D<kdHc7aTkpBf-Ad|x#wl)#c?HDC82#GiI0_3L$&YSNvNg}SFv)b%R|OKs_RxJtiuxP#3sg=kT2p)Y$I0VGCCpa7N8G@rR?LW5r#!30SO6(vQascdyA)Q9K@S>X=p(m|C$!*NZ%;+B6C6HzPO&XtxXff*Q?Q5Q*Qgi@$}nsQM8SfYP^|GGYwLP_Yn3yzN|ctu5%E~82}V_FJrA$CpFF;yKVdzy<{@L?&Gg=pUc5p>mVFcV>t6f*4$oyIVn#vr502Sg06Cezll<6H#Z$mRSI+rInGe>_}5=)+Huf+dN-X%UZA)9G`>46gSR112vc*R>7)=v6ogem=ct(1uPBxYJK$Y}GxX8wZqrWwqJ;DNJsZFJMGUBV*-qY<nMLH11tSl{H(5i#prz7U-A6EpUEw9e_9S`fsxZD|=XzhYXJ^U+f#xP=xdr!fV`Y-G#>g$=(<W@UfcxrhI2Qu?uolLg^2$^ckQ!jB4<l*fD`!_6=Iq4QRO{jEN{7*5^ov&ex@h%UJP$VstM8A?>|U=o_`Tdy4EM?ud*d;;VbD!LB&rgF#lD#u*xU08p=khCAFZyZ|BR_87)iZmTU2PGKM6YJi#}rv9=FcV&7Huw;D;5oZ}@*O!o@AZE*I<&Rzt$uZ*6%$Ygbm8wj=j;8tR%@hmb3~a(rGg;j+Q<@&h&;nPqd<)zFn_D}ZaOQmxIXdP*=6@;lj4YWP1(f8}cH{OMOQAE=B94RLD;gRLg)&Ere;IqfPcqlycZ&@eQNnfy#=*7UTxTw6!cxCC#2{=mXdG?zRl2p9Y7`iy0YL!snHtTWsqe5P9i6*r^0S?}bDKGEaz6nOe4|*J^lN-z#}6h2!=)J#Pl_N>d*uy)m{}$ILoZ_jgJzuFbdR@0WmdJyN(hMu#*8s5Sp7A(B!-=&^ig9;o6V*2gp%#;o76vwmr5zz#DcvL?zGBpYC*<Jk;PJ|BC$j>+LypbFD}#<IOj7bZn*CDhLE~R^lYg8ANIsp*<*;-B!rRFeWkpcJ2hr(iRVV^XGW~jwfKbK^`ZIWv`|k%sAb)2ouRG#VW3@OoTjU-CPTrLx@t@SGUX-VRCz?eOFy4Wu5Pd*P!HQ@)E@(Hq0B2SL#nuQnhmp6X!$FC{_)#ypTF_>j}(Rtfp`x3&0{fj(Jec(Wa%FbP<)j1vO@KBRQF(b{p1vUvaddQF3LLEs?-S`WV_e7)q6EW)cQL0(!IR(<(X8r64tOSl8<bQ;-0tpWyoFE1)URVpAL6_p?baJCyPb-@%Az0u|<a$3TYox{;`kG9|q?vm@9A9oS9T{oJ{8|W$_N&*1!Jq`#*vkp?>lFF#IaJPad)uI{&ZrKIXdGg@caFc~S<fcqrpoj&uXZ5ro9e^Pl7HpKG#qdtzg|Vg~*a`Mq>6!f>C<a}<QGedne=7|st)t>;@$3x2-fm49%-@o{_Il;z`_&M6im4WGkM#T7~eh$(DCXzTNL&64RC8;&NKSfF#?%;$=1?S=i%r&xrR$MF%odrvemIE?Yh_43Pq%=VA(>$^X{tDl56{QK(te=Kr8%}L3`Au0_BoE^IoytI^afV<ci7N4U2KMP3i=T6h=UMy*e6ayt_Risu}H<6BQFBn%nc{zWCk-t7Km|y<>m%sh;!*IVpUOp2DQXG$C9^8hoe|~Fl1l9gf@s6ROF`NUEPTYU|>o0%(^?&~Oh2Q^G<*(`iJWr1L&yZs~AfuVwgR45GLOGO=AZcyZGWD}mNjXMvJ~oP5Jm0Dpsd&fO>c;?AF+iqILExkp4@0=v#bf<3s%5e(la%};kpW{K|9*~S(GL(!n5a6!%Bfnh8+@<7eyd-4*}w*3>xYbNq5YiRdCeZbx4YC36TRX$DGnr_=lp;F*T=^{z7}Kca#z0(sAT~--G-)LdzTGhs0!y=;Pk8A7MM94bs9kmpY&^EA79mksg40!``YyD)TYP$noL1gUpj}4zC^3HMBdIfdaSLpD}JeJ<39JKR!ne$X>{VP3uG*lj5}IK;4r=NOwgZ1z<?b2D9<g~P%ucLd~&s)3odQO;|cKP_q!)W`=CB8jF$3@%wEuuuXy<}Y`?D{?{^cjk_s;+;$QTo6qqSJRBtb;AnKELs_a7Sa&LXZBC=;2tX-(z09JEoSxsk0SZtbp8*Qq4EiL_gluV@Gj*l`Aa%yp6nfwsn1ql^nw0XDLRkkXXK^+^5cMo{ni@$J6iWB@Ulz+~2zUem=bk<8nLUPtTH|PS>Z(Bov2_hjL)Wx7By0o^veN|YhOUk6;hg4`*S?VBl(#lq7QH^{0LV2o9aF($#!XF+o*l@j|(@$zc-0w!+Pl+RsN`sE;l|<PcFH6Jjfy=}uyK0|{Z!)!kgc4?7By-QZ@iP&#;Gnen5LfzW9$}dl8bUmJB+npp|IgTKS0zIA#jAK^ZkaECWq{V>IR}-eRwPy$6^H^qNk{DW?M50MU@WRiM3;=lD=EoMP>F#DeihNP@P?=dk_*s>u5-;fY+mkl`k)>=^X2#x7`nbu<({w#Xi!PHo|Q2V-H_)FFhxCvnk%n4v#g`tcf#r&Pu1L*PT?^e*|QwA$gJ&Dp2@7LqX_Fip$t1?_*~gpO~u1pXz@=Ru7I_b1Y@~a^&uyOq^L+lW-(WrT*|nAPAls;!3FUFu+E#^vWVWGO($&Om4MOhCe@$<OKTBFs$%*e<RF)Cc|Lwg%mPd5%5t#s<VZ?#=zCxHf<$FhZU>dFd|6*zM_H4ej<HJN2i2B@s_XdZ4r8AjLml1hJmUe`?N*@Xi%TaxMm+iCUcyH~n{LLY681%wyJ<cRLXkAS_#$M)@4y;{LUjp5?>6kPcoFwIkcgpQlXSKzfZDw#yZNk~O3pvehD}2%3{;TKVraf3;Q;iz+b9?bEjpSPTtnb<6ouT;m6bQ;I?N?o#xc;7q~RuljvRAR`6C&}npryF$ofRhW2{Q7fx1>y0IN>nzARvI{oY&e(WQByrVn+LPU71@Yhf6sHoga1)TU0d4<*(Suio4k#8Ati$z4E;3eSh7p&>VuRix>t{Nk;7hLLA`CSG|AW4mj9Qb0&G%)S$g4tpD_%8Exo&w&pk!mihL?EKU>SWZts*Y6`9F5=kx;t?P5F-Wf-%@i0$n{$`w^=d6$xI4y1G9C?NZ9$EAr5Xu%46rApVc;w<tDp1WD?QlwB|*&|2jQb6$X$XRVlm$mNOxFqZ6hz^Y7+WuxQMDarv#b&(b~0KAc}rQy$&10MX;uGWV<^uuL+6Kprqa=g%-|Ftoo7>^wg&n7@ZgVJ^;ofqGVdEw4HMq>>_{GLnKk{#(@H#`&wPkCqy)jcCUtX97sCN8qQ-;xro);vs#R?KBE^L{JC!0_jxX^yshXxBtol<c(Ihq9Hu4HB22m6`2X>U(7gvRZ@$v2?F}nm3CcBET}f<Rf|HPT-Wk(|SvVhm{r>lohQo@^g``Felfl2FLL$#0m6I`!nq8fqY|PAIlu=^6qSYf!PWPPD+}V>tgW&3YHB<#B0I6_g0*B4-(w@A^Owflq8(mJ&;2$4`;tO6Wa;<Pf5KC}ONG8!hF+fEw$0G-SiT;39eR+`T<+<|bm#13B`tH?CSh*f5r7)}6%}smE(C1v%)yG7agsw`{iKI8`qMv7~`3l1=sBgu3<$3wkc_GZxKMgl3Y6>aw)E6baLBq6{Qnus|Vimq0FgD#u7aD28C#(xKBY$w-O!^2fiK@ynzdl}1q`u=N(>6$a%qojW@z2`ZBSk~?EksAp9KsXbSd^44>v+Ul!qoqTcz;paW9b{UyK93M;`%n}`s)#02^3)PgQ<9cSg^Dfhx}g+F@aK&z=)SIU#P-KW1m~@KffRNmtQTFB+C>s7gh&b<%@nc%uV4?!2uo9M+Q+VJS=`K9Ia0wc+WeqIaQbVsoQf*Y0(}-+%PCm2Pq2?Jqb(T;{$gwJe*dSJIEVQ17EvJWXSmmMd_>29phIwE>ohY4^G;0>(+pun_;($hx}Ry$8(09!<JUOBuDa6-6WPl>YgNODT2wly3Td=Kif9aBG>*-+5W8^6~nVB6I};;2KF9T7EH5@cB>0Go6)zlU&5fm+&I!`KXSQ8RFG?IuF3But-35zf%@8=i;A>#!P~ITev2e^r3L_5;c+thg292gKA7kJU+jDrC*gz9)pQ1zWnqtgZR%4M7mV0LCVxtw#WC*9XPOg+h1|d_Y~h)FTPx7m-@7mAz<6o2=uSK?U95-=tk9C-p0lJ+Qh`Bw{~!x>C}f483`<Y4U>Acu<;c|Lj>`{CU58;C^0h-PdLd@EA=Rq9oXY5Ti2|`%MIV2}ZN7l<@c!h-2q(V@1hS%Yh|I9Orfw<mk71h|Y#xl8-Dqmh7Y_<7ZlXgBTik~wozIP-<WGUo`mJKTo-s`yH^>5KJD6eH{(bbQV+4D$u4pziOc-k=_#mx-#4y}RS}2qfz!_C5R2obb9zC@+@(7QEu_&2Lw`9Jo%=%s<8T+xtNKC9P(S=4}lE+{tF<6$Z2Ph3~ZL8^HV{arvYlj|q)-<hHpZW2C?pNglNRPH(Q}<6i)+R|zA2Og%Uh2S&{g%(}QN0TAu{c2p#?w%<2;vmcB{dWPG<~0OFya+cx0gHnK~F(Xh|iu)qB0-A<o;eWIR_q=T(;{tCo|ZWDFg9oEluc7*9KjbE;3|aq@qEl0@W5;@Ca&W7N8E%GB?(?@bopyuOw7Hpi4vSf6j-yc3dua1t``?o<*vF(y!qyW<*=gmt`Tq^jDXAK`W0rv%BU1gm+!GhSIM_|0U$ONwsmkio2~g1q-!W6mdYMPq?Z@^`vKhAFShZjlM+X{O%ShDkq60vL?fn)KZ}t#>x%vut&NnP;Mk<&roTEOV5*WRD>E{dy%MsxA`>YH5c4x<77{Wo!yp%5nJ$MG;@RYa1sd$u^}*=Kyv0<wfDb>`i!Ftt6&d#u3?MPe9etwU)N@5eZj2OlE<t!Q+MRWO{RA%<?#qnx<>zeY{Kghh5`L$EJ1l)moca%_)1E(ogq_a12?I#j`pdliUz)(faG4&$@H%Jso5TdK7)|gQXfWBDQI&nR#H&nBO)fh^b3T5Or5$WvU10F9V3?&qGZ`#h6Q50L<N^!T~KwiJ!a9OH|meds_l)U?V?OHvJG@_7_EH-sD%n?VxM$c8pU~8oW?K$V8X1j?HFYOzNF~tgZDAMZ>wabZHyCuK8g5=2+}aF+A+vIWx1*&A9ueqi0s@o+9`CvD98@XM*1Bgr(`VZDMdYL7}>Eh<#u8aSm)tRoehOjRIkfiFkRF+DoafyH4NPt>?(wT%RDt2F9@8d_hnG4!01#7L?CP%_qp*EmjEnjZ>+_2b4d#qu9_7$jje7y2d$VTuL6;LE1<+vqSK->V^I<4%M05y6p97-jFfTSZAJ?CNock83v&+j=!)vTH0R*sx8L5`d*>Kb?*_P)J^<&H7>Yd-iC9y0UO<&;Tn67G1T>mTQzwqY=iHmE%X5v<mho0=K&Gt#v(q*Bz{QD<QBDn`1acpMS41>{YmW|$Y?hb9m%kuJr^rsyjR;c@VBALS9z6A5XOr-7SQ^P%=hgOZfp@?Jjc|>#>9J9f9>E}6EMaZD-c~_JZRA7~2Qqf)@OQsR;^B}}a#sKPNMU0o+JAIhyM{Dl@iZEmc7e^VNlR;=s1|rw?X7ClPwC~_qTHvktb+#8Uf1^5zx)=T#g2g!mYM7KucJ-)Mw{?;I)o+NZuNxmsPsny41Aq3hQ^!B*lYr$)fU(ivt~WPy$XH=xChS{Pr=X2vwi`n`^j7OerD^w_(dBJqS0%)Hzoz`7@1VZqyBnL`D=A;V)zUUdP^EdizV|cP;K22D6;Op(j)Ik!9aU0?Cf6qTW4zxctv3KrmI18lH9h(-9uvHYh~dU%tJMetaqDTt&b4c>;oD6!^0KR$?a0W1_9s*J0pvyK&LylAT$n@31g1Bwy56I8z+m#*v#;gw3Nr9c#R=PQf$?f&gDo(A<Zov$*vj5c^Zx`jjJ>Eq8y44ZOT1@z6iwYUNP%2qfD|=W|whj%$S0P|FCVg4ggpT-6m3<xN$=vwyt|ZKic%L65VjxR(kK;{sxI~Ri#+#z#F)Op`W(*O*-9#bxb_r(B=D3;rE`nV2Pw3^kICDA#4o;20Z%pE!@}g2?9I;FSBoV%QN=LR`E{oim#vp#&KWVR~T?wiM(SHvn|rYiR849!7P(?yMRpGUE3Gwc2A-6K@zLc)lj3$eqCB=?XCyDuUha_%WVMV@{~}2GR8ZGzKLoEIRv4O4`%hcci@(>db>Q~mt!KkD0wh?4U6J8TA`!K8B^D#>K_;-r@)}L@JJvCDS-}X-tZg2OsB55(E*0pGAX50XnG^!z9w^)bArR$HjLQ32w=iUgn)m=O?tf5bzQ{Tzy8-ni>W(r;HgtRD|vxJW!jgY83e3FYx!EV<=(wGxo(;SBs&u$isM%6H&ZDb7fbsIOXHXRkh*cC!Y1f8VI`$oWc9WcSlqr}@{q&lgUvu9y}XTDx%&&Tx(fkbT(FznEdl$tKl`TYAO^)zB<j;!&+E3lVw6iT;jIeK0;XBqc7D>WNo~s|Rke1EK;*WBCH(Qt|NLIR{rmU7{qp;FZ5-b!ZS(89KORK+$<I9F_04CTOwIII{Qiy_7iC~R)2Qn4JwHfRob0lf=^k^ssnYavocsh>ej4xTGzqX>AUW{?VbeQ?yQutB)FA_ZnyG(~O^yKHWb4OcgtOiMH}3g{X^)1=GZn}NgI(TRV^12tWhI#ur(-H=oFN<>^!`vW7Y*GxmR7o-VBA{^Ls;Z9NGTrcXBRK-o|mma=^(#6><aD(oHEu6ohG}b4PIPgxvbqfkzoO2?0?p_Yp`c!V=Y8JPGy}YUo0Q)Hu${o^>sBX6#804XmmECyI1IKW7o*}#f`ewW-7{+Efpe&xvM-5?b{&KLCM<B?-ebg!iS7S%^IBAdZNeV)^l=8LU=ACnZPv_CCm=a24GmLyDQ*X&*=H|(9Po1G>16EImD@`n<hJlr=zGGfI6n>=@31c{k^vj<2Eq$a6ZfM#F{(1EVRDD8zHgq775AK?g3VmVOs%>yc0dGx>&|6%a)vq>TDA9#Dov~t~0QIKrsvoRsf_jos$}K`vjDYh64nfzK%)Fu6yi8sek!$nr-J)r`wXjL^utM9@t*}f(Y~!dBn0*yvCw<t*yeDEC9HE@d;0*l%USU;k^8xMxx4+@kAA`3r8{3+AMn&Rn5*)MHCkBK9P%>=IvHlFsy!MGHlhjSOu3K)g6=BTP9PZT%O>0+&{MV4VJE<@VBNqG4f!JP~eQYZ!8H;P?ngmu2~m$40gzK&Jx3m8FY+RlZ@Awv86sTRX{50JsQ+So`auqm60Ti#d%4|nvOu+30RQd7YDHs{pu=e>IO36l)MLOT{S8TTh$5s{>YYEpXYO;_}wN<nL1CEsfRe5(Vl#|Q}X_x03p&BXs)cyZehQK&nHxCAjbv}f{nXon$Ud>=b56VJ2NFH)+X6Gt$k~qC-4<isRJNXkphRzEE44fB5A|{7{!A!j?i`V%Yl7Uhj?L-%(2uo8DaQb^(kjN+<)*Hnnb-`#`{A=842D$L(kQ}p^3)7TYVfCwYleMQ4SCI^l_U)R`Tpfr8t{lO;!?<;nvICm;oqgk4Ba4F`4U)d>rnO^8@BN<eE3NtK16?){m`ydP_w`J)sd6Y@=^twhR8Kqxx1`(bl~K59)sw9<(VKTWFmv89*rhhBr_Z@2I~`vNLQ{%tE0Mt{p*{7<~H2pvPMh4Yk7-WlLxqCf#Xo+9rRXap`0r&tR(>M3)E{?<_V&40j~J6T(grB6UQWJ;XJy<t;^#e4Y2<s<40n2N!{3FYi#no{HjlmF(d{Dp-ib(!`eZBVcA*A}|Y97@)%32~8zZ!ws^h+LSQBA>K-+LTGt7$!&4&fufS$lT}ct1MgZzrONp;svp9x@Mm&L)qw!q7?QhXYm>#G*RCq<gwA8lPf(g{e((7YePgh*Y0uQkrAbPnuA5vh5yN%Qm9IsRC?foPgc1&@HQq=5hJYm&=X03bjw`M6rB1gPNCvCF*ix0Oo!dhx89W;L@&q@StcZ7%71&}aq8NzhqdTi8fd^EBxQ77EpVUl|j$lO`U16O|0_+E4LMtco?(zaRGc$p;S)C_93j*urn>*RNgZ7qcVYxQ|8PP_cW$`@N2)x+;5%-uh8*~PDTTOaN>9x#789k~sLmOyP7h<X@tws4^w<AN==1#SYRD*i`e}+^UFYIeF(ujRdN<qnvzI##}?&rclpY!Tf-0NvsQca6HVlMSz(dXh@M!ya-#Kp;tU~UWtohk*um|OK9kFa1KmgczL?ovz%th76!EESpuyU0Bx1EUY91H@9V^rfQbqPcV$zOIk;pMYY|!*0{ZkQtja#^%$h=8RHQpTX7fladXqp=v8S#%XB~MUpiZJj<Td6m*F}wn&hZV%KpQ%$)3EO&Jj>Z{>y-pDC{jJN6#49&@$1qO~2Ml{EMLIR-fSflETAUOoy&bBTtU$s!;Wiy*s<cgq@01iXS{z{)vdu!Bg`1S|_vYz{1LJM8Z_;_;eo#Nze-%5Q#M?OmfL>IGign`;N~V*-1^)@d@-PQk>|iY7ce%ZhW_f3S+ZZ;Gx%H_!yp=VW0z*Jw-7I|$6fDAvJ=ISq*}6nrOIjaj|khC%JpEX&8CUk*$@47s>dP@VT~J=uItV6v0ItlOg1SK5WzfKklNrd?O&W%`eZNUOfRorJ_UdLS)!h3pr%=?KArg~*hiPC2RbXFNx)ipEjhU>tM1mC}UiC*`weSqJ_gT_SAx1lpc7RjfNF>%SkQY?5nlurg%1k!9`VUd6#9kd*tJ@+^hoAbvciszte~f<}+YT!(mO{k_W98&J1D{GRA2%=1mnwM+atzXu4Kn}pWD*(uSV7>3^5flFHAJWp=(bQ&7w`^s8>VQ9u5(@@z2RM`+e3A<ZGdcfyNJF8T@X8*)d7NbCfJn{Pan%4%r@A<W-+d!JLIzdZYldgH*T-k|0>DEmM65a-mlYgv>VJ9?qG4E{x6g+}dk}}n^1wIO`<%=h@7$sy4%Ipm5vbdI7b!J}r2JZ2fGsCt?0+cDO&d@TUk-{?A(q&dJ;Y3`dL=Iil@w^<C(UoITTIjDx3=XI%O3%BhlV>r#Lzan!IpAvJTqVECX)emTCF1X45(33jw+YW8w<>?li@Mes;QKrZG<?V6CzyrHR9N$K;p!B8j+q||?!b9$6dR^}$82S}-DN0T2-M=63622RGyzUo6oP};twq^`wctz8&J*kl$Q%5eVxn()6ZOJWTa<l0uHouNHh)n?9&ZhW=%{N*^m`##A;m{>M_o~E?(8N!FM%sEry^7YsCU#lHtr}vl_Z+oO#FgseI7(P4Prg_(v)BbHtC&-OrObFW%o{Pl+^m>8y!B<+HU6Zsq)%rE<((eiV*xHzEfG69@N!BFqk4cmOk4Mk~oboQ|Q^!ij}Qpi@PtvK~TpVtC>;WN(e78v}Tnq10^ceDnn7(DGyX#AneTRZ@w;@ba|M@P*dB{z&oo-+Myv(_%qpjjwaa%ehJ1d`SQZgfU<qiQj)zJf;7f9CW;WjgKur~C)|4q*2m$~HaVu#RF1%85dk9!`M<fT%)TX2s(b1IMTLMZ^%`JzEcR(60$pG9{@Q|bPh|d&2O@ax+v=EH9VA+PvWZX5o_Ulp-!|W-Y>0;(Rg`POOAd|!?<#$)dcojX)O8OsL2e$hv7zi;+t~!qM=#fpP^)}X$!CwWb0U4hiptc;@nyjlkL;(8L|w%C)#YV#8r+gTd9!(9{6wemWr;#}bRSbbQb3>eB~I-8h_$VYI(2G6;YF&!gBLBtiezQmJcVnE!gO&yL4z;)#a3+87i)MplqyX<b?3GirJqq^4|+~$N}jYvaWlF;)V|uH$#zyp?tfEu$t}67($*m_5&HMKYM!y=9!6^;=OD2tuCEyq8{OG=yDf3DE2dy-)uyg>A$vNt=$$2={?hUIURzXu2gh2v-Y2{wFo`MYa|FxlFi^EdOU*RKtcG*`gI~==<>D-T6~TQ=b`w~N!go4&7Pb%t?RRjxp2MAd{SV)>AzBQ&LtId@7yw&KH)n*+shKnaT)g?f<0BIXEM-6R@^*)ZupQU)5|@xS308fzZ$KsskknxpY4o_3Z0R;%XIg}}OcmP~VmDbGj9+(}&T}uzxc&i=oYH-i8uE3NRj&;qP@KPEZ-&0}pBi&;GaB41riPKUKbt;BDylb**R=yi0+FP(KYA6+gP+guq^2$&8A<&<#4KWeus7<zIdur_E}$UACG2JQH}>>=v00%kNI8_iF$>L;g)8$pY~yl&#5=<5e_G>5E!55DQZI?C=KR4LOKB?0xuuD4#`ztG^_D)_s$8G|FM9*ir#Ro1{*B31srm`9*~{K%bYd4|vdp18Jhg>~Ba{@h;a&P&3iz+;imf+H6II%0!P%Q{==>(bajpC}*(mxUyCd00^U&XRO%+K^TuB-C$RQ!m!4@KoV3t8vxyOk-d4h0^lyx9<?yO2-($$e#hOw1qE_ANUUaM)xDVoRhzM{wFEo87|nBCkH2ORwNoSACK<sE1l6)jqZr9u4*_-|B`n@f+I0Ap%atFH<3VQ^Ya5%tnLzCVvG-zdAan<0N(Au8k6g)W889FYtVsYRxlK?iJV+@C;6Aqr<p2Jmzg+9)vzC8=w_6bf;`?KBm-0GO7!Vsf;GWgJ{P&vguurVcR^3+It@dz#T`%cfFqgC#7$C=Hkgn9tNG+{e_-DCEZGZY%PBg`~$cX1`&tsS?c#bqFHk+sV=-1Lostet<2AT^`l-rS^gC{G1k@Nn@afNy|S?HLF*_=VeS}4Lm2x1pUnHz{yGwPhz)ah*-l}6%kYEKM(wSZBn^NAv$$|<#r2K)QE+T?PDORM(0r2bSbJ6^^21&O|4*&;xyRY28MS*`sNi->xbwJp}eQ`Y<K*bWQsw`=Ft<acJ8RnP<{4PC1y2^siA`!zMo~PhaEg#qWH$+nj7~r+mL?enV{JA<G+7TvEY(hI@RQ2DP;Q)PF@KSQqf9BTb7ZyYo~aUBnA&q``UH1D{8FL+SWXKnbgHz05B#_6TD?`r-tB98A0)aC~Tly_}dja`|~$G|C!*}v&kbzWVCz%)4`C{wlo6t*^d22FQ7=w;PaD{(L(#&@1KjZN;cc$Bi|6fZf<M2BxCeo>(gm?rSyLJXWw991B8`jNrNr)etIicCHk%_c39Oto9IHMP|0U#-JwPK@%Az0u|-@Sc9b}#{9_-VKMYP*p+-jFNn=vqN@D9V%ehH;^4XfGz60tP&kw_|vOy7KF?9Z4>wV1C2hp8=A8o3T&!pg3j&!@<5~P-482RzP7UVg;v0a%Le~A+6_;rf$fGgI%%ePRg2h9jdPYZs&;QC;q+yY3pRBZE0<;7ZX=#F8i>MW(s#;8CLC?s;epW~gWQ%x!LVu8+mGoLH6wX2GJHCDTZ&d2c)yn9bWH#m&($@TKff6Vre@9X<NzpI}_!;|YT-_9oY)0|Y$9VD|rJJ{A%ItRFmeNh`WAT8JbXC<flxzpUx7fV_s`BO2EwG<I)>QmhuWjX5~apSMg3+9)<|K)GL{4m__kC)Hjd*`@K`gw3W1^)T1!4XvZL&ZBa^a$p33`jb0|M9QC{PoxW`QsOU|5u>M4o{By&yZs~AfuVwgR45GLdm8`&(^GM>}M&_bd2D9Y!s(>zEv+$@s68o?`PFOkICc^80y8tNH73S>slteUQp@v5<x|tjXFlM=m&@<Ok{XrJ!9BD{q=kO^;`YY?FJ5*+qdX6vW2!ceCIWL{GMu5m{DcdHz^Jzp6C33|JTRIKfV@Y?Q&PY52$4UI4!8vuf0pRFp3CsJq-IoT#?9^Gl!#2Wk_wSzCfvLWpUMtu#N%D5=bz_sZBfoHKBv9zBD5MeTmk1j=Y_3^jKSGS6Nuqf`0Bvt;6C3)9A!o7f6aHWCgU2z+rkN@}NJ7fB`x3QJ!0?^7v4?>{$-*TySYKNrnYne!tUSv=8dj;+~XSsci#_4f@q@u*;jUg|x52ONlhV`cje5)HSQO7nRrXDNwASrf|8pzF`sBvklhH&kOb$y+J;vEa(3C{n4(4sMY<SkCKTV*zr;3K~61BEYtVqyCBiH18v?-K{|ENTbod5WAW|*k9+YKPU!%H--UE6fX|U9tAfsYsYpm($4+Is3oOyr5MY8xhzE5sXo)VZZEs%{mg=G)YW$E2B|J;Br%qbgicMsc$9VcTs9iJuMfk%*1{<yybZ!Y@ccYT4#E8eh0GKw7m*QmyxR}ReYe+zbJqs(@rE~oH4BhajViON0tB(t@Fs~~5wdWs%SVywrql6jGSg8<(Q!y+s8)`}DHi&o^BYHCS72uT)u<=A?7+~d(!ENr~s5Z#+Fuc0OpIZvHwZg>~y_8Rb^i^Mwh%KIG5yVCuUv@*+xwv!S8d1(3{ZAC}Rck(U>bgmYXV*02+PkLIci(o0&elj}fn$wSNe?ww<Tn($W-%rlhUk>s=_{bJ?Wfjyy3y&1QcWLeHqSAlS%EaXEP)ZrzHAjZPYs5us+jx$4iv~hmc?_lwXGgw@})?5J#E}OtIQK!UFXdDZTX<y*WRY_k7<j$y~8=KK`2F!pb33F8p&l+3NWdl&#xgq&%<7I&@|JAFMZ#utoax@Y_}+b!#RV&Zj}q=YiuL}{0-o59D^F~1o}1V5QfzmRyrbN9m7?LZ}$8C3WC3d=Hfs5*<NOXVmO@FAW9$lC84qVz9vyaFViA0OfTP@5)}3n)w41@k)(F$NQ2g_s$E{%L!8E%8TuN(GYhRMFm9GE2Ejkgc<3DWFm!Iuc3(6$-Q3B_(-tc^^lka)$d@NUNqXSqmK}x$*}}M5)T-dgtm-I+M^$u?lz-{DNA<_RG$-3MnQp$X`RX*K7^Do-ZG8`lak17E#{d^!02^916QB)zz!xg)CM60v<``uEhhc3I&V(X;wY5ZnikYey2D_;-j}M!oBHf`!BE02vbmL=jE3kG$B$^_0;Lnj2LPy~K)SZ*-9Y+m4Pf<P()3LV;FllZR2prWb7A0ecLa+#K9JUhjUZ;zeqbm=E0uk9rVR$Jv76O>SY9={L!E7em0PKB~G}_oKWKSYSL-mLcQKSV%v-m2fHEJNG>2-+ByMi5qT>U|Y<_QwOwEvnj&LU?19ITJdkt9Bv#(ZZ<uU~WwRbDq=X$wD(o(kTl?tiQNDhlJL-ldF_7oOfAI^6J>hCGcuH>ex%0=#<9lXn{L5b)hsjA$Ogz|&;+8M!kw)Hu*oBRIx6XIcbs`XKjO4UOg!!vVux64lO1<tzFuPHu-yTfrz-H(#fO<C!}RRL$wV2*$bP$4TYuSUoZmM@V?v({5jQU^FTRDWz(kT%C`<e*gPH)+rtYX5*Zn|C~ipcv^oeyuiV4Q(Zpv2k5=8UqBGDRlIt9-7uXK?2T>%)j+sB9Qq3anyDPUF&)C5>J^eP4>n+rKwbW@iF3f}q>U*rH)fpY5=ve_2eD+(S}#Vmt~VD0hlKOg($Xpvpt^jlF3LsQM%HB&Yi%~J9_CDEo6n*C=lAdbz|<(b_ep14REj4`upq}iIF*+?i4-MD!y;SMqPI3t$u}Kl10}7^gpHZ|c=ql};z098c(Z>VzTmz9g(9GqzW}CW18y<F4AC~2s?Dve?)#UTw%Ei}(<^Zq(z^b5R*Oxq1o;MFd`RdVG?Ye|-gU9;2`Ks{Ag>Vi0Ndwy;p<FWL>gPh8_kVVFOtQ%LAghDXKv@3Px&^*7l#ZbUdNjaeP5&HfD}I{2Wat2vyh|h;3n@ts8pHUr;N-or6rM8P-UP|U7Uv(A=YZ`Fh(h*#g552paB%oUwun&ej@F7HM(Q`o6RVw5B)kgpbf)r4fwekcDp795ndDnS7cI(ziVlQtTk>IU28o^8ID9UI8ma2LV`NDWZOns<l5h<BEPkxVgNK{qU&JKz~1A^f+-<|*ZHg2jJ~A-*f_Uwq|p)uN%5qD2pdk>N7)mE0Z=C)`SqUGz%lCCZ;7O?)Bq=o!e*z;+C>7^#U^KRp<OV#y3d*0Bg`KC+SHfI2u>a!*<^oAYy-x#`Krd%p_PbBShYLvTw`MZ#{S-Yg#mD;G1{aZ88aOOW?+T13HO{OmzL_?(fbEksKbEV{6dj>m=x#&BU76@)=Y8({cW&o=&~hA>hfso{!XSc`rVx*`Oa!V0rPmwc6>$@w4xfl%iU>>f+52;H`qKFH@nf)o-ZC0SlmQ|61KQrS(XdLg`@R*m3U1{nm+DuN=}~Aw*9+FLff8HZJrhJL#T5EAFP~9UH@?Ae|MRtuPM?7Lxe|9ZG9!e<6tZ*4R5uF{*=FepOK9H*kU9%xmkHk@)+zS23tEa!0G0oMndy*?2RmD?a%|yn(E_)+!rvQrIGP&mW7+mOuex-DKz?!0e$jPmTc@dx46kw^dJHoI@}-o-7RpU)j6UCYN$tN`aa`e#4DzZEO+*U26|rMls%iifobl84a`%%fhFU9X=71M$SzX`;?s_Mp*vk0^f21UzNpdwnF_Cx%j`dw>ijnjQ**6pVFJo!v5RSiOGE5`&WF2pTrT7)VtR=^dZpQd?q6$j(iZbl=3y+#6Kkz-@U(eD17`2Cyk{&b5~YH;I=^e$?j!CJMfm`971fPMnklpvO_q@=Th*fc&@;aergs#To;ihwc#9NOhr|+@oE^KJYc#`Hx#1o5NH+yj_^5Y|)e!y|`)F&TBnr@D6<cEm-D<Nsj=snXJG(6@7`EWYXyyimoFozyVnbj!3y$qyWA^EP6ZIKK8CJo@?jfgW&gy5*84;A7wW+c?9Uik*68b<LmENtC$0N#o8vXOJ39myK2K1M4(aLpQ#^OJ#wr-7Q$kf@uO)9LTZIddR_}3GVUEb+r6k`S8+O%5-eFh<~r9O<NQqt^LEbq3AOJG3zIta+rsq0u&?)<J}<fDT3$+Eo+3&ePds;q>HY|&ixn8jr4H9@@1eK5L*2C$9UvJG@_7@cMWs1->XW1n=AnlueMA`By-;u(R;@i-;mONy>Ocw623wn|po#yA1!laWuT<AV>QC(SX)J!QG7L0nqJC>+?_HQFh3z$nNL%trbhA*W>2Rh6V$1yeImgxMkB3D$YYBk?ri^II?Gg6X1iQCVstsR6^kn9ERoGg#EA(RgDy({Dm>IE=l)=u`;=J}XJv6~9^wz>@aHT3k1mNa0dzCOu56ThBo&=G7MOVhvPiRa}f$f(I{!Xw-e!AS+An|A3J)&b!S>0Y3??wpkjt9$i^cm*pIMwP=4MG_mw<fLkdDab5{8!0^<$)>NI>72i3gH~1bQpwU#~PjMVR=iY2xo@<P@jJG<~fu~g$Enc<-?I|B9=8VhKFiIeL0eD4339|O+z{qBKIehsGVswh^B;ANG^#I1bWVC%=PW{)}Bs?6JMzYp<wY^*59f)pDwpxytWIi28!5}ND_TVFk*4rxRsEwTHZW6tnVEDUVB=K;_DLJc$mF!W3Q`^(pHKZAfr}5z$3)J9nI622y`$V;X*X5-)eTi7PkoX1gKaFJ_G>G=Pw!i-6xA-h}44kmcT)%%EZNfL&gs;;fEa`TuCyYmef$szZFG}Wwp|vQw8U2eb_-LIq>j~~v@FT!Ic)s}cpWpvMwXXZglmMC8x-Wjw2HM}o#t>5W;n5@YPN}~RdU-XvHZgn#2E8SXqs5YW7RXT(KL)$|J$F80l{{1KEVd)}+TZ*hMqUwEz3FNYog}yIarcmz_*z-G1@pj^HsrymMi~q{Z>;zlx4}O=I2%!GItfY&<+HFevUmz~x?>AM<4~C}=BR6n>OH-2vS^IW3~$3`3XrBKUSr6S)HpT8X*rUS?D5oh%|Oo6a28v2@+)I6%Ap9+hD*+Ueo?H#XvOebCRr)7%Q!S<OhLnc*lsmx(!#sy#04mev95bU#?bVz60MQiR(kK;o~wy)Ri#+#z#F)Op`W(*iFIanTOUoe{e~{zhYG*<#05(lghL<3_ZS`#sU8e?^y^!=ujLa2cmiH#-|m)Y=oasOg9vQ?5sv%fzQTahO5`1rnDd=qA(5OGGMHtu>@gKQSmv%3E#Q&cJ%!E(NvuX!Lya!`b!nxwyB_$i<l`*44JxCa;hdz-woOzs$RP;1dN8Zky#u#QIRTQ!I%~?uqNcnqd3cZ!dBtzELPwJ`rlQ@vs()aVoC1T|!Xtqoqy##kdBbl6Go8BLMh6&X%cPVVd+Vhm?rSn<IVU*0ZNrGoivT9o&nhFYR3xjqu8Uav*Z;a`F?Ht+JawbkfV@DV*6MxznL)r>w3e?$TkhS9Go`jZ0m;t9h~l`_^4nAj$Hmfq!qWJqKcsFPsjw-<;;53+EwXys3M^s;eBuy3A8ZB^X#SO`mAk(XtGf_!@9>u-S4!6U-}UU9s)HC5N0BJM#dnNRF2RJiDm)9AW^o(1sVJ`XiGsD|lB!xeMj&!q!V>=Y=6`;#-~Rpk-+uZ1yEcw*mA3iy-5(F4{N!hz@%rX7PNrshEPj7Sjf*lcpJ`O}_?{m$`v=C;J?3;%rRn83`3bQ6G~Ux`5@5SPa^eHRrgsc?QTeH;Lk9jdQ~w~F+-(k|xQA0wn_N4#1oQg>Fd*&GP<f^T*<i5Cdu!}TtG28plj3wtqtUnq1JZsY4Z7r(iV_(2*1`}L`3zEuS6^{706Ye{=VdEUI>;{%yMj9cr;PPNr=rT3h*{vpC6@ajLN!E&1&p!(S=+9`o|TQY5cxQjb((y!{D<nQDXLYkW`#mus|bzGW_0%oy>09oIls73*V;@)xw54~#QLl{qcXrNd+q1<iWX7fL&l<pFdZrWWx>IEPA=2pJR_OFH5DbyF1oHBgJ0cU0nd6y&!>lO7N@2;#39ZhPDR}`**QENMdbk0F-=d0=*jHwy?q$BfvJb{S%xRp+}UNJ^%dR-iG{aFNUnAdu%Zmx3TWh==xNo(GG<w}<Wy8=lb|OieAsuLf&BxDVNkFFAeHHy)R@~Rplmc8AlUSEOiD2l??$PA`Er_V=TxWLlEF?-Luz~V3nI`{<PpnK@fwTbwYCapvH;-v#V0(KQi3`Yhx77(8i^`P#uHV%E*!;BYqRWCR5d$G6;W8g`$R5knzvhJ!La(3$*@)9VijC|RCi2fZ<$Pua(RO1;9Ly@>!oWb{H>`@j69el6gXq<8%u%{lqDvtYu1GwgB|jmv&8UX1|6f-B;)mEY^je-6_AR0j|O#-=isMYWhBXBab8lgrXvt{0v6==#X)RDzq*Q=x`B*1CGUY+SB=WTR&~O@KeDCP=lPr{ezyrzrp{Ak>LJd?+`93c$c>Ws2L%X`zCd$jZFUR$C44@iS_3&YfDmllHPeLdYdFsoE!~+ZL9sT;&S~vi>pX$4ph_J8p^6kZWM+{lFAzy14!|fLlyQWvqhAi}n>xe`gJh1SrpXAy=c-RR+u{C$&(I|5^)lWcBFaec{uz3%{tZnu{@v>1xTwuNPm6MRz^9Mf6ta?MM=HhH1Z%RAm<+dG=Ee*_L3=c+Y>&xYZ{*`}hnycU&mq^msa@q>aIk)C?bBN-D(VT1uwWZ~6SH0LM;+C-+KRUB9e7axv+$rz!Pr9UY{>vZ@i)AIs(45JZIYc~qhb~cg>dZ%%EaK)KL$PCl4z(MwkTUd+c4=)d($@g1C2{319=8p)gZb=z<6h|DPp)I0iF<ciV&$I%IqPoc`a`#isb9O4_Ac+1UR?|9D8|(3iebK$E#!y7gE7OB$g(&q#pq@+Y*6Uu)+Wp=1yoTks5B0J=La!0S@t2G8ID0!%1$7a}N}i^q#DOLLGS5Dk@dZpHck~c7;EaQ>qRG;Kq>LEnAx`2EBGwX(x0ZYkq>#Wb=E^f9M;7olSeDRxV9a5_R3=dWjgWd#-#ff<zJF=OdJGK&|mU@;3x5u{fW@+;&`PoiBB|#XvGx{l%85WbND@O3C2S(3dB;!DL0eqpZLdOA*CDJRjXzMF~8h8pJ&WX#S*TigW}k;^+$NToPbE7!z7Kk$0CDxS5#=tj+2?0a_4PH{aaJ-W{~JR13?!0mz6p`Yem*!A9W4{*SoFq}iY|xZ7&dOG>Y0F3RXptr^-tle!R7O=&I454#;1vNm_BWuzL^>;E&P%6MU4laWU3b5aUQcJ$qo;&49~2Kt;=ui{=$%aUqZ+!1rB4~sq*-!l4jm?17sZUl2<IOtR<0LI*^|9FH2^RP6>^>&wHN?@hk31z9!JlI9<AsHBbKph~KdZjNFJr~WT)9`hDtp5ZQdmeV1K8DQLq%k(1PBmwgqWTQ3j-QllSPfNM(J@X-gD8@$vEW(utfrt#46;RnoD{o`%V6eY7i-FhNO>zawD?SURoJojnDv;e%@wWf0Ij6C@6R#7$q!r-D)sVFFq%s=)Jzrup;!djWxQL~Xd>Vh90OL)5rZ8>nkHabm|}Baaob^kzY&kuY$F!0_g8-N>uT>BHBm3{+TL6{fFBds6Shv1p>_%;mR2<3*;!Vc)Bb~1?0r*o9lC)gh(0F^)44`lg5E)39!9YaPRwaYbfMro(Q3@<^)?J@mu6W$4*haq@?pruor3DTck9XKa{`l{1ZLe9t-jJO)CP=VZZ_?@GB4AAL_}Kk?d>EazR?3|u`6W1xJ^e04lG2b^mNKeoj>C_a#b{r>IUPO+pUx)Og|}~J<B@q2k8=F%O}wGq^V-vIa&YxAZ3$WdxMoB%Z)5+C-*829)YCX=agqD6bJF+F;y+fRTVUPOy)YoGwbhFzTSYk{o(gSM`50CYOY=4&-pz-(A*@n2F^~2{=_i!<_=ua66bkxo2S#zFyB|!`U^ud{+Nc!CZNiO_(|B^D$)Z!Puf|f;x+pxj<Og9BIJqJ*Vnu@;C;`pJ>3S<oYe_h+M0CD^XAG<1WLDVLXhw_aGd;OT?{*+xr=#k6QJM`q>_}Wo-OcEXf0nnp~Wa6YfxrqSeM1M)T%S{(l>CAznmGiO%k9?X?2E{35^t%!ImzwdI=}uA|-O@qK@a~u#B!8lhQ(eMPhJ3O;LK@Rh>MG=^e66EX)B{8|NzdRZeqJ)-4f#50elmp1MtV7P(dVYhKi~&H&%%QJ~>F7C*r(T&BXBp9@!~;B(CUSa1i<W24wG?K@^G%k3^h;X<Gm-%M}>z@`as%Ayb)#BMFh9;^jlf_9!@UqIgA=M)ot)0?OlrrM(H>v0WNH?sMQD)M-1C`3nHL!#dc!3rrpk~`{(YIA2d;du#MkvSEiB0#;P*0FI%392N~>}KK@RO|B~%4rbmxtFE{L$FEjOl0~@&MLciYNMpqH{a;+k=AxImrs?~MspEju2h8JC-I%i()6IN7J|VP*|GH5hLFT*e3?SemR786EnD1u5e|Yn-dN3y@>W84iJ>*CbQvg7sa6?^%1(Kp>H=YBUVrm-*`&+EG=`emjt1UYRniU(fx@53=5sX3M(|58cFC6)eg>57gO-x)-4LWPwlPtJ2p)WEn?K>+Q?Nb`pSH;{ou+aGCW{CdNyz`rO=b2iiBjED4=5@GY^m1(yJN9WBN6EOqW9MpoO>eke>@PubKh3S<mw>N>XS`;a`w!ljQO_tHf2LR<fx)t6JBy~40u=RW7P`=&!Vn-kO^}0kc|yx@7m5Lcs_c$euP@(n@T==q@5G#6IN8FMvgBFws>SebtLK{)~_xvo73Qy^vRpe6XPd3jW0_Sx}*D;@{t1itS@n5=SQq<UDT;l3kok%4IaE`Ayy<S+vX`;TNI{?^9dS!(J!`QqrO<f!=Y4Z>Zv=o#VGxZ5_`~dLR0djHHw?j^`Z9F7EQLZI&%M;vP*8sU6r;Dd5O@!*H!b3CHF8|8#xDwMR9%2kl5(XzT0hylU*?dQ>!+0tqa-HsYUNB@${FD$M@Qz`a3w*()B*!6@f`iNuMKFUWb9IHCk$>F=jQK^B??bCMp+a>8l9tTe6$LQWU<^!LzW1C}_Wf)Abzg<m-R<o(<7r&>iA}lEnbnTDmzSY);Lj5#Zv@2Ob}pIAAIJp_jKiJcRAIo|m|Uyh*U?t9=79S%9PtyGWzQwPZ`T`8v}gyk)A`z7V^~>R|l3({!GDS;qAbh~$*+qtuYEqpW&u5P{<S4SO^6o&VIBgPYOdW-&F4r2X0SIZ{!*alEb_FcOF)t^LufU>^K@ekV0`@yJN(_aSBx`-8nv|IMjGXm<exDK23zyT7rg=Znn>WkJfJ1ddr~o-ACM&tV&v`y<{FX8+R~KWd?FK9_n)Ts7wp)>ukYS<Wp@gfq_XIIOqy$yVh81$fyTm_Eh%w)AgIu1eKUfX!a^KBE)6Ad_Vd<>9F<JRG5<pbhWR?^3{jRab1iVVbDYJ`2v?d_(6q8IEh^zsW|?57`~bKAMOAwri?LYT`=DxJM2Nc@DM^X#}$jvdTS9<jE6+W2CGDp>t<d3X`sm)G~~%G;^VIW%gQ4J5JF&ruP*+E^i@&EyL{Qo;cv(x97}MLoV+?%cyA4GAs@1U%-E(n%rD^+yod?vs!&km=A-~YKo|r-tql;Z23mnt=$ay;|ft3w=Q%kbmoX;fJiMe%?vtVQ{(;wN(xapTQY#BqtHf)NhnEO`=wBb18%3O&;`J>%oUTPH7w)c+Ig;Hh%|MGnOHcFoZHikMq4(OdK)ZZ0Y+)SJivUWM&UlDZbl(DHg{W*_bVhlrZM{sdrg&SUZ_J58Q)HpCK)gvPxAw8LG1FVt}nF@Z0F~+=u8>|HB4ImX{uSh3O+AmB5U9|Q6}hTW(Q7If_M_UEknc_&Z>x*O8<G_-)ob~MGDcW3oN%=xS~cZd~6>BNi{l$!lp}6ov2@&Y-wr*ixj89<~A_A3(_~QfLcF9X9(pzrDwb2&m>a}QZ|pCXti@kZHDTzrz$b4X-o|r)bRZ*Q$6h9@e;*19@pHsm)VB&JI@5gwjclfdx`~@+|sEg7fT`Ahj8*rh>(g_I@+>~#9ceZlO!>CfZErtqg_#BmDaZA*~_FZ_5y%0ahl*QgF7_@f654o7erwL<-*^t(Al5A@%hgL$DU0dIU=Lw3z!authS{QpwD*fH+lg@Vg{d|oQxLQ=YIcOlvT3X9v}IJ0Csa*%Ox432V0*`!z-ot%Rl=D3mYJ;EK3?}q4(2Uxhm0jU9rQe?%6~aB85smL+cJL%8$2?DUU7U^01@CG36io`21mTvI;da0#6!~`c@KKk6F%5%9GF5MD-m|zj%Haew7W1Ad8{%|61>3u0DwF^!sR2g?uIj$8x0G{gxoL48zEe|Fs~`@r~`uy!cC$P{*%Rj0aq?_FcY(T0Lk+P<mSM^99!j6Xg~_vZZ31Un(!wf<t!<Lse%fbv8x?f<PgW^Zgv}Or2^<sTT`$?wk2sk*!@-<g2mTHFQ3XkKo;V8oI$@j8CqYU;bmZe|%p*{P|sd5ohuWjoZoOev++HnZI1eIXI(y{g}6rE~8vDo1pyVQH&ILY4I?RVXO)?t;-hbAC{j1KWuak2MsD}Ieeg`CVzWx)5Zlqkq{3l|E3;SAr)TkXeb)4e~zLsY*5w4W@q5_dM|5^{|N4XeR=`E{QWO~`{l<?`ClI&|9JTnb`OqAzn}X&E0**miaz5r`^9hrZSl`Z<1Ge!X`-$7hJgpQ;nyP4zK|rZj!(2@zmlTm#C6R=_#nZSk<GMJ2B8jQz*FFq61b)%3U?`kJQwzQRsF}m{_@vf|L2bZ{r<1GrCj+T^o}E=p%tI{dBN;cV!?I%`1RQ9aR!GN;lSK5^6^}Br8-{W@-L4rWXr>OoaZf^dG*!lnj*%8zDjTOQm)(=b*Lx9B9$=l1`eTPsHzht32I5`X4w1EHRQYM>a4<Ctfo`0s`=|9=R&&uqAHVXuMIp}59E*Zj`~Hafq_glJBc4r7zln_345s=PVhjZ=Zs3}`8Q;qwz#90=?)?;s94T}p8dTOw|duXJn+kl+hC_|)-4}Y?dRWnxG~YOU;G4D&{Cpa#q2}eOh=D|2?L7~nuGeqz7))yS(-hC5zR7|Ik)55<+}JZWcHFDkAmT~cS)a4w`2$ggg-sFJycj3cg?4e0-Jr2Dzn?0sD8*b5NYZ#fFVw8AjPZqik#9kEs?_vCjMo{`0MPpH&B8UAld}LaZ7x0j1<R4gfWTMkunT}zqv8^F+R3fWO2-RZKzSHqd*laB{`t*+4#MPqfJ6&F!C~pMx6E>`mXSd5a$%5<z8!j{*=1OOrh>8l|Z&1rv!yT+1C3Hv-Z~NhZU@Y#YAd-su@jWFbTJ}t0K9gU0tXjvr^92wx`9WrfrK^=cr>4Q^WdDML8LxCEJKSmrI2?V71C_vBj8JuatOqE-kyW4iG3)rA`bUKfa1ACRv2IY6d}*C^bnQ&h{21JX#hLuF2lMCeIg;hZCo1KYzJU)y>UXwyLO+DmkA19i20PIIR3(Aw}1kXg<Du%qMJN@$qyki8Ew|JlV<Jq%<F4(tzhOLs$7J?T7*`aJbWY*y>BohJ~+9f`hDq4*A2p<}v?;7Tiyw(*5g}1rQo@c|!Em0OQYONx?n?{wT<XTu1(CvYwZgXp+(Io14d>KXiXMY6<tY)JyGUd84;pnUM3384O+5SdUs^5nppLMK6f!Ydr!P)(%~tw{TvM`fyt`1eQH?gKOCh;f<6fvExK;_d_?{O*ulJlt7$jtV<%1q05zC1Js5p+Vb%2Bb_sSuC<Mu)sj{(d-5ZbMs*u!!%e5EtgYsj5z<UkTbWf|8w%teR;?GWTMay^p%6w@)(M=t?1)uPI~=K$H>HAJEXhInY%)+A`c56LlE~*ALA<>E>b{xr?NIQknRbhVwY_02hpcP>&chla*}9LX!)Lz!@-d0gR^p{ji^>gA`iC+0D@|r7L_*QpPC2$ijY8DnIMhZ=F8p-PAXk^`m3J~=$DzI-L*pUa7@`XG=3NwN>wQf%hkngvoeM0&?68@thKVTvBxD|XgB{LvyoqN3BBnCbPPhoYq>_^$G?ICaij$+uc3`~mDR;TqQt0(iEx@HvK?xUjP-!2TnWjh<h@kUrB+h$z7+h}_-NCeLca?K_S---8zqj0@OT}Q_rx}H>sMr8jJhgE$5@NN&8BzgFyn6Fp7P{-OY2OnptO~Yhn>K2mVZu4Hcx#>o<k_Bye;vcv?wX&Jd{hcd)%-H6xZfnZg7pJU)`+lt-0f}{J3GmYmJ|G#Bf}S_cEd#+dtZEu2$s^DN7FEe(dNaWwu%W<E#i%UAvF@_s2pd&PR*=TBT0^N8lz^iIJ#$6Kj$mF>A~iywlUsu5kroW#C8dFIMYa7ajZzgBzQgdsUjd4jPF(@LO<Mjj@B;v29Y<K$&AVKHOIo08kx_L?(Rri18!qa7gB<6OXD}h(^H==MRH#7`vDl2h?yz1c01=X*y=z`+L;RQXJ7-LtXf^yr@0n7e5|ioIxHl$?S?a1NFMN3ILXwl>czymB^tiab8+SEWlGHRTgz`N0>y-mu`Zb=#L5lF|Bpvx>YMYGUTyDK`A(dmLt}VH*nB8d8=kD2kH3EZd&%Wtyn7+MMT*|teluS~QmZc+*KB~yHI(sSy?oWf;&c0)!Q9z1K);9v%rwy8XrWX|*`S9_hETBPprY)2g0s=84-NkDVJN=gl_IwTf9hfhjtR;3I)EJZ_^_Ta_)GK$tl-K6N}cC=OgGQ0j5`2TGht<Nh`_GOs!CYG+M$!3VkFh|GEWnwOB2VB-l+OSosB+#%^jdQZtnIhI0m{9V(OoU8<h+xDUENmd+XO9>YlW1q}At>ScMPA3jWzV>%U9*b~VX2^6LuK3fRUpu0#QnzlJ6WU>*q!DN1O}DmO@R&Dv`tgwXmLqN8Wn(1}_sO3|P7--JFK;ZY*`T$IjORDA*4aiW7!?QaGT|LdWg$VOztg#re|s!EjI+Jo%>YH+BQJdMn@kj=2_NjS0bbCdn&_wOO~H@cx*xz%Ij8KFVsrl1^eq_RSl=p#b)*n&bWe$5#IU>thKJ1{k=^X3Vs4a?G4XyedVX;p=jRB97!3Nud2>fRBoVKUHP#Jo*|oD8<r=5kz+7$Y7COAu*~Fp<(*cE9*2rHqhpc#u!dkuuxb&Ut)Jc1<+Yr6f=$<Cc&=YES_?pWE8ssa;dbZ60fYWqgiN4mQo1=JROBa}Km>Q{n3@*{{vp;=@&Wl!uk432{tlveDE`;W(@5;l&);6Kk!?B`<ECcQ<5vlD8Z}$8Z;0;f-=;>^scLhiBG%ZDY>3>Tw|4=UM2m*B@B?&9xPg08>{OfIey3yq$xy%GNHl+cBvG0uRK$+Qai^Q%Ya8`4fT_ATBdTNOfI+@%65Ww03VbN67RCRrjYsE2!|6fD#O?^<Ux&%J9$x;~s5UL~sBQDv}_w<k|&3b?%NqPp-*;;~QWC$f@!9YBJ;Z5^SH*{5g@?K1*tR1b}PGOMsA=)O{ZcF_#)~QEGCP#0;n`;vFaL${4BrB8QkO<N4}(;SZ6jSpJC>*u^{B&tevBimt0VqL@&RM_O^)@2tn@cU41qtyWm7ErD9mF%^7xraSF+&&YUJrIT2?<$@NB32H)|Tc*v?j=>IXWxjP*+U8`|0sqUK%ctqAx9me!BS4fteI3JSljn}%Ol?KK(rsW#$jta=VV<=3f}#iUz`!t;pKN$$%p4DJZRr{V)<-u8qb!GGG+SfMg^IQa7oCMO&X9Mz76^Eg3^pT(Lp6-C>+%&2KAuF?;$y=8*!68i4m32VAJfyNX=sBxc0(gxXBO62aWmuVU;4t2-Ix~oK;h&E?J-GvYaZj6@&+dl|6l*|TOuc$RIweq`L;F2ovg_K9pGs!1Y8=9J{0&;K%C})*gCFuQ5PCX9oRbIIdk@|fY;b<w@fpRTTO}BV-$OvwSjD;iU3LLCEG_H`|hp*Cc<FvQY++HSObR^l?q3ZW$cH>*cWY}8B-tj_r}6wKPFWx=0r>CM5pVSr&z<`Pw7582&ju+gn_Z!T4e0!7PlGr37&T-%Sp#VU&XK6WG5iaXsbv#9_nhh9fTLzJxYLvn8!jZg$WqaOh3=7#au-&qCFq{g9{gnE7mT8WU!2dKnk{hKc8LpheOfX>)@p^2UN##=$rT)_U~G5p<#l<;CGQ_sXCTg3~S!OaK^mgFpeic&4XWZ?<`zn{W>SMqCE45Td!>dQ$w5Dq?de6h-5hB<Cl))qm)9SS|eeYE=`scWFG@tUAA?L<O9PD*(x4mODd!I@Ju}jUsu3bQ^mjM6svm>X2Lj+YK?L1T;n8p9-_?tjWpq_S8wcHi$q(+LNFQmhc4SCT|JJ&JM0t6NRdqk98ig0kK<@JvoULQ<x$mgIaPWg=lMBK_V{5E2WamR?F(IKKNcD*2ec}x)LS#pEgh-8QEX}qbS5JePnECUe^S1B9M_f@9TlWFEiwijtb{5V$9Okaxr0l%!@A}N&m74Trg3Z(>jJr15TPMo8ypPA?wV|F8%%-&;^#-$<?dxpZjC?MQB&V2#fNQBgi<Xaqm_!9N=eD%`}J*+5Sd|+6d00JTQRbkFFE`<Fj^)sQ`-s!+Ar=^p~=Ef36eslX%;M?9&#s+am~)7ZX_W$+pUBu!9*kzoRUF#jt?biWRI9}THE4l!fYU(EgxeTr%c;h4b$ooNXN7P1cQ`C;fjD0Dfk!*Ja-L-Nr|~s%bi3#VT@g9n2<U^8f`)Bl;Qx9i!u+kQTpQ11UcnNSR<X<cgHzDk2lOWBV*8l4;Yx>JT<7A(fSPNoH6lDy3Xe^&o;9iEd=vcojqmbW9P+9%#m(00w5-Q1~8!2E|p3EQZ_^!NpXvK_SM-^?;P{o8aYb*0`*#T7Ni336m~mJZ-NII<x9$)4ZwnP%N3Fw<s~88$n-x89VjI^5R5S=Qu>1C4vE%=9_1i4@(T`IINug6O}HwfaE6)goyGVZm(flSQ}G$|fx!Vg!}Oywh}bYGrHDm7i8IHv76d~qcY-=U2_n51Y&O?r7_yT;X(dY{;CsdTzt$qxv%#8(S@CwAh^@i_3<&r%9FZ5B#m{Cgn`LBil8tQ|G+wEZ4)*olh#EcY(oL*7Qq~`xWZl@sst3Pzwu1W?PLQ&0i;JOF$ZQ>bx@QS#4MxxL8eLMi8Laq_GHE6m%bFxO9j$G4-P#I_zAoyk)hIg`>bW}i3f6tHbLCnd*^WrehAsprU#)u<^|z(6X<WV9=O!e2GOVXHEw_S1q6xy=J|+_Hr<1d;jd333f_Q}t54UORxNcb!xgUJP9s2s_R}GMHChiS@kjFJ<nG0EJ`#CzPe*rN`;8VD5IO2^gi>J0eozDaZQ!IoWWhX4&z@>n8+=jL~d!PCYuM_kT&~6Peu5EN%h%nSdm5?;I7(uLlaJ4_5!gLF9`C0M-<7T%O$|@%d=p_I#$P#ZAOc>)T+u}|Ojl-sw%+Z$R8~{s~38MntE4Xxg_j!vJiW&g<U|mTPc?{AALTCTCEhFkp(vuLpt7TXcl5gX-H>{xF3ANP;uvRw+?RTSMfuGP}u7^-<Gs0Knu2PobzPD;XUS7OLNRo?CNN7YoA;L&NDekcHCnpmRMy%VAw=_CU)Fh<=IB3VOddJ&o&6##c5rU%FAPS3lc)Bs5!^l|3bI@ml8p2ol^Dk>O1zsCv@ezdL`rXI)4M}ANrT7pXNG%3zbg%=~hK^Id(Y~ioFgd%Q)^1#toTgvnZ_#NU!RjWQe`yCf?z`@}9a3A!xy}w+YUXj+Idv-R44^63q!ZQ>HG?vW|EJFGFqnshd6zPuy%Oc@rb3H^Jp-=$;Al`tR0WI=*8#qskVTglG&rU+%{oFEl`rxDKU+dg-PEwurbj}`1~sW=>SXV83?07#P?LqOzCg@W2%4ajzNNfG_A4!DAZ+J@jWAKYo#`}`HFMRQ?S@T4O!;jtX@BarMB|SCy{ea~+gqw$7#F{;gDFaVZVOd}%!E+EVv<@aIg*W#aMUF5dUy7{3o;ws%@fUQK_XNWB-e9UTPU>kJtA5b5x>iA|9oCD{n#v%K&vOIB2i;ugFCnLi0LOEBl3|So&iW?zYK!&)2s|Jmm1-V0*KewB7~qW5ZJSe+ct)$XPIs|4L>C2GWBa?u^6xr(t_<hZVz#E`z?X5zy`G?Lh(YJxmrboh<++jXL4fC_(@C6z;jgYQEF>W^jbe8ON55yzR|hC=pW$x4eV#=+sdSbLeJ|u;gjWN%O$N7Hw{C|9}XF-GD=O!nUK9)h}Upf-855x?Fka1N~KR)xkdqigaB0oVGW$7X_#B3Qdu_q;k3Gp8)1N9rkdBAWv6x*Q=Q+CTkUioht=+KjG&lB5k6Q@A?gGr(6XF!*lcbjtrVmYJ~*qL#yQ6bcMWQFHmSv}R?`Vujb$ALdehi7?#o&)w3ZS@LRWS!FHqH-#s+0i6GwRx!PJ}!ITD>ip2p#AeK39+!ZO~|{!A1KA&4%-U~JWin%%NgbwnF3of8YAIu@{d==C(I$`#0hv_LbXYF)s|2VsHH;C2aMAtJ?TPH13Ue!6~CJ;3DZhu*`u=8}zx0%w|<6Z$y>2|mWX`FM;fX97$TD+i{_(xy@MOHh4!S~_A}onck^M`DSo%WJs7Y$>Tw<YZm#{!aaScc0z4ojW{u)m>$x>qR^bwrZM8_zTu<6lfbQ<=y(BX&MuIf=1MKp$H`hB#CR&H08B6uP|xcZI$OK&BQ7NvZwjIYMfL^n<<{Ey<#L?r^VMdPL&#Q{#(Q)B$pd=B<AzUtge11Xa7*{Zek}ym%`T8>49qw(<T*Q9vt(R4M?VGfA6)ynnlqj;T)+A524x4x%zYmQFIyJ4YqLMRLB&uUMj*><j<d@Tp)}NkC;Noh;&z>D6n@WRdH8IHG<-%K1%hZ0~H!a4ZVTl5h6jJ3SBWzCX=W7HLs~LA%|*+s?IpE-C&)WQkxc7*L<Vpi`^+T*Cgf>DAGLDX<q*C<3qEpJ6mYY_#hFZ>zL(41RVctqT}hxO!Jlx6nM=N`-4h{rp~scXv9yu+Viuh@gVjgRx6zBjWaD>ezY|jPDk6Ac}Ys&PD`(I;ej}XK*-&4_!P8ah$!7-?8np=CO#LB*I-8h|By$H%&)LC=)gE9DQ1JM0Q82S9VBkb(M6v9GW&Lc_&>h1Tr$ZIhPot70(WR((10}Bd_~jq)LVVlwoUnAz=+36m)Xx{bI5O(@ScQtOtt+MSIbC0j9fu%T6Vh{3YA|acx$@c&e^;H|7PtHTjXmZ&uph#E@If8+#Dyva_v(mXd=?3!Y5X{pa5bnbd#91Ky=n5o+&AbjP}BQ4qX<$Qu<Pcniga^6a`QfZTBYvSg0sL_6X!T1$~Vjt=?}`X}3N>*F-HV>lWq8wPz^9>tZvA>Zpy0memJX6JNLxJVF@ChNFM0LYB&5NvWxr76MALr$QB}Zk+Q4EPz=KNp}1jBwpmqPS>W8OCkz1b%!51=>>oEa#04bjKM$q7Nr$7-WKfN2F+}}4IilplH)QEuvp$uDm8}cKTPZTIP-@VR?jxr&19+Ih3M%9=m)yB(d;7)+h|Y2czEE32qw>%HME^k@$gR9W1H-GJYttg+|GXec=_1s3uv1YsrO(JWoY1OfqA_ijDWO;M~}HKB6H*E1L`6Kh|rjdK`g>MImLy*lS<aO>gGzZ5QOant&GqZNB8Lkyv4C3z>|5uk5q;;+$;)*mYR=fhbOYAakN(twh(;sG_2Gf<SjU8Z)N^0!1yKjOpYc_5AZor;qC|H9mGlMl6wN<cY2uk<tLGe7ot&|e9I6$rbM1?b<3=LN*#p}6ly6tGj9mo=AM<$nc^&VYf@D~pvvI1>N&=^*iz0`8EbT?+v*#Jh{(RSpB}oUwLzN-HR!-tH(QR^&zeMKJfZM5V+5C!KEE_)-|faGB6;#*o{9{?<#nRflbJi&=Z$+EEnMx|`oN}&?0)Y0h8E>!i`BX|Dv=rsjDIdAp8(+nS@NXrpI~UQOtwpuad&`d=rVV<uCY359K7gTnm7a=)znDuL96fs+xVH_(lKUrzjC$<7jub;FYmyS#Kacc-Lxu%nDAKWZ2%itU3O#^+!vHuJ+elYGHM&ci(Gs~VBIl$E)=6O5;`e;ifrd+W9WUC@xeGa<Ww-l+#4@}eq?LszIV44m!9Utb>>{g6<Bj`(~nul0jc7XFkMBlnEOU<ab{0NF@@J6#x#=}r$656PRnU!8=JZil&A1$YQFj$x&nf=5IEO}0>@|AG+uXDn|lT3ViJ7>U~(=<>VS1Bg`cy?A-S}o$J!Y|h8Zuw+2KqaOe`%tTS`(qf~K3p>r$0!pY+4d#&i6;9Z=C~T~@n?7y}OR>q2{(hfWpvi*g=PoSSF25KpWShpM-34TU<t?=<vz&;|yfCsSxXscniEnwPtA!srW+?c9@E#cdu&zZw!o*-PR^0s;(l!apXW!|3I-?kSO|%nG2>t$41u^m7I!T*03)`Dq&&^~J2_VQEex`Z-&#+?QvS;$6Ag*rJ3>RF;BcEb$_5|K}^B=E1M7fyHfJ2~;y8@^rDkRi0opqp`Dn*%$B+0YM%C{SkY>cF9c_!iD(#^VT1G`_Lg}Pi9pY24UzSQ16K`cbU?dC#8|tK%j|Sm~qUB<bdEu^jzg`r7X&y$H}k9NHjmeD@$`922wQ6w=Q=O#i3W!?4uKWTwG_BNe4Ui^XbOrV6g4PAYh?3uZs)ccugukW10Cp)e?29ca7I884c|tqvr%{(RECzpBSbCrCt-TUXuQHLzq_aY0`P%ivA=uo<ySCmuzO~W>$h}sxiE>g2Vr~7Dvy878I>^5gYZx>Few%RI?{}=@B)zi9Z2^C4{yZ!>D#*;=MH4^idw(eHe*3moNZ^Ip5zJeg?}Y#MD<f82gg%8&bu{iP9%cU;|@ZT^&u9g}@{ncD#^^BPNe>40`ja&!l;#DvAfzUS4@%Y<nYxk9l_PQ`Wlug|My-e9uyp7(#AipiI=HOQxwUv=WpPSY}_t7>q-b&29clZBg^^Mxx66lZYzEP@Ck6nLfLN!~4V2(hsrNRb6idC6}|GClXLs+2vyjv)fm|T2<E@v0B^0ZMC$u&S<ULVyd@cz&@`H2;1WV{mT~KzJDGMb8BHE(TW$l;!3Fv$N3Lv75mT7SoC#j&qtQ;FEB6N8=8QT0t0jeC2N)<UwY{q%K577jZg<k02s+O+4C~E0-{hAG2fZV?;szq`RI!2D)ty{4zfu;jfUHn=^c`xR$ouX@-bwVz}V*;g3T2U!5tdJ1>z`oV4*W5yr`R!A(hX~si7(sHNZ@gLo&H^ZJrDDq|d?eed>;o#|81>2~1`y#VRg8%2nX4LJbq<mnBPcp>+gelf+SGRb;44xMal?x<-s>B$i2AH1*C5ODOb=Vsll1fjYv~|3{cYp<d*eD*h?pRm0UM=nU&?bc}Xvv{ptPX8KP;KFwfZb~T`T9?OMhQC-;L*RHsV2&VK4Sozs4!g+`6ZnLn<NgI7Gv5+<Tw{b~IJ)=OY19otuLBFM&JA_3!#+SJ{nl7IFR(RWA*<CbYQaj9~Sje9}JjuqBI<m@35;%AOQ+RoS^+B94KP71N`u>UYY`*NSy!)A=WM1|pgeSJ%F&H8L(AMo*bX&?Rlte786TsMHou@+`iRBUQ@@2L$q3r?8f++wC0T5$wlVd1$yw2-=X**}K%*-xMBba?7V4*|K=p(6z9C<8qAvTq>1XK^v-AD9cx%S}O-Q?=F=1v=uu!emBrT^>XSR=#Pe8Z8ayOsxIB@sCpo4L>o63uwcpMkYGGL;!gg;1CCyk7UN?FbU}z8-SHiSyz8y7vjIi4k+KZzFpFrsb+QUyFHmDZgtoMOdLJ!&Y*A-GHp&i&G9a^**Nj<+c**hmAq9^VbfAU;ClVg*XwlKeOkvD3v=;1<ktH=gheTx4`jMMZjTun!$jilBtj&!YUzAq6fM=UjL<#V#8Keb(oQs=nH#!pgc7nFackW2x*iUEfiBS1R)`BSGv56O>$HJg|6Vz@mN%6eS540`-0^BF^qqH|NY2gf%p46IL=bY2-P<HvZE20Vzd<s5FAh6Gd-WduZCcXorD;YV!Py2Opmo0&dH4aWLSj{>Hk5MHXmk!Zs{gpKFhzzi9(fb1WSvW+-4_BXCzNuK%x=Ap&DtCN4ylOLFYwt92yFaQGuz;jnciGmO@8}-9dGXR!7`+w^N<`S_&Z{+V4OFZ?*f)G?!SC9Sn1~TOZU=%hMp*dUc%h<IP{rAF;Px-}x)g#ehEiTq#(R2=I<9rVtd8TnjGK69X$RL)3K#V3;cA1izCuaI^svB<y&N$5x#YYV&|&ZmO7*t=Ug*a4#@HO5bATY}OXMwvAYN<I-b{Q?oC)D3y&3U`ZUy=Qr2!aud(~7IE*YKDHE+K>D!YG31L?V*-iL!y-+m7;f92v)PodN(XvDqe{^G;T0msr7g6f!?&u0?U>OnTlTE#PO|QO#sU;i<8!1#=gYsuMWyQSe#jPtU}XJm7fRA~Djf6mc1+y=iDueSih2#+KjWl9mT<-i7rDQ|2c_<i<Eb4(A6sdpLR$sCDfHt*bNiXXwI|@R2k(z>Vb(0e?D`B+xWnv0ZK4)HV7wKyIc91Xfie*|nuf2pQ><q*`0>fGx+C{^c&zsf7`a&(^&IWy7P2Nhbzhu~P9;zaUka@vOYKIX7CD*QOe3PtF&An?EqXTyOQHd;P#SYG*UQ-ZZIik9y;~f>coF_`53X6~+F41<mYTXDk^t6zwAD@N)?(sMU^oVl0LD5s+BZ|qVTm_7cM^6NDnl$W=k`Y6OnibAfYB{YLNY!k;|Gd@k)mPdqz(}^JKpq$S%=rS`518m)Mcbx6_(ICHD<d?W{5|=jL<5$^>H9ok5bAFHI|3jgeFfv7!15`6nJI9<-;vbjNwOC=>nv@Ya&XOMck_o9W`i6Atc0dzGzPZAH2ByUhtcKFkN$7i2YcDb1tK;g>31!vB%7+48s#LAtt2mBITFdEcRNGf<m5&`z^jqiFO~RnJQ>+KdokwVC55upyK?VazENT#u>ZbkzGNAM-y@>uMRLYbx9Smb=Xm&{up=*r7vkgP{l{nV9!>amakae$8W!V{>JCOAL!3N{`vjafBon0n$EFsd7VX<u(E?k*4WXoA%S^rU^jgWL<znTRk+KSR-Zf<WgTtF=Y;aG-TFJtfelGrfIE5uhC{%ig<zTF3EMKW=LLOLCGNUnhn@CATT!_C3*F$yPZo>v<LzV0V~esal&(Ie{9_-VKMW2{Fjw9#I5Vl@I62cyyDXJ~+xpqxu0G!D7tasFud-{ukj2pXf35d1*VQiFbA-i{Qdq@98OL&@8#s<2ifx|%hu2My|Fzo_8{3rz@Rulo`LEUT9Q^mS@7$aPgXY1h^?d7T!Os`0m`)0;gOY_~Q+}(&@s24LN(i6BP~{6s9ET|zLhOlX6Ml|&#x@*HGO<ACzM0Pz+1g9$pHH!f7LVg2c(+L@P#wnj<a+t#KW6*?{lEYB{{xa*CPV')))
_ROUTES={0:_PAYLOAD['base']}
for _rid,_patch in _PAYLOAD['patches'].items():
    _tape=list(_ROUTES[0])
    for _t,_a in _patch: _tape[_t]=_a
    _ROUTES[int(_rid)]=_tape
del _PAYLOAD
_SETTINGS={'hand_align': True, 'weed_repair': True, 'sell_lead': True, 'budget_guard': False, 'room_guard': False, 'clamp_sells': False, 'dead_stock': False, 'terminal_liquidation': False, 'front_run': False}

def _router(observation,step,state):
    if step>=144 and not state.get('day6'):
        shops=_get(_get(observation,'town',{}),'unlocked_shops',[]) or []
        state['route']={('BAKERY', 'YARN_STORE'): 3, ('BRUNCH_SPOT', 'YARN_STORE'): 4, ('FARMERS_MARKET', 'YARN_STORE'): 5, ('ICE_CREAM_SHOP', 'YARN_STORE'): 6, ('PET_CAFE', 'YARN_STORE'): 5, ('PIZZA_SHOP', 'YARN_STORE'): 7, ('SMOOTHIE_SHOP', 'YARN_STORE'): 8, ('YARN_STORE', 'BAKERY'): 9, ('YARN_STORE', 'BRUNCH_SPOT'): 9, ('YARN_STORE', 'FARMERS_MARKET'): 1, ('YARN_STORE', 'ICE_CREAM_SHOP'): 9, ('YARN_STORE', 'PET_CAFE'): 10, ('YARN_STORE', 'PIZZA_SHOP'): 6, ('YARN_STORE', 'SMOOTHIE_SHOP'): 11, ('YARN_STORE', 'YARN_STORE'): 12}.get(tuple(shops[:2]),0)
        state['day6']=True
    if step>=648 and not state.get('day27'):
        state['route']=2
        state['day27']=True
    return state.get('route',0)

_R42_OPENING=[['BUY_PRODUCT', 'WHEAT', 5], ['BUY_PRODUCT', 'WHEAT', 10], ['SELL', 'WHEAT', 60]]
for _r42_tape in _ROUTES.values():
    _r42_tape[0]=dict(_r42_tape[0],market=[list(o) for o in _R42_OPENING])
del _r42_tape
_IMPL=make_agent(_ROUTES,router=_router,**_SETTINGS)
_IMPL.chassis.diagnostics['terminal_rescue_errors']=0

def agent(observation,configuration=None):
    try:
        action=_IMPL(observation,configuration)
        pass
        return action
    except Exception:
        return {'farmer':['PASS'],'hands':[],'market':[]}

_SHOP_PARENT=agent
del agent

def agent(observation,configuration=None):
    action=_SHOP_PARENT(observation,configuration)
    try:
        if _step_of(observation)>=718:
            view=_View(observation,_int(_get(observation,'player',0)),_IMPL.chassis.cfg)
            units=[]
            for i,pos in enumerate(view.positions):
                units.append(['DROP'] if _shed_adjacent(pos,view.board) and view.inv(i) else ['PASS'])
            action={'farmer':units[0],'hands':units[1:],'market':[]}
            projected=_IMPL.chassis._projected_shed(action,view)
            action['market']=[['SELL',item,projected.get(item,0)] for item in PRODUCTS if projected.get(item,0)>0]
            action['market'].sort(key=lambda o:-view.prices.get(o[1],0)*o[2])
    except Exception:
        _IMPL.chassis.diagnostics['terminal_rescue_errors'] += 1
    return action

# EXP-154 modifications: Ahmed Berat Ozer; public capabilities credited below.
# Dmitrii Gluzdov Seven Turn Rescue and Kaggle engine contributors, Apache-2.0.

_UNIT_NS={"__name__":"v28_own_unit_model"}
exec('# SPDX-License-Identifier: Apache-2.0\n# Extracted Kaggle / kaggle-environments contributor code; see NOTICE.txt.\n"""Exact deterministic unit/decay semantics extracted from kaggle-environments 1.32.7.\nSource kaggriculture.py SHA256 bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e.\nNo interpreter, market RNG, policy controls, or replay content is included.\n"""\n\nENGINE_VERSION = "1.32.7"\nSOURCE_SHA256 = "bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e"\n\nCROPS = {\n    "WHEAT":      {"seed": 10, "first_yield_day": 2, "max_yield_day": 4, "interval": 0, "max_yield": 6, "ongoing": False},\n    "CARROT":     {"seed": 20, "first_yield_day": 2, "max_yield_day": 3, "interval": 0, "max_yield": 4, "ongoing": False},\n    "TOMATO":     {"seed": 50, "first_yield_day": 8, "max_yield_day": 8, "interval": 1, "max_yield": 4, "ongoing": True},\n    "STRAWBERRY": {"seed": 100, "first_yield_day": 10, "max_yield_day": 10, "interval": 2, "max_yield": 4, "ongoing": True},\n    "MELON":      {"seed": 80, "first_yield_day": 10, "max_yield_day": 12, "interval": 0, "max_yield": 6, "ongoing": False},\n}\n\nANIMALS = {\n    "GOOSE": {"cost": 300, "structure": "COOP",    "first_yield_day": 4, "interval": 1, "max_held": 4, "product": "EGG"},\n    "COW":   {"cost": 400, "structure": "PASTURE", "first_yield_day": 8, "interval": 2, "max_held": 6, "product": "MILK"},\n    "SHEEP": {"cost": 500, "structure": "PASTURE", "first_yield_day": 6, "interval": 3, "max_held": 6, "product": "WOOL"},\n}\n\nPRODUCTS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]\n\nFARMER_MOVES = {\n    "NORTH": (0, -1),\n    "SOUTH": (0, 1),\n    "EAST":  (1, 0),\n    "WEST":  (-1, 0),\n}\n\ndef _shed_access_tiles(board_size):\n    """Four inner-corner tiles around the shed, in NWSE order."""\n    half = board_size // 2\n    return [(half - 1, half - 1), (half, half - 1), (half - 1, half), (half, half)]\n\ndef _is_shed_adjacent(pos, board_size):\n    return tuple(pos) in {(x, y) for (x, y) in _shed_access_tiles(board_size)}\n\ndef _new_plant(crop, day, turns_per_day):\n    cd = CROPS[crop]\n    return {\n        "kind": "PLANT",\n        "crop": crop,\n        "planted_day": day,\n        "watered_today": False,\n        "consecutive_unwatered": 1,  # planting day counts as unwatered\n        "yield_units": 0 if cd["ongoing"] else 1,\n        "max_lifespan_step": (-1 if cd["ongoing"] else (day + cd["max_yield_day"] + 1) * turns_per_day),\n        "fertilized_until_day": -1,\n    }\n\ndef _new_animal(animal, day):\n    a = ANIMALS[animal]\n    return {\n        "kind": a["structure"],\n        "animal": animal,\n        "placed_day": day,\n        "yield_units": 0,\n        "consecutive_unfed": 0,\n        "fed_today": False,\n        "cared_today": False,\n        "fertilizer_available": False,\n        "pending_care_bonus": 0,\n    }\n\ndef _farmer_position(farm, idx):\n    """idx 0 = main farmer, 1+ = hand index."""\n    if idx == 0:\n        return farm["farmer"]\n    return farm["hands"][idx - 1] if idx - 1 < len(farm["hands"]) else None\n\ndef _set_farmer_position(farm, idx, pos):\n    if idx == 0:\n        farm["farmer"] = list(pos)\n    else:\n        farm["hands"][idx - 1] = list(pos)\n\ndef _farmer_inventory(private, idx):\n    """Inventories list is [main_farmer, *hands]; grow it if idx is past the end."""\n    while len(private["inventories"]) <= idx:\n        private["inventories"].append({})\n    return private["inventories"][idx]\n\ndef _inv_add(inv, item, n=1):\n    inv[item] = inv.get(item, 0) + n\n\ndef _inv_take(inv, item, n=1):\n    if inv.get(item, 0) < n:\n        return False\n    inv[item] -= n\n    if inv[item] == 0:\n        del inv[item]\n    return True\n\ndef _apply_unit_action(farm, private, idx, action, board_size, day, turns_per_day, shed_capacity=100):\n    """Process one farmer/hand\'s action. Invalid / illegal actions are silent no-ops."""\n    if not isinstance(action, list) or not action:\n        return\n    op = action[0]\n    pos = _farmer_position(farm, idx)\n    if pos is None:\n        return\n    fx, fy = pos[0], pos[1]\n    inv = _farmer_inventory(private, idx)\n\n    if op in FARMER_MOVES:\n        dx, dy = FARMER_MOVES[op]\n        nx, ny = fx + dx, fy + dy\n        if not (0 <= nx < board_size and 0 <= ny < board_size):\n            return\n        # Movement onto LOCKED tiles is allowed: a hand can spawn on a locked\n        # shed-access tile, and blocking movement would strand it there forever.\n        # Tile operations (PLANT, WATER, etc.) still no-op on LOCKED tiles.\n        _set_farmer_position(farm, idx, (nx, ny))\n        return\n\n    if op == "PASS":\n        return\n\n    tile = farm["tiles"][fy][fx]\n\n    # Shed operations resolve before the LOCKED guard. They use the tile only as\n    # a standing position -- the shed itself is always owned -- and three of the\n    # four shed-access tiles start LOCKED, so guarding them first would make the\n    # shed unreachable from those tiles.\n    if op == "DROP":\n        if not _is_shed_adjacent((fx, fy), board_size):\n            return\n        shed = private["shed"]\n        for item, n in list(inv.items()):\n            if n <= 0:\n                del inv[item]\n                continue\n            room = max(0, shed_capacity - sum(shed.values()))\n            take = min(n, room)\n            if take > 0:\n                shed[item] = shed.get(item, 0) + take\n            del inv[item]\n        return\n\n    if op == "PICKUP":\n        if not _is_shed_adjacent((fx, fy), board_size):\n            return\n        if len(action) < 2:\n            return\n        item = action[1]\n        n = int(action[2]) if len(action) >= 3 else 1\n        if n <= 0:\n            return\n        # Seeds live in private["seeds"] and are consumed directly by PLANT;\n        # they never pass through farmer inventory or the shed.\n        available = private["shed"].get(item, 0)\n        n = min(n, available)\n        if n <= 0:\n            return\n        private["shed"][item] -= n\n        _inv_add(inv, item, n)\n        return\n\n    if op == "PLACE":\n        if len(action) < 2:\n            return\n        item = action[1]\n        # Animal placement: standing on a matching unoccupied structure. A LOCKED\n        # tile is the string "LOCKED", never a dict, so this branch cannot match\n        # there and PLACE falls through to the shed path below.\n        if (\n            item in ANIMALS\n            and isinstance(tile, dict)\n            and tile.get("kind") == ANIMALS[item]["structure"]\n            and "animal" not in tile\n        ):\n            if _inv_take(inv, item, 1):\n                farm["tiles"][fy][fx] = _new_animal(item, day)\n            return\n        # Shed drop: orthogonally adjacent to the shed; obeys shedCapacity.\n        if _is_shed_adjacent((fx, fy), board_size):\n            n = int(action[2]) if len(action) >= 3 else 1\n            if n <= 0:\n                return\n            n = min(n, inv.get(item, 0))\n            if n <= 0:\n                return\n            current = sum(private["shed"].values())\n            room = max(0, shed_capacity - current)\n            n = min(n, room)\n            if n <= 0:\n                return\n            inv[item] -= n\n            if inv[item] == 0:\n                del inv[item]\n            private["shed"][item] = private["shed"].get(item, 0) + n\n        return\n\n    # Everything below mutates the tile the unit stands on, so it requires that\n    # tile to be owned.\n    if tile == "LOCKED":\n        return\n\n    if op == "PLANT":\n        if len(action) < 2:\n            return\n        crop = action[1]\n        if crop not in CROPS:\n            return\n        if tile is not None:\n            return\n        if private["seeds"].get(crop, 0) <= 0:\n            return\n        private["seeds"][crop] -= 1\n        farm["tiles"][fy][fx] = _new_plant(crop, day, turns_per_day)\n        return\n\n    if op == "WATER":\n        if not (isinstance(tile, dict) and tile.get("kind") == "PLANT"):\n            return\n        if tile["watered_today"]:\n            return\n        tile["watered_today"] = True\n        crop_data = CROPS[tile["crop"]]\n        if not crop_data["ongoing"]:\n            age_days = day - tile["planted_day"]\n            window_start = (crop_data["max_yield_day"] + 1) // 2\n            if window_start <= age_days <= crop_data["max_yield_day"]:\n                bonus = 2 if tile["fertilized_until_day"] >= day else 1\n                tile["yield_units"] = min(crop_data["max_yield"], tile["yield_units"] + bonus)\n        return\n\n    if op == "HARVEST":\n        if not isinstance(tile, dict):\n            return\n        if tile.get("yield_units", 0) <= 0:\n            return\n        if tile.get("kind") == "PLANT":\n            crop_data = CROPS[tile["crop"]]\n            if day - tile["planted_day"] < crop_data["first_yield_day"]:\n                # Ongoing crops only accumulate yield_units after first_yield_day,\n                # so reaching here with yield_units > 0 indicates a bug.\n                if crop_data["ongoing"]:\n                    print(\n                        f"WARNING: HARVEST on immature ongoing {tile[\'crop\']} "\n                        f"(planted day {tile[\'planted_day\']}, current day {day}, "\n                        f"first_yield_day {crop_data[\'first_yield_day\']}, "\n                        f"yield_units {tile[\'yield_units\']}); should never happen"\n                    )\n                return\n            units = tile["yield_units"]\n            tile["yield_units"] = 0\n            _inv_add(inv, tile["crop"], units)\n            if not crop_data["ongoing"]:\n                farm["tiles"][fy][fx] = None\n        elif "animal" in tile:\n            units = tile["yield_units"]\n            tile["yield_units"] = 0\n            _inv_add(inv, ANIMALS[tile["animal"]]["product"], units)\n        return\n\n    if op == "FERTILIZE":\n        if not (isinstance(tile, dict) and tile.get("kind") == "PLANT"):\n            return\n        if not _inv_take(inv, "FERTILIZER", 1):\n            return\n        # Active for `day`, `day+1`, `day+2` (3 days inclusive).\n        tile["fertilized_until_day"] = max(tile.get("fertilized_until_day", -1), day + 2)\n        return\n\n    if op == "DIG":\n        if tile is None:\n            return\n        # Removes plants, weeds, empty coop/pasture. Does NOT remove a placed animal.\n        if isinstance(tile, dict) and "animal" in tile:\n            return\n        farm["tiles"][fy][fx] = None\n        return\n\n    if op == "BUILD_COOP":\n        if tile is not None:\n            return\n        farm["tiles"][fy][fx] = {"kind": "COOP"}\n        return\n\n    if op == "BUILD_PASTURE":\n        if tile is not None:\n            return\n        farm["tiles"][fy][fx] = {"kind": "PASTURE"}\n        return\n\n    if op == "FEED":\n        if not (isinstance(tile, dict) and "animal" in tile):\n            return\n        if tile["fed_today"]:\n            return\n        if not _inv_take(inv, "WHEAT", 1):\n            return\n        tile["fed_today"] = True\n        return\n\n    if op == "COLLECT_FERTILIZER":\n        if not (isinstance(tile, dict) and "animal" in tile):\n            return\n        if not tile["fertilizer_available"]:\n            return\n        tile["fertilizer_available"] = False\n        _inv_add(inv, "FERTILIZER", 1)\n        return\n\n    if op == "CARE":\n        if not (isinstance(tile, dict) and "animal" in tile):\n            return\n        if tile["cared_today"]:\n            return\n        tile["cared_today"] = True\n        return\n\ndef _decay_plants(farm, step):\n    board_size = len(farm["tiles"])\n    for y in range(board_size):\n        for x in range(board_size):\n            tile = farm["tiles"][y][x]\n            if not isinstance(tile, dict) or tile.get("kind") != "PLANT":\n                continue\n            mls = tile["max_lifespan_step"]\n            if mls < 0 or step < mls:\n                continue\n            if (step - mls) % 2 != 0:\n                continue\n            tile["yield_units"] -= 1\n            if tile["yield_units"] <= 0:\n                farm["tiles"][y][x] = {"kind": "WEED"}\n\n',_UNIT_NS)
_PLANNER_NS=dict(_UNIT_NS)
exec('"""E182 modification: Shop0909 last-seven-turn physical closure planner.\n\nNo engine imports, policy tapes, replay fixtures, RNG or remote calls.\nThe only supported market continuation is SELL; unknown execution abstains.\n"""\nfrom copy import deepcopy\nfrom time import perf_counter\nSTART, FINAL = (712, 718)\nOPS = set(FARMER_MOVES) | {\'PASS\', \'DROP\', \'PICKUP\', \'PLACE\', \'PLANT\', \'WATER\', \'HARVEST\', \'FERTILIZE\', \'DIG\', \'BUILD_COOP\', \'BUILD_PASTURE\', \'FEED\', \'CARE\', \'COLLECT_FERTILIZER\'}\nITEMS = tuple(PRODUCTS) + tuple(ANIMALS)\n\nclass Unsupported(ValueError):\n    pass\n\ndef _get(obj, key, default=None):\n    return obj.get(key, default) if isinstance(obj, dict) else getattr(obj, key, default)\n\ndef _settings(config):\n    size, turns, last = (_get(config, k, d) for k, d in [(\'boardSize\', 10), (\'turnsPerDay\', 24), (\'episodeSteps\', 720)])\n    if (size, turns, last) != (10, 24, 720):\n        raise Unsupported(\'requires pinned 10x10/24/720 terminal window\')\n    cap = int(_get(config, \'shedCapacity\', 100))\n    orders = min(10, int(_get(config, \'maxMarketOrdersPerTurn\', 10)))\n    if cap < 1 or orders < 1:\n        raise Unsupported(\'invalid capacity/order limit\')\n    return (size, turns, cap, orders)\n\ndef physical_state(obs):\n    """Comparable own physical state; market prices and bank are intentionally excluded."""\n    seat = int(_get(obs, \'player\', 0))\n    farm = _get(obs, \'farms\')[seat]\n    return ({k: v for k, v in farm.items() if k != \'money\'}, _get(obs, \'private\'))\n\ndef _commands(action, n):\n    return [action.get(\'farmer\', [\'PASS\']), *action.get(\'hands\', [])][:n] + [[\'PASS\'] for _ in range(max(0, n - 1 - len(action.get(\'hands\', []))))]\n\ndef _clone_state(farm, private):\n    f = dict(farm)\n    f[\'tiles\'] = [[dict(tile) if isinstance(tile, dict) else tile for tile in row] for row in farm[\'tiles\']]\n    f[\'farmer\'] = list(farm[\'farmer\'])\n    f[\'hands\'] = [list(pos) for pos in farm[\'hands\']]\n    f[\'unlocked_quadrants\'] = list(farm[\'unlocked_quadrants\'])\n    pr = dict(private)\n    pr[\'shed\'], pr[\'seeds\'] = (dict(private[\'shed\']), dict(private[\'seeds\']))\n    pr[\'inventories\'] = [dict(inv) for inv in private[\'inventories\']]\n    return (f, pr)\n\ndef _clone_schedule(schedule):\n    result = []\n    for action in schedule:\n        value = dict(action)\n        if \'farmer\' in action:\n            value[\'farmer\'] = list(action[\'farmer\'])\n        for key in [\'hands\', \'market\']:\n            if key in action:\n                value[key] = [list(command) for command in action[key]]\n        result.append(value)\n    return result\n\ndef _validate(schedule, n, orders):\n    for action in schedule:\n        if not isinstance(action, dict) or set(action) - {\'farmer\', \'hands\', \'market\'}:\n            raise Unsupported(\'unknown action shape\')\n        if not isinstance(action.get(\'hands\', []), list):\n            raise Unsupported(\'hands must be a list\')\n        for command in [action.get(\'farmer\', [\'PASS\']), *action.get(\'hands\', [])]:\n            if not isinstance(command, list) or not command or command[0] not in OPS:\n                raise Unsupported(\'unknown/malformed unit operation\')\n            if command[0] in {\'PICKUP\', \'PLACE\', \'PLANT\'}:\n                if len(command) < 2 or command[1] not in ITEMS:\n                    raise Unsupported(\'unknown unit item\')\n                if len(command) > 2 and (not isinstance(command[2], int)):\n                    raise Unsupported(\'noninteger unit quantity\')\n        market = action.get(\'market\', [])\n        if not isinstance(market, list) or len(market) > orders:\n            raise Unsupported(\'market order shape/cap\')\n        for order in market:\n            if not isinstance(order, list) or len(order) != 3 or order[0] != \'SELL\' or (order[1] not in PRODUCTS) or (not isinstance(order[2], int)) or (order[2] <= 0):\n                raise Unsupported(\'baseline market must contain positive integer SELL only\')\n\ndef liquidation(shed, inherited_market, max_orders=10):\n    """Use actual post-unit stock; retain first parent item ordering, then stable product order."""\n    items = []\n    for order in inherited_market:\n        if order[1] not in items:\n            items.append(order[1])\n    items += [item for item in PRODUCTS if item not in items]\n    orders = [[\'SELL\', item, int(shed.get(item, 0))] for item in items if shed.get(item, 0) > 0]\n    if len(orders) > min(10, max_orders):\n        raise Unsupported(\'actual final stock exceeds order slots\')\n    return orders\n\ndef shop_liquidation(farm, private, prices):\n    """Exact original final worker/drop and market rule, with current stock/prices."""\n    return liquidate(FarmView({\'player\': 0, \'farms\': [farm], \'private\': private, \'market\': {\'prices\': prices}}))\n\ndef simulate(obs, config, schedule, *, final_liquidate=False, detailed=False, preserve_final_commands=False):\n    """Exact own unit/decay and SELL-stock transitions. No claim to simulate shared prices."""\n    size, turns, cap, order_cap = _settings(config)\n    step = int(_get(obs, \'step\', -1))\n    if step < START or step + len(schedule) - 1 > FINAL or (not schedule):\n        raise Unsupported(\'outside 712..718; no day boundary or terminal auto-drop\')\n    if any(((t + 1) % turns == 0 for t in range(step, step + len(schedule)))):\n        raise Unsupported(\'day boundary\')\n    farm0, private0 = physical_state(obs)\n    farm, private = _clone_state(farm0, private0)\n    n = 1 + len(farm[\'hands\'])\n    if len(private[\'inventories\']) != n or n > 32:\n        raise Unsupported(\'invalid/unbounded worker inventory shape\')\n    _validate(schedule, n, order_cap)\n    deposited = [dict() for _ in range(n)]\n    sold = {}\n    snapshots, rows, events = ([], [], [])\n    executed = _clone_schedule(schedule)\n    overflow = 0\n    for offset, action in enumerate(executed):\n        t = step + offset\n        if detailed:\n            snapshots.append(_clone_state(farm, private))\n        if t == FINAL and (not preserve_final_commands):\n            action = shop_liquidation(farm, private, _get(obs, \'market\')[\'prices\'])\n            executed[offset] = action\n        all_commands = [action.get(\'farmer\', [\'PASS\']), *action.get(\'hands\', [])]\n        demand = {}\n        for command in all_commands:\n            if command[0] == \'PLANT\':\n                demand[command[1]] = demand.get(command[1], 0) + 1\n        blocked = {item for item, count in demand.items() if count > private[\'seeds\'].get(item, 0)}\n        for actor, command in enumerate(_commands(action, n)):\n            if command[0] == \'PLANT\' and command[1] in blocked:\n                command = [\'PASS\']\n            pos = farm[\'farmer\'] if actor == 0 else farm[\'hands\'][actor - 1]\n            xy = tuple(pos)\n            inv = private[\'inventories\'][actor]\n            before_inv = dict(inv) if command[0] in {\'DROP\', \'HARVEST\', \'COLLECT_FERTILIZER\'} else None\n            before_shed = dict(private[\'shed\']) if command[0] in {\'DROP\', \'PLACE\'} else None\n            _apply_unit_action(farm, private, actor, command, size, t // turns, turns, cap)\n            if before_shed is not None:\n                delta = {item: amount - before_shed.get(item, 0) for item, amount in private[\'shed\'].items() if amount > before_shed.get(item, 0)}\n                for item, amount in delta.items():\n                    deposited[actor][item] = deposited[actor].get(item, 0) + amount\n                if delta:\n                    events.append({\'offset\': offset, \'actor\': actor, \'op\': command[0], \'xy\': xy, \'deposited\': delta})\n                if command[0] == \'DROP\':\n                    overflow += sum((max(0, amount - inv.get(item, 0) - delta.get(item, 0)) for item, amount in before_inv.items()))\n            if command[0] in {\'HARVEST\', \'COLLECT_FERTILIZER\'}:\n                delta = {item: amount - before_inv.get(item, 0) for item, amount in inv.items() if amount > before_inv.get(item, 0)}\n                if delta:\n                    events.append({\'offset\': offset, \'actor\': actor, \'op\': command[0], \'xy\': xy, \'acquired\': delta})\n        pre_market = dict(private[\'shed\'])\n        if t == FINAL and preserve_final_commands and final_liquidate:\n            action[\'market\'] = liquidation(pre_market, [], order_cap)\n            prices = _get(obs, \'market\')[\'prices\']\n            action[\'market\'].sort(key=lambda order: -int(prices.get(order[1], 0)) * order[2])\n        for _, item, requested in action.get(\'market\', []):\n            quantity = min(requested, private[\'shed\'].get(item, 0), 99999)\n            if quantity > 0:\n                private[\'shed\'][item] -= quantity\n                sold[item] = sold.get(item, 0) + quantity\n        _decay_plants(farm, t)\n        rows.append({\'pre_market_shed\': pre_market, \'post_market_shed\': dict(private[\'shed\']), \'deposited_by_actor\': [dict(v) for v in deposited], \'sold\': dict(sold)})\n    if detailed:\n        snapshots.append(_clone_state(farm, private))\n    return {\'rows\': rows, \'states\': snapshots, \'events\': events, \'actions\': executed, \'overflow_units\': overflow, \'farm\': farm, \'private\': private, \'sold\': sold}\n\ndef _ge(left, right):\n    return all((left.get(item, 0) >= value for item, value in right.items()))\n\ndef dominates(candidate, baseline):\n    """Preserve every baseline worker\'s actual deposit prefixes and shed availability."""\n    if candidate[\'overflow_units\']:\n        return False\n    for new, old in zip(candidate[\'rows\'], baseline[\'rows\']):\n        if not _ge(new[\'pre_market_shed\'], old[\'pre_market_shed\']):\n            return False\n        if not _ge(new[\'sold\'], old[\'sold\']):\n            return False\n        if any((not _ge(a, b) for a, b in zip(new[\'deposited_by_actor\'], old[\'deposited_by_actor\']))):\n            return False\n    return True\n\ndef _value(run, prices):\n    shed = run[\'private\'][\'shed\']\n    return sum(((run[\'sold\'].get(item, 0) + shed.get(item, 0)) * prices[item] for item in PRODUCTS))\n\ndef _walk(start, end):\n    x, y = start\n    tx, ty = end\n    return [[\'EAST\']] * max(0, tx - x) + [[\'WEST\']] * max(0, x - tx) + [[\'SOUTH\']] * max(0, ty - y) + [[\'NORTH\']] * max(0, y - ty)\n\ndef _return(pos):\n    targets = _shed_access_tiles(10)\n    target = min(targets, key=lambda xy: (abs(pos[0] - xy[0]) + abs(pos[1] - xy[1]), targets.index(xy)))\n    return _walk(pos, target) + [[\'DROP\']]\n\ndef _proposals(run, actor, prices, max_per_actor):\n    """One/two resource bundles plus direct carry closure, replacing a baseline suffix."""\n    owners = {}\n    for event in run[\'events\']:\n        if \'acquired\' in event:\n            owners.setdefault((tuple(event[\'xy\']), event[\'op\']), set()).add(event[\'actor\'])\n    proposals = []\n    seen = set()\n    horizon = len(run[\'rows\'])\n    for offset in range(horizon):\n        farm, private = run[\'states\'][offset]\n        pos = tuple(farm[\'farmer\'] if actor == 0 else farm[\'hands\'][actor - 1])\n        inventory = private[\'inventories\'][actor]\n        carried = sum((prices.get(item, 0) * count for item, count in inventory.items()))\n        prefix_deposits = run[\'rows\'][offset - 1][\'deposited_by_actor\'][actor] if offset else {}\n        future_deposits = run[\'rows\'][-1][\'deposited_by_actor\'][actor]\n        obligation = sum((prices.get(item, 0) * (count - prefix_deposits.get(item, 0)) for item, count in future_deposits.items()))\n        bundles = []\n        for y, row in enumerate(farm[\'tiles\']):\n            for x, tile in enumerate(row):\n                if not isinstance(tile, dict):\n                    continue\n                xy, operations, value = ((x, y), [], 0)\n                if tile.get(\'yield_units\', 0) > 0:\n                    item = tile.get(\'crop\') if tile.get(\'kind\') == \'PLANT\' else ANIMALS.get(tile.get(\'animal\'), {}).get(\'product\')\n                    mature = item and (\'animal\' in tile or (START + offset) // 24 - tile[\'planted_day\'] >= CROPS[item][\'first_yield_day\'])\n                    if mature and (not owners.get((xy, \'HARVEST\'), set()) - {actor}):\n                        operations.append([\'HARVEST\'])\n                        value += prices[item] * tile[\'yield_units\']\n                if tile.get(\'fertilizer_available\') and \'animal\' in tile and (not owners.get((xy, \'COLLECT_FERTILIZER\'), set()) - {actor}):\n                    operations.append([\'COLLECT_FERTILIZER\'])\n                    value += prices[\'FERTILIZER\']\n                if operations:\n                    distance = len(_walk(pos, xy)) + len(operations) + len(_return(xy))\n                    if distance <= horizon - offset:\n                        bundles.append((xy, operations, value, distance))\n        bundles.sort(key=lambda b: (-b[2] / b[3], -b[2], b[0]))\n        variants = [([], carried)] if carried else []\n        for xy, ops, value, _ in bundles[:6]:\n            variants.append(([(xy, ops)], carried + value))\n        for first in bundles[:3]:\n            for second in bundles[:3]:\n                if first[0] != second[0]:\n                    variants.append(([(first[0], first[1]), (second[0], second[1])], carried + first[2] + second[2]))\n        for stops, value in variants:\n            route, cursor = ([], pos)\n            for xy, ops in stops:\n                route += _walk(cursor, xy) + ops\n                cursor = xy\n            route += _return(cursor)\n            if len(route) > horizon - offset:\n                continue\n            route += [[\'PASS\']] * (horizon - offset - len(route))\n            key = (offset, tuple((tuple(c) for c in route)))\n            if key not in seen:\n                seen.add(key)\n                proposals.append((value - obligation, offset, route, len(stops)))\n    proposals.sort(key=lambda p: (-p[0], p[1], p[2]))\n    direct = [p for p in proposals if p[3] == 0 and p[0] > 0][:2]\n    chosen = direct + [p for p in proposals if p not in direct]\n    return chosen[:max_per_actor]\n\ndef plan_terminal(obs, config, baseline_remaining, *, max_simulations=64, passes=1, proposals_per_actor=4):\n    """At 712 accept seven actions; positive physical delivery is mandatory."""\n    begun = perf_counter()\n    fallback = {\'accepted\': False, \'reason\': \'\', \'actions\': None, \'simulations\': 0}\n    try:\n        if int(_get(obs, \'step\', -1)) != START or len(baseline_remaining) != FINAL - START + 1:\n            raise Unsupported(\'planning requires step 712 and exactly seven actions through 718\')\n        max_simulations = min(256, max(1, int(max_simulations)))\n        passes = min(2, max(1, int(passes)))\n        proposals_per_actor = min(16, max(1, int(proposals_per_actor)))\n        baseline = simulate(obs, config, baseline_remaining, detailed=True)\n        prices = {item: max(1, float(_get(obs, \'market\', {}).get(\'prices\', {}).get(item, 1))) for item in PRODUCTS}\n        current, best = (_clone_schedule(baseline_remaining), baseline)\n        baseline_value = best_value = _value(baseline, prices)\n        changes, simulations = ([], 0)\n        n = len(baseline[\'private\'][\'inventories\'])\n        for sweep in range(passes):\n            improved = False\n            for actor in range(n):\n                winner = None\n                for _, offset, route, bundle_count in _proposals(best, actor, prices, proposals_per_actor):\n                    if simulations >= max_simulations:\n                        break\n                    trial = _clone_schedule(current)\n                    for i, command in enumerate(route, offset):\n                        if actor == 0:\n                            trial[i][\'farmer\'] = command\n                        else:\n                            trial[i].setdefault(\'hands\', [])\n                            while len(trial[i][\'hands\']) < n - 1:\n                                trial[i][\'hands\'].append([\'PASS\'])\n                            trial[i][\'hands\'][actor - 1] = command\n                    evaluated = simulate(obs, config, trial)\n                    simulations += 1\n                    score = _value(evaluated, prices)\n                    if score > best_value and dominates(evaluated, baseline):\n                        required = {(tuple(e[\'xy\']), e[\'op\'], e[\'actor\']): e[\'acquired\'] for e in best[\'events\'] if \'acquired\' in e and e[\'actor\'] != actor}\n                        acquired = {}\n                        for e in evaluated[\'events\']:\n                            if \'acquired\' in e:\n                                key = (tuple(e[\'xy\']), e[\'op\'], e[\'actor\'])\n                                dst = acquired.setdefault(key, {})\n                                for item, amount in e[\'acquired\'].items():\n                                    dst[item] = dst.get(item, 0) + amount\n                        if all((_ge(acquired.get(k, {}), v) for k, v in required.items())):\n                            winner, best_value = ((trial, offset, bundle_count), score)\n                if winner:\n                    current, offset, bundle_count = winner\n                    best = simulate(obs, config, current, detailed=True)\n                    changes.append({\'pass\': sweep, \'actor\': actor, \'from_step\': START + offset, \'resource_bundles\': bundle_count, \'estimated_stock_value\': best_value})\n                    improved = True\n                if simulations >= max_simulations:\n                    break\n            if not improved or simulations >= max_simulations:\n                break\n        if not changes or best_value <= baseline_value:\n            return {**fallback, \'reason\': \'no positive physical delivery gain\', \'simulations\': simulations, \'changed_workers\': [], \'changes\': [], \'certificate\': {\'stock_value_gain_at_initial_prices\': 0, \'sold_unit_delta\': dict.fromkeys(PRODUCTS, 0)}, \'planning_ms\': (perf_counter() - begun) * 1000}\n        final = simulate(obs, config, current, final_liquidate=True, detailed=True)\n        physical = simulate(obs, config, current)\n        if not dominates(physical, baseline):\n            raise Unsupported(\'no zero-overflow dominating continuation\')\n        delta = {item: final[\'sold\'].get(item, 0) - baseline[\'sold\'].get(item, 0) for item in PRODUCTS}\n        deposited_gain = any((final[\'rows\'][-1][\'deposited_by_actor\'][actor].get(item, 0) > baseline[\'rows\'][-1][\'deposited_by_actor\'][actor].get(item, 0) for actor in range(n) for item in PRODUCTS))\n        worker_change = any((_commands(new, n) != _commands(old, n) for new, old in zip(final[\'actions\'], baseline[\'actions\'])))\n        accepted = worker_change and deposited_gain and any((v > 0 for v in delta.values())) and all((v >= 0 for v in delta.values()))\n        plan = {\'accepted\': accepted, \'reason\': \'joint physical dominance\' if accepted else \'no improvement\', \'baseline\': _clone_schedule(baseline_remaining), \'actions\': final[\'actions\'], \'expected_states\': final[\'states\'][:-1], \'simulations\': simulations, \'changes\': changes, \'abandoned\': False, \'changed_workers\': sorted({c[\'actor\'] for c in changes}), \'certificate\': {\'baseline_rows\': baseline[\'rows\'], \'physical_rows\': physical[\'rows\'], \'baseline_overflow\': baseline[\'overflow_units\'], \'candidate_overflow\': final[\'overflow_units\'], \'sold_unit_delta\': delta, \'stock_value_gain_at_initial_prices\': best_value - baseline_value, \'baseline_final_shed\': baseline[\'private\'][\'shed\'], \'final_shed\': final[\'private\'][\'shed\'], \'positive_physical_deposit_gain\': deposited_gain, \'markets_712_717_unchanged\': all((final[\'actions\'][i].get(\'market\', []) == baseline_remaining[i].get(\'market\', []) for i in range(FINAL - START)))}}\n    except (Unsupported, KeyError, TypeError, ValueError, IndexError) as exc:\n        plan = {**fallback, \'reason\': str(exc)}\n    plan[\'planning_ms\'] = (perf_counter() - begun) * 1000\n    return plan\n\ndef _effective_action(action, n):\n    return (_commands(action, n), action.get(\'market\', []))\n\ndef _recover_observed(obs, config, parent_action, plan):\n    """Bounded cargo salvage after deviation; never resume old positional commands."""\n    farm, private = physical_state(obs)\n    positions = [farm[\'farmer\'], *farm[\'hands\']]\n    remaining = FINAL - int(_get(obs, \'step\')) + 1\n    room = max(0, int(_get(config, \'shedCapacity\', 100)) - sum(private[\'shed\'].values()))\n    commands = []\n    problems = []\n    prices = _get(obs, \'market\', {}).get(\'prices\', {})\n    for actor, (pos, inv) in enumerate(zip(positions, private[\'inventories\'])):\n        command = [\'PASS\']\n        if any((v > 0 for v in inv.values())):\n            route = _return(pos)\n            if len(route) > remaining:\n                problems.append({\'actor\': actor, \'reason\': \'unreachable cargo\'})\n            elif len(route) > 1:\n                command = route[0]\n            elif sum((max(0, q) for q in inv.values())) <= room:\n                command = [\'DROP\']\n                room -= sum((max(0, q) for q in inv.values()))\n            else:\n                items = [item for item in PRODUCTS if inv.get(item, 0) > 0]\n                if room and items:\n                    item = max(items, key=lambda i: (prices.get(i, 1) * min(inv[i], room), -PRODUCTS.index(i)))\n                    quantity = min(inv[item], room)\n                    command = [\'PLACE\', item, quantity]\n                    room -= quantity\n                else:\n                    problems.append({\'actor\': actor, \'reason\': \'no shed capacity\'})\n        commands.append(command)\n    action = {\'farmer\': commands[0], \'hands\': commands[1:], \'market\': deepcopy(parent_action.get(\'market\', []))}\n    if int(_get(obs, \'step\')) == FINAL:\n        action[\'market\'] = []\n        action = simulate(obs, config, [action], final_liquidate=True, preserve_final_commands=True)[\'actions\'][0]\n    plan[\'recovery_steps\'] = plan.get(\'recovery_steps\', 0) + 1\n    if problems:\n        plan.setdefault(\'recovery_failures\', []).append({\'step\': int(_get(obs, \'step\')), \'problems\': problems})\n    return action\n\ndef terminal_action(obs, config, parent_action, plan):\n    """Canonical guard, pre-deviation abstention, observed recovery after deviation."""\n    step = int(_get(obs, \'step\', -1))\n    if not plan or not plan.get(\'accepted\') or (not START <= step <= FINAL):\n        return parent_action\n    if plan.get(\'abandoned\'):\n        return _recover_observed(obs, config, parent_action, plan) if plan.get(\'deviated\') else parent_action\n    index = step - START\n    n = 1 + len(physical_state(obs)[0][\'hands\'])\n    mismatch = physical_state(obs) != plan[\'expected_states\'][index] or _effective_action(parent_action, n) != _effective_action(plan[\'baseline\'][index], n)\n    if mismatch:\n        plan[\'abandoned\'] = True\n        plan[\'abandon_step\'] = step\n        plan[\'reason\'] = \'physical observation or effective baseline action diverged\'\n        plan[\'safety_failure\'] = True\n        return _recover_observed(obs, config, parent_action, plan) if plan.get(\'deviated\') else parent_action\n    result = deepcopy(plan[\'actions\'][index])\n    if step == FINAL:\n        farm, private = physical_state(obs)\n        result = shop_liquidation(farm, private, _get(obs, \'market\')[\'prices\'])\n    if _commands(result, n) != _commands(parent_action, n):\n        plan[\'deviated\'] = True\n    return result',_PLANNER_NS)
# EXP-154 integration by Ahmed Berat Ozer, derived from Dmitrii Gluzdov E182.
# The preserved v27 parent is simulated on a private shadow only at step 712.
_PRE_TERMINAL_AGENT=agent
del agent
_TERMINAL_PLANS={}
_TERMINAL_PREVIOUS={}
_UPGRADE_STATS={'planning_calls':0,'accepted':0,'changed_steps':0,'aborted':0,'shadow_declines':0,'errors':0,'max_planning_ms':0.0}

def _parent_liquidate(farm, private, prices):
    # Exactly v27's final projected DROP ordering, in the planner's private state.
    view=_View({'player':0,'farms':[farm],'private':private,'market':{'prices':prices}},0,_IMPL.chassis.cfg)
    commands=[['DROP'] if _shed_adjacent(pos,view.board) and view.inv(i) else ['PASS'] for i,pos in enumerate(view.positions)]
    action={'farmer':commands[0],'hands':commands[1:],'market':[]}
    stock=_IMPL.chassis._projected_shed(action,view)
    action['market']=[['SELL',item,stock.get(item,0)] for item in PRODUCTS if stock.get(item,0)>0]
    action['market'].sort(key=lambda o:-view.prices.get(o[1],0)*o[2])
    return action

_PLANNER_NS['shop_liquidation']=_parent_liquidate

def _shadow_terminal(obs,config):
    seat=int(obs['player']);chassis=_IMPL.chassis
    state=chassis.players.get(seat)
    if not state or state.get('last_step')!=711 or state.get('route')!=2:
        return None
    # No delayed weed/structure intervention may depend on an unmodeled future.
    if state.get('pending'):
        return None
    shadow=copy.copy(chassis);shadow.players=copy.deepcopy(chassis.players)
    shadow.diagnostics={k:0 for k in chassis.diagnostics}
    projected=copy.deepcopy(obs);baseline=[];states=[]
    for step in range(712,719):
        projected['step']=step;projected['day']=step//24;projected['hour']=step%24
        states.append(copy.deepcopy(shadow.players[seat]))
        action=shadow.act(projected,config)
        if step==718:
            action=_parent_liquidate(projected['farms'][seat],projected['private'],projected['market']['prices'])
        else:
            market=action.get('market',[])
            if len(market)!=9 or {o[1] for o in market}!=set(PRODUCTS) or any(o[0]!='SELL' or len(o)!=3 or type(o[2]) is not int or o[2]<100 for o in market):
                return None
        if any(shadow.diagnostics.values()):return None
        run=_PLANNER_NS['simulate'](projected,config,[action])
        if run['actions'][0]!=action:return None
        baseline.append(action)
        run['farm']['money']=projected['farms'][seat]['money']
        projected['farms'][seat]=run['farm'];projected['private']=run['private']
    return baseline,states

def agent(observation,configuration=None):
    try:
        step=int(observation['step']);seat=int(observation['player'])
    except Exception:
        return _PRE_TERMINAL_AGENT(observation,configuration)
    previous=_TERMINAL_PREVIOUS.get(seat)
    if step==0 or (previous is not None and step<=previous):_TERMINAL_PLANS.pop(seat,None)
    _TERMINAL_PREVIOUS[seat]=step
    plan=_TERMINAL_PLANS.get(seat)
    if plan and plan.get('accepted') and 712<=step<=718:
        if previous!=step-1:plan.update(abandoned=True,reason='nonconsecutive callback')
        try:
            result=_PLANNER_NS['terminal_action'](observation,configuration,plan['baseline'][step-712],plan)
            if plan.get('abandoned'):
                if not plan.get('abort_counted'):
                    plan['abort_counted']=True;_UPGRADE_STATS['aborted']+=1
                if not plan.get('deviated'):
                    _IMPL.chassis.players[seat]=copy.deepcopy(plan['parent_states_before'][step-712])
                    _TERMINAL_PLANS.pop(seat,None)
                    return _PRE_TERMINAL_AGENT(observation,configuration)
            _UPGRADE_STATS['changed_steps']+=int(result!=plan['baseline'][step-712])
            return result
        except Exception:
            _UPGRADE_STATS['errors']+=1
            if plan.get('deviated'):
                try:return _PLANNER_NS['_recover_observed'](observation,configuration,plan['baseline'][step-712],plan)
                except Exception:return _parent_liquidate(observation['farms'][seat],observation['private'],observation['market']['prices'])
    if step!=712:return _PRE_TERMINAL_AGENT(observation,configuration)
    _UPGRADE_STATS['planning_calls']+=1
    try:shadow=_shadow_terminal(observation,configuration)
    except (ValueError,KeyError,TypeError,IndexError):shadow=None
    if shadow is None:
        _UPGRADE_STATS['shadow_declines']+=1
        return _PRE_TERMINAL_AGENT(observation,configuration)
    baseline,states=shadow
    actual=_PRE_TERMINAL_AGENT(observation,configuration)
    if actual!=baseline[0]:
        _UPGRADE_STATS['shadow_declines']+=1;return actual
    try:
        plan=_PLANNER_NS['plan_terminal'](observation,configuration,baseline,max_simulations=64,passes=1,proposals_per_actor=4)
        _UPGRADE_STATS['max_planning_ms']=max(_UPGRADE_STATS['max_planning_ms'],plan.get('planning_ms',0.0))
        if not plan.get('accepted'):return actual
        plan['parent_states_before']=states;_TERMINAL_PLANS[seat]=plan
        _UPGRADE_STATS['accepted']+=1
        result=_PLANNER_NS['terminal_action'](observation,configuration,actual,plan)
        _UPGRADE_STATS['changed_steps']+=int(result!=actual)
        return result
    except Exception:
        _UPGRADE_STATS['errors']+=1;return actual

agent.telemetry=_UPGRADE_STATS

# EXP-154: aurax7 Reactive v2 day-end storage guard, adapted to our v27 view.
_PRE_ROOM_AGENT=agent
del agent
_ROOM_STATS={'changed_turns':0,'added_units':0,'errors':0}
def agent(observation,configuration=None):
    action=_PRE_ROOM_AGENT(observation,configuration)
    try:
        step=_step_of(observation)
        if step%24!=23:return action
        view=_View(observation,_int(_get(observation,'player',0)),_IMPL.chassis.cfg)
        carried=sum(max(0,int(n)) for inv in view.invs for n in inv.values())
        needed=sum(view.shed.values())+carried-99
        if needed<=0:return action
        planned={}
        for o in action.get('market',[]):
            if o and o[0]=='SELL' and len(o)>=3:planned[o[1]]=planned.get(o[1],0)+max(0,int(o[2]))
        result=copy.deepcopy(action);added=0
        for item in sorted(PRODUCTS,key=lambda it:-int(view.prices.get(it,0))):
            qty=min(needed,max(0,view.shed.get(item,0)-planned.get(item,0)))
            if qty<=0:continue
            if len(result['market'])>=10:break
            result['market'].append(['SELL',item,qty]);needed-=qty;added+=qty
            if needed<=0:break
        if added:_ROOM_STATS['changed_turns']+=1;_ROOM_STATS['added_units']+=added
        return result
    except Exception:
        _ROOM_STATS['errors']+=1;return action

agent.telemetry=_ROOM_STATS

# Incorporated upstream attribution and change notice:
# E182 Shop0909 + terminal physical closure (modified 2026-09-09)
# 
# The active public parent is Yusuke Hayashi's yhay81/shop-router-0909 v3.
# router_parent.py and actions.json are exact original bytes, not newly authored
# routes. The parent credits aurax7's Reactive Router for sale timing and shed
# projection; that attribution remains in router_parent.py. Original payload
# LICENSE.txt is preserved unchanged (Apache License 2.0 text); it contains no
# named copyright grantor and no separate NOTICE was supplied. No additional
# ownership, endorsement, or upstream replay-data rights claim is made.
# 
# Local changes: separate main.py/policy.py adapter; bounded start712 planner
# copied from frozen E180/S78 and modified for seven callbacks, exact Shop final
# liquidation, strict positive physical delivery/sale gain, and observation guards.
# unit_model.py is an unchanged frozen E180 copy of Kaggle's extracted semantics.
# The following original E180 notice is retained verbatim for attribution history.
# Its references to Thomas files describe E180, not files supplied in this Shop
# package: no Thomas tapes, trees or policy are included here.
# 
# ----- Original E180 notice -----
# Kaggriculture: Last-Mile Harvest Planner
# Attribution and change notice
# 
# Thomas Tschinkel is the author of the parent public state-router policy and its
# published decision trees and action-route data. Source: Kaggriculture: 93.8% Win
# Rate Public State Router, notebook version 3, scriptVersionId 347936183:
# https://www.kaggle.com/code/thomastschinkel/kaggriculture-93-8-win-rate-public-state-router?scriptVersionId=347936183
# The public notebook identifies its license as Apache License, Version 2.0.
# Original published main.py SHA-256:
# b87a27ed614a33329be85f1b662e51cf4078a019fee937afcebbbbf2f51f8522
# 
# Changes to that source for this distribution: compressed route/tree literals
# were decoded into readable tapes.json and trees.json; a read-only planned_action
# helper was added; descriptive headers and local data loading were adapted.
# The original parent feature extraction, tree traversal and agent behavior are
# retained. These public routes are not claimed as newly authored or trained by
# the notebook distributor.
# 
# unit_model.py contains deterministic unit-action and crop-decay definitions
# extracted from Kaggle's kaggle-environments 1.32.7 Kaggriculture engine, licensed
# under Apache License, Version 2.0. Credit: Kaggle and the kaggle-environments
# contributors. Project: https://github.com/Kaggle/kaggle-environments
# Source file: kaggle_environments/envs/kaggriculture/kaggriculture.py
# Source SHA-256:
# bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e
# The extracted unit/decay definitions are not a newly authored game engine;
# market price dynamics and the full interpreter are not part of this module.
# 
# Additional work in this distribution: a bounded last-nine-action collection
# and delivery planner, observation guards and recovery, a settings-consuming
# factory and entry point, standalone examples, and deterministic packaging.
# The full Apache License, Version 2.0 is included as LICENSE.txt.
# No endorsement by Thomas Tschinkel or Kaggle is implied.
# 
# Data provenance limitation: Thomas's source refers to public replay data and
# an upstream provenance.json. That original episode-level manifest, replay IDs
# and individual replay-author identities were not supplied with the public
# notebook/output used here. No names or episode lineage have been invented.
# Notebook-level licensing does not independently establish the missing underlying
# replay-data rights chain. The package supplies usable readable routes, not a
# reproducible reconstruction of their original collection or training process.
# 
# Packaging note: source inputs described as byte-exact above are
# normalized to UTF-8/LF text with a final newline in this standalone
# notebook package. Route JSON values and parent policy behavior are unchanged.

# Final public-entry guard; measured separately and compared on captured observations.
_V28_CORE=agent
del agent
_IMPL.chassis.diagnostics['v28_entry_errors']=0
def agent(observation,configuration=None):
    try:
        return _V28_CORE(observation,configuration)
    except Exception:
        _IMPL.chassis.diagnostics['v28_entry_errors']+=1
        return {'farmer':['PASS'],'hands':[],'market':[]}
agent.telemetry=_ROOM_STATS

# EXP-155: prvsiyan V221B finite tomato investment, adapted by Ahmed Berat Ozer.
# Original public source is retained under research24/public; Apache-2.0.
MAX_ORDERS=10
class FarmView(_View):
    def __init__(self,obs):super().__init__(obs,int(obs['player']),_IMPL.chassis.cfg)
    def inventory(self,actor):return self.inv(actor)
def projected_shed(action,view):return _IMPL.chassis._projected_shed(action,view)

CROP_MIN_PRICE=70

# V219: a finite late tomato investment with dedicated, observed workers.
_V219_PARENT = agent
del agent
_V219_FERTILIZE = True  # Builder changes only this flag for the ablation.
_V219_STATES = {}
_V219_REPORT = {'commitments': 0, 'hire_requests': 0, 'confirmed_workers': 0,
                'hire_shortfalls': 0, 'plant_requests': 0, 'confirmed_plants': 0,
                'water_requests': 0, 'fertilize_requests': 0, 'harvest_requests': 0,
                'confirmed_harvest_units': 0, 'drop_requests': 0,
                'tomato_sale_requests': 0, 'budget_declines': 0, 'lost_plants': 0}


def _v219_fib(n):
    a, b = 1, 1
    for _ in range(n): a, b = b, a+b
    return a


def _v219_native_day(native, day):
    tape = _IMPL.chassis.routes[native['route']]
    return tape[day*24:min((day+1)*24,719)]


def _v219_qualifies(obs, native):
    farm=obs['farms'][obs['player']]
    if len(farm['tiles']) != 10 or set(farm['unlocked_quadrants']) != {'NW','NE','SW'}:
        return False
    if farm['money'] < 12000 or obs['market']['prices']['TOMATO'] < CROP_MIN_PRICE:
        return False
    if sum(s in ('PIZZA_SHOP','FARMERS_MARKET') for s in obs['town']['unlocked_shops']) < 3:
        return False
    if any(farm['tiles'][y][x] != 'LOCKED' for y in (5,6) for x in range(5,10)):
        return False
    if obs['private']['seeds'].get('TOMATO',0) or obs['private']['shed'].get('TOMATO',0):
        return False
    if any(isinstance(t,dict) and t.get('crop')=='TOMATO' for row in farm['tiles'] for t in row):
        return False
    # The investment uses spare land and new worker indices. Avoid taking over
    # any native tomato or land purchase obligation on the known own schedule.
    for tape in _IMPL.chassis.routes.values():
        for a in tape[432:719]:
            if any(o and o[0]=='BUY_LAND' for o in a.get('market',[])):return False
            if any(c==['PLANT','TOMATO'] for c in [a.get('farmer')]+a.get('hands',[])):return False
    return True


def _v219_walk(pos, target):
    x,y=pos;tx,ty=target
    if x != tx:return ['EAST' if x < tx else 'WEST']
    if y != ty:return ['SOUTH' if y < ty else 'NORTH']
    return None


def _v219_home(pos):
    return min(((4,4),(5,4),(4,5),(5,5)),key=lambda p:abs(pos[0]-p[0])+abs(pos[1]-p[1]))


def _v219_request(obs, action, state, native):
    step=int(obs['step']);day=step//24;offset=step%24
    farm=obs['farms'][obs['player']];private=obs['private']
    # If the planting-day transaction could not complete, abandon investment.
    # Later purchases would miss the finite day26..29 production window.
    if not state.get('committed') and day!=18:return action
    if state.get('requested_day')==day or offset>3:return action
    planned=_v219_native_day(native,day)
    remaining=planned[offset+1:]
    if any(o and o[0]=='HIRE' for a in remaining for o in a.get('market',[])):
        return action
    parent_hires=sum(bool(o) and o[0]=='HIRE' for o in action['market'])
    expected=max(len(a.get('hands',[])) for a in planned)
    if len(farm['hands'])+parent_hires != expected:return action
    fertilizer=bool(_V219_FERTILIZE and day in (24,27) and _r79_tomato_fertilizer_worthwhile(obs,action))
    # One watering tour: at most 2 entry moves + 9 between tiles + 10 waters.
    # A hire request by hour2 leaves at least21 callbacks after confirmation.
    crop_workers=1 if day in (19,20,21,22,23,25) and offset<=2 else (3 if 26<=day<=28 else 2)
    labor=_r53_labor_assignment(obs,action,fertilizer)
    if labor is not None:crop_workers=labor['workers']
    count=crop_workers+int(fertilizer and day==27 and labor is None)
    extra=[]
    if not state.get('committed'):
        extra += [['BUY_LAND'],['BUY_SEED','TOMATO',10]]
    fertilizer_quantity=_r70_parent_fert_qty(obs,action,planned,offset) if fertilizer else 0
    if fertilizer:extra.append(['BUY_PRODUCT','FERTILIZER',fertilizer_quantity])
    extra += [['HIRE'] for _ in range(count)]
    if len(action['market'])+len(extra)>MAX_ORDERS:return action
    # No assumed sale proceeds. Reserve 3,000 for parent obligations and price
    # movement; the qualification separately requires 12,000 initial liquidity.
    budget=sum(_v219_fib(n) for n in range(farm['hires_today'],farm['hires_today']+parent_hires+count))
    if not state.get('committed'):budget+=4500
    if fertilizer:budget+=fertilizer_quantity*(obs['market']['prices']['FERTILIZER']+5)
    for order in action['market']:
        if not order:continue
        if order[0]=='BUY_PRODUCT':budget+=int(order[2])*(int(obs['market']['prices'][order[1]])+10)
        elif order[0]=='BUY_ANIMAL':budget+=int(order[2])*{'COW':400,'SHEEP':500,'GOOSE':300}[order[1]]
        elif order[0]=='BUY_SEED':budget+=int(order[2])*{'WHEAT':10,'CARROT':20,'TOMATO':50,'STRAWBERRY':100,'MELON':80}[order[1]]
    if farm['money']<budget+3000:
        _V219_REPORT['budget_declines']+=1;return action
    state['pending']={'step':step,'first_actor':expected+1,'count':count,'crop_workers':crop_workers,'fertilizer':fertilizer,'labor':labor}
    if labor is not None:
        _R53_LABOR_REPORT['labor_requests']+=1;_R53_LABOR_REPORT['labor_hires_avoided']+=1;_R53_LABOR_REPORT['labor_day'+str(day)]+=1
    state['requested_day']=day
    _V219_REPORT['hire_requests']+=count
    if not state.get('committed'):
        state['committed']=True;_V219_REPORT['commitments']+=1
    changed=copy.deepcopy(action);changed['market']+=extra
    return changed


def _v219_worker(obs, state, actor, role):
    day=int(obs['step'])//24;step=int(obs['step']);view=FarmView(obs)
    pos=tuple(view.positions[actor]);inv=view.inventory(actor)
    targets=role['targets']
    # Actual cargo differences, observed on the next callback, verify harvests.
    previous=state['last_work'].get(actor)
    if previous and previous['step']==step-1 and previous['command']==['HARVEST']:
        _V219_REPORT['confirmed_harvest_units']+=max(0,int(inv.get('TOMATO',0))-previous['tomatoes'])
    if role.get('needs_fertilizer') and not role.get('loaded'):
        home=_v219_home(pos)
        walk=_v219_walk(pos,home)
        if walk:return walk
        desired=role.get('fertilizer_quantity',10 if role['kind']=='fertilizer' else 5)
        if inv.get('FERTILIZER',0)>=desired:role['loaded']=True
        elif role.get('pickup_requested'):
            # Never spend repeated turns waiting for stock that was not bought.
            role['loaded']=True;role['fertilizer_available']=int(inv.get('FERTILIZER',0))
        elif view.shed.get('FERTILIZER',0)>=desired:
            role['pickup_requested']=True;return ['PICKUP','FERTILIZER',desired]
        else:role['loaded']=True
    todo=[]
    for target in targets:
        x,y=target;tile=view.tiles[y][x]
        tomato=isinstance(tile,dict) and tile.get('crop')=='TOMATO'
        if tomato and target not in state['seen_plants']:
            state['seen_plants'].add(target);_V219_REPORT['confirmed_plants']+=1
        if target in state['seen_plants'] and not tomato and target not in state['lost']:
            state['lost'].add(target);_V219_REPORT['lost_plants']+=1
        command=None
        if role['kind']=='fertilizer':
            if tomato and tile.get('fertilized_until_day',-1)<day+2 and inv.get('FERTILIZER',0)>0:
                command=['FERTILIZE']
        elif day==18 and not tomato:
            if tile is None and obs['private']['seeds'].get('TOMATO',0)>0:command=['PLANT','TOMATO']
            elif isinstance(tile,dict) and tile.get('kind')=='WEED':command=['DIG']
        elif tomato:
            # No later production follows the final day, so watering then would
            # consume time needed to harvest and deliver the final cargo.
            if day<29 and not tile.get('watered_today'):command=['WATER']
            elif role.get('needs_fertilizer') and tile.get('fertilized_until_day',-1)<day+2 and inv.get('FERTILIZER',0)>0:
                command=['FERTILIZE']
            elif tile.get('yield_units',0)>0:command=['HARVEST']
        if command:todo.append((target,command))
    # Final return has priority once only the exact distance plus DROP remains.
    home=_v219_home(pos);distance=abs(pos[0]-home[0])+abs(pos[1]-home[1])
    if step>=718-distance and inv.get('TOMATO',0):
        return _v219_walk(pos,home) or ['PLACE','TOMATO',int(inv.get('TOMATO',0))]
    if todo:
        target,command=min(todo,key=lambda v:(abs(pos[0]-v[0][0])+abs(pos[1]-v[0][1]),targets.index(v[0])))
        return _v219_walk(pos,target) or command
    if inv.get('TOMATO',0):return _v219_walk(pos,home) or ['PLACE','TOMATO',int(inv['TOMATO'])]
    if any(inv.values()):return _v219_walk(pos,home) or ['DROP']
    return ['PASS']


def agent(observation, configuration=None):
    action=_V219_PARENT(observation,configuration)
    step=int(observation['step']);player=int(observation['player']);day=step//24
    state=_V219_STATES.get(player)
    if state is None or step<=state['last_step']:
        state={'last_step':step,'day':-1,'workers':{},'last_work':{},'seen_plants':set(),'lost':set(),
               'targets':[(x,y) for y in (5,6) for x in range(5,10)]}
        _V219_STATES[player]=state
    state['last_step']=step
    native=_IMPL.chassis.players[player]
    if step==432:state['eligible']=_v219_qualifies(observation,native)
    if not state.get('eligible') or day<18:return action
    if state['day']!=day:
        state['day']=day;state['workers']={};state['last_work']={}
    farm=observation['farms'][player]
    pending=state.pop('pending',None)
    if pending:
        if len(farm['hands'])+1 >= pending['first_actor']+pending['count'] and 'SE' in farm['unlocked_quadrants']:
            for index in range(pending['count']):
                fertilizer_worker=index==pending['crop_workers']
                if fertilizer_worker:targets=state['targets']
                elif pending['crop_workers']==1:targets=state['targets']
                elif pending['crop_workers']==2:targets=state['targets'][index*5:index*5+5]
                else:targets=[[(5,5),(6,5),(7,5)],[(8,5),(9,5),(9,6),(8,6)],[(5,6),(6,6),(7,6)]][index]
                state['workers'][pending['first_actor']+index]={'kind':'fertilizer' if fertilizer_worker else 'crop','targets':targets,
                    'needs_fertilizer':pending['fertilizer'] and (day==24 or fertilizer_worker)}
                if pending.get('labor') is not None:
                    role=state['workers'][pending['first_actor']+index]
                    role['targets']=[tuple(p) for p in pending['labor']['paths'][index]]
                    role['needs_fertilizer']=pending['labor']['fertilizer'];role['fertilizer_quantity']=len(role['targets'])
                    if tuple(farm['hands'][pending['first_actor']+index-1])!=tuple(pending['labor']['spawns'][index]):_R53_LABOR_REPORT['labor_spawn_errors']+=1
                    if index==0:_R53_LABOR_REPORT['labor_confirmed']+=1
            _V219_REPORT['confirmed_workers']+=pending['count']
        else:_V219_REPORT['hire_shortfalls']+=pending['count']
    action=_v219_request(observation,action,state,native)
    if state['workers']:
        commands=[action.get('farmer') or ['PASS']]+list(action.get('hands') or [])
        commands += [['PASS'] for _ in range(len(farm['hands'])+1-len(commands))]
        for actor,role in state['workers'].items():
            if actor>=len(commands):continue
            command=_v219_worker(observation,state,actor,role)
            commands[actor]=command
            name={'PLANT':'plant_requests','WATER':'water_requests','FERTILIZE':'fertilize_requests',
                  'HARVEST':'harvest_requests','DROP':'drop_requests'}.get(command[0])
            if name:_V219_REPORT[name]+=1
            state['last_work'][actor]={'step':step,'command':command,'tomatoes':observation['private']['inventories'][actor].get('TOMATO',0)}
        action=copy.deepcopy(action);action['farmer'],action['hands']=commands[0],commands[1:]
    if state.get('committed') and len(action['market'])<MAX_ORDERS and not any(o[:2]==['SELL','TOMATO'] for o in action['market']):
        quantity=projected_shed(action,FarmView(observation)).get('TOMATO',0)
        if quantity>0:
            action=copy.deepcopy(action);action['market'].append(['SELL','TOMATO',quantity])
            _V219_REPORT['tomato_sale_requests']+=quantity
    return action


agent.telemetry=_V219_REPORT

# V221B: labor-only ablation of frozen V219G; not yet publicly scored.


# Crop workers own their final routes after commitment. A private parent shadow
# does not contain these obligations, so terminal rescue must abstain there.
_ORIGINAL_SHADOW_TERMINAL=_shadow_terminal
def _shadow_terminal(obs,config):
    if _V219_STATES.get(int(obs['player']),{}).get('committed'):return None
    return _ORIGINAL_SHADOW_TERMINAL(obs,config)

APPLY_TIMING=False

_EXPERIMENT_PARENT=agent
del agent
_V219_REPORT['extra_fertilizer_days']=0
_V219_REPORT['reordered_market_turns']=0
_V219_REPORT['errors']=0
def agent(observation,configuration=None):
    try:
        action=_EXPERIMENT_PARENT(observation,configuration)
        if APPLY_TIMING and int(observation['step'])>=144:action=_v224_sales_first(action)
        return action
    except Exception:
        _V219_REPORT['errors']+=1
        return {'farmer':['PASS'],'hands':[],'market':[]}
agent.telemetry=_V219_REPORT

def _v224_sales_first(action):
    original=action.get('market',[])[:MAX_ORDERS]
    orders=[list(o) for o in original if o and (o[0] in ('HIRE','BUY_LAND') or (len(o)>=3 and int(o[2])>0))]
    for index in range(len(orders)):
        order=orders[index]
        if order[0]!='SELL':continue
        cursor=index
        while cursor>0:
            previous=orders[cursor-1]
            if previous[0]=='SELL':break
            if previous[0] in ('BUY_PRODUCT','BUY_ANIMAL') and previous[1]==order[1]:break
            orders[cursor-1],orders[cursor]=orders[cursor],orders[cursor-1]
            cursor-=1
    if orders==original:return action
    _V219_REPORT['reordered_market_turns']+=1
    changed=copy.deepcopy(action);changed['market']=orders
    return changed
_ORDER_PARENT=agent
del agent

def agent(observation,configuration=None):
    try:
        action=_ORDER_PARENT(observation,configuration)
        if int(observation["step"])>=144:action=_v224_sales_first(action)
        return action
    except Exception:
        _V219_REPORT["errors"]+=1
        return {"farmer":["PASS"],"hands":[],"market":[]}
agent.telemetry=_V219_REPORT

_V31_CORE=agent
del agent
_IMPL.chassis.diagnostics['production_errors']=0
_IMPL.chassis.diagnostics['v31_entry_errors']=0
def agent(observation,configuration=None):
    before=_V219_REPORT['errors']
    try:
        action=_V31_CORE(observation,configuration)
        _IMPL.chassis.diagnostics['production_errors']+=_V219_REPORT['errors']-before
        return action
    except Exception:
        _IMPL.chassis.diagnostics['v31_entry_errors']+=1
        return {'farmer':['PASS'],'hands':[],'market':[]}
agent.telemetry=_V219_REPORT

# Apache-2.0; later cattle transfer from prvsiyan, Moon (2026-09-10).
# Bounded livestock substitution; confirm owned animals before redirecting workers.
_V231_PARENT=agent
_V231_CAP=4
_V231_STATES={}
_V231_REPORT={}

def _v231_new_state():
    return {'last':-1,'confirmed':0,'reserved':0,'pending_buy':None,
            'carrying':{},'pending_places':[],'sites':{},'milk_credit':0,
            'requested':0,'failed_purchase_units':0,'picked':0,'placed':0,
            'failed_placements':0,'extra_milk_harvested':0,'extra_milk_sale_requests':0}

def _v231_controller(obs,action,state,cap):
    step=int(obs['step']);seat=int(obs['player']);farm=obs['farms'][seat]
    private=obs['private'];shed=private['shed'];inventories=private['inventories']
    positions=[farm['farmer'],*farm['hands']]
    pending=state['pending_buy']
    if pending is not None:
        gained=max(0,int(shed.get('COW',0))-pending['before'])
        confirmed=min(pending['quantity'],gained)
        state['confirmed']+=confirmed;state['reserved']+=confirmed
        state['failed_purchase_units']+=pending['quantity']-confirmed
        state['pending_buy']=None
    for pending in state['pending_places']:
        x,y=pending['site'];tile=farm['tiles'][y][x]
        if (isinstance(tile,dict) and tile.get('animal')=='COW'
                and tile.get('placed_day')==pending['day']):
            state['sites'][(x,y)]=pending['day'];state['placed']+=1
            actor=pending['actor'];state['carrying'][actor]=max(0,state['carrying'].get(actor,0)-1)
        else:state['failed_placements']+=1
    state['pending_places']=[]
    state['last']=step
    result=copy.deepcopy(action)
    workers=[result.get('farmer') or ['PASS'],*(result.get('hands') or [])]
    seen_harvest=set();cow_available=int(shed.get('COW',0));occupied=set()
    for actor,work in enumerate(workers[:len(positions)]):
        inventory=inventories[actor] if actor<len(inventories) else {}
        x,y=positions[actor];tile=farm['tiles'][y][x];site=(x,y)
        if (work==['HARVEST'] and site in state['sites'] and site not in seen_harvest
                and isinstance(tile,dict) and tile.get('animal')=='COW'
                and tile.get('placed_day')==state['sites'][site]):
            units=max(0,int(tile.get('yield_units',0)))
            state['milk_credit']+=units;state['extra_milk_harvested']+=units
            seen_harvest.add(site)
        if len(work)>=2 and work[:2]==['PICKUP','SHEEP']:
            quantity=max(0,int(work[2]) if len(work)>2 else 1)
            center=len(farm['tiles'])//2
            if (quantity and state['reserved']>=quantity and cow_available>=quantity
                    and x in (center-1,center) and y in (center-1,center)
                    and not any(inventory.get(a,0) for a in ('COW','SHEEP','GOOSE'))):
                work[1]='COW';state['reserved']-=quantity;cow_available-=quantity
                state['carrying'][actor]=state['carrying'].get(actor,0)+quantity
                state['picked']+=quantity
        if (len(work)>=2 and work[:2]==['PLACE','SHEEP']
                and state['carrying'].get(actor,0)>0 and inventory.get('COW',0)>0
                and isinstance(tile,dict) and tile.get('kind')=='PASTURE'
                and 'animal' not in tile and site not in occupied):
            work[1]='COW'
            state['pending_places'].append({'actor':actor,'site':site,'day':step//24})
        if (len(work)>=2 and work[0]=='PLACE' and work[1] in ('COW','SHEEP','GOOSE')
                and inventory.get(work[1],0)>0):occupied.add(site)
    result['farmer'],result['hands']=workers[0],workers[1:]
    market=result.get('market',[])
    animal_orders=[o for o in market if len(o)>=3 and o[0]=='BUY_ANIMAL']
    shops=obs['town']['unlocked_shops'];prices=obs['market']['prices']
    counts={'COW':0,'SHEEP':0}
    for line in farm['tiles']:
        for tile in line:
            if isinstance(tile,dict) and tile.get('animal') in counts:counts[tile['animal']]+=1
    cargo=sum(int(inv.get(a,0)) for inv in inventories for a in ('COW','SHEEP','GOOSE'))
    stock_animals=sum(int(shed.get(a,0)) for a in ('COW','SHEEP','GOOSE'))
    milk_shops=sum(shop in ('PIZZA_SHOP','ICE_CREAM_SHOP','SMOOTHIE_SHOP') for shop in shops)
    if (216<=step<=227 and len(shops)>=3 and state['confirmed']<cap and not state['reserved']
            and not any(state['carrying'].values()) and not state['pending_places']
            and not cargo and not stock_animals and len(animal_orders)==1
            and animal_orders[0][1]=='SHEEP' and milk_shops>=2 and 'YARN_STORE' not in shops
            and int(prices.get('MILK',0))>=int(prices.get('WOOL',0))
            and counts['COW']>=4 and counts['SHEEP']>=2):
        order=animal_orders[0];quantity=int(order[2])
        if 1<=quantity<=2 and quantity<=cap-state['confirmed']:
            order[1]='COW';state['requested']+=quantity
            state['pending_buy']={'before':int(shed.get('COW',0)),'quantity':quantity}
    # Sell only additional physically harvested production at an existing sale slot.
    if state['milk_credit']>0:
        stock=projected_shed(result,FarmView(obs))
        total_planned=sum(max(0,int(o[2])) for o in market if len(o)>=3 and o[:2]==['SELL','MILK'])
        extra=min(state['milk_credit'],max(0,int(stock.get('MILK',0))-total_planned))
        if extra:
            for order in market:
                if len(order)>=3 and order[:2]==['SELL','MILK'] and int(order[2])>0:
                    order[2]=int(order[2])+extra
                    state['milk_credit']-=extra;state['extra_milk_sale_requests']+=extra
                    break
    result['market']=market
    return result

def agent(observation,configuration=None):
    step=int(observation['step']);seat=int(observation['player'])
    state=_V231_STATES.get(seat)
    if state is None or step<=state['last']:
        state=_V231_STATES[seat]=_v231_new_state()
    action=_V231_PARENT(observation,configuration)
    action=_v231_controller(observation,action,state,_V231_CAP)
    _V231_REPORT.clear();_V231_REPORT.update(_V231_PARENT.telemetry)
    for name in ('confirmed','reserved','requested','failed_purchase_units','picked','placed',
                 'failed_placements','extra_milk_harvested','extra_milk_sale_requests','milk_credit'):
        _V231_REPORT['cattle_'+name]=state[name]
    _V231_REPORT['cattle_carried_pending']=sum(state['carrying'].values())
    return action

agent.telemetry=_V231_REPORT


# EXP-167, adapted from Dmitrii Gluzdov's Two Coins, One Sheep (Apache-2.0).
# Reserve only physically available stock after the final parent worker actions.
_R36_SALE_PARENT=agent
_R36_NATIVE_LEAD=Chassis._sell_lead
_R36_NATIVE_SUPPRESS=Chassis._apply_suppression
_R36_SALE_REPORT={}

def _r36_native_lead(self,action,view,projected,route,step,next_sup):
    if step<288 or step>=696:
        return _R36_NATIVE_LEAD(self,action,view,projected,route,step,next_sup)

def _r36_suppress(action,state,step):
    _R36_NATIVE_SUPPRESS(action,state,step)
    due=state.get('r36_debts',{}).pop(step,{})
    for order in action.get('market',[]):
        if len(order)>=3 and order[0]=='SELL':
            removed=min(max(0,int(order[2])),due.get(order[1],0))
            order[2]-=removed
            due[order[1]]=due.get(order[1],0)-removed

Chassis._sell_lead=_r36_native_lead
Chassis._apply_suppression=staticmethod(_r36_suppress)

def _r36_reserve(obs,action):
    step=int(obs['step'])
    # The final planner forecasts its own parent, so keep its full window native.
    if not 288<=step<696:return action
    native=_IMPL.chassis.players[int(obs['player'])]
    tape=_IMPL.chassis.routes[native['route']]
    end=min(695,step+_R37_HORIZONS.get(int(obs['player']),2),(step//72+1)*72-1)
    if end<=step:return action
    commands=[action.get('farmer') or ['PASS'],*(action.get('hands') or [])]
    view=FarmView(obs)
    # This projection intentionally abstains on ambiguous animal depot returns.
    if any(len(c)>1 and c[0]=='PLACE' and c[1] in ANIMAL_STRUCTURE
           and view.inv(i).get(c[1],0)>0 for i,c in enumerate(commands[:len(view.positions)])):
        return action
    stock=projected_shed(action,view)
    market=action.get('market',[])
    blocked={o[1] for o in market if len(o)>1 and o[0] in ('SELL','BUY_PRODUCT')}
    blocked.update(c[1] for c in commands if len(c)>1 and c[0]=='PICKUP')
    blocked.update(c[1] for queue in native['pending'].values() for pos,c in queue
                   if len(c)>1 and c[0]=='PICKUP')
    debts=native['sell_state'].setdefault('r36_debts',{})
    for item in PRODUCTS:
        if item in ('WHEAT','FERTILIZER') or item in blocked or view.prices.get(item,0)<2:continue
        available=max(0,int(stock.get(item,0)))
        if not available or len(market)>=10:continue
        reservations=[]
        for due_step in range(step+1,end+1):
            future=tape[due_step]
            work=[future.get('farmer') or ['PASS'],*(future.get('hands') or [])]
            if any(len(c)>1 and c[:2]==['PICKUP',item] for c in work):break
            if any(len(o)>1 and o[:2]==['BUY_PRODUCT',item] for o in future.get('market',[])):break
            planned=sum(max(0,int(o[2])) for o in future.get('market',[]) if len(o)>=3 and o[:2]==['SELL',item])
            amount=min(available,max(0,planned-debts.get(due_step,{}).get(item,0)))
            if amount:
                reservations.append((due_step,amount));available-=amount
            if not available:break
        qty=sum(q for _,q in reservations)
        if qty:
            market.append(['SELL',item,qty])
            for due,q in reservations:
                debt=debts.setdefault(due,{})
                debt[item]=debt.get(item,0)+q
            _R36_SALE_REPORT['sale_reserved_units']+=qty
            _R36_SALE_REPORT['sale_reservations']+=1
    return action

def agent(observation,configuration=None):
    if int(observation.get('step',0))==0:
        _R36_SALE_REPORT.update(sale_reserved_units=0,sale_reservations=0,sale_errors=0)
    action=_R36_SALE_PARENT(observation,configuration)
    try:
        if configuration is None or all(configuration.get(k,v)==v for k,v in
            [('boardSize',10),('turnsPerDay',24),('shedCapacity',100),('maxMarketOrdersPerTurn',10)]):
            action=_r36_reserve(observation,action)
            if int(observation['step'])>=288:action=_v224_sales_first(action)
    except Exception:
        _R36_SALE_REPORT['sale_errors']=_R36_SALE_REPORT.get('sale_errors',0)+1
    _R36_SALE_REPORT.update(_R36_SALE_PARENT.telemetry)
    return action

agent.telemetry=_R36_SALE_REPORT

# Ensure the Kaggle-selected final callable is the exported policy.
agent = globals().pop("agent")


# Public capability transfer: lucifer19; Flexon is the same Two Coins asset set.
# Apache-2.0; exact functions from Kaggle kaggle-environments 1.32.7.
# https://github.com/Kaggle/kaggle-environments/tree/master/kaggle_environments/envs/kaggriculture
import math
_R37_MARKET_PARAMS = {'WHEAT': {'base': 25, 'I0': 10000, 'T': 400, 'below_func': 'sqrt', 'below_target': 0.8, 'above_func': 'log', 'above_target': 0.2}, 'CARROT': {'base': 35, 'I0': 10000, 'T': 450, 'below_func': 'hinge', 'below_target': 1.0, 'above_func': 'sqrt', 'above_target': 0.7}, 'TOMATO': {'base': 60, 'I0': 10000, 'T': 200, 'below_func': 'hinge', 'below_target': 0.4, 'above_func': 'sqrt', 'above_target': 0.6}, 'STRAWBERRY': {'base': 120, 'I0': 10000, 'T': 100, 'below_func': 'sqrt', 'below_target': 0.7, 'above_func': 'linear', 'above_target': 1.6}, 'MELON': {'base': 250, 'I0': 10000, 'T': 300, 'below_func': 'log', 'below_target': 0.2, 'above_func': 'sq', 'above_target': 3.6}, 'EGG': {'base': 50, 'I0': 10000, 'T': 332, 'below_func': 'hinge', 'below_target': 0.4, 'above_func': 'log', 'above_target': 0.2}, 'MILK': {'base': 160, 'I0': 10000, 'T': 122, 'below_func': 'sqrt', 'below_target': 0.6, 'above_func': 'linear', 'above_target': 1.6}, 'WOOL': {'base': 200, 'I0': 10000, 'T': 105, 'below_func': 'log', 'below_target': 0.2, 'above_func': 'sq', 'above_target': 3.2}, 'FERTILIZER': {'base': 100, 'I0': 10000, 'T': 200, 'below_func': 'linear', 'below_target': 0.4, 'above_func': 'linear', 'above_target': 0.4}}
_R37_PRICE_FLOOR = 1
_R37_HINGE_GAIN = 8.0
def _r37_shape(func, x, T=None):
    x = max(0.0, x)
    if func == "linear": return x
    if func == "sq":     return x * x
    if func == "sqrt":   return math.sqrt(x)
    if func == "log":    return math.log(1.0 + x)
    if func == "log10":  return math.log10(1.0 + x)
    if func == "hinge":
        # Degenerates to linear if T is missing or non-positive.
        if not T or T <= 0:
            return x
        u = x / T
        return u + _R37_HINGE_GAIN * max(0.0, u - 1.0) ** 2
    return x

def _r37_market_price(item, inventory, params=None):
    """Floor at _R37_PRICE_FLOOR."""
    p = (params or _R37_MARKET_PARAMS)[item]
    base = p["base"]
    I0 = p["I0"]
    T = p["T"]
    if inventory < I0:
        f = p["below_func"]
        amp = p["below_target"] * base / _r37_shape(f, T, T)
        price = base + amp * _r37_shape(f, I0 - inventory, T)
    else:
        f = p["above_func"]
        amp = p["above_target"] * base / _r37_shape(f, T, T)
        price = base - amp * _r37_shape(f, inventory - I0, T)
    return max(_R37_PRICE_FLOOR, int(round(price)))

def _r37_similarity(observation):
    """Empty tiles cannot make two unrelated production layouts look alike."""
    farms = observation['farms']
    own, rival = farms[observation['player']], farms[1-observation['player']]
    if own['unlocked_quadrants'] != rival['unlocked_quadrants']:
        return 0.0
    matches = total = 0
    for a, b in zip([t for row in own['tiles'] for t in row],
                    [t for row in rival['tiles'] for t in row]):
        sa = (a.get('crop'), a.get('animal')) if isinstance(a, dict) else (None, None)
        sb = (b.get('crop'), b.get('animal')) if isinstance(b, dict) else (None, None)
        if sa != (None, None) or sb != (None, None):
            total += 1
            matches += sa == sb
    return matches / total if total >= 8 else 0.0


def _r37_quote_priority(observation, order, stock):
    """Revenue exposed to a small rival batch, not nominal headline revenue."""
    item = order[1]
    quantity = min(max(0, int(order[2])), stock.get(item, 0))
    if not quantity or item not in _R37_MARKET_PARAMS:
        return 0.0
    inventory = observation['market']['inventory'][item]
    params = {k: dict(v) for k, v in _R37_MARKET_PARAMS.items()}
    for k, patch in observation['market'].get('params', {}).items():
        if k in params:
            params[k].update(patch)
    rival = observation['farms'][1-observation['player']]
    crop_item = item if item in ('WHEAT','CARROT','TOMATO','STRAWBERRY','MELON') else None
    animal = {'EGG':'GOOSE','MILK':'COW','WOOL':'SHEEP'}.get(item)
    standing = sum(max(0, int(t.get('yield_units', 0))) for row in rival['tiles'] for t in row
                   if isinstance(t, dict) and
                   ((crop_item is not None and t.get('crop') == crop_item) or
                    (animal is not None and t.get('animal') == animal)))
    # Public fields do not reveal the rival shed. Eight units are a scenario,
    # not a recovered hidden quantity; visible ripe yield increases the stress.
    batch = min(24, max(8, standing))
    now = sum(_r37_market_price(item, inventory+j, params) for j in range(quantity))
    later = sum(_r37_market_price(item, inventory+batch+j, params) for j in range(quantity))
    return now-later


def _r37_reorder_sales(observation, action):
    """Keep quantities and purchase barriers; rank distinct contiguous sales."""
    stock = projected_shed(action, FarmView(observation))
    orders = [list(o) for o in action['market']]
    start = 0
    while start < len(orders):
        if orders[start][0] != 'SELL':
            start += 1
            continue
        end = start
        while end < len(orders) and orders[end][0] == 'SELL':
            end += 1
        block = orders[start:end]
        if len({o[1] for o in block}) == len(block):
            orders[start:end] = sorted(block, key=lambda o: _r37_quote_priority(observation, o, stock), reverse=True)
        start = end
    if orders != action['market']:
        _R37_STATS['quote_reordered_turns'] += 1
        action = dict(action, market=orders)
    return action



# EXP175: bounded public cash-response probe inspired by leoprovorov,
# Two Coins Mirror Counter v1 (Apache-2.0). No hidden rival inventory.
_R44_PROBES={}
_R44_REPORT=dict(probe_matches=0,probe_four_turn_calls=0,probe_errors=0)

def _r44_before(obs):
    player=int(obs['player']);step=int(obs['step'])
    st=_R44_PROBES.get(player)
    if st is None or step<=st['step']:
        st=_R44_PROBES[player]={'step':-1,'money':None,'probe':0,'matched':False}
    if step==0:_R44_REPORT.update(probe_matches=0,probe_four_turn_calls=0,probe_errors=0)
    money=tuple(float(obs['farms'][i]['money']) for i in (player,1-player))
    if st['money'] is not None and st['probe']>=100 and _r37_similarity(obs)>=.90:
        own=money[0]-st['money'][0];rival=money[1]-st['money'][1]
        if own>0 and rival>0 and abs(own-rival)<=max(5.0,.05*st['probe']):
            if not st['matched']:_R44_REPORT['probe_matches']+=1
            st['matched']=True
    st.update(step=step,money=money,probe=0)
    return st

def _r44_after(obs,action,st):
    step=int(obs['step']);player=int(obs['player'])
    if not 336<=step<648 or st['matched']:return
    # Positive all-sale probes avoid mistaking equal spending for preemption.
    if not action['market'] or any(o and o[0]!='SELL' for o in action['market']):return
    debts=_IMPL.chassis.players[player]['sell_state'].get('r36_debts',{})
    own=debts.get(step+3,{})
    if own:st['probe']=sum(max(0,int(n))*int(obs['market']['prices'].get(item,0)) for item,n in own.items())

_R37_ADAPTIVE = True
_R37_QUOTE = True
# EXP-168: adapted from lucifer19 / Harvest Nocturne, Apache-2.0.
# All rivalry features use public occupied tiles; no private rival inventory.
_R37_PARENT = agent
_R37_PLAYERS = {}
_R37_HORIZONS = {}
_R37_REPORT = {}
_R37_STATS = dict(quote_reordered_turns=0, three_turn_calls=0, nocturne_errors=0)
del agent

def agent(observation, configuration=None):
    player, step = int(observation['player']), int(observation['step'])
    state = _R37_PLAYERS.get(player)
    if state is None or step <= state['step']:
        state = _R37_PLAYERS[player] = {'step': -1, 'streak': 0}
    if step == 0:
        _R37_STATS.update(quote_reordered_turns=0, three_turn_calls=0, nocturne_errors=0)
    state['step'] = step
    _R37_HORIZONS[player] = 2
    probe_state=_r44_before(observation)
    try:
        if _R37_ADAPTIVE and step < 648:
            state['streak'] = state['streak'] + 1 if _r37_similarity(observation) >= .90 else 0
            if 336 <= step < 648 and state['streak'] >= 6:
                _R37_HORIZONS[player] = 3
                _R37_STATS['three_turn_calls'] += 1
    except Exception:
        _R37_STATS['nocturne_errors'] += 1
    if _R37_HORIZONS[player]==3 and probe_state['matched']:
        _R37_HORIZONS[player]=4
        _R44_REPORT['probe_four_turn_calls']+=1
    # EXP179: four-turn reservation; retain stock, debt and purchase barriers.
    if 288 <= step < 696:_R37_HORIZONS[player] = 4
    action = _R37_PARENT(observation, configuration)
    _r44_after(observation,action,probe_state)
    if _R37_QUOTE and step >= 288:
        try:
            action = _r37_reorder_sales(observation, action)
        except Exception:
            _R37_STATS['nocturne_errors'] += 1
    _R37_REPORT.update(getattr(_R37_PARENT, 'telemetry', {}))
    _R37_REPORT.update(_R37_STATS)
    _R37_REPORT.update(_R44_REPORT)
    return action

agent.telemetry = _R37_REPORT

# Export guard: normal decisions stay identical to the frozen screened policy.
_RELEASE_PARENT=agent
_RELEASE_REPORT={}
_RELEASE_ERRORS=0
del agent

def agent(observation,configuration=None):
    global _RELEASE_ERRORS
    try:
        result=_RELEASE_PARENT(observation,configuration)
    except Exception:
        _RELEASE_ERRORS+=1
        count=0
        try:
            count=min(64,len(observation['farms'][int(observation['player'])]['hands']))
        except Exception:
            pass
        result={'farmer':['PASS'],'hands':[['PASS'] for _ in range(count)],'market':[]}
    _RELEASE_REPORT.update(getattr(_RELEASE_PARENT,'telemetry',{}))
    _RELEASE_REPORT['release_errors']=_RELEASE_ERRORS
    return result

agent.telemetry=_RELEASE_REPORT
agent=globals().pop('agent')

# Adapted from prvsiyan / The Soil Remembers Rain, Apache-2.0.
# V233: bounded, financed six-sheep SE discovery investment.
_V233_PARENT=agent
del agent
_V233_STATES={}
_V233_REPORT=dict(sheep_commit_requests=0,sheep_committed=0,sheep_hire_requests=0,
    sheep_workers_confirmed=0,sheep_hire_shortfalls=0,sheep_budget_declines=0,
    sheep_capacity_declines=0,sheep_purchase_shortfalls=0,sheep_feed_buy_requests=0,
    sheep_wool_harvested=0,sheep_fert_collected=0,sheep_extra_wool_sales=0,
    sheep_extra_fert_sales=0,sheep_rescue_feed_requests=0)

def _v233_eligible(obs,native):
    farm=obs['farms'][obs['player']];prices=obs['market']['prices']
    if len(farm['tiles'])!=10 or set(farm['unlocked_quadrants'])!={'NW','NE','SW'}:return False
    if obs['town']['unlocked_shops'].count('YARN_STORE')<2 or prices['WOOL']<220 or prices['WHEAT']>45:return False
    if any(farm['tiles'][y][x]!='LOCKED' for y in (5,6) for x in range(5,8)):return False
    if obs['private']['shed'].get('SHEEP',0) or any(i.get('SHEEP',0) for i in obs['private']['inventories']):return False
    for day in range(12,30):
        for a in _v219_native_day(native,day):
            if any(o and (o[0]=='BUY_LAND' or o[:2]==['BUY_ANIMAL','SHEEP']) for o in a.get('market',[])):return False
            if any(c and c[0] in ('PICKUP','PLACE') and len(c)>1 and c[1]=='SHEEP' for c in [a.get('farmer')]+a.get('hands',[])):return False
    return True

def _v233_request(obs,action,state,native):
    step=int(obs['step']);day=step//24;hour=step%24
    if hour>(2 if state.get('committed') else 1) or state.get('requested_day')==day:return action
    if not state.get('committed') and (day!=12 or not _v233_eligible(obs,native)):return action
    planned=_v219_native_day(native,day)
    if any(o and o[0]=='HIRE' for a in planned[hour+1:] for o in a.get('market',[])):return action
    farm=obs['farms'][obs['player']];market=action.get('market',[])
    parent_hires=sum(bool(o) and o[0]=='HIRE' for o in market)
    expected=max(len(a.get('hands',[])) for a in planned)
    if len(farm['hands'])+parent_hires!=expected:return action
    initial=not state.get('committed')
    extra=([['BUY_LAND'],['BUY_ANIMAL','SHEEP',6]] if initial else [])+[['BUY_PRODUCT','WHEAT',6],['HIRE'],['HIRE']]
    if len(market)+len(extra)>MAX_ORDERS:return action
    stock=projected_shed(action,FarmView(obs))
    incoming=6+6*initial
    budget=7000*initial+6*(int(obs['market']['prices']['WHEAT'])+10)
    budget+=sum(_v219_fib(n) for n in range(farm['hires_today'],farm['hires_today']+parent_hires+2))
    for o in market:
        if not o:continue
        if o[0]=='BUY_LAND':return action
        if o[0]=='BUY_PRODUCT':
            incoming+=int(o[2]);budget+=int(o[2])*(int(obs['market']['prices'][o[1]])+10)
        elif o[0]=='BUY_ANIMAL':
            incoming+=int(o[2]);budget+=int(o[2])*{'SHEEP':500,'COW':400,'GOOSE':300}[o[1]]
        elif o[0]=='BUY_SEED':budget+=int(o[2])*{'WHEAT':10,'CARROT':20,'TOMATO':50,'STRAWBERRY':100,'MELON':80}[o[1]]
    if sum(stock.values())+incoming>100:
        _V233_REPORT['sheep_capacity_declines']+=1;return action
    if farm['money']<budget+(3000 if initial else 1000):
        _V233_REPORT['sheep_budget_declines']+=1;return action
    state['requested_day']=day
    state['pending']={'first':expected+1,'initial':initial}
    _V233_REPORT['sheep_hire_requests']+=2;_V233_REPORT['sheep_feed_buy_requests']+=6
    if initial:_V233_REPORT['sheep_commit_requests']+=1
    result=copy.deepcopy(action);result['market']=market+extra
    return result

def _v233_worker(obs,actor,targets):
    farm=obs['farms'][obs['player']];private=obs['private'];step=int(obs['step'])
    pos=tuple(farm['hands'][actor-1]);inv=private['inventories'][actor]
    access=((4,4),(5,4),(4,5),(5,5))
    home=min(access,key=lambda p:(abs(pos[0]-p[0])+abs(pos[1]-p[1]),p))
    distance=abs(pos[0]-home[0])+abs(pos[1]-home[1])
    cargo=[item for item in ('WOOL','FERTILIZER') if inv.get(item,0)]
    if cargo and step%24 >= (22 if step//24==29 else 23)-distance:
        return _v219_walk(pos,home) or ['PLACE',cargo[0],inv[cargo[0]]]
    missing=sum(not(isinstance(farm['tiles'][y][x],dict) and farm['tiles'][y][x].get('animal')=='SHEEP') for x,y in targets)
    if missing and not inv.get('SHEEP',0) and private['shed'].get('SHEEP',0):
        return _v219_walk(pos,home) or ['PICKUP','SHEEP',min(missing,private['shed']['SHEEP'])]
    hungry=sum(not(isinstance(farm['tiles'][y][x],dict) and farm['tiles'][y][x].get('fed_today')) for x,y in targets)
    if hungry and not inv.get('WHEAT',0) and private['shed'].get('WHEAT',0):
        return _v219_walk(pos,home) or ['PICKUP','WHEAT',min(hungry,private['shed']['WHEAT'])]
    tasks=[]
    for target in targets:
        x,y=target;tile=farm['tiles'][y][x];command=None
        if tile is None:command=['BUILD_PASTURE']
        elif isinstance(tile,dict) and tile.get('kind')=='WEED':command=['DIG']
        elif isinstance(tile,dict) and tile.get('kind')=='PASTURE' and not tile.get('animal'):
            if inv.get('SHEEP',0):command=['PLACE','SHEEP']
        elif isinstance(tile,dict) and tile.get('animal')=='SHEEP':
            if not tile['fed_today'] and inv.get('WHEAT',0):command=['FEED']
            elif not tile['cared_today']:command=['CARE']
            elif tile['yield_units']:command=['HARVEST']
            elif tile['fertilizer_available']:command=['COLLECT_FERTILIZER']
        if command:tasks.append((abs(pos[0]-x)+abs(pos[1]-y),targets.index(target),target,command))
    if tasks:
        _,_,target,command=min(tasks);return _v219_walk(pos,target) or command
    if cargo:return _v219_walk(pos,home) or ['PLACE',cargo[0],inv[cargo[0]]]
    return ['PASS']

def _v234_rescue(obs,action,state):
    if not state['workers'] or int(obs['step'])%24>14:return action
    orders=action.get('market',[])
    if len(orders)>=MAX_ORDERS:return action
    if any(o and (o[0] in ('HIRE','BUY_LAND','BUY_ANIMAL','BUY_PRODUCT','BUY_SEED') or (len(o)>1 and o[1]=='WHEAT')) for o in orders):return action
    farm=obs['farms'][obs['player']];private=obs['private'];hungry=carried=0
    commands=[action.get('farmer') or ['PASS']]+list(action.get('hands') or [])
    for actor,targets in state['workers'].items():
        command=commands[actor]
        if command==['FEED'] or command[:2]==['PICKUP','WHEAT']:return action
        carried+=private['inventories'][actor].get('WHEAT',0)
        hungry+=sum(isinstance(farm['tiles'][y][x],dict) and farm['tiles'][y][x].get('animal')=='SHEEP' and not farm['tiles'][y][x].get('fed_today') for x,y in targets)
    stock=projected_shed(action,FarmView(obs))
    shortage=hungry-carried-stock.get('WHEAT',0)
    if not 0<shortage<=6 or state.get('rescue_today',0)+shortage>6:return action
    quote=int(obs['market']['prices']['WHEAT'])
    if quote<1 or farm['money']<1000+shortage*(quote+10) or sum(stock.values())+shortage>100:return action
    result=copy.deepcopy(action);result['market'].append(['BUY_PRODUCT','WHEAT',shortage])
    state['rescue_today']=state.get('rescue_today',0)+shortage
    _V233_REPORT['sheep_rescue_feed_requests']+=shortage
    return result

def agent(observation,configuration=None):
    action=_V233_PARENT(observation,configuration)
    step=int(observation['step']);player=int(observation['player']);day=step//24
    state=_V233_STATES.get(player)
    if state is None or step<=state['last_step']:
        state={'last_step':step,'day':-1,'workers':{},'work':{},'credit':{'WOOL':0,'FERTILIZER':0}}
        _V233_STATES[player]=state
    state['last_step']=step
    if configuration is not None and any(configuration.get(k,v)!=v for k,v in
        (('boardSize',10),('turnsPerDay',24),('shedCapacity',100),('maxMarketOrdersPerTurn',10))):return action
    if day<12:return action
    farm=observation['farms'][player];private=observation['private']
    if state['day']!=day:state['day']=day;state['workers']={};state['work']={};state['rescue_today']=0
    for actor,previous in state['work'].items():
        if previous['step']!=step-1 or actor>=len(private['inventories']):continue
        item={'HARVEST':'WOOL','COLLECT_FERTILIZER':'FERTILIZER'}.get(previous['command'][0])
        if item:
            gained=max(0,private['inventories'][actor].get(item,0)-previous['inventory'].get(item,0))
            state['credit'][item]+=gained
            _V233_REPORT['sheep_wool_harvested' if item=='WOOL' else 'sheep_fert_collected']+=gained
    pending=state.pop('pending',None)
    if pending:
        funded='SE' in farm['unlocked_quadrants'] and (not pending['initial'] or private['shed'].get('SHEEP',0)>=6)
        if not funded:_V233_REPORT['sheep_purchase_shortfalls']+=1
        elif len(farm['hands'])<pending['first']+1:_V233_REPORT['sheep_hire_shortfalls']+=1
        else:
            for i in range(2):state['workers'][pending['first']+i]=[(x,5+i) for x in range(5,8)]
            _V233_REPORT['sheep_workers_confirmed']+=2
            if pending['initial']:state['committed']=True;_V233_REPORT['sheep_committed']+=1
    action=_v233_request(observation,action,state,_IMPL.chassis.players[player])
    if not state.get('committed'):return action
    result=copy.deepcopy(action)
    commands=[result.get('farmer') or ['PASS']]+list(result.get('hands') or [])
    commands += [['PASS'] for _ in range(len(farm['hands'])+1-len(commands))]
    state['work']={}
    for actor,targets in state['workers'].items():
        command=_v233_worker(observation,actor,targets);commands[actor]=command
        state['work'][actor]={'step':step,'command':command,'inventory':dict(private['inventories'][actor])}
    result['farmer'],result['hands']=commands[0],commands[1:]
    result=_v234_rescue(observation,result,state)
    stock=projected_shed(result,FarmView(observation))
    for item in ('WOOL','FERTILIZER'):
        scheduled=sum(int(o[2]) for o in result['market'] if o[:2]==['SELL',item])
        count=min(state['credit'][item],max(0,stock.get(item,0)-scheduled))
        if count and len(result['market'])<MAX_ORDERS:
            result['market'].append(['SELL',item,count]);state['credit'][item]-=count
            _V233_REPORT['sheep_extra_wool_sales' if item=='WOOL' else 'sheep_extra_fert_sales']+=count
    return result

_R46_SHEEP_AGENT=agent
_R46_SHADOW_PARENT=_shadow_terminal
_R46_REPORT={}
def _shadow_terminal(obs,config):
    if _V233_STATES.get(int(obs['player']),{}).get('committed'):return None
    return _R46_SHADOW_PARENT(obs,config)
del agent
def agent(observation,configuration=None):
    try:
        if int(observation.get('step',-1))==0:
            for k in _V233_REPORT:_V233_REPORT[k]=0
        result=_R46_SHEEP_AGENT(observation,configuration)
    except Exception:
        _R46_REPORT['sheep_overlay_errors']=_R46_REPORT.get('sheep_overlay_errors',0)+1
        result={'farmer':['PASS'],'hands':[],'market':[]}
    _R46_REPORT.update(getattr(_V233_PARENT,'telemetry',{}))
    _R46_REPORT.update(_V233_REPORT)
    return result
agent.telemetry=_R46_REPORT
agent=globals().pop('agent')

# EXP182: finite-harvest wheat/carrot input planner; original adaptation.
_R51_INPUT_PARENT=agent
_R51_INPUT_STATES={}
_R51_INPUT_REPORT={}
_R51_INPUT_MAX_WORKERS=2
_R51_INPUT_CROPS={'WHEAT':(2,4,6),'CARROT':(2,3,4)}

def _r51_input_forecast(obs,route,expected):
    step=int(obs['step']);day=step//24;farm=obs['farms'][obs['player']]
    pos=[list(farm['farmer'])]+[list(p) for p in farm['hands'][:expected]];targets={}
    for y,line in enumerate(farm['tiles']):
        for x,tile in enumerate(line):
            if not isinstance(tile,dict) or tile.get('crop') not in _R51_INPUT_CROPS:continue
            item=tile['crop'];first,last,cap=_R51_INPUT_CROPS[item]
            if 1<=day-tile['planted_day']<last:
                targets[(x,y)]={'crop':item,'birth':tile['planted_day'],'yield':tile['yield_units'],
                    'until':tile.get('fertilized_until_day',-1),'watered':tile.get('watered_today',False),'water':[],'harvest':None,'first':first,'last':last,'cap':cap}
    access=((4,4),(5,4),(4,5),(5,5));seen=set()
    # Native continuation ends before the reactive terminal closure planner.
    for t in range(step,min(712,(day+4)*24)):
        tape=_IMPL.chassis.routes[2 if t>=648 else route];a=tape[t]
        for actor,c in enumerate([a.get('farmer') or ['PASS'],*(a.get('hands') or [])][:len(pos)]):
            if not c:continue
            xy=tuple(pos[actor]);target=targets.get(xy)
            if target is not None and target['harvest'] is None:
                if c[0]=='WATER' and (t//24,xy) not in seen:
                    seen.add((t//24,xy))
                    if not(t//24==day and target['watered']) and target['first']<=t//24-target['birth']<=target['last']:target['water'].append(t)
                if c[0]=='HARVEST':target['harvest']=t
            if c[0] in MOVES:
                dx,dy=MOVES[c[0]];pos[actor]=[max(0,min(9,pos[actor][0]+dx)),max(0,min(9,pos[actor][1]+dy))]
        for o in a.get('market',[]):
            if o and o[0]=='HIRE':
                counts={p:sum(tuple(q)==p for q in pos) for p in access}
                pos.append(list(min(access,key=lambda p:(counts[p],access.index(p)))))
        if (t+1)%24==0:pos=[[4,4]]
    return targets

def _r51_input_gain(target,arrival,day):
    if target['harvest'] is None or target['harvest']<=arrival:return 0
    extra=sum(arrival<t<=target['harvest'] and day<=t//24<=day+2 and t//24>target['until'] for t in target['water'])
    baseline=target['yield']+sum(2 if t//24<=target['until'] else 1 for t in target['water'])
    return max(0,min(extra,target['cap']-baseline))

def _r51_input_path(obs,targets,action,index):
    step=int(obs['step']);day=step//24
    ready,start=_r62_input_start(obs,action,index)
    prices={p:max(1,int(obs['market']['prices'][p])-2) for p in ('WHEAT','CARROT')}
    fertilizer=max(1,_r37_market_price('FERTILIZER',obs['market']['inventory']['FERTILIZER']-16)+2)
    # Tuple: penalized value, gross value, next free turn, position, path, used,
    # wheat units, carrot units. No state reads from the rival's private farm.
    beam=[(0,0,ready,start,(),frozenset(),0,0)]
    best=None
    for depth in range(8):
        expanded=[]
        for score,gross,now,pos,path,used,wheat,carrot in beam:
            for xy,target in targets.items():
                if xy in used:continue
                arrival=now+abs(pos[0]-xy[0])+abs(pos[1]-xy[1])
                if arrival>=day*24+23:continue
                gain=_r51_input_gain(target,arrival,day)
                if not gain:continue
                item=target['crop'];new_gross=gross+gain*prices[item]
                new_path=path+((xy[0],xy[1],item,target['birth']),)
                expanded.append((new_gross-1.5*fertilizer*len(new_path),new_gross,arrival+1,xy,new_path,
                                 used|{xy},wheat+(gain if item=='WHEAT' else 0),carrot+(gain if item=='CARROT' else 0)))
        if not expanded:break
        expanded.sort(key=lambda s:(-s[0],-s[1],s[2],s[4]))
        beam=expanded[:8]
        if depth>=2:
            candidate=beam[0]
            if best is None or (-candidate[0],-candidate[1],candidate[2],candidate[4])<(-best[0],-best[1],best[2],best[4]):best=candidate
    if best is None:return [],{'WHEAT':0,'CARROT':0}
    return list(best[4]),{'WHEAT':best[6],'CARROT':best[7]}

def _r51_input_control(obs,action,state):
    step=int(obs['step']);day=step//24;hour=step%24;player=int(obs['player']);farm=obs['farms'][player];private=obs['private']
    native=_IMPL.chassis.players[player]
    if state.get('day')!=day:state.update(day=day,workers={},pending=None,placed=[])
    for x,y in state['placed']:
        tile=farm['tiles'][y][x]
        if isinstance(tile,dict) and tile.get('fertilized_until_day',-1)>=day+2:_R51_INPUT_REPORT['input_confirmed_applications']+=1
        else:_R51_INPUT_REPORT['input_application_errors']+=1
    state['placed']=[]
    if state.get('pending'):
        pending=state.pop('pending')
        for actor,plan in pending.items():
            if len(farm['hands'])>=actor:state['workers'][actor]=plan;_R51_INPUT_REPORT['input_confirmed_hires']+=1
            else:_R51_INPUT_REPORT['input_hire_errors']+=1
    if state['workers']:
        changed=copy.deepcopy(action)
        for actor,plan in state['workers'].items():
            inv=private['inventories'][actor];pos=tuple(farm['hands'][actor-1]);cmd=['PASS']
            if not plan['loaded']:
                stock=projected_shed(changed,FarmView(obs));q=min(plan['quantity'],max(0,stock.get('FERTILIZER',0)))
                if q and _shed_adjacent(pos,10):
                    cmd=['PICKUP','FERTILIZER',q];plan['loaded']=True;_R51_INPUT_REPORT['input_loaded_units']+=q
                    if q<plan['quantity']:_R51_INPUT_REPORT['input_stock_shortfalls']+=plan['quantity']-q
            elif inv.get('FERTILIZER',0):
                while plan['path']:
                    x,y,crop,birth=plan['path'][0];tile=farm['tiles'][y][x]
                    if not isinstance(tile,dict) or tile.get('crop')!=crop or tile.get('planted_day')!=birth or tile.get('fertilized_until_day',-1)>=day+2:
                        plan['path'].pop(0);continue
                    cmd=_v219_walk(pos,(x,y)) or ['FERTILIZE']
                    if cmd==['FERTILIZE']:state['placed'].append((x,y));plan['path'].pop(0);_R51_INPUT_REPORT['input_application_requests']+=1
                    break
            changed['hands'][actor-1]=cmd
        return changed
    if hour not in (1,2,3) or not 12<=day<=28:return action
    planned=_v219_native_day(native,day);expected=max(len(a.get('hands',[])) for a in planned)
    if any(o and o[0]=='HIRE' for a in planned[hour:] for o in a.get('market',[])) or native['pending']:return action
    parents=[_V219_STATES.get(player,{}),_V233_STATES.get(player,{})]
    # A parent may retry after a full market queue; its headcount must remain native.
    if day in (12,18) or any(p.get('committed') and p.get('requested_day')!=day for p in parents):return action
    if any(p.get('pending') for p in parents) or any(o and o[0]=='HIRE' for o in action.get('market',[])):return action
    owned=set(range(1,expected+1))
    for p in parents:
        actors=set(p.get('workers',{}))
        if owned&actors:return action
        owned|=actors
    if owned!=set(range(1,len(farm['hands'])+1)):return action
    targets=_r51_input_forecast(obs,native['route'],expected);plans=[];total_q=0;total_cost=0;all_units={'WHEAT':0,'CARROT':0}
    stock=projected_shed(action,FarmView(obs));purchases=sum(max(0,int(o[2])) for o in action.get('market',[]) if len(o)>2 and o[0] in ('BUY_PRODUCT','BUY_ANIMAL'))
    # Units act before market orders. Preserve the native next-turn pickup,
    # after the current parent's actual sales/purchases, before buying tour inputs.
    available=max(0,stock.get('FERTILIZER',0))
    for o in action.get('market',[]):
        if len(o)>=3 and o[:2]==['SELL','FERTILIZER']:available=max(0,available-max(0,int(o[2])))
        elif len(o)>=3 and o[:2]==['BUY_PRODUCT','FERTILIZER']:available+=max(0,int(o[2]))
    next_native=planned[hour+1];native_pickups=sum(max(0,int(c[2]) if len(c)>2 else 1) for c in [next_native.get('farmer') or ['PASS'],*(next_native.get('hands') or [])] if len(c)>1 and c[:2]==['PICKUP','FERTILIZER'])
    topup=max(0,native_pickups-available)
    plans,total_q,total_cost,all_units=_r68_joint_plans(obs,action,targets,stock,purchases,topup)
    if not plans:return action
    state['pending']={len(farm['hands'])+1+i:plan for i,plan in enumerate(plans)}
    _R51_INPUT_REPORT['input_hire_requests']+=len(plans);_R51_INPUT_REPORT['input_purchase_requests']+=total_q+topup
    _R51_INPUT_REPORT['input_forecast_wheat']+=all_units['WHEAT'];_R51_INPUT_REPORT['input_forecast_carrot']+=all_units['CARROT']
    changed=copy.deepcopy(action);changed['market'] += [['BUY_PRODUCT','FERTILIZER',total_q+topup]]+[['HIRE'] for _ in plans];return changed

def agent(observation,configuration=None):
    try:
        step=int(observation['step']);player=int(observation['player']);state=_R51_INPUT_STATES.get(player)
        if state is None or step<=state['step']:
            state=_R51_INPUT_STATES[player]={'step':-1}
            _R51_INPUT_REPORT.update(input_hire_requests=0,input_confirmed_hires=0,input_hire_errors=0,input_purchase_requests=0,
                input_loaded_units=0,input_stock_shortfalls=0,input_application_requests=0,input_confirmed_applications=0,
                input_application_errors=0,input_errors=0,input_forecast_wheat=0,input_forecast_carrot=0)
        state['step']=step;action=_R51_INPUT_PARENT(observation,configuration)
        if configuration is None or all(configuration.get(k,v)==v for k,v in [('boardSize',10),('turnsPerDay',24),('shedCapacity',100),('maxMarketOrdersPerTurn',10)]):
            action=_r51_input_control(observation,action,state)
        _R51_INPUT_REPORT.update(getattr(_R51_INPUT_PARENT,'telemetry',{}));return action
    except Exception:
        _R51_INPUT_REPORT['input_errors']=_R51_INPUT_REPORT.get('input_errors',0)+1
        return {'farmer':['PASS'],'hands':[],'market':[]}
agent.telemetry=_R51_INPUT_REPORT
agent=globals().pop('agent')

# EXP182: project the final hour's actual worker actions before automatic deposit.
_R51_WAREHOUSE_PARENT=agent
_R51_WAREHOUSE_REPORT={}

def _r51_close_warehouse(obs,action):
    step=int(obs['step']);day=step//24
    if step%24!=23 or not 12<=day<=28:return action
    # No speculative product purchase/worker count model: these hours abstain.
    if any(o and o[0] not in ('SELL',) for o in action.get('market',[])):return action
    farm,private=_PLANNER_NS['_clone_state'](obs['farms'][obs['player']],obs['private'])
    commands=[action.get('farmer') or ['PASS'],*(action.get('hands') or [])]
    demand={}
    for c in commands:
        if len(c)>1 and c[0]=='PLANT':demand[c[1]]=demand.get(c[1],0)+1
    blocked={k for k,q in demand.items() if q>private['seeds'].get(k,0)}
    for actor,c in enumerate(commands[:len(private['inventories'])]):
        if len(c)>1 and c[0]=='PLANT' and c[1] in blocked:c=['PASS']
        _PLANNER_NS['_apply_unit_action'](farm,private,actor,c,10,day,24,100)
    post=dict(private['shed'])
    for o in action.get('market',[]):
        if len(o)>=3 and o[0]=='SELL':post[o[1]]=max(0,post.get(o[1],0)-max(0,int(o[2])))
    needed=sum(post.values())+sum(max(0,q) for inv in private['inventories'] for q in inv.values())-100
    if needed<=0:return action
    result=copy.deepcopy(action);orders=result['market']
    # Grain and fertilizer have native input obligations; other products do not.
    # Additional commodity sales are bounded by actual post-action physical stock.
    for item in sorted((p for p in PRODUCTS if p not in ('WHEAT','FERTILIZER')),key=lambda p:-obs['market']['prices'].get(p,0)):
        qty=min(needed,post.get(item,0))
        if not qty:continue
        existing=next((o for o in orders if len(o)>=3 and o[:2]==['SELL',item]),None)
        if existing is not None:existing[2]=max(0,int(existing[2]))+qty
        elif len(orders)<10:orders.append(['SELL',item,qty])
        else:continue
        needed-=qty;post[item]-=qty;_R51_WAREHOUSE_REPORT['warehouse_extra_sales']+=qty
        if needed<=0:break
    if needed>0:
        native=_IMPL.chassis.players[int(obs['player'])];reserve=0
        for t in range(step+1,719):
            future=_IMPL.chassis.routes[2 if t>=648 else native['route']][t]
            for c in [future.get('farmer') or ['PASS'],*(future.get('hands') or [])]:
                if len(c)>1 and c[:2]==['PICKUP','WHEAT']:reserve+=max(0,int(c[2]) if len(c)>2 else 1)
            if any(len(o)>1 and o[:2]==['BUY_PRODUCT','WHEAT'] for o in future.get('market',[])):break
        incoming=sum(max(0,inv.get('WHEAT',0)) for inv in private['inventories'])
        others=sum(q for p,q in post.items() if p!='WHEAT')+sum(max(0,q) for inv in private['inventories'] for p,q in inv.items() if p!='WHEAT')
        # Even if every other carried item deposits first, this grain reserve fits.
        qty=min(needed,post.get('WHEAT',0),max(0,post.get('WHEAT',0)+incoming-reserve)) if 100-others>=reserve else 0
        existing=next((o for o in orders if len(o)>=3 and o[:2]==['SELL','WHEAT']),None)
        if qty and (existing is not None or len(orders)<10):
            if existing is not None:existing[2]=max(0,int(existing[2]))+qty
            else:orders.append(['SELL','WHEAT',qty])
            needed-=qty;_R51_WAREHOUSE_REPORT['warehouse_extra_sales']+=qty
    _R51_WAREHOUSE_REPORT['warehouse_projected_unresolved']+=max(0,needed)
    if result!=action:_R51_WAREHOUSE_REPORT['warehouse_changed_turns']+=1
    return result

def agent(observation,configuration=None):
    result=_R51_WAREHOUSE_PARENT(observation,configuration)
    try:
        if int(observation['step'])==0:_R51_WAREHOUSE_REPORT.update(warehouse_changed_turns=0,warehouse_extra_sales=0,warehouse_projected_unresolved=0,warehouse_errors=0)
        if configuration is None or all(configuration.get(k,v)==v for k,v in [('boardSize',10),('turnsPerDay',24),('shedCapacity',100),('maxMarketOrdersPerTurn',10)]):result=_r51_close_warehouse(observation,result)
    except Exception:_R51_WAREHOUSE_REPORT['warehouse_errors']=_R51_WAREHOUSE_REPORT.get('warehouse_errors',0)+1
    _R51_WAREHOUSE_REPORT.update(getattr(_R51_WAREHOUSE_PARENT,'telemetry',{}));return result
agent.telemetry=_R51_WAREHOUSE_REPORT
agent=globals().pop('agent')

from itertools import permutations as _r53_permutations
_R53_LABOR_REPORT=dict(labor_requests=0,labor_hires_avoided=0,labor_spawn_errors=0,labor_confirmed=0,labor_day26=0,labor_day27=0,labor_day28=0)

def _r53_labor_assignment(obs,action,fertilizer):
    step=int(obs['step']);day=step//24;farm=obs['farms'][obs['player']]
    if day not in (26,27,28) or step%24>2:return None
    # Do not preempt a later price-gated fertilizer request with a smaller unfertilized team.
    if day==27 and not fertilizer:return None
    count=3 if fertilizer else 2
    positions=[list(farm['farmer'])]+[list(p) for p in farm['hands']]
    for i,c in enumerate([action.get('farmer') or ['PASS'],*(action.get('hands') or [])][:len(positions)]):
        if c and c[0] in MOVES:
            dx,dy=MOVES[c[0]];positions[i]=[max(0,min(9,positions[i][0]+dx)),max(0,min(9,positions[i][1]+dy))]
    access=((4,4),(5,4),(4,5),(5,5));spawns=[]
    native_hires=sum(bool(o) and o[0]=='HIRE' for o in action.get('market',[]))
    for i in range(native_hires+count):
        chosen=min(access,key=lambda p:(sum(tuple(q)==p for q in positions),access.index(p)));positions.append(list(chosen))
        if i>=native_hires:spawns.append(chosen)
    groups=(((5,5),(6,5),(7,5),(8,5)),((9,5),(9,6),(8,6)),((5,6),(6,6),(7,6))) if fertilizer else (tuple((x,5) for x in range(5,10)),tuple((x,6) for x in range(5,10)))
    choices=[];remaining=23-step%24
    for assignment in _r53_permutations(groups):
        costs=[]
        for start,path in zip(spawns,assignment):
            distance=abs(start[0]-path[0][0])+abs(start[1]-path[0][1])
            distance+=sum(abs(a[0]-b[0])+abs(a[1]-b[1]) for a,b in zip(path,path[1:]))
            distance+=min(abs(path[-1][0]-x)+abs(path[-1][1]-y) for x,y in access)
            costs.append(distance+(3 if fertilizer else 2)*len(path)+1+int(fertilizer))
        if max(costs)<=remaining:choices.append((max(costs),sum(costs),assignment))
    if not choices:return None
    _,_,assignment=min(choices)
    return dict(paths=assignment,spawns=spawns,remaining=remaining,workers=count,fertilizer=fertilizer)

_R53_LABOR_PARENT=agent
def agent(observation,configuration=None):
    if isinstance(observation,dict) and observation.get('step')==0:
        for k in _R53_LABOR_REPORT:_R53_LABOR_REPORT[k]=0
    result=_R53_LABOR_PARENT(observation,configuration)
    _R53_LABOR_COMBINED.update(getattr(_R53_LABOR_PARENT,'telemetry',{}));_R53_LABOR_COMBINED.update(_R53_LABOR_REPORT)
    return result
_R53_LABOR_COMBINED={}
agent.telemetry=_R53_LABOR_COMBINED
agent=globals().pop('agent')

# EXP193: deterministic HIRE spawn after native unit actions, then next-turn pickup.
def _r62_input_start(obs,action,index):
    farm=obs['farms'][obs['player']]
    positions=[list(farm['farmer'])]+[list(p) for p in farm['hands']]
    for actor,c in enumerate([action.get('farmer') or ['PASS'],*(action.get('hands') or [])][:len(positions)]):
        if c and c[0] in MOVES:
            dx,dy=MOVES[c[0]]
            positions[actor]=[max(0,min(9,positions[actor][0]+dx)),max(0,min(9,positions[actor][1]+dy))]
    access=((4,4),(5,4),(4,5),(5,5))
    native_hires=sum(bool(o) and o[0]=='HIRE' for o in action.get('market',[]))
    for _ in range(native_hires+index+1):
        chosen=min(access,key=lambda p:(sum(tuple(q)==p for q in positions),access.index(p)))
        positions.append(list(chosen))
    return int(obs['step'])+2,chosen

agent=globals().pop('agent')

def _r68_joint_plans(obs,action,targets,stock,purchases,topup):
    farm=obs['farms'][obs['player']];choices=[]
    for mode,first_crop in enumerate((None,'WHEAT','CARROT')):
        remaining=dict(targets);plans=[];total_q=0;total_cost=0;total_value=0
        all_units={'WHEAT':0,'CARROT':0}
        for i in range(_R51_INPUT_MAX_WORKERS):
            subset={xy:t for xy,t in remaining.items() if t['crop']==first_crop} if i==0 and first_crop else remaining
            path,units=_r51_input_path(obs,subset,action,i);q=len(path)
            if q<3 or len(action.get('market',[]))+2+i>10 or sum(stock.values())+purchases+total_q+q+topup>95:break
            quote=_r37_market_price('FERTILIZER',obs['market']['inventory']['FERTILIZER']-total_q-q-topup)
            cost=(q+(topup if i==0 else 0))*(quote+2)+_v219_fib(int(farm['hires_today'])+i)
            value=sum(n*max(1,_r37_market_price(item,obs['market']['inventory'][item]+all_units[item]+n)-2) for item,n in units.items())
            if value<1.5*cost+50 or farm['money']<total_cost+cost+3000:break
            plans.append({'path':path,'quantity':q,'loaded':False});total_q+=q;total_cost+=cost;total_value+=value
            for item,n in units.items():all_units[item]+=n
            for x,y,_,_ in path:remaining.pop((x,y),None)
        score=(total_value-total_cost,total_value,-total_cost,-len(plans),-mode)
        choices.append((score,plans,total_q,total_cost,all_units))
    _,plans,total_q,total_cost,all_units=max(choices,key=lambda v:v[0])
    return plans,total_q,total_cost,all_units

agent=globals().pop('agent')

_R70_STATES={}
_R70_REPORT={}

def _r70_parent_fert_qty(obs,action,planned,offset):
    stock=dict(projected_shed(action,FarmView(obs)))
    for order in action.get('market',[]):
        if len(order)<3:continue
        op,item,quantity=order[:3];quantity=max(0,int(quantity))
        if op=='SELL':stock[item]=max(0,stock.get(item,0)-quantity)
        elif op in ('BUY_PRODUCT','BUY_ANIMAL'):
            stock[item]=stock.get(item,0)+min(quantity,max(0,100-sum(stock.values())))
    next_action=planned[offset+1] if offset+1<len(planned) else {}
    commands=[next_action.get('farmer') or ['PASS'],*(next_action.get('hands') or [])]
    native_need=sum(max(0,int(c[2]) if len(c)>2 else 1) for c in commands if len(c)>1 and c[:2]==['PICKUP','FERTILIZER'])
    quantity=max(10,10+native_need-max(0,stock.get('FERTILIZER',0)))
    if quantity>max(0,100-sum(stock.values())):
        _R70_REPORT['parent_input_capacity_declines']+=1
        return 10
    if quantity>10:
        _R70_REPORT['parent_input_guard_turns']+=1
        _R70_REPORT['parent_input_guard_extra_units']+=quantity-10
    return quantity

def _r70_before(obs):
    player=int(obs['player']);step=int(obs['step']);state=_R70_STATES.get(player)
    if state is None or step<=state['step']:
        state=_R70_STATES[player]={'step':-1,'pending':[],'roles':set()}
        _R70_REPORT.update(parent_input_guard_turns=0,parent_input_guard_extra_units=0,
            parent_input_requests=0,parent_input_confirmed=0,parent_input_shortfalls=0,
            parent_input_errors=0,parent_input_capacity_declines=0)
    state['step']=step
    for request in state['pending']:
        actor,quantity,old=request
        actual=max(0,int(obs['private']['inventories'][actor].get('FERTILIZER',0))-old)
        _R70_REPORT['parent_input_confirmed']+=min(quantity,actual)
        _R70_REPORT['parent_input_shortfalls']+=max(0,quantity-actual)
    state['pending']=[]
    return state

def _r70_after(obs,action,state):
    player=int(obs['player']);day=int(obs['step'])//24
    for actor,role in _V219_STATES.get(player,{}).get('workers',{}).items():
        if not role.get('needs_fertilizer'):continue
        key=(day,actor);inv=obs['private']['inventories'][actor].get('FERTILIZER',0)
        if key not in state['roles']:
            state['roles'].add(key)
            desired=role.get('fertilizer_quantity',10 if role['kind']=='fertilizer' else 5)
            if role.get('loaded') and not role.get('pickup_requested') and inv<desired:
                _R70_REPORT['parent_input_shortfalls']+=desired-inv
        command=action.get('hands',[])[actor-1] if actor<=len(action.get('hands',[])) else ['PASS']
        if len(command)>1 and command[:2]==['PICKUP','FERTILIZER']:
            quantity=max(0,int(command[2]) if len(command)>2 else 1)
            _R70_REPORT['parent_input_requests']+=quantity
            state['pending'].append((actor,quantity,int(inv)))

_R70_PARENT=agent

def agent(observation,configuration=None):
    state=None
    try:state=_r70_before(observation)
    except Exception:_R70_REPORT['parent_input_errors']=_R70_REPORT.get('parent_input_errors',0)+1
    result=_R70_PARENT(observation,configuration)
    try:
        if state is not None:_r70_after(observation,result,state)
    except Exception:_R70_REPORT['parent_input_errors']=_R70_REPORT.get('parent_input_errors',0)+1
    _R70_REPORT.update(getattr(_R70_PARENT,'telemetry',{}))
    return result

agent.telemetry=_R70_REPORT
agent=globals().pop('agent')

def _r79_tomato_fertilizer_worthwhile(obs,action):
    if obs['market']['prices']['FERTILIZER']<=30:return True
    farm=obs['farms'][obs['player']];day=int(obs['step'])//24;bonus=0
    for y in (5,6):
        for x in range(5,10):
            tile=farm['tiles'][y][x]
            if not isinstance(tile,dict) or tile.get('crop')!='TOMATO':continue
            birth=tile['planted_day'];until=tile.get('fertilized_until_day',-1)
            bonus+=sum(until<d and 8<=d+1-birth<=11 for d in range(day,day+3))
    if not bonus:return False
    inventory=obs['market']['inventory']
    price=max(1,_r37_market_price('TOMATO',inventory['TOMATO']+bonus+10)-2)
    fertilizer=max(1,_r37_market_price('FERTILIZER',inventory['FERTILIZER']-10)+2)
    native_hires=sum(bool(o) and o[0]=='HIRE' for o in action.get('market',[]))
    extra_labor=_v219_fib(int(farm['hires_today'])+native_hires+3)
    return bonus*price>=2*(10*fertilizer+extra_labor)+100

agent=globals().pop('agent')

# EXP216: original adaptation of economic feed and fertilizer-sale concepts.
# Conceptual credit: Steven Lee Hans, "Lord Momo Returns", September12 snapshot.
_R85_FEED = True
_R85_FERT = True
_R85_PARENT = agent
_R85_STATES = {}
_R85_REPORT = {}

def _r85_feed(obs, action):
    step=int(obs['step']);day=step//24
    if not 10<=day<=28 or step%24>21:return action
    player=int(obs['player']);native=_IMPL.chassis.players[player]
    tape=_v219_native_day(native,day)
    expected=max(len(a.get('hands',[])) for a in tape)
    farm=obs['farms'][player];positions=[farm['farmer'],*farm['hands']]
    commands=[action.get('farmer') or ['PASS'],*(action.get('hands') or [])]
    prices=obs['market']['prices'];changed=False
    for actor,command in enumerate(commands[:expected+1]):
        if command!=['FEED'] or actor>=len(positions):continue
        tile=_tile_at(farm['tiles'],positions[actor])
        if not isinstance(tile,dict) or tile.get('animal') not in ('GOOSE','COW','SHEEP'):continue
        if tile.get('fed_today') or int(tile.get('consecutive_unfed',0))!=0:continue
        if int(obs['private']['inventories'][actor].get('WHEAT',0))<=0:continue
        item={'GOOSE':'EGG','COW':'MILK','SHEEP':'WOOL'}[tile['animal']]
        bonus=_r88_feed_bonus_cost(tile,day)
        if bonus*(float(prices[item])+5)*1.25>=float(prices['WHEAT']):continue
        if not _r86_next_feed(obs,positions[actor]):continue
        commands[actor]=['PASS'];changed=True
        _R85_REPORT['feed_skips']+=1
    if not changed:return action
    result=copy.deepcopy(action);result['farmer'],result['hands']=commands[0],commands[1:]
    return result

def _r85_reserve(obs, state):
    step=int(obs['step']);player=int(obs['player']);native=_IMPL.chassis.players[player]
    route=native['route'];key=(route,step)
    cache=state.setdefault('native_reserves',{})
    if route not in cache:
        # Backward recurrence preserves field-before-market order within a turn.
        reserve=[0]*720
        for t in range(718,-1,-1):
            a=_IMPL.chassis.routes[2 if t>=648 else route][t]
            pickup=sum(max(0,int(c[2]) if len(c)>2 else 1) for c in [a.get('farmer') or ['PASS'],*(a.get('hands') or [])] if len(c)>1 and c[:2]==['PICKUP','FERTILIZER'])
            purchase=sum(max(0,int(o[2])) for o in a.get('market',[]) if len(o)>2 and o[:2]==['BUY_PRODUCT','FERTILIZER'])
            reserve[t]=pickup+max(0,reserve[t+1]-purchase)
        cache[route]=reserve
    dedicated=0
    for parent in (_V219_STATES.get(player,{}),_V233_STATES.get(player,{})):
        for actor,role in parent.get('workers',{}).items():
            if not isinstance(role,dict) or not role.get('needs_fertilizer') or role.get('loaded'):continue
            desired=role.get('fertilizer_quantity',10 if role.get('kind')=='fertilizer' else 5)
            carried=obs['private']['inventories'][actor].get('FERTILIZER',0)
            dedicated+=max(0,desired-carried)
        pending=parent.get('pending') or {}
        if pending.get('fertilizer'):dedicated+=10
    inputs=_R51_INPUT_STATES.get(player,{})
    for actor,plan in {**inputs.get('workers',{}),**(inputs.get('pending') or {})}.items():
        if not plan.get('loaded'):dedicated+=max(0,int(plan['quantity']))
    return max(14,cache[route][min(719,step+1)]+dedicated)

def _r85_fertilizer(obs, action, state):
    step=int(obs['step']);day=step//24
    if not 6<=day<=28:return action
    market=action.get('market',[])
    if len(market)>=MAX_ORDERS or any(o and o[0]!='SELL' for o in market):return action
    stock=projected_shed(action,FarmView(obs))
    held=max(0,int(stock.get('FERTILIZER',0)))
    sold=sum(max(0,int(o[2])) for o in market if len(o)>2 and o[:2]==['SELL','FERTILIZER'])
    extra=held-sold-_r85_reserve(obs,state)
    if extra<=0:return action
    result=copy.deepcopy(action);result['market'].append(['SELL','FERTILIZER',extra])
    _R85_REPORT['fert_sale_turns']+=1;_R85_REPORT['fert_sale_units']+=extra
    return result

def agent(observation, configuration=None):
    result=_R85_PARENT(observation,configuration)
    try:
        step=int(observation['step']);player=int(observation['player'])
        state=_R85_STATES.get(player)
        if state is None or step<=state['step']:
            state=_R85_STATES[player]={'step':-1}
            _R85_REPORT.update(feed_skips=0,fert_sale_turns=0,fert_sale_units=0,economic_overlay_errors=0)
        state['step']=step
        if configuration is not None and any(configuration.get(k,v)!=v for k,v in [('boardSize',10),('turnsPerDay',24),('shedCapacity',100),('maxMarketOrdersPerTurn',10)]):return result
        if _R85_FEED:result=_r85_feed(observation,result)
        if _R85_FERT:result=_r85_fertilizer(observation,result,state)
        if step%24==23:result=_r51_close_warehouse(observation,result)
    except Exception:
        _R85_REPORT['economic_overlay_errors']=_R85_REPORT.get('economic_overlay_errors',0)+1
    _R85_REPORT.update(getattr(_R85_PARENT,'telemetry',{}))
    return result

agent.telemetry=_R85_REPORT
agent=globals().pop('agent')

# EXP217: planned next-day service is required before discretionary feed cuts.
_R86_FEED_CACHE = {}

def _r86_next_feed(obs, target):
    step=int(obs['step']);day=step//24
    if day==28:return True  # No second dawn follows before game termination.
    player=int(obs['player']);native=_IMPL.chassis.players[player]
    tomorrow=day+1;route=2 if tomorrow>=27 else native['route'];key=(route,tomorrow)
    if key not in _R86_FEED_CACHE:
        positions=[(4,4)];wheat=[0];access=((4,4),(5,4),(4,5),(5,5));feeds=set()
        for hour in range(24):
            a=_IMPL.chassis.routes[route][tomorrow*24+hour]
            commands=[a.get('farmer') or ['PASS'],*(a.get('hands') or [])]
            for actor,command in enumerate(commands[:len(positions)]):
                if not command:continue
                pos=positions[actor];op=command[0]
                if op in MOVES:
                    dx,dy=MOVES[op];positions[actor]=(max(0,min(9,pos[0]+dx)),max(0,min(9,pos[1]+dy)))
                elif command[:2]==['PICKUP','WHEAT'] and pos in access:
                    wheat[actor]+=max(0,int(command[2]) if len(command)>2 else 1)
                elif op=='FEED' and wheat[actor]>0:
                    wheat[actor]-=1
                    if hour<=21:feeds.add(pos)
                elif op=='DROP' and pos in access:wheat[actor]=0
                elif command[:2]==['PLACE','WHEAT'] and pos in access:
                    wheat[actor]=max(0,wheat[actor]-max(0,int(command[2]) if len(command)>2 else 1))
            for order in a.get('market',[]):
                if order and order[0]=='HIRE':
                    chosen=min(access,key=lambda p:(positions.count(p),access.index(p)))
                    positions.append(chosen);wheat.append(0)
        _R86_FEED_CACHE[key]=frozenset(feeds)
    return tuple(target) in _R86_FEED_CACHE[key]

agent=globals().pop('agent')

# EXP219: charge care credits only when this feeding decision can affect them.
_R88_PHASE = True
_R88_HORIZON = True
_R88_ANIMAL_DAYS = {'GOOSE': (4, 1), 'COW': (8, 2), 'SHEEP': (6, 3)}


def _r88_feed_bonus_cost(tile, day):
    first, interval = _R88_ANIMAL_DAYS[tile['animal']]
    first += int(tile['placed_day'])
    tomorrow = day + 1
    produces = tomorrow >= first and (tomorrow - first) % interval == 0
    pending = max(0, int(tile.get('pending_care_bonus', 0)))
    if _R88_PHASE and not produces:
        pending = 0  # It remains banked on non-production dawns.
    care = 1  # Conservative: charge one possible CARE even if not yet observed.
    if _R88_HORIZON:
        # Today's care is added AFTER tomorrow's production; its first possible
        # payout is a later production dawn, which must occur before game end.
        next_use = first
        if next_use <= tomorrow:
            next_use += ((tomorrow - next_use) // interval + 1) * interval
        if next_use > 29:
            care = 0
    return pending + care


agent = globals().pop('agent')

# EXP226: retain physical grain for two complete days before trimming a buy.
_R95_PARENT = agent
_R95_REPORT = {}
_R95_RESERVES = {}

def _r95_reserve(obs):
    step=int(obs['step']);player=int(obs['player'])
    native=_IMPL.chassis.players[player];route=native['route']
    key=(route,step)
    if key not in _R95_RESERVES:
        demand=6  # Physical buffer beyond every scheduled pickup and sale.
        for t in range(step+1,min(719,step+49)):
            a=_IMPL.chassis.routes[2 if t>=648 else route][t]
            for c in [a.get('farmer') or ['PASS'],*(a.get('hands') or [])]:
                if c[:2]==['PICKUP','WHEAT']:
                    demand+=max(0,int(c[2]) if len(c)>2 else 1)
            for o in a.get('market',[]):
                if len(o)>2 and o[:2]==['SELL','WHEAT']:
                    demand+=max(0,int(o[2]))
        _R95_RESERVES[key]=demand
    demand=_R95_RESERVES[key]
    # Reserve full feed for a possible southeast sheep commitment. Do not
    # rely on its future discretionary buy, eligibility, or existing cargo.
    if obs['town']['unlocked_shops'].count('YARN_STORE')>=2:
        demand+=6*len({t//24 for t in range(step+1,step+49) if t//24>=12})
    return demand

def _r95_replenish(obs,action):
    step=int(obs['step'])
    if not 10<=step//24<=11:return action
    orders=action.get('market') or []
    if not any(len(o)>2 and o[:2]==['BUY_PRODUCT','WHEAT'] and int(o[2])>0 for o in orders):return action
    # Preserve all same-turn grain trading/arbitrage sequences unchanged.
    if any(o[:2]==['SELL','WHEAT'] for o in orders):return action
    farm,private=_PLANNER_NS['_clone_state'](obs['farms'][obs['player']],obs['private'])
    commands=[action.get('farmer') or ['PASS'],*(action.get('hands') or [])]
    for actor,c in enumerate(commands[:len(private['inventories'])]):
        _PLANNER_NS['_apply_unit_action'](farm,private,actor,c,10,step//24,24,100)
    held=max(0,int(private['shed'].get('WHEAT',0)))
    reserve=_r95_reserve(obs);result=None;removed=0
    for i,o in enumerate(orders):
        if len(o)<3 or o[:2]!=['BUY_PRODUCT','WHEAT']:continue
        quantity=max(0,int(o[2]));retained=min(quantity,max(0,reserve-held))
        held+=retained
        if retained<quantity:
            if result is None:result=copy.deepcopy(action)
            result['market'][i][2]=retained  # Zero keeps every later order slot.
            removed+=quantity-retained
    if result is None:return action
    _R95_REPORT['replenishment_trim_turns']+=1
    _R95_REPORT['replenishment_trim_units']+=removed
    return result

def agent(observation,configuration=None):
    result=_R95_PARENT(observation,configuration)
    try:
        if int(observation['step'])==0:
            _R95_REPORT.update(replenishment_trim_turns=0,replenishment_trim_units=0,replenishment_errors=0)
        if configuration is not None and any(configuration.get(k,v)!=v for k,v in [('boardSize',10),('turnsPerDay',24),('shedCapacity',100),('maxMarketOrdersPerTurn',10)]):return result
        result=_r95_replenish(observation,result)
    except Exception:
        _R95_REPORT['replenishment_errors']=_R95_REPORT.get('replenishment_errors',0)+1
    _R95_REPORT.update(getattr(_R95_PARENT,'telemetry',{}))
    return result

agent.telemetry=_R95_REPORT
agent=globals().pop('agent')

# EXP231: protect inputs using funded current orders without unassigned cash padding from observed physical resources.
_R97_PARENT=agent
_R97_REPORT={}
_R97_LAST={}

def _r97_market_stock(shed,orders):
    stock=dict(shed);buys={};sales={}
    for index,order in enumerate(orders):
        if len(order)<3:continue
        op,item,n=order[:3];n=max(0,int(n))
        if op=='SELL':
            q=min(n,max(0,stock.get(item,0)));stock[item]=stock.get(item,0)-q;sales[index]=q
        elif op in ('BUY_PRODUCT','BUY_ANIMAL'):
            q=min(n,max(0,100-sum(stock.values())));stock[item]=stock.get(item,0)+q;buys[index]=q
    return stock,buys,sales

def _r97_delivery(stock,private,night):
    stock=dict(stock);lost={}
    if night:
        for inv in private['inventories']:
            for item,q in inv.items():
                q=max(0,int(q));take=min(q,max(0,100-sum(stock.values())))
                stock[item]=stock.get(item,0)+take
                if q>take:lost[item]=lost.get(item,0)+q-take
    return stock,lost

def _r97_budget(obs,orders):
    farm=obs['farms'][obs['player']];cost=0;hires=int(farm['hires_today'])
    # At most ten 100-unit purchases per opponent turn. The additional 1000
    # own units give an intentionally conservative upper bound on buy quotes.
    prices={p:_r37_market_price(p,obs['market']['inventory'][p]-2000) for p in ('WHEAT','FERTILIZER')}
    for order in orders:
        if not order:continue
        op=order[0]
        if op=='HIRE':cost+=_v219_fib(hires);hires+=1
        elif op=='BUY_LAND':cost+=4000
        elif len(order)>2:
            item=order[1];q=max(0,int(order[2]))
            if op=='BUY_PRODUCT':cost+=q*prices[item]
            elif op=='BUY_ANIMAL':cost+=q*{'GOOSE':300,'COW':400,'SHEEP':500}[item]
            elif op=='BUY_SEED':cost+=q*{'WHEAT':10,'CARROT':20,'TOMATO':50,'STRAWBERRY':100,'MELON':80}[item]
    return cost<=farm['money']  # No current sale proceeds are assumed.

def _r97_supply(obs,action):
    step=int(obs['step']);player=int(obs['player']);day=step//24
    if not 144<=step<695:return action
    native=_IMPL.chassis.players[player]
    future=_IMPL.chassis.routes[2 if step+1>=648 else native['route']][step+1]
    commands=[future.get('farmer') or ['PASS'],*(future.get('hands') or [])]
    following=_IMPL.chassis.routes[2 if step+2>=648 else native['route']][step+2]
    next_orders=future.get('market') or []
    prefund=0
    if len(next_orders)==10 and not any(o[:2] in (['BUY_PRODUCT','WHEAT'],['SELL','WHEAT']) for o in next_orders):
        later=[following.get('farmer') or ['PASS'],*(following.get('hands') or [])]
        demand=lambda cs:sum(max(0,int(c[2]) if len(c)>2 else 1) for c in cs if c[:2]==['PICKUP','WHEAT'])
        if demand(later):prefund=demand(commands)+demand(later)
    if not prefund and not any(c[:2]==['PICKUP','WHEAT'] for c in commands):return action
    orders=action.get('market') or []
    if len(orders)>10 or not _r97_budget(obs,orders):
        _R97_REPORT['supply_budget_declines']+=1;return action
    farm,private=_PLANNER_NS['_clone_state'](obs['farms'][player],obs['private'])
    for actor,c in enumerate([action.get('farmer') or ['PASS'],*(action.get('hands') or [])][:len(private['inventories'])]):
        _PLANNER_NS['_apply_unit_action'](farm,private,actor,c,10,day,24,100)
    positions=[tuple(farm['farmer']),*map(tuple,farm['hands'])];night=step%24==23
    access=((4,4),(5,4),(4,5),(5,5))
    if night:positions=[(4,4)]
    else:
        for order in orders:
            if order and order[0]=='HIRE':positions.append(min(access,key=lambda p:(positions.count(p),access.index(p))))
    need=sum(max(0,int(c[2]) if len(c)>2 else 1) for pos,c in zip(positions,commands) if pos in access and c[:2]==['PICKUP','WHEAT'])
    need=max(need,prefund)
    if not need:return action
    original_stock,original_buys,_=_r97_market_stock(private['shed'],orders)
    original_final,original_loss=_r97_delivery(original_stock,private,night)
    if original_final.get('WHEAT',0)>=need:return action
    result=copy.deepcopy(action);proposed=result['market'];blocked=False
    def project(candidate):
        stock,buys,sales=_r97_market_stock(private['shed'],candidate)
        final,loss=_r97_delivery(stock,private,night)
        safe=all(buys.get(i,0)>=q for i,q in original_buys.items()) and all(q<=original_loss.get(item,0) for item,q in loss.items())
        return final,sales,safe
    # Hold an existing grain sale first. Preserve all order indices and every
    # originally funded buy; no extra overnight overflow may be introduced.
    for index in range(len(proposed)-1,-1,-1):
        if proposed[index][:2]!=['SELL','WHEAT']:continue
        final,sales,safe=project(proposed);shortage=max(0,need-final.get('WHEAT',0))
        if not shortage:break
        sold=sales.get(index,0)
        if not sold:continue
        old=proposed[index][2];proposed[index][2]=max(0,sold-shortage)
        after,_,safe=project(proposed)
        if not safe or after.get('WHEAT',0)<=final.get('WHEAT',0):proposed[index][2]=old
    final,_,safe=project(proposed);shortage=max(0,need-final.get('WHEAT',0))
    if shortage:
        last_sale=max((i for i,o in enumerate(proposed) if o[:2]==['SELL','WHEAT']),default=-1)
        index=next((i for i in range(len(proposed)-1,last_sale,-1) if proposed[i][:2]==['BUY_PRODUCT','WHEAT']),None)
        if index is not None:proposed[index][2]=max(0,int(proposed[index][2]))+shortage
        elif len(proposed)<10:proposed.append(['BUY_PRODUCT','WHEAT',shortage])
        else:_R97_REPORT['supply_slot_declines']+=1;return action
    final,_,safe=project(proposed)
    if not safe or final.get('WHEAT',0)<need:
        _R97_REPORT['supply_capacity_declines']+=1;return action
    if not _r97_budget(obs,proposed):
        _R97_REPORT['supply_budget_declines']+=1;return action
    if prefund:
        _R97_REPORT['supply_prefund_changes']+=1
        _R97_REPORT['supply_prefund_units']+=max(0,final.get('WHEAT',0)-original_final.get('WHEAT',0))
    if step<288:
        _R97_REPORT['supply_early_changes']+=1
        _R97_REPORT['supply_early_units']+=max(0,final.get('WHEAT',0)-original_final.get('WHEAT',0))
    _R97_REPORT['supply_guard_changes']+=1
    _R97_REPORT['supply_grain_protected']+=final.get('WHEAT',0)-original_final.get('WHEAT',0)
    _R97_REPORT['supply_buy_units']+=sum(max(0,int(o[2])) for o in proposed if o[:2]==['BUY_PRODUCT','WHEAT'])-sum(max(0,int(o[2])) for o in orders if o[:2]==['BUY_PRODUCT','WHEAT'])
    return result

def agent(observation,configuration=None):
    result=_R97_PARENT(observation,configuration)
    try:
        player=int(observation['player']);step=int(observation['step'])
        if player not in _R97_LAST or step<=_R97_LAST[player]:
            _R97_REPORT.update(supply_guard_changes=0,supply_grain_protected=0,supply_buy_units=0,supply_early_changes=0,supply_early_units=0,supply_prefund_changes=0,supply_prefund_units=0,supply_slot_declines=0,supply_capacity_declines=0,supply_budget_declines=0,supply_errors=0)
        _R97_LAST[player]=step
        if configuration is None or all(configuration.get(k,v)==v for k,v in [('boardSize',10),('turnsPerDay',24),('shedCapacity',100),('maxMarketOrdersPerTurn',10),('farmHandCostMult',1)]):result=_r97_supply(observation,result)
    except Exception:_R97_REPORT['supply_errors']=_R97_REPORT.get('supply_errors',0)+1
    _R97_REPORT.update(getattr(_R97_PARENT,'telemetry',{}))
    return result

agent.telemetry=_R97_REPORT
agent=globals().pop('agent')

"""Original funded planting and first-dawn labor contract, Ahmed Berat Ozer."""
_R124_PARENT=agent
_R124_STATES={}
_R124_REPORT={}

def _r124_labor_reserve(native):
    n=sum(bool(o) and o[0]=='HIRE' for o in native[24].get('market',[]))
    return sum(_v219_fib(i) for i in range(n)),n

def _r124_seed_budget(obs,action,reserve):
    if not any(o and o[0]=='BUY_SEED' for o in action.get('market',[])):return action
    player=int(obs['player']);budget=dict(obs,farms=[dict(f) for f in obs['farms']]);budget['farms'][player]['money']-=reserve
    if _r97_budget(budget,action.get('market',[])):return action
    result=copy.deepcopy(action)
    for i in range(len(result['market'])-1,-1,-1):
        order=result['market'][i]
        if len(order)<3 or order[0]!='BUY_SEED':continue
        before=max(0,int(order[2]));order[2]=before
        while order[2]>0 and not _r97_budget(budget,result['market']):order[2]-=1
        n=before-order[2]
        if n:
            _R124_REPORT['opening_seed_budget_units']+=n
            _R124_REPORT['opening_seed_budget_cost']+=n*{'WHEAT':10,'CARROT':20,'TOMATO':50,'STRAWBERRY':100,'MELON':80}[order[1]]
        if _r97_budget(budget,result['market']):break
    return result

def _r124_atomic(obs,action,state):
    commands=[action.get('farmer') or ['PASS'],*(action.get('hands') or [])]
    demand={}
    for c in commands:
        if len(c)>1 and c[0]=='PLANT':demand[c[1]]=demand.get(c[1],0)+1
    if not demand:return action
    available=obs['private']['seeds'];blocked={p for p,n in demand.items() if n>available.get(p,0)}
    farm,private=_PLANNER_NS['_clone_state'](obs['farms'][obs['player']],obs['private'])
    changed=False;kept=[]
    for actor,c in enumerate(commands):
        if len(c)>1 and c[0]=='PLANT':
            pos=None if actor>=len(private['inventories']) else farm['farmer'] if actor==0 else farm['hands'][actor-1]
            valid=pos is not None and farm['tiles'][pos[1]][pos[0]] is None and private['seeds'].get(c[1],0)>0
            if not valid:
                commands[actor]=['PASS'];changed=True;_R124_REPORT['opening_atomic_dropped']+=1
            elif c[1] in blocked:
                kept.append(dict(xy=list(pos),crop=c[1],birth=0));_R124_REPORT['opening_atomic_rescued_requests']+=1
        if actor<len(private['inventories']):_PLANNER_NS['_apply_unit_action'](farm,private,actor,commands[actor],10,0,24,100)
    if kept:state['pending_plants']=kept
    if changed:
        action=dict(action,farmer=commands[0],hands=commands[1:])
    return action

def agent(observation,configuration=None):
    result=_R124_PARENT(observation,configuration)
    try:
        player=int(observation['player']);step=int(observation['step']);state=_R124_STATES.get(player)
        if state is None or step<=state['step']:
            state=_R124_STATES[player]={'step':-1,'pending_plants':[]}
            _R124_REPORT.update(opening_seed_budget_units=0,opening_seed_budget_cost=0,opening_atomic_dropped=0,opening_atomic_rescued_requests=0,opening_atomic_rescued_confirmed=0,opening_atomic_plant_errors=0,opening_day1_cash=0,opening_day1_hires_requested=0,opening_day1_hires_confirmed=0,opening_day1_hire_shortfalls=0,opening_contract_errors=0)
        state['step']=step;farm=observation['farms'][player]
        for p in state.pop('pending_plants',[]):
            x,y=p['xy'];t=farm['tiles'][y][x]
            if isinstance(t,dict) and t.get('crop')==p['crop'] and t.get('planted_day')==p['birth']:_R124_REPORT['opening_atomic_rescued_confirmed']+=1
            else:_R124_REPORT['opening_atomic_plant_errors']+=1
        standard=configuration is None or all(configuration.get(k,v)==v for k,v in [('boardSize',10),('turnsPerDay',24),('shedCapacity',100),('maxMarketOrdersPerTurn',10),('farmHandCostMult',1)])
        if standard and 0<=step<24:
            native=_ROUTES[_IMPL.chassis.players[player]['route']];reserve,hires=_r124_labor_reserve(native)
            result=_r124_seed_budget(observation,result,reserve);result=_r124_atomic(observation,result,state)
        if step==24:
            _R124_REPORT['opening_day1_cash']=farm['money'];state['hires']=sum(bool(o) and o[0]=='HIRE' for o in result.get('market',[]));_R124_REPORT['opening_day1_hires_requested']=state['hires']
        if step==25:
            actual=len(farm['hands']);_R124_REPORT['opening_day1_hires_confirmed']=actual;_R124_REPORT['opening_day1_hire_shortfalls']=max(0,state.get('hires',0)-actual)
    except Exception:_R124_REPORT['opening_contract_errors']=_R124_REPORT.get('opening_contract_errors',0)+1
    _R124_REPORT.update(getattr(_R124_PARENT,'telemetry',{}))
    return result
agent.telemetry=_R124_REPORT
agent=globals().pop('agent')

"""Fund urgent grain at the first quote slot; avoid unwatered last-hour plants.
Original safety contracts by Ahmed Berat Ozer, EXP258.
"""
_R127_PARENT=agent
_R127_STATES={}
_R127_REPORT={}

def _r127_fields(obs,action):
    farm,private=_PLANNER_NS['_clone_state'](obs['farms'][obs['player']],obs['private'])
    commands=[action.get('farmer') or ['PASS'],*(action.get('hands') or [])]
    demand={}
    for c in commands:
        if len(c)>1 and c[0]=='PLANT':demand[c[1]]=demand.get(c[1],0)+1
    blocked={p for p,n in demand.items() if n>private['seeds'].get(p,0)}
    for actor,c in enumerate(commands[:len(private['inventories'])]):
        if len(c)>1 and c[0]=='PLANT' and c[1] in blocked:continue
        _PLANNER_NS['_apply_unit_action'](farm,private,actor,c,10,int(obs['step'])//24,24,100)
    return farm,private

def _r127_last_hour(obs,action):
    if int(obs['step'])%24!=23:return action
    commands=[action.get('farmer') or ['PASS'],*(action.get('hands') or [])]
    if not any(c and c[0]=='PLANT' for c in commands):return action
    result=copy.deepcopy(action);changed=False
    # Removing rejected requests can unblock the engine's atomic crop batch.
    # Recompute until every retained request ends the turn with a watered crop.
    for _ in range(len(commands)+1):
        farm,_=_r127_fields(obs,result);original=obs['farms'][obs['player']]
        positions=[original['farmer'],*original['hands']];drop=[]
        for actor,c in enumerate(commands):
            if not c or c[0]!='PLANT':continue
            tile=None
            if actor<len(positions):
                x,y=positions[actor];tile=farm['tiles'][y][x]
            if not (isinstance(tile,dict) and tile.get('kind')=='PLANT' and tile.get('crop')==c[1] and tile.get('planted_day')==int(obs['step'])//24 and tile.get('watered_today')):drop.append(actor)
        if not drop:break
        for actor in drop:commands[actor]=['PASS']
        result['farmer']=commands[0];result['hands']=commands[1:];changed=True
        _R127_REPORT['last_hour_plants_dropped']+=len(drop)
    return result if changed else action

def _r127_prefix_bound(obs,quantity):
    inventory=int(obs['market']['inventory']['WHEAT'])
    # Both players quote one unit before either commits. Before own unit j,
    # at most j-1 own and j-1 opponent wheat purchases have depleted inventory.
    return sum(_r37_market_price('WHEAT',inventory-(2*j-1)) for j in range(1,quantity+1))

def _r127_priority(obs,action,state):
    step=int(obs['step']);player=int(obs['player'])
    if not 144<=step<695:return action
    orders=action.get('market') or []
    if len(orders)>9 or any(o[:2] in (['BUY_PRODUCT','WHEAT'],['SELL','WHEAT']) for o in orders):return action
    native=_IMPL.chassis.players[player]
    future=_IMPL.chassis.routes[2 if step+1>=648 else native['route']][step+1]
    commands=[future.get('farmer') or ['PASS'],*(future.get('hands') or [])]
    if not any(c[:2]==['PICKUP','WHEAT'] for c in commands):return action
    if not _r97_budget(obs,orders):return action
    farm,private=_r127_fields(obs,action);night=step%24==23
    access=((4,4),(5,4),(4,5),(5,5));positions=[tuple(farm['farmer']),*map(tuple,farm['hands'])]
    if night:positions=[(4,4)]
    else:
        for o in orders:
            if o and o[0]=='HIRE':positions.append(min(access,key=lambda p:(positions.count(p),access.index(p))))
    need=sum(max(0,int(c[2]) if len(c)>2 else 1) for pos,c in zip(positions,commands) if pos in access and c[:2]==['PICKUP','WHEAT'])
    stock,buys,_=_r97_market_stock(private['shed'],orders);before,loss=_r97_delivery(stock,private,night)
    shortage=max(0,need-before.get('WHEAT',0))
    if not shortage or shortage>100-sum(private['shed'].values()):return action
    cost=_r127_prefix_bound(obs,shortage)
    budget=dict(obs,farms=[dict(f) for f in obs['farms']]);budget['farms'][player]['money']-=cost
    if not _r97_budget(budget,orders):return action
    proposed=[['BUY_PRODUCT','WHEAT',shortage],*copy.deepcopy(orders)]
    stock,after_buys,_=_r97_market_stock(private['shed'],proposed);after,after_loss=_r97_delivery(stock,private,night)
    if after.get('WHEAT',0)<need or any(after_buys.get(i+1,0)<q for i,q in buys.items()) or any(q>loss.get(p,0) for p,q in after_loss.items()):return action
    state['pending_grain']=(step+1,after.get('WHEAT',0),shortage)
    _R127_REPORT['priority_grain_orders']+=1;_R127_REPORT['priority_grain_units']+=shortage
    return dict(action,market=proposed)

def agent(observation,configuration=None):
    result=_R127_PARENT(observation,configuration)
    try:
        player=int(observation['player']);step=int(observation['step']);state=_R127_STATES.get(player)
        if state is None or step<=state['step']:
            state=_R127_STATES[player]={'step':-1}
            _R127_REPORT.update(last_hour_plants_dropped=0,priority_grain_orders=0,priority_grain_units=0,priority_grain_confirmed=0,priority_grain_shortfalls=0,priority_contract_errors=0)
        pending=state.pop('pending_grain',None)
        if pending and step==pending[0]:
            if observation['private']['shed'].get('WHEAT',0)>=pending[1]:_R127_REPORT['priority_grain_confirmed']+=pending[2]
            else:_R127_REPORT['priority_grain_shortfalls']+=1
        state['step']=step
        standard=configuration is None or all(configuration.get(k,v)==v for k,v in [('boardSize',10),('turnsPerDay',24),('shedCapacity',100),('maxMarketOrdersPerTurn',10),('farmHandCostMult',1)])
        if standard:result=_r127_priority(observation,_r127_last_hour(observation,result),state)
    except Exception:_R127_REPORT['priority_contract_errors']=_R127_REPORT.get('priority_contract_errors',0)+1
    _R127_REPORT.update(getattr(_R127_PARENT,'telemetry',{}))
    return result
agent.telemetry=_R127_REPORT
agent=globals().pop('agent')

"""Observed-input service order and guaranteed first-sale funding, Ahmed Berat Ozer."""
_R128_PARENT=agent
_R128_STATES={}
_R128_REPORT={}

def _r128_commands(action):
    return [action.get('farmer') or ['PASS'],*(action.get('hands') or [])]

def _r128_future(obs,offset=1):
    step=int(obs['step'])+offset;native=_IMPL.chassis.players[int(obs['player'])]
    return _IMPL.chassis.routes[2 if step>=648 else native['route']][step]

def _r128_sale_credit(obs,action):
    orders=action.get('market') or []
    if not orders or len(orders[0])<3 or orders[0][0]!='SELL' or orders[0][1]=='WHEAT':return 0
    item=orders[0][1]
    if item not in obs['market']['inventory']:return 0
    _,private=_r127_fields(obs,action)
    q=min(max(0,int(orders[0][2])),max(0,int(private['shed'].get(item,0))))
    inventory=int(obs['market']['inventory'][item])
    return sum(_r37_market_price(item,inventory+2*j) for j in range(q))

def _r128_next_need(obs,farm,orders,advanced):
    step=int(obs['step']);access=((4,4),(5,4),(4,5),(5,5))
    positions=[tuple(farm['farmer']),*map(tuple,farm['hands'])]
    if step%24==23:positions=[(4,4)]
    else:
        for order in orders:
            if order and order[0]=='HIRE':positions.append(min(access,key=lambda p:(positions.count(p),access.index(p))))
    return sum(max(0,int(c[2]) if len(c)>2 else 1) for actor,(p,c) in enumerate(zip(positions,_r128_commands(_r128_future(obs)))) if actor not in advanced and p in access and c[:2]==['PICKUP','WHEAT'])

def _r128_field_safe(obs,before,after,advanced):
    orders=before.get('market') or []
    if not _r97_budget(obs,orders):return False,None
    oldfarm,oldprivate=_r127_fields(obs,before);farm,private=_r127_fields(obs,after)
    oldcommands=_r128_commands(before);commands=_r128_commands(after)
    for i,c in enumerate(oldcommands[:len(private['inventories'])]):
        if c and c[0]=='PICKUP' and c==commands[i]:
            item=c[1]
            if private['inventories'][i].get(item,0)<oldprivate['inventories'][i].get(item,0):return False,None
    oldstock,oldbuys,oldsales=_r97_market_stock(oldprivate['shed'],orders)
    stock,buys,sales=_r97_market_stock(private['shed'],orders)
    oldfinal,oldloss=_r97_delivery(oldstock,oldprivate,int(obs['step'])%24==23)
    final,loss=_r97_delivery(stock,private,int(obs['step'])%24==23)
    if any(buys.get(i,0)<q for i,q in oldbuys.items()) or any(sales.get(i,0)<q for i,q in oldsales.items()) or any(q>oldloss.get(p,0) for p,q in loss.items()):return False,None
    need=_r128_next_need(obs,farm,orders,advanced)
    pending=_R127_STATES.get(int(obs['player']),{}).get('pending_grain')
    if pending and pending[0]==int(obs['step'])+1:need=max(need,pending[1])
    if final.get('WHEAT',0)<min(need,oldfinal.get('WHEAT',0)):return False,None
    return True,private

def _r128_food_need(obs,farm,private,actor):
    farm,private=copy.deepcopy(farm),copy.deepcopy(private);missing=0;day=int(obs['step'])//24
    for offset in range(1,min(5,24-int(obs['step'])%24)):
        cs=_r128_commands(_r128_future(obs,offset));c=cs[actor] if actor<len(cs) else ['PASS']
        if c[:2]==['PICKUP','WHEAT']:break
        if c==['FEED']:
            x,y=farm['farmer'] if actor==0 else farm['hands'][actor-1];tile=farm['tiles'][y][x]
            if isinstance(tile,dict) and tile.get('animal') and not tile.get('fed_today') and private['inventories'][actor].get('WHEAT',0)<=0:
                private['inventories'][actor]['WHEAT']=1;missing+=1
        _PLANNER_NS['_apply_unit_action'](farm,private,actor,c,10,day,24,100)
    return missing

def _r128_service(obs,action,state):
    step=int(obs['step']);farm=obs['farms'][obs['player']];private=obs['private'];positions=[farm['farmer'],*farm['hands']]
    for item in state.pop('arrivals',[]):
        if item['step']!=step or item['actor']>=len(private['inventories']) or private['inventories'][item['actor']].get('WHEAT',0)<item['expected']:_R128_REPORT['service_arrival_errors']+=1
        else:_R128_REPORT['service_confirmed_units']+=item['quantity']
    old_pending=state.pop('swaps',{});result=action;cs=_r128_commands(result)
    for actor,pending in old_pending.items():
        if step!=pending['step'] or actor>=len(positions) or list(positions[actor])!=pending['xy'] or cs[actor]!=pending['pickup']:
            _R128_REPORT['service_swap_errors']+=1;continue
        x,y=positions[actor];tile=farm['tiles'][y][x]
        if not isinstance(tile,dict) or tile.get('animal')!=pending['animal'] or tile.get('placed_day')!=pending['birth']:
            _R128_REPORT['service_swap_errors']+=1;continue
        if private['inventories'][actor].get('WHEAT',0)<pending['quantity']+1:
            _R128_REPORT['service_swap_errors']+=1;continue
        cs[actor]=['PASS'] if tile.get('fed_today') else ['FEED']
        _R128_REPORT['service_swaps_completed']+=1
    if old_pending:
        proposed=dict(result,farmer=cs[0],hands=cs[1:]);safe,_=_r128_field_safe(obs,result,proposed,{})
        if safe:result=proposed
        else:_R128_REPORT['service_swap_errors']+=1
    if not 144<=step<647:return result
    cs=_r128_commands(result);future=_r128_commands(_r128_future(obs));proposed=copy.deepcopy(result);commands=_r128_commands(proposed)
    swaps={};arrivals=[];prefetches=0
    projected_farm,projected_private=_r127_fields(obs,result)
    for actor,c in enumerate(cs[:len(private['inventories'])]):
        x,y=positions[actor]
        if (x,y) not in ((4,4),(5,4),(4,5),(5,5)):continue
        held=max(0,int(private['inventories'][actor].get('WHEAT',0)));tile=farm['tiles'][y][x]
        nxt=future[actor] if actor<len(future) else ['PASS']
        if c==['FEED'] and held==0 and step%24<=21 and isinstance(tile,dict) and tile.get('animal') and not tile.get('fed_today') and nxt[:2]==['PICKUP','WHEAT']:
            q=max(0,int(nxt[2]) if len(nxt)>2 else 1)
            if not q:continue
            commands[actor]=['PICKUP','WHEAT',q+1]
            swaps[actor]=dict(step=step+1,xy=[x,y],animal=tile['animal'],birth=tile.get('placed_day'),quantity=q,pickup=copy.deepcopy(nxt))
            arrivals.append(dict(step=step+1,actor=actor,expected=q+1,quantity=q+1))
        elif c==['PASS']:
            q=_r128_food_need(obs,projected_farm,projected_private,actor)
            if q:
                commands[actor]=['PICKUP','WHEAT',q];prefetches+=1
                arrivals.append(dict(step=step+1,actor=actor,expected=held+q,quantity=q))
    if not arrivals:return result
    proposed['farmer']=commands[0];proposed['hands']=commands[1:]
    safe,after=_r128_field_safe(obs,result,proposed,swaps)
    if not safe or any(after['inventories'][p['actor']].get('WHEAT',0)<p['expected'] for p in arrivals):
        _R128_REPORT['service_capacity_declines']+=1;return result
    state['swaps']=swaps;state['arrivals']=arrivals
    _R128_REPORT['service_swaps_started']+=len(swaps);_R128_REPORT['service_idle_preloads']+=prefetches
    _R128_REPORT['service_requested_units']+=sum(p['quantity'] for p in arrivals)
    return proposed

def _r128_credit_supply(obs,action,state):
    step=int(obs['step'])
    if not 144<=step<695 or _r97_budget(obs,action.get('market') or []):return action
    credit=_r128_sale_credit(obs,action)
    if not credit:return action
    budget=dict(obs,farms=[dict(f) for f in obs['farms']]);budget['farms'][obs['player']]['money']+=credit
    if not _r97_budget(budget,action.get('market') or []):return action
    result=_r97_supply(budget,action)
    if result==action:return action
    assert result['market'][0]==action['market'][0]
    _,private=_r127_fields(obs,result);stock,_,_=_r97_market_stock(private['shed'],result['market']);final,_=_r97_delivery(stock,private,step%24==23)
    quantity=lambda a:sum(max(0,int(o[2])) for o in a.get('market',[]) if len(o)>2 and o[:2]==['BUY_PRODUCT','WHEAT'])
    extra=max(0,quantity(result)-quantity(action));state['credit_pending']=(step+1,final.get('WHEAT',0),extra)
    _R128_REPORT['sale_credit_orders']+=1;_R128_REPORT['sale_credit_lower_bound']+=credit;_R128_REPORT['sale_credit_grain_units']+=extra
    return result

def agent(observation,configuration=None):
    result=_R128_PARENT(observation,configuration)
    try:
        player=int(observation['player']);step=int(observation['step']);state=_R128_STATES.get(player)
        if state is None or step<=state['step']:
            state=_R128_STATES[player]={'step':-1}
            _R128_REPORT.update(service_requested_units=0,service_confirmed_units=0,service_idle_preloads=0,service_swaps_started=0,service_swaps_completed=0,service_capacity_declines=0,service_arrival_errors=0,service_swap_errors=0,sale_credit_orders=0,sale_credit_lower_bound=0,sale_credit_grain_units=0,sale_credit_confirmed_units=0,sale_credit_errors=0,service_errors=0)
        state['step']=step;pending=state.pop('credit_pending',None)
        if pending:
            if pending[0]!=step or observation['private']['shed'].get('WHEAT',0)<pending[1]:_R128_REPORT['sale_credit_errors']+=1
            else:_R128_REPORT['sale_credit_confirmed_units']+=pending[2]
        standard=configuration is None or all(configuration.get(k,v)==v for k,v in [('boardSize',10),('turnsPerDay',24),('shedCapacity',100),('maxMarketOrdersPerTurn',10),('farmHandCostMult',1)])
        if standard:result=_r128_credit_supply(observation,_r128_service(observation,result,state),state)
    except Exception:_R128_REPORT['service_errors']=_R128_REPORT.get('service_errors',0)+1
    _R128_REPORT.update(getattr(_R128_PARENT,'telemetry',{}));_R128_REPORT.update(_R97_REPORT)
    return result
agent.telemetry=_R128_REPORT
agent=globals().pop('agent')


# EXP-260: replay-supported conservative guards.
#
# 1. A PLANT blocked by a same-day weed may be recovered when the original
#    per-worker tape contains an immediate WATER and a later PASS before dawn.
#    The inserted PLANT delays that worker's commands by one position; the PASS
#    absorbs the delay, so the worker is synchronized again within the same day.
# 2. At the end of a 72-turn block, an already-confirmed mirror race may reorder
#    an all-SELL queue.  Quantities and field actions are immutable.  A bounded
#    pair-swap search accepts only a positive gain under the exact public price
#    curve and the conservative hypothesis that the rival has the same queue and
#    saleable stock.  This layer never changes buys, hires, land or input stock.

_R132_PARENT = agent
_R132_STATES = {}
_R132_REPORT = {}


def _r132_commands(action):
    return [action.get('farmer') or ['PASS'], *(action.get('hands') or [])]


def _r132_set_command(action, actor, command):
    result = copy.deepcopy(action)
    if actor == 0:
        result['farmer'] = list(command)
    else:
        hands = list(result.get('hands') or [])
        if actor - 1 >= len(hands):
            return action
        hands[actor - 1] = list(command)
        result['hands'] = hands
    return result


def _r132_standard(configuration):
    return configuration is None or all(
        configuration.get(key, value) == value
        for key, value in (
            ('boardSize', 10),
            ('turnsPerDay', 24),
            ('shedCapacity', 100),
            ('maxMarketOrdersPerTurn', 10),
            ('farmHandCostMult', 1),
        )
    )


def _r132_command_valid(observation, action, actor, command):
    view = FarmView(observation)
    if actor >= len(view.positions):
        return False
    position = view.positions[actor]
    tile = _tile_at(view.tiles, position)
    if _is_noop(command, tile, view.inv(actor), view.seeds, position, view.board):
        return False
    if command and command[0] == 'PLANT':
        crop = command[1]
        demand = sum(
            1 for current in _r132_commands(action)
            if current[:2] == ['PLANT', crop]
        )
        # Include the replacement if the parent's command was not this plant.
        parent = _r132_commands(action)[actor]
        demand += int(parent[:2] != ['PLANT', crop])
        if demand > int(view.seeds.get(crop, 0)):
            return False
    return True


def _r132_start_repair(observation, action, state):
    step = int(observation['step'])
    if step % 24 > 20 or state.get('repair'):
        return
    player = int(observation['player'])
    native = _IMPL.chassis.players.get(player)
    if not native or native.get('route') not in _IMPL.chassis.routes:
        return
    tape = _IMPL.chassis.routes[native['route']]
    if step + 2 >= len(tape):
        return
    raw = _r132_commands(tape[step])
    actual = _r132_commands(action)
    farm = observation['farms'][player]
    positions = [farm['farmer'], *farm['hands']]
    private = observation['private']
    day_end = min(len(tape), (step // 24 + 1) * 24)
    for actor, intended in enumerate(raw[:len(positions)]):
        if intended[:1] != ['PLANT'] or actor >= len(actual) or actual[actor] != ['DIG']:
            continue
        x, y = positions[actor]
        tile = farm['tiles'][y][x]
        crop = intended[1]
        if not (isinstance(tile, dict) and tile.get('kind') == 'WEED'):
            continue
        same_crop = sum(1 for command in raw if command[:2] == ['PLANT', crop])
        if int(private['seeds'].get(crop, 0)) < same_crop:
            continue
        next_commands = _r132_commands(tape[step + 1])
        if actor >= len(next_commands) or next_commands[actor] != ['WATER']:
            continue
        deadline = None
        for future_step in range(step + 1, day_end):
            future = _r132_commands(tape[future_step])
            command = future[actor] if actor < len(future) else ['PASS']
            if command == ['PASS']:
                deadline = future_step
                break
        if deadline is None:
            continue
        state['repair'] = {
            'actor': actor,
            'queue': [list(intended)],
            'next_step': step + 1,
            'deadline': deadline,
            'route': native['route'],
        }
        _R132_REPORT['weed_repair_started'] += 1
        return


def _r132_continue_repair(observation, action, state):
    repair = state.get('repair')
    if not repair:
        return action
    step = int(observation['step'])
    player = int(observation['player'])
    native = _IMPL.chassis.players.get(player) or {}
    if (step != repair['next_step'] or step > repair['deadline'] or
            native.get('route') != repair['route']):
        state.pop('repair', None)
        _R132_REPORT['weed_repair_aborted'] += 1
        return action
    actor = repair['actor']
    commands = _r132_commands(action)
    if actor >= len(commands) or not repair['queue']:
        state.pop('repair', None)
        _R132_REPORT['weed_repair_aborted'] += 1
        return action
    command = repair['queue'].pop(0)
    if not _r132_command_valid(observation, action, actor, command):
        state.pop('repair', None)
        _R132_REPORT['weed_repair_aborted'] += 1
        return action
    displaced = commands[actor]
    if displaced != ['PASS']:
        repair['queue'].append(list(displaced))
    if step >= repair['deadline'] and repair['queue']:
        state.pop('repair', None)
        _R132_REPORT['weed_repair_aborted'] += 1
        return action
    result = _r132_set_command(action, actor, command)
    repair['next_step'] = step + 1
    _R132_REPORT['weed_repair_shifted_steps'] += 1
    if command[:1] == ['PLANT']:
        _R132_REPORT['weed_repair_plants'] += 1
    if command == ['WATER']:
        _R132_REPORT['weed_repair_waters'] += 1
    if not repair['queue']:
        state.pop('repair', None)
        _R132_REPORT['weed_repair_completed'] += 1
    return result


def _r132_price_params(observation):
    params = {item: dict(values) for item, values in _R37_MARKET_PARAMS.items()}
    for item, patch in observation['market'].get('params', {}).items():
        if item in params:
            params[item].update(patch)
    return params


def _r132_mirror_revenue(observation, own_orders, rival_orders, stock):
    inventory = dict(observation['market']['inventory'])
    params = _r132_price_params(observation)
    stocks = [dict(stock), dict(stock)]
    revenue = 0
    for index in range(max(len(own_orders), len(rival_orders))):
        pair = []
        for side, orders in enumerate((own_orders, rival_orders)):
            if index >= len(orders):
                pair.append(None)
                continue
            order = orders[index]
            if not order or len(order) < 3 or order[0] != 'SELL':
                pair.append(None)
                continue
            item = order[1]
            quantity = min(
                max(0, int(order[2])),
                max(0, int(stocks[side].get(item, 0))),
            )
            pair.append([item, quantity])
        while any(current is not None and current[1] > 0 for current in pair):
            sold = []
            for side, current in enumerate(pair):
                if current is None or current[1] <= 0:
                    continue
                item = current[0]
                quote = _r37_market_price(item, inventory[item], params)
                if side == 0:
                    revenue += quote
                current[1] -= 1
                stocks[side][item] = max(0, stocks[side].get(item, 0) - 1)
                sold.append((item, quote))
            for item, quote in sold:
                if quote > 1:
                    inventory[item] += 1
    return revenue


def _r132_mirror_reorder(observation, action):
    step = int(observation['step'])
    player = int(observation['player'])
    rival = 1 - player
    orders = action.get('market') or []
    probe = _R44_PROBES.get(player) or {}
    if not (336 <= step < 696 and step % 72 == 71 and probe.get('matched')):
        return action
    if observation['farms'][player]['money'] > observation['farms'][rival]['money'] + 500:
        return action
    if _r37_similarity(observation) < 0.90 or len(orders) < 2:
        return action
    if any(
        not order or len(order) < 3 or order[0] != 'SELL' or
        order[1] not in PRODUCTS or type(order[2]) is not int or order[2] < 0
        for order in orders
    ):
        return action
    stock = projected_shed(action, FarmView(observation))
    if not any(min(order[2], max(0, int(stock.get(order[1], 0)))) > 0 for order in orders):
        return action
    rival_orders = copy.deepcopy(orders)
    current = copy.deepcopy(orders)
    baseline = _r132_mirror_revenue(observation, current, rival_orders, stock)
    score = baseline
    # At most ten orders: bounded deterministic pair-swap ascent is inexpensive.
    for _ in range(10):
        best_score = score
        best_orders = None
        for left in range(len(current)):
            for right in range(left + 1, len(current)):
                if current[left] == current[right]:
                    continue
                trial = copy.deepcopy(current)
                trial[left], trial[right] = trial[right], trial[left]
                trial_score = _r132_mirror_revenue(
                    observation, trial, rival_orders, stock
                )
                if trial_score > best_score:
                    best_score, best_orders = trial_score, trial
        if best_orders is None:
            break
        current, score = best_orders, best_score
    gain = score - baseline
    if gain < 25 or current == orders:
        return action
    _R132_REPORT['mirror_reorders'] += 1
    _R132_REPORT['mirror_modeled_gain'] += gain
    result = copy.deepcopy(action)
    result['market'] = current
    return result


def agent(observation, configuration=None):
    result = _R132_PARENT(observation, configuration)
    try:
        player = int(observation['player'])
        step = int(observation.get('step', observation['day'] * 24 + observation['hour']))
        state = _R132_STATES.get(player)
        if state is None or step <= state['step']:
            state = _R132_STATES[player] = {'step': -1}
            _R132_REPORT.update(
                weed_repair_started=0,
                weed_repair_shifted_steps=0,
                weed_repair_plants=0,
                weed_repair_waters=0,
                weed_repair_completed=0,
                weed_repair_aborted=0,
                mirror_reorders=0,
                mirror_modeled_gain=0,
                replay_guard_errors=0,
            )
        state['step'] = step
        if not _r132_standard(configuration):
            return result
        if state.get('repair'):
            result = _r132_continue_repair(observation, result, state)
        else:
            _r132_start_repair(observation, result, state)
        result = _r132_mirror_reorder(observation, result)
    except Exception:
        _R132_REPORT['replay_guard_errors'] = _R132_REPORT.get('replay_guard_errors', 0) + 1
    _R132_REPORT.update(getattr(_R132_PARENT, 'telemetry', {}))
    return result


agent.telemetry = _R132_REPORT
agent = globals().pop('agent')


# EXP-261: bounded egg-demand livestock substitution.
# Two early cow slots become geese only when both observed opening shops demand
# eggs and neither demands milk.  Every downstream mutation is confirmed from
# owned stock: purchase -> pickup -> coop build -> goose placement.  FEED, CARE
# and HARVEST are item-agnostic in the parent tape and therefore stay unchanged.

_R134_PARENT = agent
_R134_STATES = {}
_R134_REPORT = {}
_R134_EGG_SHOPS = frozenset(('BAKERY', 'BRUNCH_SPOT'))
_R134_MILK_SHOPS = frozenset(('PIZZA_SHOP', 'ICE_CREAM_SHOP', 'SMOOTHIE_SHOP'))


def _r134_animals(farm, animal):
    return sum(
        1 for row in farm['tiles'] for tile in row
        if isinstance(tile, dict) and tile.get('animal') == animal
    )


def _r134_commit(observation, action, state):
    step = int(observation['step'])
    if state.get('committed') or not 144 <= step <= 168:
        return action
    shops = list(observation['town'].get('unlocked_shops') or [])[:2]
    if (len(shops) != 2 or not all(shop in _R134_EGG_SHOPS for shop in shops) or
            any(shop in _R134_MILK_SHOPS for shop in shops)):
        return action
    orders = action.get('market') or []
    candidates = [
        index for index, order in enumerate(orders)
        if order and len(order) == 3 and order[:2] == ['BUY_ANIMAL', 'COW']
        and type(order[2]) is int and order[2] == 2
    ]
    if len(candidates) != 1 or any(
        order and order[0] == 'BUY_ANIMAL' and index != candidates[0]
        for index, order in enumerate(orders)
    ):
        return action
    player = int(observation['player'])
    farm = observation['farms'][player]
    private = observation['private']
    # Do not take over an unrelated animal already waiting in the depot.
    if int(private['shed'].get('GOOSE', 0)) or any(
        int(inventory.get('GOOSE', 0)) for inventory in private['inventories']
    ):
        return action
    result = copy.deepcopy(action)
    result['market'][candidates[0]][1] = 'GOOSE'
    state.update(
        committed=True,
        quota=2,
        initial_geese=_r134_animals(farm, 'GOOSE'),
        pending=(step + 1, int(private['shed'].get('GOOSE', 0))),
        confirmed=False,
    )
    _R134_REPORT['egg_substitution_requests'] += 1
    return result


def _r134_confirm_purchase(observation, state):
    pending = state.pop('pending', None)
    if not pending:
        return
    step, before = pending
    gained = max(0, int(observation['private']['shed'].get('GOOSE', 0)) - before)
    if int(observation['step']) == step and gained >= state['quota']:
        state['confirmed'] = True
        _R134_REPORT['egg_substitution_confirmed_units'] += state['quota']
    else:
        state['confirmed'] = False
        _R134_REPORT['egg_substitution_purchase_shortfalls'] += state['quota']


def _r134_physical(observation, action, state):
    if not state.get('confirmed'):
        return action
    step = int(observation['step'])
    player = int(observation['player'])
    farm = observation['farms'][player]
    private = observation['private']
    positions = [farm['farmer'], *farm['hands']]
    commands = _r132_commands(action)
    placed = max(0, _r134_animals(farm, 'GOOSE') - state['initial_geese'])
    if placed >= state['quota']:
        state['confirmed'] = False
        _R134_REPORT['egg_substitution_completed'] += 1
        return action
    carrying = sum(
        int(inventory.get('GOOSE', 0))
        for inventory in private['inventories']
    )
    free = max(0, state['quota'] - placed - carrying)
    depot = max(0, int(private['shed'].get('GOOSE', 0)))
    changed = False
    for actor, command in enumerate(commands[:len(private['inventories'])]):
        inventory = private['inventories'][actor]
        x, y = positions[actor]
        tile = farm['tiles'][y][x]
        if command[:2] == ['PICKUP', 'COW'] and free > 0 and depot > 0:
            quantity = max(0, int(command[2]) if len(command) > 2 else 1)
            take = min(quantity, free, depot)
            if take > 0 and _shed_adjacent((x, y), 10):
                commands[actor] = ['PICKUP', 'GOOSE', take]
                free -= take
                depot -= take
                changed = True
                _R134_REPORT['egg_substitution_pickups'] += take
        elif command == ['BUILD_PASTURE'] and int(inventory.get('GOOSE', 0)) > 0:
            if tile is None:
                commands[actor] = ['BUILD_COOP']
                changed = True
                _R134_REPORT['egg_substitution_coops'] += 1
        elif command[:2] == ['PLACE', 'COW'] and int(inventory.get('GOOSE', 0)) > 0:
            if isinstance(tile, dict) and tile.get('kind') == 'COOP' and tile.get('animal') is None:
                commands[actor] = ['PLACE', 'GOOSE']
                changed = True
                _R134_REPORT['egg_substitution_placements'] += 1
    if step > 216 and placed < state['quota']:
        state['confirmed'] = False
        _R134_REPORT['egg_substitution_aborted'] += 1
    if not changed:
        return action
    result = copy.deepcopy(action)
    result['farmer'], result['hands'] = commands[0], commands[1:]
    return result


def agent(observation, configuration=None):
    result = _R134_PARENT(observation, configuration)
    try:
        player = int(observation['player'])
        step = int(observation.get('step', observation['day'] * 24 + observation['hour']))
        state = _R134_STATES.get(player)
        if state is None or step <= state['step']:
            state = _R134_STATES[player] = {'step': -1}
            _R134_REPORT.update(
                egg_substitution_requests=0,
                egg_substitution_confirmed_units=0,
                egg_substitution_purchase_shortfalls=0,
                egg_substitution_pickups=0,
                egg_substitution_coops=0,
                egg_substitution_placements=0,
                egg_substitution_completed=0,
                egg_substitution_aborted=0,
                egg_substitution_errors=0,
            )
        state['step'] = step
        if not _r132_standard(configuration):
            return result
        _r134_confirm_purchase(observation, state)
        result = _r134_commit(observation, result, state)
        result = _r134_physical(observation, result, state)
    except Exception:
        _R134_REPORT['egg_substitution_errors'] = _R134_REPORT.get('egg_substitution_errors', 0) + 1
    _R134_REPORT.update(getattr(_R134_PARENT, 'telemetry', {}))
    return result


agent.telemetry = _R134_REPORT
agent = globals().pop('agent')
