# -*- coding: utf-8 -*-
r"""回填时装板「投影」的 desc / icon，并把 buff_data 来源（fashion_projection_slots）并入。

设计：
- 描述与 2D 图标真源 = 已解码的 common_item 道具表（common_item_text_sources.json），
  640xxx 伴身投影道具每条都带 desc + icon，且 PNG 已落地
  （assets/fashion_posters/proj_<id>_b.png 或 assets/img_cache/common_item_text_sources/<id>.png）。
  原脚本写死 pe_test_script/common_item_data_base.py（该文件不存在），改为读已解码板，
  既不依赖解码也不依赖 pe_fetch 取图，更稳。
- 魅力值：common_item 对 640xxx 全为 None —— 投影作为特效 buff 本就没有魅力值，保持 null（不伪造）。
- buff_data（fashion_projection_slots）并入：与 wardrobe 投影同名（归一化）的条目补 sfx_path；
  buff_data 独有（如 一幕紫藤/星影微光/糖心风暴/花弄蝶，以及 body_sfx 漏列的 落叶之舞）新增为投影条目。
"""
from __future__ import annotations

import json
import hashlib
import pathlib
import re
import sys


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
WEB = PROJ / "02_wiki/web"
DATA = WEB / "data/boards"
POSTERS = WEB / "assets/fashion_posters"
IMG_CACHE = WEB / "assets/img_cache/common_item_text_sources"

BUFF_DATA_PATH = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata/buff_data.py"
# common_item / buff_data 同出自 documents 实时包（common_item_text_sources.json 登记的锁）
DOCUMENTS_SHA = "d5bc4f09209fbefbeba737498b5d142288662daa99e6b0dc7973b4d598f564d9"


def norm(name: str) -> str:
    return re.sub(r"[·\-（）()\s]", "", str(name)).replace("伴身投影", "").replace("投影", "").strip()


