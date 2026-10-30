# -*- coding: utf-8 -*-
"""Medal R16: shift strawberry volume into the d17-20 high-price window.

Elite price curve: STRAWBERRY peaks ~232 at d18, crashes to ~108 at d29.
R2 tape already sells small strawberry lots in d17-20, then dumps 1000 at d29.
R16: boost those mid-game strawberry sells, shrink the d29 strawberry flood.
"""
from pathlib import Path
import ast

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
src = ROOT / "_push_medal" / "main.py"
dst_dir = ROOT / "_push_medal_r16"
dst_dir.mkdir(parents=True, exist_ok=True)
dst = dst_dir / "main.py"

text = src.read_text(encoding="utf-8")
if "MEDAL_R16_STRAW" not in text:
    overlay = r'''

# ---------------------------------------------------------------------------
# MEDAL_R16_STRAW: d17-20 strawberry boost, d29 flood shrink
# ---------------------------------------------------------------------------
def _r16_patch_tapes(tapes):
    boost_steps = {417, 427, 429, 450, 453, 473, 477, 493, 497, 498, 501}
    for tape in tapes:
        for step in boost_steps:
            if step >= len(tape):
                continue
            mk = tape[step].get("market") or []
            changed = False
            for o in mk:
                if (isinstance(o, list) and len(o) >= 3
                        and o[0] == "SELL" and o[1] == "STRAWBERRY"):
                    q = int(o[2] or 0)
                    if 0 < q < 40:
                        o[2] = min(40, q + 8)
                        changed = True
            if not changed:
                # append a small sell if room
                if len(mk) < 10:
                    mk = list(mk) + [["SELL", "STRAWBERRY", 8]]
                    tape[step]["market"] = mk[:10]
        # shrink d29 strawberry 1000-floods to 250 so less mass dumps at ~108
        for step in range(712, 718):
            if step >= len(tape):
                continue
            for o in (tape[step].get("market") or []):
                if (isinstance(o, list) and len(o) >= 3
                        and o[0] == "SELL" and o[1] == "STRAWBERRY"
                        and int(o[2] or 0) >= 500):
                    o[2] = 250
    return tapes


_R16_POLICY_INIT = Policy.__init__
_R16_PATCHED = {"done": False}


def _r16_policy_init(self, folder):
    _R16_POLICY_INIT(self, folder)
    if not _R16_PATCHED["done"]:
        try:
            _r16_patch_tapes(self.tapes)
            _R16_PATCHED["done"] = True
        except Exception:
            pass


Policy.__init__ = _r16_policy_init
'''
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
  "id": "ziyiming/kaggriculture-medal-r16",
  "title": "Kaggriculture Medal R16",
  "code_file": "main.py",
  "enable_gpu": false,
  "kernel_type": "script"
}
""",
    encoding="utf-8",
)
print("meta ok")
