# 时装 / 外观域 反向引用扫描报告

> 数据源：`01_索引与产物/41_还原树/pe/配置/com/cdata/`（还原树内已解码表；未触碰线上客户端 npk）。
> 脚本：`90_临时/_ref_scan.py`（全表扫描）→ `_verify.py`（候选复核）→ `_report.py`（本报告）。
> 缓存：`90_临时/ref_scan_cache.jsonl`（逐表原始结果，可断点续跑）、`ref_scan_verify.json`、`ref_scan_agg.json`。

---

## 0. 口径与覆盖率

- 目录内基础表 **12451** 张（不含 `_chs`）。
- 成功解码 **9808** 张，legacy 0x73 + `lenient=True`，共 **1,900,163** 行。
- 失败 **2643** 张，逐表记录原因，**不参与任何统计、不用占位值**：

| 失败原因 | 表数 |
|---|---|
| 表体缺失（.py 只剩字节码壳，无 x{ 容器） | 1952 |
| 文本池不可解（_chs 为空族 / 格式不符） | 499 |
| 索引尾不是 0x76 族 | 128 |
| 表头 reserved != 0 | 43 |
| ULEB 截断 | 16 |
| 索引桶计数异常 | 3 |
| 未知值标记 0x11 | 2 |

**值域提取**：`0x01` 字面整数；`0x03` 布尔（丢弃）；`0x05` 文本池字符串（仅纯 ASCII 十进制串转 int）；
`0x0b` `jump:<off>` 用 `BT.read_27_group` 展开，按 kind 递归（`0x0b` 子组偏移继续、`0x01` 元素是字面 id、`0x05` 元素是池索引）。
列表字段把**所有元素**摊平进字段值域。

**题目口径**：字段去重值中命中数 `hit ≥ 5` 且 `hit / 去重值数 ≥ 30%`。

**追加的碰撞检验**（因为 Q3 的目标集合只有 403 个值却铺在 83~1054，密集度 41%，任何小整数都会“命中”）：
对每个候选算随机基线 `base = |目标集合 ∩ [候选值域]| / 区间宽度`，`lift = 命中率 / base`，分三层：

- **确认**：命中率 ≥ 95%（≥5 个去重值里几乎全部是合法 id —— 在 6~9 位 id 空间里，这靠巧合做不到）
- **可能**：命中率 30%~95% 且 `lift ≥ 5`（混合命名空间，但明显高于随机密度）
- **碰撞**：命中率 30%~95% 且 `lift < 5`（没有超过随机密度，判为命名空间巧合）

注意：`lift` **不能**用作 100% 命中字段的判据——时装主键在 `166000~166999`、`460xxx~479xxx` 这类块里是**连续**的，
块内随机密度本身就接近 100%，真引用的 lift 反而只有 1~3。所以 95% 以上走“全命中”判据，中段才用 lift。

| 目标 | 来源 | 规模 |
|---|---|---|
| F | `fashion_data` 行键 | 11,169（166000 ~ 650040136） |
| A | `player_appear_data` 行键 | 5,604（10000 ~ 1430450303） |
| M | `player_module_appear_data` 行键 | 1,200（260000 ~ 741770124） |
| FID | `fashion_data_for_export.fashion_id` 去重 | 403（来自 1178 行，83 ~ 1054） |

---

## Q1 谁引用了 `fashion_data` 的行键

过阈值 **(表,字段) = 51**：确认 **21** / 可能 **28** / 碰撞 **2**。

### 确认引用（21 条，值域几乎全是合法行键）

| # | 表 | 字段 | 命中/去重 | 命中率 | 表行数 | lift |
|---|---|---|---|---|---|---|
| 1 | `fashion_preset_do_face_config_data` | `unlock_keys` | 37/38 | 97% | 29 | 68053.08 |
| 2 | `fashion_store_current_data` | `item_id` | 202/202 | 100% | 404 | 58434.32 |
| 3 | `fashion_store_data` | `item_id` | 721/722 | 100% | 1437 | 58136.17 |
| 4 | `fashion_obtain_handbook_data` | `fashion_ids` | 861/867 | 99% | 392 | 57813.91 |
| 5 | `fashion_free_set_data` | `fashion_black_list` | 233/245 | 95% | 2 | 55719.72 |
| 6 | `store_user_portrait_data` | `exclude_fashions` | 13/13 | 100% | 382 | 465.68 |
| 7 | `yk_month_card_item_data` | `item_ids` | 199/208 | 96% | 118 | 88.87 |
| 8 | `optional_gift_data` | `pre_item_ids` | 76/77 | 99% | 46 | 36.3 |
| 9 | `wish_fashion_reward_data` | `item_ids` | 49/49 | 100% | 29 | 34.23 |
| 10 | `store_user_portrait_data` | `unlock_fashion_ids` | 60/60 | 100% | 382 | 32.53 |
| 11 | `store_daily_recommended_fashion_data` | `fashion_id` | 223/223 | 100% | 272 | 31.22 |
| 12 | `record_label_suit_ui_data` | `suit_item_id` | 10/10 | 100% | 10 | 3.1 |
| 13 | `record_label_data` | `suit_ids` | 28/28 | 100% | 5 | 3.0 |
| 14 | `team_battle_pass_conf` | `fashion_ids` | 9/9 | 100% | 3 | 2.68 |
| 15 | `player_appear_race_ctrl_data` | `unlock_fashion` | 5/5 | 100% | 10 | 2.49 |
| 16 | `record_label_brand_hd_label_conf` | `free_fashion_whitelist` | 110/110 | 100% | 5 | 2.34 |
| 17 | `fashion_recommend_data` | `item_ids` | 110/110 | 100% | 32 | 2.33 |
| 18 | `record_label_suit_data` | `suit_item_id` | 42/42 | 100% | 42 | 2.32 |
| 19 | `saint_beast_conf_data` | `fashion_id` | 7/7 | 100% | 4 | 1.76 |
| 20 | `call_up_fashion_data` | `real_item_id` | 50/50 | 100% | 50 | 1.02 |
| 21 | `fashion_card_sale_price_data` | `fashion` | 14/14 | 100% | 8 | 1.01 |

**结论**：`fashion_data` 行键被 **20 张表 / 21 个字段** 直接当“商品 id”引用。
三个入口族：① 商店/商城 `fashion_store_data.item_id`(721/722)、`fashion_store_current_data.item_id`(202/202)、`store_data.item_id`(898/1112)；
② 图鉴/收集 `fashion_obtain_handbook_data.fashion_ids`(861/867)、`fashion_free_set_data.fashion_black_list`(233/245)；
③ 奖励投放 `yk_month_card_item_data.item_ids`、`optional_gift_data.pre_item_ids`、`wish_fashion_reward_data.item_ids`、`huodong_reward_data.preview_fashion_ids`。
另有 4 个“标签/图鉴”族：`record_label_suit_data.suit_item_id`(42/42)、`record_label_data.suit_ids`(28/28)、
`record_label_brand_hd_label_conf.free_fashion_whitelist`(110/110)、`fashion_recommend_data.item_ids`(110/110)。
这 21 条的取值下界最低为 1（全部落在 366xxx / 46xxxx / 47xxxx 等时装专属段），没有小整数混入。

**抽样复核**（证明这些不是解析巧合）：`fashion_store_data.item_id` 去重 722 个值，721 命中，取值是连续的 `166000,166001,166002…`；
唯一未命中的 `650040110` 落在时装键段 `6500401xx` 内部（该段实际存在 650040130~650040136），属于**表内悬空引用**，
而不是解码错位。同理 `express_action_data.fashion_action_appear_id` 1176 个值命中 1168 个，取值 `30320,30380,30381…` 连续成段。

### 可能引用（混合命名空间，共 28 条，列前 20）

| 表 | 字段 | 命中/去重 | 命中率 | 表行数 | lift |
|---|---|---|---|---|---|
| `climb_tower_rank_data_v2` | `last_season_glowstick` | 7/8 | 88% | 10 | 52310.95 |
| `du_3_climb_tower_rank_data_v2` | `glowstick` | 7/8 | 88% | 10 | 52061.88 |
| `climb_tower_rank_data_v2` | `glowstick` | 7/8 | 88% | 10 | 51780.85 |
| `optional_reward_info_data` | `show_item_ids` | 48/57 | 84% | 343 | 50596.99 |
| `random_item_reward_data_922` | `items` | 551/1140 | 48% | 980 | 28851.09 |
| `random_item_reward_data_923` | `items` | 374/807 | 46% | 514 | 26980.28 |
| `fashion_collect_point_data` | `item_ids` | 53/133 | 40% | 111 | 23186.71 |
| `refresh_box_366` | `id` | 22/33 | 67% | 33 | 396.87 |
| `hd_draw_card_rewards` | `pre_fashion` | 10/11 | 91% | 1010 | 233.09 |
| `four_leaf_caring_gift_item_data` | `item_id` | 23/32 | 72% | 55 | 156.76 |
| `simple_optional_gift_data` | `pre_item` | 9/13 | 69% | 1955 | 106.41 |
| `store_data` | `item_id` | 898/1112 | 81% | 1431 | 62.3 |
| `super_fashion_lottery_conf_data` | `left_item_id` | 21/35 | 60% | 235 | 55.74 |
| `refresh_simple_object_366` | `id` | 8/9 | 89% | 9 | 47.29 |
| `du_1_climb_tower_rank_data_v2` | `glowstick` | 7/8 | 88% | 10 | 40.97 |
| `du_2_climb_tower_rank_data_v2` | `last_season_glowstick` | 7/8 | 88% | 10 | 40.97 |
| `du_2_climb_tower_rank_data_v2` | `glowstick` | 7/8 | 88% | 10 | 40.68 |
| `du_3_climb_tower_rank_data_v2` | `last_season_glowstick` | 7/8 | 88% | 10 | 40.68 |
| `optional_gift_data` | `item_ids` | 76/102 | 75% | 46 | 27.4 |
| `wish_store_data` | `repeat_check_items` | 200/230 | 87% | 3156 | 26.96 |

性质一致：字段是跨品类 id 容器（商店货架、礼包、抽奖奖池、爬塔排名烟花、随机奖励池），时装只占其中一类。

### 碰撞（2 条，阈值过但无判别力）

| 表 | 字段 | 命中/去重 | 命中率 | 表行数 | lift |
|---|---|---|---|---|---|
| `distortion_infect_monster_data_2350` | `id` | 36/82 | 44% | 410 | 1.03 |
| `monster_data_470` | `id` | 97/259 | 37% | 259 | 0.96 |

这些命中率虽过 30%，但 `lift < 5`：所在数值窗口本身很密（如 `monster_data_470.id` 的 id 段压在 166xxx 上），
命中率没有超过随机密度，判定为**命名空间巧合**，不算引用。

## Q2 谁引用了 `player_appear_data` / `player_module_appear_data` 的行键

过阈值：`player_appear_data` **180**（确认 35 / 可能 88 / 碰撞 57）；`player_module_appear_data` **4**（确认 0 / 可能 2 / 碰撞 2）。

### A. `player_appear_data` 确认引用（35 条）

| # | 表 | 字段 | 命中/去重 | 命中率 | 表行数 | lift |
|---|---|---|---|---|---|---|
| 1 | `express_action_data` | `fashion_action_appear_id` | 1168/1176 | 99% | 816 | 259292.0 |
| 2 | `fashion_data` | `appear_ids` | 4478/4538 | 99% | 11169 | 252916.57 |
| 3 | `fashion_data_for_export` | `appear_ids` | 4318/4378 | 99% | 10988 | 252792.72 |
| 4 | `simple_fashion_data` | `appear_ids` | 1817/1820 | 100% | 11169 | 239285.88 |
| 5 | `dungeon_extra_reward_hd_data` | `team_mbs_appear_id` | 8/8 | 100% | 1 | 7728.21 |
| 6 | `fashion_recommend_data` | `appear_ids` | 232/232 | 100% | 32 | 6355.15 |
| 7 | `simple_fashion_replace_appear_conf` | `male_appears` | 7/7 | 100% | 3 | 4481.92 |
| 8 | `do_face_v4_preset_data` | `fashion_id` | 19/19 | 100% | 21 | 3531.94 |
| 9 | `do_face_v4_preview_data` | `fashion_id` | 18/18 | 100% | 48 | 3531.94 |
| 10 | `player_appear_data` | `uncap_app_id_new` | 76/76 | 100% | 5604 | 2978.54 |
| 11 | `do_face_v4_preset_data` | `hair_id` | 13/13 | 100% | 21 | 2923.28 |
| 12 | `do_face_v4_preview_data` | `hair_id` | 18/18 | 100% | 48 | 2880.76 |
| 13 | `simple_fashion_replace_appear_conf` | `female_appears` | 7/7 | 100% | 3 | 1118.79 |
| 14 | `sub_do_face_ui_v4_data` | `hair_appear_id` | 42/42 | 100% | 1008 | 74.2 |
| 15 | `do_face_config_data` | `hair_appear_id` | 8/8 | 100% | 606 | 74.16 |
| 16 | `player_appear_data` | `replace_flower_id` | 10/10 | 100% | 5604 | 73.59 |
| 17 | `player_appear_race_ctrl_data` | `appear_ids` | 20/20 | 100% | 10 | 73.48 |
| 18 | `player_appear_recommend_data` | `appears` | 18/18 | 100% | 6 | 70.61 |
| 19 | `village_appear_building_statue_component_data` | `model_id` | 8/8 | 100% | 26 | 69.66 |
| 20 | `do_face_config_v2_data` | `hair_appear_id` | 19/19 | 100% | 1545 | 65.62 |
| 21 | `sub_do_face_ui_data` | `hair_appear_id` | 25/25 | 100% | 545 | 62.26 |
| 22 | `npc_dedicated_index_data` | `appears` | 22/22 | 100% | 45 | 57.08 |
| 23 | `do_face_config_v2_data` | `fashion` | 28/29 | 97% | 1545 | 57.01 |
| 24 | `sub_do_face_ui_data` | `fashion` | 22/23 | 96% | 545 | 56.48 |
| 25 | `player_appear_data` | `uncap_app_id` | 10/10 | 100% | 5604 | 56.01 |
| 26 | `player_appear_data` | `suit_app_id` | 10/10 | 100% | 5604 | 55.76 |
| 27 | `refresh_entities_43` | `monster_id` | 21/22 | 95% | 22 | 53.14 |
| 28 | `mission_step_data_28` | `id` | 7/7 | 100% | 196 | 2.67 |
| 29 | `mission_step_data_8` | `id` | 19/19 | 100% | 51 | 1.54 |
| 30 | `evolute_equip_conf_data` | `deform_hurt_effect` | 13/13 | 100% | 84 | 1.0 |
| 31 | `survival_manual_chapter_data_c` | `include_missions` | 11/11 | 100% | 3 | 1.0 |
| 32 | `player_appear_race_ctrl_data` | `female_app_id` | 10/10 | 100% | 10 | 1.0 |
| 33 | `player_appear_race_ctrl_data` | `male_app_id` | 10/10 | 100% | 10 | 1.0 |
| 34 | `refresh_defence_buildings_26` | `block_refresh_id` | 6/6 | 100% | 468 | 1.0 |
| 35 | `ship_weapon_data` | `weapon_ids` | 6/6 | 100% | 2 | 1.0 |

可信度分层：28 条来自表名本身就属于外观/捏脸体系的表（`*appear*` / `*fashion*` / `*do_face*`），语义与值域互相印证；
7 条表名和字段名都不带外观语义，但值域"整段落进" appear 的 id 段，**需人工再确认**，本报告只登记不下结论：

`refresh_entities_43.monster_id(vmin=10567)`、`mission_step_data_28.id(vmin=140010)`、`mission_step_data_8.id(vmin=40010)`、`evolute_equip_conf_data.deform_hurt_effect(vmin=50026)`、`survival_manual_chapter_data_c.include_missions(vmin=50101)`、`refresh_defence_buildings_26.block_refresh_id(vmin=31000)`、`ship_weapon_data.weapon_ids(vmin=10601)`

**结论**：资源层入口收敛在四个族——
① `appear_ids`（`fashion_data` 4478/4538、`fashion_data_for_export` 4318/4378、`simple_fashion_data` 1817/1820，均 99~100%）；
② 动作/表情 `express_action_data.fashion_action_appear_id`（1168/1176）；
③ 捏脸/发型 `*_do_face_*.hair_appear_id`、`do_face_v4_*.fashion_id`；
④ 自指 `player_appear_data.uncap_app_id_new / replace_flower_id / suit_app_id`（uncap 变体指向本体行键）。

注意：三张 fashion 表的 `appear_ids` **不是同一份数据**（去重值 4538 / 4378 / 1820），是不同粒度的视图，不能互相替代。

### B. `player_appear_data` 可能引用（88 条，列前 20）

| 表 | 字段 | 命中/去重 | 命中率 | 表行数 | lift |
|---|---|---|---|---|---|
| `simple_fashion_data` | `icons` | 10/16 | 62% | 11169 | 285840.42 |
| `fashion_sale_rebate_conf_data` | `fashion_ids` | 16/18 | 89% | 9 | 6243.95 |
| `refresh_defence_buildings_55` | `id` | 126/325 | 39% | 325 | 5380.81 |
| `refresh_defence_buildings_35` | `id` | 70/197 | 36% | 197 | 4864.08 |
| `furniture_preview_conf` | `player_appears` | 34/36 | 94% | 1966 | 2728.1 |
| `mission_step_data_15628` | `npc_id` | 10/13 | 77% | 262 | 2219.7 |
| `double_mission_hd_mission_data` | `single_mission_param` | 267/354 | 75% | 4307 | 2151.15 |
| `double_mission_hd_mission_data` | `double_mission_param` | 267/356 | 75% | 4307 | 2139.06 |
| `refresh_entities_133` | `npc_id` | 5/12 | 42% | 656 | 1201.64 |
| `village_boss_monster_attrs_data` | `monster_id` | 10/18 | 56% | 714 | 1169.18 |
| `scout_tower_area_data` | `monster_record_id` | 5/12 | 42% | 165 | 203.29 |
| `du_1_climb_tower_exchange_data` | `item_id` | 5/16 | 31% | 26 | 114.99 |
| `du_2_climb_tower_exchange_data` | `item_id` | 5/16 | 31% | 26 | 114.99 |
| `du_3_climb_tower_exchange_data` | `item_id` | 5/16 | 31% | 26 | 114.99 |
| `refresh_defence_buildings_58` | `id` | 94/191 | 49% | 191 | 108.39 |
| `refresh_defence_buildings_724` | `id` | 94/191 | 49% | 191 | 108.39 |
| `refresh_entities_692` | `group_id` | 53/153 | 35% | 436 | 94.39 |
| `refresh_entities_756` | `group_id` | 53/153 | 35% | 441 | 94.39 |
| `refresh_entities_757` | `group_id` | 53/153 | 35% | 441 | 94.39 |
| `joint_lottery_reward_data_880` | `item_id` | 5/12 | 42% | 13 | 62.34 |

**结论（Q2 最重要的发现）**：`player_appear_data` 的行键空间**不是单一段**：

| 键区间 | 键数 |
|---|---|
| [0, 100000) | 1328 |
| [100000, 1000000) | 1351 |
| [1000000, 10000000) | 1290 |
| [10000000, ∞) | 1635 |

它从 10000 一直铺到 1430450303（uncap 变体）。于是 `monster_data_*.equip_ids`、`refresh_entities_*.group_id`、
`refresh_defence_buildings_*.id` 这些**怪物/村庄刷新 id 段会与它部分重叠**，产生 30%~50%、lift 10~20 的“半命中”。
这些是**不同系统复用同一数字空间**，不是外观引用；真正可信的是确认级 35 条。

### C. `player_module_appear_data`（模块外观：头饰/面饰/挂饰）

| 表 | 字段 | 命中/去重 | 命中率 | 表行数 | lift | 判定 |
|---|---|---|---|---|---|---|
| `npc_gossips_data` | `mission_hide` | 7/20 | 35% | 2724 | 945.42 | 可能 |
| `yk_season_store_data` | `reward_id` | 5/16 | 31% | 16 | 79.66 | 可能 |
| `mission_step_data_52` | `id` | 8/11 | 73% | 28 | 3.09 | 碰撞 |
| `home_party_modules_data` | `item_id` | 13/18 | 72% | 18 | 2.85 | 碰撞 |

**结论：按行键口径「未找到」引用方。** 4 个候选中 2 个 lift<5（`mission_step_data_52.id`、`home_party_modules_data.item_id`，
值域 260010~260070 与模块键 260xxx 同段，但属不同 id 体系）；2 个 lift≥5 的语义完全无关
（`npc_gossips_data.mission_hide` 是任务隐藏标记、`yk_season_store_data.reward_id` 是赛季商店奖励 id）。
模块外观更可能由“模块 id / `model_socket` 槽位名”间接定位，而不是行键直连。

## Q3 值域命中「时装 id 序号（fashion_id）」的表

映射先落地：`fashion_data_for_export` 10,988 行里**只有 1178 行带 `fashion_id`**，去重 403 个值，范围 83~1054。
样本核对：行键 166000 → fashion_id **180**（与题目一致）。

按 30%/≥5 口径扫全表：**1018** 个 (表,字段) 过阈值——但这几乎是纯噪音，因为：

- 目标集合只有 403 个值却铺在 972 的区间上，**基线密度 41%**；
- 阈值 30% 低于基线，等于“随便一个小整数字段都能过”。

加上 lift 检验后，只有 **4** 个候选 lift ≥ 5，且全部语义不符：

| 表 | 字段 | 命中/去重 | 命中率 | 随机基线 | lift | 命中值样本 |
|---|---|---|---|---|---|---|
| `village_base_conf` | `prosperity_value_add` | 6/7 | 86% | 0.103 | 8.32 | 300, 350, 400, 450, 500, 600 |
| `refresh_defence_buildings_208` | `init_hp` | 6/6 | 100% | 0.126 | 7.97 | 290, 390, 420, 430, 450, 520 |
| `scout_tower_point_data` | `camera_vertical` | 5/6 | 83% | 0.146 | 5.7 | 250, 300, 350, 400, 450 |
| `mission_step_data_16400` | `circle_size` | 6/7 | 86% | 0.170 | 5.05 | 200, 250, 300, 400, 500, 600 |

对照：lift ≈ 1（命中率完全等于随机）的典型噪音样本：

| 表 | 字段 | 命中/去重 | 命中率 | 随机基线 | lift | 命中值样本 |
|---|---|---|---|---|---|---|
| `team_target_data` | `tid` | 18/40 | 45% | 0.379 | 1.19 | 105, 200, 205, 206, 217, 219 |
| `mission_step_data_217600` | `ui_tips_ids` | 5/13 | 38% | 0.323 | 1.19 | 748, 780, 832, 844, 846 |
| `monster_data_580` | `weakness_id` | 5/13 | 38% | 0.322 | 1.19 | 95, 96, 97, 98, 140 |
| `box_data` | `map_icon_id` | 7/20 | 35% | 0.293 | 1.19 | 217, 229, 290, 690, 691, 701 |
| `monster_data_390` | `special_function` | 5/16 | 31% | 0.263 | 1.19 | 84, 88, 94, 371, 390 |
| `double_tutorial_step_data` | `start_mission_step` | 19/39 | 49% | 0.415 | 1.18 | 85, 95, 110, 120, 150, 170 |
| `monster_data_271` | `call_range` | 5/11 | 45% | 0.386 | 1.18 | 150, 200, 300, 800, 1000 |
| `monster_data_331` | `call_range` | 5/11 | 45% | 0.386 | 1.18 | 200, 250, 750, 800, 1000 |
| `monster_data_370` | `call_range` | 5/11 | 45% | 0.386 | 1.18 | 150, 200, 300, 800, 1000 |
| `monster_data_610` | `call_range` | 5/11 | 45% | 0.386 | 1.18 | 150, 200, 300, 350, 1000 |

**结论**：

- **除 `fashion_data_for_export.fashion_id` 自身（定义方，403/403=100%）外，本次可解码的 9808 张表里没有任何字段以「fashion_id 序号」为引用目标。**
- 这是**有证据的排除**，不是没找到：1018 个过阈值候选中 1014 个 lift < 5，剩下 4 个 lift ≥ 5 的全是半径/血量/相机高度/圈大小。
- **命名陷阱**：多个字段名叫 `fashion_id` 却存行键——`store_daily_recommended_fashion_data.fashion_id`（223/223 命中 fashion_data 行键）、
  `do_face_v4_preset_data.fashion_id`（19/19 命中 appear 行键）、`saint_beast_conf_data.fashion_id`（7/7 命中行键）。**字段名不可信，值域才可信。**
- `fashion_id` 只覆盖 1178/10988 行（10.7%），说明这个“序号”是**局部发行编号**，不是全量时装编号体系。
- **反向证据**：1018 个候选里，字段名带 `fashion` / `appear` 的只有 **1** 个（就是定义它的 `fashion_data_for_export.fashion_id` 本身，lift 仅 2.41）。
  也就是说，连“名字最像时装”的字段都不指向序号，序号在当前还原树里没有任何二级引用者。

## Q4 字段名维度（不依赖值域，交叉验证）

匹配规则：字段名按 `_` 切词，任一词元命中 {fashion, appear, dress, outfit, suit, hair, hat, icon, skin}，或整名含 `model_id` / `model_name` 片段。

结果：**819** 个不同字段名，分布在 **1813** 张表。
（若改用宽松子串，会多出 93 个噪音字段名，例如 `chat_id`、`chat_msg`、`be_hated_male`、`condition_disappear_id` —— `chat` 里的 `hat`、`disappear` 里的 `appear`、`hated` 里的 `hat` 都会被误伤。）

按词元归类（同一字段名只归一类，优先级 fashion > appear > icon > model > suit > hair > skin）：

| 词元组 | 字段名数 | 涉及表数 | 说明 |
|---|---|---|---|
| fashion* | 106 | 67 | 真正的时装域字段 |
| appear* | 418 | 310 | 外观指针/怪物外观（`monster_appears` 占大头） |
| icon* | 1584 | 930 | 图标 id / 路径，绝大部分是 UI、地图、称号图标 |
| model_id / model_name | 1434 | 1022 | 模型资源引用（资源层旁路，不走行键） |
| suit* | 23 | 17 | 套装 |
| hair* | 18 | 11 | 发型 |
| skin* | 39 | 23 | 皮肤/肤色 |

| # | 字段名 | 出现表数 | 累计行数 |
|---|---|---|---|
| 1 | `model_name` | 528 | 103,532 |
| 2 | `model_name_prefix` | 409 | 64,422 |
| 3 | `monster_appears` | 226 | 84,611 |
| 4 | `root_model_id` | 226 | 84,611 |
| 5 | `extra_model_names` | 216 | 61,819 |
| 6 | `map_icon_id` | 200 | 59,876 |
| 7 | `icon` | 187 | 106,322 |
| 8 | `icon_path` | 127 | 5,528 |
| 9 | `appears` | 109 | 45,145 |
| 10 | `show_icon_range` | 91 | 28,655 |
| 11 | `head_icon_path` | 91 | 28,556 |
| 12 | `option_icon_type` | 21 | 12,567 |
| 13 | `ignore_corpse_map_icon` | 18 | 5,730 |
| 14 | `icon_file` | 14 | 2,692 |
| 15 | `model_id` | 13 | 41,700 |
| 16 | `fashion_id` | 10 | 11,384 |
| 17 | `ctrl_model_name` | 10 | 5,475 |
| 18 | `map_icon_id_before_drop` | 9 | 6,501 |
| 19 | `token_icon` | 9 | 4,132 |
| 20 | `map_icon_scale` | 9 | 2,410 |
| 21 | `icons` | 8 | 43,239 |
| 22 | `fashion_preview` | 8 | 38,069 |
| 23 | `unstart_icon` | 8 | 8 |
| 24 | `started_icon` | 8 | 8 |
| 25 | `appear_ids` | 7 | 33,379 |
| 26 | `pineal_skin_color` | 7 | 2,966 |
| 27 | `pineal_skin_color_para` | 7 | 2,966 |
| 28 | `tag_icon` | 6 | 243 |
| 29 | `small_icon_path` | 6 | 149 |
| 30 | `tab_icon` | 6 | 84 |
| 31 | `level_icon` | 6 | 35 |
| 32 | `gift_icon` | 5 | 16,201 |
| 33 | `alert_sign_icon` | 5 | 2,789 |
| 34 | `hide_icon_for_diff_sub_space` | 5 | 1,976 |
| 35 | `fashion_name` | 5 | 1,228 |
| 36 | `share_icon` | 5 | 840 |
| 37 | `fashion_ids` | 5 | 419 |
| 38 | `female_appear_ids` | 5 | 363 |
| 39 | `male_appear_ids` | 5 | 363 |
| 40 | `big_icon_path` | 5 | 126 |
| 41 | `icon_pos_list` | 5 | 24 |
| 42 | `fashion_action_id` | 4 | 27,782 |
| 43 | `suit_buff_id` | 4 | 27,782 |
| 44 | `is_forbid_compass_icon` | 4 | 6,909 |
| 45 | `is_fashion` | 4 | 5,464 |
| 46 | `level_1_icon` | 4 | 3,704 |
| 47 | `level_2_icon` | 4 | 3,704 |
| 48 | `level_3_icon` | 4 | 3,704 |
| 49 | `hair_appear_id` | 4 | 3,704 |
| 50 | `player_appears` | 4 | 2,732 |
| 51 | `prop_icon` | 4 | 2,489 |
| 52 | `ui_icon` | 4 | 2,472 |
| 53 | `head_icon_height_offset` | 4 | 1,150 |
| 54 | `floor_big_icon` | 4 | 839 |
| 55 | `share_tip_icon` | 4 | 839 |
| 56 | `effect_icon` | 4 | 69 |
| 57 | `unlock_icon` | 4 | 57 |
| 58 | `division_icon_big` | 4 | 40 |
| 59 | `division_icon_middle` | 4 | 40 |
| 60 | `division_icon_small` | 4 | 40 |

**结论**：

- 名称维度补上了值域扫不到的“语义引用”：`model_name`（528 张表）/`model_name_prefix`（409 张）/`monster_appears`（226 张）。
  这些表只存**模型路径/模型名**，不存 `player_appear_data` 行键，所以 Q1/Q2 一条都扫不到。
- 图标是**分散**的：`icon`（187 张）/ `icon_path`（127 张）/ `icons`（8 张）/ `female_icon`（3 张）。
  “图标 id”和“图标路径字符串”两套并存，**没有任何“图标主表”被行键引用**（Q1/Q2 里没有图标表）。
  但要留意：1584 个 icon 字段横跨 930 张表，绝大多数是地图/称号/UI 图标，**只有 `icons` 这一支属于时装域**。
- 时装域真正的字段级指针只有三个：`appear_ids`（7 张表）、`fashion_ids`（5 张）、`hair_appear_id`（4 张）——与 Q1/Q2 的确认级结果吻合，构成交叉验证。

## Q5 有没有一张能覆盖这些散表的最大最全表？

### 主干表被引用次数（合计 / 确认 / 可能；引用方不含自身）

| 目标表 | 合计 | 其中确认 | 其中可能 |
|---|---|---|---|
| `fashion_data` | 49 | 21 | 28 |
| `player_appear_data` | 119 | 35 | 88 |
| `player_module_appear_data` | 2 | 0 | 2 |
| `fashion_data_for_export` | 1 | 0 | 0 |
| `simple_fashion_data` | 2 | 0 | 0 |

### 域内表清单（表名含 fashion/appear/dress/outfit/suit/hair，按行数排序）

| # | 表 | 行数 | 引用主干(F/A/M)的字段数 | 字段数 |
|---|---|---|---|---|
| 1 | `simple_fashion_data` | 11,169 | 2 | 10 |
| 2 | `fashion_data` | 11,169 | 1 | 100 |
| 3 | `fashion_data_for_export` | 10,988 | 1 | 101 |
| 4 | `player_appear_data` | 5,604 | 4 | 121 |
| 5 | `fashion_review_score_data` | 1,526 | 0 | 1 |
| 6 | `fashion_store_data` | 1,437 | 1 | 34 |
| 7 | `pet_appear_data` | 1,319 | 0 | 9 |
| 8 | `player_module_appear_data` | 1,200 | 0 | 22 |
| 9 | `player_module_appear_data_for_export` | 1,200 | 0 | 22 |
| 10 | `fashion_obtain_res_data` | 1,161 | 0 | 2 |
| 11 | `humanoid_monster_appear_data` | 956 | 0 | 8 |
| 12 | `bobj_chair_data` | 800 | 0 | 13 |
| 13 | `appear_change_color_auto_export_data` | 736 | 0 | 7 |
| 14 | `appear_change_color_data` | 705 | 0 | 6 |
| 15 | `fashion_charm_magazine_ugc_video_data` | 654 | 0 | 15 |
| 16 | `fashion_model_change_color_data` | 623 | 0 | 25 |
| 17 | `fashion_charm_magazine_ugc_photo_data` | 567 | 0 | 11 |
| 18 | `fashion_fake_data` | 533 | 0 | 6 |
| 19 | `fashion_lottery_data` | 448 | 0 | 20 |
| 20 | `new_player_appear_data_auto` | 447 | 0 | 1 |
| 21 | `fashion_store_current_data` | 404 | 1 | 26 |
| 22 | `fashion_obtain_handbook_data` | 392 | 1 | 21 |
| 23 | `fashion_preset_do_face_makeup_data` | 331 | 0 | 4 |
| 24 | `fashion_charm_magazine_page_data` | 323 | 0 | 14 |
| 25 | `player_appear_v2_bag_data` | 296 | 0 | 27 |
| 26 | `store_daily_recommended_fashion_data` | 272 | 1 | 16 |
| 27 | `npc_appear_data` | 269 | 0 | 5 |
| 28 | `super_fashion_lottery_conf_data` | 235 | 1 | 60 |
| 29 | `fashion_charm_magazine_designer_data` | 204 | 0 | 2 |
| 30 | `super_fashion_share_data` | 167 | 0 | 0 |

（域内共 189 张，完整清单见缓存；此处列前 30。）

### 能力矩阵（按真实字段名判定）

| 能力 | fashion_data | fashion_data_for_export | simple_fashion_data | player_appear_data | player_module_appear_data |
|---|---|---|---|---|---|
| 商品名 name / show_name | Y | Y | Y | Y | Y |
| 描述 desc | Y | Y | Y | Y | Y |
| 图标 icon / icons | Y | Y | Y | — | Y |
| 部位 part / part_type | Y | Y | Y | Y | Y |
| 魅力值 charm_value | Y | Y | — | Y | Y |
| 资源指针 appear_ids | Y | Y | Y | — | — |
| 模型名 model_name | — | — | — | Y | — |
| 模型 id model_id | Y | Y | Y | Y | Y |
| 模型路径 model_paths / v2_socket_model_path | Y | Y | — | Y | Y |
| 部位隐藏 hide_head / hide_face | — | — | — | Y | — |

### 结论：**不存在单表覆盖**

证据：

1. **行数**：域内最大行数就是 **11,169**，由 `simple_fashion_data`、`fashion_data` 并列（`simple_fashion_data` 只是 `fashion_data` 的 10 字段瘦身视图）。
   没有任何时装域表超过它。全库行数前十为：`weapon_sound_data_for_query`(34,923)、`mission_step_event_data`(26,653)、`buff_data`(18,722)、`new_mission_talk_content_data`(18,471)、`huodong_reward_data`(16,116)、`vision_refresh_resources_132`(14,518)、`vision_refresh_resources_7`(13,724)、`vision_refresh_resources_381`(13,244)、`new_pve_monster_attr_conf`(13,166)、`vision_refresh_resources_20020`(12,511)，
   其中没有一张属于时装域——**不存在隐藏的大一统表**。
2. **字段互缺**（见矩阵）：`fashion_data` 有 `icons`/`show_name`/`charm_value`/`appear_ids`，但**没有 `model_name`、没有 `hide_head/hide_face`**；
   `player_appear_data` 有 `model_name`/`high_model_name`/`hide_head`/`hide_face`，但**121 个字段里 0 个图标字段**，也没有商城向的 `show_name`。
   两者不能互相推导：商品层给不出渲染所需的主模型名，资源层给不出商品图标与售价。
3. **`fashion_data_for_export` 是切片不是全集**：行数 10,988 < 11,169（少 181 行），键 10988/10988 全落在 `fashion_data` 内；
   字段上多 `fashion_id`/`fashion_tasting_args`/`is_functional_bag`，少 `hide_part`/`new_fashion_id_str`；
   **`is_available_glowstick` 两张表都有**（题目里“少 is_available_glowstick”的说法不成立，实测共有）。
4. **`simple_fashion_data` 是瘦身视图**：同为 11,169 行 / 11169 键重叠，但只有 10 个字段（`name/desc/part/valid_days/icons/model_id/model_change_color_id/appear_ids/new_fashion_id_str/change_color_id`），
   没有 `show_name`、`charm_value`、`sort_key`、`max_stack_num`。

### 真实结构：主干 + 三区

```
商品层主干  fashion_data (11169 行 / 100 字段)
            ├─ 商品属性: name, show_name, desc, icons, charm_value, valid_days, level, part, part_type, sort_key
            ├─ 资源指针: appear_ids ─────┐ (0x0b jump 组, kind 0x01 = 字面 id)
            └─ 导出切片: fashion_data_for_export (10988 行, +fashion_id 序号, 覆盖 1178 行)
                                      │
资源层      player_appear_data (5604 行 / 121 字段) ←┘
            主模型 model_name / high_model_name / oversea_*, 部位 part, hide_head / hide_face / hide_pendant, socket_*
                                      │
模块层      player_module_appear_data (1200 行 / 22 字段)  ← 独立，按行键无人引用
            头饰/面饰/挂饰; icon + female_icon + desc (自带图标和文案)
```

### 缺失信息只能从哪张表补

- **商品图标**：只有 `fashion_data.icons`（及其切片 `for_export` / `simple_fashion_data`）。`player_appear_data` 无任何图标字段，
  所以“外观长什么样”在资源层查不到，必须回商品层；模块图标则只有 `player_module_appear_data.icon` / `female_icon`。
- **主模型名**：只有 `player_appear_data`（`model_name`、`high_model_name`、`oversea_model_name`、`new_bone_model_name`…）。
  `fashion_data` 虽带 `model_id` / `v2_socket_model_path` / `socket_models_male|female`，但**没有 `model_name`**，无法直接定位主模型文件。
- **部位隐藏规则**：只有 `player_appear_data`（`hide_head`/`hide_face`/`hide_pendant`）。`fashion_data` 只有商品向的 `hide_part`/`hide_other_part`/`hide_in_bag`，语义不同。
- **序号 fashion_id**：只有 `fashion_data_for_export`，且只覆盖 1178 行；`fashion_data` 内对应的是字符串键 `new_fashion_id_str`（如 `hat_3002_1_0`）。
- **模块外观**：只有 `player_module_appear_data`（1200 行），`fashion_data` 里没有对应条目。

### 已知盲区（解码失败但与本域强相关，未取任何数字）

表名含 fashion/appear/suit/model/skin 的失败表共 **60** 张，列前 40：

| 表 |
|---|
| `appear_id_2_equip_id` |
| `appear_id_2_fashion_id` |
| `appear_id_to_action_id` |
| `appear_trade_ids` |
| `armors_to_appears_data` |
| `art_do_face_default_hair_id_data` |
| `art_do_face_hair_mapping_v4_data` |
| `camp_style_model_tree_scale_data` |
| `cat_appear_data` |
| `change_color_fashion_ids` |
| `coldarm_type_to_skin_item_data` |
| `do_face_default_appears_data` |
| `eu_appear_id_convert_data` |
| `fashion_buff_id_set` |
| `fashion_charm_magazine_time_data` |
| `fashion_charm_period_data` |
| `fashion_charm_shop_goto_data` |
| `fashion_charm_version_data` |
| `fashion_id_2_handbook_id` |
| `fashion_id_2_season_id` |
| `fashion_item_spine_data` |
| `fashion_model_base_2_model_change_color_id` |
| `fashion_model_id_2_plate_id` |
| `fashion_preset_do_face_item_key_data` |
| `fashion_preset_do_face_key_data` |
| `fashion_sfx_buff_id_set` |
| `levin_dungeon_fixed_appear_day` |
| `model_data` |
| `monster_appear_params_to_id_data` |
| `monster_horde_model_data` |
| `new_appear_id_2_appear_id` |
| `nt_super_fashion_gift_data` |
| `nt_super_fashion_gift_index_data` |
| `only_fashion_hd_tag_conf` |
| `opposite_fashion_appear_id_data` |
| `pet_appear_suit_map` |
| `plate_id_2_fashion_ids` |
| `scene_model_break_conf_data` |
| `scene_model_break_export_data` |
| `ship_model_map_with_different_level` |

这些表都落在「表体缺失（字节码壳无 `x{`）」或「文本池空族」里。其中 `appear_id_2_fashion_id`、`appear_id_2_equip_id`、
`change_color_fashion_ids`、`plate_id_2_fashion_ids`、`new_appear_id_2_appear_id`、`opposite_fashion_appear_id_data` 从命名看极可能就是
Q1/Q3 想找的“直连映射表”，**是本次报告最大的缺口，建议优先补解**。

---

## 附：交叉核对

- `fashion_data` 11169 行 / 100 字段；`player_appear_data` 5604 行 / 121 字段；`player_module_appear_data` 1200 行 / 22 字段 —— 与题目基线一致。
- `fashion_data_for_export` 10988 行，键交集 10988/10988 —— 与题目一致（全为子集）。
- `simple_fashion_data` 11169 行 / 10 字段，键交集 11169/11169 —— fashion_data 的瘦身视图。
- 所有数字可由 `_ref_scan.py` → `_verify.py` → `_report.py` 全链路复现。