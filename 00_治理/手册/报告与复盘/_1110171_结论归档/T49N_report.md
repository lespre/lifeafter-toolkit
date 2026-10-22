# T49N 报告（task-49 收尾轮 · 报告补交）

报告者：shader-auditor ｜ 生成时刻：2026-09-19 15:4x ｜ **本文件为报告，未再改代码、未起浏览器**

> ⚠ **本轮运行的控制台输出丢失**：`job_output(wait)` 调用被中断（"no result was durably recorded"），
> 因此 `seq5/stable5`、`applied/failed/missing`、`manifest_fams==runtime_fams`、`__perfStages()`、
> `exceptionDetails` **均未取到**。以下凡标 **【产物推算】** 的是我用磁盘上的 21 张 PNG 离线计算；
> 标 **【未取到】** 的需要一次短测量（约 3–4 分钟）才能补。

---

## 1. 我改了什么（viewer.js）

**改前 sha16 `3B9999B992FE8763`（330,804 B）→ 改后 `A3EBD64FF57F32DE`（332,019 B，mtime 15:40:33）**
**备份（已 `copy2`）**：`%TEMP%\wsv_bak_task49j_20260919_154024.js` = **`3B9999B992FE8763`**（另有更早的 `wsv_bak_task49i_20260919_000437.js` = `9FFC8BC18E516277`）

**逐处改动（1 处，`__neoxLiveEnv()` 内，行号按改后文件近似）**
| 位置 | 原文 | 新文 |
|---|---|---|
| L~3188 `byPrim[c.prim]={...}` | `…radiance_bound:hasCustom, faces_loaded:faces};` | 追加 **`pending_hidden:!!m.userData.__pendingHidden`**（live 读取，供下面现算） |
| L~3200 返回处 | `return Object.assign({}, rep, {missing:miss, env_warn:…, env_live:{…}});` | 前置 **`var primsLive=(rep.prims||[]).map(function(p){var L=byPrim[p.prim];return (L?Object.assign({},p,{pending_hidden:!!L.pending_hidden}):p);});`**，返回体改为 **`{prims:primsLive, missing:miss, env_warn:…, pending_hidden_source:'read_time', env_live:{…}}`**（**不改 `state.neoxReport` 本体**） |
含义：`__neox().report.prims[*].pending_hidden` 由"建材质时刻快照"改为 **read-time 口径**，与 `__texReady().pending_hidden_total` / `__acceptanceReport().pending_hidden_total` 同源（都读 live `userData.__pendingHidden`），并新增 `pending_hidden_source:'read_time'` 标口径。

## 2. `pending_hidden` 三源一致性

- **【未取到】**（需短测量）。但**修法本身即消除机制**：三源现在都按 live 取值；旧的"report=2 vs live=0"来源是"旧报告晚到覆盖 `state.neoxReport`"（已在 `env_warn` 上实测过同一机制），本次改动后该路径不再影响 `pending_hidden`。
- 待补读数：同一时刻打印 `report.prims[*].pending_hidden`、`__texReady().pending_hidden_total`、`__acceptanceReport().pending_hidden_total` + `pending_hidden_source`。

## 3. 双侧锚点（N≥5）

- **【产物推算】settle 帧 sha16（= converge 后保存的那一帧）**
| 皮肤 | settle sha16 | 备注 |
|---|---|---|
| 1110024 | `81328C8267F7211B` | |
| 1110129 | `954DC1EB9748B315` | |
| 1110145 | `52AC39FBD0072CC9` | |
| 1110152 | `02A21F72F3264C87` | |
| 1110165 | `834E01E6C0C75B0C` | |
| **1110171** | **`9B08A1134BFC484E`** | **= 此前已接受的 MASK 锚点 `9b08a1134bfc484e` ⇒ 未变 ✓** |
| **1110177** | **`EA57DCC8B8537107`** | **已变**：`viewer.json(1110177)` 现为 `4BB4D668D043B722`（内联 task-58 粒子字段）⇒ **数据侧变化，锚点应改为 `ea57dcc8b8537107`** |
- **【未取到】**：`seq5`（N=5 逐帧序列）与 `stable5` 标志；**【未取到】** 冷/热两态（磁盘上**没有 `_warm` 产物** ⇒ 热档未执行）。

## 4. 7 皮肤回归

