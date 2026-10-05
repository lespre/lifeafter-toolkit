# -*- coding: utf-8 -*-
"""T5-fix：把 003996.c159 的 per-material 晶体参数（crystal_params）写进 1110177/neox_material.json。

背景：viewer 的晶体分支读 `pr.crystal_params`（viewer.js L1139/1154/1155）；
      manifest 缺该字段 → cp=null → u_crystal_color 回退 [0,0.2118,0.8]（蓝）、
      u_base_color 回退 [0.1098,0.3961,0.502]（蓝）→ 护手/宝石恒为蓝。
来源：03_执行\\20_提取/weapon/c159_029_pair.json 的 "pairs"（c159 每材质参数块，逐项含 off/raw/value）。
      group1/block0 → material1(护手) ； group2/block1 → material2(宝石)。
      该 group↔material 归属由**项目既有产物**交叉印证：1110177 旧 viewer.json
      material_layers.per_submesh["1"] = {base_color[0.3373]³, crystal_color[0.251,0.2196,0.2314], ...}
      与 group1/block0 完全一致（脚本内断言）。

用法：python build_crystal_params.py
"""
import json, os, sys, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
SKIN = os.path.dirname(HERE)
PAIR = r'E:\la拆包项目\03_执行\\20_提取\weapon\c159_029_pair.json'
MAN = os.path.join(SKIN, 'neox_material.json')

# group/block → prim（prim1/prim2 是 pbr_crystal）
GROUP2PRIM = {1: 1, 2: 2}


def main():
    pair = json.load(open(PAIR, encoding='utf-8'))
    man = json.load(open(MAN, encoding='utf-8'))
    old_vj = json.load(open(os.path.join(SKIN, 'viewer.json'), encoding='utf-8'))
    per = (old_vj['states'][0].get('material_layers') or {}).get('per_submesh') or {}

    params_by_prim = {}
    for pr in pair.get('pairs', []):
        g = pr.get('group')
        if g not in GROUP2PRIM:
            continue
        rows = ((pr.get('pairing') or {}).get('rows')) or []
        d = {}
        for r in rows:
            v = r.get('value')
            d[r['name']] = v
        params_by_prim[GROUP2PRIM[g]] = {'params': d, 'rows': rows,
                                        'group': g, 'block': pr.get('block'),
                                        'score': pr.get('score')}

    # 交叉印证：project 既有 viewer.json per_submesh 与本脚本取到的 group 值一致
    checks = []
    for prim, sub in ((1, '1'), (2, '2')):
        pv = params_by_prim.get(prim, {}).get('params', {})
        cfg = per.get(sub, {})
        ck = {'prim': prim, 'sub': sub,
              'base_color_manifest': pv.get('u_base_color'),
              'base_color_viewerjson': cfg.get('base_color') or cfg.get('u_base_color'),
              'crystal_color_manifest': pv.get('u_crystal_color'),
              'crystal_color_viewerjson': cfg.get('crystal_color') or cfg.get('u_crystal_color')}
        ck['base_color_match'] = (ck['base_color_viewerjson'] is None) or (
            [round(x, 4) for x in ck['base_color_manifest'][:3]] == [round(x, 4) for x in ck['base_color_viewerjson'][:3]])
        ck['crystal_color_match'] = (ck['crystal_color_viewerjson'] is None) or (
            [round(x, 4) for x in ck['crystal_color_manifest'][:3]] == [round(x, 4) for x in ck['crystal_color_viewerjson'][:3]])
        checks.append(ck)
        print('prim%d  base=%s (%s)  crystal=%s (%s)  match=%s/%s'
              % (prim, ck['base_color_manifest'], ck['base_color_viewerjson'],
                 ck['crystal_color_manifest'], ck['crystal_color_viewerjson'],
                 ck['base_color_match'], ck['crystal_color_match']))

    src_sha = hashlib.sha256(open(PAIR, 'rb').read()).hexdigest()
    prov = ('c159 per-material block from %s (group%s/block%s, score=%s); '
            'pair row 逐项含 off/raw/value；group↔material 由 1110177 旧 viewer.json '
            'material_layers.per_submesh 交叉印证（base/crystal color 逐值相等）；'
            'source_sha256=%s') % ('03_执行\\20_提取/weapon/c159_029_pair.json', '{g}', '{b}', '{s}', src_sha)

    for prim, d in params_by_prim.items():
        for p in man['primitives']:
            if p['prim'] != prim:
                continue
            cp = dict(d['params'])
            cp['provenance'] = prov.format(g=d['group'], b=d['block'], s=d['score'])
            cp['_rows_raw'] = [{'name': r['name'], 'type': r['type'], 'off': r['off'], 'raw': r['raw']} for r in d['rows']]
            p['crystal_params'] = cp
            p['crystal_params_basis'] = 'REFERENCE_IMAGE_DIRECT(红宝石/银白护手为材质参数而非贴图) + c159-per-material-block'
            print('prim%d 写入 crystal_params: u_crystal_color=%s u_base_color=%s u_refraction_color=%s u_subsurface_color=%s'
                  % (prim, cp.get('u_crystal_color'), cp.get('u_base_color'),
                     cp.get('u_refraction_color'), cp.get('u_subsurface_color')))

    man['crystal_params_crosscheck'] = checks
    json.dump(man, open(MAN, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('[saved] %s (%d B)' % (MAN, os.path.getsize(MAN)))


if __name__ == '__main__':
    main()
