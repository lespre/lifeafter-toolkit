# task-48 全量回归验收报告（P1-F）—— 7 皮肤 + 板页

**结论：PASS 5 · WARN 1 · FAIL 1（FAIL 为既有遗留，非本轮回归）**

| 皮肤 | 判定 | 一句话依据 |
|---|---|---|
| 1110024 | **PASS（改动前+重切前）→ §10 改后基线 → §13 一致性修复后复核 PASS** | task-48 时：`applied 5/5`、failed/missing 空、族号全对、`envMode=source_ibl`+6 面、0×404、console 空、截图=亮银金剑；其后 Lead 把 `t_custom_ibl` 改回声明值 `indoor.cube` **且** cube 面已重切 ⇒ 改后 5/5 仍全绿、settle 后帧 `4785b69195428b9b`（详见 §10/§8.2） |
| 1110129 | **PASS** | `5/5`、族号全对（含 per-prim `_c/_d/_e/_f` 变体）、6 面、0×404、截图=深色金属枪有结构边光 |
| 1110145 | **PASS（改动前）→ 改后基线见 §9** | task-48 时为"刻意未改的对照"（`7/7`、族号全 014、6 面）；Lead 随后修好其基色（manifest `7da4b5b5bee8d496` → **`9c2edac7bcd63305`**），改后复测 **7/7 + 族号仍全 014 + settle 后帧 `fe7c9a231358b3ce`**（详见 §9） |
| 1110152 | **PASS** | `2/2`、族号 009、6 面、截图=深色金属枪有冷高光 |
| 1110165 | **PASS** | `4/4`、族号 165、6 面、截图=墨绿黑枪有尖刺与边光 |
| **1110171** | **WARN（时序窗口，非持久）** | `7/7`+族号正确；prim1 在**载入后固定时点**采样为 `envMode=missing_source_ibl`、`ibl_faces=0`，**settle 判据下 ~6.9–7.3 s 自愈为 `source_ibl`+6 面**（§5.2）；task-48 目视帧**已复核为 settle 后态**（§5.3） |
| **1110177** | **FAIL**（旧有 404）· 默认基线 **`baseline_under_investigation`** | `3/3`+族号正确，但 **3×404 `src_tex/gpk_1229.png`** —— 既有遗留（task-46 待清）；默认帧基线经 §14 三点取帧判定为"**task-48 那帧是早期态；settle 后稳定读数 = p50 0.2829 / p95 0.5745 / >0.5 18.242% / >0.75 0.989% / 暖色 0.689%**"，单一 sha 不作为基线（待 Lead 确认转正） |

> 任务书里的硬指标（`applied == expected_prims`、`failed=[]`、`missing=[]`、`hidden` 空、每 prim `manifest_fams == runtime_fams`）**7/7 皮肤全部满足**；WARN/FAIL 都出在硬指标之外的附加检查上。

## 1. 判定口径与 pin（sha16）
| 对象 | 测量时 sha16 | 备注 |
|---|---|---|
| `weapon_skin_viewer.js` | **`3357CD87518C6E8A`** | 与任务书一致；sweep 前后各读一次未变 |
| `weapon_skin_sfx_adapter.js` | **`1CD4AC5454D1F27A`** | 一致 |
| `board.html` | sweep **起** `3CD661B80E487FFC` → **末** `718202FC4D29F603` | 板页部分单独用新版**重测**（§4） |
| `data/media/weapon_skin_media.js` / `.json` | `A1C671238396FC3F`(3,439 B) / `62417B57BBBFA4F9`(4,256 B) | 与 Lead 给的新值一致 |
| `data/media/weapon_skin_skeleton.js` | `F921EDF44D096F0E` | 一致 |
| manifest | 1110024 `EC2AB0C7A1FC5297`、1110129 `339513A853725477`、1110145 `7DA4B5B5BEE8D496`、1110152 `B7F349BA453CB727`、1110165 `DA7CC185997A74C6`、1110171 **`1E091B35F713A1A4`（报告出具时的值；现已变更为 `3B1BD860774D0BAB`，见 §8）**、1110177 `DE07399720411145` | **7/7 与 Lead 当时给的期望值一致** |

口径：默认页（非 lab）、`__post`/灯光/曝光/bloom **未动**；`expected_prims` 取自各皮肤 manifest 的 `primitives.length`；族号=`/(\d{3})/` 取通道文件名首段 3 位（与 viewer `famOf` 同口径）；截图用**稳定性门 N≥5（连续 5 帧 sha 全同）**、取帧前复核 canvas rect（7/7 `rect_unchanged=true`）。
**`hidden` 字段说明**：本版 `__neox().report` 的键为 `[applied, applied_prims, base, failed, glb_sha, manifest_sha, meshes, missing, parser_sha, prims, prims_total]`，**没有 `hidden`**；改用 `__texReady().meshes[].mat_visible` 与 `__acceptanceReport().meshes[].mat_visible` 判定（**7 皮肤全部 true**）⇒ 无被隐藏 prim。

## 2. 逐皮肤原始读数（硬指标 + 族号）
| 皮肤 | prims | `__neox()` | mat_visible | 族号校验 | envMode / cube | 404 | console |
|---|---|---|---|---|---|---|---|
| 1110024 | 5 | applied 5、failed []、missing [] | 全 true | **全对**：map/normal/rough/metal 均 `024` | 5/5 `source_ibl`、6 面 | 0 | 0 |
| 1110129 | 5 | 5、[]、[] | 全 true | **全对**：prim0 `008`、prim1 `008_c`、prim2 `008_d`、prim3 `008_e`、prim4 `008_f`（repack 全 `008`） | 5/5 `source_ibl`、6 面 | 0 | 0 |
| 1110145 | 7 | 7、[]、[] | 全 true | **全对**：全 `014` | 7/7 `source_ibl`、6 面 | 0 | 0 |
| 1110152 | 2 | 2、[]、[] | 全 true | **全对**：`009` / `009_c` | 2/2 `source_ibl`、6 面 | 0 | 0 |
| 1110165 | 4 | 4、[]、[] | 全 true | **全对**：`165` / `165_c` / `165_d` / `165_e` | 4/4 `source_ibl`、6 面 | 0 | 0 |
| 1110171 | 7 | 7、[]、[] | 全 true | **全对**：prim0-3 → `012`（`param_repack_012` / `rough_repack_012`）、prim4-6 → `010`（`param_repack_010` / `rough_repack_010`） | 6/7 `source_ibl`+6 面；**prim1 `missing_source_ibl`、0 面** | 0 | 0 |
| 1110177 | 3 | 3、[]、[] | 全 true | **全对**：全 `029`（`param_repack_029` / `rough_repack_029`） | 3/3 `source_ibl`、6 面（`deferred_retries=2`） | **3× `gpk_1229.png`** | 3 条（同一 404） |

**关键结论（任务书重点）**：Lead 改的是 `Tex0`/`t_basecolor` 的**文件名**，而族号由文件名正则派生 —— 实测 **7 皮肤 / 30 个 prim 的 `manifest_fams ⊇ runtime_fams` 全部成立**（`rough_repack_*`/`param_repack_*` 族号与所属 prim 家族一致）⇒ **改基色没有破坏族号派生**。晶体 prim 的 `metalness_map=null / metalness=0`、`roughness_map=rough_repack_*` 属既有设计（非异常）。cube gate：`qiangpi / car_studio01 / gdansk_shipyard_buildings / glazed_pat… / bg61f_…` 全部 `ready:true failed:false faces 6/6`，`rebind_pending=false`。

