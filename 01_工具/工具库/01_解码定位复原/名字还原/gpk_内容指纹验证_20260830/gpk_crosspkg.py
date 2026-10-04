# -*- coding: utf-8 -*-
"""GPK step7：跨包 (c1,c2) 交集——判定 namehash 是全局一致还是包内分配。"""
import struct
from pathlib import Path
from Crypto.Cipher import AES
AES_KEY=bytes.fromhex('606308d8a32c782013d26c2f226f686d')

def pairs_of(path):
    cipher=AES.new(AES_KEY,AES.MODE_ECB); fs=path.stat().st_size
    with open(path,'rb') as f:
        pre=cipher.decrypt(f.read(4096)+b'\x00'*((16-4096%16)%16))
        B=struct.unpack_from('<I',pre,20)[0]
        need=64+B*32+64
        f.seek(0); head=f.read(need)
    pt=cipher.decrypt(head+b'\x00'*((16-len(head)%16)%16))
    pairs=set()
    for i in range(B):
        o,cp,dp,c1,c2,fl=struct.unpack_from('<IIIIII',pt,64+i*32)
        if o>=64 and o+36+cp<=fs and fl in (0,2,12): pairs.add((c1,c2))
    return B,pairs

names=["weapon.gpk","effect_02.gpk","effect_cache.gpk","ui_01.gpk"]
sets={}
for n in names:
    p=Path(r"E:/mrzh/res")/n
    if not p.exists():
        print(n,"不存在"); continue
    B,s=pairs_of(p); sets[n]=s
    print(f"{n}: 声明{B} 唯一pair {len(s)}")

ns=list(sets)
for i in range(len(ns)):
    for j in range(i+1,len(ns)):
        inter=sets[ns[i]]&sets[ns[j]]
        print(f"{ns[i]} ∩ {ns[j]} = {len(inter)}")
# 三包/四包公共
common=set.intersection(*sets.values())
print("全部包公共 pair:",len(common))
if common: print("示例:",[f'{a:08x}{b:08x}' for a,b in list(common)[:5]])
