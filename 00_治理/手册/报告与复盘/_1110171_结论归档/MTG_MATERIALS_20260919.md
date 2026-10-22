# MTG_MATERIALS_20260919 — 极光剑 1110177：33 个 `.mtg` 全量解出与逐字段落盘（task-63）

- 任务来源：**task-63**（已 `claim`，owner = env-auditor）。
- 写作用域（严格）：`MTG_MATERIALS_20260919.md` / `.json`、`MTG_raw/`（33 个原文）。**未改** `viewer.json`/`effects.json`/`neox_material.json`/`viewer.js`/adapter/`board.html`（改前改后 sha16 对照见 §8）。
- 只读来源：`effect_01.gpk`（`.mtg` 按名取，row 191892–192335）。

---

## 0. 结论先说

| 问题 | 答案 |
|---|---|
| 33 个 `.mtg` 是否全部解出并落盘？ | **是**：33/33 明文 `c159410d`，原文 + 结构化记录写在 `MTG_raw/<stem>.mtg`，每个都有 `{row, bytes, sha16}` |
| **Q1：RenderStates 能不能定出真实混合/深度状态？** | **不能**。33/33 文件的 RenderStates 段只有 **21 个字段名**，其中与渲染状态相关的只有 `AlphaRef`、`CullBack`；**没有任何 `SrcBlend/DstBlend/BlendOp/BlendEnable/ZWrite/ZEnable/ZTest/Depth*/Stencil/ColorMask` 字段**，也**没有混合方程**。值区记录的“前导字节 → 字段名”映射**未定证**（同一文件里 `0x10` 既出现字符串 `"Effect"` 又出现 `int 0`）⇒ 只能给候选，不能据此改 three.js 状态 |
| **Q2：ParamTable 有没有能驱动颜色/亮度/透明/tiling/UV 滚动的项？** | **有**，而且很充裕：**30/33** stem 有此类参数（颜色 30、自发光/亮度 29、透明度/遮罩 26、tiling 26、UV 滚动/旋转 28、扰动/溶解 26、菲涅尔 10），共 **53 个参数名**，全部带**原值 + 字节偏移 + raw hex**（见 §4 与 JSON） |
| `.mtg` 还能给出什么源级真值？ | **shader 名**（32 × `shader\uber_fx_common.fx::TShader` + 1 × `shader\uber_mask_rim_diss.fx::TShader`）、**Technique**（`Effect`）、**材质名**、**宏集合**（116 条，全部 enable=1）、**贴图槽→声明路径** |
| 42 个 Model 节点对照 | 42 个 Model 节点中 **34 个**落在 33 个 1110177 stem 上（33 个 stem 全被引用），**8 个是 `no_mtg_sibling`**（来自 `skin_2003_018`/`skin_2003_022`/`mod_sandian_02_hjl_djs`，本皮肤没有对应 `.mtg`） |

---

## 1. 产出清单

| 产出 | 说明 |
|---|---|
| `MTG_raw/<stem>.mtg` × 33 | 原文落盘：① tag 表（名字+偏移）② 值区块结构（block/record，含偏移/id/type/value/raw）③ ParamTable 逐参数 ④ 贴图槽 ⑤ 宏 ⑥ shader/technique/材质名 ⑦ 全文件 hex（每行 32 B 带偏移）。每个文件头部写 `container/row/bytes/sha16`，JSON 里另有 `raw_dump_sha16` |
| `MTG_MATERIALS_20260919.json`（489 KB） | `{stems:[…33…], model_nodes_all:[…42…], no_mtg_sibling:[…8…], declared_overlap:{…}, q1_renderstates:{…}, q2_paramtable:{…}, shader_families, unresolved}` |
| 本报告 | Q1/Q2 的回答、格式说明、42 节点对照表、受保护文件哈希对照 |

---

## 2. `.mtg` 容器格式（本轮实证，含偏移）

