# domains/weapon_skin

- Active：`artifacts/active/weapon_skin/WEAPON_SKIN_RESOLVED.jsonl`（**v0.2**，115 行）
- v0.1 已归档：`artifacts/historical/weapon_skin/v01/`（不删）
- 三 binding 全 verified（runtime row / business / name）；1110185 / 1110186 = no_main_row
- **canonical 状态字段（v1.3.1 起）**
  - `listing_status` ∈ {verified_listed, verified_unlisted, unresolved}；当前**只支持 unresolved**
    （证据：同快照 sale/shop/exchange 全 absent ⇒ 不伪造分类），明细见 `STATUS_VOCAB.json`
  - `name_status` ∈ {verified, unresolved, unsafe}；verified 必须 `name_evidence_type = verified_runtime_ui_lookup`
  - `sale_ts` 只是时间戳（`sale_ts_role` 已标注）；`release_state` 仅为 legacy 板旧派生值，**不是** canonical
- 投影/前端：`weapon_skin_active` 走 canonical 字段；`board.html` 皮肤渲染器数据驱动（不再按旧板 id 硬编码）
- **不重新调查定位链**
