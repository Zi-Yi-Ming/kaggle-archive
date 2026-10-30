# -*- coding: utf-8 -*-
"""GOLD SHOT v0 — Metav4 backbone + learned macro route override (day6).

NOT end-to-end PPO. Tabular/contextual bandit over chassis route_id at the
existing Metav4 decision point (step>=144 shop unlock).

Slot-B only idea. Kill gate before any submit discussion.
League training; eval vs heterogeneous panel + Metav4.
"""
from __future__ import annotations

import importlib.util
import io
import json
import random
import time
from collections import defaultdict
from contextlib import redirect_stdout
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "p79", r"D:\桌面\Kaggle\kaggriculture\_scripts\_p79_mass_gate_vs_thomas.py"
)
p79 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p79)

PROJ = Path(r"D:\桌面\Kaggle\kaggriculture")
METAV4 = PROJ / "_push_metav4_v13" / "main.py"
SHOPV7 = PROJ / "_external/p70_extracted/kaggriculture_shop_router_reactive_v7__0.py"
THOMAS = PROJ / "_push_thomas_2945" / "main.py"
ALPEREN = PROJ / "_push_alperen" / "main.py"
PIPE16 = PROJ / "_push_pipe16" / "main.py"
KAITO48 = PROJ / "_external/public_nb/kaito_v48/main.py"
POLICY_PATH = PROJ / "_research/goldshot_policy.json"
OUTJSON = PROJ / "_research/goldshot_v0.json"
PACK_DIR = PROJ / "_push_goldshot_v0"

MONEY_BUCKETS = (0, 500, 2000, 8000, 20000, 50000, 10**9)


def load_metav4_ns(tag: str = "gold_mv"):
    code = METAV4.read_text(encoding="utf-8", errors="ignore")
    ns = {"__name__": tag, "__file__": str(METAV4), "__builtins__": __builtins__}
    with redirect_stdout(io.StringIO()):
        exec(compile(code, str(METAV4), "exec"), ns)
    fn = ns.get("agent")
    n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)

    def agent(obs, configuration=None):
        return fn(obs) if n <= 1 else fn(obs, configuration)

    return agent, ns


def money_bucket(x: float) -> int:
    for i, b in enumerate(MONEY_BUCKETS):
        if x < b:
            return i
    return len(MONEY_BUCKETS) - 1


def extract_feat(obs, state):
    player = int(obs.get("player", 0))
    step = int(obs.get("step", 0))
    try:
        shops = tuple(((obs.get("town") or {}).get("unlocked_shops") or [])[:2])
    except Exception:
        shops = ()
    yarn = shops.count("YARN_STORE")
    try:
        farms = obs["farms"]
        me, rv = farms[player], farms[1 - player]
        my_m = money_bucket(float(me.get("money") or 0))
        rv_m = money_bucket(float(rv.get("money") or 0))
        hands = min(8, len(me.get("hands") or []))
        rkey = state.get("rkey")
        rk = 1 if rkey else 0
    except Exception:
        my_m = rv_m = hands = rk = 0
    return (shops, yarn, my_m, rv_m, hands, rk)


