# Top-5 External Candidate 16-Game Screening

## Blocked / Pre-check

| Candidate | Status | Reason |
|-----------|--------|--------|
| boatlee | BLOCKED_NO_ENTRY_POINT | see notes |

## Smoke Results

| Candidate | Load OK | Action OK | Steps | Error |
|-----------|---------|-----------|-------|-------|
| tetsu2131 | True | True | 720 | - |
| prvsiyan | True | True | 720 | - |
| flexonafft | True | True | 720 | - |
| salemali7 | True | True | 720 | - |

## 16-Game Summary

| Candidate | Verdict | W-L-T | WR | 95% CI | Mean Margin | Seat0 WR | Seat1 WR | Seat Bias |
|-----------|---------|-------|----|--------|-------------|----------|----------|-----------|
| tetsu2131 | ADVANCE | 16-0-0 | 100.00% | [100.00%, 100.00%] | 20194.1 | 100.00% | 100.00% | no |
| prvsiyan | ADVANCE | 16-0-0 | 100.00% | [100.00%, 100.00%] | 50398.0 | 100.00% | 100.00% | no |
| flexonafft | ADVANCE | 16-0-0 | 100.00% | [100.00%, 100.00%] | 44355.4 | 100.00% | 100.00% | no |
| salemali7 | ADVANCE | 16-0-0 | 100.00% | [100.00%, 100.00%] | 23968.1 | 100.00% | 100.00% | no |

## Infrastructure Q&A

1. **State bleed**: `make("kaggriculture")` creates a fresh env per call; `load_pool_agent("v11E")` returns a fresh module instance each time. No state bleed between games.

2. **Observation schema match**: Verified with seed=1..3 that both players see `player`, `step`, `farms` (len=2), `town`, `market`, `private`, `day`, `hour`. Both farms start at $3000. Schema matches all 4 candidates' expectations.

3. **Bank reading symmetry**: `obs0["farms"][0]["money"]` and `obs1["farms"][1]["money"]` correctly read each player's own farm. Cross-checked with v11E self-play and tetsu2131 action logs.

4. **v11E seed determinism**: 4 v11E-vs-v11E games showed margins 1919, -462, -2005, 3061 with alternating winners. Small margins (~1-3k) confirm v11E is functional. Known seat-mirror non-determinism documented in benchmark discipline.

5. **Module-cache collision**: Solved via `importlib.util.spec_from_file_location` with unique module names `cand_{name}` per candidate.


## Decision

- **ADVANCE**: tetsu2131, prvsiyan, flexonafft, salemali7
- **BORDERLINE**: none
- **FAIL**: none
- **BLOCKED**: boatlee

## Individual Games

