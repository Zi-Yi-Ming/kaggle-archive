"""EXP-016 physical geometry / sampling. Isolated from training logic.

Legacy path remains byte-compatible in selection order (UID order preserved).
Physical path only changes:
  1) slice sort key: dot(IPP, slice_normal) with logged fallbacks
  2) 2.5D triplets: true physical neighbors on the sorted stack
  3) clip centers: physical-span based (still capped by n_clips)

No laterality, no MIL, no labels, no loss, no backbone changes.
"""
from __future__ import annotations

import os
from collections import Counter
from dataclasses import dataclass, field

import numpy as np

# module-level counters for smoke tests / training logs
STATS = {
    "sort_ipp_z_fallback": 0,
    "sort_no_iop": 0,
    "sort_no_ipp": 0,
    "sort_physical_ok": 0,
    "triplet_missing_neighbor": 0,
    "triplet_made": 0,
    "triplet_gap_relaxed": 0,
    "triplet_skipped": 0,
}
# accumulated geometry (for EXP-016 GPU run dump)
GAPS: list[float] = []
SPANS: list[float] = []
CLIPS_PER_SERIES: list[int] = []
USED_SLICES_PER_SERIES: list[int] = []


def reset_stats() -> None:
    for k in STATS:
        STATS[k] = 0
    GAPS.clear()
    SPANS.clear()
    CLIPS_PER_SERIES.clear()
    USED_SLICES_PER_SERIES.clear()


def dump_stats() -> dict:
    import numpy as np

    g = np.asarray(GAPS, dtype=np.float64)
    sp = np.asarray(SPANS, dtype=np.float64)
    cs = np.asarray(CLIPS_PER_SERIES, dtype=np.float64)
    out = dict(STATS)
    out["fallback_rate"] = (
        (STATS["sort_ipp_z_fallback"] + STATS["sort_no_ipp"])
        / max(
            1,
            STATS["sort_physical_ok"]
            + STATS["sort_ipp_z_fallback"]
            + STATS["sort_no_ipp"],
        )
    )
    out["clips_per_series"] = float(np.median(cs)) if cs.size else None
    out["clips_total"] = int(cs.sum()) if cs.size else 0
    out["used_slices_per_series"] = (
        float(np.median(np.asarray(USED_SLICES_PER_SERIES, dtype=np.float64)))
        if USED_SLICES_PER_SERIES
        else None
    )
    out["adjacent_gap_median"] = float(np.median(g)) if g.size else None
    out["adjacent_gap_P90"] = float(np.percentile(g, 90)) if g.size else None
    out["adjacent_gap_P95"] = float(np.percentile(g, 95)) if g.size else None
    out["physical_span_median"] = float(np.median(sp)) if sp.size else None
    out["physical_span_P90"] = float(np.percentile(sp, 90)) if sp.size else None
    return out


def slice_normal_from_iop(iop) -> np.ndarray | None:
    """IOP: 6 floats [row_x,row_y,row_z, col_x,col_y,col_z] -> unit normal."""
    if iop is None:
        return None
    try:
        v = np.asarray(iop, dtype=np.float64).reshape(-1)
        if v.size < 6:
            return None
        row, col = v[:3], v[3:6]
        n = np.cross(row, col)
        nn = float(np.linalg.norm(n))
        if not np.isfinite(nn) or nn < 1e-8:
            return None
        return n / nn
    except Exception:
        return None


def physical_position(ipp, normal: np.ndarray | None) -> tuple[float | None, str]:
    """Return (pos, kind) kind in {physical, ipp_z, missing}."""
    if ipp is None:
        return None, "missing"
    try:
        p = np.asarray(ipp, dtype=np.float64).reshape(-1)
        if p.size < 3:
            return None, "missing"
        if normal is not None:
            return float(np.dot(p[:3], normal)), "physical"
        return float(p[2]), "ipp_z"
    except Exception:
        return None, "missing"


def sort_slices_physical(files, dcm_reader):
    """Sort DICOM files by physical stack position.

    dcm_reader(path) -> pydicom dataset or None (header-only ok).
    Returns (rows, meta) where rows = [(path, pos, kind)], sorted ascending.
    Fallbacks are counted in STATS and reported in meta.
    """
    rows = []
    normals = []
    for f in files:
        ds = None
        try:
            ds = dcm_reader(f)
        except Exception:
            ds = None
        iop = ds.get("ImageOrientationPatient") if ds is not None else None
        ipp = ds.get("ImagePositionPatient") if ds is not None else None
        n = slice_normal_from_iop(iop)
        if n is None:
            STATS["sort_no_iop"] += 1
        else:
            normals.append(n)
        pos, kind = physical_position(ipp, n)
        if kind == "physical":
            STATS["sort_physical_ok"] += 1
        elif kind == "ipp_z":
            STATS["sort_ipp_z_fallback"] += 1
        else:
            STATS["sort_no_ipp"] += 1
        rows.append((f, pos, kind))

    # if normals disagree a lot, still use per-slice normal (local) — log count
    meta = {
        "n": len(files),
        "n_physical": sum(1 for r in rows if r[2] == "physical"),
        "n_ipp_z": sum(1 for r in rows if r[2] == "ipp_z"),
        "n_missing": sum(1 for r in rows if r[2] == "missing"),
    }

    def key(r):
        # None last, keep stable among equals
        pos = r[1]
        return (pos is None, pos if pos is not None else 0.0, r[0])

    rows.sort(key=key)
    return rows, meta


