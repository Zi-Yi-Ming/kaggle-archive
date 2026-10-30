# -*- coding: utf-8 -*-
"""P75b: one-candidate smoke in subprocess with hard timeout."""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

PROJ = Path(r"D:\桌面\Kaggle\kaggriculture")
EXTRACT = PROJ / "_external" / "scan_p75_mass" / "extracted"
ALPEREN = PROJ / "_push_alperen" / "main.py"
OUT = PROJ / "_research" / "p75b_mass_smoke.json"
PY = r"C:\Users\Lenovo\.conda\envs\kaggle\python.exe"
WORKER = PROJ / "_scripts" / "_p75b_one_smoke.py"
TIMEOUT_S = 90  # per candidate both seats


def main() -> None:
    files = sorted(EXTRACT.glob("*.py"))
    files = [p for p in files if not p.name.endswith("_worker.py")]
    results = []
    for p in files:
        print(f"SMOKE {p.name} ...", flush=True)
        t0 = time.time()
        try:
            r = subprocess.run(
                [PY, str(WORKER), str(p), str(ALPEREN)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=TIMEOUT_S,
                env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"},
            )
            out = (r.stdout or "") + "\n" + (r.stderr or "")
            # parse last JSON line
            payload = None
            for line in reversed(out.splitlines()):
                line = line.strip()
                if line.startswith("{") and line.endswith("}"):
                    try:
                        payload = json.loads(line)
                        break
                    except Exception:
                        continue
            if payload is None:
                payload = {
                    "tag": p.stem,
                    "error": "no_json",
                    "tail": out[-400:],
                }
            payload["sec"] = round(time.time() - t0, 1)
            payload["returncode"] = r.returncode
        except subprocess.TimeoutExpired:
            payload = {
                "tag": p.stem,
                "error": "timeout",
                "sec": TIMEOUT_S,
            }
        results.append(payload)
        print(f"  -> {json.dumps(payload, ensure_ascii=False)[:220]}", flush=True)

    ranked = [
        r
        for r in results
        if isinstance(r.get("wins"), int) and r.get("n") == 2
    ]
    ranked.sort(key=lambda r: (-r["wins"], -(r.get("max_margin") or -1e18)))
    payload = {"results": results, "ranked": ranked, "submit": False}
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("\n=== RANKED ===")
    for r in ranked:
        print(f"{r['wins']}/2 maxM={r.get('max_margin')} {r['tag']}")
    print("errors:", sum(1 for r in results if r.get("error")))
    print("WROTE", OUT)


if __name__ == "__main__":
    main()