## 3. 截图（7 张，全部**亲眼看过**；门槛 N≥5、`gate_tries` 5–9）
| 皮肤 | 文件 | sha16 | 亲看结论 |
|---|---|---|---|
| 1110024 | `REG48_1110024.png` | `d11f9b58fd15b07f` | **像**：亮银/金金属剑身，高光层次清晰，**无全黑、无剪影** |
| 1110129 | `REG48_1110129.png` | `247d72e41fd33986` | **像**：深色金属枪，结构/零件分明、有边光；偏暗但**不是全黑剪影** |
| 1110145 | `REG48_1110145.png` | `9b05fb131ccf6810` | **像**：紫水晶质感武器，蓝紫高光明显（对照皮肤，本轮未改） |
| 1110152 | `REG48_1110152.png` | `b9ebb8b7ca2bd426` | **像**：深色金属枪，冷色边光与结构可见；**无全黑** |
| 1110165 | `REG48_1110165.png` | `5126499a30e66bf3` | **像**：墨绿黑金属枪，尖刺轮廓与边光清楚；**无剪影** |
| 1110171 | `REG48_1110171.png` | `4b735cf0e2c3c618` | **像**：深棕/黑尖刺弩形武器，细青色边光；**轮廓清楚、非全黑**，但整体仍偏暗、无暖高光（与 `ALBEDO_AB_20260919.md` 结论一致）。**限定/复核**：该帧取于稳定性门、未区分窗口期/稳定态；但它与 settle 判据满足后取的门控帧**逐字节相同** ⇒ 即**稳定态**外观（窗口期对照见 §5.3） |
| 1110177 | `REG48_1110177.png` | `9a0243b928a0291a` | **最像游戏内**：奶白/奶油金剑身 + 红宝石 + 绿点缀，无蓝染、无 404 可见影响 |

帧统计（`REGRESSION_frame_stats.json`）：7 张的 `p99L` 0.83–0.89、`>0.25` 亮像素占比 10.2%–14.1%、`maxL=1.0` ⇒ **不存在全黑帧**（数值与目视一致）。

## 4. 板页（`board.html` 新版 `718202FC4D29F603` 上**重测**）
| 检查 | 判据 | 读数 | 判定 |
|---|---|---|---|
| console | 无 error（favicon 忽略） | `[]` | **PASS** |
| 评级勾选筛选 | 勾选→行数随动、清除→还原 | `115` 卡 → 勾「5典藏级（19）」→ **19** 卡 → 清除 → **115** 卡 | **PASS** |
| 骨骼行 | 37 个 id 可查 | `a[href^="skeleton_preview.html?id="]` = **37**（34 行 + 3 变体链接） | **PASS** |
| 自检告警文案 | `⚠ N 处`带数字、无 `[object Object]` | `["⚠ 1 处自检告警","⚠ 1 处自检告警","⚠ 41 处自检告警"]`（1110032=41、1110160=1、1110161=1；`[object Object]` 计数 0） | **PASS** |
| 徽标中文 | 不显示原始英文键 | `.skin-media-fidelity` 共 **8** 个：`源数据（候选级）`×6（极光剑/光影咏叹调/墨隐麒麟/灵态诱导/熔炉寒霜/金蟒啸焰）、**`材质近似`×1**（天马行空=1110145）、`未建（无材质链）`×1（灰色协议=1110169）；**原始英文键 0 个** | **PASS** |
| 徽标 `title` | hover 能读到依据 | **8/8 非空**，长度 31–231 字符（例：`材质保真度依据：基色按内容类改为 color 类（029_b_m）；fashion_qiangpi cube 按声明名从 res.npk#4620 重取并重切六面；晶体三层已接线但默认关闭…`） | **PASS** |

## 5. WARN 最小复现：1110171 **prim1** 无 IBL（稳定复现 5/5）
**复现步骤**：`board.html?b=weapon_skin_sfx_text_sources&view=wiki&sort=id&dir=desc` → `WikiWeaponViewer.open(WEAPON_SKIN_MEDIA.skins['1110171'])` → 等 `__neox()` → 读 `__texReady()` / `__acceptanceReport()`。同一皮肤**连续载入 5 次**（每次新导航）：
```
#1..#5  prim1_envMode=missing_source_ibl  faces=0  pending=False  neox_applied=7 failed=[] missing=[]
=> hits = 5/5   verdict = reproducible
```
**原始字段（原文，取两次载入均一致）**：
- `__texReady().meshes[prim=1]` = `{"prim":1,"kind":"crystal","family":"pbr_crystal","faces_loaded":0,"faces_total":6,"envMap_bound":false,"radiance_bound":false,"deferred_retries":1,"envMode":"missing_source_ibl","mat_visible":true,"tex_ready":false}`
- `__texReady().gate` = `[{"cube":"qiangpi","faces_loaded":6,"faces_total":6,"ready":true,"failed":false,"bound":false,"deferred_retries":1},{"cube":"car_studio01","faces_loaded":6,"faces_total":6,"ready":true,"failed":false,"bound":false,"deferred_retries":1}]`；顶层 `rebind_pending=false`、`rebind_count=1`、`rebind_err=null`
- `__acceptanceReport().meshes[chain_prim=1]`（节选）= `{"envMap":null,"ibl_faces":null,"env_mode":"missing_source_ibl","ibl_faces_count":0,"cube_dir_err":null,"required_slots":["Tex0","NormalMap","t_basecolor"],"runtime_missing":[],"declared_unlocated":[],"albedo_slot":"t_basecolor","fail_closed":false,"mat_visible":true,"tex_faces_loaded":0,"tex_faces_total":6,"tex_envMap_bound":false,"tex_deferred_retries":1,"status":"applied","uIblScale":null,"frag_len":0,"frag_has_our_radiance_override":false}`
- 对照：同皮肤 prim2/3/5/6（同为 `pbr_crystal`、同 cube `car_studio01`）均为 `env_mode=source_ibl`、`ibl_faces=6`、`uIblScale=1`。
- 而 manifest 里 prim1 **声明了** `t_custom_ibl = src_cube/car_studio01.dds`（该 cube gate `ready:true`），且 `__neox()` 仍报 `applied=7 / failed=[] / missing=[]` ⇒ **失败对 `__neox()` 不可见**。

**归类（已由 §5.1/§5.2 更正）**：**不是本轮基色改动引入**，也**不是持久缺陷**；真实性质 = **task-40「六面就绪才绑定」就绪门造成的「首解 prim IBL 空窗」**，对 1110171 prim1 而言窗口约 **6.6 s**（`open()` 返回后），**~7.3 s 内自愈**（§5.2）。判为 **WARN = 时序窗口**（需 owner 修法：先等 cube 就绪再建材质 / 窗口期状态标 `ibl_pending` / 逐 prim `env_warn`），不是 FAIL；`frag_len:0` 的解释已按 §5.1 作废。


