# Adaptivity Analysis — Top-5 External Candidates

Classification based on actual code behavior, not notebook titles.

| Candidate | Tier | Basis |
|-----------|------|-------|
| tetsu2131 | B | `_kawa_route_label(obs)` selects among 5 pre-computed tapes, then `agent()` applies 10+ heuristic repairs (`_weed_repair_action`, `_v17_feed_guard`, `_v17_room_evac`, `_repay_shift`, `_rank_sell_slots`, `_preempt_shift`, `_v17_r5_counter`, `_v17_md_counter`, `_v17_room_guard`, `_terminal_liquidation`). Not runtime-learning; the branching logic and tape library are fixed at write time. |
| prvsiyan | B | `Policy.act(observation)` selects one of 13 complete action tapes via `SHOP_PLANS` lookup on the first two observed shops, then applies `repair_weeds`, `subtract_advanced_sales`, `advance_sales`, and terminal `liquidate`. Tape selection and repairs are observation-conditioned but fully hand-coded. |
| flexonafft | B | `_features(observation)` extracts 30+ numeric features (money delta, prices, inventory, shop counts, demand, tile yields/weeds). `_choose(block, x)` walks a pre-built decision tree (`_TREES`) to select a tape index at the start of each 144-step block. Replay is deterministic once the tree path is chosen; the tree itself is static. |
| salemali7 | B | Base actions come from a fixed `_ACTIONS[step]` tape. `agent()` then applies `_weed_repair_action`, `_repay`, and `_front_run` conditionally on the observation. The core is replay, but the repairs make the effective policy observation-dependent. |
| boatlee | U | No executable `agent()` found in the notebook; only adaptive-market hysteresis discussion / configuration. Cannot inspect code behavior. |

## Tier definitions

- **Tier A**: Truly adaptive / runtime learning (RL policy, online search, model inference). None of the inspected candidates exhibit runtime weight updates or lookahead search.

- **Tier B**: Heuristic conditional. Hand-coded rules branch on observation features, but the branching logic and base action library are pre-computed. All 4 executable candidates fall here.

- **Tier C**: Fixed tape / replay. Pre-recorded action sequence with no observation-dependent branching beyond trivial post-processing. None of the 4 are pure Tier C.

- **Tier U**: Unknown. boatlee falls here because no runnable entry point was found.
