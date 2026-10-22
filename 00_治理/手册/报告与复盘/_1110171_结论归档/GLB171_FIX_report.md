# 1110171 Model GLB 补齐报告（task-77）

## 0. pin

| 项 | 值 |
|---|---|
| effects.json | `DE667C26A99B7DEC` → **`61CE90075C53CA4E`**（140218 → 149005 B） |
| 备份 | `effects.json.bak_glb171_20260919_224942` |
| 导出 | 成功 **28** / 失败 0（共 28 个 Model） |
| 自证 | 仅 `model_glb`/`model_glb_state`/`model_glb_note` 三键变动 = **True**（变动节点 28 个） |

## 1. 缺陷根因（与 lead 口径的差异，必须写清）

- 1110171 的 **28/28** Model 节点**原本 `model_glb` 全为 `null`**、`model_name` 也全为 `null`；源路径只在 `model_fields.ModelName` 里。

- 适配器 `weapon_skin_sfx_adapter.js:468` 是 `meshRel = mf.mesh || n.model_glb || (mname ? 'sfx/' + stemOf(mname) + '.glb' : null)` ⇒ **即使 `model_glb=null`，只要 `ModelName` 在，仍会推导出 `sfx/<stem>.glb` 并发请求**。

- ⇒ **"把 model_glb 置 null + not_shipped" 并不会让 404 消失**（adapter 当前不读 `model_glb_state`，全库仅 :468 一处引用 `model_glb`）。真正的修法只有两条：**(甲) 把 GLB 真导出来（本轮采用）**；**(乙) adapter 增加一个"显式 not_shipped ⇒ 不发请求"的分支（需 lead 改 adapter，我无权改）**。

- 只报 3 条 404 的原因：其余 25 个 Model 在更早的 fail-closed 分支就被跳过（C 类无颜色驱动 / FxIgnore=TRUE / 其它前置条件），根本没走到加载；**但只要它们将来被放行，同样会 404** ⇒ 本轮按"全量补齐"处理。


## 2. 全量 Model ↔ 源件 ↔ 导出对照

