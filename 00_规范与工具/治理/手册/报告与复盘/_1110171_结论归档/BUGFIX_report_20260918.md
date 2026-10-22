# BUGFIX 报告 — 零散遗留缺陷批量修复（任务 A/B/C）

- 生成时间：2026-09-18 23:5x（本地）
- 执行者：修复型子代理（写域严格受限，见下）
- 交付目录：`03拆包产物\_target_1110171\`
- 工具目录：`01拆包器本体\工具库\06_皮肤定位链\`（**只新增，未改任何既有文件**）

## 0. 写域合规声明

| 动作 | 路径 | 是否越界 |
|------|------|----------|
| 修改 | `08Lifeafter wiki\assets\3d\weapon_skin\{1110024,1110145,1110146,1110152,1110165}\src_cube\faces\*.png` + 同名 `.bak_mangled_<ts>` 备份 | 允许（任务 A 写域） |
| 新建 | `01拆包器本体\工具库\06_皮肤定位链\{cube_faces_export.py, gpk_npk_index.py, resolve_declared_paths.py, README_新增工具.md}` | 允许（任务 C 写域，全为新文件） |
| 新建 | `03拆包产物\_target_1110171\BUGFIX_*` | 允许（新交付文件） |

**未触碰**（全部只读/只登记）：`assets\weapon_skin_viewer.js`、`assets\weapon_skin_sfx_adapter.js`、
`board.html`、`assets\3d\weapon_skin\data\**`、任何 `neox_material.json` / `viewer.json` / `effects.json`、
任何 `.dds`、`06_皮肤定位链` 下既有文件、`E:\mrzh` 下任何文件。

所有改动前均按 mtime+sha 备份（`shutil.copy2` 保留 mtime），**旧文件一律不删除**。

---

# A 段 — 修「立方体六面 PNG 被错切」

## A.1 做了什么

对 7 组已定证"分带拼接（错切）"的 cube，用新工具 `cube_faces_export.py` 按
**face-major** 重切 6 张 mip0 PNG（`BGRA→RGBA`、保 alpha）：

```
off(face=i, mip=k) = 128 + i × 87380 + Σ_{m<k} max(1,128>>m)² × 4
每面 mip 链 = (128²+64²+…+1²) × 4 B = 87380 B ；文件长度 = 128 + 6×87380 = 524408 B
```

命令（实际执行，`--backup-tag mangled`，时间戳 `20260918_231623`）：

```bash
python 01拆包器本体\工具库\06_皮肤定位链\cube_faces_export.py \
  "…\1110152\src_cube\qiangpi.dds" \
  --ref-dir "…\1110129\src_cube\faces" --ref-dir "…\1110165\src_cube\faces" \
  --ref-dir "…\1110171\src_cube\faces" --ref-dir "…\1110177\src_cube\faces" \
  --apply --timestamp 20260918_231623

