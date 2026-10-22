# task-68 验收：adapter 兜底切片修复 + 1110171 星点粒子真图集（两把皮肤）

**结论速览：PASS 4 · WARN 2 · FAIL 0**（无"格阵/全黑/全白"告警）
- PASS：① 兜底切片**功能成立**（`sliced_frames=4`、帧索引 0→1→2→3 推进、**画面上没有 2×2 格阵**）② 1110177 五节点回归与 task-67 一致 ③ 两皮肤 SFX ON 稳定帧（1110171×5、1110177×6，全 `gate_ok`）④ 6 皮肤回归 + 网络/异常 + **adapter 页内字节哈希核对** ⑤ 文件未变清单。
- WARN：(a) **1110171 的靶子节点屏幕上几乎不可见**（差异仅 0/6/17/19 px，`quad=0.1`）；(b) **两皮肤的 SFX OFF 门控帧 sha 与我记录的历史基线逐字节不同**（五读数完全一致，判为跨版本/跨会话差异，非回归，详见 §4）。

## 0. pin + 版本自证（开工前后各哈希一次，全部一致）
| 对象 | sha16 | 页内 `fetch` 实字节（no-store） |
|---|---|---|
| `weapon_skin_sfx_adapter.js` | **`97D70BFD33C16C90`**（新，91,829 B） | **200 / 91,829 B / `97D70BFD33C16C90`** ✅（**不是只看 `?v=`**） |
| `weapon_skin_viewer.js` | `B9C7281E1EE7A819`（未改） | 200 / 379,489 B / 同 ✅ |
| `board.html` | `334897F9CBE3952C`（`?v=` bump 后） | — |
| `1110177/viewer.json` | `0B752FFD08DBDE8F` | 200 / 629,529 B / 同 ✅ |
| `1110177/effects.json` | `9C60BED52F3014E3` | 200 / 565,949 B / 同 ✅ |
| `1110171/viewer.json` | **`B3AEC2A171E9C3B2`** | 200 / 156,176 B / 同 ✅ |
| `1110171/effects.json` | **`1A80510416D2203D`** | 200 / 129,586 B / 同 ✅ |
| `1110177/neox_material.json` | `A05C4F2C8DDFCF9A` | 未变 ✅ |
- `?v=97d70bfd33c16c90` 实际请求 **200**；`viewer.js?v=b9c7281e1ee7` 200。
- 1110171 新图集 `tex_glow_tp07_02__atlas207414.png`：**200 / 10,794 B / sha16 `6480F7FC1914F0C4`** = 你给的 `png_sha16` ✅。
- rect 三次读数一致 `{x:200, y:122.3, w:1178, h:717.7}`。

## 1. ① 1110171 `H_星点粒子`（兜底+切片靶子）
**运行时原文**（`__sfxDiag().particles[]`，逐 t 全表在 JSON）：
```
H_星点粒子  table=particles kind=particle  in_pool=1 visible=1 alive_now=1  sheet=[256,256]
            sliced_frames=4  frame_index_last: 0(t≤0.20) → 1(0.25–0.45) → 2(0.50–0.70) → 3(0.75–1.00)
            fallback="source_rate_missing"  rate_source="absent"  quad=0.1  slice_path=null  per_particle_size_min/max=null
```
- `sliced_frames = 4` ✅；`fallback = "source_rate_missing"` ✅（源确实无速率）。
- **`slice_path` 在 diag 行里取不到（`null`）**：adapter 把 `slice_path='fallback_quad_sliced'` 写在 **`sys.sq.userData`**（源码 L791-793），而 diag 行只暴露 `fallback / sliced_frames / frame_index_last`（L939-940）⇒ **探针未曝光该字段**（建议把它加进 diag 行）。我以**帧索引随时间推进（0→1→2→3）**作为"确实走兜底+切片路径"的直接功能证据。
- **关键目视：没有 2×2 格阵** ✅ —— t=0.10 / 0.20 / 0.35 / 0.55 的 6× 放大图上**看不到 2×2 四个团**，也没有把 256² 图集当一块贴上的痕迹。
- **⚠ 但同时几乎看不到"柔光团"**：ON 帧与默认 OFF 帧的差异只有 **0 / 6 / 17 / 19 px**（t=0.10/0.20/0.35/0.55），MASK 五读数与默认态**完全一致**（p50 0.1232 等）⇒ 该节点在屏幕上的足迹约几个像素，6× 放大后仍难与高光区分。**线索**：`quad=0.1`（0.1 世界单位）+ 兜底路径 `per_particle_size_min/max=null`（无尺寸参数）⇒ 尺寸取的是兜底值，**放不下 4 帧图集的可见内容**。判定 **WARN：修好的是"不出现格阵"，但可见性不足**。

