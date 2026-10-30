# v6 — candidate_guided @ sample/demo budget

Status: **complete, valid failure trace. Do not overwrite.**

This is a real end-to-end run, not a broken result. It is the reference point
that v7 tests against.

## Budget actually in effect

| field | value | source |
| --- | --- | --- |
| `timeout_seconds` | 60 | `sample_submission/eval_config.yaml` |
| `max_tool_calls` | 10 | same |
| `max_time_minutes` | 1 | same |
| `max_turns` | 50 | same |

`eval_settings_source: defaults (no eval_config.yaml in agent dir)`

The agent dir carries no `eval_config.yaml`, so `read_eval_settings()` fell back
to the demo values mirrored from `sample_submission`. These are the tightest
values in the system and are not the runtime's capability ceiling.

## Chain

```
MODEL_INIT        PASS
HARNESS_INIT      PASS
TASK_LOAD         PASS
CANDIDATE_INJECTED PASS   sha256 ffc2d61b...7def, 15/15 paths, 4319 chars
AGENT_EXECUTED    PASS   14 steps
PATCH_GENERATED   PASS   1244 chars
SUBMIT_PATCH      PASS   {"status":"ok","patch_size":1244,"files_changed":1}
EVALUATION        PASS   test_exit_code = 1
RESOLVED          False
```

`server_start_count=1`, `startup_sec=340.4`, `runtime_sec=423.9`, `tp_size=4`,
`served_model_name=/kaggle/input/models/google/gemma-4/other/gemma-4-31b-it-qat-w4a16-ct/2`.

## Trajectory

1. grep/read `File` + `Form` handling in `fastapi/params.py` and
   `fastapi/dependencies/utils.py` — localization direction was correct.
2. wrote `/workspace/reproduce_issue.py`.
3. ran `pytest reproduce_issue.py`, hit
   `async def functions are not natively supported`.
4. retried `-p no:anyio`, `-o timeout=0`, `-s` — same error each time, never
   concluded the failure was unrelated to the repair goal.
5. tool call 10: `{"status":"error","error_type":"BudgetExceeded",
   "error_message":"Tool call budget exhausted (10 calls)"}`.
6. `submit_patch()` with `files_patched = ["reproduce_issue.py"]`.

`fastapi/` was never modified.

## Why this outcome is ambiguous

Two causes are confounded and cannot be separated from this run alone:

- **budget** — the run stopped mid-debugging at call 10.
- **recovery policy** — it looped on a failing command without changing approach.

v7 changes only the budget, so the difference between the two runs is
attributable.

## Files

- `gpu_smoke_v6_e2e_ran_not_resolved.json` — full telemetry
- `gpu_smoke_v6_trace_fastapi_11194.json` — per-step trajectory (15 steps)
- `gpu_smoke_v6_bootstrap.json` — hardware / runtime / data inventory
- `kernel.log` — Kaggle kernel output
- `agent.log` — empty (harness writes agent output to the trace, not this file)
