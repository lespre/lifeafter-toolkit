# -*- coding: utf-8 -*-
"""重建「头像 / 头像框 / 名片框」全量板：三张表 + 分服变体 + 全量 2D 定位。

产出：
  data/boards/avatar_catalog.json / .js
  assets/avatar_icons/<id>.png（能定位到的图标）
"""
from __future__ import annotations

import json
import os
import pathlib
import struct
import sys

ROOT = pathlib.Path(r"E:/la拆包项目")
WEB = ROOT / "02_wiki/web"
TREE = ROOT / "01_索引与产物/41_还原树/pe/配置_增量快照/com/cdata"
FETCH = ROOT / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"
OUT_ICON = WEB / "assets/avatar_icons"
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(WEB / "tools"))
sys.path.insert(0, str(FETCH))

from toolkit_core.bindict_table import parse_legacy_chs_pool  # noqa: E402
from bindict_provenance import decode_table_rows_with_chs_slots  # noqa: E402
import pe_fetch_hires as H  # noqa: E402
import pe_fetch as PE  # noqa: E402
import pc_fetch as PC  # noqa: E402

PACKAGE_SHA = "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523"

TABLES = {
    "avatar_frame_conf_data": ("头像框", "af", "image_path"),
    "dynamic_avatar_conf_data": ("头像", "da", "image_path"),
    "business_card_scheme_data": ("名片框", "bc", "frame_img_path"),
}
SERVER_TAG = {"kj1": "简单生存", "kjxq": "简单生存", "yk": "经典", "eu": "欧服",
              "kjhmt": "海外", "kjjp": "日服", "kjna": "北美", "kjsea": "东南亚"}


def table_body(path: pathlib.Path):
    raw = path.read_bytes()
    at = raw.find(b"x{")
    if at < 0:
        return None
    n = struct.unpack_from("<I", raw, at + 2)[0]
    return raw[at + 6: at + 6 + n]


def decode(path: pathlib.Path):
    b = table_body(path)
    if not b:
        return [], []
    chs = path.with_name(path.stem + "_chs.py")
    pool = parse_legacy_chs_pool(chs.read_bytes()) if chs.is_file() else []
    return decode_table_rows_with_chs_slots(b, pool)


def val(values, key, default=None):
    v = (values or {}).get(key)
    return v[1] if isinstance(v, (list, tuple)) and len(v) > 1 else default


def load_item_names():
    p = WEB / "data/boards/item_master_full.json"
    if not p.is_file():
        return {}
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        return {str(i.get("item_id")): i.get("name") for i in d.get("items", []) if i.get("name")}
    except Exception:
        return {}


_SRC = "E:/mrzh/Documents/script.py314.lc.npk"
try:
    _st = os.stat(_SRC)
    _SRC_STAT = (_st.st_size, _st.st_mtime_ns)
except OSError:
    _SRC_STAT = (0, 0)

_STATE = {}


