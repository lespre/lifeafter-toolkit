# -*- coding: utf-8 -*-
r"""补齐文字表板块：称号 / 头像（框+动态）/ 技能。

统一口径：一行 = 表里一行；卡面只放中文摘要，溯源/原始字段折进技术详情。
"""
from __future__ import annotations

import copy
import json
import pathlib
import struct
import sys


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
WEB = PROJ / "02_wiki/web"
from _src import cdata_dir
CD = cdata_dir()
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

REF = json.loads((WEB / "data/boards/lottery_periods.json").read_text(encoding="utf-8"))
TPL_PROV = REF["items"][0]["provenance"]


def decode(stem: str):
    p = CD / (stem + ".py")
    c = CD / (stem + "_chs.py")
    if not (p.is_file() and c.is_file()):
        return []
    raw = p.read_bytes()
    at = raw.find(b"x{")
    if at < 0:
        return []
    L = struct.unpack_from("<I", raw, at + 2)[0]
    rows, _ = BT.decode_table_rows(raw[at + 6: at + 6 + L],
                                   BT.parse_legacy_chs_pool(c.read_bytes()), resolve_jumps=False)
    return rows


def g(r, k):
    v = r["values"].get(k)
    return (v[1] if isinstance(v, tuple) else v) if v else None


def prov(row_key, table):
    pr = copy.deepcopy(TPL_PROV)
    pr["table"] = table
    pr["row_key"] = row_key
    pr["field_refs"] = ["name", "desc"]
    ch = copy.deepcopy(pr.get("locator_chain") or {})
    ch["steps"] = [{"kind": "decoded-table-row",
                    "source_id": pr.get("source_id", "documents-py314-current"),
                    "table": table, "row_key": row_key, "field_refs": ["name", "desc"]}]
    pr["locator_chain"] = ch
    return pr


def make_board(name, category, items, summary, labels, notes, id_label="道具ID"):
    return {
        "meta": {
            "name": name, "category": category, "generated": "", "id_label": id_label,
            "source_server": "简单生存服（体验服 Documents 快照）",
            "evidence": "structure", "card_mode": "roster", "hide_media": True,
            "card_summary": summary, "field_labels": labels,
            "state_summary": {"条目": len(items)},
            "provenance": {"source_locks": [{"source_id": "documents-py314-current",
                                             "role": "primary", "sha256": "",
                                             "bytes": 0, "mtime_ns": 0}]},
            "notes": notes,
        },
        "periods": [],
        "items": items,
    }


def save(board, bid):
    ref = json.loads((WEB / "data/boards/lottery_periods.json").read_text(encoding="utf-8"))
    lock = ref["meta"]["provenance"]["source_locks"][0]
    board["meta"]["package_sha"] = lock["sha256"]
    board["meta"]["provenance"] = copy.deepcopy(ref["meta"]["provenance"])
    board["meta"]["provenance"]["source_locks"] = [dict(lock)]
    (WEB / "data/boards" / (bid + ".json")).write_text(
        json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards" / (bid + ".js")).write_text(
        "window.WIKI_BOARD_" + bid + " = " + json.dumps(board, ensure_ascii=False, indent=1) + ";",
        encoding="utf-8")
    print(bid, len(board["items"]))


