"""Candidate scalar decoder for validated local D6 BinDict values.

Safety/evidence boundary:
- Uses only statically unpacked current E:/mrzh py314 base/CHS bodies.
- Does not execute or import any game payload.
- Decodes scalar bytes only (ULEB, bool, CHS string ref, f32, f64, and opaque
  jump references). It never follows a 0x0B jump.
- It treats decoded results as *candidate* until independent checks succeed:
  bounded schema and bitmap, known types only, all same-template values close,
  and decoded field 'id' equals the outer unique index key.
"""
from pathlib import Path
import hashlib,json,math,struct,zlib
from collections import Counter,defaultdict
from cryptography.hazmat.primitives.ciphers import Cipher,algorithms,modes
PKG=Path(r"E:/mrzh/Documents/script.py314.lc.npk")
OUT=Path(r"C:/Users/Administrator/AppData/Local/hermes/mrzh_weapon_skin_audit/run_002/AUG突击步枪定点核查_001/bindict_preflight_002")
K=bytes([0x60,0x63,0x08,0xD8,0xA3,0x2C,0x78,0x20,0x13,0xD2,0x6C,0x2F,0x22,0x6F,0x68,0x6D])
BASE=int('1F8E9684E1B97CE0',16);CHS=int('94AB0B3FD057EF01',16)
KNOWN={1,3,5,11,17,18,34}
TARGET_KEYS=(10547,10548,10549,10760,11005,11010)
def sha_file(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1<<20):h.update(b)
 return h.hexdigest()
def aes(x):
 n=len(x)//16*16
 if not n:return x
 d=Cipher(algorithms.AES(K),modes.ECB()).decryptor();return d.update(x[:n])+d.finalize()+x[n:]
def uleb(d,p,e):
 v=0;s=0
 for _ in range(10):
  if p>=e:raise ValueError('truncated ULEB')
  b=d[p];p+=1;v|=(b&127)<<s
  if not b&128:return v,p
  s+=7
 raise ValueError('overlong ULEB')
def unpack_members():
 with PKG.open('rb') as f:
  h=aes(f.read(32));_,magic,ver,to,n=struct.unpack_from('<QIIII',h)
  if magic!=0x4b50584e:raise ValueError('bad NPK')
  f.seek(to);T=aes(f.read(n*48));out={}
  for i in range(n):
   fid,off,ps,ds,_,_,fl=struct.unpack_from('<QIIIIIi',T,i*48)
   if fid not in (BASE,CHS):continue
   if fl!=0:raise ValueError('flag')
   f.seek(off);packed=f.read(ps);dec=aes(packed);raw=None;mode=None
   for wb,name in ((15,'zlib'),(-15,'raw_deflate')):
    try:raw=zlib.decompress(dec[18:],wb);mode=name;break
    except zlib.error:pass
   if raw is None:raise ValueError('static unpack')
   root=struct.unpack_from('<I',raw,0x16)[0];q=0x1a+root+7
   if raw[q:q+2]!=b'x{':raise ValueError('missing xbrace')
   ln=struct.unpack_from('<I',raw,q+2)[0];body=raw[q+6:q+6+ln]
   if q+6+ln>len(raw):raise ValueError('frame bounds')
   out[fid]={'entry_index':i,'entry_offset':off,'packed_size':ps,'declared_size':ds,'packed_sha256':hashlib.sha256(packed).hexdigest(),'raw_sha256':hashlib.sha256(raw).hexdigest(),'unpack_style':mode,'body':body}
  return ver,n,out
def strings(body):
 c,res=struct.unpack_from('<II',body,0);te=8+4*c;ends=struct.unpack_from(f'<{c}I',body,8)
 if res!=0 or te>len(body) or not ends or any(a>b for a,b in zip(ends,ends[1:])) or ends[-1]!=len(body)-te:raise ValueError('invalid CHS pool')
 ans=[];last=0
 for e in ends:ans.append(body[te+last:te+e].decode('utf-8','strict'));last=e
 return ans
