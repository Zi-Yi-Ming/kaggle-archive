"""比对 Kernel B(resume)与 Kernel C(continuous)的最终状态是否等价。

EXP-018 优先级 2 的验收:resume 之后 trajectories 必须与一口气跑完的基线一致,
且代码 hash 必须统一。

口径说明(重要):
  B 的 epoch 循环从 ckpt 的 epoch_done 开始,所以 B 自己记录下来的
  `epoch_losses` / `loader_order_hashes` 只包含它实际跑过的 epoch;
  C 从 epoch 0 跑起,记录的是全量。两者不能直接比列表,必须按 B 的起点对齐:
      B.epoch_losses          == C.epoch_losses[start_epoch:]
      B.loader_order_hashes   ⊆ C.loader_order_hashes(逐 key 相等)
  另外 B 会从 ckpt 合并回 `steps_per_epoch`,所以这个字段两者都应是全量。

判定项:
  - code_sha_rsna_v3 一致(统一 hash,防「A/B/C 代码不同」再次发生)
  - global_step / epoch_done 一致
  - 参数逐位一致(param_hash_final)
  - optimizer 动量状态一致(optimizer_state_hash)
  - B 跑过的每个 epoch 的 loss 一致
  - B 跑过的每个 epoch 的 DataLoader order hash 一致(证明 shuffle 序列真的相同,
    而不是「都是随机所以等价」)
  - steps_per_epoch 一致
  - RNG 状态键齐全

用法:
  python scripts/compare_resume_bc.py <b_result.json> <c_result.json>
"""
import json
import sys


def load(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def main():
    b = load(sys.argv[1])
    c = load(sys.argv[2])

    # B 的起点 = B 的总 epoch_done - B 实际跑的 epoch 数
    b_ran = len(b.get("epoch_losses") or [])
    b_epochs = int(b["epoch_done"])
    start_epoch = b_epochs - b_ran

    checks = {}
    checks["code_hash_unified"] = b["code_sha_rsna_v3"] == c["code_sha_rsna_v3"]
    checks["code_sha"] = b["code_sha_rsna_v3"]
    checks["global_step_equal"] = b["global_step"] == c["global_step"]
    checks["epoch_done_equal"] = b["epoch_done"] == c["epoch_done"]
    checks["start_epoch"] = start_epoch

    checks["param_hash_equal"] = b["param_hash_final"] == c["param_hash_final"]
    checks["param_hash_B"] = b["param_hash_final"]
    checks["param_hash_C"] = c["param_hash_final"]

    checks["optimizer_hash_equal"] = b["optimizer_state_hash"] == c["optimizer_state_hash"]
    checks["optimizer_hash_B"] = b["optimizer_state_hash"]
    checks["optimizer_hash_C"] = c["optimizer_state_hash"]

    # 只比 B 跑过的那几段 loss
    c_losses = c.get("epoch_losses") or []
    c_tail = c_losses[start_epoch:] if start_epoch >= 0 else []
    checks["epoch_losses_equal"] = (b.get("epoch_losses") or []) == c_tail
    checks["epoch_losses_B"] = b.get("epoch_losses")
    checks["epoch_losses_C_tail"] = c_tail
    checks["epoch_losses_C_full"] = c_losses

    # order hash:B 的 key 必须是 C 的子集,且逐 key 相等
    bo = b.get("loader_order_hashes") or {}
    co = c.get("loader_order_hashes") or {}
    bk, ck = sorted(bo.keys()), sorted(co.keys())
    per_epoch = {k: (bo[k].get("hash") == co.get(k, {}).get("hash")) for k in bk}
    checks["order_keys_B"] = bk
    checks["order_keys_C"] = ck
    checks["order_hash_per_epoch_equal"] = per_epoch
    checks["order_all_equal"] = bool(bk) and all(per_epoch.values())

    checks["steps_per_epoch_equal"] = (
        (b.get("steps_per_epoch") or {}) == (c.get("steps_per_epoch") or {}))
    checks["steps_per_epoch_B"] = b.get("steps_per_epoch")
    checks["steps_per_epoch_C"] = c.get("steps_per_epoch")

    checks["rng_keys_B"] = b.get("rng_keys")
    checks["rng_keys_C"] = c.get("rng_keys")
    checks["rng_keys_complete"] = (
        set(b.get("rng_keys") or []) == {"python", "numpy", "torch_cpu", "torch_cuda"}
        and set(c.get("rng_keys") or []) == {"python", "numpy", "torch_cpu", "torch_cuda"})

    critical = ["code_hash_unified", "global_step_equal", "epoch_done_equal",
                "param_hash_equal", "optimizer_hash_equal", "epoch_losses_equal",
                "order_all_equal", "steps_per_epoch_equal", "rng_keys_complete"]
    passed = all(checks[k] for k in critical)
    checks["failed_items"] = [k for k in critical if not checks[k]]
    checks["RESUME_EQUIVALENCE"] = "PASS" if passed else "FAIL"

    print(json.dumps(checks, ensure_ascii=False, indent=2))
    print("RESUME_EQUIVALENCE =", checks["RESUME_EQUIVALENCE"])
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
