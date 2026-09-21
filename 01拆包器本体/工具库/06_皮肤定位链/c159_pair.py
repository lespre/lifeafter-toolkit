# -*- coding: utf-8 -*-
"""c159_pair.py v3 — NeoX .c159 材质解析器（通用版, 无固定偏移/固定组号/固定块数/固定文件名）

格式模型（实证 029 双 LOD + 028 交叉; 全部按结构自动识别）:
  · 名字表: [组件名...][参数名(t_*, u_*)] — 起点=首个 *AnimParam 串, 组件段止于 t_basecolor, 参数段止于首个路径/材质名类串
  · 槽位引用组: u16 列表(任意字节对齐), 值域 ≤ 名字表最大索引; 以 TransparentMode 槽位值分段; 纯零段剔除
  · 数值块: [magic 01 00 01 13][type][payload] 条目(type: 01str/02i32/05f32/06arr) 的连续簇(间隔<100B)
  · 配对: 组内『非字符串槽』序列 ↔ 数值块条目 正向 1:1; 评分 = 颜色名↔数组/标量名↔标量
  · 材料归属: 材料名(skim_*)顺序; 与块配对成功的组按文件序 ↔ 晶体材料序; 其余组按序补位

用法:
  python c159_pair.py <file.c159> [--binding <file.c159>] [--json out.json]
库:
  analyze(path) -> dict; load_asset_materials(mtl_path[, bind_path]) -> {sub: {...}}, meta
  parse_binding(path) -> {sub_index: material_name}
"""
import sys, struct, json, re, os

MAGIC = b'\x01\x00\x01\x13'

# ---------- 名字表 ----------
def read_names(b):
    strs = [(m.start(), m.group().decode('latin1')) for m in re.finditer(rb'[\x20-\x7e]{2,}', b)]
    i0 = None
    for k, (o, s) in enumerate(strs):
        if s.lstrip('0123456789') == 'AnimParam':
            i0 = k; break
    if i0 is None:
        raise ValueError('名字表: 未找到 AnimParam 起点')
    comp = []
    j = i0
    while j < len(strs) and strs[j][1] != 't_basecolor':
        comp.append(strs[j][1]); j += 1
    if j >= len(strs):
        # 兼容变体: 无 t_basecolor 时, 参数段起点 = 首个 t_/u_ 开头串
        j = i0
        while j < len(strs):
            s = strs[j][1]
            if s.startswith(('t_', 'u_')):
                break
            comp.append(s); j += 1
        if j >= len(strs):
            if any(s == 'Material' for _, s in strs):
                # 无参数表的材质文件(如仅宏/引用) — 结构化空参数表返回
                return dict(comp=comp, params=[], core=[], full=comp, idx={n: k for k, n in enumerate(comp)},
                            max_index=len(comp) - 1, strs=strs, no_param_table=True)
            raise ValueError('名字表: 未找到参数段(t_/u_ 或 t_basecolor) — 可能不是材质文件')
    params = []
    seen_version = False
    while j < len(strs):
        s = strs[j][1]
        if re.search(r'[\\]|::|\.fx$', s) or s.startswith(('skim', 'skin_', 'mm', 'shader')):
            break
        if s == 'Version':
            params.append(s); break
        params.append(s); j += 1
    # 参数核(t_/u_) vs RenderStates(names 至 Version)
    core = []
    for s in params:
        if s == 'AlphaRef': break
        core.append(s)
    full = comp + params
    idx = {}
    for k, n in enumerate(full):
        idx.setdefault(n, k)   # 取首个索引(TransparentMode: comp 位优先)
    max_index = (len(comp) + len(core) - 1) if core else (len(full) - 1)
    return dict(comp=comp, params=params, core=core, full=full, idx=idx,
                max_index=max_index, strs=strs)

