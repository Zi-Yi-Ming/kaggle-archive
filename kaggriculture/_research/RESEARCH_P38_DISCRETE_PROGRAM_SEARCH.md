# P38 — Discrete Program Discovery (Phase 1)

**Date:** 2026-09-13  
**Protocol:** pin `env.info["seed"]`, vs finn, finn **unwrapped**  
**Grid:** 480 discrete programs (opening × mid_crop × animal_mix × land × hire × sell)

---

## Decision

```text
SIMPLE_GRAMMAR_PLUS_P11_WORKERS_CANNOT_DISCOVER_ELITE_PROGRAM
```

- Stage1 max bank = **21,089** (seed 1)  
- p11 baseline (same worker substrate, unmodified market) = **26,725**  
- **0 / 480** programs beat p11  
- **0** reached Level1 (100k)  
- R2 mean3 reference = **183,850**

---

## Harness artifact (must keep)

Wrapping the opponent with a 2-arg wrapper **breaks 1-arg agents** (finn):

| protocol | R2 bank s1 |
|---|---:|
| finn unwrapped | **181,389** |
| finn wrapped (co_argcount=2) | 148,548 |

Root cause: kaggle-env passes `args[:co_argcount]`; wrap makes finn crash every step → no-op opponent → different shared market.  
**Rule: never wrap finn. Only wrap candidate with matching arity.**

---

## Stage1 distribution

| stat | bank |
|---|---:|
| max | 21,089 |
| p90 | 17,148 |
| median | 1,983 |
| mean | 4,826 |
| ≥ p11 (26.7k) | **0** |
| ≥ 100k | **0** |

Opening mean (seed1):

| opening | mean | max |
|---|---:|---:|
| wheat_flood | 9,948 | 17,793 |
| animal_pack | 6,349 | 21,089 |
| melon_pack | 4,393 | 16,425 |
| straw_open | 2,133 | 9,385 |
| melon_lean | 1,308 | 3,838 |

Top-30 unique bank values = **3** — discrete space is highly degenerate after sanitize + p11 residual market.

---

## Stage2 (top12 × seeds 2–3)

| s1 best | mean3 | note |
|---:|---:|---|
| 21,089 | **7,114** | collapses to 194 / 59 on s2/s3 |
| 19,607 | 6,565 | collapses to 30 / 59 |

**No seed-stable candidate.** s1 peaks are path noise, not programs.

Novelty: `sim_R2 = 0.000` for all — trivially different tapes (market prepends). **Novelty without bank is not discovery.**

---

## Why it failed

1. **Market prepend breaks p11 coupling (P33).**  
   p11 workers expect p11 market timing (seed buys, hires, animals). Prepending grammar orders starves or duplicates; residual p11 orders get truncated at 10.

2. **Worker throughput is the real bottleneck.**  
   R2: 19 plants by d2, 16 animals by d12, hire ramp 3→14.  
   p11+grammar: cash-poor, few plants, animals stuck in shed.  
   Market-level discrete knobs cannot create elite production volume.

3. **Cannot emit a “new program” from market vocabulary alone.**  
   P36/P37: elite = atomic open-loop program. Market grammar is one layer of a coupled whole.

4. **Custom high-throughput workers (attempted) were worse than p11** (banks ~0–300) — plant serialization, weed takeover, sticky-task thrash, BUILD vs PLANT.

---

## What is NOT supported

| hypothesis | verdict |
|---|---|
| Enumerate opening×crop×hire×sell → 100k+ program | **REJECTED** |
| Market prepend on p11 finds new elite | **REJECTED** |
| Novelty (sim=0) implies valuable new basin | **REJECTED** (bank=0–21k) |
| Stage1 seed1 peak is a real program | **REJECTED** (stage2 collapse) |

---

## Implications for medal path

```text
P37  elite tapes atomic (no recombination alpha)
P38  simple discrete grammar + weak workers ≠ new elite   ← HERE
```

To get a **5th 160k+ program** need one of:

1. **Elite-quality worker tape** as a first-class program component (not p11) — i.e. synthesize open-loop choreography, not just market knobs  
2. **True program synthesis** over larger structured space with cheap multi-seed eval (not 480-grid hand grammar)  
3. **External corpus** (more public elites / leaderboard strategies)  
4. Accept **paradigm ceiling**: production baseline R2 remains champion; no local gate-passing candidate

**STOP:** further hand-grid market grammars on p11; treating sim=0 as discovery; wrapping finn.

---

## Artifacts

```text
RESEARCH_P38_DISCRETE_PROGRAM_SEARCH.md
p38_stage1.csv          # 480 rows
p38_stage2.csv          # top12 × s2,s3
p38_program/compiler.py
_p38_search.py
_p38_wrap_diag.py       # harness wrap artifact
p26_harness.py          # pin still required; do NOT wrap finn
```
