# -*- coding: utf-8 -*-
"""看 upcoming_auto 新增条目缺什么：没图的 id、sidecar 是否有对应海报。"""
from __future__ import annotations

import json
import re
from pathlib import Path

WEB = Path(r"E:\la拆包项目\02_wiki\web")


def main() -> int:
    d = json.loads((WEB / "data/boards/upcoming_auto.json").read_text(encoding="utf-8"))
    t = (WEB / "data/media/weapon_skin_media.js").read_text(encoding="utf-8")
    m = re.match(r"window\.WEAPON_SKIN_MEDIA\s*=\s*(\{.*\})\s*;?\s*$", t, re.S)
    bank = json.loads(m.group(1)).get("skins", {}) if m else {}
    miss = [i for i in d["items"] if not ((i.get("_media") or {}).get("images") or [])]
    print("upcoming 条目", len(d["items"]), "| 无图", len(miss))
    for i in miss[:12]:
        sid = str(i.get("item_id") or i.get("id") or "")
        has = sid in bank
        poster = (WEB / f"assets/skin_posters/{sid}.png").is_file()
        print(f"  {sid:12s} {str(i.get('name'))[:16]:18s} 名={bool(i.get('desc'))} sidecar={has} poster={poster}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