# ---------- 条目 ----------
def parse_entries(b, lo=0, hi=None):
    hi = hi if hi is not None else len(b)
    out, i = [], lo
    while i < hi - 6:
        j = b.find(MAGIC, i, hi)
        if j < 0: break
        t = b[j + 4]; st = j + 5
        try:
            if t == 0x01:
                k = b.find(b'\x00', st, hi)
                if k < 0: break
                s = b[st:k].decode('utf-8', 'replace')
                if all(32 <= ord(c) < 127 for c in s):
                    out.append(dict(off=j, type='str', raw=b[st:k].hex(), value=s)); i = k + 1
                else: i = j + 5
            elif t == 0x02:
                out.append(dict(off=j, type='i32', raw=b[st:st+4].hex(), value=struct.unpack_from('<i', b, st)[0])); i = st + 4
            elif t == 0x05:
                out.append(dict(off=j, type='f32', raw=b[st:st+4].hex(), value=round(struct.unpack_from('<f', b, st)[0], 5))); i = st + 4
            elif t == 0x06:
                cnt = struct.unpack_from('<I', b, st)[0]
                if cnt <= 64:
                    vs = [round(v, 5) for v in struct.unpack_from('<%df' % cnt, b, st + 4)]
                    out.append(dict(off=j, type='f32[%d]' % cnt, raw=b[st:st+4+cnt*4].hex(), value=vs)); i = st + 4 + cnt * 4
                else: i = j + 5
            else: i = j + 5
        except Exception: i = j + 5
    return out

# ---------- 槽位组(双对齐) ----------
def find_groups(b, names):
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
    # 去重(同一起点/同样列表)
    seen = set(); uniq = []
    for align, st, v in runs:
        key = (align, st)
        if key in seen: continue
        seen.add(key); uniq.append(dict(align=align, st=st, vals=v))
    # 纯零段剔除 (max<3) + 垃圾段过滤: 至少 2 个 >=3 的值 且 distinct>=3
    uniq = [r for r in uniq if max(r['vals']) >= 3
            and sum(1 for v in r['vals'] if v >= 3) >= 2 and len(set(r['vals'])) >= 3]
    # 按 TransparentMode 分段（保留来源 align，供下面的跨对齐去重用）
    groups = []
    for r in uniq:
        cur = []
        for v in r['vals']:
            cur.append(v)
            if v == tm:
                if len(cur) >= 6: groups.append((r['align'], cur))
                cur = []
        if len(cur) >= 6: groups.append((r['align'], cur))   # 未以 TM 结尾的残段
    # ★ 修复（2026-09-18，C159PARSE）：原实现在**同一对齐内**也删掉连续重复组，
    #   但同一文件里**两份插槽列表完全相同的材料是合法的**：双枪 001265.c159 的
    #   crystal012 材料有两份（都 8 个字符串槽），实测被误删 1 组 ⇒ 材料数 7→6、
    #   后序材料整体错位（001265 余 8 串；1110024 余 4、1110129 余 11、1110145 余 6、1110165 余 5）。
    #   现只在**跨对齐**(align 0↔1)之间去重——那才是"双字节对齐各扫一遍"产生的重复；
    #   同一对齐内的连续重复一律保留。API 不变（仍返回 list[list[int]]）。
    out = []
    prev_align = None
    for align, g in groups:
        if out and g == out[-1] and align != prev_align: continue
        out.append(g); prev_align = align
    return out

# ---------- 数值块 ----------
def find_blocks(entries):
    nums = [e for e in entries if e['type'].startswith(('f32', 'i32'))]
    clusters, cur = [], []
    for e in nums:
        if cur and e['off'] - cur[-1]['off'] > 100:
            clusters.append(cur); cur = []
        cur.append(e)
    if cur: clusters.append(cur)
    return [c for c in clusters if len(c) >= 6]

# ---------- 配对 ----------
def _slot_name(names, v):
    return names['full'][v] if 0 <= v < len(names['full']) else '?'

def _is_str_slot(names, v):
    nm = _slot_name(names, v)
    if nm.startswith('Macro'): return True
    if nm in ('Tex0', 'DetailMap', 'NormalMap', 'ParamMap', 'TransparentMode'): return True
    if nm.startswith('t_'): return True
    return False

def _kind(nm):
    if 'color' in nm: return 'color'
    if nm.startswith('u_'): return 'scalar'
    return 'other'

