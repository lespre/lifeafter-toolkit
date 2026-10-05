# -*- coding: utf-8 -*-
"""方向2：从 BinDict 配置表提取资源路径 -> path_id 变体。

Read-only on E:/mrzh + C盘历史副本。输出路径候选 + 各 NPK 条目表 file_id 集合。
"""
from __future__ import annotations
import importlib.util,json,re,struct
from pathlib import Path
OUT=Path(r'E:/提取成果/filename_restore_output')
NPK_READER=Path(r'E:/提取成果/明日之后拆包工具/01_核心解包器/npk_reader.py')
# 配置表副本（含资源路径字符串的 CHS 池）
COPY_ROOTS=[
 Path(r'C:/Users/<user>/AppData/Local/hermes/mrzh_weapon_skin_audit/run_002/体验服武器商品中文表扫描_001/命中原始载荷'),
 Path(r'C:/Users/<user>/AppData/Local/hermes/mrzh_weapon_skin_audit/run_002/体验服武器商品中文表扫描_002/命中原始载荷'),
 Path(r'E:/mrzh_audit/run_004_PC_BinDict与1DPW专项_001/02_bindict/attribute_data_PC静态副本_001'),
]
EXT_RE=re.compile(rb'[A-Za-z0-9_\-/\\\.]{4,}\.(?:png|jpg|jpeg|dds|fsb|mesh|atlas|json|mat|anim|tga|wav|ogg|mp3|mp4|sfx|prefab|txt|xml|bin|ani|skeleton|skel)(?=[^a-z]|$)',re.I)

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 paths=set()
 for root in COPY_ROOTS:
  if not root.is_dir():continue
  for p in root.rglob('*.bin'):
   if p.stat().st_size>20<<20:continue
   try:d=p.read_bytes()
   except:continue
   for m in EXT_RE.finditer(d):
    s=m.group().decode('latin1')
    # 去前后缀噪音（如前一个字段名粘连）
    s=re.sub(r'^[A-Za-z_]+',lambda mm:mm.group(0) if '/' in mm.group(0) or '\\' in mm.group(0) else '',s) if False else s
    paths.add(s)
 # 归一化变体
 variants=set()
 for s in paths:
  variants.add(s)
  variants.add(s.replace('/','\\'))
  variants.add(s.replace('\\','/'))
  # 去常见前缀（ui/ res/ common/ scene/ effect/ item_icon/ font_icon/ main_v4_icon/ capture_dist 拼接残留）
  for pre in ('ui/','ui\\','res/','res\\','common/','common\\','scene/','scene\\','effect/','effect\\','item_icon/','item_icon\\','font_icon/','font_icon\\','main_v4_icon/','main_v4_icon\\','capture_','2','201','MVP'):
   if s.startswith(pre):
    rest=s[len(pre):]
    variants.add(rest)
    variants.add(rest.replace('/','\\'))
    variants.add(rest.replace('\\','/'))
 print('raw paths',len(paths),'variants',len(variants))
 # 加载 npk_reader 的 aes（path_id 内联）
 spec=importlib.util.spec_from_file_location('npkr',NPK_READER)
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 def murmur3_x86_32(data, seed):
  c1,c2=0xCC9E2D51,0x1B873593
  h=seed&0xFFFFFFFF
  end=len(data)&~3
  for off in range(0,end,4):
   k=int.from_bytes(data[off:off+4],'little')
   k=(k*c1)&0xFFFFFFFF
   k=((k<<15)|(k>>17))&0xFFFFFFFF
   k=(k*c2)&0xFFFFFFFF
   h^=k
   h=((h<<13)|(h>>19))&0xFFFFFFFF
   h=(h*5+0xE6546B64)&0xFFFFFFFF
  tail=data[end:];k=0
  if len(tail)>=3:k^=tail[2]<<16
  if len(tail)>=2:k^=tail[1]<<8
  if tail:
   k^=tail[0]
   k=(k*c1)&0xFFFFFFFF
   k=((k<<15)|(k>>17))&0xFFFFFFFF
   k=(k*c2)&0xFFFFFFFF
   h^=k
  h^=len(data)
  h^=h>>16;h=(h*0x85EBCA6B)&0xFFFFFFFF
  h^=h>>13;h=(h*0xC2B2AE35)&0xFFFFFFFF
  h^=h>>16
  return h&0xFFFFFFFF
 def path_id(p):
  e=p.encode('utf-8')
  return (murmur3_x86_32(e,0x77777777)<<32)|murmur3_x86_32(e,0x66666666)
 # 读取各 NPK 条目表 file_id 集合
 pkgs={
  'script.py3':Path(r'E:/mrzh/Documents/script.py3.npk'),
  'script.py314':Path(r'E:/mrzh/Documents/script.py314.lc.npk'),
  'res':Path(r'E:/mrzh/res.npk'),
  'ui':Path(r'E:/mrzh/res/ui.npk'),
 }
 id_sets={}
 for name,p in pkgs.items():
  if not p.exists():print(name,'missing',p);continue
  with p.open('rb') as f:
   h=m.aes_ecb(f.read(32))
   _r,magic,ver,to,n=struct.unpack_from('<QIIII',h)
   if magic!=0x4b50584e:print(name,'bad magic',hex(magic));continue
   f.seek(to);tab=m.aes_ecb(f.read(n*48))
  ids={struct.unpack_from('<Q',tab,i*48)[0] for i in range(n)}
  id_sets[name]=ids
  print(name,'entries',n)
 # 匹配：每个路径变体计算 path_id，查命中
 matches=[]
 for s in sorted(variants):
  fid=path_id(s)
  hit=[n for n,ids in id_sets.items() if fid in ids]
  if hit:
   matches.append({'path':s,'file_id':f'{fid:016X}','pkgs':hit})
 print('matches',len(matches))
 for x in matches[:40]:print(x)
 (OUT/'resource_paths_extracted.json').write_text(json.dumps({'raw_paths':sorted(paths)[:5000],'variants':sorted(variants)[:8000]},ensure_ascii=False,indent=1)+'\n',encoding='utf-8')
 (OUT/'resource_path_matches.json').write_text(json.dumps(matches,ensure_ascii=False,indent=1)+'\n',encoding='utf-8')
 print('saved to',OUT)
if __name__=='__main__':
 main()
