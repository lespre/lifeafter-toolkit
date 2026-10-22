# -*- coding: utf-8 -*-
u"""_build_bright_cube.py —— 自造「不黑」环境 cube `custom_bright_20260921` 的构造器。

═══════════════════════════════════════════════════════════════════════════════════════
⚠️⚠️ **自造近似立方体，非游戏资产**（status=self_authored_approximate，fidelity=approximate）。
    像素**基底**确实来自游戏资产（gdansk_shipyard_buildings02 的六面），但
    **辐射标定（增益 + 抬底 + RGBM alpha 反解）是本写手自造的**，源侧没有任何字段要求这样做。
    **不得**当作「游戏实际使用该环境」的证据，**不得**标成 source_verified。
═══════════════════════════════════════════════════════════════════════════════════════

为什么需要它（机制，全部由本目录 _analyze_source.py 实测得出，不采信推测）：
  查看器源 IBL 分支按 asm 542-544 解码环境立方体： q_L = pow(rgb * a * 16, 2)
  且 cube 纹理 colorSpace=NoColorSpace ⇒ **alpha 通道就是 RGBM 乘子 M**。
  实测（128×128 mip0，RGBA）：
    · qiangpi 一档 alpha≈0.015 ⇒ 解码辐射 ≈ (0.93*0.015*16)² ≈ 0.05 ⇒ 金属镜面**发黑**；
    · gdansk_shipyard_buildings02 alpha p50=0.047 ⇒ 解码辐射 p50 = 0.49~0.75（**本来就亮**）；
    · 但 gdansk 的解码辐射**长尾很深**：L<0.01 的像素占 0.60%~5.38%（f4 最深），
      min 低到 7.6e-4 ⇒ 这些**方向**采样到就是近黑镜面 —— 这就是「还有点反黑」的机制。
  ⇒ 用户目标「**不黑**」= ① 取消深黑长尾（抬底）② 保住足够辐射（落在规格给定区间）。

构造（三步，全部可复算）：
  ① 取源六面 (rgb_src, a_src) → 源解码辐射  L_src = (rgb_src * a_src * 16)²   （逐通道）
  ② 自造辐射标定（**本步是自造的核心**，一个全局标量 K + 一个软抬底 L_FLOOR）：
         L_new = sqrt( (K * L_src)² + L_FLOOR² )        # 软底（quadrature），单调、平滑、无平台
     · 保证：L_new ≥ L_FLOOR（=0.12）对**每一个像素**成立 ⇒ **任何方向都不黑**；
     · K 由「规格区间」反解：取**满足 六面 p50 全部 ≤ 0.45 的最大 K**（= 在区间内把辐射顶到最高）。
  ③ 反解 RGBM 乘子 M（与查看器解码严格互逆）：
         q = sqrt(L_new) ; s = q/16 ; M = ceil_to_8bit(max_c s_c) ; rgb_out = s / M
     取 **ceil**（而不是 round）到 8bit 网格 ⇒ M ≥ max_c s_c 恒成立 ⇒ rgb_out ≤ 1 **无需裁剪**
     ⇒ 回读解码与目标 L_new 的误差只剩 rgb_out 的 8bit 量化（实测 ~1e-3 量级）。

未做的事（如实登记）：
  · **没有**混 over_the_clouds 的亮面。规格允许「必要时补面」，但实测 gdansk **六面都没有**
    大面积近黑（存储 luma<0.05 占比 0.00%）⇒ 不需要补面，少一个来源少一份不确定性。
  · **没有**任何图像域增益/对比度/模糊/裁剪整形 —— 只做逐像素辐射映射。
  · **没有**动 exposure / ACES / bloom / 灯 / 环境强度 / lighting_approx（属任务红线）。

用法：
  $env:PYTHONIOENCODING='utf-8'
  & '<venv>\python.exe' _build_bright_cube.py
产出：faces/*.png（人眼 sRGB 档）、rgbm/*.png（**接入必须用这套**）、provenance.json、_contact_sheet.png
"""
import hashlib
import json
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
CUBES = os.path.dirname(HERE)
NAME = 'custom_bright_20260921'
SRC_CUBE = 'gdansk_shipyard_buildings02'
AXES = ['+X', '-X', '+Y', '-Y', '+Z', '-Z']

L_FLOOR = 0.12          # 软抬底：解码后辐射的**逐像素下界**（规格：最小面 ≥ ~0.12）
P50_HI = 0.45           # 规格给的目标区间上界（用它在区间内反解最大 K）
P50_LO = 0.25           # 规格给的目标区间下界（只用于报告是否落入）
ALPHA_CEIL_GRID = True  # M 取 ceil 到 8bit 网格 ⇒ rgb_out ≤ 1，永不裁剪


