# -*- coding: utf-8 -*-
"""Q3_verdict2.py — Q3 裁决 v2：用**正确的寿命口径**（粒子用 Min/MaxSpriteLifespan，Sprite 用 FxLifeSpan）重算。

J1 rate 族群；J2 rate vs 隐含 fps 相关性；J3 两假设下的行为合理性（用正确寿命）；
J4 本任务 6 个节点（**按 (container,row) 精确取我们那把皮肤的 sfx**：hit=38420 / jisha=38433）。
"""
import io, json, math, os, sys
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171\fidelity'
corpus = json.load(io.open(os.path.join(OUT, 'Q3_corpus.json'), encoding='utf-8'))
KNOWN = {'lightning07_cs.spr': 16, 'lightning_01.spr': 16, 'shandian_05_yh_djs.spr': 4,
         'smoke25.spr': 64, 'tex_special_fangkuai_tp52.spr': 4}
KNOWN_PARAM = {'lightning07_cs.spr': 10000, 'lightning_01.spr': 10000, 'shandian_05_yh_djs.spr': 1000,
               'smoke25.spr': 10000, 'tex_special_fangkuai_tp52.spr': 1000}
CANON = {0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 10.0, 12.0, 15.0, 16.0, 20.0, 23.0, 24.0, 25.0, 30.0, 40.0, 50.0, 60.0}
OUR_ROWS = {'38420', '38433'}


def noderec(n, doc):
    try:
        rate = float(n.get('SprSpeedRate'))
    except Exception:
        return None
    tex = (n.get('Texture') or '').replace('\\', '/').split('/')[-1]
    d = {'name': n.get('Name'), 'tag': n.get('_tag'), 'tex': tex, 'rate': rate, 'work': n.get('SprWorkMode'),
         'node_life': None, 'sprite_life': None, 'container': doc['container'], 'row': str(doc['row']),
         'minl': n.get('MinSpriteLifespan'), 'maxl': n.get('MaxSpriteLifespan'), 'pps': n.get('ParticlesPerSecond')}
    for k, key in (('FxLifeSpan', 'node_life'), ('MinSpriteLifespan', 'sprite_life'), ('MaxSpriteLifespan', 'sprite_life_max')):
        try:
            d[key] = float(n.get(k)) if n.get(k) is not None else None
        except Exception:
            d[key] = None
    sl = [x for x in (d.get('sprite_life'), d.get('sprite_life_max')) if x]
    d['eff_life'] = (sum(sl) / len(sl)) if sl else d['node_life']
    d['N'] = KNOWN.get(tex)
    return d


sheet = []
for doc in corpus['sfx_docs']:
    for n in doc['nodes']:
        r = noderec(n, doc)
        if r and r['tex'].lower().endswith('.spr'):
            sheet.append(r)

resolvable = [x for x in sheet if x['N'] and x['eff_life'] and x['rate'] > 0]
print('=== 样本：.spr 节点 %d；可解析(N+寿命+rate>0) %d ===' % (len(sheet), len(resolvable)))
c = Counter(x['rate'] for x in sheet if 0 < x['rate'] < 1000)
tot = sum(c.values()); canon = sum(v for k, v in c.items() if k in CANON)
print('J1 rate>0 的 .spr 节点 %d，落在"人写帧率集合" %d (%.1f%%)' % (tot, canon, 100.0 * canon / max(1, tot)))
print('   非集合取值 top8: %s' % json.dumps([(k, v) for k, v in c.most_common(60) if k not in CANON][:8], ensure_ascii=False))


