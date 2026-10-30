# -*- coding: utf-8 -*-
"""P67: fingerprint-first latest lineage hunt."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import json
import re
import sys
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

NB = ROOT / "_external" / "p67_lineage_nb"
OUT = ROOT / "_external" / "p67_extracted"
OUT.mkdir(exist_ok=True)
FINN = ROOT / "reference_agents" / "fallow_finn.py"
KNOWN = {
    "alperen": ROOT / "_external" / "p51_extracted2" / "kaggriculture_metacounter_r1_scored_agent.py",
    "guru": ROOT / "_external" / "p51_extracted2" / "kaggriculture_fully_dynamic_autonomous_agent.py",
    "R2": ROOT / "_push_medal" / "main.py",
    "V16": ROOT / "_external" / "p41_extracted" / "salem_2900_main.py",
}
SEEDS = (1, 2, 3)

STUB = '''def display(*a, **k):
    pass

class HTML(str):
    def __init__(self, *a, **k):
        pass

class FileLink(str):
    def __init__(self, *a, **k):
        pass
'''


def extract_main(path: Path):
    nb = json.loads(path.read_text(encoding="utf-8"))
    best = None
    for c in nb.get("cells", []):
        if c.get("cell_type") != "code":
            continue
        src = "".join(c.get("source") or [])
        if re.search(r"^%%writefile\s+.*main\.py", src, re.M) or re.search(r"^%%writefile\s+submission\.py", src, re.M):
            src = re.sub(r"^%%writefile[^\n]*\n", "", src)
            best = src
    if best:
        if "def display" not in best and ("display(" in best or "HTML(" in best):
            best = STUB + best
        return best, ("def agent" in best or "def build_agent" in best)
    parts = []
    for c in nb.get("cells", []):
        if c.get("cell_type") != "code":
            continue
        src = "".join(c.get("source") or [])
        src = re.sub(r"^%%writefile[^\n]*\n", "", src)
        keep = []
        for ln in src.splitlines():
            s = ln.strip()
            if s.startswith("!") or s.startswith("%") or s.startswith("get_ipython"):
                continue
            if re.match(r"^(from|import)\s+(IPython|ipywidgets|matplotlib|seaborn)", s):
                continue
            keep.append(ln)
        parts.append("\n".join(keep))
    code = "\n\n".join(parts)
    if "def display" not in code and ("display(" in code or "HTML(" in code):
        code = STUB + code
    return code, ("def agent" in code or "def build_agent" in code)


def load_quiet(path, tag):
    spec = importlib.util.spec_from_file_location(tag, str(path))
    m = importlib.util.module_from_spec(spec)
    with redirect_stdout(io.StringIO()):
        spec.loader.exec_module(m)
    return m.agent if hasattr(m, "agent") else m.build_agent({})


def run_quiet(fn, opp_fn, seed):
    """Call agents with arity-safe wrappers for fingerprint + run."""
    def make_play(inner):
        n = getattr(getattr(inner, "__code__", None), "co_argcount", 2)
        if n <= 1:
            def agent(obs):
                return inner(obs)
        else:
            def agent(obs, configuration=None):
                return inner(obs, configuration)
        return agent

    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    env.run([make_play(fn), make_play(opp_fn)])
    f = env.steps[-1]
    return (
        float(f[0]["observation"]["farms"][0]["money"]),
        float(f[1]["observation"]["farms"][1]["money"]),
    )


def tape_keys(fn, seed=1):
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
    finn = load_quiet(FINN, f"p67fn_{id(object())}")
    nfn = getattr(getattr(finn, "__code__", None), "co_argcount", 2)
    if nfn <= 1:
        def wopp(obs):
            return finn(obs)
        opp = wopp
    else:
        def wopp(obs, configuration=None):
            return finn(obs, configuration)
        opp = wopp
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    env.run([wrap, opp])
    bank = float(env.steps[-1][0]["observation"]["farms"][0]["money"])
    h = hashlib.md5("\n".join(keys).encode()).hexdigest()[:12]
    return keys, bank, h


def sim(a, b):
    n = min(len(a), len(b))
    if n == 0:
        return 0.0
    return sum(1 for i in range(n) if a[i] == b[i]) / n


def main():
    print("known fingerprints", flush=True)
    known_keys = {}
    for n, p in KNOWN.items():
        keys, bank, h = tape_keys(load_quiet(p, f"kn67_{n}"), 1)
        known_keys[n] = keys
        print(f"  {n}: finn_s1={bank:.0f} hash={h}", flush=True)

    rows = []
    for src in sorted(NB.glob("*.ipynb")):
        name = re.sub(r"[^a-zA-Z0-9]+", "_", src.stem)[:48]
        code, has = extract_main(src)
        out = OUT / f"{name}.py"
        out.write_text(code, encoding="utf-8")
        print(f"\n=== {name} agent={has} chars={len(code)} ===", flush=True)
        if not has:
            rows.append({"name": name, "status": "no_agent"})
            continue
        try:
            fn = load_quiet(out, f"c67_{name[:12]}")
        except Exception as e:
            print(f"  LOAD FAIL {type(e).__name__}: {str(e)[:120]}", flush=True)
            rows.append({"name": name, "status": "load_fail", "error": str(e)[:140]})
            continue
        try:
            keys, bank_s1, h = tape_keys(fn, 1)
        except Exception as e:
            print(f"  TAPE FAIL {str(e)[:100]}", flush=True)
            rows.append({"name": name, "status": "tape_fail"})
            continue
        sims = {n: sim(keys, known_keys[n]) for n in known_keys}
        nearest = max(sims, key=sims.get)
        print(f"  finn_s1={bank_s1:.0f} hash={h} nearest={nearest}:{sims[nearest]:.3f}", flush=True)
        rec = {"name": name, "status": "ok", "finn_s1": bank_s1, "hash": h,
               "nearest": nearest, "nearest_sim": sims[nearest],
               **{f"sim_{k}": v for k, v in sims.items()}}
        if sims[nearest] >= 0.95:
            rec["status"] = "known_family"
            print("  REJECT known", flush=True)
            rows.append(rec)
            continue
        if bank_s1 < 120000:
            rec["status"] = "weak_finn"
            print("  REJECT weak", flush=True)
            rows.append(rec)
            continue
        banks = [bank_s1]
        for seed in (2, 3):
            _, b, _ = tape_keys(fn, seed)
            banks.append(b)
        mean = sum(banks) / len(banks)
        rec["finn_mean"] = mean
        print(f"  finn mean3={mean:.0f}", flush=True)
        if mean < 150000:
            rec["status"] = "weak_finn_mean"
            rows.append(rec)
            continue
        w = d = l = 0
        for seed in SEEDS:
            a0, a1 = run_quiet(fn, load_quiet(KNOWN["alperen"], f"a{seed}"), seed)
            b0, b1 = run_quiet(load_quiet(KNOWN["alperen"], f"a{seed}b"), fn, seed)
            our = (a0 + b1) / 2
            theirs = (a1 + b0) / 2
            if our > theirs + 1:
                w += 1
            elif theirs > our + 1:
                l += 1
            else:
                d += 1
            print(f"  alp s{seed}: us={our:.0f} alp={theirs:.0f}", flush=True)
        rec.update({"vs_alp_W": w, "vs_alp_D": d, "vs_alp_L": l, "vs_alp_WL": w - l,
                    "status": "h2h_done"})
        print(f"  vs alperen {w}-{d}-{l}", flush=True)
        rows.append(rec)

    with open(ROOT / "p67_lineage_hunt.csv", "w", newline="", encoding="utf-8") as f:
        fields = sorted({k for r in rows for k in r})
        wri = csv.DictWriter(f, fieldnames=fields)
        wri.writeheader()
        wri.writerows(rows)
    print("\n=== SUMMARY ===", flush=True)
    for r in rows:
        print(f"  {r['name'][:42]:42s} {r.get('status')} "
              f"finn={r.get('finn_mean') or r.get('finn_s1')} "
              f"alpWL={r.get('vs_alp_WL','-')} sim={r.get('nearest_sim','-')}", flush=True)
    print("wrote p67_lineage_hunt.csv", flush=True)


if __name__ == "__main__":
    main()
