# -*- coding: utf-8 -*-
"""T5-fix 交付：把「晶体族 q_T=无色」的口径落到 manifest（显式、可回退、不删证据）。

依据（受控对照，见 _build_t5/_t5_exp_gem_D*.json 与 _target_1110171/S177_gem_D*.png）：
  D1 = cp 有 + t_basecolor=029_a(青蓝) → 护手仍蓝、红宝石不出现（blue 0.67% red 0.04%）
  D2 = cp 有 + prim1/2 不给 t_basecolor（viewer 走 hasBaseTex=false → q_T=vec3(1.0)）
       → 护手银白、中央+柄尾红宝石出现（blue 0.00% silver 2.03→2.70%）
口径说明：不是"删掉源路径"，而是把该槽从**渲染输入**移出并完整登记到 withheld_slots：
  源 c159 对 material1/2 仍声明 029001a；但 viewer 的晶体公式为
      A = mix(q_T, q_T*u_crystal_color, mm) ; B = mix(u_base_color, q_T*u_crystal_color, dd)
  当 q_T=029_a（青蓝）时 T*u_crystal_color 被冷色污染，红色无从出现；
  q_T 无色时颜色全部来自 029 自己的 c159 常量（u_crystal_color=[0.2431,0,0] 等），与参考图一致。
  ⇒ 恢复方式：把 withheld_slots.t_basecolor 移回 textures 即回到 D1 口径。
"""
import json, os, shutil, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
SKIN = os.path.dirname(HERE)
MAN = os.path.join(SKIN, 'neox_material.json')
REC = os.path.join(SKIN, 'binding_basis_20260917.json')

WITHHELD_BASIS = ('REFERENCE_IMAGE_DIRECT（用户在 2026-09-17 给出游戏参考图：金色剑身 + 银白护手 + '
                  '中央/柄尾红宝石）＋ 受控对照 D1 vs D2：同 manifest 只改此一处，'
                  '护手由蓝转银白、红宝石出现；- 该槽在本族被移出渲染输入，'
                  '颜色全部来自 c159 常量 u_crystal_color/u_base_color（逐 prim 各自值）')


def main():
    man = json.load(open(MAN, encoding='utf-8'))
    log = []
    for p in man['primitives']:
        if p['prim'] not in (1, 2):
            continue
        tex = p['textures']
        if 't_basecolor' not in tex:
            continue
        slot = tex.pop('t_basecolor')
        p.setdefault('withheld_slots', {})['t_basecolor'] = dict(
            slot,
            state='withheld_from_render_input',
            binding_basis=WITHHELD_BASIS,
            restore_rule='把该对象原样移回 textures.t_basecolor 即恢复 D1 口径（T=029_a 青蓝）',
        )
        p['binding_basis'] = dict(
            Tex0='c159 material1/2 路径块首项 029001b_m.tga（掩码；viewer 取 .r 作 q_mm）',
            NormalMap='c159 material1/2 路径块 029001n.tga',
            t_custom_ibl=('c159 声明；prim1=car_studio01.cube（本地已定位，source_resource_verified）；'
                          'prim2=fashion_qiangpi.cube（**本地未定位 → missing**）'),
            t_basecolor=WITHHELD_BASIS,
            crystal_params=('c159 per-material 参数块（group1/block0→prim1, group2/block1→prim2），'
                            '逐 prim 各自值，provenance 见 prim.crystal_params.provenance'),
        )
        log.append({'prim': p['prim'], 'action': 't_basecolor → withheld_slots',
                    'note': '渲染输入改为 q_T=vec3(1.0)；源路径仍完整登记'})
        print('prim%d: t_basecolor -> withheld_slots  (保留 logical_path=%s)' % (p['prim'], slot.get('logical_path')))

    man['binding_basis_summary'] = {
        'date': '2026-09-17',
        'reference_image': '金色剑身 + 银白/白护手 + 中央红宝石 + 柄尾红宝石 + 金色辉光（用户提供）',
        'changes': log,
        'evidence': {
            'D0b': {'file': 'S177_gem_D0b_diag_nocp.png', 'setup': 'cp 无 + diag env',
                    'blue_frac': 0.69, 'red_frac': 0.04, 'silver_frac': 2.03},
            'D1': {'file': 'S177_gem_D1_diag_cp.png', 'setup': 'cp 有 + t_basecolor=029_a',
                   'blue_frac': 0.67, 'red_frac': 0.04, 'silver_frac': 2.03},
            'D2': {'file': 'S177_gem_D2_diag_notbase.png', 'setup': 'cp 有 + q_T 无色',
                   'blue_frac': 0.00, 'red_frac': 0.06, 'silver_frac': 2.70},
        },
        'viewer_gap': {
            'u_emissive_fresnel': '参数已落 manifest，但 viewer 主链**未消费** → 金色辉光无法出现（需另开一轮，未自行加发光）',
            'u_emissive_strength': '同上',
            'u_subsurface_color': '参数已落 manifest，viewer 主链未消费（红宝石饱和度只能来自 u_crystal_color）',
            'u_refraction_color': '同上',
            'u_cube_brightness': '同上',
        },
        'render_blocker': {
            'file': 'assets/weapon_skin_viewer.js:1182（同型缺陷亦在 :1222）',
            'code': "((typeof prevKey==='function')?prevKey():'')  // prevKey() 未绑定 this",
            'trigger': '该材质无自有 customProgramCacheKey（iblCube=null；prim2 缺 fashion_qiangpi.cube）→ '
                       'prevKey 落到 three 的 Material.prototype.customProgramCacheKey(){return this.onBeforeCompile.toString()}'
                       '，this=undefined → TypeError → renderer.render 抛错 → **整帧中止（画面全黑、snapshot 无图）**',
            'three_ref': 'assets/vendor/three/three.core.min.js  Material.prototype.customProgramCacheKey',
            'fix_suggestion': '改为 prevKey.call(m)（L1222 的 pk 同理）',
        },
    }
    json.dump(man, open(MAN, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(man['binding_basis_summary'], open(REC, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('[saved] %s (%d B)\n[saved] %s' % (MAN, os.path.getsize(MAN), REC))


if __name__ == '__main__':
    main()