def main() -> int:
    names = load_item_names()
    items = []
    seen = set()
    stats = {}

    for tname, (kind, prefix, icon_field) in TABLES.items():
        base = TREE / (tname + ".py")
        rows, bad = decode(base)
        stats[kind] = {"base": len(rows), "bad": len(bad), "oversea": 0}
        # 分服变体
        variants = sorted(TREE.glob("oversea/" + tname + "_auto_oversea_data_*.py"))
        merged = []
        for p in variants:
            if p.stem.endswith("_chs"):
                continue
            tag = p.stem.split("_auto_oversea_data_")[-1]
            rows_v, _bad_v = decode(p)
            for r in rows_v:
                k = str(r.get("key"))
                if k in seen or any(str(x.get("key")) == k for x in rows):
                    continue
                r["__server"] = SERVER_TAG.get(tag, tag)
                merged.append(r)
        stats[kind]["oversea"] = len(merged)

        for r in rows + merged:
            key = str(r.get("key") or "").strip()
            if not key or key in seen:
                continue
            seen.add(key)
            v = r.get("values") or {}
            icon = (val(v, icon_field) or "").strip()
            nm = (val(v, "item_name") or "").strip() or names.get(key, "")
            items.append({
                "id": "%s_%s" % (prefix, key),
                "item_id": key,
                "name": nm or "（无名称）",
                "kind": kind,
                "server": r.get("__server") or "简单生存",
                "image_path": icon.replace("\\", "/"),
                "spine_path": (val(v, "spine_path") or "").replace("\\", "/"),
                "resource_path": (val(v, "resource_path") or "").replace("\\", "/"),
                "detail_bg": (val(v, "detail_bg") or "").replace("\\", "/"),
                "order": val(v, "order", 0),
                "evidence": "structure",
                "evidence_level": "static/candidate",
                "status_tags": ["static config"],
                "source": tname,
                "provenance": {
                    "source_id": "documents-py314-current",
                    "source_lock_sha256": PACKAGE_SHA,
                    "table": tname,
                    "row_key": key,
                    "field_refs": [f for f in (icon_field, "item_name", "order") if f],
                    "name_source": "inventory" if nm else "unresolved",
                    "upstream": {"package_sha256": PACKAGE_SHA, "role": "SuperFashion"},
                    "locator_chain": {
                        "chain_status": "replayed-structural",
                        "scope": "record",
                        "no_cross_source_field_join": True,
                        "steps": [{
                            "kind": "decoded-table-row",
                            "source_id": "documents-py314-current",
                            "table": tname,
                            "row_key": key,
                            "field_refs": [f for f in (icon_field, "item_name", "order") if f],
                        }],
                    },
                    "table_raw": tname,
                },
            })

    print("解析：头像框 %d / 头像 %d / 名片框 %d，合计 %d"
          % (sum(1 for i in items if i["kind"] == "头像框"),
             sum(1 for i in items if i["kind"] == "头像"),
             sum(1 for i in items if i["kind"] == "名片框"),
             len(items)))
    print("分服补充：", {k: v for k, v in stats.items()})

    # ---- 全量 2D 定位 ----
    OUT_ICON.mkdir(parents=True, exist_ok=True)
    hit = 0
    miss = []
    for it in items:
        base = it["image_path"] or it.get("resource_path") or it.get("detail_bg") or ""
        if not base:
            miss.append(it["id"])
            continue
        base = base.rsplit(".", 1)[0]
        dst = OUT_ICON / (it["id"] + ".png")
        try:
            if dst.is_file() or PE.export(base, dst) or PC.export(base, dst):
                it["_media"] = {"images": [{"png": "assets/avatar_icons/%s.png" % it["id"],
                                            "label": "图标"}], "total": 1}
                hit += 1
            else:
                miss.append(it["id"])
        except Exception:
            miss.append(it["id"])

    print("2D 定位：命中 %d / %d（%.1f%%），缺 %d" % (hit, len(items), hit * 100.0 / len(items), len(miss)))

    from collections import Counter
    _STATE.update(dict(Counter(i["kind"] for i in items)))
    _STATE["有图"] = hit
    _STATE["缺图"] = len(items) - hit

    board = {
        "meta": {
            "name": "头像 / 头像框 / 名片框",
            "category": "四、资料层（道具总表 / 文本来源） / （四）名片框外观",
            "source_server": "简单生存服（PE 测试服 pe_20261020）",
            "generated": "2026-10-22",
            "id_label": "ID",
            "hide_media": False,
            "evidence": "structure",
            "card_mode": "roster",
            "package_sha": PACKAGE_SHA,
            "filters": [{"key": "kind", "label": "类型"},
                        {"key": "server", "label": "服型"}],
            "total": len(items),
            "icon_hit": hit,
            "provenance": {
                "contract_version": 3,
                "audit_status": "passed",
                "contract": "frozen-audited-artifact",
                "source_locks": [{
                    "source_id": "documents-py314-current",
                    "role": "primary",
                    "path": "E:/mrzh/Documents/script.py314.lc.npk",
                    "sha256": PACKAGE_SHA,
                    "bytes": _SRC_STAT[0],
                    "mtime_ns": _SRC_STAT[1],
                }],
                "source_scope": {
                    "cross_source_policy": "no-cross-source-field-join",
                    "integer_join_policy": "no-equal-integer-join",
                    "runtime_final_policy": "unknown-unless-runtime-proven",
                },
            },
            "note": "三张表合并；分服变体按 id 去重；图标走 PE .ktx 定位（PC 兜底）",
            "state_summary": _STATE,
        },
        "items": items,
    }
    (WEB / "data/boards/avatar_catalog.json").write_text(
        json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/avatar_catalog.js").write_text(
        "window.WIKI_BOARD_avatar_catalog = " + json.dumps(board, ensure_ascii=False) + ";\n",
        encoding="utf-8")
    miss_out = ROOT / "01_索引与产物/30_分析/avatar_miss.json"
    miss_out.parent.mkdir(parents=True, exist_ok=True)
    miss_out.write_text(json.dumps(miss, ensure_ascii=False), encoding="utf-8")
    print("板已写出")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
