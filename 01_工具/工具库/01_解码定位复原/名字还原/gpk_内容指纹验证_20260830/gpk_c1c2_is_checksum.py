# -*- coding: utf-8 -*-
"""GPK 文件名还原 step3：判定 c1/c2 是否=数据校验和（crc32压缩/解压、adler、内容hash前缀）。"""
import struct, zlib, hashlib
from pathlib import Path
from Crypto.Cipher import AES
import lz4.block, zstandard as zstd

AES_KEY=bytes.fromhex('606308d8a32c782013d26c2f226f686d')
dctx=zstd.ZstdDecompressor()

def entries(path, n=400):
    cipher=AES.new(AES_KEY,AES.MODE_ECB); fs=path.stat().st_size
    with open(path,'rb') as f: head=f.read(80*1024*1024)
    pt=cipher.decrypt(head+b'\x00'*((16-len(head)%16)%16))
    B=struct.unpack_from('<I',pt,20)[0]
    if 64+B*32>len(pt):
        with open(path,'rb') as f: head=f.read(64+B*32+64)
        pt=cipher.decrypt(head+b'\x00'*((16-len(head)%16)%16))
    out=[]
    for i in range(min(B,n)):
        o,cp,dp,c1,c2,fl=struct.unpack_from('<IIIIII',pt,64+i*32)
        if o>=64 and o+36+cp<=fs and fl in (0,2,12):
            out.append((o,cp,dp,c1,c2,fl))
    return out

p=Path(r"E:/mrzh/res/weapon.gpk")
es=entries(p)
stat={'c1==crc_comp':0,'c2==crc_comp':0,'c1==crc_decomp':0,'c2==crc_decomp':0,
      'c1==adler_decomp':0,'c2==adler_decomp':0,'c1==md5_lo':0,'c2==md5_lo':0,
      'c1==c2':0,'total':0}
detail=[]
with open(p,'rb') as f:
    for (o,cp,dp,c1,c2,fl) in es:
        f.seek(o+36); seg=f.read(cp)
        try:
            if fl==0: d=seg
            elif fl==2: d=lz4.block.decompress(seg,uncompressed_size=dp)
            else: d=dctx.decompress(seg,max_output_size=dp+4096)
        except Exception as e:
            continue
        stat['total']+=1
        cc=zlib.crc32(seg)&0xffffffff; cd=zlib.crc32(d)&0xffffffff
        ad=zlib.adler32(d)&0xffffffff
        md5=hashlib.md5(d).digest()
        mlo=struct.unpack('<I',md5[:4])[0]; mhi=struct.unpack('<I',md5[4:8])[0]
        checks={'c1==crc_comp':c1==cc,'c2==crc_comp':c2==cc,'c1==crc_decomp':c1==cd,'c2==crc_decomp':c2==cd,
                'c1==adler_decomp':c1==ad,'c2==adler_decomp':c2==ad,'c1==md5_lo':c1==mlo,'c2==md5_lo':c2==mlo,
                'c1==c2':c1==c2}
        for k,v in checks.items():
            if v: stat[k]+=1
        if len(detail)<6:
            detail.append((fl,cp,dp,f'{c1:08x}',f'{c2:08x}',f'crc_comp={cc:08x}',f'crc_dec={cd:08x}',f'adler={ad:08x}',f'md5lo={mlo:08x}'))
print("有效样本:",stat['total'])
for k,v in stat.items():
    if k!='total': print(f"  {k}: {v}")
print("\n前6条明细 (fl,comp,decomp,c1,c2,crc_comp,crc_dec,adler,md5lo):")
for x in detail: print("  ",x)
