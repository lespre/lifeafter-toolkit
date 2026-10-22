# 极光剑 1110177 · 26 个 Model 特效节点 · 步骤1 只读取证（task-61）

> **本轮只读，未改 adapter / effects.json、未起浏览器。** 等 lead 确认后再实现（步骤2）。

## 0. 结论摘要
- **26/26 都有 GLB**（24 个唯一文件，均含 POSITION/NORMAL/TEXCOORD_0 + 1 个材质，**无 COLOR_0**）；几何合计 **2,540 顶点 / 3,029 三角形**（效应小几何：光片/环）。
- **驱动 uniform 可用性（26 节点中出现次数）**：`u_overall_opacity` 16、`u_emissivecolor` 15、`u_dissolve` 12、`u_emissive_highlight_intensity` 11、`u_depth_bias` 10、`u_diffuse_color` 9、`u_maintex` 1、`u_main_color`/`u_fresnel`/`u_alpha_ref` **0**。
- **按驱动分三类**：**A 发光可驱动 15**（有 `u_emissivecolor`）、**B 仅漫反射色 8**（有 `u_diffuse_color`，无 emissive）、**C 无颜色驱动 3**（只有 opacity/dissolve/highlight ⇒ **颜色 unresolved，不许造**）。
- 全 26 节点共通可用属性：`TransparentMode`（5:14 / 0:7 / 2:5）、`RenderBias`、`DirType`、`RenderOrder`、`FxStartTime/FxLifeSpan`、`Scale="FloatKeyFrame"`、`PostProcessKind`（全 0）、`AnimName/AnimSeqName`。
- ⚠ **唯一未定证项：节点级没有声明着色器族/technique**（attrs 里无 technique/shader 名；`ShaderComponent` 子记录是 `Name/Time/Value/Type/DisplayName/Interpolator/ChangeType` 形式的**uniform 关键帧**）。⇒ **不能声称与 `shader\uber_fx_common.nfx2` 同族**，也**绝不照抄 1110152 的驱动集合**。闭合路径（建议下一小步先做）：读 `effect\mesh\weapon\skin\skin_2003_029\mod_*.gim` 文档里的材质/technique 字段 + sfx 的 `Semantic`/`Macros` 块。

## 1. 逐节点表（26 行）
| # | 节点 | 类别 | GLB | UV | 材质 | 关键驱动 | 顶点/三角 |
|---|---|---|---|---|---|---|---|
| 1 | `L_模型_科技01` | **A 发光** | `mod_skin_2003_029_mz_kj01_djs.glb` | True | 1 | u_emissivecolor, u_overall_opacity, u_dissolve | 4/2 |
| 2 | `L_模型特效_01` | **A 发光** | `mod_skin_2003_029_mz_shandian01_djs.glb` | True | 1 | u_emissivecolor, u_overall_opacity, u_emissive_highlight_intensity, u_depth_bias | 24/12 |
| 3 | `H_模型纹理` | **B 漫反** | `mod_skin_2003_029_mz_ks01_djs.glb` | True | 1 | u_depth_bias, u_diffuse_color | 216/350 |
| 4 | `H_模型核心电小_3` | **A 发光** | `mod_skin_2003_029_mz_sd01_djs.glb` | True | 1 | u_emissivecolor, u_overall_opacity, u_emissive_highlight_intensity, u_depth_bias, u_dissolve | 24/12 |
| 5 | `M_模型核心电小_4` | **A 发光** | `mod_skin_2003_029_mz_shandian03_djs.glb` | True | 1 | u_emissivecolor, u_overall_opacity, u_emissive_highlight_intensity, u_depth_bias, u_dissolve | 16/8 |
| 6 | `H_模型核心电小_5` | **A 发光** | `mod_skin_2003_029_mz_shandian02_djs.glb` | True | 1 | u_emissivecolor, u_overall_opacity, u_emissive_highlight_intensity, u_depth_bias, u_dissolve | 12/6 |
| 7 | `L_模型_科技03` | **A 发光** | `mod_skin_2003_029_mz_kj03_djs.glb` | True | 1 | u_emissivecolor, u_overall_opacity, u_emissive_highlight_intensity, u_dissolve | 4/2 |
| 8 | `L_模型火_1` | **A 发光** | `mod_skin_2003_029_dm_qiliu_20_djs.glb` | True | 1 | u_emissivecolor, u_overall_opacity | 63/80 |
| 9 | `H_模型红` | **A 发光** | `mod_skin_2003_029_14_hjl_djs.glb` | True | 1 | u_emissivecolor, u_overall_opacity | 63/80 |
| 10 | `M_m_流动_科技_1_1_1` | **A 发光** | `mod_skin_2003_029_dm_qiliu_12_djs.glb` | True | 1 | u_emissivecolor, u_overall_opacity, u_diffuse_color | 104/150 |
| 11 | `M_模型喇叭` | **B 漫反** | `mod_skin_2003_029_dm_qiliu_23_djs.glb` | True | 1 | u_overall_opacity, u_depth_bias, u_diffuse_color | 66/64 |
| 12 | `M_m_流动_2` | **A 发光** | `mod_skin_2003_029_dm_shangdian_05_djs.glb` | True | 1 | u_emissivecolor, u_overall_opacity | 16/8 |
| 13 | `M_模型枪_1` | **C 无颜色** | `mod_skin_2003_029_dm_wuqi_01_djs.glb` | True | 1 | u_overall_opacity, u_dissolve | 1119/1121 |
| 14 | `M_模型_地扩散2` | **B 漫反** | `mod_skin_2003_022_jisha_dimiankuosan_hgz01_01_djs.glb` | True | 1 | u_depth_bias, u_diffuse_color | 63/80 |
| 15 | `H_模型_gow` | **B 漫反** | `mod_skin_2003_022_jisha_glow_shu_hgz01_01_djs.glb` | True | 1 | u_depth_bias, u_diffuse_color | 10/8 |
| 16 | `M_地裂亮_1` | **B 漫反** | `mod_skin_2003_022_jisha_dilie_hgz01_01_djs.glb` | True | 1 | u_diffuse_color | 4/2 |
| 17 | `L_m_扩散_02` | **A 发光** | `mod_skin_2003_022_kuosan_hgz_02_djs.glb` | True | 1 | u_emissivecolor, u_overall_opacity, u_emissive_highlight_intensity | 125/192 |
| 18 | `M_模型气流升_1` | **B 漫反** | `mod_skin_2003_022_jisha_qiliu_01_djs.glb` | True | 1 | u_depth_bias, u_diffuse_color | 8/4 |
| 19 | `L_m_扩散_科技_1_2` | **A 发光** | `mod_skin_2003_029_dm_qiliu_09_djs.glb` | True | 1 | u_emissivecolor, u_overall_opacity, u_emissive_highlight_intensity, u_dissolve, u_maintex | 52/50 |
| 20 | `M_模型气流升_1_1_1` | **B 漫反** | `mod_skin_2003_022_jisha_qiliu_01_djs.glb` | True | 1 | u_depth_bias, u_diffuse_color | 8/4 |
| 21 | `M_模型特效_2_1` | **A 发光** | `mod_skin_2003_029_56_hjl_djs.glb` | True | 1 | u_emissivecolor, u_overall_opacity, u_emissive_highlight_intensity, u_dissolve | 186/300 |
| 22 | `L_模型特效_1` | **A 发光** | `mod_skin_2003_029_dm_qiliu_06_djs.glb` | True | 1 | u_emissivecolor, u_dissolve | 220/320 |
| 23 | `M_mod_地裂流光_1_1` | **A 发光** | `mod_sandian_02_hjl_djs.glb` | True | 1 | u_emissivecolor, u_overall_opacity, u_emissive_highlight_intensity, u_dissolve | 4/2 |
| 24 | `M_模型_金线1` | **B 漫反** | `mod_skin_2003_018_bp_baoci_hgz01_02.glb` | True | 1 | u_diffuse_color | 32/16 |
| 25 | `L_模型特效` | **C 无颜色** | `mod_skin_2003_029_dm_shangdian_07_djs.glb` | True | 1 | u_emissive_highlight_intensity, u_dissolve | 105/160 |
| 26 | `H_模型特效_3` | **C 无颜色** | `mod_skin_2003_029_dm_shangdian_07_djs.glb` | True | 1 | u_emissive_highlight_intensity, u_dissolve | 105/160 |

