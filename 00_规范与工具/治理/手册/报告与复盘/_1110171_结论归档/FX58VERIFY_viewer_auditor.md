# SFX 链独立复测报告（viewer-auditor）

**结论速览：PASS 6 · WARN 1 · 未抓到 1（如实）**；另附 **1 条我自己的方法学发现（adapter API 挂载时机）** 与 **1 条口径更正（`__sfxDiag()` 字段名）**。
判据：`criterion=mask/weapon_box`（定义见 `MASK_CRITERION.md`）；`effect-only` = 同相位 ON vs OFF 差分（门限 >8/255，分母=整幅画面）。**只认我的读数，不附和。**

## 0. pin（运行前后一致；含页内实字节自证）
| 对象 | 磁盘 = 期望（Lead 防呆文件） | 页内 `fetch` 实字节 |
|---|---|---|
| `weapon_skin_viewer.js` | `4647CF0BE061AD81` ✅ | **200 / 335,971 B / `4647CF0BE061AD81`** |
| `weapon_skin_sfx_adapter.js` | `544D3A4A1B2CC591` ✅ | **200 / 77,511 B / `544D3A4A1B2CC591`** |
| `1110177/viewer.json` | `7575FAFAD33DD670` ✅ | **200 / 431,073 B / `7575FAFAD33DD670`** |
| `1110177/effects.json` | `10CC9A938BE92A10` ✅ | **200 / 400,615 B / `10CC9A938BE92A10`** |
| `1110171/viewer.json` | `62E7BDDC9CF6EC6D` ✅ | — |
| `board.html` | `CD298607B780B2F0` ✅ | — |
`?v=` 实际请求命中且 200：`adapter?v=544d3a4a1b2c`、`viewer.js?v=4647cf0be061`。**网络侧 `/sfx/tex/` 6 条全 200、0×404**；`gpk_1229`：1110177 **404**（既有 task-46）、1110171 **200**。

