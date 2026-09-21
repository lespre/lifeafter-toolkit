# -*- coding: utf-8 -*-
"""render_material_layers.py — 源材质分层渲染器 v1.1 (skin_2003_029 试点)
输出: BaseColor / Normal / Gloss / Reflection / Refraction / Subsurface / Fresnel / Composite_noSFX + layers_trace.json

原则:
  · 颜色/强度参数全部来自 c159 自动解析(c159_pair.load_asset_materials), 参数各进其层, 不再混成一个 Tint;
  · 颜色空间: 基色贴图视为 sRGB → 线性化; 数据图(法线/AO/遮罩)原样; u_* 参数视为线性; 合成在线性空间 → 输出转回 sRGB;
  · 光照 = 文档化观察 rig (固定常数, 非源 IBL) → shader_fidelity=approximate, 全部常数写入 trace;
  · 4012 法线 = R,G 通道（**规范 RGBA**；2026-09-15 通道序修正，原 GB 为 BGRA 误读）; 4010 = 灰度细节图(R=G, B≈1) → 以高度梯度接入晶体子网格细节; 4013.**R** = 遮罩（旧称"光泽 B"已撤销，语义待 G-buffer 定案；极性由 --gloss-polarity 指定）.
  · --dual: 通用双持呈现层 (镜像成对组合同一网格: 左=180°旋转, 右=垂直翻转; 屏面基向量推导, 纯几何变换, 不改材质/参数).
用法:
  python render_material_layers.py <mesh> <tex_dir> <out_dir> [--materials <c159>] [--polarity smooth|rough|const] [--dual] [--dual-sep 0.62]
"""
import sys, os, json, math, time, hashlib
import numpy as np
from PIL import Image
import render_neox_mesh as R

# ---------- 观察 rig (固定常数, 全部记录进 trace) ----------
RIG = dict(
    key_dir=(-0.72, -0.30, 0.62), key_col=(1.0, 0.98, 0.94), key_int=0.78,
    fill_dir=(0.6, -0.2, -0.5), fill_col=(0.72, 0.78, 0.92), fill_int=0.22,
    ambient=0.10, env_col=(0.55, 0.60, 0.70), env_int=0.32,
    spec_str=0.50, spec_pow_lo=6.0, spec_pow_hi=150.0,
    sss_k=0.35, sss_k_crystal=0.55, crystal_diffuse=0.22,
    fres_k_default=0.70, bump_sens=6.0,
)

def srgb2lin(x):
    x = np.clip(x, 0.0, 1.0)
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)

def lin2srgb(x):
    x = np.clip(x, 0.0, 1.0)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * (x ** (1.0 / 2.4)) - 0.055)

def as_rgba(path):
    return np.asarray(Image.open(path).convert('RGBA'), np.float32) / 255.0

def samp(tex, u, v):
    tx = np.clip((u * (tex.shape[1] - 1)).astype(np.int32), 0, tex.shape[1] - 1)
    ty = np.clip((v * (tex.shape[0] - 1)).astype(np.int32), 0, tex.shape[0] - 1)
    return tex[ty, tx]

def sha_p(p):
    try: return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
    except Exception: return None