### 5.1 更正（2026-09-19，与 Lead / shader-auditor 共同更正）
1. **`frag_len:0` 是报告口径伪影，不是"材质没编译/没注入"**。`__acceptanceReport().frag_len` 取自 `ud.__frag`，而 `__frag` **只在 IBL 注入块里写**；晶体注入写的是 `ud.__fragCrystal`。因此"晶体 prim 缺 IBL ⇒ `frag_len:0`"完全可能材质本身是编译好的。本报告 §5 原推断「prim1 走了另一条构建分支」**作废**。
2. **WARN 的真实性质 = "首解 prim 的 IBL 空窗"（task-40「六面就绪才绑定」就绪门的副作用）**：某个 cube 的**第一个**解析者拿到 `ready=false` ⇒ 以 `iblCube=null` 建成、状态 `missing_source_ibl`；兄弟 prim 从缓存拿到**已就绪**的同一 cube ⇒ 正常。prim1 恰是 `car_studio01` 的首解者（`__crystalOBCInfo` 显示其注入跑了 3 次 = 窗口期多轮重建）。
3. **§5 里"稳定复现 5/5"的含义更正为**：**在"载入后固定时点采样"时 5/5 命中窗口**（`__neox()` 出现 + 2.5 s 时采样），**不是**"永远没有 IBL"。settle 判据下该状态会在 ~7.3 s 后自动转好（见 §5.2）。

### 5.2 settle 判据复测（1110171，1 次载入；原始 `REGRESSION_settle_test.json`）
**判据**：页内 100 ms 轮询 `__texReady()`，**直到全部 prim 的 `envMode == 'source_ibl'`**（或 20 s 超时）；`t0` = 调用 `open()` 之前。
| 项 | 读数 |
|---|---|
| `open()` 返回耗时 | **710 ms** |
| **全绿（all_green）时刻** | **7,301 ms**（相对 t0；即 open 后约 6.6 s） |
| 采样数 / 命中窗口的采样数 | 32 / **27**（说明窗口真实存在，约 6.6 s 宽） |
| open 后首个采样（781 ms） | `modes=[]`（`__texReady()` 当时还没 meshes） |
| 窗口期代表采样 | `modes` 含 `missing_source_ibl`、`pending=false`、`rebind_count=0` |
| 全绿采样（7,301 ms） | `modes = [source_ibl ×7]`、`pending=false`、`rebind_count=1` |
| 终态 `__texReady().meshes[prim=1]` | `{faces_loaded:6, faces_total:6, envMap_bound:true, radiance_bound:true, deferred_retries:1, envMode:'source_ibl', tex_ready:true, mat_visible:true}` |
| 终态 `__acceptanceReport().meshes[chain_prim=1]` | `{env_mode:'source_ibl', ibl_faces_count:6, tex_envMap_bound:true, tex_radiance_bound:true, frag_len:24556, frag_has_our_radiance_override:true, uIblScale:1, status:'applied'}` |
| console / page errs | `[]` / — |

**⇒ 分界线结论**：**是窗口期，不是持久态**（同一判据下 ~7.3 s 内自愈；20 s 超时未触发）。WARN 的收尾建议：task-40 修法（**先等 cube 就绪再建材质 + 窗口期状态改 `ibl_pending` + 逐 prim `env_warn`**）与 **修复前/后的窗口时长（ms/帧）** 对照，修完我按**同一判据**复测确认窗口 = 0。


### 5.3 pre-fix 基线：窗口期 vs settle 后的「五读数」与两张对照帧（同一判据、同一浏览器会话）
> 目的：回答 Lead 的问题 —— task-48 的目视结论是否落在窗口期内。**结论：没有。** task-48 的 `REG48_1110171.png` 与 settle 判据满足后取的门控帧**逐字节相同**（sha256 均为 `4b735cf0e2c3c618…`）⇒「深棕近黑、无暖高光」是**稳定态**外观，不是窗口伪影。
> 方法：单浏览器 1 次载入；`open()` 后立刻取窗口帧；随后 100 ms 轮询等 `envMode` 7/7 全 `source_ibl`（判据同 §5.2）；满足后按 **N≥5 门**取 settled 帧；`bg = settled 态 __primOnly(-1)`，**两帧共用同一 mask**（同相机/布局）。

| 项 | 窗口帧（open 后 1.2 s 抓；当时 `envMode=[missing,missing,source_ibl×3]`） | settle 后帧（判据满足后 N≥5 门） | task-48 帧（`REG48_1110171.png`） |
|---|---|---|---|
| 文件 | `ALBEDO_SETTLE_pre_1110171_window.png` | `ALBEDO_SETTLE_pre_1110171_settled.png` | `REG48_1110171.png` |
| sha16 | **`3c2249e56afa3638`** | **`4b735cf0e2c3c618`** | **`4b735cf0e2c3c618`**（与 settled **逐字节相同**） |
| p50 | **1.000** | 0.1271 | 0.1271 |
| p95 | **1.000** | 0.4847 | 0.4847 |
| >0.5 | **58.015%** | 3.257% | 3.257% |
| >0.75 | **56.497%** | 0.269% | 0.269% |
| 暖色% | **54.540%** | 0.106% | 0.106% |
| meanRGB | 0.604 / 0.607 / 0.605（近白） | 0.183 / 0.192 / 0.176 | 0.183 / 0.192 / 0.176 |

- mask：29,320 px（画布 2.06%）；窗口帧↔settled 帧变化像素 31,439（≈2.2% 画布）。
- settle 判据读数（本次）：**`all_green_ms = 6,908`**、30 个采样中 **29 个**含 `missing_source_ibl`、20 s 超时未触发；终态 prim1 = `env_mode:source_ibl / ibl_faces_count:6 / frag_len:24556 / frag_has_our_radiance_override:true / uIblScale:1`。
- pin（pre-fix 基线）：viewer.js `3357CD87518C6E8A`、adapter `1CD4AC5454D1F27A`、1110171 manifest `1E091B35F713A1A4`。

**亲眼看（各一句）**：
- 窗口帧 `3c2249e56afa3638`：**武器上趴着一大块纯白扁平色块**（未绑 IBL 的晶体 prim 处于未定态）—— 这就是用户开局前几秒会看到的样子，明显异常、不是这把武器应有的外观。
- settle 后帧 `4b735cf0e2c3c618`：**深棕/黑尖刺弩形武器 + 细青色边光**，轮廓与零件清楚、非全黑剪影；与该皮肤稳定态一致（偏暗、无暖高光）。

**对 task-49 复测的口径（预先固化，修法落地后照此执行）**：① 先满足判据（`envMode` 全 `source_ibl`）**再**取帧并标「settle 后」；② 同一会话内再取一张窗口期帧；③ 两帧都给五读数 + 亲看；④ 报「窗口 = 0」用**同一判据**（100 ms 轮询、20 s 上限），并与 shader-auditor 的修前/修后窗口时长（ms/帧、I/O 与调度拆分）对齐。

## 6. 「本轮改动引入的回归」vs「本来就有的问题」
| 条目 | 归类 | 依据 |
|---|---|---|
| 1110177 3×404 `src_tex/gpk_1229.png` | **旧有** | 该 404 在基色改动**之前**的 A/B 报告（`ALBEDO_AB_readings.json`，21:55 那轮）里就已出现；Lead 已声明 task-46 清理 |
| 1110024 的 `t_custom_ibl` = `gdansk_shipyard_buildings` 而源声明 `indoor.cube` | **旧有（已在徽标注明）** | 1110024 徽标 `title` 原文写「t_custom_ibl 为源声明 indoor.cube 但盘上现绑 gdansk，已标 SUBSTITUTION_WARNING 未改」；本轮未动该槽 |
| 1110171 prim1 `missing_source_ibl` | **已定证：task-40 就绪门「首解 prim IBL 空窗」**（**非本轮基色改动**，**非持久缺陷**，~6.9–7.3 s 自愈；窗口期画面是**大白块**） | 见 §5.1/§5.2/§5.3：`open_ms=710 / all_green_ms=7301`（另一次 6,908）；`frag_len:0` 的解释已作废；task-48 目视帧 = settle 后态（逐字节相同） |
| 帧整体偏暗、暖高光≈0（1110129/1110152/1110165/1110171） | **旧有** | 与 `ALBEDO_AB_20260919.md` 同会话 A/B 一致：换成真基色后并未带回亮部/暖高光 ⇒ 属光/IBL/BRDF 路径，不是绑定错误 |
| 其余 6 皮肤的 404 / console / JS 异常 | **无** | 逐皮肤 0×404、0 console；`__neox().failed=[] missing=[]` 7/7 |

