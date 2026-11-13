# 界面还原（CSB → 本地网页）

把游戏里的活动/抽奖面板，从**原始布局文件**还原成本地可打开、可缩放的网页。
只解静态资源，不连客户端、不碰网络协议。

## 边界

- ✅ 做：CSB 布局、贴图、文案、基础颜色/透明度/旋转、入场动画末帧
- ❌ 不做：服务端模拟、协议还原、改客户端、绕过校验
- 交互（点按钮出什么）不在范围内，页面只呈现界面的稳定态

## 命令

```bash
PY="00_规范与工具/环境/venv/Scripts/python.exe"
T="02_wiki/web/tools/ui_preview"

$PY $T/csb2json.py --all                 # 全量解析体检（362 个面板）
$PY $T/csb2json.py <csb 名> --stdout     # 单面板看摘要
$PY $T/csb2html.py <csb 名>              # 生成单面板网页
$PY $T/export_all.py                     # 批量导出全部页面 + 缩略图
$PY $T/export_all.py --no-thumb          # 只出页面（约 10 秒）
$PY $T/build_index.py                    # 刷新 _ui_preview/index.html 入口页
$PY $T/ui_scheme.py                      # 解 hd_ui_scheme_reverse → 控件模块库 + 预览页
$PY $T/ui_scheme.py --dump-only          # 只落 _ui_preview/scheme/scheme.json
$PY $T/composer.py                       # 画布拼装器 → _ui_preview/composer/index.html
$PY $T/composer.py --check               # 体检：数据源在不在、页面标记齐不齐
$PY $T/match_activities.py               # 活动 → (hd_class, ui_group) 匹配表
```

产物落在项目根 `_ui_preview/`：`<面板名>/*.html`、`assets/*.png`（全局去重贴图）、
`thumbs/*.png`、`index.html`、`scheme/index.html`。不写进 `02_wiki/web`，不改动 35 个现有板。

## 管线

```
资源/ui/*.csb ──csb2json──> 节点树 JSON ──csb2html──> HTML
                                  │                     ▲
                        NodeAction 末帧          .png 逻辑名 → 同名 .ktx 解码
                        状态后缀折叠                      → assets/<目录>__<名>.png

配置/com/cdata/hd_ui_scheme_reverse_data.py
   ──ui_scheme──> 控件模块 JSON ──> scheme/index.html
   (0x36 映射帧 → 0x27 列表帧 → 0x86 行；按 (活动类, ui_group_id) 分组)
```

**两条线是并列的，不是同一件事**：上面出的是 csb 静态面板；
下面出的是活动界面的**可复用控件模块**（活动界面本身不是 csb）。
为什么拼不出整块面板，见 `ACTIVITY_PANEL_EVIDENCE.md`。

## 口径（可复算，写在代码里）

| 项 | 规则 |
|---|---|
| 文件格式 | CSParseBinary（flatbuffers），version 串 `2.1.0.0`；手写 vtable 读取，无第三方依赖 |
| 选项表层级 | `Options.data` 一般是具体 `*Options`，其 0 号字段才是 `WidgetOptions`；`Node` 类被导出器拍平，`data` 本身就是 WidgetOptions（按 vtable 长度 46 判定） |
| 可见性 | `VisibleForFrame` 字段缺省即 **true**（schema 默认值），不是 false |
| 文本方向 | CSB 内文本按**字符倒序**存储，显示前反转 |
| 稳定态 | `WidgetOptions` 存的是时间轴**首帧**（常见 alpha=0、位置在屏外）。位置/缩放/旋转取 `NodeAction` **末帧**（收敛处）；`Alpha` 取整条轨道的**最大值**——`IntFrame.value` 缺省为 0，末帧省略字段≠末帧 alpha=0，按末帧取会把已淡入完成的面板整片淡出（实测 40+ 个面板变空白）。节点 alpha 最终取「设计值与轨道最大值」的较大者，动画只会让元素更明显，不会让设计上不透明的面板消失 |
| 状态折叠 | 同一父节点下同前缀、不同后缀（`_nor/_down/_dis/_disable/_sel/_off/_on`）的贴图是同一控件的多状态；静态预览只留一个，优先 `_nor`，其余标 `hiddenByState` 并在页面用 class 隐藏（可一键叠回） |
| 全隐兜底 | 若整页按层级算下来**一个可见贴图都没有**，把 `alpha=0` 且带贴图/子节点的节点放开为 255（标 `alphaRelaxed`）。只做整页级兜底，不逐节点放开。实测触发 2 个面板 |
| 贴图命名 | CSB 里是 `.png` 逻辑名，实际文件名同名的 `.ktx`；解码后按 `目录__文件名` 存进全局 `assets/`，避免不同目录同名互相覆盖 |
| 坐标 | Cocos y 向上、以锚点定位：`left = px - ax*w`，`top = parentH - (py - ay*h) - h` |
| 数据源 | 只用 `01_索引与产物/41_还原树/pe`（可用 `LA_RESTORE_ROOT` 覆盖） |

