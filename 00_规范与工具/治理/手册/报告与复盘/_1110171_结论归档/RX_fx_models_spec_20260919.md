# RX_fx_models_spec：极光剑（1110177）26 个 Model 特效节点 —— 可实现材质规格（只读）

> **只读**产出（未改 viewer.js / adapter / manifest / board / 注册表；未起浏览器）。结构化版：同目录 `RX_fx_models_spec.json`（含 **逐 26 节点完整表** + GLB 明细 + 分类 + 配方 + unresolved）。
> **pin 校验**：`adapter 544D3A4A1B2CC591` ✓ · `1110177/effects.json 10CC9A938BE92A10` ✓ · **⚠ `viewer.js` 实测 `68F8113B864A4CA1` ≠ 你给的 `8B8E80213F5C0CA8`**（并发修改中）—— 本文结论**不依赖 viewer.js 行号** ✓
> 本规格与 chain-auditor 的 task-61 只读取证**同源可互相印证**：全部结论可复核为 `文件:行号` / 容器 `row+偏移` / GLB 头字段 ✓

---

## 1. 家族判定：**`shader\uber_fx_common.fx`（= `res.gpk` #15714）** ✓ 与你的引用一致

| 判据 | 证据 |
|---|---|
| `.sfx` 内的着色器路径 | `fx_skin_2003_029_hit.sfx` 命中 `shader\uber_fx_common.fx` **2 次**；`fx_skin_2003_029_jisha.sfx` 命中 **1 次**（各自唯一命中的 shader 路径） |
| 容器侧同族 | `shader\uber_fx_common.nfx2` → `E:\mrzh\res.gpk` **row 15714** · o=`844,308,572` · comp=6,823 · **dec=26,799** · **flag=2(lz4)** ⇒ **与 Lead 给的 #15714 完全一致** ✓ |
| 不能照抄 1110152 | 1110152 的 `sfx` 目录存在但**无 `.sfx` 文件**（0 个）⇒ 无法从其声明取同族证据；**本规格只依据 1110177 自身声明** ✓ |

**节点计数**：`hit.sfx` = **7 Model / 17 ShaderComponent**；`jisha.sfx` = **19 Model / 27 ShaderComponent** ⇒ **合计 26 个 Model** ✓（与你说的 26 一致）

## 2. 可用的驱动 uniform 与源值（逐节点表见 JSON `models[26]`）

### 2.1 汇总（两文件，按出现次数）
| uniform | hit.sfx | jisha.sfx | 关键帧类型（源文本） | 有源值？ |
|---|---|---|---|---|
| `u_depth_bias` | 15 | 12 | FloatKeyFrame（例 `8` / `10` / `2` / `-2`） | ✓ |
| `u_emissive_highlight_intensity` | 7 | 7 | FloatKeyFrame（例 `5→10→9.4375→6.4375`；另有单帧 `50`） | ✓ |
| `u_overall_opacity` | 6 | 10 | FloatKeyFrame（例 `0→1→0.9→0`） | ✓ |
| `u_emissivecolor` | 6 | 9 | **ColorKeyFrame**（8bit RGBA 文本，例 `255,255,238,208 → 255,255,173,23`） | ✓ |
| `u_dissolve_amount` | 5 | 7 | FloatKeyFrame | ✓ |
| `u_diffuse_color` / `u_diffuse_intensity` | 1 / 1 | 8 / 7 | Color / Float | ✓ |
| `AlphaMtl` | 1 | 8 | FloatKeyFrame（例 `0→1→0.775→0`） | ✓ |
| `u_emissive_intensity` / `u_emissive_power` | 1 / 2 | 2 / — | Float | ✓ |
| `u_softparticle` | 2 | — | Float | ✓ |
| `u_distort_intensity` | — | 2 | Float | ✓ |
| `u_maintex_speed_x` / `u_maintex_speed_y` | — | 1 / 1 | Float（**只有 speed，没有 tilling/offset**） | ✓ |
| `u_diffuse_uvspeed_y` | — | 2 | Float | ✓ |
| `u_base_color` / `u_intensity` | — / 1 | 1 / 1 | — | ✓ |
| **`u_emissive_color`（另一种拼写）** | — | **2** | — | ✓ ⚠ 与 `u_emissivecolor` 并存 |

**⚠ 无源值 ⇒ 不许补**：`u_uv_tilling` / `u_tilling` / `Tilling` / `u_uv_offset` 在两文件中 **命中 0** ⇒ **UV 仅由 speed 类驱动**；tilling/offset 一律标 `unresolved`，禁止自造 ✓

