# 1110177 极光剑 · 5 个 `.spr` 节点改用真图集后的浏览器验收（task-65）

**结论速览：PASS 4 · WARN 2 · FAIL 0**（另含 1 条「未能确认」的诚实边界）
- PASS：① 5 张图集 **全 200**（页内 fetch 显式校验 + 网络侧 19 条贴图请求全 200、**0×404**）② 清单 89 节点 / **可渲染 11**（6→11）且 5 条新绑定字段齐全 ③ **≥7 张 N≥5 稳定帧**全部 `gate_ok=true`、rect 取帧前后一致 ⑤ 6 皮肤默认页回归全绿 + 四个文件 sha16 未变。
- WARN：②′ 5 个节点里 **只有 3 个（闪电族）真正按图集切片**（`sliced_frames=16/16/4`、`frame_index_last` 随时间推进）；**`H_p_烟雾_02` / `H_鬼火_星点_1` 运行时 `sliced_frames=0` + `fallback="source_rate_missing"`** ⇒ 图集绑上了但**未切片**。③′ 目视：形状**很细弱**（见 §3），**未能从截图上确认"明显闪电分叉"**。

## 0. 页面 / pin / 自证
- 页面：`http://127.0.0.1:8765/board.html?b=weapon_skin_sfx_text_sources&view=wiki` → `WikiWeaponViewer.open(1110177 记录)` → **点开 SFX 开关**（adapter 懒挂载：点击后 **0 ms** `__sfxDiag/__probe` 即为 function）。
- pin（**开工前 = 收尾后，全部未变**）：`viewer.js **B9C7281E1EE7A819**`、`adapter **79F5F2B86D321995**`、`board.html **2585162AF98DB68E**`、`1110177/viewer.json **789897E94A81908D**`、`1110177/effects.json **4696FF22F57966B2**`、`1110171/viewer.json 62E7BDDC9CF6EC6D`、`1110177/neox_material.json A05C4F2C8DDFCF9A`。
- 默认 OFF 帧 `e62c1c58e5bdc383`（N≥5 门）；MASK 五读数 `1.826 / 0.2829 / 0.5745 / 18.242 / 0.989 / 0.689`（与长期基线逐项一致）；bg 用 **`__primShow(-1)`**（`e26078dc2f7077da`）。
- rect：`{x:200,y:122.3,w:1178,h:717.7}` —— 默认/取帧后/收尾**三次读数完全一致**。

## 1. 网络层 —— **PASS**
页内 `fetch`（`cache:'no-store'`）显式校验 5 张图集：
| 文件 | HTTP | 字节 |
|---|---|---|
| `lightning07_cs__atlas207659.png` | **200** | 105,308 |
| `lightning_01__atlas207671.png` | **200** | 89,041 |
| `shandian_05_yh_djs__atlas207712.png` | **200** | 69,319 |
| `smoke25__atlas208478.png` | **200** | 116,541 |
| `tex_special_fangkuai_tp52__atlas211384.png` | **200** | 22,831 |
- 网络侧本轮 `/sfx/tex/` + `/src_tex/` 共 **19 条请求全部 200、404 = 0**。
- **本页 404 逐条**：仅 **1 条 `favicon.ico` 404**；**本轮没有出现 `1110177/src_tex/gpk_1229.png` 404**（该 URL 这次未被请求）。
- **JS 异常逐条**：`Runtime.exceptionThrown` **0 条**；evaluate 级 `exceptionDetails` **0 条**；控制台错误仅上面那条 favicon（零观测注入空跑同样为 0 条异常）。