| 节点 | 源 .gim（容器#row） | 源 .mesh（容器#row） | 结果 | GLB sha16 | bytes | verts | bbox |
|---|---|---|---|---|---|---|---|
| H_模型_星点01 | `effect_01.gpk#180097` | `effect_01.gpk#180098` | exported | `C0A16DE86FDE3EDB` | 3284 | 32 | [1.4816, 3.5857, 4.1615] |
| H_模型_星点02 | `effect_01.gpk#180100` | `effect_01.gpk#180101` | exported | `D6FAE9DA5B4E6743` | 3284 | 32 | [1.4816, 3.1875, 4.2941] |
| H_模型_光晕02 | `effect_01.gpk#180058` | `effect_01.gpk#180059` | exported | `DE3368F01BE2EEB7` | 7560 | 144 | [0.9554, 2.3633, 2.5961] |
| L_模型_宝石02 | `effect_01.gpk#180055` | `effect_01.gpk#180056` | exported | `16ADDBF8CEAA56AE` | 44652 | 1182 | [0.6726, 1.9766, 2.1816] |
| L_模型_水晶01 | `effect_01.gpk#180091` | `effect_01.gpk#180092` | exported | `E56F5946E976E667` | 36648 | 960 | [0.571, 0.7403, 1.6117] |
| M_模型_水晶02 | `effect_01.gpk#180094` | `effect_01.gpk#180095` | exported | `FFCC2B5E1768C903` | 17508 | 362 | [0.571, 0.7403, 1.6117] |
| L_模型_顶黄 | `effect_01.gpk#180067` | `effect_01.gpk#180068` | exported | `3829A042D14BA944` | 10368 | 190 | [1.2329, 1.6882, 5.0044] |
| L_模型_顶黄_1 | `effect_01.gpk#180025` | `effect_01.gpk#180026` | exported | `9FA79043669E0226` | 17628 | 351 | [1.2329, 1.6882, 5.0044] |
| L_模型_枪口黄 | `effect_01.gpk#180073` | `effect_01.gpk#180074` | exported | `3EE8980E1B28C13E` | 5340 | 69 | [0.9628, 0.7581, 3.4087] |
| M_模型_五线谱 | `effect_01.gpk#180061` | `effect_01.gpk#180062` | exported | `767CDF8EA608EBA9` | 15016 | 296 | [1.4518, 2.7409, 5.1614] |
| M_模型_五线谱_1 | `effect_01.gpk#180064` | `effect_01.gpk#180065` | exported | `C308557BD2B72DA9` | 15016 | 296 | [1.4518, 2.7409, 5.1614] |
| M_模型_环绕蓝 | `effect_01.gpk#180070` | `effect_01.gpk#180071` | exported | `1AF0410C0A6E259E` | 12108 | 230 | [1.6375, 1.5833, 3.9391] |
| L_模型_环绕蓝_1 | `effect_01.gpk#180028` | `effect_01.gpk#180029` | exported | `94FDD9F0DFCD495D` | 4240 | 50 | [0.1604, 0.9776, 2.364] |
| L_模型_环绕蓝_1_1 | `effect_01.gpk#180040` | `effect_01.gpk#180041` | exported | `E72BA869BBDBB136` | 8612 | 150 | [0.1912, 1.4244, 3.1806] |
| L_模型_环绕蓝_2 | `effect_01.gpk#180043` | `effect_01.gpk#180044` | exported | `DBDDCBFB1466DD2A` | 6424 | 100 | [0.1726, 1.2949, 2.5253] |
| M_模型_顶渐变 | `effect_01.gpk#180085` | `effect_01.gpk#180086` | exported | `A4EA1EC706F7E71C` | 5912 | 81 | [0.4644, 0.9531, 3.4339] |
| M_模型_底蓝 | `effect_01.gpk#180082` | `effect_01.gpk#180083` | exported | `4BECC5723C050DCA` | 4908 | 60 | [0.4356, 0.9028, 1.8976] |
| M_模型_枪口紫 | `effect_01.gpk#180079` | `effect_01.gpk#180080` | exported | `0FFE94672DB8B146` | 9908 | 165 | [1.0718, 0.825, 3.5978] |
| L_模型_枪口紫_1 | `effect_01.gpk#180037` | `effect_01.gpk#180038` | exported | `461EA2EF9BD3BA5A` | 6424 | 100 | [0.1726, 1.2949, 2.5253] |
| M_模型_气流暗 | `effect_01.gpk#180088` | `effect_01.gpk#180089` | exported | `5148310B1CEDC121` | 32936 | 616 | [1.6113, 1.3854, 4.699] |
| H_模型_底暗 | `effect_01.gpk#180076` | `effect_01.gpk#180077` | exported | `622C932175B1664B` | 11140 | 208 | [1.0066, 1.8057, 5.3119] |
| H_m_弓弦_1 | `effect_01.gpk#180034` | `effect_01.gpk#180035` | exported | `E67BF1CF86791E0E` | 22432 | 420 | [0.5225, 1.2627, 1.9085] |
| H_m_弓弦_2 | `effect_01.gpk#180031` | `effect_01.gpk#180032` | exported | `80A4CBDA1A32A038` | 3852 | 42 | [0.018, 0.3374, 0.3454] |
| L_模型_球02 | `effect_01.gpk#180256` | `effect_01.gpk#180257` | exported | `2E8C893BAEB020C5` | 15784 | 266 | [0.5639, 0.4083, 0.4193] |
| M_模型_球01 | `effect_01.gpk#180253` | `effect_01.gpk#180254` | exported | `AA8A90F99A89EEE6` | 15784 | 266 | [0.5639, 0.4083, 0.4193] |
| H_模型_球03 | `effect_01.gpk#180259` | `effect_01.gpk#180260` | exported | `21A1F52546D0CD12` | 15784 | 266 | [0.5639, 0.4083, 0.4193] |
| M_模型_球04 | `effect_01.gpk#180262` | `effect_01.gpk#180263` | exported | `B9E06158D88FBBD1` | 15784 | 266 | [0.5639, 0.4083, 0.4193] |
| L_模型_气流02_2 | `effect_01.gpk#180295` | `effect_01.gpk#180296` | exported | `C253E64160CE4C5C` | 6612 | 104 | [0.8249, 1.9884, 6.4451] |

## 3. 已证 / 未证 / 未做

**已证**：28/28 源 `.gim`（c159 绑定文档）+ 同 stem `.mesh`（几何）**全部按名命中**（`effect_01.gpk`，逐行 row/sha16 见上表与资产 JSON）；GLB 由**既有** `export_glb.build_glb`（`set=["fx"]`、texmap 为空集 ⇒ 几何-only）导出，**未新写解析器、未内嵌贴图、未顶替**；effects.json 仅三键变动（自证通过）。
**未证**：导出的 GLB 与源 .gim 绑定文档的**姿态/缩放一致性**未做（既有 dg 批次同口径）；贴图仍未绑（几何-only）。
**未做**：未开浏览器（404 是否消失由 lead 派复测确认）；未改 adapter/viewer.json/viewer.js/board/neox_material.json/其它皮肤。
