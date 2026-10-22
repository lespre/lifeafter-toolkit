# 极光剑 1110177 特效贴图二轮匹配报告 — task-52（候选级，不强行定唯一）

## 结论

**本轮没有新增绑定，绑定仍是 6/34、可渲染节点仍是 9 个** —— 原因不是没查，而是**判据不成立**：
28 条未定名贴图**没有任何 `.spr` 引用**（项目内 `.spr` 路径串仅 6 条、可取 3 条、**点名这 28 条的 = 0 条**），⇒ **没有硬尺寸锚点** ⇒ 不满足纪律要求的『硬尺寸 + 栅格整除 + 形态一致**且唯一**』。

**但候选池按你的要求扩了一倍**：`effect_01.gpk` 全量扫出 **7488 张匿名 DDS**（池内已有 454、**池外 7034**），池外 7034 张**全部**算完形态特征（覆盖率 **100%**）并标了 `容器#row` 来源 ⇒ 候选全池 **7854 条**。

## ① `.spr` 布局算术（本轮最有力判据）实测结果

- `.spr` 格式已解：`<mode> <表宽> <表高>` / `<帧数>` / `<param>` / N 行 `<name>.tga x0 y0 x1 y1`；对 3 条已声明的 `.spr` 校验通过：表 512×512 / 16 帧 / 128×128 满铺，表 256×256 / 4 帧 / 64×256 满铺。

- 对 28 条未定名 `.tga` 逐条找 `.spr` 引用（同伴名 `<stem>.spr`、同目录、`effect\textures\<stem>.spr` 及项目全量 `.spr` 路径）：**0 命中**。

- ⇒ 硬尺寸约束**不适用于这 28 条**；把它们按『表尺寸』筛选会变成**编造约束**，故未做。

## ② 池 vs `effect_01.gpk` 匿名 DDS 对照

| 口径 | 数量 |
|---|---|
| `effect_01.gpk` 行数 | 212152 |
| 其中 DDS 载荷 | **7488** |
| 与 `_sfx_029` 池 content_sha16 相同 | 454 |
| **池外（新纳入候选池）** | **7034**（全部算完特征，带 row 来源） |

⇒ 两池**不是同一批**：wpk 池 1,031 张里只有 454 张能在 GPK 里找到同内容；GPK 另有 7,034 张池外图。索引 `FX029_match_gpk_index.json`（含 row/dims/sha16/size/fourcc）、特征 `FX029_match_gpk_features.json`。

## ③ 28 条逐条结论（top5 带来源；全部 unresolved，原因见列）

