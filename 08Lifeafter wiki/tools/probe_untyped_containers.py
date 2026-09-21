# -*- coding: utf-8 -*-
import sys, os, json, collections
W = r'E:\la拆包项目\08Lifeafter wiki'
sys.path.insert(0, os.path.join(W, 'tools'))
import importlib.util
spec = importlib.util.spec_from_file_location('rws', os.path.join(W,'tools','rebuild_weapon_skin_catalog_current.py'))
M = importlib.util.module_from_spec(spec)
try: spec.loader.exec_module(M)
except SystemExit: pass

registered = M.load_current_source()
pkg = __import__('pathlib').Path(registered['path'])
reader = M.LiveNpkReader(pkg, str(registered.get('server_branch') or 'Documents snapshot'))
entries = {f'{e.file_id:016X}': e for e in reader._entries}
print('源:', pkg, '| 条目:', len(entries), flush=True)

report = {}
for role in ('common_item_base','common_item_chs','weapon_skin_base','weapon_skin_chs','weapon_skin_sfx_base','weapon_skin_behavior_base'):
    try:
        dec, meta = M.read_payload(reader, pkg, entries, M.FIDS[role], role)
        report[role] = {'len': len(dec), 'sha16': meta['decoded_sha256'][:16]}
    except Exception as e:
        report[role] = {'error': repr(e)[:120]}
print(json.dumps(report, ensure_ascii=False, indent=1), flush=True)

def probe(name, base_role, chs_role):
    dec_b,_ = M.read_payload(reader, pkg, entries, M.FIDS[base_role], base_role)
    dec_c,_ = M.read_payload(reader, pkg, entries, M.FIDS[chs_role], chs_role)
    rows, unbound = M.table_rows(dec_b, dec_c)
    unt = [r for r in rows if r.get('untyped_containers')]
    shapes = collections.Counter()
    samples = []
    for r in unt:
        for c in r['untyped_containers']:
            key = ','.join(sorted(c.keys())) if isinstance(c, dict) else 'NOT-DICT'
            shapes[key] += 1
            if len(samples) < 6:
                samples.append({'row_key': r.get('key'), 'keys': key,
                                'sample': json.dumps(c, ensure_ascii=False)[:220]})
    print('\n### %s: 行数 %d | unbound %d | 含未定型容器的行 %d' % (name, len(rows), len(unbound), len(unt)), flush=True)
    print('   形态分布:', dict(shapes), flush=True)
    for s in samples: print('   ', json.dumps(s, ensure_ascii=False)[:300], flush=True)
    return {'rows': len(rows), 'unbound': len(unbound), 'untyped_rows': len(unt), 'shapes': dict(shapes)}

res = {}
res['weapon_skin'] = probe('weapon_skin_data', 'weapon_skin_base','weapon_skin_chs')
res['common_item'] = probe('common_item_data', 'common_item_base','common_item_chs')
json.dump(res, open(os.path.join(W,'data','_untyped_probe_20260921.json'),'w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n→ data/_untyped_probe_20260921.json ✓')
