# task-88 复核：1110177 内联同步后渲染集 = 5（6 条错图不再显示）

**结论速览：PASS 5 · WARN 1（并发写入，见 §6）· FAIL 0**
⚠ **先报一条异常**：我跑的这一轮里，**4 个皮肤文件在开工后又被改写了**（不是我这轮改的；我只读）：
`v1110177 28313EFCCA57BAE1 → BF7288193E092AA2`、`e1110177 5403931C1671ECBE → 140E27ABB3E40694`、`v1110171 0185E02C2E425A53 → 4D6CAE69DCE8CFC9`、`e1110171 A9A9FC4482E7F84D → 2B0127E574A32CBD`。
我开工时的**页内字节哈希与你给的期望值 5/5 全中**，所以**下面所有读数都是"你描述的那个快照"的有效读数**；但"文件前后未变"这条**不成立**（原因：并发写入，非我这轮造成）。

## 0. pin / 页内字节自证（开工时快照）
| 对象 | 期望 sha16 | 页内 `fetch` 实字节 | 命中 |
|---|---|---|---|
| `1110177/viewer.json` | `28313EFCCA57BAE1` | 200 / 714,290 B / **`28313EFCCA57BAE1`** | ✅ |
| `1110177/effects.json` | `5403931C1671ECBE` | 200 / 645,569 B / **`5403931C1671ECBE`** | ✅ |
| `1110171/viewer.json` | `0185E02C2E425A53` | 200 / 248,144 B / **`0185E02C2E425A53`** | ✅ |
| `1110171/effects.json` | `A9A9FC4482E7F84D` | 200 / 219,198 B / **`A9A9FC4482E7F84D`** | ✅ |
| `weapon_skin_sfx_adapter.js` | `C3BEF3C4EB27F809` | 200 / 103,154 B / **`C3BEF3C4EB27F809`** | ✅ |
| `weapon_skin_viewer.js` | `B9C7281E1EE7A819` | 200 / 379,489 B / 同 | ✅ |
- `board.html ?v=` 实际含 **`c3bef3c4eb27f809`**（你信里写的 `?v=c3bef3f0551daaa3` 应是笔误；adapter 已用 `?v=c3bef3c4eb27f809` 请求到 200）。
- 5 项期望哈希**全部命中**（`bytes_match_expected` = 5/5 true）⇒ **页面确实拿到了新内联**，不是旧内联。

## 1. ② 渲染集 = **5** —— **PASS**
内联清单（页内 fetch `viewer.json`）：**nodes 91 / `renderable_by_adapter=true` = 5 / 已撤 = 6**
```
renderable(5): H_p_闪电, H_ shandian01_1_1, M_lizi_闪电_01, H_p_烟雾_02, H_鬼火_星点_1
rejected(6)  : H_p_星点_02, M_g_glow_an, H_鬼火_lizi_1, H_g_glow地_an, L_p_星点_02, H_公告板_爆闪2
```
5 个渲染节点（清单）：`spr_frames` = **16 / 16 / 4 / 64 / 4**、`texture_status = verified_by_spr_sibling_pairing`、贴图 = 5 张真图集 ✅
6 个被撤节点（清单原文）：`renderable_by_adapter=false`、`texture_candidate=null`、**`texture_status = "REJECTED_source_dims_mismatch(fail_closed,不顶替)"`** ✅（**6/6 全部不在渲染集**）
运行时（`__sfxDiag()`，SFX 打开后）：
```
H_p_闪电          sliced_frames 16  fallback null  frame_index_last 15  in_pool 2
H_ shandian01_1_1 sliced_frames 16  fallback null  frame_index_last  5  in_pool 2
M_lizi_闪电_01     sliced_frames  4  fallback null  frame_index_last  3  in_pool 1
H_p_烟雾_02        sliced_frames 64  fallback null  frame_index_last 63  in_pool 6
H_鬼火_星点_1       sliced_frames  4  fallback null  frame_index_last  3  in_pool 5
H_p_星点_02 / L_p_星点_02 / H_鬼火_lizi_1 : sliced_frames 0 / in_pool 0 / visible 0   （已撤，登记但无池、不发射）
M_g_glow_an / H_g_glow地_an / H_公告板_爆闪2 : 不在任何表内
diag_counts = {"nodes": 20, "sprites": 0, "particles": 20}      # 改前 sprites_total = 3
```
⇒ **`sliced_frames` = 16/16/4/64/4、`fallback` 全 `null`** ✅；**`sprites_total` 从 3 → 0**（3 个错图 Sprite 彻底退出）；3 个被撤 PS 只剩 `in_pool 0 / visible 0 / sliced 0` 的登记行（不发射、不上屏）✅

## 2. ③ 画面（4 张 N≥5 稳定帧）+ 与 task-73 对比 + 目视 —— **PASS**
| 冻结 t | 帧 sha16 | 门控 | alive | 与 task-73 同 t | 像素差 |
|---|---|---|---|---|---|
| 0.10 | `5723dc1491bc279c` | ✅ | 6 | （task-73 无 0.10 取样） | — |
| 0.30 | `7972fa4489b59ee6` | ✅ | 13 | `0ff65ed7b8b91b0a` | **9 px**（bbox 3×3） |
| 0.55 | `3512b6d82a487826` | ✅ | 7 | `81f258ba298e1197` | **4 px**（bbox 2×2） |
| 1.15 | `e718bc7aea189c6f` | ✅ | 7 | `40554a2b3676e2aa` | **3,066 px = 0.2154% 画布**（bbox x[758,1121] y[414,528]，364×115） |
- MASK 五读数与基线同档（mask 1.83–1.89%、p50 0.28–0.29%、掩模内白 **0.65–0.68%**）⇒ **无全白/全黑**；放大图上**没有整张图集格阵**。
- **我亲眼（3× 放大对照 `diff_t115_task73_left_now_right.png`，左 = task-73，右 = 现在）**：左图（task-73）在剑刃左上有一**大块柔和的灰白色光斑**（那是绑错图的 `M_g_glow_an` / `glow_01.tga` 一类），**右图（现在）这块光斑消失了**；两侧都只剩剑体本身 + 零星极小的白/绿点。⇒ **那 6 条错图确实不再出现在画面上**（1.15 时刻 3,066 px 的差异主要就是这块光斑退场）。

