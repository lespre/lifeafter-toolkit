# task-90v 终验：`COLOR_ORDER=argb` / `COLOR_TRACK_PAR` / `blendOf` 三处补丁 —— 浏览器实测 A/B + 负控

**结论速览：PASS 4 · WARN 2 · FAIL 2 · unresolved 1**

| # | 项 | 判定 |
|---|---|---|
| A | 页内字节自证（adapter 108,517 B / `A2DE92CB9E5CF4C6`；board `7BE7638389715FD3`） | **PASS** |
| **补丁①** | `COLOR_ORDER` 默认 `'argb'` **在画面上完全没生效** | **FAIL** |
| B | 1110177 默认态四帧：par 生效但**极局部**，且**不是"更暖/更金"** | **WARN** |
| C | 负控 `colorTrackPar(false)` 逐字节回补丁前 | **PASS**（附 1 条参照物不一致） |
| D | 1110171 三态（argb+par / rgba+par / rgba+nopar） | **三态逐字节完全相同** |
| **补丁③** | `blendOf` 结构级已生效（未收录值不再落 additive） | **PASS(结构级)** |
| E | 7 皮肤回归 | **PASS** |
| F | 开关往返 | **PASS** |
| G | 最终 pin | **PASS** |
| — | 1110171 的 4 个 Sprite 为何像素贡献为 0 | **unresolved** |

---

## 0. 一句话结论（给人看）

- **补丁①（`COLOR_ORDER` 默认改 argb）与补丁②（par 优先）在 1110171 上都没有可见效果，补丁① 连 1110177 上也没有效果 —— 原因是 adapter 里有一个作用域遮蔽 bug**：
  `assets/weapon_skin_sfx_adapter.js` **L96**（模块级）`var COLOR_ORDER = 'argb';` 被 **L278**（`attach()` 函数内）`var COLOR_ORDER = 'unproven:[A,R,G,B]';` **遮蔽**。精灵路径（L836）与模型 `mdlRGB()`（L239）读的是 **L278 那个局部变量**，而公开 API `colorOrder(...)`（L1124）改的是 **L96 那个模块级变量** ⇒ 开关**只改报告、不改画面**（实测：切 `colorOrder('argb')`→`'rgba'`→`'argb'` 帧逐字节相同）。
- **补丁②（par 优先）确实生效**，但只在 t=0.30 与 t=1.15 两个冻结时刻改变了画面，且变化**极小、极局部**（702 px = 画布 0.049%，逐通道 2751 px，最大差 55/255），方向是**略暗、去青**，**不是**任务预期的"更暖/更金"。t=0.10 与 t=0.55 **逐字节没变**。
- **补丁③（blendOf）结构上已落地**，但这两个皮肤里没有 `blend_mode ∈ {3,6}` 的可见节点 ⇒ 新分支**在画面中没有被触发**。
- **负控 `colorTrackPar(false)` 完美通过**：四帧与 task-93 记录的四个 sha **逐个相同**，往返也回到默认帧。

---

## A. 页内字节自证（浏览器里 `fetch` 的实字节）

| 对象 | 页内 status | bytes | sha16（页内实算） | 期望 | 判定 |
|---|---|---|---|---|---|
| `assets/weapon_skin_sfx_adapter.js` | 200 | **108,517** | **`A2DE92CB9E5CF4C6`** | `A2DE92CB9E5CF4C6` | ✅ |
| `board.html` | 200 | 108,748 | **`7BE7638389715FD3`** | `7BE7638389715FD3` | ✅ |
| `assets/weapon_skin_viewer.js` | 200 | 379,489 | `B9C7281E1EE7A819` | `B9C7281E1EE7A819` | ✅ |
| `1110177/effects.json` | 200 | 673,513 | `140E27ABB3E40694` | `140E27ABB3E40694` | ✅ |
| `1110177/viewer.json` | 200 | 714,717 | `BF7288193E092AA2` | `BF7288193E092AA2` | ✅ |
| `1110171/effects.json` | 200 | 219,705 | `2B0127E574A32CBD` | `2B0127E574A32CBD` | ✅ |
| `1110171/viewer.json` | 200 | 248,580 | `4D6CAE69DCE8CFC9` | `4D6CAE69DCE8CFC9` | ✅ |
| `1110177/neox_material.json` | 200 | 48,811 | `A05C4F2C8DDFCF9A` | `A05C4F2C8DDFCF9A` | ✅ |

