# -*- coding: utf-8 -*-
"""Full THX hash extraction: parse THFB 24B entries across all .thx files.

Entry = [16B hash][u32][u32]. Verifies against the historical cross-ref CSV.
Read-only on E:/mrzh.
"""
from __future__ import annotations
import csv,json,math,collections
from pathlib import Path
OUT=Path(r'E:/提取成果/明日拆包/output/09_thfb')
THD=Path(r'E:/mrzh/Documents/thd')
MULTI=Path(r'E:/mrzh/Documents/multi_cloud1')
CSV=Path(r'C:/Users/<user>/AppData/Local/hermes/mrzh_weapon_skin_audit/run_002/物理实体链路_001/THX与IDX原始Hash交叉引用.csv')

def entropy(b):
 c=collections.Counter(b);n=len(b)
 return -sum((v/n)*math.log2(v/n) for v in c.values()) if n else 0

def extract_thx(data: bytes, path: str, csv_set: set):
 """Find 24B entry runs: [16B hash][u32][u32].
 1) anchor-align: for every CSV-hash byte position, derive candidate start
    S = pos - k*24; pick S aligning the most CSV hashes and pass ok().
 2) else linear scan best run."""
 n=len(data)
 def ok(off):
  if off+24>n:return False
  if len(set(data[off:off+16]))<12:return False
  a,b=struct_unpack(data,off+16)
  return a<0xF0000000 and b<0xF0000000
 # anchor alignment
 best_anchor=None
 if csv_set:
  from collections import defaultdict
  votes=defaultdict(int)
  for h in csv_set:
   pos=0
   while True:
    i=data.find(bytes.fromhex(h),pos)
    if i<0:break
    for k in range(0,60):
     S=i-k*24
     if S>=0 and ok(S):votes[S]+=1
    pos=i+1
  if votes:
   S,cnt=max(votes.items(),key=lambda kv:(kv[1],kv[0]))
   if cnt>=2:
    o=S;hashes=[]
    while ok(o):
     hashes.append(data[o:o+16].hex());o+=24
    best_anchor=(S,hashes,cnt)
 # linear best run (fallback / compare)
 best=None;off=0
 while off+24<=n:
  if not ok(off):off+=1;continue
  cnt=0;o=off;hashes=[]
  while ok(o):
   hashes.append(data[o:o+16].hex());cnt+=1;o+=24
  ov=sum(1 for h in hashes if h in csv_set)
  key=(ov,cnt)
  if best is None or key>best[0]:
   best=(key,off,hashes)
  off=o
 if best_anchor:
  S,hashes,anchor_votes=best_anchor
  ov=sum(1 for h in hashes if h in csv_set)
  key=(ov,len(hashes))
  if best is None or key>best[0]:
   return (key,S,hashes)
 return best

def struct_unpack(data,off):
 import struct
 a,b=struct.unpack_from('<II',data,off)
 return a,b

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 csv_hashes=set()
 with CSV.open('r',encoding='utf-8-sig') as f:
  rd=csv.DictReader(f)
  for row in rd:
   h=row.get('resource_hash','').strip()
   if len(h)==32:csv_hashes.add(h)
 files=sorted(THD.glob('*.thx'))+sorted(MULTI.rglob('*.thx'))
 # dedupe by name (multi_cloud1 preferred if same name exists)
 byname={}
 for f in files:byname.setdefault(f.name,[]).append(f)
 rows=[];all_hash=set();per_file={}
 for name,plist in sorted(byname.items()):
  p=max(plist,key=lambda x:x.stat().st_size)
  data=p.read_bytes()
  r=extract_thx(data,str(p),csv_hashes)
  if r:
   (ov,cnt),start,hashes=r
   for h in hashes:all_hash.add(h)
   per_file[name]={'file':str(p),'size':len(data),'entries':cnt,'entry_start':start}
   rows.append({'file':name,'path':str(p),'size':len(data),'entries':cnt,'entry_start':start})
  else:
   rows.append({'file':name,'path':str(p),'size':len(data),'entries':0,'entry_start':None})
 total=sum(r['entries'] for r in rows)
 # cross-check with historical CSV
 csv_hashes=set()
 with CSV.open('r',encoding='utf-8-sig') as f:
  rd=csv.DictReader(f)
  for row in rd:
   h=row.get('resource_hash','').strip()
   if len(h)==32:csv_hashes.add(h)
 match=all_hash & csv_hashes
 print(json.dumps({'thx_files':len(rows),'total_entries':total,'unique_hashes':len(all_hash),
                   'csv_hashes':len(csv_hashes),'csv_overlap':len(match),
                   'sample_overlap':list(match)[:8],
                   'top_files':sorted(per_file.items(),key=lambda x:-x[1]['entries'])[:10]},ensure_ascii=False,indent=1))
 (OUT/'thx_hash_full_extract.json').write_text(json.dumps({'files':rows,'unique_hashes':len(all_hash),'csv_overlap':len(match)},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 with (OUT/'thx_hashes_all.txt').open('w') as f:
  for h in sorted(all_hash):f.write(h+'\n')
if __name__=='__main__':
 main()
