# -*- coding: utf-8 -*-
"""Q1_color_order_v2.py — Q1 定量判定 v2（在 v1 基础上加三条皮肤级判据）。

判据（逐轨）：
  C1 alpha 列单调性（同向步占比）
  C2 alpha 列端点闭合（首/尾至少一端 ≈0）
  C3 alpha 列 vs smooth_stop 的 21 点相关
  C4 候选 RGB 的色相跳变总量（越小越像一条颜色渐变）
皮肤级判据：
  C5 色相聚类紧度：把每条轨道的候选 RGB 均值取色相，算环形均值与环形标准差（越小=同一把武器同一色系）
  C6 端点精确性：候选 alpha 列首/尾"恰好 0 或 255"的比例
  C7 编辑器默认值一致性：两皮肤 ParticleSystem 常值 (255,92,243,107) 在两种列序下的语义
"""
import io, json, math, os, sys
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
W = r'E:\la拆包项目\08Lifeafter wiki\assets\3d\weapon_skin'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171\fidelity'


def interp(track, t):
    if not track:
        return None
    k = max(0.0, min(1.0, t))
    if k <= track[0]['time']:
        return list(track[0]['value'])
    for i in range(1, len(track)):
        if k <= track[i]['time']:
            t0, t1 = track[i - 1]['time'], track[i]['time']
            u = (k - t0) / (t1 - t0) if (t1 - t0) > 1e-6 else 0.0
            a, b = track[i - 1]['value'], track[i]['value']
            return [a[j] + (b[j] - a[j]) * u for j in range(len(a))]
    return list(track[-1]['value'])


def mono(v):
    d = [v[i + 1] - v[i] for i in range(len(v) - 1)]
    nz = [x for x in d if abs(x) > 1e-9]
    if len(nz) < 2:
        return 1.0
    p = sum(1 for x in nz if x > 0)
    return max(p, len(nz) - p) / len(nz)


def pearson(a, b):
    n = len(a)
    if n < 3:
        return None
    ma, mb = sum(a) / n, sum(b) / n
    va = sum((x - ma) ** 2 for x in a); vb = sum((y - mb) ** 2 for y in b)
    if va <= 1e-12 or vb <= 1e-12:
        return None
    return sum((a[i] - ma) * (b[i] - mb) for i in range(n)) / math.sqrt(va * vb)


def hue(c):
    r, g, b = [x / 255.0 for x in c]
    mx, mn = max(r, g, b), min(r, g, b)
    if mx - mn < 1e-6:
        return None
    if mx == r:
        h = ((g - b) / (mx - mn)) % 6
    elif mx == g:
        h = (b - r) / (mx - mn) + 2
    else:
        h = (r - g) / (mx - mn) + 4
    return h * 60


def circ_stats(hs):
    hs = [h for h in hs if h is not None]
    if not hs:
        return None, None, 0
    ang = [math.radians(h) for h in hs]
    C = sum(math.cos(a) for a in ang) / len(ang)
    S = sum(math.sin(a) for a in ang) / len(ang)
    R = math.hypot(C, S)
    mean = math.degrees(math.atan2(S, C)) % 360
    std = math.degrees(math.sqrt(max(0.0, -2 * math.log(max(R, 1e-9)))))
    return round(mean, 1), round(std, 1), len(hs)