## 实测

- 362 个 CSB **全部解析成功**，27,996 个节点，平均 77 节点/面板
- 类型分布：Panel 12109、ImageView 10593、Text 4468、ScrollView 261、LoadingBar 89、
  Sprite 73、Particle 18、TextField 8、TextAtlas 8、Button 3、CheckBox 2
- 状态折叠：**187 个面板共 691 组**多状态贴图被折叠（每个面板实际隐藏数见其 meta 的 `state_hidden`）
- 贴图引用 596 处落不到本地 `.ktx`，**148 个面板**有缺图（多为动态下发或跨面板素材），按缺图处理，不补假图
- 全量产物：362 页 + 362 缩略图，`_ui_preview/` 约 275MB（其中全局 `assets/` 为去重贴图）
- **活动控件模块**（`ui_scheme.py`）：`hd_ui_scheme_reverse` 320 行 / 6 行未解 →
  **90 个活动类 / 664 个 (类, ui_group) 组合 / 2,512 个控件模块 / 30,599 个控件**；
  其中 14,319 个控件带贴图，**7,156 个解出 PNG**（50%，其余本地无 `.ktx`），
  8,184 个带模块内坐标。页面 `_ui_preview/scheme/index.html`（含 JSON 共约 14MB）。
  加了控件模块贴图后 `_ui_preview/` 约 **623MB**（assets 7,978 张）。

## 已知近似（渲染层，不伪装成原样）

- **字体**：原位图字体，网页用系统字替代，字号/颜色/对齐取自数据，字宽会有差异
- **占位文案**：不少 Text 是设计期占位（如「家具名称页签」），运行时由脚本按配置改写；
  静态预览只显示 CSB 里存的那份
- **多层遮罩叠加**：带多标签页/多套装切换的面板，各层自带半透明黑色遮罩，
  静态渲染会把它们**同时**叠上，整体偏暗甚至近黑（如
  `huancai_diancang_choujiang_ssjx_v1`）；游戏内只激活其中一层。
  这是「不知道运行时哪层生效」导致的，不做猜层。
- **设计上就是空的 10 个面板**：`main_all_mark_single`、`common_guizesm_big_new`、
  `common_guizesm_zousigui(_new)`、`gongfang_binggui_left_content`、
  `gongfang_binggui_right_content`、`huancai_diancang_choujiang_zs_item`、
  `choujiang_shenyutonghua_tc_item_s`、`jishou_qiugou_fabu_chenggong_tc`、
  `huodong_buhuiliuchoujiang_item_jiangli_v1`——它们的 ImageView 在 CSB 里**没有贴图**，
  图标由脚本运行时塞进去，所以静态就是空的。如实显示，不补图。
- **动效**：spine / Particle / 逐帧时间轴只取末帧，不播放
- **父级旋转/缩放下的子节点**：子坐标按未缩放父尺寸计算，父级带缩放时会有偏差

## 已核实「不需要做」的两项

- **九宫格**：全部 **1788 个** `Scale9Enabled=true` 节点的实际尺寸与其 `scale9Size`
  完全相等（差值 0 处）⇒ 本包内没有需要九宫格拉伸的场景，按 100%×100% 铺贴即可。
  若后续面板出现两者不等，再补 `capInsets` 三/九宫格。
