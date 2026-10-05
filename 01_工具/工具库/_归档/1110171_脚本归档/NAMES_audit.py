# -*- coding: utf-8 -*-
"""NAMES_audit.py — 只读：核对 wiki 板数据（weapon_skin_sfx_text_sources.json, 115 条）的名字/身份可靠性。
   交付 NAMES_audit.json + NAMES_audit.txt"""
import io, json, os, sys
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
WIKI = r'E:\la拆包项目\08Lifeafter wiki'
BOARD = os.path.join(WIKI, 'data', 'boards', 'weapon_skin_sfx_text_sources.json')
R = r'E:\la拆包项目\03拆包产物'
OUT = os.path.join(R, '_target_1110171')
G6_GROUPS = [('赤月晶魄', ['1110115', '1110116', '1110117']), ('炽日耀斑', ['1110131', '1110132', '1110133']),
             ('金乌负日', ['1110142', '1110143', '1110144']), ('沙海月鸣', ['1110159', '1110160', '1110161']),
             ('水晶玫瑰', ['1110173', '1110174', '1110175'])]
SPECIAL = ['1110169', '1110146']

init = json.load(open(BOARD, encoding='utf-8'))
items = init['items']
by_id = {str(x.get('id')): x for x in items}
res = {'board': {'path': BOARD, 'bytes': os.path.getsize(BOARD), 'n_items': len(items),
                 'meta': init.get('meta'), 'stats': init.get('stats')},
       'field_inventory': {}, 'name_status_counts': {}, 'non_official': [], 'g6_groups': {}, 'special': {},
       'cross_check_item_table': {}}

# ── 字段清单
keys = Counter()
for x in items:
    keys.update(x.keys())
res['field_inventory'] = dict(keys)
res['has_fields'] = {k: (k in keys) for k in ('weapon_type', 'weapon_type_label', 'release_state', 'level',
                                              'official_name_status', 'name_status', 'name_display',
                                              'name_resolution', 'field_provenance', 'catalog_layer',
                                              'version_status', 'charm_value', 'official_desc')}

# ── 状态统计
for field in ('official_name_status', 'name_status', 'catalog_layer', 'version_status', 'sfx_consensus_state', 'release_state'):
    if field in keys:
        res['name_status_counts'][field] = dict(Counter(str(x.get(field)) for x in items))
if 'name_resolution' in keys:
    res['name_status_counts']['name_resolution.state'] = dict(Counter(str((x.get('name_resolution') or {}).get('state')) for x in items))


def is_official(x):
    return (str(x.get('official_name_status')) == 'verified') or (str(x.get('name_status')) == 'verified') \
        or (str((x.get('name_resolution') or {}).get('state')) == 'verified')


for x in items:
    if not is_official(x):
        res['non_official'].append({
            'id': str(x.get('id')), 'name': x.get('name'), 'name_display': x.get('name_display'),
            'official_name_status': x.get('official_name_status'), 'name_status': x.get('name_status'),
            'name_resolution': x.get('name_resolution'), 'catalog_layer': x.get('catalog_layer'),
            'version_status': x.get('version_status'), 'model_path': x.get('model_path'),
            'release_state': x.get('release_state'), 'official_desc': (x.get('official_desc') or '')[:120]})

# ── 5 组 G6 关系
for nm, ids in G6_GROUPS:
    rows = []
    for i in ids:
        x = by_id.get(i)
        if not x:
            rows.append({'id': i, 'found': False})
            continue
        rows.append({'id': i, 'found': True, 'name': x.get('name'), 'name_display': x.get('name_display'),
                     'weapon_type': x.get('weapon_type'), 'weapon_type_label': x.get('weapon_type_label'),
                     'level': x.get('level'), 'model_path': x.get('model_path'),
                     'catalog_layer': x.get('catalog_layer'), 'version_status': x.get('version_status'),
                     'name_status': x.get('name_status'), 'official_name_status': x.get('official_name_status'),
                     'release_state': x.get('release_state'), 'charm_value': x.get('charm_value'),
                     'official_desc': (x.get('official_desc') or '')[:160]})
    wt = {r.get('weapon_type') for r in rows if r.get('found')}
    wtl = {r.get('weapon_type_label') for r in rows if r.get('found')}
    nm_set = {r.get('name') for r in rows if r.get('found')}
    st = {r.get('name_status') for r in rows if r.get('found')}
    md = [r.get('model_path') for r in rows if r.get('found')]
    res['g6_groups'][nm] = {'ids': ids, 'rows': rows, 'same_name': len(nm_set) == 1,
                            'same_weapon_type': len(wt) == 1, 'weapon_types': sorted(str(v) for v in wt),
                            'weapon_type_labels': sorted(str(v) for v in wtl),
                            'same_name_status': len(st) == 1, 'name_statuses': sorted(str(v) for v in st),
                            'distinct_model_paths': len(set(md)), 'model_paths': md}

