# -*- coding: utf-8 -*-
u"""_build_snow_cube.py —— 自造「亮雪」环境 cube `custom_bright_snow_20260921` 的构造器。

═══════════════════════════════════════════════════════════════════════════════════════
⚠️⚠️ **自造近似立方体，非游戏资产**（status=self_authored_approximate，fidelity=approximate）。
    像素**基底**确实来自游戏资产（snow 的六面），但：
      ① f3(−Y) 面在源容器里**全黑**（maxRGB=0 / maxA=1/255）⇒ 本写手用 +Y 天花镜像补出；
      ② 逐像素辐射加了**软抬底** a（反解 RGBM 的 M 得到）；
      ③ **f3 是自造的，六面里有一面不是源像素。**
    **不得**当作「游戏实际使用该环境」的证据，**不得**标成 source_verified。
═══════════════════════════════════════════════════════════════════════════════════════

为什么基底从 gdansk 改成 snow（直接采信 GI2 终报的实测结论）：
  金属区发黑程度由 **cube 中解码后 L>1 的纹素占比**决定，不是平均亮度：

    | cube              | prim3 p50 | prim3 dark% | prim3 >0.85 | L>1 占比      |
    |-------------------|-----------|-------------|-------------|---------------|
    | qiangpi（源绑定）  | 0.0460    | 75.80%      | 0.70%       | 1.79%         |
    | over_the_clouds   | 0.2435    | —           | 0.64%       | 0.64%         |
    | jiayuan02a        | 0.1974    | 61.74%      | 5.72%       | 1.76%         |
    | car_studio01      | 0.2170    | 54.00%      | 8.84%       | 8.76%         |
    | clould_weather    | 0.5789    | 37.75%      | 2.30%       | 3.42%         |
    | **snow**          | **0.5832**| **37.03%**  | **12.98%**  | **20.38%** 最高|

  ⇒ 上一个自造项 `custom_bright_20260921`（基于 gdansk、把 p50 压到 0.31–0.45、只抬底）
    **会削弱 HDR 亮点、对金属帮助有限**；新基底必须是 `snow`。

已知瑕疵与处置：`snow` 的 **f3(−Y) 面在源容器里全黑**（实测 L_min=L_p50=L_max=0，
100% 纹素 L<0.05）⇒ 任何朝下的反射方向都会采到纯黑。本构造器**补该面**：
    f3 = (+Y 天花面垂直镜像) → 逐通道高斯模糊 σ=10 → 均匀压暗 dim=0.85
  · 镜像：让"天的底部"朝下，符合"地面反射天顶"的直觉朝向；
  · 模糊：抹掉镜像后可辨认的具体形状（避免在反射里出现假细节）；128px 面上 σ=10 已足够平滑；
  · 压暗：地面反射本应弱于天顶，0.85 保留 HDR 感、不做"平灰箱"。

构造（两步，全部可复算）：
  ① 源解码辐射（asm 542-544 已被游戏 DXBC 逐指令证实）：
         L_src = (rgb_src * a_src * 16)^2        # 逐通道
  ② **软抬底**（本步是自造的核心；**不加任何增益**）：
         L_new = sqrt( L_src^2 + a^2 )           # 逐通道，a = 0.05
     · 取 **g = 1.0**：对源里已经亮的像素**逐值不动** ⇒ 不靠"整体变亮"换金属，
       这是对「自造近似」最小侵入的选择；实测已足以把 L>1 占比从 20.376% 提到 23.92%。
     · a 由硬约束反解：逐面「近黑 L<0.05 占比 == 0」。
       由于 luma 是各通道的凸组合，**min_channel(L_new) = a** ⇒ 只要 a ≥ 0.05 即恒成立；
       0.047619 实测仍差 0.0024 ⇒ 取 a = 0.05（= 规格给定的近黑阈值本身，最省能量）。
  ③ 反解 RGBM 乘子 M（与查看器解码严格互逆）：
         q = sqrt(L_new) ; s = q/16 ; M = ceil_8bit(max_c s_c) ; rgb_out = s / M
     **ceil 而非 round** ⇒ M ≥ max_c s_c 恒成立 ⇒ rgb_out ≤ 1 **无需裁剪**，
     回读误差只剩 rgb_out 的 8bit 量化。

未做的事（如实登记）：
  · **没有**任何图像域增益 / 对比度 / 裁剪整形（g 恒为 1.0）；唯一整形是 f3 的模糊与压暗。
  · **没有**混其它 cube 的像素（f3 也只是 snow 自己的 +Y 面）。
  · **没有**动 exposure / ACES / bloom / 灯 / 环境强度 / lighting_approx（任务红线）。

用法：
  $env:PYTHONIOENCODING='utf-8'
  & '<venv>\python.exe' _build_snow_cube.py
产出：faces/*.png（人眼 sRGB 档）、rgbm/*.png（**接入必须用这套**）、provenance.json、_contact_sheet.png
"""
import hashlib
import json
import os

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

