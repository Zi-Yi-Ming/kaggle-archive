# -*- coding: utf-8 -*-
"""
RSNA Knee Abnormality Detection — baseline(2.5D ResNet34 多视图)
=================================================================
目标:检测 12 种膝盖异常,宏平均 AUC。

思路(参考公开 baseline):
- 每个 study 有多个 DICOM series(不同解剖平面/序列);
- 2.5D clip = 同一 series 内相邻 3 张切片 [prev, center, next] 合成 3 通道,
  用 2D backbone(ResNet34 预训练)提取特征(无 3D 卷积,省显存);
- study 级多标签:series 特征池化 -> 12 个 sigmoid 头;
- 折划分:GroupKFold(by StudyInstanceUID),防同一患者泄漏;
- 标签:官方 train.csv 仅 58/4407 有标注(98.7% NaN),baseline 用
  官方标注 + 社区 LLM 软标签(若挂载)兜底,其余留空不参与损失。

运行环境:Kaggle Notebook(GPU,挂载比赛数据)。本地仅做语法/数据层验证。

用法(Kaggle Notebook):
    !python rsna_baseline.py --epochs 3 --batch 16 --img-size 224
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

IMG_SIZE = 224
CLIP = 3          # 每 clip 切片数(prev/center/next)
MAX_SERIES = 8    # 每 study 最多取的 series 数
FOLDS = 5
SEED = 42


def resolve_paths():
    """数据定位顺序:1) /kaggle/input 挂载;2) kagglehub 自动下载;3) 本地 rsna_knee/ 目录。"""
    # 1) Kaggle 挂载
    if os.path.isdir("/kaggle/input"):
        for sub in sorted(os.listdir("/kaggle/input")):
            d = os.path.join("/kaggle/input", sub)
            if os.path.exists(os.path.join(d, "train.csv")):
                return d, "/kaggle/working"
        print("[诊断] /kaggle/input 存在,但没有任何子目录含 train.csv;实际内容:",
              os.listdir("/kaggle/input"))
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
    # 3) 本地回退
    cands = []
    try:
        cands.append(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        pass
    cands.append(os.getcwd())
    for base in cands:
        if os.path.exists(os.path.join(base, "train.csv")):
            return base, base
    sys.exit("找不到数据:请先在比赛页加入比赛并同意数据规则,再 Add Input 挂载 "
             "rsna-knee-abnormality-detection;本地请在 rsna_knee/ 下运行。")


def find_pseudo_dataset():
    """在 /kaggle/input 下扫描社区软标签数据集(LLM 从报告提取的伪标签)。

    返回 (DataFrame 或 None, 来源描述)。识别规则:含 StudyInstanceUID 且至少有一个
    pseudo_ 前缀列(如 pseudo_ACL)。找不到返回 (None, "")。
    """
    if not os.path.isdir("/kaggle/input"):
        return None, ""
    for sub in sorted(os.listdir("/kaggle/input")):
        d = os.path.join("/kaggle/input", sub)
        for fn in ("train_folds_with_pseudo.csv", "train_with_pseudo.csv",
                   "train_with_soft_labels.csv", "train_pseudo.csv"):
            p = os.path.join(d, fn)
            if not os.path.exists(p):
                continue
            cand = pd.read_csv(p)
            if "StudyInstanceUID" in cand.columns and any(c.startswith("pseudo_") for c in cand.columns):
                return cand, f"{sub}/{fn}"
    return None, ""


def load_labels(root, pseudo_conf=0.0):
    """返回 train study 级标签 DataFrame(行=StudyInstanceUID, 列=LABELS, 0/1/NaN)。

    标签来源优先级:
    1. 官方 train.csv 标注(0/1,仅 58/4407 例);
    2. 社区 LLM 软标签(pseudo_* 列,0-1 概率)——只在官方缺失处填充,
       若数据集带置信度列(conf_/confidence_/pseudo_conf_),低于 pseudo_conf 的丢弃
       (保留 NaN 不参与损失),即"置信度过滤";
    3. 以上都没有的格子保持 NaN(不污染损失)。

    返回前打印每个标签的 官方数 / 伪标签填充数 / 最终有效数。
    """
    train = pd.read_csv(os.path.join(root, "train.csv"))
    df = train[["StudyInstanceUID"] + LABELS].copy()
    official_cnt = {c: int(df[c].notna().sum()) for c in LABELS}

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
        # 伪标签列:pseudo_<c> 优先,回退同名列(某些数据集直接用标签名存概率)
        pcol = f"pseudo_{c}" if f"pseudo_{c}" in pseudo.columns else (c if c in pseudo.columns else None)
        if pcol is None:
            print(f"[标签] 跳过 {c}:软标签数据集中无 pseudo_{c} 列")
            continue
        filled = pd.to_numeric(pseudo[pcol], errors="coerce")
        # 置信度过滤:有置信度列且低于阈值 -> 置 NaN 丢弃
        conf_col = next((cc for cc in (f"pseudo_conf_{c}", f"conf_{c}", f"confidence_{c}")
                         if cc in pseudo.columns), None)
        if conf_col is not None and pseudo_conf > 0:
            conf = pd.to_numeric(pseudo[conf_col], errors="coerce")
            filled = filled.where(conf >= pseudo_conf)  # 置信度缺失/过低 -> NaN
        # 按 StudyInstanceUID 对齐填充
        uids = df.loc[mask, "StudyInstanceUID"]
        vals = filled.reindex(uids).values
        filled_cnt[c] = int(pd.notna(vals).sum())
        df.loc[mask, c] = vals

    print(f"[标签] 填充统计({len(df)} 个 study):")
    for c in LABELS:
        print(f"  {c:18s} 官方 {official_cnt[c]:4d} + 伪标签填充 {filled_cnt[c]:4d}"
              f" = 有效 {int(df[c].notna().sum()):5d}")
    return df


def read_dicom_slices(dcm_dir, series_uid):
    """读取一个 series 的所有切片,按物理位置排序,返回 [(path, ImagePositionPatient, z)]。"""
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
    # 优先按物理位置排序,缺位置的回退 InstanceNumber 顺序
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
    # 均匀采样中心点,每个中心取 [c-1, c, c+1]
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


# ---------------- 数据集 ----------------

class KneeDataset(Dataset):
    """study 级数据集:每个 study 收集各 series 的 clips,拼接成 (C*3, H, W) 张量。"""

    def __init__(self, studies, labels_df, dcm_root, series_df, has_targets=True, n_clips=2):
        self.studies = studies
        self.labels_df = labels_df
        self.dcm_root = dcm_root
        self.series_df = series_df
        self.has_targets = has_targets
        self.n_clips = n_clips
        self.cache = {}

    def _load_study(self, uid):
        if uid in self.cache:
            return self.cache[uid]
        srows = self.series_df[self.series_df["StudyInstanceUID"] == uid]
        # 优先选多样化的 series:按 (Anatomical_Plane, Fluid_Sensitive) 去重取前 MAX_SERIES
        if "Anatomical_Plane" in srows.columns:
            srows = srows.sort_values(["Anatomical_Plane", "Fluid_Sensitive"],
                                      kind="stable").drop_duplicates(
                subset=["Anatomical_Plane", "Fluid_Sensitive"]).head(MAX_SERIES)
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

class KneeModel(nn.Module):
    """ResNet34 共享 backbone + 全局池化 + 12 sigmoid 头。"""

    def __init__(self, num_labels=len(LABELS), channels=CLIP):
        super().__init__()
        if HAS_TV:
            self.backbone = tvm.resnet34(weights=tvm.ResNet34_Weights.IMAGENET1K_V1
                                         if hasattr(tvm, "ResNet34_Weights") else None)
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
        # 只对有标注的位置算损失(valid 掩码:1=有标注,0=缺失)
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


# ---------------- 推理 / 提交 ----------------

def predict_test(model, test_df, series_df, root, device, n_clips=2):
    """对 test 每个 study 收集 clips,预测 12 个概率。"""
    ds = KneeDataset(test_df["StudyInstanceUID"].tolist(), None, root, series_df,
                     has_targets=False, n_clips=n_clips)
    loader = DataLoader(ds, batch_size=16, shuffle=False, num_workers=0)
    pred = predict(model, loader, device)
    return pd.DataFrame({"StudyInstanceUID": test_df["StudyInstanceUID"], **{
        LABELS_EN[j]: pred[:, j] for j in range(len(LABELS))}})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=2)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--workers", type=int, default=0)
    ap.add_argument("--n-clips", type=int, default=2)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--folds", type=int, default=FOLDS)
    ap.add_argument("--pseudo-conf", type=float, default=0.0,
                    help="伪标签置信度过滤阈值(0=不过滤;0.5=丢弃置信度<0.5的伪标签)")
    ap.add_argument("--verbose", action="store_true")
    args, _ = ap.parse_known_args()

    if not HAS_TORCH or not HAS_TV or not HAS_PYDICOM:
        sys.exit("依赖缺失:请在 Kaggle Notebook(GPU)环境运行(torch/torchvision/pydicom);本地仅可做数据层验证。")

    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

    root, out = resolve_paths()
    print(f"[数据] root={root}  out={out}")

    train_csv = pd.read_csv(os.path.join(root, "train.csv"))
    labels_df = load_labels(root, pseudo_conf=args.pseudo_conf)
    series_df = pd.read_csv(os.path.join(root, "train_series.csv"))
    test_df = pd.read_csv(os.path.join(root, "test.csv"))
    test_series = pd.read_csv(os.path.join(root, "test_series.csv"))
    dcm_train = os.path.join(root, "train_series")  # 与 test_series 同构
    dcm_test = os.path.join(root, "test_series")
    print(f"[数据] train {len(train_csv)} study / test {len(test_df)} study / series {len(series_df)}")

    # 折划分(GroupKFold by StudyInstanceUID)
    gkf = GroupKFold(n_splits=args.folds)
    groups = train_csv["StudyInstanceUID"].values
    oof = np.zeros((len(train_csv), len(LABELS)))
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[设备] {device}")

    for k, (tr_idx, va_idx) in enumerate(gkf.split(train_csv, groups=groups)):
        tr_studies = train_csv.iloc[tr_idx]["StudyInstanceUID"].tolist()
        va_studies = train_csv.iloc[va_idx]["StudyInstanceUID"].tolist()
        tr_ds = KneeDataset(tr_studies, labels_df, dcm_train, series_df, n_clips=args.n_clips)
        va_ds = KneeDataset(va_studies, labels_df, dcm_train, series_df, n_clips=args.n_clips)
        model = KneeModel().to(device)
        print(f"\n[折 {k + 1}/{args.folds}] train {len(tr_ds)} / val {len(va_ds)}", flush=True)
        val_pred, val_uid = run_fold(model, tr_ds, va_ds, device, args)
        for j, uid in enumerate(va_uid):
            row = np.where(train_csv["StudyInstanceUID"].values == uid)[0]
            if len(row):
                oof[row[0]] = val_pred[j]

    # OOF AUC(只算有标注的列)
    print("\n===== OOF 宏平均 AUC =====")
    aucs = []
    for j, c in enumerate(LABELS):
        y_true = labels_df[c].values.astype(float)
        valid = ~np.isnan(y_true)
        if valid.sum() >= 20:
            a = roc_auc_score(y_true[valid], oof[valid, j])
            aucs.append(a)
            print(f"  {c:18s} AUC {a:.4f} (n={valid.sum()})")
    print(f"  ==== 宏平均 AUC {np.mean(aucs):.4f} ====")

    # test 推理 + 提交(用最后一折模型)
    sub = predict_test(model, test_df, test_series, dcm_test, device, n_clips=args.n_clips)
    sub_path = os.path.join(out, "submission.csv")
    sub.to_csv(sub_path, index=False)
    print(f"\n提交文件已生成: {sub_path}  shape={sub.shape}")


if __name__ == "__main__":
    main()

