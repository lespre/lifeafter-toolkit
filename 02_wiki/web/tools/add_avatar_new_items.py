# -*- coding: utf-8 -*-
"""把配置表里新增的名片框条目增量补进 avatar_catalog.json / .js。

★ 为什么增量而不是重建：
  `build_avatar_full.py` 是整体重建，会给每条 items 重新挂「图标」占位，
  把已有 `_media`（Spine 动图引用、边框图、名片背景、内孔数据）全部清空 ——
  清完还得重跑 18 分钟的动图渲染。而这里只缺 3 条新道具，没必要连累老条目。

口径：
  · 数据全部来自 `business_card_scheme_data`（10-30 刷新的那份），不推断、不伪造；
  · 名称取 `item_name`，取不到再查 item_master_full.json，都没有就照实写「（无名称）」；
  · `_media` 留空，交给 build_avatar_frames.py 去取边框 / 背景。

用法：python add_avatar_new_items.py [--apply]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_avatar_full as B  # noqa: E402

CAT = B.WEB / "data/boards/avatar_catalog.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="真正写回（默认只报告）")
    a = ap.parse_args()

    cat = json.loads(CAT.read_text(encoding="utf-8"))
    items = cat["items"]
    cards = [it for it in items if it.get("kind") == "名片框"]
    have = {it["item_id"] for it in cards}
    names = B.load_item_names()
    rows, bad = B.decode(B.TREE / "business_card_scheme_data.py")
    print("配置表名片框行 %d（坏行 %d），板内已有 %d" % (len(rows), len(bad), len(cards)))

    added = []
    for r in rows:
        key = str(r.get("key") or "").strip()
        if not key or key in have:
            continue
        v = r.get("values") or {}
        icon = (B.val(v, "frame_img_path") or "").strip().replace("\\", "/")
        nm = (B.val(v, "item_name") or "").strip() or names.get(key, "")
        added.append({
            "id": "bc_%s" % key,
            "item_id": key,
            "name": nm or "（无名称）",
            "kind": "名片框",
            "server": r.get("__server") or "简单生存",
            "image_path": icon,
            "spine_path": (B.val(v, "spine_path") or "").replace("\\", "/"),
            "resource_path": (B.val(v, "resource_path") or "").replace("\\", "/"),
            "detail_bg": (B.val(v, "detail_bg") or "").replace("\\", "/"),
            "order": B.val(v, "order", 0),
            "evidence": "structure",
            "evidence_level": "static/candidate",
            "status_tags": ["static config"],
            "source": "business_card_scheme_data",
            "provenance": {
                "source_id": "documents-py314-current",
                "source_lock_sha256": B.PACKAGE_SHA,
                "table": "business_card_scheme_data",
                "row_key": key,
                "field_refs": [f for f in ("frame_img_path", "item_name", "order") if f],
                "name_source": "inventory" if nm else "unresolved",
                "upstream": {"package_sha256": B.PACKAGE_SHA, "role": "SuperFashion"},
                "locator_chain": {
                    "chain_status": "replayed-structural",
                    "scope": "record",
                    "no_cross_source_field_join": True,
                    "steps": [{
                        "kind": "decoded-table-row",
                        "source_id": "documents-py314-current",
                        "table": "business_card_scheme_data",
                        "row_key": key,
                        "field_refs": ["frame_img_path", "item_name", "order"],
                    }],
                },
                "table_raw": "business_card_scheme_data",
            },
            "_media": {"images": [], "total": 0},
        })

    print("新增 %d 条:" % len(added))
    for it in added:
        print("   ", it["id"], it["name"], "| 边框", it["image_path"] or "(无)",
              "| 背景", it["resource_path"] or "(无)", "| spine", it["spine_path"] or "(无)")

    if a.apply and added:
        items.extend(added)
        meta = cat["meta"]
        meta["total"] = len(items)
        st = meta.setdefault("state_summary", {})
        st["名片框"] = sum(1 for x in items if x.get("kind") == "名片框")
        CAT.write_text(json.dumps(cat, ensure_ascii=False, indent=1), encoding="utf-8")
        (B.WEB / "data/boards/avatar_catalog.js").write_text(
            "window.WIKI_BOARD_avatar_catalog = " + json.dumps(cat, ensure_ascii=False) + ";\n",
            encoding="utf-8")
        print("已写回 %s（共 %d 条）" % (CAT.name, len(items)))
    elif not added:
        print("没有新增，无需写回")
    else:
        print("试运行，未写回（加 --apply 生效）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
