# -*- coding: utf-8 -*-
"""P37: elite program recombination — splice open-loop tapes at landmarks.

NOT market|worker split (P33: coupled).
Splice by time window / phase boundary.
Pinned harness. vs finn. seeds 1-3.
"""
from __future__ import annotations

import csv
import importlib.util
import sys
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


def load_finn():
    return load_mod(ROOT / "reference_agents" / "fallow_finn.py", "finn_p37").agent


def make_splice(agent_a, agent_b, step_lo, step_hi):
    """Use A on [step_lo, step_hi), B otherwise."""
    def agent(obs, configuration=None):
        step = int(obs.get("step") or 0)
        if step_lo <= step < step_hi:
            return agent_a(obs, configuration)
        return agent_b(obs, configuration)
    return agent


def make_phase_splice(a_fn, b_fn, day_cut):
    """A on days < day_cut, B on days >= day_cut."""
    return make_splice(a_fn, b_fn, 0, day_cut * 24)


def run_vs_finn(own_fn, seed):
    finn = load_finn()
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    env.run([own_fn, finn])
    f = env.steps[-1]
    return float(f[0]["observation"]["farms"][0]["money"])


def main():
    # load all once per seed (fresh instances)
    def fresh(name):
        return get_agent(load_mod(ELITES[name], f"p37_{name}_{id(object())}"))

    # recombination specs: (label, make_fn)
    def pure(name):
        return lambda: fresh(name)

    def spliced(na, nb, lo, hi):
        def f():
            return make_splice(fresh(na), fresh(nb), lo, hi)
        return f

    def phase(na, nb, day_cut):
        def f():
            return make_phase_splice(fresh(na), fresh(nb), day_cut)
        return f

    specs = [
        ("pure_R2", pure("R2")),
        ("pure_kaito", pure("kaito_v27")),
        ("pure_Q", pure("qeinstein")),
        ("pure_rayk", pure("rayk_rank")),
        # shop branch window: before 144 vs after
        ("R2_then_kaito@144", spliced("R2", "kaito_v27", 144, 720)),
        ("kaito_then_R2@144", spliced("kaito_v27", "R2", 144, 720)),
        ("R2_then_Q@144", spliced("R2", "qeinstein", 144, 720)),
        ("Q_then_R2@144", spliced("qeinstein", "R2", 144, 720)),
        ("rayk_then_R2@144", spliced("rayk_rank", "R2", 144, 720)),
        # phase cuts (P34 landmarks)
        ("R2_boot_kaito_rest_d2", phase("R2", "kaito_v27", 2)),
        ("R2_expand_kaito_rest_d6", phase("R2", "kaito_v27", 6)),
        ("R2_convert_Q_rest_d10", phase("R2", "qeinstein", 10)),
        ("kaito_boot_R2_rest_d2", phase("kaito_v27", "R2", 2)),
        ("kaito_scale_rayk_rest_d12", phase("kaito_v27", "rayk_rank", 12)),
        ("rayk_boot_R2_rest_d6", phase("rayk_rank", "R2", 6)),
    ]

    rows = []
    for seed in (1, 2, 3):
        for label, factory in specs:
            try:
                fn = factory()
                bank = run_vs_finn(fn, seed)
            except Exception as e:
                print(f"  {label} s{seed} ERR {e}", flush=True)
                bank = None
            rows.append({"seed": seed, "label": label, "bank": bank})
            if bank is not None:
                print(f"  {label:28s} s{seed}: {bank:.0f}", flush=True)

    out = ROOT / "p37_recombination.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # summary
    print("\n=== MEAN BANKS ===")
    from collections import defaultdict
    by = defaultdict(list)
    for r in rows:
        if r["bank"] is not None:
            by[r["label"]].append(r["bank"])
    means = {k: sum(v)/len(v) for k, v in by.items()}
    for k, v in sorted(means.items(), key=lambda x: -x[1]):
        print(f"  {k:28s} {v:.0f}  n={len(by[k])}")

    # decision
    pure_max = max((means[k] for k in means if k.startswith("pure_")), default=0)
    hybrid = {k: v for k, v in means.items() if not k.startswith("pure_")}
    hybrid_max = max(hybrid.values()) if hybrid else 0
    best_h = max(hybrid, key=hybrid.get) if hybrid else None
    print(f"\npure_max={pure_max:.0f} hybrid_max={hybrid_max:.0f} best={best_h}")
    if hybrid_max >= pure_max * 1.03:
        print("PROGRAM_COMPOSITION_SUPPORTED")
    elif hybrid_max >= pure_max * 0.8:
        print("PROGRAM_WEAK_COMPOSITION")
    else:
        print("ATOMIC_PROGRAM")
    print("wrote", out.name)


if __name__ == "__main__":
    main()
