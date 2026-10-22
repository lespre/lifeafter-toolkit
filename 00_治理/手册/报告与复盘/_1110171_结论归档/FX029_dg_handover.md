# FX029 · task-62 (b) 交接书 —— 把 `_dg.sfx` 的 23 节点合并进 `1110177/effects.json`

> 写给"下一棒"（新 agent 或 lead 本人）。**只做 (b) 合并**；(a) 16 个 `.gim`→GLB 导出 = env-auditor（写域 `1110177/sfx/dg/`）；(c) 测量 = viewer-auditor。
> 纪律：**每完成一步立即写盘并报 sha16**；改前 `copy2` 备份；不碰 viewer.js / viewer.json / manifest / board / registry；adapter **不需要改**（除非另批）。

---

## 0. 当前 pin（2026-09-19 18:5x，做 (b) 前请重新哈希确认）
| 对象 | sha16 | size |
|---|---|---|
| `08Lifeafter wiki/assets/weapon_skin_sfx_adapter.js` | `79F5F2B86D321995` | 90,499 B |
| `08Lifeafter wiki/assets/3d/weapon_skin/1110177/effects.json` | `399223E5F0B15813` | 441,573 B |
| `08Lifeafter wiki/assets/3d/weapon_skin/1110177/viewer.json` | `FD29DCD83C718B44` | 493,771 B |
| `08Lifeafter wiki/assets/weapon_skin_viewer.js` | `B9C7281E1EE7A819` | 379,489 B |
| `03拆包产物/_target_1110171/FX029_dg_inventory.json` | （dg 清单，11,353 B） | — |

默认关基线帧 sha16（**合并后必须不变**）：`61A8171DAE53D73A`（1578×902 全页 PNG；取自 `FX029_models_measure.json` §s03/s04）。

---

## 1. 脚本与用法（都在 `E:\la拆包项目\03拆包产物\_target_1110171\`）
| 脚本 | 作用 | 跑法 |
|---|---|---|
| `FX029_dg_unpack.py` | 解 `_dg.sfx`（生 `FX029_dg_inventory.json`） | venv python 直接跑，无参数 |
| `FX029_model_keyframes.py` | **源字段注入模板**（task-61 用的；(b) 请仿写一份 dg 版，勿原地改） | venv python 直接跑 |
| `FX029_models_expected.py` | 从 `effects.json` 生成 26 行期望表 + 打印 `class_counts` | venv python |
| `fx061_measure.py` | 浏览器测量夹具（**只给 viewer-auditor 用**；本交接不作要求） | venv python |
| `%TEMP%\fx061_verify.py` | 块级核对：注入的 `uniform_tracks` 与节点自身块 26/26 一致 | venv python |

python：`C:\Users\Administrator\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe`

## 2. `_dg.sfx` 已证事实（可直接引用，勿重解）
- `E:\mrzh\Documents\gres\0057.gpk` **row 32153** · `off=652,984` · `comp=4,654` · `dec=66,424` · `flag=12(zstd)` · `block_base=1,823,837,828` · **`payload = block_base + off + 20` = 1,824,490,832** ⇒ 解出 **66,424 B，sha16 `9F4FE3A6AD3F8851`**（我解的和 env-auditor 独立解的**逐位一致**）。
- 格式 GBK 明文 XML：`<FxGroup Name="MyFx" FxLifeSpan="0.000" Loop="FALSE" EndLessPlay="FALSE" …>`；**真时长由节点推导 = 1.500 s**。
- **23 节点 = Dummy 3 / Model 16 / ParticleSystem 3 / ParticleRes 1**；**全 23 节点无 Bool 宏**（`macros:{}`）。
- 16 个 Model 的 `ModelName` = `effect\mesh\weapon\skin\skin_2003_029\mod_skin_2003_029_dg_wl_01..08_djs.gim` + `…_dg_{01,02,04,08,09,10,12,14}_djs.gim`（**16/16 新增；与 `_hit.sfx` 交集 0**）。
- **3 个与现有同名、必须隔离的 Dummy**：`L_空特效`、`L_空特效_1_1`、`L_空特效_2`。
- dg 驱动**声明节点数**（不是帧数）：`u_overall_opacity` 15 · `u_emissivecolor` 9 · `u_dissolve_amount` 5 · `u_emissive_desaturate` 3 · `u_emissive_highlight_intensity` 3 · `u_depth_bias` 3 · `u_mask_power` 1。
- 配套件（**本轮不解**）：`fx_skin_2003_029_daoguang_02.sfx` = row 31106（dec 9,922，另 `effect_01.gpk#38416`）；`.spr` = `effect_01.gpk#208478`(smoke25, 1,814 B) / `#211384`(tex_special_fangkuai_tp52, 200 B)；`glow_16_yh_djs.tga` 按名 0 命中（**内容候选已在用**，不许手填绑定）。

