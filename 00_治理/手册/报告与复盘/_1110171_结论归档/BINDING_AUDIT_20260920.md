# BINDING_AUDIT_20260920 — 用权威源尺寸复核并纠正两把皮肤的贴图绑定（task-85）

- 任务：**task-85**（chain-auditor 完成只读取证后容量耗尽未写盘，**env-auditor 接手完成**）。
- 写作用域（严格遵守）：`1110177/effects.json`、`1110171/effects.json` 的**贴图绑定字段** + 本报告 + `BINDING_AUDIT_20260920.json`。**未碰** `viewer.json`/adapter/`viewer.js`/`board.html`/`neox_material.json`/其它皮肤。
- 源级依据：`E:\mrzh\res.npk` **entry 8858**（80,369,252 B）的清单 `名字 → {checksum=md5(原始资产), has_alpha, img_size}`；**本人自己重解 = 529,268 条**（chain-auditor 口径一致；差 102 条是边界行）。

---

## ① 判定结果总览

| 皮肤 | 撤回候选 | `renderable_by_adapter` 变化 | effects.json sha16 | 字节 |
|---|---|---|---|---|
| **1110177** | **6 条**（节点 19 / 34 / 37 / 44 / 60 / 61） | **11 → 5** | `13AAA1B05B9AD770` → **`5403931C1671ECBE`** | 627,850 → 645,569 |
| **1110171** | **3 条**（节点 26 / 34 / 43） | **11 → 8** | `42DF44D9B54A3C2C` → **`B13010971B2327D7`** | 198,283 → 210,724 |

- 撤回动作（逐节点）：`texture_status = "REJECTED_source_dims_mismatch(fail_closed,不顶替)"`、`renderable_by_adapter = false`、`texture_candidate = null`、`texture_binding = null`，**原值完整存入 `rejected_candidates[]`**（含声明名、候选、候选 dims、源 dims、源 checksum、源 has_alpha、原 binding/status、原因）。
- **canonical diff 守卫**：改动字段 1110177 = 459 个 / 1110171 = 314 个，**越界字段 0 个**（守卫先算 diff，越界即拒写；本次因第一次 allowlist 过窄而被自己的守卫拦下并修正后重写）。
- 备份：`effects.json.bak_task85_20260920_004714`（两份，`copy2`）。

---

## ② 权威源尺寸表（逐候选节点，两皮肤全量）

### 1110177（11 个带候选节点）

| 节点 | 声明名 | 清单 checksum | 源尺寸 | has_alpha | 候选图 | 候选 dims | 判定 |
|---|---|---|---|---|---|---|---|
| [7] H_p_闪电 | `lightning07_cs.spr` | 帧 `lightning07_cs.tga` = `2a781daa…` | 512×512 | 1 | `lightning07_cs__atlas207659.png` | 512×512 | ✅ 图集（保留） |
| [19] H_p_星点_02 | `glow_16_yh_djs.tga` | `f9d3f01663e6…` | **128×128** | 1 | `glow_16_yh_djs__7ce99117.png` | 256×256 | ❌ **撤回** |
| [30] H_ shandian01_1_1 | `lightning_01.spr` | 帧 `lightning_01.tga` **清单无此项** | — | — | `lightning_01__atlas207671.png` | 512×512 | ✅ 图集（无源证据，保留） |
| [34] M_g_glow_an | `glow_01.tga` | `6a62146a607a…` | **128×128** | 1 | `glow_01__13211b02.png` | 256×256 | ❌ **撤回** |
| [37] H_鬼火_lizi_1 | `dian_12.tga` | `e5f1db051e8b…` | **128×128** | 1 | `dian_12__7240b831.png` | 256×256 | ❌ **撤回** |
| [38] M_lizi_闪电_01 | `shandian_05_yh_djs.spr` | 帧 `shandian_05_yh_djs.tga` = `295faf49…` | 256×256 | 1 | `shandian_05_yh_djs__atlas207712.png` | 256×256 | ✅ 图集（保留） |
| [44] H_g_glow地_an | `glow_01.tga` | `6a62146a607a…` | **128×128** | 1 | `glow_01__13211b02.png` | 256×256 | ❌ **撤回** |
| [60] L_p_星点_02 | `glow_16_yh_djs.tga` | `f9d3f01663e6…` | **128×128** | 1 | `glow_16_yh_djs__7ce99117.png` | 256×256 | ❌ **撤回** |
| [61] H_公告板_爆闪2 | `glow_01.tga` | `6a62146a607a…` | **128×128** | 1 | `glow_01__13211b02.png` | 256×256 | ❌ **撤回** |
| [83] H_p_烟雾_02 | `smoke25.spr` | 帧 `smoke25.tga` = `7ad3294f…` | 512×512 | 1 | `smoke25__atlas208478.png` | 512×512 | ✅ 图集（保留） |
| [88] H_鬼火_星点_1 | `tex_special_fangkuai_tp52.spr` | 帧 `tex_special_fangkuai_tp52.tga` = `ba7917b6…` | 256×256 | 1 | `tex_special_fangkuai_tp52__atlas211384.png` | 256×256 | ✅ 图集（保留） |

