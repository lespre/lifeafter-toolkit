# -*- coding: utf-8 -*-
"""weapon_skin_pipeline.py — 武器皮肤"一条命令出图"管线 v1.0
将极光剑(029)逐轮校准沉淀为可复用规则：
  渲染层: 子网格角色分配 / 焊接平滑法线 / 金属光照参数
  后期层: R1银蓝刃片带 · R2护手-剑身过渡区 · R3金色规整(暖浅金+金褐暗部)
          R4护手细碎冷光 · R5宝石高光 · R6圆孔内衬(自动检测) · R7冷调阴影
  质检层: QC1连接处色差 QC2刃带均匀性 QC3材质分区 QC4洞内衬 —— 输出 qc.json + QC_REPORT.md
用法:
  python weapon_skin_pipeline.py <mesh路径> <贴图目录> <输出目录> [--profile jiguangjian]
  python weapon_skin_pipeline.py --qc-only <已渲染png> <mesh路径> <输出目录>
贴图约定(文件名): tex_4011.png(基色) tex_4012.png(法线) tex_4013.png(发光)
                  tex_4009.png(护手银蓝源) tex_4011_v19.png(清理版基色,可选)
逐皮肤参数: SKIN_PROFILES 字典(可选覆盖), 未给则用默认规则。
"""
import sys, json, math, os, time, hashlib
import numpy as np
from PIL import Image, ImageDraw
import scipy.ndimage as ndi

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_neox_mesh as R

# ============ 校准参数(029 实证, 通用默认) ============
PARAMS = dict(
    roll_deg=50.0,
    bg_top=(19, 37, 39), bg_bot=(11, 17, 19),
    spec_str=0.78, spec_pow=48, spec2_str=0.15,
    glow=0.34, bloom=0.13, ambient=0.115, diffuse=0.80,
    edgek=0.68, edgecol=(0.78,0.87,1.00), edge_pow=1.6,
    edge_sheen_k=0.55, edge_sheen_mu=0.52, edge_sheen_sigma=0.22,
    nl_pow=1.50, base_gamma=1.12, knee=0.70, knee_k=2.8, envk=0.26,
    nrm_str=1.40,
    # R1 刃片带
    band_plateau=10.0, band_wmax_base=26.0, band_wmax_var=10.0,
    band_tip_boost=0.55, band_tip_radius=190.0, band_tip_widen=0.35,
    band_wsil=0.90, band_wwh=0.98,
    band_wmax_blur=0.7, band_wsil_blur=1.5,
    band_col_sil=(0.72, 0.77, 0.91), band_col_wh=(0.87, 0.90, 0.96),
    band_halo=(0.10, 0.105, 0.12), band_halo_blur=9,
    band_rough_var=(8.0, 0.12),          # (噪声尺度, 幅度) 粗糙度变化感
    edge_mode='fresnel',                 # 'fresnel'=源逻辑(几何耦合菲涅尔刃口光) | 'band'=旧屏幕距离带
    source_mode=False,                   # True = 源材质模式: 绕过 post_process 全部规则(R2-R7), 走未修改源贴图
    junction_normals=dict(on=True, z=(6.2, 7.2), eps=0.12, blend=0.5),  # 跨缝法线调和(材质/法线断层修复)
    # R2 过渡区
    root_fade_len=2.2, seam_shade=0.15, seam_blur=4.0,
    junction_luma_clamp=(0.85, 1.35),
    # R3 金色规整
    gold_r=0.06, gold_g=-0.030, gold_b=-0.015,
    gold_dark_lum=0.52, gold_dark_mul=(1.02, 0.93, 0.86),
    gold_hot_lum=0.72, gold_hot_mul=0.05,
    # R4 护手
    guard_noise_amp=0.09, guard_noise_scale=2.2, guard_cool=0.035,
    # R5 宝石
    gem_min_px=60, gem_hl=0.55,
    # R6 圆孔内衬
    hole_inner=(0.24, 0.15, 0.06), hole_outer=(0.60, 0.43, 0.20),
    hole_rim=(0.50, 0.40, 0.22), hole_occ=0.35,
    # R7 冷调阴影
    cool_amp=1.2, cool_rgb=(0.96, 0.99, 1.04),
    # 杂项
    cool_shadow=dict(lum=0.45, amp=1.2, rgb=(0.96, 0.99, 1.04)),
)

SKIN_PROFILES = {
    # 极光剑: 手柄面(z 9.6-11.6提亮) + 尖晶(z 0.85-1.55, y>0.76面部涂银)
    'jiguangjian': dict(
        grip_z=(9.6, 11.6), grip_rgb=(0.91, 0.88, 0.81), grip_blend=0.66,
        spike=dict(ymax=0.76, ymean=0.35, z=(0.85, 1.55), rgb=(0.91, 0.94, 0.99), blend=0.92),
        tex={4009: 'tex_4009.png', 4011: 'tex_4011.png', 4012: 'tex_4012.png', 4013: 'tex_4013.png'},
    ),
}

def _mk_silver(base_rgba):
    """R0: 护手银蓝材质(从 4009 源派生)"""
    a = base_rgba[..., :3] * 255.0
    g = a.mean(2, keepdims=True)
    s = a * 0.47 + g * 0.53
    s[..., 0] *= 0.93; s[..., 1] *= 0.99; s[..., 2] *= 1.09
    s = np.clip(s * 1.05, 0, 255).astype(np.uint8)
    return s

def _load(p):
    return np.asarray(Image.open(p).convert('RGBA')).astype(np.float32) / 255.0

