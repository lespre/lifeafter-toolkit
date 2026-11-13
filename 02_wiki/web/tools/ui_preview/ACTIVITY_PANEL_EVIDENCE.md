# 「未上线活动 → 面板」映射：四条验证与结论

> 结论：**本包内不可由数据推出**。不是没找到，是四条独立路径全部落空，
> 且第一条给出了机制性解释（布局表根本不在包内）。
> 因此入口页只按「名称语义候选」展示，并逐条写明依据；没有依据的写「无」，不硬凑。

验证时间：2026-11-07　｜　数据源：`01_索引与产物/41_还原树/pe/`（不碰线上 npk）

---

## 验证 0（机制）：界面是脚本动态搭建，不是 csb 面板

`ui/huodong/CommonSignInHDUI.py`（周年签到，47 KB）的字符串表里：

```
load_hd_ui_scheme        ← 唯一的界面装配入口
ui_group_id              ← 传参
WeekItemsH.load_hd_ui_scheme / WeekItemsV.load_hd_ui_scheme
```

`ui/huodong/MultiOptionalLotteryV2HDUI.py`（学院企划，17 KB）同样只出现
`ui_group_id`，没有任何 `.csb` 字面量。

⇒ 这类活动面板 = **按 `ui_group_id` 从 `hd_ui_scheme` 表逐控件搭出来的**，
不存在对应的 .csb 文件。所以「找哪个 csb」这个问题本身预设错了。

## 验证 1：布局表 `hd_ui_scheme_data_base` 在包里没有数据副本

`com/cdata/hd_ui_scheme_data.py`（822 B）只是一个合并壳，反编译后名字表为：

```
com.cdata.hd_ui_scheme_data_base   → _base
com.cdata.hd_ui_scheme_data_inc    → _inc
com.cdata.hd_ui_scheme_data_del    → _del
com.utils.SplitTableData           → data = SplitTableData(_base, _inc, _del)
```

★ 方法说明：`**/hd_ui_scheme*` 这类 glob 在本仓库会漏（目录深度/忽略规则），
本条的结论来自 **`Path.rglob` 全项目遍历**，实测命中 **41 个**文件，按类别只有四种：

| 类别 | 文件 | 体量 | 是不是表体 |
|---|---|---|---|
| 合并壳 | `cdata/hd_ui_scheme_data.py` ×3（还原树 + 两个热更快照） | 822 B | 否，只 import |
| reverse 表 | `hd_ui_scheme_reverse_data.py` + `_chs.py` | 444 KB / 679 KB | 是（已解，见验证 2） |
| 分服删除补丁 | `oversea/hd_ui_scheme_data_auto_oversea_data_*.py` | 7.6 KB × 9 | 否，只有 `region_delete_keys` |
| 分服 reverse | `oversea/hd_ui_scheme_reverse_data_auto_oversea_data_*` | 28 KB × 2（含 `_chs`） | 否，同为补丁 |

**没有任何一个是 `_base` 表体。** 壳的 `data` 因此恒为空 ——
这也是 `vm_cdata_table` 解出「4 个字典、最大 0 条」的原因
（不是解码器坏，是无数据）。分服文件里只有 `BeltChipNormalLotteryHD` 这类待删键名，
同样是补丁而非表体。

## 验证 2：同类表能解，唯独缺 base 的那张解不出（反证解码链路没问题）

同族 `hd_ui_spine_data.py` 用同一套解码链路**完整解出 708 行 / 0 行失败**：

```
hd_ui_spine 池 660 项：spine_node / anims / csb_name / node_name / spine_path / <活动类名>
首行：csb_name = ui/htpy_zhuanpan_proto_main_comp_choujiang_2.csb
      spine_path = ui/spine_new/shizhuangchoujiang/xiyangyang/btn_2
```

说明 bindict 行解码（`BT.decode_table_rows` + `parse_chs_pool`）对该格式有效。

但 spine 表给的是**「该活动类会往哪个 csb 里挂 spine 动效」**，不是「活动主面板是哪个 csb」。
实测它把 `MultiOptionalLotteryHD` 关联到 `huodong_shuitun_yushi_v1`（水豚玉石）等，
语义明显不是主面板 ⇒ 只能算弱信号，**不能当映射用**，因此不采纳。

## 验证 6：`hd_ui_scheme_reverse` 解开了，但它是「控件模块库」不是面板

这张 444 KB 的表是真数据，且能解：**320 行 / 6 行失败**（`lenient=True`；
严格模式只有 47 行能过，其余卡在 `inline list variant`）。

