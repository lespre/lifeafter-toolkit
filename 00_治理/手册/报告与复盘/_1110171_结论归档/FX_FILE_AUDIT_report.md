# FX_FILE_AUDIT — 《明日之后》武器皮肤特效（SFX）引用资源彻查

**审计日期**：2026-09-18
**工作目录**：`E:\la拆包项目`（**只读取证**；脚本全部写在 `%TEMP%\fx_audit\`；未修改项目内任何既有文件）
**扫描范围**：`E:\mrzh` 下 91 个 `.gpk`（成功索引 90）+ **158** 个 `.npk`（分布在 11 个子目录）+ 64 个 `.fpk`
**索引条目键合计**：**5,318,147**（GPK 2,102,975 + NPK 1,145,522 + FPK 2,069,650），构建耗时 17 s
**交付**：本文件 + `FX_FILE_AUDIT.json`（逐条机读）

> **版本说明**：本文件为**终稿**，替换任务预置骨架（骨架中 `lightning07_cs.spr` / `lightning_01.spr` / `shandian_05_yh_djs.spr` 三条"已知命中"本轮已独立复现，row 依次 207659 / 207671 / 207712，与骨架一致）。
> **并行作业提示**：审计期间另有一路代理写入同一路径。其草稿中的两条前提**经本轮原始字节复核为误**，已在 §4.5 用原文逐字纠正。本终稿只采用可复核的原始字节证据。

---

## 0. 结论先行

| 问题 | 判定 | 关键数字 |
|---|---|---|
| `effect\textures\glow\*.tga`、`alpha\*.tga`、`debris\**\*.tga` 在不在包里？ | **按名不可达** | 声明 **366** 条 `.tga`，命中 **1** 条（且在 `effect_02.gpk`，属 `veins`，**非** glow/alpha/debris）；366 个名字换成 `.dds/.png/.spr/.spd` 再试仍 **0** |
| 特效贴图本身有没有？ | **有** | `effect\textures\**.spr` 声明 **52** 条，**52 条精确命中**（同名+同目录+同扩展），全部落在 `effect_01.gpk` |
| 这两套名字是同一批吗？ | **不是** | `.tga` 声明名集合与 `.spr` 声明名集合 **basename 交集 = 0** |
| 贴图本体在哪？ | `effect_01.gpk` 内的**匿名 DDS** | 抽样 30,300 行 → **1,070 条 DDS**，其中 **1,069 条 `dxgiFormat=98`(BC7_UNORM)**，尺寸 256²/128²/64²/512²/1024² |
| 能不能拿到？ | **能定位，未出图** | 已抽到 DDS 字节（sha16 见 §6）；解成 PNG 需 `texture2ddecoder`，**本机所有 Python 均未安装** |

**一句话**：SFX 文本里写的 `.tga` **不是客户端的发布形态**；发布形态是**同名的 `.spr` 精灵表描述符**，它自己的逻辑路径 100% 精确可达。这是 **①「在包里，但声明名与发布名不同轴」**，已定位到容器 + 行号 + 字节数 + sha16 —— 只差 BC7 解码做像素级终审。

---

## 1. 方法与可复现性：先证明工具是对的

### 1.1 索引规模

| 容器 | 数量 | 条目键 |
|---|---|---|
| `.gpk` | 91（成功 90，失败 35\*） | 2,102,975 |
| `.npk` | **158**（`E:\mrzh` 下 11 个子目录：`res` 1、`res\building` 1、`res\character` 10、`res\model` 62、`res\model\bigworld` 1、`res\scene` 5、`res\scene_bw` 6、`res\scene_bw\bigworld` 44、`res\ui` 22、`mrzh` 3、`Documents` 3） | 1,145,522 |
| `.fpk` | 64（预建 `fpk_fid_index.json`） | 2,069,650 |
| **合计** | | **5,318,147** |

\* 91 个 `.gpk` 中 35 个无法索引，**全部**位于 `E:\mrzh\Documents\gres`，解密后 magic 非 `HPGF`（见到 `RPGF`/`tPGF`/`gPGF` 及单字节变体）。见 `unresolved[GPK_HEADER_VARIANTS]`；这些包**未**被搜索特效贴图。

> 条目数说明：5,318,147 是**实测**键对总数；任务简报的 3,336,339 可能是子集容器或去重口径。
> `.npk` 数量说明：`Get-ChildItem E:\mrzh -Recurse -Filter *.npk` 实测 **158**（已按目录分布列于上表）。另有一路代理称".npk 实际只有 4 个"，本轮实测**不成立**（`res\ui.npk` 一个就有 33 亿字节；`Documents`/`scene*`/`model`/`character` 下均存在）。本报告采用实测 158。

### 1.2 AES 解密自证（全链条地基）

本机**没有任何 Python 装有 `cryptography` / `Crypto` / `pyaes` / `texture2ddecoder`**（对 Python 3.10 / 3.11 / 3.12 及 `01拆包器本体\.buildenv` 逐个 `importlib.find_spec` 验证）。既有工具 `find_entry_by_path.py` 因此无法直接运行。本轮自建两条实现：

- `fx_aes.py` —— 纯 Python AES-128-ECB
- `cng_aes.py` —— Windows CNG（`bcrypt.dll`）+ ctypes，约 **1 GB/s**（纯 Python 仅 18 KB/s，相差约 5 万倍，是本轮能扫全量的关键）

用 **5 条独立证据**钉死正确性（含一路独立第三方复核）：

| # | 证据 | 结果 |
|---|---|---|
| 1 | FIPS-197 C.1 官方向量：`key=000102…0f`，`ct=69c4e0d86a7b0430d8cdb78070b4c55a` | → `00112233445566778899aabbccddeeff` ✅ |
| 2 | 与手写的 canonical FIPS-197 实现逐块对拍（4 密钥 × 64 随机块 = 256 次） | decrypt 不匹配 **0/256** ✅ |
| 3 | 90 个真实 `.gpk` 前 64 B 解密后 `head[4:8]` 与 `u32@20` | magic = **`HPGF`**，且 `64+N*32 ≤ filesize` → **90/90** ✅ |
| 4 | 158 个真实 `.npk` 前 32 B 解密为 `<QIIII>` | `table_offset + entry_count*48 ≤ filesize` → **158/158** ✅ |
| 5 | **独立第三方复核**（另一路代理从零自写 S-box/T-table 实现，S-box 由 GF(2⁸) 现场推导） | FIPS-197 C.1 通过；`effect_01.gpk` 得 `HPGF` / N=212152；六行数据与本轮**逐字段一致**；`o+36` zstd 帧膨胀到**恰好 50117 B** 且首字节 `<FxGroup`，sha256[:16] `b3f6deb2c63d22ff` **完全相同** ✅ |

> **顺带修正一条既有假设**：`.gpk` 的 magic 是 **`HPGF`**（`head[4:8]`）。
> 早先"`KPGF`"的来源已查明：同一头部 `head[56:60]` 另有字节序反转的 `KPGF`（`4B 50 47 46`）——两者都在同一个 64 字节头里，容易误读。
> 第三方复核还指出：`head[24:28]` 在 `effect_01.gpk` 恰好 = `filesize - 16`，但在 `textures.gpk` 不等于 `filesize-16`，**该字段不是常数**，不宜作为判据。

### 1.3 哈希→行号映射：实证而非假设

对已知路径逐字段、逐编码枚举，只有一种成立：

| 声明路径 | 行号 | 表中 `u32_6` | 表中 `u32_7` | 判定 |
|---|---|---|---|---|
| `effect\fx\weapon\skin\skin_1003_010\fx_skin_1003_010_dd.sfx` | 37295 | `57E71CAD` | `01EC32C5` | `[6]=mm3(p,0x66666666)`、`[7]=mm3(p,0x77777777)` ✅ |
| `…\fx_skin_1003_010_dd_lx.sfx` | 37296 | `6F1AA73C` | `F5492AF8` | 同上 ✅ |
| `…\skin_2003_029\fx_skin_2003_029_hit.sfx` | 38420 | `ECF13093` | `CEE54CB5` | 同上 ✅ |

**反证（同样重要）**：同一路径改成正斜杠后，两个格子**立刻都不匹配** → 确认是「反斜杠 + 原样大小写 + latin1」，不是任何归一化形式。

### 1.4 载荷解码验证

| 行号 | `o` | comp | dec | flag | 压缩段头 12 B | 解出 | sha16 |
|---|---|---|---|---|---|---|---|
| 37295 | 139460504 | 4159 | 50117 | 12 | `28b52ffd60c5c2ad81008a67` | 50117 B | `b3f6deb2c63d22ff` |
| 37296 | 139464684 | 1739 | 13997 | 12 | `28b52ffd60ad350d3600b637` | 13997 B | `6e8582714e7e79fb` |
| 37297 | 139466444 | 4433 | 66053 | 12 | `28b52ffda0050201002d8a00` | 66053 B | `4faf348cbe58c9a9` |
| 37322 | 139545824 | 5160 | 129785 | 12 | `28b52ffda0f9fa0100e5a000` | 129785 B | `59115620b779a5e8` |
| 38420 | 143008880 | 5840 | 94278 | 12 | `28b52ffda0467001006c6100` | 94278 B | `d406a3b00a0f890e` |
| 38433 | 143056452 | 9248 | 154301 | 12 | `28b52ffda0bd5a0200ac7a00` | 154301 B | `0e6cfb5ff9f08996` |

`28b52ffd` = zstd magic；解出文本均以 `<FxGroup` 开头 → 与既有结论「`.sfx` 是 XML 风格文本」一致。**全链条打通。**
（第三方复核独立复现了 37295 的全部数值，含完整 sha256 `b3f6deb2c63d22fff798b6f32ca6136a94a8478b31d91a0d0e5d9adb5f08baea`。）

---

## 2. A1：全游戏武器皮肤 SFX 枚举（名字候选法）

**名单来源**：`03拆包产物\_target_1110171\ROSTER_g5_g6.json` → **34 个唯一模型 stem**（对应 37 条 id 记录）
**后缀词表**：任务指定 29 个 + 从 `asset_path_dictionary.jsonl` 真值补齐 66 个（`dm`/`dd_01`/`zishen_01`/`fashuchang`/`jinghe_daoguang_01` 等）= **95 个**
**路径形状**：`effect\fx\weapon\skin\<stem>\fx_<stem>_<suffix>.sfx`

### 2.1 命中率

| 指标 | 数值 |
|---|---|
| 候选路径总数 | **3,230** |
| **命中** | **164**（命中率 **5.1%**） |
| 有 ≥1 命中的 stem | **30 / 34** |
| 命中容器 | **`effect_01.gpk` 164/164**（无跨包） |
| 命中条目 flag | **全部 12（zstd）** |

**4 个零命中 stem**：`skin_1006_002`（1110013 幻影狩蝎）、`skin_1002_007`（1110146 龙渊永寂）、`skin_2003_017`（1110116 赤月晶魄）、`skin_1006_009`（1110132 炽日耀斑）
→ 这 4 个皮肤的特效**不在这套命名下**，或后缀在词表之外。**不构成「无特效」结论**，只说明候选法在这 4 个 stem 上 0 命中。

### 2.2 命中分布（每 stem）

```
skin_1003_010:16  skin_1012_013:14  skin_1007_009:13  skin_1007_007:12  skin_1001_013:11
skin_2003_029:11  skin_1001_011: 9  skin_1001_014: 8  skin_1002_009: 8  skin_1006_010: 7
skin_1006_008: 6  skin_1006_011: 5  skin_1012_009: 5  skin_1012_011: 5  skin_2003_019: 4
skin_1001_008: 3  skin_1003_005: 3  skin_1006_004: 3  skin_1007_002: 3  skin_1007_004: 3
skin_1001_004: 2  skin_1013_003: 2  skin_2003_013: 2  skin_2003_018: 2  skin_2003_022: 2
skin_1001_012: 1  skin_1007_008: 1  skin_1012_012: 1  skin_1013_007: 1  skin_2003_005: 1
```

### 2.3 完整命中清单

**164 条，全量见 `FX_FILE_AUDIT.json` → `A1_sfx_enumeration.hits[]`**（含 container / row / flag / comp / dec）。示例 12 条：

| 行号 | 路径 |
|---|---|
| 36933 | `effect\fx\weapon\skin\skin_1001_004\fx_skin_1001_004_dd_03.sfx` |
| 36934 | `effect\fx\weapon\skin\skin_1001_004\fx_skin_1001_004_fashuchang.sfx` |
| 37124 | `effect\fx\weapon\skin\skin_1001_014\fx_skin_1001_014_fashuchang.sfx` |
| 37276 | `effect\fx\weapon\skin\skin_1003_005\fx_skin_1003_005_dd_01.sfx` |
| 37295 | `effect\fx\weapon\skin\skin_1003_010\fx_skin_1003_010_dd.sfx` |
| 37416 | `effect\fx\weapon\skin\skin_1006_004\fx_skin_1006_004_dd.sfx` |
| 37659 | `effect\fx\weapon\skin\skin_1007_002\fx_skin_1007_002_dd_01.sfx` |
| 38012 | `effect\fx\weapon\skin\skin_1012_009\fx_skin_1012_009_dd_01.sfx` |
| 38204 | `effect\fx\weapon\skin\skin_1013_003\fx_skin_1013_003_dm_01.sfx` |
| 38253 | `effect\fx\weapon\skin\skin_2003_005\fx_skin_2003_005_zishen_01.sfx` |
| 38367 | `effect\fx\weapon\skin\skin_2003_019\fx_skin_2003_019_daoguang_01.sfx` |
| 38420 | `effect\fx\weapon\skin\skin_2003_029\fx_skin_2003_029_hit.sfx` |

---

## 3. A2：SFX 内声明资源全量提取

**164 条 SFX 全部提取 + 正则抽路径** → **1,633 条去重声明路径**。

| 指标 | 数值 |
|---|---|
| 解析 SFX 数 | **164**（全部成功，无提取失败） |
| 去重声明路径 | **1,633** |
| 声明 ≥1 条 `.tga` 的 SFX 数 | **150 / 164** |
| `.tga` 声明**出现次数**（含重复） | **996** |

> **150/164 个 SFX 都声明了 `.tga`** —— 「贴图缺失」不是个别皮肤问题，而是**全量系统性现象**。
> 同时，**同一个 SFX 里 `.tga` 与 `.spr` 声明并存**（见 §4.5 原始文本），说明这不是"新旧版本二选一"，而是引擎在同一份 XML 里按类型分别取用两种资源。

---

## 4. A3：逐条解析（核心）

对 1,633 条声明路径，每条按 13 类变体（原样 / 扩展名互换 / 大小写 / 去一层目录 / 去两层 / 加 `res\`、`assets\`、`common\` 等 7 种前缀 / 正斜杠 / 去扩展名）解析 → **共试 21,141 个候选路径**（另加 §4.4 的 100,080 条具名容器候选）。

### 4.1 按顶层目录 × 扩展名的命中矩阵

| 顶层目录 | 扩展名 | 声明数 | **命中数** | 命中率 |
|---|---|---|---|---|
| `effect\fx` | `.sfx` | 77 | **77** | **100%** |
| `effect\mesh` | `.gim` | 1130 | **1127** | **99.7%** |
| `effect\textures` | `.spr` | 52 | **52** | **100%** |
| **`effect\textures`** | **`.tga`** | **366** | **1** | **0.3%** |
| `effect\mesh_h` | `.gim` | 1 | 0 | 0% |
| `weapon\skin` | `.gim` | 2 | **2** | **100%** |
| `shader\*.fx` | `.fx` | 5 | 0 | 0% |
| **合计** | | **1633** | **1259** | **77.1%** |

**读法**：`.sfx` / `.gim` / `.spr` 三类几乎 100% 命中，说明**哈希口径与工具链完全正确**；唯独 `.tga` 塌成 0.3%。**这不是工具问题，是资源问题。**

> `shader\*.fx` 5 条 0 命中：着色器很可能编在 exe/独立格式里，不在 gpk/npk/fpk 命名空间；属**未决**（§9.6）。

### 4.2 核心问题：有没有任何一条 `effect\textures\*` 命中？

**有 53 条 —— 但 52 条是 `.spr`，只有 1 条是 `.tga`，且那条不是 glow/alpha/debris。**

**唯一命中的 `.tga`（原始声明 vs 实际命中名，并排）**：

| | 值 |
|---|---|
| **原始声明** | `effect\textures\veins\tex_xingdian_02_uvva.tga` |
| **实际命中名** | `effect\textures\veins\tex_xingdian_02_uvva.tga`（**逐字节相同**） |
| 容器 / 行号 | `E:\mrzh\res\effect_02.gpk` row **2140** |
| flag / comp / dec | 12 (zstd) / 197,830 / **4,194,348** |
| 解出 sha16 | `c540a52b3e289b70` |
| 解出头 16 B | `00000200000000000000000000040004` |

→ 这**不是改名**，而是**原样存在**。证明：`.tga` 命名形态在客户端**确实存在**（`veins` 目录），只是 glow/alpha/debris 那 366 条不在。

### 4.3 推出的命名规则：两套平行的名字，零交集

**规则**：客户端把「特效贴图」按**精灵表描述符**（`.spr`，**明文本**）发布，描述符文件名与 SFX 声明名**逐字节一致**；而 SFX 里另有一批 `.tga` 声明，其名字**在容器里不存在任何形态**。

`.spr` 描述符真实格式（**明文本**，已完整解出，`effect_01.gpk` row 206926）：

```
1 256 256\r\n
9\r\n
10000\r\n
glow03.tga 0 0 85 85\r\n
glow03.tga 85 0 171 85\r\n
…（共 9 行子矩形）
```

字段 = `<mode> <W> <H>` / `<bpp>` / `<param>` / 然后 N 行 `<name>.tga x0 y0 x1 y1`（子矩形切分）。**即描述符自己写明它引用 `glow03.tga`。**

**52 条精确命中的 `.spr` 全清单**（全部 `effect_01.gpk`，全部 flag=12）：

| 目录 | 文件（row） |
|---|---|
| `debris\glass` | `bingkuai_01_yx_djs.spr` (205923) |
| `debris\leaf` | `huaban_02_yh_djs.spr` (205971)、`huaban_03_zy_djs.spr` (205973) |
| `debris\other` | `boli01_lj_djs.spr` (206127)、`boli_03_zy_djs.spr` (206130)、`debris01.spr` (206141) |
| `debris\rock` | `rock02.spr` (206510) |
| `fire` | `fire02.spr` (206617)、`fire_01_jzj_djs.spr` (206653)、`tex_fire18_tp52.spr` (206724) |
| `fire_hd` | `fire18_zy_djs.spr` (206760)、`fire19_zy_djs.spr` (206762)、`tex_fire_f1_007a_hgz01.spr` (206774) |
| `fx` | `duye04.spr` (206832)、`duye05.spr` (206834) |
| `fx\yellow` | `yellow01.spr` (206883) |
| **`glow`** | **`glow03.spr` (206926)、`glow08.spr` (206932)、`glow13.spr` (206940)、`glow_smg_01.spr` (207127)、`tex_glow_suipian_hgz01_01.spr` (207406)、`tex_glow_tp07_02.spr` (207414)** |
| `lightning` | `lightning07_cs.spr` (207659)、`lightning_01.spr` (207671)、`lightning_01_pt_djs.spr` (207675)、`shandian_05_yh_djs.spr` (207712) |
| `muzzleflash` | `muzzleflash03.spr` (207773)、`muzzleflash19_jzj_djs.spr` (207793)、`muzzleflash27.spr` (207801)、`muzzleflash28.spr` (207803)、`tex_muzzleflash_tp07_01.spr` (207821) |
| `smoke` | `smoke03.spr` (208447)、`smoke14.spr` (208464)、`smoke17.spr` (208470)、`smoke25.spr` (208478)、`smoke27.spr` (208482)、`smoke_01_wfj_djs.spr` (208532)、`tex_smoke_yan_tp71.spr` (208633) |
| `smoke_hd` | `smoke02.spr` (208672)、`smoke_wf_07.spr` (208680)、`smoke_wf_25.spr` (208691) |
| `sparks` | `sparks01.spr` (208712) |
| `special` | `tex_special_caisefangkuai_tp60_01.spr` (211285)、`tex_special_fangkuai_tp52.spr` (211384)、`tex_special_shuijing_hgz03_01.spr` (211836)、`tex_special_yinfu_tp60_01.spr` (45)、`xingzuo_01_yh_djs.spr` (487) |
| `trail` | `trail05.spr` (1080) |
| `water` | `water068_lv.spr` (2564)、`water39.spr` (2610)、`xq_beijinghua2.spr` (2700) |
| `water\blood` | `blood45_zy_djs.spr` (2328) |

**关键否证**：这 52 个已命中的 `.spr` basename 与 366 个声明 `.tga` 的 basename **交集 = 0**。
例：SFX 声明 `…\glow\glow01.tga`、`glow10_d.tga`、`tex_glow_xr_03_cc.tga`；包里有 `glow03.spr`、`glow08.spr`、`glow13.spr` —— **编号不同、集合不同**。

### 4.4 「改名」结论的量化依据

| 测试 | 候选数 | 命中 |
|---|---|---|
| 366 条声明 `.tga` → 换成 `.dds` | 366 | **0** |
| 366 条声明 `.tga` → 换成 `.png` | 366 | **0** |
| 366 条声明 `.tga` → 换成 `.spr` | 366 | **0** |
| 366 条声明 `.tga` → 换成 `.spd` | 366 | **0** |
| 366 条声明 `.tga` → 换成 `.jpg` | 366 | **0** |
| 366 个 basename × 6 扩展名（全交叉） | 2,196 | **0** |
| 418 条声明贴图路径 × 5 交叉扩展名 | 2,090 | **0** |
| 365 个 basename × 28 个 `effect\textures` 子目录 | **10,210** | **1**（即 §4.2 那条 `veins`） |
| 417 个 basename × 20 种前缀根 × 4 扩展名，打向 `textures.gpk`/`textures_bw.gpk`/`effect_cache.gpk` | **100,080** | **0** |

**累计为「改名」假说试过的候选路径：> 104,000 条，命中 1 条（且非目标类别）。**

### 4.5 ★ 对并行草稿两条前提的原文级纠正

审计期间另一路代理在草稿里写下两条前提。本轮**回到原始字节**逐字复核，两条**均不成立**：

**（a）"sfx 声明 `effect\textures\glow\tex_glow_tp07_02.tga`，而索引里存在 `…\tex_glow_tp07_02.spr` ⇒ 声明 `.tga`／实际 `.spr`"**

对 `effect\fx\weapon\skin\skin_1003_010\fx_skin_1003_010_zs.sfx`（row 37320）原始文本正则扫描，`tex_glow_tp07_02` 的**唯一出现形式**是：

```
'tex_glow_tp07_02.spr"'      ← 声明就是 .spr，不是 .tga
```

同一 SFX 内的 `.tga` 声明是**另外 6 个名字**：`glow40_tp30.tga`、`glow_gyun_01_smg.tga`、`glow_tp17_04.tga`、`star_xing_02_tp165.tga`、`tex_glow_ray_tp60_01.tga`、`caihong_06_jh_djs.tga`。

**（b）"`glow13.spr` 佐证 `.tga`→`.spr` 改名"**

对 `fx_skin_1003_010_dm.sfx`（row 37297）原始文本扫描，唯一出现形式是：

```
'glow13.spr"'                ← 同样是 .spr 声明
```

**结论**：`.spr` 条目命中的原因**不是**"`.tga` 被改名成 `.spr`"，而是**SFX 本来就把它声明为 `.spr`**。"名字改写"这条因果链**不成立**；正确的因果是"**引擎对两类贴图采用两套资源类型**"。

**同时补一条并行草稿里可信的观察**（本轮未独立复核其 manifest 数字，标注为**转引**）：
`03拆包产物\effect_01\manifest.json`（212,151 条）给出 `effect_01.gpk` 的扩展名构成 `.c159` 111,572 / `.mesh` 52,990 / `.bin` 39,535 / **`.dds` 7,501** / `.rgis` 553，且 `effect_cache.gpk` **99,800 条全部 `.bin`、0 贴图** —— 与本轮 §5.2「`effect_cache.gpk` 99,801 行 0 张图」**方向一致**，交叉印证。
（若该 manifest 可信，则 `effect_01.gpk` 的 DDS 总数为 **7,501**，比本轮 stride=7 抽样外推值更准。**转引，未复核**。）

---

## 5. B4：内容路线 —— 贴图实际在哪

因为容器不存名字，改从**内容**入手。

### 5.1 头 64 字节 magic 分布（压缩前）

`effect_01.gpk` 载荷段（`o+36` 起）首 4 字节**全是 `28b52ffd`（zstd）** → 只看压缩段头区分不出类型，**必须先解压再判**。

### 5.2 解压后 magic 分布（决定性）

| 容器 | 抽样行数 | 解压后分类 |
|---|---|---|
| `effect_01.gpk` row 205000–205399 | 400 | **DDS 397** / 其他 3（`.spr` 描述符文本 + 1 条 TGA 裸头 `00000200`） |
| `effect_01.gpk` 全包 stride=7 | 30,300 | **DDS 1,070**（dxgi 98 = **1,069**）/ 其他 29,230 |
| `effect_cache.gpk` row 0–1999 | 2,000 | zstd 2000 → 解压后**全部** `ccaa5566`（**非图片**） |
| `textures.gpk` | 564（全量） | **DDS 505** / 其他 59 / 失败 3 |
| `textures_bw.gpk` | 614（全量） | **DDS 536** / 其他 78 / 失败 3 |

### 5.3 纹理条目逐条记录（`effect_01.gpk`）

| row | comp | dec | dxgiFormat | 尺寸 | DDS sha16 | 抽取产物 |
|---|---|---|---|---|---|---|
| 205000 | 9,408 | 87,556 | **98 (BC7_UNORM)** | 256×256 | `fa11e58619079607` | `%TEMP%\fx_audit\proof_effect01_row205000.dds` |
| 205001 | 3,396 | 87,556 | **98** | 256×256 | `44eb78973ad0563c` | `…row205001.dds` |
| 205009 | 1,287 | 5,636 | **98** | 64×64 | `7293028bb7b8bf57` | `…row205009.dds` |

**尺寸分布**（30,300 行抽样）：256²×378、64²×333、128²×175、512²×97、32²×45、1024²×25、16²×8、512×1024×4、128×256×2、4×4×1。

**自洽性校验**：BC7 256² 主 mip = 65,536 B，加 8 级 mip ≈ 87,376 B；DDS 头 16+124=140 B；合计 ≈ 87,516 B，**实测 dec = 87,556 B**（差 40 B，属 header 字段差异）→ **是完整 DDS，不是残缺数据**。

### 5.4 这些贴图能否与 SFX 声明的贴图对应？

**不能直接对应，理由决定性**：
1. 声明的名字在容器里**任何扩展名都查不到**（§4.4）→ 没有「名字桥」。
2. 容器内是**匿名哈希条目**，无法枚举名字（既有结论，本轮独立复现）。
3. `.spr` 描述符虽**明文本写着自己引用的 `.tga` 名**（如 `glow03.tga`），但**那个 `.tga` 同样不在容器里** → 描述符里的 `.tga` 只是**逻辑名/历史名**，真正的位图是匿名 DDS。
4. 因此「声明 `.tga` ↔ 匿名 DDS」的最终绑定**只能靠尺寸/数量/顺序或解码看形状**。解码被 BC7 挡住（§9.1）。

---

## 6. B5：项目里「以前是怎么拿到特效贴图的」

**找到了既有成果，读到了源码级出处。**

### 6.1 既有产物

```
08Lifeafter wiki\assets\3d\weapon_skin\1110171\sfx\tex\
    glow_01.png  glow10_d.png  glow_02_sk2.png  glow_16_yh_djs.png
    glow_26_tp37.png  glow_tp25_08.png  tex_glow_xr_03_cc.png
    lightning07_cs.png  lightning1_rzx_djs.png  ray_01_sk.png  dian_12.png
    + 17 个 16 位十六进制哈希名 .png