## 2. 逐类清单（供实现用）
- **A（15，可做源驱动自发光）**：`L_模型_科技01`、`L_模型特效_01`、`H_模型核心电小_3`、`M_模型核心电小_4`、`H_模型核心电小_5`、`L_模型_科技03`、`L_模型火_1`、`H_模型红`、`M_m_流动_科技_1_1_1`、`M_m_流动_2`、`L_m_扩散_02`、`L_m_扩散_科技_1_2`、`M_模型特效_2_1`、`L_模型特效_1`、`M_mod_地裂流光_1_1`
- **B（8，仅漫反射色可用）**：`H_模型纹理`、`M_模型喇叭`、`M_模型_地扩散2`、`H_模型_gow`、`M_地裂亮_1`、`M_模型气流升_1`、`M_模型气流升_1_1_1`、`M_模型_金线1`
- **C（3，颜色 unresolved）**：`M_模型枪_1`、`L_模型特效`、`H_模型特效_3`

## 3. 步骤2 实现方案（等确认后执行）
1. **A 类 15**：`MeshStandardMaterial`（或 `MeshBasicMaterial`）自发光颜色取源 `u_emissivecolor` 关键帧（按节点时间窗取样）、透明度取 `u_overall_opacity`、`u_depth_bias` → `polygonOffset`；**无贴图保持无贴图**。
2. **B 类 8**：颜色取 `u_diffuse_color`；**不伪造 emissive**；透明度若源有 `u_overall_opacity` 则用，否则不透明（并在探针标 `opacity_src=null`）。
3. **C 类 3**：**不渲染颜色**，探针标 `fallback_reason=no_color_driver_unresolved`（如需可见性，必须你另行裁定）。
4. **默认关 + 独立开关** `WikiSfxAdapter.models(on)`（既有语义不动）；`__sfxDiag().models[]` 暴露 `{name, glb, shader_family(null=未定证), drivers_used, tex_bound(false), opacity, emissive_src, fallback_reason}`。
5. **不动** `unitScale/sprSlice/colorOrder/psFallback` 既有语义；不加人工强度系数。

## 4. 步骤3 测量计划（等实现后）
- 同载入 A/B `models(false)` vs `(true)`：alive/visible 计数、effect-only%、逐节点世界尺寸/武器对角线、**全白像素占比**（防白块回归）、截图 sha16 + **我亲眼描述**。
- 负控：`sprites(false)+models(true)` vs `sprites(true)+models(false)` 两帧互不干扰；**默认关 ⇒ OFF 帧逐字节一致**。
- `applied==expected`、`failed/missing` 空、`exceptionDetails` 逐条。