- **【产物推算】7 个皮肤都产出了 settle 帧且掩模非空**（`mask_pct` 2.449–5.773%）⇒ **7/7 都渲染出可见武器**（非白块/非黑屏）；窗口帧也 7/7 存在。
- **【未取到】**：`applied == manifest prim 数`（5/5、5/5、7/7、2/2、4/4、7/7、3/7? ⇒ 应为 3/3）、`failed/missing` 空、**`manifest_fams == runtime_fams`** —— 这些是脚本的控制台输出，随中断丢失。

## 5. `__perfStages()` / `all_green`

- **【未取到】**（同上）。参考：上一版（含 sha 缓存、无本轮改动）曾测得 **首轮 14 miss（`sha_ms` 418）→ 次轮 51 hit（仅 HEAD 校验）**，`all_green` 一次为 **4089 ms**；本轮未复测。

## 6. 亲眼描述（本轮**已看 2 张**，均 1578×902）

- **窗口帧 `T49N_1110171_window.png`（`72F9AE743F28E7F6`）**：【亲看】武器**仍有明显扁平白块**——刃/晶体区是一片**没有明暗结构、没有刻面的纯白/浅灰平面**，机身深色部分正常；与改前窗口帧（`3c2249e56afa3638`，p50 1.000 整片白）相比**白块面积与亮度大幅下降**（离线统计 p50 **0.1301**、`>0.5` 13.325%、暖色 1.940%），但**白块并未完全消失**。⇒ **判定：部分修复，未根除**（原因待查：`pendingHide` 只在"建材质时 `envMode==='ibl_pending'`"的 prim 上生效，晚一轮重建出来的 prim、或"门已 ready 但 IBL 注入尚未生效"的 prim 仍会以白底绘制）。
- **settle 帧 `T49N_1110171_settle.png`（`9B08A1134BFC484E`）**：【亲看】武器为**深青铜/钢色机身 + 浅蓝白晶体刃**，刃面**有明暗结构与刻面**，**无扁平白块**，面板已隐藏（`__hidePanels(true)`）⇒ 与锚点一致、画面正常 ✓。
- 其余 5 皮肤的 window/settle 帧**未亲看**（预算），仅给出 sha16 与离线统计。

## 7. `exceptionDetails`

- **【未取到】**（脚本会把 `EXC ...` 打进控制台，随中断丢失）。
- **【产物异常，可用于定位中断点】**：`T49N_1110177_bg.png`（774,322 B）**损坏**（PIL 报 `UnidentifiedImageError`）⇒ 写入被截断；结合"**无 `_warm` 产物**"可判定：**运行在最后一个皮肤（1110177）之后/期间被掐断**，热档与所有回归/一致性打印**从未执行**。

---

## 8. 结论与请求

- **代码侧**：`pending_hidden` 三源改成同源（read-time）已落地并 `node --check` 通过；锚点侧 **1110171 稳定不变**，**1110177 因数据侧更新应换锚**（`ea57dcc8b8537107`）。
- **测量侧缺 6 项读数**（第 2/4/5/7 项 + seq5 + 冷热），原因是一次运行被中断。
- **请求（请裁）**：给我一次 **约 4 分钟** 的浏览器窗口，我重跑 `%TEMP%\t49_next.py` 即可补齐全部缺失读数（脚本已在盘上、无需改代码）；或明确接受"以产物推算为准、缺项标未取到"，我即按此收尾。
- **另需登记的观察**：窗口帧**白块只是减小、未消失**（§6）⇒ `pendingHide` 的覆盖条件需要扩大到"任何 `envMode!=='source_ibl'` 的 prim（含门已 ready 但注入未生效者）"，或配合 task-54/47 的"`ibl_pending` ⇒ metalness=0"一起解决。这条应作为**下一轮修法的输入**。

---

## 9. Lead 裁决与下一轮计划（2026-09-19，追加；本轮未改代码、未起浏览器）

**裁决 ①（采纳并升级 §8 观察为主任务）**：**批准把 `pendingHide` 扩到"任何 `envMode !== 'source_ibl'` 的 prim 暂不提交渲染"**。附加三条（不可协商）：
1. **安全阀**：`retry` 收敛 **或** `retry_exhausted` ⇒ **必须恢复可见**（绝不永久消失）；
2. `pending_hidden` 与 fail-closed 的 hidden **分列**，并**保持三源一致**（沿用本轮落地的 read-time 口径：三源同源于 live `userData.__pendingHidden`）；
3. **settle 帧逐字节一致**：1110171 = `9b08a1134bfc484e`、1110177 = `ea57dcc8b8537107`；窗口帧需给"不再是扁平白块"的读数（p50 / `>0.5` / 暖色）+ **亲眼描述**。

