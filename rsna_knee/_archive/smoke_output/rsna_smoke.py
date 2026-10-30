# -*- coding: utf-8 -*-
"""RSNA v3 生命体征 smoke test v2 (1 fold × 1 epoch, GPU 额度恢复后运行).

v2 校准(2026-09-04, Root Cause Audit 结论校准):
  - 体征1 不再用单一硬阈值,改为分级报告 + 分级判断;
  - 体征3/4 改为证据链指标(不做绝对 pass/fail,报告趋势 + 参考线);
  - pass/fail 改为五环证据链: Label → DICOM → gradient → parameter update
    → prediction variance; 任一环失败即停止正式 5-fold。

运行(Kaggle Notebook GPU,挂载比赛数据 + 软标签数据集 + 离线权重):
    !python rsna_smoke.py --verbose
不写正式 submission。
"""
import os
import sys
import time
import importlib.util

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

import numpy as np
import pandas as pd
import torch
import torch.nn as nn

spec = importlib.util.spec_from_file_location("rsna_v3", os.path.join(BASE, "rsna_v3.py"))
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)

LABELS = R.LABELS
TOTAL_CELLS = 4407 * 12  # 全量 grid;实际以 len(df)*12 为准

# 参考线(非硬性 pass/fail,仅用于分级判断)
REF = {
    "hit_ratio": 0.7,    # DICOM 读到 clip 的 study 占比参考线
    "loss_cap": 0.65,    # 若 final loss 高于此,强烈提示训练停滞(ln2=0.693)
    "pred_std": 0.05,    # 预测 std 参考线(远离 0 = 有输出方差)
    "gnorm_min": 0.01,   # grad_norm 非零参考线
    "pdelta_min": 1e-4,  # 参数绝对 delta 非零参考线
}


def load_labels_smoke(root):
    """体征1:分级报告 label supervision 覆盖(不设唯一 pass/fail)。"""
    train = pd.read_csv(os.path.join(root, "train.csv"))
    official = train[LABELS].notna()
    gold_cells = int(official.sum().sum())
    gold_studies = int(official.any(axis=1).sum())

    df = R.load_labels(root, pseudo_conf=0.0, use_report_labels=True)
    merged = df[LABELS].notna()
    merged_cells = int(merged.sum().sum())
    # 对齐判断:pseudo 填充格 = merged 中官方原本 NaN 的位置(load_labels 顺序与 train 一致)
    pseudo_filled = (merged.values & ~official.values)
    pseudo_cells = int(pseudo_filled.sum())
    n_studies_pseudo = int(pseudo_filled.any(axis=1).sum())
    coverage = merged_cells / max(1, len(df) * len(LABELS))
    per_study = merged_cells / max(1, len(df))

    print(f"[体征1] total target cells = {len(df) * len(LABELS)} ({len(df)} studies × {len(LABELS)})")
    print(f"[体征1] gold valid cells   = {gold_cells} ({gold_studies} studies, 官方)")
    print(f"[体征1] pseudo valid cells = {pseudo_cells} ({n_studies_pseudo} studies 被 pseudo 填充)")
    print(f"[体征1] merged valid cells = {merged_cells}")
    print(f"[体征1] valid coverage     = {coverage:.4f} ({merged_cells}/{len(df) * len(LABELS)})")
    print(f"[体征1] 每 study 平均 valid = {per_study:.2f} 个 target")

    # 分级判断(非唯一 pass/fail)
    if merged_cells <= gold_cells + 50:
        level = "❌ 基本可确认 pseudo 未进入训练(merged ≈ gold)"
    elif coverage > 0.9:
        level = "✅ 几乎全覆盖(≥90% grid)"
    elif n_studies_pseudo > 1000:
        level = "✅ pseudo 已进入训练(覆盖数千 study)"
    else:
        level = "⚠️ pseudo 部分进入(仅数千以下 study),需检查 merge 是否失配"
    print(f"[体征1] 分级判断: {level}")
    return {"gold_cells": gold_cells, "pseudo_cells": pseudo_cells,
            "merged_cells": merged_cells, "coverage": coverage,
            "n_studies_pseudo": n_studies_pseudo, "level": level,
            "df": df}