- `board.html` 的 `?v=` 集合：`["06efcf4469a8","20260913","7ee9dbaa765c","9c3b9c3eb04c","a2de92cb9e5cf4c6","b9c7281e1ee7","ec7cf93a17f7","f921edf44d09"]` ⇒ **含 `a2de92cb9e5cf4c6`** ✅
- 磁盘 pin 与页内哈希**一致**；`pins_unchanged` **16/16 true**（开工=收尾）。
- ⇒ **A 判定：PASS。拿到的确实是新版本。**

---

## 1. 补丁①（`COLOR_ORDER` 默认 argb）：**FAIL —— 画面完全没变**

### 1.1 源码级证据（作用域遮蔽）

| 行号 | 代码 | 作用域 |
|---|---|---|
| L96 | `var COLOR_ORDER = 'argb';` | **模块级**（`colorOrder()` / `adaptSwitches()` / `__sfxDiag()` 读它） |
| L278 | `var COLOR_ORDER = 'unproven:[A,R,G,B]';` | **`attach()` 函数内局部**（var 提升 ⇒ 遮蔽 L96） |
| L836 | `if (col && COLOR_ORDER === 'rgba') { col = [col[3],col[0],col[1],col[2]]; }` | 精灵路径 → 读 **L278 局部**（恒 `'unproven…'` ⇒ **恒等于旧行为**） |
| L239 | `if (COLOR_ORDER === 'argb') { r=col[1];… }` （`mdlRGB`） | 模型路径 → 同样被 L278 遮蔽 |
| L1124 | `WikiSfxAdapter.colorOrder = function (m) { … COLOR_ORDER = m; … }` | 只改 **L96 模块级** |

⇒ `colorOrder('argb')` 只能改"报告字段"，**永远到不了渲染代码**。

### 1.2 运行时证据

| 探针 | 读数 |
|---|---|
| `attached` 期 `__audit.colorOrder` | **`"unproven:[A,R,G,B]"`**（不是 `argb`） |
| `__sfxDiag().color_order` | **`"unproven:[A,R,G,B]"`** |
| `adaptSwitches().colorOrder` | **`"unproven:[A,R,G,B]"`** |
| `colorOrder('argb')` → 帧 sha | `30f0a9dcf6fdf7ec` |
| `colorOrder('rgba')` → 帧 sha | `30f0a9dcf6fdf7ec`（**同一冻结帧 t=0.30，N≥5 门通过**） |
| `colorOrder('argb')` → 帧 sha | `30f0a9dcf6fdf7ec` |
| 三帧严格逐字节 diff | **0 px** |
| 切到 `'rgba'` 后 `__audit.colorOrder` | **仍是 `"unproven:[A,R,G,B]"`**（没被改到） |

### 1.3 顺带确认（与 Q1 预期一致，但**不是**因为补丁）

- 1110177 的 5 个可见节点**全是 ParticleSystem**。粒子路径 **L764-765 写死 `alpha=col[0]`、`RGB=col[1..3]`**（本来就是 argb，与 `COLOR_ORDER` 无关）⇒ 补丁① 对 1110177 **结构上就不该有影响**，实测一致（帧没变）。
- 1110171 的 4 个是 **Sprite**，本应受补丁① 影响 —— **实测一像素都没变**（见 §3）。

> **⇒ 补丁① 判定 FAIL：默认值改了、消费者没改到。需要 Lead 处理。**

---

## 2. B. 1110177 默认态改后读数（四个冻结时刻，N≥5 稳定门全过）

口径与 KINVEL 报告一致：`MASK` = 帧 vs 背景（同会话 `__primShow(-1)` 隐藏全部 prim）的差异区，阈值 24/255；`p50/p95` = 该区内 Rec.709 亮度分位；`暖色%` = 区内 `R>0.9 且 G>0.85` 占比；`>0.5%/>0.75%` = 区内亮度超阈占比。

