# TEXTSEARCH_20260920 — 用"缺失贴图的名字"做全盘文本搜索 + 客户端目录清点（task-83）

- 任务：**task-83**（已 `claim`）。只读；只写本报告与同名 `.json`；**未改任何既有文件**。
- 搜索编码：**ASCII + UTF-16LE** 双编码。
- 执行范围（逐项给台账，见 §5）：两个 install 的 `Documents\` 全树、`res\*.idx` 全字节、9 个 NPK 容器逐条目解包内容。

---

## 0. 结论先说（最重要的一条）

> ### ✅ **找到了"名字 → 内容哈希"的权威表**
> **`E:\mrzh\res.npk` 的 entry 8858（80,369,252 B）** 内含 **529,370 条**记录，格式：
> ```
> <正斜杠路径> {"checksum": "<32 hex = md5>", "has_alpha": N, "img_size": [w, h]}
> 例：effect/textures/alpha/alpha_01_tp52_01.tga {"checksum": "21825119883ba4ec5548bb454e1c3087", "has_alpha": 1, "img_size": [128, 128]}
> ```
> - **397,105 个唯一 checksum**；`effect/` 前缀 **7,505** 条（`effect/textures/` **7,399**、`effect/mesh/` 40）。
> - **我们的 34 条声明名里有 29 条在清单中，带 checksum 与源尺寸**（缺 5 条，见 §1）。
> - **checksum 语义已端到端证实 = `md5(原始资产字节)`**：`Documents\res\ui\<checksum>` 是 `1DPW` 块，`stage1 + ENON/DTSZ` 解出 payload 后 **`md5(payload) == 文件名 == 清单 checksum`**（抽 3 个全中）；清单里这些 checksum 对应的名字是 UI 贴图路径（如 `ui/spine/djl_vx/bingo/bingo.png`）。
> - **取回链（已验证）**：`名字 → (res.npk 清单) checksum → res\<family>\<checksum>（1DPW）→ stage1 → payload（md5 自校验）`。
>
> ### ⚠️ 但"我们的 29 条"本机 **没有物化**（0/29）
> - 全盘按 checksum 找文件名：命中 **32 个**（都在 `Documents\res\ui\`），**29 条声明名的 checksum 一个都不在其中**；2,041 个 `res\{effect,model,character,weapon}\<md5>` 也不含它们的 checksum。
> - ⇒ 本机只存了 **转码后的 DDS**（`effect.idx`/`effect3.wpk`，键 = md5(DDS 载荷) ≠ 源资产 checksum），**源 `.tga` 资产未落盘**。要拿真图，只能按 checksum 去取源资产（补丁源/另一台客户端/服务器）。

**附带两条可直接用的源级证据**
1. **29 条声明名的源尺寸**（清单 `img_size`）——例如 `glow_01.tga`=**128×128**、`dian_12.tga`=**128×128**、`glow_16_yh_djs.tga`=**128×128**、`noise_04_tp05.tga`=256×256、`lightning_01_ycy_djs.tga`=**256×512**。
2. **3 条与现有绑定尺寸冲突**：`dian_12.tga` / `glow_01.tga` / `glow_16_yh_djs.tga` = 清单 **128×128** vs 现绑定 **256×256** ⇒ 同名复用绑定在**源尺寸**上可疑。

---

## 1. 逐名字结果表（34 条声明名）

| 声明名 | 清单 checksum（前 12） | 源尺寸 | 现绑定尺寸 | 判定 |
|---|---|---|---|---|
| `alpha_01_tp52_01.tga` | `21825119883b…` | 128×128 | — | 有源尺寸、无绑定 |
| `tex_alpha_mask_tp60_04.tga` | `dabc31dd38d9…` | 128×128 | — | 有源尺寸、无绑定 |
| `tex_alpha_tp104_04.tga` | `5bbb4f060b3e…` | 128×128 | — | 有源尺寸、无绑定 |
| `tex_crack_02_yx_djs.tga` | — | — | — | **清单中无此项** |
| `tex_crack_tp71_05.tga` | `1d702b420e44…` | 256×256 | — | 有源尺寸、无绑定 |
| **`dian_12.tga`** | `e5f1db051e8b…` | **128×128** | 256×256 | ⚠ **尺寸冲突** |
| `glow01_yc.tga` | `84efe77e2650…` | 128×128 | — | 有源尺寸、无绑定 |
| `glow25.tga` | `251812d75ca6…` | 128×128 | — | 有源尺寸、无绑定 |
| **`glow_01.tga`** | `6a62146a607a…` | **128×128** | 256×256 | ⚠ **尺寸冲突** |
| `glow_04_tp29.tga` | `bc433f097d46…` | 256×256 | — | 有源尺寸、无绑定 |
| `glow_14_cs.tga` | `a83585b4b726…` | 128×128 | — | 有源尺寸、无绑定 |
| **`glow_16_yh_djs.tga`** | `f9d3f01663e6…` | **128×128** | 256×256 | ⚠ **尺寸冲突** |
| `tex_glow_01_cs_tp60_01.tga` | `e4965e6d6153…` | 128×128 | — | 有源尺寸、无绑定 |
| `tex_glow_guangci_tp78_01.tga` | `f93ddd8eba46…` | 256×256 | — | 有源尺寸、无绑定 |
| `tex_glow_qirishijie_guangyun_hgz03_03.tga` | — | — | — | **清单中无此项** |
| `tex_glow_ray_x10_01.tga` | `70df89e784d0…` | 256×256 | — | 有源尺寸、无绑定 |
| `tex_glow_tp07_05.tga` | `b22eab96d375…` | 256×256 | — | 有源尺寸、无绑定 |
| `tex_glow_tp61_02.tga` | `13f6afafa4df…` | 128×128 | — | 有源尺寸、无绑定 |
| `tex_glow_x04_01.tga` | `88376ddd6daa…` | 128×128 | — | 有源尺寸、无绑定 |
| `xing_01_yh_djs.tga` | `c391a3ea1ffe…` | 256×256 | — | 有源尺寸、无绑定 |
| `lighting_01_rzx_djs.tga` | `bed9757de9e9…` | 256×256 | — | 有源尺寸、无绑定 |
| `lightning07_cs.spr` | — | — | 256×256 | **清单中无此项** |
| `lightning_01.spr` | — | — | 512×512 | **清单中无此项** |
| `lightning_01_ycy_djs.tga` | `b932678b71e3…` | **256×512** | — | 有源尺寸、无绑定（非方形） |
| `shandian_05_yh_djs.spr` | — | — | 256×256 | **清单中无此项** |
| `tex_lightning_shandian_tp52.tga` | `361619e3f01d…` | 256×256 | — | 有源尺寸、无绑定 |
| `guangshu01_cjf_djs.tga` | `850421aa7263…` | 256×256 | — | 有源尺寸、无绑定 |
| `keji_02_wh_djs.tga` | `9260569e5a8e…` | 256×256 | — | 有源尺寸、无绑定 |
| `tex_trail_huo_01_zhf_djs.tga` | `6402211af237…` | 128×128 | — | 有源尺寸、无绑定 |
| `tex_trail_x07_01.tga` | `bb6a7f3fb516…` | 128×128 | — | 有源尺寸、无绑定 |
| `trail_11_lmq_djs.tga` | `ce89117be139…` | 256×256 | — | 有源尺寸、无绑定 |
| `noise_04_tp05.tga` | `c75ac975be9a…` | 256×256 | — | 有源尺寸、无绑定 |
| `tex_noise_y.tga` | `04491eb734d8…` | 128×128 | — | 有源尺寸、无绑定 |
| `v_veins_tp116_08.tga` | `7462553b1942…` | 256×256 | — | 有源尺寸、无绑定 |

**逐"搜索范围 × 名字"的命中表**（本轮 4 类范围）：

| 范围 | 结果 |
|---|---|
| 两个 install 的 `Documents\` 全树（18,453 文件 / 19.31 GB，ASCII+UTF-16LE） | **9 处命中**：`loading_record.bin` 7 处（`glow_01`、`glow25`、`lightning07_cs`、`effect\textures\veins`×4）、两侧 `script.py314.lc.npk` 各 1 处（`glow_01`，嵌在 `fx_glow_01` 里）。**无新的名字表** |
| `res\*.idx` 全字节（27 个 .idx，共 2.27 MB） | **0 命中**（键是 md5，不含名字；与既有结论一致） |
| NPK 逐条目解包内容（LifeAfter 5 个 + mrzh 2 个） | LifeAfter：`script.py3.npk` **107 处**、`script.py314.lc.npk` **107 处** 命中（大清单里的路径串）；`ui.npk`/`res.npk`/`script.npk` 0 处。mrzh：**`res.npk` 30/34 声明名精确命中**（即 §0 的清单）、`script.py314.lc.npk` 0 处精确命中 |
| GPK/NPK fid 哈希轴复核（20,000 个清单名字 × murmur3(路径)） | **0 命中**（GPK 0、`res.npk` 0、`ui.npk` 0）⇒ **NPK 的 fid 不是路径哈希** |

> **注意口径**：`script.py3.npk` 的 107 处"命中"绝大多数是**子串巧合**（例如 `lightning_01` 命中在 `m_1103_shield01_lightning_01.sfx` 里、`glow_01` 命中在 `fx_bg_lanchao_daizi_glow_01_gz.sfx` 里），**不是我们的资产**。真正的资产级命中只有 `res.npk` 的清单。

---

## 2. 目录清点表（两个 install）

| 顶层目录 | mrzh 文件 / 大小 | LifeAfter 文件 / 大小 | 说明 |
|---|---|---|---|
| `gres` | 35 / 70.4 GB | 45 / 94.7 GB | GPK 容器（名字轴已排除） |
| `res` | 2,268 / 5.2 GB | 12,788 / 9.9 GB | `.idx`（27 个）+ `.wpk` + **无扩展名 md5 物化文件**（`res\ui\<checksum>` 就在这里） |
| `bin` | 866 / 3.3 GB | 1,233 / 4.8 GB | 客户端二进制（`.dll/.pak/.exe/.log/.bin`）**已全文扫** |
| `(root)` | 61 / 1.2 GB | 63 / 1.3 GB | `res.npk`、`ui.npk`、`script*.npk`、`.json/.ini/.txt` |
| `g66discrete` | 5,712 / 0.77 GB | 698 / 1.25 GB | 回放/媒体（`.pipe/.mp4/.vd/.jpg`），已跳过 `.pipe` |
| `multi_cloud1/2` | 339 / 0.12 GB | 391 / 0.84 GB | 云补丁（`.thh/.thx/.json/.ini/.wpk/.idx`） |
| `thd` + `thdext2..9` | 116 / 0.014 GB | 116 / 0.014 GB | 纹理解压缓存头（`.thh/.thx`）**已扫** |
| `loading_records` | 1 / 2.0 MB | — | 加载日志（已知） |
| `db` | — | 3 / 0.00005 GB | `shader_compile.db`（SQLite 12 KB）**已扫** |
| `extract` | 33 / 0.16 GB | 56 / 0.27 GB | `.mp4` |
| `Record` | — | 0 文件 | 空目录 |
| **合计** | **9,510 / 81.2 GB** | **15,572 / 113.1 GB** | 全树 25,082 文件 / 194.3 GB |

**扫描台账**：跳过 `.gpk` 80 + `.wpk` 144 + `.mp4` 151 + `.pipe` 6,254 个文件（175.0 GB，均为已排除容器或媒体）；**实扫 18,453 文件 / 19.31 GB / 0 读取错误**。

---

## 3. 可疑文件清单（按价值排序）

| # | 文件 | 是什么 | 为什么可疑/有价值 |
|---|---|---|---|
| 1 | **`E:\mrzh\res.npk` entry 8858**（80,369,252 B） | **529,370 条 `<path, md5, has_alpha, img_size>` 清单** | ⭐ **名字轴的权威表**；含 7,505 条 `effect/` 路径；本任务 29/34 声明名在此 |
| 2 | `Documents\res\ui\<checksum>`（32 个，1.0–5.5 MB） | **以 md5 命名的 1DPW 物化资产**（解出为 PNG） | 证实 checksum = md5(payload)，并给出"按名取回资产"的落点与解码链 |
| 3 | `script.py3.npk` / `script.py314.lc.npk`（365 / 400 MB；mrzh 456 MB） | Python 字节码容器，内含多个大清单（entry 42622 = **159,566 条路径**、66367 = 字符串表） | 客户端资源路径全集（45,899 条 `effect/`），可用于**名字存在性**与**同族名**检索 |
| 4 | `Documents\loading_records\loading_record.bin`（2.0 MB） | 引擎加载日志（已知） | 本轮命中 7 处；含**同一时段的时间戳**（如 `4569546242576`）⇒ 与 §0 的 checksum 资产可做时间/顺序关联 |
| 5 | `Documents\db\shader_compile.db`（12 KB SQLite） | shader 编译缓存 | 体量最大的"数据库"候选；已全文扫，无声明名命中 |
| 6 | `Documents\thd\*.thh/*.thx` + `thdext2..9`（各 0.4 MB） | 纹理解压缓存头 | 命名像"纹理目录"；已扫，无命中 |
| 7 | `Documents\multi_cloud*`（0.12 / 0.84 GB） | 云补丁配置（`.json/.ini/.wpk/.idx`） | 含 `.idx/.wpk` 对（小型容器），已扫 |

---

## 4. 明确回答三个问题

1. **有没有任何地方能给"名字→内容"或至少"名字→内容哈希"？**
   → **有（名字→内容哈希）**：`E:\mrzh\res.npk` 的 entry 8858 给出 `名字 → md5(源资产) + has_alpha + 源尺寸`；且"名字→内容"的**取回链已端到端验证**（32 个 UI 资产：清单 checksum == `res\ui\<checksum>` 的 payload md5）。
   → **但本机拿不到我们那 29 条的内容**：它们的 checksum 文件在本机不存在（0/29），源资产未物化。
2. **清单里有哪些我们的名字？** 29/34（缺 5：`tex_crack_02_yx_djs.tga`、`tex_glow_qirishijie_guangyun_hgz03_03.tga`、`lightning07_cs.spr`、`lightning_01.spr`、`shandian_05_yh_djs.spr`——3 个 `.spr` 属"描述文件"而非贴图资产，清单里本就只收贴图）。
3. **现有绑定有没有被源尺寸打脸？** 有 3 条：`dian_12.tga`、`glow_01.tga`、`glow_16_yh_djs.tga`（清单 128×128 vs 绑定 256×256）。

**未命中的部分（写明范围与编码，不写"确认不存在"）**
- 已搜：两个 install 的 `Documents` 全树（18,453 文件 / 19.31 GB；ASCII + UTF-16LE；`.gpk/.wpk/.mp4/.pipe` 按既有取证跳过）、27 个 `res\*.idx` 全字节、9 个 NPK 容器逐条目解包内容（LifeAfter `ui.npk` 35 条 / `res.npk` 3,114 条 / `script.npk` 531 条 / `script.py3.npk` 81,148 条 / `script.py314.lc.npk` 110,836 条；mrzh `script.py314.lc.npk` 105,777 条 / `res.npk` 16,905 条）。
- **未搜**（如实登记）：`E:\mrzh\res\ui.npk`（3.3 GB）与 `E:\LifeAfter` 之外的其它 NPK 大类（不在 Lead 指定范围）；`effect_cache.gpk` 等已证明非贴图池的容器；`.gpk/.wpk` 内部字节（名字轴已由既有多轮取证排除，且体量 164 GB）。

---

## 5. 只读核对

- 本轮**只新增** 2 个文件：`TEXTSEARCH_20260920.md`、`TEXTSEARCH_20260920.json`（都在 `03拆包产物/_target_1110171/`）。
- 对 `E:\mrzh\Documents`、`E:\LifeAfter\Documents`、`E:\mrzh\res.npk`、`*.idx`、NPK 容器的访问全部为**只读打开**（`open(...,'rb')` / `os.walk` / `getsize`），无写操作。
- 未改 `effects.json` / `viewer.json` / `viewer.js` / adapter / `board.html` / `neox_material.json`（这些不在本轮任何写入路径中）。

## 6. 复现

| 脚本（`%TEMP%`） | 作用 |
|---|---|
| `TS_inventory.py` | 两个 Documents 树清点（目录/文件数/扩展名/可疑文件） |
| `TS_scan.py` | 全树 ASCII+UTF-16LE 流式搜索（18,453 文件 / 19.31 GB） |
| `TS_npk.py` / `TS_hits_detail.py` / `TS_manifest.py` | NPK 逐条目搜索与命中深挖 |
| `TS_record.py` / `TS_manifest_struct.py` | 清单记录结构探测（有无并行 id/哈希） |
| `TS_exact.py` | manifest 路径 × 34 声明名精确匹配 |
| `TS_manifest_full.py` | 抽全量 529,370 条清单 + 三轴 fid 校验 |
| `TS_fetch_by_csum.py` / `TS_csum_files.py` | 按 checksum 找物化文件 + 语义验证 |
| `TS_size_table.py` / `TS_build.py` | 源尺寸对照表 / 交付 JSON 组装 |
