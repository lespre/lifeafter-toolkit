# 09 Wiki 构建：数据源候选链

> 状态：2026-09-07 已盘点并登记。
> 原始 NPK 一律只读；实际路径、SHA-256、大小、mtime_ns 以
> `08Lifeafter wiki/data/live_sources.json`（schema v3）
> 和 `tools/audit_live_sources.py` 的复核结果为准。


## 1. 数据源总原则

### 1.1 客户端与服务器是两个独立维度

游戏环境必须拆成两个完全独立的维度：

【客户端维度】
- 正式服客户端
- 测试服客户端

【服务器维度】
- 经典服
- 简单生存服

两者不存在固定的一一对应关系。

实际结构为：

正式服客户端
├─ 经典服
└─ 简单生存服

测试服客户端
├─ 经典服
└─ 简单生存服

因此理论上存在四种组合：

1. 正式服客户端 / 经典服
2. 正式服客户端 / 简单生存服
3. 测试服客户端 / 经典服
4. 测试服客户端 / 简单生存服

严禁使用以下错误推导：

- 测试服客户端 = 简单生存服
- 正式服客户端 = 经典服
- `E:\mrzh` = 简单生存服
- `E:\LifeAfter` = 经典服

客户端来源只能证明客户端来源，不能自动证明服务器分支。


### 1.2 当前本地客户端来源

当前已确认：

- `E:\mrzh`
  - client_channel = test
  - 即：测试服客户端来源

- `E:\LifeAfter`
  - client_channel = formal
  - 即：正式服客户端来源

除非存在额外静态证据、selector、loader、consumer、运行时参数或实机锚点，
否则不得仅根据目录、NPK 或客户端来源判断其服务器分支。


### 1.3 server_branch 判定原则

服务器分支字段：

- `classic`
  - 经典服

- `simple_survival`
  - 简单生存服

- `shared`
  - 已有证据证明两个服务器分支共同使用

- `unresolved`
  - 当前无法证明具体服务器归属

当前仅通过客户端目录发现的 NPK：

`server_branch = unresolved`

除非后续存在足够证据，否则禁止自行将其改成 `classic` 或
`simple_survival`。


### 1.4 数据源身份模型

数据源身份不得再使用：

`客户端 / 服务器`

这种未经证明就绑定两个维度的写法。

至少应拆分为：

- client_channel
- server_branch
- source_id
- snapshot / source_lock
- path
- SHA-256
- size
- mtime_ns

其中：

`client_channel`

用于表示：

- test
- formal

`server_branch`

用于表示：

- classic
- simple_survival
- shared
- unresolved


### 1.5 同源闭合

base、CHS、字段语义、行级 locator chain 必须在同一个
source lock / 同一快照内完成。

跨客户端数据只能进行明确的存在性或差异比较，例如：

- both
- test-only
- formal-only
- conflict

禁止将两个客户端来源拼接成一条业务事实。

服务器分支同理。

在 server_branch 尚未解决时，不得自行将某条数据归入经典服或简单生存服。


### 1.6 静态存在不等于运行时启用

包内表、同 FID 或相同 payload 只能证明静态存在性或一致性。

以下业务状态：

- 当前活动
- 当前货架
- 当前奖池
- 当前发奖
- 服务器分支启用状态
- 经典服 / 简单生存服差异

仍需 selector、consumer、loader、运行时参数或实机锚点证明。



## 2. 第一层：当前目标文件

当前目标文件只按“客户端来源”分类。

| 优先级 | 客户端来源 | server_branch | source_id | 当前目标文件 | 用途 |
|---|---|---|---|---|---|
| 1 | 测试服 | unresolved | documents-py314-current | E:\mrzh\Documents\script.py314.lc.npk | 测试服客户端主侦查源、表族扫描、行级定位链默认源 |
| 2 | 正式服 | unresolved | lifeafter-classic-current | E:\LifeAfter\Documents\script.py314.lc.npk | 正式服客户端补充、双客户端存在性与差异校验 |

注意：

`lifeafter-classic-current`

是现有 source_id。

如果该名称原本建立在“正式服客户端 = 经典服”的错误假设上，
后续应单独迁移为不带服务器归属暗示的 source_id。

在完成 registry、脚本和引用关系检查前，不直接在本文中擅自修改 source_id，
避免破坏现有引用。

