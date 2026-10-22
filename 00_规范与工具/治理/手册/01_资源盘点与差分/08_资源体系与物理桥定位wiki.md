# 明日之后 资源体系与物理桥定位 Wiki

> 版本：2026-08-31 ｜ 方法：全部结论经只读实跑验证，覆盖率为当场实测
> 配套引擎：`01拆包器本体\工具库\10_应用核心\toolkit_core\resource_resolver.py`
> 逆向对象：`E:\mrzh\res`（体验服）；对照：`E:\lifeafter\res`（正式服，仅结构对照）

---

## 一、三层资源容器总览

| 容器 | 魔数 | 条目大小 | 是否带名字 | 条目字段 | 角色 |
|---|---|---|---|---|---|
| **NPK / FPK** | `NXPK` | 48B | **带 fid（路径哈希，可还原路径）** | fid(u64), off, clen, olen, c1, c2, flag | 脚本包(script*.npk)、UI 按需包(ui.npk)、64 个美术资源包(001~064.fpk) |
| **GPK** | `HPGF`(逻辑名 FPGH) | 32B | **完全匿名（无 fid）** | off, clen, olen, c1, c2, flag | 55 个旧结构美术大包（weapon/character/ui_*/effect…） |
| **KPGF 分卷 GPK** | 头[56]=`KPGF` | 32B 表 + **每条目 36B 明文头** | 匿名 | 36B 头内 [16]clen/[20]olen/[24]c1/[28]c2/[32]flag，zstd 流从 off+36 起、可多帧 | textures.gpk 等通用 tiling 材质库（493 张 BC7，泥土/噪声，非皮肤专属），`iter_kpgf_entries()` |
| **WPK + .idx(SKPW)** | `1DPW`/`SKPW` | idx 36B | idx 带 16B hash | 按需分块下载包 | 贴图/资源按需下发，1DPW 加密已攻破 |
| **FHPK** | `FHPK` | 变长 | **明文带磁盘文件名** | 路径 + 3×size + 16B MD5 | `Documents\file_hash_pack.bin`，整包/程序文件**热更校验清单**，不含包内资源 |

关键认知：**GPK 条目匿名、FPK 条目带名，二者通过内容指纹 c1/c2 互通**（见第四节）。

---

## 二、通用加密 / 压缩（全容器一致）

- **AES-128-ECB KEY**：`606308D8A32C782013D26C2F226F686D`
  - NPK/FPK/GPK 的「头部 + 条目表」按 16 字节倍数整体 AES-ECB 解密。
- **条目 flag**：
  - `0` 原始（数据体再走一层 AES-ECB；此时 c1==c2）
  - `2` LZ4 block（自研块解压，见 `lz4_block`）
  - `12` zstd
- **条目定位**：
  - NXPK：头解密后 `[16]=条目表偏移, [20]=条目数`；条目表每条 48B。
  - FPGH：头解密后 `[20]=条目数`；条目表固定从偏移 64 开始、每条 32B；数据体从 `off+36` 起。

---

## 三、fid：路径 → 条目的钥匙（核心突破）

### 3.1 算法（双 Murmur3 x86_32）

```
fid = (murmur3_x86_32(path_bytes, seed=0x77777777) << 32)
      | murmur3_x86_32(path_bytes, seed=0x66666666)
```

### 3.2 输入规范（此前长期卡住的根因）

- **资源路径用反斜杠 `\`、UTF-8**：例如 `weapon\skin\skin_1001_001\skin_1001_001.gim`。
- 脚本 tI 路径多用正斜杠；定位美术资源时若正斜杠不中，**必须换反斜杠**。`resource_resolver` 已自动尝试两种。
- 路径区分大小写、保留扩展名；不要自行去扩展名或加目录前缀。

### 3.3 全局 fid 索引（实测）

- **仅根目录**（64 .fpk + ui.npk）：2,069,650 条，约 4 秒。
- **递归含子目录分类 npk（默认，`build_index(recursive=True)`）**：res 下 character/ui/model/building/scene/scene_bw
  共 **216 包、3,007,422 条、唯一 c1c2 2,632,212、约 7.3 秒、0 失败**。找资源一律用递归版，避免漏掉分类 npk。
- 索引产物（可选落盘）：`03拆包产物\fpk_fid_index.json`（旧根目录版）；默认内存重建即可。

---

## 四、c1/c2 内容指纹与「物理桥」

### 4.1 c1/c2 是什么

- c1/c2 **不是路径哈希**（8 步实验已永久证伪逆路径哈希取名，见 `06_文件名还原\GPK文件名还原_最终结论与交接_20260830.md`）。
- 它们是**内容指纹 / 打包去重 key**：flag=0 时 c1==c2；flag=2 压缩时分别对应压缩态/解压态。相同 (c1,c2) ⇒ 解压内容逐字节相同。

### 4.2 桥接原理

```
逻辑路径 --双murmur--> FPK.fid --(同条目)--> FPK.c1c2
                                          ↑ 内容指纹相等
