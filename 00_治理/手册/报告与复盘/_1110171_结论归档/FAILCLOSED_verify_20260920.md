# task-81 终验：`models()` fail-closed 修复 + C 类归因标签修正

**结论速览：PASS 6 · WARN 0 · FAIL 0**（两条 task-80 WARN **均已修好**，并给出"到底几个 Model 上屏"的答复）

## 0. pin / 版本自证（开工前后各哈希一次，全部一致）
| 对象 | sha16 | 页内 `fetch` 实字节 |
|---|---|---|
| `weapon_skin_sfx_adapter.js` | **`C3BEF3C4EB27F809`**（103,154 B） | 200 / 103,154 B / 同 ✅（非只看 `?v=`；`?v=c3bef3c4eb27f809` 命中 200） |
| `weapon_skin_viewer.js` | `B9C7281E1EE7A819`（未改） | 200 / 379,489 B / 同 ✅ |
| `1110171/effects.json` / `viewer.json` | `42DF44D9B54A3C2C` / `11E24BA804B0E919` | 200 / 同 ✅（未变） |
| `1110177/effects.json` / `viewer.json` | `13AAA1B05B9AD770` / `B67BCA9CA679BF7A` | 200 / 同 ✅（未变） |
| `m1110177` / 5 张真图集 / `atlas171` / 3 个 GLB | `A05C4F2C8DDFCF9A` / 5 张 / `6480F7FC1914F0C4` / `A4EA1EC706F7E71C`·`21A1F52546D0CD12`·`B9E06158D88FBBD5`（见下注） | 全部未变 ✅ |
`pins_unchanged` **16/16 true**。（3 个 GLB 实际哈希：`A4EA1EC706F7E71C` / `21A1F52546D0CD12` / **`B9E06158D88FBBD1`**。）

## 1. 靶子 A：`models()` 开关语义恢复 —— **PASS**
1110171，SFX 开，**同一载入内** `models(true) → (false) → (true)`：

| 冻结 t | `models(T1)` sha16 | `models(F)` sha16 | `models(T2)` sha16 | **T-vs-F 像素差** | T1-vs-T2（往返） |
|---|---|---|---|---|---|
| **0.10** | `e64c359c6f087c14` | `a541529334382b28` | `e64c359c6f087c14` | **7,494 px = 0.5265% 画布**（bbox `x[551,822] y[512,619]`，272×108，对角线 **292.7 px**） | **0 px** ✅ |
| **0.30** | 同上 | 同上 | 同上 | 同上 | **0 px** ✅ |
| 1.15 | `48b6c95c1165c80a` | `48b6c95c1165c80a` | `48b6c95c1165c80a` | **0 px**（该时刻 3 个模型都不在各自时间窗：probe `visible 0 / groupVisibleN 25`） | 0 px ✅ |
| **2.50** | `e64c359c6f087c14` | `a541529334382b28` | `e64c359c6f087c14` | **7,494 px = 0.5265%** | **0 px** ✅ |

逐帧 `__probe()` 原文（t=0.30 抽样）：
```
models(T): {"fixedTime":0.3,"rafActive":true,"groupVisible":true,"modelsOn":true,"modelsForce":true,
            "total":28,"visible":3,"groupVisibleN":28,"ok":3,
            "states":{"disabled_color_semantics_unresolved":20,"disabled_fxignore":3,"disabled_no_color_driver":2,"ok":3},
            "visible_nodes":["M_模型_顶渐变","H_模型_球03","M_模型_球04"]}
models(F): {"fixedTime":0.3,"rafActive":true,"groupVisible":true,"modelsOn":false,"modelsForce":false,
            "total":28,"visible":0,"groupVisibleN":0,"ok":3, …同一 states…, "visible_nodes":[]}
```
⇒ **`models(F)` 时 `visible 0 / groupVisibleN 0`（几何真的被隐藏），`models(T)` 时 `visible 3 / groupVisibleN 28`**；**T→F→T 往返逐字节自洽（T1 == T2，0 px）** ✅ —— 这正是你要验的修复目标，**不再是 task-80 那种"F/T 逐字节相同（0 px）"**。

