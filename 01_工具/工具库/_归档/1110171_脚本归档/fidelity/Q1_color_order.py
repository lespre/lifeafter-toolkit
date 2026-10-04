# -*- coding: utf-8 -*-
"""Q1_color_order.py — Q1：颜色通道序 rgba vs argb 的**定量判定**（两皮肤全部 color_track + color_track_par）。

判据（每条轨道独立打分，两序各算一次）：
  C1 alpha 包络单调性：候选 alpha 列的"同向步占比"（越小=越跳跃）。
  C2 alpha 端点闭合：候选 alpha 列首/尾至少一端 ≈0（不可见收尾），另一端达 20–255 量级。
  C3 alpha 与 SmoothStop 一致性：候选 alpha 列 vs smooth_stop[0] 的 21 点采样 Pearson 相关
     （适配器里 alpha 会被 smooth_stop 相乘 ⇒ 若列序正确，两者应正相关）。
  C4 RGB 色相稳定性：候选 RGB 三列相邻键帧的色相跳变总量（越小=越像一条颜色渐变）。
每条轨道按 C1..C4 多数投票得 rgba/argb/tie；最后汇总比例。
"""
import io, json, math, os, sys
from collections import Counter, defaultdict
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
W = r'E:\la拆包项目\08Lifeafter wiki\assets\3d\weapon_skin'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171\fidelity'


def sample(track, t):
    """与适配器 sample() 同口径的线性插值（track = [{time, value:[...]}]）。"""
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


def monotone_fraction(vals):
    """同向步占比：在 |diff|>1e-9 的相邻步中，方向与主导方向一致的占比（1.0=完全单调）。"""
    diffs = [vals[i + 1] - vals[i] for i in range(len(vals) - 1)]
    nz = [d for d in diffs if abs(d) > 1e-9]
    if len(nz) < 2:
        return 1.0 if len(nz) <= 1 else 1.0
    pos = sum(1 for d in nz if d > 0)
    neg = len(nz) - pos
    return max(pos, neg) / len(nz)


def pearson(a, b):
    n = len(a)
    if n < 3:
        return None
    ma, mb = sum(a) / n, sum(b) / n
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((y - mb) ** 2 for y in b)
    if va <= 1e-12 or vb <= 1e-12:
        return None
    cov = sum((a[i] - ma) * (b[i] - mb) for i in range(n))
    return cov / math.sqrt(va * vb)


def hue_jump(rgb_seq):
    """相邻键帧色相跳变总和（度，取最短弧）。"""
    tot = 0.0
    for i in range(len(rgb_seq) - 1):
        h1 = rgb_to_hue(rgb_seq[i]); h2 = rgb_to_hue(rgb_seq[i + 1])
        if h1 is None or h2 is None:
            continue
        d = abs(h1 - h2)
        tot += min(d, 360 - d)
    return tot


def rgb_to_hue(c):
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


def analyze(skin, nodes):
    rows = []
    for idx, n in enumerate(nodes):
        ct = n.get('color_track') or []
        if len(ct) < 2:
            continue
        cols = []
        for c in range(4):
            cols.append([kf['value'][c] for kf in ct if len(kf['value']) > c])
        if any(len(c) < 2 for c in cols):
            continue
        times = [kf['time'] for kf in ct]
        ss = n.get('smooth_stop') or []
        s0 = [sample(ss, t / 20.0)[0] for t in range(21)] if ss else None
        col_s = [[sample(ct, t / 20.0)[c] for t in range(21)] for c in range(4)]
        seq = [[kf['value'][c] for kf in ct] for c in range(4)]
        rec = {'skin': skin, 'idx': idx, 'name': n.get('name'), 'tag': n.get('tag'), 'n_keys': len(ct),
               'times': times, 'cols': seq, 'interp': col_s}

        def score(alpha_i, rgb_idx):
            a = seq[alpha_i]
            mf = monotone_fraction(a)
            v0, v1 = a[0], a[-1]
            mx = max(a)
            closed = 1 if (min(v0, v1) <= max(2.0, 0.06 * mx) and mx >= 20) else 0
            corr = pearson(col_s[alpha_i], s0) if s0 else None
            hj = hue_jump([[seq[c][i] for c in rgb_idx] for i in range(len(ct))])
            return {'monotone': round(mf, 4), 'endpoint_closed': closed, 'end0': v0, 'end1': v1,
                    'smooth_corr': (None if corr is None else round(corr, 4)), 'hue_jump': round(hj, 2)}

        r_rgba = score(3, [0, 1, 2])
        r_argb = score(0, [1, 2, 3])
        # 四条判据各自的投票
        votes = []
        votes.append('rgba' if r_rgba['monotone'] > r_argb['monotone'] else
                     ('argb' if r_argb['monotone'] > r_rgba['monotone'] else 'tie'))
        votes.append('rgba' if r_rgba['endpoint_closed'] > r_argb['endpoint_closed'] else
                     ('argb' if r_argb['endpoint_closed'] > r_rgba['endpoint_closed'] else 'tie'))
        if r_rgba['smooth_corr'] is not None and r_argb['smooth_corr'] is not None:
            votes.append('rgba' if r_rgba['smooth_corr'] > r_argb['smooth_corr'] else
                         ('argb' if r_argb['smooth_corr'] > r_rgba['smooth_corr'] else 'tie'))
        votes.append('rgba' if r_rgba['hue_jump'] < r_argb['hue_jump'] else
                     ('argb' if r_argb['hue_jump'] < r_rgba['hue_jump'] else 'tie'))
        cnt = Counter(votes)
        verdict = 'rgba' if cnt['rgba'] > cnt['argb'] else ('argb' if cnt['argb'] > cnt['rgba'] else 'tie')
        rec.update({'rgba': r_rgba, 'argb': r_argb, 'votes': votes, 'vote_count': dict(cnt), 'verdict': verdict})
        rows.append(rec)
    return rows


