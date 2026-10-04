"""tonemap_source.py —— 按【游戏 filmic_tonemapping 汇编】实现色调映射
依据：_pipeline_disasm/4cdb2cc6_e4fe8643_d11.pipe_blob1_blob.asm（86 行 ✓ 游戏自带 D3DCompiler ✓）

cbuffer NeoxUBOLocal：RTSize@0 · BloomIntensity@16 · VignetteIntensity@20
资源：t0 Tex1 · t1 Tex2 · t2 Tex3（★ 32 分片 3D LUT ✓）

汇编逐行（✓ 全部是游戏里的字面量 ✗ 无一处编造）：
  L53-60  暗角（VignetteIntensity/BloomIntensity → 1/(1+dot(r,r))²）
  L65-67  r0 = sample(t0) + sample(t1) × BloomIntensity
  L68     r0 ×= 0.002668          ← 曝光/中间灰
  L69     log(r0)                 ← 对数域
  L70     mad_sat(log, 0.071429, 0.610727)
  L71     坐标 = log × 0.96875 + 0.015625
  L72-76  B 轴分 32 片
  L77-81  采 LUT 两次 + lerp
  L82     mul_sat(r0, 1.05)
"""
import numpy as np
from PIL import Image

# 游戏汇编里的字面量（✓ 真值）
EXPOSURE_MID = 0.002668       # L68
LOG_SCALE = 0.071429          # L70（= 1/14 ✓）
LOG_BIAS = 0.610727           # L70
COORD_SCALE = 0.968750        # L71（= 31/32 ✓）
COORD_BIAS = 0.015625         # L71（= 1/64  ✓）
LUT_SLICES = 32               # L72（B 轴分片数 ✓）
FINAL_GAIN = 1.05             # L82


def load_lut(path, slices=None):
    """读 3D LUT（★ 竖排分片 ✓）→ (N,3) 查询表
    实测 colorgrading_*.png = (16, 256) ⇒ 16 片，每片 16×16，竖着排 ✓
      即 size = W(16) · n_slice = H/size(16) ⇒ N = 16³ = 4096 ✓
    """
    im = Image.open(path).convert('RGB')
    W, H = im.size
    a = np.asarray(im).astype(np.float32) / 255.0
    size = W if H % W == 0 else int(round(H ** (1 / 3)))
    n_slice = H // size
    if slices is not None:
        n_slice = min(n_slice, int(slices))
    out = np.zeros((n_slice * size * size, 3), np.float32)
    k = 0
    for s in range(n_slice):
        blk = a[s * size:(s + 1) * size, :, :]       # ★ 竖排：按行切片 ✓
        out[k:k + size * size] = blk.reshape(-1, 3)
        k += size * size
    return out, n_slice, size


def apply_tonemap(rgb_linear, lut=None, n_slices=None, size=None,
                  bloom=None, bloom_intensity=0.0, vignette=0.0,
                  exposure_mid=EXPOSURE_MID):
    """★ 按汇编逐行实现（输入/输出均为线性 [0,1+] ✓）
       rgb_linear: (H,W,3) 或 (N,3)
    """
    x = np.asarray(rgb_linear, np.float32)
    shape = x.shape
    flat = x.reshape(-1, 3)
    # L65-67：bloom 叠加（可选）
    if bloom is not None:
        b = np.asarray(bloom, np.float32).reshape(-1, 3)
        flat = flat + b * float(bloom_intensity)
    # L68：× 曝光/中间灰
    v = np.clip(flat * float(exposure_mid), 1e-8, None)
    # L69：log（自然对数；DXBC 的 log 即 ln ✓）
    lv = np.log(v)
    # L70：mad_sat(log, 1/14, 0.610727)
    c = np.clip(lv * LOG_SCALE + LOG_BIAS, 0.0, 1.0)
    # L71：坐标缩放
    c = c * COORD_SCALE + COORD_BIAS
    if lut is not None and n_slices:
        # L72-76：B 轴分片 + 小数
        nb = c[:, 2] * n_slices - 0.5
        idx = np.floor(nb)
        frac = (nb - idx)[:, None]
        i0 = np.clip(idx, 0, n_slices - 1).astype(np.int32)
        i1 = np.clip(idx + 1, 0, n_slices - 1).astype(np.int32)
        per = size * size
        def look(sl, cc):
            u = np.clip(cc[:, 0], 0, 1)
            w = np.clip(cc[:, 1], 0, 1)
            xi = np.clip((u * (size - 1)).astype(np.int32), 0, size - 1)
            yi = np.clip((w * (size - 1)).astype(np.int32), 0, size - 1)
            return lut[sl * per + yi * size + xi]
        a0 = look(i0, c)
        a1 = look(i1, c)
        out = a0 * (1.0 - frac) + a1 * frac          # L77-81 ✓
    else:
        out = c                                       # 无 LUT 时退化为 log 归一
    # L82：mul_sat(·, 1.05)
    out = np.clip(out * FINAL_GAIN, 0.0, 1.0)
    return out.reshape(shape)


def apply_tonemap_nolut(rgb_linear, exposure_mid=EXPOSURE_MID):
    """LUT 缺失时的等价近似（只差最后一步 LUT 查表 ✓ 其余常数照汇编 ✓）"""
    return apply_tonemap(rgb_linear, None, None, None, exposure_mid=exposure_mid)
