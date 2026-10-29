# -*- coding: utf-8 -*-
"""无人机板：并入经典服（藏宝阁 all_equips 18xxxx 段 285 行）+ 补图。

用户报（2026-10-29）：无人机取的是简单生存服的，不够完整，要经典服 + 详情。

数据现实（如实记录）：
  · 经典服 all_equips_data_base 已在经典服 npk 里定位（entry 11805，1227 行），
    但 0x73 解码出的字段值错位（行 180010 的 target_entity_type 落的是护甲文案），
    逐字段可信回放暂不可得 —— 本工具不使用它。
  · 藏宝阁 all_equips_data.json 是经典服口径的官方静态导出，18xxxx 段 285 行，
    字段 name/desc/icon/level —— 用它做经典服名册并集与文案/品级差异，
    标 provenance=cbg_reference。
  · 简单生存服 49 台（现板）保留全部字段（skills/talents/model/power），
    server_branch=简单生存；新并入卡 server_branch=经典服，仅 CBG 四字段。

用法：--dry / 默认落盘（自动备份）。
"""
from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

WEB = PROJ / "02_wiki/web"
CBG = PROJ / "00_规范与工具/治理/参考资料/藏宝阁_CBG/json/game_auto_config/all_equips_data.json"
BOARD = WEB / "data/boards/drone_catalog.json"
BOARD_JS = WEB / "data/boards/drone_catalog.js"
ICON_DIR = WEB / "assets/drone_icons"

sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"))


def fetch_icon(iid: int, out_dir: pathlib.Path):
    """pe_fetch 三档导出，返回 (rel, suffix) 或 None。"""
    import pe_fetch
    c = pe_fetch.con()
    for suf in ("_b", "_s", ""):
        r = pe_fetch.resolve("ui/item_icon/icon_%d" % iid, suf, c)
        if not r:
            continue
        out = out_dir / ("icon_%d%s.png" % (iid, suf))
        if not out.exists():
            if not pe_fetch.export(r[0], out):
                continue
        return ("assets/drone_icons/" + out.name, suf)
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    board = json.loads(BOARD.read_text(encoding="utf-8"))
    cbg = json.loads(CBG.read_text(encoding="utf-8"))
    classic = {}
    for k, v in cbg.items():
        if not k.startswith("18"):
            continue
        try:
            iid = int(k)
        except ValueError:
            continue
        if not (180000 <= iid <= 189999):
            continue
        classic[iid] = v
    print("经典服 CBG 18xxxx 行", len(classic))

    items = board["items"]
    by_id = {}
    for it in items:
        try:
            by_id[int(it["drone_id"])] = it
        except (KeyError, TypeError, ValueError):
            continue

    st = {"现卡": len(items), "cbg行": len(classic),
          "存量更新": 0, "新增卡": 0, "新卡有图": 0, "存量差异文案": 0}
    # ── 存量：并入经典服差异 ──
    for iid, v in sorted(classic.items()):
        it = by_id.get(iid)
        if it is None:
            continue
        cls = {"name": v.get("name"), "desc": v.get("desc"), "level": v.get("level"),
               "icon": v.get("icon")}
        diff = (it.get("name") != cls["name"]) or ((it.get("desc") or "") != (cls["desc"] or ""))
        if not a.dry:
            it["classic_ref"] = cls
            it["server_branches"] = sorted(set((it.get("server_branches") or []) + ["经典服", "简单生存"]))
            if diff:
                st["存量差异文案"] += 1
        st["存量更新"] += 1

    # ── 新增：仅 CBG 有 ──
    for iid, v in sorted(classic.items()):
        if iid in by_id:
            continue
        st["新增卡"] += 1
        if a.dry:
            continue
        icon = fetch_icon(iid, ICON_DIR)
        media = {"total": 0, "images": [], "missing": []}
        if icon:
            media["images"].append({"png": icon[0], "base": "ui/item_icon/icon_%d" % iid,
                                    "suffix": icon[1], "via": "pe"})
            media["total"] = 1
            st["新卡有图"] += 1
        else:
            media["missing"].append({"base": "ui/item_icon/icon_%d" % iid, "suffix": "_b"})
        card = {
            "id": "drone_%d" % iid,
            "drone_id": iid,
            "name": v.get("name") or ("无人机 %d" % iid),
            "name_status": "resolved",
            "kind": "经典服收录",
            "kind_code": None,
            "grade": None,
            "grade_level": v.get("level"),
            "grade_raw": None,
            "power": None,
            "desc": v.get("desc"),
            "icon": "ui/item_icon/icon_%d" % iid,
            "icon_state": "有图" if icon else "缺图",
            "_media": media,
            "server_branch": "经典服（藏宝阁 all_equips 18xxxx）",
            "server_branches": ["经典服"],
            "skills": [],
            "skills_note": "经典服 all_equips 解码字段错位（0x73），技能/模块字段暂缺，等解码修复",
            "talents": [],
            "evidence": "structure",
            "evidence_level": "static/candidate",
            "source": "CBG all_equips_data.json 18xxxx 段",
            "provenance": {"source_id": "cbg_reference", "note":
                           "经典服口径官方静态导出；仅 name/desc/icon/level 四字段"},
            "status_tags": ["cbg_reference"],
        }
        items.append(card)

    if not a.dry:
        board["meta"]["server_note"] = (
            "机体名册 = 简单生存服 49 台（全字段）∪ 经典服（藏宝阁 CBG all_equips 18xxxx 段 %d 行，"
            "name/desc/icon/level）。经典服 all_equips_data_base 已定位（经典 npk entry 11805）"
            "但 0x73 解码字段错位，技能/模块字段等解码修复后回填。" % len(classic))
        board["meta"]["source_server"] = "简单生存服（全字段）+ 经典服（CBG 名册并集）"
        ts = time.strftime("%Y%m%d_%H%M%S")
        shutil.copy2(BOARD, BOARD.with_name(BOARD.name + ".bak_%s_classic" % ts))
        shutil.copy2(BOARD_JS, BOARD_JS.with_name(BOARD_JS.name + ".bak_%s_classic" % ts))
        BOARD.write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
        BOARD_JS.write_text(
            "window.WIKI_BOARD_drone_catalog = "
            + json.dumps(board, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")
    print(st)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
