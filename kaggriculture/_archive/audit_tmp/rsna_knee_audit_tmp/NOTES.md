# Kaggriculture Open-Source Audit — Working Notes (2026-09-06)

Audit workspace: _audit_tmp/repoA (Seyamalam), repoB (lonespear), repoC (COK).

## Repo A — Seyamalam/Kaggriculture (repoA)
- HEAD 8b8c421, 46 commits. Current = V21 (capital latch on V18/C20).
- 2053.6 claim: LEADERBOARD (reported, verified internally consistent): submission 55260568 (commit 69c64ae, SHA 30683478...), 27 public episodes 24-3, rating 600 -> 2053.6 (per-match table 696→1014.9→...→1804.1→2053.6). V18 opened 24-3.
- V21 = exact V18 until step 577, one-time latch: late_abstain = opponent_money - own_money <= -5000 (disables only the added recovery sweep). Evidence: historical public55 corpus 94→100 wins (+927.8 mean), live15 27→29, frozen top20 31→31 (38/40 exact V18); 100 paired seeds vs exact V18: 2-1-97 ties (+6.98 margin). BENCHMARK (open-loop replay corpus) + SELF-PLAY (vs exact V18 = same family, high tie rate).
- V20 late abstain (global cutoff step 577) REJECTED: rescued weak-supply opponents but removed denial vs strong supply (26 traces 20/0/32, -1235.8 mean). Strong conditional lesson: global late cutoffs harm strong-supply matchups.
- Key mechanisms (main.py 4899 lines): closed-loop farm route (8 cows 6 sheep, three quadrants, 12 hands — attributed public V18/C20), market interference (_apply_market_interference, _safe_wheat_squeeze), expert selection (_expert_weights, _blended_targets), opponent pipeline (_opponent_pipeline), version ladder v11-v18 market modes + "senkin" actions, v17 market ranker, v18 closed-loop market.
- Discipline: per-version promotion gates, rejected experiments recorded (v19 wool floor REJECTED, v10 market ranker REJECTED, v2 ablations rejected), replay-loss attribution harness, SHA-pinned artifacts. Engine 1.32.4.

## Repo B — lonespear/kaggriculture (repoB)
- HEAD 774b260, 29 commits. v1-v23 ladder; current main.py = main_v18.py (submitted id 55309483).
- Why self-play strong but online 921 (evidence: README + commits): internal league 48-2 (SELF-PLAY); online 692→1000→settled 921 as matchmaking found stronger opponents; "last ten episodes opponents averaged 117,920 vs our 103,979 — outscored at this band" (commit e060c18). Ladder Elo median inflated 670→2838 in 6 days (daily_meta.py).
- v23 copied winners' shape (3 quadrants, 44 strawberry, 14 hands) and lost 0-40: cannot pay ~$22,600 extra hire cost — SHAPE WITHOUT ECONOMIC BASE FAILS.
- Config: COW_MAX 8, STRAWBERRY_MAX 24, WHEAT_TILES 10, MAX_QUADRANTS 2, MAX_HANDS 11 (mirror/league-tested). FERTILIZE_PRI raced flat; shed fertilizer pickup removal worse (-2302).
- OPEN THREAD (untested at handoff): FeedMeSeymour issued BUY_PRODUCT:FERTILIZER 620 — fertilizer floors at $1, doubles crop yield; every acreage ceiling may have been measured on half-yield crops. Decisive test: action_trace FERTILIZE vs COLLECT_FERTILIZER count (actions vs supply binding).
- Known weakness: milk-crash matchups (~1 in 7), town drain ~26/day vs 20 cows ~30/day.
- Tools: h2h.py (seat-swapped league), par_sweep.py (parallel sweep, seed-variance warning: one config ranged 54k-68k), market_trace.py, daily_meta.py (meta tracker), action_trace.py (phase-split action histograms).

## Repo C — COK-ZhangZiliang/Kaggriculture (repoC)
- HEAD 7ef67ea, 32 commits. V10 = fail-closed opening recovery on V9 (submission COMPLETE, SHA 56831f3c...).
- Strategy: step-72 public-signature recovery gate (opponent 1 cow/4 sheep/5 wheat/4-5 melon + lower cash + shop BAKERY/PIZZA) -> frozen V5 low 10C/4S route; Yarn-by-168 -> high 6C/12S route; else V9 five-route policy. Sticky/seat-isolated/reset-safe. Step 718 projected-shed terminal liquidation.
- Evidence: 597-game calibrated public replay corpora (V7 control 333, V8 control 177, latest V9 87): V9→V10 W/T/L 336/3/258 → 339/3/255, 7 improved, 590 identical, 0 regressed; mean margin +1171.9→+1266.0. BENCHMARK (open-loop replay corpus, calibrated public replays). 77 tests.
- Mechanisms: _meta_* (clone profile/signature distance -> expert route selection), _front_run/_town_demand_now (shared-market timing), _weed_repair_action (visible-state repair), _reconcile_scheduled_cows, executable SELL ranking, retry-safe action cache. Deterministic public-state only; explicitly no replay lookup/identity/seed routing.

