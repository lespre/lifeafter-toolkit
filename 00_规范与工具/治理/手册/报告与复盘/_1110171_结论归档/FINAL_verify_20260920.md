# task-78 终验：GLB 404 归零 + `mtgParamsInfo` 探针修复 + 默认零回归

**结论速览：PASS 5 · WARN 1 · FAIL 0**
- PASS：① **1110171 `models(true)` 的 GLB 404 = 0**（改前 3 条）② 探针新字段**确认有值**（`applied_color 14 / applied_highlight 19`，OFF 正确标 `declared_not_applied_switch_off`）③ 默认零回归（1110177 逐字节同 task-76；1110171 像素差 0）④ 最小四组合**与 task-76 逐字节相同** ⇒ 探针改动未动渲染 ⑤ 6 皮肤回归 + 未变清单。
- WARN：1110171 那 3 个 GLB 虽已 `ok`，但该皮肤 **`models` 可见数仍 = 0**、画面 **0 px 变化** ⇒ **404 消了，模型仍不可见**（原因未定证，请 Lead 判是否继续）。

## 0. pin / 版本自证（开工前后各哈希一次，全部一致）
| 对象 | sha16 | 页内 `fetch` 实字节 |
|---|---|---|
| `weapon_skin_sfx_adapter.js` | **`FFBE14706C2CFD0A`**（98,932 B） | 200 / 98,932 B / 同 ✅（非只看 `?v=`） |
| `weapon_skin_viewer.js` | `B9C7281E1EE7A819`（未改） | 200 / 379,489 B / 同 ✅ |
| `1110171/effects.json` | **`61CE90075C53CA4E`**（149,005 B） | 200 / 149,005 B / 同 ✅ |
| `1110171/viewer.json` | **`C21369F0AC2BA131`**（181,998 B） | 200 / 181,998 B / 同 ✅ |
| `1110177/effects.json` / `viewer.json` | `56BEF14E53B6316A` / `101355157BEFBD53`（未变） | 200 / 同 ✅ |
| `m1110177` / 5 张真图集 / `atlas171` | `A05C4F2C8DDFCF9A` / `DBC4D2E4FE65FF4F`·`DDE58C1EB420384F`·`BAB99D2E79746152`·`45AE45AB090353CB`·`37FA4BE63541FFAB` / `6480F7FC1914F0C4` | 全部未变 ✅ |
| 3 个新导出 GLB | `mod_skin_1003_010_zs_ql07_djs.glb` **`A4EA1EC706F7E71C`**（5,912 B）、`…_zs_qiu03_djs.glb` **`21A1F52546D0CD12`**（15,784 B）、`…_zs_qiu04_djs.glb` **`B9E06158D88FBBD1`**（15,784 B） | 与 Lead 给的一致 ✅；`1110171/sfx/` 现有 **28 个 .glb** |
`pins_unchanged` **16/16 true**；rect 三次读数一致 `{x:200, y:122.3, w:1178, h:717.7}`。

## 1. ① GLB 404 归零（本轮靶子）—— **PASS**
1110171 → SFX 开 → `WikiSfxAdapter.models(true)` → 等载入完成：
```
GLB 404 : []                       # 改前 3 条
GLB 200 : dual.glb, mod_skin_1003_010_zs_ql07_djs.glb,
          mod_skin_1003_012_zs_qiu03_djs.glb, mod_skin_1003_012_zs_qiu04_djs.glb
__probe(): {"modelsOn":true,"modelsForce":true,"total":28,"visible":0,"ok":3,
            "states":{"disabled_no_color_driver":22,"disabled_fxignore":3,"ok":3}}
```
- **本页全部 404 逐条**：只有 **1 条 `http://127.0.0.1:8765/favicon.ico`** ✅（控制台错误同为这 1 条）。
- `Runtime.exceptionThrown` **0** + evaluate 级 **0**；载入等待期间无新增 404。
- ⚠ **WARN（请 Lead 判）**：3 个 GLB 现在 `state='ok'`（载入成功），但 1110171 的 **`visible = 0`**，且 `models(true)` 帧与默认 OFF 帧**像素差 = 0（>6/255 的像素 0 个，max 0.0039）** ⇒ **404 消除达成，但这 3 个模型在 1110171 仍不上屏**。对照：1110177 同口径是 `ok 31 / visible 31` ⇒ 探针本身没问题，差异在 1110171 的这 3 个（`disabled_no_color_driver 22` 那一类仍被拦）。

## 2. ② `mtgParamsInfo()` 探针修复 —— **PASS（有前提：样本只在 `models(true)` 下产生）**
**四态原文**（1110177，同载入逐一设置；这解释了我第一次"看起来还是 0/空"的读数）：
| 状态 | `applied_color` / `applied_highlight` | `declared_color` / `declared_highlight` | `sample` |
|---|---|---|---|
| `models(F) + mtg(F)` | 0 / 0 | 0 / 0 | 6 条，`color_src/color_val/highlight_src` 全 `null` |
| `models(F) + mtg(T)` | 0 / 0 | 0 / 0 | **`[]`（空）** |
| **`models(T) + mtg(F)`** | 0 / 0 | **14 / 19** | 6 条，**`highlight_src:"declared_not_applied_switch_off"`、`highlight_val:60`、`color_src:"no_u_emissivecolor_declared"`（`color_val:null`）** ✅ 正是你要的 OFF 标记 |
| **`models(T) + mtg(T)`** | **14 / 19** | 14 / 19 | 6 条，**`color_src:"mtg:u_emissivecolor"`、`color_val:[0.4196,0.2902,1]`（紫蓝）/ `[1,0.3451,0]`（橙）、`highlight_src:"mtg:u_emissive_highlight_intensity"`、`highlight_val:50`** ✅ |
- 其他字段：`recs=43`、`with_mtg_params=35`、默认 `mtgParams()` = `{"mtgParamsOn":false,"modelHighlight":true}` ⇒ **开关默认仍 OFF** ✅。
- **前提（重要）**：`sample` 只有在 **`models(true)`** 时才有内容（因为样本记的是"模型材质实际应用"）；`models` 关时 `applied_*` 恒 0、`sample` 为空或全 null。**建议在文档里写明这一点**，否则后续复测容易误判成"字段没修好"（我第一次就是先在 `models` 关的状态下读的）。

