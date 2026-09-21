# -*- coding: utf-8 -*-
"""从 all_equips 配置表搜索武器皮肤关键词。"""
from __future__ import annotations
import json, runpy, struct, sys
from pathlib import Path
import os

_SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
_LIB = _SCRIPT_DIR / 'bindict_lib' / 'decode_current_all_equips_D6_scalar_006.py'
if not _LIB.exists():
    _LIB = Path(r'C:/Users/Administrator/AppData/Local/hermes/mrzh_weapon_skin_audit/run_002/bindict_preflight_002/decode_current_all_equips_D6_scalar_006.py')

KEYWORD = sys.argv[1] if len(sys.argv) > 1 else '战神烈火剑'

M = runpy.run_path(str(_LIB), run_name='search')
uleb = M['uleb']
ver, n, src = M['unpack_members']()
slots = M['strings'](src[M['CHS']]['body'])
blob, de, keystarts = M['base_blob'](src[M['BASE']]['body'])

print(f'=== 搜索关键词: {KEYWORD} ===')
print(f'配置表版本: {ver}, 条目数: {n}')
print(f'字符串池大小: {len(slots)}')
print()

# 1. 在字符串池中搜索
print('--- 字符串池命中 ---')
string_hits = []
for i, s in enumerate(slots):
    if KEYWORD in s:
        string_hits.append((i, s))
        print(f'  slot[{i}] = {s}')
print(f'共 {len(string_hits)} 条字符串命中')
print()

# 2. 解码所有行，找包含关键词的行
print('--- 武器条目命中 ---')
def schema_at(ref):
    p = ref
    n2, p = uleb(blob, p, len(blob))
    bits, p = uleb(blob, p, len(blob))
    fs = []
    for ix in range(n2):
        slot, p = uleb(blob, p, len(blob))
        typ = blob[p]; p += 1
        fs.append({'index': ix, 'slot': slot, 'type': typ, 'name': slots[slot] if slot < len(slots) else f'<bad{slot}>'})
    return n2, bits, fs, p

def decode_row(key, start):
    if blob[start] != 0xd6:
        return None
    p = start + 1
    sref, p = uleb(blob, p, len(blob))
    bref, p = uleb(blob, p, len(blob))
    n3, bits3, fs3, se = schema_at(sref)
    bm = blob[bref:bref + (bits3 + 7) // 8]
    use = [f for f in fs3 if f['index'] >= bits3 or bm[f['index'] // 8] & (1 << (f['index'] % 8))]
    vals = []
    ops = []
    for f in use:
        typ = f['type']
        if typ == 1:
            v, p = uleb(blob, p, len(blob))
        elif typ == 3:
            v = blob[p]; p += 1
        elif typ == 5:
            v, p = uleb(blob, p, len(blob))
        elif typ == 11:
            v, p = uleb(blob, p, len(blob))
            ops.append((f['index'], f['name'], v))
        elif typ == 17:
            v, p = uleb(blob, p, len(blob))
            v = (v >> 1) ^ (-(v & 1))
        elif typ == 18:
            v = struct.unpack_from('<f', blob, p)[0]; p += 4
        elif typ == 34:
            v = struct.unpack_from('<d', blob, p)[0]; p += 8
        else:
            return None
        vals.append({'index': f['index'], 'name': f['name'], 'type': hex(typ), 'value': v})
    return {'key': key, 'start': start, 'schema_ref': sref, 'values': vals, 'ops': ops}

rows = [decode_row(k, st) for k, st in keystarts.items()]
rows = [r for r in rows if r]

# 找包含关键词的行
weapon_hits = []
for r in rows:
    row_text = ' '.join(str(v['value']) for v in r['values'])
    row_slots = [v['name'] for v in r['values']]
    # 检查值是否是字符串槽位引用
    for v in r['values']:
        if v['type'] == '0x5' and isinstance(v['value'], int) and v['value'] < len(slots):
            if KEYWORD in slots[v['value']]:
                weapon_hits.append(r)
                break
    # 检查key是否是字符串
    if isinstance(r['key'], int) and r['key'] < len(slots):
        if KEYWORD in slots[r['key']]:
            if r not in weapon_hits:
                weapon_hits.append(r)

print(f'共 {len(weapon_hits)} 个武器条目命中')
print()

# 3. 输出命中条目的详细信息
for i, r in enumerate(weapon_hits):
    print(f'=== 命中 #{i+1} ===')
    print(f'  key: {r["key"]}', end='')
    if isinstance(r['key'], int) and r['key'] < len(slots):
        print(f' ({slots[r["key"]]})', end='')
    print()
    print(f'  schema_ref: {r["schema_ref"]}')
    print(f'  字段值:')
    for v in r['values']:
        val_str = str(v['value'])
        if v['type'] == '0x5' and isinstance(v['value'], int) and v['value'] < len(slots):
            val_str = f'{v["value"]} -> "{slots[v["value"]]}"'
        print(f'    {v["name"]} ({v["type"]}): {val_str}')
    if r['ops']:
        print(f'  0x0B引用:')
        for ix, name, v in r['ops']:
            print(f'    {name}: offset={v}')
    print()

# 4. 保存结果
OUT = _SCRIPT_DIR / 'output' / 'weapon_search'
OUT.mkdir(parents=True, exist_ok=True)
result = {
    'keyword': KEYWORD,
    'string_hits': [{'slot': i, 'text': s} for i, s in string_hits],
    'weapon_hits': weapon_hits,
}
out_path = OUT / f'search_{KEYWORD}.json'
out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'结果已保存: {out_path}')
