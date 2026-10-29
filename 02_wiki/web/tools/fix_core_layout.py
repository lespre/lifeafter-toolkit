import sys
# -*- coding: utf-8 -*-
"""核芯详情整理：品级四档（极品/高级/中级/基础）+ 去重 + 技术信息二次折叠。"""
import json
import pathlib


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import WEB  # noqa: E402
B = WEB / "data/boards"

GRADE = {
    "特级": ("极品", "金", 12),
    "高级": ("高级", "紫", 9),
    "中级": ("中级", "蓝", 5),
    "低级": ("基础", "绿", None),   # 不可升
}

d = json.loads((B / "mutation_core_full.json").read_text(encoding="utf-8"))
for it in d["items"]:
    g = it.get("grade_clean")
    label, color, star = GRADE.get(g, ("中级", "蓝", 5))
    it["grade_name"] = label
    it["grade_color"] = color
    it["max_star"] = star
    it["grade_label"] = ("%s（%s）" % (label, "不可升" if star is None else ("%d 星" % star)))

d["meta"]["name"] = "异变核芯 · 全量表"
d["meta"]["source_server"] = "经典服口径（极品 12 / 高级 9 / 中级 5 / 基础不可升）"
d["meta"]["filters"] = [{"key": "grade_name", "label": "品级"},
                        {"key": "weapon_type", "label": "武器类型"}]
d["meta"]["card_summary"] = [["grade_label", "品级"]]
d["meta"]["note"] = ("核芯唯一总表（common_item 660xxx 段 132 行）。品级：极品（金，12 星）、"
                     "高级（紫，9 星）、中级（蓝，5 星）、基础（绿，不可升）。卡面简略，点开看特技与升星。")
from collections import Counter
c = Counter(it["grade_name"] for it in d["items"])
d["meta"]["state_summary"] = {"核芯": len(d["items"]), "极品": c.get("极品", 0),
                              "高级": c.get("高级", 0), "中级": c.get("中级", 0),
                              "基础": c.get("基础", 0)}
(B / "mutation_core_full.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
(B / "mutation_core_full.js").write_text("window.WIKI_BOARD_mutation_core_full = " + json.dumps(d, ensure_ascii=False) + ";\n",
                                          encoding="utf-8")

# --- board.html：sumKeys 去重 + 技术区二次折叠 ---
p = WEB / "board.html"
s = p.read_text(encoding="utf-8")

old_sum = '''const sumKeys=nucleusMode?new Set(["item_id","grade_clean","skill_icon","skill_desc","weapon_type_display","weapon_type_label","weapon_type_code"]):new Set();'''
new_sum = '''const sumKeys=nucleusMode?new Set(["item_id","grade_clean","grade_name","grade_color","grade_label",
      "max_star","star_text","skill_icon","skill_desc","weapon_type_display","weapon_type_label",
      "weapon_type_code","rank_star_segments","desc"]):new Set();'''
assert old_sum in s
s = s.replace(old_sum, new_sum, 1)

old_block = '''      const det=[];
      if(it.skill_desc)det.push(`<div class="k">核芯特技</div><div class="v nucleus-desc">${richText(it.skill_desc)}</div>`);
      if(it.rank_star_segments&&typeof it.rank_star_segments==="object"){const segs=Object.keys(it.rank_star_segments).sort((a,b)=>Number(a)-Number(b)).map(s=>`<div class="star"><b>${esc(s)}星</b><div class="star-txt">${richText(zhText(String(it.rank_star_segments[s])))}</div></div>`).join("");det.push(`<div class="k">升星解锁</div><div class="v stars">${segs}</div>`);}
      bodyHtml=`<div class="kv">${sum.join("")}<div class="i-detail" hidden><div class="kv">${det.join("")}${rows}</div>`+
        `${referenceSection}${rewardsSection}${poolsSection}${activityPoolRefsSection}${variantSection}${behaviorSection}${childSection}`+
        `${techSection}</div></div>`;'''

new_block = '''      const det=[];
      if(it.skill_desc)det.push(`<div class="k">核芯特技</div><div class="v nucleus-desc">${richText(it.skill_desc)}</div>`);
      if(it.rank_star_segments&&typeof it.rank_star_segments==="object"){const segs=Object.keys(it.rank_star_segments).sort((a,b)=>Number(a)-Number(b)).map(s=>`<div class="star"><b>${esc(s)}星</b><div class="star-txt">${richText(zhText(String(it.rank_star_segments[s])))}</div></div>`).join("");det.push(`<div class="k">升星解锁</div><div class="v stars">${segs}</div>`);}
      if(it.desc)det.push(`<div class="k">描述</div><div class="v nucleus-desc">${richText(zhText(String(it.desc)))}</div>`);
      const techBlock=(rows||techSection||referenceSection)?
        `<details class="tech sub"><summary>技术详情 · 数据来源 / 字段槽位</summary>`+
        `${rows?`<div class="kv">${rows}</div>`:""}${referenceSection}${techSection}</details>`:"";
      const extraBlock=`${rewardsSection}${poolsSection}${activityPoolRefsSection}${variantSection}${behaviorSection}${childSection}`;
      bodyHtml=`<div class="kv">${sum.join("")}<div class="i-detail" hidden><div class="kv">${det.join("")}</div>`+
        `${extraBlock}${techBlock}</div></div>`;'''
assert old_block in s
s = s.replace(old_block, new_block, 1)

if ".grade-pill.g-绿" not in s:
    s = s.replace(".g-蓝{color:#5aa9e6}", ".g-蓝{color:#5aa9e6}.g-绿{color:#7fbf5f}", 1)

p.write_text(s, encoding="utf-8")
print("品级四档 + 详情去重 + 技术区二次折叠 完成", dict(c))