## 5. 已证 / 未证 / 未做（本轮）
- **已证**：26/26 有 GLB（24 唯一）；几何/属性事实（UV+法线，无顶点色，自带 1 材质）；逐节点驱动 uniform 可用性与三类划分；共通属性（TransparentMode/RenderBias/DirType/时间窗/Scale）。
- **未证**：**着色器族**（节点级无 technique 声明；需 `.gim`/`Semantic`/`Macros` 补证）；Model 是否存在贴图声明（本轮未见 `Tex0`/`TextureFile` 字段，按"无贴图"处理）。
- **未做**：实现、浏览器测量、白块占比、负控、OFF 一致性（均待 confirm 后执行）。
- **仍未解决（照旧）**：28 条声明贴图无名字轴（34 只绑 6）；`BlendMode` 值表 NOT_FOUND；"单位=cm"属推导；`H_p_闪电` 仍为 `content_candidate_2hop_dims_scaled`（`dims_match=false`）。


---

## §15 task-61 步骤①b —— 族判定取证 + 交叉验证（只读；命令 `%TEMP%\fx061b/c/d/e.py`）

### 已证（我自己独立复核）
1. **族 = `shader\uber_fx_common.fx`**（与 renderer-auditor 独立复现一致）：`fx_skin_2003_029_hit.sfx` 命中 2 次、`fx_skin_2003_029_jisha.sfx` 命中 1 次，**全文件唯一 shader 路径串**（正则 `[A-Za-z0-9_\\/\.\-]*\.(fx|nfx2)`）。
2. **容器侧行坐标逐字复核一致**：`GpkIndex.read('shader\uber_fx_common.nfx2')` → `container=res.gpk · row=15714 · off=844,308,572 · comp=6,823 · dec=26,799 · flag=2(lz4)`；解压后 26,799 B，**magic `c159 410d`** 与 `.gim` 同族文档（NeoX c159）。`.fx` 原路径 `read=False`（容器内只有 nfx2）。
3. nfx2（解压后）自带参数/宏面，样例串：`ADD_COLORTEX`、`ALPHA_TEST_ENABLE`、`AddressU/V/W`、`APLutInvSize`、`APLutSize`、`AerialPerspectiveLUT`、以及 32-hex 摘要串。→ 供 renderer-auditor 的 DXBC 侧使用；**我不据此解释 `TransparentMode` 枚举含义**。
4. `.gim` 26/26 可读（`effect\mesh\weapon\skin\skin_2003_029\mod_*.gim`），字符池**纯 ASCII**（11 采样：ASCII 211 / UTF-16 0），头 `c159 410d 4901 … NeoX … Sub0`。gim 内**无** shader/technique/pass/`.fx`/`.nfx2` 串；唯一材质相关 token = `MtlIdx`(11/11) 与 `PreZAlphaBlend`(11/11)。→ **gim 只给材质索引，不给族名**（与族判定不冲突）。
5. Model 节点在 `effects.json` 中 **`attrs` 为空 `{}`**，属性键中无任何 `Tech/Shader/Pass/Mtl/fx` 命中 ⇒ 技术与族名确实不在节点属性里。
6. sfx `<Macros><Variables>` 26/26 存在但宏面极小：22 节点无宏；2 节点 `USE_EMISSIVE_CONTROL=TRUE`（`L_模型无效_01`、`M_模型核心地小_4`）；2 节点 `USE_SOFTPARTICLE=TRUE,USE_EMISSIVE_CONTROL=TRUE`（`H_模型核心地小_3`、`H_模型核心地小_5`）。4 个宏节点**全属 A 类**（A 共 15）⇒ 分类与宏不矛盾，但宏不能作为分类依据。
7. `<Semantic>` 即 uniform 声明（`Name/Type/Value/DisplayName`）；采样器槽名固定 **`Tex0`**（`Type=String`，值为 `effect\textures\...tga`），另有 `AlphaMtl`（`FloatKeyFrame`, `Value=AlphaMtl_Keyframe`）与 `u_*` Keyframe uniform ⇒ 统一 `u_*` namespace + 固定 `Tex0` 槽。

### 未证（→ unresolved，按最保守实现）
- 族已定证为 `uber_fx_common`，但 **uniform 语义/公式仍 unresolved**（renderer-auditor：`_disasm` 968 asm 对相关 uniform 0 命中）⇒ 不猜混合公式、不引入强度系数；`u_emissive_highlight_intensity`（含单帧 50）仅登记 `present_unwired`。
- `TransparentMode` / `RenderBias` 枚举值表未定证 ⇒ 只原样上报，不解释。
- **拼写变体 U4**：jisha 中 `u_emissive_color`(2 处) 与 `u_emissivecolor` 并存 ⇒ 按节点各自声明取用，不合并。
- `u_uv_tilling`/`u_tilling`/`Tilling`/`u_uv_offset` 命中 0 ⇒ UV tilling/offset = unresolved，不引入 UV 缩放。
- 贴图槽 ↔ 源声明名 = unresolved（候选 `bound:false/confidence:low`）⇒ 不手填绑定。

### 未做
- 未反编译、未读 DXBC（renderer-auditor 侧）。
- 本步**未改任何代码/数据**：adapter `544D3A4A1B2CC591`(77,511 B)、`1110177/effects.json 10CC9A938BE92A10`(400,615 B)、`1110177/viewer.json 7575FAFAD33DD670`(431,073 B) 全 MATCH。

