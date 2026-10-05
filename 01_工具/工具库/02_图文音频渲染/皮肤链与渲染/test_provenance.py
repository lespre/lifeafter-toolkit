# -*- coding: utf-8 -*-
"""test_provenance.py — source_data_integrity 判定单元测试(函数级)。
端到端注入测试见 test_provenance_e2e.py (实际启动管线)。
运行: python test_provenance.py  (exit 0 = 全过)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import weapon_skin_pipeline as W

TEX_OK = [dict(file='tex_4011.png', match=True, maxdiff=0)]
BASE = dict(textures=TEX_OK, v19_used=False, tint_map_used=False, tint_map_sourced=False,
            face_overrides_used=False, edgeface_used=False, band_used=False,
            post_executed=False, source_mode=True, out_of_root=[])

CASES = [
    ('clean(源模式全干净)', {}, True),
    ('inject: Tint 染色(无源标注)', {'tint_map_used': True}, False),
    ('sourced tint (c159解析值, 允许)', {'tint_map_used': True, 'tint_map_sourced': True}, True),
    ('inject: v19 人工改色贴图', {'v19_used': True}, False),
    ('inject: Face Override 选面', {'face_overrides_used': True}, False),
    ('inject: Band 屏幕距离带', {'band_used': True}, False),
    ('inject: 后处理(post, source模式)', {'post_executed': True}, False),
    ('inject: 贴图哈希不符(原始DDS锚定失败)', {'textures': [dict(file='tex_4011.png', match=False)]}, False),
    ('inject: 贴图路径越界', {'out_of_root': ['tex_4011.png']}, False),
    ('inject: edgeface 面选区染银', {'edgeface_used': True}, False),
]

if __name__ == '__main__':
    allok = True
    for name, over, want in CASES:
        ok, reasons = W.provenance_eval(dict(BASE, **over))
        good = (ok == want)
        allok = allok and good
        print(('PASS' if good else 'FAIL'), '|', name, '=> source_data_integrity.pass =', ok,
              ('(期望 %s)' % want) if not good else '', ('原因: ' + '; '.join(reasons)) if reasons else '')
    # fidelity 冒烟: 近似项存在 => approximate
    st, rs = W.fidelity_eval(dict(BASE), {}, None)
    good = (st == 'approximate' and len(rs) >= 1)
    allok = allok and good
    print(('PASS' if good else 'FAIL'), '| shader_fidelity 冒烟 =>', st, '(%d reasons)' % len(rs))
    print('==== 单元测试', '全部通过' if allok else '存在失败', '====')
    sys.exit(0 if allok else 1)
