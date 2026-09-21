# 抽奖/奖池定位链方法论（LOTTERY CHAIN LOCATOR v1）

> 目标：任何「活动 → 主池/子池 → 奖励叶子 → 概率」的定位，都按本链逐层推进；
> 每一层有原始出处才能进下一层；断点必须精确定位并移交运行时通道，不许用猜补链。
>
> 本文档由铠甲再临二期（刑天/飞影）定位战役沉淀（2026-09-06，06 日志 27.63-27.69）。

## 1. 分层模型（每层独立验收）

```text
L0 展示层      super_fashion_lottery_conf_data.<活动行>.panel_show_item_ids
              → 只证明 UI 展示；不等于真实 reward slot 顺序或概率。

L1 活动配置行  super_fashion_lottery_conf_data key=N
              lottery_id（→ L2 主池）、lottery_group_id、fortune_bag_dct（→ 福袋小池）、
              rule_id / lottery_share_conf_id / lottery_ui
              → lottery_id 就是 reward_pool 池 ID，无中间映射表（common_lottery 侧已证阴性）。

L2 奖池        reward_pool_data_base 内 [pool_id, slot] 行集合
              → 每行带 note/name、broadcast_content、expiration_time、prob_note、reward jump→leaf。
              → 跨活动复用池（同名池含不同广播/有效期行）必须按 cohort 切分：
                同 broadcast + 同 expiration_time 的行才同属一次活动实例。

L3 叶子        reward jump → 0x27 组 [item_id, quantity]（common_item/道具层命名可查时）
              → 组内首元素 == pool_id 时只是“池 ID 被复用为奖励”候选，
                不得自动晋升为父子池边（391536→391772 教训）。

L4 二次路由    「奖励是珍匣/福袋类触发物 → 从另一池再抽一个」
              → 目前 BA8 已解包表内无静态路由表（27.68 全排查）；
                命中此类缺口直接移交运行时 selector，不扩静态扫。
```

## 2. 双源分支判定法（先于一切归属结论）

包内同一逻辑表常有多份文件，分支归属判定顺序：

1. **同 FID = 同文件**：两 NPK 中 FID 相同的 entry 是同一份数据，路径/entry index 不同不算差异。
2. **主表对比**：`<表>_data(_base)` + `<表>_data_chs` 两包逐表 SHA 一致 → 行侧无分支差异（铠甲 8 表实证）。
3. **变体定位**：`<表>_data_auto_oversea_data_{kj1,kjxq,yk,…}` 变体文件，先查**两包各自是否存在**：
   - 只存在于测试服包（BA8）→ 是**测试服覆盖通道**（把活动指向测试环境自己的池）；
   - 两包都有 → 逐行对比，差异行才是分支证据。
   - 单看「BA8 有变体」不能证明该变体=服务器分支载体，必须对照正式服包有无。
4. **同名族文件先验结构再判角色**：0x73 头 + `{` 池无 `x{` = CHS 文本池（即使 655KB 也是池）；
   有 `x{` 才是行表；`_base` 后缀的行表只有一份时，通道差异只可能在文本池层。
5. kj1/kjxq 后缀 = 数据通道名，不是服务器名；通道语义要靠上面 1-4 的证据落定。

## 3. 表文件定位法（无 manifest 名字时）

- BA8 工作副本 manifest 条目无 name 字段 → 用**尾部模块名扫描**：
  每个 entry 尾部 ~4KB 找 `.py` 路径（`com\cdata\<表名>(_chs|_auto_oversea_data_*).py`）。
- 正式服工作副本 manifest 有 name → 直接按名查 entry。
- 命中文件按体积分层：几百 B=壳/桩、1-40KB=配置行表、数百 KB=CHS 池或大行表；
  尾部无 .py 且几十 KB~MB = 大表体（按内容指纹另行识别）。

## 4. 表族档案（BA8 实测，2026-09-06）

### super_fashion_lottery_conf_data（时装抽奖配置）
| 角色 | BA8 | 正式服 | 说明 |
|---|---|---|---|
| 主表 | 012591（FID 7E5A5A83B1F07D31） | 022498 同 FID | 两服同一文件；26 行 |
| 主 CHS | 007953 | 014527 | |
| kj1 变体 | 012545 + chs 009828 | **无** | 测试服覆盖通道 |
| kjxq 变体 | 004258 + chs 018233 | **无** | 同上 |

行字段：lottery_id / lottery_group_id / lottery_share_conf_id / lottery_ui /
rule_id / share_reward_id / ui_group_id / weapon_display_video / quick_buy_id /
fortune_bag_dct(jump→0x36 map) / panel_show_item_ids(jump→0x27 组)。

