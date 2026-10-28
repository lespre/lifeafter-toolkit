"""probe_effect_show_build — 生成 weapon_skin_effect_show.json（皮肤ID → 战斗表现各项）。

布局（本脚本实测确认）：
  file = [263B 容器头][x{][u32 body_len][body]
  body = [u32 nrows][u32 0][nrows*4 全零占位][blob]
  blob = [u32 de][data(4..de)][index tail @ de]
  tail = 76 01 0b <bucket_count> <bucket_count * 8B (u32 key, u32 off)>
         → 每个 off 处是 bucket 链: (uleb key, uleb row_start)*
  row @ row_start = 27 0b <n> <n x uleb 记录偏移>     ← n = 该皮肤的战斗表现项数；顺序 = 面板顺序
  record @ off    = 86 0a <cold_icon><cold_label><hot_icon><hot_label><name><order>
                    07 02 01 <extra> 0b <jump>
     6 个字段的 schema 在 blob[10]: n=6 bits=0, slots 0..5 类型 05,05,05,05,05,01
     slot 名 = chs_pool[0..5] = cold_weapon_icon, cold_weapon_name, hot_weapon_icon,
                hot_weapon_name, name, order
  cold = 冷兵器(近战) 显示名/图标, hot = 热兵器(枪械) 显示名/图标
"""
import json
import os
import struct
import sys
from collections import Counter

sys.path.insert(0, r"E:/la拆包项目/00_规范与工具/工具/工具库/00_共享核心")
from toolkit_core import bindict_table as BT

BASE = r"E:/la拆包项目/01_索引与产物/41_还原树/pe/配置/com/cdata"
OUT = r"E:/la拆包项目/01_索引与产物/30_分析/weapon_skin_effect_show.json"

RAW = open(BASE + "/weapon_skin_effect_show_data.py", "rb").read()
POOL = BT.parse_legacy_chs_pool(open(BASE + "/weapon_skin_effect_show_data_chs.py", "rb").read())

p = RAW.find(b"x{")
ln = struct.unpack_from("<I", RAW, p + 2)[0]
body = RAW[p + 6:p + 6 + ln]
nrows, reserved = struct.unpack_from("<II", body, 0)
assert reserved == 0
blob = body[8 + 4 * nrows:]
de = struct.unpack_from("<I", blob, 0)[0]
assert blob[de:de + 3] == b"\x76\x01\x0b", blob[de:de + 4].hex()

# ---- 1) 扫描全部 86 0a 记录 --------------------------------------------------
records = {}
for off in range(4, de - 16):
    if blob[off] != 0x86 or blob[off + 1] != 0x0A:
        continue
    try:
        q = off + 2
        vals = []
        for _ in range(6):
            v, q = BT.uleb(blob, q, de)
            vals.append(v)
        if blob[q:q + 3] != b"\x07\x02\x01":
            continue
        q += 3
        extra, q = BT.uleb(blob, q, de)
        if blob[q] != 0x0B:
            continue
        q += 1
        jump, q = BT.uleb(blob, q, de)
    except (ValueError, IndexError):
        continue
    ci, cl, hi, hl, name, order = vals
    if not all(0 <= v < len(POOL) for v in vals):
        continue
    records[off] = dict(off=off, end=q, cold_icon=ci, cold_label=cl, hot_icon=hi,
                        hot_label=hl, name=name, order=order, extra=extra, jump=jump)
rec_starts = sorted(records)

# ---- 2) 索引行 → 组元素 → 记录 ----------------------------------------------
index_rows = BT.parse_index(blob)
result = {}
assign = Counter()
srcdelta = Counter()
for key, row_start in index_rows:
    assert blob[row_start] == 0x27, hex(blob[row_start])
    kind, n = blob[row_start + 1], blob[row_start + 2]
    assert kind == 0x0B, f"unexpected group kind {kind:#x} for {key}"
    q = row_start + 3
    elems = []
    for _ in range(n):
        v, q = BT.uleb(blob, q, de)
        elems.append(v)
    slots = []
    for pos, e in enumerate(elems, 1):
        cand = [r for r in rec_starts if 0 <= e - r <= 12]
        assert len(cand) == 1, (key, e, cand)
        rec = records[cand[0]]
        srcdelta[e - cand[0]] += 1
        item = {
            "order": pos,
            "slot": POOL[rec["hot_label"]],          # 手枪械(热兵器)面板显示名
            "slot_gun": POOL[rec["hot_label"]],
            "slot_melee": POOL[rec["cold_label"]],   # 近战(冷兵器)面板显示名
            "name": POOL[rec["name"]],
            "icon": POOL[rec["hot_icon"]],
            "icon_melee": POOL[rec["cold_icon"]],
            "record_off": rec["off"],
        }
        slots.append(item)
    result[str(key)] = slots

# ---- 3) 自检 -----------------------------------------------------------------
label_strings = set()
name_strings = set()
for r in records.values():
    label_strings |= {POOL[r["cold_label"]], POOL[r["hot_label"]]}
    name_strings.add(POOL[r["name"]])
overlap = label_strings & name_strings
dupe_slots = [k for k, v in result.items() if len({s["slot"] for s in v}) != len(v)]
print("rows(皮肤ID)", len(result), "records", len(records),
      "group elems", sum(len(v) for v in result.values()))
print("elem->record delta", dict(srcdelta))
print("label∩name 交叉污染", sorted(overlap))
print("同一皮肤内重复 slot 的皮肤", dupe_slots[:10], "共", len(dupe_slots))
print("每皮肤项数分布", Counter(len(v) for v in result.values()))
print("max order", max(max(s["order"] for s in v) for v in result.values()))

GT = [("命中效果", "辉光绽放"), ("击败特效", "咏叹终章"), ("伤害跳字", "光影游数"),
      ("攻击弹道", "辉光流转"), ("战斗音效", "咏叹之音"), ("攻击准星", "影辉锁定"),
      ("核芯联动", "决斗时刻"), ("特殊交互", "光影咏叹")]
got = result["1110171"]
print("\n=== 1110171 逐项 ===")
ok = 0
for (g_slot, g_name), item in zip(GT, got):
    hit = item["slot"] == g_slot and item["name"] == g_name
    ok += hit
    print(f"  {'OK ' if hit else 'DIFF'} got slot={item['slot']} name={item['name']}"
          f"   | expect slot={g_slot} name={g_name}"
          f"   (melee slot={item['slot_melee']})")
print(f"ground-truth match {ok}/8")

if len(got) != 8:
    print("!! 项数不是 8:", len(got))

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(result, fh, ensure_ascii=False, indent=1)
print("\nwrote", OUT, os.path.getsize(OUT), "bytes")
