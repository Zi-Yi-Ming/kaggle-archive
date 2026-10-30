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
import json
import os
import random
import subprocess
import sys
import threading
import time
import warnings
from pathlib import Path

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

try:
    import rsna_report_labels as RL   # 报告→12 病灶弱标签(与 rsna_v3.py 同目录)
    HAS_RL = True
except ImportError:
    HAS_RL = False

try:
    import sampling_geometry as SG  # EXP-016 physical sort / 2.5D sampling
    HAS_SG = True
except ImportError:
    HAS_SG = False

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
_WEIGHT_EXT = (".pth", ".pt", ".ckpt", ".pth.tar")  # 离线预训练权重文件扩展名

# 12 标签多语言关键词词典(英/西/荷/德/法)——零挂载软标签兜底
# 命中 → 高置信,未命中 → 低置信(软标签,不给硬 0/1,避免错词误导)
_REPORT_KEYWORDS = {
    "ACL": ["acl", "anterior cruciate", "cruciado anterior", "voorste kruisband",
            "vorderen kreuzband", "lca", "ligament croisé antérieur"],
    "MCL": ["mcl", "medial collateral", "colateral medial", "mediale collaterale",
            "inneres seitenband", "ligament collatéral médial"],
    "Medial Meniscus": ["medial meniscus", "menisco interno", "meniscus medialis",
                        "meniskus medial", "menisque médial", "inner meniscus", "menisco medial"],
    "Lateral Meniscus": ["lateral meniscus", "menisco externo", "meniscus lateralis",
                         "meniskus lateral", "menisque latéral", "outer meniscus"],
    "Medial OA": ["medial osteoarthritis", "artrosis femorotibial medial",
                  "mediale gonartrose", "mediale arthrose", "osteoartritis medial",
                  "medial compartment narrowing", "medial joint space narrowing"],
    "Lateral OA": ["lateral osteoarthritis", "artrosis femorotibial lateral",
                   "laterale gonartrose", "laterale arthrose", "lateral joint space narrowing"],
    "PF OA": ["patellofemoral osteoarthritis", "artrosis patelofemoral",
              "patellofemorale artrose", "patellofemoral arthrose", "pf oa",
              "patellofemoral narrowing", "patellofemoral joint space"],
    "Effusion": ["effusion", "derrame", "vocht", "erguss", "épanchement", "joint effusion"],
    "Synovitis": ["synovitis", "sinovitis", "synoviale", "synovial thickening", "synovitis"],
    "Baker's": ["baker", "popliteal cyst", "quiste de baker", "baker cyst"],
    "Contusion": ["contusion", "bone bruise", "contusión", "kneuzing", "kontusion",
                  "marrow edema", "óseo", "bone bruising"],
    "Fracture": ["fracture", "fractura", "fractuur", "fraktur", "fracture line",
                 "fracture line", "subchondral fracture"],
}


def _pseudo_from_reports(train_csv, conf_hit=0.9, conf_miss=0.1):
    """从放射报告文本用多语言关键词生成 12 标签软标签(零挂载兜底)。

    返回 DataFrame(StudyInstanceUID + pseudo_* 列)。关键词命中→conf_hit,
    未命中→conf_miss(不给硬 0/1,降低错词误导)。官方已有标注的 study
    仍以官方为准(load_labels 的填充逻辑保证官方优先)。
    """
    if "Report" not in train_csv.columns:
        return None
    rep = train_csv["Report"].fillna("")
    rows = {}
    for lab, kws in _REPORT_KEYWORDS.items():
        low = [k.lower() for k in kws]
        rows[f"pseudo_{lab}"] = rep.apply(
            lambda t: conf_hit if any(k in str(t).lower() for k in low) else conf_miss)
    df = pd.DataFrame({"StudyInstanceUID": train_csv["StudyInstanceUID"], **rows})
    return df


def _print_mount_tree(base="/kaggle/input", tag="数据", max_files=6):
    """打印挂载目录树(最多两层,每目录前几个文件),帮用户确认挂载内容。"""
    if not os.path.isdir(base):
        print(f"[诊断-{tag}] 目录不存在: {base}", flush=True)
        return
    print(f"[诊断-{tag}] /kaggle/input 实际挂载内容:", flush=True)
    for sub in sorted(os.listdir(base)):
        p = os.path.join(base, sub)
        try:
            if os.path.isdir(p):
                inner = sorted(os.listdir(p))[:max_files]
                print(f"  {sub}/ -> {inner}", flush=True)
            else:
                print(f"  {sub} (文件)", flush=True)
        except OSError:
            print(f"  {sub} (无法读取)", flush=True)


def _print_dcm_tree(root, tag="DICOM", max_show=5):
    """打印 train_series 目录前几层真实结构 + 抽样 .dcm 计数,确认 DICOM 布局。

    RSNA 常见布局:train_series/<StudyInstanceUID>/<SeriesInstanceUID>/*.dcm(两层);
    也兼容一层(<SeriesInstanceUID>/*.dcm)或更深层,这里打印实际看到的。
    """
    dcm = os.path.join(root, "train_series")
    if not os.path.isdir(dcm):
        print(f"[诊断-{tag}] {dcm} 不存在!", flush=True)
        return
    try:
        subs_all = sorted(os.listdir(dcm))
    except OSError:
        subs_all = []
    subs = subs_all[:max_show]
    print(f"[诊断-{tag}] {dcm}", flush=True)
    print(f"[诊断-{tag}] 子目录/文件数: {len(subs_all)},样本:", flush=True)
    for s in subs:
        sp = os.path.join(dcm, s)
        if os.path.isdir(sp):
            try:
                inner = sorted(os.listdir(sp))[:max_show]
            except OSError:
                inner = []
            print(f"  {s}/ -> {inner}", flush=True)
            for it in inner[:2]:
                itp = os.path.join(sp, it)
                if os.path.isdir(itp):
                    try:
                        files = sorted(os.listdir(itp))[:3]
                    except OSError:
                        files = []
                    print(f"      {it}/ -> {files}", flush=True)
        else:
            print(f"  {s} (文件)", flush=True)
    # 抽样 .dcm 计数:前 3 study × 前 3 series
    n_dcm = 0
    try:
        for s in subs_all[:3]:
            sp = os.path.join(dcm, s)
            if not os.path.isdir(sp):
                continue
            for it in sorted(os.listdir(sp))[:3]:
                itp = os.path.join(sp, it)
                if os.path.isdir(itp):
                    n_dcm += sum(1 for f in os.listdir(itp) if f.lower().endswith(".dcm"))
    except OSError:
        pass
    print(f"[诊断-{tag}] 抽样 .dcm 文件数: {n_dcm}(前 3 study × 前 3 series)", flush=True)


def _scan_offline_weights(base="/kaggle/input", depth=0, max_depth=4):
    """递归扫描挂载目录下的预训练权重文件(.pth/.pt 等),跳过 DICOM 大目录。

    返回 [(绝对路径, 相对 /kaggle/input 的描述)];找不到返回空列表。
    社区打包的离线权重数据集(如 matteonaccarato/resnet34-imagenet-pth、
    marcshade/resnet-pretrained-weights-imagenet、pytorch/resnet34)挂载后即可被扫到,
    无需联网。
    """
    hits = []
    if depth > max_depth or not os.path.isdir(base):
        return hits
    try:
        entries = sorted(os.listdir(base))
    except OSError:
        return hits
    for fn in entries:
        p = os.path.join(base, fn)
        if os.path.isfile(p) and fn.lower().endswith(_WEIGHT_EXT):
            hits.append((p, os.path.relpath(p, "/kaggle/input")))
        elif os.path.isdir(p) and fn not in _SKIP_DIRS:
            hits.extend(_scan_offline_weights(p, depth + 1, max_depth))
    return hits


