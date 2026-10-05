# -*- coding: utf-8 -*-
"""Q4_clamp_audit.py — Q4：尺寸钳制是否削掉了源尺寸？逐节点（1110177 5 个 / 1110171 8 个可渲染节点）。

两条独立证据：
  A) **运行时实测**：从既有产物 JSON 抽 adapter 的 `quad_raw / quad / quad_clamped / clamp_cap / weapon_diag`
     （结构化对象 + 被转义的嵌入 diag 字符串都解析）。
  B) **按源码口径重算**：adapter L402 `U(v) = v × SFX_UNIT_TO_MODEL(0.1)`（**全局**，不是逐皮肤 model_unit_scale）；
     Sprite: raw = U(Radius) × 源 TrackScale XScale；PS: raw = U(minRadius + r1×(maxRadius−minRadius)) × XScale；
     cap = weapon_diag × SPRITE_CLAMP_K(0.6)。
结论只看："raw > cap 是否发生"、触发倍数、以及"最坏源值离 cap 有多近"。
"""
import io, json, os, re, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
W = r'E:\la拆包项目\08Lifeafter wiki\assets\3d\weapon_skin'
P = r'E:\la拆包项目\03拆包产物'
OUT = os.path.join(P, '_target_1110171', 'fidelity')
U_GLOBAL = 0.1          # adapter L83 SFX_UNIT_TO_MODEL
K_CLAMP = 0.60          # adapter L108 SPRITE_CLAMP_K
DIAG = {'1110177': 15.4551, '1110171': 6.882}   # 运行时实测（见跑分表）

# ---------- A) 从产物里抽运行时读数 ----------
rx_obj = re.compile(r'\{[^{}]*"quad_raw"[^{}]*\}')
runtime = defaultdict(list)
seen_src = defaultdict(set)
for root, dirs, files in os.walk(P):
    if os.path.normpath(root).startswith(os.path.normpath(os.path.join(P, '_target_1110171', 'fidelity'))):
        continue                      # 不把自己的产物当"运行时读数来源"（自我污染防护）
    for fn in files:
        if not fn.lower().endswith('.json'):
            continue
        fp = os.path.join(root, fn)
        try:
            if os.path.getsize(fp) > 400_000_000:
                continue
            raw = io.open(fp, encoding='utf-8', errors='ignore').read()
        except Exception:
            continue
        if 'quad_raw' not in raw:
            continue
        blob = raw.replace('\\"', '"').replace('\\n', '\n')
        for m in rx_obj.finditer(blob):
            s = m.group(0)

            def g(k, cast=str):
                mm = re.search(r'"%s"\s*:\s*(null|"[^"]*"|[-\d.eE]+|true|false)' % k, s)
                if not mm:
                    return None
                v = mm.group(1)
                if v == 'null':
                    return None
                if cast is float:
                    try:
                        return float(v)
                    except Exception:
                        return None
                return v.strip('"')
            rec = {'file': os.path.relpath(fp, P), 'name': g('name'), 'kind': g('kind'), 'texture': g('texture'),
                   'quad_size_world': g('quad_size_world', float), 'quad_raw': g('quad_raw', float),
                   'quad': g('quad', float), 'quad_clamped': g('quad_clamped'), 'clamp_cap': g('clamp_cap', float),
                   'weapon_diag': g('weapon_diag', float), 'bbox_vs_weapon_ratio': g('bbox_vs_weapon_ratio', float),
                   'start': g('start', float), 'life': g('life', float), 'visible': g('visible')}
            sid = None
            if rec['weapon_diag']:
                sid = '1110177' if abs(rec['weapon_diag'] - 15.4551) < 0.01 else (
                    '1110171' if abs(rec['weapon_diag'] - 6.882) < 0.01 else None)
            if sid:
                runtime[sid].append(rec)
                seen_src[sid].add(rec['file'])

print('=== A) 运行时实测读数（按 weapon_diag 归皮肤）===')
for sid in ('1110177', '1110171'):
    lst = [r for r in runtime[sid] if r['quad_raw'] is not None]
    print('  %s: %d 条 quad 读数，来自 %d 个产物文件' % (sid, len(lst), len(seen_src[sid])))
    for f in sorted(seen_src[sid]):
        print('      - %s' % f)

# ---------- B) 按源码口径重算 ----------
report = {'unit_global': U_GLOBAL, 'clamp_k': K_CLAMP, 'weapon_diag': DIAG,
          'runtime': {k: v for k, v in runtime.items()}, 'runtime_sources': {k: sorted(v) for k, v in seen_src.items()},
          'analytic': {}, 'all_nodes_worst': {}}


def scale_vals(n):
    out = []
    for kf in (n.get('scale_track') or []):
        v = kf.get('value')
        if v is None:
            continue
        if isinstance(v, (int, float)):
            out.append(float(v))
        elif isinstance(v, (list, tuple)) and v:
            try:
                out.append(float(v[0]))
            except Exception:
                pass
    return out


