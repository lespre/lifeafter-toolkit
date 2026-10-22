# -*- coding: utf-8 -*-
"""render_experimental_dxbc_pbr.py — 实验：DXBC 源公式渲染（独立路径，外审 v6 令 #5）

与正式/冻结路径完全隔离：只写入 --out 指定目录，不改动任何既有产物。

首版实现（仅外审"允许接入"清单）：
  · BaseColor = Tex0 (sRGB→Linear)
  · Metallic  = ParamMap.y（规范 RGBA 的 G 通道）= GBuffer SV_Target1.w
  · Roughness = ParamMap.x（诊断；源用途 = 环境立方体 LOD，见 DXBC [1499-1504]）
  · F0        = lerp(0.08, BaseColor, Metallic)        ← DXBC [357-358]
  · Diffuse   = BaseColor × (1 − Metallic)             ← DXBC [336-337]
  · SpecularIBL = F0 × env（**占位**：真实 env = 引擎 cubemap array / 材质自订 qiangpi.cube，本地不可得）
  · Normal    = NormalMap（R,G 通道；八面体编码 → 法线）
  · surfacemap.x / ParamMap.w → 诊断层（语义未赋名）
暂缓（按外审令）：粗糙度公式最终化、bit-pack 字段、env LOD、自发光/菲涅尔强度、C 族常量。

来源证据（指令行号）记录在 <out>/formula_source.json；shader_fidelity = partial。
用法: python render_experimental_dxbc_pbr.py <mesh> <texmap.json> <out_dir> [--eye X,Y,Z] [--roll deg] [--size WxH]
"""
import sys, os, json, math, time, hashlib
import numpy as np
from PIL import Image
import mesh_parse2 as MP
import raw_anchor as RA

ENV_PLACEHOLDER = (0.55, 0.60, 0.70)   # 占位环境色（非源；真实 = 引擎 cubemap array / 材质 cube）
FORMULA_SOURCE = {
    "BaseColor": "deferred\\pbr_weapon GBuffer PS: SV_Target1.xyz = Tex0.rgb",
    "Metallic": "同上 SV_Target1.w = ParamMap.y（采样 swizzle .ywxz → r3.x）",
    "Roughness(诊断)": "同上 SV_Target2.z = ParamMap.x；光照端 [1499] log r1.z → [1504] sample_l(cubearray) LOD",
    "F0": "deferred_dir_light_stencil PS [357] add r15.xyz, r0.xyzx, l(-0.079956) + [358] mad r15.xyz, r0.W, r15, 0.079956",
    "Diffuse": "同 PS [336] add r1.y, -r0.w, 1.0 + [337] mul r12.xyz, r0.xyzx, r1.yyyy",
    "SpecularIBL": "同 PS [1504] sample_l(texturecubearray t13, s0, LOD) × F0（env 为引擎 cubemap array，本地占位）",
    "surfacemap": "武器端 SV_Target3.y = t_surfacemap.x（规范 RGBA 的 R 通道）",
}
UNRESOLVED = ["粗糙度→LOD 公式最终化", "bit-pack 字段语义", "env 立方体阵列（占位）",
              "自发光/菲涅尔强度（shader 默认值未取）", "C 族三变体常量差异", "SV_Target0 消费方 pass"]


def srgb2lin(x):
    x = np.clip(x, 0.0, 1.0)
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)


def lin2srgb(x):
    x = np.clip(x, 0.0, 1.0)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * (x ** (1.0 / 2.4)) - 0.055)


def as_rgba(p):
    return np.asarray(Image.open(p).convert('RGBA'), np.float32) / 255.0


def samp(tex, u, v):
    tx = np.clip((np.remainder(u, 1.0) * (tex.shape[1] - 1)).astype(np.int32), 0, tex.shape[1] - 1)
    ty = np.clip((np.remainder(v, 1.0) * (tex.shape[0] - 1)).astype(np.int32), 0, tex.shape[0] - 1)
    return tex[ty, tx]


def sha_p(p):
    try:
        return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
    except Exception:
        return None


