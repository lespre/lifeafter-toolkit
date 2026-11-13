# 全量分服奖池解析：工具链与产物（v1 · 2026-11-07）

> 目标功能：**给出每个服、每个池、每一格的具体奖励**（item_id / 数量 / 中文名 / 概率 / 到期 / 广播），
> 并区分「经典服 base」与各分服（kj1 简单生存服、kjxq、yk、ykxq）的差异。
>
> 本文是从这个功能**反推**出来的工具改造记录。旧研究（路径裁决、广播否决、六源闭环）见
> `LOTTERY_REWARD_BRANCH_RESEARCH.md`；本文只讲「为了全量分服，工具和流程改了什么」。

## 0. 一句话结论

**能出，而且已经出了。** 116,415 行 / 5 个服 / 每服全量 23,281 格；
中文名覆盖 99.9%，概率覆盖 92%；base ↔ 各服的 8 替换 + 5 新增逐格可查。

## 1. 功能缺口到底是什么

不是「拿不到奖励」——`LOTTERY_POOL_RESOLVED_v01.jsonl` 早就有 24,041 行
`(池, 格) → item_id + 数量`。缺的是三样：

| 缺口 | 表现 |
|---|---|
| **全量** | 只有台面上的池；每服只有自己 overlay 的那几百行，看不到「这个服完整有哪些格」 |
| **分服** | 5 个服平铺在一个文件里，没有「某服最终视图」；跨服同 `(pool, slot)` 会撞车 |
| **具体** | 没有中文名 / 概率 / 到期 / 广播；名字只能靠 `ITEM_MASTER` 桥补到 82.5% |

## 2. 反推出来的五个工具缺口（及修法）

### D1 消费层看不见无名大表

`pe_source.paths_of()` 只认 `com/cdata/<表>.py`。而 `reward_pool_data` 这份是 815B 的
`MergedTableData(_base,_inc,_del)` **分发壳**，本身 0 行；真数据体在
`pe/配置/Documents/script.py314.lc.npk/_未命名/`，文件名只有行号。

**修**：`paths_of` 先判「是不是真表体」（小文件才读内容找 `x{` 帧），不是就走
`unnamed_registry.paths_for_table()` 按 `file_id` 反查。

### D2 无名大表没有身份登记

**修**：`rules/unnamed_table_registry.yml` 建契约，键是 `file_id`（跨版本不变），行号只作人工核对。
**同一逻辑表必须按 `component` 分开登记** —— 实测 `reward_pool_data` 的 base 与 ykxq
是两个不同的 `file_id`，混在一起会把两个服当成同一张表。

### D3 跨服串号：`(pool, slot)` 不能当全局键

`toolkit_cli.py` 的 `tg[(pool, slot)] = t` 让后写的覆盖先写的。
实测 `pool 391513 slot 2`：base = `660055 裂变效应`，kj1 = `660023 极光狙击`，
于是 `lottery show` 打出「`item_id=660055` 名字=裂变效应 原始=`[660023]`」——**名字和值对不上**。

**修**（两处，都在 00 工具层）：

1. `_lot_target_rows` 保留 `component`；`tg` 同时建 `(component, pool, slot)` 精确键，
   取值走 `_tg_of()`，有服维度就用服维度。
2. 新增 `_eff_iid()`：**行内原始值优先于 target 索引**。因为上游 targets 只收
   「已发布」组件（隔离的 kj1/kjxq 那 474 行根本不在里面），索引给出的永远是 base 的值。

### D4 上游把 kj1/kjxq 整体判为 `unsafe` 隔离

`build_lottery_pool_resolved_v01.py` 里 `reliability_state="unsafe"` +
`dataset_partition="quarantined_records"`，**474 行（237×2）全部隔离，不参与任何结论**，
而代码里没有留下这个判定的判据。

**不沿用、也不推翻**：新产物保留 `partition` 字段原样，改用自己的一套可复算门禁
（见 §5）。要按上游口径过滤时用 `component + partition`。

### D5 没有分服产物 / 没有门禁

**修**：`build_lottery_servers.py` 产出 + `check_lottery_servers.py` 验收（G1~G8）。

## 3. 五个服的数据体在哪（这是「分服」的物理前提）

| 服 | 角色 | data 体 | 有名/无名 | 行数 | 池串 |
|---|---|---|---|---|---|
| base | base | `_未命名/00022771.bin` | **无名** | 23,902 | 12,511 |
| kj1 | channel | `oversea/reward_pool_data_auto_oversea_data_kj1.py` | 有名 | 237 | 562 |
| kjxq | channel | 同上 `_kjxq.py` | 有名 | 237 | 562 |
| yk | channel | 同上 `_yk.py` | 有名 | 162 | 471 |
| ykxq | channel | `_未命名/00019997.bin` | **无名** | 162 | 470 |

⇒ **5 个服里有 2 个（base、ykxq）只能靠 `file_id` 找到**。按文件名找会漏掉一半，
这就是为什么「按路径找表」这条路从来走不通。

## 4. 合成口径（可复算）

1. **权威键**取上游冻结产物的 `lookup_key.(pool_key, item_no)`，**不自己重解**。
   理由：该键单组件内唯一性 100%（base 23,281 / kj1 237 / kjxq 237 / yk 143 / ykxq 143 全唯一），
   而 `decode_table_rows` 的 `inline_groups[0]` 实测是**下一行**的键组（错位一格），
   拿它当键会得到整批假差异。
2. **中文字段按 reward 值挂载**（不是按槽位）：上游 `reward_raw` 与树内 `reward` 组
   `[item_id, qty]` 直接相等。覆盖率 base 23,268/23,281 = **99.9%**，
   kj1/kjxq 237/237 = **100%**，yk 142/143。
