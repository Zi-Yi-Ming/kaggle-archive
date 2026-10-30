# -*- coding: utf-8 -*-
"""P12 Phase6: B0 vs B1 vs R2, 4 paired seeds, both seats. Minimal gate."""
from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402


def load_r2():
    spec = importlib.util.spec_from_file_location(
        "r2_abl_" + str(id(object())), str(ROOT / "_push_medal" / "main.py")
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def day_money(env, seat):
    out = {}
    for idx, s in enumerate(env.steps):
        rec = s[seat]
        if not rec:
            continue
        obs = rec.get("observation") or {}
        step = int(obs.get("step") or idx)
        farms = obs.get("farms") or []
        if len(farms) >= 2:
            out[step // 24] = {
                "my": float(farms[seat].get("money") or 0),
                "opp": float(farms[1 - seat].get("money") or 0),
                "hands": len(farms[seat].get("hands") or []),
            }
    return out


def run(label, own_factory, seed, seat):
    from _p12_b1_agent import make_b0_agent, make_b1_agent
    if label == "B0":
        own = make_b0_agent()
    else:
        own = make_b1_agent()
    opp = load_r2()
    agents = [own, opp] if seat == 0 else [opp, own]
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.configuration["seed"] = seed
    env.run(agents)
    f = env.steps[-1]
    my = float(f[seat]["observation"]["farms"][seat]["money"])
    op = float(f[seat]["observation"]["farms"][1 - seat]["money"])
    err = [s.get("error") for s in f if s.get("error")]
    snaps = day_money(env, seat)
    rec = {
        "label": label, "seed": seed, "seat": seat,
        "my": my, "opp": op, "margin": my - op, "win": int(my > op),
        "bankrupt": int(my < 1000), "errors": str(err),
    }
    for d in (5, 10, 15, 20, 25, 29):
        sn = snaps.get(d) or {}
        rec[f"d{d}_my"] = sn.get("my")
        rec[f"d{d}_gap"] = (sn.get("my") - sn.get("opp")) if sn.get("my") is not None else None
        rec[f"d{d}_hands"] = sn.get("hands")
    print(f"{label} s{seed} seat{seat}: {my:.0f} vs {op:.0f} m={my-op:+.0f} "
          f"d10={rec.get('d10_my')} d10h={rec.get('d10_hands')} "
          f"d20={rec.get('d20_my')} d29={rec.get('d29_my')} err={err}", flush=True)
    return rec


def main():
    rows = []
    for seat in (0, 1):
        for seed in (1, 2, 3, 4):
            rows.append(run("B0", None, seed, seat))
            rows.append(run("B1", None, seed, seat))

    out = ROOT / "p12_primitive_ablation.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    for label in ("B0", "B1"):
        sub = [r for r in rows if r["label"] == label]
        wins = sum(r["win"] for r in sub)
        mm = sum(r["margin"] for r in sub) / len(sub)
        bank = sum(r["my"] for r in sub) / len(sub)
        d10 = [r["d10_my"] for r in sub if r.get("d10_my") is not None]
        d20 = [r["d20_my"] for r in sub if r.get("d20_my") is not None]
        d29 = [r["d29_my"] for r in sub if r.get("d29_my") is not None]
        h10 = [r["d10_hands"] for r in sub if r.get("d10_hands") is not None]
        print(f"\n{label}: {wins}/{len(sub)}  margin={mm:+.0f}  bank={bank:.0f}  "
              f"d10={sum(d10)/len(d10) if d10 else None:.0f}  "
              f"d20={sum(d20)/len(d20) if d20 else None:.0f}  "
              f"d29={sum(d29)/len(d29) if d29 else None:.0f}  "
              f"hands10={sum(h10)/len(h10) if h10 else None:.1f}")
    print("wrote", out.name)


if __name__ == "__main__":
    main()
