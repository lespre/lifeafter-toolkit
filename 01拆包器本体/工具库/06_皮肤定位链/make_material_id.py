# -*- coding: utf-8 -*-
"""make_material_id.py — 辅助工具: 输出材质 ID 图 (子网格分区着色) + 图例 JSON。
不改动冻结渲染器; 仅用于交付的 "Material" 层可视化 (材质归属一眼可查)。
用法: python make_material_id.py <mesh> <out.png> [--legend out.json]
"""
import sys, os, json, math
import numpy as np
from PIL import Image
import render_neox_mesh as R

COLORS = {0: (200, 200, 200), 1: (80, 170, 255), 2: (255, 90, 200)}  # 白/蓝/品红

def main():
    mesh = sys.argv[1]; out = sys.argv[2]
    P, uv, faces, meta = R.parse_mesh(mesh)
    if '--dual' in sys.argv:
        # 通用双持组合(与 render_material_layers.py --dual 同一数学): 左=180°旋转, 右=垂直翻转
        dual_sep = float(sys.argv[sys.argv.index('--dual-sep') + 1]) if '--dual-sep' in sys.argv else 0.62
        a_r = math.radians(55.0)
        e_d = np.array([1.0, 0.0, 0.0], np.float32)
        up_d = np.array([0, 0, 1.0], np.float32)
        r_d = np.cross(up_d, e_d); r_d /= np.linalg.norm(r_d)
        u_d = np.cross(e_d, r_d); u_d /= np.linalg.norm(u_d)
        w_x = (math.cos(a_r) * r_d - math.sin(a_r) * u_d).astype(np.float32)
        w_y = (math.sin(a_r) * r_d + math.cos(a_r) * u_d).astype(np.float32)
        c0d = (P.min(0) + P.max(0)) / 2.0
        Pc = P - c0d
        wg = float((Pc @ w_x).max() - (Pc @ w_x).min())
        P_L = Pc - 2 * np.outer(Pc @ w_x, w_x) - 2 * np.outer(Pc @ w_y, w_y)
        P_R = Pc - 2 * np.outer(Pc @ w_y, w_y)
        P_L = (P_L - w_x * (dual_sep * wg / 2)).astype(np.float32)
        P_R = (P_R + w_x * (dual_sep * wg / 2)).astype(np.float32)
        Nv = len(P)
        f_R = faces[:, ::-1] + Nv
        P = np.concatenate([P_L, P_R]).astype(np.float32)
        uv = np.concatenate([uv, uv]).astype(np.float32)
        faces = np.concatenate([faces, f_R]).astype(np.int32)
        old_so = meta['sub_offsets']
        meta['sub_offsets'] = list(old_so) + [(a0 + Nv, a1 + Nv) for (a0, a1) in old_so]
    W, H = (2260, 1150) if '--dual' in sys.argv else (1560, 1100)
    c = (P.min(0) + P.max(0)) / 2.0; p = P - c
    e = np.array([1.0, 0, 0], np.float32)
    up0 = np.array([0, 0, 1.0], np.float32)
    r0 = np.cross(up0, e); r0 /= np.linalg.norm(r0)
    u0 = np.cross(e, r0); u0 /= np.linalg.norm(u0)
    sx = p @ r0; sy = p @ u0; dep = p @ e
    a = math.radians(55.0)
    Rr = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]], np.float32)
    s = Rr @ np.stack([sx, sy]); sxx, syy = s[0], s[1]
    Mg = 60
    sc = min((W - 2*Mg)/(sxx.max()-sxx.min()), (H - 2*Mg)/(syy.max()-syy.min()))
    cx = (sxx.max()+sxx.min())/2; cy = (syy.max()+syy.min())/2
    vx = (sxx-cx)*sc + W/2; vy = H/2 - (syy-cy)*sc
    sub_of = np.zeros(len(P), np.int32)
    for k, (a0, a1) in enumerate(meta['sub_offsets']): sub_of[a0:a1] = k
    img = np.zeros((H, W, 3), np.uint8); zb = np.full((H, W), -1e9, np.float32)
    for t in np.argsort(dep[faces].mean(1)):
        fa, fb, fc = faces[t]
        x0, y0 = vx[fa], vy[fa]; x1, y1 = vx[fb], vy[fb]; x2, y2 = vx[fc], vy[fc]
        minx = max(int(min(x0, x1, x2)), 0); maxx = min(int(max(x0, x1, x2))+1, W)
        miny = max(int(min(y0, y1, y2)), 0); maxy = min(int(max(y0, y1, y2))+1, H)
        if maxx <= minx or maxy <= miny: continue
        gx, gy = np.meshgrid(np.arange(minx, maxx)+0.5, np.arange(miny, maxy)+0.5)
        d0 = (x1-x0)*(gy-y0)-(y1-y0)*(gx-x0); d1 = (x2-x1)*(gy-y1)-(y2-y1)*(gx-x1); d2 = (x0-x2)*(gy-y2)-(y0-y2)*(gx-x2)
        m = ((d0 >= 0) & (d1 >= 0) & (d2 >= 0)) | ((d0 <= 0) & (d1 <= 0) & (d2 <= 0))
        if not m.any(): continue
        area = d0+d1+d2; w0 = d1/area; w1 = d2/area; w2 = d0/area
        dd = w0*dep[fa]+w1*dep[fb]+w2*dep[fc]
        sub = zb[miny:maxy, minx:maxx]; upd = m & (dd > sub)
        if not upd.any(): continue
        si = int(sub_of[fa])
        col = np.array(COLORS.get(si, (255, 255, 0)), np.uint8)
        img[miny:maxy, minx:maxx][upd] = col
        sub[upd] = dd[upd]
    Image.fromarray(img).save(out)
    legend = {'sub_colors': {str(k): COLORS.get(k) for k in sorted(set(sub_of.tolist()))},
              'sub_offsets': meta['sub_offsets'], 'note': 'Material ID: 分区=子网格(材质槽), 对应 skim_XXX_N'}
    if '--legend' in sys.argv:
        json.dump(legend, open(sys.argv[sys.argv.index('--legend')+1], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('MATERIAL_ID DONE ->', out)

if __name__ == '__main__':
    main()
