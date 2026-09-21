# -*- coding: utf-8 -*-
"""Decode KJ1 transfer-consume table (advanced_recipe_consume_conf) rows with the
verified BinDict codec: base x{ body + chs pool, D6 schema + bitmap + scalar + 0x0B refs.

Static read only; no payload import/marshal/eval/exec.
"""
from __future__ import annotations
import hashlib,importlib.util,json,struct,runpy
from pathlib import Path
OUT=Path(r'E:/mrzh_audit/run_004_PC_BinDict与1DPW专项_001/02_bindict/KJ1转印消耗解码_006')
PKG=Path(r'E:/mrzh/Documents/script.py314.lc.npk')
READER=Path(r'C:/Users/Administrator/AppData/Local/hermes/mrzh_weapon_skin_audit/run_002/audit_mrzh_aurora_script_presence.py')
HASHER=Path(r'C:/Users/Administrator/AppData/Local/hermes/mrzh_weapon_skin_audit/run_002/重构转印器核查_001/reextract_current_transfer_consume_tables_002.py')
M=runpy.run_path(r'C:/Users/Administrator/AppData/Local/hermes/mrzh_weapon_skin_audit/run_002/bindict_preflight_002/decode_current_all_equips_D6_scalar_006.py',run_name='ae4')
uleb=M['uleb']
def load(path,name):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
r=load(READER,'reader');h=load(HASHER,'hasher')
def sha(p):
 hh=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):hh.update(b)
 return hh.hexdigest()
def extract(logical):
 fid=h.path_id(logical)
 with PKG.open('rb') as f:
  _rr,ma,v,to,n=struct.unpack_from('<QIIII',r.aes_ecb(f.read(32)));f.seek(to);tab=r.aes_ecb(f.read(n*48))
  for i in range(n):
   row=struct.unpack_from('<QIIIIIi',tab,i*48)
   if row[0]==fid:
    f.seek(row[1]);raw=r.unpack_entry(f.read(row[2]),row[3],row[6])
    return {'fid':fid,'entry':i,'raw':raw,'archive_offset':row[1],'packed':row[2],'declared':row[3]}
 raise KeyError(logical)
def xbrace(raw):
 q=raw.find(b'x{')
 if q<0:return None
 ln=struct.unpack_from('<I',raw,q+2)[0]
 return raw[q+6:q+6+ln]
def chs_pool(chs):
 # locate [u32 count][u32 0][ends...][strings] at unaligned offset by scanning
 for off in range(0,256):
  c,res=struct.unpack_from('<II',chs,off)
  if res!=0 or not(1<=c<=6000):continue
  te=off+8+4*c
  if te>=len(chs):continue
  ends=struct.unpack_from(f'<{c}I',chs,off+8)
  if any(a>b for a,b in zip(ends,ends[1:])):continue
  if ends[-1]!=len(chs)-te:continue
  # sanity: first strings look like schema names / ascii
  s0=chs[te:te+min(ends[0],32)]
  if all(32<=x<127 for x in s0[:max(1,len(s0)-1)]) or len(s0)==0:
   return off,c,te,ends
 return None
BASE_P=r'com\cdata\oversea\advanced_recipe_consume_conf_auto_oversea_data_kj1'
CHS_P=r'com\cdata\oversea\advanced_recipe_consume_conf_auto_oversea_data_kj1_chs'
bb=extract(BASE_P+'.nxs');cb=extract(CHS_P+'.nxs')
base=bb['raw'];chs=cb['raw']
body=xbrace(base)
if body is None:raise ValueError('no x{ in base')
c0,res0=struct.unpack_from('<II',body,0);te0=8+4*c0
pool=chs_pool(chs)
print('POOL',pool)
if pool is None:raise ValueError('chs pool not found')
poff,pcount,pte,pends=pool
slots=[]
last=0
for e in pends:
 slots.append(chs[pte+last:pte+e].decode('utf-8','strict'));last=e
b=body[te0:]
de=struct.unpack_from('<I',b,0)[0]
print('de',de,'marker',b[de:de+3].hex() if de+3<=len(b) else None,'blob_len',len(b),'slots',len(slots))
if b[de:de+3]!=b'\x76\x01\x0b':raise ValueError('index marker')
t=b[de:];bc=t[3]
nodes=sorted({struct.unpack_from('<I',t,4+8*i+4)[0]>>8 for i in range(bc)})
rows=[]
for ni,s in enumerate(nodes):
 e=nodes[ni+1] if ni+1<len(nodes) else len(b);p=s
 while p<e:
  key,p=uleb(b,p,e);start,p=uleb(b,p,e);rows.append((key,start))
print('ROWS',len(rows),'keys',[k for k,_ in rows][:20])
def schema_at(ref):
 p=ref;n2,p=uleb(b,p,len(b));bits,p=uleb(b,p,len(b));fs=[]
 for ix in range(n2):
  slot,p=uleb(b,p,len(b));typ=b[p];p+=1
  fs.append({'index':ix,'slot':slot,'type':typ,'name':slots[slot] if slot<len(slots) else f'<bad{slot}>'})
 return n2,bits,fs,p
def decode_row(key,start):
 if b[start]!=0xd6:return {'key':key,'error':'not d6'}
 p=start+1;sref,p=uleb(b,p,len(b));bref,p=uleb(b,p,len(b))
 n2,bits,fs,se=schema_at(sref)
 bm=b[bref:bref+(bits+7)//8]
 use=[f for f in fs if f['index']>=bits or bm[f['index']//8]&(1<<(f['index']%8))]
 vals=[];ops=[]
 for f in use:
  typ=f['type']
  if typ==1:v,p=uleb(b,p,len(b))
  elif typ==3:v=b[p];p+=1
  elif typ==5:
   v,p=uleb(b,p,len(b));v=slots[v] if v<len(slots) else f'<badref{v}>'
  elif typ==11:v,p=uleb(b,p,len(b));ops.append((f['index'],f['name'],v));v={'opaque_jump':v}
  elif typ==17:v,p=uleb(b,p,len(b));v=(v>>1)^(-(v&1))
  elif typ==18:v=struct.unpack_from('<f',b,p)[0];p+=4
  elif typ==34:v=struct.unpack_from('<d',b,p)[0];p+=8
  else:raise ValueError(hex(typ))
  vals.append({'index':f['index'],'name':f['name'],'type':hex(typ),'value':v})
 return {'key':key,'start':start,'schema_ref':sref,'bitmap_ref':bref,'schema_n':n2,'bits':bits,'bitmap':bm.hex(),'values':vals,'ops':ops,'end':p}
dec=[]
for key,start in rows:
 try:d=decode_row(key,start)
 except Exception as e:d={'key':key,'error':repr(e)}
 dec.append(d)
ok=[d for d in dec if 'error' not in d]
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'kj1_rows_006.json').write_text(json.dumps({'rows':dec},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'decoded':len(ok),'failed':len(dec)-len(ok),'sample':ok[:3],'ops_any':sum(1 for d in ok if d['ops'])},ensure_ascii=False,indent=1))
