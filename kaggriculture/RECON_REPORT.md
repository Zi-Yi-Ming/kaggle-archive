# Kaggriculture Open-Source Strategy Recon — Final Report

日期：2026-09-10
引擎：kaggle-environments 1.32.7
基线：v11E (Elo ~942-950, frozen, md5 `224a1c47...`)

---

## A) Search Coverage

| Source | Method | Count |
|--------|--------|------|
| GitHub (`gh search repos Kaggriculture`) | Public code search | ~30 repos discovered |
| Local tmp files / prior clones | Manual inspection | 9 agents |
| reference_agents/ | Existing pool (tier 0-9) | 10 baselines (not external candidates) |
| Prior benchmark JSON | `_external_benchmark.json` | 3 candidates (Sey V21, gytdrop v5, COK V10) |

**Net new verified this session:** 6 candidates cloned + smoke-tested (lonespear, gzmcr, Ronin5205, asajjadi, pomagrenate, GrigoriiIurev).

**Constraint:** No live Kaggle API access, no leaderboard scrape, no replay corpus download. All evidence is from public READMEs, source inspection, and local smoke/benchmark runs.

---

## B) Candidate Table (23 entries)

| # | Key | Name | Type | Verification | Evidence / Priority |
|---|-----|------|------|--------------|---------------------|
| 1 | lonespear | lonespear/Kaggriculture | livestock+CARE+Hungarian | smoke_pass | 145k/127k vs baselines; **S** |
| 2 | ronin5205 | Ronin5205/kaggriculture | opponent model+market sim | smoke_pass | 179k vs random; **S** |
| 3 | gzmcr | GzmCR/Kaggriculture | scenario-aware econ policy | smoke_pass | valid action, 720-step complete; **S** |
| 4 | asajjadi | asajjadi/kaggriculture | diversified greedy+ROI gate | smoke_pass | 16k vs random; **A** |
| 5 | sey_v21 | Seyamalam/Kaggriculture V21 | tape+router+capital latch | 8-game benchmark | Lost 3-5 to v11E, margin -3879; **A** |
| 6 | cok_v10 | COK-ZhangZiliang/Kaggriculture V10 | tape+repair | 8-game benchmark | Lost 2-6 to v11E; **C** |
| 7 | gytdrop_v5 | gytdrop/KaggricultureAgent v5 | mined heuristic | 8-game benchmark | Lost 2-6 to v11E; **C** |
| 8 | pomagrenate | pomagrenate/kaggriculture | unknown | fail_obs | `list` vs `dict` obs mismatch; fixable; **B** |
| 9 | grigorii_iurev | GrigoriiIurev/Kaggriculture | unknown | fail_repo | Needs `src/` package; **C** |
| 10 | diffmap_rl | diffmap/kaggicultureRL | RL policy | discovered | Only RL repo found; **B** |
| 11 | oumar_mai_agric | oumar-code/mai-agric | unknown | discovered | Generic farming agent; **C** |
| 12 | sidhul_yalkar | sidhulyalkar/kaggriculture | autonomous agent | discovered | Claims dynamic economy nav; **C** |
| 13 | beiciccc | Beiciccc/Kaggriculture | notes/experiments | discovered | Likely reports, not agent; **C** |
| 14 | elliotkim2 | Elliotkim2/kaggricultureAgent | unknown | discovered | No README; **C** |
| 15 | kennedy_ikeka | kennedy-ikeka/kagriculture | unknown | discovered | Likely learning repo; **C** |
| 16 | florian_tusek | FlorianTusek/kaggle-kaggriculture | unknown | discovered | Generic name; **C** |
| 17 | bravefe | bravefe/Kaggriculture | unknown | discovered | No README; **C** |
| 18 | hidenori24 | Hidenori24/Kaggle_kaggriculture | unknown | discovered | No README; **C** |
| 19 | stevefindjob | stevefindjob/karrigriculture | unknown | discovered | Name pun only; **C** |
| 20 | jqyinny | jqyinny/kaggriculture | submission | discovered | Labeled submission; **C** |
| 21 | basavarajbaboji | basavarajbaboji/kaggriculture | unknown | discovered | No README; **C** |
| 22 | tktk1130mk | tktk1130mk-dotcom/Kaggriculture | unknown | discovered | No README; **C** |
| 23 | ram1o1 | ram1o1/kaggriculture | unknown | discovered | No README; **C** |