**FAIL 计数**：1（1110177，旧有 404）；**没有任何由本轮改动引入的 FAIL**。

## 7. 交付与运维
- 交付：本报告 + `REGRESSION_settle_pre.json`（§5.3 pre-fix 窗口/settled 原始） + `REGRESSION_settle_frames_metrics.json`（§5.3 五读数） + `REGRESSION_sweep_readings.json`（含逐皮肤 verdict/判据/族号明细/404/console/截图 sha）、`REGRESSION_frame_stats.json`、`REGRESSION_board_readings.json`（新版板页）、`REGRESSION_board_badges.json`（8 徽标原文）、`REGRESSION_warn_repro.json`（§5 复现原始） + `REG48_*.png` 7 张。
- 纪律：**未改任何文件**（只写上述交付）；未进 lab 口径；未碰曝光/灯光/bloom。
- 浏览器卫生：**四次运行**（sweep / 新版板页+徽标 / WARN 复现 5 载入 / settle 判据复测）**各只起 1 个**浏览器、跑完 `taskkill /PID <pid> /T /F` 杀整树；端口 **10061 / 10063 / 10065 / 10067 / 10069 全部无 LISTEN**，匹配我的 chrome 进程 0 个 ⇒ **已关闭、无残留**（未触碰他人 headless）。

## 8. 基线变更登记（2026-09-19，报告出具**之后**由 Lead 变更；本报告原读数不追溯修改）
| 对象 | 报告出具时 | 现（已核对） | 说明 |
|---|---|---|---|
| `1110171/neox_material.json` | `1E091B35F713A1A4` | **`3B1BD860774D0BAB`**（75,927 B） | prim6 的脏槽键 `<unresolved>`（`logical_path=common\textures\crystal_caustic_uvva.tga`）归位为 `t_caustic_tex`，`original_slot_key` 保留，证据级别 `declared_name_semantic_candidate` |
| `1110177/neox_material.json` | `DE07399720411145` | `DE07399720411145`（未变） | — |
| `weapon_skin_viewer.js` | `3357CD87518C6E8A` | `3357CD87518C6E8A`（316,396 B） | shader-auditor 的 task-49 修复**尚未落地** |
| `weapon_skin_sfx_adapter.js` | `1CD4AC5454D1F27A` | `1CD4AC5454D1F27A` | — |
| `board.html` | `718202FC4D29F603` | `718202FC4D29F603`（107,169 B） | — |
| `data/media/weapon_skin_media.js` | `A1C671238396FC3F` | `A1C671238396FC3F` | — |
| `data/media/weapon_skin_skeleton.js` | `F921EDF44D096F0E` | `F921EDF44D096F0E` | — |

- **对 §1 的影响**：§1 表里 1110171 manifest 的 `1E091B35F713A1A4` 是**报告出具时的值**，保留为历史读数；**后续复测一律以 `3B1BD860774D0BAB` 为 pin**。Lead 预计该改动**不影响默认帧**（caustic 层默认 OFF）—— task-49 复测时我会用**同一判据 + 五读数**核对（若默认帧 sha16 与 `REG48_1110171.png` 不同，即说明该改动有可见影响，会如实报）。

### 8.1 立方体面 PNG 的「重切前」指纹（供复测声明"重切前/后"）
另一修复子代理将按 **face-major** 重切 7 组立方体面 PNG（只写 `assets/3d/weapon_skin/*/src_cube/**`，旧文件备份为 `.bak_mangled_*`）。以下为**本报告出具后、重切前**的实测：`bak_mangled_files = 0`（全部 0）⇒ **尚未重切**。
| 皮肤 | cube | 面数 | 不同 sha16 数 | 首面 sha16 |
|---|---|---|---|---|
| 1110024 | `indoor` | 6 | 6 | 4FA21056199DFB46 … |
| 1110024 | `gdansk_shipyard_buildings` | 6 | 6 | 0E77AD1E968BD1EF … |
| 1110145 | `bg61f_light_spherereflectioncapture_1` | 6 | 6 | 1D39D9171E9A1223 … |
| 1110152 | `qiangpi` | 6 | 6 | A0C22BD85F5880A4 … |
| 1110165 | `bg61f_light_spherereflectioncapture_1` | 6 | 6 | 1D39D9171E9A1223 … |
| 1110165 | `glazed_patio` | 6 | 6 | 74D283DCAC18EBD1 … |
| 1110146 | `glazed_patio` | 6 | 6 | 74D283DCAC18EBD1 … |
> **复测声明口径**：task-49 复测时我会重新计算上表，并与本表逐面对比 —— **若任一面的 sha16 与本表不同，即声明"测于重切后"**，并把差值列出；若我把这些皮肤（1110024/1110145/1110152/1110165/1110146）纳入复测，会等修复子代理报完再测，避免混合两种输入。原始指纹（含每面 sha16）：`REGRESSION_baseline_pins_20260919b.json`。

## 9. 1110145 改后基线（Lead 小活；**该皮肤本轮最后被修，task-48 的那次 PASS 是改动前**）
| 项 | 读数 |
|---|---|
| pin（实测） | manifest **`9C2EDAC7BCD63305`**（45,943 B）✅ / `media.js` **`D1A16408CE10FC22`** ✅ / viewer.js `3357CD87518C6E8A` / adapter `1CD4AC5454D1F27A` / board `718202FC4D29F603` |
| `__neox()` | `applied=7`、`applied_prims=[0..6]`、`failed=[]`、`missing=[]`；`applied == expected_prims`（**7/7**）✅ |
| `mat_visible` | **7/7 true**（`__acceptanceReport()` 逐 prim）✅ |
| settle 判据 | **`all_green_ms = 1,427`**（100 ms 轮询，20 s 上限未触发；6 个采样、其中 5 个含 `missing_source_ibl`） |
| settle 后帧 | `R145_after_default.png` **`fe7c9a231358b3ce`**（N≥5 门，`gate_tries=8`）；bg `R145_after_bg.png` `d9e77c94add9985b` |
| 五读数（settle 后） | p50 **0.228** / p95 **0.4443** / >0.5 **2.158%** / >0.75 **0.020%** / 暖色 **0.000%**；mask 4.531%（64,492 px）；meanRGB 0.256/0.242/0.270 |
| console | `[]` |
| cube 状态 | `bg61f_light_spherereflectioncapture_1`：**pre-recut（faces/ 内无 `.bak_mangled_*`）**，且取帧前后逐面 sha16 未变（`cube_unchanged=true`）⇒ 本读数与 task-48 同口径（重切前） |

