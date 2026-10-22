# NPK_CONTENT_HUNT_20260920 — NPK 载荷 md5 全量比对（task-86 续，最后一族）

- 任务：**task-86 续**（env-auditor）。源包只读；本报告只写 `NPK_CONTENT_HUNT_20260920.md/.json` + `npk_hits/`。
- 打法：与 fpk/gpk/gres 完全同构 —— **`parse_npk` 行表 → `unpack_entry` 取载荷 → md5 → 比对清单 checksum**（`checksum = md5(原始资产字节)`）。
- 覆盖：**15 个 NPK / 8.87 GB**，`E:\mrzh\res.npk`、`E:\mrzh\res\ui.npk`、`E:\mrzh\script*.npk`、`E:\mrzh\Documents\script*.npk`、`E:\LifeAfter` 全部同类文件。
- **不做任何 dec 预筛**（全条目）。
- 未触碰任何 wiki / viewer / adapter / `effects.json`（写盘范围仅本目录）。

---

## 0. 直接回答：**NPK 里也没有那 28 条** —— 四族至此全部扫完

> - **NPK 命中声明名 0/34**（`effect/` 前缀亦 **0**）。
> - 四族（fpk 73 + gpk 136〔内含 gres 80〕+ NPK 15 = **224 个容器**）累计命中两皮肤声明资产 **仅 1 条**：`star_xing_02_tp165.tga`（存在于 048.fpk / effect_01.gpk / 0052.gpk，**不在 NPK**）。
> - **健全性检查（本轮新增，最关键）**：30 个唯一声明 checksum **全部**落在三套目标集口径（399,037 / 399,108 / 400,070）之内 ⇒ 各族的"未出现"是**有效负面证据**，不是"没比到"。
> - 因此结论可升级为：**这 28 条声明源资产在本机（四族全部容器 + 清单口径内）不存在**；不是"本轮范围未出现"。若需引用，仍建议保留限定语"在 2026-09-20 本机快照的四族容器内"。

---

## 1. 规模台账（15 个容器，可复算）

| 容器 | 条目 | 解出 | 失败 | 输出 | 命中（声明） | 秒 |
|---|---|---|---|---|---|---|
| `E:\mrzh\res.npk` | 16,905 | 16,905 | 0 | 3.00 GB | **18** (0) | 10.0 |
| `E:\mrzh\res\ui.npk` | 57,353 | 57,353 | 0 | 3.74 GB | **46,405** (0) | 44.6 |
| `E:\mrzh\script.npk` | 61,343 | 61,343 | 0 | 0.58 GB | 0 | 3.1 |
| `E:\mrzh\script.py314.lc.npk` | 105,777 | 105,777 | 0 | 1.11 GB | 0 | 6.6 |
| `E:\mrzh\Documents\script.npk` | 87,597 | 87,597 | 0 | 0.85 GB | 0 | 4.5 |
| `E:\mrzh\Documents\script.py3.npk` | 93,977 | 93,977 | 0 | 1.15 GB | 0 | 5.6 |
| `E:\mrzh\Documents\script.py314.lc.npk` | 27,558 | 27,558 | 0 | 0.49 GB | 0 | 3.4 |
| `E:\LifeAfter\res.npk` | 3,114 | 3,114 | 0 | 0.03 GB | 1 | 0.3 |
| `E:\LifeAfter\res\ui.npk` | 35 | 35 | 0 | 0.01 GB | **25** | 0.1 |
| `E:\LifeAfter\script.npk` | 531 | 531 | 0 | 0.00 GB | 0 | 0.0 |
| `E:\LifeAfter\script.py3.npk` | 81,148 | 81,148 | 0 | 0.89 GB | 0 | 4.5 |
| `E:\LifeAfter\script.py314.lc.npk` | 110,836 | 110,836 | 0 | 0.97 GB | 0 | 6.0 |
| `E:\LifeAfter\Documents\script.npk` | 85,525 | 85,525 | 0 | 0.83 GB | 0 | 4.4 |
| `E:\LifeAfter\Documents\script.py3.npk` | 38,965 | 38,965 | 0 | 0.87 GB | 0 | 3.7 |
| `E:\LifeAfter\Documents\script.py314.lc.npk` | 46,617 | 46,617 | 0 | 0.92 GB | 0 | 5.4 |
| **合计** | **817,281** | **817,281** | **0** | **15.43 GB** | **46,449 (0)** | **123** |

- 失败 **0**（flag 分布见 JSON `npk_files[].flag_counts`）；`lz4` 原生/纯 Python **在线自检 440 条，0 不一致**。
- 11 个 `script*.npk`（61.4 GB 级脚本包）**全 0 命中** —— 脚本包不含清单资产（符合预期，但已实测而非假设）。

---

## 2. 命中分布（46,449 条）

