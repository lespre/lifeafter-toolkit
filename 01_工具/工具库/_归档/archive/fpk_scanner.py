# -*- coding: utf-8 -*-
"""Generic FPK parser: 32B header + Zstd frame stream.

Classifies frames (manifest text / DDS / JSON skeleton / other) and dumps the
manifest of each package. Read-only on E:/mrzh.
"""
from __future__ import annotations
import json,re,struct,sys
from pathlib import Path
import zstandard as zstd

ROOT=Path(r'E:/mrzh/res')
OUT=Path(__file__).resolve().parent / 'output' / 'fpk_overview'
HEADER=32
SCAN_LIMIT=8<<20  # first 8MB per package for overview

def frame_type(out: bytes):
 if out.startswith(b'\x89PNG'): return 'png'
 if out.startswith(b'DDS '): 
  w,h=struct.unpack_from('<II',out,12)
  return f'dds_{w}x{h}'
 if out[:1]==b'{' or out[:1]==b'[':
  return 'json'
 if b'\nsize: ' in out[:512] and b'\nformat:' in out[:512]:
  return 'manifest'
 if out.startswith(b'\n'):
  return 'manifest'
 return 'other'

def parse_manifest(out: bytes):
 txt=out.decode('utf-8','replace')
 m=re.match(r'\s*(.+\.png)\s*\nsize:\s*(\d+),(\d+)\s*\nformat:\s*(\S+)',txt)
 entries=re.findall(r'^([A-Za-z0-9_\.\-]+)\s*$',txt,re.M)
 return {'atlas':m.group(1) if m else None,'size':(int(m.group(2)),int(m.group(3))) if m else None,
         'format':m.group(4) if m else None,'sub_textures':len(entries)-1 if m else len(entries),
         'first_names':entries[1:8] if m else entries[:8]}

def scan(p: Path):
 with p.open('rb') as f:
  f.seek(HEADER);buf=f.read(SCAN_LIMIT)
 d=zstd.ZstdDecompressor()
 frames=[];pos=0
 for i in range(40):
  s=buf.find(b'\x28\xb5\x2f\xfd',pos)
  if s<0:break
  try:
   obj=d.decompressobj()
   out=obj.decompress(buf[s:])
   used=len(buf)-s-len(obj.unused_data)
  except Exception as e:
   frames.append({'idx':i,'off':HEADER+s,'error':repr(e)});break
  ft=frame_type(out)
  rec={'idx':i,'off':HEADER+s,'comp':used,'out':len(out),'type':ft}
  if ft=='manifest':
   rec['manifest']=parse_manifest(out)
  elif ft=='json':
   rec['json_head']=out[:200].decode('utf-8','replace')
  frames.append(rec)
  pos=s+max(1,used)
 return frames

def main():
 import struct
 OUT.mkdir(parents=True,exist_ok=True)
 pkgs=sorted(ROOT.glob('*.fpk'))
 rows=[]
 for p in pkgs:
  with p.open('rb') as f:head=f.read(HEADER+16)
  magic=struct.unpack_from('<I',head,HEADER)[0] if len(head)>=HEADER+4 else 0
  if head[HEADER:HEADER+4]==b'\x00\x00\x00\x14' and b'ftyp' in head[HEADER:HEADER+64]:
   kind='mp4(isom)'
  elif head[HEADER:HEADER+4]==b'FSB5':
   kind='fsb5_audio'
  elif head[HEADER:HEADER+4]==b'\x28\xb5\x2f\xfd':
   kind='zstd_stream'
  else:
   kind='enc/unknown'
  fr=scan(p)
  man=[f for f in fr if f['type']=='manifest']
  types={}
  for f in fr: types[f['type']]=types.get(f['type'],0)+1
  rows.append({'name':p.name,'size':p.stat().st_size,'kind':kind,'frames_scanned':len(fr),'types':types,
               'atlas':man[0]['manifest']['atlas'] if man else None,
               'sub':man[0]['manifest']['sub_textures'] if man else None,
               'json_hashes':[f['json_head'][:60] for f in fr if f['type']=='json'][:2]})
 (OUT/'fpk_overview_001.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 for r in rows:
  print(f"{r['name']:9s} {r['kind']:14s} frames={r['frames_scanned']:3d} types={r['types']} atlas={r['atlas']} sub={r['sub']}")

if __name__=='__main__':
 main()
