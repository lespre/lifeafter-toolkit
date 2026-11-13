# 奖池「具体奖励」破解路径研究（v3 · 2026-11-07）

> **v3 只改根因判定，不动 v2 的任何业务结论**（§1/§2/§4/§5 全部有效）。

## 0-A. ★★ v3 更正：v2 §3 / §6-P0 的「数据没落盘」是错的

2026-11-07 追加取证（`90_临时/probe_unnamed_tables.py`）**推翻了 v2 的核心归因**。

| v2 说法 | v3 实测裁决 |
|---|---|
| 「匿名大 entry 没落盘，经典服 1.09MB 数据 + 655KB 中文池只在当年临时目录存在过」 | ❌ **完全错误。文件一直在树里** |
| 「12 张壳 × 3 分片 = 36 张分片全缺 ⇒ 还原树构建/保留系统性遗漏」 | ⚠ 前半对（`com/cdata/` 下确实没有分片文件），但**归因错**：真实数据表不是那三张分片，而是 `script.py314.lc.npk` 里的编译表 blob，落在 `_未命名/` |
| 「base 中文名/概率/到期时间丢了，只能靠 `ITEM_MASTER_v03` 补 82.5%」 | ❌ **没丢**。中文池里 12,511 条串、45 个字段名全在，23,898/23,902 行自带中文 `note` |
| 「需用户开口子按 fid 从当前 npk 补录」 | ❌ **不需要**。数据已在本地树内，缺的只是「行号文件 → 逻辑表名」的映射 |

**真实落点**（`01_索引与产物/41_还原树/pe/配置/Documents/script.py314.lc.npk/_未命名/`）：

| 文件 | 大小 | 实测内容 |
|---|---|---|
| `00022771.bin` | 1,119,971 B | 经典服 `reward_pool_data` **完整行表**：`body_of()` + `BT.decode_table_rows()` 解出 **23,902 行** |
| `00011262.bin` | 661,115 B | 配套 `string_pool`：`MP.pool_of_file()` 解出 **12,511 串**，前 10 个即 `expiration_time / reward / note / initial_weights / prob_note / …` |

配池后字段名还原 **45 个**（`note` / `prob_note` / `expiration_time` / `broadcast_content` / `reward` / `desc` / `weights_x_count` …），**23,898/23,902 行带中文 note**；「异变核芯-裂变效应」「异变核芯-极光狙击」均命中，`prob_note=0.03472` 与公示 3.47% 一致。

⚠ 版本差异：当前树是 **23,902 行 / 1,119,971 B**，冻结产物锁定的 BA8 快照是 **23,281 行 / 1,091,069 B** —— 不同版本，**行数与字段值不可直接混排**，但都属「本地静态配置」。

### 0-A.1 真正的根因（三层，回答「是不是文件名不到位」）

1. **打包层**：`script.py314.lc.npk` 的编译表 entry **只有 64-bit `file_id`、没有游戏内路径**。
   `npk_index.entries` 表结构可证：`layer / row / file_id / offset / packed / declared / flag`，**无 `name` 列**。
2. **名字恢复层**：`pe_index.fid_names`（416 万条）只能给出**占位名**
   `Documents\script.py314.lc.npk\_未命名\00022771.bin`。`restore_tree.materialize()` 的规则是
   「有真名按真名落，无名落 `_未命名/<行号>.bin`」(`include_unnamed=True` 默认) —— **落盘动作是对的、文件完整保留了**。
3. **消费层（真正断点）**：`merge_pe_cdata.py` / `merge_pe_config_tree.py` 只汇总 `com/cdata/` 子目录，
   `pe_config_merge_ledger_v2.json` 里没有 `_未命名/`；`pe_source.paths_of()` 等所有重建脚本
   **只认 `com/cdata/<表名>.py`**。⇒ `_未命名/` 那半边（Documents 层 4,394 个文件 / 114.9 MB，
   其中 >100KB 的 88 个 / 97.4 MB）**从来没进入「配置树」的视野**。

项目里其实有人**手工**补过一次映射：`pe_source.py` 硬编码 `COMMON_ITEM_FID = "B42760CCA41DBC25"`，
对应 `90_表缓存/base_B42760CCA41DBC25.py`；但那是**逐表一次性硬编码，没规模化**。

