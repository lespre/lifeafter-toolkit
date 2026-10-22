# RX_fx_model_mtl：Model 节点 `MtlIdx` → 材质记录 → 贴图槽 —— 调查结论（只读）

> **交付**：本文件 + `RX_fx_model_mtl_20260919.json`。**未改任何既有文件**；未起浏览器；scratch 全部在 `%TEMP%`（抽出的 gim 在 `%TEMP%\gimout\`）。
> **一句话结论**：**"MtlIdx → 材质记录 → 贴图槽"这条链拿不到模型层贴图** ✗ —— 材质记录里**有槽名、但唯一被绑定的路径是 `common\textures\white.tga`（且该名字在 91 容器里 MISS）** ⇒ **模型层白块是源数据结构的结果**；`MtlIdx` 的**数值本身仍未解出**（卡在 c159 对象图的标签编码，已给原始字节）。

---

## 1. `MtlIdx` 从哪里来：**effect 的 `.gim` 本身就是一份 c159 对象图** ✓

抽 7 个 Model 的 gim（`find_entry_by_path --extract`，路径 `effect\mesh\weapon\skin\skin_2003_029\<mod>.gim` ✓ 均在 `E:\mrzh\res\effect_01.gpk`）：

| gim | 容器 row | dec 字节 | magic | 名字表里含 |
|---|---|---|---|---|
| `mod_skin_2003_029_mz_kj01_djs.gim` | 192312 | 329 | `c1 59 41 0d` = **C159410D** | `Sub0`/`SubMesh`/**`MtlIdx`(名字表 off 134)**/`Name`(141)/`PreZAlphaBlend`(146)/`BoundingHalf`/`MeshSortMethod`/`ModelSceneFlag` ✓ |
| `mz_ks01` / `dm_wuqi_01` / `56_hjl` / `dg_01` / `dg_wl_01` / `14_hjl` | — | 349–369 | 同 magic | **完全相同的名字表** ✓（字段名 @134/141/146 一致 ✓） |

- 名字表后的原始值区（可复核）：`a4 00 00 00 00 00 00 00 03 00 01 02 01 01 00 06 00 01 74 72 75…`（`mz_kj01` ✓）
- **`MtlIdx` 数值 = unresolved** ✗：既有解析器都试过且失败——
  · `c159_parser.py`（v1，magic `01 00 01 13`）→ **条目=0**（该 gim 不含此 magic ✗）
  · `parse_mtlidx_chain.py` 的绑定编码 `0a 02 <u32 MtlIdx> 0c 01 <name>` → 在这些 gim 里 **0 命中** ✗
  ⇒ 卡点是**该 c159 的标签编码**（不是加密、不是缺字段：`MtlIdx` 字段名在名字表里**确实存在** ✓）。**未穷尽**：`c159_pair.py v3` 未试（它是材质/绑定对解析器）⇒ 留给下一步 ✓

## 2. 材质表在哪：**effect 族的 c159** `shader\uber_fx_common.nfx2` **含材质/槽位记录** ✓（映射未定证）

`res.gpk` row 15714（dec 26,799 B，magic `C1 59 41 0D` ✓ 已抽至 `_target_1110171/fx_family/uber_fx_common.nfx2.bin`）里：

| 类别 | 内容 |
|---|---|
| **槽名（40 个）** | `Tex0` · `TextureFile` · `Textures` · **`t_mask01`** · `t_mask02` · **`t_distort_tex1`** · `t_distort_tex2` · **`t_dissolve_tex`** · `t_dissolve_dirmask_tex` · `t_fresnel_normalMap` · `t_addColor_tex` · `t_gradient` · `t_depth_tex` · `t_fow_buffer` · `t_gbuffer4` · `t_mip_fog` · `t_aerial_perspective_lut` · `t_volumtric_fog_volume` · `t_skin_bone_animation` · `SamplerName` · `SamShadowMap` · … ✓ |
| **贴图路径** | **只有 `common\\textures\\white.tga`，出现 10 次**（off **25925 / 25989 / 26074 / 26138 / 26202 / 26266 / 26330 / 26394 / 26458 / 26522** ✓ 间距 ~64 B ⇒ 10 条材质式记录 ✓），另 **1 条记录无贴图**（tail 里 `… 1d 02 00 00 00 00 …` ✓） |
| 记录内重复模板 | `01 59 00 01 00 03 0d 02 01 00 00 00 1a 02 06 00 00 00 1d 01` + 路径串 ⇒ 每条 = 槽绑定记录 ✓ |
| 尾部索引表 | last `white.tga` 之后为 `01 03 02 04 00 00 00 01` ×17 ✓（17 = 该族 17 个 ShaderComponent 量级 ✓，**未定证**） |

⇒ **很可能这就是 `MtlIdx` 索引的材质表** ✓（同一 effect 族的 c159 ✓、含全部槽名 ✓、条目数 10–17 ✓）——但 **`MtlIdx` 值未解 ⇒ 映射未定证** ✗（不猜 ✓）。
⇒ **`common\textures\white.tga` 名字级解析 = MISS** ✗（`find_entry_by_path` ✓）

## 3. 逐个材质的贴图槽：**槽名可得、路径不可得** ✓/✗
- **槽名**：上表 40 个 ✓（含 Model 分支实际用到的 4 个 PS 绑定名 `t_distort_tex1`/`Tex0`/`t_mask01`/`t_dissolve_tex` ✓ —— 与 `fx_family/9053b046_…asm` 的纹理绑定表**逐名对应** ✓✓ 这是"槽名属于该族"的强证据）
- **路径**：**全部 10 条记录绑的都是 `common\textures\white.tga`**（MISS ✗），**没有任何 per-material 的 .tga/.dds 路径** ✗
⇒ **"槽名可得、路径不可得"** ✓

## 4. 与同一 `.sfx` 里 Sprite/ParticleSystem 声明的关系：**不是同一批** ✗
`.sfx` 的 `Texture=` 值是**贴图文件路径**（23 条去重 ✓），与 FX 材质的**槽名**是**两个命名空间** ✓：
- 例：`effect\textures\glow\glow25.tga`(×3) · `effect\textures\glow\glow_01.tga`(×3) · `effect\textures\lightning\lightning07_cs.spr` · `effect\textures\trail\keji_02_wh_djs.tga` … ✓
- **实测按名解析（`find_entry_by_path`，23 条）**：**HIT 3 / MISS 20**
  - **HIT = 3 个 `.spr`** ✓：`effect\textures\lightning\lightning07_cs.spr` · `lightning_01.spr` · `shandian_05_yh_djs.spr`
  - **MISS = 20 个 `.tga`** ✗（glow/trail 全部）
⇒ **不能把 Sprite/PS 的 `.tga` 命中率数据套到 Model 层**（Model 材质根本没有这些路径 ✓）；唯一可用的实测是那 **3 个 .spr** ✓

## 5. 可行性结论（Lead 假设：证实/否证）
**否证** ✗：**`MtlIdx` 指向的材质记录里没有可用的模型层贴图路径** —— 唯一路径是白色贴图，且：
1. 该路径名字级 **MISS** ✗；
2. 材质记录**没有 per-material 的其它贴图路径** ✗；
3. 与 Sprite/PS 声明的 23 条路径**不同命名空间**，且其中 `.tga` **全 MISS** ✗
⇒ **"从材质链解出模型层贴图、从根上治白块"这条路走不通** ✗ ⇒ **模型层无贴图（源即如此）**，白块是**源数据结构的结果**（10 条记录全绑白色贴图 ✓）⇒ 若要改观，只能走**明确的创作/替换口径**（不属本任务、也不许我猜 ✗）

**仍 unresolved 的两点（都不是加密，是编码未解）**
| id | 项 | 已试/下一步 |
|---|---|---|
| U1 | `MtlIdx` 具体数值与取值分布 | 已试 `c159_parser.py`（0 条目）· `0a 02` 绑定编码（0 命中）⇒ 下一步用 `c159_pair.py v3` 或按名字表后的值区解码 |
| U2 | `MtlIdx` → 材质条目的映射（是否就是 §2 那 10 条） | 需 U1 解开后逐值核对；条目数 10 vs 尾部索引 17 的差异也未定证 |
**已排除**：① 模型 gim 里没有贴图字段名（名字表只有 `SubMesh/MtlIdx/Name/PreZAlphaBlend/…` ✓）；② FX 族 c159 里没有 per-material 贴图路径（只有 white.tga ✓）；③ `.sfx` 的 `Texture` 与模型材质槽不同批 ✓；④ 工作区无 `.mtg` ✓；⑤ 不是加密所致（c159 都能解出字符串 ✓，卡在标签编码 ✓）

## 6. 复核命令
```
# 抽 gim（只读源 + scratch）
python 03拆包产物\_gim_out\find_entry_by_path.py --extract "effect\mesh\weapon\skin\skin_2003_029\mod_skin_2003_029_mz_kj01_djs.gim" %TEMP%\kj01.gim
# 材质族 c159 的槽名/路径
python -c "import re;d=open(r'03拆包产物\_target_1110171\fx_family\uber_fx_common.nfx2.bin','rb').read();print([m.group().decode() for m in re.finditer(rb'[\x20-\x7e]{3,}',d)][-30:])"
# 23 条 effect 贴图路径 HIT/MISS
python %TEMP%\rxmtl3.py
```