当前本地 reader 默认只开放这两个目标快照。

它们是默认工作源，不代表其他锁定包不存在。

同时：

- 测试服客户端内容不能自动视为简单生存服内容。
- 测试服客户端内容不能自动视为经典服内容。
- 正式服客户端内容不能自动视为经典服内容。
- 正式服客户端内容不能自动视为简单生存服内容。

服务器归属必须另行证明。



## 3. 第二层：同 Documents 目录的辅助候选

下列文件属于两个客户端的 Documents 脚本组。

它们是较早快照或可能的热更辅助候选。

仅凭文件名、目录和 mtime：

- 不得认定为某张表的 base / inc / del；
- 不得直接认定 loader 会合并它们；
- 不得认定属于经典服；
- 不得认定属于简单生存服。

| 客户端来源 | server_branch | source_id | 候选文件 | 快照角色 |
|---|---|---|---|---|
| 测试服 | unresolved | mrzh-documents-py3-legacy | E:\mrzh\Documents\script.py3.npk | Documents 历史 / 回退候选 |
| 测试服 | unresolved | mrzh-documents-script-legacy | E:\mrzh\Documents\script.npk | Documents 历史 / 回退候选 |
| 正式服 | unresolved | lifeafter-documents-py3-legacy | E:\LifeAfter\Documents\script.py3.npk | Documents 历史 / 回退候选 |
| 正式服 | unresolved | lifeafter-documents-script-legacy | E:\LifeAfter\Documents\script.npk | Documents 历史 / 回退候选 |

文件层盘点显示：

两个客户端的 Documents 目录都存在：

- `script.npk`
- `script.py3.npk`
- `script.py314.lc.npk`

三份脚本包。

但这只能证明文件组完整性。

不能据此证明：

1. 表级三件套语义；
2. loader 合并关系；
3. 经典服归属；
4. 简单生存服归属。



## 4. 第三层：根目录全量基线与历史回退候选

根目录 `script.py314.lc.npk` 是优先级最高的全量基线候选。

用途包括：

- 当前 Documents 目标包物理缺表时的独立比对；
- 格式复证；
- 历史考古。

它们不是当前 Documents 包的字段补丁。

禁止跨快照回填。

同时，根目录位置不能证明服务器分支。

| 客户端来源 | server_branch | source_id | 候选文件 | 快照角色 |
|---|---|---|---|---|
| 测试服 | unresolved | mrzh-root-py314-full | E:\mrzh\script.py314.lc.npk | 根目录 py314 全量基线 |
| 测试服 | unresolved | mrzh-root-script-legacy | E:\mrzh\script.npk | 根目录 legacy 历史候选 |
| 正式服 | unresolved | lifeafter-root-py314-full | E:\LifeAfter\script.py314.lc.npk | 根目录 py314 全量基线 |
| 正式服 | unresolved | lifeafter-root-py3-legacy | E:\LifeAfter\script.py3.npk | 根目录 py3 历史候选 |
| 正式服 | unresolved | lifeafter-root-script-legacy | E:\LifeAfter\script.npk | 根目录 legacy 历史候选 |

测试服根目录不存在：

`E:\mrzh\script.py3.npk`

不得在 registry、文档或脚本中补造此路径。



## 5. 当前脚本 / 表数据候选总清单

【测试服客户端】

server_branch：当前默认 unresolved

1. E:\mrzh\Documents\script.py314.lc.npk      当前目标
2. E:\mrzh\Documents\script.py3.npk           Documents 辅助候选
3. E:\mrzh\Documents\script.npk               Documents 辅助候选
4. E:\mrzh\script.py314.lc.npk                 根目录全量基线
5. E:\mrzh\script.npk                          根目录历史候选


【正式服客户端】

server_branch：当前默认 unresolved

6.  E:\LifeAfter\Documents\script.py314.lc.npk 当前目标
7.  E:\LifeAfter\Documents\script.py3.npk      Documents 辅助候选
8.  E:\LifeAfter\Documents\script.npk          Documents 辅助候选
9.  E:\LifeAfter\script.py314.lc.npk           根目录全量基线
10. E:\LifeAfter\script.py3.npk                根目录历史候选
11. E:\LifeAfter\script.npk                    根目录历史候选


这 11 个包是当前已准入的脚本 / 表数据候选源。

这里的“测试服 / 正式服”只描述：

