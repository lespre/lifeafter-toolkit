# 只读冒烟报告（1110177 / 1110171 载入 + SFX 开关 + board 页）

**三档结论：已证 8 条 · 未证 2 条 · 未做 1 条**（末节列出）。**发现 1 个真实缺陷（含根因与一行修法），未改任何文件。**
原始数据：`SMOKE_20260919.json`、`SMOKE_followup_20260919.json`、`SMOKE_followup2_20260919.json`。

## 0. pin（**测量期间三方同时在改文件**，每条读数按此归因）
| 对象 | smoke 起 | smoke 末 | followup 末 | followup2 末 |
|---|---|---|---|---|
| `1110177/viewer.json` | **`1652A648FB602465`** ✅（与 Lead 给的一致） | 同 | 同 | 同 |
| `1110177/effects.json` | `4CE3F4EA6782AE6B` ✅ | 同 | `16B02BA0B3A48247`（被改） | — |
| `1110171/viewer.json` | `62E7BDDC9CF6EC6D` | 同 | 同 | — |
| `weapon_skin_viewer.js` | `75784198127282DC` | `07037554A1F2ACB5` | 同 | **`A8F023D8A8174164`** |
| `weapon_skin_sfx_adapter.js` | **`A19F8B4551DBDE49`**（已不是我交付的 `1CD4AC5454D1F27A`） | 同 | **`F9CBAAA8966659C4`** | 同 |
| `board.html` | `718202FC4D29F603` | 同 | 同 | 同 |

## 1. `__neox()` / `env_warn` / errs（lab=1）
| 皮肤 | applied/expected | failed | missing | `env_warn` 演化 | js 异常 |
|---|---|---|---|---|---|
| **1110177** | **3/3** ✅ | `[]` ✅ | **+3 s：3 个 prim `{slots:['__env_ibl__'],envMode:'ibl_pending'}`** → **+8 s 起 `[]`** | +3 s 非空（3 prim `ibl_pending`, faces 0）→ **+8 / +13 / +21 / +31 s 全为 `null`** ✅ | **0** |
| **1110171** | **7/7** ✅ | `[]` ✅ | +15 s：**prim1 `ibl_pending`** → **+20 s 起 `[]`** | +15 s 非空（prim1）→ **+20 / +27 / +37 s 全为 `null`** ✅ | **0** |

- ⇒ **`env_warn=null` 成立，但要等 settle**：1110177 ≤8 s、1110171 ≤20 s（+3 s 采样时两者都还没好）。**这不是失败**，是新"IBL 就绪门"的 `ibl_pending` 窗口；`missing` 里新增的是伪槽 `__env_ibl__`。
- `window.__errs` / `window.__glowErrors`：**该页未定义**（返回 `null`）⇒ 以 `Runtime.exceptionThrown` 为证：**0 条** ✅。
- console / 404：
  - 1110177：`favicon.ico` 404 + **`src_tex/gpk_1229.png` 404 ×3**（既有，task-46）——**另有 §2 的 5 条特效贴图 404**。
  - 1110171：本轮 **console `[]`、404 `[]`** ✅（早前一轮出现过 3 条 `assets/audio/weapon_skin/jg/*.wav` `ERR_CONNECTION_REFUSED`，环境性）。

## 2. ⚠ 真实缺陷：特效贴图 URL **双前缀** `sfx/tex/sfx/tex/` ⇒ 新 adapter 下 1110177 的 SFX 什么都不画
**证据 1（网络侧，smoke 第一轮实测 404 明细）**：
```
/assets/3d/weapon_skin/1110177/sfx/tex/sfx/tex/lightning07_cs__a8764b3a.png
/assets/3d/weapon_skin/1110177/sfx/tex/sfx/tex/glow_16_yh_djs__7ce99117.png
/assets/3d/weapon_skin/1110177/sfx/tex/sfx/tex/lightning_01__662b911e.png
/assets/3d/weapon_skin/1110177/sfx/tex/sfx/tex/glow_01__13211b02.png
/assets/3d/weapon_skin/1110177/sfx/tex/sfx/tex/dian_12__7240b831.png
```
**证据 2（磁盘侧）**：这 5 个文件**都在** `assets/3d/weapon_skin/1110177/sfx/tex/<name>`（`sfx/tex/` 共 103 个文件）；`sfx/tex/sfx/tex/` **不存在** ⇒ 是**请求路径被拼了两次**。
**证据 3（根因，一行）**：
- 新 `1110177/viewer.json` 的 `effects`：**`assets_base = 'sfx/tex/'`、`textures_dir = ''`（空串）**；
- adapter **L172**：`var baseUrl = abs((effects.assets_base || '') + (effects.textures_dir || 'sfx/tex/'), ctx.manifestUrl);`
  → `textures_dir=''` 是**假值** ⇒ `|| 'sfx/tex/'` 又补一次 ⇒ `…/1110177/sfx/tex/sfx/tex/`。
  **建议修法（我不动手，adapter 现属 task-53 写域）**：把 `||` 改成显式判空，例如
  `var td = (effects.textures_dir === undefined || effects.textures_dir === null) ? 'sfx/tex/' : effects.textures_dir; var baseUrl = abs((effects.assets_base || '') + td, ctx.manifestUrl);`
  （或让 `assets_base` 与 `textures_dir` 二者只保留一个生效。）