## 2. 运行时绑定 —— **部分切片（WARN）**
清单侧（页内 fetch `viewer.json`）：**nodes 89、`renderable_by_adapter===true` = 11**（6→11 ✅），5 条新绑定字段：
| 节点 | `texture_candidate` | `texture_status` | `spr_sheet` | `spr_frames` 帧数 |
|---|---|---|---|---|
| `H_p_闪电` | `lightning07_cs__atlas207659.png` | `verified_by_spr_sibling_pairing` | 512×512 | **16** |
| `H_ shandian01_1_1` | `lightning_01__atlas207671.png` | 同上 | 512×512 | **16** |
| `M_lizi_闪电_01` | `shandian_05_yh_djs__atlas207712.png` | 同上 | 256×256 | **4** |
| `H_p_烟雾_02` | `smoke25__atlas208478.png` | 同上 | 512×512 | **64** |
| `H_鬼火_星点_1` | `tex_special_fangkuai_tp52__atlas211384.png` | 同上 | 256×256 | **4** |
运行时（`__sfxDiag().particles[]`，原文摘录）：
```
H_p_闪电          sheet[512,512] sliced_frames 16 frame_index_last 15  alive 0/2  rate=10
H_ shandian01_1_1 sheet[512,512] sliced_frames 16 frame_index_last  5  alive 1/3  rate=5
M_lizi_闪电_01    sheet[256,256] sliced_frames  4 frame_index_last  3  alive 0/2  rate=3
H_p_烟雾_02       sheet[512,512] sliced_frames  0 frame_index_last null alive 1/1  fallback="source_rate_missing" rate=absent
H_鬼火_星点_1      sheet[256,256] sliced_frames  0 frame_index_last null alive 1/1  fallback="source_rate_missing" rate=absent
```
- **"单个粒子只显示 1 帧"——对闪电族 3 个节点成立** ✅：`sliced_frames` = 16/16/4（= 图集格子数），且**帧索引随时间推进**（同一节点 `H_p_闪电`：t=0.08 idx **0** → t=0.14 idx **3** → t=0.30 idx **7**；`H_ shandian01_1_1`：t=1.15 idx **4** → t=1.20 idx **6**；`M_lizi_闪电_01`：idx 2 → 3）⇒ 每帧只取图集一格，不是整张图集。
- **⚠ 另 2 个节点未切片**：`H_p_烟雾_02` 与 `H_鬼火_星点_1` 运行时 `sliced_frames=0`（图集已绑、节点 alive），并带 `fallback="source_rate_missing"`（该二者源 `.sfx` 无 `ParticlesPerSecond` ⇒ 走回退路径）。**未切片是否存在"整张图集当一帧"的风险，见 §3 目视结论（本组截图上未见格阵）。**
- `__probe()`：`models 42 / modelTable 42 / sprites 3 / systems 20 / modelsOn:false`。

## 3. 目视（≥7 张 N≥5 稳定帧；我给 6× 放大对照图）+ 诚实边界
稳定帧（`gate_ok=true` 全部，rect 已复核）：
| 源时间 t | 帧 sha16 | `alive_now` | 可见节点数 | 掩模白像素占比 |
|---|---|---|---|---|
| 0.04 | `0537a1cc918f25d4` | 3 | 3 | 0.68% |
| 0.08 | `33305388f5707eaa` | 4 | 4 | 0.68% |
| 0.14 | `e4d4fb88e5b660b1` | 4 | 4 | 0.68% |
| 0.22 | `7fe308bd643ce6ec` | 6 | 4 | 0.68% |
| 0.30 | `f0479d42813d800d` | 6 | 6 | 0.68% |
| 1.15 | `40554a2b3676e2aa` | 9 | 9 | 0.69% |
| 1.20 | `bd7e32a9ca6cbe23` | 10 | 9 | 0.66% |
（放大对照图在 `sfx_verify_shots/`：`zoom_t0xx.png` = OFF|ON 三窗口 6× 并排；`crop_t0xx_vs_off.png` = 全效果区 3×。）
**我亲眼看（6× 放大）**：
1. **闪电/放电弧**：**有，但很细弱** —— t=0.30 帧上能看到**极细的淡青色折线/斜向丝状痕迹**（像细电弧/放电丝，单条约几十像素），**没有粗壮的分叉闪电或明显"放电弧"**；t=1.20 帧上闪电族节点 alive 但只在剑刃附近留下极小淡痕。⇒ **我无法从截图上确认"明显闪电形状"**（可能与粒子尺寸 0.5–1.5 单位、透明度低有关），**如实报**。
2. **烟雾团**：**未观察到明显的烟雾团**。`H_p_烟雾_02` 运行时 alive=1 但 `sliced_frames=0`（见 §2）；放大图上只有极淡的絮状痕迹。⇒ 该项 **未能确认**。
3. **发光方块**：**有** —— t=1.20 帧上出现**一个小的黄绿色亮点/方块**（`H_鬼火_星点_1`），位置在剑刃上缘附近；尺寸很小（十几像素）。
4. **整张图集当一帧 / 糊成一坨 / 全黑全白**：**均未观察到** ❌（即没有这些坏形态）—— 放大图上**没有 4×4 / 8×8 格阵**，没有大块白/黑，掩模内白像素占比 **0.66–0.69%**（与默认态 0.677% 持平），画面也没有糊团；效果整体**新增面积极小**（t=1.20 相对默认帧差异 4,073 px ≈ **0.29% 画布**）。

