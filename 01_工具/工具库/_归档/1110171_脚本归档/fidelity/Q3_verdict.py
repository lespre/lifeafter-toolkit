# -*- coding: utf-8 -*-
"""Q3_verdict.py — Q3 裁决：H1（按寿命均匀=现行）vs H2（SprSpeedRate = fps）在 36,008 份 sfx 大样本上的对拍。

判据：
  J1 **rate 取值族群**：若 rate 是 fps，其取值应集中在"人写的帧率数字"（1.5/5/10/15/20/23/30/50…）；
    若 H1 隐含 fps=N/life 才是真语义，rate 应与 N/life 高度相关（Pearson / 比值聚集）。
  J2 **相关性**：sheet 节点上 rate vs N/life 的相关系数与比值分布。
  J3 **行为差异**：两种假设下每个节点实际会播到第几帧（含 H2 的"永不推进"与 H1 的"频闪过快"反例计数）。
  J4 **渲染节点**：本任务 6 个 spr 节点的逐节点读数。
"""
import io, json, math, os, sys
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171\fidelity'
corpus = json.load(io.open(os.path.join(OUT, 'Q3_corpus.json'), encoding='utf-8'))
KNOWN = {'lightning07_cs.spr': 16, 'lightning_01.spr': 16, 'shandian_05_yh_djs.spr': 4,
         'smoke25.spr': 64, 'tex_special_fangkuai_tp52.spr': 4, 'tex_glow_tp07_02.spr': 4}
CANON = {0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 10.0, 12.0, 15.0, 20.0, 23.0, 24.0, 25.0, 30.0, 50.0, 60.0}

sheet, nonsheet = [], []
for doc in corpus['sfx_docs']:
    for n in doc['nodes']:
        r = n.get('SprSpeedRate')
        if r is None:
            continue
        try:
            rf = float(r)
        except Exception:
            continue
        tex = (n.get('Texture') or '').replace('\\', '/').split('/')[-1]
        try:
            life = float(n.get('FxLifeSpan')) if n.get('FxLifeSpan') is not None else None
        except Exception:
            life = None
        rec = {'name': n.get('Name'), 'tag': n.get('_tag'), 'tex': tex, 'rate': rf, 'life': life,
               'work': n.get('SprWorkMode'), 'container': doc['container'], 'row': doc['row'],
               'minl': n.get('MinSpriteLifespan'), 'maxl': n.get('MaxSpriteLifespan'),
               'pps': n.get('ParticlesPerSecond')}
        # 只保留"带 .spr 表"或"带单帧贴图"的节点
        if tex.lower().endswith('.spr'):
            rec['N'] = KNOWN.get(tex)
            sheet.append(rec)
        elif tex.lower().endswith(('.tga', '.dds', '.png')):
            nonsheet.append(rec)


def pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    vx = sum((x - mx) ** 2 for x in xs); vy = sum((y - my) ** 2 for y in ys)
    if vx <= 1e-12 or vy <= 1e-12:
        return None
    return sum((xs[i] - mx) * (ys[i] - my) for i in range(n)) / math.sqrt(vx * vy)


print('=== 样本量 ===')
print('  .spr 贴图节点 %d（其中可解析 N 的 %d）；单帧贴图节点 %d' % (
    len(sheet), sum(1 for x in sheet if x['N']), len(nonsheet)))
print('\n=== J1 rate 取值族群（.spr 节点，rate>0 且 <1000）===')
c = Counter(x['rate'] for x in sheet if 0 < x['rate'] < 1000)
tot = sum(c.values())
canon_hits = sum(v for k, v in c.items() if k in CANON)
print('  rate>0 的 .spr 节点 %d；其中落在"人写帧率集合"C 的 %d (%.1f%%)' % (tot, canon_hits, 100.0 * canon_hits / max(1, tot)))
print('  非 C 的取值（top10，说明这些不是帧率画风）:', json.dumps([(k, v) for k, v in c.most_common(40) if k not in CANON][:10], ensure_ascii=False))

