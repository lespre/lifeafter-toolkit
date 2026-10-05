# -*- coding: utf-8 -*-
"""Q2_blend_analysis.py — 用 36,008 份 .sfx 统计 `BlendMode` 的取值分布与共现（**只报分布，不用分布反推名字**）。"""
import io, json, os, sys
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171\fidelity'
corpus = json.load(io.open(os.path.join(OUT, 'Q3_corpus.json'), encoding='utf-8'))

bm = Counter()
bm_tags = Counter()
joint_is = Counter()
joint_tm = Counter()
tag_of = Counter()
per_value_tags = {}
value_nodes = {}
for doc in corpus['sfx_docs']:
    for n in doc['nodes']:
        v = n.get('BlendMode')
        if v is None:
            continue
        bm[v] += 1
        tag = n.get('_tag')
        bm_tags[(v, tag)] += 1
        joint_is[(v, n.get('IsSprBlend'))] += 1
        joint_tm[(v, n.get('TransparentMode'))] += 1
        per_value_tags.setdefault(v, Counter())[tag] += 1
        value_nodes.setdefault(v, []).append({'name': n.get('Name'), 'tag': tag, 'tex': (n.get('Texture') or '')[-40:],
                                              'container': doc['container'], 'row': doc['row'],
                                              'IsSprBlend': n.get('IsSprBlend'), 'TransparentMode': n.get('TransparentMode'),
                                              'FxIgnore': n.get('FxIgnore')})
print('=== BlendMode 取值分布（来自 %d 份 sfx 文档）===' % len(corpus['sfx_docs']))
print('   ', json.dumps(dict(bm.most_common()), ensure_ascii=False))
print('=== 每个取值下的节点 tag 分布（前 6）===')
for v, c in bm.most_common(10):
    print('   BlendMode=%-3s n=%-6d %s' % (v, c, json.dumps(dict(per_value_tags[v].most_common(6)), ensure_ascii=False)))
print('=== BlendMode × IsSprBlend ===')
print('   ', json.dumps({str(k): v for k, v in joint_is.most_common(20)}, ensure_ascii=False))
print('=== BlendMode × TransparentMode ===')
print('   ', json.dumps({str(k): v for k, v in joint_tm.most_common(20)}, ensure_ascii=False))
print('\n=== BlendMode=7 的全部实例（含容器/row/纹理）===')
for x in value_nodes.get('7', [])[:30]:
    print('   ', json.dumps(x, ensure_ascii=False))
print('   合计 %d 个' % len(value_nodes.get('7', [])))
# 是否存在"非数字"取值（即名字直证）
nonnum = [v for v in bm if not str(v).lstrip('-').isdigit() and v != '']
print('\n是否存在非数字 BlendMode 取值（若有即为名字直证）: %s' % (nonnum or '无——全部为整数'))
json.dump({'blendmode_dist': dict(bm.most_common()), 'joint_issprblend': {str(k): v for k, v in joint_is.most_common()},
           'joint_transparentmode': {str(k): v for k, v in joint_tm.most_common()},
           'per_value_tags': {k: dict(v.most_common()) for k, v in per_value_tags.items()},
           'value7_examples': value_nodes.get('7', [])[:50], 'value7_total': len(value_nodes.get('7', [])),
           'nonnumeric_values': nonnum},
          io.open(os.path.join(OUT, 'Q2_blend_analysis.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('-> Q2_blend_analysis.json')