python … "…\1110024\src_cube\indoor.dds" "…\1110024\src_cube\gdansk_shipyard_buildings.dds" --apply …
python … "…\1110145\src_cube\bg61f_…_1.dds" "…\1110146\src_cube\glazed_patio.dds" --apply …
python … "…\1110165\src_cube\bg61f_…_1.dds" --ref-dir "…\1110145\src_cube\faces" --apply …
python … "…\1110165\src_cube\glazed_patio.dds" --ref-dir "…\1110146\src_cube\faces" --apply …
```

**结果：重切 42 张面 PNG（7 cube × 6 面），其中 35 张内容发生变化**
（每 cube 的 f0 在两种切法下同址，故不变 —— 这正是"面 0 侥幸正确"的量化证据）；
生成 **35 个备份**，合计 1,089,363 B。全部 cube 自检通过。

## A.2 证据（自证）

### 证据 0 — 修改前的定量判定（重扫 17 个 cube-dir）

| 皮肤 | cube | 文件字节 | 与 face-major 切法 mean\|Δ\| | 与 mip-major 切法 mean\|Δ\| | 判定 |
|------|------|---------|------------------------------|-------------------------------|------|
| 1110024 | gdansk_shipyard_buildings | 524408 | 26.2743 | **0.0000** | 错切 |
| 1110024 | indoor | 524408 | 80.7090 | **0.0000** | 错切 |
| 1110145 | bg61f_light_spherereflectioncapture_1 | 524408 | 17.3261 | **0.0000** | 错切 |
| 1110146 | glazed_patio | 524408 | 21.6064 | **0.0000** | 错切 |
| 1110152 | qiangpi | 524408 | 33.2570 | **0.0000** | 错切 |
| 1110165 | bg61f_light_spherereflectioncapture_1 | 524408 | 17.3261 | **0.0000** | 错切 |
| 1110165 | glazed_patio | 524408 | 21.6064 | **0.0000** | 错切 |
| 1110129 / 1110165 / 1110171 / 1110171_cand / 1110177 | qiangpi、car_studio01、fashion_qiangpi | — | **0.0000** | >0 | 正常（未动） |

> 逐面看更清楚：错切 cube 的 **f0 在两种切法下 mean\|Δ\| 都是 0**，f1..f5 则"face-major 大、mip-major 恰为 0"。
> 机理：mip-major 读面 f 的起点比真实链起点晚 `f×21844 B` ⇒ 读到的前 21844 B（≈42.66 行）
> 是**上一面的小 mip 带**，其余 43692 B（≈85.34 行）才是真面 f 的顶部。

### 证据 (a) — 与其它皮肤「正确的同名 cube」逐像素一致

| cube | 新切目标 | 参照皮肤 | 结果 |
|------|---------|---------|------|
| qiangpi | 1110152 | 1110129 / 1110165 / 1110171 / 1110177 | **6 面 × 4 参照 = 24/24 全等**，mean\|Δ\|=0.0000，像素 sha16 完全相同 |
| bg61f_light_spherereflectioncapture_1 | 1110165 | 1110145 | 6/6 全等，mean\|Δ\|=0.0000 |
| glazed_patio | 1110165 | 1110146 | 6/6 全等，mean\|Δ\|=0.0000 |

`qiangpi` 的独立复现尤其强：`1110152/qiangpi.dds` 与那 4 个皮肤的 `qiangpi.dds`
**sha16 全部等于 `173d52990b3ab836`**（同一份字节），而那 4 个皮肤的旧面图已被独立判定为
正确的 face-major 切法 ⇒ 新切结果与 4 个独立来源逐像素一致。

### 证据 (b) — 六面互异 + 与 DDS 原始字节逐字节吻合

对全部 7 个 cube、42 张面：

* `六面互异 = True`（6 张 m0 的像素 sha16 无重复）；
* `byte_exact_vs_dds = True`（每面 PNG 像素按 `RGBA→BGRA` 还原后，与 DDS 在公式偏移处的原始字节
  **完全相等**，不是"近似"；失败面列表为空）；
* 写盘后回读校验 PNG 往返一致。

`1110024/indoor` 与 `1110024/gdansk_shipyard_buildings` 在全盘**没有同名 cube 可对照**，
故只靠 (b) 成立。

### 旧 vs 新 mean\|Δ\|（应显著 >0）

| 皮肤 | cube | dds sha16 | f1 | f2 | f3 | f4 | f5 | 六面均值 |
|------|------|-----------|----|----|----|----|----|---------|
| 1110024 | gdansk_shipyard_buildings | 3c838953a5db91c1 | 28.7836 | 36.2255 | 40.3811 | 23.7728 | 28.4831 | 26.2743 |
| 1110024 | indoor | a464190b0febb360 | 70.4337 | 81.1531 | 150.3877 | 82.1506 | 100.1287 | 80.7090 |
| 1110145 | bg61f_light_spherereflectioncapture_1 | 8d0047fb56726870 | 21.9357 | 22.2325 | 17.7464 | 18.7062 | 23.3358 | 17.3261 |
| 1110146 | glazed_patio | 3c06f63dc94ed8f7 | 29.1525 | 28.4592 | 29.7301 | 20.5350 | 21.7614 | 21.6064 |
| 1110152 | qiangpi | 173d52990b3ab836 | 36.6896 | 36.7060 | 37.1137 | 44.5623 | 44.4703 | 33.2570 |
| 1110165 | bg61f_light_spherereflectioncapture_1 | 8d0047fb56726870 | 21.9357 | 22.2325 | 17.7464 | 18.7062 | 23.3358 | 17.3261 |
| 1110165 | glazed_patio | 3c06f63dc94ed8f7 | 29.1525 | 28.4592 | 29.7301 | 20.5350 | 21.7614 | 21.6064 |

（f0 全部 0.0000，故未列入。）

### 改前/改后 sha16 + 字节（逐面，节选；完整表在 JSON 里）

格式：`f<i> 旧像素sha16 (旧字节) → 新像素sha16 (新字节)`

```
1110165/glazed_patio (dds sha16=3c06f63dc94ed8f7)
  f0 49777f8a720318a1 (37003B) → 49777f8a720318a1 (37003B)   mean|Δ|=0.0000   ← 未变
  f1 d36c73f47d87a5c3 (41219B) → 059b79e93dd75bbc (40969B)   mean|Δ|=29.1525
  f2 dc347fc6e24754fa (41444B) → ff6bfce3167b6232 (37987B)   mean|Δ|=28.4592
  f3 34f64d905cdf4a1a (39608B) → c0a558182785f9de (37506B)   mean|Δ|=29.7301
  f4 5e1d44beee6978a2 (37452B) → 48a3ffbc82e4e2bc (41541B)   mean|Δ|=20.5350
  f5 e3a55133a288e778 (41504B) → c13ff76af2aece8f (36484B)   mean|Δ|=21.7614

