# SPR_CHANNEL_20260919 — `.spr` 兄弟图集通道（全容器扩查 + 1110177 声明名交叉匹配）
> toolchain-auditor · **task-64** · 2026-09-19 · 只读源包；只写 `_target_1110171/SPR_CHANNEL_20260919.{md,json}` 与新建 `spr_atlas/`

## 1. 通道规则 · 三重证据 · **两容器独立复现**
**规则**：`.spr` 描述符行 **i** 的图集 DDS 在**同一容器的行 i-1**。
| 证据 | 结果 |
|---|---|
| 结构 | `effect_01.gpk` **756/756 (100%)** 前一行是 DDS；`effect_02.gpk` **192/192 (100%)** —— **规则已在两个容器独立复现**（我用 Lead 的布局代码另行复扫，数字与 Lead 一致） |
| 尺寸 | `effect_01`：`dims_match` **368**（显式 sheet）**+ 24**（`sheet` 缺失时按帧表推导，即 Lead 索引的 `dims_from_frames`）**= 392/756** ⇒ **与 Lead 的 392 完全对上**；`sheet_unknown` 单列 **165 **；按 Lead 口径（`sheet is None` 不入分子也不入分母）= **368/591 = 62.27%** |
| 目视 | 复用 Lead 3 例目视；本轮另导出 5 张真图集 PNG 可复看 |

**`.spr` 文本**：第 1 行 `<mode>[ <W> <H>]`（同行）· 第 2 行 `<bpp>` · 第 3 行 `<param>` · 其后 N 行 `<name>.tga x0 y0 x1 y1`（**`name.tga` 即名字轴**）。

## 2. 全容器扩查（**便宜扫法**：只用行表 `dec ∈ [8,8192]` 过滤，只解压小行；不算 gpk 行数以外的载荷）
范围 = `E:\mrzh\Documents\gres\*.gpk`(36) + `E:\LifeAfter\Documents\gres\*.gpk`(37) + `E:\mrzh\res\*.gpk` + `E:\LifeAfter\res\*.gpk` ⇒ **135 个容器**。

| 容器（择要） | 行数 | 小行 | `.spr` | 前一行是 DDS | `sheet_unknown` | dims 相符/分母 |
|---|---|---|---|---|---|---|
| `0042.gpk` | 167541 | 37859 | 12 | 0 | 11 | 0/1 |
| `0054.gpk` | 99023 | 15979 | 15 | 0 | 12 | 0/3 |
| `0057.gpk` | 41406 | 18529 | 2 | 0 | 0 | 0/2 |
| `0058.gpk` | 64276 | 29313 | 11 | 1 | 6 | 0/5 |
| `0007.gpk` | 118417 | 79649 | 38 | 4 | 35 | 0/3 |
| `0032.gpk` | 194234 | 137723 | 835 | 0 | 140 | 0/695 |
| `0049.gpk` | 88615 | 18695 | 2 | 0 | 2 | 0/0 |
| `0062.gpk` | 79219 | 11083 | 26 | 0 | 22 | 0/4 |
| `0064.gpk` | 75688 | 33830 | 13 | 0 | 6 | 0/7 |
| `effect_01.gpk` | 212151 | 168890 | 756 | 756 | 165 | 368/591 |
| `effect_02.gpk` | 3048 | 806 | 192 | 192 | 69 | 86/123 |

**合计**：**135 容器 · `.spr` 1,974 条 · 唯一帧名（名字轴）931 个**。

⚠ **重要负面结论**：**除 `effect_01/02.gpk` 外，其它容器的 `.spr` 前一行几乎都不是 DDS**（如 `LifeAfter\gres\0032.gpk` 有 **835 条 `.spr`** 但 `atlas_is_dds = 0`）⇒ **「兄弟行」规则只在这两个 effect 容器成立**；gres 族里 `.spr` 存在但**图集不在前一行**（不得据此配对）。

## 3. `effect3.wpk` 族 ⇒ `no_spr_in_wpk`（判定依据）
- `E:\mrzh\Documents\res\effect3.wpk`(35.7 MB) 与 `E:\LifeAfter\...\effect3.wpk`(55.6 MB)：用 gpk 布局解析**失败**（`unpack_from requires a buffer of at least 35651552 bytes ... actual 35651520`）⇒ **块链/行表布局不同**，未硬套规则；
- raw 特征探针字段写入 json（`raw_spr_signature_hits` / `raw_has_spr_ext`）⇒ 结论 **`no_spr_in_wpk`**（在 wpk 里未取得 `.spr` 描述符证据，而非＂确认不存在＂，判定依据即上述解析失败 + raw 特征）。