```
[c159410d][u32 文件长度][u32 0]
NUL 分隔 tag 表：
   组件段：AnimParam / LightingMaterial / Macro0..N / Material / MaterialGroup / Material_0 / NeoX /
           ParamTable / RenderStates / ShaderMacro / Technique / Tex0 / TransparentMode …
   参数段：t_* / u_*（参数名）
   状态字段段：AlphaRef / AlphaVal / Ambient / CullBack / Diffuse / Emissive / Key / LightingEnable /
           MaterialCount / Name / Power / Specular / SpecularEnable / Speed / TechName /
           TransparentMode / Type / VColorEnable / Val / Value / Version
值区块（本轮解出）：<01 00><count:1B><count × record>
   record = <前导字节:1B><类型:1B><payload>
   类型：01 = NUL 结尾字符串 / 02 = i32(4B) / 03 = u8(1B) / 05 = f32(4B) / 06 = f32[n]（n 为 u32 前缀）
参数条目：<01 00 01 13><类型><payload>，与 tag 表参数名/u16 槽组按序 1:1 配对（复用既有 c159 解析器）
结束标记：01 00 01 0f 02 05 00 00 00 01 00
```
**样例（`mod_skin_2003_029_dg_wl_03_djs.mtg`，1139 B，row 192104）逐块**：

| block | 偏移 | count | 记录（off / 前导 / 类型 / 值 / raw） |
|---|---|---|---|
| 0 | 606 | 3 | 617 `0x08 i32 1`；624 `0x09 str ""`；631 `0x14 f32[4] [0,0,1,3]` |
| 1 | 640 | 1 | 645 `0x10 i32 0` |
| 2 | 649 | 2 | 654 `0x09 str "Material #5"`；672 `0x14 f32[4] [0,0,1,3]` |
| 3 | 688 | 1 | 693 `0x0d i32 1` |
| 5 | 700 | 2 | 705 `0x0e str "shader\uber_fx_common.fx::TShader"`；741 `0x10 str "Effect"` |
| 7 | 751 | 5 | 760 `0x02 f32[4] [0,0,0,0]`；782 `0x04 f32[4]`；804 `0x05 f32[4]`；822 `0x0a i32 0`；832 `0x0b f32[4]` |
| 8 | 848 | 6 | 853 `0x00 i32 0`；859 `0x01 i32 255`；865 `0x03 str "False"`；873 `0x07 str "False"`；881 `0x0c str "False"`；889 `0x11 str "False"` |
| 9 | 895 | 2 | 900 `0x06 str "USE_MASK01"`；913 `0x12 u8 1` |
| 10 | 914 | 2 | 919 `0x06 str "USE_FRESNEL"`；933 `0x12 u8 1` |

参数区（`01 00 01 13` 条目，同文件）：`off=934 f32 0.8`、`943 f32 0.3`、`952 f32 0.1`、`961 f32 0.45`、`970 f32[4] [0,0,0,1]`、`995 i32 1`、`1004 i32 1`、`1013 i32 1`、`1022 f32 0.6`、`1031 f32 0.2`、`1040 str "effect\textures\glow\glow_01.tga"`、`1078 str "effect\textures\alpha\alpha_tp61_lsy_djs.tga"` —— 与槽组配对后即 `ParamTable` 逐参数值（§4）。

**诚实边界**：值区仍有约 15% 字节未被块解析器消费（stray），且**前导字节不是稳定字段 id**（同一文件 `0x10` 出现为 str 与 i32 两种）⇒ 值→字段名的**归属未定证**。下面凡涉及归属一律标 `candidate / unresolved`。

---

## 3. Q1：`RenderStates` 能不能定出真实混合/深度状态？——**不能**

### 3.1 字段级证据（33/33 文件一致）

