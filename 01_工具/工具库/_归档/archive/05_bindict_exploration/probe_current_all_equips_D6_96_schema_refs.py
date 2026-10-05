"""Probe local D6/96 value headers for schema-reference candidates.

No value is decoded or semantically reported. It verifies only whether ULEB
numbers in D6/96 value headers can point to bounded blocks shaped like local
field definitions: count, bitmap width, CHS-slot reference plus one type byte.
The CHS text is used only to make a candidate auditable, not to bind an item.
"""
from pathlib import Path
import hashlib,json,re,struct,zlib
from collections import Counter,defaultdict
from cryptography.hazmat.primitives.ciphers import Cipher,algorithms,modes
PKG=Path(r"E:/mrzh/Documents/script.py314.lc.npk")
OUT=Path(r"C:/Users/<user>/AppData/Local/hermes/mrzh_weapon_skin_audit/run_002/AUG突击步枪定点核查_001/bindict_preflight_002")
K=bytes([0x60,0x63,0x08,0xD8,0xA3,0x2C,0x78,0x20,0x13,0xD2,0x6C,0x2F,0x22,0x6F,0x68,0x6D])
BASE=int('1F8E9684E1B97CE0',16);CHS=int('94AB0B3FD057EF01',16)
def aes(x):
 n=len(x)//16*16
 if not n:return x
 d=Cipher(algorithms.AES(K),modes.ECB()).decryptor();return d.update(x[:n])+d.finalize()+x[n:]
def uleb(d,p,e):
 v=0;s=0
 for _ in range(10):
  if p>=e:raise ValueError('truncated')
  b=d[p];p+=1;v|=(b&127)<<s
  if not b&128:return v,p
  s+=7
 raise ValueError('overlong')
def entries():
 with PKG.open('rb') as f:
  h=aes(f.read(32));_,magic,ver,to,n=struct.unpack_from('<QIIII',h)
  if magic!=0x4b50584e:raise ValueError('bad npk')
  f.seek(to);T=aes(f.read(n*48));o={}
  for i in range(n):
   fid,off,ps,ds,_,_,fl=struct.unpack_from('<QIIIIIi',T,i*48)
   if fid not in (BASE,CHS):continue
   if fl!=0:raise ValueError('flag')
   f.seek(off);p=f.read(ps);q=aes(p);raw=None
   for wb in (15,-15):
    try:raw=zlib.decompress(q[18:],wb);break
    except zlib.error:pass
   if raw is None:raise ValueError('unpack')
   root=struct.unpack_from('<I',raw,0x16)[0];qpos=0x1a+root+7
   if raw[qpos:qpos+2]!=b'x{':raise ValueError('frame')
   ln=struct.unpack_from('<I',raw,qpos+2)[0];body=raw[qpos+6:qpos+6+ln]
   o[fid]={'raw':raw,'body':body,'entry_index':i,'packed_sha256':hashlib.sha256(p).hexdigest(),'raw_sha256':hashlib.sha256(raw).hexdigest()}
  return ver,n,o
def chs_strings(body):
 c,res=struct.unpack_from('<II',body,0);te=8+4*c;ends=struct.unpack_from(f'<{c}I',body,8)
 if res!=0 or te>len(body) or any(a>b for a,b in zip(ends,ends[1:])) or ends[-1]!=len(body)-te:raise ValueError('invalid chs')
 ans=[];last=0
 for e in ends:ans.append(body[te+last:te+e].decode('utf-8','strict'));last=e
 return ans
def index(blob):
 de=struct.unpack_from('<I',blob,0)[0];tail=blob[de:]
 if tail[:3]!=b'\x76\x01\x0b':raise ValueError('tail')
 bc=tail[3];nodes=sorted({struct.unpack_from('<I',tail,4+8*i+4)[0]>>8 for i in range(bc)})
 rows=[]
 for ni,s in enumerate(nodes):
  e=nodes[ni+1] if ni+1<len(nodes) else len(blob);p=s
  while p<e:
   k,p=uleb(blob,p,e);v,p=uleb(blob,p,e);rows.append((k,v))
  if p!=e:raise ValueError('node')
 return de,rows
