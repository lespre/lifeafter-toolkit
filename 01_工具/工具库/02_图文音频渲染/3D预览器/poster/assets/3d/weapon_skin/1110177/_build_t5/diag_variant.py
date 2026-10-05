# -*- coding: utf-8 -*-
"""生成诊断用 manifest 变体（**临时**，用于绕过 viewer 崩溃取得可视化对比；不作为交付绑定）。

背景：viewer.js:1182 `prevKey()` 未绑定 this 调用；当该材质没有自有 customProgramCacheKey
（= iblCube 为 null，即 prim2 缺 fashion_qiangpi.cube）时，prevKey 落到 three 的
Material.prototype.customProgramCacheKey(){ return this.onBeforeCompile.toString() }，
this=undefined → TypeError → renderer.render 抛出 → 整帧中止（画面全黑、snapshot 无图）。
诊断变体只把 prim2 的 t_custom_ibl 临时指向 prim1 同一 cube（car_studio01）以走进 iblCube 分支，
使渲染可跑，从而对 crystal_params 做前后对比。**交付 manifest 不保留该覆盖。**
"""
import json, os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKIN = os.path.dirname(HERE)
MAN = os.path.join(SKIN, 'neox_material.json')
COMPLIANT = os.path.join(HERE, '_t5_manifest_compliant.json')


def main(mode):
    if mode == 'save':
        shutil.copyfile(MAN, COMPLIANT)
        print('saved compliant manifest ->', COMPLIANT)
        return
    man = json.load(open(MAN, encoding='utf-8'))
    print('[base] loaded current manifest')
    if mode == 'diag_on':
        for p in man['primitives']:
            if p['prim'] == 2:
                t = p['textures']['t_custom_ibl']
                t.update({'local_file': 'src_cube/car_studio01.dds', 'sha256': None,
                          'evidence': 'DIAGNOSTIC-ONLY 临时覆盖（非交付绑定）：prim2 真源 fashion_qiangpi.cube 缺失，'
                                      '为绕过 viewer.js:1182 的 unbound prevKey() 崩溃、取得可视化前后对比而临时指向同一 cube',
                          'confidence': 'diagnostic', 'state': 'diagnostic_override_for_render',
                          'reason': '交付版本必须回到 missing'})
                print('prim2 t_custom_ibl -> diagnostic override (car_studio01)')
    elif mode == 'diag_notbase':
        # 诊断：去掉 prim1/2 的 t_basecolor（viewer 会走 hasBaseTex=false → q_T=vec3(1.0)）
        for p in man['primitives']:
            if p['prim'] in (1, 2):
                if 't_basecolor' in p['textures']:
                    p['textures'].pop('t_basecolor')
                p['missing_required'] = [s for s in (p.get('missing_required') or []) if s != 't_basecolor']
                p['_diag_note'] = 'DIAGNOSTIC-ONLY: 临时移除 t_basecolor 以检验 viewer 的 q_T=vec3(1.0) 分支'
                print('prim%d t_basecolor removed (diagnostic)' % p['prim'])
    elif mode == 'cp_off':
        for p in man['primitives']:
            p.pop('crystal_params', None)
            p.pop('crystal_params_basis', None)
        man.pop('crystal_params_crosscheck', None)
        print('crystal_params removed (before-state)')
    json.dump(man, open(MAN, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('wrote', MAN)


if __name__ == '__main__':
    main(sys.argv[1])