| t | 状态 | sha16 | p50 | p95 | >0.5% | >0.75% | 暖色% | 白像素%（区内） | mask% | 存活粒子 | 门 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.10 | **默认(argb+par)** | `2F1D02498AEF6C5B` | 0.2838 | 0.5745 | 18.284 | 0.989 | 0.689 | 0.677 | 1.826 | 6 | 5/5 ✅ |
| 0.10 | par 关（=补丁前） | `2F1D02498AEF6C5B` | 0.2838 | 0.5745 | 18.284 | 0.989 | 0.689 | 0.677 | 1.826 | 6 | 5/5 ✅ |
| 0.30 | **默认(argb+par)** | **`10C9E772453B595F`** | 0.2860 | 0.5745 | 18.247 | 0.993 | 0.690 | 0.678 | 1.833 | 13 | 5/5 ✅ |
| 0.30 | par 关（=补丁前） | `A3E63C2FBB3DFA8C` | 0.2870 | 0.5745 | 18.319 | 0.995 | 0.685 | 0.674 | 1.836 | 13 | 5/5 ✅ |
| 0.55 | **默认(argb+par)** | `6C2C384ED52D62BD` | 0.2829 | 0.5745 | 18.271 | 0.988 | 0.685 | 0.673 | 1.827 | 7 | 5/5 ✅ |
| 0.55 | par 关（=补丁前） | `6C2C384ED52D62BD` | 0.2829 | 0.5745 | 18.271 | 0.988 | 0.685 | 0.673 | 1.827 | 7 | 5/5 ✅ |
| 1.15 | **默认(argb+par)** | **`DBB1D3A10387BC06`** | 0.2829 | 0.5745 | 18.242 | 0.989 | 0.689 | 0.677 | 1.826 | 7 | 5/5 ✅ |
| 1.15 | par 关（=补丁前） | `61C1E08B18B9F921` | 0.2829 | 0.5745 | 18.238 | 0.988 | 0.688 | 0.677 | 1.827 | 7 | 5/5 ✅ |

**逐帧改前/改后差分（严格逐字节，thr=0）**

| t | 默认 vs par 关：逐字节差 | 其中 >6/255 的像素 | max 逐通道差 | 变化区 bbox |
|---|---|---|---|---|
| 0.10 | **0 px** | 0 | 0 | — |
| 0.30 | **2,751 px**（画布 0.193%；>6/255 计 **702 px** = 0.0493%） | 702 | 55/255 | [768,841,414,485]（58×40 @2x 区域） |
| 0.55 | **0 px** | 0 | 0 | — |
| 1.15 | **53 px**（0.0037%；>6/255 计 **26 px**） | 26 | 25/255 | [833,840,402,408] |

**变化方向（只统计变化区，t=0.30）**：
- 默认 变化区 meanRGB = **(0.138, 0.224, 0.207)**；par 关 = **(0.130, 0.244, 0.227)**
- Δ(默认−par关) = **(+0.008, −0.020, −0.020)**，Δ亮度 = **−0.0141** ⇒ **更暗、更少青**
- 暖色占比：默认 **0.07%** vs par 关 0.04%（**都不是"更金"**；这是"变化区内"口径，全帧 `MASK` 口径下是 0.690% vs 0.685%，见上表）
- 整幅 meanL：默认 **0.17320** vs par 关 0.17323（几乎不变）；`n(L>0.9)` 2310 vs 2311

### 我亲眼看到的（人话描述）

1. **`c177_zoom5x_default_paroff_diffx10_t0030.png`**（5 倍放大：左=默认、中=par关、右=|差|×10）：
   画面是**极光剑的枪口/剑身中段**——底色是暗青绿，剑脊是暗金/褐金色，剑身带一圈细白高光。
   中幅（par 关）在这个区域里那一小簇**青绿色的电花/雾团更亮更实**（能看出块状的青绿光斑）；左幅（默认）
   同一处的**青绿光更薄、更暗**，能透出后面剑身的暗金褐色。右幅差异图把差别画成一圈**环绕剑脊的细白描边 + 两块光斑**，
   说明差异**只发生在那一小片光环上**，不是整幅。
2. **`c177_side2_default_left_paroff_right_t0030.png`**（2 倍并排，外扩 253×251）：同一结论——
   par 关（右）剑脊中段的青绿光团**更亮更清晰**；默认（左）**更弱**、剑身的暗金褐色透出来更多。
   剑柄/护手上的**红斑、白高光完全一样**。
3. **`c177_side2_default_left_paroff_right_t0115.png`**（t=1.15）：两幅几乎完全一样，只在剑脊靠上一处
   有**极小的一点青绿色差**（53 px），肉眼几乎不可辨。
4. **没有任何异常**：没有全黑、没有纯色块、没有过曝白团（整幅白像素 2310→2311，meanL 0.17320 vs 0.17323）。

### 对"是否变成源 ramp"的回答

**是"用了 ramp 数据"，但视觉上不是"更暖/更金"**，原因在数据本身（`effects.json` 实测）：

