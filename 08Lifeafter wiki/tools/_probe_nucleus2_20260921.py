# -*- coding: utf-8 -*-
import sys, os, json, importlib.util, re
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
b,_ = RWS.read_payload(reader, pkg, entries, 'B42760CCA41DBC25', 'b')
c,_ = RWS.read_payload(reader, pkg, entries, 'EF3A8474A5E5F7A4', 'c')
rows, _u = RWS.table_rows(b, c)
def val(r,f):
    vs=r.get('values') or {}; v=vs.get(f)
    if isinstance(v,(list,tuple)) and len(v)>1: return v[1]
    return v
# 660000 段核芯 + 名称含"核芯"
nuc=[]
for r in rows:
    k=r.get('key')
    nm=str(val(r,'name') or '')
    if not nm: continue
    if (isinstance(k,int) and 660000<=k<661000) or ('核芯' in nm and isinstance(k,int)):
        nuc.append((k, nm, str(val(r,'desc') or '')[:80]))
print('候选核芯行:', len(nuc))
# 霰弹相关
shot=[x for x in nuc if any(w in (x[1]+x[2]) for w in ('霰弹','极寒','冰爆','强酸','酸流','连锁','爆裂','穿心','巨蛇','寒霜','霜'))]
print('\n★ 霰弹/冰系相关核芯:', len(shot))
for k,nm,d in sorted(shot): print('   %-8s %-10s %s' % (k, nm, d[:70]))
print('\n=== 全部 660000 段核芯（前 60）===')
for k,nm,d in sorted(nuc)[:60]: print('   %-8s %-10s %s' % (k, nm, d[:60]))
