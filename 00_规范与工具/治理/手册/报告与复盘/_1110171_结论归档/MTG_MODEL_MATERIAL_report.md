# MTG_MODEL_MATERIAL_report

> task-75 · 写作用域：`weapon_skin_sfx_adapter.js` + `1110177/effects.json`（只新增 `mtg_*`）+ 本报告
> **阶段一（只读取证）**：本文件先只含这一节；阶段二/三（数据侧/adapter/A-B 测量）随后追加。

## 0. 决定性小问题（GLB 事实）—— **已证**

| 项 | 结果 | 说明 |
|---|---|---|
| GLB 总数 | **40** | `1110177/sfx/**/*.glb`（含 `dg/`） |
| `POSITION` | **40 / 40** | **有** ✓ |
| `NORMAL` | **40 / 40** | **有** ✓ |
| `TEXCOORD_0` | **40 / 40** | **有** ✓ |
| `COLOR_0` | **0 / 40** | **全部没有** ✗ |
| 内嵌图像 image | **0 / 40** ✗ | 无内嵌贴图 |
| 材质名 | `MAT_s0`×24 · `MAT_fx`×16 | 每 GLB 单材质（无贴图） |
| 顶点/图元合计 | verts **4,574** · prims **40** | 特效面片级几何 |

**⇒ 结论**：**40/40 GLB 都没有顶点色 `COLOR_0`** ✗ ⇒ **"顶点色 + 自发光"路线不成立**；
唯一有源依据的上色办法 = **`u_emissivecolor`（源色）+ `u_emissive_highlight_intensity`（源强度）** ✓。
UV/法线齐全 ✓（将来有贴图直证可直接接），但**无任何贴图直证** ⇒ **渲出来仍不是成品外观**（如实登记）。

## 1. 逐 Model 节点（42 = 34 有 .mtg 同族 + 8 无）

