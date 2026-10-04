# -*- coding: utf-8 -*-
"""T5：合并验收数据 → 打印槽位绑定状态表（lab + prod）。"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))


def rows(src, tag):
    nx = json.loads(src)
    rep = nx.get('report') or {}
    print('=' * 24, tag, '=' * 24)
    print('applied=%s applied_prims=%s failed=%s missing=%s'
          % (rep.get('applied'), rep.get('applied_prims'), rep.get('failed'), rep.get('missing')))
    print('%-5s %-24s %-8s %-16s %-24s %-10s %s' % ('prim', 'material', 'status', 'slot', 'local_file', 'color', 'logical_path'))
    for pr in rep.get('prims', []):
        for slot, v in (pr.get('slots') or {}).items():
            print('%-5s %-24s %-8s %-16s %-24s %-10s %s'
                  % (pr.get('prim'), pr.get('material'), pr.get('status'), slot,
                     v.get('file') or '-MISSING-', v.get('color_space'), (v.get('logical') or '')))
    print()


p = os.path.join(HERE, '_t5_lab_neox.json')
if os.path.exists(p):
    rows(open(p, encoding='utf-8').read(), 'lab=1')
acc = json.load(open(os.path.join(HERE, '_t5_accept.json'), encoding='utf-8'))
for r in acc:
    if r.get('tag') == 'prod':
        rows(r.get('neox'), 'prod (无 lab)')
        print('screenshot:', r.get('screenshot'))
        print('gl:', r.get('gl'))
