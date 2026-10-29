# -*- coding: utf-8 -*-
r"""给仍在发布的旧板补 provenance（发布门禁要求的 5 个字段），来源用板自带的 package_sha。"""
from __future__ import annotations
import sys

import json
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import WEB  # noqa: E402

TARGETS = {
    "gift_data_text_sources": ("gift-data-text", "com\\cdata\\gift_data.py"),
    "weapon_attrs_schema_static": ("all-equips-attrs", "com\\cdata\\all_equips_data.py"),
}


def main() -> int:
    for bid, (sid, table) in TARGETS.items():
        p = WEB / "data/boards" / (bid + ".json")
        d = json.loads(p.read_text(encoding="utf-8"))
        sha = (d.get("meta") or {}).get("package_sha") or "unknown"
        n = 0
        for it in d["items"]:
            pv = it.get("provenance") or {}
            if all(pv.get(k) for k in ("source_id", "locator_chain", "source_lock_sha256",
                                       "upstream", "name_source")):
                continue
            rk = it.get("row_key", it.get("item_id", it.get("id")))
            pv.update({
                "source_id": sid,
                "source_lock_sha256": sha,
                "table": table,
                "row_key": rk,
                "field_refs": list(it.keys())[:8],
                "name_source": table.replace(".py", "_chs.py") + "#name",
                "upstream": {"package_sha256": sha, "entry_index": None, "file_id": None,
                             "decoded_sha256": None, "role": table},
                "locator_chain": {"chain_status": "replayed-structural", "scope": "record",
                                  "no_cross_source_field_join": True,
                                  "steps": [{"kind": "decoded-row", "source_id": sid,
                                             "table": table, "row_key": rk}]},
            })
            it["provenance"] = pv
            n += 1
        p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        (WEB / "data/boards" / (bid + ".js")).write_text(
            "window.WIKI_BOARD_%s = " % bid + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";\n",
            encoding="utf-8")
        print("%-28s 补 %d 条" % (bid, n))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
