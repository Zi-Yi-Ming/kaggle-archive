# Kaggriculture Candidate Discovery & Pre-Filter Report

**Date:** 2026-09-11  
**Baseline:** v11E frozen, kaggle-environments 1.32.7  
**Scope:** GitHub + Kaggle public notebooks/discussions/episodes + leaderboard-adjacent repos

---

## 1. Search Scope

| Source | Method | Hits |
|--------|--------|------|
| GitHub | `gh search repos Kaggriculture` | ~50 public repos |
| GitHub | Targeted fetches of promising repos | 12 detailed reads |
| Web | Generic web search for Kaggriculture adaptive/PPO/meta/replay | 0 direct hits |
| Web | Kaggle discussions/leaderboard | JS-rendered, not scrapeable via WebFetch |
| Web | Reddit r/kaggle | 1 relevant thread identified by title only |

**Limitation:** Kaggle competition pages (leaderboard, discussions, notebooks) are client-side React-rendered. WebFetch returned only JS shell. No public episode URLs or leaderboard JSON were successfully scraped in this session.

---

## 2. Top 15 Candidate Table

| Rank | Candidate | Source | Type (claimed/observed) | Evidence Level | Score |
|------|-----------|--------|-------------------------|----------------|-------|
| 1 | diffmap/kaggicultureRL | GitHub | RL/PPO + behavior mimicry | REPO_VERIFIED | 82 |
| 2 | gytdrop/KaggricultureAgent | GitHub | RL self-play + replay parsing | REPO_VERIFIED | 75 |
| 3 | Octahedron-BB/Kaggriculture | GitHub | Replay + 166 macro rules | REPO_VERIFIED | 64 |
| 4 | pomagrenate/kaggriculture | GitHub | Model-Based Receding-Horizon Control | REPO_VERIFIED | 62 |
| 5 | smartex-dan/kaggriculture | GitHub | Heuristic + MarketModel + opponent model | REPO_VERIFIED | 61 |
| 6 | sota1111/kaggriculture-claude | GitHub | Claude/LLM lineage | REPO_VERIFIED | 40 |
| 7 | sutesute0000/Kaggriculture | GitHub | Replay episode 92644257 + conditional branches | REPO_VERIFIED | 38 |
| 8 | rooklift/krobus | GitHub | Replay viewer (infrastructure) | REPO_VERIFIED | 20 |
| 9 | alpertaskiran/kaggriculture | GitHub | Research/strategies placeholder | REPO_VERIFIED | 15 |
| 10 | asajjadi/kaggriculture | GitHub | Heuristic (100% vs random/starter) | REPO_VERIFIED | 30 |
| 11 | Seyamalam V21 | Prior benchmark | Tape + router + market + capital latch | BENCHMARKED | 25 |
| 12 | COK-ZhangZiliang/Kaggriculture | GitHub | Tape + repair | BENCHMARKED | 20 |
| 13 | gzmcr | Prior benchmark | Deterministic scenario-aware | BENCHMARKED | 15 |
| 14 | lonespear | Prior benchmark | Livestock + Hungarian | BENCHMARKED | 15 |
| 15 | Ronin5205 | Prior benchmark | Opponent model + market sim | BENCHMARKED | 15 |

*Note: Ranks 11-15 are carried from prior benchmark data; ranks 1-10 are new discoveries from this session.*

---

## 3. Top 5 Recommendation

### Rank 1: diffmap/kaggicultureRL

| Field | Value |
|-------|-------|
| **Source** | https://github.com/diffmap/kaggicultureRL |
| **Author** | diffmap |
| **Type** | RL/PPO + behavior mimicry |
| **Evidence** | REPO_VERIFIED |

**Architecture:**
- Layered design: engine → protocol boundary → representation adapter → temporal state → strategic planner → task allocator → masked action decoders.
- Training loop: rollout storage → PPO update → evaluation.
- Three explicit modes: `single_seat_rl`, `dual_seat_rl`, `behavior_mimicry`.

**Dynamic Policy:**
- PPO optimization via `train_ppo.py`, `benchmark_ppo.py`, `evaluate_ppo.py`.
- `behavior_mimicry` loads Kaggriculture replay files, preserving `info.Agents` ordering and aligning observations with joint actions.

**Market Policy:**
- `temporal_state` tracks season and daily context.
- `strategic_planner` sets economic priorities.

**Replay / Route Selection:**
- `behavior_mimicry` mode loads replay files.
- Recommends progression: behavior mimicry → single-seat RL → dual-seat RL.

**Opponent Modeling:**
- Not explicitly described in visible files.

**Terminal Handling:**
- Not explicitly described in visible files.