| # | 节点名 | stem | shader | macros | 可用驱动参数（名=源值） | GLB |
|---|---|---|---|---|---|---|
| 1 | L_模型_科技01 | `mod_skin_2003_029_mz_kj01_djs` | shader\uber_fx_common | USE_DISSOLVE,USE_DISSOLVE_POLAR_UV,USE_MAIN_POLAR_UV,USE | u_emissive_highlight_intensity=60 · u_dissolve_amount=0.63 · u_mask_power=2 · u_mask_intensity=4 · u_maintex_speed_y=-1 | NORMAL,POSITION,TEXCOORD_0 无C |
| 2 | L_模型特效_01 | `mod_skin_2003_029_mz_shandian01_djs` | shader\uber_fx_common | USE_DISSOLVE,USE_FRESNEL,USE_MAIN_DISTORT,USE_MASK01 | u_emissive_highlight_intensity=30 · u_emissive_power=1.6 · u_dissolve_amount=0.52 · u_distort01_speed_y=0.5 | NORMAL,POSITION,TEXCOORD_0 无C |
| 3 | H_模型纹理 | `mod_skin_2003_029_mz_ks01_djs` | shader\uber_mask_rim_diss.fx | DISSOLVE_ENABLE,DISTORT_ENABLE,EDGEDISSOLVE_ENABLE,MASK_ | （无） | NORMAL,POSITION,TEXCOORD_0 无C |
| 4 | H_模型核心电小_3 | `mod_skin_2003_029_mz_sd01_djs` | shader\uber_fx_common | USE_DISSOLVE,USE_FRESNEL,USE_MAIN_DISTORT,USE_MASK01,USE | u_emissivecolor=[0.4196, 0.2902, 1.0, 1.0] · u_emissive_highlight_intensity=50 · u_dissolve_amount=0.63 · u_mask_intensity=2 · u_distort01_speed_y=0.5 | NORMAL,POSITION,TEXCOORD_0 无C |
| 5 | M_模型核心电小_4 | `mod_skin_2003_029_mz_shandian03_djs` | shader\uber_fx_common | USE_DISSOLVE,USE_FRESNEL,USE_MAIN_DISTORT,USE_MASK01 | u_emissive_highlight_intensity=20 · u_emissive_power=2 · u_dissolve_amount=0.63 · u_distort01_speed_y=0.5 | NORMAL,POSITION,TEXCOORD_0 无C |
| 6 | H_模型核心电小_5 | `mod_skin_2003_029_mz_shandian02_djs` | shader\uber_fx_common | USE_DISSOLVE,USE_FRESNEL,USE_MAIN_DISTORT,USE_MASK01,USE | u_emissive_highlight_intensity=20 · u_emissive_power=2 · u_dissolve_amount=0.63 · u_distort01_speed_y=0.5 | NORMAL,POSITION,TEXCOORD_0 无C |
| 7 | L_模型_科技03 | `mod_skin_2003_029_mz_kj03_djs` | shader\uber_fx_common | USE_DISSOLVE,USE_DISSOLVE_POLAR_UV,USE_MAIN_POLAR_UV,USE | u_emissive_highlight_intensity=10 · u_dissolve_amount=0.67 · u_mask_power=1.5 · u_maintex_speed_y=-2 | NORMAL,POSITION,TEXCOORD_0 无C |
| 8 | L_模型火_1 | `mod_skin_2003_029_dm_qiliu_20_djs` | shader\uber_fx_common | USE_MAIN_DISTORT,USE_MASK01 | u_emissivecolor=[1.0, 0.3451, 0.0, 0.0] · u_emissive_highlight_intensity=1.6 · u_maintex_speed_y=0.25 · u_distort01_speed_y=0.1 | NORMAL,POSITION,TEXCOORD_0 无C |
| 9 | H_模型红 | `mod_skin_2003_029_14_hjl_djs` | shader\uber_fx_common | USE_MAIN_DISTORT,USE_MASK01 | u_emissivecolor=[0.1647, 0.0, 1.0, 0.0] · u_emissive_highlight_intensity=2 · u_maintex_speed_y=0.6 · u_distort01_speed_y=-0.1 | NORMAL,POSITION,TEXCOORD_0 无C |
| 10 | M_m_流动_科技_1_1_1 | `mod_skin_2003_029_dm_qiliu_12_djs` | shader\uber_fx_common | USE_DISSOLVE,USE_MASK01,USE_MASK02 | u_emissivecolor=[1.0, 0.8235, 0.4235, 1.0] · u_emissive_highlight_intensity=10 · u_dissolve_amount=0.64 · u_mask_power=2 · u_mask_intensity=5 · u_maintex_speed_y=-0.2 | NORMAL,POSITION,TEXCOORD_0 无C |
| 11 | M_模型喇叭 | `mod_skin_2003_029_dm_qiliu_23_djs` | shader\uber_fx_common | USE_MAIN_DISTORT,USE_MASK01 | u_emissivecolor=[1.0, 0.8275, 0.3608, 1.0] · u_emissive_highlight_intensity=2 · u_mask_power=2 · u_maintex_speed_y=0.15 · u_distort01_speed_y=0.5 | NORMAL,POSITION,TEXCOORD_0 无C |
| 12 | M_m_流动_2 | `mod_skin_2003_029_dm_shangdian_05_djs` | shader\uber_fx_common | USE_MAIN_DISTORT,USE_MASK01 | u_emissivecolor=[0.6353, 0.7137, 1.0, 1.0] · u_emissive_highlight_intensity=3 · u_maintex_speed_y=-0.5 | NORMAL,POSITION,TEXCOORD_0 无C |
| 13 | M_模型枪_1 | `mod_skin_2003_029_dm_wuqi_01_djs` | shader\uber_fx_common | USE_DISSOLVE,USE_MASK01 | u_emissivecolor=[1.0, 0.8745, 0.6431, 1.0] · u_emissive_highlight_intensity=20 · u_emissive_power=0.5 · u_dissolve_amount=0.48 | NORMAL,POSITION,TEXCOORD_0 无C |
| 14 | L_m_扩散_科技_1_2 | `mod_skin_2003_029_dm_qiliu_09_djs` | shader\uber_fx_common | USE_DISSOLVE,USE_MASK01,USE_MASK02 | u_emissivecolor=[1.0, 0.8235, 0.4235, 1.0] · u_emissive_highlight_intensity=10 · u_dissolve_amount=0.72 · u_mask_intensity=5 · u_maintex_speed_y=-0.2 | NORMAL,POSITION,TEXCOORD_0 无C |
| 15 | M_模型特效_2_1 | `mod_skin_2003_029_56_hjl_djs` | shader\uber_fx_common | USE_DISSOLVE,USE_FRESNEL,USE_MAIN_DISTORT,USE_MASK01 | u_emissivecolor=[0.0824, 0.0471, 0.4, 1.0] · u_emissive_highlight_intensity=5 · u_emissive_power=1.5 · u_dissolve_amount=0 · u_maintex_speed_y=-0.3 · u_distort01_speed_y=-1 | NORMAL,POSITION,TEXCOORD_0 无C |
| 16 | L_模型特效_1 | `mod_skin_2003_029_dm_qiliu_06_djs` | shader\uber_fx_common | ADD_COLORTEX,USE_DISSOLVE,USE_FRESNEL,USE_MAIN_DISTORT,U | u_emissivecolor=[1.0, 0.8235, 0.3451, 1.0] · u_emissive_highlight_intensity=2 · u_dissolve_amount=0 · u_mask_power=1.5 · u_distort01_speed_y=-0.6 | NORMAL,POSITION,TEXCOORD_0 无C |
| 17 | L_模型特效 | `mod_skin_2003_029_dm_shangdian_07_djs` | shader\uber_fx_common | ADD_COLORTEX,USE_DISSOLVE,USE_FRESNEL,USE_MAIN_DISTORT,U | u_emissivecolor=[1.0, 0.6863, 0.2784, 1.0] · u_emissive_highlight_intensity=50 · u_emissive_power=2 · u_dissolve_amount=0 · u_mask_power=2 · u_maintex_speed_y=0.5 · u_distort01_speed_y=-0.4 | NORMAL,POSITION,TEXCOORD_0 无C |
| 18 | H_模型特效_3 | `mod_skin_2003_029_dm_shangdian_07_djs` | shader\uber_fx_common | ADD_COLORTEX,USE_DISSOLVE,USE_FRESNEL,USE_MAIN_DISTORT,U | u_emissivecolor=[1.0, 0.6863, 0.2784, 1.0] · u_emissive_highlight_intensity=50 · u_emissive_power=2 · u_dissolve_amount=0 · u_mask_power=2 · u_maintex_speed_y=0.5 · u_distort01_speed_y=-0.4 | NORMAL,POSITION,TEXCOORD_0 无C |
| 19 | H_模型bian_glow | `mod_skin_2003_029_dg_wl_01_djs` | shader\uber_fx_common | USE_FRESNEL,USE_MASK01 | u_emissive_highlight_intensity=3 · u_mask_power=1.2 | NORMAL,POSITION,TEXCOORD_0 无C |
| 20 | M_模型_an_1 | `mod_skin_2003_029_dg_wl_02_djs` | shader\uber_fx_common | USE_DISSOLVE,USE_MASK01 | （无） | NORMAL,POSITION,TEXCOORD_0 无C |
| 21 | H_模型bian_an_1 | `mod_skin_2003_029_dg_wl_03_djs` | shader\uber_fx_common | USE_FRESNEL,USE_MASK01 | （无） | NORMAL,POSITION,TEXCOORD_0 无C |
| 22 | L_模型red_1 | `mod_skin_2003_029_dg_10_djs` | shader\uber_fx_common | USE_DISSOLVE,USE_MAIN_DISTORT,USE_MASK01,USE_MASK02 | u_emissivecolor=[0.0902, 0.3294, 1.0, 1.0] · u_emissive_highlight_intensity=50 · u_dissolve_amount=0.66 · u_mask_power=1.8 · u_maintex_speed_y=-1 · u_distort01_speed_y=-0.4 | NORMAL,POSITION,TEXCOORD_0 无C |
| 23 | L_模型twl01 | `mod_skin_2003_029_dg_12_djs` | shader\uber_fx_common | ADD_COLORTEX,USE_DISSOLVE,USE_MASK01 | u_emissive_highlight_intensity=5 · u_emissive_power=2 · u_dissolve_amount=0.52 · u_mask_power=4 · u_mask_intensity=4 | NORMAL,POSITION,TEXCOORD_0 无C |
| 24 | H_mod_外圈电 | `mod_skin_2003_029_dg_09_djs` | shader\uber_fx_common | USE_DISSOLVE,USE_MAIN_DISTORT,USE_MASK01 | u_emissivecolor=[1.0, 0.5608, 0.0667, 1.0] · u_emissive_highlight_intensity=50 · u_dissolve_amount=0.16 · u_mask_power=1.3 · u_distort01_speed_y=2 | NORMAL,POSITION,TEXCOORD_0 无C |
| 25 | M_模型red03_1 | `mod_skin_2003_029_dg_08_djs` | shader\uber_fx_common | ADD_COLORTEX,USE_DISSOLVE,USE_MAIN_DISTORT,USE_MASK01,US | u_emissivecolor=[0.5373, 0.3373, 0.0353, 1.0] · u_emissive_highlight_intensity=2 · u_emissive_power=2 · u_dissolve_amount=0.66 · u_mask_power=3 · u_maintex_speed_y=1 · u_distort01_speed_y=-0.1 | NORMAL,POSITION,TEXCOORD_0 无C |
| 26 | L_模型tou_2 | `mod_skin_2003_029_dg_wl_04_djs` | shader\uber_fx_common | USE_EMISSIVE_CONTROL,USE_MAIN_DISTORT,USE_MAIN_ROTATION_ | u_emissivecolor=[0.3647, 0.4902, 1.0, 1.0] · u_emissive_highlight_intensity=5 · u_emissive_power=5 · u_distort01_speed_y=-0.5 | NORMAL,POSITION,TEXCOORD_0 无C |
| 27 | H_mod_刀光_04 | `mod_skin_2003_029_dg_wl_06_djs` | shader\uber_fx_common | ADD_COLORTEX,USE_DISSOLVE,USE_MAIN_DISTORT,USE_MASK01,US | u_emissivecolor=[1.0, 0.0667, 0.0, 1.0] · u_emissive_highlight_intensity=2 · u_emissive_power=4 · u_dissolve_amount=0 · u_mask_power=3.5 · u_mask_intensity=2 · u_maintex_speed_y=0.6 · u_distort01_speed_y=0.2 | NORMAL,POSITION,TEXCOORD_0 无C |
| 28 | H_mod_刀光_02 | `mod_skin_2003_029_dg_wl_07_djs` | shader\uber_fx_common | USE_DISSOLVE,USE_MAIN_DISTORT,USE_MASK01,USE_MASK02 | u_emissivecolor=[0.1765, 0.0, 0.0, 1.0] · u_emissive_power=1.5 · u_dissolve_amount=0 · u_mask_intensity=2 · u_maintex_speed_y=1.2 · u_distort01_speed_y=0.5 | NORMAL,POSITION,TEXCOORD_0 无C |
| 29 | H_mod_刀光_05 | `mod_skin_2003_029_dg_wl_08_djs` | shader\uber_fx_common | USE_EMISSIVE_CONTROL,USE_MAIN_ROTATION_UV,USE_MASK01 | u_emissivecolor=[0.7647, 0.1255, 0.0314, 1.0] · u_emissive_highlight_intensity=10 · u_dissolve_amount=0 · u_distort01_speed_y=0.2 | NORMAL,POSITION,TEXCOORD_0 无C |
| 30 | L_模型白边 | `mod_skin_2003_029_dg_14_djs` | shader\uber_fx_common |  | （无） | NORMAL,POSITION,TEXCOORD_0 无C |
| 31 | M_模型尾_2 | `mod_skin_2003_029_dg_02_djs` | shader\uber_fx_common | USE_MAIN_DISTORT,USE_MASK01 | u_emissivecolor=[1.0, 0.4431, 0.0471, 1.0] · u_emissive_highlight_intensity=5 · u_emissive_power=0.3 · u_mask_power=1.5 · u_maintex_speed_y=-2 · u_distort01_speed_y=-1 | NORMAL,POSITION,TEXCOORD_0 无C |
| 32 | M_模型qiliu_2 | `mod_skin_2003_029_dg_wl_05_djs` | shader\uber_fx_common | USE_EMISSIVE_CONTROL,USE_MAIN_DISTORT,USE_MAIN_ROTATION_ | u_emissivecolor=[0.8314, 0.9098, 1.0, 1.0] · u_emissive_highlight_intensity=3 · u_mask_power=1.5 · u_maintex_speed_y=1 · u_distort01_speed_y=-0.5 | NORMAL,POSITION,TEXCOORD_0 无C |
| 33 | M_模型尾_glow_1 | `mod_skin_2003_029_dg_04_djs` | shader\uber_fx_common | ADD_COLORTEX,USE_MASK01,USE_MASK02 | u_emissivecolor=[1.0, 0.6392, 0.1412, 1.0] · u_emissive_highlight_intensity=10 · u_emissive_power=1.4 · u_mask_power=1.5 · u_mask_intensity=2 · u_maintex_speed_y=-0.6 | NORMAL,POSITION,TEXCOORD_0 无C |
| 34 | M_模型尾_glow_3 | `mod_skin_2003_029_dg_01_djs` | shader\uber_fx_common | ADD_COLORTEX,USE_MASK01,USE_MASK02 | u_emissivecolor=[1.0, 0.7216, 0.1294, 1.0] · u_emissive_highlight_intensity=80 · u_emissive_power=1.2 · u_mask_power=1.5 · u_mask_intensity=5 · u_maintex_speed_y=-0.8 | NORMAL,POSITION,TEXCOORD_0 无C |
| 35 | M_模型_地扩散2 | `mod_skin_2003_022_jisha_dimiankuosan_hgz01_01_djs`(非本皮肤) | — | — | **无 .mtg 同族 ⇒ 不接、不猜** | NORMAL,POSITION,TEXCOORD_0 无C |
| 36 | H_模型_gow | `mod_skin_2003_022_jisha_glow_shu_hgz01_01_djs`(非本皮肤) | — | — | **无 .mtg 同族 ⇒ 不接、不猜** | NORMAL,POSITION,TEXCOORD_0 无C |
| 37 | M_地裂亮_1 | `mod_skin_2003_022_jisha_dilie_hgz01_01_djs`(非本皮肤) | — | — | **无 .mtg 同族 ⇒ 不接、不猜** | NORMAL,POSITION,TEXCOORD_0 无C |
| 38 | L_m_扩散_02 | `mod_skin_2003_022_kuosan_hgz_02_djs`(非本皮肤) | — | — | **无 .mtg 同族 ⇒ 不接、不猜** | NORMAL,POSITION,TEXCOORD_0 无C |
| 39 | M_模型气流升_1 | `mod_skin_2003_022_jisha_qiliu_01_djs`(非本皮肤) | — | — | **无 .mtg 同族 ⇒ 不接、不猜** | NORMAL,POSITION,TEXCOORD_0 无C |
| 40 | M_模型气流升_1_1_1 | `mod_skin_2003_022_jisha_qiliu_01_djs`(非本皮肤) | — | — | **无 .mtg 同族 ⇒ 不接、不猜** | NORMAL,POSITION,TEXCOORD_0 无C |
| 41 | M_mod_地裂流光_1_1 | `mod_sandian_02_hjl_djs`(非本皮肤) | — | — | **无 .mtg 同族 ⇒ 不接、不猜** | NORMAL,POSITION,TEXCOORD_0 无C |
| 42 | M_模型_金线1 | `mod_skin_2003_018_bp_baoci_hgz01_02`(非本皮肤) | — | — | **无 .mtg 同族 ⇒ 不接、不猜** | NORMAL,POSITION,TEXCOORD_0 无C |