class RoutePolicy:
    def __init__(self, routes_set):
        self.routes = sorted(routes_set)
        self.q = {}  # feat -> {route: [n, mean]}
        self.default_route = 100
        self.stats = defaultdict(int)

    def key(self, feat):
        return json.dumps(list(feat), default=str)

    def choose(self, feat, default, explore=False, rng=None, eps=0.25):
        k = self.key(feat)
        table = self.q.get(k) or {}
        self.default_route = default
        if explore and rng is not None and rng.random() < eps:
            # mix: default + empirical best + random valid
            pool = [default] + [r for r in table] + self.routes[:12]
            pick = rng.choice(pool)
            self.stats["explore"] += 1
            return pick
        if table:
            # UCB-ish: prefer high mean, break ties by n
            best = max(table.items(), key=lambda kv: (kv[1][1], kv[1][0]))
            self.stats["greedy_q"] += 1
            return int(best[0])
        self.stats["default"] += 1
        return default

    def update(self, feat, route, reward, alpha=0.25):
        k = self.key(feat)
        table = self.q.setdefault(k, {})
        ent = table.get(str(route)) or table.get(route)
        if ent is None:
            table[str(route)] = [1, float(reward)]
        else:
            n, mu = ent[0], ent[1]
            table[str(route)] = [n + 1, mu + alpha * (reward - mu)]
        self.stats["updates"] += 1

    def save(self, path: Path):
        payload = {
            "routes": self.routes,
            "q": {k: {str(r): v for r, v in t.items()} for k, t in self.q.items()},
            "stats": dict(self.stats),
        }
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def load(cls, path: Path, routes_set):
        p = cls(routes_set)
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            p.q = data.get("q") or {}
            p.stats.update(data.get("stats") or {})
        return p


def install_router(ns, policy: RoutePolicy, train=False, rng=None, eps=0.25):
    orig = ns["_router"]
    routes_set = set(ns["_ROUTES"].keys())
    policy.routes = sorted(routes_set)
    log = {"overrides": [], "decisions": 0}

    def router(observation, step, state):
        route = orig(observation, step, state)
        try:
            if int(step) >= 144 and state.get("day6") and not state.get("gs_done"):
                feat = extract_feat(observation, state)
                pick = policy.choose(feat, default=int(route), explore=train, rng=rng, eps=eps)
                if pick in routes_set and pick != route:
                    state["route"] = pick
                    log["overrides"].append({"step": step, "from": route, "to": pick, "feat": str(feat)})
                state["gs_done"] = True
                log["decisions"] += 1
                state["gs_feat"] = feat
                state["gs_pick"] = int(state.get("route", route))
        except Exception:
            pass
        return state.get("route", route)

    ns["_IMPL"].chassis.router = router
    # keep module-level _router in sync if layers re-read it
    ns["_router"] = router
    return log


def call_agent(fn, obs, configuration=None):
    n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)
    return fn(obs, configuration) if n > 1 else fn(obs, configuration)


def run_game(agent_fn, opp_fn, seed, seat0=True):
    env = p79.make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    if seat0:
        env.run([agent_fn, opp_fn])
        f = env.steps[-1]
        return float(f[0]["observation"]["farms"][0]["money"]), float(f[1]["observation"]["farms"][1]["money"])
    env.run([opp_fn, agent_fn])
    f = env.steps[-1]
    return float(f[1]["observation"]["farms"][1]["money"]), float(f[0]["observation"]["farms"][0]["money"])


def reward_from(cand, opp):
    if cand > opp:
        return 1.0
    if cand < opp:
        return -1.0
    return 0.0


def train_loop(policy, ns_parent_agent, league, n_games=36, eps=0.3, seed0=100):
    rng = random.Random(42)
    rows = []
    for i in range(n_games):
        opp_name, opp_path = league[i % len(league)]
        tag = f"gs_train_{i}"
        # fresh ns each game so router install doesn't leak badly
        agent, ns = load_metav4_ns(tag)
        log = install_router(ns, policy, train=True, rng=rng, eps=eps)
        try:
            opp = p79.load_quiet(opp_path, f"o_{tag}")
        except Exception as e:
            print("opp load fail", opp_name, e, flush=True)
            continue
        seed = seed0 + i
        seat0 = (i % 2 == 0)
        try:
            cb, ob = run_game(agent, opp, seed, seat0=seat0)
        except Exception as e:
            print(f"TRAIN FAIL {opp_name} s={seed}: {e}", flush=True)
            rows.append({"i": i, "opp": opp_name, "error": str(e)[:160]})
            continue
        r = reward_from(cb, ob)
        # credit assignment: use last decision feat if any
        feat = None
        # recover from ns router log — reinstall has log closed over; parse overrides
        # simpler: re-extract is hard; store feat on policy during choose
        # update using choose-time feat saved in policy._last_feat
        feat = getattr(policy, "_last_feat", None)
        pick = getattr(policy, "_last_pick", None)
        if feat is not None and pick is not None:
            policy.update(feat, pick, r)
        rows.append({
            "i": i, "opp": opp_name, "seed": seed, "seat0": seat0,
            "cand": cb, "opp_bank": ob, "margin": cb - ob, "reward": r,
            "overrides": log["overrides"][:3],
        })
        print(f"TRAIN {i} {opp_name} s={seed} seat0={seat0} c={cb:.0f} o={ob:.0f} r={r} ov={len(log['overrides'])}", flush=True)
    return rows


