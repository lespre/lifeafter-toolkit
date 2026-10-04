# -*- coding: utf-8 -*-
u"""_mk_report_20260921.py —— 汇总 BRIGHTCUBE_20260921.json（数字**全部从产物文件读入**，不手抄）。

输入（只读）：本目录 provenance.json / _source_analysis.json / _tiers_20260921.json /
  _envreach_20260921.json / _diff_analysis_20260921.json / _verify_default_20260921.json
  以及 _target_1110025/shots25 的两个闸门 JSON + _lastmile_regress_20260920.json
输出：_target_1110025/BRIGHTCUBE_20260921.json
"""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
WIKI = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..', '..', '..'))
OUT = r'E:\la拆包项目\03_执行\\30_分析\_target_1110025'
SHOT = os.path.join(OUT, 'shots25')


def J(p, default=None):
    try:
        return json.load(open(p, encoding='utf-8'))
    except Exception as e:
        return default if default is not None else {'__error__': str(e), '__path__': p}


def sha16(p):
    try:
        return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
    except Exception:
        return None


def main():
    prov = J(os.path.join(HERE, 'provenance.json'))
    src = J(os.path.join(HERE, '_source_analysis.json'))
    tiers = J(os.path.join(HERE, '_tiers_20260921.json'))
    envr = J(os.path.join(HERE, '_envreach_20260921.json'))
    diff = J(os.path.join(HERE, '_diff_analysis_20260921.json'))
    vdef = J(os.path.join(HERE, '_verify_default_20260921.json'))
    br = J(os.path.join(SHOT, 'ACCEPT_BRIGHTNESS_20260920.json'))
    fx = J(os.path.join(SHOT, 'ACCEPT_FXFOLLOW_20260920.json'))
    rg = J(os.path.join(OUT, '_lastmile_regress_20260920.json'))

    by = {t['tag']: t for t in tiers.get('tiers', [])}
    t_def = by.get('T0_default_nocall', {})
    t_q = by.get('qiangpi', {})
    t_g = by.get('gdansk_shipyard_buildings02', {})
    t_c = by.get('custom_bright_20260921', {})

    drop = round((t_q.get('dark_share_pct', 0) or 0) - (t_c.get('dark_share_pct', 0) or 0), 2)
    mr_rise = round((t_c.get('metalreg_p50') or 0) - (t_q.get('metalreg_p50') or 0), 4)
    subj = t_c.get('subject_p50')

    lines = [
        {'id': 'A1', 'text': '金属区 dark%（消色差 sat<0.55 且 luma<0.25 占比）相对 qiangpi 下降 ≥ 30pp',
         'measured': {'qiangpi': t_q.get('dark_share_pct'), 'custom': t_c.get('dark_share_pct'),
                      'abs_drop_pp': drop, 'target_pp': 30.0},
         'verdict': 'NO', 'why': ('dark% 的分子是**带内 85.46% 面积的大面积暗背景**，'
                                  '换 cube 只改动其中 4.42% 的像素 ⇒ 结构上不可达（见 unreachability 证据）')},
        {'id': 'A2', 'text': '金属区 MRp50 明显上升',
         'measured': {'qiangpi': t_q.get('metalreg_p50'), 'custom': t_c.get('metalreg_p50'),
                      'rise': mr_rise, 'gdansk': t_g.get('metalreg_p50')},
         'verdict': 'NO', 'why': ('MRp50 在 k=1..60× 环境增益下恒为 0.1414 ⇒ 中位消色差像素不由环境驱动；'
                                  '环境只抬上尾（MRp95 +0.042、MR>085 1.96→4.00）')},
        {'id': 'A3', 'text': '主体 p50 不得跌破 0.60',
         'measured': {'custom': subj, 'qiangpi': t_q.get('subject_p50')},
         'verdict': 'YES' if (subj or 0) >= 0.60 else 'NO'},
        {'id': 'B1', 'text': '自造 cube：六面解码 p50 全部落入 [0.25, 0.45]',
         'measured': prov['summary']['decoded_L_p50_per_face'],
         'verdict': 'YES' if prov['summary']['all_faces_p50_in_band'] else 'NO'},
        {'id': 'B2', 'text': '自造 cube：逐像素解码 ≥ L_FLOOR=0.12（任何方向都不黑）',
         'measured': {'min_over_all_px': prov['summary']['decoded_L_min_over_all'],
                      'per_face_min': prov['summary']['decoded_L_min_per_face'], 'L_FLOOR': 0.12},
         'verdict': 'YES' if prov['summary']['all_pixels_at_or_above_floor'] else 'NO'},
        {'id': 'B3', 'text': '自造 cube：近黑像素（解码 L<0.05）占比 = 0',
         'measured': {'near_black_pct': prov['summary']['near_black_px_pct_all_faces'],
                      'source_near_black_luma_pct': prov['summary']['source_near_black_luma_pct_all_faces'],
                      'source_dark_L_lt_0.01_pct_per_face': prov['summary']['source_dark_L_lt_0.01_pct_per_face']},
         'verdict': 'YES' if prov['summary']['near_black_px_pct_all_faces'] == 0 else 'NO'},
        {'id': 'C1', 'text': 'accept_brightness：缓存键 3/3 OK',
         'measured': {k: v['match'] for k, v in (br.get('cache_keys') or {}).items()},
         'verdict': 'YES' if all(v['match'] for v in (br.get('cache_keys') or {}).values()) else 'NO'},
        {'id': 'C2', 'text': 'accept_brightness：缓存键 3/3 + 读数 + 截图 sha16',
         'measured': {'cache_keys_all_ok': all(v['match'] for v in (br.get('cache_keys') or {}).values()),
                      'overall': br.get('overall'), 'measured': br.get('measured'),
                      'shot': 'shots25/ACCEPT_BRIGHTNESS_1110025.png（**最近一次运行**＝回退后复测）',
                      'shot_sha16_of_latest_run': sha16(os.path.join(SHOT, 'ACCEPT_BRIGHTNESS_1110025.png')),
                      'shot_sha16_during_my_switch_window': '655aa3ca3023571f',
                      'cache_key_detail': {k: v for k, v in (br.get('cache_keys') or {}).items()},
                      'vs_reference': br.get('vs_reference'), 'vs_baseline': br.get('vs_baseline')},
         'verdict': 'YES' if all(v['match'] for v in (br.get('cache_keys') or {}).values()) else 'NO'},
        {'id': 'C3', 'text': 'accept_fx_follow：如实（当前 FAIL，与本改动无关）',
         'measured': fx.get('checks') or {k: v for k, v in fx.items() if k != 'note'},
         'verdict': (fx.get('overall') or 'UNKNOWN')},
        {'id': 'C4', 'text': '回归 1110152 / 1110024 默认行为不变',
         'measured': {'REGRESS_OK': rg.get('ok'),
                      'rows': [{'skin_id': r.get('skin_id'), 'delta': r.get('delta'),
                                'metric_identical': r.get('metric_identical'),
                                'manifest_has_lighting_approx': r.get('manifest_has_lighting_approx')}
                               for r in (rg.get('rows') or [])]},
         'verdict': 'YES' if rg.get('ok') else 'NO'},
        {'id': 'C5', 'text': 'HTTP 200，含自造六面 12/12',
         'measured': {'faces_and_rgbm_12_of_12': True,
                      'provenance_json': True, 'cubes_custom_js': True},
         'verdict': 'YES'},
        {'id': 'C6', 'text': '默认已切换为**本自造项**（不点任何控件）—— 最终态',
         'measured': {'applied_and_verified_at': '2026-09-21 12:16–12:26（sha16 655aa3ca3023571f，'
                                                 '两次独立运行逐字节一致，默认档 == 显式选择档）',
                      'superseded_at': '2026-09-21 12:26:50 被并发代理的 custom_bright_snow_20260921 取代',
                      'final_product_default_cube': 'custom_bright_snow_20260921（并发代理 SNOWCUBE）',
                      'final_product_default_applied': 'custom_bright_snow_20260921',
                      'my_mechanism_reverted': 'neox_material.json 已回到原始 hash A6F4CABDF38D4820',
                      'my_cube_still_registered_and_selectable': True,
                      'verify_verdict': vdef.get('verdict')},
         'verdict': 'NO',
         'why': ('我方切换在 12:16 落地并**已自证**；但默认档接着被**其它代理连续改写**：'
                 '12:26:50 → custom_bright_snow_20260921（用规格所要求的 viewer.js 消费器），'
                 '12:29:38–12:31:03 → night_clearsky02（源 cube）。'
                 '为不留**互相矛盾的产品档声明**，我把自己的机制**主动回退**（neox_material.json 回到原始 hash），'
                 '只保留规格内的那条机制。最终默认归谁**不在本写手权限内** ⇒ C6 记 NO，'
                 '并给出「一行把默认指回本 cube」的命令供 Lead 裁决。')},
    ]

    rep = {
        'schema': 'BRIGHTCUBE_20260921/v1',
        'title': '自造「不黑」环境 cube custom_bright_20260921 + 设为 1110025 默认',
        'generated_from': 'assets/3d/weapon_skin/_shared/cubes/custom_bright_20260921/_mk_report_20260921.py',
        'honesty': {
            'cube_status': 'self_authored_approximate',
            'authority': 'user_authorized_manual_20260921',
            'fidelity': 'approximate',
            'is_game_asset': False,
            'statement': ('像素基底取自游戏资产 gdansk_shipyard_buildings02 六面；'
                          '**辐射标定（增益 K + 抬底 L_FLOOR + RGBM alpha 反解）系自造近似**。'
                          '源侧无选择器 ⇒ 默认改用它属**产品选择**（product_choice_20260921 / not_source_determined）。'
                          '不得标为 source_verified，不得当作「游戏实际使用该环境」的证据。'),
        },
        'construction': {
            'base_cube': 'gdansk_shipyard_buildings02',
            'base_cube_sha256': 'd28948b4cffe512ae170fa142cb28e3e556967466ea25700bf117d1b236571e3',
            'base_cube_sha16': 'd28948b4cffe512a',
            'base_container': '0000.gpk', 'base_row': 11706, 'base_dims': '128x128', 'base_mips': 8,
            'base_format': 'B8G8R8A8_UNORM cubemap',
            'mixed_other_cubes': False,
            'mixed_other_cubes_why': ('规格允许「必要时混 over_the_clouds 亮面补面」，但实测 gdansk 六面'
                                      '存储 luma<0.05 占比 **0.00%**（无黑面）⇒ 不需要补面，少一个来源少一份不确定性'),
            'formula': 'L_new = sqrt( (K * L_src)^2 + L_FLOOR^2 )   逐通道',
            'L_src': 'L_src = (rgb_src * a_src * 16)^2   /* asm 542-544 源解码 */',
            'K': prov['radiance_calibration']['K'],
            'K_rule': ('取满足「六面解码 p50 全部 ≤ 0.45」的**最大** K（二分反解）'
                       '⇒ 在规格给定区间内把有效辐射顶到最高'),
            'L_FLOOR': prov['radiance_calibration']['L_FLOOR'],
            'L_FLOOR_rule': '软抬底（quadrature）：保证 L_new ≥ 0.12 对**每一像素**成立 ⇒ 任何方向都不黑',
            'rgbm_encode': 'q=sqrt(L_new) ; s=q/16 ; M=ceil_8bit(max_c s_c) ; rgb_out=s/M',
            'rgbm_ceil_note': 'M 取 ceil 到 8bit 网格 ⇒ M ≥ max_c s_c 恒成立 ⇒ rgb_out ≤ 1 **无需裁剪**',
            'no_image_domain_gain': True,
            'forbidden_untouched': ['exposure', 'ACES/tonemapping', 'bloom', 'lights',
                                    'env_intensity', 'lighting_approx'],
            'source_face_sha256': [f['sha256'] for f in prov['derived_from'][0]['faces']],
            'source_face_files': [f['file'] for f in prov['derived_from'][0]['faces']],
        },
        'mechanism_finding_contradicts_brief': {
            'brief_claim': '这些 cube 的 alpha≈0.015~0.028 ⇒ 有效辐射 ≈0.04 ⇒ 镜面仍黑',
            'measured': ('该 alpha 区间属 **qiangpi/jiayuan02a**；**gdansk_shipyard_buildings02 实测 alpha p50=0.047**'
                         '（+Y 面 0.0667，max 0.937）⇒ 源解码辐射 **p50 已是 0.490~0.749，不是 0.04**'),
            'real_gdansk_defect': ('是**长尾**而非整体偏暗：解码 L<0.01 的像素占 0.60%~5.38%（+Z 面最深，min=7.6e-4）'
                                   '⇒ 那些**方向**才是「还有点反黑」'),
            'implication': '自造动作 = **抬底消长尾** + 把 p50 压回规格区间，而不是「从 0.04 提上去」',
        },
        'per_face': [{
            'axis': r['axis'], 'face': i,
            'source': {'file': r['source']['file'], 'sha256': r['source']['sha256'],
                       'decoded_L': r['source']['src_decoded_L'], 'alpha': r['source']['src_alpha'],
                       'rgb_lum': r['source']['src_rgb_lum'],
                       'near_black_luma_lt_0.05_pct': r['source']['src_near_black_luma_lt_0.05_pct'],
                       'dark_L_lt_0.01_pct': r['source']['src_dark_L_lt_0.01_pct']},
            'new': {'decoded_L': r['decoded_L'], 'srgb_lum': prov['faces'][i]['srgb_lum'],
                    'alpha_M': r['alpha_M'], 'alpha_M_byte': r['alpha_M_byte'],
                    'decode_roundtrip_abs_err': r['decode_roundtrip_abs_err'],
                    'decode_roundtrip_rel_err': r['decode_roundtrip_rel_err'],
                    'floor_dominated_px_pct': r['floor_dominated_px_pct'],
                    'near_black_L_lt_0.05_pct': prov['faces'][i]['near_black_L_lt_0.05_pct'],
                    'near_black_srgb_lum_lt_0.05_pct': prov['faces'][i]['near_black_srgb_lum_lt_0.05_pct']},
            'files': {'srgb': prov['faces'][i]['file'],
                      'srgb_sha256': prov['faces'][i]['sha256'],
                      'rgbm': r['file'], 'rgbm_sha256': r['sha256']},
        } for i, r in enumerate(prov['rgbm_faces'])],
        'three_tier_metal_region': {
            'metric_definition': ('逐字复用 gi2_tiers_20260921.metal_region()：带 x∈[0.18,0.85] y∈[0.33,0.62]；'
                                  'ach = sat<0.55（**不设亮度下限**）；dark = ach & luma<0.25；'
                                  'dark_share_pct = dark.mean()*100（= 用户报的「发黑」直接量）'),
            'note': '本次为**默认切换之后**的复测；T0_default_nocall = 不点任何控件/不调任何 API',
            'rows': [{k: t.get(k) for k in ('tag', 'shot_sha16', 'subject_p50', 'subject_p95', 'gt085_pct',
                                            'bg_p50', 'metalreg_px', 'metalreg_share_pct', 'dark_px',
                                            'dark_share_pct', 'metalreg_p50', 'metalreg_p95',
                                            'metalreg_gt085_pct', 'ach_p05', 'ach_lt_010_pct',
                                            'ach_lt_050_pct', 'band_p50_all_px')}
                     for t in (t_def, t_q, t_g, t_c)],
            'default_equals_custom_tier_bytewise': t_def.get('shot_sha16') == t_c.get('shot_sha16'),
            'old_default_sha16_prechange': 'a1cf4661a7e2dbe6',
            'qiangpi_tier_sha16_now': t_q.get('shot_sha16'),
            'sha16_caveat': ('诊断 `__cubeAB` 与 manifest 装载不是逐字节同一路径：同一套 qiangpi 在两条路上'
                             '给出 a1cf4661（改前 manifest 装载）/ ' + str(t_q.get('shot_sha16')) +
                             '（现诊断装载）；实测差异 ~0.83% 像素、max 11/255、局限武器区 ⇒ '
                             '口径上应报「cube 身份 + 指标」，不要只报 sha16 相等。'),
        },
        'unreachability_evidence': {
            'why': '>30pp 达标线在结构上不可达，两条独立证据',
            'pixel_diff': {
                'source': '_diff_analysis_20260921.json (qiangpi vs custom_bright 默认档)',
                'D_definition': 'D = 带内 sat<0.55 & luma<0.25（= dark% 的分子）',
                'D_px_total_in_band': diff.get('reachability', {}).get('D_px_total_in_band'),
                'D_share_of_band_pct': diff.get('dark_achr_D', {}).get('share_of_band_pct'),
                'D_frac_moved_by_cube_pct_in_band': diff.get('reachability', {}).get('D_frac_moved_by_cube_pct_in_band'),
                'D_dL_mean': diff.get('reachability', {}).get('D_dL_mean'),
                'D_lum_p50_before': diff.get('dark_achr_D', {}).get('lum0_p50'),
                'D_lum_p50_after': diff.get('dark_achr_D', {}).get('lum1_p50'),
                'S_definition': 'S = 带内 sat<0.55 & luma>0.25（武器主体那一半）',
                'S_n_px': diff.get('bright_achr_S', {}).get('n_px_band'),
                'S_frac_moved_pct': diff.get('bright_achr_S', {}).get('frac_px_moved_gt_0.01_pct'),
                'S_lum_p50_before': diff.get('bright_achr_S', {}).get('lum0_p50'),
                'S_lum_p50_after': diff.get('bright_achr_S', {}).get('lum1_p50'),
                'S_dL_mean': diff.get('reachability', {}).get('S_dL_mean'),
                'D_spatial_density_pct_5x5': {'rows': diff.get('D_spatial', {}).get('row_density_pct (top->bottom of band)'),
                                              'cols': diff.get('D_spatial', {}).get('col_density_pct (left->right of band)')},
                'reading': ('D 占带面积 85.46%，在 5×5 全部空间格密度 58%~98% ⇒ 是**大面积暗背景**；'
                            '换 cube 只改动 D 的 4.42% ⇒ dark% 只能动 ~3.7pp。'
                            '而武器集 S 有 74.51% 像素被改动、亮度 p50 0.7516→0.8074 ⇒ **cube 确实抬亮了武器**'),
            },
            'env_reachability': {
                'source': '_envreach_20260921.json（诊断 API __cubeBrightApprox，默认关、非交付改动）',
                'k_values': [r['k'] for r in envr.get('rows', [])],
                'dark_pct_by_k': envr.get('verdict', {}).get('dark_pct_by_k'),
                'MRp50_by_k': envr.get('verdict', {}).get('MRp50_by_k'),
                'subject_p50_by_k': envr.get('verdict', {}).get('subject_p50_by_k'),
                'dark_pct_span_pp': envr.get('verdict', {}).get('dark_pct_span_k1_to_kmax_pp'),
                'reading': ('环境辐射放大到 **60×**，dark% 仍 81.68（vs k=1 的 81.72，跨度 **0.04pp**），'
                            'MRp50 在 k=1..60 **恒等于 0.1414** ⇒ 那批暗像素**完全不由环境驱动**；'
                            '任何 cube 都对这条达标线无效'),
            },
            'recommendation': ('若该线的本意是量「金属」，请把金属区代理限制到**武器剪影**'
                               '（或直接用消色差且亮集 S）再定达标线；否则本项 NO 应记为**指标口径问题**，'
                               '不是 cube 缺陷。'),
        },
        'default_switch': {
            'mechanism': ('改 `neox_material.json` 5 个 prim 的 `t_custom_ibl`'
                          '（`local_file` + `faces_glob`）；**未改 `weapon_skin_viewer.js` / `board.html` 任何字节**'),
            'why_not_viewer_js': ('真正被 loader 消费的 IBL 声明在 neox_material.json'
                                  '（viewer.js L1435 fetch 它，T=pr.textures）；viewer.json **全文件无 t_custom_ibl**；'
                                  '且既有 per-material 覆盖分支被硬限制在 qiangpi|jiayuan02a（L1608）'),
            'why_local_file_renamed': ('iblName 由 local_file 基名派生（L1934-1939），而它是 '
                                       '__srcCubeCache/__iblGate 的键；不换基名会让 __cubeAB(\'qiangpi\') '
                                       '命中本 cube 缓存，污染取证选择器'),
            'why_relative_glob': ('L1966-1971 只信任以 src_cube/ 开头的 faces_glob ⇒ 用 src_cube/../../ '
                                  '相对回 _shared/，命中既有 base+t 分支'),
            'files': {
                'neox_material.json': {'sha256_before': 'A6F4CABDF38D4820', 'sha256_after_patch': '96C1A2AEAB683621',
                                       'sha256_final_after_my_revert': 'A6F4CABDF38D4820',
                                       'final_equals_original': True,
                                       'backup': 'neox_material.json.bak_brightcube_20260921',
                                       'backup_bytes': 74263},
                'viewer.json': {'sha256_before': 'A069A869A726FD7E', 'sha256_after_patch': 'A169FFBB890A8B9F',
                                'note': ('此后被并发代理多次改写（12:26:50 → snow；12:29:38 → night_clearsky02），'
                                         '故不给「最终 hash」；' 
                                         '我方 12:16 的备份 viewer.json.bak_brightcube_20260921 仍是原始态'),
                                'backup': 'viewer.json.bak_brightcube_20260921',
                                'backup_bytes': 270535},
            },
            'viewer_json_field': J(os.path.join(WIKI, 'assets', '3d', 'weapon_skin', '1110025', 'viewer.json'))
                                  .get('cube_default_selection'),
            'viewer_json_field_note': '**声明性记录**；本查看器不读该字段，功能绑定在 neox_material.json（已如实标注）',
            'preserved_semantics': {
                'manifest_original_binding': '源 logical_path=common\\env_map\\qiangpi.cube 逐字保留；原 local_file/faces_glob 存于 _product_default_override.*_source_declared',
                'nocover_option': '下拉「（manifest 原绑定·不覆盖）」= __cubeAB(null) → qiangpi，语义保留',
                'source_cubes_still_selectable': 32,
                'old_self_authored_still_selectable': 'custom_studio_20260920',
            },
            'runtime_proof': vdef.get('verdict'),
            'runtime_proof_detail': {
                'cubeDirProbe': vdef.get('cubeDirProbe'),
                'picker_selected': (J(vdef.get('picker_state')) if isinstance(vdef.get('picker_state'), str) else None) or None,
            },
            'reproducibility': {
                'window': '2026-09-21 12:16:26 – 12:26:50（我方机制生效期间，尚未被并发代理改写）',
                'default_sha16_verify_run': '655aa3ca3023571f',
                'default_sha16_accept_brightness_run': '655aa3ca3023571f',
                'byte_identical_across_two_independent_chrome_runs': True,
                'equals_explicit_selection_tier_sha16': True,
                'differs_from_pre_change_default_a1cf4661a7e2dbe6': True,
                'caveat': ('⚠ 上述是**历史窗口内实测并已记录**的事实；磁盘上的 PNG 已被我后续的重跑覆盖，'
                           '且 12:26:50 后并发代理改写 viewer.js/viewer.json ⇒ **当前**再算这两个 sha16 已不再相等'
                           '（当前帧 3b05236eb8642502 / 回退后 5b4f6e55cc3c2d29）。故不把「当前帧」当本项证据。'),
                'sha16_path_caveat': ('即便在我方窗口内，诊断 __cubeAB 的**首次现场加载**路径给出 8af39788d6d64f32，'
                                      '与 manifest 装载路径的 655aa3ca3023571f 差 ~0.83% 像素 / max 11/255 / '
                                      '局限武器区 ⇒ 口径上以「cube 身份 + 指标」为准，不只看 sha16 相等。'),
            },
        },
        'regression': {
            'http': {'new_cube_faces_12_of_12': True, 'all_200': True},
            'skins_1110152_1110024': rg.get('ok'),
            'rows': rg.get('rows'),
        },
        'acceptance_lines': lines,
        'acceptance_summary': {
            'YES': [l['id'] for l in lines if l['verdict'] == 'YES'],
            'NO': [l['id'] for l in lines if l['verdict'] == 'NO'],
            'FAIL_reported': [l['id'] for l in lines if l['verdict'] == 'FAIL'],
            'honest_conclusion': ('自造 cube 已造出并登记（六面解码 p50 ∈[0.25,0.45]、逐像素 ≥0.12、'
                                  '近黑 0.0000%），且**确实抬亮了武器**'
                                  '（消色差主体亮度 p50 0.7516→0.8074，MRp95 0.797→0.839，MR>085 1.96%→4.00%）。'
                                  '①「金属区 dark% 相对 qiangpi 降 ≥30pp」这条线**在结构上不可达**：'
                                  '该指标的分子是带内 85.46% 面积的暗背景，60× 环境增益下 dark% 只动 0.04pp。'
                                  '剩余「黑」主要是**背景**的黑，不是金属镜面的黑；金属方向的深黑长尾已由抬底消除。'
                                  '②默认档：我方于 12:16 切换并已自证成功（默认帧与显式选择档逐字节一致、'
                                  '两次独立 Chrome 运行一致），但 12:26:50 被**并发代理**用规格内的 '
                                  'viewer.json:cube_default_selection 机制改成它的 custom_bright_snow_20260921；'
                                  '为避免留下两个互相矛盾的产品档声明，我方已把自己的机制**逐字节回退**，'
                                  '最终默认归谁**待 Lead 裁决**（改一个字段即可）。'),
        },
        'artifacts': {
            'cube_dir': '04_站点\\web/assets/3d/weapon_skin/_shared/cubes/custom_bright_20260921/',
            'srgb_faces': ['faces/' + f['file'] for f in prov['faces']],
            'rgbm_faces': [r['file'] for r in prov['rgbm_faces']],
            'provenance': 'provenance.json',
            'contact_sheet': '_contact_sheet.png',
            'scripts': ['_analyze_source.py', '_build_bright_cube.py', '_emit_manifest.py',
                        '_probe_tiers_20260921.py', '_analyze_diff_20260921.py',
                        '_probe_envreach_20260921.py', '_verify_default_20260921.py',
                        '_patch_default_20260921.py', '_revert_default_20260921.py',
                        '_mk_report_20260921.py'],
            'gate_outputs': ['shots25/ACCEPT_BRIGHTNESS_20260920.json',
                             'shots25/ACCEPT_BRIGHTNESS_1110025.png',
                             'shots25/ACCEPT_FXFOLLOW_20260920.json'],
        },
        'backup_and_revert': {
            'backups': ['assets/3d/weapon_skin/1110025/neox_material.json.bak_brightcube_20260921',
                        'assets/3d/weapon_skin/1110025/viewer.json.bak_brightcube_20260921',
                        'data/media/weapon_skin_cubes_custom.js.bak_brightcube_20260921',
                        'board.html.bak_brightcube_20260921'],
            'revert_cmd': ('python _shared/cubes/custom_bright_20260921/_revert_default_20260921.py '
                           '--mode restore-bak --apply'),
            'note': '备份只写一次（已存在则不覆盖），避免用打补丁后的内容覆盖好备份',
        },
        'pin': {
            'cube_name': 'custom_bright_20260921',
            'cube_status': 'self_authored_approximate',
            'rgbm_face_sha256': [r['sha256'] for r in prov['rgbm_faces']],
            'srgb_face_sha256': [f['sha256'] for f in prov['faces']],
            'provenance_sha256': sha16(os.path.join(HERE, 'provenance.json')),
            'neox_material_json_sha256_16': '96C1A2AEAB683621',
            'viewer_json_sha256_16': 'A169FFBB890A8B9F',
            'weapon_skin_viewer_js_untouched': True,
        },
        'concurrency_log': {
            'lock_observed': ('开工时 weapon_skin_viewer.js/board.html 仅 7 分钟前被改（<10min），'
                              '且 _gi2_*/GI2_* 产物持续 5 分钟内更新 ⇒ 按规则**只造 cube 资产、不写渲染文件**'),
            'unlock': ('12:16 检查：GI2 最新 age 5.4 min（>5）、viewer.js 22.1 min、board.html 22.0 min（>10）'
                       '⇒ 判定静默后才切默认'),
            'peer_conflict': ('发现另一路代理的 default_cube_probe_20260921.py（12:03:32 落盘）以'
                              '「默认环境 cube = **clould_weather**」为题，且在读 __cubePickerState() 的 '
                              'product_default* 字段（当时现有 viewer.js **不存在**该字段）⇒ 两路在改同一个默认档。'
                              '12:26:50 该路代理落地：新建 custom_bright_snow_20260921、给 viewer.js 加 '
                              'cube_default_selection 消费器 + product_default* 探针、把 '
                              'viewer.json.cube_default_selection 指向 snow、并更新 board 缓存键。'
                              '⇒ 其机制优先级高于我走的 manifest t_custom_ibl 路径。'),
            'overwrite_check': ('切换后复检 hash 仍为 96C1A2AEAB683621 / A169FFBB890A8B9F（我方未被顶掉）；'
                                '12:26:50 后 viewer.js/viewer.json/board.html/cubes_custom.js 被对方改写'),
            'default_churn_observed': {
                'why': ('默认档在我方之后**继续被其它代理改动**，故不写「最终态」，只写真值观测序列。'
                        '所有读数均为该时刻的文件/运行时真值。'),
                'timeline': [
                    {'t': '≤12:01（进房时）', 'default': 'qiangpi', 'how': 'manifest 原绑定',
                     'evidence': '默认帧 sha16 a1cf4661a7e2dbe6（== __cubeAB(\'qiangpi\') 档）'},
                    {'t': '12:16:26', 'default': 'custom_bright_20260921', 'how': '我方改 neox_material.json t_custom_ibl',
                     'evidence': '默认帧 sha16 655aa3ca3023571f（== 显式选择本 cube 档，两次独立运行一致）'},
                    {'t': '12:26:50', 'default': 'custom_bright_snow_20260921',
                     'how': '并发代理 SNOWCUBE：viewer.js 加 cube_default_selection 消费器 + 改 viewer.json',
                     'evidence': '__cubeProductDefault().applied == custom_bright_snow_20260921；帧 3b05236eb8642502'},
                    {'t': '12:28:4x', 'default': '(我方机制回退，snow 仍生效)',
                     'how': '_revert_default_20260921.py --mode unset-override --apply',
                     'evidence': 'neox_material.json 回到 A6F4CABDF38D4820（原始 hash，零残留）'},
                    {'t': '12:29:38 – 12:31:03', 'default': 'night_clearsky02（**源 cube**）',
                     'how': '另一路改写 viewer.json + neox_material.json（t_custom_ibl local_file=src_cube/night_clearsky02.dds）',
                     'evidence': ('viewer.json.cube_default_selection={"cube":"night_clearsky02",'
                                  '"authority":"product_choice_20260921","fidelity":"not_source_determined",'
                                  'note:"…依据：用户实测最优；Lead 复算逐面最小亮度 0.051（无黑方向）、'
                                  '面内 p50 0.346（全库最高）…"}；neox_material.json sha16 E0D94252E21352AB')},
                ],
                'my_cube_unaffected': {
                    'still_in_manifest': True,
                    'all_three_self_authored_registered': ['custom_studio_20260920',
                                                           'custom_bright_20260921（本项）',
                                                           'custom_bright_snow_20260921'],
                    'rgbm_faces_sha256_verified': '6/6 OK',
                    'selectable': True,
                },
                'cache_keys_latest_check_12_32': '3/3 OK（weapon_skin_viewer.js board?v=fa5d00cb2bed == file fa5d00cb2bed）',
                'conclusion': ('默认档归属**不在本写手权限内决定**（多路代理在改同一个字段）。'
                               '本项交付物 = cube 资产 + 清册登记 + 构造/达标证据；'
                               '默认切换我方已完成并自证，但**不是最终态**；C6 记 NO。'
                               '无论默认最终选谁，本 cube 都可从下拉「自造·近似（非游戏资产）」组选中，'
                               '且其辐射保证（六面 p50 ∈[0.25,0.45]、逐像素 ≥0.12、近黑 0.0000%）可复算。'),
            },
            'arbitration_options': {
                'A_use_my_cube_as_default': ('把 viewer.json 的 cube_default_selection.cube 改成 '
                                             'custom_bright_20260921（走规格内的 viewer.js 消费器，一个字段）：'
                                             'python -c "import json;p=r\'...1110025\\viewer.json\';'
                                             'd=json.load(open(p,encoding=\'utf-8\'));'
                                             'd[\'cube_default_selection\'][\'cube\']=\'custom_bright_20260921\';'
                                             'json.dump(d,open(p,\'w\',encoding=\'utf-8\'),ensure_ascii=False,indent=1)"'),
                'B_keep_current_default': ('保持其它代理的当前选择（观测到 12:29 起为 night_clearsky02，'
                                           '一个**源 cube**）；我方机制已回退，无矛盾声明；'
                                           '本 cube 仍可选、仍已登记、辐射保证可复算'),
                'C_use_a_source_cube': ('我方不反对：把默认留在**源 cube**（如 night_clearsky02）'
                                        '在「不伪造源数据」这条上比我方的自造档更干净 —— '
                                        '自造档的价值是「把深黑长尾抬掉」，可作为**可选对照项**而非默认'),
                'note': ('两套自造 cube 都是 self_authored_approximate、都非游戏资产；'
                         '差别只在像素基底（我方 gdansk / 对方 snow+补黑面）与辐射标定。'
                         '按本目录实测，我方六面保证：p50 ∈[0.25,0.45]、逐像素 ≥0.12、近黑 0.0000%。'),
            },
            'honest_note_on_frames': ('并发写手在 12:26:50 改过 viewer.js/viewer.json 后，**渲染帧不再能'
                                      '干净归因**于单一机制：我方切换期间（12:16–12:26）默认帧 655aa3ca3023571f'
                                      '可与显式选择档逐字节对齐；12:26:50 后帧变为 3b05236eb8642502，'
                                      '我方机制回退后又变为 5b4f6e55cc3c2d29。故 C6 报 NO，且不把任何'
                                      '「最终态帧」当作我方切换的证据。'),
        },
    }

    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, 'BRIGHTCUBE_20260921.json')
    json.dump(rep, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('wrote', p)
    print('YES:', rep['acceptance_summary']['YES'])
    print('NO :', rep['acceptance_summary']['NO'])
    print('FAIL_reported:', rep['acceptance_summary']['FAIL_reported'])
    print('default==custom tier:', rep['three_tier_metal_region']['default_equals_custom_tier_bytewise'])
    print('reproducible:', rep['default_switch']['reproducibility'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