def _load_state_dict_from_file(path):
    """从权重文件读 state_dict(兼容:直接 state_dict / 包在 checkpoint 里 / 各种前缀)。

    读取失败或格式不对返回 None。
    """
    try:
        obj = torch.load(path, map_location="cpu", weights_only=True)
    except TypeError:  # 旧版 torch 无 weights_only 参数
        obj = torch.load(path, map_location="cpu")
    except Exception as e:
        print(f"[权重] {path} 读取失败: {e}", flush=True)
        return None
    if isinstance(obj, dict) and "state_dict" in obj:
        obj = obj["state_dict"]
    elif isinstance(obj, dict) and "model_state_dict" in obj:
        obj = obj["model_state_dict"]
    elif isinstance(obj, dict) and "model" in obj and isinstance(obj["model"], dict):
        obj = obj["model"]
    if not isinstance(obj, dict):
        return None
    # 剥常见前缀:module. / model. / backbone.(若整体带前缀,统一还原)
    out = {}
    for k, v in obj.items():
        for pre in ("module.", "model.", "backbone."):
            if k.startswith(pre):
                k = k[len(pre):]
                break
        out[k] = v
    return out


def _try_load_offline(net, paths):
    """按序尝试把候选离线权重加载进 net(state_dict 结构须与 ResNet34 匹配)。

    适配规则(面向社区 RSNA 权重,如 barun2104 的 best_resnet34_fold0.pth):
    - conv1.weight 通道数不同时:reshape+mean 适配到 net 的 conv1 通道数(如 24→3,
      barun2104 是 8 clip × 3 通道的 2.5D 模型);
    - fc.* / head.* / classifier.* 一律剥离(我们的模型会替换成 12 头);
    返回 (是否成功, 命中描述)。
    """
    for p, desc in paths:
        sd = _load_state_dict_from_file(p)
        if sd is None:
            continue
        # 1) 适配 conv1:通道数不同则 reshape+mean(如 24 通道 → 3 通道)
        if "conv1.weight" in sd:
            w = sd["conv1.weight"]
            target = net.conv1.weight.shape[1]
            if w.shape[1] != target and w.shape[1] % target == 0:
                B, C, H, W = w.shape
                w2 = w.reshape(B, target, C // target, H, W).mean(dim=2)
                sd["conv1.weight"] = w2
                print(f"[权重] {desc} conv1 通道 {C}→{target} 平均适配", flush=True)
            elif w.shape[1] != target:
                sd.pop("conv1.weight")  # 无法适配,丢弃(用随机初始化)
        # 2) 剥离 fc/head/classifier(模型会替换成 12 头)
        for k in list(sd.keys()):
            if k.startswith(("fc.", "head.", "classifier.")):
                sd.pop(k)
        try:
            missing, unexpected = net.load_state_dict(sd, strict=False)
        except Exception as e:
            print(f"[权重] {desc} 与 ResNet34 结构不匹配: {e}", flush=True)
            continue
        exempt = {k for k in missing if k.startswith(("conv1.", "fc."))}
        if not unexpected and len(missing) == len(exempt):
            print(f"[权重] 离线预训练加载成功: {desc} (覆盖 {len(sd)} 个参数张量)", flush=True)
            return True, desc
        print(f"[权重] {desc} 结构不匹配(missing {len(missing) - len(exempt)} 个非豁免 key, "
              f"unexpected {len(unexpected)}),尝试下一个", flush=True)
    return False, ""


def _scan_pseudo(base, depth=0, max_depth=3):
    """递归在挂载目录下找软标签 CSV(限制深度,跳过 DICOM 目录)。

    返回 (DataFrame 或 None, 来源描述)。识别规则:含 StudyInstanceUID 且至少有一个
    pseudo_ 前缀列(如 pseudo_ACL)。找不到返回 (None, "")。

    识别方式双通道:
    1. 文件名白名单(_PSEUDO_FILES)快速命中;
    2. **按内容识别**:任意 *.csv 只要表头含 StudyInstanceUID + pseudo_* 列即命中
       (不依赖文件名,社区数据集改名/换结构也能扫到)。
    """
    if depth > max_depth or not os.path.isdir(base):
        return None, ""
    try:
        entries = sorted(os.listdir(base))
    except OSError:
        return None, ""
    # 通道 1:文件名白名单(向后兼容,读全量)
    for fn in _PSEUDO_FILES:
        p = os.path.join(base, fn)
        if os.path.exists(p) and os.path.isfile(p):
            try:
                cand = pd.read_csv(p)
            except Exception:
                continue
            if "StudyInstanceUID" in cand.columns and any(
                    c.startswith("pseudo_") for c in cand.columns):
                return cand, os.path.relpath(p, "/kaggle/input")
    # 通道 2:按内容识别(只读表头 nrows=3 判断,命中再全读)
    for fn in entries:
        if not fn.lower().endswith(".csv"):
            continue
        p = os.path.join(base, fn)
        if not os.path.isfile(p):
            continue
        try:
            head = pd.read_csv(p, nrows=3)
        except Exception:
            continue
        if "StudyInstanceUID" in head.columns and any(
                c.startswith("pseudo_") for c in head.columns):
            try:
                cand = pd.read_csv(p)
                return cand, os.path.relpath(p, "/kaggle/input")
            except Exception:
                continue
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


def load_labels(root, pseudo_conf=0.0, use_report_labels=True):
    """返回 train study 级标签 DataFrame(行=StudyInstanceUID, 列=LABELS, 分数/NaN)。

    标签来源优先级(2026-09-06 起;旧的"社区软标签数据集"方案已证伪弃用——
    barun2104 的 pseudo_* 98.7% 是字面 0.5 死值、零增量信息,是 loss 恒 0.693
    的真根因):
    1. 官方 train.csv 标注(0/1,仅 58/4407 例);
    2. 内置报告规则抽取器 rsna_report_labels(移植自 rsna-knee-baseline-v1,
       多语言/按句否定极性/严重度分级):对每份放射报告产出 12 病灶 soft 分数
       (阳性 0.72~0.95 / 阴性 0.04~0.20 / 无证据=NaN);
       官方缺失格用抽取分数填充,无证据格保持 NaN(不进损失,由 valid 掩码排除)。
    """
    train = pd.read_csv(os.path.join(root, "train.csv"))
    df = train[["StudyInstanceUID"] + LABELS].copy()
    official_cnt = {c: int(df[c].notna().sum()) for c in LABELS}

    # EXP-013: multi-source consensus soft labels
    if os.environ.get("EXP013_MULTISOURCE", ""):
        from exp013_multisource import build_exp013_labels
        out = build_exp013_labels(os.path.join(root, "train.csv"), verbose=True)
        print("[标签] EXP-013 multi-source table loaded")
        return out
    # EXP-012: LLM-primary soft labels (gold wins; silence 0.25/0.5 → NaN)
    exp012 = os.environ.get("EXP012_LLM_PRIMARY", "")
    if exp012:
        from exp012_llm_primary import build_exp012_labels
        out = build_exp012_labels(os.path.join(root, "train.csv"), verbose=True)
        print("[标签] EXP-012 LLM-primary table loaded")
        return out

    if not use_report_labels:
        print("[标签] --no-report-labels:仅官方标注可用")
        return df
    if not HAS_RL:
        print("[标签] 未找到 rsna_report_labels.py(需与 rsna_v3.py 同目录),"
              "仅官方标注可用")
        return df
    if "Report" not in train.columns:
        print("[标签] train.csv 无 Report 列,仅官方标注可用")
        return df

    pseudo = RL.build_pseudo_table(train, verbose=True)
    pseudo = pseudo.set_index("StudyInstanceUID")
    print(f"[标签] 填充统计({len(df)} 个 study):")
    for c in LABELS:
        mask = df[c].isna().values
        if not mask.any():
            print(f"  {c:18s} 官方全量,无需填充")
            continue
        uids = df.loc[mask, "StudyInstanceUID"]
        vals = pseudo["pseudo_" + c].reindex(uids).values
        n_fill = int(pd.notna(vals).sum())
        df.loc[mask, c] = vals
        print(f"  {c:18s} 官方 {official_cnt[c]:4d} + 报告抽取填充 {n_fill:4d}"
              f" = 有效 {int(df[c].notna().sum()):5d}")
    return df


_DCM_MISS_PRINTED = [False]  # 只打印一次 DICOM 未命中诊断,避免 2 万 series 刷屏


def read_dicom_slices(dcm_dir, series_uid, study_uid=None, sampling_mode="legacy"):
    """读取一个 series 的所有切片并排序,返回 [(path, pos)]。

    sampling_mode:
      legacy  — 按 ImagePositionPatient[2]（历史行为, EXP-00x baseline）
      physical — 按 dot(ImagePositionPatient, slice_normal)（EXP-016）
    """
    cands = [os.path.join(dcm_dir, series_uid)]
    if study_uid:
        cands.append(os.path.join(dcm_dir, study_uid, series_uid))
    sdir = next((c for c in cands if os.path.isdir(c)), None)
    if sdir is None:
        if not _DCM_MISS_PRINTED[0]:
            _DCM_MISS_PRINTED[0] = True
            print(f"[诊断-DICOM] 找不到 series 目录,尝试过: {cands}", flush=True)
            print(f"[诊断-DICOM] {dcm_dir} 是否存在: {os.path.isdir(dcm_dir)}", flush=True)
            try:
                inner = sorted(os.listdir(dcm_dir))[:8] if os.path.isdir(dcm_dir) else []
                print(f"[诊断-DICOM] {dcm_dir} 实际内容样本: {inner}", flush=True)
            except OSError:
                pass
        return []
    files = [os.path.join(sdir, f) for f in os.listdir(sdir) if f.lower().endswith(".dcm")]
    if not files:
        if not _DCM_MISS_PRINTED[0]:
            _DCM_MISS_PRINTED[0] = True
            print(f"[诊断-DICOM] 目录存在但无 .dcm 文件: {sdir}", flush=True)
            print(f"[诊断-DICOM] 目录内容样本: {sorted(os.listdir(sdir))[:8]}", flush=True)
        return []
    if sampling_mode == "physical" and HAS_SG:
        def _hdr(path):
            return pydicom.dcmread(path, stop_before_pixels=True)

        rows3, meta = SG.sort_slices_physical(files, _hdr)
        # return (path, pos) compatible with legacy consumers
        return [(f, p) for (f, p, _k) in rows3]
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


def make_clips(series_rows, n_clips=2, img_size=IMG_SIZE, sampling_mode="legacy"):
    """从排序好的切片列表生成若干 3 通道 clip。

    legacy  : 均匀 index 步进,三元组 = (c-1,c,c+1) 在排序数组上的邻居
    physical: 按物理跨度选 center,三元组必须在排序后的物理位置上真正相邻
              (gap 相对 median spacing 判定,见 sampling_geometry)
    """
    if sampling_mode == "physical" and HAS_SG:
        clips, _metas = SG.make_clips_physical(
            series_rows,
            n_clips=n_clips,
            img_size=img_size,
            window_fn=window_and_resize,
            dcm_read_fn=lambda p: pydicom.dcmread(p),
        )
        return clips
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


if HAS_TORCH:
    # ---------------- 数据集(v2:按平面过滤 series) ----------------

    class KneeDataset(Dataset):
        """study 级数据集,只取指定 Anatomical_Plane 的 series,拼成 (C*3, H, W)。"""

        def __init__(self, studies, labels_df, dcm_root, series_df, plane,
                     has_targets=True, n_clips=2, sampling_mode="legacy"):
            self.studies = studies
            self.labels_df = labels_df
            self.dcm_root = dcm_root
            self.series_df = series_df
            self.plane = plane
            self.has_targets = has_targets
            self.n_clips = n_clips
            self.sampling_mode = sampling_mode
            self.cache = {}  # 每折独立缓存:fold 结束随 dataset 释放,避免 5 折累积 OOM
            # 诊断计数:读到 clip 的 study / 空 study / 累计 clip 数
            self.n_hit = 0
            self.n_empty = 0
            self.n_clips_total = 0

        def stats(self):
            """返回 (读到 clip 的 study 数, 空 study 数, 平均 clip 数),防止静默白训练。"""
            total = self.n_hit + self.n_empty
            avg = (self.n_clips_total / self.n_hit) if self.n_hit else 0.0
            return self.n_hit, self.n_empty, avg

        def _load_study(self, uid):
            key = (uid, self.plane)
            if key in self.cache:
                return self.cache[key]
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
                rows = read_dicom_slices(
                    self.dcm_root, sid, study_uid=uid, sampling_mode=self.sampling_mode
                )
                clips.extend(
                    make_clips(rows, n_clips=self.n_clips, sampling_mode=self.sampling_mode)
                )
            self.cache[uid] = clips
            # 仅首次加载计数(缓存命中不再累加,避免多 epoch 重复)
            if clips:
                self.n_hit += 1
                self.n_clips_total += len(clips)
            else:
                self.n_empty += 1
            return clips

        def __len__(self):
            return len(self.studies)

        def __getitem__(self, i):
            uid = self.studies[i]
            clips = self._load_study(uid)  # 命中/空计数在 _load_study 首次加载时完成
            in_ch = self.n_clips * CLIP  # 输入通道数:clip 数 × 每 clip 3 切片
            if not clips:
                x = np.zeros((in_ch, IMG_SIZE, IMG_SIZE), dtype=np.float32)
            else:
                x = np.concatenate(clips[: self.n_clips], axis=0)  # (k*3, H, W)
                pad = in_ch - x.shape[0]
                if pad > 0:
                    x = np.concatenate([x, np.zeros((pad, IMG_SIZE, IMG_SIZE), dtype=np.float32)])
                elif pad < 0:
                    x = x[: in_ch]
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


    def _build_resnet34(use_pretrained=False, offline_paths=None):
        """构造 ResNet34 并加载 ImageNet 预训练权重。

        权重来源优先级:
        1. offline_paths:挂载的离线权重文件(扫描 /kaggle/input 得到,无需联网);
        2. use_pretrained=True:联网下载 torchvision 权重(带重试,失败回退随机);
        3. 否则随机初始化。
        成功加载后权重由 torch 缓存,后续 fold 秒加载。
        """
        net = tvm.resnet34(weights=None)
        if offline_paths:
            ok, desc = _try_load_offline(net, offline_paths)
            if ok:
                return net
            print(f"[权重] 离线候选均不匹配({desc}),回退到随机/联网路径", flush=True)
        if not use_pretrained:
            print("[权重] 未开启 --pretrained 且无离线权重,使用随机初始化"
                  "(不联网;如需预训练请加 --pretrained 并开启 Internet,"
                  "或挂载离线权重数据集)", flush=True)
            return net
        if _PRETRAINED_TRIED[0]:
            return net  # 之前已确认下载不了,直接随机
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

        def __init__(self, num_labels=len(LABELS), channels=CLIP, pretrained=False, offline_paths=None):
            super().__init__()
            if HAS_TV:
                self.backbone = _build_resnet34(use_pretrained=pretrained,
                                                offline_paths=offline_paths)
            else:
                raise RuntimeError("需要 torchvision(请在 Kaggle Notebook GPU 环境运行)")
            conv1_w = self.backbone.conv1.weight  # 保留预训练 conv1 权重
            self.backbone.conv1 = nn.Conv2d(channels, 64, kernel_size=7, stride=2, padding=3, bias=False)
            if conv1_w.shape == self.backbone.conv1.weight.shape:  # channels==3 时直接沿用
                self.backbone.conv1.weight.data.copy_(conv1_w.data)
            elif channels % 3 == 0 and conv1_w.shape[1] == 3:
                # 2.5D 通道扩展:把 3 通道预训练权重复制 n_clips 份(常见做法)
                rep = channels // 3
                self.backbone.conv1.weight.data.copy_(conv1_w.repeat(1, rep, 1, 1))
                print(f"[权重] conv1 预训练权重复制 {rep} 份扩展到 {channels} 通道", flush=True)
            self.backbone.fc = nn.Identity()
            self.head = nn.Linear(512, num_labels)

        def forward(self, x):
            feat = self.backbone(x)  # (B, 512)
            return self.head(feat)   # logits (B, 12)



# ---------------- 训练 / 验证 ----------------

def predict(model, loader, device):
    model.eval()
    rows = []
    with torch.no_grad():
        for x, _, _ in loader:
            x = x.to(device)
            out = torch.sigmoid(model(x))
            # .cpu().tolist() 而非 .cpu().numpy():torch 2.2.0+cu118 编于 numpy1.x,
            # 在 Kaggle numpy2.0.2 下 torch→numpy interop 崩;tolist 纯 C++ 路径安全。
            rows.extend(out.cpu().tolist())
    return np.asarray(rows, dtype=np.float32) if rows else np.zeros((0, len(LABELS)), dtype=np.float32)


def _epoch_loader(ds, args, epoch, shuffle):
    """建 DataLoader —— **保持 EXP-016 的原始 shuffle 语义**。

    这里刻意不传 generator:DataLoader(shuffle=True) 走 global RNG,与 EXP-016
    control 完全一致。任何「给 shuffle 换随机源」的改动都会额外引入一个实验
    变量,使 EXP-018 vs EXP-016 从「只改 n_clips」退化成双变量比较。

    epoch 参数仅用于日志/断点标识,不参与随机源构造。
    """
    return DataLoader(ds, batch_size=args.batch, shuffle=shuffle,
                      num_workers=args.workers, drop_last=False)


def loader_order_hash(loader, limit=8):
    """对 DataLoader 实际吐出的 batch 顺序取指纹(用于 continuous vs resume 比对)。

    不用「都是随机 shuffle 所以等价」来论证 —— 直接对真实顺序取 hash。
    为控制成本只取前 limit 个 batch。返回 (hash, 采样到的 batch 数)。
    """
    import hashlib
    h = hashlib.sha256()
    n = 0
    for bi, batch in enumerate(loader):
        if bi >= limit:
            break
        x = batch[0]
        # 用张量内容本身而非 __getitem__ 索引:后者在 Dataset 侧不可观测
        h.update(x.detach().float().cpu().contiguous().view(-1).numpy().tobytes())
        n += 1
    return h.hexdigest(), n


def probe_loader_order(ds, args, epoch, limit=8):
    """在 RNG 副本里取一个 epoch 的 batch 顺序指纹,不干扰训练用的 RNG。

    必须隔离 torch / numpy / python 三个 RNG:loader 迭代可能经 Dataset 间接
    消费其中任意一个。torch.random.fork_rng 只管 torch 侧,所以另外两个手动
    存还原。
    """
    py_state = random.getstate()
    np_state = np.random.get_state()
    try:
        with torch.random.fork_rng(devices=[]):
            probe = _epoch_loader(ds, args, epoch, shuffle=True)
            h, n = loader_order_hash(probe, limit=limit)
            del probe
        return h, n
    finally:
        random.setstate(py_state)
        np.random.set_state(np_state)


def train_epoch(model, loader, opt, crit, device, max_batches=0, step_cb=None,
                start_step=0):
    """跑一个 epoch。

    max_batches>0 时提前停止(仅用于 smoke / 诊断,不用于正式训练)。
    step_cb(global_step) 让上层写 telemetry。
    """
    model.train()
    tot, cnt = 0.0, 0
    gstep = int(start_step)
    for bi, (x, y, valid) in enumerate(loader):
        if max_batches and bi >= max_batches:
            break
        x, y, valid = x.to(device), y.to(device), valid.to(device)
        opt.zero_grad()
        out = model(x)
        if valid.sum() == 0:
            gstep += 1
            if step_cb:
                step_cb(gstep)
            continue
        # EXP-013: confidence-weight soft BCE — w = 2*|y-0.5| (UNK/silence already NaN)
        w = 2.0 * (y - 0.5).abs()
        denom = (valid * w).sum()
        loss = (crit(out, y) * valid * w).sum() / denom.clamp(min=1e-6)
        loss.backward()
        opt.step()
        tot += loss.item() * len(x)
        cnt += len(x)
        gstep += 1
        if step_cb:
            step_cb(gstep)
    return tot / max(cnt, 1), gstep


def run_fold(model, train_ds, val_ds, device, args, artifact_root=None, fold=0,
             plane="", resume_ckpt=None):
    """训练一个折。

    EXP-018 改动(只增观测与持久化,不改训练语义):
    - 每个 epoch 结束写 ckpt/epoch{N}.ckpt + latest.ckpt(写后读回校验);
    - 后台线程采样内存(含 DataLoader worker 进程树);
    - --resume-ckpt 支持从 epoch 边界继续,恢复 model/opt/sched/epoch/step/RNG。

    可复现性约定:每个 epoch 用独立 generator 建 DataLoader(见 _epoch_loader),
    shuffle 顺序由 (seed, epoch) 唯一确定,因此恢复 global RNG 后无需预热重放。
    """
    has_cuda = (device.type == "cuda")
    if has_cuda:
        torch.cuda.reset_peak_memory_stats()

    opt = AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    sched = CosineAnnealingLR(opt, T_max=args.epochs)
    crit = nn.BCEWithLogitsLoss(reduction="none")

    # ---- checkpoint / telemetry 目录 ----
    ckpt_dir = None
    mem_logger = None
    diag_json = getattr(args, "diag_json", "") or ""
    if artifact_root is not None:
        ckpt_dir = _ckpt_dir(artifact_root, fold, plane or "plane")
        ckpt_dir.mkdir(parents=True, exist_ok=True)
    if diag_json:
        mem_logger = MemLogger(diag_json,
                               interval_sec=float(getattr(args, "mem_interval", 30.0) or 30.0),
                               has_cuda=has_cuda,
                               worker_count=int(getattr(args, "workers", 0) or 0)).start()

    steps_per_epoch_by_epoch = {}
    smoke_batches = int(getattr(args, "max_batches", 0) or 0)

    # ---- resume ----
    # 顺序要求(不可调换,否则 resumed trajectory 会变):
    #   1. 建 model / optimizer / scheduler(构造本身可能消费 RNG)
    #   2. load_state_dict(不消费 RNG)
    #   3. 恢复 epoch / global_step
    #   4. 最后恢复 RNG
    # 禁止「先恢复 RNG 再初始化 model」——model init 会再消费 RNG。
    # 恢复 RNG 后,每个 epoch 在循环内建 DataLoader(shuffle=True 走 global RNG),
    # 与连续训练同一顺序消费 RNG,因此 shuffle order 可复现,无需预热重放。
    start_epoch = 0
    global_step = 0
    resume_info = None
    if resume_ckpt:
        rp = Path(resume_ckpt)
        if not rp.exists():
            sys.exit(f"[resume] checkpoint 不存在: {rp}")
        ck = _load_ckpt(rp, map_location="cpu")
        model.load_state_dict(ck["model_state_dict"])
        opt.load_state_dict(ck["optimizer_state_dict"])
        if ck.get("scheduler_state_dict") is not None:
            sched.load_state_dict(ck["scheduler_state_dict"])
        start_epoch = int(ck.get("epoch_done", 0))
        global_step = int(ck.get("global_step", 0))
        rng_ok = _restore_rng(ck.get("rng"))
        steps_per_epoch_by_epoch = ck.get("steps_per_epoch", {}) or {}
        resume_info = {
            "resumed_from": str(rp),
            "start_epoch": start_epoch,
            "global_step": global_step,
            "rng_restored": rng_ok,
            "ckpt_saved_at": ck.get("saved_at"),
            "ckpt_runtime": ck.get("runtime"),
        }
        print(f"[resume] 从 {rp} 恢复: epoch_done={start_epoch} "
              f"global_step={global_step} rng_restored={rng_ok}", flush=True)
        if start_epoch >= args.epochs:
            print(f"[resume] epoch_done={start_epoch} >= 目标 {args.epochs},该折已训完",
                  flush=True)

    epoch_losses = []
    loader_hashes = {}
    for ep in range(start_epoch, args.epochs):
        t0 = time.time()
        # 每 epoch 在循环内建 loader,shuffle 走 global RNG(与 EXP-016 同语义)
        train_loader = _epoch_loader(train_ds, args, ep, shuffle=True)
        # 顺序指纹:continuous 与 resumed 的同一 epoch 必须给出同一 batch 序列。
        # 在隔离的 RNG 副本里取,不影响训练本身。
        if getattr(args, "loader_order_probe", False):
            try:
                lh, ln = probe_loader_order(train_ds, args, ep)
                loader_hashes[str(ep)] = {"hash": lh, "batches": ln}
                print(f"[order] epoch {ep + 1} loader_order_hash={lh[:16]} n={ln}",
                      flush=True)
            except Exception as exc:
                print(f"[order] probe failed: {type(exc).__name__}: {exc}", flush=True)
        if mem_logger:
            mem_logger.mark(f"epoch{ep + 1}_start", epoch=ep + 1)
        loss, global_step = train_epoch(
            model, train_loader, opt, crit, device,
            max_batches=smoke_batches,
            start_step=global_step,
            step_cb=(mem_logger.mark if mem_logger else None),
        )
        del train_loader  # 让其 worker 及时退出,避免 worker 数与内存统计漂移
        sched.step()
        epoch_losses.append(loss)
        # 本 epoch 实际步数 = 当前 global_step - 之前所有 epoch 累计步数。
        # resume 时用作下一段预热步数(逐 batch 重放 DataLoader/Dropout 的 RNG 消费)。
        _prev = sum(int(steps_per_epoch_by_epoch.get(str(j), 0))
                    for j in range(ep) if str(j) in steps_per_epoch_by_epoch)
        steps_per_epoch_by_epoch[str(ep)] = int(global_step) - _prev
        print(f"  epoch {ep + 1}/{args.epochs} loss {loss:.4f} "
              f"({time.time() - t0:.0f}s) global_step={global_step} "
              f"steps_this_epoch={steps_per_epoch_by_epoch[str(ep)]}", flush=True)

        if ckpt_dir is not None:
            extra = {"steps_per_epoch": steps_per_epoch_by_epoch,
                     "epoch_losses": list(epoch_losses)}
            try:
                _save_ckpt_verified(ckpt_dir / f"epoch{ep + 1}.ckpt",
                                    model, opt, sched, ep + 1, global_step,
                                    args, artifact_root, fold, plane,
                                    mem_logger=mem_logger, extra=extra)
                _save_ckpt_verified(ckpt_dir / "latest.ckpt",
                                    model, opt, sched, ep + 1, global_step,
                                    args, artifact_root, fold, plane,
                                    mem_logger=mem_logger, extra=extra)
                print(f"[checkpoint] saved epoch{ep + 1}.ckpt + latest.ckpt -> {ckpt_dir}",
                      flush=True)
            except _CkptWriteFailure as e:
                print(f"[checkpoint] 写失败(校验不过): {e}", flush=True)

    val_loader = _epoch_loader(val_ds, args, 0, shuffle=False)
    val_pred = predict(model, val_loader, device)
    # DICOM 命中诊断:训练+验证已迭代完毕,此时计数才准确
    th, eh, at = train_ds.stats()
    vh, ev, av = val_ds.stats()
    print(f"[数据] train 命中 {th}/{len(train_ds)} study(空 {eh}, 平均 {at:.1f} clip) | "
          f"val 命中 {vh}/{len(val_ds)} study(空 {ev})", flush=True)
    if th == 0 or vh == 0:
        print("[警告] 有折 DICOM 全部没读到(命中 0)——输入将是全零,分数必然 ~0.5!", flush=True)

    if mem_logger:
        mem_logger.mark("fold_end")
        mem_logger.stop()
        if diag_json:
            report = {
                "experiment_id": getattr(args, "experiment_id", ""),
                "fold": fold,
                "plane": plane,
                "n_clips": args.n_clips,
                "batch": args.batch,
                "workers": args.workers,
                "smoke_batches": smoke_batches,
                "resume": resume_info,
                "loader_order_hashes": loader_hashes,
                "epoch_losses": [round(x, 6) for x in epoch_losses],
                "global_step": global_step,
                "param_hash": _model_param_hash(model),
                "runtime": _runtime_info(),
                "peak": {
                    "process_tree_rss_gb": max(
                        [r.get("process_tree_rss_gb", 0) for r in mem_logger.rows] or [0]),
                    "main_process_rss_gb": max(
                        [r.get("main_process_rss_gb", 0) for r in mem_logger.rows] or [0]),
                    "child_process_rss_gb": max(
                        [r.get("child_process_rss_gb", 0) for r in mem_logger.rows] or [0]),
                    "system_used_pct": max(
                        [r.get("system_used_pct", 0) for r in mem_logger.rows] or [0]),
                    "system_available_gb_min": min(
                        [r.get("system_available_gb", 0) for r in mem_logger.rows] or [0]),
                    "torch_cuda_max_allocated_gb": max(
                        [r.get("torch_cuda_max_allocated_gb", 0) for r in mem_logger.rows] or [0]),
                    "torch_cuda_max_reserved_gb": max(
                        [r.get("torch_cuda_max_reserved_gb", 0) for r in mem_logger.rows] or [0]),
                    "nvidia_smi_gpu_mem_used_mib": max(
                        [r.get("gpu_mem_used_mib", 0) for r in mem_logger.rows] or [0]),
                },
                "n_samples": len(mem_logger.rows),
            }
            Path(diag_json).parent.mkdir(parents=True, exist_ok=True)
            summary_path = Path(str(diag_json) + ".summary.json")
            summary_path.write_text(
                json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"[telemetry] 峰值汇总 -> {summary_path}", flush=True)
            print(f"[telemetry] {json.dumps(report['peak'])}", flush=True)

    val_uid = np.array(val_ds.studies)  # shuffle=False,顺序与数据集一致
    return val_pred, val_uid


# ---------------- 推理 / 融合 / 提交 ----------------

def predict_test(model, test_df, series_df, root, device, plane, n_clips=2, sampling_mode="legacy"):
    """对 test 每个 study 按指定平面收集 clips,预测 12 个概率。"""
    ds = KneeDataset(test_df["StudyInstanceUID"].tolist(), None, root, series_df,
                     plane, has_targets=False, n_clips=n_clips, sampling_mode=sampling_mode)
    loader = DataLoader(ds, batch_size=16, shuffle=False, num_workers=0)
    return predict(model, loader, device)


def plane_oof_auc(oof, labels_df, uid_list):
    """计算一个平面模型在指定 study 子集上的宏平均 OOF AUC(只算有标注的列)。

    labels_df 必须是【官方 gold 原始表】(0/1/NaN,如 train_csv 原列),不能传
    load_labels 填充后的 soft 表——soft 伪标签既非 ground truth,也会让
    roc_auc_score 崩(continuous)。58 例小样本下某列可能只有单一类别,跳过该列。
    """
    aucs = []
    for j, c in enumerate(LABELS):
        y_true = labels_df.set_index("StudyInstanceUID")[c].reindex(uid_list).values.astype(float)
        valid = ~np.isnan(y_true)
        if valid.sum() >= 20:
            yv = y_true[valid]
            if len(np.unique(yv)) < 2:
                continue
            aucs.append(roc_auc_score(yv, oof[valid, j]))
    return float(np.mean(aucs)) if aucs else 0.0


# ---------------- artifact / resume / ensemble helpers ----------------

def _artifact_root(args):
    base = Path(getattr(args, "artifact_dir", "") or "artifacts")
    exp = getattr(args, "experiment_id", "exp_001_5fold_sagittal")
    return base / exp


def _fold_meta_path(artifact_root, fold):
    return artifact_root / f"fold{fold}" / "meta.json"


def _is_fold_done(artifact_root, fold):
    p = _fold_meta_path(artifact_root, fold)
    if not p.exists():
        return False
    try:
        meta = json.loads(p.read_text(encoding="utf-8"))
        return meta.get("completion_status") == "done"
    except Exception:
        return False


def _save_fold_artifact(artifact_root, fold, test_pred, test_uids, meta):
    fold_dir = artifact_root / f"fold{fold}"
    fold_dir.mkdir(parents=True, exist_ok=True)
    np.save(str(fold_dir / "test_pred.npy"), test_pred.astype(np.float32))
    pd.DataFrame({"StudyInstanceUID": test_uids}).to_csv(
        fold_dir / "test_uid.csv", index=False
    )
    meta["completion_status"] = "done"
    meta["prediction_shape"] = list(test_pred.shape)
    (fold_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _load_fold_predictions(artifact_root, fold, canonical_uids):
    fold_dir = artifact_root / f"fold{fold}"
    pred = np.load(fold_dir / "test_pred.npy")
    uids = pd.read_csv(fold_dir / "test_uid.csv")["StudyInstanceUID"].tolist()
    if pred.shape != (len(canonical_uids), len(LABELS)):
        raise ValueError(f"fold{fold} shape mismatch: {pred.shape} vs expected {(len(canonical_uids), len(LABELS))}")
    if uids != canonical_uids:
        raise ValueError(f"fold{fold} UID order mismatch")
    if not np.isfinite(pred).all():
        raise ValueError(f"fold{fold} contains NaN/Inf")
    if pred.min() < 0 or pred.max() > 1:
        raise ValueError(f"fold{fold} predictions out of [0,1]")
    return pred


def _save_experiment_meta(artifact_root, train_fold_uids, test_uids, args):
    meta = {
        "experiment_id": getattr(args, "experiment_id", "exp_001_5fold_sagittal"),
        "git_commit": __git_commit(),
        "args": vars(args),
        "labels": LABELS,
        "train_fold0_uids": train_fold_uids,
        "test_uids": test_uids,
    }
    (artifact_root / "config.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    pd.DataFrame({"StudyInstanceUID": test_uids}).to_csv(
        artifact_root / "test_uid.csv", index=False
    )
    fold_rows = []
    for k in range(args.folds):
        fold_rows.append({"fold": k, "train_uids": train_fold_uids[k]})
    pd.DataFrame(fold_rows).to_csv(artifact_root / "fold_assignment.csv", index=False)


# ---------------- EXP-018: 真实训练内存遥测 / checkpoint / resume ----------------
# 本段只做观测与持久化,不改变任何训练语义(采样/损失/优化/超参一律不动)。
# 目的:上一轮 SIGKILL 后既没有内存轨迹也没有任何 checkpoint,无法定位也无法续训。

try:
    import psutil  # Kaggle 镜像自带
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


def _gb(nbytes):
    return round(float(nbytes) / (1024 ** 3), 3)


def _nvidia_smi():
    """读一次 nvidia-smi。失败返回 None(不抛,不影响训练)。"""
    try:
        out = subprocess.run(
            ["nvidia-smi",
             "--query-gpu=memory.used,memory.total,utilization.gpu",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=10,
        )
        if out.returncode != 0:
            return None
        parts = [p.strip() for p in out.stdout.strip().splitlines()[0].split(",")]
        if len(parts) < 3:
            return None
        return {
            "gpu_mem_used_mib": float(parts[0]),
            "gpu_mem_total_mib": float(parts[1]),
            "gpu_util_pct": float(parts[2]),
        }
    except Exception:
        return None


class MemLogger:
    """后台线程周期性采样内存,落 JSONL。

    必须把 DataLoader worker 计入:worker 是独立进程,主进程的
    psutil.Process().memory_info().rss 完全看不到它们。若 SIGKILL 来自
    worker 内存,只看主进程会得出错误结论。

    采样项:
      main_process_rss_gb / child_process_rss_gb / process_tree_rss_gb
      system_total_gb / system_available_gb / system_used_pct
      torch_cuda_allocated_gb / reserved / max_allocated / max_reserved
      nvidia_smi(gpu_mem_used_mib / gpu_mem_total_mib / gpu_util_pct)
    """

    def __init__(self, path, interval_sec=30.0, has_cuda=False, worker_count=0):
        self.path = Path(path)
        self.interval = float(interval_sec)
        self.has_cuda = bool(has_cuda)
        self.worker_count = int(worker_count)
        self.rows = []
        self._stop = threading.Event()
        self._thr = None
        self._proc = psutil.Process() if HAS_PSUTIL else None
        self.t0 = time.time()

    def _sample(self, tag, epoch=None, step=None):
        row = {
            "t_sec": round(time.time() - self.t0, 1),
            "tag": tag,
            "epoch": epoch,
            "step": step,
            "worker_count": self.worker_count,
        }
        if HAS_PSUTIL:
            try:
                vm = psutil.virtual_memory()
                main_rss = self._proc.memory_info().rss
                children = self._proc.children(recursive=True)
                child_rss = 0
                for c in children:
                    try:
                        child_rss += c.memory_info().rss
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                row.update({
                    "main_process_rss_gb": _gb(main_rss),
                    "child_process_rss_gb": _gb(child_rss),
                    "process_tree_rss_gb": _gb(main_rss + child_rss),
                    "n_children": len(children),
                    "system_total_gb": _gb(vm.total),
                    "system_available_gb": _gb(vm.available),
                    "system_used_pct": float(vm.percent),
                })
            except Exception as exc:
                row["psutil_error"] = f"{type(exc).__name__}: {exc}"
        if self.has_cuda:
            try:
                import torch as _t
                row.update({
                    "torch_cuda_allocated_gb": _gb(_t.cuda.memory_allocated()),
                    "torch_cuda_reserved_gb": _gb(_t.cuda.memory_reserved()),
                    "torch_cuda_max_allocated_gb": _gb(_t.cuda.max_memory_allocated()),
                    "torch_cuda_max_reserved_gb": _gb(_t.cuda.max_memory_reserved()),
                })
            except Exception as exc:
                row["cuda_error"] = f"{type(exc).__name__}: {exc}"
        smi = _nvidia_smi()
        if smi:
            row.update(smi)
        return row

    def _loop(self):
        while not self._stop.wait(self.interval):
            self._write(self._sample("periodic"))

    def _write(self, row):
        self.rows.append(row)
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        except Exception:
            pass

    def start(self):
        self._write(self._sample("start"))
        self._thr = threading.Thread(target=self._loop, daemon=True)
        self._thr.start()
        return self

    def mark(self, tag, epoch=None, step=None):
        row = self._sample(tag, epoch=epoch, step=step)
        self._write(row)
        return row

    def stop(self):
        self._stop.set()
        if self._thr is not None:
            self._thr.join(timeout=5)
        return self._write(self._sample("stop"))


def _rng_state():
    """快照全部 RNG 状态。resume 时不恢复这些,续训轨迹就不可能对齐。"""
    st = {"python": random.getstate(), "numpy": np.random.get_state()}
    if HAS_TORCH:
        st["torch_cpu"] = torch.get_rng_state()
        try:
            if torch.cuda.is_available():
                st["torch_cuda"] = torch.cuda.get_rng_state_all()
        except Exception:
            pass
    return st


def _restore_rng(st):
    if not st:
        return False
    try:
        if "python" in st:
            random.setstate(st["python"])
        if "numpy" in st:
            np.random.set_state(st["numpy"])
        if HAS_TORCH:
            if "torch_cpu" in st:
                torch.set_rng_state(st["torch_cpu"])
            if "torch_cuda" in st and torch.cuda.is_available():
                torch.cuda.set_rng_state_all(st["torch_cuda"])
        return True
    except Exception as e:
        print(f"[resume] RNG 恢复失败: {e}", flush=True)
        return False


def _runtime_info():
    info = {
        "python": sys.version.split()[0],
        "executable": sys.executable,
        "pid": os.getpid(),
    }
    if HAS_TORCH:
        info["torch"] = torch.__version__
        info["cuda_available"] = bool(torch.cuda.is_available())
        if torch.cuda.is_available():
            info["torch_cuda"] = torch.version.cuda
            info["gpu"] = torch.cuda.get_device_name(0)
            info["vram_total_gb"] = _gb(
                torch.cuda.get_device_properties(0).total_memory)
    info["numpy"] = np.__version__
    if HAS_PSUTIL:
        vm = psutil.virtual_memory()
        info["host_total_ram_gb"] = _gb(vm.total)
    return info


def _model_param_hash(model):
    """参数指纹:resume 后与连续训练比对这个值,用来判定 resume 是否真的等价。"""
    import hashlib
    h = hashlib.sha256()
    for name, p in sorted(model.state_dict().items()):
        h.update(name.encode())
        try:
            h.update(p.detach().float().cpu().contiguous().view(-1).tolist().__repr__().encode())
        except Exception:
            h.update(b"<unhashable>")
    return h.hexdigest()


def _ckpt_dir(artifact_root, fold, plane):
    root = _CKPT_OVERRIDE["root"]
    base = Path(root) if root else Path(artifact_root)
    return base / f"fold{fold}" / plane / "ckpt"


_CKPT_OVERRIDE = {"root": None}


def _job_read(job_id):
    p = Path(job_id)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _job_stage_done(job_id, stage):
    return stage in set(_job_read(job_id).get("done_stages", []))


def _job_mark_stage(job_id, stage, extra=None):
    """记录一个阶段位点。重读-改写-原子替换,避免与其他写者互相覆盖。"""
    p = Path(job_id)
    data = _job_read(job_id)
    stages = list(data.get("done_stages", []))
    if stage not in stages:
        stages.append(stage)
    data["done_stages"] = stages
    data.setdefault("stages_detail", {})[stage] = {
        "at": time.strftime("%Y-%m-%d %H:%M:%S"),
        **(extra or {}),
    }
    data["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(str(tmp), str(p))
    return data


def _save_ckpt(path, model, opt, sched, epoch_done, global_step, args,
               artifact_root, fold, plane, mem_logger=None, extra=None):
    """写一个 epoch 级 checkpoint。

    epoch_done = 已完整跑完的 epoch 数。resume 时从 epoch_done 开始继续。
    写临时文件再 os.replace:被 SIGKILL 打断也不会留下半个损坏的 ckpt。
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    mem = None
    if mem_logger is not None:
        mem = mem_logger.mark(f"ckpt_epoch{epoch_done}")
    payload = {
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": opt.state_dict(),
        "scheduler_state_dict": sched.state_dict() if sched is not None else None,
        "epoch_done": int(epoch_done),
        "global_step": int(global_step),
        "experiment_id": getattr(args, "experiment_id", ""),
        "fold": int(fold),
        "plane": plane,
        "config": vars(args) if hasattr(args, "__dict__") else {},
        "runtime": _runtime_info(),
        "rng": _rng_state(),
        "memory_snapshot": mem,
        "saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    if extra:
        payload.update(extra)
    tmp = path.with_suffix(path.suffix + ".tmp")
    torch.save(payload, str(tmp))
    os.replace(str(tmp), str(path))
    return payload


def _load_ckpt(path, map_location="cpu"):
    return torch.load(str(path), map_location=map_location, weights_only=False)


class _CkptWriteFailure(Exception):
    pass


def _save_ckpt_verified(path, *a, **kw):
    """写 ckpt 并立刻读回校验。写不成功且校验不过 → 抛异常,不许静默继续。"""
    payload = _save_ckpt(path, *a, **kw)
    try:
        back = _load_ckpt(path)
    except Exception as e:
        raise _CkptWriteFailure(f"checkpoint 写后读回失败 {path}: {e}")
    for k in ("model_state_dict", "optimizer_state_dict", "epoch_done", "global_step"):
        if k not in back:
            raise _CkptWriteFailure(f"checkpoint 缺字段 {k}: {path}")
    if int(back["epoch_done"]) != int(payload["epoch_done"]):
        raise _CkptWriteFailure(f"checkpoint epoch_done 回读不一致: {path}")
    return payload


def _maybe_kaggle_dataset_version(artifact_root, message):
    if os.environ.get("KAGGLE_KERNEL_RUN_TYPE") != "Interactive":
        return
    slug = os.environ.get("KAGGLE_KERNEL_SLUG", "rsna-artifacts-tmp")
    owner = os.environ.get("KAGGLE_USERNAME", "ziyiming")
    dataset_id = f"{owner}/{slug}"
    try:
        subprocess.run(
            [
                "kaggle",
                "datasets",
                "version",
                "-p",
                str(artifact_root),
                "-m",
                message,
                "--dir-mode",
                "tar",
            ],
            check=True,
            capture_output=True,
        )
        print(f"[artifact] uploaded dataset version: {dataset_id}", flush=True)
    except Exception as e:
        print(f"[artifact] dataset upload skipped: {e}", flush=True)


def __git_commit():
    try:
        import subprocess
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip()
    except Exception:
        return "unknown"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=2)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--workers", type=int, default=0)
    ap.add_argument("--n-clips", type=int, default=2)
    ap.add_argument("--sampling-mode", type=str, default="legacy",
                    choices=["legacy", "physical"],
                    help="EXP-016: legacy=z-sort+index clips; physical=IOP normal sort + physical 2.5D")
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--folds", type=int, default=FOLDS)
    ap.add_argument("--only-fold", type=int, default=-1,
                    help="只跑指定折(其余跳过;默认 -1=全部)。探路用:--folds 5 --only-fold 0 训第 0 折"
                         "(train 4/5 与正式同分布),test 推理用该折模型出提交")
    ap.add_argument("--planes", type=str, default=",".join(PLANES),
                    help="逗号分隔的平面子集,如 axial,sagittal(小写,不区分大小写)")
    ap.add_argument("--fuse", type=str, default="weight",
                    choices=["weight", "mean"],
                    help="平面融合方式:weight=按 OOF AUC 加权;mean=简单平均")
    ap.add_argument("--pseudo-conf", type=float, default=0.0,
                    help="伪标签置信度过滤阈值(0=不过滤;0.5=丢弃置信度<0.5的伪标签)")
    ap.add_argument("--no-report-labels", action="store_true",
                    help="禁用内置报告关键词软标签兜底(默认开启:未挂社区数据集时"
                         "自动从 4407 份放射报告生成软标签,零挂载)")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--pretrained", action="store_true",
                    help="尝试下载 ImageNet 预训练权重(需开启 Internet);默认随机初始化不联网")
    ap.add_argument("--offline-weights", type=str, default="",
                    help="逗号分隔的离线权重 .pth 路径(优先级最高);留空则自动扫描挂载目录")
    ap.add_argument("--no-offline-scan", action="store_true",
                    help="禁用自动扫描 /kaggle/input 下的离线权重文件")
    ap.add_argument("--data", type=str, default="",
                    help="显式指定数据根目录(如 kagglehub.competition_download 返回的 path),"
                         "指定后跳过自动查找")
    ap.add_argument("--artifact-dir", type=str, default="artifacts",
                    help="artifact 根目录(默认 artifacts)")
    ap.add_argument("--experiment-id", type=str, default="exp_001_5fold_sagittal",
                    help="experiment ID(用于 artifact 子目录)")
    ap.add_argument("--resume-dir", type=str, default="",
                    help="已有 artifact 目录,启动时扫描 meta.json 跳过已完成 fold")
    ap.add_argument("--resume-ckpt", type=str, default="",
                    help="EXP-018:从指定 epoch-level checkpoint 续训(恢复 model/opt/"
                         "sched/epoch/global_step/RNG)。与 --resume-dir 的折级跳过不同。")
    ap.add_argument("--ckpt-dir", type=str, default="",
                    help="EXP-018:checkpoint 根目录(默认跟随 --artifact-dir 的 exp 目录)")
    ap.add_argument("--diag-json", type=str, default="",
                    help="EXP-018:内存遥测 JSONL + 峰值汇总的输出路径(留空=不采样)")
    ap.add_argument("--mem-interval", type=float, default=30.0,
                    help="EXP-018:内存采样间隔秒(默认 30)")
    ap.add_argument("--max-batches", type=int, default=0,
                    help="EXP-018:每 epoch 只跑前 N 个 batch(0=全量)。仅用于 smoke/诊断," 
                         "会改变训练结果,不得用于正式实验。")
    ap.add_argument("--job-id", type=str, default="",
                    help="EXP-018:作业状态文件(如 /kaggle/working/exp018_job.json),"
                         "检查点/阶段位点跨实例可见,用于判定是否还需要继续跑")
    ap.add_argument("--loader-order-probe", action="store_true",
                    help="EXP-018:记录每个 epoch 的 DataLoader batch 顺序指纹,"
                         "用于证明 continuous 与 resumed 的 shuffle order 一致。"
                         "在隔离 RNG 副本中执行,不影响训练。")
    args, _ = ap.parse_known_args()

    resume_root = Path(args.resume_dir) if args.resume_dir else None
    if resume_root and args.artifact_dir and not args.experiment_id:
        args.experiment_id = resume_root.name

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
    labels_df = load_labels(root, pseudo_conf=args.pseudo_conf,
                            use_report_labels=not args.no_report_labels)
    series_df = pd.read_csv(os.path.join(root, "train_series.csv"))
    test_df = pd.read_csv(os.path.join(root, "test.csv"))
    test_series = pd.read_csv(os.path.join(root, "test_series.csv"))
    dcm_train = os.path.join(root, "train_series")
    dcm_test = os.path.join(root, "test_series")
    print(f"[数据] train {len(train_csv)} study / test {len(test_df)} study / series {len(series_df)}")
    _print_dcm_tree(root, "DICOM")  # 打印 train_series 真实目录结构,确认布局

    print(f"[采样] sampling_mode={args.sampling_mode} n_clips={args.n_clips} "
          f"HAS_SG={HAS_SG}")
    planes = [p.strip().title() for p in args.planes.split(",") if p.strip()]
    planes = [p for p in planes if p in PLANES]
    if not planes:
        sys.exit(f"--planes 无效,可选: {PLANES}")
    print(f"[平面] 使用 {planes}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[设备] {device}")

    # 离线预训练权重:显式指定优先,否则自动扫描 /kaggle/input
    offline_paths = []
    if args.offline_weights.strip():
        for p in [x.strip() for x in args.offline_weights.split(",") if x.strip()]:
            if os.path.isfile(p):
                offline_paths.append((p, p))
            else:
                print(f"[权重] --offline-weights 指定的文件不存在,跳过: {p}", flush=True)
    elif not args.no_offline_scan:
        offline_paths = _scan_offline_weights()
        if offline_paths:
            print(f"[权重] 自动扫描到 {len(offline_paths)} 个离线权重候选:", flush=True)
            for p, desc in offline_paths[:6]:
                print(f"  {desc}", flush=True)
            if len(offline_paths) > 6:
                print(f"  ... 共 {len(offline_paths)} 个", flush=True)
        else:
            print("[权重] 未在挂载目录发现离线权重(可挂载社区打包的 resnet34 权重数据集)", flush=True)
            _print_mount_tree("/kaggle/input", "权重")

    gkf = GroupKFold(n_splits=args.folds)
    groups = train_csv["StudyInstanceUID"].values

    # 每个平面独立跑折,记录 OOF 与 test 预测
    plane_oof, plane_test, plane_auc, plane_uids = {}, {}, {}, {}
    for plane in planes:
        print(f"\n########## 平面: {plane} ##########")
        oof = np.zeros((len(train_csv), len(LABELS)))
        artifact_root = _artifact_root(args)
        if getattr(args, "ckpt_dir", ""):
            _CKPT_OVERRIDE["root"] = args.ckpt_dir
        canonical_test_uids = test_df["StudyInstanceUID"].tolist()
        train_fold_uids = []
        for k, (tr_idx, va_idx) in enumerate(gkf.split(train_csv, groups=groups)):
            tr_studies = train_csv.iloc[tr_idx]["StudyInstanceUID"].tolist()
            va_studies = train_csv.iloc[va_idx]["StudyInstanceUID"].tolist()
            train_fold_uids.append(tr_studies)
            if args.only_fold >= 0 and k != args.only_fold:
                continue
            if resume_root and _is_fold_done(artifact_root, k):
                print(f"[artifact] fold {k} done, skip", flush=True)
                continue
            job_id = getattr(args, "job_id", "")
            if job_id and _job_stage_done(job_id, f"fold{k}_done"):
                print(f"[job] fold {k} 已完成(见 {job_id}),skip", flush=True)
                continue
            tr_ds = KneeDataset(tr_studies, labels_df, dcm_train, series_df, plane,
                                n_clips=args.n_clips, sampling_mode=args.sampling_mode)
            va_ds = KneeDataset(va_studies, labels_df, dcm_train, series_df, plane,
                                n_clips=args.n_clips, sampling_mode=args.sampling_mode)
            model = KneeModel(pretrained=args.pretrained,
                              offline_paths=offline_paths,
                              channels=args.n_clips * CLIP).to(device)
            print(f"[折 {k + 1}/{args.folds}] {plane} train {len(tr_ds)} / val {len(va_ds)}", flush=True)
            # 断点续训:显式 --resume-ckpt 优先,否则在 --job-id 模式下自动找该折 latest.ckpt
            fold_ckpt = getattr(args, "resume_ckpt", "") or ""
            if not fold_ckpt and job_id:
                cand = _ckpt_dir(artifact_root, k, plane) / "latest.ckpt"
                if cand.exists():
                    fold_ckpt = str(cand)
                    print(f"[resume] 自动发现 {cand}", flush=True)
            t0 = time.time()
            val_pred, val_uid = run_fold(model, tr_ds, va_ds, device, args,
                                         artifact_root=artifact_root, fold=k,
                                         plane=plane, resume_ckpt=fold_ckpt or None)
            fold_train_time = time.time() - t0
            for j, uid in enumerate(val_uid):
                row = np.where(train_csv["StudyInstanceUID"].values == uid)[0]
                if len(row):
                    oof[row[0]] = val_pred[j]
            t0 = time.time()
            test_pred = predict_test(model, test_df, test_series, dcm_test, device, plane,
                                     n_clips=args.n_clips, sampling_mode=args.sampling_mode)
            fold_inference_time = time.time() - t0
            meta = {
                "fold": k,
                "plane": plane,
                "n_clips": args.n_clips,
                "sampling_mode": getattr(args, "sampling_mode", "legacy"),
                "image_size": IMG_SIZE,
                "epochs": args.epochs,
                "batch_size": args.batch,
                "seed": args.seed,
                "git_commit": __git_commit(),
                "fold_train_time_sec": fold_train_time,
                "fold_inference_time_sec": fold_inference_time,
            }
            _save_fold_artifact(artifact_root, k, test_pred, canonical_test_uids, meta)
            try:
                wdir = artifact_root / f"fold{k}" / plane
                wdir.mkdir(parents=True, exist_ok=True)
                wpath = wdir / "model.pt"
                torch.save(model.state_dict(), str(wpath))
                meta2 = dict(meta)
                meta2["channels"] = int(args.n_clips * CLIP)
                meta2["num_labels"] = len(LABELS)
                (wdir / "model_meta.json").write_text(
                    json.dumps(meta2, ensure_ascii=False, indent=2), encoding="utf-8")
                print(f"[weights] saved {wpath}", flush=True)
            except Exception as e:
                print(f"[weights] save failed: {e}", flush=True)
            print(f"[artifact] saved fold{k} -> {artifact_root / f'fold{k}'}", flush=True)
            if job_id:
                _job_mark_stage(job_id, f"fold{k}_done",
                                {"artifact_root": str(artifact_root), "plane": plane})
            if HAS_SG and getattr(args, "sampling_mode", "legacy") == "physical":
                import json as _json
                st = SG.dump_stats()
                sp = artifact_root / "sampling_stats.json"
                sp.write_text(_json.dumps(st, indent=2), encoding="utf-8")
                print(f"[sampling-stats] {st}", flush=True)
        # experiment-level meta once per plane
        _save_experiment_meta(artifact_root, train_fold_uids, canonical_test_uids, args)
        print(f"[artifact] saved experiment meta -> {artifact_root}", flush=True)
        # 该平面 OOF AUC(宏平均)
        uid_list = train_csv["StudyInstanceUID"].tolist()
        if args.only_fold >= 0:
            print(f"[{plane}] 探路模式(--only-fold {args.only_fold}):OOF 单折不完整,"
                  f"跳过 OOF AUC(权重记 0=均等);test 推理用该折模型")
            auc = 0.0
        else:
            auc = plane_oof_auc(oof, train_csv[["StudyInstanceUID"] + LABELS], uid_list)
            print(f"[{plane}] OOF 宏平均 AUC {auc:.4f}")
        plane_oof[plane], plane_auc[plane], plane_uids[plane] = oof, auc, uid_list
        # load saved fold predictions for this plane
        per_fold = []
        missing = []
        for k in range(args.folds):
            p = artifact_root / f"fold{k}" / "test_pred.npy"
            if not p.exists():
                missing.append(k)
                continue
            try:
                per_fold.append(_load_fold_predictions(artifact_root, k, canonical_test_uids))
            except Exception as e:
                missing.append(k)
                print(f"[ensemble] fold{k} invalid: {e}", flush=True)
        if len(missing) == args.folds:
            sys.exit(f"[ensemble] no valid fold predictions available under {artifact_root}")
        if missing:
            print(f"[ensemble] missing folds: {missing}; ensemble with available folds only", flush=True)
        plane_test[plane] = np.mean(per_fold, axis=0) if per_fold else None
        if plane_test[plane] is not None:
            print(f"[ensemble] {plane} ensembled from {len(per_fold)} folds, shape={plane_test[plane].shape}")

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
        LABELS[j]: fused[:, j] for j in range(len(LABELS))}})
    sub_path = os.path.join(out, "submission.csv")
    sub.to_csv(sub_path, index=False)
    print(f"\n提交文件已生成: {sub_path}  shape={sub.shape}")


if __name__ == "__main__":
    main()