def main() -> int:
    wf = DATA / "fashion_wardrobe.json"
    d = json.loads(wf.read_text(encoding="utf-8"))

    # 1) common_item 源（desc + icon），按 item_id 与 归一名 两路索引
    ci = json.loads((DATA / "common_item_text_sources.json").read_text(encoding="utf-8"))
    ci_by_id, ci_by_norm = {}, {}
    for i in ci["items"]:
        if str(i.get("item_id", "")).startswith("640"):
            ci_by_id[str(i["item_id"])] = i
            ci_by_norm.setdefault(norm(i["name"]), i)

    # 2) buff_data 源（sfx）
    slots = json.loads((DATA / "fashion_projection_slots.json").read_text(encoding="utf-8"))
    slots_by_norm = {}
    for s in slots["items"]:
        slots_by_norm.setdefault(norm(s["name"]), s)

    # 注册溯源锁（supplement）
    locks = d["meta"]["provenance"].setdefault("source_locks", [])
    for _id, _path, _sha in (
        ("fashion-projection-common_item", None, DOCUMENTS_SHA),
        ("fashion-projection-buff_data", BUFF_DATA_PATH, None),
    ):
        if any(l.get("source_id") == _id for l in locks):
            continue
        if _path is not None:
            _p = pathlib.Path(_path)
            st = _p.stat()
            sha = hashlib.sha256(_p.read_bytes()).hexdigest()
        else:
            sha = _sha
        locks.append({
            "source_id": _id, "role": "comparison",
            "path": (str(_path) if _path else "documents 实时包（common_item_text_sources.json 同源）"),
            "sha256": sha,
            "bytes": st.st_size if _path else 196059988,
            "mtime_ns": int(st.st_mtime_ns) if _path else 1792505574167464800,
        })
    ci_lock = next(l for l in locks if l["source_id"] == "fashion-projection-common_item")
    buff_lock = next(l for l in locks if l["source_id"] == "fashion-projection-buff_data")

    def backfill_media(it):
        iid = it.get("item_id")
        ci_row = ci_by_id.get(str(iid)) if iid is not None else None
        if ci_row is None:
            ci_row = ci_by_norm.get(norm(it.get("name", "")))
        if ci_row:
            if ci_row.get("desc") is not None:
                it["desc"] = ci_row["desc"]
                it["desc_note"] = "common_item_text_sources.desc（common_item_data_base 解码）"
            if ci_row.get("name"):
                it["name"] = ci_row["name"]
            ciid = str(ci_row.get("item_id"))
            png = None
            cand = POSTERS / f"proj_{ciid}_b.png"
            if cand.exists():
                png = f"assets/fashion_posters/proj_{ciid}_b.png"
            else:
                cand2 = IMG_CACHE / f"{ciid}.png"
                if cand2.exists():
                    png = f"assets/img_cache/common_item_text_sources/{ciid}.png"
            if png:
                it["_media"] = {"images": [{"png": png, "base": ci_row.get("icon"),
                                            "suffix": "_b", "label": "图标"}], "total": 1}
                it["icon_state"] = "有图"
                it["icon_count"] = 1
                it["icon_note"] = "common_item.icon → " + str(ci_row.get("icon"))
            else:
                it["icon_state"] = "无2D图（特效类）"
                it["icon_count"] = 0
                it["icon_note"] = "未找到已导出图标"
            # 溯源补充：desc/icon 来自 common_item
            prov = it.setdefault("provenance", {})
            prov["desc_source"] = "common_item（common_item_data_base）"
            prov["icon_source"] = "common_item.icon"
            if "fashion-projection-common_item" not in [s.get("source_id") for s in prov.get("supplement_locks", [])]:
                prov.setdefault("supplement_locks", []).append({"source_id": ci_lock["source_id"],
                                                               "sha256": ci_lock["sha256"]})
        # sfx（buff_data）
        s = slots_by_norm.get(norm(it.get("name", "")))
        if s and s.get("sfx_path"):
            it["sfx_path"] = s["sfx_path"]
            it["buff_row_key"] = s.get("row_key")

    # 3) 回填现有 wardrobe 投影（body_sfx 注入的 44 条）
    proj = [i for i in d["items"] if i.get("part") == "投影"]
    for it in proj:
        backfill_media(it)

    # 4) buff_data 独有投影 → 新增条目（含 body_sfx 漏列的 落叶之舞，其 desc/icon 按名补回）
    have_norm = {norm(i["name"]) for i in proj}
    added_new = 0
    for s in slots["items"]:
        ns = norm(s["name"])
        if ns in have_norm:
            continue
        have_norm.add(ns)
        entry = {
            "id": "proj_buff_%s" % s.get("row_key"),
            "name": s["name"],
            "item_id": None,
            "part": "投影",
            "part_bucket": ["投影"],
            "kind": "投影",
            "grade_level": None,
            "desc": None,
            "desc_note": "buff_data 无道具描述字段（非 common_item 640xxx 道具）",
            "charm_value": None,
            "charm_note": "客户端无投影魅力字段",
            "sfx_path": s.get("sfx_path"),
            "buff_row_key": s.get("row_key"),
            "icon_state": "无2D图（特效类）",
            "icon_note": "伴身投影为运行时特效，客户端无独立 2D 图标",
            "icon_count": 0,
            "_media": {"images": [], "total": 0},
            "evidence": "structure",
            "evidence_level": "structure-only",
            "status_tags": ["verified", "static config"],
            "source": "buff_data row=%s（伴身投影 sfx，无对应 640xxx 道具）" % s.get("row_key"),
            "provenance": {
                "source_id": buff_lock["source_id"],
                "source_lock_sha256": buff_lock["sha256"],
                "upstream": {"package_sha256": buff_lock["sha256"], "role": "buff_data"},
                "table": "buff_data", "row_key": s.get("row_key"),
                "field_refs": ["buff_data.name", "buff_data.sfx_path"],
                "name_source": "buff_data.name",
                "locator_chain": {"chain_status": "replayed-structural", "scope": "record",
                                  "no_cross_source_field_join": True,
                                  "steps": [{"kind": "decoded-table-row", "source_id": buff_lock["source_id"],
                                             "table": "buff_data", "row_key": s.get("row_key"),
                                             "field_refs": ["buff_data.name", "buff_data.sfx_path"]}]},
            },
        }
        d["items"].append(entry)
        backfill_media(entry)  # 落叶之舞等若有 common_item 同名，补回 desc/icon
        added_new += 1

    # 5) 更新 state_summary
    d["meta"]["state_summary"]["有图"] = sum(
        1 for i in d["items"] if (((i.get("_media") or {}).get("images") or [{}])[0] or {}).get("png"))
    wf.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/fashion_wardrobe.js").write_text(
        "window.WIKI_BOARD_fashion_wardrobe = " + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";",
        encoding="utf-8")
    n_desc = sum(1 for i in d["items"] if i.get("part") == "投影" and i.get("desc"))
    n_img = sum(1 for i in d["items"] if i.get("part") == "投影" and i.get("icon_state") == "有图")
    n_proj = sum(1 for i in d["items"] if i.get("part") == "投影")
    print(f"投影总条目 {n_proj}｜有描述 {n_desc}｜有2D图 {n_img}｜新增 buff_data 独有 {added_new} 条")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