### pin 异常（需 lead 裁定）
- `08Lifeafter wiki\assets\viewer.js` **不存在**；该目录下唯一 `*viewer*.js` = `assets\weapon_skin_viewer.js` = `68F8113B864A4CA1`(378,682 B) ≠ lead pin `8B8E80213F5C0CA8`（renderer-auditor 实测同为 `68F8113B864A4CA1`，疑并发改动）。与本规格无依赖。


---

## §16 task-61 步骤② —— 实现落地（源字段注入 + 适配器保守材质）

### 一、改动清单（逐处行文）
**A. 数据侧（唯一写入 `1110177/effects.json`，脚本 `03拆包产物\_target_1110171\FX029_model_keyframes.py`）**
1. 26/26 Model 节点新增 `model_fields.uniform_tracks`（**源** uniform 关键帧，原样注入：96 轨道 / 254 帧；规则 `<u_*_Keyframe ChangeType Interpolator><Frame Time Value/>`）。
2. `model_fields.uniform_tracks_meta`（每轨 `ChangeType`/`Interpolator` 原值）+ `keyframe_source`（sfx 文件/节点/轨道清单/帧数，含「未做任何解释换算」声明）。
3. 源属性落到 `model_fields` 的既有小写键（供适配器运行时优先读取）：`transparent_mode/render_bias/track_type/render_order/dir_type/render_level/fx_start_time/fx_life_span/model_name/post_process_kind/scale_type`。
4. `model_field_patch.model_keyframes` 记录本次注入统计（含**源侧分类自检**：A=15 / B=8 / C=3，与既有驱动计数表一致）。
5. 备份 `effects.json.bak_modelkf_20260919_184146`；sha16 `10CC9A938BE92A10` → **`399223E5F0B15813`**（400,615 → 441,573 B）。
6. **未写入**：`models_enabled`（保持默认关）、`renderable_by_adapter`（未动）、任何贴图绑定（`tex_bound=false` 一律）。

**B. 适配器侧（`08Lifeafter wiki/assets/weapon_skin_sfx_adapter.js`）**
7. 新增 `mdlRGB(col)`：Model 源色列序**复用已独立 PASS 的 `COLOR_ORDER`**（默认 `'rgba'` ⇒ 列 0..2；`'argb'` ⇒ 1..3）。**U5 登记**：1110152 时代 Model 路径写死 `(A,R,G,B)`，两说并存、`colorOrder()` 一处置换，未定证前不作结论。
8. `rec` 新增：`cls`(A/B/C，**只看源驱动项存在性**)、`emissive_src`/`diffuse_src`/`opacity_src`、`opTrack`、`db`、`drivers_used`、`unwired`、`tex_bound=false`、`fallback_reason`。
9. `applyModelMaterial` 改为保守口径：A=emissive 源色 + `color` 置黑 + additive；B=`color` 源色 + emissive 置黑 + normal；两者 `depthWrite=false`/`depthTest=true`；`emissiveIntensity=1`（中性恒等，**源强度项一律不接线**）；`opacity` **只取** `u_overall_opacity`（无 ⇒ 1）；`polygonOffset` **仅源有 `u_depth_bias` 时启用**（10/26 节点）。
10. 逐帧驱动：RGB 走 `mdlRGB`；`a` 取 `u_overall_opacity`；**删除** 旧版 `a = 颜色alpha × u_maintex*_opacity`、`inten = u_maintex*_brightness/100 或 highlight`（源公式 unresolved ⇒ 不猜）。
11. `models(on)`：C 类**即使开也不加载**（`disabled_no_color_driver` / `no_color_driver_unresolved`）；`hasTex0` 仍不加载；默认仍 `MODELS_FORCE=null` ⇒ 跟随 `effects.models_enabled`（未写 ⇒ **默认关**，不改变默认行为）。
12. `modelMaterial(mode,k)`：改成按**源轨道**重取颜色/透明度后再套用（旧版把现有 `color` 当 rgb 传回 ⇒ A 类置黑的 color 会被写进 emissive，属旧缺陷）。`k=null` 默认不加任何系数。
13. `__sfxDiag().models[]` 逐节点新增 lead 指定字段：`'class'`、`glb`、`drivers_used`(数)+`drivers`(表)、`unwired`、`tex_bound`、`opacity`、`opacity_src`、`emissive_src`、`diffuse_src`、`depth_bias_src`、`blending`、`depthWrite`、`depthTest`、`polygonOffset(+Units)`、`fallback_reason`，并保留 `state/hasObj/objVisible/groupVisible/scale/measured/expectedSpan`。
14. `modelBranchBasis` **追加**（不覆盖历史）：`task61_rule` / `task61_sources` / `task61_color_order`。
15. **未改动**：`unitScale/sprSlice/colorOrder/psFallback` 的语义一行未改（Model 路径只是*调用* `COLOR_ORDER`）；`viewer.js`/`viewer.json`/`neuro_material.json`/manifest/board/registry 一律未碰。
16. 备份 `weapon_skin_sfx_adapter.js.bak_task61_20260919_184250`；`node --check` exit=0；sha16 `544D3A4A1B2CC591`(77,511 B) → **`6A0ED1DA58705F21`**(84,657 B)。

### 二、期望表（从改后数据静态导出，供浏览器实测对照）
见 `FX029_models_expected.json`（26 行 + summary）。

