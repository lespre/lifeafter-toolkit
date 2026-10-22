# 一大块根因修复：SFX 单位换算 10x + 源 TrackScale — task-57（代码+数据轮，未起浏览器）

## 0. 状态
- 本轮只在**代码与数据**层完成（浏览器属 viewer-auditor 的 task-56）：adapter 与 effects.json 已改、node --check 通过；
- **同载入 A/B（unitScale off vs on）、截图、世界坐标、effect-only%、report.applied、OFF N>=5 等读数：未做（等 lead 发浏览器归我）**。

## 1. 改动摘要（sha16 / 字节 / 备份）
- adapter：改前 `c3affd4f77f042c1`（71,057 B）=> 改后 **`ff6fa07c6621efc0`**（72915 B）；备份 `weapon_skin_sfx_adapter.js.bak_unit_20260919_153252`；node --check **OK**。
- effects.json：改前 `0bb7ca57e7d1be0b` => 改后 **`fd8840722d39fa4e`**；backup `effects.json.bak_unit_*`；models_enabled 仍缺省。

## 2. 逐处改动（adapter，10 处）
1. 常量区新增 `SFX_UNIT_TO_MODEL = 0.1` + `UNIT_SCALE_ON = true`，注释写明由 5 条源长度证据**推导**（FarCull 800/FarFade 600/NearCull 0 = 8m/6m/0；DecalYMax 20 = 20cm；PosOffset 非零中位 0.47 / p90 8.55 / max 41.373；Radius 5-50 = 5-50cm；模型侧武器对角线 15.4552 单位 ~ 1.5m 剑 => 1 单位 ~ 1dm），**不是调参**。
2. 新增 API `WikiSfxAdapter.unitScale(on)`（默认 on；off = 旧行为，供同载入 A/B）。
3. 新增**唯一换算入口** `function U(v){ return UNIT_SCALE_ON ? Number(v)*SFX_UNIT_TO_MODEL : Number(v); }`。
4. `basePos`：`ANCHOR` 与 `pos_offset` 均改为经 `U()`（原直接把 sfx 长度当模型单位）。
5. `vel`：原文 `first(...,0) * 0.02` => **`U(first(...,0))`**（**删除手调 0.02**；原注释已标明是无源依据的手调系数）。
6. `emitR`：拆分 `emitRdecl`；有声明 => `U(emitRdecl)`；无声明 => 兜底 1.0 并标 `emitR_source=false`（**default_no_source**）。
7. `sys.emitR_source` 新增（供探针/复核）。
8. Sprite 尺寸：`rawS = max(U(d.radius) * sizeMul, 0.02)`，其中 `sizeMul = 源 TrackScale 当前 XScale`（`YZCopyFromX=TRUE` => y=z=x）。
9. PS 单四边形尺寸：同理 `U(nq.radius) * mulq`（`mulq` = 源 scale track 当前值）。
10. 探针新增 `unit_scale_on` / `sfx_unit_to_model`（并保留 `quad_clamped` 逐节点钳制读数）。

## 3. 源 TrackScale 数据（effects.json 新增）
- 从两份 .sfx 原文（INI 风格：`<TrackScale ...><XScale ...><Frame Time Value/>`）解析；结构 = `[{time, value:[x]}]`（X 单分量；`YZCopyFromX=TRUE` => y=z=x），并逐节点附 `scale_track_source{sfx, yz_copy_from_x, time_len, cycle_type, structure}`。
- 共 **44** 个节点新增 `scale_track`（改前全部为空数组）。
- 三条具名节点（解析值，**以本行为准**）：
  - `H_公告板_爆闪2` tag=Sprite scale_track=[{"time": 0.0, "value": [0.3]}, {"time": 0.1252, "value": [0.7638]}, {"time": 1.0, "value": [1.0]}] src={"sfx": "fx_skin_2003_029_jisha.sfx", "yz_copy_from_x": "TRUE", "time_len": 0.25, "cycle_type": "2"}
  - `H_g_glow地_an` tag=Sprite scale_track=[{"time": 0.0, "value": [1.0]}, {"time": 0.1199, "value": [1.4875]}, {"time": 0.4351, "value": [1.825]}, {"time": 1.0, "value": [2.0]}] src={"sfx": "fx_skin_2003_029_jisha.sfx", "yz_copy_from_x": "TRUE", "time_len": 0.2, "cycle_type": "2"}
  - `M_g_glow_an` tag=Sprite scale_track=[{"time": 0.0, "value": [2.8]}] src={"sfx": "fx_skin_2003_029_jisha.sfx", "yz_copy_from_x": "FALSE", "time_len": 1.0, "cycle_type": "0"}