| # | 声明名 | 族类 | `.spr` 引用 | 硬尺寸 | top1 候选（来源） | score | margin | 结论 | 原因 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `alpha_01_tp52_01.tga` | alpha_mask | — | — | `effect_01.gpk#204060`:ae1d1003985d2303.dds | 1.5 | 0.0 | unresolved | 无 .spr 引用 ⇒ 无硬尺寸锚点；形态排序非唯一 ⇒ 按纪律不绑定（只登记候选） |
| 2 | `tex_alpha_mask_tp60_04.tga` | alpha_mask | — | — | `effect_01.gpk#204060`:ae1d1003985d2303.dds | 1.5 | 0.0 | unresolved | 无 .spr 引用 ⇒ 无硬尺寸锚点；形态排序非唯一 ⇒ 按纪律不绑定（只登记候选） |
| 3 | `tex_alpha_tp104_04.tga` | alpha_mask | — | — | `effect_01.gpk#204060`:ae1d1003985d2303.dds | 1.5 | 0.0 | unresolved | 无 .spr 引用 ⇒ 无硬尺寸锚点；形态排序非唯一 ⇒ 按纪律不绑定（只登记候选） |
| 4 | `tex_crack_02_yx_djs.tga` | debris | — | — | `effect_01.gpk#210114`:ebb94ac1a2c50bb2.dds | 0.8099 | 0.0268 | unresolved | 无 .spr 引用 ⇒ 无硬尺寸锚点；形态排序非唯一 ⇒ 按纪律不绑定（只登记候选） |
| 5 | `tex_crack_tp71_05.tga` | debris | — | — | `effect_01.gpk#210114`:ebb94ac1a2c50bb2.dds | 0.8099 | 0.0268 | unresolved | 无 .spr 引用 ⇒ 无硬尺寸锚点；形态排序非唯一 ⇒ 按纪律不绑定（只登记候选） |
| 6 | `glow01_yc.tga` | glow | — | — | `effect_01.gpk#204120`:10bf0d1d28afca59.dds | 2.2489 | 0.0123 | unresolved | 无 .spr 引用 ⇒ 无硬尺寸锚点；形态排序非唯一 ⇒ 按纪律不绑定（只登记候选） |
| 7 | `glow25.tga` | glow | — | — | `effect_01.gpk#204120`:10bf0d1d28afca59.dds | 2.2489 | 0.0123 | unresolved | 无 .spr 引用 ⇒ 无硬尺寸锚点；形态排序非唯一 ⇒ 按纪律不绑定（只登记候选） |
| 8 | `glow_04_tp29.tga` | glow | — | — | `effect_01.gpk#204120`:10bf0d1d28afca59.dds | 2.2489 | 0.0123 | unresolved | 无 .spr 引用 ⇒ 无硬尺寸锚点；形态排序非唯一 ⇒ 按纪律不绑定（只登记候选） |
| 9 | `glow_14_cs.tga` | glow | — | — | `effect_01.gpk#204120`:10bf0d1d28afca59.dds | 2.2489 | 0.0123 | unresolved | 无 .spr 引用 ⇒ 无硬尺寸锚点；形态排序非唯一 ⇒ 按纪律不绑定（只登记候选） |
| 10 | `tex_glow_01_cs_tp60_01.tga` | glow | — | — | `effect_01.gpk#204120`:10bf0d1d28afca59.dds | 2.2489 | 0.0123 | unresolved | 无 .spr 引用 ⇒ 无硬尺寸锚点；形态排序非唯一 ⇒ 按纪律不绑定（只登记候选） |
| 11 | `tex_glow_guangci_tp78_01.tga` | alpha_mask | — | — | `effect_01.gpk#204060`:ae1d1003985d2303.dds | 1.5 | 0.0 | unresolved | 无 .spr 引用 ⇒ 无硬尺寸锚点；形态排序非唯一 ⇒ 按纪律不绑定（只登记候选） |
| 12 | `tex_glow_qirishijie_guangyun_hgz03_03.tga` | glow | — | — | `effect_01.gpk#204120`:10bf0d1d28afca59.dds | 2.2489 | 0.0123 | unresolved | 无 .spr 引用 ⇒ 无硬尺寸锚点；形态排序非唯一 ⇒ 按纪律不绑定（只登记候选） |
| 13 | `tex_glow_ray_x10_01.tga` | trail | — | — | `effect_01.gpk#210667`:d957663b865a9931.dds | 102794713.7422 | 75950053.8652 | unresolved | 无 .spr 引用 ⇒ 无硬尺寸锚点；形态排序非唯一 ⇒ 按纪律不绑定（只登记候选） |
| 14 | `tex_glow_tp07_05.tga` | glow | — | — | `effect_01.gpk#204120`:10bf0d1d28afca59.dds | 2.2489 | 0.0123 | unresolved | 无 .spr 引用 ⇒ 无硬尺寸锚点；形态排序非唯一 ⇒ 按纪律不绑定（只登记候选） |
| 15 | `tex_glow_tp61_02.tga` | glow | — | — | `effect_01.gpk#204120`:10bf0d1d28afca59.dds | 2.2489 | 0.0123 | unresolved | 无 .spr 引用 ⇒ 无硬尺寸锚点；形态排序非唯一 ⇒ 按纪律不绑定（只登记候选） |
| 16 | `tex_glow_x04_01.tga` | glow | — | — | `effect_01.gpk#204120`:10bf0d1d28afca59.dds | 2.2489 | 0.0123 | unresolved | 无 .spr 引用 ⇒ 无硬尺寸锚点；形态排序非唯一 ⇒ 按纪律不绑定（只登记候选） |
| 17 | `xing_01_yh_djs.tga` | glow | — | — | `effect_01.gpk#204120`:10bf0d1d28afca59.dds | 2.2489 | 0.0123 | unresolved | 无 .spr 引用 ⇒ 无硬尺寸锚点；形态排序非唯一 ⇒ 按纪律不绑定（只登记候选） |
| 18 | `lighting_01_rzx_djs.tga` | glow | — | — | `effect_01.gpk#204120`:10bf0d1d28afca59.dds | 2.2489 | 0.0123 | unresolved | 无 .spr 引用 ⇒ 无硬尺寸锚点；形态排序非唯一 ⇒ 按纪律不绑定（只登记候选） |
| 19 | `lightning_01_ycy_djs.tga` | streak | — | — | `effect_01.gpk#210667`:d957663b865a9931.dds | 128493392.0126 | 94937567.7701 | unresolved | 无 .spr 引用 ⇒ 无硬尺寸锚点；形态排序非唯一 ⇒ 按纪律不绑定（只登记候选） |
| 20 | `tex_lightning_shandian_tp52.tga` | streak | — | — | `effect_01.gpk#210667`:d957663b865a9931.dds | 128493392.0126 | 94937567.7701 | unresolved | 无 .spr 引用 ⇒ 无硬尺寸锚点；形态排序非唯一 ⇒ 按纪律不绑定（只登记候选） |
| 21 | `guangshu01_cjf_djs.tga` | trail | — | — | `effect_01.gpk#210667`:d957663b865a9931.dds | 102794713.7422 | 75950053.8652 | unresolved | 无 .spr 引用 ⇒ 无硬尺寸锚点；形态排序非唯一 ⇒ 按纪律不绑定（只登记候选） |
| 22 | `keji_02_wh_djs.tga` | glow | — | — | `effect_01.gpk#204120`:10bf0d1d28afca59.dds | 2.2489 | 0.0123 | unresolved | 无 .spr 引用 ⇒ 无硬尺寸锚点；形态排序非唯一 ⇒ 按纪律不绑定（只登记候选） |
| 23 | `tex_trail_huo_01_zhf_djs.tga` | trail | — | — | `effect_01.gpk#210667`:d957663b865a9931.dds | 102794713.7422 | 75950053.8652 | unresolved | 无 .spr 引用 ⇒ 无硬尺寸锚点；形态排序非唯一 ⇒ 按纪律不绑定（只登记候选） |
| 24 | `tex_trail_x07_01.tga` | trail | — | — | `effect_01.gpk#210667`:d957663b865a9931.dds | 102794713.7422 | 75950053.8652 | unresolved | 无 .spr 引用 ⇒ 无硬尺寸锚点；形态排序非唯一 ⇒ 按纪律不绑定（只登记候选） |
| 25 | `trail_11_lmq_djs.tga` | trail | — | — | `effect_01.gpk#210667`:d957663b865a9931.dds | 102794713.7422 | 75950053.8652 | unresolved | 无 .spr 引用 ⇒ 无硬尺寸锚点；形态排序非唯一 ⇒ 按纪律不绑定（只登记候选） |
| 26 | `noise_04_tp05.tga` | glow | — | — | `effect_01.gpk#204120`:10bf0d1d28afca59.dds | 2.2489 | 0.0123 | unresolved | 无 .spr 引用 ⇒ 无硬尺寸锚点；形态排序非唯一 ⇒ 按纪律不绑定（只登记候选） |
| 27 | `tex_noise_y.tga` | glow | — | — | `effect_01.gpk#204120`:10bf0d1d28afca59.dds | 2.2489 | 0.0123 | unresolved | 无 .spr 引用 ⇒ 无硬尺寸锚点；形态排序非唯一 ⇒ 按纪律不绑定（只登记候选） |
| 28 | `v_veins_tp116_08.tga` | glow | — | — | `effect_01.gpk#204120`:10bf0d1d28afca59.dds | 2.2489 | 0.0123 | unresolved | 无 .spr 引用 ⇒ 无硬尺寸锚点；形态排序非唯一 ⇒ 按纪律不绑定（只登记候选） |

