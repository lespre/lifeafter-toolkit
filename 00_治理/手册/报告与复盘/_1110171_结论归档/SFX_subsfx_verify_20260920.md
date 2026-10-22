# task-73 轻量验收：子特效登记后的零回归（1110177 / 1110171）

**结论速览：PASS 6 · WARN 0 · FAIL 0**（另 2 条口径说明，非缺陷）
本轮改动**未产生任何可见渲染变化**：两把皮肤在 10 个取样点上的帧与 **task-70 逐字节相同**（像素差 0）。

## 0. pin / 版本自证（开工前后各哈希一次，全部一致）
| 对象 | sha16 | 页内 `fetch` 实字节 |
|---|---|---|
| `1110177/effects.json` | **`535909555A2599A6`**（578,144 B） | 200 / 578,144 B / 同 ✅ |
| `1110177/viewer.json` | **`CD4590E5D8353558`**（641,859 B） | 200 / 641,859 B / 同 ✅ |
| `1110171/effects.json` | **`DE667C26A99B7DEC`**（140,218 B） | 200 / 140,218 B / 同 ✅ |
| `1110171/viewer.json` | **`D4F4A8272E7E7BF8`**（173,165 B） | 200 / 173,165 B / 同 ✅ |
| `weapon_skin_sfx_adapter.js` | `7799134F17D5032E`（93,851 B）**未改** | 200 / 93,851 B / 同 ✅ |
| `weapon_skin_viewer.js` | `B9C7281E1EE7A819` **未改** | 200 / 379,489 B / 同 ✅ |
| `board.html` | `44A2339A06BDD4A1` | — |
| `neox_material.1110177` | `A05C4F2C8DDFCF9A` **未改** ✅ | — |
| 5 张真图集（1110177） | `DBC4D2E4FE65FF4F` / `DDE58C1EB420384F` / `BAB99D2E79746152` / `45AE45AB090353CB` / `37FA4BE63541FFAB` **均未变** ✅ | — |
| `atlas171` | `6480F7FC1914F0C4` **未变** ✅ | — |
`pins_unchanged` 全 true（14 项）。rect 三次读数一致 `{x:200, y:122.3, w:1178, h:717.7}`。

## 1. ① 健康与异常 —— **PASS**
| 皮肤 | `__neox()` | 异常 |
|---|---|---|
| 1110177 | **applied 3 == prims 3** ✅、`failed=[]`、`missing=[]`、`env_warn=null`、`pending 0` | `exceptionThrown` 0 / evaluate 级 0 |
| 1110171 | **applied 7 == prims 7** ✅、`failed=[]`、`missing=[]`、`env_warn=null`、`pending 0` | 同上 |
- 贴图请求 **84 条全 200、404 = 0**；**全页唯一 404 = `favicon.ico`**（零观测注入空跑与完整协议各一条，均为 favicon）。
- 注：task 文本写"1110171=3、1110177=7"，**实际相反**（1110177 3 个 prim、1110171 7 个 prim），我按 manifest 实数报。

## 2. ② 节点数 91 / 48 与新子节点在渲染集之外 —— **PASS（附 1 条口径说明）**
清单侧（页内 fetch `viewer.json`，与磁盘哈希一致）：
| 皮肤 | manifest 节点数 | `renderable_by_adapter=true` | `fxIgnore=TRUE` | `unresolved` 类 |
|---|---|---|---|---|
| 1110177 | **91** ✅（89→91） | **11** ✅（不变） | 4 | 0 |
| 1110171 | **48** ✅（44→48） | **11** ✅（不变） | **31** | **4** |
新子特效节点（清单原文）：
```
1110177  L_空特效__sub     tag=Dummy  renderable=false  fxIgnore=false  status=no_texture_declared  spr_frames=0
1110177  L_模型特效__sub   tag=Model  renderable=false  fxIgnore=false  status=no_texture_declared  spr_frames=0
1110171  L_glow_03         tag=Sprite renderable=false  fxIgnore=TRUE   status=unresolved_dot_tga_no_evidence  spr_frames=0
1110171  L_glow_03_1       tag=Sprite renderable=false  fxIgnore=TRUE   status=unresolved_dot_tga_no_evidence  spr_frames=0
1110171  L_glow_03_2       tag=Sprite renderable=false  fxIgnore=TRUE   status=unresolved_dot_tga_no_evidence  spr_frames=0
1110171  L_p_光刺_01_1     tag=ParticleSystem renderable=false fxIgnore=false status=unresolved_dot_tga_no_evidence spr_frames=0
```
⇒ **6/6 全部 `renderable_by_adapter=false`，都在渲染集之外** ✅（fail-closed 生效；`L_glow_03*` 还叠加 `FxIgnore=TRUE`）。
**⚠ 口径说明（不是缺陷）**：`__sfxDiag()` **不是**按 manifest 全量列节点的，它只列**参与运行的**节点 —— 本轮实测 1110177 `nodes 23 / sprites 3 / particles 20`、1110171 `nodes 14 / sprites 4 / particles 10`。**91 / 48 是 manifest 级计数**（我已在页内 fetch 核对），diag 的 23/14 是运行级子集；两者都对，只是口径不同。
- 新节点在 diag 里的实况：1110177 的 `L_空特效__sub` / `L_模型特效__sub` **不在 diag**（非运行节点）✅；1110171 的 `L_glow_03/_1/_2` 不在 diag ✅；**`L_p_光刺_01_1` 在 diag 里有一行**，其运行时原文为：
```
{"name":"L_p_光刺_01_1","kind":"particle","in_pool":0,"visible":0,"rate_source":"absent","alive_now":0,
 "fallback":null,"sliced_frames":0,"slice_path":null,"ignored":false,"fx_ignore_honored":true,"frame_index_last":null,"sheet":null,"quad":null}
```
⇒ **登记在册但不发射、不渲染**（`in_pool 0 / visible 0 / alive 0 / rate absent / 无 sheet`）✅ 与"`renderable=false`"一致。

