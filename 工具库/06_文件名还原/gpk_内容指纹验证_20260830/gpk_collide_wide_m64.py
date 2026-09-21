# -*- coding: utf-8 -*-
"""GPK step6：补测 UTF-16 宽字符 + Murmur64/128 + FNV64 等最后一批标准算法。"""
import struct, json
from pathlib import Path
from Crypto.Cipher import AES
AES_KEY=bytes.fromhex('606308d8a32c782013d26c2f226f686d')
MASK=0xFFFFFFFFFFFFFFFF

def load_pairs(path):
    cipher=AES.new(AES_KEY,AES.MODE_ECB); fs=path.stat().st_size
    with open(path,'rb') as f: head=f.read(120*1024*1024)
    pt=cipher.decrypt(head+b'\x00'*((16-len(head)%16)%16))
    B=struct.unpack_from('<I',pt,20)[0]
    if 64+B*32>len(pt):
        with open(path,'rb') as f: head=f.read(64+B*32+64)
        pt=cipher.decrypt(head+b'\x00'*((16-len(head)%16)%16))
    pairs=set();c1s=set();c2s=set()
    for i in range(B):
        o,cp,dp,c1,c2,fl=struct.unpack_from('<IIIIII',pt,64+i*32)
        if o>=64 and o+36+cp<=fs and fl in (0,2,12): pairs.add((c1,c2));c1s.add(c1);c2s.add(c2)
    return pairs,c1s,c2s

def rotl(x,r): return ((x<<r)|(x>>(64-r)))&MASK
def murmur3_x64_128(key,seed=0):
    c1=0x87c37b91114253d5; c2=0x4cf5ad432745937f
    n=len(key); h1=seed; h2=seed; nblocks=n//16
    for i in range(nblocks):
        k1=struct.unpack_from('<Q',key,i*16)[0]; k2=struct.unpack_from('<Q',key,i*16+8)[0]
        k1=(k1*c1)&MASK; k1=rotl(k1,31); k1=(k1*c2)&MASK; h1^=k1
        h1=rotl(h1,27); h1=(h1+h2)&MASK; h1=(h1*5+0x52dce729)&MASK
        k2=(k2*c2)&MASK; k2=rotl(k2,33); k2=(k2*c1)&MASK; h2^=k2
        h2=rotl(h2,31); h2=(h2+h1)&MASK; h2=(h2*5+0x38495ab5)&MASK
    tail=key[nblocks*16:]; k1=0;k2=0
    sz=len(tail)
    if sz>=15: k2^=tail[14]<<48
    if sz>=14: k2^=tail[13]<<40
    if sz>=13: k2^=tail[12]<<32
    if sz>=12: k2^=tail[11]<<24
    if sz>=11: k2^=tail[10]<<16
    if sz>=10: k2^=tail[9]<<8
    if sz>=9:
        k2^=tail[8]; k2=(k2*c2)&MASK; k2=rotl(k2,33); k2=(k2*c1)&MASK; h2^=k2
    if sz>=8: k1^=tail[7]<<56
    if sz>=7: k1^=tail[6]<<48
    if sz>=6: k1^=tail[5]<<40
    if sz>=5: k1^=tail[4]<<32
    if sz>=4: k1^=tail[3]<<24
    if sz>=3: k1^=tail[2]<<16
    if sz>=2: k1^=tail[1]<<8
    if sz>=1:
        k1^=tail[0]; k1=(k1*c1)&MASK; k1=rotl(k1,31); k1=(k1*c2)&MASK; h1^=k1
    h1^=n; h2^=n; h1=(h1+h2)&MASK; h2=(h2+h1)&MASK
    # fmix64
    def fmix(k):
        k^=k>>33; k=(k*0xff51afd7ed558ccd)&MASK; k^=k>>33
        k=(k*0xc4ceb9fe1a85ec53)&MASK; k^=k>>33; return k
    h1=fmix(h1); h2=fmix(h2); h1=(h1+h2)&MASK; h2=(h2+h1)&MASK
    return h1,h2
def fnv1a64(b):
    h=0xcbf29ce484222325
    for x in b: h=((h^x)*0x100000001b3)&MASK
    return h

pairs,c1s,c2s=load_pairs(Path(r"E:/mrzh/res/weapon.gpk"))
emb=json.loads(Path(r"E:\la拆包项目\04临时存放\2026-08-30_FPK场景包攻坚与收尾自检\embedded_paths_3k.json").read_text(encoding='utf-8'))
raw=set()
for e in emb:
    for s in e['paths']: raw.add(s)
print("语料:",len(raw)," pair目标:",len(pairs))

def forms(s):
    import os
    base={s,s.replace('\\','/'),s.lower(),s.lower().replace('\\','/')}
    out=set(base)
    for b in base:
        out.add(os.path.splitext(b)[0])           # 去扩展名
        out.add(os.path.basename(b.replace('\\','/')))  # basename
    return out

hits=[]
for s in raw:
    for v in forms(s):
        for enc in ('utf-8','utf-16-le'):
            try: b=v.encode(enc)
            except: continue
            h1,h2=murmur3_x64_128(b,0)
            cands={
                'm128_h1_lohi':(h1&0xffffffff,(h1>>32)&0xffffffff),
                'm128_h1h2_lo':(h1&0xffffffff,h2&0xffffffff),
                'm128_h2_lohi':(h2&0xffffffff,(h2>>32)&0xffffffff),
            }
            for seed in (0,0x77777777,1):
                x,y=murmur3_x64_128(b,seed)
                cands[f'm128s{seed}_lohi']=(x&0xffffffff,(x>>32)&0xffffffff)
            fv=fnv1a64(b)
            cands['fnv64_lohi']=(fv&0xffffffff,(fv>>32)&0xffffffff)
            for cn,pr in cands.items():
                if pr in pairs: hits.append((v,enc,cn,f'{pr[0]:08x}{pr[1]:08x}'))
print("64/128位算法 pair命中:",len(hits))
for x in hits[:20]: print("  HIT",x)
