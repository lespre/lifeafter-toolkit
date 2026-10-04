# -*- coding: utf-8 -*-
"""皮肤 3D 批量【探测】：对候选皮肤逐条探「能不能出 3D」，把结果写成 probe_result.json。

★ 2026-09-26 改名（原名 build_wiki_3d_batch.py）：原名与文档都声称它「批量出 GLB +
  海报 + viewer/provenance/effects + 投放 + 索引」，但代码实际只做探测 ——
  产出文件名就是 probe_result.json，从不写任何 GLB 或页面资产。
  名字与文档一起改对，避免下一个接手人以为这里有现成的落地器。

★ 它需要的两个输入（本脚本不生成，需预先备好）：
    <20_提取>/batch_3d/c159_skin_map.json
    <20_提取>/batch_3d/skins_grade5.json
  实测这两个文件全项目找不到、batch_3d 目录也不存在 ⇒ 当前跑不起来。

角色判定：法线用"RG 圆盘度"（010 先例），并按物理顺序模式 (a,m,n,s_m) 匹配 4 连组。

用法: python probe_skin_3d_batch.py [--limit N] [--only 1110013,...] [--dry]
"""
import os, re, sys, json, csv, math, struct, hashlib, shutil, subprocess, time
import numpy as np
from PIL import Image

E = r'E:\la拆包项目\03_执行\20_提取'
D = os.path.join(E, 'weapon')
BATCH = os.path.join(E, 'batch_3d')
WIKI = r'E:\la拆包项目\04_站点\\web'
WD = r'E:\la拆包项目\01_工具\工具库\02_图文音频渲染\皮肤链与渲染'
PY = r'C:\Users\<user>\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe'
sys.path.insert(0, WD)
from dds_rgba_canonical import decode_dds_rgba_u8
import mesh_parse2

ALL = os.listdir(D)
BY_ID = {}
for f in ALL:
    m = re.match(r'^(\d+)\.(\w+)$', f)
    if m:
        BY_ID[int(m.group(1))] = f


def sha16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


def feature(path):
    canon, prov = decode_dds_rgba_u8(path, verify_oiio=False)
    a = np.asarray(canon, np.float32)
    if a.max() > 1.5:
        a = a / 255.0
    rgb = a[..., :3]
    R, G, B = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    disk = float((((R - 0.5) ** 2 + (G - 0.5) ** 2) <= 0.25).mean())
    return dict(w=prov.get('width'), h=prov.get('height'), mean=rgb.reshape(-1, 3).mean(0).tolist(),
                std=float(rgb.std()), sat=float((rgb.max(2) - rgb.min(2)).mean()), disk=disk,
                bmean=float(B.mean()), rmean=float(R.mean()), gmean=float(G.mean()))


def is_normal(f):
    return f['disk'] > 0.90 and f['bmean'] > 0.80


def is_solid(f):
    return f['std'] < 0.06


def block_for(skin_dir, map_):
    hits = map_.get(skin_dir, [])
    if not hits:
        return None
    ids = sorted(int(h['file'].split('.')[0]) for h in hits)
    lo, hi = ids[0] - 40, ids[-1] + 40
    return [BY_ID[i] for i in range(lo, hi + 1) if i in BY_ID]


def pick_roles(files):
    """在块里找 4 连 DDS 组，模式 (base, param, normal, s_m)"""
    dds = sorted([f for f in files if f.endswith('.dds')], key=lambda f: int(f.split('.')[0]))
    out = []
    feats = {}
    for f in dds:
        try:
            feats[f] = feature(os.path.join(D, f))
        except Exception as e:
            feats[f] = None
    for i in range(len(dds) - 3):
        w = dds[i:i + 4]
        fs = [feats[x] for x in w]
        if any(x is None for x in fs):
            continue
        a, m, n, s = fs
        score = 0
        if is_normal(n): score += 3
        if is_normal(a): score -= 3
        if a['std'] > 0.03: score += 1
        if m['bmean'] > 0.95: score += 1
        if is_solid(s): score += 1
        out.append((score, w, fs, i))
    out.sort(key=lambda x: -x[0])
    return out, feats


