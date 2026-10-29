# -*- coding: utf-8 -*-
"""绕过索引，直接扫 182 个包内的 entry.fid，验证某路径到底在不在包里。

对照项：icon_mvp01（已知在）必须命中；否则说明扫描/哈希口径本身有问题。
"""
from __future__ import annotations

import pathlib
import sys


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"))
import pe_fetch as PE  # noqa: E402
from toolkit_core.path_fid import fid_of  # noqa: E402

AG = PE.AG
PACKS = PROJ / "01_索引与产物/源包/pe_gres_android"

TARGETS = {
    "icon_mvp01.png": "ui/shangcheng_icon/jingshi/icon_mvp01.png",
    "icon_mvp06.png": "ui/shangcheng_icon/jingshi/icon_mvp06.png",
    "icon_mvp06.ktx": "ui/shangcheng_icon/jingshi/icon_mvp06.ktx",
    "icon_mvp06.dds": "ui/shangcheng_icon/jingshi/icon_mvp06.dds",
    "icon_mvp06.bc7": "ui/shangcheng_icon/jingshi/icon_mvp06.bc7",
    "icon_366420_1_b.ktx": "ui/item_icon/icon_366420_1_b.ktx",
    "icon_366418_1_b.ktx": "ui/item_icon/icon_366418_1_b.ktx",
    "mvp06_nv.png": "ui/mvpvedio/vediocover/mvp06_nv.png",
}

wanted = {}
for label, path in TARGETS.items():
    wanted["%016X" % (fid_of(path) & 0xFFFFFFFFFFFFFFFF)] = label
print("待查 fid 数", len(wanted))
for f, l in wanted.items():
    print("  ", l, f)

hits = {}
packs = sorted(PACKS.glob("*.gpk"))
for i, pk in enumerate(packs, 1):
    try:
        for e in AG.iter_entries(str(pk)):
            fid = "%016X" % (e["fid"] & 0xFFFFFFFFFFFFFFFF)
            if fid in wanted:
                hits.setdefault(wanted[fid], []).append((pk.name, e["row"], e["off"]))
    except Exception as ex:  # noqa: BLE001
        print("跳过", pk.name, repr(ex)[:60])
    if i % 40 == 0:
        print("  扫到 %d/%d" % (i, len(packs)), flush=True)

print("== 结果 ==")
for label in TARGETS:
    print("%-22s %s" % (label, hits.get(label, "未命中")))
