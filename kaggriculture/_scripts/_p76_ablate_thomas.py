# -*- coding: utf-8 -*-
"""P76 ablation: neutralize thomas v9 layers, compare banks. No submit."""
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
SRC = PROJ / "_external" / "scan_20260919" / "extracted" / "thomas_2945_clean.py"
ABL = PROJ / "_research" / "p76_ablation_agents"
ABL.mkdir(parents=True, exist_ok=True)
ALPEREN = PROJ / "_push_alperen" / "main.py"
OUT = PROJ / "_research" / "p76_ablation_results.json"
sys.path.insert(0, str(PROJ))
from kaggle_environments import make  # noqa: E402

SEEDS = (1, 2, 3)

# Neutralize layers by forcing early return / no-op on key functions.
# Order in file: later defs wrap earlier; we patch by unique function bodies.
PATCHES = {
    "full": [],  # no patch
    "no_courier": [
        (
            r"def _v9_courier\(obs, action, st\):",
            "def _v9_courier(obs, action, st):\n    return action  # ABLATE_COURIER\n",
            1,
        )
    ],
    "no_herd": [
        (
            r"def _v9_herd\(obs, action, st\):",
            "def _v9_herd(obs, action, st):\n    return action  # ABLATE_HERD\n",
            1,
        )
    ],
    "no_race": [
        (
            r"def _v9_race_update\(obs, st\):",
            "def _v9_race_update(obs, st):\n    return  # ABLATE_RACE_UPDATE\n",
            1,
        ),
        (
            r"def _v9_racepx_lead\(self, action, view, projected, route, step, next_sup\):",
            "def _v9_racepx_lead(self, action, view, projected, route, step, next_sup):\n"
            "    return route  # ABLATE_RACEPX\n",
            1,
        ),
    ],
    "no_v9_all": [
        (
            r"def _v9_courier\(obs, action, st\):",
            "def _v9_courier(obs, action, st):\n    return action  # ABLATE\n",
            1,
        ),
        (
            r"def _v9_herd\(obs, action, st\):",
            "def _v9_herd(obs, action, st):\n    return action  # ABLATE\n",
            1,
        ),
        (
            r"def _v9_race_update\(obs, st\):",
            "def _v9_race_update(obs, st):\n    return  # ABLATE\n",
            1,
        ),
        (
            r"def _v9_racepx_lead\(self, action, view, projected, route, step, next_sup\):",
            "def _v9_racepx_lead(self, action, view, projected, route, step, next_sup):\n"
            "    return route  # ABLATE\n",
            1,
        ),
    ],
}


def build_variant(name: str) -> Path:
    text = SRC.read_text(encoding="utf-8", errors="ignore")
    for pat, repl, cnt in PATCHES[name]:
        new, n = re.subn(pat, repl, text, count=cnt)
        if n == 0:
            print(f"WARN patch miss {name}: {pat[:50]}")
        text = new
    out = ABL / f"thomas_{name}.py"
    out.write_text(text, encoding="utf-8")
    return out


def load_quiet(path: Path, tag: str):
    code = path.read_text(encoding="utf-8", errors="ignore")
    code = re.sub(r"(?m)^%%writefile.*\n", "", code)
    code = re.sub(r"(?m)^get_ipython\(\).*\n", "", code)
    futures = re.findall(r"(?m)^from __future__ import .+$", code)
    for f in futures:
        code = code.replace(f + "\n", "", 1)
    if futures:
        code = "\n".join(futures) + "\n" + code
    ns = {"__name__": tag, "__file__": str(path), "__builtins__": __builtins__}
    try:
        with redirect_stdout(io.StringIO()):
            exec(compile(code, str(path), "exec"), ns)
    except Exception as e:
        raise RuntimeError(f"{type(e).__name__}:{e}") from e
    fn = ns.get("agent")
    if fn is None:
        raise RuntimeError("no_agent")
    n = getattr(getattr(fn, "__code__", None), "co_argcount", 2)

    def agent(obs, configuration=None):
        return fn(obs) if n <= 1 else fn(obs, configuration)

    return agent