def median_spacing(positions) -> float:
    """Median |Δpos| of consecutive finite positions (stack spacing)."""
    p = np.asarray(
        [x for x in positions if x is not None and np.isfinite(x)], dtype=np.float64
    )
    if p.size < 2:
        return float("nan")
    d = np.abs(np.diff(p))
    d = d[d > 1e-8]
    if d.size == 0:
        return float("nan")
    return float(np.median(d))


def select_triplet_centers(positions, n_clips: int):
    """Choose center indices for 2.5D clips using physical span.

    Strategy:
      - require finite positions for span; fallback to even index centers
      - centers evenly spaced in *physical position* within [lo, hi]
      - map each desired position to nearest valid interior index
      - enforce center in [1, n-2] so neighbors exist
    Returns list of center indices (length <= n_clips), unique, ascending.
    """
    n = len(positions)
    if n < 3 or n_clips <= 0:
        return []
    pos = np.asarray(
        [np.nan if p is None else float(p) for p in positions], dtype=np.float64
    )
    finite = np.isfinite(pos)
    if finite.sum() < 3:
        # fallback: even index centers in sorted order
        step = max(1, (n - 2) // n_clips)
        return list(range(1, n - 1, step))[:n_clips]

    lo = float(np.nanmin(pos))
    hi = float(np.nanmax(pos))
    if not np.isfinite(lo) or not np.isfinite(hi) or hi - lo < 1e-8:
        step = max(1, (n - 2) // n_clips)
        return list(range(1, n - 1, step))[:n_clips]

    # physical targets
    if n_clips == 1:
        targets = [0.5 * (lo + hi)]
    else:
        targets = [lo + (hi - lo) * (i + 0.5) / n_clips for i in range(n_clips)]

    used = set()
    centers = []
    for t in targets:
        # nearest index among interior slices with finite pos
        best_i, best_d = None, None
        for i in range(1, n - 1):
            if not finite[i]:
                continue
            d = abs(pos[i] - t)
            if best_d is None or d < best_d:
                best_i, best_d = i, d
        if best_i is None:
            continue
        if best_i in used:
            # try neighbors
            for delta in (1, -1, 2, -2):
                j = best_i + delta
                if 1 <= j <= n - 2 and j not in used and finite[j]:
                    best_i = j
                    break
            else:
                continue
        used.add(best_i)
        centers.append(best_i)
    return sorted(centers)


def make_clips_physical(
    series_rows,
    n_clips=2,
    img_size=224,
    window_fn=None,
    dcm_read_fn=None,
    max_gap_factor=3.0,
    abs_gap_cap=None,
):
    """Build 2.5D clips with true physical neighbors.

    series_rows: list of (path, pos, kind) from sort_slices_physical
                 or legacy (path, z) tuples — we accept both.
    Returns (clips, clip_meta_list).
    """
    assert window_fn is not None and dcm_read_fn is not None
    # normalize rows to (path, pos)
    norm = []
    for r in series_rows:
        if len(r) == 3:
            norm.append((r[0], r[1]))
        else:
            norm.append((r[0], r[1]))
    n = len(norm)
    if n < 3:
        return [], []
    paths = [r[0] for r in norm]
    pos = [r[1] for r in norm]
    spacing = median_spacing(pos)
    centers = select_triplet_centers(pos, n_clips)
    clips, metas = [], []
    for c in centers:
        idx_trip = (c - 1, c, c + 1)
        if idx_trip[0] < 0 or idx_trip[2] >= n:
            STATS["triplet_skipped"] += 1
            continue
        ps = [pos[i] for i in idx_trip]
        if any(p is None or not np.isfinite(p) for p in ps):
            STATS["triplet_missing_neighbor"] += 1
            # still allow if indices are consecutive in sorted order
            gaps = (None, None)
            relaxed = True
        else:
            gaps = (
                abs(ps[1] - ps[0]),
                abs(ps[2] - ps[1]),
            )
            max_gap = None
            if np.isfinite(spacing) and spacing > 0:
                max_gap = spacing * max_gap_factor
            if abs_gap_cap is not None:
                max_gap = min(max_gap, abs_gap_cap) if max_gap else abs_gap_cap
            if max_gap is not None and (gaps[0] > max_gap or gaps[1] > max_gap):
                STATS["triplet_gap_relaxed"] += 1
                relaxed = True
            else:
                relaxed = False
        chan = []
        ok = True
        for k in idx_trip:
            try:
                dcm = dcm_read_fn(paths[k])
                chan.append(window_fn(dcm, img_size))
            except Exception:
                ok = False
                break
        if not ok:
            STATS["triplet_skipped"] += 1
            continue
        clips.append(np.stack(chan, axis=0))
        STATS["triplet_made"] += 1
        if gaps and gaps[0] is not None:
            GAPS.append(float(gaps[0]))
            GAPS.append(float(gaps[1]))
        metas.append(
            {
                "center": c,
                "idx": idx_trip,
                "pos": ps,
                "gaps": gaps,
                "spacing": spacing,
                "relaxed": relaxed,
            }
        )
    # series-level accumulators
    CLIPS_PER_SERIES.append(len(clips))
    USED_SLICES_PER_SERIES.append(len(clips) * 3)
    finite_pos = [p for _, p in norm if p is not None and np.isfinite(p)]
    if len(finite_pos) >= 2:
        SPANS.append(float(max(finite_pos) - min(finite_pos)))
    return clips, metas