## 3. ③ 默认零回归 —— **PASS**
| 皮肤 | SFX OFF 门控帧（N≥5） | 与 task-76 对比 | MASK 五读数 |
|---|---|---|---|
| **1110177** | **`e62c1c58e5bdc383`** | **sha 相同、像素差 0** ✅ | `1.826 / 0.2829 / 0.5745 / 18.242 / 0.989 / 0.689` = 基线 ✅ |
| **1110171** | `48b6c95c1165c80a` | sha ≠ task-76 的 `c20d869ec4aa0f90`，但**像素差 = 0（>6/255 的像素 0 个）** ⇒ 视觉不可辨（跨会话微差） | `2.449 / 0.1232 / 0.4865 / 3.394 / 0.273 / 0.106` = 基线 ✅ |
- `__neox()`：**1110177 applied 3 == 3**、**1110171 7 == 7**；`failed=[]`、`missing=[]`、`env_warn=null`。
- 两皮肤 OFF↔(SFX+models+mtg) 往返后都回到默认帧（`equals_default_OFF = true`）✅；贴图 `/sfx/tex` 请求 404 = 0。

## 4. ④ 最小四组合复测（同载入、t=0.30）—— **PASS：与 task-76 逐字节相同**
| 组合 | `models` 可见数 | 掩模内白% | effect-only% | 本帧 sha16 | task-76 | 一致？ |
|---|---|---|---|---|---|---|
| `models(T) + mtg(F)` | **31**（`ok 31 / disabled_fxignore 1`） | **90.569** | 8.7103 | **`a6bd7f3e311e1c0c`** | `a6bd7f3e311e1c0c` | ✅ **逐字节相同** |
| `models(T) + mtg(T)` | **31** | **90.278** | 8.7103 | **`f5f712b1e41969c1`** | `f5f712b1e41969c1` | ✅ **逐字节相同** |
⇒ **本轮 adapter 探针修复没有改动渲染**（白占比、effect-only、帧 sha 全对得上），预期"不变"成立 ✅。

## 5. ⑤ 6 皮肤回归 —— **PASS**
| 皮肤 | applied/expected | failed / missing | env_warn | SFX 默认态 |
|---|---|---|---|---|
| 1110024 | **5 == 5** | 0 / 0 | null | `SFX 关闭`（disabled=true, pressed=false） |
| 1110129 | **5 == 5** | 0 / 0 | null | 同上 |
| 1110145 | **7 == 7** | 0 / 0 | null | 同上 |
| 1110152 | **2 == 2** | 0 / 0 | null | `SFX 关闭`（disabled=false, pressed=false） |
| 1110165 | **4 == 4** | 0 / 0 | null | 同上（disabled=true） |
| 1110171 | **7 == 7** | 0 / 0 | null | `SFX 关闭`（disabled=false, pressed=false） |

## 6. ⑥ 未变清单 —— **PASS**
`viewer.js B9C7281E1EE7A819`、`m1110177 A05C4F2C8DDFCF9A`、5 张真图集 + `atlas171 6480F7FC1914F0C4`、`1110177` 两枚（`56BEF14E53B6316A` / `101355157BEFBD53`）、3 个新 GLB（`A4EA1EC706F7E71C` / `21A1F52546D0CD12` / `B9E06158D88FBBD1`）—— **开工前后哈希全一致**。

## 7. 诚实边界与建议
1. **404 归零 ≠ 上屏**：1110171 的 3 个模型 `ok` 但 `visible 0`、画面 0 px 变化（§1 WARN）；若目标包含"让它们显示"，需再查这 3 个为何不通过可见性门（与 `disabled_no_color_driver` 那 22 个同类嫌疑）。
2. `mtgParamsInfo()` 的 `sample`/`applied_*` **只在 `models(true)` 时有内容**（§2 前提），请写进台账以免误判。
3. Model 层仍无贴图直证、GLB 无顶点色 ⇒ `mtgParams(true)` 得到的仍是**源色面片**（task-76 已记录白占比 90%+，本轮复测一致），**不是成品外观**。

## 8. 纪律与产物
- 只读 `08Lifeafter wiki/**`（未改任何文件）；两阶段各 **1 个**浏览器（主流程 `FXVA78_prof`/10137、探针四态补测 `FXVA78b_prof`/10139），均按 `user-data-dir` 反查真实 PID `taskkill /T /F`（8 / 9 进程）；**端口 10137、10139 无 LISTEN**、我的 profile chrome = 0、全机 chrome 0。
- 产物（仅写 task 允许的三条路径）：本报告 + `FINAL_verify_20260920.json`（含 `stage_extra78` 四态原文）；截图 `sfx_verify_shots7/`（两皮肤默认 OFF/bg、`s171_models_on.png`、`s177_models_T_mtg_F/T.png`）。
