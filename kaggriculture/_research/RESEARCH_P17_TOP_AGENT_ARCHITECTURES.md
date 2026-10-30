# P17 — Top-Agent Architecture Mining

**Date:** 2026-09-12  
**Sources:** local public notebooks (`_external/public_nb`), RL training repo (`diffmap_kaggicultureRL`), R2 family.  
**Web leaderboard scrape:** unavailable this session (tool offline) — rank-only teams marked UNKNOWN.  
**No new agent. No submission.**

---

## Final answer to the research question

```text
EXTERNAL_SIGNAL_STRONG — Type A/E dominates among VERIFIED public elites
```

反复出现的结构 **不是** “每步 closed-loop planner”，也不是我们 P16 那种单点 cash bailout：

```text
open-loop route/tape skeleton
+ 2–4 sparse observable checkpoint branches
+ bounded repair
```

**我们尚未真正测过** 的是：**prefix-compatible continuation library**（tetsu_shape 式），不是 P16 的 FORCE_SELL branch。

---

## Q1–Q6 (required)

| Q | Answer | Evidence |
|---|---|---|
| **Q1** 普遍 open-loop+branch？ | **VERIFIED yes** among public elites we can read | tetsu_shape, R2/yhay81, kaito v43/v48, prvsiyan_moon |
| **Q2** branch 粒度？ | **Milestone / turn-checkpoint + observable feature**，不是每步、也不是最终分数 | tetsu DECISIONS `(turn, feature, thr, tail)` |
| **Q3** RL 在哪层？ | **训练期 action-bundle PPO**；replay 是 **init/prior**；**未见** runtime branch-level RL 在 top public nb | diffmap POLICY_MODES / ARCHITECTURE |
| **Q4** replay 是完整 policy？ | **VERIFIED: tape 是 backbone policy**（720-step tapes）；branch 只选 tail | tetsu_shape docstring; R2 `_INLINE_TAPES` |
| **Q5** branch/RL 跨 matchup 泛化？ | **UNKNOWN / 无公开证明** | 无 private leaderboard 分析 |
| **Q6** 我们未测过的？ | **Continuation library + prefix-compatible checkpoint switch** | P9 closed-loop 0-8；P16 单 branch NOT_ROBUST |

---

## Architecture Taxonomy

| Type | Description | VERIFIED examples |
|---|---|---|
| **A** | Pure open-loop replay/tape | prvsiyan_moon raw episodes; R2 tape core |
| **B** | Open-loop + deterministic branches | **tetsu_shape** (3 DECISIONS); **kaito v43** (2 shop branches); R2 SHOP_PLANS |
| **C** | Open-loop + learned branch selector | not seen in public elite code |
| **D** | Open-loop + RL continuation (runtime) | not seen in submitted public nbs |
| **D-train** | Offline RL/PPO training stack | **diffmap_kaggicultureRL** (mimicry→single→dual seat) |
| **E** | Tape library + online policy/tail selection | **tetsu_shape**; kaito sparse_router |
| **F** | Fully closed-loop planner | our P9/P11 — **local FAIL**, not observed in top public |

---

## Team / source map (`p17_team_architectures.csv`)

| Source | Type | Branch granularity | RL role | Replay role | Status |
|---|---|---|---|---|---|
| **tetsu_shape** | B/E | **turn+feature+threshold → tail tape** (3 pts) | none runtime | **backbone tapes** | **VERIFIED** |
| **R2 / yhay81 / prvsiyan_moon** | A/B/E | shop-pair @ step 144 → 1 of 13 tapes | none runtime | **full 720-step tapes** | **VERIFIED** |
| **kaito v43** | B/E | “two observable shop branches”; sparse_router | none in header | route memory + planner lib | **VERIFIED** (docstring/modules) |
| **kaito v48** | B/E | “two real fast-climber continuations” + gold_floor | none in header | same stack | **VERIFIED** |
| **diffmap_kaggicultureRL** | D-train | N/A runtime (research repo) | **PPO action-bundle** every step in train | **behavior mimicry init** | **VERIFIED** (repo docs) |
| tetsu_msf | A/B | shop router lineage | none | tapes | **VERIFIED** (same family) |
| Majkel1337 / SpaTaro / Otter Vibe / feel the agi | ? | ? | ? | ? | **UNKNOWN** (no local public code) |

---

## Best VERIFIED pseudocode (structure only)

