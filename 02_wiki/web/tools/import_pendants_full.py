# -*- coding: utf-8 -*-
r"""挂饰全量：all_equips_data(oversea kj1) 里 id 270xxx 段 = 挂饰本体（124 件）。
导出 icon_270xxx 图标，替换板内旧的 28 条礼盒条目。
"""
from __future__ import annotations

import json
import pathlib
import struct
import sys


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
WEB = PROJ / "02_wiki/web"
BASE = PROJ / "01_索引与产物/41_还原树/Documents/script.py314.lc.npk/com/cdata/oversea"
PACKS = PROJ / "01_索引与产物/10_索引/热更检测/pe_packs"
OUTDIR = WEB / "assets/fashion_icon_refs"

sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "01_索引与产物/10_索引/热更检测/pe_icon_bind"))
import toolkit_core.bindict_table as BT  # noqa: E402
from toolkit_core import android_gpk as AG  # noqa: E402
import decoders as DEC  # noqa: E402
from PIL import Image  # noqa: E402
import sqlite3  # noqa: E402

IDX = PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"


def main() -> int:
    p = BASE / "all_equips_data_auto_oversea_data_kj1.py"
    c = BASE / "all_equips_data_auto_oversea_data_kj1_chs.py"
    raw = p.read_bytes()
    at = raw.find(b"x{")
    length = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + length]
    cnt = struct.unpack_from("<I", body, 0)[0]
    blob = body[8 + 4 * cnt:]
    pool = BT.parse_legacy_chs_pool(c.read_bytes())
    rows, _ = BT.decode_table_rows(body, pool, resolve_jumps=True)

    items = []
    for r in rows:
        if not (270000 <= r["key"] < 271000):
            continue
        f = {k: (v[1] if isinstance(v, tuple) and len(v) == 2 else v) for k, v in r["values"].items()}
        ic = []
        v = f.get("icons")
        if isinstance(v, str) and v.startswith("jump:"):
            g = BT._resolve_27_group_reference(blob, int(v.split(":")[1]))
            if g:
                ic = [pool[x] if x < len(pool) else str(x) for x in g["values"]]
        items.append({"id": r["key"], "name": f.get("name") or "",
                      "icon": ic[0] if ic else "", "charm": f.get("charm_value"),
                      "desc": str(f.get("desc") or "")[:200]})
    print("挂饰本体", len(items), "｜ 有 icon 字段", sum(1 for x in items if x["icon"]))

    con = sqlite3.connect("file:%s?mode=ro" % str(IDX).replace("\\", "/"), uri=True)
    plan = {}
    for it in items:
        base = it["icon"].rsplit("/", 1)[-1]
        if not base:
            continue
        for suf in ("_b", "_s"):
            r = con.execute("select pack,row,name from rows where name like ? limit 1",
                            ("%%/%s%s.ktx" % (base, suf),)).fetchone()
            if r:
                plan.setdefault(r[0], {})[r[1]] = (base + suf, it["id"], suf)
    con.close()

    ok = 0
    for pack, want in plan.items():
        path = PACKS / pack
        if not path.is_file():
            continue
        for e in AG.iter_entries(str(path)):
            if e["row"] not in want:
                continue
            stem, _iid, _suf = want[e["row"]]
            pl = e.get("payload") or b""
            try:
                rgba = DEC.decode_compblks(pl) if pl.startswith(b"CompBlks") else None
                if rgba is None:
                    rec = dict(e)
                    rec["data"] = pl
                    if e.get("kind") == "ktx":
                        rec["info"] = AG.parse_ktx(pl)
                    rgba = AG.decode_image(rec)
                Image.fromarray(rgba, "RGBA").save(OUTDIR / (stem + ".png"))
                ok += 1
            except Exception:
                pass
    print("导出 PNG", ok)

    board_p = WEB / "data/boards/fashion_wardrobe.json"
    d = json.loads(board_p.read_text(encoding="utf-8"))
    before = len(d["items"])
    d["items"] = [x for x in d["items"] if not str(x.get("id", "")).startswith("pendant_")]
    removed = before - len(d["items"])
    have = {x["id"] for x in d["items"]}
    added = 0
    for it in items:
        pid = "pendant_%d" % it["id"]
        if pid in have:
            continue
        base = it["icon"].rsplit("/", 1)[-1]
        imgs = []
        if base:
            for suf in ("_b", "_s"):
                png = OUTDIR / (base + suf + ".png")
                if png.is_file():
                    imgs.append({"png": "assets/fashion_icon_refs/%s%s.png" % (base, suf),
                                 "suffix": suf, "base": "ui/item_icon/" + base})
        d["items"].append({
            "id": pid, "name": it["name"] or ("挂饰 %d" % it["id"]),
            "part": "挂饰", "part_bucket": ["挂饰"],
            "grade_level": None, "charm_value": it["charm"],
            "duration_state": "unknown", "has_permanent": None,
            "_media": {"total": len(imgs), "images": imgs} if imgs else {"total": 0},
            "evidence": "structure",
            "source": "all_equips_data 270xxx（挂饰本体）",
            "desc": it["desc"],
        })
        added += 1
    board_p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/fashion_wardrobe.js").write_text(
        "window.WIKI_BOARD_fashion_wardrobe = "
        + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print("板：移除礼盒 %d ｜ 新增挂饰 %d ｜ 现总 %d" % (removed, added, len(d["items"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
