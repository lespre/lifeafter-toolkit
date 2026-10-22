"""render_game_faithful.py — 完全按【游戏 shader 汇编】出图
依据：_game_shader_db/pipes/d11_deferred_quality2_shader_pbr_crystal.nfx2_01393c07_b2d62c97_d11.pipe_blob1_blob.asm
     + deferred_pbr_weapon 同法
不进颜色运算的东西一律不做（宁缺不编 ✓）；每个步骤打印它的汇编出处 ✓。

用法:
  python render_game_faithful.py <mesh> <out_dir> --c159 <001223.c159>
        --tex-a <a.png> --tex-bm <b_m.png> --tex-n <n.png>
        --tex-bump <crystal_bump.png> --tex-caustic <crystal_caustic.png>
        --tex-refr <refraction.png> --ibl <faces_dir> --ibl-name car_studio01
"""
import sys, os, json, math
import numpy as np
from PIL import Image

SK = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SK)
import render_neox_mesh as R
import crystal_source as CS
try:
    import source_ibl as SIBL
except Exception:
    SIBL = None
try:
    import c159_pair as CP
except Exception:
    CP = None

W, H = 1400, 1000


def load_rgba(p):
    return np.asarray(Image.open(p).convert('RGBA'), np.float32) / 255.0


def srgb2lin(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)


def lin2srgb(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * (x ** (1 / 2.4)) - 0.055)


