# fashion_wardrobe 参数清单（2026-11-01 实测版）

## ✅ 本轮已落地（用户 2026-11-01 点选，脚本 `add_fashion_style_fields.py`）

| 卡片字段 | 覆盖卡数 | 说明 |
|---|---|---|
| `dye` | 202 | 染色方案（`change_color_id` → `appear_change_color_data`，384/388 对上，带 HEX 色值 + 色块）；含 `dye.hair` 发色方案（14/14 全对） |
| `model_change_color_id` | 2,083 | 默认配色 id，原样存 |
| `obtain_res` | 749 | 获取途径（`fashion_obtain_res_data`）：于活动获得 / 于商城获得 / 于明日通行证获得 … |
| `theme` | 861 | 套装主题（`fashion_obtain_handbook_data`）：主题名 + 海报图 + 开放日期 |
| `show_start` | 10 | 上架时间（`start_show_ts` → UTC+8 日期） |
| `gift_package` | 23 | 礼包 id |
| `display_bg` | 35 | 展示背景（`bg_ids` → `fashion_bg_data`，26/26 全对，带背景图路径 + 场景文件） |
| `anim_graph` | 46 | 专属动作图 id 串（`anim_graph_data` 是空表，只存 id） |
| `glowstick_switchable` | 128 | 荧光棒可切换 |
| `hide_idle_anim` | 61 | 展示动作可关 |

**用户答复「待我辨析」的 4 项（`friendliness` / `uncap_appear_gender` / `rebirth_tex` / `value_word_ids`）与骨架类一律未写入。**

口径来源：`01_索引与产物/41_还原树/pe/配置/com/cdata/fashion_data.py`（11,169 行 / 100 字段）、
`player_appear_data.py`（5,604 行 / 121 字段）。板上共 3,152 张卡。
**所有数字都是本轮实测**，不是估计；能接到辅助表的已接上并给出一致率。

已进卡片（不再列）：`show_no_have` / `fashion_preview` / `desc_man` / `man_name`+`female_name` /
`replace_flower_path`+`replace_flower_id`+`reborn_socket` / `reborn_vis` / `suit_buff_id` /
`mutex_modules` / `takeoff_head` / `not_show_rebirth_makeup` / `special_idle_anims` /
`fashion_action_id` / `point_light_id` / `foreign_name` / `is_2025` / `is_climb_tower` /
`new_fashion_id_str` / `sort_key` / `back_weapon_vis` / `hide_other_part` / `charm_value` /
`desc` / `icons` / `level` / `model_id` / `appear_ids` / `valid_days` / `part_type` / `brand_id`。

---

## 一、染色

| # | 项 | 实测 | 结论 |
|---|---|---|---|
| 1 | **染色方案** | `change_color_id` 1,355 行 / 388 个 id；接 `appear_change_color_data`（705 行）**384/388 对上**，表里带 `colors`（HEX 色值，如 `FF1B1928`）+ `change_color_switch` + `pbr_default_mode` | **建议加**，落「可染色 · N 套方案」+ 颜色值 |
| 2 | **发色方案** | `hair_change_color_id` 49 行 / 14 个 id；接 `appear_change_hair_color_data`（14 行）**14/14 全对上**，带 `color_socket`（如 `h_f_3262_1`）、`model_type` | **建议加**，与 #1 合并为染色区 |
| 3 | `model_change_color_id` | 11,168 行几乎全量，值 1/2/3 | **不加**：是默认配色 id，不是「能否染色」 |

## 二、获取与上架

| # | 项 | 实测 | 结论 |
|---|---|---|---|
| 4 | **获取途径** | 新表 `fashion_obtain_res_data`（1,161 行，主键与 fashion_data 直接命中 1,043 行 / **749 卡**），字段 `obtain_res` 原文：于活动获得 393 / 于商城获得 351 / 于明日通行证获得 10 / 于商城或活动获得 6 / 于S8高校证书获得 4 / 于S9高校证书获得 4 | **建议加**（749 卡有明确途径） |
| 5 | **套装主题** | 新表 `fashion_obtain_handbook_data`（392 行），带 `theme_name`（决战绿茵 / 远洋风姿 / 宿命守护 / CC定制 / 圣诞恋人 / 醒狮踏春 …）、`fashion_ids`、`open_time`、海报图路径。命中 **861 行 / 859 卡**；`theme_codes='yh'` 的 168 行按同名兜底 **168/168 全中** | **建议加**（859 卡有主题 + 海报图） |
| 6 | **上架时间** | `start_show_ts` 96 行 / 10 卡，Unix 秒：最早 2026-01-22（雪语冰梦-头饰），最晚 2026-09-24（云兔衔光-衣服） | **建议加**，转成日期显示 |
| 7 | 礼包绑定 | `gift_package_id` 23 行 / 23 卡，形如 `[1, 922299]`；库里没找到能直接对上 922299 的礼包表 | **待定**：只能存 id 号 |
| 8 | `other_get_methods` | 7 行 / 2 卡（纸箱头、运动达人），值都是 `[17]`；`other_get_method_data` 只有 `.nxs` 新格式，暂解不开 | **待定** |
| 9 | `faked_times_limit` | 160 行**全是 1**，且这 160 行的 `valid_days` 全为空 | **不加**：与时限无关，是恒 1 开关 |
| 10 | `valid_scene_ids` | 只有 4 行，值全是 `[280]` | **不加**：覆盖太小 |
| 11 | `obtain_notify` | 10,237 行 / 1,945 卡，值恒 1 | **不加**：无区分度 |

