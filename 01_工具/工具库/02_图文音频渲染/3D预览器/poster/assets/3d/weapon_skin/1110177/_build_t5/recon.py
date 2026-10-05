# -*- coding: utf-8 -*-
"""T5 recon：把 1110177 的 c159 逻辑贴图路径映射到本地已解出文件（只读源，写本目录）。

输入：03_执行\\20_提取/weapon/manifest.json（GPK 解包索引）
输出：_t5_logical_map.json（本目录内）
"""
import json, os, re, sys

W = r'E:\la拆包项目\03_执行\\20_提取\weapon'
OUT = os.path.dirname(os.path.abspath(__file__))

NEED = {
    'skin_a': r'skin_2003_029001a.tga',
    'skin_m': r'skin_2003_029001m.tga',
    'skin_n': r'skin_2003_029001n.tga',
    'skin_b_m': r'skin_2003_029001b_m.tga',
    'crystal_bump_n02': r'crystal_bump_n02.tga',
    'crystal_caustic_uvva002': r'crystal_caustic_uvva002.tga',
    'crystal_reflection_uvva': r'crystal_reflection_uvva.tga',
    'crystal_bump_n_uvva': r'crystal_bump_n_uvva.tga',
    'crystal_caustic_uvva': r'crystal_caustic_uvva.tga',
    'refraction_envmap_3': r'refraction_envmap_3.tga',
    'cube_qiangpi': r'qiangpi.cube',
    'cube_car_studio01': r'car_studio01.cube',
    'cube_fashion_qiangpi': r'fashion_qiangpi.cube',
}


def main():
    p = os.path.join(W, 'manifest.json')
    d = json.load(open(p, encoding='utf-8'))
    ents = d['entries']
    print('manifest: source=%s files=%s entries=%s' % (d.get('source'), d.get('files'), len(ents)))
    print('entry[0] =', json.dumps(ents[0], ensure_ascii=False)[:600])
    # 收集 029 相关
    by_lower = {}
    for e in ents:
        s = json.dumps(e, ensure_ascii=False).lower()
        if 'skin_2003_029' in s:
            by_lower.setdefault('029', []).append(e)
    print('\n=== 029 相关条目 %d ===' % len(by_lower.get('029', [])))
    for e in by_lower.get('029', [])[:40]:
        print('  ', json.dumps(e, ensure_ascii=False)[:300])
    # 逐个查需要项
    print('\n=== 目标资源查找 ===')
    found = {}
    for key, needle in NEED.items():
        nl = needle.lower()
        hits = [e for e in ents if nl in json.dumps(e, ensure_ascii=False).lower()]
        found[key] = hits
        print('%-24s %-46s hits=%d' % (key, needle, len(hits)))
        for h in hits[:4]:
            print('      ', json.dumps(h, ensure_ascii=False)[:300])
    json.dump({k: v for k, v in found.items()}, open(os.path.join(OUT, '_t5_logical_map.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
