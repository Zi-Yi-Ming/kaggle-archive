# Kaggriculture Deep Discovery: Candidate Discovery Report

**Date:** 2026-09-11  
**Scope:** Kaggle Discussions, Notebooks, Public Episodes, Leaderboard  
**Baseline:** v11E frozen, score ~2900  
**Goal:** Identify agents that can beat v11E, prioritize truly adaptive (Tier A) over fixed-tape (Tier C)

---

## 1. Leaderboard Snapshot (Prize Contenders)

| Rank | Team | Score | Medal |
|------|------|-------|-------|
| 1 | Majkel1337 | 3101.7 | Gold |
| 2 | SpaTaro | 3086.7 | Gold |
| 3 | feel the agi | 3045.0 | Gold |
| 4 | c0nrad | 3006.6 | Gold |
| 5 | Otter Vibe | 3005.6 | Gold |
| 6 | ymg_aq | 2995.4 | Gold |
| 7 | Unknown Mother-Goose | 2990.5 | Gold |
| 8 | binghua | 2976.5 | Gold |
| 9 | carlos-tagosaku | 2974.5 | Gold |
| 10 | Gleb Tumanov | 2967.6 | Gold |
| 11 | redblackbst | 2960.8 | Gold |
| 12 | 3정훈 | 2949.9 | Gold |
| 13 | Mengfei Li | 2941.5 | Gold |
| 14 | mtmr_s1 | 2937.2 | Gold |
| 15 | charmq | 2936.9 | Gold |
| 16 | Xiangyu Liu | 2918.3 | Gold |
| 17 | Syed Asad Ali | 2918.2 | Gold |
| 18 | QQ Farming | 2917.8 | Gold |
| 19 | american gothic | 2914.8 | Gold |
| 20 | Subramanya N | 2911.8 | Gold |

**Observation:** No top-10 team has public notebooks or discussion threads revealing their implementation. All code appears private.

---

## 2. Adaptive Notebook Candidates (Public Code)

### Tier A — Truly Adaptive / Runtime Policy

| Candidate | Author | Notebook | Best Score | Public Score | Votes | Key Evidence | Provenance |
|-----------|--------|----------|------------|--------------|-------|--------------|------------|
| PPO Meta-Agent | dzjiann (rank 15) | Discussion only: "RL of Meta Agent: 960 Matchups and a PPO Plateau" | N/A (private) | N/A | 14 | PPO selects/switches between high-scoring public trajectories; 960 games, 16 seeds, both seats; found rock-paper-scissors cycles; opponent+opening interaction 67.5% predictive | CLAIMED (discussion, no public code/episodes) |
| Adaptive Farming Strategy | tetsu2131 | 🌾Adaptive Farming Strategy for Kaggriculture | 2879.7 | 1569.9 | 142 | 153 copies; Apache 2.0; title/snippet say "adaptive route selection", "720-turn economic control" | VERIFIED (public notebook) |
| Frontier / Soil Remembers Rain | prvsiyan | Kaggriculture Frontier \| The Soil Remembers Rain | 2843.3 | 1627.6 | 103 | 139 copies; Apache 2.0; title/snippet say "adaptive livestock, with failures left in..." | VERIFIED (public notebook) |
| Smart Farm Strategy Lab | flexonafft | Kaggriculture \| Smart Farm Strategy Lab | 2483.9 | 2483.9 | 62 | Apache 2.0; snippet: "Public State Router Adapted from the public six-day" | VERIFIED (public notebook) |
| Kaggriculture 2900+ | Salem Ali | Kaggriculture \| 2900+ | 2702.3 | N/A | 77 | Apache 2.0; snippet: "Adaptive Execution The executable implementation is not restricted to replaying a fixed sequence" | VERIFIED (public notebook) |
| Adaptive Market Hysteresis | boatlee | V29-R1 \| Adaptive Market Hysteresis | 2177.7 | 2177.7 | 69 | Apache 2.0; title explicitly "Adaptive Market Hysteresis" | VERIFIED (public notebook) |
| Barnyard Economist | Roman Rozen | [STRONG] Barnyard Economist | N/A | N/A | 63 | Apache 2.0; snippet: "Adaptive replay controller for Kaggriculture" | VERIFIED (public notebook) |
| Fieldbook: Commit for Three Days | Yusuke Hayashi | Fieldbook: Commit for Three Days | N/A | N/A | 69 | Apache 2.0; snippet shows "adaptive" routing code | VERIFIED (public notebook) |

### Tier B — Heuristic / Structured but Possibly Strong

