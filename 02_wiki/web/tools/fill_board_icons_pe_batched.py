# -*- coding: utf-8 -*-
"""给 common_item_text_sources 补齐图标 —— 分批落盘、可续跑版本。

与 fill_board_icons_from_pe.py 的差别（上一轮只跑出 6457 的原因）：
  1. 上一轮 `--max 8000` 是"前 N 条"上限，而不是"补齐 N 条"；
     板块 38,571 条，前 8000 条里只有 6,457 条能出图 → 后 30,335 条被 cap 直接跳过。
  2. 上一轮不区分"已有图"，也不分批落盘，中途被掐就全丢。
本脚本：
  * pending = 无 _media.images 且有 icon 字段的条目（**自动续跑**，跑过的不会再跑）
  * fid 批量 IN 查询（不做逐条 8 次点查）
  * 每 --flush-every 张 PNG 落盘一次 board；--budget 秒到点即落盘退出（退出码 0，状态写在 state 里）
  * 失败原因逐条记录（fid_not_in_index / pack_missing / row_missing / header_mismatch /
    oob / decompress_failed / compblks_undecoded / not_image / ktx_bad_header / decode_failed / bad_array）

用法：
    python fill_board_icons_pe_batched.py --board common_item_text_sources --budget 50
反复调用直到输出 "PENDING 0"。
"""
from __future__ import annotations

import argparse
import json
import mmap
import pathlib
import re
import shutil
import sqlite3
import struct
import sys
import time
from collections import Counter, defaultdict

import numpy as np
from PIL import Image

PROJ = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core.path_fid import fid_of          # noqa: E402
from toolkit_core import android_gpk as AG         # noqa: E402
DEC = None

DET = PROJ / "01_索引与产物/10_索引/热更检测"
IDX = DET / "pe_index.sqlite3"
PKGDIR = PROJ / "01_索引与产物/源包/pe_gres_android"
BOARDS = PROJ / "02_wiki/web/data/boards"
CACHE = PROJ / "02_wiki/web/assets/img_cache"
SUFFIXES = ("", "_b", "_s", "_max")
REL_CACHE = DET / ("fid_rel_cache_%s.json")       # fid -> 包内路径（索引 name 列补全用）

sys.path.insert(0, str(DET / "pe_icon_bind"))
try:
    import decoders as DEC                          # noqa: E402
except Exception:                                    # noqa: BLE001
    DEC = None


def candidates(icon: str):
    """icon 字段 → [(rel, suffix)]，按质量优先：原尺寸 → _b → _s → _max；各试 ui/ 前缀。"""
    base = icon.strip().replace("\\", "/")
    stem = re.sub(r"\.[A-Za-z0-9]{2,5}$", "", base)
    stems = [stem]
    if not stem.lower().startswith("ui/"):
        stems.append("ui/" + stem)
    out = []
    for s in stems:
        for suf in SUFFIXES:
            out.append((s + suf + ".ktx", suf))
    return out


def batch_resolve(con, icons: dict[str, str]):
    """{iid: icon} → ({iid: (pack,row,suf,rel)}, {iid: reason})。

    同一个 fid 可能被多个 id 命中（例如 icon 字段本身带 _b，与大哥 icon 的 _b 变体撞同一路径），
    所以 fid → [(rank, iid, rel, suf)] 用 list，不能用 setdefault 只留一个 ——
    否则后来者会被误判成 fid_not_in_index（已实测踩过：换一下顺序能多解出 2,567 条）。
    """
    want: dict[str, list] = {}
    for iid, icon in icons.items():
        for rank, (rel, suf) in enumerate(candidates(icon)):
            want.setdefault("%016X" % fid_of(rel), []).append((rank, iid, rel, suf))
    hit = {}
    fids = list(want)
    for i in range(0, len(fids), 800):
        chunk = fids[i:i + 800]
        q = "select fid,pack,row from rows where fid in (%s)" % ",".join("?" * len(chunk))
        for fid, pack, row in con.execute(q, chunk):
            hit[fid] = (pack, int(row))
    ok, best = {}, {}
    for fid, lst in want.items():
        h = hit.get(fid)
        if not h:
            continue
        for rank, iid, rel, suf in lst:
            if iid not in best or rank < best[iid]:
                best[iid] = rank
                ok[iid] = (h[0], h[1], suf, rel)
    miss = {iid: "fid_not_in_index" for iid in icons if iid not in ok}
    return ok, miss