**裁决 ②**：因运行中断造成的缺项**不必编造**（标"未取到"已被接受）；核准一次 **约 4 分钟**浏览器窗口，**排在 chain-auditor 的 SFX `colorOrder`/帧序列 A/B 之后**，收到 **GO** 才动。

**下一轮一次做完（收到 GO 后）**
1. 落地裁决 ①（**先 `copy2` 备份 + `node --check` + 报新 sha16**）；
2. 补齐本轮缺的直接读数：`pending_hidden` 三源一致性 · 双侧锚点 `seq5/stable5` · 7 皮肤回归（`applied == manifest prim 数` = 5/5、5/5、7/7、2/2、4/4、7/7、3/3 + `failed/missing` 空 + `manifest_fams == runtime_fams`）· `__perfStages()` **首轮 miss / 次轮 hit** · `all_green` **冷/热 + 负载标注** · `exceptionDetails` 逐条；
3. **亲眼看**窗口帧（改前 `3c2249e56afa3638` / 改后各一张）与 settle 帧，如实写"白块是否消失"。

**冻结 pin（本轮未变更）**：`viewer.js A3EBD64FF57F32DE` · `viewer.json(1110177) 4BB4D668D043B722` · `viewer.json(1110171) 62E7BDDC9CF6EC6D` · `effects.json(1110177) C4C16E2765D18A54` · adapter `13331424C3CB4FE4` · board `B89F7E79AD7E7094`。
**脚本就绪（盘上、未运行）**：`%TEMP%\t49_next.py`（`py_compile` 通过；冷/热 + 7 皮肤 + 三源一致性 + `__perfStages()` + 窗口/settle 帧 + 负载标注）。

---

## 10. GO 轮实测结果（2026-09-19；`viewer.js A3EBD64FF57F32DE → 4F5630461B1EFAC1`）

**改动（1 处）**：`pendingHide` 覆盖条件 `envMode==='ibl_pending'` → **`envMode!=='source_ibl'`**（含"门 ready 但注入未生效"/`missing_source_ibl`），保留安全阀（收敛或 `retry_exhausted` ⇒ 恢复可见）。备份 `%TEMP%\wsv_bak_task49k_20260919_155049.js` = **`A3EBD64FF57F32DE`**；`node --check` 通过；**新 sha16 `4F5630461B1EFAC1`**（332,818 B）。
**负载标注**：`LOAD_START headless=0 cpu_top=HipsDaemon:185,Hermes:128,python:59` → `LOAD_END headless=0 cpu_top=HipsDaemon:187,Hermes:132,python:64` ⇒ **无并发浏览器**。
**清理**：`LEFT_MINE=0`、`PORTS=0,0,0,0,0,0,0,0`。

| 皮肤 | applied | failed/missing/env_warn | N=5 stable | **anchor_sha** | `all_green` | fam_ok | 三源 pending |
|---|---|---|---|---|---|---|---|
| 1110024 | 5/5 | 0/0/0 | ✓ | `81328c8267f7211b` | 1831 ms | ✓ | `neox=[] acc=[] acc_total=0 tex_total=0` |
| 1110129 | 5/5 | 0/0/0 | ✓ | `954dc1eb9748b315` | 1894 ms | ✓ | 同上 |
| 1110145 | 7/7 | 0/0/0 | ✓ | `52ac39fbd0072cc9` | 2189 ms | ✓ | 同上 |
| 1110152 | 2/2 | 0/0/0 | ✓ | `02a21f72f3264c87` | 1626 ms | ✓ | 同上 |
| 1110165 | 4/4 | 0/0/0 | ✓ | `834e01e6c0c75b0c` | 2377 ms | ✓ | 同上 |
| **1110171** | **7/7** | 0/0/0 | ✓ | **`9b08a1134bfc484e`（= 指定锚点，逐字节一致 ✓）** | 3691 ms | ✓ | 同上 |
| **1110177** | **3/3** | 0/0/0 | ✓ | **`49c6f3adcaea235b`**（本版 `viewer.json 0A3E13DBF3003CD5` 下的锚；上一版 `4BB4D668…` 时为 `ea57dcc8b8537107`） | 1821 ms | ✓ | 同上 |
| 1110171 WARM | — | — | ✓ | `9b08a1134bfc484e` | 3174 ms | — | — |