08Lifeafter wiki\assets\3d\weapon_skin\1110171\sfx\tex_candidates_provenance.json
```

### 6.2 当时用的路径（读 provenance 得出）

`tex_candidates_provenance.json` 内容形如：

```json
"glow10_d.tga": { "dds": "77af349fc90bbd4c.dds", "size": [256,256], "decoder": "texture2ddecoder" }
```

**判读**：
- 当时**确实拿到了**这些贴图（11 个有名字 + 一批哈希名）。
- 但记录的 provenance 里，源文件是 **16 位十六进制内容哈希 `.dds`**，**不是逻辑路径**。
- 结合本轮结论（366 条 `.tga` 按名全不可达），**当时的成功路径是「内容路线」而非「名字路线」** —— 与既有日志 `06（agent写）拆包器进展与交接日志.md` §14.1 第 648 行「匿名纹理墙 6 路证伪、缺的是 fid→路径全局名表」完全一致。

### 6.3 项目既有工具（本轮已定位，未改写）

| 文件 | 作用 |
|---|---|
| `01拆包器本体\工具库\10_应用核心\toolkit_core\resource_resolver.py` | `parse_mtg` / `iter_kpgf_entries` / `decode_bcn_dds` / `find_unique_in_gpk` / 递归 `build_index` |
| `01拆包器本体\工具库\10_应用核心\toolkit_core\texture_extractor.py` | BCn 解码 + 颜色/HSV 打分 → 候选 PNG 联系表 |
| `01拆包器本体\工具库\06_皮肤定位链\dds_rgba_canonical.py` | BCn 输出通道序 canonical（`texture2ddecoder` 输出为 **BGRA**） |
| `08Lifeafter wiki\data\asset_path_dictionary.jsonl` | 34,679 条脚本引用逻辑路径（**本轮用作 sfx 名字真值来源**） |

### 6.4 本轮复现情况

| 环节 | 状态 |
|---|---|
| 定位并抽取 DDS 字节 | ✅ **已复现** —— 3 条，sha16 `fa11e58619079607` / `44eb78973ad0563c` / `7293028bb7b8bf57` |
| DDS 解成 PNG | ❌ **未复现** —— 本机无 `texture2ddecoder`；Pillow 11.1.0 不认 BC7/DX10 |
| 自建 BC1/BC3 解码器 | ✅ **已建成并逐像素验证**（见下），但**对本次目标无用**（目标是 BC7） |

**BC1/BC3 自建解码器的验证强度**（本轮新增能力，供后续复用）：用项目内 **2,036 个真实 DDS** 对拍 —
(A) 与项目自带 `texture2ddecoder` 真值 PNG 比 RGB：**max-abs-diff = 0，差异像素比例 0.0000000000**（517 BC1 + 1519 BC3）；
(B) 四个通道（含 alpha）与 Pillow 11.1.0 **独立** DXT1/DXT5 解码器比：**max-abs-diff = 0（全部 2036 个）**。
正确变体 = RGB565 位复制扩展 + **截断（floor）**插值；四舍五入变体会偏 ±1。
**但它按设计拒绝 `dxgiFormat 98`（BC7）**，而本次目标贴图**正是 BC7**。

**为什么本机没有 `texture2ddecoder`**：对 `Python310` / `Python311` / `Python312` / `01拆包器本体\.buildenv` 四个解释器逐个 `importlib.find_spec`，**全部为 False**。既有 `resource_resolver.decode_bcn_dds` 在缺库时按设计返回 `None`。这是**环境缺口，不是代码问题**。

---

## 7. B6：`effect_cache.gpk` / `textures.gpk` / `textures_bw.gpk` 点名测试

用**本轮全部 164 条 SFX** 声明的**全部 417 个贴图 basename**，逐个打这三个包：

| 容器 | 行数 | 探测候选数 | 命中 |
|---|---|---|---|
| `textures.gpk` | 564 | 33,360 | **0** |
| `textures_bw.gpk` | 614 | 33,360 | **0** |
| `effect_cache.gpk` | 99,801 | 33,360 | **0** |
| **合计** | | **100,080** | **0** |

**顺带查明这三个包到底是什么**（内容路线）：

| 容器 | 真实内容 |
|---|---|
| `textures.gpk` | 通用材质库：564 行中 **505 行解出 DDS**（多为 1,398,276 B 的 1024²）→ 与既有结论「通用 tiling 库、非皮肤专属」一致 |
| `textures_bw.gpk` | 同类黑白版：**536/614 行解出 DDS** |
| `effect_cache.gpk` | **99,801 行，0 张图片**。全部解压为 magic **`ccaa5566`** 的二进制块（`ccaa5566 02000000 01000000 00000000`），形似序列化缓存/配置 → **不是贴图容器** |

> `effect_cache.gpk` 是**排除项**：特效贴图**不在**这里。

---

## 8. C：明确判定（三种情况都带正反证据）

### 判定：①「在包里，但声明名与发布名不同轴」—— ①的一个特定子型

**支持它的证据**
1. `effect\textures\**.spr` **52/52 精确命中**，同名同目录同扩展，落在 `effect_01.gpk` —— 证明「特效贴图」确实发布在客户端，且**命名精确可查**。
2. `.spr` 是**明文本描述符**，内容直接写明它引用 `glow03.tga` 之类的名字 —— 证明 `.tga` 是引擎的**逻辑名**。
3. `effect_01.gpk` 内含 **1,070 张匿名 DDS**（BC7_UNORM，256²/128²/64²/512²/1024²），正是辉光/遮罩类贴图的典型形态与尺寸；转引 manifest 更给出 **7,501** 张 `.dds`。
4. `effect\mesh\*.gim` **1127/1130（99.7%）**、`effect\fx\*.sfx` **77/77（100%）** 命中 —— 证明哈希口径与工具链无误，`.tga` 的 0.3% 是**资源侧现象**而非工具假阴性。
5. 唯一命中的 `.tga`（`effect\textures\veins\tex_xingdian_02_uvva.tga`，`effect_02.gpk` row 2140，4,194,348 B）证明 `.tga` 命名形态**在客户端确实存在**，只是不在 glow/alpha/debris 那 366 条上。

**反对它的证据（必须并列）**
1. 把 366 条 `.tga` 换成 `.dds`/`.png`/`.spr`/`.spd`/`.jpg`，全交叉扫描 **2,196 个候选，命中 0**。**没有任何改名方向成立。**
2. `.tga` 声明名集合与 `.spr` 声明名集合 **basename 交集为 0**（`glow03/08/13.spr` vs `glow01/glow10_d/tex_glow_xr_03_cc.tga`）。**不是同一批资源的两种写法。**
3. 10,210 个 basename×子目录组合只命中 1 条（且属 `veins`，非目标类别）。
4. **`effect_cache.gpk` 99,801 行里 0 张图** —— 「缓存里另有一份」的退路被排除。
5. **无法证明**「某个匿名 DDS = 某条声明的 `.tga`」：容器不存名字，且 BC7 解码缺口让我们连形状比对都做不了。

### 判定：②「真的没发布」—— 对「`.tga` 这个名字」成立，对「贴图内容」不成立

- **支持**：>104,000 个候选路径全部落空；跨 5 种扩展名 0 命中。
- **反对**：`effect_01.gpk` 里有 1,070 张 BC7 特效类贴图，`.spr` 描述符齐全。**内容显然是发布了的。**
- **结论**：**「`.tga` 名未发布」≠「贴图未发布」**。按名查不到**不能**说成文件不存在 —— 这正是本报告要区分的事。

### 判定：③「在别的容器 / 别的格式里」—— 部分成立

- **支持**：确实在**另一个容器**（`effect_01.gpk`，不是 `effect_cache.gpk`/`textures.gpk`）；确实在**另一种格式**（`.spr` 明文本描述符 + 匿名 BC7 DDS，不是 `.tga`）。
- **反对**：`textures.gpk`/`textures_bw.gpk` 已用 417 basename × 33,360 候选排除；但 35 个 `gres` 下异型 `.gpk` **未扫**。
- **结论**：**格式维度已确认**（`.spr` + BC7 DDS）；**容器维度在 `effect_01.gpk` 已确认**，但 `gres` 那 35 个异型包是**未决口**。

---

## 9. unresolved（未决项 + 试过的入口清单）

### 9.1 `BC7_DECODER_MISSING` —— 最高优先级
- **未决**：把 `effect_01.gpk` 里的 BC7 DDS 解成 PNG，做像素级确认（是否径向渐变 / 遮罩）。
- **为什么重要**：这是「匿名 DDS ↔ 声明 `.tga`」唯一剩下的绑定手段。
- **试过的入口**：
  - `texture2ddecoder` → 在 `Python310` / `Python311` / `Python312` / `01拆包器本体\.buildenv` 四个解释器 `importlib.find_spec` **全部 False**
  - `Pillow 11.1.0`（py3.10）→ 不认 BC7/DX10
  - 自建 BC1/BC3 解码器（已逐像素验证 max-abs-diff 0）→ **按设计正确拒绝** `dxgiFormat 98`
  - `cryptography` → 无（故 AES 自建，已自证 + 第三方复核）
- **解锁条件**：装 `texture2ddecoder`（或 `texconv`/DirectXTex），或人工在 DCC 里看那 3 个 `.dds`。

### 9.2 `GPK_HEADER_VARIANTS`
- **未决**：`E:\mrzh\Documents\gres` 下 **35 个 `.gpk`** 未索引（magic 非 `HPGF`，见 `RPGF`/`tPGF`/`gPGF`）。
- **试过**：用已验证的容器密钥解前 64 B，magic 判定失败即跳过。
- **风险**：特效贴图**有可能**也在这 35 个包里。**未查。**

### 9.3 `WHY_TGA_IS_DECLARED`
- **未决**：SFX 为何声明 `.tga` 而引擎实际加载 `.spr`。
- **已被否证的假说**：「`.tga` 被改名成 `.spr`」—— §4.5 用原始文本证明命中的 `.spr` 本来就是声明为 `.spr` 的。
- **现行假说（未证）**：`.tga` 是美术期/历史名或另一套渲染路径的引用，运行时由引擎统一映射；**未读引擎代码路径，不作结论**。

### 9.4 `NAME_ENUMERATION_LIMIT`（方法论边界，必须写清）
- 容器只存路径哈希，**无法枚举名字**，只能按候选名试。
- 本轮对 366 个声明名试了：13 类通用变体 + 10,210 个 basename×子目录 + 100,080 个具名容器候选，**累计 > 104,000 条**。
- **证据边界**：这证明「**用我们构造得出的任何名字都到不了**」，**不**等于「用穷举证明文件不存在」。

### 9.5 `SPR_ENTRY_IS_DESCRIPTOR`
- **未决**：`.spr` 描述符自己可达，但它引用的**位图本体**是否另有一条独立哈希条目，未确定。
- **已知**：描述符内部写的 `.tga`（如 `glow03.tga`）**同样不在容器里** → 描述符里的 `.tga` 只是逻辑名。

### 9.6 其它入口（试过、无果，供后续避免重复劳动）
- `.pak` / `.dat` / `.bin` → 已确认为 Chromium/CEF 运行时（`cef.pak`、`icudtl.dat`、v8 快照），非资源容器。**未再查。**
- `shader\*.fx`（5 条）→ 0 命中；着色器可能编在 exe 或独立格式里，**未查**。
- 扩展名变体：`.tga/.dds/.png/.spr/.spd/.jpg/.bmp/.ktx/.pvr/.astc/.hdr/.exr` —— 除前 5 个外均为形式化枚举。
- 前缀变体：`res\`、`assets\`、`common\`、`common\res\`、`assets\common\`、`res\assets\`、`assets\res\`、`textures\`、`res\textures\` —— 全 0。
- 目录变体：去一层 / 去两层 / 正斜杠 / 全小写 / basename 全大写 / 去尾部 `_d` / 去扩展名 —— 全 0（`effect\mesh` 与 `.sfx` 上同批变体大量命中，构成对照）。

### 9.7 `ROW_N_MINUS_1`（第三方复核补充，未独立验证）
- 第三方复核报告：`effect_01.gpk` **最后一行（index 212151）不是有效条目**（其 flag 字段为 `2578442032`，是全表 flag 直方图中唯一的离群点）。
- **未独立验证**。若下游有代码 `for i in range(N)`，会命中此行。**已记录，未下结论。**

---

## 10. 产物与命令

### 10.1 本轮交付（仅这两份写入项目）
| 文件 | 说明 |
|---|---|
| `03拆包产物\_target_1110171\FX_FILE_AUDIT_report.md` | 本文件 |
| `03拆包产物\_target_1110171\FX_FILE_AUDIT.json` | 逐条机读（1,633 条资源 + 矩阵 + 判定 + unresolved） |

### 10.2 脚本（全在 `%TEMP%\fx_audit\`，未污染项目）
| 脚本 | 作用 |
|---|---|
| `cng_aes.py` | Windows CNG AES-128-ECB 解密（约 1 GB/s），含 FIPS-197 自检 |
| `fx_aes.py` | 纯 Python AES-128-ECB（备用 + 对拍） |
| `aes_crosscheck.py` | FIPS-197 + canonical 对拍 + 90 gpk / 158 npk 语义验证 |
| `fx_index.py` | 91 gpk + 158 npk + 64 fpk 索引（17 s） |
| `validate_pipeline.py` | 哈希映射实证 + 载荷解码验证 |
| `fx_audit.py` | A1 枚举 / A2 抽取解析 / A3 逐条解析 / B4 内容扫描 |
| `spr_probe.py`、`spr_decode.py`、`spr_matrix.py`、`spr_vs_tga.py`、`final_probe.py` | `.spr` 描述符解码、跨扩展名扫描、basename 普查、具名容器点名 |

### 10.3 一键复跑
```powershell
cd $env:TEMP\fx_audit
py -3.10 aes_crosscheck.py     # 先证明 AES 是对的
py -3.10 fx_index.py           # 建索引（17 s）
py -3.10 validate_pipeline.py  # 验证哈希映射与载荷解码
py -3.10 fx_audit.py           # 主审计
py -3.10 final_probe.py        # .spr / 具名容器终审
```

---

## 11. 变更日志
- 2026-09-18 23:22 任务预置骨架落盘（含 3 条 `.spr` 已知命中）。
- 2026-09-18 23:2x 自建 AES（纯 Python + CNG），4 条证据自证；建 5,318,147 键索引（17 s）。
- 2026-09-18 23:3x A1 枚举 3,230 候选 → 164 命中；A2 抽 1,633 条声明路径。
- 2026-09-18 23:4x A3 逐条解析：`.spr` 52/52、`.tga` 1/366；解出 `.spr` 明文本描述符格式。
- 2026-09-18 23:5x B4 内容扫描（`effect_01.gpk` 1,070 张 BC7 DDS）；B6 三容器 100,080 候选 0 命中。
- 2026-09-18 23:5x B5 读到既有 provenance，确认当时走「内容路线」；自建 BC1/BC3 解码器（max-abs-diff 0，但目标为 BC7 不可用）。
- 2026-09-18 23:5x **第三方独立复核 AES 通过**（HPGF / N=212152 / 六行逐字段一致 / zstd 精确膨胀 50117 B / sha256 相同）。
- 2026-09-19 00:0x **本文件替换骨架为终稿**；§4.5 用原始字节纠正并行草稿两条误判；补 §9.7。

---

# 附录 A（第二路并行代理追加，2026-09-19 00:0x）

> **性质声明**：附录 A 由**第二路并行代理**（任务书要求"彻查 `effect\textures\glow|alpha|debris\*.tga`"）追加。
> 正文 §0–§11 为该代理的终稿，**未被改动**。本附录只做三件事：**独立复现验证**、**自我更正**、**补一项正文未做的超大规模普查**。
> 追加方式为 `edit` 尾部追加，未重写正文。

## A.0 事故与修复（必须记录）

1. **事故**：本代理在未知正文作者已写入的情况下，以 `write` 覆盖了 `FX_FILE_AUDIT.json`（23:31:10，1,206,335 B）。
2. **修复**：定位到正文作者的脚本目录 `%TEMP%\fx_audit\`（含 `make_deliverables.py` + `patch_json.py`），按其原设计**顺序重跑二者**恢复：
   ```
   cd $env:TEMP\fx_audit
   <Python311>\python.exe make_deliverables.py   # -> 1,470,454 B, sha16 30bb4550c2e57f70
   <Python311>\python.exe patch_json.py          # -> 1,477,803 B, sha16 d46092abefdc8c2d  (unresolved = 8)
   ```
   恢复后的 JSON **比被覆盖前更大**（1,477,803 B > 1,348,536 B），因为 `make_deliverables.py` 会重算 `A1/A2/A3` 而未打补丁；`patch_json.py` 重新补齐 `spr_axis_correction` / `third_party_verification` / `npk_enumeration` / `row_n_minus_1_flag` / `transcribed_not_verified` 并追加 3 条 unresolved。
   **正文 `.md` 未被覆盖**（本代理发现后改为追加）。
3. **结论**：正文结构化数据已恢复；`unresolved` 8 条与正文 §9 的 7 条 + `EFFECT02_VEINS_TGA` 一致。

## A.1 自我更正（本代理草稿的两条误判 —— 已用原始字节独立确认正文 §4.5 正确）

| # | 本代理草稿的错误主张 | 原始字节复核结果 | 判定 |
|---|---|---|---|
| 1 | "sfx 声明 `effect\textures\glow\tex_glow_tp07_02.tga`，实存 `.spr` ⇒ `.tga`→`.spr` 改名" | `fx_skin_1003_010_zs.sfx`（row **37320**，126,753 B，sha16 `083bd15770f26221`）中 `tex_glow_tp07_02` 的**唯一**出现形式是 `tex_glow_tp07_02.spr"`。同文件另有**6 个完全不同的** `.tga` 声明（`glow40_tp30` / `glow_gyun_01_smg` / `glow_tp17_04` / `star_xing_02_tp165` / `tex_glow_ray_tp60_01` / `caihong_06_jh_djs`）。本代理原先把**同文件内的 `.spr` 声明与另一批 `.tga` 声明缝合**成了因果链 | **草稿错误，正文正确** |
| 2 | "`glow13.spr` 佐证 `.tga`→`.spr` 改名" | `glow13` 仅出现于 `fx_skin_1003_010_dm.sfx`（row 37297），形式为 `glow13.spr"` | **草稿错误，正文正确** |
| 3 | ".npk 实测只有 4 个" | `Get-ChildItem E:\mrzh -Recurse -Filter *.npk` = **158**（3+3+1+1+10+62+1+5+6+44+22，11 个目录）。本代理原命令只 glob 了 `res\*.npk` / `Documents\gres\*.npk` / `mrzh\*.npk` **三个顶层**，漏掉了 `res\model`(62)、`res\scene_bw\bigworld`(44)、`res\ui`(22) 等子目录 | **草稿错误，正文 §1.1 正确** |

