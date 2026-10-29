# -*- coding: utf-8 -*-
r"""给核芯板补「升星固定解锁」：nucleus_build_data.rank_to_desc（星级 → 文案）。

rank_to_desc 格式：[0x36][kind][fmt][n] + n×(rank uleb, 字符串池下标 uleb)
关联：nucleus_build_data.nucleus_effect_name == 核芯名（已去「异变核芯-」前缀）
"""
from __future__ import annotations

import json
import pathlib
import struct
import sys


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
WEB = PROJ / "02_wiki/web"
OV = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata/oversea"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402


def main() -> int:
    p = OV / "nucleus_build_data_auto_oversea_data_kj1.py"
    c = OV / "nucleus_build_data_auto_oversea_data_kj1_chs.py"
    b = p.read_bytes()
    at = b.find(b"x{")
    L = struct.unpack_from("<I", b, at + 2)[0]
    body = b[at + 6: at + 6 + L]
    cnt = struct.unpack_from("<I", body, 0)[0]
    blob = body[8 + 4 * cnt:]
    pool = BT.parse_legacy_chs_pool(c.read_bytes())
    rows, _ = BT.decode_table_rows(body, pool, resolve_jumps=False)

    def g(r, k):
        v = r["values"].get(k)
        return (v[1] if isinstance(v, tuple) else v) if v else None

    def stars(rec):
        v = g(rec, "rank_to_desc")
        if not isinstance(v, str) or not v.startswith("jump:"):
            return []
        pos = int(v.split(":")[1])
        if blob[pos] != 0x36:
            return []
        n = blob[pos + 3]
        pos += 4
        out = []
        for _ in range(n):
            rk, pos = BT.uleb(blob, pos, len(blob))
            idx, pos = BT.uleb(blob, pos, len(blob))
            txt = pool[idx] if idx < len(pool) else ""
            txt = (txt.replace("#f", "").replace("#n", "").replace("#r", "\n")).strip()
            if txt:
                out.append({"star": rk, "text": txt})
        return out

    by_name = {}
    for r in rows:
        nm = str(g(r, "nucleus_effect_name") or "").strip()
        if not nm:
            continue
        by_name[nm] = {
            "stars": stars(r),
            "build_desc": str(g(r, "desc") or "").strip(),
            "icon": str(g(r, "icon_path") or ""),
            "build_id": r["key"],
        }

    bp = WEB / "data/boards/mutation_core_full.json"
    d = json.loads(bp.read_text(encoding="utf-8"))
    hit = 0
    for it in d["items"]:
        info = by_name.get(str(it.get("name")).strip())
        if not info:
            continue
        it["star_entries"] = info["stars"]
        it["build_id"] = info["build_id"]
        it["build_desc"] = info["build_desc"]
        hit += 1

    d["meta"]["field_labels"]["star_entries"] = "升星解锁"
    d["meta"]["notes"] = (str(d["meta"].get("notes") or "") +
                          "\n升星解锁来自 nucleus_build_data.rank_to_desc（按核芯名关联），"
                          "共命中 %d 枚。" % hit).strip()
    bp.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/mutation_core_full.js").write_text(
        "window.WIKI_BOARD_mutation_core_full = " + json.dumps(d, ensure_ascii=False, indent=1) + ";",
        encoding="utf-8")
    print("命中核芯", hit, "/", len(d["items"]))
    for it in d["items"]:
        if it.get("star_entries"):
            print("  ", it["name"], "→", [(s["star"], s["text"][:24]) for s in it["star_entries"]])
            break
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