| 节点 | `color_track`（编辑器默认常数，单键） | `color_track_par`（真 ramp） | argb 下首帧语义 |
|---|---|---|---|
| `H_p_闪电` | `[255,92,243,107]` | 5 键 `[255,255,248,224]→[198,255,234,159]→[176,255,204,87]→[127,255,194,64]→[127,138,130,255]` | α=255，RGB(255,248,224) 暖白 → 中段转**青绿** |
| `H_ shandian01_1_1` | 同上 | 4 键 `[0,191,148,110]→[236,26,20,13]→[191,9,6,3]→[0,0,0,0]` | **α=0**（列0=0）⇒ 首键完全透明 |
| `M_lizi_闪电_01` | 同上 | 8 键 `[0,255,212,154]→[255,255,188,102]→…→[45,255,154,60]` | α 在 0↔255 间跳 |
| `H_p_烟雾_02` | 同上 | **无 par**（`null`） | 仍用默认常数 |
| `H_鬼火_星点_1` | 同上 | **无 par**（`null`） | 仍用默认常数 |

⇒ 这 3 条 ramp 的主导色相是**青绿/青白**（不是金），而且它们被 `alpha` 通道强门控（`H_ shandian01_1_1` 首键 α=0）
⇒ **默认比补丁前更暗、更少青**，暖色占比几乎不动。**任务预期的"更暖/金"没有出现**；这是
"用对了字段但源数据本身不是金"的结果，不是调参问题。

> **⇒ B 判定：WARN（补丁②生效但可见幅度极小、且与预期方向不符）。**

---

## 3. C. 负控：`colorTrackPar(false)` 是否逐字节回补丁前

| t | 补丁前（task-93 记录） | 本轮 `colorTrackPar(false)` sha16 | sha 相同？ | 与 `sfx_verify_shots10/r177_t*.png` 的 PNG 级差 |
|---|---|---|---|---|
| 0.10 | `2f1d02498aef6c5b` | **`2f1d02498aef6c5b`** | ✅ 相同 | 602 px（max 132/255） |
| 0.30 | `a3e63c2fbb3dfa8c` | **`a3e63c2fbb3dfa8c`** | ✅ 相同 | 5,780 px（max 194/255） |
| 0.55 | `6c2c384ed52d62bd` | **`6c2c384ed52d62bd`** | ✅ 相同 | 5,665 px（max 80/255） |
| 1.15 | `61c1e08b18b9f921` | **`61c1e08b18b9f921`** | ✅ 相同 | 50 px（max 15/255） |

- **四个 sha 与 task-93 记录逐个逐字节相同**（N≥5 稳定门全过）；往返 `colorTrackPar(true)` 回到默认帧，`diff = 0 px`（四个 t 全部 0 px）。
- **没有出现任务担心的回归**：`argb` 默认与 `blendOf` 都没有意外改动粒子路径行为（事实上 `argb` 默认根本没生效，见 §1）；`blendOf` 在这些节点上输出的仍是 `normal`（与旧默认一致）。
- ⚠ **参照物不一致（如实登记）**：`sfx_verify_shots10/r177_t0010.png` 等 4 张**不是**这四个 sha 对应的帧
  （mtime 11:43–11:44，与 task-93 记录的 sha 不符；PNG 级差 602/5780/5665/50 px）。
  因此 **task-93 报告里 `off_diff_vs_task88_png = 0 px` 这一条我无法在本轮复核**（它的 PNG 载体与 sha 记录互相矛盾）。
  另：SFX 关锚与背景锚**是**逐字节相同的（`c177_off` vs `r177_off`、`c171_off` vs `s171_off`、两侧 bg 均 **0 px**）⇒ 只有"冻结帧"那 4 张旧 PNG 对不上。
  ⇒ 这**不影响**本轮负控结论（我用的是 sha 记录，且逐帧吻合）。

> **⇒ C 判定：PASS（负控逐字节通过 + 往返通过）；附 1 条参照物不一致，建议 Lead 裁决是否作废旧 PNG。**

---

## 4. D. 1110171 三态（`argb`+par / `rgba`+par / `rgba`+nopar）

同一载入、同一冻结时刻 **t=0.55**、同一背景，N≥5 门全过：

