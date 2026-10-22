# task-56 独立复测报告（viewer-auditor）

**结论速览：PASS 4 · WARN 1 · 无法判定/未复现 1 · 未做 0**
判据 `criterion=mask/weapon_box`（定义见 `MASK_CRITERION.md`）。**我只认自己的读数；与 chain-auditor 的数值逐条并列，不附和。**

## 0. 运行与 pin（两阶段；第二阶段因 Lead 的 adapter 变更而加跑）
| 阶段 | viewer.js | adapter | `1110177/viewer.json` | `1110171/viewer.json` | `1110177/effects.json` | board |
|---|---|---|---|---|---|---|
| **① `C3AFFD4F` 期**（运行中跨过变更） | `3B9999B992FE8763` | 起 `C3AFFD4F77F042C1` → 末 `FF6FA07C6621EFC0` | `D7DA78F87C625303` | `62E7BDDC9CF6EC6D` | `0BB7CA57E7D1BE0B` | 起 `20A4D8C3B7E9BD44` |
| **② `FF6FA07C` 期（单位换算修复后）** | `3B9999B992FE8763` | **`FF6FA07C6621EFC0`**（前后一致） | `D7DA78F87C625303` | `62E7BDDC9CF6EC6D` | `FD8840722D39FA4E`（**未内联进 viewer.json**） | `4E9B2421B3210C2F` |

**版本自证（不信 `?v=`）**：阶段②页内 `fetch('/assets/weapon_skin_sfx_adapter.js',{cache:'no-store'})` → **200 / 72,915 B / sha256[:16] = `FF6FA07C6621EFC0`**（= 磁盘现值）；`fetch('/assets/weapon_skin_viewer.js')` → **200 / 330,804 B / `3B9999B992FE8763`**。阶段②全部 SFX 读数**均属 `FF6FA07C…`**；阶段①的 SFX ON 读数为 `C3AFFD4F77F042C1`（页面加载时该版本），末次 pin 变更发生在我的测量之后。

## 1. P1-1 网络侧 404 归零 —— **PASS（独立复现成功）**
判据：抓 `Network.responseReceived` 中所有含 `/sfx/tex/` 的响应；`gpk_1229.png` 单列。
- **阶段①：12 条 `/sfx/tex/` 请求，200×12、404×0**（1110177 五张：`glow_16_yh_djs__7ce99117`、`lightning_01__662b911e`、`dian_12__7240b831`、`glow_01__13211b02`、`shandian_05_yh_djs__a9aa4caf`；1110171 七张）。
- **阶段②：5 条 `/sfx/tex/` 请求，200×5、404×0**（同一批 1110177 贴图）。
- 既有项单列：`1110177/src_tex/gpk_1229.png` = **404**（task-46 既有）；`1110171/src_tex/gpk_1229.png` = **200**。
- 交付层：`weapon_skin_viewer.js?v=3b9999b992fe` → **200**、`weapon_skin_sfx_adapter.js?v=c3affd4f77f0`（阶段①）/ 实字节 `FF6FA07C`（阶段②）→ **200**；**无 304**（新 profile + `?v=`）。

## 2. P1-2 MASK 五读数 —— **PASS（默认态无变化）**
| 皮肤 / 状态 | 版本 | 帧 sha16（N≥5 门） | 五读数（mask 口径） | 与基线 |
|---|---|---|---|---|
| 1110171 OFF | ① | `48b6c95c1165c80a`（gate_ok=true） | p50 **0.1232** / p95 **0.4865** / >0.5 **3.394%** / >0.75 **0.273%** / 暖色 **0.106%**（mask 2.449%，n=34,857） | **与基线逐项相同** ✅ |
| 1110177 OFF | ① | `3a6f3bd4a4147c59`（gate_ok=true） | p50 **0.2829** / p95 **0.5745** / >0.5 **18.242%** / >0.75 **0.989%** / 暖色 **0.689%**（mask 1.826%，n=25,995） | **与基线逐项相同**（**数据版本已变：撤回 1 条矛盾绑定，但默认帧未变**） |
| 1110177 OFF | ② | `e62c1c58e5bdc383`（gate_ok=true） | 同 ① 五项**逐位相同** | **五读数与 ① 一致；但跨载入帧 sha 不同**（① `3a6f3bd4a4147c59` vs ② `e62c1c58e5bdc383`）⇒ 再次印证"门只保证载入内稳定、跨载入用五读数" |
| 1110171 ON @t=0.55 | ① | `102f94be0c8919c6` | p50 **0.2099** / p95 **0.8629** / >0.5 **9.363%** / >0.75 **5.454%** / 暖色 **3.322%**（mask 3.236%，n=46,062） | 该皮肤自闪点（非默认态） |
| 1110177 ON @t=1.175 | ① | `d2a427e8c8251522` | p50 **0.3683** / p95 **0.5801** / >0.5 **14.788%** / >0.75 **2.061%** / 暖色 **0.468%**（mask 3.709%，n=52,786） | 同相位 OFF 差分 effect-only **2.3608% 画布** |
| 1110177 ON @t=1.175 | ② | `72a7ad3648f76c58` | 见 §3.2（屏幕度量） | effect-only **0.4284% 画布** |