| 字段名 | 出现 | 典型 D3D/引擎语义 | 我们的判定 |
|---|---|---|---|
| `AlphaRef` | 33/33 | alpha test 阈值 | 字段存在；值区有 `i32 255` 候选记录（`0x01`，33/33 文件），**归属未证** ⇒ unresolved |
| `CullBack` | 33/33 | 背面剔除开关 | 字段存在；4 个布尔串记录之一，**名称对应未证** ⇒ candidate |
| `LightingEnable` / `SpecularEnable` / `VColorEnable` | 33/33 | 受光/高光/顶点色开关 | 同上（4 个布尔串 ↔ 4 个布尔字段，**计数一致**） |
| `Ambient` / `Diffuse` / `Emissive` / `Specular` | 33/33 | 材质颜色 rgba | 4 个 `f32[4]` 记录 ↔ 4 个颜色字段（**计数一致**）；本皮肤这 4 个值**全为 [0,0,0,0]** |
| `TransparentMode` | 33/33 | 引擎透明枚举（同 `.sfx` 字段名） | **只有字段名，没有可归属的值** ⇒ unresolved |
| `Type`/`Version`/`MaterialCount`/`Key`/`Val`/`Value`/`Power`/`Speed`/`Name`/`TechName`/`AlphaVal` | 33/33（Key/Val 32/33） | 枚举/标量/字符串 | 仅字段名 ⇒ unresolved |
| **`SrcBlend`/`DstBlend`/`BlendOp`/`BlendEnable`/`ZWrite`/`ZEnable`/`ZTest`/`DepthTest`/`DepthWrite`/`Stencil`/`ColorMask`** | **0/33** | 混合与深度状态本体 | **不存在** ⇒ 无法从 `.mtg` 定证 |

### 3.2 值区实况（可用的“量化”部分）

- 记录类型统计：`str` 380、`i32` 215、`f32[4]` 199、`u8` 100、`f32` 2。
- **4 个布尔字段**（id `0x03/0x07/0x0c/0x11`，值为字符串 `"False"/"True"`，**有真实变化**）：
  `0x03`：27 False / **6 True**；`0x07`：29 False / **3 True**；`0x0c`：29 False / **3 True**；`0x11`：29 False / **3 True**。
- **4 个颜色字段**（id `0x02/0x04/0x05/0x0b`，`f32[4]`）：本皮肤**全为 [0,0,0,0]**（即未覆盖，取默认）。
- 另有两类固定向量：`0x14 = [0,0,1,3]`（每文件 2 条，64/33 条）；以及**唯一一条非零颜色** `(1.0, 0.6, 0.1725, 1.0)`（金色，见 §7）。

### 3.3 对 three.js 的映射建议（**全部标注可信度**）

| three.js 属性 | 可能来源 | 可信度 | 建议动作 |
|---|---|---|---|
| `side` | `CullBack` | candidate（值归属未证） | **本轮不改动**；若要试，需先定证 id↔字段名 |
| `alphaTest` | `AlphaRef` | candidate（`i32 255` 候选） | **本轮不改动** |
| `transparent` / `blending` | `TransparentMode` | **unresolved**（无值可归属，且 `.mtg` 无混合方程） | 维持 adapter 现状近似映射，并在 `modelBranchBasis` 里写明“无值表” |
| `depthWrite` / `depthTest` | —— | **absent**（源里不存在） | **禁止自拟** |
| （补充）材质颜色/自发光/遮罩 | ParamTable（§4） | **已定证**（参数名 → 原值，带偏移） | 可用 |

**要定证还缺什么**：① 引擎 RDEF/schema 表（把前导字节映射成字段名）；② 运行时 cbuffer 抓取（读 `TransparentMode`/`AlphaRef` 实值）；③ 同材质 A/B 渲染比对。三者任一即可把上面的 `candidate` 升级为直证。

---

## 4. Q2：`ParamTable` 的驱动项（**有**，逐 stem）

- **53 个参数名并集**；**30/33** stem 至少有一项颜色/亮度/透明/tiling/UV 驱动；**3 个 stem 无 ParamTable 数值**：`dg_14`、`dg_wl_02`、`mz_ks01`（这 3 个 `.mtg` 里没有数值块，如实为空、未补默认）。
- 类别覆盖 stem 数：**颜色 30/33**、**自发光/亮度 29/33**、**透明度/alpha/遮罩 26/33**、**tiling 26/33**、**UV 滚动/旋转 28/33**、**扰动/溶解 26/33**、**菲涅尔 10/33**。
- 出现最多的非零参数（名 → 非零 stem 数，值样例）：