def pair_block(names, group, block):
    slots = [v for v in group if not _is_str_slot(names, v)]
    rows, ei, score, warn = [], 0, 0, []
    for v in slots:
        nm = _slot_name(names, v)
        if ei < len(block):
            e = block[ei]
            got = 'color' if e['type'].startswith('f32[') else ('scalar' if e['type'] in ('f32', 'i32') else 'other')
            exp = _kind(nm)
            if exp == got: score += 2
            elif {exp, got} == {'scalar', 'other'}: score += 1
            else: score -= 2
            rows.append(dict(slot=v, name=nm, type=e['type'], off=e['off'], raw=e['raw'], value=e['value']))
            ei += 1
        else:
            rows.append(dict(slot=v, name=nm, type=None, off=None, raw=None, value=None, note='未序列化/默认'))
            warn.append('slot %d(%s) 无对应值' % (v, nm))
    leftover = [dict(off=e['off'], type=e['type'], value=e['value']) for e in block[ei:]]
    if leftover: warn.append('块尾有 %d 条未消费条目' % len(leftover))
    return dict(rows=rows, consumed=ei, score=score, leftover=leftover, warnings=warn)

def match_all(names, groups, blocks):
    cand = []
    for gi, g in enumerate(groups):
        for bi, blk in enumerate(blocks):
            p = pair_block(names, g, blk)
            compat = 3 if len(p['rows']) == len(blk) else 0
            cand.append((p['score'] + compat, gi, bi, p))
    cand.sort(key=lambda x: (-x[0], x[1], x[2]))
    used_g, used_b, pairs = set(), set(), []
    for sc, gi, bi, p in cand:
        if gi in used_g or bi in used_b: continue
        n = min(len(p['rows']), len(blocks[bi]))
        if p['score'] < n or abs(len(p['rows']) - len(blocks[bi])) > max(2, int(0.15 * n)): continue
        pairs.append(dict(group=gi, block=bi, score=sc, pairing=p))
        used_g.add(gi); used_b.add(bi)
    return pairs, sorted(used_g), sorted(used_b)

# ---------- 材料/绑定 ----------
def read_materials(b):
    mats = []
    for m in re.finditer(rb'[\x20-\x7e]{2,}', b):
        s = m.group().decode('latin1')
        if re.match(r'^(?:skim|skin)_[\w]+$', s):
            if s not in mats: mats.append(s)
    shaders = [m.group().decode('latin1') for m in re.finditer(rb'shader\\[\w\.]+::TShader', b)]
    return mats, shaders

def parse_binding(path):
    b = open(path, 'rb').read()
    subs = []
    for m in re.finditer(rb'[\x20-\x7e]{2,}', b):
        s = m.group().decode('latin1')
        mm = re.match(r'^mm?skin_[\w]+_(\d+)$', s) or re.match(r'^skin_[\w]+_(\d+)$', s)
        if mm:
            name = s[2:] if s.startswith('mm') else s
            subs.append((int(mm.group(1)), name))
    subs.sort()
    return {i: n for i, n in subs}

# ---------- 总分析 ----------
def analyze(path):
    b = open(path, 'rb').read()
    names = read_names(b)
    entries = parse_entries(b)
    groups = find_groups(b, names)
    blocks = find_blocks(entries)
    pairs, used_g, used_b = match_all(names, groups, blocks)
    mats, shaders = read_materials(b)
    return dict(file=os.path.abspath(path), size=len(b), names=names, entries=entries,
                groups=groups, blocks=blocks, pairs=pairs, used_groups=used_g, used_blocks=used_b,
                materials=mats, shaders=shaders)