### 三、卡点（需 lead 处理才可测量）
- **viewer.json 需重新内联新 effects.json**（`399223E5F0B15813`）；否则页面里仍是旧数据 ⇒ 26 个 Model 全被判 C 类、`models(true)` 一个都不渲。当前 `1110177/viewer.json 7575FAFAD33DD670` 仍内联旧 effects（`10CC9A938BE92A10`）。


---

## §17 task-61 步骤② 补正（源公式子集落地 + 两处口径修正）

1. **按 lead 新口径落地源公式子集**（证据：renderer-auditor asm `L409-415`/`L425`，槽位 `u_emissivecolor`=cb0[3].xyz、`u_emissive_highlight_intensity`=cb0[24].x）：
   A 类自发光项 = `u_emissivecolor`（必带）× `u_emissive_highlight_intensity`（**仅当该节点有声明**；无声明 ⇒ 不乘并记 `omitted_undeclared`）。
   **未声明/不可得的因子**（`u_emissive_grey_intensity`、`u_emissive_mix`、`u_emissive_desaturate`、`u_mask_intensity`、
   以及自发光贴图采样项 `e`）**整个子项省略**，探针 `omitted_undeclared[]` 逐项登记，**不以"中性默认值"顶替**。
   ⇒ 本实现是源公式的**子集**：`approx:true`，`approx_reason='tex_unbound_e_sampler_unavailable + omitted_undeclared'`。
   `emissiveIntensity` 承载 highlight 因子（MeshStandardMaterial 的 emissive 通道 = shader 内 `final = diffuse + r1` 的自发光项加法结构）。
2. **新增开关 `WikiSfxAdapter.modelsHighlight(true|false)`**：默认 `true`（按 lead 指令接线）；`false` = 去掉该因子的基线，用于 A/B 对照。
3. **`u_depth_bias` 不进 shader**：按 lead 口径 5 与本轮证据（4 份 asm 内 `[unused]`）**一律不启用 polygonOffset**，探针记
   `depth_bias_state='present_unwired(engine_state_unresolved)'`（10/26 节点存在该轨道）。上一版 §16 第 9 条「仅源有则启用 polygonOffset」**作废**（本条为准）。
4. **类别口径修正**：拼写变体 `u_emissive_color`（1 个节点，非"2 处"）按 lead「按节点各自声明取用、不合并」的口径**视为自发光声明** ⇒
   适配器实测分类 **A=16 / B=7 / C=3**；若只认 `u_emissivecolor`（lead 原清单口径）则为 A=15 / B=8 / C=3。两口径差在**同一个节点**，已在期望表登记。
5. 期望表 `FX029_models_expected.json` 同步修正 `unwired`（**highlight 已接线，移出 unwired**）并附两口径计数。
6. 探针新增字段：`omitted_undeclared` / `approx` / `approx_reason` / `highlight_src` / `highlight_state` / `emissiveIntensity` /
   `blending_asserted=false` / `blending_source`（TransparentMode 映射未定证）/ `depth_bias_state`。


---

## §18 task-61 步骤③ —— 实测（含单位换算修复）与配对规则结论

### 18.1 本轮我改了什么（逐处）
1. **修缺陷（adapter）**：Model 网格解析原读 `mf.ModelName`/`mf.mesh` —— 本 effects.json 里 **0/26 存在** ⇒ 26/26 全落 `no_mesh_field`，`models(true)` 一个都不加载（实测 8 帧逐字节相同 = 证据）。改为读**节点级** `n.model_name` / `n.model_glb`（`sfx/<stem>.glb`），并把回退目录从 `sfx/model/` 改回 `sfx/`。
2. **单位换算（adapter，按 lead 指令）**：Model 实例缩放乘 `U()`（= `SFX_UNIT_TO_MODEL` = 0.1），**随 `unitScale` 同一开关**（`unitScale(false)` 可对照），**源 Scale 轨道保留为乘子**。位置侧无需改：`basePos` 早已走 `U()`（L408）。
3. **探针补字段**：`'class'`/`glb`/`drivers_used`/`drivers`/`unwired`/`omitted_undeclared`/`approx`/`approx_reason`/`tex_bound`/`opacity`/`opacity_src`/`emissive_src`/`diffuse_src`/`highlight_src`/`highlight_state`/`emissiveIntensity`/`blending`/`depthWrite`/`depthTest`/`polygonOffset(+Units)`/`depth_bias_state`/`fallback_reason`/`spelling_variant`/`confidence`/`macros`/`effective_gates`。
4. **源公式子集（adapter）**：`emissive = u_emissivecolor × u_emissive_highlight_intensity`（**仅该节点有声明才乘**；`modelsHighlight(on)` 默认 true，false 作对照）；`u_emissive_grey_intensity`/`u_emissive_mix`/`u_emissive_desaturate`/`u_mask_intensity`/贴图采样 `e` **整子项省略**并逐项登记 ⇒ `approx_reason='tex_unbound_e_sampler_unavailable + omitted_undeclared'`。**"省略"≠"等价于 0"**：这几个因子由**引擎材质默认值**填充（c159 仅名字池、无静态默认；`.sfx` 未逐节点声明）⇒ 本实现是**源公式的子集，不是源还原**。
5. **`u_depth_bias` 不做 z 偏移**（asm 4 份全 `[unused]`）⇒ `depth_bias_state='present_unwired(engine_state_unresolved)'`，`polygonOffset=false`。
6. **脚本修复（我的夹具链）**：`fx061_measure.py` CDP 传输 `asyncio.Future.result(timeout)` → `concurrent.futures.Future`（原报 `TypeError: Future.result() takes no arguments (1 given)`）；`Driver.d` 自引用别名（原报 `'Driver' object has no attribute 'd'`）；输出目录预建。
7. 备份：`weapon_skin_sfx_adapter.js.bak_task61_20260919_184250` · `.bak_task61_unit_20260919_185536`；`effects.json.bak_modelkf_20260919_184146`。

