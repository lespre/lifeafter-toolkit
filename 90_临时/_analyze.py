# -*- coding: utf-8 -*-
"""聚合 ref_scan_cache.jsonl -> 结构化结果"""
import json, pathlib, collections, re, sys

PROJ = pathlib.Path(r'E:/la拆包项目')
TMP = PROJ / '90_临时'
CACHE = TMP / 'ref_scan_cache.jsonl'

recs = []
for ln in CACHE.read_text(encoding='utf-8').splitlines():
    if ln.strip():
        recs.append(json.loads(ln))

ok = [r for r in recs if r['ok'] == 1]
print('tables', len(recs), 'decoded', len(ok), 'rows_total', sum(r['n'] for r in ok))

NAMES = {'F': 'fashion_data.key', 'A': 'player_appear_data.key',
         'M': 'player_module_appear_data.key', 'FID': 'fashion_id(序号)'}
IDX = {'F': 3, 'A': 5, 'M': 7, 'FID': 9}
SIDX = {'F': 4, 'A': 6, 'M': 8, 'FID': 10}

MIN_HIT = 5
MIN_RATIO = 0.30

hits = {k: [] for k in NAMES}
for r in ok:
    for f in r['f']:
        name, occ, nd = f[0], f[1], f[2]
        for k in NAMES:
            h = f[IDX[k]]
            hs = f[SIDX[k]]
            if h >= MIN_HIT and nd and h / nd >= MIN_RATIO:
                hits[k].append({'table': r['t'], 'field': name, 'hit': h,
                                'nd': nd, 'ratio': round(h / nd, 4), 'rows': r['n'],
                                'occ': occ, 'hit_from_str': hs})

for k in NAMES:
    hits[k].sort(key=lambda x: (-x['hit'], -x['ratio'], x['table']))
    print(f'\n=== {NAMES[k]} 命中 {len(hits[k])} 个 (表,字段)')
    for h in hits[k][:25]:
        print(f"  {h['table']}.{h['field']}  hit={h['hit']}/{h['nd']}={h['ratio']:.0%} rows={h['rows']} str={h['hit_from_str']}")

# 表级被引用次数
for k in NAMES:
    c = collections.Counter()
    for h in hits[k]:
        c[h['table']] += 1
    print(f'\n--- {NAMES[k]} 表级 top10:', c.most_common(10))

# 字段名扫描 Q4
PAT = re.compile(r'fashion|appear|model_id|model_name|dress|outfit|suit|hair|hat|icon|skin', re.I)
fn = collections.defaultdict(lambda: {'tables': 0, 'rows': 0, 'cols': set(), 'tbls': []})
for r in ok:
    for k in (r.get('allf') or {}):
        if PAT.search(k):
            d = fn[k]
            d['tables'] += 1
            d['rows'] += r['n']
            d['cols'].add(r['t'])
print('\n=== Q4 字段名命中去重字段数:', len(fn))
for k, d in sorted(fn.items(), key=lambda x: (-x[1]['tables'], -x[1]['rows']))[:70]:
    print(f'  {k:38s} tables={d["tables"]:5d} rows={d["rows"]:7d}')

out = {'hits': hits, 'fieldnames': {k: {'tables': v['tables'], 'rows': v['rows'],
                                        'cols': sorted(v['cols'])} for k, v in fn.items()},
       'tables': len(recs), 'decoded': len(ok)}
(TMP / 'ref_scan_agg.json').write_text(json.dumps(out, ensure_ascii=False), encoding='utf-8')
print('\nsaved ref_scan_agg.json')
