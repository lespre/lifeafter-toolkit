# _1110171_脚本归档 · README

> 从 `E:\la拆包项目\03_执行\96_审阅区\_target_1110171\` **搬入**（`shutil.move`，同盘 rename；逐份 `sha256` 前后对拍，**只搬不删**）。
> 归档时间：2026-09-26 ｜ 归档执行者：Hermes 归档子代理 ｜ 环境：`C:/Users/<user>/py312_env/Scripts/python.exe`

## 1. 归档内容

| 项 | 值 |
|---|---:|
| 文件数 | **140** 个 `.py` |
| 体积 | **1,088,410 B**（1.04 MB） |
| 行数 | 18,997 行（审阅口径：`ast` 全量解析，`errors="replace"`） |
| 子目录结构 | **原样保持** |

```
_1110171_脚本归档\
├──（107 个）根目录脚本          AB_* AB2_* ENV_* FX* NAMES_* REPACK_* SFX_* SUBSFX_* _conv_* _run_* _scan_* env_* fx061_measure.py shader_*
├── fidelity\        12 个   FID_build / FID_selfcheck / Q1_color_order(_v2) / Q2_blend_analysis / Q2_scriptscan / Q3_analyze / Q3_corpus_scan / Q3_spr_timing / Q3_verdict(2) / Q4_clamp_audit
├── wpkscan\          8 个   step1_idx_probe … step5_pool_index
├── newver_scan\      5 个   step1_parse_probe / step2_scan / step2b_hash_struct / step2c_query_fixed / step3_final
├── h16c2\            3 个   stepA_anchor / stepD_wpk_scan / stepD2_launcher
├── model171_probe\   3 个   MODEL171_backfill / make_report / model171_probe
├── h16\              1 个   step1_e1.py
└── h16c\             1 个   h16_anchor_probe.py
```

## 2. ⚠ 这些脚本的**执行根已失效**

脚本里硬编码的三个旧根**均已不存在**（全量 `grep` 实测，按文件计）：

| 旧根（脚本里写的） | 引用它的脚本数 | 现址（已重构后） |
|---|---:|---|
| `03拆包产物` | **124 / 140** | `E:\la拆包项目\03_执行\` |
| `08Lifeafter wiki` | **65 / 140** | `E:\la拆包项目\04_站点\web\` |
| `01拆包器本体` | **31 / 140** | `E:\la拆包项目\01_工具\` |

（三者可重叠，故计数之和 > 140。现址三处均已 `os.path.isdir` 核实存在。）

⇒ **直接 `python X.py` 会 import / open 失败**。要重跑必须先改脚本里的路径常量。

### 2.1 只有 12/140 不含上述死路径（可直接读、路径无关）

| # | 脚本 | 说明 |
|---:|---|---|
| 1 | `shader_dump_evidence.py` | 从 `shader_gl_compile_probe.json` 抽决定性最小证据（纯读 JSON 打印） |
| 2 | `shader_extract_report.py` | 同上，只打印关键字段 |
| 3 | `h16/step1_e1.py` | H16 真值对 + E1 判别 + E2/E3 初筛 |
| 4 | `newver_scan/step1_parse_probe.py` | LA `res/*.fpk` 解析 + 名字变体查询（探路版） |
| 5 | `newver_scan/step2b_hash_struct.py` | 看清 `hashes` 元素结构以正确取 fid |
| 6 | `wpkscan/step1_idx_probe.py` | `idx` 结构 + 两份对比 + wpk 头 |
| 7 | `wpkscan/step1b_idx_parse.py` | `idx` 真结构 = 36B 头 + n×36B + md5 自证 |
| 8 | `wpkscan/step1c_key_offset.py` | 用已导出 DDS 池反算 md5 → 定位真键偏移 |
| 9 | `wpkscan/step2_4_wpk_probe.py` | wpk 头部/表/载荷 + 双向自证 |
| 10 | `wpkscan/step2_5_final.py` | `idx_keys(p)` 定位键表偏移/步长/条目字段 |
| 11 | `wpkscan/step3_union_pool.py` | 独立复现 wpk 自证 + 建并集池 |
| 12 | `wpkscan/step5_pool_index.py` | 写 `effect_pool_union/effect_pool_union.json` |

> 复现命令（只读）：
> ```bash
> cd ".../\_1110171_脚本归档"
> for f in $(find . -name "*.py" | sort); do
>   grep -qE "03拆包产物|08Lifeafter wiki|01拆包器本体" "$f" || echo "$f"; done   # → 上面这 12 个
> ```

## 3. 复用分级（引 `00_治理\文档\审阅_1110171_脚本与大件.md` §1–§2，**未执行任何脚本**）

| 分级 | 数量 | 处置建议 |
|---|---:|---|
| **R 可复用**（真算法/真判据/真引擎） | 92 | 搬入公共层（保留原件作证据） |
| **O 一次性**（结论已被文档侧吸收） | 35 | 脚本可删，文档留 |
| **S 已被取代**（能力已在公共层或同目录另一脚本） | 13 | 删前先确认取代者在库 |

**最值钱的单个文件**：`fx061_measure.py`（1,429 行 / 70.4 KB）—— 一台**通用 CDP 验收夹具引擎**
（`Driver` 类 / 手写 zlib PNG 解码 `png_stats` / `chrome_pids_by_profile`+`kill_tree` 的进程清理 /
pin 哈希链 / `collect_assertions()` 集中门）。审阅建议整体抽成 `toolkit_core/browser_harness.py`
（**目前 `toolkit_core` 21 个模块里没有浏览器验收层**；`_run_colorfix_verify.py` 625 行、
`REPACK_matdump.py`、`env_t6_*`、`BLACK129_*`、`SFX_e2e_check` 全是它的后代）。

**可直接照抄的四个「写入即自证」模板**：`FXIGNORE_carry.py`、`SUBSFX_merge.py`、`FX029_dg_merge.py`、`FX029_dg_merge2.py`
（`--dry-run` → `copy2` 备份 → 逐位置 canonical 快照 → 门不过拒写）。

## 4. 诚实边界

- 本归档**未执行这 140 个脚本中的任何一个**，未对其行为做运行验证；
  「可复用」判定来自审阅的 `ast` 解析 + 函数体逐段阅读（见审阅 §7 未证/边界）。
- 行数 18,997 与审阅 `ast` 口径一致；旧盘点文件记的 18,871 行是**解码口径差异**（本次统一 `errors="replace"`），非文件变化。
- **源目录里这 140 个文件已不在原位**（搬走），但源目录其余内容一律未动、未删。
