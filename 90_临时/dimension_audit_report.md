# 时装/外观域 · 维度字段全树普查

> 目标：回答「要建一张全量索引，每个维度该从哪张表取」。
> 范围：`01_索引与产物/41_还原树/pe/配置/com/cdata/` 共 12,451 张表（9,808 张成功解码，2,643 张无 `{ CHS` 池或空 body 跳过）。
> 口径：`decode_table_rows(..., resolve_jumps=False, lenient=True)` + 自定义 `expand()`（含 `kind 0x01` 字面整数支），所有数字为实跑结果。
> 生成日期：2026-11-01

## 0. 字段名全表普查（缓存 `90_临时/ref_scan_cache.jsonl` 结构确认）

缓存每行 `{t:表名, ok, n:行数, cnt, unb, f:[[字段,非零行数,distinct,...]], allf:{字段:非零行数}}`。
`allf` 用于字段名存在性扫描，值域统计另行解码（缓存里的"非零行数"对 bool 字段是 True 计数，对 jump 字段不可靠，故未直接引用）。

| 维度 | 命中字段名数量 | 命中表数量 | 时装域真正相关表 |
|---|---|---|---|
| D1 icon | 610 | 930 | 3（fashion_data / fashion_data_for_export / simple_fashion_data / player_module_appear_data） |
| D2 desc | 786 | 1,957 | 4（fashion_data / player_appear_data / player_module_appear_data / desc_info_data） |
| D3 charm | 12 | 33 | 3 + follow_charm_conf_data |
| D4 flower | 29 | 15 | 2（fashion_data / player_appear_data） |
| D5 hide/mutex | 252 | 858 | 3 |
| D6 gender | 100 | 172 | 1（player_appear_data） |
| D7 小参 | 20 | — | 3 |

---

## D1 取图（图标）

| 表 | 字段 | 有值行数 / 总行 | 形态 | 说明 |
|---|---|---|---|---|
| **fashion_data** | `icons` | **11,169 / 11,169（100%）** | jump → kind 0x05 | 每行**恰好 2 条** `ui/item_icon/*` 路径，共 22,338 条 |
| fashion_data_for_export | `icons` | 10,988 / 10,988 | 同上 | 切片，与主表同源 |
| simple_fashion_data | `icons` | 11,169 标称 | 同上 | **实测 9,321 行展开为空**（jump 偏移在该表 blob 中取不到组 0x05），不可作为图标源 |
| **player_module_appear_data** | `icon` + `female_icon` | icon 1,200 / 1,200；female_icon 1,174 / 1,200 | 0x05 字符串 | 双列都有 1,174；仅 icon 26；仅 female_icon **0** |
| player_appear_data | — | — | — | **121 个字段逐个核对，无任何 icon 字段**（`icon`/`icons`/`icon_path`/`head_icon_path` 均不存在） |

**每一行路径数分布（fashion_data，11,169 行）**

| 路径数 | 行数 |
|---|---|
| 1 条 | 0 |
| **2 条** | **11,169（100%）** |
| 3 条及以上 | 0 |

**两路径的配对形态**

| 形态 | 行数 | 例子 |
|---|---|---|
| `icon_*_f_*` 在前、`icon_*_m_*` 在后 | **9,537（85.4%）** | `icon_b_f_3544001` / `icon_b_m_3544001` |
| 两条完全相同 | 342 | — |
| `icon_<n>_1` / `icon_<n>_2` | 1,135 | `icon_366758_1` / `icon_366758_2` |
| 纯数字对（无性别标记） | 155 | `icon_32548` / `icon_32553` |

**结论**：`fashion_data.icons` 是唯一权威来源，100% 覆盖，恒定 2 条，顺序为 **[女, 男]**（由 9,537 行 `_f_` 在前的显式标记确定；现有板 `icons_all` 的 gender 标注 女 1,750 / 男 1,749 与此一致）。`player_appear_data` 完全不存图标，图标只能从时装行取。**不存在独立的"图标 ID → 时装"映射表**（`gift_data`/`new_role_desc_data`/`recipe`/`ugc_special_desc_data` 虽也有 `icons` 字段，但值域属掉落/配方/角色包，与 11169 时装键零交集）。

