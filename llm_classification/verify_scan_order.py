# -*- coding: utf-8 -*-
"""验证 llm_pref_v1._scan_hf_models 的排序:distilbert 优先, albert 殿后。"""
import os
import sys
import shutil
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import llm_pref_v1 as m

tmp = tempfile.mkdtemp()
try:
    base = os.path.join(tmp, "kaggle", "input")
    for model in ("albert-large-v2", "distilbert-base-uncased", "roberta-base"):
        d = os.path.join(base, "datasets", "kozodoi", "transformers", model)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "config.json"), "w").close()
        open(os.path.join(d, "pytorch_model.bin"), "w").close()

    # 用 posix 风格模拟 /kaggle/input 相对路径(Windows 下 os.path.relpath 会因盘符报错)
    orig_relpath = os.path.relpath
    def fake_relpath(p, start="/kaggle/input"):
        p2 = p.replace("\\", "/").replace(tmp, "/kaggle/input")
        return posixpath_relpath(p2, start)
    def posixpath_relpath(p, start):
        ps = [x for x in p.split("/") if x]
        ss = [x for x in start.split("/") if x]
        while ps and ss and ps[0] == ss[0]:
            ps.pop(0)
            ss.pop(0)
        return "/".join([".."] * len(ss) + ps)
    os.path.relpath = fake_relpath

    hits = m._scan_hf_models(base=base)
    os.path.relpath = orig_relpath

    print("扫描顺序:")
    for p, desc in hits:
        print("  ", desc)

    first = os.path.basename(hits[0][0])
    last = os.path.basename(hits[-1][0])
    print()
    print("首选:", first, "| 末位:", last)
    assert "distilbert" in first, "首选应为 distilbert"
    assert "albert" in last, "albert 应排最后"
    print("排序断言通过 OK (distilbert 优先, albert 殿后)")
finally:
    shutil.rmtree(tmp, ignore_errors=True)
