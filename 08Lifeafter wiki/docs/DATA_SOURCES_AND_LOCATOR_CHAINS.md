# 《明日之后》拆包数据源与定位链总纲

> 版本：2026-09-07（27.107–27.114 轮沉淀）· 承接：docs/DUAL_SOURCE_CALIBRATION.md（双源校准实证）、docs/PIPELINE.md（发布流水线）、docs/SCHEMA.md（板数据规范）
> 配套日志：`E:\la拆包项目\06（agent写）拆包器进展与交接日志.md`

## 目录
1. 数据源全景
2. 定位链总则（用户定版口径）
3. 通用命名补缺层级
4. 业务域定位链分述
5. 硬锚 id 表
6. 阴性表族登记（穷尽证据）
7. 工具缺口与出路
8. 证据等级与发布契约速查

---

## 一、数据源全景

### 1.1 当前双源（默认侦查/对照入口）

| 源 | 路径 | 角色 |
|---|---|---|
| 体验服（简单生存服 BA8） | `E:\mrzh\Documents\script.py314.lc.npk` | 拆包主源（本会话全部 entry 来自此包） |
| 经典服 | `E:\LifeAfter\Documents\script.py314.lc.npk` | 双服校准对照源 |

- 包锁（live_sources.json）：体验服 SHA-256 = `328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f`，270,106,156 B。
- 铁律：**原始只读**。探针产物只进 `%LOCALAPPDATA%\Temp` 且用完即删；`03拆包产物` 只做读侧副本。
- 双服同 FID 同 SHA 实证：002962（宸世商店）= f2573710…（双服完全同一份文件）；common_item= 双版本同一文件。**凡同 SHA=合并无效，不再重复此路**（已固化，见 4.1/6）。

### 1.2 备选全量包与热更表族（schema v3）

`data/live_sources.json` 不再把两个 Documents 包误写成“全部数据源”。现在的 11 个候选脚本包均已锁定**路径、SHA-256、bytes、mtime_ns、客户端角色、服务器分支、快照角色**，并且一律 `read_only`。

| 包角色 | 简单生存服·测试服 | 经典服·正式服 | 可用于什么 |
|---|---|---|---|
| 根目录 py314 全量基线 | `mrzh-root-py314-full` | `lifeafter-root-py314-full` | 当前 Documents 包物理缺表时的**独立回退快照**；不可静默补当前字段。 |
| Documents 历史快照 | `mrzh-documents-py3-legacy`、`mrzh-documents-script-legacy` | `lifeafter-documents-py3-legacy`、`lifeafter-documents-script-legacy` | 表族发现、格式回归、版本考古；不可写为当前事实。 |
| 根目录历史快照 | `mrzh-root-script-legacy` | `lifeafter-root-py3-legacy`、`lifeafter-root-script-legacy` | 仅历史反证/结构线索；不得向当前图鉴回填名称或属性。 |

默认的 localhost 读取器仍只打开两份“当前 Documents”包，避免枚举备选包时无意义 hash、索引多 GB 原始数据；备选包已可审计，后续需要时只能显式开启只读复核。测试服优先只是侦查次序，**不是**正式服事实的替代。

#### BA8 `common_item` 热更分片：组件已定位，合成语义待复证

BA8 测试服当前 Documents 包已通过命名表族扫描定位到 `common_item_data_base.py`（FID `B42760CCA41DBC25`）、`common_item_data_inc.py`（FID `363827281579481B`）与 **147B 的** `common_item_data_del.py`（FID `A44D99E0490CA9BF`，entry `16447`），并分别锁定了同包 `base_chs` / `inc_chs`。`del` 曾被扫描器的“文件小于 250B 即跳过”规则漏掉；现在扫描器按恢复的逻辑路径筛选，小模块也会进入候选结果。entry `1765`（FID `1232F498D07A0EBB`）的静态字符串同时出现 `MergedTableData`、base/inc/del 三个逻辑名，因而已形成**同快照表族与合并壳的静态证据**。这仍不等于已动态验证读取顺序、同 key 覆盖粒度、删除键语义、条件分支或正式服实际启用。

