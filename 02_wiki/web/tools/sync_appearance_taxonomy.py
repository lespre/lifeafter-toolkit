# -*- coding: utf-8 -*-
"""taxonomy / publication_policy / board_builders 同步：去掉（六）其他外观，加捏脸·戒指·花苞。"""
from __future__ import annotations
import sys

import json
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

ROOT = pathlib.Path(PROJ)
D = ROOT / "02_wiki/web/data"

NEW = [
    {"name": "（六）捏脸", "boards": ["appearance_face"]},
    {"name": "（七）戒指", "boards": ["appearance_ring"]},
    {"name": "（八）半感染者花苞", "boards": ["appearance_bud"]},
]


def main() -> int:
    t = json.loads((D / "wiki_taxonomy.json").read_text(encoding="utf-8"))
    for node in t["树"]:
        kids = node.get("children") or []
        if not any("appearance_extra" in (k.get("boards") or []) for k in kids):
            continue
        kept = [k for k in kids if "appearance_extra" not in (k.get("boards") or [])]
        node["children"] = kept + NEW
        print("taxonomy：已替换（六），当前子项", [k["name"] for k in node["children"]])
    (D / "wiki_taxonomy.json").write_text(json.dumps(t, ensure_ascii=False), encoding="utf-8")
    (D / "wiki_taxonomy.js").write_text("window.WIKI_TAXONOMY=" + json.dumps(t, ensure_ascii=False) + ";\n",
                                        encoding="utf-8")

    p = D / "publication_policy.json"
    pol = json.loads(p.read_text(encoding="utf-8"))
    boards = pol.setdefault("boards", {})
    boards.pop("appearance_extra", None)
    for cat, bid in (("（六）捏脸", "appearance_face"), ("（七）戒指", "appearance_ring"),
                     ("（八）半感染者花苞", "appearance_bud")):
        boards[bid] = {"publication_status": "published",
                       "category": "一、时装类 / " + cat,
                       "reason": "由 appearance_extra 按部位拆出；数据来自 player_appear_data，只证静态存在。"}
    p.write_text(json.dumps(pol, ensure_ascii=False), encoding="utf-8")
    print("publication_policy 已更新，板块数", len(boards))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
