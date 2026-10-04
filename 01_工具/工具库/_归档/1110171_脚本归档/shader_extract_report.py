# -*- coding: utf-8 -*-
"""shader_extract_report.py — 读取 shader_gl_compile_probe.json，只打印关键字段（只读）。"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, 'shader_gl_compile_probe.json'), encoding='utf-8'))
print('KEYS:', list(d.keys()))
print('gl_len_after_chain:', d.get('gl_len_after_chain'))
print('gl_after_ladder:', d.get('gl_after_ladder'))
print('snapshot:', d.get('snapshot'))
print('ladderL1_red:', d.get('ladderL1_red'))
print('ladderL1_green:', d.get('ladderL1_green'))
print('ladderCompile keys:')
try:
    lc = json.loads(d.get('ladderCompile') or '{}')
    print('  checkShaderErrors:', lc.get('checkShaderErrors'),
          ' ext_shader_texture_lod:', lc.get('extension_shader_texture_lod'),
          ' program_count:', lc.get('program_count'))
    for q in lc.get('programs') or []:
        print('  prog[%s] key=%s' % (q.get('index'), str(q.get('cacheKey'))[:60]))
        print('      vs_compile=%s fs_compile=%s link=%s' % (q.get('vertex_compile'), q.get('fragment_compile'), q.get('program_link')))
        for f in ('vertex_info_log', 'fragment_info_log', 'program_info_log'):
            v = (q.get(f) or '').strip()
            if v:
                print('      %s: %s' % (f, v[:1200].replace('\n', '\n        ')))
except Exception as e:
    print('  parse fail:', e, str(d.get('ladderCompile'))[:800])
gl = d.get('gl') or {}
print('--- GL compile fails:', len(gl.get('fails') or []))
for f in (gl.get('fails') or []):
    print('  kind:', f.get('kind'))
    print('  log:', (f.get('log') or '')[:2500])
print('--- GL link fails:', len(gl.get('linkFails') or []))
for f in (gl.get('linkFails') or []):
    print('  proglog:', (f.get('prog') or '')[:600])
    for i, s in enumerate(f.get('shaders') or []):
        print('   shader[%d]: %s' % (i, (s or '')[:2500]))
print('--- useInvalid:', gl.get('useInvalid'))
print('--- exceptions:', gl.get('exceptions'))
print('--- sources summary:')
for s in (gl.get('sources') or []):
    print('   n=%s len=%s ok=%s ver300=%s' % (s.get('n'), s.get('len'), s.get('ok'), s.get('has_ver300')))
print('--- filtered logs:')
for L in (gl.get('logs') or []):
    low = L.lower()
    if any(k in low for k in ['shader', 'error', 'program', 'invalid', 'three', 'gl_', 'log2', 'layout']):
        print('  |', L[:500])