# patch choose to record last feat/pick for credit
_orig_choose = RoutePolicy.choose


def choose_logged(self, feat, default, explore=False, rng=None, eps=0.25):
    pick = _orig_choose(self, feat, default, explore=explore, rng=rng, eps=eps)
    self._last_feat = feat
    self._last_pick = pick
    return pick


RoutePolicy.choose = choose_logged


def eval_policy(policy, n_eval=24, seed0=500):
    panel = [
        ("metav4", METAV4),
        ("shop_v7", SHOPV7),
        ("thomas", THOMAS),
        ("alperen", ALPEREN),
        ("pipe16", PIPE16),
    ]
    if KAITO48.exists():
        panel.append(("kaito_v48", KAITO48))
    results = {}
    all_rows = []
    for name, path in panel:
        wins = n = 0
        margins = []
        for j, seed in enumerate(range(seed0, seed0 + 4)):
            for seat0 in (True, False):
                agent, ns = load_metav4_ns(f"gs_eval_{name}_{seed}_{int(seat0)}")
                install_router(ns, policy, train=False, rng=None, eps=0)
                try:
                    opp = p79.load_quiet(path, f"oe_{name}_{seed}_{int(seat0)}")
                    cb, ob = run_game(agent, opp, seed, seat0=seat0)
                    m = cb - ob
                    win = cb > ob
                    n += 1
                    wins += int(win)
                    margins.append(m)
                    print(f"EVAL gold vs {name} s={seed} seat0={seat0} c={cb:.0f} o={ob:.0f} m={m:.0f} win={win}", flush=True)
                    all_rows.append({"opp": name, "seed": seed, "seat0": seat0, "cand": cb, "opp": ob, "margin": m, "win": win})
                except Exception as e:
                    print(f"EVAL FAIL {name} s={seed}: {e}", flush=True)
                    all_rows.append({"opp": name, "seed": seed, "seat0": seat0, "error": str(e)[:160]})
        sm = {
            "n": n, "wins": wins,
            "win_rate": round(wins / n, 3) if n else None,
            "mean_margin": round(sum(margins) / len(margins), 1) if margins else None,
        }
        results[name] = sm
        print("EVAL SUM", name, sm, flush=True)
    return results, all_rows


def baseline_metav4_eval(n_seeds=2, seed0=500):
    """Pure Metav4 vs same panel slice for comparison."""
    agent, _ = load_metav4_ns("gs_base")
    out = {}
    for name, path in [("metav4", METAV4), ("shop_v7", SHOPV7)]:
        wins = n = 0
        margins = []
        for seed in range(seed0, seed0 + n_seeds):
            for seat0 in (True, False):
                try:
                    opp = p79.load_quiet(path, f"ob_{name}_{seed}_{int(seat0)}")
                    cb, ob = run_game(agent, opp, seed, seat0=seat0)
                    m = cb - ob
                    n += 1
                    wins += int(cb > ob)
                    margins.append(m)
                    print(f"BASE metav4 vs {name} s={seed} seat0={seat0} c={cb:.0f} o={ob:.0f} m={m:.0f}", flush=True)
                except Exception as e:
                    print("BASE FAIL", name, seed, e, flush=True)
        out[name] = {"n": n, "wins": wins, "win_rate": round(wins / n, 3) if n else None,
                     "mean_margin": round(sum(margins) / len(margins), 1) if margins else None}
    return out