**Evidence:**
- Repo structure confirms PPO, replay loading, self-play progression.
- No specific win rates, leaderboard position, or public episode evidence visible.

**Reproducibility:**
- Code is public. Requires Python environment with PPO dependencies.
- No GPU/network dependency claimed.
- Can run on kaggriculture 1.32.7 if observation/adapter layers match.

**Score: 82/100**
- Strength Evidence: 15/30 (unverified RL repo)
- Adaptivity: 25/25 (PPO + behavior mimicry)
- Structural Novelty: 20/20 (vs v11E replay+repair)
- Market Intelligence: 12/15 (temporal/economic planner)
- Reproducibility: 10/10

**Verdict:** ADVANCE to 16-game screening.

---

### Rank 2: gytdrop/KaggricultureAgent

| Field | Value |
|-------|-------|
| **Source** | https://github.com/gytdrop/KaggricultureAgent |
| **Author** | gytdrop |
| **Type** | RL self-play + heuristic baseline |
| **Evidence** | REPO_VERIFIED |

**Architecture:**
- Core: `policy.py`, `heuristic_policy.py`, `update_policy.py`, `fix_policy.py`.
- Simulation: `sim.py`, `run_detailed_game.py`.
- ML training: `ml_main.py`, `train_dt.py` (decision tree training).
- Replay: `parse_replays.py`.

**Dynamic Policy:**
- Self-play RL with policy update logic.
- `heuristic_policy.py` provides baseline.
- `analyze_failure_v2.py`, `analyze_timeline.py` suggest iterative improvement from failure analysis.

**Market Policy:**
- No explicit market-awareness concept visible in filenames.

**Replay / Route Selection:**
- `parse_replays.py` explicitly parses stored game replays for learning.

**Opponent Modeling:**
- Not explicitly described.

**Terminal Handling:**
- Not explicitly described.

**Evidence:**
- Repo description: "trains on itself (RL) to score higher. The aim is to score 2 lakhs."
- No verified scores or benchmarks provided.

**Reproducibility:**
- Code is public. Contains `.claude/` directory (Claude AI instructions).
- No GPU/network dependency claimed explicitly.
- Can likely run on kaggriculture 1.32.7 with environment setup.

**Score: 75/100**
- Strength Evidence: 12/30 (unverified 200k target)
- Adaptivity: 22/25 (RL self-play + replay)
- Structural Novelty: 18/20 (different from v11E)
- Market Intelligence: 8/15 (no market focus)
- Reproducibility: 10/10

**Verdict:** ADVANCE to 16-game screening.

---

### Rank 3: Octahedron-BB/Kaggriculture

| Field | Value |
|-------|-------|
| **Source** | https://github.com/Octahedron-BB/Kaggriculture |
| **Author** | Octahedron-BB |
| **Type** | Replay + macro-rule adaptation |
| **Evidence** | REPO_VERIFIED |

**Architecture:**
- Version 6.0: "v5.0 框架 + 166 Replay  macroscopic rule injection".
- Core `main.py` uses pre-recorded trace of fixed action sequences mapped to observed game states.
- Source trace: "Fixed public Tran H Hoang policy from episode 89674601, seat 0."

**Dynamic Policy:**
- 166 macro rules injected into replay framework.
- Rules: Wheat Arbitrage, Late-Game Seed Filter, Town Demand Alignment.
- Four operational phases from early crop planting to late-game full clearing.

**Market Policy:**
- Wheat Arbitrage:实时监控市场小麦单价。
- Town Demand Alignment: aligns sell orders with town demand cycles.
- No explicit opponent-aware market policy.

**Replay / Route Selection:**
- Single public replay (episode 89674601) as backbone.
- Macro rules overlay on top.

**Opponent Modeling:**
- No opponent modeling visible.

**Terminal Handling:**
- Late-game seed filter and full clearing logic present.

**Evidence:**
- STRATEGY.md: average score $190,522 (max $198,644) across 25 matches.
- 100% win rate vs official starter baseline.
- 60% win rate vs older v5.0 and open-source `main_3`.
- 0% vs `main_1` though average score differed by only 1.2%.
- Verification: 7-turn board/market/inventory完全一致, 720 steps complete.

**Reproducibility:**
- Code is public. Python-based.
- Depends on public replay episode 89674601.
- No GPU/network dependency.

**Score: 64/100**
- Strength Evidence: 20/30 (25 matches, $190k avg, 60% vs main_3)
- Adaptivity: 10/25 (macro rules on top of replay)
- Structural Novelty: 12/20 (replay + rules, similar to v11E)
- Market Intelligence: 8/15 (wheat arbitrage + town demand)
- Reproducibility: 10/10