**家族**：`ui` **45,799** / `l10n` 631 / `common_preview` 11 / `scene` 4 / `common` 2 / `shader` 2；**`effect` 0**。
**唯一性**：唯一 md5 **44,365** = 唯一清单名 **44,365**（无一对多冲突）。
**二级目录 top12**：`ui/upload_icon` 2,849｜`ui/all_pc` 2,247｜`ui/quyuxingdong_v4` 1,033｜`ui/map_icon` 992｜`ui/other_icon` 953｜`ui/shangcheng_icon` 937｜`ui/main_zhujiemian_v3` 922｜`ui/shangcheng` 897｜`ui/zhuti_huodong_v3` 658｜`ui/resources_icon` 657｜`ui/jiaju_v3` 646｜`ui/zazhi_huodong_v4` 606。
**家族字节**：ui 3,489.7 MB｜l10n 57.5｜scene 11.5｜shader 2.1｜common 0.5｜common_preview 0.5。

**落盘**：`npk_hits/` —— **写入 25,976 次 → 磁盘唯一文件 25,296 个 / 1.97 GB**（648 个文件名相同且 md5 相同 ⇒ 覆盖，内容逐位相同、无损失）；非 ui 家族 **650 条全部落盘**，ui 家族按 **2 GB 上限**落盘；未落盘的 20,473 条**在 JSON 里仍有完整元数据**（容器/条目/fid/偏移/flag/md5/sha16/清单名/尺寸/alpha）。落盘时逐条**重算 md5 断言等于命中 md5**（25,976/25,976 通过）；复核脚本 `NPK_saved_audit.py`。

> 这 46,449 条是**源级 ui/l10n/scene/shader 资产**（可直接用于其它 wiki 页面的图片溯源），但对极光剑两皮肤的 `effect/textures/*` 声明**没有帮助**（effect 命中 0）。

---

## 3. 方法学补遗（并入 `FPK_CONTENT_HUNT_20260920.md` §2A）

### 3.1 NPK 取载荷口径
```
head = AES_ECB(f.read(32)) → (_u, magic=0x4B50584E, ver, table_off, entry_count)
table = AES_ECB(f.read(entry_count*48))           # 48 B/条
row = <QIIIIIi> = (fid, off, packed_size, decoded_size, c1, c2, flag)
payload = f[off : off+packed_size]
flag=2 → lz4（原生）；flag=12 → zstd（max_output_size=ds*4+4096）；flag=0 → npk_reader.unpack_entry（AES+zlib 或原样）
```
### 3.2 ⚡ 性能修正：**不要用纯 Python LZ4**（方法学级）
- `npk_reader.lz4_block` 是**逐字节纯 Python**，对 `E:\mrzh\res.npk`/`ui.npk`（flag 2 占多数，输出 3+3.7 GB）会跑成小时级 —— 我第一版因此挂在 `res.npk` 上 ~40 分钟未完成。
- **修正**：`lz4.block.decompress(raw, uncompressed_size=ds)`（原生 C）。
- **等价性证明**：40 条 ≥200 KB 样本 **40/40 逐位相同**（md5 相等）；运行中再抽 **440 条在线自检，0 不一致**；**148×** 加速（2.9 s → 0.02 s/40 条）。
- 结果：全量 15 个 NPK（含 8.87 GB 压缩 / 15.43 GB 输出）**123 秒**跑完。

### 3.3 目标集口径（三套，声明 checksum 全覆盖）
| 口径 | 唯一 checksum | 来源 |
|---|---|---|
| 严格正则（要求 `has_alpha`+`img_size` 完整） | **399,037** | 自解 `res.npk` entry 8858（532,462 行） |
| `TS_manifest_full.json` | 397,105 | 前轮自建（529,370 条） |
| **本段扫描实际用（严格 ∪ full）** | **399,108** | `NPK_hunt.py` |
| 宽松正则（只要求 path+checksum） | **400,070** | 533,861 行 |
- **健全性检查**：30 个唯一声明 checksum 在 **399,037 / 399,108 / 400,070 三套里都命中 30/30** ⇒ 三族扫描都能"比到"这些声明（`NPK_coverage_check.py`）。
- 差异说明：严格正则漏掉 962 行（meta 形状不同），故 400,070 才是上界口径；对本轮结论无影响（声明全覆盖）。

---

## 4. 两皮肤声明名最终裁决表（四族）

数据源：四族命中 md5 集合（fpk 52,934 / gpk 29 / gres 168 / NPK 46,449，唯一 md5 74,758）+ 清单并集（400,070）。

**集 A（32 条皮肤声明名，`FPK_declared.json` 口径）**
- **可比 24**（checksum 在扫描目标集内）：**命中 1**（`star_xing_02_tp165.tga`）、**未出现 23**。
- **不可比 8**：清单里没有同名 basename ⇒ 内容轴**无法核验**（4 个 `.spr`：`lightning_01`/`lightning07_cs`/`shandian_05_yh_djs`/`tex_glow_tp07_02`/`smoke25`/`tex_special_fangkuai_tp52` 中的 `.spr`，以及 2 个 `.tga`：`caihong_06_jh_djs.tga`、`tex_glow_qirishijie_guangyun_hgz03_03.tga`）。
  - ⚠ 注意 `.spr`(5 条) 是清单**不收**的帧表，不是"不存在"。

