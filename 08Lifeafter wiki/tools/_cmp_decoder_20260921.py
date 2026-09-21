# -*- coding: utf-8 -*-
import sys, os, importlib.util
W = r'E:\la拆包项目\08Lifeafter wiki'
sys.path.insert(0, os.path.join(W, 'tools'))
spec = importlib.util.spec_from_file_location('rws', os.path.join(W,'tools','rebuild_weapon_skin_catalog_current.py'))
RWS = importlib.util.module_from_spec(spec)
try: spec.loader.exec_module(RWS)
except SystemExit: pass

# 找 pool/xbody 的提供者
get = lambda m,n: getattr(m,n,None)
poolfn = get(RWS,'parse_legacy_chs_pool'); xbodyfn = get(RWS,'xbody')
if poolfn is None:
    import toolkit_core.bindict_rows as BR
    poolfn = get(BR,'parse_legacy_chs_pool'); xbodyfn = xbodyfn or get(BR,'xbody')
print('poolfn:', bool(poolfn), '| xbodyfn:', bool(xbodyfn))

def load(path, name):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    try: s.loader.exec_module(m)
    except SystemExit: pass
    return m
NEW = load(os.path.join(W,'tools','bindict_provenance.py'), 'bp_new')
OLD = load(r'C:\Users\Administrator\AppData\Local\Temp\old_bindict_provenance.py', 'bp_old')
print('NEW 有 decode:', hasattr(NEW,'decode_table_rows_with_chs_slots'), '| OLD 有:', hasattr(OLD,'decode_table_rows_with_chs_slots'))

reg = RWS.load_current_source()
pkg = __import__('pathlib').Path(reg['path'])
reader = RWS.LiveNpkReader(pkg, str(reg.get('server_branch') or 'x'))
entries = {f'{e.file_id:016X}': e for e in reader._entries}
base,_ = RWS.read_payload(reader, pkg, entries, RWS.FIDS['weapon_skin_behavior_base'], 'b')
chs,_  = RWS.read_payload(reader, pkg, entries, RWS.FIDS['weapon_skin_behavior_chs'], 'c')
body = xbodyfn(base); pool = poolfn(chs)
print('body', len(body), '| pool', len(pool))

for tag, bp in (('新(修复后)', NEW), ('旧(修复前)', OLD)):
    try:
        rows, unbound = bp.decode_table_rows_with_chs_slots(body, pool)
        keys = sorted(r['key'] for r in rows if isinstance(r.get('key'), int))
        print('\n### %s: 行 %d | unbound %d' % (tag, len(rows), len(unbound)))
        print('   含 1110036:', 1110036 in keys, '| 1110156:', 1110156 in keys, '| 1110185/6:', 1110185 in keys, 1110186 in keys)
        for sid in (1110036,1110156):
            if sid in keys:
                row=[r for r in rows if r.get('key')==sid][0]
                vs=row.get('values') or {}
                sfx=[str(v) for v in vs.values() if '.sfx' in str(v)]
                print('   %s: 字段 %d, .sfx 值 %d 条' % (sid, len(vs), len(sfx)))
                for s in sfx[:2]: print('        ', s[:88])
        if 1110036 not in keys:
            print('   样本键:', keys[:20])
    except Exception as e:
        print('\n### %s: ✗ %r' % (tag, e))