## 1. 粒子层 —— **PASS（独立复现成功）**
`__sfxDiag()` 本次实测顶层：`{weapon_diag 15.4551, clamp_k 0.6, sprite_fix true, unit_scale_on true, sfx_unit_to_model 0.1, color_order "unproven:[A,R,G,B]", sprites_total 3, particles_total 16, alive_now 8, sliced_total 0, distinct_textures ["glow_01.tga"×3]}`。
**⚠ 口径更正**：本 build 的逐节点粒子表字段是 **`particles[]`（不是 `ps[]`）**；`sprites[]`、`nodes[]` 亦在顶层。Lead/chain-auditor 口径里的 `__sfxDiag().ps[]` 在本版取不到（`ps` 不存在）——请以 `particles` 为准。
| 节点 | `rate_source` | in_pool/visible/**alive_now** | `per_particle_size_min–max` | `quad`(world) | `sliced_frames`/`frame_index_last`/`sheet` |
|---|---|---|---|---|---|
| `H_p_闪电` | `xml_attr:ParticlesPerSecond=10` | 2/0/0 | 7–12 | **1.9561** | **16**/15/[256,256] |
| `H_ shandian01_1_1` | `…=5` | 3/**2/2** | 0.5–1.5 | 0.2506 | **16**/4/[512,512] |
| `H_鬼火_lizi_1` | `…=5` | 3/**3/3** | 0.15–0.35 | 0.07 | 0/–/– |
| `M_lizi_闪电_01` | `…=3` | 2/**1/1** | 2–3 | 0.1546 | **4**/3/[256,256] |
| `L_p_星点_02` | `…=4` | 1/**1/1** | 2–6 | 0.0673 | 0/–/– |
| `H_p_星点_02` | `…=7` | 2/0/0 | 1–3 | 0.1076 | 0/–/– |
| 其余 10 个 | **`absent`** | 0/0/0 | – | – | 0/–/– |
⇒ **rate 数据到位（6/16 有源 rate，其余 10 个源侧确无 rate）**；**采样瞬间 `alive_now` 合计 8**（4 个发射器同时活着）⇒ 粒子确实按源 rate 发射，**独立复现成功**。`sliced_frames` **16/16/4** 与 chain-auditor 报的完全一致（我独立取自 diag）。
**`psFallback(true)` vs `(false)`**：开关已验证生效（`adaptSwitches().psFallbackOn` false/true），但在 **t∈[0.00,0.30] 全部 16 个取样点帧 sha 完全相同**（如 t=0.28 两者都是 `02005743…`、eff 0.3076%）⇒ **我未能复现两者的可见差异**（10 个无 rate 节点本就不发射；有 rate 的 6 个在两种设置下都发射）。标 **WARN/未能复现**。

## 2. `.spr` 帧切片 —— **PASS（A/B 差异独立复现）**
`sprSlice(true)` vs `(false)`（隔离开关后测）在 **t=0.06–0.28 每个取样点帧 sha 都不同**，例：
| t | `sprSlice(true)` | `sprSlice(false)` | eff% (true/false) |
|---|---|---|---|
| 0.10 | `d21d6353…` | `bc891b0b…` | 0.048 / 0.048 |
| 0.20 | `9ab90ddc…` | `13c411a0…` | 0.209 / 0.200 |
| 0.28 | `02005743…` | `2a63ef0c…` | 0.308 / 0.297 |
| 0.30 | `9aaac234…` | `9aaac234…`（该点相同） | 0.305 / 0.305 |
⇒ **切片开关确实改变画面**（我复现了"有差异"这一结论）；**具体 sha 与 chain-auditor 的 `28f23b85…`/`bf2482ea…` 不同**（不同 build/数据/取样时点，逐字节不可比）。
**我亲眼看的描述**（放大 2× 对比图 `FX58V2_crop_sliceTrue_top_sliceFalse_bottom.png`）：切片开（上）时那片光斑**边缘更细碎、内部出现更清楚的横向条纹感**；切片关（下）时更接近**整团模糊的均匀光**。差别是"纹理感/可辨度"的差别，**两者都不是"一大块"**（该窗口 eff 仅 0.3% 画布）。

## 3. `colorOrder` —— **PASS（A/B 差异独立复现）；RGBA 属推导非源直证**
| t | `colorOrder('rgba')` | `colorOrder('argb')` | eff% rgba / argb |
|---|---|---|---|
| 0.95 | `5b1bf8ff…` | `f77f2106…` | 0.004 / 0.004 |
| 1.15 | `e49dfd3f…` | `3a564c8d…` | 0.166 / 0.204 |
| 1.175 | `f5d5d91b…` | `9c27907c…` | 0.220 / 0.257 |
| 1.20 | `d8e91191…` | `68cb2708…` | 0.247 / 0.267 |
峰值 MASK 五读数：rgba `mask 1.84% / p50 0.2838 / p95 0.5745 / >0.5 18.227 / >0.75 0.985 / 暖色 0.684`；argb `mask 1.994% / p50 0.2731 / p95 0.5725 / >0.5 16.813 / >0.75 0.909 / 暖色 0.631` ⇒ 两态**逐 t 帧不同、argb 亮部略多**。
**我亲眼看的描述**（全帧 + 2× 放大 `FX58V2_crop_rgba_top_argb_bottom.png`）：两态都只是**剑刃旁一小团柔光**；**rgba 偏冷偏暗（青白）**，**argb 略亮、光核略带一点暖白**。在 0.25% 量级下差异**是"轻微亮度/色相偏移"，不是"冷青 ⇄ 暖金"的戏剧性切换**——我不会把 argb 说成"暖金"。
**明确写入结论：RGBA 属推导、非源直证**——adapter 自己的 `__sfxDiag().color_order` 返回 **`"unproven:[A,R,G,B]"`**，与 Lead 的要求一致。

## 4. MASK 五读数 —— **PASS（默认态无变化；ON 比 task-56 更小）**
| 皮肤/状态 | 帧 sha16 | 五读数 |
|---|---|---|
| 1110177 OFF（N≥5 同 sha） | `e62c1c58e5bdc383` | p50 **0.2829** / p95 **0.5745** / >0.5 **18.242%** / >0.75 **0.989%** / 暖色 **0.689%**（mask 1.826%，n=25,995）⇒ **与基线逐项相同** ✅ |
| 1110171 OFF（N≥5 同 sha） | `48b6c95c1165c80a` | p50 **0.1232** / p95 **0.4865** / >0.5 **3.394%** / >0.75 **0.273%** / 暖色 **0.106%**（mask 2.449%）⇒ **与基线逐项相同** ✅ |
| 1110177 ON @t=1.175（argb） | `9c27907c69d70954` | mask 1.994%；**effect-only 0.257% 画布** |
| 1110177 ON @t=1.20（argb 峰值） | `68cb27085ab3601a` | mask 1.994%；**effect-only 0.2666% 画布** |
| 1110177 ON @t=1.20（rgba） | `d8e91191d31560c6` | mask 1.84%；effect-only 0.2472% |
⇒ 对 task-56 基线（effect-only **0.4284%**）**进一步变小**（0.247–0.267%），与"一大块已修"的方向一致。

## 5. 负控（按更正的调用方式重做）—— **PASS（独立复现成功）**
| 控制态 | 调用 | `spriteOn` 为 boolean | 帧1/帧2（≥1.4 s 间隔） | 结论 |
|---|---|---|---|---|
| `all_off` | `sprites(false)+models(false)` | **true**（`spriteOn:false`） | `6b219622865dde01` / 同 | 基准 |
| `sprite_only` | `sprites(true)+models(false)` | **true**（`spriteOn:true`） | **`9c27907c69d70954`** / 同 | **≠ all_off ⇒ 精灵层是可见贡献者** ✅ |
| `model_only` | `sprites(false)+models(true)` | **true**（`spriteOn:false`） | `6b219622865dde01` / 同 | **= all_off ⇒ Model 层不加东西** ✅ |
⇒ **与 chain-auditor 的结论一致，且由我独立复现**；每态两帧同 sha ⇒ 不会被下一帧点亮。上一轮我报的"开关未注册"**确认是我的 harness 缺陷**（把两条语句塞进 `JSON.stringify(...)` 造成 SyntaxError），已修正并在此重测。

## 6. 异常归属 —— **我的两轮 = 0 条；chain-auditor 的 1 条我未复现**
- 零观测注入空跑（只 navigate + 截图 + 等 20 s）：`Runtime.exceptionThrown` **0 条**。
- 完整协议（含 `Runtime.evaluate`/异步 IIFE/`fetch` 自证）：**0 条**；我的 evaluate 级 `exceptionDetails` 也为 **0**（上一轮那批是我自己的 SyntaxError，已修）。
⇒ **无法判定** chain-auditor 那条 `scriptId 20 / line 0 / col 22` 的来源（我这边两轮都没有），**不能**替它定证"来自注入"。

## 7. 加载窗口白块 —— **未抓到白块帧（如实）**
`open()` 后 **200 ms × 15 帧**（1.10 s → 10.71 s）全部存档；`canvas p50 = 0.1517 → 0.154` 稳定，**没有任何 p50>0.6 的帧**（`window_white_blocks=[]`）。
最接近窗口态的 1.9–2.5 s 帧：`mask_pct 16.206 / p50 0.1395 / p95 0.7687 / >0.5 13.605→13.494 / >0.75 5.476 / 暖色 1.306`，与 Lead 给的窗口帧（`16.133 / 0.1392 / 0.7934 / 13.123 / 6.308 / 1.897`）**同档**⇒ **窗口期不是白块**这一点我支持；但**我没有抢到白块那一帧**（我的最早帧 1.10 s，白块应在更早），**如实写"未抓到"**。

## 8. 方法学发现（重要，供 Lead 归档）
1. **adapter 方法只在"attach（点 SFX）之后"才挂上**：`document.readyState==='complete'` 时、`open()` 之后、点击之前，`window.WikiSfxAdapter` 虽是 `object`，但 `sprites / adaptSwitches / __sfxDiag / psFallback / sprSlice / colorOrder` **全部 `undefined`**；**点击 SFX 后 1 ms 内全部变为 `function`**（实测 `wait_methods ok=true, ms=1`）。⇒ Lead 给的第 2 条根因（"等 readyState 即可"）**在本 build 不成立**；正确门控是 **"attach 之后"**。这也解释了此前"时有时无"。
2. **`__sfxDiag()` 字段名**：逐节点粒子表是 **`particles`**（16 行），不是 `ps`；`sliced_total` 顶层计数器与逐节点 `sliced_frames` 语义不同（顶层为 0 而节点有 16/16/4）。
3. 我第一轮的 **3 处 harness 缺陷**（已修并在此报告）：① 等 adapter 的时机错（应在 attach 后）；② 粒子/切片取样落在**精灵窗口** t≈1.1–1.2，而粒子窗口是 **t≲0.3**；③ 负控把两条语句塞进 `JSON.stringify(...)` ⇒ SyntaxError、开关未生效。第一轮对应读数**作废**，本报告全部采用修正轮数据（两轮原始数据都在 `FX58VERIFY_readings.json`，`round1` 与 `repair_round` 分列）。

## 9. 纪律与产物
- 只读；两轮各 **1 个**浏览器（`FXVA581_prof`/10109 轮1、`FXVA582_prof`/10111 轮2 与修正轮），结束按 `user-data-dir` 反查真实 PID `taskkill /T /F`（各 8 个进程）；**端口 10109/10111 无 LISTEN**、匹配我的 profile 的 chrome = 0。
- 产物：本报告 + `FX58VERIFY_readings.json`（`round1` / `repair_round`）、截图 `FX58V_*.png`（轮1）、`FX58V2_*.png`（修正轮）、放大对比 `FX58V2_crop_*.png`。
```
