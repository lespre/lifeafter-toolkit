# -*- coding: utf-8 -*-
import sys, pathlib
sys.path.insert(0, r"E:/la拆包项目/00_规范与工具/工具/工具库/00_共享核心")
from toolkit_core import la_glb

files = [
    r"E:/la拆包项目/01_索引与产物/41_还原树/pe/资源/character/players2021/bag_f_3314/bag_f_3314.mesh",
    r"E:/la拆包项目/01_索引与产物/41_还原树/pe/资源/character/players2021/bag_f_3314/bag_f_3314_1_high.mesh",
    r"E:/la拆包项目/01_索引与产物/30_分析/新背包_3327_3328/src2/bag_f_3328_high.mesh",
    r"E:/la拆包项目/01_索引与产物/30_分析/新背包_3327_3328/src2/bag_m_3328_high.mesh",
]
for f in files:
    p = pathlib.Path(f)
    try:
        P, uv, idx, meta = la_glb.parse_part(str(p))
        print("%-26s size=%6d v=%5d f=%5d tri/v=%.3f sizes_ok=%s extra=%s" % (
            p.name, p.stat().st_size, len(P), len(idx),
            len(idx) / max(len(P), 1), meta.get("sizes_ok"), meta.get("extra_streams_state")))
    except Exception as e:
        print("%-26s ERR %r" % (p.name, e))
    print("   head:", p.read_bytes()[:24].hex(" "))
