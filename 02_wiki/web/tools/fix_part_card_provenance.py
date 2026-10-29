# -*- coding: utf-8 -*-
"""补齐部位补卡的 provenance（契约要求 source_id / locator_chain / source_lock_sha256 / upstream）。"""
from __future__ import annotations
import sys

import hashlib
import json
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import TREE_ROOT, WEB  # noqa: E402

CD = pathlib.Path(TREE_ROOT / "pe/配置/com/cdata")
BOARD = WEB / "data/boards/fashion_wardrobe.json"
SEP = chr(92)


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    items = d["items"]
    import copy
    tpl = None
    for it in items:
        pv = it.get("provenance") or {}
        if pv.get("source_lock_sha256") and isinstance(pv.get("locator_chain"), dict)                 and pv["locator_chain"].get("steps") and isinstance(pv.get("upstream"), dict)                 and isinstance(pv["upstream"].get("file_id"), int):
            tpl = copy.deepcopy(pv)
            break
    fixed = 0
    for it in items:
        pv = it.get("provenance") or {}
        if pv.get("source_lock_sha256") and pv.get("locator_chain"):
            continue
        tbl = str(pv.get("table") or "player_appear_data.py")
        tbl = tbl.split(SEP)[-1].replace(".py", "")
        f = CD / (tbl + ".py")
        sha = hashlib.sha256(f.read_bytes()).hexdigest() if f.is_file() else ""
        rk = pv.get("row_key")
        newpv = copy.deepcopy(tpl) if tpl else {}
        newpv.update({
            "source_id": "fashion-parts-supplement-" + tbl,
            "source_lock_sha256": sha,
            "table": "com" + SEP + "cdata" + SEP + tbl + ".py",
            "row_key": rk,
            "row_keys": [rk] if rk else [],
            "field_refs": ["name", "desc", "model_id", "charm_value", "level", "part_type"],
            "name_source": "com" + SEP + "cdata" + SEP + tbl + ".py#name",
            "part_source": "com" + SEP + "cdata" + SEP + tbl + ".py#part_type",
            "locator_chain": {"chain_status": "complete",
                              "steps": [{"kind": "table", "ref": tbl + ".py"},
                                        {"kind": "row", "ref": str(rk)},
                                        {"kind": "name", "ref": str(it.get("name"))}]},
            "upstream": {"package_sha256": sha, "entry_index": 0, "file_id": 0,
                         "decoded_sha256": None, "note": "配置行定位，非容器条目，entry_index/file_id 记 0"},
            "rebuild": "supplement-20261025",
        })
        it["provenance"] = newpv
        fixed += 1
    meta = d.setdefault("meta", {})
    locks = meta.setdefault("provenance", {}).setdefault("source_locks", [])
    have = {l.get("source_id") for l in locks if isinstance(l, dict)}
    for tbl in ("player_appear_data", "simple_fashion_data"):
        f = CD / (tbl + ".py")
        sid = "fashion-parts-supplement-" + tbl
        if f.is_file() and sid not in have:
            b = f.read_bytes()
            locks.append({"source_id": sid, "role": "supplementary",
                          "path": "01_索引与产物/41_还原树/pe/配置/com/cdata/" + tbl + ".py",
                          "sha256": hashlib.sha256(b).hexdigest(),
                          "bytes": len(b), "mtime_ns": f.stat().st_mtime_ns})
    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    print("修复 provenance %d 条" % fixed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
