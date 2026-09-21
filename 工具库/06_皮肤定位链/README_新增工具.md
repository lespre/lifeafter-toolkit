# 06_皮肤定位链 — 新增工具（2026-09-18 缺陷修复批次固化）

本目录本轮**新建** 4 个文件（不改动本目录任何既有文件）：

| # | 文件 | 作用 |
|---|------|------|
| 1 | `gpk_npk_index.py` | 313 个容器的全量条目索引 / 按候选名查找 |
| 2 | `resolve_declared_paths.py` | 从 `.c159`/`.sfx`/任意文件抽路径并逐条判 HIT/MISS |
| 3 | `cube_faces_export.py` | cubemap `.dds` → 6 张 mip0 PNG（face-major 真值切法）+ 自检 |
| 4 | `README_新增工具.md` | 本文件 |

**通用约定**：全部支持 `--help`；中文 docstring；启动即强制 UTF-8
（用 `sys.stdout.reconfigure`，**不**替换 `sys.stdout` —— 否则本模块被 `import` 时会因旧
wrapper 被 GC 而关掉调用方的 stdout）；失败语义见各自"退出码"；默认**只读**，写盘一律要显式开关。

---

## 1. `gpk_npk_index.py`

### 用途
把 `E:\mrzh` 下全部资源容器的**条目表**读成一个统一索引，并支持按路径名反查。
容器里**不存文件名、只存路径的 murmur3 双哈希**，所以"某资产在不在包里"只能靠
"候选名 → 哈希 → 查表"来判。

### 容器格式（本工具实测口径）
| 族 | 数量 | 格式 |
|----|------|------|
| `.gpk` res 族（`res\*.gpk` + 根 `res.gpk`） | 56 | 16 B 文件头 + 1 个 AES 块 |
| `.gpk` gres 族（`Documents\gres\*.gpk`） | 35 | 16 B 文件头 + **块链**（5~164 块，每块独立 AES 表） |
| `.fpk`（`res\*.fpk`） | 64 | 从既有 `03拆包产物\fpk_fid_index.json` 搬运，不重解析 |
| `.npk`（含 `Documents\` 下 5 个脚本包） | 158 | AES 头 `<QIIII>` + `48 B/行` 表 |

**GPK 统一块链布局**（res 族与 gres 族同一套，只是块数不同）：
```
文件头 16 B : [0]=0 ; [4]=block_count ^ 0x46475049 ; [8]=2 ; [12]=block_count
块 base B   : B+4  = entry_count + 1      ← 注意是 count+1，不是 count
              B+8  = block_size          （下一块 = B+block_size；末块为 0）
              B+48 : entry_count × 32 B 表，AES-ECB
              行 <8I> = (off, comp, dec, c1, c2, flag, hash_lo, hash_hi)
              载荷在 B+off，明文；off==1 表示去重到别的卷（gres）
统一 fid    : (hash_hi << 32) | hash_lo  = (murmur3(path,0x77777777)<<32)|murmur3(path,0x66666666)
```
`.npk` 行 `<QIIIIIi>` = `(file_id, offset, packed, decoded, c1, c2, flag)`，**file_id 用同一约定**，
所以三类容器可以共用一个 64 位 fid 做统一查找。

### 用法
```bash
# 对账（只读表，秒级~分钟级）
python gpk_npk_index.py --count --reconcile

# 建全量索引（流式写；JSON 紧凑数组 + 可选 TSV）
python gpk_npk_index.py --out INDEX.json --tsv INDEX.tsv

# 按候选名查找（不建索引也能查：流式只匹配查询集，低内存）
python gpk_npk_index.py --find "common\env_map\qiangpi.cube"
python gpk_npk_index.py --find "common/env_map/qiangpi.cube" --variants --deep-variants
python gpk_npk_index.py --find "xxx" --index INDEX.tsv      # 复用已建 TSV

