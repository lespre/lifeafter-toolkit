# task-22 交付：无 Tex0 的 Model 走「源自发光/叠加分支」

**唯一写域**：`08Lifeafter wiki/assets/weapon_skin_sfx_adapter.js`（未碰 viewer.js/manifest/board/贴图）
**改前**：sha16 `FFF6180DF4ED5BAB` · 42,590 B · 备份 `_target_1110171\MODEL_adapter_before_FFF6180DF4ED5BAB.js`
**改后**：sha16 `2E61C5234BB37CED` · 55,263 B · 773 行 · `node --check` OK

## 逐处改动（行号 + 原 → 新）
| 行号 | 原文（要点） | 新文（要点） |
|---|---|---|
| L210-238 | `applyModelMaterial`：`m.color.setRGB(rgb)` + `additive = (MODEL_BLEND==='additive')` + `opacity=a*k` + `emissiveIntensity=hiv` | **color 置黑**（消除 GLB 白色 PBR 基色）+ `emissive=源rgb` + `metalness=0/roughness=1` + **blending 由源 `TransparentMode` 直译**（'0'→Normal，'2'→Additive）+ `opacity=A/255 × 源 u_overall_opacity` + `polygonOffset` ← 源 `u_depth_bias` |
| L64-90（新增） | — | `SRC_BRIDGE_1110152`：26 行**源值桥**（键=`<ModelName 文件名>#<同 stem 序号>`，值=tm/rb/tt/xml_line/op/db/tex0），**runtime 字段优先、桥只补缺** |
| L127-133（新增） | — | `trackFirst()`：取轨道 t=0 首值（u_overall_opacity / u_depth_bias） |
| L355-362 | `color: flat(ut.u_emissivecolor_Keyframe)` | 颜色源**优先级链**：`u_emissivecolor` → `u_diffuse_color` → `u_main_color1/2/3`（跨皮肤通用），并记 `colorSource` |
| L374-376 | `if(!MODELS_ON) disabled_fail_closed else loadModel` | 顺序改为：`hasTex0 → disabled_texture_unresolved`（2 环节点，不顶替）→ **无颜色源 → `disabled_no_color_source`（绝不默认白）** → 默认关 → loadModel |
| L650-676（新增） | — | `__probe().modelTable` 26 行：node/bridgeKey/meshRel/has_Tex0/texture_source/color_source/tm/rb/tt/xml_line/op/db/源色/branch/status/applied + `modelBranchBasis` + `textureUnresolved` |
| L735-736 | `models(true)` 只翻 visible | 追加：`hasTex0`/无颜色源 ⇒ **即使 models(true) 也不加载**（fail-closed） |
| — | `DirType='2'→面向相机(billboard)`（本轮试做） | **实测视觉更差**（面片正对相机 ⇒ 大片平白卡）⇒ **已回退**，只留说明注释；DirType 语义仍 unresolved |

**源级 / 近似 / unresolved**
- 源级：颜色（`u_emissivecolor` 等）、不透明度（A × `u_overall_opacity`）、`TransparentMode`/`RenderBias`/`TrackType`/`DirType` 原值
- 近似（依据已写进代码注释与 `modelBranchBasis`）：blending 映射（源属性值直译，语义未在源端验证）；`u_depth_bias`→polygonOffset（尺度语义未证）
- unresolved：`u_emissive_highlight_intensity` 语义=高光项 ⇒ **不作全局强度**（`emissiveIntensity=1` 中性恒等），原值留档；`u_overall_opacity > 1` 的增强项无法套用（clamp 到 1）

## 验收读数
| 项 | 结果 |
|---|---|
| `__cfgEffects()` | 1110152 `handle_present=true · effects_status=partial · effects_node_count=40 · adapter_present=true`；1110171 `handle_present=true · effects_node_count=44` |
| 逐节点 status（1110152 默认关） | `{disabled_fail_closed:22, disabled_no_color_source:2, disabled_texture_unresolved:2}` |
| 逐节点 status（1110152 models(true)） | `{ok:22, disabled_no_color_source:2, disabled_texture_unresolved:2}` |
| 逐节点 status（1110171，`models_enabled=true`） | `{disabled_no_color_source:28}`（28/28 无颜色源 ⇒ 不加载） |
| **全白像素占比（canvas y<740，250/255）** | 1110152：**改前 ON 10.063% → 改后 ON 1.924%**（OFF 0.021%）；1110171 OFF=ON=0.011%（未渲染） |
| 两个环节点 | `L_m_圈3→tex_ring_fz01_x06.tga`、`H_m_圈5→tex_ring_keji_hgz01_04.tga` ⇒ `disabled_texture_unresolved`，`__probe().textureUnresolved` 暴露，**未用白色/自拟贴图** |
| JS 异常 | **0**（`MODEL_verify_after.json`） |
| `wiki_selfcheck.py` | **PASS 63 · FAIL 1**（唯一 FAIL＝已知 1110171 mesh[5,3,6] SwiftShader 假阳性）✓ 达线 |
| 旋转回归（1110152，24 mesh 在场） | idle 逐帧 `projCenter` **distinct=1（零跳变）**；drag net (−0.0289,+0.0684)、maxstep 0.0077、`clipped=false` |
| 默认关不回归（同 harness、逐像素） | 1110024 / 1110129 / 1110152 / 1110171 四皮肤 **SFX 关态与默认态均 0 px 差异** ✓ |
| 26 行节点表 | `FXADAPT/MODEL_verify_after.json → skins.1110152.models_on.table` + `MODEL_src_values_1110152.json`（源值，带 xml_line） |

## 目视（亲看，不美化）
`MODEL_after_1110152_on_on.png`：**白块已显著收敛（10.06%→1.92%）**，但 **24 个无贴图 Model 仍呈现为大片淡青色面板**，
字形/朝向与本机观感差距仍在 ⇒ **ON 状态尚不能称"游戏内特效"**。原因（如实）：这些是**面片网格**，源端靠
`DecalTech = shader\uber_fx_common.fx::TShader` 的着色器语义（无贴图、无 alpha 掩码）呈现；我们只复现了源**均匀量**，
未复原该 shader ⇒ 只能到"源驱动自发光近似"。`DirType` 面向相机试过更差，已回退。

## 下一步（需他人/资产侧）
1. **1110171 的 108 个 GLB 未发布到 wiki 根**：`assets/3d/weapon_skin/1110171/sfx/model` = 0 files（108 个在 `03拆包产物\_gim_out\1110171\sfx\model`）⇒ 页面必 404；发布后本分支即可跑。
2. **1110171 effects.json 缺颜色/不均匀量轨道**：28/28 `color_source=null`（`u_emissivecolor` 仅 5 个节点有关键字且无值），`u_overall_opacity`/`u_depth_bias`/`TransparentMode`/`RenderBias` 也未抽 ⇒ 现由 `SRC_BRIDGE_1110152` 覆盖 1110152，1110171 需同类抽取。
3. 两个环节点贴图：由 freeze-auditor 用新破解的 `path→entry`（`u32_7=mm3(path,0x77777777)`）定位后即可解除 `texture_unresolved`。
