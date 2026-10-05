# -*- coding: utf-8 -*-
"""export_tex_png.py — 规范 RGBA 的 DDS→PNG 导出（唯一入口链 · 外审 v6 修复）

规则: 只允许通过 `dds_rgba_canonical` 解码；导出 PNG 时记录 provenance JSON。

用法:
  python export_tex_png.py <dds> <out.png> [--prov out.json]
  python export_tex_png.py --batch <spec.json>
     spec.json = {"items": [{"dds": "a.dds", "png": "a.png", "prov": "a.prov.json"}, ...]}
"""
import os, sys, json
import numpy as np
from PIL import Image
import dds_rgba_canonical as CAN


def export_one(dds, png, prov_path=None, verify_oiio=True):
    u8, prov = CAN.decode_dds_rgba_u8(dds, verify_oiio=verify_oiio)
    os.makedirs(os.path.dirname(os.path.abspath(png)) or '.', exist_ok=True)
    Image.fromarray(u8, 'RGBA').save(png)
    prov['png'] = os.path.abspath(png)
    prov['png_sha256'] = __import__('hashlib').sha256(open(png, 'rb').read()).hexdigest()
    if prov_path:
        json.dump(prov, open(prov_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return prov


def main():
    a = sys.argv[1:]
    if a and a[0] == '--batch':
        spec = json.load(open(a[1], encoding='utf-8'))
        for it in spec['items']:
            prov = export_one(it['dds'], it['png'], it.get('prov'))
            oc = prov.get('oiio_crosscheck') or {}
            print('%-34s <- %-26s | %dx%d %-5s | OIIO ok=%s md=%s | %s' % (
                os.path.basename(it['png']), os.path.basename(it['dds']),
                prov['width'], prov['height'], prov['fmt'], oc.get('ok'), oc.get('maxdiff'),
                prov['canonical_pixel_sha256'][:12]))
        return
    if len(a) < 2:
        print(__doc__); return
    dds, png = a[0], a[1]
    prov_path = a[a.index('--prov') + 1] if '--prov' in a else None
    prov = export_one(dds, png, prov_path)
    print(json.dumps({k: prov[k] for k in ('dds_sha256', 'decoder', 'raw_channel_order',
                                           'applied_swizzle', 'canonical_pixel_sha256')}, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
