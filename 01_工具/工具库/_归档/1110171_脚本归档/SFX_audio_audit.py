# -*- coding: utf-8 -*-
"""SFX_audio_audit.py — 武器皮肤「皮肤音效」区块数据流 / 覆盖率 / 404 全量实测（只读）。

实测内容：
 1. 运行时数据源（board.html 实际加载的是 .js）解析：window.WEAPON_SKIN_AUDIO_ATTACHMENTS
 2. 每条音频的解析 URL：assets/audio/weapon_skin/<group.dir||skin.dir>/<file>
 3. 逐条 HTTP 状态码（127.0.0.1:8765）+ 磁盘是否存在
 4. 板块条目集（data/workbench_boards|boards/<board>.js）与 bank 的交集 → 有 SFX 区块的卡数
 5. 404 的 basename 在 03拆包产物 下的定位（全量 .wav basename 索引）
 6. effects.json 的键结构（判定“特效”还是“音效”）
输出：SFX_audio_audit.json（本目录）
"""
import json, os, re, sys, urllib.request, urllib.error, collections, time, io

WIKI = r'E:\la拆包项目\08Lifeafter wiki'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
PACK = r'E:\la拆包项目\03拆包产物'
BASE_HTTP = 'http://127.0.0.1:8765/'
BOARD = 'weapon_skin_sfx_text_sources'


def load_js_obj(path, var_re):
    txt = open(path, encoding='utf-8').read()
    m = re.search(var_re, txt, re.S)
    if not m:
        raise SystemExit('未匹配到变量: %s @ %s' % (var_re, path))
    return json.loads(m.group(1))


def http_status(url, timeout=20):
    for method in ('HEAD', 'GET'):
        try:
            req = urllib.request.Request(url, method=method)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, r.headers.get('Content-Type'), r.headers.get('Content-Length')
        except urllib.error.HTTPError as e:
            return e.code, None, None
        except Exception as e:
            if method == 'GET':
                return 'ERR:' + type(e).__name__, None, None
    return 'ERR', None, None