⇒ 准确说法：**不是「还原文件名没起对」，也不是「文件被删」，而是「只做了第一层名字恢复，缺第二层
`(_未命名/行号文件 或 file_id) → 逻辑表名/配对池` 的反向注册表」**。工具能解、数据也在，是索引/账本层丢了关联。

### 0-A.2 根治方案（三层，待用户定口径后落地）

| 层 | 做法 | 状态 |
|---|---|---|
| L1 注册表 | `02_wiki/rules/unnamed_table_registry.yml`：**主键 `file_id`（不是行号）**，每条带 `container` 消歧，登记 `data` / `pool` 两个 fid。只放已实测确证项，禁止脚本自动写入 | ✅ **已落地**（2026-11-07，只登记 `reward_pool_data` 一组） |
| L2 验收关卡 | `02_wiki/web/tools/check_unnamed_table_registry.py`：按 `(file_id, container)` 从 `fid_names` 反查当前落盘路径 → 实测解表/解池 → 报「登记项是否命中」+「未登记大表清单」。**不自动配对、不猜逻辑名** | ✅ **已落地**（只读，退出码 2 可挂门禁） |
| L3 消费层 | `pe_source.paths_of(stem)` 增加「注册表 → 无名大表」回退分支 | 待建（涉及口径，需用户定） |
| L4 流程挂接 | 把 L2 校验挂进还原树构建/归一后的固定 pass | 待建（项目目前**无**还原树侧统一编排器；`pipeline_graph.yml` 是板级执行图，语义不符，不改它） |

**L1/L2 落地实测**：
```
[ OK ] reward_pool_data  data D558884A36C972C5  23,902 行 → …/_未命名/00022771.bin
[ OK ] reward_pool_data  pool 69E58821939CB515  12,511 串 → …/_未命名/00011262.bin
未登记的可解大表 298 个（主表 170 / 池 128），只告警不阻断
```
⇒ 这个 298 说明**缺映射是系统性、不是个别表**：整棵 `pe/配置/` 下所有 `_未命名/` 目录里，
能解但没身份的编译表比已登记的多两个数量级。L1 目前只认了奖池一组，其余交人工逐类判定。

配对判据必须**可复算**：用冻结产物 manifest 的 `file_id` + `fid_names` 占位名做精确关联；
⚠ 不能用「还原字段数最多」贪心 —— `probe_unnamed_tables.py` §3 实测 8 张主表会全假配到
同一个 6,144 串大池。特征签名只作校验，不作唯一依据（符合「关系推断须全量一致率验证」铁律）。

---

> 问题：想拿到**奖池里的具体奖励**，且**经典服(base) 与 简单生存服(kj1) 不同**。
> 现有两条思路：① 破解宣传展示页；② 从广播解析大奖。
> 数据源：**只用** PE 还原树 `01_索引与产物/41_还原树/pe/配置` + `02_wiki/web/site_data` 冻结产物，
> 不扫线上 npk。全部数字由 `90_临时/probe_lottery_rewards{,2,3,4,5,6}.py` 与
> `90_临时/probe_p0{,b,c,d,e}*.py`、`probe_p1{,b,c,d,e,f,g}*.py` 实测，可复算。
>
> 纪律：不猜数、不伪造 locator_chain；静态配置 ≠ 运行时最终发奖（见 §8）。

---

## 0. v2 修订摘要（★ 先看这里）

v1 有 **三处结论被本轮实测推翻**，以 v2 为准：

| v1 说法 | v2 实测裁决 |
|---|---|
| P0「base 815B 是字节码空壳，修 `script_table_replay` 重放器就能拿 base 全量行」 | ❌ **证伪**。它是 `SplitTableData/MergedTableData` 的**模块分发壳**（引用 `_base/_inc/_del`），本身 0 行；修工具也拿不到数据。且三张分片**根本没进 PE 还原树** —— 是还原树构建/保留缺口，不是解析失败 |
| §2.3 规则 3「行复合键 `(pool_id, slot)` 在 `row.raw.inline_groups` 首个二元素组」 | ❌ **证伪，且会产出整批假差异**。实测那是**下一行的索引键组**（键-行错位一格）。正确唯一来源 = 冻结产物 `lookup_key.pool_key / item_no`（来自 0x7B 索引尾 `index_key_group_offset`） |
| §5 P3「base 侧 pool 390477 有 6 行、`item_no=0` 重复 3 次 ⇒ 禁按 `(pool_id,slot)` 对照」 | ❌ **误述**。base 的 `(pool,item_no)` **23,281/23,281 全局唯一**；390477 只有 4 行（item_no 0~3，reward 分别 35542 / 170217 / 170218 / 9883×24）。**按正确复合键对照是成立的** |

