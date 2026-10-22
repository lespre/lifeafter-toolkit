# 极光剑 1110177 特效贴图解锁报告 — task-51（候选级 content_candidate）

**一句话**：贴图容器族补上了（`effect.idx` + `effect3.wpk`），池 **1031 条**；34 条声明贴图里 **绑定 6 条**（同名复用 4 + `.spr` 指纹 2）、**28 条只登记候选不绑定**；PNG **99 张**（保 alpha）。**全部按 `content_candidate` 标注，无一条写成源级**；`idx_hash` 非路径哈希 ⇒ 按名直证不可得（沿 Lead 结论）。

## 池（新目录 `03拆包产物/_sfx_029/`）

- 索引/载荷：`E:\mrzh\Documents\res\effect.idx`（37,188 B）+ `effect3.wpk`（35,651,584 B）；`effect.idx` 条目 1032 → 提取 DDS **1031**（1 条非 DDS），dims 分布 = 256²:684 / 128²:184 / 512²:120 / 64²:20 / 1024²:19 + 3 个单例

- 产物：`texture_pool\<content_sha16>.dds`、`effect_texture_pool_029.json`（字段与 1110171 一致：`idx_hash/pkg/type/size/dims/content_sha16`，外加 `file/fourcc`）、`_pool_features_029.json`（形态特征 + alpha 统计）、`_pool_extract_errors.json`（1 条）

- **抽样 sha16**：[{"file": "cf03382cf49ed20c.dds", "sha16": "cf03382cf49ed20c", "dims": [256, 256]}, {"file": "daa089fcc382393d.dds", "sha16": "daa089fcc382393d", "dims": [256, 256]}, {"file": "8804a8ddebcd6755.dds", "sha16": "8804a8ddebcd6755", "dims": [256, 256]}]

- **与 1110171 池的等价性复核**：1110171 provenance 的 11 个候选 DDS 其 `content_sha16` 在本池 **11/11 命中且逐字节一致** ⇒ 同一套管线、同一份池

## 31 条声明贴图逐条结论（含 3 条 .spr，合计 34）

