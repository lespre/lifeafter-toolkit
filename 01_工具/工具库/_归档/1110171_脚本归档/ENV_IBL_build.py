# -*- coding: utf-8 -*-
"""ENV_IBL_build.py — 生成 ENV_IBL_diff.json（机读：逐 prim × 逐项 {source_evidence, current_code, verdict}）。只写该文件。"""
import io, json, os, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
V = {'sha256': '113692f0f38362c483b1f65fa695665bf7b619f1a6edf7bd2c285fdaaa22b6ef',
     'bytes': 298329, 'lines': 4149, 'file': r'08Lifeafter wiki\assets\weapon_skin_viewer.js'}
R = '03拆包产物'

# 源声明（c159 逐块，含 slot 记录 off 与原始字节 off）
DECL = {
    '1110171': {'c159': ['001265.c159(dual)', '001223.c159(single)'], 'prims': [
        {'prim': 0, 'kind': 'weapon', 'material': 'skin_1003_012_0', 'block': 0, 'declared': 'qiangpi.cube',
         'slot_off': 3498, 'raw_off': [3518, 6282], 'current': 'src_cube/qiangpi.dds', 'verdict': 'ok'},
        {'prim': 1, 'kind': 'crystal', 'material': 'skin_1003_012_1', 'block': 1, 'declared': 'car_studio01.cube',
         'slot_off': 4217, 'raw_off': [4237], 'current': 'src_cube/car_studio01.dds', 'verdict': 'ok'},
        {'prim': 2, 'kind': 'crystal', 'material': 'skin_1003_012_2', 'block': 2, 'declared': 'car_studio01.cube',
         'slot_off': 5032, 'raw_off': [5052], 'current': 'src_cube/fashion_qiangpi.dds', 'verdict': 'mismatch'},
        {'prim': 3, 'kind': 'crystal', 'material': 'skin_1003_012_3', 'block': 3, 'declared': 'car_studio01.cube',
         'slot_off': 5789, 'raw_off': [5809], 'current': 'src_cube/car_studio01.dds', 'verdict': 'ok'},
        {'prim': 4, 'kind': 'weapon', 'material': 'skin_1003_010_0', 'block': 4, 'declared': 'qiangpi.cube',
         'slot_off': 6262, 'raw_off': [6282], 'current': 'src_cube/qiangpi.dds', 'verdict': 'ok'},
        {'prim': 5, 'kind': 'crystal', 'material': 'skin_1003_010_1', 'block': 5, 'declared': 'car_studio01.cube',
         'slot_off': 6981, 'raw_off': [7001], 'current': 'src_cube/car_studio01.dds', 'verdict': 'ok'},
        {'prim': 6, 'kind': 'crystal', 'material': 'skin_1003_010_2', 'block': 6, 'declared': 'car_studio01.cube',
         'slot_off': 7720, 'raw_off': [7740], 'current': 'src_cube/car_studio01.dds', 'verdict': 'ok'}]},
    '1110177': {'c159': ['003996.c159'], 'prims': [
        {'prim': 0, 'kind': 'weapon', 'material': 'skim_2003_029_0', 'block': 0, 'declared': 'qiangpi.cube',
         'slot_off': 2152, 'raw_off': [2172], 'current': 'src_cube/qiangpi.dds', 'verdict': 'ok'},
        {'prim': 1, 'kind': 'crystal', 'material': 'skim_2003_029_1', 'block': 1, 'declared': 'car_studio01.cube',
         'slot_off': 2926, 'raw_off': [2946], 'current': 'src_cube/car_studio01.dds', 'verdict': 'ok'},
        {'prim': 2, 'kind': 'crystal', 'material': 'skim_2003_029_2', 'block': 2, 'declared': 'fashion_qiangpi.cube',
         'slot_off': 3726, 'raw_off': [3746], 'current': 'src_cube/fashion_qiangpi.dds', 'verdict': 'ok'}]}}

