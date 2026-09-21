# -*- coding: utf-8 -*-
"""Read-only extraction of PC attribute_data cdata variants."""
from __future__ import annotations
import hashlib,importlib.util,json,struct
from pathlib import Path
PKG=Path(r'E:/mrzh/Documents/script.py3.npk')
OUT=Path(r'E:/mrzh_audit/run_004_PC_BinDict与1DPW专项_001/02_bindict/attribute_data_PC静态副本_001')
READER=Path(r'C:/Users/Administrator/AppData/Local/hermes/mrzh_weapon_skin_audit/run_002/audit_mrzh_aurora_script_presence.py')
HASHER=Path(r'C:/Users/Administrator/AppData/Local/hermes/mrzh_weapon_skin_audit/run_002/重构转印器核查_001/reextract_current_transfer_consume_tables_002.py')
TARGETS=(r'com\cdata\attribute_data.nxs',r'com\cdata\attribute_data_chs.nxs',r'com\cdata\attribute_data_kj1.nxs',r'com\cdata\attribute_data_yk.nxs')
def load(path,name):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def xbrace(d):
 out=[];p=0
 while True:
  p=d.find(b'x{',p)
  if p<0:return out
  n=struct.unpack_from('<I',d,p+2)[0] if p+6<=len(d) else -1
  out.append({'offset':p,'declared_body':n,'body_start':p+6,'body_end':p+6+n,'fits':p+6+n<=len(d),'body_head':d[p+6:p+54].hex()});p+=1
def main():
 OUT.mkdir(parents=True,exist_ok=True);r=load(READER,'reader');h=load(HASHER,'hasher');before={'path':str(PKG),'bytes':PKG.stat().st_size,'mtime_ns':PKG.stat().st_mtime_ns,'sha256':sha(PKG)}
 with PKG.open('rb') as f:
  _r,magic,v,to,n=struct.unpack_from('<QIIII',r.aes_ecb(f.read(32)));f.seek(to);tab=r.aes_ecb(f.read(n*48));idx={struct.unpack_from('<Q',tab,i*48)[0]:(i,struct.unpack_from('<QIIIIIi',tab,i*48)) for i in range(n)};rows=[]
  for logical in TARGETS:
   fid=h.path_id(logical);i,row=idx[fid];_fid,off,ps,ds,a,b,flag=row;f.seek(off);raw=r.unpack_entry(f.read(ps),ds,flag);dest=OUT/(Path(logical).stem+f'_{fid:016X}.static.bin');dest.write_bytes(raw);rows.append({'logical_path':logical,'file_id':f'{fid:016X}','entry_index':i,'archive_offset':off,'packed_size':ps,'declared_size':ds,'checks':[a,b],'flag':flag,'raw_copy':str(dest),'raw_bytes':len(raw),'raw_sha256':hashlib.sha256(raw).hexdigest(),'head':raw[:96].hex(),'xbrace':xbrace(raw)})
 after={'path':str(PKG),'bytes':PKG.stat().st_size,'mtime_ns':PKG.stat().st_mtime_ns,'sha256':sha(PKG)}
 if before!=after:raise RuntimeError('source changed')
 rep={'source':after,'source_unchanged':True,'boundary':'static bytes only','rows':rows};p=OUT/'attribute_data_PC_source_lock_001.json';p.write_text(json.dumps(rep,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'report':str(p),'source':after,'rows':rows},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
