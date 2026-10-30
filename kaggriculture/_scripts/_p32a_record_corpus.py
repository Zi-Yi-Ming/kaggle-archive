# -*- coding: utf-8 -*-
"""P32a: record heterogeneous elite trajectories to elite_corpus/."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

CORPUS = ROOT / "elite_corpus"

ELITES = {
    "R2": ROOT / "_push_medal" / "main.py",
    "kaito_v27": ROOT / "_external" / "public_nb" / "kaito_v27" / "main.py",
    "qeinstein": ROOT / "_external" / "git" / "qeinstein" / "dist" / "sub-009-moev2" / "main.py",
    "rayk_rank": ROOT / "_external" / "public_nb" / "rayk_rank" / "main.py",
}

TRAIN_SEEDS = (1, 2, 3, 4)
HOLDOUT_SEEDS = (11, 12, 13)


def load_mod(path, name):
    spec = importlib.util.spec_from_file_location(name, str(path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def get_agent(mod):
    if hasattr(mod, "agent"):
        return mod.agent
    if hasattr(mod, "build_agent"):
        return mod.build_agent({})
    return None


def load_finn():
    return load_mod(ROOT / "reference_agents" / "fallow_finn.py", "finn_p32").agent


def record(name, agent_fn, seed):
    finn = load_finn()
    recs = []

    def wrap(inner):
        def agent(obs, configuration=None):
            a = inner(obs, configuration)
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
            market = a.get("market") or []
            sig = []
            for o in market:
                if not o:
                    continue
                if o[0] == "HIRE":
                    sig.append("HIRE")
                elif o[0] == "SELL":
                    sig.append("SELL")
                elif o[0].startswith("BUY"):
                    sig.append(o[0])
            recs.append({
                "policy": name, "seed": seed, "step": step,
                "day": step // 24, "hour": step % 24,
                "money": float(farm.get("money") or 0),
                "hands": len(farm.get("hands") or []),
                "plants": plants, "melon": melon, "animals": animals, "empty": empty,
                "n_shops": len((obs.get("town") or {}).get("unlocked_shops") or []),
                "sig": "|".join(sorted(set(sig))),
            })
            return a
        return agent

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    env.run([wrap(agent_fn), finn])
    f = env.steps[-1]
    bank = float(f[0]["observation"]["farms"][0]["money"])
    return recs, bank


def main():
    CORPUS.mkdir(exist_ok=True)
    banks = []
    for name, path in ELITES.items():
        if not path.exists():
            print("SKIP", name, flush=True)
            continue
        try:
            fn = get_agent(load_mod(path, f"el_{name}"))
        except Exception as e:
            print("SKIP load", name, e, flush=True)
            continue
        outdir = CORPUS / name
        outdir.mkdir(exist_ok=True)
        all_recs = []
        for seed in TRAIN_SEEDS + HOLDOUT_SEEDS:
            recs, bank = record(name, fn, seed)
            split = "train" if seed in TRAIN_SEEDS else "holdout"
            for r in recs:
                r["split"] = split
                r["bank_end"] = bank
            all_recs.extend(recs)
            banks.append({"policy": name, "seed": seed, "split": split, "bank": bank})
            print(f"  {name} s{seed} [{split}] bank={bank:.0f}", flush=True)
        out = outdir / "trajectories.csv"
        with open(out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(all_recs[0].keys()))
            w.writeheader()
            w.writerows(all_recs)
        print(f"wrote {out} n={len(all_recs)}", flush=True)

    outb = CORPUS / "banks.csv"
    with open(outb, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(banks[0].keys()))
        w.writeheader()
        w.writerows(banks)
    print("wrote", outb)


if __name__ == "__main__":
    main()
