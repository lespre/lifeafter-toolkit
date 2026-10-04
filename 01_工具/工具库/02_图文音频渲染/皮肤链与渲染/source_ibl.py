"""source_ibl.py — 源 IBL（游戏内环境反射）实现
规格来源：00_治理/文档/报告与复盘/_1110171_结论归档/ENV_IBL_spec_1110171_1110177_20260919.md
          与 RX_CRYSTAL_spec_1110171_1110177_20260919.md（全部有 DXBC 汇编级证据）

要点（逐条对应汇编）：
  · LOD = 5 + 1.2·log2(max(rough, 0.0019))          asm L520-522
  · RGBM 解码 = (rgb·a·16)²                          asm L525-527
  · min(·, 1.5)                                      asm L528
  · lightmap 混合 = lerp(C, min(C,1.5)·0.299805, sat(u_lightmap_factor))  viewer L1369
  · cube 采样属性 = UNORM（不 sRGB）+ ClampToEdge    规格 §3
  · 旋转 = u_rotate_angle（晶体 cb0[7].w）；亮度 = u_cube_brightness（cb0[8].x）
"""
import numpy as np
from PIL import Image
from pathlib import Path

def load_cube(faces_dir, name, max_mip=8):
    """读 <name>_f{0..5}_m{0..max_mip-1}.png → list[mip] = (6, H, W, 4) float32 [0,1] (RGBM 原样 ✓ 不解码)"""
    mips = []
    for m in range(max_mip):
        faces = []
        ok = True
        for f in range(6):
            p = Path(faces_dir) / ('%s_f%d_m%d.png' % (name, f, m))
            if not p.is_file():
                ok = False; break
            a = np.asarray(Image.open(p).convert('RGBA'), np.float32) / 255.0
            faces.append(a)
        if not ok:
            break
        arr = np.stack(faces, 0)                      # (6,H,W,4)
        if mips and arr.shape[1] != mips[-1].shape[1] // 2 and mips[-1].shape[1] > 1:
            pass
        mips.append(arr)
    return mips

def _face_uv(D):
    """方向 (N,3) → (face(6 选 1), u, v in [0,1])  GL 立方图约定"""
    ax = np.argmax(np.abs(D), axis=1)
    ma = np.take_along_axis(D, ax[:, None], 1)[:, 0]
    s = np.where(ma >= 0, 1.0, -1.0)
    x, y, z = D[:, 0], D[:, 1], D[:, 2]
    u = np.zeros_like(x); v = np.zeros_like(x); face = np.zeros(len(x), np.int32)
    # +X, -X, +Y, -Y, +Z, -Z  （与 three CubeTexture 加载顺序一致）
    m0 = ax == 0
    face[m0] = np.where(s[m0] > 0, 0, 1)
    u[m0] = np.where(s[m0] > 0, -z[m0], z[m0]) / np.abs(np.where(s[m0] > 0, x[m0], x[m0]))
    v[m0] = -y[m0] / np.abs(x[m0]) if False else -y[m0] / np.maximum(np.abs(x[m0]), 1e-9)
    m1 = ax == 1
    face[m1] = np.where(s[m1] > 0, 2, 3)
    u[m1] = x[m1] / np.maximum(np.abs(y[m1]), 1e-9)
    v[m1] = np.where(s[m1] > 0, -z[m1], z[m1]) / np.maximum(np.abs(y[m1]), 1e-9)
    m2 = ax == 2
    face[m2] = np.where(s[m2] > 0, 4, 5)
    u[m2] = np.where(s[m2] > 0, x[m2], -x[m2]) / np.maximum(np.abs(z[m2]), 1e-9)
    v[m2] = -y[m2] / np.maximum(np.abs(z[m2]), 1e-9)
    return face, (u * 0.5 + 0.5), (v * 0.5 + 0.5)

def sample_cube(mips, D, lod):
    """D:(N,3) 方向 · lod:(N,) 连续 mip ⇒ 返回 (N,4) RGBM 原值（未解码 ✓）"""
    face, u, v = _face_uv(D)
    out = np.zeros((len(D), 4), np.float32)
    nl = np.clip(np.round(lod).astype(np.int32), 0, len(mips) - 1)
    for L in np.unique(nl):
        sel = nl == L
        cub = mips[L]                        # (6,H,W,4)
        H, W = cub.shape[1], cub.shape[2]
        x = np.clip((u[sel] * W - 0.5), 0, W - 1)
        y = np.clip((v[sel] * H - 0.5), 0, H - 1)
        x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int)
        x1 = np.minimum(x0 + 1, W - 1); y1 = np.minimum(y0 + 1, H - 1)
        fx = (x - x0)[:, None]; fy = (y - y0)[:, None]
        f = face[sel]
        def g(xx, yy):
            return cub[f, yy, xx]            # (n,4)
        top = g(x0, y0) * (1 - fx) + g(x1, y0) * fx
        bot = g(x0, y1) * (1 - fx) + g(x1, y1) * fx
        out[sel] = top * (1 - fy) + bot * fy
    return out

def ibl_radiance(mips, N, V, rough, brightness=1.0, rotate_rad=0.0,
                 lightmap_factor=0.0, env_scale=1.0):
    """返回 (N,3) 环境辐射（已 RGBM 解码 + min1.5 + lightmap ✓），线性空间"""
    N = np.asarray(N, np.float32)
    if N.ndim == 1:
        N = N[None, :]
    N = N / np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-9)
    V = np.asarray(V, np.float32)
    if V.ndim == 1:                                    # ★ 视角向量常是 1 维（全场一致）⇒ 广播 ✓
        V = np.broadcast_to(V[None, :], N.shape).copy()
    V = V / np.maximum(np.linalg.norm(V, axis=1, keepdims=True), 1e-9)
    rough = np.asarray(rough, np.float32)
    if rough.ndim == 0:
        rough = np.full(len(N), float(rough), np.float32)
    R = 2 * np.sum(N * V, 1, keepdims=True) * N - V        # reflect(-V,N) ✓
    if abs(rotate_rad) > 1e-8:                              # 绕 Y 旋转（规格 L515-519 ✓）
        c, s = np.cos(rotate_rad), np.sin(rotate_rad)
        Rx = R[:, 0] * c + R[:, 2] * s
        Rz = -R[:, 0] * s + R[:, 2] * c
        R = np.stack([Rx, R[:, 1], Rz], 1)
    lod = 5.0 + 1.2 * np.log2(np.maximum(np.asarray(rough, np.float32), 0.0019))   # ✓
    S = sample_cube(mips, R, lod)                                                 # (N,4)
    C = (S[:, :3] * S[:, 3:4] * 16.0) ** 2                                        # RGBM ✓
    C = np.minimum(C, 1.5)                                                        # ✓
    if lightmap_factor > 0:                                                       # ✓
        C = C * (1 - lightmap_factor) + np.minimum(C, 1.5) * 0.299805 * lightmap_factor
    return C * float(brightness) * float(env_scale)
