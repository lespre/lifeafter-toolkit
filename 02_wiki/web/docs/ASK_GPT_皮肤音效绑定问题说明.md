# 求助：明日之后（LifeAfter / NeoX 引擎）拆包 —— 皮肤 ↔ 音效 归属关系求解

## 0. 一句话卡点
音效**找得到、放得出**；皮肤**信息齐全**；但两边**没有共同键**可以机械 join ——
音效侧是**内部代号**（`yongtandiao`、`jinwu`），皮肤侧是 **stem**（`skin_1003_010`），
而唯一同时带皮肤名的 `.sfx` 文件（`fx_skin_1003_010_jisha_01.sfx`）**找不到本体**，且它出现的引用处**没跟包内条目号绑定**。

---

## 1. 目标
给图鉴里 100+ 个武器皮肤（stem 形如 `skin_1003_010`）**自动、机械地**找到其音效（WAV），
不靠人工听音、不靠猜内部代号、不做实机截图。

## 2. 环境与工具（已有，均可用）
- 客户端根目录 `E:\mrzh`（**只读**，不注入、不改游戏）
- 容器：
  - `E:\mrzh\res\weapon.gpk` 1.52 GB / 51,665 条目
  - `E:\mrzh\res\sound.gpk` 1.23 GB
  - `E:\mrzh\res\effect_01.gpk`（XML 条目 38,597 个）、`effect_02.gpk`（3,049）、`effect_cache.gpk`（99,801）
  - `E:\mrzh\res\utility.gpk` 21,426 条目；`ui.npk` 3.33 GB；`model_*.gpk` 共 17 个包 / 231,887 条目
  - `E:\mrzh\Documents\gres\*.gpk`（35 个）
  - `E:\mrzh\Documents\script.py314.lc.npk`（188,306,920 B，105,777 条目，sha `508bb5bd…`）
- 自写工具（Python）：`lifeafter_unpacker_full.extract_gpk(容器, 输出目录)`、`extract_fsb(fsb, 输出目录)`（FSB5→WAV 已验证）
- 依赖：`texture2ddecoder`（BC7）、`Pillow`、`numpy`、（贴图侧另有 `fsb5` 库）

## 3. 已实证的事实（逐条可复现）

### 3.1 包内条目**完全匿名**
- **GPK**：解包出来的条目名是**序号**（例：`037318.bin`），没有原始路径；条目内 `c1/c2` 字段是**内容指纹**（Murmur/CRC/FNV/djb2 × 各种编码全部 0 命中，不是路径哈希）。
- **NPK**：条目带 64 位 `file_id` = 双 Murmur3(路径, seed 高 `0x77777777` / 低 `0x66666666`) ⇒ 有路径字典时**可算**；但 GPK **没有**这个字段。

### 3.2 `.fev` = FMOD 工程文件（在 `sound.gpk` 里，扩展名被解成 `.riff`）
- 文件头：`RIFF <size> FEV FMT ... LIST ... PROJOBCT`
- 内含 **20,995 条样本名**（例 `sample/weapon/huitailang_yongtandiao/yongtandiao_hit1.wav`）与**事件名**
- 音频数据在**同包的 1,068 个 FSB5 音库**里（FSB5 → WAV 已跑通，VORBIS）

### 3.3 `.c159` = 带**明文段名**的序列化文档（magic `c1 59 41 0d`）
- 头部：`+0 magic | +4 u32 文件总长 | +8 u32 0 | 随后字段名表（NUL 分隔 ASCII）| 再后带 tag 的值流`
- 值流 tag（实证）：`0x03 <u8 01> <ASCII 字符串>`、`0x06 <u8 计数> <u8 03> <每项 u32 0 + float32×3>`、`0x07 <名>`、`0x08 <true/false>`
- `weapon.gpk` 中与 `skin_1003_010` 相关的 13 条 `.c159` 里读出：
  - 模型路径 `weapon\skin\skin_1003_010\skin_1003_010_lod01.gim`（及 lod02/lod03）
  - 子网格名 `skin_1003_010_0` / `_1` / `_2`
  - 字段：`BoundObject / Lod1..Lod4 / Lods / NeoX / Object / Openworld / Socket_0..Socket_6 / Sockets / Sub0..2 / SubMesh / BindType / BoundingCenter / BoundingHalf / BoundingInfo / CompatibleMask / Dist / MatrixToBone / MeshSortMethod / ModelSceneFlag / MtlIdx / MustShow / Name / Path / ReplaceLodLevel / TangentEnable / Version`（共 38 个）
  - 包围盒明文：`(0,0.3,1.7),(0.33,1.26,2.47),2.628`
  - 事件名：`fx_idle_01` / `muzzle_fire` / `sound` / `pifuguashi` / `hongwai`
  - 动画事件轨：`EventTrack_weapon_1003_11_01`、`EventTrack_weapon_1001_10_01`、`EventTrack_weapon_2003_91_bms_idle_01`
- 音效侧：`utility.gpk` 的 `021165.c159` = 音效描述符，含
  `effect\fx\weapon\skin\skin_1003_010\fx_skin_1003_010_hezi.sfx`

### 3.4 effect 包里的 FxGroup XML（**明文**，两类条目分开存放）
- **特效组**（例 `037300/037305/037315/037316/037317/037319/037320.bin`）：
  ```xml
  <SfxName = "effect\fx\weapon\skin\skin_1003_010\fx_skin_1003_010_jisha_01.sfx">
  ```
  → **带皮肤名**
