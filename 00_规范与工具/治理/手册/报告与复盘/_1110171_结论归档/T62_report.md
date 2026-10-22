# task-62 报告 —— 1110177（极光剑）viewer 侧收尾：`gpk_1229.png` 404 修复 + 专属回归

作者：shader-auditor ｜ 2026-09-19 ｜ **结论：修复生效且默认零回归；404 在默认态归零（仅剩 favicon）；异常 0 条；正控证明该请求只来自显式开关。**

## 0. 钉（pins）

| 项 | 值 |
|---|---|
| viewer.js **改后** | **`68F8113B864A4CA1`**（378,682 B / 5025 行 / `node --check` OK） |
| viewer.js 改前 | `8B8E80213F5C0CA8`（376,205 B） |
| 备份 | `%TEMP%\wsv_bak_task62_20260919_183833.js`（= `8B8E80213F5C0CA8`） |
| 其它（改前复核一致、未动） | `adapter 544D3A4A1B2CC591`、`1110177/viewer.json 7575FAFAD33DD670`、`1110177/effects.json 10CC9A938BE92A10`、`board 5008117AA03BB7A0` |

## 1. 改了什么（4 处，只围绕这一处 404）

**核查（与 lead 给的行号不同，中间版本已变动）**：全文件只有 **2 处** `tex('src_tex/…')` 硬编码 ——
L1406 `rough_repack_<fam>.png`（**1110177 磁盘上有 `rough_repack_029.png` ⇒ 不 404**）与 **L1769 `gpk_1229.png`**（真正的 404 源）；
`1110177/src_tex/` **无 `gpk_1229.png`**；两个皮肤的 `neox_material.json` 里 **`gpk_1229` 均 0 命中** ⇒ 它不是任何槽位的声明值。

1. **删除无条件加载**：`const detailTex = tex('src_tex/gpk_1229.png', false);` →
   `const legacyDetailPath='src_tex/gpk_1229.png';`
   `const legacyDetailTex=(state.__useLegacyDetail===true)?tex(legacyDetailPath,false):null;`
   ⇒ 默认 `null`：**不发起请求**、**不顶替** DetailMap 槽位；`uHasDetail` 判据**一字未改**。
2. **`uDetailMap` 回落链**：`{value:((detailFile?tex(detailFile,false):null)||legacyDetailTex)}` —— `detailFile` 有值时行为**逐字不变**。
3. **新增 `window.__legacyDetail(on)`**（默认关）：只有显式 `true` 才加载该历史候选（仅供 1110171 A/B）。
4. **`__texReady()` 增两字段**：`legacy_tex_missing`（默认 `['src_tex/gpk_1229.png']`）与 `legacy_detail_on`（默认 `false`）
   ⇒ "404 归零"在探针里**可读**，不必只靠网络日志。

## 2. 回归读数（单浏览器；CDP 抓 Network/Log/Console/Exception）

### 2.1 1110177 默认态（主验收）

| 项 | 读数 | 判定 |
|---|---|---|
| `applied` | **3/3**（`applied_prims=[0,1,2]`） | ✅ |
| `failed` / `missing` / `env_warn` | **0 / 0 / `null`（无该字段）** | ✅ |
| `bad`（非 source_ibl 的 mesh） | **[]** | ✅ |
| `retry` / `exhausted` | 2 / `false` | ✅ |
| **默认 OFF 帧 sha** | **`9dbb3449da619f56`** = 我的改前锚 | ✅ **逐字节一致** |
| 五读数 | `p50 0.2829 / p95 0.5745 / >0.5 18.242 / >0.75 0.989 / 暖色 0.689 / mask 1.826` | ✅ 与长期基线**逐项相同** |
| `__texReady().legacy_tex_missing` | `["src_tex/gpk_1229.png"]`；`legacy_detail_on=false` | ✅ |
| `exceptionDetails` | **[] （逐条为空）** | ✅ |
| `__glowErrors` / `renderErr` | `typeof === 'undefined'`（board 页无此全局）/ `null` | ✅ |

### 2.2 404 / 网络（默认态）

* **404 共 1 条：`favicon.ico`**（lead 已明示除外）⇒ **`src_tex/` 下 0 条 404**，`gpk_1229` **0 次请求** ✅
* `src_tex/` 全部 **200**：`029_a? 否` —— 实测加载的 11 个文件为 `029_b_m / 029_m / 029_n / 029_s_m / param_repack_029 / rough_repack_029 / crystal_bump_n02 / crystal_bump_n_uvva / crystal_caustic_uvva / crystal_reflection_uvva / refraction_envmap_3`。
* **打开 SFX（`.wv-sfx`）后**：`/sfx/tex/` **6 条，全 200** ——
  `lightning07_cs__a8764b3a / glow_16_yh_djs__7ce99117 / lightning_01__662b911e / glow_01__13211b02 / dian_12__7240b831 / shandian_05_yh_djs__a9aa4caf`；404 仍仅 favicon ✅
