# -*- coding: utf-8 -*-
"""NAMES_extract.py — 只读：从宿表逐 id 取证中文名（含表名·行号·字段），并复核 19 个 L5。
   输出 NAMES_extract.json / NAMES_extract.txt（最终交付 NAMES_g6.json 由 NAMES_build.py 生成）"""
import io, json, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
R = r'E:\la拆包项目\03拆包产物'
OUT = os.path.join(R, '_target_1110171')
G6 = ['1110115', '1110116', '1110117', '1110131', '1110132', '1110133', '1110142', '1110143', '1110144',
      '1110159', '1110160', '1110161', '1110173', '1110174', '1110175']
L5 = ['1110013', '1110021', '1110022', '1110024', '1110031', '1110032', '1110036', '1110121', '1110128', '1110129',
      '1110137', '1110145', '1110146', '1110151', '1110152', '1110165', '1110169', '1110171', '1110177']
L5_TIMED = ['11101451', '11101691', '11101771']

ITEM = os.path.join(R, 'common_item_data_rows.json')
lines = []
res = {'item_table': ITEM, 'g6': {}, 'l5': {}, 'sources': {}}

# ── ① common_item_data_rows.json：解析 + 行号
txt = open(ITEM, encoding='utf-8').read()
txt_lines = txt.splitlines()
d = json.loads(txt)
by_id = {}
for i, row in enumerate(d['rows']):
    key = row.get('id')
    if key is not None:
        by_id[str(key)] = (i, row)
res['sources']['common_item_data_rows'] = {'schema': d.get('schema'), 'row_count': d.get('row_count'),
                                           'total_lines': len(txt_lines),
                                           'id_field_line_offsets': {}}


def line_of_id(gid):
    """返回 'id': <gid> 所在行号（1-based）；同名出现多处时返回列表"""
    pat = re.compile(r'"id":\s*%s\b' % gid)
    return [i + 1 for i, ln in enumerate(txt_lines) if pat.search(ln)]


for gid in G6 + L5 + L5_TIMED:
    hit = by_id.get(gid)
    ln = line_of_id(gid)
    if hit is None:
        res['g6' if gid in G6 else 'l5'][gid] = {'found': False, 'id_line_candidates': ln}
        continue
    idx, row = hit
    rec = {'found': True, 'row_index_in_rows_array': idx, 'id_lines': ln,
           'name': row.get('name'), 'desc': row.get('desc'), 'icon': row.get('icon'),
           'level': row.get('level'), 'value': row.get('value'),
           'all_fields': {k: v for k, v in row.items() if k not in ('desc',)}}
    (res['g6'] if gid in G6 else res['l5'])[gid] = rec

# ── ② 其它表交叉命中（同一 id 的 name 字段）
CROSS = {'common_item_data.csv': os.path.join(R, 'common_item_data.csv'),
         'weapon_skin_data_rows.json': os.path.join(R, 'weapon_skin_data_rows.json'),
         'fashion_obtain_handbook_rows.json': os.path.join(R, 'fashion_obtain_handbook_rows.json'),
         'weapon_skin_data_全量.csv': os.path.join(R, 'weapon_skin_data_全量.csv'),
         'skins_grade5.json': os.path.join(R, 'batch_3d', 'skins_grade5.json')}
for label, p in CROSS.items():
    if not os.path.isfile(p):
        continue
    t = open(p, encoding='utf-8', errors='replace').read()
    e = {'bytes': os.path.getsize(p), 'ids_present': {}, 'name_field_hits': {}}
    for gid in G6 + L5 + L5_TIMED:
        c = t.count(gid)
        if c:
            e['ids_present'][gid] = c
    res['sources'][label] = e

# weapon_skin_data_rows: 是否存在 name 类键（逐 row values 键并集）
wsd = json.load(open(os.path.join(R, 'weapon_skin_data_rows.json'), encoding='utf-8'))
keyset = {}
for row in wsd['rows']:
    keyset.setdefault(row.get('key'), set()).update((row.get('values') or {}).keys())
