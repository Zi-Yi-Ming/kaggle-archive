# -*- coding: utf-8 -*-
"""P30-A: history dependence of R2 actions (pinned harness).

M0 = current state only
Mk = state + k-day history summary
Measure: can we predict R2 market action-bundle better with history?

Falsification:
  If M1/M3/M5/M10 accuracy ≈ M0 (within 2pp), HISTORY_DEPENDENCE = NOT_SUPPORTED
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


def record(seed: int):
    r2 = load_r2()
    finn = load_pool("fallow_finn")
    recs = []

    def wrap(inner):
        def agent(obs, configuration=None):
            a = inner(obs, configuration)
            step = int(obs.get("step") or 0)
            day = step // 24
            hour = step % 24
            farm = (obs.get("farms") or [])[int(obs.get("player") or 0)]
            private = obs.get("private") or {}
            shed = dict(private.get("shed") or {})
            tiles = farm.get("tiles") or []
            plants = melon = animals = empty = wheat = 0
            for row in tiles:
                for t in row:
                    if t is None:
                        empty += 1
                    elif isinstance(t, dict):
                        if t.get("kind") == "PLANT":
                            plants += 1
                            if t.get("crop") == "MELON":
                                melon += 1
                            if t.get("crop") == "WHEAT":
                                wheat += 1
                        if t.get("animal"):
                            animals += 1
            market = a.get("market") or []
            sig = []
            hires = sells = buys = 0
            for o in market:
                if not o:
                    continue
                if o[0] == "HIRE":
                    hires += 1
                    sig.append("HIRE")
                elif o[0] == "SELL":
                    sells += 1
                    sig.append("SELL")
                elif o[0].startswith("BUY"):
                    buys += 1
                    sig.append(o[0])
            recs.append({
                "seed": seed, "step": step, "day": day, "hour": hour,
                "money": float(farm.get("money") or 0),
                "hands": len(farm.get("hands") or []),
                "n_land": len(farm.get("unlocked_quadrants") or []),
                "plants": plants, "melon": melon, "wheat": wheat,
                "animals": animals, "empty": empty,
                "shed_total": sum(int(v or 0) for v in shed.values()),
                "n_shops": len((obs.get("town") or {}).get("unlocked_shops") or []),
                "hires": hires, "sells": sells, "buys": buys,
                "sig": "|".join(sorted(set(sig))),
                "sig_full": "|".join(sig),
            })
            return a
        return agent

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    env.run([wrap(r2), finn])
    f = env.steps[-1]
    bank = float(f[0]["observation"]["farms"][0]["money"])
    return recs, bank


def cur_bucket(r, hour_only=False):
    mb = 0 if r["money"] < 200 else (1 if r["money"] < 1000 else (2 if r["money"] < 5000 else 3))
    return (
        r["day"],
        r["hour"] if not hour_only else r["hour"],
        mb,
        min(r["animals"], 5),
        min(r["plants"] // 5, 4),
        min(r["hands"], 4),
    )


def hist_features(recs, i, k):
    """Summarize previous k days ending at recs[i] day."""
    day = recs[i]["day"]
    past = [r for r in recs if day - k <= r["day"] < day]
    if not past:
        return ()
    hires = sum(r["hires"] for r in past)
    sells = sum(r["sells"] for r in past)
    buys = sum(r["buys"] for r in past)
    # deltas if we have start/end of window
    first = past[0]
    last = past[-1]
    d_money = last["money"] - first["money"]
    d_animals = last["animals"] - first["animals"]
    d_plants = last["plants"] - first["plants"]
    return (
        min(hires, 20) // 4,
        min(sells, 20) // 4,
        min(buys, 10) // 2,
        max(-5, min(5, int(d_money / 500))),
        max(-5, min(5, d_animals)),
        max(-5, min(5, d_plants // 3)),
    )


def evaluate(pred_fn, dataset):
    hit = tot = 0
    for r in dataset:
        pred = pred_fn(r)
        if pred == r["sig"]:
            hit += 1
        tot += 1
    return hit / max(tot, 1)


def main():
    all_recs = []
    for seed in (1, 2, 3, 4, 5):
        recs, bank = record(seed)
        for r in recs:
            r["bank_end"] = bank
        all_recs.extend(recs)
        print(f"seed{seed}: bank={bank:.0f} n={len(recs)}", flush=True)

    # write features
    out = ROOT / "p30_history_features.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["seed", "day", "hour", "money", "hands", "animals", "plants",
                    "melon", "shed_total", "n_shops", "hires", "sells", "buys", "sig"])
        for r in all_recs:
            w.writerow([r["seed"], r["day"], r["hour"], r["money"], r["hands"],
                        r["animals"], r["plants"], r["melon"], r["shed_total"],
                        r["n_shops"], r["hires"], r["sells"], r["buys"], r["sig"]])
    print("wrote", out.name, "rows", len(all_recs), flush=True)

    # train/test split by seed
    train = [r for r in all_recs if r["seed"] <= 3]
    test = [r for r in all_recs if r["seed"] >= 4]

    # ambiguity: same cur bucket, different sig
    by_bucket = defaultdict(list)
    for r in train:
        by_bucket[cur_bucket(r)].append(r["sig"])
    ambig = sum(1 for v in by_bucket.values() if len(set(v)) > 1)
    print(f"\n=== AMBIGUITY train ===")
    print(f"  buckets={len(by_bucket)} ambiguous={ambig} ({100*ambig/max(len(by_bucket),1):.0f}%)")
    # top ambiguous
    ambig_list = [(len(set(v)), k, Counter(v).most_common(3)) for k, v in by_bucket.items() if len(set(v)) > 1]
    ambig_list.sort(reverse=True)
    for n, k, top in ambig_list[:5]:
        print(f"  bucket={k} n_sig={n} top={top}")

    # build predictors
    def make_lookup(key_fn):
        votes = defaultdict(Counter)
        for r in train:
            votes[key_fn(r)][r["sig"]] += 1
        lut = {k: c.most_common(1)[0][0] for k, c in votes.items()}
        def pred(r):
            return lut.get(key_fn(r), lut.get(("default",), Counter(x["sig"] for x in train).most_common(1)[0][0]))
        return pred

    results = []
    for k, name in [(0, "M0"), (1, "M1"), (3, "M3"), (5, "M5"), (10, "M10")]:
        if k == 0:
            fn = lambda r: (cur_bucket(r),)
        else:
            fn = lambda r, k=k: (cur_bucket(r), hist_features(all_recs, all_recs.index(r), k) if r in all_recs else ())
        # hist_features needs global index — rebuild with attached hist
        pass

    # attach hist using list position (NOT list.index equality)
    for i, r in enumerate(all_recs):
        for k in (1, 3, 5, 10):
            r[f"h{k}"] = hist_features(all_recs, i, k)
    uh1 = set(r.get("h1") for r in train)
    print(f"debug unique h1 in train: {len(uh1)} sample={list(uh1)[:3]}", flush=True)

    results = []
    for k in (0, 1, 3, 5, 10):
        if k == 0:
            key = lambda r: cur_bucket(r)
        else:
            key = lambda r, k=k: (cur_bucket(r), r.get(f"h{k}"))
        votes = defaultdict(Counter)
        for r in train:
            votes[key(r)][r["sig"]] += 1
        default = Counter(r["sig"] for r in train).most_common(1)[0][0]
        lut = {kk: c.most_common(1)[0][0] for kk, c in votes.items()}
        acc = 0
        n = 0
        for r in test:
            pred = lut.get(key(r), default)
            acc += int(pred == r["sig"])
            n += 1
        acc /= max(n, 1)
        results.append({"model": f"M{k}", "accuracy": acc, "n_buckets": len(votes)})
        print(f"  M{k}: acc={acc:.3f} buckets={len(votes)}", flush=True)

    # ambiguity reduction with history
    print("\n=== AMBIGUITY with history (train) ===")
    for k in (1, 3, 5):
        by_b = defaultdict(set)
        for r in train:
            by_b[(cur_bucket(r), r.get(f"h{k}"))].add(r["sig"])
        amb = sum(1 for v in by_b.values() if len(v) > 1)
        print(f"  M{k} buckets={len(by_b)} ambiguous={amb} ({100*amb/max(len(by_b),1):.0f}%)")

    out2 = ROOT / "p30_history_model_comparison.csv"
    with open(out2, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        w.writeheader()
        w.writerows(results)
    print("wrote", out2.name)

    # decision
    m0 = results[0]["accuracy"]
    best_hist = max(results[1:], key=lambda x: x["accuracy"])
    delta = best_hist["accuracy"] - m0
    print(f"\nM0={m0:.3f} best_hist={best_hist['model']}={best_hist['accuracy']:.3f} Δ={delta:+.3f}")
    if delta < 0.02:
        print("HISTORY_DEPENDENCE = NOT_SUPPORTED")
    else:
        print("HISTORY_DEPENDENCE = SUPPORTED")


if __name__ == "__main__":
    main()
