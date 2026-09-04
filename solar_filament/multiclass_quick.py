# -*- coding: utf-8 -*-
"""Solar 多类(3 类) vs 二值 快速对比:19 张图 CPU 冒烟。"""
import os, json
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image, ImageDraw

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
ANN = os.path.join(DATA, "MAGFiLO_1.0_Annotations_kaggle2026_train.json")

def load():
    d = json.load(open(ANN, encoding="utf-8"))
    imgs = {im["id"]: im for im in d["images"]}
    by = {}
    for a in d["annotations"]:
        by.setdefault(a["image_id"], []).append(a)
    return d, imgs, by

def poly_mask(poly, W, H):
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon([(poly[i], poly[i+1]) for i in range(0, len(poly), 2)], outline=1, fill=1)
    return np.array(m)

# 每张本地图:二值 mask + 3 类 mask(每类一通道)
d, imgs, by = load()
local = [f[:-5] for f in os.listdir(DATA) if f.endswith(".jpeg")]
samples = []
for im_id, anns in by.items():
    im = imgs.get(im_id)
    if im is None or im["file_name"].split(".")[0] not in local:
        continue
    W, H = im["width"], im["height"]
    binm = np.zeros((H, W), np.uint8)
    cls = np.zeros((3, H, W), np.uint8)  # 类1/2/3 -> idx0/1/2
    for a in anns:
        for poly in a["segmentation"]:
            pm = poly_mask(poly, W, H)
            binm |= pm
            if a["category_id"] in (1, 2, 3):
                cls[a["category_id"]-1] |= pm
    samples.append((im["file_name"], binm, cls))
print(f"[多类] 本地可用图 {len(samples)} 张")

PATCH = 128
def get_patch(s, x0, y0):
    fn, binm, cls = s
    img = np.array(Image.open(os.path.join(DATA, fn)).convert("L"))[y0:y0+PATCH, x0:x0+PATCH]
    b = binm[y0:y0+PATCH, x0:x0+PATCH] > 0
    c = cls[:, y0:y0+PATCH, x0:x0+PATCH] > 0
    return img, b, c

def run(n_classes):
    # 简单卷积网络(小模型够冒烟)
    torch.manual_seed(42)
    conv = nn.Sequential(nn.Conv2d(1, 16, 3, padding=1), nn.ReLU(),
                         nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(),
                         nn.Conv2d(32, n_classes, 1)).to("cpu")
    opt = torch.optim.Adam(conv.parameters(), lr=1e-3)
    rng = np.random.RandomState(0)
    losses = []
    for ep in range(8):
        tot = 0.0
        for s in samples:
            for _ in range(3):
                x0 = rng.randint(0, imgs[list(by.keys())[0]]["width"] - PATCH)
                y0 = rng.randint(0, imgs[list(by.keys())[0]]["height"] - PATCH)
                img, b, c = get_patch(s, x0, y0)
                x = torch.from_numpy(img.astype(np.float32)/255.0)[None, None]
                if n_classes == 1:
                    yt = torch.from_numpy(b.astype(np.float32))[None, None]
                    p = conv(x)
                    loss = F.binary_cross_entropy_with_logits(p, yt)
                else:
                    yt = torch.from_numpy(c.astype(np.float32))
                    p = conv(x).squeeze(0)
                    loss = F.binary_cross_entropy_with_logits(p, yt)
                opt.zero_grad(); loss.backward(); opt.step()
                tot += loss.item()
        losses.append(tot/len(samples)/3)
    return losses

l_bin = run(1)
l_multi = run(3)
print("二值 loss:", [round(v,4) for v in l_bin])
print("3类 loss:", [round(v,4) for v in l_multi])
print("结论: 多类可学" if l_multi[-1] < l_multi[0]*0.9 else "多类难学/收敛慢")