def pearson(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    vx = sum((x - mx) ** 2 for x in xs); vy = sum((y - my) ** 2 for y in ys)
    if vx <= 1e-12 or vy <= 1e-12:
        return None
    return sum((xs[i] - mx) * (ys[i] - my) for i in range(n)) / math.sqrt(vx * vy)


xs = [x['rate'] for x in resolvable]
ys = [x['N'] / x['eff_life'] for x in resolvable]
ratios = [y / x for x, y in zip(xs, ys)]
print('J2 Pearson(rate, N/eff_life) = %.4f；(N/eff_life)/rate 中位 %.2f；落在±10%% 的 %.1f%%' % (
    pearson(xs, ys), sorted(ratios)[len(ratios) // 2], 100.0 * sum(1 for r in ratios if 0.9 <= r <= 1.1) / len(ratios)))
adv = [x for x in resolvable if x['rate'] * x['eff_life'] >= 1.0]
one = [x for x in resolvable if 0.9 <= x['rate'] * x['eff_life'] / x['N'] <= 1.1]
strobe = [x for x in resolvable if x['N'] / x['eff_life'] > 120]
print('J3 用正确寿命：')
print('   H2(rate=fps)：至少推进过 1 帧的 %d/%d (%.1f%%)；正好播完一圈 %d (%.1f%%)' % (
    len(adv), len(resolvable), 100.0 * len(adv) / len(resolvable), len(one), 100.0 * len(one) / len(resolvable)))
print('   H1(按寿命均匀)：隐含 fps>120 的 %d (%.1f%%)；隐含 fps 落在帧率集合的 %.1f%%' % (
    len(strobe), 100.0 * len(strobe) / len(resolvable),
    100.0 * sum(1 for x in resolvable if round(x['N'] / x['eff_life'], 1) in CANON) / len(resolvable)))
# rate×life 的分布（H2 下的实际帧数）
fr = [x['rate'] * x['eff_life'] for x in resolvable]
print('   H2 实际帧数（rate×eff_life）分位：p10=%.2f 中位=%.2f p90=%.2f max=%.1f' % (
    sorted(fr)[len(fr) // 10], sorted(fr)[len(fr) // 2], sorted(fr)[len(fr) * 9 // 10], max(fr)))

print('\n=== J4 本任务节点（按 (container,row)=38420/38433 精确定位 1110177 的两份 sfx）===')
rows = []
for x in sheet:
    if x['row'] in OUR_ROWS:
        rows.append(x)
seen = set()
for x in rows:
    key = (x['name'], x['tex'])
    if key in seen:
        continue
    seen.add(key)
    N = x['N']
    print('   %-18s %-30s N=%-4s param=%-6s rate=%-7s node_life=%-7s spriteLife=%s/%s | H1隐含=%-8s H2=%-7s' % (
        x['name'], x['tex'], N, KNOWN_PARAM.get(x['tex']), x['rate'], x['node_life'], x['minl'], x['maxl'],
        ('%.1f fps' % (N / x['eff_life'])) if (N and x['eff_life']) else '-', '%.1f fps' % x['rate']))
print('   H_星点粒子（1110171, render_1003_010 bin）: tex_glow_tp07_02.spr N=4 param=1000 rate=0.000 life=1.000 work=1')
print('   → H1 隐含 4.0 fps（4 帧走 1 s）；H2 0.000 fps（整段不动，只有第 0 帧）')

json.dump({'sheet_nodes': len(sheet), 'resolvable': len(resolvable),
           'j1_canon_pct': 100.0 * canon / max(1, tot), 'j1_noncanon_top': [(k, v) for k, v in c.most_common(60) if k not in CANON][:10],
           'j2_pearson': pearson(xs, ys), 'j2_ratio_median': sorted(ratios)[len(ratios) // 2],
           'j2_within10_pct': 100.0 * sum(1 for r in ratios if 0.9 <= r <= 1.1) / len(ratios),
           'j3_h2_advance_pct': 100.0 * len(adv) / len(resolvable),
           'j3_h2_one_cycle_pct': 100.0 * len(one) / len(resolvable),
           'j3_h1_strobe_pct': 100.0 * len(strobe) / len(resolvable),
           'j3_h2_frames_p10_med_p90_max': [sorted(fr)[len(fr) // 10], sorted(fr)[len(fr) // 2],
                                            sorted(fr)[len(fr) * 9 // 10], max(fr)],
           'our_nodes': rows},
          io.open(os.path.join(OUT, 'Q3_verdict.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n-> Q3_verdict.json')
