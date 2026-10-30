# -*- coding: utf-8 -*-
"""P79c: extract fix + gate remaining large clean agents vs thomas."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "p79", r"D:\桌面\Kaggle\kaggriculture\_scripts\_p79_mass_gate_vs_thomas.py"
)
p79 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p79)

EXT = Path(r"D:\桌面\Kaggle\kaggriculture\_external")
OUTDIR = EXT / "scan_p79_kernels" / "extracted"
OUTDIR.mkdir(parents=True, exist_ok=True)
OUTJSON = Path(r"D:\桌面\Kaggle\kaggriculture\_research\p79c_gate_vs_thomas.json")

# --- fix extractions ---

def extract_ahmed_v48():
    import json as _json
    nbp = EXT / "scan_p79_kernels/ahmedberatozer__kaggriculture-v48-clear-the-queue/kaggriculture-v48-clear-the-queue.ipynb"
    nb = _json.loads(nbp.read_text(encoding="utf-8"))
    src = "".join(nb["cells"][2]["source"]) if isinstance(nb["cells"][2]["source"], list) else nb["cells"][2]["source"]
    # cell writes MAIN.write_text — capture source assigned
    # typically: source = '''...''' or SOURCE = bytes
    out = OUTDIR / "ahmed_v48_embedded.py"
    # find write_text argument
    import re
    # immutable source is the long string after a variable
    m = re.search(r"(?ms)^(?:source|SOURCE|V48_SRC|MAIN_SRC)\s*=\s*(?:b?'''|b?\"\"\")(.+?)(?:'''|\"\"\")", src)
    if m:
        body = m.group(1)
        if body.count("\\n") > 50:
            body = body.encode("utf-8").decode("unicode_escape")
        out.write_text("WORKDIR=__import__('pathlib').Path('.')\n" + body, encoding="utf-8")
        print("ahmed_v48", out.stat().st_size)
        return out
    # if whole cell is mostly the agent with write at end
    code = src
    for marker in ("MAIN.write_text", "Path.write_text", "write_bytes", "hashlib.sha256"):
        i = code.find(marker)
        if i > 10000:
            code = code[:i]
            break
    if "def agent" in code:
        out.write_text("from pathlib import Path\nWORKDIR=Path('.')\n" + code, encoding="utf-8")
        print("ahmed_v48 trimmed", out.stat().st_size)
        return out
    print("ahmed_v48 extract fail")
    return None


def extract_thomas95():
    p = EXT / "scan_p79_kernels/extracted/thomastschinkel__kaggriculture-95-5-win-rate-via-replay-routing.py"
    t = p.read_text(encoding="utf-8")
    cut = t.find("\nif __name__")
    if cut > 0:
        t = t[:cut]
    # also cut markdown after agent
    for mark in ("\n## A full match", "\n720 turns"):
        i = t.find(mark)
        if i > 0:
            t = t[:i]
    out = OUTDIR / "thomas95_clean.py"
    out.write_text(t, encoding="utf-8")
    print("thomas95", out.stat().st_size, "def_agent", "def agent" in t)
    return out


def extract_dmitrii():
    # multi-file: write settings + main/policy/router into a package dir
    nb_dir = EXT / "scan_p79_kernels/dmitriigluzdov__kaggriculture-herd-safe-sale-window-lb-2700"
    nbp = next(nb_dir.glob("*.ipynb"))
    import json as _json
    nb = _json.loads(nbp.read_text(encoding="utf-8"))
    pkg = OUTDIR / "dmitrii_herd_pkg"
    pkg.mkdir(parents=True, exist_ok=True)
    (pkg / "settings.json").write_text('{"sale_horizon": 3}', encoding="utf-8")
    import re
    files = {}
    for cell in nb["cells"]:
        src = "".join(cell.get("source", [])) if isinstance(cell.get("source"), list) else cell.get("source", "")
        for m in re.finditer(r"(?ms)^%%writefile\s+(\S+)\s*\n(.+?)(?=^%%writefile|\Z)", src):
            files[m.group(1)] = m.group(2)
        # notebook-level writefile already in joined
    # also scan joined
    joined = "\n".join(
        "".join(c.get("source", [])) if isinstance(c.get("source"), list) else c.get("source", "")
        for c in nb["cells"]
    )
    for m in re.finditer(r"(?ms)^%%writefile\s+(\S+)\s*\n(.+?)(?=^%%writefile|\Z)", joined):
        files[m.group(1)] = m.group(2)
    for name, body in files.items():
        (pkg / name).write_text(body, encoding="utf-8")
        print("dmitrii file", name, len(body))
    # loader main that imports from package
    loader = pkg / "load_agent.py"
    loader.write_text(
        "import importlib.util, sys\n"
        "from pathlib import Path\n"
        "HERE = Path(__file__).parent\n"
        "sys.path.insert(0, str(HERE))\n"
        "spec = importlib.util.spec_from_file_location('dmain', HERE / 'main.py')\n"
        "m = importlib.util.module_from_spec(spec)\n"
        "spec.loader.exec_module(m)\n"
        "agent = m.agent\n",
        encoding="utf-8",
    )
    return loader


CLEAN = [
    ("farming_score_v5", EXT / "p70_extracted/farming_score_v5_timing_optimized__0.py"),
    ("farming_score_v2", EXT / "p70_extracted/farming_score_v2_a_better_approach__0.py"),
    ("v46_micro", EXT / "p70_extracted/kaggriculture_v46_first_turn_microstructure_and___0.py"),
    ("shop_router_v7", EXT / "p70_extracted/kaggriculture_shop_router_reactive_v7__0.py"),
    ("shop_router_v6", EXT / "p66_extracted/kaggriculture_shop_router_reactive_v6.py"),
    ("shop_router_v5", EXT / "p51_extracted/kaggriculture_shop_router_reactive_v5.py"),
    ("v62_metabalance", EXT / "p66b_extracted/v62_metabalance_kaggriculture.py"),
    ("adaptive_route_v2", EXT / "p67_extracted/adaptive_route_agent_v2.py"),
    ("adaptive_farming", EXT / "p51_extracted2/adaptive_farming_strategy_for_kaggriculture.py"),
    ("pipe5_extract", EXT / "p66_extracted/kaggriculture_pipe_5_terminal_boost.py"),
    ("farming_score_v4", EXT / "p62c_main/farming_score_v4_a_better_shop.py"),
    ("v62_composite", EXT / "git/v66/candidate_v62_composite_bakery_yarn.py"),
    ("prvsiyan_main", EXT / "top5_notebooks/prvsiyan/prvsiyan_main.py"),
    ("danilchil_champ", EXT / "git/danilchil/champ/main.py"),
    ("qeinstein_sub009", EXT / "git/qeinstein/dist/sub-009-moev2/main.py"),
    ("shape_shop_pasture", EXT / "p51_extracted/shape_the_shop_work_the_pasture_kaggriculture.py"),
]


def main():
    payload = {"results": {}}
    if OUTJSON.exists():
        try:
            payload = json.loads(OUTJSON.read_text(encoding="utf-8"))
        except Exception:
            payload = {"results": {}}
    payload.setdefault("results", {})

    extras = []
    a = extract_ahmed_v48()
    if a:
        extras.append(("ahmed_v48_embedded", a))
    t = extract_thomas95()
    if t:
        extras.append(("thomas95", t))
    d = extract_dmitrii()
    if d:
        extras.append(("dmitrii_pkg", d))

    jobs = extras + [(k, p) for k, p in CLEAN if p.exists()]
    for key, path in jobs:
        print(f"=== P79C {key} ===", flush=True)
        try:
            rows = p79.gate_one(key, path, (1, 2))
            sm = p79.summarize(rows)
            res = {"path": str(path), "rows": rows, "summary": sm}
        except Exception as e:
            res = {"path": str(path), "error": str(e)[:200]}
            print("FAIL", key, e, flush=True)
        payload["results"][key] = res
        OUTJSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(key, res.get("summary") or res.get("error"), flush=True)

    print("\n==== P79C SUMMARY ====", flush=True)
    for k, v in payload["results"].items():
        s = v.get("summary") or {}
        print(f"{k:28s} WR={s.get('win_rate')} W={s.get('wins')}/{s.get('n')} m={s.get('mean_margin')} err={s.get('errors')}", flush=True)


if __name__ == "__main__":
    main()