GPK 匿名条目 ------------------------------→ GPK.c1c2
```

FPK 同时持有 fid 与 c1/c2，GPK 只有 c1/c2；用 c1/c2 即可把匿名 GPK 条目对接到 FPK 的 fid（再由路径语料反查名字）。

### 4.3 全索引下桥接覆盖率（实测）

| GPK | 桥接条目/总条目 | 覆盖率 |
|---|---|---|
| weapon.gpk | 50,396 / 51,665 | **97.5%** |
| character_01.gpk | 43,807 / 47,390 | 92.4% |
| character_05.gpk | 72,915 / 77,827 | 93.7% |
| ui_01.gpk | 65,825 / 79,769 | 82.5% |

> 结论：绝大多数 GPK 匿名条目都能经 c1/c2 对到带名 FPK 条目；剩余缺口靠路径语料扩充 / MD5 撞库补齐。

---

## 五、完整皮肤定位链（已端到端跑通）

以一把武器皮肤为例，从配置到模型实体：

1. **配置层**：`weapon_skin_data_rows.json`（BinDict 解码产物）给出武器 id 与 `model_path`，
   如 `weapon/skin/skin_1001_001/skin_1001_001.gim`。
2. **定位层**：反斜杠化后算 fid，在 206 万 FPK 索引精确命中
   → `003.fpk#2633, flag=12(zstd), c1c2=026c6289/bc2d0592`。
   - **实测 89/112（79.5%）皮肤 model_path 直接命中**；皮肤 gim 集中在 002/003.fpk。
3. **解包层**：按 flag 解出 c159 NeoX 对象（主 gim，含 BoundObject/Lods/Sockets）。
4. **递归层**：gim 内部以明文路径引用子资源，递归 path_id 定位，**实测一套皮肤访问 12 节点、0 缺失（跨 001/002/003/004 包）**：
   - `*_lod01/02/03.gim`（多级细节，SubMesh：MtlIdx 材质索引、包围盒）
   - `*_shadow.gim`（阴影）、挂件 `utility\*.gim`、`weapon\hongwai\*.gim`
   - **同名 `.mesh` 即网格**：`skin_1001_001.mesh`(226KB 主网格)、`skin_1001_001_lod01.mesh`(127KB)，均定位成功。
5. **材质层（2026-08-31 已破，旧稿"cgmat"为误判，实际是 .mtg）**：主 gim 用整数字段 MtlIdx 引材质，
   **与 gim 同名的 `.mtg`** 即 NeoX 材质（c159 序列化）。`parse_mtg()` 可抽出：
   - shader：`shader\pbr_weapon.fx::TShader`（PBR 武器材质）；
   - 4 张 PBR 贴图逻辑路径，位于 `<dir>\textures\`，命名 `<stem><3位编号><通道>.tga`：
     **a=albedo 主色 / n=normal 法线 / m=metallic 金属度 / s_m=smoothness 光滑度**。
   - 样例 `skin_1001_001.mtg = 003.fpk#7517(1033B)`，引用 `...textures\skin_1001_001001a/n/m/s_m.tga`。
6. **纹理实体层（关键墙与绕行，见第五·补）**：这些 .tga 逻辑路径在**全部 216 包 300 万条索引里 0 命中**——
   源 tga 打包后转为 BCn-DDS 进入**匿名 weapon.gpk**，无路径 fid。无法按名直取，改用
   「版本独有判据 + 颜色特征筛选」绕开（已实测捞出铠甲金剑/金步枪，见下）。

### 命名规则（实测）

| 资源 | 规则 | 示例 |
|---|---|---|
| 主对象 | `<dir>\<stem>.gim` | weapon\skin\skin_1001_001\skin_1001_001.gim |
| LOD | `<stem>_lod0N.gim/.mesh` | skin_1001_001_lod01.gim |
| 网格 | 与 gim 同名 `.mesh` | skin_1001_001.mesh |
| 材质 | 与 gim 同名 `.mtg`（非 cgmat） | skin_1001_001.mtg |
| 贴图 | `<dir>\textures\<stem>001<a/n/m/s_m>.tga` | skin_1001_001001a.tga(主色) |
| 阴影 | `<stem>_shadow.gim` | skin_1001_001_shadow.gim |

### 第五·补　匿名纹理墙（6 路证伪）与两条绕行判据