- **活动 → 面板的注册表**：活动界面由 `hd_ui_scheme` 配置驱动。
  `com/cdata/hd_ui_scheme_data.py` 只是合并壳，`hd_ui_scheme_data_base.py` 不在包内，
  `hd_ui_scheme_reverse_data.py` 是 444KB 二进制表，`vm_cdata_table` 会抛
  `unhashable type: 'list'`、`script_table_replay` 得到 0 行；`ui_class` 脚本里也不含
  `.csb` 字面量（反编译常量表里只有方法名）。**所以活动→面板无法从数据推出**，
  只在 `activity_panel_candidates.json` 里按命名/类型语义给出**候选**（带依据与置信度），
  页面按「候选」展示，不写成事实。

## 活动界面（不是 csb 的那条线）

活动界面由 `ui_class` 脚本调用 `load_hd_ui_scheme(ui_group_id)` **动态搭建**，
包里没有对应 csb。四条独立验证都指向「活动 → 面板」不可由数据推出，
证据与复算方法见 **`ACTIVITY_PANEL_EVIDENCE.md`**（含一次被证伪的检索方法：
IDE 全文搜索会跳过二进制表，必须做字节级遍历 + 阳性对照）。

`ui_scheme.py` 能解的是同族的 **reverse 表**，它给的是**可复用控件模块**
（按钮三态组、折扣标签、任务格…），带 `widget_name / texture / pnl_offset /
pnl_size / str / font_size`，并按 `ui_group_id` 存多套变体。
**模块之间互不嵌套**，所以拼不出整块面板——「面板由哪些模块组成 + 摆在哪」
在缺失的 `hd_ui_scheme_data_base` 里。

## 画布拼装器（`composer/index.html`）

**默认从「活动」进**：列出 `huodong_conf` 实际配置的活动（进行中在最前，按结束时间排），
每条标明 `N 模块 / M 控件`、`仅对到类` 或 `无界面数据`，点一下直接跳到那组模块。
切「按控件类」才回到老的 90 类浏览。

- **不猜位置**：模块落点、缩放、层级全由人拖；程序只忠实还原模块**内部**的 `pnl_offset`
- **未定位控件不再是「?」墙**：按基名**归并状态变体**（`_nor/_down/_hover/_dis` 算一个），
  贴图按真实比例铺、按有无贴图排序，文字槽标 `文`、容器标 `框`、粒子标 `特`，右上角角标是变体数
- **空槽显式化**：有坐标但没有贴图/文案的控件画成虚线小框并写上控件名（如 `txt_time`），
  不再是一块说不清的空白——内容本来就是运行时塞进去的
- **全部铺上**：把当前组模块按 3 列「零件总览」网格铺开，超大的模块自动等比缩到格子里
- 其余：图层列表、撤销/重做、`Ctrl+D` 复制、`[`/`]` 层级、`Alt+拖` 不吸附、可换画布/底图

### 为什么有些活动点不开

`match_activities.py` 用 `hd_class ∈ 模块表` 且 `ui_group_id` 那组存在才算「可拼」：
3535 条活动里 **63 条可拼 / 1186 条仅对到类 / 2286 条无模块数据**，
其中 2266 条**连界面脚本都不在包里**（配置已热更到 2026-11，界面属未入库部分）。
点击时会当场说明是哪一种，不糊成「加载失败」。证据见 `ACTIVITY_PANEL_EVIDENCE.md` 验证 5。

### 导出单文件（自包含 HTML）

页面点「导出单文件」→ 得到 `bake_<活动类>.json`（里面是**已渲染好的画布 DOM**），再：

```bash
$PY $T/composer.py --bake bake_XXX.json          # 同目录生成 bake_XXX.html
$PY $T/composer.py --bake bake_XXX.json --out 成品.html
```

贴图按 `../assets/x.png` 逐个换 base64 内联，输出可以直接发人、离线打开。
**Python 不重算几何**——只做「换图 + 套壳」，避免和页面两套渲染逻辑漂移。
缺图会在页脚如实写「缺 N 张」，不补假图。

## 下一步（按需）

1. 入口页加「按活动时间线」视图（已有未上线清单，缺历史活动归档）
2. 拼装器支持「导出为单文件 HTML」（把当前排布烘成一页给别人看）
3. 等含 `hd_ui_scheme_data_base` 的包体；拿到后 `ui_scheme.py` 可直接复用同一套
   0x36/0x27/0x86 解析器读出面板组成，拼装器就能改成「按真实组成自动落位」