def main() -> int:
    # 称号
    # 2026-11-01：补齐「档位 / 颜色 / 动态 / 艺术字」四项，全部来自 title_conf_data 自身字段或同源资源，
    # 不做跨表推断：
    #   style            → 档位 1-8（源表字段；1/2/3 对应初/中/高级职业称号，4+ 为特殊称号）
    #   style + 贴图色   → 颜色（ui/chenghao_icon/img_chenghao_line_N、bg_N 已解码：1 蓝 / 2 紫 / 3 金 / 4 红 / 8 绿）
    #   shining_style    → 动态；319 条全部命中 shining_title_conf_data.key，取其 cocos_csb 动画文件
    #   style_icon / normal_name_icon → 艺术字（称号名美术字图，png 路径）
    # 无对应贴图的档位（5/6/7）颜色留空，不猜。
    shining = {r["key"]: r for r in decode("shining_title_conf_data")}

    def sval(r, k):
        v = r["values"].get(k)
        return v[1] if isinstance(v, tuple) else v

    style_color = {1: "蓝", 2: "紫", 3: "金", 4: "红", 8: "绿"}
    items = []
    for r in decode("title_conf_data"):
        nm = str(g(r, "name") or "").strip()
        if not nm:
            continue
        st = g(r, "style")
        st = int(st) if st not in (None, "") else None
        col = style_color.get(st, "") if st else ""
        ss = g(r, "shining_style")
        anim = ""
        if ss not in (None, "") and int(ss) in shining:
            anim = str(sval(shining[int(ss)], "cocos_csb") or "")
        art = str(g(r, "style_icon") or g(r, "normal_name_icon") or "")
        flags = []
        if anim:
            flags.append("动态")
        if art:
            flags.append("美术字")
        items.append({"id": "title_%s" % r["key"], "item_id": r["key"], "name": nm,
                      "kind": "称号", "desc": str(g(r, "desc") or "").strip(),
                      "obtain": str(g(r, "quest") or ""),
                      "style": st, "color": col, "flags": flags,
                      "anim_csb": anim, "art_icon": art,
                      "evidence": "structure", "evidence_level": "static/candidate",
                      "status_tags": ["static config"],
                      "source": "title_conf_data", "provenance": prov(r["key"], "title_conf_data")})
    save(make_board("（内测版）称号总表", "四、资料层 / （四）称号", items,
                    [["name", "称号"], ["desc", "说明"]],
                    {"item_id": "称号ID", "obtain": "获取条件", "desc": "说明",
                     "style": "档位", "color": "颜色", "flags": "特性",
                     "anim_csb": "动态动画资源", "art_icon": "艺术字资源"},
                    "一行 = title_conf_data 一行；获取条件为客户端 quest 键名（技术详情）。"
                    "档位=style（1-8）；颜色按 style 对应贴图（ui/chenghao_icon/img_chenghao_line_N、bg_N）实测："
                    "1 蓝 / 2 紫 / 3 金 / 4 红 / 8 绿，5-7 无贴图留空；"
                    "动态=shining_style 命中 shining_title_conf_data 的 cocos 动画；"
                    "美术字=style_icon / normal_name_icon 指向的称号名图。",
                     id_label="称号ID"), "title_catalog")

    # 头像框 + 动态头像
    items = []
    for stem, kind, prefix in (("avatar_frame_conf_data", "头像框", "af"),
                               ("dynamic_avatar_conf_data", "动态头像", "da")):
        for r in decode(stem):
            nm = str(g(r, "item_name") or "").strip()
            if not nm:
                continue
            items.append({"id": "%s_%s" % (prefix, r["key"]), "item_id": r["key"], "name": nm,
                          "kind": kind, "image_path": str(g(r, "image_path") or ""),
                          "order": g(r, "order"),
                          "evidence": "structure", "evidence_level": "static/candidate",
                          "status_tags": ["static config"],
                          "source": stem, "provenance": prov(r["key"], stem)})
    save(make_board("头像总表（头像框 / 动态头像）", "四、资料层 / （五）头像", items,
                    [["name", "名称"], ["kind", "类型"]],
                    {"item_id": "头像ID", "kind": "类型", "image_path": "图像资源", "order": "排序"},
                    "头像框与动态头像合表，按来源表区分类型。", id_label="头像ID"), "avatar_catalog")

    # 技能
    items = []
    for r in decode("skill_data"):
        nm = str(g(r, "name") or "").strip()
        if not nm:
            continue
        items.append({"id": "skill_%s" % r["key"], "item_id": r["key"], "name": nm,
                      "kind": "技能", "skill_type": str(g(r, "type") or ""),
                      "weapon_type": str(g(r, "weapon_type") or ""),
                      "cd": g(r, "cd"), "skill_range": g(r, "range"),
                      "evidence": "structure", "evidence_level": "static/candidate",
                      "status_tags": ["static config"],
                      "source": "skill_data", "provenance": prov(r["key"], "skill_data")})
    save(make_board("技能总表", "二、战力类 / （七）技能", items,
                    [["name", "技能"], ["kind", "类别"]],
                    {"item_id": "技能ID", "skill_type": "类型", "weapon_type": "武器类型",
                     "cd": "冷却", "skill_range": "射程"},
                    "一行 = skill_data 一行；冷却/射程为客户端数值。", id_label="技能ID"), "skill_catalog")

    # 天赋
    items = []
    for r in decode("new_talent_data"):
        nm = str(g(r, "name") or "").strip()
        if not nm:
            continue
        items.append({"id": "talent_%s" % r["key"], "item_id": r["key"], "name": nm,
                      "kind": "天赋", "desc": str(g(r, "desc") or "").strip(),
                      "level": g(r, "level"),
                      "evidence": "structure", "evidence_level": "static/candidate",
                      "status_tags": ["static config"], "source": "new_talent_data",
                      "provenance": prov(r["key"], "new_talent_data")})
    save(make_board("天赋总表", "二、战力类 / （八）天赋", items,
                    [["name", "天赋"], ["desc", "说明"]],
                    {"item_id": "天赋ID", "desc": "说明", "level": "等级"},
                    "一行 = new_talent_data 一行；图标字段在技术详情。", id_label="天赋ID"),
         "talent_catalog")

    # 可食用物品
    items = []
    for r in decode("edible_item_data"):
        nm = str(g(r, "name") or "").strip()
        if not nm:
            continue
        items.append({"id": "edible_%s" % r["key"], "item_id": r["key"], "name": nm,
                      "kind": "可食用", "desc": str(g(r, "desc") or "").strip(),
                      "level": g(r, "level"),
                      "evidence": "structure", "evidence_level": "static/candidate",
                      "status_tags": ["static config"], "source": "edible_item_data",
                      "provenance": prov(r["key"], "edible_item_data")})
    save(make_board("可食用物品总表", "二、战力类 / （九）可食用物品", items,
                    [["name", "名称"], ["desc", "说明"]],
                    {"item_id": "物品ID", "desc": "说明", "level": "等级"},
                    "一行 = edible_item_data 一行。", id_label="物品ID"),
         "edible_catalog")

    # 图鉴收集
    items = []
    for r in decode("illustration_collect_item_data"):
        nm = str(g(r, "name") or "").strip()
        if not nm:
            continue
        items.append({"id": "illus_%s" % r["key"], "item_id": r["key"], "name": nm,
                      "kind": "图鉴", "desc": str(g(r, "desc") or "").strip(),
                      "extra_desc": str(g(r, "extra_desc") or "").strip(),
                      "evidence": "structure", "evidence_level": "static/candidate",
                      "status_tags": ["static config"], "source": "illustration_collect_item_data",
                      "provenance": prov(r["key"], "illustration_collect_item_data")})
    save(make_board("图鉴收集总表", "四、资料层 / （六）图鉴收集", items,
                    [["name", "条目"], ["desc", "说明"]],
                    {"item_id": "条目ID", "desc": "说明", "extra_desc": "补充"},
                    "一行 = illustration_collect_item_data 一行。", id_label="条目ID"),
         "illustration_catalog")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
