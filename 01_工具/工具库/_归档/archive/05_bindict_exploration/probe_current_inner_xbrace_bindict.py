"""Read-only framing audit for the *inner* x{ BinDict body in current py314.

The direct raw member begins with a Python/NXS object envelope. This script
first validates that envelope's root-code length and x{ body framing, then
compares base/CHS/YK internal bodies. It does not execute, compile, marshal,
or import a game payload.
"""
from pathlib import Path
import hashlib, json, struct, zlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

PKG=Path(r"E:/mrzh/Documents/script.py314.lc.npk")
OUT=Path(r"C:/Users/<user>/AppData/Local/hermes/mrzh_weapon_skin_audit/run_002/AUG突击步枪定点核查_001/bindict_preflight_002")
KEY=bytes([0x60,0x63,0x08,0xD8,0xA3,0x2C,0x78,0x20,0x13,0xD2,0x6C,0x2F,0x22,0x6F,0x68,0x6D])
TARGETS={'base':int('1F8E9684E1B97CE0',16),'chs':int('94AB0B3FD057EF01',16),'yk':int('0F92F8F525E6D201',16)}
def sha_file(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1<<20):h.update(b)
 return h.hexdigest()
def aes(x):
 n=len(x)//16*16
 if not n:return x
 d=Cipher(algorithms.AES(KEY),modes.ECB()).decryptor();return d.update(x[:n])+d.finalize()+x[n:]
def uleb(data,pos,end):
 val=0;sh=0
 for _ in range(10):
  if pos>=end:return None,pos,'truncated'
  b=data[pos];pos+=1;val|=(b&127)<<sh
  if not b&128:return val,pos,None
  sh+=7
 return None,pos,'overlong'
def raw_targets():
 with PKG.open('rb') as f:
  hdr=aes(f.read(32));_,magic,ver,to,n=struct.unpack_from('<QIIII',hdr)
  if magic!=0x4b50584e:raise ValueError('bad NPK magic')
  f.seek(to);T=aes(f.read(n*48));out={}
  for i in range(n):
   fid,off,ps,ds,_,_,fl=struct.unpack_from('<QIIIIIi',T,i*48)
   label=next((a for a,b in TARGETS.items() if b==fid),None)
   if label is None:continue
   if fl!=0:raise ValueError(label+' flag !=0')
   f.seek(off);packed=f.read(ps);dec=aes(packed);raw=None;style=None
   for wb,name in ((15,'zlib'),(-15,'raw_deflate')):
    try:raw=zlib.decompress(dec[18:],wb);style=name;break
    except zlib.error:pass
   if raw is None:raise ValueError(label+' no stream')
   out[label]={'entry_index':i,'entry_offset':off,'packed_size':ps,'declared_size':ds,'raw':raw,'raw_sha256':hashlib.sha256(raw).hexdigest(),'packed_sha256':hashlib.sha256(packed).hexdigest(),'unpack_style':style}
  return ver,n,out
