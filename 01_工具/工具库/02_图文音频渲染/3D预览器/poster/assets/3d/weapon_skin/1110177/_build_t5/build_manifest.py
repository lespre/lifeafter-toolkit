# -*- coding: utf-8 -*-
"""T5 build2：生成 1110177 的 neox_material.json / viewer.json / provenance.json。

槽位绑定三条依据（每条都能被复核）：
  A) c159(003996.c159) 每个材质的路径块 → 槽名↔逻辑名（源文件直读，见 c159_029_pair.json L649-765）
  B) 集群贴图组 004009..004013 的顺序 b_m,s_m,a,n,m —— 该顺序由 1110171 两个组的
     ground truth（gpk_raw_8u32.json 的 label）实证；029 组 5 张的顺序与角色数完全同构
  C) 内容签名与 1110171 ground-truth 对齐（_t5_decode_stats.json）：
       b_m: mean[211,179,141] std 高 / s_m: R 饱和 / a: B 恒 256 + 彩 / n: blue_dom 95 / m: G,B 恒 256
缺的资源一律登记 missing，不顶替。
"""
import os, sys, json, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
SKIN = os.path.dirname(HERE)
WIKI = r'E:\la拆包项目\04_站点\\web'
WDDS = r'E:\la拆包项目\03_执行\\20_提取\weapon'
REL = 'assets/3d/weapon_skin/1110177'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest() if os.path.exists(p) else None


def T(logical, local, slot, cs, rule, evidence, conf, **extra):
    d = {'logical_path': logical, 'slot': slot, 'local_file': local, 'sha256': sha(os.path.join(SKIN, local)),
         'evidence': evidence, 'confidence': conf, 'classification_rule': rule, 'color_space': cs}
    d.update(extra)
    return d


def MISS(logical, slot):
    return {'logical_path': logical, 'slot': slot, 'local_file': None, 'sha256': None,
            'evidence': 'c159 材质路径块声明存在，但本地未定位到解包条目',
            'confidence': 'none', 'state': 'missing',
            'reason': '未在 03_执行\\20_提取/weapon 与本项目既有产物中定位到该逻辑路径对应的解包文件；'
                      '按纪律不顶替、不猜文件名，登记 missing（viewer 走 fail-closed / 记入 pending_layers）'}