`client_channel`

不描述：

`server_branch`

执行前必须运行：

cd "E:/la拆包项目/08Lifeafter wiki"
python tools/audit_live_sources.py --include-disabled

任何锁定文件的：

- path
- SHA-256
- 大小
- mtime_ns

不匹配时：

旧 offset、FID 映射、行定位、名称和业务结论都必须降级，
不可继续沿用。



## 6. 未准入的资源 NPK 范围

对：

- `E:\mrzh`
- `E:\LifeAfter`

进行只读文件层盘点，共发现 166 个 `.npk`：

- 测试服客户端：158 个
- 正式服客户端：8 个

除上述 11 个脚本包外，另有 155 个资源包候选，例如：

- `res.npk`
- `res\ui.npk`
- 角色分包
- 模型分包
- UI 分包

这些资源包目前只属于待侦查资源范围。

不能因为扩展名而自动加入 `live_sources.json`。

必须先静态证明：

- 内部含目标表；
- 存在同快照 loader / consumer；
- 或存在可审计的 table-family 证据；

才可升级为表数据候选源。

不得将：

- 资源路径
- 贴图
- 模型
- UI 文本邻近关系

直接当作：

- item
- 活动
- 奖池

的业务绑定证据。

同样，不得根据资源包所在客户端目录自动推断其服务器分支。



## 7. BA8 `common_item` 热更表族边界

当前 BA8 测试服客户端 Documents 快照已在同一包内定位到以下静态组件：

| 输入角色 | 表 / 组件 | FID | entry | 证据状态 |
|---|---|---|---|---|
| base | common_item_data_base.py | B42760CCA41DBC25 | 18005 | 已定位 |
| base_chs | common_item_data_base_chs.py | EF3A8474A5E5F7A4 | 23928 | 已定位，必须与 base 同包配对 |
| inc | common_item_data_inc.py | 363827281579481B | 5292 | 已定位 |
| inc_chs | common_item_data_inc_chs.py | 1A81E67098A6E8D9 | 2592 | 已定位，必须与 inc 同包配对 |
| del | common_item_data_del.py | A44D99E0490CA9BF | 16447 | 已定位；147B 小模块，静态 payload 形状尚未解释 |
| 合并壳 | common_item_data.py | 1232F498D07A0EBB | 1765 | 静态字符串同时列出 MergedTableData、base/inc/del |

保留的通用热更模型是：

`base ∪ inc − del`

当前正式状态：

`components-located-loader-replay-pending`

原先 `common_item_data_del` 的“0 命中”是扫描器缺陷：

扫描器跳过了小于 250B 的模块，而 `del` 恰为 147B。

现已移除该尺寸过滤，并新增真实 BA8 小模块回归测试。

以下命令可复现该定位：

`scan_table_family.py common_item_data_del --json`

三件套路径和 `MergedTableData` 合并壳属于：

同快照静态证据。

2026-09-07 追加（详见 `08Lifeafter wiki/tools/audit_common_item_family.py` + `data/audit/common_item_family_composition_audit.json`）：

- `inc` 解码：35/37 索引行可解（0x86 附属 detail 行支持落地，10 行从 unbound 转正；`bindict_provenance.py` 仅接受能精确闭合到行边界的 0x86，解析失败回退 unsupported 语义=零回归）
- 1224504（detail 溢出边界 1B）与 1345059（0x0c 扩展区）保持 unresolved，不猜
- 集合事实：base 36038 key / inc 35 key / 重叠 27 / 仅 base 36011 / 仅 inc 8
- **key 语义警示**：重叠 27 中 23 组 name 不同（key 1224479：base=1型倒三角墙 vs inc=3型倒三角墙）→ 重叠不等于同一物品被修改，inc 行 key 可能是槽位而非 item_id
- `del` 删除键=自定义 marshal set 常量，静态不可解 → `payload-shape-unresolved`，不应用任何删除

但不能单独证明：

- 运行时读取顺序
- 同 key 覆盖
- 删除 key 语义
- 灰度条件
- 正式服客户端启用状态
- 测试服客户端启用状态
- 经典服启用状态
- 简单生存服启用状态

在 loader / consumer 回放前：