# ────────────────────────────────── 色彩空间 ──────────────────────────────────
def linear_to_srgb(x):
    x = np.clip(np.asarray(x, dtype=np.float64), 0.0, 1.0)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * np.power(x, 1.0 / 2.4) - 0.055)


def srgb_to_linear(x):
    x = np.asarray(x, dtype=np.float64)
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)


def pct(x, q):
    return round(float(np.percentile(np.asarray(x, dtype=np.float64).ravel(), q)), 6)


def st(x):
    x = np.asarray(x, dtype=np.float64).ravel()
    return {'min': round(float(x.min()), 6), 'p05': pct(x, 5), 'p50': pct(x, 50),
            'p95': pct(x, 95), 'max': round(float(x.max()), 6), 'mean': round(float(x.mean()), 6)}


# ────────────────────────────────── 载入源六面 ──────────────────────────────────
def load_source():
    faces = []
    for i in range(6):
        p = os.path.join(CUBES, SRC_CUBE, 'faces', '%s_f%d_m0.png' % (SRC_CUBE, i))
        raw = open(p, 'rb').read()
        im = Image.open(p)
        assert im.mode == 'RGBA', '源面必须是 RGBA（alpha 承载 RGBM 乘子），实测 %s' % im.mode
        arr = np.asarray(im.convert('RGBA')).astype(np.float64) / 255.0
        faces.append({'face': i, 'axis': AXES[i], 'src_path': p, 'src_bytes': len(raw),
                      'src_sha256': hashlib.sha256(raw).hexdigest(),
                      'rgb': arr[:, :, :3], 'a': arr[:, :, 3]})
    return faces


def solve_K(faces):
    """取满足「六面 p50 全部 ≤ P50_HI」的最大 K（在规格区间内把辐射顶到最高）。"""
    def worst_p50(K):
        return max(pct(np.sqrt((K * f['L_src']) ** 2 + L_FLOOR ** 2).mean(axis=2), 50) for f in faces)

    lo, hi = 0.01, 8.0
    if worst_p50(hi) <= P50_HI:            # 极端情况：整个区间都还没到上界
        return hi
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if worst_p50(mid) <= P50_HI:
            lo = mid
        else:
            hi = mid
    return round(lo, 5)


