# -*- coding: utf-8 -*-
"""P67b: decode embedded submission archives from high-score notebooks."""
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

NB = ROOT / "_external" / "p67_lineage_nb"
OUT = ROOT / "_external" / "p67b_main"
OUT.mkdir(exist_ok=True)
FINN = ROOT / "reference_agents" / "fallow_finn.py"
ALPEREN = ROOT / "_external" / "p51_extracted2" / "kaggriculture_metacounter_r1_scored_agent.py"
KNOWN = {
    "alperen": ALPEREN,
    "guru": ROOT / "_external" / "p51_extracted2" / "kaggriculture_fully_dynamic_autonomous_agent.py",
    "R2": ROOT / "_push_medal" / "main.py",
}


def load_quiet(path, tag):
    spec = importlib.util.spec_from_file_location(tag, str(path))
    m = importlib.util.module_from_spec(spec)
    with redirect_stdout(io.StringIO()):
        spec.loader.exec_module(m)
    return m.agent if hasattr(m, "agent") else m.build_agent({})


def play_wrap(inner):
    n = getattr(getattr(inner, "__code__", None), "co_argcount", 2)
    if n <= 1:
        def agent(obs):
            return inner(obs)
    else:
        def agent(obs, configuration=None):
            return inner(obs, configuration)
    return agent


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
    finn = load_quiet(FINN, f"f67b_{id(object())}")
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    env.info = {"seed": int(seed)}
    env.run([wrap, play_wrap(finn)])
    bank = float(env.steps[-1][0]["observation"]["farms"][0]["money"])
    h = hashlib.md5("\n".join(keys).encode()).hexdigest()[:12]
    return keys, bank, h


def sim(a, b):
    n = min(len(a), len(b))
    return sum(1 for i in range(n) if a[i] == b[i]) / n if n else 0.0


def extract_from_nb(path: Path):
    """Find base64 payloads and extract main.py from tar/gzip/zlib."""
    nb = json.loads(path.read_text(encoding="utf-8"))
    src = "\n".join("".join(c.get("source") or []) for c in nb.get("cells", []) if c.get("cell_type") == "code")
    # gather long quoted strings that look like b64
    blobs = re.findall(r"[\"']([A-Za-z0-9+/=\-_]{200,})[\"']", src)
    blobs += re.findall(r"PAYLOAD\s*=\s*[\"']([^\"']+)[\"']", src)
    # also join parenthesized string lists
    m = re.search(r"ARCHIVE_B64\s*=\s*\((.*?)\)", src, flags=re.S)
    if m:
        parts = re.findall(r"[\"']([^\"']+)[\"']", m.group(1))
        blobs.append("".join(parts))
    m = re.search(r"_AGENT_B64_PARTS\s*=\s*\[(.*?)\]", src, flags=re.S)
    if m:
        parts = re.findall(r"[\"']([^\"']+)[\"']", m.group(1))
        blobs.append("".join(parts))
    # zlib+b85 SOURCE
    m = re.search(r"SOURCE_B85\s*=\s*[\"']([^\"']+)[\"']", src, flags=re.S)
    if m:
        blobs.append("B85:" + m.group(1))

    out_dir = OUT / path.stem[:40]
    out_dir.mkdir(exist_ok=True)
    found = []
    for i, blob in enumerate(blobs):
        if blob.startswith("B85:"):
            raw = base64.b85decode(blob[4:].encode())
        else:
            try:
                raw = base64.b64decode(blob)
            except Exception:
                continue
        # try zlib then tar
        for decoder in ("raw", "zlib"):
            data = raw
            if decoder == "zlib":
                try:
                    data = zlib.decompress(raw)
                except Exception:
                    continue
            # tar?
            try:
                bio = io.BytesIO(data)
                if tarfile.is_tarfile(bio):
                    bio.seek(0)
                    with tarfile.open(fileobj=bio) as tf:
                        for m in tf.getmembers():
                            if m.name.endswith("main.py") or m.name.endswith(".py"):
                                f = tf.extractfile(m)
                                if f:
                                    text = f.read().decode("utf-8", errors="replace")
                                    dest = out_dir / Path(m.name).name
                                    dest.write_text(text, encoding="utf-8")
                                    found.append(dest)
                    break
            except Exception:
                pass
            # plain python?
            try:
                text = data.decode("utf-8")
                if "def agent" in text or "def build_agent" in text:
                    dest = out_dir / f"payload_{i}.py"
                    dest.write_text(text, encoding="utf-8")
                    found.append(dest)
                    break
            except Exception:
                pass
    return found


