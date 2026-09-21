# -*- coding: utf-8 -*-
"""Decode PC attribute_data table (base ends + chs strings) and map idx -> attribute names."""
from __future__ import annotations
import json,struct,runpy
from pathlib import Path
D=Path(r'E:/mrzh_audit/run_004_PC_BinDict与1DPW专项_001/02_bindict/attribute_data_PC静态副本_001')
OUT=Path(r'E:/mrzh_audit/run_004_PC_BinDict与1DPW专项_001/02_bindict/attribute_data_PC解析_002')
M=runpy.run_path(r'C:/Users/Administrator/AppData/Local/hermes/mrzh_weapon_skin_audit/run_002/bindict_preflight_002/decode_current_all_equips_D6_scalar_006.py',run_name='ae_mod')
uleb=M['uleb']
BASE=(D/'attribute_data_8D008E3F7EE9628C.static.bin').read_bytes()
CHS=(D/'attribute_data_chs_4D97783A1FC8AFEC.static.bin').read_bytes()
q=BASE.find(b'x{')
ln=struct.unpack_from('<I',BASE,q+2)[0];body=BASE[q+6:q+6+ln]
c,res=struct.unpack_from('<II',body,0);te=8+4*c
ends=struct.unpack_from(f'<{c}I',body,8)
assert res==0 and ends[-1]+te<=len(CHS)
# CHS string region starts at te (same layout offset as base)
slots=[]
last=0
for e in ends:
 s=CHS[te+last:te+e].decode('utf-8','strict');slots.append(s);last=e
print('SLOTS',c,'first8',slots[:8],'has_attack',any('attack' in s for s in slots))
# blob after ends table
b=body[te:]
de=struct.unpack_from('<I',b,0)[0]
print('DE',de,'marker',b[de:de+3].hex() if de+3<=len(b) else None,'blob_len',len(b))
if b[de:de+3]!=b'\x76\x01\x0b':raise ValueError('index root marker mismatch')
# rows: bucket nodes (u32 pairs, second>>8) then ULEB key/start
t=b[de:];bc=t[3]
nodes=sorted({struct.unpack_from('<I',t,4+8*i+4)[0]>>8 for i in range(bc)})
rows=[]
for ni,s in enumerate(nodes):
 e=nodes[ni+1] if ni+1<len(nodes) else len(b);p=s
 while p<e:
  key,p=uleb(b,p,e);start,p=uleb(b,p,e);rows.append((key,start))
print('ROWS',len(rows),'keys0_10',[r[0] for r in rows[:10]],'keys_last',[r[0] for r in rows[-5:]])
# decode rows: try D6 or C6 marker at value start
def decode_row(key,start):
 for marker in (0xd6,0xc6):
  if start<len(b) and b[start]==marker:
   p=start+1;schema_ref,p=uleb(b,p,len(b));bitmap_ref,p=uleb(b,p,len(b))
   try:
    sp=schema_ref;n,p2=uleb(b,sp,len(b));bits,p2=uleb(b,p2,len(b))
    if not(1<=n<=512 and 0<=bits<=n):continue
    fs=[]
    for ix in range(n):
     slot,p2=uleb(b,p2,len(b));typ=b[p2];p2+=1
     fs.append((ix,slot,typ))
    bsz=(bits+7)//8
    if not(0<=bitmap_ref and bitmap_ref+bsz<=len(b)):continue
    bitmap=b[bitmap_ref:bitmap_ref+bsz]
    use=[f for f in fs if f[0]>=bits or bitmap[f[0]//8]&(1<<(f[0]%8))]
    vals=[]
    for ix,slot,typ in use:
     if typ==1:v,p=uleb(b,p,len(b));kind='uleb'
     elif typ==3:v=b[p];p+=1;kind='bool'
     elif typ==5:
      v,p=uleb(b,p,len(b));v=slots[v] if v<len(slots) else f'<badref{v}>';kind='str'
     elif typ==18:v=struct.unpack_from('<f',b,p)[0];p+=4;kind='f32'
     elif typ==34:v=struct.unpack_from('<d',b,p)[0];p+=8;kind='f64'
     elif typ==11:v,p=uleb(b,p,len(b));v={'opaque_jump':v};kind='jump'
     elif typ==17:v,p=uleb(b,p,len(b));v=(v>>1)^(-(v&1));kind='zigzag'
     else:raise ValueError(f'type {typ:#x}')
     vals.append({'index':ix,'slot':slot,'type':hex(typ),'kind':kind,'value':v})
    return {'marker':hex(marker),'schema_ref':schema_ref,'bitmap_ref':bitmap_ref,'n':n,'bits':bits,'bitmap':bitmap.hex(),'values':vals}
   except Exception:
    continue
 return None
dec={}
for key,start in rows:
 d=decode_row(key,start)
 if d is None:print('FAIL',key,start);continue
 dec[key]=d
out=[]
for key in sorted(dec)[:80]:
 d=dec[key];m={x['index']:x for x in d['values']}
 em=m.get(6);nm=m.get(10);sn=m.get(14)
 out.append({'idx':key,'marker':d['marker'],'bitmap':d['bitmap'],'e_name':em['value'] if em else None,'name':nm['value'] if nm else None,'s_name':sn['value'] if sn else None,'field_count':len(d['values'])})
print(json.dumps(out,ensure_ascii=False,indent=1))
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'attribute_data_rows_002.json').write_text(json.dumps({'decoded':len(dec),'rows':out},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
