# -*- coding: utf-8 -*-
"""场景平衡：按场景名回挂 scene_id 列表 + PvP/PvE 分类（space_data.map_tag==4）。

map_tag 语义（space_data 实测 1,249 场景）：
  1 开放世界 · 2 营地/城镇 · 3 PvE 副本战役 · 4 PvP · 5 特殊活动
"""
from __future__ import annotations

import json
import pathlib
import struct
import sys
from collections import defaultdict


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
ROOT = pathlib.Path(PROJ)
BOARD = ROOT / "02_wiki/web/data/boards/scene_balance.json"
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(ROOT / "02_wiki/web/tools"))
from toolkit_core.bindict_table import decode_table_rows, parse_legacy_chs_pool  # noqa: E402
from _src import cdata_dir  # noqa: E402

PVP_TAG = 4
EXTRA_PVP = {"南希市", "夏尔镇", "夏尔镇中转站", "远星城", "特训地图", "旷野战场", "营地保卫战"}


def load_space():
    CD = cdata_dir()
    raw = (CD / "space_data.py").read_bytes()
    at = raw.find(b"x{")
    n = struct.unpack_from("<I", raw, at + 2)[0]
    chs = CD / "space_data_chs.py"
    pool = parse_legacy_chs_pool(chs.read_bytes()) if chs.exists() else []
    rows, _ = decode_table_rows(raw[at + 6: at + 6 + n], pool, resolve_jumps=False, lenient=True)
    by_name = defaultdict(list)
    tag_of = {}
    for r in rows:
        v = {k: (x[1] if isinstance(x, tuple) else x) for k, x in (r.get("values") or {}).items()}
        sid, nm, tag = v.get("id"), v.get("name"), v.get("map_tag")
        if isinstance(sid, int) and isinstance(nm, str) and nm:
            by_name[nm].append(sid)
            if isinstance(tag, int):
                tag_of[sid] = tag
    return by_name, tag_of


def main() -> int:
    by_name, tag_of = load_space()
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    n_pvp = 0
    for it in d["items"]:
        nm = it.get("name") or ""
        ids = sorted(set(by_name.get(nm) or []))
        it["scene_ids"] = ids
        if ids:
            it["场景编号"] = "%d 个：%s" % (len(ids), ", ".join(str(x) for x in ids[:8]) + ("…" if len(ids) > 8 else ""))
        is_pvp = any(tag_of.get(i) == PVP_TAG for i in ids) or nm in EXTRA_PVP
        it["scene_type"] = "PvP" if is_pvp else "PvE"
        it["场景类型"] = it["scene_type"]
        if is_pvp:
            n_pvp += 1
    meta = d.setdefault("meta", {})
    meta["name"] = "场景平衡"
    meta["filters"] = [{"key": "server_type", "label": "服型"},
                       {"key": "source_kind", "label": "来源类型"},
                       {"key": "scene_type", "label": "场景类型"}]
    meta["pvp_rule"] = ("PvP = space_data.map_tag==4（夏尔镇 / 夏尔镇中转站 / 远星城 / 南希市 / 特训地图 / 旷野战场），"
                        "另加名字白名单兜底；其余为 PvE。")
    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    print("PvP %d / 共 %d ｜ 回挂 scene_id 的条目 %d"
          % (n_pvp, len(d["items"]), sum(1 for i in d["items"] if i.get("scene_ids"))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