### 18.2 pin（跑前跑后一致，`pin_diff: OK`）
adapter **`79F5F2B86D321995`**(90,499 B，`node --check` exit=0) · `1110177/effects.json` **`399223E5F0B15813`**(441,573 B) · `1110177/viewer.json` **`FD29DCD83C718B44`**(493,771 B) · `weapon_skin_viewer.js` **`B9C7281E1EE7A819`** · `board.html` **`B8284433492B2101`**。
内联一致性独立核验：内联 effects 与 `effects.json` **66 节点逐键等价**，仅 `models_enabled`(缺省→false) 与 lead 自己的 `lead_wiring_note` 两个顶层键不同 ⇒ **不是数据漂移**。

### 18.3 测量结果（一次载入内，单浏览器，收尾 chrome=0 / 端口空闲 / 0 残留）
| 步骤 | 截图 sha16 | white255 | white±2 | meanL | nonBlack |
|---|---|---|---|---|---|
| s03 默认关 attempt1_a | `61A8171DAE53D73A` | 0.00005 | 0.00007 | 44.275 | 0.9925 |
| s03 默认关 attempt1_b | `61A8171DAE53D73A` | 同 | 同 | 同 | 同 |
| s04 `models(false)` | `61A8171DAE53D73A` | 同 | 同 | 同 | 同 |
| s05 `models(true)`（highlight on） | `DC7035C0E21F17C4` | **0.05778** | 0.05786 | 62.074 | 0.9925 |
| s06 `modelsHighlight(false)` | `BDEA42895A014398` | 0.05718 | 0.05728 | 61.655 | 0.9925 |
| s07 负控 `modelMaterial('normal')` | `3D262DD1BA419308` | 0.02472 | 0.02476 | 59.403 | 0.9925 |
| s07b 复原 additive+hl(on) | `DC7035C0E21F17C4` | 0.05778 | 0.05786 | 62.074 | 0.9925 |

- **默认关逐字节一致 ✓**：两次零操作帧 `61A8171DAE53D73A` 相同；`models(false)` 帧与默认关帧**同 sha**；`modelsOn=false`、`visible=0`、状态 = `disabled_fail_closed`×23 + `disabled_no_color_driver`×3。
- **`models(true)` ✓**：`visible=23`、`hasObj=23`、收敛 277 ms、`exc=0`、状态 = `ok`×23 + `disabled_no_color_driver`×3；**类别计数 A=16 / B=7 / C=3**（与期望表逐项一致）；材质分布（复原后）`AdditiveBlending(2)`×16 + `NormalBlending(1)`×7 + 无材质×3 = **正好 A/B/C**；`tex_bound=false` 26/26；`opacity_src='u_overall_opacity'` 16 行。
- **highlight 硬门（lead 判据 2）**：`(true)` 0.05778 vs `(false)` 0.05718 ⇒ **+0.06pp（相对 +1.0%）**，无白块显著上升 ⇒ **保持默认 true（源式）**；`highlight_state` 分布 `applied`/`omitted_undeclared`/`not_applicable`，`changed_hl=9` 证明开关确实生效。
- **负控 ✓**：强制 `normal` ⇒ sha 变化、白像素 0.0578→0.0247（**减半**）⇒ 混合模式确实改变观感，但 `TransparentMode` 映射**仍未定证**（探针 `blending_asserted=false`）。
- **健康项**：`loadErrors=[]`、`exceptionDetails` **0 条**、`neox={applied:3, prims_n:3, failed:[], missing:[]}`、`warnings=0`。

### 18.4 几何（源侧数字，非观感）
| 量 | 值 |
|---|---|
| GLB 自带 POSITION bbox 最大维度（24 个 GLB） | min 12.9998 / **median 38.7085** / **max 163.0668** |
| 武器对角线 | **15.4552 模型单位** |
| 直接挂载（无换算） | **163.07 / 15.4552 = 10.55×** ⇒ 铺满视口（截图 `771B5400A942660A` 佐证） |
| **×U()=0.1 后** | **1.055×**（与"特效几何与武器同尺度"相符）⇒ 实测白像素 15.86% → **5.78%** |

### 18.5 亲眼描述（我的判断）
- **默认关**：武器（极光剑）完整、贴图正常、深青工业背景；除极小高光点外无白区（0.005%）。
- **`models(true)`**：几何已回到武器尺度 —— 可见**一条竖向宽红带**（约武器长度量级）＋**若干扁平白色/淡青四边形面片**围绕剑身，另有少量淡青楔形；**仍不像刀光/闪电/星环**，因为这些面片 26/26 **未绑贴图**（`tex_bound=false`），无贴图的自发光平面自然呈现"白卡片"；`mz_ks01` 类 GLB 本身就是 `76.28×76.21×0.0` 的**平面**（厚度 0）⇒ 白卡片的来源可解释。
- 结论：**单位换算 bug 已修，但观感主因转为"贴图未绑"** ⇒ 我**不建议**把 `models_enabled` 置 true；保持默认关（fail-closed）等待纹理槽位定证。