| 态 | 调用 | 帧 sha16 | mask% | 差异像素（严格 thr=0） | `__sfxDiag().color_order` | 亲眼 |
|---|---|---|---|---|---|---|
| S1 默认 | 无（默认态） | **`48B6C95C1165C80A`** | 2.449 | — | `unproven:[A,R,G,B]` | 见下 |
| S2 | `colorOrder('rgba')` | **`48B6C95C1165C80A`** | 2.449 | **S1 vs S2 = 0 px** | `rgba` | **与 S1 像素完全相同** |
| S3 | `colorOrder('rgba')` + `colorTrackPar(false)` | **`48B6C95C1165C80A`** | 2.449 | **S1 vs S3 = 0 px**，**S2 vs S3 = 0 px** | `rgba` | **与 S1/S2 像素完全相同** |
| S1b 往返 | `colorOrder('argb')`+`colorTrackPar(true)` | **`48B6C95C1165C80A`** | 2.449 | vs S1 = **0 px** | — | 同 |

- 四态 sha16 **完全相同**、严格逐字节 **diff = 0 px**。
- 关键旁证（证明"开关确实改了数值、只是没改画面"）：`__sfxDiag()` 逐 sprite 的 `opacity`
  在 S1=**0.0903**、S2/S3=**0.2475**（比值 0.3648）。这个比值 = `93/255 = 0.3647`，
  正是 `effects.json` 里 `M_g_光晕亮_01` 的 `color_track` 值 **`[93,48,113,255]`** 在**默认(argb)**下取
  **列0=93** 当 alpha、而显式 `'rgba'` 下取 **列3=255** 当 alpha 的结果。
  ⇒ **默认态在精灵路径上确实是 argb 语义**（=预期），但**画面照样一点不变**。

### 亲眼看到的（人话描述）

- **`c171_three_state_labeled_t0055.png`**（三态并排，2 倍放大，同一裁剪区）：三幅**看起来一模一样**——
  一把**银白/浅金羽刃状**的剑（深青绿底、深色背景），剑体中段有一小片**青绿色微光**、以及几处细白高光；
  三幅之间**看不出任何差别**（没有哪一态更红/更蓝/更亮/更暗）。
- 对应地，**无法**用"哪一态更像源节点名"作判据：三态帧是同一个字节流，没有可分辨的现象。
  源节点名是 `M_g_光晕暗_01/亮_01/暗_02/亮_02`、贴图 `glow40_tp30.tga` / `glow_gyun_01_smg.tga`（glow 光环），
  但**这三个开关组合没有在画面上留下任何可辨差异**，所以"更像光环"这个判断在本轮**无从谈起**。

### 附带发现（unresolved，登记给 Lead）

`__probe()` 显示 1110171 的**2 个可见 sprite**（`M_g_光晕亮_01/02`）状态是：
`ready:true, visible:true, hasMap:true, opacity:0.0903→0.2475`（alpha 变了 2.74×）、
`scale:0.48`（世界单位）、`worldPos:[-0.043, 0, 0.145]`（**两个都在同一位置**，groupWorldPos=[0,0,0]）。
在加法混合下 opacity 变化 2.74× 通常会改变画面，但**实测 0 px** ⇒ 这 2 个 sprite 在**本相机、本冻结时刻对画面零贡献**。
- 另外 2 个（`M_g_光晕暗_01/02`）`visible:false, opacity:0`（`FxIgnore`/时间窗所致）。
- **判定：unresolved**（我只有"像素贡献为 0"这一实测事实，**没有**定位到原因：可能是它们被画在
  剑体内部被遮挡、或贴图在加法混合下贡献 < 1/255、或渲染被别处覆盖）。**本轮不猜。**

> **⇒ D 判定：三态逐字节相同（=补丁① 在 1110171 上零效果）；`M_g_光晕亮_01/02` 为何零贡献 unresolved。**

---

## 5. 补丁③（`blendOf`）：结构级已生效，画面未触发

**源码级**：`blendOf` 是**模块级函数（L250）**，与 `BLEND`（L246）同作用域、**没有被遮蔽**；
三个旧调用点（L470 / L637 / L882）已全部换成 `blendOf(...)`；`BLEND[x] || 'additive'` 写法**已消失**。
- `BLEND` 表：`{0:'normal', 2:'additive', 5:'additive', 7:BLEND7, 8:'additive'}`；`BLEND7 = 'normal'`。
- `blendOf(v)`：`null/undefined ⇒ 'additive'`（未改）；数值型未收录（3/6）⇒ `BLEND7`（=normal）。

**运行时读数**（`__sfxDiag()`）：

