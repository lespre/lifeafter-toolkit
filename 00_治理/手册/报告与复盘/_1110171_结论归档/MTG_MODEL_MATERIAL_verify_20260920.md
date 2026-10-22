# task-76 验收：`mtgParams` 开关（默认 OFF）+ `.mtg` 源参数内联后的零回归与四组合 A/B

**结论速览：PASS 4 · WARN 2 · FAIL 0**（另 2 条值得 Lead 跟进的新发现）
- PASS：① 默认零回归（1110177 与 task-73 **逐字节**相同；1110171 差值仅 1 灰阶）② 四组合 A/B 与负控③ 6 皮肤回归 ④ 未变清单 + **adapter 页内字节哈希 = `2C2703FD546BC23E`**。
- WARN：(a) **`mtgParamsInfo().sample[]` 的 `color_src`/`highlight_src` 恒为 `null`**（OFF/ON 都 6/6 null，而 `with_mtg_params=35`）；(b) **`models(true)+mtgParams(true)` 后画面仍是"白面片为主"**（mask 内白 90.57%→90.28%，仅 0.26% 画布变色）——**源色只染到局部，未成为整片源色面片**。

## 0. pin / 版本自证（开工前后各哈希一次，全部一致）
| 对象 | sha16 | 页内 `fetch` 实字节 |
|---|---|---|
| `weapon_skin_sfx_adapter.js` | **`2C2703FD546BC23E`**（97,081 B） | 200 / 97,081 B / 同 ✅（非只看 `?v=`） |
| `weapon_skin_viewer.js` | `B9C7281E1EE7A819`（未改） | 200 / 379,489 B / 同 ✅ |
| `1110177/effects.json` | **`56BEF14E53B6316A`**（653,917 B） | 200 / 653,917 B / 同 ✅ |
| `1110177/viewer.json` | **`101355157BEFBD53`**（694,379 B） | 200 / 694,379 B / 同 ✅ |
| `1110171/effects.json` | `DE667C26A99B7DEC`（未改） | 200 / 140,218 B / 同 ✅ |
| `1110171/viewer.json` | `D4F4A8272E7E7BF8`（未改） | 200 / 173,165 B / 同 ✅ |
| `board.html` / `m1110177` | `F198742EE8010ADD` / `A05C4F2C8DDFCF9A`（未变） | — |
| 5 张真图集 + `atlas171` | `DBC4D2E4FE65FF4F` / `DDE58C1EB420384F` / `BAB99D2E79746152` / `45AE45AB090353CB` / `37FA4BE63541FFAB` / `6480F7FC1914F0C4` | 全部未变 ✅ |
`pins_unchanged` **14/14 true**。

## 1. ① 默认零回归 —— **PASS**
| 皮肤 | SFX OFF 门控帧（N≥5） | 与 task-73 对比 | MASK 五读数 |
|---|---|---|---|
| **1110177** | **`e62c1c58e5bdc383`** | **sha 相同、像素** **max diff = 0.0000（逐字节）** ✅ | `1.826 / 0.2829 / 0.5745 / 18.242 / 0.989 / 0.689` = 长期基线 ✅ |
| **1110171** | `c20d869ec4aa0f90`（sha 与 task-73 的 `48b6c95c1165c80a` 不同） | **像素 max diff = 1/255，>6/255 的像素 = 0**（584 px 差 1 灰阶）⇒ 视觉不可辨；MASK 与 task-73 **逐项相同** | `2.449 / 0.1232 / 0.4865 / 3.394 / 0.273 / 0.106` = 基线 ✅ |
- `__neox()`：**1110177 applied 3 == 3**、**1110171 7 == 7**；`failed=[]`、`missing=[]`、`env_warn=null`。
- `Runtime.exceptionThrown` **0** + evaluate 级 **0**；贴图（`/sfx/tex|src_tex`）**84 条全 200、0×404**；OFF↔SFX 往返两皮肤都回到默认帧 ✅。
- 404 说明：见 §7（**只有 `models(true)` 时才有 3 条缺失 `.glb` 的 404**；补测不调 models 时 404 仅 favicon）。

