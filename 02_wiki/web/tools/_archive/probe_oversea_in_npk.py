# -*- coding: utf-8 -*-
"""检查 script npk 里能否按名字（fid）取回 oversea 表。"""
from __future__ import annotations

import sys

sys.path.insert(0, "E:/la拆包项目/02_wiki/web/tools")
sys.path.insert(0, "E:/la拆包项目/00_规范与工具/工具/工具库/00_共享核心")
import live_npk_reader as L  # noqa: E402
from toolkit_core.path_fid import fid_of  # noqa: E402

NPK = "E:/la拆包项目/01_索引与产物/源包/pe_20261020/script.py314.lc.npk"
NAMES = [
    r"com\cdata\oversea\all_equips_data_auto_oversea_data_kj1.py",
    r"com\cdata\oversea\compressed_attr_data_kj1.py",
    r"com\cdata\oversea\special_hurt_params_data_kj1.py",
    r"com\cdata\oversea\special_attr_params_data_kj1.py",
    r"com\cdata\oversea\all_equips_data_auto_oversea_data_yk.py",
    r"com\cdata\compressed_attr_data.py",
    r"com\cdata\special_hurt_params_data.py",
    r"com\cdata\special_attr_params_data.py",
    r"com\cdata\hurt_params_data.py",
    r"com\cdata\attribute_data.py",
]


def main() -> int:
    r = L.LiveNpkReader(NPK, "playertest")
    ids = {e.file_id for e in r._entries}
    print("npk 条目", len(ids))
    for n in NAMES:
        f = fid_of(n)
        print("HIT " if f in ids else "miss", "%016X" % f, n.rsplit("\\", 1)[-1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
