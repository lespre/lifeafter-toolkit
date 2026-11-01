# -*- coding: utf-8 -*-
"""直接读 PE gpk 指定 row 的 payload，落盘并打印头信息（绕过 extract_raw_asset）。"""
import sys, pathlib, hashlib
PROJ = pathlib.Path(r"E:/la拆包项目")
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import android_gpk as AG

PK = PROJ / "01_索引与产物/源包/pe_gres_android/0359.gpk"
OUT = pathlib.Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
WANT = {
    1820: "bag_f_3328_high.mesh",
    1816: "bag_f_3328.mesh",
    1835: "bag_m_3328_high.mesh",
    2690: "bag_m_3328.mesh",
    2672: "bag_f_3327_high.mesh",
    932:  "bag_f_3327.mesh",
    2688: "bag_m_3327_high.mesh",
    2684: "bag_m_3327.mesh",
}
got = {}
for e in AG.iter_entries(str(PK)):
    r = e.get("row")
    if r in WANT:
        p = e["payload"]
        dst = OUT / WANT[r]
        dst.write_bytes(bytes(p))
        got[r] = (len(p), hashlib.md5(bytes(p)).hexdigest()[:12], bytes(p)[:16].hex(" "))
for r, name in WANT.items():
    print("%-24s row=%-5s %s" % (name, r, got.get(r, "未命中")))