# 约定自检（用 res.npk 已直证行号做 ground truth）
python gpk_npk_index.py --selftest
```

### 实测结果（2026-09-18，`E:\mrzh`）
```
.gpk   91 个容器  4,579,785 条（含 gres 全块）
.fpk   64 个容器  2,012,297 条（fpk_fid_index 搬运）
.npk  158 个容器  1,568,681 条
容器行数合计 313 个容器  8,160,763 条
去重并集（全量条目数口径）= 3,698,181    重复率 54.68%
交集：fpk∩gpk 1,986,863 ; fpk∩npk 63,899 ; gpk∩npk 9,858
```
`--selftest` 3/3 PASS：`common\env_map\qiangpi.cube` → res.npk row **14213**、
`car_studio01.cube` → **12100**、`fashion_qiangpi.cube` → **4620**（与前序会话直证行号一致）。

### 与历史数字 3,336,339 的对账（`--reconcile`）
老口径 = `union( fpk_fid_index ∪ 91 .gpk 按 n=u32@20 读 ∪ gres 只读第 0 块 ∪ 158 .npk )`
**= 3,336,339，逐位复现**。差额来源两处，都在 `.gpk` 侧：

1. **每个 `.gpk` 多算 1 行**：真实字段是 `entry_count+1`，多读到表尾紧邻 32 B 的 AES 解密垃圾。
   实测 56/56 个 res 族文件"第 n 行"flag 非法（如 `0x75241C13`）、"第 n−1 行"完全合法且 0/56 越界。
   ⇒ 91 个容器多出 91 个假 fid。
2. **gres 不是"头+单表"**：老口径只读偏移 64 处的第 0 块（34,917 行），
   漏掉后续块；gres 真实全块 = 2,476,866 行 / 1,884,746 个不同哈希。

修正后全量口径 = **3,698,181**。

### 已知边界
* **容器只存哈希不存名字** ⇒ `--find` 的 MISS 只证明"这些候选名都不在"，
  **不证明资产不存在**（可能进了匿名容器或打包时改了名）。务必配合 `--variants`。
* **皮肤贴图 / 特效贴图按名 0 命中是预期结果**：`.c159` 里声明 `weapon\skin\*\textures\*.tga`
  等 63 条全部 MISS（实测），因为这类资产进的是匿名 gpk；只能用"内容指纹 + 块定界"定位，
  不能按名查。`common\env_map\*.cube` 则 6/6 HIT —— 两类资产行为不同，不要外推。
* `flag` 语义：`0=原始`、`2=LZ4 block`、`12=zstd`。
  **gres 族的 `flag==0` 载荷是明文，不要再 AES 解密**（见下"既有代码缺陷"）。
* `.fpk` 完全依赖 `03拆包产物\fpk_fid_index.json`；该文件缺失则 fpk 族记 `unresolved`。
* `fpk_fid_index.json` 的 `fid2info` 里除 64 个 `.fpk` 外还含 `res\ui.npk`(57,353 行) ——
  本工具把它从 fpk 计数里剔除（否则与 npk 扫描重复计数），并在 `fpk_index_detail` 里单列。
* `--reconcile` 会额外常驻 4 个 ~2M 元素的集合，内存需求明显上升。

### 退出码
`0` 成功 / `1` 参数错 / `2` 容器全失败 / `3` 写盘失败 /
`4` 与 `--expect` 对账不符（`--reconcile` 下若老口径精确复现 `--expect` 则视为通过）/ `5` 查找 0 命中

---

## 2. `resolve_declared_paths.py`

### 用途
`*.c159`（材质/参数块）、`*.sfx`（特效轨道）等声明文件里写的是**逻辑路径**，
而容器只存哈希 ⇒ "声明了却没生效"必须靠哈希反查判。本工具：
**抽路径 → 逐条解析 → 按「顶层目录 × 扩展名」给命中矩阵 + 逐条 HIT/MISS**。

### 用法
```bash
# 基本：解析一批声明文件（自带流式索引，无需预建）
python resolve_declared_paths.py "03拆包产物\weapon\*.c159" --json RESULT.json

# 复用 TSV 索引（反复查更快）
python resolve_declared_paths.py a.sfx b.c159 --index INDEX.tsv

# 展开候选名变体（分隔符 / 大小写 / 去一层目录 / .tga↔.dds/.png）
python resolve_declared_paths.py x.c159 --variants --deep-variants