## 2. 靶子 B：C 类归因标签 + "到底几个 Model 上屏" —— **PASS**
- `__probe().states` 原文（1110171，`models(true)`）：
```
{"disabled_color_semantics_unresolved": 20, "disabled_fxignore": 3, "disabled_no_color_driver": 2, "ok": 3}   # 合计 28 ✅
```
⇒ **与你预期的 `~20 unresolved / 2 no_color_driver / 3 fxignore / 3 ok` 逐项一致** ✅（`disabled_no_color_driver` 已从 22 → 2）
- `fallback_reason` 抽样（原文）：
```
{"node":"H_模型_星点01","state":"disabled_color_semantics_unresolved","fallback_reason":"color_slot_semantics_unresolved:u_emissive_highlight_intensity_Keyframe"}
{"node":"H_模型_星点02","state":"disabled_color_semantics_unresolved","fallback_reason":"color_slot_semantics_unresolved:u_emissive_highlight_intensity_Keyframe"}
{"node":"H_模型_光晕02","state":"disabled_fxignore","fallback_reason":"FxIgnore=TRUE"}
```
（本轮运行时抽样里出现的是 `u_emissive_highlight_intensity_Keyframe` 这一族；`u_main_color1/2/3_Keyframe` 未落在我抽到的 3 条里。）
- **1110171 现在几个 Model 上屏：`visible = 3`** —— 节点名 `M_模型_顶渐变`、`H_模型_球03`、`M_模型_球04`；
  **屏上 bbox = 272×108 px、对角线 292.7 px**；**武器在屏对角线 = 485.0 px**（bbox 606–993 × 325–615）⇒ **比值 = 0.6035**。t=1.15 时这 3 个都出窗（`visible 0`）。
- 小注（数据侧口径）：磁盘 `viewer.json` 里 28 个 Model 节点的 `color_family_unresolved` 键均为 `null`（该记录名未落在顶层；运行时 `fallback_reason` 正常输出），如需在数据侧留痕请确认字段名。

## 3. 默认零回归 —— **PASS**
| 皮肤 | SFX OFF 门控帧（N≥5） | 与 task-80 对比 | MASK 五读数 |
|---|---|---|---|
| **1110177** | **`e62c1c58e5bdc383`** | **sha 相同、像素差 0（max 0.0）** ✅ | `1.826 / 0.2829 / 0.5745 / 18.242 / 0.989 / 0.689`（= 基线）✅ |
| **1110171** | `48b6c95c1165c80a` | sha 与 task-80 的 `09611e2e90b49bc0` 不同，但**像素差 0（max 1 灰阶 0.00392）**、MASK 五项一致 | `2.449 / 0.1232 / 0.4865 / 3.394 / 0.273 / 0.106`（= 基线）✅ |
- `applied`：**1110177 3 == 3**、**1110171 7 == 7**；`failed=[]`、`missing=[]`、`env_warn=null`；两皮肤 OFF↔(SFX+models 往返) 后回到默认帧 ✅。
- **404 全页逐条：只有 1 条 `http://127.0.0.1:8765/favicon.ico`** ✅；GLB 请求 **40 条全 200、0×404**；贴图 **84 条全 200、0×404**；控制台错误 1 条（favicon）。
- **`Runtime.exceptionThrown` 0 + evaluate 级 0** ✅；**adapter 页内 fetch 字节哈希 = `C3BEF3C4EB27F809`（103,154 B）= 磁盘** ✅。

