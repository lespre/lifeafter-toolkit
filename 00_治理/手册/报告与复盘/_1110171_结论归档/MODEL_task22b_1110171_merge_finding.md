# 1110171 追加定证：为什么开了 SFX 仍空 + 一条已验证的解封配方（task-22 续）

**结论先说**：不是适配器 bug，也不是 GLB 没发布。唯一缺的是**运行时节点数据**：
页面实际消费的是 `viewer.json.effects.nodes`，而 `model_fields`（源 `ModelName` + 源 uniform 轨道）只在**同目录的 `effects.json`** 里。
`viewer.json.effects.nodes` 的 28 个 Model 节点 **0/28 带 `model_fields`** ⇒ 适配器无 `ModelName`/无色源 ⇒ 如实 fail-closed（`disabled_no_color_source:28`）。

## 一、纠正我上一条报告里的两点（均为实测）
| 我先前所说 | 实测（现在） |
|---|---|
| 「108 个 GLB 未发布到 wiki 根 ⇒ 页面必 404」 | **错**：`08Lifeafter wiki\assets\3d\weapon_skin\1110171\sfx\model\` **已有 108 个 GLB**（另 `sfx\tex` 30 个）。生产路径（无任何 override）实测 **14/28 节点 `ok`、`loadErrors: []`** ⇒ 发布已完成，不需要再发。 |
| 「1110171 的 `viewer.json.effects.models_enabled` 是 true」 | **错**：`viewer.json.effects` 与 `effects.json` 均**无 `models_enabled` 键**（`None`）⇒ 1110171 默认也是 **Model OFF**（fail-closed 默认未被改动）。 |

## 二、根因链（每步有读数）
1. `weapon_skin_viewer.js:772`：`const effects = state.config.effects`；`:776` 把它交给 `adapter.attach({effects, manifestUrl})`。
2. `state.config.effects` = **`viewer.json` 的 `effects`**（`__cfgEffects()` 报 `inline_has_effects=false`、`effects_node_count=44`）。
3. `viewer.json.effects.nodes` 结构对比：
   - 1110152：40 节点，**26/26 Model 带 `model_fields`**（`ModelName` + `uniform_tracks{u_emissivecolor_Keyframe,…}`）⇒ 我 task-22 的分支在 1110152 上 22/26 `ok`。
   - 1110171：44 节点，**28/28 Model 无 `model_fields`**（`effects.json` 里 28/28 都有）⇒ 适配器读不到 `ModelName` ⇒ `meshRel=null`、`color=[]`、`bridgeKey=null` ⇒ 28/28 `disabled_no_color_source`。
4. 适配器行为正确：`weapon_skin_sfx_adapter.js:309-310,314,356,374-376`（`mf=n.model_fields||{}`；无颜色源即 fail-closed，绝不默认白）。

## 三、解封配方（已用**运行时注入**验证；资产文件一个都没改）
- 配方 = 把 `effects.json` 的 28 个 Model 节点 `model_fields` 按 **`node.name`** 合入 `viewer.json.effects.nodes[*].model_fields`。
  - 名称匹配：**同序号 28/28 完全一致**，集合交集 28 ⇒ 可按名或按序合入，零歧义。
  - 产物：`03拆包产物\_target_1110171\MODEL_patch_1110171_model_fields.json`（22,685 B，28 行，key=节点名，value=适配器实际读取的字段子集：`ModelName/uniform_tracks/DirType/RenderOrder/FxStartTime/FxLifeSpan/tracks`）。
- 验证方式（A/B 都做了）：
  - **对照组（只装探针、不合并）**：`__probe()` 前 3 行 = `bridgeKey:null, color_source:null, status:'disabled_no_color_source'`（`MODEL_recipe_marker.json`）。探针被调用 1 次（`__calls=1`、localStorage 同步为 1）⇒ 证明 `attach` 确实走我的包裹层，先前 `__patchHit=undefined` 只是**我在点击 SFX 之前就读了**（attach 由 SFX 按钮触发），已排除。
  - **实验组（合并 + models(true)）**：`{ok:14, disabled_no_color_source:14}`，`loadErrors: []`，JS 异常 **0**；14 行 `bridgeKey` 全部非空、色源分别为 `u_emissivecolor_Keyframe`(5) / `u_main_color3_Keyframe`(5) / `u_main_color1_Keyframe`(3) / `u_diffuse_color_Keyframe`(1)。
  - **生产路径复核**：不加任何 models 基址 override（走 `assets/3d/weapon_skin/1110171/sfx/model/*.glb`）⇒ 同样 `{ok:14, no_color_source:14}`、`loadErrors: []`。
- 结果文件：`MODEL_recipe_1110171_prodpath.json`、`MODEL_recipe_1110171_run2.json`、`MODEL_recipe_marker.json`；截图 `MODEL_prodpath_1110171_{off,on}.png`（sha256 on=`5dacc808bf0bdd48`）。

## 四、像素与目视（亲看，不美化）
| 项 | OFF | ON（14 节点） |
|---|---|---|
| 全白(≥250) 占比（y<740） | 0.000%（4 px） | **0.019%（157 px）** |
| 画面变化 | — | 39,508 px = **3.916%** 画布；bbox x[168,648] y[326,545]；变化像素均色 RGB≈(100.6,126.9,155.2)（淡蓝） |
| 平均亮度 | 39.1 | 43.7 |

**白块问题没有复现**（0.019%），但目视 `MODEL_prodpath_1110171_on.png`：14 个无贴图 Model 呈现为**大片半透明蓝白飘带 + 若干矩形薄片**（其中约 3–4 个明显是平直矩形卡片）。
比"白块"好，但**仍未达到游戏内特效观感**；原因同 task-22 报告：源端靠 `uber_fx_common.fx::TShader` 着色器语义，只复现均匀量不够。
另：14/28 节点源里**确实没有颜色轨道**（`u_overall_opacity_Keyframe`/`u_depth_bias_Keyframe` 对 1110171 也是 0/28 有值）⇒ 这 14 个按纪律保持 fail-closed，**没有**给常量或自拟色。

## 五、需你裁决的一件事
配方落地要改 **`08Lifeafter wiki\assets\3d\weapon_skin\1110171\viewer.json`**（不在我写域内）：
把 28 行 `model_fields` 合入 `effects.nodes`。要不要做、由谁做（env-auditor？你？），以及是否顺带把 `models_enabled` 维持**缺省不写**（保持默认 OFF），请示下。
仅合并、**不动** `effects.json`、不动适配器、不改贴图。

## 六、命令/文件清单
- 配方与证据脚本（均在 `%TEMP%`）：`p27_1171_patch.py`（生成 patch）、`p27_1171_recipe.py` / `p27_1171_recipe2.py`（注入+截图）、`p27_1171_prodpath.py`（生产路径）、`p27_1171_marker.py`（对照组/探针计数）、`p27_1171_metrics*.py`（像素统计）。
- 未修改任何资产文件：`viewer.json` mtime 仍 `2026-09-18 01:45:45`、`effects.json` 仍 `02:03:11`；适配器 sha16 仍 `2E61C5234BB37CED`（55,263 B）。
- 残留未解项：一次 `404 (File not found)` 与一次 `ERR_CONNECTION_REFUSED` 控制台条目（非 GLB：`loadErrors:[]`）；未定位到具体 URL，标 unresolved。