def data_smoke(root, series_df, plane):
    """体征2:DICOM 是否真的读到(采样前 32 study,含总数/命中/空/比例)。"""
    from sklearn.model_selection import GroupKFold
    train_csv = pd.read_csv(os.path.join(root, "train.csv"))
    gkf = GroupKFold(n_splits=5)
    tr, va = next(iter(gkf.split(train_csv, groups=train_csv["StudyInstanceUID"].values)))
    tr_studies = train_csv.iloc[tr]["StudyInstanceUID"].tolist()[:32]
    va_studies = train_csv.iloc[va]["StudyInstanceUID"].tolist()[:16]
    dcm = os.path.join(root, "train_series")
    tr_ds = R.KneeDataset(tr_studies, None, dcm, series_df, plane,
                          has_targets=False, n_clips=2)
    va_ds = R.KneeDataset(va_studies, None, dcm, series_df, plane,
                          has_targets=False, n_clips=2)
    # 全部采样 study 都触发加载(32+16=48,小样本)
    for uid in tr_studies:
        tr_ds._load_study(uid)
    for uid in va_studies:
        va_ds._load_study(uid)
    th, eh, at = tr_ds.stats()
    vh, ev, _ = va_ds.stats()
    t_sampled = th + eh
    v_sampled = vh + ev
    t_hit_ratio = th / max(1, t_sampled)
    v_hit_ratio = vh / max(1, v_sampled)
    print(f"[体征2] train 采样 {t_sampled} study: DICOM 命中 {th} / 空 {eh} / "
          f"命中率 {t_hit_ratio:.2f} (均 {at:.1f} clip/study)")
    print(f"[体征2] val   采样 {v_sampled} study: DICOM 命中 {vh} / 空 {ev} / "
          f"命中率 {v_hit_ratio:.2f}")
    print(f"[体征2] 参考线命中率 {REF['hit_ratio']};若命中率≈0 → 输入全零/路径错,训练必停")
    return t_hit_ratio


def train_smoke(root, series_df, plane, labels_df):
    """体征3/4/5:1 fold × 1 epoch,证据链指标(不做单一绝对 pass/fail)。"""
    from sklearn.model_selection import GroupKFold
    train_csv = pd.read_csv(os.path.join(root, "train.csv"))
    gkf = GroupKFold(n_splits=5)
    tr, va = next(iter(gkf.split(train_csv, groups=train_csv["StudyInstanceUID"].values)))
    tr_studies = train_csv.iloc[tr]["StudyInstanceUID"].tolist()
    va_studies = train_csv.iloc[va]["StudyInstanceUID"].tolist()
    dcm = os.path.join(root, "train_series")
    tr_ds = R.KneeDataset(tr_studies, labels_df, dcm, series_df, plane, n_clips=2)
    va_ds = R.KneeDataset(va_studies, labels_df, dcm, series_df, plane, n_clips=2)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = R.KneeModel(pretrained=False, offline_paths=R._scan_offline_weights(),
                        channels=2 * R.CLIP).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=1e-4)
    crit = nn.BCEWithLogitsLoss(reduction="none")

    loader = torch.utils.data.DataLoader(tr_ds, batch_size=8, shuffle=True, num_workers=0)
    model.train()

    # 训练前参数快照(分三组:conv1 / layer4 / head,分别报告各自 delta)
    def group_names():
        return {"conv1": [], "layer4": [], "head": []}
    snap0 = {"conv1": [], "layer4": [], "head": []}
    for n, p in model.named_parameters():
        if not p.requires_grad:
            continue
        if n.startswith("backbone.conv1"):
            snap0["conv1"].append((n, p.detach().clone()))
        elif "layer4" in n:
            snap0["layer4"].append((n, p.detach().clone()))
        elif n.startswith("head"):
            snap0["head"].append((n, p.detach().clone()))
    losses = []
    gnorm = []
    total_batches = 0
    valid_batches = 0
    t0 = time.time()
    for x, y, valid in loader:
        total_batches += 1
        x, y, valid = x.to(device), y.to(device), valid.to(device)
        if valid.sum() == 0:
            continue  # skipped batch: 无任何有效标签
        valid_batches += 1
        opt.zero_grad()
        out = model(x)
        loss = (crit(out, y) * valid).sum() / valid.sum()
        loss.backward()
        gn = sum(p.grad.norm().item() ** 2 for p in model.parameters()
                 if p.grad is not None) ** 0.5
        gnorm.append(gn)
        losses.append(loss.item())
        opt.step()
    skipped_batches = total_batches - valid_batches
    optimizer_steps = valid_batches

    # 训练首末 loss(仅在有有效 step 时定义;losses 在训练循环中收集)
    initial_loss = losses[0] if losses else float("nan")
    final_loss = losses[-1] if losses else float("nan")

    # 分环参数 delta(conv1 / layer4 / head,训练前后各自绝对差)
    pdelta = {}
    for grp in ("conv1", "layer4", "head"):
        d = 0.0
        for n, p0 in snap0[grp]:
            p1 = dict(model.named_parameters())[n]
            d += float((p1.detach() - p0).abs().sum())
        pdelta[grp] = d
    total_delta = sum(pdelta.values())

    print(f"[体征5] 分环参数绝对 delta: conv1={pdelta['conv1']:.6f}  "
          f"layer4={pdelta['layer4']:.6f}  head={pdelta['head']:.6f}  "
          f"(合计 {total_delta:.6f}; 参考: 各环>{REF['pdelta_min']} = 该层真在更新)")

    # 体征4:验证集 logits/pred 统计(限前 64 study,避免全量 val DICOM 加载拖长)
    model.eval()
    logits_all, preds = [], []
    val_sub = va_studies[:64]
    va_sub_ds = R.KneeDataset(val_sub, None, dcm, series_df, plane,
                              has_targets=False, n_clips=2)
    with torch.no_grad():
        for x, _, _ in torch.utils.data.DataLoader(va_sub_ds, batch_size=8, shuffle=False):
            x = x.to(device)
            lg = model(x)
            logits_all.append(lg.cpu().numpy())
            preds.append(torch.sigmoid(lg).cpu().numpy())
    logits = np.concatenate(logits_all, axis=0) if logits_all else np.zeros((1, 1))
    pred = np.concatenate(preds, axis=0) if preds else np.zeros((1, 1))

    print(f"[体征3] total_batches={total_batches}  valid_batches={valid_batches}  "
          f"skipped_batches={skipped_batches}  optimizer_steps={optimizer_steps}")
    print(f"[体征3] initial_loss={initial_loss:.4f}  final_loss={final_loss:.4f}  "
          f"(理想: final < initial; 参考: 若终值仍≈0.693 → 训练停滞)")
    if gnorm:
        print(f"[体征3] grad_norm mean={np.mean(gnorm):.4f} min={np.min(gnorm):.4f} "
              f"max={np.max(gnorm):.4f}")
    else:
        print("[体征3] grad_norm: 无有效 step")
    print(f"[体征4] (val 前 {len(val_sub)} study) logits mean={logits.mean():.4f} "
          f"std={logits.std():.4f}")
    print(f"[体征4] pred mean={pred.mean():.4f} std={pred.std():.4f} "
          f"(参考: std>{REF['pred_std']} = 输出有方差)")

    return {"total_batches": total_batches, "valid_batches": valid_batches,
            "skipped_batches": skipped_batches, "optimizer_steps": optimizer_steps,
            "initial_loss": initial_loss, "final_loss": final_loss,
            "gnorm": gnorm, "logits_std": float(logits.std()),
            "pred_std": float(pred.std()), "pdelta": total_delta,
            "pdelta_by_group": pdelta}