1110152/qiangpi (dds sha16=173d52990b3ab836)
  f0 15beb9663c062eba (32213B) → 15beb9663c062eba (32213B)   mean|Δ|=0.0000   ← 未变
  f1 81884a00fbd008b4 (34858B) → 3355f34eeea9035d (28195B)   mean|Δ|=36.6896
  f2 5c0a1dc259022689 (29636B) → c8bf2d86fb46c1ec (32495B)   mean|Δ|=36.7060
  f3 8b3345f17c678603 (36022B) → 3b8b49746c36cee1 (20764B)   mean|Δ|=37.1137
  f4 a8575ea5d2bac74d (20856B) → b9e1c9b31b2ba422 (32369B)   mean|Δ|=44.5623
  f5 58d567231894d1b3 (32128B) → 275d383cdcd46fc6 (30113B)   mean|Δ|=44.4703

1110024/indoor (dds sha16=a464190b0febb360)
  f3 e45bde5ec6e50593 (23271B) → 3d3e2b7e99ddc808 (390B)     mean|Δ|=150.3877  ← 旧的 f3 是"带"，新的 f3 本身近似纯色
  f4 90968cf69e9a04d6 (392B)   → 9b204db6b0a38711 (18617B)   mean|Δ|=82.1506   ← 旧的 f4 只有 392 B（"带"几乎全被压掉）
