# -*- coding: utf-8 -*-
"""种族潜能板：并入经典服名册差异（池名册级）。

用户报（2026-10-29）：各种族潜能没区分简单生存服和经典服。

数据现实：
  · 板 = gene_node_data(kj1)（简单生存体验服快照）63 行 / 29 个唯一名。
  · 经典服 npk（E:\\LifeAfter\\Documents\\script.py314.lc.npk）里已定位两份
    gene_node_data 字符串池：entry 36574（经典 base，77 个「X潜能:名」）、
    entry 24038（简单生存变体，41 个）—— 池名册可信。
  · 表体暂不可解：0x73 / 76-idx 两种签名全量扫描均未命中表体载荷，
    字段级数值（node_score / effect_desc）等解码突破后回填。

做法：经典池里有、板里没有的名字 → 新增「经典服名册」卡（只有名字+档位，
不猜 race/数值）；板内既有卡标注 server_branches 交集/独有；meta 记录口径。
"""
from __future__ import annotations
import sys

import argparse
import json
import pathlib
import shutil
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

WEB = PROJ / "02_wiki/web"
BOARD = WEB / "data/boards/gene_potential_catalog.json"
BOARD_JS = WEB / "data/boards/gene_potential_catalog.js"
POOLS = WEB / "data/boards/_refs/gene_pools_classic.json"

TIER = ["初级", "中级", "高级", "特级", "超级", "究级"]


def tier_of(name: str):
    for t in TIER:
        if name.startswith(t + "潜能"):
            return t
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    board = json.loads(BOARD.read_text(encoding="utf-8"))
    pools = json.loads(POOLS.read_text(encoding="utf-8"))
    classic = set(pools["36574"])
    kj1 = set(pools["24038"])

    items = board["items"]
    board_names = {x["name"].strip() for x in items}
    st = {"板卡": len(items), "经典名册": len(classic), "存量标注": 0,
          "新增经典卡": 0, "简单生存独有": 0}

    for it in items:
        nm = it["name"].strip()
        branches = ["简单生存"]
        if nm in classic:
            branches.append("经典服")
        elif nm in kj1:
            st["简单生存独有"] += 1
        if not a.dry:
            it["server_branches"] = branches
        st["存量标注"] += 1

    new_names = sorted(classic - board_names)
    for nm in new_names:
        st["新增经典卡"] += 1
        if a.dry:
            continue
        items.append({
            "id": "gene_cls_%d" % (len(items) + 1),
            "name": nm,
            "kind": "种族潜能",
            "tier": tier_of(nm),
            "race": None,
            "race_name": None,
            "level": None,
            "node_score": None,
            "effect_desc": None,
            "server_branch": "经典服（gene_node_data base 池名册）",
            "server_branches": ["经典服"],
            "fields_note": "经典服表体暂不可解（0x73/76-idx 均未命中载荷），"
                           "仅池名册级：名字+档位；race/数值等解码突破后回填",
            "evidence": "structure",
            "evidence_level": "static/candidate",
            "status_tags": ["static config", "name-roster-only"],
            "source": "经典服 npk entry 36574 gene_node_data_chs 池",
            "provenance": {"source_id": "classic-npk-pool",
                           "note": "字符串池名册级证据，非行级解码"},
        })

    if not a.dry:
        board["meta"]["server_note"] = (
            "名册口径：简单生存（gene_node_data kj1，%d 名）∪ 经典服（base 池 %d 名）。"
            "经典服独有 %d 名（特级/超级/究级档为主）；简单生存独有 %d 名。"
            "字段级数值仅简单生存侧有；经典服表体解码突破后回填。"
            % (len(kj1), len(classic), len(new_names), st["简单生存独有"]))
        board["meta"]["source_server"] = "简单生存（字段级）+ 经典服（池名册级，待解码）"
        board["meta"]["field_labels"].update({
            "server_branches": "服型", "tier": "档位", "fields_note": "字段说明"})
        ts = time.strftime("%Y%m%d_%H%M%S")
        shutil.copy2(BOARD, BOARD.with_name(BOARD.name + ".bak_%s_gene" % ts))
        shutil.copy2(BOARD_JS, BOARD_JS.with_name(BOARD_JS.name + ".bak_%s_gene" % ts))
        BOARD.write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
        BOARD_JS.write_text(
            "window.WIKI_BOARD_gene_potential_catalog = "
            + json.dumps(board, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")
    print(st)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
