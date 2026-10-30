# -*- coding: utf-8 -*-
"""P44 Phase1-4: parse R2 live replays → distill → evaluate base tape.

Red lines: finn never wrapped; env.info['seed'] pinned; no R2 mutation.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import statistics
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

REP = ROOT / "_external" / "p42_replays"
OUT_TAPES = ROOT / "p44_distilled_tapes"
OUT_TAPES.mkdir(exist_ok=True)

R2_PATH = ROOT / "_push_medal" / "main.py"
FINN_PATH = ROOT / "reference_agents" / "fallow_finn.py"


def load_agent(path, tag):
    spec = importlib.util.spec_from_file_location(tag, str(path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent if hasattr(m, "agent") else m.build_agent({})


def wrap_match_arity(inner, keys=None):
    n = getattr(getattr(inner, "__code__", None), "co_argcount", 2)

    def _rec(a):
        if keys is not None:
            keys.append(json.dumps(
                {"m": a.get("market"), "f": a.get("farmer"), "h": a.get("hands")},
                sort_keys=True, default=str,
            ))

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


def run_vs_finn(agent_fn, seed, collect=False):
    """finn NEVER wrapped. Returns bank0 (us), bank1 (finn), hash."""
    finn = load_agent(FINN_PATH, f"finn_p44_{seed}_{id(object())}")
    keys = []
    play = wrap_match_arity(agent_fn, keys) if collect else agent_fn
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    env.run([play, finn])
    f = env.steps[-1]
    b0 = float(f[0]["observation"]["farms"][0]["money"])
    b1 = float(f[1]["observation"]["farms"][1]["money"])
    h = hashlib.md5("\n".join(keys).encode()).hexdigest()[:16] if keys else ""
    return b0, b1, h


def parse_r2_replays():
    """Extract our R2 actions from each live replay (seat-aware)."""
    meta = json.loads((REP / "meta.json").read_text(encoding="utf-8"))
    episodes = []
    for m in meta:
        path = Path(m["path"])
        if not path.exists():
            continue
        d = json.loads(path.read_text(encoding="utf-8"))
        steps = d.get("steps") or []
        if len(steps) != 720:
            print(f"  SKIP {m['episode_id']} n_steps={len(steps)}")
            continue
        seat = int(m.get("our_seat") or 0)
        actions = []
        for step in steps:
            a = step[seat].get("action") or {}
            actions.append({
                "market": a.get("market") or [],
                "farmer": a.get("farmer") or ["PASS"],
                "hands": a.get("hands") or [],
            })
        episodes.append({
            "episode_id": m["episode_id"],
            "opp": m["opp_team"],
            "seat": seat,
            "reward": m.get("our_reward"),
            "actions": actions,
            "seed_info": (d.get("info") or {}).get("seed"),
        })
    return episodes


def canon_action(a, kind):
    if kind == "market":
        return json.dumps(a.get("market"), sort_keys=True, default=str)
    return json.dumps({"f": a.get("farmer"), "h": a.get("hands")}, sort_keys=True, default=str)


def majority_tape(episodes):
    """Per-step majority vote. market and worker voted SEPARATELY.
    Tie → keep first-episode order, record tie. No random.
    """
    n = len(episodes)
    assert n > 0
    L = 720
    distilled = []
    stats = {
        "n_episodes": n,
        "market_agree_steps": 0,
        "worker_agree_steps": 0,
        "both_agree_steps": 0,
        "market_ties": 0,
        "worker_ties": 0,
        "market_unanimous": 0,
        "worker_unanimous": 0,
    }
    step_rows = []
    for t in range(L):
        m_votes = Counter()
        w_votes = Counter()
        m_ex = {}
        w_ex = {}
        for ep in episodes:
            a = ep["actions"][t]
            mk = canon_action(a, "market")
            wk = canon_action(a, "worker")
            m_votes[mk] += 1
            w_votes[wk] += 1
            m_ex.setdefault(mk, a["market"])
            w_ex.setdefault(wk, (a["farmer"], a["hands"]))

        # market winner
        m_top = m_votes.most_common()
        m_best = m_top[0][1]
        m_cands = [k for k, c in m_top if c == m_best]
        m_tie = len(m_cands) > 1
        if m_tie:
            # deterministic: first episode order among tied
            for ep in episodes:
                k = canon_action(ep["actions"][t], "market")
                if k in m_cands:
                    m_key = k
                    break
            stats["market_ties"] += 1
        else:
            m_key = m_cands[0]
        m_agree = m_best / n
        if m_best == n:
            stats["market_unanimous"] += 1
        if m_agree >= 0.95:
            stats["market_agree_steps"] += 1

        # worker winner
        w_top = w_votes.most_common()
        w_best = w_top[0][1]
        w_cands = [k for k, c in w_top if c == w_best]
        w_tie = len(w_cands) > 1
        if w_tie:
            for ep in episodes:
                k = canon_action(ep["actions"][t], "worker")
                if k in w_cands:
                    w_key = k
                    break
            stats["worker_ties"] += 1
        else:
            w_key = w_cands[0]
        w_agree = w_best / n
        if w_best == n:
            stats["worker_unanimous"] += 1
        if w_agree >= 0.95:
            stats["worker_agree_steps"] += 1

        if m_agree >= 0.95 and w_agree >= 0.95:
            stats["both_agree_steps"] += 1

        farmer, hands = w_ex[w_key]
        distilled.append({
            "market": m_ex[m_key],
            "farmer": farmer,
            "hands": hands,
        })
        step_rows.append({
            "step": t,
            "day": t // 24,
            "market_agree": round(m_agree, 4),
            "worker_agree": round(w_agree, 4),
            "market_tie": int(m_tie),
            "worker_tie": int(w_tie),
            "n_market_modes": len(m_votes),
            "n_worker_modes": len(w_votes),
            "market_votes": m_best,
            "worker_votes": w_best,
        })
    stats["market_agree_ratio"] = stats["market_agree_steps"] / L
    stats["worker_agree_ratio"] = stats["worker_agree_steps"] / L
    stats["both_agree_ratio"] = stats["both_agree_steps"] / L
    stats["market_unanimous_ratio"] = stats["market_unanimous"] / L
    stats["worker_unanimous_ratio"] = stats["worker_unanimous"] / L
    return distilled, stats, step_rows


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


def eval_tape(tape, seeds, label):
    """Double-seat vs finn. W/D/L uses bank comparison per seat-pair? Spec:
    candidate vs finn seat A and seat B. W if our bank > finn bank."""
    rows = []
    w = d = l = 0
    banks = []
    for seed in seeds:
        # seat 0: we are agent0
        b0a, b1a, h0 = run_vs_finn(tape_agent(tape), seed)
        # seat 1: we are agent1 → swap by running [finn, us]
        finn = load_agent(FINN_PATH, f"finn_sw_{seed}")
        us = tape_agent(tape)
        env = make("kaggriculture", debug=False)
        env.configuration["episodeSteps"] = 720
        if env.info is None:
            env.info = {}
        env.info["seed"] = int(seed)
        env.run([finn, us])
        f = env.steps[-1]
        b0b = float(f[0]["observation"]["farms"][0]["money"])  # finn
        b1b = float(f[1]["observation"]["farms"][1]["money"])  # us

        # paired: mean our bank vs mean finn bank across seats
        our = (b0a + b1b) / 2
        opp = (b1a + b0b) / 2
        banks.append(our)
        if our > opp + 1:
            w += 1
            res = "W"
        elif opp > our + 1:
            l += 1
            res = "L"
        else:
            d += 1
            res = "D"
        rows.append({
            "label": label, "seed": seed,
            "us_s0": b0a, "finn_s1": b1a,
            "finn_s0": b0b, "us_s1": b1b,
            "our_mean": our, "opp_mean": opp, "result": res,
            "hash_s0": h0,
        })
        print(f"    {label} seed={seed} our={our:.0f} opp={opp:.0f} {res}", flush=True)
    return {
        "label": label, "W": w, "D": d, "L": l, "W-L": w - l,
        "bank_mean": statistics.mean(banks) if banks else 0,
        "bank_std": statistics.pstdev(banks) if len(banks) > 1 else 0,
        "bank_min": min(banks) if banks else 0,
        "bank_max": max(banks) if banks else 0,
        "rows": rows,
    }


def main():
    t0 = time.time()
    print("=== P44 PHASE1 parse R2 live replays ===", flush=True)
    episodes = parse_r2_replays()
    print(f"parsed {len(episodes)} complete 720-step R2 episodes", flush=True)

    print("\n=== PHASE3 majority distillation ===", flush=True)
    tape, stats, step_rows = majority_tape(episodes)
    print(json.dumps(stats, indent=2), flush=True)

    # hashes
    tape_json = json.dumps(tape, sort_keys=True, default=str)
    tape_hash = hashlib.md5(tape_json.encode()).hexdigest()[:16]
    print(f"tape_hash={tape_hash}", flush=True)

    (OUT_TAPES / "r2_live_distilled.json").write_text(
        json.dumps({"tape_hash": tape_hash, "stats": stats, "tape": tape}),
        encoding="utf-8",
    )
    with open(ROOT / "p44_distillation.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(step_rows[0].keys()))
        w.writeheader()
        w.writerows(step_rows)

    # sources
    with open(ROOT / "p44_replay_sources.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "episode_id", "opp", "seat", "reward", "seed_info", "n_steps",
        ])
        w.writeheader()
        for e in episodes:
            w.writerow({
                "episode_id": e["episode_id"], "opp": e["opp"], "seat": e["seat"],
                "reward": e["reward"], "seed_info": e["seed_info"], "n_steps": 720,
            })

    # Reconstruction gate: base tape vs source R2 bank on same seeds
    print("\n=== PHASE4 base tape vs finn (3 seeds, both seats) ===", flush=True)
    seeds = (1, 2, 3)
    base = eval_tape(tape, seeds, "distilled_base")
    print(f"BASE W-D-L {base['W']}-{base['D']}-{base['L']} W-L={base['W-L']} "
          f"bank_mean={base['bank_mean']:.0f}±{base['bank_std']:.0f}", flush=True)

    print("\n=== source live R2 bank reference (from replays) ===", flush=True)
    live_banks = [e["reward"] for e in episodes if e["reward"] is not None]
    print(f"live reward mean={statistics.mean(live_banks):.0f} "
          f"min={min(live_banks)} max={max(live_banks)}", flush=True)

    # also real R2 agent vs finn for comparison
    print("\n=== real R2 agent vs finn same seeds ===", flush=True)
    r2_res = []
    for seed in seeds:
        r2 = load_agent(R2_PATH, f"r2_p44_{seed}")
        b0, b1, _ = run_vs_finn(r2, seed)
        finn = load_agent(FINN_PATH, f"finn_r2_{seed}")
        r2b = load_agent(R2_PATH, f"r2_p44b_{seed}")
        env = make("kaggriculture", debug=False)
        env.configuration["episodeSteps"] = 720
        env.info = {"seed": int(seed)}
        env.run([finn, r2b])
        f = env.steps[-1]
        b1b = float(f[1]["observation"]["farms"][1]["money"])
        our = (b0 + b1b) / 2
        opp = (b1 + float(f[0]["observation"]["farms"][0]["money"])) / 2
        r2_res.append(our)
        print(f"  R2 seed={seed} our_mean={our:.0f} opp={opp:.0f}", flush=True)

    # reconstruction pass criteria
    # distilled should not be catastrophic vs live mean (~94k) or vs real R2
    recon_pass = True
    reasons = []
    if base["bank_mean"] < 20000:
        recon_pass = False
        reasons.append(f"bank_mean {base['bank_mean']:.0f} < 20k catastrophic")
    if base["bank_mean"] < statistics.mean(live_banks) * 0.25:
        recon_pass = False
        reasons.append("bank < 25% of live source mean")
    # need at least some W or D
    if base["W"] + base["D"] == 0:
        # still may pass reconstruction if tape runs clean
        reasons.append("no W/D vs finn (may still be valid recon)")

    print(f"\nRECONSTRUCTION_PASS={recon_pass} reasons={reasons}", flush=True)

    result = {
        "tape_hash": tape_hash,
        "stats": stats,
        "base": {k: v for k, v in base.items() if k != "rows"},
        "r2_local_mean": statistics.mean(r2_res),
        "live_mean": statistics.mean(live_banks),
        "recon_pass": recon_pass,
        "reasons": reasons,
        "dt": time.time() - t0,
    }
    (ROOT / "p44_phase4_base.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    with open(ROOT / "p44_candidate_results.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(base["rows"][0].keys()))
        w.writeheader()
        w.writerows(base["rows"])

    print("wrote p44_distillation.csv p44_replay_sources.csv p44_candidate_results.csv "
          f"dt={time.time()-t0:.0f}s", flush=True)
    return recon_pass, tape, stats, base


if __name__ == "__main__":
    main()