```
> 旧的 `indoor_f4_m0.png` 只有 **392 B**、旧的 `indoor_f3_m0.png` 有 23271 B；新切后 f3 才是 390 B。
> 两侧都说明旧图内容是"小 mip 带"的产物，与真面无关。

## A.3 修改后的复检

* `fix_probe_faces` 重扫 **17/17 个 cube-dir 全部 `OK_face-major`**，`fm_max mean|Δ| = 0.0000`；
* 7 组错切 cube 的"新面 vs mip-major 切法"mean\|Δ\| 现在等于修改前的 `mm_mean`（17.33 ~ 80.71），
  说明新旧图确实互换了角色；
* 全部 `.dds` 长度校验通过（无 size mismatch）。

## A.4 A 段未做项 / 需 Lead 接手

1. **`faces_glob` 仍是不可消费写法（8 条 `{i}` + 4 条 `*`）** —— 在 `neox_material.json` 里，
   属 Lead 写域，**本子代理只登记不改**：
   | 文件 | 值 | 条数 | 匹配到的面文件数 |
   |------|----|------|-----------------|
   | `1110024\neox_material.json` | `src_cube/faces/gdansk_shipyard_buildings_f{i}_m0.png` | 5（prim0..4） | 6（文件在，但占位符不合法） |
   | `1110152\neox_material.json` | `src_cube/faces/qiangpi_f{i}_m0.png` | 2 | 6 |
   | `1110177\neox_material.json` | `src_cube/faces/fashion_qiangpi_f{i}_m0.png` | 1（prim2） | 6 |
   | `1110165\neox_material.json` | `src_cube/faces/qiangpi_f*_m0.png` / `glazed_patio_f*_m0.png` | 2 + 2 | 6 |

   判据：`1110129\neox_material.json` 的 `faces_glob_note` 已直证
   "原值 `src_cube/faces/qiangpi_f*_m0.png` 含 shell 通配 `*`（会 404），改为既定占位符写法"
   ⇒ `*` 与 `{i}` 同属不可消费写法。**A 段把面图切对了，但这些 glob 不改就等于视觉空操作。**
2. **未重切 m1..m7**：这 7 组的 faces 目录原本只发布 m0，本次维持同一发布口径
   （`1110171` / `1110171_cand` 的 `car_studio01`、`qiangpi` 已有 m1..m7，属他人写域，未动）。
   工具支持 `--mips`，需要时一条命令即可补齐。
3. **面序 ↔ 空间朝向未定证**：本次只保证"面号 ↔ 字节偏移"正确，未主张 `f0..f5` 与引擎
   `+X/−X/…` 的对应关系。
4. **`1110024/indoor` 没有被任何 `faces_glob` 引用**（只有 `gdansk_…` 被引用）；
   `1110024` 的 `indoor.dds` 仍留在盘上但六面无消费者 —— 属清单口径问题，登记不修。

---

# B 段 — 资产引用一致性体检（只报不改）

## B.1 扫描范围与规模

`08Lifeafter wiki\assets\3d\weapon_skin\**\*.json`（`*.json.bak_*` 的扩展名不是 `.json`，天然排除）：

* JSON 文件 **318** 个，**全部解析成功**（0 个解析失败）；
* 抽出**文件引用 2,284 条**，按类型：

| 引用类型 | 条数 |
|---------|------|
| wiki 资产引用（存在） | 848 |
| 游戏逻辑路径（容器内资产，磁盘本无对应文件，应查容器索引） | 806 |
| wiki 资产引用（**MISS，需关注**） | 182 |
| 无法判定（MISS，需人工看） | 448 |

> 这条分类是有意加的：`logical_path` / `mesh_path` / `gim_path` / `MtlIdx` 这类字段装的是
> **游戏内逻辑路径**（`weapon\skin\…`、`res\…`），磁盘上本来就没有同名文件 ——
> 把它们算成 MISS 会产生上千条噪声。真正要关注的是 182 条 wiki MISS（去重后 151 条）。

## B.2 逐条明细（完整 2,284 条在 JSON）

`{文件, 字段, 引用值, 存在?, 归属写者}` 逐条落盘于
`BUGFIX_asset_refs_20260918.json` 的 `refs[]`；下面只列需要关注的部分。

### B.2.1 点名登记：`viewer.js` 硬编码 `src_tex/gpk_1229.png`

* 位置：`assets\weapon_skin_viewer.js` **第 1540 行**
  `const detailTex = tex('src_tex/gpk_1229.png', false);`
* 解析式：`L920 const base=state.modelDir;` + `L943-948 tex(f) → TL.load(base + f)`
  ⇒ 实际请求 `assets/3d/weapon_skin/<当前皮肤>/src_tex/gpk_1229.png`
* 磁盘事实：该文件**只存在于 `1110171` 与 `1110171_cand`**（各 1,576,284 B）；
  其余 **36 个皮肤目录均无此文件** ⇒ 载入那些皮肤时 404。
* 归属写者：**viewer.js 写者（本子代理禁改，只登记）**。
* 同类（同文件内其它硬编码 `src_tex`）：`L2452` 的 `012_b_m.png` / `012_a.png` / `010_b_m.png`、
  `L3769` 的 `010_a.png` —— 同样只在 `1110171` / `1110171_cand` 存在（各缺 36 个皮肤）。

### B.2.2 过期/失效说明文件（22 个，只登记）

| 文件 | 字节 | mtime |
|------|------|-------|
| `1110146\_build\BLOCKED.md` | 16481 | 2026-09-18 22:09:06 |
| `1110145\_build\REPACK_014_PROVENANCE.md` | 1881 | 2026-09-18 02:05:06 |
| `1110171\INVALIDATED_artificial_chain.json` | 1874 | 2026-09-16 19:04:52 |
| `1110171_cand\neox_material.swapped.json` | 37420 | 2026-09-17 22:38:44 |
| `1110177\_build_t5\` 下 18 个 `_t5_*.json` / `neox_material.before_cp.json` / `_keep_v1.json` / `texmap_029_glb.json` | 328 ~ 23064 | 2026-09-17 21:24 ~ 23:29 |

> 你点名的 `1110171\_build\BLOCKED.md` **不存在**（`1110171` 下没有 `_build` 目录）；
> 实际存在的是 `1110146\_build\BLOCKED.md`（16481 B，2026-09-18 22:09）—— 已登记。
> `INVALIDATED_artificial_chain.json` 从名字看是**主动作废**的产物，一并登记不删。

### B.2.3 其它需要关注的 wiki MISS（去重 151 条，节选）

| 文件 | 字段 | 引用值 | 备注 |
|------|------|--------|------|
| `1110115\viewer.json` | model | `skin_2003_013.glb` | 该皮肤目录下无此 glb |
| `1110152\effects.json` / `viewer.json` | png | `2ea72d9f3d7c3ab2.png`、`345dd407ae890e2d.png`、`a74377f1fba7defe.png` | 哈希命名的特效帧，盘上无（effects.json 属禁改写域） |
| `1110165\_build\BINDING_13.json` | local_file | `src_tex/165_*.png` × 13 | `_build` 暂存清单，非交付清单 |
| `1110171\INVALIDATED_artificial_chain.json` | file | `approx_albedo_010.png` | 文件已主动作废 |

（其余 448 条"无法判定"多为上述 `_build` / 暂存 JSON 里的中间产物名，已逐条落盘，未逐条解读。）

## B.3 B4 — `src_cube` 下明显损坏/半截的 PNG

**扫描结果：0 个**（无 0 字节、无不可解码的 PNG）⇒ **本段无需执行任何修复**。

顺带登记 `src_cube` 下 3 个异常小文件（非 PNG，无内容可切，**只登记不删**）：

| 文件 | 字节 | 判定 |
|------|------|------|
| `1110171\src_cube\faces\_t.dds` | 132 | 仅 DDS 头 128 B + 4 B，无任何 mip 数据；非 cubemap，不参与切面 |
| `1110171\src_cube\faces.bak_20260917_081053\_t.dds` | 132 | 同上（历史备份目录内） |
| `1110171_cand\src_cube\faces\_t.dds` | 132 | 同上 |

---

# C 段 — 把取证脚本固化为工具

## C.0 交付的 4 个新文件

| 文件 | 字节 | sha16 |
|------|------|-------|
| `01拆包器本体\工具库\06_皮肤定位链\gpk_npk_index.py` | 39000 | `4743addc0035a20b` |
| `01拆包器本体\工具库\06_皮肤定位链\resolve_declared_paths.py` | 16172 | `90ced44342b2869c` |
| `01拆包器本体\工具库\06_皮肤定位链\cube_faces_export.py` | 22805 | `da513e318545483c` |
| `01拆包器本体\工具库\06_皮肤定位链\README_新增工具.md` | 13153 | `76c569f3cefc200f` |

（`改前` = 不存在，均为新建；上表"改后"值见 §交付校验。）

三个工具均：支持 `--help`、中文 docstring、启动强制 UTF-8、退出码语义明确、
默认只读（写盘要显式开关）、不照抄临时脚本的硬编码路径（全部参数化，
`--res-root` / `--fpk-index` / `--out` / `--json` 等）。

## C.1 `gpk_npk_index.py`

### 实跑命令与输出摘要

```bash
python gpk_npk_index.py --selftest
python gpk_npk_index.py --count --quiet --reconcile --json …\BUGFIX_index_counts_20260918.json
python gpk_npk_index.py --find "common\env_map\qiangpi.cube"
python gpk_npk_index.py --quiet --out …\INDEX_ALL_containers_20260918.json --tsv …\INDEX_ALL_containers_20260918.tsv
```

`--selftest`（用前序会话已直证的 `res.npk` 行号做 ground truth）**3/3 PASS**：
```
common\env_map\qiangpi.cube          fid=D763973EACDC554E row=14213  期望=14213  PASS
common\env_map\car_studio01.cube     fid=B83FF34C105E8150 row=12100  期望=12100  PASS
common\env_map\fashion_qiangpi.cube  fid=46AD501D4C9147E9 row=4620   期望=4620   PASS
res_npk_entries = 16905
```

`--count --reconcile`：
```
.gpk   91 个容器  4,579,785 条        （56 res 族 + 35 gres 族）
.fpk   64 个容器  2,012,297 条        （源自 fpk_fid_index.json）
.npk  158 个容器  1,568,681 条
容器行数合计 313 个容器  8,160,763 条
未解析容器：0 个
.gpk 去重 fid 2,537,083 ; .fpk 去重 fid 2,069,650 ; .npk 去重 fid 1,145,522
交集：fpk∩gpk 1,986,863 ; fpk∩npk 63,899 ; gpk∩npk 9,858 ; 三者 6,546
★ 全量条目数（去重并集）= 3,698,181   重复率 54.68%
```

`--find`（顺带独立复现了前序证据里的 npk 行号）：
```
common\env_map\qiangpi.cube ⇒ HIT
   res.gpk  gpk row=4501  off=524927644 packed=348117 decoded=524408 flag=12 fid=D763973EACDC554E
   res.npk  npk row=14213 off=1710400516 packed=446736 decoded=524408 flag=2  fid=D763973EACDC554E