## 3. ④ 默认零回归 —— **PASS**
| 皮肤 | SFX OFF 门控帧（N≥5） | 与 task-81 对比 | MASK 五读数 |
|---|---|---|---|
| **1110177** | **`e62c1c58e5bdc383`** | **sha 相同、像素差 0（max 0.0）** ✅ | `1.826 / 0.2829 / 0.5745 / 18.242 / 0.989 / 0.689` = 基线 ✅ |
| **1110171** | **`48b6c95c1165c80a`** | **sha 相同、像素差 0（max 0.0）** ✅ | `2.449 / 0.1232 / 0.4865 / 3.394 / 0.273 / 0.106` = 基线 ✅ |
- `__neox()`：**1110177 3 == 3**、**1110171 7 == 7**；`failed/missing` 空、`env_warn=null`；1110177 OFF↔SFX 往返自洽 ✅。
- **异常：`Runtime.exceptionThrown` 0 + evaluate 级 0**；**全页 404 逐条 = 仅 `http://127.0.0.1:8765/favicon.ico`** ✅；网络：GLB 7 条全 200、贴图 74 条全 200、**0×404** ✅。

## 4. ⑤ 6 皮肤回归 —— **PASS**
| 皮肤 | applied/expected | failed / missing | env_warn | SFX 默认态 |
|---|---|---|---|---|
| 1110024 | **5 == 5** | 0 / 0 | null | `SFX 关闭`（disabled=true, pressed=false） |
| 1110129 | **5 == 5** | 0 / 0 | null | 同上 |
| 1110145 | **7 == 7** | 0 / 0 | null | 同上 |
| 1110152 | **2 == 2** | 0 / 0 | null | `SFX 关闭`（disabled=false, pressed=false） |
| 1110165 | **4 == 4** | 0 / 0 | null | 同上（disabled=true） |
| 1110171 | **7 == 7** | 0 / 0 | null | `SFX 关闭`（disabled=false, pressed=false） |

## 5. 附带读数（1110171 侧，供台账）
内联一致性：**nodes 48 / `renderable_by_adapter=true` = 8 / 已撤 = 3**（与你说的一致）；OFF 门控帧 `48b6c95c1165c80a` = task-81 **逐字节相同（max 0.0）**；MASK 与基线逐项一致。

## 6. ⑥ 未变清单 —— **WARN/FAIL（并发写入，非本轮改动）**
| 文件 | 我开工时 | 我收尾时 | 判定 |
|---|---|---|---|
| `viewer.js` | `B9C7281E1EE7A819` | 同 | ✅ 未变 |
| `adapter` | `C3BEF3C4EB27F809` | 同 | ✅ 未变 |
| `board.html` | `8F9F39F8C76BACB1` | 同 | ✅ 未变 |
| `m1110177` | `A05C4F2C8DDFCF9A` | 同 | ✅ 未变 |
| 5+1 张真图集 / 3 个 GLB | （见 §0） | 同 | ✅ 未变 |
| **1110177/viewer.json** | `28313EFCCA57BAE1` | **`BF7288193E092AA2`** | ❌ **被改写** |
| **1110177/effects.json** | `5403931C1671ECBE` | **`140E27ABB3E40694`** | ❌ **被改写** |
| **1110171/viewer.json** | `0185E02C2E425A53` | **`4D6CAE69DCE8CFC9`** | ❌ **被改写** |
| **1110171/effects.json** | `A9A9FC4482E7F84D` | **`2B0127E574A32CBD`** | ❌ **被改写** |
⇒ **建议**：这批文件正在被并发推进（应该是下一轮的改动）。**本报告的结论只对"开工快照"负责**；若要给最终交付定 pin，请在写入停止后**再跑一次短复核**（我这边随时可跑：只要页内 fetch + OFF 门控 + 4 帧即可）。

## 7. 诚实边界
1. 运行时"渲染集"我按 `__sfxDiag()` 的表（sprites/particles）+ 清单 `renderable_by_adapter` 双证；被撤的 3 个 PS 仍会出现在 diag 的**登记行**里（`in_pool 0`），但**不在渲染集**——这不是漏撤，是探针口径。
2. 与 task-73 的像素差只在 0.30/0.55/1.15 三个 t 上有可比帧（task-73 没有 0.10）；0.30/0.55 的 4–9 px 差属跨会话/版本级微差，1.15 的 3,066 px 才是"错图退场"的实量。
3. 视觉描述基于 3× 放大对照图；未做逐节点像素归属（没有"单节点隔离"开关）。

## 8. 纪律与产物
- 只读 `08Lifeafter wiki/**`（本轮**未改任何文件**；上面的 4 个文件变更由其他成员写入，我只观测到）；单浏览器 `FXVA88_prof` / 端口 **10147**；结束按 `user-data-dir` 反查真实 PID `taskkill /T /F`（8 进程）；**端口 10147 无 LISTEN**、我的 profile chrome = 0、全机 chrome = 0。
- 产物（仅写 task 允许的三条路径）：本报告 + `WIRED_verify_20260920.json`；截图 `sfx_verify_shots10/`（OFF/bg + 4 张稳定帧 + `diff_t115_task73_left_now_right.png`）。