def kill_gate(eval_res, policy):
    mv = eval_res.get("metav4") or {}
    shop = eval_res.get("shop_v7") or {}
    wr_mv = mv.get("win_rate") or 0
    wr_sp = shop.get("win_rate") or 0
    mm = mv.get("mean_margin")
    collapses = [k for k, v in eval_res.items() if (v.get("n") or 0) >= 4 and (v.get("wins") or 0) == 0]
    # Slot B: no family collapse + some signal vs field
    field = [v for k, v in eval_res.items() if k != "metav4"]
    field_wr = None
    if field:
        tw = sum(v.get("wins") or 0 for v in field)
        tn = sum(v.get("n") or 0 for v in field)
        field_wr = round(tw / tn, 3) if tn else None
    slot_a = wr_mv >= 0.6 and wr_sp >= 0.5
    slot_b_signal = (wr_mv >= 0.45 or (mm is not None and mm > 50)) and wr_sp >= 0.4 and not collapses
    decision = "STOP_NO_SIGNAL"
    if slot_a:
        decision = "SLOT_A_CANDIDATE_NEEDS_HOLDOUT"
    elif slot_b_signal:
        decision = "SLOT_B_SIGNAL_EXPAND"
    if collapses and "shop_v7" in collapses:
        decision = "KILL_SHOP_COLLAPSE"
    return {
        "wr_mv": wr_mv, "mean_margin_mv": mm, "wr_shop": wr_sp, "field_wr": field_wr,
        "collapses": collapses, "slot_a": slot_a, "slot_b_signal": slot_b_signal,
        "decision": decision, "policy_stats": dict(policy.stats),
    }


def main():
    print("=== GOLD SHOT v0 ===", flush=True)
    payload = {"updated": time.strftime("%Y-%m-%dT%H:%M:%S"), "phase": "init"}
    agent0, ns0 = load_metav4_ns("gs_init")
    routes_set = set(ns0["_ROUTES"].keys())
    policy = RoutePolicy.load(POLICY_PATH, routes_set)
    print("policy q states", len(policy.q), "routes", len(policy.routes), flush=True)

    league = [
        ("metav4", METAV4),
        ("shop_v7", SHOPV7),
        ("thomas", THOMAS),
        ("alperen", ALPEREN),
        ("pipe16", PIPE16),
    ]

    print("\n--- TRAIN ---", flush=True)
    payload["phase"] = "train"
    train_rows = train_loop(policy, agent0, league, n_games=30, eps=0.35, seed0=100)
    policy.save(POLICY_PATH)
    payload["train"] = train_rows
    payload["policy_stats"] = dict(policy.stats)
    payload["q_states"] = len(policy.q)
    payload["updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("train done stats", dict(policy.stats), "q", len(policy.q), flush=True)

    print("\n--- BASELINE Metav4 ---", flush=True)
    base = baseline_metav4_eval(n_seeds=2, seed0=500)
    payload["baseline_metav4"] = base
    OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n--- EVAL goldshot ---", flush=True)
    payload["phase"] = "eval"
    eval_res, eval_rows = eval_policy(policy, seed0=500)
    payload["eval"] = eval_res
    payload["eval_rows"] = eval_rows
    gate = kill_gate(eval_res, policy)
    payload["kill_gate"] = gate
    payload["updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n==== GOLD SHOT KILL GATE ====", flush=True)
    print(json.dumps(gate, indent=2, ensure_ascii=False), flush=True)
    print("baseline", base, flush=True)
    print("eval", eval_res, flush=True)
    print("policy saved", POLICY_PATH, flush=True)
    print("results", OUTJSON, flush=True)


if __name__ == "__main__":
    main()
