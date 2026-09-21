# -*- coding: utf-8 -*-
"""Final KJ1 transfer-consume decode: 11 recipes -> 6 shared configs, full field values.

Static read of the previously extracted KJ1 pair + common_item occurrence check.
"""
from __future__ import annotations
import json,struct
from pathlib import Path
D=Path(r'C:/Users/Administrator/AppData/Local/hermes/mrzh_weapon_skin_audit/run_002/重构转印器核查_001/当前py314_转印消耗主题配置_原始副本_002')
OUT=Path(r'E:/mrzh_audit/run_004_PC_BinDict与1DPW专项_001/02_bindict/KJ1转印消耗解码_006')
base=next(f for f in D.iterdir() if 'kj1_' in f.name and 'chs' not in f.name)
raw=base.read_bytes();q=raw.find(b'x{');ln=struct.unpack_from('<I',raw,q+2)[0];body=raw[q+6:q+6+ln]
def uleb(d,p,e):
 v=0;s=0
 for _ in range(10):
  if p>=e:return None,p
  b=d[p];p+=1;v|=(b&127)<<s
  if not b&128:return v,p
  s+=7
 return None,p
# rows: 96 32 segments with 6 ULEB head + 27 groups
segs=[96,130,169,218,247,281];idx76=293
head_rows=[]
for si in range(len(segs)):
 st=segs[si];end=segs[si+1] if si+1<len(segs) else idx76
 p=st+2;head=[]
 for _ in range(6):
  v,p=uleb(body,p,end);head.append(v)
 groups=[]
 while p<end:
  if body[p]!=0x27:raise ValueError(f'non-group at {p}')
  kind=body[p+1];cnt=body[p+2];els=[];p+=3
  for _ in range(cnt):
   v,p=uleb(body,p,end);els.append(v)
  groups.append({'kind':kind,'count':cnt,'elements':els})
 head_rows.append({'row_index':si,'byte_offset':st,'head_ulebs':head,'groups':groups})
# recipe -> start map from index bucket at 395
keys_starts=[(75,98),(109,64),(114,137),(149,137),(154,137),(159,98),(164,98),(169,186),(198,215),(227,64),(232,249)]
start_to_row={64:None,98:0,137:2,186:3,215:4,249:5}
# row -1 (body[32..96]) holds default header row with 6 fields
p=32;head0=[]
for _ in range(6):
 v,p=uleb(body,p,96);head0.append(v)
recipes=[]
for key,start in keys_starts:
 row=start_to_row.get(start)
 r=head_rows[row] if row is not None else {'head_ulebs':head0,'groups':None}
 recipes.append({'recipe_key':key,'config_start':start,'row':row,'head':r['head_ulebs'],'groups':r['groups']})
report={'mode':'static_kj1_transfer_consume','field_names':['consume_items','consume_token_item_cnt','consume_token_item_id','lock_consume_item_cnt','lock_consume_items','transfer_consume_items'],'rows':head_rows,'recipes':recipes,'boundary':'kind=0x01 groups interpreted as (item_id,count) pairs of consume_items; kind=0x0b groups are transfer references, operand semantics unbound; head ULEB #2/#3/#4 bound to token cnt/id and lock cnt by field order and cross-row consistency'}
OUT.mkdir(parents=True,exist_ok=True)
p=OUT/'kj1_transfer_consume_full_006.json';p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'report':str(p),'recipes':[{'key':r['recipe_key'],'start':r['config_start'],'consume_token_item_cnt':r['head'][1],'consume_token_item_id':r['head'][2],'lock_consume_item_cnt':r['head'][3],'consume_items_pairs':[g['elements'] for g in r['groups'] if g['kind']==1] if r['groups'] else None,'transfer_groups':[g['elements'] for g in r['groups'] if g['kind']==11] if r['groups'] else None} for r in recipes]},ensure_ascii=False,indent=1))