布局与 `bindict_73` 文档一致，且实测吻合：

```
[0:4]   u32 count = 11951     ← 等于 CHS 池长度（可当断言）
[4:8]   u32 reserved = 0
[8:..]  count × u32 ends，全 0（基表不带字面量池）
        u32 de = 392007 → blob[de] = 0x76 05 0b（索引尾，327 桶 / 327 节点，全部命中）
```

**CHS 池 11951 项 = 字段名 + 类名 + 327 个 `.csb` 路径**，字段名恰好是控件属性：

```
font_id / texture_scale / id / widget_name / texture / pnl_offset / visible /
texture_offset / pnl_size / str / font_size / color / logic_widget /
anchor_pos / rich_mode / font_ids / flip_x
```

每行结构（行键是**模块 id**，不是活动类）：

```
行键 6783 ─┬─ 列名『FashionSuitLotteryHD』→ 0x0b jump:313199
           └─ blob[313199] = 0x36 映射帧：{ ui_group 4 → [子控件偏移…] }
                                    { ui_group 3 → … }{ 2 → … }{ 5 → … }
子控件偏移 → 0x27 列表帧 → 0x86 行（schema 32）
           → {id, widget_name, texture, pnl_offset, pnl_size, font_size, str, …}
pnl_offset → 0x27 12 02 + 2×float32（实测 (38.0, −90.0)）
```

实测解出（`MultiOptionalLotteryHD` + `ui_group_id=4`，正是「学院企划」）：

| 模块 id | 子控件数 | 内容 |
|---|---|---|
| 6860 | 18 | `pnl_btn_zhuandong_left` / `img_zhuandong_left_nor/_down` / `txt_zhuandong_left` |
| 6863 | 17 | `pnl_btn_zhuandong_right` … |
| 6795 | 11 | `pnl_btn_tehuibao` / `img_tehuibao_nor/_hover/_down` |
| 6801 | 18 | `img_zhekou_tag03` / `txt_zhekou_tag` / `pnl_title_shipei` |
| 6806 | 12 | `img_bg` / `img_title` / `pnl_tag_time` |
| 7517 | 28 | `img_bg` / `img_title` / `pnl_renwu_wupin` … |

**关键限制**：这 6 个模块**互不嵌套**（父键 6795/6801/6806/6860/6863/7517 没有一个出现在子 id 里），
子 id 是 1~90 的扁平编号。也就是说这张表提供的是
**「可复用控件模块 + 模块内部布局 + 每个 ui_group 的变体」**，
而**「一个面板由哪些模块组成、模块摆在哪」不在本表**——那部分属于缺失的 base 表。

⇒ 能拿到按钮长什么样、文案是什么、贴图是哪张，但**拼不出整块面板**。


## 验证 3：没有任何一张表同时含 `HDUI` 与 `.csb`

★ 方法说明：IDE 的全文搜索会**跳过二进制文件**（这些表是 NeoX 字节码，内含大量 NUL），
直接搜 `HDUI` 会得到假的「0 命中」。本条改为**字节级遍历**
（`rglob` + `b'HDUI' in bytes`，跳过 >60 MB 的单文件），并带阳性对照。

实测（52,212 个文件 / 337 MB，耗时 26 s）：

| 检索项 | 命中文件数 | 说明 |
|---|---|---|
| `spine_path`（阳性对照） | **40** | 证明该扫描能进二进制表 |
| `.csb`（阳性对照） | **51** | 同上 |
| `HDUI` | **11** | 全部集中在 `huodong_conf` / 向导 / 跳转表 |
| `HDUI` **且** `.csb` | **0** | ← 关键 |

11 个含 `HDUI` 的文件逐个复查，`.csb` 计数全为 0：

```
huodong_conf_data.py                               HDUI=609  .csb=0
huodong_conf_data.nxs                              HDUI=602  .csb=0
ui_tutorial_data_chs.py / _kj1 / _yk               HDUI=24   .csb=0
common_jump_type_data_chs.py                       HDUI=2    .csb=0
mission_step_event_data_chs.py                     HDUI=2    .csb=0
```

⇒ 配置数据里**没有任何表**把界面视图类（`XxxHDUI`）与面板/布局关联起来。

## 验证 4：csb 文件里没有活动类名字面量

对 362 个 csb 的原始字节，逐条检索 35 条未开始活动的
`hd_class` 与 `ui_class` 字面量（UTF-8）：**命中 0 / 35**。

## 验证 5（附带排除）：入口图标也拿不到

