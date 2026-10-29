# -*- coding: utf-8 -*-
"""时装板补图（PE 索引命中版）：fid 命中 → pe_packs 解包 → assets/fashion_posters/<id>.png → 回写 _media.images。

只补没有 _media.images 的条目；每 --flush 张落盘一次 board；--budget 秒到点即落盘退出。
用法：python fill_fashion_posters_pe.py --budget 45 [--apply]
"""
from __future__ import annotations

import argparse
import json
import mmap
import pathlib
import shutil
import struct
import sys
import time

import numpy as np
from PIL import Image


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "01_索引与产物/10_索引/热更检测/pe_icon_bind"))
from toolkit_core import android_gpk as AG   # noqa: E402
import decoders as DEC                      # noqa: E402

DET = PROJ / "01_索引与产物/10_索引/热更检测"
PKGDIR = DET / "pe_packs"
BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"
OUT = PROJ / "02_wiki/web/assets/fashion_posters"
HITS = DET / "_fashion_miss_hits_tmp.json"


def decode_payload(pl: bytes):
    if pl.startswith(b"CompBlks"):
        return DEC.decode_compblks(pl)
    if pl.startswith(b"\xabKTX"):
        return AG.decode_image({"kind": "ktx", "data": pl, "info": AG.parse_ktx(pl)})
    if pl.startswith(b"DDS "):
        return AG.decode_image({"kind": "dds", "data": pl})
    if pl.startswith(b"\x89PNG"):
        from io import BytesIO
        return np.asarray(Image.open(BytesIO(pl)).convert("RGBA"), dtype=np.uint8)
    return None


def export_pack(pack, wanted, fail, deadline):
    pkg = PKGDIR / pack
    if not pkg.is_file():
        for row in wanted:
            for iid in wanted[row]:
                fail[iid] = "pack_missing"
        return 0, "pack_missing"
    try:
        _rec, spans, factory = AG.open_blocks(str(pkg))
    except Exception as e:                                    # noqa: BLE001
        for row in wanted:
            for iid in wanted[row]:
                fail[iid] = "pack_open_failed:%s" % e
        return 0, "pack_open_failed"
    need = set(wanted)
    meta = {}
    for row, _fid, off, packed, decoded, flag in factory():
        if row in need:
            meta[row] = (off, packed, decoded, flag)
    fh = pkg.open("rb")
    mm = mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ)
    done = 0
    state = "done"
    try:
        size = len(mm)
        for row, ids in wanted.items():
            if time.time() > deadline:
                state = "timeout"
                break
            m = meta.get(row)
            if not m:
                for iid in ids:
                    fail[iid] = "row_missing"
                continue
            off, packed, decoded, flag = m
            h = AG._base_of(spans, row) + off
            if h + 20 > size:
                for iid in ids:
                    fail[iid] = "oob"
                continue
            hp, hd, _c1, _c2, hf = struct.unpack_from("<5I", mm, h)
            if (hp, hd, hf) != (packed, decoded, flag):
                for iid in ids:
                    fail[iid] = "header_mismatch"
                continue
            pl = AG.decompress(bytes(mm[h + 20:h + 20 + packed]), flag, decoded)
            if not pl:
                for iid in ids:
                    fail[iid] = "decompress_failed"
                continue
            try:
                rgba = decode_payload(pl)
            except Exception as e:                            # noqa: BLE001
                rgba = None
                for iid in ids:
                    fail[iid] = "decode_failed:%s" % str(e)[:40]
            if rgba is None:
                for iid in ids:
                    fail.setdefault(iid, "not_image_or_decode_failed")
                continue
            arr = np.asarray(rgba, dtype=np.uint8)
            if arr.ndim != 3 or arr.shape[2] != 4:
                for iid in ids:
                    fail[iid] = "bad_array"
                continue
            im = Image.fromarray(arr, "RGBA")
            for iid in ids:
                im.save(OUT / (iid + ".png"))
                done += 1
    finally:
        mm.close()
        fh.close()
    return done, state


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=float, default=45.0)
    ap.add_argument("--flush", type=int, default=150)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    t0 = time.time()

    board = json.loads(BOARD.read_text(encoding="utf-8"))
    items = board["items"]
    by_id = {str(it["id"]): it for it in items}
    hits = json.loads(HITS.read_text(encoding="utf-8"))
    pending = {iid: v for iid, v in hits.items()
               if not ((by_id[iid].get("_media") or {}).get("images"))}
    print("命中可补 %d ｜ 待处理 %d" % (len(hits), len(pending)))
    if not a.apply:
        print("[dry] 按包分布 top:", {k: sum(1 for v in pending.values() if v[1] == k)
                                     for k, _ in __import__("collections").Counter(
                                         v[1] for v in pending.values()).most_common(5)})
        return 0

    OUT.mkdir(parents=True, exist_ok=True)
    by_pack = {}
    for iid, (rel, pack, row) in pending.items():
        by_pack.setdefault(pack, {}).setdefault(int(row), []).append(iid)

    fail = {}
    written = 0
    dirty = 0
    deadline = t0 + a.budget
    state = "done"

    def flush_board():
        nonlocal dirty
        if not dirty:
            return
        tmp = BOARD.with_suffix(BOARD.suffix + ".tmp")
        tmp.write_text(json.dumps(board, ensure_ascii=False), encoding="utf-8")
        tmp.replace(BOARD)
        dirty = 0

    for pack in sorted(by_pack, key=lambda p: -sum(len(v) for v in by_pack[p].values())):
        if time.time() > deadline - 3:
            state = "timeout"
            break
        t1 = time.time()
        wanted = by_pack[pack]
        before = dict(fail)
        n, st = export_pack(pack, wanted, fail, deadline)
        for row, ids in wanted.items():
            for iid in ids:
                if iid in fail and iid not in before:
                    continue
            pass
        # 成功的回写
        for row, ids in wanted.items():
            for iid in ids:
                if iid in fail:
                    continue
                rel, _pk, _rw = pending[iid]
                it = by_id[iid]
                it["_media"] = {"images": [{"png": "assets/fashion_posters/%s.png" % iid,
                                            "label": "图标", "base": rel,
                                            "source": "fashion_data.icons → PE 补图 20261024"}],
                                "total": 1}
                it["icon_state"] = "有图"
                it["icon_count"] = 1
                for ic in it.get("icons_all") or []:
                    if ic.get("path") == rel:
                        ic["png"] = "assets/fashion_posters/%s.png" % iid
                written += 1
                dirty += 1
                if dirty >= a.flush:
                    flush_board()
                    print("  [落盘] 累计 %d ｜ %.1fs" % (written, time.time() - t0))
        print("  %-10s 目标 %4d 出图 %4d ｜ %.1fs ｜ 累计 %d"
              % (pack, sum(len(v) for v in wanted.values()), n, time.time() - t1, written))
        if st == "timeout":
            state = "timeout"
            break

    flush_board()
    have = sum(1 for it in items if (it.get("_media") or {}).get("images"))
    print("本轮补 %d ｜ 有图 %d/%d ｜ %s ｜ 失败 %d ｜ %.1fs"
          % (written, have, len(items), state, len(fail), time.time() - t0))
    (DET / "_fashion_pe_fail.json").write_text(json.dumps(fail, ensure_ascii=False, indent=1),
                                               encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
