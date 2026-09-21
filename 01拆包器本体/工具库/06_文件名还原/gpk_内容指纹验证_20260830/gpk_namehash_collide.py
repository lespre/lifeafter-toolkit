# -*- coding: utf-8 -*-
"""GPK 文件名还原 step2：用已知 model_path 穷尽碰撞 c1/c2。证实/证伪 namehash 算法。"""
import struct, json, zlib, itertools
from pathlib import Path
from Crypto.Cipher import AES

AES_KEY = bytes.fromhex('606308d8a32c782013d26c2f226f686d')

def murmur3_x86_32(data, seed):
    c1,c2=0xCC9E2D51,0x1B873593; v=seed&0xFFFFFFFF; end=len(data)&~3
    for o in range(0,end,4):
        b=int.from_bytes(data[o:o+4],'little')
        b=(b*c1)&0xFFFFFFFF; b=((b<<15)|(b>>17))&0xFFFFFFFF; b=(b*c2)&0xFFFFFFFF
        v^=b; v=((v<<13)|(v>>19))&0xFFFFFFFF; v=(v*5+0xE6546B64)&0xFFFFFFFF
    t=data[end:]; b=0
    if len(t)>=3: b^=t[2]<<16
    if len(t)>=2: b^=t[1]<<8
    if t:
        b^=t[0]; b=(b*c1)&0xFFFFFFFF; b=((b<<15)|(b>>17))&0xFFFFFFFF; b=(b*c2)&0xFFFFFFFF; v^=b
    v^=len(data); v^=v>>16; v=(v*0x85EBCA6B)&0xFFFFFFFF
    v^=v>>13; v=(v*0xC2B2AE35)&0xFFFFFFFF; v^=v>>16
    return v&0xFFFFFFFF

def fnv1a32(d):
    h=0x811c9dc5
    for x in d: h=((h^x)*0x01000193)&0xFFFFFFFF
    return h
def fnv1_32(d):
    h=0x811c9dc5
    for x in d: h=((h*0x01000193)&0xFFFFFFFF); h^=x
    return h&0xFFFFFFFF
def djb2(d):
    h=5381
    for x in d: h=((h*33)+x)&0xFFFFFFFF
    return h

def load_pairs(path):
    cipher=AES.new(AES_KEY,AES.MODE_ECB); fs=path.stat().st_size
    with open(path,'rb') as f: head=f.read(80*1024*1024)
    pt=cipher.decrypt(head+b'\x00'*((16-len(head)%16)%16))
    B=struct.unpack_from('<I',pt,20)[0]
    if 64+B*32>len(pt):
        with open(path,'rb') as f: head=f.read(64+B*32+64)
        pt=cipher.decrypt(head+b'\x00'*((16-len(head)%16)%16))
    pairs=set(); c1s=set(); c2s=set()
    for i in range(B):
        o,cp,dp,c1,c2,fl=struct.unpack_from('<IIIIII',pt,64+i*32)
        if o>=64 and o+36+cp<=fs and fl in (0,2,12):
            pairs.add((c1,c2)); c1s.add(c1); c2s.add(c2)
    return pairs,c1s,c2s

def variants(p):
    out=set()
    bases={p, p.replace('/','\\'), p.lower(), p.lower().replace('/','\\')}
    stems=set()
    for b in list(bases):
        stems.add(b)
        # 去扩展名 / 换扩展名
        import os
        noext=os.path.splitext(b)[0]
        stems.add(noext)
        for ext in ('.gim','.mesh','.dds','.c159','.bin','.png','.rgis','.mat','.anim','.tga'):
            stems.add(noext+ext)
    for s in stems:
        out.add(s)
        for pre in ('res/','res\\','/','./','weapons/',''):
            out.add(pre+s)
        # 只文件名 / 只目录
        slash=max(s.rfind('/'),s.rfind('\\'))
        if slash>=0:
            out.add(s[slash+1:])
    return out

pairs,c1s,c2s=load_pairs(Path(r"E:/mrzh/res/weapon.gpk"))
print("weapon.gpk: pair=%d c1=%d c2=%d"%(len(pairs),len(c1s),len(c2s)))

d=json.loads(Path(r"E:\la拆包项目\03拆包产物\weapon_skin_data_rows.json").read_text(encoding='utf-8'))
paths=[r['values']['model_path'][1] for r in d['rows'] if 'model_path' in r.get('values',{})]
print("已知model_path:",len(paths),"示例",paths[0])

SEEDS=[0,1,0x77777777,0x66666666,0xFFFFFFFF,0x9e3779b9,0xdeadbeef,0x12345678]
ALGS={'murmur':None,'crc32':lambda b:zlib.crc32(b)&0xffffffff,'fnv1a':fnv1a32,'fnv1':fnv1_32,'djb2':djb2}

hits={'c1':0,'c2':0,'pair_murmur':0}
hit_examples=[]
tested=0
for p in paths:
    for v in variants(p):
        for enc in ('utf-8','gbk'):
            try: b=v.encode(enc)
            except: continue
            # 单32位算法撞 c1/c2
            for an,af in ALGS.items():
                if an=='murmur':
                    hs=[(f'murmur_s{s:x}',murmur3_x86_32(b,s)) for s in SEEDS]
                else:
                    hs=[(an,af(b))]
                for an2,h in hs:
                    tested+=1
                    if h in c1s: hits['c1']+=1; hit_examples.append(('c1',p,v,an2,hex(h)))
                    if h in c2s: hits['c2']+=1; hit_examples.append(('c2',p,v,an2,hex(h)))
            # 双murmur组成pair（枚举种子对）
            for sa,sb in itertools.product(SEEDS,SEEDS):
                pair=(murmur3_x86_32(b,sa),murmur3_x86_32(b,sb))
                tested+=1
                if pair in pairs:
                    hits['pair_murmur']+=1; hit_examples.append(('pair',p,v,f's{sa:x}/s{sb:x}',f'{pair[0]:08x}{pair[1]:08x}'))

print("总测试次数:",tested)
print("命中统计:",hits)
for x in hit_examples[:30]: print("  HIT",x)
