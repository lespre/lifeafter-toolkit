# -*- coding: utf-8 -*-
"""生成「人物时装板块映射架构」清单：源表字段 → 卡字段 → 覆盖卡数。

口径：
- 覆盖卡数直接从板产物 `fashion_wardrobe.json` 实测（不是估的）。
- 源字段 → 卡字段的映射规则写死在 RULE 表里（每条都能在构建脚本里找到对应读取点）。
- 输出：`90_临时/fashion_mapping_清单.md`
"""
import json
import pathlib
import re
import sys

PROJ = pathlib.Path("E:/la拆包项目")
BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"
OUT = PROJ / "90_临时/fashion_mapping_清单.md"

# ── 维度分组：卡字段 → (维度, 源表.源字段, 判定/说明) ──────────────────────
# 源表简写：F=fashion_data  A=player_appear_data  M=player_module_appear_data
RULE: list[tuple] = [
    # 身份 / 名称
    ("name", "身份", "F.name", "商品名（原子卡名）"),
    ("show_name", "身份", "F.show_name", "游戏内显示名（时限变体行显示基础款名）"),
    ("man_show_name", "身份", "F.man_show_name", "男版显示名"),
    ("desc", "身份", "F.desc", "描述（本身即女/通用版）"),
    ("desc_man", "身份", "F.man_desc", "男版描述"),
    ("name_man", "身份", "F.man_name", "男版命名"),
    ("name_female", "身份", "F.female_name", "女版命名"),
    ("foreign_name", "身份", "F.foreign_name", "海外名"),
    ("new_fashion_id_str", "身份", "F.new_fashion_id_str", "内部款号（如 hat_3002_1_0）"),
    ("sort_key", "身份", "F.sort_key", "排序键"),
    ("brand_id", "身份", "F.brand_id", "品牌"),
    ("is_2025", "身份", "F.is_2025", "2025 新品标记"),
    ("is_climb_tower", "身份", "F.is_climb_tower", "爬塔可用"),
    ("source", "身份", "（构建器合成）", "卡面来源描述"),
    ("provenance", "身份", "（板级 source_locks）", "可机读定位链（行级/结构级）"),
    ("evidence", "身份", "（板级 evidence）", "证据等级"),

    # 部位 / 性别
    ("part_bucket", "部位", "F.part_type", "展示分组（头饰/衣服/背包/挂饰…）"),
    ("part_code", "部位", "F.part", "★ 内部部位码 = 部位判定唯一口径"),
    ("part_code_cn", "部位", "F.part", "部位码中文（1 头发头饰 3 衣服整套 4 背包 5 荧光棒）"),
    ("gender", "部位", "F.force_gender + A.gender", "性别标注"),
    ("gender_scope", "部位", "A.model_name / socket_models / force_gender", "双版/仅女/仅男/通用"),
    ("gender_scope_note", "部位", "（判定链）", "性别判定依据"),
    ("uncap_appear_gender", "部位", "F.uncap_appear_gender", "未解锁/不封顶时的外观版本（脱帽款）"),

    # 取图 / 媒体
    ("_media", "取图", "F.icons（[0]女 [1]男）", "图标（男女两列）"),
    ("icon_state", "取图", "（构建器）", "图标齐全度状态"),
    ("icon_count", "取图", "（构建器）", "图标张数"),
    ("icon_note", "取图", "（构建器）", "缺图/替代图说明"),
    ("model_paths", "取图", "A.model_name / high_model_name / human_body_model_name", "模型路径"),
    ("npc_hidden", "取图", "A.forbid_in_npc_monster", "禁止在 NPC/怪物身上出现"),
    ("model_change_color_id", "取图", "F.model_change_color_id", "默认配色 id（2,087 卡）"),

    # 数值
    ("charm_value", "数值", "F.charm_value", "魅力值"),
    ("charm_note", "数值", "F.charm_value", "魅力值说明"),
    ("grade_level", "数值", "F.level", "品级"),
    ("cohabit_friendliness", "数值", "F.friendliness", "friendliness 原值（按部位固定，语义待核）"),
    ("cohabit_level", "数值", "F.friendliness + cohabit_level_data", "折算同居五档（相遇0/相知700/相伴1500/同行3000/同心6000）"),
    ("level", "数值", "F.level", "品级（部分卡）"),

    # 花苞
    ("reborn_vis", "花苞", "F.reborn_vis", "藏花（11-01 游戏内核对定论）"),
    ("flower_bud", "花苞", "F.replace_flower_path + A.replace_flower_id + A.socket_names['flower']", "换花（挂点 flower · 仅再生者）"),

    # 染色
    ("dye", "染色", "F.change_color_id → appear_change_color_data", "染色方案（HEX 色值 + 开关）"),
    ("dye.hair", "染色", "F.hair_change_color_id → appear_change_hair_color_data", "发色方案"),
    ("dye.appear_ids", "染色", "A.change_color_id", "外观层染色 id"),
    ("dye.sockets", "染色", "F.change_color_socket", "染色插槽"),

    # 获取 / 上架
    ("obtain_res", "获取", "fashion_obtain_res_data.obtain_res", "获取途径原文"),
    ("other_get_methods", "获取", "F.other_get_methods → other_get_method_data", "其他获取方式（配方兑换）"),
    ("theme", "获取", "fashion_obtain_handbook_data.theme_name", "套装主题 + 海报 + 开放日"),
    ("show_start", "获取", "F.start_show_ts", "上架时间"),
    ("show_schedule", "获取", "F.show_time_offset_ids / show_valid_times", "上架与可见时段"),
    ("gift_package", "获取", "F.gift_package_id", "礼包 id"),
    ("display_bg", "获取", "F.bg_ids → fashion_bg_data", "展示背景（图 + 场景文件）"),

    # 卖点 / 预览
    ("value_words", "卖点", "F.value_word_ids → fashion_value_word_data", "26 个卖点标签"),
    ("preview_group", "卖点", "F.preview_id → player_fashion_preview_data.group_id", "专属预览分组（32/32 全中）"),
    ("anim_graph", "卖点", "F.anim_graph_id / ui_anim_graph_id", "专属动作图 id 串"),
    ("special_idle_anims", "卖点", "F.special_idle_anims2", "专属待机动作"),
    ("fashion_action_id", "卖点", "F.fashion_action_id", "专属动作"),
    ("point_light_id", "卖点", "F.point_light_id", "点光源 id"),

    # 展示开关
    ("show_no_have", "开关", "F.show_no_have", "未拥有也显示（1=显示 / 空=不显示）"),
    ("fashion_preview", "开关", "F.fashion_preview", "可预览"),
    ("takeoff_head", "开关", "F.takeoff_head", "可脱帽"),
    ("not_show_rebirth_makeup", "开关", "F.not_show_rebirth_makeup", "再生形态不显示妆容"),
    ("hide_parts", "开关", "F.hide_other_part + A.hide_head/face/pendant", "隐藏部位"),
    ("back_weapon_vis", "开关", "F.back_weapon_vis", "隐藏副武器"),
    ("suit_buff_ids", "开关", "F.suit_buff_id", "套装 buff"),
    ("mutex_modules", "开关", "F.mutex_modules", "互斥模块"),

    # 技术留档
    ("tech_flags", "技术", "F/A 的挂点/软骨骼/权重类字段", "挂点名、软骨骼、v2/link/dynamic 挂点、AI 权重…"),
    ("misc_flags", "技术", "F 的零散开关", "礼包次数、背包假词条、折星型、组队背景…"),
    ("bone_info", "技术", "F.is_new_bone + new_bone_soft_bone_id", "新骨骼 / 软骨骼 id"),
    ("green_model", "技术", "F.green_model_path_female(+_high)", "风底形态模型"),
    ("durations", "技术", "F.valid_days / body_sfx_data.valid_days", "时限（永久 / N 天）"),
    ("duration_state", "技术", "（构建器）", "permanent / timed / mixed"),
    ("row_keys", "技术", "（构建器）", "商品层行键（★ 不是外观行键）"),
]