VALS = {'1110177': {'prim1': {'u_rotate_angle': 3.09, 'u_cube_brightness': 0.71,
                              'bytes': {'u_rotate_angle_f32@': 2434, 'u_cube_brightness_f32@': 2443, 'block@': 2393,
                                        'param_names@': {'u_rotate_angle': 653, 'u_cube_brightness': 473}},
                              'viewer_json': 'per_submesh.sub1.cube_brightness=0.71'},
                   'prim2': {'u_rotate_angle': 2.6, 'u_cube_brightness': 2.74,
                             'bytes': {'u_rotate_angle_f32@': 3253, 'u_cube_brightness_f32@': 3262, 'block@': 3221},
                             'viewer_json': 'per_submesh.sub2.cube_brightness=2.74'}}}

ITEMS = [
    ('cube_declaration', '每 prim 声明哪个 cube（c159 t_custom_ibl 槽）',
     'c159 逐块 t_custom_ibl 明文（slot 记录 off + 原始字节 off，见 objects[*].prims）',
     'viewer_skin_viewer.js L1162 iblName ← manifest t_custom_ibl.local_file 基名；L1193-1198 六面 URL（faces_glob 优先，回落 iblName_f{i}_m0）',
     'per_prim'),
    ('cube_face_loading_m0', '六面 m0 PNG 装载',
     '源 cube = 128² B8G8R8A8_UNORM、8 级 mip、caps2=0xfe00（六面 flag 全置）',
     'viewer L1234 CubeTextureLoader().load(urls) 六条 *_f{i}_m0.png；L1238 NoColorSpace；L1240 LinearMipmapLinear/Linear；L1241 ClampToEdge；L1242 anisotropy=MAXANISO',
     'ok'),
    ('readiness_gate', '六面未就绪时的行为',
     '源端无对应概念（cube 常驻）',
     'viewer L1219-1245：gate 判据 image 全 complete && naturalWidth>0；未就绪 return null（不绑 envMap/uCustomIbl）+ state.__iblGate + __iblRebindPending → 就绪后一次重绑；L1208-1218 六 URL 非互异即拒绝装配',
     'ok_chain_extra'),
    ('mip_chain', 'mip 链来源（作者 mip vs 自动生成）',
     '源 textureLod 于 8 级 mip 立方图；作者 mip 存在于 DDS 与磁盘 PNG（1110171 qiangpi/car_studio01 有 m0..m7 + cube_faces_mips.json）',
     'viewer 只装 m0 PNG；L1239 generateMipmaps=true ⇒ 由 GPU 自动生成 mip；作者 mip 未被消费',
     'mismatch'),
    ('rgbm_decode', 'RGBM 解码 (rgb·a·16)²',
     'asm L525-527（晶体 PS）/(等同 weapon PS)：`(S.rgb·S.a·16)²`',
     'viewer L1367 `pow(q_sm.rgb*q_sm.a*16.0, vec3(2.0))`',
     'ok'),
    ('min_clamp_1p5', 'min(L,1.5)',
     'asm L528 `min`',
     'viewer L1368 `min(q_L, vec3(1.5))`',
     'ok'),
    ('lod_formula', 'LOD = 5 + 1.2·log2(rough)',
     'asm L520-522 `log r·-1.2+1·+6`（T2 文档 L41 行号映射）',
     'viewer L1356-1357 `max(roughness,0.0019)` → `5.0 + 1.2*log2(q_rough)`',
     'ok'),
    ('rotation_u_rotate_angle', '环境旋转 u_rotate_angle',
     '材质级 NeoxUBOLocal@124（晶体 cb0[7].w / weapon cb0[4].x）；1110177 晶体实测 3.09 rad(≈177°) / 2.60 rad(≈149°)（003996.c159 f32@2434/2443、3253/3262）；1110171 两份 c159 均无 u_rotate_angle 名',
     'viewer L1361-1365 用 shader uniform uIblRot（L1342 默认 state.iblRot===undefined→0.0）；无任何代码从 c159/viewer.json 读取 u_rotate_angle',
     'per_prim'),
    ('env_material_scale_u_cube_brightness', '材质级环境亮度 u_cube_brightness',
     '材质级 NeoxUBOLocal@128（晶体 cb0[188].x）；asm 亮度分支 `movc r5.xyz, r1.z, r5.xyz, r9.xyz`；1110177 晶体 0.71 / 2.74（003996.c159 f32@2443/3262；viewer.json per_submesh.sub1/sub2.cube_brightness 同值）；1110171 无配对值',
     '生产路径不消费：viewer L2187-2190（非 lab 且 applied>0 ⇒ return 0，永不到 L2236+）；仅 lab 路径 L2363 `envMapIntensity=env*(cfg.cube_brightness||1)`；且 L1339-1376 覆写体内不含任何材质级系数',
     'per_prim'),
    ('env_scene_exposure', '场景曝光乘子 u_env_day2night_exposure',
     '场景级 NeoxUBOGlobal1@3824 = cb1[239].x；DXBC 定义 flag:"unused"、4 份定义均无取值 ⇒ 身份已定、值未取（AUDIT_8皮肤缺陷与卡点 L52）',
     'viewer L1344-1346 uIblScale 默认 0.25（照抄 lab_src.html 的 opt.envExposure，非源常量）；L1370 `q_env *= uIblScale`',
     'mismatch_no_source_value'),
    ('lightmap_lerp', 'lightmap 混合 lerp(C, min(C,1.5)·0.299805, sat(u_lightmap_factor))',
     'asm L529-531；系数 = cb1[86].z = u_lightmap_factor（offset 1384，场景级，值未取）',
     'viewer L1369 `q_env = q_L + uIblMix*(q_Lc*0.299805 - q_L)`；uIblMix 默认 0（L1343）⇒ 该分支在生产默认不生效（同型实现，值缺）',
     'unresolved'),
    ('envmap_intensity', 'three envMapIntensity 是否作用于 IBL',
     '源无该量；源侧材质级环境系数是 u_cube_brightness',
     'viewer L1288/L1316 `envMapIntensity = envAllowed?1.0:0.0`；但 three r180 的 envMapIntensity 乘法位于被覆写的 getIBLRadiance 体内（three.module.min.js @34262 `return envMapColor.rgb * envMapIntensity;`）⇒ 覆写后该 uniform 不参与 radiance',
     'mismatch_inert'),
    ('three_brdf_reflect_mix', 'reflect + mix(normal, rough²) + inverseTransformDirection',
     '源 asm L514-524 只用旋转 + sample_l；未见 mix(normal,rough²)（T2 文档 L35 的 asm 片段）',
     'viewer L1358-1360 三行 = three r180 原 getIBLRadiance 正文（three.module.min.js @33802 起）⇒ 属"恢复 Three BRDF"口径，非源行',
     'ok_by_policy'),
    ('face_order_basis', '六面顺序/基变换是否等于源',
     '源 cube 面序与引擎采样约定未定位（本项目无 .cube 容器字段证据）',
     'viewer 按 f0..f5 顺序交给 CubeTextureLoader；无基变换',
     'unresolved'),
    ('cube_storage_layout', 'DDS 排布（face-major / mip-major）',
     '—（源容器为 .cube，DDS 为派生物）',
     '本对皮肤 6 个 DDS 实测 **face-major**（face-major 与磁盘 m0 PNG mean|Δ|=0.00；mip-major 为 98.7-199.5）；而 1110024 的 indoor/gdansk 实测为 mip-major ⇒ 提取产物排布跨皮肤不一致',
     'unresolved_extraction_inconsistency'),
    ('lab_hardcoded_cube_selector', 'lab 路径写死的逐 prim cube 选择',
     '源按材质声明（每块 t_custom_ibl）',
     'viewer L2307 `CUBE_OF={0:qiangpi,4:qiangpi,1..3,5,6:car_studio01}` + L2308 CUBE_FOR_PRIM + L2311-2318 srcCube() ⇒ lab 路径忽略 manifest 声明（1110171 prim2 亦被写成 car_studio01）',
     'mismatch_lab_only'),
    ('f0_crystal', '（相关，非 IBL）晶体 F0',
     '源 F0 = lerp(0.079956, BaseColor, metallic)（`render_experimental_dxbc_pbr.py` L10/L31；asm [357]-[358]）',
     'three MeshStandardMaterial F0 = mix(0.04, diffuse, metalness)（three.module.min.js lights_physical_fragment）⇒ metal=0 晶体镜面项≈源的一半（T2_渲染器专项 L43-51）',
     'mismatch_related'),
]