def smooth_welded(P, faces, tol=0.005):
    key = np.round(P / tol).astype(np.int64)
    uniq, inv = np.unique(key, axis=0, return_inverse=True)
    N = np.zeros((len(uniq), 3), np.float64)
    fn = np.cross(P[faces[:, 1]] - P[faces[:, 0]], P[faces[:, 2]] - P[faces[:, 0]])
    for k in range(3):
        np.add.at(N, inv[faces[:, k]], fn)
    ln = np.linalg.norm(N, axis=1, keepdims=True)
    return (N / np.maximum(ln, 1e-12))[inv].astype(np.float32)


def main():
    a = sys.argv[1:]
    mesh, texmap_p, out_dir = a[0], a[1], a[2]
    eye = tuple(float(x) for x in a[a.index('--eye') + 1].split(',')) if '--eye' in a else (-1.0, 0.0, 0.0)
    roll = float(a[a.index('--roll') + 1]) if '--roll' in a else 215.0
    W, H = ([int(x) for x in a[a.index('--size') + 1].split('x')] if '--size' in a else (1560, 1100))
    os.makedirs(out_dir, exist_ok=True)
    texmap = json.load(open(texmap_p, encoding='utf-8'))
    st = list(texmap['sets'].values())[0]

    P3, uv, faces, meta = MP.parse_mesh2(mesh)
    c = (P3.min(0) + P3.max(0)) / 2.0
    p = P3 - c
    e = np.array(eye, np.float32); e /= np.linalg.norm(e)
    up0 = np.array([0, 0, 1.0], np.float32)
    if abs(float(np.dot(up0, e))) > 0.9:
        up0 = np.array([0, 1.0, 0], np.float32)
    r0 = np.cross(up0, e); r0 /= np.linalg.norm(r0)
    u0 = np.cross(e, r0); u0 /= np.linalg.norm(u0)
    sx = p @ r0; sy = p @ u0; dep = p @ e
    t = math.radians(roll)
    Rr = np.array([[math.cos(t), -math.sin(t)], [math.sin(t), math.cos(t)]])
    s = Rr @ np.stack([sx, sy]); sxx, syy = s[0], s[1]
    Mg = 60
    sc = min((W - 2 * Mg) / (sxx.max() - sxx.min()), (H - 2 * Mg) / (syy.max() - syy.min()))
    cx = (sxx.max() + sxx.min()) / 2; cy = (syy.max() + syy.min()) / 2
    vx = (sxx - cx) * sc + W / 2; vy = H / 2 - (syy - cy) * sc; vd = dep.copy()

    Nsm = smooth_welded(P3, faces)
    f0, f1, f2 = faces[:, 0], faces[:, 1], faces[:, 2]
    dP1 = P3[f1] - P3[f0]; dP2 = P3[f2] - P3[f0]
    du1 = uv[f1] - uv[f0]; du2 = uv[f2] - uv[f0]
    det = du1[:, 0] * du2[:, 1] - du2[:, 0] * du1[:, 1]
    safe = np.abs(det) > 1e-12
    rr = np.where(safe, 1.0 / np.where(safe, det, 1.0), 0.0)
    Tf = (dP1 * du2[:, 1:2] - dP2 * du1[:, 1:2]) * rr[:, None]
    Bf = (dP2 * du1[:, 0:1] - dP1 * du2[:, 0:1]) * rr[:, None]
    Nf = (Nsm[f0] + Nsm[f1] + Nsm[f2]) / 3.0
    Nf /= np.maximum(np.linalg.norm(Nf, axis=1, keepdims=True), 1e-9)
    Tf = Tf - Nf * np.sum(Tf * Nf, axis=1, keepdims=True)
    tn = np.linalg.norm(Tf, axis=1, keepdims=True)
    Tf = np.where(tn > 1e-9, Tf / np.maximum(tn, 1e-9), np.array([1.0, 0, 0], np.float32))
    Bf = np.cross(Nf, Tf)

    submap = np.full((H, W), -1, np.int32)
    uvmap = np.zeros((H, W, 2), np.float32)
    nrmmap = np.zeros((H, W, 3), np.float32)
    fmap = np.full((H, W), -1, np.int32)
    zb = np.full((H, W), -1e9, np.float32)
    sub_of = np.zeros(len(P3), np.int32)
    for k, (a0, a1) in enumerate(meta['sub_offsets']):
        sub_of[a0:a1] = k
    for tri in np.argsort(vd[faces].mean(1)):
        fa, fb, fc = faces[tri]
        x0, y0 = vx[fa], vy[fa]; x1, y1 = vx[fb], vy[fb]; x2, y2 = vx[fc], vy[fc]
        minx = max(int(min(x0, x1, x2)), 0); maxx = min(int(max(x0, x1, x2)) + 1, W)
        miny = max(int(min(y0, y1, y2)), 0); maxy = min(int(max(y0, y1, y2)) + 1, H)
        if maxx <= minx or maxy <= miny:
            continue
        gx, gy = np.meshgrid(np.arange(minx, maxx) + 0.5, np.arange(miny, maxy) + 0.5)
        d0 = (x1 - x0) * (gy - y0) - (y1 - y0) * (gx - x0)
        d1 = (x2 - x1) * (gy - y1) - (y2 - y1) * (gx - x1)
        d2 = (x0 - x2) * (gy - y2) - (y0 - y2) * (gx - x2)
        m = ((d0 >= 0) & (d1 >= 0) & (d2 >= 0)) | ((d0 <= 0) & (d1 <= 0) & (d2 <= 0))
        if not m.any():
            continue
        area = d0 + d1 + d2
        w0 = d1 / area; w1 = d2 / area; w2 = d0 / area
        dd = w0 * vd[fa] + w1 * vd[fb] + w2 * vd[fc]
        sub = zb[miny:maxy, minx:maxx]; upd = m & (dd > sub)
        if not upd.any():
            continue
        uu = w0 * uv[fa, 0] + w1 * uv[fb, 0] + w2 * uv[fc, 0]
        vv = w0 * uv[fa, 1] + w1 * uv[fb, 1] + w2 * uv[fc, 1]
        nn = (w0[..., None] * Nsm[fa] + w1[..., None] * Nsm[fb] + w2[..., None] * Nsm[fc])
        nn /= np.maximum(np.linalg.norm(nn, axis=2, keepdims=True), 1e-6)
        submap[miny:maxy, minx:maxx][upd] = int(sub_of[fa])
        uvmap[miny:maxy, minx:maxx][upd] = np.stack([uu, vv], -1)[upd]
        nrmmap[miny:maxy, minx:maxx][upd] = nn[upd]
        fmap[miny:maxy, minx:maxx][upd] = tri
        sub[upd] = dd[upd]

    tex_T0 = srgb2lin(as_rgba(st['a'])[..., :3])     # Tex0（sRGB→线性）
    tex_N = as_rgba(st['n'])
    tex_PM = as_rgba(st['m'])
    tex_SM = as_rgba(st['s_m'])

    def blank():
        return np.zeros((H, W, 3), np.float32)

    L_base = blank(); L_F0 = blank(); L_diff = blank(); L_spec = blank()
    L_metal = np.zeros((H, W), np.float32); L_rough = np.zeros((H, W), np.float32)
    L_norm = blank(); L_sm = np.zeros((H, W), np.float32); L_pmw = np.zeros((H, W), np.float32)
    K = np.array([-0.72, -0.30, 0.62], np.float32); K /= np.linalg.norm(K)
    Vdir = -e
    env = np.array(ENV_PLACEHOLDER, np.float32)
    m = submap >= 0
    u = uvmap[m]
    base = samp(tex_T0, u[:, 0], u[:, 1])                  # 线性空间
    pm = samp(tex_PM, u[:, 0], u[:, 1])
    sm = samp(tex_SM, u[:, 0], u[:, 1])
    nrm = samp(tex_N, u[:, 0], u[:, 1])
    metal = pm[:, 1]                                       # ParamMap.y
    rough = pm[:, 0]                                       # ParamMap.x（诊断）
    F0 = 0.08 + (base - 0.08) * metal[:, None]             # lerp(0.08, BaseColor, Metallic)
    diff = base * (1.0 - metal)[:, None]                   # BaseColor × (1−Metallic)
    nx = nrm[:, 0] * 2 - 1; ny = nrm[:, 1] * 2 - 1
    nz = np.sqrt(np.clip(1 - nx * nx - ny * ny, 0, 1))
    # 世界法线：几何法线 + 法线贴图（R,G 通道，按逐像素面切线基展开）
    fs = fmap[m]
    gN = nrmmap[m]
    gN = gN / np.maximum(np.linalg.norm(gN, axis=1, keepdims=True), 1e-6)
    nw = Tf[fs] * nx[:, None] + Bf[fs] * ny[:, None] + gN * nz[:, None]
    nw /= np.maximum(np.linalg.norm(nw, axis=1, keepdims=True), 1e-6)
    nw = np.where(nz[:, None] > 0.999, gN, nw)   # nz≈1 时保持几何法线
    ndv = np.abs(np.sum(nw * Vdir[None, :], axis=1))
    ndl = np.maximum(np.sum(nw * K[None, :], axis=1), 0)
    fres = F0 + (1 - F0) * ((1 - ndv) ** 5)[:, None]
    spec_env = fres * env[None, :] * (0.5 + 0.5 * ndv[:, None]) * (0.6 + 0.4 * (1 - rough))[:, None]
    diff_lit = diff * (0.10 + 0.78 * ndl[:, None])         # 占位直接光（观察 rig 常数）
    comp = np.clip(diff_lit + spec_env, 0, 1)
    comp_img = np.zeros((H, W, 3), np.float32)
    comp_img[m] = comp   # 逐像素值散射回画布（此前把 (N,3) 直接存成 3xN 坏图）
    L_base[m] = np.clip(base, 0, 1)
    L_F0[m] = np.clip(F0, 0, 1)
    L_diff[m] = np.clip(diff_lit, 0, 1)
    L_spec[m] = np.clip(spec_env, 0, 1)
    L_metal[m] = np.clip(metal, 0, 1)
    L_rough[m] = np.clip(rough, 0, 1)
    L_norm[m] = nw * 0.5 + 0.5
    L_sm[m] = np.clip(sm[:, 0], 0, 1)
    L_pmw[m] = np.clip(pm[:, 3], 0, 1)

    def save3(name, arr, srgb=True):
        aa = lin2srgb(np.clip(arr, 0, 1)) if srgb else np.clip(arr, 0, 1)
        Image.fromarray((aa * 255).astype(np.uint8)).save(os.path.join(out_dir, name))

    def save1(name, arr):
        Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8)).save(os.path.join(out_dir, name))

    save3('BaseColor_linear.png', L_base)
    save1('Metallic.png', L_metal)
    save1('Roughness_diag.png', L_rough)
    save3('F0.png', L_F0)
    save3('Diffuse.png', L_diff)
    save3('SpecularIBL_placeholder.png', L_spec)
    save3('Normal.png', L_norm, srgb=False)
    save1('surfacemap_R.png', L_sm)
    save1('ParamMap_W.png', L_pmw)
    save3('Composite_noSFX.png', comp_img)

    checks = []
    for slot in ('a', 'n', 'm', 's_m'):
        src = (st.get('sources') or {}).get(slot)
        if src:
            checks.append(RA.verify_texture_vs_declared(st[slot], src))
    bad = [c['file'] for c in checks if c.get('match') is not True]
    json.dump(dict(generator='render_experimental_dxbc_pbr.py v1.0', time=time.strftime('%Y-%m-%d %H:%M:%S'),
                   mesh=os.path.abspath(mesh), mesh_sha=sha_p(mesh), texmap=os.path.abspath(texmap_p),
                   eye=list(eye), roll=roll, size=[W, H],
                   formula_source=FORMULA_SOURCE, unresolved=UNRESOLVED,
                   env_placeholder=ENV_PLACEHOLDER,
                   source_data_integrity=dict(pass_=(len(bad) == 0), checks=checks, reasons=(['贴图未通过锚定: ' + ','.join(bad)] if bad else [])),
                   shader_fidelity=dict(status='partial',
                                        reasons=['观察 rig 常数(占位直接光)', 'env = 占位(非引擎 cubemap array)',
                                                 '自发光/菲涅尔未接入', '粗糙度仅用于启发式高光宽度']),
                   isolation=dict(note='实验路径: 不改动冻结/正式产物; 与 v1.3 基线分开存放')),
              open(os.path.join(out_dir, 'formula_source.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('integrity=%s  ->' % (len(bad) == 0), out_dir)
    if bad:
        print('  未通过锚定:', bad)


if __name__ == '__main__':
    main()
