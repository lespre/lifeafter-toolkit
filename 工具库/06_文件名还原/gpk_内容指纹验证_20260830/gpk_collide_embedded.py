# -*- coding: utf-8 -*-
"""GPK step5：用 gpk 内部挖出的真实依赖路径撞 (c1,c2)，验证双murmur/自研hash。"""
import struct, json, itertools
from pathlib import Path
from Crypto.Cipher import AES
AES_KEY=bytes.fromhex('606308d8a32c782013d26c2f226f686d')

def murmur3_x86_32(data, seed):
    c1,c2=0xCC9E2D51,0x1B873593; v=seed&0xFFFFFFFF; end=len(data)&~3
    for o in range(0,end,4):
        b=int.from_bytes(data[o:o+4],'little'); b=(b*c1)&0xFFFFFFFF
        b=((b<<15)|(b>>17))&0xFFFFFFFF; b=(b*c2)&0xFFFFFFFF
        v^=b; v=((v<<13)|(v>>19))&0xFFFFFFFF; v=(v*5+0xE6546B64)&0xFFFFFFFF
    t=data[end:]; b=0
    if len(t)>=3: b^=t[2]<<16
    if len(t)>=2: b^=t[1]<<8
    if t:
        b^=t[0]; b=(b*c1)&0xFFFFFFFF; b=((b<<15)|(b>>17))&0xFFFFFFFF; b=(b*c2)&0xFFFFFFFF; v^=b
    v^=len(data); v^=v>>16; v=(v*0x85EBCA6B)&0xFFFFFFFF; v^=v>>13
    v=(v*0xC2B2AE35)&0xFFFFFFFF; v^=v>>16; return v&0xFFFFFFFF

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

pairs,c1s,c2s=load_pairs(Path(r"E:/mrzh/res/weapon.gpk"))
emb=json.loads(Path(r"E:\la拆包项目\04临时存放\2026-08-30_FPK场景包攻坚与收尾自检\embedded_paths_3k.json").read_text(encoding='utf-8'))
raw=set()
for e in emb:
    for s in e['paths']: raw.add(s)
print("内嵌真实路径语料:",len(raw))

def forms(s):
    out={s, s.replace('\\','/'), s.lower(), s.lower().replace('\\','/'), s.replace('/','\\')}
    return out

SEEDS=[0x77777777,0x66666666,0,1,0xFFFFFFFF]
pair_hit=[]; single=0; tested=0
for s in raw:
    for v in forms(s):
        b=v.encode('utf-8')
        # 双murmur 经典组合 + 全部种子对
        hv={f'{sd:08x}':murmur3_x86_32(b,sd) for sd in SEEDS}
        tested+=1
        # 经典 NPK 组合
        classic=(hv[f'{0x77777777:08x}'],hv[f'{0x66666666:08x}'])
        if classic in pairs: pair_hit.append((v,'7777/6666',f'{classic[0]:08x}{classic[1]:08x}'))
        for sa,sb in itertools.combinations(SEEDS,2):
            pr=(hv[f'{sa:08x}'],hv[f'{sb:08x}'])
            if pr in pairs: pair_hit.append((v,f'{sa:x}/{sb:x}',f'{pr[0]:08x}{pr[1]:08x}'))
            pr2=(hv[f'{sb:08x}'],hv[f'{sa:08x}'])
            if pr2 in pairs: pair_hit.append((v,f'{sb:x}/{sa:x}',f'{pr2[0]:08x}{pr2[1]:08x}'))
        for sd,h in hv.items():
            if h in c1s or h in c2s: single+=1
print("测试变体:",tested)
print("双32位pair命中:",len(pair_hit))
for x in pair_hit[:20]: print("  PAIR-HIT",x)
print("单32位命中(c1/c2):",single,"(随机期望≈",tested*len(SEEDS)*2*len(c1s)/2**32,")")