因此 registry 保留通用模型 `base ∪ inc − del`，但状态是 **`components-located-loader-replay-pending`**：组件物理存在已证实，loader 读取顺序、同 key 覆盖、删除语义与合成后行集仍未复放，不能把任何合成结果写成已证实业务事实。

**静态集合审计已落地（2026-09-07，`tools/audit_common_item_family.py`）**：base（18005+23928）36038 key、inc（5292+2592）35 key、重叠 27、仅 base 36011、仅 inc 8。重叠 27 中 23 组 name 不同（如 key 1224479：base=1型倒三角墙 vs inc=3型倒三角墙）→ **重叠 key 不等于同一物品被修改**，inc 行 key 可能是槽位而非 item_id；4 组 name 相同（如 156182 重构转印器）=真重叠候选。`del`（16447）删除键为自定义 marshal set 常量，`payload-shape-unresolved`，不应用任何删除。`inc` 自身解码 35/37（0x86 附属 detail 行支持；1224504 溢出边界 1B、1345059 的 0x0c 扩展区保持 unresolved）。这些是纯集合事实，不构成 loader 顺序/行身份/覆盖语义结论。

后续如果完成复证，合成只能发生在**同一锁定 NPK、同一客户端/服务器分支、同一表族**：`inc` 的同 key 覆盖先验证 loader 语义，`del` 只能删除本包确认的 key；根目录全量包、另一客户端或另一服的行禁止加入合成。输出逐行保留 `base` / `increment` / `base-overridden-by-increment` / `deleted-by-hotfix` / `unresolved-composition` 来源状态。

### 1.3 NPK 结构与 entry 形态

- 包内为文档表集合；每个文档表= `x{` + u32 长度 + body + 尾部文本池（CHS 池）等。CHS 池=中文名册（名字层主源）。
- entry 提取产物：`E:\la拆包项目\03拆包产物\config_work\script_py314_docs_BA8A239A\entries\<NNNNNN>.bin`
- 表格式族：
  - 新格式行（D6/C6/96 + schema_ref + bitmap + 值流）= bindict_table 标准解码（decode_table_rows）
  - 老格式特形（0x96 老容器、0x76 行、D6 紧凑数值行、部分表 parse_index 不认）= 专项攻坚或工具缺口登记（见七）
  - 解码器：`01拆包器本体\工具库\10_应用核心\toolkit_core\bindict_table.py`（17 章 walkthrough 定：解码器核心无 bug，**禁改核心**；工具缺口走独立解析器/扩展登记）

### 1.4 双版本核验资产（780363 域）

