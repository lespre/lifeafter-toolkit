# PM4 验收报告：1110129 prim4 补回源级 ParamMap(#410) 后是否已可见（board/默认页）

只读验收；新增文件仅 `_target_1110171/PM4_*`。未改任何默认文件（manifest / viewer / board 均未动）。

## 1. 逐 mesh 对比（`window.__meshDump()`，board/默认页）

改前读数**引 shader-auditor task-18**（我无法回滚 manifest 复测，故标注为引用值）；改后 = 本轮实测。

| mesh | prim | 改前（引用 task-18） | 改后（本轮实测） | 判定 |
|---|---|---|---|---|
| `1110129_1` | 0 | — | matVisible **True** · fragLen **24556** · rad True · vertices 17924 · inFrustum True | 正常 |
| `1110129_2` | 1 | — | 同左 | 正常 |
| `1110129_3` | 2 | — | 同左 | 正常 |
| `1110129_4` | 3 | — | 同左 | 正常 |
| **`1110129_5`** | **4** | **matVisible `false` · fragLen `0` · rad `false`** | **matVisible `True` · fragLen `24556` · rad `True` · vertices 17924 · inFrustum `True` · hasMap `True` · hasEnv `True` · visibleChain `True`** | ✅ **已编译并已显示** |

**明确回答：prim4 已编译并显示** ✓（`matVisible=True` + `fragLen=24556` + `inFrustum=True`，且 `__fragMarkers` 的 `rad=True`）。
`__meshDump` 其余字段：5 个 mesh 全 `kind=weapon`、`frustumCulled` 同构、`side` 同构、`obc=true`（onBeforeCompile 已挂）。

## 2. `__neox()` 与 `__acceptanceReport`（board）

```
applied = 5 ; applied_prims = [0,1,2,3,4] ; failed = [] ; missing = []
prim0..prim4 status = "applied" ; missing_required = []   （含 prim4）
```
`__acceptanceReport()` 逐 prim：`mat = MeshStandardMaterial` · `ibl_faces = qiangpi_f0..f5_m0.png`**六面齐** · `uIblScale = 0.25` ·
`envMap = null`（**设计使然**：源 cube 以 `uCustomIbl` uniform 注入片元，不经 `material.envMap`）· `source_env_bright = null`。

**5 个 prim 的几何完全相同（vertices=17924）** ⇒ 它们是同一几何的 5 层材质壳 ⇒ prim4 从"不渲染"变为"渲染"后，
画面变化很小（见第 3 节），这属预期，不是"没生效"。

## 3. 截图与目视（`PM4_1110129_board.png`）

- 文件：`_target_1110171/PM4_1110129_board.png`（1178×717）· **sha16 `a320649d52a081d0`**
- **我看过**：1110129 熔炉寒霜**整枪完整可见** —— 深色金属枪身 + **蓝色镶边面板** + 白色/浅色高光 + 金色细节，
  构图居中、**无 UI 残留、无纯色块、无全黑、无错位、无尺寸突变** ✓
- board 帧指标：掩模 **6.12%** 画布 · meanL **19.90** · p50 8.57 · p95 70.66 · `toneMapping=4(ACES)`/`exposure=1.75`/`background=texture`
- 与**改前**（task-14 实测：掩模 6.05% · meanL 19.87 · p50 8.51 · p95 70.72）对比：**变化极小（Δmean +0.03）** ⇒ 与"5 层同几何壳"一致 ✓
- ⚠ **附带如实登记**：当前 board 帧 sha `a320649d52a081d0` ≠ task-14 海报所用的源帧 ⇒ **1110129 海报（02:0x）早于本次 prim4 修复**，
  差异虽小但客观存在。**本任务只读，我未重拍**；建议由 lead 决定是否重拍（我可在下轮任务里做）。

## 4. 残差登记：`#410` 的 alpha 与同类 `_m` 不同 —— **当前无影响** ✓

我自己测的（PIL，只读）：

