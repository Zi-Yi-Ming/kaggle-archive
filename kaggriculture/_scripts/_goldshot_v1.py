# -*- coding: utf-8 -*-
"""GOLD SHOT v1 — multi-window macro policy on Metav4 executor.

NOT community-scale PPO. Throughput measured ~126 env-steps/s (Python engine)
vs community ~10k SPS — 100M+ steps NOT feasible this week.

Within-budget v1:
- Decision windows: day6/9/12/15/18/21 (before day27 terminal lock)
- Cash-dominant reward + league training
- Slot-B eval; Metav4 stays Slot A
"""
from __future__ import annotations

import importlib.util
import io
import json
import random
import sys
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
POLICY_PATH = PROJ / "_research/goldshot_v1_policy.json"
OUTJSON = PROJ / "_research/goldshot_v1.json"

# day*24: d6=144 (Metav4 shop unlock), then every 3 days; stop before d27=648
WINDOWS = (144, 216, 288, 360, 432, 504)
MONEY_B = (0, 800, 3000, 10000, 30000, 80000, 10**9)
HANDS_B = (0, 2, 4, 6, 8, 99)
PLANT_B = (0, 5, 15, 30, 50, 200)
ANIMAL_B = (0, 2, 5, 10, 20, 99)


def load_metav4_ns(tag: str):
    code = METAV4.read_text(encoding="utf-8", errors="ignore")
    ns = {"__name__": tag, "__file__": str(METAV4), "__builtins__": __builtins__}
    with redirect_stdout(io.StringIO()):
        exec(compile(code, str(METAV4), "exec"), ns)
    fn = ns.get("agent")
    n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)

    def agent(obs, configuration=None):
        return fn(obs) if n <= 1 else fn(obs, configuration)

    return agent, ns


def bucket(x, edges):
    for i, b in enumerate(edges):
        if x < b:
            return i
    return len(edges) - 1


def farm_sig(f):
    plants = animals = 0
    crops = {}
    for row in f.get("tiles") or []:
        for t in row:
            if not isinstance(t, dict):
                continue
            if t.get("crop"):
                plants += 1
                crops[t["crop"]] = crops.get(t["crop"], 0) + 1
            if t.get("animal"):
                animals += 1
    return plants, animals, crops


def extract_feat(obs, state, window):
    player = int(obs.get("player", 0))
    try:
        shops = tuple(((obs.get("town") or {}).get("unlocked_shops") or [])[:2])
    except Exception:
        shops = ()
    yarn = shops.count("YARN_STORE")
    try:
        farms = obs["farms"]
        me, rv = farms[player], farms[1 - player]
        my_m = bucket(float(me.get("money") or 0), MONEY_B)
        rv_m = bucket(float(rv.get("money") or 0), MONEY_B)
        hands = bucket(len(me.get("hands") or []), HANDS_B)
        plants, animals, _ = farm_sig(me)
        rp, ra, _ = farm_sig(rv)
        pb = bucket(plants, PLANT_B)
        ab = bucket(animals, ANIMAL_B)
        rpb = bucket(rp, PLANT_B)
        rab = bucket(ra, ANIMAL_B)
        rkey = 1 if state.get("rkey") else 0
    except Exception:
        my_m = rv_m = hands = pb = ab = rpb = rab = rkey = 0
    inv = (obs.get("market") or {}).get("inventory") or {}
    px = (obs.get("market") or {}).get("prices") or {}
    wheat_inv = bucket(int(inv.get("WHEAT", 10000) or 10000), (9000, 9800, 10000, 10200, 11000, 10**9))
    milk_px = bucket(int(px.get("MILK", 0) or 0), (100, 140, 160, 180, 220, 10**9))
    widx = WINDOWS.index(window) if window in WINDOWS else 9
    return (shops, yarn, widx, my_m, rv_m, hands, pb, ab, rpb, rab, rkey, wheat_inv, milk_px)