| 皮肤 | 节点 | 源 `blend_mode` | `blend_mode_used` |
|---|---|---|---|
| 1110177 | `H_p_闪电` / `H_ shandian01_1_1` / `M_lizi_闪电_01` / `H_p_烟雾_02` / `H_鬼火_星点_1` | 见源（含 7） | 全 **`normal`**（5/5） |
| 1110171 | `M_g_光晕暗_01` / `M_g_光晕暗_02` | 非 7 | **`normal`** |
| 1110171 | `M_g_光晕亮_01` / `M_g_光晕亮_02` | 2 或 5 | **`additive`** |

- ⇒ 数值型未收录值不再落 additive；`7` 仍是 `normal`（与旧默认一致）。
- ⚠ **诚实边界**：这两把皮肤里**没有 `blend_mode ∈ {3,6}` 的可见节点** ⇒ `blendOf` 的**新分支在画面中没有被触发**，
  我只能给到"函数已接线 + 现有节点读数与旧默认一致"的**结构级**验证，**不能**给"未收录值不再发白"的画面级证据。

> **⇒ 补丁③ 判定：PASS（结构级；画面级未触发，登记）。**

---

## 6. E. 7 皮肤回归

全部经 `window.WikiWeaponViewer.open(record)` → settle 门（`applied 非空 且 pending=0 且 env_warn∈{0,null}`）：

| 皮肤 | `applied` | `expected` | `applied==expected` | prims | failed | missing | env_warn | pending | SFX 默认 | `window.__errs` |
|---|---|---|---|---|---|---|---|---|---|---|
| 1110024 | 5 | 5 | ✅ 5/5 | 5 | 0 | 0 | null | 0 | 关（按钮 disabled，text「SFX 关闭」） | `[]` |
| 1110129 | 5 | 5 | ✅ 5/5 | 5 | 0 | 0 | null | 0 | 关（disabled） | `[]` |
| 1110145 | 7 | 7 | ✅ 7/7 | 7 | 0 | 0 | null | 0 | 关（disabled） | `[]` |
| 1110152 | 2 | 2 | ✅ 2/2 | 2 | 0 | 0 | null | 0 | 关（enabled，未按下） | `[]` |
| 1110165 | 4 | 4 | ✅ 4/4 | 4 | 0 | 0 | null | 0 | 关（disabled） | `[]` |
| 1110171 | 7 | 7 | ✅ 7/7 | 7 | 0 | 0 | null | 0 | 关（enabled，未按下） | `[]` |
| 1110177 | 3 | 3 | ✅ 3/3 | 3 | 0 | 0 | null | 0 | 关（enabled，未按下） | `[]` |

- **SFX 默认关 7/7**（`aria-pressed="false"`，text「SFX 关闭」）✅
- `failed=[]`、`missing=[]`、`env_warn=null`、`pending=0` ✅
- **`window.__errs=[]`（7/7 皮肤页面，外加两轮开关往返）** ✅；CDP `Runtime.exceptionThrown` = **0 条**；`Runtime.evaluate` 异常 = **0 条**
- **全页 404 只有 1 条：`http://127.0.0.1:8765/favicon.ico`** ✅
- 网络：**GLB 7 条全 200**、**sfx/src 贴图 79 条全 200**、4 条 js（含带 `?v=` 的 adapter/viewer）全 200 ✅

> **⇒ E 判定：PASS。**

---

## 7. F. 开关往返

| 调用 | 返回值 | `adaptSwitches()` 同步读数 | `__errs` |
|---|---|---|---|
| `colorTrackPar(true)` | `{colorTrackPar:true, rule:'par_if_nonempty_else_color_track'}` | `colorTrackPar:true` | `[]` |
| `colorTrackPar(false)` | `{colorTrackPar:false, …}` | `colorTrackPar:false` | `[]` |
| `colorTrackPar(true)` | `{colorTrackPar:true, …}` | `colorTrackPar:true` | `[]` |
| `colorOrder('argb')` | `{colorOrder:'argb'}` | `colorOrder:'argb'` | `[]` |
| `colorOrder('rgba')` | `{colorOrder:'rgba'}` | `colorOrder:'rgba'` | `[]` |
| `colorOrder('argb')` | `{colorOrder:'argb'}` | `colorOrder:'argb'` | `[]` |