**墙**：皮肤专属贴图在匿名 gpk，逻辑路径反推实体已从 6 个方向证伪，勿再重复试：
①tga/dds/pvr/png 路径 fid 在递归全索引 0 命中；②gpk 全文件搜不到任何 fid 字节（连对照 gim 也无）；
③wpk 的 .idx 16B 是**内容 MD5**非路径 hash；④local_finfo* 是磁盘文件 pickle 清单、不含包内资源；
⑤textures.gpk 条目头 16B 不是 fid（第 4 字段为递增小值）；⑥扩展到子目录 216 包仍 0 命中。
→ 真正缺的是「fid→路径字符串全局名表」，只能靠 exe 逆向或外部名表（已交接硬骨头）。

**绕行 1：版本独有判据（`find_unique_in_gpk`，最重要的可复用方法）**
匿名 gpk 条目用 c1/c2 去桥全量索引，**桥不到 fid 的即本版独有新内容**。weapon.gpk 实测：

| 类型 | 总数 | 桥到 | 独有 | 独有率 |
|---|---|---|---|---|
| dds | 4948 | 4624 | **324** | 6.5% |
| mesh | 11037 | 10783 | 254 | 2.3% |
| c159(gim) | 35275 | 34617 | 658 | 1.9% |

即找未上线武器贴图时，候选从 4948 直接浓缩到 324。铠甲金剑 `weapon#4009` 正是桥不到的独有条目。

**绕行 2：颜色特征筛选（`texture_extractor.py`）**
BCn 主 mip 解码后按 RGB/HSV 规则打分（默认 gold=金色，用于铠甲联动金武器），多进程
（智能 80% 核、留 2 核、高负载自动减半，32 核机用 25 进程，4919 张约 7 秒），出候选 PNG+联系表，
再由人/多模态按形态确认。已实测捞出：#4009 黑金华丽长剑（铠甲联动剑，独有）、#49505 金黑蓝能重武器、
#179/#3163 金色步枪、#19771 三叉星暗纹金步枪、玫瑰金/蓝金/紫金枪械系列。

---

## 六、引擎资源管理机制（来自脚本层 ResourceMgr / GpkHelper / WpkManager）

从 `script.npk` 提取的三个核心模块（entry：ResourceMgr=58630 / GpkHelper=70552 / WpkManager=28944）确认：

- 引擎维护全局 **FileDict**：资源路径 → `get_name_id()`（即双 murmur）→ `name_id_to_file_data`（包内 off/size/flag）。
- 挂载包时把条目索引并入 FileDict；取文件走 `get_file_datas_by_name_id`。
- `file_hash_pack.bin`（FHPK）是**磁盘文件级热更清单**（路径+MD5+压缩/原始 size+分块），列 dll/exe/pak/`.layers.*.npk` 整包，**不含 .gpk/.dds/.mesh 等包内资源**，不能用于包内取名。
- WpkManager 负责按需下载（res_id → DownloadFile → .layers 增量包）。
- 这些模块是 Python 3.14 marshal、系统 3.13 无法直接反编译，但**常量字符串足以还原机制，且算法已被数据实测独立证实**。

---

## 七、工具用法：resource_resolver.py

位置：`01拆包器本体\工具库\10_应用核心\toolkit_core\resource_resolver.py`（只读源）

```python
from toolkit_core.resource_resolver import ResourceResolver, parse_mtg, decode_bcn_dds
r = ResourceResolver(r"E:\mrzh\res").build_index()     # 递归216包, ~7s, 300万条

e = r.locate(r"weapon\skin\skin_1001_001\skin_1001_001.gim")  # -> Entry(pkg,index,...)
data = r.read_path(...)                                # 直接解出 bytes
tree = r.resolve_tree(root_gim, depth=3)               # 递归整套资源位置（含 .mtg/.tga）
rep  = r.bridge_gpk(r"E:\mrzh\res\weapon.gpk")         # GPK 匿名条目 c1c2->fid
uniq = r.find_unique_in_gpk(r"E:\mrzh\res\weapon.gpk") # ★版本独有条目(桥不到fid)
mtg  = parse_mtg(r.read_path("...skin_1001_001.mtg"))  # {shader,textures,channels}
img  = decode_bcn_dds(dds_bytes)                       # BC7/DXT5/DXT1 -> PIL.Image
```

匿名纹理颜色筛选（找金武器/某色相皮肤贴图）：
```python
from toolkit_core.texture_extractor import scan_dir
scan_dir(r"03拆包产物\weapon", r"输出\候选", res_dir=r"E:\mrzh\res",
         rule="gold", only_unique=True, top=60)        # 独有判据+多进程+联系表
```