**v2 新增成果**：拿到**完整、可复算的双服奖励差异清单** —— kj1 overlay 237 行里
`232 行命中 base 同键`，其中 **224 行奖励相同**（overlay 主要补中文名/概率/到期/广播），
**8 行奖励被替换**、**5 行新增**。第 8 行正是公示第 5 项「裂变效应 → 极光狙击」，精确落在
`(pool=391513, item_no=2)`。详见 §5。

---

## 1. 对两条现有思路的裁决（实测，v1 结论不变）

| 路径 | 能给什么 | 不能给什么 | 裁决 |
|---|---|---|---|
| ① 宣传展示页 | 完整奖励**名字 + 概率**（24 个公示块）；展示位 1~4 个**具体 item_id** | 不带 item_id（公示层）；只覆盖 24 个活动；顶层三份文本**不分服** | 只能做交叉校验，不能当主源 |
| ② 广播解析大奖 | 「哪一行会播报」「属于哪个活动」 | **拿不到奖励**：63/63 条广播都是 `{1:format_item_name}` 模板，奖励名运行时才填 | 否决为主源；可留作 cohort 切分键 |
| ③ **静态配置覆盖层** | 分服 `lottery_id` → 池行 → `[item_id, qty]` + 概率 + 中文名 + 到期时间 | runtime_final 仍未验证 | **唯一能落到「具体奖励 + 分服差异」的路** |

### 1.1 宣传展示页：顶层三份文本 0 差异

`com/cdata/desc_info_data_chs.py`（1,841,484 B）/ `_kj1.py` / `_yk.py` 各解出 **24 个概率公示块**，
逐条 SHA 对比：**有分服差异的公示块 0 / 24**。⇒ 只看顶层三份会误判「奖励不分服」。

分服差异在 overlay：`oversea/desc_info_data_auto_oversea_data_kj1_chs.py`（303,831 B），只覆盖
**1 个**公示块【潜龙宝珠概率公示】，与主表**只差第 5 项**：

| # | 经典服（主 chs） | 简单生存服（kj1 覆盖） | 概率 |
|---|---|---|---|
| 5 | 异变核芯-**裂变效应**\*1 | 异变核芯-**极光狙击**\*1 | 3.47% |

`super_fashion_lottery_conf_data.panel_show_item_ids` 可全量解出展示位 id（base 226/226、kj1 28/28），
但只有台面上 1~4 个大奖，不是完整清单。

### 1.2 广播：63/63 是模板

`broadcast_content` 是 `reward_pool_data` 的**行级字段**（kj1 213/237 行带广播，去重 63 条），
**63/63 全用 `{1:format_item_name}` 占位**，奖励名由运行时填。给不出 item_id / 数量 / 概率。

---

## 2. 推荐主线：静态配置覆盖层

```
L0 活动注册   super_fashion_lottery_conf_data（base 235 行 · lottery_id = 奖池 ID）
                    │  kj1 覆盖表改掉 lottery_id
                    ▼
L1 分服覆盖   oversea/super_fashion_lottery_conf_data_auto_oversea_data_kj1.py（28 行）
              ★ 28/28 共有行全有差异，且都改了 lottery_id
                例：key222 391510→391536、key177 390883→390884、key212 391302→391307
                    ▼
L2 池行       经典服 base = LOTTERY_POOL_RESOLVED_v01.jsonl（23,281 行 · reward_raw=[id,qty]）
              简单生存服 kj1 overlay = oversea/reward_pool_data_auto_oversea_data_kj1.py
                         （18,890 B · 237 行，自带 note / prob_note / expiration_time /
                          broadcast_content / initial_weights / icon …）
                    ▼
L3 叶子       reward jump → 0x27 组 [item_id, qty]
              ★ blob = body[8 + 4*cnt:]；用整个 body 只能解 6/237，用 blob 解 237/237
                    ▼
L4 名字桥     ITEM_MASTER_v03.jsonl（30,251 个 id，无同名冲突）
              ★ 必须用 v03：关键 16 个 id 命中 v01=0 / v02=4 / v03=10
                    ▼
L5 运行时     optional_pool_replace_data（185 行）+ optional_version_data（30 行/18 张分服变体）
              ⇒ 静态奖励 ≠ 最终发奖，runtime_final 一律 unresolved
```