**合计**：有 `.mtg` 同族 = **34** · 无 = **8** · 总 **42**（= 42 ✓）

## 2. 数据侧（只读引用 env-auditor 的 MTG 文件）

- `stems`：**33** 条，每条含 `stem/mtg/container/row_gim/row_mesh/row_mtg/bytes/sha16/material_name/shader/technique/macros/params/textures/render_states/transparent_mode` ✓
- `model_nodes`：**34** 条（已带 `shader`/`macros`/`textures`/`params_count` ✓）· `no_mtg_sibling`：**8** 条 ⇒ **42** ✓
- `render_states` 只有 `LightingEnable/SpecularEnable/VColorEnable/AlphaRef/AlphaVal/CullBack/TransparentMode`（**无 blend/depth**）⇒ 混合状态仍 `engine_state_unresolved` ✓

## 3. 阶段一结论

- **已证**：34/42 有 `.mtg` 同族（33 stem，32/33 属 `uber_fx_common`）；**GLB 40/40 无 `COLOR_0`** ✗；UV/法线齐 ✓；内嵌贴图 0 ✗；几何 4,574 verts ✓
- **未证/沿用既有**：Model 层贴图路径不可得（族材质只绑 `white.tga` 且 MISS）⇒ `mtg_textures` 一律 `unresolved` 登记
- **未做（阶段二/三）**：`effects.json` 只新增 `mtg_*`；`WikiSfxAdapter.mtgParams(on)` 默认 OFF；`models × mtgParams` 四组合 A/B + 负控
## 4. 阶段二（数据侧）—— **已完成** ✓