## 3. ③ 默认态零回归（会话内自洽 + 与 task-70 同值）—— **PASS**
| 皮肤 | SFX OFF 门控帧（N≥5） | MASK 五读数 | OFF↔SFX 往返 |
|---|---|---|---|
| 1110177 | **`e62c1c58e5bdc383`**（与 task-70 相同） | `1.826 / 0.2829 / 0.5745 / 18.242 / 0.989 / 0.689`（= 长期基线） | 回同值 ✅ |
| 1110171 | **`48b6c95c1165c80a`**（与 task-70 相同） | `2.449 / 0.1232 / 0.4865 / 3.394 / 0.273 / 0.106`（= 长期基线） | 回同值 ✅ |
（1110171 的 OFF 门序列前 2 帧为瞬态 `a823bdb9…`/`e5df2f71…`，第 3 帧起稳定 —— N≥5 门正确跳过。）

## 4. ④ 画面零回归 —— **PASS：10 个取样点与 task-70 逐字节相同**
| 皮肤 | t | 本轮 sha16 | = task-70？ | 像素差（>6/255） |
|---|---|---|---|---|
| 1110177 | 0.08 | `08738b769b60e619` | ✅ | **0 px** |
| 1110177 | 0.14 | `59c4d9f613fc7b23` | ✅ | **0 px** |
| 1110177 | 0.22 | `cde8ef83db23b530` | ✅ | **0 px** |
| 1110177 | 0.30 | `0ff65ed7b8b91b0a` | ✅ | **0 px** |
| 1110177 | 0.55 | `81f258ba298e1197` | ✅ | **0 px** |
| 1110177 | 1.15 | `40554a2b3676e2aa` | ✅ | **0 px** |
| 1110171 | 0.10 / 0.20 / 0.35 / 0.55 | 四点全 `a541529334382b28` | ✅ | **0 px ×4** |
- 全部 **N≥5 稳定门通过**（`gate_ok=true`）；MASK 五读数与 task-70 同档（1110177 mask 1.827–1.962、p50 0.280–0.293；1110171 mask 2.449、p50 0.1232）⇒ **本轮子特效登记对可见画面为零影响**（与"预期不产生新可见渲染"完全一致）。
- 画面**无全黑/全白/格阵/糊团**：掩模内白像素 1110177 **0.677%**、1110171 **0.089%**（与各轮基线持平）。

## 5. ⑤ 6 皮肤回归 —— **PASS**
| 皮肤 | applied/expected | failed / missing | env_warn | SFX 默认态 |
|---|---|---|---|---|
| 1110024 | **5 == 5** | 0 / 0 | null | `SFX 关闭`（disabled=true, pressed=false） |
| 1110129 | **5 == 5** | 0 / 0 | null | 同上 |
| 1110145 | **7 == 7** | 0 / 0 | null | 同上 |
| 1110152 | **2 == 2** | 0 / 0 | null | `SFX 关闭`（disabled=false, pressed=false） |
| 1110165 | **4 == 4** | 0 / 0 | null | 同上（disabled=true） |
| 1110171 | **7 == 7** | 0 / 0 | null | `SFX 关闭`（disabled=false, pressed=false） |

## 6. ⑥ 未变清单 —— **PASS**
`viewer.js B9C7281E1EE7A819`、`adapter 7799134F17D5032E`、`m1110177 A05C4F2C8DDFCF9A`、5 张真图集（`DBC4D2E4FE65FF4F` / `DDE58C1EB420384F` / `BAB99D2E79746152` / `45AE45AB090353CB` / `37FA4BE63541FFAB`）、`atlas171 6480F7FC1914F0C4` —— **开工前后哈希全一致**。

## 7. 说明（非缺陷，供归档）
1. **diag 计数 ≠ manifest 计数**：`__sfxDiag()` 只列运行集（23/14），manifest 才是 91/48；后续复测请按"manifest 验节点数、diag 验运行集"分工。
2. **`L_p_光刺_01_1` 出现在 diag 但不在渲染集**：这是"登记 + fail-closed（贴图 unresolved）"的正常表现；它的 `in_pool/visible/alive` 全 0。
3. `unresolved` 计数只统计 `texture_status` 含 "unresolved" 的节点：1110171 = 4（新子节点）；1110177 的两个新子节点状态是 `no_texture_declared`（另一类）⇒ 1110177 的 unresolved = 0。

## 8. 纪律与产物
- 只读 `08Lifeafter wiki/**`（未改任何文件）；单浏览器 `FXVA73_prof` / 端口 **10131**；结束按 `user-data-dir` 反查真实 PID `taskkill /T /F`（8 进程）；**端口 10131 无 LISTEN**、我的 profile chrome = 0、全机 chrome 0。
- 产物（仅写 task 允许的三条路径）：本报告 + `SFX_subsfx_verify_20260920.json`；截图目录 `sfx_verify_shots5/`（两皮肤默认 OFF/bg + 10 张 N≥5 稳定帧）。