def main():
    args = sys.argv[1:]
    mesh = args[0]; tex_dir = args[1]; out_dir = args[2]
    mat_path = None
    if '--materials' in args:
        i = args.index('--materials'); mat_path = args[i + 1]
    polarity = 'smooth'
    if '--polarity' in args:
        i = args.index('--polarity'); polarity = args[i + 1]
    dual = '--dual' in args
    dual_sep = 0.62
    if '--dual-sep' in args:
        dual_sep = float(args[args.index('--dual-sep') + 1])
    dual_info = None
    W0, H0 = (2260, 1150) if dual else (1560, 1100)
    os.makedirs(out_dir, exist_ok=True)

    # ---------- 材质参数 ----------
    sub_params = {0: {}, 1: {}, 2: {}}
    mat_meta = None
    if mat_path:
        import c159_pair as CP
        mats, meta = CP.load_asset_materials(mat_path)
        for si, d in mats.items():
            sub_params[int(si)] = d.get('params') or {}
        mat_meta = dict(file=os.path.abspath(mat_path), bind=meta.get('bind_file'),
                        materials=meta.get('materials'), shaders=meta.get('shaders'))
    def P(si, name, dflt):
        v = sub_params.get(si, {}).get(name)
        if v is None: return dflt
        if isinstance(v, list): return tuple(float(x) for x in v[:3])
        return float(v)

    # ---------- 贴图 ----------
    T = {n: os.path.join(tex_dir, 'tex_%d.png' % n) for n in (4009, 4010, 4011, 4012, 4013)}
    _mp = os.path.join(tex_dir, '_input_manifest.json')
    if os.path.exists(_mp):
        # 通用输入清单: 槽位→实际文件名 (与 weapon_skin_pipeline.py 同一约定)
        _slots = (json.load(open(_mp, encoding='utf-8')).get('slots') or {})
        for _n in list(T.keys()):
            _fn = _slots.get(str(_n))
            if _fn: T[_n] = os.path.join(tex_dir, _fn)
    t11 = srgb2lin(as_rgba(T[4011])[..., :3]); t09 = srgb2lin(as_rgba(T[4009])[..., :3])
    t10 = as_rgba(T[4010]); t12 = as_rgba(T[4012]); t13 = as_rgba(T[4013])

    # ---------- 网格 + 投影 (与 render_neox_mesh 同一数学) ----------
    P3, uv, faces, meta = R.parse_mesh(mesh)
    if dual:
        # 屏面基向量 (roll 55° 的逆推: w_x=屏右, w_y=屏上), 纯几何镜像组合
        a_r = math.radians(55.0)
        e_d = np.array([1.0, 0.0, 0.0], np.float32)
        up_d = np.array([0, 0, 1.0], np.float32)
        r_d = np.cross(up_d, e_d); r_d /= np.linalg.norm(r_d)
        u_d = np.cross(e_d, r_d); u_d /= np.linalg.norm(u_d)
        w_x = (math.cos(a_r) * r_d - math.sin(a_r) * u_d).astype(np.float32)
        w_y = (math.sin(a_r) * r_d + math.cos(a_r) * u_d).astype(np.float32)
        c0d = (P3.min(0) + P3.max(0)) / 2.0
        Pc = P3 - c0d
        wg = float((Pc @ w_x).max() - (Pc @ w_x).min())
        P_L = Pc - 2 * np.outer(Pc @ w_x, w_x) - 2 * np.outer(Pc @ w_y, w_y)  # 左枪 = 180°旋转(两次翻转)
        P_R = Pc - 2 * np.outer(Pc @ w_y, w_y)                                # 右枪 = 垂直翻转(单次, 绕序反转)
        P_L = (P_L - w_x * (dual_sep * wg / 2)).astype(np.float32)
        P_R = (P_R + w_x * (dual_sep * wg / 2)).astype(np.float32)
        Nv = len(P3)
        f_R = faces[:, ::-1] + Nv
        P3 = np.concatenate([P_L, P_R]).astype(np.float32)
        uv = np.concatenate([uv, uv]).astype(np.float32)
        faces = np.concatenate([faces, f_R]).astype(np.int32)
        old_so = meta['sub_offsets']
        meta['sub_offsets'] = list(old_so) + [(a0 + Nv, a1 + Nv) for (a0, a1) in old_so]
        dual_info = dict(mode='mirror-pair', sep_frac=dual_sep, sep_world=round(dual_sep * wg, 4),
                         left='rot180(full-mirror)', right='flipV(winding-reversed)',
                         note='呈现层: 同一网格两实例; 材质/参数未改; 左/右枪色相分布=按源子网格材质')
    W, H = W0, H0
    c = (P3.min(0) + P3.max(0)) / 2.0; p = P3 - c
    e = np.array([1.0, 0.0, 0.0], np.float32); e /= np.linalg.norm(e)
    up0 = np.array([0, 0, 1.0], np.float32)
    if abs(np.dot(up0, e)) > 0.9: up0 = np.array([0, 1.0, 0], np.float32)
    r0 = np.cross(up0, e); r0 /= np.linalg.norm(r0)
    u0 = np.cross(e, r0); u0 /= np.linalg.norm(u0)
    sx = p @ r0; sy = p @ u0; dep = p @ e
    a = math.radians(55.0)
    Rr = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]], np.float32)
    s = Rr @ np.stack([sx, sy]); sxx, syy = s[0], s[1]
    spanx = sxx.max() - sxx.min(); spany = syy.max() - syy.min()
    Mg = 60
    sc = min((W - 2 * Mg) / max(spanx, 1e-6), (H - 2 * Mg) / max(spany, 1e-6))
    cx = (sxx.max() + sxx.min()) / 2; cy = (syy.max() + syy.min()) / 2
    vx = (sxx - cx) * sc + W / 2; vy = H / 2 - (syy - cy) * sc
    vd = dep.copy()

    Nsm = R.smooth_normals_welded(P3, faces)
    # 每面 TBN (向量化)
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
    # 退化面给默认帧
    Tf[~safe] = np.array([1.0, 0, 0]); Bf[~safe] = np.cross(Nf[~safe], Tf[~safe])

    # ---------- 光栅 (z-buffer, 存缓冲) ----------
    submap = np.full((H, W), -1, np.int32)
    uvmap = np.zeros((H, W, 2), np.float32)
    nrmmap = np.zeros((H, W, 3), np.float32)
    fmap = np.full((H, W), -1, np.int32)
    zb = np.full((H, W), -1e9, np.float32)
    sub_of = np.zeros(len(P3), np.int32)
    for k, (a0, a1) in enumerate(meta['sub_offsets']): sub_of[a0:a1] = k
    order = np.argsort(vd[faces].mean(1))
    for t in order:
        fa, fb, fc = faces[t]
        x0, y0 = vx[fa], vy[fa]; x1, y1 = vx[fb], vy[fb]; x2, y2 = vx[fc], vy[fc]
        minx = max(int(min(x0, x1, x2)), 0); maxx = min(int(max(x0, x1, x2)) + 1, W)
        miny = max(int(min(y0, y1, y2)), 0); maxy = min(int(max(y0, y1, y2)) + 1, H)
        if maxx <= minx or maxy <= miny: continue
        gx, gy = np.meshgrid(np.arange(minx, maxx) + 0.5, np.arange(miny, maxy) + 0.5)
        d0 = (x1 - x0) * (gy - y0) - (y1 - y0) * (gx - x0)
        d1 = (x2 - x1) * (gy - y1) - (y2 - y1) * (gx - x1)
        d2 = (x0 - x2) * (gy - y2) - (y0 - y2) * (gx - x2)
        m = ((d0 >= 0) & (d1 >= 0) & (d2 >= 0)) | ((d0 <= 0) & (d1 <= 0) & (d2 <= 0))
        if not m.any(): continue
        area = d0 + d1 + d2
        w0 = d1 / area; w1 = d2 / area; w2 = d0 / area
        dd = w0 * vd[fa] + w1 * vd[fb] + w2 * vd[fc]
        sub = zb[miny:maxy, minx:maxx]; upd = m & (dd > sub)
        if not upd.any(): continue
        uu = w0 * uv[fa, 0] + w1 * uv[fb, 0] + w2 * uv[fc, 0]
        vv = w0 * uv[fa, 1] + w1 * uv[fb, 1] + w2 * uv[fc, 1]
        nn = (w0[..., None] * Nsm[fa] + w1[..., None] * Nsm[fb] + w2[..., None] * Nsm[fc])
        nn /= np.maximum(np.linalg.norm(nn, axis=2, keepdims=True), 1e-6)
        si = int(sub_of[fa])
        submap[miny:maxy, minx:maxx][upd] = si
        uvmap[miny:maxy, minx:maxx][upd] = np.stack([uu, vv], -1)[upd]
        nrmmap[miny:maxy, minx:maxx][upd] = nn[upd]
        fmap[miny:maxy, minx:maxx][upd] = t
        sub[upd] = dd[upd]

    # ---------- 分层着色 (线性空间) ----------
    def blank(): return np.zeros((H, W, 3), np.float32)
    L_base = blank(); L_refl = blank(); L_refr = blank(); L_sss = blank(); L_fres = blank()
    L_diff = blank()
    L_gloss = np.zeros((H, W), np.float32); L_norm = np.zeros((H, W, 3), np.float32)
    model = submap >= 0
    K = np.array(RIG['key_dir'], np.float32); K /= np.linalg.norm(K)
    F = np.array(RIG['fill_dir'], np.float32); F /= np.linalg.norm(F)
    Vdir = -e
    u_vec = np.stack([uvmap[..., 0], uvmap[..., 1]], -1)
    for si in (0, 1, 2):
        m = submap == si
        if not m.any(): continue
        uvm = uvmap[m]; nm = nrmmap[m]; fidm = fmap[m]
        Tm = Tf[fidm]; Bm = Bf[fidm]; Nm = Nf[fidm]
        texb = t11 if si == 0 else t09
        base_srgb = samp(texb, uvm[:, 0], uvm[:, 1])[..., :3]
        base = srgb2lin(base_srgb) * np.array(P(si, 'u_base_color', (1.0, 1.0, 1.0)), np.float32)
        # 切线空间法线: 主法线 4012(R,G) —— 规范 RGBA
        chg = samp(t12, uvm[:, 0], uvm[:, 1])
        nx = (chg[:, 0] * 2 - 1) * 1.0
        ny = (chg[:, 1] * 2 - 1) * 1.0
        # 4010 灰度细节 → 高度梯度 bump (仅晶体子网格)
        # 规范 RGBA：灰度数据在 G 通道（004010: R≡0.995 常量, G≡B=0.678±0.195）；旧用下标 0 = BGRA 误读(取到常量)
        if si in (1, 2):
            S = RIG['bump_sens']; px = 1.6 / 1024.0
            h0 = samp(t10, uvm[:, 0], uvm[:, 1])[:, 1]
            hx = samp(t10, uvm[:, 0] + px, uvm[:, 1])[:, 1]
            hy = samp(t10, uvm[:, 0], uvm[:, 1] + px)[:, 1]
            nx = nx - (hx - h0) * S
            ny = ny - (hy - h0) * S
        d2 = nx * nx + ny * ny
        nz = np.sqrt(np.clip(1.0 - d2, 0.0, 1.0))
        nw = Tm * nx[:, None] + Bm * ny[:, None] + Nm * nz[:, None]
        nw /= np.maximum(np.linalg.norm(nw, axis=1, keepdims=True), 1e-6)
        L_norm[m] = nw * 0.5 + 0.5
        # 遮罩 (4013.R, 规范 RGBA) + 极性  —— 旧标注 (4013.B=光泽) 已撤销
        g = samp(t13, uvm[:, 0], uvm[:, 1])[:, 0]
        if polarity == 'rough': gloss = 1.0 - g
        elif polarity == 'const': gloss = np.full_like(g, 0.5)
        else: gloss = g
        L_gloss[m] = gloss
        # 视线/光
        ndv = np.abs(np.sum(nw * Vdir[None, :], axis=1))
        ndl_k = np.maximum(np.sum(nw * K[None, :], axis=1), 0)
        ndl_f = np.maximum(np.sum(nw * F[None, :], axis=1), 0)
        hv = (K + Vdir); hv /= np.linalg.norm(hv)
        ndh = np.maximum(np.sum(nw * hv[None, :], axis=1), 0)
        # 材质量
        metal = P(si, 'u_crystal_metallic', P(si, 'u_base_metallic', 1.0)) if si in (1, 2) else 1.0
        refl_tint = np.array(P(si, 'u_crystal_color', (1.0, 1.0, 1.0)), np.float32) if si in (1, 2) \
            else base  # 刀身: 金属 F0 = 基色
        F0 = np.clip(refl_tint, 0, 1) * metal + 0.04 * (1 - metal)
        fres = F0[None, :] + (1 - F0[None, :]) * ((1 - ndv) ** 5)[:, None]
        spec_pow = RIG['spec_pow_lo'] + (RIG['spec_pow_hi'] - RIG['spec_pow_lo']) * (gloss ** 2)
        spec = (ndh ** spec_pow) * RIG['spec_str']
        # Reflection 层: 环境 + 双灯高光
        env = np.array(RIG['env_col'], np.float32) * RIG['env_int']
        refl = fres * env[None, :] * (0.5 + 0.5 * ndv[:, None])
        refl += spec[:, None] * (np.array(RIG['key_col'], np.float32) * RIG['key_int'])[None, :]
        refl += ((ndh ** spec_pow) * 0.4)[:, None] * (np.array(RIG['fill_col'], np.float32) * RIG['fill_int'])[None, :]
        # Refraction 层
        refr_c = np.array(P(si, 'u_refraction_color', (0.0, 0.0, 0.0)), np.float32)
        refr_b = P(si, 'u_refraction_brightness', 0.0)
        refr_k = float(np.clip(refr_b / 5.0, 0.0, 1.0)) * 0.65
        refr = refr_c[None, :] * (refr_k * (0.45 + 0.55 * ndv))[:, None]
        # Subsurface 层
        sss_c = np.array(P(si, 'u_subsurface_color', (0.0, 0.0, 0.0)), np.float32)
        sss_kx = RIG['sss_k'] if si == 0 else RIG['sss_k_crystal']
        sss = sss_c[None, :] * (sss_kx * (0.35 + 0.65 * ndl_k))[:, None]
        # Fresnel 层
        fk = P(si, 'u_emissive_fresnel', RIG['fres_k_default'])
        fs = P(si, 'u_emissive_strength', 1.0) if 'u_emissive_strength' in sub_params.get(si, {}) else 0.5
        fres_term = fk * (0.5 + 0.5 * float(np.clip(fs / 2.0, 0, 1))) * ((1 - ndv) ** 3)
        # Diffuse (观察补偿项)
        kd = 1.0 if si == 0 else RIG['crystal_diffuse']
        diff = base * kd * (RIG['ambient'] + RIG['key_int'] * ndl_k[:, None] * np.array(RIG['key_col'], np.float32)[None, :]
                            + RIG['fill_int'] * 0.6 * ndl_f[:, None] * np.array(RIG['fill_col'], np.float32)[None, :])
        # 写入各层
        L_base[m] = np.clip(base, 0, 1)
        L_diff[m] = np.clip(diff, 0, None)
        L_refl[m] = np.clip(refl, 0, None)
        L_refr[m] = np.clip(refr, 0, None)
        L_sss[m] = np.clip(sss, 0, None)
        L_fres[m] = np.clip(fres_term[:, None] * np.array([1.0, 1.0, 1.0], np.float32)[None, :], 0, None)
    # 合成 = 漫反射 + 反射 + 折射 + 次表面 + 菲涅尔 (线性空间逐像素相加)
    comp = np.clip(L_diff + L_refl + L_refr + L_sss + L_fres, 0, 1)

    # ---------- 保存 ----------
    def save3(name, arr, srgb=True):
        a = lin2srgb(np.clip(arr, 0, 1)) if srgb else np.clip(arr, 0, 1)
        Image.fromarray((a * 255).astype(np.uint8)).save(os.path.join(out_dir, name))
    save3('BaseColor.png', L_base, srgb=True)
    save3('Normal.png', L_norm, srgb=False)
    Image.fromarray((np.clip(L_gloss, 0, 1) * 255).astype(np.uint8)).save(os.path.join(out_dir, 'Gloss.png'))
    save3('Reflection.png', L_refl, srgb=True)
    save3('Refraction.png', L_refr, srgb=True)
    save3('Subsurface.png', L_sss, srgb=True)
    save3('Fresnel.png', L_fres, srgb=True)
    save3('Composite_noSFX.png', comp, srgb=True)

    trace = dict(
        generator='render_material_layers.py v1.1 (+--dual)', time=time.strftime('%Y-%m-%d %H:%M:%S'),
        mesh=os.path.abspath(mesh), mesh_sha=sha_p(mesh),
        materials=mat_meta or '(未提供 --materials, 使用默认参数)',
        textures={str(n): dict(path=T[n], sha=sha_p(T[n])) for n in T},
        polarity=polarity, rig=RIG, dual=dual_info,
        sub_params={str(k): v for k, v in sub_params.items()},
        channels=dict(normal_main='4012 通道 R,G (规范RGBA; 原GB=BGRA误读)',
                      crystal_detail='4010 G 通道灰度(梯度 bump; 规范RGBA; 旧"R=G"为BGRA误读)',
                      mask='4013.R 极性=%s (旧称 4013.B=光泽, 已撤销)' % polarity),
        color_space='基色 sRGB→线性; 参数线性; 合成线性→sRGB 输出',
        approximations=['观察 rig=固定常数(非源 IBL)', '层强度常数(sss_k/spec_str/refr 系数)=文档化常数', 'Sub0 无 c159 覆写=默认参数', '4010 接入方式=高度梯度 bump(编码定案为灰度细节)'],
        coverage={k: int((submap == k).sum()) for k in (0, 1, 2)},
        layer_mean={k: float(v[model].mean()) if model.any() else 0.0 for k, v in
                    dict(Base=L_base, Reflection=L_refl, Refraction=L_refr, Subsurface=L_sss, Fresnel=L_fres).items()},
    )
    json.dump(trace, open(os.path.join(out_dir, 'layers_trace.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('LAYERS DONE ->', out_dir)
    for f in ('BaseColor', 'Normal', 'Gloss', 'Reflection', 'Refraction', 'Subsurface', 'Fresnel', 'Composite_noSFX'):
        print(' ', f + '.png')

if __name__ == '__main__':
    main()
