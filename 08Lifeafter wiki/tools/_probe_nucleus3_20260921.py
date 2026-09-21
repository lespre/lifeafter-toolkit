# -*- coding: utf-8 -*-
import sys, os, importlib.util, re
W = r'E:\la拆包项目\08Lifeafter wiki'
sys.path.insert(0, os.path.join(W,'tools'))
spec = importlib.util.spec_from_file_location('rws', os.path.join(W,'tools','rebuild_weapon_skin_catalog_current.py'))
RWS = importlib.util.module_from_spec(spec)
try: spec.loader.exec_module(RWS)
except SystemExit: pass
reg = RWS.load_current_source()
pkg = __import__('pathlib').Path(reg['path'])
reader = RWS.LiveNpkReader(pkg, str(reg.get('server_branch') or 'x'))
entries = {f'{e.file_id:016X}': e for e in reader._entries}
b,_ = RWS.read_payload(reader, pkg, entries, 'B42760CCA41DBC25','b')
c,_ = RWS.read_payload(reader, pkg, entries, 'EF3A8474A5E5F7A4','c')
rows,_u = RWS.table_rows(b,c)
def val(r,f):
    vs=r.get('values') or {}; v=vs.get(f)
    if isinstance(v,(list,tuple)) and len(v)>1: return v[1]
    return v
items=[]
for r in rows:
    k=r.get('key'); nm=str(val(r,'name') or '')
    if isinstance(k,int) and 660000<=k<=660999 and nm:
        items.append((k, nm, str(val(r,'desc') or '')))
items.sort()
print('=== 660xxx 段共 %d 颗 ===' % len(items))
for k,nm,d in items:
    flame = '霰弹' if '霰弹' in d+nm else ''
    print('  %-7s %-22s %s' % (k, nm.replace('异变核芯-',''), (flame + ' | ' if flame else '') + d[:56]))
print('\n=== 描述含「霰弹」的（= 霰弹枪核芯）===')
for k,nm,d in items:
    if '霰弹' in d+nm: print('  %-7s %s' % (k, nm))
