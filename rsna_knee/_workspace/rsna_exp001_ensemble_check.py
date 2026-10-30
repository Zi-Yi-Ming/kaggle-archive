from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOTS = [
    Path(r"D:/桌面/Kaggle/rsna_knee/artifacts/exp_001_5fold_sagittal"),
    Path(r"D:/桌面/Kaggle/rsna_knee/_out/fold4_final/artifacts/exp_001_5fold_sagittal"),
    Path(r"D:/桌面/Kaggle/rsna_knee/_out/fold14_v2_final/artifacts/exp_001_5fold_sagittal"),
    Path(r"D:/桌面/Kaggle/rsna_knee/_out/fold0_probe_out/artifacts/exp_001_5fold_sagittal"),
]
SUBS = {
    "local_exp001": Path(r"D:/桌面/Kaggle/rsna_knee/submissions/submission_exp001_5fold.csv"),
    "kaggle_like": Path(r"D:/桌面/Kaggle/rsna_knee/submissions/submission.csv__from_Kaggle"),
    "baseline_v3": Path(r"D:/桌面/Kaggle/rsna_knee/submissions/submission.csv"),
}
OUT = Path(r"D:/桌面/Kaggle/_workspace/rsna_exp001_ensemble_check")
OUT.mkdir(parents=True, exist_ok=True)

LABELS = [
    "ACL",
    "MCL",
    "Medial Meniscus",
    "Lateral Meniscus",
    "Medial OA",
    "Lateral OA",
    "PF OA",
    "Effusion",
    "Synovitis",
    "Baker's",
    "Contusion",
    "Fracture",
]