def mesh_for(files, bind_boxes):
    best = None
    for f in sorted([x for x in files if x.endswith('.mesh')], key=lambda x: int(x.split('.')[0])):
        try:
            P3, uv, faces, meta = mesh_parse2.parse_mesh2(os.path.join(D, f))
        except Exception:
            continue
        mn, mx = P3.min(0), P3.max(0)
        ctr = (mn + mx) / 2; half = (mx - mn) / 2
        sc = 0
        for bc, bh in bind_boxes:
            d = float(np.abs(ctr - np.array(bc)).max() + np.abs(half - np.array(bh)).max())
            sc = max(sc, -d)
        subs = len(meta.get('sub_offsets') or [])
        best = best if (best and best[0] > sc) else (sc, f, len(P3), len(faces), subs, float(np.linalg.norm(half)))
    return best


def bind_boxes_of(path):
    b = open(path, 'rb').read()
    got = []
    for m in re.finditer(rb'\(([-\d.,]+)\),\(([-\d.,]+)\),([\d.]+)', b):
        try:
            c = [float(x) for x in m.group(1).split(b',')]
            h = [float(x) for x in m.group(2).split(b',')]
            got.append((c, h))
        except Exception:
            pass
    return got


def process(skin, map_, dry=False):
    d = skin['dir']
    files = block_for(d, map_)
    if not files:
        return {'id': skin['id'], 'name': skin['name'], 'dir': d, 'status': 'no_block'}
    c159 = [f for f in files if f.endswith('.c159')]
    bind = None
    for f in c159:
        b = open(os.path.join(D, f), 'rb').read()
        if b'BoundObject' in b and d.encode() in b:
            bind = f; break
    mat = None
    for f in c159:
        b = open(os.path.join(D, f), 'rb').read()
        if b'Material_' in b and d.encode() in b and b'.tga' in b:
            mat = f; break
    boxes = bind_boxes_of(os.path.join(D, bind)) if bind else []
    mesh = mesh_for(files, boxes)
    groups, feats = pick_roles(files)
    if not groups or groups[0][0] < 2:
        return {'id': skin['id'], 'name': skin['name'], 'dir': d, 'status': 'roles_unresolved',
                'block': len(files), 'dds': len([f for f in files if f.endswith('.dds')]),
                'best_score': groups[0][0] if groups else None}
    return {'id': skin['id'], 'name': skin['name'], 'dir': d, 'status': 'candidate',
            'bind': bind, 'material': mat, 'boxes': boxes,
            'mesh': mesh[1] if mesh else None, 'mesh_verts': mesh[2] if mesh else None,
            'mesh_score': round(mesh[0], 3) if mesh else None, 'mesh_subs': mesh[4] if mesh else None,
            'group': groups[0][1], 'score': groups[0][0], 'feats': {k: groups[0][2][i] for i, k in enumerate('amns')},
            'block': len(files)}


def _require_inputs():
    """开工前自检输入。缺东西就【明确点名怎么补】，不丢裸 FileNotFoundError。"""
    need = {
        os.path.join(BATCH, 'c159_skin_map.json'): '皮肤 → c159 材质映射',
        os.path.join(BATCH, 'skins_grade5.json'): '候选皮肤清单',
    }
    missing = [f'{p}（{why}）' for p, why in need.items() if not os.path.isfile(p)]
    if missing:
        print('[probe_skin_3d_batch] 缺少输入，无法开工：', file=sys.stderr)
        for m in missing:
            print('  ✗ ' + m, file=sys.stderr)
        print(f'[probe_skin_3d_batch] 它们应放在 {BATCH}', file=sys.stderr)
        print('[probe_skin_3d_batch] ★ 本脚本只做探测，不出 GLB；'
              '要真出件请看 ② 线的「单皮肤落地器」缺口（待修 B1）', file=sys.stderr)
        return False
    return True


if __name__ == '__main__':
    if not _require_inputs():
        raise SystemExit(2)
    a = sys.argv[1:]
    map_ = json.load(open(os.path.join(BATCH, 'c159_skin_map.json'), encoding='utf-8'))
    skins = json.load(open(os.path.join(BATCH, 'skins_grade5.json'), encoding='utf-8'))
    if '--only' in a:
        want = set(a[a.index('--only') + 1].split(','))
        skins = [s for s in skins if s['id'] in want or s['dir'] in want]
    if '--limit' in a:
        skins = skins[:int(a[a.index('--limit') + 1])]
    res = []
    for s in skins:
        t0 = time.time()
        r = process(s, map_, dry='--dry' in a)
        r['secs'] = round(time.time() - t0, 1)
        res.append(r)
        print(json.dumps(r, ensure_ascii=False)[:400], flush=True)
    json.dump(res, open(os.path.join(BATCH, 'probe_result.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('\n状态汇总:')
    from collections import Counter
    for k, v in Counter(r['status'] for r in res).items():
        print('  %-18s %d' % (k, v))
