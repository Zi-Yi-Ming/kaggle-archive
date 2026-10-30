#!/bin/bash
# Orchestrator: wait for probe completion, push validation kernel, wait for it, dump logs.
set -u
TS() { date +%H:%M:%S; }

echo "[$(TS)] waiting for arc2-env-probe to leave queue/finish..."
for i in $(seq 1 120); do
  S=$(kaggle kernels status ziyiming/arc2-env-probe 2>&1)
  echo "[$(TS)] probe: $S"
  echo "$S" | grep -qi "complete\|error\|cancel" && break
  sleep 60
done

echo "[$(TS)] === probe logs (tail) ==="
kaggle kernels logs ziyiming/arc2-env-probe 2>&1 | tail -40

echo "[$(TS)] pushing validation kernel..."
for i in $(seq 1 10); do
  OUT=$(kaggle kernels push -p /tmp/arcwork/k_arc2-nvarc-v38-evalval 2>&1)
  echo "[$(TS)] push: $OUT"
  echo "$OUT" | grep -qi "successfully pushed" && break
  sleep 120
done

echo "[$(TS)] === waiting for validation kernel ==="
for i in $(seq 1 180); do
  S=$(kaggle kernels status ziyiming/arc2-nvarc-v38-evalval 2>&1)
  echo "[$(TS)] evalval: $S"
  echo "$S" | grep -qi "complete\|error\|cancel" && break
  sleep 60
done

echo "[$(TS)] === validation logs (tail) ==="
kaggle kernels logs ziyiming/arc2-nvarc-v38-evalval 2>&1 | tail -60

echo "[$(TS)] === fetching submission output ==="
mkdir -p /tmp/arcwork/evalval_out
kaggle kernels output ziyiming/arc2-nvarc-v38-evalval -p /tmp/arcwork/evalval_out 2>&1 | tail -3
ls -la /tmp/arcwork/evalval_out
echo "[$(TS)] ORCHESTRATOR DONE"