- **音效组**（例 `037318.bin`，678 B，全文只有这些）：
  ```xml
  <FxGroup>
    <FxSoundEventDrive Name="L_fmod音效" FxLifeSpan="1.186"
        FileName  = "sound\g66_weapon.fev"
        EventName = "g66_weapon/202606_yongtandiao/yongtandiao_hit"
        UseFmodSetting="TRUE" ...>
  ```
  → **带音效事件，不带皮肤**

---

## 4. 卡点（精确定义）
**缺「皮肤 stem ↔ 音效事件」的对应表。**
1. 音效事件名是**内部代号**（`yongtandiao`、`huisexieyi`、`jinwu`），**不是**皮肤 stem；皮肤行/`.c159` 里也**没有**代号字段。
2. 唯一同时带皮肤名的键是 `.sfx` **逻辑路径**（`effect/fx/weapon/skin/skin_1003_010/fx_skin_1003_010_jisha_01.sfx`）。
   - 它出现在 FxGroup 的 `SfxName` 字段里（**明文**）；
   - 但**没告诉**我们"哪个包内条目号 = 那个 `.sfx`"；
   - 而 `.sfx` **本体**在 `effect_01/02/cache.gpk`、`script.py314.lc.npk`、`utility.gpk`、
     `model_*.gpk`(17 GB / 231,887 条目)、`gres/*.gpk` 里**都搜不到**
     （搜字符串 `fx_skin_1003_010` 与代号 `yongtandiao` 均 **0 命中**）。
3. ⇒ 目前只能靠**条目编号相邻**做启发式配对，会串到无关事件组（`monster_*` / `object` / `car*`），**不可靠**。

---

## 5. 已排除（**请勿重复建议**）
| 尝试 | 判据 | 结果 |
|---|---|---|
| 在**压缩容器原始字节**里搜明文 | 字符串匹配 | 必然 0 命中（必须先解包再搜） |
| `.mesh`（`weapon.gpk` 11,037 个，magic `34 80 C8 BB`）顶点直排 float32 / half / int16 / int8 | 法线模长 ≈ 1.0 | **全部 0** |
| int16/int8 量化顶点 | \|n\| ≈ 32767 / 127 | 最好 16% 误差，不成立 |
| 按 `.c159` 明文包围盒的 **float32 字节**在 17 个 `model_*.gpk`（231,887 条目）反查 | 精确字节匹配 | **0**（几何非裸 float，已量化） |
| 包围盒**比值**判据扫 `.mesh` | 尺度无关比值 | **有假阳性**（同批数据既比值吻合又给出 ±7000 的荒谬尺度）⇒ 不可单独用 |
| `.sfx` 本体搜索（多个容器） | 字符串 | 0 命中 |

---

## 6. 想问的问题
1. **NeoX / 明日之后 的 `.sfx` 文件是什么格式？通常存在哪个容器？**
   还是说它根本没有实体文件，而是运行时用 `SfxName` 的路径去 `.fev` 里按名查找事件？
2. **`.fev` 里的事件组名规则**：`g66_weapon/202606_yongtandiao/yongtandiao_hit` —— 事件组 `202606_yongtandiao`
   与音库目录 `sample/weapon/huitailang_yongtandiao/` 的对应规则是什么？
   客户端里是否存在一份**明文的「代号 ↔ 皮肤 ID」表**（可能在哪个包里）？
3. **能不能从"资源引用图"反推 GPK 条目号**？即：已知逻辑路径 `effect\fx\weapon\skin\skin_1003_010\x.sfx`，
   在**条目匿名**的 GPK 里怎么定位到它对应的条目？（GPK 是否有内嵌的目录表 / 哈希索引 / 文件名表？）
4. **包内分组结构**：`effect_01.gpk` 里"引用皮肤的组"与"纯音效组"是**分开的条目**、编号**相邻** ——
   有没有可靠的**包内隐式文件系统结构**（目录树 / 批次边界 / 条目标签）能界定"一个武器的特效包"？
   也就是说，除了"编号相邻"，还有没有别的结构性依据可以判定"这些条目同属一个武器"？

---

## 7. 可验证的确证样本（人工听感确认 ✅）
| 皮肤 | 皮肤侧键 | 事件 | 音库目录 | 产物 |
|---|---|---|---|---|
| 光影咏叹调 | `skin_1003_010`（id 1110171） | `g66_weapon/202606_yongtandiao/yongtandiao_hit` | `sample/weapon/huitailang_yongtandiao/` | 15 个 WAV ✅ |
| 金乌负日 | 子网格名 `jinwu_01_0/1`（id 1110142） | —（子网格名即代号，直接匹配音库目录） | `sample/weapon/jinwu_20260115/` | `000880.fsb` → 15 WAV ✅ |

---

## 8. 附：具体数值
- `sound.gpk`：`.fev` 样本名 **20,995** 条；`sample/weapon` 下 **116** 个音库目录；FSB5 音库 **1,068** 个
- `effect_01.gpk`：XML 条目 **38,597** 个（特效组 / 音效组分属不同条目）
- `weapon.gpk`：`.c159` **35,275** 个（子网格名多为 `skin_XXXX_YYY_N`，仅极少数如 `jinwu` 带代号）；`.mesh` **11,037** 个；`.dds` 4,948 个
- `weapon.gpk` 中 `skin_1003_010` 相关条目：`001209/001211/001212/001214/001215/001217/001218/001220/001221/001223/001263/001265/001267.c159`（13 条）
- 数据源：`Documents/script.py314.lc.npk`，sha `508bb5bdaac0aaf09acc43a31939e150abf45a22429846c7fb49bc1b5b20cdf3`，188,306,920 B，27,519 条目