### 2.2 逐节点（完整 26 行在 JSON；此处给结构示例）
| # | sfx | L | 节点名 | .gim | TM | Bias | Order | Life | 配对 uniforms |
|---|---|---|---|---|---|---|---|---|---|
| 1 | hit | 513 | u_dissolve_amount | mod_skin_2003_029_mz_kj01_djs.gim | 0 | 2 | 0 | 0.600 | u_depth_bias,u_emissive_intensity |
| 2 | hit | 1740 | USE_EMISSIVE_CONTROL | mod_skin_2003_029_mz_shandian01_djs.gim | 5 | 3 | 0 | 0.268 | u_depth_bias,u_emissive_highlight_intensity |
| 3 | hit | 1871 | u_depth_bias | mod_skin_2003_029_mz_ks01_djs.gim | 5 | 2 | 0 | 0.348 | u_emissivecolor,u_emissive_highlight_intensity,u_overall_opacity,u_dep |
| 4 | hit | 2047 | USE_EMISSIVE_CONTROL | mod_skin_2003_029_mz_sd01_djs.gim | 5 | 3 | 0 | 0.200 | u_diffuse_intensity,u_diffuse_color,AlphaMtl,u_intensity,u_depth_bias |
| 5 | hit | 2228 | USE_EMISSIVE_CONTROL | mod_skin_2003_029_mz_shandian03_djs.gim | 5 | 3 | 0 | 0.400 | u_overall_opacity,u_emissivecolor,u_emissive_highlight_intensity,u_dis |
| 6 | hit | 2383 | USE_EMISSIVE_CONTROL | mod_skin_2003_029_mz_shandian02_djs.gim | 2 | 3 | 0 | 0.348 | u_overall_opacity,u_emissivecolor,u_emissive_highlight_intensity,u_dis |
| 7 | hit | 3143 | u_emissive_highlight_i | mod_skin_2003_029_mz_kj03_djs.gim | 0 | 3 | 0 | 0.600 | u_depth_bias |
| 8 | jisha | 87 | u_overall_opacity | mod_skin_2003_029_dm_qiliu_20_djs.gim | 5 | 0 | 0 | 1.500 | （无） |
| 9 | jisha | 203 | u_overall_opacity | mod_skin_2003_029_14_hjl_djs.gim | 2 | 1 | 0 | 1.700 | u_emissivecolor,u_overall_opacity |
| 10 | jisha | 319 | u_emissivecolor | mod_skin_2003_029_dm_qiliu_12_djs.gim | 5 | -2 | 0 | 1.498 | u_emissivecolor,u_overall_opacity |
| 11 | jisha | 694 | u_overall_opacity | mod_skin_2003_029_dm_qiliu_23_djs.gim | 5 | 2 | 0 | 1.350 | u_diffuse_color,AlphaMtl,u_diffuse_intensity,u_overall_opacity,u_emiss |
| 12 | jisha | 907 | u_overall_opacity | mod_skin_2003_029_dm_shangdian_05_djs.gim | 5 | -1 | 0 | 1.498 | u_depth_bias,u_diffuse_intensity,AlphaMtl,u_emissive_color,u_diffuse_c |
| 13 | jisha | 1755 | u_dissolve_amount | mod_skin_2003_029_dm_wuqi_01_djs.gim | 0 | 2 | 0 | 0.700 | u_depth_bias |
| 14 | jisha | 3440 | Tex0 | mod_skin_2003_022_jisha_dimiankuosan_hgz01_01_djs.gim | 2 | 1 | 0 | 0.500 | u_depth_bias |
| 15 | jisha | 3588 | AlphaMtl | mod_skin_2003_022_jisha_glow_shu_hgz01_01_djs.gim | 0 | -1 | 0 | 1.200 | u_depth_bias,u_diffuse_color,u_diffuse_intensity,AlphaMtl |
| 16 | jisha | 3728 | Tex0 | mod_skin_2003_022_jisha_dilie_hgz01_01_djs.gim | 5 | 4 | 0 | 1.200 | u_depth_bias,u_diffuse_color,u_diffuse_intensity,AlphaMtl |
| 17 | jisha | 3996 | Tex0 | mod_skin_2003_022_kuosan_hgz_02_djs.gim | 5 | 1 | 0 | 0.900 | AlphaMtl,u_diffuse_color,u_diffuse_intensity,u_intensity |
| 18 | jisha | 4426 | u_diffuse_uvspeed_y | mod_skin_2003_022_jisha_qiliu_01_djs.gim | 5 | 5 | 0 | 0.700 | u_emissive_intensity |
| 19 | jisha | 4604 | u_emissive_highlight_i | mod_skin_2003_029_dm_qiliu_09_djs.gim | 5 | 1 | 0 | 1.000 | u_depth_bias,u_diffuse_intensity,AlphaMtl,u_diffuse_color,u_distort_in |
| 20 | jisha | 4828 | mask_tex | mod_skin_2003_022_jisha_qiliu_01_djs.gim | 5 | 5 | 0 | 0.900 | u_overall_opacity,u_maintex_speed_y,u_maintex_speed_x,u_dissolve_amoun |
| 21 | jisha | 5035 | u_dissolve_amount | mod_skin_2003_029_56_hjl_djs.gim | 2 | -2 | 0 | 1.000 | u_depth_bias,u_diffuse_intensity,AlphaMtl,u_diffuse_color,u_distort_in |
| 22 | jisha | 5203 | u_emissivecolor | mod_skin_2003_029_dm_qiliu_06_djs.gim | 2 | 0 | 0 | 0.834 | u_overall_opacity,u_emissive_highlight_intensity,u_emissivecolor,u_dis |
| 23 | jisha | 5316 | Tex0 | mod_sandian_02_hjl_djs.gim | 5 | 0 | 0 | 0.800 | u_dissolve_amount,u_emissivecolor |
| 24 | jisha | 5475 | u_diffuse_color | mod_skin_2003_018_bp_baoci_hgz01_02.gim | 0 | 0 | 0 | 0.900 | u_dissolve_amount,u_overall_opacity,u_emissivecolor,u_emissive_highlig |
| 25 | jisha | 6222 | u_emissive_highlight_i | mod_skin_2003_029_dm_shangdian_07_djs.gim | 0 | 0 | 0 | 0.800 | u_depth_bias |
| 26 | jisha | 6306 | Tex0 | mod_skin_2003_029_dm_shangdian_07_djs.gim | 0 | 0 | 0 | 0.500 | u_dissolve_amount,u_emissive_highlight_intensity |

