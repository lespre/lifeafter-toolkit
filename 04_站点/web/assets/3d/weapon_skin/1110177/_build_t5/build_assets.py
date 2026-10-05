# -*- coding: utf-8 -*-
"""T5 build：为 1110177 极光剑 (skin_2003_029) 产出与 1110171 同构的查看器资产。

写作用域：仅 .../assets/3d/weapon_skin/1110177/ 内（本脚本自建于 _build_t5/）。
源（只读）：E:\\la拆包项目\\03_执行\\20_提取\\weapon\\{003994..003996, 004009..004013}
          + 1110171/src_cube/{qiangpi,car_studio01}.dds（= common\\env_map\\*.cube，同逻辑路径）

槽位判定依据（见 _t5_decode_stats.json / _t5_rule_check.json）：
  · c159(003996.c159) 内每材质路径块 → 槽名↔逻辑名（源文件直读）
  · 集群贴图组顺序 b_m,s_m,a,n,m（由 1110171 两个组的 ground truth 实证）
  · 内容签名与 1110171 ground-truth 对齐（_t5_decode_stats.json）
"""
import os, sys, json, shutil, hashlib, io
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SKIN = os.path.dirname(HERE)                      # .../1110177
TOOLS = r'E:\la拆包项目\01_工具\工具库\02_图文音频渲染\皮肤链与渲染'
sys.path.insert(0, TOOLS)
import dds_rgba_canonical as CAN
import export_glb as EG

WDDS = r'E:\la拆包项目\03_执行\\20_提取\weapon'
S171 = r'E:\la拆包项目\04_站点\\web\assets\3d\weapon_skin\1110171'
MESH = os.path.join(WDDS, '003995.mesh')

# 集群组 004009..004013 → 槽职责（顺序规则 b_m,s_m,a,n,m + 内容签名双重印证）
GRP = {'4009': 'b_m', '4010': 's_m', '4011': 'a', '4012': 'n', '4013': 'm'}
SRC_TEX = {  # 本地 png 名 ← dds idx
    '029_a.png': '004011', '029_m.png': '004013', '029_n.png': '004012',
    '029_b_m.png': '004009', '029_s_m.png': '004010',
}