最终态：`{spriteFix:true, clampOn:true, clampK:0.6, psFallbackOn:true, spriteOn:null, blend7:"normal", honorFxIgnore:true, colorOrder:"argb", colorTrackPar:true, spriteClampNeverTriggered_13nodes:true}`；`__errs={n:0}`。

- ⚠ 附带登记：**在页面刚载入、adapter 尚未 `attach` 之前**调用 `adaptSwitches()/colorOrder()/colorTrackPar()`
  会抛 `TypeError: … is not a function`（`window.WikiSfxAdapter` 对象先注册、这些方法在脚本后段才挂）。
  这是既有行为、不影响渲染；我把它作为"调用时机"提示登记（我的首轮读数里出现过 3 条，均在 attach 前）。

> **⇒ F 判定：PASS。**

---

## 8. G. 最终 pin 表（开工 = 收尾，`pins_unchanged` 16/16 true）

| 对象 | sha16 |
|---|---|
| `assets/weapon_skin_sfx_adapter.js` | **`A2DE92CB9E5CF4C6`**（108,517 B） |
| `board.html` | **`7BE7638389715FD3`**（108,748 B，`?v=a2de92cb9e5cf4c6`） |
| `assets/weapon_skin_viewer.js` | `B9C7281E1EE7A819`（379,489 B） |
| `1110177/effects.json` / `viewer.json` | `140E27ABB3E40694` / `BF7288193E092AA2` |
| `1110171/effects.json` / `viewer.json` | `2B0127E574A32CBD` / `4D6CAE69DCE8CFC9` |
| `1110177/neox_material.json` | `A05C4F2C8DDFCF9A` |
| 5 张真图集（1110177） | `DBC4D2E4FE65FF4F` / `DDE58C1EB420384F` / `BAB99D2E79746152` / `45AE45AB090353CB` / `37FA4BE63541FFAB` |
| `tex_glow_tp07_02__atlas207414.png`（1110171） | `6480F7FC1914F0C4` |
| 3 个 GLB（1110171，任务点名） | `mod_skin_1003_010_zs_ql07_djs.glb` = `A4EA1EC706F7E71C`、`mod_skin_1003_012_zs_qiu03_djs.glb` = `21A1F52546D0CD12`、`mod_skin_1003_012_zs_qiu04_djs.glb` = `B9E06158D88FBBD1` |
| （附加）1110171 `sfx/*.glb` **全量 28 个** + 两张皮肤 `sfx/tex/*.png` **全量 135 张** | 见 JSON `supplement.glb_all_1110171` / `supplement.atlas_all` |

---

## 9. 纪律与产物

- **只读 `08Lifeafter wiki/**`**：未改/建/删任何 wiki 文件（`pins_unchanged` 16/16 可证）。**没有**改曝光/灯光/bloom/ACES，**没有**调任何参数凑好看。
- 浏览器：**单浏览器**，profile `FXVA94_prof` / `--remote-debugging-port=10159`（补充定证用 `FXVA95_prof` / 10169），
  两次都按 `user-data-dir` 反查真实 PID 后 `taskkill /T /F` **自己的进程树**（各 8 个 PID），**端口 10149/10159/10169 均无 LISTEN**，`FXVA94_prof`/`FXVA95_prof` 的 chrome 进程残留 = **0**；未触碰别人的 headless，未重启 8765 服务（PID 25832）。
- 写入范围：`COLORFIX_verify_20260920.md`、`COLORFIX_verify_20260920.json`、`COLORFIX_probe_20260920.json`、`sfx_verify_shots12/**`；
  两个可复现驱动脚本 `_run_colorfix_verify.py`（主验收）与 `_run_colorfix_probe.py`（补充定证）保留在同一目录（辅助的 `_read_*/_pixdiff_*/_make_eyes_*/_finalize_*/_pin_extend_*` 临时脚本已删除，其读数全部落在上面两份 JSON 里）。
  **未动** `FIDELITY_EVIDENCE_*`、`fidelity/**`、`LA_SOURCE_HUNT_*`、`NAMEHASH_*`、`KINEL_*`、`KINVEL_*`。

### 截图清单（`sfx_verify_shots12/`）