---

## D2 描述

| 表 | `desc` | `female_desc` | `man_desc` | 总行 |
|---|---|---|---|---|
| **fashion_data** | **11,041（98.9%）** | 21 | 33 | 11,169 |
| player_appear_data | 2,909（51.9%） | 6 | 6 | 5,604 |
| player_module_appear_data | 1,200（100%） | 无此字段 | 无此字段 | 1,200 |

**语义（关键发现）**：21 行同时有 `desc` 与 `female_desc` 的记录里，`desc == female_desc` **21/21 全等**。即 **`desc` 就是女版/通用版，`man_desc` 是男版覆盖**；`female_desc` 只是极少数（21 行）的冗余副本。

**男女分版确实不同——5 个例子**（同一行三字段并列，原样）

| key | name | desc（女/通用） | man_desc（男版） |
|---|---|---|---|
| 366212 | 战术专家（Resident Evil） | Resident Evil生化危机中艾达·王曾经穿着的衣服。 | 生化危机中里昂·斯科特·肯尼迪曾经穿着的衣服。 |
| 366466 | 自由之翼 | 米卡莎在調查軍團穿的衣服。「明日之后×進擊的巨人」聯動限定物品。 | 艾連在調查軍團穿的衣服。「明日之后×進擊的巨人」聯動限定物品。 |
| 366468 | 扫除时刻 | 進擊的巨人中希絲特莉亞的衣服。… | 進擊的巨人中里維的衣服。… |
| 366337 | 最强义体 | [明日之后x攻壳机动队]素子入侵电子脑时所穿的紧身衣。 | 巴特在生活和执行任务时所穿着的服装 |
| 469060 | 战斗服・EVA零号机版 | female_desc：还原丽的战斗服。… | 还原真嗣的战斗服。… |

**富文本标记统计（不清洗，14,016 个文本块）**

| 标记 | 次数 |
|---|---|
| `#r`（换行） | 1,628 |
| `#n`（颜色复位） | 920 |
| `#cRRGGBB`（6 位色值） | 727 |
| `#f(...)`（字型/字号） | 404 |
| `#r(...)`（带参换行，实为文本误匹配） | 3 |

**独立描述表**：`desc_info_data` 3,684 行，仅 `title` + `desc` 两字段，内容为 UI 帮助（"图纸打印""防御分值""辐射诡楼规则说明"），与时装行键**键交集 0**，非时装描述。`desc_info_data_kj1` / `desc_info_data_yk` **解码失败**（body 长度为 0，无数据），已跳过。

---

## D3 魅力值

| 表 | 有值行数 / 总行 | 覆盖率 | 取值范围 | 不同取值数 |
|---|---|---|---|---|
| **fashion_data.charm_value** | **9,232 / 11,169** | 82.7% | 0 ~ 3,000 | 41 |
| player_appear_data.charm_value | 2,375 / 5,604 | 42.4% | 0 ~ 3,000 | 36 |
| player_module_appear_data.charm_value | 1,153 / 1,200 | 96.1% | 10 ~ 350 | 6 |

**一致性**：按 `appear_ids` 关联出 **16,489 对**（时装行 ↔ appear 行），`charm_value` 完全相同 **16,489 / 16,489 = 100.00%**；随机抽 30 例核对 30/30 一致（如 472833→334000201 均 130；478261→13336601 均 1100）。三表无 `-1` 哨兵值，`0` 极少（fashion 56 行 / appear 16 行）。

**独立魅力表**：`follow_charm_conf_data` 57 行（`buff_id` / `charm_value` / `source_content`），其中 53 行有 `charm_value`（1~2,000）。它是"魅力值**获取来源 / 阶段奖励**"的 buff 门槛表（如 20001 = 1000，"魅力值闪耀商店限时获取"；20301 = 2000，"魅力值阶段达成奖励"），**不做逐件定义**，与逐件的 `charm_value` 无外键关系。未发现 `charm_level` / `charm_point` / `charm_score` 字段。

