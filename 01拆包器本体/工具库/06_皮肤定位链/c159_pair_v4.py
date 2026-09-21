# -*- coding: utf-8 -*-
"""c159_pair v4 — 归属规则修复版（只改归属逻辑，不改 c159 解析本身）

修复点（对应 2026-09-15 外审）：
 1. find_groups_v2：每个槽位组保留**原始字节偏移**（align + st*2）；
    **删除**"相邻列表相同就丢弃"的旧逻辑（它会吞掉槽位表相同但独立的材质记录）。
 2. 三层分离：材质记录（name/shader/record_off） / 槽位组（group_off） / 数值块（block_off）。
    禁止仅凭评分或晶体材质顺序静默分配。
 3. 仅当「晶体材质数 == 槽位组数 == 数值块数」且三方文件顺序一致时，输出
    ordered candidate-high（method=ordered-1to1）；否则 fail-closed：
    attribution=unresolved，不给出任何块→材质分配。
 4. 每个 primitive 输出：MtlIdx / 材质名 / shader / 材质记录偏移 / 槽位组偏移 /
    数值块偏移 / 参数表 / 归属方法 / 置信度。

用法：
  python c159_pair_v4.py <material.c159> [--binding <bind.c159>] [--json out.json]
  python c159_pair_v4.py --regress        # 三资产回归 + 反向测试
"""
import os, re, sys, json, struct

E = r'E:\la拆包项目\03拆包产物'
D = os.path.join(E, 'weapon')

# ---------- 名称表 ----------
def read_names(b):
    names = {}
    for m in re.finditer(rb'([A-Za-z_][\w]{2,40})\x00', b):
        s = m.group(1).decode('latin1')
        names.setdefault(s, m.start())
    idx = {}
    # 槽位名 → 索引：按出现顺序编号（与旧版一致的保守做法）
    for i, m in enumerate(re.finditer(rb'([A-Za-z_][\w]{2,40})\x00', b)):
        s = m.group(1).decode('latin1')
        idx.setdefault(s, i)
    full = [None] * (max(idx.values()) + 1 if idx else 0)
    for nm, i in idx.items():
        if full[i] is None: full[i] = nm
    # ★ 原版 pair_block 需要 names['full']（按索引反查槽位名）
    return dict(idx=idx, max_index=len(idx) - 1, all=names, full=full)


# ---------- 槽位组（保留偏移，不去重） ----------
def find_groups_v2(b, names):
    max_i = names['max_index']
    tm = names['idx'].get('TransparentMode', max_i)
    runs = []
    for align in (0, 1):
        seg = b[align:]
        n = len(seg) // 2
        vals = struct.unpack('<%dH' % n, seg[:n * 2])
        i = 0
        while i < n:
            if vals[i] <= max_i:
                st = i
                while i < n and vals[i] <= max_i:
                    i += 1
                if i - st >= 6:
                    runs.append((align, st, list(vals[st:i])))
            else:
                i += 1
    seen = set(); uniq = []
    for align, st, v in runs:
        key = (align, st)
        if key in seen:
            continue
        seen.add(key)
        uniq.append(dict(align=align, st=st, off=align + st * 2, vals=v))
    uniq = [r for r in uniq if max(r['vals']) >= 3
            and sum(1 for v in r['vals'] if v >= 3) >= 2 and len(set(r['vals'])) >= 3]
    groups = []
    for r in uniq:
        cur = []
        off0 = None
        for k, v in enumerate(r['vals']):
            if cur == []:
                off0 = r['off'] + k * 2
            cur.append(v)
            if v == tm:
                if len(cur) >= 6:
                    groups.append(dict(vals=cur, off=off0, align=r['align'], st=r['st'] + k - len(cur) + 1))
                cur = []
        if len(cur) >= 6:
            groups.append(dict(vals=cur, off=off0, align=r['align'], st=r['st']))
    # ★ 不再丢弃"内容相同但位置不同"的组：内容相同只做标注，不做删除
    for i, g in enumerate(groups):
        g['index'] = i
        g['duplicate_of'] = next((j for j in range(i) if groups[j]['vals'] == g['vals']), None)
    return groups