### 2.1 分服差异的三个独立静态载体

| 载体 | 体量 | 差异证据 |
|---|---|---|
| `oversea/...super_fashion_lottery_conf_data..._kj1.py` | 28 行 | 28/28 行改 `lottery_id`、展示 id、福袋、累积奖励 |
| `oversea/reward_pool_data_auto_oversea_data_kj1.py` | 237 行 | 完整分服池行，自带中文 `note` |
| `oversea/desc_info_data_auto_oversea_data_kj1_chs.py` | 1 块 | 公示第 5 项「裂变效应→极光狙击」 |

对照：`oversea/..._yk.py` 162 行、`..._kjxq.py` 237 行（与 kj1 同内容）。

### 2.2 ★★ 复合键口径（v2 硬规则，踩过最大的坑）

```
✓ 唯一正确来源：冻结产物 lookup_key.pool_key.value + lookup_key.item_no.value
               （row_locator.index_key_group_offset → 0x7B 索引尾的索引键组）
✗ 禁用：row.raw.inline_groups 首个二元素组 —— 实测是「下一行的索引键组」
```

**证伪过程（可复算）**：
1. `inline_groups[0]` 给的 kj1 键有 **224/237 行 item_no=0**、值域 391xxx；冻结产物给的键是
   `390011,0 / 390012,0 / …` 这类连续池号。按 `(item,qty)` 对齐两套解析，**129 组键完全不同**。
2. 并列行序可见「键比行晚一格」：`PE 第 i 行 ck = 冻结第 i+1 行 ck`。
3. PE 树行 `key=4` 的 `inline_groups[1]=[660000,1]` 恰好是 `key=165` 行的 reward
   ⇒ `inline_groups` 收集的是「本行起点之后一段字节里的所有 0x27 组」，会串到下一行。
4. 用错键去做双服对照，会得出「223/232 行奖励不同」的**整批假差异**，且呈链式错位
   （kj1 某池的 item 恰好等于 base 相邻池的 item）。

**用正确键的结论**：base `(pool,item_no)` **23,281/23,281 全局唯一**；kj1 键命中率
**232/237 = 97.9%**；冻结产物 kj1 与 PE 树 kj1 的 `(item,qty)` 多重集**完全相同**（同一份 18,890 B
字节的两次解析）。⇒ 按复合键做 overlay 对照成立。

### 2.3 其它两条可复算口径（v1 保留，仍有效）

1. **小表 = 空壳字节码头 + 尾部 `x{` 数据**；`cdata_nxs.load_table` 走 legacy 分支能解，
   不要把「0x73 头」误判成「必须重放字节码」。
2. **jump 目标偏移相对 `blob`，不是整个 `body`**：
   `body = raw[at+6 : at+6+ln]`；`cnt = u32(body[0:4])`；`blob = body[8+4*cnt:]`。

---

## 3. 工具 / 还原树的责任划分（回答「是工具不够好用，还是建树有问题」）

> ⚠ **本节 v2 归因已被 §0-A 推翻，保留作排查史**。正确结论：工具能解、数据也全在
> `配置/Documents/script.py314.lc.npk/_未命名/`，缺的是「无名大表 → 逻辑表名」的**反向映射**，
> 属**索引/账本层**断点，不是解包或保留失败。下表「没落盘」相关行一律以 §0-A 为准。

**v3 主因：索引/账本层缺映射；工具只有两个小坑。**

### 3.1（v2 旧稿，结论已作废）曾经的判断：匿名大 entry 没落盘

| 证据 | 值 |
|---|---|
| kj1 overlay 用同一套 `cdata_nxs` 解 | 18,890 B → **237 行全字段**，工具本身没问题 |
| base `reward_pool_data.py` 815 B 反汇编 | `from com.cdata.reward_pool_data_base import _base` / `_inc` / `_del`；`data = MergedTableData(_base, _inc, _del, "4c2cc793640277ac")` ⇒ **分发壳，0 行** |
| 合并账本 v2 找 `reward_pool_data_{base,inc,del}.py` | **0 命中**；PE 树里也没有 |
| 同结构分发壳 | **12 张**（all_equips_data / common_item_data / npc_data / model_data / battle_mission_data…），全部 <1KB |
| 全树分发壳引用完整性 | **12 张壳 × 3 分片 = 36 张分片文件全缺**（`probe_p0d/e` 校验） |
| NPK 索引 `entries` 查 base 的 fid | `D558884A36C972C5`（解压 1,091,069 B）、`69E58821939CB515`（解压 655,092 B）**都存在** |
| 同一索引查 kj1 的 fid | `7C1978372D53EA7A`（解压 18,890 B）**正确落进了还原树** |
| 项目已有「按 fid 抠分片」先例 | `03_执行/pe_all_equips_基线分片/all_equips_data__fid1F8E.py`（834,179 B），但 reward_pool_data 没做 |
| 合并账本 v2 的 3 个源目录 | `增量快照` / `合并体` / `基线包` —— 现在只剩「配置」，另两个已清掉；`03拆包产物/config_work/…BA8A239A` 也不存在 |

