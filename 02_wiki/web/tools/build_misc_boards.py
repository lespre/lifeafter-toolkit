# -*- coding: utf-8 -*-
r"""补三张表：状态效果(buff_data) / 实体(common_entity_data) / 说明条目(desc_info_data)。"""
from __future__ import annotations

import copy
import datetime
import json
import pathlib
import struct
import sys

PROJ = pathlib.Path(r"E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
from _src import cdata_dir
CD = cdata_dir()
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

REF = json.loads((WEB / "data/boards/lottery_periods.json").read_text(encoding="utf-8"))
TPL = REF["items"][0]["provenance"]
LOCK = REF["meta"]["provenance"]["source_locks"][0]
TODAY = datetime.date.today().isoformat()


def load(stem):
    p = CD / (stem + ".py")
    c = CD / (stem + "_chs.py")
    b = p.read_bytes()
    at = b.find(b"x{")
    L = struct.unpack_from("<I", b, at + 2)[0]
    return BT.decode_table_rows(b[at + 6: at + 6 + L],
                                BT.parse_legacy_chs_pool(c.read_bytes()), resolve_jumps=False)[0]


def g(r, k):
    v = r["values"].get(k)
    return (v[1] if isinstance(v, tuple) else v) if v else None


def save(bid, name, category, summary, labels, notes, items, id_label):
    board = {"meta": {
        "name": name, "category": category, "source_server": "简单生存服（体验服 Documents 快照）",
        "generated": TODAY, "id_label": id_label, "hide_media": True,
        "evidence": "structure", "card_mode": "roster",
        "card_summary": summary, "field_labels": labels,
        "state_summary": {"条目": len(items)},
        "package_sha": LOCK["sha256"], "provenance": copy.deepcopy(REF["meta"]["provenance"]),
        "notes": notes,
    }, "periods": [], "items": items}
    board["meta"]["provenance"]["source_locks"] = [dict(LOCK)]
    (WEB / "data/boards" / (bid + ".json")).write_text(
        json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards" / (bid + ".js")).write_text(
        "window.WIKI_BOARD_" + bid + " = " + json.dumps(board, ensure_ascii=False, indent=1) + ";",
        encoding="utf-8")
    print(bid, len(items))


def prov(row_key, table):
    pr = copy.deepcopy(TPL)
    pr["table"] = table
    pr["row_key"] = row_key
    ch = copy.deepcopy(pr.get("locator_chain") or {})
    ch["steps"] = [{"kind": "decoded-table-row",
                    "source_id": pr.get("source_id", "documents-py314-current"),
                    "table": table, "row_key": row_key, "field_refs": ["name", "desc"]}]
    pr["locator_chain"] = ch
    return pr


def main() -> int:
    # 1) 状态效果
    items = []
    for r in load("buff_data"):
        nm = str(g(r, "name") or g(r, "status_title") or "").strip()
        if not nm:
            continue
        items.append({"id": "buff_%s" % r["key"], "item_id": r["key"], "name": nm,
                      "kind": "状态效果",
                      "desc": str(g(r, "status_content") or "").strip(),
                      "icon": str(g(r, "status_icon") or ""),
                      "buff_type": str(g(r, "type") or ""),
                      "evidence": "structure", "evidence_level": "static/candidate",
                      "status_tags": ["static config"], "source": "buff_data",
                      "provenance": prov(r["key"], "buff_data")})
    save("buff_catalog", "状态效果总表", "二、战力类 / （十一）状态效果",
         [["name", "效果"], ["desc", "说明"]],
         {"item_id": "效果ID", "desc": "说明", "icon": "图标路径", "buff_type": "类型"},
         "一行 = buff_data 一行；纯内部 buff 也在内，说明为空则不显示。", items, "效果ID")

    # 2) 实体
    items = []
    for r in load("common_entity_data"):
        nm = str(g(r, "name") or "").strip()
        if not nm:
            continue
        items.append({"id": "ent_%s" % r["key"], "item_id": r["key"], "name": nm,
                      "kind": "实体", "model_path": str(g(r, "model_path") or ""),
                      "scale": g(r, "scale"),
                      "evidence": "structure", "evidence_level": "static/candidate",
                      "status_tags": ["static config"], "source": "common_entity_data",
                      "provenance": prov(r["key"], "common_entity_data")})
    save("entity_catalog", "实体总表", "四、资料层 / （八）实体",
         [["name", "实体"], ["model_path", "模型"]],
         {"item_id": "实体ID", "model_path": "模型路径", "scale": "缩放"},
         "一行 = common_entity_data 一行；偏内部对象，供检索用。", items, "实体ID")

    # 3) 说明条目
    items = []
    for r in load("desc_info_data"):
        t = str(g(r, "title") or "").strip()
        if not t:
            continue
        items.append({"id": "desc_%s" % r["key"], "item_id": r["key"], "name": t,
                      "kind": "说明", "desc": str(g(r, "desc") or "").strip(),
                      "evidence": "structure", "evidence_level": "static/candidate",
                      "status_tags": ["static config"], "source": "desc_info_data",
                      "provenance": prov(r["key"], "desc_info_data")})
    save("desc_catalog", "说明条目总表", "四、资料层 / （九）说明条目",
         [["name", "标题"], ["desc", "说明"]],
         {"item_id": "条目ID", "desc": "说明"},
         "一行 = desc_info_data 一行（游戏内帮助/提示文案）。", items, "条目ID")

    # 4) 文本与提示（错误码 + 官方公告）
    items = []
    for r in load("error_code_data"):
        txt = str(g(r, "error_content") or "").strip()
        if not txt:
            continue
        items.append({"id": "err_%s" % r["key"], "item_id": r["key"],
                      "name": str(g(r, "error_code") or r["key"]),
                      "kind": "错误码", "desc": txt,
                      "evidence": "structure", "evidence_level": "static/candidate",
                      "status_tags": ["static config"], "source": "error_code_data",
                      "provenance": prov(r["key"], "error_code_data")})
    for r in load("official_accounts_data"):
        t2 = str(g(r, "title") or g(r, "text") or "").strip()
        if not t2:
            continue
        items.append({"id": "acc_%s" % r["key"], "item_id": r["key"], "name": t2,
                      "kind": "官方公告", "desc": str(g(r, "text") or g(r, "short_text") or "").strip(),
                      "evidence": "structure", "evidence_level": "static/candidate",
                      "status_tags": ["static config"], "source": "official_accounts_data",
                      "provenance": prov(r["key"], "official_accounts_data")})
    save("text_notice_catalog", "文本与提示（错误码 / 官方公告）", "四、资料层 / （十）文本与提示",
         [["name", "标题"], ["desc", "内容"]],
         {"item_id": "编号", "desc": "内容", "kind": "类型"},
         "错误码面向开发/排障，官方公告面向玩家推送；两者都不是图鉴物件。", items, "编号")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
