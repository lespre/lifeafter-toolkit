"""Zero-execution structural preflight for current test-server BinDict bodies.

This is deliberately narrower than a value decoder.  It validates the public
NeoXtractor parser's *entry assumptions* against direct, statically unpacked
E:/mrzh py314 all_equips_data bodies: string pool, jump base, relative hash
region and every hash-index target range.  It does not infer values or execute
payloads.
"""
from pathlib import Path
import hashlib, json, struct, zlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

PKG = Path(r"E:/mrzh/Documents/script.py314.lc.npk")
OUT = Path(r"C:/Users/<user>/AppData/Local/hermes/mrzh_weapon_skin_audit/run_002/AUG突击步枪定点核查_001/bindict_preflight_002")
KEY = bytes([0x60,0x63,0x08,0xD8,0xA3,0x2C,0x78,0x20,0x13,0xD2,0x6C,0x2F,0x22,0x6F,0x68,0x6D])
TARGETS = {
    "all_equips_base": int("1F8E9684E1B97CE0", 16),
    "all_equips_chs": int("94AB0B3FD057EF01", 16),
    "all_equips_yk": int("0F92F8F525E6D201", 16),
    "BindictHelper": int("0EF6B1F0B69A79CB", 16),
}

def sha256_file(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        while b:=f.read(1<<20): h.update(b)
    return h.hexdigest()

def aes(data):
    n=len(data)//16*16
    if not n: return data
    d=Cipher(algorithms.AES(KEY),modes.ECB()).decryptor()
    return d.update(data[:n])+d.finalize()+data[n:]

def uleb(data, pos, limit):
    value=0; shift=0; start=pos
    for _ in range(10):
        if pos>=limit: return None, pos, "truncated"
        b=data[pos];pos+=1;value|=(b&127)<<shift
        if not b&128:return value,pos,None
        shift+=7
    return None,pos,"more_than_10_bytes"

def get_entries():
    with PKG.open('rb') as f:
        h=aes(f.read(32));_,magic,version,to,n=struct.unpack_from('<QIIII',h)
        if magic!=0x4b50584e: raise ValueError('unexpected NPK magic')
        f.seek(to); table=aes(f.read(n*48))
        result={}
        for i in range(n):
            fid,off,psz,dsz,_,_,flag=struct.unpack_from('<QIIIIIi',table,i*48)
            for label,want in TARGETS.items():
                if fid==want:
                    if flag!=0: raise ValueError(f'{label}: expected flag0, got {flag}')
                    f.seek(off); packed=f.read(psz); dec=aes(packed)
                    raw=None; trace=[]
                    for wb,name in ((15,'zlib'),(-15,'raw_deflate')):
                        try:
                            raw=zlib.decompress(dec[18:],wb); trace.append(name);break
                        except zlib.error as e: trace.append(f'{name}_fail')
                    if raw is None: raise ValueError(f'{label}: no verified zlib stream')
                    result[label]={'entry_index':i,'offset':off,'packed_size':psz,'declared_size':dsz,'packed_sha256':hashlib.sha256(packed).hexdigest(),'raw':raw,'trace':trace}
        return version,n,result

def preflight(label,item):
    d=item['raw']; n=len(d)
    out={'entry_index':item['entry_index'],'entry_offset':item['offset'],'packed_size':item['packed_size'],'declared_size':item['declared_size'],'packed_sha256':item['packed_sha256'],'raw_size':n,'raw_sha256':hashlib.sha256(d).hexdigest(),'static_unpack_trace':item['trace'],'checks':[]}
    def check(name,ok,detail): out['checks'].append({'check':name,'pass':bool(ok),'detail':detail})
    if n<8:
        check('minimum_header',False,{'raw_size':n});out['accepted_for_public_layout']=False;return out
    count,pad=struct.unpack_from('<II',d,0)
    out['string_count_u32']=count;out['padding_u32']=pad
    check('bounded_string_count',0<=count<=500000,{'count':count})
    off_end=8+4*count
    check('offset_table_in_bounds',off_end<=n,{'offset_table_end':off_end,'raw_size':n})
    if off_end>n: out['accepted_for_public_layout']=False;return out
    ends=list(struct.unpack_from(f'<{count}I',d,8)) if count else []
    terminal=ends[-1] if ends else 0
    monotonic=all(a<=b for a,b in zip(ends,ends[1:]))
    raw_start=off_end; jump_base=raw_start+terminal
    out.update({'string_ends_head':ends[:12],'string_ends_tail':ends[-5:],'string_raw_start':raw_start,'string_raw_length_from_terminal_end':terminal,'jump_base_candidate':jump_base})
    check('end_offsets_monotonic',monotonic,{'count':count})
    check('jump_base_in_bounds',raw_start<=jump_base<=n,{'jump_base':jump_base,'raw_size':n})
    strings=[];prev=0;decode_errors=0
    if jump_base<=n:
        for e in ends:
            try: strings.append(d[raw_start+prev:raw_start+e].decode('utf-8','strict'))
            except UnicodeDecodeError: decode_errors+=1; strings.append(None)
            prev=e
    out['string_utf8_decode_errors']=decode_errors;out['string_samples']=[{'slot':i,'text':x} for i,x in enumerate(strings[:40])]
    check('all_pool_strings_strict_utf8',decode_errors==0,{'decode_errors':decode_errors})
    if jump_base+4>n:
        check('relative_hash_offset_in_bounds',False,{'reason':'no_u32_at_jump_base'});out['accepted_for_public_layout']=False;return out
    rel=struct.unpack_from('<I',d,jump_base)[0]; abspos=jump_base+rel
    out.update({'hash_offset_relative_u32':rel,'hash_region_absolute_candidate':abspos})
    check('relative_hash_offset_in_bounds',jump_base<=abspos<n,{'jump_base':jump_base,'relative':rel,'absolute':abspos,'raw_size':n})
    if not jump_base<=abspos<n:out['accepted_for_public_layout']=False;return out
    marker=d[abspos];out['hash_region_marker']=f'0x{marker:02x}'
    check('public_parser_root_marker_supported',marker in (0x56,0x66,0x76),{'marker':f'0x{marker:02x}','supported':['0x56','0x66','0x76']})
    if marker not in (0x56,0x66,0x76) or abspos+3>n:out['accepted_for_public_layout']=False;return out
    cursor=abspos+1
    if marker==0x56:
        types={'key_type':d[cursor]};cursor+=1
    elif marker==0x66:
        types={'value_type':d[cursor]};cursor+=1
    else:
        types={'key_type':d[cursor],'value_type':d[cursor+1]};cursor+=2
    entries,cursor,err=uleb(d,cursor,n)
    out['hash_region_types']=types;out['hash_region_declared_entry_count']=entries;out['hash_region_count_uleb_error']=err;out['hash_index_pairs_start']=cursor
    check('hash_index_count_uleb_valid',entries is not None and err is None,{'entries':entries,'error':err})
    if entries is None:out['accepted_for_public_layout']=False;return out
    pairs_end=cursor+8*entries
    check('hash_index_pairs_in_bounds',pairs_end<=n,{'pairs_end':pairs_end,'raw_size':n,'entries':entries})
    if pairs_end>n:out['accepted_for_public_layout']=False;return out
    pairs=[];targets=[]
    for k in range(entries):
        hv,ov=struct.unpack_from('<II',d,cursor+8*k);ta=jump_base+ov
        pairs.append({'hash_u32':hv,'relative_offset':ov,'absolute_offset':ta});targets.append(ta)
    out['hash_index_unique_targets']=len(set(targets));out['hash_index_target_range']={'min':min(targets) if targets else None,'max':max(targets) if targets else None};out['hash_index_pair_sample_first10']=pairs[:10]
    valid_targets=all(jump_base<=x<n for x in targets)
    check('all_hash_index_targets_in_bounds',valid_targets,{'targets':len(targets),'valid':sum(jump_base<=x<n for x in targets),'jump_base':jump_base,'raw_size':n})
    out['target_byte_sample_first20']=[{'absolute_offset':x,'byte':f'0x{d[x]:02x}'} for x in targets[:20] if 0<=x<n]
    required=['bounded_string_count','offset_table_in_bounds','end_offsets_monotonic','jump_base_in_bounds','all_pool_strings_strict_utf8','relative_hash_offset_in_bounds','public_parser_root_marker_supported','hash_index_count_uleb_valid','hash_index_pairs_in_bounds','all_hash_index_targets_in_bounds']
    out['accepted_for_public_layout']=all(next(c['pass'] for c in out['checks'] if c['check']==r) for r in required)
    return out

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    ver,n,items=get_entries()
    result={'analysis':'zero_execution_public_bindict_layout_preflight','scope':'E:/mrzh only; direct current py314 members; no imports/eval/exec/marshal.loads','package':{'path':str(PKG),'sha256':sha256_file(PKG),'version':ver,'entry_count':n},'targets':{label:preflight(label,item) for label,item in items.items()}}
    p=OUT/'体验服_BinDict公共布局预检_002.json';p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    check=json.loads(p.read_text(encoding='utf-8')); assert check['package']==result['package']
    summary={x:{'accepted':y['accepted_for_public_layout'],'marker':y.get('hash_region_marker'),'entries':y.get('hash_region_declared_entry_count'),'strings':y.get('string_count_u32')} for x,y in result['targets'].items()}
    print(json.dumps({'output':str(p),'summary':summary},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
