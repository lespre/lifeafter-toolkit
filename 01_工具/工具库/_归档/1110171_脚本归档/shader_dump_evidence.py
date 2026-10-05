# -*- coding: utf-8 -*-
"""shader_dump_evidence.py — 从 shader_gl_compile_probe.json 提取决定性最小证据（只读）。"""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, 'shader_gl_compile_probe.json'), encoding='utf-8'))
gl = d.get('gl')
gl = json.loads(gl) if isinstance(gl, str) else (gl or {})
lc = json.loads(d.get('ladderCompile') or '{}')

print('=== 1. renderer.debug 与 program 统计 ===')
print('checkShaderErrors =', lc.get('checkShaderErrors'), '| EXT_shader_texture_lod =', lc.get('extension_shader_texture_lod'))
progs = lc.get('programs') or []
bad = [q for q in progs if q.get('fragment_compile') is False or q.get('program_link') is False]
print('program 总数 =', len(progs), '| 失败 =', len(bad),
      '| 失败 cacheKey =', [str(q.get('cacheKey'))[:70] for q in bad])
print('GL 侧统计 (lab 链跑完):', d.get('gl_len_after_chain'))
print('GL 侧统计 (ladder 后):', d.get('gl_after_ladder'))

print()
print('=== 2. 失败片元着色器完整 info log（第 1 个失败 program） ===')
if bad:
    print(bad[0].get('fragment_info_log'))
    print('program_info_log =', repr(bad[0].get('program_info_log')))

print()
print('=== 3. 编译失败的 shader 源码片段（GL 侧 shaderSource 抓取的最终串，含 three 前缀） ===')
hits = 0
for s in reversed(gl.get('sources') or []):
    tail = s.get('tail') or ''
    if '__rough' in tail and s.get('ok') is False:
        hits += 1
        print('--- source n=%s len=%s ok=%s ---' % (s.get('n'), s.get('len'), s.get('ok')))
        idx = tail.find('__rough')
        print(tail[max(0, idx - 700): idx + 1400])
        break
print('匹配到的失败源码数:', hits)

print()
print('=== 4. 注入语句中使用的双下划线标识符（GLSL ES 3.00 保留） ===')
srcs = [s for s in (gl.get('sources') or []) if '__rough' in (s.get('tail') or '')]
if srcs:
    tail = srcs[-1]['tail']
    ids = sorted(set(re.findall(r'\b__[A-Za-z0-9_]+\b', tail)))
    print('倒数第 1 个含注入的源码中出现的 __ 标识符:', ids)
print('viewer.js L938-948 注入体内标识符: __rough __lod __R __c __s2 __Rr __sm __L __Lc __env')

print()
print('=== 5. 关键 uniform 是否在 shader 里声明 ===')
for name in ('uCustomIbl', 'uIblRot', 'uIblMix', 'uIblScale', 'uIblStrength', 'uSrcIbl'):
    decl = 0
    use = 0
    for s in (gl.get('sources') or []):
        t = s.get('tail') or ''
        decl += len(re.findall(r'uniform\s+\w+\s+' + name + r'\s*;', t))
        use += len(re.findall(r'\b' + name + r'\b', t))
    print('  %-14s 声明次数=%d  出现次数=%d' % (name, decl, use))

print()
print('=== 6. 锚点注入是否生效（#include <dithering_fragment> 是否真的被替换） ===')
for s in (gl.get('sources') or []):
    t = s.get('tail') or ''
    if 'dithering_fragment' in t or 'DITHERING' in t:
        i = t.find('__rough')
        if i >= 0:
            seg = t[i: i + 900]
            print('  注入体后是否仍有未解析的 #include:', '#include <' in seg)
            print('  DITHERING chunk 是否在注入体之后:', 'dithering' in seg.lower())
            break

print()
print('=== 7. viewer 可见性/置换状态 ===')
print('snapshot:', d.get('snapshot'))
print('ladderL1 red :', str(d.get('ladderL1_red'))[:200])
print('ladderL1 green:', str(d.get('ladderL1_green'))[:200])
print('gl.useInvalid =', gl.get('useInvalid'))
print('exceptions =', gl.get('exceptions'))
