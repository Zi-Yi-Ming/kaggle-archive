# -*- coding: utf-8 -*-
"""P73: top-team replay tapes as agents vs alperen."""
from __future__ import annotations

import csv
import importlib.util
import io
import json
import sys
import time
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle") / "kaggraviculture"
if not ROOT.exists():
    ROOT = Path(r"D:\桌面\Kaggle") / "kaggraviculture"
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

EP_DIRS = [
    ROOT / "_external" / "p68_daily_top",
    ROOT / "_external" / "p69_daily_top",
]
FINN = ROOT / "reference_agents" / "fallow_finn.py"
ALPEREN = ROOT / "_external" / "p51_extracted2" / "kaggraviculture_metacounter_r1_scored_agent.py"
if not ALPEREN.exists():
    ALPEREN = ROOT / "_external" / "p51_extracted2" / "kaggraviculture_metacounter_r1_scored_agent.py"

TEAMS = (
    "Majkel", "SpaTaro", "ymg_aq", "Artem", "DSM",
    "HowardLee", "Mengfei", "Orbital", "Catalyst", "carbonapi",
)


def load_quiet(path, tag):
    spec = importlib.util.spec_from_file_location(tag, str(path))
    m = importlib.util.module_from_spec(spec)
    with redirect_stdout(io.StringIO()):
        spec.loader.exec_module(m)
    return m.agent if hasattr(m, "agent") else m.build_agent({})


def play(inner):
    n = getattr(getattr(inner, "__code__", None), "co_argcount", 2)
    if n <= 1:
        def agent(obs):
            return inner(obs)
    else:
        def agent(obs, configuration=None):
            return inner(obs, configuration)
    return agent


def tape_agent(tape):
    def agent(observation, configuration=None):
        step = int((observation or {}).get("step") or 0)
        step = max(0, min(len(tape) - 1, step))
        a = tape[step]
        return {
            "farmer": a.get("farmer") or ["PASS"],
            "hands": a.get("hands") or [],
            "market": a.get("market") or [],
        }
    return agent


def run(a0, a1, seed):
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    env.run([play(a0), play(a1)])
    f = env.steps[-1]
    return (
        float(f[0]["observation"]["farms"][0]["money"]),
        float(f[1]["observation"]["farms"][1]["money"]),
    )


def collect():
    picked = []
    seen = set()
    for folder in EP_DIRS:
        if not folder.exists():
            print("skip missing", folder)
            continue
        for path in sorted(folder.glob("*.json")):
            try:
                d = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue
            teams = (d.get("info") or {}).get("TeamNames") or []
            rewards = d.get("rewards") or []
            steps = d.get("steps") or []
            if len(steps) != 720:
                continue
            for seat in range(min(2, len(teams))):
                team = str(teams[seat])
                if not any(t in team for t in TEAMS):
                    continue
                key = (team, path.name, seat)
                if key in seen:
                    continue
                seen.add(key)
                tape = []
                for step in steps:
                    a = step[seat].get("action") or {}
                    tape.append({
                        "market": a.get("market") or [],
                        "farmer": a.get("farmer") or ["PASS"],
                        "hands": a.get("hands") or [],
                    })
                picked.append({
                    "source": path.name,
                    "team": team,
                    "seat": seat,
                    "reward": rewards[seat] if seat < len(rewards) else None,
                    "tape": tape,
                })
    picked.sort(key=lambda r: -(r.get("reward") or 0))
    # max 2 per team
    by = {}
    out = []
    for r in picked:
        n = by.get(r["team"], 0)
        if n >= 2:
            continue
        by[r["team"]] = n + 1
        out.append(r)
    return out


def main():
    t0 = time.time()
    print("ROOT", ROOT, ROOT.exists(), flush=True)
    print("FINN", FINN.exists(), flush=True)
    print("ALPEREN", ALPEREN.exists(), flush=True)
    picked = collect()
    print(f"picked {len(picked)} tapes", flush=True)
    for r in picked:
        print(f"  {r['team'][:22]:22s} reward={r['reward']} {r['source']}", flush=True)
    if not picked:
        print("NO TAPES")
        return
    rows = []
    for rec in picked:
        agent = tape_agent(rec["tape"])
        banks = []
        try:
            for seed in (1, 2, 3):
                b0, _ = run(agent, load_quiet(FINN, f"f_{rec['team'][:8]}_{seed}"), seed)
                banks.append(b0)
        except Exception as e:
            print(f"FAIL {rec['team'][:20]} {e}", flush=True)
            continue
        mean = sum(banks) / len(banks)
        row = {
            "team": rec["team"], "source": rec["source"], "seat": rec["seat"],
            "live_reward": rec["reward"], "finn_mean3": mean,
        }
        print(f"{rec['team'][:22]:22s} live={rec['reward']} finn_mean={mean:.0f}", flush=True)
        if mean >= 140000:
            w = d = l = 0
            for seed in (1, 2, 3):
                a0, a1 = run(agent, load_quiet(ALPEREN, f"a{seed}"), seed)
                b0, b1 = run(load_quiet(ALPEREN, f"ab{seed}"), agent, seed)
                our = (a0 + b1) / 2
                theirs = (a1 + b0) / 2
                if our > theirs + 1:
                    w += 1
                elif theirs > our + 1:
                    l += 1
                else:
                    d += 1
            row.update({"vs_alp_W": w, "vs_alp_D": d, "vs_alp_L": l, "vs_alp_WL": w - l})
            print(f"  vs alperen {w}-{d}-{l}", flush=True)
        rows.append(row)
    out_csv = ROOT / "p73_top_tape_eval.csv"
    if rows:
        with open(out_csv, "w", newline="", encoding="utf-8") as f:
            fields = sorted({k for r in rows for k in r})
            wri = csv.DictWriter(f, fieldnames=fields)
            wri.writeheader()
            wri.writerows(rows)
        print("wrote", out_csv, flush=True)
    print("dt", round(time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