> 本代理**不删除**上述错误主张，因为任务书要求"走不通的路要写下试过什么"。记录于此即为留痕。

## A.2 独立复现验证（正文未改动，此处只做交叉印证）

以下各项由本代理**用独立脚本与独立索引**复算，结论与正文一致：

| 项 | 正文值 | 本代理独立复算 | 一致 |
|---|---|---|---|
| `effect_01.gpk` 行数 | 212,152 | 212,152（行号 0–212151 **完全连续无缺口**） | ✅ |
| 6 条 sfx 的 sha16 | §1.4 表 | 逐条一致，含 `59115620b779a5e8`（row 37322） | ✅ |
| `.spr` 52/52 精确命中 | §4.3 | `glow03.spr`→206926、`glow02.spr`→206924、`glow13.spr`→206940、`tex_glow_tp07_02.spr`→207414、`lightning07_cs.spr`→207659、`tex_smoke_yan_tp71.spr`→208633 **逐个直查命中** | ✅ |
| 唯一命中 `.tga` | `veins\tex_xingdian_02_uvva.tga` row **2140** | 直查命中 `effect_02.gpk` row 2140 | ✅ |
| `.dds` 存在且量大 | 7,501（转引 manifest） | **独立核实**：`effect_01\manifest.json` sha16 `26F8F9FC507F2BBD`，212,151 条，ext 直方图 `.c159` 111,572 / `.mesh` 52,990 / `.bin` 39,535 / **`.dds` 7,501** / `.rgis` 553 **逐项相符** → 正文 §4.5 中标注"转引，未复核"的数字**现已复核通过** | ✅ |
| `effect_cache.gpk` 0 贴图 | 99,801 行 0 张 | `effect_cache\manifest.json` sha16 `EB7BE28429066437`，**99,800 条全 `.bin`** | ✅ |
| TGA 头判定 | image type 2 | 实抽 `star_01_wfj_djs_uvva.tga`(207274)、`tex_xingdian_uvva.tga`(2141) 头均为 `00 00 02 …` = **未压缩真彩 TGA**（注意：**第 3 字节**才是 image type） | ✅ |
| `effect\textures\glow\glow03.tga` 是否在包内 | 不在（§9.5） | **直查 MISS**；而其同 stem `glow03.spr` row 206926 HIT，且该 `.spr` 内部 9 行全部自引用 `glow03.tga` | ✅ |

