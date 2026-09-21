# -*- coding: utf-8 -*-
"""载具模型清单板块（图鉴类-载具）。

数据源：all_equips 装备属性表（同 weapon_attrs_table 的 BASE/CHS），载具行=含 vehicle_type 的 D6 行。
重要事实（2026-09-01 核查）：
- all_equips 载具行的 name/desc/icon 槽错位比时装更严重（混入鱼竿/霰弹枪/材料机等无关物品名），
  **不可逐行用 name 命名**；可靠锚点是 body_model 路径 + vehicle_type + item key/icon。
- 故本板块以 body_model 为主键：载具类型从路径一级目录推断（比 vehicle_type 数字码可靠），
  候选名仅在「同一系列目录内投票一致 + 含载具语素白名单 + 不含物品黑名单」时给出，标 structure；
  否则只给系列型号、名称留空标 candidate，不硬套。
- 火刑战驱（刑天载具）当前不在 all_equips（无 key194190/car_2001005），按二期奖池 gift 硬证据 verified 单列。
只读源。
"""
import re, json, hashlib, collections, importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NPK = Path("E:/mrzh/Documents/script.py314.lc.npk")
OUT = ROOT / "data" / "boards" / "vehicle_catalog.json"
spec = importlib.util.spec_from_file_location(
    "W", "E:/la拆包项目/01拆包器本体/工具库/05_BinDict解码器/weapon_attrs_table.py")
W = importlib.util.module_from_spec(spec); spec.loader.exec_module(W)

TYPE_FROM_PATH = {
    "car": "载具车", "motorcycle": "摩托车", "bicycle": "自行车", "horse": "马",
    "helicopter": "直升机", "aircraft": "飞行器", "ship": "船", "boat": "船",
    "surfboard": "冲浪板", "carriage": "马车/雪橇", "scar": "特殊载具",
}
# 载具名语素白名单（候选名需含其一）
GOOD = tuple("座骑马车翼艇船橇鲸鹰驾轮飞驰驰影铠战驱麟鸦羚豹蝎牛狮兔鱼鸟")
# 明显非载具的错位物品/描述黑名单
BAD = ("手枪", "手雷", "步枪", "霰弹", "战斧", "反曲刀", "栅栏", "材料", "炮塔", "鱼竿", "玻璃瓶",
       "骰子", "礼盒", "伤害", "场景", "玩具", "木", "操作", "只能", "受感染", "涂层", "木制", "的")


def path_type(model: str):
    m = re.search(r"carrier(?:2025)?/([a-z]+)_", model)
    if not m:
        return "特殊/未知"
    return TYPE_FROM_PATH.get(m.group(1), m.group(1))


def series_of(model: str):
    m = re.search(r"carrier(?:2025)?/([a-z]+_\d+)", model)
    return m.group(1) if m else model.split("/")[-2] if "/" in model else model


def good_name(nm: str):
    if not (isinstance(nm, str) and 2 <= len(nm) <= 14):
        return False
    if any(b in nm for b in BAD):
        return False
    if "/" in nm or "#" in nm or "。" in nm or "，" in nm:
        return False
    if not re.fullmatch(r"[一-龥A-Za-z0-9·\-・]+", nm):
        return False
    return any(g in nm for g in GOOD)


ver, slots, blob, de, ks = W.load()
records = []
for key, st in ks.items():
    if blob[st] != 0xd6:
        continue
    try:
        p = st + 1; sref, p = W.uleb(blob, p, len(blob)); bref, p = W.uleb(blob, p, len(blob))
        sn, sb, sfs, _ = W.schema_at(blob, slots, sref)
        bm = blob[bref:bref + (sb + 7) // 8]
        use = [f for f in sfs if f['i'] >= sb or bm[f['i'] // 8] & (1 << (f['i'] % 8))]
        row = {}
        for f in use:
            v, p = W.read_val(blob, f['t'], p, slots)
            if f['t'] != 11:
                row[f['name']] = v
        if 'vehicle_type' in row and row.get('body_model'):
            records.append(row)
    except Exception:
        continue

# 按 body_model 聚合，同系列投票候选名
by_model = {}
for r in records:
    mdl = r['body_model']
    a = by_model.setdefault(mdl, {'keys': set(), 'vt': set(), 'names': [], 'icons': set()})
    a['keys'].add(r.get('key')); a['vt'].add(r.get('vehicle_type'))
    if good_name(r.get('name')):
        a['names'].append(r['name'])
    if isinstance(r.get('icon'), str):
        a['icons'].add(r['icon'])

# 系列名投票（用于无名单的型号回填系列名）
series_vote = collections.defaultdict(collections.Counter)
for mdl, a in by_model.items():
    for nm in set(a['names']):
        base = re.split(r"[-・·]", nm)[0]
        series_vote[series_of(mdl)][base] += 1

items = []
for mdl, a in sorted(by_model.items()):
    vote = collections.Counter(a['names'])
    cand = vote.most_common(1)[0][0] if vote else None
    ser = series_of(mdl)
    series_name = series_vote[ser].most_common(1)[0][0] if series_vote[ser] else None
    has_name = cand is not None
    items.append({
        "id": f"veh_{len(items):04d}",
        "name": cand if has_name else f"{series_name or ser}（型号待命名）",
        "evidence": "structure" if has_name else "candidate",
        "source": "all_equips 载具行（body_model 可靠锚点；name 槽错位，候选名经系列投票+语素白名单）",
        "vehicle_class": path_type(mdl),
        "series": ser,
        "body_model": mdl,
        "vehicle_type_code": sorted(x for x in a['vt'] if x is not None),
        "item_ids": sorted(x for x in a['keys'] if x is not None),
        "candidate_names": sorted(set(a['names']))[:5] or None,
    })

# 火刑战驱（二期铠甲再临奖池硬证据，用户确认；all_equips 当前未收录其属性行）
items.insert(0, {
    "id": "veh_huoxing_zhanqu", "name": "火刑战驱（刑天载具）", "evidence": "verified",
    "source": "二期铠甲再临 super_fashion_lottery key232 panel 194190 + 用户确认（all_equips 属性表当前未收录）",
    "vehicle_class": "载具车", "series": "car_2001005",
    "body_model": "character/carrier2025/car_2001005/...", "vehicle_type_code": [3],
    "item_ids": [194190], "candidate_names": None,
})

ev = collections.Counter(it["evidence"] for it in items)
sha = hashlib.sha256(NPK.read_bytes()).hexdigest()
board = {
    "meta": {
        "name": "载具·模型清单（以 body_model 为锚）",
        "category": "图鉴类-载具",
        "source_server": "体验服 script.py314 all_equips 载具行 + 二期奖池硬证据",
        "package_sha": sha, "generated": "2026-09-01", "evidence": "structure",
        "notes": (f"{len(items)} 条（去重 body_model {len(by_model)} + 火刑战驱）。"
                  "all_equips 载具 name 槽跨记录错位严重，不逐行命名：类型从路径目录推断，"
                  "候选名经同系列投票+载具语素白名单（structure），无法确认的只给系列型号标 candidate，不硬套。"
                  f"证据分布 {dict(ev)}。火刑战驱为二期奖池 verified。vehicle_type_code 为内部码。"),
    },
    "items": items,
}
OUT.write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
print("写出", OUT.name, "条目", len(items), "证据", dict(ev))
