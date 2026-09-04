# -*- coding: utf-8 -*-
"""Solar patch 大小/增广实验:19 张图 CPU,对比 128/256 patch 训练信号。"""
import os, json
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image, ImageDraw

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
ANN = os.path.join(DATA, "MAGFiLO_1.0_Annotations_kaggle2026_train.json")
d = json.load(open(ANN, encoding="utf-8"))
imgs = {im["id"]: im for im in d["images"]}
by = {}
for a in d["annotations"]:
    by.setdefault(a["image_id"], []).append(a)
local = {f[:-5] for f in os.listdir(DATA) if f.endswith(".jpeg")}
W0, H0 = 2048, 2048

def poly_mask(poly):
    m = Image.new("L", (W0, H0), 0)
    ImageDraw.Draw(m).polygon([(poly[i], poly[i+1]) for i in range(0, len(poly), 2)], outline=1, fill=1)
    return np.array(m)

def mask_of(im_id):
    m = np.zeros((H0, W0), np.uint8)
    for a in by.get(im_id, []):
        for poly in a["segmentation"]:
            m |= poly_mask(poly)
    return m > 0

# 预计算所有本地图的二值 mask
masks = {}
for im_id, im in imgs.items():
    if im["file_name"].split(".")[0] in local:
        masks[im_id] = mask_of(im_id)
keys = list(masks.keys())
print(f"[数据] 本地图 {len(keys)} 张(去重后实际文件 {len(local)} 个)")

def run(patch, n_patch):
    torch.manual_seed(42)
    conv = nn.Sequential(nn.Conv2d(1, 16, 3, padding=1), nn.ReLU(),
                         nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(),
                         nn.Conv2d(32, 1, 1))
    opt = torch.optim.Adam(conv.parameters(), lr=1e-3)
    rng = np.random.RandomState(0)
    losses = []
    for ep in range(6):
        tot = 0.0
        for _ in range(40):
            im_id = keys[rng.randint(len(keys))]
            fn = imgs[im_id]["file_name"]
            x0 = rng.randint(0, W0 - patch); y0 = rng.randint(0, H0 - patch)
            img = np.array(Image.open(os.path.join(DATA, fn)).convert("L"))[y0:y0+patch, x0:x0+patch]
            m = masks[im_id][y0:y0+patch, x0:x0+patch]
            x = torch.from_numpy(img.astype(np.float32)/255.0)[None, None]
            yt = torch.from_numpy(m.astype(np.float32))[None, None]
            p = conv(x)
            loss = F.binary_cross_entropy_with_logits(p, yt)
            opt.zero_grad(); loss.backward(); opt.step()
            tot += loss.item()
        losses.append(tot/40)
    return losses

print("patch=128:", [round(v,4) for v in run(128, 1)])
print("patch=256:", [round(v,4) for v in run(256, 1)])
# patch 内有 filament 的比例(信号密度)
pos_ratio = []
for im_id in keys:
    m = masks[im_id]
    pos_ratio.append(m.mean())
print(f"[信号密度] 全图 filament 占比均值 {np.mean(pos_ratio):.3%} min {np.min(pos_ratio):.3%} max {np.max(pos_ratio):.3%}")
