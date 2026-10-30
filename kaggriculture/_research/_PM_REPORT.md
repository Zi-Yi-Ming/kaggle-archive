# Kaggriculture Open Strategy Scout — Final Report

## 1. Executive Summary

**Mission**: Find 1-3 executable open-source Kaggriculture agents worth benchmarking against v11E (Elo 942/949.9). Strict constraints: do NOT modify v11E, do NOT submit to Kaggle, do NOT treat replay tapes as agents.

**Bottom line**:
- Local reference pool fully catalogued (10 tiers + v11E/v12/D/B/A).
- v11E post **74.5% win rate** (Wilson 68.0%–80.0%) over 200 paired games against the local pool, with mean margin **+57,302 coins.
- Only `closer_cleo` (tier 9, `_SELLS_FIRST=False`) consistently exploits v11E’s market controller; v11E goes 7-43 vs that layout.
- External scan found **4 strong candidates** with executable `agent(obs)` and public strength claims.

## 2. Local Benchmark Results (Phase 2-3)

All games were paired (seeds 1-50, alternating seat 0/1), run through `kaggle_environments` via `_pm_bench.py`. CSV: `_pm_bench.csv`.

### 2.1 v11E vs Key Opponents (50 games each)

| Opponent | Tier | Type | Games | Wins | Losses | Win Rate | Wilson 95% CI | Avg Margin |
|---|---|---|---|---|---|---|---|---|
| broker_bea | 6 | tape + market controller | 50 | 42 | 8 | 84.0% | 71.5% – 91.7% | +2,867 |
| rancher_rita | 5 | adaptive policy | 50 | 50 | 0 | 100% | 92.9% – 100% | +106,241 |
| closer_cleo | 9 | tape (in-place sell) | 50 | 7 | 43 | 14.0% | 7.0% – 26.2% | -1,150 |
| melon_mateo | 4 | adaptive MELON specialist | 50 | 50 | 0 | 100% | 92.9% – 100% | +121,250 |

### 2.2 Combined Summary (200 games)

| Metric | Value |
|---|---|
| Total games | 200 |
| Wins | 149 |
| Losses | 51 |
| Win rate | 74.5% |
| Wilson 95% CI | 68.0% – 80.0% |
| Mean margin | +57,302 |

### 2.3 Structural Insight

All tape-based tiers 6-9 share the **identical `_TRACE` field plan** and **identical `_MP` price model**. The only meaningful differences are market-layer SELL ordering knobs:
- `broker_bea / ledger_lena / slotter_silas`: `_SELLS_FIRST = True` (sorted sells take earliest slots).
- `closer_cleo`: `_SELLS_FIRST = False` (sells stay in original tape slots).
- `broker_bea` adds `_PROMOTE_IF_OPP_MONEY = {'WHEAT': 200.0}` for opportunistic wheat timing.

`closer_cleo`’s opposite layout is the only local opponent that structurally disrupts v11E’s market controller, suggesting v11E’s slot-assumption is a real fragility.

## 3. External Candidate Classification (Phase 0 / Background Audit)

All four repos below have standard `agent(obs)` signatures, no `kaggle_environments` import, and use standard obs keys (`step`, `day`, `player`, `farms`, `private`).

### 3.1 Tier S — Seyamalam/Kaggriculture
- **URL**: https://github.com/Seyamalam/Kaggriculture
- **Executable**: Yes — `main.py` (self-contained, ~5,000 lines).
- **Strategy type**: tape + router + adaptive.
  - *Tape*: compressed expert schedules (`_FIXED_SCHEDULE_B85`, `_V10_SCHEDULE_B85`, `_V11_RADIANT_SCHEDULE_B85`, `_V12_SYOUYA_SCHEDULE_B85`, `_V13_SENKIN_SCHEDULE_B85`, `_V16_P0/P1_SCHEDULE_B85`, `_V17_SCHEDULE_B85`, `_V18_RUNTIME_B85`).
  - *Router*: schedule dispatcher selects among V8–V18 experts based on `STRATEGY["fixed_schedule_version"]` and opening public signature.
  - *Adaptive*: v17 frozen MLP pairwise ranker (53→16→1); v18 closed-loop market expert re-selected daily; recovery sweep (`_v18s_recovery_sweep`) and capital-latch gate (`_v21_late_abstain`).