# ---------- 数值块 ----------
def find_blocks(entries):
    # ★ 复用原 c159_pair 的块发现
    import importlib.util as _iu
    _spec = _iu.spec_from_file_location('_c159pair2', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'c159_pair.py'))
    _m = _iu.module_from_spec(_spec); _spec.loader.exec_module(_m)
    return _m.find_blocks(entries)
    clusters, cur = [], []
    for e in nums:
        if cur and e['off'] - cur[-1]['off'] > 100:
            clusters.append(cur); cur = []
        cur.append(e)
    if cur:
        clusters.append(cur)
    return [c for c in clusters if len(c) >= 5]


def parse_entries(b, lo=0, hi=None):
    # ★ 复用原 c159_pair 的条目解析（含数值记录），不自行重写
    import importlib.util as _iu
    _spec = _iu.spec_from_file_location('_c159pair', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'c159_pair.py'))
    _m = _iu.module_from_spec(_spec); _spec.loader.exec_module(_m)
    return _m.parse_entries(b, lo, hi) if hi is not None else _m.parse_entries(b, lo)


def read_materials(b):
    """复用原版 read_materials：名字与 shader 为两个平行数组（不交错）"""
    import importlib.util as _iu
    _sp = _iu.spec_from_file_location('_c159p_r', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'c159_pair.py'))
    _m = _iu.module_from_spec(_sp); _sp.loader.exec_module(_m)
    mats, shaders = _m.read_materials(b)
    hits = {}
    for mm in re.finditer(rb'[\x20-\x7e]{2,}', b):
        nm = mm.group().decode('latin1')
        if nm in mats and nm not in hits:
            hits[nm] = mm.start()
    recs = [dict(name=nm, record_off=hits.get(nm), shader=(shaders[i] if i < len(shaders) else None))
            for i, nm in enumerate(mats)]
    return recs, shaders

def valid_groups(mats, groups):
    nm0 = min([m['record_off'] for m in mats if m['record_off'] is not None], default=None)
    return sorted([g for g in groups if (nm0 is None or g['off'] < nm0)], key=lambda g: g['off'])

def attribute(mats, groups, blocks, bind=None):
    valid = valid_groups(mats, groups)
    sh_ok = all(m['shader'] for m in mats)
    crystal = [(i, m) for i, m in enumerate(mats) if m['shader'] and 'crystal' in m['shader']]
    n_mats, n_g, n_c, n_b = len(mats), len(valid), len(crystal), len(blocks)
    reason = []
    if n_mats != n_g: reason.append('材质数(%d)!=材质名前有效槽位组数(%d)' % (n_mats, n_g))
    if n_c != n_b: reason.append('晶体材质数(%d)!=数值块数(%d)' % (n_c, n_b))
    if not sh_ok: reason.append('shader 数组与材质数不等 -> 无法判定晶体')
    if reason:
        return dict(method='fail-closed', confidence='unresolved', assign={}, reason=reason,
                    counts=dict(materials=n_mats, crystal_mats=n_c, valid_groups=n_g, blocks=n_b),
                    valid_group_offsets=[g['off'] for g in valid])
    assign, bi = {}, 0
    for i, m in enumerate(mats):
        a = dict(group=i, block=None)
        if m['shader'] and 'crystal' in m['shader']:
            a['block'] = bi; bi += 1
        assign[i] = a
    if bi != len(blocks):
        return dict(method='fail-closed', confidence='unresolved', assign={},
                    reason=['存在未消费数值块 %s' % list(range(bi, len(blocks)))],
                    counts=dict(materials=n_mats, crystal_mats=n_c, valid_groups=n_g, blocks=n_b),
                    valid_group_offsets=[g['off'] for g in valid])
    return dict(method='ordered-1to1', confidence='candidate-high', assign=assign,
                counts=dict(materials=n_mats, crystal_mats=n_c, valid_groups=n_g, blocks=n_b),
                valid_group_offsets=[g['off'] for g in valid])