def main():
    glb = os.path.join(SKIN, 'dual.glb')
    prims = [
        {'prim': 0, 'mtl_idx': 0, 'material': 'skin_2003_029_0', 'chain_material_raw': 'mmskin_2003_029_0',
         'glb_material': 'skin_2003_029_blade', 'shader': r'shader\pbr_default.fx::TShader',
         'shader_kind': 'weapon',
         'shader_kind_basis': '源 shader=pbr_default（不透明金属基底）→ viewer 的 weapon 分支；'
                              '与 1110171 prim0（pbr_weapon）同分支；非 pbr_crystal 故不按晶体处理',
         'attribution': 'c159 路径块内 4 条路径直读 + 集群角色补齐 Tex0',
         'textures': {
             'Tex0': T(r'weapon\skin\skin_2003_029\textures\skin_2003_029001a.tga', 'src_tex/029_a.png', 'Tex0',
                       'ab_test', 'rule:001a.tga', 'c159 该材质基色路径 029001a.tga', 'high'),
             't_basecolor': T(r'weapon\skin\skin_2003_029\textures\skin_2003_029001a.tga', 'src_tex/029_a.png',
                              't_basecolor', 'ab_test', 'rule:001a.tga', 'c159 该材质基色路径 029001a.tga', 'high'),
             'ParamMap': T(r'weapon\skin\skin_2003_029\textures\skin_2003_029001m.tga', 'src_tex/029_m.png',
                           'ParamMap', 'linear', 'rule:001m.tga', 'c159 该材质 ParamMap 路径 Declared', 'high'),
             'NormalMap': T(r'weapon\skin\skin_2003_029\textures\skin_2003_029001n.tga', 'src_tex/029_n.png',
                            'NormalMap', 'linear', 'rule:001n.tga', 'c159 该材质法线路径声明', 'high'),
             't_custom_ibl': T(r'common\env_map\qiangpi.cube', 'src_cube/qiangpi.dds', 't_custom_ibl', 'linear',
                               r'rule:\.cube', 'c159 该材质 cube 路径声明；与 1110171 同一逻辑路径', 'high',
                               faces_glob='src_cube/faces/qiangpi_f{0..5}_m0.png',
                               dds_header='legacy DDS, B8G8R8A8_UNORM, 128x128, 6 faces, mips=8',
                               state='source_resource_verified', sampling='sampling_unresolved'),
             't_surfacemap': T(r'weapon\skin\skin_2003_029\textures\skin_2003_029001s_m.tga', 'src_tex/029_s_m.png',
                               't_surfacemap', 'linear', 'rule:001s_m.tga',
                               '集群 004010 内容签名为 s_m 角色；material0 路径块未声明该槽 → 仅登记资源，不参与渲染',
                               'candidate-high', viewer_usage='NOT_CONSUMED'),
         },
         'missing_required': []},
        {'prim': 1, 'mtl_idx': 1, 'material': 'skin_2003_029_1', 'chain_material_raw': 'mmskin_2003_029_1',
         'glb_material': 'skin_2003_029_crystal', 'shader': r'shader\pbr_crystal.fx::TShader',
         'shader_kind': 'crystal', 'attribution': 'c159 路径块 7 条路径直读（槽名↔逻辑名）',
         'textures': {
             'Tex0': T(r'weapon\skin\skin_2003_029\textures\skin_2003_029001b_m.tga', 'src_tex/029_b_m.png',
                       'Tex0', 'linear', 'rule:001b_m.tga', 'c159 该材质首路径 029001b_m.tga（掩码）', 'high'),
             't_basecolor': T(r'weapon\skin\skin_2003_029\textures\skin_2003_029001a.tga', 'src_tex/029_a.png',
                              't_basecolor', 'ab_test', 'rule:001a.tga', 'c159 该材质路径声明', 'high'),
             'NormalMap': T(r'weapon\skin\skin_2003_029\textures\skin_2003_029001n.tga', 'src_tex/029_n.png',
                            'NormalMap', 'linear', 'rule:001n.tga', 'c159 该材质路径声明', 'high'),
             't_custom_ibl': T(r'common\env_map\car_studio01.cube', 'src_cube/car_studio01.dds', 't_custom_ibl',
                               'linear', r'rule:\.cube', 'c159 该材质 cube 路径声明', 'high',
                               faces_glob='src_cube/faces/car_studio01_f{0..5}_m0.png',
                               state='source_resource_verified', sampling='sampling_unresolved'),
             'DetailMap': MISS(r'common\textures\crystal_bump_n02.tga', 'DetailMap'),
             't_caustic_tex': MISS(r'weapon\skin\skin_1012_013\testures\crystal_caustic_uvva002.tga', 't_caustic_tex'),
             't_reflection_tex': MISS(r'common\textures\crystal_reflection_uvva.tga', 't_reflection_tex'),
         },
         'missing_required': []},
        {'prim': 2, 'mtl_idx': 2, 'material': 'skin_2003_029_2', 'chain_material_raw': 'mmskin_2003_029_2',
         'glb_material': 'skin_2003_029_crystal', 'shader': r'shader\pbr_crystal.fx::TShader',
         'shader_kind': 'crystal', 'attribution': 'c159 路径块 8 条路径直读（槽名↔逻辑名）',
         'textures': {
             'Tex0': T(r'weapon\skin\skin_2003_029\textures\skin_2003_029001b_m.tga', 'src_tex/029_b_m.png',
                       'Tex0', 'linear', 'rule:001b_m.tga', 'c159 该材质首路径 029001b_m.tga（掩码）', 'high'),
             't_basecolor': T(r'weapon\skin\skin_2003_029\textures\skin_2003_029001a.tga', 'src_tex/029_a.png',
                              't_basecolor', 'ab_test', 'rule:001a.tga', 'c159 该材质路径声明', 'high'),
             'NormalMap': T(r'weapon\skin\skin_2003_029\textures\skin_2003_029001n.tga', 'src_tex/029_n.png',
                            'NormalMap', 'linear', 'rule:001n.tga', 'c159 该材质路径声明', 'high'),
             't_custom_ibl': MISS(r'common\env_map\fashion_qiangpi.cube', 't_custom_ibl'),
             'DetailMap': MISS(r'common\textures\crystal_bump_n_uvva.tga', 'DetailMap'),
             't_caustic_tex': MISS(r'common\textures\crystal_caustic_uvva.tga', 't_caustic_tex'),
             't_reflection_tex': MISS(r'common\textures\crystal_reflection_uvva.tga', 't_reflection_tex'),
             't_refraction_tex': MISS(r'common\textures\refraction_envmap_3.tga', 't_refraction_tex'),
         },
         'missing_required': []},
    ]
    man = {
        'schema': 'neox_material/v2', 'skin': '1110177',
        'block_rule': '01 00 01 13 01 + path + 00 ; 01 00 01 0f 02 = EOB',
        'source': {'bind_c159': '003994.c159', 'material_c159': '003996.c159',
                   'material_c159_sha256': sha(os.path.join(WDDS, '003996.c159')),
                   'bind_c159_sha256': sha(os.path.join(WDDS, '003994.c159')),
                   'mesh': '003995.mesh (LOD1)', 'mesh_sha256': sha(os.path.join(WDDS, '003995.mesh'))},
        'glb': {'path': 'dual.glb', 'sha256': sha(glb)},
        'geometry_glb_sha256': sha(glb),
        'parser_sha256': None,
        'required_by_program_family': {
            'pbr_default(weapon 分支)': {'required_slots': ['Tex0', 'ParamMap', 'NormalMap']},
            'pbr_crystal(crystal 分支)': {'required_slots': ['Tex0', 't_basecolor', 'NormalMap']}},
        'slot_binding_basis': {
            'A_c159_path_blocks': 'c159(003996.c159) 每材质路径块直读（c159_029_pair.json L649-765）',
            'B_cluster_order': '同集群贴图组顺序 b_m,s_m,a,n,m —— 由 1110171 两个组 ground truth（gpk_raw_8u32.json label）实证',
            'C_content_signature': '004011/004012/004013 内容签名与 1110171 的 a/n/m ground truth 逐项同族（_t5_decode_stats.json）',
            'unresolved': '未取得「逻辑名 → GPK 条目 idx」的名称级直证（weapon.gpk 条目字段不含路径哈希，'
                          '见 _known_loop/gpk_namehash_vs_pathid.json）；因此 029 的 5 张贴图到槽位的归属为 '
                          'candidate-high（A+B+C 三重印证），非 name-level 直证。'
        },
        'primitives': prims,
    }
    out = os.path.join(SKIN, 'neox_material.json')
    json.dump(man, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('neox_material.json -> %d B' % os.path.getsize(out))

    # ---- viewer.json：保留 1110177 既有 c159 参数层，仅把 model 指向 dual.glb 并补 crystal_submeshes ----
    oldp = os.path.join(SKIN, 'viewer.json')
    old = json.load(open(oldp, encoding='utf-8'))
    NEW_VIEWER_BAK = os.path.join(SKIN, 'viewer.json.bak_t5_20260917')
    if not os.path.exists(NEW_VIEWER_BAK):
        json.dump(old, open(NEW_VIEWER_BAK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    ml = old['states'][0].get('material_layers') or {}
    CPS = ['u_base_color', 'u_crystal_color', 'u_crystal_metallic', 'u_crystal_specular', 'u_cube_brightness',
           'u_detail_intensity', 'u_detail_tilling', 'u_emissive_fresnel', 'u_emissive_strength',
           'u_refraction_brightness', 'u_refraction_color', 'u_refraction_contrast', 'u_refraction_rotation',
           'u_rotate_angle', 'u_subsurface_color', 'u_base_metallic', 'u_base_specular', 'u_caustic_brightness',
           'u_caustic_depth', 'u_caustic_tilling']
    for sub, cfg in (ml.get('per_submesh') or {}).items():
        if isinstance(cfg, dict):
            for k in list(cfg.keys()):
                if ('u_' + k) in CPS and ('u_' + k) not in cfg:
                    cfg['u_' + k] = cfg[k]      # 仅恢复 c159 源参数名的 u_ 前缀（viewer 读 u_ 前缀键）
    ml['crystal_submeshes'] = [1, 2]
    ml['weapon_submeshes'] = [0]
    ml['other_submeshes'] = []
    ml['counts'] = {'weapon': 1, 'crystal': 2, 'other': 0, 'submeshes': 3}
    ml['classification_basis'] = ('按源 c159 shader 名：material0=pbr_default（不透明金属基底→viewer weapon 分支）、'
                                  'material1/2=pbr_crystal（→crystal 分支）')
    ml['slot_binding_basis'] = man['slot_binding_basis']
    for st in old['states']:
        st['model'] = 'dual.glb'
    old['default_state'] = old['states'][0]['id']
    old['_t5'] = {
        'task': 'T5 新传说武器（task-11）',
        'selected': {'skin_id': '1110177', 'name': '极光剑', 'dir': 'skin_2003_029', 'type': '冷兵器',
                     'chain': 'bind 003994.c159 / material 003996.c159 / mesh 003995.mesh(LOD1, 7943v/7422f, 3 子网格)',
                     'why': ['① 有 c159 材质定义：003996.c159 三个材质（pbr_default + 2×pbr_crystal），路径块可直读',
                             '② 有可用网格：003995.mesh 已破译（WEAPON_MESH_v4_FORMAT.md 实证 0% 异常）',
                             '③ 有源贴图可得：集群 004009..004013 五张 BC7(1024²) 完整覆盖 b_m/s_m/a/n/m 五个角色',
                             '④ 有参考图：poster.webp（既有）+ skin_2003_029 参考图历史',
                             '⑤ 同族已有 ground truth 可复核（1110171 的 a/n/m/b_m/s_m 签名）']},
        'assets': {'dual.glb': '从 003995.mesh 重建（export_glb.py，逐子网格一 primitive）',
                   'src_tex': '5 张源贴图（BGRA→RGBA，保留 alpha）+ 2 张纯通道重排派生图',
                   'src_cube': 'qiangpi / car_studio01（同一 common cube，六面与 1110171 既有面逐字节一致）',
                   'missing': ['common\\env_map\\fashion_qiangpi.cube (prim2 t_custom_ibl)',
                               'crystal_bump_n02 / crystal_bump_n_uvva / crystal_caustic_uvva002 / crystal_caustic_uvva / '
                               'crystal_reflection_uvva / refraction_envmap_3（晶体后续层，登记 missing）']},
    }
    json.dump(old, open(out.replace('neox_material.json', 'viewer.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('viewer.json -> %d B' % os.path.getsize(os.path.join(SKIN, 'viewer.json')))
    json.dump(man['slot_binding_basis'], open(os.path.join(HERE, '_t5_slot_basis.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
