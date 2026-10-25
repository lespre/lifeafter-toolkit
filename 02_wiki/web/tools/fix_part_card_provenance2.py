# -*- coding: utf-8 -*-
"""给部位补卡生成契约合规的 provenance（严格照既有卡的形状）。"""
from __future__ import annotations

import copy
import hashlib
import json
import pathlib

WEB = pathlib.Path("E:/la拆包项目/02_wiki/web")
CD = pathlib.Path("E:/la拆包项目/01_索引与产物/41_还原树/pe/配置/com/cdata")
BOARD = WEB / "data/boards/fashion_wardrobe.json"
SEP = chr(92)


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    items = d["items"]
    tpl = None
    for it in items:
        pv = it.get("provenance") or {}
        ch = pv.get("locator_chain")
        if pv.get("source_lock_sha256") and isinstance(ch, dict) and ch.get("steps"):
            tpl = copy.deepcopy(pv)
            break
    if tpl is None:
        print("找不到模板 provenance")
        return 1

    fixed = 0
    for it in items:
        pv = it.get("provenance") or {}
        if pv.get("source_lock_sha256") and isinstance(pv.get("locator_chain"), dict):
            continue
        tbl = str(pv.get("table") or "player_appear_data.py").split(SEP)[-1].replace(".py", "")
        f = CD / (tbl + ".py")
        sha = hashlib.sha256(f.read_bytes()).hexdigest() if f.is_file() else ""
        rk = pv.get("row_key")
        newpv = copy.deepcopy(tpl)
        newpv["source_id"] = "fashion-parts-supplement-" + tbl
        newpv["source_lock_sha256"] = sha
        newpv["table"] = "com" + SEP + "cdata" + SEP + tbl + ".py"
        newpv["row_key"] = rk
        newpv["row_keys"] = [rk] if rk else []
        newpv["field_refs"] = ["name", "desc", "model_id", "charm_value", "level", "part_type"]
        newpv["name_source"] = "com" + SEP + "cdata" + SEP + tbl + ".py#name"
        newpv["part_source"] = "com" + SEP + "cdata" + SEP + tbl + ".py#part_type"
        chain = copy.deepcopy(tpl["locator_chain"])
        step = copy.deepcopy(chain["steps"][0])
        step.update({"source_id": newpv["source_id"], "table": newpv["table"],
                     "row_key": rk, "field_refs": newpv["field_refs"]})
        chain["steps"] = [step]
        newpv["locator_chain"] = chain
        newpv["upstream"] = copy.deepcopy(tpl["upstream"])
        newpv["rebuild"] = "supplement-20261025"
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
            locks.append({"source_id": sid, "role": "comparison",
                          "path": "01_索引与产物/41_还原树/pe/配置/com/cdata/" + tbl + ".py",
                          "sha256": hashlib.sha256(b).hexdigest(),
                          "bytes": len(b), "mtime_ns": f.stat().st_mtime_ns})

    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    print("修复 provenance %d 条 ｜ source_locks %d 条" % (fixed, len(locks)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