```

### ★ 与 3,336,339 的对账：**逐位复现**，差额已完全归因

`--reconcile` 复刻历史口径并断言：
```
老口径并集 = 3336339     修正后并集 = 3698181     差 +361842
公式 union( fpk_fid_index(64 fpk) ∪ 91 .gpk 按 n=u32@20 读 ∪ gres 只读第 0 块 ∪ 158 .npk )
⇒ 老口径 恰等于 3,336,339   （与 --expect 3336339 完全一致，退出码 0）
```

差额**全部来自 `.gpk` 侧的两个口径问题**，与 fpk/npk 无关：

1. **每个 `.gpk` 多算 1 行**：条目数字段存的是 `entry_count + 1`。
   实测 **56/56** 个 res 族 gpk 的"第 n 行"`flag` 是解密垃圾（如 `0x75241C13`、`0x0C0F9D42`），
   而"第 n−1 行"完全合法且 **0/56** 越界；同时 `block_size == filesize − 16` 对 56/56 成立。
   ⇒ 91 个容器各多出 1 个假 fid。
2. **gres 族（35 个）不是"头 + 单表"**，而是 **16 B 头 + 块链**（块数 5~164，每块独立 AES 表、
   独立 32 B 行表）。老口径只读文件偏移 64 处的第 0 块 = 34,917 行，**漏掉后续块**。
   gres 真实全块 = **2,476,866 行 / 1,884,746 个不同哈希**；`off == 1`（去重到别的卷）95,xxx 行。

两族**同一个块链格式**（gres = 多块，res = 1 块），所以本工具用同一个 `_gpk_blockchain` 读取；
`--reconcile` 下 `res-gpk 唯一 2,102,919 ; gres 第0块唯一 34,703 ; 每容器假行 91 个 ;
gres 全块唯一 1,884,746`，`3,336,339 + 361,842 = 3,698,181` 闭合。

### 索引落盘

```
out: 03拆包产物\_target_1110171\INDEX_ALL_containers_20260918.json
tsv: 03拆包产物\_target_1110171\INDEX_ALL_containers_20260918.tsv
```
（文件大小与 sha16 见 §交付校验。）

## C.2 `resolve_declared_paths.py`

### 实跑命令与输出摘要

```bash
python resolve_declared_paths.py "03拆包产物\weapon\001265.c159" "…\001223.c159" "…\003996.c159" \
  "…\000334.c159" "…\000654.c159" "…\002731.c159" "…\001631.c159" "…\001386.c159"
