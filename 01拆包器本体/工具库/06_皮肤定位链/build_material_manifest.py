# -*- coding: utf-8 -*-
"""统一材质清单 material_manifest.json —— 合并三段已有工具，不另写 c159 扫描器

链路:
  parse_bind(绑定 c159)      -> submesh -> MtlIdx -> 绑定材质名        [high]
  c159_pair.load_asset...    -> shader + 参数名/类型/值/字节偏移       [high(工具已验证)]
  material c159 字符串        -> 贴图槽名 -> 路径                       [heuristic]
  mesh sub 表                -> submesh -> index range / faces         [high]
  viewer.json                -> 晶体层近似参数                          [approximate]

每条边单独标 evidence，禁止整条写"权威链"。

用法: python build_material_manifest.py <bind.c159> <material.c159> <mesh> <out.json> [--skin 1110171] [--name 光影咏叹调]
"""
import sys, os, json, re, struct
WD = os.path.dirname(os.path.abspath(__file__))
if WD not in sys.path:
    sys.path.insert(0, WD)
import c159_pair  # noqa: E402


def mesh_subs(path):
    """网格 sub 表 -> 每个子网格的 index range（高可信：由 sub 表 vc/fc 累计推出）"""
    d = open(path, 'rb').read()
    for k in range(1, 12):
        off = 0x0E + 10 * k
        subs = [struct.unpack_from('<IIH', d, 0x0E + 10 * i) for i in range(k)]
        try:
            tv, tf = struct.unpack_from('<II', d, off + 2)
        except Exception:
            continue
        if sum(s[0] for s in subs) == tv and sum(s[1] for s in subs) == tf and 0 < tv < (1 << 22):
            vv = ff = 0
            out = []
            for i, (vc, fc, u) in enumerate(subs):
                out.append(dict(submesh=i, vrange=[vv, vv + vc], index_range=[ff * 3, (ff + fc) * 3],
                                faces=fc, vcount=vc, draw_group=u & 0xFF, sub_flag=hex(u)))
                vv += vc; ff += fc
            return out, dict(vertices=tv, faces=tf, submesh_count=k)
    return [], {}


def material_texture_slots(mtl_path):
    """材质文件里的 t_* 槽名 + 路径串（按文件出现序）。
    注意：槽名->路径的归属**未直证**（缺槽位引用组解析），标记 heuristic。"""
    d = open(mtl_path, 'rb').read()
    ss = [s.decode('latin1') for s in re.findall(rb'[\x20-\x7e]{4,}', d)]
    slots = [s for s in ss if s.startswith('t_')]
    paths = [s for s in ss if s.lower().endswith(('.tga', '.dds', '.cube'))]
    return slots, paths


def bind_by_record_order(path):
    """绑定 c159 的 SubMesh 记录**按数组顺序**就是 submesh 下标。
    单枪：顺序与材质名后缀一致（互为印证）；双枪：两族名后缀会相撞，必须用顺序。
    证据等级 medium-high（顺序与网格子网格构成互为印证：7 条 ↔ 012 枪 4 + 010 枪 3）"""
    b = open(path, 'rb').read()
    recs = []
    for m in re.finditer(rb'\x0a\x02(.{4})\x0c\x01([\x20-\x7e]+)\x00', b, re.S):
        idx = struct.unpack('<I', m.group(1))[0]
        nm = m.group(2).decode('latin1')
        if idx < 64 and 3 < len(nm) < 96:
            recs.append(dict(mtl_idx=idx, name=nm[2:] if nm.startswith('mm') else nm))
    return recs