# 只要矩阵 / 只抽字符串（查抽取质量）
python resolve_declared_paths.py x.c159 --no-detail
python resolve_declared_paths.py x.c159 --dump-strings
```

### 实测结果（2026-09-18）
8 个皮肤 `.c159`（000334/000654/001223/001265/001386/001631/002731/003996）：
抽出 82 条去重路径，命中 9 条（11.0%）——
```
common   .cube   6 声明  6 HIT  100.0%
common   .tga   12 声明  3 HIT   25.0%
weapon   .tga   63 声明  0 HIT    0.0%
character .tga   1 声明  0 HIT    0.0%
```
加 3 个 `.sfx` 后（含 `effect\*.gim` 24 条）：
```
common   .cube   4/4 100% ; common .tga 10/10 100%
effect   .gim   24/24 100% ; effect .sfx 2/2 100% ; effect .tga 0/5 0%
weapon   .tga    0/23 0%  ; character .tga 0/1 0%
合计 69 声明 / 40 HIT / 29 MISS = 58.0%
```
`cube` 与 `effect/.gim/.sfx` 全命中、`weapon\skin\*\textures\*.tga` 全不命中 —— 与第 1 节的
边界结论互证。

### 已知边界
* **不理解 `.c159`/`.sfx` 语法**：只抽"像路径的可打印串"（含分隔符 + 扩展名在白名单），
  可能抽到注释/拼接片段；每条都带**原始字节偏移**便于人工复核。
* `--ext` 可覆盖扩展名白名单；给 `--ext ""` 关闭过滤（噪声会大幅上升）。
* 编排含义：**MISS 不是工具故障**，不影响退出码（`0`）。
* 只读，不改被检文件。

### 退出码
`0` 完成 / `1` 参数错 / `2` 输入不可读 / `3` 写盘失败 / `4` 索引完全不可用

---

## 3. `cube_faces_export.py`

### 用途
把 `B8G8R8A8_UNORM` 的 Neox cubemap `.dds`（128²、8 级 mip、`caps2` 含 `DDSCAPS2_CUBEMAP`）
按 **face-major** 切成 6 张 mip0 PNG（BGRA→RGBA、保 alpha），供 viewer 的 `faces_glob` 消费；
可选 `--mips` 逐级导出；**自带自检**。

### 为什么默认 face-major
已定证：面 i 的 mip 链起点 = `128 + i × Σ_k max(1,128>>k)²×4 = 128 + i × 87380`。
历史提取链误按 mip-major（面 i 偏移 `128 + i×65536`）读 ⇒ 面 0 侥幸正确，
面 1..5 变成"上一面的小 mip 带（21844 B ≈ 42.66 行）+ 真面顶部（43692 B ≈ 85.34 行）"
的**分带拼接**。

### 用法
```bash
# 干跑（默认）：只报差异，不写盘
python cube_faces_export.py "…\src_cube\*.dds"

# 正式导出；覆写旧 PNG 前先备份为 <原文件名>.bak_mangled_<时间戳>
python cube_faces_export.py <dds> --out <faces_dir> --apply --backup-tag mangled

# 连逐级 mip 一起导出
python cube_faces_export.py <dds> --out <faces_dir> --mips --apply

# 跨皮肤对照（可给多个）：要求逐面 mean|Δ|=0.0000 且像素 sha16 全等
python cube_faces_export.py <dds> --ref-dir <另一皮肤 faces 目录> --apply

