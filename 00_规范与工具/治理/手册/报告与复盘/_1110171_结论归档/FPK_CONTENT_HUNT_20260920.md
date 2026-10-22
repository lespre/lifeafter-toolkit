# FPK_CONTENT_HUNT_20260920 — fpk/gpk **载荷 md5** 全量比对清单 checksum（task-86）

- 任务：**task-86**（env-auditor）。源包只读；只写本报告 + `.json` + `fpk_hits/`。
- 打法（Lead 读清格式后的正确方向）：**把每个条目的载荷解出来算 `md5`，比对清单 checksum**（checksum = md5(原始资产字节)，已端到端证实）。
- 目标集合：`E:\mrzh\res.npk` entry 8858 清单，**`TS_manifest_full` 397,105 个唯一 checksum**；严格正则重解 **532,462 行 → 399,037**，本轮 NPK 段升级为两路并集 **399,108**（宽松口径上界 **400,070**），见 2A.4。
- **两个可复用产出**（Lead 指定补录）：**§1A** `star_xing_02_tp165.tga` 源级直证（三容器互证）｜**§2A** 载荷 md5 方法学（含 **gres 每块 base** 修正）
- 写盘范围核对：只写了 `FPK_CONTENT_HUNT_20260920.md/.json` 与 `fpk_hits/`；**未改任何 wiki 文件**（`viewer.js`/adapter/board/effects.json 等本轮未触碰）。

---

## 0. 直接回答：**那 29 条源资产在不在本机？**

> ### 只找到 **1 条**；**其余 28 条不在本机任何容器里**
> - ✅ **找到**：**`effect/textures/glow/star_xing_02_tp165.tga`** —— 在 **3 个容器**里都有同一份载荷：
>   | 容器 | 位置 | 字节 | md5 | sha16 |
>   |---|---|---|---|---|
>   | `E:\mrzh\res\048.fpk` | entry **191518** | 262,188 | `f1524e26d09832be95734d4527208051` | `be21a24a68e18a91` |
>   | `effect_01.gpk` | row **207282** | 262,188 | 同上 | 同上 |
>   | `E:\LifeAfter\Documents\gres\0052.gpk` | block 23 / row **26601** | 262,188 | 同上 | 同上 |
>   （TGA type-2，256×256，alpha=1；已落盘 `fpk_hits/star_xing_02_tp165__f1524e26d09832be.tga` + PNG 预览）
> - ❌ **未找到（28 条）**：`glow_01`、`dian_12`、`glow_16_yh_djs`、`glow25`、`glow_04_tp29`、`glow_14_cs`、`glow01_yc`、`tex_glow_*`（7 条）、`xing_01_yh_djs`、`lighting_01_rzx_djs`、`lightning_01_ycy_djs`、`tex_lightning_shandian_tp52`、`guangshu01_cjf_djs`、`keji_02_wh_djs`、`tex_trail_*`（3 条）、`trail_11_lmq_djs`、`noise_04_tp05`、`tex_noise_y`、`v_veins_tp116_08`、`alpha_01_tp52_01`、`tex_alpha_mask_tp60_04`、`tex_alpha_tp104_04`、`tex_crack_tp71_05`、`tex_crack_02_yx_djs`（后两条清单本身就无此项）……
>   在 **224 个容器**（73 fpk + 136 gpk〔内含 80 gres〕+ **15 NPK**）的载荷 md5 扫描中**一次都没出现**。
> - 🆕 **NPK 段已补扫（2026-09-20 续，见 `NPK_CONTENT_HUNT_20260920.md`）**：15 个 NPK / 817,281 条目 / 15.43 GB / **失败 0** / 46,449 命中，其中 `effect/` 前缀 **0**、声明名 **0** ⇒ **四族至此全部扫完，那 28 条在本机四族容器内确实不存在**。
> - 🆕 **健全性检查**：30 个唯一声明 checksum 在 399,037 / 399,108 / 400,070 三套目标集里**都命中 30/30** ⇒ "未出现"是有效负面证据（`%TEMP%\NPK_coverage_check.py`）。
> - ⚠ **不可核的 8 条**（集 A 口径）：4~5 个 `.spr` 帧表 + `caihong_06_jh_djs.tga`、`tex_glow_qirishijie_guangyun_hgz03_03.tga` 在清单里**没有同名 basename** ⇒ 内容轴无法核验（写"不可核"，不写"不存在"）。