## 4. 与改前基线对比 —— 多出来了什么
| 项 | 改前 | 改后（本轮实测） |
|---|---|---|
| `1110177/effects.json` | `2acca552a6f0d1e0` | **`4696FF22F57966B2`** |
| `1110177/viewer.json` | `8748780e7bd3fb2b` | **`789897E94A81908D`** |
| 可渲染节点 | 6 | **11** |
| 3 个闪电节点（`H_p_闪电`/`H_ shandian01_1_1`/`M_lizi_闪电_01`） | `REJECTED_wrong_image(fail_closed,不顶替)`、`texture_candidate=null` ⇒ **完全不渲染** | 绑定真图集、`sliced_frames 16/16/4`、**运行中确实出现**（`alive_now` 峰值 10、逐帧索引推进） |
| 画面增量 | — | 剑刃附近**细小淡青折线/丝状痕迹 + 零散白色/黄绿色小亮点**；**没有**白块、糊团、格阵 |

## 5. 回归（另 6 皮肤默认页）—— **PASS**
| 皮肤 | `__neox()` | SFX 按钮默认态 |
|---|---|---|
| 1110024 | applied **5 == 5**、failed 0、missing 0、env_warn null、pending 0 | `SFX 关闭`（disabled=true） |
| 1110129 | applied **5 == 5**、0 / 0 / null / 0 | `SFX 关闭`（disabled=true） |
| 1110145 | applied **7 == 7**、0 / 0 / null / 0 | `SFX 关闭`（disabled=true） |
| 1110152 | applied **2 == 2**、0 / 0 / null / 0 | `SFX 关闭`（**disabled=false**，pressed=false） |
| 1110165 | applied **4 == 4**、0 / 0 / null / 0 | `SFX 关闭`（disabled=true） |
| 1110171 | applied **7 == 7**、0 / 0 / null / 0 | `SFX 关闭`（**disabled=false**，pressed=false） |
- **SFX 默认关**：6/6 `pressed="false"`、文案 `SFX 关闭` ✅（4 个皮肤无 effects 配置故按钮 disabled，2 个可用但默认关）。
- **文件 sha16 未变清单**：`viewer.js` / `adapter` / `board.html` / `1110171/viewer.json` / `1110177/neox_material.json` **全部 true**；`1110177/viewer.json`+`effects.json` 为本轮**预期新值**（见 §4）——开工前后两次哈希一致（`pins_unchanged` 全 true）。
- 关 SFX 后重新门控 OFF = 默认 OFF `e62c1c58e5bdc383`（逐字节一致）✅。

## 6. 诚实边界（我主动报的两条）
1. **形状细弱**：闪电族节点在屏幕上只有**极细的淡青折线/丝状痕迹**，**不能确认"明显闪电分叉"**；烟雾节点**看不到明显烟雾团**。若用户期望"一眼看到闪电/烟雾"，当前尺寸/不透明度可能不足 —— **这属于观感判据，请 Lead 裁决**（数据侧绑定与切片是对的）。
2. **`H_p_烟雾_02` / `H_鬼火_星点_1` 未切片**（`sliced_frames=0` + `fallback=source_rate_missing`）：图集已绑、节点 alive，但**没有按 64/4 帧切片**的运行时读数；本组截图上**未见格阵**（即没有明显"整张图集当一帧"），但**这两条的"单帧显示"我无法用运行时读数证明**（只能证否"格阵出现"）。建议下一步给这两条补切片路径或说明回退语义。
3. 本轮的 5 条绑定证据 = **结构 + 尺寸 + 目视**三重（非内容指纹直证，与你 task 里写的一致）。

## 7. 纪律与产物
- 只读 `08Lifeafter wiki/assets/**`（未改任何文件，见 §5 未变清单）；单浏览器 `FXVAA65_prof` / 端口 **10121**；结束按 `user-data-dir` 反查真实 PID `taskkill /T /F`（8 个进程）；**端口 10121 无 LISTEN**、我的 profile chrome = 0。
- 产物：本报告 + `SFX_1110177_browser_verify_20260919.json`；截图目录 `sfx_verify_shots/`（`main_default_off.png`、`main_bg.png`、`shot_t*.png` 7 张稳定帧、`crop_t*_vs_off.png` 3× 对照、`zoom_t*.png` 6× 三窗口对照）。
