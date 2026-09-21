"""Validate the current all_equips custom 0x76 hash index without decoding values.

The output deliberately calls the result 'key_to_value_start', not an item
record. It proves only container and pointer structure: packed node offset
(high 24 bits), bounded ULEB pairs, key uniqueness and value starts in the
data area. No value end or field meaning is inferred.
"""
from pathlib import Path
import hashlib,json,struct,zlib
from collections import Counter
from cryptography.hazmat.primitives.ciphers import Cipher,algorithms,modes
PKG=Path(r"E:/mrzh/Documents/script.py314.lc.npk")
OUT=Path(r"C:/Users/Administrator/AppData/Local/hermes/mrzh_weapon_skin_audit/run_002/AUG突击步枪定点核查_001/bindict_preflight_002")
KEY=bytes([0x60,0x63,0x08,0xD8,0xA3,0x2C,0x78,0x20,0x13,0xD2,0x6C,0x2F,0x22,0x6F,0x68,0x6D])
FID=int('1F8E9684E1B97CE0',16)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1<<20):h.update(b)
 return h.hexdigest()
def aes(x):
 n=len(x)//16*16
 if not n:return x
 d=Cipher(algorithms.AES(KEY),modes.ECB()).decryptor();return d.update(x[:n])+d.finalize()+x[n:]
def uleb(d,p,e):
 v=0;s=0;start=p
 for _ in range(10):
  if p>=e:raise ValueError('truncated ULEB at '+str(start))
  b=d[p];p+=1;v|=(b&127)<<s
  if not b&128:return v,p
  s+=7
 raise ValueError('overlong ULEB at '+str(start))
def extract_base():
 with PKG.open('rb') as f:
  h=aes(f.read(32));_,magic,ver,to,n=struct.unpack_from('<QIIII',h)
  if magic!=0x4b50584e:raise ValueError('bad NPK')
  f.seek(to);T=aes(f.read(n*48));hit=None
  for i in range(n):
   fid,off,ps,ds,_,_,fl=struct.unpack_from('<QIIIIIi',T,i*48)
   if fid==FID:hit=(i,off,ps,ds,fl);break
  if hit is None:raise ValueError('base absent')
  i,off,ps,ds,fl=hit
  if fl!=0:raise ValueError('unexpected flag')
  f.seek(off);packed=f.read(ps);q=aes(packed);raw=None;mode=None
  for wb,name in ((15,'zlib'),(-15,'raw_deflate')):
   try:raw=zlib.decompress(q[18:],wb);mode=name;break
   except zlib.error:pass
  if raw is None:raise ValueError('static unpack failure')
  rootlen=struct.unpack_from('<I',raw,0x16)[0];frame=0x1a+rootlen+7
  if raw[frame:frame+2]!=b'x{':raise ValueError('no xbrace')
  blen=struct.unpack_from('<I',raw,frame+2)[0];body=raw[frame+6:frame+6+blen]
  c,res=struct.unpack_from('<II',body,0);tableend=8+4*c
  if frame+6+blen>len(raw) or tableend>len(body):raise ValueError('body bounds')
  return {'entry_index':i,'entry_offset':off,'packed_size':ps,'declared_size':ds,'packed_sha256':hashlib.sha256(packed).hexdigest(),'raw_sha256':hashlib.sha256(raw).hexdigest(),'unpack_style':mode,'body_length':blen,'table_count':c,'table_reserved':res,'table_all_zero':not any(body[8:tableend]),'blob':body[tableend:]}
def main():
 OUT.mkdir(parents=True,exist_ok=True);s=extract_base();b=s.pop('blob');de=struct.unpack_from('<I',b)[0]
 if not (4<=de<len(b)):raise ValueError('data_end invalid')
 tail=b[de:]
 if len(tail)<4 or tail[0:3]!=b'\x76\x01\x0b':raise ValueError('unexpected custom root')
 bc=tail[3];pairs_end=4+8*bc
 if pairs_end>len(tail):raise ValueError('root pairs truncated')
 buckets=[]
 for i in range(bc):
  hv,packed=struct.unpack_from('<II',tail,4+8*i);buckets.append({'hash_u32':hv,'packed_u32':packed,'low_flag_u8':packed&255,'node_offset_high24':packed>>8})
 nodes=sorted(set(x['node_offset_high24'] for x in buckets))
 if not nodes or any(not(de<=x<len(b)) for x in nodes):raise ValueError('node offsets out of blob')
 rows=[];bucket_errors=[]
 for ni,start in enumerate(nodes):
  end=nodes[ni+1] if ni+1<len(nodes) else len(b);p=start;before=len(rows)
  try:
   while p<end:
    k,p=uleb(b,p,end);v,p=uleb(b,p,end);rows.append({'key_u':k,'value_start':v,'bucket_node_offset':start})
   if p!=end:raise ValueError('node cursor does not close')
  except Exception as exc:
   bucket_errors.append({'node_offset':start,'node_end':end,'error':repr(exc),'parsed_before_error':len(rows)-before})
 keys=[x['key_u'] for x in rows];starts=[x['value_start'] for x in rows]
 valid_starts=[x for x in starts if 4<=x<de]
 tag=Counter(f'0x{b[x]:02x}' for x in valid_starts)
 target={k:[x for x in rows if x['key_u']==k] for k in (10547,10548,10549,10760,11005,11010)}
 out={'analysis':'zero_execution_all_equips_0x76_index_validation','scope':'E:/mrzh current py314 only; no payload execution; no inferred records/fields/values','package_sha256':sha(PKG),'base':s,'container':{'blob_size':len(b),'data_area_start':4,'data_area_end_exclusive':de,'tail_size':len(tail),'root_marker':'0x76','key_type':'0x01','value_type':'0x0b','bucket_count_u8':bc,'root_pair_end_within_tail':pairs_end,'bucket_unique_node_count':len(nodes),'bucket_low_flag_counts':dict(sorted(Counter(x['low_flag_u8'] for x in buckets).items())),'node_offset_range':[min(nodes),max(nodes)]},'node_parse':{'node_count':len(nodes),'all_nodes_closed_without_leftover':not bucket_errors,'node_errors':bucket_errors,'key_to_value_start_pair_count':len(rows),'unique_key_count':len(set(keys)),'duplicate_key_count':len(keys)-len(set(keys)),'all_value_starts_in_data_area':len(valid_starts)==len(starts),'valid_value_start_count':len(valid_starts),'invalid_value_start_count':len(starts)-len(valid_starts),'value_start_byte_tag_counts':dict(sorted(tag.items()))},'target_key_locations_uninterpreted':target}
 p=OUT/'体验服_all_equips_0x76索引校验_004.json';p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');read=json.loads(p.read_text(encoding='utf-8'));assert read['node_parse']['key_to_value_start_pair_count']==out['node_parse']['key_to_value_start_pair_count']
 print(json.dumps({'output':str(p),'summary':{'buckets':bc,'nodes':len(nodes),'pairs':len(rows),'unique_keys':len(set(keys)),'node_errors':len(bucket_errors),'valid_starts':len(valid_starts),'tag_counts':dict(sorted(tag.items())),'targets':target}},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