| 参数名 | 非零 stem | 值样例（stem → 原值） |
|---|---|---|
| `u_emissive_highlight_intensity` | 28 | `14_hjl` → 2；`56_hjl` → 5 |
| `u_emissivecolor`（f32[4]） | 22 | `dg_01` → [1.0, 0.7216, 0.1294, 1.0]（金）；`56_hjl` → [0.0824, 0.0471, 0.4, 1.0]（蓝） |
| `u_distort01_speed_y` | 19 | `14_hjl` → -0.1；`56_hjl` → -1 |
| `u_maintex_speed_y` | 18 | `14_hjl` → 0.6；`56_hjl` → -0.3 |
| `u_distort1_intensity` | 16 | `14_hjl` → 0.1 |
| `u_dissolvetex_tilling_x` | 16 | `56_hjl` → 3；`dg_09` → 2 |
| `u_mask_power` | 16 | `dg_01` → 1.5 |
| `u_maintex_tilling_x` / `_y` | 15 / 15 | `56_hjl` → 2 / 0.5；`dg_01` → 1.2 |
| `u_emissive_power` | 14 | `56_hjl` → 1.5；`dg_01` → 1.2 |
| `u_dissolve_amount` | 13 | `dg_08` → 0.66；`dg_09` → 0.16 |
| `u_dissolve_smooth` | 13 | `dg_08` → 0.19；`dg_10` → 0.98 |

**逐 stem 类别矩阵**（`Y`=有该项，`P`=参数个数，`T`=贴图槽数；完整参数/原值见 JSON `q2_paramtable.per_stem` 与 `MTG_raw/<stem>.mtg`）：

| stem | P | T | 颜色 | 自发光/亮度 | 透明/遮罩 | tiling | UV滚动 | 扰动/溶解 | 菲涅尔 |
|---|---|---|---|---|---|---|---|---|---|
| `14_hjl_djs` | 7 | 3 | Y | Y | – | – | Y | Y | – |
| `56_hjl_djs` | 19 | 4 | Y | Y | Y | Y | Y | Y | Y |
| `dg_01_djs` | 13 | 4 | Y | Y | Y | Y | Y | – | – |
| `dg_02_djs` | 11 | 3 | Y | Y | Y | Y | Y | Y | – |
| `dg_04_djs` | 13 | 4 | Y | Y | Y | Y | Y | – | – |
| `dg_08_djs` | 21 | 6 | Y | Y | Y | Y | Y | Y | – |
| `dg_09_djs` | 13 | 4 | Y | Y | Y | Y | Y | Y | – |
| `dg_10_djs` | 19 | 5 | Y | Y | Y | Y | Y | Y | – |
| `dg_12_djs` | 18 | 4 | Y | Y | Y | Y | Y | Y | – |
| **`dg_14_djs`** | **0** | 1 | – | – | – | – | – | – | – |
| `dg_wl_01_djs` | 7 | 2 | Y | Y | Y | – | – | – | Y |
| **`dg_wl_02_djs`** | **0** | 3 | – | – | – | – | – | – | – |
| `dg_wl_03_djs` | 10 | 2 | Y | – | Y | Y | Y | – | Y |
| `dg_wl_04_djs` | 8 | 2 | Y | Y | – | Y | Y | Y | – |
| `dg_wl_05_djs` | 9 | 3 | Y | Y | Y | Y | Y | Y | – |
| `dg_wl_06_djs` | 23 | 6 | Y | Y | Y | Y | Y | Y | – |
| `dg_wl_07_djs` | 21 | 5 | Y | Y | Y | Y | Y | Y | – |
| `dg_wl_08_djs` | 11 | 2 | Y | Y | Y | Y | Y | Y | – |
| `dm_qiliu_06_djs` | 18 | 5 | Y | Y | Y | Y | Y | Y | Y |
| `dm_qiliu_09_djs` | 12 | 4 | Y | Y | Y | Y | Y | Y | – |
| `dm_qiliu_12_djs` | 12 | 4 | Y | Y | Y | Y | Y | Y | – |
| `dm_qiliu_20_djs` | 10 | 3 | Y | Y | – | Y | Y | Y | – |
| `dm_qiliu_23_djs` | 12 | 3 | Y | Y | Y | Y | Y | Y | – |
| `dm_shangdian_05_djs` | 6 | 3 | Y | Y | – | – | Y | Y | – |
| `dm_shangdian_07_djs` | 17 | 5 | Y | Y | Y | Y | Y | Y | Y |
| `dm_wuqi_01_djs` | 11 | 3 | Y | Y | Y | – | – | Y | Y |
| `mz_kj01_djs` | 22 | 4 | Y | Y | Y | Y | Y | Y | – |
| `mz_kj03_djs` | 17 | 4 | Y | Y | Y | Y | Y | Y | – |
| **`mz_ks01_djs`** | **0** | 1 | – | – | – | – | – | – | – |
| `mz_sd01_djs` | 16 | 4 | Y | Y | Y | Y | Y | Y | Y |
| `mz_shandian01_djs` | 18 | 4 | Y | Y | Y | Y | Y | Y | Y |
| `mz_shandian02_djs` | 14 | 4 | Y | Y | Y | Y | Y | Y | Y |
| `mz_shandian03_djs` | 14 | 4 | Y | Y | Y | Y | Y | Y | Y |

