"""EXP-10B validation batch on Kaggle Notebook (16 games).

Runs V0 (v11E production) seeds 1-8 x seats 0/1 vs closer_cleo on the
Kaggle notebook runtime, pinning kaggle-environments to 1.32.7, and writes
kaggle_v0.json in the same record format as the local collector for
bit-exact cross-machine comparison.

Data layout: /kaggle/input/exp10a-code/{v11e_agent.py, executed_ledger.py}
"""
import glob
import json
import multiprocessing as mp
import os
import subprocess
import sys

WORK = "/tmp/exp10a_work"
os.makedirs(WORK, exist_ok=True)


def pin_engine():
    """Ensure kaggle-environments 1.32.7 (same as local baseline)."""
    try:
        from kaggle_environments import version
        v = version()
        print("engine version:", v)
        if v == "1.32.7":
            return
    except Exception:
        pass
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q",
                           "kaggle-environments==1.32.7"])


pin_engine()

# Stage code files from the attached dataset into WORK (flat import dir).
# v3 diagnostic showed the dataset mounts under /kaggle/input/datasets/
# (dir-mode zip naming), not /kaggle/input/exp10a-code/. Search both.
print("INPUT root:", os.listdir("/kaggle/input") if os.path.isdir("/kaggle/input") else "MISSING",
      flush=True)
SRC = []
for root in ("/kaggle/input/exp10a-code", "/kaggle/input/datasets"):
    SRC += glob.glob(os.path.join(root, "**", "*.py"), recursive=True)
print("candidate files:", SRC, flush=True)
import shutil
seen = set()
for p in SRC:
    base = os.path.basename(p)
    if base not in seen:
        seen.add(base)
        shutil.copy(p, os.path.join(WORK, base))
        print("staged", base, flush=True)
sys.path.insert(0, WORK)

# v4 diagnosis: Kaggle's preinstalled kaggle_environments has a NEWER utils.py
# without resolve_episode_seed, while pip-installed 1.32.7 didn't take effect
# cleanly -> mixed package. Overwrite both engine files with the vendored
# 1.32.7 copies before importing executed_ledger.
import kaggle_environments as _ke
_ke_dir = os.path.dirname(_ke.__file__)
_overwrites = {
    os.path.join(_ke_dir, "envs", "kaggriculture", "kaggriculture.py"):
        os.path.join(WORK, "engine_kaggriculture.py"),
    os.path.join(_ke_dir, "utils.py"):
        os.path.join(WORK, "engine_utils.py"),
}
for dst, src in _overwrites.items():
    if os.path.isfile(src):
        shutil.copy(src, dst)
        print("overwrote", dst, flush=True)
# clear cached modules to force reimport of overwritten files
for _m in list(sys.modules):
    if _m.startswith("kaggle_environments"):
        del sys.modules[_m]

import executed_ledger as EL  # noqa: E402
from kaggle_environments import make  # noqa: E402


def load_agent(path):
    import importlib.util
    spec = importlib.util.spec_from_file_location(path.replace("/", "_").replace(".", "_"), path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


OPP = load_agent(os.path.join(WORK, "closer_cleo.py"))
CAND = load_agent(os.path.join(WORK, "v11e_agent.py"))


def run_one(args):
    seed, seat = args
    a, b = (CAND, OPP) if seat == 0 else (OPP, CAND)
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.info["seed"] = seed
    env.run([a, b])
    steps = env.steps
    agg, valid, n, mism = EL.replay_game(steps, seat)
    final = steps[-1][seat]["observation"]["farms"][seat]["money"]
    rev = agg["SELL"][1]
    cost = sum(agg[t][1] for t in ("BUY_SEED", "BUY_PRODUCT", "BUY_ANIMAL", "HIRE", "BUY_LAND"))
    recon = round(final - (EL.INITIAL_BANK + rev - cost), 4)
    first_sell_step = None
    for s in range(1, len(steps)):
        for m in ((steps[s][seat].get("action") or {}).get("market") or []):
            if isinstance(m, list) and m and m[0] == "SELL":
                first_sell_step = s
                break
        if first_sell_step is not None:
            break
    return {"seed": seed, "seat": seat, "steps": len(steps), "valid": valid,
            "recon": recon, "bank": round(float(final), 2),
            "sell_rev": round(float(rev), 2), "sell_exec": agg["SELL"][0],
            "sell_issued": agg["issued"]["SELL"], "first_sell_step": first_sell_step}


def main():
    tasks = [(s, seat) for s in range(1, 9) for seat in (0, 1)]
    # v5 crashed in mp.Pool workers ("buffer full" C++ abort during fork);
    # run sequentially instead — 16 games fits the 12h kernel limit easily.
    res = []
    for t in tasks:
        r = run_one(t)
        res.append(r)
        print("done", r["seed"], r["seat"], r["bank"], flush=True)
    res.sort(key=lambda r: (r["seed"], r["seat"]))
    bad = [r for r in res if r["steps"] != 720 or abs(r["recon"]) > 0.005]
    print(f"{len(res)} games | gate failures {len(bad)}")
    with open("/kaggle/working/kaggle_v0.json", "w") as f:
        json.dump(res, f)


if __name__ == "__main__":
    main()
