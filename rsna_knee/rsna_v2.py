# -*- coding: utf-8 -*-
"""
RSNA Knee Abnormality Detection — v2(按 Anatomical_Plane 分平面独立建模 + 融合)
================================================================================
相对 baseline(rsna_baseline.py)的核心改动:
- baseline 把 study 内所有平面的 series 粗暴拼成通道;v2 按 Anatomical_Plane
  (Axial / Sagittal / Coronal)各训一个独立 ResNet34,平面内部再做 2.5D clip;
- test 推理时每个平面模型独立预测,最终按 各平面 OOF 宏平均 AUC 加权融合
  (权重可 --fuse weight 用 AUC 加权,或 --fuse mean 简单平均);
- 某 study 缺某平面时,融合只对该 study 实际可用的平面归一化权重。

其余逻辑(软标签填充、GroupKFold、valid 掩码损失、DICOM 预处理)与 baseline 一致。

运行环境:Kaggle Notebook(GPU,挂载比赛数据 + 社区软标签数据集)。
用法:
    !python rsna_v2.py --epochs 3 --batch 16 --n-clips 2 --planes sagittal,coronal
    !python rsna_v2.py --epochs 3 --batch 16 --fuse weight --pseudo-conf 0.3
输出: submission.csv(StudyInstanceUID + 12 列置信分数)
"""
import argparse
import os
import sys
import time
import warnings

import numpy as np
import pandas as pd

try:
    import torch
    import torch.nn as nn
    from torch.utils.data import Dataset, DataLoader
    from torch.optim import AdamW
    from torch.optim.lr_scheduler import CosineAnnealingLR
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

try:
    import torchvision.models as tvm
    HAS_TV = True
except ImportError:
    HAS_TV = False

try:
    import pydicom
    HAS_PYDICOM = True
except ImportError:
    HAS_PYDICOM = False

from sklearn.model_selection import GroupKFold
from sklearn.metrics import roc_auc_score

warnings.filterwarnings("ignore")

LABELS = ["ACL", "MCL", "Medial Meniscus", "Lateral Meniscus",
          "Medial OA", "Lateral OA", "PF OA", "Effusion", "Synovitis",
          "Baker's", "Contusion", "Fracture"]
LABELS_EN = ["ACL", "MCL", "MedialMeniscus", "LateralMeniscus",
             "MedialOA", "LateralOA", "PFOA", "Effusion", "Synovitis",
             "Bakers", "Contusion", "Fracture"]  # 列名安全化(写提交用)
PLANES = ["Axial", "Sagittal", "Coronal"]

IMG_SIZE = 224
CLIP = 3          # 每 clip 切片数(prev/center/next)
MAX_SERIES = 4    # 每 study 每个平面最多取的 series 数(v2 按平面取,单平面 series 更少,4 足够)
FOLDS = 5
SEED = 42


