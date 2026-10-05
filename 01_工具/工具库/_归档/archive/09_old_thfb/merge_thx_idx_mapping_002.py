# -*- coding: utf-8 -*-
"""P2 final merge: CSV hash map + THX attribution + un-matched hash IDX check.

Output: merged mapping table (hash | group | idx_index | payload_size | thx_file | in_idx).
Read-only on E:/mrzh.
"""
from __future__ import annotations
import csv,json
from pathlib import Path
OUT=Path(r'E:/提取成果/明日拆包/output/09_thfb')
CSV=Path(r'C:/Users/<user>/AppData/Local/hermes/mrzh_weapon_skin_audit/run_002/物理实体链路_001/THX与IDX原始Hash交叉引用.csv')
RES=Path(r'E:/mrzh/Documents/res')

def main():
 # 1) thx attribution: hash -> in any thx extract
 thx_all=set((OUT/'thx_hashes_all.txt').read_text().split())
 # 2) csv rows + attribution + idx check
 idx_cache={}
 for p in RES.glob('*.idx'):
  idx_cache[p.name]=p.read_bytes()
 rows=[];matched_thx=0;in_idx=0
 with CSV.open(encoding='utf-8-sig') as f:
  for row in csv.DictReader(f):
   h=row.get('resource_hash','').strip()
   if len(h)!=32:continue
   g=row.get('group','');ii=row.get('idx_index','');ps=row.get('idx_payload_size','')
   thx_hit = 'yes' if h in thx_all else ''
   b=bytes.fromhex(h)
   idx_hit=[n for n,d in idx_cache.items() if b in d]
   if thx_hit:matched_thx+=1
   if idx_hit:in_idx+=1
   rows.append({'hash':h,'group':g,'idx_index':ii,'payload_size':ps,
                'in_thx':thx_hit,'in_idx':';'.join(idx_hit)})
 out_csv=OUT/'thx_idx_mapping_final.csv'
 with out_csv.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=['hash','group','idx_index','payload_size','in_thx','in_idx'])
  w.writeheader();w.writerows(rows)
 unmatched=[r for r in rows if not r['in_thx'] and not r['in_idx']]
 print(json.dumps({'csv_rows':len(rows),'matched_thx':matched_thx,'in_idx':in_idx,
                   'unmatched_both':len(unmatched),
                   'unmatched_sample':unmatched[:5]},ensure_ascii=False,indent=1))
 (OUT/'thx_idx_mapping_final.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':
 main()
