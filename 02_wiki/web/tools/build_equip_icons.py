# -*- coding: utf-8 -*-
"""装备 2D 图标导出（2026-11-01 用户定版：大图 _b + 新建 assets/equip_icons，三服按路径共用）。

数据源：30_分析/all_equips_全量_node索引_20261029/all_equips_attrs_{kj1,classic,yk}.json
        行字段 icon（如 ui/item_icon/icon_ningjiaohuang，无扩展名）
取图：pe_index（fid → pack,row）→ 源包/pe_gres_android/*.gpk 解码 → PNG

命名：按图标路径扁平化（ui/item_icon/icon_xxx → ui_item_icon_icon_xxx.png），
      同路径同图，三服共用；优先 _b 大图，只有 _s 时退回小图。
清单：assets/equip_icons/_index.json（原始路径 → png / 档位 / 包行 定位）

用法：python tools/build_equip_icons.py [--limit N]
"""
from __future__ import annotations

import json
import pathlib
import sqlite3
import sys

PROJ = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "01_索引与产物/10_索引/热更检测/pe_icon_bind"))
from toolkit_core.path_fid import fid_of  # noqa: E402
from toolkit_core import android_gpk as AG  # noqa: E402
import decoders as DEC  # noqa: E402

FREEZE = PROJ / "01_索引与产物/30_分析/all_equips_全量_node索引_20261029"
IDX = PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
PACKS = PROJ / "01_索引与产物/源包/pe_gres_android"
OUT = PROJ / "02_wiki/web/assets/equip_icons"
WEB = PROJ / "02_wiki/web"

ICON_FILES = {"kj1": "all_equips_attrs_kj1.json",
              "classic": "all_equips_attrs_classic.json",
              "yk": "all_equips_attrs_yk.json"}


def con():
    return sqlite3.connect("file:%s?mode=ro" % str(IDX).replace("\\", "/"),
                           uri=True, timeout=30)


def fid_hex(p: str) -> str:
    return "%016X" % (fid_of(p) & 0xFFFFFFFFFFFFFFFF)


def probe(c, base: str):
    """返回 (命中路径, 档位, pack, row)。优先 _b 大图，退化 _s。"""
    prefs = [base]
    if not base.startswith("ui/"):
        prefs.append("ui/" + base)
    for pre in prefs:
        for suf in ("_b", "_s"):
            p = pre + suf + ".ktx"
            r = c.execute("select pack,row from rows where fid=? limit 1", (fid_hex(p),)).fetchone()
            if r:
                return p, suf[1:], r[0], r[1]
    return None


def flat(png_path: str) -> str:
    s = png_path.replace("\\", "/")
    for e in (".ktx", ".dds", ".png", ".bc7"):
        if s.lower().endswith(e):
            s = s[: -len(e)]
    return s.replace("/", "_") + ".png"


class Packs:
    def __init__(self):
        self._cache = {}

    def entry(self, pack: str, row: int):
        if pack not in self._cache:
            d = {}
            for e in AG.iter_entries(str(PACKS / pack)):
                d[e["row"]] = e
            self._cache[pack] = d
        return self._cache[pack].get(row)


def export_one(packs: Packs, pack: str, row: int, dst: pathlib.Path) -> bool:
    e = packs.entry(pack, row)
    if not e:
        return False
    pl = e.get("payload") or b""
    try:
        rgba = DEC.decode_compblks(pl) if pl.startswith(b"CompBlks") else None
        if rgba is None:
            rec = dict(e)
            rec["data"] = pl
            if e.get("kind") == "ktx":
                rec["info"] = AG.parse_ktx(pl)
            rgba = AG.decode_image(rec)
        from PIL import Image
        dst.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(rgba, "RGBA").save(dst)
        return True
    except Exception:  # noqa: BLE001
        return False


def main() -> int:
    limit = 0
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else 0

    paths = {}
    for tag, name in ICON_FILES.items():
        d = json.loads((FREEZE / name).read_text(encoding="utf-8"))
        for r in d["rows"]:
            ic = r.get("icon")
            if isinstance(ic, str) and ic.strip():
                paths.setdefault(ic.strip(), set()).add(tag)
    print("唯一图标路径", len(paths))

    c = con()
    packs = Packs()
    index = {}
    hit = miss = 0
    OUT.mkdir(parents=True, exist_ok=True)
    todo = list(paths.items())[: limit] if limit else list(paths.items())
    for i, (p, tags) in enumerate(todo, 1):
        h = probe(c, p)
        if not h:
            miss += 1
            index[p] = {"png": None, "state": "缺图（客户端无素材）", "servers": sorted(tags)}
            continue
        hp, suf, pack, row = h
        dst = OUT / flat(hp)
        ok = dst.is_file() or export_one(packs, pack, row, dst)
        if not ok:
            miss += 1
            index[p] = {"png": None, "state": "缺图（解码失败）", "servers": sorted(tags)}
            continue
        hit += 1
        rel = str(dst.relative_to(WEB)).replace("\\", "/")
        index[p] = {"png": rel, "suffix": suf, "source_path": hp,
                    "pack": pack, "row": row, "servers": sorted(tags)}
        if i % 200 == 0:
            print("  进度", i, "/", len(todo), "｜ 命中", hit, "｜ 缺", miss)

    (OUT / "_index.json").write_text(
        json.dumps({"generated": "2026-11-01", "total_paths": len(paths),
                    "hit": hit, "miss": miss,
                    "note": "大图 _b 优先；同路径同图三服共用；缺图=客户端无素材",
                    "icons": index}, ensure_ascii=False), encoding="utf-8")
    print("完成：命中 %d ｜ 缺 %d → %s" % (hit, miss, OUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