for sid in ('1110177', '1110171'):
    d = json.load(io.open(os.path.join(W, sid, 'effects.json'), encoding='utf-8'))
    diag = DIAG[sid]
    cap = diag * K_CLAMP
    rows = []
    # 全部节点的最坏值（回答"钳制到底会不会咬到"）
    worst = []
    for i, n in enumerate(d['nodes']):
        sv = scale_vals(n)
        smax = max(sv) if sv else 1.0
        r = n.get('radius')
        mn, mx = n.get('minRadius'), n.get('maxRadius')
        rmax = None
        if r is not None:
            rmax = float(r)
        elif mn is not None or mx is not None:
            rmax = float(mx if mx is not None else mn)
        if rmax is None:
            continue
        raw = max(U_GLOBAL * rmax * smax, 0.02)
        worst.append({'idx': i, 'name': n.get('name'), 'tag': n.get('tag'), 'source_radius': rmax,
                      'scale_key_max': smax, 'raw_max': round(raw, 4), 'ratio_raw_over_cap': round(raw / cap, 4),
                      'renderable': n.get('renderable_by_adapter') is True, 'clamped': raw > cap})
    worst.sort(key=lambda x: -x['ratio_raw_over_cap'])
    report['all_nodes_worst'][sid] = {'cap': round(cap, 4), 'top10': worst[:10],
                                      'max_ratio': worst[0]['ratio_raw_over_cap'] if worst else None,
                                      'n_clamped_anywhere': sum(1 for w in worst if w['clamped'])}
    print('\n=== B) %s：全 %d 个有尺寸节点里 raw/cap 最大 10 个（cap=%.4f = %.4f×%.2f）===' % (
        sid, len(worst), cap, diag, K_CLAMP))
    for w in worst[:10]:
        print('   #%-3d %-22s %-16s radius=%-6s scale=%-5s raw=%-8s raw/cap=%-7.3f renderable=%-5s clamped=%s' % (
            w['idx'], w['name'], w['tag'], w['source_radius'], w['scale_key_max'], w['raw_max'],
            w['ratio_raw_over_cap'], w['renderable'], w['clamped']))

    for i, n in enumerate(d['nodes']):
        if n.get('renderable_by_adapter') is not True:
            continue
        tag = n.get('tag')
        sv = scale_vals(n)
        smax = max(sv) if sv else 1.0
        base = {'idx': i, 'name': n.get('name'), 'tag': tag, 'cap': round(cap, 4),
                'unit_used': U_GLOBAL, 'scale_key_max': smax, 'blend_mode': n.get('blend_mode'), 'life': n.get('life')}
        if tag == 'Sprite':
            r = n.get('radius')
            raw = None if r is None else max(U_GLOBAL * float(r) * smax, 0.02)
            base.update({'kind': 'sprite', 'source_radius': r, 'quad_raw_analytic': None if raw is None else round(raw, 4),
                         'clamped': None if raw is None else raw > cap,
                         'ratio_raw_over_cap': None if raw is None else round(raw / cap, 4),
                         'quad_analytic': None if raw is None else round(min(raw, cap), 4)})
            rows.append(base)
        elif tag in ('ParticleSystem', 'ParticleRes'):
            mn, mx = n.get('minRadius'), n.get('maxRadius')
            note = None
            if mn is None and mx is None:
                mn = mx = 1.2
                note = 'adapter L732 兜底 1.2（源无 minRadius/maxRadius）'
            else:
                mn = float(mn if mn is not None else mx)
                mx = float(mx if mx is not None else mn)
            for lbl, rv in (('min', mn), ('mid', (mn + mx) / 2), ('max', mx)):
                raw = max(U_GLOBAL * rv * smax, 0.02)
                rows.append({**base, 'kind': 'particle', 'radius_case': lbl, 'source_radius': rv,
                             'quad_raw_analytic': round(raw, 4), 'clamped': raw > cap,
                             'ratio_raw_over_cap': round(raw / cap, 4), 'quad_analytic': round(min(raw, cap), 4),
                             'note': note})
        else:
            rows.append({**base, 'kind': 'model/other', 'source_radius': None, 'quad_raw_analytic': None,
                         'clamped': None, 'ratio_raw_over_cap': None, 'quad_analytic': None,
                         'note': 'Model/其它：adapter 的 clampQuad 只作用于 Sprite/粒子 quad ⇒ 不受钳制'})
    report['analytic'][sid] = {'weapon_diag': diag, 'cap': round(cap, 4), 'rows': rows}
    print('\n--- %s 可渲染节点逐节点（U=%.2f 全局）---' % (sid, U_GLOBAL))
    for r in rows:
        print('  #%-3d %-22s %-14s %-4s radius=%-6s raw=%-8s cap=%-7s clamped=%-5s raw/cap=%s' % (
            r['idx'], r['name'], r['tag'], r.get('radius_case', '-'), r['source_radius'],
            r['quad_raw_analytic'], r['cap'], r['clamped'], r['ratio_raw_over_cap']))
    # 与运行时读数对拍（同名节点）
    rt = {}
    for x in runtime[sid]:
        if x['quad_raw'] is None:
            continue
        nm = x['name']
        if nm and (nm not in rt or (x['quad_raw'] or 0) > (rt[nm]['quad_raw'] or 0)):
            rt[nm] = x
    print('  运行时对拍（同名节点，取实测最大值）：')
    for r in rows:
        if r['name'] in rt:
            x = rt[r['name']]
            print('     %-22s 实测 raw=%-8s quad=%-8s clamped=%-5s cap=%-8s | 解析 raw=%s clamped=%s' % (
                r['name'], x['quad_raw'], x['quad'], x['quad_clamped'], x['clamp_cap'],
                r['quad_raw_analytic'], r['clamped']))
    report['analytic'][sid]['runtime_match'] = {r['name']: rt[r['name']] for r in rows if r['name'] in rt}
    trig = [r for r in rows if r['clamped'] is True]
    print('  >> 触发钳制 %d / %d' % (len(trig), len(rows)))

json.dump(report, io.open(os.path.join(OUT, 'Q4_clamp_audit.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n-> Q4_clamp_audit.json')