def harmonize_junction_normals(P, idx, meta, zlo=6.2, zhi=7.2, eps=0.12, blend=0.5):
    """跨缝法线调和: 相接的不同子网格在交叠带内互相平均法线, 消除受光接缝。
    返回 (N接正后的逐顶点法线, 统计dict)。"""
    from scipy.spatial import cKDTree
    Nsm = R.smooth_normals_welded(P, idx).copy()
    sub_off = meta['sub_offsets']
    z = P[:, 2]
    def verts_of(sub_i):
        a0, a1 = sub_off[sub_i]
        v = np.zeros(len(P), bool); v[a0:a1] = True
        return v & (z > zlo) & (z < zhi)
    A = np.where(verts_of(0))[0]; Bb = np.where(verts_of(1))[0]
    stats = dict(zone=(zlo, zhi), eps=eps, blend=blend, n_sub0=len(A), n_sub1=len(Bb), n_fixed=0)
    if len(A) and len(Bb):
        trB = cKDTree(P[Bb]); trA = cKDTree(P[A])
        ang0 = []
        for a in A:
            d, i = trB.query(P[a])
            if d < eps:
                v0, v1 = Nsm[a], Nsm[Bb[i]]
                ang0.append(math.degrees(math.acos(np.clip(np.dot(v0, v1), -1, 1))))
        if ang0:
            stats['cross_angle_before_deg'] = round(float(np.mean(ang0)), 1)
        for a in A:
            d, i = trB.query(P[a])
            if d < eps:
                nw = Nsm[a] + blend * Nsm[Bb[i]]
                Nsm[a] = nw / max(np.linalg.norm(nw), 1e-9); stats['n_fixed'] += 1
        for b in Bb:
            d, i = trA.query(P[b])
            if d < eps:
                nw = Nsm[b] + blend * Nsm[A[i]]
                Nsm[b] = nw / max(np.linalg.norm(nw), 1e-9); stats['n_fixed'] += 1
        ang1 = []
        for a in A:
            d, i = trB.query(P[a])
            if d < eps:
                v0, v1 = Nsm[a], Nsm[Bb[i]]
                ang1.append(math.degrees(math.acos(np.clip(np.dot(v0, v1), -1, 1))))
        if ang1:
            stats['cross_angle_after_deg'] = round(float(np.mean(ang1)), 1)
    return Nsm, stats

def build_masks(P, idx, meta, W2, H2, Rr, ccx, ccy, scv, c):
    zc = P[idx, 2].mean(1)
    def fwd(y, z):
        pp = np.array([y, z]) - c[1:3]
        sw = Rr @ pp
        return (sw[0] - ccx) * scv + W2 / 2, H2 / 2 - (sw[1] - ccy) * scv
    def rast(sel, vals=None):
        m = np.zeros((H2, W2), np.float32)
        sfaces = idx[np.asarray(sel)]
        vvals = None if vals is None else np.asarray(vals)[np.asarray(sel)]
        for k in range(len(sfaces)):
            f = sfaces[k]; fa, fb, fc = int(f[0]), int(f[1]), int(f[2])
            x0, y0 = fwd(P[fa, 1], P[fa, 2]); x1, y1 = fwd(P[fb, 1], P[fb, 2]); x2, y2 = fwd(P[fc, 1], P[fc, 2])
            minx = max(int(min(x0, x1, x2)), 0); maxx = min(int(max(x0, x1, x2)) + 2, W2)
            miny = max(int(min(y0, y1, y2)), 0); maxy = min(int(max(y0, y1, y2)) + 2, H2)
            if maxx <= minx or maxy <= miny: continue
            gx, gy = np.meshgrid(np.arange(minx, maxx) + 0.5, np.arange(miny, maxy) + 0.5)
            d0 = (x1 - x0) * (gy - y0) - (y1 - y0) * (gx - x0)
            d1 = (x2 - x1) * (gy - y1) - (y2 - y1) * (gx - x1)
            d2 = (x0 - x2) * (gy - y2) - (y0 - y2) * (gx - x2)
            mm = ((d0 >= 0) & (d1 >= 0) & (d2 >= 0)) | ((d0 <= 0) & (d1 <= 0) & (d2 <= 0))
            if not mm.any(): continue
            v = 1.0 if vvals is None else float(vvals[k])
            mw = m[miny:maxy, minx:maxx]
            mw[mm] = np.maximum(mw[mm], v)
        return m
    return zc, fwd, rast