`03拆包产物\config_work\script_py314_docs_780363b86008\`：经典服核验 JSON + manifest（2949 entry）——用户实机核验兑换表（2026-09-01）的源侧留档，含 entry 2949（static）、file_id 反查链。

### 1.5 应用层工具（wiki/tools/）

- `live_npk_reader.py`：双 npk 直查（FID 反查/entry 提取/双服对照）
- `audit_live_sources.py`：只读核验注册表中当前、全量基线与历史备选包的 path/SHA-256/bytes/mtime_ns；默认仅当前包，`--include-disabled` 才全量核验。
- `decode_probe.py`：单表解码探针（--chs 挂池、--rows 预览、--dump 全量）
- `bindict_provenance.py`：带行级 provenance（source_entries/field 坐标/CHS 槽回放）的解码
- `build_wiki.py`：发布门禁构建（manifest/policy 校验）
- `publication_policy.py`、各 export_*.py、rebuild_chenshi_slots.py（宸世板生成器）
- 后台扫描器：`scan_table_family.py`（表族扫描=按前缀族批量探测目标表）

### 1.6 Wiki 资产（E:\la拆包项目\08Lifeafter wiki）

- `data/boards/`：发布板 JSON（21 板，43952 条，2026-09-07）
- `data/external_refs/`：锚点层留档（实机快照、静态池、车库名册、公告源等——见各域分述）
- `data/publication_policy.json`：板发布状态（published/quarantined/unpublished/retired）
- `data/manifest.js` + `wiki.html`（主页 grid 按 category 注入）+ `board.html`（卡渲染）
- `tests/test_publication_gate.py`：发布契约测试（计数期望随板行数同步）

---

## 二、定位链总则（用户定版口径，逐条为铁律）

1. **内容=拆包主体，实机截图=锚点层**。截图文本不上板；截图只用于核验/锚定（▲ 标 + user-verified 级 provenance）。「不要来自我的实机截图，我要你拆包，然后根据定位链，我的只是给你锚点而已」。
2. **禁拼接/禁相邻 id 瞎关联**。名称/id↔名桥不得按顺序、邻近、共现推断。教训实证：633090140 曾被错标「刑天召唤器」，真锚是 633070140（铠甲再临）——锚必须逐字用用户给的。
3. **板结构=容器卡**。卡=期次/常驻=唯一卡单位；商品并入容器卡的族分组文本（〔族〕品名(id)…）；逐品成卡=用户两次否决。锚点品 ▲ 标。
4. **双服双版本校准=交付铁律**。交付前经典 vs 体验（BA8）双源 FID 对照+行数对比+差异全列出。同 FID 同 SHA=同一份文件=合并无效证据。
5. **期次↔时间窗三态制**：conf key n ↔ ykxq 行序=全错；只允许官方公告锚/用户实机锚/诚实「待校准」。
6. **常驻/限时=纯服务端逻辑**（静态无 ts/限购字段时）——唯一权威=实机 UI 倒计时（无倒计时+月/周限=重置型常驻；限 1/1 无倒计时=一次性位待确认）。
7. **未上线判定先排重**：先对照 `E:\la拆包项目\明日之后完整历史更新汇总_2018-2026.md` 排除已上线；行为资源新增≠未上线。
8. **只读解包边界**：原始 NPK 只读；8765 服务不得重启；中文路径部分场景禁 rg/search_files。
9. **发布契约 7 项**（见八）：source_entries 非空、decoded_sha256 非空、顶层 source、evidence ∈ 枚举、user-verified 带 user_evidence、卡带 source_lock_sha256、测试计数同步。

---

## 三、通用命名补缺层级

用户指定顺序（已穷尽审计=不可再向上游重试）：

```
common_item 名册（道具名册，名↔id 主表）
  → 道具总表（common_item_text_sources 板=当前包全道具 id 键文字表）
  → 双版本数据源合并补缺（经典服 ∪ 体验服）
  → 诚实占位（ID + 「名册缺」/「待命名」），绝不硬造