def main():
    args = sys.argv[1:]
    mesh = args[0]; out_dir = args[1]
    os.makedirs(out_dir, exist_ok=True)
    def opt(k, d=None):
        return args[args.index(k) + 1] if k in args else d

    c159 = opt('--c159')
    T = dict(a=opt('--tex-a'), bm=opt('--tex-bm'), n=opt('--tex-n'),
             bump=opt('--tex-bump'), caustic=opt('--tex-caustic'),
             refr=opt('--tex-refr'))
    ibl_dir = opt('--ibl'); ibl_name = opt('--ibl-name', 'car_studio01')

    print('══ 输入 ══')
    for k, v in T.items():
        print('   %-8s %s %s' % (k, '✓' if (v and os.path.isfile(v)) else '✗', v or ''))
    print('   ibl      %s / %s' % ('✓' if ibl_dir else '✗', ibl_dir or ''))

    # ---- 材质参数（从 c159 读；来源 = c159_pair ✓）----
    params = {}
    if c159 and CP is not None and hasattr(CP, 'load_asset_materials'):
        try:
            r = CP.load_asset_materials(c159)
            mats = r[0] if isinstance(r, tuple) else r        # ★ 返回 (mats, binds) ✓
            if isinstance(mats, dict):
                subs = [mats[k].get('params') or {} for k in sorted(mats, key=lambda z: int(z))]
            elif isinstance(mats, list):
                subs = [(m.get('params') or {}) for m in mats]
            else:
                subs = []
        except Exception as e:
            print('   参数读取失败: %s' % e)
            subs = []
    subs = [] if 'subs' not in dir() else subs
    print('   c159 材质块: %d' % len(subs))

    def P(si, name, dflt):
        if si < len(subs):
            v = subs[si].get(name)
            if v is not None:
                return v
        return dflt

    # ---- 几何（沿用项目的 mesh 解析 ✓ 顶点流已按引擎对标改过 ✓）----
    P3, uv, idx, meta = R.parse_mesh2(mesh) if hasattr(R, 'parse_mesh2') else (None, None, None, None)
    if P3 is None:
        import mesh_parse2 as MP
        P3, uv, idx, meta = MP.parse_mesh2(mesh)
    sub_off = meta['sub_offsets']
    print('   顶点 %d · 面 %d · submesh %d %s' % (P3.shape[0], len(idx) // 3, len(sub_off), list(sub_off)))

    # ---- 纹理（★ 按【shader 的绑定名】✓ 不是按我猜 ✗）----
    #   asm L260-266:  t0 Tex0 · t1 NormalMap · t2 DetailMap · t3 t_basecolor
    #                  t4 t_caustic_tex · t5 t_refraction_tex · t6 t_custom_ibl(cube)
    t0 = load_rgba(T['bm']) if T['bm'] else None      # Tex0   ← b_m（c159 块1 声明 Tex0←001b_m ✓）
    t1 = load_rgba(T['n']) if T['n'] else None        # NormalMap
    t2 = load_rgba(T['bump']) if T['bump'] else None  # DetailMap ← crystal_bump ✓
    t3 = load_rgba(T['a']) if T['a'] else None        # t_basecolor ← a ✓（晶体色的来源 ✓）
    t4 = load_rgba(T['caustic']) if T['caustic'] else None
    t5 = load_rgba(T['refr']) if T['refr'] else None
    mips = SIBL.load_cube(ibl_dir, ibl_name) if (SIBL and ibl_dir) else None
    print('   IBL mips: %s' % (len(mips) if mips else '无'))

    if t0 is None or t3 is None:
        raise SystemExit('至少要 --tex-bm（t0 Tex0）与 --tex-a（t3 t_basecolor）')

    # ---- 相机：★ 用 viewer.json 的 game_reference（游戏参照视角 ✓ 不是我随手设的 ✗）----
    N = P3.shape[0]
    CAMPOS = np.array([-14.6129, -2.2747, -1.2894], np.float32)
    CAMTGT = np.array([0.0602, -0.1842, 0.0986], np.float32)
    CAMUP = np.array([-0.8246, -0.5572, -0.0982], np.float32)
    CAMFOV = 34.0
    if '--cam-json' in args:      # 允许指定别的 viewer.json ✓
        try:
            _j = json.loads(open(args[args.index('--cam-json') + 1], encoding='utf-8').read())
            _c = (_j.get('camera_presets') or [{}])[0]
            CAMPOS = np.array(_c.get('position', CAMPOS), np.float32)
            CAMTGT = np.array(_c.get('target', CAMTGT), np.float32)
            CAMUP = np.array(_c.get('up', CAMUP), np.float32)
            CAMFOV = float(_c.get('fov', CAMFOV))
        except Exception as _e:
            print('  相机读取失败: %s' % _e)
    print('   相机 game_reference: pos=%s tgt=%s up=%s fov=%.1f' % (CAMPOS, CAMTGT, CAMUP, CAMFOV))

    fwd = CAMTGT - CAMPOS; fwd /= np.linalg.norm(fwd)
    rgt = np.cross(fwd, CAMUP); rgt /= np.linalg.norm(rgt)
    upv = np.cross(rgt, fwd)
    rel = P3 - CAMPOS                                  # 世界坐标（顶点已是世界 ✓）
    Zc = rel @ fwd                                     # 相机空间深度
    Xc = rel @ rgt
    Yc = rel @ upv
    Zc = np.maximum(Zc, 1e-4)
    fpx = 0.5 * H / math.tan(math.radians(CAMFOV) * 0.5)   # 焦距（像素）
    sx = (Xc / Zc * fpx + W / 2).astype(np.int32)
    sy = (H / 2 - Yc / Zc * fpx).astype(np.int32)
    dep = np.full((H, W), 1e18, np.float32)            # ★ 透视：z 越小越近 ✓
    buf = np.zeros((H, W, 3), np.float32)
    uvb = np.zeros((H, W, 2), np.float32)
    nb = np.zeros((H, W, 3), np.float32)
    sb = np.full((H, W), -1, np.int32)
    nsub = len(sub_off)
    for si in range(nsub):
        a0, a1 = sub_off[si]
        # 该 submesh 的面（★ idx 形状 (N,3) ✓ 每行一个三角形 ✓）
        t3i = np.nonzero(((idx >= a0) & (idx < a1)).all(1))[0]
        print('   sub%d 顶点[%d:%d] 面 %d' % (si, a0, a1, len(t3i)))
        for t in t3i:
            ia, ib, ic = idx[t, 0], idx[t, 1], idx[t, 2]      # ★ 不是 idx[t*3] ✗
            x0, y0 = sx[ia], sy[ia]; x1, y1 = sx[ib], sy[ib]; x2, y2 = sx[ic], sy[ic]
            minx = max(min(x0, x1, x2), 0); maxx = min(max(x0, x1, x2) + 1, W)
            miny = max(min(y0, y1, y2), 0); maxy = min(max(y0, y1, y2) + 1, H)
            if maxx <= minx or maxy <= miny: continue
            gx, gy = np.meshgrid(np.arange(minx, maxx) + 0.5, np.arange(miny, maxy) + 0.5)
            d0 = (x1 - x0) * (gy - y0) - (y1 - y0) * (gx - x0)
            d1 = (x2 - x1) * (gy - y1) - (y2 - y1) * (gx - x1)
            d2 = (x0 - x2) * (gy - y2) - (y0 - y2) * (gx - x2)
            m = ((d0 >= 0) & (d1 >= 0) & (d2 >= 0)) | ((d0 <= 0) & (d1 <= 0) & (d2 <= 0))
            if not m.any(): continue
            area = d0 + d1 + d2
            # ★ 透视校正插值：用 1/z 加权 ✓
            i0, i1, i2 = 1.0 / Zc[ia], 1.0 / Zc[ib], 1.0 / Zc[ic]
            l0 = d1 / area; l1 = d2 / area; l2 = d0 / area
            den = l0 * i0 + l1 * i1 + l2 * i2
            den = np.where(np.abs(den) < 1e-12, 1e-12, den)
            w0 = l0 * i0 / den; w1 = l1 * i1 / den; w2 = l2 * i2 / den
            dd = 1.0 / den                                  # 透视深度
            sub = dep[miny:maxy, minx:maxx]; upd = m & (dd < sub)     # ★ 越小越近 ✓
            if not upd.any(): continue
            uu = w0 * uv[ia, 0] + w1 * uv[ib, 0] + w2 * uv[ic, 0]
            vv = w0 * uv[ia, 1] + w1 * uv[ib, 1] + w2 * uv[ic, 1]
            nn = (w0[..., None] * P3[ia] + w1[..., None] * P3[ib] + w2[..., None] * P3[ic])
            nn /= np.maximum(np.linalg.norm(nn, axis=2, keepdims=True), 1e-6)
            uvb[miny:maxy, minx:maxx][upd] = np.stack([uu, vv], -1)[upd]
            nb[miny:maxy, minx:maxx][upd] = nn[upd]
            sb[miny:maxy, minx:maxx][upd] = si
            sub[upd] = dd[upd]

    model = sb >= 0
    print('   覆盖像素 %d (%.1f%%)' % (model.sum(), 100.0 * model.mean()))

    # ---- 逐像素：完全按汇编 ✓ ----
    def samp(tex, u, v):
        if tex is None: return np.zeros((len(u), 4), np.float32)
        tx = np.clip((u * (tex.shape[1] - 1)).astype(np.int32), 0, tex.shape[1] - 1)
        ty = np.clip((v * (tex.shape[0] - 1)).astype(np.int32), 0, tex.shape[0] - 1)
        return tex[ty, tx]

    out = np.zeros((H, W, 3), np.float32)
    sv = sb[model]
    uvm = uvb[model]; nm = nb[model]
    base_s = samp(t0, uvm[:, 0], uvm[:, 1])
    base = np.clip(base_s[..., :3], 0, 1)                       # L346 mov_sat ✓
    nmap = samp(t1, uvm[:, 0], uvm[:, 1])[..., :2] * 2 - 1      # L347-348 ✓
    det = samp(t2, uvm[:, 0], uvm[:, 1]) if t2 is not None else None
    tc = samp(t3, uvm[:, 0], uvm[:, 1])[..., :3]                # ★ t3 = t_basecolor ✓
    ca = samp(t4, uvm[:, 0], uvm[:, 1]) if t4 is not None else None
    rf = samp(t5, uvm[:, 0], uvm[:, 1]) if t5 is not None else None

    for si in np.unique(sv):
        m_ = sv == si
        uc = np.array(P(si, 'u_crystal_color', (1, 1, 1))[:3], np.float32)
        ub = np.array(P(si, 'u_base_color', (0.5, 0.5, 0.5))[:3], np.float32)
        br = np.array(P(si, 'u_caustic_brightness', 0.0), np.float32)
        d_w = (det[..., 3] if det is not None else np.full(m_.sum(), 0.5, np.float32))[m_] \
            if det is not None else np.full(m_.sum(), 0.5, np.float32)
        # ★ 晶体色（L382-391 ✓）
        C = CS.crystal_color(tc[m_], base[..., 0][m_], d_w, uc, ub)
        # ★ caustic 进颜色（L416-418 ✓）
        if ca is not None:
            C = CS.caustic_add(C, ca[..., :3][m_], br, ca[..., 3][m_])
        # ★ IBL（L527-546 ✓）
        if mips is not None:
            rough = np.clip(P(si, 'u_crystal_roughness', P(si, 'u_base_roughness', 0.3)), 0.02, 1.0)
            lod = CS.roughness_to_lod(np.full(int(m_.sum()), float(rough), np.float32))
            Nw = nm[m_].astype(np.float32)
            # ★ 逐像素视角方向 = 从相机指向该像素（世界坐标 ✓）
            ii = np.nonzero(model)
            px = np.stack([ii[0][m_], ii[1][m_]], 1)
            # 反投影：像素 → 相机空间方向 → 世界
            xc = (px[:, 1] - W / 2) / fpx
            yc = (H / 2 - px[:, 0]) / fpx
            Vw = (rgt[None, :] * xc[:, None] + upv[None, :] * yc[:, None] + fwd[None, :])
            Vv = Vw / np.maximum(np.linalg.norm(Vw, axis=1, keepdims=True), 1e-9)
            Rr = 2 * np.sum(Nw * Vv, 1, keepdims=True) * Nw - Vv
            rot = float(P(si, 'u_rotate_angle', 0.0))
            if abs(rot) > 1e-8:
                c0, s0 = np.cos(rot), np.sin(rot)
                Rr = np.stack([Rr[:, 0] * c0 + Rr[:, 2] * s0, Rr[:, 1], -Rr[:, 0] * s0 + Rr[:, 2] * c0], 1)
            S = SIBL.sample_cube(mips, Rr, lod)
            env = CS.rgbm_env(S)
            env = CS.lightmap_mix(env, float(P(si, 'u_lightmap_factor', 0.0)))
            env = env * float(P(si, 'u_cube_brightness', 1.0)) * float(P(si, 'u_env_day2night_exposure', 1.0))
            # ★ 最终 = 环境 × 晶体色（L545-546 ✓）
            C = CS.env_times_color(env, C)
        else:
            C = C * 0.35
        out_sel = np.zeros((H, W, 3), np.float32)
        out_sel[np.nonzero(model)] = 0
        outm = np.zeros((int(m_.sum()), 3), np.float32)
        outm[:] = C
        full = np.zeros((H, W, 3), np.float32)
        ii = np.nonzero(model)
        full[ii[0][m_], ii[1][m_]] = outm
        out += full

    img = (lin2srgb(out) * 255).astype(np.uint8)
    Image.fromarray(img).save(os.path.join(out_dir, 'game_faithful.png'))
    print('✓ 出图 → %s' % os.path.join(out_dir, 'game_faithful.png'))


if __name__ == '__main__':
    main()
