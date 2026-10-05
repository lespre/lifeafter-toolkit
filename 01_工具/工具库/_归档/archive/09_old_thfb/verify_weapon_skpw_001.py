# -*- coding: utf-8 -*-
"""Verify weapon SKPW idx -> 1DPW chain for CSV row weapon,0.

SKPW: [header 0x20][36B entries: hash16 + u32 u32 u32 u32 u32]
Read-only on E:/mrzh.
"""
from __future__ import annotations
import hashlib,json,struct,zlib
from pathlib import Path
import zstandard as zstd
OUT=Path(r'E:/提取成果/明日拆包/output/09_thfb/weapon_1dpw_verify')
IDX=Path(r'E:/mrzh/Documents/res/weapon.idx')
WPK=Path(r'E:/mrzh/Documents/res/weapon3.wpk')
EXPECT=bytes.fromhex('dcaa9737ef96ab6a46e8c85b17ec2048')

def main():
 idx=IDX.read_bytes();wpk=WPK.read_bytes()
 assert idx[:4]==b'SKPW'
 n=struct.unpack_from('<I',idx,0x0c)[0]
 print('entries',n,'idx_size',len(idx),'expected_tail',0x20+36*n)
 # entry 0
 recs=[]
 for i in range(min(n,8)):
  off=0x20+36*i
  h=idx[off:off+16]
  f1,f2,off2,size,f5=struct.unpack_from('<IIIII',idx,off+16)
  recs.append({'i':i,'hash':h.hex(),'f1':f1,'f2':f2,'wpk_off':off2,'size':size,'f5':f5})
 print(json.dumps(recs,ensure_ascii=False,indent=1))
 r0=recs[0]
 print('entry0 hash match CSV?',r0['hash']==EXPECT.hex())
 # 1DPW chain on entry0
 off=r0['wpk_off'];size=r0['size']
 payload=wpk[off:off+size]
 print('payload',len(payload),'head',payload[:16].hex())
 # try 1DPW shell: [16B magic?][u32..] per verify_1dpw_entry logic - check header
 if payload[:4]==b'1DPW':
  print('has 1DPW shell')
 (OUT).mkdir(parents=True,exist_ok=True)
 (OUT/'weapon_entry0_payload.bin').write_bytes(payload)
 # save idx head for record
 print('done')
if __name__=='__main__':
 main()
