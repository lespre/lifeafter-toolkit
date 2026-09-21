# -*- coding: utf-8 -*-
"""END-TO-END: all_equips AUG family row -> 0x0B attrs reference -> attrs object -> {hurt,power}.

Static read of E:/mrzh current all_equips (BASE/CHS pair). No game payload is
imported, unmarshalled, evaluated or executed.
"""
from __future__ import annotations
import json,runpy,struct
from pathlib import Path
import os
_SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
OUT = _SCRIPT_DIR / 'output' / 'bindict_attrs'
_LIB = _SCRIPT_DIR / 'bindict_lib' / 'decode_current_all_equips_D6_scalar_006.py'
if not _LIB.exists():
    _LIB = Path(r'C:/Users/Administrator/AppData/Local/hermes/mrzh_weapon_skin_audit/run_002/bindict_preflight_002/decode_current_all_equips_D6_scalar_006.py')
M=runpy.run_path(str(_LIB),run_name='ae3')
uleb=M['uleb']
ver,n,src=M['unpack_members']()
slots=M['strings'](src[M['CHS']]['body'])
blob,de,keystarts=M['base_blob'](src[M['BASE']]['body'])
def schema_at(ref):
 p=ref;n2,p=uleb(blob,p,len(blob));bits,p=uleb(blob,p,len(blob))
 fs=[]
 for ix in range(n2):
  slot,p=uleb(blob,p,len(blob));typ=blob[p];p+=1
  fs.append({'index':ix,'slot':slot,'type':typ,'name':slots[slot] if slot<len(slots) else f'<bad{slot}>'})
 return n2,bits,fs,p
# 1) full attrs schema at 6109
n2,bits,fs,schema_end=schema_at(6109)
assert n2==55 and bits==55
schema={'schema_ref':6109,'field_count':n2,'bitmap_bits':bits,'fields':fs,'schema_end':schema_end}
# 2) find all rows whose 0x0B operand resolves to a c6/c6+6109 attrs object
def decode_row(key,start):
 if blob[start]!=0xd6:return None
 p=start+1;sref,p=uleb(blob,p,len(blob));bref,p=uleb(blob,p,len(blob))
 n3,bits3,fs3,se=schema_at(sref)
 bm=blob[bref:bref+(bits3+7)//8]
 use=[f for f in fs3 if f['index']>=bits3 or bm[f['index']//8]&(1<<(f['index']%8))]
 vals=[];ops=[]
 for f in use:
  typ=f['type']
  if typ==1:v,p=uleb(blob,p,len(blob))
  elif typ==3:v=blob[p];p+=1
  elif typ==5:v,p=uleb(blob,p,len(blob))
  elif typ==11:v,p=uleb(blob,p,len(blob));ops.append((f['index'],f['name'],v))
  elif typ==17:v,p=uleb(blob,p,len(blob));v=(v>>1)^(-(v&1))
  elif typ==18:v=struct.unpack_from('<f',blob,p)[0];p+=4
  elif typ==34:v=struct.unpack_from('<d',blob,p)[0];p+=8
  else:return None
  vals.append({'index':f['index'],'name':f['name'],'type':hex(typ),'value':v})
 return {'key':key,'start':start,'schema_ref':sref,'bitmap_ref':bref,'values':vals,'ops':ops}
rows=[decode_row(k,st) for k,st in keystarts.items()]
rows=[r for r in rows if r]
# find attrs-object operand targets
ATTRS_REF=6109
def attrs_obj_at(off):
 if off>=len(blob) or blob[off] not in (0xc6,0x86,0xd6):return None
 p=off+1;sr,p=uleb(blob,p,len(blob))
 if sr!=ATTRS_REF:return None
 br,p=uleb(blob,p,len(blob))
 n4,bits4,fs4,se=schema_at(sr)
 bm=blob[br:br+(bits4+7)//8]
 use=[f for f in fs4 if f['index']>=bits4 or bm[f['index']//8]&(1<<(f['index']%8))]
 vals=[]
 for f in use:
  typ=f['type']
  if typ==1:v,p=uleb(blob,p,len(blob))
  elif typ==3:v=blob[p];p+=1
  elif typ==5:v,p=uleb(blob,p,len(blob))
  elif typ==11:v,p=uleb(blob,p,len(blob))
  elif typ==17:v,p=uleb(blob,p,len(blob));v=(v>>1)^(-(v&1))
  elif typ==18:v=struct.unpack_from('<f',blob,p)[0];p+=4
  elif typ==34:v=struct.unpack_from('<d',blob,p)[0];p+=8
  else:return None
  vals.append({'index':f['index'],'name':f['name'],'type':hex(typ),'value':v})
 return {'offset':off,'marker':hex(blob[off]),'schema_ref':sr,'bitmap_ref':br,'bitmap_hex':bm.hex(),'values':vals,'end':p}
# collect all 0x0B operands
opmap={}
for r in rows:
 for ix,name,v in r['ops']:
  opmap.setdefault(v,[]).append({'key':r['key'],'field_index':ix,'field_name':name})
targets={v for v in opmap if attrs_obj_at(v)}
# report AUG family: rows whose attrs operand -> 6109 object
aug_family=[]
for v in sorted(targets):
 obj=attrs_obj_at(v)
 refs=opmap[v]
 aug_family.append({'attrs_offset':v,'object':obj,'referenced_by':refs})
report={'mode':'static_end_to_end','source':{'version':ver,'entries':n},'attrs_schema':schema,'attrs_object_targets':aug_family,'boundary':'values bound only through schema field names; no item-id semantics asserted beyond row keys'}
OUT.mkdir(parents=True,exist_ok=True)
p=OUT/'attrs_hurt_power_end_to_end_005.json';p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'report':str(p),'schema_field_23':schema['fields'][23],'schema_field_35':schema['fields'][35],'attrs_objects':len(aug_family),'summary':[{'attrs_offset':a['attrs_offset'],'values':{v['name']:v['value'] for v in a['object']['values']},'referenced_by':[{'key':r['key'],'field':r['field_name']} for r in a['referenced_by']]} for a in aug_family]},ensure_ascii=False,indent=1))