**贴图槽**：33 个文件合计 **118 个槽位**（`Tex0` / `t_*`），其中 **69 条**归属到具体槽（其余槽在同一材质里为空/重复槽名）；槽→路径按“组内槽序 ↔ 文件内路径条目序”1:1 配对，**每条都带路径条目偏移**（例：`dg_wl_03`：`Tex0` → `effect\textures\glow\glow_01.tga`（off 1040）、`t_mask01` → `effect\textures\alpha\alpha_tp61_lsy_djs.tga`（off 1078））。**该配对是按序，不是语义直证**（本任务不取贴图内容）。

---

## 5. 逐 stem 总表（33 行）

| stem | gim/mesh/mtg row | bytes | sha16（4-4-4-4） | shader | technique | 宏 | 参数 | 槽 |
|---|---|---|---|---|---|---|---|---|
| `mod_skin_2003_029_14_hjl_djs` | 191892/191893/191894 | 1144 | `fe69 ebcf 562b fda1` | uber_fx_common | Effect | 2 | 7 | 3 |
| `mod_skin_2003_029_56_hjl_djs` | 192021/192022/192023 | 1662 | `bdab fcb6 d211 ab5e` | uber_fx_common | Effect | 4 | 19 | 4 |
| `mod_skin_2003_029_dg_01_djs` | 192057/192058/192059 | 1420 | `bbcb 9637 1be1 c61f` | uber_fx_common | Effect | 3 | 13 | 4 |
| `mod_skin_2003_029_dg_02_djs` | 192060/192061/192062 | 1265 | `53e7 facd c0cc 7909` | uber_fx_common | Effect | 2 | 11 | 3 |
| `mod_skin_2003_029_dg_04_djs` | 192066/192067/192068 | 1424 | `56f9 6998 c148 54ff` | uber_fx_common | Effect | 3 | 13 | 4 |
| `mod_skin_2003_029_dg_08_djs` | 192075/192076/192077 | 1919 | `0eda d080 e414 7fde` | uber_fx_common | Effect | 7 | 21 | 6 |
| `mod_skin_2003_029_dg_09_djs` | 192078/192079/192080 | 1433 | `3195 40e1 5f23 2294` | uber_fx_common | Effect | 3 | 13 | 4 |
| `mod_skin_2003_029_dg_10_djs` | 192081/192082/192083 | 1708 | `0e41 4e8b 6332 c9af` | uber_fx_common | Effect | 4 | 19 | 5 |
| `mod_skin_2003_029_dg_12_djs` | 192087/192088/192089 | 1578 | `435e d7f4 f294 31d9` | uber_fx_common | Effect | 3 | 18 | 4 |
| `mod_skin_2003_029_dg_14_djs` | 192093/192094/192095 | 857 | `0563 f255 7139 54f3` | uber_fx_common | Effect | 0 | 0 | 1 |
| `mod_skin_2003_029_dg_wl_01_djs` | 192096/192097/192098 | 1078 | `69a6 cf6a 3418 2d60` | uber_fx_common | Effect | 2 | 7 | 2 |
| `mod_skin_2003_029_dg_wl_02_djs` | 192099/192100/192101 | 985 | `dcff 3c55 605e 870f` | uber_fx_common | Effect | 2 | 0 | 3 |
| `mod_skin_2003_029_dg_wl_03_djs` | 192102/192103/192104 | 1139 | `14fd 99c4 da62 0b05` | uber_fx_common | Effect | 2 | 10 | 2 |
| `mod_skin_2003_029_dg_wl_04_djs` | 192105/192106/192107 | 1165 | `41ad 886b 3868 dd80` | uber_fx_common | Effect | 3 | 8 | 2 |
| `mod_skin_2003_029_dg_wl_05_djs` | 192108/192109/192110 | 1273 | `630d 2787 a5fa e46f` | uber_fx_common | Effect | 4 | 9 | 3 |
| `mod_skin_2003_029_dg_wl_06_djs` | 192111/192112/192113 | 1925 | `cf59 b251 110f ce2c` | uber_fx_common | Effect | 5 | 23 | 6 |
| `mod_skin_2003_029_dg_wl_07_djs` | 192114/192115/192116 | 1767 | `3022 6a80 52f9 ceeb` | uber_fx_common | Effect | 4 | 21 | 5 |
| `mod_skin_2003_029_dg_wl_08_djs` | 192117/192118/192119 | 1262 | `7b25 52e4 ea64 7714` | uber_fx_common | Effect | 3 | 11 | 2 |
| `mod_skin_2003_029_dm_qiliu_06_djs` | 192147/192148/192149 | 1719 | `e0df 9856 3372 e043` | uber_fx_common | Effect | 5 | 18 | 5 |
| `mod_skin_2003_029_dm_qiliu_09_djs` | 192156/192157/192158 | 1374 | `7d0c 4f9d 9f16 3c72` | uber_fx_common | Effect | 3 | 12 | 4 |
| `mod_skin_2003_029_dm_qiliu_12_djs` | 192165/192166/192167 | 1378 | `a2e3 c5d2 b10d 624a` | uber_fx_common | Effect | 3 | 12 | 4 |
| `mod_skin_2003_029_dm_qiliu_20_djs` | 192186/192187/192188 | 1241 | `38e0 d3d4 8ef6 395d` | uber_fx_common | Effect | 2 | 10 | 3 |
| `mod_skin_2003_029_dm_qiliu_23_djs` | 192192/192193/192194 | 1295 | `7fce 8d8b 2a3a a449` | uber_fx_common | Effect | 2 | 12 | 3 |
| `mod_skin_2003_029_dm_shangdian_05_djs` | 192201/192202/192203 | 1105 | `40f8 4522 c8ce 84eb` | uber_fx_common | Effect | 2 | 6 | 3 |
| `mod_skin_2003_029_dm_shangdian_07_djs` | 192207/192208/192209 | 1687 | `ac96 3e74 32da 488d` | uber_fx_common | Effect | 5 | 17 | 5 |
| `mod_skin_2003_029_dm_wuqi_01_djs` | 192210/192211/192212 | 1288 | `b7a6 f863 ec4b 6ebc` | uber_fx_common | Effect | 2 | 11 | 3 |
| `mod_skin_2003_029_mz_kj01_djs` | 192312/192313/192314 | 1838 | `bdd0 ee58 08d1 bc00` | uber_fx_common | Effect | 7 | 22 | 4 |
| `mod_skin_2003_029_mz_kj03_djs` | 192318/192319/192320 | 1648 | `ca9c 1c1b 45dc 8e46` | uber_fx_common | Effect | 6 | 17 | 4 |
| `mod_skin_2003_029_mz_ks01_djs` | 192321/192322/192323 | 1157 | `c15e e8d2 48a2 958f` | uber_mask_rim_diss | Effect | 4 | 0 | 1 |
| `mod_skin_2003_029_mz_sd01_djs` | 192324/192325/192326 | 1600 | `2c7a da94 cabb 0158` | uber_fx_common | Effect | 5 | 16 | 4 |
| `mod_skin_2003_029_mz_shandian01_djs` | 192327/192328/192329 | 1624 | `a0b6 ddb8 68ec a487` | uber_fx_common | Effect | 4 | 18 | 4 |
| `mod_skin_2003_029_mz_shandian02_djs` | 192330/192331/192332 | 1532 | `271f cc73 cda8 615c` | uber_fx_common | Effect | 5 | 14 | 4 |
| `mod_skin_2003_029_mz_shandian03_djs` | 192333/192334/192335 | 1498 | `e7ac d07d f536 9f8e` | uber_fx_common | Effect | 4 | 14 | 4 |