## A.3 新增：4,186 个 `effect\textures\*.tga` 名超大规模普查（正文未做）

**方法（独立于正文）**：不局限于 sfx 声明，而是从 `E:\la拆包项目` **全工作区**（`.json/.txt/.md/.py/.csv/.xml/.sfx/.cfg/.ini`）正则抽取**全部** `effect\textures\*` 明文路径名，去重后逐一对**自建全量 gpk 索引**（91 容器 / 2,137,892 行 / 唯一哈希键 2,107,832，3.5 s 建成）做五形态直查。

**样本远大于正文 §4 的 366 个声明名 —— 这是本附录的主要增量。**

| 类别 | 判定条件 | 数量 | 占比 |
|---|---|---|---|
| `TGA_VERBATIM` | `.tga` 本身在包内 | **29** | **0.69%** |
| `TGA_VIA_SPR` | `.tga` 不在，但**同 stem `.spr`** 在 | **48** | **1.15%** |
| `TGA_ABSENT` | 两者皆无 | **4,109** | **98.16%** |
| 合计 | | **4,186** | 100% |

**决定性副产物**：**29 个 `TGA_VERBATIM` 全部（29/29）带 `_uvva` 后缀**，非 `_uvva` 的为 **0**。
⇒ 把正文 §4.2 的"唯一命中"从**孤例**升级为**族规律**：`effect\textures\*.tga` 在客户端**唯一真实存在的命名族是 `*_uvva.tga`**；glow/alpha/debris 的常规名**不在该族内**。

