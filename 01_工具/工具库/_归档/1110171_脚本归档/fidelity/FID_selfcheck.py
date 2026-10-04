# -*- coding: utf-8 -*-
"""FID_selfcheck.py — 交付一致性自检：MD 数字 vs 各 JSON（fail-closed）。"""
import io, json, os, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
T = r'E:\la拆包项目\03拆包产物\_target_1110171'
F = os.path.join(T, 'fidelity')
md = io.open(os.path.join(T, 'FIDELITY_EVIDENCE_20260920.md'), encoding='utf-8').read()
d = json.load(io.open(os.path.join(T, 'FIDELITY_EVIDENCE_20260920.json'), encoding='utf-8'))
q1 = json.load(io.open(os.path.join(F, 'Q1_color_order.json'), encoding='utf-8'))
q2 = json.load(io.open(os.path.join(F, 'Q2_scriptscan.json'), encoding='utf-8'))
q4 = json.load(io.open(os.path.join(F, 'Q4_clamp_audit.json'), encoding='utf-8'))
checks = [
    ('MD 含 argb 结论', 'argb' in md and 'Q1｜颜色通道序' in md),
    ('Q1 1110177 argb=17 tie=10 rgba=1', q1['skin_level']['1110177']['verdict'] == {'argb': 17, 'rgba': 1, 'tie': 10}),
    ('Q1 1110171 argb=5 rgba=1 tie=1', q1['skin_level']['1110171']['verdict'] == {'argb': 5, 'rgba': 1, 'tie': 1}),
    ('MD 含 17:1 / 5:1', '17:1' in md and '5:1' in md),
    ('MD 含色相跳变 188.3/56.3', '188.3' in md and '56.3' in md),
    ('MD 含端点 27/28 与 4/28', '27/28' in md and '4/28' in md),
    ('Q2 扫描量 817281/15.43GB', q2['totals']['entries'] == 817281 and abs(q2['totals']['bytes_scanned'] / 1e9 - 15.43) < 0.02),
    ('MD 含 817,281 与 15.43 GB', '817,281' in md and '15.43 GB' in md),
    ('Q2 无枚举结论在 JSON', d['Q2_blend_enum']['verdict'].startswith('枚举表不在本机')),
    ('MD 含材质表 0–4 且声明不适用', 'ALPHA_BLEND_WRITE_Z' in md and '不是同一枚举' in md),
    ('Q2 BlendMode=7 第 4 高频出现（16,268）', '16,268' in md and d['Q2_blend_enum']['fx_blendmode_distribution_36008_sfx'].get('7') == 16268),
    ('MD 含 Q3 98.4% 与 15.0×1.07', '98.4%' in md and '16.05' in md),
    ('MD 含 Q4 0/13 与 0.539', '0/13' in md and '0.539' in md),
    ('Q4 两皮肤 0 触发', q4['all_nodes_worst']['1110177']['n_clamped_anywhere'] == 0 and q4['all_nodes_worst']['1110171']['n_clamped_anywhere'] == 0),
    ('Q4 13 行全 clamped=False', all(r['clamped'] is False for s in ('1110177', '1110171') for r in q4['analytic'][s]['rows'] if r['clamped'] is not None)),
    ('Q4 实测对拍 4 条一致', len(q4['analytic']['1110171'].get('runtime_match', {})) >= 4),
    ('JSON 基线含两 effects.json 哈希', 'sha16' in d['baseline']['effects_json_analyzed']['1110177']),
    ('MD 声明未改 wiki', '未改任何 wiki 文件' in md),
    ('JSON not_done 含未改 adapter', any('未改 adapter' in x for x in d['not_done'])),
]
bad = [c for c, ok in checks if not ok]
for c, ok in checks:
    print('  %s %s' % ('OK  ' if ok else 'FAIL', c))
print('\n自检：%d/%d 通过' % (len(checks) - len(bad), len(checks)))
sys.exit(1 if bad else 0)
