# -*- coding: utf-8 -*-
"""P62 medal recon: extract, screen vs finn, then H2H vs alperen if strong."""
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

NB = ROOT / "_external" / "p62_medal_nb"
OUT = ROOT / "_external" / "p62_extracted"
OUT.mkdir(exist_ok=True)
FINN = ROOT / "reference_agents" / "fallow_finn.py"
ALPEREN = ROOT / "_external" / "p51_extracted2" / "kaggriculture_metacounter_r1_scored_agent.py"
SEEDS = (1, 2, 3)

DROP = re.compile(r"^\s*(!|%)|get_ipython|^\s*from IPython|^\s*import IPython|ipywidgets")


def clean(code: str) -> str:
    lines = [ln for ln in code.splitlines() if not DROP.search(ln)]
    text = "\n".join(lines)
    futures = re.findall(r"^from __future__ import .+$", text, flags=re.M)
    text = re.sub(r"^from __future__ import .+\n?", "", text, flags=re.M)
    head = ("\n".join(futures) + "\n") if futures else ""
    return head + "def display(*a, **k):\n    pass\n\n" + text


def extract_file(path: Path):
    if path.suffix == ".py":
        return clean(path.read_text(encoding="utf-8", errors="replace")), "def agent" in path.read_text(encoding="utf-8", errors="replace")
    nb = json.loads(path.read_text(encoding="utf-8"))
    parts = []
    for c in nb.get("cells", []):
        if c.get("cell_type") != "code":
            continue
        src = "".join(c.get("source") or [])
        src = re.sub(r"^%%writefile[^\n]*\n", "", src)
        parts.append(src)
    code = clean("\n\n".join(parts))
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


def vs_finn(make_fn, seeds):
    banks = []
    w = l = 0
    for seed in seeds:
        b0, b1 = run(make_fn(), load_quiet(FINN, f"f_{seed}a"), seed)
        c0, c1 = run(load_quiet(FINN, f"f_{seed}b"), make_fn(), seed)
        our = (b0 + c1) / 2
        banks.append(our)
        if our > 3001:
            w += 1
        else:
            l += 1
        print(f"    finn s{seed}: {our:.0f}", flush=True)
    return sum(banks) / len(banks), w, l


def vs_alperen(make_fn, seeds):
    w = d = l = 0
    banks = []
    for seed in seeds:
        a0, a1 = run(make_fn(), load_quiet(ALPEREN, f"a_{seed}a"), seed)
        b0, b1 = run(load_quiet(ALPEREN, f"a_{seed}b"), make_fn(), seed)
        our = (a0 + b1) / 2
        theirs = (a1 + b0) / 2
        banks.append(our)
        if our > theirs + 1:
            w += 1
            res = "W"
        elif theirs > our + 1:
            l += 1
            res = "L"
        else:
            d += 1
            res = "D"
        print(f"    alp s{seed}: us={our:.0f} alp={theirs:.0f} {res}", flush=True)
    return w, d, l, sum(banks) / len(banks) if banks else 0


def main():
    rows = []
    for src in sorted(NB.iterdir()):
        if src.suffix not in (".ipynb", ".py"):
            continue
        name = re.sub(r"[^a-zA-Z0-9]+", "_", src.stem)[:48]
        code, has = extract_file(src)
        out = OUT / f"{name}.py"
        out.write_text(code, encoding="utf-8")
        print(f"\n=== {name} agent={has} ===", flush=True)
        if not has:
            rows.append({"name": name, "status": "no_agent"})
            continue
        try:
            def make(path=out, name=name):
                return load_quiet(path, f"c62_{name[:16]}_{id(object())}")
            mean, fw, fl = vs_finn(make, SEEDS)
        except Exception as e:
            print(f"  FAIL {type(e).__name__}: {str(e)[:120]}", flush=True)
            rows.append({"name": name, "status": "fail", "error": str(e)[:160]})
            continue
        print(f"  finn mean={mean:.0f}", flush=True)
        rec = {"name": name, "status": "ok", "finn_mean": mean, "finn_W": fw, "finn_L": fl}
        if mean >= 150000:
            try:
                aw, ad, al, am = vs_alperen(make, SEEDS)
                rec.update({"vs_alp_W": aw, "vs_alp_D": ad, "vs_alp_L": al, "vs_alp_WL": aw - al})
                print(f"  vs alperen {aw}-{ad}-{al}", flush=True)
            except Exception as e:
                print(f"  alp FAIL {str(e)[:100]}", flush=True)
        rows.append(rec)

    out_csv = ROOT / "p62_medal_scan.csv"
    fields = sorted({k for r in rows for k in r})
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        wri = csv.DictWriter(f, fieldnames=fields)
        wri.writeheader()
        wri.writerows(rows)
    ok = [r for r in rows if r.get("finn_mean")]
    ok.sort(key=lambda r: -r["finn_mean"])
    print("\n=== SUMMARY ===", flush=True)
    for r in ok:
        print(f"  {r['name'][:40]:40s} finn={r['finn_mean']:.0f} "
              f"vs_alp={r.get('vs_alp_WL', '-')}", flush=True)
    print("wrote p62_medal_scan.csv", flush=True)


if __name__ == "__main__":
    main()
