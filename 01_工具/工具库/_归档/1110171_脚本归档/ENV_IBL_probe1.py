# -*- coding: utf-8 -*-
"""ENV_IBL_probe1.py — 只读：① c159 逐块 t_custom_ibl 声明（含原始字节位次）② 1110171/1110177 src_cube 素材清单
   ③ cube_faces_mips.json / view_*_mips.png 结构。输出 ENV_IBL_probe1.txt"""
import io, json, os, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
W = r'E:\la拆包项目\08Lifeafter wiki\assets\3d\weapon_skin'
R = r'E:\la拆包项目\03拆包产物'
OUT = os.path.join(R, '_target_1110171')
C159DIRS = [os.path.join(R, 'weapon'), R]
lines = []

# ① c159 行（C159PARSE_skins_fixed.json 有 off）
fixed = json.load(open(os.path.join(OUT, 'C159PARSE_skins_fixed.json'), encoding='utf-8'))
for key in ('1110171_dual', '1110171_single', '1110177'):
    s = fixed.get(key, {})
    rows = s.get('rows', [])
    lines.append('#### c159 %s file=%s rows=%d' % (key, s.get('file'), len(rows)))
    for r in rows:
        if r.get('slot_class') == 't_custom_ibl':
            lines.append('   blk%-2s t_custom_ibl ref=%-28s off=%s dual=%s order_only=%s' % (
                r.get('material_block'), r.get('ref'), r.get('off'), r.get('dual_proof'), r.get('agree_by_order_only')))
    blocks = sorted({r.get('material_block') for r in rows})
    lines.append('   全部块: %s' % blocks)
    # 每块槽清单（只看 Tex0/t_basecolor/t_custom_ibl）
    for b in blocks:
        sl = {r.get('slot_class'): r.get('ref') for r in rows if r.get('material_block') == b}
        lines.append('   blk%s Tex0=%s t_basecolor=%s ibl=%s' % (
            b, sl.get('Tex0'), sl.get('t_basecolor'), sl.get('t_custom_ibl')))

# ② 原始 c159 字节扫描（cube 名 + 相关 uniform 名）
for fname in ('001265.c159', '001223.c159', '003996.c159'):
    p = next((os.path.join(d, fname) for d in C159DIRS if os.path.isfile(os.path.join(d, fname))), None)
    lines.append('')
    lines.append('#### 原始 %s → %s' % (fname, p))
    if not p:
        lines.append('   未找到')
        continue
    raw = open(p, 'rb').read()
    for tok in (b'qiangpi.cube', b'fashion_qiangpi.cube', b'car_studio01.cube', b'crystal_reflection_uvva',
                b'crystal_bump', b'u_cube_brightness', b'u_ibl', b'u_reflection', b'cube'):
        offs = []
        st = 0
        while True:
            k = raw.find(tok, st)
            if k < 0:
                break
            offs.append(k)
            st = k + 1
        if offs:
            lines.append('   %-26s count=%-3d offsets=%s' % (tok.decode('latin1'), len(offs), offs[:16]))

# ③ 皮肤目录素材
for skin in ('1110171', '1110177'):
    d = os.path.join(W, skin, 'src_cube')
    lines.append('')
    lines.append('#### %s/src_cube 清单' % skin)
    if not os.path.isdir(d):
        lines.append('   目录不存在')
        continue
    for root, dirs, fs in os.walk(d):
        for f in sorted(fs):
            p = os.path.join(root, f)
            lines.append('   %-58s %10d B' % (os.path.relpath(p, os.path.join(W, skin)), os.path.getsize(p)))
    # 顶层皮肤目录非 src_cube 里与 cube/mips 有关的文件
    dd = os.path.join(W, skin)
    for f in sorted(os.listdir(dd)):
        if any(k in f.lower() for k in ('mip', 'cube', 'ibl')):
            lines.append('   [skin根] %-52s %10d B' % (f, os.path.getsize(os.path.join(dd, f))))

# ④ cube_faces_mips.json / view_*_mips.png 结构
for skin in ('1110171', '1110177'):
    for cand in ('src_cube/cube_faces_mips.json', 'cube_faces_mips.json', 'src_cube/cube_mips.json'):
        p = os.path.join(W, skin, cand)
        if os.path.isfile(p):
            try:
                j = json.load(open(p, encoding='utf-8'))
                lines.append('')
                lines.append('#### %s/%s 结构: %s' % (skin, cand, json.dumps(j, ensure_ascii=False)[:2400]))
            except Exception as e:
                lines.append('#### %s/%s 解析失败 %s' % (skin, cand, e))

json.dump({'lines': lines}, open(os.path.join(OUT, 'ENV_IBL_probe1.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
open(os.path.join(OUT, 'ENV_IBL_probe1.txt'), 'w', encoding='utf-8').write('\n'.join(lines))
print('\n'.join(lines))
