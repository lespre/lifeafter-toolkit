# adapter 缺口可执行清单（task-30 第 3 条，chain-auditor）

对象：`08Lifeafter wiki/assets/weapon_skin_sfx_adapter.js`（现状以 **改后 sha16 `1cd4ac5454d1f27a`** 为准）；声明依据：`FXSHADER_uber_fx_common.nfx2`；驱动计数来自 `MODELTEX_1110152.json` 与 `FXMODEL_1110171_tex_viewer_effects.json`。


## 结论一句话

**11 条缺口里，只有 2 条『有源驱动且公式未定证』（dissolve、distort），其余 9 条**要么源里 0 驱动**、要么只缺一张实体贴图 ⇒ 建议全部**不接**，维持现状（默认关 + fail-closed），不产生新的近似值。


## 逐条

| # | 项 | 源是否驱动 | adapter 现状 | 缺什么 | 所需数据 | 建议 |
|---|---|---|---|---|---|---|
| 1 | u_dissolve_amount / dissolve 族 | 1110152 有 9 处（2 个大法阵节点，值 0/0.5） | 0 次出现（未接） | 溶解阈值→裁剪/alphaTest 的实现 | dissolve 公式（uber_fx_common PS 字节码/pipes）+ t_dissolve_tex/t_dissolve_dirmask_tex 实际贴图 | 可接（有源驱动 + nfx2 声明），但公式未定证 ⇒ 先按 clip(alpha - amount) 的**近似**并在 basis 标注？—— 不，公式未定证 ⇒ 暂不接，等字节码或实测 A/B |
| 2 | u_distort1_intensity / distort 族 | 1110152 有 5 处（节点 #6/#7） | 0 次出现（未接） | UV 扰动实现 | 扰动公式 + t_distort_tex1/2 分辨率口径 | 暂不接（同因：公式未定证） |
| 3 | u_emissive_highlight_intensity | 1110152 50 处、1110171 36 处 | 8 处引用（行 48/131/186/220/329/368…）——仅作**缺失时的回落常量**，未作为强度乘子 | 该参数的**语义**（高光项 vs 全局增益）与乘入位置 | PS 字节码中该 uniform 的使用点 | 维持不乘（现状即 correct-by-default） |
| 4 | u_maintex_rotation / speed / tilling / offset（UV 族） | rotation 有驱动（1110152 3 处、1110171 无；adapter 已接 4 处引用）；speed/tilling/offset **源数据 0 次** | rotation 已接（轴=本地 Z 未证 ⇒ approximate）；speed/tilling/offset 0 次 | speed/tilling/offset 无源驱动 ⇒ **没有驱动数据可接** | 若某皮肤出现这些属性，再按 nfx2 声明（u_maintex_speed_x/y 等）接 | 不接（无驱动）；rotation 的轴保留 approximate |
| 5 | u_fresnel* 边缘光 | 1110171 有 6 处（2 节点驱动 u_fresnel_color）；1110152 的 26 节点 **0 个**驱动 | 0 次出现（未接） | Fresnel 项实现 + 宏 USE_FRESNEL 开关值 | fresnel 公式（字节码）+ 宏开关值 | 不接（24 节点无驱动；1110171 的 2 节点需公式） |
| 6 | ADD_COLORTEX 第二贴图层（u_addcolor_intensity / t_addColor_tex / u_addcolortex_*） | 两份审计源里 0 次 | 0 次出现（未接） | 第二层贴图 + 叠加公式 | t_addColor_tex 实际贴图 + 宏开关值/默认值 | 不接（无驱动） |
| 7 | SoftParticle / 深度淡出（u_softparticle + t_depth_tex） | 两份审计源里 0 次（Model 节点） | 0 次出现（未接） | 深度图接入（viewer 无 depth texture） | 深度纹理 + 公式 | 不接（无驱动；且影响 Sprite/Particle 而非 Model） |
| 8 | VertexColor（COLOR_0） | 宏 USE_VERTEXCOLOR 值未定证；源数据未见驱动 | 0 次出现；export_glb.py 不导出 COLOR_0（既有结论） | GLB COLOR_0 流 + 宏开关值 | 带 COLOR_0 的 GLB + 宏值 | 不接（无驱动证据）；若将来需要，先定宏值再重导 GLB |
| 9 | u_emissive_mix / power / desaturate / grey_intensity / u_alpha_ref | 两份审计源里 0 次 | 全部 0 次出现 | 同上，无驱动数据 | — | 不接（无驱动） |
| 10 | 枚举值表（TransparentMode/RenderBias/DirType/BlendMode） | 属性本身有驱动（取值全为数值字符串） | blending 用 '0'→Normal / '2'→Additive 近似；RenderBias/TrackType 未映射 | name↔int 值表 | 引擎侧枚举定义（已判 NOT_FOUND，见 FXENUM_probe_report.json） | 维持 approximate + 明文禁令（禁止用观测分布反推枚举名）；已写入 modelBranchBasis.enumValueTable |
| 11 | 2 个 Tex0 节点的环贴图 | — | fail-closed（无贴图即不渲染该节点） | 两张环贴图实体 | freeze-auditor 的内容特征匹配结果 | 等对方结论；不顶替 |

