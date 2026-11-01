import json, struct, sys, os, glob

def glb_info(path):
    with open(path, 'rb') as f:
        data = f.read()
    size = len(data)
    if data[:4] != b'glTF':
        return {'err': 'not_glb'}
    ver, total = struct.unpack('<II', data[4:12])
    off = 12
    js = None
    while off < len(data):
        clen, ctype = struct.unpack('<I4s', data[off:off+8])
        chunk = data[off+8:off+8+clen]
        if ctype == b'JSON':
            js = json.loads(chunk.decode('utf-8'))
            break
        off += 8 + clen + ((4 - clen % 4) % 4)
    if not js:
        return {'err': 'no_json'}
    tris = 0
    for m in js.get('meshes', []):
        for p in m.get('primitives', []):
            idx = p.get('indices')
            if idx is not None:
                acc = js['accessors'][idx]
                tris += acc.get('count', 0) // 3
            else:
                pos = p.get('attributes', {}).get('POSITION')
                if pos is not None:
                    tris += js['accessors'][pos].get('count', 0) // 3
    mats = js.get('materials', [])
    texs = js.get('textures', [])
    imgs = js.get('images', [])
    # 材质里是否引用 baseColorTexture
    withtex = 0
    for m in mats:
        pbr = m.get('pbrMetallicRoughness', {})
        if 'baseColorTexture' in pbr:
            withtex += 1
    return {
        'kb': round(size/1024),
        'nodes': len(js.get('nodes', [])),
        'meshes': len(js.get('meshes', [])),
        'prims': sum(len(m.get('primitives', [])) for m in js.get('meshes', [])),
        'tris': tris,
        'mats': len(mats),
        'texs': len(texs),
        'imgs': len(imgs),
        'mat_with_basecolor_tex': withtex,
        'mat_names': [m.get('name', '?') for m in mats][:8],
    }

targets = []
for pat in sys.argv[1:]:
    targets.extend(sorted(glob.glob(pat)))

for p in targets:
    try:
        info = glb_info(p)
    except Exception as e:
        info = {'err': repr(e)}
    print(os.path.relpath(p).replace('\\', '/'), '|', json.dumps(info, ensure_ascii=False))
