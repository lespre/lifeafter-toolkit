# -*- coding: utf-8 -*-
"""场景类型改为「只认可靠标志」：space_data.map_tag==4 → PvP，其余 PvE；无场景号则标未匹配。

去掉手写名单兜底（南希市/夏尔镇…），不做任何按名字的猜测。
"""
from __future__ import annotations

import json
import pathlib
import struct
import sys
from collections import defaultdict

ROOT = pathlib.Path("E:/la拆包项目")
BOARD = ROOT / "02_wiki/web/data/boards/scene_balance.json"
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(ROOT / "02_wiki/web/tools"))
from toolkit_core.bindict_table import decode_table_rows, parse_legacy_chs_pool  # noqa: E402
from _src import cdata_dir  # noqa: E402

PVP_TAG = 4


def load_space():
    CD = cdata_dir()
    raw = (CD / "space_data.py").read_bytes()
    at = raw.find(b"x{")
    n = struct.unpack_from("<I", raw, at + 2)[0]
    chs = CD / "space_data_chs.py"
    pool = parse_legacy_chs_pool(chs.read_bytes()) if chs.exists() else []
    rows, _ = decode_table_rows(raw[at + 6: at + 6 + n], pool, resolve_jumps=False, lenient=True)
    by_name, tag_of = defaultdict(list), {}
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
    cnt = defaultdict(int)
    for it in d["items"]:
        nm = it.get("name") or ""
        ids = sorted(set(by_name.get(nm) or []))
        if not ids:
            import re as _re
            m = _re.search(r"场景\s*(\d+)", nm)
            if m:
                cand = int(m.group(1))
                ids = [cand] if cand in tag_of else []
        it["scene_ids"] = ids
        if ids:
            it["场景编号"] = "%d 个：%s" % (len(ids), ", ".join(str(x) for x in ids[:8]) + ("…" if len(ids) > 8 else ""))
        if not ids:
            it["scene_type"] = "未匹配"
        elif any(tag_of.get(i) == PVP_TAG for i in ids):
            it["scene_type"] = "PvP"
        else:
            it["scene_type"] = "PvE"
        it["场景类型"] = it["scene_type"]
        cnt[it["scene_type"]] += 1
    meta = d.setdefault("meta", {})
    meta["filters"] = [{"key": "server_type", "label": "服型"},
                       {"key": "source_kind", "label": "来源类型"},
                       {"key": "scene_type", "label": "场景类型"}]
    meta["pvp_rule"] = ("只认可靠标志：space_data.map_tag==4 → PvP；其余有场景号的 → PvE；"
                        "连 scene_id 都挂不上的 → 未匹配（不按名字猜）。")
    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    print(dict(cnt), "共", len(d["items"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
