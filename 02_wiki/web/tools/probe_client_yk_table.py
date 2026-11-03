# -*- coding: utf-8 -*-
"""在客户端 script npk 里按逻辑路径 fid 直接取 special_hurt_params_data 的 yk 变体。"""
from __future__ import annotations

import sys

sys.path.insert(0, r"E:\la拆包项目\00_规范与工具\工具\工具库\01_解码定位复原\解包与扫描")
sys.path.insert(0, r"E:\la拆包项目\00_规范与工具\工具\工具库\00_共享核心")

import npk_reader as NR
from toolkit_core.path_fid import fid_of

NPK = r"E:\la拆包项目\90_临时\pe_client\Documents\script.py314.lc.npk"
MASK = 0xFFFFFFFFFFFFFFFF
BASE = "special_hurt_params_data"

prefixes = ["com/cdata/", "com\\cdata\\", "com/cdata/oversea/", "com\\cdata\\oversea\\"]
suffixes = [".py", ".nxs", "_yk.py", "_yk.nxs", "_kj1.py", "_chs.py",
            "_auto_oversea_data_yk.py", "_auto_oversea_data_yk.nxs",
            "_auto_oversea_data_yk_chs.py", "_auto_oversea_data_kj1.py"]


def main() -> int:
    hits = 0
    for pre in prefixes:
        for suf in suffixes:
            path = pre + BASE + suf
            f = fid_of(path)
            hx = f if isinstance(f, str) else "%016X" % (f & MASK)
            try:
                data = NR.read_entry(NPK, file_id=int(hx, 16))
            except Exception:
                continue
            if data:
                hits += 1
                print(f"HIT {path}  fid={hx}  bytes={len(data)}")
                out = r"E:\la拆包项目\90_临时\extracted2"
                import pathlib
                d = pathlib.Path(out)
                d.mkdir(parents=True, exist_ok=True)
                (d / (BASE + suf.replace("/", "_"))).write_bytes(data)
    print("命中", hits)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
