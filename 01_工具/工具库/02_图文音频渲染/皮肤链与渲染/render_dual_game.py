"""render_dual_game.py — 双持（001264.mesh）按游戏汇编出图
每把枪用自己的贴图组（sub0-3=012 族 · sub4-6=010 族 ✓ 来自 viewer.json source_chain ✓）
相机 = viewer.json 的 game_reference ✓
"""
import sys, os, json, math
import numpy as np
from PIL import Image

SK = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SK)
import crystal_source as CS
try:
    import source_ibl as SIBL
except Exception:
    SIBL = None
try:
    import c159_pair as CP
except Exception:
    CP = None
try:
    import mesh_parse2 as MP
except Exception:
    MP = None

W, H = 1600, 1000


def load_rgba(p):
    return np.asarray(Image.open(p).convert('RGBA'), np.float32) / 255.0


def srgb2lin(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)


def lin2srgb(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * (x ** (1 / 2.4)) - 0.055)


def main():
    a = sys.argv[1:]
    mesh = a[0]; out_dir = a[1]
    os.makedirs(out_dir, exist_ok=True)
    def opt(k, d=None):
        return a[a.index(k) + 1] if k in a else d

    c159 = opt('--c159'); texdir = opt('--texdir')
    faces = opt('--ibl'); ibl_name = opt('--ibl-name', 'car_studio01')
    cam_json = opt('--cam-json')

    T0 = dict(a=os.path.join(texdir, '010_a.png'), bm=os.path.join(texdir, '010_b_m.png'),
              n=os.path.join(texdir, '010_n.png'))
    T1 = dict(a=os.path.join(texdir, '012_a.png'), bm=os.path.join(texdir, '012_b_m.png'),
              n=os.path.join(texdir, '012_n.png'))
    BUMP = os.path.join(texdir, 'crystal_bump_n_uvva.png')
    CAUS = os.path.join(texdir, 'crystal_caustic_uvva.png')

    subs_param = []
    if c159 and CP:
        try:
            r = CP.load_asset_materials(c159)
            mats = r[0] if isinstance(r, tuple) else r
            if isinstance(mats, dict):
                subs_param = [mats[k].get('params') or {} for k in sorted(mats, key=lambda z: int(z))]
        except Exception as e:
            print('参数失败', e)
    print('材质块 %d' % len(subs_param))

    P3, uv, idx, meta = MP.parse_mesh2(mesh)
    sub_off = meta['sub_offsets']
    print('顶点 %d 面 %d submesh %d %s' % (P3.shape[0], len(idx), len(sub_off), list(sub_off)))

    # 相机（game_reference ✓）
    CPos = np.array([-14.6129, -2.2747, -1.2894], np.float32)
    CTgt = np.array([0.0602, -0.1842, 0.0986], np.float32)
    CUp = np.array([-0.8246, -0.5572, -0.0982], np.float32)
    FOV = 34.0
    if cam_json and os.path.isfile(cam_json):
        try:
            j = json.loads(open(cam_json, encoding='utf-8').read())
            c = (j.get('camera_presets') or [{}])[0]
            CPos = np.array(c.get('position', CPos), np.float32)
            CTgt = np.array(c.get('target', CTgt), np.float32)
            CUp = np.array(c.get('up', CUp), np.float32)
            FOV = float(c.get('fov', FOV))
        except Exception:
            pass
    fwd = CTgt - CPos; fwd /= np.linalg.norm(fwd)
    rgt = np.cross(fwd, CUp); rgt /= np.linalg.norm(rgt)
    upv = np.cross(rgt, fwd)
    rel = P3 - CPos
    Zc = np.maximum(rel @ fwd, 1e-4)
    fpx = 0.5 * H / math.tan(math.radians(FOV) * 0.5)
    sx = ((rel @ rgt) / Zc * fpx + W / 2).astype(np.int32)
    sy = (H / 2 - (rel @ upv) / Zc * fpx).astype(np.int32)
    print('相机 pos=%s fov=%.1f · 屏幕范围 x[%d,%d] y[%d,%d]' % (CPos, FOV, sx.min(), sx.max(), sy.min(), sy.max()))

    dep = np.full((H, W), 1e18, np.float32)
    uvb = np.zeros((H, W, 2), np.float32)
    nb = np.zeros((H, W, 3), np.float32)
    sb = np.full((H, W), -1, np.int32)
    for si in range(len(sub_off)):
        a0, a1 = sub_off[si]
        t3i = np.nonzero(((idx >= a0) & (idx < a1)).all(1))[0]
        print('  sub%d 面 %d' % (si, len(t3i)))
        for t in t3i:
            ia, ib, ic = idx[t, 0], idx[t, 1], idx[t, 2]
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
            i0, i1, i2 = 1.0 / Zc[ia], 1.0 / Zc[ib], 1.0 / Zc[ic]
            l0, l1, l2 = d1 / area, d2 / area, d0 / area
            den = l0 * i0 + l1 * i1 + l2 * i2
            den = np.where(np.abs(den) < 1e-12, 1e-12, den)
            w0, w1, w2 = l0 * i0 / den, l1 * i1 / den, l2 * i2 / den
            dd = 1.0 / den
            sub = dep[miny:maxy, minx:maxx]; upd = m & (dd < sub)
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
    print('覆盖 %d (%.1f%%)' % (model.sum(), 100 * model.mean()))

    # IBL：★ 按材质块选 cube（游戏 c159 逐块声明 ✓）
    #   块0/4（pbr_weapon）→ qiangpi ✓（暖金 ✓ 均值 0.787,0.916,1.072）
    #   块1-3/5-6（pbr_crystal）→ car_studio01 ✓（暗中性 ✓ 0.320,0.311,0.305）
    ibl_sets = {}
    if SIBL and faces:
        base_faces = os.path.dirname(faces.rstrip('/\\'))
        for nm in ('qiangpi', 'car_studio01'):
            d2 = os.path.join(base_faces, 'faces') if os.path.basename(os.path.normpath(faces)) != 'faces' else faces
            try:
                ibl_sets[nm] = SIBL.load_cube(faces, nm)
            except Exception:
                pass
    print('IBL 可用 cube: %s' % {k: len(v) for k, v in ibl_sets.items()})
    mips = ibl_sets.get(ibl_name) or (SIBL.load_cube(faces, ibl_name) if (SIBL and faces) else None)

    def mips_for(si):
        """★ 游戏 c159 逐块声明：武器块(0/4)→qiangpi · 晶体块→car_studio01 ✓"""
        if si in (0, 4):
            return ibl_sets.get('qiangpi')
        return ibl_sets.get('car_studio01')

    # 贴图缓存（两组 ✓）
    def samp(tex, u, v):
        if tex is None: return np.zeros((len(u), 4), np.float32)
        tx = np.clip((u * (tex.shape[1] - 1)).astype(np.int32), 0, tex.shape[1] - 1)
        ty = np.clip((v * (tex.shape[0] - 1)).astype(np.int32), 0, tex.shape[0] - 1)
        return tex[ty, tx]

    tex_sets = {}
    for k, d in (('010', T0), ('012', T1)):
        tex_sets[k] = {kk: (load_rgba(vv) if vv and os.path.isfile(vv) else None) for kk, vv in d.items()}
        tex_sets[k]['bump'] = load_rgba(BUMP) if os.path.isfile(BUMP) else None
        tex_sets[k]['caustic'] = load_rgba(CAUS) if os.path.isfile(CAUS) else None

    ii = np.nonzero(model)
    order = np.argsort(sb[model], kind='stable')     # 按 submesh 顺序（索引稳定 ✓）
    si_of = sb[model]
    uvm = uvb[model]
    nm = nb[model]
    out = np.zeros((int(model.sum()), 3), np.float32)

    for si in np.unique(si_of):
        m_ = si_of == si
        key = '012' if si <= 3 else '010'
        S = tex_sets[key]
        is_weapon = si in (0, 4)                     # ★ 块0/4 = pbr_weapon ✓
        if is_weapon:
            # ── 武器本体（pbr_weapon ✓）
            #   asm L314: r2 = sample t0(Tex0=s_diffuse ✓) → 本体的色
            base = np.clip(samp(S['a'], uvm[m_, 0], uvm[m_, 1])[..., :3], 0, 1)
            #   asm L346-350 的珍珠 LUT 我们【没有那张贴图】⇒ 按缺处理（不猜 ✗）
            C = base
            #   asm L328-368：法线 → 世界 → 球面UV → 环境；此处按缺省做环境反射 ✓
            Pm = mips_for(si)
            if Pm is not None:
                Nw = nm[m_].astype(np.float32)
                px = np.stack([ii[0][m_], ii[1][m_]], 1)
                xc = (px[:, 1] - W / 2) / fpx; yc = (H / 2 - px[:, 0]) / fpx
                Vw = rgt[None, :] * xc[:, None] + upv[None, :] * yc[:, None] + fwd[None, :]
                Vv = Vw / np.maximum(np.linalg.norm(Vw, axis=1, keepdims=True), 1e-9)
                Rr = 2 * np.sum(Nw * Vv, 1, keepdims=True) * Nw - Vv
                lod = CS.roughness_to_lod(np.full(int(m_.sum()), 0.25, np.float32))
                env = CS.rgbm_env(SIBL.sample_cube(Pm, Rr, lod))
                C = C * env                            # ★ 武器 = 本体色 × 环境（qiangpi 暖金 ✓）
                print('   sub%d 武器本体会用 %s cube ✓（金色来源 ✓）' % (si, 'qiangpi'))
            else:
                C = C * 0.35
            out[m_] = C
            continue
        # ── 晶体件（pbr_crystal ✓）
        base = np.clip(samp(S['bm'], uvm[m_, 0], uvm[m_, 1])[..., :3], 0, 1)   # t0 Tex0 ← b_m ✓
        Tc = samp(S['a'], uvm[m_, 0], uvm[m_, 1])[..., :3]                    # t3 t_basecolor ← a ✓
        det = S['bump']
        d_w = samp(det, uvm[m_, 0], uvm[m_, 1])[..., 3] if det is not None else np.full(int(m_.sum()), 0.5, np.float32)
        uc = np.array((subs_param[si].get('u_crystal_color') or [1, 1, 1])[:3], np.float32) if si < len(subs_param) else np.array([1, 1, 1], np.float32)
        ub = np.array((subs_param[si].get('u_base_color') or [0.5, 0.5, 0.5])[:3], np.float32) if si < len(subs_param) else np.array([0.5, 0.5, 0.5], np.float32)
        C = CS.crystal_color(Tc, base[..., 0], d_w, uc, ub)
        if S['caustic'] is not None:
            ca = samp(S['caustic'], uvm[m_, 0], uvm[m_, 1])
            br = float(subs_param[si].get('u_caustic_brightness') or 0.0) if si < len(subs_param) else 0.0
            C = CS.caustic_add(C, ca[..., :3], br, ca[..., 3])
        Pm = mips_for(si)
        if Pm is not None:
            rough = 0.3
            if si < len(subs_param):
                rough = float(subs_param[si].get('u_crystal_roughness') or subs_param[si].get('u_base_roughness') or 0.3)
            lod = CS.roughness_to_lod(np.full(int(m_.sum()), np.clip(rough, 0.02, 1.0), np.float32))
            Nw = nm[m_].astype(np.float32)
            px = np.stack([ii[0][m_], ii[1][m_]], 1)
            xc = (px[:, 1] - W / 2) / fpx; yc = (H / 2 - px[:, 0]) / fpx
            Vw = rgt[None, :] * xc[:, None] + upv[None, :] * yc[:, None] + fwd[None, :]
            Vv = Vw / np.maximum(np.linalg.norm(Vw, axis=1, keepdims=True), 1e-9)
            Rr = 2 * np.sum(Nw * Vv, 1, keepdims=True) * Nw - Vv
            rot = float(subs_param[si].get('u_rotate_angle') or 0.0) if si < len(subs_param) else 0.0
            if abs(rot) > 1e-8:
                c0, s0 = np.cos(rot), np.sin(rot)
                Rr = np.stack([Rr[:, 0] * c0 + Rr[:, 2] * s0, Rr[:, 1], -Rr[:, 0] * s0 + Rr[:, 2] * c0], 1)
            Sm = SIBL.sample_cube(Pm, Rr, lod)
            env = CS.rgbm_env(Sm)
            env = env * (float(subs_param[si].get('u_cube_brightness') or 1.0) if si < len(subs_param) else 1.0)
            C = CS.env_times_color(env, C)
        else:
            C = C * 0.35
        out[m_] = C

    full = np.zeros((H, W, 3), np.float32)
    full[ii[0], ii[1]] = out
    img = (lin2srgb(full) * 255).astype(np.uint8)
    Image.fromarray(img).save(os.path.join(out_dir, 'dual_game.png'))
    print('✓ → %s' % os.path.join(out_dir, 'dual_game.png'))


if __name__ == '__main__':
    main()