HERE = os.path.dirname(os.path.abspath(__file__))
CUBES = os.path.dirname(HERE)
NAME = 'custom_bright_snow_20260921'
SRC_CUBE = 'snow'
AXES = ['+X', '-X', '+Y', '-Y', '+Z', '-Z']
SRC_DIR = os.path.join(CUBES, SRC_CUBE, 'faces')
SRC_META = os.path.join(CUBES, SRC_CUBE, 'meta.json')

GAIN = 1.0            # **不加增益**：源里已亮的像素逐值不动
FLOOR_A = 0.0505      # 软抬底：逐通道下界（规格阈值 0.05 + 8bit 量化余量，见下）
F3_SIGMA = 10.0       # f3 补面：高斯模糊 σ（128px 面，σ=10 已足平滑）
F3_DIM = 0.85         # f3 补面：均匀压暗（保留 HDR 感，不做平灰箱）
NEAR_BLACK = 0.05     # 规格：近黑阈值
HDR_CUT = 1.0         # 规格：L>1 记为 HDR 亮点
_CEIL_EPS = 1e-9


def linear_to_srgb(x):
    x = np.clip(np.asarray(x, dtype=np.float64), 0.0, 1.0)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * np.power(x, 1.0 / 2.4) - 0.055)


def pct(x, q):
    return round(float(np.percentile(np.asarray(x, dtype=np.float64).ravel(), q)), 6)


def st(x):
    x = np.asarray(x, dtype=np.float64).ravel()
    return {'min': round(float(x.min()), 6), 'p05': pct(x, 5), 'p50': pct(x, 50),
            'p95': pct(x, 95), 'max': round(float(x.max()), 6), 'mean': round(float(x.mean()), 6)}


