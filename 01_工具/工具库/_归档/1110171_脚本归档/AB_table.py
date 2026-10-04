# -*- coding: utf-8 -*-
"""AB_table.py — 绑定差异表（c159 逐槽直证 vs 当前绑定 vs A 组），只读。
   输入：AB_bindings.json、C159PARSE_skins_fixed.json、各皮肤 neox_material.json
   输出：AB_table.md / AB_table.json
"""
import io, json, os, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
W = r'E:\la拆包项目\08Lifeafter wiki\assets\3d\weapon_skin'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
SKINS = ['1110024', '1110129', '1110145', '1110152', '1110165', '1110171', '1110177']
C159KEY = {'1110024': '1110024', '1110129': '1110129', '1110145': '1110145', '1110152': '1110152',
           '1110165': '1110165', '1110171': '1110171_dual', '1110177': '1110177'}
SLOTS = ['Tex0', 't_basecolor', 'ParamMap', 't_surfacemap', 'NormalMap', 't_custom_ibl']

bind = json.load(open(os.path.join(OUT, 'AB_bindings.json'), encoding='utf-8'))
c159 = json.load(open(os.path.join(OUT, 'C159PARSE_skins_fixed.json'), encoding='utf-8'))

res = {'per_skin': {}}
lines = []
lines.append('# 绑定差异表（task-15）\n')
lines.append('口径：**源 c159 = `C159PARSE_skins_fixed.json` 的 `material_block/slot_class/ref` 直读**；'
             '当前 local_file 与 sha16 取自磁盘实际文件；A 组 = weapon prim 的 Tex0 改指同族 `*_a.png`。\n')

for s in SKINS:
    c = c159.get(C159KEY[s], {})
    rows = c.get('rows', [])
    decl = {}
    for r in rows:
        decl.setdefault((r['material_block'], r['slot_class']), set()).add(r['ref'])
    weapon_blocks = sorted(b for (b, sl) in decl if sl == 'Tex0' and any(x.endswith('a.tga') for x in decl[(b, 'Tex0')]))
    crystal_blocks = sorted({b for (b, sl) in decl if (b, 't_basecolor') in decl})
    e = {'c159_file': c.get('file'), 'c159_blocks': sorted(set(r['material_block'] for r in rows)),
         'weapon_blocks': weapon_blocks, 'crystal_blocks': crystal_blocks,
         'declared_Tex0_weapon': sorted({x for b in weapon_blocks for x in decl[(b, 'Tex0')]}),
         'declared_Tex0_crystal': sorted({x for b in crystal_blocks for x in decl.get((b, 'Tex0'), set())}),
         'prim_rows': [], 'slot_mismatch': []}
    for pr in bind['skins'][s]['prims']:
        t0 = pr['slots'].get('Tex0') or {}
        row = {'prim': pr['prim'], 'material': pr['material'], 'shader_kind': pr['kind'],
               'cur': t0.get('local_file'), 'cur_sha16': t0.get('disk_sha16'), 'cur_bytes': t0.get('disk_bytes'),
               'manifest_logical_path': t0.get('logical_path'), 'manifest_evidence': (t0.get('evidence') or '')[:120],
               'A': t0.get('A_local_file'), 'A_sha16': t0.get('A_sha16'), 'A_on_disk': t0.get('A_on_disk'),
               'text_diff': t0.get('text_diff')}
        if pr['kind'] == 'crystal':
            row['verdict'] = 'crystal：c159 声明 Tex0=*_b_m（掩码），当前 %s' % ('符合' if (t0.get('local_file') or '').endswith('_b_m.png') else '不符')
        else:
            row['verdict'] = ('weapon：c159 全块声明 Tex0=*a；当前 %s ⇒ %s' % (
                t0.get('local_file'), '不符' if (t0.get('local_file') or '').endswith('_b_m.png') else '符合'))
            if not t0.get('A_on_disk'):
                row['verdict'] += '（A 组无法覆盖：同族 `_a.png` 磁盘缺失）'
        e['prim_rows'].append(row)
        # 其它槽的差异
        for sl in SLOTS:
            if sl == 'Tex0':
                continue
            cur = pr['slots'].get(sl)
            cur_lf = cur.get('local_file') if cur else None
            dset = sorted({x for (b, k) in decl if k == sl for x in decl[(b, k)]})
            if cur_lf is None and not dset:
                continue
            v = 'ok' if (cur_lf and dset) else ('未绑定' if cur_lf is None else ('c159 无该槽' if not dset else '?'))
            if cur_lf and dset:
                csuf = cur_lf.split('/')[-1].replace('.png', '').replace('_repack', '')
                v = 'ok(名族同)' if any(csuf.split('_')[-1] in x for x in dset) else '名称不同'
                if sl == 'ParamMap' and 'param_repack' in (cur_lf or ''):
                    v = '派生重打包（源为 *m）'
            e['slot_mismatch'].append({'slot': sl, 'prim': pr['prim'], 'cur': cur_lf,
                                       'cur_sha16': (cur or {}).get('disk_sha16'),
                                       'c159_declared_set': dset, 'verdict': v})
    res['per_skin'][s] = e

    lines.append('## %s（c159=%s，块 %s；weapon 块 %s / crystal 块 %s）' % (
        s, e['c159_file'], e['c159_blocks'], e['weapon_blocks'], e['crystal_blocks']))
    lines.append('c159 weapon 块 Tex0 声明：%s ｜ crystal 块 Tex0 声明：%s\n' % (
        e['declared_Tex0_weapon'], e['declared_Tex0_crystal']))
    lines.append('| prim | shader_kind | 槽 | manifest.logical_path（自称 c159 名） | 当前 local_file | cur sha16 | c159 逐槽直证 | A 组 local_file | A sha16 | 文本差异 | 判定 |')
    lines.append('|---|---|---|---|---|---|---|---|---|---|---|')
    for r in e['prim_rows']:
        lines.append('| %s | %s | Tex0 | %s | %s | %s | %s | %s | %s | %s | %s |' % (
            r['prim'], r['shader_kind'], r['manifest_logical_path'] or '—', r['cur'], r['cur_sha16'],
            (e['declared_Tex0_crystal'] if r['shader_kind'] == 'crystal' else e['declared_Tex0_weapon']),
            r['A'] or '—', r['A_sha16'] or '—', r['text_diff'] or '—', r['verdict']))
    # 其它槽汇总
    seen = {}
    for m in e['slot_mismatch']:
        seen.setdefault((m['slot'], m['cur'], tuple(m['c159_declared_set']), m['verdict']), []).append(m['prim'])
    lines.append('')
    lines.append('其它槽（汇总，prim 列表）：')
    lines.append('| 槽 | 当前 local_file | c159 声明集合 | 判定 | prims |')
    lines.append('|---|---|---|---|---|')
    for (sl, cur, dset, v), prims in sorted(seen.items(), key=lambda x: (x[0][0], str(x[0][1]))):
        lines.append('| %s | %s | %s | %s | %s |' % (sl, cur or '—', list(dset) or '—', v, prims))
    lines.append('')

json.dump(res, open(os.path.join(OUT, 'AB_table.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
open(os.path.join(OUT, 'AB_table.md'), 'w', encoding='utf-8').write('\n'.join(lines))
print('\n'.join(lines[:40]))
print('... total lines', len(lines), '-> AB_table.md / AB_table.json')