- **`manifest_fams == runtime_fams`：7/7 `fam_ok=True`** ✓；`errs=[]` / `renderErr=''` / **无 `EXC`（exceptionDetails 0 条）** ✓。
- **三源 `pending_hidden` 一致性**：7 皮肤在 settle 全部 `neox=[] / acc=[] / acc_total=0 / tex_total=0` ⇒ **此前 1110171 的 WARN（report=2 vs live=0）已消除** ✓；`retry=1–2/6`、`lastmiss=0`、`exhausted=False`、`pendinghide=on`、`bad=[]`。
- **`__perfStages()`（首轮 miss → 次轮 hit）**：1110024 `4→46` · 1110129 `16→32` · 1110145 `5→79` · 1110152 `7→13` · 1110165 `11→37` · 1110171 `14→86` · 1110177 `12→48`；`sha_ms` 14–434 ms；`head_checks == hits` ⇒ **首轮全 miss（真 fetch+digest）、次轮全 hit，校验从不跳过** ✓。
- **settle 五读数（`criterion=mask/weapon_box`）**：1110171 `mask_pct 2.449 / p50 0.1232 / p95 0.4865 / >0.5 3.394 / >0.75 0.273 / 暖色 0.106`（与改前逐位相同 ⇒ **settle 未变** ✓）；1110177 `1.826 / 0.2829 / 0.5745 / 18.242 / 0.989 / 0.689`（= chain-auditor 参考值逐位相同 ✓）。
- **③ 改后窗口帧：未取到（如实）**：本脚本窗口抓取是 best-effort 且要求 `bad` 非空，而本轮收敛极快（`all_green` 1.6–3.7 s）⇒ **未抓到**；磁盘上 `T49N_1110171_window.png` 仍是**上一轮那份**（sha `72F9AE743F28E7F6`、size 801405 均未变）。故"**改后白块是否消失**"本轮**无法亲眼看证**；能确证的是：**settle 帧无白块（已亲看）、`bad=[]`、settle 期所有 prim 均可见**。要拿到窗口帧目视结论，需一次**专门的窗口抓取**（判定改为"mesh 出现即抓"或 200 ms 连拍取首帧）。
- **settle 帧亲看**：`9b08a1134bfc484e` = 深青铜机身 + 浅蓝白晶体刃、有刻面、无扁平白块 ✓（本版锚点相同 ⇒ 同一帧）。

---

## 11. 专门窗口抓取（2026-09-19，Lead 批准；**本轮未改 viewer.js**，仍 `4F5630461B1EFAC1` / 332,818 B）

**方法**：点击后 **200 ms 连拍 18 帧**（每帧同步读 `__texReady()`/`__neox().report`），**"mesh 出现即抓"**（不再要求 `bad` 非空）；settle 后 `__primOnly(-1)` 取 bg，同口径算五读数。

**抓到的窗口帧**
| 项 | 值 |
|---|---|
| 文件 / sha16 | `T49W_window.png` / **`7e2e5e54a88f7cd9`**（1578×902；`T49W_first_mesh.png` 同帧同 sha） |
| 抓取时刻 | **1760 ms**（点击起算） |
| 同帧状态 | `n:4` · `bad:["0:ibl_pending","1:ibl_pending"]` · **`vis:"0H1H2v3v"`（prim0/1 已隐藏）** · `retry:0` · `pend:true` |
| **五读数**（`criterion=mask/weapon_box`） | `mask_pct 16.133` · **p50 0.1392** · p95 0.7934 · **>0.5 13.123** · >0.75 6.308 · **暖色 1.897** |
| 改前对照（`3c2249e56afa3638`） | **p50 1.000** · **>0.5 58.0%** · **暖色 54.5%** |

**亲眼看（我本人）**：**扁平白块已消失** —— 画面是**深青铜机身 + 几条细白高光/细片**，**没有**改前那种"整片无结构纯白面"；细白条仍在但面积很小、不成"白块"。⇒ 与读数一致（p50 1.000 → 0.1392、`>0.5` 58% → 13.1%、暖色 54.5% → 1.9%）。

**窗口时间线（同一次载入，仅列变化点）**
```
 857ms  n=0                          （材质未建）
1760ms  n=4  bad=[0,1]  vis=0H1H2v3v            ← pendingHide 生效；抓窗口帧
2555ms  n=7  bad=[0,1]  vis=0H1H2v3v4v5v6v  ph=[0,1]
3299ms  n=7  bad=[1]    vis=0v1H2v3v4v5v6v  ph=[1]      ← prim0 已恢复
4122ms  n=7  bad=[]     vis=0v1v2v3v4v5v6v  ph=[]       ← 全部恢复（窗口结束）
```
⇒ **窗口 ≈ 1.76→4.12 s（≈2.4 s）**，隐藏**逐 prim 恢复**、settle 全可见 ⇒ **安全阀有效** ✓。