**集 B（34 条声明路径，`TS_validate.json` 口径，checksum 来自声明行 meta）**
- **可比 29 → 命中 0**；不可比 5（无 meta checksum：`tex_crack_02_yx_djs.tga`、`tex_glow_qirishijie_...tga`、3 个 `.spr`）。
- 逐条 34 行裁决（含每个 checksum 与"可比/不可比"判定）见 `NPK_CONTENT_HUNT_20260920.json` → `declare_verdict` 及 `%TEMP%\TWO_SKIN_SOURCE_VERDICT.json`。

---

## 5. fid 轴：**证伪**（如实登记为未决，不作为证据）

- 本轮 stage0 曾用「NPK 条目表 fid = 双 murmur3 路径哈希」对 34 条声明名 × 2,028 变体（分隔符 \\ / `/`、扩展名互换、大小写、去一层目录）× 3 编码（utf-8/gbk/latin1）查表，**0 命中**。
- **阳性对照：（该结果不可用）** —— 拿 `E:\mrzh\script.npk` 里 **65,995 条能还原出逻辑路径**（`patch\PanelPCDownloader.py` 等）的条目去核同一口径，**0/65,995 对上**。
- 再做有界穷举：8 组真值对 × 9 种字符串变换 × 4 编码 × {murmur3×10 seed, crc32, adler32, fnv1a32/64} + 双 murmur seed 组合 = **16,560 个候选，0 命中**。
- 观察：真值对的 fid 高 32 位随条目序号**单调增长**（`0x00016295…`→`0x000879d8…`），低 32 位近似随机 ⇒ 该代 NPK 的 fid 更像"全局 ID + 未知哈希"，**不是路径哈希**。
- 结论：**`npk_reader.path_id` docstring 声称的"已验证"不成立于本机这一代 NPK**；fid 轴不能用于名字→内容反查（与 gpk 族结论一致：20,000 清单名 0 命中）。
- 遗留未决：fid 低 32 位的真实哈希口径（穷举范围外，未破解）。

---

## 6. 未证 / 未做

**未证（保留限定语，不写"确认不存在"）**
1. 集 A 的 8 条 + 集 B 的 5 条**无清单 checksum** 的声明（多为 `.spr` 帧表）⇒ 内容轴**无法核验**，只能写"清单不收、无法核验"。
2. **gpk 单块族 dec > 1.1 MB 的行**未参与比对（task-86 的 stage 预筛）—— 与声明源资产尺寸（≤512²、≤1.05 MB）无关，故不影响本结论。

**未做**
1. 未做"按内容反推候选替代"（纪律：**不顶替**）。
2. 未对 46,449 条 ui/l10n 命中做逐条 wiki 归属（超出本任务；元数据已全量交代，可另开任务）。

**建议（按性价比）**
1. **接受"这 28 条源资产本机没有"**，交由用户裁决：要么用**同族 `effect/` 源资产按尺寸/用途做保守替代并显式标注非源级**，要么保持 unresolved（推荐后者符合既有纪律）。
2. 立即可用：`star_xing_02_tp165.tga` 的源级直证（见 `FPK_CONTENT_HUNT_20260920.md` §1A）已足以支撑 1110171 `node[24]` 的绑定升级。
3. 若要继续找：只剩"非本机来源"（服务器下发 / 更高版本客户端 / 其它机器快照）——本机四族已穷尽。

---

## 7. 复现（脚本均在 `%TEMP%`）

| 脚本 | 作用 |
|---|---|
| `NPK_hunt.py` | 主扫描：15 NPK → `parse_npk` → 原生 lz4/zstd → md5 → 比 399,108 checksum；命中落盘 `npk_hits/`（**约 123 秒**） |
| `NPK_post.py` | 后处理：统计 + 命中重算 md5 落盘 + `NPK_hunt_post.json`（全量命中元数据 18.5 MB） |
| `NPK_deliver.py` | 交付 JSON 瘦身组装（non-ui 全量 + ui 抽样 + 裁决摘要） |
| `NPK_lz4_equiv.py` | 原生 lz4 vs 纯 Python **等价性证明**（40/40 逐位相同，148×） |
| `NPK_coverage_check.py` | **健全性检查**：30/30 声明 checksum 在三套目标集内 |
| `NPK_verdict2.py` | 四族 × 声明集 A/B 裁决表（`TWO_SKIN_SOURCE_VERDICT.json`） |
| `NPK_fid_control.py` / `NPK_fid_crack.py` | fid 轴**阳性对照**（0/65,995）与有界穷举（16,560 候选 0 命中） |
| `NPK_evi_3cont.py` / `NPK_evi_gres_id2.py` | star_xing 三容器**源级直证**的独立重解（见 FPK 报告 §1A） |

**产物**：`NPK_CONTENT_HUNT_20260920.md`（本文件）、`NPK_CONTENT_HUNT_20260920.json`（1.08 MB）、`npk_hits/`（**唯一文件 25,296 个 / 1.97 GB**，25,976 次写入含 648 个同名同 md5 覆盖）。
