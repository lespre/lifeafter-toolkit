# -*- coding: utf-8 -*-
"""斜坡法线正负光验证 (外审 v7 令 第4项)
目的: 不依赖参考图, 用方向明确的合成斜坡法线图 + 左右/上下灯光, 验证:
  1) shader 公式 (02ac9f54 反汇编: n = normalize(T*x + B*y + N); saturate(N·L)) 的单侧光方向正确;
  2) 渲染器 (render_neox_mesh: |N·L| 双侧近似) 的符号响应, 并显式记录其 ±不可分辨性.
输出: _normal_ramp_test/ (对比图 + 判定 JSON)
"""
import os, sys, json
import numpy as np
from PIL import Image

W = H = 512
yy, xx = np.mgrid[0:H, 0:W]
u = xx / (W - 1.0); v = yy / (H - 1.0)

# 合成平面: 面向观察者, N=+Z, T 沿 +u(=+X), B 沿 +v(=+Y)
N = np.zeros((H, W, 3), np.float32); N[..., 2] = 1.0
T = np.zeros((H, W, 3), np.float32); T[..., 0] = 1.0
B = np.zeros((H, W, 3), np.float32); B[..., 1] = 1.0

ramp_x = np.clip(u * 2 - 1, -1, 1)   # -1(左) → +1(右)
ramp_y = np.clip(v * 2 - 1, -1, 1)   # -1(上) → +1(下)

def nrm(nm_xy):
    x = nm_xy[..., 0]; y = nm_xy[..., 1]
    nz = np.sqrt(np.clip(1 - x * x - y * y, 0, 1))
    nw = T * x[..., None] + B * y[..., None] + N * nz[..., None]
    return nw / np.maximum(np.linalg.norm(nw, axis=2, keepdims=True), 1e-6)

def shade_shader(nm_xy, L):   # shader: saturate(N·L) 单侧
    return np.clip(np.sum(nrm(nm_xy) * np.array(L, np.float32), axis=2), 0, 1)

def shade_renderer(nm_xy, L): # 渲染器: |N·L| 双侧近似
    return np.clip(np.abs(np.sum(nrm(nm_xy) * np.array(L, np.float32), axis=2)), 0, 1)

def half_means(img):
    l = float(img[:, :W // 2].mean()); r = float(img[:, W // 2:].mean())
    t = float(img[:H // 2].mean()); b = float(img[H // 2:].mean())
    return dict(left=round(l, 4), right=round(r, 4), top=round(t, 4), bottom=round(b, 4))

res = {}
sheet = np.zeros((H * 2, W * 2, 3), np.float32)

nmx = np.stack([ramp_x, np.zeros_like(ramp_x)], -1)
nmy = np.stack([np.zeros_like(ramp_y), ramp_y], -1)

# —— shader 单侧光: 方向必须跟随光源 ——
xl = shade_shader(nmx, (-1, 0, 0.25)); xr = shade_shader(nmx, (1, 0, 0.25))
yt = shade_shader(nmy, (0, 1, 0.25)); yb = shade_shader(nmy, (0, -1, 0.25))
hx_l, hx_r, hy_t, hy_b = half_means(xl), half_means(xr), half_means(yt), half_means(yb)
res['shader_single_sided'] = dict(
    nx_light_left=hx_l, nx_light_right=hx_r,
    nx_expect='左光→左半亮(right<left); 右光→右半亮(left<right)',
    nx_pass=bool(hx_l['left'] > hx_l['right'] and hx_r['right'] > hx_r['left']),
    ny_light_down=hy_t, ny_light_up=hy_b,
    ny_expect='光在下方(y+)→下半亮; 光在上方(y-)→上半亮',
    ny_pass=bool(hy_t['bottom'] > hy_t['top'] and hy_b['top'] > hy_b['bottom']))
# —— 渲染器双侧近似: 记录 ±光源不可分辨 ——
axl = shade_renderer(nmx, (-1, 0, 0.25)); axr = shade_renderer(nmx, (1, 0, 0.25))
diff = float(np.abs(axl - axr).max())
axl0 = shade_renderer(nmx, (-1, 0, 0.0)); axr0 = shade_renderer(nmx, (1, 0, 0.0))
diff0 = float(np.abs(axl0 - axr0).max())
res['renderer_two_sided'] = dict(
    note='render_neox_mesh 用 |N·L| (双侧): 纯轴 ±光互换时响应完全对称(翻转不可证); 带 z 分量时 |−x+cz| ≠ |x+cz|, 略有差异. 属已知近似, 记录在案',
    max_abs_diff_light_swap_with_z=round(diff, 6),
    max_abs_diff_light_swap_pure_axis=round(diff0, 8))
res['all_pass'] = bool(res['shader_single_sided']['nx_pass'] and res['shader_single_sided']['ny_pass'])

sheet[0:H, 0:W] = np.stack([xl] * 3, -1); sheet[0:H, W:] = np.stack([xr] * 3, -1)
sheet[H:, 0:W] = np.stack([yt] * 3, -1); sheet[H:, W:] = np.stack([yb] * 3, -1)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_normal_ramp_test')
os.makedirs(out, exist_ok=True)
Image.fromarray((np.clip(sheet, 0, 1) * 255).astype(np.uint8)).save(os.path.join(out, 'ramp_sheet.png'))
with open(os.path.join(out, 'verdict.json'), 'w', encoding='utf-8') as f:
    json.dump(dict(
        test='斜坡法线正负光验证',
        formula='n = normalize(T*x + B*y + N); NM=(R*2-1, G*2-1) 不翻转G',
        source='shader 02ac9f54 VS/PS 反汇编 (v0=POSITION v1=NORMAL v2=UV v3=TANGENT; w=(|T|^2>1.5)?+1:-1)',
        panels='左上=左光 右上=右光 (nx 斜坡) / 左下=下光 右下=上光 (ny 斜坡)',
        results=res), f, ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1))
print('sheet ->', os.path.join(out, 'ramp_sheet.png'))