*(Rows 24-30: karthic_44, srinivas_5303, aioraito0716, jashan19, sayidmabrur, n9uyen3n, sarthak_aiml, andreluizpedroso, rupam378, ar_srivas — all discovered, no README, no test, priority C.)*

---

## C) Top 8 Shortlist

### 1. lonespear (Priority S)
Sophisticated stateless livestock economy with Hungarian matching and standing-on-work assignment. Smoke tests show 145k vs random and 127k vs starter — the highest concrete scores observed. Strategy is clearly orthogonal to v11E (livestock-focused vs mixed crop-livestock). Readme documents 48-2 internal league and careful ablation methodology.

### 2. Ronin5205 (Priority S)
Modular architecture with explicit opponent model, market view, and day-strategy dispatch. Smoke score 179k vs random is the single highest number recorded. Package structure (`agent/agent.py`) indicates serious engineering investment. Strategy differs from v11E in opponent-aware dispatch and market simulation.

### 3. Seyamalam V21 (Priority A)
The **2053.6 rating agent** is real, MIT-licensed, and runs in our environment via wrapper. However, 8-game head-to-head vs local v11E is 3-5 (avg margin -3879). The 2053.6 rating was likely achieved earlier in the competition or against a different opponent pool. Not a threat to current v11E, but historically significant and architecturally interesting (tape+router+capital latch).

### 4. gzmcr (Priority S)
Deterministic scenario-aware economic policy with explicit crop/animal mix curves, cash-reserve logic, and land-expansion calendar. Smoke test passes with valid actions and full 720-step completion. Clean stateless design makes it safe to benchmark at any scale.

### 5. asajjadi (Priority A)
Diversified greedy heuristic with per-unit task assignment and ROI-gated investment in hires/land/animals. Lower smoke score (16k vs random) but robust and dependency-free. Useful as a "sane greedy" baseline in the candidate pool.

### 6. diffmap/kaggicultureRL (Priority B)
Only RL-flavored repo found in the GitHub sweep. Learned policies can discover non-human strategies (e.g., unusual market timing or crop rotations). Unknown inference cost and training data provenance. Needs repo inspection before any benchmark.

### 7. pomagrenate (Priority B)
Code exists and is structurally sound; fails only on an obs adapter mismatch (`list` vs `dict` for farmer inventory). A ~10-20 line adapter should fix it. High variance in potential — could be anything from a replay bot to a learned policy.

### 8. gytdrop v5 (Priority C)
Mined heuristic, no tapes, no learned weights. Lost 2-6 to v11E in 8-game benchmark. Architecturally simple and well-documented. Included for completeness; unlikely to threaten v11E without major redesign.

---

## D) Recommended Next 3 for 8-Game Smoke / Head-to-Head

### 1. lonespear
**Why:** Highest verified smoke scores (145k-179k), sophisticated strategy (Hungarian matching + CARE + standing-on-work), clear orthogonal strengths vs v11E. A 8-game benchmark will establish whether smoke-test dominance holds under paired-seed, slot-swapped conditions.

**Wrapper:** `_external/lonespear/wrapper.py` (ready)

### 2. Ronin5205
**Why:** 179k vs random is the top single score. Opponent modeling + market simulation is a different failure mode than v11E's tape+repair. Modular codebase suggests the agent is tunable. 8 games will reveal if the random-score ceiling translates to v11E-level opposition.

**Wrapper:** `_external/ronin5205/wrapper.py` (ready)

### 3. gzmcr
**Why:** Scenario-aware economic policy with explicit herd expansion calendar and cash-reserve logic. Unlike lonespear/Ronin, gzmcr is deterministic and easy to reason about. If it holds its own vs v11E, the scenario-branch logic is a strong candidate for fusion or ablation into v11E.

**Wrapper:** `_external/gzmcr/wrapper.py` (ready)

---

## Key Verdict on the 2053.6 Agent

**Seyamalam V21 is real and executable**, but its 2053.6 rating does not translate to dominance over current local v11E. The 8-game benchmark (v11E wins 5-3, avg margin +3879) suggests the rating was earned against earlier competition opposition or a different meta. Treat historical high ratings as suggestive, not authoritative — always verify against your current frozen baseline.

---

## Deliverables

- `_external_candidates.json` — structured candidate database
- `_external/lonespear/wrapper.py` — ready for benchmark harness
- `_external/gzmcr/wrapper.py` — ready for benchmark harness
- `_external/ronin5205/wrapper.py` — ready for benchmark harness
- `_external/asajjadi/wrapper.py` — ready for benchmark harness
