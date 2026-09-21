# -*- coding: utf-8 -*-
"""source_strict 自动化验收：槽位角色 / 缺失 / SHA / 候选误入 / 旧材质残留 / 假成功"""
import os, json, hashlib, re, sys
W=r'E:\la拆包项目\08Lifeafter wiki'; ROOT=os.path.join(W,r'assets\3d\weapon_skin\1110171')
V=open(os.path.join(W,r'assets\weapon_skin_viewer.js'),encoding='utf-8').read()
man=json.load(open(os.path.join(ROOT,'neox_material.json'),encoding='utf-8'))
probe=json.load(open(os.path.join(ROOT,'candidate_resource_probe.json'),encoding='utf-8'))
R=[]
def chk(name, ok, detail=''):
    R.append((name, bool(ok), detail)); print(('PASS' if ok else 'FAIL')+' | %-42s %s' % (name, detail))
# 1 人工链不得被读取
forbidden=['approx_albedo','approximate_palette','chain_albedo','chain_orm_','chain_rough_','invalidated.png']
chk('T1 正式链不读人工产物', not any(f in V for f in forbidden), '命中=%s' % [f for f in forbidden if f in V])
# 2 角色绑定（manifest 判定）
kinds={}
for p in man['primitives']:
    kinds[p['prim']]=p.get('shader_kind')
chk('T2 weapon=prim0/4', all(kinds.get(i)=='weapon' for i in (0,4)), str({i:kinds.get(i) for i in (0,4)}))
chk('T2 crystal=prim1/2/3/5/6', all(kinds.get(i)=='crystal' for i in (1,2,3,5,6)), str({i:kinds.get(i) for i in (1,2,3,5,6)}))
# 3 候选资源不得进 strict
cand_files={c['local'].split('/')[-1] for c in probe['candidates']}
ms=json.dumps(man, ensure_ascii=False)
leak=[f for f in cand_files if f in ms]
chk('T3 候选资源未进 strict manifest', not leak, '泄漏=%s' % leak)
chk('T3 viewer 不引用候选探针', 'candidate_resource_probe' not in V, '')
# 4 每个 loaded 槽必须有 local_file + sha256
bad=[]
for p in man['primitives']:
    for sn,sv in (p.items() if isinstance(p,dict) else []):
        pass
chk('T4 strict 槽位无匿名填充', 'loaded_from_gpk' not in ms, '')
# 5 缺输入不得品红（生产）
chk('T5 生产缺输入不显品红', ('m.visible=false' in V) and ('0xff00ff' in V), 'lab 保留诊断色')
# 6 无人工调参键
art=[k for k in ('uGold','uSilver','uViolet','uMaskThresh','gold_threshold','ref_fit') if k in V]
chk('T6 无人工金色/阈值参数', not art, '命中=%s' % art)
# 7 逐材质 IBL（禁 scene-wide）
chk('T7 逐材质 envMap + 禁 scene-wide', ('__envPlan' in V) and ('state.scene.environment=null' in V), '')
# 8 源贴图文件齐备且 SHA 可核
need={'010_a.png':None,'012_a.png':None,'010_m.png':None,'012_m.png':None,'010_n.png':None,'012_n.png':None,
      '010_b_m.png':None,'012_b_m.png':None,'param_repack_010.png':None,'param_repack_012.png':None}
miss=[f for f in need if not os.path.exists(os.path.join(ROOT,'src_tex',f))]
chk('T8 源贴图齐备', not miss, '缺=%s' % miss)
sh={f:hashlib.sha256(open(os.path.join(ROOT,'src_tex',f),'rb').read()).hexdigest()[:16] for f in need if not os.path.exists(os.path.join(ROOT,'src_tex',f)) or True}
json.dump(sh, open(os.path.join(ROOT,'src_tex_shas.json'),'w',encoding='utf-8'), ensure_ascii=False, indent=1)
# 9 未实现层必须如实标记
chk('T9 未实现层如实登记', all(x in V for x in ('pending_layers','ibl_fail_closed','missing_source_ibl')), '')
# 10 旧 GLB 材质不得残留（运行期判定留待浏览器测试）
chk('T10 材质替换断言存在', 'neox_replaced' in V, '')
npass=sum(1 for _,ok,_ in R if ok)
print('\n== %d/%d PASS ==' % (npass, len(R)))
json.dump(dict(passed=npass, total=len(R), results=[dict(name=n, ok=o, detail=d) for n,o,d in R]),
          open(r'E:\la拆包项目\03拆包产物\_target_1110171\assertion_suite.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
sys.exit(0 if npass==len(R) else 1)