⇒ ~~解包能力没问题：名字带 `_auto_oversea_data_kj1` 的能按名落盘，匿名大 entry 没落盘。
经典服的 1.09MB 数据 + 655KB 中文池只在当年临时工作目录里存在过。~~
**【v3 作废】** 上句按「fid 字符串」搜文件名得 0 命中就下了结论，而实际落盘用**行号名**
`00022771.bin` / `00011262.bin`，一直都在 `配置/Documents/script.py314.lc.npk/_未命名/`（见 §0-A）。
另两处误导：① `pe_config_merge_ledger_v2.json` 只登记 `com/cdata/`，查不到无名层不代表文件不存在；
② 账本列的三个源目录确实只剩「配置」，但**「配置」目录里就含 `Documents/.../_未命名/`**，不是数据被清。

⚠ 另一个限制：当前本地 `E:\mrzh\Documents\script.py314.lc.npk` 为 **238,543,344 B**，
与冻结产物锁定的 BA8 快照（270,106,156 B / sha `ba8a239a…`）**不是同一个包**。
即使现在补解包，拿到的也是「当前版本」而非冻结产物那份，按项目铁律不能直接并进现有产物。

### 3.2 已修的工具缺口（本轮，纯增强）

`00_规范与工具/工具/工具库/00_共享核心/toolkit_core/script_table_replay.py`：

- `STORE_NAME` 增加**非标量 key 兜底**（`names[a]` 被 marshal 解成 `list(Value)` 时不再抛
  `TypeError: unhashable type: 'list'`）。分发壳现在正常返回 `rows=0`。
- 新增 `detect_split_dispatch(names, consts)` → `meta.module_kind` / `shard_modules` / `markers` /
  `shard_note`，**明确报「这是分发壳，行在分片模块里，未落盘属还原树缺口」**，不再误导排查方向。
- 回归：`huodong_conf_data.py` 新版 3,056 行 vs HEAD 旧版 3,056 行，keys 相同，
  归一化对象内存地址后 **0 差异**；改动 39 行、保持 LF 换行。
- 验证脚本：`90_临时/verify_replay_patch{,2}.py`、`verify_replay_diff.py`。

### 3.3 仍待补的工具缺口（未改核心，先记口径）

- `cdata_nxs.load_table` 对 `_chs` 表报 `Bindict73Error: 找不到 0x73 表体载荷`。
  真身是 **`LOAD_CONST` + `STORE_NAME string_pool` 的字节码常量**（`kj1_chs` 池 562 条、
  含中文 300 条，「异变核芯-极光狙击」命中 1 条、「裂变效应」0 条）。
  正确入口已有：`lottery_chain.MP.pool_of_file`（`parse_pool_bytes`），只是没接成统一入口。
- 构建期缺「分发壳引用完整性校验」；本轮 `verify_replay_patch.py` 第 4 节给了可复用的校验实现。

---

## 4. 可交付度对照（v2）

| 项 | 经典服 base | 简单生存服 kj1 |
|---|---|---|
| 池行 | 冻结产物 **23,281 行**，`(pool,item_no,item_id,qty)` | overlay **237 行**（232 命中 base 同键 / 5 新增） |
| 中文奖励名 | 冻结产物无；名字桥 `ITEM_MASTER_v03` 可补 **19,197 行 = 82.5%**（4,383 个不同 id 命中 3,529） | 行内 `note` **237/237**；按 item 唯一挂回冻结键 **212/237**（25 条多义） |
| 概率 | 冻结产物 `probability_semantics.state=unresolved` | 行内 `prob_note` 156/237；按 item 挂回 137/237 |
| 到期时间 | 无 | 行内 **237/237**；挂回 212/237 |
| 广播 | 无 | 行内 213/237；挂回 190/237 |
| 权重 / 保底 / 图标 | 无 | `initial_weights` 237、`ensure_count` 133、`icon` 223、`total_limit_count` 223 |
| 展示位 item_id | 226/226 可解 | 28/28 可解 |
| 公示文本 | 24 块（主 chs） | 1 块 overlay 差异 |