*（TM=TransparentMode，Bias=RenderBias，Order=RenderOrder，Life=FxLifeSpan；配对为"最近前置 ShaderComponent"推断）*
节点属性（每个 Model 自带，可复核）：`ModelName`(→`.gim`)、`FxLifeSpan`、`TransparentMode`、`RenderBias`、`RenderOrder`、`LightIntensity`、`FogIntensity` ✓
**配对说明**：`.sfx` 内**未发现**节点↔`<ShaderComponent>` 的显式字段 ⇒ 本规格按**文件顺序取最近的前置 ShaderComponent**（**推断**，标记为 U2，供 task-61 独立印证）✓

## 3. 语义与公式：**unresolved（不给猜测）** ✗

| 现象 | 结论 |
|---|---|
| 反汇编可用性 | **整棵 `_disasm`（968 个 asm）对 `u_emissivecolor` / `u_overall_opacity` / `u_depth_bias` / `u_emissive_highlight_intensity` **0 命中** ✓ ⇒ **FX 族（uber_fx_common）尚未反汇编**，仓库内也无 DXBC 反汇编器 ⇒ **无法给出"自发光如何进最终色 / opacity 语义 / depth_bias 单位"的指令级证据** |
| 下一步的现成坐标（可直接复用我 RX_* 系列的做法） | `shader\uber_fx_common.nfx2` @ `res.gpk` **row 15714** · o=`844,308,572` · comp=6,823 · dec=26,799 · **flag=2(lz4 block)** ⇒ 解出即 DXBC 容器 |
| 现在**能**确定的结构性事实 | ① `u_emissivecolor` = **ColorKeyFrame（4 通道含 alpha）**；② `u_emissive_highlight_intensity` / `u_overall_opacity` / `u_depth_bias` = **FloatKeyFrame（标量）**；③ `u_depth_bias` 取值是小整数（8/10/2/−2）⇒ 单位未定证；④ 每节点自带 `TransparentMode`(0/2/5) / `RenderBias`(−2..3) / `RenderOrder` / `LightIntensity` / `FogIntensity` |
| **禁止** | 在拿到反汇编前断言"emissive 直接相加"或"乘 highlight 后再加"、"opacity 乘 alpha 还是乘亮度" —— 属猜测 ✗ |

## 4. GLB 侧事实（抽查 5 个，全 26 个同名规则）

| GLB | 顶点 | 三角 | 属性 | 材质 | 内嵌贴图 |
|---|---|---|---|---|---|
| `dm_wuqi_01_djs.glb` | 1,119 | 1,121 | **POSITION + NORMAL + TEXCOORD_0** | 1（`MAT_s0`） | **0** |
| `mz_ks01_djs.glb` | 216 | 350 | 同上 | 1（`MAT_s0`） | 0 |
| `56_hjl_djs.glb` | 186 | 300 | 同上 | 1（`MAT_s0`） | 0 |
| `dm_qiliu_06_djs.glb` | 220 | 320 | 同上 | 1（`MAT_s0`） | 0 |
| `mz_shandian01_djs.glb` | 24 | 12 | 同上 | 1（`MAT_s0`） | 0 |

