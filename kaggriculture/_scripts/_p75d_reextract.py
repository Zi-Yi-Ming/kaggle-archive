# -*- coding: utf-8 -*-
"""P75d: improve extract for failed notebooks — hunt agent() in string blobs."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, r"D:\桌面\Kaggle\kaggriculture\_scripts")
from _p75c_goodpjw_gate import prep_source  # reuse mocks/future hoist

SCAN = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_p75_mass")
OUT = SCAN / "extracted_v2"
OUT.mkdir(exist_ok=True)

TARGETS = [
    "ahmedberatozer__kaggriculture-v47-reacti",
    "ahmedberatozer__kaggriculture-v48-clear-",
    "ahmedberatozer__kaggregulture-v49-funded",
    "ahmedberatozer__kaggriculture-v49-funded",
    "ahmedberatozer__kaggriculture-v50-early-",
    "guruprasaathas111__game-theoretic-master",
    "lynnsakurai__farming-score-v2-a-better-a",
    "sunil123kumar__kaggregulture-v8",
    "sunil123kumar__kaggriculture-v8",
    "xuanzhang001__kaggriculture-auto-top1",
    "yeshawang__kaggriculture-agent-evolution",
    "aurax7__kaggregulture-shop-router-reacti",
    "aurax7__kaggriculture-shop-router-reacti",
    "boatlee__v16-rc5-high-score-8c-4s-premiu",
    "prvsiyan__kaggriculture-frontier-the-moo",
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
    if "\\n" in text[:500] and text.count("\n") < 5:
        try:
            return text.encode("utf-8").decode("unicode_escape")
        except Exception:
            return text
    return text


def harvest_agents(code: str) -> list[str]:
    blocks = []
    # full code if has def agent at top level-ish
    if re.search(r"(?m)^def\s+agent\s*\(", code):
        blocks.append(code)
    # triple-quoted blobs
    for m in re.finditer(r"(?s)(?:r?\"\"\"|r?''')(.*?)(?:\"\"\"|''')", code):
        blob = decode(m.group(1))
        if re.search(r"def\s+agent\s*\(", blob) and len(blob) > 2000:
            blocks.append(blob)
    # assignments
    for m in re.finditer(
        r"(?is)(?:main_py|MAIN_PY|AGENT_SRC|agent_src|SOURCE|CODE|script)\s*=\s*(r?\"\"\"|r?''')(.*?)(?:\"\"\"|''')",
        code,
    ):
        blob = decode(m.group(2))
        if re.search(r"def\s+agent\s*\(", blob):
            blocks.append(blob)
    return blocks


def main() -> None:
    for d in sorted(SCAN.iterdir()):
        if not d.is_dir() or d.name == "extracted" or d.name == "extracted_v2":
            continue
        nbs = list(d.glob("*.ipynb"))
        if not nbs:
            continue
        raw = nb_code(nbs[0])
        blocks = harvest_agents(raw)
        if not blocks:
            print(f"NO_BLOCK {d.name}")
            continue
        # pick longest block with agent()
        best = max(blocks, key=len)
        try:
            code = prep_source(Path("x"))  # dummy
        except Exception:
            pass
        # manual prep on string
        code = best
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
                "    sys.modules['IPython.display']=_d\n"
                + code
            )
        out = OUT / f"{d.name[:48]}.py"
        out.write_text(code, encoding="utf-8")
        has = bool(re.search(r"def\s+agent\s*\(", code))
        print(f"WROTE {out.name} bytes={out.stat().st_size} agent={has}")


if __name__ == "__main__":
    main()
