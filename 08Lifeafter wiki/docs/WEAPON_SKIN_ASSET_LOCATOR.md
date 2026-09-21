# 武器皮肤 / 外观 素材定位链（可复用）

> 2026-09-13 建立。**只写已实证的环节**；未证的一律标注「未证」。

## 一、四级定位链（行 → 素材）

```
① 行锚定   data/boards/weapon_skin_sfx_text_sources.json
             item.id = 1110171 → model_path = weapon/skin/skin_1003_010/skin_1003_010.gim
             → stem = skin_1003_010            （board 字段直读，可复现）

② 容器检索（**必须搜对目录**，这是本次最大的坑）
   E:\mrzh\res\*.fpk              64 个（各约 1GB）→ 已建**帧级索引**（见第三节）
   E:\mrzh\res\{weapon,ui_01..ui_05,textures,sound,model_01..11,character_01..09,effect_*}.gpk
   E:\mrzh\Documents\gres\*.gpk    35 个（热更包；只有 0058/0045 含音频）
   E:\mrzh\res.npk / res.gpk       根目录两个大容器（条目表可读：16,905 / 19,600 条）

③ 条目/帧定位（**不能在容器原始字节里搜** —— 条目是压缩的，明文搜一律 0 命中）
   .fpk ：32B 头 + 连续 zstd 帧流 → toolkit_core.fpk_frames.iter_fpk_frames 逐帧解压
   .gpk/.npk ：按条目解包（lifeafter_unpacker_full.extract_gpk / npk 表 + unpack_entry）

④ 素材导出
   贴图：dxgiFormat=struct.unpack_from('<I',dds,128)[0]（98/99=BC7、77/78=BC3、71/72=BC1、28/29=RGBA8）
        BC7 必须 texture2ddecoder.decode_bc7(dds[148:],w,h)（Pillow 直开=花屏）
        **全程 RGBA，禁止 convert('RGB')**（否则透明区填实色 → "色块异常延伸"）
        图集：同帧附近 ATLAS 帧是文本清单（名字 + xy/size）→ 按矩形 crop 才是"一件一图"
   音频：FSB5 → lifeafter_unpacker_full.extract_fsb（需 pip install fsb5）；RIFF 容器按 riff 处理

## 二、命名规律（实证）

| 形态 | 实例 | 出处 |
|---|---|---|
| `sample/weapon/<名字>_<年月>/<名字>_<事件>.wav` | `sample/weapon/shuijinmeigui_202607/shuijinmeigui_hit_lv3.wav` | `E:\mrzh\res\sound.gpk` 000365.riff |
| `ui/all_txt_meishuzi_icon/.../<名字>/txt_<名字>.png` | `.../huodongtanchuan/yueseyongtandiao/txt_yueseyongtandiao.png` | `E:\mrzh\res\ui_01.gpk` 004527.bin |
| `weapon/<武器>/textures/skin_XXXX_YYY001{a,m,n,s}.tga` | `weapon/weapon_1001_16/textures/skin_1012_002_1001a_a.tga` | `res/001.fpk` 第 14057 帧 |
| `skin_XXXX_YYY_mvp_nan/nv.gim` | 展示模型（男/女） | 脚本包路径字典 |

**内部名 ≠ 上线名**（实证）：水晶玫瑰 → `shuijinmeigui_202607`；月色咏叹调 → `yueseyongtandiao`。
⇒ 定位时**不能只按中文名猜拼音**，要按容器里的实际串检索。

## 三、已建成的可复用资产

- `data/fpk_index/fpk_index.jsonl` —— **1,896,538 帧 / 全 64 个 fpk / 64 包全覆盖**。
  每行：`{pack, frame, offset, magic, size, atlas_names[], stems[], paths[]}`
  ⇒ 之后定位任何外观素材，**先查这份索引**（`stems` 命中即得包+帧），不必重扫。
  重建：`python tools/build_fpk_index.py --workers 24`（约 18 分钟）
- `tools/export_fpk_textures.py --pack 001 --out <dir> --sprites` —— fpk 贴图/切片导出（BC7+RGBA 正确管线）
- `tools/carve_fsb5_banks.py --only 0058` —— gpk 里的 FSB5→WAV（0058 实测 8 bank/102 WAV）
- `tools/aggregate_skin_audio.py` —— 音频按皮肤归类（stem + 拼音双路，认不出进 unmatched）
- `tools/search_decompressed.py --gpk/--npk <容器> --pat <串>` —— **解压后**再搜（明文搜无用的正解）

## 四、未证 / 待办（别当成已完成）

- **光影咏叹调（1110171 / skin_1003_010）**：在 `res/*.fpk`(64)、`gres/*.gpk`(35)、`res.npk`、`res.gpk`、
  `res/weapon.gpk`、`res/ui.npk`、`res/ui_01~05.gpk`、`res/sound.gpk` 中**均未命中**（含 `guangying`,
  `1003_010`, `1110171`, `yingyongtandiao`）。⇒ 它的**内部名形态仍未定位**（未证），需要按第一节②的
  容器 + 「名字_年月」规律继续反查。
- 索引里 `skin_1003_*` 系只出现 **001–005**（贴图 a/m/n/s 齐全），无 010 —— 与上条一致。
- `Documents/res` 是否还有别处容器、以及 `Documents/g66discrete`、`bin`(3.2GB)、`multi_cloud*` 未查。

---

## 四补：内部名 ↔ 上线名 实证表（**别按拼音猜**）

| 上线名 | 内部名（音库目录） | 依据 |
|---|---|---|
| 水晶玫瑰 | `shuijinmeigui_202607` | 用户听感确认 ✅（板上无此皮肤，属板外皮肤） |
| 光影咏叹调 (1110171) | `huitailang_yongtandiao` | 用户听感确认 ✅ |
| 极光剑 (1110177) | `jiguangjian_202608` | 拼音吻合 ✓ |
| 金乌负日 (1110142) | `jinwu_20260115` | 拼音吻合 ✓ |
| 墨隐麒麟 (1110165) | `moyinqilin_20260512` | 拼音吻合 ✓ |
| 九霄狐啸 (1110032) | `weapon_1013_003_20250312` | stem 吻合 ✓ |

⇒ 绑定依据只有三种：**用户听感确认** / **拼音吻合** / **stem 吻合**；其余 110 个音库（多为基础武器音 `ak`/`mp5`/`shotgun` 与纯代号）**尚未绑定**，需要 `.fev` 事件名桥。

## 五、音效链（2026-09-13 **已跑通并经用户听感确认** ✅）

```
外观名 → E:\mrzh\res\sound.gpk
        ├── .riff  (实为 FMOD Designer 的 .fev：头 = RIFF…FEV FMT… LIST…PROJOBCT)
        │         只存【事件 + 样本名表】，例 000365.riff 含 339 条 sample/weapon/**.wav 名字
        └── .fsb   (FSB5 音库，共 1068 个；名字表里的样本就在这里)
       → lifeafter_unpacker_full.extract_fsb(<fsb>, <outdir>) → WAV（名字取自 bank 自带样本名）
```

**实证案例**：`sample/weapon/huitailang_yongtandiao/`（29 个名字）
→ `000920.fsb`（0.65MB，VORBIS，35 samples）→ 转出 35 个 WAV，其中 **咏叹调 15 个**：
`yongtandiao_shoot1..6` / `hit1..5` / `single_reload` / `single_switch` / `double_reload` / `double_switch`
→ 产物 `03拆包产物/sky1003_audio/`，**用户已确认"对的"** ✅

**要点（别再踩）**：
- `.riff` **不是**音频本体（开凿 `RIFF/WAVE` 得 0 个）——它是 FEV 事件表，音频在 `.fsb`。
- `sound.gpk` 1.2GB 里有 **1068 个 FSB5**；搜"名字"要在 **.fev/.riff** 里搜，取音频要在 **.fsb** 里取。
- `extract_fsb` 需 `pip install fsb5`（缺了会静默 0 样本）。

**这条链对任何外观通用** ✅：`.fev` 名字表搜名字 → 找同名 FSB5 → extract_fsb → WAV。

---

## 六、皮肤 ↔ 音效 的绑定方法（2026-09-13 实测，**这是目前唯一可复现的路**）

### 已证的四段（三段通，一段缺口已定位）

| 段 | 状态 | 证据（可复现入口） |
|---|---|---|
| ① 皮肤 → 模型/贴图 | ✅ | `res/weapon.gpk`：材质 `.c159` 条目**自述** `weapon\skin\skin_XXXX_YYY\...gim` 与 `textures\...tga` |
| ② 皮肤 → `.sfx` 路径 | ✅ | `res/effect_01.gpk`：FxGroup XML 的 `SfxName = "effect/fx/weapon/skin/skin_XXXX_YYY/fx_skin_XXXX_YYY_*.sfx"` |
| ③ `.sfx` 本体 → 事件名 | ❌ **缺口** | `.sfx` 本体**不在** `effect_01/effect_02/effect_cache`（三包全扫，0 命中）也不在 `script.py314.lc.npk`（105,777 条，0 命中） |
| ④ 事件/名字 → 音库 → WAV | ✅ | `res/sound.gpk`：`.riff` 实为 FMOD `.fev`（事件+样本名表，20,995 条名字）；音频在同包 **1,068 个 FSB5** 里 → `extract_fsb` → WAV |

### 现在就能用的绑定启发法（**实测有效，2 例已由用户听感确认**）

```
皮肤中文名 → 取其中 2~4 个关键字（如「光影咏叹调」取「咏叹调」、「水晶玫瑰」取「玫瑰」）
          → 在 sound.gpk 的 .fev 名字表（20,995 条）与音库目录名（sample/weapon 下 115 个）里搜
          → 命中即得音库目录（如 huitailang_yongtandiao / shuijinmeigui_202607）
          → 找同名 FSB5 → extract_fsb → WAV（名字取自 bank）
          → 用「听」验证（成本最低、结论最硬）
```
佐证：拼音吻合的自动匹配也成立 —— 极光剑=`jiguangjian_202608`、金乌负日=`jinwu_20260115`、
墨隐麒麟=`moyinqilin_20260512`；stem 吻合的：九霄狐啸=`weapon_1013_003_20250312`。

### 待办（把③补上即全链闭环）
- 找 `.sfx` 本体所在容器（候选：`gres/*.gpk`、`Documents/res` 其他包、`thd/`）。
- 或改用配置表桥：`weapon_skin_sfx_function_data`（352 行）里皮肤行 ↔ `1120xxx` 音效道具 ↔ 事件名。

---

## 七、`.mesh` 解析交接件（2026-09-13 **未完成，已排除法定位**）

### 输入
- 样本：`001210.mesh` = `skin_1003_010`（光影咏叹调）的 LOD0 模型，**203,406 B**
- 全量池：`weapon` 包解出 **约 10,000 个 `.mesh`**（临时目录 `%TEMP%\gim__dyg5vsd\`，重跑 `extract_gpk` 可复得）
- 配套贴图：同区 `.dds` 4,949 张（已正确解出 BC7+RGBA，见本文件第三节）

### 已确定（逐字节核实）
| 偏移 | 内容 |
|---|---|
| +0 | magic `34 80 C8 BB`（明日的 mesh 魔数） |
| +4 | u16 数组起始：`[4, 5]`（段数 / 版本 候选） |
| +10 | `0x1a7e` = **6782**（计数候选：顶点数或索引数） |
| +16 | 偏移表 `5,804` / `5,840`（已核对落在文件内） |
| +20 | 描述符表：`0x0102` 开头的三连组 `<u16 fmt, u16 a, u16 b>` 重复：`(0x0102,702,565) (0x0102,303,244) (0x0102,258,303) (0x0102,258,244) (0x0102,1,6809) …`——**疑似子网格/顶点格式区段表**，需继续解 |
| 尾部 | 成片 `00 00 00 ff` 重复 → **疑似量化法线/顶点色（4 分量）** |
| 末尾 16B | `01 00 0e 00 00 00 01 00 04 00 00 00 00 00 00 00`（材质/子网格收尾表） |

### 已排除（**别重复走**）
| 假设 | 判据 | 结果 |
|---|---|---|
| float32 顶点（13 个起点 × 22 个 stride × 滑动 noff） | 3 连续 float 长度 ≈ 1.0 | **0 命中** |
| half-float 顶点（7 × 9 × 滑动） | 同上 | **0 命中** |
| int16 顶点（12 起点 × 15 stride × 滑动） | \|n\| ≈ 32767 | 最好 err 0.186（**不成立**） |
| int8 顶点（8 × 11 × 滑动） | \|n\| ≈ 127 | 最好 err 0.162（**不成立**） |

⇒ **结论：顶点区不是直排数值，是压缩/量化编码**（可能是块式量化、基数+位移、或先索引后解压）。

### 下一步（按性价比排序）
1. **解 +20 的描述符表**：它自述各段 `<格式, 参数, 大小>`，是合法入口（比盲扫 stride 高效得多）。
2. 对照 `+16` 的两个偏移（5,804 / 5,840）切出两个区段，比对其"头 32 字节"找区段头格式。
3. 若描述符表解通 → 直接按表取顶点/索引，不再盲扫。
4. 兜底：搜 NeoX 引擎（明日之后同源）的 `.mesh`/`.nmb` 结构文档或开源实现。

---

## 八、光影咏叹调 = **双枪**（用户纠正，2026-09-13）+ 形状判据

### 事实（用户实机确认）
- 武器类别：**双枪**（左右各一把手枪），**不是**弓/刀/单枪。
- 姿态：**左右镜像**，左枪蓝青、朝 10–11 点钟；右枪紫罗兰、朝 1–2 点钟；握把朝下向中央收拢（外八字/V 形），中央握把+扳机区交叠。
- 包围盒：**宽:高 ≈ 2.3:1**（横长）。
- 材质：金属骨架 + 金色包边 + 枪口外缘能量/晶石发光（左青蓝、右紫红）。
- 用途：**渲染图的验收基准**（外部参考图：`composer-images/60a5d1b1…png`）。

### 由此确立的形状判据（**取代**单点法线判据）
`.mesh`/`.gim` 顶点解对的必要条件（可自动打分）：
1. 包围盒 **X ≫ Y ≈ Z**，比例约 **2.3:1**；
2. 点云**左右镜像对称**（对 X=0 平面做镜像残差）；
3. 轮廓**双峰**（两个分离的簇 = 两把枪，中央有交叠区）。
⇒ 盲解各候选布局，**形状对的那一组**才算赢；法线模长只作辅助。

### 教训（写进 RE 惯例）
- **音效命名能定武器类别**：`single_reload` / `double_reload`、`single_switch` / `double_switch`
  ⇒ 「单持/双持」= **双枪**。同类线索还有：`_shoot1..6`（射速档）、`_hit1..5`、`xuli`（蓄力）、`mvp_nan/nv`（展示）。
- **别用渲染图猜类别**（低分辨率+光效极易误判为弓/翼）；**先用结构化线索（音效名/模型路径/stem）定类别，再用图校正**。

---

## 九、**.c159 = 带字段名的序列化文档**（2026-09-13 突破，**推翻"盲解二进制"路线**）

### 事实
`weapon.gpk` 中与 `skin_1003_010` 相关的 **13 个条目全部是 `.c159`**，**同一 magic `c1 59 41 0d`**，
且**字段名为 ASCII 明文**（无需猜）：

| 条目 | 大小 | 明文段名 | 含义 |
|---|---|---|---|
| 001209 / 001221 / 001263 | 1,853 / 1,609 / 2,612 B | `BoundObject` | 边界体（包围盒/体积） |
| 001211 / 001214 / 001217 / 001220 / 001223 / 001265 | 3,714–7,860 B | `AnimParam` | 动画参数 |
| 001212 / 001215 / 001218 | 608 / 617 / 614 B | `NeoX` `Sub0` `S…` | **子网格描述** |
| 001267 | 2,165 B | `AnimationEvent` | 动画事件 |

另：`utility.gpk` 的 **`021165.c159`**（657 B）= 音效描述符，含
`effect\fx\weapon\skin\skin_1003_010\fx_skin_1003_010_hezi.sfx`（盒子音效）。
⇒ **`.c159` 是通用资源描述符**：同一个类型在 `weapon.gpk` 里描述模型/动画，在 `utility.gpk` 里描述音效。

### 结构头（已核实）
```
+0  c1 59 41 0d            magic
+4  <u32 小端>             段数据长度（如 0x73d=1853-12）
+8  <u32> 0
+11 <u8 len><ASCII 段名>     如 15 "BoundObject" / 2f "AnimParam" / 05 "NeoX"
```
⇒ **TLV 式**：`段长 + 段名 + 段体`，段名明文可列举。

### 这改变了什么（**原计划作废**）
- ~~在 `.mesh` 上盲扫 stride/字段序~~ → **作废**（那是 1 万个**独立零件**，且是另一套格式）
- 新路线：**解 `.c159` 的 TLV**（段名明文 → 段体结构可逐段对照）→ 模型/动画/边界体全在这套文档里
- `.gim` = 逻辑路径名（供引擎按名取用），**不是**要单独找的容器文件

### 下一步（可直接开工）
1. 写 `.c159` TLV 解析器（magic + 段表），先用 `001212.c159`（608 B 最小）打通。
2. 解 `Sub0` 段 → 取顶点/索引（子网格）；解 `BoundObject` → 包围盒（**正好用来验双枪形状判据：≈2.3:1 / 镜像 / 双峰**）。
3. 通后按同法批处理 1 万个 `.mesh` 与全部 `.c159`。

---

## 十、`.mesh` 顶点布局：**未破解，已定界**（2026-09-13 收口）

### 已排除（全部实测，勿重复）
| 尝试 | 判据 | 结果 |
|---|---|---|
| float32 / half / int16 / int8 直排（起点 13×stride 22×滑动偏移） | 法线模长≈1 | 0 命中 |
| int16/int8 量化 | \|n\|≈32767 / 127 | 最好 16% 误差，不成立 |
| 在 17 个 `model_*.gpk`（231,887 条目）按边界体浮点字节反查 | 精确 float 字节匹配 | 0 命中（几何非裸 float，已量化） |
| `.mesh` 候选布局 × 包围盒**比值**判据（尺度无关） | 比值≈目标 | **有假阳性**（同一批数据既"比值吻合"又给出 ±7000 的荒谬尺度）⇒ 比值判据不可单独用 |

### 结论（诚实）
- `.mesh`（`weapon.gpk` 11,037 条，magic `34 80 C8 BB`）**是否**即 `.c159` 引用的 `.gim` 本体，**未证**；
- 顶点区**不是**直排 float/整型，是**压缩/量化编码**，且现有判据（法线、比值）**都不足以定位**；
- 下一步必须先加**绝对尺度约束**（目标半长 (0.33,1.26,2.47) 允许单位缩放）+ 缩小候选范围（用 header 计数 `0x1a7e=6782` 或编号相邻文件），否则全量 11,037 文件按当前速度需 ~34 小时。

### 本轮真正拿到的东西（有效、可复用）
1. **`.c159` 文档层完全打通** —— `tools/parse_c159.py` 可读出模型文档全部**字段名**（`001209.c159` = 38 个字段：`BoundObject / Lod1..Lod4 / Lods / NeoX / Object / Openworld / Socket_0..6 / Sockets / Sub0..2 / SubMesh / BindType / BoundingCenter / BoundingHalf / BoundingInfo / CompatibleMask / Dist / MatrixToBone / MeshSortMethod / ModelSceneFlag / MtlIdx / MustShow / Name / Path / ReplaceLodLevel / TangentEnable / Version`）。
2. **皮肤 → 资源** 的完整绑定**就在这里**：模型路径（3 级 LOD `.gim`）、子网格名（`skin_1003_010_0/1/2`）、7 个挂点、包围盒（明文数值）、特效/音效事件名（`fx_idle_01` / `muzzle_fire` / `sound` / `pifuguashi` / `hongwai`）。
3. 音效侧二次印证：`utility.gpk` 的 `021165.c159` = 音效描述符（`fx_skin_1003_010_hezi.sfx`）。

---

## 十一、**皮肤 ↔ 音效桥：实证打通**（2026-09-13，金乌案例）

### 链路（机械可复现，无需听感）
```
皮肤文档 weapon.gpk/XXXXXX.c159
   └─ 子网格名 = 皮肤【代号】   例：'jinwu_01_0' 'jinwu_01_1'
        ↓
sound.gpk 的音库目录按「代号_日期」命名   例：sample/weapon/jinwu_20260115/
        ↓
同包 FSB5 音库（含同名样本）            例：000880.fsb（15 样本，VORBIS）
        ↓
lifeafter_unpacker_full.extract_fsb → WAV
```

### 实证（金乌）
- 皮肤文档：`weapon.gpk` 中 `002148/002153/002158/002166.c159` 等 **38 个文件**含 `jinwu`，
  子网格名 `jinwu_01_0` / `jinwu_01_1`，同文档含 `weapon\skin\skin…` 路径。
- 音库：`000880.fsb` → **15 个 WAV**，名字全部以 `jinwu_` 开头：
  `jinwu_shoot_1/3`、`jinwu_hit_1/3`、`jinwu_ready_1/3`、`jinwu_ready_shan_1/3`、`jinwu_relax_3`、
  `jinwu_suan_hit`、`jinwu_suan_shan1/2`、`jinwu_xuli_loop_1/3`、`jinwu_mvp`
- 与 `data/exports/sound_library_index.csv` 里 `jinwu_20260115` 的 15 条**逐条吻合**。
- 产物：`03拆包产物/skin_audio_all/jinwu/`（15 WAV）

### 边界（诚实）
- 该桥依赖「子网格名里有代号」；`skin_1003_010`（光影咏叹调）的子网格名是 `skin_1003_010_0/1/2`
  **不含代号**，其代号 `huitailang_yongtandiao` 只在 `sound.gpk` 侧出现。⇒ 桥对**部分皮肤**直接可用，
  另一部分仍需代号对照表（候选：动画文档 `EventTrack_*` 或配置表）。

---

## 十二、**皮肤 → 音效 全链闭环**（2026-09-13 找到最后一环）

### 最后一环：`.sfx` 本体 = effect 包里的 FxGroup XML，字段 `EventName`
`effect_01.gpk` 的 `037318.bin`（明文 XML）：
```
FileName  = "sound\g66_weapon.fev"
EventName = "g66_weapon/202606_yongtandiao/yongtandiao_hit"
```
`037168/037229.bin` 同形：`EventName = "g66_weapon/202606_huitailang/huisexieyi_hit"`。
⇒ **皮肤的特效定义直接点名 FMOD 事件**（`<fev 名>/<事件组>/<事件>`）。

### 完整定位链（**全部机械可复现，无需听感猜测**）
```
① 皮肤行   board: 1110171 → model_path → stem = skin_1003_010
② 资源文档 weapon.gpk 的 .c159（tools/parse_c159.py）
            模型路径 skin_1003_010_lod01/02/03.gim · 子网格 skin_1003_010_0/1/2
            挂点 Socket_0..6 · 包围盒(明文) · 事件 fx_idle_01 / muzzle_fire / sound
③ 特效定义 effect_01.gpk 的 FxGroup XML
            SfxName   = effect/fx/weapon/skin/skin_1003_010/fx_skin_1003_010_*.sfx
            FileName  = sound\g66_weapon.fev
            EventName = g66_weapon/202606_yongtandiao/yongtandiao_hit     ★ 关键
④ 音效       sound.gpk: sample/weapon/<事件组>/<事件>.wav 的样本名表
            同名 FSB5 音库 → lifeafter_unpacker_full.extract_fsb → WAV
```
验证：光影咏叹调 15 个 WAV（用户确认 ✅）；金乌 `jinwu_01_*` → `jinwu_20260115` → `000880.fsb` 15 WAV（用户确认 ✅）。

### 注意
- 事件组带日期后缀：`202606_yongtandiao` 而音库目录为 `huitailang_yongtandiao`（前缀为联动活动名）⇒ 用「事件组名的主体（yongtandiao）」去音库目录匹配。
- `.fev` = `sound\*.fev`，即 `sound.gpk` 里的 `.riff`（FMOD 工程文件，含事件与样本名表）。

### 十二补：自动化铺表的现状（诚实）
- `effect_01.gpk` 共 **38,597 个 XML 条目**；其中「引用皮肤」的组与「纯 `FxSoundEventDrive`」的组是**分开的条目**
  （例：`037300/037305/037315..037320.bin` 引用 `skin_1003_010`；`037318.bin` 只有 `EventName`，**不含皮肤引用**）。
- 用**邻域 ±80 条目**配对可得 **12 个皮肤** 的事件绑定（`data/exports/skin_event_bind.csv`），
  但**有噪声**（会串到 `monster_*` / `object` / `car*` 等与皮肤无关的事件组）⇒ **不可直接当结论用**。
- 干净全量表仍缺一步：**`.sfx` 条目号 ↔ `.sfx` 逻辑路径** 的对应（FxGroup 里明文写着 `SfxName` 路径，但条目本身匿名）。
- **已确证可靠的两例**：`skin_1003_010`（光影咏叹调）、`jinwu`（金乌）——均经用户听感确认。
