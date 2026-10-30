# -*- coding: utf-8 -*-
"""P66b: fingerprint-first recon. Known family → reject before H2H."""
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

NB_DIRS = [
    ROOT / "_external" / "p66_recon_nb",
    ROOT / "_external" / "p62_medal_nb",
]
OUT = ROOT / "_external" / "p66b_extracted"
OUT.mkdir(exist_ok=True)
FINN = ROOT / "reference_agents" / "fallow_finn.py"
KNOWN = {
    "alperen": ROOT / "_external" / "p51_extracted2" / "kaggriculture_metacounter_r1_scored_agent.py",
    "guru": ROOT / "_external" / "p51_extracted2" / "kaggriculture_fully_dynamic_autonomous_agent.py",
    "R2": ROOT / "_push_medal" / "main.py",
    "V16": ROOT / "_external" / "p41_extracted" / "salem_2900_main.py",
}
SKIP_NAMES = {
    "kaggriculture_shop_router_reactive_v6",  # known guru family
    "farming_score_v4_a_better_shop",
    "kaggriculture_v6",
    "kaggriculture_route_replay_agent",
    "score2710_t23_kaggriculture_smart_harvest",
}

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
    if path.suffix == ".py":
        raw = path.read_text(encoding="utf-8", errors="replace")
        return raw, "def agent" in raw or "def build_agent" in raw
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


def tape_keys(fn, seed=1):
    keys = []

    def wrap(obs, configuration=None):
        a = fn(obs, configuration)
        keys.append(json.dumps({"m": a.get("market"), "f": a.get("farmer"), "h": a.get("hands")},
                               sort_keys=True, default=str))
        return a

    finn = load_quiet(FINN, f"fp_fn_{id(object())}")
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    env.run([wrap, finn])
    bank = float(env.steps[-1][0]["observation"]["farms"][0]["money"])
    h = hashlib.md5("\n".join(keys).encode()).hexdigest()[:12]
    return keys, bank, h


def sim(a, b):
    n = min(len(a), len(b))
    if n == 0:
        return 0.0
    return sum(1 for i in range(n) if a[i] == b[i]) / n


def run(a0, a1, seed):
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    env.run([a0, a1])
    f = env.steps[-1]
    return (
        float(f[0]["observation"]["farms"][0]["money"]),
        float(f[1]["observation"]["farms"][1]["money"]),
    )


def main():
    # known fingerprints
    known_keys = {}
    print("loading known families...", flush=True)
    for n, p in KNOWN.items():
        try:
            keys, bank, h = tape_keys(load_quiet(p, f"kn_{n}"), 1)
            known_keys[n] = keys
            print(f"  {n}: finn_s1={bank:.0f} hash={h}", flush=True)
        except Exception as e:
            print(f"  {n} fail {e}", flush=True)

    rows = []
    for nbd in NB_DIRS:
        if not nbd.exists():
            continue
        for src in sorted(nbd.iterdir()):
            if src.suffix not in (".ipynb", ".py"):
                continue
            name = re.sub(r"[^a-zA-Z0-9]+", "_", src.stem)[:48]
            if name in SKIP_NAMES:
                print(f"\n=== {name} SKIP known ===", flush=True)
                rows.append({"name": name, "status": "known_skip"})
                continue
            code, has = extract_main(src)
            out = OUT / f"{name}.py"
            out.write_text(code, encoding="utf-8")
            print(f"\n=== {name} agent={has} ===", flush=True)
            if not has:
                rows.append({"name": name, "status": "no_agent"})
                continue
            try:
                fn = load_quiet(out, f"r66_{name[:12]}")
            except Exception as e:
                print(f"  LOAD FAIL {str(e)[:100]}", flush=True)
                rows.append({"name": name, "status": "load_fail"})
                continue
            try:
                keys, bank_s1, h = tape_keys(fn, 1)
            except Exception as e:
                print(f"  TAPE FAIL {str(e)[:100]}", flush=True)
                rows.append({"name": name, "status": "tape_fail"})
                continue
            sims = {n: sim(keys, known_keys[n]) for n in known_keys if n in known_keys}
            nearest = max(sims, key=sims.get) if sims else "?"
            nsim = sims.get(nearest, 0)
            print(f"  finn_s1={bank_s1:.0f} hash={h} nearest={nearest}:{nsim:.3f} all={ {k:round(v,3) for k,v in sims.items()} }", flush=True)
            rec = {"name": name, "status": "ok", "finn_s1": bank_s1, "hash": h,
                   "nearest": nearest, "nearest_sim": nsim,
                   **{f"sim_{k}": v for k, v in sims.items()}}
            if nsim >= 0.95:
                rec["status"] = "known_family"
                print("  REJECT known lineage", flush=True)
                rows.append(rec)
                continue
            if bank_s1 < 120000:
                rec["status"] = "weak_finn"
                print("  REJECT weak finn", flush=True)
                rows.append(rec)
                continue
            # finn mean3
            banks = [bank_s1]
            for seed in (2, 3):
                try:
                    _, b, _ = tape_keys(fn, seed)
                    banks.append(b)
                except Exception:
                    break
            mean = sum(banks) / len(banks)
            rec["finn_mean"] = mean
            print(f"  finn mean{len(banks)}={mean:.0f}", flush=True)
            if mean < 150000:
                rec["status"] = "weak_finn_mean"
                rows.append(rec)
                continue
            # H2H vs alperen only if new + strong
            w = d = l = 0
            for seed in (1, 2, 3):
                a0, a1 = run(fn, load_quiet(KNOWN["alperen"], f"a{seed}"), seed)
                b0, b1 = run(load_quiet(KNOWN["alperen"], f"a{seed}b"), fn, seed)
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

    with open(ROOT / "p66b_fingerprint_recon.csv", "w", newline="", encoding="utf-8") as f:
        fields = sorted({k for r in rows for k in r})
        wri = csv.DictWriter(f, fieldnames=fields)
        wri.writeheader()
        wri.writerows(rows)
    print("\n=== SUMMARY ===", flush=True)
    for r in rows:
        if r.get("status") in ("ok", "h2h_done", "known_family", "weak_finn", "weak_finn_mean"):
            print(f"  {r['name'][:42]:42s} {r['status']:14s} "
                  f"finn={r.get('finn_mean') or r.get('finn_s1')} "
                  f"alpWL={r.get('vs_alp_WL', '-')} sim={r.get('nearest_sim', '-')}", flush=True)
    print("wrote p66b_fingerprint_recon.csv", flush=True)


if __name__ == "__main__":
    main()