| 文件 | 尺寸 | alpha min/mean/max | R mean | G mean |
|---|---|---|---|---|
| `008_f_m.png`（=#410，与 `008_f_a.png` **字节完全相同**） | **512×512** | **0.000 / 0.0728 / 1.000** | 0.6459 | 1.0000 |
| `008_e_m.png`（同类 #408） | 1024×1024 | 1.000 / 1.0000 / 1.000 | 0.1619 | 1.0000 |
| `param_repack_008.png` | 1024×1024 | **1.000 / 1.0000 / 1.000** | 1.0000 | **0.1571** |
| `rough_repack_008.png` | 1024×1024 | 1.000 / 1.0000 / 1.000 | 1.0000 | 0.6796 |

- 我实测 `A[0,0] = 0.000`（auditor 报 `a0=0.807`）—— **口径可能不同**（首像素 vs 其他位置/统计量），此处以我的实测值为准并标注分歧。
- **渲染不消费 `ParamMap.alpha`** ✓：three 的 `roughnessMap` 读 `.G`、`metalnessMap` 读 `.B`；而 viewer 给的是
  **派生贴图** `param_repack_008.png`（**alpha ≡ 1**，只做 R→G 重排）。⇒ `#410` 的 alpha 残差**不进入渲染** ⇒ **当前无影响** ✓
- 另注：family 级 repack（1024², Gmean 0.1571）来源于 `_m` 家族源，**不是**新绑的 512² `008_f_m.png`（Rmean 0.6459）；
  即 prim4 的 `ParamMap` 绑定作用是**补齐链的必需槽位**（使 prim4 通过 fail-closed 检查并渲染），不改变 roughness 取值来源。

## 5. 回归

- **`wiki_selfcheck.py`**：`PASS 63 · FAIL 1 · WARN 0`，退出码 1（符合作业要求 PASS≥63 / FAIL≤1）✓
  唯一 FAIL = 1110171 `map/normalMap 缺`（crystal 族的已知 SwiftShader 假阳性），但**本轮明细为 mesh[2,3,5,6]**
  （Lead 此前记录为 mesh[3,5,6]，**多出 #2**）⇒ 如实登记差异，非 1110129 改动引起（不同皮肤、不同族）。
  1110129 在自检中为 **PASS**（"5 mesh 按族判据全过"）✓；1110024/1110165/1110145/1110152/1110177 均 PASS ✓
- **逐帧回归（最硬）**：1110024 board 帧 **sha16 `d2edd7f700619a70`**、1110152 board 帧 **sha16 `2549fe2ffc362af2`**
  —— 与本次变更**之前**我的实测帧**逐字节相同** ⇒ **其它皮肤零回归** ✓
  （指标：1110024 掩模 7.26%/meanL 96.37/p50 74.75/p95 226.3；1110152 8.74%/37.11/22.48/99.79；两者 `rect_unchanged=true`、`hide_dom=24`）

## 6. 附：Lead 引用值的一处对不上（如实登记）
Lead 说 before sha256 `ceb8173c2ef007f1` / 20,581 B；但磁盘上 `bak_pm4_20260918_031737` = **21,162 B / sha16 `9596bd860124bbb7`**，
且 bak 链为 `bak_003947` 19,096 B（`5aefd78a5ffff562`）→ `bak_fg_024152` 20,465 B（`906e47d6a7023bf7`）→ `bak_pm4_031737` 21,162 B（`9596bd86…`）→ 现状 22,891 B（`2312fdca0f90fa99` ✅ 与 Lead 的 after 一致）。
⇒ **after 值吻合、before 值无对应文件**，只作登记（不影响本次验收结论）。

## 7. 命令清单
```
venv\Scripts\python.exe %TEMP%\PM4_man.py      # manifest/备份/贴图 sha 与 alpha 只读校验
venv\Scripts\python.exe %TEMP%\PM4_res.py      # bak 链 + #410 alpha 残差
venv\Scripts\python.exe %TEMP%\PM4_verify.py   # board 逐 mesh 验收（__meshDump/fragMarkers/neox/acceptance）+ 截图 + 2 皮肤回归
venv\Scripts\python.exe 06_皮肤定位链\wiki_selfcheck.py   # PASS 63 / FAIL 1
```
产物：`PM4_result.json` · `PM4_1110129_board.png`(=`a320649d52a081d0`) · `PM4_1110129_board_bg.png` · `PM4_1110024_board.png` · `PM4_1110152_board.png`
