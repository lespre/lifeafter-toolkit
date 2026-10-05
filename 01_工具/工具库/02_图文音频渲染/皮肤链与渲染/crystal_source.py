"""crystal_source.py — 按【游戏自己的 shader 汇编】实现的晶体/武器着色
唯一依据：03_执行/30_分析/render_1003_010/_game_shader_db/pipes/
          d11_deferred_quality2_shader_pbr_crystal.nfx2_01393c07_b2d62c97_d11.pipe_blob1_blob.asm
          （游戏自带 D3DCompiler_47 反汇编 ✓）
每条都标了汇编行号；没有汇编依据的一律不做（宁缺不编 ✓）。

Shader 绑定（asm L260-266 ✓）：
  t0 Tex0(形状) t1 NormalMap t2 DetailMap t3 t_basecolor
  t4 t_caustic_tex t5 t_refraction_tex t6 t_custom_ibl(cube)

UBO NeoxUBOLocal 偏移（asm 头部 ✓）：
  48 u_base_color · 64 u_crystal_color · 80 u_refraction_color · 96 u_subsurface_color
  140 u_emissive_strength · 144 u_emissive_fresnel
  148 u_rotate_angle · 152 u_cube_brightness · 156 u_base_roughness
  160 u_base_metallic · 164 u_crystal_metallic · 168 u_base_specular · 172 u_crystal_specular
  176 u_caustic_tilling · 180 u_caustic_depth · 184 u_caustic_brightness
  188 u_refraction_rotation · 192 u_refraction_contrast
  196 u_refraction_mipmap · 200 u_refraction_brightness · 204 u_refraction_opacity
"""
import numpy as np

CB = {  # 名字 → NeoxUBOLocal 偏移
    'u_base_color': 48, 'u_crystal_color': 64, 'u_refraction_color': 80,
    'u_subsurface_color': 96, 'u_emissive_color_saturation': 32,
    'u_emissive_strength': 140, 'u_emissive_fresnel': 144,
    'u_rotate_angle': 148, 'u_cube_brightness': 152,
    'u_base_roughness': 156, 'u_base_metallic': 160, 'u_crystal_metallic': 164,
    'u_base_specular': 168, 'u_crystal_specular': 172,
    'u_caustic_tilling': 176, 'u_caustic_depth': 180, 'u_caustic_brightness': 184,
    'u_refraction_rotation': 188, 'u_refraction_contrast': 192,
    'u_refraction_mipmap': 196, 'u_refraction_brightness': 200,
    'u_refraction_opacity': 204,
}


def crystal_color(T, tex0_r, detail_w, uc, ub):
    """L382-391 ✓ 逐行：
       r8 = lerp(T, T*uc, m)            L382-383（mad/mad）
       r7 = lerp(ub, T*uc, d)           L388-389
       C  = lerp(r8, r7, m)             L390-391
    T: sampler t3(t_basecolor) 采样 · tex0_r: saturate(Tex0.r)（= m）
    detail_w: detail 通道（= d）· uc=u_crystal_color · ub=u_base_color
    """
    T = np.asarray(T, np.float32)
    uc = np.asarray(uc, np.float32)
    ub = np.asarray(ub, np.float32)
    m = np.asarray(tex0_r, np.float32)
    d = np.asarray(detail_w, np.float32)
    if m.ndim == 1 and T.ndim == 2:                 # ★ 升维广播 ✓
        m = m[:, None]
    if d.ndim == 1 and T.ndim == 2:
        d = d[:, None]
    r8 = T + m * (T * uc - T)                       # lerp(T, T*uc, m)
    r7 = ub + d * (T * uc - ub)                     # lerp(ub, T*uc, d)
    return r8 + m * (r7 - r8)                       # lerp(r8, r7, m)


def caustic_add(C, caustic_rgb, u_caustic_brightness, w):
    """L416-418 ✓：r1 = sample(t4) * cb0[11].z(u_caustic_brightness)
       mad r1.xyz, r1.xyzx, r1.wwww, r7.xyzx  ⇒ C += caustic * w
    ★ 注意：汇编那行用的是 r1.w（caustic 采样的 alpha）作权重 ✓
    """
    rgb = np.asarray(caustic_rgb, np.float32)
    wv = np.asarray(w, np.float32)
    if wv.ndim == 1 and rgb.ndim == 2:
        wv = wv[:, None]
    return np.asarray(C, np.float32) + rgb * float(u_caustic_brightness) * wv


def roughness_to_lod(rough):
    """L533-535 ✓：log r0.w · ×1.2 · ... ⇒ LOD = 5 + 1.2*log2(rough)"""
    r = np.maximum(np.asarray(rough, np.float32), 0.0019)
    return 5.0 + 1.2 * np.log2(r)


def rgbm_env(cube_sample):
    """L538-544 ✓：(rgb*a*16)^2 → min(1.5) → lerp(C, C*0.299805, lightmap)"""
    S = np.asarray(cube_sample, np.float32)
    C = (S[..., :3] * S[..., 3:4] * 16.0) ** 2
    C = np.minimum(C, 1.5)
    return C


def lightmap_mix(C, u_lightmap_factor):
    """L542-544 ✓：mad_sat(cb1[86].z) ⇒ lm；lerp(C, C*0.299805, lm)"""
    lm = float(np.clip(u_lightmap_factor, 0.0, 1.0))
    return C + lm * (C * 0.299805 - C)


