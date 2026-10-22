# 子特效拆包与合并报告（task-72）—— js_04 / zs_01

## 0. 定位与 pin

| 皮肤 | 子 sfx | 容器 | row | bytes | sha16 | 节点 |
|---|---|---|---|---|---|---|
| 1110177 | `effect\fx\weapon\skin\skin_2003_029\fx_skin_2003_029_js_04.sfx` | `effect_01.gpk` | 38437 | 3938 | `C602AD795A764092` | 2 |
| 1110171 | `effect\fx\weapon\skin\skin_1003_010\fx_skin_1003_010_zs_01.sfx` | `effect_01.gpk` | 37321 | 15908 | `62A127F0BEDC3515` | 4 |

| 皮肤 | effects.json 改前 | 改后 | 字节 | 备份 | 节点数 | renderable_by_adapter |
|---|---|---|---|---|---|---|
| 1110177 | `F3C0623DC3CF684E` | **`535909555A2599A6`** | 575605 → 578144 | `effects.json.bak_subsfx_20260919_222650` | 89 → 91 | **11 → 11** |
| 1110171 | `1742FA1FC56C3093` | **`DE667C26A99B7DEC`** | 130095 → 140218 | `effects.json.bak_subsfx_20260919_222650` | 44 → 48 | **11 → 11** |

自证：**既有节点零改动**（按位置 canonical JSON 逐字节比对）= 1110177 True / 1110171 True；`json.load` 可读通。

## 1. 节点树逐条

### 1110177 ← `fx_skin_2003_029_js_04.sfx`（row 38437，sha16 `C602AD795A764092`）
| 节点 | tag | FxStartTime | FxLifeSpan | FxIgnore | rate | 贴图声明 | emit 轨 | ModelName |
|---|---|---|---|---|---|---|---|---|
| L_空特效 | Dummy | 0.000 | 0.500 | FALSE | None | [] | 1 | — |
| L_模型特效 | Model | 0.000 | 1.000 | FALSE | None | [] | 1 | `effect\mesh\weapon\skin\skin_2003_029\mod_skin_2003_029_dm_shangdian_07_djs.gim` |

### 1110171 ← `fx_skin_1003_010_zs_01.sfx`（row 37321，sha16 `62A127F0BEDC3515`）
| 节点 | tag | FxStartTime | FxLifeSpan | FxIgnore | rate | 贴图声明 | emit 轨 | ModelName |
|---|---|---|---|---|---|---|---|---|
| L_glow_03 | Sprite | 0.000 | 1.000 | TRUE | None | ["effect\\textures\\glow\\glow25.tga"] | 4 | — |
| L_glow_03_2 | Sprite | 0.000 | 1.800 | TRUE | None | ["effect\\textures\\glow\\glow_01.tga"] | 4 | — |
| L_glow_03_1 | Sprite | 0.000 | 1.000 | TRUE | None | ["effect\\textures\\glow\\tex_glow_ray_tp60_01.tga"] | 4 | — |
| L_p_光刺_01_1 | ParticleSystem | 0.000 | 0.100 | FALSE | 3.000 | ["effect\\textures\\glow\\tex_glow_ray_tp60_01.tga"] | 16 | — |

## 2. 贴图可达性（逐条）

- **`.spr` 声明数 = 0** ⇒ **没有任何 `.spr` 可走兄弟图集通道**，本轮**未导出任何 PNG**（`sfx/sub/` 未创建：没有可导的真图集）。
- `effect\textures\glow\glow25.tga` → **unresolved**（`.tga`，源名轴无直证；按纪律**不顶替**）｜出现于 ["1110171:L_glow_03"]
- `effect\textures\glow\glow_01.tga` → **unresolved**（`.tga`，源名轴无直证；按纪律**不顶替**）｜出现于 ["1110171:L_glow_03_2"]
- `effect\textures\glow\tex_glow_ray_tp60_01.tga` → **unresolved**（`.tga`，源名轴无直证；按纪律**不顶替**）｜出现于 ["1110171:L_glow_03_1", "1110171:L_p_光刺_01_1"]

## 3. 合并结果（新增节点）

### 1110177 新增 ["L_空特效__sub", "L_模型特效__sub"]
- `parent_node` = ["M_ParticleRes"]（父 ParticleRes；1110171 有 一个）
- 带 `from_sub_sfx=true`、`source_sfx_id`（容器:row）、`sub_sfx_path/sha16`、`fxIgnore`(+provenance)、`emit` 全子轨、`start/life/pos_offset/render_bias/transparent_mode/track_type/dir_type`、`texture_status`。
- **fail-closed**：子节点贴图 unresolved ⇒ `renderable_by_adapter=false` + `sub_render_reason`；**两把皮肤 renderable 计数均未变（11 → 11）** ⇒ 这是一次**如实登记**，没有引入新渲染。
### 1110171 新增 ["L_glow_03", "L_glow_03_2", "L_glow_03_1", "L_p_光刺_01_1"]
- `parent_node` = ["L_ParticleRes", "L_ParticleRes_1"]（父 ParticleRes；1110171 有 两个）
- 带 `from_sub_sfx=true`、`source_sfx_id`（容器:row）、`sub_sfx_path/sha16`、`fxIgnore`(+provenance)、`emit` 全子轨、`start/life/pos_offset/render_bias/transparent_mode/track_type/dir_type`、`texture_status`。
- **fail-closed**：子节点贴图 unresolved ⇒ `renderable_by_adapter=false` + `sub_render_reason`；**两把皮肤 renderable 计数均未变（11 → 11）** ⇒ 这是一次**如实登记**，没有引入新渲染。
- 1110177 的 `L_模型特效__sub`：`ModelName = mod_skin_2003_029_dm_shangdian_07_djs.gim` ⇒ **该 GLB 早已在 `1110177/sfx/` 存在**（task-61 的 24 个之一），故 `model_glb = sfx/mod_skin_2003_029_dm_shangdian_07_djs.glb` + `model_glb_state="existing_glb"`；按 task-72 的 fail-closed 规则仍置 `renderable_by_adapter=false`，但**它与现有 26 个无贴图 Model 同类（A 类自发光）**，若按主皮肤规则即可渲 —— 该一处由 lead 裁定，报告如实两种口径。

## 4. 自引用那条

- 1110177 dg 源里的 `H_ParticleRes` → `...\fx_skin_2003_029_daoguang_02.sfx` = **该文件自身** ⇒ 按 task 要求**不递归展开**，仅登记（本文档 §0 的 dg 行已有其容器/row/sha16 = `gres\0057.gpk#32153` / `9F4FE3A6AD3F8851`）。

## 5. 已证 / 未证 / 未做

**已证**：两个子 sfx 按名命中（`effect_01.gpk` row 38437 / 37321，3,938 / 15,908 B，sha16 `C602AD795A764092` / `62A127F0BEDC3515`）；节点树 2 / 4 个（js_04: Dummy+Model；zs_01: 3 Sprite + 1 PS）；`.spr` 声明 **0** ⇒ 无真图集；三张 `.tga` 全部 unresolved；既有节点零改动；两皮肤 renderable 计数不变。
**未证**：`glow25.tga` / `glow_01.tga` / `tex_glow_ray_tp60_01.tga` 的**内容候选**未做匹配（按纪律不顶替）；子 sfx 里 `L_p_光刺_01_1`(rate 3) 的贴图同样 unresolved ⇒ 未能驱动。
**未做**：未开浏览器（验收另派）；未导出任何 PNG/GLB（无可导出的真图集；GLB 已存在）；未改 adapter/viewer.json/viewer.js/board/neox_material.json。**没有顶替、没有编造。**
