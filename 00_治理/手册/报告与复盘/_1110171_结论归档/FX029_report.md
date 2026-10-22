# 极光剑 1110177（skin_2003_029）SFX 提取报告 — task-50

**结论先说**：特效**文件齐**（2 份 sfx 按路径直取 + 24/24 特效模型已导出 GLB + 3 个 `.spr` 精灵表描述文件也取到了），**唯缺口是 31 条 `effect\textures\*.tga` 按名全 MISS**（与皮肤贴图同因：打包改名）；按纪律**一律 unresolved、零顶替**。

产出：`08Lifeafter wiki/assets/3d/weapon_skin/1110177/effects.json`（302077 B，sha16 `dbc14e8a7d48f9e6`，**66 节点**）、`1110177/sfx/**`（24 GLB + 3 spr + 2 sfx）、`FX029_assets.json`、本报告。

改前 `effects.json` 已备份：`effects.json.bak_20260918_231908`（793 B，sha16 `3cc1f0de52615fab`）。


## 1. 两份 sfx（直取证：按路径命中 effect_01.gpk）

| 文件 | 逻辑路径 | 容器 | row | bytes | sha16 | 节点 | XML 序对齐 |
|---|---|---|---|---|---|---|---|
| `fx_skin_2003_029_hit.sfx` | `effect\fx\weapon\skin\skin_2003_029\fx_skin_2003_029_hit.sfx` | effect_01.gpk | 38420 | 94278 | `d406a3b00a0f890e` | 21 | ✓ |
| `fx_skin_2003_029_jisha.sfx` | `effect\fx\weapon\skin\skin_2003_029\fx_skin_2003_029_jisha.sfx` | effect_01.gpk | 38433 | 154301 | `0e6cfb5ff9f08996` | 45 | ✓ |

节点构成：hit = 21（Dummy 3 / Sprite 4 / Model 7 / ParticleSystem 7）；jisha = 45（Dummy 8 / Model 19 / Sprite 9 / ParticleSystem 8 / ParticleRes 1）⇒ 合计 **66**。`frame_binding=direct_path_entry`（强于 1110171 的帧候选：这两份是**路径直命中**）。

两份 sfx 已原样落盘到 `1110177/sfx/`（不转码、不改名）。


## 2. 24 个特效 `.gim` → GLB（24/24）

路线：`.gim` 同 stem `.mesh`（全部存在）→ 既有 `export_glb.py`（单材质集、无贴图、几何级）→ `1110177/sfx/<stem>.glb`。**不新写解析器**。

