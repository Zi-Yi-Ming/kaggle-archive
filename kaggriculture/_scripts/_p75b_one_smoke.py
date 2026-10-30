# -*- coding: utf-8 -*-
"""Smoke one candidate vs alperen, seed=1 both seats. Prints one JSON line."""
from __future__ import annotations

import importlib.util
import io
import json
import re
import sys
import time
from contextlib import redirect_stdout
from pathlib import Path

cand_path = Path(sys.argv[1])
alp_path = Path(sys.argv[2])
sys.path.insert(0, str(Path(alp_path).parents[1]))


def load_quiet(path: Path, tag: str):
    # neutralize common notebook side-effect writes
    code = path.read_text(encoding="utf-8", errors="ignore")
    code = re.sub(r"(?m)^%%writefile.*\n", "", code)
    code = re.sub(r"(?m)^get_ipython\(\).*\n", "", code)
    # block accidental file writes at import via display/print only; keep logic
    spec = importlib.util.spec_from_file_location(tag, str(path))
    m = importlib.util.module_from_spec(spec)
    # exec from compiled text to avoid re-reading; still uses path for spec
    ns = {
        "__name__": tag,
        "__file__": str(path),
        "__builtins__": __builtins__,
    }
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            exec(compile(code, str(path), "exec"), ns)
    except Exception as e:
        raise RuntimeError(f"exec_fail:{type(e).__name__}:{e}") from e
    fn = ns.get("agent")
    if fn is None and hasattr(ns.get("build_agent", None), "__call__"):
        fn = ns["build_agent"]({})
    if fn is None:
        raise RuntimeError("no_agent")
    n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)

    def agent(obs, configuration=None):
        return fn(obs) if n <= 1 else fn(obs, configuration)

    return agent


def run_game(a0, a1, seed: int):
    from kaggle_environments import make

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


def main() -> None:
    tag = cand_path.stem[:40]
    try:
        rows = []
        for seat0 in (True, False):
            cand = load_quiet(cand_path, f"c_{tag}_{seat0}")
            alp = load_quiet(alp_path, f"a_{tag}_{seat0}")
            if seat0:
                b0, b1, st, sec = run_game(cand, alp, 1)
                cb, ab = b0, b1
            else:
                b0, b1, st, sec = run_game(alp, cand, 1)
                cb, ab = b1, b0
            rows.append(
                {
                    "seat0": seat0,
                    "cand": cb,
                    "alperen": ab,
                    "margin": cb - ab,
                    "win": cb > ab,
                    "status": st,
                }
            )
        wins = sum(1 for r in rows if r["win"])
        max_margin = max(r["margin"] for r in rows)
        print(
            json.dumps(
                {
                    "tag": tag,
                    "wins": wins,
                    "n": len(rows),
                    "max_margin": max_margin,
                    "rows": rows,
                    "error": None,
                }
            )
        )
    except Exception as e:
        print(json.dumps({"tag": tag, "error": str(e)[:240], "wins": None, "n": 0}))


if __name__ == "__main__":
    main()
