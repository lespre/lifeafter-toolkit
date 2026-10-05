# domains/

每个业务域拥有：builder / rules / schema / README / evidence references。
产物统一写入 `artifacts/active/<domain>/`（**只有 active**）。
builder 只是**包装器**：复用 `tools/` 下既有实现，不重写算法。

| domain | active artifact |
|---|---|
| item | `artifacts/active/item/ITEM_MASTER.jsonl` |
| fashion | `artifacts/active/fashion/FASHION_IDENTITY_STATE.json`（不生成假 resolved） |
| weapon_skin | `artifacts/active/weapon_skin/WEAPON_SKIN_RESOLVED.jsonl` |
| lottery | `artifacts/active/lottery/LOTTERY_POOL.jsonl` + `LOTTERY_REWARD_TARGETS.jsonl`（永久分层） |