## 4. 1110177 回归 —— **PASS（`models(F)` 也会隐藏）**
- SFX OFF **`e62c1c58e5bdc383`** = task-80 **逐字节相同**（diff 0.0）+ MASK 五项一致 ✅。
- 5 个真图集节点：`H_p_烟雾_02` **64** / `H_鬼火_星点_1` **4** / `H_p_闪电` **16** / `H_ shandian01_1_1` **16** / `M_lizi_闪电_01` **4**，`fallback` 全 `null` ✅（与 task-80 一致）。
- `models(T)`：`total 43 / ok 31 / visible 31 / groupVisibleN 43` ✅；t=0.30 帧 = **`a6bd7f3e311e1c0c` = task-78/80 逐字节相同** ✅（本轮修复**未改动 T 态画面**）。
- **`models(F)` 现在确实隐藏模型**：`visible 0 / groupVisibleN 0`；F 帧 = **`0ff65ed7b8b91b0a`**，与 task-67/70 的"无模型"同 t 帧**逐字节相同** ✅；**T-vs-F = 123,328 px = 8.6646% 画布**（bbox `x[596,1143] y[271,816]`，548×546，对角线 773.6 px）。
- 往返：T == T2（0 px）✅；states：`{ok 31, disabled_fxignore 1, disabled_color_semantics_unresolved 9, disabled_no_color_driver 2}`（合计 43）⇒ **新标签在两把皮肤都生效**。

## 5. 6 皮肤回归 —— **PASS**
| 皮肤 | applied/expected | failed / missing | env_warn | SFX 默认态 |
|---|---|---|---|---|
| 1110024 | **5 == 5** | 0 / 0 | null | `SFX 关闭`（disabled=true, pressed=false） |
| 1110129 | **5 == 5** | 0 / 0 | null | 同上 |
| 1110145 | **7 == 7** | 0 / 0 | null | 同上 |
| 1110152 | **2 == 2** | 0 / 0 | null | `SFX 关闭`（disabled=false, pressed=false） |
| 1110165 | **4 == 4** | 0 / 0 | null | 同上（disabled=true） |
| 1110171 | **7 == 7** | 0 / 0 | null | `SFX 关闭`（disabled=false, pressed=false） |

## 6. 未变清单 —— **PASS**
`viewer.js B9C7281E1EE7A819`、`m1110177 A05C4F2C8DDFCF9A`、5 张真图集 + `atlas171 6480F7FC1914F0C4`、3 个新 GLB（`A4EA1EC706F7E71C` / `21A1F52546D0CD12` / `B9E06158D88FBBD1`）、`1110171` 两枚、`1110177` 两枚 —— **开工前后哈希全一致**。

## 7. 诚实边界
1. 我**只验了语义与标签**：`disabled_color_semantics_unresolved` 的 20 个节点**仍不渲染**（你要求"不猜 slot 语义"），本报告不评估"它们应该渲染成什么"。
2. `u_main_color1/2/3_Keyframe` 一族**未出现在我抽到的 3 条样本**里（样本是 `u_emissive_highlight_intensity_Keyframe` + `FxIgnore=TRUE`）；若要覆盖全部轨道名，建议探针把 `fallback_reason` 的**去重清单**也吐出来。
3. 模型屏上 bbox 取"T 与 F 的差异区"作代理（F 态几何消失 ⇒ 该差异区就是模型实际占屏范围）；比值分母用武器在屏对角线 485.0 px。

## 8. 纪律与产物
- 只读 `08Lifeafter wiki/**`（未改任何文件）；单浏览器 `FXVA81_prof` / 端口 **10145**；结束按 `user-data-dir` 反查真实 PID `taskkill /T /F`（8 进程）；**端口 10145 无 LISTEN**、我的 profile chrome = 0、全机 chrome = 0。
- 产物（仅写 task 允许的三条路径）：本报告 + `FAILCLOSED_verify_20260920.json`；截图 `sfx_verify_shots9/`（1110171 四个冻结时刻 × T1/F/T2 + OFF/bg；1110177 T/F/T2 + OFF/bg）。