### tetsu_shape (canonical Type B/E)

```python
# VERIFIED public docstring + DECISIONS table
backbone = load_route_tape(MAIN)  # long open-loop route

for turn in range(720):
    action = backbone[turn]
    for (t, feature, thr, tail) in DECISIONS:  # only 3 checkpoints
        if turn == t and observe(feature) >= thr:
            backbone = prefix_compatible_tail(tail)  # switch continuation
    action = repair_noop_sells_capacity(action, state)
    emit(action)
```

Checkpoints (VERIFIED):

| turn | feature | threshold | tail |
|---:|---|---:|---|
| 226 | shop_YARN_STORE | 1 | YARN |
| 360 | px_CARROT | 42 | YARN_CARROT |
| 433 | inv_MILK | 10067 | MILK_GLUT |

**Branch 粒度 = 少量固定 turn + 可观测 economic/shop 信号 → 预验证 tail tape。**

### R2 / shop-router family

```python
# VERIFIED from _push_medal / public_nb headers
tapes = load_13_inline_tapes()
plan = SHOP_PLANS[tuple(unlocked_shops[:2])] if step == 144 else plan
action = tapes[plan][step]
action = repair_weeds + advance_sales + overlays
```

---

## Branch taxonomy (`p17_branch_taxonomy.csv`)

| Granularity | Example | VERIFIED |
|---|---|---|
| Full 720-step tape | R2, moon raw | YES |
| Shop-pair route @ d6 | R2 SHOP_PLANS | YES |
| Sparse turn checkpoints (2–3) | tetsu_shape | YES |
| Shop branch @ climb window | kaito v43 | YES |
| Inventory/price economic thr | tetsu px_CARROT / inv_MILK | YES |
| Continuous state deviation detector | our P16 | local only, NOT_ROBUST |
| Learned branch policy | — | NO public elite |

---

## RL role (`p17_rl_role.csv`)

| Question | diffmap_kaggicultureRL |
|---|---|
| Where | **action-level** (masked action bundles) |
| When | **every step in training rollouts** (not runtime branch) |
| Action space | structured farm/market action bundles + masks |
| Before RL | **behavior mimicry from Kaggle replays** |
| Runtime submit | policy checkpoint inference — **not** “RL each turn in notebook” as far as docs show |

**CLAIMED** that this can beat tape agents — **UNKNOWN** vs current top-10 (no public score attached in repo README).

---

## Replay role (`p17_replay_role.csv`)

| Source | Replay = policy? | Replay = prior? |
|---|---|---|
| R2 / moon / tetsu_msf | **YES backbone** | also |
| tetsu_shape | **YES backbone + tails** | also |
| diffmap | **NO** (init only) | **YES mimicry** |

---

## Internal P0–P16 vs external

| External pattern | Our status |
|---|---|
| Type F closed-loop planner | **P9/P11 FAIL 0-8 / bankruptcy** — matches external rarity |
| Type A/B tape backbone | R2 is our champion; clone overlays **STOP** |
| Type B sparse economic checkpoints | **P16 tried one FORCE_SELL — NOT_ROBUST** (not the same as tail-library) |
| Type E prefix-compatible continuation library | **NOT TESTED** |
| Type D-train PPO | not built; high cost; no public elite proof in corpus |

---

## Strongest untested architecture (for P17.1 only)

```text
Type E: tape/route library
+ 2–3 observable checkpoints (shop / price / inventory)
+ prefix-compatible tail switch
+ p10-style repair
```

**不是** 复制 tetsu tapes；是实现 **architecture**：`skeleton → checkpoint → continuation`。

**本轮默认不实现**（user rule 11）。若开 P17.1：最小 2 tails + 1 shop checkpoint + repair only.

---

## Decision

```text
EXTERNAL_SIGNAL_STRONG
```

不是 `NO_EXTERNAL_ARCHITECTURE_SIGNAL`。

**Q1 YES** among VERIFIED public elites.  
**Q6 gap = Type E continuation library**, not another hand-tuned cash branch.

**NO IMPLEMENTATION this cycle. NO SUBMIT.**

---

## Artifacts

```text
RESEARCH_P17_TOP_AGENT_ARCHITECTURES.md
p17_team_architectures.csv
p17_branch_taxonomy.csv
p17_rl_role.csv
p17_replay_role.csv
p17_architecture_evidence.csv
```