### 18.6 配对规则（回答 lead 三问）
1. **我的规则 = 源 XML 嵌套，无任何推断**：对每个节点，`txt.find('Name = "<节点名>"')` → 截到下一个顶层标签（`ParticleSystem/Sprite/Model/Dummy/ParticleRes/Trail`）→ 取该**节点自己块内**的 `<ShaderComponent><Uniforms><Variables><u_*_Keyframe>…` 帧。节点与组件是**包含关系**，不需要"最近前置/后置"。
2. **交叉核对事实**：我的注入与我方块解析 **26/26 一致**（脚本 `%TEMP%\fx061_verify.py`）；再与 `model_fields.shader.ShaderComponent` 的声明列（上一轮独立解析）一致 —— 例：`L_模型_科技01` 块偏移 11894 / 长 3237，块内**恰好 1 个组件**，其 uniforms = `{u_overall_opacity, u_emissivecolor, u_dissolve_amount}`。
3. **双方差异的来源（事实，不下断言）**：renderer-auditor 的 `pairing_divergence.driver_set_matches` 显示**整体错位一格**（其 #3=我 #2、#5=我 #4/#6、#20=我 #19、#23=我 #22、#24=我 #23、#26=我 #25/#26）⇒ 与"最近**前置**组件"在有嵌套结构时的错位一致。**另有一点必须澄清**：其 `driver_diffs` 标的 `only_mine` 与我方公开表**不符**（例：`L_模型_科技01` 其记我方 = `{u_depth_bias, u_emissive_intensity}`，而我方该行实为 `{u_overall_opacity, u_emissivecolor, u_dissolve_amount}`，恰等于其 #1 行 = 该块自身集合）⇒ 其比较器除配对规则外**还有一处对齐问题**。**影响面**：以我方嵌套规则为准时，颜色/透明度**未挂错节点**（26/26 块级核对通过；A/B/C=16/7/3 亦与 lead 裁定一致）；建议 renderer-auditor 用嵌套规则重出一列即可对齐。

### 18.7 宏门（lead 追加 2）
`model_fields.shader.ShaderComponent` 里 `Type==='Bool'` 的条目 = **6 条 / 4 个 Model 节点**（`USE_EMISSIVE_CONTROL`×4：`L_模型特效_01`、`H_模型核心电小_3`、`M_模型核心电小_4`、`H_模型核心电小_5`；`USE_SOFTPARTICLE`×2 于后两者）。
⚠ 口径差异：renderer-auditor 报 `USE_EMISSIVE_CONTROL` **6 处 / 10 个非空宏块**（含 `USE_SFXLIGHT_FOG`/`USE_VERTEXCOLOR`/`USE_MASK01`）—— 那是**全节点类型**计数；**Model 节点内**只有上述 6 条 / 4 节点。两者不冲突，但引用时必须写清范围。

### 18.8 未证 / 未做
- 未证：`TransparentMode`→混合状态映射（静态不可得，已收窄到极限）· `u_depth_bias` 引擎侧单位/阶段 · 贴图槽↔源名（26/26 未绑）· 颜色列序 U5（取 `COLOR_ORDER='rgba'`，与 1110152 时代 `(A,R,G,B)` 之说并存）· 自发光子集被省略因子的引擎默认值。
- 未做：`u_dissolve_amount` 公式**未接**（12 节点，仅登记「下一项可接」）· 未填任何 UV tilling/offset · 未手填贴图 · 未改 `unitScale/sprSlice/colorOrder/psFallback` 语义 · 未碰 viewer.js/viewer.json/manifest/board/registry · 未做 task-62。


---

## §19 task-62 (b) 前置：`_dg.sfx` 解包互证 + dissolve 裁决登记 + 交接书

### 19.1 `_dg.sfx` 独立解包（已与 env-auditor 互证）
`E:\mrzh\Documents\gres\0057.gpk` **row 32153**：`block_base=1,823,837,828 + off=652,984 + 20 = 1,824,490,832`，`comp=4,654`、`flag=12(zstd, 28b52ffd…)` ⇒ **解出 66,424 B = dec 精确吻合，sha16 `9F4FE3A6AD3F8851`**（与 env-auditor 的解**逐位一致**）。格式 = GBK 明文 `<FxGroup Name="MyFx" …>`；**23 节点 = Dummy 3 / Model 16 / ParticleSystem 3 / ParticleRes 1**；**全 23 节点无 Bool 宏**。
- 16 个 Model 的 `ModelName` 全为新增 `…_dg_wl_01..08_djs.gim` + `…_dg_{01,02,04,08,09,10,12,14}_djs.gim`（**与 `_hit.sfx` 交集 0**）。
- **3 个需隔离的同名 Dummy**：`L_空特效`、`L_空特效_1_1`、`L_空特效_2`。
- dg 驱动**声明节点数**：`u_overall_opacity` 15 · `u_emissivecolor` 9 · `u_dissolve_amount` 5 · `u_emissive_desaturate` 3 · `u_emissive_highlight_intensity` 3 · `u_depth_bias` 3 · `u_mask_power` 1（口径＝"声明该 uniform 的节点数"，与 env-auditor 的"关键帧帧数"口径不同，引用须写清）。
- 机读清单：`_target_1110171\FX029_dg_inventory.json`（脚本 `FX029_dg_unpack.py`）。