- 不得把 inc 自动覆盖 base；
- 不得生成最终 effective table；
- 不得断言行级删除；
- 不得断言覆盖优先级；
- 不得断言最终 origin；
- 不得断言正式服客户端适用性；
- 不得断言经典服适用性；
- 不得断言简单生存服适用性。

后续若合成，必须限定在：

- 同一锁定 NPK
- 同一客户端来源
- 同一快照
- 同一表族

如果服务器分支已经得到证明，还必须记录：

- server_branch

如果服务器分支尚未得到证明：

`server_branch = unresolved`

不得为了完成数据结构而猜测服务器归属。

每行来源状态只能显式写为：

- base
- increment
- base-overridden-by-increment
- deleted-by-hotfix
- unresolved-composition



## 8. 使用顺序

当前目标 Documents py314
  ↓
同客户端 Documents 辅助快照
  ↓
同客户端根目录 py314 全量基线
  ↓
同客户端历史 / legacy 回退包
  ↓
经静态证据准入后的资源 NPK


每一步都是独立 source lock 的：

- 比较
- 缺表侦查
- 格式复证

不是字段拼接链。

禁止：

- 跨客户端拼接业务数据
- 跨快照拼接业务数据
- 跨已确认服务器分支拼接业务数据

对于：

`server_branch = unresolved`

的数据，不得为了 Wiki 展示方便而擅自归入经典服或简单生存服。



## 9. 服务器分支识别规则

后续 Wiki 构建必须增加“服务器分支识别”步骤。

目标是区分：

- classic
- simple_survival
- shared
- unresolved

可接受的服务器分支证据包括但不限于：

1. 明确的服务器类型 selector；
2. 配置字段；
3. loader 分支；
4. consumer 分支；
5. 运行时参数；
6. 网络 / 登录后下发配置；
7. 实机切换经典服与简单生存服后的可复现实验；
8. 同一客户端、同一快照下可重复验证的差异；
9. 其他可以形成审计链的静态或运行时证据。

不能作为单独服务器归属证据的包括：

- 客户端目录名称；
- NPK 文件名；
- 文件所在 `E:\mrzh` 或 `E:\LifeAfter`；
- 单纯文本邻近；
- UI 资源邻近；
- 根据玩法内容进行主观猜测。


## 10. 四种客户端 / 服务器组合的当前证据状态

### 测试服客户端 / 经典服

client_channel = test
server_branch = classic

客户端存在：已知
服务器组合存在：已由游戏实际结构确认
当前 NPK 是否专属于该服务器：未证明


### 测试服客户端 / 简单生存服

client_channel = test
server_branch = simple_survival

客户端存在：已知
服务器组合存在：已由游戏实际结构确认
当前 NPK 是否专属于该服务器：未证明


### 正式服客户端 / 经典服

client_channel = formal
server_branch = classic

客户端存在：已知
服务器组合存在：已由游戏实际结构确认
当前 NPK 是否专属于该服务器：未证明


### 正式服客户端 / 简单生存服

client_channel = formal
server_branch = simple_survival

客户端存在：已知
服务器组合存在：已由游戏实际结构确认
当前 NPK 是否专属于该服务器：未证明


因此当前 11 个候选 NPK 的正确默认状态不是：

“测试服 / 简单生存服”

或：

“正式服 / 经典服”

而应该是：

测试服客户端来源：
client_channel = test
server_branch = unresolved

正式服客户端来源：
client_channel = formal
server_branch = unresolved


## 11. Wiki 后续数据归属原则

Wiki 中每条需要区分环境的业务事实，应尽可能记录：

client_channel
server_branch
source_id
snapshot
table
row/key
locator
evidence_status

其中客户端和服务器必须分别判定。

例如：

client_channel = test
server_branch = unresolved

表示：

已证明来自测试服客户端，
但尚未证明属于经典服、简单生存服或两者共用。

不得将其展示成：

“测试服简单生存服数据”。


只有服务器分支证据充分时，才能写：

client_channel = test
server_branch = classic

或者：

client_channel = test
server_branch = simple_survival


如果证明两个服务器共同使用，则写：

server_branch = shared


最终原则：

客户端来源 ≠ 服务器分支。

正式服 / 测试服描述客户端。

经典服 / 简单生存服描述服务器。

两个维度必须独立取证、独立记录、独立比较。

任何无法证明的服务器归属统一标记：

server_branch = unresolved

禁止猜测，禁止为了补全 Wiki 数据而强行归服。