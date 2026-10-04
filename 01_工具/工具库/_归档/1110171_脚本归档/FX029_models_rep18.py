# -*- coding: utf-8 -*-
import io, os, hashlib, sys
sys.stdout.reconfigure(encoding='utf-8')
REP = r'E:\la拆包项目\03拆包产物\_target_1110171\FX029_models_report.md'
sec = u'''

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
2. **交叉核对事实**：我的注入与我方块解析 **26/26 一致**（脚本 `%TEMP%\\fx061_verify.py`）；再与 `model_fields.shader.ShaderComponent` 的声明列（上一轮独立解析）一致 —— 例：`L_模型_科技01` 块偏移 11894 / 长 3237，块内**恰好 1 个组件**，其 uniforms = `{u_overall_opacity, u_emissivecolor, u_dissolve_amount}`。
3. **双方差异的来源（事实，不下断言）**：renderer-auditor 的 `pairing_divergence.driver_set_matches` 显示**整体错位一格**（其 #3=我 #2、#5=我 #4/#6、#20=我 #19、#23=我 #22、#24=我 #23、#26=我 #25/#26）⇒ 与"最近**前置**组件"在有嵌套结构时的错位一致。**另有一点必须澄清**：其 `driver_diffs` 标的 `only_mine` 与我方公开表**不符**（例：`L_模型_科技01` 其记我方 = `{u_depth_bias, u_emissive_intensity}`，而我方该行实为 `{u_overall_opacity, u_emissivecolor, u_dissolve_amount}`，恰等于其 #1 行 = 该块自身集合）⇒ 其比较器除配对规则外**还有一处对齐问题**。**影响面**：以我方嵌套规则为准时，颜色/透明度**未挂错节点**（26/26 块级核对通过；A/B/C=16/7/3 亦与 lead 裁定一致）；建议 renderer-auditor 用嵌套规则重出一列即可对齐。

### 18.7 宏门（lead 追加 2）
`model_fields.shader.ShaderComponent` 里 `Type==='Bool'` 的条目 = **6 条 / 4 个 Model 节点**（`USE_EMISSIVE_CONTROL`×4：`L_模型特效_01`、`H_模型核心电小_3`、`M_模型核心电小_4`、`H_模型核心电小_5`；`USE_SOFTPARTICLE`×2 于后两者）。
⚠ 口径差异：renderer-auditor 报 `USE_EMISSIVE_CONTROL` **6 处 / 10 个非空宏块**（含 `USE_SFXLIGHT_FOG`/`USE_VERTEXCOLOR`/`USE_MASK01`）—— 那是**全节点类型**计数；**Model 节点内**只有上述 6 条 / 4 节点。两者不冲突，但引用时必须写清范围。

### 18.8 未证 / 未做
- 未证：`TransparentMode`→混合状态映射（静态不可得，已收窄到极限）· `u_depth_bias` 引擎侧单位/阶段 · 贴图槽↔源名（26/26 未绑）· 颜色列序 U5（取 `COLOR_ORDER='rgba'`，与 1110152 时代 `(A,R,G,B)` 之说并存）· 自发光子集被省略因子的引擎默认值。
- 未做：`u_dissolve_amount` 公式**未接**（12 节点，仅登记「下一项可接」）· 未填任何 UV tilling/offset · 未手填贴图 · 未改 `unitScale/sprSlice/colorOrder/psFallback` 语义 · 未碰 viewer.js/viewer.json/manifest/board/registry · 未做 task-62。
'''
old = io.open(REP, 'r', encoding='utf-8').read()
if u'§18 task-61' not in old:
    io.open(REP, 'a', encoding='utf-8').write(sec)
    print('已追加 §18')
print('报告 sha16 =', hashlib.sha256(open(REP, 'rb').read()).hexdigest()[:16].upper(), os.path.getsize(REP), 'B')