### 1110171（11 个带候选节点）

| 节点 | 声明名 | 清单 checksum | 源尺寸 | has_alpha | 候选图 | 候选 dims | 判定 |
|---|---|---|---|---|---|---|---|
| [23] H_星点粒子 | `tex_glow_tp07_02.spr` | 清单无 `.spr` 项 | — | — | `tex_glow_tp07_02__atlas207414.png` | 256×256 | ✅ 图集（保留） |
| [24] H_星点粒子_3 | `star_xing_02_tp165.tga` | `f1524e26d098…` | 256×256 | 1 | `bf887707a4496fe3.png` | 256×256 | ⚠ dims 一致，**仍非源级**（登记不绑定） |
| [26] L_p_光刺_01 | `tex_glow_ray_tp60_01.tga` | （见 `bindings_review_20260920.dims_exact_pool_rerun`） | **256×256** | 1 | `a74377f1fba7defe.png` | 128×128 | ❌ **撤回** |
| [27] M_g_光晕暗_01 | `glow40_tp30.tga` | — | 128×128 | 1 | `c63f1436228725ad.png` | 128×128 | ⚠ dims 一致，仍非源级 |
| [28] M_g_光晕亮_01 | `glow_gyun_01_smg.tga` | — | 256×256 | 1 | `3eb4edfb85276f07.png` | 256×256 | ⚠ dims 一致，仍非源级 |
| [29] H_p_光圈01 | `caihong_06_jh_djs.tga` | 清单无此项 | — | — | `07ebe6c048506c81.png` | 128×128 | 仍 unresolved（无源尺寸可比） |
| [34] L_p_光刺_02 | `tex_glow_ray_tp60_01.tga` | — | **256×256** | 1 | `a74377f1fba7defe.png` | 128×128 | ❌ **撤回** |
| [35] M_g_光晕暗_02 | `glow40_tp30.tga` | — | 128×128 | 1 | `c63f1436228725ad.png` | 128×128 | ⚠ dims 一致，仍非源级 |
| [36] M_g_光晕亮_02 | `glow_gyun_01_smg.tga` | — | 256×256 | 1 | `3eb4edfb85276f07.png` | 256×256 | ⚠ dims 一致，仍非源级 |
| [37] H_p_光圈02 | `caihong_06_jh_djs.tga` | 清单无此项 | — | — | `07ebe6c048506c81.png` | 128×128 | 仍 unresolved |
| [43] H_星点粒子_1 | `glow_tp17_04.tga` | — | **128×128** | 1 | `700bf8b7fbacf8f7.png` | 256×256 | ❌ **撤回** |

---

## ③ 5 张 `.spr` 真图集独立校验（用清单源尺寸）

| `.spr` | 帧名 | `.spr` 声明表 | 清单源尺寸 | 绑定图集 dims | 结论 |
|---|---|---|---|---|---|
| `lightning07_cs.spr` | `lightning07_cs.tga` | 512×512 | **512×512**（`2a781daa…`） | 512×512 | ✅ **一致** |
| `lightning_01.spr` | `lightning_01.tga` | 512×512 | **清单无此项** | 512×512 | ⚪ **无源证据**（不给结论，未撤回） |
| `shandian_05_yh_djs.spr` | `shandian_05_yh_djs.tga` | 256×256 | **256×256**（`295faf49…`） | 256×256 | ✅ **一致** |
| `smoke25.spr` | `smoke25.tga` | 512×512 | **512×512**（`7ad3294f…`） | 512×512 | ✅ **一致** |
| `tex_special_fangkuai_tp52.spr` | `tex_special_fangkuai_tp52.tga` | 256×256 | **256×256**（`ba7917b6…`） | 256×256 | ✅ **一致** |