def sha256_file(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def luma_lin(L):
    return 0.2126 * L[:, :, 0] + 0.7152 * L[:, :, 1] + 0.0722 * L[:, :, 2]


def load_source():
    faces = []
    for i in range(6):
        p = os.path.join(SRC_DIR, '%s_f%d_m0.png' % (SRC_CUBE, i))
        raw = open(p, 'rb').read()
        im = Image.open(p)
        assert im.mode == 'RGBA', '源面必须 RGBA（alpha 承载 RGBM 乘子），实测 %s' % im.mode
        arr = np.asarray(im.convert('RGBA')).astype(np.float64) / 255.0
        L = np.square(arr[:, :, :3] * arr[:, :, 3:4] * 16.0)      # 逐通道解码辐射
        faces.append({'face': i, 'axis': AXES[i], 'src_path': p, 'src_bytes': len(raw),
                      'src_sha256': hashlib.sha256(raw).hexdigest(),
                      'rgb': arr[:, :, :3], 'a': arr[:, :, 3], 'L_src': L,
                      'src_is_black': bool(L.max() == 0.0)})
    return faces


def build_f3(plus_y_L):
    """f3(−Y) 补面：+Y 天花垂直镜像 → 逐通道高斯模糊 → 均匀压暗。"""
    flipped = plus_y_L[::-1, :, :]
    out = np.stack([gaussian_filter(flipped[:, :, c], sigma=F3_SIGMA, mode='reflect')
                    for c in range(3)], axis=2)
    return out * F3_DIM


def encode_rgbm(L):
    """L(逐通道线性辐射, 可 >1) → (rgbm_byte, M_byte, 回读)。与查看器 pow(rgb*a*16,2) 互逆。"""
    q = np.sqrt(L)
    s = q / 16.0
    m_raw = s.max(axis=2)
    m_byte = np.clip(np.ceil(m_raw * 255.0 - _CEIL_EPS), 1, 255).astype(np.uint8)
    M = m_byte.astype(np.float64) / 255.0
    rgbm = np.clip(s / M[:, :, None], 0.0, 1.0)
    rgbm_byte = np.clip(np.round(rgbm * 255.0), 0, 255).astype(np.uint8)
    out = np.zeros(L.shape[:2] + (4,), dtype=np.uint8)
    out[:, :, :3] = rgbm_byte
    out[:, :, 3] = m_byte
    return out, m_byte


def main():
    src = load_source()
    src_meta = json.load(open(SRC_META, encoding='utf-8'))

    print('=== 源 snow 六面（解码 L = luma((rgb*a*16)^2)）===')
    for f in src:
        l = luma_lin(f['L_src'])
        print('  f%d %-3s L_min=%-9.4f p50=%-8.4f max=%-9.4f L<0.05=%-8.3f%% L>1=%-7.3f%% %s'
              % (f['face'], f['axis'], l.min(), np.median(l), l.max(),
                 100.0 * (l < NEAR_BLACK).mean(), 100.0 * (l > HDR_CUT).mean(),
                 '← **全黑，需补面**' if f['src_is_black'] else ''))
    base_all = np.concatenate([luma_lin(f['L_src']).ravel() for f in src])
    print('  六面合并: mean=%.4f p50=%.4f L>1=%.3f%% L<0.05=%.3f%%'
          % (base_all.mean(), np.percentile(base_all, 50),
             100.0 * (base_all > HDR_CUT).mean(), 100.0 * (base_all < NEAR_BLACK).mean()))

    # ── f3 补面 ──
    f3_built = build_f3(src[2]['L_src'])
    l3 = luma_lin(f3_built)
    print()
    print('=== f3(−Y) 补面：+Y 镜像 → 高斯 σ=%.1f → 压暗 %.2f ===' % (F3_SIGMA, F3_DIM))
    print('  f3 补后 L_min=%.4f p50=%.4f max=%.4f  L<0.05=%.3f%%  L>1=%.3f%%'
          % (l3.min(), np.median(l3), l3.max(), 100.0 * (l3 < NEAR_BLACK).mean(),
             100.0 * (l3 > HDR_CUT).mean()))
    assert l3.min() > NEAR_BLACK, 'f3 补面失败：仍近黑'
    assert f3_built.max() > 1.0, 'f3 补面失败：无 HDR 亮点'

    # ── 软抬底（g=1.0，不加增益）──
    faces_out = []
    for f in src:
        if f['face'] == 3:
            faces_out.append({'face': 3, 'axis': AXES[3], 'L': f3_built, 'is_filled': True})
        else:
            faces_out.append({'face': f['face'], 'axis': f['axis'], 'L': f['L_src'],
                              'is_filled': False})
    for fo in faces_out:
        fo['L_new'] = GAIN * np.sqrt(fo['L'] ** 2 + FLOOR_A ** 2)

    print()
    print('=== 抬底：L_new = sqrt(L^2 + %.4f^2)，增益 = %.2f（**不加增益**）===' % (FLOOR_A, GAIN))

    faces_dir = os.path.join(HERE, 'faces')
    rgbm_dir = os.path.join(HERE, 'rgbm')
    os.makedirs(faces_dir, exist_ok=True)
    os.makedirs(rgbm_dir, exist_ok=True)

    prov_faces, prov_rgbm, tiles = [], [], []
    for fo, f in zip(faces_out, src):
        L = fo['L_new']
        out, m_byte = encode_rgbm(L)
        rp = os.path.join(rgbm_dir, '%s_f%d_m0.png' % (NAME, fo['face']))
        Image.fromarray(out, 'RGBA').save(rp, optimize=True)

        # 回读校验（模拟查看器解码）
        back = np.asarray(Image.open(rp).convert('RGBA')).astype(np.float64) / 255.0
        dec = np.square(back[:, :, :3] * back[:, :, 3:4] * 16.0)
        abs_err = np.abs(dec - L)
        err = float(abs_err.max())
        Lm, dec_m = luma_lin(L), luma_lin(dec)
        rel_err = np.abs(dec_m - Lm) / np.maximum(Lm, 1e-12)

        # 人眼档：解码线性辐射 → sRGB 显示（clamp；>1 的 HDR 在此档截断，仅供看图）
        disp = linear_to_srgb(L)
        disp_byte = (np.clip(disp, 0.0, 1.0) * 255.0).round().astype(np.uint8)
        sp = os.path.join(faces_dir, '%s_f%d_m0.png' % (NAME, fo['face']))
        Image.fromarray(disp_byte).save(sp, optimize=True)
        disp_lum = 0.2126 * disp[:, :, 0] + 0.7152 * disp[:, :, 1] + 0.0722 * disp[:, :, 2]

        src_lum = luma_lin(f['L_src'])
        prov_faces.append({
            'face': fo['face'], 'axis': fo['axis'],
            'file': '%s_f%d_m0.png' % (NAME, fo['face']),
            'sha256': sha256_file(sp), 'bytes': os.path.getsize(sp),
            'is_filled_face': fo['is_filled'],
            'decoded_L': st(dec_m),
            'decoded_L_min': round(float(dec_m.min()), 6),
            'dark_L_lt_0.05_pct': round(float(100.0 * (dec_m < NEAR_BLACK).mean()), 4),
            'gt1_pct': round(float(100.0 * (dec_m > HDR_CUT).mean()), 4),
            'gt085_pct': round(float(100.0 * (dec_m > 0.85).mean()), 4),
            'srgb_lum': st(disp_lum),
            'source': {
                'cube': SRC_CUBE, 'face': f['face'], 'axis': f['axis'],
                'file': os.path.basename(f['src_path']), 'sha256': f['src_sha256'],
                'bytes': f['src_bytes'],
                'src_decoded_L': st(src_lum),
                'src_dark_L_lt_0.05_pct': round(float(100.0 * (src_lum < NEAR_BLACK).mean()), 4),
                'src_gt1_pct': round(float(100.0 * (src_lum > HDR_CUT).mean()), 4),
                'src_alpha': {'min': round(float(f['a'].min()), 6),
                              'p50': pct(f['a'], 50), 'max': round(float(f['a'].max()), 6),
                              'mean': round(float(f['a'].mean()), 6)},
                'src_is_all_black': f['src_is_black'],
            },
            'fill_provenance': ({
                'method': '+Y(f2) 天花面**垂直镜像** → 逐通道高斯模糊 σ=%.1f → 均匀压暗 ×%.2f' % (F3_SIGMA, F3_DIM),
                'mirror_source_face': 2, 'mirror_source_axis': '+Y',
                'mirror_source_sha256': src[2]['src_sha256'],
                'gaussian_sigma': F3_SIGMA, 'dim': F3_DIM,
                'why': ('源 f3(−Y) 在容器里 maxRGB=0 / maxA=1 ⇒ 解码后 100%% 近黑 ⇒ 任何朝下方向采样到纯黑。'
                        '镜像 +Y 使"天的底部"朝下（地面反射天顶的直觉朝向）；模糊抹掉可辨认的具体形状；'
                        '压暗表示地面反射弱于天顶。**此面是本写手自造的，六面里唯一一面不是源像素。**'),
            } if fo['is_filled'] else None),
        })
        prov_rgbm.append({
            'face': fo['face'], 'axis': fo['axis'],
            'file': 'rgbm/%s_f%d_m0.png' % (NAME, fo['face']),
            'sha256': sha256_file(rp), 'bytes': os.path.getsize(rp),
            'rgbm_rgb_byte': {'min': int(out[:, :, :3].min()), 'p50': int(np.percentile(out[:, :, :3], 50)),
                              'max': int(out[:, :, :3].max())},
            'alpha_M': {'min': round(float(back[:, :, 3].min()), 6), 'p05': pct(back[:, :, 3], 5),
                        'p50': pct(back[:, :, 3], 50), 'p95': pct(back[:, :, 3], 95),
                        'max': round(float(back[:, :, 3].max()), 6),
                        'mean': round(float(back[:, :, 3].mean()), 6)},
            'alpha_M_byte': {'min': int(m_byte.min()), 'p05': int(np.percentile(m_byte, 5)),
                             'p50': int(np.percentile(m_byte, 50)), 'p95': int(np.percentile(m_byte, 95)),
                             'max': int(m_byte.max())},
            'target_L': st(Lm), 'decoded_L': st(dec_m),
            'decode_roundtrip_max_abs_err': round(err, 8),
            'decode_roundtrip_abs_err': {'p50': pct(abs_err, 50), 'p95': pct(abs_err, 95)},
            'decode_roundtrip_rel_err': {'p50': pct(rel_err, 50), 'p95': pct(rel_err, 95),
                                         'max': round(float(rel_err.max()), 6)},
            'source_face_sha256': f['src_sha256'],
            'is_filled_face': fo['is_filled'],
        })
        tiles.append(disp_byte)
        print('  %-3s L_new min=%-8.4f p50=%-8.4f max=%-9.4f | L<0.05=%-7.3f%% L>1=%-7.3f%% '
              '| M byte p50=%-4d max=%-4d | abs_err p50=%.2e max=%.2e%s'
              % (fo['axis'], dec_m.min(), np.median(dec_m), dec_m.max(),
                 100.0 * (dec_m < NEAR_BLACK).mean(), 100.0 * (dec_m > HDR_CUT).mean(),
                 int(np.percentile(m_byte, 50)), int(m_byte.max()),
                 pct(abs_err, 50), err, '  ← 自造补面' if fo['is_filled'] else ''))

    sheet = np.concatenate([np.concatenate(tiles[0:3], axis=1),
                            np.concatenate(tiles[3:6], axis=1)], axis=0)
    Image.fromarray(sheet).save(os.path.join(HERE, '_contact_sheet.png'), optimize=True)

    # 六面合并统计：**一律从落盘的 rgbm/ PNG 回读解码**，保证数字就是接入后看到的
    def decode_png(p):
        arr = np.asarray(Image.open(p).convert('RGBA')).astype(np.float64) / 255.0
        return luma_lin(np.square(arr[:, :, :3] * arr[:, :, 3:4] * 16.0))

    dec_all = np.concatenate([
        decode_png(os.path.join(rgbm_dir, r['file'].split('/')[-1])).ravel() for r in prov_rgbm])

    p50s = [r['decoded_L']['p50'] for r in prov_faces]
    mins = [r['decoded_L_min'] for r in prov_faces]
    darks = [r['dark_L_lt_0.05_pct'] for r in prov_faces]
    gts = [r['gt1_pct'] for r in prov_faces]

    # ★ 硬断言：验收要求「逐面解码 min > 0.05」与「逐面近黑 L<0.05 占比 = 0」，均按**回读值**判。
    if not all(r['dark_L_lt_0.05_pct'] == 0.0 for r in prov_faces):
        worst = max(r['dark_L_lt_0.05_pct'] for r in prov_faces)
        raise SystemExit('FAIL: 回读后仍有近黑纹素，逐面最差 %.4f%%（需增大 FLOOR_A）' % worst)
    if not (min(mins) > NEAR_BLACK):
        raise SystemExit('FAIL: 有面回读 min=%.6f ≤ %.2f（8bit 量化吃掉了抬底余量，需增大 FLOOR_A）'
                         % (min(mins), NEAR_BLACK))

    prov = {
        'name': NAME,
        'status': 'self_authored_approximate',
        'authority': 'user_authorized_manual_20260921',
        'fidelity': 'approximate',
        'is_game_asset': False, 'not_a_game_asset': True,
        'note': ('**自造近似、非游戏资产**：像素基底取自游戏资产 snow 的前五面，'
                 '**f3(−Y) 面是自造的**（源该面全黑 ⇒ 用 +Y 天花镜像 + 模糊 + 压暗补出）；'
                 '并逐像素加了**软抬底** a=0.05（反解 RGBM 的 M）。'
                 '源侧**无选择器** ⇒ 默认改用它属**产品选择**；目的 = **消除武器金属镜面发黑**。'
                 '不得作为「游戏实际使用该环境」的证据，不得标成 source_verified，不得顶替源资产，'
                 '也不得计入「源数据驱动」目标。'),
        'derived_from': [{
            'cube': SRC_CUBE, 'role': 'f0/f1/f2/f4/f5 五面像素基底（f3 由 f2 镜像自造）',
            'cube_sha256': src_meta.get('sha256'), 'cube_sha16': src_meta.get('sha16'),
            'container': src_meta.get('container'), 'row': src_meta.get('row'),
            'off': src_meta.get('off'), 'comp': src_meta.get('comp'), 'dec': src_meta.get('dec'),
            'logical': src_meta.get('logical'), 'dims': src_meta.get('dims'),
            'format': src_meta.get('format'), 'status': src_meta.get('status'),
            'faces': [{'face': f['face'], 'axis': f['axis'], 'file': os.path.basename(f['src_path']),
                       'sha256': f['src_sha256'], 'bytes': f['src_bytes'],
                       'is_all_black_in_source': f['src_is_black']} for f in src],
        }],
        'cubemap_order': AXES, 'face_size': 128,
        'container': None, 'row': None, 'sha16': None, 'dims': '128x128',
        'format': 'PNG RGBA RGBM(a=multiplier) — 与源 B8G8R8A8_UNORM + asm542-544 解码约定对齐',
        'resolve': 'self_authored', 'in_skin': False,
        'identity_basis': 'self_authored_approximate — 无容器/无哈希命中，**不是**源 cube',
        'selectable': True, 'group': 'self_authored（自造近似，非游戏资产）',
        'rgbm_encoding': {
            'decode_in_viewer': 'q_L = pow(rgb * a * 16.0, 2.0)   /* asm 542-544，已由游戏 DXBC 逐指令证实 */',
            'texture_colorSpace': 'NoColorSpace (viewer L2001/L5106/L5223)',
            'encode': 'q = sqrt(L_new) ; s = q/16 ; M = ceil_8bit(max_c s_c) ; rgb_out = s / M',
            'alpha_is_rgbm_multiplier': True,
            'ceil_not_round_why': ('M 取 ceil 到 8bit 网格 ⇒ M ≥ max_c s_c 恒成立 ⇒ rgb_out ≤ 1 '
                                   '**无需裁剪**，回读误差只剩 rgb_out 的 8bit 量化。'),
            'why_alpha_matters': ('源 IBL 分支解码 pow(rgb*a*16,2)，alpha 就是 RGBM 乘子 M。'
                                  '实测 qiangpi alpha≈0.015 ⇒ 解码辐射≈0.05 ⇒ 金属镜面发黑。'),
        },
        'radiance_calibration': {
            'is_self_authored': True,
            'formula': 'L_new = sqrt( L_src^2 + a^2 )  逐通道；L_src = (rgb_src * a_src * 16)^2',
            'GAIN': GAIN,
            'GAIN_rule': ('**恒为 1.0，不加任何增益** —— 对源里已经亮的像素逐值不动。'
                          '这是对「自造近似」最小侵入的选择，避免"靠整体变亮换金属"。'),
            'L_FLOOR_A': FLOOR_A,
            'L_FLOOR_A_rule': ('a 由硬约束反解：逐面「近黑 L<0.05 占比 == 0」。'
                               'luma 是各通道的凸组合 ⇒ min_channel(L_new) = a ⇒ a ≥ 0.05 数学上即恒成立。'
                               '但 RGBM 落 8bit 后回读会略降：实测 a=0.0500 回读 min=0.049917（差 8.3e-5）、'
                               'a=0.047619 回读 min=0.0476 ⇒ 取 a = 0.0505（回读 min=0.050358 > 0.05，'
                               '余量 0.72%），刚好覆盖 8bit 量化误差、不浪费能量。'),
            'no_image_domain_gain': ('未施加任何图像域增益/对比度/裁剪整形（g 恒 1.0）。'
                                     '唯一的图像域整形是 f3 补面的高斯模糊与均匀压暗。'),
            'forbidden_touched': '未改 exposure / ACES / bloom / 灯 / 环境强度 / lighting_approx 既有值。',
        },
        'faces': prov_faces, 'rgbm_faces': prov_rgbm, 'faces_encoding': 'rgbm',
        'summary': {
            'decoded_L_p50_per_face': p50s,
            'decoded_L_min_per_face': mins,
            'dark_L_lt_0.05_pct_per_face': darks,
            'gt1_pct_per_face': gts,
            'gt1_pct_cube': round(float(100.0 * (dec_all > HDR_CUT).mean()), 4),
            'decoded_L_mean_cube': round(float(dec_all.mean()), 6),
            'decoded_L_p50_cube': round(float(np.percentile(dec_all, 50)), 6),
            'decoded_L_min_over_all_faces': round(min(mins), 6),
            'dark_L_lt_0.05_pct_worst_face': round(max(darks), 4),
            'all_faces_dark_zero': bool(all(d == 0.0 for d in darks)),
            'all_faces_min_gt_0.05': bool(min(mins) > NEAR_BLACK),
            'gt1_ge_source_snow': bool(100.0 * (dec_all > HDR_CUT).mean() >= 20.376),
            'source_snow': {
                'cube_sha256': src_meta.get('sha256'), 'cube_sha16': src_meta.get('sha16'),
                'gt1_pct_cube': round(float(100.0 * (base_all > HDR_CUT).mean()), 4),
                'decoded_L_mean_cube': round(float(base_all.mean()), 6),
                'decoded_L_p50_cube': round(float(np.percentile(base_all, 50)), 6),
                'dark_L_lt_0.05_pct_cube': round(float(100.0 * (base_all < NEAR_BLACK).mean()), 4),
                'f3_all_black': True,
            },
            'f3_fill': {'method': '+Y mirror → gaussian σ=%.1f → dim ×%.2f' % (F3_SIGMA, F3_DIM),
                        'sigma': F3_SIGMA, 'dim': F3_DIM,
                        'src_f3_sha256': src[3]['src_sha256'],
                        'built_f3_L_min': round(float(luma_lin(f3_built).min()), 6),
                        'built_f3_L_p50': round(float(np.median(luma_lin(f3_built))), 6),
                        'built_f3_gt1_pct': round(float(100.0 * (luma_lin(f3_built) > HDR_CUT).mean()), 4)},
        },
        'builder_script': '_build_snow_cube.py',
        'analyzer_scripts': ['_sweep_gain_floor.py', '_sweep_refine.py', '_sweep_minimal.py'],
        'limitations': [
            '**f3(−Y) 面是自造的**（源该面在容器里全黑）⇒ 六面里有一面不是源像素，整体为自造近似。',
            ('软抬底把 L<0.05 的深黑方向抬成**近中性灰**（逐通道取同一底）⇒ 这些方向**丢失细节、趋于消色差**；'
             '这是「任何方向都不黑」的必然代价，已如实登记（见 dark_L_lt_0.05_pct_per_face 与逐面 min）。'),
            ('本 cube 启用 f3 补面后**整体均值必然高于源 snow**（0.5050 → %.4f），因为源 snow 的 −Y 面是'
             '纯黑(贡献 0)、补面后该面贡献真实辐射。这部分升亮**不是**人为增益，而是"补全一个全黑面"的'
             '直接后果，已如实登记。' % float(dec_all.mean())),
            ('"L>1 占比决定金属发黑" 这条是 GI2 终报给出的**相关性**结论，未做逐反射方向的半球/镜面方向'
             '积分证明；本 cube 的达标线按该相关性口径验收。'),
            '面朝向沿用源 cube 的 six-face 顺序（+X,-X,+Y,-Y,+Z,-Z，与 three.js CubeTextureLoader 一致），未与引擎采样基变换重新对齐。',
            '该 cube **不是**游戏实际使用的环境；只是为消除金属镜面发黑而自造的显示用近似环境。',
        ],
    }
    json.dump(prov, open(os.path.join(HERE, 'provenance.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)

    print()
    print('GAIN=%.2f  FLOOR_A=%.4f' % (GAIN, FLOOR_A))
    print('六面解码 p50   : %s' % p50s)
    print('六面解码 min   : %s' % mins)
    print('六面 L<0.05 %%  : %s' % darks)
    print('六面 L>1 %%     : %s' % gts)
    print('逐面 dark==0   : %s' % prov['summary']['all_faces_dark_zero'])
    print('逐面 min>0.05  : %s' % prov['summary']['all_faces_min_gt_0.05'])
    print('cube L>1 = %.3f%%  (源 snow 20.376%%)  ⇒ ≥ 源: %s'
          % (prov['summary']['gt1_pct_cube'], prov['summary']['gt1_ge_source_snow']))
    print('cube 均值 = %.4f  (源 snow %.4f)'
          % (prov['summary']['decoded_L_mean_cube'], prov['summary']['source_snow']['decoded_L_mean_cube']))
    print('wrote provenance.json / faces/ / rgbm/ / _contact_sheet.png')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
