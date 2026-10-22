# -*- coding: utf-8 -*-
"""silhouette_render.py — 网格轮廓/分区平涂渲染（通用, 变长子网格）
用途: 轮廓配准 (对比截图判网格同构) + 子网格分区识别。
用法:
  python silhouette_render.py <mesh> <out.png> [--roll 55] [--flip-h] [--size 1560x1100] [--mode sub|vcol|vc_a]
"""
import sys, os, math
import numpy as np
from PIL import Image
import mesh_parse2 as MP

PAL = [(235,235,235),(90,170,255),(255,95,205),(255,200,80),(120,255,170),(255,120,80),(170,120,255),(120,230,255),(240,240,120),(140,255,230)]

def main():
    mesh = sys.argv[1]; out = sys.argv[2]
    args = sys.argv[3:]
    roll = float(args[args.index('--roll') + 1]) if '--roll' in args else 55.0
    flip = '--flip-h' in args
    W, H = (1560, 1100)
    if '--size' in args:
        W, H = [int(x) for x in args[args.index('--size') + 1].split('x')]
    mode = args[args.index('--mode') + 1] if '--mode' in args else 'sub'
    eye = (1.0, 0.0, 0.0)
    if '--eye' in args:
        eye = tuple(float(x) for x in args[args.index('--eye') + 1].split(','))
    P, uv, faces, meta = MP.parse_mesh2(mesh)
    c = (P.min(0) + P.max(0)) / 2.0; p = P - c
    e = np.array(eye, np.float32); e /= np.linalg.norm(e)
    up0 = np.array([0, 0, 1.0], np.float32)
    if abs(float(np.dot(up0, e))) > 0.9:
        up0 = np.array([0, 1.0, 0], np.float32)
    r0 = np.cross(up0, e); r0 /= np.linalg.norm(r0)
    u0 = np.cross(e, r0); u0 /= np.linalg.norm(u0)
    sx = p @ r0; sy = p @ u0; dep = p @ e
    a = math.radians(roll)
    Rr = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
    s = Rr @ np.stack([sx, sy]); sxx, syy = s[0], s[1]
    if flip:
        sxx = -sxx
    Mg = 60
    sc = min((W-2*Mg)/(sxx.max()-sxx.min()), (H-2*Mg)/(syy.max()-syy.min()))
    cx = (sxx.max()+sxx.min())/2; cy = (syy.max()+syy.min())/2
    vx = (sxx-cx)*sc + W/2; vy = H/2 - (syy-cy)*sc
    sub_of = np.zeros(len(P), np.int32)
    for k, (a0, a1) in enumerate(meta['sub_offsets']):
        sub_of[a0:a1] = k
    vcol = meta.get('vcol')
    img = np.zeros((H, W, 3), np.uint8); zb = np.full((H, W), -1e9, np.float32)
    order = np.argsort(dep[faces].mean(1))
    for t in order:
        fa, fb, fc = faces[t]
        x0, y0 = vx[fa], vy[fa]; x1, y1 = vx[fb], vy[fb]; x2, y2 = vx[fc], vy[fc]
        minx = max(int(min(x0, x1, x2)), 0); maxx = min(int(max(x0, x1, x2))+1, W)
        miny = max(int(min(y0, y1, y2)), 0); maxy = min(int(max(y0, y1, y2))+1, H)
        if maxx <= minx or maxy <= miny: continue
        gx, gy = np.meshgrid(np.arange(minx, maxx)+0.5, np.arange(miny, maxy)+0.5)
        d0 = (x1-x0)*(gy-y0)-(y1-y0)*(gx-x0); d1 = (x2-x1)*(gy-y1)-(y2-y1)*(gx-x1); d2 = (x0-x2)*(gy-y2)-(y0-y2)*(gx-x2)
        m = ((d0 >= 0) & (d1 >= 0) & (d2 >= 0)) | ((d0 <= 0) & (d1 <= 0) & (d2 <= 0))
        if not m.any(): continue
        area = d0+d1+d2
        w0 = d1/area; w1 = d2/area; w2 = d0/area
        dd = w0*dep[fa]+w1*dep[fb]+w2*dep[fc]
        sub = zb[miny:maxy, minx:maxx]; upd = m & (dd > sub)
        if not upd.any(): continue
        si = int(sub_of[fa])
        if mode == 'sub':
            col = np.array(PAL[si % len(PAL)], np.uint8)
            img[miny:maxy, minx:maxx][upd] = col
        elif mode in ('vcol', 'vc_a') and vcol is not None:
            ch = 3 if mode == 'vc_a' else 0
            if mode == 'vc_a':
                cc = (w0*vcol[fa, 3] + w1*vcol[fb, 3] + w2*vcol[fc, 3])
                colv = (np.clip(cc, 0, 1)*255).astype(np.uint8)
                img[miny:maxy, minx:maxx][upd] = np.stack([colv, colv, colv], -1)[upd]
            else:
                cco = (w0[..., None]*vcol[fa, :3] + w1[..., None]*vcol[fb, :3] + w2[..., None]*vcol[fc, :3])
                img[miny:maxy, minx:maxx][upd] = (np.clip(cco, 0, 1)*255).astype(np.uint8)[upd]
        sub[upd] = dd[upd]
    Image.fromarray(img).save(out)
    print('OK ->', out, '| subs=%d flags=%s vcol=%s' % (len(meta['subs']), [hex(u) for u in meta['flags']], vcol is not None))

if __name__ == '__main__':
    main()
