# -*- coding: utf-8 -*-
"""StrategicPlanner: live resource targets → production program → validated action."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from p10_executor.primitives import repair_weeds, liquidate as p10_liquidate
from p10_executor.validators import sanitize_action
from p10_executor.primitives import DayState

from .production import build_market, worker_command, beside_shed
from .targets import infer_targets


class StrategicPlanner:
    def __init__(self):
        self.day_state = DayState()
        self.last_targets = None
        self.intent_log = []
        self.player_mem = {}

    def reset(self):
        self.day_state = DayState()
        self.last_targets = None
        self.intent_log = []

    def act(self, observation):
        obs = observation or {}
        step = int(obs.get("step") or 0)
        player = int(obs.get("player") or 0)
        day = step // 24
        hour = step % 24

        # per-player weed state (R2 style)
        mem = self.player_mem.get(player)
        if mem is None or step <= mem.get("last_step", -1):
            mem = {"state": DayState(), "last_step": -1}
            self.player_mem[player] = mem
        mem["last_step"] = step
        day_state = mem["state"]

        farms = obs.get("farms") or []
        farm = farms[player] if player < len(farms) else {}
        private = obs.get("private") or {}
        shed = dict(private.get("shed") or {})
        seeds = dict(private.get("seeds") or {})
        inventories = list(private.get("inventories") or [])
        prices = dict((obs.get("market") or {}).get("prices") or {})
        money = float(farm.get("money") or 0)
        tiles = farm.get("tiles") or []
        positions = [farm.get("farmer") or [4, 4], *(farm.get("hands") or [])]
        hires_today = int(farm.get("hires_today") or 0)
        hands = farm.get("hands") or []

        # Terminal liquidate via p10
        if step >= LAST_STEP:
            action = p10_liquidate(positions, shed, inventories, prices, beside_shed)
            return sanitize_action(action, shed=shed, money=money, prices=prices)

        targets = infer_targets(obs, day, hour, step)
        self.last_targets = targets
        self.intent_log.append((step, day, targets.priority, dict(targets.buy_animals),
                                targets.buy_land, targets.hire_n))

        market = build_market(
            targets, shed, seeds, money, prices, day, hour, step,
            hires_today, len(hands),
        )
        # P12 B3: wheat feed top-up when animals hungry
        try:
            from p12_primitives.animal_care import scan_animals, wheat_topup_orders
            hungry, _, _, _ = scan_animals(tiles)
            extra = wheat_topup_orders(shed, prices, money, len(hungry))
            if extra:
                existing = {tuple(o[:2]) for o in market if o}
                for o in extra:
                    if tuple(o[:2]) not in existing and len(market) < 10:
                        market.append(o)
        except Exception:
            pass

        # Worker commands
        farmer_cmd = ["PASS"]
        hands_cmds = []
        n_workers = 1 + len(hands)
        plant_budget = {c: int(seeds.get(c) or 0) for c in seeds}
        for actor in range(n_workers):
            cmd = worker_command(
                obs, actor, tiles, positions, inventories, shed, seeds, day, step,
            )
            # Engine drops ALL plants for a crop if requests exceed seeds
            if cmd and cmd[0] == "PLANT" and len(cmd) >= 2:
                crop = cmd[1]
                if plant_budget.get(crop, 0) <= 0:
                    # fallback: build if animals wait, else pass
                    if any(int(shed.get(a) or 0) > 0 for a in ("GOOSE", "COW", "SHEEP")):
                        cmd = ["BUILD_COOP"] if int(shed.get("GOOSE") or 0) else ["BUILD_PASTURE"]
                    else:
                        cmd = ["PASS"]
                else:
                    plant_budget[crop] -= 1
            if actor == 0:
                farmer_cmd = cmd
            else:
                hands_cmds.append(cmd)

        action = {"farmer": farmer_cmd, "hands": hands_cmds, "market": market}

        # P10 weed repair
        action = repair_weeds(action, positions, tiles, day_state, step)
        action = sanitize_action(action, shed=shed, money=money, prices=prices)
        return action


# module-level singleton for kaggle agent API
_PLANNER = None
LAST_STEP = 718


def agent(observation, configuration=None):
    global _PLANNER
    if _PLANNER is None:
        _PLANNER = StrategicPlanner()
    return _PLANNER.act(observation)


def debug_state():
    if _PLANNER is None:
        return {}
    t = _PLANNER.last_targets
    return {
        "priority": getattr(t, "priority", None),
        "hire_n": getattr(t, "hire_n", None),
        "buy_animals": dict(getattr(t, "buy_animals", {}) or {}),
        "buy_land": getattr(t, "buy_land", None),
        "n_intents": len(_PLANNER.intent_log),
    }