## 3. P1-3 闪帧窗口 / 尺寸 / effect-only —— **PASS：「一大块」在世界与屏幕两个口径都被修掉**
### 3.1 阶段②（`FF6FA07C`，t=1.175 峰值）逐节点**世界**尺寸 vs 武器对角线（武器 `15.4551`）
| 节点 | opacity | scale | world diag | **/武器对角线** | map |
|---|---|---|---|---|---|
| `M_g_glow_an` | 0.0447 | [0.6, 0.6] | 0.8485 | **0.0549** | `glow_01__13211b02.png` |
| `H_g_glow地_an` | 0.03 | [1.3, 1.3] | 1.8385 | **0.119** | `glow_01__13211b02.png` |
| `H_公告板_爆闪2` | 0.2322 | [5, 5] | 7.0711 | **0.4575** | `glow_01__13211b02.png` |
| `H_p_星点_02` | 1 | [0.1, 0.1] | 0.1414 | **0.0091** | `glow_16_yh_djs__7ce99117.png` |
| `H_ shandian01_1_1` | 1 | [0.1, 0.1] | 0.1414 | **0.0091** | `lightning_01__662b911e.png` |
| `H_鬼火_lizi_1` | 1 | [0.1, 0.1] | 0.1414 | **0.0091** | `dian_12__7240b831.png` |
| `M_lizi_闪电_01` | 1 | [0.1, 0.1] | 0.1414 | **0.0091** | `shandian_05_yh_djs__a9aa4caf.png` |
| `L_p_星点_02` | 1 | [0.1, 0.1] | 0.1414 | **0.0091** | `glow_16_yh_djs__7ce99117.png` |
- 特效层包围盒 **5×5（diag 7.0711）= 0.4575× 武器**（对照：修复前 `50×50 / diag 70.711` = **4.5752×**；钳制-only 期最大节点 `9.2731` = 0.60× 顶到钳制帽）。
- **钳制帽 0.60× 已不再触发**（最大节点 5 < 9.2731）——与 Lead 预期一致；但 `unitScale()` / `__sfxDiag()` 在本 build **`typeof !== 'function'` ⇒ 拿不到 `quad_clamped` / `unit_scale_on`，标未证**。
- 另观察到 5 个 PS 回退单面节点（`H_p_星点_02` / `H_ shandian01_1_1` / `H_鬼火_lizi_1` / `M_lizi_闪电_01` / `L_p_星点_02`）**scale=0.1（0.0091× 武器对角线）**，其中 `H_p_星点_02` `chainVisible=false` ⇒ 这些新回退面在屏幕上几乎不可见（见 §7.2）。

### 3.2 阶段② 屏幕空间（t 扫描，与同相位 OFF 差分，门限 >8/255）
| t(s) | sha16 | flash_px | % 画布 | 闪/武器 bbox 对角比 | bbox 填充率 | core_share | interior_share |
|---|---|---|---|---|---|---|---|
| 1.1 | `451683230c59e69d` | 24 | 0.0017 | 0.012 | 0.96 | 0.625 | 0.375 |
| 1.13 | `6f233593f287a184` | 4166 | 0.2927 | 0.264 | 0.367 | 0.004 | 0.911 |
| 1.15 | `2de7ae1a88c09491` | 5664 | 0.3979 | 0.281 | 0.442 | 0.003 | 0.924 |
| 1.175 | `72a7ad3648f76c58` | 6098 | 0.4284 | 0.285 | 0.459 | 0.535 | 0.926 |
| 1.2 | `1157e53c7e4f25e7` | 5430 | 0.3815 | 0.278 | 0.43 | 0.003 | 0.922 |
| 1.225 | `a272e64ef3218840` | 37 | 0.0026 | 0.219 | 0.005 | 0.405 | 0.243 |
| 1.25 | `451683230c59e69d` | 24 | 0.0017 | 0.012 | 0.96 | 0.625 | 0.375 |
（explanation: 1.10/1.25 两点的极低 flash_px 表示"窗口外"；有效窗口 1.13–1.20，峰值 **1.175**。）