**逐 prim 族号（manifest Fam == runtime Fam，全部 `014`）**
| prim | kind | map | normalMap | roughnessMap | metalnessMap | rough fam | envMode |
|---|---|---|---|---|---|---|---|
| 0 | weapon | `014_b_m.png` | `014_n.png` | `param_repack_014.png` | `param_repack_014.png` | 014 | source_ibl |
| 1 | weapon | `014_b_m.png` | `014_n.png` | `param_repack_014.png` | `param_repack_014.png` | 014 | source_ibl |
| 2 | weapon | `014_b_m.png` | `014_n.png` | `param_repack_014.png` | `param_repack_014.png` | 014 | source_ibl |
| 3 | weapon | `014_b_m.png` | `014_n.png` | `param_repack_014.png` | `param_repack_014.png` | 014 | source_ibl |
| 4 | weapon | `014_b_m.png` | `014_n.png` | `param_repack_014.png` | `param_repack_014.png` | 014 | source_ibl |
| 5 | weapon | `014_b_m.png` | `014_n.png` | `param_repack_014.png` | `param_repack_014.png` | 014 | source_ibl |
| 6 | weapon | `014_b_m.png` | `014_n.png` | `param_repack_014.png` | `param_repack_014.png` | 014 | source_ibl |

**改动前 vs 改动后（同一 mask：改动后 settle 态的 `__primOnly(-1)` 背景，64,492 px）**
| 项 | 改动前 `REG48_1110145.png` `9b05fb131ccf6810` | 改动后 `R145_after_default.png` `fe7c9a231358b3ce` |
|---|---|---|
| 变化像素 | — | **63,800 px = mask 的 98.93%**（几乎整把武器都变了） |
| p50 | 0.2591 | 0.2280 |
| p95 | 0.5427 | 0.4443 |
| 暖色% | 0.000% | 0.000% |
| meanRGB | 0.226 / 0.272 / **0.454**（明显偏蓝） | 0.256 / **0.242** / 0.270（蓝染退去、转中性/金） |

**亲眼看（settle 后帧 `fe7c9a231358b3ce`）**：**像** —— 金/青铜色装甲板 + 紫水晶翼状结构、表面细节与暖色金属高光可见；**无全黑剪影、无白色块**；与改动前那张"通体紫蓝"相比，明显更接近该皮肤的实体配色（与 1110177 修好后的观感同一路径）。

> 注：§4 板页那次记录的徽标分布是**改动前**的（当时 `材质近似`×1 = 1110145）；Lead 已把 1110145 徽标改为 `源数据（候选级）` 且 `media.js` 已变 ⇒ §4 的徽标计数**已过期**，将在 task-49 复测里按新 `media.js` 重新核对（本次未重测板页）。

### 8.2 1110024 IBL 顶替撤销（Lead 变更）+ 立方体面**重切已落地**
| 对象 | 报告出具时 | 现（实测） | 说明 |
|---|---|---|---|
| `1110024/neox_material.json` | `EC2AB0C7A1FC5297` | **`F4EE514FF43745AA`**（34,515 B） | 5 个 prim 的 `t_custom_ibl` 由顶替的 `gdansk_shipyard_buildings.dds` 改回 c159 声明的 `common\env_map\indoor.cube`，`SUBSTITUTION_WARNING` 移除 |
| `data/media/weapon_skin_media.js` | `A1C671238396FC3F` | **`06EFCF4469A8ACD7`**（3,789 B） | 1110024 note 更新后重生成（期间还经历过 1110145 的 `D1A16408CE10FC22`） |
| `data/media/weapon_skin_media.json` | `62417B57BBBFA4F9` | **`07DAA9519A31D98D`**（4,606 B） | 同上 |
| `board.html` | `718202FC4D29F603` | `718202FC4D29F603` | 未变 |
| 其余 6 皮肤 manifest | — | 1110129 `339513A853725477`、1110145 `9C2EDAC7BCD63305`、1110152 `B7F349BA453CB727`、1110165 `DA7CC185997A74C6`、1110171 `3B1BD860774D0BAB`、1110177 `DE07399720411145` | 未变 |

**§8.1 的 1110024 面指纹已被推翻（重切落地）**：`src_cube/faces/` 出现 **10 个 `.bak_mangled_20260918_231623`**（indoor f1–f5 与 gdansk f1–f5），f0 未变；逐面对比：
| 面 | 重切前（§8.1） | 重切后（现） | 变化 |
|---|---|---|---|
| `indoor_f0_m0.png` | `4FA21056199DFB46` | `4FA21056199DFB46` | 未变 |
| `indoor_f1_m0.png` | `11A54A0961F02950` | `0C829DC6C0CC33C2` | 变了 |
| `indoor_f2_m0.png` | `FCA45AFAEC163299` | `5E8CB7AC8D5B0D92` | 变了 |
| `indoor_f3_m0.png` | `93830A3236432CC3` | `A37162D1AD434720` | 变了 |
| `indoor_f4_m0.png` | `7D105582CC618C74` | `970F006412371453` | 变了 |
| `indoor_f5_m0.png` | `27AD0D25EA058ADB` | `999F7325D55D3E34` | 变了 |
| `gdansk_shipyard_buildings_f0_m0.png` | `0E77AD1E968BD1EF` | `0E77AD1E968BD1EF` | 未变 |
| `gdansk_shipyard_buildings_f1_m0.png` | `5025C7C668F53189` | `D1B6C4C68418EB7B` | 变了 |
| `gdansk_shipyard_buildings_f2_m0.png` | `F705BBEF937F4E21` | `D1256EEF4816B8E9` | 变了 |
| `gdansk_shipyard_buildings_f3_m0.png` | `24AD11D0640F50DA` | `6AE59D1E8265A20D` | 变了 |
| `gdansk_shipyard_buildings_f4_m0.png` | `C9FA11658EBC3D26` | `9BF99AF66516F464` | 变了 |
| `gdansk_shipyard_buildings_f5_m0.png` | `CFB4668566A6D00D` | `AA4B5FE203998C5A` | 变了 |

> **限定**：task-48 摘要表里 1110024 的 **PASS 是"改动前 + 重切前"**的读数，本报告**未追溯修改**；改后基线见 §10。Lead 亦已更正：当初"保留 gdansk"所依据的 A/B（indoor 32.7/46.8 vs gdansk 35.8/113.2）是在**两组面 PNG 都错切**的前提下做的 ⇒ **该比较无效**，须在重切后重跑 —— §10 即重切后的读数。

## 10. 1110024 改后基线（**IBL 改回声明值 + 立方体重切后**；单皮肤 1 次载入、settle 判据取帧、亲看）
| 项 | 读数 |
|---|---|
| pin（实测） | manifest **`F4EE514FF43745AA`** ✅ / `media.js` **`06EFCF4469A8ACD7`** ✅ / `media.json` `07DAA9519A31D98D` / viewer.js `3357CD87518C6E8A` / adapter `1CD4AC5454D1F27A` / board `718202FC4D29F603` |
| `__neox()` | `applied=5`、`applied_prims=[0..4]`、`failed=[]`、`missing=[]` ⇒ `applied == expected_prims` **5/5** ✅ |
| `mat_visible` | **5/5 true** ✅ |
| 逐 prim 族号 | 5 个 prim（全 `pbr_weapon`）：`map=024_b_m.png`、`normalMap=024_n.png`、`roughnessMap/metalnessMap=param_repack_024.png`，`fam_*` 全 **`024`** ✅ |
| settle 判据 | **`all_green_ms = 0`**（首个采样即全 `source_ibl`；无窗口） |
| settle 后帧 | `R124_after_default.png` **`4785b69195428b9b`**（N≥5 门，`gate_tries=5`）；bg `R124_after_bg.png` `d9e77c94add9985b` |
| 五读数 | p50 **0.4239** / p95 **0.7731** / >0.5 **16.762%** / >0.75 **5.337%** / 暖色 **3.635%**；mask 3.678%（52,356 px）；meanRGB 0.438/0.407/0.370 |
| console | `[]` |
| cube 状态 | **post-recut**（`faces/` 内有 `.bak_mangled_20260918_231623`），取帧前后逐面 sha16 未变（`cube_unchanged=true`）⇒ 本次读数 = **重切后** |

