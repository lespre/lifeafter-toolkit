# -*- coding: utf-8 -*-
"""extract_vcolor.py — .mesh v4 顶点色流读取与可视化（通用）
布局: header(78) + pos(tv*6) + nrm(tv*6) + pad(2) + idx(tf*6) + uv(tv*4) + [color(tv*4)] + trailer(16)
color 流存在条件: 子网格表 u16 标志含 0x0100 (=257) 且尺寸算术余量 == tv*4。
输出: 统计(总/逐子网格) + 量化唯一色 + 顶点色平涂预览图 + vcolor.npy
用法: python extract_vcolor.py <mesh> [--out-dir <dir>] [--roll 55]
"""
import sys, os, struct, math
import numpy as np
from PIL import Image
import render_neox_mesh as R

def main():
    mesh = sys.argv[1]
    out_dir = os.path.dirname(os.path.abspath(mesh)) if '--out-dir' not in sys.argv else sys.argv[sys.argv.index('--out-dir')+1]
    roll = 55.0 if '--roll' not in sys.argv else float(sys.argv[sys.argv.index('--roll')+1])
    base = os.path.splitext(os.path.basename(mesh))[0]
    buf = open(mesh, 'rb').read()
    subs = [struct.unpack_from('<IIH', buf, 0x0E + k*10) for k in range(3)]
    tv, tf = struct.unpack_from('<II', buf, 0x2E)
    has_flag = any((u & 0x0100) for _, _, u in subs)
    known = 78 + tv*6 + tv*6 + 2 + tf*6 + tv*4 + 16
    extra = len(buf) - known
    print('mesh=%s ver=%d tv=%d tf=%d subs=%s' % (base, struct.unpack_from('<H', buf, 4)[0], tv, tf, subs))
    print('color_flag=%s extra_bytes=%d (= tv*%.4f)' % (has_flag, extra, extra/tv))
    if not has_flag or abs(extra - tv*4) > 8:
        print('=> 无顶点色流（或布局不同）'); return
    off = 78 + tv*6 + tv*6 + 2 + tf*6 + tv*4
    cols = np.frombuffer(buf[off:off+tv*4], np.uint8).reshape(tv, 4).astype(np.float32)/255.0
    np.save(os.path.join(out_dir, base + '_vcolor.npy'), cols)
    for k, (vc, fc, u) in enumerate(subs):
        a0 = sum(s[0] for s in subs[:k]); a1 = a0 + vc
        c = cols[a0:a1]
        print('sub%d n=%d mean=[%.3f %.3f %.3f %.3f] std=[%.3f %.3f %.3f %.3f] min=[%.2f %.2f %.2f %.2f] max=[%.2f %.2f %.2f %.2f]'
              % (k, vc, *c.mean(0), *c.std(0), *c.min(0), *c.max(0)))
    print('overall mean=[%.3f %.3f %.3f %.3f] median=[%.3f %.3f %.3f %.3f]' % (*cols.mean(0), *np.median(cols, 0)))
    q = (cols[:, :3]*31).astype(np.int32)
    key = q.dot(np.array([1, 32, 1024]))
    uq, cnt = np.unique(key, return_counts=True)
    print('unique colors(q5) = %d; top12:' % len(uq))
    for v, c in sorted(zip(uq, cnt), key=lambda x: -x[1])[:12]:
        r = (v % 32)/31; g = ((v//32) % 32)/31; b = (v//1024)/31
        print('  (%.2f, %.2f, %.2f) x%d (%.1f%%)' % (r, g, b, c, 100.0*c/tv))
    # 预览: 顶点色平涂(与渲染器同一投影/roll), Gouraud 插值
    P, uv, faces, meta = R.parse_mesh(mesh)
    W, H = 1560, 1100
    c0 = (P.min(0) + P.max(0))/2.0; p = P - c0
    e = np.array([1.0, 0, 0], np.float32)
    up0 = np.array([0, 0, 1.0], np.float32)
    r0 = np.cross(up0, e); r0 /= np.linalg.norm(r0)
    u0 = np.cross(e, r0); u0 /= np.linalg.norm(u0)
    sx = p @ r0; sy = p @ u0; dep = p @ e
    a = math.radians(roll)
    Rr = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
    s = Rr @ np.stack([sx, sy]); sxx, syy = s[0], s[1]
    Mg = 60
    sc = min((W-2*Mg)/(sxx.max()-sxx.min()), (H-2*Mg)/(syy.max()-syy.min()))
    cx = (sxx.max()+sxx.min())/2; cy = (syy.max()+syy.min())/2
    vx = (sxx-cx)*sc + W/2; vy = H/2 - (syy-cy)*sc
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
        cco = (w0[..., None]*cols[fa] + w1[..., None]*cols[fb] + w2[..., None]*cols[fc])
        img[miny:maxy, minx:maxx][upd] = (np.clip(cco[..., :3], 0, 1)*255).astype(np.uint8)[upd]
        sub[upd] = dd[upd]
    out = os.path.join(out_dir, base + '_vcolor_preview.png')
    Image.fromarray(img).save(out)
    # alpha 通道预览(灰度)
    imgA = np.zeros((H, W), np.uint8); zb = np.full((H, W), -1e9, np.float32)
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
        aa = (w0*cols[fa, 3] + w1*cols[fb, 3] + w2*cols[fc, 3])
        imgA[miny:maxy, minx:maxx][upd] = (np.clip(aa, 0, 1)*255).astype(np.uint8)[upd]
        sub[upd] = dd[upd]
    outA = os.path.join(out_dir, base + '_vcolor_alpha.png')
    Image.fromarray(imgA).save(outA)
    print('preview ->', out, '| alpha ->', outA)

if __name__ == '__main__':
    main()