（`sha16` 逐条见 JSON；宏名全表见 JSON `stems[].macros`，示例：`USE_MASK01` 30 文件、`USE_MAIN_DISTORT` 19、`USE_DISSOLVE` 19、`USE_MASK02` 10、`USE_FRESNEL` 9、`ADD_COLORTEX` 7。）

**shader 家族（源级事实）**：**32/33 是 `uber_fx_common.fx::TShader`，唯一例外 `mz_ks01_djs` 用 `uber_mask_rim_diss.fx::TShader`** —— 这条对 adapter 有意义：`mz_ks01` 与其它 32 个不是同一材质族，参数表也为空。

---

## 6. 42 个 Model 节点 ↔ 33 个 stem 对照

- Model 节点总数 **42**（判据：节点含 `model_name` 或 `model_glb`）。
- **34 个**节点落在 1110177 的 33 个 stem 上（33 个 stem 全被引用；`dm_shangdian_07` 等有 2 个节点共用一个 stem）。
- **8 个 `no_mtg_sibling`**（模板引用的是**别的皮肤**的模型，本皮肤无同名 `.mtg`）：

| 节点 | 节点名 | stem | 归属皮肤 |
|---|---|---|---|
| [46] | M_模型_地扩散2 | `mod_skin_2003_022_jisha_dimiankuosan_hgz01_01_djs` | 2003_022 |
| [47] | H_模型_gow | `mod_skin_2003_022_jisha_glow_shu_hgz01_01_djs` | 2003_022 |
| [48] | M_地裂亮_1 | `mod_skin_2003_022_jisha_dilie_hgz01_01_djs` | 2003_022 |
| [50] | L_m_扩散_02 | `mod_skin_2003_022_kuosan_hgz_02_djs` | 2003_022 |
| [52] | M_模型气流升_1 | `mod_skin_2003_022_jisha_qiliu_01_djs` | 2003_022 |
| [54] | M_模型气流升_1_1_1 | `mod_skin_2003_022_jisha_qiliu_01_djs` | 2003_022 |
| [57] | M_mod_地裂流光_1_1 | `mod_sandian_02_hjl_djs` | 2003_019 |
| [58] | M_模型_金线1 | `mod_skin_2003_018_bp_baoci_hgz01_02` | 2003_018 |

