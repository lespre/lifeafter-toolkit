# -*- coding: utf-8 -*-
'''task-79 GO：1110171 的 28 个 Model 从源 bin 按名补齐 + 顶层 model_unit_scale（只新增，canonical 子集自证）。'''
import io, os, re, sys, json, hashlib, shutil, time
sys.stdout.reconfigure(encoding='utf-8')
W = r'E:\la拆包项目\08Lifeafter wiki\assets\3d\weapon_skin'
BIN = r'E:\la拆包项目\03拆包产物\render_1003_010\_sfx_010\gpk_effect_01_f74635_59115620b779a5e8.bin'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
TAGS = ('Dummy', 'Model', 'ParticleSystem', 'ParticleRes', 'Sprite', 'Trail')
REP = os.path.join(OUT, 'MODEL171_probe_report.md')
SRCID = 'effect_01.gpk#f74635_59115620b779a5e8(bin)'

def frames_of(body):
    out = []
    for fm in re.finditer(r'<Frame\s+([^>/]*)/?>', body):
        a = dict(re.findall(r'(\w+)\s*=\s*"([^"]*)"', fm.group(1)))
        if 'Time' in a and 'Value' in a:
            v = a['Value']
            val = [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', v)] if ',' in v else (
                float(v) if re.match(r'^-?\d+(\.\d+)?$', v.strip()) else v)
            out.append({'time': float(a['Time']), 'value': val})
    return out

txt = io.open(BIN, 'rb').read().decode('gbk', 'replace')
SRC = {}
for m in re.finditer(r'<(%s)\b([^>]*)>' % '|'.join(TAGS), txt):
    at = m.group(2)
    nxt = re.search(r'<(?:%s)\b' % '|'.join(TAGS), txt[m.end():])
    blk = txt[m.end():(m.end() + nxt.start()) if nxt else (m.end() + 60000)]
    a = dict(re.findall(r'(\w+)\s*=\s*"([^"]*)"', at))
    if not a.get('Name'):
        continue
    tr = {}
    for um in re.finditer(r'<(u_[A-Za-z0-9_]+)\b([^>]*?)(?:/>|>(.*?)</\1>)', blk, re.S):
        fr = frames_of(um.group(3) or '')
        if fr:
            tr[um.group(1)] = fr
    SRC[a['Name']] = {'tag': m.group(1), 'attrs': a, 'tracks': tr}
print('源 bin 节点 %d（Model %d）' % (len(SRC), sum(1 for v in SRC.values() if v['tag'] == 'Model')))

MAP = (('FxStartTime', 'fx_start_time', 'FxStartTime'), ('FxLifeSpan', 'fx_life_span', 'FxLifeSpan'),
       ('TransparentMode', 'transparent_mode', 'TransparentMode'), ('RenderBias', 'render_bias', 'RenderBias'),
       ('TrackType', 'track_type', 'TrackType'), ('DirType', 'dir_type', 'DirType'),
       ('RenderOrder', 'render_order', 'RenderOrder'), ('RenderLevel', 'render_level', 'RenderLevel'),
       ('PosOffset', 'pos_offset_csl', 'PosOffset'))
