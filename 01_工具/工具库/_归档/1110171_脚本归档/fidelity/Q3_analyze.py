# -*- coding: utf-8 -*-
"""Q3_analyze.py — Q3 阶段 2：用 36,008 份 .sfx + 714 个 .spr 头的大样本检验帧推进假设。

假设：
  H1（现行实现）帧索引按 `age / LifeSpan` 均匀推进 ⇒ 隐含 fps = N / life。
  H2 `SprSpeedRate` = **帧/秒(fps)** ⇒ 帧索引 = floor(age × SprSpeedRate)（mod N）。
  H3 `SprSpeedRate` = 每寿命播放圈数 ⇒ fps = N × rate / life。
  H4 `.spr 的 param` 是每帧时长（1/10000 s）⇒ fps = 10000 / param。
判据：对"有 .spr 贴图且能解析出 N"的节点，比较 rate 与 N/life（H1 隐含 fps），并统计 rate×life/N 的分布。
"""
import io, json, math, os, re, sys
from collections import Counter, defaultdict
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171\fidelity'
corpus = json.load(io.open(os.path.join(OUT, 'Q3_corpus.json'), encoding='utf-8'))
sfx_docs, spr_headers = corpus['sfx_docs'], corpus['spr_headers']

# ---- .spr 头：name -> (N, param, mode, sheet, row) ----
rx_rectname = re.compile(rb'\r?\n([^\r\n]+?\.tga)[ \t]')
spr_map = {}
for h in spr_headers:
    # 需要重读该行载荷拿"内层名"；改为从 corpus 里已存的头 + 重新扫描 gpk 代价高 ⇒ 用 rect 名近似：
    # corpus 未存内层名 ⇒ 用 (container,row) 反查不可行；改由下面 resolve 用 nodes 的 Texture 名做匹配集
    spr_map[(h['container'], h['row'])] = h
print('spr 头 %d；sfx 文档 %d' % (len(spr_headers), len(sfx_docs)))

# 由于 corpus 未存 .spr 内层名，这里按 **四元组 (mode,sheet,N,param) 出现频次** 统计；
# 渲染节点那 6 个 .spr 的内层名已在 Q3_spr_timing.json 里给出（磁盘文件）。
spr_multi = Counter((h['mode'], h['sheet'][0], h['sheet'][1], h['n_frames'], h['param']) for h in spr_headers)
print('\n=== .spr 头形态分布（mode,W,H,N,param）→ 计数 top15 ===')
for k, v in spr_multi.most_common(15):
    print('   %-28s %d' % (str(k), v))
print('唯一形态 %d 种；N 分布: %s' % (len(spr_multi), json.dumps(dict(Counter(h['n_frames'] for h in spr_headers).most_common(12)), ensure_ascii=False)))
print('param 分布: %s' % json.dumps(dict(Counter(h['param'] for h in spr_headers).most_common(12)), ensure_ascii=False))

# ---- 所有 sfx 节点的 SprSpeedRate 分布 ----
rate_all = Counter()
rate_spr_tex = Counter()
sheet_nodes = []
for doc in sfx_docs:
    for n in doc['nodes']:
        r = n.get('SprSpeedRate')
        if r is None:
            continue
        try:
            rf = float(r)
        except Exception:
            continue
        rate_all[r] += 1
        tex = n.get('Texture') or ''
        if tex.lower().endswith('.spr'):
            rate_spr_tex[r] += 1
            sheet_nodes.append({'container': doc['container'], 'row': doc['row'], 'name': n.get('Name'),
                                'tex': tex.replace('\\', '/').split('/')[-1], 'rate': rf,
                                'work': n.get('SprWorkMode'), 'life': n.get('FxLifeSpan'),
                                'minl': n.get('MinSpriteLifespan'), 'maxl': n.get('MaxSpriteLifespan'),
                                'pps': n.get('ParticlesPerSecond'), 'tag': n.get('_tag')})
