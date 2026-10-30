# -*- coding: utf-8 -*-
"""P77c: extract + smoke vs alperen for scan_p77 candidates."""
from __future__ import annotations

import ast
import importlib.util
import io
import json
import re
import subprocess
import sys
import time
from contextlib import redirect_stdout
from pathlib import Path

PROJ = Path(r"D:\桌面\Kaggle\kaggriculture")
SCAN = PROJ / "_external" / "scan_p77"
EXTRACT = SCAN / "extracted"
EXTRACT.mkdir(exist_ok=True)
ALPEREN = PROJ / "_push_alperen" / "main.py"
THOMAS = PROJ / "_push_thomas_2945" / "main.py"
OUT = PROJ / "_research" / "p77_smoke.json"
PY = r"C:\Users\Lenovo\.conda\envs\kaggle\python.exe"
sys.path.insert(0, str(PROJ))

PRIORITY = [
    "hesoponyo__pure-rl-agent-bc-ppo-self-play",
    "municef1__lb-2448-single-file-kaggriculture-agent",
    "dmitriigluzdov__kaggriculture-7-turn-rescue-historical-lb-2800",
    "dmitriigluzdov__kaggriculture-herd-safe-sale-window-lb-2700",
    "salemali7__kaggregulture-2900",
    "salemali7__kaggriculture-2900",
    "nusrati__2715-6",
    "avioon__kaggriculture-apex-v7-god-emperor",
    "llccqq624__kaggriculture-top-5-meta-ensemble",
    "guruprasaathas111__kaggriculture-fully-dynamic-autonomous-agent",
    "rohitt94__kaggriculture-route-replay-agent",
    "denizeryilmaz__v111-8c4s-economic-core-premium-lead",
    "andrewsokolovsky__kaggriculture-breaking-the-tie",
    "evgendvorkin__kaggriculture",
    "reyhanksatria__kaggriculture-dynamic-route-agent",
    "yhay81__shop-router-0913",
    "thomastschinkel__kaggregulture-93-8-win-rate-public-state-router",
    "thomastschinkel__kaggriculture-93-8-win-rate-public-state-router",
    "lime0001__score2710-t23-kaggriculture-smart-harvest",
    "alperen5252525__kaggriculture-metacounter-r1-scored-agent",
]


def nb_code(p: Path) -> str:
    nb = json.loads(p.read_text(encoding="utf-8"))
    parts = []
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        src = cell.get("source", [])
        parts.append("".join(src) if isinstance(src, list) else str(src))
    return "\n\n".join(parts)


def decode(text: str) -> str:
    if "\\n" in text[:800] and text.count("\n") < 8:
        try:
            return text.encode("utf-8").decode("unicode_escape")
        except Exception:
            return text
    return text


def harvest(code: str) -> str | None:
    code = decode(code)
    code = re.sub(r"(?m)^%%writefile.*\n", "", code)
    code = re.sub(r"(?m)^get_ipython\(\).*\n", "", code)
    blocks = []
    if re.search(r"(?m)^def\s+agent\s*\(", code):
        blocks.append(code)
    for m in re.finditer(r"(?s)(?:r?\"\"\"|r?''')(.*?)(?:\"\"\"|''')", code):
        blob = decode(m.group(1))
        if re.search(r"def\s+agent\s*\(", blob) and len(blob) > 1500:
            blocks.append(blob)
    if not blocks:
        return None
    best = max(blocks, key=len)
    futures = re.findall(r"(?m)^from __future__ import .+$", best)
    for f in futures:
        best = best.replace(f + "\n", "", 1)
    if futures:
        best = "\n".join(futures) + "\n" + best
    if "IPython" in best:
        best = (
            "import sys, types\n"
            "if 'IPython' not in sys.modules:\n"
            "    _m=types.ModuleType('IPython'); _m.display=lambda *a,**k:None\n"
            "    sys.modules['IPython']=_m\n"
            "    _d=types.ModuleType('IPython.display'); _d.display=lambda *a,**k:None\n"
            "    _d.FileLink=object; _d.HTML=object\n"
            "    sys.modules['IPython.display']=_d\n" + best
        )
    try:
        ast.parse(best)
    except SyntaxError:
        return None
    return best


def load_quiet(path: Path, tag: str):
    code = path.read_text(encoding="utf-8", errors="ignore")
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


