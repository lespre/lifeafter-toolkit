# -*- coding: utf-8 -*-
import sys, os, json, importlib.util, re, datetime
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

def rows_of(base_fid, chs_fid, tag):
    b,_ = RWS.read_payload(reader, pkg, entries, base_fid, tag+'b')
    c,_ = RWS.read_payload(reader, pkg, entries, chs_fid, tag+'c')
    r,_u = RWS.table_rows(b, c)
    return r
def txts(rows):
    out=[]
    for r in rows:
        vs=r.get('values') or {}
        for k,v in vs.items():
            s = v[1] if isinstance(v,(list,tuple)) and len(v)>1 and isinstance(v[1],str) else (v if isinstance(v,str) else None)
            if s and re.search(r'[\u4e00-\u9fff]', s): out.append((r.get('key'),k,s))
    return out

# ① 道具总表（名字正源）
items = rows_of('B42760CCA41DBC25','EF3A8474A5E5F7A4','item')
it = txts(items)
print('道具表中文文本:', len(it))
for kw in ('冰核心','冰核','冰芯','霰弹','免控'):
    hits=[t for t in it if kw in t[2]]
    print('\n★ [%s] 命中 %d 条:' % (kw, len(hits)))
    for h in hits[:14]: print('   id=%-9s %-10s %s' % (h[0], h[1], h[2][:66]))
# ② 活动表里的
hdc = rows_of('F394516378015E27','DACF87AE00F14120','hd')
ht = txts(hdc)
for kw in ('冰核心','冰核','免控','霰弹'):
    hits=[t for t in ht if kw in t[2]]
    print('\n[活动表 %s] %d 条:' % (kw, len(hits)))
    for h in hits[:12]: print('   key=%-7s %-12s %s' % (h[0], h[1], h[2][:70]))
