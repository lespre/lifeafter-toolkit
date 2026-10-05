# -*- coding: utf-8 -*-
"""把 material_manifest 的源参数写进 viewer.json 的 material_layers（源驱动，非人工拟合）

规则（用户 2026-09-15 收口）：
 · 晶体参数只应用到该材质对应的子网格（按 MtlIdx）
 · 全局 rig（环境/曝光/色调映射）统一；材质级差异只读源 u_cube_brightness
 · 晶体表达仍为近似 → status=approximate
 · 归属有歧义时标 candidate，不写 high

用法: python apply_source_materials.py <viewer.json> <manifest.json> [--dual-candidate]
"""
import sys, os, json

# 参数名 → 查看器材质属性（只做"源参数 → 渲染属性"的直译，不发明数值）
def to_layer(params):
    g = {p['name']: p['value'] for p in params}
    out = {}
    if 'u_base_color' in g:
        out['base_color'] = g['u_base_color'][:3]
    if 'u_crystal_color' in g:
        out['crystal_color'] = g['u_crystal_color'][:3]
    if 'u_crystal_metallic' in g:
        v = g['u_crystal_metallic']
        out['metalness'] = float(1 if isinstance(v, int) else v)
    if 'u_crystal_roughness' in g:
        out['roughness'] = float(g['u_crystal_roughness'])
    if 'u_crystal_specular' in g:
        out['crystal_specular'] = g['u_crystal_specular']
    if 'u_refraction_color' in g:
        out['refraction_color'] = g['u_refraction_color'][:3]
    if 'u_refraction_brightness' in g:
        out['refraction_brightness'] = g['u_refraction_brightness']
    if 'u_subsurface_color' in g:
        out['subsurface_color'] = g['u_subsurface_color'][:3]
    if 'u_caustic_brightness' in g:
        out['caustic_brightness'] = g['u_caustic_brightness']
    if 'u_caustic_depth' in g:
        out['caustic_depth'] = g['u_caustic_depth']
    if 'u_cube_brightness' in g:           # ← 唯一允许的材质级环境因子（源值）
        out['cube_brightness'] = g['u_cube_brightness']
    if 'u_emissive_strength' in g:
        out['emissive_strength'] = g['u_emissive_strength']
    return out


def main(vp, mp, dual_candidate=False):
    v = json.load(open(vp, encoding='utf-8'))
    m = json.load(open(mp, encoding='utf-8'))
    per, notes = {}, []
    mats = m['materials']
    if dual_candidate:
        # 双枪：4 配对块 vs 5 晶体材料 → 顺序对应必然错位。
        # 用"行数锚"重挂：010 族两块的行数在单枪已验证为 14/15；本文件里 010 族是 Sub5/Sub6。
        rows2sub = {}
        for x in mats:
            if x['source_params']:
                rows2sub.setdefault(len(x['source_params']), []).append(x)
        sub_by_face = {x['faces']: x for x in mats}
        # 010 族：faces 11857/971/472（单枪同构），取其中两个晶体 sub（faces 971、472）
        f010 = [x for x in mats if x['faces'] in (971, 472) and x['source_params'] is not None]
        notes.append('双枪归属 candidate：001265 有 4 配对块 vs 5 晶体材料 → 工具的顺序对应会整体错位。'
                     '按"行数锚"（010 族两块在单枪已验证为 14/15 行）把 14/15 行块挂到 Sub5/Sub6；'
                     '012 族第三块视为未覆写。此为 candidate，非格式直证。')
        # 找 14 行与 15 行的块（排除已被 012 族按面数占用的重复行数情形）
        blocks = [x for x in mats if x['source_params']]
        b14 = [x for x in blocks if len(x['source_params']) == 14]
        b15 = [x for x in blocks if len(x['source_params']) == 15]
        b13 = [x for x in blocks if len(x['source_params']) == 13]
        assign = {}
        if b14 and b15:
            assign[b14[-1]['submesh']] = b14[-1]      # 14 行 → 010 族第 1 块
            assign[b15[0]['submesh']] = b15[0]        # 15 行 → 010 族第 2 块
        for x in blocks:
            if x['submesh'] in assign:
                layer = to_layer(x['source_params'])
                if layer:
                    per[str(x['submesh'])] = layer
        # 012 族：保留其自身 13/14 行块的归属（另一 14 行块已被 010 族占用 → 该 sub 不再挂参数）
        for x in blocks:
            if x['submesh'] in assign:
                continue
            if x in (b15[0] if b15 else None,):
                continue
            # 012 族中与 010 族同为 14 行的那个 sub 无法区分 → 不挂（避免错挂）
            if len(x['source_params']) == 14 and b14 and x is not b14[-1]:
                notes.append('Sub%d（14 行块）与 010 族同型块无法区分 → 不挂参数（宁缺勿错）' % x['submesh'])
                continue
            layer = to_layer(x['source_params'])
            if layer:
                per[str(x['submesh'])] = layer
    else:
        for x in mats:
            if not x['source_params']:
                continue
            layer = to_layer(x['source_params'])
            if layer:
                per[str(x['submesh'])] = layer
    layers = {
        "status": "approximate",
        "basis": "源 c159 参数（c159_pair.py 槽位引用组解析）+ 绑定 c159 的 MtlIdx 归属",
        "global_rig": {"env_intensity": 1.0, "exposure": 1.0, "tone_mapping": "ACESFilmic",
                       "note": "全局展示 rig 统一，所有皮肤一致；不做逐资产标定"},
        "material_level_source_factor": "u_cube_brightness（唯一允许的材质级差异来源）",
        "per_submesh": per,
        "unoverridden_submeshes": [x['submesh'] for x in m['materials'] if not x['source_params']],
        "notes": notes,
        "not_yet_implemented": ["crystal_bump/reflection/refraction/caustic 采样关系", "crystal IBL cube", "shader DXBC 公式", "Sub0 刀身金色来源（默认参数/IBL/自发光/SFX 追踪中）"],
    }
    v['material_layers'] = layers
    json.dump(v, open(vp, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('写入 %s' % os.path.basename(vp))
    for k, s in sorted(per.items(), key=lambda kv: int(kv[0])):
        print('   Sub%s: %s' % (k, {kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in s.items()}))
    if layers['unoverridden_submeshes']:
        print('   未覆写（引擎默认）: Sub%s' % layers['unoverridden_submeshes'])


if __name__ == '__main__':
    a = sys.argv[1:]
    main(a[0], a[1], '--dual-candidate' in a)