def load_meta(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8", errors="ignore"))


def inspect_root(root: Path) -> dict:
    info = {"root": str(root), "exists": root.exists(), "folds": {}, "canonical": None}
    if not root.exists():
        return info
    uid_path = root / "test_uid.csv"
    if uid_path.exists():
        info["canonical"] = pd.read_csv(uid_path)["StudyInstanceUID"].tolist()
    cfg = root / "config.json"
    if cfg.exists():
        c = load_meta(cfg)
        info["config"] = {
            "experiment_id": c.get("experiment_id"),
            "planes": c.get("args", {}).get("planes"),
            "only_fold": c.get("args", {}).get("only_fold"),
            "epochs": c.get("args", {}).get("epochs"),
            "resume_dir": c.get("args", {}).get("resume_dir"),
        }
    for k in range(5):
        fold_dir = root / f"fold{k}"
        meta_p = fold_dir / "meta.json"
        pred_p = fold_dir / "test_pred.npy"
        uid_p = fold_dir / "test_uid.csv"
        rec = {
            "has_meta": meta_p.exists(),
            "has_pred": pred_p.exists(),
            "has_uid": uid_p.exists(),
        }
        if meta_p.exists():
            m = load_meta(meta_p)
            rec.update(
                {
                    "status": m.get("completion_status"),
                    "plane": m.get("plane"),
                    "train_h": None
                    if m.get("fold_train_time_sec") is None
                    else round(m["fold_train_time_sec"] / 3600.0, 3),
                    "pred_shape_meta": m.get("prediction_shape"),
                    "n_clips": m.get("n_clips"),
                    "epochs": m.get("epochs"),
                    "batch": m.get("batch_size"),
                    "seed": m.get("seed"),
                }
            )
        if pred_p.exists() and uid_p.exists():
            pred = np.load(pred_p)
            uids = pd.read_csv(uid_p)["StudyInstanceUID"].tolist()
            rec["pred_shape"] = list(pred.shape)
            rec["pred_dtype"] = str(pred.dtype)
            rec["finite"] = bool(np.isfinite(pred).all())
            rec["range"] = [float(pred.min()), float(pred.max())]
            rec["mean"] = float(pred.mean())
            rec["uid_match_canon"] = (info["canonical"] is None) or (uids == info["canonical"])
            rec["uids"] = uids
            rec["pred"] = pred
        info["folds"][k] = rec
    return info


def ensemble_mean(folds: dict, canonical: list[str]) -> tuple[np.ndarray | None, list[str]]:
    preds = []
    used = []
    issues = []
    for k, rec in folds.items():
        if "pred" not in rec:
            issues.append(f"fold{k}: missing pred")
            continue
        if rec.get("status") != "done":
            issues.append(f"fold{k}: status={rec.get('status')}")
        if canonical is not None and rec.get("uids") != canonical:
            issues.append(f"fold{k}: uid mismatch")
            continue
        if rec["pred"].shape[0] != len(canonical or rec["uids"]):
            issues.append(f"fold{k}: shape {rec['pred']} vs n_uids")
            continue
        preds.append(rec["pred"].astype(np.float64))
        used.append(k)
    if not preds:
        return None, issues + ["no valid folds"]
    return np.mean(np.stack(preds, axis=0), axis=0), issues + [f"used_folds={used}"]


def to_df(pred: np.ndarray, uids: list[str]) -> pd.DataFrame:
    return pd.DataFrame(pred, columns=LABELS).assign(StudyInstanceUID=uids)[
        ["StudyInstanceUID"] + LABELS
    ]


def max_abs_diff(a: pd.DataFrame, b: pd.DataFrame) -> float | None:
    cols = LABELS
    if list(a["StudyInstanceUID"]) != list(b["StudyInstanceUID"]):
        return None
    return float(np.max(np.abs(a[cols].to_numpy() - b[cols].to_numpy())))


report = []
report.append("# EXP-001 5-fold ensemble 核对报告")
report.append("")

roots_info = {}
for root in ROOTS:
    info = inspect_root(root)
    roots_info[root] = info
    report.append(f"## {root}")
    report.append(f"- exists: {info['exists']}")
    if info.get("config"):
        report.append(f"- config: {info['config']}")
    report.append(f"- canonical_uids: {0 if not info['canonical'] else len(info['canonical'])}")
    for k, rec in info["folds"].items():
        pred = rec.pop("pred", None)
        uids = rec.pop("uids", None)
        report.append(f"- fold{k}: {rec}")
        if pred is not None:
            # keep for ensemble only on the richest complete root
            rec["_pred"] = pred
            rec["_uids"] = uids
    report.append("")

# choose primary root with most complete folds
primary = None
best = -1
for root, info in roots_info.items():
    score = sum(
        1
        for rec in info["folds"].values()
        if rec.get("status") == "done" and "pred" in rec or rec.get("_pred") is not None
    )
    # recompute cleanly
    score = 0
    for rec in info["folds"].values():
        has = (root / f"fold{list(info['folds'].keys())[list(info['folds'].values()).index(rec)]}")
    score = 0
    for k in range(5):
        if (root / f"fold{k}" / "test_pred.npy").exists() and (root / f"fold{k}" / "meta.json").exists():
            m = load_meta(root / f"fold{k}" / "meta.json")
            if m.get("completion_status") == "done":
                score += 1
    report.append(f"complete_done_folds {root.name if False else root}: {score}")
    if score > best:
        best = score
        primary = root

report.append("")
report.append(f"## Primary root: {primary} (done folds={best})")
primary_info = inspect_root(primary)
canonical = primary_info["canonical"]
pred, issues = ensemble_mean(primary_info["folds"], canonical)
report.append(f"ensemble issues: {issues}")
if pred is not None:
    ens_df = to_df(pred, canonical)
    ens_path = OUT / "exp001_ensemble_mean_local.csv"
    ens_df.to_csv(ens_path, index=False)
    report.append(f"local ensemble written: {ens_path} shape={ens_df.shape}")
    report.append(f"ensemble value range: [{pred.min():.6f}, {pred.max():.6f}] mean={pred.mean():.6f}")

    for name, path in SUBS.items():
        if not path.exists():
            report.append(f"sub {name}: MISSING {path}")
            continue
        sub = pd.read_csv(path)
        report.append(f"sub {name}: rows={len(sub)} cols={list(sub.columns)[:3]}... path={path}")
        if "StudyInstanceUID" not in sub.columns:
            report.append("  no StudyInstanceUID column")
            continue
        if list(sub["StudyInstanceUID"]) != canonical:
            report.append(f"  UID mismatch vs canonical; sub_n={len(sub['StudyInstanceUID'])} canon_n={len(canonical)}")
            # still try order-insensitive compare if same set
            if set(sub["StudyInstanceUID"]) == set(canonical):
                sub2 = sub.set_index("StudyInstanceUID").loc[canonical].reset_index()
                d = max_abs_diff(ens_df, sub2)
                report.append(f"  reindexed max_abs_diff vs local ensemble: {d}")
            continue
        d = max_abs_diff(ens_df, sub)
        report.append(f"  max_abs_diff vs local mean ensemble: {d}")

# cross-root consistency for overlapping folds
report.append("")
report.append("## Cross-root fold prediction consistency")
for k in range(5):
    arrays = []
    labels = []
    for root in ROOTS:
        p = root / f"fold{k}" / "test_pred.npy"
        if p.exists():
            arrays.append(np.load(p))
            labels.append(str(root))
    if len(arrays) < 2:
        report.append(f"fold{k}: only {len(arrays)} copy")
        continue
    base = arrays[0]
    for arr, lab in zip(arrays[1:], labels[1:]):
        if arr.shape != base.shape:
            report.append(f"fold{k}: shape mismatch {labels[0]} {base.shape} vs {lab} {arr.shape}")
        else:
            md = float(np.max(np.abs(arr - base)))
            report.append(f"fold{k}: max_abs_diff {labels[0]} vs {lab} = {md}")

# map to LB timeline
report.append("")
report.append("## Submission timeline notes")
report.append("- LB 0.658 @ 2026-09-10 ref 56139481 = BASELINE fold0 single model (memory)")
report.append("- LB 0.667 @ 2026-09-13 likely EXP-001 5-fold sagittal ensemble")
report.append("- LB 0.659 @ 2026-09-15 likely EXP-002 a3 fold0")
report.append("- LB 0.685 @ 2026-09-17 best; 0.679 @ 2026-09-18 latest")
report.append("- Local test set size is 3 studies; public LB is noisy")

text = "\n".join(report) + "\n"
(OUT / "report.md").write_text(text, encoding="utf-8")
print(text)