results = {}
for skin, val, basis in (('1110171', 1, 'source-space m'), ('1110177', 0.1, 'source-space cm')):
    E = os.path.join(W, skin, 'effects.json')
    old = open(E, 'rb').read()
    eff = json.loads(old.decode('utf-8'))
    old_nodes = [json.dumps(n, ensure_ascii=False, sort_keys=True) for n in eff['nodes']]
    old_top = {k: json.dumps(v, ensure_ascii=False, sort_keys=True) for k, v in eff.items() if k != 'nodes'}
    MD = [n for n in eff['nodes'] if n.get('tag') == 'Model']
    rows = []
    for n in MD:
        s = SRC.get(n.get('name'))
        if not s:
            rows.append({'node': n.get('name'), 'status': 'no_source_node'}); continue
        mf = n.setdefault('model_fields', {})
        added = {}
        for src, low, cap in MAP:
            if src in s['attrs']:
                v = s['attrs'][src]
                mf[cap] = v                                   # 适配器读的就是 mf.FxStartTime / mf.FxLifeSpan
                mf[low] = v
                added[cap] = v
        if 'PosOffset' in s['attrs']:
            pv = [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', s['attrs']['PosOffset'])]
            if len(pv) == 3:
                mf['pos_offset'] = pv
                added['pos_offset'] = pv
        ut = mf.get('uniform_tracks')
        had = bool(ut)
        if not had:
            ut = mf['uniform_tracks'] = {}
        newtracks = [k for k in sorted(s['tracks']) if k not in ut]
        for k in newtracks:
            ut[k] = s['tracks'][k]
        mf['model_param_source'] = {k: 'dg_bin:%s:%s:%s' % (SRCID, n.get('name'), k) for k in list(added) + newtracks}
        n['model_param_status'] = 'backfilled_from_bin'
        rows.append({'node': n.get('name'), 'status': 'ok', 'had_uniform_tracks': had,
                     'added_caps': sorted(added.keys()), 'tracks_added': newtracks,
                     'tracks_total': sorted(ut.keys()), 'src_tag': s['tag']})
    # 顶层：只新增 model_unit_scale / _basis
    if 'model_unit_scale' not in eff:
        eff['model_unit_scale'] = val
    eff['model_unit_scale_basis'] = {
        'value': eff['model_unit_scale'], 'skin': skin, 'source_space': basis,
        'evidence': ('1110171 导出 GLB 源空间 bbox 量级 = 0.46–3.43（m 量级，例 顶渐变 size [0.464,0.953,3.434]）；'
                     '1110177 = 13–163（cm 量级）⇒ 两皮肤源空间差 10×，故 unit 定标不可一刀切')
                    if skin == '1110171' else
                    ('1110177 导出 GLB 源空间 bbox = 13.0–163.07（cm）；与武器对角线 15.4552 之比 '
                     '163.07/15.4552=10.55 ⇒ 需 ×0.1 才回到 1.055×'),
        'weapon_diagonal_ratio_pending': (skin == '1110171'),
        'set_by': 'lead 裁定 2026-09-19（逐皮肤数据定标）；chain-auditor 落数据 + 依据',
        'adapter': 'MODEL_UNIT_SCALE（adapter 读取 effects.model_unit_scale，缺省回落常量）'}
    # 自证：旧键/旧值必须全部保持（只允许新增）
    ok = True
    for i, n in enumerate(eff['nodes']):
        now = json.loads(json.dumps(n, ensure_ascii=False))
        try:
            bef = json.loads(old_nodes[i])
        except Exception:
            ok = False; break
        def sub(old_o, new_o):
            if isinstance(old_o, dict):
                if not isinstance(new_o, dict):
                    return False
                return all(k in new_o and sub(v, new_o[k]) for k, v in old_o.items())
            if isinstance(old_o, list):
                return old_o == new_o
            return old_o == new_o
        if not sub(bef, now):
            ok = False; break
    top_ok = all(k in eff and json.dumps(eff[k], ensure_ascii=False, sort_keys=True) == v for k, v in old_top.items())
    print('[%s] Model %d：补全 %d，no_source_node %d ｜ 自证(旧键值全保留)=%s ｜ 顶层只新增=%s' % (
        skin, len(MD), sum(1 for r in rows if r['status'] == 'ok'), sum(1 for r in rows if r['status'] != 'ok'), ok, top_ok))
    nt = {r['node']: r.get('tracks_added') for r in rows if r.get('tracks_added')}
    print('   新增 uniform_tracks 的节点: %s' % json.dumps({k: v for k, v in list(nt.items())[:8]}, ensure_ascii=False)[:400])
    if not (ok and top_ok):
        print('** 自证未过 ⇒ 拒绝写盘 **'); sys.exit(3)
    bs = E + '.bak_model171_' + time.strftime('%Y%m%d_%H%M%S')
    shutil.copy2(E, bs)
    pp = '\n' in old.decode('utf-8', 'replace')[:4000]
    open(E, 'w', encoding='utf-8', newline='\n').write(json.dumps(eff, ensure_ascii=False, indent=1 if pp else None, separators=None if pp else (',', ':')))
    nb = open(E, 'rb').read()
    results[skin] = {'before': hashlib.sha256(old).hexdigest()[:16].upper(), 'after': hashlib.sha256(nb).hexdigest()[:16].upper(),
                     'bytes_before': len(old), 'bytes_after': len(nb), 'backup': os.path.basename(bs), 'rows': rows,
                     'unit_scale': eff['model_unit_scale'], 'self_proof': bool(ok and top_ok)}
    print('   写盘 %s -> %s (%d -> %d B) 备份=%s' % (results[skin]['before'], results[skin]['after'], len(old), len(nb), os.path.basename(bs)))
json.dump(results, io.open(os.path.join(OUT, 'MODEL171_backfill_rows.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('逐条表 -> MODEL171_backfill_rows.json')
