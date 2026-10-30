# -*- coding: utf-8 -*-
"""P77d deep gate: guru fully-dynamic vs alperen + thomas, seeds 1-4."""
from __future__ import annotations

import io
import json
import re
import sys
import time
from contextlib import redirect_stdout
from pathlib import Path

PROJ = Path(r"D:\桌面\Kaggle\kaggriculture")
CAND = next(Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_p77\extracted").glob("guruprasaathas111__kaggriculture-fully-d*.py"))
ALPEREN = PROJ / "_push_alperen" / "main.py"
THOMAS = PROJ / "_push_thomas_2945" / "main.py"
R2 = PROJ / "_push_medal" / "main.py"
OUT = PROJ / "_research" / "p77d_guru_dynamic_gate.json"
sys.path.insert(0, str(PROJ))
from kaggle_environments import make  # noqa: E402

SEEDS = (1, 2, 3, 4)


def load_quiet(path: Path, tag: str):
    code = path.read_text(encoding="utf-8", errors="ignore")
    code = re.sub(r"(?m)^%%writefile.*\n", "", code)
    code = re.sub(r"(?m)^get_ipython\(\).*\n", "", code)
    futures = re.findall(r"(?m)^from __future__ import .+$", code)
    for f in futures:
        code = code.replace(f + "\n", "", 1)
    if futures:
        code = "\n".join(futures) + "\n" + code
    if "IPython" in code:
        code = (
            "import sys, types\n"
            "if 'IPython' not in sys.modules:\n"
            "    _m=types.ModuleType('IPython'); _m.display=lambda *a,**k:None\n"
            "    sys.modules['IPython']=_m\n"
            "    _d=types.ModuleType('IPython.display'); _d.display=lambda *a,**k:None\n"
            "    _d.FileLink=object; _d.HTML=object\n"
            "    _m.get_ipython=lambda: type('X',(),{'run_line_magic':lambda *a,**k:None,'magic':lambda *a,**k:None})()\n"
            "    _m.version_info=(3,11)\n"
            "    sys.modules['IPython.display']=_d\n" + code
        )
    ns = {"__name__": tag, "__file__": str(path), "__builtins__": __builtins__}
    try:
        with redirect_stdout(io.StringIO()):
            exec(compile(code, str(path), "exec"), ns)
    except Exception as e:
        raise RuntimeError(f"{type(e).__name__}:{e}") from e
    fn = ns.get("agent")
    if fn is None and callable(ns.get("build_agent")):
        fn = ns["build_agent"]({})
    if fn is None:
        raise RuntimeError("no_agent")
    n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)

    def agent(obs, configuration=None):
        return fn(obs) if n <= 1 else fn(obs, configuration)

    return agent


def run(a0, a1, seed: int):
    env = make("kaggriculture", debug=False)
    env.configuration["episodeSteps"] = 720
    if env.info is None:
        env.info = {}
    env.info["seed"] = int(seed)
    t0 = time.time()
    env.run([a0, a1])
    f = env.steps[-1]
    return (
        float(f[0]["observation"]["farms"][0]["money"]),
        float(f[1]["observation"]["farms"][1]["money"]),
        [s.get("status") for s in f],
        round(time.time() - t0, 1),
    )


def series(opp_path: Path, opp_name: str):
    rows = []
    for seed in SEEDS:
        for seat0 in (True, False):
            try:
                c = load_quiet(CAND, f"c_{opp_name}_{seed}_{seat0}")
                o = load_quiet(opp_path, f"o_{opp_name}_{seed}_{seat0}")
                if seat0:
                    b0, b1, st, sec = run(c, o, seed)
                    cb, ob = b0, b1
                else:
                    b0, b1, st, sec = run(o, c, seed)
                    cb, ob = b1, b0
            except Exception as e:
                print(f"FAIL {opp_name} s={seed}: {e}", flush=True)
                rows.append({"opp": opp_name, "error": str(e)[:160]})
                continue
            row = {
                "opp": opp_name,
                "seed": seed,
                "seat0": seat0,
                "cand": cb,
                "opp_bank": ob,
                "margin": cb - ob,
                "win": cb > ob,
                "status": st,
            }
            print(
                f"guru vs {opp_name} s={seed} seat0={seat0} "
                f"cand={cb:.0f} opp={ob:.0f} m={row['margin']:.0f} win={row['win']}",
                flush=True,
            )
            rows.append(row)
    ok = [r for r in rows if "error" not in r]
    wins = sum(1 for r in ok if r.get("win"))
    mean_m = sum(r["margin"] for r in ok) / len(ok) if ok else None
    return rows, {"opp": opp_name, "wins": wins, "n": len(ok), "mean_margin": mean_m}


def main() -> None:
    print("CAND", CAND)
    # hash note
    print("bytes", CAND.stat().st_size)
    payload = {"cand": str(CAND), "rows": [], "summary": []}
    for opp_path, opp_name in ((ALPEREN, "alperen"), (R2, "R2"), (THOMAS, "thomas")):
        print(f"\n=== vs {opp_name} ===", flush=True)
        rows, summary = series(opp_path, opp_name)
        payload["rows"].extend(rows)
        payload["summary"].append(summary)
        print("SUMMARY", summary, flush=True)
    payload["submit"] = False
    payload["note"] = "local gate only; farm_v4 risk remains; do not submit without user auth"
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("\nWROTE", OUT)
    print(json.dumps(payload["summary"], indent=2))


if __name__ == "__main__":
    main()