unresolved 数 = **28 / 28**；可升级 = 0。

## ④ 新落盘 PNG（`1110177/sfx/tex/_match003/`）

每名 top1（扩展池胜出者）落一张，共 **28 张**（**不改动** `sfx/tex/` 已落盘的 99 张）：

| PNG | 来源 | dims | sha16 |
|---|---|---|---|
| `alpha_01_tp52_01__gpk_ae1d1003.png` | effect_01.gpk#204060 | [128, 128] | `99e10b7c7a57390a` |
| `tex_alpha_mask_tp60_04__gpk_ae1d1003.png` | effect_01.gpk#204060 | [128, 128] | `99e10b7c7a57390a` |
| `tex_alpha_tp104_04__gpk_ae1d1003.png` | effect_01.gpk#204060 | [128, 128] | `99e10b7c7a57390a` |
| `tex_crack_02_yx_djs__gpk_ebb94ac1.png` | effect_01.gpk#210114 | [4, 4] | `88d344aae5ee20ce` |
| `tex_crack_tp71_05__gpk_ebb94ac1.png` | effect_01.gpk#210114 | [4, 4] | `88d344aae5ee20ce` |
| `glow01_yc__gpk_10bf0d1d.png` | effect_01.gpk#204120 | [256, 256] | `300c6a93f83359ea` |
| `glow25__gpk_10bf0d1d.png` | effect_01.gpk#204120 | [256, 256] | `300c6a93f83359ea` |
| `glow_04_tp29__gpk_10bf0d1d.png` | effect_01.gpk#204120 | [256, 256] | `300c6a93f83359ea` |
| `glow_14_cs__gpk_10bf0d1d.png` | effect_01.gpk#204120 | [256, 256] | `300c6a93f83359ea` |
| `tex_glow_01_cs_tp60_01__gpk_10bf0d1d.png` | effect_01.gpk#204120 | [256, 256] | `300c6a93f83359ea` |
| `tex_glow_guangci_tp78_01__gpk_ae1d1003.png` | effect_01.gpk#204060 | [128, 128] | `99e10b7c7a57390a` |
| `tex_glow_qirishijie_guangyun_hgz03_03__gpk_10bf0d1d.png` | effect_01.gpk#204120 | [256, 256] | `300c6a93f83359ea` |
| `tex_glow_ray_x10_01__gpk_d957663b.png` | effect_01.gpk#210667 | [512, 512] | `8218a061eb67152d` |
| `tex_glow_tp07_05__gpk_10bf0d1d.png` | effect_01.gpk#204120 | [256, 256] | `300c6a93f83359ea` |
| `tex_glow_tp61_02__gpk_10bf0d1d.png` | effect_01.gpk#204120 | [256, 256] | `300c6a93f83359ea` |
| `tex_glow_x04_01__gpk_10bf0d1d.png` | effect_01.gpk#204120 | [256, 256] | `300c6a93f83359ea` |
| `xing_01_yh_djs__gpk_10bf0d1d.png` | effect_01.gpk#204120 | [256, 256] | `300c6a93f83359ea` |
| `lighting_01_rzx_djs__gpk_10bf0d1d.png` | effect_01.gpk#204120 | [256, 256] | `300c6a93f83359ea` |
| `lightning_01_ycy_djs__gpk_d957663b.png` | effect_01.gpk#210667 | [512, 512] | `8218a061eb67152d` |
| `tex_lightning_shandian_tp52__gpk_d957663b.png` | effect_01.gpk#210667 | [512, 512] | `8218a061eb67152d` |
| `guangshu01_cjf_djs__gpk_d957663b.png` | effect_01.gpk#210667 | [512, 512] | `8218a061eb67152d` |
| `keji_02_wh_djs__gpk_10bf0d1d.png` | effect_01.gpk#204120 | [256, 256] | `300c6a93f83359ea` |
| `tex_trail_huo_01_zhf_djs__gpk_d957663b.png` | effect_01.gpk#210667 | [512, 512] | `8218a061eb67152d` |
| `tex_trail_x07_01__gpk_d957663b.png` | effect_01.gpk#210667 | [512, 512] | `8218a061eb67152d` |
| `trail_11_lmq_djs__gpk_d957663b.png` | effect_01.gpk#210667 | [512, 512] | `8218a061eb67152d` |
| `noise_04_tp05__gpk_10bf0d1d.png` | effect_01.gpk#204120 | [256, 256] | `300c6a93f83359ea` |
| `tex_noise_y__gpk_10bf0d1d.png` | effect_01.gpk#204120 | [256, 256] | `300c6a93f83359ea` |
| `v_veins_tp116_08__gpk_10bf0d1d.png` | effect_01.gpk#204120 | [256, 256] | `300c6a93f83359ea` |

