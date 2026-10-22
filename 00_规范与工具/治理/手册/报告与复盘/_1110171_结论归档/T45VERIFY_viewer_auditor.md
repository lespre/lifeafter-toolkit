# task-45 独立复测报告（viewer-auditor）

**结论速览：PASS 5 · WARN 2 · FAIL 0**
判据：MASK/weapon_box（`MASK_CRITERION.md`）；**bg 一律用 `__primShow(-1)`（新口径）**；`effect-only` = 同相位 ON vs OFF 差分（>8/255，分母=整幅画面）。**只认我的读数，不附和。**

## 0. pin 与版本自证（运行前后一致）
| 对象 | 磁盘 = 防呆文件 | 页内 `fetch` 实字节 |
|---|---|---|
| `weapon_skin_viewer.js` | `57D181F1432095F3` ✅ | **200 / 348,136 B / `57D181F1432095F3`** |
| `weapon_skin_sfx_adapter.js` | `544D3A4A1B2CC591` ✅ | **200 / 77,511 B / `544D3A4A1B2CC591`** |
| `board.html` | `D14ACC59F0106362` ✅ | — |
| `1110177/viewer.json` | `7575FAFAD33DD670` ✅ | — |
| `1110171/viewer.json` | `62E7BDDC9CF6EC6D` ✅ | — |
| `1110177/effects.json` | `10CC9A938BE92A10` ✅ | — |
页内 `?v=` 命中：`viewer.js?v=57d181f14320`、`adapter?v=544d3a4a1b2c`（均 200）。

## 1. 默认 OFF 与锚的逐字节比对 —— **WARN：锚未能复现（自洽性通过）**
| 皮肤 | 我的 OFF sha16（N≥5 门，series） | Lead 给的锚 | 结论 |
|---|---|---|---|
| **1110177** | **`e62c1c58e5bdc383`** ×5 | `49c6f3adcaea235b` | **不等** ❌ |
| **1110171** | **`09611e2e90b49bc0`**（series = `af8d6b21…`, `376c8eeb…`, 然后 ×5 同值） | `9b08a1134bfc484e` | **不等** ❌ |
**但自洽性全部通过**：① 两皮肤 OFF 帧在自己的载入内**逐位稳定**（N≥5 同 sha）；② **OFF 的 MASK 五读数与我长期基线逐项相同**（1110177 `1.826% / 0.2829 / 0.5745 / 18.242 / 0.989 / 0.689`；1110171 `2.449% / 0.1232 / 0.4865 / 3.394 / 0.273 / 0.106`）；③ **OFF→ON→OFF 回到同一 OFF sha**（见 §2）。
⇒ 我只能得出：**跨 harness 的帧捕获管线差异**（面板/UI 状态、取帧时点或序列不同）导致逐字节锚不可比；**锚在两个协议各自内部都成立**。按你的要求，我**只报差异**，不把它归因成数据/功能问题。

## 2. 每项 A/B + 可复现性 —— **PASS**
| 皮肤 | 项 | OFF | ON（我） | shader-auditor 报的 ON | effect-only | OFF→ON→OFF | ON 两次相同 |
|---|---|---|---|---|---|---|---|
| 1110177 | `u_cube_brightness` | `e62c1c58e5bdc383` | **`d28111ee5b0e5614`** | `00684d16fd84bd28`（≠我） | **31 px = 0.0022% 画布**（bbox x[556,689] y[303,410]） | 回到 OFF ✅ | ✅ `d28111ee5b0e5614` |
| 1110177 | `u_rotate_angle` | 同上 | **`b88e8065e130fe7c`** | `58a10b0f34fce803`（≠我） | **99 px = 0.0070% 画布**（bbox x[549,741] y[307,471]） | 回到 OFF ✅ | ✅ `b88e8065e130fe7c` |
| 1110171 | 两项 | `09611e2e90b49bc0` | **同 OFF** | — | **0 px = 0.0000%** | ✅ | ✅ |
⇒ **功能认定 PASS**：两项开关**只影响有值皮肤**、**可逆**、**两次 ON 逐位一致**。ON 帧具体 sha 与 shader-auditor 的不同（`WARN`，与 §1 同一跨 harness 原因）。

## 3. 逐 prim 归属（`__primShow(i)`）—— **PASS**
- **1110177**：`u_cube_brightness` 改动的 prim = **{1, 2}**，prim0 不变；`u_rotate_angle` 同样 = **{1, 2}**，prim0 不变。逐 prim 帧 sha：
  | prim | OFF | ON(cubeB) | ON(srcRot) |
  |---|---|---|---|
  | 0 | `6b823235f85f9ea4` | `6b823235f85f9ea4`（不变） | `6b823235f85f9ea4`（不变） |
  | 1 | `19b4b4e33ed732ad` | `9c07b460cc3c1508` | `47a82e3eadcc4d0a` |
  | 2 | `fb47cece42c7c1c0` | `bf2e1319ef3201c4` | `83bc0e3cd9979e98` |