* `Log` 里 **error 仅 favicon**；`exceptions` 两次页面均 **[]** ✅

### 2.3 正控（证明"请求源唯一"）

`__legacyDetail(true)` **在开皮肤之前**置位 ⇒ 编译期才会走历史分支：
**恰好出现 3 条 `…/1110177/src_tex/gpk_1229.png` 404**（+favicon），默认态 **0 条** ✅
⇒ 该请求**只**来自这个显式开关，已**不在默认路径**上。（第一次尝试"开完皮肤后再置位"没有产生请求——因为该加载发生在 `onBeforeCompile`/材质编译期，事后置位不会触发加载；这一条如实登记。）

## 3. 只读发现（**未改**，供 lead 分派）

| # | 现象 | 我的判断 / 建议 |
|---|---|---|
| **D1** | `console` 6 条警告：`THREE.Material: 'emissive' / 'emissiveIntensity' is not a property of THREE.MeshBasicMaterial.`（3 对） | **真·viewer 侧代码味**：某处把 emissive/emissiveIntensity 赋给了 `MeshBasicMaterial`（嫌疑：`__primOnly`/`__primSolid`/`__exp` 的 unlit 路径或 SFX 精灵材质）。**只读登记**，未改；建议另立小项定位（改前也可能存在，非本项引入） |
| **D2** | `Network.loadingFailed` 中约 **210 条 `net::ERR_ABORTED`**（Media ~180、Fetch ~30） | **不是 404**；更像重建/切换时被取消的在飞请求（或媒体预载中断）。**只读登记**，需判"是否无害"，建议归 chain-auditor/另立项 |
| **D3** | 同一贴图 URL 被**重复请求**（如 `029_b_m.png` 12 次 200） | 根因：`applyNeoxManifest` 内 **`const cache={}`（L936）是"每次调用一份"**，而 1110177 本页发生 `retry=2`（≈3 次重建）⇒ 每次重建重新请求全部贴图。**只读登记**（非本轮引入、非 404），是**可优化项**（把 cache 提到会话级即可减请求），但**未改** |
| **D4** | 1110177 的 DetailMap 实际加载的是 `crystal_bump_n02.png`(prim1) / `crystal_bump_n_uvva.png`(prim2)，而 manifest 这两个槽是 `file:null / confidence:none` | viewer 用的是 `local_file` 字段。与 task-47 的 **C1 待补项**一致 ⇒ **归 lead 补 manifest**（我不碰） |
| **D5** | `Log` 4 条 GL 警告 `GPU stall due to ReadPixels` | **headless 截图（`Page.captureScreenshot`）引起**，非页面缺陷，可忽略 |

## 4. D1 修复：`emissive/emissiveIntensity` 警告 6 → 0（本轮新增，pin `B9C7281E1EE7A819`）

**钉**：viewer.js = **`B9C7281E1EE7A819`**（379,489 B / 5031 行 / `node --check` OK）；改前 `68F8113B864A4CA1`；
备份 `%TEMP%\wsv_bak_task63_20260919_184211.js`。

**定位（1 处）**：`applyMaterialLayers()` 里「源链未生效 ⇒ 回退无光照预览」那条分支（`state.neoxReport.applied===0`，**含链就绪前的窗口期**）：

```js
obj.material=new state.THREE.MeshBasicMaterial({map:t,color:0xffffff,toneMapped:false,fog:false,side:side,
                                                emissive:0x000000,emissiveIntensity:0});   // ← 这两键 MeshBasicMaterial 没有
```
`MeshBasicMaterial` **没有** `emissive`/`emissiveIntensity`（属 Standard/Physical）⇒ three 的 `Material.setValues()` 对**每个 mesh 各报 2 条** ⇒ 1110177 三个 prim 实测 **6 条**。

**逐处行文（只删这两个键，其余逐字不变）**
```js
obj.material=new state.THREE.MeshBasicMaterial({map:t,color:0xffffff,toneMapped:false,fog:false,side:side});
```
**为什么是零语义改动**：这两个键**本来就被 three 丢弃**（`m.emissive===undefined`；`__matDump()` 由此恒读 `null`）⇒ 删除前后材质属性集合相同；
`__previewMode/__srcTexFile/__label` 与 `map/side/toneMapped/fog/color` 全部不动；**未触碰曝光/灯光/bloom/ACES 与任何材质层语义**。

