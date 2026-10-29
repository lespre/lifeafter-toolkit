# -*- coding: utf-8 -*-
r"""把真正的「挂饰」（gift_data 中 icon_270xxx 的 28 条礼盒）配图并进人物时装板。

来源：gift_data 行，字段 icon=ui/item_icon/icon_270xxx，名称形如「彩虹独角兽挂饰礼盒」。
图标族：icon_270xxx（_b 300×150 / _s 154×78）。
"""
from __future__ import annotations

import json
import pathlib
import re
import struct
import sys


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
WEB = PROJ / "02_wiki/web"
BASE = PROJ / "01_索引与产物/41_还原树/Documents/script.py314.lc.npk/com/cdata"
PACKS = PROJ / "01_索引与产物/10_索引/热更检测/pe_packs"
OUTDIR = WEB / "assets/fashion_icon_refs"

sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "01_索引与产物/10_索引/热更检测/pe_icon_bind"))
from toolkit_core.bindict_table import parse_legacy_chs_pool, decode_table_rows  # noqa: E402
from toolkit_core import android_gpk as AG  # noqa: E402
import decoders as DEC  # noqa: E402
from PIL import Image  # noqa: E402
import sqlite3  # noqa: E402

IDX = PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"


def load_gifts():
    p = BASE / "gift_data.py"
    c = BASE / "gift_data_chs.py"
    raw = p.read_bytes()
    at = raw.find(b"x{")
    length = struct.unpack_from("<I", raw, at + 2)[0]
    rows, _ = decode_table_rows(raw[at + 6: at + 6 + length], parse_legacy_chs_pool(c.read_bytes()))
    out = []
    for r in rows:
        f = {k: (v[1] if isinstance(v, tuple) and len(v) == 2 else v) for k, v in r["values"].items()}
        ic = str(f.get("icon") or "")
        if "icon_270" in ic:
            out.append({"gift": r["key"], "name": f.get("name") or "",
                        "icon": ic, "level": f.get("level")})
    return out


def main() -> int:
    gifts = load_gifts()
    con = sqlite3.connect("file:%s?mode=ro" % str(IDX).replace("\\", "/"), uri=True)
    rows = []
    for g in gifts:
        base = g["icon"].rsplit("/", 1)[-1]
        got = []
        for suf in ("_b", "_s"):
            r = con.execute("select pack,row,name from rows where name like ? limit 1",
                            ("%%/%s%s.ktx" % (base, suf),)).fetchone()
            if r:
                got.append((suf, r[0], r[1], r[2]))
        rows.append((g, got))
    con.close()

    by_pack = {}
    for g, got in rows:
        for suf, pack, row, name in got:
            by_pack.setdefault(pack, {})[row] = (base_name := name.rsplit("/", 1)[-1].rsplit(".", 1)[0])
    ok = 0
    for pack, want in by_pack.items():
        path = PACKS / pack
        if not path.is_file():
            continue
        for e in AG.iter_entries(str(path)):
            if e["row"] not in want:
                continue
            pl = e.get("payload") or b""
            try:
                rgba = DEC.decode_compblks(pl) if pl.startswith(b"CompBlks") else None
                if rgba is None:
                    rec = dict(e)
                    rec["data"] = pl
                    if e.get("kind") == "ktx":
                        rec["info"] = AG.parse_ktx(pl)
                    rgba = AG.decode_image(rec)
                Image.fromarray(rgba, "RGBA").save(OUTDIR / (want[e["row"]] + ".png"))
                ok += 1
            except Exception:
                pass

    board_p = WEB / "data/boards/fashion_wardrobe.json"
    d = json.loads(board_p.read_text(encoding="utf-8"))
    have = {x["id"] for x in d["items"]}
    added = 0
    for g, got in rows:
        pid = "pendant_%s" % g["gift"]
        if pid in have:
            continue
        imgs = []
        for suf, pack, row, name in got:
            stem = name.rsplit("/", 1)[-1].rsplit(".", 1)[0]
            imgs.append({"png": "assets/fashion_icon_refs/%s.png" % stem,
                         "suffix": suf, "base": "ui/item_icon/" + stem.rsplit("_", 1)[0],
                         "pack": pack, "row": row})
        nm = re.sub(r"礼盒$", "", g["name"]) or g["name"]
        d["items"].append({
            "id": pid, "name": nm, "part": "挂饰", "part_bucket": ["挂饰"],
            "grade_level": g.get("level"), "charm_value": None,
            "duration_state": "unknown", "has_permanent": None,
            "_media": {"total": len(imgs), "images": imgs} if imgs else {"total": 0},
            "evidence": "structure", "source": "gift_data icon_270xxx（挂饰礼盒）",
        })
        added += 1
    board_p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/fashion_wardrobe.js").write_text(
        "window.WIKI_BOARD_fashion_wardrobe = "
        + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print("挂饰礼盒 %d 条 ｜ 导出 PNG %d 张 ｜ 板内新增 %d 件 ｜ 现总 %d"
          % (len(gifts), ok, added, len(d["items"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
