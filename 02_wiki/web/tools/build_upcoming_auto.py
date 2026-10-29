# -*- coding: utf-8 -*-
r"""重建「零、新更新与预告」：自动从武器皮肤板 / 奖池板筛「未上架」条目。

口径：
  武器皮肤：release_state in (upcoming, no_sale_field) 或 sale_date > today
  奖池：期次 start > today（未开始），连带该期成员
输出：data/boards/upcoming_auto.json/.js，card_mode=group（按来源分卡）
"""
from __future__ import annotations

import datetime
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

WEB = PROJ / "02_wiki/web"
TODAY = datetime.date.today().isoformat()


def main() -> int:
    skin = json.loads((WEB / "data/boards/weapon_skin_sfx_text_sources.json").read_text(encoding="utf-8"))
    lot = json.loads((WEB / "data/boards/lottery_periods.json").read_text(encoding="utf-8"))

    items = []
    src_skin = 0
    for it in skin["items"]:
        # 2026-10-29：canonical listing_status 覆盖层优先（与 board.html listingOf 口径一致）。
        # 人工订正已上线的皮肤（彩虹过载/全糖暴击，见 mark_skins_listed_manual_20261029.py）
        # 不再进预告专栏；源表 release_state=no_sale_field 是数据源事实，不代表未上线。
        if str(it.get("listing_status") or "") == "on_sale":
            continue
        st = str(it.get("release_state") or "")
        sd = str(it.get("sale_date") or "")
        if st in ("upcoming", "no_sale_field") or (sd and sd > TODAY):
            items.append({
                "id": "up_skin_%s" % it.get("skin_id") or it.get("id"),
                "name": it.get("name_display") or it.get("name"),
                "item_id": it.get("skin_id") or it.get("id"),
                "kind": "武器皮肤",
                "grade": it.get("grade"),
                "weapon_type": it.get("weapon_type_label"),
                "expect_date": sd or "未定",
                "release_state": st or "unknown",
                "family": "武器皮肤（未上线）", "period_id": "up_skin", "period_label": "武器皮肤 · 未上线",
                "family_key": "UpcomingSkin",
                "evidence": it.get("evidence") or "structure",
                "evidence_level": it.get("evidence_level") or "structure-only",
                "status_tags": it.get("status_tags") or ["verified", "static config"],
                "_media": it.get("_media") or {"images": [], "total": 0},
                "icon_state": it.get("icon_state") or ("有图" if ((it.get("_media") or {}).get("images")) else "未下发"),
                "source": "weapon_skin_sfx_text_sources（release_state=%s）" % st,
                "provenance": it.get("provenance"),
            })
            src_skin += 1

    fut = [p for p in lot["periods"] if str(p.get("start") or "") > TODAY]
    by_period = {}
    for it in lot["items"]:
        by_period.setdefault(it["period_id"], []).append(it)

    src_pool = 0
    for per in fut:
        for it in by_period.get(per["period_id"], []):
            items.append({
                "id": "up_pool_%s_%s" % (per["period_id"], it.get("item_id")),
                "name": it.get("name"),
                "item_id": it.get("item_id"),
                "kind": it.get("kind") or "奖池奖励",
                "grade": it.get("grade"),
                "expect_date": per.get("start"),
                "release_state": "upcoming",
                "family": "奖池（未开始）", "period_id": "up_pool_%s" % per["period_id"], "period_label": "%s（%s 起）" % (per.get("label"), per.get("start")),
                "family_key": "UpcomingPool",
                "period_label": per.get("label"),
                "family_src": per.get("family"),
                "evidence": it.get("evidence") or "structure",
                "evidence_level": it.get("evidence_level") or "structure-only",
                "status_tags": it.get("status_tags") or ["verified", "static config"],
                "_media": it.get("_media") or {"images": [], "total": 0},
                "icon_state": it.get("icon_state") or "未下发",
                "source": "lottery_periods · %s" % per.get("label"),
                "provenance": it.get("provenance"),
            })
            src_pool += 1

    # 3) 新活动（huodong 里 start > 今天、且不在奖池板里的）
    import struct as _st
    sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
    from toolkit_core import bindict_table as _BT
    # 表根走 _src（PE → Documents → LA_CDATA_ROOT），不再写死 PE 路径
    from _src import cdata_dir
    CD = cdata_dir("oversea")
    hp = CD / "huodong_conf_data_auto_oversea_data_kj1.py"
    hc = CD / "huodong_conf_data_auto_oversea_data_kj1_chs.py"
    if not hp.exists():
        print("缺表：%s（当前表根 %s）" % (hp.name, CD), file=sys.stderr)
        return 3
    _raw = hp.read_bytes(); _at = _raw.find(b"x{")
    _L = _st.unpack_from("<I", _raw, _at + 2)[0]
    _rows, _ = _BT.decode_table_rows(_raw[_at + 6:_at + 6 + _L],
                                     _BT.parse_legacy_chs_pool(hc.read_bytes()), resolve_jumps=False)

    def _g(r, k):
        v = r["values"].get(k)
        return (v[1] if isinstance(v, tuple) else v) if v else None

    def _day(ts):
        return datetime.datetime.fromtimestamp(ts + 8 * 3600, datetime.UTC).strftime("%Y-%m-%d")             if isinstance(ts, (int, float)) and ts > 1e9 else ""

    known = {str(p.get("activity_id")) for p in lot["periods"] if p.get("activity_id")}
    NEW_ACT = []
    for r in _rows:
        st = _day(_g(r, "start_ts"))
        if not st or st <= TODAY:
            continue
        if str(r["key"]) in known:
            continue
        NEW_ACT.append({"id": "up_act_%s" % r["key"], "name": str(_g(r, "name") or r["key"]),
                        "item_id": r["key"], "kind": "活动",
                        "expect_date": st, "release_state": "upcoming",
                        "family": "新活动（未开始）", "family_key": "UpcomingActivity",
                        "period_id": "up_act", "period_label": "新活动 · 尚未开始",
                        "family_src": str(_g(r, "hd_class") or ""),
                        "evidence": "structure", "evidence_level": "static/candidate",
                        "status_tags": ["static config"],
                        "_media": {"images": [], "total": 0}, "icon_state": "未下发",
                        "source": "huodong_conf(kj1)"})
    import copy as _copy
    _tpl = _copy.deepcopy((lot["items"][0].get("provenance") if lot["items"] else {}) or {})
    for _it in NEW_ACT:
        _p = _copy.deepcopy(_tpl)
        _p["table"] = "huodong_conf_data(kj1)"
        _p["row_key"] = _it["item_id"]
        _ch = dict(_copy.deepcopy(_p.get("locator_chain") or {}))
        _step = dict(((_ch.get("steps") or [{}])[0]))
        _step.update({"kind": "decoded-table-row", "table": "huodong_conf_data(kj1)",
                      "row_key": _it["item_id"], "field_refs": ["name", "start_ts", "hd_class"]})
        _ch.update({"chain_status": "replayed-structural", "scope": "record",
                    "no_cross_source_field_join": True, "steps": [_step]})
        _p["locator_chain"] = _ch
        _it["provenance"] = _p
    items.extend(NEW_ACT)

    meta = dict(lot["meta"])
    meta.update({
        "name": "新更新与预告（自动）",
        "category": "零、新更新与预告专栏（游戏未上线资源预告）",
        "card_mode": "period",
        "card_summary": [["name", "名称"], ["kind", "类型"], ["expect_date", "预计上架"]],
        "state_summary": {"武器皮肤": src_skin, "奖池成员": src_pool,
                          "奖池期次": len(fut), "合计": len(items)},
        "notes": "自动从武器皮肤板与奖池板筛选未上架条目（%s 为界）；不再人工维护预告卡。" % TODAY,
    })
    # provenance 归一：primary=奖池主源(documents)，comparison=皮肤热更源
    lot_lk = (lot["meta"].get("provenance") or {}).get("source_locks", [])[0]
    skin_lk = None
    for lk in (skin["meta"].get("provenance") or {}).get("source_locks", []):
        if lk.get("source_id") != lot_lk.get("source_id") or lk.get("sha256") != lot_lk.get("sha256"):
            skin_lk = lk
            break
    primary = {"source_id": lot_lk["source_id"], "role": "primary", "sha256": lot_lk["sha256"],
               "path": lot_lk.get("path", ""), "bytes": lot_lk.get("bytes", 0), "mtime_ns": 0}
    locks = [primary]
    if skin_lk:
        locks.append({"source_id": skin_lk["source_id"], "role": "comparison",
                      "sha256": skin_lk["sha256"], "path": skin_lk.get("path", ""),
                      "bytes": skin_lk.get("bytes", 0), "mtime_ns": 0})
    meta.setdefault("provenance", {})["source_locks"] = locks
    for it in items:
        prov = dict(it.get("provenance") or {})
        sha = prov.get("source_lock_sha256")
        chosen = next((lk for lk in locks if lk["sha256"] == sha), primary)
        prov["source_id"] = chosen["source_id"]
        prov["source_lock_source_id"] = chosen["source_id"]
        prov["source_lock_sha256"] = chosen["sha256"]
        prov.setdefault("table", it.get("kind") or "lottery")
        prov.setdefault("row_key", it.get("item_id"))
        chain = prov.get("locator_chain") or {}
        steps = chain.get("steps") or []
        if not steps:
            steps = [{"source_id": chosen["source_id"], "kind": "decoded-table-row",
                      "table": prov["table"], "row_key": prov.get("row_key"),
                      "field_refs": ["name", "item_id"]}]
        else:
            for s in steps:
                s["source_id"] = chosen["source_id"]
        chain["steps"] = steps
        chain.setdefault("kind", "table-row")
        prov["locator_chain"] = chain
        it["provenance"] = prov

    
    per_map = {}
    for it in items:
        pid = it["period_id"]
        pg = per_map.setdefault(pid, {"period_id": pid, "label": it.get("period_label") or pid,
                                      "family": it["family"], "family_key": it["family_key"],
                                      "start": it.get("expect_date") if it["family_key"] == "UpcomingPool" else "",
                                      "member_count": 0})
        pg["member_count"] += 1
    out = {"meta": meta, "periods": list(per_map.values()), "items": items}
    p = WEB / "data/boards/upcoming_auto.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/upcoming_auto.js").write_text(
        "window.WIKI_BOARD_upcoming_auto = " + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";",
        encoding="utf-8")
    print("武器皮肤未上线", src_skin, "｜奖池未开始期次", len(fut), "｜奖池成员", src_pool, "｜合计", len(items))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