**实测（同一页，1110177）**

| 项 | 读数 | 判定 |
|---|---|---|
| console `emissive` 警告 | **0**（改前同页实测 **6**） | ✅ 6 → 0 |
| console 总条数 | **0**（本页已无任何 console 输出） | ✅ |
| 默认 OFF 帧 sha | **`9dbb3449da619f56`** = 锚 | ✅ **逐字节零回归** |
| 五读数 | `p50 0.2829 / p95 0.5745 / >0.5 18.242 / >0.75 0.989 / 暖色 0.689 / mask 1.826` | ✅ 与基线逐项相同 |
| 链健康 | `applied 3/3`、`failed=0`、`missing=0`、`bad=0`、`retry=2`、`pending=false`、`renderErr=null` | ✅ |

**波及面**：全文件 20 处 `MeshBasicMaterial` 构参已脚本复查 **0 处**再传 `emissive*`（改前该断言失败）；该分支属"回退预览"，
故修复对**所有链未生效/窗口期**的皮肤同样生效，且不改变其外观。

## 5. D2 判定：~202 条 `net::ERR_ABORTED` ⇒ **无害**（只读，未改代码）

**采集**：同页 CDP 抓 `requestWillBeSent / responseReceived / loadingFailed` + 每 50 ms 轮询重建标记（`retry_count/rebind_count/rebind_pending/__crystalOBC`）。

| 证据 | 读数 |
|---|---|
| abort 总数 / 类型 / 错误码 | **202** = Media 153 + Fetch 49，**全部 `net::ERR_ABORTED`**（无一条 4xx/5xx/超时） |
| **相位** | **settle 前 202 / settle 后（含最后 8 s 稳定相位）0** ⇒ **全部发生在载入期** |
| 重建标记 | 4 个：`t=0.05s(retry0/rebind0)` → `0.98s(pending=true)` → **`1.72s(retry1/rebind1, __crystalOBC 2)`** → **`2.05s(retry2/rebind2, __crystalOBC 3, pending=false)`** ⇒ 载入期 **2 次重建**，中止集中在 0→2.05 s 窗口 |
| 被中止 URL | **103 个不同 URL**；`without_200 = 0`、`that_404 = 0`、`with_200`（样本，列表按 12 截断，逻辑上全部）⇒ **103/103 同时存在成功 200 响应** |
| 典型 URL | `src_tex/029_b_m.png`×17、`029_n.png`×8、`crystal_reflection_uvva.png`×5；以及 board 侧音频预载 `assets/audio/weapon_skin/<他皮肤>/*.wav`×3 各 |
| 404 | 仅 `favicon.ico` 1 条（与本判定无关） |

**结论：无害。** 理由是链条完整的四条：① 错误码全是"被主动取消"（`ERR_ABORTED`），不是失败状态；
② **全部落在载入期的 0→2.05 s 重建窗口内**，settle 后与 8 s 稳定相位 **0 条**；
③ **每一个被中止的 URL 都有成功的 200**（无"只有 abort 没有成功"的 URL，也无 404）⇒ 资源全部拿到了，被取消的只是**重复/在飞的旧请求**；
④ 153 条 Media 是 board 侧音频预载被打断（他皮肤音频、非本皮肤资产）。
**根因**：与 D3 同源 —— `applyNeoxManifest` 内 `const cache={}`（L936）为"每次调用一份" + 本页 2 次重建 ⇒ 每轮重建重发贴图/资源请求，旧请求被取消。
⇒ **无隐患**（不影响最终渲染与资源完整性）；若日后要降噪，与 D3 一起做"会话级 cache"即可（本项不做）。


## 6. 主验收结论（task-62 第 1+2 项 = 404 修复 + 极光剑回归）

* **修复目标达成**：默认态 `src_tex/` **404 = 0**（仅剩 favicon），历史硬编码**被守卫在显式开关后**，且**不再顶替槽位**；正控给出"请求源唯一"的实证。
* **零回归**：1110177 默认 OFF 帧 = 改前锚（逐字节）、五读数逐项相同；`applied 3/3`、`failed/missing` 空、`bad=[]`、`exceptionDetails=[]`。
* 其它皮肤：本次改动只把"`detailFile` 为空时的兜底"从"硬编码贴图"改为"`null`"，**不触碰任何已绑定槽位**；
  且该兜底原先会**给所有皮肤发一个必然 404 的请求**（含 1110171 之外的每一个皮肤）⇒ 属**全体皮肤受益**的修复。
