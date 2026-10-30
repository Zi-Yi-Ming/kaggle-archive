# -*- coding: utf-8 -*-
"""P84 hunt: extract public agents and gate vs production Metav4. NO SUBMIT."""
from __future__ import annotations

import base64
import gzip
import importlib.util
import json
import re
import zlib
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "p79", r"D:\桌面\Kaggle\kaggriculture\_scripts\_p79_mass_gate_vs_thomas.py"
)
p79 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p79)

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_p84_vs_metav4")
OUTDIR = ROOT / "extracted"
OUTDIR.mkdir(parents=True, exist_ok=True)
METAV4 = Path(r"D:\桌面\Kaggle\kaggriculture\_push_metav4_v13\main.py")
OUTJSON = Path(r"D:\桌面\Kaggle\kaggriculture\_research\p84_hunt_vs_metav4.json")

# also legacy extracts that may still be loadable
LEGACY = [
    Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_p83_metav4\metav4_v13_main.py"),  # skip self
    Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_p77\extracted\dmitriigluzdov__kaggriculture-herd-safe-sale-win.py"),
    Path(r"D:\桌面\Kaggle\kaggriculture\_external\p70_extracted\farming_score_v5_timing_optimized__0.py"),
    Path(r"D:\桌面\Kaggle\kaggriculture\_external\p66_extracted\kaggriculture_shop_router_reactive_v6.py"),
]


def strip_tail(code: str) -> str:
    code = re.sub(r"(?m)^%%writefile.*\n", "", code)
    agent_i = code.find("\ndef agent")
    if agent_i > 0:
        for mark in (
            "from kaggle_environments",
            'Path("main.py")',
            "Path('main.py')",
            "Wrote verified",
            "%%writefile",
            "def load_agent",
        ):
            i = code.find(mark, agent_i)
            if i > agent_i:
                code = code[:i]
                break
    # packaging
    code = re.split(r"(?m)^data = Path\([\"']main\.py[\"']\)\.read_bytes\(\)", code, maxsplit=1)[0]
    return code


