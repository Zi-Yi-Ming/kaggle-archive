# -*- coding: utf-8 -*-
"""P75c full-ish gate: goodpjw + repaired extracts vs alperen/R2."""
from __future__ import annotations

import importlib.util
import io
import json
import re
import sys
import time
from contextlib import redirect_stdout
from pathlib import Path

PROJ = Path(r"D:\桌面\Kaggle\kaggriculture")
sys.path.insert(0, str(PROJ))
from kaggle_environments import make  # noqa: E402

ALPEREN = PROJ / "_push_alperen" / "main.py"
R2 = PROJ / "_push_medal" / "main.py"
GOODPJW = PROJ / "_external" / "scan_p75_mass" / "extracted" / "goodpjw2008__kaggriculture-melon-thresho.py"
THOMAS = PROJ / "_external" / "scan_20260919" / "extracted" / "thomas_2945_clean.py"
OUT = PROJ / "_research" / "p75c_goodpjw_gate.json"
SEEDS = (1, 2, 3, 4)


def prep_source(path: Path) -> str:
    code = path.read_text(encoding="utf-8", errors="ignore")
    code = re.sub(r"(?m)^%%writefile.*\n", "", code)
    code = re.sub(r"(?m)^get_ipython\(\).*\n", "", code)
    # mock IPython if referenced
    if "IPython" in code and "sys.modules" not in code:
        code = (
            "import sys, types\n"
            "if 'IPython' not in sys.modules:\n"
            "    _m=types.ModuleType('IPython'); _m.display=lambda *a,**k:None\n"
            "    sys.modules['IPython']=_m\n"
            "    sys.modules['IPython.display']=types.ModuleType('IPython.display')\n"
            "    sys.modules['IPython.display'].display=lambda *a,**k:None\n"
            "    sys.modules['IPython.display'].FileLink=object\n"
            "    sys.modules['IPython.display'].HTML=object\n"
            + code
        )
    # hoist __future__ imports
    futures = re.findall(r"(?m)^from __future__ import .+$", code)
    if futures:
        for f in futures:
            code = code.replace(f + "\n", "", 1)
        code = "\n".join(futures) + "\n" + code
    return code


def load_quiet(path: Path, tag: str):
    code = prep_source(path)
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


def series(cand_path: Path, opp_path: Path, opp_name: str, tag: str):
    rows = []
    for seed in SEEDS:
        for seat0 in (True, False):
            try:
                cand = load_quiet(cand_path, f"c_{tag}_{opp_name}_{seed}_{seat0}")
                opp = load_quiet(opp_path, f"o_{tag}_{opp_name}_{seed}_{seat0}")
            except Exception as e:
                print(f"LOADFAIL {tag} vs {opp_name} seed={seed}: {e}", flush=True)
                return [{"error": str(e)[:200]}]
            env = make("kaggriculture", debug=False)
            env.configuration["episodeSteps"] = 720
            if env.info is None:
                env.info = {}
            env.info["seed"] = int(seed)
            t0 = time.time()
            try:
                if seat0:
                    env.run([cand, opp])
                    cb = float(env.steps[-1][0]["observation"]["farms"][0]["money"])
                    ob = float(env.steps[-1][1]["observation"]["farms"][1]["money"])
                else:
                    env.run([opp, cand])
                    ob = float(env.steps[-1][0]["observation"]["farms"][0]["money"])
                    cb = float(env.steps[-1][1]["observation"]["farms"][1]["money"])
            except Exception as e:
                print(f"RUNFAIL {tag}: {e}", flush=True)
                return [{"error": str(e)[:200]}]
            st = [s.get("status") for s in env.steps[-1]]
            row = {
                "opp": opp_name,
                "seed": seed,
                "seat0": seat0,
                "cand": cb,
                "opp_bank": ob,
                "margin": cb - ob,
                "win": cb > ob,
                "status": st,
                "sec": round(time.time() - t0, 1),
            }
            print(
                f"{tag} vs {opp_name} s={seed} seat0={seat0} "
                f"cand={cb:.0f} opp={ob:.0f} m={row['margin']:.0f} win={row['win']}",
                flush=True,
            )
            rows.append(row)
    return rows


def main() -> None:
    payload = {"games": [], "summary": {}}
    for cand_path, tag in ((GOODPJW, "goodpjw"), (THOMAS, "thomas_ref")):
        for opp_path, opp_name in ((ALPEREN, "alperen"), (R2, "R2")):
            print(f"\n=== {tag} vs {opp_name} ===", flush=True)
            rows = series(cand_path, opp_path, opp_name, tag)
            payload["games"].extend([{**r, "cand_tag": tag} for r in rows])
            ok = [r for r in rows if "error" not in r]
            wins = sum(1 for r in ok if r.get("win"))
            payload["summary"][f"{tag}_vs_{opp_name}"] = {
                "wins": wins,
                "n": len(ok),
                "mean_margin": (sum(r["margin"] for r in ok) / len(ok)) if ok else None,
            }
            print(f"SUMMARY {tag} vs {opp_name}: {wins}/{len(ok)}", flush=True)

    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("\n=== FINAL SUMMARY ===")
    print(json.dumps(payload["summary"], indent=2))
    print("WROTE", OUT)
    print("SUBMIT_CANDIDATES_PENDING_USER:", end=" ")
    # auto shortlist
    short = []
    for k, v in payload["summary"].items():
        if v["n"] >= 6 and v["wins"] / max(1, v["n"]) >= 0.75:
            short.append(k)
    print(short)


if __name__ == "__main__":
    main()
