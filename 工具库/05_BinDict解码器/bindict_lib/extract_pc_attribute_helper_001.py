# -*- coding: utf-8 -*-
"""Extract PC AttributeHelper.nxs from current script archives, as bytes only."""
from __future__ import annotations
import hashlib,importlib.util,json,struct
from pathlib import Path
OUT=Path(r'E:/mrzh_audit/run_004_PC_BinDict与1DPW专项_001/02_bindict/AttributeHelper_PC静态副本_001')
PKGS=(Path(r'E:/mrzh/Documents/script.npk'),Path(r'E:/mrzh/Documents/script.py3.npk'))
FID=0x17743EBE250D2810
HELPER=Path(r'C:/Users/Administrator/AppData/Local/hermes/mrzh_weapon_skin_audit/run_002/audit_mrzh_aurora_script_presence.py')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def load():
 s=importlib.util.spec_from_file_location('r',HELPER);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def strings(d):
 out=[]
 for i in range(len(d)-2):
  if d[i] in (0xd3,0xf3,0xda,0xfa):
   n=d[i+1];x=d[i+2:i+2+n]
   if n and len(x)==n and all(32<=c<127 for c in x):out.append({'offset':i,'tag':f'{d[i]:02x}','text':x.decode('ascii')})
 return out
def main():
 OUT.mkdir(parents=True,exist_ok=True);r=load();rows=[]
 for p in PKGS:
  before={'path':str(p),'bytes':p.stat().st_size,'mtime_ns':p.stat().st_mtime_ns,'sha256':sha(p)}
  with p.open('rb') as f:
   _r,magic,v,to,n=struct.unpack_from('<QIIII',r.aes_ecb(f.read(32)));f.seek(to);tab=r.aes_ecb(f.read(n*48));match=None
   for i in range(n):
    row=struct.unpack_from('<QIIIIIi',tab,i*48)
    if row[0]==FID:match=(i,row);break
   if not match:raise RuntimeError(f'missing FID in {p}')
   i,row=match;fid,off,ps,ds,a,b,flag=row;f.seek(off);raw=r.unpack_entry(f.read(ps),ds,flag)
  after={'path':str(p),'bytes':p.stat().st_size,'mtime_ns':p.stat().st_mtime_ns,'sha256':sha(p)}
  if before!=after:raise RuntimeError('source changed')
  dest=OUT/(p.stem.replace('.','_')+'_AttributeHelper_17743EBE250D2810.static.bin');dest.write_bytes(raw)
  ss=strings(raw)
  rows.append({'source':after,'entry_index':i,'file_id':f'{fid:016X}','archive_offset':off,'packed_size':ps,'declared_size':ds,'checks':[a,b],'flag':flag,'raw_copy':str(dest),'raw_bytes':len(raw),'raw_sha256':hashlib.sha256(raw).hexdigest(),'head_hex':raw[:64].hex(),'static_strings':ss,'boundary':'raw bytes only; no marshal/import/eval/exec'})
 rep={'logical_path':r'com\utils\AttributeHelper.nxs','rows':rows};q=OUT/'AttributeHelper_PC双包source_lock与静态字符串_001.json';q.write_text(json.dumps(rep,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'report':str(q),'rows':[{'source':x['source'],'entry':x['entry_index'],'raw_copy':x['raw_copy'],'raw_bytes':x['raw_bytes'],'raw_sha256':x['raw_sha256'],'head':x['head_hex'],'strings':len(x['static_strings']),'interesting':[z for z in x['static_strings'] if any(k in z['text'].lower() for k in ('attr','attack','damage','hurt','armor','critical','fire','life','hp','shield'))][:300]} for x in rows]},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