res = {'task': 'ENV IBL 链规格 + 现状差异（1110171 / 1110177）', 'readonly': True,
       'viewer_revision': V, 'generated_from': ['ENV_IBL_probe1..4', 'C159PARSE_skins_fixed.json',
                                                'c159_pair_v4_001265.json', 'c159_pair_v4_regress.json',
                                                'T2_渲染器专项_20260917.md', '渲染链现状报告_给外部AI_20260918.md',
                                                'AUDIT_8皮肤缺陷与卡点_20260918.md'],
       'objects': DECL, 'source_uniform_values': VALS, 'items': []}

for name, title, src, cur, mode in ITEMS:
    it = {'item': name, 'title': title, 'source_evidence': src, 'current_code': cur, 'mode': mode, 'per_prim': {}}
    for skin, obj in DECL.items():
        for pr in obj['prims']:
            pid = 'prim%d' % pr['prim']
            if mode == 'per_prim':
                if name == 'cube_declaration':
                    v = pr['verdict']
                    se = '%s：blk%d t_custom_ibl=%s（slot off=%s，原始字节 off=%s）' % (
                        ','.join(obj['c159']), pr['block'], pr['declared'], pr['slot_off'], pr['raw_off'])
                    cc = 'manifest 现值 = %s' % pr['current']
                elif name == 'rotation_u_rotate_angle':
                    vals = (VALS.get(skin, {}).get(pid) or {})
                    if vals:
                        v, se, cc = ('mismatch',
                                     '003996.c159 声明 u_rotate_angle=%s（f32@%s，块@%s）' % (
                                         vals['u_rotate_angle'], vals['bytes']['u_rotate_angle_f32@'], vals['bytes']['block@']),
                                     '链 uIblRot 默认 0.0（viewer L1342），无读取代码 ⇒ 环境方向差 %s rad' % vals['u_rotate_angle'])
                    elif skin == '1110171':
                        v, se, cc = ('ok_no_declaration',
                                     '001265.c159/001223.c159 全文无 `u_rotate_angle`（原始字节扫描 0 命中）⇒ 该材质无声明',
                                     '链 uIblRot=0.0（L1342）与"无声明"一致；引擎默认块值不可得 ⇒ 不判缺陷')
                    else:
                        v, se, cc = ('unresolved', 'weapon prim：003996.c159 无 u_rotate_angle 值（block_off=null）',
                                     '链 uIblRot=0.0；weapon PS 读 cb0[4].x，引擎默认值不可得')
                elif name == 'env_material_scale_u_cube_brightness':
                    vals = (VALS.get(skin, {}).get(pid) or {})
                    if vals:
                        v, se, cc = ('mismatch',
                                     '003996.c159 声明 u_cube_brightness=%s（f32@%s）；viewer.json %s' % (
                                         vals['u_cube_brightness'], vals['bytes']['u_cube_brightness_f32@'], vals['viewer_json']),
                                     '生产路径无任何材质级 env 系数（L2187-2190 早退；覆写体 L1339-1376 不含）⇒ 实际按 1.0，缺 %s×' % vals['u_cube_brightness'])
                    elif skin == '1110171':
                        v, se, cc = ('ok_no_declaration',
                                     '001265/001223 中 `u_cube_brightness` 仅作为参数名出现一次（off 518/474），无配对数值；viewer.json 5 个 per_submesh 均无 cube_brightness',
                                     '生产按 1.0 ⇒ 与"无声明"一致，不判缺陷')
                    else:
                        v, se, cc = ('unresolved', 'weapon prim 无值（block_off=null）', '生产按 1.0；引擎默认值不可得')
                else:
                    v, se, cc = mode, src, cur
            else:
                v, se, cc = mode, src, cur
            it['per_prim'].setdefault(skin, {})[pid] = {'source_evidence': se, 'current_code': cc, 'verdict': v}
    res['items'].append(it)

