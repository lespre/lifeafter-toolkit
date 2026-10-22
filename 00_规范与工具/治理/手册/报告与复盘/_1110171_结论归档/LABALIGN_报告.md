# LABALIGN：lab/board 口径对齐（我上轮 lab 数字的复测结论）

只读复测；新增文件仅 `_target_1110171/LABALIGN_*`。未改 viewer/manifest/board。

## 1. 我上轮（TASK19_verify.py）lab 页构造原文 —— 逐条

| 项 | 值 |
|---|---|
| 完整 URL | `http://127.0.0.1:8765/board.html?b=weapon_skin_sfx_text_sources&view=wiki&sort=id&dir=desc&lab=1`（`BASE + '&lab=1'`） |
| 入口方式 | `Page.navigate(url)` → **sleep 9000 ms** → `WikiWeaponViewer.open(registry_record,{title:'x'})`（等价于卡片 `openSkin3D`；非点击，是直接调用同一 record） |
| 等待条件 | 轮询 `__neox()` 含 `"applied"`（≤40×1500 ms）→ 再 sleep 2000 ms |
| 我的探针 | `__post(false)` → `__hidePanels(true)` → `__sfxTime(0)` → sleep 1200 ms → 4 次 CDP 探针（cfgEffects/acceptance/neox/matdump）→ **读一次 rect** → `HIDE_JS`（DOM 覆盖层隐藏）→ sleep 1000 ms → **单次截图** |
| 相机 | **未额外改动**（无 `__setCam`）；由 viewer.json 默认 `game_reference` 生效 |
| 其它开关 | 无 `__diagAlb`、无 `__useCubeEnv`。`__primOnly(-1)/(null)` **仅用于背景帧**（在 full 之后） |
| 窗口/画布 | Chrome `--window-size=1600,1000`（headless=new, `--force-device-scale-factor=1`）→ canvas rect ≈ `1178×717.7`，backing `1178×718` |
| 取帧时机 | 单次截图；**无帧稳定门**；rect 只读一次且**未在 HIDE 后复核** |

## 2. 复测（LABALIGN.py：每入口两次读数 + 帧稳定门 + rect 复核）

**R0 = 不动任何探针**（navigate→open→applied→稳定门→取帧）；**R1 = 走我上轮口径**；稳定门 = 连续两帧 sha16 相同。

| 皮肤 | 入口 | 读数 | 掩模% | 掩模 mean L | p50 | 帧 sha16 | toneMapping | bloom | 稳定尝试 |
|---|---|---|---|---|---|---|---|---|---|
| 1110024 | board | R0 | 6.64 | **96.26** | 74.79 | `7c4b418c2fe09a87` | 4 (ACES) | false | 3 |
| 1110024 | board | R1 | 7.26 | **96.37** | 74.75 | `d2edd7f700619a70` | 4 | false | 2 |
| 1110024 | **lab** | R0 | 8.68 | **91.61** | 74.95 | `79e429c7a85b4ca3` | **0 (NoToneMapping)** | **true** | 3 |
| 1110024 | **lab** | R1 | 9.74 | **92.70** | 76.77 | `1a0908284431970c` | 0 | true | 2 |
| 1110152 | board | R0 | 8.07 | **37.10** | 22.65 | `d9d63d881314b081` | 4 | false | 3 |
| 1110152 | board | R1 | 8.74 | **37.11** | 22.48 | `2549fe2ffc362af2` | 4 | false | 2 |
| 1110152 | **lab** | R0 | 17.44 | **80.26** | 72.09 | `638310619fdeb25b` | **0** | **true** | 3 |
| 1110152 | **lab** | R1 | 19.56 | **80.89** | 72.21 | `8ee8308f9c0d85f9` | 0 | true | 2 |

## 3. 结论（含自我更正）

1. **「1110024 lab mean 0.00 / 掩模 70.46% 全黑」不可复现** ✗ —— 同 URL、同入口、同窗口，加稳定门后 lab 实测
   **mean 91.61 / 92.70**（p50 74.95 / 76.77），与 board（96.26 / 96.37）同量级 ⇒ **我上轮那条 lab 全黑数字作废**，是我方取帧伪影，不是"lab 渲染黑"。
2. **「1110152 lab 更亮」方向可复现、绝对值不可复现** ✓/⚠ —— 本轮 board 37.10 → lab 80.26（**≈2.16×**，上轮我报 2.6×，且 lab 绝对值 98.31 vs 80.89 不同）。
3. **伪影机理（证据级，不臆测单一原因）**：本轮 `stable_tries = 3`（前两帧 sha 不同）⇒ lab 页在 `applied` 之后**帧尚未稳定**；
   我上轮为**单次截图 + rect 只读一次且 HIDE 后未复核**（对比：其它 harness 我加了 rect 复核，TASK19 这条漏了）
   ⇒ 单发射击落在未稳定/重排中的帧上。**修法即本轮做法**：稳定门 + 取帧前复核 rect。
4. **两入口可复现的真实差异 = 渲染器状态**：lab `toneMapping=0 (NoToneMapping)` / `bloom=true`，
   board `toneMapping=4 (ACESFilmic)` / `bloom=false`（exposure 两页同为 1.75）⇒ 与 shader-auditor 的结论一致 ✓。
5. **海报入口 = 一律 board/默认页** ✓：`POSTER_render.py`、`POSTER_reshoot2.py`、task-14 与 task-19 的海报帧**全部来自不带 `&lab=1` 的 board 页**（脚本内无 lab 分支用于取帧）。
   ⇒ 我上轮 lab 伪影**不影响任何海报**，也不影响 1110024「可见有色模型」结论（那是 board 读数 96.26/96.37）。
6. 接受统一口径：**验收基准 = board/默认页**；lab 仅诊断，且须标注"含 viewer rig 额外光（此处为关 tone mapping + 开 bloom），不可作保真度证据" ✓。

## 4. 掩模口径差异（解释为何与 auditor 的绝对值不同）
我这套掩模 = **无-mesh 帧差集**（`|full − bg| > 24`，bg 由 `__primOnly(-1)` 取），计入模型对背景的遮挡与辉光；
auditor 的读数（如 1110024 board mean 37.28）用的是另一套掩模/区域 ⇒ **绝对均值不可跨口径比较**，可比较的是
「同口径下 board↔lab 的相对关系」与「帧 sha16 是否相同」。

命令：`venv\Scripts\python.exe %TEMP%\LABALIGN.py`；证据 `LABALIGN_result.json` + 8 张 `LABALIGN_*_full.png` / `_bg.png`。