## New discoveries (task 5, GitHub search 307 repos + web search)
- diffmap/kaggicultureRL: RL policy-training system (behavior mimicry from daily leaderboard replays -> single-seat RL -> dual-seat RL, PPO). ARCHITECTURE TOOL, no rating evidence seen. EVIDENCE: unknown. Possible complement: RL policy candidates for market execution (research-only).
- deepeshumrao/kaggriculture-agent: Vibe Coding capstone, rule-based FarmBrain, contract-first local sim. Uses premium-first market reorder (MELON/MILK/WOOL/STRAWBERRY first) + _front_run pre-empting town consumption — same CONCEPT as our Fix-A (which failed online). No rating evidence. EVIDENCE: README_CLAIM/INFERENCE only. Not a transplant source.
- rooklift/krobus: Kaggriculture replay viewer (JS tool, not an agent).
- raykkretzschmar/kaggriculture-reference-agents (Kaggle dataset): tiers 0-9 reference agents — this is the source of OUR reference_agents/ pool (broker_bea/ledger_lena/slotter_silas/closer_cleo...). agents_manifest.csv has measured bank per agent. Context/benchmark value only.
- Kaggle discussion deep-dive: not completed (auth-gated); covered via web search only.

## gh search 补充 (2026-09-06, gh CLI authed)
- CDrookieDc/kaggriculture (1 star, 2026-08-21): wheat + melon + GOOSE economy (sector-owner controller). README: goose core (~28 coops, 2 eggs/day/tile, free ~$90 fertilizer/day), wheat backbone (5-day cycles, age-4 harvest), melon burst (8 tiles, 2 cycles ~$6-7k each), AVOIDS cows/sheep/strawberry/tomato/carrot (market curves crash to $1 after ~100-150 units). Genuinely different farm route vs v11E/8cow-6sheep. EVIDENCE: README_CLAIM/INFERENCE only (no rating/benchmark seen). Worth noting as farm-route alternative; transplant risk HIGH (route change, not isolated mechanism).
- bravefe/Kaggriculture (2 stars): team-workflow repo (README = git/PR instructions), NOT an agent — excluded.
- gytdrop/KaggricultureAgent (2 stars): RL self-training, aspirational ("aim to score 2 lakhs"), no evidence — excluded.
- Others (Alloysj, harryii-eng, sidhulyalkar, kyconf, Vikaspal505, JaydonJP, VladimirCro, etc.): low-star capstone/basic rule agents, no rating/benchmark evidence — recorded as EVIDENCE: unknown, not transplant sources.
- 307 total repos match "kaggriculture"; most are tools/viewers/capstones. High-value audit set = A/B/C + diffmap (RL system).

## Cross-cutting lessons
1. All three repos' strongest internal evidence is open-loop replay corpus (BENCHMARK) or self-play/league (SELF-PLAY BIAS) — none has independent opponent evidence matching our v11E's 942.
2. Ladder Elo inflated fast (670→2838 in 6 days) — raw Elo numbers are era-dependent; "2053.6" and "921" are snapshots, not stable truths.
3. Common mechanisms across A/B/C: market-front-run (sell before town consumption), premium-first ordering (A: interference; C: _front_run; deepeshumrao: reorder), opponent public-state estimation (A/B/C), route/expert selection by public signature (A: expert weights; C: clone-profile gate), late-game conditional (A: capital latch 577; B: endgame liquidation v16), fail-closed recovery (C), fertilizer arbitrage (B open thread — NOT in v11E).
4. v11E (942) has: ProductBelief/hazard/first-mover hazard/expected opponent sell (opponent model), sequential beam (liquidity-aware sell ordering), v12 comparison, Fix-A (rejected online).

## 7-layer fingerprints (task 6)

### Repo B (lonespear v18, 891-line rule-based)
- L1 Farm: 8 cow + 6 sheep + STRAWBERRY_MAX 24 + WHEAT_TILES 10 + MAX_QUADRANTS 2; objective = final coins, herd-before-crops capital priority (CODE).
- L2 Labor: _assign — standing-on-work pass (unit on ready tile acts free, never dragged off), shed logistics (feed/animals/fert pickup with small WHEAT_CARRY to avoid shed overflow), ENDGAME_DUMP_DAY thresholds collapse to 1 (CODE; league 48-2 SELF-PLAY).
- L3 Capital: explicit cash-reserve formula reserve = 300 + wheat_px × (animals+1) × feed_days (price-gated runway, replay 90323915 starvation lesson), feed-first ordering, land last, endgame fill-seed (wheat→carrot by days_left) (CODE).
- L4 Market: price-threshold drip selling (TOWN_DEMANDED DRIP_LIMIT 6/2), WHEAT sellable = qty − feed-reserve, FERTILIZER surplus-only, endgame dump all day≥29; NOT per-unit sequential-pricing aware; NO market-list slot logic (CODE).
- L5 Opponent: NONE (own-state only) (CODE).
- L6: Rule-based adaptive (B).
- L7 Late: ENDGAME_DUMP_DAY full liquidation, endgame fill-seed, terminal conditions (v15/v16, league 59-1 SELF-PLAY); no opponent-gap conditional (CODE).
- Open thread: FERTILIZER arbitrage (buy $1 fertilizer, doubles crop yield) UNTESTED — action_trace decisive measurement not run (README_CLAIM).

### Repo A (Seyamalam v21, 4899-line)
- L1 Farm: attributed public V18/C20 closed-loop route — 8 cow + 6 sheep, 3 quadrants, 12 hands (README_CLAIM + THIRD_PARTY attribution; CODE in main.py route).
- L2 Labor: deterministic task assignment (plant/water/harvest/weed/shed) (CODE).
- L3 Capital: cash-runway-aware daily hiring, staged land (CODE).
- L4 Market: market-interference overlay — sell-first reordering by _interference_value = opponent_exposure × price (denial sequencing, exposure-targeted NOT blanket), WHEAT order preserved, _safe_wheat_squeeze feed-denial attack (gated, disabled by default), version ladder v13-v18 market modes (concentration gate, daily lane lock, ranker, closed-loop + senkin), demand-matched premium sales first turn after town consumption (CODE; v18 24-3 LEADERBOARD-entangled).
- L5 Opponent: _opponent_pipeline (public farm → supply estimates), expert selection _expert_weights/_blended_targets keyed on public supply, market modes with daily hysteresis (CODE).
- L6: Rule-based + expert selection (E/F hybrid).
- L7 Late: V21 capital latch — step 577 one-time opponent_money − own_money ≤ −5000 → disable recovery sweep (conditional late policy; corpus 94→100 wins BENCHMARK + 100 paired seeds SELF-PLAY 2-1-97); V20 global late abstain REJECTED (hurts strong-supply); auto liquidation (CODE).