**改动前 vs 改动后（同一 mask：改后 settle 态的 `__primOnly(-1)` 背景，52,356 px）**
| 项 | 改前 `REG48_1110024.png` `d11f9b58fd15b07f`（旧 IBL + 错切面） | 改后 `R124_after_default.png` `4785b69195428b9b`（声明 cube + 重切面） |
|---|---|---|
| 变化像素 | — | **43,409 px = mask 的 82.91%** |
| p50 | 0.4548 | 0.4239 |
| p95 | **0.9529** | **0.7731** |
| >0.5 | — | 16.762% |
| >0.75 | — | 5.337% |
| 暖色% | **8.030%** | **3.635%** |
| meanRGB | 0.503 / 0.497 / 0.475 | 0.438 / 0.407 / 0.370 |

**⚠ 归因更正（见 §11）**：`faces_glob` 仍指 gdansk ⇒ **运行期实际加载的始终是 gdansk 面，IBL 改回声明值是空操作**；因此本节的 82.91% 变化**应归因于"立方体面重切"**，**不是** IBL 目标切换。原文的"同时变了两件事"表述在此更正为"实际只变了一件"；再加上你自己指出的"旧 A/B 无效"，本轮**只能**得出"重切后、声明 cube 下的改后基线"。若要把 IBL 目标单独判掉，需要**重切后的 indoor vs gdansk 同会话 A/B**（我可按 task-42 的 Fetch 拦截法做，等你指令）。

**亲眼看（`4785b69195428b9b`）**：**像那把武器** —— 青铜/棕色哑光装甲枪剑，装甲板与面板线清楚、有柔和高光；**无全黑剪影、无白色块**；与改前那张"亮银金"相比**高光收敛（p95 0.953→0.773、暖色 8.0%→3.6%）**，但仍保有色相与层次。

> 注：`REGRESSION_1110024_after.json` 首次生成时 `pins_*` 沿用了我 1110145 脚本的路径 ⇒ 字段 `m1110024` 被贴错标签（实际是 1110145 的 manifest）；已用只读哈希重读并覆盖为真实 pin，并在该 JSON 里留 `pin_fix_note` 记录此更正。

## 11. 1110024「重切后」cube 内容 A/B：**声明值 indoor 比 gdansk 差得多**（且发现 IBL 改回**当前无效**）
### 11.1 机制发现（先决问题）：`faces_glob` 过期 ⇒ 运行期仍加载 gdansk 面
- manifest（现 `F4EE514FF43745AA`）5 个 prim 的 `t_custom_ibl`：`logical_path=common\env_map\indoor.cube`、`local_file=src_cube/indoor.dds` ——**但**
  - **`faces_glob = src_cube/faces/gdansk_shipyard_buildings_f{i}_m0.png`**（仍指 gdansk）；
  - **`sha256 = 3c838953a5db91c1…` = `gdansk_shipyard_buildings.dds` 的哈希**（`indoor.dds` 实为 `A464190B0FEBB360…`，与 Lead 的容器证据一致）；
  - `face_sha16` 的 6 个值**与盘上任何一组面都不匹配**（重切后/重切前、indoor/gdansk 交集均为 0）。
- viewer 的 cube 装载（`viewer.js` L1191-1198）**优先使用 `faces_glob`** ⇒ 网络侧实测请求的就是 **`faces/gdansk_shipyard_buildings_f0..f5_m0.png`**（group A `continued_faces` 6/6），而 `__texReady().gate` 的名字却是 **`indoor`**。
- ⇒ **Lead 这次的 IBL 改回声明值在视觉上是"空操作"**（面仍是 gdansk 内容）；**§10 那次 82.91% 的像素变化应归因于"面重切"，不是 IBL 目标切换** —— §10 的表述在此更正。

### 11.2 A/B（同会话、同布局、稳定性门 N≥5；只换 cube **内容**，两组都用当前重切面）
| 组 | 做法 | 帧 sha16 | mask% | p50 | p95 | >0.5% | >0.75% | 暖色% | meanRGB |
|---|---|---|---|---|---|---|---|---|---|
| **A**（现状=gdansk 内容） | 不拦截 | **`c336d323330c1166`** | 4.368 | **0.4262** | **0.7866** | **16.968** | **5.616** | **3.775** | 0.441/0.410/0.372 |
| **B**（=声明 indoor 内容） | 拦截 `faces/gdansk_*_f*_m0.png` 的 6 个请求，按字节返回 `faces/indoor_*_f*_m0.png` | **`3d325719d47f306c`** | 3.816 | **0.0246** | **0.1292** | **0.031** | **0.000** | **0.000** | 0.043/0.037/0.033 |
- B 组拦截**实测生效 6/6**；两组 A↔B 在 mask 内 **97.2% 像素不同**；面文件在整轮前后 sha16 未变（`faces_unchanged=true`）。
- **判定**：**声明值 `indoor` 的内容在该 viewer 链下近乎全黑**（p50 0.0246 / p95 0.1292 / 暖色 0%），**明显差于 gdansk**（p50 0.4262 / p95 0.7866 / 暖色 3.775%）。这与 Lead 当初"保留 gdansk"的**观感**方向一致 —— 但请注意：**那次 A/B 因两组面都错切而无效，本次是重切后的有效比较**。
- **机制线索**：`indoor` 六面中 **恰好 1 面全黑**（`indoor_f3` meanL=0.0），其余面 0.36–0.77；而 `gdansk` 六面 0.79–0.84 且均匀。**重切前**的 indoor 组也有 1 面全黑（在 f4）⇒ **黑面是内容固有、不是重切新引入**；但重切把黑面从 f4 挪到 f3（f2/f3/f4 亮度互换了）⇒ 若后续要判定"indoor 是否真的这么暗"，需先确认重切的**面序**正确（我的数据无法验证面序，标 unresolved）。
- **结论只适用 1110024**，不外推到其它皮肤。**我没有改任何文件**；是否回退到 gdansk（或修 `faces_glob`/`sha256`/`face_sha16` 后再判）等你裁决。

## 12. 1110177 `viewer.json` effects v3（`2A9ED75C7B4F663B`）复核
| 检查 | 结果 |
|---|---|
| pin | `1110177/viewer.json` = **`2A9ED75C7B4F663B`** ✅（Lead 值）；`1110177` manifest `DE07399720411145` ✅；viewer.js `3357CD87518C6E8A` / adapter `1CD4AC5454D1F27A` / board `718202FC4D29F603` / media.js `06EFCF4469A8ACD7` 均未变 |
| viewer.json 差异范围 | 与备份 `.bak_fxwire_20260918_232142` 逐键比对：**8,553 个差异键全部位于 `/effects` 下**（非 effects 差异 **0 条**）⇒ Lead 所述"只换 effects"**成立** |
| SFX 按钮 | `{text:"SFX 关闭", disabled:false, title:"切换实时特效"}` ⇒ 由"未提供"变为**可用且默认关闭** ✅（与 Lead 预测一致） |
| console | **3 条**，全部是**既有** `1110177/src_tex/gpk_1229.png` 404（task-46 待清）；**没有**来自 302 KB 内联 effects 清单的解析错误 ✅ |
| `__neox()` | `applied=3`、`applied_prims=[0,1,2]`、`failed=[]`、`missing=[]` ✅ |
| **默认帧** | 本次 **`6541c6c945520e31`**（N≥5，`gate_tries=5`，`rect_unchanged=true`）—— **不等于** Lead 给的 `2b48eeebb26d24bd`，也**不等于**我 task-48 的 `9a0243b928a0291a`；settle 判据 `all_green_ms=0`（无 IBL 空窗） |
| 帧差性质 | 以本次 bg 为 mask：mask bbox `x[542,1023] y[293,655]`，**diff∩mask 的 bbox 完全相同**（几何未变）；**mask 内 97.4% 像素不同**、武器区 **p50 0.1577→0.2829**（变亮）、p95 0.5516→0.5745；mask 外另有 342,406 px 差异（UI 区域） |

