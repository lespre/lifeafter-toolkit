# 1110177 精灵表贴图 .spr 硬尺寸锚校正 — task-55

## 结论
- **不做新绑定**：按 .spr 声明尺寸硬过滤后候选仍多解（512x512: 池A 120 + 池B 668；256x256: 684 + 2529）=> 按纪律不强行定唯一，只登记 top5（`_spr_hard/candidates.json`）。
- **lightning07_cs.spr**：旧候选 256x256 与 .spr 声明 **512x512/16 帧** 硬矛盾 => 绑定**撤回**（texture_candidate=null，texture_status=unresolved_spr_hard_dims_mismatch，该节点 renderable_by_adapter=false）。
- **lightning_01.spr / shandian_05_yh_djs.spr**：保留 task-51 绑定（dims 512x512 / 256x256 与声明吻合），证据级别升为 content_candidate_spr_hard_dims_match，并补 spr_hard_dims / spr_source / dims_match。
- **自我纠错**：第一轮 periodic 度量退化（最大 1.28e8，DC 除近零）判出的 REPLACE **已作废**，3 张误落盘 PNG 已删：["lightning07_cs__d957663b.png", "lightning_01__d957663b.png", "shandian_05_yh_djs__824998f5.png"]

## 1. 三条 .spr 直证（容器/row/dec/flag/sha16 + 原文）
- `lightning07_cs.spr` 容器 effect_01.gpk row 207659/207659 dec 582 flag 12 sha16 7d0ecce9fd3cddd7 首行 512x512 frames=16 param=10000 帧矩形前三 [[0, 0, 128, 128], [128, 0, 256, 128], [256, 0, 384, 128]] 算术=True
- `lightning_01.spr` 容器 effect_01.gpk row 207671/207671 dec 550 flag 12 sha16 6e8b303b2233eb92 首行 512x512 frames=16 param=10000 帧矩形前三 [[0, 0, 128, 128], [128, 0, 256, 128], [256, 0, 384, 128]] 算术=True
- `shandian_05_yh_djs.spr` 容器 effect_01.gpk row 207712/207712 dec 168 flag 12 sha16 94dedcf52b8712c8 首行 256x256 frames=4 param=1000 帧矩形前三 [[0, 0, 63, 255], [64, 0, 127, 255], [128, 0, 191, 255]] 算术=True

## 2. 候选统计与判定（有界度量：periodic>50 视为退化剔除）
- `lightning07_cs.spr` 512x512 / 16 帧 / grid_ok=True => 池A 120 + 池B 668 => **MULTI_CANDIDATES_NOT_BOUND**
  - top1 effect_01.gpk#205896 `cc800e7686280515.dds` dims [512, 512] score 27.01101 edge 0.0187 center 0.273 alpha_mean 14.12
  - top2 effect_01.gpk#209267 `6de02eb8b382ed38.dds` dims [512, 512] score 26.26184 edge 0.0146 center 0.0 alpha_mean 41.03
  - top3 effect_01.gpk#208527 `bfd296ac86302af5.dds` dims [512, 512] score 25.09188 edge 0.0042 center 0.774 alpha_mean 5.05
  - top4 effect_01.gpk#207122 `7671202e9d044368.dds` dims [512, 512] score 24.72001 edge 0.0129 center 0.0 alpha_mean 55.01
  - top5 effect_01.gpk#208450 `72c9f5b098a57dea.dds` dims [512, 512] score 24.2247 edge 0.0308 center 0.839 alpha_mean 59.01
- `lightning_01.spr` 512x512 / 16 帧 / grid_ok=True => 池A 120 + 池B 668 => **MULTI_CANDIDATES_NOT_BOUND**
  - top1 effect_01.gpk#205896 `cc800e7686280515.dds` dims [512, 512] score 27.01101 edge 0.0187 center 0.273 alpha_mean 14.12
  - top2 effect_01.gpk#209267 `6de02eb8b382ed38.dds` dims [512, 512] score 26.26184 edge 0.0146 center 0.0 alpha_mean 41.03
  - top3 effect_01.gpk#208527 `bfd296ac86302af5.dds` dims [512, 512] score 25.09188 edge 0.0042 center 0.774 alpha_mean 5.05
  - top4 effect_01.gpk#207122 `7671202e9d044368.dds` dims [512, 512] score 24.72001 edge 0.0129 center 0.0 alpha_mean 55.01
  - top5 effect_01.gpk#208450 `72c9f5b098a57dea.dds` dims [512, 512] score 24.2247 edge 0.0308 center 0.839 alpha_mean 59.01
- `shandian_05_yh_djs.spr` 256x256 / 4 帧 / grid_ok=True => 池A 684 + 池B 2529 => **MULTI_CANDIDATES_NOT_BOUND**
  - top1 _sfx_029_pool `e6c0fc9e4c328495.dds` dims [256, 256] score 29.68287 edge 0.0397 center 0.03 alpha_mean 33.09
  - top2 effect_01.gpk#206871 `948f4a8a2e9fa2c1.dds` dims [256, 256] score 29.5993 edge 0.0656 center 0.439 alpha_mean 93.66
  - top3 effect_01.gpk#206902 `c4df934421f1ac10.dds` dims [256, 256] score 29.27551 edge 0.0019 center 1.0 alpha_mean 3.31
  - top4 _sfx_029_pool `597e6a4693411b12.dds` dims [256, 256] score 29.05978 edge 0.0408 center 0.65 alpha_mean 157.17
  - top5 _sfx_029_pool `597e6a4693411b12.dds` dims [256, 256] score 29.05978 edge 0.0408 center 0.65 alpha_mean 157.17

## 3. 新落盘 PNG
无（本轮不替换绑定）。第一轮误落盘 3 张已删；task-51 的 99 张 PNG + 3 个 .spr **全部保留**。候选清单：`1110177/sfx/tex/_spr_hard/candidates.json`。

## 4. effects.json 改动
- task-51 原态 `16b02ba0b3a48247` => 第一轮误判后 `79e3a2108d671616` => **纠正后 `0bb7ca57e7d1be0b`**；models_enabled **仍缺省**。
- 逐处：[{"node": "H_p_闪电", "texture": "lightning07_cs.spr", "from": "lightning07_cs__d957663b.png", "to": null, "why": "old 256x256 contradicts .spr hard 512x512; first-pass REPLACE verdict void (degenerate metric)"}, {"node": "H_ shandian01_1_1", "texture": "lightning_01.spr", "kept": "lightning_01__662b911e.png", "dims_match": true}, {"node": "M_lizi_闪电_01", "texture": "shandian_05_yh_djs.spr", "kept": "shandian_05_yh_djs__a9aa4caf.png", "dims_match": true}]

## 5. unresolved 原因
1. lightning07_cs：512x512 候选 788 条（120+668），有界度量下无唯一解 => 保持 unresolved，旧 256x256 候选已撤回。
2. lightning_01 / shandian_05_yh_djs：dims 吻合但图集本体名字轴不可得 => 仅 content_candidate_spr_hard_dims_match，**不是源图直证**。
3. 19 条无锚点声明贴图：保持 unresolved；未再试路径写法（已穷举 8,218,116 行 x 1,099,560 写法 = 0/31）。

## 6. 只读校验
- effects.json 可解析、schema=lifeafter-weapon-skin-effects/3、66 节点、models_enabled 不存在（默认关）；绑定节点 9 -> **8**（lightning07_cs 已撤回）。
- 浏览器侧只读验证（adapter 读出）本轮**未做**（浏览器按裁决转交 shader-auditor）。