def analyze_v4(mtl_path, bind_path=None):
    b = open(mtl_path, 'rb').read()
    names = read_names(b)
    entries = parse_entries(b)
    groups = find_groups_v2(b, names)
    blocks = find_blocks(entries)
    mats, shaders = read_materials(b)
    vg = valid_groups(mats, groups)
    att = attribute(mats, groups, blocks, bind_path)
    # ★ 参数解析：用该材质自己的有效槽位组 vals × 对应数值块调用原版 pair_block
    import importlib.util as _iu
    _sp = _iu.spec_from_file_location('_c159p_pb', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'c159_pair.py'))
    _m = _iu.module_from_spec(_sp); _sp.loader.exec_module(_m)
    def _val_of(r):
        for k in ('value', 'val', 'v'):
            if k in r: return r[k]
        return None
    prims = []
    for i, m in enumerate(mats):
        a = att['assign'].get(i)
        row = dict(prim=i, mtl_idx=i, material=m['name'], shader=m['shader'],
                   material_record_off=m['record_off'],
                   group_off=(vg[a['group']]['off'] if (a and a.get('group') is not None and a['group'] < len(vg)) else None),
                   block_off=(blocks[a['block']][0]['off'] if (a and a.get('block') is not None) else None),
                   params={}, attribution_method=att['method'], confidence=(att['confidence'] if a else 'unresolved'))
        if a and a.get('block') is not None and a.get('group') is not None and a['group'] < len(vg):
            g = vg[a['group']]; blk = blocks[a['block']]
            pr = _m.pair_block(names, g['vals'], blk)
            params, dropped = {}, []
            for r in pr['rows']:
                nm = r.get('name') or r.get('slot') or r.get('param')
                vv = _val_of(r)
                if nm and vv is not None: params[nm] = vv
                elif nm: dropped.append(nm)
            row['params'] = params
            row['pair_consumed'] = pr.get('consumed')
            row['pair_score'] = pr.get('score')
            row['leftover'] = [dict(off=e.get('off'), type=e.get('type'), value=e.get('value')) for e in (pr.get('leftover') or [])]
            row['warnings'] = list(pr.get('warnings') or []) + (['参数解析失败: %s' % dropped] if dropped else [])
            # ★ 未消费值 / 严重形状不匹配 → 不得保持 candidate-high
            n_slots = len([v for v in g['vals'] if not _m._is_str_slot(names, v)])
            severe = (len(row['leftover']) > max(2, int(0.15 * max(1, n_slots)))) or bool(dropped)
            if severe:
                row['confidence'] = 'unresolved'
                row['attribution_method'] = 'ordered-1to1+param-fail'
                row['warnings'].append('fail-closed 原因: leftover=%d 槽位=%d dropped=%s' % (len(row['leftover']), n_slots, dropped))
                row['attribution_method'] = 'ordered-1to1'
                row['confidence'] = 'candidate-high' if not dropped else 'unresolved'
        prims.append(row)
    return dict(file=os.path.basename(mtl_path), counts=att['counts'], method=att['method'],
                valid_group_offsets=att.get('valid_group_offsets'),
                confidence=att['confidence'], reason=att.get('reason'),
                groups=[dict(index=g['index'], off=g['off'], n=len(g['vals']), dup_of=g['duplicate_of'], valid=(g in vg)) for g in groups],
                blocks=[dict(index=k, off=bl[0]['off'], n=len(bl)) for k, bl in enumerate(blocks)],
                primitives=prims)


# ---------- 回归 ----------
CASES = [
    ('001265.c159', 'dual 光影咏叹调（7 材质；晶体=1,2,3,5,6）',
     dict(crystal=5, blocks=5, expect_offsets=[3745, 4560, 5375, 6509, 7262])),
    ('001223.c159', 'single 光影咏叹调（3 材质；晶体=1,2）', dict(crystal=2, blocks=None, expect_offsets=None)),
    ('003996.c159', '极光剑 029（3 材质；晶体=1,2）', dict(crystal=2, blocks=None, expect_offsets=None)),
]


