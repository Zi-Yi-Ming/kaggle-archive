---
written-at: 1790757913393
---
# T16 progress journal

## §1 Task identity
- task_id: T16
- short summary: Research FREE GPU options for PyTorch training (ResNet34 224, 2–7h, pydicom) on Lightning AI Studio free tier vs Hugging Face; write evidence file.

## §2 Subagent intent
The subagent was asked to research free GPU options suitable for actual PyTorch training (not inference-only) — specifically ResNet34 at 224 resolution, 2–7 hour jobs, with pydicom data loading — and to focus ONLY on two platforms: (1) Lightning AI Studio free tier (credits, GPU type, credit card requirement, preemption, max session length, disk, 2026 validity) and (2) Hugging Face, carefully distinguishing ZeroGPU Spaces vs Jobs vs paid Spaces GPU vs Inference, and determining which if any can run 2–7h training jobs for free. Deliverable: evidence-backed findings with URLs and quotes written to `D:/桌面/Kaggle/_workspace/gpu_scout/findings_lightning_hf.md` in a specified claim/quote/url/published/confidence format, plus a NOT MEASURED/blocked section. Final response was required to be a 5–10 bullet summary + file path, with a Status/Summary header block.

## §3 Files and code sections
- D:/桌面/Kaggle/_workspace/gpu_scout/findings_lightning_hf.md: created the deliverable — 25 evidence claims (L1–L12 Lightning, H1–H7 HF) each with quote/url/published/confidence, a synthesis table for ResNet34/pydicom fit, and a NOT MEASURED/blocked section.
- D:/桌面/Kaggle/_workspace/gpu_scout/.firecrawl/search-lightning.json: saved firecrawl web search + scrape results for Lightning AI free tier.
- D:/桌面/Kaggle/_workspace/gpu_scout/.firecrawl/search-hf.json: saved firecrawl web search + scrape results for Hugging Face ZeroGPU/Jobs.
- D:/桌面/Kaggle/_workspace/gpu_scout/.firecrawl/scrape-lightning-pricing.md: scraped https://lightning.ai/pricing/ (primary source for credits, 4h restart, disk, GPU table).
- D:/桌面/Kaggle/_workspace/gpu_scout/.firecrawl/scrape-lightning-studio.md: scraped Lightning AI Studio docs (signup/phone/80 GPU hours).
- D:/桌面/Kaggle/_workspace/gpu_scout/.firecrawl/scrape-lightning-interruptible.md: scraped interruptible-machines docs (preemption, 2-min warning, paid-tier conflict).
- D:/桌面/Kaggle/_workspace/gpu_scout/.firecrawl/scrape-lightning-bg.md: scraped background-execution docs (unlimited bg exec, 10-min auto-sleep).
- D:/桌面/Kaggle/_workspace/gpu_scout/.firecrawl/scrape-lightning-disk.md: scraped manage-disk-size docs (400GB Studio disk).
- D:/桌面/Kaggle/_workspace/gpu_scout/.firecrawl/scrape-hf-jobs.md: scraped HF Jobs index docs.
- D:/桌面/Kaggle/_workspace/gpu_scout/.firecrawl/scrape-jobs-pricing-raw.md: scraped HF jobs-pricing.md from GitHub raw (Jobs billing, timeout, GPU prices).
- D:/桌面/Kaggle/_workspace/gpu_scout/.firecrawl/scrape-hf-jobs-pricing.md: scraped HF Jobs pricing page (nav-heavy fallback).
- D:/桌面/Kaggle/_workspace/gpu_scout/.firecrawl/scrape-hf-spaces-gpus.md: scraped HF Spaces GPU upgrades (CPU Basic free; GPU paid).
- D:/桌面/Kaggle/_workspace/gpu_scout/.firecrawl/scrape-hf-pro.md: scraped HF PRO plan docs ($2/mo credits).
- D:/桌面/Kaggle/_workspace/gpu_scout/.firecrawl/scrape-hf-billing.md: scraped HF billing docs (PRO credits usable on Jobs).
- D:/桌面/Kaggle/_workspace/gpu_scout/.firecrawl/search-hf-jobs-pricing.json: search scrape of HF pricing page (Spaces GPU price table).
- D:/桌面/Kaggle/_workspace/gpu_scout/.firecrawl/search-hf-pro-credits.json: search scrape confirming PRO $2.00/month credits.
- D:/桌面/Kaggle/_workspace/gpu_scout/.firecrawl/search-lightning-preempt.json: search scrape for Lightning preemption/restart details.

