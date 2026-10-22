# POSTER 终轮（task-27）报告：7 皮肤 变/未变 判定 + 1110129/1110171 的**暗化回归**与回滚

只读判定 + 只在"确有变化"时重拍；**本次已把两处重拍回滚**（原因见 §2），未改任何默认文件。

## 0. 口径披露（每皮肤相同）
- **入口**：board/默认页（`board.html?b=...&view=wiki&sort=id&dir=desc`，**不带 `lab=1`**）
- **窗口/画布**：Chrome `--window-size=1600,1000`（headless=new, `--force-device-scale-factor=1`）→ canvas **1178×718**（所有 7 皮肤一致）
- **隐藏**：`__post(false)` + `__hidePanels(true)` + `__sfxTime(0)` + HIDE_JS → **`hide_dom=24`**，`rect_unchanged=true`（取帧前复核 rect ✓）
- **帧稳定门**：连续两帧 sha16 相同才取帧 → **7/7 皮肤 `stable_tries=2`**（纪律已加 ✓）

## 1. 变/未变判定（新帧 vs 当前海报源帧，逐像素）

| skin | 新帧 sha16 | 基准（海报源帧） | 逐像素差 | 判定 |
|---|---|---|---|---|
| 1110024 | `d2edd7f700619a70` | `TASK19_1110024_board_full.png`（同 sha） | **0 px** | **未变 ⇒ 无需替换，未覆盖** ✓ |
| 1110145 | `7a449dc13a1b7124` | `POSTER_1110145_diag_full.png`（同 sha） | **0 px** | 同上 ✓ |
| 1110152 | `2549fe2ffc362af2` | `TASK19_1110152_board_full.png`（同 sha） | **0 px** | 同上 ✓ |
| 1110165 | `62b1fc7ece47cef1` | `POSTER_1110165_diag_full.png`（同 sha） | **0 px** | 同上 ✓ |
| 1110177 | `dee6955320b3df7d` | `POSTER_1110177_diag_full.png`（同 sha） | **0 px** | 同上 ✓ |
| **1110129** | `96a348146a34004d` | `PM4_1110129_board.png` `a320649d52a081d0` | 17,883 px = **2.117%**（max 255） | ★ **确有变化** |
| **1110171** | `9626b6e09584b44a` | `POSTER_1110171_diag_full.png` `bbed79bbb2092b14` | 32,533 px = **3.852%**（max 255, mean 2.016） | ★ **确有变化（非预期）** |

⇒ **只有 1110129 如预期变化；1110171 也变了（Lead 预计不会变）** ⇒ 两者都需重拍 ✓

## 2. ★ 但两张的新画面都是**暗化到近乎全黑剪影** ⇒ 我已回滚，未发布

**我裁切后的指标（1600×900 / q88 / uiPix=0）**
| skin | 新（暗）字节 | 新 sha16 | 旧（好）字节/sha16 | 非背景% | 武器区 p50 | p95 | gold% | 主体高 |
|---|---|---|---|---|---|---|---|---|
| 1110129 | 51,018 | `b889f0b43605443c` | 65,408 / `265dc756e3b5f32e` | 16.5 | 35.3 | **58.0**（旧 65.9） | **0.00**（旧 3.31） | 558.4 px (62.0%) |
| 1110171 | 45,084 | `5fa91fa053de1581` | 74,540 / `0b72060d067a82a8` | 9.0 | 36.1 | **51.6**（旧 81.1） | **0.00** | 557.2 px (62.0%) |

画布帧指标：1110129 掩模 6.72% · meanL **10.07**（task-25 时 19.90）· p50 8.57；1110171 掩模 4.2% · meanL **6.59**（此前 53.45）· p95 51.6。

**我看过两张（`POSTER_final_1110129_board.png` / `POSTER_final_1110171_board.png`）**：
- 1110129：枪**左半（枪托段）几乎纯黑**、只剩右段有细节 ✗（上一版整枪有蓝色镶边与高光）
- 1110171：**整把武器近乎全黑剪影**、只剩少许浅色高光 ✗（上一版是蓝紫晶体 + 中央粉紫核心）

**处理**：为避免把"明显变差的暗图"推到用户面前，我**只做了回滚**（不是美化）：
`1110129/poster.webp` 恢复为 `265dc756e3b5f32e`、`1110171/poster.webp` 恢复为 `0b72060d067a82a8`（**已校验 sha 一致 ✓**）。
暗帧与裁切参数全部留档：`POSTER_final_<skin>_board.png`（`96a348146a34004d` / `9626b6e09584b44a`）、`POSTER_final_posters.json`、备份 `POSTER_final_<skin>_old.webp`。
⇒ **是否发布当前暗画面，请 Lead 决定**；你点头我一分钟内可重出（参数已固定）。

## 3. 归因证据：**不是链/数据断了**，而是 viewer 修订的着色结果

两皮肤当前读数（同一轮抓取）：
```
toneMapping=4(ACES) · exposure=1.75 · background="texture" · envIntensity=1.4 · lights 同前（Hemisphere0.8 + Dir1.5 + Dir0.5）
__neox(): applied=5（1110129 全部 prim）/ applied=7（1110171 全部 prim）· failed=[] · missing=[] · 每 prim status="applied"
__meshDump(): 每 mesh matVisible=true · fragLen=24556 · hasMap/hasEnv=true · inFrustum=true
__acceptanceReport(): 每 prim ibl_faces=6 · uIblScale=0.25 · roughness/metalness 映射同前
__fragMarkers(): 每 prim q_envW/rad/079956 全 true（补丁在）
```
⇒ 材质链、cube 六面、补丁、曝光/色调映射**全部正常** ⇒ 暗化发生在**着色/光照结果**层，不是加载或数据问题。
**时间线旁证**：`weapon_skin_viewer.js` sha16 在 task-25 时是 **`6E9589555911287E`**，本轮到 **`ba2a84695e53f865`**（本轮跑动期间未变）⇒ 暗化与 **viewer 修订变更**同时发生。
**具体归因（哪一处改动导致）我不猜**：需要 viewer 所有者（Lead / shader-auditor）比对这两版 diff 才能定；本报告只给读数与时间线。

## 4. 未变动的 5 张（未覆盖，逐像素 0 差异）
1110024 / 1110145 / 1110152 / 1110165 / 1110177 —— 当前帧与各自海报源帧**逐字节相同** ⇒ **无需替换** ✓
（其余读数：1110024 掩模 7.26%/meanL 96.37；1110145 9.36%/66.97；1110152 8.74%/37.11；1110165 7.54%/30.65；1110177 3.24%/95.25）

## 5. 命令与产物
```
venv\Scripts\python.exe %TEMP%\P27_final.py    # 7 皮肤取帧（稳定门 + rect 复核 + hide_dom）
venv\Scripts\python.exe %TEMP%\P27_cmp.py      # 逐像素 变/未变 判定
venv\Scripts\python.exe %TEMP%\P27_post.py     # 对“确有变化”的两张重裁（随后已回滚）
venv\Scripts\python.exe %TEMP%\P27_diag.py     # 链/渲染器状态诊断（含 viewer sha 前后）
```
产物：`POSTER_final_frames.json` · `POSTER_final_compare.json` · `POSTER_final_posters.json` · `P27_DIAG_result.json` · `POSTER_final_<skin>_board.png` / `_board_bg.png` · 备份 `POSTER_final_<skin>_old.webp`