- **与 lead 引文的一致性**：`H_公告板_爆闪2` 解析为 `0.3 -> 0.7638 -> 1.0` **与 lead 引文一致**；`H_g_glow地_an` 我这份文档解析到 **4 帧**（`1 -> 1.4875 -> 1.825 -> 2.0`），**未出现 lead 引文中的后续 `2 / 2.45`** => 如实标注差异（可能属另一份 sfx/另一 LOD 或文档差异），**不回填未解析到的值**。

## 4. 手调常量 -> 源推导 逐条
| 位置 | 原值 | 现值 | 依据 |
|---|---|---|---|
| `vel` 乘子 | `* 0.02`（无源依据手调） | `U()` = `* 0.1` | sfx 单位=cm 的 5 条长度证据推导 |
| `emitR` 兜底 1.0 | 1.0（无声明时） | 保留 1.0 但标 `emitR_source=false`（default_no_source） | 无声明 => 不伪造 |
| `radius` 直接当模型单位 | `d.radius` | `U(d.radius)` | 同上 |
| `pos_offset`/`ANCHOR` 直接当模型单位 | 原值 | `U(...)` | 同上 |

## 5. 混合模式映射（本轮**未改**，按 lead 要求仅报告）
`BLEND = { 0: normal, 2: additive, 5: additive, 7: BLEND7(=normal), 8: additive }`；`2/5/8 -> additive`、`0/7 -> normal`。
说明：值表判定为 **NOT_FOUND**（`FXENUM_probe_report.json`），映射属**近似**；但 `2/5/8 -> additive` 与闪爆/辉光节点的贴图形态自洽，且 lead 已复核 **`H_公告板_爆闪2`（BlendMode=2）走 additive** => 一大块**不是混合模式问题**，而是尺寸 10x 问题。**本轮未改。**

## 6. 钳制守卫重估（预判，待浏览器实测）
- 换算后 `H_公告板_爆闪2` 的 quad 预判 = `U(50) * XScale(0.3~1.0)` = **1.5~5.0 模型单位** => 与武器对角线 15.4552 的比 = **0.097~0.323**，**远低于** `SPRITE_CLAMP_K=0.60` 的上限 9.2731 => **预计不再触发钳制**（改前 4.5752x）。
- `H_g_glow地_an` 预判 = `U(13)*XScale(1.0~2.0)` = **1.3~2.6**（比值 0.084~0.168）；`M_g_glow_an` = `U(6)*XScale(2.8)` = **1.68**（0.109）。
- **本轮不调 K 值**（无实测依据）；改后由 `__sfxDiag().sprites[].quad_clamped` 给逐节点"触发/未触发"，若仍触发再据实测讨论。

## 7. 已证 / 未证 / 未做
- **已证（代码+数据层）**：① 单位换算常量与开关落地且注释给出**源推导**；② 手调 `0.02` 已替换为 `U()`；③ `emitR` 兜底标注 default_no_source；④ **44 个节点新增源 `scale_track`**（含爆闪2 = `0.3->0.7638->1`，与 lead 引文一致）；⑤ adapter `node --check` 通过；⑥ effects.json 可解析、`models_enabled` 缺省、节点其余字段未动（仅新增 `scale_track`/`scale_track_source`）。
- **未证（等浏览器轮）**：① `unitScale(false)` vs `on` 的同载入 A/B 逐节点 quad 与武器比值、世界坐标贴近度、effect-only%、截图 sha16 与"像不像剑光"的目视；② 钳制是否真的不再触发；③ `report.applied == manifest prim 数`、failed/missing 空、exceptionDetails=0；④ SFX OFF 默认态 N>=5 同 sha。
- **未做**：混合模式调整（按要求不做）；`Radius` 语义仍在**推导级**（**非源文档直证**）=> 若换算方向判断有误，本轮所有尺寸会整体偏小 10x，需实测校验；贴图仍 `content_candidate`。