| # | gim（逻辑路径） | gim 容器·row | gim sha16 | .mesh 容器·row | glb | glb bytes | glb sha16 | tv/tf |
|---|---|---|---|---|---|---|---|---|
| 1 | `effect\mesh\weapon\skin\skin_2003_018\mod_skin_2003_018_bp_baoci_hgz01_02.gim` | None#None | `None` | effect_01.gpk#190729 | `mod_skin_2003_018_bp_baoci_hgz01_02.glb` | 3336 | `464ee0cc7c167137` | 32/16 |
| 2 | `effect\mesh\weapon\skin\skin_2003_019\mod_sandian_02_hjl_djs.gim` | None#None | `None` | effect_01.gpk#191158 | `mod_sandian_02_hjl_djs.glb` | 2196 | `47045f015c823565` | 4/2 |
| 3 | `effect\mesh\weapon\skin\skin_2003_022\mod_skin_2003_022_jisha_dilie_hgz01_01_djs.gim` | None#None | `None` | effect_01.gpk#191584 | `mod_skin_2003_022_jisha_dilie_hgz01_01_djs.glb` | 2252 | `56e843eb48d7750c` | 4/2 |
| 4 | `effect\mesh\weapon\skin\skin_2003_022\mod_skin_2003_022_jisha_dimiankuosan_hgz01_01_djs.gim` | None#None | `None` | effect_01.gpk#191587 | `mod_skin_2003_022_jisha_dimiankuosan_hgz01_01_djs.glb` | 5148 | `39c18d701334d221` | 63/80 |
| 5 | `effect\mesh\weapon\skin\skin_2003_022\mod_skin_2003_022_jisha_glow_shu_hgz01_01_djs.gim` | None#None | `None` | effect_01.gpk#191593 | `mod_skin_2003_022_jisha_glow_shu_hgz01_01_djs.glb` | 2576 | `f62848d81ee4306d` | 10/8 |
| 6 | `effect\mesh\weapon\skin\skin_2003_022\mod_skin_2003_022_jisha_qiliu_01_djs.gim` | None#None | `None` | effect_01.gpk#191611 | `mod_skin_2003_022_jisha_qiliu_01_djs.glb` | 2412 | `5c58315f68962f00` | 8/4 |
| 7 | `effect\mesh\weapon\skin\skin_2003_022\mod_skin_2003_022_kuosan_hgz_02_djs.gim` | None#None | `None` | effect_01.gpk#191626 | `mod_skin_2003_022_kuosan_hgz_02_djs.glb` | 8448 | `86005530636038d7` | 125/192 |
| 8 | `effect\mesh\weapon\skin\skin_2003_029\mod_skin_2003_029_14_hjl_djs.gim` | None#None | `None` | effect_01.gpk#191893 | `mod_skin_2003_029_14_hjl_djs.glb` | 5084 | `4cc36d3b156518de` | 63/80 |
| 9 | `effect\mesh\weapon\skin\skin_2003_029\mod_skin_2003_029_56_hjl_djs.gim` | None#None | `None` | effect_01.gpk#192022 | `mod_skin_2003_029_56_hjl_djs.glb` | 11668 | `8e8978871bdede19` | 186/300 |
| 10 | `effect\mesh\weapon\skin\skin_2003_029\mod_skin_2003_029_dm_qiliu_06_djs.gim` | None#None | `None` | effect_01.gpk#192148 | `mod_skin_2003_029_dm_qiliu_06_djs.glb` | 13016 | `eef727769f90b8de` | 220/320 |
| 11 | `effect\mesh\weapon\skin\skin_2003_029\mod_skin_2003_029_dm_qiliu_09_djs.gim` | None#None | `None` | effect_01.gpk#192157 | `mod_skin_2003_029_dm_qiliu_09_djs.glb` | 4392 | `8d8c98f73a405047` | 52/50 |
| 12 | `effect\mesh\weapon\skin\skin_2003_029\mod_skin_2003_029_dm_qiliu_12_djs.gim` | None#None | `None` | effect_01.gpk#192166 | `mod_skin_2003_029_dm_qiliu_12_djs.glb` | 7232 | `6bf26e8b425e97bf` | 104/150 |
| 13 | `effect\mesh\weapon\skin\skin_2003_029\mod_skin_2003_029_dm_qiliu_20_djs.gim` | None#None | `None` | effect_01.gpk#192187 | `mod_skin_2003_029_dm_qiliu_20_djs.glb` | 5100 | `1b9d2bba152f4804` | 63/80 |
| 14 | `effect\mesh\weapon\skin\skin_2003_029\mod_skin_2003_029_dm_qiliu_23_djs.gim` | None#None | `None` | effect_01.gpk#192193 | `mod_skin_2003_029_dm_qiliu_23_djs.glb` | 5004 | `61618c397daa5e03` | 66/64 |
| 15 | `effect\mesh\weapon\skin\skin_2003_029\mod_skin_2003_029_dm_shangdian_05_djs.gim` | None#None | `None` | effect_01.gpk#192202 | `mod_skin_2003_029_dm_shangdian_05_djs.glb` | 2744 | `90c12705d006ee27` | 16/8 |
| 16 | `effect\mesh\weapon\skin\skin_2003_029\mod_skin_2003_029_dm_shangdian_07_djs.gim` | None#None | `None` | effect_01.gpk#192208 | `mod_skin_2003_029_dm_shangdian_07_djs.glb` | 7424 | `52fdaad454498b35` | 105/160 |
| 17 | `effect\mesh\weapon\skin\skin_2003_029\mod_skin_2003_029_dm_wuqi_01_djs.gim` | None#None | `None` | effect_01.gpk#192211 | `mod_skin_2003_029_dm_wuqi_01_djs.glb` | 51404 | `a521aff01c16a527` | 1119/1121 |
| 18 | `effect\mesh\weapon\skin\skin_2003_029\mod_skin_2003_029_mz_kj01_djs.gim` | None#None | `None` | effect_01.gpk#192313 | `mod_skin_2003_029_mz_kj01_djs.glb` | 2248 | `43f5ef7f36b8d20e` | 4/2 |
| 19 | `effect\mesh\weapon\skin\skin_2003_029\mod_skin_2003_029_mz_kj03_djs.gim` | None#None | `None` | effect_01.gpk#192319 | `mod_skin_2003_029_mz_kj03_djs.glb` | 2248 | `02804b41409a6323` | 4/2 |
| 20 | `effect\mesh\weapon\skin\skin_2003_029\mod_skin_2003_029_mz_ks01_djs.gim` | None#None | `None` | effect_01.gpk#192322 | `mod_skin_2003_029_mz_ks01_djs.glb` | 13240 | `e98ce7608acfa39e` | 216/350 |
| 21 | `effect\mesh\weapon\skin\skin_2003_029\mod_skin_2003_029_mz_sd01_djs.gim` | None#None | `None` | effect_01.gpk#192325 | `mod_skin_2003_029_mz_sd01_djs.glb` | 3012 | `063237013ca44235` | 24/12 |
| 22 | `effect\mesh\weapon\skin\skin_2003_029\mod_skin_2003_029_mz_shandian01_djs.gim` | None#None | `None` | effect_01.gpk#192328 | `mod_skin_2003_029_mz_shandian01_djs.glb` | 3032 | `6dec887c7a9a3cd6` | 24/12 |
| 23 | `effect\mesh\weapon\skin\skin_2003_029\mod_skin_2003_029_mz_shandian02_djs.gim` | None#None | `None` | effect_01.gpk#192331 | `mod_skin_2003_029_mz_shandian02_djs.glb` | 2572 | `65701e13d0386263` | 12/6 |
| 24 | `effect\mesh\weapon\skin\skin_2003_029\mod_skin_2003_029_mz_shandian03_djs.gim` | None#None | `None` | effect_01.gpk#192334 | `mod_skin_2003_029_mz_shandian03_djs.glb` | 2724 | `16039d9b1fb56367` | 16/8 |

