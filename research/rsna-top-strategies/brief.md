# Research brief: RSNA Knee — top strategies & next experiment choice

Date: 2026-09-29
Depth: **deep**
Audience: solo Kaggle competitor chasing a medal on `rsna-knee-abnormality-detection` (deadline 2026-10-22, macro AUC 12 labels, public test = 3 studies / very noisy LB).

## Decision at stake

We are at **public 0.721** (best). Medal band on public LB is **~0.956+**. Median is ~0.92.

Two candidate next moves (need ranked recommendation):

1. **A — Multi-source label consensus**: blend stevenleehans / lixin73 / pilkwang (etc.) LLM report labels with silence-masking + sharpening; retrain. Hypothesis: labels are the main lever (community claims 0.74→0.87 is mostly labels).
2. **B — Scale current recipe**: keep labels005 or single-source LLM-primary and go **S+C+A multi-plane** (we already proved multi-plane +0.022: Axial 0.699 → S+C+A 0.721).

We just A/B'd single-source LLM-primary vs report rules on Axial fold0: **0.701 vs 0.699** (wash). Silence 0.25/0.5 must be NaN (EXP-009/010 collapsed to 0.58–0.60 when mishandled).

## Scope IN

- Public Kaggle discussion posts, top-solution write-ups, notebooks, GitHub for this competition / RSNA 2026 knee MRI abnormality
- Label construction: LLM report labels, multi-source merge, soft-label calibration/sharpening, teacher–student / pseudo-labels
- Model choices of top teams (backbone, resolution, 2.5D/3D, multi-plane fusion)
- Inference tricks: TTA, ensembling, fold averaging, score calibration
- Quantitative claims with numbers (LB scores, AUC, label-key quality)

## Scope OUT

- Unrelated Kaggle medical comps unless the method is explicitly transferable and cited
- Pure architecture papers with no competition evidence
- Our internal EXP-00x history (already known)

## Assumptions

- Public leaderboard is noisy (3 studies); still use it because private is unknown and top public correlates with private practice quality
- GPU left ~14h this week; can afford one more ~7h S+C+A train OR several ~2h Axial ablations
- Cannot submit local CSVs; code-comp re-runs notebook (train-at-submit times out → need weights+infer-only)

## Decision criteria (how we will choose)

Rank by expected public AUC lift per GPU-hour, then robustness (doesn't die on 3-study noise), then feasibility before 2026-10-22.

## Angles

1. Top public leaderboard strategies & discussion posts (0.93–0.96 cluster)
2. Label engineering winners: multi-source LLM merge, soft labels, sharpening, teacher-student
3. Model architecture / resolution / multi-plane fusion of top teams
4. Inference & ensemble tricks (TTA, folds, score postproc)
5. Public write-ups / notebooks / GitHub solution posts for RSNA knee 2026
6. Failure modes: why soft LLM labels sometimes hurt image models; calibration
7. Comparative EV: multi-source labels vs multi-plane scale-up for a mid-pack 0.72 team