```

- 名册表族通道：common_item（双服同文件=无效）、gift_data（1 命中=135048 福鼠迎春典藏）、vehicle_catalog（item_ids 不覆盖）、collect 族 319 表（卡牌/执照类=不对路）、res_handbook（1344xxx 资源域≠194xxx 载具域=阴性）、root 老包（规则禁）。
- 名字不可得时出路（按序）：更新包登记 → 用户图鉴/实机截图 → 服务端下发数据。静态穷尽阴性=证据闭环（落盘 name_gap_audit），不是失败而是边界。

---

## 四、业务域定位链分述

### 4.1 宸世商店（臻藏/稀世）——002962

**数据源**：
- 静态池：002962.bin（81,534B，双服同 FID 同 SHA f2573710…，file_id 1E888FAB015CA82D）
- 三通道同内容实证：main 002962 / ykxq 005580 / ykxq 007946（76,144B 大表）解出逐条相同（30 商品同 id 序）=**当期单快照冗余**；历史 27 期商店内容=客户端物理不存在（已固化）
- 锚点层：`external_refs/chenshi_shops_snapshot_20260906.json`（84 行=9-06 22:06~22:13 实机 14 截图全景：两店全分类/品/价/限购/倒计时；玩家 430002/14221351）
- 期次源：`external_refs/announce_chenshi.json`（官方公告=期次↔时间窗锚）

**结构认知**：
- body = x{@263，marker 73×19/76×88/92×112/96×120/D6×84
- 商品目录流 130+ 条记录（核芯 660002~660074 / 皮肤 1110013~1110171 / 载具 193/194/182xxx / 福虎 57000xx×8 / 46xxxx 时装群 / 召唤器段 633090140…）
- 价组三元组 `[X,1]` / `[X]` + `[货币,价]`——**价组可前可后于品行**（前向+后向都要绑；3 石价组在帝皇盒行之前=曾丢绑）
- 无任何时间戳/限购字段（ts 形值 0=字节级验证）

**定性（核心结论）**：002962 = **客户端候选池/静态默认货架**（130+ 品历史返场库），当期商店=服务端池选+新货下发（星月落羽/深渊之力/凝渊之擎/福虎典藏=静态无行）。固定格≈常驻位（实机同价）、轮换格≈服务端覆盖（浑天穹焰 拆 5/1 vs 核 35 特惠=打折覆盖原价先例）。

**锚↔静态反查法**：实机价档 → 静态价组双向候选 → id 级唯一锁定（12 品实证：贯通 30+40 双档=特惠划线互证、105 档=守御灵配方（曾误绑 660061 流光疾射）…）

### 4.2 载具——vehicle_ui_data（014186/CHS 014204）

**数据源**：车库注册表 014186.bin（23KB，274 行）+ CHS 池 014204（105 条=字段名池 1-35 + 车名/desc 全集）。

**格式解剖（27.112–27.114）**：
- 行布局：头部 schema 区（0-2874）→ D6 行区 226 行（=变体行：D6 + 固定 83 + 记录号（177/414/578…递增=每车一组） + 数值参数流=无文本，行含 double（0x66×6+e6 3f=0.7 被 uleb 误读元凶））→ 文本行区 ~48 行（C6/76/86 开头=含车辆 key 194167 + desc 池引用=uleb/double 混合值流）→ 尾索引
- **尾索引（21900+）= 车库全量显示序：154 个 id 交替 = 77 对（193xxx 本体 + 194xxx 皮肤对）+ 递增排序值**。已实证=与车库 UI 滚动序 1:1（月舞风华=193013=图 2 第一辆✓ 古典绅士=193014✓…缺号 193016=隐藏品）
- 3 个标准 schema 行（194097/194106/194166=羊羊摇摇车 14 天=活动车=002962 池无=交集空=正常）

**名册锚定成果（2026-09-07）**：车库截图 47 辆（DS vision-exp 读图=Agnes 挂后的替代通道）↔ 尾索引序 1:1 = 47 辆官方名 id 级锚定（193013 月舞风华→194147 独行者）；002962 池 31 品回填命名（commit 17ee9c7）；vehicle_garage_names 板 47 行上板（commit b9b6339=时装类（八）载具占位转正）。
- 首排 7 个自定义名（香菇菇菇/淇铭/…）=玩家命名=排除；都市游侠=追光/怒火（用户确认，此前误读追风/怒人）。

**残留**：vehicle_catalog 板（125 型号=body_model 锚）=quarantined（all_equips name 槽跨记录错位）；型号↔车名桥=需 vehicle_ui 行级参数解析（工具缺口，见七）；索引 77 对中 30 辆未截图=可补滚屏。

### 4.3 神秘商店——RandomDiscountHD

- 静态侧封顶=**证据闭环**：discount 族 28 表全扫=全无关（配方改造/月卡/家园派对折扣）；random_discount 名 0 命中=**商品载体表客户端静态确定缺失**。
- 板上限：mystery_shop_panel_static.json=4 期行+系统定位+返场候选链+刷新币机制。下一步=等开店实机截图（服务端下发）。

### 4.4 芯片/核芯/时装/奖池/武器皮肤（已发布板，简引）

- 芯片图鉴（chip_type 池全集）/ 限定芯片抽奖（半闭合=期次↔时间窗待校准）
- 核芯卡（双服合并：经典 12 星+体验 12 星）/ 核芯研制（半闭合）
- 时装外观表/背包挂饰/面饰挂饰/荧光棒/伴身投影/本场最佳=player_appear 族各槽行级复原
- 抽奖活动（帝皇一期·再临二期）双分支定位 / 新奖池预告（未上线=仅行为资源，先对照历史更新汇总）/ 满减市场 / 礼盒文字表 / 武器皮肤图鉴（正式名+时限变体）
- 武器皮肤预告板（skin_behavior_preview）：仅行为资源未上线=不表示上线或可得（预告别）

### 4.5 其它域定位链备忘

- 武器三条件（父项/道具行/行为资源）重做=等锚清单在列
- 零/一/二区核验=细节丢失需重新指定范围（旧审计产物 03拆包产物/wiki_position_chain_audit_20260902）

---

## 五、硬锚 id 表（用户实机验证=user-verified 级）

| id | 名 | 备注 |
|---|---|---|
| 153036 | 宸晶臻石 | 臻藏币（名册硬锚；「宸世臻石」=转录笔误不用） |
| 153040 | 稀世之证 | 稀世币（名册硬锚） |
| 156182 | 重构转印器 | 臻藏常驻 2 石 月限 1/1（唯一无倒计时） |
| 139267 | 帝皇战翼交易盒 | 铠甲联动=臻藏 3 石 限 3/3 |
| 660060 | 贯通战术 | 稀世 30（特惠）原价 40=双档互证 |
| 660076 | 余烬流火 | 稀世 30 特惠 |
| 640015 | 浑天穹焰 | 经典臻藏 35 特惠 vs 体验 5/1=双服价目不同实证 |
| 640011 | 时空裂隙 | 经典臻藏 2 石 vs 体验稀世 50 证 |
| 1110021 | 紫焰蛇矛 | 皮肤 |
| 366126 | 霓虹恶魔 | 稀世 450（002962 池 194130=同车双 id 先例） |
| 152182 | 飞行载具改装模块 | 稀世 10 |
| 153523 | 银蛇迅影升级芯片 | UI 全名含「升级芯片」（9-01 录缺二字） |
| 633070140 | 铠甲再临 | 召唤器段真锚（633090140 非刑天=勿再串） |
| 135048 | 福鼠迎春典藏 | gift_data 唯一命中 |
| 守御灵配方 | 105 档 | 实机锚（曾误绑 660061） |
| 一瞬光年 | 50 证 | 9-06 特惠（vision 误读 100=用户纠正） |

载具锚（47 辆全表见 `external_refs/vehicle_garage_registry.json` + board vehicle_garage_names）：
193013 月舞风华 / 193014 古典绅士 / 193015 金鳞浮光 / 193017 银虹贯日 / 193018 星光掠影 / 193019 初樱绽放 / 193020 机动阿波罗 / 193021 极夜闪光 / 193022 鹿鸣星月 / 193023 摩羯座·银河踏步 / 193024 金甲凯旋 / 193025 天马淬火 / 193026 猎户战歌 / 193027 绝影星鸿 / 193028 丹凤飞焰 / 193029 天蝎座·月下美人 / 193030 迅电流光 / 193031 银龙入海 / 193032 黄金镖客 / 193033 沧溟脉冲 / 193034 青锋铸钢 / 193035 铁马冰河 / 193036 幽野疾风 / 193037 赤鬃踏炎 / 193038 铃弧飞翼·霜梦 / 193039 猎户座 / 193043 伏暗追光 / 193045 双栖幻影 / 193046 小叶鲸 / 193047 旷野骑士 / 193048 霓虹恶魔 / 193049 都市游侠·追光 / 193050 都市游侠·怒火 / 193051 急驰救护 / 193052 彩虹之旅 / 193053 驰风电轮 / 193054 雪人滚滚 / 193055 雪人圆圆 / 193056 美梦骑旅 / 193057 都市游侠 / 193058 游园单车·樱草 / 193059 游园单车·雏菊 / 193060 游园单车·朝颜 / 193062 飞爪青龙 / 194146 逐风者 / 194147 独行者（+银骑飞鹰 194122/194123 对）

---

## 六、阴性表族登记（穷尽证据=不再重扫）

| 表族 | 结论 |
|---|---|
| optional_hd_exchange / optional_version（ykxq 域） | 007946=全量主表误判收回；三通道同内容=当期单快照；历史期=客户端不存在 |
| collect 族 319 表 | 卡牌/执照类=非商店 |
| discount 族 28 表 / random_discount | 神秘商店载体缺失=静态封顶证据闭环 |
| res_handbook（005886/023520） | 1344xxx 资源域≠194xxx 载具域=阴性 |
| root 老包 | 规则禁（用户定版边界） |

---

## 七、工具缺口与出路

| 缺口 | 说明 | 出路 |
|---|---|---|
| parse_index 不支持特形索引 | 002962 同族 0x76 特形、vehicle_ui_data（「index bucket count unreadable」）——bindict 核心禁改 | 独立索引解析器=专项轮（27.114 登记） |
| vehicle_ui_data 行值流字段类型表 | 头部 schema 区（0x27 组）未读透；uleb/double 混合切分需字段序 | 从头部 schema 类型表收尾=一次专注轮 |
| 504 无名品正式名 | 双服所有静态名册穷尽阴性 | 更新包登记 / 用户图鉴截图 / 服务端 |
| 载具 30 辆（索引无截图） | 77 对中 30 辆无名 | 用户再滚两屏车库=全锁 |
| vision 主通道 | AgnesAI 401=外部故障；已切 deepseek-v4-flash-vision-exp（config auxiliary.vision；Agnes 恢复后可选切回） | DS vision-exp 读图已验证可靠 |

---

## 八、证据等级与发布契约速查

证据枚举（meta/行级，与 policy 校验一致）：`structure`（结构/名册）/ `verified`（跨源互证或用户核验）/ `candidate`（候选/静态推测）——板级 evidence 同枚举。
行级语义细分：锚=user-verified 级（provenance.user_evidence 必填）、名册=structure-only、无名=static/candidate。

发布 7 契约（任一不过=build 拒+测试红）：
1. provenance.source_entries 非空（entry_index/file_id/decoded_sha256）
2. decoded_sha256=源 entry 实算 SHA-256
3. 卡顶层 source 字段
4. evidence 值 ∈ 枚举（无 "verified"/"candidate" 字样=只取枚举值）
5. user-verified 级必须 provenance.user_evidence（锚=用户原话）
6. meta.provenance.source_locks[0] 含 sha256/bytes/mtime_ns（可机读源锁）
7. tests/test_publication_gate.py 期望（板数/条数）随板行数同步

发布动作边界：「发布 wiki」=本地 data/boards + manifest 重建（wiki_server 8765 本地浏览）；**不部署公网**。

---

## 附：关键文件索引

- 日志：`E:\la拆包项目\06（agent写）拆包器进展与交接日志.md`（27.107–27.114）
- 源包锁：`08Lifeafter wiki\data\live_sources.json`
- 双源校准实证：`docs/DUAL_SOURCE_CALIBRATION.md` + `external_refs/dual_source_calibration.json`
- 板数据 21 板：`data/boards/`（宸世 29 行=28 期次+常驻池卡；载具名册 47）
- 锚点资产：`external_refs/chenshi_shops_snapshot_20260906.json`（84 行）、`chenshi_static_pool_002962.json`（702+audit）、`vehicle_garage_registry.json`（77 对）、`vehicle_garage_anchors_20260906.json`（75 名锚）、`vehicle_ui_pool_names.json`（23 候选名）、`announce_*.json`（公告期次锚）
- 待办参考：`docs/HANDOFF_TO_DEEPSEEK_V4F_20260903.md`、`E:\la拆包项目\wiki待优化事项.txt`