### Repo C (COK v10, 1673-line)
- L1 Farm: five-route + frozen V5 low 10C/4S / high 6C/12S, selected by step-72 public signature + Yarn-by-168 gate (CODE).
- L2 Labor: _align_hands, _reconcile_scheduled_cows, _weed_repair_action/_clear_passive_weeds (visible-state repair) (CODE).
- L3 Capital: _clip_seed_surplus, premium repayment, capital-order priority (CODE).
- L4 Market: _front_run sells exactly 1 step before town-consumption ticks (demand model _town_demand_now, targets from own action tape _future_quantity, repay mechanism prevents double-sell), executable SELL ranking, step-718 projected-shed top-up liquidation within 10-cap (CODE; 597-game corpus V9→V10 336→339 W, 0 regress BENCHMARK).
- L5 Opponent: _meta_* clone profile/signature distance → route selection; _meta_observe_h4 market-delta opponent-sell inference (CODE).
- L6: Rule-based + signature route selection (B/E hybrid).
- L7 Late: step-718 conservative top-up liquidation; no opponent-gap conditional (CODE).

### v11E (ours, 1531-line)
- L1: closer_cleo lineage 8cow/6sheep farm, MELON schedule, WHEAT cap (CODE).
- L2: base scheduler farmer+hands shed logistics (CODE).
- L3: _cash_needed (seed/animals/land cost model) (CODE).
- L4: _v10_priority (revenue − price_damage + cash_unlock + opp_factor), _v11_beam_order sequential liquidity evaluator (sells fund buys), _sell_priority impact-slot ranking, reserve-price selling; Fix-A premium-first REJECTED online (LEADERBOARD -50 vs v11).
- L5: ProductBelief (mean/var/low/high, floor/drop/carry, hazards, first-mover), expected_opponent_market_sell, _OPP market-delta observer — STRONGEST opponent model of the four (CODE).
- L6: Rule-based + beam search (C/D hybrid).
- L7: _terminal_action 717+, _terminal_liquidation 680+, step-based; no opponent-gap conditional (CODE).

## v11E Differential (task 7)

### Public agents have X, v11E does NOT have X
- A1 exposure-targeted market denial sort: _interference_value = opp_exposure × price, reorders sells by opponent supply (NOT blanket premium-first; Fix-A was blanket and failed) — v11E has opp_factor (small weight) but no exposure-sorted market list (CODE; v18-open evidence LEADERBOARD-entangled).
- A2 safe wheat squeeze: gated feed-denial (opp animals ≥10, opp cash ≤250, wheat px ≤30, own shed ≥2×animals; DISABLED by default in A too) — v11E has no denial attacks (CODE).
- A3 market-expert selection with daily hysteresis (v13-v18 modes, lane lock, ranker) — v11E has belief but no expert switching (CODE).
- A4 opponent-gap conditional late policy (V21 latch at 577: opp − own ≤ −5000 → stop risky sweeps; v11E has NO opponent-gap late policy) (CODE; corpus BENCHMARK + live15 27→29 + SELF-PLAY 100 seeds).
- B1 standing-on-work labor pass (act free when standing on ready tile; never dragged to marginal far task) — v11E scheduler walks to nearest target; likely lacks (CODE; league SELF-PLAY only).
- B2 price-gated cash reserve for animal buys: reserve = 300 + wheat_px × (animals+1) × feed_days — v11E _cash_needed is flat cost, not feed-price-runway (CODE; replay starvation lesson).
- B3 endgame fill-seed: buy short-horizon WHEAT/CARROT seed to fill freed strawberry tiles near end — v11E terminal is liquidation-only (CODE).
- B5 fertilizer arbitrage open thread: buy $1-floor FERTILIZER → doubles crop yield; UNTESTED by B (decisive action_trace measurement not run) — v11E sells surplus fertilizer; unknown if buys (README_CLAIM/INFERENCE).
- C2 clone-profile → ROUTE selection (switch farm route on opponent build) — v11E uses clone profile only to activate front-run, no route switching (CODE).
- C4 step-718 conservative top-up liquidation (project shed, preserve existing SELLs, 10-cap aware) — v11E _terminal_liquidation sells everything 680+ (coarser) (CODE).

### v11E has Y, public agents do NOT have Y
- Sequential beam (liquidity-aware sell sequencing, sells fund buys) — none of A/B/C has beam search (v11/v12 gap = 67 Elo ONLINE, LEADERBOARD).
- ProductBelief/hazard/first-mover hazard/expected opponent market sell — strongest opponent model of the four (B has NONE).
- Fixed-RNG heterogeneous benchmark discipline (community pool + synthetic) — public repos rely on league/corpus.

