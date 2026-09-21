# -*- coding: utf-8 -*-
"""exe step4：明文字符串扫描（ASCII + UTF-16LE），判断关键符号是否不脱壳可得。"""
import re
from pathlib import Path
raw=Path(r"E:\mrzh\Documents\bin\x64\lifeafter.exe").read_bytes()
asc=re.findall(rb'[\x20-\x7e]{6,}',raw)
u16=re.findall(rb'(?:[\x20-\x7e]\x00){5,}',raw)
print("ASCII串(>=6):",len(asc)," UTF16串(>=5):",len(u16))
# 长度分布 / 较长串样本
asc_sorted=sorted(asc,key=len,reverse=True)
print("\n最长20个ASCII串:")
for s in asc_sorted[:20]: print("  ",s[:100].decode('latin1'))

KW=[b'murmur',b'Murmur',b'hash',b'Hash',b'namehash',b'NameHash',b'Resource',b'resource',
    b'.gpk',b'.fpk',b'.npk',b'NeoX',b'neox',b'WpkResource',b'.dds',b'.gim',b'.mesh',
    b'weapon',b'skin',b'fashion',b'lottery',b'AttributeHelper',b'BinDict',b'xbrace',
    b'UPX',b'.py',b'python',b'Python',b'VMP',b'Themida']
blob_ascii=b'\n'.join(asc)
print("\n关键词命中（ASCII串池内）:")
for k in KW:
    n=blob_ascii.count(k)
    if n:
        i=blob_ascii.find(k)
        print(f"  {k.decode():16} x{n}  例: {blob_ascii[max(0,i-30):i+50].decode('latin1','replace')!r}")
print("\nUTF16 长串样本:")
for s in sorted(u16,key=len,reverse=True)[:15]:
    print("  ",s.decode('utf-16le','replace')[:90])
