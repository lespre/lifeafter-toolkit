# task-70 验收：源 `FxIgnore` 生效后的显示集收缩（两把皮肤）

> 本报告合并两段：**stage-1（1110171，上一轮产出，Lead 已读过）** + **stage-2（1110177 + 6 皮肤回归，本轮补做）**。原始读数：`SFX_fxignore_verify_20260920.json`（同一文件，分段保存）；截图：`sfx_verify_shots4/`。

**结论速览：PASS 5 · WARN 2 · FAIL 0**（无全黑/全白/格阵/糊团）
- PASS：① 1110171 的 8 个可渲染禁用节点**全部不再渲染**（`ignored=true`、PS 6 个 `in_pool/visible/alive=0`、Sprite 2 个 `visible=false`）② 1110177 五节点读数不变、`fxIgnore TRUE=4` 且**全部 `renderable=false`**（显示集不变符合预期）③ 两皮肤默认 OFF 门控帧与 MASK 五读数**会话内自洽 + 与基线一致**；`applied==expected`、`failed/missing` 空 ④ 6 皮肤回归全绿 ⑤ 网络/异常干净 + **adapter 字节哈希核对 = `7799134F17D5032E`**
- WARN：(a) `honorFxIgnore(false)` 的 A/B **只把 2 个 Sprite 节点恢复，6 个 PS 节点未复活**（切开关不重建 pool）；(b) 1110177 的可见帧与 **task-68** 的 sha **不一致**（但与 task-67 的完全相同，MASK 五读数各轮一致）⇒ 判为跨会话/跨版本整体差异，非视觉回归。

## 0. 版本 / 未变清单（开工前后各哈希一次，全部一致）
| 对象 | sha16 | 说明 |
|---|---|---|
| `weapon_skin_sfx_adapter.js` | **`7799134F17D5032E`**（93,851 B） | **页内 fetch 实字节核对 = 同值** ✅（非只看 `?v=`）；`?v=7799134f17d5032e` 请求 200 |
| `weapon_skin_viewer.js` | `B9C7281E1EE7A819` | 未变 ✅ |
| `board.html` | `44A2339A06BDD4A1` | `?v=` bump 后 |
| `1110177/viewer.json` | `ABC653B54227D8B9` | 本轮新内联 |
| `1110177/effects.json` | `F3C0623DC3CF684E` | 本轮新值 |
| `1110171/viewer.json` | `696E40B6881C2E6B` | 本轮新内联 |
| `1110171/effects.json` | `1742FA1FC56C3093` | 本轮新值 |
| `neox_material.1110177` | `A05C4F2C8DDFCF9A` | 未变 ✅ |
| 5 张真图集（1110177） | `DBC4D2E4FE65FF4F` / `DDE58C1EB420384F` / `BAB99D2E79746152` / `45AE45AB090353CB` / `37FA4BE63541FFAB` | 与 Lead 给的期望值**逐项一致** ✅ |
| `atlas171`（1110171） | `6480F7FC1914F0C4` | 与期望一致 ✅ |

## 1. ① 1110171：8 个可渲染禁用节点已被压下（stage-1）
清单侧（磁盘只读复核）：`effects.nodes = 44`、`fxIgnore TRUE = 28`，**其中 `renderable_by_adapter=true` 恰 8 个** —— `H_星点粒子`、`H_星点粒子_3`、`L_p_光刺_01`、`L_p_光刺_02`、`H_p_光圈01`、`H_p_光圈02`、`M_g_光晕暗_01`、`M_g_光晕暗_02` ✅（与 Lead 清单逐项一致）

运行时（`__sfxDiag()`，默认 `honorFxIgnore(true)`）原文摘录：
```
H_星点粒子    table=particles ignored=true in_pool=0 visible=0 alive_now=0 sliced_frames=0 slice_path=null fallback=source_rate_missing
H_星点粒子_3   table=particles ignored=true in_pool=0 visible=0 alive_now=0 sliced_frames=0 slice_path=null
L_p_光刺_01   table=particles ignored=true in_pool=0 visible=0 alive_now=0 sliced_frames=0 slice_path=null
L_p_光刺_02   table=particles ignored=true in_pool=0 visible=0 alive_now=0 sliced_frames=0 slice_path=null
H_p_光圈01    table=particles ignored=true in_pool=0 visible=0 alive_now=0 sliced_frames=0 slice_path=null
H_p_光圈02    table=particles ignored=true in_pool=0 visible=0 alive_now=0 sliced_frames=0 slice_path=null
M_g_光晕暗_01  table=sprites   visible=false
M_g_光晕暗_02  table=sprites   visible=false
```
⇒ **8/8 都不再渲染**（截图 `sfx_verify_shots4/s171_ign_t00{10,20,35,55}.png`，四张 t 的 sha 全为 `a541529334382b28`，`gate_ok=true`）；`alive_now` 合计 **3**。

