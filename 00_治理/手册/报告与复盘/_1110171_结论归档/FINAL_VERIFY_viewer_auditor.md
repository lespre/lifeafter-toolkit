# 最终端到端验证报告（viewer-auditor · 本期最后一轮）

**结论速览：PASS 5 · WARN 0 · FAIL 0 · 「未抓到」1（窗口白块帧，如实）**
判据：MASK/weapon_box（`MASK_CRITERION.md`）；**bg 一律 `__primShow(-1)`**；帧 sha 只在**同一 harness 内**可比（§3b），跨 harness 只比五读数 + 自洽性。

## 0. pin（开跑前 / 收尾各哈希一次，全部一致）+ 页内实字节自证
| 对象 | sha16 | 页内 `fetch`（no-store） |
|---|---|---|
| `weapon_skin_viewer.js` | **`8B8E80213F5C0CA8`** ✅ | 200 / **376,205 B** / `8B8E80213F5C0CA8` |
| `weapon_skin_sfx_adapter.js` | `544D3A4A1B2CC591` ✅ | 200 / 77,511 B / `544D3A4A1B2CC591` |
| `board.html` | **`5008117AA03BB7A0`** ✅ | — |
| `1110177/viewer.json` | `7575FAFAD33DD670` ✅ | 200 / 431,073 B / 同 |
| `1110171/viewer.json` | `62E7BDDC9CF6EC6D` ✅ | — |
| `1110177/effects.json` | `10CC9A938BE92A10` ✅ | 200 / 400,615 B / 同 |
| manifest `1110171` | **`64A07D5DF157EC16`** ✅ | 200 / 76,249 B / 同 |
| manifest `1110177` | **`A05C4F2C8DDFCF9A`** ✅ | 200 / 48,811 B / 同 |
页内 `?v=` 命中 200：`viewer.js?v=8b8e80213f5c`、`adapter?v=544d3a4a1b2c`。

## 1. 默认态零回归 —— **PASS**
| 皮肤 | OFF 帧 sha16（N≥5 门，series 全同） | MASK 五读数 | 与长期基线 |
|---|---|---|---|
| **1110171** | `09611e2e90b49bc0` | mask 2.449 / p50 **0.1232** / p95 **0.4865** / >0.5 **3.394** / >0.75 **0.273** / 暖色 **0.106** | **五项逐项相同** ✅（`match:true`×5） |
| **1110177** | `8352c4e30bbaf981` | mask 1.826 / p50 **0.2829** / p95 **0.5745** / >0.5 **18.242** / >0.75 **0.989** / 暖色 **0.689** | **五项逐项相同** ✅（`match:true`×5） |
- `applied == expected`：1110171 **7 == 7** ✅、1110177 **3 == 3** ✅；`failed=[]`、`missing=[]`、`env_warn=null` ✅；`__glowErrors` 该页未定义（记 `null`）。
- 注：我的 OFF 帧 sha 与此前别人报的锚逐字节不同（跨 harness 规则，见 §7），但**四开关往返后都回到同一 OFF sha**、五读数与基线逐项相同 ⇒ 零回归成立。

## 2. 四个实验开关（默认 OFF / 可开 / 可逆）—— **PASS**
判据：① `__X(false)` 后与默认 OFF 帧**逐字节相同**（证明默认确实 OFF）；② `__X(true)` 取 ON 帧；③ `__X(false)` 后**回到同一 OFF sha**。
| 皮肤 | 开关 | `typeof` | 调 false 后 == OFF | ON 帧 sha16 | ON effect-only | 关回 == OFF |
|---|---|---|---|---|---|---|
| 1110171 | `__cubeBright` | function | ✅ | `09611e2e90b49bc0`（无值 ⇒ **0.0000%**） | 0.0000% | ✅ |
| 1110171 | `__srcRot` | function | ✅ | `09611e2e90b49bc0`（无值 ⇒ **0.0000%**） | 0.0000% | ✅ |
| 1110171 | `__brdfSrc` | function | ✅ | `408d561f0e4c1c99` | **0.1366%** | ✅ |
| 1110171 | `__iblIrrSrc` | function | ✅ | `f913bea0f58503d8` | **1.4580%** | ✅ |
| 1110177 | `__cubeBright` | function | ✅ | `516fac8ce0c0cfea` | 0.0022% | ✅ |
| 1110177 | `__srcRot` | function | ✅ | `28834e06d9722594` | 0.0070% | ✅ |
| 1110177 | `__brdfSrc` | function | ✅ | `b339452f26387fa5` | **0.4317%** | ✅ |
| 1110177 | `__iblIrrSrc` | function | ✅ | `a779b0826b351ee1` | **1.8853%** | ✅ |
**ON 时 MASK 五读数（bg 同一掩模）**：
- `__brdfSrc`：1110177 p50 **0.2829→0.2437**、>0.5 **18.242→5.807**、>0.75 0.989→1.003；1110171 p50 0.1232→0.1223、>0.5 3.394→**1.995**。
- `__iblIrrSrc`：1110177 p50 **0.2829→0.0705**（−75%）、>0.5 18.242→**3.07**；1110171 p50 **0.1232→0.0289**（−77%）、>0.5 3.394→**1.307** ⇒ **该开关效果显著（大幅压暗/改变光照），不是微调**（默认 OFF 故不影响交付态；仅作事实登记）。
- 探针默认值（原文）：`__cubeBrightProbe` 1110177 prim1 **0.71** / prim2 **2.74**（`source:manifest`）、1110171 7 个 prim 全 `absent`；`__srcRotProbe` 1110177 prim1 **3.09** / prim2 **2.6**（`manifest`，`fragRotRead:true`）、1110171 全 `absent`；`__brdfSrcProbe` 两皮肤默认 `switch:"off"`、`ibl_ready_at_build:true`；**`__iblIrrSrcProbe` 不存在（无探针）**，只能以帧判定（已在表中给出）。

