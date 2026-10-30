# -*- coding: utf-8 -*-
"""P29: does imitation transfer ratio rise with elite corpus size?

Corpus = R2 trajectories on train seeds (diverse shop paths = diverse elite demos).
Policy = tabular BC: state bucket -> majority market action-bundle.
Workers = existing p11 stack (not learned this round).
Holdout = unseen seeds. Ratio = bank(imit) / bank(R2 same seed).
Fixed budget. No PPO. No submit.
"""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402
from p26_harness import load_r2, load_pool  # noqa: E402


# ---------- record R2 ----------
def record_r2(seed, max_steps=720):
    r2 = load_r2()
    finn = load_pool("fallow_finn")
    recs = []

    def wrap(inner):
        def agent(obs, configuration=None):
            a = inner(obs, configuration)
            step = int(obs.get("step") or 0)
            farm = (obs.get("farms") or [])[int(obs.get("player") or 0)]
            private = obs.get("private") or {}
            tiles = farm.get("tiles") or []
            plants = melon = animals = empty = 0
            for row in tiles:
                for t in row:
                    if t is None:
                        empty += 1
                    elif isinstance(t, dict):
                        if t.get("kind") == "PLANT":
                            plants += 1
                            if t.get("crop") == "MELON":
                                melon += 1
                        if t.get("animal"):
                            animals += 1
            market = a.get("market") or []
            # compact market signature
            sig = []
            for o in market:
                if not o:
                    continue
                if o[0] == "HIRE":
                    sig.append("HIRE")
                elif o[0] == "SELL" and len(o) >= 2:
                    sig.append("SELL:" + str(o[1]))
                elif o[0] in ("BUY_ANIMAL", "BUY_SEED", "BUY_PRODUCT") and len(o) >= 2:
                    sig.append(o[0] + ":" + str(o[1]))
                else:
                    sig.append(o[0])
            recs.append({
                "step": step, "day": step // 24, "hour": step % 24,
                "money": float(farm.get("money") or 0),
                "hands": len(farm.get("hands") or []),
                "n_land": len(farm.get("unlocked_quadrants") or []),
                "plants": plants, "melon": melon, "animals": animals, "empty": empty,
                "n_shops": len((obs.get("town") or {}).get("unlocked_shops") or []),
                "sig": "|".join(sig),
            })
            return a
        return agent

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = max_steps
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    env.run([wrap(r2), finn])
    f = env.steps[-1]
    bank = float(f[0]["observation"]["farms"][0]["money"])
    return recs, bank


