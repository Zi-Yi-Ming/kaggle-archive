# -*- coding: utf-8 -*-
"""P68: fingerprint lineages in recent daily top episodes."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import json
import sys
from collections import Counter, defaultdict
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

EP = ROOT / "_external" / "p68_daily_top"
FINN = ROOT / "reference_agents" / "fallow_finn.py"
KNOWN = {
    "alperen": ROOT / "_external" / "p51_extracted2" / "kaggriculture_metacounter_r1_scored_agent.py",
    "guru": ROOT / "_external" / "p51_extracted2" / "kaggriculture_fully_dynamic_autonomous_agent.py",
    "R2": ROOT / "_push_medal" / "main.py",
    "V16": ROOT / "_external" / "p41_extracted" / "salem_2900_main.py",
}


def load_quiet(path, tag):
    spec = importlib.util.spec_from_file_location(tag, str(path))
    m = importlib.util.module_from_spec(spec)
    with redirect_stdout(io.StringIO()):
        spec.loader.exec_module(m)
    return m.agent if hasattr(m, "agent") else m.build_agent({})


def play_wrap(inner):
    n = getattr(getattr(inner, "__code__", None), "co_argcount", 2)
    if n <= 1:
        def agent(obs):
            return inner(obs)
    else:
        def agent(obs, configuration=None):
            return inner(obs, configuration)
    return agent


def fp_keys(fn, seed=1):
    keys = []
    n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)
    if n <= 1:
        def wrap(obs):
            a = fn(obs)
            keys.append(json.dumps({"m": a.get("market"), "f": a.get("farmer"), "h": a.get("hands")},
                                   sort_keys=True, default=str))
            return a
    else:
        def wrap(obs, configuration=None):
            a = fn(obs, configuration)
            keys.append(json.dumps({"m": a.get("market"), "f": a.get("farmer"), "h": a.get("hands")},
                                   sort_keys=True, default=str))
            return a
    finn = load_quiet(FINN, f"fp68_{id(object())}")
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    env.run([wrap, play_wrap(finn)])
    return keys


def sim(a, b):
    n = min(len(a), len(b))
    return sum(1 for i in range(n) if a[i] == b[i]) / n if n else 0.0


def episode_fps(path: Path):
    """Return list of seat fingerprints (keys of first 120 actions) + rewards."""
    d = json.loads(path.read_text(encoding="utf-8"))
    steps = d.get("steps") or []
    rewards = d.get("rewards") or []
    out = []
    for seat in (0, 1):
        keys = []
        for step in steps[:120]:
            a = step[seat].get("action") or {}
            keys.append(json.dumps({"m": a.get("market"), "f": a.get("farmer"), "h": a.get("hands")},
                                   sort_keys=True, default=str))
        h = hashlib.md5("\n".join(keys).encode()).hexdigest()[:12]
        # first market signature
        a0 = steps[0][seat].get("action") or {}
        out.append({
            "seat": seat,
            "fp": keys,
            "hash": h,
            "reward": rewards[seat] if seat < len(rewards) else None,
            "first_market": json.dumps(a0.get("market"), default=str)[:80],
        })
    return out, rewards


def main():
    print("known lineages seed1", flush=True)
    known_fp = {}
    for n, p in KNOWN.items():
        keys = fp_keys(load_quiet(p, f"kn68_{n}"), 1)
        known_fp[n] = keys[:120]
        print(f"  {n} fp120_hash={hashlib.md5(chr(10).join(known_fp[n]).encode()).hexdigest()[:12]}", flush=True)

    seats = []
    for path in sorted(EP.glob("*.json")):
        fps, rewards = episode_fps(path)
        for s in fps:
            sims = {n: sim(s["fp"], known_fp[n]) for n in known_fp}
            nearest = max(sims, key=sims.get)
            rec = {
                "file": path.name, "seat": s["seat"], "hash": s["hash"],
                "reward": s["reward"], "nearest": nearest, "nearest_sim": sims[nearest],
                "first_market": s["first_market"],
                **{f"sim_{k}": v for k, v in sims.items()},
            }
            seats.append(rec)
            print(f"  {path.name} s{s['seat']} r={s['reward']} "
                  f"nearest={nearest}:{sims[nearest]:.3f} fp={s['hash']}", flush=True)

    # cluster by hash
    print("\n=== hash clusters ===", flush=True)
    by_hash = defaultdict(list)
    for r in seats:
        by_hash[r["hash"]].append(r)
    print(f"unique hashes {len(by_hash)} / {len(seats)} seats", flush=True)
    for h, rs in sorted(by_hash.items(), key=lambda x: -len(x[1]))[:15]:
        rewards = [r["reward"] for r in rs if r["reward"] is not None]
        mean_r = sum(rewards)/len(rewards) if rewards else 0
        print(f"  {h} n={len(rs)} mean_r={mean_r:.0f} nearest={rs[0]['nearest']}:{rs[0]['nearest_sim']:.3f}", flush=True)

    # novel vs known: sim < 0.5
    novel = [r for r in seats if r["nearest_sim"] < 0.5]
    print(f"\nnovel seats (sim<0.5): {len(novel)}/{len(seats)}", flush=True)
    # high reward novel
    novel_sorted = sorted(novel, key=lambda r: -(r["reward"] or 0))
    for r in novel_sorted[:10]:
        print(f"  r={r['reward']} nearest={r['nearest']}:{r['nearest_sim']:.3f} {r['file']} s{r['seat']}", flush=True)

    with open(ROOT / "p68_daily_fingerprints.csv", "w", newline="", encoding="utf-8") as f:
        fields = [k for k in seats[0].keys() if k != "fp"]
        wri = csv.DictWriter(f, fieldnames=fields)
        wri.writeheader()
        for r in seats:
            wri.writerow({k: r[k] for k in fields})
    print("wrote p68_daily_fingerprints.csv", flush=True)


if __name__ == "__main__":
    main()
