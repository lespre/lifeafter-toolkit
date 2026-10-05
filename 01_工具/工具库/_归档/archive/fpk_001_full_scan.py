# -*- coding: utf-8 -*-
"""Full-frame scan of 001.fpk: frame offsets, types, manifests, skeleton JSON.

Read-only on E:/mrzh. Extracts all DDS/manifest/json frames to E:/mrzh_audit.
"""
from __future__ import annotations
import json,re,struct
from pathlib import Path
import zstandard as zstd

SRC=Path(r'E:/mrzh/res/001.fpk')  # 修改为其他包即可解包对应 fpk
OUT=Path(__file__).resolve().parent / 'output' / 'fpk_001_full'
MAGIC=b'\x28\xb5\x2f\xfd'
CHUNK=8<<20

def frame_type(out):
 if out.startswith(b'\x89PNG'):return 'png'
 if out.startswith(b'DDS '):
  w,h=struct.unpack_from('<II',out,12);return f'dds_{w}x{h}'
 if out[:1] in (b'{',b'['):return 'json'
 if b'\nsize:' in out[:512] and b'\nformat:' in out[:512]:return 'manifest'
 return 'other'

def parse_manifest(out):
 txt=out.decode('utf-8','replace')
 m=re.search(r'([A-Za-z0-9_\.\-]+\.png)\s*\nsize:\s*(\d+),(\d+)\s*\nformat:\s*(\S+)',txt)
 names=re.findall(r'^([A-Za-z0-9_\.\-]+)\s*$',txt,re.M)
 return {'atlas':m.group(1) if m else None,'size':(int(m.group(2)),int(m.group(3))) if m else None,
         'format':m.group(4) if m else None,'sub_count':len(names)-(1 if m else 0),'names':names[:40]}

def main():
 # 1) full frame offset table
 offs=[32]
 with SRC.open('rb') as f:
  pos=32;over=b''
  while True:
   buf=f.read(CHUNK)
   if not buf:break
   data=over+buf;base=pos-len(over)
   i=0
   while True:
    s=data.find(MAGIC,i)
    if s<0:break
    if base+s>32:offs.append(base+s)
    i=s+1
   over=data[-(len(MAGIC)-1):] if len(data)>=len(MAGIC)-1 else data
   pos=base+len(buf)
 offs=sorted(set(offs))
 print('total frames',len(offs)-1)
 # 2) decompress each frame, classify, save
 d=zstd.ZstdDecompressor();rows=[];dds_out=[]
 OUT.mkdir(parents=True,exist_ok=True)
 with SRC.open('rb') as f:
  for i in range(len(offs)-1):
   f.seek(offs[i]);data=f.read(offs[i+1]-offs[i])
   try:out=d.decompress(data)
   except Exception as e:
    rows.append({'idx':i,'off':offs[i],'comp':len(data),'type':'error','error':repr(e)});continue
   ft=frame_type(out)
   rec={'idx':i,'off':offs[i],'comp':len(data),'out':len(out),'type':ft}
   if ft=='manifest':
    rec['manifest']=parse_manifest(out)
    (OUT/f'manifest_{i:03d}.txt').write_bytes(out)
   elif ft=='json':
    rec['json_head']=out[:300].decode('utf-8','replace')
    (OUT/f'skel_{i:03d}.json').write_bytes(out)
   elif ft.startswith('dds_'):
    if i in (1,2,4):  # only the big atlases
     (OUT/f'tex_{i:03d}_{ft[4:]}.dds').write_bytes(out)
    dds_out.append(i)
   rows.append(rec)
 # summary
 types={}
 for r in rows:types[r['type']]=types.get(r['type'],0)+1
 man=[r for r in rows if r.get('manifest')]
 (OUT/'001_frames_full.json').write_text(json.dumps({'source':str(SRC),'total_frames':len(rows),'types':types,'rows':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'types':types,'manifests':[{ 'atlas':m['manifest']['atlas'],'size':m['manifest']['size'],'sub':m['manifest']['sub_count']} for m in man],'dds_frames':len(dds_out),'json_frames':[r['idx'] for r in rows if r['type']=='json'],'other_frames':[r['idx'] for r in rows if r['type']=='other']},ensure_ascii=False,indent=1))

if __name__=='__main__':
 main()
