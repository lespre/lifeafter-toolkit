# -*- coding: utf-8 -*-
"""核对：重渲失败清单 vs 缺口审计清单，是否完全一致（不该有「本可渲却失败」）。"""
from __future__ import annotations

import json
import pathlib

AN = pathlib.Path("E:/la拆包项目/01_索引与产物/30_分析")


def main() -> int:
    gap = json.loads((AN / "avatar_anim_gap_audit.json").read_text(encoding="utf-8"))
    rows = gap.get("records") or gap.get("items") or gap.get("rows") or []
    gap_ids = set()
    for r in rows:
        if r.get("verdict") in (None, "ok", "OK"):
            continue
        gap_ids.add(str(r.get("id") or r.get("item_id")))
    # 失败列表：以目录里缺 APNG 的条目为准（重渲写回 avatar_catalog，失败条目不产出文件）
    cat = json.loads(pathlib.Path("E:/la拆包项目/02_wiki/web/data/boards/avatar_catalog.json")
                     .read_text(encoding="utf-8"))
    web = pathlib.Path("E:/la拆包项目/02_wiki/web")
    have, missing, no_spine = [], [], []
    for it in cat["items"]:
        if not it.get("spine_path"):
            no_spine.append(it["id"])
            continue
        png = (it.get("_media") or {}).get("anim") or it.get("anim_png")
        ok = bool(png) and (web / png).is_file()
        (have if ok else missing).append(it["id"])
    print("有 spine 的条目 %d ｜ 有动图 %d ｜ 缺动图 %d ｜ 无 spine %d"
          % (len(have) + len(missing), len(have), len(missing), len(no_spine)))
    print("缺口审计标记 %d 条" % len(gap_ids))
    extra = sorted(set(missing) - gap_ids)
    print("缺动图但审计里没标记的：%d %s" % (len(extra), extra[:10]))
    print("审计标记但已渲出图的：%d %s"
          % (len([x for x in gap_ids if x in have]), sorted(gap_ids & set(have))[:10]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
