# -*- coding: utf-8 -*-
"""FID_build.py — 组装 task-90 交付 JSON（把四个问题的读数汇总成一份机读件）。"""
import datetime, hashlib, io, json, os, sys
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
T = r'E:\la拆包项目\03拆包产物\_target_1110171'
F = os.path.join(T, 'fidelity')
OUT = os.path.join(T, 'FIDELITY_EVIDENCE_20260920.json')
W = r'E:\la拆包项目\08Lifeafter wiki'


def load(p):
    return json.load(io.open(p, encoding='utf-8'))


def sha16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16] if os.path.isfile(p) else None


q1 = load(os.path.join(F, 'Q1_color_order.json'))
q2s = load(os.path.join(F, 'Q2_scriptscan.json'))
q2b = load(os.path.join(F, 'Q2_blend_analysis.json'))
q3 = load(os.path.join(F, 'Q3_verdict.json'))
q3s = load(os.path.join(F, 'Q3_spr_timing.json'))
q4 = load(os.path.join(F, 'Q4_clamp_audit.json'))

# wiki 基线（未改动的证明）
wiki = {}
for rel in ('assets/weapon_skin_viewer.js', 'board.html',
            'assets/3d/weapon_skin/1110177/neox_material.json', 'assets/3d/weapon_skin/1110171/neox_material.json',
            'assets/weapon_skin_sfx_adapter.js'):
    p = os.path.join(W, rel.replace('/', os.sep))
    wiki[rel] = {'sha16': sha16(p), 'bytes': os.path.getsize(p) if os.path.isfile(p) else None,
                 'changed_by_env_auditor': False}
effects = {}
for sid in ('1110177', '1110171'):
    p = os.path.join(W, 'assets', '3d', 'weapon_skin', sid, 'effects.json')
    effects[sid] = {'bytes': os.path.getsize(p), 'sha16': sha16(p)}