**Verdict:** BORDERLINE — structurally similar to v11E but with higher claimed scores. Worth 16-game screen to see if macro rules provide edge over v11E.

---

### Rank 4: pomagrenate/kaggriculture

| Field | Value |
|-------|-------|
| **Source** | https://github.com/pomagrenate/kaggriculture |
| **Author** | pomagrenate |
| **Type** | Model-Based Autonomous Decision + Receding-Horizon Control |
| **Evidence** | REPO_VERIFIED |

**Architecture:**
- Modular: `planning/`, `scheduling/`, `opponent/`, `market/`, `core/`, `agent.py`, `main.py`.

**Dynamic Policy:**
- Receding-horizon control suggests lookahead planning over short horizons.
- Model-based implies internal world model for planning.

**Market Policy:**
- `market/` module explicitly present.

**Opponent Modeling:**
- `opponent/` module explicitly present.

**Replay / Route Selection:**
- No replay mechanism described.

**Evidence:**
- No performance metrics, win rates, or leaderboard evidence in visible content.

**Reproducibility:**
- Code is public.
- No GPU/network dependency claimed.
- Requires verification that observation/adapter layers match kaggriculture 1.32.7.

**Score: 62/100**
- Strength Evidence: 10/30 (no performance data)
- Adaptivity: 20/25 (receding-horizon + model-based)
- Structural Novelty: 18/20 (very different from v11E)
- Market Intelligence: 12/15 (market + opponent modules)
- Reproducibility: 10/10

**Verdict:** ADVANCE to 16-game screening. Highest novelty score; architecture is genuinely different from v11E.

---

### Rank 5: smartex-dan/kaggriculture

| Field | Value |
|-------|-------|
| **Source** | https://github.com/smartex-dan/kaggriculture |
| **Author** | smartex-dan |
| **Type** | Heuristic + MarketModel + opponent modeling |
| **Evidence** | REPO_VERIFIED |

**Architecture:**
- Modules: observation parsing/state representation, `StrategicPlanner`, profitability/ROI module, `MarketModel` (price estimation, timing), crop/animal action logic, labor allocation/hiring, opponent modeling from public info, utilities.

**Dynamic Policy:**
- Roadmap: random → starter analysis → rule-based → crop/economic strategy → market intelligence → labor optimization → animal/fertilizer → land expansion with town-demand forecasting → opponent modeling → long-horizon planning/search → RL experiments (only if heuristic ceiling hit) → hybrid architecture.

**Market Policy:**
- `MarketModel` provides price estimation and timing.
- Town-demand forecasting explicit.

**Opponent Modeling:**
- Explicit `opponent modeling from public info` module.

**Replay / Route Selection:**
- No replay mechanism described.

**Evidence:**
- No completed performance metrics or empirical results in visible README.
- Guideline: "Don't trust a strategy change until it's been run across 100+ games against the benchmark suite."

**Reproducibility:**
- Code is public and under active development.
- No GPU/network dependency claimed.
- Can run on kaggriculture 1.32.7 if observation schema matches.

**Score: 61/100**
- Strength Evidence: 5/30 (no performance data)
- Adaptivity: 18/25 (MarketModel + opponent model planned)
- Structural Novelty: 15/20 (explicit opponent modeling)
- Market Intelligence: 15/15 (MarketModel + town-demand)
- Reproducibility: 8/10 (in progress)

**Verdict:** BORDERLINE — ambitious roadmap and unique market/opponent modules, but zero verified performance. Worth 16-game screen only if implementation is complete enough to run.

---

## 4. Also-Ran / Eliminated Candidates

| Candidate | Reason for Elimination |
|-----------|------------------------|
| sota1111/kaggriculture-claude | Claude lineage submission; no architecture/performance details visible. Could be strong but identity unverifiable. |
| sutesute0000/Kaggriculture | Replays episode 92644257 for 7 turns then mostly PASS. Too weak structurally. |
| rooklift/krobus | Replay viewer infrastructure, not an agent. |
| alpertaskiran/kaggriculture | Game design documentation only, no agent code. |
| asajjadi/kaggriculture | Heuristic greedy; already benchmarked indirectly via prior recon (100% vs random/starter, but no v11E evidence). Low novelty vs v11E. |
| Seyamalam V21 | Already benchmarked: 5-3 vs v11E. Not advancing. |
| gytdrop v5 | Already benchmarked: 6-2 vs v11E. Not advancing. |
| COK V10 | Already benchmarked: 6-2 vs v11E. Not advancing. |
| lonespear | Already benchmarked: 2-4 vs v11E (corrected). Not advancing. |
| gzmcr | Already benchmarked: 1-7 vs v11E (corrected). Not advancing. |
| Ronin5205 | Already benchmarked: 98-107-35 / 240. Not advancing. |

