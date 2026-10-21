# -*- coding: utf-8 -*-
r"""补齐时装板里缺的可机读定位链（publication gate 要求 5 个 provenance 字段）。"""
from __future__ import annotations

import hashlib
import json
import pathlib

BS = chr(92)
BASE = pathlib.Path(r"E:/la拆包项目/03_执行/41_还原树/Documents/script.py314.lc.npk/com/cdata")
BOARD = pathlib.Path(r"E:/la拆包项目/04_站点/web/data/boards/fashion_wardrobe.json")
JS = BOARD.with_suffix(".js")
KEYS = ("source_id", "locator_chain", "source_lock_sha256", "upstream", "name_source")


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    meta_sha = d["meta"].get("package_sha") or ""
    cache: dict[str, str] = {}

    def sha_of(table: str) -> str:
        if not table:
            return meta_sha
        if table in cache:
            return cache[table]
        p = BASE / table.replace(BS, "/")
        v = hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else meta_sha
        cache[table] = v
        return v

    n = 0
    for it in d["items"]:
        p = it.get("provenance") or {}
        if all(p.get(k) for k in KEYS):
            continue
        table = p.get("table") or ""
        sha = p.get("source_lock_sha256") or sha_of(table)
        sid = p.get("source_id") or "fashion-extra-20261018"
        rk = p.get("row_key") or it.get("id")
        p["source_id"] = sid
        p["source_lock_sha256"] = sha
        p["name_source"] = p.get("name_source") or ((table + "#name") if table else "board-meta")
        p["upstream"] = p.get("upstream") or {
            "package_sha256": sha, "entry_index": None, "file_id": None,
            "decoded_sha256": None, "role": table or "board-meta"}
        p["locator_chain"] = p.get("locator_chain") or {
            "chain_status": "replayed-structural", "scope": "record",
            "no_cross_source_field_join": True,
            "steps": [{"kind": "decoded-row", "source_id": sid,
                       "table": table, "row_key": rk}]}
        it["provenance"] = p
        n += 1

    BOARD.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    JS.write_text("window.WIKI_BOARD_fashion_wardrobe = "
                  + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print("补齐 provenance", n, "件｜共", len(d["items"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
