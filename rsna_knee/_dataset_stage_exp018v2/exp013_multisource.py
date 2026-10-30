"""EXP-013 multi-source soft labels.

Sources (probability-space blend, silence → NaN):
  - stevenleehans llm_labels_v4_blend.csv  (gold-key 0.893)
  - lixin73 labels_llm_gpt56sol.csv        (0.835, decorrelated)
  - pilkwang report_labels_v2.csv          (0.870, conf + UNK verdict)

Weights: base 0.5 / 0.2 / 0.3, then optional per-class reliability on gold58.
Silence: 0.25/0.5 rounded buckets and pilkwang UNK → NaN (never train).
Targets: shrink 0.5+(p-0.5)*0.75, clip [0.08, 0.92].
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

SILENCE_ROUNDED = {0.25, 0.5}
CLIP_LO, CLIP_HI = 0.08, 0.92
BASE_W = {"steven": 0.50, "lixin": 0.20, "pilk": 0.30}


def _stage_root() -> Path:
    return Path(os.environ.get(
        "EXP013_LABEL_ROOT",
        r"D:/桌面/Kaggle/rsna_knee/_dataset_stage",
    ))


def _find(name: str) -> Path:
    env = os.environ.get(f"EXP013_{name.upper()}")
    if env and Path(env).is_file():
        return Path(env)
    for root in (
        Path("/kaggle/input"),
        _stage_root(),
    ):
        if not root.is_dir():
            continue
        for p in root.rglob(name):
            return p
    raise FileNotFoundError(name)


def _clean(arr: np.ndarray) -> np.ndarray:
    out = arr.astype(np.float64).copy()
    out = np.where(np.isin(np.round(out, 2), list(SILENCE_ROUNDED)), np.nan, out)
    out = np.where(np.isfinite(out), 0.5 + (out - 0.5) * 0.75, out)
    out = np.clip(out, CLIP_LO, CLIP_HI)
    return out


def _load_sources():
    steven = pd.read_csv(_find("llm_labels_v4_blend.csv")).set_index("StudyInstanceUID")
    lixin = pd.read_csv(_find("labels_llm_gpt56sol.csv")).set_index("StudyInstanceUID")
    pilk = pd.read_csv(_find("report_labels_v2.csv")).set_index("StudyInstanceUID")
    return steven, lixin, pilk


def _pilk_soft(pilk: pd.DataFrame, c: str) -> pd.Series:
    """Map pilkwang verdict+conf to soft probs; UNK → NaN."""
    if f"{c}__verdict" not in pilk.columns or c not in pilk.columns:
        return pd.Series(np.nan, index=pilk.index)
    v = pilk[f"{c}__verdict"].astype(str).str.upper()
    raw = pilk[c].astype(float)
    out = raw.copy()
    out[v == "UNK"] = np.nan
    return out


def build_exp013_labels(train_csv: str | Path, verbose: bool = True) -> pd.DataFrame:
    train = pd.read_csv(train_csv)
    df = train[["StudyInstanceUID"] + LABELS].copy()
    steven, lixin, pilk = _load_sources()
    if verbose:
        print("[EXP-013] sources:",
              f"steven={len(steven)} lixin={len(lixin)} pilk={len(pilk)}")
        print(f"[EXP-013] weights {BASE_W}")

    n_cells = 0
    for c in LABELS:
        mask = df[c].isna().values
        uids = df.loc[mask, "StudyInstanceUID"]

        parts = []
        ws = []
        for src, key, w in (
            (steven, c, BASE_W["steven"]),
            (lixin, c, BASE_W["lixin"]),
            (pilk, None, BASE_W["pilk"]),
        ):
            if key is not None:
                if key not in src.columns:
                    continue
                raw = src[key].reindex(uids).to_numpy(dtype=np.float64)
                cl = _clean(raw)
            else:
                cl = _pilk_soft(src, c).reindex(uids).to_numpy(dtype=np.float64)
                cl = _clean(cl)
            parts.append(cl)
            ws.append(w)

        stack = np.vstack(parts)  # (S, N)
        wvec = np.asarray(ws, dtype=np.float64)[:, None]
        valid = np.isfinite(stack)
        wsum = np.where(valid, wvec, 0.0).sum(axis=0)
        psum = np.where(valid, stack * wvec, 0.0).sum(axis=0)
        blend = np.where(wsum > 0, psum / np.maximum(wsum, 1e-9), np.nan)

        df.loc[mask, c] = blend
        n_use = int(np.isfinite(blend).sum())
        n_cells += n_use
        if verbose:
            agree = valid.all(axis=0).sum() if valid.size else 0
            print(
                f"  {c:18s} gold {int(train[c].notna().sum()):4d}"
                f" + multi {n_use:4d} (all3={int(agree)}) = {int(df[c].notna().sum()):5d}"
            )
    if verbose:
        print(f"[EXP-013] multi-source cells: {n_cells}")
        # show loss-weight mass
        y = df[LABELS].to_numpy(dtype=np.float64)
        w = 2.0 * np.abs(y - 0.5)
        print(f"[EXP-013] loss-w mean={np.nanmean(w):.3f} "
              f"p10={np.nanquantile(w,0.1):.3f} p90={np.nanquantile(w,0.9):.3f}")
    return df


if __name__ == "__main__":
    root = Path(os.environ.get("RSNA_ROOT", r"D:/桌面/Kaggle/rsna_knee"))
    out = build_exp013_labels(root / "train.csv")
    dst = root / "labels" / "train_exp013_multisource.csv"
    dst.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(dst, index=False)
    print("wrote", dst, out.shape)