### 🔴 本轮新发现（我的镜像缺陷，未修；待下一轮）
**`__texReady().pending_hidden_total` 恒为 0**：该计数遍历的是 **mesh 的 `o.userData.__pendingHidden`**，而隐藏标记写在 **材质的 `m.userData.__pendingHidden`** 上 ⇒ 永远读不到。证据（同帧）：`2555ms` 时 `vis="0H1H2v3v4v5v6v"`、`ph=[0,1]`，但 **`th=0`**。
- **修法（1 行）**：`__texReady()` 统计判据改为 **`o.material.userData.__pendingHidden`**（与 `__acceptanceReport()` 的 `ud=mm.userData` 口径一致）。
- **影响**：§10 的"三源一致"**只在 settle 期成立（三者恰为 0）**；**窗口期三源并不一致**（`th` 恒 0）⇒ 修完须在**窗口期**复验三源一致。
- 本轮**未改代码**（Lead 指令"做完这一件就停手"），viewer.js 仍 **`4F5630461B1EFAC1`**；清理：`KILLED=2 / LEFT_MINE=0 / PORT_9601_LISTEN=0`。

---

## 12. 镜像修复 + 窗口期三源复验（2026-09-19；`viewer.js 4F5630461B1EFAC1 → 0B9F2148E6A9935D`）

**改动（1 处，L4213-4223）**：`__texReady()` 的 `pending_hidden_total` 判据由 **mesh `o.userData.__pendingHidden`** 改为 **材质 `mm.userData.__pendingHidden`**（与 `__acceptanceReport()` 的 `ud=mm.userData` 同源）。备份 `%TEMP%\wsv_bak_task49L_20260919_160128.js` = **`4F5630461B1EFAC1`**；`node --check` 通过；**新 sha16 `0B9F2148E6A9935D`**（333,466 B）。

**§10 结论更正（按 Lead 要求）**：**settle 期三源一致；窗口期因该镜像缺陷不一致（`th` 恒 0），已修后复验。**
- **修复生效**：窗口帧（t=1706/2727 ms）`src_tex_total` 由 **0 → 2**，与 `src_acc_total=2`、`src_acc=[0,1]` 一致 ✓。

### 🔴 但窗口期**三源仍未一致**，原因**已精确定位（与上一缺陷不同，不凑口径）**
| t | n | bad[] | vis | `src_neox` | `src_acc` | `tex_total` | `acc_total` | `ph_source` |
|---|---|---|---|---|---|---|---|---|
| 792 ms | 0 | — | `` | `[]` | `[]` | 0 | 0 | `null` |
| **1706 ms** | 5 | `[0:ibl_pending,1:ibl_pending]` | `0H1H2v3v4v` | **`[]`** | `[0,1]` | **2** | **2** | **`null`** |
| **2727 ms** | 6 | 同上 | `0H1H2v3v4v5v` | **`[]`** | `[0,1]` | **2** | **2** | **`null`** |
| 3536 ms | 7 | `[]` | `0v1v2v3v4v5v6v` | `[]` | `[]` | 0 | 0 | `read_time` |

**根因（最小复现）**：`state.neoxReport` **只在 `applyNeoxManifest()` resolve 时赋值**（函数末尾），而 `pendingHide` 在**材质建立过程中**就打标记 ⇒ **窗口期 `state.neoxReport` 仍为 `null`** ⇒ `__neoxLiveEnv()` 命中 `if(!rep) return rep;` 直接返回 ⇒ `__neox().report` **没有 prim 列表**（`prims` 缺省空）⇒ 该路在窗口期无法表达 pending。
**复现步骤**：载入 1110171，在 `__texReady().meshes` 非空且含 `ibl_pending` 时**同帧**读三源 ⇒ `src_neox=[]` / `src_acc=[0,1]` / `tex_total=2`；等 `bad=[]` 后三源同为 0 且 `ph_source='read_time'`。