## 3. (b) 要注入什么（字段清单 + 来源规则）
对 dg 的 **16 个 Model** 节点，逐节点从 `_dg.sfx` 该节点**自身块**注入（口径与 task-61 完全一致）：
1. `source_sfx = "fx_skin_2003_029_daoguang.sfx"`（或实际文件名）—— **隔离键**，用于区分三份 sfx；同名 Dummy 靠它 + 重命名消歧。
2. `model_name = <该节点 ModelName 原值>`（源 .gim 路径）；**`model_glb = "sfx/dg/<stem>.glb"`**（env-auditor 的导出文件名必须是 `<stem>.glb`，stem = 去 `.gim` 的 basename）。
3. `model_fields.uniform_tracks = { "<u_XXX_Keyframe>": [ {time, value} … ] }` —— 解析规则：取该节点块内 `<Uniforms>…</Uniforms>`，再取 `<u_*_Keyframe ChangeType Interpolator><Frame Time Value/></u_*_Keyframe>`；`Value` 含逗号 ⇒ 数值数组，否则标量数。**原样注入、不做任何换算/解释**。
4. `model_fields.uniform_tracks_meta`（每轨 `ChangeType`/`Interpolator` 原值）+ `model_fields.keyframe_source`（provenance：sfx/节点/轨道清单/帧数）。
5. 源属性小写键：`transparent_mode / render_bias / track_type / render_order / dir_type / render_level / fx_start_time / fx_life_span / model_name / post_process_kind / scale_type`（取自该节点头部属性，缺失则**不写**）。
6. `model_fields.shader.ShaderComponent`（含 `<Semantic>` 声明与 Bool 宏条目）—— 若 dg 无宏就写空数组，**不要编**。
7. **不要写** `models_enabled`（保持默认关）、不要写任何贴图绑定（`tex_bound=false` 一律）。
8. Dummy/PS/ParticleRes 节点：按现有 effects.json 同 tag 结构登记；**3 个同名 Dummy 改名**（建议 `L_空特效__dg`、`L_空特效_1_1__dg`、`L_空特效_2__dg`），并**同步改写引用它们的 `parent` 字段**（dg 内部引用必须指向改名后的 dg 版，不能串到 `_hit`/`_jisha` 的同名节点）。
9. `effects.json` 顶层：`model_field_patch.dg_merge = {when, by, source_sfx, rows, tracks, frames, dummies_renamed[], sha_of_sfx:'9F4FE3A6AD3F8851'}`。

## 4. 验收断言（做完逐条核）
1. **节点总数 66 → 89**（+23）；tag 分布：Model 26→42、ParticleSystem 15→18、Dummy 11→14、ParticleRes 1→2、Sprite 13 不变。
2. `source_sfx` 分布：`fx_skin_2003_029_hit.sfx` 7 Model、`…_jisha.sfx` 19 Model、dg 新增 23 节点用独立值；**无跨文件同名**（3 个 Dummy 已隔离，且**全局 `name` 唯一**）。
3. **A/B/C 分类（dg 16 个 Model 的源侧期望）**：`u_emissivecolor` 声明 9 个 ⇒ **A +9**；dg **无 `u_diffuse_color` 声明** ⇒ **B +0**；其余 **C +7**（C 不渲染，`fallback_reason=no_color_driver_unresolved`）。⇒ 合并后全表期望 **A=25 / B=7 / C=10**（用 `FX029_models_expected.py` 打印的 `class_counts` 复核；若不等，先查"变体拼写 `u_emissive_color` 是否出现"）。
4. `model_glb` 26+16=42 个路径**全部可解析**（16 个新 GLB 必须在 `1110177/sfx/dg/` 下真实存在，缺一个就报缺，**不得回退顶替**）。
5. JSON 可解析 + `node --check`（adapter 未改时应 exit=0）；**`effects.json` 新 sha16 与旧值一并报 lead**。
6. **默认关不变**：合并 + lead 重新内联后，`models(false)`/默认关全页帧 sha16 **必须仍为 `61A8171DAE53D73A`**；(c) 由 viewer-auditor 测；若该帧变了，**先判是不是内联/缓存问题，再判是不是我们引入了默认态渲染**。
7. 报告纪律：在 `FX029_models_report.md` **新增 §19+**（不要改动历史 §15–§18）；分「已证/未证/未做」。

## 5. 坑（都踩过，照抄可避）
- **gres 偏移 = `block_base + row_off + 20`**，不是 res 族的 `o+36`。
- **不要按名去猜贴图**：`<Model>` 节点在源里**不声明任何贴图槽**（hit 0/7 + jisha 0/19）⇒ "白卡片"是源数据无贴图的必然结果，本链不绑是**正确 fail-closed**。
- **`u_dissolve_amount` 明确不做**（lead 裁决 2026-09-19，选乙）：12 个组件只声明 `amount`，最小式仍需 `mask = t_dissolve_tex`（**无任何节点声明**）与 `base = Tex0.a`（仅 1 节点有）⇒ mask 源不存在；按最小式接线只能造"无源 mask"，会引入白块/黑洞且无可观测差异。⇒ 只登记 `dissolve_state='declared_blocked(mask_source_unavailable)'`。
- **unitScale**：Model 实例缩放已乘 `U()`=0.1（随 `unitScale` 开关）；dg 新模型**同口径**（GLB 顶点空间同 sfx=cm）。源侧数字参考：GLB bbox 最大维度 163.07 / 武器对角线 15.4552 = 10.55× ⇒ ×0.1 = 1.055×。
- 控制台是 GBK：**别用含中文的内联 pwsh/python 一行命令**，写临时 `.py` 文件并 `sys.stdout.reconfigure(encoding='utf-8')`。
- 浏览器礼仪：单浏览器、专用 profile + 端口 10087、按 profile 反查 PID `taskkill /T /F`、收尾核对 `chrome.exe` 残留 = 0。

## 6. task-61 已完成部分（供对照，勿重做）
族 = `shader\uber_fx_common.fx`（两 sfx 唯一 shader 路径；容器 `res.gpk row 15714 / dec 26,799 / flag 2 lz4`）· Model 26/26 注入源关键帧 **96 轨道 / 254 帧** · A=16/B=7/C=3 · 材质（复原后）Additive16+Normal7+无材质3 · 默认关 3 帧逐字节相同 · `models(true)` visible=23 收敛 277 ms 异常 0 · highlight 硬门 +0.06pp ⇒ 默认 true · 白像素 5.78%（单位修复前 15.86%）。
