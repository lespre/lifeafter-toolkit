# -*- coding: utf-8 -*-
"""按 fid 在 ui_*.gpk 里定位条目并导出（只读源包）。"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, r"E:/la拆包项目/01_工具/工具库/01_解码定位复原/解包与扫描")
import la_unpack_core as core  # noqa: E402

RES = pathlib.Path(r"E:/mrzh/res")
OUT = pathlib.Path(r"E:/la拆包项目/03_执行/90_临时/ui_icons")
FIDS = {
    "3FFB31FC57B53000": "icon_touxiangkuang_01",
}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    packs = sorted(RES.glob("ui_*.gpk"))
    print("候选包", [p.name for p in packs])
    for pack in packs:
        try:
            a = core.NpkArchive(str(pack))
        except Exception as e:
            print(pack.name, "打开失败", str(e)[:60])
            continue
        hits = 0
        for ent in a.iter_entries():
            fid = "%016X" % ent.file_id
            if fid in FIDS:
                data = a.read_entry(ent)
                dest = OUT / (FIDS[fid] + ".bin")
                dest.write_bytes(data)
                print("命中", pack.name, fid, len(data), "→", dest)
                hits += 1
        print(pack.name, "条目", "扫描完成，命中", hits)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
