# -*- coding: utf-8 -*-
"""Read-only static scan for the PC attrs schema/type registry.

Every current py314 entry is decrypted/decompressed as bytes only. No payload is
imported, unmarshalled, evaluated, compiled, or executed.
"""
from __future__ import annotations
import hashlib, importlib.util, json, re, struct
from pathlib import Path

PKG=Path(r"E:/mrzh/Documents/script.py314.lc.npk")
HELPER=Path(r"C:/Users/Administrator/AppData/Local/hermes/mrzh_weapon_skin_audit/run_002/audit_mrzh_aurora_script_presence.py")
OUT=Path(r"E:/mrzh_audit/run_004_PC_BinDict与1DPW专项_001/02_bindict")
TERMS=(b"attrs",b"attack",b"base_attack",b"attack_power",b"damage",b"hurt",b"critical",b"armor",b"fire_speed",b"durability",b"all_equips")
TOKENS=("attr","attack","damage","hurt","critical","armor","defen","fire_speed","durability","equip","weapon","schema","bindict")

def sha_path(p:Path)->str:
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def load_reader():
 spec=importlib.util.spec_from_file_location('readonly_npk_reader',HELPER)
 if not spec or not spec.loader:raise RuntimeError('reader unavailable')
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def d3_strings(d:bytes):
 out=[]
 for i in range(len(d)-2):
  if d[i]!=0xd3:continue
  n=d[i+1];raw=d[i+2:i+2+n]
  if n and len(raw)==n and all(32<=x<127 for x in raw):
   try:out.append((i,raw.decode('ascii')))
   except:pass
 return out
def contexts(d:bytes,term:bytes):
 out=[];p=0
 while len(out)<5:
  at=d.find(term,p)
  if at<0:break
  s=max(0,at-96);e=min(len(d),at+len(term)+160)
  out.append({'offset':at,'hex':d[s:e].hex(),'text':d[s:e].decode('utf-8','backslashreplace')});p=at+1
 return out
def main():
 OUT.mkdir(parents=True,exist_ok=True);reader=load_reader();st0={'size':PKG.stat().st_size,'mtime_ns':PKG.stat().st_mtime_ns,'sha256':sha_path(PKG)}
 rows=[];fail=[];term_counts={x.decode():0 for x in TERMS};decoded=0
 with PKG.open('rb') as f:
  _r,magic,version,to,count=struct.unpack_from('<QIIII',reader.aes_ecb(f.read(32)))
  if magic!=0x4b50584e:raise ValueError('NXPK magic')
  f.seek(to);table=reader.aes_ecb(f.read(count*48))
  for i in range(count):
   fid,off,ps,ds,_a,_b,flag=struct.unpack_from('<QIIIIIi',table,i*48)
   try:
    if off+ps>st0['size']:raise ValueError('entry bounds')
    f.seek(off);packed=f.read(ps)
    if len(packed)!=ps:raise ValueError('short packed')
    raw=reader.unpack_entry(packed,ds,flag);decoded+=1
   except Exception as e:
    if len(fail)<100:fail.append({'entry':i,'file_id':f'{fid:016X}','error':repr(e)})
    continue
   present=[t for t in TERMS if t in raw]
   for t in present:term_counts[t.decode()]+=raw.count(t)
   if not present:continue
   ss=d3_strings(raw)
   rel=[{'offset':p,'text':s} for p,s in ss if any(k in s.lower() for k in TOKENS)]
   ids=[s for _p,s in ss if re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{0,95}',s)]
   paths=[s for _p,s in ss if ('\\' in s or '/' in s) and (s.endswith('.py') or s.endswith('.nxs'))]
   # Keep entries with attrs, or with a dense family of attribute literals.
   lowset={s.lower() for _p,s in ss}
   score=sum(1 for k in ('attrs','attack','base_attack','attack_power','damage','hurt','critical','armor','fire_speed','durability') if any(k in s for s in lowset))
   if b'attrs' not in present and score<3:continue
   rows.append({'entry_index':i,'file_id':f'{fid:016X}','archive_offset':off,'packed_size':ps,'declared_size':ds,'flag':flag,'raw_size':len(raw),'raw_sha256':hashlib.sha256(raw).hexdigest(),'terms':{t.decode():raw.count(t) for t in present},'d3_score':score,'d3_relevant':rel[:500],'d3_identifier_count':len(ids),'d3_identifiers':ids[:1500],'d3_paths':paths[:100],'contexts':{t.decode():contexts(raw,t) for t in present}})
 st1={'size':PKG.stat().st_size,'mtime_ns':PKG.stat().st_mtime_ns,'sha256':sha_path(PKG)}
 if st0!=st1:raise RuntimeError('source changed')
 report={'mode':'read_only_static_literal_and_D3_scan','source':{'path':str(PKG),'version':version,'entry_count':count,**st1},'source_unchanged':True,'execution_boundary':'No game payload imported/marshalled/evaluated/compiled/executed.','entries_decoded':decoded,'decode_failures':len(fail),'failure_samples':fail,'term_byte_counts':term_counts,'matching_entries':rows}
 p=OUT/'当前PC_py314_attrs_schema静态扫描_001.json';p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'report':str(p),'source':report['source'],'decoded':decoded,'failures':len(fail),'matching_entries':len(rows),'compact':[{'entry':r['entry_index'],'fid':r['file_id'],'terms':r['terms'],'score':r['d3_score'],'paths':r['d3_paths'][:8],'relevant':[x['text'] for x in r['d3_relevant'][:40]]} for r in rows]},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