- **如实标注 unresolved**：默认帧 sha 变化**未能完全归因**。已知：(a) `viewer.json` 只改了 `effects`；(b) 本次 settle=0 ms（无空窗）；(c) 几何未变而武器区变亮。两个待验假设：① task-48 那一帧可能取在**加载/构建未完全稳定**时点（当时没有 settle 判据，且该皮肤 gate 曾 `deferred_retries=2`）；② 新 `effects`（`status:'partial'` + 可用按钮）触发了某个默认渲染路径差异。**建议**：如需坐实，可加一轮"同会话内 t≈1 s / t≈3 s / 全绿后"三点取帧（我可随时做，约 1 分钟）。

## 13. 1110024 一致性修复后的复核（manifest **`1F7E17F261D7F834`**）—— PASS
| 检查 | 结果 |
|---|---|
| pin | `1110024/neox_material.json` = **`1F7E17F261D7F834`** ✅；viewer.js `3357CD87518C6E8A` / adapter `1CD4AC5454D1F27A` / board `718202FC4D29F603` / media.js `06EFCF4469A8ACD7` 未变 |
| 网络侧 faces | 实测请求 = `gdansk_shipyard_buildings.dds` + **`gdansk_shipyard_buildings_f0..f5_m0.png`（6 面）** ✅ |
| `__texReady().gate` | `cube = "gdansk_shipyard_buildings"`、`faces_loaded 6/6`、`ready:true` ✅ ⇒ **名字与 `faces_glob` 现在一致**（修复前是"名字 indoor / 内容 gdansk"的分裂） |
| settle | **`all_green_ms = 0`**（无窗口）；`open_ms` 754 |
| 默认帧 | **`c336d323330c1166`** —— 与 §11 的 A 组（修复前、同样加载 gdansk 内容）**逐字节相同** ✅ ⇒ 说明本次只是"清单内部一致性修复"，渲染**符合预期地未变** |
| 五读数 | p50 **0.4262** / p95 **0.7866** / >0.5 **16.968%** / >0.75 **5.616%** / 暖色 **3.775%**（与 §11 A 组完全一致） |

⇒ 你的修复目标（faces 请求 = gdansk、gate 名与 faces_glob 一致、默认帧回到与 gdansk 内容相符的读数）**三条全部达成**；`indoor` 的可用性仍按你的安排留待用户裁决（我这边不做判断）。

## 14. 1110177 三点取帧：**task-48 那帧是"早期态"，`6541c6c9…` 是稳定态**
方法：同一会话；`open()` 返回后 t≈3.7 s 先取**单帧**（未过门）；随后三点各自过 **N≥5 门**（三点分别开始于 17.7 s / 33.9 s / 52.8 s）。settle 判据 `all_green_ms = 0`；`open_ms = 709`。
| 取帧点 | 帧 sha16 | mask% | p50 | p95 | >0.5% | >0.75% | 暖色% | meanRGB |
|---|---|---|---|---|---|---|---|---|
| 早期单帧（t≈3.7 s，未过门） | `5c5e774641ddcead` | **16.206** | **0.1395** | **0.7687** | 13.494 | 5.476 | 1.306 | 0.199/0.248/0.255 |
| t1 门控（开始 17.7 s） | **`e62c1c58e5bdc383`** | 1.826 | **0.2829** | 0.5745 | 18.242 | 0.989 | 0.689 | 0.322/0.299/0.279 |
| t3 门控（开始 33.9 s） | **`e62c1c58e5bdc383`** | 1.826 | 0.2829 | 0.5745 | 18.242 | 0.989 | 0.689 | 同左 |
| settle 后门控（开始 52.8 s） | **`e62c1c58e5bdc383`** | 1.826 | 0.2829 | 0.5745 | 18.242 | 0.989 | 0.689 | 同左 |
| （对照）task-48 帧 `REG48_1110177.png` `9a0243b928a0291a` | — | 16.204 | **0.1394** | 0.7679 | 13.431 | 5.455 | 1.306 | 0.199/0.247/0.254 |

**判定（回答 Lead 的问题）**：
1. **三点（17.7 / 33.9 / 52.8 s）帧完全相同** ⇒ 1110177 的默认帧在**一次载入内自 ~17 s 起就稳定**，没有 settle 前后的漂移。
2. **task-48 的 `9a0243b928a0291a` 是"早期态"**：其五读数与本轮 t≈3.7 s 单帧几乎逐项相同（p50 0.1394↔0.1395、p95 0.7679↔0.7687、>0.5 13.43↔13.49、暖色 1.306↔1.306）⇒ **task-48 那次捕捉到的是"材质/纹理未完全稳定"的阶段**（当时协议没有 settle 判据；该皮肤 gate 曾 `deferred_retries=2`）。**因此 `9a0243b928a0291a`（我 task-48 的值）不能当 1110177 的默认基线。**
3. **`6541c6c945520e31` 不是"settle 前中间态"，而是"稳定态"**：它与本轮稳定帧**五读数完全相同**（p50 0.2829 / p95 0.5745 / >0.5 18.242 / >0.75 0.989 / 暖色 0.689），只是**跨载入的逐字节 sha 会变**（同一协议的两次独立载入：`6541c6c9…` vs `e62c1c58…`，读数一致）—— 与我早先记录的"门只保证载入内稳定、不保证跨载入逐字节一致"完全吻合。
4. **1110177 基线结论（status = `baseline_under_investigation`，待你确认后转正）**：
   - **不要用任何单一 sha 当基线**（含你给的 `2b48eeebb26d24bd`）；建议改用**settle 后门控的五读数**：`p50 0.2829 / p95 0.5745 / >0.5 18.242% / >0.75 0.989% / 暖色 0.689%`（两次独立会话复现一致），帧 sha 只作为"该次载入的指纹"记录；
   - 若你需要逐字节基线，我可以补一轮"3 次独立载入各取 settle 后门控帧"给你分布（约 2 分钟）。

## 15. 板页徽标复验（新 `media.js` `06EFCF4469A8ACD7`）
| 检查 | 结果 |
|---|---|
| 卡数 / 骨骼 id | **115** 卡 / **37** 个骨骼 id ✅ |
| 徽标总数 | **8**（`.skin-media-fidelity`） |
| 徽标取值 | **`源数据（候选级）`×7**（极光剑/光影咏叹调/墨隐麒麟/灵态诱导/**天马行空(1110145)**/熔炉寒霜/金蟒啸焰）+ **`未建（无材质链）`×1**（灰色协议 1110169）⇒ **1110145 已由 `材质近似` 变为 `源数据（候选级）`** ✅（你脚本 bug 修复的连带效果已生效） |
| 原始英文键 / 空 title | **0 / 0** ✅ |
| 评级筛选 | 勾选 → **19** 卡；清除 → **115** 卡 ✅ |
| console | 仅 1110177 的既有 `gpk_1229.png` 404（其余为空）✅ |

