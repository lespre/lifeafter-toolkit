# -*- coding: utf-8 -*-
"""render_layers_multiset.py — 多材质集分层渲染器 v1.0（通用: 变长子网格 + 每子网格按材质名配贴图集）
背景: 合体网格(如 skin_1003_010+012 双枪)的子网格分属不同皮肤的材质/贴图集。
能力:
  · mesh_parse2 解析(N 子网格, 含顶点色流探测);
  · c159_pair 自动解析多材质参数; shader 含 crystal 的子网格走晶体路径(基色=该集 b_m), 其余走武器路径(基色=该集 a);
  · --tex-map JSON: 按材质名前缀(如 skin_1003_010 / skin_1003_012)绑定贴图集 {a,n,m,s_m,b_m};
  · 输出 8 层图 + trace.json + provenance.json(统一溯源: 全部消费贴图逐一锚定 + 语义单独记录 + fail-closed)。
用法:
  python render_layers_multiset.py <mesh> <texmap.json> <out_dir> --materials <c159> [--eye X,Y,Z] [--roll deg] [--flip-h] [--size WxH] [--skip-provenance]
"""
import sys, os, json, math, time, hashlib
import numpy as np
from PIL import Image
import mesh_parse2 as MP

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
    tx = np.clip((np.remainder(u, 1.0) * (tex.shape[1] - 1)).astype(np.int32), 0, tex.shape[1] - 1)
    ty = np.clip((np.remainder(v, 1.0) * (tex.shape[0] - 1)).astype(np.int32), 0, tex.shape[0] - 1)
    return tex[ty, tx]

def sha_p(p):
    try:
        return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
    except Exception:
        return None

