---
written-at: 1790669943513
---
# T10 Progress Journal

## §1 Task identity
- task_id: T10
- short summary: Research top public-leaderboard strategies for the 0.93–0.96 cluster on RSNA Knee Abnormality Detection 2026 (Kaggle).

## §2 Subagent intent
This subagent was asked to research a single angle for a solo Kaggle competitor on rsna-knee-abnormality-detection (12-label macro AUC, deadline 2026-10-22, currently 0.721 vs a top cluster of ~0.956–0.960): find what top teams actually did, using web searches and primary sources (official docs, original writeups, papers) rather than generic advice. The deliverable was an information-dense findings file at D:/桌面/Kaggle/research/rsna-top-strategies/findings/F1.md in a strict template (Findings with quote/url/source_type/published/confidence, Dead ends, Suggested follow-ups), 5–12 solid sourced claims, plus a short orchestrator-facing summary.

## §3 Files and code sections
- D:/桌面/Kaggle/research/rsna-top-strategies/findings/F1.md: created the required F1 findings file (14 findings) covering competition shape, label-extraction ceiling, public-LB score ladder, soft labels, laterality/flips, ensemble negatives, measurement protocol, winning configs, weak columns, and code-comp constraints.
- D:/桌面/Kaggle/research/rsna-top-strategies/findings/: created directory.
- .firecrawl/: attempted firecrawl search output dir (empty — CLI not installed).

## §4 Verbatim commands
```
New-Item -ItemType Directory -Force -Path "D:/桌面/Kaggle/research/rsna-top-strategies/findings" | Out-Null
Get-ChildItem "D:/桌面/Kaggle/research" -ErrorAction SilentlyContinue | Select-Object Name
Get-Command firecrawl -ErrorAction SilentlyContinue; Get-ChildItem "C:\Users\Lenovo\.agents\skills\firecrawl" -Recurse -Include *.ps1,*.cmd,*.bat,firecrawl* -ErrorAction SilentlyContinue | Select-Object FullName -First 20; where.exe firecrawl 2>$null; npm list -g firecrawl 2>$null
Get-Item "D:\桌面\Kaggle\research\rsna-top-strategies\findings\F1.md" | Select-Object FullName, Length; (Get-Content "D:\桌面\Kaggle\research\rsna-top-strategies\findings\F1.md" | Select-String "^### \[").Count
```

Web searches / fetches performed via WebFetch (firecrawl CLI unavailable):
```
https://duckduckgo.com/html/?q=RSNA+Knee+Abnormality+Detection+2026+kaggle+top+solution+leaderboard
https://www.bing.com/search?q=kaggle+RSNA+2026+knee+abnormality+detection+solution+leaderboard+AUC
https://www.google.com/search?q=kaggle+rsna+2026+knee+abnormality+detection+top+teams+solution+writeup
https://html.duckduckgo.com/html/?q=RSNA+knee+MRI+AI+challenge+2026+kaggle+ensemble+multi-instance+top+score+solution
https://html.duckduckgo.com/html/?q=%22rsna-knee-abnormality%22+kaggle+2026+%220.95%22+OR+%220.96%22+OR+%22first+place%22+OR+%22gold%22+solution
https://huggingface.co/blog/bishnoiyash/rsna-competetion
https://github.com/mathischmp/challenge_rsna
https://raw.githubusercontent.com/mathischmp/challenge_rsna/main/README.md
https://github.com/shraddhauser/rsna-knee-detection
https://github.com/SathishKumarAI/rsna-knee-2026
https://www.rsna.org/artificial-intelligence/ai-image-challenge/knee-mri-ai-challenge
https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/leaderboard
https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion
https://www.kaggle.com/datasets/pilkwang/rsna-knee-llm-labels
```

## §5 Outcome and discoveries
- Outcome (partial): Wrote F1.md with 14 sourced findings from three competitor writeups + official RSNA docs. The specific 0.93–0.96 top-cluster strategy could not be sourced — no public writeup exists for that band, and Kaggle leaderboard/discussion pages are JS-gated and returned empty shells via WebFetch. Closest public artifact is a "public reference (single model)" at 0.928 LB. Overall confidence: high on the 0.85–0.928 mechanics, low on the 0.93–0.96 delta itself.
- Discoveries that may matter for other tasks:
  - Competition shape: 12-label macro AUC, 4,407 train studies / 24,371 series / ~820k slices, only 58 expert labels; 4,349 rely on free-text multilingual reports; test.csv has no report column. Entry 2026-10-15, submit 2026-10-22, $77k incl. efficiency prize, 9h offline code-comp on ~1,300 hidden studies.
  - Label extraction is the real bottleneck: rank-18 pipeline (0.903 LB, 18/792 on 2026-08-09) used Qwen3.6-35B via Ollama with clinical-rule prompt, 0.833 mean acc / 0.766 mean F1 vs gold-58; intrinsic ceiling ~0.88–0.92 because reports disagree with image re-reads.
  - Score ladder: DINOv2-S 18-slice = 0.853 LB; CoAtNet-2 window-bags 64-slice per-finding attention = 0.920 LB / 0.903 gold-58; "public reference" single model = 0.928 LB / 0.920 gold-58. Slice coverage 18→64 mattered more than encoder swap.
  - Consensus preprocessing contract: sort slices by ImagePositionPatient on slice normal (NOT filename/InstanceNumber), per-series percentile windowing, mm-space crop via PixelSpacing (varies 3.4×), ban horizontal flips (5/12 labels are laterality-specific; Laterality tag missing on half the corpus by vendor).
  - Soft labels with per-cell confidence as loss weight beat hard 0/1; silence-in-report must not be taught as absent (esp. synovitis).
  - Ensemble negatives: blending same-recipe models worthless (rank corr 0.92); equal fusion of 4 report readers worse than best single reader; more inference slices than training hurt 5/5 folds; DINOv2-B looked better on proxy but worse full-scale.
  - Measurement protocol: gold-58 AUC SE ~0.086 — never train/select on the 58 (leaked 0.9357 collapsed to honest 0.8568); measured noise floor 0.0015, require ≥0.004 holdout gain; calibrate gold→LB offset (+0.017 for CoAtNet family).
  - Weakest columns to close the 0.93+ gap: lateral meniscus (−0.09 vs public reference) and MCL (−0.06) — both laterality-dependent.
  - Public third-party label set exists: kaggle.com/datasets/pilkwang/rsna-knee-llm-labels (used as a third fusion vote by rank-18).
  - Tooling: firecrawl CLI is NOT installed on this machine (skill doc assumed it); DuckDuckGo captcha'd mid-run; Brave 429 / Ecosia 403 / Mojeek transport error. Kaggle pages need a JS-capable browser (playwright) or authenticated Kaggle API for any future LB/discussion pull. PowerShell 5.1 on this box rejects `&&` — use `;`.