# ── 特别项
for i in SPECIAL:
    x = by_id.get(i)
    res['special'][i] = None if not x else {
        'name': x.get('name'), 'name_display': x.get('name_display'),
        'official_name_status': x.get('official_name_status'), 'name_status': x.get('name_status'),
        'name_resolution': x.get('name_resolution'), 'release_state': x.get('release_state'),
        'catalog_layer': x.get('catalog_layer'), 'version_status': x.get('version_status'),
        'model_path': x.get('model_path'), 'weapon_type': x.get('weapon_type'),
        'weapon_type_label': x.get('weapon_type_label'), 'level': x.get('level'),
        'official_desc': x.get('official_desc'), 'sfx_consensus_state': x.get('sfx_consensus_state')}

# ── 二级旁证：common_item_data_rows.json 的同 id name/desc（既有 JSON，只读）
p = os.path.join(R, 'common_item_data_rows.json')
if os.path.isfile(p):
    d = json.load(open(p, encoding='utf-8'))
    m = {str(r.get('id')): r for r in d['rows']}
    for nm, ids in G6_GROUPS:
        for i in ids:
            r = m.get(i)
            res['cross_check_item_table'][i] = None if not r else {'name': r.get('name'), 'desc': r.get('desc')}

json.dump(res, open(os.path.join(OUT, 'NAMES_audit.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

L = []
L.append('板数据: %s (%d B, %d 条)  meta=%s' % (BOARD, res['board']['bytes'], res['board']['n_items'],
                                              json.dumps(init.get('meta'), ensure_ascii=False)[:300]))
L.append('字段存在性: %s' % json.dumps(res['has_fields'], ensure_ascii=False))
L.append('')
L.append('== 状态统计')
for k, v in res['name_status_counts'].items():
    L.append('  %-22s %s' % (k, json.dumps(v, ensure_ascii=False)))
L.append('')
L.append('== 非 official 条目（%d 条）' % len(res['non_official']))
for r in res['non_official']:
    L.append('  %s name=%-10s official=%s name_status=%s state=%s layer=%s release=%s' % (
        r['id'], r['name'], r['official_name_status'], r['name_status'],
        (r['name_resolution'] or {}).get('state'), r['catalog_layer'], r['release_state']))
L.append('')
L.append('== G6 五组关系')
for nm, g in res['g6_groups'].items():
    L.append('  [%s] same_name=%s same_weapon_type=%s(=%s/%s) name_status=%s distinct_model_paths=%s' % (
        nm, g['same_name'], g['same_weapon_type'], g['weapon_types'], g['weapon_type_labels'],
        g['name_statuses'], g['distinct_model_paths']))
    for r in g['rows']:
        L.append('      %s wt=%-4s label=%-12s level=%-3s path=%s' % (
            r['id'], r.get('weapon_type'), r.get('weapon_type_label'), r.get('level'), r.get('model_path')))
        L.append('          desc=%s' % (r.get('official_desc') or ''))
L.append('')
L.append('== 特别项')
for i, s in res['special'].items():
    L.append('  %s %s' % (i, json.dumps(s, ensure_ascii=False)[:900]))
    L.append('      item_table: %s' % json.dumps(res['cross_check_item_table'].get(i), ensure_ascii=False)[:260])
L.append('')
L.append('== item 表旁证（既有 JSON common_item_data_rows.json）')
for nm, ids in G6_GROUPS:
    for i in ids:
        c = res['cross_check_item_table'].get(i) or {}
        L.append('  %s item_name=%-8s desc=%s' % (i, c.get('name'), (c.get('desc') or '')[:90]))
open(os.path.join(OUT, 'NAMES_audit.txt'), 'w', encoding='utf-8').write('\n'.join(L))
print('\n'.join(L))