- fortune_bag_dct = 0x36 映射 `{key: pool_id}`，语义 = **福袋附加小奖池**；
  主表 key232 → {4: 391783}（铃兰福袋系），kj1 key232 → {726: 391786}（天国家具系）。
  ⚠️ fortune ≠ 秘宝/珍匣内容池；秘宝池不挂在 fortune 字段。
- 0x36 判定：`[36][kt][vt][pair_count uleb][(key uleb, value uleb)×n]`。
  ⚠️ 判定代码别用 `blob[t:t+2] == b'\x36'`（长度不匹配恒 False，实踩）。

### reward_pool_data_base（奖池行表，唯一行源）
| 角色 | BA8 文件 |
|---|---|
| 行表 | 021380（1.09MB，唯一带 x{ 的行表；两服同 SHA） |
| 主 CHS | 010496 |
| 通道 CHS（yk/kj1/base_yk/base_kj1/chs 族） | 010219 / 023723 / 010551 / 023391 / 023705 —— 全是文本池，无行数据 |
| kj1/kjxq 覆盖行表 | 012386 / 023115（各 237 行，auto_oversea_data 版；目标池零命中=不是铠甲分支载体） |

行内 0x27 组 `[pool_id, slot]` marker = `27 01 02 + uleb(pool_id)`；
cohort 切分用 broadcast_content + expiration_time。

### common_lottery_conf_data（货币/次数抽奖配置，与时装抽奖无关）
- 主表 008644 + chs 000035：371 行；kj1/kjxq 覆盖 000675/021903 各 2 行（key 4/117 货币配置）。
- 目标 lottery_id 全不在 → lottery_id 无中间映射表，super_fashion 直连 reward_pool。

### fashion_sale_conf_data（时装售卖）
- 主表 001388 + chs 001940：75 行；无 reward_pool 池引用（铠甲目标零命中）。

### lottery_big_reward_conf / index（大额/复合奖励）
- 006173（1314 行）/ 002571；目标池 ID 零命中 → 不是珍匣路由表。
- 行形态：`[big_item_id, qty]` 0x27 组注册（如飞影召唤器 [633080140,1] row 20413），
  但注册 ≠ 活动池归属。

### reward_pool_no_item_no_list（017006）
- key → 嵌套 ULEB/组大 blob；目标同现但相隔数千字节 ≠ 引用关系；语义未闭合，勿当路由表。

### common_item（道具名册）
- 018005 + 023928（35986 行）；奖池触发物（391772 等）/召唤器/面饰叶子常不在道具层
  → 名册缺失不能反推「无此物」，只说明名册层不收录。

## 5. 铠甲二期实例（已闭合/未闭合对照）

### 已闭合（原始行 + prob_note）
- 主表 key232（两服同）→ lottery 391782：菌焰喷火器典藏 slot0 prob 0.00163、
  雨战版 slot1 prob 0.00253（经典服锚点命中；行级 broadcast「铠甲再临」+ exp 1801353599）。
- 面板 10 项（L0 展示，kj1 与主表一致）。
- 内容池静态行（无活动行引用=孤儿，勿当发布结论）：
  - 390704 秘宝 cohort（exp 10377590399）9 项 + prob（缺飞影召唤器 slot/prob）；
  - 391536 cohort（exp 1801353599）16 项 + prob（无菌焰；含珍匣触发 slot2 0.03706 → [391772,1]），
    缺锚点 4 项（飞影锋眸/能量电池/酸焰核芯/1型记忆材料）；
  - 391533 cohort（exp 1801353599）17 项 + prob（含菌焰雪地版=经典向嫌疑）。

### 断点（移交运行时）
- kj1/kjxq key232（测试服覆盖）→ lottery 391785 / fortune 391786：两池静态内容为空
  （391785=虹神北斗/宸世臻藏等旧行，391786=天国家具/纳米旧行）。
- 391536/390704 无任何 super_fashion/common_lottery/fashion_sale 行引用；
  「珍匣 → 秘宝池」无静态路由（391772→390704 全排查阴性）。

## 6. 验收门禁（发布前必须全过）

1. 三池成员与用户锚点逐字一致（fixture：tests/fixtures/kaijia_simple_survival_anchor.json）；
2. 每个实际奖励都有原始 prob_note；
3. 活动行 → 池的引用链闭合（不能是孤儿池）；
4. 双源分支归属有证据（主表 vs 覆盖通道，见第 2 节）；
5. 展示名与内部标记并列（火刑裁决/火刑电光炮；面饰：刑天面甲/刑天口罩），名称桥不代替归属证据。

未过门禁 = 保持未发布，宁可 null。

## 7. 可复用工具链

- 行表解码：`tools/trace_kaijia_formal_reward_chain.py`（pool→record 追踪骨架，含 0x36 fortune 解析）；
- 池 dump：按第 4 节文件定位 + `bindict_provenance.decode_table_rows_with_chs_slots` + 0x27 marker 扫描；
- 双源对比：FID 直读（LiveNpkReader by_fid）优先于 entry index。

## 8. 外观锚点 → 活动载体定位链（满减案例，2026-09-06 沉淀）

适用：用户只给「某活动里见到的外观/商品名」，要反查该活动及其载体表。

步骤：
1. **名册反查 id**：外观名 → 名册表行 key。名册按外观类型选表：
   `player_module_appear_data`（面饰/时装格）、`fashion_data`/`simple_fashion_data`（时装）、
   `buff_data`（伴身投影/称号）、`weapon_skin_data`（武器皮肤）、`gift_data`（礼盒/交易盒）、`common_item_data_base`（道具）。
   时限变体同行族（如 -1/3/7/30 天）。
2. **活动注册反查**：`huodong_conf_data_*`（活动总表）按活动名/子系统定位 hd 行——字段
   `hd_class`（类型类名）、`ui_class`（UI 入口）、start/end_ts、sub_title。
   满减家族：旧 `ManJianHuoDong/ManJianMarketUI`（2023-24）vs 新 `DiscountMarketHD/DiscountMarketHDUI`
   （2025-26 各期「XX满减补贴」，如 灵笼满减补贴 huodong key 3402，2026-04-16~30）。
3. **数值同现定位**：多锚点 id 的精确 ULEB 在 BA8 全条目出现表 → 排除名册/公告/交易/行为表后，
   剩余即商品/定价载体候选。满减案例四锚点（136388/640041/492700/1110156）同现 51 文件全为存在性表
   → DiscountMarketHD 商品载体表静态缺失（模块名扫描 0 命中双重印证）。
4. **锚点侧直接引用**：唯一活动级直接文本=136388 desc「灵笼满减活动结束后可交易」（gift 通道增量 yk）。
5. **判定与交付**：半闭合板（活动族期次行 + 锚点名册行 + 缺失声明），禁声明定价/档位/在售；全闭合需
   商品载体表（运行时或其它包）。未上线判定纪律不变：名册/行为/公告命中≠上线。

## 9. 核芯研制 / 芯片保底定位链 + 通道层级铁律（2026-09-06 沉淀）

### 9.1 通道层级铁律（本批最大教训，先于一切活动类侦察）

BA8 内同一逻辑表存在**多通道变体**，层级必须分清，否则期数结论差数倍：

| 通道 | 文件 | 行数 | 性质 |
|---|---|---|---|
| **ykxq（主表全量）** | 024329（huodong 1382 行，0 unbound） | **权威全量**：含全部历史期（2023-05 起） |
| kj1 | 025079（858 行） | **后期覆盖子集**：只含近段期（如核芯仅 10 期→真实 72 期） |
| kjxq/yk/xq | — | 更小子集/壳 |

铁律：
1. **活动注册/期次类结论必须以 ykxq 主表为准**；kj1 只用于"覆盖差异对比"（如 sub_title 覆盖 bug：kj1 把核芯 9 期 sub_title 复制成「电掣双刀返场」=占位，ykxq 全真实期名）。
2. **行数对不上时先怀疑通道**：NucleusLotteryHD kj1 10 期 vs ykxq 72 期（2023-08-04~2026-09-16）——用户连续五次纠正"期数不对"才暴露。
3. ykxq decode：base F394516378015E27 + chs DACF87AE00F14120（0 unbound）。

### 9.2 核芯研制链（限定核芯研制，NucleusLotteryHD）

```
huodong_conf ykxq（72 期）→ 期次行：start/end + sub_title=UP 期名
期名语义（用户口径）：「XX登场」=新核芯首次出（约 1 个月期）；「XX返场」=老核芯回归（约 2 周期）
  同名返场可多轮（电掣双刀返场 ×10；凝滞侵袭返场 extra45/70/73）
期名↔核芯本体：期名去"登场/返场"=核芯名（如 凝滞侵袭=异变核芯-凝滞侵袭 660072 特级·狙击）
  核芯全集=660000 段 77 卡（nucleus 卡板）；核芯词条=350000 段（nucleus_conf）
研制池族：nucleus_lottery_pool_data（kj1 003119，355 行）：nucleus_lottery_pool_id→reward_pool_id
  + is_guarantee/init_weight/display_group（极品/基础异变核芯）——外围奖励池行；UP 核芯本体不在此层
```

### 9.3 芯片保底链（限定芯片抽奖/自选，BeltChipSpecialLotteryHD）

```
huodong_conf ykxq（30 期，2023-05-25 起）= special_chip_lottery_hd_conf（30 行）1:1（conf key n ↔ 期序第 n 期）
conf 行：up_chips（UP 组：旧格式 2 款/新格式 ui20 8 款=返厂 8 个）、new_chips、active_pool_ids、
  rule_ids、gold_chip_guarantee_num（80/450）、total_guarantee_num（170/180）、discount_rate=0.9
rule 行（60）：pool_id→reward_group，reward_guaranteed_num=2 / group_guaranteed_num=80
保底物=rule reward 首值（[item,count] 取 item）：旧格式「XX自选箱」（240807 连环暴击自选箱）/
  新格式 241405 限定特级芯片自选箱
芯片名册：common_item 330xxx/331001-331017（67 卡）；331018+ 名册缺口=名册外 id（如实 '?'）
```

### 9.4 双服差异判据（活动期名 ≠ 当期内容）

- huodong 主表（ykxq）=**两服共享**：期名=经典服视角（如芯片 key30 期名「破盾强攻返场」）。
- special_chip conf/rule 仅 BA8（简单服测试包）打包：UP 组=简单服实际配置（key30=连环暴击 8 款，
  因简单服无破盾强攻故替换——用户校准）。正式服包 0 命中 special_chip 表=经典服当期内容运行时下发。
- 判据：**期名/活动壳看 huodong（共享层）；当期内容/UP 名单看 conf（如为 BA8 专属=仅简单服，经典服需运行时）**。

### 9.5 验证锚点（用户验收 2026-09-06）

- 核芯：凝滞侵袭返场=extra73 2026-09-03 当期（BA8 内末段）；电掣双刀返场多次；穿心极雷登场/返场。
- 芯片：key30=2026-07-16~08-05；当期 8 款名单（连环暴击/覆盖打击/好事成双/势如破竹/全副武装/
  坚如磐石〔331026 用户补名〕/坚韧不拔〔331018 用户补名〕/荆棘护盾）。

### 9.6 宸世臻藏链（2026-09-06 重建；此前误把 common_exchange 当宸世=勘误见 27.105）

「宸世臻藏」=**独立活动体系**，只含以「宸晶臻石（臻藏商店）+ 稀世之证（稀世商店）」为货币的
内容。**不属于宸世**（勿混入）：common_exchange_shop_data（通用兑换=商队/集市，载具格子在此）、
MultiOptionalLotteryHD（幻海旖旎/青春变奏曲/喵不可言/学院企划/夏日香氛=独立主题时装自选活动，
仅同 Optional 框架）、WeaponDecompOptionalHD 战备工坊（经典武器返场=独立）——用户 2026-09-06
「把宸世里面的乱七八糟的东西删掉」定版。

```text
活动注册（huodong ykxq 全量 1382 行）：
  OptionalLotteryHD「宸世臻藏」key2538（2024-04-26 起=长驻框架行，end 空=每期服务端轮换）
  OptionalExchangeHD「臻藏商店」key2591（货币=宸晶臻石 153036，兑换高价值臻藏外观）
  OptionalExchangeHD「稀世商店」key2592（货币=稀世之证 153040，道具 desc 又称「稀有商店」）
货币/道具链（common_item 名册）：
  宸世之钥 153035（宸世臻藏活动中消耗，开启不同宸世宝箱=抽奖券）
  → 宸世宝箱 → 宸晶臻石 153036（臻藏商店货币，不回收永久）+ 稀世之证 153040（稀世商店货币，
    不回收永久）+ 臻藏时装兑换券 155956（兑典藏/幻彩时装，长期有效）
  （99736/99741=宸晶臻石旧版/独享版）
商店载体表：
  optional_hd_exchange_shop_data 主表 002962（81.5KB FID 1E888FAB015CA82D 双源共享）+ yk 变体
  005580（76KB 双源共享）——臻藏/稀世两商店商品行（行内应含货币字段=石头/稀世之证两系；
  ⚠行级=0x76 特形索引=parse_index 不支持 decode 0 行=待工具扩展；解出后按货币字段筛两系，
  其余不展示）
  宝箱随机奖励载体候选：ext_dynamic 007729（1.8MB，臻石+兑换券 uleb 同现；未解）
载具：可升级飞行载具（灰翼游鹰等）随宸世臻藏返场=臻藏商店/稀世商店/宝箱产出（公告实证）；
  common_exchange 同段格子=通用商店≠宸世
双源：optional_hd_exchange_shop_data 主/yk=双源共享（经典服同读）
```