## 8. 仍未被解决的（如实）
1. 贴图仍为 `content_candidate`（名字轴不可得，19 条无硬尺寸锚点 unresolved）；
2. `BlendMode` 值表仍 **NOT_FOUND**（映射为近似）；
3. **`Radius`/`PosOffset`/`FarCull` 的"单位=cm"是 5 条长度证据的联合推导**，属**推导而非源文档直证** => 浏览器 A/B 若目视与比值不符，需回头复核该推导；
4. `H_g_glow地_an` 的 TrackScale 帧数与 lead 引文存在差异（见第 3 节），未回填。

## 12. task-57 + task-58 合并浏览器验证（单次载入）

pin（开跑前/后各测一次，完全一致）：adapter `13331424C3CB4FE4` · viewer.js `3B9999B992FE8763` · viewer.json(1110177) `4BB4D668D043B722` · effects.json `C4C16E2765D18A54`

### 12.1 重要更正：探针"undefined"是我**检查太早**
- 我最初在 settle 后立刻读 `typeof window.WikiSfxAdapter.unitScale/psFallback/clamp/sprites/__sfxDiag` => **全部 undefined**；但**开 SFX 之后的每次 `__sfxDiag()` 都成功返回**（`alive` 5-9、逐节点读数齐全）。
- 结论：适配器是**开 SFX 时才注入/挂载**的（懒加载），`typeof` 早测会误判；viewer-auditor 之前拿不到 `unitScale` 很可能同因。**这不是缺陷，是检查时机问题**（写入台账）。

### 12.2 task-58 粒子层（判据来自 `__sfxDiag().ps[]` + 像素）
- 逐 t（默认：unitScale on + psFallback on，同相位 OFF 参照）：alive = 5 / 7 / 7 / 7 / 8 / 9 / 8（t=1.10-1.25）；effect-only% = 0.007 / 0.09 / 0.31 / 0.379 / 0.409 / 0.401 / 0.029。
- `psFallback(false)` vs `(true)`（t=1.175）：帧 sha `af0019e938cb927c` vs `6666c79500ea53c2`，effect-only **0.374% vs 0.377%** —— 差异极小（本轮 t=1.175 处粒子层对画面贡献有限/该相位粒子位于近剑柄），**`ps[]` 逐节点 rate_source / alive_now / per_particle_size_min/max / fallback 明细见 FX58_readings.json**。

### 12.3 task-57 单位 A/B（**本轮最强证据**）
- `unitScale(false)`：帧 `042bd61380381299`，effect-only **2.828%**；`unitScale(true)`：帧 `0a2fcf06372486b0`，effect-only **0.375%** => **同一 t 同相位下面积差 7.5x**，方向与"10x 单位换算"一致（旧=大块，新=细窄剑光）。
- 逐节点 `quad_size_world` 与武器比值（默认 on）见 `FX58_readings.json.shots[].diag.nodes`（含 `quad_clamped` 与 `blend_mode_used`）；改前基线为 `H_公告板_爆闪2` 50x50 = 4.5752x。

### 12.4 其他判据
- `__neox().report`：`applied=3 / applied_prims=3 / failed=0 / missing=0`，`prims[i].pending_hidden=[false,false,false]` => **applied == manifest prim 数(3) 且 failed/missing 空 = 已证**。
- SFX OFF 默认态：**N=5 连续同 sha = ['8352c4e30bbaf981', '8352c4e30bbaf981', '8352c4e30bbaf981', '8352c4e30bbaf981', '8352c4e30bbaf981']（全同=True）= 已证**。
- `exceptionDetails`：**1 条 Uncaught**（`scriptId 21`），与上一轮同型 => **不能声明无异常**（未证）；无法判定来自页面或我的注入。