| # | 声明名 | 引用方 | 命中方式 | 池条目(dds) | dims | 证据 | confidence | 是否落盘 PNG |
|---|---|---|---|---|---|---|---|---|
| 1 | `alpha_01_tp52_01.tga` | hit | c_content_feature | — | — | 无同名锚点/无 .spr 锚点 ⇒ 按族类 glow 的内容特征排序取 top3（**只登记候选、不绑定**） | low | — |
| 2 | `tex_alpha_mask_tp60_04.tga` | jisha | c_content_feature | — | — | 无同名锚点/无 .spr 锚点 ⇒ 按族类 glow 的内容特征排序取 top3（**只登记候选、不绑定**） | low | — |
| 3 | `tex_alpha_tp104_04.tga` | jisha | c_content_feature | — | — | 无同名锚点/无 .spr 锚点 ⇒ 按族类 glow 的内容特征排序取 top3（**只登记候选、不绑定**） | low | — |
| 4 | `tex_crack_02_yx_djs.tga` | jisha | c_content_feature | — | — | 无同名锚点/无 .spr 锚点 ⇒ 按族类 glow 的内容特征排序取 top3（**只登记候选、不绑定**） | low | — |
| 5 | `tex_crack_tp71_05.tga` | jisha | c_content_feature | — | — | 无同名锚点/无 .spr 锚点 ⇒ 按族类 glow 的内容特征排序取 top3（**只登记候选、不绑定**） | low | — |
| 6 | `dian_12.tga` | jisha | a_same_name_reuse | 7240b8319d081a0f.dds | [256, 256] | 同名复用 1110171 provenance（7240b8319d081a0f.dds）+ 内容 sha16 在 029 池中复核一致 | medium | dian_12__7240b831.png |
| 7 | `glow01_yc.tga` | jisha | c_content_feature | — | — | 无同名锚点/无 .spr 锚点 ⇒ 按族类 glow 的内容特征排序取 top3（**只登记候选、不绑定**） | low | — |
| 8 | `glow25.tga` | hit, jisha | c_content_feature | — | — | 无同名锚点/无 .spr 锚点 ⇒ 按族类 glow 的内容特征排序取 top3（**只登记候选、不绑定**） | low | — |
| 9 | `glow_01.tga` | jisha | a_same_name_reuse | 13211b0279d2a247.dds | [256, 256] | 同名复用 1110171 provenance（13211b0279d2a247.dds）+ 内容 sha16 在 029 池中复核一致 | medium | glow_01__13211b02.png |
| 10 | `glow_04_tp29.tga` | jisha | c_content_feature | — | — | 无同名锚点/无 .spr 锚点 ⇒ 按族类 glow 的内容特征排序取 top3（**只登记候选、不绑定**） | low | — |
| 11 | `glow_14_cs.tga` | jisha | c_content_feature | — | — | 无同名锚点/无 .spr 锚点 ⇒ 按族类 glow 的内容特征排序取 top3（**只登记候选、不绑定**） | low | — |
| 12 | `glow_16_yh_djs.tga` | hit, jisha | a_same_name_reuse | 7ce99117a10f5163.dds | [256, 256] | 同名复用 1110171 provenance（7ce99117a10f5163.dds）+ 内容 sha16 在 029 池中复核一致 | medium | glow_16_yh_djs__7ce99117.png |
| 13 | `tex_glow_01_cs_tp60_01.tga` | jisha | c_content_feature | — | — | 无同名锚点/无 .spr 锚点 ⇒ 按族类 glow 的内容特征排序取 top3（**只登记候选、不绑定**） | low | — |
| 14 | `tex_glow_guangci_tp78_01.tga` | jisha | c_content_feature | — | — | 无同名锚点/无 .spr 锚点 ⇒ 按族类 glow 的内容特征排序取 top3（**只登记候选、不绑定**） | low | — |
| 15 | `tex_glow_qirishijie_guangyun_hgz03_03.tga` | jisha | c_content_feature | — | — | 无同名锚点/无 .spr 锚点 ⇒ 按族类 glow 的内容特征排序取 top3（**只登记候选、不绑定**） | low | — |
| 16 | `tex_glow_ray_x10_01.tga` | hit | c_content_feature | — | — | 无同名锚点/无 .spr 锚点 ⇒ 按族类 trail 的内容特征排序取 top3（**只登记候选、不绑定**） | low | — |
| 17 | `tex_glow_tp07_05.tga` | hit | c_content_feature | — | — | 无同名锚点/无 .spr 锚点 ⇒ 按族类 glow 的内容特征排序取 top3（**只登记候选、不绑定**） | low | — |
| 18 | `tex_glow_tp61_02.tga` | hit | c_content_feature | — | — | 无同名锚点/无 .spr 锚点 ⇒ 按族类 glow 的内容特征排序取 top3（**只登记候选、不绑定**） | low | — |
| 19 | `tex_glow_x04_01.tga` | hit | c_content_feature | — | — | 无同名锚点/无 .spr 锚点 ⇒ 按族类 glow 的内容特征排序取 top3（**只登记候选、不绑定**） | low | — |
| 20 | `xing_01_yh_djs.tga` | hit | c_content_feature | — | — | 无同名锚点/无 .spr 锚点 ⇒ 按族类 glow 的内容特征排序取 top3（**只登记候选、不绑定**） | low | — |
| 21 | `lighting_01_rzx_djs.tga` | hit | c_content_feature | — | — | 无同名锚点/无 .spr 锚点 ⇒ 按族类 glow 的内容特征排序取 top3（**只登记候选、不绑定**） | low | — |
| 22 | `lightning07_cs.spr` | hit | a_same_name_reuse_with_conflict | a8764b3acfeaff93.dds | [256, 256] | 同名复用 1110171 provenance（a8764b3acfeaff93.dds）+ 内容 sha16 在 029 池中复核一致；⚠ 证据冲突：.spr 描述表 512x512 而复用候选 [256, 256] | low | lightning07_cs__a8764b3a.png |
| 23 | `lightning_01.spr` | jisha | b_spr_fingerprint | 662b911ee5599742.dds | [512, 512] | .spr 描述：表 512x512 / 16 帧 / 帧矩形 [0, 0, 128, 128] ⇒ 池中 dims 完全吻合 3 条，按图集形态分排序取 top3；**多个候选并列，未强行唯一化** | low | lightning_01__662b911e.png |
| 24 | `lightning_01_ycy_djs.tga` | jisha | c_content_feature | — | — | 无同名锚点/无 .spr 锚点 ⇒ 按族类 streak 的内容特征排序取 top3（**只登记候选、不绑定**） | low | — |
| 25 | `shandian_05_yh_djs.spr` | jisha | b_spr_fingerprint | a9aa4caf1f52a374.dds | [256, 256] | .spr 描述：表 256x256 / 4 帧 / 帧矩形 [0, 0, 63, 255] ⇒ 池中 dims 完全吻合 3 条，按图集形态分排序取 top3；**多个候选并列，未强行唯一化** | low | shandian_05_yh_djs__a9aa4caf.png |
| 26 | `tex_lightning_shandian_tp52.tga` | hit | c_content_feature | — | — | 无同名锚点/无 .spr 锚点 ⇒ 按族类 streak 的内容特征排序取 top3（**只登记候选、不绑定**） | low | — |
| 27 | `guangshu01_cjf_djs.tga` | hit | c_content_feature | — | — | 无同名锚点/无 .spr 锚点 ⇒ 按族类 trail 的内容特征排序取 top3（**只登记候选、不绑定**） | low | — |
| 28 | `keji_02_wh_djs.tga` | hit, jisha | c_content_feature | — | — | 无同名锚点/无 .spr 锚点 ⇒ 按族类 glow 的内容特征排序取 top3（**只登记候选、不绑定**） | low | — |
| 29 | `tex_trail_huo_01_zhf_djs.tga` | jisha | c_content_feature | — | — | 无同名锚点/无 .spr 锚点 ⇒ 按族类 trail 的内容特征排序取 top3（**只登记候选、不绑定**） | low | — |
| 30 | `tex_trail_x07_01.tga` | jisha | c_content_feature | — | — | 无同名锚点/无 .spr 锚点 ⇒ 按族类 trail 的内容特征排序取 top3（**只登记候选、不绑定**） | low | — |
| 31 | `trail_11_lmq_djs.tga` | jisha | c_content_feature | — | — | 无同名锚点/无 .spr 锚点 ⇒ 按族类 trail 的内容特征排序取 top3（**只登记候选、不绑定**） | low | — |
| 32 | `noise_04_tp05.tga` | jisha | c_content_feature | — | — | 无同名锚点/无 .spr 锚点 ⇒ 按族类 glow 的内容特征排序取 top3（**只登记候选、不绑定**） | low | — |
| 33 | `tex_noise_y.tga` | jisha | c_content_feature | — | — | 无同名锚点/无 .spr 锚点 ⇒ 按族类 glow 的内容特征排序取 top3（**只登记候选、不绑定**） | low | — |
| 34 | `v_veins_tp116_08.tga` | jisha | c_content_feature | — | — | 无同名锚点/无 .spr 锚点 ⇒ 按族类 glow 的内容特征排序取 top3（**只登记候选、不绑定**） | low | — |