allkeys = sorted({k for s in keyset.values() for k in s})
res['sources']['weapon_skin_data_keys'] = {'n_keys': len(allkeys), 'keys': allkeys,
                                           'name_like': [k for k in allkeys if any(x in k.lower() for x in ('name', 'title', 'chs', 'desc'))]}
for gid in G6:
    res['sources']['weapon_skin_data_keys'].setdefault('per_id', {})[gid] = sorted(keyset.get(int(gid), set()))

# skins_grade5.json 对照
g5 = json.load(open(os.path.join(R, 'batch_3d', 'skins_grade5.json'), encoding='utf-8'))
res['sources']['skins_grade5'] = g5

# ── ③ 各名字在既有产物中的命中（仅在我方目录内做一次全局扫描）
name_hits = {}
names = {r.get('name') for r in (res['g6'].values()) if isinstance(r, dict) and r.get('name')}
names |= {r.get('name') for r in (res['l5'].values()) if isinstance(r, dict) and r.get('name')}
for scan_root in (OUT, os.path.join(R, 'batch_3d')):
    for fn in sorted(os.listdir(scan_root)):
        p = os.path.join(scan_root, fn)
        if not os.path.isfile(p) or os.path.getsize(p) > 40 * 1024 * 1024:
            continue
        if os.path.splitext(fn)[1].lower() not in ('.json', '.txt', '.md', '.csv', '.log'):
            continue
        try:
            t = open(p, encoding='utf-8', errors='replace').read()
        except Exception:
            continue
        for nm in names:
            if nm and nm in t:
                name_hits.setdefault(nm, []).append(os.path.relpath(p, R))
res['name_hits_in_artifacts'] = {k: sorted(set(v))[:10] for k, v in name_hits.items()}

json.dump(res, open(os.path.join(OUT, 'NAMES_extract.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

lines.append('== G6 15 个 id 从 common_item_data_rows.json 取名（表 %d 行 / %d 行 JSON）' % (d['row_count'], len(txt_lines)))
for gid in G6:
    r = res['g6'][gid]
    lines.append('  %s → %s | rows[%s] JSON行%s | desc=%s' % (
        gid, r.get('name'), r.get('row_index_in_rows_array'), r.get('id_lines'),
        (r.get('desc') or '')[:60].replace('\n', ' ')))
lines.append('')
lines.append('== L5 19 个 id（item 表 vs skins_grade5.json）')
g5map = {str(x.get('id')): x.get('name') for x in (g5 if isinstance(g5, list) else g5.get('items', []))}
mismatch = []
for gid in L5:
    r = res['l5'].get(gid, {})
    a = r.get('name')
    b = g5map.get(gid)
    same = 'SAME' if (a == b) else 'DIFF'
    if a != b:
        mismatch.append((gid, a, b))
    lines.append('  %s item=%-10s skins_grade5=%-10s %s' % (gid, a, b, same))
lines.append('  不一致项: %s' % (mismatch or '无'))
lines.append('')
lines.append('== L5 时效变体（roster 中 11101451/11101691/11101771）')
for gid in L5_TIMED:
    r = res['l5'].get(gid, {})
    lines.append('  %s item=%s skins_grade5=%s' % (gid, r.get('name'), g5map.get(gid)))
lines.append('')
lines.append('== weapon_skin_data_rows 键（%d 个）name-like=%s' % (
    res['sources']['weapon_skin_data_keys']['n_keys'], res['sources']['weapon_skin_data_keys']['name_like']))
lines.append('   示例 per_id 1110115: %s' % res['sources']['weapon_skin_data_keys'].get('per_id', {}).get('1110115'))
lines.append('')
lines.append('== 各表 id 命中：')
for label, e in res['sources'].items():
    if isinstance(e, dict) and e.get('ids_present') is not None:
        lines.append('   %-34s ids命中=%d 个' % (label, len(e['ids_present'])))
lines.append('')
lines.append('== 名字在既有产物中的命中：')
for nm, fs in sorted(res['name_hits_in_artifacts'].items()):
    lines.append('   %-10s %s' % (nm, fs))
open(os.path.join(OUT, 'NAMES_extract.txt'), 'w', encoding='utf-8').write('\n'.join(lines))
print('\n'.join(lines))