**A/B（`honorFxIgnore(false)`）** —— 见 §2 WARN：`honorFxIgnoreOn=false` 生效，`alive_now` 3 → **5**，像素差 t=0.1 **0 px** / t=0.2 **5 px**（bbox x[756,765] y[460,479]）/ t=0.35 **11 px**；对照帧 `s171_unign_t00{10,20,35,55}.png`（sha `11d74dd4…` / `95a9f3be…` / `f8609cf7…` / `4bfca440…`）。
**恢复**：`honorFxIgnore(true)` 后 t=0.20 帧 = `a541529334382b28` = 禁用态帧 ⇒ `restore_matches_ignored = true` ✅。

## 2. ② 1110177：显示集不变（符合预期）
- 清单（磁盘只读）：`effects.nodes = 89`、**`fxIgnore TRUE = 4`** —— `M_shandian_04`、`M_粒子_科技`、`H_模型核心电小_5`、`M_鬼火细线_2`，**四个全部 `renderable_by_adapter=false`** ✅ ⇒ **对可见画面无影响**（与 Lead 的"预计视觉不变"一致）。
- 运行时：diag 的 `particles` 表里给出 3 个（`M_shandian_04` / `M_粒子_科技` / `M_鬼火细线_2`，均 `ignored=true / in_pool 0 / visible 0 / alive_now 0`）；**第 4 个 `H_模型核心电小_5` 是 Model 节点**，不在 diag 的 `particles`/`sprites` 表覆盖范围内（Model 行在 `__probe().models`/`modelTable`，我本轮未采）⇒ **如实标注：diag 覆盖面为 Sprite/Particle，Model 的 `ignored` 需另读 `models` 表**（建议后续把 Model 行也带 `ignored`）。
- 5 个真图集节点读数 **与 task-67/68 一致**：
  | 节点 | `sliced_frames` | `fallback` | 帧索引取值数（26 个 t） | alive 峰值 |
  |---|---|---|---|---|
  | `H_p_烟雾_02` | **64** | `None` | 24（0→63） | 6 |
  | `H_鬼火_星点_1` | **4** | `None` | 4（0→3） | 5 |
  | `H_p_闪电` | **16** | `None` | 7（1→15） | 2 |
  | `H_ shandian01_1_1` | **16** | `None` | 6（1→6） | 2 |
  | `M_lizi_闪电_01` | **4** | `None` | 4（0→3） | 1 |

### ⚠ 帧 sha 三方对比（WARN：与 task-68 不一致，但与 task-67 完全一致）
| t | **本轮（adapter 7799134F / board 44A2339A）** | task-68（adapter 97D70BFD / board 334897F9） | task-67（adapter 79F5F2B8 / board 2585162A） |
|---|---|---|---|
| 0.08 | `08738b769b60e619` | `4b00fda9252ded8d` | **`08738b769b60e619`** ✅ |
| 0.14 | `59c4d9f613fc7b23` | `e6f472f8a658c763` | **`59c4d9f613fc7b23`** ✅ |
| 0.22 | `cde8ef83db23b530` | `da63f6d3577d8a4d` | **`cde8ef83db23b530`** ✅ |
| 0.30 | `0ff65ed7b8b91b0a` | `9dfcfd16cf6212ee` | **`0ff65ed7b8b91b0a`** ✅ |
| 0.55 | `81f258ba298e1197` | `e7bfc3fc7de83d22` | **`81f258ba298e1197`** ✅ |
| 1.15 | `40554a2b3676e2aa` | `92a1b42021e71270` | **`40554a2b3676e2aa`** ✅ |
- **判读**：本轮的 1110177 画面 **= task-67 基线（逐字节）**，**≠ task-68** 那一轮；三轮的 **MASK 五读数一致**（mask 1.827–1.962、p50 0.28x），且**两皮肤 OFF 锚在各轮也有所漂移**（本轮 1110177 OFF = `e62c1c58e5bdc383` = 你的基线；task-68 那轮是 `6541c6c945520e31`）⇒ 属**跨会话/跨版本的整体帧差异**（我们已采纳的口径），**不是 FxIgnore 引入的视觉变化**（1110177 的 4 个 TRUE 节点本就不渲染）。
- 画面**无全黑/全白/格阵/糊团**：掩模内白像素 1110177 0.677%、1110171 0.089%（与各轮基线持平）。

