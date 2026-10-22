# -*- coding: utf-8 -*-
"""全量扫 npk 索引：找含指定中文关键词的条目（定位 CHS 池 / 名称来源）。"""
import json
import pathlib
import sqlite3
import sys
import zlib

DB = pathlib.Path(r"E:/la拆包项目/01_索引与产物/30_分析/热更检测/npk_index.sqlite3")
OUT = pathlib.Path(r"E:/la拆包项目/01_索引与产物/30_分析/npk_keyword_hits.json")
KEYS = ("一勺甜", "不在线挂饰", "刑天铠甲", "面饰", "全场最佳", "击败")


def body_of(blob: bytes) -> bytes:
    if blob[16:18] == b"\x78\xda":
        try:
            return zlib.decompress(blob[16:])
        except Exception:
            return blob
    if blob[:2] == b"\x78\xda":
        try:
            return zlib.decompress(blob)
        except Exception:
            return blob
    return blob


def main() -> int:
    c = sqlite3.connect("file:%s?mode=ro" % str(DB).replace("\\", "/"), uri=True)
    layers = dict(c.execute("select key,value from meta where key like 'source:%'").fetchall())
    hits = []
    scanned = 0
    for layer, src in layers.items():
        lay = layer.split(":", 1)[1]
        with open(src, "rb") as f:
            for row, off, packed in c.execute(
                    "select row,offset,packed from entries where layer=?", (lay,)):
                f.seek(off)
                blob = f.read(packed)
                scanned += 1
                body = body_of(blob)
                txt = body.decode("utf-8", "ignore")
                found = [k for k in KEYS if k in txt]
                if found:
                    hits.append({"layer": lay, "row": row, "bytes": len(body),
                                 "keys": found, "preview": txt[:120]})
                if scanned % 10000 == 0:
                    print("已扫", scanned, "命中", len(hits), flush=True)
    OUT.write_text(json.dumps(hits, ensure_ascii=False, indent=1), encoding="utf-8")
    print("完成：扫描 %d 条，命中 %d 条 → %s" % (scanned, len(hits), OUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
