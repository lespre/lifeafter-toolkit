# -*- coding: utf-8 -*-
"""Decode attribute_data rows 23/35 with the verified CHS pool; print full field values."""
from __future__ import annotations
import json,struct,runpy
from pathlib import Path
D=Path(r'E:/mrzh_audit/run_004_PC_BinDict与1DPW专项_001/02_bindict/attribute_data_PC静态副本_001')
OUT=Path(r'E:/mrzh_audit/run_004_PC_BinDict与1DPW专项_001/02_bindict/attribute_data_PC解析_002')
M=runpy.run_path(r'C:/Users/Administrator/AppData/Local/hermes/mrzh_weapon_skin_audit/run_002/bindict_preflight_002/decode_current_all_equips_D6_scalar_006.py',run_name='ae');uleb=M['uleb']
BASE=(D/'attribute_data_8D008E3F7EE9628C.static.bin').read_bytes();CHS=(D/'attribute_data_chs_4D97783A1FC8AFEC.static.bin').read_bytes()
q=BASE.find(b'x{');ln=struct.unpack_from('<I',BASE,q+2)[0];body=BASE[q+6:q+6+ln]
c,res=struct.unpack_from('<II',body,0);assert (c,res)==(1404,0)
# ends from CHS at 48
ends=struct.unpack_from('<1404I',CHS,49);STR_BASE=5665
assert CHS[STR_BASE:STR_BASE+9]==b'max_value' and CHS[STR_BASE+9:STR_BASE+20]==b'attr_weight'
slots=[];last=0
for e in ends:
 slots.append(CHS[STR_BASE+last:STR_BASE+e].decode('utf-8','strict'));last=e
b=body[8+4*c:];de=struct.unpack_from('<I',b,0)[0];t=b[de:];bc=t[3]
nodes=sorted({struct.unpack_from('<I',t,4+8*i+4)[0]>>8 for i in range(bc)})
rows=[]
for ni,s in enumerate(nodes):
 e=nodes[ni+1] if ni+1<len(nodes) else len(b);p=s
 while p<e:
  k,p=uleb(b,p,e);st,p=uleb(b,p,e);rows.append((k,st))
K={k:st for k,st in rows}
def schema_of(ref):
 p=ref;n,p=uleb(b,p,len(b));bits,p=uleb(b,p,len(b));fs=[]
 for ix in range(n):
  slot,p=uleb(b,p,len(b));typ=b[p];p+=1;fs.append({'index':ix,'slot':slot,'name':slots[slot] if slot<len(slots) else f'<bad{slot}>','type':typ})
 return n,bits,fs
def decode(key):
 st=K[key];assert b[st]==0xd6
 p=st+1;sref,p=uleb(b,p,len(b));bref,p=uleb(b,p,len(b))
 n,bits,fs=schema_of(sref);bm=b[bref:bref+(bits+7)//8]
 use=[f for f in fs if f['index']>=bits or bm[f['index']//8]&(1<<(f['index']%8))]
 vals=[]
 for f in use:
  typ=f['type']
  if typ==1:v,p=uleb(b,p,len(b));kind='uleb'
  elif typ==3:v=b[p];p+=1;kind='bool'
  elif typ==5:
   v,p=uleb(b,p,len(b));v=slots[v] if v<len(slots) else f'<badref{v}>';kind='str'
  elif typ==11:v,p=uleb(b,p,len(b));v={'opaque_jump':v};kind='jump'
  elif typ==17:v,p=uleb(b,p,len(b));v=(v>>1)^(-(v&1));kind='zigzag'
  elif typ==18:v=struct.unpack_from('<f',b,p)[0];p+=4;kind='f32'
  elif typ==34:v=struct.unpack_from('<d',b,p)[0];p+=8;kind='f64'
  else:raise ValueError(hex(typ))
  vals.append({'index':f['index'],'name':f['name'],'type':hex(typ),'kind':kind,'value':v})
 return {'key':key,'start':st,'schema_ref':sref,'bitmap_ref':bref,'schema_n':n,'bits':bits,'bitmap':bm.hex(),'values':vals}
out={k:decode(k) for k in (23,35)}
print(json.dumps(out,ensure_ascii=False,indent=1))
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'attribute_data_idx23_35_full_004.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