## 2. ② 1110177 五节点回归 —— **PASS（与 task-67 一致）**
| 节点 | `sliced_frames` | `fallback` | 帧索引变化数（26 个 t） | alive 峰值 |
|---|---|---|---|---|
| `H_p_烟雾_02` | **64** | `None` | 24（0→63） | 6 |
| `H_鬼火_星点_1` | **4** | `None` | 4（0→3） | 5 |
| `H_p_闪电` | **16** | `None` | 8（1→15） | 2 |
| `H_ shandian01_1_1` | **16** | `None` | 5（1→6） | 2 |
| `M_lizi_闪电_01` | **4** | `None` | 4（0→3） | 1 |
⇒ 五节点切片与推进**全部保持**，与 task-67 读数一致。

## 3. ③ 两皮肤 SFX ON 稳定帧（N≥5 门，全 `gate_ok=true`）
**1110171**（`alive` 合计 11，t=1.10 起无存活 ⇒ 与默认帧同 sha）：
| t | 0.10 | 0.20 | 0.35 | 0.55 | 1.10 |
|---|---|---|---|---|---|
| sha16 | `fc8b767922c2b9ad` | `cbd12df358dfa507` | `fc857065acd0180c` | `434cf056f4ddf72b` | `48b6c95c1165c80a` |
**1110177**：
| t | 0.08 | 0.14 | 0.22 | 0.30 | 0.55 | 1.15 |
|---|---|---|---|---|---|---|
| sha16 | `4b00fda9252ded8d` | `e6f472f8a658c763` | `da63f6d3577d8a4d` | `9dfcfd16cf6212ee` | `e7bfc3fc7de83d22` | `92a1b42021e71270` |
| alive | 5 | 7 | 13 | 15 | 9 | 12 |
**亲眼**：1110177 侧见**灰绿烟雾团 + 细青丝状电弧 + 零散亮点**（与 task-67 相同，无格阵/糊团/全黑白）；1110171 侧**只有极小的光斑变化**（<20 px，6× 放大后仍不显眼），同样**无格阵**。掩模内白像素占比：1110171 0.089%、1110177 0.677% ⇒ **无全白**。

## 4. ④ 默认态零回归 —— **WARN（逐字节不一致，五读数一致）**
| 皮肤 | 本次 OFF 门控帧（N≥5 同 sha） | 我记录的历史基线 | 逐字节 | MASK 五读数 vs 基线 | 关 SFX 后回 OFF |
|---|---|---|---|---|---|
| 1110177 | **`6541c6c945520e31`** | `e62c1c58e5bdc383`（你信里也这么指） | **不一致** ❌ | `1.826 / 0.2829 / 0.5745 / 18.242 / 0.989 / 0.689` ⇒ **逐项相同** ✅ | ✅ 回到 `6541c6c945520e31` |
| 1110171 | **`48b6c95c1165c80a`** | `09611e2e90b49bc0`（我 task-45/56 的读法） | **不一致** ❌ | `2.449 / 0.1232 / 0.4865 / 3.394 / 0.273 / 0.106` ⇒ **逐项相同** ✅ | ✅ 回到 `48b6c95c1165c80a` |
- 说明：**两把皮肤的 OFF 帧 sha 都变了**（1110177 从上两轮的 `8352c4e30bbaf981` → 本轮 `6541c6c945520e31`；1110171 从 `09611e2e90b49bc0` → `48b6c95c1165c80a`），而**五读数一字不差**，且**同会话内 OFF↔SFX 往返自洽**。
- 按我们已采纳的口径（`MASK_CRITERION.md` §3b：**帧 sha 只在同一 harness/同一取帧管线内可比；跨 harness 只比五读数 + 自洽性**），我判为**跨版本/跨会话差异（本轮 adapter `97D70BFD` + board `334897F9` 都变了），非渲染回归**；但**如实报"不等于你给的 `e62c1c58e5bdc383`"**。若你要求逐字节锚稳定，需要固定 adapter/board 版本后在同一会话复现。

