# -*- coding: utf-8 -*-
"""Decode common_item_data pair and look up item names for the KJ1 transfer ids."""
from __future__ import annotations
import json,struct
from pathlib import Path
BASE=Path(r'C:/Users/<user>/AppData/Local/hermes/mrzh_weapon_skin_audit/run_002/重构转印器核查_001/当前包_common_item_pair_原始只读副本/common_item_data_1232F498D07A0EBB.static.bin')
CHS=Path(r'C:/Users/<user>/AppData/Local/hermes/mrzh_weapon_skin_audit/run_002/重构转印器核查_001/当前包_common_item_pair_原始只读副本/common_item_data_chs_16037E102973F615.static.bin')
OUT=Path(r'E:/mrzh_audit/run_004_PC_BinDict与1DPW专项_001/02_bindict/KJ1转印消耗解码_006')
base=BASE.read_bytes();chs=CHS.read_bytes()
def uleb(d,p,e):
 v=0;s=0
 for _ in range(10):
  if p>=e:return None,p
  b=d[p];p+=1;v|=(b&127)<<s
  if not b&128:return v,p
  s+=7
 return None,p
q=base.find(b'x{')
print('x{ at',q,'base_len',len(base),'chs_len',len(chs))
ln=struct.unpack_from('<I',base,q+2)[0];body=base[q+6:q+6+ln]
print('body_len',len(body),'head',body[:16].hex())
# base layout: [u32 count][u32 res][ends zeros][blob]; chs: [u32 count@43][ends@47][strings]
c0=struct.unpack_from('<I',body,0)[0];te0=16+4*c0
print('count',c0,'te0(blob start)',te0)
b=body[te0:]
de=struct.unpack_from('<I',b,0)[0]
print('de',de,'marker',b[de:de+3].hex() if de+3<=len(b) else None,'blob_len',len(b))
if b[de:de+3]!=b'\x76\x01\x0b':raise SystemExit('marker mismatch at blob[de]')
# chs pool
c1=struct.unpack_from('<I',chs,43)[0]
assert c1==c0
pends=struct.unpack_from(f'<{c0}I',chs,47)
pte=47+4*c0
slots=[];last=0
for e in pends:
 slots.append(chs[pte+last:pte+e].decode('utf-8','strict'));last=e
print('slots',len(slots),'ends[-1]',pends[-1],'string_area_len',len(chs)-pte,'first',slots[:8])
t=b[de:];bc=t[3]
nodes=sorted({struct.unpack_from('<I',t,4+8*i+4)[0]>>8 for i in range(bc)})
rows=[]
for ni,s in enumerate(nodes):
 e=nodes[ni+1] if ni+1<len(nodes) else len(b);p=s
 while p<e:
  k,p=uleb(b,p,e);st,p=uleb(b,p,e);rows.append((k,st))
print('ROWS',len(rows),'key range',min(k for k,_ in rows),max(k for k,_ in rows))
K={k:st for k,st in rows}
def schema_at(ref):
 p=ref;n2,p=uleb(b,p,len(b));bits,p=uleb(b,p,len(b));fs=[]
 for ix in range(n2):
  slot,p=uleb(b,p,len(b));typ=b[p];p+=1
  fs.append({'index':ix,'slot':slot,'type':typ,'name':slots[slot] if slot<len(slots) else f'<bad{slot}>'})
 return n2,bits,fs,p
def decode(key):
 st=K[key]
 if b[st]!=0xd6:return {'key':key,'err':'not d6 at '+str(st)}
 p=st+1;sref,p=uleb(b,p,len(b));bref,p=uleb(b,p,len(b))
 n2,bits,fs,se=schema_at(sref)
 bm=b[bref:bref+(bits+7)//8]
 use=[f for f in fs if f['index']>=bits or bm[f['index']//8]&(1<<(f['index']%8))]
 vals=[]
 for f in use:
  typ=f['type']
  if typ==1:v,p=uleb(b,p,len(b))
  elif typ==3:v=b[p];p+=1
  elif typ==5:
   v,p=uleb(b,p,len(b));v=slots[v] if v<len(slots) else f'<badref{v}>'
  elif typ==11:v,p=uleb(b,p,len(b));v=f'<ref{v}>'
  elif typ==17:v,p=uleb(b,p,len(b));v=(v>>1)^(-(v&1))
  elif typ==18:v=struct.unpack_from('<f',b,p)[0];p+=4
  elif typ==34:v=struct.unpack_from('<d',b,p)[0];p+=8
  else:return {'key':key,'err':'type '+hex(typ)+' @ '+str(st)}
  vals.append({'index':f['index'],'name':f['name'],'type':hex(typ),'value':v})
 return {'key':key,'start':st,'values':vals}
targets=[150004,9137,9157,9161,9165,9515,9517,151783,151784,156182,7,80,119,26]
out={}
for k in targets:
 if k in K:
  out[k]=decode(k)
 else:
  out[k]={'key':k,'err':'key not in table'}
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'common_item_lookup_006.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for k,v in out.items():
 if 'values' in v:
  names={x['name']:x['value'] for x in v['values'] if x['name'] in ('name','e_name','s_name','icon')}
  print(k,json.dumps(names,ensure_ascii=False))
 else:print(k,v['err'])
PY