## Self-play bias audit (task 7)
- Repo A: 2053.6 = LEADERBOARD (27 real matches, 24-3, reported table) but era-inflated ladder; V21 delta evidence = BENCHMARK (open-loop corpus 94→100) + SELF-PLAY (100 paired seeds vs exact V18, 2-1-97 ties — same family, high tie rate) + live15 30 seats 27→29 (real matches, 2 changed — weakest-bias slice). Moderate bias; V18→V21 is same-family improvement.
- Repo B: internal league 48-2 / version gates 40-0, 59-1 = PURE SELF-PLAY/mirror; online 921 (13-11, 24 episodes) = LEADERBOARD. The 48-2→921 gap IS the self-play-bias lesson (league dominance ≠ ladder; outscored 117,920 vs 103,979 at band). B flags seed variance (54k-68k) and fine-tuning noise itself (par_sweep docstring).
- Repo C: 597-game corpus = open-loop REPLAY (frozen public action traces — deterministic, non-adaptive; semi-independent since traces are real public episodes). V10 delta tiny (7 improved / 590 identical) — weak signal. No live ladder evidence.
- v11E: online 942 Elo = strongest independent evidence of the four; local fixed-RNG heterogeneous pool (community agents) + the Fix-A lesson (local +228 didn't transfer online — SELF-PLAY/replay bias confirmed empirically by our own Fix-A experience).

## Transplant candidates + Priority Score (task 8)
Score = Evidence × Gain × Compat × Testability / Risk (each 0-5).

| # | Mechanism | Source | Evid | Gain | Compat | Risk | Test | Score |
|---|---|---|---|---|---|---|---|---|
| 1 | Opponent-gap conditional late policy (V21 capital-latch concept: at 577, opp−own ≤ −5000 → stop risky late actions) | A | 3 | 2 | 3 | 3 | 5 | 30 |
| 2 | Endgame fill-seed (buy short-horizon WHEAT/CARROT seed for freed late tiles) | B | 2 | 2 | 3 | 2 | 4 | 24 |
| 3 | Conservative step-718 top-up liquidation (project shed, preserve existing SELLs, 10-cap aware) | C | 2 | 1 | 3 | 1 | 4 | 24 |
| 4 | Exposure-targeted market denial sort (interference_value = opp_exposure × price; targeted, NOT blanket) | A | 2 | 2 | 3 | 3 | 5 | 20 |
| 5 | Fertilizer arbitrage (buy $1-floor FERTILIZER → double crop yield; v11E lineage had v3.4 MELON-window buy) | B(open thread) | 1 | 4 | 3 | 3 | 5 | 20 |
| 6 | Standing-on-work labor pass (act free when on ready tile) | B | 2 | 2 | 2 | 2 | 4 | 16 |
| 7 | Price-gated cash reserve for animal buys (300 + wheat_px × (animals+1) × feed_days) | B | 2 | 2 | 2 | 2 | 4 | 16 |
| 8 | Market-expert selection with daily hysteresis (v13-v18 modes) | A | 2 | 2 | 2 | 3 | 4 | 11 |
| 9 | Clone-profile → farm route selection | C | 2 | 2 | 1 | 4 | 4 | 4 |
| 10 | Safe wheat squeeze (feed denial) | A | 0* | 2 | 2 | 4 | 4 | 0 |

*A2 was DISABLED by default in repo A itself — author judged it not worth enabling; evidence of effectiveness = none. Excluded.

Scoring notes (honest):
- All candidates carry SELF-PLAY/replay bias risk (Fix-A lesson: local +228 did not transfer online). Any transplant MUST go through fixed-RNG heterogeneous-pool paired bench, not self-play.
- #1 (A4) has the strongest mixed evidence (real-match live15 slice) and is cheap/conditional; adapts to v11E by gating late front-run/liquidation aggressiveness on opponent gap (v11E has no sweep to disable — concept, not literal port).
- #5 (fertilizer) has the largest ceiling (all crops double yield; B claims every acreage ceiling was measured on half-yield crops) but zero direct evidence — needs B's own decisive measurement first (FERTILIZE vs COLLECT counts: is supply or ACTIONS binding?).
- #3 (C4) is cheap and low-risk but low-gain; user's own finding says terminal conversion is not a lever — marked accordingly.
- #2 (B3) touches late production (not conversion) — distinct from the excluded terminal-conversion direction.
- Market-list reorders (#1-related, #4) carry elevated risk on v11E post-Fix-A; exposure-targeted denial is mechanically different from blanket premium-first but must be benchmarked on the heterogeneous pool first.

## Mechanism Differential Audit — Seyamalam V18 深拆 (task 2, 2026-09-06)

关键发现（CODE，main.py DEFAULT_STRATEGY L74-205 + configure_strategy L2400/2592 确认提交版用默认值）：
- **repoA 没有 beam**——用户"post-beam"框架与实际代码不符（discrepancy 记录）。实际 V18 市场管线 = v18 closed-loop board/market 专家选择（L3399-3480，每日 state-distance 到 prototype + seat bias + stay_bonus，market 专家含 SELL timing/quantity/BUY/HIRE）→ v17 ranker（L3307-3348，53→16→1 离线训练 pairwise 排名，仅重排 free slot 内非 WHEAT SELL，permutation-only，min_confidence 0.95 门）→ _apply_market_interference（L2720-2752）→ _safe_wheat_squeeze（L2677，默认关）。
- **exposure×price 排序存在但默认关闭**：interference_targeted_sort=False（L193）；interference_sell_first=True（L192，稳定 sell-first：SELL 全部提到 BUY 前、内部保序）+ preserve_wheat_order=True + collision_only=False。_interference_value = exposure×price×min(qty,10)（L2665-2674）只在 targeted_sort=True 时启用。提交的 V18 实际行为 ≠ "exposure×price 排序"。
- v17 ranker = "constrained local reorder"（只能重排既有非 WHEAT SELL 于原 free slot，不改 quantity/timing/BUY），最接近用户概念 B，但信号是离线训练的 pairwise 神经网络概率，非 exposure×price。
- 14 问要点（伪代码/结论见最终报告）：输入 = closed-loop 专家产出的完整 market list；exposure = _opponent_pipeline（对手公开农场供给估计）；price = obs 当前市场价；阈值 = interference_min_exposure 0.5（仅 collision_only 时用）、v17 min_confidence 0.95；WHEAT 保留 = executor cash-flow 循环的一部分（L186-189 注释：wheat buy/sell 是现金循环，必须不动）；可重排产品 = v17 ranker 的 _V17_MARKET_MODEL["products"]（非 WHEAT）；quantity/timing/BUY 不变（v17 permutation-only）；v18 closed-loop 专家本身改变 SELL timing/quantity/BUY/HIRE（但与 v11E 的 beam 是不同层）；fallback = min_confidence 门不足则保序；slot 依赖 = ranker 只能在"原 free slot"内置换（slot 数不变）；耦合 = v18 专家与完整 route/board 强耦合（不能独立移植）。
- 类别预判：v17 ranker/exposure sort（off by default）→ Category B/D（v11E beam 已做 liquidity+opp_factor 排序，且默认未启用无线上证据）；v18 closed-loop 专家选择 → Category D（离线训练权重、与全套 route 耦合、无独立证据）。

## Mechanism Differential Audit — lonespear fill-seed 深拆 (task 3, 2026-09-06)

- 代码：main_v18.py L758-773（_market_orders 内）。触发：days_left_m = 30 − day ≤ ENDGAME_FILL_FROM 且 money > 400 且 spare tiles > 0；种子选择按成熟周期：days_left > WHEAT.maxday(4) → 买 WHEAT 种（≤12，spare − 已有种子），elif days_left > CARROT.maxday(3) → 买 CARROT 种（≤12）。需确认 ENDGAME_FILL_FROM 与 CROP_INFO.maxday 具体值（见下）。
- 机制性质：纯 BUY_SEED（市场订单层）+ 后续 PLANT/收获走既有调度器；不改任何既有订单/产量/劳动力分配。收益来源 = additional production（把草莓衰败/收获后腾出的空格换成短周期作物，晚生产），非 capital/liquidation。
- 与 v11E beam 冲突评估：无直接冲突（只加 BUY_SEED 订单；但会挤占 market list 槽位与现金）。

（CROP_INFO/ENDGAME_FILL_FROM 具体值待补读）→ 已补：ENDGAME_FILL_FROM=6（L154）、CROP_INFO maxday：WHEAT 4/CARROT 3/MELON 10/TOMATO 11/STRAWBERRY 16（L41-47）。两条路径：L763-773（_market_orders 买种：days_left≤6 且 money>400 且 spare>0；days_left>4→WHEAT 种 ≤12，elif >3→CARROT 种 ≤12，want=spare−已有种子）+ L489-492（种植侧同条件排程）。ENDGAME_DUMP_DAY=28 全清仓——晚产作物喂给终局清算。容量考量：只填 empty 格（不替代其他作物）、按 spare−已持种限量。现金考量：>400 门槛。v11E 等效：基础调度器持续种 WHEAT，但"草莓衰败后填空 + 按成熟周期买晚种"未见明确实现（Category A 或 D，待静态比对）。

## Mechanism Differential Audit — Top-3 Category E 候选 (task 6, 2026-09-06)

**E1 — Standing-on-work labor pass（站立即做工）**
- Source: lonespear v18, main_v18.py `_assign` L576+（"Standing-on-work pass"注释块）
- Exact impl: 任务分配时，若单位已站在需要动作的格上，直接免费执行（不消耗移动）；否则才按优先级把任务派给最近空闲单位——避免"站在就绪工作上却被拖去远处次要任务，两件都白走路"（B 的 v13 commit: "standing-on-work assignment (40-0)"）
- Why v11E lacks: v11E 调度器（closer_cleo 家族 _plan_sells/_move 逻辑）按"最近目标"走路，未见站在就绪格免移动的 pass
- Expected mechanism: 减少移动回合 → 腾出劳动力给浇水/收获/除草（24回合/天硬墙下每个省下的移动都是产出）
- Interaction risk: 中——动 scheduler（但不动 farmer 主路线/不动 BUY/不动 beam；可只做 hands 的站位优化，隔离度高）
- Evidence: CODE + league(SELF-PLAY) → 证据强度低但机制假设清晰可测
- Priority: 3（排在 E2/E3 后——调度器改动面大，需先静态确认 v11E 是否已隐含此行为）

**E2 — Endgame fill-seed（末局填空种植）**
- Source: lonespear v18, main_v18.py L758-773（_market_orders）+ L489-492（种植侧）
- Exact impl: days_left=30−day ≤ 6 且 money>400 且 spare tiles>0 → 若 days_left>WHEAT.maxday(4) 买 WHEAT 种 ≤12（want=spare−已持种）；elif days_left>CARROT.maxday(3) 买 CARROT 种 ≤12。只填 empty 格、按成熟周期选种、限量
- Why v11E lacks: v11E 基础调度器持续种 WHEAT 但无"草莓衰败后按剩余天数买短周期种填空"的显式逻辑（需静态比对确认——若已隐含则降级 A）
- Expected mechanism: additional production（末局空格转晚产，喂给终局清算）
- Interaction risk: 低——只加 BUY_SEED 市场订单（挤占 market list 槽位与现金，不触 beam/farm/scheduler）
- Evidence: CODE + league(SELF-PLAY) + v15 "endgame tile fill 52-8"（SELF-PLAY）
- Priority: 1（改动面最小、隔离度最高、机制可解释）

**E3 — Price-gated cash reserve（价格门控现金储备）**
- Source: lonespear v18, main_v18.py L775-797
- Exact impl: 买动物前 reserve = 300 + wheat_px × (n_animals+1) × ANIMAL_BUY_FEED_DAYS——储备随当前麦价缩放（麦价高时收紧买动物）；B 的 replay 90323915 断粮教训（每分钱都买牲畜 → 第 6 天 2 牛→0 牛）
- Why v11E lacks: v11E 的 _cash_needed 是平值成本模型（种子/动物/土地固定预留），未按当前喂料价缩放
- Expected mechanism: 高麦价局避免牲畜断粮逃逸（动物是 $400-500 资产，连续 2 天不喂逃逸）；低麦价局释放资金
- Interaction risk: 中——动 BUY 门控（v11E 的 BUY 来自 base tape/beam 资金流；需确认 v11E 是否已有等价防护）
- Evidence: CODE + INFERENCE（断粮 replay 教训）
- Priority: 2

候选池结论：三候选全部来自 lonespear（Seyamalam/COK 无 Category E——前者 market 机制被 beam 支配或默认关闭/强耦合，后者抽象已被 v11E 覆盖或架构不相容）。exposure×price 排序 = Category B/D（默认关、被 beam opp_factor 支配），不构成 Exp 3A 前提。

| 层 | 机制 | Repo/Ver | 代码位置 | 作用 | v11E 等效 | 类别 | 证据 | 交互风险 |
|---|---|---|---|---|---|---|---|---|
| Market | v17 pairwise ranker | A/V17 | L3307-3348 | 仅重排 free slot 内非 WHEAT SELL（permutation-only，min_conf 0.95） | beam 排序（更原则化、线上验证） | B | CODE+LEADERBOARD(包裹) | 低（若独立跑） |
| Market | sell-first 稳定重排 | A/V18 | L2720-2752 | SELL 全部提前到 BUY 前、内部保序、WHEAT 保留 | beam 已做排序（子集） | B | CODE | 低 |
| Market | exposure×price 定向排序 | A/V18 | L2665-2674 | 按对手暴露度×价格排序 | beam opp_factor(0.12)+Belief | B/D | CODE（**默认关**，无线上证据） | 中（Fix-A 教训） |
| Market | closed-loop market 专家 | A/V18 | L3399-3480 | 每日按 state-distance+seat bias 选专家，改 SELL timing/qty/BUY/HIRE | 无（belief 有、专家切换无） | D/C | CODE+LEADERBOARD(强耦合) | 高（动 beam 冻结面） |
| Market | price-threshold drip | B/V18 | L846-852 | 镇需求商品按阈值+DRIP_LIMIT 限量卖 | reserve-price + expected-sell | B | CODE | 低 |
| Market | feed-reserve WHEAT | B/V18 | L835-839 | 卖量 = 库存 − 喂料储备（末局归 0） | 有喂料核算 | A | CODE | 低 |
| Market | front_run+repay | C/V10 | L399-433 | 镇消费前 1 步卖+防双卖 repay | front_run 同族（无 repay 细化） | A/B | CODE+BENCHMARK(corpus) | 低 |
| Market | step-718 保守补卖 | C/V10 | agent() 末段 | 投影 shed、保留既有 SELL、10-cap 补顶 | 终局清算 680+（更粗） | B | CODE+BENCHMARK(弱) | 低（terminal 非杠杆） |
| Farm | closed-loop route 8C6S | A/V18 | DEFAULT_STRATEGY | 3 象限 13 手固定路线 | 同家族 8C6S | A | CODE | — |
| Farm | route 8C6S+24S | B/V18 | 常量区 | 2 象限 11 手 | 同家族 | A | CODE | — |
| Farm | 签名→frozen tape 选路 | C/V10 | L1255 | 按对手公开态+镇商店选路线 tape | 无路线切换 | C/D | CODE+BENCHMARK(半独立弱) | 高（农场级） |
| Labor | standing-on-work pass | B/V18 | _assign L576+ | 站就绪格免费行动，不被拖走 | 无（调度器走到最近目标） | **E** | CODE+league(SELF-PLAY) | 中（调度器） |
| Labor | 小携带量防 shed 溢出 | B/V18 | L557-564 | WHEAT_CARRY 限量 | 有类似 | A | CODE | 低 |
| Labor | visible-state repair | C/V10 | L215/299 | 杂草/奶牛对齐修复 | 有杂草处理 | A | CODE | 低 |
| Capital | price-gated cash reserve | B/V18 | L775-797 | reserve=300+麦价×(动物+1)×喂养天 | _cash_needed 平值 | **E** | CODE+INFERENCE(断粮 replay) | 中（BUY 门控） |
| Capital | adaptive capital priority | A/V18 | L182-185 | 对手自适应资本优先级 | 无 | D | CODE（默认关） | 中 |
| Capital | V21 capital latch | A/V21 | v21 report | step577 对手领先≥5000 停 recovery sweep | 无 | D（EXP-2 LOW_COVERAGE→future only） | BENCHMARK+SELF-PLAY | 低 |
| Capital | endgame fill-seed | B/V18 | L758-773+L489 | 末 6 天按成熟周期买 WHEAT/CARROT 种填空 | 无明确实现 | **E** | CODE+league(SELF-PLAY) | 低（仅 BUY_SEED） |
| Opponent | _opponent_pipeline | A/V18 | L2657 | 公开农场→供给估计 | ProductBelief/_OPP（更强） | B | CODE | 低 |
| Opponent | clone profile+H4 | C/V10 | L725/L789 | 签名距离→置信；市场增量→对手供给 | clone 检测+_OPP 同族 | A/B | CODE+BENCHMARK(弱) | 低 |
| Late | ENDGAME_DUMP_DAY 清算 | B/V18 | L829-852 | day≥28 全清仓 | 终局清算 680+ | B | CODE+league(SELF-PLAY) | 低（terminal 非杠杆） |
| Late | v15 末局填格 | B/V15 | commit 记录 | 末局 tile fill（league 52-8） | 无 | D | SELF-PLAY | 低 |
| Late | A2 安全小麦挤压 | A/V18 | L2677 | 对手断粮攻击 | 无 | 已拒（作者默认关） | CODE | 高 |

类别：A=已有 B=被支配 C=不相容 D=未验证 E=新候选（仅 E 可进 Exp 候选池）。证据分级：CODE/BENCHMARK/LEADERBOARD/README_CLAIM/INFERENCE。SELF-PLAY 不得作主要验收。

- agent() 管线（CODE）：_select_route（L1255：step72 V10 恢复门 _v10_should_use_v5 粘滞、24-72 legacy 布局捕获、_v8_route_label 选 V7 legacy/current 路线 tape）→ _meta_update_clone_profile（L725：公开签名距离 ≤1 置信+1 / ≤4 −1 / 否则 −3，cap 8）→ _meta_observe_h4（L789：市场库存增量推断对手供给 = observed_delta + 镇需求 − 自身供给；门：价格>1、own_supply≥2、比值 0.4-2.5、clone_confidence≥3、h4_active 粘滞）→ 修复链（_clip_seed_surplus/_weed_repair_action/_clear_passive_weeds/_cow_place_alignment/_reconcile_scheduled_cows/_guarded_demand_cow9/_repay/_front_run）。
- 结论（opponent-generalization vs self-play gain）：
  1. 克隆画像 + H4 市场增量对手推断 = 与 v11E 的 _OPP/ProductBelief/expected-opponent-sell 同族抽象 → Category A/B（v11E 已覆盖更完整：hazard/first-mover/expected sell）。
  2. 公开签名→路线门控 = 真正 opponent-conditioned（按对手公开农场与镇商店选 frozen tape）→ 但路线是开环 tape 非 live planner，且与 v11E live 调度器架构不兼容 → 直接移植 Category C；概念（签名→选路）v11E 无，但农场级改动交互风险高。
  3. visible-state repair（杂草修复等）= 无对手成分的鲁棒性，Category A（v11E 调度器已有杂草处理）。
  4. shared-market timing（_front_run + _repay + _town_demand_now）= v11E front_run 同族 + repay 防双卖细化 → Category A（细节 B）。
  5. **discrepancy 记录**：用户规格中"both-seat evaluation"与代码不符——COK 是 seat-ISOLATED 状态（_seat/per-seat _ROUTE_STATE/_META），非双座位联合评估。
  6. 总判定：COK 无 v11E 缺失的 decision abstraction；其区分特征是 frozen-tape 路线+修复链，与 v11E 架构不相容。

## Mechanism Differential Audit — Exp 3A/4 推荐方案 + Rejected 清单 (task 7, 2026-09-06)

**Exp 3A 前提判定（重要）**：用户规格假设"post-beam exposure-aware reorder 是最强候选"——**源码审计未通过**：repoA 无 beam；exposure×price 排序（_interference_value）默认关闭（interference_targeted_sort=False），提交版实际行为是稳定 sell-first + v17 ranker；且被 v11E beam 的 opp_factor+ProductBelief 支配（Category B/D）。按用户规则（"不能被 isolate → 不做"、"排序机制污染 → 优先怀疑 self-family replay"），**不推荐以 exposure reorder 为 Exp 3A**。以下按实际 Top-1/2 候选给方案。

**Exp 3A（改用 Top-1 = E2 Endgame fill-seed）**
- Treatment: research-only wrapper —— 在 v11E 的 market 订单中，当 day≥24（days_left≤6）且 money>400 且 spare tiles>0 时，按成熟周期追加 BUY_SEED（days_left>4→WHEAT ≤12；elif >3→CARROT ≤12；want=spare−已持种）
- Control: v11E 精确
- Invariant constraints: 守恒审计（cost/qty/timing/block）、SELL 集不变、beam 输入不变、farmer/hands 调度不变、terminal 不变
- 允许变化: 仅最后 6 天的 BUY_SEED 订单（market list 槽位与现金占用；后续种植交给既有调度器自然执行）
- 禁止变化: beam/farm route/scheduler/SELL/terminal/ProductBelief/动物与土地 BUY
- Primary metric: paired final bank delta（fixed-RNG 120 seeds）
- Secondary: 末局（day24-30）SELL revenue、晚产 harvest 数、win rate、BUY_SEED 触发次数
- Stopping rule: 若先静态确认 v11E 末局已无空余可填（fill 从不触发）→ LOW_COVERAGE 停；若 120 局 paired CI 跨 0 且 effect 小 → FAIL；若出现 win→loss 回归 → FAIL

**Exp 4（Top-2 = E3 Price-gated cash reserve）**
- Hypothesis: v11E 的平值 _cash_needed 在高麦价局储备不足 → 牲畜断粮逃逸损失 > 低麦价局资金闲置成本；按麦价缩放储备改善期望
- Expected mechanism: 减少断粮逃逸（$400-500 资产/头）；麦价低时释放购买力
- Likely confounders: v11E 基础 tape 可能已隐含喂料优先（若已等价 → A 类降级）；效果只在高麦价 seed 显现（方差大）
- Minimal isolated treatment: 仅当基础逻辑要买动物时，用 reserve=300+麦价×(动物+1)×喂养天 收紧门控（其余完全不变）
- 前置检查: 120 seeds 静态统计 v11E 动物断粮天数（≈0 则实验无意义，跳过）

**Rejected mechanisms（含证据）**
1. exposure×price 排序（A）— 默认关 + 无线上证据 + 被 beam opp_factor 支配（B/D）— CODE
2. v17 pairwise ranker（A）— 被 beam 排序支配（B）— CODE
3. closed-loop market 专家（A/v18）— 离线权重 + 与完整 route 强耦合 + 改 SELL timing/qty/BUY（C）— CODE
4. 签名→frozen tape 选路（C）— 与 v11E live 调度器架构不相容（C）— CODE+BENCHMARK(半独立弱)
5. V21 capital latch（A）— EXP-2 = LOW_COVERAGE（2.5% 覆盖）→ 仅 future candidate — BENCHMARK
6. 终局转换类（B step-718/C）— 用户已证伪 terminal conversion 非杠杆（B）— LEADERBOARD/实证
7. 肥料买入（B 开链）— 供应盈余 DEAD（动作瓶颈）— BENCHMARK(120 局实测)
8. A2 安全小麦挤压（A）— 作者默认关闭自判不值 — CODE
9. 全量 premium-first（Fix-A）— 线上 −50 Elo 已拒，禁止重提 — LEADERBOARD

Common protocol: engine 1.32.7, fixed-RNG via env.info["seed"] (NOT configuration["seed"]), paired seeds 1..120, seat alternation by seed parity, ledger harness for invariants (cost/quantity/timing/block conservation) + exact reconciliation, Wilson CI on win rate + paired test on per-seed bank delta.

### Exp 1 (candidate #5) — Fertilizer arbitrage. PRIORITY 1 (largest ceiling, cheap decisive measurement)
- Phase 0 (decisive measurement, B's unrun test): instrument v11E: per-game FERTILIZE count vs COLLECT_FERTILIZER count vs shed FERTILIZER at end vs fertilizable-tile window coverage. If supply surplus (fertilizer unsold in shed/sold surplus) AND FERTILIZE < coverage → ACTIONS binding → buying more useless → STOP (B's FERTILIZE_PRI race was flat, evidence of actions binding). If shed runs dry → SUPPLY binding → proceed.
- Hypothesis: BUY_PRODUCT FERTILIZER at $1 floor to cover the STRAWBERRY yield window doubles per-tile yield (4→8), SELL revenue gain > fertilizer spend.
- Control: v11E exact. Treatment: v11E + BUY_PRODUCT FERTILIZER sized to fertilizable tile-cycles + FERTILIZE priority inside the window (mirror v3.4 MELON-window line, extended to main crop).
- Frozen: _TRACE/farmer/hand scheduler/BUY slots/beam/WHEAT/terminal.
- n=120 fixed-RNG paired + heterogeneous pool (broker_bea/slotter_silas/ledger_lena/melon_mateo/rancher_rita) ≥50 each.
- Metric: SELL revenue, bank delta, FERTILIZE count, fertilizer bought/spent; check watering coverage not starved (labor competition).
- Acceptance: revenue gain > spend with 95% CI excluding 0 on pool; invariants conserved.

### Exp 2 (candidate #1) — Opponent-gap conditional late policy (V21 capital-latch concept adapted)
- Hypothesis: one-time latch at step 577 — if opponent_money − own_money ≤ −5000, disable v11E's premium front-run (risky late denial) through 719; otherwise exact v11E. Rescues hopeless games without harming close ones (v20's global version REJECTED — conditional only).
- Control: v11E. Treatment: v11E + latch. Frozen: everything else.
- n=120 paired + heterogeneous pool. Metric: bank delta vs opp, win rate, front-run activation count.
- Acceptance: pool improvement CI excluding 0; zero win-to-loss flips vs control on the self-family; invariant conservation.

### Exp 3 (candidate #4) — Exposure-targeted market denial sort (post-beam, targeted reorder; NOT blanket like Fix-A)
- Hypothesis: among final SELL orders, order by opponent_exposure×price DESC (from v11E's _opp_est) with WHEAT position preserved and exposure threshold — improves realized price vs blanket premium-first (which failed online −50).
- Control: v11E. Treatment: v11E + exposure-sorted post-beam partition. Frozen: everything else.
- n=120 paired + heterogeneous pool. Metric: SELL revenue, per-item realized price (STB/MILK/WOOL/MELON/WHEAT).
- Acceptance: pool improvement CI excluding 0 AND no closer_cleo regression AND explicit comparison to Fix-A failure mode (must not repeat −50).
- RISK FLAG: any market-list ordering change on v11E is elevated post-Fix-A; run ONLY after Exp 1/2.

### Exp 4 (candidate #2) — Endgame fill-seed (late production, NOT conversion — distinct from excluded direction)
- Hypothesis: buying WHEAT/CARROT seed (days_left ≥ harvest horizon) for tiles freed by strawberry decay adds late harvest revenue > seed cost.
- Control: v11E. Treatment: v11E + fill-seed in buy path (day ≥ threshold, spare tiles, horizon-aware seed). Frozen: everything else.
- n=120 paired + pool. Metric: late SELL revenue, bank.
- Acceptance: pool CI excluding 0.

### Exp 5 (candidates #6/#7) — Labor/capital micro (defer; check first)
- B1: static check — does v11E base scheduler already act free when standing on ready tile? If absent, isolated standing-on-work pass experiment (labor only).
- B2: instrument v11E for animal-unfed days across 120 fixed-RNG seeds; if starvation is rare, skip.

Priority order: Exp 1 → Exp 2 → Exp 3 (only if 1/2 clean) → Exp 4 → Exp 5.