### 3.3 阶段①（钳制-only `C3AFFD4F`）同法对照
| t(s) | sha16 | flash_px | % 画布 | 闪/武器 bbox 对角比 | core_share |
|---|---|---|---|---|---|
| 1.1 | `8e4eef8b2692160f` | 4507 | 0.3166 | 0.266 | 0.105 |
| 1.13 | `88083eb8901b3f20` | 27400 | 1.925 | 0.498 | 0.039 |
| 1.15 | `9b91279a0640217b` | 32144 | 2.2583 | 0.512 | 0.039 |
| 1.175 | `d2a427e8c8251522` | 33602 | 2.3608 | 0.517 | 0.04 |
| 1.2 | `c75a121f3e05c7ba` | 31887 | 2.2403 | 0.517 | 0.039 |
| 1.225 | `66adcd3f86e70188` | 19788 | 1.3902 | 0.538 | 0.049 |
| 1.25 | `c43e9bdfed5da6d6` | 14315 | 1.0057 | 0.552 | 0.062 |

### 3.4 三档纵向对照（同一 t=1.175、同判据）
| 版本 | 世界里最大节点 / 武器 | 屏幕闪/武器 bbox 对角比 | effect-only % 画布 |
|---|---|---|---|
| 基线（无钳制、无单位换算，我改前基线） | 50×50 = **3.235×**（层 4.5752×） | — | **38.08%** |
| 钳制-only `C3AFFD4F` | 9.2731 = **0.60×**（顶帽） | **0.517** | **2.3608%** |
| **单位换算后 `FF6FA07C`** | 5.0 = **0.323×**（`H_公告板_爆闪2`；层 0.4575×） | **0.285** | **0.4284%** |
⇒ **独立复现成功**：flash 面积降到钳制-only 期的 **1/5.5**、改前基线的 **1/89**；屏幕 bbox 对角比 **0.285** 落在 Lead 预期的 0.10–0.32× 内。

### 3.5 我亲眼看的描述（`FX53b_1110177_on_t1175.png`，sha `72a7ad3648f76c58`）
**不再是一大块**：画面里只有**剑刃右侧一小团柔和的白色/淡青光晕**（屏幕 bbox ≈ **91×146 px**，对角约为武器 bbox 的 **28%**），边缘渐隐、**无明显方形边界与硬直四角**；既不像"方形亮块"，也不像清晰的闪电分叉或星点群，**更像一次小范围爆闪/辉光**（贴图确为 `glow_01__13211b02.png` 径向辉光，形态一致）。**与用户"还是一大块的闪"在本读数下不再对应**——除非用户浏览器仍在跑缓存旧 adapter（我无法证明用户端，见 §7.3）。

## 4. P2-4 负控（`sprite_only` / `model_only` / `all_off`）—— **无法判定 / 未复现**
| 控制态 | 帧1 sha16 | 帧2（≥1.3 s 后） | 两帧相同 | `adaptSwitches()` 读回 |
|---|---|---|---|---|
| sprite_only | `72a7ad3648f76c58` | `72a7ad3648f76c58` | True | `{"spriteFix": true, "clampOn": true, "clampK": 0.6, "psFallbackOn": true, "spriteOn": null, "blend7": "normal"}` |
| model_only | `72a7ad3648f76c58` | `72a7ad3648f76c58` | True | `{"spriteFix": true, "clampOn": true, "clampK": 0.6, "psFallbackOn": true, "spriteOn": null, "blend7": "normal"}` |
| all_off | `72a7ad3648f76c58` | `72a7ad3648f76c58` | True | `{"spriteFix": true, "clampOn": true, "clampK": 0.6, "psFallbackOn": true, "spriteOn": null, "blend7": "normal"}` |
- 三种控制态**帧完全相同**，且都等于 t=1.175 的 ON 峰值帧 `72a7ad3648f76c58` ⇒ **我这一侧没有复现 chain-auditor 的 `sprite_only 2873eb380e0b6e30(alive=7)` / `model_only=all_off=8352c4e30bbaf981(alive=0)`**。
- **【2026-09-19 更正，Lead 转 shader-auditor 只读定证】根因不是"API 未注册"**，而是**我的 harness 少了一步**：
  1. `spriteOn` 恒为 `null` 是**设计语义**（adapter L834：`if(SPRITE_ON===null) return {spriteOn:null, note:'follow_sfx_switch'}`）⇒ `null` = 跟随 SFX 总开关；**负控必须先显式调用 `WikiSfxAdapter.sprites(true/false)`（L830 注册）**并断言 `typeof spriteOn==='boolean'`。我调用的是 `__spriteOn(true/false)`，语义不同 ⇒ 三态帧当然相同。
  2. `adaptSwitches` "时有时无" = **装载时序**：adapter 在文件末尾（L959）才 `window.WikiSfxAdapter=`，而 `board.html` 用 `script defer` ⇒ 我在 `Page.navigate` 后未等 `readyState==='complete'` 就 evaluate。全仓只有 board 一处 `script` 引入 adapter，**不存在两次装载/副本互盖**（我先前"疑似两副本"的推断**撤回**）。
  ⇒ 因此 §4 的判定由"API 未注册"更正为：**我的负控执行无效（harness 缺陷），独立复现失败**；是否复现 chain-auditor 的负控结论**待下一轮**用 `sprites(true/false)` + 布尔断言重做（已写入预置 harness `%TEMP%\fx58_retest.py` 的 controls 段）。