### 19.2 dissolve —— **不做**（lead 裁决 2026-09-19，选乙）
`u_dissolve_amount` 的公式（renderer-auditor，`RX_fx_dissolve_20260919.md`）虽已展开为最小式，但最小式仍需要 **`mask = t_dissolve_tex`（sampler t3）的采样值**与 **`base = Tex0.a`**：
- `<Model>` 节点在源里**不声明任何贴图槽**（lead 亲自核：hit 0/7 + jisha 0/19）；`Tex0` 语义仅 **1 个** Model 节点出现；**`t_dissolve_tex` 无任何节点声明** ⇒ **mask 源不存在**。
- 按最小式接线只能造"无源 mask" ⇒ 会引入**新的白块/黑洞**且**无可观测差异**，违反"不猜/不顶替"纪律。
⇒ **本轮不接线**，只登记 **`dissolve_state='declared_blocked(mask_source_unavailable)'`**（12 个组件），列为本报告「仍未解决」项；**待纹理绑定定证后**再评估。

### 19.3 交接书（给下一棒）
`_target_1110171\FX029_dg_handover.md` —— 含：当前 pin、脚本与用法、`_dg.sfx` 已证事实、**(b) 注入字段清单与来源规则**（`source_sfx` 隔离 / `model_glb='sfx/dg/<stem>.glb'` / `uniform_tracks` 注入口径 / 3 个 Dummy 改名并改写 `parent`）、**7 条验收断言**（节点 66→89、`source_sfx` 分布、dg A/B/C 期望、42 个 glb 必须存在、默认关帧 sha16 仍为 `61A8171DAE53D73A`…）、已踩过的坑（gres 偏移 `block_base+row_off+20`、源无贴图、unitScale=0.1、GBK 控制台、单浏览器礼仪）。

### 19.4 未做（明确）
- (a) 16 个 `.gim`→GLB 导出 = **env-auditor**（写域 `1110177/sfx/dg/`）；(b) 合并 = 交接书所指下一棒；(c) 测量 = **viewer-auditor**。
- 本步**未改** adapter / `effects.json` / viewer.js / viewer.json / manifest / board / registry；仅新增 `FX029_dg_unpack.py`、`FX029_dg_inventory.json`、`FX029_dg_handover.md` 与本 §19。


---

## §20 task-62 (b) 就绪状态 · source_sfx 命名口径 · 已知技术债

### 20.1 source_sfx 命名口径（lead 裁定 2026-09-19，已落到脚本）
`_dg.sfx` 的**文件名未被直证**（env-auditor 盘点清单只直证了同族 `fx_skin_2003_029_daoguang_02.sfx`）⇒ dg 节点**不写**无保留的 `source_sfx` 名，改为：
- **主键（直证）**：`source_sfx_id = "gres\0057.gpk#32153"`；
- **人类可读名（降级）**：`source_sfx_name_inferred = "fx_skin_2003_029_dg.sfx"` + `source_sfx_name_evidence = "inferred_from_family_naming"`；
- 每行另带 `dg_provenance = {container, row:32153, off, dec:66424, sha16:"9F4FE3A6AD3F8851", note}`。
- **status_reason 表述统一为**：「**资产已按容器坐标定位并接入（名字为同族命名推定）**」。
干跑复核：A2 分布显示 `gres\0057.gpk#32153` × **23**（不再是未加限定的文件名）。

### 20.2 已知技术债（不在本轮范围，仅登记）
1. **现有 66 节点内已有 4 处重名**：`L_空特效`、`L_空特效_1`、`L_空特效_1_1`、`H_鬼火_射线_02` —— **各 ×2，全部是 `fx_skin_2003_029_hit.sfx` 与 `fx_skin_2003_029_jisha.sfx` 各一份**（**task-61 之前即存在**，非 dg 引入、非本轮引入）。
   ⇒ 因此"全局 name 唯一"不能作为验收断言；**(b) 的断言改为「dg 不得引入新重名」**：合并前 4 处 → 合并后 4 处、**dg 新增 0**（dg 的 3 个同名 Dummy 已改名 `L_空特效__dg` / `L_空特效_1_1__dg` / `L_空特效_2__dg`）。
   ⇒ **若后续要按 `parent` 构建层级树，必须先对 hit/jisha 做命名空间隔离**（现有 `parent` 值如 `L_空特效_1_1 → L_空特效_1` 在两个文件里各有一套，按名解析会串）。
2. 现有 66 节点的 `parent` 中 **14 行为 `None`**；dg 侧 **`parent` 全为 `None`**（dg 源全文 `Parent` 类文字 **0 次命中**，排除 `TransparentMode`）⇒ 如实，非漏解析。

### 20.3 (b) 就绪状态（真实写盘未执行）
- 合并脚本 `_target_1110171\FX029_dg_merge.py` 已就绪（`--dry-run` 只解析+断言、不写文件）。
- 干跑：**A1 66→89 ✓** ｜ **A2 分布 21 / 45 / 23 ✓** ｜ **A2b dg 新增重名 0 ✓** ｜ **A3 类分布 A25/B7/C10 ✓** ｜ **A6 `models_enabled` 缺省（默认关）✓** ｜ **A4 42 个 `model_glb`：26 在盘 / 16 个 dg 缺失 ⇒ 待 env-auditor 导出**（`1110177/sfx/dg/` 尚未创建）。
- **`effects.json` 未改动**，仍为 **`399223E5F0B15813`**（不存在半成品）。放行条件：A4 的 16 个缺失项消失。
- 默认关帧基线 **`61A8171DAE53D73A`** 必须在内联后由 (c) 复核（合并本身不影响默认关路径：dg 行 `renderable_by_adapter=False`、无 `models_enabled`）。