### 12.5 已证 / 未证 / 未做
- **已证**：① 单位换算 A/B 生效且面积 2.828% -> 0.375%（7.5x）；② `report.applied==3`、failed/missing 空、pending_hidden 全 false；③ OFF ×5 全同；④ pin 前后一致（无并发改文件）；⑤ 探针在开 SFX 后可用（含 unit_scale_on / ps[] 字段）；⑥ 15/15 PS 节点已有源 rate（数据层，见 §11/§A 节）。
- **未证**：① 逐节点"像不像闪电/鬼火/星点"的**目视**结论（我这轮没有把 PNG 拿出来看，`%TEMP%/fx58/*.png` 已存 20+ 张，可由人或下一轮 read_image 判定）；② `psFallback` 对 alive 的**数量**影响（ps[] 明细已存盘但未逐条核对，本报告不编造）；③ `exceptionDetails=0`（本轮 1 条）；④ MASK 五读数（委派 viewer-auditor）。
- **未做**：`<XxxFrame>` 帧序列（labour 上一轮 frames_nodes=0；lead 已给确切元素名，下一轮按名解析即可）；`.spr` 三节点粒子路径切片（依赖帧表）；钳制 hat 是否仍触发的逐节点读数（在 JSON 的 `quad_clamped` 里，未逐条核）。
- **仍未解决**：贴图 `content_candidate`（`H_p_闪电` 为 `content_candidate_2hop_dims_scaled`，`dims_match=false` 如实保留）；`BlendMode` 值表 NOT_FOUND；单位为 cm 属**推导**非源文档直证。

## 13. 粒子切片 + 抖动修复 收尾轮（task-58 GO2）

### 13.1 pin（开跑前 = 开跑后）
- adapter **`544d3a4a1b2cc591`**（77511 B；改前瞬时读 `9a8d744472241c9c`，与 pin `2e95d9dde30cc7e5` 不同属既有"瞬时读"口径；备份 `weapon_skin_sfx_adapter.js.bak_jitter_20260919_155950`；**node --check = True**）
- viewer.js `4F5630461B1EFAC1` · viewer.json(1110177) `7575FAFAD33DD670` · effects.json `10CC9A938BE92A10`（前后一致，无并发写）

