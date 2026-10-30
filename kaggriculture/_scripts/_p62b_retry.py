# -*- coding: utf-8 -*-
"""P62b: retry load-failed notebooks with richer display stubs + writefile extract."""
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
OUT = ROOT / "_external" / "p62b_extracted"
OUT.mkdir(exist_ok=True)
FINN = ROOT / "reference_agents" / "fallow_finn.py"
ALPEREN = ROOT / "_external" / "p51_extracted2" / "kaggriculture_metacounter_r1_scored_agent.py"
SEEDS = (1, 2, 3)

STUB = '''
class _Anything:
    def __init__(self, *a, **k): pass
    def __call__(self, *a, **k): return self
    def __getattr__(self, n): return self
    def __iter__(self): return iter(())
    def __enter__(self): return self
    def __exit__(self, *a): return False

def display(*a, **k):
    pass

class HTML(str):
    def __init__(self, *a, **k):
        pass

class FileLink(str):
    def __init__(self, *a, **k):
        pass

class Markdown(str):
    def __init__(self, *a, **k):
        pass

def clear_output(*a, **k):
    pass

_IPYTHON = _Anything()
'''

DROP = re.compile(
    r"^\s*(!|%)|get_ipython|^\s*from IPython|^\s*import IPython|ipywidgets|"
    r"^\s*from ipykernel|^\s*import matplotlib|^\s*from matplotlib|"
    r"^\s*import seaborn|^\s*from PIL|^\s*import cv2"
)


def clean(code: str) -> str:
    lines = [ln for ln in code.splitlines() if not DROP.search(ln)]
    text = "\n".join(lines)
    futures = re.findall(r"^from __future__ import .+$", text, flags=re.M)
    text = re.sub(r"^from __future__ import .+\n?", "", text, flags=re.M)
    head = ("\n".join(futures) + "\n") if futures else ""
    # soft-fail integrity asserts
    text = re.sub(r"^\s*assert .*(integrity|sha256|main\.py).*$", "  pass", text, flags=re.M)
    return head + STUB + text


def extract_file(path: Path):
    if path.suffix == ".py":
        raw = path.read_text(encoding="utf-8", errors="replace")
    else:
        nb = json.loads(path.read_text(encoding="utf-8"))
        parts = []
        for c in nb.get("cells", []):
            if c.get("cell_type") != "code":
                continue
            src = "".join(c.get("source") or [])
            src = re.sub(r"^%%writefile[^\n]*\n", "", src)
            parts.append(src)
        raw = "\n\n".join(parts)
    code = clean(raw)
    has = "def agent" in code or "def build_agent" in code
    return code, has


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


RETRY = [
    "farming-score-v4-a-better-shop.ipynb",
    "harvestforge-x-high-throughput-farming.ipynb",
    "kaggriculture-frontier-the-moon-counts-melons.ipynb",
    "kaggriculture-v43-recovering-lost-harvests.ipynb",
    "kaggriculture-v6.ipynb",
    "kaggriculture-route-replay-agent.ipynb",
    "kaggriculture-terminal-logistics.ipynb",
]


def main():
    rows = []
    for fname in RETRY:
        src = NB / fname
        if not src.exists():
            print("missing", fname, flush=True)
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
            fn = load_quiet(out, f"c62b_{name[:14]}")
        except Exception as e:
            print(f"  LOAD FAIL {type(e).__name__}: {str(e)[:140]}", flush=True)
            rows.append({"name": name, "status": "load_fail", "error": str(e)[:160]})
            continue

        banks = []
        for seed in SEEDS:
            try:
                b0, b1 = run(fn, load_quiet(FINN, f"f{seed}a"), seed)
                c0, c1 = run(load_quiet(FINN, f"f{seed}b"), fn, seed)
                our = (b0 + c1) / 2
                banks.append(our)
                print(f"  finn s{seed}: {our:.0f}", flush=True)
            except Exception as e:
                print(f"  RUN FAIL s{seed} {str(e)[:100]}", flush=True)
                banks = []
                break
        if not banks:
            rows.append({"name": name, "status": "run_fail"})
            continue
        mean = sum(banks) / len(banks)
        print(f"  finn mean={mean:.0f}", flush=True)
        rec = {"name": name, "status": "ok", "finn_mean": mean}
        if mean >= 150000:
            w = d = l = 0
            for seed in SEEDS:
                a0, a1 = run(fn, load_quiet(ALPEREN, f"a{seed}a"), seed)
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
        rows.append(rec)

    with open(ROOT / "p62b_retry.csv", "w", newline="", encoding="utf-8") as f:
        fields = sorted({k for r in rows for k in r})
        wri = csv.DictWriter(f, fieldnames=fields)
        wri.writeheader()
        wri.writerows(rows)
    print("wrote p62b_retry.csv", flush=True)


if __name__ == "__main__":
    main()
