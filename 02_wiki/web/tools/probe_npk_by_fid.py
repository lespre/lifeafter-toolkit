# -*- coding: utf-8 -*-
r"""在 npk 里按 fid 找条目：解析本地 npk 的条目表（AES 头 + 32B 表项），查目标路径的 fid。

用途：gpk 里没有的图标，可能躺在 res.ui.layers.*.npk 里（客户端衣柜从那儿取）。
npk 表项结构：<Q fid, I off, I packed, I decoded, i flag> = 32B
"""
from __future__ import annotations

import argparse
import pathlib
import struct
import sys

PROJ = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/解包与扫描"))
from la_unpack_core import aes_ecb_decrypt  # noqa: E402
from toolkit_core.path_fid import fid_of  # noqa: E402


def entries(path: pathlib.Path):
    with path.open("rb") as f:
        head = aes_ecb_decrypt(f.read(48))
        if head[8:12] != b"NXPK":
            raise ValueError("不是 NXPK：%r" % head[8:12])
        table_off = struct.unpack_from("<I", head, 16)[0]
        count = struct.unpack_from("<I", head, 20)[0]
        f.seek(table_off)
        raw = f.read(count * 48)
        tbl = aes_ecb_decrypt(raw)
    for i in range(count):
        b = i * 48
        fid, off, packed, decoded = struct.unpack_from("<QIII", tbl, b)
        flag = struct.unpack_from("<i", tbl, b + 28)[0]
        yield dict(idx=i, fid=fid, off=off, packed=packed, decoded=decoded, flag=flag)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--npk", default="01_索引与产物/源包/pe_npk_20261029/res.ui.layers.1.1.npk")
    ap.add_argument("--paths", nargs="*", default=[
        "ui/item_icon/icon_b_f_3659001.ktx",
        "ui/item_icon/icon_b_m_3659001_b.ktx",
        "ui/item_icon/icon_h_f_3659001_b.ktx",
    ])
    a = ap.parse_args()

    p = PROJ / a.npk
    if not p.is_file():
        print("npk 不存在", p); return 1
    want = {fid_of(x) & 0xFFFFFFFFFFFFFFFF: x for x in a.paths}
    print(f"{p.name} {p.stat().st_size/2**20:.0f} MB ｜ 目标 {len(want)} 条")
    n = 0
    found = {}
    for e in entries(p):
        n += 1
        if e["fid"] in want:
            found[want[e["fid"]]] = e
    print("条目", n, "｜ 命中", len(found))
    for k, v in found.items():
        print("  ", k, v)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