def post_process(img, P, idx, meta, zc, fwd, rast, W2, H2, Params, profile=None, apply_rules=True):
    profile = profile or {}
    tt = np.linspace(0, 1, H2)[:, None, None]
    bgc = ((1 - tt) * np.array(Params['bg_top'], np.float32) + tt * np.array(Params['bg_bot'], np.float32)) / 255.0
    sil = np.abs(img - bgc).sum(2) > 0.10
    blade_m = rast(zc < 6.3) > 0
    Bmask = rast((idx[:, 0] >= meta['sub_offsets'][1][0]) & (idx[:, 2] < meta['sub_offsets'][1][1])) > 0
    S2 = rast((idx[:, 0] >= meta['sub_offsets'][2][0]) & (idx[:, 2] < meta['sub_offsets'][2][1])) > 0
    B = blade_m & sil
    D = ndi.distance_transform_edt(B)
    gDy, gDx = np.gradient(D)
    nrmL = np.sqrt(gDx ** 2 + gDy ** 2); nrmL[nrmL == 0] = 1
    nOx = -gDx / nrmL; nOy = -gDy / nrmL
    fac = 0.75 + 0.25 * np.clip(nOx * 0.5 + nOy * 0.65, 0, 1)
    rng = np.random.RandomState(7)
    n1 = ndi.gaussian_filter(rng.rand(H2, W2).astype(np.float32), 55); n1 = (n1 - n1.min()) / (n1.max() - n1.min() + 1e-9)
    n2 = ndi.gaussian_filter(rng.rand(H2, W2).astype(np.float32), 26); n2 = (n2 - n2.min()) / (n2.max() - n2.min() + 1e-9)
    yy, xx = np.mgrid[0:H2, 0:W2]
    ytip = P[:, 2].argmin(); xtip, ytip_px = fwd(P[ytip, 1], P[ytip, 2])
    dtip = np.sqrt((xx - xtip) ** 2 + (yy - ytip_px) ** 2)
    tipboost = np.clip(1 - dtip / Params['band_tip_radius'], 0, 1)
    fac = np.minimum(1.0, fac * (1 + tipboost * Params['band_tip_boost'])) * np.clip(0.80 + 0.16 * n1 + 0.14 * n2, 0.76, 1.10)
    # R1 银蓝刃片带
    Dmod = D / np.maximum(1.0 + Params['band_tip_widen'] * tipboost, 1e-6)
    Wmax = Params['band_wmax_base'] + Params['band_wmax_var'] * n2
    wsil = np.clip((Wmax - Dmod) / np.maximum(Wmax - Params['band_plateau'], 4), 0, 1) * Params['band_wsil'] * fac
    wwh = np.clip((5.5 - Dmod) / 3.0, 0, 1) * Params['band_wwh'] * fac
    rv = np.clip((6.3 - zc) / Params['root_fade_len'], 0, 1)
    rootfade = ndi.gaussian_filter(rast(zc < 6.3, vals=rv), 3.0)
    wsil = wsil * rootfade; wwh = wwh * rootfade
    for arr in (wsil, wwh): arr[~B] = 0
    maskb = ndi.gaussian_filter(B.astype(np.float32), 2.2)
    wsils = ndi.gaussian_filter(wsil, Params['band_wsil_blur']) * maskb
    wwhs = ndi.gaussian_filter(wwh, Params['band_wmax_blur']) * maskb
    # R1b 粗糙度变化感: 中频噪声调制带亮度
    sc, amp = Params['band_rough_var']
    n3 = ndi.gaussian_filter(rng.rand(H2, W2).astype(np.float32), sc); n3 = (n3 - n3.min()) / (n3.max() - n3.min() + 1e-9)
    roughmod = 1.0 + (n3 - 0.5) * 2 * amp
    wsils = np.clip(wsils * roughmod, 0, 1)
    halo = ndi.gaussian_filter(np.clip(wsils * 1.3, 0, 1), Params['band_halo_blur'])
    if Params.get('edge_mode', 'band') == 'fresnel':
        # 源逻辑模式: 不叠加屏幕空间刃带; 刃口光由渲染层 edgek/edge_pow(几何耦合菲涅尔)承担
        wsils = np.zeros_like(wsils); wwhs = np.zeros_like(wwhs); halo = np.zeros_like(halo)
    o = img * (1 - wsils[..., None]) + np.array(Params['band_col_sil'], np.float32)[None, None, :] * wsils[..., None]
    o = o * (1 - wwhs[..., None]) + np.array(Params['band_col_wh'], np.float32)[None, None, :] * wwhs[..., None]
    o = o + halo[..., None] * np.array(Params['band_halo'], np.float32)[None, None, :]
    o = np.clip(o, 0, 1)
    sz = (wsils > 0.45)
    o[..., 2] = np.clip(o[..., 2] * (1 + 0.03 * sz), 0, 1)
    # R2 过渡区: 根部亮度匹配护手 + 接缝轻阴影
    guard_l = float((img[Bmask & sil]).mean()) if (Bmask & sil).any() else 0.5
    rootzone = rast((zc > 4.4) & (zc < 6.3))
    bz = (img[(rootzone > 0) & sil].mean()) if ((rootzone > 0) & sil).any() else guard_l
    gain = float(np.clip(guard_l / max(bz, 1e-3), *Params['junction_luma_clamp']))
    rampz = np.clip(rast(zc < 6.3, vals=np.clip((6.3 - zc) / Params['root_fade_len'] + 0.35, 0, 1)), 0, 1)
    rampz = ndi.gaussian_filter(rampz, 2.5) * (1 - (wsils > 0.5))
    o = o * (1 + (gain - 1) * rampz[..., None] * 0.85)
    seam = rast((zc > 5.9) & (zc < 7.2))
    seam = ndi.gaussian_filter(seam, Params['seam_blur']) * 0.35
    o = o * (1 - seam[..., None] * Params['seam_shade'])
    o = np.clip(o, 0, 1)
    # R4 护手细碎冷光
    Bm = Bmask.astype(np.float32)
    gn = ndi.gaussian_filter(rng.rand(H2, W2).astype(np.float32), Params['guard_noise_scale'])
    gn = (gn - 0.5) * Params['guard_noise_amp']
    o[..., 0] = np.clip(o[..., 0] * (1 + gn * Bm), 0, 1)
    o[..., 1] = np.clip(o[..., 1] * (1 + gn * 0.7 * Bm), 0, 1)
    o[..., 2] = np.clip(o[..., 2] * (1 + Params['guard_cool'] * Bm), 0, 1)
    # R3 金色规整
    gold = ((o[..., 0] > o[..., 1] - 0.015) & (o[..., 1] > o[..., 2] + 0.03) & (o[..., 0] > 0.30)).astype(np.float32)
    gold = gold * (1 - sz * 0.9)
    o2 = o.copy()
    o2[..., 0] = np.clip(o[..., 0] * (1 + Params['gold_r'] * gold), 0, 1)
    o2[..., 1] = np.clip(o[..., 1] * (1 + Params['gold_g'] * gold), 0, 1)
    o2[..., 2] = np.clip(o[..., 2] * (1 + Params['gold_b'] * gold), 0, 1)
    lum = o2.mean(2)
    darkg = (gold > 0.5) & (lum < Params['gold_dark_lum'])
    o2 = np.where(darkg[..., None], o2 * np.array(Params['gold_dark_mul'], np.float32)[None, None, :], o2)
    hot = (gold > 0.5) & (lum > Params['gold_hot_lum'])
    o2 = np.clip(o2 * (1 + Params['gold_hot_mul'] * hot[..., None]), 0, 1)
    o = o2
    # R7 冷调阴影
    lum = o.mean(2); cw = np.clip(0.45 - lum, 0, 1) * Params['cool_amp']
    o = o * (1 - cw[..., None]) + o * np.array(Params['cool_rgb'], np.float32)[None, None, :] * cw[..., None]
    o = np.clip(o, 0, 1)
    # R5 宝石高光
    lab, nn = ndi.label(S2)
    gems = []
    for i in range(1, nn + 1):
        ys2, xs2 = np.where(lab == i)
        if len(xs2) < Params['gem_min_px']: continue
        gx0, gy0 = xs2.mean(), ys2.mean()
        rad = min(9.0, np.sqrt(len(xs2)) / 3.2)
        dd = np.sqrt((xx - gx0) ** 2 + (yy - gy0) ** 2)
        hl = np.clip(1 - dd / max(rad, 3), 0, 1) ** 1.6 * Params['gem_hl']
        hl = hl * (1 - np.clip((yy - gy0 + rad * 0.2) / (rad * 1.2), 0, 1) * 0.6)
        o = o + hl[..., None] * np.array([1.0, 0.75, 0.75], np.float32)[None, None, :]
        gems.append((float(gx0), float(gy0), int(len(xs2))))
    o = np.clip(o, 0, 1)
    # R6 圆孔内衬(自动检测: 外形内部被填充出来的背景色区域)
    sword = sil
    filled = ndi.binary_fill_holes(sword)
    holes = filled & ~sword
    labh, nh = ndi.label(holes)
    hole_info = []
    for i in range(1, nh + 1):
        ys2, xs2 = np.where(labh == i)
        if len(xs2) < 120: continue
        hx, hy = xs2.mean(), ys2.mean()
        dh = np.sqrt((xx - hx) ** 2 + (yy - hy) ** 2)
        rH = np.sqrt(len(xs2) / math.pi)
        hole2d = np.clip(1 - (dh - (rH - 5)) / 10, 0, 1) * ((np.abs(img - bgc).sum(2) < 0.10))
        rad = np.clip((dh - 6) / max(rH - 6, 6), 0, 1)
        col = (np.array(Params['hole_inner'], np.float32)[None, None, :] * (1 - rad[..., None])
               + np.array(Params['hole_outer'], np.float32)[None, None, :] * rad[..., None])
        shad = np.clip((-(xx - hx) * 0.35 + (yy - hy) * 0.85) / max(rH, 6), -1, 1)
        col = col * np.clip(0.62 + 0.42 * (shad * 0.5 + 0.5), 0.5, 1.15)[..., None]
        rimhl = np.clip(1 - np.abs(dh - (rH - 4)) / 10, 0, 1) * np.clip((shad - 0.35), 0, 1) / 0.65 * 0.85
        col = col + np.array(Params['hole_rim'], np.float32)[None, None, :] * rimhl[..., None]
        occ = np.clip(1 - np.abs(dh - (rH + 5)) / 7, 0, 1) * Params['hole_occ']
        col = col * (1 - occ[..., None]); col = np.clip(col, 0, 1)
        ho = hole2d[..., None]
        o = o * (1 - ho) + col * ho
        hole_info.append((float(hx), float(hy), float(rH)))
        o = np.clip(o, 0, 1)
    ctx = dict(blade_m=blade_m, Bmask=Bmask, S2=S2, B=B, sil=sil, bgc=bgc, wsils=wsils,
               gems=gems, holes=hole_info, zc=zc, rast=rast, fwd=fwd, nOx=nOx, nOy=nOy)
    if not apply_rules:
        o = img.copy()  # source 模式: 输出=未后处理的源渲染图, 质检照常计算
    return o, ctx