合计 GLB **24/24**，总字节 168512。Model 节点回填：**filled 26 / absent 0**（26 个 Model 节点映射到 24 个唯一模型）。


## 3. 贴图：31 条 `.tga` 按名 **0/31**（unresolved，零顶替）

已试入口（每条最多 20 个变体：原样 / `.dds` / `.png` / 大写 / 小写 / 去 `effect\` / `textures\` 前缀 / `res\` `assets\` `common\` 前缀）：

| # | 声明路径 | 被哪份 sfx 引用 | 状态 | 试过条数 |
|---|---|---|---|---|
| 1 | `effect\textures\alpha\alpha_01_tp52_01.tga` | fx_skin_2003_029_hit.sfx | MISS | 8 |
| 2 | `effect\textures\alpha\tex_alpha_mask_tp60_04.tga` | fx_skin_2003_029_jisha.sfx | MISS | 8 |
| 3 | `effect\textures\alpha\tex_alpha_tp104_04.tga` | fx_skin_2003_029_jisha.sfx | MISS | 8 |
| 4 | `effect\textures\debris\crack\tex_crack_02_yx_djs.tga` | fx_skin_2003_029_jisha.sfx | MISS | 8 |
| 5 | `effect\textures\debris\crack\tex_crack_tp71_05.tga` | fx_skin_2003_029_jisha.sfx | MISS | 8 |
| 6 | `effect\textures\glow\dian_12.tga` | fx_skin_2003_029_jisha.sfx | MISS | 8 |
| 7 | `effect\textures\glow\glow01_yc.tga` | fx_skin_2003_029_jisha.sfx | MISS | 8 |
| 8 | `effect\textures\glow\glow25.tga` | fx_skin_2003_029_hit.sfx, fx_skin_2003_029_jisha.sfx | MISS | 8 |
| 9 | `effect\textures\glow\glow_01.tga` | fx_skin_2003_029_jisha.sfx | MISS | 8 |
| 10 | `effect\textures\glow\glow_04_tp29.tga` | fx_skin_2003_029_jisha.sfx | MISS | 8 |
| 11 | `effect\textures\glow\glow_14_cs.tga` | fx_skin_2003_029_jisha.sfx | MISS | 8 |
| 12 | `effect\textures\glow\glow_16_yh_djs.tga` | fx_skin_2003_029_hit.sfx, fx_skin_2003_029_jisha.sfx | MISS | 8 |
| 13 | `effect\textures\glow\tex_glow_01_cs_tp60_01.tga` | fx_skin_2003_029_jisha.sfx | MISS | 8 |
| 14 | `effect\textures\glow\tex_glow_guangci_tp78_01.tga` | fx_skin_2003_029_jisha.sfx | MISS | 8 |
| 15 | `effect\textures\glow\tex_glow_qirishijie_guangyun_hgz03_03.tga` | fx_skin_2003_029_jisha.sfx | MISS | 8 |
| 16 | `effect\textures\glow\tex_glow_ray_x10_01.tga` | fx_skin_2003_029_hit.sfx | MISS | 8 |
| 17 | `effect\textures\glow\tex_glow_tp07_05.tga` | fx_skin_2003_029_hit.sfx | MISS | 8 |
| 18 | `effect\textures\glow\tex_glow_tp61_02.tga` | fx_skin_2003_029_hit.sfx | MISS | 8 |
| 19 | `effect\textures\glow\tex_glow_x04_01.tga` | fx_skin_2003_029_hit.sfx | MISS | 8 |
| 20 | `effect\textures\glow\xing_01_yh_djs.tga` | fx_skin_2003_029_hit.sfx | MISS | 8 |
| 21 | `effect\textures\lightning\lighting_01_rzx_djs.tga` | fx_skin_2003_029_hit.sfx | MISS | 8 |
| 22 | `effect\textures\lightning\lightning_01_ycy_djs.tga` | fx_skin_2003_029_jisha.sfx | MISS | 8 |
| 23 | `effect\textures\lightning\tex_lightning_shandian_tp52.tga` | fx_skin_2003_029_hit.sfx | MISS | 8 |
| 24 | `effect\textures\trail\guangshu01_cjf_djs.tga` | fx_skin_2003_029_hit.sfx | MISS | 8 |
| 25 | `effect\textures\trail\keji_02_wh_djs.tga` | fx_skin_2003_029_hit.sfx, fx_skin_2003_029_jisha.sfx | MISS | 8 |
| 26 | `effect\textures\trail\tex_trail_huo_01_zhf_djs.tga` | fx_skin_2003_029_jisha.sfx | MISS | 8 |
| 27 | `effect\textures\trail\tex_trail_x07_01.tga` | fx_skin_2003_029_jisha.sfx | MISS | 8 |
| 28 | `effect\textures\trail\trail_11_lmq_djs.tga` | fx_skin_2003_029_jisha.sfx | MISS | 8 |
| 29 | `effect\textures\veins\noise_04_tp05.tga` | fx_skin_2003_029_jisha.sfx | MISS | 8 |
| 30 | `effect\textures\veins\tex_noise_y.tga` | fx_skin_2003_029_jisha.sfx | MISS | 8 |
| 31 | `effect\textures\veins\v_veins_tp116_08.tga` | fx_skin_2003_029_jisha.sfx | MISS | 8 |

⇒ `effects.json` 里这些节点的 `texture_candidate` / `texture_binding` **全为 null**、`texture_binding_status=unresolved_name_miss`、`texture_selection={}`；**未把任何候选说成源级**。


## 4. 3 条 `.spr` 命中（本轮新增发现）

| 声明路径 | 解析为 | 容器·row | bytes | sha16 | 头部（描述文件） |
|---|---|---|---|---|---|
| `effect\textures\lightning\lightning07_cs.spr` | `lightning07_cs.spr` | effect_01.gpk#207659 | 582 | `7d0ecce9fd3cddd7` | `1 512 512\r\n16\r\n1` |
| `effect\textures\lightning\lightning_01.spr` | `lightning_01.spr` | effect_01.gpk#207671 | 550 | `6e8b303b2233eb92` | `1 512 512\r\n16\r\n1` |
| `effect\textures\lightning\shandian_05_yh_djs.spr` | `shandian_05_yh_djs.spr` | effect_01.gpk#207712 | 168 | `94dedcf52b8712c8` | `0 256 256\r\n4\r\n10` |

`.spr` 是**精灵表描述文件**（首行 `行列 宽 高` + 帧序号），不是图像 ⇒ 其对应图集仍落在 31 条 MISS 的 `.tga` 里。已原样落盘 `1110177/sfx/tex/`。


## 5. `fx_skin_2003_029_dg.sfx` 与 `.fx` 的 MISS（如实登记）

- **`fx_skin_2003_029_dg.sfx`：按名 MISS**（已试 `effect\fx\weapon\skin\skin_2003_029\fx_skin_2003_029_dg.sfx`, `effect\fx\weapon\skin\skin_2003_029\fx_skin_2003_029_dg.fx`, `effect\fx\weapon\skin\skin_2003_029\fx_skin_2003_029.sfx`, `effect\fx\weapon\skin\skin_2003_029\fx_skin_2003_029_dg.sfx.txt`）。

- **引用它的字段**（板数据，非 sfx 内部）：`08Lifeafter wiki/data/boards/weapon_skin_sfx_text_sources.json` 中 `id=1110177 / skin_id=1110177`（极光剑）记录的 **`fire_sfx_path`**：

  ```json
  "fire_sfx_path": { "field_chs_slot": 16, "value_chs_slot": 54, "scalar_type": "0x05",
                     "text": "effect/fx/weapon/skin/skin_2003_029/fx_skin_2003_029_dg.sfx" }
  ```

  ⇒ 结论：该 sfx **被行为表引用但未随包发布**（同目录 `..._hit.sfx`/`..._jisha.sfx` 都在，唯独 `_dg` 不在）——**不是我们没找到，是包里没有**（56 个可表寻址容器 + 158 npk + 64 fpk 索引按路径全 MISS，Lead 已独立复核）。

- `.fx` 1 条 MISS：`shader\uber_fx_common.fx`（由 fx_skin_2003_029_hit.sfx, fx_skin_2003_029_jisha.sfx 引用）—— 需要在 `.fx`（着色器）级别，非本任务范围。


## 6. attach（挂点）：源未声明 ⇒ 不编造

- 两份 sfx 的节点均声明 `BindBonesHead=FALSE`、`SelBindBonesIdx=""`、`AnchorSum=0` ⇒ XML 侧**无骨骼/插槽挂点**。

- `effects.json.attach.anchor = null`；`mode=unresolved_sfx_declares_no_attach`；候选（1110177 武器 gim 的 `fx01` 等 5 个 socket，见 `_gim_out\skel\1110177_mount.json`）**只登记为同名族候选，未绑定**。


## 7. 只读验证：现有 adapter 能解析这份 effects.json（不改 adapter、不开浏览器）

做法：node 在无 DOM 的 stub 环境加载 `weapon_skin_sfx_adapter.js`（adapter_loaded=True），并把 adapter 源码里出现的每个 `effects.<键>` 读取点与这份 json 逐一对账。

- adapter 加载 **成功**，API：`attach, setModelsBase, models, modelMaterial, selfUrl, loaderCandidates`。

- 读取点共 10 个，全部存在（`effects.models_enabled` 属**按设计缺省**：不写=true ⇒ Model 分支默认关、fail-closed，开关由 `viewer.json` 侧控制）；唯一 `missing_keys` 里的 `effects.json` 是正则把注释文本 `effects.json 的 …` 误当键名的假阳性。

- 结构断言 **8 项全过**（schema / nodes 非空 / 每节点 name+tag / Model 节点都有 model_glb / **贴图候选全 null** / assets_base+textures_dir / loop_seconds / attach.anchor 为 null）。

- 原始证据：`03拆包产物/_target_1110171/FX029_src/FX029_adapter_check.json`（加载结果 + 读取点对账 + 逐条断言）。
- ⚠ 仍未验的：`attach(ctx)` 需要 THREE+场景，未在无头环境执行 ⇒ 本验证只到“可解析 + 字段对账”，不宣称渲染通过。


## 8. unresolved / 未做

- Model 节点：模型特效（本份已导出 24 GLB，适配器 Model 分支默认关）
- ParticleRes：粒子资源（源仅引用子帧 .sfx）
- Dummy：容器节点
- 贴图 31 条 effect\textures\{glow|alpha|debris|lightning|trail}\*.tga 按名全 MISS ⇒ unresolved（16 变体已试；独立只读子代理彻查中）
- blend_mode=7：观测到 1 次，但枚举值表在已扫范围内不存在（见 FXENUM_probe_report.json）⇒ 映射为 null，不猜
- .fx 1 条 MISS（fx_skin_2003_029_dg 相关引用，见 dg 段）
- attach：两份 sfx 均声明 BindBonesHead=FALSE / SelBindBonesIdx="" / AnchorSum=0 ⇒ 源未声明挂点
- **Sprite/ParticleSystem 节点 renderable_by_adapter = false**（无贴图即不可渲染，适配器 fail-closed）⇒ **这把皮肤的特效在 viewer 上仍不会显示**，直到 31 条贴图定位完成。

- `blend_mode=7`（观测 1 次）映射为 **null**：枚举值表已判 NOT_FOUND（`FXENUM_probe_report.json`），**禁止用观测分布反推枚举名**。

- `model_fields` 只保留了 Model 节点的原始 XML 属性 + ShaderComponent 子树（未把 uniform 轨道解释成颜色/缩放语义）。


## 9. 命令清单

```
C:\...\python.exe 01拆包器本体\工具库\06_皮肤定位链\locate_skeleton.py --id 1110177   # 仅用于 GpkIndex 复用
python %TEMP%\fx029_scan.py    # 取 2 sfx + 枚举 60 条声明资源（HIT/MISS + 容器·row·sha16）
python %TEMP%\fx029_glb.py     # 24 gim → GLB（export_glb 单集）
python %TEMP%\fx029_attach.py  # attach 字段扫描 + 3 spr 原样导出
python %TEMP%\fx029_build.py   # effects.json v3 + FX029_assets.json
node %TEMP%\fx029_adapter_check.js   # 只读验证
```