# -*- coding: utf-8 -*-
"""Parse PC attribute_data tables: locate CHS pool, decode base blob index, map idx->fields.

Reads only the previously extracted static copies under attribute_data_PC静态副本_001.
"""
from __future__ import annotations
import json,struct
from pathlib import Path
D=Path(r'E:/mrzh_audit/run_004_PC_BinDict与1DPW专项_001/02_bindict/attribute_data_PC静态副本_001')
OUT=Path(r'E:/mrzh_audit/run_004_PC_BinDict与1DPW专项_001/02_bindict/attribute_data_PC解析_002')
BASE=(D/'attribute_data_8D008E3F7EE9628C.static.bin').read_bytes()
CHS=(D/'attribute_data_chs_4D97783A1FC8AFEC.static.bin').read_bytes()

def uleb(d,p,e):
 v=0;s=0
 for _ in range(10):
  if p>=e:raise ValueError('uleb trunc')
  b=d[p];p+=1;v|=(b&127)<<s
  if not b&128:return v,p
  s+=7
 raise ValueError('uleb long')
def find_chs_pool(d):
 """Brute force (count,res,ends) header whose ends[-1] closes exactly at EOF."""
 best=[]
 for pos in range(0,min(len(d)-8,20000),4):
  c,res=struct.unpack_from('<II',d,pos)
  if res!=0 or not(1<=c<=4000):continue
  te=pos+8+4*c
  if te>=len(d):continue
  ends=struct.unpack_from(f'<{c}I',d,pos+8)
  if any(a>b for a,b in zip(ends,ends[1:])):continue
  if ends[-1]!=len(d)-te:continue
  # first string must look like ascii-ish or utf8
  best.append({'pos':pos,'count':c,'pool_len':len(d)-te,'first_32':d[te:te+32].hex()})
 return best

# 1) exact literal search
for term in (b'attack',b'e_attack',b'fire_speed',b'durability',b'critical_rate',b'critical_hurt',b'armor'):
 hits=[i for i in range(len(CHS)) if CHS.startswith(term,i)]
 print(term.decode(),hits[:20])
# 2) pool header candidates
print('POOL CANDIDATES',json.dumps(find_chs_pool(CHS)[:10],ensure_ascii=False))
# 3) base x{ body -> base_blob equivalent
q=255
assert BASE[q:q+2]==b'x{'
ln=struct.unpack_from('<I',BASE,q+2)[0];body=BASE[q+6:q+6+ln]
c,res=struct.unpack_from('<II',body,0);te=8+4*c
print('XBRACE',{'offset':q,'body_len':ln,'c':c,'res':res,'te':te})
if c==0:
 b=body[te:];de=struct.unpack_from('<I',b,0)[0]
 print('BLOB',{'de':de,'root_marker':b[de:de+8].hex() if de+8<=len(b) else None,'blob_len':len(b)})
