# -*- coding: utf-8 -*-
"""NAMES_audit2.py — 只读补充：逐状态 id 清单、1110169/1110146 全字段、item 表存在性矩阵。
   把结果并入 NAMES_audit.json（新增 sections）。"""
import io, json, os, sys
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
WIKI = r'E:\la拆包项目\08Lifeafter wiki'
BOARD = os.path.join(WIKI, 'data', 'boards', 'weapon_skin_sfx_text_sources.json')
R = r'E:\la拆包项目\03拆包产物'
OUT = os.path.join(R, '_target_1110171')
G6 = ['1110115', '1110116', '1110117', '1110131', '1110132', '1110133', '1110142', '1110143', '1110144',
      '1110159', '1110160', '1110161', '1110173', '1110174', '1110175']
L5 = ['1110013', '1110021', '1110022', '1110024', '1110031', '1110032', '1110036', '1110121', '1110128', '1110129',
      '1110137', '1110145', '1110146', '1110151', '1110152', '1110165', '1110169', '1110171', '1110177']
L5_TIMED = ['11101451', '11101691', '11101771']

init = json.load(open(BOARD, encoding='utf-8'))
items = init['items']
by_id = {str(x.get('id')): x for x in items}
audit = json.load(open(os.path.join(OUT, 'NAMES_audit.json'), encoding='utf-8'))

L = []
# ① 逐状态 id 清单
sets = {}
for field in ('official_name_status', 'name_status', 'catalog_layer', 'version_status', 'release_state',
              'sfx_consensus_state'):
    g = defaultdict(list)
    for x in items:
        g[str(x.get(field))].append(str(x.get('id')))
    sets[field] = {k: sorted(v) for k, v in g.items()}
g = defaultdict(list)
for x in items:
    g[str((x.get('name_resolution') or {}).get('state'))].append(str(x.get('id')))
sets['name_resolution.state'] = {k: sorted(v) for k, v in g.items()}
audit['status_id_sets'] = sets
L.append('== 逐状态 id 清单')
for f, d in sets.items():
    for k, v in d.items():
        L.append('  %-22s %-52s n=%-3d %s' % (f, k, len(v), v if len(v) <= 12 else v[:12] + ['…']))

# ② 特别项全字段
audit['special_full'] = {}
for i in ('1110169', '1110146'):
    x = by_id.get(i)
    if not x:
        audit['special_full'][i] = None
        continue
    fp = x.get('field_provenance') or {}
    keep = {k: v for k, v in x.items() if k != 'field_provenance'}
    audit['special_full'][i] = {'fields': keep,
                                'field_provenance_summary': {k: {'field_chs_slot': (v or {}).get('field_chs_slot'),
                                                                 'value_chs_slot': (v or {}).get('value_chs_slot'),
                                                                 'text': (v or {}).get('text')}
                                                             for k, v in fp.items()}}
    L.append('')
    L.append('== 特别项 %s 全字段' % i)
    L.append(json.dumps(keep, ensure_ascii=False, indent=1)[:2600])
    L.append('  field_provenance 摘要: %s' % json.dumps(audit['special_full'][i]['field_provenance_summary'], ensure_ascii=False)[:900])

# ③ item 表存在性矩阵（id 归一化：int/float/str 统一）
p = os.path.join(R, 'common_item_data_rows.json')
d = json.load(open(p, encoding='utf-8'))


def norm(v):
    if v is None:
        return None
    if isinstance(v, float):
        return str(int(v)) if v == int(v) else str(v)
    return str(v)


idset = {norm(r.get('id')) for r in d['rows']}
raw_types = {}
for r in d['rows']:
    raw_types.setdefault(type(r.get('id')).__name__, 0)
    raw_types[type(r.get('id')).__name__] += 1
audit['item_table_presence'] = {'table': p, 'row_count': d.get('row_count'), 'id_types': raw_types,
                                'g6': {i: (i in idset) for i in G6},
                                'l5': {i: (i in idset) for i in L5},
                                'l5_timed': {i: (i in idset) for i in L5_TIMED}}
L.append('')
L.append('== common_item_data_rows.json 存在性（row_count=%s, id 类型分布=%s）' % (d.get('row_count'), raw_types))
miss = [i for i in G6 + L5 + L5_TIMED if i not in idset]
L.append('  缺失 id: %s' % (miss or '无'))
for i in G6 + L5 + L5_TIMED:
    if i in idset:
        continue
L.append('  逐项: %s' % json.dumps(audit['item_table_presence']['l5'], ensure_ascii=False))

# ④ 板自身 meta/stats
L.append('')
L.append('== 板 meta / stats')
L.append(json.dumps(init.get('meta'), ensure_ascii=False, indent=1)[:2000])
L.append(json.dumps(init.get('stats'), ensure_ascii=False, indent=1)[:1500])

json.dump(audit, open(os.path.join(OUT, 'NAMES_audit.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
open(os.path.join(OUT, 'NAMES_audit2.txt'), 'w', encoding='utf-8').write('\n'.join(L))
print('\n'.join(L))