def main():
    src = load_source()
    for f in src:
        # 源解码辐射（逐通道）：asm 542-544
        f['L_src'] = (f['rgb'] * f['a'][:, :, None] * 16.0) ** 2
        f['L_src_ch_mean'] = f['L_src'].mean(axis=2)

    K = solve_K(src)
    print('反解增益 K = %.5f   （约束：六面解码 p50 全部 ≤ %.2f）' % (K, P50_HI))

    faces_dir = os.path.join(HERE, 'faces')
    rgbm_dir = os.path.join(HERE, 'rgbm')
    os.makedirs(faces_dir, exist_ok=True)
    os.makedirs(rgbm_dir, exist_ok=True)

    prov_faces, prov_rgbm, tiles = [], [], []
    floor_dom_all = []

    for f in src:
        L = np.sqrt((K * f['L_src']) ** 2 + L_FLOOR ** 2)      # 逐通道目标辐射
        q = np.sqrt(L)
        s = q / 16.0
        m_raw = s.max(axis=2)
        if ALPHA_CEIL_GRID:
            m_byte = np.clip(np.ceil(m_raw * 255.0 - 1e-9), 1, 255).astype(np.uint8)
            M = m_byte.astype(np.float64) / 255.0
        else:
            M = np.clip(m_raw, 1.0 / 255.0, 1.0)
            m_byte = np.clip(np.round(M * 255.0), 1, 255).astype(np.uint8)
            M = m_byte.astype(np.float64) / 255.0
        rgbm = np.clip(s / M[:, :, None], 0.0, 1.0)
        rgbm_byte = np.clip(np.round(rgbm * 255.0), 0, 255).astype(np.uint8)

        # ── 接入档：RGBA PNG（rgb=RGBM 的 rgb，a=乘子 M），查看器按 pow(rgb*a*16,2) 解码 ──
        out = np.zeros(f['rgb'].shape[:2] + (4,), dtype=np.uint8)
        out[:, :, :3] = rgbm_byte
        out[:, :, 3] = m_byte
        rp = os.path.join(rgbm_dir, '%s_f%d_m0.png' % (NAME, f['face']))
        Image.fromarray(out, 'RGBA').save(rp, optimize=True)

        # ── 回读校验：模拟查看器解码 ──
        back = np.asarray(Image.open(rp).convert('RGBA')).astype(np.float64) / 255.0
        dec = (back[:, :, :3] * back[:, :, 3:4] * 16.0) ** 2
        abs_err = np.abs(dec - L)
        err = float(abs_err.max())
        Lm = L.mean(axis=2)
        dec_m = dec.mean(axis=2)
        rel_err = np.abs(dec_m - Lm) / np.maximum(Lm, 1e-9)

        # ── 人眼档：解码线性辐射 → sRGB 显示编码（clamp 到 [0,1]；>1 的 HDR 高光在此档截断） ──
        disp = linear_to_srgb(L)
        disp_byte = np.clip(np.round(disp * 255.0), 0, 255).astype(np.uint8)
        sp = os.path.join(faces_dir, '%s_f%d_m0.png' % (NAME, f['face']))
        Image.fromarray(disp_byte, 'RGB').save(sp, optimize=True)
        disp_lum = (0.2126 * disp[:, :, 0] + 0.7152 * disp[:, :, 1] + 0.0722 * disp[:, :, 2])

        srgb_lum = (0.2126 * f['rgb'][:, :, 0] + 0.7152 * f['rgb'][:, :, 1] + 0.0722 * f['rgb'][:, :, 2])
        floor_dom = float(100.0 * ((K * f['L_src_ch_mean']) < L_FLOOR).mean())
        floor_dom_all.append(floor_dom)

        prov_faces.append({
            'face': f['face'], 'axis': f['axis'],
            'file': '%s_f%d_m0.png' % (NAME, f['face']),
            'sha256': hashlib.sha256(open(sp, 'rb').read()).hexdigest(),
            'bytes': os.path.getsize(sp),
            'decoded_L': st(dec_m),
            'srgb_lum': st(disp_lum),
            'near_black_L_lt_0.05_pct': round(float(100.0 * (dec_m < 0.05).mean()), 4),
            'near_black_srgb_lum_lt_0.05_pct': round(float(100.0 * (disp_lum < 0.05).mean()), 4),
        })
        prov_rgbm.append({
            'file': 'rgbm/%s_f%d_m0.png' % (NAME, f['face']), 'axis': f['axis'],
            'sha256': hashlib.sha256(open(rp, 'rb').read()).hexdigest(),
            'bytes': os.path.getsize(rp),
            'alpha_M': {'min': round(float(back[:, :, 3].min()), 6), 'p05': pct(back[:, :, 3], 5),
                        'p50': round(float(np.percentile(back[:, :, 3], 50)), 6),
                        'p95': pct(back[:, :, 3], 95), 'max': round(float(back[:, :, 3].max()), 6),
                        'mean': round(float(back[:, :, 3].mean()), 6)},
            'alpha_M_byte': {'min': int(m_byte.min()), 'p50': int(np.percentile(m_byte, 50)),
                             'max': int(m_byte.max())},
            'target_L': st(Lm),
            'decoded_L': st(dec_m),
            'decode_roundtrip_max_abs_err': round(err, 8),
            'decode_roundtrip_abs_err': {'p50': pct(abs_err, 50), 'p95': pct(abs_err, 95),
                                         'max': round(err, 8)},
            'decode_roundtrip_rel_err': {'p50': pct(rel_err, 50), 'p95': pct(rel_err, 95),
                                         'max': round(float(rel_err.max()), 6)},
            'roundtrip_note': ('max_abs_err 出现在源里极亮的灯/太阳像素上（源 L 最大到 224.9）；'
                               '该处**相对**误差依然很小，故同时报 p50/p95/max 的绝对与相对误差。'),
            'floor_dominated_px_pct': round(floor_dom, 3),
            'source': {'cube': SRC_CUBE, 'face': f['face'], 'axis': f['axis'],
                       'file': os.path.basename(f['src_path']), 'sha256': f['src_sha256'],
                       'src_decoded_L': st(f['L_src_ch_mean']),
                       'src_alpha': {'min': round(float(f['a'].min()), 6),
                                     'p50': round(float(np.percentile(f['a'], 50)), 6),
                                     'max': round(float(f['a'].max()), 6),
                                     'mean': round(float(f['a'].mean()), 6)},
                       'src_rgb_lum': st(srgb_lum),
                       'src_near_black_luma_lt_0.05_pct': round(float(100.0 * (srgb_lum < 0.05).mean()), 4),
                       'src_dark_L_lt_0.01_pct': round(float(100.0 * (f['L_src_ch_mean'] < 0.01).mean()), 4)},
        })
        tiles.append(disp_byte)
        print('  %-3s L_new p50=%.4f min=%.4f | M byte p50=%-3d max=%-3d | abs_err p50=%.2e max=%.2e | '
              'rel_err p50=%.2e | 近黑(L<.05)=%.3f%% | 抬底占比=%.2f%%'
              % (f['axis'], pct(dec_m, 50), float(dec_m.min()), int(np.percentile(m_byte, 50)),
                 int(m_byte.max()), pct(abs_err, 50), err, pct(rel_err, 50),
                 100.0 * (dec_m < 0.05).mean(), floor_dom))

    # ── 六面拼图（人眼档，仅供复核看图） ──
    sheet = np.concatenate([np.concatenate(tiles[0:3], axis=1),
                            np.concatenate(tiles[3:6], axis=1)], axis=0)
    Image.fromarray(sheet, 'RGB').save(os.path.join(HERE, '_contact_sheet.png'), optimize=True)

    p50s = [r['decoded_L']['p50'] for r in prov_rgbm]
    mins = [r['decoded_L']['min'] for r in prov_rgbm]
    src_p50s = [r['source']['src_decoded_L']['p50'] for r in prov_rgbm]

    prov = {
        'name': NAME,
        'status': 'self_authored_approximate',
        'authority': 'user_authorized_manual_20260921',
        'fidelity': 'approximate',
        'not_a_game_asset': True,
        'is_game_asset': False,
        'note': ('**自造近似、非游戏资产**：像素基底取自游戏资产 gdansk_shipyard_buildings02 的六面，'
                 '但**辐射标定（增益 K + 抬底 L_FLOOR + RGBM alpha 反解）是本写手自造的**，'
                 '源侧没有任何选择器/字段要求这样做。目的 = 消除金属镜面方向的**纯黑**。'
                 '不得作为「游戏实际使用该环境」的证据，不得计入「源数据驱动」目标。'),
        'derived_from': [
            {'cube': SRC_CUBE,
             'role': '六面像素基底（**唯一**像素来源；未混任何其它 cube）',
             'cube_sha256': 'd28948b4cffe512ae170fa142cb28e3e556967466ea25700bf117d1b236571e3',
             'cube_sha16': 'd28948b4cffe512a',
             'container': '0000.gpk', 'row': 11706, 'dims': '128x128', 'mips': 8,
             'format': 'B8G8R8A8_UNORM cubemap',
             'faces': [{'face': f['face'], 'axis': f['axis'], 'file': os.path.basename(f['src_path']),
                        'sha256': f['src_sha256'], 'bytes': f['src_bytes']} for f in src]},
        ],
        'cubemap_order': AXES,
        'face_size': 128,
        'container': None, 'row': None, 'sha16': None,
        'dims': '128x128',
        'format': 'PNG RGBA RGBM(a=multiplier) — 与源 B8G8R8A8_UNORM + asm542-544 解码约定对齐',
        'resolve': 'self_authored',
        'in_skin': False,
        'identity_basis': 'self_authored_approximate — 无容器/无哈希命中，**不是**源 cube',
        'selectable': True,
        'group': 'self_authored（自造近似，非游戏资产）',
        'rgbm_encoding': {
            'decode_in_viewer': 'q_L = pow(rgb * a * 16.0, 2.0)   /* asm 542-544 */',
            'texture_colorSpace': 'NoColorSpace (viewer L1799/L2021)',
            'encode': 'q = sqrt(L_new) ; s = q/16 ; M = ceil_8bit(max_c s_c) ; rgb_out = s / M',
            'alpha_is_rgbm_multiplier': True,
            'ceil_not_round_why': ('M 取 ceil 到 8bit 网格 ⇒ M ≥ max_c s_c 恒成立 ⇒ rgb_out ≤ 1 '
                                   '**无需裁剪**，回读误差只剩 rgb_out 的 8bit 量化（见各面 '
                                   'decode_roundtrip_max_abs_err，~1e-3 量级）。'),
            'why_alpha_matters': ('源 IBL 分支解码 pow(rgb*a*16,2)，alpha 就是 RGBM 乘子 M。'
                                  '实测 qiangpi alpha≈0.015 ⇒ 解码辐射≈0.05 ⇒ 金属镜面发黑。'),
        },
        'radiance_calibration': {
            'is_self_authored': True,
            'formula': 'L_new = sqrt( (K * L_src)^2 + L_FLOOR^2 )   逐通道；L_src = (rgb_src * a_src * 16)^2',
            'K': K,
            'K_rule': ('取满足「六面解码 p50 全部 ≤ %.2f」的**最大** K —— 即在规格给定区间内把有效辐射顶到最高。'
                       '二分反解，约束单调。' % P50_HI),
            'L_FLOOR': L_FLOOR,
            'L_FLOOR_rule': '软抬底（quadrature）：保证 L_new ≥ %.2f 对**每一像素**成立 ⇒ 任何方向都不黑。' % L_FLOOR,
            'target_band_p50': [P50_LO, P50_HI],
            'floor_dominated_px_pct_per_face': [round(x, 3) for x in floor_dom_all],
            'no_image_domain_gain': ('未施加任何图像域增益/对比度/模糊/裁剪整形；也未混其它 cube '
                                     '（实测 gdansk 六面均无大面积近黑 ⇒ 规格允许的「补面」不需要）。'),
            'forbidden_touched': ('未改 exposure / ACES / bloom / 灯 / 环境强度 / lighting_approx 既有值。'),
        },
        'faces': prov_faces,
        'rgbm_faces': prov_rgbm,
        'faces_encoding': 'rgbm',
        'summary': {
            'decoded_L_p50_per_face': p50s,
            'decoded_L_min_per_face': mins,
            'decoded_L_p50_min_face': min(p50s),
            'decoded_L_p50_max_face': max(p50s),
            'decoded_L_min_over_all': round(min(mins), 6),
            'src_decoded_L_p50_per_face': src_p50s,
            'K_applied_to_source_p50_ratio': round(min(p50s) / max(src_p50s), 4),
            'band_p50': [P50_LO, P50_HI],
            'all_faces_p50_in_band': bool(all(P50_LO <= p <= P50_HI for p in p50s)),
            'all_pixels_at_or_above_floor': bool(min(mins) >= L_FLOOR - 1e-6),
            'near_black_px_pct_all_faces': round(max(r['near_black_L_lt_0.05_pct'] for r in prov_faces), 4),
            'source_near_black_luma_pct_all_faces': round(max(
                r['source']['src_near_black_luma_lt_0.05_pct'] for r in prov_rgbm), 4),
            'source_dark_L_lt_0.01_pct_per_face': [r['source']['src_dark_L_lt_0.01_pct'] for r in prov_rgbm],
        },
        'builder_script': '_build_bright_cube.py',
        'analyzer_script': '_analyze_source.py',
        'limitations': [
            '像素基底是**游戏资产**，但**辐射标定（K / 抬底 / alpha）是自造的** ⇒ 整体为自造近似，非源环境。',
            ('平滑抬底把 L<0.12 的深黑方向抬成**近中性灰**（逐通道取同一底）⇒ 这些方向**丢失细节、'
             '趋于消色差**；这是「任何方向都不黑」的必然代价，已如实登记（见 floor_dominated_px_pct_per_face）。'),
            ('源 +Y 面解码辐射最大到 224.9（源里有极亮的灯/太阳像素）；本 cube 保留之（经 K 衰减），'
             '故仍是高动态范围环境，不是「均匀灰箱」。'),
            '面朝向沿用源 cube 的 six-face 顺序（+X,-X,+Y,-Y,+Z,-Z，与 three.js CubeTextureLoader 一致），未与引擎采样基变换重新对齐。',
            '该 cube **不是**游戏实际使用的环境；只是为消除金属镜面纯黑而自造的显示用近似环境。',
        ],
    }
    json.dump(prov, open(os.path.join(HERE, 'provenance.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)

    print()
    print('K=%.5f  L_FLOOR=%.2f' % (K, L_FLOOR))
    print('六面解码 p50: %s' % p50s)
    print('六面解码 min: %s' % mins)
    print('全部落入 [%.2f, %.2f]: %s' % (P50_LO, P50_HI, prov['summary']['all_faces_p50_in_band']))
    print('全部 ≥ L_FLOOR: %s' % prov['summary']['all_pixels_at_or_above_floor'])
    print('近黑像素占比（全部面）: %.4f%%' % prov['summary']['near_black_px_pct_all_faces'])
    print('源近黑 luma 占比（全部面）: %.4f%%' % prov['summary']['source_near_black_luma_pct_all_faces'])
    print('wrote provenance.json / faces/ / rgbm/ / _contact_sheet.png')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