def load_asset_materials(mtl_path, bind_path=None):
    """返回 ({sub_idx: {material, params:{name:value}, group, block}}, meta)"""
    A = analyze(mtl_path)
    def key_of(nm):
        m = re.search(r'(\d+_\d+)_(\d+)$', nm)
        return (m.group(1), int(m.group(2))) if m else (nm, -1)
    mats = A['materials']
    if bind_path is None:
        d = os.path.dirname(os.path.abspath(mtl_path))
        base = os.path.splitext(os.path.basename(mtl_path))[0]
        mids = {key_of(m)[0] for m in mats}
        try: n0 = int(base)
        except ValueError: n0 = None
        cands = []
        if n0 is not None:
            cands += [os.path.join(d, '%06d.c159' % (n0 + k)) for k in (1, 2, 3)]
        if d and os.path.isdir(d):
            for f in sorted(os.listdir(d)):
                if f.endswith('.c159') and os.path.abspath(os.path.join(d, f)) != os.path.abspath(mtl_path):
                    cands.append(os.path.join(d, f))
        for c in cands:
            if os.path.exists(c):
                try: subs = parse_binding(c)
                except Exception: continue
                if len(subs) >= 2 and {key_of(v)[0] for v in subs.values()} == mids:
                    bind_path = c; break
    bind = parse_binding(bind_path) if bind_path else {}
    # 材料↔组: 已与块配对的组(按文件序) 对应 晶体材料(按材料序); 其余材料拿剩余的非晶体组
    paired_gi = [p['group'] for p in sorted(A['pairs'], key=lambda p: p['group'])]
    mats = A['materials']
    crystal_mats = [m for m, sh in zip(mats, A['shaders']) if 'crystal' in sh]
    attrib = {}
    for k, gi in enumerate(paired_gi):
        if k < len(crystal_mats):
            attrib[key_of(crystal_mats[k])] = gi
    used = set(attrib.values())
    leftovers = [i for i in range(len(A['groups'])) if i not in used and i not in A['used_groups']]
    plain_mats = [m for m in mats if m not in attrib]
    blocks_by_gi = {p['group']: p['block'] for p in A['pairs']}
    result = {}
    for si, mname in bind.items():
        gi = attrib.get(key_of(mname))
        out = dict(material=mname, group=gi, params={})
        if gi is not None and gi in blocks_by_gi:
            p = next(p for p in A['pairs'] if p['group'] == gi)
            for r in p['pairing']['rows']:
                if r.get('type') and r.get('value') is not None:
                    out['params'][r['name']] = r['value']
            out['block_off'] = A['blocks'][blocks_by_gi[gi]][0]['off']
        result[si] = out
    # 无绑定文件时: 按材料序/组序顺位
    if not bind:
        for si, mname in enumerate(mats):
            gi = attrib.get(key_of(mname))
            out = dict(material=mname, group=gi, params={})
            if gi is not None and gi in blocks_by_gi:
                p = next(p for p in A['pairs'] if p['group'] == gi)
                for r in p['pairing']['rows']:
                    if r.get('type') and r.get('value') is not None:
                        out['params'][r['name']] = r['value']
            result[si] = out
    meta = dict(mtl_file=A['file'], bind_file=os.path.abspath(bind_path) if bind_path else None,
                materials=mats, shaders=A['shaders'], crystal_mats=crystal_mats,
                groups_count=len(A['groups']), blocks_count=len(A['blocks']),
                attrib=attrib, leftover_groups=leftovers,
                block_shapes=[len(x) for x in A['blocks']], group_shapes=[len(g) for g in A['groups']])
    return result, meta

# ---------- CLI ----------
def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__); return
    path = args[0]
    bind = None
    if '--binding' in args:
        bind = args[args.index('--binding') + 1]
    A = analyze(path)
    print('== %s  %dB ==' % (A['file'], A['size']))
    print('组件(%d): %s' % (len(A['names']['comp']), A['names']['comp']))
    print('参数(%d): %s' % (len(A['names']['params']), A['names']['params']))
    print('材料: %s' % A['materials'])
    print('shader: %s' % A['shaders'])
    print('组数=%d 形%s' % (len(A['groups']), [len(g) for g in A['groups']]))
    print('块数=%d 形%s' % (len(A['blocks']), [len(x) for x in A['blocks']]))
    for p in A['pairs']:
        print('配对: 组%d(形%d) ↔ 块%d(%d条) 评分=%d' % (p['group'], len(A['groups'][p['group']]), p['block'], len(A['blocks'][p['block']]), p['score']))
        for r in p['pairing']['rows']:
            if r.get('type') and not r['type'].startswith('('):
                print('   slot %-3d %-26s %-8s off=%-5s = %s' % (r['slot'], r['name'], r['type'], r['off'], str(r['value'])[:60]))
        for w in p['pairing']['warnings']:
            print('   ⚠ %s' % w)
    if bind:
        print('绑定: %s -> %s' % (bind, parse_binding(bind)))
    if '--json' in args:
        out = args[args.index('--json') + 1]
        json.dump(A, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('JSON ->', out)

if __name__ == '__main__':
    main()