**扫描规模（可复现）**

| 段 | 容器 | 条目/行 | 解压成功 | 失败 | 输出 | 命中 |
|---|---|---|---|---|---|---|
| fpk（LA 9 + mrzh 64） | 73 | 2,131,168 | 1,844,927 | 43,514 | **192.5 GB** | **52,934** |
| gpk 单块（stage A：dec 精确尺寸集） | 136 | 7,606,686 | 6,001 | 13,434 | 0.1 GB | 0 |
| gpk 单块（stage B：dec ∈[1 KB,1.1 MB]） | 136 | 7,606,686 | 1,957,882 | 4,014,729 ⚠ | 67.5 GB | **29** |
| **gres 多块（修正版）** | 80 | 5,503,767 | **4,425,837** | **7** ✅ | 171.4 GB | **168** |
| **NPK（本轮补扫，无预筛）** | **15** | **817,281** | **817,281** | **0** ✅ | **15.43 GB** | **46,449**（effect 0 / 声明 0） |

⚠ **首版有个方法学 bug（已修，如实登记）**：stage B 对 **gres 多块容器只用了 `bases[0]`**，导致属第 2+ 块的行全部解压失败（4,014,729 行）。修正版**按块累积 row 区间、每行取自己块的 base** ⇒ 失败骤降到 **7 行**。**那 29 条缺的贴图不是被这个 bug 掩盖的**：修正版把 gres 的 4.42M 行真正测完了，仍然没有它们。

---

## 1. 命中的两类（Lead 指定重点）

### ① `effect/` 前缀（清单 7,505 条中的一部分）
在 fpk/gpk/gres 里共命中 **effect 家族源资产 79 条唯一名**（fpk 21 + gpk effect_01/02 的 28 + gres 的 30）。样例（**这些是"源 .tga 未转码"的真身**）：

| 清单名 | 容器 · 位置 | 字节 |
|---|---|---|
| `effect/textures/glow/star_xing_02_tp165.tga` | 048.fpk e191518 / effect_01.gpk r207282 / 0052.gpk b23 r26601 | 262,188 |
| `effect/textures/trail/trail_05_yh_djs.tga` | `effect_02.gpk` **row 1219** | 262,188 |
| `effect/textures/trail/trail_04_yh_djs.tga` | effect_02.gpk r1212 / 0045.gpk b77 r93756 | 262,188 |
| `effect/textures/veins/veins_03_yy_djs.tga` | effect_01.gpk r205783 / 0032.gpk b57 r58709 | 262,188 |
| `effect/textures/alpha/alpha_39_zy_djs.tga` | effect_01.gpk r204425 / 0032.gpk b54 r55086 | 65,580 |
| `effect/textures/glow/star_01_wfj_djs.tga` | effect_01.gpk r207274 / 0062.gpk / 0048.gpk | 262,188 |
| `effect/textures/special/color_all_01.tga` | effect_01.gpk r208986 / 0032.gpk b47 r48042 | 1,048,620 |
| …（完整 79 条见 JSON `hits.gpk` / `hits.gres`） | | |

**顺带一个对"按名找图"很重要的现象**：`effect_02.gpk` row 1219 的载荷 md5 = `e33c73a6a1f4…`，清单名是 **`trail_05_yh_djs.tga`**，而我在 task-83 从同一行导出的文件名来自加载日志 `trail_05_yh_djs_uvva.tga` ⇒ **同一份内容、两个名字**（"一资产多名"确实存在）。

