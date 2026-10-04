# -*- coding: utf-8 -*-
'''task-79 A/B 只读取证：1110171 28 个 Model 的现状 vs 源 bin 的真实声明'''
import io, os, re, sys, json, struct, hashlib
sys.stdout.reconfigure(encoding='utf-8')
B = r'E:\la拆包项目\08Lifeafter wiki\assets\3d\weapon_skin\1110171'
E = os.path.join(B, 'effects.json')
BIN = r'E:\la拆包项目\03拆包产物\render_1003_010\_sfx_010\gpk_effect_01_f74635_59115620b779a5e8.bin'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171\MODEL171_probe.json'
TAGS = ('Dummy', 'Model', 'ParticleSystem', 'ParticleRes', 'Sprite', 'Trail')
eff = json.loads(open(E, 'rb').read().decode('utf-8'))
MD = [n for n in eff['nodes'] if n.get('tag') == 'Model']
txt = io.open(BIN, 'rb').read().decode('gbk', 'replace')
SRC = {}
for m in re.finditer(r'<(%s)\b([^>]*)>' % '|'.join(TAGS), txt):
    at, tag = m.group(2), m.group(1)
    nxt = re.search(r'<(?:%s)\b' % '|'.join(TAGS), txt[m.end():])
    blk = txt[m.end():(m.end() + nxt.start()) if nxt else (m.end() + 60000)]
    a = dict(re.findall(r'(\w+)\s*=\s*"([^"]*)"', at))
    if a.get('Name'):
        uni = sorted(set(re.findall(r'<(u_[A-Za-z0-9_]+)\b', blk)))
        SRC[a['Name']] = {'tag': tag, 'attrs': a, 'uniforms': uni, 'blk_len': len(blk),
                          'sem': sorted(set(re.findall(r'<Semantic\s+Name\s*=\s*"([^"]+)"', blk)))}
print('源 bin：%d 节点（%s）' % (len(SRC), json.dumps({t: sum(1 for v in SRC.values() if v['tag'] == t) for t in TAGS if any(v['tag'] == t for v in SRC.values())}, ensure_ascii=False)))
CRIT = ('u_emissivecolor', 'u_emissive_color', 'u_diffuse_color', 'u_main_color', 'u_base_color',
        'u_overall_opacity', 'u_emissive_highlight_intensity', 'u_emissive_intensity')
rows = []
for n in MD:
    mf = n.get('model_fields') or {}
    ut = mf.get('uniform_tracks') or {}
    cls = 'A' if ('u_emissivecolor_Keyframe' in ut or 'u_emissive_color_Keyframe' in ut) else ('B' if 'u_diffuse_color_Keyframe' in ut else 'C')
    s = SRC.get(n.get('name'))
    rows.append({'node': n.get('name'), 'cls_now': cls,
                 'has_uniform_tracks': bool(ut), 'ut': sorted(ut.keys()),
                 'start': n.get('start'), 'life': n.get('life'),
                 'fxStartTime_mf': mf.get('fx_start_time'), 'fxLifeSpan_mf': mf.get('fx_life_span'),
                 'color_track_len': len(n.get('color_track') or []), 'scale_track_len': len(n.get('scale_track') or []),
                 'render_bias': n.get('render_bias') or mf.get('render_bias'),
                 'transparent_mode': n.get('transparent_mode') or mf.get('transparent_mode'),
                 'fxIgnore': n.get('fxIgnore'), 'model_glb': n.get('model_glb'),
                 'src_found': bool(s), 'src_uniforms': (s or {}).get('uniforms', []),
                 'src_colors': [u for u in (s or {}).get('uniforms', []) if any(c in u for c in CRIT)],
                 'src_FxIgnore': (s or {}).get('attrs', {}).get('FxIgnore'),
                 'src_fxStart': (s or {}).get('attrs', {}).get('FxStartTime'), 'src_fxLife': (s or {}).get('attrs', {}).get('FxLifeSpan')})
from collections import Counter
print('现状分类（effects.json）：', json.dumps(dict(Counter(r['cls_now'] for r in rows)), ensure_ascii=False))
print('源侧有颜色 uniform 的节点数:', sum(1 for r in rows if r['src_colors']))
print('effects.json 里带 uniform_tracks 的 Model:', sum(1 for r in rows if r['has_uniform_tracks']))
print()
print('%-20s %-4s %-6s %-5s %-5s %-7s %-6s %s' % ('node', 'cls', 'u_track', 'start', 'life', 'fxIgn', 'glb', 'src_colors'))
for r in rows:
    print('%-20s %-4s %-6s %-5s %-5s %-7s %-6s %s' % (
        r['node'], r['cls_now'], 'Y' if r['has_uniform_tracks'] else '-', str(r['start'])[:5], str(r['life'])[:5],
        str(r['fxIgnore'])[:6], 'Y' if r['model_glb'] else '-', json.dumps(r['src_colors'], ensure_ascii=False)[:60]))
# 3 个 ok（= 有颜色且非 ignored）
okc = [r for r in rows if r['cls_now'] in 'AB' and not r['fxIgnore']]
print()
print('=== 非 C 且非 ignored 的节点（推测 3 个 ok）: %s' % json.dumps([r['node'] for r in okc], ensure_ascii=False))
def glb_mm(p):
    b = open(p, 'rb').read(); off = 12; js = None
    while off < len(b):
        clen, ctype = struct.unpack('<II', b[off:off + 8])
        if ctype == 0x4E4F534A:
            js = json.loads(b[off + 8:off + 8 + clen].decode('utf-8')); break
        off += 8 + clen
    if not js:
        return None
    lo = [1e9] * 3; hi = [-1e9] * 3
    for a in js.get('accessors', []):
        if a.get('type') == 'VEC3' and a.get('min') and a.get('max'):
            for i in range(3):
                lo[i] = min(lo[i], a['min'][i]); hi[i] = max(hi[i], a['max'][i])
    return {'min': [round(x, 3) for x in lo], 'max': [round(x, 3) for x in hi], 'size': [round(hi[i] - lo[i], 3) for i in range(3)]}
for r in okc:
    if r['model_glb']:
        p = os.path.join(B, r['model_glb'].replace('/', os.sep))
        print('  %s  GLB(%s) = %s' % (r['node'], r['model_glb'], json.dumps(glb_mm(p) if os.path.isfile(p) else 'MISSING', ensure_ascii=False)))
json.dump({'rows': rows, 'src_node_count': len(SRC),
           'verdict_counts': {'cls_now': dict(Counter(r['cls_now'] for r in rows)),
                              'src_has_colors': sum(1 for r in rows if r['src_colors']),
                              'has_uniform_tracks': sum(1 for r in rows if r['has_uniform_tracks'])}},
          io.open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('探针 JSON ->', OUT, os.path.getsize(OUT), 'B')