def main():
    args = sys.argv[1:]
    mesh, texmap_p, out_dir = args[0], args[1], args[2]
    mat_path = args[args.index('--materials') + 1] if '--materials' in args else None
    eye = tuple(float(x) for x in args[args.index('--eye') + 1].split(',')) if '--eye' in args else (1.0, 0.0, 0.0)
    roll = float(args[args.index('--roll') + 1]) if '--roll' in args else 55.0
    flip = '--flip-h' in args
    W, H = (2260, 1150)
    if '--size' in args:
        W, H = [int(x) for x in args[args.index('--size') + 1].split('x')]
    os.makedirs(out_dir, exist_ok=True)
    texmap = json.load(open(texmap_p, encoding='utf-8'))
    sets = texmap.get('sets', {})
    default_set = texmap.get('default')

    # 材质
    sub_params, mat_meta, mat_names, mat_shaders = {}, None, [], []
    if mat_path:
        import c159_pair as CP
        mats, meta = CP.load_asset_materials(mat_path)
        sub_params = {int(k): (v.get('params') or {}) for k, v in mats.items()}
        mat_meta = dict(file=os.path.abspath(mat_path), bind=meta.get('bind_file'),
                        materials=meta.get('materials'), shaders=meta.get('shaders'))
        mat_names = meta.get('materials') or []
        mat_shaders = meta.get('shaders') or []
    def P(si, name, dflt):
        v = sub_params.get(si, {}).get(name)
        if v is None: return dflt
        if isinstance(v, list): return tuple(float(x) for x in v[:3])
        return float(v)
    def set_for(si):
        nm = mat_names[si] if si < len(mat_names) else ''
        prefix = nm.rsplit('_', 1)[0] if nm else ''
        st = sets.get(prefix) or default_set
        return st, prefix

    # 网格
    P3, uv, faces, meta = MP.parse_mesh2(mesh)
    nsub = len(meta['subs'])
    c = (P3.min(0) + P3.max(0)) / 2.0; p = P3 - c
    e = np.array(eye, np.float32); e /= np.linalg.norm(e)
    up0 = np.array([0, 0, 1.0], np.float32)
    if abs(float(np.dot(up0, e))) > 0.9: up0 = np.array([0, 1.0, 0], np.float32)
    r0 = np.cross(up0, e); r0 /= np.linalg.norm(r0)
    u0 = np.cross(e, r0); u0 /= np.linalg.norm(u0)
    sx = p @ r0; sy = p @ u0; dep = p @ e
    a = math.radians(roll)
    Rr = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
    s = Rr @ np.stack([sx, sy]); sxx, syy = s[0], s[1]
    if flip: sxx = -sxx
    Mg = 60
    sc = min((W-2*Mg)/(sxx.max()-sxx.min()), (H-2*Mg)/(syy.max()-syy.min()))
    cx = (sxx.max()+sxx.min())/2; cy = (syy.max()+syy.min())/2
    vx = (sxx-cx)*sc + W/2; vy = H/2 - (syy-cy)*sc
    vd = dep.copy()

    Nsm = _smooth_welded(P3, faces)
    f0, f1, f2 = faces[:, 0], faces[:, 1], faces[:, 2]
    dP1 = P3[f1]-P3[f0]; dP2 = P3[f2]-P3[f0]
    du1 = uv[f1]-uv[f0]; du2 = uv[f2]-uv[f0]
    det = du1[:, 0]*du2[:, 1] - du2[:, 0]*du1[:, 1]
    safe = np.abs(det) > 1e-12
    rr = np.where(safe, 1.0/np.where(safe, det, 1.0), 0.0)
    Tf = (dP1*du2[:, 1:2] - dP2*du1[:, 1:2])*rr[:, None]
    Bf = (dP2*du1[:, 0:1] - dP1*du2[:, 0:1])*rr[:, None]
    Nf = (Nsm[f0]+Nsm[f1]+Nsm[f2])/3.0
    Nf /= np.maximum(np.linalg.norm(Nf, axis=1, keepdims=True), 1e-9)
    Tf = Tf - Nf*np.sum(Tf*Nf, axis=1, keepdims=True)
    tn = np.linalg.norm(Tf, axis=1, keepdims=True)
    Tf = np.where(tn > 1e-9, Tf/np.maximum(tn, 1e-9), np.array([1.0, 0, 0], np.float32))
    Bf = np.cross(Nf, Tf)

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
        minx = max(int(min(x0, x1, x2)), 0); maxx = min(int(max(x0, x1, x2))+1, W)
        miny = max(int(min(y0, y1, y2)), 0); maxy = min(int(max(y0, y1, y2))+1, H)
        if maxx <= minx or maxy <= miny: continue
        gx, gy = np.meshgrid(np.arange(minx, maxx)+0.5, np.arange(miny, maxy)+0.5)
        d0 = (x1-x0)*(gy-y0)-(y1-y0)*(gx-x0); d1 = (x2-x1)*(gy-y1)-(y2-y1)*(gx-x1); d2 = (x0-x2)*(gy-y2)-(y0-y2)*(gx-x2)
        m = ((d0 >= 0) & (d1 >= 0) & (d2 >= 0)) | ((d0 <= 0) & (d1 <= 0) & (d2 <= 0))
        if not m.any(): continue
        area = d0+d1+d2
        w0 = d1/area; w1 = d2/area; w2 = d0/area
        dd = w0*vd[fa]+w1*vd[fb]+w2*vd[fc]
        sub = zb[miny:maxy, minx:maxx]; upd = m & (dd > sub)
        if not upd.any(): continue
        uu = w0*uv[fa, 0]+w1*uv[fb, 0]+w2*uv[fc, 0]
        vv = w0*uv[fa, 1]+w1*uv[fb, 1]+w2*uv[fc, 1]
        nn = (w0[..., None]*Nsm[fa]+w1[..., None]*Nsm[fb]+w2[..., None]*Nsm[fc])
        nn /= np.maximum(np.linalg.norm(nn, axis=2, keepdims=True), 1e-6)
        si = int(sub_of[fa])
        submap[miny:maxy, minx:maxx][upd] = si
        uvmap[miny:maxy, minx:maxx][upd] = np.stack([uu, vv], -1)[upd]
        nrmmap[miny:maxy, minx:maxx][upd] = nn[upd]
        fmap[miny:maxy, minx:maxx][upd] = t
        sub[upd] = dd[upd]

    # 图层
    def blank(): return np.zeros((H, W, 3), np.float32)
    L_base = blank(); L_refl = blank(); L_refr = blank(); L_sss = blank(); L_fres = blank(); L_diff = blank()
    L_gloss = np.zeros((H, W), np.float32); L_norm = np.zeros((H, W, 3), np.float32)
    model = submap >= 0
    K = np.array(RIG['key_dir'], np.float32); K /= np.linalg.norm(K)
    F = np.array(RIG['fill_dir'], np.float32); F /= np.linalg.norm(F)
    Vdir = -e
    tex_cache = {}
    def tex_of(st, slot, srgb=True):
        key = (st.get(slot), srgb)
        if key not in tex_cache:
            t = as_rgba(st[slot])
            tex_cache[key] = srgb2lin(t[..., :3]) if srgb else t
        return tex_cache[key]
    for si in range(nsub):
        m = submap == si
        if not m.any(): continue
        st, prefix = set_for(si)
        is_crystal = 'crystal' in (mat_shaders[si].lower() if si < len(mat_shaders) else '')
        uvm = uvmap[m]; nm_ = nrmmap[m]; fidm = fmap[m]
        Tm = Tf[fidm]; Bm = Bf[fidm]; Nm = Nf[fidm]
        texb = tex_of(st, 'b_m' if is_crystal else 'a')
        base_srgb = samp(texb, uvm[:, 0], uvm[:, 1])[..., :3]
        base = base_srgb * np.array(P(si, 'u_base_color', (1.0, 1.0, 1.0)), np.float32)
        chg = samp(tex_of(st, 'n', srgb=False), uvm[:, 0], uvm[:, 1])
        # 规范 RGBA：法线在 R,G 通道（原 (1,2) 为 BGRA 误读，2026-09-15 修正）
        nx = (chg[:, 0]*2-1); ny = (chg[:, 1]*2-1)
        d2 = nx*nx+ny*ny
        nz = np.sqrt(np.clip(1.0-d2, 0.0, 1.0))
        nw = Tm*nx[:, None]+Bm*ny[:, None]+Nm*nz[:, None]
        nw /= np.maximum(np.linalg.norm(nw, axis=1, keepdims=True), 1e-6)
        L_norm[m] = nw*0.5+0.5
        # 规范 RGBA：遮罩取 R 通道（原 [:,2] 为 BGRA 误读；旧称 m.B=gloss 已撤销）
        g = samp(tex_of(st, 'm', srgb=False), uvm[:, 0], uvm[:, 1])[:, 0]
        L_gloss[m] = g
        ndv = np.abs(np.sum(nw*Vdir[None, :], axis=1))
        ndl_k = np.maximum(np.sum(nw*K[None, :], axis=1), 0)
        ndl_f = np.maximum(np.sum(nw*F[None, :], axis=1), 0)
        hv = (K+Vdir); hv /= np.linalg.norm(hv)
        ndh = np.maximum(np.sum(nw*hv[None, :], axis=1), 0)
        metal = P(si, 'u_crystal_metallic', P(si, 'u_base_metallic', 1.0)) if is_crystal else 1.0
        refl_tint = np.array(P(si, 'u_crystal_color', (1.0, 1.0, 1.0)), np.float32) if is_crystal else base
        F0 = np.clip(refl_tint, 0, 1)*metal + 0.04*(1-metal)
        fres = F0[None, :] + (1-F0[None, :])*((1-ndv)**5)[:, None]
        spec_pow = RIG['spec_pow_lo'] + (RIG['spec_pow_hi']-RIG['spec_pow_lo'])*(g**2)
        spec = (ndh**spec_pow)*RIG['spec_str']
        env = np.array(RIG['env_col'], np.float32)*RIG['env_int']
        refl = fres*env[None, :]*(0.5+0.5*ndv[:, None])
        refl += spec[:, None]*(np.array(RIG['key_col'], np.float32)*RIG['key_int'])[None, :]
        refl += ((ndh**spec_pow)*0.4)[:, None]*(np.array(RIG['fill_col'], np.float32)*RIG['fill_int'])[None, :]
        refr_c = np.array(P(si, 'u_refraction_color', (0.0, 0.0, 0.0)), np.float32)
        refr_b = P(si, 'u_refraction_brightness', 0.0)
        refr_k = float(np.clip(refr_b/5.0, 0.0, 1.0))*0.65
        refr = refr_c[None, :]*(refr_k*(0.45+0.55*ndv))[:, None]
        sss_c = np.array(P(si, 'u_subsurface_color', (0.0, 0.0, 0.0)), np.float32)
        sss_kx = RIG['sss_k'] if not is_crystal else RIG['sss_k_crystal']
        sss = sss_c[None, :]*(sss_kx*(0.35+0.65*ndl_k))[:, None]
        fk = P(si, 'u_emissive_fresnel', RIG['fres_k_default'])
        fs = P(si, 'u_emissive_strength', 1.0) if 'u_emissive_strength' in sub_params.get(si, {}) else 0.5
        fres_term = fk*(0.5+0.5*float(np.clip(fs/2.0, 0, 1)))*((1-ndv)**3)
        kd = 1.0 if not is_crystal else RIG['crystal_diffuse']
        diff = base*kd*(RIG['ambient'] + RIG['key_int']*ndl_k[:, None]*np.array(RIG['key_col'], np.float32)[None, :]
                        + RIG['fill_int']*0.6*ndl_f[:, None]*np.array(RIG['fill_col'], np.float32)[None, :])
        L_base[m] = np.clip(base, 0, 1)
        L_diff[m] = np.clip(diff, 0, None)
        L_refl[m] = np.clip(refl, 0, None)
        L_refr[m] = np.clip(refr, 0, None)
        L_sss[m] = np.clip(sss, 0, None)
        L_fres[m] = np.clip(fres_term[:, None], 0, None)
    comp = np.clip(L_diff+L_refl+L_refr+L_sss+L_fres, 0, 1)

    def save3(name, arr, srgb=True):
        aa = lin2srgb(np.clip(arr, 0, 1)) if srgb else np.clip(arr, 0, 1)
        Image.fromarray((aa*255).astype(np.uint8)).save(os.path.join(out_dir, name))
    save3('BaseColor.png', L_base)
    save3('Normal.png', L_norm, srgb=False)
    Image.fromarray((np.clip(L_gloss, 0, 1)*255).astype(np.uint8)).save(os.path.join(out_dir, 'Gloss.png'))
    save3('Reflection.png', L_refl); save3('Refraction.png', L_refr)
    save3('Subsurface.png', L_sss); save3('Fresnel.png', L_fres)
    save3('Composite_noSFX.png', comp)

    trace = dict(generator='render_layers_multiset.py v1.0', time=time.strftime('%Y-%m-%d %H:%M:%S'),
                 mesh=os.path.abspath(mesh), mesh_sha=sha_p(mesh),
                 materials=mat_meta, texmap=os.path.abspath(texmap_p),
                 eye=list(eye), roll=roll, flip_h=flip, rig=RIG,
                 nsub=nsub, sub_flags=[hex(u) for u in meta['flags']], vcol=bool(meta.get('vcol') is not None),
                 per_sub=[dict(si=k, material=(mat_names[k] if k < len(mat_names) else None),
                               shader=(mat_shaders[k] if k < len(mat_shaders) else None),
                               set_prefix=set_for(k)[1],
                               params={kk: vv for kk, vv in sub_params.get(k, {}).items()
                                       if kk in ('u_crystal_color', 'u_refraction_color', 'u_subsurface_color', 'u_base_color')})
                          for k in range(nsub)],
                 approximations=['观察 rig=固定常数', '层强度常数', 's_m 贴图语义未定未接入', '顶点色(掩码+alpha)未接入'])
    json.dump(trace, open(os.path.join(out_dir, 'layers_trace.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    # 统一 provenance
    if '--skip-provenance' not in args:
        import raw_anchor as RA
        consumed = []
        for si in range(nsub):
            st, prefix = set_for(si)
            is_crystal = 'crystal' in (mat_shaders[si].lower() if si < len(mat_shaders) else '')
            for slot in (('b_m', 'n', 'm') if is_crystal else ('a', 'n', 'm')):
                gp = st.get(slot + ('' if slot != 'a' else ''))
                gp = st.get(slot)
                if gp and gp not in [c['file'] for c in consumed]:
                    consumed.append(dict(file=gp, slot=slot, set=prefix, src=st.get('sources', {}).get(slot)))
        checks = []
        for c_ in consumed:
            if c_['src']:
                checks.append(RA.verify_texture_vs_declared(c_['file'], c_['src']))
            else:
                checks.append(dict(file=os.path.basename(c_['file']), declared=False, match=False,
                                   reason='未声明来源', norm_path=os.path.normcase(os.path.abspath(c_['file']))))
        bad = [t['file'] for t in checks if t.get('match') is not True]
        prov = dict(
            run_id=time.strftime('%Y%m%d_%H%M%S') + '_MS',
            mode='multiset-layered',
            script_hashes={'multiset': sha_p(__file__), 'parser2': sha_p(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mesh_parse2.py'))},
            inputs=dict(mesh=os.path.abspath(mesh), mesh_sha=sha_p(mesh),
                        c159=os.path.abspath(mat_path) if mat_path else None,
                        c159_sha=sha_p(mat_path) if mat_path else None,
                        texmap=os.path.abspath(texmap_p)),
            source_data_integrity=dict(pass_=(len(bad) == 0),
                                       checks={'textures': checks, 'manual_flags': {'v19_used': False, 'tint_map_used': False,
                                               'face_overrides_used': False, 'edgeface_used': False, 'band_used': False, 'post_executed': False}},
                                       reasons=(['贴图未通过锚定: ' + ','.join(bad)] if bad else [])),
            texture_semantics=dict(note='贴图语义=内容签名+跨皮肤位置模板判定(非名字级地面真值); 字节来源与语义分开记录',
                                   consumed=consumed),
            shader_fidelity=dict(status='approximate',
                                 reasons=['观察 rig=固定 studio 常数(非源 IBL)', '层强度常数', '刃口/菲涅尔近似', 's_m 未接入', '顶点色未接入']),
            presentation=dict(eye=list(eye), roll=roll, flip_h=flip,
                              presentation_fidelity='reference_aligned',
                              fidelity_note='相机由参考图选择(reference_aligned); 非源展示位还原(source_matched); 面选择(-X正面)与面内旋转为独立变量',
                              note='多材质集合体网格直渲(无镜像组合); 相机轴按轮廓配准选定'),
        )
        json.dump(prov, open(os.path.join(out_dir, 'provenance.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('provenance integrity:', prov['source_data_integrity']['pass_'])
    print('MULTISET DONE ->', out_dir)

def _smooth_welded(P, faces, tol=0.005):
    """焊接平滑法线(按位置合并)"""
    key = np.round(P / tol).astype(np.int64)
    uniq, inv = np.unique(key, axis=0, return_inverse=True)
    N = np.zeros((len(uniq), 3), np.float64)
    fn = np.cross(P[faces[:, 1]] - P[faces[:, 0]], P[faces[:, 2]] - P[faces[:, 0]])
    for k in range(3):
        np.add.at(N, inv[faces[:, k]], fn)
    ln = np.linalg.norm(N, axis=1, keepdims=True)
    N = N / np.maximum(ln, 1e-12)
    return N[inv].astype(np.float32)

if __name__ == '__main__':
    main()