# 复现历史错误切法（仅取证）
python cube_faces_export.py <dds> --layout mip-major --dry-run
```

### 自检口径（每次运行都做）
1. **六面互异**：6 张 m0 的像素 sha16 两两不同；
2. **与 DDS 字节逐字节吻合**：把 PNG 像素按 RGBA→BGRA 还原，与该面在公式偏移处的
   DDS 原始字节**完全相等**（不是"近似"）；
3. **旧 vs 新 mean|Δ|**：量化"旧图错的幅度"；
4. **`--ref-dir` 跨皮肤全等**（可选）；
5. 写盘后回读校验（PNG 往返一致）。

### 实测结果（2026-09-18）
修复 7 组错切 cube（9 个 cube-dir / 6 个皮肤）：
```
1110024/indoor                                  旧vs新 mean|Δ| 70.43/81.15/150.39/82.15/100.13 (f1..f5)
1110024/gdansk_shipyard_buildings               23.77/36.23/40.38/23.77/28.48
1110145/bg61f_light_spherereflectioncapture_1   21.94/22.23/17.75/18.71/23.34
1110146/glazed_patio                            29.15/28.46/29.73/20.54/21.76
1110152/qiangpi                                 36.69/36.71/37.11/44.56/44.47
1110165/bg61f_light_spherereflectioncapture_1   21.94/22.23/17.75/18.71/23.34
1110165/glazed_patio                            29.15/28.46/29.73/20.54/21.76
（f0 全部 mean|Δ|=0.0000 —— 面 0 在两种切法下同址，正是"面 0 侥幸正确"的量化证据）
```
重切 42 张面 PNG（35 张内容变化），自检全通过；`cube_faces_export.py --dry-run` 复扫
**17/17 个 cube-dir 均 face-major 吻合（max mean|Δ| = 0.0000）**。

### 已知边界
* **只保证"面号 ↔ 字节偏移"正确，不主张朝向正确**：cube 面号与引擎采样约定
  （+X/−X/…）的对应仍未定证。
* **拒绝瞎切**：默认要求文件长度**恰好** `128 + 6 × 87380`、方形 2 次幂、cubemap 标志、
  `B8G8R8A8`（fourcc=0 且 32 位）。不符则报 `dds_rejected` 并**不切任何面**（退出码 2）。
* 非方形 / 非 2 次幂 / 非该像素格式一律不解（不猜）。
* 不改 DDS、不改 manifest（`faces_glob` / sha256 回填属 Lead 写域）。
* `--layout mip-major` 仅供取证复现，**不要用于交付**。

### 退出码
`0` 成功 / `1` 参数错 / `2` DDS 被拒 / `3` 自检失败 / `4` 写盘失败

---

## 附：本轮顺带查出的「既有代码缺陷」（**未改**，因不在本子代理写域）

| 位置 | 问题 | 证据 | 影响 |
|------|------|------|------|
| `06_皮肤定位链\locate_skeleton.py` 的 `GpkIndex` | `n = u32@20` 比真实条目数**多 1**（该字段是 `entry_count+1`） | 56/56 res 族 gpk 的"第 n 行"flag 非法、第 n−1 行合法 | 每个 gpk 索引出一个解密垃圾条目；且只读 gres 的第 0 块 |
| `10_应用核心\toolkit_core\resource_resolver.py` 的 `unpack_entry` | `flag == 0 → aes_ecb(packed)` 对 **gres 族**是错的（gres 的 flag-0 载荷本就是明文） | `Documents\gres\0000.gpk` 的 flag-0 条目直接是可读 GBK 文本 / DDS 魔数 | 会损坏 gres 侧全部 raw 条目 |
| `01_核心解包器\lifeafter_unpacker_full.py` 的 `parse_gpk_entries` | 同 `GpkIndex` 的 off-by-one | 同上 | 同上 |
| 8 个 `neox_material.json` 的 `faces_glob` | 2026-09-18 仍有 12 条不可消费写法：`…_f{i}_m0.png`（8 条）/ `…_f*_m0.png`（4 条） | `1110129/neox_material.json` 的 `faces_glob_note` 已直证 `*` 会 404 | 面图切对了也不会被消费 |
| `assets\weapon_skin_viewer.js` L1540 | 硬编码 `tex('src_tex/gpk_1229.png')`，而该文件只在 `1110171` / `1110171_cand` 存在（`tex(f)=TL.load(state.modelDir+f)`） | 其余 36 个皮肤目录均无此文件 ⇒ 404 | 每次载入 404；属 viewer.js 写域 |

以上问题本批次**只登记不修改**（写域边界见
`03拆包产物\_target_1110171\BUGFIX_asset_refs_20260918.json` 的 `writer_attribution_rule`）。
