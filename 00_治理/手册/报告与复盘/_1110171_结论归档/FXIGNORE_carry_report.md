# FXIGNORE 携带报告（task-69）—— 显示集收缩，不是美化、不是回归

## 0. pin 与自证

| 皮肤 | 改前 sha16 | 改后 sha16 | 字节 | 备份 |
|---|---|---|---|---|
| 1110177 | `9C60BED52F3014E3` | **`F3C0623DC3CF684E`** | 565949 → 575605 | `effects.json.bak_fxignore_20260919_220839` |
| 1110171 | `1A80510416D2203D` | **`1742FA1FC56C3093`** | 129586 → 130095 | `effects.json.bak_fxignore_20260919_220839` |

**自证门**：除新增 `fxIgnore`/`fx_ignore_source`（及缺源时的 `fx_ignore_status`）外，**每个节点的其余字段 canonical JSON 逐字节相同**（脚本判定不通过即拒绝写盘）：1110177 = True、1110171 = True；两份 `json.load` 均可读通。

## 1. 计数

| 皮肤 | 节点数 | TRUE（= 源禁用 ⇒ ignored） | FALSE | 缺源 |
|---|---|---|---|---|
| 1110177 | 89 | **4** | 85 | 0 |
| 1110171 | 44 | **28** | 16 | 0 |

源：1110177 = `fx_skin_2003_029_hit.sfx`(17F/4T) + `fx_skin_2003_029_jisha.sfx`(45F) + `gres\0057.gpk#32153`(23F 全 FALSE)；1110171 = `gpk_effect_01_f74635_59115620b779a5e8.bin`（28 TRUE / 16 FALSE）。属性正则一律 `\s*=\s*`（这两个 sfx 是 GBK，写法为 `Name = "x"`）。

## 2. 被置为 ignored 的节点（逐条）