def f0_from_base(base_rgb, metal):
    """L501-503 ✓：mul 0.079956 · mad（-metal*0.079956 + base）· mad（m*that + 0.079956*metal）
       ⇒ F0 = lerp(0.079956, base, metal)"""
    m = np.clip(np.asarray(metal, np.float32), 0.0, 1.0)
    if m.ndim == 0:
        return 0.079956 + m * (np.asarray(base_rgb, np.float32) - 0.079956)
    return 0.079956 + m[..., None] * (np.asarray(base_rgb, np.float32) - 0.079956)


def env_times_color(env_rgb, C):
    """L545-546 ✓：env *= cb1[239].x(u_env_day2night_exposure) ⇒ 再 mul r6.yzw, r12.xyz, r6.yzw
       ⇒ ★ 最终 = 环境项 × 晶体色（不是相加 ✓）"""
    return np.asarray(env_rgb, np.float32) * np.asarray(C, np.float32)


def refraction_uv(R, rotation_rad):
    """★ 从【游戏汇编】还原的折射 UV（L433-468 的 atan2/asin 展开 ✓）：
       L468 行：u = atan2(R.y, R.x) / (2π) + 0.5   （×0.159155 = 1/2π ✓）
                v = asin(R.z)      / π     + 0.5   （×0.318310 = 1/π  ✓）
       L423 行：先把方向绕 u_refraction_rotation×2π 旋转 ✓
       R: (N,3) 方向（通常=反射方向 ✓ 归一化 ✓）
    """
    R = np.asarray(R, np.float32)
    if abs(rotation_rad) > 1e-8:
        ang = rotation_rad * 2.0 * np.pi                     # L423 ✓
        c, s = np.cos(ang), np.sin(ang)
        R = np.stack([R[:, 0] * c - R[:, 1] * s,
                      R[:, 0] * s + R[:, 1] * c,
                      R[:, 2]], 1)
    Rn = R / np.maximum(np.linalg.norm(R, axis=1, keepdims=True), 1e-9)
    x, y, z = Rn[:, 0], Rn[:, 1], Rn[:, 2]
    u = np.arctan2(y, x) * (1.0 / (2.0 * np.pi)) + 0.5        # L468 ✓ 0.159155
    v = np.arcsin(np.clip(z, -1.0, 1.0)) * (1.0 / np.pi) + 0.5  # L468 ✓ 0.318310
    return np.stack([u, v], 1)


def sample_bilinear(tex, uv):
    """双线性采样（tex: (H,W,C) float [0,1] ✓ · uv: (N,2) ✓）"""
    if tex is None:
        return None
    H_, W_ = tex.shape[0], tex.shape[1]
    x = np.clip(uv[:, 0] * (W_ - 1), 0, W_ - 1)
    y = np.clip(uv[:, 1] * (H_ - 1), 0, H_ - 1)
    x0 = np.floor(x).astype(np.int32); y0 = np.floor(y).astype(np.int32)
    x1 = np.minimum(x0 + 1, W_ - 1); y1 = np.minimum(y0 + 1, H_ - 1)
    fx = (x - x0)[:, None]; fy = (y - y0)[:, None]
    t = tex[y0, x0] * (1 - fx) + tex[y1, x0] * fx
    b = tex[y0, x1] * (1 - fx) + tex[y1, x1] * fx
    return t * (1 - fy) + b * fy


def crystal_finish(C, refr_sample, refr_color, refr_contrast, refr_brightness,
                   emissive_sat, emissive_fresnel, emissive_strength, alpha_C,
                   scene_exposure=1.0):
    """★ pbr_crystal PS 收尾段（汇编 L470-487 ✓ 逐行）：
       L473-477 折射项 = sat-ish(r_x × (1+contrast) − contrast) × brightness × u_refraction_color
                        × C 的某通道（r4.z ✓）
       L480-481 r8 = lerp(r1, u_emissive_color_saturation, sat.w)
                  （r1 = 已被 caustic 加过的色 ✓ 即传入的 C ✓）
       L482-486 r8 *= (1 + u_emissive_fresnel × (r6.x − 1)) × alpha
                 r8 = r8 × u_emissive_strength + r7
       L487     r8 /= scene_exposure
    """
    C = np.asarray(C, np.float32)
    cnt = float(refr_contrast)
    br = float(refr_brightness)
    sat = np.asarray(emissive_sat, np.float32)[:3]
    # L480-481：lerp(C, u_emissive_color_saturation, .w)
    w_sat = float(np.asarray(emissive_sat, np.float32)[3]) if np.asarray(emissive_sat).size > 3 else 0.0
    r8 = C + w_sat * (sat - C)
    # L473-477：折射项
    if refr_sample is not None:
        rs = np.asarray(refr_sample, np.float32)
        k = np.clip(rs[:, 0] * (1.0 + cnt) - cnt, 0.0, 1.0)          # L473-475 ✓
        r7 = (k * br)[:, None] * np.asarray(refr_color, np.float32)[:3][None, :]   # L476-477 ✓
        r7 = r7 * rs[:, 2:3]                                          # L479（r4.z 权重 ✓）
    else:
        r7 = np.zeros_like(C)
    # L482-483：菲涅尔增益
    fr = 1.0 + float(emissive_fresnel) * (np.asarray(alpha_C, np.float32) - 1.0)
    # L484-485
    r8 = r8 * (fr * np.asarray(alpha_C, np.float32))[:, None] if fr.ndim else r8 * fr
    # L486
    r8 = r8 * float(emissive_strength) + r7
    # L487
    if scene_exposure and scene_exposure != 1.0:
        r8 = r8 / float(scene_exposure)
    return r8
