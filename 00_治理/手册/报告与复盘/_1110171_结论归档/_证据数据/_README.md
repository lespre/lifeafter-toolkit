# _证据数据 · README

> 从 `E:\la拆包项目\03_执行\96_审阅区\_target_1110171\` **搬入**（`shutil.move`，同盘 rename；逐份 `sha256` 前后对拍，**只搬不删**）。
> 归档时间：2026-09-26 ｜ 环境：`C:/Users/Administrator/py312_env/Scripts/python.exe`
> 关联索引：`..\\_00_必读清单.md`（文档 22 篇 A 类）｜ `_外部引用清单.md`（防断链白名单）｜ `..\\_对照集\\`（可对照小件）

## 1. 总量

| 项 | 值 |
|---|---:|
| 文件数 | **48** |
| 体积 | **136,990,767 B**（130.64 MiB / 137.0 MB） |

**另有 2 篇判据/冻结文档在上级目录**（它们同时也是文档组的成员，故**未在本目录留副本**）：
`..\CRITERION_BASELINE_20260919.md`（7,854 B，判据基线读数）与 `..\FREEZE_checkpoint.md`（3,790 B，冻结点）。

### ⚠ 体积上限纪律

委派方要求「若体积超 150 MB 就停下报告」。
**本组实搬 130.6 MiB（含外引文件共 137.0 MB），未超限**，故一次搬完。
**未搬入的大件**：`fidelity\Q3_corpus.json`（410,993,327 B = 392.0 MiB）—— 它在委派清单里属于「下一步可删」候选，不是本轮归档对象；
其**正本仍留在源目录**（`fidelity\Q3_corpus.json`）。

---

## 2. 分组清单

### 2.1 C 类决定性 JSON —— 平铺（17 件）

| 文件 | B | 是什么（依据） |
|---|---:|---|
| `GIM_effect_full_scan.json` | 40,114,071 | GIM/mesh 全量扫描；文件头实读 `scanned.effect_01.gpk.frames=423086, gim=111151, mesh=52822` |
| `GIM_effect01_bbox_v2.json` | 23,605,180 | GIM 包围盒扫描（**未被点名，作为同族一手扫描一并归档**） |
| `GIM_effect01_gim_name_index.json` | 19,708,275 | GIM 名字索引 |
| `FPK_PAYLOAD_MD5_20260920.json` | 13,634,511 | fpk 载荷 md5 表 |
| `SPR_CHANNEL_20260919.json` | 3,175,625 | `.spr` 兄弟行通道的扫描证据（对应 A 类 `SPR_CHANNEL_20260919.md`） |
| `FX_FILE_AUDIT.json` | 1,477,803 | FX 文件级审计机读件（对应 A 类 `FX_FILE_AUDIT_report.md`） |
| `R_off_sources.json` | 1,020,908 | } 6 件 `*_sources.json` 派生件（合计 **8,372,133 B ≈ 7.98 MiB**）： |
| `R_on_sources.json` | 1,022,585 | 委派清单写的是「`fidelity/` 下的 Q1–Q4 派生 `*_sources.json`」； |
| `R_B_off_sources.json` | 1,626,432 | **实测 `fidelity/` 下无此命名，真正的 `*_sources.json` 六件在根目录**， |
| `R_C_off_sources.json` | 1,534,233 | 故按实测位置搬这一组（名称与体积与「约 8 MB」吻合）。 |
| `R_D_off_sources.json` | 1,534,233 | |
| `R_D_on_sources.json` | 1,633,742 | |
| `CALIB_ruleR_verdict.json` | 42,881 | } 裁决表 3 件（合计 **73,333 B**） |
| `CALIB_ruleR2_verdict.json` | 23,168 | 对应 A 类 `CALIB_rule.md`（规则 C/D 对拍） |
| `CALIB_selfcheck_verdict.json` | 7,284 | |
| `assertion_suite.json` | 1,261 | } 断言套件 + 基线（合计 **17,303 B**） |
| `baseline.json` | 16,042 | |

### 2.2 保留子目录结构（10 件）

| 路径 | B | 说明 |
|---|---:|---|
| `h16/truth_pairs.json` | 14,049,682 | H16 真值对（对应 A 类 `H16_CALIBRATION_20260920.md` 的否证）**外部引用 3 次** |
| `fidelity/Q1_color_order.json` | 39,319 | } fidelity 派生读数/裁决 **7 件合计 2,547,640 B ≈ 2.43 MiB** |
| `fidelity/Q2_blend_analysis.json` | 13,402 | Q2 BlendMode 取值分布（36,008 份 `.sfx`） |
| `fidelity/Q2_scriptscan.json` | 1,192,709 | Q2 枚举表猎取（全量 NPK 载荷关键词扫描） |
| `fidelity/Q2_scriptscan.partial.json` | 1,192,328 | 同上的检查点残留 |
| `fidelity/Q3_spr_timing.json` | 61,373 | Q3 精灵帧时序源字段 |
| `fidelity/Q3_verdict.json` | 1,837 | Q3 裁决（H1 vs H2 对拍） |
| `fidelity/Q4_clamp_audit.json` | 46,672 | Q4 尺寸钳制双证据（对应 A 类 `FIDELITY_EVIDENCE_20260920.md` Q4） |
| `bychecksum/selected.json` | 874 | **6 条「名字→checksum→尺寸/alpha」声明真值**（权威清单里挑出的那几条） |

### 2.3 被外部引用的文件（防断链）—— 平铺 18 件（9,833,111 B）+ 目录 1 个（4 件 / 381,226 B）

| 文件 | B | 外部引用次数（引 `00_治理\规范\_target_1110171盘点.md` §7b） |
|---|---:|---:|
| `SKEL2_all_37.json` | 100,963 | **23** |
| `neox_roles.png` | 726,781 | 1 |
| `ENV_uniforms_per_prim.json` | 236,847 | 3 |
| `FXADAPT_missing_resources.json` | 3,860 | 1 |
| `AFTER_default.png` | 682,229 | 1 |
| `v3_default.png` | 682,229 | 1 |
| `wiki_page_final.png` | 764,421 | 1 |
| `neox_view_source_strict.png` | 641,169 | 1 |
| `neox_view_m.png` / `neox_view_forward_family.png` / `neox_view_T_sRGB.png` / `neox_view_T_linear.png` / `neox_view_C_base.png` / `neox_view_C_base_diagA1.png` | 各 640,871 | 各 1 |
| `S177_gem_D0_diag_nocp.png` | 12,022 | 1（「`S177_gem_D0_diag_nocp.png` 等 4 张」） |
| `S177_gem_D0b_diag_nocp.png` | 711,313 | 1 |
| `S177_gem_D1_diag_cp.png` | 713,786 | 1 |
| `S177_gem_D2_diag_notbase.png` | 712,265 | 1 |
| `_repro_backup_20260916_231108/`（4 件） | 381,226 | 1 |

> 7 张 `neox_view_*.png` 与 4 张 `S177_gem_D*.png` **不在委派方的点名清单里**，
> 但 `_target_1110171盘点.md` §7b 的「外部点名白名单」把它们列为被引用 ⇒ 按「防断链」的同一目的**一并搬入**，并在此显式登记。

---

## 3. 诚实边界（**没读的就说没读**）

- 本节所有「是什么」列的依据是：① 同批审阅报告的结论；② 该文件的**体积与文件名**实测。
- **本次归档未打开/未解析上表任何 JSON 的内容**（除 `.._00_必读清单.md` 生成时读的库存元数据）。
  `Q2_scriptscan.json`、`truth_pairs.json` 等大件的内部结构描述**引自审阅**，非本次实测。
- 归档执行只做了 `stat` / `sha256`（搬移对拍）+ 集合比对，**未做内容级校验**。