**修法（两选一；**不采用"改口径凑一致"**）**
- **(A) 合成 prim 列表（推荐）**：`__neoxLiveEnv()` 在 `state.neoxReport` 为空（或尚未含目标 prim）时，用**场景 live 材质**（`byPrim` 键）合成 `prims`，至少填 `{prim, pending_hidden, envMode}`，并标 `pending_hidden_source:'read_time(scene-synthesized)'`。
- **(B) 独立 live registry**：`pendingHide` 处同时写 `state.__pendingHiddenPrims`（Set），`__neox()` 暴露 `report.pending_hidden_live`，三源口径改为"`pending_hidden_live` / `__texReady().pending_hidden_total` / `__acceptanceReport().pending_hidden_total`"。
- 两者都不改渲染、不改 fail-closed。

**窗口帧复核**：`T49S_window.png` sha16 = **`7e2e5e54a88f7cd9`**（与改前 `T49W_window.png` **逐字节相同**）⇒ 五读数相同 `mask_pct 16.133 / p50 0.1392 / p95 0.7934 / >0.5 13.123 / >0.75 6.308 / 暖色 1.897` ⇒ **本轮修复未改变渲染** ✓、**窗口帧无扁平白块**（§11 已亲眼看证）。
**settle**：`n=7 · bad=[] · vis=0v1v2v3v4v5v6v · src_*=0 · ph_source='read_time'` ✓。
**清理**：`killed=2 / LEFT_MINE=0 / PORT_9591_LISTEN=0` ✓。

---

## 13. (A) 修法落地（2026-09-19；`viewer.js 0B9F2148E6A9935D → 4647CF0BE061AD81`）

**Lead 裁决**：批准 **(A)**（从 live 材质合成 `prims`）——**不加第二状态源**、**渲染零变化**、**实测由 viewer-auditor 独立复测承担**。

**逐处改动（`__neoxLiveEnv()` 内 2 段）**
| 行 | 原文 | 新文 |
|---|---|---|
| L3182 → **L3189** | `var rep=state.neoxReport; if(!rep) return rep;` | **`var rep=state.neoxReport||{};`** ⇒ rep 为空不再空转返回，改走下面的 live 合成路径 |
| L3214-3220 → **L3214-3249** | `primsLive=(rep.prims\|\|[]).map(...)` 后直接 `return Object.assign({… pending_hidden_source:'read_time' …})` | **(a) 合成**：以 `byPrim` 键为准，把**只存在于场景、尚未进入 report** 的 prim 补进 `primsLive`（标 `synthesized:true`，字段取自同一份 live 材质）；**(b)** `miss/warn` 遍历对象由 `rep.prims` 改为 **`primsLive`**（否则窗口期 `missing/env_warn` 也看不见未就绪 prim）；**(c)** `pending_hidden_source:(synthesized?'read_time(scene-synthesized)':'read_time')` |

**备份**：`%TEMP%\wsv_bak_task49M_20260919_160315.js` = **`0B9F2148E6A9935D`** · `node --check` **通过** · **新 sha16 `4647CF0BE061AD81`**（335,971 B · 4575 行）。
**约束核对**：**无第二状态源** ✓（只读 `byPrim`）· **不改渲染** ✓（该函数只构造 `__neox()` 返回对象）· **不改 fail-closed** ✓ · **本轮未起浏览器** ✓（`HEADLESS_NOW=0`）。

**代码级论证（窗口期三源应同帧同值）**：窗口期 `state.neoxReport===null` ⇒ `rep={}` ⇒ 合成路径把 `byPrim` 的**全部** live prim 补进 `prims` ⇒ `report.prims[*].pending_hidden` = live `m.userData.__pendingHidden`，与 `__texReady().pending_hidden_total`（**已修**为读材质标记）及 `__acceptanceReport().pending_hidden_total`（读 `ud=mm.userData`）**同源同值**；`pending_hidden_source` 在窗口期为 `'read_time(scene-synthesized)'`、settle 期为 `'read_time'`（可据此判断走了哪条路）。**实测由 viewer-auditor 承担**（其协议含窗口 200 ms × 15 帧 + 五读数 + 三源）。

**已知无害冗余（如实登记）**：函数内原有一段基于 `rep.prims` 的 `miss/warn` 遍历，现被新增的 `primsLive` 版本覆盖（`var` 重声明合法、后者生效，前者成死代码）⇒ **语义正确但留有死代码**，下次动该函数时清理（本轮不再扩 diff）。

**渲染零变化（预期，待独立复测确认）**：本改动不触碰任何渲染路径 ⇒ 预期 **settle 帧 `9b08a1134bfc484e`、窗口帧 `7e2e5e54a88f7cd9` 逐字节不变**。
**清理**：本轮未起浏览器 ⇒ 无残留、无端口占用。