节点→stem→材质/宏/贴图 的完整对照（42 行）在 JSON `model_nodes_all`；单节点示例：
`node[4] L_模型_科技01` → `mz_kj01_djs` → 宏 `USE_MASK01/USE_MASK02/USE_DISSOLVE/USE_MAIN_DISTORT/USE_MAIN_POLAR_UV/…`、参数 22 项（含 `u_emissive_highlight_intensity`、`u_mask_intensity`、`u_dissolve_amount`）、贴图 4 槽。

---

## 7. 交叉核对（与 `.sfx` 34 条声明名）

- **精确同名交集：3 条** —— `effect\textures\glow\glow_01.tga`、`effect\textures\veins\noise_04_tp05.tga`、`effect\textures\veins\tex_noise_y.tga`（`.mtg` 里逐字相同）。
- **同 stem 不同扩展名：1 条** —— `.sfx` 声明 `effect\textures\lightning\shandian_05_yh_djs.spr`，`.mtg` 里点名的是同 stem 的 `.tga`。
- 路径口径说明：本任务“槽归属路径”**69 条**；上一棒对整段文本做正则得到 **72 条**字符串。差值 3 条是**出现在文本里但未归属到任何槽位组**的路径（例如 `dg_14` 只有 1 条路径且无材质块）——两个数字都保留、不混用。
- `.mtg` 里出现、但不在 34 条声明名里的路径（示例）：`effect\textures\veins\tex_noise01_yb52.tga`、`effect\textures\weapon\...`（武器本体贴图 `weapon\skin\skin_2003_029\textures\skin_2003_029001a.tga`）等 ⇒ 说明**模型层的贴图需求比 sfx 声明更宽**。