# 以及带 --variants --no-detail --json 的混合批次（含 3 个 .sfx）
```

**批次 1（8 个皮肤 c159）**：抽出 82 条去重路径（原始出现 108 次）
```
顶层目录   扩展名   声明  HIT  MISS   命中率
common     .cube      6    6     0   100.0%
common     .tga      12    3     9    25.0%
weapon     .tga      63    0    63     0.0%
character  .tga       1    0     1     0.0%
合计 82 声明 / 9 HIT / 73 MISS = 11.0%
```

**批次 2（3 个 c159 + 3 个 sfx，`--variants`）**：69 条去重路径
```
common   .cube   4/4 100%     common  .tga  10/10 100%
effect   .gim   24/24 100%    effect  .sfx   2/2  100%
effect   .tga    0/5   0%     weapon  .tga   0/23   0%     character .tga 0/1 0%
合计 69 声明 / 40 HIT / 29 MISS = 58.0%
索引：流式扫过 249 个容器，失败 0 个
```

> 这张矩阵本身就是结论：**`common\env_map\*.cube` 与 `effect\*.gim/.sfx` 按名 100% 命中**，
> 而 **`weapon\skin\*\textures\*.tga` 63/63 全 MISS、`effect\*.tga` 5/5 全 MISS** ——
> 与 README「已知边界」里"皮肤/特效贴图按名 0 命中"完全吻合，
> 佐证这类资产进的是匿名容器，只能靠内容指纹定位。

## C.3 `cube_faces_export.py`

### 实跑命令与输出摘要

见 A.1（本轮真正的修复就是用它做的：干跑 → `--apply --backup-tag mangled` → 复检）。
另外单独验证了 `--mips` 与取证模式：

```bash
# --mips：face × mip 全导出（6 面 × 8 级 = 48 张），自检通过
python cube_faces_export.py "…\1110165\src_cube\qiangpi.dds" --out "%TEMP%\fix_mips_demo" --mips --apply
   → 面写盘 48，面变更 0，备份 0；自检：六面互异=True 与 DDS 字节逐字节吻合=True