| 项 | 值 |
|---|---|
| `effects.json` 改前 sha16 | `535909555a2599a6` · 578,144 B |
| **改后 sha16** | **`56bef14e53b6316a`** · 653,917 B |
| 备份（`copy2`） | `effects.json.bak_mtg_20260919_223833`（回滚用）· **`effects.json.bak_mtg2_20260919_223844`**（本次写入前） |
| **canonical diff** | **ADD = 258 · DEL/CHG/LEN = 0** ✓（**纯新增，既有字段零改动** ⇒ 门通过才写盘） |
| 新增字段 | `mtg_stem` · `mtg_params`（源值逐项）· `mtg_provenance`（含 `mtg:<container>#<row_mtg>:<param>`）· `mtg_macros` · `mtg_shader` · `mtg_textures`（`status: unresolved`） |
| 覆盖 | **35 节点拿到源参数**（`mtg_sibling=true`）· **8 节点 `no_mtg_sibling` ⇒ 不接不猜** · Model 类节点合计 **43**（比 MTG 文件的 42 多 1：多出那个节点是 effects.json 里一个额外带 `model_name` 的条目，按 stem 也匹配到了记录 ⇒ **已如实登记这 1 个差异，待复核**） |
| 示例 | `L_模型_科技01` → stem `mod_skin_2003_029_mz_kj01_djs` · shader `uber_fx_common.fx::TShader` · provenance `effect_01.gpk#192314`（sha16 `bdd0ee5808d1bc00` · 1,838 B）· params 含 `u_maintex_tilling_x=10/u_maintex_offset_x=0.25/u_maintex_speed_y=-1/u_dissolve_amount=0.63/…` |

