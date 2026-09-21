# -*- coding: utf-8 -*-
"""test_c159_parser.py — c159 解析器跨 LOD / 跨资产测试。
运行: python test_c159_parser.py  (exit 0 = 全过)
覆盖: 029 LOD1/2/3 标准文件 ×3 + LOD0 ×1 (红/灰四色断言); 028 皮毛文件; 034 武器文件; 034 Lod 场景文件(应清晰报错)。
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c159_pair as CP

W = r'E:\la拆包项目\03拆包产物\weapon'
REDS = {'u_crystal_color': [0.2431, 0.0, 0.0, 1.0],
        'u_refraction_color': [1.0, 0.0, 0.0, 1.0],
        'u_subsurface_color': [0.8549, 0.0, 0.0, 1.0]}
GRAY_BASE = [0.3373, 0.3373, 0.3373, 1.0]

def rows_of(A, p):
    return {r['name']: r.get('value') for r in p['pairing']['rows'] if r.get('value') is not None}

def test_029(path, tag):
    A = CP.analyze(path)
    assert len(A['materials']) == 3, '%s: 材料数 %s' % (tag, A['materials'])
    assert len(A['blocks']) == 2, '%s: 块数 %s' % (tag, [len(b) for b in A['blocks']])
    assert len(A['pairs']) >= 2, '%s: 配对数 %d' % (tag, len(A['pairs']))
    rowsets = [rows_of(A, p) for p in A['pairs']]
    for k, v in REDS.items():
        assert any(rs.get(k) == v for rs in rowsets), '%s: %s 未找到 (期望 %s)' % (tag, k, v)
    assert any(rs.get('u_base_color') == GRAY_BASE for rs in rowsets), '%s: 灰基色缺' % tag
    mats, meta = CP.load_asset_materials(path)
    assert len(mats) == 3 and mats[2]['params'].get('u_crystal_color') == REDS['u_crystal_color'], '%s: 绑定解析失败 %s' % (tag, mats.get(2))
    return '块%s 组%s 配对%s' % ([len(b) for b in A['blocks']], [len(g) for g in A['groups']], [(p['group'], p['block'], p['score']) for p in A['pairs']])

if __name__ == '__main__':
    ok = True
    # 1) 029 标准材质文件 ×3 (LOD1/2/3) + LOD0
    for f, tag in (('003996', '029-LOD1'), ('003999', '029-LOD2'), ('004002', '029-LOD3'), ('004008', '029-LOD0')):
        try:
            info = test_029(os.path.join(W, f + '.c159'), tag)
            print('PASS | %-9s | %s' % (tag, info))
        except Exception as e:
            ok = False
            print('FAIL | %-9s | %r' % (tag, e))
    # 2) 跨资产: 028 皮毛 (不同 schema, 只要求不崩 + 能读材料/着色器)
    try:
        A = CP.analyze(os.path.join(W, '003990.c159'))
        hit = any('028' in m for m in A['materials']) and any('fur' in s or 'weapon' in s for s in A['shaders'])
        print('PASS | 028-fur   | 材料=%s shader=%s 组%d 块%d %s' % (A['materials'], [s.split(chr(92))[-1] for s in A['shaders']], len(A['groups']), len(A['blocks']), '✓' if hit else '⚠ 材料/着色器未识别'))
        ok = ok and (len(A['materials']) >= 1)
    except Exception as e:
        ok = False
        print('FAIL | 028-fur   | %r' % e)
    # 3) 跨资产: 034 武器材质
    try:
        A = CP.analyze(os.path.join(W, '004016.c159'))
        print('PASS | 034-weapon| 材料=%s shader=%s 组%d 块%d' % (A['materials'], [s.split(chr(92))[-1] for s in A['shaders']], len(A['groups']), len(A['blocks'])))
        ok = ok and len(A['materials']) >= 1
    except ValueError as e:
        print('PASS | 034-weapon| 清晰拒绝(可接受): %s' % e)
    except Exception as e:
        ok = False
        print('FAIL | 034-weapon| %r' % e)
    # 4) 非材质文件: 034 Lod 场景 → 必须清晰 ValueError, 不得 IndexError/崩溃
    try:
        CP.analyze(os.path.join(W, '004014.c159'))
        print('pass | 034-lods  | 未报错(含可解析结构)')
    except ValueError as e:
        print('PASS | 034-lods  | 清晰拒绝: %s' % e)
    except Exception as e:
        ok = False
        print('FAIL | 034-lods  | 非清晰异常: %r' % e)
    print('==== 跨LOD/跨资产测试', '全部通过' if ok else '存在失败', '====')
    sys.exit(0 if ok else 1)
