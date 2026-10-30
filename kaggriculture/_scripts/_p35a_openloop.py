# -*- coding: utf-8 -*-
"""P35-A: open-loop acc action=f(day,hour) for each elite."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
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


def record(name, agent_fn, seed=1):
    finn = load_mod(ROOT / "reference_agents" / "fallow_finn.py", f"ol_{name}").agent
    recs = []

    def wrap(inner):
        def agent(obs, configuration=None):
            a = inner(obs, configuration)
            step = int(obs.get("step") or 0)
            sig = json.dumps(
                {"m": a.get("market"), "f": a.get("farmer"), "h": a.get("hands")},
                sort_keys=True, default=str,
            )
            recs.append({"day": step // 24, "hour": step % 24, "sig": sig})
            return a
        return agent

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    env.run([wrap(agent_fn), finn])
    f = env.steps[-1]
    return recs, float(f[0]["observation"]["farms"][0]["money"])


def main():
    rows = []
    for name, path in ELITES.items():
        fn = get_agent(load_mod(path, f"ola_{name}"))
        recs, bank = record(name, fn, seed=1)
        # exact f(day,hour) -> sig
        votes = defaultdict(Counter)
        for r in recs:
            votes[(r["day"], r["hour"])][r["sig"]] += 1
        # if unique mapping, acc=1
        hit = 0
        ent = 0.0
        import math
        for r in recs:
            c = votes[(r["day"], r["hour"])]
            pred = c.most_common(1)[0][0]
            if pred == r["sig"]:
                hit += 1
        acc = hit / len(recs)
        # entropy of day-hour mapping
        for k, c in votes.items():
            tot = sum(c.values())
            for v in c.values():
                p = v / tot
                ent -= p * math.log2(p)
        n_unique = sum(1 for k, c in votes.items() if len(c) == 1)
        rows.append({
            "policy": name, "bank": bank, "n_steps": len(recs),
            "openloop_acc": acc, "unique_dh": n_unique, "n_dh": len(votes),
            "entropy_dh": ent / max(len(votes), 1),
        })
        print(f"{name:14s} bank={bank:.0f} openloop_acc={acc:.4f} "
              f"unique_dh={n_unique}/{len(votes)} ent={ent/max(len(votes),1):.3f}", flush=True)

    out = ROOT / "p35a_openloop_acc.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("wrote", out.name)


if __name__ == "__main__":
    main()
