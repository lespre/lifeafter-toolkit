# -*- coding: utf-8 -*-
r"""时装板补图（通用）：从 item id 数字段取号，依次查

 1) _cache_official_icons.json（道具/礼盒/配方）
 2) all_equips_data(kj1).icons 跳转组（挂饰 270xxx / 面饰 260xxx / 光源等）
命中即导出到 assets/fashion_posters/<条目id>.png。
"""
from __future__ import annotations

import json
import pathlib
import re
import struct
import sys

PROJ = pathlib.Path(r"E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
CD = PROJ / "01_索引与产物/41_还原树/pe_test_script/com/cdata"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "01_索引与产物/30_分析/热更检测"))
from toolkit_core import bindict_table as BT  # noqa: E402
import pe_fetch  # noqa: E402

P = WEB / "data/boards/fashion_wardrobe.json"
OUT = WEB / "assets/fashion_posters"


def load_equip_icons():
    p = CD / "oversea/all_equips_data_auto_oversea_data_kj1.py"
    c = CD / "oversea/all_equips_data_auto_oversea_data_kj1_chs.py"
    raw = p.read_bytes()
    at = raw.find(b"x{")
    L = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + L]
    cnt = struct.unpack_from("<I", body, 0)[0]
    blob = body[8 + 4 * cnt:]
    pool = BT.parse_legacy_chs_pool(c.read_bytes())
    rows, _ = BT.decode_table_rows(body, pool, resolve_jumps=False)

    def g(r, k):
        v = r["values"].get(k)
        return (v[1] if isinstance(v, tuple) else v) if v else None

    def uleb(b, i):
        r = s = 0
        while True:
            x = b[i]
            i += 1
            r |= (x & 0x7F) << s
            s += 7
            if x < 0x80:
                return r, i

    def grp(off):
        if not off or blob[off] != 0x27:
            return []
        n = blob[off + 2]
        j = off + 3
        out = []
        for _ in range(n):
            v, j = uleb(blob, j)
            out.append(v)
        return out

    out = {}
    for r in rows:
        ic = g(r, "icons")
        if not ic:
            continue
        off = int(str(ic).split(":")[1])
        paths = [pool[i] for i in grp(off) if i < len(pool)]
        if paths:
            out[str(r["key"])] = paths
    return out


def main() -> int:
    cache = json.loads((WEB / "_cache_official_icons.json").read_text(encoding="utf-8"))
    icons = cache["icons"]
    equip = load_equip_icons()
    print("道具 icon", len(icons), "｜装备 icon", len(equip), flush=True)

    d = json.loads(P.read_text(encoding="utf-8"))
    miss = [i for i in d["items"]
            if not (((i.get("_media") or {}).get("images") or [{}])[0] or {}).get("png")]
    OUT.mkdir(parents=True, exist_ok=True)

    ok = 0
    for it in miss:
        m = re.search(r"(\d{3,})", str(it.get("id") or ""))
        if not m:
            continue
        num = m.group(1)
        cands = []
        if num in equip:
            cands = equip[num]
        elif num in icons:
            cands = [icons[num]]
        if not cands:
            continue
        f = OUT / (re.sub(r"[^0-9A-Za-z_.\-]+", "_", str(it.get("id"))) + ".png")
        got = False
        for base in cands:
            b = base[:-4] if base.lower().endswith((".png", ".ktx", ".dds")) else base
            for cand in (b, b + "_b"):
                try:
                    if pe_fetch.export(cand, f):
                        got = True
                        break
                except Exception:
                    pass
            if got:
                break
        if got:
            ok += 1
            it["_media"] = {"images": [{"png": "assets/fashion_posters/" + f.name, "label": "图标"}], "total": 1}
            it["icon_state"] = "有图"
            it["icon_count"] = 1

    have = sum(1 for i in d["items"]
               if (((i.get("_media") or {}).get("images") or [{}])[0] or {}).get("png"))
    d["meta"]["state_summary"]["有图"] = have
    P.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/fashion_wardrobe.js").write_text(
        "window.WIKI_BOARD_fashion_wardrobe = " + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";",
        encoding="utf-8")
    print("补上", ok, "｜有图", have, "/", len(d["items"]), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