def extract_payload(nb_path: Path) -> str | None:
    try:
        nb = json.loads(nb_path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return None
    srcs = []
    for c in nb.get("cells", []):
        s = c.get("source", "")
        if isinstance(s, list):
            s = "".join(s)
        srcs.append(s)
    blob = "\n".join(srcs)
    # zlib/base64 payload like Metav4
    m = re.search(r"_PAYLOAD\s*=\s*'([A-Za-z0-9+/=]+)'", blob)
    if m:
        try:
            raw = zlib.decompress(base64.b64decode(m.group(1)))
            if b"def agent" in raw:
                return raw.decode("utf-8", errors="ignore")
        except Exception:
            pass
    # writefile main.py
    m = re.search(r"(?ms)^%%writefile\s+main\.py\s*\n(.+?)(?=^%%writefile|\Z)", blob)
    if m and "def agent" in m.group(1):
        return m.group(1)
    # largest cell with def agent
    best = None
    for s in srcs:
        if "def agent" in s and len(s) > 5000:
            if best is None or len(s) > len(best):
                best = s
    return best


def main():
    # collect candidates
    jobs = []
    for nb in sorted(ROOT.rglob("*.ipynb")):
        code = extract_payload(nb)
        if not code or "def agent" not in code:
            print("no agent", nb.parent.name)
            continue
        code = strip_tail(code)
        out = OUTDIR / (nb.parent.name + ".py")
        out.write_text(code, encoding="utf-8")
        print("extracted", out.name, out.stat().st_size)
        jobs.append((nb.parent.name, out))
    for py in ROOT.rglob("*.py"):
        if py.parent == OUTDIR:
            continue
        t = py.read_text(encoding="utf-8", errors="ignore")
        if "def agent" in t:
            out = OUTDIR / (py.parent.name + ".py")
            out.write_text(strip_tail(t), encoding="utf-8")
            print("extracted py", out.name, out.stat().st_size)
            jobs.append((py.parent.name, out))
    for p in LEGACY:
        if p.exists() and p != METAV4 and "metav4_v13_main" not in p.name:
            jobs.append((p.stem[:40], p))

    payload = {"baseline": str(METAV4), "results": {}}
    if OUTJSON.exists():
        try:
            payload = json.loads(OUTJSON.read_text(encoding="utf-8"))
        except Exception:
            payload = {"baseline": str(METAV4), "results": {}}
    payload.setdefault("results", {})

    print(f"jobs {len(jobs)}", flush=True)
    for key, path in jobs:
        prev = (payload["results"].get(key) or {}).get("summary") or {}
        if prev.get("n", 0) >= 4 and (prev.get("win_rate") or 0) < 0.5:
            print("SKIP", key, prev)
            continue
        print(f"===== {key} vs Metav4 =====", flush=True)
        try:
            rows = p79.gate_one(key, path, (1, 2))
            # p79.gate_one always loads THOMAS - need custom vs Metav4
        except Exception as e:
            payload["results"][key] = {"path": str(path), "error": str(e)[:200]}
            print("FAIL", key, e)
            continue

    # custom series vs Metav4
    def series(key, path, seeds=(1, 2)):
        rows = []
        for seed in seeds:
            for seat0 in (True, False):
                tag = f"{key}_mv4_{seed}_{int(seat0)}"
                try:
                    c = p79.load_quiet(path, f"c_{tag}")
                    o = p79.load_quiet(METAV4, f"o_{tag}")
                    if seat0:
                        b0, b1, st, sec = p79.run(c, o, seed)
                        cb, ob = b0, b1
                    else:
                        b0, b1, st, sec = p79.run(o, c, seed)
                        cb, ob = b1, b0
                    row = {
                        "cand": key,
                        "seed": seed,
                        "seat0": seat0,
                        "cand_bank": cb,
                        "metav4_bank": ob,
                        "margin": cb - ob,
                        "win": cb > ob,
                        "status": st,
                    }
                    print(
                        f"{key} vs Metav4 s={seed} seat0={seat0} c={cb:.0f} m={ob:.0f} "
                        f"Δ={row['margin']:.0f} win={row['win']}",
                        flush=True,
                    )
                except Exception as e:
                    row = {"cand": key, "seed": seed, "seat0": seat0, "error": str(e)[:180]}
                    print(f"FAIL {key} s={seed} seat0={seat0}: {e}", flush=True)
                rows.append(row)
        ok = [r for r in rows if "error" not in r]
        wins = sum(1 for r in ok if r.get("win"))
        return rows, {
            "cand": key,
            "opp": "metav4",
            "n": len(ok),
            "wins": wins,
            "win_rate": round(wins / len(ok), 3) if ok else None,
            "mean_margin": round(sum(r["margin"] for r in ok) / len(ok), 1) if ok else None,
            "errors": len(rows) - len(ok),
        }

    for key, path in jobs:
        if path.name.startswith("metav4_v13_main"):
            continue
        rows, sm = series(key, path)
        payload["results"][key] = {"path": str(path), "summary": sm, "rows": rows}
        OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print("SUM", sm, flush=True)
        if sm.get("wins", 0) >= 2 and sm.get("errors", 0) == 0:
            print("PROMISING escalate", key, flush=True)
            rows2, sm2 = series(key, path, seeds=(3, 4, 5))
            payload["results"][key]["rows"] = rows + rows2
            payload["results"][key]["summary"] = {
                **sm2,
                "wins": sm["wins"] + sm2["wins"],
                "n": sm["n"] + sm2["n"],
                "win_rate": round((sm["wins"] + sm2["wins"]) / max(1, sm["n"] + sm2["n"]), 3),
            }
            OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
            print("ESC", payload["results"][key]["summary"], flush=True)

    print("\n==== P84 vs Metav4 ====", flush=True)
    for k, v in payload["results"].items():
        s = v.get("summary") or v.get("error")
        print(f"{k[:40]:40s} {s}", flush=True)


if __name__ == "__main__":
    main()