- **几何自带 UV ✓、法线 ✓**；**无 `COLOR_0`（顶点色）✗**；每 GLB **单材质 `MAT_s0` 且无内嵌图像** ⇒ **贴图必须由 wiki 侧提供**
- **贴图槽该指向哪个源声明名 = `unresolved`** ✗：`1110177/sfx/tex_candidates_provenance.json`（29,142 B）里以**源声明名**为键（`alpha_01_tp52_01.tga`、`tex_alpha_mask_tp60_04.tga`、`tex_alpha_tp104_04.tga`、`tex_crack_02_yx_djs.tga`、`tex_crack_tp71_05.tga`、`dian_12.tga`、`glow01_yc.tga`、`glow25.tga`），但每条都写着 **`bound:false` / `confidence:low` / "只登记候选、不绑定"** ⇒ **不可当作已定绑定**，也不得据此手填 ✓

## 5. 可实现建议（按代价排序）

| # | 配方 | 依赖的源证据 | 代价 | 风险 |
|---|---|---|---|---|
| **A** | **静态占位**：`MeshBasicMaterial({ color: u_emissivecolor 中段帧, transparent:true, opacity: u_overall_opacity 中段帧, depthWrite:false })`，混合模式**先按 `TransparentMode` 节点属性**取值而非猜 ADD | `u_emissivecolor`/`u_overall_opacity` 有源值 ✓；节点 `TransparentMode`(0/2/5) 有源值 ✓ | 低 | **大面积白块**（若误用 additive）、透明排序、深度冲突；先关 `depthWrite` |
| **B** | **按帧驱动 A**：用 `.sfx` 的 `<Frame Time Value>` 插值驱动 color/opacity（数据完整 ✓；`FxLifeSpan` 有值 ✓） | 关键帧表 ✓ | 中 | 8bit 颜色文本的**色彩空间/编码未定证**（U5）；需与节点生命周期对齐 |
| **C** | **自定义注入**：等 FX 族反汇编后按 `u_emissive_highlight_intensity`/`u_emissive_power`/`u_dissolve_amount` 的源公式注入 | 待反汇编（坐标已给 §3） | 高 | 公式未定证前**不要做** ✗ |
| **D** | 为每个 GLB 挑 UV 贴图并绑定 | provenance 明确 `bound:false` ⇒ **无源依据** | — | **不能补**（禁止造绑定）✗ |

**建议顺序**：`A`（先跑通几何可见）→ `B`（按帧驱动）→ 等 `C` 的反汇编结果再谈源级还原 ✓

## 6. unresolved + 已排除

**unresolved**
| id | 项 | 备注 |
|---|---|---|
| U1 | FX 族公式：emissive 如何进色、`u_overall_opacity` 语义、`u_depth_bias` 单位/阶段 | 需反汇编 `res.gpk#15714`（坐标见 §3）；无指令级证据前一律不给结论 |
| U2 | 节点 ↔ `ShaderComponent` 的**显式**绑定机制 | 本规格用"最近前置组件"推断；请 task-61 独立取证印证 |
| U3 | 贴图槽 ↔ 源声明名的对应 | `tex_candidates_provenance.json` 只登记候选（`bound:false`） |
| U4 | `u_emissive_color` 与 `u_emissivecolor` 两种拼写的优先/语义差异 | jisha.sfx 内并存 |
| U5 | 颜色关键帧的色彩空间（8bit 文本 ⇒ 线性 or sRGB） | — |
| U6 | GLB 的 UV 集合与源贴图 UV 约定的逐顶点一致性 | 未做逐顶点核对 |

**已排除**
- **照抄 1110152**：其 `sfx` 目录内 **0 个 `.sfx`**，无同族声明可取 ✓
- **UV tilling/offset**：源内 0 声明 ⇒ 不得自造 ✓
- **手填贴图绑定**：provenance `bound:false` ✓
- **在无反汇编时断言混合模式**（ADD vs ALPHA）✓

## 7. 复核命令
```
venv\Scripts\python.exe %TEMP%\RXFX1.py    # .sfx 结构（ShaderComponent/Macros/Uniforms 块）
venv\Scripts\python.exe %TEMP%\RXFX2.py    # 逐 Model + 关键帧 + uniform 汇总 + GLB 头解析 → RXFX2.txt/.json
venv\Scripts\python.exe %TEMP%\RXFX_json.py # 生成 RX_fx_models_spec.json
venv\Scripts\python.exe 03拆包产物\_gim_out\find_entry_by_path.py --batch %TEMP%\fx_paths.txt   # 家族容器命中（row 15714）
```