def sha256f(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def decode(idx):
    u8, prov = CAN.decode_dds_rgba_u8(os.path.join(WDDS, idx + '.dds'), verify_oiio=False)
    return u8, prov


def save(u8, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    Image.fromarray(u8, 'RGBA').save(path)
    return sha256f(path)


def decode_cube_legacy(path):
    d = open(path, 'rb').read()
    hh = int.from_bytes(d[12:16], 'little'); ww = int.from_bytes(d[16:20], 'little')
    caps2 = int.from_bytes(d[112:116], 'little')
    faces, pos = [], 128
    for fi in range(6):
        m0 = np.frombuffer(d, dtype=np.uint8, count=ww * hh * 4, offset=pos).reshape(hh, ww, 4)
        faces.append(m0[:, :, [2, 1, 0, 3]].copy()); pos += 0  # advance below
        w, h, sz = ww, hh, 0
        while w >= 1 and h >= 1:
            sz += w * h * 4; w //= 2; h //= 2
        pos = 128 + (fi + 1) * sz
    return faces


def main():
    rep = {'skin_id': '1110177', 'assets': {}, 'slots': {}, 'leftovers': []}
    texdir = os.path.join(SKIN, 'src_tex')
    cubedir = os.path.join(SKIN, 'src_cube')

    # ---------- 1. src_tex ----------
    got = {}
    for png, idx in SRC_TEX.items():
        u8, prov = decode(idx)
        p = os.path.join(texdir, png)
        got[png] = {'src_dds': idx + '.dds', 'sha256': save(u8, p), 'w': u8.shape[1], 'h': u8.shape[0],
                    'dds_sha256': prov['dds_sha256'], 'canonical_pixel_sha256': prov['canonical_pixel_sha256'],
                    'decoder': prov['decoder'], 'swizzle': prov['applied_swizzle'], 'fmt': prov['fmt']}
        print('src_tex/%-14s <- %s  %s  sha=%s' % (png, idx + '.dds', u8.shape[:2], got[png]['sha256'][:16]))

    # param_repack: G<-m.R(roughness) B<-m.G(metalness) R<-m.R A<-255（与 1110171 既有产物逐字节同规则）
    m = np.asarray(Image.open(os.path.join(texdir, '029_m.png')).convert('RGBA')).astype(np.uint8)
    out = np.zeros_like(m)
    out[:, :, 0] = m[:, :, 0]; out[:, :, 1] = m[:, :, 0]; out[:, :, 2] = m[:, :, 1]; out[:, :, 3] = 255
    got['param_repack_029.png'] = {'rule': 'R<-m.R, G<-m.R(roughness), B<-m.G(metalness), A<-255',
                                   'derived_from': '029_m.png', 'sha256': save(out, os.path.join(texdir, 'param_repack_029.png'))}
    print('src_tex/param_repack_029.png  sha=%s' % got['param_repack_029.png']['sha256'][:16])

    # rough_repack: G<-a.A, R/B/A<-255（与 1110171 既有产物逐字节同规则）
    a = np.asarray(Image.open(os.path.join(texdir, '029_a.png')).convert('RGBA')).astype(np.uint8)
    r2 = np.zeros_like(a); r2[:, :, 0] = 255; r2[:, :, 1] = a[:, :, 3]; r2[:, :, 2] = 255; r2[:, :, 3] = 255
    got['rough_repack_029.png'] = {'rule': 'G<-a.A(Roughness=Ta), R/B/A<-255', 'derived_from': '029_a.png',
                                   'sha256': save(r2, os.path.join(texdir, 'rough_repack_029.png'))}
    print('src_tex/rough_repack_029.png  sha=%s' % got['rough_repack_029.png']['sha256'][:16])
    rep['assets']['src_tex'] = got

    # ---------- 2. src_cube ----------
    cub = {}
    os.makedirs(os.path.join(cubedir, 'faces'), exist_ok=True)
    for name in ('qiangpi', 'car_studio01'):
        src = os.path.join(S171, 'src_cube', name + '.dds')
        dst = os.path.join(cubedir, name + '.dds')
        shutil.copyfile(src, dst)
        faces = decode_cube_legacy(dst)
        fsha = []
        for fi, f in enumerate(faces):
            fp = os.path.join(cubedir, 'faces', '%s_f%d_m0.png' % (name, fi))
            Image.fromarray(f, 'RGBA').save(fp)
            fsha.append(sha256f(fp))
        cub[name] = {'dds': name + '.dds', 'dds_sha256': sha256f(dst), 'faces_sha256': fsha,
                     'logical': 'common\\env_map\\%s.cube' % name,
                     'evidence': 'common\\env_map\\%s.cube（与 1110171 同逻辑路径的同一 cube）；六面像素与 1110171 既有面逐字节一致（_t5_rule_check.json）' % name}
        print('src_cube/%s.dds + 6 faces  ok' % name)
    cub['fashion_qiangpi'] = {'state': 'missing',
                              'logical': 'common\\env_map\\fashion_qiangpi.cube',
                              'reason': '本地未定位该 cube 的解包条目；禁止用 qiangpi/car_studio01 顶替 → prim2 的 t_custom_ibl 记 missing（fail-closed，envMapIntensity=0）'}
    rep['assets']['src_cube'] = cub

    # ---------- 3. dual.glb ----------
    texmap = {"sets": {
        "skin_2003_029_blade": {"a": os.path.join(texdir, '029_a.png'), "n": os.path.join(texdir, '029_n.png'),
                                "m": os.path.join(texdir, '029_m.png'), "s_m": os.path.join(texdir, '029_s_m.png'),
                                "sources": {"a": "004011.dds", "n": "004012.dds", "m": "004013.dds", "s_m": "004010.dds"}},
        "skin_2003_029_crystal": {"a": os.path.join(texdir, '029_b_m.png'), "n": os.path.join(texdir, '029_n.png'),
                                  "sources": {"a": "004009.dds", "n": "004012.dds"}}}}
    tmp = os.path.join(HERE, 'texmap_029_glb.json')
    json.dump(texmap, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    glb = os.path.join(SKIN, 'dual.glb')
    r = EG.build_glb(MESH, tmp, ['skin_2003_029_blade', 'skin_2003_029_crystal'], glb,
                     label='skin_2003_029', center=True,
                     submap=['skin_2003_029_blade', 'skin_2003_029_crystal', 'skin_2003_029_crystal'])
    rep['assets']['dual.glb'] = {'file': 'dual.glb', 'sha256': sha256f(glb), 'size': os.path.getsize(glb),
                                 'vertices': r['vertices'], 'faces': r['faces'], 'prims_meta': r['prims_meta'],
                                 'builder': 'export_glb.py（POSITION/NORMAL/TEXCOORD_0 与源 .mesh 一致，未导出 TANGENT）',
                                 'mesh': '003995.mesh', 'mesh_sha16': hashlib.sha256(open(MESH, 'rb').read()).hexdigest()[:16],
                                 'submap': '0->blade, 1,2->crystal（显式指定，非按名相似推断）'}
    print('dual.glb  %d B  v=%d f=%d prims=%s' % (os.path.getsize(glb), r['vertices'], r['faces'],
                                                  [p['material'] for p in r['prims_meta']]))
    json.dump(rep, open(os.path.join(HERE, '_t5_build_assets.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('[saved] _t5_build_assets.json')


if __name__ == '__main__':
    main()