def analyze(label,src):
 raw=src['raw'];r={'entry_index':src['entry_index'],'entry_offset':src['entry_offset'],'packed_size':src['packed_size'],'declared_size':src['declared_size'],'packed_sha256':src['packed_sha256'],'raw_size':len(raw),'raw_sha256':src['raw_sha256'],'unpack_style':src['unpack_style'],'checks':[]}
 def ck(name,ok,detail):r['checks'].append({'check':name,'pass':bool(ok),'detail':detail})
 if len(raw)<0x1a:ck('root_header',False,{'reason':'raw short'});return r
 root_len=struct.unpack_from('<I',raw,0x16)[0];root_start=0x1a;root_end=root_start+root_len;q=root_end+7
 r['root']={'tag':f'0x{raw[0]:02x}','tag_at_0x15':f'0x{raw[0x15]:02x}','code_length_u32_at_0x16':root_len,'code_start':root_start,'code_end':root_end,'Q_after_root_plus_7':q}
 ck('root_code_within_raw',root_end<=len(raw),{'root_end':root_end,'raw_size':len(raw)})
 ck('xbrace_at_Q',q+6<=len(raw) and raw[q:q+2]==b'x{',{'bytes_at_Q':raw[q:q+12].hex()})
 if not root_end<=len(raw) or q+6>len(raw) or raw[q:q+2]!=b'x{':return r
 body_len=struct.unpack_from('<I',raw,q+2)[0];bs=q+6;be=bs+body_len
 r['xbrace']={'body_length_u32':body_len,'body_start':bs,'body_end':be,'head32_hex':raw[bs:bs+32].hex()}
 ck('xbrace_body_within_raw',be<=len(raw),{'body_end':be,'raw_size':len(raw)})
 if be>len(raw) or body_len<8:return r
 body=raw[bs:be];count,reserved=struct.unpack_from('<II',body,0);tab_end=8+4*count
 r['body_header']={'u32_count':count,'u32_reserved':reserved,'table_start':8,'table_end':tab_end,'body_size':len(body)}
 ck('count_table_in_body',tab_end<=len(body),{'count':count,'table_end':tab_end,'body_size':len(body)})
 if tab_end>len(body):return r
 vals=list(struct.unpack_from(f'<{count}I',body,8)) if count else []
 r['first_u32_table_head']=vals[:16];r['first_u32_table_tail']=vals[-8:]
 r['first_u32_table_stats']={'monotonic_non_decreasing':all(a<=b for a,b in zip(vals,vals[1:])),'zero_count':sum(x==0 for x in vals),'max':max(vals) if vals else 0,'last':vals[-1] if vals else 0,'body_bytes_after_table':len(body)-tab_end}
 # CHS-style end offset test; only reported if it fully proves itself.
 maxend=vals[-1] if vals else 0; raw_len=len(body)-tab_end
 chs_ok=bool(vals) and all(a<=b for a,b in zip(vals,vals[1:])) and maxend==raw_len
 r['chs_style_end_offset_test']={'accepted':chs_ok,'raw_start':tab_end,'raw_length':raw_len,'last_end_offset':maxend}
 if chs_ok:
  prev=0;bad=0;find={}
  for i,e in enumerate(vals):
   try:t=body[tab_end+prev:tab_end+e].decode('utf-8','strict')
   except UnicodeDecodeError:bad+=1;t=None
   if t in ('AUG突击步枪','AUG突击体验版','AUG突击典藏版','AUG突击雨战版','AUG突击雪地版'):find[t]=i
   prev=e
  r['chs_style_end_offset_test'].update({'strict_utf8_errors':bad,'exact_aug_strings':find})
 # Custom data-area test (known old working family): u32 data_end + 0x76 tail.
 if len(body)-tab_end>=4:
  blob=body[tab_end:];data_end=struct.unpack_from('<I',blob,0)[0]
  r['post_table_blob']={'size':len(blob),'u32_data_end':data_end,'head64_hex':blob[:64].hex()}
  idx_ok=4<=data_end<len(blob) and blob[data_end:data_end+1]==b'\x76'
  r['post_table_blob']['custom_0x76_tail_test']={'accepted':idx_ok,'byte_at_data_end':f'0x{blob[data_end]:02x}' if 0<=data_end<len(blob) else None}
  if idx_ok and data_end+4<=len(blob):
   tail=blob[data_end:]; ktype,vtype,decl=tail[1],tail[2],tail[3];pairs_end=4+8*decl
   pairs_ok=pairs_end<=len(tail)
   r['post_table_blob']['custom_0x76_tail_test'].update({'key_type_byte':f'0x{ktype:02x}','value_type_byte':f'0x{vtype:02x}','declared_pair_count_u8':decl,'pairs_end':pairs_end,'pairs_in_bounds':pairs_ok})
   if pairs_ok:
    pairs=[struct.unpack_from('<II',tail,4+8*i) for i in range(decl)]
    offs=[x[1] for x in pairs]
    r['post_table_blob']['custom_0x76_tail_test'].update({'unique_second_u32':len(set(offs)),'second_u32_range':[min(offs),max(offs)] if offs else None,'all_second_u32_in_data_area':all(4<=x<data_end for x in offs),'pair_sample_first8':[{'hash_u32':a,'second_u32':b,'byte_at_second':f'0x{blob[b]:02x}' if 0<=b<len(blob) else None} for a,b in pairs[:8]]})
 r['inner_frame_validated']=all(x['pass'] for x in r['checks'])
 return r
def main():
 OUT.mkdir(parents=True,exist_ok=True);ver,n,sources=raw_targets();out={'analysis':'zero_execution_inner_xbrace_body_framing','scope':'E:/mrzh only; no source writes; no code/payload execution','package':{'path':str(PKG),'sha256':sha_file(PKG),'version':ver,'entry_count':n},'variants':{a:analyze(a,b) for a,b in sources.items()}}
 p=OUT/'体验服_内层BinDictFrame结构核查_003.json';p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');check=json.loads(p.read_text(encoding='utf-8'));assert check['package']==out['package']
 summ={a:{'inner_frame_validated':b.get('inner_frame_validated',False),'count':b.get('body_header',{}).get('u32_count'),'chs_end_pool':b.get('chs_style_end_offset_test',{}).get('accepted'),'custom_tail':b.get('post_table_blob',{}).get('custom_0x76_tail_test',{}).get('accepted')} for a,b in out['variants'].items()};print(json.dumps({'output':str(p),'summary':summ},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
