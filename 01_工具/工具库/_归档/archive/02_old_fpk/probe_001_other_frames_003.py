# -*- coding: utf-8 -*-
"""Probe 001 other frames: header pattern distribution + version check."""
from __future__ import annotations
import json,collections
from pathlib import Path
import zstandard as zstd
SRC=Path(r'E:/mrzh/res/001.fpk')
OUT=Path(r'E:/提取成果/明日拆包/output/fpk/001_full')
def main():
 d=zstd.ZstdDecompressor();MAGIC=b'\x28\xb5\x2f\xfd'
 pat=collections.Counter();ver=collections.Counter();lens=[];other=0;total=0
 with SRC.open('rb') as f:
  f.seek(32);buf=f.read(8<<20)
  while True:
   obj=d.decompressobj()
   try:out=obj.decompress(buf)
   except zstd.ZstdError:break
   if not obj.eof:
    c=f.read(8<<20)
    if not c:break
    buf+=c;continue
   total+=1
   if not (out.startswith(b'DDS ') or out.startswith(b'\x89PNG') or out[:1] in (b'{',b'[') or b'\nsize:' in out[:512]):
    other+=1
    pat[out[:8].hex()]+=1
    ver[b'2.1.0.0' in out[:512]]+=1
    if other<=3000:lens.append(len(out))
   buf=obj.unused_data
   m=buf.find(MAGIC)
   while m<0:
    c=f.read(8<<20)
    if not c:break
    buf+=c;m=buf.find(MAGIC)
   if m<0:break
   buf=buf[m:]
   if total%5000==0:print('total',total,'other',other,flush=True)
 lens.sort()
 print(json.dumps({'total':total,'other':other,'head_patterns':pat.most_common(8),'has_version_2_1_0_0':ver,'other_len_min':lens[0] if lens else None,'other_len_med':lens[len(lens)//2] if lens else None,'other_len_max':lens[-1] if lens else None},ensure_ascii=False,indent=1))
 (OUT/'001_other_frames_probe.json').write_text(json.dumps({'total':total,'other':other,'head_patterns':dict(pat.most_common(20)),'has_version_2_1_0_0':dict(ver)},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':
 main()