## 5. ⑤ 6 皮肤回归 —— **PASS**
| 皮肤 | applied/expected | failed / missing | env_warn | pending | SFX 默认态 |
|---|---|---|---|---|---|
| 1110024 | **5 == 5** | 0 / 0 | null | 0 | `SFX 关闭`（disabled=true, pressed=false） |
| 1110129 | **5 == 5** | 0 / 0 | null | 0 | 同上 |
| 1110145 | **7 == 7** | 0 / 0 | null | 0 | 同上 |
| 1110152 | **2 == 2** | 0 / 0 | null | 0 | `SFX 关闭`（disabled=false, pressed=false） |
| 1110165 | **4 == 4** | 0 / 0 | null | 0 | 同上（disabled=true） |
| 1110171 | **7 == 7** | 0 / 0 | null | 0 | `SFX 关闭`（disabled=false, pressed=false） |

## 6. ⑥ 网络 / 异常 —— **PASS**
- 贴图请求（`/sfx/tex/` + `/src_tex/`）**84 条全 200、404 = 0**；**本页唯一 404 = `favicon.ico`**。
- `Runtime.exceptionThrown` **0 条**；evaluate 级 `exceptionDetails` **0 条**（零观测注入空跑同为 0）。
- **adapter 版本已用页内字节哈希核对**：`97D70BFD33C16C90`（91,829 B），与磁盘一致 ⇒ 确实加载了新 adapter（非只看 `?v=`）。

## 7. ⑦ 文件未变清单 —— **PASS**
`viewer.js` / `adapter`(新) / `board.html`(新) / `1110177/viewer.json` / `1110177/effects.json` / `1110171/viewer.json`(新) / `1110171/effects.json`(新) / `neox_material.1110177` —— **开工前后哈希全 true**。

## 8. 诚实边界与建议
1. **靶子节点可见性不足**（WARN）：兜底路径无 `per_particle_size_min/max`、`quad=0.1` ⇒ 即便切片正确也几乎看不到；若目标是"看得见的星点"，需要给兜底路径一个可用的尺寸来源（或源参数），**否则本项只是"不再出格阵"**。
2. **`slice_path` 未在 diag 行曝光**（仅 `sq.userData`）：建议在 `__sfxDiag().particles[]` 行里加 `slice_path`，后续复测即可直接读。
3. **OFF 帧 sha 的跨版本变化**（见 §4）：建议把"OFF 锚"定义为**同会话内 OFF↔往返自洽 + 五读数一致**，避免版本一变就误判回归。
4. 枚举语义（`TransparentMode`/`BlendMode`/`RenderBias`）仍未定证；dg 的 16 Model 仍默认不渲。

## 9. 纪律与产物
- 只读 `08Lifeafter wiki/**`（未改任何文件）；单浏览器 `FXVA68_prof` / 端口 **10125**；结束按 `user-data-dir` 反查真实 PID `taskkill /T /F`（8 个进程）；**端口 10125 无 LISTEN**、我的 profile chrome = 0。
- 产物（仅写 task 允许的三条路径）：本报告 + `SFX_two_skins_verify_20260920.json`；截图目录 `sfx_verify_shots3/`（两皮肤默认 OFF/bg/稳定帧 11 张 + `zoom_*` 6× 放大对照 5 张）。
