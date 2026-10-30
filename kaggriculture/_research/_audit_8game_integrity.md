# Benchmark Result Integrity Audit

**Date:** 2026-09-11  
**Scope:** `_external_8game_benchmark.py` + `_external_8game_results.json` (24 games, 3 candidates)  
**Verdict:** `INVALID` — previous FAIL must be discarded

---

## 1. Harness Validation

**Status:** FAIL — critical bug found.

File `D:\桌面\Kaggle\kaggriculture\_external_8game_benchmark.py` lines 12-17 use the pattern:

```python
sys.path.insert(0, os.path.join(..., "_external", "lonespear"))
import wrapper as ls_wrapper
sys.path.insert(0, os.path.join(..., "_external", "ronin5205"))
import wrapper as ron_wrapper
sys.path.insert(0, os.path.join(..., "_external", "gzmcr"))
import wrapper as gz_wrapper
```

Python caches modules by name. Because all three directories contain a file named `wrapper.py`, the first import (`lonespear/wrapper.py`) is cached under the name `wrapper`. The next two `import wrapper as ...` statements return the **same cached module object**, ignoring the different `sys.path` entries.

Evidence (fresh Python process):

```
ls_wrapper.__file__: D:\...\lonespear\wrapper.py
ron_wrapper.__file__: D:\...\lonespear\wrapper.py
gz_wrapper.__file__:  D:\...\lonespear\wrapper.py
ls_wrapper.agent is ron_wrapper.agent is gz_wrapper.agent: True
ls_wrapper is ron_wrapper is gz_wrapper: True
```

**Impact:** `CANDIDATES` dict lambdas at lines 22-24 all return `ls_wrapper.agent`. Every game labeled `ronin5205` or `gzmcr` actually executed lonespear's agent.

---

## 2. Wrapper Compatibility

All three wrappers share the same structure:

```python
import main as <alias>
def agent(obs): return <alias>.agent(obs)
```

The wrappers themselves are compatible with the kaggriculture observation schema (`obs["farms"][0]["money"]`, etc.). The failure is not in the wrapper body but in the benchmark harness's import strategy.

A correct loader must use distinct module names, e.g.:

```python
import importlib.util
spec = importlib.util.spec_from_file_location("ronin_main", r"…\ronin5205\main.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
```

---

## 3. Agent Execution Verification

Smoke tests for lonespear, ronin5205, and gzmcr were recorded as `smoke_pass` in `D:\桌面\Kaggle\kaggriculture\_external_candidates.json` with notes such as "Import OK, valid action dict, 720-step game completes DONE/DONE."

Those smoke results are **not directly reproducible** from a saved results file (`_external_smoke_results.json` does not exist in the workspace). They were generated inline in a prior session. Because the smoke-test script `_external_smoke.py` uses the same `import wrapper as X` pattern for `sey_v21`, `gytdrop_v5`, and `cok_v10`, those particular smoke tests are also internally inconsistent (all three wrappers resolve to `sey_v21/wrapper.py` in that script).

For the three candidates in question, we have no file-backed smoke evidence that ronin5205 or gzmcr were actually executed during smoke. The `smoke_pass` flag is therefore **untrusted** unless re-verified with unique-name loading.

---

## 4. Result Auditing (6 Selected Games)

Selected games from `_external_8game_results.json`:

| Candidate | Seed | External Seat | Ext Bank | v11E Bank | Margin |
|-----------|------|---------------|----------|-----------|--------|
| lonespear | 1 | 0 | 36,064 | 62,751 | -26,687 |
| lonespear | 1 | 1 | 61,490 | 109,167 | -47,677 |
| ronin5205 | 1 | 0 | 33,850 | 58,868 | -25,018 |
| ronin5205 | 1 | 1 | 37,600 | 61,519 | -23,919 |
| gzmcr | 1 | 0 | 47,797 | 85,924 | -38,127 |
| gzmcr | 1 | 1 | 83,483 | 126,628 | -43,145 |

All six entries show `completed: true` and `runtime_error: null`. Because the harness bug forces all three candidate labels to use `ls_wrapper.agent`, these six records are **not independent observations**. They are six independent game runs of the **same agent** (lonespear) under different seed/seat conditions.

To confirm lonespear's margin scale, two properly-loaded verification games were run with `importlib.util.spec_from_file_location`:

- seed=1, lonespear seat0: margin = -36,106
- seed=1, lonespear seat1: margin = -42,109

These margins are consistent in magnitude and sign with the benchmark JSON entries for all three candidates, consistent with the interpretation that the JSON records are all lonespear games.

---

## 5. Hypothesis Investigation