---

## D4 藏花（花苞 / 花部替换）

| 表 | 字段 | 有值行数 | 值域 |
|---|---|---|---|
| **fashion_data** | `replace_flower_path` | **63 / 11,169** | jump → 2 条 `.gim` 路径，5 组不同值 |
| **player_appear_data** | `replace_flower_id` | **10 / 5,604** | 70893/70894/70895/70899/70900 + 170893/170894/170895/170899/170900 |
| player_appear_data | `part == 7` | **22**（女 11 + 男 11） | 花部件行 |
| 其他 | `hide_flower` / `flower_id` / `replace_flower_path`（appear 侧） | **无此字段** | — |

**`replace_flower_id` 的 10 个值指向**（去 appear 表查行）

| 源 appear 行 | name | part | → 目标行 | 目标 name | part |
|---|---|---|---|---|---|
| 3346001 | 香韵弄樱-衣服 | 3 cloth | 70893 | 香韵弄樱 | 7 |
| 3349901 | 尼罗河传说-衣服 | 3 cloth | 70894 | 尼罗河传说 | 7 |
| 3355101 | 心绪共鸣-衣服 | 3 cloth | 70895 | 心绪共鸣 | 7 |
| 3364501 | 雪语冰梦-衣服 | 3 cloth | 70899 | 雪绽霜华 | 7 |
| 3366101 | 樱灵狐梦-衣服 | 3 cloth | 70900 | 折樱见春 | 7 |
| 13346001 / 13349901 / 13355101 / 13364501 / 13366101 | 同 5 款（男版） | 3 cloth | 170893 / 170894 / 170895 / 170899 / 170900 | 同名 | 7 |

**`replace_flower_path` 与 `replace_flower_id` 的关系**：同一批 **5 款衣服**。`path` 是花部替换模型（`character\monsters\cloth_<id>_hua\cloth_<id>_hua.gim` + `_1.gim`，5 组：3460 / 3499 / 3551 / 3661 / 3669），`id` 是花部 appear 行号。两者款式集合一致，但 3 款同名、2 款花名不同（雪语冰梦→雪绽霜华，樱灵狐梦→折樱见春）。

**part=7 / 花苞行**：fashion_data **无 part=7 行**（part 只有 1/3/4/5/None）；player_appear_data 有 22 行 part=7（70891~70901 女、170891~170901 男），其中 70891「花朵」、70892「控制器」为基座行，其余 9 对为可选花饰。

---

## D5 藏头饰 / 面饰 / 挂饰

**各字段有值行数与取值分布**

| 表 | 字段 | 有值行数 | 取值 |
|---|---|---|---|
| fashion_data | `hide_other_part` | **762 / 11,169** | 部位名列表，仅 5 种组合：`['pendant']` 392、`['face']` 154、`['hat','face']` 112、`['hat']` 97、`['hat','bag']` 7 |
| fashion_data | `hide_part` | **1 / 11,169** | 单值 `[1]`（367333 军刀雅典娜-套装；1 = hat） |
| fashion_data | `hide_in_bag` | 11,169（全 True） | 0x03 恒真，无区分度 |
| fashion_data | `not_show_rebirth_makeup` | 63 | True |
| fashion_data | `mutex_modules` | 349 | 组 id 列表，长度 2(238) / 3(105) / 1(6) |
| **player_appear_data** | `hide_head` | **163** | True |
| player_appear_data | `hide_face` | **125** | True |
| player_appear_data | `hide_pendant` | **117** | True |
| player_appear_data | `hide_bag` | **6** | True |
| player_appear_data | `takeoff_head` | **6** | True（暗夜行者/星象迷影/军刀雅典娜/时光童话，3 款×男女） |
| player_appear_data | `mutex_modules` | 310 | 组 id 列表 |
| player_appear_data | `not_show_rebirth_makeup` | 46 | True |
| player_module_appear_data | `hide_in_bag` | 1,200（全 True） | 无区分度 |

