# -*- coding: utf-8 -*-
"""P66 recon: extract writefile mains, screen vs finn, H2H vs alperen."""
from __future__ import annotations

import csv
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

NB = ROOT / "_external" / "p66_recon_nb"
OUT = ROOT / "_external" / "p66_extracted"
OUT.mkdir(exist_ok=True)
FINN = ROOT / "reference_agents" / "fallow_finn.py"
ALPEREN = ROOT / "_external" / "p51_extracted2" / "kaggriculture_metacounter_r1_scored_agent.py"
# recent elites for gate step 2
RECENT = {
    "R2": ROOT / "_push_medal" / "main.py",
    "guru": ROOT / "_external" / "p51_extracted2" / "kaggriculture_fully_dynamic_autonomous_agent.py",
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
    # fallback keep all code cells without stripping mid-block
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
    rows = []
    for src in sorted(NB.iterdir()):
        if src.suffix not in (".ipynb", ".py"):
            continue
        name = re.sub(r"[^a-zA-Z0-9]+", "_", src.stem)[:48]
        code, has = extract_main(src)
        out = OUT / f"{name}.py"
        out.write_text(code, encoding="utf-8")
        print(f"\n=== {name} agent={has} chars={len(code)} ===", flush=True)
        if not has:
            rows.append({"name": name, "status": "no_agent"})
            continue
        try:
            fn = load_quiet(out, f"c66_{name[:14]}")
        except Exception as e:
            print(f"  LOAD FAIL {type(e).__name__}: {str(e)[:120]}", flush=True)
            rows.append({"name": name, "status": "load_fail", "error": str(e)[:140]})
            continue

        banks = []
        ok = True
        for seed in SEEDS:
            try:
                b0, _ = run(fn, load_quiet(FINN, f"f{seed}"), seed)
                _, c1 = run(load_quiet(FINN, f"f{seed}b"), fn, seed)
                banks.append((b0 + c1) / 2)
                print(f"  finn s{seed}: {banks[-1]:.0f}", flush=True)
            except Exception as e:
                print(f"  RUN FAIL {str(e)[:100]}", flush=True)
                ok = False
                break
        if not ok or not banks:
            rows.append({"name": name, "status": "run_fail"})
            continue
        mean = sum(banks) / len(banks)
        rec = {"name": name, "status": "ok", "finn_mean": mean}
        print(f"  finn mean={mean:.0f}", flush=True)

        # always H2H vs alperen if runnable (gate step 1) — even if finn low, skip if fail
        if mean < 100000:
            rows.append(rec)
            continue
        try:
            w = d = l = 0
            for seed in SEEDS:
                a0, a1 = run(fn, load_quiet(ALPEREN, f"a{seed}"), seed)
                b0, b1 = run(load_quiet(ALPEREN, f"a{seed}b"), fn, seed)
                our = (a0 + b1) / 2
                theirs = (a1 + b0) / 2
                if our > theirs + 1:
                    w += 1
                elif theirs > our + 1:
                    l += 1
                else:
                    d += 1
                print(f"  alp s{seed}: us={our:.0f} alp={theirs:.0f}", flush=True)
            rec.update({"vs_alp_W": w, "vs_alp_D": d, "vs_alp_L": l, "vs_alp_WL": w - l})
            print(f"  vs alperen {w}-{d}-{l}", flush=True)
            # step2 if promising
            if w >= 2:
                for rname, rpath in RECENT.items():
                    rw = rd = rl = 0
                    for seed in SEEDS:
                        a0, a1 = run(fn, load_quiet(rpath, f"{rname}{seed}"), seed)
                        b0, b1 = run(load_quiet(rpath, f"{rname}{seed}b"), fn, seed)
                        our = (a0 + b1) / 2
                        theirs = (a1 + b0) / 2
                        if our > theirs + 1:
                            rw += 1
                        elif theirs > our + 1:
                            rl += 1
                        else:
                            rd += 1
                    rec[f"vs_{rname}_WL"] = rw - rl
                    print(f"  vs {rname}: {rw}-{rd}-{rl}", flush=True)
        except Exception as e:
            print(f"  alp FAIL {str(e)[:100]}", flush=True)
        rows.append(rec)

    out_csv = ROOT / "p66_recon_scan.csv"
    fields = sorted({k for r in rows for k in r})
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        wri = csv.DictWriter(f, fieldnames=fields)
        wri.writeheader()
        wri.writerows(rows)
    ok = [r for r in rows if r.get("finn_mean")]
    ok.sort(key=lambda r: -r["finn_mean"])
    print("\n=== SUMMARY ===", flush=True)
    for r in ok:
        print(f"  {r['name'][:40]:40s} finn={r['finn_mean']:.0f} alpWL={r.get('vs_alp_WL','-')} "
              f"R2={r.get('vs_R2_WL','-')} guru={r.get('vs_guru_WL','-')}", flush=True)
    print("wrote p66_recon_scan.csv", flush=True)


if __name__ == "__main__":
    main()
