# -*- coding: utf-8 -*-
"""把 nucleus 并入 mutation_core_full：核芯只保留一个全量表。

口径：
  · 主体 mutation_core_full（132 条，带品级/描述/图标/武器类型）
  · 并入 nucleus 重建版的 76 条（按名字对齐，补 server / max_star / 属性类型）
  · 12 星上限统一写入 max_star
  · card_mode=roster：卡面只留图+名，详情点开才看
"""
from __future__ import annotations

import json
import pathlib
import re

WEB = pathlib.Path(r"E:/la拆包项目/02_wiki/web")
B = WEB / "data/boards"

core = json.loads((B / "mutation_core_full.json").read_text(encoding="utf-8"))
nuc = json.loads((B / "nucleus.json").read_text(encoding="utf-8"))


def norm(s: str) -> str:
    return re.sub(r"[\s·・\-—（）()【】\[\]]", "", s or "")


by_name = {}
for it in core["items"]:
    by_name.setdefault(norm(it.get("name")), it)

merged = added = enriched = 0
for it in nuc["items"]:
    k = norm(it.get("name"))
    tgt = by_name.get(k)
    if tgt:
        tgt["server"] = it.get("server") or tgt.get("server")
        tgt["attr_type"] = it.get("attr_type") or tgt.get("attr_type")
        tgt["max_star"] = 12
        if it.get("provenance") and not tgt.get("provenance"):
            tgt["provenance"] = it["provenance"]
        enriched += 1
    else:
        it["max_star"] = 12
        it["kind"] = "核芯"
        core["items"].append(it)
        by_name[k] = it
        added += 1
    merged += 1

for it in core["items"]:
    it.pop("sort_660", None)          # 去掉这个字段，页面才会走 roster（简略卡面）
    it.setdefault("max_star", 12)
    it["star_text"] = "★" * 12
    it.setdefault("server", "简单生存")
    it.setdefault("evidence_level", "static/candidate")
    it.setdefault("status_tags", ["static config"])

core["meta"]["name"] = "异变核芯 · 全量表（12 星）"
core["meta"]["card_mode"] = "roster"
core["meta"]["card_summary"] = [["grade_clean", "品级"], ["star_text", "星上限"], ["weapon_type_display", "武器类型"]]
core["meta"]["field_labels"] = {"skill_desc": "核芯特技", "rank_star_segments": "升星解锁",
                                "desc": "描述", "max_star": "星上限", "server": "服型"}
core["meta"]["filters"] = [{"key": "grade_clean", "label": "品级"},
                           {"key": "weapon_type", "label": "武器类型"},
                           {"key": "server", "label": "服型"}]
core["meta"]["state_summary"] = {
    "核芯": len(core["items"]),
    "12 星上限": len(core["items"]),
}
core["meta"]["note"] = ("核芯只保留这一张表：本体 660xxx + 并入的 76 枚（server/属性类型来自 "
                        "nucleus_build_data kj1）；星上限统一按经典服 12 星展示；卡面默认简略，点击展开详情。")

(B / "mutation_core_full.json").write_text(json.dumps(core, ensure_ascii=False, indent=1), encoding="utf-8")
(B / "mutation_core_full.js").write_text("window.WIKI_BOARD_mutation_core_full = " + json.dumps(core, ensure_ascii=False) + ";\n",
                                          encoding="utf-8")

# 撤掉重复板
for n in ("nucleus.json", "nucleus.js"):
    p = B / n
    if p.is_file():
        p.unlink()
pol = WEB / "data/publication_policy.json"
d = json.loads(pol.read_text(encoding="utf-8"))
d["boards"].pop("nucleus", None)
d["boards"]["mutation_core_full"]["items"] = len(core["items"])
d["boards"]["mutation_core_full"]["reason"] = (
    "核芯唯一总表：common_item 660000 段 132 行 + nucleus_build_data(kj1) 76 枚按名合并；"
    "星上限按经典服 12 星展示；卡面简略、详情展开。")
pol.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
(WEB / "data/publication_policy.js").write_text("window.WIKI_PUBLICATION_POLICY = " + json.dumps(d, ensure_ascii=False) + ";\n",
                                                encoding="utf-8")

print("合并：对齐 %d 条（其中新增 %d）｜ 总表 %d 条" % (enriched, added, len(core["items"])))