def main() -> int:
    board = json.loads(BOARD.read_text(encoding="utf-8"))
    items = board["items"]
    cnt: dict[str, int] = {}
    for it in items:
        for k in it:
            cnt[k] = cnt.get(k, 0) + 1

    # 三主表字段总数（实测）
    tables = {
        "F": ("fashion_data", 11169, 100),
        "A": ("player_appear_data", 5604, 121),
        "M": ("player_module_appear_data", 1200, 22),
    }
    aux = [
        ("appear_change_color_data", "染色方案", "384/388 id 对上"),
        ("appear_change_hair_color_data", "发色方案", "14/14 全对"),
        ("fashion_value_word_data", "26 个卖点标签", "nxs，00 共享工具读通"),
        ("other_get_method_data", "其他获取方式", "nxs，132 行"),
        ("fashion_obtain_res_data", "获取途径原文", "1,161 行 / 749 卡"),
        ("fashion_obtain_handbook_data", "套装主题 + 海报 + 开放日", "392 行 / 861 卡"),
        ("player_fashion_preview_data", "专属预览分组", "group_id 32/32 全中"),
        ("fashion_bg_data", "展示背景图 + 场景", "26/26 全对"),
        ("cohabit_level_data", "同居五档阈值", "5 行"),
        ("body_sfx_data", "衣柜投影名册", "44 行 → 46 张投影卡"),
        ("follow_charm_conf_data", "跟随魅力（投影）", "主键是 buff_id 不是 item_id"),
    ]

    L: list[str] = []
    L.append("# 人物时装板块 · 映射架构清单")
    L.append("")
    L.append("> 生成脚本：`90_临时/_gen_mapping.py`；数据源 `01_索引与产物/41_还原树/pe/配置/com/cdata/`（不扫线上 npk）。")
    L.append(f"> 板产物：`02_wiki/web/data/boards/fashion_wardrobe.json`，**{len(items)} 张卡 / {len(cnt)} 种卡字段**。")
    L.append("> 覆盖卡数均为实测值（非估值）。")
    L.append("")
    L.append("## 一、源表 → 主干三表 → 辅助表")
    L.append("")
    L.append("| 层 | 表 | 行数 | 字段数 | 角色 |")
    L.append("|---|---|---|---|---|")
    L.append("| 商品层 | `fashion_data` | 11,169 | 100 | ★ 主干：商品名/图标/魅力值/部位/时限/藏花/染色 id… |")
    L.append("| 资源层 | `player_appear_data` | 5,604 | 121 | ★ 主干：模型路径/隐藏部位/挂点/染色 id/flower 挂点 |")
    L.append("| 模块层 | `player_module_appear_data` | 1,200 | 22 | 面饰/挂饰，自带 icon + female_icon + 文案 |")
    L.append("| 切片 | `simple_fashion_data` | 11,169 | 10 | fashion_data 的瘦身视图（10 字段） |")
    L.append("| 切片 | `fashion_data_for_export` | 10,988 | 101 | 导出切片（+fashion_id 序号，非全集） |")
    L.append("")
    L.append("**主键连接**：`fashion_data.appear_ids`（0x0b jump 组，kind=0x01 字面 id）→ `player_appear_data` 行键；")
    L.append("`player_appear_data.part` 是部位码唯一来源；`fashion_data.part` 是商品层部位码。")
    L.append("")
    L.append("### 辅助表（11 张，已接）")
    L.append("")
    L.append("| 表 | 提供 | 命中率 |")
    L.append("|---|---|---|")
    for t, p, note in aux:
        L.append(f"| `{t}` | {p} | {note} |")
    L.append("")
    L.append("## 二、字段映射（源字段 → 卡字段 → 覆盖卡数）")
    L.append("")
    cur = None
    for key, dim, src, note in RULE:
        if dim != cur:
            cur = dim
            L.append("")
            L.append(f"### {dim}")
            L.append("")
            L.append("| 卡字段 | 源字段 | 覆盖卡数 | 说明 |")
            L.append("|---|---|---|---|")
        L.append(f"| `{key}` | {src} | {cnt.get(key, 0):,} | {note} |")
    L.append("")
    L.append("## 三、构建脚本分层（顺序固定，三者幂等）")
    L.append("")
    L.append("| 层 | 脚本 | 负责 |")
    L.append("|---|---|---|")
    L.append("| 维度层 | `02_wiki/web/tools/enrich_fashion_dimensions.py` | 展示开关 / 分版描述 / 藏花 / 换花 / 性别范围 / 隐藏部位 |")
    L.append("| 外观层 | `02_wiki/web/tools/add_fashion_style_fields.py` | 染色 / 获取 / 套装主题 / 预览分组 / friendliness / 部位码 / 模型路径 / NPC 限制 / 技术留档 |")
    L.append("| 结构层 | `02_wiki/web/tools/merge_projection_variants.py` | 投影时限变体合并（同名 + 同 buff_id → 一张卡） |")
    L.append("")
    L.append("★ 卡片的 `row_keys` 是**商品层行键**，不是外观行键 —— 外观层字段必须经 fashion 行的")
    L.append("`appear_ids` 关联（`amap[appear_id]`），直接拿 row_keys 取 amap 会全空。")
    L.append("")
    L.append("## 四、板级溯源")
    L.append("")
    sl = board["meta"]["provenance"]["source_locks"]
    L.append(f"`meta.provenance.source_locks` 共 **{len(sl)} 条**（sha256 字面量，字节级可复现）：")
    L.append("")
    L.append("| role | source_id | 路径 |")
    L.append("|---|---|---|")
    for x in sl:
        L.append(f"| {x.get('role')} | `{x.get('source_id')}` | `{x.get('path')}` |")
    L.append("")
    L.append("## 五、尚未落板的部分")
    L.append("")
    L.append("- `player_appear_data` 余约 40 个字段未落：多为 NPC/AI 相关或恒定值，价值低。")
    L.append("- `friendliness` 语义未确证（已用中性措辞，配置表里没有把时装与好感度连起来的线）。")
    L.append("- 少数「PE 测试服池串、配置无行」的卡只能走 roster 通道，缺行级定位链。")
    L.append("")
    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"写出 {OUT}（{len(L)} 行）")
    print(f"卡 {len(items)} / 字段种类 {len(cnt)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