def main():
    root, _ = R.resolve_paths()
    train_csv = pd.read_csv(os.path.join(root, "train.csv"))
    series_df = pd.read_csv(os.path.join(root, "train_series.csv"))
    plane = "Sagittal"
    print(f"[smoke] root={root}  plane={plane}")
    t0 = time.time()

    # ============ 五环证据链 ============
    evidence = {}

    # 环1: Label supervision
    lab = load_labels_smoke(root)
    evidence["label"] = (lab["merged_cells"] > lab["gold_cells"] + 50)
    print(f"[证据链1 Label] {'✅' if evidence['label'] else '❌'} "
          f"(merged {lab['merged_cells']} > gold {lab['gold_cells']})")

    # 环2: DICOM input
    hit_ratio = data_smoke(root, series_df, plane)
    evidence["dicom"] = hit_ratio > 0.0
    print(f"[证据链2 DICOM] {'✅' if evidence['dicom'] else '❌'} 命中率={hit_ratio:.2f}")

    # 环3-5: 训练动态
    tr = train_smoke(root, series_df, plane, None if not evidence["label"] else lab.get("df", None))
    evidence["gradient"] = bool(tr["gnorm"]) and max(tr["gnorm"]) > REF["gnorm_min"]
    evidence["param_update"] = tr["pdelta"] > REF["pdelta_min"]
    evidence["pred_var"] = tr["pred_std"] > REF["pred_std"]
    print(f"[证据链3 Gradient] {'✅' if evidence['gradient'] else '❌'} "
          f"grad_norm_max={max(tr['gnorm']):.4f}" if tr["gnorm"] else "[证据链3 Gradient] ❌ 无 step")
    print(f"[证据链4 ParamUpdate] {'✅' if evidence['param_update'] else '❌'} "
          f"delta={tr['pdelta']:.6f}")
    print(f"[证据链5 PredVar] {'✅' if evidence['pred_var'] else '❌'} "
          f"pred_std={tr['pred_std']:.4f}")

    print(f"\n===== 五环证据链总结 (耗时 {time.time() - t0:.0f}s) =====")
    chain = ["label", "dicom", "gradient", "param_update", "pred_var"]
    for k in chain:
        print(f"  {k:13s}: {'✅' if evidence.get(k) else '❌'}")
    all_ok = all(evidence.get(k) for k in chain)
    print("\n五环全 ✅ → 可以进入正式 5-fold×N-epoch 全量训练")
    print("任一环 ❌ → 按审计报告对应 Root Cause 修复,勿直接跑全量;"
          "若仅个别环弱,先观察趋势再决定")


if __name__ == "__main__":
    main()