def build(bind_p, mtl_p, mesh_p, skin=None, name=None):
    recs = bind_by_record_order(bind_p)                     # 按记录顺序 = submesh 序
    try:
        res = c159_pair.analyze(mtl_p)                     # 材质文件解析（首选）
    except Exception as _e:                                # 降级：结构不同（如 000654.c159）
        raw = open(mtl_p, 'rb').read()
        _mats = [(m.start(), m.group(1).decode('latin1'))
                 for m in re.finditer(rb'(Material_[\x20-\x7e]{1,80}?)\x00', raw)]
        _sh = [(m.start(), m.group(1).decode('latin1'))
               for m in re.finditer(rb'([A-Za-z0-9_]+\.fx)::TShader', raw)]
        _out = []
        for _pos, _nm in _mats:
            _nxt = [(sp, sn) for sp, sn in _sh if sp > _pos]
            _out.append(dict(name=_nm, shader=(min(_nxt)[1] if _nxt else None)))
        res = dict(materials=_out, shaders=[x['shader'] for x in _out], pairs=[],
                   _fallback='c159_pair.analyze 失败：%s' % _e,
                   _evidence='low（降级解析：材质名/着色器按文件内顺序提取；参数块 unresolved）')
    
    mats = res.get('materials') or []
    shaders = res.get('shaders') or []
    pairs = res.get('pairs') or []
    subs, mesh_meta = mesh_subs(mesh_p)
    slots, paths = material_texture_slots(mtl_p)

    # 复用工具的归属规则：配对成功的组（组号升序＝文件序）↔ 晶体材料（按材质序）
    pairs_sorted = sorted(pairs, key=lambda p: p.get('group', 0))
    crystal_mats = [i for i, sh in enumerate(shaders) if 'crystal' in (sh or '')]
    pair_of_mtl = {}
    for k, pr in enumerate(pairs_sorted):
        if k < len(crystal_mats):
            pair_of_mtl[crystal_mats[k]] = pr

    out = dict(skin_id=skin, name=name,
               files=dict(bind=os.path.basename(bind_p), material=os.path.basename(mtl_p), mesh=os.path.basename(mesh_p)),
               mesh_meta=mesh_meta, materials=[])
    for s in subs:
        si = s['submesh']
        rec = recs[si] if si < len(recs) else None
        mtl_name = rec['name'] if rec else None
        mi = rec['mtl_idx'] if rec else None
        pr = pair_of_mtl.get(mi) if mi is not None else None
        rows = []
        if pr:
            for r in pr['pairing']['rows']:
                rows.append(dict(name=r['name'], type=r['type'], value=r['value'],
                                 byte_offset=r['off'], raw=r['raw']))
        out['materials'].append(dict(
            submesh=si, index_range=s['index_range'], faces=s['faces'], vcount=s['vcount'],
            mtl_idx=mi, bind_material_name=mtl_name,
            material_file_index=mi,
            shader=shaders[mi] if (mi is not None and mi < len(shaders)) else None,
            texture_slot_names=slots,
            texture_paths=paths,
            source_params=rows,
            defaults=f"未覆写：材质 {mi} 无参数值块，走引擎默认 + ParamMap + IBL + shader 公式" if not rows else None,
            evidence=dict(
                submesh_index_range='high（mesh sub 表累计 vc/fc）',
                mtl_idx='high（绑定 c159 记录内 MtlIdx 字段直读）',
                mtl_idx_to_submesh='medium-high（绑定记录数组顺序 ↔ 网格子网格序；单枪与名后缀一致，双枪以两族构成印证）',
                bind_material_name='high（绑定 c159 记录内字符串）',
                material_file_index='medium（按材质表顺序对应 MtlIdx；槽位结构解析前不升 high）',
                shader='medium（按材质表顺序取 shaders[]；同上）',
                texture_slot_names='high（材质文件 t_* 槽名，文件内直读）',
                texture_paths='heuristic（路径串按文件出现序；槽名↔路径归属未直证）',
                source_params='high（c159_pair.py 槽位引用组解析，工具已验证）' if rows else 'n/a（无覆写块）',
            )))
    return out


if __name__ == '__main__':
    a = sys.argv[1:]
    skin = a[a.index('--skin') + 1] if '--skin' in a else None
    name = a[a.index('--name') + 1] if '--name' in a else None
    m = build(a[0], a[1], a[2], skin, name)
    json.dump(m, open(a[3], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('SubMt | idx范围 | faces | MtlIdx | 绑定材质名 | shader | 源参数条数 | 未覆写?')
    for x in m['materials']:
        print('  %d | %s | %d | %s | %-18s | %-16s | %d | %s' % (
            x['submesh'], x['index_range'], x['faces'], x['mtl_idx'], x['bind_material_name'],
            (x['shader'] or '-').split('\\')[-1], len(x['source_params']),
            'YES' if x['defaults'] else ''))
    print('->', a[3])