⇒ **4/5 一致，1/5 清单无此项（不是"不一致"）**；**没有任何一张图集被源尺寸打脸**。校验结果已写进对应节点的 `atlas_provenance.source_dims_check`。

---

## ④ 按源尺寸硬过滤重跑候选（只允许 dims 精确相等）

池 = `_sfx_029/texture_pool`(875) + `effect_pool_union/dds`(1,229) + `effect_01.gpk` 全表匿名 DDS(7,501) = **8,730 张**（去重前）。

| 声明名 | 源尺寸 | 池内 dims 精确候选数 | 结论 |
|---|---|---|---|
| `glow_01.tga` / `dian_12.tga` / `glow_16_yh_djs.tga` / `glow_tp17_04.tga` / `glow40_tp30.tga` | 128×128 | **1,565** | 非唯一 ⇒ 只登记 top-N，**不绑定** |
| `star_xing_02_tp165.tga` / `glow_gyun_01_smg.tga` / `tex_glow_ray_tp60_01.tga` | 256×256 | **3,317** | 非唯一 ⇒ 只登记 top-N，**不绑定** |

⇒ **没有任何一条能凭"源尺寸"唯一化**（尺寸只能排除，不能指认）。top-N 已登记在 `bindings_review_20260920.dims_exact_pool_rerun`（每个名字 5 条，含来源池与文件名），**未写入任何绑定**。`.mtg` 的 72 条声明名同样只登记（未改 Model 渲染）。

---

## ⑤ 逐处改动与 canonical diff 守卫

**1110177**（改 459 个叶子字段，全部在允许集合内）：
- 节点 19/34/37/44/60/61：`texture_candidate` 6 处清空、`texture_binding` 6 处清空、`texture_status` 6 处改 REJECTED、`renderable_by_adapter` 6 处 → false、`rejected_candidates` 6 个新数组（每个 11 字段）。
- 5 个 `.spr` 节点：`atlas_provenance.source_dims_check` 新增（5 字段）。
- 顶层：`texture_binding_status` 文案更新；`texture_selection` 中 3 个被撤回名字补 `bound=false` + `rejected_reason` + `source_dims`；新增 `bindings_review_20260920`（复审块）。

**1110171**（改 314 个叶子字段）：
- 节点 26/34/43：同上四字段 + `rejected_candidates` 3 个。
- 节点 23：`atlas_provenance.source_dims_check` 新增。
- 顶层：`texture_binding_status` 文案更新；`texture_selection` 中被撤回名字标注；新增 `bindings_review_20260920`。

**守卫规则**：允许路径 = `nodes[i].{texture_candidate,texture_binding,texture_status,renderable_by_adapter,rejected_candidates,atlas_provenance,spr_*}` 与顶层 `{texture_binding_status,texture_selection,bindings_review_20260920}` 及其子路径；**越界字段 0 个**（两次写入各自校验）；两份文件写后用 `json.load` 复读通过。

---

## ⑥ 诚实声明与附带登记

- **没有顶替、没有编造**：9 条撤回全部基于"清单 `img_size` ≠ 候选图实际 dims"的源级反证；**未对任何撤回项填入替代候选**；`texture_candidate` 一律清空而不是换一个。
- **`glow_04_tp29.tga`（清单 `256×256`、`has_alpha=0` 不透明）**：在 1110177 里只作为**声明名**出现在 node[45] `M_g_爆点`，**没有绑定任何候选** ⇒ 本轮**不撤回**，仅登记"源为不透明贴图，若当 alpha 用会错"。1110171 未使用该名。
- **仍 unresolved**：`caihong_06_jh_djs.tga`（清单无此项）、`lightning_01.tga`（清单无此项）、以及所有"dims 一致但非源级"的 1110171 候选（5 条，仍标 `candidate_content_feature_not_source`）。
- **任务板登记**：task-85 的 owner 仍显示 `chain-auditor`（我无权 `reassign`，`claim` 被拒），**Lead 需把 owner 改到我名下**；工作已按 Lead 交接完成。

## ⑦ 复现

| 脚本（`%TEMP%`） | 作用 |
|---|---|
| `BA_analyze.py` | 自解清单 + 两皮肤逐候选源尺寸/候选 dims 对照 + 5 `.spr` 校验 + 池 dims 精确过滤 |
| `BA_apply.py` | 备份 → 撤回 → 图集校验入档 → canonical diff 守卫 → 写盘 |
| `BA_deliver.py` | 组装本报告对应 JSON + 写后复核 |