## 2. ② `mtgParamsInfo()` 原文 —— **WARN（字段恒 null）**
开关默认态：`mtgParams()` → `{"mtgParamsOn":false,"modelHighlight":true}`；**默认 OFF 确认** ✅。
`mtgParamsInfo()`（OFF 与 ON 两个状态都测）：
```
{"recs":43,"with_mtg_params":35,"on":false,"sample":[
  {"node":"L_模型_科技01","stem":"mod_skin_2003_029_mz_kj01_djs","shader":"shader\\uber_fx_common.fx::TShader","color_src":null,"highlight_src":null},
  {"node":"L_模型特效_01","stem":"mod_skin_2003_029_mz_shandian01_djs","shader":"shader\\uber_fx_common.fx::TShader","color_src":null,"highlight_src":null},
  {"node":"H_模型纹理","stem":"mod_skin_2003_029_mz_ks01_djs","shader":"shader\\uber_mask_rim_diss.fx::TShader","color_src":null,"highlight_src":null},
  {"node":"H_模型核心电小_3","stem":"mod_skin_2003_029_mz_sd01_djs","shader":"…uber_fx_common.fx::TShader","color_src":null,"highlight_src":null},
  {"node":"M_模型核心电小_4","stem":"mod_skin_2003_029_mz_shandian03_djs","shader":"…::TShader","color_src":null,"highlight_src":null},
  {"node":"H_模型核心电小_5","stem":"mod_skin_2003_029_mz_shandian02_djs","shader":"…::TShader","color_src":null,"highlight_src":null}]}
```
- **`recs=43` / `with_mtg_params=35` / `on:false→true` 都正确**；但 **`color_src` 与 `highlight_src` 在 OFF 与 ON 下都是 6/6 `null`** ⇒ **探针没有把 `.mtg` 的源字段暴露出来**（而 `models(T)+mtgParams(T)` 确实改了 3,727 px ⇒ 数据是被用上的）。**建议 Lead/renderer-auditor 确认这两个字段是否按预期填充**（或补一个能读出 `u_emissivecolor`/`u_emissive_highlight_intensity` 源值的字段）。
- 1110171：`mtgParamsInfo()` = `{"recs":28,"with_mtg_params":0,"on":false}` ⇒ 该皮肤**无 `.mtg` 参数**（符合"本轮只做 1110177"）。

## 3. ③ 四组合 A/B（同载入内，t=0.30 固定，每格 N≥5 门）—— **PASS**
| 组合 | `models` 可见数 | 掩模内白像素% | effect-only%（vs 默认 OFF） | 帧 sha16 |
|---|---|---|---|---|
| `models(F) + mtg(F)` | 0 | 0.651 | 0.2358 | **`0ff65ed7b8b91b0a`** |
| `models(F) + mtg(T)` | 0 | 0.651 | 0.2358 | **`0ff65ed7b8b91b0a`（与上一格逐字节相同）** |
| `models(T) + mtg(F)` | **31** | **90.569** | 8.7103 | `a6bd7f3e311e1c0c` |
| `models(T) + mtg(T)` | **31** | **90.278** | 8.7103 | `f5f712b1e41969c1` |
- **`models(T)` 的 MASK：`p50 1.0 / p95 1.0 / >0.5 93.97% / >0.75 91.5%`** ⇒ Model 层就是**大片纯白**（与 task-62/68 的已知限制同源：Model 源不声明贴图 ⇒ 无 alpha 塑形）。
- **`mtgParams` 的净效果**（`models(T)` 下 F→T）：**3,727 px = 0.2618% 画布**（bbox x[598,968] y[278,592]），**白像素占比只从 90.569% 降到 90.278%**，亮部颜色统计几乎不动（warm_share 0.041→0.042、blue_share 0.031→0.033、meanRGB 0.955/0.961/0.954→0.957/0.961/0.954）。
- **负控**：① `models(F)+mtg(F)` = **`0ff65ed7b8b91b0a` = task-70 "SFX 开、完全不调开关"的同 t 帧（逐字节）** ⇒ 显式关两开关**像素中性** ✅；② `models(T)+mtg(F)` **两次采样同 sha**（`a6bd7f3e…`×2）⇒ 可复现 ✅；③ 同载入内"未调 vs 显式 false/false"的对照**本次未完成**（见 §8 限制）。
- **我亲眼（2× 放大 `zoom_mtgF_left_mtgT_right.png`，左=F 右=T）**：两边都是**巨大白色平面群**；右侧（`mtgParams=true`）在**局部**出现**淡粉紫、局部偏金**的小片色晕（左上与刃尖附近），**但大面积仍是纯白**。⇒ **不能说"白面片变成了源色面片"**，只能说"**局部染上源色**"。

