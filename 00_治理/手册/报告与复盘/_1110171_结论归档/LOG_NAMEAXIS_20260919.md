# LOG_NAMEAXIS_20260919 — `loading_record.bin` × GPK 哈希索引（O(1)）取证

- 任务：按 Lead 指定路线，用**加载日志的真实名字**打“名字轴”；`.mtg` 兄弟假设优先；能按名取到的真图全部导出；并对内容寻址假设做验证。
- 边界：**只读**（日志/容器/缓存目录全部只读）；**未改** `effects.json`/viewer/adapter/manifest/board；未起浏览器。
- 交付：本报告 + `LOG_NAMEAXIS_20260919.json` + 导出目录 `LOG_tex_20260919/`（39 张有名字的真图 PNG）。
- 性能：**未用 `find_entry_by_path`**；复用既有产物 `%TEMP%\gpk_hashset.bin`(30,445,008 B) + `gpk_hashset_rows.bin`(114,494,625 B) + `gpk_hash_index_meta.json`，用 numpy `searchsorted` 做 **O(1)/O(log n)** 查询（2,537,083 个 hash key / 4,579,785 条记录 / 91 个容器，载入 <1 s）。

---

## 0. 结论（TL;DR）

1. **`.mtg` 兄弟假设成立（最高优先项已完成）**：1110177 的 42 个 Model 节点 = **33 个唯一 stem**（16 个 `dg_*` + 17 个其它），它们在 `effect_01.gpk` 里**每个都有 `.gim` / `.mesh` / `.mtg` 三件套**，共 **99 条记录（row 191892–192335）**，**全部按名命中**（构造兄弟路径 + O(1) 索引）。
2. **`.mtg` = 明文 `c159410d` 材质文件**，可直接读出**贴图槽名与声明路径**（例：`mod_skin_2003_029_dg_wl_03_djs.mtg` → `effect\textures\glow\glow_01.tga` + `effect\textures\alpha\alpha_tp61_lsy_djs.tga`；材质名 `Material #5`、shader `shader\uber_fx_common.fx::TShader`、宏 `USE_MASK01`/`USE_FRESNEL`）。
3. ⚠️ **但 `.mtg` 只有名字、没有任何内容 id**（全文 8~16 位十六进制 token = **0**）；其声明的 **72 个贴图名，0 个能按名命中容器** ⇒ `.mtg` 是**名字证据**，不能直接取内容。
4. **日志 × 索引命中率（按扩展名）**：文件类 **100%**（`.gim` 1539/1539、`.mtg` 1273/1273、`.bin` 160/160、`.sfx` 89/89、`.spr` 13/13）；**贴图类几乎全不可按名取**（`.tga` **39/2322 = 1.7%**、`.png` 0/405、`.fx` 0/46、`.dds` 0/8）。`effect\` 子集 540 条里 `.tga` 只有 **1/40**。
5. **能按名取到的真图已全部导出**：**39 张**（有名字、有容器 row、有内容 sha16）→ `LOG_tex_20260919/*.png`。其中 effect 侧 1 张：`effect\textures\trail\trail_05_yh_djs_uvva.tga`（**真实 TGA type-2 256×256**，非 DDS —— 容器里 `.tga` 与 DDS 混装）。
6. **34 条声明名分级**（详见 §4）：`mtg_exact_declared` **3**（`glow_01.tga`/`noise_04_tp05.tga`/`tex_noise_y.tga`）、`log_exact_observed` **3**（`glow_04_tp29.tga`/`glow_14_cs.tga`/`lightning07_cs.spr`）、`same_prefix_observed` **1**（`glow25.tga`↔日志 `glow25_d2.tga`）、`same_stem_in_mtg` **1**（`shandian_05_yh_djs.spr`↔`.mtg` 点名的 `shandian_05_yh_djs.tga`）、`same_family_only` **21**、`no_name_evidence` **5**。**全部只是名字证据，不是同一性证明。**
7. **内容寻址假设成立（附带决定性发现）**：`res\{effect,model,character,weapon}` 下 **2,041 个 32-hex 名文件全部是 `1DPW` 块**，样本 `e3eaa46ef974bc248b143dc95b0eb8e9` 解密后为 **DDS 2048×2048**，且 **`md5(payload)` 恰等于文件名**；该文件名同时等于 **`effect.idx` 第 365 条的键**（`pkg=255`，文件大小 = 48 + psz 精确吻合）⇒ **它是“运行时物化的内容寻址缓存”，`pkg=255` 就表示“已物化到此缓存”**。反查名字的可行步骤见 §5.3（**按 Lead 要求本轮不做关联**）。
8. **可取 / 不可取**（§6）：33 个 Model 的三件套 + 39 张命名贴图 **有证据可取**；34 条声明里其余 **32 条 `.tga` 仍不可取证**（没有名字→内容通道），**未用任何候选顶替**。

---

## 1. 方法（可复现、零全表扫）

| 环节 | 做法 |
|---|---|
| 日志解析 | `loading_record.bin`（1,950,952 B）中取可打印 ASCII 串，筛出含路径分隔符且以已知扩展名结尾者 ⇒ **5,359 条唯一路径**（`.tga` 2,322、`.gim` 1,539、`.mtg` 1,273、`.png` 405、`.bin` 160、`.sfx` 89、`.fx` 46、`.spr` 13、`.dds` 8；`effect\` 前缀 **540** 条） |
| 命中判定 | `fid=(murmur3(path,0x77777777)<<32)\|murmur3(path,0x66666666)` → 在既有索引的 2,537,083 个 key 上二分 ⇒ **O(log n)，单次 <10 µs**；正控：`lightning07_cs.spr`、`glow03.spr`、`wood03.spr` 等日志路径全部命中 |
| 解包 | 与既有工具一致：`base(16) + row_off + 20` → `flag=12` ⇒ zstd；再按魔数分支（DDS→`texture2ddecoder`；**TGA type-2/3/10/11→PIL**；PNG/JPEG→PIL） |
| `.mtg` | 33 个 stem 的构造兄弟路径 3,976 条候选（同 `.gim` 目录换扩展 + 去 `_djs`/加 `_pt` + 4 个候选目录） |

---

## 2. `.mtg` 兄弟假设（最高优先项）

**结果：成立且完整。** 33 个 stem 的三件套（`.gim`/`.mesh`/`.mtg`）全部命中，且同一 stem 的三件套在容器里**连续相邻 row**（例：`dg_01` → gim 192057 / mesh 192058 / mtg 192059），说明它们是同一批次烘进容器的同源资产。

节选（完整 99 条见 JSON `mtg_sibling_hypothesis.skin_2003_029_hits`）：

| stem | `.gim` row | `.mesh` row | `.mtg` row | `.mtg` 解出 |
|---|---|---|---|---|
| `mod_skin_2003_029_14_hjl_djs` | 191892 | 191893 | 191894 | 1,144 B 明文 |
| `mod_skin_2003_029_dg_01_djs` | 192057 | 192058 | 192059 | 1,420 B 明文 |
| `mod_skin_2003_029_dg_wl_01_djs` | 192096 | 192097 | 192098 | 1,078 B 明文 |
| `mod_skin_2003_029_dm_wuqi_01_djs` | 192210 | 192211 | 192212 | 1,288 B 明文 |
| `mod_skin_2003_029_mz_shandian03_djs` | 192333 | 192334 | 192335 | 1,498 B 明文 |
| …（33/33 全中，row 191892–192335） | | | | **33/33 明文** |

**⚠️ 一处前提更正**：**日志里没有任何 `2003_029` 路径**（0 条；日志只含 `weapon\skin\skin_2003_015\…` 与 `character\monsters\*2003*` 等无关条目）⇒ 本次命中**不是靠日志**，而是“兄弟路径构造 + O(1) 索引”直接命中。结论不变，但归因要写对。

### 2.1 `.mtg` 的结构（源级可读）

```
magic c159410d | u32 长度 | NUL 分隔 tag 表 | 数值/字符串值区
tag 表样例: AnimParam / LightingMaterial / Macro0..MacroN / Material / MaterialGroup / Material_0 /
            NeoX / ParamTable / RenderStates / ShaderMacro / Technique / Tex0 / TransparentMode /
            t_mask01 / t_addColor_tex / t_distort_tex1 / t_dissolve_tex / u_emissivecolor / u_maintex_tilling_x …
材质名: Material #5       shader: shader\uber_fx_common.fx::TShader      宏: USE_MASK01 / USE_FRESNEL
贴图声明（`01 00 01 13 01 <path>`，NUL 结尾）:
    effect\textures\glow\glow_01.tga
    effect\textures\alpha\alpha_tp61_lsy_djs.tga
```
- **33/33 明文**，无加密层；`c159410d` 是二进制魔数（不是文本串）。
- **无内容 id**：全文 8~16 位十六进制 token 计数 = **0**；所有贴图引用都是可读路径字符串。
- 33 个 `.mtg` 共声明 **72 个唯一贴图路径**，域分布：`veins` 最多，其次 `alpha`、`glow`、`trail`、`lightning`、`special`、`fire`，另有 1 条武器本体贴图 `weapon\skin\skin_2003_029\textures\skin_2003_029001a.tga`。
- **这 72 个声明名 0 个能按名命中任何容器**（§3 同一索引）⇒ `.mtg` 给出的是**模型层期望的名字**，取不到内容。

---

## 3. 日志 × 索引：命中率（按扩展名）

| 扩展名 | 全路径命中 | `effect\` 子集命中 | 说明 |
|---|---|---|---|
| `.gim` | **1,539 / 1,539 (100%)** | 199 / 199 | 模型几何 |
| `.mtg` | **1,273 / 1,273 (100%)** | 199 / 199 | 材质（§2） |
| `.bin` | **160 / 160 (100%)** | — | 配置/表 |
| `.sfx` | **89 / 89 (100%)** | 89 / 89 | 特效脚本 |
| `.spr` | **13 / 13 (100%)** | 13 / 13 | 声明表 |
| `.tga` | **39 / 2,322 (1.7%)** | **1 / 40** | 仅少量 `.tga` 直存容器 |
| `.png` | 0 / 405 | 0 / 0 | — |
| `.fx` | 0 / 46 | — | shader 源（不在容器） |
| `.dds` | 0 / 8 | 0 / 0 | — |

**读法**：凡是“文件型资源”（模型/材质/脚本/配置）**名字就是键、100% 可取**；凡是**贴图型资源**，绝大多数只能走 idx/wpk（内容寻址、无名字）——与上一棒 `idx key = md5(内容)` 的结论互证。

---

## 4. 34 条声明名分级（**只是名字证据**）

| 分级 | 条数 | 名单 |
|---|---|---|
| `mtg_exact_declared`（`.mtg` 同路径声明，源级） | **3** | `glow_01.tga`、`noise_04_tp05.tga`、`tex_noise_y.tga` |
| `log_exact_observed`（日志同路径） | **3** | `glow_04_tp29.tga`、`glow_14_cs.tga`、`lightning07_cs.spr` |
| `same_prefix_observed`（日志同前缀） | **1** | `glow25.tga`（日志有 `glow25_d2.tga`） |
| `same_stem_in_mtg`（`.mtg` 里同 stem） | **1** | `shandian_05_yh_djs.spr` → `.mtg` 点名 `effect\textures\lightning\shandian_05_yh_djs.tga` |
| `same_family_only`（仅同族目录） | **21** | 含 `dian_12.tga`、`glow_16_yh_djs.tga`、`lightning_01.spr`、各种 `tex_glow_*`、`tex_trail_*` 等 |
| `no_name_evidence`（无任何同级/前缀/族） | **5** | `alpha_01_tp52_01.tga`、`tex_alpha_mask_tp60_04.tga`、`tex_alpha_tp104_04.tga`、`tex_crack_02_yx_djs.tga`、`tex_crack_tp71_05.tga` |

- **`mtg_exact_declared` 的含义**：模型层 `.mtg` 里出现了**完全相同的路径**，即“该模型期望加载这张图”。这是目前**最高等级的名字证据**，但**仍不是内容同一性**（`.mtg` 不携带内容 id）。
- `lightning_01.tga` / `lightning07_cs.tga`：既不在日志同路径、也不在 33 个 `.mtg` 的声明里 ⇒ 只有族目录证据 ⇒ **不可取证**。
- 上表**没有**任何“候选顶替”等级：不存在 `content_candidate` 之类的推断性绑定。

---

## 5. 能按名取到的真图（已导出）与内容寻址缓存

### 5.1 导出清单（39 张）

- 目录：`03拆包产物/_target_1110171/LOG_tex_20260919/`（**39 个 PNG**，文件名 = `<原名>__<内容 sha16>.png`）
- effect 侧唯一一张：`effect\textures\trail\trail_05_yh_djs_uvva.tga` → `trail_05_yh_djs_uvva__709e68551f7b7103.png`（**TGA type-2 256×256**，容器 `effect_02.gpk` row 1219，fid `878d10a56259101e`）
- 其余 38 张为 `scene_bw\jiayuan\jiayuan02_content\terrain\matidtex\*.tga`（65×65 地形材质贴图）等
- 格式事实：这批 `.tga` 在容器里是**真实 TGA 文件**（不是 DDS）⇒ 解码必须按魔数分支（DDS / TGA / PNG / JPEG）

### 5.2 内容寻址缓存（判定：**成立**）

| 项 | 实测 |
|---|---|
| 位置 | `E:\mrzh\Documents\res\{effect,model,character,weapon}\` |
| 数量/命名 | **2,041 个文件，文件名均为 32 位 hex**；**全部 `1DPW` 魔数** |
| 样本 | `effect\e3eaa46ef974bc248b143dc95b0eb8e9`（1,088,827 B）→ `stage1(AC)` → `DTSZ/ZSTD` → **DDS 2048×2048** |
| 关键等式 | **`md5(payload) = e3eaa46ef974bc248b143dc95b0eb8e9` = 文件名** ✔ |
| 与 idx 的关系 | 该 hex **正是 `effect.idx` 第 365 条的键**；文件大小 **= 48 + psz(1,088,779)** 精确吻合；该条 `pkg=255` |
| 语义 | ⇒ **缓存 = 按内容 md5 命名的无名字内容库**；`pkg=255` = “该条已物化到 `res\<family>\<md5>` 缓存” |

### 5.3 用它反查名字的可行步骤（**本轮按 Lead 要求不做关联**）

1. 由日志建立 `(时间戳 double, 读入顺序, 路径)` 序列；
2. 与缓存文件 `mtime` 对齐：**新落盘的那个 md5 文件 ↔ 那一刻被读入的路径**；
3. 顺序一致性二次校验：同一 `.mtg`/`.sfx` 里声明的贴图**出现顺序** vs 该时段缓存落盘顺序；
4. 累积 `name → md5` 表后，用 `idx key = md5` 规则把名字直接翻成 idx 条目/缓存文件。

**⚠️ 限制（必须随结论传递）**：缓存 mtime 跨 **2026-04-27 ~ 2026-06-19**，而本次日志会话是 **2026-05-13**，同日文件**只有 2 个** ⇒ 单次日志的配对窗口很窄；要成表需**多会话日志**或更强顺序约束，不能靠这一份日志配全。

---

## 6. 结论：哪些有证据可取、哪些仍不可取证

**现在有证据可取（名字命中 ⇒ 可直接按名取用）**
1. **1110177 的 33 个 Model stem × `.gim`/`.mesh`/`.mtg` 三件套（99 条，row 191892–192335，`effect_01.gpk`）** —— 模型与材质层 100% 按名可取；`.mtg` 明文，可直接读出模型期望的贴图路径（可据此驱动 viewer 的材质覆盖，替代猜测）。
2. **39 张命名 `.tga`**（含 1 张 effect 侧）—— 有名字、有容器 row、有内容 sha16，已导出 PNG。
3. 日志里 **3,078 条**文件型名字命中（`.gim` 1,539 + `.mtg` 1,273 + `.bin` 160 + `.sfx` 89 + `.spr` 13 + `.xml` 4）—— 需要时可再导出。

> 口径说明：本报告的“34 条声明名”= `FX029_report.md` 声明表 31 条 `.tga` + 3 条 `.spr`；正则扫描该报告还会多抓到一处**散文 glob** `effect\textures\*.tga`，已剔除（它不是真实声明项）。

**仍不可取证（不得用候选顶替）**
1. **34 条声明里其余 32 条 `.tga`**：`.mtg` 只写名字、idx 只认内容 md5 ⇒ **没有“名字→内容”通道**。
2. `lightning_01.tga` / `lightning07_cs.tga`：无同路径、无 `.mtg` 声明 ⇒ 仅族目录证据。
3. 其中 3 条（`glow_01.tga` / `noise_04_tp05.tga` / `tex_noise_y.tga`）虽拿到 `.mtg` **源级同名声明**，但那只证明“哪个模型用它”，**不构成内容同一性**。

**本轮未把任何候选写成绑定**；所有结论只落在“名字命中（容器 row 可查）/ 源级声明（`.mtg` 同路径）”两个等级上。

---

## 7. 更正与边界登记

1. **Lead 前提更正**：日志中 `2003_029` 路径 **0 条** ⇒ “日志里有 1110177 相关 `.mtg`”不成立；`.mtg` 命中来自构造兄弟路径 + O(1) 索引。
2. **上一轮推测更正**：`pkg=255` 不是“哨兵/终止条目”，而是**已物化到内容寻址缓存**的标记；第 365 条**其实可从缓存文件解出**（本轮未把它计入候选池筛选）。
3. 只读边界：未改 `effects.json` / viewer / adapter / manifest / board；新增文件仅本报告、同名 JSON 与导出目录 `LOG_tex_20260919/`。

---

## 8. 复现

| 脚本（`%TEMP%`） | 作用 |
|---|---|
| `LOG_scan.py` | 日志解析（5,359 路径）+ `effect\` 540 条 O(1) 命中率 |
| `LOG_scan2b.py` | `.mtg`/`.mesh`/`.gim` 兄弟假设（3,976 候选 → 120 命中） |
| `LOG_mtg_decode.py` | 33 个 `.mtg` 解包 + 72 条贴图引用 |
| `LOG_mtg_full.py` | 单个 `.mtg` 全文与引用上下文（判定无内容 id） |
| `LOG_scan3.py` / `LOG_export2.py` | 34 条声明名分级 / 39 张命名贴图导出 |
| `LOG_cache.py` | 内容寻址缓存语义验证（md5 == 文件名 == idx 365 键） |
| `LOG_build.py` | 组装本报告对应 JSON |