def state_bucket(r):
    """Coarse tabular state key."""
    money = r["money"]
    mb = 0 if money < 200 else (1 if money < 1000 else (2 if money < 5000 else 3))
    ab = min(r["animals"], 5)
    hb = min(r["hands"], 4)
    return (r["day"], r["hour"] // 6, mb, ab, hb)


def train_bc(corpus):
    """corpus: list of recs from multiple seeds. Return bucket->sig majority."""
    votes = defaultdict(Counter)
    for r in corpus:
        votes[state_bucket(r)][r["sig"]] += 1
    policy = {k: c.most_common(1)[0][0] for k, c in votes.items()}
    return policy


def parse_sig(sig):
    """sig string -> market orders list."""
    if not sig:
        return []
    orders = []
    for part in sig.split("|"):
        if not part:
            continue
        if part == "HIRE":
            orders.append(["HIRE"])
        elif part.startswith("SELL:"):
            orders.append(["SELL", part.split(":", 1)[1], 99])  # qty filled later
        elif part.startswith("BUY_ANIMAL:"):
            orders.append(["BUY_ANIMAL", part.split(":", 1)[1], 1])
        elif part.startswith("BUY_SEED:"):
            orders.append(["BUY_SEED", part.split(":", 1)[1], 4])
        elif part.startswith("BUY_PRODUCT:"):
            orders.append(["BUY_PRODUCT", part.split(":", 1)[1], 4])
        elif part in ("BUY_LAND",):
            orders.append(["BUY_LAND"])
    return orders


class TabularBCAgent:
    def __init__(self, policy):
        self.policy = policy
        from p11_planner import planner as pmod
        self._pmod = pmod
        self._planner = None

    def act(self, observation, configuration=None):
        obs = observation or {}
        if self._planner is None:
            self._planner = self._pmod.StrategicPlanner()
        base = self._planner.act(obs)
        step = int(obs.get("step") or 0)
        player = int(obs.get("player") or 0)
        farm = (obs.get("farms") or [])[player]
        private = obs.get("private") or {}
        tiles = farm.get("tiles") or []
        plants = melon = animals = empty = 0
        for row in tiles:
            for t in row:
                if t is None:
                    empty += 1
                elif isinstance(t, dict):
                    if t.get("kind") == "PLANT":
                        plants += 1
                        if t.get("crop") == "MELON":
                            melon += 1
                    if t.get("animal"):
                        animals += 1
        r = {
            "day": step // 24, "hour": step % 24,
            "money": float(farm.get("money") or 0),
            "hands": len(farm.get("hands") or []),
            "plants": plants, "melon": melon, "animals": animals, "empty": empty,
        }
        key = state_bucket(r)
        sig = self.policy.get(key, "")
        market = parse_sig(sig)
        # fix SELL qty from shed
        shed = dict(private.get("shed") or {})
        fixed = []
        for o in market:
            if o[0] == "SELL":
                q = int(shed.get(o[1]) or 0)
                if q > 0:
                    fixed.append(["SELL", o[1], q])
            else:
                fixed.append(o)
        action = dict(base or {})
        action["market"] = (fixed + list(action.get("market") or []))[:10]
        from p10_executor.validators import sanitize_action
        return sanitize_action(
            action, shed=shed, money=float(farm.get("money") or 0),
            prices=dict((obs.get("market") or {}).get("prices") or {}),
        )


def run_agent_vs_finn(agent_fn, seed):
    finn = load_pool("fallow_finn")
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    env.run([agent_fn, finn])
    f = env.steps[-1]
    return float(f[0]["observation"]["farms"][0]["money"])


def main():
    TRAIN = (1, 2, 3, 4, 5, 6, 7, 8)
    HOLDOUT = (11, 12, 13)
    # optional valid unused for first pass (fixed hyperparams)

    # record corpus
    corpus_by_seed = {}
    banks_train = {}
    for seed in TRAIN:
        recs, bank = record_r2(seed)
        corpus_by_seed[seed] = recs
        banks_train[seed] = bank
        print(f"recorded train seed{seed} R2={bank:.0f} n={len(recs)}", flush=True)

    # R2 holdout reference
    r2_hold = {}
    for seed in HOLDOUT:
        _, bank = record_r2(seed)
        r2_hold[seed] = bank
        print(f"holdout seed{seed} R2={bank:.0f}", flush=True)

    # corpus sizes
    sizes = [1, 2, 4, 8]
    results = []
    for n in sizes:
        seeds_used = TRAIN[:n]
        corpus = []
        for s in seeds_used:
            corpus.extend(corpus_by_seed[s])
        policy = train_bc(corpus)
        print(f"\n=== C{n} buckets={len(policy)} ===", flush=True)
        ratios = []
        for seed in HOLDOUT:
            # reset B flags
            import p13_1_melon, p13_3_water, p14_1_on, p14_2_on, p16_branch, p17_1_library, p18_selector
            p13_1_melon.set_enabled(False)
            p13_3_water.set_enabled(True)
            p14_1_on.set_enabled(True)
            p14_2_on.set_enabled(False)
            p16_branch.set_branch_mode("off")
            p17_1_library.set_enabled(False)
            p18_selector.set_selector("S0")
            from p11_planner import planner as pmod
            pmod._PLANNER = None
            agent = TabularBCAgent(policy)
            bank = run_agent_vs_finn(agent.act, seed)
            ratio = bank / r2_hold[seed] if r2_hold[seed] else 0
            ratios.append(ratio)
            print(f"  holdout s{seed}: imit={bank:.0f} r2={r2_hold[seed]:.0f} ratio={ratio:.2%}", flush=True)
        mean_r = sum(ratios) / len(ratios)
        results.append({"corpus_n": n, "mean_ratio": mean_r,
                        "min_ratio": min(ratios), "max_ratio": max(ratios),
                        "n_buckets": len(policy)})
        print(f"  C{n} mean_ratio={mean_r:.2%}", flush=True)

    out = ROOT / "p29_corpus_scaling.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        w.writeheader()
        w.writerows(results)
    print("\n=== SCALING ===")
    for r in results:
        print(f"  C{r['corpus_n']}: ratio={r['mean_ratio']:.2%} buckets={r['n_buckets']}")
    print("wrote", out.name)


if __name__ == "__main__":
    main()
