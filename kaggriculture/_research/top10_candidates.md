# Top 10 Candidates

**Baseline:** v11E frozen, score ~2900  
**Date:** 2026-09-11

---

## Ranking Methodology

Candidates are ranked by a composite score reflecting:
1. **Evidence strength** (public code/discussion, votes, copies)
2. **Reported score proximity to v11E** (~2900)
3. **Adaptivity tier** (Tier A = truly adaptive/runtime; Tier B = heuristic/structured)
4. **Provenance** (VERIFIED > CLAIMED > UNVERIFIED)

---

## Top 10

### 1. dzjiann PPO Meta-Agent
- **Tier:** A
- **Rank:** 15 (competition)
- **Source:** Discussion: "RL of Meta Agent: 960 Matchups and a PPO Plateau"
- **Score:** N/A (private)
- **Votes:** 14
- **Provenance:** CLAIMED
- **Evidence:** PPO selects/switches between high-scoring public trajectories. 960 games, 16 seeds, both seats. Found rock-paper-scissors cycles. Adaptive Farming strongest overall (121/160), but Kaito v35 beat it 17-15. Diagnostic: opponent+opening = 67.5% predictive.
- **Why #1:** Only confirmed PPO/meta-agent implementation with detailed experimental protocol. Rank 15 proves ladder effectiveness. Even if plateaued, it's the strongest publicly documented adaptive approach.
- **Benchmark readiness:** NOT READY (no public code or episodes). Would require contacting author for collaboration.

### 2. tetsu2131 Adaptive Farming Strategy
- **Tier:** A
- **Source:** Notebook: "Adaptive Farming Strategy for Kaggriculture"
- **Best Score:** 2879.7 (~rank 33)
- **Public Score:** 1569.9
- **Votes:** 142 | **Copies:** 153
- **Provenance:** VERIFIED
- **Evidence:** Apache 2.0 notebook. Title/snippet explicitly say "adaptive route selection", "720-turn economic control". 153 copies indicate broad community use.
- **Why #2:** Highest public best-score among adaptive notebooks. Strong community validation. Gap to v11E is ~20 points at best version.
- **Benchmark readiness:** READY (public notebook, executable).

### 3. prvsiyan Frontier / Soil Remembers Rain
- **Tier:** A
- **Source:** Notebook: "Kaggriculture Frontier | The Soil Remembers Rain"
- **Best Score:** 2843.3
- **Public Score:** 1627.6
- **Votes:** 103 | **Copies:** 139
- **Provenance:** VERIFIED
- **Evidence:** Apache 2.0 notebook. Title/snippet say "adaptive livestock, with failures left in..." — suggests memory/state system for livestock management.
- **Why #3:** Second-highest public adaptive best-score. High copies/votes. Novel livestock-adaptive angle may complement crop-focused agents.
- **Benchmark readiness:** READY (public notebook, executable).

### 4. Kaito Fukami v21.1 / v35
- **Tier:** B
- **Source:** Notebook: "177/180 Fresh Top-30 | v21.1 Conditional Memory"
- **Score:** ~2900+ (claimed top-30)
- **Votes:** 102
- **Provenance:** VERIFIED
- **Evidence:** Highly versioned series (v20, v21.1, v27, v29). "Conditional Memory" suggests mid-game branching. dzjiann's tournament found Kaito v35 beats Adaptive Farming 17-15.
- **Why #4:** Claimed top-30 ladder presence. Beats the strongest public adaptive agent (tetsu2131) head-to-head in dzjiann's tournament. Likely a fixed-tape with very strong conditional logic, but not "truly adaptive" in the runtime-policy sense.
- **Benchmark readiness:** READY (public notebook). High priority because it beats tetsu2131.

### 5. Salem Ali Kaggriculture 2900+
- **Tier:** A
- **Source:** Notebook: "Kaggriculture | 2900+"
- **Best Score:** 2702.3
- **Votes:** 77 | **Copies:** 71
- **Provenance:** VERIFIED
- **Evidence:** Apache 2.0. Snippet: "Adaptive Execution The executable implementation is not restricted to replaying a fixed sequence". Claims 2900+ capability.
- **Why #5:** Explicitly claims adaptive runtime execution. Score 2702.3 is below v11E but the gap may be due to public/private version split (like tetsu2131's 1569 vs 2879).
- **Benchmark readiness:** READY (public notebook).