def smoke(cand: Path, tag: str, opp_path: Path, opp_name: str) -> dict:
    rows = []
    for seat0 in (True, False):
        try:
            c = load_quiet(cand, f"c_{tag}_{opp_name}_{seat0}")
            o = load_quiet(opp_path, f"o_{tag}_{opp_name}_{seat0}")
            if seat0:
                b0, b1, st, sec = run_game(c, o, 1)
                cb, ob = b0, b1
            else:
                b0, b1, st, sec = run_game(o, c, 1)
                cb, ob = b1, b0
        except Exception as e:
            return {"tag": tag, "opp": opp_name, "error": str(e)[:180], "wins": None, "n": 0}
        rows.append(
            {
                "seat0": seat0,
                "cand": cb,
                "opp": ob,
                "margin": cb - ob,
                "win": cb > ob,
                "status": st,
            }
        )
    wins = sum(1 for r in rows if r["win"])
    return {
        "tag": tag,
        "opp": opp_name,
        "wins": wins,
        "n": len(rows),
        "max_margin": max(r["margin"] for r in rows),
        "rows": rows,
        "error": None,
    }


def main() -> None:
    # extract all folders
    extracted = []
    for d in sorted(SCAN.iterdir()):
        if not d.is_dir() or d.name == "extracted":
            continue
        nbs = list(d.glob("*.ipynb"))
        if not nbs:
            continue
        code = harvest(nb_code(nbs[0]))
        if not code:
            print(f"NO_AGENT {d.name}")
            continue
        out = EXTRACT / f"{d.name[:48]}.py"
        out.write_text(code, encoding="utf-8")
        extracted.append(out)
        print(f"EXTRACT {out.name} bytes={out.stat().st_size}", flush=True)

    # prioritize named
    ordered = []
    seen = set()
    for pref in PRIORITY:
        for p in extracted:
            if p.stem.startswith(pref[:30]) or pref[:20] in p.stem:
                if p not in seen:
                    ordered.append(p)
                    seen.add(p)
    for p in extracted:
        if p not in seen:
            ordered.append(p)

    print(f"\nSMOKE n={len(ordered)} vs alperen seed1 both seats\n", flush=True)
    results = []
    for p in ordered:
        print(f"== {p.stem[:40]} ==", flush=True)
        r = smoke(p, p.stem[:40], ALPEREN, "alperen")
        print(" ", json.dumps({k: r[k] for k in r if k != "rows"}, ensure_ascii=False), flush=True)
        results.append(r)

    ranked = [r for r in results if r.get("wins") is not None and r.get("n") == 2]
    ranked.sort(key=lambda r: (-r["wins"], -(r.get("max_margin") or -1e18)))
    # full gate top unique winners that aren't known thin clones
    print("\n=== RANKED vs alperen seed1 ===")
    for r in ranked:
        print(f"{r['wins']}/2 maxM={r.get('max_margin')} {r['tag']}")

    # deeper: top 3 non-error winners vs alperen AND thomas, seeds 1-3
    deep = []
    top = [r for r in ranked if r["wins"] >= 2][:4]
    for r in top:
        p = EXTRACT / f"{r['tag']}.py"
        if not p.exists():
            # try match
            hits = list(EXTRACT.glob(f"{r['tag'][:30]}*.py"))
            p = hits[0] if hits else None
        if not p:
            continue
        print(f"\n=== DEEP {r['tag']} ===", flush=True)
        for opp_path, opp_name in ((ALPEREN, "alperen"), (THOMAS, "thomas")):
            wins = n = 0
            margins = []
            for seed in (1, 2, 3):
                for seat0 in (True, False):
                    try:
                        rr = smoke_seed(p, opp_path, seed, seat0)
                    except Exception as e:
                        print(" deep fail", e)
                        continue
                    n += 1
                    wins += int(rr["win"])
                    margins.append(rr["margin"])
                    print(f"  {opp_name} s={seed} seat0={seat0} m={rr['margin']:.0f} win={rr['win']}", flush=True)
            deep.append(
                {
                    "tag": r["tag"],
                    "opp": opp_name,
                    "wins": wins,
                    "n": n,
                    "mean_margin": (sum(margins) / len(margins)) if margins else None,
                }
            )
            print(f"DEEP SUMMARY {r['tag']} vs {opp_name}: {wins}/{n}", flush=True)

    payload = {
        "smoke": results,
        "ranked": ranked,
        "deep": deep,
        "submit": False,
        "timeline": {
            "final_submission_deadline": "2026-09-30",
            "bt_period": "2026-10-01 to ~2026-10-15",
        },
    }
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("\nDEEP RESULTS:")
    print(json.dumps(deep, indent=2))
    print("WROTE", OUT)


def smoke_seed(cand: Path, opp_path: Path, seed: int, seat0: bool) -> dict:
    c = load_quiet(cand, f"dc_{seed}_{seat0}")
    o = load_quiet(opp_path, f"do_{seed}_{seat0}")
    if seat0:
        b0, b1, st, sec = run_game(c, o, seed)
        cb, ob = b0, b1
    else:
        b0, b1, st, sec = run_game(o, c, seed)
        cb, ob = b1, b0
    return {"cand": cb, "opp": ob, "margin": cb - ob, "win": cb > ob, "status": st}


if __name__ == "__main__":
    main()