**`hide_part` vs `hide_other_part` vs `hide_*` 是否同一件事**

- `hide_part` 与 `hide_other_part` 是同一件事的两种表达：前者用**部位编号**（仅 1 行，`[1]=hat`），后者用**部位名字符串**（762 行）。
- `hide_other_part` 与 `hide_head/hide_face/hide_pendant/hide_bag` 的隐式映射为 `hat→hide_head`、`face→hide_face`、`pendant→hide_pendant`、`bag→hide_bag`。逐条交叉验证：762 行 × 4 部位 = **3,048 次判定，0 冲突**（881 组"声明且为真"、2,167 组"未声明且为假"）。
- 但**集合层面不等价**：`fashion` 声明涉及 appear 行 vs `appear` 实际为 True 的行：

| 部位 | fashion 声明涉及的 appear 行 | appear 实际 True | 交集 | 仅 fashion | 仅 appear |
|---|---|---|---|---|---|
| 头 | 62 | 163 | 61 | 1 | **102** |
| 面 | 76 | 125 | 76 | 0 | **49** |
| 挂饰 | 112 | 117 | 112 | 0 | **5** |
| 包 | 2 | 6 | 2 | 0 | **4** |

**结论**：映射一致、无矛盾，但 `player_appear_data` 是**运行期真值且更全**（多 102 遮头 / 49 遮脸 / 5 遮挂饰 / 4 遮包，多为 30 条不被任何时装行引用的 appear 行）。

**完整清单规模**

| 部位 | fashion 行级 | 去时效后款式数 | appear 行级 |
|---|---|---|---|
| 遮头（hat / hide_head） | 216 | **28** | 163 |
| 遮面（face / hide_face） | 266 | **37** | 125 |
| 遮挂饰（pendant / hide_pendant） | 392 | **53** | 117 |
| 遮包（bag / hide_bag） | 7 | **1** | 6 |

**独立互斥/隐藏规则表**：**不存在**。全表扫 `mutex|hide|conflict|exclude|forbid` 命中 19 张表，全部与时装无关（跨服匹配禁用、场景隐藏模型、剧情 NPC 隐藏等）。互斥逻辑靠两个内嵌字段承载：`fashion_data.mutex_modules`（349 行）、`player_appear_data.mutex_modules`（310 行）。

---

## D6 性别与双版

| 字段 | 所在表 | 有值行数 | 取值 | 含义 |
|---|---|---|---|---|
| `gender` | **player_appear_data** | **5,604 全有**（含 None） | 1 = 2,783 / 0 = 1,502 / None = 1,319 | **1 = 男，0 = 女**，None = 老款/无性别 |
| `force_gender` | fashion_data | 84 | 仅 `1` | 84 行（白月魁等…），appear 侧男女都存在，语义未能在配置内证实 |
| `force_gender` | player_appear_data | 27 | 仅 `1` | 同上 |
| `uncap_appear_gender` | fashion_data | 133 | 1=21 / 2=35 / 3=77 | 出现在 suit / hat |
| `female_name` / `man_name` | fashion_data | 21 / 22 | 字符串 | 分版命名 |
| `female_desc` / `man_desc` | fashion_data | 21 / 33 | 字符串 | 分版描述（见 D2） |
| `gender_scope` | **无此字段**（全表无） | — | — | 板上的 `gender_scope` 是派生值，非表字段 |

**`gender` 语义的三重交叉验证（1 = 男）**

