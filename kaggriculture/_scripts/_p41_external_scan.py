# -*- coding: utf-8 -*-
"""P41 external elite discovery: extract notebook agents, pinned eval vs finn."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import sys
import time
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

NB_DIR = ROOT / "_external" / "p41_candidates"
OUT_DIR = ROOT / "_external" / "p41_extracted"
OUT_DIR.mkdir(exist_ok=True)


def extract_notebook(path: Path) -> str:
    nb = json.loads(path.read_text(encoding="utf-8"))
    parts = []
    for c in nb.get("cells", []):
        if c.get("cell_type") == "code":
            parts.append("".join(c.get("source") or []))
    return "\n\n# --- cell ---\n\n".join(parts)


def save_agent_module(nb_path: Path) -> Path | None:
    code = extract_notebook(nb_path)
    if "def agent" not in code and "def build_agent" not in code:
        return None
    # strip notebook magics / shell
    lines = []
    for line in code.splitlines():
        s = line.strip()
        if s.startswith("!") or s.startswith("%") or s.startswith("get_ipython"):
            continue
        lines.append(line)
    out = OUT_DIR / (nb_path.stem[:40] + ".py")
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def load_agent(path: Path):
    spec = importlib.util.spec_from_file_location(f"p41_{path.stem[:20]}", str(path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    if hasattr(m, "agent"):
        return m.agent
    if hasattr(m, "build_agent"):
        return m.build_agent({})
    raise RuntimeError(f"no agent in {path}")


def load_finn():
    spec = importlib.util.spec_from_file_location("finn_p41", str(ROOT / "reference_agents" / "fallow_finn.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent


def wrap(inner, keys):
    n = getattr(getattr(inner, "__code__", None), "co_argcount", 2)
    if n <= 1:
        def agent(obs):
            a = inner(obs)
            keys.append(json.dumps({"m": a.get("market"), "f": a.get("farmer"), "h": a.get("hands")},
                                   sort_keys=True, default=str))
            return a
    else:
        def agent(obs, configuration=None):
            a = inner(obs, configuration)
            keys.append(json.dumps({"m": a.get("market"), "f": a.get("farmer"), "h": a.get("hands")},
                                   sort_keys=True, default=str))
            return a
    return agent


def run(agent_fn, seed, collect=False):
    finn = load_finn()
    keys = []
    play = wrap(agent_fn, keys) if collect else agent_fn
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    env.run([play, finn])
    bank = float(env.steps[-1][0]["observation"]["farms"][0]["money"])
    h = hashlib.md5("\n".join(keys).encode()).hexdigest()[:16] if keys else ""
    return bank, keys, h


def load_elite(name):
    paths = {
        "R2": ROOT / "_push_medal" / "main.py",
        "kaito_v27": ROOT / "_external" / "public_nb" / "kaito_v27" / "main.py",
        "qeinstein": ROOT / "_external" / "git" / "qeinstein" / "dist" / "sub-009-moev2" / "main.py",
        "rayk_rank": ROOT / "_external" / "public_nb" / "rayk_rank" / "main.py",
    }
    spec = importlib.util.spec_from_file_location(f"el_{name}", str(paths[name]))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.agent if hasattr(m, "agent") else m.build_agent({})


def sim(a, b):
    n = min(len(a), len(b))
    if n == 0:
        return 0.0
    return sum(1 for i in range(n) if a[i] == b[i]) / n


def main():
    t0 = time.time()
    # extract
    mods = []
    for nb in sorted(NB_DIR.glob("*.ipynb")):
        p = save_agent_module(nb)
        if p:
            mods.append((nb.stem, p))
            print(f"extracted {nb.name} -> {p.name}", flush=True)
        else:
            print(f"skip (no agent) {nb.name}", flush=True)

    # elite refs
    print("\n=== ELITE REFS ===", flush=True)
    elite_keys = {}
    for name in ("R2", "kaito_v27", "qeinstein", "rayk_rank"):
        fn = load_elite(name)
        bank, keys, h = run(fn, 1, collect=True)
        elite_keys[name] = keys
        print(f"  {name}: {bank:.0f}", flush=True)

    rows = []
    print("\n=== CANDIDATES ===", flush=True)
    for stem, path in mods:
        try:
            fn = load_agent(path)
        except Exception as e:
            print(f"  LOAD FAIL {stem}: {e}", flush=True)
            rows.append({"name": stem, "status": "load_fail", "bank_s1": None, "error": str(e)[:200]})
            continue
        try:
            bank, keys, h = run(fn, 1, collect=True)
        except Exception as e:
            print(f"  RUN FAIL {stem}: {e}", flush=True)
            rows.append({"name": stem, "status": "run_fail", "bank_s1": None, "error": str(e)[:200]})
            continue
        sims = {n: sim(keys, elite_keys[n]) for n in elite_keys}
        nearest = min(sims, key=sims.get)
        rec = {
            "name": stem,
            "status": "ok",
            "bank_s1": bank,
            "tape_hash": h,
            "nearest": nearest,
            "nearest_sim": sims[nearest],
            "sim_R2": sims["R2"],
            "sim_kaito": sims["kaito_v27"],
            "sim_Q": sims["qeinstein"],
            "sim_rayk": sims["rayk_rank"],
            "error": "",
        }
        rows.append(rec)
        flag = "E5?" if bank >= 100000 and sims[nearest] < 0.5 else ("strong" if bank >= 100000 else "weak")
        print(f"  {stem[:36]:36s} bank={bank:8.0f} nearest={nearest}:{sims[nearest]:.3f} {flag}", flush=True)

    # multi-seed for top ok candidates
    ok = [r for r in rows if r.get("status") == "ok" and (r.get("bank_s1") or 0) >= 50000]
    ok.sort(key=lambda r: -r["bank_s1"])
    print(f"\n=== MULTI-SEED top n={min(5,len(ok))} ===", flush=True)
    for rec in ok[:5]:
        path = OUT_DIR / (rec["name"][:40] + ".py")
        # stem mapping: save used stem[:40]
        # find file
        cand = list(OUT_DIR.glob(rec["name"][:20] + "*"))
        if not cand:
            # fallback by name prefix
            cand = [p for p in OUT_DIR.glob("*.py") if rec["name"][:12] in p.name]
        if not cand:
            continue
        fn = load_agent(cand[0])
        banks = [rec["bank_s1"]]
        for s in (2, 3):
            b, _, _ = run(fn, s)
            banks.append(b)
        rec["bank_s2"] = banks[1]
        rec["bank_s3"] = banks[2]
        rec["mean3"] = sum(banks) / 3
        print(f"  {rec['name'][:36]:36s} mean3={rec['mean3']:.0f} {banks}", flush=True)

    out = ROOT / "p41_external_scan.csv"
    fields = sorted({k for r in rows for k in r})
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"\nwrote {out.name} dt={time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