`huodong_conf` 的 `tab_img_path`（活动入口 tab 图标）在 769 条未开始活动行里
**只有 4 条有值，且本地 `.ktx` 命中 0**。所以也无法用图标兜底做「活动卡片墙」。

---

## 所以现在的口径

| 项 | 状态 |
|---|---|
| 活动 → 主面板 | **不可确定**（验证 0~4） |
| 活动 → spine 挂点所在 csb | 可解（`hd_ui_spine`，708 行），但**语义不是主面板**，不采用 |
| 活动 → 控件模块 | **可解**（`hd_ui_scheme_reverse`，320 模块 / 90 个活动类 / 184 个 ui_group 变体），能拿到按钮、文案、贴图、模块内坐标 |
| 活动 → 面板（模块组成 + 摆放） | **不可解**：依赖缺失的 `hd_ui_scheme_data_base`（验证 1、6） |
| 名称语义候选 | 8 条，写死在 `activity_panel_candidates.json`，带 `confidence` / `evidence`，页面标「候选」 |

**要真正解开，需要两样东西之一：**

1. 含 `hd_ui_scheme_data_base` 的包体（该表随版本热更，可能只下发给实际要展示的服）；
2. 或者一次**运行时抓取**：进游戏打开该活动，记录 `load_hd_ui_scheme(ui_group_id)`
   实际用了哪份 scheme —— 这属于运行态，本项目按铁律不做。

在此之前，任何「活动 X = 面板 Y」的断言都没有数据支撑。
但 **「活动 X 的按钮/文案/贴图长什么样」已经有数据了**，可作为下一步「模块级还原」的基础。

---

# 追加（2026-11-07 晚）：把「活动 → 用哪组模块」这条**能对上的**部分做出来

上一节的结论只对「**面板组成**（谁摆在哪）」成立。复核 `huodong_conf_data` 逐行取值后发现，
行里本来就带界面指向字段，之前只看 `ui_class` 脚本是漏的：

| 字段 | 有值行数 | 含义 |
|---|---|---|
| `hd_class` | 3457 | 活动处理器类（如 `MultiOptionalLotteryHD`） |
| `ui_class` | 3152 | 界面类 |
| `use_ui` | 3100 | 1=旧界面（多走 csb）/ 2=HD 动态界面 |
| `ui_group_id` | 84 | 该活动用哪个 ui_group（**新活动才有**） |
| `use_ui_scheme` | 265 | 另一套 scheme 编号，指向缺失的基表，解不了 |

## 可复算结果（`match_activities.py`）

以 `hd_class ∈ scheme.classes` **且** `str(ui_group_id) ∈ scheme[hd_class]` 为命中：

- 3535 条带名活动 → **可拼 63**条 ｜ **仅对到类 1186** ｜ **无模块数据 2286**
- 2286 条里 **2266 条连界面脚本都不在包里**（下面这条验证）

## 验证 5：最新一批活动的界面不在包内（带阳性对照）

2026-11 正在进行的那批（周年庆）逐个查 `配置/ui/<ui_class>.py` 是否存在：

```
周年庆典广场  AnnFest2026HD   → 配置/ui/ 下无此文件
庆典烟花      CommonFireworksHD → 无
派对游戏      PlazaGameHD      → 无
周年庆锦鲤    AnnFestKoiHD     → 无
末日回响      RenewCombatSfxHD → 无
```

再做字节级检索（5951 个 `配置/ui/*.py`，逐文件 `read_bytes()` 后 `in`）：

- `b"AnnFest2026"` 命中 **0** 个文件
- **阳性对照**：同一批文件前 800 个里 `b"load_hd_ui_scheme"` 命中 **5** 个
  ⇒ 检索工具有效，0 命中是真 0，不是假阴性

即：**配置已经热更到 2026-11，但界面脚本/资源属于未入库部分**。
所以最新活动「看不到界面」不是匹配失败，是包内没有。工具现在对每条活动都会
区分这两件事：`包里无脚本` vs `有脚本但不在 90 个 HD 类里`。

## 顺带纠正一条更早的过宽结论

`配置/ui/*.py` 里 **2564 个**文件含 `.csb` 字符串（字节级），说明**很多界面确实是 csb**
（不是全都走 `load_hd_ui_scheme`）。但全树 `*.csb` 只有 **362 个**（`41_还原树` 362 +
`30_分析` 341 份副本，去重后 362），脚本里引用的 csb 绝大多数没被解包出来
（例：`AimCross.py` 引用 6 个 `ui/main_sight_*.csb`，磁盘只有 1 个）。
⇒ 修正为：**「活动界面一律不是 csb」是错的；「本包只有 362 个 csb」才是结论**。