def resolve_paths():
    """数据定位顺序:1) /kaggle/input 挂载;2) kagglehub 自动下载;3) 本地 rsna_knee/ 目录。"""
    # 1) Kaggle 挂载(兼容多层挂载:/kaggle/input/<数据名>/ 或 /kaggle/input/<分类>/<数据名>/)
    if os.path.isdir("/kaggle/input"):
        for sub in sorted(os.listdir("/kaggle/input")):
            d = os.path.join("/kaggle/input", sub)
            for cand in (d, os.path.join(d, sub)):  # 处理 Kaggle 双层挂载
                if os.path.exists(os.path.join(cand, "train.csv")):
                    return cand, "/kaggle/working"
            if os.path.isdir(d):  # 再往下一层找(如 /kaggle/input/competitions/<name>/)
                for sub2 in sorted(os.listdir(d)):
                    cand = os.path.join(d, sub2)
                    if os.path.exists(os.path.join(cand, "train.csv")):
                        return cand, "/kaggle/working"
        print("[诊断] /kaggle/input 存在,但没找到含 train.csv 的目录。实际挂载内容如下:", flush=True)
        for sub in sorted(os.listdir("/kaggle/input")):
            p = os.path.join("/kaggle/input", sub)
            try:
                inner = os.listdir(p)
            except OSError:
                inner = ["(无法读取)"]
            print(f"  /kaggle/input/{sub}/  ->  {inner[:8]}", flush=True)
        print("[诊断] 如果你挂的是 '作者数据包/别人的 kernel 输出', 里面没有 train.csv 和 train_series/,",
              "必须挂比赛数据本体 rsna-knee-abnormality-detection (Add Input -> Competitions 标签页)", flush=True)
    # 2) kagglehub 兜底:未挂载时自动下载比赛数据(Kaggle Notebook 内置凭据)
    try:
        import kagglehub
        d = kagglehub.competition_download("rsna-knee-abnormality-detection")
        if os.path.exists(os.path.join(d, "train.csv")):
            print(f"[路径] 未挂载,已用 kagglehub 获取数据: {d}", flush=True)
            return d, "/kaggle/working"
    except ImportError:
        pass  # 本地未装 kagglehub
    except Exception as e:
        print(f"[提示] kagglehub 下载数据失败: {e}", flush=True)
    # 3) 本地回退(脚本目录 / cwd / cwd 下的 rsna_knee 子目录都找)
    cands = []
    try:
        cands.append(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        pass
    cands.append(os.getcwd())
    for base in list(cands):
        cands.append(os.path.join(base, "rsna_knee"))
    seen = set()
    for base in cands:
        if base in seen:
            continue
        seen.add(base)
        if os.path.exists(os.path.join(base, "train.csv")):
            return base, base
    sys.exit("找不到数据:请先在比赛页加入比赛并同意数据规则,再 Add Input 挂载 "
             "rsna-knee-abnormality-detection;本地请在 rsna_knee/ 下运行。")


_PSEUDO_FILES = ("train_folds_with_pseudo.csv", "train_with_pseudo.csv",
                 "train_with_soft_labels.csv", "train_pseudo.csv")
_SKIP_DIRS = {"train_series", "test_series"}  # DICOM 大目录,绝不去遍历


def _scan_pseudo(base, depth=0, max_depth=3):
    """递归在挂载目录下找软标签 CSV(限制深度,跳过 DICOM 目录)。

    返回 (DataFrame 或 None, 来源描述)。识别规则:含 StudyInstanceUID 且至少有一个
    pseudo_ 前缀列(如 pseudo_ACL)。找不到返回 (None, "")。
    """
    if depth > max_depth or not os.path.isdir(base):
        return None, ""
    try:
        entries = sorted(os.listdir(base))
    except OSError:
        return None, ""
    for fn in _PSEUDO_FILES:
        p = os.path.join(base, fn)
        if os.path.exists(p):
            try:
                cand = pd.read_csv(p)
            except Exception:
                continue
            if "StudyInstanceUID" in cand.columns and any(
                    c.startswith("pseudo_") for c in cand.columns):
                return cand, os.path.relpath(p, "/kaggle/input")
    for sub in entries:
        if sub in _SKIP_DIRS:
            continue
        cand, src = _scan_pseudo(os.path.join(base, sub), depth + 1, max_depth)
        if cand is not None:
            return cand, src
    return None, ""


def find_pseudo_dataset():
    """在 /kaggle/input 下递归扫描社区软标签数据集(LLM 从报告提取的伪标签)。

    兼容单层(/kaggle/input/<slug>/)与多层(/kaggle/input/datasets/<slug>/)挂载。
    返回 (DataFrame 或 None, 来源描述);找不到返回 (None, "")。
    """
    if not os.path.isdir("/kaggle/input"):
        return None, ""
    return _scan_pseudo("/kaggle/input")


def load_labels(root, pseudo_conf=0.0):
    """返回 train study 级标签 DataFrame(行=StudyInstanceUID, 列=LABELS, 0/1/NaN)。

    标签来源优先级:
    1. 官方 train.csv 标注(0/1,仅 58/4407 例);
    2. 社区 LLM 软标签(pseudo_* 列,0-1 概率)——只在官方缺失处填充,
       若数据集带置信度列(conf_/confidence_/pseudo_conf_),低于 pseudo_conf 的丢弃
       (保留 NaN 不参与损失),即"置信度过滤";
    3. 以上都没有的格子保持 NaN(不污染损失)。
    """
    train = pd.read_csv(os.path.join(root, "train.csv"))
    df = train[["StudyInstanceUID"] + LABELS].copy()

    pseudo, src = find_pseudo_dataset()
    if pseudo is None:
        print("[标签] 未发现社区软标签数据集(未挂载或列不匹配),仅官方 58 例标注可用")
        n_lab = df[LABELS].notna().sum().sum()
        print(f"[标签] {len(df)} 个 study,有效标签格 {n_lab}/{len(df) * len(LABELS)}")
        return df

    print(f"[标签] 发现社区软标签数据集: {src}  shape={pseudo.shape}")
    pseudo = pseudo.set_index("StudyInstanceUID")

    filled_cnt = {c: 0 for c in LABELS}
    for c in LABELS:
        mask = df[c].isna().values
        if not mask.any():
            continue
        pcol = f"pseudo_{c}" if f"pseudo_{c}" in pseudo.columns else (c if c in pseudo.columns else None)
        if pcol is None:
            print(f"[标签] 跳过 {c}:软标签数据集中无 pseudo_{c} 列")
            continue
        filled = pd.to_numeric(pseudo[pcol], errors="coerce")
        conf_col = next((cc for cc in (f"pseudo_conf_{c}", f"conf_{c}", f"confidence_{c}")
                         if cc in pseudo.columns), None)
        if conf_col is not None and pseudo_conf > 0:
            conf = pd.to_numeric(pseudo[conf_col], errors="coerce")
            filled = filled.where(conf >= pseudo_conf)
        uids = df.loc[mask, "StudyInstanceUID"]
        vals = filled.reindex(uids).values
        filled_cnt[c] = int(pd.notna(vals).sum())
        df.loc[mask, c] = vals

    print(f"[标签] 填充统计({len(df)} 个 study):")
    for c in LABELS:
        print(f"  {c:18s} 官方 {int((df[c].notna().sum()) - 0)} + 伪标签填充 {filled_cnt[c]:4d}"
              f" = 有效 {int(df[c].notna().sum()):5d}")
    return df


def read_dicom_slices(dcm_dir, series_uid):
    """读取一个 series 的所有切片,按物理位置排序,返回 [(path, z)]。"""
    sdir = os.path.join(dcm_dir, series_uid)
    files = [os.path.join(sdir, f) for f in os.listdir(sdir) if f.endswith(".dcm")] if os.path.isdir(sdir) else []
    if not files:
        return []
    rows = []
    for f in files:
        try:
            d = pydicom.dcmread(f, stop_before_pixels=False)
            pos = d.get("ImagePositionPatient")
            z = float(pos[2]) if pos is not None and len(pos) >= 3 else None
            rows.append((f, z))
        except Exception:
            continue
    rows.sort(key=lambda r: (r[1] is None, r[1] if r[1] is not None else 0.0))
    return rows


# ---------------- DICOM -> 2.5D clip 预处理 ----------------

def window_and_resize(dcm, img_size=IMG_SIZE):
    """单张切片:Rescale 后百分位窗口化 -> [0,1] -> resize 224。"""
    arr = dcm.pixel_array.astype(np.float32)
    slope = float(dcm.get("RescaleSlope", 1))
    inter = float(dcm.get("RescaleIntercept", 0))
    arr = arr * slope + inter
    if dcm.get("PhotometricInterpretation") == "MONOCHROME1":
        arr = arr.max() - arr
    lo, hi = np.percentile(arr, [1, 99])
    arr = np.clip((arr - lo) / max(hi - lo, 1e-6), 0, 1)
    from PIL import Image
    img = Image.fromarray((arr * 255).astype(np.uint8)).resize((img_size, img_size), Image.BILINEAR)
    return np.asarray(img, dtype=np.float32) / 255.0


def make_clips(series_rows, n_clips=2, img_size=IMG_SIZE):
    """从排序好的切片列表生成若干 3 通道 clip(相邻三张)。"""
    clips = []
    paths = [r[0] for r in series_rows]
    if len(paths) < CLIP:
        return clips
    step = max(1, (len(paths) - 2) // n_clips)
    for c in range(1, len(paths) - 1, step):
        if len(clips) >= n_clips:
            break
        chan = []
        ok = True
        for k in (c - 1, c, c + 1):
            try:
                dcm = pydicom.dcmread(paths[k])
                chan.append(window_and_resize(dcm, img_size))
            except Exception:
                ok = False
                break
        if ok:
            clips.append(np.stack(chan, axis=0))  # (3, H, W)
    return clips


# ---------------- 数据集(v2:按平面过滤 series) ----------------

class KneeDataset(Dataset):
    """study 级数据集,只取指定 Anatomical_Plane 的 series,拼成 (C*3, H, W)。"""

    def __init__(self, studies, labels_df, dcm_root, series_df, plane,
                 has_targets=True, n_clips=2):
        self.studies = studies
        self.labels_df = labels_df
        self.dcm_root = dcm_root
        self.series_df = series_df
        self.plane = plane
        self.has_targets = has_targets
        self.n_clips = n_clips
        self.cache = {}

    def _load_study(self, uid):
        if uid in self.cache:
            return self.cache[uid]
        srows = self.series_df[self.series_df["StudyInstanceUID"] == uid]
        if "Anatomical_Plane" in srows.columns:
            srows = srows[srows["Anatomical_Plane"] == self.plane]
            srows = srows.sort_values("Fluid_Sensitive", kind="stable").drop_duplicates(
                subset=["Fluid_Sensitive"]).head(MAX_SERIES)
        else:
            srows = srows.head(MAX_SERIES)
        clips = []
        for _, sr in srows.iterrows():
            sid = sr["SeriesInstanceUID"]
            rows = read_dicom_slices(self.dcm_root, sid)
            clips.extend(make_clips(rows, n_clips=self.n_clips))
        self.cache[uid] = clips
        return clips

    def __len__(self):
        return len(self.studies)

    def __getitem__(self, i):
        uid = self.studies[i]
        clips = self._load_study(uid)
        if not clips:
            x = np.zeros((CLIP, IMG_SIZE, IMG_SIZE), dtype=np.float32)
        else:
            x = np.concatenate(clips[: self.n_clips], axis=0)  # (k*3, H, W)
            pad = self.n_clips * CLIP - x.shape[0]
            if pad > 0:
                x = np.concatenate([x, np.zeros((pad, IMG_SIZE, IMG_SIZE), dtype=np.float32)])
            elif pad < 0:
                x = x[: self.n_clips * CLIP]
        x = torch.tensor(x, dtype=torch.float32)
        y = torch.zeros(len(LABELS), dtype=torch.float32)
        valid = torch.zeros(len(LABELS), dtype=torch.float32)
        if self.has_targets:
            row = self.labels_df[self.labels_df["StudyInstanceUID"] == uid]
            if len(row):
                for j, c in enumerate(LABELS):
                    v = row.iloc[0][c]
                    if pd.notna(v):
                        y[j] = float(v)
                        valid[j] = 1.0
        return x, y, valid


# ---------------- 模型 ----------------

_PRETRAINED_TRIED = [False]  # 模块级标志:下载失败过一次就不再反复重试


def _build_resnet34(use_pretrained=False):
    """构造 ResNet34 并加载 ImageNet 预训练权重。

    默认 use_pretrained=False:随机初始化,不联网(适合未开启 Internet 的 Notebook)。
    开启 --pretrained 时才尝试下载(带重试),多次失败则回退随机初始化并打印警告。
    成功下载后权重会缓存到 ~/.cache/torch,后续 fold 秒加载。
    """
    if not use_pretrained:
        print("[权重] 未开启 --pretrained,使用随机初始化(不联网;如需预训练请加 --pretrained 并开启 Internet)", flush=True)
        return tvm.resnet34(weights=None)
    if _PRETRAINED_TRIED[0]:
        return tvm.resnet34(weights=None)  # 之前已确认下载不了,直接随机
    for attempt in range(1, 4):
        try:
            net = tvm.resnet34(weights=tvm.ResNet34_Weights.IMAGENET1K_V1
                               if hasattr(tvm, "ResNet34_Weights") else None)
            return net
        except Exception as e:
            print(f"[权重] ResNet34 预训练下载失败(第 {attempt}/3 次): {e}", flush=True)
            time.sleep(5)
    _PRETRAINED_TRIED[0] = True
    print("[权重] 3 次均失败,改用随机初始化(精度会明显下降;建议重试或挂载预训练权重数据集)", flush=True)
    return tvm.resnet34(weights=None)


class KneeModel(nn.Module):
    """ResNet34 共享 backbone + 全局池化 + 12 sigmoid 头(每个平面一个实例)。"""

    def __init__(self, num_labels=len(LABELS), channels=CLIP, pretrained=False):
        super().__init__()
        if HAS_TV:
            self.backbone = _build_resnet34(use_pretrained=pretrained)
        else:
            raise RuntimeError("需要 torchvision(请在 Kaggle Notebook GPU 环境运行)")
        self.backbone.conv1 = nn.Conv2d(channels, 64, kernel_size=7, stride=2, padding=3, bias=False)
        self.backbone.fc = nn.Identity()
        self.head = nn.Linear(512, num_labels)

    def forward(self, x):
        feat = self.backbone(x)  # (B, 512)
        return self.head(feat)   # logits (B, 12)


# ---------------- 训练 / 验证 ----------------

def train_epoch(model, loader, opt, crit, device):
    model.train()
    tot, cnt = 0.0, 0
    for x, y, valid in loader:
        x, y, valid = x.to(device), y.to(device), valid.to(device)
        opt.zero_grad()
        out = model(x)
        if valid.sum() == 0:
            continue
        loss = (crit(out, y) * valid).sum() / valid.sum()
        loss.backward()
        opt.step()
        tot += loss.item() * len(x)
        cnt += len(x)
    return tot / max(cnt, 1)


@torch.no_grad()
def predict(model, loader, device):
    model.eval()
    outs = []
    for x, _, _ in loader:
        x = x.to(device)
        out = torch.sigmoid(model(x)).cpu().numpy()
        outs.append(out)
    return np.concatenate(outs, axis=0)


def run_fold(model, train_ds, val_ds, device, args):
    train_loader = DataLoader(train_ds, batch_size=args.batch, shuffle=True,
                              num_workers=args.workers, drop_last=False)
    val_loader = DataLoader(val_ds, batch_size=args.batch, shuffle=False,
                            num_workers=args.workers, drop_last=False)
    opt = AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    sched = CosineAnnealingLR(opt, T_max=args.epochs)
    crit = nn.BCEWithLogitsLoss(reduction="none")
    for ep in range(args.epochs):
        t0 = time.time()
        loss = train_epoch(model, train_loader, opt, crit, device)
        sched.step()
        if args.verbose:
            print(f"  epoch {ep + 1}/{args.epochs} loss {loss:.4f} ({time.time() - t0:.0f}s)", flush=True)
    val_pred = predict(model, val_loader, device)
    val_uid = np.array(val_ds.studies)  # shuffle=False,顺序与数据集一致
    return val_pred, val_uid


# ---------------- 推理 / 融合 / 提交 ----------------

def predict_test(model, test_df, series_df, root, device, plane, n_clips=2):
    """对 test 每个 study 按指定平面收集 clips,预测 12 个概率。"""
    ds = KneeDataset(test_df["StudyInstanceUID"].tolist(), None, root, series_df,
                     plane, has_targets=False, n_clips=n_clips)
    loader = DataLoader(ds, batch_size=16, shuffle=False, num_workers=0)
    return predict(model, loader, device)


def plane_oof_auc(oof, labels_df, uid_list):
    """计算一个平面模型在指定 study 子集上的宏平均 OOF AUC(只算有标注的列)。"""
    aucs = []
    for j, c in enumerate(LABELS):
        y_true = labels_df.set_index("StudyInstanceUID")[c].reindex(uid_list).values.astype(float)
        valid = ~np.isnan(y_true)
        if valid.sum() >= 20:
            aucs.append(roc_auc_score(y_true[valid], oof[valid, j]))
    return float(np.mean(aucs)) if aucs else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=2)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--workers", type=int, default=0)
    ap.add_argument("--n-clips", type=int, default=2)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--folds", type=int, default=FOLDS)
    ap.add_argument("--planes", type=str, default=",".join(PLANES),
                    help="逗号分隔的平面子集,如 axial,sagittal(小写,不区分大小写)")
    ap.add_argument("--fuse", type=str, default="weight",
                    choices=["weight", "mean"],
                    help="平面融合方式:weight=按 OOF AUC 加权;mean=简单平均")
    ap.add_argument("--pseudo-conf", type=float, default=0.0,
                    help="伪标签置信度过滤阈值(0=不过滤;0.5=丢弃置信度<0.5的伪标签)")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--pretrained", action="store_true",
                    help="尝试下载 ImageNet 预训练权重(需开启 Internet);默认随机初始化不联网")
    ap.add_argument("--data", type=str, default="",
                    help="显式指定数据根目录(如 kagglehub.competition_download 返回的 path),"
                         "指定后跳过自动查找")
    args, _ = ap.parse_known_args()

    if not HAS_TORCH or not HAS_TV or not HAS_PYDICOM:
        sys.exit("依赖缺失:请在 Kaggle Notebook(GPU)环境运行(torch/torchvision/pydicom);本地仅可做数据层验证。")

    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

    if args.data:
        if os.path.exists(os.path.join(args.data, "train.csv")):
            root, out = args.data, args.data
            print(f"[数据] 使用 --data 指定目录: {root}")
        else:
            sys.exit(f"--data 指定目录 {args.data} 下没有 train.csv,请检查路径")
    else:
        root, out = resolve_paths()
    print(f"[数据] root={root}  out={out}")

    train_csv = pd.read_csv(os.path.join(root, "train.csv"))
    labels_df = load_labels(root, pseudo_conf=args.pseudo_conf)
    series_df = pd.read_csv(os.path.join(root, "train_series.csv"))
    test_df = pd.read_csv(os.path.join(root, "test.csv"))
    test_series = pd.read_csv(os.path.join(root, "test_series.csv"))
    dcm_train = os.path.join(root, "train_series")
    dcm_test = os.path.join(root, "test_series")
    print(f"[数据] train {len(train_csv)} study / test {len(test_df)} study / series {len(series_df)}")

    planes = [p.strip().title() for p in args.planes.split(",") if p.strip()]
    planes = [p for p in planes if p in PLANES]
    if not planes:
        sys.exit(f"--planes 无效,可选: {PLANES}")
    print(f"[平面] 使用 {planes}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[设备] {device}")

    gkf = GroupKFold(n_splits=args.folds)
    groups = train_csv["StudyInstanceUID"].values

    # 每个平面独立跑折,记录 OOF 与 test 预测
    plane_oof, plane_test, plane_auc, plane_uids = {}, {}, {}, {}
    for plane in planes:
        print(f"\n########## 平面: {plane} ##########")
        oof = np.zeros((len(train_csv), len(LABELS)))
        for k, (tr_idx, va_idx) in enumerate(gkf.split(train_csv, groups=groups)):
            tr_studies = train_csv.iloc[tr_idx]["StudyInstanceUID"].tolist()
            va_studies = train_csv.iloc[va_idx]["StudyInstanceUID"].tolist()
            tr_ds = KneeDataset(tr_studies, labels_df, dcm_train, series_df, plane,
                                n_clips=args.n_clips)
            va_ds = KneeDataset(va_studies, labels_df, dcm_train, series_df, plane,
                                n_clips=args.n_clips)
            model = KneeModel(pretrained=args.pretrained).to(device)
            print(f"[折 {k + 1}/{args.folds}] {plane} train {len(tr_ds)} / val {len(va_ds)}", flush=True)
            val_pred, val_uid = run_fold(model, tr_ds, va_ds, device, args)
            for j, uid in enumerate(val_uid):
                row = np.where(train_csv["StudyInstanceUID"].values == uid)[0]
                if len(row):
                    oof[row[0]] = val_pred[j]
        # 该平面 OOF AUC(宏平均)
        uid_list = train_csv["StudyInstanceUID"].tolist()
        auc = plane_oof_auc(oof, labels_df, uid_list)
        print(f"[{plane}] OOF 宏平均 AUC {auc:.4f}")
        # 该平面 test 预测(与 train 行对齐:最后一折模型)
        plane_oof[plane], plane_test[plane] = oof, predict_test(
            model, test_df, test_series, dcm_test, device, plane, n_clips=args.n_clips)
        plane_auc[plane], plane_uids[plane] = auc, uid_list

    # 融合
    if args.fuse == "weight":
        wsum = sum(max(a, 1e-6) for a in plane_auc.values())
        weights = {p: max(a, 1e-6) / wsum for p, a in plane_auc.items()}
        print(f"[融合] OOF AUC 加权: { {p: round(w, 4) for p, w in weights.items()} }")
    else:
        weights = {p: 1.0 / len(planes) for p in planes}
        print("[融合] 简单平均")
    fused = np.zeros_like(plane_test[planes[0]])
    for p, w in weights.items():
        fused += w * plane_test[p]
    sub = pd.DataFrame({"StudyInstanceUID": test_df["StudyInstanceUID"], **{
        LABELS_EN[j]: fused[:, j] for j in range(len(LABELS))}})
    sub_path = os.path.join(out, "submission.csv")
    sub.to_csv(sub_path, index=False)
    print(f"\n提交文件已生成: {sub_path}  shape={sub.shape}")


if __name__ == "__main__":
    main()
