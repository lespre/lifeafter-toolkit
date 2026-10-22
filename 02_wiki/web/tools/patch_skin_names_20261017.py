# -*- coding: utf-8 -*-
r"""把本批武器的**验证名 + 真值字段**写进看板  weapon_skin_sfx_text_sources。

口径（照项目规矩）：
· 名字只认「common_item_data_base 行 key == skin_id」这一条来源（38,571 条索引已命中）
  —— 之前那个「星魂追光」是礼包描述旁证（candidate），这次降级/替换为正式名。
· weapon_type / level / sale_ts 来自 weapon_skin_data 行真值（同一份表解出来的）。
· 1110189 没有主表行：只写「喷火器（由特效路径 skin_1013_* 推定）」，标 inferred，不给假名。
写盘：.json + .js 同步；先备份。
"""
from __future__ import annotations

import datetime
import json
import pathlib
import shutil

WEB = pathlib.Path(r"E:/la拆包项目/02_wiki/web")
BOARD = WEB / "data/boards/weapon_skin_sfx_text_sources.json"
JS = BOARD.with_suffix(".js")

WT = {1: "突击步枪", 3: "弓箭", 4: "霰弹枪", 5: "狙击枪", 6: "手枪",
      7: "榴弹炮", 8: "电磁机枪", 20: "喷火器", 50: "冷兵器", 51: "护臂/盾"}

UPD = {
    1110188: dict(name="一魂共鸣", wt=1, level=5, sale=1792598400,
                  model="weapon/skin/skin_1001_017/skin_1001_017.gim",
                  tex=["skin_1001_017001a.tga", "skin_1001_017001m.tga",
                       "skin_1001_017001n.tga", "skin_1001_017001s_m.tga",
                       "skin_1001_017_1001a.tga", "car_flake.tga"]),
    1110191: dict(name="紧急预案", wt=6, level=2, sale=1792598400,
                  model="weapon/skin/skin_1003_013/skin_1003_013.gim", tex=[]),
    1110192: dict(name="第十三页", wt=8, level=4, sale=1792598400,
                  model="weapon/skin/skin_1008_007/skin_1008_007.gim", tex=[]),
    1110189: dict(name=None, wt=None, level=None, sale=None, model="", tex=[],
                  note="行为资源行（无主表父行/无道具行/无模型）；特效路径 skin_1013_010"),
}

data = json.loads(BOARD.read_text(encoding="utf-8"))
ts = datetime.date.today().strftime("%Y%m%d")
shutil.copy2(BOARD, BOARD.with_suffix(".json.bak_namefix_%s" % ts))
shutil.copy2(JS, JS.with_suffix(".js.bak_namefix_%s" % ts))

changed = []
for it in data["items"]:
    sid = int(it.get("skin_id") or it.get("id") or 0)
    u = UPD.get(sid)
    if not u:
        continue
    if u["name"]:
        it["name"] = u["name"]
        it["name_display"] = u["name"]
        it["name_status"] = "verified"
        it["official_name_status"] = "item_row_match"
        it["name_status_note"] = "common_item_data_base 行 key == skin_id（索引 38,571 条命中）"
        it["name_resolution"] = {
            "state": "verified_from_item_row",
            "name": u["name"],
            "rule": "名字只认同快照道具行（key==skin_id）；礼包描述旁证不采用",
            "evidence": "01_索引与产物/10_索引/items/common_item_names.json → items['%d'].name" % sid,
        }
        it.pop("candidate_name", None)
    if u["wt"]:
        it["weapon_type"] = u["wt"]
        it["weapon_type_label"] = "%s（%d）" % (WT.get(u["wt"], "?"), u["wt"])
        it["weapon_type_status"] = "verified"
    elif sid == 1110189:
        it["weapon_type_label"] = "喷火器（20）· 由特效路径 skin_1013_* 推定"
        it["weapon_type_status"] = "inferred_from_sfx_path"
    if u["level"]:
        it["level"] = u["level"]
    if u["sale"]:
        it["sale_ts"] = u["sale"]
        it["sale_date"] = datetime.datetime.fromtimestamp(
            u["sale"], datetime.timezone(datetime.timedelta(hours=8))).strftime("%Y-%m-%d")
    if u.get("model"):
        it["model_path"] = u["model"]
    if u["tex"]:
        it["textures"] = u["tex"]
    if u.get("note"):
        it["hotfix_note"] = u["note"]
    it["hotfix_batch"] = "20261016_213554_playertest_newpc"
    changed.append(sid)

data.setdefault("meta", {})
data["meta"]["names_updated_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
data["meta"]["names_source"] = "common_item_data_base（key==skin_id）+ weapon_skin_data 行真值"

BOARD.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
JS.write_text("window.WIKI_BOARD_weapon_skin_sfx_text_sources = "
              + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n",
              encoding="utf-8")
print("更新条目：", changed, "｜总条目", len(data["items"]))
for it in data["items"]:
    if int(it.get("skin_id") or 0) in UPD:
        print("   %-9s %-14s %-22s level=%s sale=%s" %
              (it.get("skin_id"), it.get("name_display"), it.get("weapon_type_label"),
               it.get("level"), it.get("sale_date")))
