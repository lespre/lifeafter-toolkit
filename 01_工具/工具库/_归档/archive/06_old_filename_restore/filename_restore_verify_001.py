# -*- coding: utf-8 -*-
"""批量解包验证 170 条命中（方向2 成果定稿）。"""
from __future__ import annotations
import importlib.util,json,struct
from pathlib import Path
OUT=Path(r'E:/提取成果/filename_restore_output')
spec=importlib.util.spec_from_file_location('npkr',Path(r'E:/提取成果/明日之后拆包工具/01_核心解包器/npk_reader.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def murmur3_x86_32(data, seed):
 c1,c2=0xCC9E2D51,0x1B873593
 h=seed&0xFFFFFFFF
 end=len(data)&~3
 for off in range(0,end,4):
  k=int.from_bytes(data[off:off+4],'little')
  k=(k*c1)&0xFFFFFFFF; k=((k<<15)|(k>>17))&0xFFFFFFFF; k=(k*c2)&0xFFFFFFFF
  h^=k; h=((h<<13)|(h>>19))&0xFFFFFFFF; h=(h*5+0xE6546B64)&0xFFFFFFFF
 tail=data[end:];k=0
 if len(tail)>=3:k^=tail[2]<<16
 if len(tail)>=2:k^=tail[1]<<8
 if tail:
  k^=tail[0]; k=(k*c1)&0xFFFFFFFF; k=((k<<15)|(k>>17))&0xFFFFFFFF; k=(k*c2)&0xFFFFFFFF
  h^=k
 h^=len(data); h^=h>>16; h=(h*0x85EBCA6B)&0xFFFFFFFF; h^=h>>13; h=(h*0xC2B2AE35)&0xFFFFFFFF; h^=h>>16
 return h&0xFFFFFFFF
def path_id(p):
 e=p.encode('utf-8')
 return (murmur3_x86_32(e,0x77777777)<<32)|murmur3_x86_32(e,0x66666666)
def load_ids(pkgpath):
 ids={}
 with pkgpath.open('rb') as f:
  h=m.aes_ecb(f.read(32))
  _r,magic,ver,to,n=struct.unpack_from('<QIIII',h)
  f.seek(to);tab=m.aes_ecb(f.read(n*48))
  for i in range(n):
   row=struct.unpack_from('<QIIIIIi',tab,i*48)
   ids[row[0]]=(i,row)
 return ids
def main():
 matches=json.loads((OUT/'resource_path_matches.json').read_text(encoding='utf-8'))
 ids=load_ids(Path(r'E:/mrzh/res/ui.npk'))
 results=[]
 for x in matches:
  fid=int(x['file_id'],16)
  ent=ids.get(fid)
  if not ent:continue
  i,row=ent
  with Path(r'E:/mrzh/res/ui.npk').open('rb') as f:
   f.seek(row[1]);raw=m.unpack_entry(f.read(row[2]),row[3],row[6])
  typ='png' if raw[:4]==b'\x89PNG' else 'dds' if raw[:4]==b'DDS ' else raw[:8].hex()
  results.append({'path':x['path'],'file_id':x['file_id'],'entry':i,'flag':row[6],'raw_bytes':len(raw),'type':typ})
 # stats
 from collections import Counter
 c=Counter(r['type'] for r in results)
 ok=sum(1 for r in results if r['type'] in ('png','dds'))
 print(json.dumps({'total':len(results),'ok':ok,'types':dict(c),'sample':results[:5]},ensure_ascii=False,indent=1))
 (OUT/'resource_path_verified.json').write_text(json.dumps(results,ensure_ascii=False,indent=1)+'\n',encoding='utf-8')
 (OUT/'resource_path_verified.csv').write_text('path,file_id,entry,flag,raw_bytes,type\n'+'\n'.join(f"{r['path']},{r['file_id']},{r['entry']},{r['flag']},{r['raw_bytes']},{r['type']}" for r in results)+'\n',encoding='utf-8')
 print('saved')
if __name__=='__main__':
 main()