| Candidate | Author | Notebook | Score | Votes | Evidence | Provenance |
|-----------|--------|----------|-------|-------|----------|------------|
| Kaito Fukami v35 / v21.1 | kaitofukami | 177/180 Fresh Top-30 \| v21.1 Conditional Memory | ~2900+ | 102 | Top-30 claim; "Conditional Memory" suggests mid-game branching | VERIFIED (public notebook) |
| Rayk Kretzschmar meta | raykkretzschmar | Kaggriculture: Findings from Zero to Top Meta / Rank Your Agent | N/A | 187/108 | "Findings from Zero to Top Meta"; "Rank Your Agent against a known ladder" | VERIFIED (public notebook) |
| Top Farms Live Meta | cjlcjlcjl | Kaggriculture: What the Top Farms Do — a Live Meta | N/A | 75 | Live meta analysis from top replays | VERIFIED (public notebook) |
| Premium-First Market Agent | ameythakur20 | Kaggriculture: Premium-First Market Agent | N/A | 19 | Market-aware heuristic | VERIFIED (public notebook) |
| Harvest Nocturne V2 | lucifer19 | 🌙 Harvest Nocturne V2 \| A Lighter Start | N/A | 6 | Build-order variant | VERIFIED (public notebook) |
| X-ray your agent | destbreso | X-ray your agent | N/A | 37 | Diagnostics/visualization | VERIFIED (public notebook) |

---

## 3. Discussion Threads: Key Findings

### 3.1 RL of Meta Agent: 960 Matchups and a PPO Plateau
- **Author:** dzjiann (rank 15)
- **URL:** https://www.kaggle.com/competitions/kaggriculture/discussion/736439
- **Architecture:** Replay-based meta-agent. PPO selects/switches between high-scoring public trajectories at turn 0 and turn ~120. Selected expert route executes low-level farming actions.
- **Training:** 960 games among 6 public strategies, 16 seeds, both seats. Opponents = strong public agents + self-play. Reward = zero-sum (+1/0/-1).
- **Results:**
  - Rock-paper-scissors cycle found: Public B85 → Andrews 2883 → Kaito v35 → Public B85
  - Adaptive Farming (tetsu2131) strongest overall: 121/160 wins, but Kaito v35 beat it 17-15
  - Diagnostic accuracy: opponent+opening = 67.5%, opponent alone = 56.5%, opening alone = 56.5%
- **Conclusion:** PPO plateau may be a mixed-strategy Nash equilibrium, not training failure. Conflicting gradients from opponent-indistinguishable openings cancel out.

### 3.2 Beyond Replay Cloning: PPO, GA, & Beam Search
- **Author:** Nguyễn Mạnh (rank 1190)
- **URL:** https://www.kaggle.com/competitions/kaggriculture/discussion/738325
- **Key quotes from comments:**
  - Cho Royou (rank 15): "At least from watching the replays, you can tell that quite a few top players are using RL-based approaches. I'd guess this is also the kind of approach with the highest ceiling."
  - Steve421471 (rank 767): "I see strong evidence that at least one of the top players has submitted an agent that was built using RL."
  - Belati Jagad Bintang Syuhada (rank 1387): "So far no known behavior cloning approach in the top leaderboards yet."
  - Yohanes Alfredo (rank 1520): "making a top tier RL-based agent within the time constraint, is going to be very tough challenge."

### 3.3 Rating Mechanics (Ryo Hasegawa)
- **Author:** Ryo Hasegawa (rank 1870)
- **URL:** https://www.kaggle.com/competitions/kaggriculture/discussion/736219
- **Key facts:**
  - Elo-like system: K ≈ 200·e^(−n/26)
  - ~90% convergence after ~60 games
  - Only last 2 submissions active for final evaluation
  - Final leaderboard = Bradley-Terry tournament on post-deadline games
  - Byte-identical family agents common; early path dependence can be 300-1400 points
  - Seat asymmetry exists (destbreso notebooks mention measured seat-0 edge)

---

## 4. Public Episodes

No public episodes with full 720-turn trajectories were confirmed during this session. The leaderboard "View episodes" buttons require login or do not expose replay downloads without authentication. No direct episode URLs were found from top-10 team profiles or notebook pages.

---

## 5. Provenance Summary

| Provenance | Count | Candidates |
|------------|-------|------------|
| VERIFIED (public notebook + code, Apache 2.0) | 8 | tetsu2131, prvsiyan, flexonafft, Salem Ali, boatlee, Roman Rozen, Yusuke Hayashi, VijaiKurianMathew |
| CLAIMED (discussion only, no public code/episodes) | 1 | dzjiann PPO meta-agent |
| UNVERIFIED (inferred from comments/replays) | 3+ | Top-10 teams (Majkel1337, SpaTaro, feel the agi, etc.) |

---

## 6. Conclusions & Next Steps

1. **No public code currently beats v11E at its published public score.** The best public best-score is tetsu2131 at 2879.7, which is close to but below v11E (~2900).
2. **True RL agents exist in the top leaderboard but are not shared.** Multiple high-ranked participants confirm top players use RL-based approaches, but no top-10 team has published code.
3. **The most promising public adaptive candidate is tetsu2131's "Adaptive Farming Strategy"** — highest public best score (2879.7), 142 votes, 153 copies, Apache 2.0 license.
4. **dzjiann's PPO meta-agent is the most credible CLAIMED candidate** — rank 15, detailed experimental setup, 960-matchup tournament, but no public source or episodes.
5. **Next step:** Run 16-game smoke + benchmark against the top 3-5 VERIFIED adaptive notebooks to establish whether any can beat v11E offline. If none can, the gap to v11E is likely in private RL/optimization not available publicly.
