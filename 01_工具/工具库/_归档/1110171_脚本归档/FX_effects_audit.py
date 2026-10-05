# -*- coding: utf-8 -*-
"""FX_effects_audit.py — 武器皮肤「动态光效(SFX 视觉特效)」链全面实测（只读）。

链：<skin>/effects.json ──(viewer.json.effects)──> weapon_skin_viewer.js:707-712 attachEffects()
    ──> weapon_skin_sfx_adapter.js:53-114（nodes[] → Sprite / ParticleSystem → 贴图）
覆盖：effects.json 数量/nodes 数、板上 115 卡可出光效数、nodes=0 逐个成因、
      .sfx XML 结构解析、adapter 字段契约对照、贴图存在性、缺资源清单。
输出：FX_effects_audit.json
"""
import json, os, re, sys, urllib.request, urllib.error, collections, time

WIKI = r'E:\la拆包项目\08Lifeafter wiki'
PACK = r'E:\la拆包项目\03拆包产物'
S3D = os.path.join(WIKI, 'assets', '3d', 'weapon_skin')
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
BASE = 'http://127.0.0.1:8765/'
BOARD = 'weapon_skin_sfx_text_sources'

# adapter 契约：node 级字段（weapon_skin_sfx_adapter.js 实际读取）
NODE_CONTRACT = [
    ('name', 'L205 ignoredParticleNodes'),
    ('tag', 'L82 isPS=n.tag===ParticleSystem'),
    ('texture_candidate', 'L57 filter 唯一门槛; L72 贴图 URL'),
    ('fxIgnore', 'L81 禁用标志'),
    ('blend_mode', 'L83 BLEND 映射'),
    ('pos_offset', 'L85 位置偏移'),
    ('start', 'L93/L126 起始时间'),
    ('life', 'L93/L126 寿命'),
    ('radius', 'L94/L189 sprite 缩放'),
    ('color_track', 'L94/L151 颜色曲线'),
    ('smooth_start', 'L94/L154 淡入'),
    ('smooth_stop', 'L94/L154 淡出'),
    ('scale_track', 'L95/L185 缩放曲线'),
    ('particlesPerSecond|ParticlesPerSecond', 'L102 发射率'),
    ('minSpriteLifespan|MinSpriteLifespan', 'L103 粒子寿命下限'),
    ('maxSpriteLifespan|MaxSpriteLifespan', 'L104 粒子寿命上限'),
    ('emit.EmissionRadiusFrame', 'L106 发射半径'),
    ('emit.MaxSpriteVelocityFrame', 'L107 速度'),
    ('emit.SpriteScaleFrame', 'L108 缩放'),
    ('emitAtBegin', 'L111 首帧发射'),
]
EFFECTS_CONTRACT = [
    ('status', 'viewer.js:709/724 非 none 才启用'),
    ('nodes', 'L57'),
    ('loop_seconds', 'L60'),
    ('assets_base', 'L61'),
    ('textures_dir', 'L61（默认 sfx/tex/）'),
    ('attach.anchor', 'L62'),
]


def http_status(url, timeout=15):
    for m in ('HEAD', 'GET'):
        try:
            req = urllib.request.Request(url, method=m)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status
        except urllib.error.HTTPError as e:
            return e.code
        except Exception as e:
            if m == 'GET':
                return 'ERR:' + type(e).__name__
    return 'ERR'


def get_path(d, *ks):
    cur = d
    for k in ks:
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        else:
            return None
    return cur


