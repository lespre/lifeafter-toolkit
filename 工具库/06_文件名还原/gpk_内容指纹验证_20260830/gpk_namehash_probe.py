# -*- coding: utf-8 -*-
"""GPK 文件名还原 step1：dump 条目表 c1/c2，统计特征，判断是否 namehash。只读 gpk 头部。"""
import struct, collections
from pathlib import Path
from Crypto.Cipher import AES

AES_KEY = bytes.fromhex('606308d8a32c782013d26c2f226f686d')

def parse_entries(path):
    cipher = AES.new(AES_KEY, AES.MODE_ECB)
    fs = path.stat().st_size
    with open(path,'rb') as f:
        head = f.read(64*1024*1024)
    pad = (16-len(head)%16)%16
    pt = cipher.decrypt(head + b'\x00'*pad)
    B = struct.unpack_from('<I', pt, 20)[0]
    need = 64 + B*32
    if need > len(pt):
        with open(path,'rb') as f:
            head = f.read(need+64)
        pad=(16-len(head)%16)%16
        pt = cipher.decrypt(head+b'\x00'*pad)
    ents=[]
    for i in range(B):
        base=64+i*32
        o,cmp_,dec_,c1,c2,fl = struct.unpack_from('<IIIIII', pt, base)
        if o>=64 and o+36+cmp_<=fs and fl in (0,2,12):
            ents.append((o,cmp_,dec_,c1,c2,fl))
    # 头部前64字节也打印
    return ents, pt[:64], B

for name in ("weapon.gpk","effect_02.gpk"):
    p = Path(r"E:/mrzh/res")/name
    ents, head, B = parse_entries(p)
    c1s=[e[3] for e in ents]; c2s=[e[4] for e in ents]
    pair=[(e[3],e[4]) for e in ents]
    print("="*80); print(name, "声明条目数B=",B," 有效条目=",len(ents))
    print(" 头部64B hex:", head.hex())
    print(" c1: 唯一=%d/%d 零值=%d 最小=%08x 最大=%08x"%(len(set(c1s)),len(c1s),c1s.count(0),min(c1s),max(c1s)))
    print(" c2: 唯一=%d/%d 零值=%d 最小=%08x 最大=%08x"%(len(set(c2s)),len(c2s),c2s.count(0),min(c2s),max(c2s)))
    print(" (c1,c2)对 唯一=%d/%d"%(len(set(pair)),len(pair)))
    print(" flag分布:", collections.Counter(e[5] for e in ents))
    print(" 前8条 (off,comp,decomp,c1,c2,flag):")
    for e in ents[:8]:
        print("   off=%-10d comp=%-9d decomp=%-9d c1=%08x c2=%08x fl=%d"%e)