class MacroPolicy:
    def __init__(self):
        self.q = {}
        self.stats = defaultdict(int)
        self._last = None

    @staticmethod
    def k(feat):
        return "|".join(str(x) for x in feat)

    def choose(self, feat, default, routes, explore=False, rng=None, eps=0.25):
        key = self.k(feat)
        table = self.q.get(key) or {}
        if explore and rng is not None and rng.random() < eps:
            pool = [default] + list(table.keys()) + list(routes)[:15]
            pick = int(rng.choice(pool))
            self.stats["explore"] += 1
        elif table:
            pick = int(max(table.items(), key=lambda kv: (kv[1][1], kv[1][0]))[0])
            self.stats["greedy"] += 1
        else:
            pick = int(default)
            self.stats["default"] += 1
        if pick not in routes:
            pick = int(default)
        self._last = (key, pick)
        return pick

    def update(self, reward, alpha=0.3):
        if not self._last:
            return
        key, pick = self._last
        table = self.q.setdefault(key, {})
        ent = table.get(str(pick))
        if ent is None:
            table[str(pick)] = [1, float(reward)]
        else:
            n, mu = ent
            table[str(pick)] = [n + 1, mu + alpha * (float(reward) - mu)]
        self.stats["updates"] += 1

    def save(self, path: Path):
        path.write_text(
            json.dumps({"q": self.q, "stats": dict(self.stats)}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path: Path):
        p = cls()
        if path.exists():
            try:
                d = json.loads(path.read_text(encoding="utf-8"))
                p.q = d.get("q") or {}
                p.stats.update(d.get("stats") or {})
            except Exception:
                pass
        return p


def install_router(ns, policy: MacroPolicy, train=False, rng=None, eps=0.25):
    orig = ns["_router"]
    routes = set(ns["_ROUTES"].keys())
    log = {"overrides": [], "windows_hit": []}

    def router(observation, step, state):
        route = orig(observation, step, state)
        try:
            step = int(step)
            if step < 648:
                for w in WINDOWS:
                    flag = f"gs_w{w}"
                    if step >= w and not state.get(flag):
                        state[flag] = True
                        feat = extract_feat(observation, state, w)
                        pick = policy.choose(
                            feat,
                            default=int(state.get("route", route)),
                            routes=routes,
                            explore=train,
                            rng=rng,
                            eps=eps,
                        )
                        old = int(state.get("route", route))
                        if pick != old:
                            state["route"] = pick
                            log["overrides"].append({"step": step, "window": w, "from": old, "to": pick})
                        log["windows_hit"].append(w)
        except Exception:
            pass
        return state.get("route", route)

    ns["_IMPL"].chassis.router = router
    ns["_router"] = router
    return log


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


def shaped_reward(cb, ob):
    """Cash-dominant: 0.7 * relative cash + 0.3 * WDL sign."""
    margin = (cb - ob) / 20000.0
    cash = max(-1.0, min(1.0, margin))
    wdl = 1.0 if cb > ob else (-1.0 if cb < ob else 0.0)
    return 0.7 * cash + 0.3 * wdl


def train(policy, league, n_games, eps=0.35, seed0=200):
    rng = random.Random(7)
    rows = []
    t0 = time.time()
    for i in range(n_games):
        opp_name, opp_path = league[i % len(league)]
        tag = f"gsv1_tr_{i}"
        agent, ns = load_metav4_ns(tag)
        install_router(ns, policy, train=True, rng=rng, eps=eps)
        try:
            opp = p79.load_quiet(opp_path, f"o_{tag}")
        except Exception as e:
            print("opp fail", opp_name, e, flush=True)
            continue
        seed = seed0 + i
        seat0 = i % 2 == 0
        t_g = time.time()
        try:
            cb, ob = run_game(agent, opp, seed, seat0=seat0)
        except Exception as e:
            print(f"TRAIN FAIL {opp_name} s={seed}: {e}", flush=True)
            rows.append({"i": i, "opp": opp_name, "seed": seed, "error": str(e)[:160]})
            continue
        r = shaped_reward(cb, ob)
        # credit last window decision
        policy.update(r)
        dt = time.time() - t_g
        print(
            f"TRAIN {i:03d} {opp_name:10s} s={seed} seat0={int(seat0)} "
            f"c={cb:.0f} o={ob:.0f} m={cb-ob:.0f} r={r:.3f} ov={len(policy.stats) and dt:.1f}s",
            flush=True,
        )
        rows.append({
            "i": i, "opp": opp_name, "seed": seed, "seat0": seat0,
            "cand": cb, "opp_bank": ob, "margin": cb - ob, "reward": r, "sec": dt,
        })
    elapsed = time.time() - t0
    return rows, elapsed


def eval_panel(policy, seed0=800):
    panel = [
        ("metav4", METAV4),
        ("shop_v7", SHOPV7),
        ("thomas", THOMAS),
        ("alperen", ALPEREN),
        ("pipe16", PIPE16),
    ]
    if KAITO48.exists():
        panel.append(("kaito_v48", KAITO48))
    results, all_rows = {}, []
    for name, path in panel:
        wins = n = 0
        margins = []
        for seed in range(seed0, seed0 + 3):
            for seat0 in (True, False):
                agent, ns = load_metav4_ns(f"gsv1_ev_{name}_{seed}_{int(seat0)}")
                install_router(ns, policy, train=False)
                try:
                    opp = p79.load_quiet(path, f"oe_{name}_{seed}_{int(seat0)}")
                    cb, ob = run_game(agent, opp, seed, seat0=seat0)
                    m = cb - ob
                    n += 1
                    wins += int(cb > ob)
                    margins.append(m)
                    print(f"EVAL vs {name} s={seed} seat0={int(seat0)} c={cb:.0f} o={ob:.0f} m={m:.0f}", flush=True)
                    all_rows.append({"opp": name, "seed": seed, "seat0": seat0, "cand": cb, "opp": ob, "margin": m, "win": cb > ob})
                except Exception as e:
                    print(f"EVAL FAIL {name} s={seed}: {e}", flush=True)
                    all_rows.append({"opp": name, "seed": seed, "seat0": seat0, "error": str(e)[:160]})
        results[name] = {
            "n": n, "wins": wins,
            "win_rate": round(wins / n, 3) if n else None,
            "mean_margin": round(sum(margins) / len(margins), 1) if margins else None,
        }
        print("EVAL SUM", name, results[name], flush=True)
    return results, all_rows


def kill_gate(eval_res, policy, train_elapsed, n_train):
    mv = eval_res.get("metav4") or {}
    shop = eval_res.get("shop_v7") or {}
    wr_mv = mv.get("win_rate") or 0
    mm = mv.get("mean_margin")
    wr_sp = shop.get("win_rate") or 0
    collapses = [k for k, v in eval_res.items() if (v.get("n") or 0) >= 4 and (v.get("wins") or 0) == 0]
    field = [v for k, v in eval_res.items() if k != "metav4"]
    tw = sum(v.get("wins") or 0 for v in field)
    tn = sum(v.get("n") or 0 for v in field)
    field_wr = round(tw / tn, 3) if tn else None
    games_per_h = (n_train / train_elapsed * 3600) if train_elapsed > 0 else 0
    sps = (n_train * 720 / train_elapsed) if train_elapsed > 0 else 0
    throughput_gate = "FAIL_COMMUNITY_SCALE"  # ~126 SPS << 10k
    if sps >= 2000:
        throughput_gate = "MAYBE_COMMUNITY_SCALE"
    slot_a = wr_mv >= 0.6 and wr_sp >= 0.5
    slot_b = (wr_mv >= 0.45 or (mm is not None and mm > 80)) and wr_sp >= 0.35 and "shop_v7" not in collapses
    if "shop_v7" in collapses:
        decision = "KILL_SHOP_COLLAPSE"
    elif slot_a:
        decision = "SLOT_A_NEEDS_HOLDOUT"
    elif slot_b:
        decision = "SLOT_B_SIGNAL"
    else:
        decision = "STOP_NO_SIGNAL"
    return {
        "throughput_gate": throughput_gate,
        "measured_sps_approx": round(sps, 1),
        "games_per_hour": round(games_per_h, 1),
        "wr_mv": wr_mv,
        "mean_margin_mv": mm,
        "wr_shop": wr_sp,
        "field_wr": field_wr,
        "collapses": collapses,
        "slot_a": slot_a,
        "slot_b_signal": slot_b,
        "decision": decision,
        "policy_stats": dict(policy.stats),
        "q_states": len(policy.q),
        "note": "v1 is within-budget multi-window macro bandit, NOT 100M-step JAX RL",
    }


def main():
    n_train = int(sys.argv[1]) if len(sys.argv) > 1 else 90
    print("=== GOLD SHOT v1 ===", flush=True)
    print("windows", WINDOWS, "train_games", n_train, flush=True)
    _, ns0 = load_metav4_ns("gsv1_init")
    routes = set(ns0["_ROUTES"].keys())
    policy = MacroPolicy.load(POLICY_PATH)
    print("loaded q", len(policy.q), flush=True)

    league = [
        ("metav4", METAV4),
        ("shop_v7", SHOPV7),
        ("thomas", THOMAS),
        ("alperen", ALPEREN),
        ("pipe16", PIPE16),
    ]
    if KAITO48.exists():
        league.append(("kaito_v48", KAITO48))

    print("\n--- TRAIN ---", flush=True)
    rows, elapsed = train(policy, league, n_games=n_train, eps=0.35, seed0=200)
    policy.save(POLICY_PATH)
    print(f"train done games={len(rows)} elapsed_s={elapsed:.1f}", flush=True)

    print("\n--- EVAL ---", flush=True)
    eval_res, eval_rows = eval_panel(policy, seed0=800)
    gate = kill_gate(eval_res, policy, elapsed, max(1, len(rows)))
    payload = {
        "updated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "n_train": n_train,
        "train_elapsed_s": elapsed,
        "train_rows": rows,
        "eval": eval_res,
        "eval_rows": eval_rows,
        "kill_gate": gate,
        "production": "Metav4 56390446 HOLD; Thomas slot B not replaced unless SIGNAL",
    }
    OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n==== KILL GATE v1 ====", flush=True)
    print(json.dumps(gate, indent=2, ensure_ascii=False), flush=True)
    print("eval", json.dumps(eval_res, indent=2), flush=True)
    print("saved", OUTJSON, POLICY_PATH, flush=True)


if __name__ == "__main__":
    main()