## 4. ④ 6 皮肤回归 —— **PASS**
| 皮肤 | applied/expected | failed / missing | env_warn | SFX 默认态 |
|---|---|---|---|---|
| 1110024 | **5 == 5** | 0 / 0 | null | `SFX 关闭`（disabled=true, pressed=false） |
| 1110129 | **5 == 5** | 0 / 0 | null | 同上 |
| 1110145 | **7 == 7** | 0 / 0 | null | 同上 |
| 1110152 | **2 == 2** | 0 / 0 | null | `SFX 关闭`（disabled=false, pressed=false） |
| 1110165 | **4 == 4** | 0 / 0 | null | 同上（disabled=true） |
| 1110171 | **7 == 7** | 0 / 0 | null | `SFX 关闭`（disabled=false, pressed=false） |

## 5. ⑤ 未变清单 —— **PASS**
`viewer.js B9C7281E1EE7A819`、`m1110177 A05C4F2C8DDFCF9A`、5 张真图集（`DBC4D2E4FE65FF4F`/`DDE58C1EB420384F`/`BAB99D2E79746152`/`45AE45AB090353CB`/`37FA4BE63541FFAB`）、`atlas171 6480F7FC1914F0C4`、`1110171` 两枚（`DE667C26A99B7DEC` / `D4F4A8272E7E7BF8`）—— **前后哈希全一致**。

## 6. ⑥ 诚实边界
- Model 层**没有贴图直证**、GLB **无顶点色**（`COLOR_0 = 0/40`）⇒ 打开 `mtgParams` 得到的是**源色面片**，**仍不是成品外观**；本报告不拔高（实测也证明：白仍占 90%+）。
- `mtgParams` 只改**取值来源**、不新增乘法 ⇒ 它的净视觉贡献天然是"局部换色"；这一点与实测一致。

## 7. ⚠ 新发现（请 Lead 跟进）：`models(true)` 触发 3 条缺失 GLB 的 404
主运行（`http_errors_all` / `console_all` 原文，均为 **404**）：
```
1110171/sfx/mod_skin_1003_010_zs_ql07_djs.glb
1110171/sfx/mod_skin_1003_012_zs_qiu03_djs.glb
1110171/sfx/mod_skin_1003_012_zs_qiu04_djs.glb
（另有 favicon.ico 404）
```
- **只在开启 `models(true)` 时出现**：补测（不开 models）404 仅 `favicon.ico` 一条 ⇒ 这 3 条是 task-72 登记的**子特效 Model 节点**在 `models(true)` 下尝试加载时打出来的。
- fail-closed 生效（不渲染、不崩、异常 0），但**控制台会留 3 条错误**；若希望"开 models 也干净"，需要补这 3 个 `.glb` 或把这类无 GLB 的 Model 排除出加载列表。

## 8. 限制（如实）
- **同载入内"未调 vs 显式 false/false"对照未完成**：补测里第三次门控帧 `gate_ok=false`（`6f3d09717a3d0277` 未在 14 次内稳定）⇒ 该载入在开关往返后**帧在动画**（`__sfxTime` 冻结被后续 API 调用打断），所以同载入对照不可用。**替代证据**：主运行 `models(F)+mtg(F)` 与 task-70"完全不调"的同 t 帧**逐字节相同**（跨会话），可支撑"两开关关闭时像素中性"。
- 四组合只在 **t=0.30** 取样（Model 层不随时间变化，该点足够）；`effect-only%` 以**本次会话默认 OFF 帧**为参照。

## 9. 纪律与产物
- 只读 `08Lifeafter wiki/**`（未改任何文件）；两个阶段各 **1 个**浏览器（`FXVA76_prof`/10133、`FXVA76b_prof`/10135），均按 `user-data-dir` 反查真实 PID `taskkill /T /F`（各 8 进程）；**端口 10133/10135 无 LISTEN**、我的 profile chrome = 0、全机 chrome 0。
- 产物（仅写 task 允许的三条路径）：本报告 + `MTG_MODEL_MATERIAL_verify_20260920.json`；截图 `sfx_verify_shots6/`（默认 OFF/bg、四组合帧、`zoom_mtgF_left_mtgT_right.png`、补测 3 帧）。