## 16. 用户"只闪一下 / 一大块 / 很劣质"取证（只读；两组都测）
### 16.1 量出来的事实
| 项 | **1110177**（新接线） | **1110171**（更早做的） |
|---|---|---|
| `__probe()` 精灵（SFX 开） | 3 个：`M_g_glow_an` opacity 0.0019 / **scale 6**；`H_g_glow地_an` **visible=true** opacity 0.016 / **scale 13**；**`H_公告板_爆闪2` opacity 0.0074 / scale 50** | 4 个：`M_g_光晕暗_01` 0.0388 / scale 6；`M_g_光晕亮_01` 0.0311 / scale 5.75；`M_g_光晕暗_02` 0.0618 / scale 6（采样瞬间 visible 均为 false） |
| 特效层包围盒 / 武器包围盒 | sfx `size [50, 50, 0]` diag **70.71**；武器 diag **15.46** ⇒ **4.58 ×** | sfx `size [6, 6, 0]` diag **8.49**；武器 diag **6.88** ⇒ **1.23 ×** |
| 贴图（全部特效对象） | **只有一张**：`glow_01__13211b02.png` ×3 | 两张：`c63f1436228725ad.png` ×2、`3eb4edfb85276f07.png` ×2 |
| 固定时间扫描（25 ms 步进，源时间） | 活动窗口 **t = 1.150 → 1.200 s（≈75 ms）**，峰值 **32.73% 画布**（465,892 px）@ t=1.175 s；其余 46/49 步为 0 | 活动窗口 **t = 0.175 → 0.825 s（≈675 ms）**，峰值 **0.81% 画布**（11,544 px）@ t=0.55 s |
| 峰值帧 sha16 | `09326543546759bf`（`SWP_1110177_t1175.png`） | `1f369d40d0b37bec`（`SWP_1110171_t550.png`） |
| 峰值帧颜色/亮度 | meanL **0.30**、meanRGB 0.243/0.339/0.315（青绿）、diff bbox 覆盖 x[458,1122] y[122,839]（≈664×717 px） | meanL 0.2417、meanRGB 0.143/0.263/0.319（青蓝）、diff bbox x[450,892] y[270,711]（≈443×441 px） |
| 墙钟突发采样（80 ms 名义、实测 0.65 s/0.97 s 间隔，30 帧） | 30 帧里仅 **2 帧**有 >500px 变化（t=15.13 s 30.23%、t=18.99 s 27.08%） | 30 帧里 **11 帧**有变化（最大 0.81%） |
| 默认态（SFX 关） | 默认帧 `8352c4e30bbaf981`；五读数 p50 0.2829 / p95 0.5745 / >0.5 18.242% / >0.75 0.989% / 暖色 0.689%（与前几轮**一致**）；且与**上一会话**的默认帧**逐字节相同**（`changed_px=0`）⇒ **默认渲染未受 effects 变更影响** | 默认帧 `13c8c5ce35bb869e`/`48b6c95c1165c80a`（跨载入不同）；五读数 p50 **0.1232** / p95 **0.4865** / >0.5 3.394% / >0.75 0.273% / 暖色 0.106%（与我早先 0.127/0.485 同档） |
| console | 仅既有 `1110177/src_tex/gpk_1229.png` 404 | 同（跨页共享） |

### 16.2 一句话结论（按 Lead 要求的口径）
**用户看到的那一下 = 1110177 的公告板类节点 `H_公告板_爆闪2`（`scale=50`，武器对角线约 15.46 ⇒ 约为武器的 3.2×；连同 `H_g_glow地_an` scale=13 一起把特效层包围盒推到武器的 4.58×），用唯一一张 `glow_01__13211b02.png`（`content_candidate`），在**源时间 t≈1.15–1.20 s 的约 75 ms 窗口**内出现，峰值覆盖画布 **32.7%**、呈青绿色低透明度大片**；其余时间（46/49 步）画面无变化 ⇒ 既"只闪一下"又"一大块"，且只有一张贴图、无精灵表切片/无缩放动画 ⇒ 观感平板"劣质"。**
**1110171 同法测得的不是"一大块"**：3–4 个 `scale≈6` 的光晕，活动窗口 175–825 ms、峰值仅 0.81% 画布（1.23× 武器）。

### 16.3 取证口径与限制（如实）
1. **viewer.js 在本次取证期间被改动过**：`pins_start=3357CD87518C6E8A` → 过程中 `D802153DA05E5DF3` → `pins_end=7108D8CE85DE4F06`（task-49 进行中）。因此：`__probe()` 与默认帧那批读数对应 `D802153D…` 附近版本，**固定时间扫描的 1110177/1110171 两轮可能处于不同 viewer 版本**；`adapter` 全程 `1CD4AC5454D1F27A`、`v1110177=C59DD70479217BFE`、`m1110177=DE07399720411145`、`m1110171=3B1BD860774D0BAB`、board `718202FC4D29F603` 未变。
2. 固定时间扫描里每步的**对象级探针**因我的注入脚本在导航后失效而返回 `err:'Cannot read properties of undefined'`（**仅探针失效，截图/像素差有效**）；几何/贴图数据取自点击后立刻读取的 `__probe()` + `THREE.Box3`。**下一轮（viewer 冻结后）我会把注入改为每次导航后重打，补齐逐步对象读数。**
3. 25 ms 是**源时间**分辨率（`__sfxTime(t)` 固定时间，非墙钟）；墙钟采样受截图耗时限制只能到 ~0.65–0.97 s/帧，故"只闪一下"的毫秒级判定用源时间扫描给出。
4. 两张峰值截图我已**亲眼**看过：1110177 的 `SWP_1110177_t1175.png` 是**整屏泛起的青绿色大片**（房间与武器均被罩住、无明显边界），符合"一大块"；1110171 的 `SWP_1110171_t550.png` 只是武器附近的**小片青蓝光晕**。**结论仅对这两把皮肤成立、不外推。**（`SWP_1110177_t1175.png` sha16 `09326543546759bf`；`SWP_1110171_t550.png` sha16 `1f369d40d0b37bec`。）

## 17. 同口径对照（MASK vs CANVAS）与 1110177 SFX 改前基线
- 判据定义：`MASK_CRITERION.md`；读数与对照：`CRITERION_BASELINE_20260919.md`；原始数据：`REGRESSION_criterion_baseline.json`。
- **两口径同表**：1110171 MASK `0.1232 / 0.4865 / 3.394% / 0.273% / 0.106%`（mask 2.449%）vs CANVAS `0.1568 / 0.3008 / 1.899% / 0.776% / 0.180%`；1110177 MASK `0.2829 / 0.5745 / 18.242% / 0.989% / 0.689%`（mask 1.826%）vs CANVAS `0.1587 / 0.3056 / 2.149% / 0.787% / 0.190%` ⇒ 分位数不可跨口径换算、占比可按 mask_pct 换算。
- **稳定门序列**：1110171 `e5df2f713b260180` → `48b6c95c1165c80a`×9（第 2 帧起稳定）；1110177 `3a6f3bd4a4147c59`×10 ⇒ 首帧瞬态存在，N≥5 门自动跳过。
- **1110177 SFX 改前基线**：峰值 t=1.175 s（窗口 1.150–1.200 s ≈75 ms）、帧 `09326543546759bf`、effect-only 38.08% 画布、alive=3、quad 6×6/13×13/50×50（层 4.58× 武器）、仅 1 张贴图、**6 个 ParticleSystem 全部未渲染**。
