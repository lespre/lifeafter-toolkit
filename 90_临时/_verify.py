# -*- coding: utf-8 -*-
"""对候选 (表,字段) 复核：取真实去重值，算命中值、值域、随机基线密度与 lift"""
import sys, json, pathlib, collections, os
PROJ = pathlib.Path(r'E:/la拆包项目')
sys.path.insert(0, str(PROJ / '90_临时'))
import _ref_scan as S

AGG = json.loads((PROJ / '90_临时/ref_scan_agg.json').read_text(encoding='utf-8'))
HITS = AGG['hits']

TGT = {}
for nm, key in (('fashion_data', 'F'), ('player_appear_data', 'A'),
                ('player_module_appear_data', 'M')):
    rows, _, _, _, _ = S.load_table(nm)
    TGT[key] = {int(r['key']) for r in rows}
rows, _, _, _, _ = S.load_table('fashion_data_for_export')
TGT['FID'] = {int(r['values']['fashion_id'][1]) for r in rows if 'fashion_id' in r['values']}

need = collections.defaultdict(set)
for k, lst in HITS.items():
    for h in lst:
        need[h['table']].add((h['field'], k))

S.init_worker({k: set() for k in TGT})   # 关闭扫描期命中统计，只取值


def collect(name):
    try:
        rows, unb, blob, pool, cnt = S.load_table(name)
    except Exception as e:
        return name, None, str(e)[:120]
    out = {}
    for r in rows:
        for f, v in (r.get('values') or {}).items():
            buf = []
            S.walk(blob, pool, v, buf)
            if buf:
                s = out.setdefault(f, set())
                s.update(iv for iv, _ in buf)
    return name, out, None


def stats(vals, tset):
    if not vals:
        return None
    hits = vals & tset
    lo = max(min(tset), min(vals))
    hi = min(max(tset), max(vals))
    if hi <= lo or not hits:
        return {'hit': len(hits), 'nd': len(vals), 'ratio': len(hits) / len(vals),
                'base': 0.0, 'lift': None, 'sample': sorted(hits)[:12], 'vmin': min(vals),
                'vmax': max(vals)}
    width = hi - lo + 1
    cnt_t = sum(1 for t in tset if lo <= t <= hi)
    base = cnt_t / width
    ratio = len(hits) / len(vals)
    return {'hit': len(hits), 'nd': len(vals), 'ratio': round(ratio, 4),
            'base': round(base, 6), 'lift': round(ratio / base, 2) if base else None,
            'sample': sorted(hits)[:12], 'vmin': min(vals), 'vmax': max(vals),
            'win': [lo, hi]}


if __name__ == '__main__':
    import multiprocessing as mp
    names = sorted(need)
    print('candidate tables', len(names), flush=True)
    ctx = mp.get_context('spawn')
    data = {}
    errs = {}
    with ctx.Pool(16) as pool:
        for name, out, err in pool.imap_unordered(collect, names, chunksize=4):
            if err:
                errs[name] = err
            else:
                data[name] = out
    print('decoded', len(data), 'failed', len(errs), flush=True)

    res = {}
    for tgt in ('F', 'A', 'M', 'FID'):
        rows = []
        for h in HITS[tgt]:
            t, f = h['table'], h['field']
            vals = (data.get(t) or {}).get(f)
            st = stats(vals, TGT[tgt]) if vals else None
            if not st:
                continue
            st.update({'table': t, 'field': f, 'rows': h['rows'], 'occ': h['occ'],
                       'raw_hit': h['hit'], 'raw_nd': h['nd']})
            rows.append(st)
        rows.sort(key=lambda x: (-(x['lift'] or 0), -x['ratio']))
        res[tgt] = rows
    (PROJ / '90_临时/ref_scan_verify.json').write_text(
        json.dumps(res, ensure_ascii=False), encoding='utf-8')

    for tgt in ('F', 'A', 'M'):
        rs = res[tgt]
        print(f'\n=== {tgt}: {len(rs)} 候选, lift>=5 且 ratio>=0.3: '
              f'{sum(1 for r in rs if (r["lift"] or 0) >= 5)}')
        for r in rs[:15]:
            print(f"  {r['table']}.{r['field']} hit={r['hit']}/{r['nd']} ratio={r['ratio']:.0%} "
                  f"base={r['base']:.4f} lift={r['lift']} win={r['win']} sample={r['sample'][:6]}")
    rs = res['FID']
    print(f'\n=== FID: {len(rs)} 候选; lift>=5: {sum(1 for r in rs if (r["lift"] or 0) >= 5)}')
    for r in rs[:15]:
        print(f"  {r['table']}.{r['field']} hit={r['hit']}/{r['nd']} ratio={r['ratio']:.0%} "
              f"base={r['base']:.3f} lift={r['lift']} win={r['win']} sample={r['sample'][:6]}")