## 3. ③ `slice_path` 探针可用性 —— **`no_live_fallback_node_to_verify`**（如实）
- 本轮 diag 行**已带 `slice_path` 字段**（不再报"取不到"）；但两把皮肤**当前都没有"仍走兜底且带图集、且未被 FxIgnore 禁用"的活节点**：1110171 里有图集的兜底节点 `H_星点粒子` 的 `fxIgnore=TRUE`（禁用后 `sliced_frames=0 / slice_path=null` 属预期），其同源兄弟 `H_星点粒子_1` 虽未被禁用但 **`sheet=null`**（无 `spr_frames/spr_sheet` ⇒ 不走切片，`slice_path=null` 也属预期）；`H_星点粒子_3` 同为 TRUE。
  ⇒ **结论：`no_live_fallback_node_to_verify`**（无法在不改数据的前提下给出 `fallback_quad_sliced` 的实读）。**验证建议**：在 `honorFxIgnore(false)` 下把 `H_星点粒子` 的 pool 重建（当前切开关不重建），或临时用一个未禁用的兜底+带表节点。

## 4. ④ 默认态零回归（两皮肤，会话内自洽）
| 皮肤 | OFF 门控帧（N≥5） | MASK 五读数 | OFF↔SFX 往返 |
|---|---|---|---|
| 1110177 | **`e62c1c58e5bdc383`**（= 你的基线 ✅） | `1.826 / 0.2829 / 0.5745 / 18.242 / 0.989 / 0.689`（= 长期基线 ✅） | 回同值 ✅ |
| 1110171 | `48b6c95c1165c80a` | `2.449 / 0.1232 / 0.4865 / 3.394 / 0.273 / 0.106`（= 长期基线 ✅） | 回同值 ✅ |
- `__neox()`：1110177 **applied 3 == 3**、1110171 **7 == 7**；`failed=[]`、`missing=[]`、`env_warn=null`；rect 三次读数一致 `{x:200, y:122.3, w:1178, h:717.7}`。

## 5. ⑤ 6 皮肤回归 —— **PASS**
| 皮肤 | applied/expected | failed / missing | env_warn | SFX 默认态 |
|---|---|---|---|---|
| 1110024 | **5 == 5** | 0 / 0 | null | `SFX 关闭`（disabled=true, pressed=false） |
| 1110129 | **5 == 5** | 0 / 0 | null | 同上 |
| 1110145 | **7 == 7** | 0 / 0 | null | 同上 |
| 1110152 | **2 == 2** | 0 / 0 | null | `SFX 关闭`（disabled=false, pressed=false） |
| 1110165 | **4 == 4** | 0 / 0 | null | 同上（disabled=true） |
| 1110171 | **7 == 7** | 0 / 0 | null | `SFX 关闭`（disabled=false, pressed=false） |

## 6. ⑥ 网络 / 异常 —— **PASS**
- stage-1 + stage-2 合计贴图请求 **84 + 77 = 161 条全 200、404 = 0**；**唯一 404 = `favicon.ico`**（阶段 1、2 各一条）。
- `Runtime.exceptionThrown` **0 条**（两阶段）；evaluate 级 `exceptionDetails` **0 条**；adapter 页内字节哈希 `7799134F17D5032E`（93,851 B）与磁盘一致 ✅。

## 7. 需要 Lead 裁决/知悉的两点
1. **A/B 只恢复了 Sprite 类**：`honorFxIgnore(false)` 让 `M_g_光晕暗_01/02` 回来（`visible=false→true`，alive 3→5，像素差 0/5/11 px），但 6 个 **PS 节点仍 `in_pool=0/visible=0`** ⇒ 该开关只影响"已建对象"的可见性/发射门控，**不重建 pool**。若 A/B 目的是证明"禁用是可逆的"，需要补一次重建（或在 attach 前设 false 再载入）。
2. **1110177 与 task-68 的帧 sha 不一致但与 task-67 完全一致**（§2 表）⇒ 请按"跨会话/跨版本只比五读数"的口径记账；若你要逐字节锚，需要在同一会话内做 A/B（本轮 `honorFxIgnore` 的 restore 已证明同会话可复现）。

## 8. 纪律与产物
- 只读 `08Lifeafter wiki/**`（未改任何文件）；两阶段各 **1 个**浏览器（stage-1 `FXVA70_prof`/10127、stage-2 `FXVA70b_prof`/10129），结束均按 `user-data-dir` 反查真实 PID `taskkill /T /F`（各 8 进程）；**端口 10127/10129 无 LISTEN**、我的 profile chrome = 0、全机 chrome 0。
- 产物（仅写 task 允许的三条路径）：本报告 + `SFX_fxignore_verify_20260920.json`（`skin_1110171` = stage-1、`skin_1110177_stage2`+`regression_default` = stage-2）；截图目录 `sfx_verify_shots4/`（1110171 禁用态/未禁用态各 4 张 + 恢复帧 + 两皮肤 OFF/bg + 1110177 六张稳定帧）。
