# -*- coding: utf-8 -*-
"""P32b: single/multi/leave-one-out BC + conditioned vs unconditioned."""
from __future__ import annotations

import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
CORPUS = ROOT / "elite_corpus"
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402
from p26_harness import load_pool  # noqa: E402

POLICIES = ("R2", "kaito_v27", "qeinstein", "rayk_rank")
TRAIN = (1, 2, 3, 4)
HOLDOUT = (11, 12, 13)


def load_corpus():
    data = {}  # policy -> list recs
    banks = {}  # (policy, seed) -> bank
    for p in POLICIES:
        path = CORPUS / p / "trajectories.csv"
        recs = list(csv.DictReader(path.open(encoding="utf-8")))
        for r in recs:
            for k in ("seed", "step", "day", "hour", "hands", "plants", "melon", "animals", "empty", "n_shops"):
                r[k] = int(float(r[k]))
            r["money"] = float(r["money"])
            r["bank_end"] = float(r["bank_end"])
        data[p] = recs
        for r in recs:
            banks[(p, r["seed"])] = r["bank_end"]
    return data, banks


def state_key(r, policy_id=None):
    mb = 0 if r["money"] < 200 else (1 if r["money"] < 1000 else (2 if r["money"] < 5000 else 3))
    base = (r["day"], r["hour"] // 6, mb, min(r["animals"], 5), min(r["plants"] // 5, 4), min(r["hands"], 4))
    if policy_id is None:
        return base
    return (policy_id,) + base


def train_bc(recs, conditioned=False):
    votes = defaultdict(Counter)
    for r in recs:
        if r["split"] != "train":
            continue
        pid = r["policy"] if conditioned else None
        votes[state_key(r, pid)][r["sig"]] += 1
    default = Counter(r["sig"] for r in recs if r["split"] == "train").most_common(1)[0][0]
    lut = {k: c.most_common(1)[0][0] for k, c in votes.items()}
    return lut, default, len(votes)


def parse_sig(sig):
    orders = []
    if not sig:
        return orders
    for part in sig.split("|"):
        if part == "HIRE":
            orders.append(["HIRE"])
        elif part == "BUY_LAND":
            orders.append(["BUY_LAND"])
        elif part in ("BUY_ANIMAL", "BUY_SEED", "BUY_PRODUCT"):
            orders.append([part, "WHEAT", 4])  # generic; sanitize will clamp
        elif part == "SELL":
            orders.append(["SELL", "MILK", 1])  # qty filled from shed later
    return orders


class BCAgent:
    def __init__(self, lut, default, policy_id=None, conditioned=False):
        self.lut = lut
        self.default = default
        self.policy_id = policy_id
        self.conditioned = conditioned
        from p11_planner import planner as pmod
        self._pmod = pmod
        self._planner = None

    def act(self, observation, configuration=None):
        obs = observation or {}
        if self._planner is None:
            self._planner = self._pmod.StrategicPlanner()
        base = self._planner.act(obs)
        step = int(obs.get("step") or 0)
        farm = (obs.get("farms") or [])[0]
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
        key = state_key(r, self.policy_id if self.conditioned else None)
        sig = self.lut.get(key, self.default)
        shed = dict(private.get("shed") or {})
        market = []
        for o in parse_sig(sig):
            if o[0] == "SELL":
                # sell all non-wheat
                for item, q in shed.items():
                    if item != "WHEAT" and int(q or 0) > 0:
                        market.append(["SELL", item, int(q)])
            else:
                market.append(o)
        action = dict(base or {})
        action["market"] = (market + list(action.get("market") or []))[:10]
        from p10_executor.validators import sanitize_action
        return sanitize_action(
            action, shed=shed, money=float(farm.get("money") or 0),
            prices=dict((obs.get("market") or {}).get("prices") or {}),
        )


def run_bc(lut, default, seed, policy_id=None, conditioned=False):
    finn = load_pool("fallow_finn")
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
    agent = BCAgent(lut, default, policy_id, conditioned)
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    env.run([agent.act, finn])
    f = env.steps[-1]
    return float(f[0]["observation"]["farms"][0]["money"])


def eval_policy_set(train_recs, name, banks, conditioned=False, use_policy_id="R2"):
    lut, default, nb = train_bc(train_recs, conditioned=conditioned)
    ratios = []
    banks_h = []
    for seed in HOLDOUT:
        bank = run_bc(lut, default, seed, policy_id=use_policy_id, conditioned=conditioned)
        ref = banks.get(("R2", seed), 0)
        ratio = bank / ref if ref else 0
        ratios.append(ratio)
        banks_h.append(bank)
    mean_r = sum(ratios) / len(ratios)
    print(f"  {name}: mean_ratio={mean_r:.2%} banks={[round(b) for b in banks_h]} buckets={nb}", flush=True)
    return {"name": name, "mean_ratio": mean_r, "n_buckets": nb,
            "bank_s11": banks_h[0], "bank_s12": banks_h[1], "bank_s13": banks_h[2],
            "conditioned": int(conditioned)}


def main():
    data, banks = load_corpus()
    print("corpus sizes:", {p: len(data[p]) for p in POLICIES})

    results = []

    # P32-A single elite
    print("\n=== P32-A single elite unconditioned ===")
    for p in POLICIES:
        recs = data[p]
        results.append(eval_policy_set(recs, f"single_{p}", banks, conditioned=False))

    # P32-B multi-elite unconditioned
    print("\n=== P32-B multi-elite unconditioned ===")
    combos = [
        ("R2",),
        ("R2", "kaito_v27"),
        ("R2", "kaito_v27", "qeinstein"),
        ("R2", "kaito_v27", "qeinstein", "rayk_rank"),
        ("kaito_v27", "qeinstein", "rayk_rank"),
    ]
    for combo in combos:
        recs = []
        for p in combo:
            recs.extend(data[p])
        name = "multi_" + "+".join(combo)
        results.append(eval_policy_set(recs, name, banks, conditioned=False))

    # P32-B2 multi-elite conditioned (policy_id=R2 at test — pick one family)
    print("\n=== P32-B2 multi-elite conditioned (test as R2) ===")
    combo = ("R2", "kaito_v27", "qeinstein", "rayk_rank")
    recs = []
    for p in combo:
        recs.extend(data[p])
    results.append(eval_policy_set(recs, "multi_all_cond_R2", banks, conditioned=True, use_policy_id="R2"))
    results.append(eval_policy_set(recs, "multi_all_cond_kaito", banks, conditioned=True, use_policy_id="kaito_v27"))
    results.append(eval_policy_set(recs, "multi_all_uncond", banks, conditioned=False))

    # P32-C leave-one-out: train 3, test ratio still vs R2 bank
    print("\n=== P32-C leave-one-out (unconditioned) ===")
    for held in POLICIES:
        train = [p for p in POLICIES if p != held]
        recs = []
        for p in train:
            recs.extend(data[p])
        results.append(eval_policy_set(recs, f"LOO_held_{held}", banks, conditioned=False))

    out = ROOT / "p32_bc_transfer.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        w.writeheader()
        w.writerows(results)

    print("\n=== SUMMARY ratios ===")
    for r in sorted(results, key=lambda x: -x["mean_ratio"]):
        print(f"  {r['name']:40s} {r['mean_ratio']:.2%}")
    print("wrote", out.name)


if __name__ == "__main__":
    main()
