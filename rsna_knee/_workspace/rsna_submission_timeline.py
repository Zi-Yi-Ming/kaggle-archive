from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(r"D:/桌面/Kaggle/rsna_knee")
OUT = Path(r"D:/桌面/Kaggle/_workspace/rsna_submission_timeline")
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

# From earlier kaggle CLI this session (UTC as returned by API)
API_SUBS = [
    # ref, date_utc, score, note_guess
    ("56331070", "2026-09-18 13:19:00", 0.679, "latest"),
    ("56299753", "2026-09-17 08:25:51", 0.685, "BEST"),
    ("56256422", "2026-09-15 14:19:11", 0.659, ""),
    ("56203211", "2026-09-13 08:40:28", 0.667, ""),
    ("56162074", "2026-09-11 08:38:48", 0.663, ""),
    ("56139481", "2026-09-10 07:04:13", 0.658, "memory baseline fold0"),
    ("55913420", "2026-08-31 10:38:30", None, ""),
    ("55909290", "2026-08-31 06:44:33", None, ""),
    ("55908018", "2026-08-31 05:26:40", 0.495, ""),
    ("55734380", "2026-08-24 05:52:41", 0.503, ""),
    ("55732362", "2026-08-24 04:05:07", 0.500, ""),
    ("55709319", "2026-08-23 07:42:56", 0.495, ""),
    ("55668747", "2026-08-21 12:15:37", 0.500, ""),
]


def load_preds(path: Path) -> np.ndarray | None:
    if not path.exists():
        return None
    return np.load(path)


def mean_ensemble(root: Path, folds, planes=None) -> tuple[np.ndarray | None, list[str]]:
    """planes None => flat fold{k}/test_pred.npy; else fold{k}/{plane}/test_pred.npy"""
    preds = []
    used = []
    for k in folds:
        if planes is None:
            p = root / f"fold{k}" / "test_pred.npy"
        else:
            arrs = []
            for pl in planes:
                pp = root / f"fold{k}" / pl / "test_pred.npy"
                if not pp.exists():
                    arrs = None
                    break
                arrs.append(np.load(pp))
            if arrs is None:
                continue
            # plane fuse mean for this fold
            p_arr = np.mean(np.stack(arrs, 0), 0)
            preds.append(p_arr.astype(np.float64))
            used.append(k)
            continue
        a = load_preds(p)
        if a is None:
            continue
        preds.append(a.astype(np.float64))
        used.append(k)
    if not preds:
        return None, used
    return np.mean(np.stack(preds, 0), 0), used


# candidate prediction sources
cands = {}

e1 = ROOT / "artifacts/exp_001_5fold_sagittal"
e1_mean, used = mean_ensemble(e1, range(5))
if e1_mean is not None:
    cands["exp001_mean5"] = e1_mean
for k in range(5):
    a = load_preds(e1 / f"fold{k}" / "test_pred.npy")
    if a is not None:
        cands[f"exp001_fold{k}"] = a.astype(np.float64)

e2 = ROOT / "artifacts/exp_002_a3_fold0"
a = load_preds(e2 / "fold0" / "test_pred.npy")
if a is not None:
    cands["exp002_fold0"] = a.astype(np.float64)

e3 = ROOT / "artifacts/exp_003_sagittal_coronal"
e3_fold0_sc, _ = mean_ensemble(e3, [0], ["Sagittal", "Coronal"])
if e3_fold0_sc is not None:
    cands["exp003_fold0_SC_mean"] = e3_fold0_sc
for plane in ["Sagittal", "Coronal"]:
    a = load_preds(e3 / "fold0" / plane / "test_pred.npy")
    if a is not None:
        cands[f"exp003_fold0_{plane}"] = a.astype(np.float64)

e3p = ROOT / "_out/exp003_fold1_pull/artifacts/exp_003_sagittal_coronal"
e3_2f, used = mean_ensemble(e3p, [0, 1], ["Sagittal", "Coronal"])
if e3_2f is not None:
    cands["exp003_2fold_SC_mean"] = e3_2f
for k in [0, 1]:
    for plane in ["Sagittal", "Coronal"]:
        a = load_preds(e3p / f"fold{k}" / plane / "test_pred.npy")
        if a is not None:
            cands[f"exp003_fold{k}_{plane}"] = a.astype(np.float64)

# also last-fold style as rsna_v3 code fact
a = load_preds(e1 / "fold4" / "test_pred.npy")
if a is not None:
    cands["exp001_lastfold4"] = a.astype(np.float64)

# local submission files
local_subs = [
    ROOT / "submissions/submission.csv",
    ROOT / "submissions/submission_v3_2epoch.csv",
    ROOT / "submissions/submission_exp001_5fold.csv",
    ROOT / "submissions/submission_exp002_a3_fold0.csv",
    ROOT / "submissions/submission_exp003_sc_fold0.csv",
    ROOT / "submissions/submission.csv__from_Kaggle",
    ROOT / "_out/exp002_a3_final/submission.csv",
    ROOT / "_out/exp002_a3_final2/submission.csv",
    ROOT / "_out/exp003_final/submission.csv",
    ROOT / "_out/exp003_fold1_pull/submission.csv",
    ROOT / "_out/fold0_probe_out/submission.csv",
    ROOT / "_out/fold4_final/submission.csv",
]