# 附加：可量化事实
res['facts'] = {
    'cube_asset_identity': {'qiangpi.dds_sha16': '173d52990b3ab836', 'car_studio01.dds_sha16': 'bea649d8525cdc3e',
                            'fashion_qiangpi.dds_sha16': '34252fcb4d641227',
                            'note': '1110171 与 1110177 三张 dds + 18 个 m0 面 sha16 全同（同一资产的两份拷贝）；qiangpi 亦与 1110129 相同'},
    'source_rgbm_env_level_mean': {'1110171|1110177 qiangpi': [0.7866, 0.9157, 1.0719],
                                   'car_studio01': [0.3204, 0.3114, 0.3047],
                                   'fashion_qiangpi': [0.2162, 0.2492, 0.2744],
                                   'note': '(rgb·a·16)² 六面均值（Rec.709 前）；qiangpi:car:fashion ≈ 2.5 : 1 : 0.8'},
    'authored_mip_vs_auto_m1': {'1110171/qiangpi mean|ΔRGB| 逐面': [28.36, 23.77, 31.03, 4.35, 33.26, 'f5'],
                                '1110171/car_studio01 mean|ΔRGB| 逐面': [4.91, 5.02, 5.49, 7.96, 6.52, 'f5'],
                                'note': '作者 m1(64²) vs m0 盒降采样；qiangpi 最大 33.26/255（13%）且 alpha 均值差 1.5-2.2 ⇒ 自动 mip ≠ 作者 mip'},
    'mip_availability': {'1110171': {'qiangpi': 'm0..m7 + cube_faces_mips.json', 'car_studio01': 'm0..m7 + cube_faces_mips.json',
                                     'fashion_qiangpi': '仅 m0（无 mip、无 mips.json 条目）'},
                         '1110177': {'qiangpi': '仅 m0', 'car_studio01': '仅 m0', 'fashion_qiangpi': '仅 m0',
                                     'cube_faces_mips.json': '不存在'}},
    'dds_layout': {'1110171/1110177 六个 dds': 'face-major（face-major mean|Δ|=0.00 对 m0 PNG）',
                   '1110024 indoor/gdansk': 'mip-major（task-23 实测 0.00）⇒ 跨皮肤不一致'},
    'acceptance': {'P1_offset': {'p50': 0.132, 'p95': 0.727, 'gt0.5_pct': 8.23, 'gt0.75_pct': 4.68, 'warm_pct': 3.01},
                   'P2_current': {'p50': 0.138, 'p95': 0.282, 'gt0.5_pct': 0.83, 'gt0.75_pct': 0.03, 'warm_pct': 0.00}}
}
json.dump(res, open(os.path.join(OUT, 'ENV_IBL_diff.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('ENV_IBL_diff.json written: items=%d objects=%d bytes=%d' % (len(res['items']), len(res['objects']),
                                                                 os.path.getsize(os.path.join(OUT, 'ENV_IBL_diff.json'))))
for it in res['items']:
    vs = {skin: {p: d['verdict'] for p, d in pv.items()} for skin, pv in it['per_prim'].items()}
    print('  %-42s %s' % (it['item'], json.dumps(vs, ensure_ascii=False)[:150]))