- **Claimed strength**: Rating **2,053.6** (V18 public release 24-3; V21 100/110 on frozen corpus, 29/30 on live-15).
- **Integration**: Drop-in via `importlib.util`; requires per-episode reset of `_V18_SELECTED_MARKET`, `_V18_SELECTED_BOARD`, `_WEED_STATE`, `_META_STATE`.

### 3.2 Tier A — COK-ZhangZiliang/Kaggriculture
- **URL**: https://github.com/COK-ZhangZiliang/Kaggriculture
- **Executable**: Yes — `main.py` (~2,000 lines).
- **Strategy type**: tape + repair.
  - *Tape*: compressed action schedules (`_ACTIONS_10C4S_3Q`, `_ACTIONS_8C6S_3Q`, `_ACTIONS_6C8S_3Q`) plus V7 routes/sales schedule.
  - *Repair*: weed repair, cow alignment, terminal liquidation, front-running opportunistic sells, fail-closed opening recovery gate at step 72.
- **Claimed strength**: Submission `55848408` reached `COMPLETE`; 597-game corpus **339-3-255** (mean margin +1,266); fresh 80-game closed-loop panel **68 wins**.
- **Integration**: Drop-in via `importlib.util`; accepts `(obs, config=None)`. Requires per-episode reset of `_ACTION_CACHE` and `_META_STATE`.

### 3.3 Tier A — gytdrop/KaggricultureAgent
- **URL**: https://github.com/gytdrop/KaggricultureAgent
- **Executable**: Yes — `policy.py` + `main.py`.
- **Strategy type**: mined heuristic.
  - Mirrors exact crop/animal/market/specs from 72 leaderboard replays (144 player-episodes, top scores 100k–158k).
  - `main.py` delegates to `policy.agent(obs, config)`. No tapes, no learned weights in shipped agent.
- **Claimed strength**: Phase3 v1 **16/16** vs A1 (p=0.000), local mean ~111–116k. `CHECKPOINT_RESUME.md` notes a −113k regression from an RL rewrite, so the heuristic v5 is the validated build.
- **Integration**: Standard `agent(obs)`; lowest overhead of the three.

### 3.4 Tier B — graceyunliu/kaggriculture
- **URL**: https://github.com/graceyunliu/kaggriculture
- **Executable**: Yes — `candidates/H30.py`, `candidates/H11.py`, `candidates/H12.py`, `candidates/C1.py`, `main.py`.
- **Strategy type**: tape + router / tape + repair.
  - `H30`: full 720-step tape with guard and C1 fallback.
  - `H11/H12`: tape with divergence guard + C1 fallback; H12 recommended over H10.
  - `C1`: knob-parameterized heuristic (frontier opening).
- **Claimed strength**: H30 loses only $0.4k/game to `tape_yuan800`, $2.0k to `tape_strawhats`, and beats V3.12 by $41.3k/game. H11 cuts loss to `tape_strawhats` from $98.4k to $24.2k/game.
- **Integration**: Drop-in; each candidate file exports `agent(obs)`.

## 4. Tier Classifications

| Tier | Agent | Strategy Type | Executable | Evidence Base | Verdict |
|---|---|---|---|---|---|
| **S** | Seyamalam V21 | tape + router + adaptive | Yes | 2053.6 rating, 100/110 wins, 29/30 live | Benchmark mandatory — highest historical public score |
| **A** | COK-ZhangZiliang V10 | tape + repair | Yes | 597 games 339-3-255, 68/80 fresh panel | Benchmark — strongest fail-closed repair overlay |
| **A** | gytdrop v5 | mined heuristic | Yes | 16/16 vs A1, ~116k local mean | Benchmark — best non-tape open heuristic |
| **B** | graceyunliu H30 | tape + router | Yes | H30 loss $0.4k to tape_yuan800 | Lower priority; interesting if Seyamalam integration fails |
| **B** | lonespear main | pure heuristic | Yes | Rating 921, 13-11 | Already covered by local reference strength |
| **B** | GzmCR main | pure heuristic | Yes | 11-5 holdout | Already covered by local reference strength |
| **Reject** | diffmap/kaggicultureRL | RL training only | No | PPO stack, no `agent(obs)` | Not executable as submitted |
| **Reject** | bravefe/Kaggriculture | starter tutorial | Partial | `melon_maxxer` notebook cell | Not a competitive agent |
| **Reject** | gnr8trAI-stack/kaggriculture | experimental baseline | Yes | README admits unvalidated | No strength evidence |
| **Reject** | rooklift/krobus | replay viewer | Yes | JS only | Not an agent |
| **Reject** | sidhulyalkar/kaggriculture | unknown | Unknown | Rate-limited, no verified source | Insufficient evidence |