**按子目录（任务书点名的三类）**：

| 子目录 | 总数 | `TGA_VERBATIM` | `TGA_VIA_SPR` | `TGA_ABSENT` |
|---|---|---|---|---|
| `glow` | 346 | 3（全 `_uvva`） | 2 | **341** |
| `alpha` | 962 | 1（`_uvva`） | **0** | **961** |
| `debris` | 215 | **0** | 15 | **200** |

> `alpha` 是**最干净的反例**：962 个名字里 `.spr` 替身 **0** 个 —— "`.tga` 都改成了 `.spr`"这一说法在 alpha 类上**完全不成立**；alpha 贴图在任何已索引容器中均无对应条目。

**对正文判定的影响**：
- **加强 ①**（"发布名与声明名不同轴"）：`.spr` 替身现象在 15/215 的 debris、2/346 的 glow 上成立。
- **加强 ②**（"真的没发布"）：98.16% 的名字**连替身都没有**，且 alpha 类为 0 —— 说明"换成 `.spr`"**不能**解释绝大多数目标贴图。
- **仍不改变** 正文 §8 的三选一结论与 §9 的未决项；本附录只是把"366 条"扩到"4,186 条"后**同一方向**。

## A.4 本附录仍未解决的

- 4,109 个 `TGA_ABSENT`（含 alpha 961 / glow 341 / debris 200）**无法区分**：引擎运行时生成 / 未随包发布 / 在未索引容器（正文已列的 35 个 `gres` 异型 `.gpk`、64 个 `.fpk`）。
- `.fpk` 的 `path→fid` 规则**本代理未破解**，故 64 个 `.fpk` 内的贴图仍无法按名查询（正文用预建 `fpk_fid_index.json` 的 2,069,650 键另有覆盖，本代理未复用）。
- 本附录普查**只覆盖名字**，未做内容级（BC7 解码）绑定 —— 与正文 §9.1 同一堵墙。

## A.5 本附录脚本（全在 `%TEMP%\fxq\`，未污染项目）

| 脚本 | 作用 |
|---|---|
| `build_index.py` | 91 gpk + 4 npk 索引（3.5 s）→ `index.jsonl` |
| `extract_sfx.py` / `parse_sfx2.py` | 提取 6 sfx + 3 spr；抽 134 条声明路径并解析 |
| `broad_probe.py` | 20 stem × 6 前缀 × 12 子目录 × 8 扩展 × 3 根 = **110,448** 候选 |
| `pool.py` / `final_classify.py` | 4,186 名普查 + 三类判定 |
| `verify_dispute.py` | §A.1 的原始字节复核（row 37320 / 37297） |
| `audit_own_class.py` | 对 §A.3 分类做**无回退链**的直查复验 |
| `manifest_ext_census.py` | 5 个既有 manifest 的 ext 直方图复核 |