| Hypothesis | Verdict | Evidence |
|------------|---------|----------|
| **H1 — Module caching bug** | **CONFIRMED** | `ls_wrapper is ron_wrapper is gz_wrapper` returns `True`; all `__file__` point to lonespear/wrapper.py |
| **H2 — v11E is actually that strong** | **Partially supported** | Properly-loaded lonespear loses to v11E by ~25k–50k in spot checks. v11E is clearly strong, but this does not explain why ronin5205/gzmcr show identical 0-8 records |
| **H3 — External agents crash/error silently** | **Rejected** | All 24 JSON records have `completed: true` and `runtime_error: null` |
| **H4 — Observation format mismatch** | **Rejected** | All games reach terminal state; no `AttributeError` or `Struct` failures observed in results |
| **H5 — Determinism/seeding issue** | **Rejected as root cause** | v11E mirror matches are non-deterministic locally, but this affects both seats equally and cannot produce a perfect 0-8 sweep across three distinct agents by chance |

**Primary root cause:** H1 (module caching collision).

---

## 6. Margin Definition Verification

`_external_8game_benchmark.py` line 78:

```python
margin = (ext_bank - v11e_bank) if (ext_bank is not None and v11e_bank is not None) else None
```

Seat mapping:
- `external_seat == 0` → `run_game(ext, v11e, seed)` → `ext_bank = bank_seat0`, `v11e_bank = bank_seat1`
- `external_seat == 1` → `run_game(v11e, ext, seed)` → `v11e_bank = bank_seat0`, `ext_bank = bank_seat1`

`run_game` reads `fin[-1]["observation"]["farms"][player_id]["money"]`, which matches the engine's terminal observation structure.

**Conclusion:** Margin and seat-mapping logic are arithmetically correct. The bug is upstream (wrong agent object), not in post-processing.

---

## 7. Seat Swap Verification

Summary in JSON:

- lonespear: `seat0_record = "0-4"`, `seat1_record = "0-4"`
- ronin5205: `seat0_record = "0-4"`, `seat1_record = "0-4"`
- gzmcr:    `seat0_record = "0-4"`, `seat1_record = "0-4"`

The seat swap code path is exercised (lines 70-77 of the benchmark script). Because all three candidates share the same underlying agent, the symmetric 0-4 / 0-4 split is exactly what we would expect if a single agent played all 8 games.

---

## 8. Smoke Test Validity

The candidate database marks lonespear, ronin5205, and gzmcr as `smoke_pass`. However:

1. No `_external_smoke_results.json` file exists in the workspace.
2. The only smoke script found (`_external_smoke.py`) tests `sey_v21`, `gytdrop_v5`, `cok_v10` against `closer_cleo`, and that script suffers from the same wrapper-collision bug for its three external candidates.
3. There is no file-backed evidence that ronin5205 or gzmcr were individually verified to import correctly and produce valid actions.

**Conclusion:** Smoke status for these three candidates is **unverified by persisted artifacts**. Even if inline smoke succeeded in a prior session, the absence of saved results means we cannot audit the smoke phase after the fact.

---

## 9. v11E Determinism Check

Two v11E vs v11E mirror games with seed=1 produced:

- Run 1: seat0=106,947, seat1=98,082
- Run 2: seat0=71,267,  seat1=71,948

This confirms the local `kaggle_environments` runtime is **non-deterministic** for mirror matches, likely because the engine's default `random_agent` path or OpenSpiel initialization injects hidden state. This does not affect the candidate-vs-v11E comparison's directional validity (both seats see the same engine noise), but it does mean exact margin reproduction across separate Python invocations is not guaranteed.

---

## 10. Engine Seed Handling

`kaggriculture.py` uses:

```python
seed = env.info.get("seed", 0)
rng = random.Random((seed * 1_000_003) ^ day)
```

for day-level RNG (town shop unlocks). The benchmark script sets `env.configuration["seed"] = seed` before `env.run(...)`, which the engine reads via `resolve_episode_seed`. Seed handling is consistent across all 24 games.

---

## 11. Observation Structure

The engine's terminal observation provides:

```python
obs["farms"][player_id]["money"]
```

This is what the benchmark script reads. It matches the structure verified in prior sessions and matches what external agents expect to receive.

---

## 12. Final Verdict

**`INVALID`**

The 24 games in `_external_8game_results.json` are not genuine head-to-head matches between v11E and three distinct external agents. Due to the wrapper module caching collision in `_external_8game_benchmark.py`, **all three candidates executed the same agent (lonespear)**.

Consequences:
- The `0-8` records for `ronin5205` and `gzmcr` are artifacts, not evidence of strength.
- The `0-8` record for `lonespear` is a genuine lonespear-vs-v11E result, but it is entangled with the other two labels and cannot be interpreted as a clean 8-game sample without re-running with corrected wrappers.
- The previous conclusion `FAIL` for all three candidates is **vacated**.
- Smoke-test claims for these candidates are **untrusted** because no file-backed smoke artifacts exist and the only smoke script in the repo has the same collision bug for its own candidate set.

**Required minimal retest scope (no v11E/production changes, no fusion, no tuning):**
1. Fix wrapper loading in `_external_8game_benchmark.py` to use `importlib.util.spec_from_file_location` with unique module names per candidate.
2. Re-run the exact same 24-game matrix (seeds 1-4, both seats).
3. Re-run smoke for the three candidates with the same unique-name loader, persisting results to `_external_8game_smoke_results.json`.

Anything beyond that 24-game matrix is out of scope for this audit.