resolvable = [x for x in sheet if x['N'] and x['life'] and x['rate'] > 0]
xs = [x['rate'] for x in resolvable]
ys = [x['N'] / x['life'] for x in resolvable]
print('\n=== J2 相关性（可解析 N 且 rate>0 的 .spr 节点，n=%d）===' % len(resolvable))
print('  Pearson(rate, N/life) = %s' % (None if pearson(xs, ys) is None else round(pearson(xs, ys), 4)))
ratios = [x['N'] / x['life'] / x['rate'] for x in resolvable]
print('  (N/life)/rate 比值：min=%.3f 中位=%.3f max=%.3f' % (min(ratios), sorted(ratios)[len(ratios) // 2], max(ratios)))
print('  比值落在 [0.9,1.1] 的比例：%.1f%%（若 H1==H2 应接近 100%%）' % (
    100.0 * sum(1 for r in ratios if 0.9 <= r <= 1.1) / max(1, len(ratios))))
# 隐含 fps 的族群
h1c = Counter(round(x['N'] / x['life'], 1) for x in resolvable)
print('  H1 隐含 fps 落在 C 的比例：%.1f%%' % (100.0 * sum(v for k, v in h1c.items() if k in CANON) / max(1, sum(h1c.values()))))
print('  H1 隐含 fps 的极端值（>120fps 数量）: %d / %d' % (sum(1 for x in resolvable if x['N'] / x['life'] > 120), len(resolvable)))

print('\n=== J3 行为差异（可解析 N 的 .spr 节点）===')
never = [x for x in resolvable if x['rate'] * x['life'] < 1.0]
strobe = [x for x in resolvable if x['N'] / x['life'] > 120]
print('  H2 下"整段寿命连第 1 帧都没走完"（rate×life<1）: %d 个 (%.1f%%)' % (len(never), 100.0 * len(never) / max(1, len(resolvable))))
print('  H1 下"隐含 fps>120（频闪）"                : %d 个 (%.1f%%)' % (len(strobe), 100.0 * len(strobe) / max(1, len(resolvable))))
print('  H2 下 rate×life/N ∈[0.9,1.1]（正好播完一圈）: %d 个 (%.1f%%)' % (
    sum(1 for x in resolvable if 0.9 <= x['rate'] * x['life'] / x['N'] <= 1.1),
    100.0 * sum(1 for x in resolvable if 0.9 <= x['rate'] * x['life'] / x['N'] <= 1.1) / max(1, len(resolvable))))

print('\n=== J4 本任务 6 个 spr 节点的逐节点读数（源值）===')
TASK_NODES = ['H_p_闪电', 'H_ shandian01_1_1', 'M_lizi_闪电_01', 'H_p_烟雾_02', 'H_鬼火_星点_1', 'H_星点粒子']
# 1110171 的 H_星点粒子 不在 effect_01/02 corpus（它来自 render_1003_010 的 sfx bin）
rows = []
for nm in TASK_NODES:
    lst = [x for x in sheet if x['name'] == nm]
    if not lst:
        print('   %-18s （不在 gpk 扫描范围；1110171 的节点见 Q3_spr_timing.json：rate=0.000 / work=1 / tex_glow_tp07_02.spr N=4）' % nm)
        continue
    for x in lst[:2]:
        N = x['N']
        print('   %-18s %-28s N=%-4s param=%-6s rate=%-7s life=%-7s | H1隐含fps=%-8s H2(rate)=%-7s | H2帧@u=0.5=%-3s H1帧@u=0.5=%s' % (
            nm, x['tex'], N, {'lightning07_cs.spr': 10000, 'lightning_01.spr': 10000, 'shandian_05_yh_djs.spr': 1000,
                              'smoke25.spr': 10000, 'tex_special_fangkuai_tp52.spr': 1000}.get(x['tex'], '?'),
            x['rate'], x['life'],
            ('%.1f' % (N / x['life'])) if (N and x['life']) else '-', '%.1f fps' % x['rate'],
            (min(N - 1, int(0.5 * x['life'] * x['rate'])) if (N and x['life']) else '-'),
            (min(N - 1, int(0.5 * N)) if N else '-')))
        rows.append(x)

# 1110171 的 6 号节点（源在 render_1003_010 bin）
print('   H_星点粒子           tex_glow_tp07_02.spr      N=4    param=1000  rate=0.000   life=1.000   | work=1; H1隐含fps=4.0  H2=0.000 fps')

# WorkMode 联合分布
wm = Counter((x['work'], 'rate=0' if x['rate'] == 0 else ('rate=1' if x['rate'] == 1 else 'rate>1<1')) for x in sheet)
print('\n=== SprWorkMode × rate 联合分布（.spr 节点）%s ===' % json.dumps({str(k): v for k, v in wm.most_common()}, ensure_ascii=False))
wm2 = Counter((x['work'], 'rate=0' if x['rate'] == 0 else ('rate=1' if x['rate'] == 1 else 'other')) for x in nonsheet)
print('=== SprWorkMode × rate 联合分布（单帧 .tga 节点）%s ===' % json.dumps({str(k): v for k, v in wm2.most_common()}, ensure_ascii=False))

json.dump({'sheet_nodes': len(sheet), 'resolvable': len(resolvable), 'nonsheet': len(nonsheet),
           'pearson_rate_vs_implied_fps': pearson(xs, ys),
           'ratio_dist': {'min': min(ratios), 'median': sorted(ratios)[len(ratios) // 2], 'max': max(ratios)},
           'ratio_within_10pct': 100.0 * sum(1 for r in ratios if 0.9 <= r <= 1.1) / max(1, len(ratios)),
           'canon_hit_rate': 100.0 * canon_hits / max(1, tot),
           'h1_implausible_gt120fps': len(strobe), 'h2_never_advance': len(never),
           'h2_exact_one_cycle_frac': 100.0 * sum(1 for x in resolvable if 0.9 <= x['rate'] * x['life'] / x['N'] <= 1.1) / max(1, len(resolvable)),
           'workmode_joint': {str(k): v for k, v in wm.most_common()},
           'workmode_joint_nonsheet': {str(k): v for k, v in wm2.most_common()},
           'task_node_rows': rows},
          io.open(os.path.join(OUT, 'Q3_verdict.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n-> Q3_verdict.json')