⚠ **`note` ≠ 正式道具名**：kj1 行 `note` 与 `reward[0]` 经名字桥查出的正式名
**只有 66/237 逐字一致**，35 条写法不同（「机械材料等级3」vs「机械材料-等级3」、
「星雨狐愿」vs「星语狐愿」等错字），136 个 item_id 根本不在 v03 里。
⇒ 展示必须 **item_id + `note` + 桥名三者并列**，不能只信其中一个。

---

## 5. ★ 完整双服奖励差异清单（v2 核心成果，可复算）

按**正确复合键**（冻结产物 `lookup_key`）对照：kj1 237 行 → `232 命中`，
其中 **224 行奖励相同**（overlay 只补运行参数）、**8 行被替换**、**5 行新增**。

### 5.1 被替换的 8 行（逐行，经典服 → 简单生存服）

| pool | item_no | 经典服 base | 简单生存服 kj1 | note | prob |
|---:|---:|---|---|---|---|
| 390985 | 0 | `103101` ×1（未解析） | `103018` ×1（未解析） | 配方:医疗无人机 | — |
| 390985 | 4 | `134527` ×1 雷托霰弹枪配方套装 | `151994` ×20 能量电池 | 能量电池 | — |
| 391475 | 0 | `103101` ×1（未解析） | `103018` ×1（未解析） | 配方:医疗无人机 | — |
| 391475 | 3 | `139008` ×1 菌焰喷火器套装 | `241890` ×1 极品异变核芯自选箱（不可交易） | 霰弹枪异变核芯自选箱 | — |
| 391475 | 4 | `241646` ×1 喷火器极品异变核芯自选箱 | `151994` ×20 能量电池 | 能量电池 | — |
| 391508 | 2 | `132099` ×4 保密级配方资料(不可交易) | `151783` ×200（未解析） | 重构分子 | — |
| 391508 | 4 | `150059` ×400 配方残页 | `151783` ×400（未解析） | 重构分子 | — |
| **391513** | **2** | **`660055` ×1 异变核芯-裂变效应** | **`660023` ×1 异变核芯-极光狙击** | **异变核芯-极光狙击** | **0.03472** |

### 5.2 新增的 5 行（base 无此键，全在 pool 391711）

| pool | item_no | item_id | 桥名 / note | prob | expiration_time |
|---:|---:|---:|---|---:|---:|
| 391711 | 0 | 660081 | 异变核芯-淬焰燃锋 | 0.00999 | 4854556799 |
| 391711 | 1 | 660000 | 异变核芯-疾影火刃 | 0.00999 | 4854556799 |
| 391711 | 2 | 660001 | 异变核芯-绝对零度 | 0.00999 | 4854556799 |
| 391711 | 3 | 660002 | 异变核芯-脉冲闪电 | 0.00999 | 4854556799 |
| 391711 | 4 | 660030 | 异变核芯-侵蚀效应 | 0.00999 | 4854556799 |

### 5.3 六源闭环：公示第 5 项精确落在 `(391513, 2)`

| # | 证据 | 值 |
|---|---|---|
| 1 | 主 chs 公示【潜龙宝珠概率公示】第 5 项 | 异变核芯-**裂变效应**\*1 · 3.47% |
| 2 | kj1 overlay 公示同位置 | 异变核芯-**极光狙击**\*1 · 3.47% |
| 3 | 冻结产物 **base** `(391513,2)` | `660055` → 桥名 异变核芯-**裂变效应** |
| 4 | 冻结产物 **kj1** `(391513,2)` | `660023` |
| 5 | PE 树 kj1 行（按 item 挂回） | `note=异变核芯-极光狙击`, `prob_note=0.03472` |
| 6 | `ITEM_MASTER_v03` | `660023 → 异变核芯-极光狙击`、`660055 → 异变核芯-裂变效应` |

kj1 全表检索：「裂变效应」**0 行**、「极光狙击」**1 行**；`kj1_chs` 字符串池同样
「极光狙击」命中 1 条、「裂变效应」0 条。**不是推测，是六处独立证据逐字一致**。

