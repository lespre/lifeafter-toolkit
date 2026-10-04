# -*- coding: utf-8 -*-
"""NAMES_audit3.py — 只读补充 2：逐组明细、时限变体层（13 official / 5 candidate）枚举、1110169/1110146 资产侧核查。"""
import io, json, os, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
WIKI = r'E:\la拆包项目\08Lifeafter wiki'
R = r'E:\la拆包项目\03拆包产物'
OUT = os.path.join(R, '_target_1110171')
G6 = {'赤月晶魄': ['1110115', '1110116', '1110117'], '炽日耀斑': ['1110131', '1110132', '1110133'],
      '金乌负日': ['1110142', '1110143', '1110144'], '沙海月鸣': ['1110159', '1110160', '1110161'],
      '水晶玫瑰': ['1110173', '1110174', '1110175']}
init = json.load(open(os.path.join(WIKI, 'data', 'boards', 'weapon_skin_sfx_text_sources.json'), encoding='utf-8'))
items = init['items']
by_id = {str(x['id']): x for x in items}
audit = json.load(open(os.path.join(OUT, 'NAMES_audit.json'), encoding='utf-8'))
L = []

# ① 逐组明细（组内 3 个 id 的全部身份字段）
audit['g6_detail'] = {}
L.append('== G6 五组逐 id 身份字段')
for nm, ids in G6.items():
    audit['g6_detail'][nm] = []
    for i in ids:
        x = by_id.get(i, {})
        rec = {k: x.get(k) for k in ('name', 'name_status', 'official_name_status', 'catalog_layer', 'version_status',
                                     'release_state', 'weapon_type', 'weapon_type_label', 'weapon_type_state',
                                     'level', 'grade', 'sale_ts', 'sale_date', 'model_path', 'sfx_item_count',
                                     'named_sfx_item_count', 'variant_item_count')}
        rec['id'] = i
        audit['g6_detail'][nm].append(rec)
        L.append('  %s %s %s level=%s grade=%s wt=%s(%s) sale=%s release=%s variant_items=%s path=%s' % (
            i, rec['name'], rec['name_status'], rec['level'], rec['grade'], rec['weapon_type'],
            rec['weapon_type_label'], rec['sale_date'], rec['release_state'], rec['variant_item_count'], rec['model_path']))

# ② 时限变体层枚举：timed id 区间 11,100,000–11,199,999（runtime literal），permanent = id//10
wsd = json.load(open(os.path.join(R, 'weapon_skin_data_rows.json'), encoding='utf-8'))
row_keys = [str(r.get('key')) for r in wsd['rows']]
item_rows = json.load(open(os.path.join(R, 'common_item_data_rows.json'), encoding='utf-8'))
item_ids = {str(r.get('id')) for r in item_rows['rows']}
LO, HI = 11100000, 11199999
main_ids = [k for k in row_keys if not (LO <= int(k) <= HI)]
timed_ids = [k for k in row_keys if LO <= int(k) <= HI]
variants = []
for t in timed_ids:
    variants.append({'id': t, 'permanent_skin_id': str(int(t) // 10),
                     'permanent_present_in_weapon_skin_data': str(int(t) // 10) in row_keys,
                     'has_item_row': t in item_ids,
                     'name_from_board_items': (by_id.get(t) or {}).get('name'),
                     'in_board_items_115': t in by_id})
audit['timed_layer'] = {'rule': 'runtime literal [11100000,11199999]; permanent = id//10',
                        'weapon_skin_data_rows': len(row_keys), 'main_rows': len(main_ids), 'timed_rows': len(timed_ids),
                        'timed_with_item_row': sum(1 for v in variants if v['has_item_row']),
                        'timed_without_item_row': [v for v in variants if not v['has_item_row']],
                        'variants': sorted(variants, key=lambda v: v['id'])}
L.append('')
L.append('== 时限变体层（weapon_skin_data_rows.json：主 %d + 变体 %d = %d）' % (len(main_ids), len(timed_ids), len(row_keys)))
L.append('   有道具行变体 = %d / 无道具行（candidate）= %d' % (
    audit['timed_layer']['timed_with_item_row'], len(audit['timed_layer']['timed_without_item_row'])))
for v in sorted(variants, key=lambda v: v['id']):
    L.append('   %s → perm=%s item_row=%-5s board_item_name=%s' % (
        v['id'], v['permanent_skin_id'], v['has_item_row'], v['name_from_board_items']))
L.append('   无道具行（名称 candidate）: %s' % json.dumps([v['id'] for v in variants if not v['has_item_row']], ensure_ascii=False))

# ③ 1110169 / 1110146 资产侧核查
audit['special_assets'] = {}
L.append('')
L.append('== 1110169 / 1110146 资产侧（只读磁盘）')
for i in ('1110169', '1110146'):
    d = os.path.join(WIKI, 'assets', '3d', 'weapon_skin', i)
    files = sorted(os.path.relpath(os.path.join(r2, f), d) for r2, _, fs in os.walk(d) for f in fs) if os.path.isdir(d) else []
    rec = {'dir_exists': os.path.isdir(d), 'n_files': len(files),
           'has_viewer_json': 'viewer.json' in files, 'has_neox_material': 'neox_material.json' in files,
           'has_glb': 'model.glb' in files, 'files': files[:12]}
    audit['special_assets'][i] = rec
    L.append('  %s dir=%s files=%d viewer.json=%s neox=%s glb=%s %s' % (
        i, rec['dir_exists'], rec['n_files'], rec['has_viewer_json'], rec['has_neox_material'], rec['has_glb'], files[:8]))

json.dump(audit, open(os.path.join(OUT, 'NAMES_audit.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
open(os.path.join(OUT, 'NAMES_audit3.txt'), 'w', encoding='utf-8').write('\n'.join(L))
print('\n'.join(L))