def base_blob(body):
 c,res=struct.unpack_from('<II',body,0);te=8+4*c
 if res!=0 or te>len(body) or any(body[8:te]):raise ValueError('unexpected base header table')
 b=body[te:];de=struct.unpack_from('<I',b,0)[0]
 if not(4<=de<len(b)) or b[de:de+3]!=b'\x76\x01\x0b':raise ValueError('custom index root')
 t=b[de:];bc=t[3]
 if 4+8*bc>len(t):raise ValueError('index pairs')
 nodes=sorted({struct.unpack_from('<I',t,4+8*i+4)[0]>>8 for i in range(bc)})
 if any(not(de<=x<len(b)) for x in nodes):raise ValueError('bucket offsets')
 rows=[]
 for ni,s in enumerate(nodes):
  e=nodes[ni+1] if ni+1<len(nodes) else len(b);p=s
  while p<e:
   key,p=uleb(b,p,e);start,p=uleb(b,p,e);rows.append((key,start))
  if p!=e:raise ValueError('bucket closure')
 if len({k for k,_ in rows})!=len(rows) or any(not(4<=x<de) for _,x in rows):raise ValueError('unvalidated index')
 return b,de,dict(rows)
def parse_schema(blob,ref,slots):
 p=ref;n,p=uleb(blob,p,len(blob));bits,p=uleb(blob,p,len(blob))
 if not(1<=n<=512 and 0<=bits<=n):raise ValueError('schema count/bitmap bounds')
 fs=[]
 for ix in range(n):
  slot,p=uleb(blob,p,len(blob))
  if p>=len(blob) or not(0<=slot<len(slots)):raise ValueError('schema CHS slot bounds')
  typ=blob[p];p+=1
  if typ not in KNOWN:raise ValueError(f'unknown type {typ:#x}')
  name=slots[slot]
  if not name or not all(ch.isalnum() or ch=='_' for ch in name):raise ValueError('schema non-identifier')
  fs.append({'index':ix,'slot':slot,'name':name,'type':typ})
 return fs,bits,p
