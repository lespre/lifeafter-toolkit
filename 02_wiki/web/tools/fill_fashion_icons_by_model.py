# -*- coding: utf-8 -*-
r"""按 fashion_data.icons 跳转组给时装板补图标。

fashion_data 每行：model_id + icons(jump) → 0x27 组 → 字符串池索引 → 'ui/item_icon/...'
匹配键：model_id + 名称（同 model 多配色时按名精确匹配，否则取同 model 第一行）。
"""
from __future__ import annotations

import json
import pathlib
import re
import struct
import sys

PROJ = pathlib.Path(r"E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
from _src import cdata_dir
CD = cdata_dir()
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "01_索引与产物/30_分析/热更检测"))
from toolkit_core import bindict_table as BT  # noqa: E402
import pe_fetch  # noqa: E402
from toolkit_core import img_fetch  # PE→PC 双源取图

P = WEB / "data/boards/fashion_wardrobe.json"
OUT = WEB / "assets/fashion_posters"


def main() -> int:
    raw = (CD / "fashion_data.py").read_bytes()
    at = raw.find(b"x{")
    L = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + L]
    cnt = struct.unpack_from("<I", body, 0)[0]
    blob = body[8 + 4 * cnt:]
    pool = BT.parse_legacy_chs_pool((CD / "fashion_data_chs.py").read_bytes())
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

    by_model = {}
    for r in rows:
        mid = str(g(r, "model_id"))
        ic = g(r, "icons")
        off = int(str(ic).split(":")[1]) if ic else 0
        paths = [pool[i] for i in grp(off) if i < len(pool)]
        by_model.setdefault(mid, []).append({"name": str(g(r, "name") or ""), "icons": paths})

    d = json.loads(P.read_text(encoding="utf-8"))
    miss = [i for i in d["items"]
            if not (((i.get("_media") or {}).get("images") or [{}])[0] or {}).get("png")]
    print("无图", len(miss), "｜model 表", len(by_model), flush=True)

    OUT.mkdir(parents=True, exist_ok=True)
    ok = tried = 0
    for it in miss:
        mid = str(it.get("model_id") or (it.get("model_ids") or [None])[0])
        cands = by_model.get(mid) or []
        if not cands:
            continue
        row = next((c for c in cands if c["name"] and c["name"] in str(it.get("name") or "")), cands[0])
        f = OUT / (re.sub(r"[^0-9A-Za-z_.\-]+", "_", str(it.get("id"))) + ".png")
        for base in row["icons"]:
            b = base[:-4] if base.lower().endswith((".png", ".ktx", ".dds")) else base
            tried += 1
            got = False
            for cand in (b, b + "_b"):
                try:
                    if img_fetch.export(cand, f):
                        got = True
                        break
                except Exception:
                    pass
            if got:
                ok += 1
                it["_media"] = {"images": [{"png": "assets/fashion_posters/" + f.name, "label": "图标"}], "total": 1}
                it["icon_state"] = "有图"
                it["icon_count"] = 1
                break

    have = sum(1 for i in d["items"]
               if (((i.get("_media") or {}).get("images") or [{}])[0] or {}).get("png"))
    d["meta"]["state_summary"]["有图"] = have
    P.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/fashion_wardrobe.js").write_text(
        "window.WIKI_BOARD_fashion_wardrobe = " + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";",
        encoding="utf-8")
    print("尝试", tried, "｜补上", ok, "｜有图", have, "/", len(d["items"]), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
