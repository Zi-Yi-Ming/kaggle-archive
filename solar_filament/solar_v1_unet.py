# -*- coding: utf-8 -*-
"""
Solar Filament v1: 纯 torch 手写轻量 U-Net baseline(patch 切片 + Dice/BCE)
========================================================================
数据:MAGFiLO 1.0(COCO polygon 标注,2048x2048 灰度,19 张 train 图)。
极小样本(19 图)分割,策略:
  - 2048² 大图切 512×512 patch(每图多 patch,扩样)
  - 二值化:4 类 filament 合并为前景(1)
  - 轻量 U-Net(纯 torch,无 torchvision/SMP 依赖,本地 CPU 可冒烟)
  - 损失:Dice + BCE 混合

用法:
  本地冒烟(CPU,极快):  python solar_v1_unet.py --smoke
  完整训练(Kaggle):    python solar_v1_unet.py --epochs 30 --patch 512
"""
import os
import json
import argparse
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image, ImageDraw
from torch.utils.data import Dataset, DataLoader

SEED = 42
torch.manual_seed(SEED)
np.random.seed(SEED)

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
ANN = os.path.join(DATA, "MAGFiLO_1.0_Annotations_kaggle2026_train.json")


# ---------------------------------------------------------------------------
# 数据:COCO polygon -> 二值 mask;大图切 patch
# ---------------------------------------------------------------------------
def load_coco():
    d = json.load(open(ANN, encoding="utf-8"))
    imgs = {im["id"]: im for im in d["images"]}
    by_img = {}
    for a in d["annotations"]:
        by_img.setdefault(a["image_id"], []).append(a)
    return d, imgs, by_img


def polygon_to_mask(poly, W, H):
    m = Image.new("L", (W, H), 0)
    pts = [(poly[i], poly[i + 1]) for i in range(0, len(poly), 2)]
    ImageDraw.Draw(m).polygon(pts, outline=1, fill=1)
    return np.array(m)


class SolarDataset(Dataset):
    """每项 = (patch_img, patch_mask), patch 从标注图随机裁剪。"""

    def __init__(self, imgs, by_img, patch=512, n_patches_per_img=8, seed=SEED):
        self.items = []
        self.masks = {}  # fn -> 全图 mask(预计算,__getitem__ 不再重解析 JSON)
        rng = np.random.RandomState(seed)
        for im_id, anns in by_img.items():
            im = imgs.get(im_id)
            if im is None:
                continue
            fn = os.path.join(DATA, im["file_name"])
            if not os.path.exists(fn):
                continue  # 本地下载的训练图可能只有部分
            W, H = im["width"], im["height"]
            full_mask = np.zeros((H, W), dtype=np.uint8)
            for a in anns:
                for poly in a["segmentation"]:
                    full_mask |= polygon_to_mask(poly, W, H)
            self.masks[fn] = full_mask
            for _ in range(n_patches_per_img):
                x0 = rng.randint(0, max(1, W - patch))
                y0 = rng.randint(0, max(1, H - patch))
                self.items.append((fn, x0, y0))
        self.patch = patch

    def __len__(self):
        return len(self.items)

    def __getitem__(self, i):
        fn, x0, y0 = self.items[i]
        p = self.patch
        img = np.array(Image.open(fn).convert("L"))[y0:y0 + p, x0:x0 + p]
        full = self.masks[fn]
        mask = full[y0:y0 + p, x0:x0 + p]
        img = (img.astype(np.float32) / 255.0)[None]
        mask = (mask > 0).astype(np.float32)[None]
        return torch.from_numpy(img), torch.from_numpy(mask)


# ---------------------------------------------------------------------------
# 轻量 U-Net(纯 torch)
# ---------------------------------------------------------------------------
class DoubleConv(nn.Module):
    def __init__(self, cin, cout):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(cin, cout, 3, padding=1, bias=False), nn.BatchNorm2d(cout), nn.ReLU(inplace=True),
            nn.Conv2d(cout, cout, 3, padding=1, bias=False), nn.BatchNorm2d(cout), nn.ReLU(inplace=True))

    def forward(self, x):
        return self.net(x)


class UNet(nn.Module):
    def __init__(self, n_channels=1, n_classes=1, base=32):
        super().__init__()
        self.inc = DoubleConv(n_channels, base)
        self.d1 = DoubleConv(base, base * 2)
        self.d2 = DoubleConv(base * 2, base * 4)
        self.d3 = DoubleConv(base * 4, base * 8)
        self.pool = nn.MaxPool2d(2)
        self.up3 = nn.ConvTranspose2d(base * 8, base * 4, 2, stride=2)
        self.u3 = DoubleConv(base * 8, base * 4)
        self.up2 = nn.ConvTranspose2d(base * 4, base * 2, 2, stride=2)
        self.u2 = DoubleConv(base * 4, base * 2)
        self.up1 = nn.ConvTranspose2d(base * 2, base, 2, stride=2)
        self.u1 = DoubleConv(base * 2, base)
        self.out = nn.Conv2d(base, n_classes, 1)

    def forward(self, x):
        i = self.inc(x)
        d1 = self.d1(self.pool(i))
        d2 = self.d2(self.pool(d1))
        d3 = self.d3(self.pool(d2))
        u3 = self.u3(torch.cat([self.up3(d3), d2], 1))
        u2 = self.u2(torch.cat([self.up2(u3), d1], 1))
        u1 = self.u1(torch.cat([self.up1(u2), i], 1))
        return self.out(u1)


def dice_loss(p, t, eps=1.0):
    p = torch.sigmoid(p)
    inter = (p * t).sum()
    return 1 - (2 * inter + eps) / (p.sum() + t.sum() + eps)


# ---------------------------------------------------------------------------
# 训练 / 冒烟
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true", help="本地 CPU 冒烟:1 patch 跑 1 步")
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--patch", type=int, default=512)
    ap.add_argument("--batch", type=int, default=2)
    args = ap.parse_args()

    d, imgs, by_img = load_coco()
    print(f"[数据] {len(imgs)} 张图标注 / {sum(len(v) for v in by_img.values())} 个 polygon 标注")
    local = [fn for fn in os.listdir(DATA) if fn.endswith(".jpeg")]
    print(f"[数据] 本地已下载训练图 {len(local)} 张")

    ds = SolarDataset(imgs, by_img, patch=args.patch,
                      n_patches_per_img=1 if args.smoke else 8)
    loader = DataLoader(ds, batch_size=args.batch, shuffle=True)
    print(f"[数据] patch 样本数: {len(ds)}")

    model = UNet(n_channels=1, n_classes=1)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)

    n_epochs = 1 if args.smoke else args.epochs
    for ep in range(n_epochs):
        tot = 0.0
        for x, m in loader:
            p = model(x)
            loss = F.binary_cross_entropy_with_logits(p, m) + dice_loss(p, m)
            opt.zero_grad()
            loss.backward()
            opt.step()
            tot += loss.item()
        print(f"epoch {ep + 1}/{n_epochs}: loss {tot / max(1, len(loader)):.4f}", flush=True)
        if args.smoke:
            break
    print("v1 U-Net 链路跑通 OK" if args.smoke else "v1 训练完成")


if __name__ == "__main__":
    main()