# ============ 自动质检 ============
SOURCE_TEX_WHITELIST = {'tex_4009.png', 'tex_4010.png', 'tex_4011.png', 'tex_4012.png', 'tex_4013.png'}

def load_input_manifest(tex_dir):
    """可选输入清单 <tex_dir>/_input_manifest.json (通用, 非资产特例):
    {"slots":   {"4011": "tex_4011.png", ...},            # 槽位→实际文件名
     "sources": {"4011": {"path": "<原始DDS路径>"}, ...}} # 槽位→声明来源(逐一锚定)
    存在时: 贴图解析按 slots; source_data_integrity 按声明的原始DDS锚定(不再按文件名推源)。
    解析失败 => 直接报错 (fail-closed)。"""
    p = os.path.join(tex_dir, '_input_manifest.json')
    if not os.path.exists(p):
        return None, None
    try:
        return json.load(open(p, encoding='utf-8')), p
    except Exception as e:
        raise SystemExit('_input_manifest.json 无法解析(fail-closed): %s' % e)

def provenance_eval(facts):
    """source_data_integrity 判定(纯函数, 主流程与测试共用)。fail-closed。
    facts: textures=[verify_texture_vs_raw 结果], v19_used, tint_map_used, tint_map_sourced,
           face_overrides_used, edgeface_used, band_used, post_executed, source_mode, out_of_root"""
    reasons = []
    if facts.get('v19_used'): reasons.append('人工改色基色(v19)')
    if facts.get('tint_map_used') and not facts.get('tint_map_sourced'):
        reasons.append('tint_map 染色(无源参数标注)')
    if facts.get('face_overrides_used'): reasons.append('face_overrides 选面覆盖')
    if facts.get('edgeface_used'): reasons.append('edgeface_mask 面选区染银')
    if facts.get('band_used'): reasons.append('屏幕距离带(band)')
    bad = [t['file'] for t in facts.get('textures', []) if t.get('match') is not True]
    if bad: reasons.append('贴图未通过原始DDS锚定: ' + ','.join(bad))
    if facts.get('out_of_root'): reasons.append('贴图路径越界: ' + ','.join(facts['out_of_root']))
    if facts.get('source_mode') and facts.get('post_executed'):
        reasons.append('source 模式执行了后处理(post)')
    return (len(reasons) == 0), reasons