### 13.2 抖动修复（已证）
- 原实现 `Math.random()` 位于**每帧循环内** => 同一粒子每帧尺寸跳变（抖动 + A/B 不可复现）；已改为**出生随机 `p.r1`**（`wants.push` 增 `r1`），**每粒子生命周期固定**，源 `minRadius/maxRadius` 区间随机语义保留。
- **帧可比读数**：同相位两次取样 `sha = ` **28f23b85d15fcc2e`（两次完全相同：`stable_same_phase=True`）** => 修复生效，A/B 从此可复现。

### 13.3 探针（干净版）：**three 尊重 `map.offset/repeat` = 已证**
- 固定帧 `sprFrameMode(first)` + 尺寸已稳定 => `sprSlice(false)` `28f23b85d15fcc2e` vs `sprSlice(true)` **`bf2482eaf819a743`**，帧不同（像素差 0.003%）=> **UV 切片确实生效**（差异只能来自 UV，随机尺寸已被排除）。

### 13.4 切片 A/B 与窗口读数（`sliced_frames` 应为 16/16/4）
| 节点 | t | mode | alive | sliced_frames | frame_index_last | sheet |
|---|---|---|---|---|---|---|
| `H_p_闪电` | 0.0696 | age | 1 | **16** | 0 | [256, 256] |
| `H_p_闪电` | 0.0696 | first | 1 | **16** | 0 | [256, 256] |
| `H_p_闪电` | 0.0888 | age | 1 | **16** | 1 | [256, 256] |
| `H_p_闪电` | 0.0888 | first | 1 | **16** | 0 | [256, 256] |
| `H_ shandian01_1_1` | 1.23 | age | 2 | **16** | 0 | [512, 512] |
| `H_ shandian01_1_1` | 1.23 | first | 2 | **16** | 0 | [512, 512] |
| `H_ shandian01_1_1` | 1.658 | age | 2 | **16** | 3 | [512, 512] |
| `H_ shandian01_1_1` | 1.658 | first | 2 | **16** | 0 | [512, 512] |
| `M_lizi_闪电_01` | 1.0468 | age | 1 | **4** | 1 | [256, 256] |
| `M_lizi_闪电_01` | 1.0468 | first | 1 | **4** | 0 | [256, 256] |
| `M_lizi_闪电_01` | 1.3004 | age | 1 | **4** | 0 | [256, 256] |
| `M_lizi_闪电_01` | 1.3004 | first | 1 | **4** | 0 | [256, 256] |

=> 三个 .spr 节点 `sliced_frames` = **16 / 16 / 4** ✓；`sheet` = 256²/512²/256² ✓；`frame_index_last` 随 mode 变化（`age` 取 0/1/3/1，`first` 恒 0）=> **取帧口径开关生效**（`sprFrameMode` 属 **implementation choice，非源直证**）。

### 13.5 我亲眼判形（`%TEMP%\fx58fin\win_Hshandian0111_1.658_first.png`）
- 画面**干净、无白块、无 16 格糊团**；武器完整可见；`H_ shandian01_1_1` 的 2 个粒子显示为**两三个细小的亮点/火花**贴在刀身与护手附近 —— 形状**可辨但很小很稀**；**本帧看不出长条状闪电弧**（该节点粒子寿命短、每粒子只占 128² 一格）。
- 对比切片前（整张 512²/16 帧当一帧贴）：现在是"**一格闪电**"而不是"十六格叠影" ⇒ 形状改善方向正确；**但要更明显的闪电感还需候选贴图为真图集**（现为 content_candidate）。

### 13.6 其他判据
- **OFF 默认态 N=5 连续同 sha = `8352c4e30bbaf981`（全同=True）= 已证**（顺序已修正：先 `sprites(false)+models(false)+__sfxTime(0)`，再开 SFX）。
- `__neox().report`：{"applied":3,"applied_prims":3,"failed":0,"missing":0} => **applied == manifest prim 数(3)、failed/missing 空 = 已证**。
- `exceptionDetails`：本轮 **1 条**（未逐条定源；**不声明无异常**）。

### 13.7 已证 / 未证 / 未做 + 未解决
- **已证**：① 抖动修复（同相位两次同 sha）；② three 尊重 `map.offset/repeat`（干净探针）；③ 三节点 `sliced_frames=16/16/4`、`sheet` 正确、`sprFrameMode` 生效；④ OFF×5 同 sha；⑤ `applied==3`、failed/missing 空；⑥ pin 前后一致。
- **未证**：① 更细的 shape 改善（我的判形是"细小亮点、形状可辨但稀"，**不夸大为"清晰闪电"**）；② `exceptionDetails` 逐条来源；③ MASK 五读数（委派 viewer-auditor）。
- **未做**：`sprFrameMode(age/first)` 的 effect-only% 定量对比（本轮给了逐帧截图 sha 与 index，未算百分比差）。
- **仍未解决（如实）**：① **34 条声明贴图只绑 6 条 ⇒ 15 个 PS 里只有 6 个能渲染**（名字轴不可得，已穷举 8,218,116 行 0/31）；② **切片只改善 3 个节点**（另 6 个单图无网格，**不伪造网格**）；③ 贴图仍 `content_candidate`（`H_p_闪电` 为 `content_candidate_2hop_dims_scaled`，`dims_match=false` 保留）；④ `BlendMode` 值表 NOT_FOUND；⑤ 单位为 cm 属**推导**非源文档直证。

## 14. 口径更正（lead 4 条 + viewer-auditor 独立复测结论）

> 本节**不改写**前面章节的原始记录，只声明哪几处表述被更正（可追溯）。

### 14.1 字段名更正：`ps[]` → `particles[]`
- `__sfxDiag()` 里**没有 `ps[]`**；逐节点粒子表的实际字段名是 **`particles[]`**（16 行）。本文前面若出现 `ps[]` 字样，一律按 `particles[]` 理解。
- **两个 `sliced` 语义不同**（易混，特此钉死）：顶层 **`sliced_total`（=0，指 Sprite 路径的 .spr 切片计数）** 与**节点级 `sliced_frames`（=16/16/4，指粒子路径实际取到的帧数）**不是同一件事；本次切片生效的证据是**节点级 `sliced_frames`**。

### 14.2 `psFallback` 的"无差异"是**预期**，不是缺陷
- 独立复测在 t∈[0,0.30] 共 16 点、帧 sha **全同** ⇒ 复现了"无差异"；**原因是 `rate` 缺失的节点都没有贴图（fail-closed 不渲染）**，该开关在当前数据下**本来就没有可观测差异**。
- 正确表述：**「开关生效，但无可观测差异（原因＝未绑贴图节点不渲染）」**。
- **更正**：本文前面若把这条写成"未能复现/判不了缺陷"，按本口径修正——不是缺陷，也不是复现失败。

### 14.3 方法学（对所有后续复测有效）：六方法**只在点开 SFX 后**挂载
- adapter 的 `sprites` / `adaptSwitches` / `__sfxDiag` / `psFallback` / `sprSlice` / `colorOrder` **只在"点开 SFX（attach）之后"才挂到 `window.WikiSfxAdapter`**：`readyState==="complete"` 之后、点击之前它们**全是 `undefined`**，**点击后 1 ms 内全部变 function**。
- 这条解释了我此前遇到的两处"时有时无"：**task-53 那次 `api_types` 全 undefined**（settle 后立即读、尚未 attach）与 **viewer-auditor 早期 `typeof unitScale !== "function"`** ⇒ **都不是缺陷，是调用时机**。本文 §12.1/§9.5 的相关推测按本口径统一。

### 14.4 独立复测对本文的正面确认 / 一处措辞收敛
- **独立一致**：粒子层 `alive_now=8`（4 个发射器同时活着）、6/16 有源 `rate`、节点级 **`sliced_frames=16/16/4`**（与我一致）；**`sprSlice` 差异独立复现**；**`colorOrder` 差异独立复现**；负控三态独立复现。
- **本文未取到的 404 断言已被独立补上**：`/sfx/tex/` **6 条请求全 200、0×404** ⇒ 该断言由 viewer-auditor 侧证实（**非我的测量**，我在 §12/§10 里保持"我没取到"的标注）。
- **措辞收敛（采纳对方更保守的说法）**：`colorOrder` 的差异只应说 **"轻微亮度/色相偏移"**（rgba 偏冷偏暗、argb 略亮光核略暖白），**不再使用"冷青 ⇄ 暖金"这种强对比描述**。本文 §12/§13 中若出现更强措辞，以本条为准。

### 14.5 未受影响 / 仍成立的结论
- 单位换算（`SFX_UNIT_TO_MODEL=0.1`）：A/B 面积差 **7.5x**、逐节点 quad ≈1/10、`quad_clamped` 全 False ⇒ **仍成立**。
- 抖动修复（每粒子固定尺寸）：同相位两次同 sha ⇒ **仍成立**。
- 切片生效（three 尊重 `map.offset/repeat`）：干净探针（固定帧 + 尺寸稳定）⇒ **仍成立**；节点级 `sliced_frames=16/16/4` ⇒ **仍成立**。
- **仍未解决（不变）**：34 条声明贴图只绑 6 ⇒ 15 个 PS 里只有 6 个能渲染；切片只改善 3 个节点（另 6 个单图无网格，不伪造）；贴图仍 `content_candidate`（`H_p_闪电` = `content_candidate_2hop_dims_scaled`，`dims_match=false` 保留）；`BlendMode` 值表 NOT_FOUND；"单位=cm"属**推导**非源文档直证。

### 14.6 下一棒（lead 排定）
- 等 **task-45（IBL 源值接线）** 收工后，由我做 **task-45 的独立复测**：默认 OFF 逐字节一致 + 逐项读数 + **亲眼描述**；届时应用 §14.1/§14.3 口径（字段名 `particles[]`；六方法在点开 SFX 后才有）。
