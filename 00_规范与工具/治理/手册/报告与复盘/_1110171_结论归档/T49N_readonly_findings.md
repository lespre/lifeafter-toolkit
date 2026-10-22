# T49N 只读发现（task-49 收尾前置分析）

分析者：shader-auditor ｜ 时间：2026-09-19 00:2x ｜ **本文件为纯只读分析，未改任何代码、未起浏览器**
被测 pin（分析时）：`weapon_skin_viewer.js = 3B9999B992FE8763`（未动）· adapter = `13331424c3cb4fe4`（board.html L14 引用 `?v=13331424c3cb`）

---

## 一、`pending_hidden` 三源不一致（1110171 WARN：neox 计 2，另两源 0）

### 1.1 三处各自读的字段与取值时刻（行号级）
| 来源 | 字段 | 写入/读取位置 | **取值时刻** |
|---|---|---|---|
| `__neox().report.prims[i].pending_hidden` | `rec.pending_hidden` | 建材质循环内：`rec.pending_hidden=true/false`（我加的镜像快照） | **建材质时刻的快照**，之后**不再更新** |
| `__texReady().pending_hidden_total` | 惰性遍历 `o.userData.__pendingHidden` 计数 | `__texReady()` 体内（`out.pending_hidden_total=0; scene.traverse(...)`） | **读取时现算（live）** |
| `__acceptanceReport().pending_hidden_total` | 由 `out.meshes[i].pending_hidden = !!ud.__pendingHidden` aggregate | `__acceptanceReport()` 的 mesh 收集 + 末尾 filter | **读取时现算（live）** |

### 1.2 结论（**不是"镜像没同源"，而是"快照 vs 现算"混用**）
- 三源的**底层事实源其实是同一个** `userData.__pendingHidden`；差异来自**取值时刻**：
  - `rec.pending_hidden` 是 **`state.neoxReport` 里那份报告的快照**，而 `state.neoxReport` 会被**某一次重建的 report 覆盖**（且窗口期那次 build 的 promise 可能**晚于**重绑那次 resolve ⇒ 晚到的旧报告盖住新报告，这条在 `env_warn` 上已实测过一次）。
  - 窗口期 build 时确有 2 个 prim 处于 `ibl_pending` ⇒ 那份（旧）报告里 `pending_hidden` = 2 个 prim；settle 后恢复逻辑清掉 `userData.__pendingHidden` ⇒ **live 两源 = 0**。
- 因此 WARN 的正确表述是：**"`__neox().report.prims[*].pending_hidden` 是建材质时刻的快照，settle 后可能陈旧；另两源是读取时现算"** —— 不是字段不一致，也不是"恢复逻辑漏了"。（恢复逻辑本身有效：live 两源为 0，且 `visible` 串显示全部 `v`。）

### 1.3 最小复现
1. 载入 1110171，**在窗口期**（mesh 刚出现、`__texReady().meshes[*].envMode` 含 `ibl_pending`）读一次三源；
2. 等 `__texReady()` 全 `source_ibl` 后再读一次三源。
预期：第 1 次三者可能同值（都≥1）；第 2 次 **`report.prims[*].pending_hidden` 仍保留窗口期快照**，而 `__texReady/__acceptanceReport` 的 total = 0 ⇒ 复现 WARN。

### 1.4 修法（建议，待 lead 批 + 走"冻结窗口"）
**首选（与既有 `env_warn` 修复同法，1 处小改）**：在 `__neoxLiveEnv()`（read-time 重算 `missing/env_warn` 的那个函数）里**同时按 live 场景重算 `prims[*].pending_hidden`**：
- 遍历场景取每个 `chain.prim` 的 `!!material.userData.__pendingHidden`；
- 覆写返回对象里 `prims[i].pending_hidden`（**不改 `state.neoxReport` 本体**，避免污染其它读者）；
- 并在返回里加一个 `pending_hidden_source:'read_time'` 字段，明确口径。
**备选**：在收敛恢复处顺手把 `state.neoxReport` 对应 prim 的 `pending_hidden` 置 false（缺点：仍有"晚到旧报告覆盖"的竞态，不如 read-time 稳）。
**期望影响面**：仅报告口径（无渲染影响）；`applied/failed/missing` 不变；修复后三源在**任一时刻**取值一致（都按 live 计），并且窗口期读数仍能反映"当时确实 pending"（因为窗口期 live 就是 ≥1）。

---

## 二、`adaptSwitches` 时有时无 / `__spriteOn` 恒 null