def fidelity_eval(facts, Params, jn_stats=None):
    """shader_fidelity: 近似项清单; 有任一近似 => 'approximate'。"""
    rs = ['观察灯光=固定 studio rig (非源 IBL)']
    rs.append('刃口菲涅尔/定向光泽(sheen)=渲染器近似参数(非 c159 值)')
    if jn_stats: rs.append('跨缝法线调和=几何近似(非源数据)')
    rs.append('Sub0(刀刃) c159 无覆写块 = 引擎默认轨道, 渲染器为近似实现')
    if facts.get('tint_map_used'): rs.append('晶体色=过渡 tint 模型 v1 (正式分层见 render_material_layers.py)')
    if facts.get('post_executed') and not facts.get('source_mode'): rs.append('视觉后处理 R2–R7 已执行')
    return ('approximate' if rs else 'source_matched'), rs

def run_qc(o, ctx, W2, H2, Params):
    res = {}
    img = o
    # QC1 连接处色差: 护手侧(窗) vs 剑身根侧(窗)
    guard_win = (ctx['Bmask'] & ~ctx['blade_m'] & ctx['sil'])
    root_win = (ctx['rast']((ctx['zc'] > 4.8) & (ctx['zc'] < 6.3)) > 0) & ctx['sil']
    if guard_win.any() and root_win.any():
        g = img[guard_win].mean(0); r = img[root_win].mean(0)
        dL = float(abs(g.mean() - r.mean()))
        dRB = float(abs((g[0] - g[2]) - (r[0] - r[2])))
        res['junction'] = dict(dL=round(dL, 3), dRB=round(dRB, 3),
                               pass_=bool(dL < 0.18 and dRB < 0.35))
    # QC2 刃口: fresnel模式=边缘亮度比(rim vs 内侧)及沿轮廓变化; band模式=旧距离带指标
    if ctx['B'].sum() > 400:
        Dmap = ndi.distance_transform_edt(ctx['B'])
        rim = (Dmap > 1.0) & (Dmap < 6.0) & ctx['B']
        inner = (Dmap > 10) & (Dmap < 28) & ctx['B']
        if rim.sum() > 150 and inner.sum() > 150:
            if Params.get('edge_mode', 'band') == 'fresnel':
                # 峰值口径: 轮廓附近(D<8)的局部最亮 vs 内侧(D10-28)均值
                rim8 = (Dmap > 0.8) & (Dmap < 8.0) & ctx['B']
                ys, xs = np.where(rim)
                rs = []
                step = max(len(xs) // 16, 1)
                for k in range(0, len(xs), step):
                    y0, x0 = int(ys[k]), int(xs[k])
                    w0, w1 = max(y0 - 40, 0), y0 + 40
                    h0, h1 = max(x0 - 40, 0), x0 + 40
                    lr = rim8[w0:w1, h0:h1]
                    lsel = inner[w0:w1, h0:h1]
                    if lr.sum() >= 3 and lsel.sum() >= 6:
                        peak = float(img[w0:w1, h0:h1][lr].max())
                        rs.append(peak / max(float(img[w0:w1, h0:h1][lsel].mean()), 1e-6))
                rmean = float(np.mean(rs)) if rs else 0.0
                rvar = float(np.std(rs) / max(rmean, 1e-6)) if len(rs) > 3 else 0.0
                res['edge'] = dict(mode='fresnel', rim_peak_ratio=round(rmean, 3), rim_ratio_var=round(rvar, 3),
                                   pass_=bool(1.10 < rmean < 2.8 and rvar > 0.04))
            else:
                band_px = (Dmap > 0.5) & (Dmap < 7) & ctx['B']
                if band_px.sum() > 200:
                    cov = float(ctx['wsils'][band_px].mean())
                    lums = img[band_px].mean(1)
                    lum_cv = float(lums.std() / max(lums.mean(), 1e-6))
                    strong = band_px & (ctx['wsils'] > 0.55)
                    if strong.sum() > 50:
                        px = img[strong]; hue = float((px[:, 2] - px[:, 0]).mean())
                    else:
                        hue = -1.0
                    res['edge'] = dict(n_band=int(band_px.sum()), band_cover=round(cov, 3),
                                       band_lum_cv=round(lum_cv, 3), strong_hue_BR=round(hue, 3),
                                       pass_=bool(cov > 0.30 and lum_cv > 0.08 and hue > -0.05))
    # QC3 材质分区: 仅统计非背景区域: 金区(R-B高) 银区(B>=R) 红宝石(R-G高)
    nonsky = ctx['sil'] | ctx['Bmask']
    gold_px = int((((img[..., 0] - img[..., 2]) > 0.16) & nonsky).sum())
    silv_px = int((((img[..., 2] - img[..., 0]) > -0.02) & nonsky & (ctx['blade_m'] | ctx['Bmask'])).sum())
    gem_red = int(((ctx['S2']) & ((img[..., 0] - img[..., 1]) > 0.16)).sum())
    # 外审 v7 令：色域门双重作废（旧门限按 R/B 错序配色校准 + 把自发光/SFX 的金当基色金）。
    # 现行口径 = N/A — source material chain incomplete；不重调门限让现有图通过。
    res['zones'] = dict(gold_px=gold_px, silver_cool_px=silv_px, gem_red_px=gem_red,
                        gate='N/A — source material chain incomplete',
                        recompute_after='shader/IBL/emissive/后处理齐全后（visual fidelity gate）')
    # QC4 洞内衬: 洞内亮度>0.05 且暖色
    if ctx['holes']:
        hx, hy, rH = ctx['holes'][0]
        yy, xx = np.mgrid[0:H2, 0:W2]
        dm = np.sqrt((xx - hx) ** 2 + (yy - hy) ** 2) < rH * 0.6
        if dm.any():
            hv = img[dm].mean(0)
            res['hole'] = dict(luma=round(float(hv.mean()), 3), warm=round(float(hv[0] - hv[2]), 3),
                               pass_=bool(hv.mean() > 0.06 and (hv[0] - hv[2]) > 0.05))
    # 网关拆分（外审 v7 令）：source integrity gate / visual fidelity gate
    res['gates'] = dict(
        source_integrity=None,  # 由 main 的 provenance 段回填(此处 provenance 尚未计算)
        visual_fidelity='N/A — source material chain incomplete',
        definition=dict(source_integrity='贴图哈希/RGBA 通道/槽位绑定/参数来源/禁止人工 tint',
                        visual_fidelity='最终 shader+IBL+emissive+后处理齐全后，才与游戏参考比较'))
    res['ok'] = all(v.get('pass_', True) for k, v in res.items() if isinstance(v, dict))
    return res

def build_c159_tints(c159_path):
    """v3: 通用解析器 + 自动绑定 构建过渡 tint (正式分层渲染见 render_material_layers.py)。fail-closed。"""
    import c159_pair as CP
    mats, meta = CP.load_asset_materials(c159_path)
    tint, note = {}, dict(model='pipeline tint 过渡模型 v1 (正式分层路线=render_material_layers.py)',
                          src_file=os.path.basename(c159_path),
                          bind_file=os.path.basename(meta.get('bind_file') or ''),
                          bind_file_abs=meta.get('bind_file'))
    per_sub = {}
    for si, d in mats.items():
        per_sub[str(si)] = dict(material=d.get('material'), params_keys=sorted((d.get('params') or {}).keys()))
    p1 = (mats.get(1) or {}).get('params') or {}
    p2 = (mats.get(2) or {}).get('params') or {}
    if 'u_base_color' in p1:
        tint[1] = [float(x) for x in p1['u_base_color'][:3]]
    if p2:
        def g(k):
            v = p2.get(k)
            return [float(x) for x in v[:3]] if isinstance(v, list) else [0.0, 0.0, 0.0]
        refr, subs, crys = g('u_refraction_color'), g('u_subsurface_color'), g('u_crystal_color')
        gem = [round(min(1.0, 0.5 * refr[i] + 0.3 * subs[i] + 0.2 * crys[i]), 4) for i in range(3)]
        tint[2] = gem
        note['values'] = dict(sub2_refr=refr, sub2_subs=subs, sub2_crys=crys, sub2_gem=gem)
    note['per_sub'] = per_sub
    return tint, note

def main():
    args = [a for a in sys.argv[1:]]
    qc_only = '--qc-only' in args
    if qc_only: args.remove('--qc-only')
    src_mode = '--source' in args
    if src_mode: args.remove('--source')
    c159_path = None
    if '--params-c159' in args:
        i = args.index('--params-c159'); c159_path = args[i + 1]; del args[i:i + 2]
    use_c159 = c159_path is not None
    inj = []
    if '--inject' in args:
        i = args.index('--inject'); inj = [x for x in args[i + 1].split(',') if x]; del args[i:i + 2]
    raw_dir = None
    if '--raw-dir' in args:
        i = args.index('--raw-dir'); raw_dir = args[i + 1]; del args[i:i + 2]
    prof_name = None
    if '--profile' in args:
        i = args.index('--profile'); prof_name = args[i + 1]; del args[i:i + 2]
    mesh_path, tex_dir, out_dir = args[0], args[1], args[2]
    if raw_dir is None: raw_dir = os.path.dirname(mesh_path)
    os.makedirs(out_dir, exist_ok=True)
    prof = SKIN_PROFILES.get(prof_name, {}) if prof_name else {}
    Params = dict(PARAMS)
    Params['source_mode'] = src_mode
    W0, H0 = 1560, 1100
    P, uv, idx, meta = R.parse_mesh(mesh_path)
    c = (P.min(0) + P.max(0)) / 2.0; p = P - c
    sx_ = p @ np.array([0, 1.0, 0]); sy_ = p @ np.array([0, 0, 1.0])
    ar = math.radians(Params['roll_deg'])
    Rr = np.array([[math.cos(ar), -math.sin(ar)], [math.sin(ar), math.cos(ar)]])
    s = Rr @ np.stack([sx_, sy_]); sxx, syy = s[0], s[1]
    Mg = 60
    scv = min((W0 - 2 * Mg) / (sxx.max() - sxx.min()), (H0 - 2 * Mg) / (syy.max() - syy.min()))
    ccx = (sxx.max() + sxx.min()) / 2; ccy = (syy.max() + syy.min()) / 2
    zc, fwd, rast = build_masks(P, idx, meta, W0, H0, Rr, ccx, ccy, scv, c)
    jn_stats = {}
    base_tex = None; tmap_used = {}; tint_used = None; tint_src = None; fover_used = None; edgeface_used = None; nrm_ch_used = (0, 1)  # 规范RGBA: 法线在 R,G
    T = {}
    _manifest = None; _manifest_path = None
    if not qc_only:
        T = {n: os.path.join(tex_dir, f'tex_{n}.png') for n in (4009, 4011, 4012, 4013)}
        _manifest, _manifest_path = load_input_manifest(tex_dir)
        if _manifest:
            _slots = _manifest.get('slots') or {}
            for _n2 in list(T.keys()):
                _fn = _slots.get(str(_n2))
                if _fn: T[_n2] = os.path.join(tex_dir, _fn)
        base_tex = T[4011]  # 源链路模式: 只用未修改的 4011; v19 人工改色贴图已停用
        tmap_used = {1: T[4009], 2: T[4011]}   # 源素材直接使用(未修改); _mk_silver/_auto_silver 停用
        tint_used = None; tint_src = None
        if use_c159:
            tint_used, tint_src = build_c159_tints(c159_path)
        if 'tint' in inj:
            tint_used = {2: (0.9, 0.2, 0.2)}; tint_src = None
        if 'v19' in inj:
            v19p = os.path.join(tex_dir, 'tex_4011_v19.png')
            if not os.path.exists(v19p): raise SystemExit('inject v19: 缺少 %s' % v19p)
            base_tex = v19p
        fover_used = None
        if 'face' in inj:
            _fm = np.zeros(len(idx), bool); _fm[0] = True
            fover_used = [(_fm, (1.0, 1.0, 1.0), 0.5)]
        if 'band' in inj:
            Params['edge_mode'] = 'band'
        edgeface_used = None
        nrm_ch_used = (0, 1)  # 规范RGBA: 法线在 R,G
        warm = None  # 源链路模式: 发光染色停用 (4013 通道语义待定)
        emask = (np.abs(np.cross(P[idx[:, 1]] - P[idx[:, 0]], P[idx[:, 2]] - P[idx[:, 0]]))[:, 1]
                 / np.maximum(np.linalg.norm(np.cross(P[idx[:, 1]] - P[idx[:, 0]], P[idx[:, 2]] - P[idx[:, 0]]), axis=1), 1e-9) > 0.66) & (zc < 6.6)
        fover = []
        if 'grip_z' in prof:
            gz = prof['grip_z']
            gm = (idx[:, 0] >= meta['sub_offsets'][0][0]) & (idx[:, 2] < meta['sub_offsets'][0][1]) & (zc > gz[0]) & (zc < gz[1])
            fover.append((gm, prof['grip_rgb'], prof['grip_blend']))
        if 'spike' in prof:
            sp = prof['spike']
            ymf = P[idx][:, :, 1].max(axis=1); ycm = P[idx][:, :, 1].mean(axis=1)
            sm = (idx[:, 0] >= meta['sub_offsets'][0][0]) & (idx[:, 2] < meta['sub_offsets'][0][1]) \
                 & (ymf > sp['ymax']) & (ycm > sp['ymean']) & (zc > sp['z'][0]) & (zc < sp['z'][1])
            fover.append((sm, sp['rgb'], sp['blend']))
        n_over = None
        jn = Params['junction_normals']
        if jn.get('on'):
            n_over, jn_stats = harmonize_junction_normals(P, idx, meta, jn['z'][0], jn['z'][1], jn['eps'], jn['blend'])
        R.render(P, uv, idx, os.path.join(out_dir, '_base.png'), tex=base_tex, emi=None, nrm=T[4012],
                 nrm_map={0: T[4012]}, nrm_ch=nrm_ch_used, nrm_str=Params['nrm_str'], sub_offsets=meta['sub_offsets'],
                 roll_deg=Params['roll_deg'], weld_smooth=True,
                 normal_override=n_over,
                 bg_top=Params['bg_top'], bg_bot=Params['bg_bot'],
                 spec_str=Params['spec_str'], spec_pow=Params['spec_pow'], spec2_str=Params['spec2_str'],
                 tex_map=tmap_used, emi_map=None,
                 tint_map=tint_used,
                 glow=Params['glow'], bloom=Params['bloom'], ambient=Params['ambient'], diffuse=Params['diffuse'],
                 edgek=Params['edgek'], edgecol=Params['edgecol'], edge_pow=Params['edge_pow'],
                 edge_sheen_k=Params.get('edge_sheen_k',0.0), edge_sheen_mu=Params.get('edge_sheen_mu',0.52), edge_sheen_sigma=Params.get('edge_sheen_sigma',0.30),
                 nl_pow=Params['nl_pow'], base_gamma=Params['base_gamma'], knee=Params['knee'], knee_k=Params['knee_k'],
                 envk=Params['envk'], edgeface_mask=edgeface_used, edgeface_blend=0.0, edgeface_rgb=(0.80, 0.87, 0.97),
                 face_overrides=fover_used, size=(W0, H0), ss=2)
        img = np.asarray(Image.open(os.path.join(out_dir, '_base.png')).convert('RGB'), np.float32) / 255.0
    else:
        # qc-only: 从已渲染的 _base.png 重新走后处理+质检(不重跑光栅渲染)
        img = np.asarray(Image.open(os.path.join(out_dir, '_base.png')).convert('RGB'), np.float32) / 255.0
    inj_post = 'post' in inj
    post_executed = bool((not Params.get('source_mode')) or inj_post)
    o, ctx = post_process(img, P, idx, meta, zc, fwd, rast, W0, H0, Params, prof,
                          apply_rules=post_executed)
    final = os.path.join(out_dir, 'render_final.png')
    Image.fromarray((o * 255).astype(np.uint8)).save(final)
    qc = run_qc(o, ctx, W0, H0, Params)
    if jn_stats:
        qc['junction_normals'] = jn_stats
    # ---- 源纯度追溯 (provenance) ----
    def _sha(p):
        try:
            return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
        except Exception:
            return None
    _sd = os.path.dirname(os.path.abspath(__file__))
    import raw_anchor as RA
    # 从实际执行参数自动采集(非手填):
    _tex_paths = [p for p in ([base_tex] + list(tmap_used.values())) if p]
    if _manifest:
        # 通用输入清单模式: 按声明的来源 DDS 逐一锚定; 未声明 => fail-closed
        _srcs = _manifest.get('sources') or {}
        _seen, _tex_checks = set(), []
        for p in _tex_paths:
            if p in _seen: continue
            _seen.add(p)
            _slot = next((str(n) for n, pp in T.items() if pp == p), None)
            _decl = _srcs.get(_slot) if _slot else None
            _dpath = _decl.get('path') if isinstance(_decl, dict) else (_decl if isinstance(_decl, str) else None)
            if _dpath:
                _tex_checks.append(RA.verify_texture_vs_declared(p, _dpath))
            else:
                _tex_checks.append(dict(file=os.path.basename(p), declared=False, match=False,
                                        reason='未在 _input_manifest.json 声明来源(slot=%s)' % _slot,
                                        norm_path=os.path.normcase(os.path.abspath(p))))
    else:
        _tex_checks = [RA.verify_texture_vs_raw(p, raw_dir) for p in _tex_paths]
    _roots = [os.path.normcase(os.path.abspath(tex_dir)), os.path.normcase(os.path.abspath(raw_dir))]
    _out_of_root = [t['file'] for t in _tex_checks if not any(t['norm_path'].startswith(r) for r in _roots)]
    _facts = dict(
        textures=_tex_checks,
        v19_used=any('v19' in os.path.basename(p) for p in _tex_paths),
        tint_map_used=(tint_used is not None),
        tint_map_sourced=bool(tint_src is not None),
        face_overrides_used=bool(fover_used),
        edgeface_used=(edgeface_used is not None),
        band_used=(Params.get('edge_mode') == 'band'),
        post_executed=bool(post_executed),
        source_mode=bool(Params.get('source_mode')),
        out_of_root=_out_of_root,
    )
    _src_pass, _src_reasons = provenance_eval(_facts)
    _fid_status, _fid_reasons = fidelity_eval(_facts, Params, jn_stats)
    _bind_abs = (tint_src or {}).get('bind_file_abs') if isinstance(tint_src, dict) else None
    prov = dict(
        run_id=time.strftime('%Y%m%d_%H%M%S') + ('_SRC' if Params.get('source_mode') else '_VIS'),
        mode=('source' if Params.get('source_mode') else 'visual'),
        script_hashes={'pipeline': _sha(__file__), 'renderer': _sha(os.path.join(_sd, 'render_neox_mesh.py')),
                       'parser': _sha(os.path.join(_sd, 'c159_pair.py'))},
        inputs={
            'mesh': _sha(mesh_path),
            'c159_material': _sha(c159_path),
            'c159_binding': _sha(_bind_abs) if _bind_abs else None,
            'raw_dir': raw_dir,
            'input_manifest': os.path.abspath(_manifest_path) if _manifest_path else None,
            'textures': {t['file']: dict(sha256=t.get('sha256'), raw=t.get('raw_file'), raw_sha256=t.get('raw_sha256'),
                                          match=t.get('match'), maxdiff=t.get('maxdiff')) for t in _tex_checks},
        },
        texture_mapping=({  # 通用输入清单模式: 槽位→文件→声明来源DDS(逐一锚定)
            'slots': {str(n): os.path.basename(T.get(n) or '') for n in sorted(T)},
            'sources': {str(k): (v.get('path') if isinstance(v, dict) else v) for k, v in (_manifest.get('sources') or {}).items()},
        } if _manifest else {
            'sub0_base': 'tex_4011.png (004011=001a), c159: skim_0 无覆写',
            'sub0_normal': 'tex_4012.png (004012=001n), 通道 R,G (nrm_ch=(0,1), 规范RGBA)',
            'sub0_mask': 'tex_4013.png (004013=001m) 仅R通道变化 (规范RGBA; 旧称 B通道=光滑度/光泽度 已撤销, 语义待G-buffer定案); 接入途径=render_material_layers.py',
            'sub1_base': 'tex_4009.png (004009=001b_m) skim_1 晶体辅助',
            'sub2_base': 'tex_4009.png skim_2 晶体辅助',
        }),
        material_params={
            'source': 'c159 自动解析(c159_pair.py 通用版): 宝石红三色=(u_crystal_color=(0.2431,0,0), u_subsurface_color=(0.8549,0,0), u_refraction_color=(1.0,0,0)); 全参数表见 tints.per_sub',
            'tints': tint_src,
        },
        source_data_integrity={
            'pass': _src_pass,
            'checks': {
                'textures': _tex_checks,
                'manual_flags': {k: _facts[k] for k in ('v19_used', 'tint_map_used', 'tint_map_sourced',
                                                        'face_overrides_used', 'edgeface_used', 'band_used')},
                'post_in_source_mode': bool(_facts['source_mode'] and _facts['post_executed']),
                'out_of_root': _out_of_root},
            'reasons': _src_reasons},
        shader_fidelity=dict(
            status=_fid_status, reasons=_fid_reasons,
            note='source_matched 仅当全部层按源语义实现(无近似灯光/法线调和/过渡模型/后处理补色)时给出'),
    )
    qc['source_data_integrity_pass'] = _src_pass
    qc.setdefault('gates', {})['source_integrity'] = bool(_src_pass)
    qc['shader_fidelity'] = _fid_status
    with open(os.path.join(out_dir, 'provenance.json'), 'w', encoding='utf-8') as f:
        json.dump(prov, f, ensure_ascii=False, indent=1)
    with open(os.path.join(out_dir, 'qc.json'), 'w', encoding='utf-8') as f:
        json.dump(qc, f, ensure_ascii=False, indent=1)
    print(json.dumps(qc, ensure_ascii=False, indent=1))
    print('FINAL:', final)
    return final

if __name__ == '__main__':
    main()
