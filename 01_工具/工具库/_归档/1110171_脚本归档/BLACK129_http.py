# -*- coding: utf-8 -*-
"""BLACK129_http.py — 核对 8765 实际服务的 viewer.js 与 1110129/1110145 cube 资源（sha + 状态）。只写 BLACK129_*。"""
import hashlib, json, os, urllib.request, urllib.error

WIKI = r'E:\la拆包项目\08Lifeafter wiki'
BASE = 'http://127.0.0.1:8765/'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'


def get(url, head=False):
    req = urllib.request.Request(url, method='HEAD' if head else 'GET')
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.headers.get('Content-Type'), (b'' if head else r.read())
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get('Content-Type') if e.headers else None, b''
    except Exception as e:
        return 'ERR:' + e.__class__.__name__, str(e)[:80], b''


res = {'viewer_js': {}, 'files': {}}
# 1) served viewer.js vs disk
p = os.path.join(WIKI, 'assets', 'weapon_skin_viewer.js')
disk = open(p, 'rb').read()
st, ct, body = get(BASE + 'assets/weapon_skin_viewer.js')
res['viewer_js'] = {
    'http_status': st, 'mime': ct, 'served_sha256': hashlib.sha256(body).hexdigest(),
    'served_bytes': len(body), 'disk_sha256': hashlib.sha256(disk).hexdigest(), 'disk_bytes': len(disk),
    'match': hashlib.sha256(body).hexdigest() == hashlib.sha256(disk).hexdigest(),
}

# 2) per-skin cube assets over HTTP
paths = []
for skin, cubename in (('1110129', 'qiangpi'), ('1110145', 'bg61f_light_spherereflectioncapture_1')):
    paths.append(('assets/3d/weapon_skin/%s/src_cube/%s.dds' % (skin, cubename), skin, 'dds'))
    for i in range(6):
        paths.append(('assets/3d/weapon_skin/%s/src_cube/faces/%s_f%d_m0.png' % (skin, cubename, i), skin, 'face%d' % i))
    paths.append(('assets/3d/weapon_skin/%s/neox_material.json' % skin, skin, 'neox_material.json'))
    paths.append(('assets/3d/weapon_skin/%s/viewer.json' % skin, skin, 'viewer.json'))

for rel, skin, kind in paths:
    st, ct, body = get(BASE + rel)
    d = os.path.join(WIKI, rel.replace('/', os.sep))
    dsha = hashlib.sha256(open(d, 'rb').read()).hexdigest() if os.path.isfile(d) else None
    res['files'].setdefault(skin, {})[kind] = {
        'status': st, 'mime': ct, 'bytes': (len(body) if body else None),
        'disk_bytes': (os.path.getsize(d) if os.path.isfile(d) else None),
        'served_sha16': (hashlib.sha256(body).hexdigest()[:16] if body else None),
        'disk_sha16': (dsha[:16] if dsha else None),
        'match': (bool(body) and dsha is not None and hashlib.sha256(body).hexdigest() == dsha),
    }

# 3) per-prim t_custom_ibl keys as actually served
for skin in ('1110129', '1110145'):
    st, ct, body = get(BASE + 'assets/3d/weapon_skin/%s/neox_material.json' % skin)
    try:
        d = json.loads(body.decode('utf-8'))
    except Exception as e:
        res.setdefault('prim_ibl', {})[skin] = {'error': str(e)}
        continue
    rows = []
    for i, pr in enumerate(d.get('primitives', [])):
        T = pr.get('textures') or {}
        t = T.get('t_custom_ibl')
        rows.append({'i': i, 'material': pr.get('material'), 'shader': pr.get('shader'),
                     'tex_keys': sorted(T.keys()),
                     'ibl': (None if t is None else {'local_file': t.get('local_file'),
                                                     'logical': t.get('logical_path') or t.get('logical'),
                                                     'faces_glob': t.get('faces_glob'),
                                                     'state': t.get('state')}),
                     'req': pr.get('required_slots'), 'missing': pr.get('missing_required')})
    res.setdefault('prim_ibl', {})[skin] = rows

json.dump(res, open(os.path.join(OUT, 'BLACK129_http.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

print('viewer.js served==disk:', res['viewer_js']['match'], res['viewer_js']['served_sha256'][:16], res['viewer_js']['disk_sha256'][:16], res['viewer_js']['served_bytes'])
for skin in ('1110129', '1110145'):
    print('===', skin)
    for kind, v in res['files'][skin].items():
        print('   %-18s %-5s mime=%-22s served=%-9s disk=%-9s match=%s' % (kind, v['status'], v['mime'], v['bytes'], v['disk_bytes'], v['match']))
    for r in res.get('prim_ibl', {}).get(skin, []):
        print('   prim%-2d %-18s shader=%-28s keys=%s' % (r['i'], r['material'], r['shader'], ','.join(r['tex_keys'])))
        print('        ibl=%s' % json.dumps(r['ibl'], ensure_ascii=False))
print('json ->', os.path.join(OUT, 'BLACK129_http.json'))