print('\n=== SprSpeedRate 取值分布（全部节点 n=%d）===' % sum(rate_all.values()))
print('   ', json.dumps(dict(rate_all.most_common(20)), ensure_ascii=False))
print('=== 其中"贴图是 .spr"的节点（n=%d）===' % len(sheet_nodes))
print('   rate 分布:', json.dumps(dict(rate_spr_tex.most_common(20)), ensure_ascii=False))

# ---- 用磁盘上 6 个 .spr 的真实 N/param 做判据（这 6 个是渲染节点的 atlas） ----
KNOWN = {
    'lightning07_cs.spr': {'N': 16, 'param': 10000, 'mode': 1},
    'lightning_01.spr': {'N': 16, 'param': 10000, 'mode': 1},
    'shandian_05_yh_djs.spr': {'N': 4, 'param': 1000, 'mode': 0},
    'smoke25.spr': {'N': 64, 'param': 10000, 'mode': 1},
    'tex_special_fangkuai_tp52.spr': {'N': 4, 'param': 1000, 'mode': 0},
    'tex_glow_tp07_02.spr': {'N': 4, 'param': 1000, 'mode': 0},
}
print('\n=== 判据表：渲染节点用的 6 个 .spr（含 1110177 的 5 个 + 1110171 的 1 个）===')
print('%-30s %-4s %-6s %-8s %-8s %-10s %-12s %-12s' % ('spr', 'N', 'param', 'rate', 'life', 'H1 隐含fps', 'H2(rate=fps)', 'rate×life/N'))
for k, v in KNOWN.items():
    nodes = [x for x in sheet_nodes if x['tex'] == k]
    if not nodes:
        # 该 spr 只在 1110171 的 sfx 里出现
        continue
    for x in nodes:
        life = float(x['life']) if x['life'] else None
        h1 = (v['N'] / life) if life else None
        print('%-30s %-4d %-6d %-8.3f %-8s %-10s %-12s %-12s' % (
            k, v['N'], v['param'], x['rate'], x['life'],
            ('%.1f' % h1) if h1 else '-', '%.3f fps' % x['rate'],
            ('%.3f' % (x['rate'] * life / v['N'])) if life else '-'))
    if not nodes:
        print('%-30s %-4d %-6d %-8s %-8s %-10s %-12s %-12s   （本 corpus 无该节点；1110171 单独见 Q3_spr_timing.json）' % (
            k, v['N'], v['param'], '-', '-', '-', '-', '-'))

# ---- H2 全样本检验：对 .spr 节点，用同族 (mode,sheet,N,param) 不唯一 ⇒ 只在可解析子集上做 ----
print('\n=== H2 间接检验：Sheet 节点 rate 是否 = N/life（= 现行实现隐含 fps）===')
ok = bad = unknown = 0
examples = []
for x in sheet_nodes:
    v = KNOWN.get(x['tex'])
    if not v or not x['life']:
        unknown += 1
        continue
    life = float(x['life'])
    h1 = v['N'] / life
    if abs(h1 - x['rate']) / max(1e-9, x['rate']) < 0.05:
        ok += 1
    else:
        bad += 1
        examples.append((x['tex'], v['N'], life, x['rate'], h1, x['container'], x['row'], x['name']))
print('  可判定 %d：rate==N/life %d，不等 %d；不可判定 %d' % (ok + bad, ok, bad, unknown))
for e in examples[:12]:
    print('   ✗ %-28s N=%-3d life=%-6s rate=%-7s 隐含fps=%.1f  (%s row %d %s)' % (
        e[0], e[1], e[2], e[3], e[4], e[5], e[6], e[7]))

json.dump({'rate_all': dict(rate_all), 'rate_spr_tex': dict(rate_spr_tex), 'sheet_nodes': sheet_nodes,
           'spr_forms': {str(k): v for k, v in spr_multi.most_common()}, 'n_forms': len(spr_multi),
           'n_dist': dict(Counter(h['n_frames'] for h in spr_headers)),
           'param_dist': dict(Counter(h['param'] for h in spr_headers)),
           'h2_verdict': {'match': ok, 'mismatch': bad, 'undecidable': unknown},
           'h2_mismatch_examples': examples[:40]},
          io.open(os.path.join(OUT, 'Q3_analyze.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n-> Q3_analyze.json')
