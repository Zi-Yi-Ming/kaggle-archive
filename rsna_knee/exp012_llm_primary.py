"""EXP-012 label builder: LLM-primary soft labels with silence masking.

Why: report-rules key ≈ 0.81 vs gold; steven v4_blend key ≈ 0.89.
EXP-009 filled silence 0.25 as confident negatives (0.586).
EXP-010 only filled remaining gaps so report rules still dominated (0.601).
EXP-012 uses LLM as PRIMARY for non-gold, silence → NaN, gold overrides.
"""
from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd

LABELS = [
    "ACL", "MCL", "Medial Meniscus", "Lateral Meniscus",
    "Medial OA", "Lateral OA", "PF OA", "Effusion",
    "Synovitis", "Baker's", "Contusion", "Fracture",
]

# silence / dead buckets in steven CSVs — never train on these
SILENCE_ROUNDED = {0.25, 0.5}

# match report-label calibration (pos 0.72-0.95 / neg 0.04-0.20)
CLIP_LO, CLIP_HI = 0.08, 0.92


def _find_llm() -> Path:
    env = os.environ.get("EXP012_LLM_CSV")
    if env and Path(env).is_file():
        return Path(env)
    cands = [
        Path(r"D:/桌面/Kaggle/rsna_knee/_dataset_stage/steven_labels/llm_labels_v4_blend.csv"),
        Path(r"D:/桌面/Kaggle/rsna_knee/_dataset_stage/steven_labels/llm_labels_v2.csv"),
    ]
    for root in ("/kaggle/input", r"D:/桌面/Kaggle/rsna_knee/_dataset_stage"):
        if not Path(root).is_dir():
            continue
        for p in Path(root).rglob("llm_labels_v4_blend.csv"):
            return p
        for p in Path(root).rglob("llm_labels_v2.csv"):
            return p
    for p in cands:
        if p.is_file():
            return p
    raise FileNotFoundError("llm_labels_v4_blend.csv not found")


def clean_llm_values(arr: np.ndarray) -> np.ndarray:
    out = arr.astype(np.float64).copy()
    out = np.where(np.isin(np.round(out, 2), list(SILENCE_ROUNDED)), np.nan, out)
    # shrink extremes so BCE does not overfit 0.02/0.98 report-style noise
    out = 0.5 + (out - 0.5) * 0.75
    out = np.clip(out, CLIP_LO, CLIP_HI)
    return out


def build_exp012_labels(train_csv: str | Path, verbose: bool = True) -> pd.DataFrame:
    train = pd.read_csv(train_csv)
    df = train[["StudyInstanceUID"] + LABELS].copy()
    gold_cnt = {c: int(df[c].notna().sum()) for c in LABELS}

    llm_path = _find_llm()
    llm = pd.read_csv(llm_path)
    llm = llm.set_index("StudyInstanceUID")
    if verbose:
        print(f"[EXP-012] LLM source: {llm_path.name} rows={len(llm)}")

    n_fill = 0
    for c in LABELS:
        if c not in llm.columns:
            if verbose:
                print(f"  {c:18s} LLM missing column")
            continue
        mask = df[c].isna().values
        uids = df.loc[mask, "StudyInstanceUID"]
        raw = llm[c].reindex(uids).to_numpy(dtype=np.float64)
        cleaned = clean_llm_values(raw)
        df.loc[mask, c] = cleaned
        n_use = int(np.isfinite(cleaned).sum())
        n_sil = int(np.isfinite(raw).sum()) - n_use
        n_fill += n_use
        if verbose:
            print(
                f"  {c:18s} gold {gold_cnt[c]:4d} + LLM {n_use:4d}"
                f" (silence/drop {n_sil:4d}) = {int(df[c].notna().sum()):5d}"
            )
    if verbose:
        print(f"[EXP-012] total LLM cells filled: {n_fill}")
    return df


if __name__ == "__main__":
    root = Path(os.environ.get("RSNA_ROOT", r"D:/桌面/Kaggle/rsna_knee"))
    out = build_exp012_labels(root / "train.csv")
    dst = root / "labels" / "train_exp012_llm_primary.csv"
    dst.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(dst, index=False)
    print("wrote", dst, out.shape)