## 4. 1110177 声明名逐条结论
- 口径：`1110177/**` 下 `.sfx/.json/.xml/.txt/.gltf` 全覆盖正则（GBK/UTF-8 双解）⇒ **唯一 145 条**（出现 1,306 次；tga 50 · dds 46 · png 43 · spr 6）。⚠ Lead 口径为 **140 条**（`sfx/*.sfx + effects.json`，tga 93/dds 30/spr 11/png 6）⇒ **两口径都保留**，json 内逐条 `declared` 可按任一口径取子集。
- 搜索结果：**命中 5 / unresolved 140**（在 **135 容器 / 1,974 条 `.spr` / 931 个帧名**的名字轴上按 basename 与 stem 双口径搜索）。

| 声明名 | 真图集（结构+尺寸） | 另在 gres 名字轴出现 |
|---|---|---|
| `lightning07_cs.spr` | `effect_01.gpk` row207659（atlas_row 207658，dims [512, 512]，sheet 相符） | 0032.gpk |
| `lightning_01.spr` | `effect_01.gpk` row207671（atlas_row 207670，dims [512, 512]，sheet 相符） | 0057.gpk、0064.gpk |
| `shandian_05_yh_djs.spr` | `effect_01.gpk` row207712（atlas_row 207711，dims [256, 256]，sheet 相符） | 0032.gpk |
| `smoke25.spr` | `effect_01.gpk` row208478（atlas_row 208477，dims [512, 512]，sheet 相符） | 0032.gpk |
| `tex_special_fangkuai_tp52.spr` | `effect_01.gpk` row211384（atlas_row 211383，dims [256, 256]，sheet 相符） | 0032.gpk |

**导出 PNG（真图集，保 alpha）**：`spr_atlas/` 5 张 —— `lightning07_cs__atlas207658.png`(512², sha16 `dbc4d2e4fe65ff4f`) · `lightning_01__atlas207670.png`(512², `dde58c1eb420384f`) · `shandian_05_yh_djs__atlas207711.png`(256², `bab99d2e79746152`) · `smoke25__atlas208477.png`(512², `45ae45ab090353cb`) · `tex_special_fangkuai_tp52__atlas211383.png`(256², `37fa4be63541ffab`)。

**你点名要核的 6 个 content_candidate**（`glow_01.tga`/`dian_12.tga`/`glow_16_yh_djs.tga` 等）：**全容器名字轴 0 命中** ⇒ **仍无直证，维持 unresolved**（未顶替）。

## 5. 诚实写明：为什么对 `.tga`/`.dds`/`.png` 声明无效
**直接原因**：那 140 个名字**没有作为任何 `.spr` 的帧名出现**（`names[]` 的 basename 与去扩展 stem 双口径、135 容器全域搜索均为 0），**不是「容器里没有内容」** —— 这些名字对应的是**独立贴图资源**（走 DDS 行/PKG 名字轴），不是精灵表帧名。⇒ **通道对它们结构性无效**，不是覆盖不足。

## 6. **直接回答**：能把 1110177 绑定率从 9/34 提上去多少？
- 可提：**5 条**（上表，全部结构+尺寸双证、已导出真图集，帧表在 json 的 `frames`，viewer 侧支持按帧矩形切片即可用）；
- 不可提：**140 条**（见 §5 的结构性原因）；
- ⇒ **9/34（26.5%）→ 最多 14/34（41.2%）**，增量 **+5 条 / +14.7pt**。**这 5 条都是 `.spr` 类声明**，`.tga`/`.dds`/`.png` 声明一条都提不上。

## 7. 未解项 / 未做 / 边界
1. `virtual_sheet_ratio`（等值不符但结构成立）**用途未判定**：含义（虚拟画布/UV 归一）未证 ⇒ 只标注，不当配对成功也不当失败；
2. `effect3.wpk` 族与其它非 gpk 容器**未解**（布局不同）⇒ `no_spr_in_wpk`；
3. 帧矩形 ↔ 粒子尺寸换算属 task-58 范畴，本轮不涉；
4. **边界**：全程只读源包；**未改** `08Lifeafter wiki/**` 任何文件（`1110177/effects.json`、`viewer.json`、viewer.js、adapter、board.html 一个都没碰）；只新建/更新了本报告的两个文件与 `spr_atlas/`。

## 8. 复现命令
```
python -X utf8 %TEMP%\spr_scan_multi.py     # 阶段一：effect_01/02 + wpk 判定
python -X utf8 %TEMP%\spr_match_export.py   # 阶段二：dims/ratio + 声明名匹配
python -X utf8 %TEMP%\spr_final.py          # 阶段三：图集 PNG 导出 + 报告初稿
python -X utf8 %TEMP%\spr_discover.py       # 阶段四：135 容器便宜扫（行表 dec 过滤）
python -X utf8 %TEMP%\spr_final2.py         # 阶段五：全容器名字轴匹配 + dims 口径 + 终稿
```