**证据 4（渲染后果，followup2 实测）**：SFX 开启后固定时间扫 **t=0.80→1.45 s（14 步）**，与同相位 OFF 帧差分**全部 0.000%**；探针逐步读数：
`M_g_glow_an / H_g_glow地_an / H_公告板_爆闪2` 三个 Sprite **全部 `visible=false, opacity=0, scale=1`**（对比**改前基线**：t=1.175 s 时 `alive=3 / visible=3 / opacity 0.045·0.030·0.232 / quad 6×6·13×13·50×50`、effect-only **38.08%** 画布）。
⇒ **当前 adapter 版本下 1110177 的 SFX 完全不出画**，直接原因就是上面 5 个贴图 404（无 map ⇒ 不透明度过门）。

## 3. SFX 开关仍可用 + OFF 帧与 MASK 基线对照
| 皮肤 | 按钮 | OFF 帧 sha16 | ON 帧 sha16 | OFF2（关回） | OFF 五读数（MASK） | 与基线 |
|---|---|---|---|---|---|---|
| **1110171** | `SFX 关闭`→`SFX 开启`，`disabled=false` ✅ | `48b6c95c1165c80a` | **`07a272d49eb738a7`（变了 ⇒ 真画出东西）** | `48b6c95c1165c80a`（**可逆**） | p50 **0.1232** / p95 **0.4865** / >0.5 **3.394%** / >0.75 **0.273%** / 暖色 **0.106%**（mask 2.449%） | **与 `CRITERION_BASELINE_20260919.md` 逐项相同** ✅ |
| **1110177** | 同上 ✅ | `3a6f3bd4a4147c59` | `3a6f3bd4a4147c59`（`__sfxTime(0)` 不在闪窗内 ⇒ 预期不变） | 同上 | p50 **0.2829** / p95 **0.5745** / >0.5 **18.242%** / >0.75 **0.989%** / 暖色 **0.689%**（mask 1.826%） | **与基线逐项相同** ✅ |
- `__cfgEffects()` 在 ON 后：`{effects_status:'partial', effects_type:'object', handle_present:true, btn_disabled:false, btn_text:'SFX 开启'}` ✅。
- ⇒ **默认态未受影响**；**开关可用且可逆**（1110171 两侧 sha 往返一致，1110177 需在闪窗时间看，但 §2 显示当前无画）。

## 4. board 页
| 检查 | 读数 | 判定 |
|---|---|---|
| 卡片 / 骨骼 id | **115** 卡 / **37** 个 `skeleton_preview.html?id=` 链接 | ✅ |
| 评级勾选筛选 | 勾选 → **19** 卡；清除 → **115** 卡 | ✅ |
| `skeleton_preview.html` 链接 | `1110171` → `href="skeleton_preview.html?id=1110171"`、文本 `3D 挂点预览` | ✅ |
| 徽标 | 8 条：`源数据（候选级）`×7 + `未建（无材质链）`×1，`title` 8/8 非空 | ✅ |
| **旧文案残留** | `texture_binding_status`=0、`SFX 未提供`=0、`content_candidate`=0、`6/34`=0（全文命中数） | **无旧文案** ✅ |
| **你认为应展示的口径** | 页面**完全没有** `6/34` / "19 条声明未绑" / "26 个 Model 默认关" 这些字样 | **不符**：若要展示需改 board/注册表（我未改） |
| **控制台** | **非空**：10 条 `assets/audio/weapon_skin/dajian/*.wav` `net::ERR_CONNECTION_REFUSED` | **✗ "无错误"不成立**（音频附件，与皮肤材质无关；如需干净需另修） |

## 5. 三档结论
**已证**：① 1110177 applied 3/3、failed/missing 最终空、`env_warn` 最终 null（≤8 s）；② 1110171 applied 7/7、`env_warn` 最终 null（≤20 s）；③ JS 异常 0；④ OFF 帧两皮肤五读数与 MASK 基线逐项一致；⑤ SFX 按钮可用/可逆、`effects_status=partial`；⑥ board 115 卡/37 id/筛选 19↔115/骨架链接可用；⑦ 徽标 8 条中文 + title 非空、无旧文案；⑧ 1110177 的 `viewer.json`/`effects.json` 与 Lead 给的 sha 一致。
**未证**：① 1110177 当前 adapter 下"SFX 能不能画出东西" —— **当前版本下不出画**（已定位为贴图双前缀 404，非最终结论，待 task-53 修完复测）；② board"控制台无错误" —— 实际有 10 条音频连接被拒。
**未做**：未做长时扫描/全皮肤回归（按"小范围冒烟"要求）；未在 task-53 冻结后复测 SFX 前/后（等通知）。

## 6. 纪律
- 只读；本轮三个脚本均**按 `user-data-dir` 反查真实浏览器 PID 再 `taskkill /T /F`**（分别杀掉 8 / 8 / 8 个进程），复查：匹配 `SMOKE*_prof`/`SMKF*_prof` 的 chrome = 0、我的端口 **10093 / 10095 / 10097 无 LISTEN**。
- 期间 `weapon_skin_viewer.js`、`effects.json`、`adapter` 被他人改动（见 §0），所有读数已按各自 pin 标注。
