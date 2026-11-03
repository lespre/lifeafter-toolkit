#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全站补图（导出阶段）：用 common_item 图标索引给「缺图」条目下发 PNG。

目标板（item_id 即 common_item key，且图标族与 ui/item_icon 兼容）：
  lottery_periods / common_item_text_sources / chip_item_catalog

三条取图路线（按优先级）：
  1. ktx 直解码：41_还原树/pe/资源 里 <icon>_b.ktx > _s.ktx > <icon>.ktx
  2. 站内既有 png 复用：assets/item_icons_full/<icon 扁平名>.png（同路径同图，不重新解码）
  3. 都不可得 → 记源缺失（区分「PE 包内无此路径」与「未还原」）

输出目录：02_wiki/web/assets/lottery_icons/<item_id>.png（已存在则跳过）
报告：01_索引与产物/30_分析/common_item_icon_export_report.json

只读 PE 源；不改 41_还原树；不读 PC / APK。
"""
from __future__ import annotations

import json
import sqlite3
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image

PROJ = Path(r"E:\la拆包项目")
WEB = PROJ / "02_wiki/web"
RES = PROJ / "01_索引与产物/41_还原树/pe/资源"
OUT = WEB / "assets/lottery_icons"
FLAT = WEB / "assets/item_icons_full"
INDEX = PROJ / "01_索引与产物/30_分析/common_item_icon_index.json"
PE_INDEX = PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
REPORT = PROJ / "01_索引与产物/30_分析/common_item_icon_export_report.json"

sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "01_索引与产物/10_索引/热更检测/pe_icon_bind"))
from toolkit_core import android_gpk as AG  # noqa: E402
import decoders as DEC  # noqa: E402

BOARDS = ["lottery_periods", "common_item_text_sources", "chip_item_catalog"]
SUFFIXES = ("_b", "_s", "", "_sq", "_l")
PACKS = PROJ / "01_索引与产物/源包/pe_gres_android"


class Packs:
    """源包按需直读单条（pe_index 给 pack/row/off），只解一条，不整包遍历。"""

    def __init__(self) -> None:
        self._cache: dict[str, bytes] = {}

    def payload(self, pack: str, row: int, off: int, packed: int, decoded: int, flag: int):
        p = PACKS / pack
        if not p.exists():
            return None
        if pack not in self._cache:
            import struct as _s
            rec, spans, _factory = AG.open_blocks(str(p))
            self._cache[pack] = (Path(p).read_bytes(), spans)
        blob, spans = self._cache[pack]
        import struct as _s
        h = AG._base_of(spans, row) + off
        if h + 20 > len(blob):
            return None
        pay = blob[h + 20: h + 20 + packed]
        return AG.decompress(pay, flag, decoded)


def decode_bytes(data_b: bytes):
    if data_b.startswith(b"CompBlks"):
        arr = DEC.decode_compblks(data_b)
        if arr is None:
            raise ValueError("decode_compblks None")
        return np.ascontiguousarray(arr)
    info = AG.parse_ktx(data_b)
    if not info:
        raise ValueError("parse_ktx empty")
    return np.ascontiguousarray(AG._ktx_rgba(data_b, info))


def magic_bad(arr: np.ndarray) -> bool:
    """紫底/噪声守卫：RGBA 里不透明像素中 (255,0,255) 占比过高视为坏图。"""
    al = arr[:, :, 3]
    op = al > 8
    n = int(op.sum())
    if n == 0:
        return True
    px = arr[op]
    mag = (px[:, 0] > 240) & (px[:, 1] < 16) & (px[:, 2] > 240)
    return mag.sum() / n > 0.30


def png_ok(path: Path) -> tuple[bool, str]:
    try:
        with Image.open(path) as im:
            im.load()
            if im.width < 8 or im.height < 8:
                return False, "too_small"
            rgba = im.convert("RGBA")
            arr = np.array(rgba)
    except Exception as exc:  # noqa: BLE001
        return False, f"open_fail:{exc.__class__.__name__}"
    if int((arr[:, :, 3] > 8).sum()) < 16:
        return False, "empty_alpha"
    if magic_bad(arr):
        return False, "magenta_bg"
    return True, ""


def media_pngs(it: dict) -> list[str]:
    m = it.get("_media") or {}
    return [(im.get("png") or "").split("?")[0] for im in (m.get("images") or []) if isinstance(im, dict)]


def has_local_png(it: dict) -> bool:
    for p in media_pngs(it):
        if p and (WEB / p).exists():
            return True
    return False


def main() -> int:
    idx = json.loads(INDEX.read_text(encoding="utf-8"))
    icons: dict[str, str] = idx["icons"]
    local: dict[str, str] = idx["local_ktx"]

    con = sqlite3.connect(f"file:{PE_INDEX.as_posix()}?mode=ro", uri=True, timeout=60)
    pack_map = {r[0]: r[1:] for r in con.execute(
        "select name,pack,row,off,packed,decoded,flag from rows where name like 'ui/%'")}
    con.close()
    packs = Packs()

    report: dict = {
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "index": str(INDEX.relative_to(PROJ)),
        "out_dir": "02_wiki/web/assets/lottery_icons",
        "boards": {},
        "totals": {"exported_ktx": 0, "from_pack": 0, "exported_png": 0, "skipped_exists": 0,
                   "fail_missing": 0, "fail_decode": 0, "fail_unusable_png": 0},
        "fail_detail": {},
    }

    for bn in BOARDS:
        data = json.loads((WEB / f"data/boards/{bn}.json").read_text(encoding="utf-8"))
        items = data["items"]
        st = {"items": len(items), "candidates": 0, "ktx": 0, "from_pack": 0, "png_reuse": 0,
              "skipped_exists": 0, "fail_missing": 0, "fail_decode": 0, "fail_unusable_png": 0}
        fails: dict[str, list[str]] = {}
        for it in items:
            if not isinstance(it, dict) or not it.get("item_id"):
                continue
            iid = str(it["item_id"])
            if has_local_png(it):
                continue
            st["candidates"] += 1
            tgt = OUT / f"{iid}.png"
            if tgt.exists():
                st["skipped_exists"] += 1
                continue
            # 取图路径：板自身 raw 字段优先，其次索引
            ic = it.get("icon") if isinstance(it.get("icon"), str) and it["icon"].startswith("ui/") else None
            ic = ic or icons.get(iid)
            if not ic:
                st["fail_missing"] += 1
                fails.setdefault("no_index_row", []).append(iid)
                continue

            src = RES / local[iid] if iid in local else None
            ok = False
            if src is not None and src.exists():
                try:
                    arr = decode_bytes(src.read_bytes())
                    if arr.ndim != 3 or arr.shape[2] != 4 or magic_bad(arr):
                        raise ValueError("bad_rgba")
                    Image.fromarray(arr).save(tgt)
                    st["ktx"] += 1
                    ok = True
                except Exception as exc:  # noqa: BLE001
                    if tgt.exists():
                        tgt.unlink()
                    st["fail_decode"] += 1
                    fails.setdefault("decode_failed", []).append(f"{iid}:{exc.__class__.__name__}")
                    continue
            if ok:
                continue
            # 路线 1b：还原树没有、但源包里有（pe_index 定位 pack/row 直解）
            pack_hit = None
            for suf in SUFFIXES:
                r = pack_map.get(f"{ic}{suf}.ktx")
                if r:
                    pack_hit = r
                    break
            if pack_hit is not None:
                pl = packs.payload(*pack_hit) or b""
                if pl:
                    try:
                        arr = decode_bytes(pl)
                        if arr.ndim != 3 or arr.shape[2] != 4 or magic_bad(arr):
                            raise ValueError("bad_rgba")
                        Image.fromarray(arr).save(tgt)
                        st["from_pack"] += 1
                        continue
                    except Exception as exc:  # noqa: BLE001
                        if tgt.exists():
                            tgt.unlink()
                        st["fail_decode"] += 1
                        fails.setdefault("decode_failed", []).append(f"{iid}:pack:{exc.__class__.__name__}")
                        continue
            # 路线 2：站内既有 png
            flat = ic.replace("/", "_")
            cand_png = None
            for suf in ("", "_b", "_s"):
                p = FLAT / f"{flat}{suf}.png"
                if p.exists():
                    cand_png = p
                    break
            if cand_png is not None:
                good, why = png_ok(cand_png)
                if good:
                    Image.open(cand_png).convert("RGBA").save(tgt)
                    st["png_reuse"] += 1
                    continue
                st["fail_unusable_png"] += 1
                fails.setdefault("unusable_png", []).append(f"{iid}:{why}")
                continue
            # 真缺源：区分包内有/无
            st["fail_missing"] += 1
            in_pack = any(f"{ic}{s}.ktx" in pack_map for s in SUFFIXES)
            fails.setdefault("pack_has_unrestored" if in_pack else "not_in_pack", []).append(iid)

        st["exported"] = st["ktx"] + st["from_pack"] + st["png_reuse"]
        report["boards"][bn] = st
        report["fail_detail"][bn] = {k: len(v) for k, v in fails.items()}
        report["fail_detail"][bn + "_samples"] = {k: v[:5] for k, v in fails.items()}
        for k in ("ktx", "from_pack", "png_reuse", "skipped_exists", "fail_missing", "fail_decode", "fail_unusable_png"):
            key = "exported_ktx" if k == "ktx" else ("exported_png" if k == "png_reuse" else k)
            report["totals"][key] += st[k]
        print(f"{bn:28s} cand={st['candidates']:6d} ktx={st['ktx']:5d} pack={st['from_pack']:3d} png={st['png_reuse']:5d} "
              f"exists={st['skipped_exists']:5d} miss={st['fail_missing']:5d} "
              f"decode_fail={st['fail_decode']:3d} badpng={st['fail_unusable_png']:3d} "
              f"| {report['fail_detail'][bn]}")

    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print("totals:", report["totals"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
