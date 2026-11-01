# -*- coding: utf-8 -*-
"""探查称号板剩余缺口：留空颜色、动画/艺术字资源是否存在、未用字段。"""
from __future__ import annotations
import json, pathlib, sys, collections

PROJ = pathlib.Path(r"E:\la拆包项目")
CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
RES = PROJ / "01_索引与产物/41_还原树/pe/资源"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT
import struct


def decode(stem):
    p = CD / (stem + ".py"); c = CD / (stem + "_chs.py")
    if not (p.is_file() and c.is_file()): return []
    raw = p.read_bytes(); at = raw.find(b"x{")
    if at < 0: return []
    L = struct.unpack_from("<I", raw, at + 2)[0]
    rows, _ = BT.decode_table_rows(raw[at+6:at+6+L], BT.parse_legacy_chs_pool(c.read_bytes()), resolve_jumps=False)
    return rows


def gv(r, k):
    v = r["values"].get(k)
    v = v[1] if isinstance(v, tuple) else v
    return v


rows = decode("title_conf_data")
print("rows", len(rows))

# 1. 留空颜色的条目
blank = []
for r in rows:
    st = gv(r, "style")
    if st is None or st == "":
        blank.append((r["key"], gv(r, "name"), "style=none"))
    elif int(st) not in (1, 2, 3, 4, 8):
        blank.append((r["key"], gv(r, "name"), "style=%s" % st))
print("留空颜色 %d:" % len(blank))
for k, n, s in blank: print("   ", k, n, s)

# 2. 动画资源存在性
shining = {r["key"]: r for r in decode("shining_title_conf_data")}
print("shining rows", len(shining))
anim_used = []
for r in rows:
    ss = gv(r, "shining_style")
    if ss not in (None, ""):
        a = shining.get(int(ss))
        anim_used.append((r["key"], gv(r, "name"), int(ss), gv(a, "cocos_csb") if a else None))
miss_anim = 0
for k, n, ss, p in anim_used:
    if not p: miss_anim += 1; print("   无 csb:", k, n, ss); continue
    fp = RES / p.replace("\\", "/")
    if not fp.is_file(): miss_anim += 1; print("   文件缺失:", k, n, p)
print("动态引用 %d, 缺失 %d" % (len(anim_used), miss_anim))

# 3. 艺术字存在性
arts = []
for r in rows:
    a = gv(r, "style_icon") or gv(r, "normal_name_icon")
    if a: arts.append((r["key"], gv(r, "name"), a))
miss_art = 0
bad_art = []
for k, n, p in arts:
    fp = RES / str(p).replace("\\", "/")
    if not fp.is_file(): miss_art += 1; bad_art.append((k, n, p))
print("艺术字 %d, 缺失文件 %d" % (len(arts), miss_art))
for x in bad_art[:8]: print("   ", x)

# 4. 其它未用字段分布
for f in ("special_style", "wear_special_effects", "ui_light", "can_repeated_gain",
          "default_life_time", "ui_chat_visible", "buff_ids", "get_title_mail", "quest_params",
          "start_times", "end_times", "shining_style_opacity", "buff_levels"):
    vals = [gv(r, f) for r in rows if gv(r, f) not in (None, "")]
    print(f, len(vals), "样例:", vals[:3])

# 5. 资源目录对比
dirs_mei = RES / "ui/all_txt_meishuzi_icon/chenghao"
dirs_ch = RES / "ui/chenghao"
print("meishuzi 目录数", len(list(dirs_mei.iterdir())) if dirs_mei.is_dir() else "NA")
print("chenghao 目录数", len(list(dirs_ch.iterdir())) if dirs_ch.is_dir() else "NA")
print("chenghao_icon 文件:")
ic = RES / "ui/chenghao_icon"
if ic.is_dir(): print("   ", sorted(p.name for p in ic.iterdir())[:60])