def run_banks(a0, a1, seed: int):
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
        [s.get("status") for s in f],
    )


def series_vs(cand_path: Path, opp_path: Path, tag: str, opp_name: str):
    rows = []
    for seed in SEEDS:
        for seat0 in (True, False):
            try:
                c = load_quiet(cand_path, f"c_{tag}_{opp_name}_{seed}_{seat0}")
                o = load_quiet(opp_path, f"o_{tag}_{opp_name}_{seed}_{seat0}")
            except Exception as e:
                return [{"error": str(e)[:200], "tag": tag, "opp": opp_name}]
            try:
                if seat0:
                    b0, b1, st = run_banks(c, o, seed)
                    cb, ob = b0, b1
                else:
                    b0, b1, st = run_banks(o, c, seed)
                    cb, ob = b1, b0
            except Exception as e:
                return [{"error": str(e)[:200], "tag": tag, "opp": opp_name}]
            rows.append(
                {
                    "tag": tag,
                    "opp": opp_name,
                    "seed": seed,
                    "seat0": seat0,
                    "cand": cb,
                    "opp_bank": ob,
                    "margin": cb - ob,
                    "win": cb > ob,
                    "status": st,
                }
            )
            print(
                f"{tag:12s} vs {opp_name:8s} s={seed} seat0={int(seat0)} "
                f"cand={cb:.0f} opp={ob:.0f} m={cb-ob:.0f}",
                flush=True,
            )
    return rows


def summarize(rows):
    ok = [r for r in rows if "error" not in r]
    if not ok:
        return {"n": 0, "wins": 0, "mean_cand": None, "mean_margin": None}
    return {
        "n": len(ok),
        "wins": sum(1 for r in ok if r["win"]),
        "mean_cand": sum(r["cand"] for r in ok) / len(ok),
        "mean_margin": sum(r["margin"] for r in ok) / len(ok),
    }


def main() -> None:
    # sanity: patches applied?
    full = build_variant("full")
    print("full exists", full.exists(), full.stat().st_size)
    for name in PATCHES:
        p = build_variant(name)
        t = p.read_text(encoding="utf-8", errors="ignore")
        print(
            f"variant {name:12s} bytes={p.stat().st_size} "
            f"ABLATE_markers={t.count('ABLATE')}"
        )

    payload = {"seeds": list(SEEDS), "series": [], "summary": {}}
    variants = list(PATCHES.keys())
    for name in variants:
        path = ABL / f"thomas_{name}.py"
        # vs full thomas (layer contribution) — full vs full is control
        opp = ABL / "thomas_full.py" if name != "full" else ALPEREN
        opp_name = "thomas_full" if name != "full" else "alperen"
        if name == "full":
            # also vs alperen for absolute
            for opp_path, on in ((ALPEREN, "alperen"), (ABL / "thomas_full.py", "self")):
                if on == "self":
                    continue
                print(f"\n=== {name} vs {on} ===", flush=True)
                rows = series_vs(path, opp_path, name, on)
                payload["series"].extend(rows)
                payload["summary"][f"{name}_vs_{on}"] = summarize(rows)
        else:
            print(f"\n=== {name} vs thomas_full ===", flush=True)
            rows = series_vs(path, ABL / "thomas_full.py", name, "thomas_full")
            payload["series"].extend(rows)
            payload["summary"][f"{name}_vs_thomas_full"] = summarize(rows)
            print(f"=== {name} vs alperen ===", flush=True)
            rows = series_vs(path, ALPEREN, name, "alperen")
            payload["series"].extend(rows)
            payload["summary"][f"{name}_vs_alperen"] = summarize(rows)

    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("\n=== SUMMARY ===")
    print(json.dumps(payload["summary"], indent=2))
    print("WROTE", OUT)


if __name__ == "__main__":
    main()
