# 人物时装板块 · 映射架构清单

> 生成脚本：`90_临时/_gen_mapping.py`；数据源 `01_索引与产物/41_还原树/pe/配置/com/cdata/`（不扫线上 npk）。
> 板产物：`02_wiki/web/data/boards/fashion_wardrobe.json`，**3151 张卡 / 120 种卡字段**。
> 覆盖卡数均为实测值（非估值）。

## 一、源表 → 主干三表 → 辅助表

| 层 | 表 | 行数 | 字段数 | 角色 |
|---|---|---|---|---|
| 商品层 | `fashion_data` | 11,169 | 100 | ★ 主干：商品名/图标/魅力值/部位/时限/藏花/染色 id… |
| 资源层 | `player_appear_data` | 5,604 | 121 | ★ 主干：模型路径/隐藏部位/挂点/染色 id/flower 挂点 |
| 模块层 | `player_module_appear_data` | 1,200 | 22 | 面饰/挂饰，自带 icon + female_icon + 文案 |
| 切片 | `simple_fashion_data` | 11,169 | 10 | fashion_data 的瘦身视图（10 字段） |
| 切片 | `fashion_data_for_export` | 10,988 | 101 | 导出切片（+fashion_id 序号，非全集） |

**主键连接**：`fashion_data.appear_ids`（0x0b jump 组，kind=0x01 字面 id）→ `player_appear_data` 行键；
`player_appear_data.part` 是部位码唯一来源；`fashion_data.part` 是商品层部位码。

### 辅助表（11 张，已接）

| 表 | 提供 | 命中率 |
|---|---|---|
| `appear_change_color_data` | 染色方案 | 384/388 id 对上 |
| `appear_change_hair_color_data` | 发色方案 | 14/14 全对 |
| `fashion_value_word_data` | 26 个卖点标签 | nxs，00 共享工具读通 |
| `other_get_method_data` | 其他获取方式 | nxs，132 行 |
| `fashion_obtain_res_data` | 获取途径原文 | 1,161 行 / 749 卡 |
| `fashion_obtain_handbook_data` | 套装主题 + 海报 + 开放日 | 392 行 / 861 卡 |
| `player_fashion_preview_data` | 专属预览分组 | group_id 32/32 全中 |
| `fashion_bg_data` | 展示背景图 + 场景 | 26/26 全对 |
| `cohabit_level_data` | 同居五档阈值 | 5 行 |
| `body_sfx_data` | 衣柜投影名册 | 44 行 → 46 张投影卡 |
| `follow_charm_conf_data` | 跟随魅力（投影） | 主键是 buff_id 不是 item_id |

## 二、字段映射（源字段 → 卡字段 → 覆盖卡数）


### 身份

| 卡字段 | 源字段 | 覆盖卡数 | 说明 |
|---|---|---|---|
| `name` | F.name | 3,151 | 商品名（原子卡名） |
| `show_name` | F.show_name | 1,195 | 游戏内显示名（时限变体行显示基础款名） |
| `man_show_name` | F.man_show_name | 3 | 男版显示名 |
| `desc` | F.desc | 2,457 | 描述（本身即女/通用版） |
| `desc_man` | F.man_desc | 15 | 男版描述 |
| `name_man` | F.man_name | 4 | 男版命名 |
| `name_female` | F.female_name | 3 | 女版命名 |
| `foreign_name` | F.foreign_name | 158 | 海外名 |
| `new_fashion_id_str` | F.new_fashion_id_str | 905 | 内部款号（如 hat_3002_1_0） |
| `sort_key` | F.sort_key | 2,209 | 排序键 |
| `brand_id` | F.brand_id | 302 | 品牌 |
| `is_2025` | F.is_2025 | 13 | 2025 新品标记 |
| `is_climb_tower` | F.is_climb_tower | 215 | 爬塔可用 |
| `source` | （构建器合成） | 3,151 | 卡面来源描述 |
| `provenance` | （板级 source_locks） | 3,151 | 可机读定位链（行级/结构级） |
| `evidence` | （板级 evidence） | 3,151 | 证据等级 |

### 部位

| 卡字段 | 源字段 | 覆盖卡数 | 说明 |
|---|---|---|---|
| `part_bucket` | F.part_type | 3,151 | 展示分组（头饰/衣服/背包/挂饰…） |
| `part_code` | F.part | 1,201 | ★ 内部部位码 = 部位判定唯一口径 |
| `part_code_cn` | F.part | 1,201 | 部位码中文（1 头发头饰 3 衣服整套 4 背包 5 荧光棒） |
| `gender` | F.force_gender + A.gender | 3,096 | 性别标注 |
| `gender_scope` | A.model_name / socket_models / force_gender | 2,258 | 双版/仅女/仅男/通用 |
| `gender_scope_note` | （判定链） | 2,258 | 性别判定依据 |
| `uncap_appear_gender` | F.uncap_appear_gender | 18 | 未解锁/不封顶时的外观版本（脱帽款） |

