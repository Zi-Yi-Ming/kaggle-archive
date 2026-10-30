# -*- coding: utf-8 -*-
"""Extract executable agents from new public notebooks."""
from __future__ import annotations

import json
import re
from pathlib import Path

NB = Path(r"D:\桌面\Kaggle\kaggriculture\_external\p50_candidates_nb")
OUT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\p51_extracted")
OUT.mkdir(parents=True, exist_ok=True)

DROP = re.compile(
    r"^\s*(!|%)|get_ipython|^\s*from IPython|^\s*import IPython|ipywidgets"
)


def clean(code: str) -> str:
    lines = []
    for line in code.splitlines():
        if DROP.search(line):
            continue
        lines.append(line)
    text = "\n".join(lines)
    # move __future__ up
    futures = re.findall(r"^from __future__ import .+$", text, flags=re.M)
    text = re.sub(r"^from __future__ import .+\n?", "", text, flags=re.M)
    head = ("\n".join(futures) + "\n") if futures else ""
    stub = "def display(*a, **k):\n    pass\n\n"
    return head + stub + text


def extract(nb_path: Path):
    nb = json.loads(nb_path.read_text(encoding="utf-8"))
    parts = []
    for c in nb.get("cells", []):
        if c.get("cell_type") == "code":
            src = "".join(c.get("source") or [])
            # keep writefile bodies
            src = re.sub(r"^%%writefile[^\n]*\n", "", src)
            parts.append(src)
    code = clean("\n\n".join(parts))
    has = "def agent" in code or "def build_agent" in code
    return code, has


def main():
    for nb in sorted(NB.glob("*.ipynb")):
        code, has = extract(nb)
        name = re.sub(r"[^a-zA-Z0-9]+", "_", nb.stem)[:48] + ".py"
        out = OUT / name
        out.write_text(code, encoding="utf-8")
        print(f"{nb.name[:50]:50s} agent={has} chars={len(code)} -> {name}")


if __name__ == "__main__":
    main()