| 文件 | 内容 |
|---|---|
| `c177_t00{10,30,55,115}_{default,paroff,back}.png` | 1110177 四个冻结时刻 × 默认/par关/往返（12 张） |
| `c177_zoom5x_default_paroff_diffx10_t0030.png` | **亲眼主图**：5× 放大 默认｜par关｜\|差\|×10 |
| `c177_side2_default_left_paroff_right_t0030.png` / `…_t0115.png` | 2× 并排（带标注） |
| `c177_colororder_{argb,rgba,argb}_t0030.png`、`c177_co_{argb,rgba}_t0030.png` | 补丁① 零效果的四张证据帧（同 sha） |
| `c177_off.png` / `c177_bg.png`、`c171_off.png` / `c171_bg.png` | SFX 关锚 / 背景（与 task-93 逐字节相同） |
| `c171_S1_default_argb_par_t0055.png` 等四态 + `c171_three_state_labeled_t0055.png` | 1110171 三态（+往返）与并排 |
| `c171_probe_sfxon_t0055.png` | 补充定证的 sprite-on 帧 |

---

## 10. 未做 / 未证（诚实边界）

1. **补丁① 的画面级有效性未证**（并且已证**在浏览器里为 0 效果**）：我只证了"切换 `colorOrder()` 帧逐字节不变 + `__audit.color_order` 恒为 `unproven:[A,R,G,B]`"。我没有在页内绕过遮蔽做 monkey-patch 实拍（那需要注入脚本改页面行为，超出本轮"只读 + 只切公开开关"的口径）。若要做，最干净的验证是 Lead **把 L278 那行删掉/改名**再复测。
2. **`H_p_烟雾_02` / `H_鬼火_星点_1` 的 `color_track_par` 为空**（`null`）⇒ 补丁② 对它们无作用；我未验证"若 par 缺失是否应回落到别的源字段"。
3. **1110171 的 2 个可见 Sprite 为何对画面零贡献 = unresolved**（只有 0 px 的实测事实 + `opacity` 0.0903→0.2475 的旁证；未定位原因）。
4. **`blend_mode ∈ {3,6}` 未在画面中触发**（两皮肤无此可见节点）⇒ 补丁③ 只到结构级。
5. **task-93 的 `off_diff_vs_task88_png = 0 px` 无法复核**（shots10 的 4 张 r177_t*.png 与对应 sha 冲突，PNG 级差 602/5780/5665/50 px）。我按 sha 记录做了负控，结论不受影响，但"旧 PNG 是否作废"需 Lead 裁决。
6. 只做了 **4 个冻结时刻**（0.10/0.30/0.55/1.15）；未做时间轴扫描。补丁② 可能在其它时刻影响更大 —— 若 Lead 要，我可以加 `t∈[0,2]` 步长 0.05 的扫描（同配方，约 20 分钟）。
7. 未做"光源/贴图/渲染管线"层面的归因（本轮只需要判补丁是否生效与是否回归）。

---

## 11. 跑过的命令清单

```
# 环境探测
python -c "import websocket/websockets/PIL/numpy …"                       # 系统 3.12 无这些库
"C:\Users\Administrator\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe" -c "import websockets,numpy,PIL;…"
                                                                          # ⇒ ws 15.0.1 / numpy 2.4.3 / PIL 12.3.0 / py3.11.15（本轮全程用它）
netstat -ano | Select-String ":8765|:10149"                               # 确认 8765 已在跑（PID 25832），未重启
Get-ChildItem "$env:TEMP" -Recurse | Select-String "FXVA93|10149"         # 找到上一轮配方 t93_verify.py
# 主验收（单浏览器 profile FXVA94_prof / 端口 10159，N≥5 稳定门）
& $PY -u E:\la拆包项目\03拆包产物\_target_1110171\_run_colorfix_verify.py
# 补充定证（profile FXVA95_prof / 端口 10169）：colorOrder 逐帧零效果 + sprite 探针
& $PY -u E:\la拆包项目\03拆包产物\_target_1110171\_run_colorfix_probe.py
# 读数汇总 / 严格逐像素 / 亲眼图
& $PY -u E:\la拆包项目\03拆包产物\_target_1110171\_read_colorfix.py
& $PY -u E:\la拆包项目\03拆包产物\_target_1110171\_pixdiff_colorfix.py
& $PY -u E:\la拆包项目\03拆包产物\_target_1110171\_make_eyes_colorfix.py
& $PY -u E:\la拆包项目\03拆包产物\_target_1110171\_finalize_colorfix.py
# 收尾核查
netstat -ano | Select-String "LISTENING" | Select-String ":10159|:10149"  # 空 ⇒ 无 LISTEN
(Get-CimInstance Win32_Process | ? { $_.Name -match 'chrome' -and $_.CommandLine -match 'FXVA94_prof' }).Count  # 0
```