### ② 两皮肤声明名（34 条 → 清单有 checksum 的 32 条）
**命中 1 条**（上表 `star_xing_02_tp165.tga`，属 1110171 `node[24] H_星点粒子_3`）；其余 31 条未在容器载荷中出现。

---

## 1A. `star_xing_02_tp165.tga` —— **源级直证（三容器互证）**〔本轮补录，Lead 指定〕

**结论**：1110171 `node[24] H_星点粒子_3` 声明的 `star_xing_02_tp165.tga` = 清单 `effect/textures/glow/star_xing_02_tp165.tga`（checksum `f1524e26d09832be95734d4527208051`）；其**原始资产字节**在本机 **3 个互不相干的容器**里各存一份，三份**逐位相同**（同一 md5 / 同一 sha256 前 16）。

**本轮重新独立解了一遍（不是复读旧 JSON）** —— `%TEMP%\NPK_evi_3cont.py` → `NPK_evi_3cont.json`：

| # | 容器（族） | 定位 | 绝对偏移 | 压缩 | 载荷 |
|---|---|---|---|---|---|
| 1 | `E:\mrzh\res\048.fpk`（fpk，1,084,109,184 B / 215,598 条目） | entry **191518**（条目表 @1,073,760,480） | **834,767,784** | clen 1,875 → olen 262,188（zstd） | 262,188 B，md5 `f1524e26…8051`，sha16 `be21a24a68e18a91` |
| 2 | `E:\mrzh\res\effect_01.gpk`（gpk 单块，700,157,292 B / 212,151 行） | block 0（base 16）row **207282** | 16+585,858,584+20 = **585,858,620** | comp 1,875 → dec 262,188，flag **12** | 同上（逐位相同） |
| 3 | `E:\LifeAfter\Documents\gres\0052.gpk`（gres 多块，2,147,257,346 B / 29 块 / 30,280 行） | block **23**（base 401,855,328）row **26601** | 401,855,328+893,984+20 = **402,749,332** | comp 1,875 → dec 262,188，flag **12** | 同上（逐位相同） |

`all_match = true`（3/3）、`identical_sha16 = true`。

**证据链 4 环（每环可单独复核）**
1. **容器行 → 载荷**：三条读取路径互不相同 —— fpk 走「AES 解 48 B 头 → 条目表 48 B/条 → zstd」；gpk 走「块 base + row.off + 20」；gres 走「**该行自己块的 base** + row.off + 20」（三种表结构、三个物理文件）。
2. **载荷 md5 == 清单 checksum**：`f1524e26d09832be95734d4527208051` 与清单该行 checksum 逐位相等（checksum = md5(原始资产字节)，已端到端证实）。
3. **头部自证（不靠名字）**：载荷前 4 B = `00 00 02 00` ⇒ 未压缩 TGA type-**2**，宽 **256** / 高 **256** / **32 bpp** / **alpha 位 8** ⇒ 与清单该行 `img_size [256,256]`、`has_alpha 1` 独立吻合（清单是"名字说的"，头部是"字节说的"）。
4. **三容器独立**：三条路径解出同一 md5、同一 sha256 前 16、同一 262,188 B ⇒ 不是某个容器的解析巧合。

**落盘件（SHA256 已复核，可直接使用）**

| 文件（`fpk_hits/`） | 字节 | md5 | sha16 | 来历 |
|---|---|---|---|---|
| `star_xing_02_tp165__f1524e26d09832be.tga` | 262,188 | `f1524e26…8051` | `be21a24a68e18a91` | fpk entry 191518 解出 |
| `gpk__star_xing_02_tp165.tga__f1524e26d09832be.bin` | 262,188 | 同上 | 同上 | gpk row 207282 解出（逐位相同） |
| `gres__star_xing_02_tp165.tga__f1524e26d09832be.bin` | 262,188 | 同上 | 同上 | gres block23/row26601 解出（逐位相同） |
| `star_xing_02_tp165__f1524e26d09832be.png` | 3,225 | `fab79934…` | `8864515a8e5df3f6` | **派生** 256×256 预览，**不参与绑定/不作为证据** |