def main():
    rep = {'generated': time.strftime('%Y-%m-%d %H:%M:%S')}

    # ---------- A) 皮肤目录清点 ----------
    skins = sorted(d for d in os.listdir(S3D) if os.path.isdir(os.path.join(S3D, d)))
    inv = {}
    for sid in skins:
        d = os.path.join(S3D, sid)
        ep = os.path.join(d, 'effects.json')
        vp = os.path.join(d, 'viewer.json')
        e = json.load(open(ep, encoding='utf-8')) if os.path.isfile(ep) else None
        v = None
        if os.path.isfile(vp):
            try:
                v = json.load(open(vp, encoding='utf-8'))
            except Exception as ex:
                v = {'_error': str(ex)}
        ve = (v or {}).get('effects')
        rec = {
            'has_effects_json': bool(e), 'effects_bytes': os.path.getsize(ep) if e else None,
            'has_viewer_json': bool(v), 'viewer_bytes': os.path.getsize(vp) if os.path.isfile(vp) else None,
        }
        if e:
            nodes = e.get('nodes') or []
            rec.update({
                'schema': e.get('schema'), 'status': e.get('status'), 'status_reason': e.get('status_reason'),
                'note': e.get('note'), 'nodes': len(nodes),
                'node_tags': dict(collections.Counter(str(n.get('tag')) for n in nodes)),
                'node_names': [n.get('name') for n in nodes][:20],
                'sfx_source': e.get('sfx_source'), 'attach': e.get('attach'),
                'assets_base': e.get('assets_base'), 'textures_dir': e.get('textures_dir'),
                'loop_seconds': e.get('loop_seconds'), 'has_pending': e.get('pending'),
                'unsupported': e.get('unsupported'), 'top_keys': sorted(e.keys()),
                'node_field_union': sorted(set(k for n in nodes for k in n.keys())),
            })
        if ve is not None:
            vn = ve.get('nodes') or []
            rec['viewer_effects'] = {'status': ve.get('status'), 'nodes': len(vn),
                                     'keys': sorted(ve.keys()) if isinstance(ve, dict) else None}
            rec['viewer_effects_equals_file'] = (json.dumps(ve, sort_keys=True, ensure_ascii=False) ==
                                                 json.dumps(e, sort_keys=True, ensure_ascii=False)) if e else None
            rec['viewer_effects_node_keys'] = sorted(set(k for n in vn for k in n.keys())) if vn else []
        else:
            rec['viewer_effects'] = None
        inv[sid] = rec
    rep['skins_total'] = len(skins)
    rep['skins_with_effects_json'] = sorted(k for k, v in inv.items() if v['has_effects_json'])
    rep['skins_with_nodes_gt0'] = sorted(k for k, v in inv.items() if (v.get('nodes') or 0) > 0)
    rep['skins_with_effects_but_nodes0'] = sorted(k for k, v in inv.items() if v['has_effects_json'] and (v.get('nodes') or 0) == 0)
    rep['skins_with_viewer_effects_nonzero'] = sorted(k for k, v in inv.items() if ((v.get('viewer_effects') or {}).get('nodes') or 0) > 0)
    rep['skins_with_viewer_effects_status_not_none'] = sorted(
        k for k, v in inv.items() if (v.get('viewer_effects') or {}).get('status') not in (None, 'none'))
    rep['inventory'] = inv

    # ---------- B) 板上 115 卡覆盖 ----------
    bf = os.path.join(WIKI, 'data', 'boards', BOARD + '.js')
    txt = open(bf, encoding='utf-8').read()
    obj = json.loads(re.search(r'WIKI_BOARD_%s\s*=\s*(\{.*\})\s*;?\s*$' % BOARD, txt, re.S).group(1))
    items = obj['items']
    eff_skins = set(rep['skins_with_effects_json'])
    node_skins = set(rep['skins_with_nodes_gt0'])
    ids = []
    for it in items:
        ids.append(str(it.get('skin_id') or it.get('skin_item_id') or it.get('id') or ''))
    rep['board'] = {
        'file': bf, 'items': len(items),
        'ids_sample': ids[:8],
        'items_with_effects_json': sum(1 for i in ids if i in eff_skins),
        'items_with_nodes_gt0': sum(1 for i in ids if i in node_skins),
        'items_with_effects_json_ids': sorted(set(i for i in ids if i in eff_skins)),
        'items_with_nodes_gt0_ids': sorted(set(i for i in ids if i in node_skins)),
        'skins_with_effects_not_on_board': sorted(eff_skins - set(ids)),
    }

    # ---------- C) 字段契约对照（1110171 有 nodes 的那个）----------
    def contract_check(eff, label):
        out = {'label': label, 'effects_level': {}, 'node_level': {}}
        for k, src in EFFECTS_CONTRACT:
            v = get_path(eff, *k.split('.')) if '.' in k else eff.get(k)
            out['effects_level'][k] = {'present': v is not None, 'value': (v if not isinstance(v, (list, dict)) else ('<%s>' % type(v).__name__)), 'where': src}
        nodes = eff.get('nodes') or []
        for k, src in NODE_CONTRACT:
            if '|' in k:
                hit = [n for n in nodes if any(x in n for x in k.split('|'))]
            elif '.' in k:
                hit = [n for n in nodes if isinstance(n.get(k.split('.')[0]), dict) and k.split('.')[1] in n[k.split('.')[0]]]
            else:
                hit = [n for n in nodes if k in n]
            out['node_level'][k] = {'present_in_nodes': len(hit), 'of_nodes': len(nodes),
                                    'empty_or_null_in': len([n for n in nodes if (n.get(k.split('.')[0]) in (None, [], {}) if '.' in k else n.get(k) in (None, [], {}))]),
                                    'where': src}
        return out
    rep['contract'] = {}
    for sid in rep['skins_with_nodes_gt0']:
        e = json.load(open(os.path.join(S3D, sid, 'effects.json'), encoding='utf-8'))
        rep['contract'][sid] = contract_check(e, sid)

    # ---------- D) 贴图存在性（adapter L61/L72 实际算法）----------
    tex = []
    for sid, rec in inv.items():
        if not rec['has_effects_json']:
            continue
        e = json.load(open(os.path.join(S3D, sid, 'effects.json'), encoding='utf-8'))
        base_rel = str(e.get('assets_base') or '') + str(e.get('textures_dir') or 'sfx/tex/')
        n0 = len(e.get('nodes') or [])
        for n in (e.get('nodes') or []):
            tc = n.get('texture_candidate')
            if not tc:
                continue
            rel = base_rel + str(tc).replace('.dds', '.png')
            # viewer 的 manifestUrl = assets/3d/weapon_skin/<sid>/viewer.json
            abs_path = os.path.normpath(os.path.join(S3D, sid, rel))
            url = BASE + 'assets/3d/weapon_skin/%s/%s' % (sid, rel)
            tex.append({'skin_id': sid, 'node': n.get('name'), 'texture_candidate': tc,
                        'texture_src': n.get('texture'), 'resolved_rel': rel,
                        'local': abs_path, 'disk': os.path.isfile(abs_path),
                        'http': http_status(url) if n0 else None, 'url': url if n0 else None})
    rep['textures'] = tex
    rep['textures_missing'] = [t for t in tex if not t['disk']]
    rep['textures_total'] = len(tex)
    rep['textures_disk_ok'] = sum(1 for t in tex if t['disk'])

    # ---------- E) .sfx 源文件全库定位 ----------
    sfx_files = []
    t0 = time.time()
    for root, dirs, files in os.walk(PACK):
        for f in files:
            if f.lower().endswith('.sfx'):
                sfx_files.append(os.path.join(root, f))
    for root, dirs, files in os.walk(WIKI):
        for f in files:
            if f.lower().endswith('.sfx'):
                sfx_files.append(os.path.join(root, f))
    rep['sfx_files_found'] = len(sfx_files)
    rep['sfx_walk_seconds'] = round(time.time() - t0, 1)
    rep['sfx_index'] = sorted(sfx_files)
    # 4 个有 effects.json 的皮肤，按 skin primary/secondary id 找同名 .sfx
    rep['sfx_lookup'] = {}
    for sid in sorted(rep['skins_with_effects_json']):
        e = json.load(open(os.path.join(S3D, sid, 'effects.json'), encoding='utf-8'))
        src = e.get('sfx_source') or {}
        lp = str(src.get('logical_path') or '')
        base = os.path.basename(lp.replace('\\', '/'))
        hits = [p for p in sfx_files if base and base.lower() in p.lower()]
        prim = (e.get('skin') or {}).get('primary')
        hits2 = [p for p in sfx_files if prim and str(prim).lower() in p.lower()]
        rep['sfx_lookup'][sid] = {'logical_path': lp, 'basename': base, 'found_by_basename': hits[:5],
                                  'primary': prim, 'found_by_primary': hits2[:5],
                                  'nodes': len(e.get('nodes') or []), 'status': e.get('status'),
                                  'status_reason': e.get('status_reason')}

    # ---------- F) 1110171 的 .sfx XML 结构 ----------
    tgt = None
    for p in sfx_files:
        if 'fx_skin_1003_010_zs_02' in p.lower():
            tgt = p
            break
    rep['sfx_parse'] = {'target': tgt}
    if tgt:
        raw = open(tgt, 'rb').read()
        txt2 = raw.decode('gbk', errors='replace')
        rep['sfx_parse']['bytes'] = len(raw)
        rep['sfx_parse']['decl'] = txt2.split('\n')[0][:200]
        rep['sfx_parse']['root_tags'] = re.findall(r'<([A-Za-z_][\w:]*)[ >]', txt2)[:12]
        tags = collections.Counter(re.findall(r'<([A-Za-z_][\w:]*)[ >/]', txt2))
        rep['sfx_parse']['tag_counts'] = dict(tags.most_common(40))
        attrs = collections.Counter(re.findall(r'\s([A-Za-z_][\w]*)\s*=\s*"', txt2))
        rep['sfx_parse']['attr_counts'] = dict(attrs.most_common(60))
        # 关键字段抽样
        for key in ('ParticlesPerSecond', 'MinSpriteLifespan', 'MaxSpriteLifespan', 'FxStartTime', 'FxLifeSpan',
                    'FxIgnore', 'BlendMode', 'EmissionRadiusFrame', 'MaxSpriteVelocityFrame', 'SpriteScaleFrame',
                    'ColorFrame', 'GenerateChaos', 'FxName', 'Texture', 'Material'):
            m = re.findall(r'<%s[^>]*>' % key, txt2)[:3]
            rep['sfx_parse'].setdefault('samples', {})[key] = [x[:200] for x in m]
        rep['sfx_parse']['tag_names_sample'] = re.findall(r'<Tag>\s*([^<]{1,40})</Tag>', txt2)[:20]
        rep['sfx_parse']['name_attrs'] = re.findall(r'\bName\s*=\s*"([^"]{1,60})"', txt2)[:25]
        rep['sfx_parse']['texture_refs'] = sorted(set(re.findall(r'[Tt]exture[^>]*?"([^"]+\.(?:tga|dds|png|tif))"', txt2)))[:25]
    # 3 个 nodes=0 的皮肤：源在不在
    rep['nodes0_verdict'] = {}
    for sid in rep['skins_with_effects_but_nodes0']:
        e = json.load(open(os.path.join(S3D, sid, 'effects.json'), encoding='utf-8'))
        prim = (e.get('skin') or {}).get('primary')
        cand = [p for p in sfx_files if prim and str(prim).lower() in p.lower()]
        rep['nodes0_verdict'][sid] = {
            'status': e.get('status'), 'status_reason': e.get('status_reason'), 'primary': prim,
            'sfx_for_primary_found': cand[:5], 'sfx_source_field': e.get('sfx_source'),
            'unsupported': e.get('unsupported'), 'note': e.get('note')}

    json.dump(rep, open(os.path.join(OUT, 'FX_effects_audit.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    # ---------- 打印 ----------
    print('== 皮肤总数 %d；有 effects.json 的 %d 个：%s' % (rep['skins_total'], len(rep['skins_with_effects_json']), rep['skins_with_effects_json']))
    for sid in rep['skins_with_effects_json']:
        v = inv[sid]
        print('   %-8s schema=%-38s status=%-14s nodes=%-3s tags=%s bytes=%s' % (
            sid, str(v.get('schema')), str(v.get('status')), v.get('nodes'), json.dumps(v.get('node_tags'), ensure_ascii=False), v.get('effects_bytes')))
        print('            status_reason=%s' % str(v.get('status_reason'))[:200])
        print('            viewer.effects=%s' % json.dumps(v.get('viewer_effects'), ensure_ascii=False))
    print('== 板上：%d 卡；有 effects.json 的卡 %d；有 nodes>0 的卡 %d %s' % (
        rep['board']['items'], rep['board']['items_with_effects_json'], rep['board']['items_with_nodes_gt0'],
        rep['board']['items_with_nodes_gt0_ids']))
    print('== nodes=0 的皮肤 %s → 逐个判定：' % rep['skins_with_effects_but_nodes0'])
    for sid, v in rep['nodes0_verdict'].items():
        print('   %-8s primary=%-14s 源.sfx命中=%s' % (sid, v['primary'], json.dumps(v['sfx_for_primary_found'], ensure_ascii=False)))
        print('            status_reason=%s' % str(v['status_reason'])[:200])
    print('== 贴图：共 %d 条 texture_candidate，磁盘可解析 %d，缺 %d' % (rep['textures_total'], rep['textures_disk_ok'], len(rep['textures_missing'])))
    for t in rep['textures_missing'][:20]:
        print('   MISS %-8s %-22s rel=%s http=%s' % (t['skin_id'], t['node'], t['resolved_rel'], t['http']))
    print('== .sfx 全库命中 %d 个（%s 秒）' % (rep['sfx_files_found'], rep['sfx_walk_seconds']))
    for s in rep['sfx_lookup'].items():
        print('   %-8s base=%-34s found=%d primary=%s found_by_primary=%d' % (
            s[0], s[1]['basename'], len(s[1]['found_by_basename']), s[1]['primary'], len(s[1]['found_by_primary'])))
    print('== 契约对照（1110171）：')
    for k, v in (rep['contract'].get('1110171', {}).get('effects_level') or {}).items():
        print('   effects.%-16s present=%-6s value=%-22s %s' % (k, v['present'], v['value'], v['where']))
    for k, v in list((rep['contract'].get('1110171', {}).get('node_level') or {}).items()):
        print('   node %-34s 命中 %d/%d  %s' % (k, v['present_in_nodes'], v['of_nodes'], v['where']))
    sp = rep['sfx_parse']
    print('== .sfx 解析 %s (%s B)' % (sp.get('target'), sp.get('bytes')))
    print('   decl=%s' % str(sp.get('decl'))[:160])
    print('   tag_counts=%s' % json.dumps(sp.get('tag_counts'), ensure_ascii=False)[:900])
    print('   attr_counts=%s' % json.dumps(sp.get('attr_counts'), ensure_ascii=False)[:900])
    print('   samples=%s' % json.dumps(sp.get('samples'), ensure_ascii=False)[:1200])
    print('   texture_refs=%s' % json.dumps(sp.get('texture_refs'), ensure_ascii=False)[:400])
    print('json ->', os.path.join(OUT, 'FX_effects_audit.json'))


main()
