# -*- coding: utf-8 -*-
"""ENV_IBL_probe3.py — 只读：① 1110171/1110177 逐 prim 的 c159 材质参数键（含 u_rotate_angle/u_cube_brightness）
   ② 对 003996.c159 的 3.09/0.71/2.60/2.74 做原始字节 float32 复核 ③ 001265/001223 中同名参数是否存在。
   输出 ENV_IBL_probe3.txt"""
import io, json, os, struct, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
R = r'E:\la拆包项目\03拆包产物'
OUT = os.path.join(R, '_target_1110171')
WEAPON = os.path.join(R, 'weapon')
lines = []
res = {}

# ① 逐 prim 参数键
for f, label in (('c159_pair_v4_001265.json', '1110171 dual(001265)'),
                 ('c159_pair_v4_regress.json', '多文件回归（含 001265/001223/003996）')):
    p = os.path.join(R, f)
    if not os.path.isfile(p):
        continue
    d = json.load(open(p, encoding='utf-8'))
    nodes = d.get('primitives') if isinstance(d.get('primitives'), list) else d.get('regression')
    lines.append('#### %s (%s)' % (label, f))
    for ni, node in enumerate(nodes if isinstance(nodes, list) else [nodes]):
        prims = node.get('primitives') if isinstance(node, dict) else None
        if prims is None:
            continue
        fname = node.get('file') if isinstance(node, dict) else None
        lines.append('  node[%d] file=%s blocks=%s' % (ni, fname, json.dumps(node.get('blocks'), ensure_ascii=False)[:200]))
        for pr in prims:
            keys = sorted((pr.get('params') or {}).keys())
            hot = {k: (pr.get('params') or {})[k] for k in keys if k in ('u_rotate_angle', 'u_cube_brightness')}
            lines.append('    prim%-2s %-18s block_off=%-6s n_params=%-3s hot=%s' % (
                pr.get('prim'), pr.get('material'), pr.get('block_off'), len(keys), json.dumps(hot, ensure_ascii=False)))
            if f.endswith('001265.json'):
                lines.append('         keys=%s' % ','.join(keys))

# ③ 原始 c159：参数名 + float32 复核
def scan(fname):
    p = os.path.join(WEAPON, fname)
    if not os.path.isfile(p):
        return {'error': 'missing'}
    raw = open(p, 'rb').read()
    out = {'bytes': len(raw)}
    for tok in (b'u_rotate_angle', b'u_cube_brightness', b'u_lightmap_factor', b'u_env_day2night_exposure'):
        offs = []
        st = 0
        while True:
            k = raw.find(tok, st)
            if k < 0:
                break
            offs.append(k)
            st = k + 1
        out[tok.decode()] = offs
    # 目标 float 值出现在哪些偏移
    for v in (3.09, 0.71, 2.6, 2.74):
        b4 = struct.pack('<f', v)
        offs = []
        st = 0
        while True:
            k = raw.find(b4, st)
            if k < 0:
                break
            offs.append(k)
            st = k + 1
        out['float_le_%s' % v] = offs
    return out


res['raw_scan'] = {f: scan(f) for f in ('001265.c159', '001223.c159', '003996.c159')}
lines.append('')
lines.append('#### 原始 c159 扫描（参数名 / 目标 float32 出现位置）')
for f, o in res['raw_scan'].items():
    lines.append('  %s bytes=%s' % (f, o.get('bytes')))
    for k, v in o.items():
        if k == 'bytes':
            continue
        lines.append('     %-28s %s' % (k, v))

# 003996：把回归 JSON 里 1110177 的成对值与其 raw 偏移对齐（若 JSON 提供 pairs）
p = os.path.join(R, 'c159_pair_v4_regress.json')
d = json.load(open(p, encoding='utf-8'))
node = d['regression'][2]
lines.append('')
lines.append('#### 1110177 节点全字段（键名）: %s' % list(node.keys()))
for pr in node['primitives']:
    lines.append('  prim%s mtl=%s block_off=%s keys=%s' % (pr.get('prim'), pr.get('material'), pr.get('block_off'),
                                                         list((pr.get('params') or {}).keys())))
    if pr.get('pairs'):
        lines.append('     pairs=%s' % json.dumps(pr['pairs'], ensure_ascii=False)[:600])
json.dump(res, open(os.path.join(OUT, 'ENV_IBL_probe3.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
open(os.path.join(OUT, 'ENV_IBL_probe3.txt'), 'w', encoding='utf-8').write('\n'.join(lines))
print('\n'.join(lines))