**两处口径修正（本轮实测，供后续复用）**
- **gres 的 0052.gpk 只有一个根**：`E:\LifeAfter\Documents\gres\0052.gpk`（`E:\mrzh\Documents\gres\` 下**无**此文件）；row 26601 属 **block 23**，其 block base = 401,855,328（**不是 0**）——用 base=0 去读必然读错。
- **该行 flag 12 的 zstd 帧没有 content size**：`npk_reader.unpack_entry(raw, dec, flag)` 会抛 `ZstdError: error determining content size from frame header`；必须用 `ZstdDecompressor().decompress(raw, max_output_size=dec*4+4096)`（FPK/GPK 两段历来就是这么做的）。**照抄 `unpack_entry` 的定长口径会漏掉这类行**。

**绑定状态**：Lead 已把它绑到 1110171 `node[24] H_星点粒子_3`（`verified_by_payload_md5_source_asset`）。与 task-85 的「候选回撤」不冲突：task-85 撤的是**按名/按尺寸猜**的候选，这条是**源资产内容直证**。

---

## 2. 逐段台账（可复现）

### 2.1 fpk 73 个（LA 9 = 正式服 UI 包 + mrzh 64）
**LA 9 个逐文件命中与我上一轮一致，也与 Lead 的实测完全一致**：001:1140 / 015:8382 / 016:2850 / 017:7954 / 018:6920 / 019:6843 / 020:5303 / 021:4636 / 022:7865 = **51,893**。
mrzh 64 个合计 **1,041**，其中 `048.fpk` 24 条（22 条 `effect/`）。
**家族分布**：`ui` 52,168 / `l10n` 729 / **`effect` 22** / `character` 12 / `textures`·`scene`·`common` 各 1。

### 2.2 gpk 单块（`E:\mrzh\res\*.gpk` 55 + `res.gpk` + `effect_01/02.gpk` + `effect_cache.gpk`）
- stage A（dec 精确落"目标尺寸典型体积"集合）→ **0 命中**；
- stage B（dec ∈[1 KB,1.1 MB]）→ **29 命中**：`effect_01.gpk` **7**（含声明名 1）、`effect_02.gpk` **22**；
- 关键容器全部 0 失败：`res.gpk` 16,711 行、`building_*`/`character_*`/`scene_*`/`ui_*`/`model_*`/`weapon`/`utility` 合计 1.9M 行、`effect_cache.gpk` 99,790 行（全 DXBC，0 命中）。

### 2.3 gres 多块（修正版，80 个：LA 45 + mrzh 35）
- 逐容器"块数 / 行数 / 预筛 / 解压 / 失败 / 命中"全表见 JSON `gress_files_fixed`；
- 命中集中：`0032.gpk` 29、`0039.gpk` 47、`0045.gpk` 21（**含 `common/env_map/*.dds` 一整批 IBL 环境图**：`car_studio01.dds`、`qiangpi.dds`…）、`0052.gpk` 3（含声明名 1）、`0053/0042/0062` 各 4、`0003.gpk` 44（UI PNG）等；
- 失败仅 7 行（修正前 4,014,729）。

### 2.4 NPK（🆕 本轮补扫，15 个，**无预筛**）
- 详见 **`NPK_CONTENT_HUNT_20260920.md/.json`** + `npk_hits/`（唯一文件 25,296 个 / 1.97 GB，25,976 次写入含 648 个同名同 md5 覆盖）。
- **15 个容器**（`E:\mrzh\res.npk`、`E:\mrzh\res\ui.npk`、7 个 `E:\mrzh` script 包、5 个 `E:\LifeAfter` 包）；**817,281 条目全部解出，失败 0**，输出 15.43 GB，**46,449 命中**（唯一 md5 44,365）。
- 家族：`ui` 45,799 / `l10n` 631 / `common_preview` 11 / `scene` 4 / `common` 2 / `shader` 2；**`effect/` 0、声明名 0**。
- 11 个 `script*.npk` 全 0 命中（脚本包不含清单资产，实测非假设）。
- ⚡ **性能修正**：`npk_reader.lz4_block` 是纯 Python（3+3.7 GB 会跑成小时级）；改用原生 `lz4.block.decompress`，**40/40 逐位等价 + 148× 加速**，全量 15 包 **123 秒**完成。

---

## 2A. 方法学（本轮最重要的可复用产出）：**载荷 md5** 打法 ＋ gres 每块 base 修正

> 一句话：**不要问容器"这条叫什么"，要问容器"这条解出来是什么"** —— 把条目载荷解出来算 `md5`，与清单 checksum 求交。

### 2A.1 为什么只剩这条路（前三轴都断了）

| 轴 | 状态 | 证据 |
|---|---|---|
| 名字 → 容器条目（按名查 fid） | ✗ | GPK/NPK 的 fid 不是路径哈希：20,000 条清单名 0 命中；本轮**阳性对照**（`NPK_fid_control.py`）拿 `E:\mrzh\script.npk` 里 **65,995 条真有逻辑路径**（`parse_logical_path` 已能还原成 `com\cdata\xxx.py`）的条目去核 `npk_reader.path_id`（双 murmur3 0x77777777/0x66666666），**0/65,995 对上**；再对 8 组真值对穷举 16,560 个候选哈希（murmur3×10 seed / crc32 / adler32 / fnv1a32/64 / 9 种字符串变换 × 4 种编码）仍 0 命中 ⇒ **该 docstring 声称的"已验证"不成立于本机这一代 NPK**（如实登记为未决，`NPK_fid_crack.json`） |
| 名字 → 索引（`.idx`/`.wpk`） | ✗ | idx 键 = **md5(DDS 载荷)**（1,031/1,031）确证，但 idx/wpk **不存名字**，无法反向给出路径 |
| 名字 → 尺寸 | ✗（只能排除） | 128² 池 1,565 / 256² 池 3,317：尺寸能**排掉**不可能项，不能**认定** |
| **内容 → 名字（载荷 md5）** | ✅ | 命中即清单该 checksum 对应的路径；`checksum = md5(原始资产字节)` 已端到端证实（`Documents\res\ui\<checksum>` 的 `1DPW` 块解密载荷 md5 == 文件名 == 清单 checksum） |

### 2A.2 四族容器的"取载荷"口径（照抄即可，均已在源包上实测）

| 族 | 头部 / 表 | 载荷定位 | 解压 |
|---|---|---|---|
| **fpk**（NXPK） | `head = AES_ECB(前 48 B)`；`head[8:12]=='NXPK'`、`entry_off=u32@16`、`entry_n=u32@20`；条目表 AES 加密、**48 B/条**：`off=u32@8`、`clen=u32@12`、`olen=u32@16` | `d[off : off+clen]` | `clen==olen` ⇒ **原样拷**；`clen!=olen` ⇒ **zstd**（`max_output_size=max(olen,clen)*4+4096`） |
| **gpk 单块**（HPGF） | 16 B 文件头（`[4]=block_count^0x46475049`、`[8]=2`、`[12]=block_count`；`[20]` 存的是 count**+1**，56/56 实测）；块 base **B**：`B+4=entry_count+1`、`B+8=block_size`、`B+48` 起 `entry_count×32 B` AES 表，行 `<8I>=(off,comp,dec,c1,c2,flag,hash_lo,hash_hi)` | `abs = B + off + 20`，读 `comp` B | `flag==12` ⇒ zstd；`off==1` = 载荷去重到别卷（跳过并计数） |
| **gres 多块** | 同上块链，但**多块**，每块独立 AES + 独立 32 B 表 | **`abs = 该行自己块的 base + off + 20`** ⚠ | 同上；⚠ 帧头无 content size 时**不能**用定长 decompress |
| **NPK** | `AES_ECB(32 B)` ⇒ `(_u, magic=0x4B50584E, ver, table_off, entry_count)`；表 `entry_count×48 B` AES，行 `<QIIIIIi> = (fid, off, ps, ds, c1, c2, flag)` | `[off, off+ps)` | `unpack_entry(raw, ds, flag)`：flag **2**=lz4（**用原生 `lz4.block`，见 2A.7**）、**12**=zstd（`max_output_size`）、**0**=AES 后 zlib（若 `u64@0==1` 且 `[16:18]` 是 zlib 头）否则原样 |

### 2A.3 ⚠ gres 多块 bug（本轮修正，任何复用者必读）
- **错法**：只取 `bases[0]` 当所有行的 base ⇒ 属第 2+ 块的行**全部解压失败**：stage B **4,014,729 行失败**（例：`0022.gpk` 预筛 134,164 → 失败 117,892）。
- **正法**：先按块累积 row 区间（`block['base']` 与 `block['entries']` 逐块累加），**每行取自己那块的 base** ⇒ 失败骤降到 **7 行**（4,425,837/4,425,844 解出，171.4 GB，168 命中）。
- **代价**：修正前，gres 第 2+ 块里的源资产对"载荷 md5"**完全不可见**，会得出"源资产不存在"的**假结论**。这是本轮唯一的方法学级修正。
- **旁证（1A 表 #3）**：`0052.gpk` row 26601 的 base 是 **401,855,328**（block 23），不是 0；且该行 zstd 帧**无 content size**，定长 `decompress` 会抛 `error determining content size from frame header`，必须给 `max_output_size`。

### 2A.4 目标集合（清单口径）
- 来源：`E:\mrzh\res.npk` entry **8858**（`ds=80,369,252`）解出的文本行 `路径 {"checksum": md5, "has_alpha": N, "img_size": [w,h]}`。
- 本轮改为**两路取并集**（`NPK_hunt.py`）：自解 **532,462 行 → 399,037 唯一 checksum**（严格口径）；∪ `%TEMP%\TS_manifest_full.json`（529,370 条）→ **399,108 唯一**。宽松口径（只要 path+checksum）可达 **400,070**。
- 🆕 **健全性检查（32 皮肤批量必须先做）**：任何"未命中"结论都要先证"该 checksum 确实在本次目标集里"。本轮 30 个唯一声明 checksum 在 **399,037 / 399,108 / 400,070 三套里都 30/30 命中** ⇒ 四族"未出现"有效（`NPK_coverage_check.py`）。
- 清单字段可直接做**独立互证**：`img_size`/`has_alpha` 与载荷头部（如 TGA `00 00 02 00` + 宽高 + alpha 位）对拍 —— 名字是清单说的、头部是字节说的，两者独立吻合才算"源级"。

### 2A.5 什么才算"命中证据"（落盘纪律）
1. **只认"原始资产字节"的 md5**：预览 PNG/JPG、转码后的 DDS、wiki 派生图一律**不算**（例：star_xing 的 PNG 预览 md5 `fab79934…` ≠ 清单 checksum，故 1A 里明确标注"派生、不参与绑定"）。
2. 命中即落盘（`fpk_hits/`，本轮起 `npk_hits/`），文件名带 md5 后 16 位，并记 `sha16` 供复核。
3. **同一资产可能在多个容器**：位置要**逐处记全**，不写"唯一位置"（star_xing 三处）。
4. 去重优化：`(off, ps, ds, flag)` 相同 ⇒ 载荷逐位必然相同，md5 直接复用（本轮 NPK 段单列 `dedup_reuse`）。
5. **不做 dec 预筛**（预筛只能排除、不能认定）；NPK 段即**全条目无预筛**扫描。

### 2A.6 34 皮肤批量的复用配方（下一步照做）
```
checksum集 = 清单(399,108 唯一)            # 2A.4
for 容器 in 四族全部（224 个不同容器，口径见 2A.2）:
    for 条目 in 0..entry_count:
        payload = 取载荷(条目)              # 2A.2 各族不同，gres 用「自己块的 base」
        if md5(payload) in checksum集:
            记 {容器, 条目, 绝对偏移, fid, flag, md5, sha16, 清单名, 尺寸, has_alpha}
            if checksum ∈ 该皮肤声明名 or 清单名 startswith 'effect/': 载荷落盘
```
- 已扫规模（可复算）：**224 个不同容器**（73 fpk + 136 gpk〔内含 80 gres〕 + 本轮 15 NPK）；各段累计解出 **>9.0 M 条载荷 / 446 GB**（gres 修正版是对同一批 80 个容器的重扫，勿重复计数）。
- 内存/时间量级：399,108 条 checksum 集合 ≈ 40 MB；主要成本是**解压**（本轮 >446 GB 输出量级按小时计），md5 本身可忽略。

### 2A.7 ⚡ 性能陷阱：**纯 Python LZ4 会把 NPK 段跑成小时级**（本轮实测修正）
- `npk_reader.lz4_block` 是**逐字节纯 Python**；`E:\mrzh\res.npk` + `res\ui.npk` 的 flag 2 条目输出 3.0 + 3.7 GB ⇒ 第一版扫描挂在 `res.npk` 上 ~40 分钟未完。
- **修正**：`lz4.block.decompress(raw, uncompressed_size=ds)`（原生 C）。
- **等价性证明**：40 条 ≥200 KB 样本 **40/40 逐位相同**（md5 相等），运行中在线自检 **440 条 0 不一致**；**148×** 加速（2.9 s → 0.02 s / 40 条）。
- 结果：15 个 NPK（8.87 GB 压缩 / 15.43 GB 输出）**123 秒**完成；`flag 12` 一律用 `max_output_size=ds*4+4096`（避免"帧无 content size"报错）。
- **同理**：任何"逐字节纯 Python 解压器"（lz4/lzma/zlib 手写版）在批量任务里都是陷阱 —— 先测等价性，再换原生库。

---

## 3. 已证 / 未证 / 未做

**已证**
1. **载荷 md5 打法有效**且**双向可复现**：LA 9 fpk 的 51,893 条命中与 Lead 逐文件一致；**四族 224 个容器**共解出 **>9.0 million 条载荷 / 446 GB**，命中 **99,580 条**（fpk 52,934 + gpk 29 + gres 168 + **NPK 46,449**）。
2. **清单 checksum = md5(原始资产字节)**：命中的载荷 md5 与清单逐位相等；其中 1 条（`star_xing_02_tp165.tga`）是**两皮肤的声明资产**，且**三容器互证**（§1A），已落盘可立刻用于绑定。
3. **gres 多块容器必须按块取 base**（修正后失败 7 行 vs 4,014,729 行）——本轮的方法学修正，已写进口径。
4. 🆕 **NPK 段全条目无预筛扫完**（817,281 条、失败 0、123 秒，见 `NPK_CONTENT_HUNT_20260920.md`）；**声明名 0、`effect/` 0**。
5. 🆕 **负面证据有效性已证**：30 个唯一声明 checksum 在 399,037 / 399,108 / 400,070 三套目标集里**都命中 30/30** ⇒ 四族的"未出现"不是"没比到"。
6. 🆕 **fid 轴被证伪**：`npk_reader.path_id` 双 murmur3 口径对 **65,995 条真有逻辑路径**的 NPK 条目 **0/65,995** 命中；再穷举 16,560 个候选哈希口径仍 0 ⇒ 名字→条目这条路在本机这一代容器上不通（与 gpk 的 20,000 名 0 命中一致）。

**未证**
1. 其余 **28 条声明资产**在 **224 个容器**中**未出现**（fpk 全量 + gpk dec ≤1.1 MB + NPK 全量）；**不写"绝对不存在"**，写"在 2026-09-20 本机快照的四族容器与清单口径内不存在"。若要更强的否定，需要"非本机来源"（服务器/更高版本/其它快照）。
2. **不可核 8 条**（集 A 口径）：`.spr` 帧表 + `caihong_06_jh_djs.tga`、`tex_glow_qirishijie_guangyun_hgz03_03.tga` 在清单里无同名 basename ⇒ 内容轴**无法核验**（清单不收 `.spr`）。
3. **gpk 单块族 dec >1.1 MB 的行**未参与比对（stage 预筛所致）；与声明源资产尺寸（≤512² ⇒ ≤1.05 MB）无关，故不影响结论。

**未做**
1. ~~NPK 条目载荷 md5~~ → **本轮已完成**（15 个 NPK，见 §2.4 与 `NPK_CONTENT_HUNT_20260920.md`）。
2. 未做"按内容反推候选替代"（纪律：**不顶替**）。
3. 未对 NPK 的 46,449 条 ui/l10n 命中做逐条 wiki 归属（元数据已全量交代，可另开任务）。

**建议下一步（按性价比）**
1. **交由用户裁决**：这 28 条源资产本机没有 —— 要么**按已找到的 effect 家族源资产 + 清单尺寸做保守替代（必须显式标注非源级）**，要么保持 unresolved（推荐后者，符合既有纪律）。
2. 立即可用：`star_xing_02_tp165.tga` 的三容器源级直证（§1A）支撑 1110171 `node[24]` 绑定升级；`npk_hits/` 里 25,976 个 ui/l10n/scene/shader 源资产可用于其它溯源。
3. 继续找只剩"非本机来源"：本机四族（fpk/gpk/gres/NPK）已穷尽。

---

## 4. 复现

| 脚本（`%TEMP%`） | 作用 |
|---|---|
| `FPK_hunt.py` | fpk 73 个：条目表 AES → 逐条 zstd → md5 → 比清单（含命中落盘） |
| `FPK_declared.py` / `FPK_inspect.py` | 用两皮肤完整声明名集合复核 fpk 命中；effect 家族清单 |
| `FPK_save_hit.py` | 命中资产落盘 + 格式/尺寸/哈希自证 |
| `GPK_hunt.py` | gpk 单块：stage A（dec 精确尺寸集）→ stage B（dec 1 KB–1.1 MB） |
| `GPK_gres_fix.py` | **gres 多块修正版**（每行自己块的 base）+ 目标扩到清单全量 397,105 checksum |
| `FPKH_build.py` / `FPKH_trim2.py` | 交付 JSON 组装 / 瘦身 |
| 🆕 `NPK_hunt.py` | **NPK 15 个主扫描**（原生 lz4 + zstd → md5 → 比 399,108；约 123 秒） |
| 🆕 `NPK_post.py` / `NPK_deliver.py` | NPK 命中重算落盘（25,976 次写入 → 唯一文件 25,296 个 / 1.97 GB）+ 交付 JSON |
| 🆕 `NPK_lz4_equiv.py` | 原生 lz4 vs 纯 Python **等价性证明**（40/40，148×） |
| 🆕 `NPK_coverage_check.py` | **健全性检查**：30/30 声明 checksum 在三套目标集内 |
| 🆕 `NPK_verdict2.py` | 四族 × 声明集 A/B 最终裁决表（`TWO_SKIN_SOURCE_VERDICT.json`） |
| 🆕 `NPK_evi_3cont.py` / `NPK_evi_gres_id2.py` | §1A 三容器源级直证的**独立重解** |
| 🆕 `NPK_fid_control.py` / `NPK_fid_crack.py` | fid 轴阳性对照（0/65,995）与有界穷举（16,560 候选 0 命中） |

产物：`FPK_CONTENT_HUNT_20260920.md`（本文件）、`FPK_CONTENT_HUNT_20260920.json`（696,862 B）、
`fpk_hits/star_xing_02_tp165__f1524e26d09832be.tga`（262,188 B，+ gpk/gres 同名 `.bin` 与 `.png` 预览）、
🆕 `NPK_CONTENT_HUNT_20260920.md` / `.json`（1.08 MB）、🆕 `npk_hits/`（唯一文件 25,296 个 / 1.97 GB）。