## 3. SFX 链抽查（1110177）—— **PASS**
| 检查 | 读数 |
|---|---|
| adapter 方法门控（点 SFX 之后） | `methods_ready=true`，**0 ms**（attach 后立即挂上） |
| `__sfxDiag()` | 可用：`unit_scale_on true`、`sfx_unit_to_model 0.1`、`clamp_k 0.6`、`particles_total 16`、`sprites_total 3`、`color_order "unproven:[A,R,G,B]"` |
| `particles[]` 源 rate | **6/16** 节点带 `xml_attr:ParticlesPerSecond`（10/7/5/5/4/3） |
| `sliced_frames` | **`H_p_闪电 16`（sheet 256²）、`H_ shandian01_1_1 16`（512²）、`M_lizi_闪电_01 4`（256²）** ⇒ **16 / 16 / 4 与要求一致** ✅ |
| `/sfx/tex/` 网络 | **200 × 6、404 × 0** ✅ |
| 关 SFX | 回到 `e62c1c58e5bdc383` = 本阶段 OFF 帧 ✅（同阶段内 OFF→ON→OFF 自洽） |

## 4. 窗口白块 —— **未抓到白块帧（如实）；最接近的窗口帧读数已给**
- `open(1110177)` 后 200 ms × **20 帧**（1.25 s → 14.04 s），**canvas p50 = 0.1517 → 0.1540**，**无任何帧 p50 > 0.6** ⇒ `window_white_blocks = []`。
- 最近的两帧（mask 口径，bg 用 `__primShow(-1)`）：
  | t | 帧 sha16 | mask% | p50 | p95 | >0.5% | >0.75% | 暖色% |
  |---|---|---|---|---|---|---|---|
  | 1250 ms | `208acffb94fb3fb5` | 14.671 | 0.1263 | 0.7823 | 12.975 | 5.942 | 1.371 |
  | 2028 ms | `5d27b91147cd921c` | 16.206 | 0.1395 | 0.7687 | 13.605 | 5.476 | 1.306 |
- 与 shader-auditor 的窗口帧（`16.133 / 0.1392 / 0.7934 / 13.123 / 6.308 / 1.897`）**同档** ⇒ 支持"窗口期不是白块"；但**我没有抢到白块那一帧**（我最早 1.25 s），**如实写"未抓到"**。

## 5. board 页 —— **PASS**
| 检查 | 读数 |
|---|---|
| 卡片 / 骨骼 id / 徽标 | **115** 卡 / **37** 个 `skeleton_preview.html?id=` / **8** 徽标 |
| 评级筛选 | 勾选 → **19** 卡；清除 → **115** 卡 ✅ |
| 骨骼预览链接 | `href="skeleton_preview.html?id=1110171"`、文本「3D 挂点预览」✅ |
| **页面控制台错误** | **board 阶段 0 条** ✅（`console_after: []`） |
| 已知既有 404（单列） | `1110177/src_tex/gpk_1229.png` = **404**（出现在**打开 1110177 皮肤**时；board 页本身不请求它）；`1110171/src_tex/gpk_1229.png` = **200**；另有 `favicon.ico` 404 |

## 6. `exceptionDetails` —— **PASS**
- **零观测注入空跑**（只 navigate + 截图 + 等 20 s）：`Runtime.exceptionThrown` **0 条**。
- **完整协议**（含全部 `Runtime.evaluate`、异步 IIFE、`fetch` 自证、逐开关往返）：`Runtime.exceptionThrown` **0 条**；evaluate 级 `exceptionDetails` **0 条**。
- ⇒ 本轮**无任何异常**；chain-auditor 此前那条未定源 Uncaught 在我这里依旧**未复现**（无法判定其来源，不是本轮回归）。

## 7. 你的亲眼看（默认帧）
- **1110177**（`FINAL_1110177_off.png` `8352c4e30bbaf981`）：**像那把武器** —— 金/银装饰的剑体、红色宝石核心、深青工业房间场景，构图居中、刃面/护手细节清楚；**无黑屏、无白块**。
- **1110171**（`FINAL_1110171_off.png` `09611e2e90b49bc0`）：**像那把武器** —— 紫黑色扇形晶刃（该皮肤固有的偏暗外观）、边缘有细亮线，背景同样清晰；**无黑屏、无白块**（与其长期基线 p50 0.1232 一致）。
- 跨 harness 锚说明：我的 OFF 帧 sha 与别人此前报的锚不同（`8B8E8021…` 版 viewer.js 下我的值为 `8352c4e30bbaf981` / `09611e2e90b49bc0`）；按 `MASK_CRITERION.md` §3b，**帧 sha 只在同一 harness 内可比**，因此我以"四开关往返回同 sha + 五读数与基线逐项相同"作为零回归的证据。

## 8. 纪律与产物
- 只读；**单浏览器** `FXVAFIN_prof` / 端口 **10117**；结束按 `user-data-dir` 反查真实 PID `taskkill /T /F`（8 个进程）；**端口 10117 无 LISTEN**、匹配我的 profile 的 chrome = **0**。
- 产物：本报告 + `FINAL_VERIFY_readings.json`（含 `window_masked`/`window_white_blocks`）；截图 `FINAL_*.png`（默认帧、各开关 ON 帧、bg、窗口 20 帧）。
