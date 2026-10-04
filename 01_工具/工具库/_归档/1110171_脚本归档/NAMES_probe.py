# -*- coding: utf-8 -*-
"""NAMES_probe.py — 只读：探明候选名称表的结构，并搜索 15 个传世 L6 id 与 model_path。输出 NAMES_probe.txt。"""
import io, json, os, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
R = r'E:\la拆包项目\03拆包产物'
OUT = os.path.join(R, '_target_1110171')
G6 = ['1110115', '1110116', '1110117', '1110131', '1110132', '1110133', '1110142', '1110143', '1110144',
      '1110159', '1110160', '1110161', '1110173', '1110174', '1110175']
PATHS = ['weapon/skin/skin_2003_013', 'weapon/skin/skin_2003_017', 'weapon/skin/skin_2003_018',
         'weapon/skin/skin_1006_008', 'weapon/skin/skin_1006_009', 'weapon/skin/skin_1006_010',
         'weapon/skin/skin_1007_007', 'weapon/skin/skin_1007_008', 'weapon/skin/skin_1007_009',
         'weapon/skin/skin_1001_011', 'weapon/skin/skin_1001_012', 'weapon/skin/skin_1001_013',
         'weapon/skin/skin_1012_011', 'weapon/skin/skin_1012_012', 'weapon/skin/skin_1012_013']
FILES = ['weapon_skin_data_rows.json', 'fashion_obtain_handbook_rows.json', 'common_item_data_rows.json',
         'common_item_py3_index.json', 'weapon_skin_data_全量.csv',
         os.path.join('batch_3d', 'skins_grade5.json'),
         os.path.join('wiki_position_chain_audit_20260902', 'fashion_row_field_probe.json')]

lines = []


def structure(v, depth=0, maxd=2):
    pad = '  ' * depth
    if isinstance(v, dict):
        ks = list(v.keys())
        return 'dict(%d) keys=%s' % (len(ks), ks[:10])
    if isinstance(v, list):
        return 'list(%d) first=%s' % (len(v), structure(v[0], depth, maxd) if v and depth < maxd else type(v[0]).__name__ if v else 'empty')
    return '%s %s' % (type(v).__name__, str(v)[:60])


for f in FILES:
    p = os.path.join(R, f)
    if not os.path.isfile(p):
        lines.append('#### %s : MISSING' % f)
        continue
    lines.append('#### %s (%d B)' % (f, os.path.getsize(p)))
    try:
        if f.endswith('.csv'):
            txt = open(p, encoding='utf-8-sig', errors='replace').read()
            lines.append('   csv lines=%d ; header=%s' % (len(txt.splitlines()), txt.splitlines()[0][:300] if txt else ''))
            for gid in G6:
                hit = [ln for ln in txt.splitlines() if gid in ln]
                if hit:
                    lines.append('   id %s → %d 行: %s' % (gid, len(hit), hit[0][:300]))
            continue
        d = json.load(open(p, encoding='utf-8'))
        lines.append('   top: %s' % structure(d))
        if isinstance(d, dict):
            for k in list(d.keys())[:6]:
                lines.append('     [%s] %s' % (k, structure(d[k])))
        # 关键 entry
        if f == 'weapon_skin_data_rows.json' and isinstance(d, dict):
            for ekey in ('11762', '21081'):
                if ekey in d:
                    lines.append('   ENTRY %s = %s' % (ekey, json.dumps(d[ekey], ensure_ascii=False)[:1500]))
                else:
                    lines.append('   ENTRY %s 不在顶层键' % ekey)
        # id / path 搜索
        blob = open(p, encoding='utf-8', errors='replace').read()
        for gid in G6:
            c = blob.count(gid)
            if c:
                i = blob.find(gid)
                lines.append('   id %s 出现 %d 次，首处上下文: %s' % (gid, c, blob[max(0, i - 160):i + 200].replace('\n', ' ')[:360]))
        for pa in PATHS[:4]:
            c = blob.count(pa)
            if c:
                i = blob.find(pa)
                lines.append('   path %s 出现 %d 次，上下文: %s' % (pa, c, blob[max(0, i - 200):i + 260].replace('\n', ' ')[:460]))
    except Exception as ex:
        lines.append('   ERROR %s: %s' % (type(ex).__name__, ex))

open(os.path.join(OUT, 'NAMES_probe.txt'), 'w', encoding='utf-8').write('\n'.join(lines))
print('\n'.join(lines))
