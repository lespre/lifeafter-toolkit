# -*- coding: utf-8 -*-
"""零依赖 GLB (glTF 2.0) 导出器 — LifeAfter 武器皮肤交付用
输入: <mesh> <texmap.json> <set名,逗号分隔> <out.glb> [--label] [--center] [--submap a,b,c]
- POSITION/NORMAL/TEXCOORD_0/indices(u32), 每子网格一个 primitive
- 材质: baseColorTexture=a / normalTexture=n / metallicRoughnessTexture=m(金属度在 G, 粗糙度在 R)
- 忠实记录: 源法线为网格流(u16×3), 不重算; 切线/手性 unresolved => 不导出 TANGENT
"""
import os, sys, json, struct, base64, hashlib
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mesh_parse2 as MP


def _png_bytes(path, mode='RGBA'):
    im = Image.open(path)
    if im.mode != mode:
        im = im.convert(mode)
    import io
    b = io.BytesIO(); im.save(b, format='PNG', optimize=True)
    return b.getvalue(), im.size


def _sha(b):
    return hashlib.sha256(b).hexdigest()[:16]


def build_glb(mesh_path, texmap_path, set_names, out_path, label='', center=False, submap=None):
    P, uv, idx, meta = MP.parse_mesh2(mesh_path)
    tv, tf = meta['tv'], meta['tf']
    d = open(mesh_path, 'rb').read()
    nrm_off = meta['dataoff'] + tv * 6
    nraw = np.frombuffer(d, dtype='<u2', count=tv * 3, offset=nrm_off).reshape(-1, 3).astype(np.float32)
    N = nraw / 65535.0 * 2.0 - 1.0
    N /= np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-9)

    tm = json.load(open(texmap_path, encoding='utf-8'))['sets']
    sets = [tm[s] for s in set_names]
    sub_off = meta['sub_offsets']
    # 面→子网格归属（按首顶点）
    face_sub = np.zeros(tf, np.int32)
    for si, (a, b) in enumerate(sub_off):
        m = (idx[:, 0] >= a) & (idx[:, 0] < b)
        face_sub[m] = si

    images, textures, materials, prims = [], [], [], []
    bin_parts = []          # (bytes)
    accessors = []
    bufferviews = []
    cur_off = 0

    def add_view(data, target=None):
        nonlocal cur_off
        pad = (-len(data)) % 4
        blob = data + b'\x00' * pad
        bufferviews.append(dict(buffer=0, byteOffset=cur_off, byteLength=len(data), **({'target': target} if target else {})))
        bin_parts.append(blob)
        cur_off += len(blob)
        return len(bufferviews) - 1

    def add_acc(arr, comp_type, type_str, target, vmin=None, vmax=None):
        bv = add_view(np.ascontiguousarray(arr).tobytes(), target)
        n = len(arr)
        acc = dict(bufferView=bv, componentType=comp_type, count=n, type=type_str)
        if vmin is not None:
            acc['min'] = [float(x) for x in vmin]
            acc['max'] = [float(x) for x in vmax]
        accessors.append(acc)
        return len(accessors) - 1

    # 顶点属性（全网格一次，按子网格切 indices）
    pos_f = np.asarray(P, np.float32)
    _ctr = None
    if center:
        _ctr = (pos_f.min(0) + pos_f.max(0)) / 2.0
        pos_f = pos_f - _ctr   # 纯平移：按交付约定使模型以原点为中心（provenance 记录）
    uv_f = np.asarray(uv, np.float32)
    nrm_f = N.astype(np.float32)
    a_pos = add_acc(pos_f, 5126, 'VEC3', 34962, pos_f.min(0), pos_f.max(0))
    a_nrm = add_acc(nrm_f, 5126, 'VEC3', 34962)
    a_uv = add_acc(uv_f, 5126, 'VEC2', 34962)

    # 每个 set 的贴图
    set_tex = {}
    for si, s in enumerate(sets):
        ent = {}
        for slot, key in (('a', 'a'), ('n', 'n'), ('m', 'm')):
            fp = s.get(key)
            if not fp or not os.path.exists(fp):
                continue
            if slot == 'm':
                # glTF metallicRoughness: G=粗糙度, B=金属度;
                # 源 ParamMap(canonical RGBA): R=粗糙度(ParamMap.x), G=金属度(ParamMap.y)
                # => 纯格式级通道重排(数值不变, 不改色), provenance 记录
                src = np.asarray(Image.open(fp).convert('RGBA'), np.uint8)
                mr = np.empty_like(src)
                mr[..., 0] = 255
                mr[..., 1] = src[..., 0]   # roughness <- source R
                mr[..., 2] = src[..., 1]   # metallic  <- source G
                mr[..., 3] = 255
                import io
                b = io.BytesIO(); Image.fromarray(mr, 'RGBA').save(b, format='PNG', optimize=True)
                pb, size = b.getvalue(), (src.shape[1], src.shape[0])
            else:
                pb, size = _png_bytes(fp)
            images.append(dict(bufferView=add_view(pb), mimeType='image/png', name='%s_%s' % (set_names[si], key)))
            textures.append(dict(source=len(images) - 1, sampler=0))
            ent[slot] = len(textures) - 1
            ent[slot + '_meta'] = dict(path=fp.replace('\\', '/'), sha256_16=_sha(pb), w=size[0], h=size[1],
                                       channel_repack=('glTF MR: G=roughness(source R), B=metallic(source G); 数值不变'
                                                       if slot == 'm' else None))
        set_tex[set_names[si]] = ent
        mat = dict(name='MAT_%s' % set_names[si], pbrMetallicRoughness=dict(
            metallicFactor=1.0, roughnessFactor=1.0,
            baseColorFactor=[1, 1, 1, 1]), doubleSided=True)
        if 'a' in ent:
            mat['pbrMetallicRoughness']['baseColorTexture'] = dict(index=ent['a'])
        if 'm' in ent:
            mat['pbrMetallicRoughness']['metallicRoughnessTexture'] = dict(index=ent['m'])
        if 'n' in ent:
            mat['normalTexture'] = dict(index=ent['n'])
        mat['extras'] = dict(source_slots={k: ent[k + '_meta'] for k in ('a', 'n', 'm') if k + '_meta' in ent},
                             note='metallicRoughness 来自 ParamMap: 源 R=粗糙度(ParamMap.x), G=金属度(ParamMap.y); '
                                  '导出时按 glTF 规范做纯格式级通道重排(G=roughness,B=metallic), 数值未变')
        materials.append(mat)
    mat_index = {s: i for i, s in enumerate(set_names)}

    # 子网格 → 材质
    n_sub = len(sub_off)
    sub_mat = []
    for si in range(n_sub):
        if submap:
            # 显式指定：--submap a,b,c → 第 i 个子网格用哪个材质集（'.' = 第一个集）
            name = submap[si] if si < len(submap) else submap[-1]
            sub_mat.append(mat_index[name] if name in mat_index else 0)
        elif len(set_names) == 1:
            sub_mat.append(0)
        else:
            # 双枪: 前 n_sub-3 个子网格 = 012(4), 后 3 = 010(3)  —— 由 001264 组成实证
            sub_mat.append(mat_index[set_names[0]] if si >= n_sub - 3 else mat_index[set_names[-1]])
    prims_meta = []
    for si in range(n_sub):
        fm = np.nonzero(face_sub == si)[0]
        if len(fm) == 0:
            continue
        ind = idx[fm].reshape(-1).astype(np.uint32)
        a_idx = add_acc(ind, 5125, 'SCALAR', 34963)
        prims.append(dict(attributes=dict(POSITION=a_pos, NORMAL=a_nrm, TEXCOORD_0=a_uv),
                          indices=a_idx, material=sub_mat[si]))
        prims_meta.append(dict(submesh=si, vrange=list(sub_off[si]), faces=int(len(fm)), material=set_names[min(sub_mat[si], len(set_names) - 1)]))

    gltf = dict(
        asset=dict(version='2.0', generator='la-skin-glb-exporter v1 (source-faithful, no tangent recompute)'),
        scene=0,
        scenes=[dict(nodes=[0])],
        nodes=[dict(mesh=0, name=label or os.path.basename(mesh_path))],
        meshes=[dict(primitives=prims, name=label)],
        materials=materials, textures=textures, images=images,
        samplers=[dict(magFilter=9729, minFilter=9987, wrapS=10497, wrapT=10497)],
        accessors=accessors, bufferViews=bufferviews,
        buffers=[dict(byteLength=cur_off)],
        extras=dict(source_mesh=str(mesh_path).replace('\\', '/'),
                    mesh_sha256_16=hashlib.sha256(d).hexdigest()[:16],
                    vertices=int(tv), faces=int(tf), submeshes=prims_meta,
                    center_offset=([float(x) for x in _ctr] if _ctr is not None else None),
                    center_note=('已按交付约定平移使 bbox 中心=原点（纯平移，未改朝向/尺度）' if _ctr is not None else None),
                    normal_source='mesh stream u16x3 /65535*2-1, normalize (source-faithful)',
                    tangent='not exported (source tangent stream semantics unresolved)',
                    uv='f16x2 source',
                    texmap=str(texmap_path).replace('\\', '/'), sets=set_names)
    )
    js = json.dumps(gltf, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    js += b' ' * ((-len(js)) % 4)
    binb = b''.join(bin_parts)
    total = 12 + 8 + len(js) + 8 + len(binb)
    with open(out_path, 'wb') as f:
        f.write(struct.pack('<III', 0x46546C67, 2, total))
        f.write(struct.pack('<II', len(js), 0x4E4F534A)); f.write(js)
        f.write(struct.pack('<II', len(binb), 0x004E4942)); f.write(binb)
    return dict(out=out_path, size=os.path.getsize(out_path), vertices=int(tv), faces=int(tf),
                submeshes=len(prims), images=len(images), materials=len(materials),
                prims_meta=prims_meta)


if __name__ == '__main__':
    a = sys.argv[1:]
    lab = ''
    if '--label' in a:
        i = a.index('--label'); lab = a[i + 1]; del a[i:i + 2]
    sm = None
    if '--submap' in a:
        i = a.index('--submap'); sm = a[i + 1].split(','); del a[i:i + 2]
    mesh, texmap, sets, out = a[0], a[1], a[2], a[3]
    r = build_glb(mesh, texmap, sets.split(','), out, lab, center=('--center' in a), submap=sm)
    print(json.dumps(r, ensure_ascii=False, indent=1))