## 本次 adapter 改动（裁决①③）与『仅注释/诊断』证明

改前：`weapon_skin_sfx_adapter.js.bak_20260918_215545`（55,263 B，sha16 `2e61c5234bb37ced`，已校验为逐字节原文）；改后：57,692 B，sha16 `1cd4ac5454d1f27a`，`node --check` 通过。

diff（before → after）：**新增 21 行 / 删除 2 行**；其中删除-新增成对的 2 行是**同一行文字加长**（`'blending'` 注记尾追加『证据与禁令见 enumValueTable』）。判据：删除行里**不含任何代码语句**（正则筛 `function|var |if (|return |=>|else` 命中 = 0）⇒ **代码路径未变**，默认关/fail-closed 未动。


```diff

--- before
+++ after
@@ -51,0 +52,5 @@
+  /* ★ 枚举值表禁令（2026-09-18，chain-auditor；裁决③）：TransparentMode/RenderBias/DirType/BlendMode 的
+     name↔int 值表在已扫范围内**不存在**（详见 modelBranchBasis.enumValueTable 与
+     `03拆包产物\_target_1110171\FXENUM_probe_report.json`）
+     ⇒ 本模块对它们的任何映射只能是 **approximate（观测分布，非值表）**；
+     ★ **禁止用观测分布反推枚举名**（观测分布只能证明"哪些整数出现过"，不能证明"哪个整数叫什么"）。 */
@@ -669,0 +675,3 @@
+          /* ★ 枚举值表探测结论（NOT_FOUND，2026-09-18，chain-auditor；证据 _target_1110171\FXENUM_probe_report.json）
+             ★ 明文禁令：**禁止用观测分布反推枚举名** —— 观测分布只能证明"哪些整数取值出现过"，
+               不能证明"哪个整数叫什么"；本项保持 unresolved，默认仍关、仍 fail-closed。 */
@@ -674 +682 @@
-            'blending': "approximate: TransparentMode '0'→NormalBlending / '2'→AdditiveBlending（映射语义未在源中验证；值为源属性原值）",
+            'blending': "approximate: TransparentMode '0'→NormalBlending / '2'→AdditiveBlending（映射语义未在源中验证；值为源属性原值；证据与禁令见 enumValueTable）",
@@ -676 +684,12 @@
-            'bridge': 'SRC_BRIDGE_1110152（逐节点源值 + xml_line）；运行时字段优先'
+            'bridge': 'SRC_BRIDGE_1110152（逐节点源值 + xml_line）；运行时字段优先',
+            /* ★ 值表探测结论（NOT_FOUND）：已扫范围内不存在 name↔int 值表 ⇒ 现有映射一律标 approximate */
+            enumValueTable: 'NOT_FOUND: 枚举值表在已扫范围内不存在'
+              + '（① 10 个皮肤 .sfx（XML-like 文本）10/10 命中这 4 个属性名，但取值全是数值字符串、非数值取值 0 个；'
+              + '② uber_fx_common.nfx2 里 TransparentMode/RenderBias/DirType/BlendMode 各 0 次，其 enum 只有宏名族 INSTANCE_TYPE_*/NEOX_DEBUG_*；'
+              + '③ 客户端 bin 1,017 文件 / 4.26 GB 全扫（含 lifeafter.exe×4，无 >400MB 跳过），409 命中全在第三方库'
+              + '（libcef/Chromium/Skia/Qt/ffmpeg），游戏自有模块 0 命中；④ task-30 既有台账：shader 0 / 50MB 脚本配置数据 0）'
+              + ' ⇒ 当前映射是 approximate（观测分布，非值表）。全量观测分布（10 个皮肤 .sfx）：'
+              + 'TransparentMode {0:213, 2:31, 5:29}；RenderBias {2:114, 0:67, 1:60, 3:35, 4:30, -1:21, 5:6, -2:6, 6:2}；'
+              + 'DirType {2:280, 0:55, 7:4, 1:2}；BlendMode {2:32, 8:27, 0:9}；TrackType {0:316, 4:84, 3:14, 1:4}。'
+              + '★ 禁令：禁止用观测分布反推枚举名（观测分布不能证明整数↔名字）。'
+              + '★ 值表真值来源只剩引擎侧定义/静态逆向，不在本任务口径内 ⇒ 保持 unresolved。',

```


## 明文禁令（裁决③）

**禁止用观测分布反推枚举名。** 已写入两处：文件头注释（L53-56）+ `modelBranchBasis.enumValueTable`（L676/L686-695）；报告侧见 `FXENUM_probe_report.json`。
