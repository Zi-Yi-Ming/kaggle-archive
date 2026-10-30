# -*- coding: utf-8 -*-
"""P70b: rebuild multi-cell %%writefile main.py stacks (2312, 2820, jaxa)."""
from __future__ import annotations

import base64
import csv
import hashlib
import importlib.util
import io
import json
import re
import sys
import tarfile
import zlib
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(ROOT))
from kaggle_environments import make  # noqa: E402

NB = ROOT / "_external" / "p70_learning_nb"
OUT = ROOT / "_external" / "p70b_main"
OUT.mkdir(exist_ok=True)
FINN = ROOT / "reference_agents" / "fallow_finn.py"
ALPEREN = ROOT / "_external" / "p51_extracted2" / "kaggriculture_metacounter_r1_scored_agent.py"

STUB = '''def display(*a, **k):
    pass

class HTML(str):
    def __init__(self, *a, **k):
        pass
'''


def play_wrap(inner):
    n = getattr(getattr(inner, "__code__", None), "co_argcount", 2)
    if n <= 1:
        def agent(obs):
            return inner(obs)
    else:
        def agent(obs, configuration=None):
            return inner(obs, configuration)
    return agent


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
    env.run([play_wrap(a0), play_wrap(a1)])
    f = env.steps[-1]
    return (
        float(f[0]["observation"]["farms"][0]["money"]),
        float(f[1]["observation"]["farms"][1]["money"]),
    )


def rebuild_writefile_stack(nb_path: Path):
    """Concatenate all %%writefile main.py and %%writefile -a main.py cells."""
    nb = json.loads(nb_path.read_text(encoding="utf-8"))
    parts = []
    for c in nb.get("cells", []):
        if c.get("cell_type") != "code":
            continue
        src = "".join(c.get("source") or [])
        m = re.match(r"^%%writefile(\s+-a)?\s+main\.py\n", src)
        if m:
            body = re.sub(r"^%%writefile[^\n]*\n", "", src)
            parts.append(body)
    if not parts:
        return None
    code = STUB + "\n\n".join(parts)
    return code


def extract_tar_main(nb_path: Path):
    nb = json.loads(nb_path.read_text(encoding="utf-8"))
    src = "\n".join("".join(c.get("source") or []) for c in nb.get("cells", []) if c.get("cell_type") == "code")
    # ARCHIVE_B64 style
    m = re.search(r"ARCHIVE_B64\s*=\s*\((.*?)\)", src, flags=re.S)
    blobs = []
    if m:
        parts = re.findall(r"[\"']([^\"']+)[\"']", m.group(1))
        blobs.append("".join(parts))
    # long quoted strings
    blobs += re.findall(r"[\"']([A-Za-z0-9+/=\-_]{500,})[\"']", src)
    for i, blob in enumerate(blobs):
        try:
            raw = base64.b64decode(blob)
        except Exception:
            continue
        for decoder in ("raw", "zlib", "gzip"):
            data = raw
            try:
                if decoder == "zlib":
                    data = zlib.decompress(raw)
                elif decoder == "gzip":
                    data = zlib.decompress(raw, 16 + zlib.MAX_WBITS)
            except Exception:
                continue
            try:
                bio = io.BytesIO(data)
                if tarfile.is_tarfile(bio):
                    bio.seek(0)
                    with tarfile.open(fileobj=bio) as tf:
                        for mem in tf.getmembers():
                            if mem.name.endswith("main.py"):
                                f = tf.extractfile(mem)
                                if f:
                                    return f.read().decode("utf-8", errors="replace")
            except Exception:
                pass
            try:
                text = data.decode("utf-8")
                if "def agent" in text:
                    return text
            except Exception:
                pass
    return None


def eval_agent(code: Path, name: str):
    try:
        fn = load_quiet(code, f"p70b_{name[:12]}")
    except Exception as e:
        print(f"  LOAD FAIL {str(e)[:120]}", flush=True)
        return {"name": name, "status": "load_fail", "error": str(e)[:140]}
    banks = []
    try:
        for seed in (1, 2, 3):
            a0, _ = run(fn, load_quiet(FINN, f"f_{seed}"), seed)
            banks.append(a0)
            print(f"  finn s{seed}: {a0:.0f}", flush=True)
    except Exception as e:
        print(f"  RUN FAIL {str(e)[:100]}", flush=True)
        return {"name": name, "status": "run_fail"}
    mean = sum(banks) / len(banks)
    rec = {"name": name, "status": "ok", "finn_mean": mean}
    print(f"  finn mean3={mean:.0f}", flush=True)
    if mean < 150000:
        rec["status"] = "weak_mean"
        return rec
    w = d = l = 0
    for seed in (1, 2, 3):
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
    rec.update({"vs_alp_W": w, "vs_alp_D": d, "vs_alp_L": l, "vs_alp_WL": w - l, "status": "h2h"})
    print(f"  vs alperen {w}-{d}-{l}", flush=True)
    return rec


def main():
    rows = []
    jobs = [
        ("2312_q30", "kaggriculture-2312-9-q30-v2a.ipynb", "stack"),
        ("2820_v44y", "kaggriculture-2820-score.ipynb", "stack"),
        ("jaxa_2802", "2802-two-identical-agents-90-points-apart.ipynb", "tar"),
        ("auto_top1", "kaggriculture-auto-top1.ipynb", "tar"),
    ]
    for name, fname, kind in jobs:
        print(f"\n=== {name} ===", flush=True)
        path = NB / fname
        if kind == "stack":
            code = rebuild_writefile_stack(path)
        else:
            code = extract_tar_main(path)
        if not code:
            print("  no code", flush=True)
            rows.append({"name": name, "status": "no_code"})
            continue
        out = OUT / f"{name}_main.py"
        out.write_text(code, encoding="utf-8")
        print(f"  wrote {out.name} bytes={len(code)} agent={'def agent' in code}", flush=True)
        rec = eval_agent(out, name)
        rows.append(rec)

    with open(ROOT / "p70b_stack_eval.csv", "w", newline="", encoding="utf-8") as f:
        fields = sorted({k for r in rows for k in r})
        wri = csv.DictWriter(f, fieldnames=fields)
        wri.writeheader()
        wri.writerows(rows)
    print("\nSUMMARY", flush=True)
    for r in rows:
        print(r, flush=True)


if __name__ == "__main__":
    main()
