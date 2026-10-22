# -*- coding: utf-8 -*-
"""生成 PvP 相关属性表：id / 名称 / 战力权重 / 是否吃压缩 / 压缩曲线。"""
from __future__ import annotations

import json
import pathlib
import struct
import sys

sys.path.insert(0, r"E:/la拆包项目/00_规范与工具/工具/工具库/00_共享核心")
from toolkit_core import bindict_table as BT  # noqa: E402

CD = pathlib.Path(r"E:/la拆包项目/01_索引与产物/41_还原树/pe_20261020/com/cdata")
OUT = pathlib.Path(r"E:/la拆包项目/02_wiki/web/analysis")


def rows_of(p, chs=None):
    b = pathlib.Path(p).read_bytes()
    at = b.find(b"x{")
    L = struct.unpack_from("<I", b, at + 2)[0]
    pool = BT.parse_legacy_chs_pool(pathlib.Path(chs).read_bytes()) if chs else {}
    return BT.decode_table_rows(b[at + 6:at + 6 + L], pool, resolve_jumps=False)[0]


def main() -> int:
    cur = {c["id"]: c for c in json.loads((OUT / "attr_compress_curves.json").read_text(encoding="utf-8"))["base"]["curves"]}
    rows = rows_of(CD / "attribute_data.py", CD / "attribute_data_chs.py")

    def g(r, k):
        v = r["values"].get(k)
        return (v[1] if isinstance(v, tuple) else v) if v else None

    out = []
    for r in rows:
        nm = str(g(r, "name") or "")
        en = str(g(r, "e_name") or "")
        ds = str(g(r, "player_attr_desc") or "")
        if "玩家" not in nm:
            continue
        aid = int(r["key"])
        c = cur.get(aid)
        seg = c["segs"][0] if c else None
        ident = bool(seg) and all(abs(a - b) < 1e-6 for a, b in zip(seg["x"], seg["y"]))
        out.append({
            "id": aid, "name": nm, "e_name": en,
            "weight": g(r, "attr_weight"),
            "desc": ds,
            "in_compress_table": bool(c),
            "identity": ident,
            "curve": seg,
        })
    dest = OUT / "pvp_attrs.json"
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("PvP 相关属性", len(out), "→", dest)
    for it in out:
        tag = "不压缩(恒等)" if it["identity"] else ("压缩" if it["curve"] else "无曲线")
        print("  %-4d %-20s w=%-7s %s" % (it["id"], it["name"][:18], it["weight"], tag))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