def main():
    print("known fp", flush=True)
    known_keys = {}
    for n, p in KNOWN.items():
        keys, bank, h = tape_keys(load_quiet(p, f"knb_{n}"), 1)
        known_keys[n] = keys
        print(f"  {n} finn={bank:.0f} hash={h}", flush=True)

    rows = []
    for nb in sorted(NB.glob("*.ipynb")):
        print(f"\n=== {nb.name} ===", flush=True)
        files = extract_from_nb(nb)
        print(f"  extracted {len(files)} python files", flush=True)
        for f in files:
            print(f"  try {f.name} {f.stat().st_size}", flush=True)
            try:
                fn = load_quiet(f, f"e_{f.stem[:16]}")
            except Exception as e:
                print(f"    LOAD FAIL {str(e)[:100]}", flush=True)
                rows.append({"nb": nb.name, "file": f.name, "status": "load_fail"})
                continue
            try:
                keys, bank_s1, h = tape_keys(fn, 1)
            except Exception as e:
                print(f"    TAPE FAIL {str(e)[:100]}", flush=True)
                rows.append({"nb": nb.name, "file": f.name, "status": "tape_fail"})
                continue
            sims = {n: sim(keys, known_keys[n]) for n in known_keys}
            nearest = max(sims, key=sims.get)
            print(f"    finn_s1={bank_s1:.0f} hash={h} nearest={nearest}:{sims[nearest]:.3f}", flush=True)
            rec = {"nb": nb.name, "file": f.name, "status": "ok", "finn_s1": bank_s1,
                   "hash": h, "nearest": nearest, "nearest_sim": sims[nearest],
                   **{f"sim_{k}": v for k, v in sims.items()}}
            if sims[nearest] >= 0.95:
                rec["status"] = "known_family"
                print("    REJECT known", flush=True)
                rows.append(rec)
                continue
            if bank_s1 < 120000:
                rec["status"] = "weak_finn"
                rows.append(rec)
                continue
            banks = [bank_s1]
            for seed in (2, 3):
                _, b, _ = tape_keys(fn, seed)
                banks.append(b)
            mean = sum(banks) / len(banks)
            rec["finn_mean"] = mean
            print(f"    finn mean3={mean:.0f}", flush=True)
            if mean < 150000:
                rec["status"] = "weak_mean"
                rows.append(rec)
                continue
            w = d = l = 0
            for seed in (1, 2, 3):
                a0, a1 = run(fn, load_quiet(ALPEREN, f"al{seed}"), seed)
                b0, b1 = run(load_quiet(ALPEREN, f"al{seed}b"), fn, seed)
                our = (a0 + b1) / 2
                theirs = (a1 + b0) / 2
                if our > theirs + 1:
                    w += 1
                elif theirs > our + 1:
                    l += 1
                else:
                    d += 1
                print(f"    alp s{seed}: us={our:.0f} alp={theirs:.0f}", flush=True)
            rec.update({"vs_alp_W": w, "vs_alp_D": d, "vs_alp_L": l, "vs_alp_WL": w - l,
                        "status": "h2h_done"})
            print(f"    vs alperen {w}-{d}-{l}", flush=True)
            rows.append(rec)

    with open(ROOT / "p67b_embedded_eval.csv", "w", newline="", encoding="utf-8") as f:
        fields = sorted({k for r in rows for k in r})
        wri = csv.DictWriter(f, fieldnames=fields)
        wri.writeheader()
        wri.writerows(rows)
    print("\nSUMMARY", flush=True)
    for r in rows:
        print(f"  {r['nb'][:30]} {r['file'][:24]} {r['status']} "
              f"finn={r.get('finn_mean') or r.get('finn_s1')} alpWL={r.get('vs_alp_WL','-')} "
              f"sim={r.get('nearest_sim','-')}", flush=True)
    print("wrote p67b_embedded_eval.csv", flush=True)


if __name__ == "__main__":
    main()