def identifier(s):return bool(re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*',s or ''))
def try_defs(blob,at,strings):
 # public-style candidate only: n, bitmap_bits, then n x (slot ULEB,type byte)
 try:
  p=at;e=len(blob);n,p=uleb(blob,p,e);bits,p=uleb(blob,p,e)
  if not(1<=n<=128 and 0<=bits<=512):return None
  fs=[]
  for _ in range(n):
   slot,p=uleb(blob,p,e)
   if p>=e or not(0<=slot<len(strings)):return None
   typ=blob[p];p+=1;fs.append((slot,typ,strings[slot]))
  ident=sum(identifier(x[2]) for x in fs)
  # Strong filter: all names must be identifier-ish. This avoids recognizing
  # accidental binary sequences as a field schema.
  if ident!=n:return None
  return {'offset':at,'field_count':n,'bitmap_bits':bits,'end_offset':p,'fields':[{'slot':a,'type_byte':f'0x{b:02x}','name':c} for a,b,c in fs]}
 except (ValueError,struct.error):return None
def main():
 OUT.mkdir(parents=True,exist_ok=True);ver,n,src=entries();base=src[BASE]['body'];chs=src[CHS]['body'];strings=chs_strings(chs)
 c,res=struct.unpack_from('<II',base,0);te=8+4*c
 if res!=0 or any(base[8:te]):raise ValueError('unexpected base pretable')
 blob=base[te:];de,rows=index(blob);heads=[];refs=defaultdict(lambda: {'D6_first':0,'D6_second':0,'96_first':0,'sample_keys':[]})
 for key,at in rows:
  tag=blob[at]
  item={'key_u':key,'value_start':at,'tag':f'0x{tag:02x}','head_hex':blob[at:at+24].hex()}
  try:
   if tag==0xd6:
    a,p=uleb(blob,at+1,de);b,p2=uleb(blob,p,de);item.update({'uleb1':a,'uleb2':b,'header_end':p2});refs[a]['D6_first']+=1;refs[b]['D6_second']+=1;refs[a]['sample_keys'].append(key);refs[b]['sample_keys'].append(key)
   elif tag==0x96:
    a,p=uleb(blob,at+1,de);item.update({'uleb1':a,'header_end':p});refs[a]['96_first']+=1;refs[a]['sample_keys'].append(key)
  except ValueError as exc:item['uleb_error']=repr(exc)
  heads.append(item)
 attempts=[]
 for ref,uses in sorted(refs.items()):
  # Test exact offset relative to blob, and data area only. No guessed base.
  cand=try_defs(blob,ref,strings) if 4<=ref<de else None
  if cand:attempts.append({'reference_offset':ref,'uses':{k:(v[:10] if isinstance(v,list) else v) for k,v in uses.items()},'candidate':cand})
 target_keys={k:next((x for x in heads if x['key_u']==k),None) for k in (10547,10548,10549,10760,11005,11010)}
 out={'analysis':'zero_execution_D6_96_header_schema_pointer_probe','scope':'E:/mrzh only. Candidate schema recognition requires bounded ULEB and every referenced CHS slot be an ASCII identifier; no values, record ends, item mapping or numeric values are inferred.','package':{'sha256':hashlib.sha256(PKG.read_bytes()).hexdigest(),'version':ver,'entry_count':n},'source_members':{'base':{k:v for k,v in src[BASE].items() if k!='raw' and k!='body'},'chs':{k:v for k,v in src[CHS].items() if k!='raw' and k!='body'}},'base_layout':{'zero_table_count':c,'blob_size':len(blob),'data_area_end':de,'indexed_values':len(rows),'tag_counts':dict(sorted(Counter(x['tag'] for x in heads).items()))},'header_reference_stats':{'distinct_references':len(refs),'first_25':[{'offset':a,**{k:(b[:10] if isinstance(b,list) else b) for k,b in v.items()}} for a,v in sorted(refs.items())[:25]]},'accepted_local_field_definition_candidates':attempts,'target_key_headers_uninterpreted':target_keys}
 p=OUT/'体验服_all_equips_D6_96字段定义指针探针_005.json';p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');z=json.loads(p.read_text(encoding='utf-8'));assert z['base_layout']==out['base_layout']
 print(json.dumps({'output':str(p),'summary':{'indexed_values':len(rows),'distinct_header_refs':len(refs),'schema_candidates':len(attempts),'candidate_offsets':[x['reference_offset'] for x in attempts],'target_headers':target_keys}},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
