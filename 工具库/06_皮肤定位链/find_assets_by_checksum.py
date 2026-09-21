# -*- coding: utf-8 -*-
"""按"源资产 checksum"在本地所有容器/目录里找资产并自证（可复用）。

由来：`E:\\mrzh\\res.npk` entry 8858 是**构建期清单**：
    <路径> {"checksum": "<md5(原始资产字节)>", "has_alpha": 0|1, "img_size": [w,h]}
本工具做三件事：
  1) 解析该清单 → 导出 `name -> {checksum, has_alpha, w, h}`（机读）；
  2) 在给定搜索面里按 checksum 找资产：
     · 目录里的 `<32hex>` 物化文件（`Documents\\res\\<family>\\<checksum>`）
     · `*.idx` + `*.wpk`（idx 键 = 内容 md5；pkg 决定 wpk 文件名）
     · `*.gpk`（行表 16B 指纹）、`*.fpk`（NXPK 指纹列表）、`*.npk`（fid u64）
  3) 命中即取内容 → `md5(payload) == checksum` **自证** → 落盘 + 机读报告。

用法：
  python find_assets_by_checksum.py --table-dump                 # 只导出清单
  python find_assets_by_checksum.py --names <json/txt> --scan    # 按声明名找并自证
  python find_assets_by_checksum.py --names-csv a.tga,b.tga --scan
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import struct
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (_HERE, os.path.join(_HERE, "..", "01_核心解包器")):
    _p = os.path.abspath(_p)
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)

from gpk_npk_index import aes_ecb, parse_npk  # noqa: E402
from npk_reader import unpack_entry  # noqa: E402
import idx_wpk_dds_extractor as X  # noqa: E402

RES_NPK = r"E:\mrzh\res.npk"
ENTRY = 8858
LINE = re.compile(rb'^(\S+)\s+\{"checksum":\s*"([0-9a-f]{32})",\s*"has_alpha":\s*(\d),\s*"img_size":\s*\[(\d+),\s*(\d+)\]\}')
IDX_DIRS = [r"E:\mrzh\Documents\res", r"E:\LifeAfter\Documents\res"]
CACHE_DIRS = [r"E:\mrzh\Documents\res", r"E:\LifeAfter\Documents\res"]
GPK_DIRS = [r"E:\mrzh\res", r"E:\mrzh\Documents\gres", r"E:\LifeAfter\Documents\gres", r"E:\LifeAfter\res"]
FPK_DIRS = [r"E:\mrzh\res", r"E:\LifeAfter\res"]


def load_table(npk=RES_NPK, entry=ENTRY):
    rec, rows = parse_npk(npk)
    for i, fid, off, ps, ds, fl in rows():
        if i != entry:
            continue
        with open(npk, "rb") as f:
            f.seek(off)
            pay = unpack_entry(f.read(ps), ds, fl)
        out, bad = {}, 0
        for ln in pay.split(b"\n"):
            m = LINE.match(ln.strip())
            if m:
                out[m.group(1).decode("utf-8", "replace")] = {
                    "checksum": m.group(2).decode(), "has_alpha": int(m.group(3)),
                    "w": int(m.group(4)), "h": int(m.group(5))}
            elif ln.strip():
                bad += 1
        return out, bad
    return {}, 0


def scan_dir_checksums(targets):
    hits = []
    for root in CACHE_DIRS:
        for dirpath, _d, files in os.walk(root):
            for fn in files:
                if len(fn) == 32 and fn.lower() in targets:
                    hits.append({"kind": "materialized_file", "path": os.path.join(dirpath, fn),
                                 "checksum": fn.lower()})
    return hits


def scan_idx(targets):
    hits = []
    for d in IDX_DIRS:
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".idx"):
                continue
            p = os.path.join(d, fn)
            try:
                for e in X.parse_idx(__import__("pathlib").Path(p)):
                    if e["hash"].lower() in targets:
                        hits.append({"kind": "idx", "idx": p, "index": e["index"],
                                     "checksum": e["hash"].lower(), "pkg": e["pkg"],
                                     "off": e["offset"], "psz": e["payload_size"],
                                     "hsz": e["header_size"]})
            except Exception:
                continue
    return hits


def scan_gpk(targets_u64):
    hits = []
    for root in GPK_DIRS:
        if not os.path.isdir(root):
            continue
        for fn in sorted(os.listdir(root)):
            if not fn.lower().endswith(".gpk"):
                continue
            p = os.path.join(root, fn)
            try:
                size = os.path.getsize(p)
                with open(p, "rb") as f:
                    outer = aes_ecb(f.read(16))
                    _z, _masked, two, nb = struct.unpack("<IIII", outer)
                    B = 16
                    rown = 0
                    for _k in range(nb):
                        f.seek(B)
                        bh = aes_ecb(f.read(48))
                        n1, bsize = struct.unpack_from("<II", bh, 4)
                        cnt = n1 - 1
                        f.seek(B + 48)
                        tab = aes_ecb(f.read(cnt * 32))
                        for j in range(cnt):
                            _o, _cm, _de, _c1, _c2, _fl, lo, hi = struct.unpack_from("<IIIIIIII", tab, j * 32)
                            if lo in targets_u64 or hi in targets_u64:
                                hits.append({"kind": "gpk_row", "container": p, "row": rown,
                                             "lo": "%016x" % lo, "hi": "%016x" % hi})
                            rown += 1
                        if bsize <= 0 or B + bsize > size:
                            break
                        B += bsize
            except Exception:
                continue
    return hits


def scan_fpk(targets):
    sys.path.insert(0, os.path.join(_HERE, "..", "01_核心解包器"))
    try:
        import lifeafter_unpacker_full as LU
    except Exception:
        return []
    hits = []
    for root in FPK_DIRS:
        if not os.path.isdir(root):
            continue
        for fn in sorted(os.listdir(root)):
            if not fn.lower().endswith(".fpk"):
                continue
            p = os.path.join(root, fn)
            try:
                r = LU.parse_fpk(p)
            except Exception:
                continue
            for h in (r.get("hashes") or []):
                if h.lower() in targets:
                    hits.append({"kind": "fpk", "container": p, "checksum": h.lower()})
    return hits


def extract_idx_hit(h, outdir):
    stem = os.path.splitext(os.path.basename(h["idx"]))[0]
    wpk = os.path.join(os.path.dirname(h["idx"]), "%s%d.wpk" % (stem, h["pkg"]))
    if not os.path.exists(wpk):
        return {"status": "wpk_missing", "wpk": wpk}
    try:
        final, typ, layers, tag, _p, _t = X.extract_dds_from_wpk(
            __import__("pathlib").Path(wpk), h["off"], h["hsz"], h["psz"])
    except Exception as exc:
        return {"status": "extract_fail", "err": repr(exc)[:120]}
    md5 = hashlib.md5(final).hexdigest()
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, h["checksum"] + "." + typ)
    open(out, "wb").write(final)
    return {"status": "ok", "type": typ, "layers": layers, "bytes": len(final),
            "md5": md5, "selfcheck": md5 == h["checksum"], "saved": out,
            "sha16": hashlib.sha256(final).hexdigest()[:16]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--table-dump", action="store_true")
    ap.add_argument("--names", help="JSON/txt：要查的声明名（basename 或全路径）")
    ap.add_argument("--names-csv")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(RES_NPK), "_bychecksum_out"))
    ap.add_argument("--scan", action="store_true")
    a = ap.parse_args()

    table, bad = load_table()
    print("清单条数 %d（未匹配行 %d）" % (len(table), bad))
    if a.table_dump:
        p = os.path.join(a.out, "name_table.json")
        os.makedirs(a.out, exist_ok=True)
        json.dump(table, open(p, "w", encoding="utf-8"), ensure_ascii=False)
        print("导出", p)
        return
    want = set()
    if a.names_csv:
        want |= {x.strip().lower() for x in a.names_csv.split(",") if x.strip()}
    if a.names:
        d = json.load(open(a.names, encoding="utf-8")) if a.names.endswith(".json") else \
            open(a.names, encoding="utf-8").read().split()
        def walk(o):
            if isinstance(o, dict):
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
            elif isinstance(o, str) and re.search(r"\.(tga|dds|png)$", o, re.I):
                want.add(os.path.basename(o.replace("\\", "/")).lower())
        walk(d)
    sel = {k: v for k, v in table.items() if os.path.basename(k).lower() in want} if want else table
    print("选定 %d 条（want=%d）" % (len(sel), len(want)))
    targets = {v["checksum"] for v in sel.values()}
    if not a.scan:
        json.dump(sel, open(os.path.join(a.out, "selected.json"), "w", encoding="utf-8")
                  if os.path.isdir(a.out) else sys.stdout, ensure_ascii=False, indent=1)
        return
    u64 = set()
    for cs in targets:
        b = bytes.fromhex(cs)
        u64 |= {int.from_bytes(b[:8], "little"), int.from_bytes(b[:8], "big"),
                int.from_bytes(b[8:], "little"), int.from_bytes(b[8:], "big")}
    rep = {"selected": len(sel), "checksums": len(targets)}
    rep["materialized"] = scan_dir_checksums(targets)
    rep["idx"] = scan_idx(targets)
    rep["gpk"] = scan_gpk(u64)
    rep["fpk"] = scan_fpk(targets)
    rep["extracted"] = [extract_idx_hit(h, os.path.join(a.out, "hits")) for h in rep["idx"]]
    print(json.dumps({k: (len(v) if isinstance(v, list) else v) for k, v in rep.items()},
                     ensure_ascii=False))
    os.makedirs(a.out, exist_ok=True)
    json.dump(rep, open(os.path.join(a.out, "by_checksum_report.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("报告 →", os.path.join(a.out, "by_checksum_report.json"))


if __name__ == "__main__":
    main()