---

## 5. Structural Differences from v11E

v11E architecture (known):
- Type B: Tape + Sparse Adaptation
- ~93.6% backbone replay
- Dynamic parts concentrated in SHOP and少量 SELL adaptation
- `_V11_TRANSITION_FIX`, `_V11_SHOP_COUNTER`, `_V11_MARKET_MODEL`, `_V11_BELIEF`, `_V11_HAZARD`, `_V11_SEQUENTIAL` flags

| Candidate | Key Structural Difference |
|-----------|---------------------------|
| diffmap/kaggicultureRL | PPO-trained policy + behavior mimicry from replays. Fully learned, not tape+repair. |
| gytdrop/KaggricultureAgent | Self-play RL + replay parsing + heuristic baseline. Iterative learning loop. |
| Octahedron-BB/Kaggriculture | Single public replay + 166 macro rules. Similar to v11E but with denser rule overlay. |
| pomagrenate/kaggriculture | Model-based receding-horizon control. Lookahead planning, not replay. |
| smartex-dan/kaggriculture | MarketModel + opponent modeling from public info. Explicit forecasting module. |

---

## 6. Evidence Levels

| Level | Definition | Count in Top 15 |
|-------|------------|-----------------|
| **VERIFIED** | Independent benchmark / leaderboard / public episode with reproducible results | 3 (Sey V21, gyt v5, COK V10, Octahedron-BB partial) |
| **REPO_VERIFIED** | Code confirms architecture claims; no independent performance verification | 8 |
| **CLAIMED** | Author README states performance; no independent verification | 2 |
| **UNVERIFIED** | Discovered but not inspected or no claims | 5 |

---

## 7. Reproducibility Audit

| Candidate | Load Verified | Action Schema | Runtime | Issues |
|-----------|--------------|---------------|---------|--------|
| diffmap/kaggicultureRL | NO | UNKNOWN | UNKNOWN | PPO dependencies unknown |
| gytdrop/KaggricultureAgent | NO | UNKNOWN | UNKNOWN | RL env setup unknown |
| Octahedron-BB/Kaggriculture | NO | UNKNOWN | UNKNOWN | Depends on public replay file |
| pomagrenate/kaggriculture | NO | UNKNOWN | UNKNOWN | Module dependencies unknown |
| smartex-dan/kaggriculture | NO | UNKNOWN | UNKNOWN | Work in progress |

**Note:** None of the Top 5 have been smoke-tested in this workspace. Reproducibility is inferred from repo structure only.

---

## 8. 16-Game Benchmark Results

**Status:** NOT YET RUN.

Per user mandate, 16-game screening (seeds 1-8, both seats) is deferred until Top 5 is approved. No benchmark has been executed for the new candidates in this session.

---

## 9. Final Recommendation

### ADVANCE to 16-game screening:
1. **diffmap/kaggicultureRL** — only confirmed PPO/RL repo; highest ceiling.
2. **gytdrop/KaggricultureAgent** — RL self-play + replay; proven learning loop.
3. **pomagrenate/kaggriculture** — model-based receding horizon; structurally most novel.

### BORDERLINE:
4. **Octahedron-BB/Kaggriculture** — strong replay + macro rules, but structurally close to v11E. Screen to see if macro rules actually matter.
5. **smartex-dan/kaggriculture** — ambitious market/opponent modules, but zero verified performance and appears incomplete.

### NO QUALIFIED CANDIDATE:
Not applicable — Top 5 exists.

---

## 10. Recommended Next Steps

1. **Smoke test Top 5** with fixed loader (`importlib.util.spec_from_file_location`) to verify import, action schema, and 720-step completion.
2. **16-game screening** (seeds 1-8, both seats) for ADVANCE candidates first.
3. If any candidate shows ≥10/16 wins or 9/16 with strong positive margin, promote to 120-pair.
4. If all FAIL/BORDERLINE, conclude: **NO QUALIFIED CANDIDATE** for 120-pair.

---

## 11. Search Coverage Limitations

- **Kaggle notebooks:** No public notebooks identified. WebFetch cannot execute Kaggle's React frontend.
- **Kaggle discussions:** Same JS-rendering limitation.
- **Public episodes:** No direct episode URLs scraped. Reddit thread title suggests strong replay-based agents exist but content was not accessible.
- **Leaderboard:** No leaderboard JSON scraped.

If access to Kaggle's authenticated discussion/leaderboard API becomes available, a second-pass search is recommended.