3. **全量 = base 每一格都在，本服 overlay 叠上去**，`diff` 五态：

   | diff | 含义 |
   |---|---|
   | `base` | base 服自己 |
   | `inherit` | 本服没覆盖这一格，沿用 base |
   | `same` | 覆盖了，但奖励与 base 相同（只补了中文名/概率/到期/广播） |
   | `replaced` | 覆盖了，奖励被换 |
   | `added` | base 没有这一格，本服新增 |

4. **`note` 是策划备注，不等于道具正式名**：同 reward 存在多种写法（5,050 个 reward 里 561 个），
   用 `note_conflict=true` 标出。展示时 `item_id + note` 并列，别只给 note。

## 5. 门禁 G1~G8（`check_lottery_servers.py`）

独立于生成器：只读产物 + 上游冻结产物，**重新算一遍**。

| # | 检查 |
|---|---|
| G1 | schema / `runtime_final_state=unresolved` / 行数与 manifest 一致 / 每行合法 JSON |
| G2 | 每服 `(pool_key, item_no)` 唯一 |
| G3 | `reward_raw` 与上游逐字一致（`inherit` 行本就不在上游，属正常） |
| G4 | `diff` 可由「产物自身 + 上游各服覆盖键集」重算 |
| G5 | `note` 覆盖率（base ≥95%、channel ≥90%） |
| G6 | 每服非空（缺数据必须显式说明，不能静默出空） |
| G7 | 每个服的数据源 state = `verified` |
| G8 | 每行必有 `component`，且属于 manifest 声明的服（禁止混排） |

退出码 2 阻断发布。实测全过。

## 6. 产物与用法

```
02_wiki/web/site_data/LOTTERY_POOL_SERVERS_v01/
  manifest.json     # schema / 上游 sha256 / 每服统计 / 数据源 / 口径 notes
  rows.jsonl        # 116,415 行（5 服 × 23,281 + 13×2）
```

命令：

```bash
PY=00_规范与工具/环境/venv/Scripts/python.exe
$PY 02_wiki/web/tools/build_lottery_servers.py           # 预览
$PY 02_wiki/web/tools/build_lottery_servers.py --apply   # 落盘（幂等：rows.jsonl sha 不变）
$PY 02_wiki/web/tools/check_lottery_servers.py           # 门禁
$PY 02_wiki/web/tools/check_unnamed_table_registry.py    # 无名大表契约校验
```

查询（脚本/看板都能用）：

```python
import sys; sys.path.insert(0, "02_wiki/web/tools")
import lottery_servers as LS
for r in LS.pool_of("kj1", 391513):
    print(r["item_no"], r["item_id"], r["note"], r["prob_note"])
LS.diff_of("kj1")        # 该服相对 base 的全部差异格
```

## 7. 实测结果

每服全量行数：base 23,281｜kj1 23,286｜kjxq 23,286｜yk 23,281｜ykxq 23,281。
中文名覆盖 99.9%~100%，概率覆盖 92%。

kj1 / kjxq 相对 base：`inherit 23,049 / same 224 / replaced 8 / added 5`。

八个替换格：

| 池 | 格 | base | kj1 / kjxq |
|---|---|---|---|
| 390985 | 0 | 103101 | 103018 配方:医疗无人机 |
| 390985 | 4 | 134527 | 151994 能量电池 ×20 |
| 391475 | 0 | 103101 | 103018 配方:医疗无人机 |
| 391475 | 3 | 139008 | 241890 霰弹枪异变核芯自选箱 |
| 391475 | 4 | 241646 | 151994 能量电池 ×20 |
| 391508 | 2 | 132099 ×4 | 151783 重构分子 ×200 |
| 391508 | 4 | 150059 ×400 | 151783 重构分子 ×400 |
| **391513** | **2** | **660055 异变核芯-裂变效应** | **660023 异变核芯-极光狙击（prob 0.03472）** |

最后一行与公示文本「潜龙宝珠概率公示第 5 项 3.47%」、`ITEM_MASTER` 反查、
PE 树行 note 四方逐字一致 —— 这是「分服奖励确实不同」的闭环证据。

五个新增格都在 `pool 391711`：660081 淬焰燃锋 / 660000 疾影火刃 / 660001 绝对零度 /
660002 脉冲闪电 / 660030 侵蚀效应，各 `prob_note=0.00999`。

yk / ykxq 相对 base：`inherit 23,138 / same 143`，**没有任何奖励被替换**（只补字段）。

## 8. 还没解决的

| 项 | 状态 |
|---|---|
| `oversea_table_map_data.py`（1.9MB，服→表映射） | 不是标准 0x76/0x56 表体，暂时解不开；不影响分服解析（服清单取自冻结产物 manifest） |
| `runtime_final` | 恒 `unresolved`。`optional_pool_replace_data`(185 行) + `optional_version_data` 会在运行时替换奖励，静态结构 ≠ 当前实发 |
| `dispatch=child_pool` 的 43 格 | 指向子池，需要递归展开；本产物原样保留 `dispatch` 字段，未展开 |
| 概率语义 | `prob_note` 是静态标注，不含保底/pity 算法；`initial_weights` 也在，但权重换算规则未验证 |
| 无名层还有 298 个未登记大表 | 只按需登记（本次只登记 `reward_pool_data` 的 base + ykxq），不一次性铺开 |
| 板级展示 | 本产物只到数据层，未接任何板；要上线需要单独定口径与卡片结构 |
