#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A 层补图：奖池板上「索引里有 local_ktx 但 assets/lottery_icons/<id>.png 不存在」的 id。

索引：01_索引与产物/30_分析/common_item_icon_index.json
  local_ktx[id] = "ui/item_icon/icon_850001_b.ktx"（相对 41_还原树/pe/资源 的路径）
解码：CompBlks 先 decoders.decode_compblks；KTX 走 android_gpk.parse_ktx + _ktx_rgba
     （RGBA8_ETC2_EAC，禁用 texture2ddecoder.decode_astc）
输出：02_wiki/web/assets/lottery_icons/<item_id>.png（已存在跳过）
只读 PE 源；不改 41_还原树；不改板。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

PROJ = Path(r"E:\la拆包项目")
WEB = PROJ / "02_wiki/web"
RES = PROJ / "01_索引与产物/41_还原树/pe/资源"
OUT = WEB / "assets/lottery_icons"
INDEX = PROJ / "01_索引与产物/30_分析/common_item_icon_index.json"
REPORT = PROJ / "01_索引与产物/30_分析/lottery_icons_fill_index_report.json"

sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "01_索引与产物/10_索引/热更检测/pe_icon_bind"))
from toolkit_core import android_gpk as AG  # noqa: E402
import decoders as DEC  # noqa: E402


def decode_bytes(data: bytes) -> np.ndarray:
    if data.startswith(b"CompBlks"):
        arr = DEC.decode_compblks(data)
        if arr is None:
            raise ValueError("decode_compblks None")
        return np.asarray(arr)
    info = AG.parse_ktx(data)
    if not info:
        raise ValueError("parse_ktx empty")
    return np.asarray(AG._ktx_rgba(data, info))


def magenta_ratio(arr: np.ndarray) -> float:
    if arr.ndim != 3 or arr.shape[2] < 3:
        return 1.0
    m = (arr[..., 0] > 240) & (arr[..., 1] < 16) & (arr[..., 2] > 240)
    op = arr[..., 3] > 8 if arr.shape[2] == 4 else np.ones(arr.shape[:2], bool)
    n = int(op.sum())
    return 0.0 if n == 0 else float(m[op].mean())


def main() -> int:
    idx = json.loads(INDEX.read_text(encoding="utf-8"))
    local = idx.get("local_ktx") or {}

    board = json.loads((WEB / "data/boards/lottery_periods.json").read_text(encoding="utf-8"))
    ids = list(dict.fromkeys(str(i["item_id"]) for i in board["items"] if isinstance(i, dict) and i.get("item_id")))

    OUT.mkdir(parents=True, exist_ok=True)
    rep = {"ids": len(ids), "candidates": 0, "exported": 0,
           "skipped_exists": 0, "fail_no_file": [], "fail_decode": [], "fail_bad": []}

    for iid in ids:
        tgt = OUT / f"{iid}.png"
        if tgt.exists():
            rep["skipped_exists"] += 1
            continue
        rel = local.get(iid)
        if not rel:
            continue
        rep["candidates"] += 1
        src = RES / rel.replace("/", "\\")
        if not src.exists():
            rep["fail_no_file"].append({"id": iid, "path": rel})
            continue
        try:
            arr = decode_bytes(src.read_bytes())
        except Exception as exc:  # noqa: BLE001
            rep["fail_decode"].append({"id": iid, "path": rel, "err": f"{type(exc).__name__}:{exc}"})
            continue
        if arr.ndim != 3 or arr.shape[2] != 4 or int((arr[..., 3] > 8).sum()) < 16:
            rep["fail_bad"].append({"id": iid, "path": rel, "why": "bad_rgba_or_empty"})
            continue
        if magenta_ratio(arr) > 0.30:
            rep["fail_bad"].append({"id": iid, "path": rel, "why": "magenta"})
            continue
        Image.fromarray(np.ascontiguousarray(arr.astype("uint8"))).save(tgt)
        rep["exported"] += 1

    rep["fail_no_file_n"] = len(rep["fail_no_file"])
    rep["fail_decode_n"] = len(rep["fail_decode"])
    rep["fail_bad_n"] = len(rep["fail_bad"])
    REPORT.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"A层: ids={rep['ids']} cand={rep['candidates']} exported={rep['exported']} "
          f"exists={rep['skipped_exists']} nofile={rep['fail_no_file_n']} "
          f"decode={rep['fail_decode_n']} bad={rep['fail_bad_n']}")
    for k in ("fail_no_file", "fail_decode", "fail_bad"):
        for s in rep[k][:5]:
            print("  ", k, s)
    return 0


if __name__ == "__main__":
    sys.exit(main())