- **tetsu2131** seed=1 seat=0: cand=75951.0 opp=48115.0 margin=27836.0 winner=0 status=completed
- **tetsu2131** seed=2 seat=0: cand=81608.0 opp=65529.0 margin=16079.0 winner=0 status=completed
- **tetsu2131** seed=3 seat=0: cand=93157.0 opp=70207.0 margin=22950.0 winner=0 status=completed
- **tetsu2131** seed=4 seat=0: cand=82636.0 opp=68074.0 margin=14562.0 winner=0 status=completed
- **tetsu2131** seed=5 seat=0: cand=92402.0 opp=64869.0 margin=27533.0 winner=0 status=completed
- **tetsu2131** seed=6 seat=0: cand=90319.0 opp=58829.0 margin=31490.0 winner=0 status=completed
- **tetsu2131** seed=7 seat=0: cand=114381.0 opp=82668.0 margin=31713.0 winner=0 status=completed
- **tetsu2131** seed=8 seat=0: cand=124031.0 opp=109322.0 margin=14709.0 winner=0 status=completed
- **tetsu2131** seed=1 seat=1: cand=56537.0 opp=41349.0 margin=15188.0 winner=1 status=completed
- **tetsu2131** seed=2 seat=1: cand=71993.0 opp=51511.0 margin=20482.0 winner=1 status=completed
- **tetsu2131** seed=3 seat=1: cand=96682.0 opp=69638.0 margin=27044.0 winner=1 status=completed
- **tetsu2131** seed=4 seat=1: cand=70196.0 opp=52221.0 margin=17975.0 winner=1 status=completed
- **tetsu2131** seed=5 seat=1: cand=50916.0 opp=43669.0 margin=7247.0 winner=1 status=completed
- **tetsu2131** seed=6 seat=1: cand=85266.0 opp=70618.0 margin=14648.0 winner=1 status=completed
- **tetsu2131** seed=7 seat=1: cand=93295.0 opp=79057.0 margin=14238.0 winner=1 status=completed
- **tetsu2131** seed=8 seat=1: cand=45225.0 opp=25814.0 margin=19411.0 winner=1 status=completed
- **prvsiyan** seed=1 seat=0: cand=106223.0 opp=58655.0 margin=47568.0 winner=0 status=completed
- **prvsiyan** seed=2 seat=0: cand=117707.0 opp=50940.0 margin=66767.0 winner=0 status=completed
- **prvsiyan** seed=3 seat=0: cand=93298.0 opp=51651.0 margin=41647.0 winner=0 status=completed
- **prvsiyan** seed=4 seat=0: cand=161641.0 opp=122853.0 margin=38788.0 winner=0 status=completed
- **prvsiyan** seed=5 seat=0: cand=103142.0 opp=58720.0 margin=44422.0 winner=0 status=completed
- **prvsiyan** seed=6 seat=0: cand=113534.0 opp=74333.0 margin=39201.0 winner=0 status=completed
- **prvsiyan** seed=7 seat=0: cand=153359.0 opp=90944.0 margin=62415.0 winner=0 status=completed
- **prvsiyan** seed=8 seat=0: cand=96753.0 opp=47041.0 margin=49712.0 winner=0 status=completed
- **prvsiyan** seed=1 seat=1: cand=101505.0 opp=36950.0 margin=64555.0 winner=1 status=completed
- **prvsiyan** seed=2 seat=1: cand=135085.0 opp=92279.0 margin=42806.0 winner=1 status=completed
- **prvsiyan** seed=3 seat=1: cand=112972.0 opp=55104.0 margin=57868.0 winner=1 status=completed
- **prvsiyan** seed=4 seat=1: cand=118772.0 opp=45701.0 margin=73071.0 winner=1 status=completed
- **prvsiyan** seed=5 seat=1: cand=79272.0 opp=36758.0 margin=42514.0 winner=1 status=completed
- **prvsiyan** seed=6 seat=1: cand=115992.0 opp=79665.0 margin=36327.0 winner=1 status=completed
- **prvsiyan** seed=7 seat=1: cand=171698.0 opp=121409.0 margin=50289.0 winner=1 status=completed
- **prvsiyan** seed=8 seat=1: cand=89305.0 opp=40887.0 margin=48418.0 winner=1 status=completed
- **flexonafft** seed=1 seat=0: cand=94239.0 opp=42882.0 margin=51357.0 winner=0 status=completed
- **flexonafft** seed=2 seat=0: cand=88430.0 opp=45786.0 margin=42644.0 winner=0 status=completed
- **flexonafft** seed=3 seat=0: cand=118395.0 opp=86151.0 margin=32244.0 winner=0 status=completed
- **flexonafft** seed=4 seat=0: cand=162001.0 opp=115770.0 margin=46231.0 winner=0 status=completed
- **flexonafft** seed=5 seat=0: cand=108109.0 opp=68185.0 margin=39924.0 winner=0 status=completed
- **flexonafft** seed=6 seat=0: cand=115728.0 opp=71126.0 margin=44602.0 winner=0 status=completed
- **flexonafft** seed=7 seat=0: cand=114897.0 opp=73430.0 margin=41467.0 winner=0 status=completed
- **flexonafft** seed=8 seat=0: cand=91526.0 opp=50883.0 margin=40643.0 winner=0 status=completed
- **flexonafft** seed=1 seat=1: cand=132325.0 opp=89031.0 margin=43294.0 winner=1 status=completed
- **flexonafft** seed=2 seat=1: cand=95054.0 opp=45002.0 margin=50052.0 winner=1 status=completed
- **flexonafft** seed=3 seat=1: cand=130689.0 opp=88885.0 margin=41804.0 winner=1 status=completed
- **flexonafft** seed=4 seat=1: cand=99533.0 opp=30914.0 margin=68619.0 winner=1 status=completed
- **flexonafft** seed=5 seat=1: cand=100565.0 opp=59151.0 margin=41414.0 winner=1 status=completed
- **flexonafft** seed=6 seat=1: cand=96759.0 opp=50990.0 margin=45769.0 winner=1 status=completed
- **flexonafft** seed=7 seat=1: cand=133662.0 opp=91110.0 margin=42552.0 winner=1 status=completed
- **flexonafft** seed=8 seat=1: cand=89854.0 opp=52784.0 margin=37070.0 winner=1 status=completed
- **salemali7** seed=1 seat=0: cand=131069.0 opp=106452.0 margin=24617.0 winner=0 status=completed
- **salemali7** seed=2 seat=0: cand=100158.0 opp=80816.0 margin=19342.0 winner=0 status=completed
- **salemali7** seed=3 seat=0: cand=112978.0 opp=80728.0 margin=32250.0 winner=0 status=completed
- **salemali7** seed=4 seat=0: cand=110410.0 opp=81387.0 margin=29023.0 winner=0 status=completed
- **salemali7** seed=5 seat=0: cand=103057.0 opp=80956.0 margin=22101.0 winner=0 status=completed
- **salemali7** seed=6 seat=0: cand=117043.0 opp=100550.0 margin=16493.0 winner=0 status=completed
- **salemali7** seed=7 seat=0: cand=99686.0 opp=72826.0 margin=26860.0 winner=0 status=completed
- **salemali7** seed=8 seat=0: cand=123076.0 opp=92979.0 margin=30097.0 winner=0 status=completed
- **salemali7** seed=1 seat=1: cand=124547.0 opp=99442.0 margin=25105.0 winner=1 status=completed
- **salemali7** seed=2 seat=1: cand=155421.0 opp=135152.0 margin=20269.0 winner=1 status=completed
- **salemali7** seed=3 seat=1: cand=54733.0 opp=38132.0 margin=16601.0 winner=1 status=completed
- **salemali7** seed=4 seat=1: cand=111815.0 opp=93563.0 margin=18252.0 winner=1 status=completed
- **salemali7** seed=5 seat=1: cand=71304.0 opp=41923.0 margin=29381.0 winner=1 status=completed
- **salemali7** seed=6 seat=1: cand=112471.0 opp=91788.0 margin=20683.0 winner=1 status=completed
- **salemali7** seed=7 seat=1: cand=123099.0 opp=97117.0 margin=25982.0 winner=1 status=completed
- **salemali7** seed=8 seat=1: cand=82386.0 opp=55953.0 margin=26433.0 winner=1 status=completed