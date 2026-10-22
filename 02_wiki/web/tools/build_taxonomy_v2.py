# -*- coding: utf-8 -*-
"""按用户草稿重建 wiki 目录树（四分类），旧树备份为 wiki_taxonomy_旧_20261022.json。"""
import json
import pathlib
import shutil

WEB = pathlib.Path(r"E:/la拆包项目/02_wiki/web")
DATA = WEB / "data"
old = DATA / "wiki_taxonomy.json"
if old.exists():
    shutil.copy2(old, DATA / "wiki_taxonomy_旧_20261022.json")

TREE = [
    {
        "id": "preview",
        "name": "置顶 · 预告专栏（未上线资源）",
        "boards": [],
        "children": [
            {"name": "角色时装 / 武器皮肤 / 活动奖池 预告", "boards": ["upcoming_auto"]},
        ],
    },
    {
        "id": "fashion",
        "name": "一、时装类",
        "boards": [],
        "children": [
            {"name": "（一）人物时装 · 头饰 / 衣服&套装 / 背包 / 挂饰 / 面饰 / 发饰 / 投影 / 荧光棒",
             "boards": ["fashion_wardrobe"]},
            {"name": "（二）武器皮肤 · 2D图 / 描述 / SFX音效 / 魅力值",
             "boards": ["weapon_skin_sfx_text_sources"]},
            {"name": "（三）载具 · 类型 / 魅力值", "boards": ["vehicle_full"]},
            {"name": "（四）击败播报与全场最佳动画", "boards": ["kill_broadcast"]},
            {"name": "（五）头像 / 头像框 / 名片框", "boards": ["avatar_catalog"]},
        ],
    },
    {
        "id": "combat",
        "name": "二、战力类",
        "boards": [],
        "children": [
            {"name": "（一）异变核芯", "boards": ["mutation_core_full", "core_skill_12star"]},
            {"name": "（二）战术芯片", "boards": ["tactical_chip_full"]},
            {"name": "（三）无人机", "boards": ["drone_catalog"]},
            {"name": "（四）料理与食谱", "boards": ["edible_catalog"]},
            {"name": "（五）伤害计算公式与场景平衡", "boards": ["scene_balance"]},
            {"name": "（六）各种族潜能", "boards": ["gene_potential_catalog"]},
            {"name": "（七）战斗天赋 / 职业天赋 / 职业技能",
             "boards": ["talent_battle", "talent_prof"]},
        ],
    },
    {
        "id": "activity",
        "name": "三、活动奖池",
        "boards": [],
        "children": [
            {"name": "（一）活动表", "boards": ["activity_master", "lottery_periods"]},
        ],
    },
    {
        "id": "reference",
        "name": "四、综合资料",
        "boards": [],
        "children": [
            {"name": "（一）服务器类型", "boards": ["server_types"]},
            {"name": "（二）全量道具总表", "boards": ["item_master_full"]},
            {"name": "（三）称号", "boards": ["title_catalog"]},
            {"name": "（四）配方", "boards": ["recipe_catalog"]},
            {"name": "（五）说明条目 / 文字与提示总表",
             "boards": ["desc_catalog", "text_notice_catalog", "gift_data_text_sources"]},
            {"name": "（六）实体技能", "boards": ["entity_catalog", "skill_catalog"]},
            {"name": "（七）状态", "boards": ["buff_catalog"]},
            {"name": "（八）图鉴收集", "boards": ["illustration_catalog"]},
        ],
    },
]

doc = {
    "schema": "wiki-taxonomy/v1",
    "generated": "2026-10-22",
    "说明": "四分类重建：置顶预告 / 时装类 / 战力类 / 活动奖池 / 综合资料",
    "标号口径": "中文序号；子级用（一）（二）…；不再使用 零、",
    "折叠": False,
    "树": TREE,
}

(DATA / "wiki_taxonomy.json").write_text(
    json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
(DATA / "wiki_taxonomy.js").write_text(
    "window.WIKI_TAXONOMY = " + json.dumps(doc, ensure_ascii=False) + ";\n", encoding="utf-8")

ids = [b for top in TREE for c in top["children"] for b in c["boards"]]
print("顶层", len(TREE), "｜叶子", sum(len(t["children"]) for t in TREE), "｜板块引用", len(ids))
print("去重", len(set(ids)))
