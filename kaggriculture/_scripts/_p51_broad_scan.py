# -*- coding: utf-8 -*-
"""Extract agents from notebooks and screen vs finn (3 seeds, both seats)."""
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

NB = ROOT / "_external" / "p51_candidates_nb"
OUT = ROOT / "_external" / "p51_extracted2"
OUT.mkdir(exist_ok=True)
FINN = ROOT / "reference_agents" / "fallow_finn.py"
R2 = ROOT / "_push_medal" / "main.py"
SEEDS = (1, 2, 3)

DROP = re.compile(r"^\s*(!|%)|get_ipython|^\s*from IPython|^\s*import IPython|ipywidgets")


def clean(code: str) -> str:
    lines = []
    for line in code.splitlines():
        if DROP.search(line):
            continue
        lines.append(line)
    text = "\n".join(lines)
    futures = re.findall(r"^from __future__ import .+$", text, flags=re.M)
    text = re.sub(r"^from __future__ import .+\n?", "", text, flags=re.M)
    head = ("\n".join(futures) + "\n") if futures else ""
    return head + "def display(*a, **k):\n    pass\n\n" + text


def extract_file(path: Path):
    if path.suffix == ".py":
        return clean(path.read_text(encoding="utf-8", errors="replace")), True
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
    if hasattr(m, "agent"):
        return m.agent
    return m.build_agent({})


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
        code, has = extract_file(src)
        out = OUT / f"{name}.py"
        out.write_text(code, encoding="utf-8")
        print(f"\n=== {name} agent={has} chars={len(code)} ===", flush=True)
        if not has:
            rows.append({"name": name, "status": "no_agent"})
            continue
        try:
            fn = load_quiet(out, f"e2_{name[:16]}")
        except Exception as e:
            print(f"  LOAD FAIL {type(e).__name__}: {str(e)[:120]}", flush=True)
            rows.append({"name": name, "status": "load_fail", "error": str(e)[:160]})
            continue

        banks = []
        w = d = l = 0
        try:
            for seed in SEEDS:
                finn0 = load_quiet(FINN, f"f0_{name[:10]}_{seed}")
                b0, b1 = run(fn, finn0, seed)
                finn1 = load_quiet(FINN, f"f1_{name[:10]}_{seed}")
                c0, c1 = run(finn1, fn, seed)
                our = (b0 + c1) / 2
                banks.append(our)
                if our > 3000 + 1:
                    w += 1
                else:
                    l += 1
                print(f"  vs finn s{seed}: {our:.0f}", flush=True)
        except Exception as e:
            print(f"  RUN FAIL {type(e).__name__}: {str(e)[:120]}", flush=True)
            rows.append({"name": name, "status": "run_fail", "error": str(e)[:160]})
            continue

        mean = sum(banks) / len(banks)
        print(f"  vs finn mean={mean:.0f} W={w} L={l}", flush=True)
        rec = {"name": name, "status": "ok", "finn_mean": mean, "finn_W": w, "finn_L": l}
        # only H2H vs R2 if strong vs finn
        if mean >= 140000:
            try:
                r2fn = load_quiet(R2, f"r2e2_{name[:12]}")
                rw = rd = rl = 0
                rbanks = []
                for seed in SEEDS:
                    a0, a1 = run(fn, r2fn, seed)
                    b0, b1 = run(r2fn, fn, seed)
                    our = (a0 + b1) / 2
                    theirs = (a1 + b0) / 2
                    rbanks.append(our)
                    if our > theirs + 1:
                        rw += 1
                        res = "W"
                    elif theirs > our + 1:
                        rl += 1
                        res = "L"
                    else:
                        rd += 1
                        res = "D"
                    print(f"  vs R2 s{seed}: us={our:.0f} r2={theirs:.0f} {res}", flush=True)
                rec.update({
                    "vs_R2_W": rw, "vs_R2_D": rd, "vs_R2_L": rl,
                    "vs_R2_WL": rw - rl, "vs_R2_mean": sum(rbanks) / len(rbanks),
                })
            except Exception as e:
                print(f"  R2 FAIL {str(e)[:100]}", flush=True)
        rows.append(rec)

    out_csv = ROOT / "p51_broad_scan.csv"
    fields = sorted({k for r in rows for k in r})
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        wri = csv.DictWriter(f, fieldnames=fields)
        wri.writeheader()
        wri.writerows(rows)

    print("\n=== SUMMARY (sorted by finn_mean) ===", flush=True)
    ok = [r for r in rows if r.get("finn_mean")]
    ok.sort(key=lambda r: -r["finn_mean"])
    for r in ok:
        r2s = r.get("vs_R2_WL")
        print(f"  {r['name'][:40]:40s} finn={r['finn_mean']:.0f} "
              f"vsR2_WL={r2s if r2s is not None else '-'}", flush=True)
    print("wrote", out_csv.name, flush=True)


if __name__ == "__main__":
    main()