统计：**绑定 6 / 未绑定 28**；方式分布 a=4、b=2、c=28。

### 绑定规则（明文，防误用）

1. **(a) 同名复用**：声明 basename 与 **1110171** `tex_candidates_provenance.json` 的键完全相同，**且**其 DDS 的 `content_sha16` 在本池命中（内容核对）⇒ 绑定，`confidence=medium`。命中：`dian_12.tga` / `glow_01.tga` / `glow_16_yh_djs.tga` / `lightning07_cs.spr`。

2. **(b) `.spr` 指纹**：`.spr` 描述文件给出 *表宽/表高/帧数/帧矩形*（如 `lightning_01.spr` = 512×512 / 16 帧 / 128×128 格）⇒ 只取池中 **dims 完全吻合** 的条目，按图集形态分排序 ⇒ 绑定 top1，`confidence=low`，**并列候选一并登记**。

3. **(c) 内容特征**：无同名/无 .spr 锚点的 28 条 ⇒ 按名字族类（glow / ring / streak / trail）用池形态特征排序取 top3，`confidence=low`，**只登记候选、不绑定**（`texture_candidate=null`）；**绝不把候选说成源级、也不强行唯一化**。

### ⚠ 一处证据冲突（如实登记，未掩盖）

- `lightning07_cs.spr`：`(a)` 复用 1110171 的候选 `a8764b3acfeaff93.dds`（256×256），但 `.spr` 描述文件写的是**表 512×512 / 16 帧** ⇒ 两者矛盾。处理：**保留复用候选（标 `low`）+ 并列登记 512×512 的 spr 吻合候选**，不擅自二选一。

## 文件落盘与 `effects.json` 更新

- PNG：`1110177/sfx/tex/*.png` 共 **99 张**（保 alpha，`texture2ddecoder` 解码；命名 `<声明名>__<dds sha8>.png`，候选加 `__c1/2/3_`）；清单见 `FX029_tex_assets.json.png_files`（含每张 sha16 + 尺寸）。

- `1110177/sfx/tex_candidates_provenance.json`：与 1110171 同格式（`dds/png/size/decoder/sha16` + 本任务要求的 `evidence/confidence/mode/bound/candidates`）。

- `effects.json`：**改前 sha16 `8938bc9fea2eeeb3`**（task-50 交付态；本轮因重跑一次，磁盘上的备份文件保存的是中间态 `8938bc9fea2eeeb3`）⇒ **改后 `9ee22514b5d6cf71`**（312345 B）；逐处改动：节点 `texture_candidate/texture_binding/texture_status/texture_candidates_ranked`、顶层 `texture_binding_status/texture_selection/unsupported/provenance.texture_pool`；**`renderable_by_adapter=true` 的节点 = 9 个**；`models_enabled` **不存在（= 默认关，开关留给用户）**。

## 只读验证（不改 adapter、不开浏览器）

- adapter 无 DOM 加载 **成功**（API：attach, setModelsBase, models, modelMaterial, selfUrl, loaderCandidates）；源码 `effects.<键>` 读取点全部对账；结构断言 **11 项全过**；`models_enabled` 仍不在 JSON 中（= false，fail-closed）⇒ 默认关不变。

- 未验：`attach(ctx)` 需 THREE+场景（不在只读范围）。

## unresolved / 未做

- 28 条声明贴图**只有候选、无绑定**：`idx_hash` 不是常见路径哈希（Lead 已验 8 哈希 × 21 变体 = 0 命中）⇒ 除非拿到引擎侧 名↔哈希 规则，否则无法升级为直证。

- 池内含 2048×2048 / 2048×1024 等大图（各 1 条），未参与绑定候选排序的尺寸筛选。

- `.spr` 只是**描述文件**：真正图集 = 其 `sheet` 尺寸的 DDS；已按表尺寸筛候选，但帧矩形与图集内容的对应未逐帧核对。