### 6. flexonafft Smart Farm Strategy Lab
- **Tier:** A
- **Source:** Notebook: "Kaggriculture | Smart Farm Strategy Lab"
- **Score:** 2483.9
- **Votes:** 62 | **Copies:** 73
- **Provenance:** VERIFIED
- **Evidence:** Apache 2.0. Snippet: "Public State Router Adapted from the public six-day". Implies runtime state machine routing between precomputed policies.
- **Why #6:** "Public State Router" is a concrete adaptive mechanism. Score is modest but public/private split may exist.
- **Benchmark readiness:** READY (public notebook).

### 7. Roman Rozen [STRONG] Barnyard Economist
- **Tier:** A
- **Source:** Notebook: "[STRONG] Barnyard Economist"
- **Score:** N/A
- **Votes:** 63
- **Provenance:** VERIFIED
- **Evidence:** Apache 2.0. Snippet: "Adaptive replay controller for Kaggriculture". Implies runtime selection between replay modes.
- **Why #7:** "Adaptive replay controller" is a clear Tier A signal. No score visible but high votes indicate community interest.
- **Benchmark readiness:** READY (public notebook).

### 8. boatlee V29-R1 Adaptive Market Hysteresis
- **Tier:** A
- **Source:** Notebook: "V29-R1 | Adaptive Market Hysteresis"
- **Score:** 2177.7
- **Votes:** 69 | **Copies:** 72
- **Provenance:** VERIFIED
- **Evidence:** Apache 2.0. Title explicitly "Adaptive Market Hysteresis" — state-dependent market timing.
- **Why #8:** Explicit adaptive market focus. Score is low but may be a public/private split.
- **Benchmark readiness:** READY (public notebook).

### 9. Rayk Kretzschmar Findings from Zero to Top Meta
- **Tier:** B
- **Source:** Notebook: "Kaggriculture: Findings from Zero to Top Meta"
- **Score:** N/A
- **Votes:** 187
- **Provenance:** VERIFIED
- **Evidence:** 187 votes — highest among all notebooks found. Also authored "Rank Your Agent" (108 votes). Meta-analysis/reconstruction of top strategies.
- **Why #9:** Most popular notebook in search results. Likely contains reconstructions of top agents that may be strong baselines even if not adaptive.
- **Benchmark readiness:** READY (public notebook). Good for baseline comparison.

### 10. Yusuke Hayashi Fieldbook: Commit for Three Days
- **Tier:** B
- **Source:** Notebook: "Fieldbook: Commit for Three Days"
- **Score:** N/A
- **Votes:** 69
- **Provenance:** VERIFIED
- **Evidence:** Apache 2.0. Snippet shows `if fieldbook_seat == 0 else [fixed, adaptive]` routing. Seat-aware heuristic with some adaptive branching.
- **Why #10:** Seat-adaptive routing is a concrete mechanism. 69 votes indicate community validation.
- **Benchmark readiness:** READY (public notebook).

---

## Also Notable (Not in Top 10)

| Candidate | Reason Not Ranked |
|-----------|-------------------|
| Nguyễn Mạnh PPO/GA/Beam Search | No public code; rank 1190; PPO failed to learn |
| Cho Royou / Steve421471 (comments) | No public code; only discussion comments |
| Kaito Fukami v27/v29 series | Ranked above as #4 (v21.1 representative) |
| destbreso X-ray | Diagnostics only, not an agent |
| VijaiKurianMathew EDA Framework | Rank 2652, beginner tutorial |

---

## Key Insight: The Public/Private Score Gap

Multiple adaptive notebooks show a massive gap between public score and best score:
- tetsu2131: public 1569.9 vs best 2879.7
- prvsiyan: public 1627.6 vs best 2843.3

This pattern suggests authors deliberately publish weaker public versions while keeping stronger private versions for the leaderboard. The private versions may be the ones that actually compete with v11E. **Any benchmark against public versions must account for this gap.**
