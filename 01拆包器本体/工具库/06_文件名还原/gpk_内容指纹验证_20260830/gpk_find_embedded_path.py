# -*- coding: utf-8 -*-
"""GPK step4：在解压内容里找自带路径字符串的条目，建立 路径->(c1,c2) 真实配对。"""
import struct, re
from pathlib import Path
from Crypto.Cipher import AES
import lz4.block, zstandard as zstd
AES_KEY=bytes.fromhex('606308d8a32c782013d26c2f226f686d')
dctx=zstd.ZstdDecompressor()
PATH_RE=re.compile(rb'[A-Za-z0-9_/\\.\-]{3,}\.(?:gim|mesh|dds|png|c159|mat|rgis|anim|tga|fx|prefab|sfx|fsb)')

def all_entries(path):
    cipher=AES.new(AES_KEY,AES.MODE_ECB); fs=path.stat().st_size
    with open(path,'rb') as f: head=f.read(120*1024*1024)
    pt=cipher.decrypt(head+b'\x00'*((16-len(head)%16)%16))
    B=struct.unpack_from('<I',pt,20)[0]
    if 64+B*32>len(pt):
        with open(path,'rb') as f: head=f.read(64+B*32+64)
        pt=cipher.decrypt(head+b'\x00'*((16-len(head)%16)%16))
    out=[]
    for i in range(B):
        o,cp,dp,c1,c2,fl=struct.unpack_from('<IIIIII',pt,64+i*32)
        if o>=64 and o+36+cp<=fs and fl in (0,2,12): out.append((i,o,cp,dp,c1,c2,fl))
    return out

p=Path(r"E:/mrzh/res/weapon.gpk")
es=all_entries(p)
print("条目:",len(es))
found=[]
with open(p,'rb') as f:
    # 先看第一条 flag=0 的原始内容
    for (i,o,cp,dp,c1,c2,fl) in es[:3000]:
        f.seek(o+36); seg=f.read(cp)
        try:
            if fl==0: d=seg
            elif fl==2: d=lz4.block.decompress(seg,uncompressed_size=dp)
            else: d=dctx.decompress(seg,max_output_size=dp+4096)
        except: continue
        ms=PATH_RE.findall(d)
        if ms:
            found.append((i,c1,c2,fl,sorted(set(m.decode('latin1') for m in ms))[:8]))
            if len(found)<=10:
                print(f"条目{i} c1={c1:08x} c2={c2:08x} fl={fl} 路径串:",found[-1][3])
print("\n前3000条中含路径字符串的条目数:",len(found))
import json
Path(r"E:\la拆包项目\04临时存放\2026-08-30_FPK场景包攻坚与收尾自检\embedded_paths_3k.json").write_text(
    json.dumps([{'idx':i,'c1':f'{a:08x}','c2':f'{b:08x}','paths':ps} for i,a,b,fl,ps in found],ensure_ascii=False,indent=1),encoding='utf-8')