⚠ 仍保留 v1 警告：**公示 8 项 ≠ 单个池**。这 8 行替换里只有第 8 行对应公示第 5 项，
其余 7 行不在该公示块里；不要把公示 8 项硬塞进一个 `pool_id`。

---

## 6. 剩余断点与下一步（按性价比）

| # | 断点 | 现状 | 建议 |
|---|---|---|---|
| P0 | base 全量行 + 中文池 | ✅ **v3 已找到，不需要补录**：`配置/Documents/script.py314.lc.npk/_未命名/00022771.bin`（23,902 行）+ `00011262.bin`（12,511 串池）。冻结产物 BA8 快照（23,281 行 / 1,091,069 B）与当前树是**不同版本**，按铁律不混排 | 待用户定口径：是否把这份「当前版本静态配置」作为**独立 source_locks** 纳入板；以及 §0-A.2 的 L1 注册表是否建 |
| P1 | base 中文名 | 名字桥覆盖 82.5%（19,197/23,281），未命中 854 个不同 id | 补 `ITEM_MASTER` 或补 `_chs` 池解析；不改现有数字 |
| P2 | 活动→池绑定 | 冻结产物 `activity_binding.lottery_id=null`；super_fashion 的 188 个 id 中 184 个落池 | 把 super_fashion 行作为绑定证据写 `meta.notes`（可复算规则），不伪造 locator_chain |
| P3 | kj1 键多义 / 未解析名 | 25/237 条 note 按 item 挂回多义；8 行替换里 3 个 id 未进名字桥 | 出**说明性空卡**，不猜数 |
| P4 | runtime_final | `optional_pool_replace_data` 185 行 + `optional_version_data` 30 行/18 张分服变体 + `OptionalVersionMgrController.on_replace_child_reward` | 静态层一律标 `runtime_final=unresolved`；要声称「当前服实际发什么」必须补运行时观测或下发表 |
| P5 | 工具统一入口 | `_chs` string_pool 已有 `MP.pool_of_file`，但 `cdata_nxs.load_table` 不认 | 接一层转发；并把分发壳引用校验加进构建期门禁 |

---

## 7. 发布纪律

- 分服子卡分开不混排；缺数据出**说明性空卡**，不猜数。
- `kj1` = 简单生存服，无后缀 `base` = 通用/经典服（`toolkit_core/server_types.py`）。
- `yh`（硬核）无池表族属预期；`xq/xyd/cn` 语义未定，不推断。
- 静态奖励 ≠ 运行时最终奖励；`publication_tier` 不写 verified-runtime-final。
- 复合键**只用冻结产物 `lookup_key`**；`inline_groups[0]` 禁用（§2.2）。
- 找不到证据就跳过并写报告，不伪造 `locator_chain` / 占位值。

---

## 附：探针与产物

| 用途 | 路径 |
|---|---|
| v1 六轮只读探针 | `90_临时/probe_lottery_rewards{,2,3,4,5,6}.py` |
| v2 P0 诊断 / 源取证 | `90_临时/probe_p0_base_replay.py`、`probe_p0b_base_sources.py`、`probe_p0c_chs_and_frozen.py`、`probe_p0d_tree_ledger.py`、`probe_p0e_split_shards.py` |
| v2 工具回归 | `90_临时/verify_replay_patch.py`、`verify_replay_patch2.py`、`verify_replay_diff.py` |
| v2 P1 双服对照（**最终口径 = `probe_p1g`**） | `90_临时/probe_p1_dual_server.py`、`probe_p1b_key_alignment.py`、`probe_p1c_fields.py`、`probe_p1d_overlay_consistency.py`、`probe_p1e_key_crosscheck.py`、`probe_p1f_bindict_keys.py`、**`probe_p1g_correct_comparison.py`** |
| 旧方法论 | `02_wiki/web/docs/LOTTERY_CHAIN_LOCATOR.md` |
| 池结构冻结产物 | `02_wiki/web/site_data/LOTTERY_POOL_RESOLVED_v01.jsonl` |
| 名字桥（**用 v03**） | `02_wiki/web/site_data/ITEM_MASTER_v03.jsonl` |
| 统一表读取 / string_pool | `toolkit_core/cdata_nxs.py` · `bindict_table.resolve_jump_group` · `lottery_chain.MP.pool_of_file` |