---

## 8. 未解清单与只读核对

**未解（如实登记，不猜）**
1. `RenderStates` 值区“前导字节 → 字段名”映射（缺引擎 schema）⇒ `TransparentMode`/`AlphaRef`/4 个布尔/4 个颜色的**名称归属**未定证。
2. `.mtg` 侧 `TransparentMode` 的**数值**（本任务未取得；只有字段名）。
3. 每个 `.mtg` 有 **2 个材质记录**，与 42 个 Model 节点的**逐一归属**未定（一个 stem 可能被多个节点共用）。
4. 69/72 条声明贴图的**内容**未取（名字轴已定案：idx 内容寻址、无名字，本任务不覆盖）。
5. 值区块约 15% 字节未被解析器消费（stray），已逐文件记入 JSON `stray_bytes`。

**只读核对（改前 → 改后，sha16）**

| 文件 | 改前 | 改后 |
|---|---|---|
| `1110177/effects.json` | `4661BD5CFE44457E` | 同前（未改） |
| `weapon_skin_viewer.js` | `B9C7281E1EE7A819` | 同前（未改） |
| `weapon_skin_sfx_adapter.js` | `79F5F2B86D321995` | 同前（未改） |
| `1110177/neox_material.json` | `A05C4F2C8DDFCF9A` | 同前（未改） |
| `board.html` | `2585162AF98DB68E` | 同前（未改） |
| `viewer.json` | 不在该路径（缺失） | — |

本轮**新增**文件：`MTG_MATERIALS_20260919.md`、`MTG_MATERIALS_20260919.json`、`MTG_raw/`（33 个）。可选副本目录 `1110177/mtg/` **未创建**（task 里标为可选；如需 adapter 直接读取，可再派单，我不擅自写 viewer 侧目录）。

---

## 9. 复现

| 脚本（`%TEMP%`） | 作用 |
|---|---|
| `MTG_explore.py` | 解出 33 个 `.mtg` 到 `%TEMP%\mtg033`，跑既有 `c159_pair`/`c159_slot_parser` |
| `MTG_parse2.py` | 单一文件的块结构验证（`<01 00><count><record>`） |
| `MTG_build.py` | 全量解析 + 落 `MTG_raw/` + stage1 JSON |
| `MTG_final.py` / `MTG_final2.py` | Q1/Q2、42 节点对照、交叉核对、机读 JSON 组装 |
| `MTG_tables.py` | 类别矩阵与报告表数据 |
| `MTG_state_dump.py` / `MTG_bytemap.py` | 值区偏移化 hex 转储（复核用） |