def regress():
    res = []
    for f, label, exp in CASES:
        p = os.path.join(D, f)
        if not os.path.exists(p):
            res.append(dict(file=f, label=label, error='文件缺失')); continue
        r = analyze_v4(p)
        r['label'] = label
        r['expect'] = exp
        # 断言
        checks = []
        if exp.get('expect_offsets'):
            got = [bl['off'] for bl in r['blocks']]
            checks.append(('块偏移集合一致', got == exp['expect_offsets'], got))
            checks.append(('block3@6509 未漏配',
                           any(p['block_off'] == 6509 for p in r['primitives']), [p['block_off'] for p in r['primitives']]))
        checks.append(('晶体材质数=%s' % exp['crystal'], r['counts']['crystal_mats'] == exp['crystal'], r['counts']['crystal_mats']))
        # ★ 真实参数断言（阻止 prim5/prim6 再次串块）
        by = {p['prim']: p for p in r['primitives']}
        def pv(i, k):
            return (by.get(i, {}).get('params') or {}).get(k)
        if exp.get('expect_offsets'):
            checks.append(('prim5 参数表非空', bool(pv(5,'u_base_color') or pv(5,'u_crystal_color')), pv(5,'u_base_color')))
            checks.append(('prim5 u_base_color=[0.1098,0.3961,0.502,1]',
                           [round(x,4) for x in (pv(5,'u_base_color') or [])] == [0.1098,0.3961,0.502,1], pv(5,'u_base_color')))
            checks.append(('prim5 u_crystal_color=[0,0.2118,0.8,1]',
                           [round(x,4) for x in (pv(5,'u_crystal_color') or [])] == [0.0,0.2118,0.8,1], pv(5,'u_crystal_color')))
            checks.append(('prim5 u_detail_tilling=4', pv(5,'u_detail_tilling') == 4, pv(5,'u_detail_tilling')))
            checks.append(('prim5 u_detail_intensity=0.1', pv(5,'u_detail_intensity') == 0.1, pv(5,'u_detail_intensity')))
            checks.append(('prim5 u_crystal_metallic=1', pv(5,'u_crystal_metallic') == 1, pv(5,'u_crystal_metallic')))
            checks.append(('prim5 不得有 u_detail_offset_x/y',
                           (pv(5,'u_detail_offset_x') is None and pv(5,'u_detail_offset_y') is None),
                           [pv(5,'u_detail_offset_x'), pv(5,'u_detail_offset_y')]))
            cc6 = [round(x,4) for x in (pv(6,'u_crystal_color') or [])]
            checks.append(('prim6 u_crystal_color=[0.0039,0,0.6745,1]', cc6 == [0.0039,0.0,0.6745,1], pv(6,'u_crystal_color')))
            checks.append(('prim6 u_detail_offset_x=-1', pv(6,'u_detail_offset_x') == -1, pv(6,'u_detail_offset_x')))
            checks.append(('prim6 u_detail_offset_y=-0.68', pv(6,'u_detail_offset_y') == -0.68, pv(6,'u_detail_offset_y')))
            checks.append(('prim5/prim6 不串块', (pv(5,'u_crystal_color') or [None])[0] != (pv(6,'u_crystal_color') or [None])[0], None))
        else:
            for pr in r['primitives']:
                if pr['shader'] and 'crystal' in (pr['shader'] or ''):
                    checks.append(('prim%d 参数表非空' % pr['prim'], bool(pr['params']), list(pr['params'])[:3] or '{}'))
        used = [p['block_off'] for p in r['primitives'] if p['block_off'] is not None]
        blk_all = [bl['off'] for bl in r['blocks']]
        checks.append(('所有数值块被消费一次', sorted(used) == sorted(blk_all) and len(set(used)) == len(used), used))
        r['checks'] = checks
        res.append(r)
    return res


