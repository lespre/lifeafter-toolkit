# -*- coding: utf-8 -*-
"""unlit_render.py — 无光照采样渲染（贴图直出, 无任何灯光/参数）
用途: "无光照采样结果" — 把某张贴图直接映射到网格上, 确认贴图内容与形状的对应。
用法: python unlit_render.py <mesh> <texture(dds|png)> <out.png> [--roll 55] [--flip-h] [--srgb] [--size WxH]
  --srgb: 把贴图按已有 sRGB 值直接输出(默认); 不加时为直通(不做变换)。
"""
import sys, os, math
import numpy as np
from PIL import Image
import mesh_parse2 as MP

def load_tex(path):
    if path.lower().endswith('.dds'):
        from raw_anchor import decode_dds_bc7
        a = decode_dds_bc7(path)
        return a.astype(np.float32) / 255.0, a
    im = Image.open(path).convert('RGBA')
    a = np.asarray(im)
    return a.astype(np.float32) / 255.0, a

def main():
    mesh = sys.argv[1]; texp = sys.argv[2]; out = sys.argv[3]
    args = sys.argv[4:]
    roll = float(args[args.index('--roll') + 1]) if '--roll' in args else 55.0
    flip = '--flip-h' in args
    W, H = (1560, 1100)
    if '--size' in args:
        W, H = [int(x) for x in args[args.index('--size') + 1].split('x')]
    P, uv, faces, meta = MP.parse_mesh2(mesh)
    tex, _ = load_tex(texp)
    c = (P.min(0) + P.max(0)) / 2.0; p = P - c
    e = np.array([1.0, 0, 0], np.float32)
    up0 = np.array([0, 0, 1.0], np.float32)
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
    TW, TH = tex.shape[1], tex.shape[0]
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
        uu = w0*uv[fa, 0] + w1*uv[fb, 0] + w2*uv[fc, 0]
        vv = w0*uv[fa, 1] + w1*uv[fb, 1] + w2*uv[fc, 1]
        tx = np.clip((uu*(TW-1)).astype(np.int32), 0, TW-1)
        ty = np.clip(((1.0-vv)*(TH-1)).astype(np.int32), 0, TH-1)
        cc = tex[ty, tx][..., :3]
        img[miny:maxy, minx:maxx][upd] = np.clip(cc*255, 0, 255).astype(np.uint8)[upd]
        sub[upd] = dd[upd]
    Image.fromarray(img).save(out)
    print('UNLIT OK ->', out, '| tex', os.path.basename(texp))

if __name__ == '__main__':
    main()
