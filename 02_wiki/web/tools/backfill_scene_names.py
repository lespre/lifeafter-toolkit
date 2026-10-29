# -*- coding: utf-8 -*-
"""把子代理查出的 25 个场景名回填进 scene_balance.json。"""
from __future__ import annotations
import sys

import json
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import ANALYSIS_ROOT  # noqa: E402

OUT = pathlib.Path(ANALYSIS_ROOT / "伤害系统逆向")
bal = OUT / "scene_balance.json"
attr = OUT / "scene_attribution/unnamed_scene_ids/scene_attribution.json"


def main() -> int:
    data = json.loads(bal.read_text(encoding="utf-8"))
    recs = json.loads(attr.read_text(encoding="utf-8"))["records"]
    name = {}
    for r in recs:
        sid = int(r["scene_id"])
        nm = r.get("name") or r.get("space_name")
        if nm:
            name[sid] = nm

    filled = 0
    for x in data:
        sid = int(x["scene_id"])
        if not x.get("name"):
            if sid in name:
                x["name"] = name[sid]
                x["name_source"] = "space_data(lenient)"
                filled += 1
            else:
                x["name"] = None
                x["name_note"] = "space_data 无此 id（预留/未启用）"
    bal.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")

    named = sum(1 for x in data if x.get("name"))
    print("回填", filled, "条；现在有名", named, "/", len(data))
    missing = sorted({int(x["scene_id"]) for x in data if not x.get("name")})
    print("仍无名字", missing)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