1. `gender=1` 且 `model_name` 含 `f_m_` → 2,327 行；`gender=0` 且含 `f_f_` → 1,221 行，反向为 0。
2. 21 行有 `man_name`+`female_name` 的时装（如 469060 EVA）：`appear_ids = [3327401(女, suit_f_…), 13327401(男, suit_m_…)]`，其 gender 分别为 0 / 1，且 `female_name` 对应前者、`man_name` 对应后者。
3. `appear_ids` 两元素 gender 组合：`(0,1)` 9,121、`(None,1)` 1,631、`(0,None)` 417 —— 即 **`appear_ids` 固定为 [女, 男]**；1,631 行的女版 appear 行存在但未标 `gender`；417 行男版 id 在 appear 表中查无此行（与"417 行缺失"已知事实一致）。两元素都能命中 appear 行的 10,752 行，其余 417 行仅女版可命中。

---

## D7 其他"小参"

| 字段 | 所在表 | 有值行数 | 取值范围 / 分布 | 对图鉴的价值 |
|---|---|---|---|---|
| `model_scale` | appear only | 70 / 5,604 | 7 档（1.0 / 0.9 / 0.8 / 0.7 …） | 低，仅展示缩放 |
| `back_weapon_vis` | fashion 399 / appear 114 | 3.6% / 2.0% | 恒 True | 中，标注"背后武器可见"，可做标签 |
| `point_light_id` | fashion 896 / appear 466 | 8.0% / 8.3% | 1~7，7 档 | 低，光源预设 |
| `reborn_vis` | fashion 1,121 / appear 425 | 10.0% / 7.6% | 恒 True | 中，再生外观可见 |
| `fly_light` | **无此字段** | — | — | — |
| `flowing_light_group_id` | fashion 14 / appear 4 | 0.1% | 恒 3310 | 低 |
| `special_idle_anims` | appear 850 | 15.2% | 4 种，主流 `idle_show_01 / idle_show_shoot_01` | 中，展示动作 |
| `special_idle_anims2` | fashion 800 / appear 245 | 7.2% / 4.4% | 54 种 `bq_*_idle_01` | 中，同上 |
| `fashion_action_id` | fashion 3,829 / appear 887 | 34.3% / 15.8% | 590 / 316 种 | 高，站姿动作，可做展示 |
| `anim_graph_id` | fashion 481 / appear 104 | 4.3% / 1.9% | 39 种（`156;154` 这类组合串） | 中 |
| `need_idle_hide_main_weapon` | appear 122 | 2.2% | 恒 1 | 低 |
| `is_slim_bag` | fashion 6,563(空组) / appear 2,172 | 58.8% / 38.8% | fashion 全为空元组，appear 有 297 行 `1` | 低（主表字段为空壳，真值在 appear） |
| `max_stack_num` | fashion 11,169 | 100% | 恒 2147483647 | 无价值 |
| `sort_key` | fashion 11,168 / appear 2,925 / module 1,174 | 100% | 1/2/4/5 共 5 档 | 高，图鉴排序依据 |
| `level` | fashion 11,169 / appear 2,925 / module 1,200 | 100% | 1~7（4 占 9,054） | 高，品级 |
| `valid_days` | fashion 8,912 / module 1,031 | 79.8% / 85.9% | 1/3/5/7/14/30/… 9 档 | 高，时效 |
| `theme_codes` | fashion 168 / appear 23 | 1.5% | 恒 `('yh',)` | 低 |
| `brand_id` | fashion 2,608 / appear 750 | 23.4% | 1~5 | 高，品牌归属 |
| `bg_ids` | fashion 233 / appear 70 | 2.1% | 26 种，单值 | 中，背景图 |
| `suit_buff_id` | fashion 320 / appear 94 | 2.9% | 36 种，多为 2 元组 | 中，套装 buff |
| `preview_id` | fashion 621 / appear 186 | 5.6% | 32 种 | 低 |
| `fashion_preview` | fashion 9,142 / module 1,174 | 81.9% / 97.8% | 恒 True | 中（无区分度） |
| `new_fashion_id_str` | fashion 1,631 | 14.6% | 1,574 种，如 `bag_3050_1_0` | **高**，部位代码权威（cloth/hat/bag/light/suit） |
| `show_name` | fashion 8,176 / module 1,006 | 73.2% | 1,153 / 168 种 | 高，展示名（含"典藏"等） |
| `value_word_ids` | fashion 412 / appear 102 | 3.7% | 28 种 id 组合 | 中，卖点词条 |
| `valid_scene_ids` | fashion 4 | 0.0% | 恒 `(280,)` | 无 |
| `is_2025` / `is_climb_tower` | fashion 122 / 929 | 1.1% / 8.3% | 恒 True | 中，活动标签 |