allrows = {}
summary = {}
for sid in ('1110177', '1110171'):
    d = json.load(io.open(os.path.join(W, sid, 'effects.json'), encoding='utf-8'))
    rows = analyze(sid, d['nodes'])
    allrows[sid] = rows
    v = Counter(r['verdict'] for r in rows)
    vc = Counter(x for r in rows for x in r['votes'])
    # 每条判据的胜出比例（更细）
    per_crit = {'monotone': Counter(), 'endpoint_closed': Counter(), 'smooth_corr': Counter(), 'hue_jump': Counter()}
    for r in rows:
        per_crit['monotone'][r['votes'][0]] += 1
        per_crit['endpoint_closed'][r['votes'][1]] += 1
        per_crit['smooth_corr'][r['votes'][2 if len(r['votes']) > 2 else 2]] += 1
        per_crit['hue_jump'][r['votes'][-1]] += 1
    summary[sid] = {'tracks': len(rows), 'verdict': dict(v), 'criteria_votes': dict(vc),
                    'per_criterion': {k: dict(c) for k, c in per_crit.items()},
                    'monotone_alpha_mean_rgba': round(sum(r['rgba']['monotone'] for r in rows) / max(1, len(rows)), 4),
                    'monotone_alpha_mean_argb': round(sum(r['argb']['monotone'] for r in rows) / max(1, len(rows)), 4),
                    'hue_jump_mean_rgba': round(sum(r['rgba']['hue_jump'] for r in rows) / max(1, len(rows)), 2),
                    'hue_jump_mean_argb': round(sum(r['argb']['hue_jump'] for r in rows) / max(1, len(rows)), 2),
                    'smooth_corr_mean_rgba': round(sum((r['rgba']['smooth_corr'] or 0) for r in rows) / max(1, len(rows)), 4),
                    'smooth_corr_mean_argb': round(sum((r['argb']['smooth_corr'] or 0) for r in rows) / max(1, len(rows)), 4)}
    print('== %s ==  轨道 %d' % (sid, len(rows)))
    print('   逐条判定:', json.dumps(dict(v), ensure_ascii=False))
    print('   四判据投票:', json.dumps(dict(vc), ensure_ascii=False))
    print('   分判据:', json.dumps(summary[sid]['per_criterion'], ensure_ascii=False))
    print('   alpha 单调性均值 rgba=%.4f argb=%.4f' % (summary[sid]['monotone_alpha_mean_rgba'],
                                                       summary[sid]['monotone_alpha_mean_argb']))
    print('   RGB 色相跳变均值(度) rgba=%.2f argb=%.2f' % (summary[sid]['hue_jump_mean_rgba'],
                                                            summary[sid]['hue_jump_mean_argb']))
    print('   alpha↔smoothStop 相关均值 rgba=%.4f argb=%.4f' % (summary[sid]['smooth_corr_mean_rgba'],
                                                                 summary[sid]['smooth_corr_mean_argb']))

json.dump({'summary': summary, 'tracks': allrows}, io.open(os.path.join(OUT, 'Q1_color_order.json'), 'w',
          encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n-> Q1_color_order.json')
# 样例对照（供人眼看）
for sid in ('1110177', '1110171'):
    r = allrows[sid][0]
    print('\n样例 %s %s: rgba→alpha=%s rgb=%s ; argb→alpha=%s rgb=%s' % (
        sid, r['name'], [c[-1] for c in [r['cols'][3]]], [[r['cols'][c][i] for c in (0, 1, 2)] for i in range(len(r['times']))],
        [r['cols'][0][0], r['cols'][0][-1]], [[r['cols'][c][i] for c in (1, 2, 3)] for i in range(len(r['times']))]))
