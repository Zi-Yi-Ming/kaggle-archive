# -*- coding: utf-8 -*-
"""P75 mass extract + fast smoke vs alperen (seed1 both seats)."""
from __future__ import annotations

import ast
import importlib.util
import io
import json
import re
import sys
import time
from contextlib import redirect_stdout
from pathlib import Path

ROOT_PROJ = Path(r"D:\桌面\Kaggle\kaggriculture")
SCAN = ROOT_PROJ / "_external" / "scan_p75_mass"
SCAN2 = ROOT_PROJ / "_external" / "scan_20260919"
EXTRACT = SCAN / "extracted"
EXTRACT.mkdir(parents=True, exist_ok=True)
ALPEREN = ROOT_PROJ / "_push_alperen" / "main.py"
OUT = ROOT_PROJ / "_research" / "p75_mass_smoke.json"
sys.path.insert(0, str(ROOT_PROJ))
from kaggle_environments import make  # noqa: E402

KNOWN = ("shop-router", "yhay81", "aurax7", "prvsiyan", "v11E", "cleo_v11", "alperen_meta")


def cell_text(nb_path: Path) -> str:
    nb = json.loads(nb_path.read_text(encoding="utf-8"))
    parts = []
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        src = cell.get("source", [])
        parts.append("".join(src) if isinstance(src, list) else str(src))
    return "\n".join(parts)


def decode_escapes(text: str) -> str:
    if text.count("\\n") > 20 and "\n" not in text[:200]:
        try:
            return text.encode("utf-8").decode("unicode_escape")
        except Exception:
            return text
    return text


def extract_agent(text: str) -> str | None:
    text = decode_escapes(text)
    text = re.sub(r"(?m)^%%writefile.*\n", "", text)
    text = re.sub(r"(?m)^get_ipython\(\).*\n", "", text)
    if re.search(r"def\s+agent\s*\(", text):
        return text
    m = re.search(
        r"""(?is)(?:main_py|MAIN_PY|AGENT_SRC|agent_src|SOURCE)\s*=\s*(?:r?\"\"\"|r?''')(.*?)(?:\"\"\"|''')""",
        text,
    )
    if m:
        body = decode_escapes(m.group(1))
        if re.search(r"def\s+agent\s*\(", body):
            return body
    return None


def load_quiet(path: Path, tag: str):
    spec = importlib.util.spec_from_file_location(tag, str(path))
    m = importlib.util.module_from_spec(spec)
    try:
        with redirect_stdout(io.StringIO()):
            spec.loader.exec_module(m)
    except Exception:
        spec.loader.exec_module(m)
    if hasattr(m, "agent"):
        fn = m.agent
    elif hasattr(m, "build_agent"):
        fn = m.build_agent({})
    else:
        raise RuntimeError("no agent")
    n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)

    def agent(obs, configuration=None):
        return fn(obs) if n <= 1 else fn(obs, configuration)

    return agent


def run_game(a0, a1, seed: int):
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    t0 = time.time()
    env.run([a0, a1])
    f = env.steps[-1]
    b0 = float(f[0]["observation"]["farms"][0]["money"])
    b1 = float(f[1]["observation"]["farms"][1]["money"])
    st = [s.get("status") for s in f]
    return b0, b1, st, round(time.time() - t0, 1)


def smoke(cand_path: Path, tag: str) -> dict:
    rows = []
    for seat0 in (True, False):
        try:
            cand = load_quiet(cand_path, f"c_{tag}_{seat0}")
            alp = load_quiet(ALPEREN, f"a_{tag}_{seat0}")
        except Exception as e:
            return {"tag": tag, "load_error": str(e)[:200], "wins": 0, "n": 0}
        try:
            if seat0:
                b0, b1, st, sec = run_game(cand, alp, 1)
                cb, ab = b0, b1
            else:
                b0, b1, st, sec = run_game(alp, cand, 1)
                cb, ab = b1, b0
        except Exception as e:
            return {"tag": tag, "run_error": str(e)[:200], "wins": 0, "n": 0}
        rows.append(
            {
                "seat0": seat0,
                "cand": cb,
                "alperen": ab,
                "margin": cb - ab,
                "win": cb > ab,
                "status": st,
                "sec": sec,
            }
        )
        print(f"  {tag} seat0={seat0} cand={cb:.0f} alp={ab:.0f} margin={cb-ab:.0f}", flush=True)
    wins = sum(1 for r in rows if r.get("win"))
    return {"tag": tag, "rows": rows, "wins": wins, "n": len(rows)}


def main() -> None:
    # collect notebooks
    cands: list[tuple[str, Path]] = []
    for base in (SCAN, SCAN2):
        if not base.exists():
            continue
        for d in sorted(base.iterdir()):
            if not d.is_dir() or d.name == "extracted":
                continue
            nbs = list(d.glob("*.ipynb"))
            if not nbs:
                continue
            text = cell_text(nbs[0])
            block = extract_agent(text)
            if not block:
                continue
            try:
                ast.parse(block)
            except SyntaxError:
                continue
            if not re.search(r"def\s+agent\s*\(", block):
                continue
            tag = d.name[:40]
            out = EXTRACT / f"{tag}.py"
            if not out.exists():
                out.write_text(block, encoding="utf-8")
            ids = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]{3,}", block))
            marks = [m for m in KNOWN if m.lower() in block.lower()]
            cands.append((tag, out))
            print(f"EXTRACTED {tag} bytes={out.stat().st_size} marks={marks}", flush=True)

    print(f"\nSMOKE vs alperen seed1 both seats, n={len(cands)} candidates\n", flush=True)
    results = []
    for tag, path in cands:
        print(f"== {tag} ==", flush=True)
        results.append(smoke(path, tag))

    # rank
    ranked = sorted(
        [r for r in results if r.get("n") == 2],
        key=lambda r: (-(r["wins"]), -max((x.get("margin") or -1e9) for x in r["rows"])),
    )
    payload = {
        "results": results,
        "ranked": [
            {
                "tag": r["tag"],
                "wins": r["wins"],
                "margins": [x.get("margin") for x in r["rows"]],
            }
            for r in ranked
        ],
        "submit": False,
        "note": "seed1 smoke only; full gate still required",
    }
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("\n=== RANKED (wins, margins) ===")
    for r in payload["ranked"]:
        print(f"{r['wins']}/2  {r['margins']}  {r['tag']}")
    print("WROTE", OUT)


if __name__ == "__main__":
    main()