## 三、穿戴效果

| # | 项 | 实测 | 结论 |
|---|---|---|---|
| 12 | `is_slim_bag` | 6,563 行 = **全部 cloth 3,778 + hat 2,618 + suit 167**，即每一件衣服/头饰/套装都有；**背包一件都没有** | **不加**：与「薄款背包」无关，是恒 1 开关（原判断有误） |
| 13 | `is_available_glowstick` | 896 行 / 128 卡 | 建议加（荧光棒可切换），值恒 1，无文本 |
| 14 | `uncap_appear_gender` | 133 行 / 17 卡，值只有 3（77 行）/ 2（35 行）/ 1（21 行） | **待定**：1/2/3 含义未知 |
| 15 | `rebirth_tex` | 427 行 / 58 卡，值恒 True | **待定**：疑为再生形态专用贴图 |
| 16 | `friendliness` | 1,355 行 / 1,043 卡，值 1280(615) / 680(475) / 1960(127) / 780 / 400 / 980 / 720 / 540 | **待定**：疑为好感度加成；`add_friendliness_data.nxs` 解不开 |

## 四、展示动作与 UI

| # | 项 | 实测 | 结论 |
|---|---|---|---|
| 17 | **专属动作图** | `anim_graph_id` / `ui_anim_graph_id`，值是**分号串**（`156;154`、`20;`），共 119 个 id；`anim_graph_data` **是空表**，接不到文本 | **建议加**：只存 id 串 + 标「专属动作图」 |
| 18 | **展示背景** | `bg_ids` 26 个 id，接 `fashion_bg_data`（137 行）**26/26 全对上**，带背景图路径（`shizhuang_icon/…/img_bg03.png`）与场景文件（`scene/login/login04.scn`） | **建议加**（35 卡） |
| 19 | `preview_id` | 32 个小整数（1~21…）；`player_fashion_preview_data` 只有 1 个能对上，不是主键引用 | **待定**：只能存编号 |
| 20 | `value_word_ids` | 412 行 / 85 卡，值如 `[2]` `[1,4]`；文本表 `fashion_value_word_data.nxs` 是 **0x73 新格式**（模块字节码），本轮解不开 | **待定**：需先破解该表 |
| 21 | `can_hide_special_idle_anim` | 565 行 / 61 卡，值恒 True | 建议加（展示动作可关） |
| 22 | `theme_codes` | 168 行**全是 `['yh']`**，本身无区分度；但能经 #5 的主题表拿到主题名 | 不单独加，已并入 #5 |

## 五、骨架 / 模型技术

| # | 项 | 实测 | 结论 |
|---|---|---|---|
| 23 | `is_new_bone` + `new_bone_soft_bone_id` | 596 / 282 行，57 / 32 卡 | **待定**：新骨骼（影响与其它时装的穿模） |
| 24 | `green_model_path_female` (+`_high`) | 252 / 56 行，26 卡，样例 `…/fengdi_b_f_3411…` | **待定**：「风底」形态模型 |
| 25 | `socket_model_use_high_model` / `forbid_primary_high_model` | 441 / 84 行，55 / 12 卡 | **不加**：纯技术，无文案 |

## 明确不加（技术字段，留索引即可）

`max_stack_num`（恒 2147483647）· `hide_in_bag`（全 True）· `tex_compress_type` · `model_socket`（恒 waist_r）·
`socket_models*` / `socket_names*` / `soft_bone_ids*` / `v2_socket_*` / `v2_soft_bone_id` / `link_*` /
`dynamic_*` · `show_valid_times`（0 行）· `state_action_anim` / `state_action_socket` / `replace_weapon_anim`（0 行）。

## 附：`reborn_vis` = 藏花（已定论）

- `reborn_vis=True` 1,121 行，部位 头饰 473 / 衣服 551 / 套装 97 / 背包 0 / 荧光棒 0；卡级 199 张。
- 用户 2026-11-01 游戏内核对确认：**就是藏花**。前端角标 `藏花`（实色深青）。
- 换花 5 款（尼罗河传说 / 心绪共鸣 / 樱灵狐梦 / 雪语冰梦 / 香韵弄樱）走的是另一条路：
  `socket_names=['flower']` + `socket_models=cloth_xxxx_hua.gim` + `socket_model_only_for_reborn=[1]` +
  `replace_flower_id` —— 在再生者背上挂花模型把花苞**换掉**，故这 5 款 `reborn_vis` 为空，**藏花与换花互斥**。
  卡上 `flower_bud.reborn_socket` 记挂点 / 模型 / 仅再生者标记。
- 背包包围盒 span_x≥13 的结论**已撤字段**（用户判定为权宜之计），待全量 `.mesh` 再谈。