## 5. 阶段三（adapter）—— **未做**（下一步）

**关键发现（决定实现方式，避免双重相乘）**：adapter **已经**在 Model 分支乘过一次 `u_emissive_highlight_intensity` ——
- `L55 var MODEL_HIGHLIGHT = true;`（注释：自发光项按源公式带上 `u_emissive_highlight_intensity`）
- `L317 m.emissiveIntensity = (rec.cls === 'A') ? Math.max(0, Number(hiv) || 1) : 1;`（applyModelMaterial 内）
- `L46-48` 另有 `MODEL_BLEND_K = null`（源级）与 opacity/emissiveIntensity 的源口径说明
⇒ **`mtgParams(on)` 必须只"提供源值"、不得再乘一次 highlight**：推荐**只替换 hiv/颜色的取值来源**（来自 `node.mtg_params`），乘法仍走 `L317` 那一处；或开启 `mtgParams` 时**同时把 `MODEL_HIGHLIGHT` 处置为单一来源**并在报告写明 ✓
⇒ 另：Model 节点在 `attach` 里经 `L207 nodes.filter(n => n.texture_candidate)` 过滤后**不进该列表**，Model 走 `modelRecs`/`applyModelMaterial` 路径（`L252/L279/L429+`）⇒ `mtgParams` 开关应挂在 `applyModelMaterial` 的取值处 ✓

## 6. 仍未做（阶段三/四清单，待续）

- adapter：`WikiSfxAdapter.mtgParams(on)`（默认 OFF）+ 源色/源强度接入（单点乘法，防双重相乘）+ `node --check`
- 顶点色分支：**不写**（`COLOR_0 = 0/40` 已证 ✗；如需在开关里显式登记 `unavailable_no_vertex_color`）
- 测量：`models(false/true) × mtgParams(false/true)` 四组合（白块占比、截图 sha16、亲眼描述）+ 负控「`models(true)+mtgParams(false)` 与改前逐字节一致」
- **未证/沿用既有**：Model 层贴图路径不可得（族材质只绑 `white.tga` 且 MISS）⇒ **渲出来仍不是成品外观** ✓；`render_states` 无 blend/depth ⇒ 混合状态仍 `engine_state_unresolved` ✓