## 5. Answers to the 6 Required Questions

**Q1: Most promising candidate?**
**Seyamalam V21** is unambiguously the most promising open-source agent ever published for Kaggriculture. At rating **2,053.6**, it is more than double v11E’s 942/949.9. Its architecture (tape + router + closed-loop market + frozen neural ranker + capital-latch recovery) is the strongest evidence that “copying open-source can reach silver” is real.

**Q2: Which candidates are most similar to v11E and easiest to port?**
`broker_bea` and `closer_cleo` are already local; they ARE v11E’s ancestors. Of the external set, **COK-ZhangZiliang V10** is closest in spirit: same tape+repair philosophy, same fail-closed safety culture, same market overlay concerns. Its `_weed_repair_action`, `_terminal_liquidate`, and `_front_run` map directly onto v11E concepts.

**Q3: Which candidates offer the most diverse strategic ideas?**
- **gytdrop v5** is the most diverse: a pure mined-heuristic agent with no tape, no router, no learned weights. Its strength comes from exact engine mirroring and 72-replay mining — a completely different inductive bias from v11E’s belief + hazard + beam-search stack.
- **graceyunliu H30** offers the tape+router divergence-guard pattern, which is absent from v11E’s current market controller.

**Q4: Should we benchmark Seyamalam given the rating gap?**
Yes, but **measure win rate + margin, not Elo**. A blowout will still be informative: Seyamalam’s closed-loop market selection and capital-latch gate are concrete mechanisms. If v11E loses >90% with mean margin <-200k, the gap is architectural (closed-loop > open-loop). If margin is closer, the gap is in the ranker/latch details.

**Q5: Which candidate should we benchmark first?**
Benchmark order:
1. **gytdrop v5** — fastest to integrate, lowest overhead, gives a quick heuristic ceiling.
2. **COK-ZhangZiliang V10** — moderate integration, tests tape+repair directly.
3. **Seyamalam V21** — heaviest import, requires state-reset hook, but highest information yield.

**Q6: What is the expected outcome?**
Local data already shows v11E is **top-tier against the local pool** (74.5% win rate, +57k mean margin). Against external open-source:
- **gytdrop v5** and **COK V10**: v11E likely still wins (>60%), but margin will shrink because both have stronger market overlays than local tiers.
- **Seyamalam V21**: v11E will likely lose (>70% loss rate) given the 1,100-point rating gap. The useful signal is *how* it loses: if v11E stays close on money but loses on market timing, the fix is in the controller; if v11E collapses early, the fix is in the board planner.

## 6. Recommendations

1. **Immediate**: Integrate `gytdrop v5` and `COK-ZhangZiliang V10` into `_pm_pool.py` and run 50-game paired benchmarks vs v11E. These are the highest-yield, lowest-risk external tests.
2. **Short-term**: Clone Seyamalam, add state-reset hook, run 30-game paired benchmark. Do not run 50 games unless the 30-game margin looks informative.
3. **Do NOT integrate into v11E yet.** The local-vs-local gap already proved v11E’s market controller has a known fragility (`closer_cleo` layout). Adding external agents without first hardening v11E’s slot logic will just produce more losses.
4. **Hardening target**: v11E’s `_SELLS_FIRST` assumption and the slot-layout logic in `_plan_sells` / `_sell_priority` are the most exposed code paths. closer_cleo’s 86% win rate vs v11E is a reproducible bug, not noise.

## 7. Deliverables

- `kaggriculture/_pm_bench.csv` — raw benchmark results (1,480 lines, multiple agents and opponents).
- `kaggriculture/_quick_analysis.py` — Wilson CI + win-rate analysis script.
- This report: `kaggriculture/_PM_REPORT.md`.