def export_pack(pack: str, wanted: dict[int, list[str]], outdir: pathlib.Path,
                stats: Counter, fail: dict[str, str], flush, deadline: float) -> tuple[int, str]:
    """返回 (出图数, 状态)。状态: done / timeout / pack_missing。"""
    pkg = PKGDIR / pack
    if not pkg.is_file():
        for _row, ids in wanted.items():
            for i in ids:
                fail[i] = "pack_missing"
        stats["pack_missing"] += sum(len(v) for v in wanted.values())
        return 0, "pack_missing"
    try:
        _rec, spans, factory = AG.open_blocks(str(pkg))
    except Exception:                                        # noqa: BLE001
        stats["pack_open_failed"] += sum(len(v) for v in wanted.values())
        for _row, ids in wanted.items():
            for i in ids:
                fail[i] = "pack_open_failed"
        return 0, "pack_missing"
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
                stats["row_missing"] += len(ids)
                for i in ids:
                    fail[i] = "row_missing"
                continue
            off, packed, decoded, flag = m
            h = AG._base_of(spans, row) + off
            if h + 20 > size:
                stats["oob"] += len(ids)
                for i in ids:
                    fail[i] = "oob"
                continue
            hp, hd, _c1, _c2, hf = struct.unpack_from("<5I", mm, h)
            if (hp, hd, hf) != (packed, decoded, flag):
                stats["header_mismatch"] += len(ids)
                for i in ids:
                    fail[i] = "header_mismatch"
                continue
            data = AG.decompress(bytes(mm[h + 20:h + 20 + packed]), flag, decoded)
            if not data:
                stats["decompress_failed"] += len(ids)
                for i in ids:
                    fail[i] = "decompress_failed"
                continue
            if data.startswith(b"\xabKTX"):
                info = AG.parse_ktx(data)
                if not info:
                    stats["ktx_bad_header"] += len(ids)
                    for i in ids:
                        fail[i] = "ktx_bad_header"
                    continue
                rec = {"kind": "ktx", "data": data, "info": info}
            elif data.startswith(b"CompBlks"):
                # 二级容器：pe_icon_bind/decoders.decode_compblks 已验证（ETC2/ETC1 + 画布裁边）
                rgba = None
                if DEC is not None:
                    try:
                        rgba = DEC.decode_compblks(data)
                    except Exception:                        # noqa: BLE001
                        rgba = None
                if rgba is None:
                    stats["compblks_undecoded"] += len(ids)
                    for i in ids:
                        fail[i] = "compblks_undecoded"
                    continue
                rec = None
            elif data.startswith(b"DDS "):
                rec = {"kind": "dds", "data": data}
            elif data.startswith(b"\x89PNG"):
                rec = {"kind": "png", "data": data}
            elif data.startswith(b"CompBlks"):
                stats["compblks_undecoded"] += len(ids)
                for i in ids:
                    fail[i] = "compblks_undecoded"
                continue
            else:
                stats["not_image"] += len(ids)
                for i in ids:
                    fail[i] = "not_image"
                continue
            if rec is not None:
                try:
                    rgba = AG.decode_image(rec)
                except Exception:                            # noqa: BLE001
                    stats["decode_failed"] += len(ids)
                    for i in ids:
                        fail[i] = "decode_failed"
                    continue
            arr = np.asarray(rgba, dtype=np.uint8)
            if arr.ndim != 3 or arr.shape[2] != 4:
                stats["bad_array"] += len(ids)
                for i in ids:
                    fail[i] = "bad_array"
                continue
            im = Image.fromarray(arr, "RGBA")
            for iid in ids:
                im.save(outdir / (iid + ".png"))
                stats["png_written"] += 1
                done += 1
                flush(iid, pack, row)
    finally:
        mm.close()
        fh.close()
    return done, state


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--board", required=True)
    ap.add_argument("--budget", type=float, default=50.0, help="本进程墙钟预算（秒）")
    ap.add_argument("--flush-every", type=int, default=1500)
    ap.add_argument("--retry-failed", action="store_true", help="忽略 state 里的永久失败重试")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    t0 = time.time()

    bpath = BOARDS / (a.board + ".json")
    statep = DET / ("fill_icons_state_%s.json" % a.board)
    board = json.loads(bpath.read_text(encoding="utf-8"))
    items = board["items"]
    by_id = {str(it["id"]): it for it in items}

    state = {"failed": {}, "runs": 0, "written": 0}
    if statep.is_file():
        try:
            state = json.loads(statep.read_text(encoding="utf-8"))
        except Exception:                                    # noqa: BLE001
            pass
    failed_prev = dict(state.get("failed") or {})
    skip = set() if a.retry_failed else set(failed_prev)

    pending_icon: dict[str, str] = {}
    no_icon = 0
    for it in items:
        iid = str(it["id"])
        if (it.get("_media") or {}).get("images"):
            continue
        icon = (it.get("icon") or "").strip()
        if not icon:
            no_icon += 1
            continue
        if iid in skip:
            continue
        pending_icon[iid] = icon

    n_media0 = sum(1 for it in items if (it.get("_media") or {}).get("images"))
    print("板块 %s ｜ 条 %d ｜ 已有图 %d ｜ 待补 %d ｜ 无icon字段 %d ｜ state跳过 %d"
          % (a.board, len(items), n_media0, len(pending_icon), no_icon, len(skip)))

    con = sqlite3.connect("file:%s?mode=ro" % str(IDX).replace("\\", "/"), uri=True, timeout=10)
    ok, fail = batch_resolve(con, pending_icon)
    print("  索引命中 %d ｜ 索引无 %d" % (len(ok), len(fail)))
    if a.dry:
        c = Counter(v[0] for v in ok.values())
        print("  [dry] 包数 %d ｜ top %s" % (len(c), c.most_common(5)))
        return 0

    by_pack: dict[str, dict[int, list[str]]] = defaultdict(lambda: defaultdict(list))
    meta_ok = {}
    for iid, (pack, row, suf, rel) in ok.items():
        by_pack[pack][row].append(iid)
        meta_ok[iid] = (pack, row)

    outdir = CACHE / a.board
    outdir.mkdir(parents=True, exist_ok=True)
    stats = Counter()
    stats["fid_not_in_index"] = len(fail)

    deadline = t0 + a.budget
    written = 0
    dirty = 0

    def flush_board():
        nonlocal dirty
        if not dirty:
            return
        bak = bpath.with_suffix(bpath.suffix + ".bak_20261024_icons")
        if not bak.exists():
            shutil.copy2(bpath, bak)
        tmp = bpath.with_suffix(bpath.suffix + ".tmp")
        tmp.write_text(json.dumps(board, ensure_ascii=False), encoding="utf-8")
        tmp.replace(bpath)
        dirty = 0

    def make_flush():
        nonlocal written, dirty
        def flush(iid, pack, row):
            nonlocal written, dirty
            it = by_id[iid]
            it["_media"] = {"images": [{"png": "assets/img_cache/%s/%s.png" % (a.board, iid),
                                        "label": "图标", "pack": pack, "row": row}],
                            "total": 1}
            written += 1
            dirty += 1
            if dirty >= a.flush_every:
                flush_board()
                print("    [落盘] 累计出图 %d ｜ %.1fs" % (written, time.time() - t0))
        return flush

    flush = make_flush()
    packs = sorted(by_pack.items(), key=lambda kv: -sum(len(v) for v in kv[1].values()))
    stopped = "done"
    for pack, wanted in packs:
        if time.time() > deadline - 3:
            stopped = "timeout"
            break
        t1 = time.time()
        n, st = export_pack(pack, wanted, outdir, stats, fail, flush, deadline)
        print("  %-10s 目标 %5d 出图 %5d ｜ %.1fs ｜ 累计 %d"
              % (pack, sum(len(v) for v in wanted.values()), n, time.time() - t1, written))
        if st == "timeout":
            stopped = "timeout"
            break

    flush_board()
    n_media1 = sum(1 for it in items if (it.get("_media") or {}).get("images"))
    # 永久失败：本轮的 fail + 之前 state 的失败（未重试时保留）
    if a.retry_failed:
        merged = dict(fail)
    else:
        merged = dict(failed_prev)
        merged.update(fail)
    for iid in ok:
        merged.pop(iid, None)
    state = {"board": a.board, "failed": merged,
             "runs": int(state.get("runs") or 0) + 1,
             "written_total": int(state.get("written_total") or 0) + written,
             "media_now": n_media1, "media_target": len(items),
             "updated": time.strftime("%Y-%m-%d %H:%M:%S")}
    statep.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")

    pend = sum(1 for it in items if not (it.get("_media") or {}).get("images")
               and (it.get("icon") or "").strip() and str(it["id"]) not in skip)
    print("本轮出图 %d ｜ 有图 %d/%d ｜ 剩余可补 %d ｜ %s ｜ 失败原因 %s ｜ %.1fs"
          % (written, n_media1, len(items), pend, stopped, dict(stats), time.time() - t0))
    print("PENDING %d" % pend)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
