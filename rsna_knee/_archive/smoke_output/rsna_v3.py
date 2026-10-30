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
    """返回 train study 级标签 DataFrame(行=StudyInstanceUID, 列=LABELS, 0/1/NaN)。

    标签来源优先级:
    1. 官方 train.csv 标注(0/1,仅 58/4407 例);
    2. 社区 LLM 软标签(pseudo_* 列,0-1 概率)——只在官方缺失处填充,
       若数据集带置信度列(conf_/confidence_/pseudo_conf_),低于 pseudo_conf 的丢弃
       (保留 NaN 不参与损失),即"置信度过滤";
    3. 零挂载兜底:从 4407 份放射报告用多语言关键词生成软标签(use_report_labels=True,
       默认开启,无需挂任何数据集);
    4. 以上都没有的格子保持 NaN(不污染损失)。
    """
    train = pd.read_csv(os.path.join(root, "train.csv"))
    df = train[["StudyInstanceUID"] + LABELS].copy()

    pseudo, src = find_pseudo_dataset()
    if pseudo is None and use_report_labels:
        print("[标签] 未发现社区软标签数据集,改用【报告关键词软标签】(零挂载兜底)")
        print("[标签] 提示:若想用社区 LLM 软标签,Add Input 挂 数据集 barun2104/"
              "rsna-knee-stratified-folds-and-llm-soft-labels(而非 notebook 输出)")
        pseudo = _pseudo_from_reports(train)
        src = "report-keywords(内置词典)"
    if pseudo is None:
        print("[标签] 未发现任何软标签来源,仅官方 58 例标注可用")
        _print_mount_tree("/kaggle/input", "标签")
        n_lab = df[LABELS].notna().sum().sum()
        print(f"[标签] {len(df)} 个 study,有效标签格 {n_lab}/{len(df) * len(LABELS)}")
        return df

    print(f"[标签] 软标签来源: {src}  shape={pseudo.shape}")
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


_DCM_MISS_PRINTED = [False]  # 只打印一次 DICOM 未命中诊断,避免 2 万 series 刷屏


def read_dicom_slices(dcm_dir, series_uid, study_uid=None):
    """读取一个 series 的所有切片,按物理位置排序,返回 [(path, z)]。

    路径兼容多种 Kaggle 布局(实测 RSNA 2026 为两层):
      1) <dcm_dir>/<series_uid>/                (旧假设:series 目录直接挂)
      2) <dcm_dir>/<study_uid>/<series_uid>/    (RSNA 标准:study 目录下再挂 series)
    找不到或读不到返回 []。
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
            rows = read_dicom_slices(self.dcm_root, sid, study_uid=uid)
            clips.extend(make_clips(rows, n_clips=self.n_clips))
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
    # DICOM 命中诊断:训练+验证已迭代完毕,此时计数才准确
    th, eh, at = train_ds.stats()
    vh, ev, av = val_ds.stats()
    print(f"[数据] train 命中 {th}/{len(train_ds)} study(空 {eh}, 平均 {at:.1f} clip) | "
          f"val 命中 {vh}/{len(val_ds)} study(空 {ev})", flush=True)
    if th == 0 or vh == 0:
        print("[警告] 有折 DICOM 全部没读到(命中 0)——输入将是全零,分数必然 ~0.5!", flush=True)
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
    labels_df = load_labels(root, pseudo_conf=args.pseudo_conf,
                            use_report_labels=not args.no_report_labels)
    series_df = pd.read_csv(os.path.join(root, "train_series.csv"))
    test_df = pd.read_csv(os.path.join(root, "test.csv"))
    test_series = pd.read_csv(os.path.join(root, "test_series.csv"))
    dcm_train = os.path.join(root, "train_series")
    dcm_test = os.path.join(root, "test_series")
    print(f"[数据] train {len(train_csv)} study / test {len(test_df)} study / series {len(series_df)}")
    _print_dcm_tree(root, "DICOM")  # 打印 train_series 真实目录结构,确认布局

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
        for k, (tr_idx, va_idx) in enumerate(gkf.split(train_csv, groups=groups)):
            tr_studies = train_csv.iloc[tr_idx]["StudyInstanceUID"].tolist()
            va_studies = train_csv.iloc[va_idx]["StudyInstanceUID"].tolist()
            tr_ds = KneeDataset(tr_studies, labels_df, dcm_train, series_df, plane,
                                n_clips=args.n_clips)
            va_ds = KneeDataset(va_studies, labels_df, dcm_train, series_df, plane,
                                n_clips=args.n_clips)
            model = KneeModel(pretrained=args.pretrained,
                              offline_paths=offline_paths,
                              channels=args.n_clips * CLIP).to(device)
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
