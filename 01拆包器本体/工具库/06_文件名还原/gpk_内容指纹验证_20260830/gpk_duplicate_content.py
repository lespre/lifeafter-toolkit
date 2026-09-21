# -*- coding: utf-8 -*-
"""GPK step8：相同(c1,c2)的重复条目，解压内容是否一致？判定是否内容指纹。"""
import struct, hashlib, collections
from pathlib import Path
from Crypto.Cipher import AES
import lz4.block, zstandard as zstd
AES_KEY=bytes.fromhex('606308d8a32c782013d26c2f226f686d')
dctx=zstd.ZstdDecompressor()

def entries(path):
    cipher=AES.new(AES_KEY,AES.MODE_ECB); fs=path.stat().st_size
    with open(path,'rb') as f: pre=cipher.decrypt(f.read(4096)+b'\x00'*((16-4096%16)%16))
    B=struct.unpack_from('<I',pre,20)[0]
    with open(path,'rb') as f:
        f.seek(0); need=64+B*32+64; head=f.read(need)
    pt=cipher.decrypt(head+b'\x00'*((16-len(head)%16)%16))
    out=[]
    for i in range(B):
        o,cp,dp,c1,c2,fl=struct.unpack_from('<IIIIII',pt,64+i*32)
        if o>=64 and o+36+cp<=fs and fl in (0,2,12): out.append((i,o,cp,dp,c1,c2,fl))
    return out

es=entries(Path(r"E:/mrzh/res/weapon.gpk"))
groups=collections.defaultdict(list)
for e in es: groups[(e[4],e[5])].append(e)
dups={k:v for k,v in groups.items() if len(v)>=2}
print("重复(c1,c2)组数:",len(dups))

same=diff=0; ex=[]
with open(r"E:/mrzh/res/weapon.gpk",'rb') as f:
    for k,members in list(dups.items())[:60]:
        hashes=set(); sizes=set()
        for (i,o,cp,dp,c1,c2,fl) in members:
            f.seek(o+36); seg=f.read(cp)
            try:
                if fl==0: d=seg
                elif fl==2: d=lz4.block.decompress(seg,uncompressed_size=dp)
                else: d=dctx.decompress(seg,max_output_size=dp+4096)
            except: continue
            hashes.add(hashlib.md5(d).hexdigest()); sizes.add(len(d))
        if len(hashes)==1: same+=1
        else:
            diff+=1
            if len(ex)<8: ex.append((f'{k[0]:08x}{k[1]:08x}',len(members),len(hashes),sizes))
print(f"前60重复组：内容完全一致={same} 组, 内容不同={diff} 组")
for x in ex: print("  内容不同组:",x)
