# TASK-19 证据汇总（1110024 / 1110152 海报重拍 + 1110024「空的」二值验证）

写作用域：`1110024/poster.webp`、`1110152/poster.webp`、`_target_1110171/TASK19_*`。未改 viewer / manifest / board.html。

## 1. 海报重拍（口径：1600×900 / q88 / uiPix=0 / 主体高 62% / `rect_unchanged=true`）

| skin | 尺寸 | 新字节（旧） | 新 sha16 | 旧 sha16 | 非背景% | 武器区 p50/p95 | 主体高 | bbox 触边 |
|---|---|---|---|---|---|---|---|---|
| **1110024** | 1600×900 | **133,960**（134,130） | **`826106cf0433c9b7`** | `9314222700e7795e` | 18.9 | 37.8 / 129.2 | 557.2 px = **61.9%** | 否 |
| **1110152** | 1600×900 | **115,718**（115,726） | **`26fcbdb6c6adc744`** | `8791c441fe6f4a08` | 20.5 | 37.8 / 81.1 | 558.0 px = **62.0%** | 否 |

两张 `uiPix=0`、`magenta_pct=0.0`、`clamped=false`；旧图备份 `POSTER_1110024_old.webp` / `POSTER_1110152_old.webp`。

## 2. ★ 1110024 二值结论：**「可见有色模型」** ✓（不是洋红、不是空白）

- **亲眼看过的截图**：`_target_1110171/TASK19_1110024_board_full.png`（1178×717, sha16 `d2edd7f700619a70`）
  —— 目视 = **银白/金色装饰的完整枪械**，构图居中、无 UI、无洋红块 ✓✓
- board（默认页）武器区读数（掩模 = 无-mesh 帧差集，61,318 px = **7.26%** 画布）：
  **mean L 96.37** · p50 74.75 · p95 226.30 · **gold 26.14%** · silver 19.45% · **magenta 0.00%** · bg mean 38.71
- 逐 prim（`__acceptanceReport` / `__neox().report`）：5/5 `status="applied"` · `missing_required=[]` ·
  `unresolved_slots=["t_surfacemap"]`（唯一）· `ibl_faces` = `gdansk_shipyard_buildings_f0..f5_m0.png` 六面全齐 ✓
- ⇒ **fail-closed 洋红占位已不存在**（magenta 0.00% + 目视无洋红 + 5/5 applied）

## 3. 两个入口（board 卡片 / `?lab=1`）—— **1110024 存在严重差异，仅登记不改**

| 入口 | 掩模占画布 | 掩模内 mean L | p50 | p95 | 帧 sha16 | 目视 |
|---|---|---|---|---|---|---|
| 1110024 **board** | 7.26% | **96.37** | 74.75 | 226.3 | `d2edd7f700619a70` | 完整银金枪械 ✓ |
| 1110024 **lab** | **70.46%** | **0.00** | 0.00 | 0.00 | `85955a822f2239dd` | **几乎全黑**（仅右侧一条背景可见）✗ |
| 1110152 **board** | 8.74% | 37.11 | 22.48 | 99.79 | `2549fe2ffc362af2` | 深色机械武器 ✓ |
| 1110152 **lab** | 24.26% | **98.31** | 87.38 | 186.3 | `4e7699a0747ba95b` | 明显更亮更大 |

**逐 prim `len / q_envW / rad`（两入口逐条对比）**
- 1110024：board = `p0..p4 len=24556 q_envW=True rad=True`；lab = **完全相同**（5 条一致）
- 1110152：board = `p0/p1 len=24556 q_envW=True rad=True`；lab = **完全相同**
⇒ **两入口的材质注入读数一致** ⇒ 1110024 的 lab 全黑**不是**注入层差异，而是**画幅/相机/渲染层**问题（登记给 task-18，本任务只取证不改）。

## 4. ★ 1110152 特效：**当前画面中没有特效**（如实登记，未美化）

`__cfgEffects()` 运行时原始读数（board 与 lab 完全一致）：
```
effects_status          = "partial"          ← 磁盘 effects.json（138,641 B, schema v3, skin_1012_009）
effects_node_count      = 40                 ← 清单里确实有 40 个节点
adapter_present         = true  (attach=function)
handle_present          = false   ★ 关键：适配器**未附着** ⇒ 运行时无任何特效实例
btn_disabled            = false ; btn_text = "SFX 关闭" ; btn_title = "切换实时特效"
inline_has_effects      = false
```
⇒ **海报中无特效 = 因为 `handle_present=false`（Model 默认关，`.gim`/SFX 未接）**，
  特效清单在磁盘上存在（40 节点）但运行时未附着；**我没有开启开关、也没有把它拍成有特效的样子** ✓
  目视复核：`TASK19_1110152_board_full.png`（sha16 `2549fe2ffc362af2`）无辉光/粒子/拖尾 ✓

对照 1110024（无特效清单）：`effects_status="none"` · `btn_disabled=true` · `btn_title="该模型没有 SFX 清单"` ✓

## 5. 命令清单
```
venv\Scripts\python.exe %TEMP%\TASK19_verify.py    # 4 次测量（2 皮肤 × 2 入口）+ cfgEffects/acceptance/fragMarkers
venv\Scripts\python.exe %TEMP%\TASK19_diag.py      # 离线复核 in-page 指标（确认 board 帧非黑）
venv\Scripts\python.exe %TEMP%\TASK19_post.py      # 从 board 帧重裁两张海报 + 备份 + 验收
```
证据文件：`TASK19_result.json`（4 条完整读数）· `TASK19_posters.json`（海报指标）·
`TASK19_1110024_board_full.png` / `TASK19_1110024_lab_full.png` / `TASK19_1110152_board_full.png` / `TASK19_1110152_lab_full.png`
（+ 各自 `_bg.png` 无-mesh 背景帧）。

**未动其它 5 张海报与 `_build/render_*.png`。**
