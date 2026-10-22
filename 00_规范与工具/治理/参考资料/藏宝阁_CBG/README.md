# 藏宝阁（CBG）前端配置 · 外部参照源

> **性质：官方站点前端配置，不是拆包数据。**
> 用途：给 `common_item_data` / `all_equips_data` / `weapon_skin_data` 这类
> 「拆包表文本槽错位、不敢拿去命名」的地方，提供一份**官方口径的物品名 / 图标 / 品级**做交叉校验。
> **不含任何战斗数值**（无伤害、无属性数值），品级只是交易站展示档位（1~7）。

## 来源

| 项 | 值 |
|---|---|
| 入口 | https://mrzh.cbg.163.com/ （网易《明日之后》藏宝阁，官方交易站） |
| 文件 | `https://cbg-mrzh.res.netease.com/js/game_auto_config.js` |
| 同目录 | `format_game_auto_config.js`（交易站筛选器下拉枚举） |
| 加载方式 | 站点 `dist/main.js` 里的路由守卫 `gameConfigFirst`：`$.getScript(...)` → `window.CBG_GAME_CONFIG` |
| 形态 | 单行 JS，`var CBG_GAME_CONFIG={…}`，约 25 MB，无版本号（CDN，`Cache-Control: max-age=300`） |
| 抓取记录 | `_manifest.json`（URL / 时间 / HTTP 头 / sha256 / 大小 / 内容变更前后哈希） |

## 结构

```text
藏宝阁_CBG/
├── raw/                      上游原始字节（只读，校验基准）
│   ├── game_auto_config.js           24,991,849 B · 75 个顶层键
│   ├── format_game_auto_config.js       318,243 B · 34 个顶层键
│   └── _evidence/dist_main.js          站点 dist/main.js，证明「谁加载了它」（grep gameConfigFirst）
├── json/                     ★ 规范化后比 raw 小（raw 是 \uXXXX 转义，这里直接 UTF-8）
│   ├── game_auto_config/<顶层键>.json   一键一文件 · 17.8 MB · 读哪个键就只读哪个
│   ├── format_game_auto_config/<…>.json  0.2 MB
│   ├── game_auto_config.json          整份合并 · 17.8 MB（要全量时用）
│   ├── format_game_auto_config.json
│   └── _index.json                    键 → 条目数 / 字节数 / sha256
├── _manifest.json
└── README.md
```

**`_classic` 双份**：除 `merged_server_mapping` 外，每个键都有一份 `_classic` 双胞胎，
条目数基本一致（如 `weapon_skin_data` 138 / `_classic` 137）。
两套是同一份数据的两个服务器口径，**不要混用**：判断「某条是不是新版独有」时对比两者差集。

## 能用来干什么

| 键 | 条目 | 用途 |
|---|---|---|
| `common_item_data` | 24,856 | id → 显示名 + 图标 + 品级。**皮肤 id（1110xxx 段）139 条全在这里** |
| `all_equips_data` | 1,807 | 装备 id → 名称 / 描述 / 图标 / 品级 |
| `weapon_skin_data` | 138 | 皮肤 id → 名称 / 图标 / 品级（`common_item_data` 的子集投影，同名率 138/138） |
| `fashion_data` | 10,811 | 时装/头饰 → 名称 / 图标组 / 品级 |
| `attribute_data` | 515 | 属性显示定义：`s_name` 中文名 · `s_percent` 是否百分比 · `s_neg` 正负向 · `ndigits` 小数位 |
| `nucleus_entry_data` | 87 | 核芯词条文案模板（含 `{0}{1}` 占位） |
| `tactic_equip_data` | 71 | 战术装备 → 各等级描述 |
| `illustration` | 9 | 图鉴总量分母（成就 2407 / 怪物研究学 1800 / 食谱 2936 …） |
| `merged_server_mapping` | 1,577 | 合服映射（旧服 id → 新服 id） |
| `player_appear_data` / `appear_id_2_fashion_id` | 5,561 / 4,466 | 外观部件 → 时装 id |
| `recipe_ui_type_name` | 22 | 配方大类中文名（武器/工具/结构/无人机…） |
| `zx_conf_data` / `zx_level_data` | 2 / 5 | 皮肤「专属」四档（幻颜/淬饰/天华/绝影）+ 对应色值 |
| `format_…/weapon_skin` `accessories` `fashion` … | 34 键 | 交易站高级筛选的下拉枚举（分类 → 可选项） |

## 不能用来干什么（边界，别越界）

- ✗ **取战斗数值**：没有伤害倍率、属性点数、成长曲线。
- ✗ **当拆包数据源**：它不进 `41_还原树`（那边只放从容器还原出来的东西）。
- ✗ **判「未上线」**：交易站只挂能交易的，官方配置里有 ≠ 游戏内已上线 ≠ 玩家能拿到。
- △ **命名口径**：这是交易站展示名（如 `11100061` = `傲隼睨视（14天）`，带限时后缀）；
  写进 wiki 前要去掉限时后缀，别把 `（14天）` 当皮肤名。

## 怎么更新 / 校验

```bash
PY=E:/la拆包项目/00_规范与工具/环境/venv/Scripts/python.exe
TOOL=00_规范与工具/工具/工具库/01_解码定位复原/客户端逆向/cbg_reference.py

$PY $TOOL fetch     # 重新下载 raw/（内容变了会打印 旧 sha256 → 新 sha256）
$PY $TOOL build     # raw/ → json/（一键一文件 + _index.json）
$PY $TOOL check     # 质检：manifest 哈希一致 / 一键一文件 / 每条能重解析 / _classic 配对
$PY $TOOL keys      # 人看：顶层键与条目数排行
$PY $TOOL all       # 三步串跑
```

`check` 退出码 0 = 全过；1 = 有 FAIL（哈希不符 / 缺键 / 内容不一致）。
**每次 `fetch` 后必须 `build`**，否则 `json/` 还是旧内容（`check` 会因内容不一致报 FAIL，不会静默放过）。

## 已做的交叉核对

见 `01_索引与产物/30_分析/藏宝阁参照_皮肤表交叉核对_20261019.md`（三方对账：CBG 138 / 内部索引 138 / 面板 128）

**结论速记**：CBG 的 `weapon_skin_data` 与内部正源 `01_索引与产物/10_索引/items/common_item_names.json`
在 138 个皮肤 id 上**名字逐字一致 138/138** ⇒ 互证成立。
⇒ **补名首选内部索引**（同快照、可回放）；CBG 的角色是**独立第二源**（不同体系、可交叉验证），
而不是「唯一命名源」。写进 wiki 时按 `source=cbg` 标第二源，别当拆包正源。