# --layout mip-major：复现历史错误切法（仅取证）
# --ref-dir：跨皮肤逐像素对照（A.2 证据(a) 即由它产出）
```

复检（`--dry-run` 扫全部 17 个 cube-dir）：**17/17 `OK_face-major`，max mean\|Δ\| = 0.0000**。

## C.4 `README_新增工具.md`

写清 3 个工具的用途、真实用法示例、实测结果，以及**已知边界**：

* 容器只存哈希不存名字 ⇒ `--find` 的 MISS 只证明"这些候选名都不在"；
* **皮肤贴图 / 特效贴图按名 0 命中是预期**（63/63 MISS 实测），而 `common\env_map\*.cube` 6/6 HIT；
* gres 的 `flag==0` 载荷是**明文**，不要再 AES 解密；
* `GpkIndex` / `unpack_entry` / `parse_gpk_entries` 的既有缺陷（见下）；
* 8 个 `faces_glob` 的不可消费写法；
* 面序 ↔ 朝向未定证；
* `fpk_fid_index.json` 里含 `res\ui.npk` 的行，本工具已剔除避免重复计数。

## C.5 ★ 顺带查出的「既有代码缺陷」（**未改**，不在本子代理写域）

| 位置 | 问题 | 证据 | 影响 |
|------|------|------|------|
| `06_皮肤定位链\locate_skeleton.py` `GpkIndex.__init__` | `n = u32@20` **多 1 行**（字段是 `entry_count+1`）；且只看 gres 的第 0 块 | 56/56 res 族 gpk 的"第 n 行"flag 非法、"第 n−1 行"合法 | 每个 gpk 索引出一条解密垃圾；gres 大部分条目缺失 |
| `01_核心解包器\lifeafter_unpacker_full.py` `parse_gpk_entries` | 同上 off-by-one | 同上 | 同上 |
| `10_应用核心\toolkit_core\resource_resolver.py` `unpack_entry` | `flag == 0 → aes_ecb(packed)` 对 **gres 族**是错的（gres 的 flag-0 载荷本就是明文） | `Documents\gres\0000.gpk` flag-0 条目直接是可读 GBK 文本 / 明文 DDS 魔数 | 会损坏 gres 侧全部 raw 条目 |
| 8 处 `neox_material.json` 的 `faces_glob` | `…_f{i}_m0.png`（8 条）/ `…_f*_m0.png`（4 条）不可消费 | `1110129` 的 `faces_glob_note` 已直证 `*` 会 404 | 面图切对了也不被消费 |
| `assets\weapon_skin_viewer.js` L1540 | 硬编码 `src_tex/gpk_1229.png`，只在 1110171 存在 | 其余 36 个皮肤目录无此文件 | 每次载入 404 |

---

# 未做项与原因（汇总）

| # | 未做项 | 原因 |
|---|--------|------|
| 1 | 8+4 处 `faces_glob` 归一化为 `{0..5}` | 在 `neox_material.json` 里，属 Lead 独占写域（本任务明令禁改）。**这是 A 段生效的前置条件，建议优先处理。** |
| 2 | 修 `GpkIndex` / `parse_gpk_entries` 的 off-by-one | 在 `06_皮肤定位链` 与 `01_核心解包器` 的**既有文件**里，本任务明令"不得改动该目录下任何既有文件"；且会影响其他并行工作。已给出一行修法（`n = u32@20 - 1` + 走块链）。 |
| 3 | 修 `resource_resolver.unpack_entry` 对 gres flag-0 的误 AES | 同上（既有文件、跨写域）。 |
| 4 | 删掉 `src_tex/gpk_1229.png` 硬编码 / 补 36 个皮肤的该文件 | `viewer.js` 禁改写域；补文件也不合适（该资产是 1110171 专属候选）。只登记。 |
| 5 | 清理 22 个过期/失效说明文件 | 非本子代理写域；且 `INVALIDATED_*` 属主动作废记录，删除可能损失证据链。只登记。 |
| 6 | 重切 m1..m7 | 这 7 组原本只发布 m0，维持同一口径；工具已支持 `--mips`。 |
| 7 | cube 面号 ↔ 空间方向映射 | 源面序本身未定证，超出本任务范围；不猜。 |
| 8 | 修复 448 条"无法判定"MISS | 多为 `_build` / 暂存 JSON 的中间产物名，非交付清单；已逐条落盘待人工判。 |
| 9 | `1110115\viewer.json` 的 `model: skin_2003_013.glb` 缺失 | `viewer.json` 禁改写域。只登记。 |

# 卡点 / 需要 Lead 决策

1. **A 段的视觉效果取决于 `faces_glob`**：`1110024`(5)、`1110152`(2)、`1110165`(4)、`1110177`(1)
   共 12 条 glob 不可消费。面图已正确，但消费端拿不到 —— 需 Lead 侧改 `neox_material.json`。
2. **`3,336,339` 这个基准数本身含 2 个口径错误**（91 个假行 + gres 只算 1/5~1/164 的块）。
   若后续以它做验收基线，会系统性少算 361,842 条。建议改用 `3,698,181`（去重并集，全块）。
3. **gres 的 `off == 1` 跨卷引用**（载荷在别的卷）本工具照常入库但不解析；
   若要真正取内容需要跨卷解析（本次未做，属新增能力而非缺陷修复）。

---

# 交付校验（sha16）

| 交付物 | 字节 | sha16 |
|--------|------|-------|
| `03拆包产物\_target_1110171\BUGFIX_report_20260918.md` | 本文件 | 见文件末尾 |
| `03拆包产物\_target_1110171\BUGFIX_cube_faces_20260918.json` | 22847 | `26d7a925c737fb42` |
| `03拆包产物\_target_1110171\BUGFIX_asset_refs_20260918.json` | 1004939 | `f4e8458e8b3a4896` |
| `03拆包产物\_target_1110171\BUGFIX_declared_paths_20260918.json` | 50714 | `0476509266d0d039` |
| `03拆包产物\_target_1110171\BUGFIX_index_counts_20260918.json` | 374154 | `5f99e79eab227deb` |
| `03拆包产物\_target_1110171\INDEX_ALL_containers_20260918.json` | 264390407 | `8ab6554e74a2494e` |
| `03拆包产物\_target_1110171\INDEX_ALL_containers_20260918.tsv` | 447109762 | `0588a201a00cd8f3` |
| `01拆包器本体\工具库\06_皮肤定位链\gpk_npk_index.py` | 39000 | `4743addc0035a20b` |
| `01拆包器本体\工具库\06_皮肤定位链\resolve_declared_paths.py` | 16172 | `90ced44342b2869c` |
| `01拆包器本体\工具库\06_皮肤定位链\cube_faces_export.py` | 22805 | `da513e318545483c` |
| `01拆包器本体\工具库\06_皮肤定位链\README_新增工具.md` | 13153 | `76c569f3cefc200f` |
| 备份（35 个 `*.bak_mangled_20260918_231623`） | 1089363 合计 | 见 `BUGFIX_cube_faces_20260918.json` 逐条 |

索引落盘校验：`json.load` 通过（5.3 s），`containers` 314 项、`rows` **6,148,466** 行，
`totals` 与 `--count --reconcile` 完全一致；`--find --index <TSV>` 复跑命中
`fashion_qiangpi.cube → res.npk row=4620`（与直证一致）、`glazed_patio.cube → res.npk row=9466`。

> 注：`INDEX_ALL_containers_*`（264 MB + 447 MB）是**运行产物**，不是工具本身。
> 若嫌占盘可安全删除，随时用
> `python gpk_npk_index.py --out <json> --tsv <tsv>` 重建（本次实测重建耗时约 12 分钟）。

---

# 收尾复检（重要：本轮有多个写者在并行改同一批文件）

复检时刻 2026-09-19 00:0x。期间检测到**其他写者**在并行修改：
`1110177\viewer.json`、`1110177\effects.json`、`assets\weapon_skin_sfx_adapter.js`、
`data\media\weapon_skin_media.{js,json}`、以及 `1110024/1110129/1110145/1110152/1110165/1110171/1110177`
的 `neox_material.json`（备份标签可见 `bak_rgbasha_*`、`bak_shabind_*`、`bak_ibl2_*`、`bak_fxwire3_*`、
`bak_sprhard_*` 等）。**这些改动均非本子代理所为**（本子代理只写了 `src_cube\faces\**` 下的 PNG 与备份）。

在上述并行写入之后重跑复检：

1. **A 段修复完好**：`fix_probe_faces` 重扫 **17/17 个 cube-dir 仍为 `OK_face-major`**，
   `fm_max mean|Δ| = 0.0000`，无 size mismatch ⇒ 我的重切面未被覆盖、仍与 DDS 一致。
2. **A 段未做项依旧存在**：`faces_glob` 仍是 **47 条中 12 条不可消费**
   （`1110024` 5 条 `{i}`、`1110152` 2 条 `{i}`、`1110177` 1 条 `{i}`、`1110165` 4 条 `*`），
   与 B 段扫描结果一致，尚未被并行写者归一化。
3. 本子代理**未**在任何时刻写入 `neox_material.json` / `viewer.json` / `effects.json` /
   `viewer.js` / `sfx_adapter.js` / `data\**`（写域合规）。