### 2.1 先纠正一条前提（含行号证据）
- **`weapon_skin_viewer.js` 内不存在任何 adapter 引用或注入**：grep `WikiSfxAdapter|adaptSwitches|spriteOn|__spriteOn` 在 viewer.js 中**零命中**；唯一命中 `document.body.removeChild(ta)` 在 **L3090**，那是**剪贴板复制**代码（`document.execCommand('copy')` + 移除临时 `textarea`），**与 adapter 无关**。
- **不存在"adapter 被装载两次"**：全仓只有 board.html **L14** 一处 `<script defer src="assets/weapon_skin_sfx_adapter.js?v=13331424c3cb">`；viewer.js 无动态插入 script 的代码（同 grep 证据）。
⇒ 因此"两个实例互相盖"的假设**不成立**。

### 2.2 `adaptSwitches` / `__spriteOn` **都已注册**（adapter 侧行号）
| 名字 | 行号 | 说明 |
|---|---|---|
| `WikiSfxAdapter.adaptSwitches` | **L847** | 返回 `{spriteFix, clampOn, clampK, psFallbackOn, spriteOn, blend7}` |
| `WikiSfxAdapter.sprites(on)` | **L830** | 设置/读取 `SPRITE_ON` |
| `WikiSfxAdapter.__spriteOn()` | **L841** | `return SPRITE_ON` |
⇒ 两者**不是"未注册"**。

### 2.3 `spriteOn` 恒为 `null` 是**设计语义，不是坏值**
- L834：`if (SPRITE_ON === null) return { spriteOn: null, note: 'follow_sfx_switch' };`
⇒ `null` = **跟随 SFX 总开关**。**这恰好解释"三态负控帧完全相同"**：若负控脚本只读 `spriteOn` 而**从未显式设置** `sprites(true/false)`，该开关处于 follow 态 ⇒ 切它不动画面 ⇒ **负控失去判别力**。
- 期望影响面/建议（adapter 归 viewer-auditor，我不代改）：负控前先 `WikiSfxAdapter.sprites(true)`（或 `false`）**显式定态**并断言 `typeof spriteOn === 'boolean'`，再做 A/B。

### 2.4 "开场 not a function、稍后同调用返回对象"的最可能原因（**装载时序**）
- `window.WikiSfxAdapter = WikiSfxAdapter;` 在 **L959**，即**该文件 IIFE 的末尾**才赋值；board 用 **`defer`** 加载（L14）。
- ⇒ 任何在 **defer 脚本执行完成之前**发起的调用（例如 `Page.navigate` 后立刻 evaluate、或在 `readyState!=='complete'` 时、或另一个 frame/上下文）都会看到 `window.WikiSfxAdapter === undefined` ⇒ 报 `not a function`；稍后轮询则拿到对象。
- **最小复现**：`Page.navigate` → **不等待** 直接 `Runtime.evaluate("WikiSfxAdapter.adaptSwitches()")` ⇒ TypeError；等 `document.readyState==='complete'`（或轮询 `typeof window.WikiSfxAdapter==='object'`）后再调用 ⇒ 返回对象。
- 另一条**未定证**的旁证：adapter **L1010** 会 `window.WikiWeaponViewer.registerEffectsAdapter(WikiSfxAdapter)`，但该调用处于某个**条件分支**内（我只读到该行，未读上下文）⇒ **该分支的判定条件未验证**，若它依赖 viewer 已就绪，则"谁先就绪"也会影响开关是否真正接线。**标 `unresolved`**，建议 viewer-auditor 读 L1000-1012 上下文并给出：`registerEffectsAdapter` 是否被调用、调用时的参数与返回。

### 2.5 修法建议（按写入面归属）
- **harness 侧（viewer-auditor）**：调用前 gate：`typeof window.WikiSfxAdapter==='object' && typeof window.WikiSfxAdapter.adaptSwitches==='function'`（或等 `readyState==='complete'`）；负控前显式 `sprites(true/false)`。
- **adapter 侧（viewer-auditor）**：可考虑在文件**开头**先挂一个**占位对象**（`window.WikiSfxAdapter = window.WikiSfxAdapter || {}`），结尾再补方法；这样"早调用"至少不会 `not a function`，而是明确报"尚未就绪"（**属语义变更，需 lead 批**）。
- **viewer.js 侧（我）**：**无需改动**（本文件不引用 adapter）。

---

## 三、下一轮我要做的（等"浏览器归你 + 解冻"）
1. `t49_next.py`（已在 `%TEMP%`，未运行）：双侧锚点 N≥5 + 7 皮肤回归（`applied==expected` + `manifest_fams==runtime_fams`）+ 三源 `pending_hidden` 一致性 + `__perfStages()` + 窗口/settle 帧 + 冷/热 `all_green` + 负载标注；
2. **本文件 §1.4 的 read-time 修复**（1 处小改，先 `copy2` 备份 + `node --check`）；
3. 亲眼看窗口/settle 帧并如实描述。
**明确不做**：adapter（另一写者）· viewer.json/manifest/board · 曝光/灯光/bloom/ACES。
