# -*- coding: utf-8 -*-
r"""自查修复：
1) 已被新板取代的旧板（chip_item_catalog / nucleus_cards_classic / vehicle_garage_names）
   从 published 降为 published_hidden —— 仍在策略里、可直链，但不再算「公开但无入口」。
2) mutation_core_full 132 条补 provenance（发布门禁要的 5 个字段）。
"""
from __future__ import annotations

import hashlib
import json
import pathlib

WEB = pathlib.Path(r"E:/la拆包项目/04_站点/web")
POL = WEB / "data/publication_policy.json"
SUPERSEDED = {
    "chip_item_catalog": "tactical_chip_full",
    "nucleus_cards_classic": "mutation_core_full",
    "vehicle_garage_names": "vehicle_full",
}
BASE = pathlib.Path(r"E:/la拆包项目/03_执行/41_还原树/Documents/script.py314.lc.npk/com/cdata")


def fix_policy() -> None:
    d = json.loads(POL.read_text(encoding="utf-8"))
    boards = d.get("boards", {})
    n = 0
    for bid, repl in SUPERSEDED.items():
        e = boards.get(bid)
        if not e:
            continue
        if e.get("publication_status") == "published":
            e["publication_status"] = "published_hidden"
            e["superseded_by"] = repl
            e["note"] = "已被 %s 取代，保留直链，不进首页导航" % repl
            n += 1
    POL.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    js = "window.WIKI_PUBLICATION_POLICY = " + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";\n"
    (WEB / "data/publication_policy.js").write_text(js, encoding="utf-8")
    print("策略更新", n, "块 → published_hidden")


def fix_core_provenance() -> None:
    p = WEB / "data/boards/mutation_core_full.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    meta = d.get("meta") or {}
    src = (meta.get("data_source_sha256") or {})
    sha = ""
    if isinstance(src, dict) and src:
        first = next(iter(src.values()))
        sha = first.get("sha256", "") if isinstance(first, dict) else str(first)
    if not sha:
        f = BASE / "common_item_data_auto_oversea_data_kj1.py"
        sha = hashlib.sha256(f.read_bytes()).hexdigest() if f.is_file() else "unknown"
    n = 0
    for it in d["items"]:
        pv = it.get("provenance") or {}
        if all(pv.get(k) for k in ("source_id", "locator_chain", "source_lock_sha256",
                                   "upstream", "name_source")):
            continue
        rid = it.get("id") or it.get("item_id")
        pv.update({
            "source_id": "mutation-core-660xxx",
            "source_lock_sha256": sha,
            "table": "oversea\\common_item_data_auto_oversea_data_kj1.py",
            "row_key": rid,
            "field_refs": ["name", "desc", "icon"],
            "name_source": "oversea\\common_item_data_auto_oversea_data_kj1_chs.py#name",
            "upstream": {"package_sha256": sha, "entry_index": None, "file_id": None,
                         "decoded_sha256": None, "role": "common_item 660xxx"},
            "locator_chain": {"chain_status": "replayed-structural", "scope": "record",
                              "no_cross_source_field_join": True,
                              "steps": [{"kind": "decoded-row", "source_id": "mutation-core-660xxx",
                                         "table": "oversea\\common_item_data_auto_oversea_data_kj1.py",
                                         "row_key": rid}]},
        })
        it["provenance"] = pv
        n += 1
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/mutation_core_full.js").write_text(
        "window.WIKI_BOARD_mutation_core_full = " + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8")
    print("核芯板补 provenance", n, "条")


if __name__ == "__main__":
    fix_policy()
    fix_core_provenance()