---

## 8. 现有板（`fashion_wardrobe.json`，3,152 卡）覆盖度

板已将 11,169 行聚合成 3,152 卡（`row_keys` 命中 **11,159 行，缺 10 行**），行维度近乎全量；**缺口在字段维度**。

| 维度 | 源行数 | 涉及卡 | 板上字段 | 板上实有 | 缺口 |
|---|---|---|---|---|---|
| D1 图标 | 11,169 | 2,235 | `icons_all` / `icon_count` / `icon_state` | 2,423 卡 | **161 卡有源图标但无 icons_all**；另 281 卡标"无独立图标"、309 卡"缺图" |
| D2 描述 | 11,041 | 2,205 | `desc` | 2,423 卡 | **149 卡缺 desc** |
| D3 魅力 | 9,232 | 1,953 | `charm_value` | 2,025 卡 | **152 卡缺 charm_value** |
| D4 藏花 | 63（5 款式） | 5 | **无此字段** | 0 | **100% 缺失**（5 卡） |
| D5 隐藏 | 762 | 102 | `hide_parts` | 98 卡 | 4 卡 |
| D6 性别 | 5,604 appear | — | `gender`（女/男/仅女款…） | 2,576 卡 | 576 卡 gender 为空 |
| D2 男女分版描述 | 21+33 行 | 17 | **无此字段** | 0 | **100% 缺失**（17 卡） |

板已有的图标性别标注：`icons_all` 条目 gender 分布 女 1,750 / 男 1,749 / None 922 / '' 42 —— 说明"2 条图标 = 女+男"的口径已被板采用。

---

## 9. 权威来源结论（建全量索引的取数口径）

| 维度 | 权威表.字段 | 覆盖率 |
|---|---|---|
| D1 图标 | `fashion_data.icons`（[女,男] 2 条） | 11,169 / 11,169 = 100% |
| D2 描述 | `fashion_data.desc`（女/通用）+ `man_desc`（男覆盖） | 98.9%（另 33 行男版） |
| D3 魅力 | `fashion_data.charm_value`（与 appear 100% 同值） | 9,232 / 11,169 = 82.7% |
| D4 藏花 | `fashion_data.replace_flower_path`（模型）+ `player_appear_data.replace_flower_id`（部件行） | 63 行 / 5 款式 |
| D5 隐藏 | `player_appear_data.hide_head/hide_face/hide_pendant/hide_bag`（运行期真值，更全）；`fashion_data.hide_other_part` 为声明值 | 163/125/117/6 |
| D6 性别 | `player_appear_data.gender`（1=男，0=女）+ `fashion_data.female_name/man_name` | 4,285 有标记（76.5%） |
| D7 小参 | `fashion_data.new_fashion_id_str / sort_key / level / valid_days / brand_id` | 14.6% / 100% / 100% / 79.8% / 23.4% |

## 10. 解码失败清单（跳过，未中断）

| 表 | 原因 |
|---|---|
| `desc_info_data_kj1` | body 长度 0，无数据 |
| `desc_info_data_yk` | body 长度 0，无数据 |
| `fashion_charm_version_data` | body 长度 0，无数据 |
| `appear_id_2_fashion_id` / `new_appear_id_2_appear_id` | 非 `x{` 容器格式（marshal 风格），本解码器不支持；影响可忽略，反向映射可由 `fashion_data.appear_ids` 自建 |
| `simple_fashion_data.icons` | 9,321 行 jump 偏移取不到组，展开为空 → 不作为图标源 |
