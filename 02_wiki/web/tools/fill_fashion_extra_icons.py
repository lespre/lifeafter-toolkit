# -*- coding: utf-8 -*-
"""给时装板剩余缺图条目补图：面饰（slots 板 icon 字段）+ 挂饰（all_equips icons 跳转组）。

只补没有 _media 的条目；已有图的跳过。取图走 img_fetch（PE→PC 兜底）。
"""
from __future__ import annotations

import json
import pathlib
import sys

WEB = pathlib.Path(__file__).resolve().parents[1]
PROJ = WEB.parents[1]
sys.path.insert(0, str(WEB / "tools"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))

from _src import table_path                      # noqa: E402
from toolkit_core import img_fetch               # noqa: E402
from toolkit_core import bindict_table as BT     # noqa: E402

BOARD = WEB / "data/boards/fashion_wardrobe.json"
OUT = WEB / "assets/fashion_posters"


def _v(v):
    return v[1] if isinstance(v, tuple) else v


def face_icons() -> dict:
    p = WEB / "data/boards/fashion_face_slots.json"
    if not p.exists():
        return {}
    m = {}
    for it in json.loads(p.read_text(encoding="utf-8")).get("items", []):
        ic = it.get("icon")
        if ic:
            m[str(it["id"])] = ic if ic.startswith("ui/") else "ui/" + ic
    return m


def pendant_icons() -> dict:
    """all_equips 270xxx 行的 icons 跳转组 → 池里的路径。"""
    base = table_path("all_equips_data_auto_oversea_data_kj1", "oversea")
    if not base or not base.exists():
        return {}
    chs = base.with_name(base.stem + "_chs.py")
    raw = base.read_bytes()
    at = raw.find(b"x{")
    if at < 0:
        return {}
    L = int.from_bytes(raw[at + 2:at + 6], "little")
    import struct as _st
    body = raw[at + 6: at + 6 + L]
    cnt = _st.unpack_from("<I", body, 0)[0]
    blob = body[8 + 4 * cnt:]
    pool = BT.parse_legacy_chs_pool(chs.read_bytes()) if chs.exists() else None
    rows = BT.decode_table_rows(body, pool, resolve_jumps=True, lenient=True)[0]
    out = {}
    for r in rows:
        key = str(r.get("key") or "")
        if not key.startswith("270"):
            continue
        ic = r.get("values", {}).get("icons")
        if not isinstance(ic, tuple):
            continue
        try:
            off = int(str(ic[1]).split(":")[1])
        except Exception:
            continue
        grp = BT.read_27_group(blob, off)
        if not grp:
            continue
        paths = [pool[i] for i in grp[1] if pool and i < len(pool)]
        if paths:
            out["pendant_%s" % key] = paths[0] if paths[0].startswith("ui/") else "ui/" + paths[0]
    return out


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    items = d.get("items", [])
    icons = {}
    icons.update(face_icons())
    icons.update(pendant_icons())
    OUT.mkdir(parents=True, exist_ok=True)

    ok = 0
    for it in items:
        if (it.get("_media") or {}).get("images"):
            continue
        iid = str(it.get("id"))
        base = icons.get(iid)
        if not base:
            continue
        dst = OUT / (iid + ".png")
        if not dst.exists():
            if not img_fetch.export(base, dst):
                continue
        it["_media"] = {"images": [{"png": "assets/fashion_posters/%s.png" % iid, "label": "图标"}],
                        "total": 1}
        ok += 1

    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    have = sum(1 for i in items if (i.get("_media") or {}).get("images"))
    print("本次补", ok, "｜现在有图", have, "/", len(items))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
