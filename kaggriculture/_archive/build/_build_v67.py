# -*- coding: utf-8 -*-
"""Build v67: v66 + shop-router public-state signature → clone route.

Live loss: automatylicza (shop-router style) beat v66 by 12k.
Signature at mid-game: opponent GOOSE>=2, COW>=7, SHEEP>=5, 3 quads.
When matched and no other branch active, switch to clone (victor counter).
"""
from pathlib import Path
import shutil
import ast

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
src_dir = ROOT / "_external" / "git" / "v66"
dst_dir = ROOT / "_push_v67"

if dst_dir.exists():
    shutil.rmtree(dst_dir, ignore_errors=True)
if dst_dir.exists():
    alt = ROOT / "_push_v67_old"
    if alt.exists():
        shutil.rmtree(alt, ignore_errors=True)
    try:
        dst_dir.rename(alt)
    except Exception as e:
        print("rename fail", e)

shutil.copytree(
    src_dir,
    dst_dir,
    ignore=shutil.ignore_patterns(".git", "*.tar.gz", "__pycache__", "build_submission.py"),
)

# Patch candidate_v66_meta_closed_loop.py
cand = dst_dir / "candidate_v66_meta_closed_loop.py"
text = cand.read_text(encoding="utf-8")
if "V67_SHOPROUTER" not in text:
    # Insert signature check inside _advance after step==144 block, before route assignment
    needle = '''        if state["coke_armed"]:
            if _public_signature(obs) == _COKE_STEP144:
                _activate(state, "coke", "known_yarn", step)
            else:
                state["events"].append("144:coke:rejected")
            state["coke_armed"] = False

    route = state["route"]'''
    insert = '''        if state["coke_armed"]:
            if _public_signature(obs) == _COKE_STEP144:
                _activate(state, "coke", "known_yarn", step)
            else:
                state["events"].append("144:coke:rejected")
            state["coke_armed"] = False

    # V67_SHOPROUTER: mid-game livestock signature of shop-router clones
    if step in (144, 216) and not state["route"]:
        try:
            opp = _BASE._v58_farms(obs)[1 - seat] or {}
            counts = _V65._asset_counts(opp)
            goose = int(counts.get("GOOSE", 0) or 0)
            cow = int(counts.get("COW", 0) or 0)
            sheep = int(counts.get("SHEEP", 0) or 0)
            quads = len(opp.get("unlocked_quadrants") or [])
            if goose >= 2 and cow >= 7 and sheep >= 5 and quads >= 3:
                _activate(state, "shoprouter", "clone", step)
        except Exception:
            pass

    route = state["route"]'''
    if needle not in text:
        raise SystemExit("needle not found in v66 meta file")
    text = text.replace(needle, insert, 1)
    text = text.replace(
        '__version__ = "local-v66-public-meta-q2-terminal-h6"',
        '__version__ = "local-v67-shoprouter-clone"',
        1,
    )
    cand.write_text(text, encoding="utf-8")

ast.parse(cand.read_text(encoding="utf-8"))
ast.parse((dst_dir / "main.py").read_text(encoding="utf-8"))
print("OK", dst_dir, "files", len(list(dst_dir.iterdir())))

# smoke import
import os, sys, importlib.util
sys.path.insert(0, str(dst_dir))
old = os.getcwd()
os.chdir(dst_dir)
try:
    spec = importlib.util.spec_from_file_location("v67_smoke", str(dst_dir / "main.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    print("import ok agent", hasattr(m, "agent"))
finally:
    os.chdir(old)