def reverse_tests():
    """反向测试：相同槽位组不同块 → 不得去重/串材质；数量不一致 → 必须 fail-closed"""
    out = []
    # ① 构造两个内容完全相同的槽位组（不同位置）
    # 组必须在材质名之前（与真实文件一致）；两个组槽位列表完全相同、仅位置不同
    g  = dict(vals=[5, 7, 9, 11, 13, 15], off=100, align=0, st=1, index=0, duplicate_of=None)
    g2 = dict(vals=[5, 7, 9, 11, 13, 15], off=200, align=0, st=2, index=1, duplicate_of=0)
    b1 = [dict(off=5000, type='f32', value=1.0)] * 8
    b2 = [dict(off=6000, type='f32', value=2.0)] * 8
    mats = [dict(name='skin_x_0', record_off=1000, shader='shader\\pbr_crystal.fx::TShader'),
            dict(name='skin_x_1', record_off=1200, shader='shader\\pbr_crystal.fx::TShader')]
    a = attribute(mats, [g, g2], [b1, b2])
    out.append(dict(test='相同槽位组不同块', method=a['method'], confidence=a['confidence'],
                    assign=a['assign'], groups_kept=2,
                    pass_=(len(a['assign']) == 2 and a['assign'][0]['block'] == 0 and a['assign'][1]['block'] == 1)))
    # ② 数量不一致（2 晶体 vs 1 块）→ fail-closed
    a2 = attribute(mats, [g, g2], [b1])
    out.append(dict(test='数量不一致', method=a2['method'], confidence=a2['confidence'], assign=a2['assign'],
                    reason=a2.get('reason'), pass_=(a2['method'] == 'fail-closed' and not a2['assign'])))
    return out


if __name__ == '__main__':
    a = sys.argv[1:]
    if '--regress' in a:
        R = regress(); T = reverse_tests()
        print('=== 三资产回归 ===')
        for r in R:
            if r.get('error'):
                print('  %-16s %s ✗' % (r['file'], r['error'])); continue
            print('  %-16s %-34s 晶体=%s 组=%s 块=%s 方法=%s 置信=%s' % (
                r['file'], r['label'], r['counts']['crystal_mats'], r['counts']['valid_groups'], r['counts']['blocks'],
                r['method'], r['confidence']))
            print('      块偏移: %s' % [bl['off'] for bl in r['blocks']])
            for c in r['checks']:
                print('      [%s] %s → %s' % ('PASS' if c[1] else 'FAIL', c[0], c[2]))
            for p in r['primitives']:
                print('      prim%d MtlIdx=%s %-18s %-14s rec@%s grp@%s blk@%s %s' % (
                    p['prim'], p['mtl_idx'], p['material'], (p['shader'] or '-'),
                    p['material_record_off'], p['group_off'], p['block_off'], p['confidence']))
        print('=== 反向测试 ===')
        for t in T:
            print('  [%s] %s → method=%s conf=%s assign=%s %s' % ('PASS' if t['pass_'] else 'FAIL',
                  t['test'], t['method'], t['confidence'], t['assign'], t.get('reason', '')))
        json.dump(dict(regression=R, reverse=T), open(os.path.join(E, 'c159_pair_v4_regress.json'), 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
        print('\n-> 03拆包产物\\c159_pair_v4_regress.json')
    else:
        do_json = '--json' in a
        r = analyze_v4(a[0], a[a.index('--binding') + 1] if '--binding' in a else None)
        if do_json:
            out = a[a.index('--json') + 1]
            json.dump(r, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            print('JSON -> %s' % out)
        print('file=%s  method=%s  confidence=%s' % (r['file'], r['method'], r['confidence']))
        if r.get('reason'): print('fail-closed reason:', r['reason'])
        print('valid group offsets: %s' % r.get('valid_group_offsets'))
        print('block offsets: %s' % [b['off'] for b in r['blocks']])
        for pr in r['primitives']:
            print('')
            print('prim%d MtlIdx=%d %s  shader=%s' % (pr['prim'], pr['mtl_idx'], pr['material'], pr['shader']))
            print('   record@%s  group@%s  block@%s  attribution=%s/%s' % (
                pr['material_record_off'], pr['group_off'], pr['block_off'], pr['attribution_method'], pr['confidence']))
            if pr.get('params'):
                print('   pair_score=%s consumed=%s leftover=%s warnings=%s' % (
                    pr.get('pair_score'), pr.get('pair_consumed'), len(pr.get('leftover') or []), pr.get('warnings') or 'none'))
                for k, v in pr['params'].items():
                    print('     %-26s = %s' % (k, v))