### 1110171（28 个）
| 节点 | tag | renderable_by_adapter=true | 有贴图 | 源 |
|---|---|---|---|---|
| H_m_弓弦_1 | Model | 否 | 否 | `gpk_effect_01_f74635_59115620b779a5e8.bin:H_m_弓弦_1` |
| H_m_弓弦_2 | Model | 否 | 否 | `gpk_effect_01_f74635_59115620b779a5e8.bin:H_m_弓弦_2` |
| H_p_光圈01 | ParticleSystem | **是** | 是 | `gpk_effect_01_f74635_59115620b779a5e8.bin:H_p_光圈01` |
| H_p_光圈02 | ParticleSystem | **是** | 是 | `gpk_effect_01_f74635_59115620b779a5e8.bin:H_p_光圈02` |
| H_星点粒子 | ParticleSystem | **是** | 是 | `gpk_effect_01_f74635_59115620b779a5e8.bin:H_星点粒子` |
| H_星点粒子_3 | ParticleSystem | **是** | 是 | `gpk_effect_01_f74635_59115620b779a5e8.bin:H_星点粒子_3` |
| H_模型_光晕02 | Model | 否 | 否 | `gpk_effect_01_f74635_59115620b779a5e8.bin:H_模型_光晕02` |
| H_模型_底暗 | Model | 否 | 否 | `gpk_effect_01_f74635_59115620b779a5e8.bin:H_模型_底暗` |
| H_模型_星点01 | Model | 否 | 否 | `gpk_effect_01_f74635_59115620b779a5e8.bin:H_模型_星点01` |
| H_模型_星点02 | Model | 否 | 否 | `gpk_effect_01_f74635_59115620b779a5e8.bin:H_模型_星点02` |
| L_p_光刺_01 | ParticleSystem | **是** | 是 | `gpk_effect_01_f74635_59115620b779a5e8.bin:L_p_光刺_01` |
| L_p_光刺_02 | ParticleSystem | **是** | 是 | `gpk_effect_01_f74635_59115620b779a5e8.bin:L_p_光刺_02` |
| L_模型_宝石02 | Model | 否 | 否 | `gpk_effect_01_f74635_59115620b779a5e8.bin:L_模型_宝石02` |
| L_模型_枪口紫_1 | Model | 否 | 否 | `gpk_effect_01_f74635_59115620b779a5e8.bin:L_模型_枪口紫_1` |
| L_模型_枪口黄 | Model | 否 | 否 | `gpk_effect_01_f74635_59115620b779a5e8.bin:L_模型_枪口黄` |
| L_模型_气流02_2 | Model | 否 | 否 | `gpk_effect_01_f74635_59115620b779a5e8.bin:L_模型_气流02_2` |
| L_模型_水晶01 | Model | 否 | 否 | `gpk_effect_01_f74635_59115620b779a5e8.bin:L_模型_水晶01` |
| L_模型_环绕蓝_1_1 | Model | 否 | 否 | `gpk_effect_01_f74635_59115620b779a5e8.bin:L_模型_环绕蓝_1_1` |
| L_模型_球02 | Model | 否 | 否 | `gpk_effect_01_f74635_59115620b779a5e8.bin:L_模型_球02` |
| L_模型_顶黄 | Model | 否 | 否 | `gpk_effect_01_f74635_59115620b779a5e8.bin:L_模型_顶黄` |
| M_g_光晕暗_01 | Sprite | **是** | 是 | `gpk_effect_01_f74635_59115620b779a5e8.bin:M_g_光晕暗_01` |
| M_g_光晕暗_02 | Sprite | **是** | 是 | `gpk_effect_01_f74635_59115620b779a5e8.bin:M_g_光晕暗_02` |
| M_模型_五线谱 | Model | 否 | 否 | `gpk_effect_01_f74635_59115620b779a5e8.bin:M_模型_五线谱` |
| M_模型_底蓝 | Model | 否 | 否 | `gpk_effect_01_f74635_59115620b779a5e8.bin:M_模型_底蓝` |
| M_模型_枪口紫 | Model | 否 | 否 | `gpk_effect_01_f74635_59115620b779a5e8.bin:M_模型_枪口紫` |
| M_模型_气流暗 | Model | 否 | 否 | `gpk_effect_01_f74635_59115620b779a5e8.bin:M_模型_气流暗` |
| M_模型_水晶02 | Model | 否 | 否 | `gpk_effect_01_f74635_59115620b779a5e8.bin:M_模型_水晶02` |
| M_模型_球01 | Model | 否 | 否 | `gpk_effect_01_f74635_59115620b779a5e8.bin:M_模型_球01` |
### 1110177（4 个）
| 节点 | tag | renderable_by_adapter=true | 有贴图 | 源 |
|---|---|---|---|---|
| H_模型核心电小_5 | Model | 否 | 否 | `fx_skin_2003_029_hit.sfx:H_模型核心电小_5` |
| M_shandian_04 | ParticleSystem | 否 | 是 | `fx_skin_2003_029_hit.sfx:M_shandian_04` |
| M_粒子_科技 | ParticleSystem | 否 | 是 | `fx_skin_2003_029_hit.sfx:M_粒子_科技` |
| M_鬼火细线_2 | ParticleSystem | 否 | 是 | `fx_skin_2003_029_hit.sfx:M_鬼火细线_2` |

## 3. 性质声明

**这是一次显示集收缩**（不渲染源 `FxIgnore=TRUE` 的节点），**不是美化，也不是回归**：只按源语义把被禁用的节点从渲染集里去掉；未被禁用的节点其字段一字未动（自证门保证）。1110171 预计有 **8** 个当前 `renderable_by_adapter=true` 的节点会因此不再渲染（lead 给的预期是 8 个）；1110177 预计 **0** 个。

## 4. 已证 / 未证 / 未做

**已证**：两皮肤各节点的 `fxIgnore` 均取自**其自身来源**（hit/jisha 按 `source_sfx` 分文件、dg 按容器 row、1110171 按 bin），逐节点带 `fx_ignore_source` provenance；缺源节点写 `fx_ignore_status="no_source_node"`（不编造）；除新增键外零改动。
**未证**：`FxIgnore=TRUE` 在**引擎侧的实际行为**（我们按 lead 定证的语义解释为"禁用"；本轮不重新验证语义）；1110171 的 bin 是否为其唯一 sfx 源（按 task 给定的唯一源使用）。
**未做**：未开浏览器（验收另派）；未改 adapter/viewer.json/viewer.js/board/neox_material.json；未动任何贴图字段。