## §4 Verbatim commands
Exact commands run (PowerShell 5.1 — note `&&` is invalid; use `;`):
```
mkdir -p "D:/桌面/Kaggle/_workspace/gpu_scout/.firecrawl"
```
```
npx --yes firecrawl-cli --status
```
```
npx --yes firecrawl-cli search "Lightning AI Studio free tier GPU credits 2026" --scrape -o "D:/桌面/Kaggle/_workspace/gpu_scout/.firecrawl/search-lightning.json" --json
```
```
npx --yes firecrawl-cli search "Hugging Face ZeroGPU Spaces Jobs free GPU training limits 2026" --scrape -o "D:/桌面/Kaggle/_workspace/gpu_scout/.firecrawl/search-hf.json" --json
```
```
npx --yes firecrawl-cli scrape "https://lightning.ai/pricing/" -o "D:/桌面/Kaggle/_workspace/gpu_scout/.firecrawl/scrape-lightning-pricing.md" --json
```
```
npx --yes firecrawl-cli scrape "https://lightning.ai/docs/platform/build/ai-studio" -o "D:/桌面/Kaggle/_workspace/gpu_scout/.firecrawl/scrape-lightning-studio.md" --json
```
```
npx --yes firecrawl-cli scrape "https://raw.githubusercontent.com/huggingface/hub-docs/main/docs/hub/jobs-pricing.md" -o "D:/桌面/Kaggle/_workspace/gpu_scout/.firecrawl/scrape-jobs-pricing-raw.md"
```
```
npx --yes firecrawl-cli scrape "https://raw.githubusercontent.com/huggingface/hub-docs/main/docs/hub/jobs.md" -o "D:/桌面/Kaggle/_workspace/gpu_scout/.firecrawl/scrape-jobs-raw.md"
```
```
npx --yes firecrawl-cli scrape "https://raw.githubusercontent.com/huggingface/hub-docs/main/docs/hub/pro.md" -o "D:/桌面/Kaggle/_workspace/gpu_scout/.firecrawl/scrape-hf-pro.md"
```
```
npx --yes firecrawl-cli scrape "https://raw.githubusercontent.com/huggingface/hub-docs/main/docs/hub/billing.md" -o "D:/桌面/Kaggle/_workspace/gpu_scout/.firecrawl/scrape-hf-billing.md"
```
```
npx --yes firecrawl-cli scrape "https://huggingface.co/docs/hub/en/spaces-gpus" -o "D:/桌面/Kaggle/_workspace/gpu_scout/.firecrawl/scrape-hf-spaces-gpus.md" --json
```
```
npx --yes firecrawl-cli scrape "https://lightning.ai/docs/platform/build/ai-studio/interruptible-machines" -o "D:/桌面/Kaggle/_workspace/gpu_scout/.firecrawl/scrape-lightning-interruptible.md"
```
```
npx --yes firecrawl-cli scrape "https://lightning.ai/docs/platform/build/ai-studio/background-execution" -o "D:/桌面/Kaggle/_workspace/gpu_scout/.firecrawl/scrape-lightning-bg.md"
```
```
npx --yes firecrawl-cli scrape "https://lightning.ai/docs/platform/build/ai-studio/manage-disk-size" -o "D:/桌面/Kaggle/_workspace/gpu_scout/.firecrawl/scrape-lightning-disk.md"
```

## §5 Outcome and discoveries
- Outcome (success): Deliverable written to `D:/桌面/Kaggle/_workspace/gpu_scout/findings_lightning_hf.md` (15.7 KB, 192 lines) with 19 sourced claims (L1–L12 Lightning, H1–H7 HF) in the required quote/url/published/confidence format, a ResNet34/pydicom fit table, and a NOT MEASURED/blocked section. All facts came from live pages opened via firecrawl-cli (npx) on 2026-09-30; Lightning pricing scrape cache timestamp 2026-09-30 confirms 2026 validity.
- Discoveries that may matter for other tasks:
  - Lightning AI free credits are ONE-TIME (5 on signup, +25 with a card = up to 30; expire in 12 months), NOT monthly. Third-party blogs claiming "80 free GPU hours per month" are wrong — official wording is "up to 80 free GPU hours to start". Budget credits across experiments.
  - Lightning free tier: no credit card required (phone verification is required). Card only unlocks the extra 25 credits.
  - Binding constraint for 2–7h jobs: free Studios "run 24/7 but require restart every 4 hours". Jobs ≤~4h fit one window; 5–7h jobs need checkpoint/resume design. Pro+ removes this limit.
  - Lightning Free: 1 active Studio, max 1 GPU/Studio, 2 concurrent GPUs, 32-core CPU, 10 GB free storage / 50 GB persistent limit (Studio working disk default 400 GB). Free hours by GPU: T4 75h, L4 31h, L40S 5h, A100-40GB 10h, A100-80GB 5h.
  - Lightning conflict: pricing page lists "80% off interruptible (spot)" as a Free feature and FAQ says 30 credits ≈ 80 GPU hours on interruptible, but interruptible-machines docs say "Upgrade to paid tiers to start using interruptible machines". Verify in-product before relying on free spot.
  - Hugging Face has NO free path for 2–7h training: ZeroGPU Spaces = 5 min/day quota (Gradio-only, demo/inference); Jobs = training-capable but requires positive credit balance (T4 $0.40/hr, default timeout 30 min, settable longer); Spaces GPU = paid (CPU Basic is the only free Space hardware); Inference = inference-only.
  - HF PRO ($9/mo) includes only $2.00/month compute credits (~5h T4) usable on Jobs — paid and insufficient for routine 2–7h jobs.
  - Tooling note: `firecrawl` bare command is NOT on PATH; use `npx --yes firecrawl-cli`. PowerShell 5.1 rejects `&&` — separate commands with `;`. Reddit scrapes fail (blocked); only search-snippet quotes available. HF docs are reliably scraped from `raw.githubusercontent.com/huggingface/hub-docs/main/docs/hub/*.md` when huggingface.co HTML scrapes are nav-heavy.