def main():
    rep = {'generated': time.strftime('%Y-%m-%d %H:%M:%S')}

    # ---------- 1) 运行时 JS 数据源 ----------
    p_js = os.path.join(WIKI, 'data', 'weapon_skin_audio_attachments.js')
    p_json = os.path.join(WIKI, 'data', 'weapon_skin_audio_attachments.json')
    js_obj = load_js_obj(p_js, r'WEAPON_SKIN_AUDIO_ATTACHMENTS\s*=\s*(\{.*\})\s*;?\s*$')
    json_obj = json.load(open(p_json, encoding='utf-8'))
    rep['source'] = {
        'js_file': p_js, 'js_bytes': os.path.getsize(p_js),
        'json_file': p_json, 'json_bytes': os.path.getsize(p_json),
        'js_json_identical': js_obj == json_obj,
        'schema': js_obj.get('schema'), 'generated': js_obj.get('generated'),
        'method': js_obj.get('method'), 'by': js_obj.get('by'),
        'batch2': js_obj.get('batch2'),
    }
    skins = js_obj['skins']

    # ---------- 2) 逐条解析 ----------
    items = []
    n_pending = 0
    for sid, rec in skins.items():
        for g in (rec.get('groups') or []):
            gdir = g.get('dir') or rec.get('dir')
            for x in (g.get('items') or []):
                url = BASE_HTTP + 'assets/audio/weapon_skin/' + str(gdir) + '/' + str(x.get('file'))
                local = os.path.join(WIKI, 'assets', 'audio', 'weapon_skin', str(gdir), str(x.get('file')))
                if x.get('pending'):
                    n_pending += 1
                items.append({'skin_id': sid, 'skin_name': rec.get('name'), 'skin_dir': rec.get('dir'),
                              'group_label': g.get('label') or '', 'group_dir': g.get('dir'),
                              'label': x.get('label'), 'file': x.get('file'), 'pending': bool(x.get('pending')),
                              'url': url, 'local': local, 'rel': 'assets/audio/weapon_skin/%s/%s' % (gdir, x.get('file'))})
    rep['totals'] = {
        'skins_in_bank': len(skins),
        'groups': sum(len(r.get('groups') or []) for r in skins.values()),
        'items': len(items),
        'items_pending': n_pending,
        'unique_files': len(set(i['rel'] for i in items)),
        'unique_dirs': len(set(str(i['group_dir'] or i['skin_dir']) for i in items)),
    }

    # ---------- 3) HTTP + 磁盘 ----------
    for i in items:
        i['http'], i['ctype'], i['clen'] = http_status(i['url'])
        i['on_disk'] = os.path.isfile(i['local'])
        i['disk_bytes'] = os.path.getsize(i['local']) if i['on_disk'] else None
    rep['items'] = items

    by_status = collections.Counter(str(i['http']) for i in items)
    rep['http_status_counts'] = dict(by_status)
    missing = [i for i in items if i['http'] != 200]
    rep['missing_count'] = len(missing)
    rep['missing'] = [{'skin_id': i['skin_id'], 'skin_name': i['skin_name'], 'label': i['label'],
                       'file': i['file'], 'rel': i['rel'], 'http': i['http'],
                       'on_disk': i['on_disk'], 'pending': i['pending']} for i in missing]
    # 每条皮肤缺多少
    per_skin = {}
    for sid, rec in skins.items():
        tot = [i for i in items if i['skin_id'] == sid]
        bad = [i for i in tot if i['http'] != 200]
        per_skin[sid] = {'name': rec.get('name'), 'dir': rec.get('dir'), 'items': len(tot),
                         'missing': len(bad), 'missing_files': [i['file'] for i in bad],
                         'ok': len(tot) - len(bad)}
    rep['per_skin'] = per_skin
    rep['skins_all_ok'] = sum(1 for v in per_skin.values() if v['missing'] == 0)
    rep['skins_with_missing'] = sum(1 for v in per_skin.values() if v['missing'] > 0)

    # ---------- 4) 板块条目 ↔ bank 覆盖率 ----------
    board_files = [os.path.join(WIKI, 'data', 'workbench_boards', BOARD + '.js'),
                   os.path.join(WIKI, 'data', 'boards', BOARD + '.js')]
    rep['board'] = {'candidates': board_files}
    for bf in board_files:
        if os.path.isfile(bf):
            obj = load_js_obj(bf, r'WIKI_BOARD_%s\s*=\s*(\{.*\})\s*;?\s*$' % BOARD)
            rep['board']['file'] = bf
            rep['board']['bytes'] = os.path.getsize(bf)
            its = obj.get('items') or []
            rep['board']['items'] = len(its)
            keys = set(skins.keys())
            with_sfx = []
            for it in its:
                cand = [it.get('skin_id'), it.get('skin_item_id'), it.get('id'), it.get('structural_record_key')]
                hit = next((str(c) for c in cand if c is not None and str(c) in keys), None)
                if hit:
                    with_sfx.append(hit)
            rep['board']['items_with_sfx_section'] = len(with_sfx)
            rep['board']['items_without'] = len(its) - len(with_sfx)
            rep['board']['bank_skins_absent_from_board'] = sorted(keys - set(with_sfx))
            rep['board']['audio_items_visible_on_board'] = sum(
                len([i for i in items if i['skin_id'] == s]) for s in set(with_sfx))
            rep['board']['sfx_label_field'] = 'skin_id/skin_item_id/id/structural_record_key（试键顺序同 board.html L574）'
            break

    # ---------- 5) 404 的 basename 在解包产物里定位 ----------
    want = set(os.path.basename(i['file']) for i in missing)
    want_stem = set(os.path.splitext(w)[0].lower() for w in want)
    wav_index = {}
    t0 = time.time()
    for root, dirs, files in os.walk(PACK):
        for f in files:
            if f.lower().endswith(('.wav', '.ogg', '.mp3', '.wem', '.bnk', '.fsb', '.ogg')):
                wav_index.setdefault(f.lower(), []).append(os.path.join(root, f))
    rep['pack_wav_index'] = {'files': sum(len(v) for v in wav_index.values()),
                             'unique_names': len(wav_index), 'walk_seconds': round(time.time() - t0, 1)}
    located = {}
    for w in sorted(want):
        k = w.lower()
        if k in wav_index:
            located[w] = wav_index[k][:6]
    stem_located = {}
    for w in sorted(want):
        stem = os.path.splitext(w)[0].lower()
        for name, paths in wav_index.items():
            if os.path.splitext(name)[0] == stem and name != w.lower():
                stem_located.setdefault(w, []).extend(paths[:4])
    rep['missing_located_in_pack'] = located
    rep['missing_located_by_stem'] = stem_located
    rep['missing_not_found_anywhere'] = sorted(w for w in want if w not in located and w not in stem_located)

    # ---------- 6) effects.json 结构 ----------
    sfx_dirs = sorted(set(str(i['group_dir'] or i['skin_dir']) for i in items))
    eff = {}
    dirs3d = os.path.join(WIKI, 'assets', '3d', 'weapon_skin')
    for sid in sorted(skins.keys()):
        p = os.path.join(dirs3d, sid, 'effects.json')
        if os.path.isfile(p):
            d = json.load(open(p, encoding='utf-8'))
            keys = sorted(d.keys())
            eff[sid] = {'path': p, 'bytes': os.path.getsize(p), 'top_keys': keys,
                        'has_audio_keys': [k for k in keys if re.search(r'audio|sound|wav|music|voice|bank', k, re.I)],
                        'nodes': len(d.get('nodes') or []),
                        'sample_keys': keys[:12]}
    rep['effects_json'] = eff
    rep['effects_json_count'] = len(eff)
    rep['audio_dir_dirs_on_disk'] = sorted(os.listdir(os.path.join(WIKI, 'assets', 'audio', 'weapon_skin')))
    rep['bank_dirs_set'] = sfx_dirs
    rep['bank_dirs_missing_on_disk'] = sorted(set(sfx_dirs) - set(rep['audio_dir_dirs_on_disk']))

    json.dump(rep, open(os.path.join(OUT, 'SFX_audio_audit.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    # ---------- 打印 ----------
    print('== 数据源 ==', json.dumps(rep['source'], ensure_ascii=False))
    print('== 总量 ==', json.dumps(rep['totals'], ensure_ascii=False))
    print('== HTTP 状态分布 ==', json.dumps(rep['http_status_counts'], ensure_ascii=False))
    print('== 缺失 %d 条 / %d 皮肤有缺失 ==' % (rep['missing_count'], rep['skins_with_missing']))
    print('== 板块覆盖 ==', json.dumps({k: v for k, v in rep['board'].items() if k != 'candidates'}, ensure_ascii=False))
    print('== 解包产物音频索引 ==', json.dumps(rep['pack_wav_index'], ensure_ascii=False))
    print('== 404 在解包产物中命中: %d 个 basename' % len(located))
    print('== 404 完全未定位: %d 个' % len(rep['missing_not_found_anywhere']))
    print('== 404 清单（前 40） ==')
    for m in rep['missing'][:40]:
        print('   %-9s %-12s %s  http=%s disk=%s pending=%s' % (m['skin_id'], m['skin_name'], m['rel'], m['http'], m['on_disk'], m['pending']))
    print('== effects.json ==', rep['effects_json_count'], '个；示例：')
    for sid, v in list(eff.items())[:3]:
        print('   ', sid, json.dumps(v, ensure_ascii=False)[:400])
    print('== assets/audio/weapon_skin 磁盘目录数 =', len(rep['audio_dir_dirs_on_disk']),
          ' bank 引用目录数 =', len(sfx_dirs), ' bank 缺失目录 =', rep['bank_dirs_missing_on_disk'])
    print('json ->', os.path.join(OUT, 'SFX_audio_audit.json'))


main()
