# -*- coding: utf-8 -*-
"""P39 harness: pin seed, never wrap finn, record/replay worker and market tapes."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

ELITES = {
    "R2": ROOT / "_push_medal" / "main.py",
    "kaito_v27": ROOT / "_external" / "public_nb" / "kaito_v27" / "main.py",
    "qeinstein": ROOT / "_external" / "git" / "qeinstein" / "dist" / "sub-009-moev2" / "main.py",
    "rayk_rank": ROOT / "_external" / "public_nb" / "rayk_rank" / "main.py",
}


def load_mod(path, name):
    spec = importlib.util.spec_from_file_location(name, str(path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def get_agent(mod):
    if hasattr(mod, "agent"):
        return mod.agent
    return mod.build_agent({})


def load_finn():
    return load_mod(ROOT / "reference_agents" / "fallow_finn.py", "finn_p39").agent


def load_elite(name):
    return get_agent(load_mod(ELITES[name], f"p39_{name}_{id(object())}"))


def wrap_candidate(inner, keys=None, tape=None):
    """Wrap OUR agent only. Match arity. Optionally record full actions."""
    n = getattr(getattr(inner, "__code__", None), "co_argcount", 2)

    def _rec(a):
        if keys is not None:
            keys.append(json.dumps(
                {"m": a.get("market"), "f": a.get("farmer"), "h": a.get("hands")},
                sort_keys=True, default=str,
            ))
        if tape is not None:
            step = None
            tape.append({
                "farmer": a.get("farmer"),
                "hands": a.get("hands"),
                "market": a.get("market"),
            })

    if n <= 1:
        def agent(obs):
            a = inner(obs)
            _rec(a)
            return a
    else:
        def agent(obs, configuration=None):
            a = inner(obs, configuration)
            _rec(a)
            return a
    return agent


def run_vs_finn(agent_fn, seed, collect_keys=False, collect_tape=False):
    """Pinned. finn NEVER wrapped. Returns bank, keys, tape, hash."""
    finn = load_finn()
    keys = []
    tape = []
    play = wrap_candidate(agent_fn, keys if collect_keys else None,
                          tape if collect_tape else None)
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    env.run([play, finn])
    f = env.steps[-1]
    bank = float(f[0]["observation"]["farms"][0]["money"])
    shops = []
    try:
        shops = list((f[0]["observation"].get("town") or {}).get("unlocked_shops") or [])
    except Exception:
        pass
    h = hashlib.md5("\n".join(keys).encode()).hexdigest()[:16] if keys else ""
    return {
        "bank": bank,
        "keys": keys,
        "tape": tape,
        "hash": h,
        "shops": shops,
        "seed": int(seed),
    }


def record_elite_tapes(names, seed=1):
    """Run each elite once, return {name: tape[step] = {farmer,hands,market}}."""
    out = {}
    for name in names:
        fn = load_elite(name)
        r = run_vs_finn(fn, seed, collect_keys=True, collect_tape=True)
        out[name] = {
            "bank": r["bank"],
            "hash": r["hash"],
            "tape": r["tape"],
            "keys": r["keys"],
            "shops": r["shops"],
        }
        print(f"recorded {name}: bank={r['bank']:.0f} steps={len(r['tape'])} hash={r['hash']}", flush=True)
    return out


# ---------------------------------------------------------------------------
# Weak / fixed half-programs for crossing
# ---------------------------------------------------------------------------

PRODUCTS = (
    "WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON",
    "EGG", "MILK", "WOOL", "FERTILIZER",
)
SEED_COST = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80}
ANIMAL_COST = {"COW": 400, "SHEEP": 500, "GOOSE": 300}


def weak_market_agent(observation, configuration=None):
    """Minimal viable market: hire, land, buy seeds/animals, sell all at dusk."""
    obs = observation or {}
    step = int(obs.get("step") or 0)
    day, hour = step // 24, step % 24
    player = int(obs.get("player") or 0)
    farm = (obs.get("farms") or [player])[player] if obs.get("farms") else {}
    private = obs.get("private") or {}
    shed = dict(private.get("shed") or {})
    prices = dict((obs.get("market") or {}).get("prices") or {})
    money = float(farm.get("money") or 0)
    hires_today = int(farm.get("hires_today") or 0)
    n_land = len(farm.get("unlocked_quadrants") or [])
    tiles = farm.get("tiles") or []
    empty = sum(1 for row in tiles for t in row if t is None)
    live = {"COW": 0, "SHEEP": 0, "GOOSE": 0}
    for row in tiles:
        for t in row:
            if isinstance(t, dict) and t.get("animal") in live:
                live[t["animal"]] += 1

    market = []
    cash = money

    def add(o):
        if len(market) >= 10:
            return False
        market.append(o)
        return True

    def fib(n):
        a, b = 1, 1
        for _ in range(max(0, n)):
            a, b = b, a + b
        return a

    if day == 0 and hour == 0:
        for crop, q, cost in (("MELON", 12, 80), ("WHEAT", 7, 10)):
            if cash >= cost * q + 20 and add(["BUY_SEED", crop, q]):
                cash -= cost * q
        for a, q in (("COW", 2), ("SHEEP", 2)):
            if cash >= ANIMAL_COST[a] * q + 20 and add(["BUY_ANIMAL", a, q]):
                cash -= ANIMAL_COST[a] * q

    if hour == 0 and day in (6, 11, 18) and n_land < 4 and cash >= 1300:
        if add(["BUY_LAND"]):
            cash -= 1000

    if hour == 0 and day >= 1:
        for a, target in (("COW", 8), ("SHEEP", 8)):
            gap = target - (live[a] + int(shed.get(a) or 0))
            can = min(max(0, gap), 2, int(max(0.0, cash - 100) // ANIMAL_COST[a]))
            for _ in range(can):
                if add(["BUY_ANIMAL", a, 1]):
                    cash -= ANIMAL_COST[a]

    if hour in (0, 6, 12) and empty > 1 and cash >= 60:
        for crop, cost, qmax in (("MELON", 80, 3), ("STRAWBERRY", 100, 2), ("WHEAT", 10, 5)):
            if day >= 10 and crop == "MELON":
                continue
            q = min(empty, qmax, int(max(0, cash - 30) // cost))
            if q > 0 and add(["BUY_SEED", crop, q]):
                cash -= cost * q
                empty -= q

    if hour == 0:
        room = max(0, 9 - len(market))
        target = 5 if day <= 2 else (8 if day <= 9 else 10)
        n = 0
        while n < target and n < room:
            cost = fib(hires_today + n)
            if cash < cost + 5 or not add(["HIRE"]):
                break
            cash -= cost
            n += 1

    if hour in (18, 20, 21) or day >= 29:
        hold = 0 if day >= 29 else 8
        for item in PRODUCTS:
            q = int(shed.get(item) or 0)
            if item == "WHEAT":
                q = max(0, q - hold)
            if q > 0:
                add(["SELL", item, q])

    # pass-through workers: stay home
    return {"farmer": ["PASS"], "hands": [], "market": market}


def weak_worker_from_p11(observation, configuration=None):
    """p11 full agent as the 'weak but real' worker+market substrate."""
    if not hasattr(weak_worker_from_p11, "_pl"):
        from p11_planner import planner as pmod
        weak_worker_from_p11._pl = pmod.StrategicPlanner()
    return weak_worker_from_p11._pl.act(observation)


def tape_worker_agent(tape):
    """Replay recorded worker commands; use weak market."""
    def agent(observation, configuration=None):
        obs = observation or {}
        step = int(obs.get("step") or 0)
        step = max(0, min(len(tape) - 1, step))
        w = tape[step] or {}
        m = weak_market_agent(obs, configuration)
        return {
            "farmer": w.get("farmer") or ["PASS"],
            "hands": w.get("hands") or [],
            "market": m.get("market") or [],
        }
    return agent


def tape_market_agent(tape):
    """Replay recorded market orders; weak/pass workers."""
    def agent(observation, configuration=None):
        obs = observation or {}
        step = int(obs.get("step") or 0)
        step = max(0, min(len(tape) - 1, step))
        w = tape[step] or {}
        return {
            "farmer": ["PASS"],
            "hands": [],
            "market": w.get("market") or [],
        }
    return agent


def tape_market_p11_worker_agent(tape):
    """Elite market + p11 workers (coupled test)."""
    if not hasattr(tape_market_p11_worker_agent, "_pl"):
        from p11_planner import planner as pmod
        tape_market_p11_worker_agent._pl = pmod.StrategicPlanner()
    pl = tape_market_p11_worker_agent._pl

    def agent(observation, configuration=None):
        obs = observation or {}
        step = int(obs.get("step") or 0)
        step = max(0, min(len(tape) - 1, step))
        w = tape[step] or {}
        base = pl.act(obs) or {}
        return {
            "farmer": base.get("farmer") or ["PASS"],
            "hands": base.get("hands") or [],
            "market": w.get("market") or [],
        }
    return agent


def hybrid_worker_tape_market_program(tape, market_fn):
    """Arbitrary market_fn(obs)->market list + elite worker tape."""
    def agent(observation, configuration=None):
        obs = observation or {}
        step = int(obs.get("step") or 0)
        step = max(0, min(len(tape) - 1, step))
        w = tape[step] or {}
        mk = market_fn(obs) or []
        return {
            "farmer": w.get("farmer") or ["PASS"],
            "hands": w.get("hands") or [],
            "market": mk[:10],
        }
    return agent