report = {'tracks_multi': {}, 'tracks_const': {}, 'skin_level': {}, 'shared_constant': {}}
for sid in ('1110177', '1110171'):
    d = json.load(io.open(os.path.join(W, sid, 'effects.json'), encoding='utf-8'))
    multi, const = [], []
    for i, n in enumerate(d['nodes']):
        ct = n.get('color_track') or []
        cps = n.get('color_track_par') or []
        for label, tr in (('color_track', ct), ('color_track_par', cps)):
            if len(tr) < 2:
                if len(tr) == 1:
                    const.append({'idx': i, 'name': n.get('name'), 'tag': n.get('tag'), 'track': label,
                                  'time': tr[0]['time'], 'value': tr[0]['value'],
                                  'blend_mode': n.get('blend_mode')})
                continue
            seq = [[kf['value'][c] for kf in tr] for c in range(4)]
            ss = n.get('smooth_stop') or []
            s0 = [interp(ss, t / 20.0)[0] for t in range(21)] if ss else None
            col_s = [[interp(tr, t / 20.0)[c] for t in range(21)] for c in range(4)]

            def sc(ai, ri):
                a = seq[ai]
                mx = max(a)
                return {'mono': round(mono(a), 4), 'end_closed': 1 if (min(a[0], a[-1]) <= max(2.0, 0.06 * mx) and mx >= 20) else 0,
                        'end0': a[0], 'end1': a[-1],
                        'corr': (None if not s0 else (lambda c: None if c is None else round(c, 4))(pearson(col_s[ai], s0))),
                        'hue_jump': round(sum(min(abs((hue([seq[c][k] for c in ri]) or 0) - (hue([seq[c][k + 1] for c in ri]) or 0)),
                                              360 - abs((hue([seq[c][k] for c in ri]) or 0) - (hue([seq[c][k + 1] for c in ri]) or 0)))
                                          for k in range(len(tr) - 1)), 2),
                        'hue_seq': [hue([seq[c][k] for c in ri]) for k in range(len(tr))]}
            R, A = sc(3, [0, 1, 2]), sc(0, [1, 2, 3])
            votes = []
            votes.append('rgba' if R['mono'] > A['mono'] else ('argb' if A['mono'] > R['mono'] else 'tie'))
            votes.append('rgba' if R['end_closed'] > A['end_closed'] else ('argb' if A['end_closed'] > R['end_closed'] else 'tie'))
            if R['corr'] is not None and A['corr'] is not None:
                votes.append('rgba' if R['corr'] > A['corr'] else ('argb' if A['corr'] > R['corr'] else 'tie'))
            votes.append('rgba' if R['hue_jump'] < A['hue_jump'] else ('argb' if A['hue_jump'] < R['hue_jump'] else 'tie'))
            c = Counter(votes)
            multi.append({'skin': sid, 'idx': i, 'name': n.get('name'), 'tag': n.get('tag'), 'track': label,
                          'n_keys': len(tr), 'rgba': R, 'argb': A, 'votes': votes, 'vote_count': dict(c),
                          'verdict': 'rgba' if c['rgba'] > c['argb'] else ('argb' if c['argb'] > c['rgba'] else 'tie')})
    # 皮肤级：色相聚类（用每条轨道候选 RGB 的时间均值）
    def hue_cluster(key_alpha_idx, rgb_idx):
        hs, rows = [], []
        for r in multi:
            seqs = r['rgba'] if key_alpha_idx == 3 else r['argb']
            hh = [x for x in seqs['hue_seq'] if x is not None]
            if hh:
                hs.append(sum(hh) / len(hh)); rows.append(r['name'])
        m, s, n = circ_stats(hs)
        return {'mean_hue_deg': m, 'circ_std_deg': s, 'n_tracks': n}
    hl_rgba = hue_cluster(3, [0, 1, 2])
    hl_argb = hue_cluster(0, [1, 2, 3])
    # 端点精确性
    ex = {'rgba_col3': {'first': 0, 'last': 0}, 'argb_col0': {'first': 0, 'last': 0}, 'n': len(multi)}
    for r in multi:
        # 重新取原始列
        rr = r
    # 直接统计（用 multi 里存的端点）
    for r in multi:
        if r['rgba']['end0'] in (0, 255):
            ex['rgba_col3']['first'] += 1
        if r['rgba']['end1'] in (0, 255):
            ex['rgba_col3']['last'] += 1
        if r['argb']['end0'] in (0, 255):
            ex['argb_col0']['first'] += 1
        if r['argb']['end1'] in (0, 255):
            ex['argb_col0']['last'] += 1
    v = Counter(r['verdict'] for r in multi)
    report['tracks_multi'][sid] = multi
    report['tracks_const'][sid] = const
    report['skin_level'][sid] = {
        'multi_tracks': len(multi), 'const_tracks': len(const), 'verdict': dict(v),
        'hue_cluster_rgba': hl_rgba, 'hue_cluster_argb': hl_argb, 'endpoint_exact': ex,
        'mean_hue_jump_rgba': round(sum(r['rgba']['hue_jump'] for r in multi) / max(1, len(multi)), 2),
        'mean_hue_jump_argb': round(sum(r['argb']['hue_jump'] for r in multi) / max(1, len(multi)), 2),
        'mean_mono_rgba': round(sum(r['rgba']['mono'] for r in multi) / max(1, len(multi)), 4),
        'mean_mono_argb': round(sum(r['argb']['mono'] for r in multi) / max(1, len(multi)), 4),
    }
    print('===== %s =====' % sid)
    print('  多键轨道 %d；单键常数轨道 %d' % (len(multi), len(const)))
    print('  逐条判定:', json.dumps(dict(v), ensure_ascii=False))
    print('  色相聚类 rgba: %s' % json.dumps(hl_rgba, ensure_ascii=False))
    print('  色相聚类 argb: %s' % json.dumps(hl_argb, ensure_ascii=False))
    print('  色相跳变均值 rgba=%.1f argb=%.1f' % (report['skin_level'][sid]['mean_hue_jump_rgba'],
                                                 report['skin_level'][sid]['mean_hue_jump_argb']))
    print('  端点精确(0/255) col3-first=%d col3-last=%d | col0-first=%d col0-last=%d (n=%d)' % (
        ex['rgba_col3']['first'], ex['rgba_col3']['last'], ex['argb_col0']['first'], ex['argb_col0']['last'], ex['n']))
    print('  常数轨道样本:', json.dumps(const[:6], ensure_ascii=False))

# 共享常数：两皮肤 ParticleSystem 的 (255,92,243,107)
print('\n=== 共享常数 (255,92,243,107) 的两序语义 ===')
c = [255, 92, 243, 107]
print('  rgba → RGB=%s (hue %.1f) alpha=%d' % (c[:3], hue(c[:3]) or -1, c[3]))
print('  argb → RGB=%s (hue %.1f) alpha=%d' % (c[1:], hue(c[1:]) or -1, c[0]))
report['shared_constant'] = {'value': c, 'rgba': {'rgb': c[:3], 'hue': hue(c[:3]), 'alpha': c[3]},
                             'argb': {'rgb': c[1:], 'hue': hue(c[1:]), 'alpha': c[0]}}
json.dump(report, io.open(os.path.join(OUT, 'Q1_color_order.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n-> Q1_color_order.json (v2)')