### 取图

| 卡字段 | 源字段 | 覆盖卡数 | 说明 |
|---|---|---|---|
| `_media` | F.icons（[0]女 [1]男） | 2,516 | 图标（男女两列） |
| `icon_state` | （构建器） | 3,151 | 图标齐全度状态 |
| `icon_count` | （构建器） | 2,494 | 图标张数 |
| `icon_note` | （构建器） | 66 | 缺图/替代图说明 |
| `model_paths` | A.model_name / high_model_name / human_body_model_name | 1,833 | 模型路径 |
| `npc_hidden` | A.forbid_in_npc_monster | 49 | 禁止在 NPC/怪物身上出现 |
| `model_change_color_id` | F.model_change_color_id | 2,087 | 默认配色 id（2,087 卡） |

### 数值

| 卡字段 | 源字段 | 覆盖卡数 | 说明 |
|---|---|---|---|
| `charm_value` | F.charm_value | 2,339 | 魅力值 |
| `charm_note` | F.charm_value | 257 | 魅力值说明 |
| `grade_level` | F.level | 2,269 | 品级 |
| `cohabit_friendliness` | F.friendliness | 1,047 | friendliness 原值（按部位固定，语义待核） |
| `cohabit_level` | F.friendliness + cohabit_level_data | 1,047 | 折算同居五档（相遇0/相知700/相伴1500/同行3000/同心6000） |
| `level` | F.level | 0 | 品级（部分卡） |

### 花苞

| 卡字段 | 源字段 | 覆盖卡数 | 说明 |
|---|---|---|---|
| `reborn_vis` | F.reborn_vis | 199 | 藏花（11-01 游戏内核对定论） |
| `flower_bud` | F.replace_flower_path + A.replace_flower_id + A.socket_names['flower'] | 5 | 换花（挂点 flower · 仅再生者） |

### 染色

| 卡字段 | 源字段 | 覆盖卡数 | 说明 |
|---|---|---|---|
| `dye` | F.change_color_id → appear_change_color_data | 342 | 染色方案（HEX 色值 + 开关） |
| `dye.hair` | F.hair_change_color_id → appear_change_hair_color_data | 0 | 发色方案 |
| `dye.appear_ids` | A.change_color_id | 0 | 外观层染色 id |
| `dye.sockets` | F.change_color_socket | 0 | 染色插槽 |

### 获取

| 卡字段 | 源字段 | 覆盖卡数 | 说明 |
|---|---|---|---|
| `obtain_res` | fashion_obtain_res_data.obtain_res | 749 | 获取途径原文 |
| `other_get_methods` | F.other_get_methods → other_get_method_data | 2 | 其他获取方式（配方兑换） |
| `theme` | fashion_obtain_handbook_data.theme_name | 864 | 套装主题 + 海报 + 开放日 |
| `show_start` | F.start_show_ts | 10 | 上架时间 |
| `show_schedule` | F.show_time_offset_ids / show_valid_times | 20 | 上架与可见时段 |
| `gift_package` | F.gift_package_id | 23 | 礼包 id |
| `display_bg` | F.bg_ids → fashion_bg_data | 36 | 展示背景（图 + 场景文件） |

### 卖点

| 卡字段 | 源字段 | 覆盖卡数 | 说明 |
|---|---|---|---|
| `value_words` | F.value_word_ids → fashion_value_word_data | 86 | 26 个卖点标签 |
| `preview_group` | F.preview_id → player_fashion_preview_data.group_id | 72 | 专属预览分组（32/32 全中） |
| `anim_graph` | F.anim_graph_id / ui_anim_graph_id | 47 | 专属动作图 id 串 |
| `special_idle_anims` | F.special_idle_anims2 | 571 | 专属待机动作 |
| `fashion_action_id` | F.fashion_action_id | 598 | 专属动作 |
| `point_light_id` | F.point_light_id | 227 | 点光源 id |

### 开关