lines = []
lines.append("# RSNA 提交时间线对照（Kaggle API 时间按 UTC；本地文件为 Windows 本地时区≈UTC+8）")
lines.append("")
lines.append("## Kaggle 提交（本会话 CLI 已拉取）")
lines.append("")
lines.append("| ref | date (API) | local≈UTC+8 | publicScore | 本地候选匹配 |")
lines.append("|---|---|---|---|---|")

# load each local sub and compare to candidates
sub_scores = {}
for path in local_subs:
    if not path.exists():
        continue
    df = pd.read_csv(path)
    if "StudyInstanceUID" not in df.columns or not set(LABELS).issubset(df.columns):
        continue
    vals = df[LABELS].to_numpy(dtype=np.float64)
    best_name, best_d = None, 1e9
    for name, arr in cands.items():
        if arr.shape != vals.shape:
            continue
        d = float(np.max(np.abs(arr - vals)))
        if d < best_d:
            best_d, best_name = d, name
    sub_scores[str(path)] = {
        "mtime": pd.Timestamp(path.stat().st_mtime, unit="s"),
        "best": best_name,
        "diff": best_d,
        "vals": vals,
        "uids": df["StudyInstanceUID"].tolist(),
    }

# map API times to nearest local files by content match notes
# known content matches from previous verification
content_map = {
    "56203211": ("submission_exp001_5fold.csv", "exp001_mean5", "EXP-001 5-fold mean"),
    "56256422": ("submission_exp002_a3_fold0.csv", "exp002_fold0", "EXP-002 a3 fold0"),
    "56139481": ("(memory baseline fold0)", "exp001_fold0 or older v3", "BASELINE fold0"),
}

from datetime import datetime, timedelta

for ref, date_s, score, note in API_SUBS:
    dt = datetime.strptime(date_s, "%Y-%m-%d %H:%M:%S")
    local = dt + timedelta(hours=8)
    # find nearest local file by mtime within ±2 days
    near = []
    for p, rec in sub_scores.items():
        delta = abs((rec["mtime"].to_pydatetime() - local).total_seconds())
        if delta < 3 * 86400:
            near.append((delta, Path(p).name, rec["best"], rec["diff"], rec["mtime"]))
    near.sort()
    near_s = "; ".join(
        f"{n} best={b} d={d:.2e} mtime={m}" for _, n, b, d, m in near[:3]
    ) or "(no near local file)"
    mapped = content_map.get(ref, ("", "", note))
    lines.append(
        f"| {ref} | {date_s} | {local:%Y-%m-%d %H:%M} | {score} | {mapped[2] or ''} || {near_s} |"
    )

lines.append("")
lines.append("## 本地 submission 与候选预测的最近匹配")
lines.append("")
for path, rec in sorted(sub_scores.items(), key=lambda x: x[1]["mtime"]):
    lines.append(
        f"- `{Path(path).name}` mtime={rec['mtime']} best={rec['best']} max_abs_diff={rec['diff']:.8f}"
    )

lines.append("")
lines.append("## 候选预测源")
lines.append("")
for name, arr in cands.items():
    lines.append(f"- {name}: shape={arr.shape} mean={arr.mean():.6f} range=[{arr.min():.4f},{arr.max():.4f}]")

# critical comparison: local exp003 fold0 file vs pull fold1 2fold
lines.append("")
lines.append("## 关键数值对照")
lines.append("")


def diff(a, b):
    return float(np.max(np.abs(a - b)))


if "exp003_fold0_SC_mean" in cands and "exp003_2fold_SC_mean" in cands:
    lines.append(
        f"- EXP-003 fold0 SC vs 2fold SC: {diff(cands['exp003_fold0_SC_mean'], cands['exp003_2fold_SC_mean']):.8f}"
    )
if "exp001_mean5" in cands and "exp001_fold0" in cands:
    lines.append(
        f"- EXP-001 mean5 vs fold0: {diff(cands['exp001_mean5'], cands['exp001_fold0']):.8f}"
    )

# Is 0.685 submission maybe not local? Check if any local file mtime clusters on 09-17
lines.append("")
lines.append("## 09-17 / 09-18 缺口")
lines.append("- API BEST 0.685 @ 2026-09-17 08:25 UTC (=16:25 CST)")
lines.append("- API latest 0.679 @ 2026-09-18 13:19 UTC (=21:19 CST)")
lines.append("- local exp003 fold0 submission mtime=2026-09-18 16:33 CST (=08:33 UTC)")
lines.append("- local exp003 fold1 kernel run=2026-09-18 08:49 (API/kernel timezone)")
lines.append("- local exp003_fold1_pull submission mtime=2026-09-19 11:00 CST — pulled after, not necessarily submitted")
lines.append("- No local submission file dated 2026-09-17 was found in rsna_knee/submissions")

# Search more broadly for any file modified on 09-17
lines.append("")
lines.append("## 全仓 09-17 附近修改的 csv/log/ipynb")
base = Path(r"D:/桌面/Kaggle/rsna_knee")
for p in base.rglob("*"):
    if not p.is_file():
        continue
    if p.suffix.lower() not in {".csv", ".log", ".ipynb", ".md", ".json"}:
        continue
    m = pd.Timestamp(p.stat().st_mtime, unit="s")
    if pd.Timestamp("2026-09-16") <= m <= pd.Timestamp("2026-09-19"):
        lines.append(f"- {m} {p.relative_to(base)}")

text = "\n".join(lines) + "\n"
(OUT / "timeline.md").write_text(text, encoding="utf-8")
print(text)
