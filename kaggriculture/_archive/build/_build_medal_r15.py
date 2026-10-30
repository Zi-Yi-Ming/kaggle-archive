# -*- coding: utf-8 -*-
"""Medal R15: patch tape endgame dumps at load time.

At steps 670-671 the tape issues MILK/FERT/CARROT ~1000 floods.
R15 splits those into premium-first smaller batches + keeps a residual dump.
Also reorders sells at 712-717 premium-first (C16 window, tape-internal).
"""
from pathlib import Path
import ast
import copy

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
src = ROOT / "_push_medal" / "main.py"
dst_dir = ROOT / "_push_medal_r15"
dst_dir.mkdir(parents=True, exist_ok=True)
dst = dst_dir / "main.py"

text = src.read_text(encoding="utf-8")
if "MEDAL_R15_TAPEPATCH" not in text:
    overlay = r'''

# ---------------------------------------------------------------------------
# MEDAL_R15_TAPEPATCH: rewrite late tape market orders after load
# ---------------------------------------------------------------------------
def _r15_patch_tapes(tapes):
    """Surgically rewrite d27 milk/fert floods and dump-window sell order."""
    rank = {
        "STRAWBERRY": 0, "MELON": 1, "MILK": 2, "WOOL": 3,
        "EGG": 4, "TOMATO": 5, "CARROT": 6, "FERTILIZER": 7, "WHEAT": 9,
    }
    for tape in tapes:
        # 670/671: replace 1000-floods with premium-first moderate batches
        for step in (670, 671):
            if step >= len(tape):
                continue
            mk = tape[step].get("market") or []
            if not any(o and o[0] == "SELL" and len(o) >= 3 and int(o[2] or 0) >= 500 for o in mk):
                continue
            # keep non-huge sells, replace huge ones with 180-batches premium first
            new_mk = []
            for o in mk:
                if o and o[0] == "SELL" and len(o) >= 3 and int(o[2] or 0) >= 500:
                    continue
                new_mk.append(list(o) if isinstance(o, list) else o)
            for item in ("STRAWBERRY", "MILK", "WOOL", "MELON", "CARROT", "FERTILIZER"):
                if len(new_mk) >= 10:
                    break
                new_mk.append(["SELL", item, 180])
            tape[step]["market"] = new_mk[:10]
        # 712-717: reorder sells premium-first, wheat last
        for step in range(712, 718):
            if step >= len(tape):
                continue
            mk = list(tape[step].get("market") or [])
            sells = [(i, list(o)) for i, o in enumerate(mk)
                     if isinstance(o, (list, tuple)) and len(o) >= 2 and o[0] == "SELL"]
            if len(sells) < 2:
                continue
            sells_sorted = sorted(sells, key=lambda t: rank.get(t[1][1], 5))
            slots = [i for i, _ in sells]
            for slot, (_, order) in zip(slots, sells_sorted):
                mk[slot] = order
            tape[step]["market"] = mk[:10]
    return tapes


# Policy stores tapes on first agent() call via Policy.__init__
_R15_POLICY_INIT = Policy.__init__
_R15_PATCHED = {"done": False}


def _r15_policy_init(self, folder):
    _R15_POLICY_INIT(self, folder)
    if not _R15_PATCHED["done"]:
        try:
            _r15_patch_tapes(self.tapes)
            _R15_PATCHED["done"] = True
        except Exception:
            pass


Policy.__init__ = _r15_policy_init
'''
    # insert before final kaggle_agent=agent
    if "kaggle_agent=agent" in text:
        text = text.replace("kaggle_agent=agent", overlay + "\nkaggle_agent=agent\n", 1)
    else:
        text = text + overlay

dst.write_text(text, encoding="utf-8")
ast.parse(dst.read_text(encoding="utf-8"))
print("wrote", dst, dst.stat().st_size)
(dst_dir / "kernel-metadata.json").write_text(
    """{
  "competition_sources": ["kaggriculture"],
  "language": "python",
  "enable_internet": false,
  "is_private": true,
  "id": "ziyiming/kaggriculture-medal-r15",
  "title": "Kaggriculture Medal R15",
  "code_file": "main.py",
  "enable_gpu": false,
  "kernel_type": "script"
}
""",
    encoding="utf-8",
)
print("meta ok")