out = {
    'schema': 'FIDELITY_EVIDENCE/v1',
    'task': 'task-90',
    'owner': 'env-auditor',
    'date': '2026-09-20',
    'write_scope': '03拆包产物/_target_1110171/FIDELITY_EVIDENCE_20260920.md|.json|fidelity/**（源包只读；未写 08Lifeafter wiki/**）',
    'baseline': {
        'effects_json_analyzed': effects,
        'wiki_files_untouched_by_me': wiki,
        'note': 'adapter 现值 AC7D71B6E58ABB7B 是 Lead 的 kinVel 改动；我全程只读它取行号，未写入',
        'toolkit_readonly': {'gpk_npk_index.py': sha16(r'E:\la拆包项目\01拆包器本体\工具库\06_皮肤定位链\gpk_npk_index.py'),
                             'npk_reader.py': sha16(r'E:\la拆包项目\01拆包器本体\01_核心解包器\npk_reader.py')},
    },
    'Q1_color_order': {
        'verdict': 'argb（alpha=列0，RGB=列1..3）',
        'level': '已证（强）',
        'samples': {sid: {'multi_key_tracks': len(q1['tracks_multi'][sid]),
                          'const_tracks': len(q1['tracks_const'][sid]),
                          'verdict_counts': q1['skin_level'][sid]['verdict']} for sid in ('1110177', '1110171')},
        'criteria': {sid: {k: q1['skin_level'][sid][k] for k in
                           ('hue_cluster_rgba', 'hue_cluster_argb', 'endpoint_exact', 'mean_hue_jump_rgba',
                            'mean_hue_jump_argb', 'mean_mono_rgba', 'mean_mono_argb')} for sid in ('1110177', '1110171')},
        'tracks_multi': {sid: [{k: r[k] for k in ('idx', 'name', 'tag', 'track', 'n_keys', 'verdict', 'votes',
                                                  'rgba', 'argb')} for r in q1['tracks_multi'][sid]]
                         for sid in ('1110177', '1110171')},
        'tracks_const': q1['tracks_const'],
        'shared_constant': q1['shared_constant'],
        'adapter_implication': {
            'current_default': "COLOR_ORDER='rgba'（adapter L93）",
            'paths': {
                'sprite_tick_L814_815': 'rgba ⇒ A=列3/RGB=列0..2；切 argb ⇒ A=列0/RGB=列1..3',
                'particle_updateParticles_L742': '写死 A=列0/RGB=列1..3（=argb），忽略 COLOR_ORDER',
                'model_mdlRGB_L223_227_alpha_L323': 'RGB=列0..2(rgba) 与 alpha=列0 ⇒ 列0 被同时当 R 与 A（自相矛盾）；切 argb 后一致',
            },
            'apply_by': "WikiSfxAdapter.colorOrder('argb')（adapter L1102）",
            'visible_node_impact': {
                '1110177_5_nodes': '全为 ParticleSystem（粒子路径已 argb）⇒ 切开关后不变',
                '1110171_8_nodes': '4 个 Sprite 走 rgba ⇒ 切 argb 后变色（例 M_g_光晕暗_01 [116,9,12,93]：rgba α=93/RGB=(116,9,12) → argb α=116/RGB=(9,12,93)）',
            },
        },
        'corollary_findings': [
            'adapter 只采样 color_track（L613/L741/L889），未用 color_track_par；1110177 的 28 条多键轨道里 15 条在 par，1110171 的 7 条全部在 par',
            '源 .sfx 实测：粒子节点 ColorFrame 是单键编辑器默认值 (255,92,243,107)（两皮肤 22 个粒子节点全同值），真实渐变在 ColorFramePar（5 键）⇒ 现渲染用的是默认常数而非 ramp',
        ],
    },
    'Q2_blend_enum': {
        'verdict': '枚举表不在本机数据内（NOT_FOUND_IN_LOCAL_DATA）',
        'level': '已证（否定）',
        'scanned': {
            'npk_containers': q2s['totals']['containers'], 'npk_entries': q2s['totals']['entries'],
            'npk_unpacked': q2s['totals']['unpacked'], 'npk_fail': q2s['totals']['fail'],
            'npk_bytes_scanned': q2s['totals']['bytes_scanned'],
            'npk_seconds': round(sum(c['seconds'] for c in q2s['containers']), 1),
            'sfx_docs': 36008, 'sfx_nodes_with_attrs': 248227, 'spr_headers': 714,
            'mtg_files': 33, 'client_bin_task30': {'files': 1017, 'bytes': 4256107398, 'game_module_hits': 0},
        },
        'kw_counts': q2s['kw_counts'],
        'per_container': [{k: c[k] for k in ('npk', 'entries', 'unpacked', 'fail', 'bytes_scanned', 'hits',
                                             'entries_with_hit', 'seconds')} for c in q2s['containers']],
        'hit_nature': {
            'res_npk': '着色器反射/渲染状态字段名表（SrcBlend/AlphaBlendEnable/DestBlend…）；含 c159 FxGroup 类型描述符（只列属性名，无成员枚举）',
            'script_npk': '全为"动画混合"：is_blend_mode/_has_init_blend_mode/blend_percent/blend_speed/blend_anim_controller、GmBlendOP、CameraBlendMode、curveBlendMode',
            'mtg': '只有 RenderStates 字段名 TransparentMode，无枚举成员',
            'project_grep': '仅 three.js 的 NormalBlending/AdditiveBlending',
        },
        'material_enum_found_but_not_applicable': {
            'source': 'res.npk entry 1388/6090（6,019 B 着色器宏头）',
            'table': {'0': 'ALPHA_UNKONWN', '1': 'OPAQUE', '2': 'ALPHA_BLEND', '3': 'ALPHA_TEST', '4': 'ALPHA_BLEND_WRITE_Z'},
            'why_not_usable': '这是材质 DEFAULT_BLEND_MODE 枚举（值域 0–4），而 FX 节点 BlendMode 实测取值 0/2/3/5/6/7/8（含 5/6/7/8 超出值域）⇒ 不同枚举，禁止挪用',
        },
        'fx_blendmode_distribution_36008_sfx': q2b['blendmode_dist'],
        'value7_instances_sample': q2b['value7_examples'][:8],
        'value7_total': q2b['value7_total'],
        'nonnumeric_values_found': q2b['nonnumeric_values'],
        'recommendation': [
            '7 保持保守 normal（现状）——本地无任何证据支持 additive；观测分布不得用于命名',
            '必修一致性 bug：BLEND[n.blend_mode] || "additive"（adapter L424/L591/L823）使未收录的 3/6 落 additive，而 7 被特殊保守为 normal；建议统一为保守默认',
            '若要定证 7，只剩引擎二进制逆向或运行时逐值 A/B 实拍（需 Lead 裁决）',
        ],
    },
    'Q3_spr_timing': {
        'verdict': '源里有 SprSpeedRate（帧率画风，98.4%）但单位未定证；现行"按寿命均匀"与它不一致',
        'level': '强推断（非文档级直证）',
        'source_fields': [{k: r.get(k) for k in ('name', 'tex', 'rate', 'work', 'node_life', 'minl', 'maxl', 'N', 'tag')}
                          for r in q3['our_nodes']],
        'spr_headers': q3s['spr_headers'],
        'j1_rate_population': {'spr_nodes_rate_gt0': 31004, 'in_human_fps_set': 30494, 'pct': q3['j1_canon_pct'],
                               'non_set_top': q3['j1_noncanon_top']},
        'j2_relation_to_current': {'pearson_rate_vs_N_over_life': q3['j2_pearson'],
                                   'ratio_median': q3['j2_ratio_median'], 'within_10pct': q3['j2_within10_pct']},
        'j3_behaviour': {'h2_advance_pct': q3['j3_h2_advance_pct'], 'h2_one_cycle_pct': q3['j3_h2_one_cycle_pct'],
                         'h1_strobe_pct': q3['j3_h1_strobe_pct'],
                         'h2_frames_p10_med_p90_max': q3['j3_h2_frames_p10_med_p90_max']},
        'formula_proposal': "rate>0: fi = floor(age * rate) mod N；rate<=0: fi = 0（锁首帧）——建议做成 SPR_FRAME_MODE='rate' 开关，默认仍 'age'",
        'counterexamples': [
            'rate=1.0 且寿命<1s 的节点（H_p_闪电、M_lizi_闪电_01）在 H2 下几乎不动（永远第0帧），与"作者为何配 4/16 帧图集"冲突',
            'H2 下 33.8% 节点寿命内不足 1 帧；只有 0.2% 正好播一圈',
            '.spr param（10000/1000）语义未定证；"每帧时长"解释被否（10000 ⇒ 1s/帧）',
        ],
    },
    'Q4_clamp': {
        'verdict': '钳制没有削掉任何源尺寸：13 个可渲染节点 0 触发',
        'level': '已证',
        'formula': 'raw = max(U(radius_or_particle_radius) * scaleTrack, 0.02)，U(v)=v*0.1（全局 SFX_UNIT_TO_MODEL，adapter L427）；cap = weapon_diag * 0.6（L429-433）',
        'weapon_diag_measured': q4['weapon_diag'],
        'cap': {sid: q4['analytic'][sid]['cap'] for sid in ('1110177', '1110171')},
        'per_node': {sid: [{k: r.get(k) for k in ('idx', 'name', 'tag', 'kind', 'radius_case', 'source_radius',
                                                  'quad_raw_analytic', 'cap', 'clamped', 'ratio_raw_over_cap', 'note')}
                           for r in q4['analytic'][sid]['rows']] for sid in ('1110177', '1110171')},
        'runtime_readings_matched': {sid: q4['analytic'][sid].get('runtime_match', {}) for sid in ('1110177', '1110171')},
        'runtime_sources': q4['runtime_sources'],
        'worst_case_any_node': {sid: {'cap': q4['all_nodes_worst'][sid]['cap'],
                                      'max_ratio': q4['all_nodes_worst'][sid]['max_ratio'],
                                      'n_clamped_anywhere': q4['all_nodes_worst'][sid]['n_clamped_anywhere'],
                                      'top3': q4['all_nodes_worst'][sid]['top10'][:3]} for sid in ('1110177', '1110171')},
        'historical_motivation_correction': 'K=0.6 的注释依据"70.71 = 武器 4.58×"来自未做单位换算的旧路径（radius=50 当 50 世界单位）；现行 U=0.1 后同节点仅 5.0 单位 = 0.324×武器对角线 ⇒ 当年"一大块"是缺单位换算，不是被钳制修好的；钳制现为恒不触发的惰性保险',
    },
    'proven': ['Q1=argb（28+7 条多键轨道的多数判据 + 3.3x/2.1x 色相平滑 + 端点闭合 + 金系色相聚类）',
               'Q2 枚举表不在本机（15 NPK/817,281 条目/15.43 GB + 36,008 sfx + 33 mtg + 4.26 GB 客户端二进制）',
               'Q4 钳制 0/13 触发；解析与 4 处实测逐位吻合；全皮肤最坏 raw/cap=0.539',
               'Q3 源字段事实：SprSpeedRate 帧率画风（98.4%）+ 15×1.07≈16 帧；.spr param 10000/1000 两档存在'],
    'unproven': ['ColorFramePar 语义（adapter 未消费 color_track_par ⇒ 粒子 ramp 未生效）',
                 '.spr param 含义；SprSpeedRate 单位（fps 为强推断）；SprWorkMode(0/1) 语义',
                 'FX BlendMode 的值→名（7 与 6/3 均 unresolved）'],
    'not_done': ['未改 adapter/viewer/effects.json/board（零写入）', '未开浏览器；未做运行时 A/B 实拍',
                 '未反汇编引擎二进制'],
    'scripts': ['fidelity/Q1_color_order_v2.py', 'fidelity/Q2_scriptscan.py', 'fidelity/Q2_blend_analysis.py',
                'fidelity/Q3_corpus_scan.py', 'fidelity/Q3_spr_timing.py', 'fidelity/Q3_verdict2.py',
                'fidelity/Q4_clamp_audit.py'],
    'perf_note': 'Q2 扫法三版：逐关键词 finditer（>10 min 未完成）→ 合并交替正则（1.77 GB/99.6 s）→ bytes.count 预筛（15.43 GB/247 s）',
    'hits_evidence_dir': 'fidelity/q2_payloads/（56 个含 BlendMode 的载荷原文）',
}
json.dump(out, io.open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('-> %s  %.2f MB' % (OUT, os.path.getsize(OUT) / 1e6))
chk = json.load(io.open(OUT, encoding='utf-8'))
assert chk['Q1_color_order']['verdict'].startswith('argb')
assert chk['Q2_blend_enum']['scanned']['npk_entries'] == 817281
assert chk['Q4_clamp']['verdict'].startswith('钳制没有')
print('复核通过：可再读、三个关键结论字段正确')