- **1110171**：两项 `changed_prims = []`（7 个 prim 全不变）⇒ 与"7/7 absent"一致。
- 值来源（探针原文）：`__cubeBrightProbe()` → prim1 **0.71** / prim2 **2.74**（`source:"manifest"`，prim0 `absent`）；`__srcRotProbe()` → prim1 **3.09** / prim2 **2.60** rad（`source:"manifest"`），**`fragRotRead: true`** ✅ ⇒ **与 shader-auditor 的数值声明一致**。

## 4. MASK 五读数（bg=`__primShow(-1)`）—— **PASS**
| 状态 | mask% | p50 | p95 | >0.5% | >0.75% | 暖色% |
|---|---|---|---|---|---|---|
| 1110177 OFF | 1.826 | 0.2829 | 0.5745 | 18.242 | 0.989 | 0.689 |
| 1110177 ON `u_cube_brightness` | 1.826 | **0.2830** | 0.5721 | **18.116** | 0.989 | 0.689 |
| 1110177 ON `u_rotate_angle` | 1.827 | **0.2832** | 0.5734 | **18.302** | 0.988 | 0.688 |
| 1110171 OFF（两项 ON 同值） | 2.449 | 0.1232 | 0.4865 | 3.394 | 0.273 | 0.106 |
⇒ 两项对亮部统计的影响是**极小量级**（p50 ±0.0001–0.0003，占比 ≤±0.13 个百分点），与 `effect-only` 的 31/99 px 一致。

## 5. 无值皮肤抽查 —— **PASS（3/3 逐字节恒等）**
| 皮肤 | OFF（N≥5 门） | `__cubeBright(true)` 后 | ON == OFF | 探针 |
|---|---|---|---|---|
| 1110129 | `53902ace37ad3d8a` | 同 | **✅** | 全 `absent` |
| 1110145 | `48ff1dd4846bd04c` | 同 | **✅** | 全 `absent` |
| 1110152 | `1015edb365511ffd` | 同 | **✅** | 全 `absent` |

## 6. 口径 / 异常 —— **PASS**
- `applied == prims 数`：1110177 **3 == 3** ✅、1110171 **7 == 7** ✅；`failed=[]`、`missing=[]`、`env_warn=null` ✅。
- `window.__glowErrors`：**该页未定义（`null`）** ⇒ 我以数值形式记录为 `null`（不是 `[]`；与 task-56 一致）。
- `Runtime.exceptionThrown`：**0 条**；我的 evaluate 级 exceptionDetails：**0 条**。

## 7. 我亲眼看的描述（2× 放大对比图，OFF 左 / ON 右）
- **`u_cube_brightness`**（`T45_crop_cubeBright_OFF_left_ON_right.png`）：是**局部亮度再分配**——银白刃边与红宝石核心略微变亮，**不是**整体提亮，**高光落点不动**；量级极小（31 px 超阈值）。**部分同意** shader-auditor 的"prim1 略暗 / prim2 略亮"：我**能证实两 prim 的像素都变了且方向不同**（`changed_prims={1,2}`），但在放大图上我**分不出一处是"变暗"**——更准确的描述是"**银白金属略亮、红色核心略亮**"。
- **`u_rotate_angle`**（`T45_crop_srcRot_OFF_left_ON_right.png`）：ON 后**银白金属面上多出一小块更亮的区域**（护手/左翼附近），**红色核心位置与亮度基本不动**（99 px 超阈值）。**同意** shader-auditor 的"prim2 多出一小块更亮的面、红块位置不动"，并且**不像整体提亮**，符合"源驱动（IBL 方向/旋转）"的表现。

## 8. 方法学备注（本轮新增）
- **viewer 侧 task-45 开关的门控与 adapter 不同**：`__primShow / __cubeBright / __cubeBrightProbe / __srcRot / __srcRotProbe` 在 **board 页（未 open 皮肤）时全部 `undefined`**（我在 open 前探了一次，如实记录）；`open()` 之后可用（本轮全部调用成功）。⇒ 复测别人时请在 `open()` 之后再探。
- 1110171 的 OFF 门序列出现 **2 帧瞬态**（`af8d6b21…`、`376c8eeb…`）后才稳定到 `09611e2e90b49bc0` ⇒ 再次说明 N≥5 同 sha 门是必要的。

## 9. 纪律与产物
- 只读；单浏览器 `FXVA45_prof` / 端口 **10113**（本轮两次运行：第一次因我脚本里 `rgb(fn)` 用相对路径而中止，已修）；结束按 `user-data-dir` 反查真实 PID `taskkill /T /F`（8 个进程）；**端口 10113 无 LISTEN**、匹配我的 profile 的 chrome = 0。
- 产物：本报告 + `T45VERIFY_readings.json`；截图 `T45_*.png`（OFF/ON/bg/noval）与 2× 放大对比 `T45_crop_*.png`。
