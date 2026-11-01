# -*- coding: utf-8 -*-
"""探查：special_style 分布、3 条无色称号的其它字段、资源是否在 npk 内。"""
from __future__ import annotations
import collections, pathlib, struct, sys

PROJ = pathlib.Path(r"E:\la拆包项目")
CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
RES = PROJ / "01_索引与产物/41_还原树/pe/资源"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT


def decode(stem):
    p = CD / (stem + ".py"); c = CD / (stem + "_chs.py")
    raw = p.read_bytes(); at = raw.find(b"x{")
    L = struct.unpack_from("<I", raw, at + 2)[0]
    rows, _ = BT.decode_table_rows(raw[at+6:at+6+L], BT.parse_legacy_chs_pool(c.read_bytes()), resolve_jumps=False)
    return rows


def gv(r, k):
    v = r["values"].get(k)
    return v[1] if isinstance(v, tuple) else v


rows = decode("title_conf_data")
by_key = {r["key"]: r for r in rows}
sp = collections.Counter(gv(r, "special_style") for r in rows if gv(r, "special_style"))
print("special_style:", dict(sp))
print("special_style 样例 (key,name,style):")
n = 0
for r in rows:
    s = gv(r, "special_style")
    if s:
        print("   ", r["key"], gv(r, "name"), "style=%s" % gv(r, "style"), "special=", s)
        n += 1
        if n >= 8: break

for k in (319, 321, 322):
    r = by_key[k]
    d = {f: gv(r, f) for f in ("name", "style", "special_style", "shining_style", "style_icon",
                                "normal_name_icon", "ui_light", "wear_special_effects")}
    print("blank:", k, d)

# 艺术字目录内容示例
mei = RES / "ui/all_txt_meishuzi_icon/chenghao"
for d in sorted(mei.iterdir())[:5]:
    print("meishuzi", d.name, [p.name for p in list(d.iterdir())[:6]])
ch = RES / "ui/chenghao"
print("chenghao dirs:", sorted(p.name for p in ch.iterdir())[:40])


