# -*- coding: utf-8 -*-
r"""重建时装板的「投影」条目：正确数据源是 body_sfx_data（43 行，buff_item_id 640xxx）。

旧板里的 proj_124979 之类是历史 JSON 的错 id（既不在 buff_data 也不在任何道具表），
本脚本按 PE 源 body_sfx_data 重建，并如实标注「无 desc / 无 charm / 无 2D 图」。
"""
from __future__ import annotations

import json
import pathlib
import struct
import sys


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
WEB = PROJ / "02_wiki/web"
CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402


def main() -> int:
    p = CD / "body_sfx_data.py"
    c = CD / "body_sfx_data_chs.py"
    raw = p.read_bytes()
    at = raw.find(b"x{")
    L = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + L]
    rows, _ = BT.decode_table_rows(body, BT.parse_legacy_chs_pool(c.read_bytes()), resolve_jumps=False)

    def g(r, k):
        v = r["values"].get(k)
        return (v[1] if isinstance(v, tuple) else v) if v else None

    bf = WEB / "data/boards/fashion_wardrobe.json"
    d = json.loads(bf.read_text(encoding="utf-8"))
    # 投影的真实来源是 body_sfx_data（含 chs 名表），单独登记为 supplement source_lock，
    # 不再错挂 fashion_data 的 source_lock（旧写法 provenance 与 locator_chain 的 table 自相矛盾）。
    import hashlib
    def _sha(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()
    proj_base_id = "fashion-projection-body_sfx_data"
    proj_chs_id = "fashion-projection-body_sfx_data-chs"
    locks = d["meta"]["provenance"].setdefault("source_locks", [])
    for _id, _p in ((proj_base_id, p), (proj_chs_id, c)):
        if not any(l.get("source_id") == _id for l in locks):
            st = _p.stat()
            locks.append({
                "source_id": _id, "role": "comparison",
                "path": "01_索引与产物/41_还原树/pe/配置/com/cdata/" + _p.name,
                "sha256": _sha(_p), "bytes": st.st_size,
                "mtime_ns": int(st.st_mtime_ns),
            })
    lock = next(l for l in locks if l["source_id"] == proj_base_id)
    d["items"] = [i for i in d["items"] if i.get("part") != "投影"]

    added = 0
    for r in rows:
        nm = str(g(r, "buff_item_name") or "").strip()
        if not nm:
            continue
        iid = g(r, "buff_item_id")
        d["items"].append({
            "id": "proj_%s" % iid,
            "name": "伴身投影·%s" % nm if not nm.startswith("伴身投影") else nm,
            "item_id": iid,
            "buff_id": g(r, "buff_id"),
            "part": "投影",
            "part_bucket": ["投影"],
            "kind": "投影",
            "grade_level": g(r, "buff_item_level"),
            "desc": None,
            "desc_note": "body_sfx_data 无外观描述字段",
            "charm_value": None,
            "charm_note": "客户端无投影魅力字段",
            "icon_state": "无2D图（特效类）",
            "icon_note": "伴身投影为运行时特效，客户端无独立 2D 图标",
            "icon_count": 0,
            "_media": {"images": [], "total": 0},
            "evidence": "structure",
            "evidence_level": "structure-only",
            "status_tags": ["verified", "static config"],
            "source": "body_sfx_data row=%s（buff_item_id=%s, buff_id=%s）" % (r["key"], iid, g(r, "buff_id")),
            "provenance": {
                "source_id": lock["source_id"], "source_lock_sha256": lock["sha256"],
                "table": "body_sfx_data", "row_key": r["key"],
                "field_refs": ["buff_id", "buff_item_id", "buff_item_name"],
                "name_source": "body_sfx_data.buff_item_name",
                "upstream": {"package_sha256": lock["sha256"], "role": "body_sfx_data"},
                "locator_chain": {"chain_status": "replayed-structural", "scope": "record",
                                  "no_cross_source_field_join": True,
                                  "steps": [{"kind": "decoded-table-row", "source_id": lock["source_id"],
                                             "table": "body_sfx_data", "row_key": r["key"],
                                             "field_refs": ["buff_id", "buff_item_id", "buff_item_name"]}]},
            },
        })
        added += 1

    bf.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/fashion_wardrobe.js").write_text(
        "window.WIKI_BOARD_fashion_wardrobe = " + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";",
        encoding="utf-8")
    print("重建投影条目", added, "｜总条目", len(d["items"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
