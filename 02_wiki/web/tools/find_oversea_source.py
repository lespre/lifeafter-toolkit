# -*- coding: utf-8 -*-
"""在多个 script npk 源里找 oversea 表的 fid，定位可恢复来源。"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, "E:/la拆包项目/02_wiki/web/tools")
sys.path.insert(0, "E:/la拆包项目/00_规范与工具/工具/工具库/00_共享核心")
import live_npk_reader as L  # noqa: E402
from toolkit_core.path_fid import fid_of  # noqa: E402

ROOT = pathlib.Path("E:/la拆包项目/01_索引与产物/源包")
NPKS = [
    ROOT / "apk_20261002/mumu_5.0.679/assets/script.py314.lc.npk",
    ROOT / "pe_20261020/script.py314.lc.npk",
    ROOT / "post_update_20260924_1610/raw/script.py314.lc.npk",
    ROOT / "post_update_20260929_2031/raw/script.py314.lc.npk",
    ROOT / "pre_update_20260924_1600/raw/script.py314.lc.npk",
]
NAMES = [
    r"com\cdata\oversea\all_equips_data_auto_oversea_data_kj1.py",
    r"com\cdata\oversea\compressed_attr_data_kj1.py",
    r"com\cdata\oversea\special_hurt_params_data_kj1.py",
    r"com\cdata\oversea\special_attr_params_data_kj1.py",
    r"com\cdata\compressed_attr_data.py",
]


def main() -> int:
    for p in NPKS:
        if not p.is_file():
            print("缺", p)
            continue
        try:
            r = L.LiveNpkReader(p, "probe")
            ids = {e.file_id for e in r._entries}
        except Exception as e:  # noqa: BLE001
            print("读失败", p.name, type(e).__name__, str(e)[:60])
            continue
        hits = []
        for n in NAMES:
            f = fid_of(n)
            if f in ids:
                hits.append(n.rsplit("\\", 1)[-1])
        print("%-58s 条目 %6d ｜ 命中 %d %s" % (str(p.relative_to(ROOT)), len(ids), len(hits), hits))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