命令行：
```
python resource_resolver.py locate "weapon\skin\skin_1001_001\skin_1001_001.gim"
python resource_resolver.py tree   "<gim路径>" --depth 3
python resource_resolver.py dump   "<路径>" out.bin
python resource_resolver.py bridge-gpk "E:\mrzh\res\weapon.gpk"
python -m toolkit_core.texture_extractor scan "03拆包产物\weapon" --res E:\mrzh\res --out 输出\候选
```

---

## 八、后缀速查与当前可解度

| 后缀/格式 | 内容 | 可解度 | 入口 |
|---|---|---|---|
| .gpk | FPGH 匿名资源大包 | ✅ 全解 + c1c2 桥接取名 82~97% | 主解包器 extract-gpk / resolver.bridge_gpk |
| .fpk/.npk | NXPK 带名包 | ✅ 条目表全解、fid 定位、flag 解压 | resolver / 主解包器 |
| .wpk+.idx | 1DPW 按需包 | ✅ AC/PC/XC+ENON/DTSZ 全链已攻破 | 03_WPK_1DPW |
| .gim(c159) | NeoX 模型对象 | ✅ 可解、可抽依赖路径递归 | resolver |
| .mesh | NeoX 几何 | ✅ 可取出；几何顶点流解析待做（3D 预览） | 待办 |
| .mtg | NeoX 材质(c159) | ✅ parse_mtg 抽 shader+4 通道 PBR 贴图路径 | resolver.parse_mtg |
| .dds(BC7/DX10/DXT5/DXT1) | 纹理 | ✅ decode_bcn_dds（texture2ddecoder，BGRA） | resolver / texture_extractor |
| .ktx | 纹理 | ✅ astcenc 路线 | 07_纹理转换 |
| KPGF textures.gpk | 通用 tiling 材质库 | ✅ 36B 头+多帧 zstd，493 张 BC7 | iter_kpgf_entries |
| ~~.cgmat~~ | 旧稿误判，材质实为 .mtg | — | 已由 .mtg 取代 |
| .nxs(BinDict) | 数值/配置 | ✅ 行级解码；attrs schema 部分 | 05_BinDict解码器 |
| .fsb5 | 音频库 | ✅ vgmstream 转 wav | 主解包器 extract-fsb |
| .thx/.thh(THFB) | 纹理引用哈希 | 🟡 19.8 万索引可读、数据区独立加密 | 09_THFB |
| lifeafter.exe | 自定义加密壳 | ❌ 动态脱壳待专业逆向（不阻塞主线） | 12_EXE脱壳分析 |

---

## 九、剩余缺口（按收益排序）

1. **匿名纹理的"精确命名"**（材质→纹理最后一跳的唯一残留）：逻辑链已 100% 闭合（知道每套皮肤要哪 4 张通道贴图），
   但源 tga 转 BCn 后进入匿名 gpk、无 fid，6 路反推证伪；现用「独有判据+颜色筛选」绕开可取到图，但要把某张匿名 DDS
   **精确断言**为"某皮肤的 a/n/m 通道"，仍需「fid→路径全局名表」（exe 逆向 WpkResourceMgr，或外部名表）。
2. **23/112 皮肤 model_path 未直接命中**：多为编号跳跃/在 GPK，经 c1c2 桥 + 路径语料补；需统计是"已删资源"还是"在 GPK"。
3. **.mesh 几何顶点流 → 可渲染 3D**：SubMesh/顶点格式已部分分析（u16+AABB+子网格的 NeoX 顶点流），对接 Three.js 做 3D 预览（用户已排期）。
4. **GPK 全量取名**：用 FPK 路径 + gim/mtg 依赖传播 + 正式服明文名册 + APK/缓存 MD5 撞库，把 c1c2→fid→路径语料做大。
5. **THFB 数据区、exe 脱壳**：低收益 / 专业逆向，挂起。

---

## 十、一句话结论

**GPK 匿名、FPK 带名：反斜杠路径算双 murmur 得 fid，可在递归 300 万条索引里秒级定位解出已知路径资源；匿名 GPK 条目用内容指纹 c1/c2 桥回名字（weapon 97.5%）。皮肤"配置→gim→mesh→mtg→4 通道 PBR 贴图逻辑路径"逻辑链已 100% 闭合；贴图实体在匿名 gpk，用「c1c2 桥不到即版本独有（4948→324）+ 颜色特征筛选」已实际捞出铠甲金剑/金步枪等未上线贴图。唯一残留是把匿名 DDS 精确绑定到具体皮肤通道名（需全局名表/exe 逆向），以及 .mesh 顶点流的 3D 渲染。**