- （已撤回）~~同一页面内 API 面自相矛盾 ⇒ 疑似两次装载~~：见上条 2。

## 5. P2-5 异常归属 —— **我的两阶段异常数 = 0（chain-auditor 的 Uncaught 未复现）**
- `Runtime.exceptionThrown`：阶段① **0 条**、阶段② **0 条**（我的注入含 `Runtime.evaluate` + `awaitPromise` 异步 IIFE + 动态 `import()`）。
- ⇒ **未能复现** chain-auditor 的 `scriptId 20 / line 0 / col 22`；因此我**不能**替它定证"来自注入"。我能确定的只是：**在我这套注入下页面没有该异常**。要定证需拿他们的注入清单逐个二分（**未做**）。
- 非异常噪声：`favicon.ico` 404、`1110177/src_tex/gpk_1229.png` 404（既有）；无其它。

## 6. P2-6 `report` 口径 —— **WARN：三源 `pending_hidden` 不一致**
| 皮肤 | `applied == prims 数` | failed/missing | `report.prims[i].pending_hidden` | `__texReady().pending_hidden_total` | `__acceptanceReport().pending_hidden_total` |
|---|---|---|---|---|---|
| 1110177 | **3 == 3** ✅ | `[]` / `[]` ✅ | **0** | **0** | **0** ✅ 三源一致 |
| 1110171 | **7 == 7** ✅ | `[]` / `[]` ✅ | **2** | **0** | **0** ❌ **不一致** |
最小复现：阶段①、皮肤 **1110171**、`board.html?b=weapon_skin_sfx_text_sources&view=wiki&sort=id&dir=desc` → `open()` → 等 `env_warn=null` 且 `missing=[]` → 同时读三源：`report.prims` 计得 2 个 `pending_hidden=true`，而两个聚合口径都为 0。**第二阶段未重跑 1110171 的 report ⇒ 标 WARN 待复核。**
**【2026-09-19 更正，Lead 转 shader-auditor 定证】归因**：`__neox().report.prims[i]` 是**建材质时刻的快照**且会被晚到的旧报告覆盖；`__texReady()` / `__acceptanceReport()` 是**读取时现算（live）** ⇒ settle 期 live 两源 = 0 准确，**WARN 的准确表述是"`report` 侧陈旧"**（不是 live 口径错）。修法在 viewer.js（shader-auditor 写域，已排入其下一轮）。我的最小复现仍是该差异的有效证据。

## 7. 需要 Lead 决策/注意
1. **负控重做**（§4 更正后）：下一轮按 `WikiSfxAdapter.sprites(true/false)` + `models(true/false)` + `typeof spriteOn==='boolean'` 断言重做三态 A/B；已预置在 `%TEMP%\fx58_retest.py`。
2. **PS 回退单面节点 scale=0.1（0.0091× 武器对角线）**：屏幕上几乎看不见；若它们是"星点/闪电"的来源，量级可能**过小**（0.1 单位=1 cm）⇒ 与"只剩一小团光"的观感一致。请判是否改用源 `Radius`/`TrackScale` 而非固定 0.1。
3. **交付层**：我只能证明**服务端字节**与**本机新 profile** 装载的都是新版（页内 fetch 实字节 sha16 自证）；**无法证明用户浏览器不是旧缓存**。

## 8. 纪律
- 只读（只写本报告 + `FX53_VERIFY_readings.json` + `%TEMP%` 脚本 + `FX53*/FX53b*` 截图）；两阶段各只起 **1 个**浏览器；均按 `user-data-dir` 反查真实 PID 后 `taskkill /T /F`（阶段①杀 8 个、阶段②杀 8 个）；端口 **10099 / 10101 / 10103 无 LISTEN**、匹配 `FX53*_prof` 的 chrome = 0。
- 原始数据：`FX53_VERIFY_readings.json`（含 `verdicts`）；截图 `FX53_*.png`（阶段①）、`FX53b_*.png`（阶段②）。