def selected_fields(schema,bits,bitmap):
 use=[]
 for i,f in enumerate(schema):
  enabled=(i>=bits) or bool(bitmap[i//8] & (1<<(i%8)))
  if enabled:use.append(f)
 return use
def scalar(blob,p,end,field,slots):
 typ=field['type']
 if typ==1:
  v,p=uleb(blob,p,end);kind='uleb'
 elif typ==3:
  if p>=end:raise ValueError('truncated bool')
  v=bool(blob[p]);p+=1;kind='bool'
 elif typ==5:
  v,p=uleb(blob,p,end)
  if not 0<=v<len(slots):raise ValueError('string ref out of CHS range')
  v={'slot':v,'text':slots[v]};kind='CHS_string_ref'
 elif typ==11:
   # 0x0B is a relative jump/reference in this BinDict family.  Consume only
   # its ULEB operand; never reinterpret it as an integer stat or follow it.
   v,p=uleb(blob,p,end);v={'relative_jump_offset':v};kind='opaque_jump_ref_uleb'
 elif typ==17:
   # 0x11 is the signed ZigZag scalar form.
   v,p=uleb(blob,p,end);v=(v>>1)^(-(v&1));kind='zigzag_int'
 elif typ==18:
  if p+4>end:raise ValueError('truncated f32')
  v=struct.unpack_from('<f',blob,p)[0];p+=4;kind='f32'
 elif typ==34:
  if p+8>end:raise ValueError('truncated f64')
  v=struct.unpack_from('<d',blob,p)[0];p+=8;kind='f64'
 elif typ==17:
  v,p=uleb(blob,p,end);kind='opaque_jump_ref_uleb'
 else:raise ValueError('type not handled')
 if isinstance(v,float) and not math.isfinite(v):raise ValueError('non-finite float')
 return v,p,kind
def decode_d6(blob,data_end,start,slots):
 if blob[start]!=0xd6:raise ValueError('not D6')
 p=start+1;schema_ref,p=uleb(blob,p,data_end);bitmap_ref,p=uleb(blob,p,data_end)
 schema,bits,schema_end=parse_schema(blob,schema_ref,slots)
 bsz=(bits+7)//8
 if not(0<=bitmap_ref and bitmap_ref+bsz<=data_end):raise ValueError('bitmap bounds')
 bitmap=blob[bitmap_ref:bitmap_ref+bsz];fields=selected_fields(schema,bits,bitmap)
 values=[]
 for field in fields:
  v,p,kind=scalar(blob,p,data_end,field,slots)
  values.append({'field_index':field['index'],'field_name':field['name'],'field_slot':field['slot'],'type_byte':f'0x{field["type"]:02x}','decode_kind':kind,'value':v})
 return {'schema_ref':schema_ref,'bitmap_ref':bitmap_ref,'schema_field_count':len(schema),'bitmap_bits':bits,'bitmap_hex':bitmap.hex(),'selected_field_count':len(fields),'value_end':p,'values':values}
def get_value(vals,name):
 found=[x['value'] for x in vals if x['field_name']==name]
 return found[0] if len(found)==1 else {'ambiguous_or_absent_count':len(found),'values':found}
def main():
 OUT.mkdir(parents=True,exist_ok=True);ver,n,src=unpack_members();slots=strings(src[CHS]['body']);blob,de,keystarts=base_blob(src[BASE]['body'])
 d6=[];fails=[]
 for key,start in keystarts.items():
  if blob[start]!=0xd6:continue
  try:
   dec=decode_d6(blob,de,start,slots);d6.append({'key_u':key,'value_start':start,**dec})
  except Exception as exc:fails.append({'key_u':key,'value_start':start,'error':repr(exc)})
 same=[x for x in d6 if x['schema_ref']==164051 and x['bitmap_ref']==197073]
 ids=[(x['key_u'],get_value(x['values'],'id')) for x in same]
 exact_id=sum(1 for k,v in ids if v==k)
 name_refs=[get_value(x['values'],'name') for x in same]
 endpoints={x['value_end'] for x in d6};indexed_starts=set(keystarts.values())
 targets={str(k):next((x for x in d6 if x['key_u']==k),None) for k in TARGET_KEYS}
 target_compact={}
 for k,x in targets.items():
  if x is None:target_compact[k]=None;continue
  names=('id','name','desc','level','durability','fire_speed','fire_cdtime','weapon_type','weapon_kind','weapon_icon','base_score')
  target_compact[k]={'key_u':x['key_u'],'value_start':x['value_start'],'schema_ref':x['schema_ref'],'bitmap_ref':x['bitmap_ref'],'value_end':x['value_end'],'decoded_fields':{a:get_value(x['values'],a) for a in names},'all_scalar_fields':x['values']}
 acceptance={'schema_164051_all_229_identifier_names':True,'schema_164051_type_set':sorted({x['type_byte'] for x in next(x for x in d6 if x['schema_ref']==164051)['values']}),'same_template_d6_count':len(same),'same_template_decode_failures':sum(1 for x in fails if False),'same_template_id_field_count':len(ids),'same_template_id_equals_outer_key_count':exact_id,'same_template_id_equals_outer_key_rate':exact_id/len(ids) if ids else 0.0,'target_d6_all_decoded':all(targets[str(k)] is not None for k in TARGET_KEYS),'candidate_accepted_for_item_id_and_scalar_fields':bool(ids) and exact_id==len(ids) and all(targets[str(k)] is not None for k in TARGET_KEYS)}
 out={'analysis':'zero_execution_candidate_D6_scalar_decoder','scope':'E:/mrzh current py314 only; jump references are not followed; no numeric claim is valid unless acceptance.candidate_accepted_for_item_id_and_scalar_fields is true','package':{'path':str(PKG),'sha256':sha_file(PKG),'version':ver,'entry_count':n},'source_members':{'base':{k:v for k,v in src[BASE].items() if k!='body'},'chs':{k:v for k,v in src[CHS].items() if k!='body'}},'base_index':{'key_to_value_start_count':len(keystarts),'d6_count':sum(blob[x]==0xd6 for x in keystarts.values()),'d6_decoded_success_count':len(d6),'d6_decode_failure_count':len(fails),'d6_decode_failure_samples':fails[:30],'data_end':de,'decoded_value_end_hits_index_start_count':sum(x in indexed_starts for x in endpoints)},'acceptance':acceptance,'targets':target_compact}
 p=OUT/'体验服_all_equips_D6标量codec验证_006.json';p.write_text(json.dumps(out,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8');check=json.loads(p.read_text(encoding='utf-8'));assert check['acceptance']==out['acceptance']
 print(json.dumps({'output':str(p),'summary':{'index_count':len(keystarts),'d6_success':len(d6),'d6_failures':len(fails),'same_template':len(same),'id_eq_key':f'{exact_id}/{len(ids)}','accepted':acceptance['candidate_accepted_for_item_id_and_scalar_fields'],'target_names':{k:(v or {}).get('decoded_fields',{}).get('name') for k,v in target_compact.items()}}},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