| 卡字段 | 源字段 | 覆盖卡数 | 说明 |
|---|---|---|---|
| `show_no_have` | F.show_no_have | 2,874 | 未拥有也显示（1=显示 / 空=不显示） |
| `fashion_preview` | F.fashion_preview | 2,874 | 可预览 |
| `takeoff_head` | F.takeoff_head | 2,874 | 可脱帽 |
| `not_show_rebirth_makeup` | F.not_show_rebirth_makeup | 25 | 再生形态不显示妆容 |
| `hide_parts` | F.hide_other_part + A.hide_head/face/pendant | 177 | 隐藏部位 |
| `back_weapon_vis` | F.back_weapon_vis | 53 | 隐藏副武器 |
| `suit_buff_ids` | F.suit_buff_id | 37 | 套装 buff |
| `mutex_modules` | F.mutex_modules | 199 | 互斥模块 |

### 技术

| 卡字段 | 源字段 | 覆盖卡数 | 说明 |
|---|---|---|---|
| `tech_flags` | F/A 的挂点/软骨骼/权重类字段 | 2,088 | 挂点名、软骨骼、v2/link/dynamic 挂点、AI 权重… |
| `misc_flags` | F 的零散开关 | 2,088 | 礼包次数、背包假词条、折星型、组队背景… |
| `bone_info` | F.is_new_bone + new_bone_soft_bone_id | 58 | 新骨骼 / 软骨骼 id |
| `green_model` | F.green_model_path_female(+_high) | 26 | 风底形态模型 |
| `durations` | F.valid_days / body_sfx_data.valid_days | 2,076 | 时限（永久 / N 天） |
| `duration_state` | （构建器） | 2,076 | permanent / timed / mixed |
| `row_keys` | （构建器） | 2,916 | 商品层行键（★ 不是外观行键） |

## 三、构建脚本分层（顺序固定，三者幂等）

| 层 | 脚本 | 负责 |
|---|---|---|
| 维度层 | `02_wiki/web/tools/enrich_fashion_dimensions.py` | 展示开关 / 分版描述 / 藏花 / 换花 / 性别范围 / 隐藏部位 |
| 外观层 | `02_wiki/web/tools/add_fashion_style_fields.py` | 染色 / 获取 / 套装主题 / 预览分组 / friendliness / 部位码 / 模型路径 / NPC 限制 / 技术留档 |
| 结构层 | `02_wiki/web/tools/merge_projection_variants.py` | 投影时限变体合并（同名 + 同 buff_id → 一张卡） |

★ 卡片的 `row_keys` 是**商品层行键**，不是外观行键 —— 外观层字段必须经 fashion 行的
`appear_ids` 关联（`amap[appear_id]`），直接拿 row_keys 取 amap 会全空。

## 四、板级溯源

`meta.provenance.source_locks` 共 **10 条**（sha256 字面量，字节级可复现）：

| role | source_id | 路径 |
|---|---|---|
| primary | `fashion-wardrobe-struct` | `01_索引与产物/41_还原树/pe/配置_增量快照/com/cdata/fashion_data.py` |
| comparison | `fashion-parts-supplement-player_appear_data` | `01_索引与产物/41_还原树/pe/配置/com/cdata/player_appear_data.py` |
| comparison | `fashion-parts-supplement-simple_fashion_data` | `01_索引与产物/41_还原树/pe/配置/com/cdata/simple_fashion_data.py` |
| primary | `face-preset-fashion_preset_do_face_config_data` | `01_索引与产物/41_还原树/pe/配置/com/cdata/fashion_preset_do_face_config_data.py` |
| comparison | `fashion-projection-body_sfx_data` | `01_索引与产物/41_还原树/pe/配置/com/cdata/body_sfx_data.py` |
| comparison | `fashion-projection-body_sfx_data-chs` | `01_索引与产物/41_还原树/pe/配置/com/cdata/body_sfx_data_chs.py` |
| comparison | `fashion-projection-common_item` | `documents 实时包（common_item_text_sources.json 同源）` |
| comparison | `fashion-projection-buff_data` | `E:\la拆包项目\01_索引与产物\41_还原树\pe\配置\com\cdata\buff_data.py` |
| comparison | `documents-py314-current` | `documents 实时包（player_module_appear_data 同源）` |
| comparison | `fashion-projection-follow_charm_conf_data` | `01_索引与产物/41_还原树/pe/配置/com/cdata/follow_charm_conf_data.py` |

## 五、尚未落板的部分

- `player_appear_data` 余约 40 个字段未落：多为 NPC/AI 相关或恒定值，价值低。
- `friendliness` 语义未确证（已用中性措辞，配置表里没有把时装与好感度连起来的线）。
- 少数「PE 测试服池串、配置无行」的卡只能走 roster 通道，缺行级定位链。