## ⑤ `effects.json` 改动

- **改前 sha16 `9ee22514b5d6cf71`**（task-51 交付态）⇒ **改后 `3929a32c585fec58`**（317112 B）。

- 逐处改动：各节点 `texture_candidates_ranked` 改为 **`来源:文件`** 形式（`effect_01.gpk#row` 或 `_sfx_029_pool`）、未绑定节点 `texture_status` 标注二轮结论；顶层 `texture_binding_status` 追加二轮说明、`provenance.candidate_pool_extended` 记录扩展池。**未新增绑定、未改 `models_enabled`（仍缺省=关）**。

- `renderable_by_adapter=true` 节点数 = **9**（与 task-51 相同）。

## ⑥ 只读验证

- adapter 无 DOM 加载成功；读取点对账；结构断言 **11 项** ⇒ 失败项 **无**；`models_enabled` 仍缺省。

## ⑦ unresolved（未猜）

- 28 条无硬尺寸锚点 ⇒ 无法在『不强行定唯一』的前提下绑定。**唯一可行的升级路径**：拿到引擎侧 `名↔idx_hash` 规则，或找到某个 `.spr`/配置把 `.tga` 名与内容对上。

- wpk 池 1,031 张中 **158 张**解码失败（features 缺失，已在池特征文件里带 `err`），本轮候选只用了可解码的 873 张 + GPK 6,981 张。

- `effect_02.gpk` 等其它匿名容器未纳入本轮（本轮按要求只对 `effect_01.gpk` 做了全量对照）。
