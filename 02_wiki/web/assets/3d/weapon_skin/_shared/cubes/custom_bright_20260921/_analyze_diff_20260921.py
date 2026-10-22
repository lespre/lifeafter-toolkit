# -*- coding: utf-8 -*-
"""_analyze_diff_20260921.py —— 换 cube 到底改变了**哪些像素**？（只读 _shots/ 里的 PNG）

动机（必须回答的问题）：
  三档实测：qiangpi dark%=85.46 / gdansk 82.81 / 自造 81.72 —— 只降 3.74pp；
  但环境辐射从 ~0.05 抬到 ~0.31（≈6×）。若金属镜面真吃 cube 辐射，dark% 不该几乎不动。
  ⇒ 要么「金属区代理」的消色差暗像素**不是金属**（被暗背景主导），
     要么这些像素**根本不由 cube 驱动**。本脚本用像素级对照把二者分开。

判据：
  ① 换 cube 后被改动的像素集 M = { |Δ| > 0.01 }；
  ② 对照档的「消色差暗像素集」D = { sat<0.55 ∧ luma<0.25 }（= 代理指标的分子）；
  ③ 若 |M ∩ D| / |D| 很小 ⇒ **D 不由 cube 驱动**（代理指标测的不是金属，或金属不由 env 主导）；
  ④ D 的空间分布（行/列直方图）⇒ 判断它是「背景带」还是「武器主体」。
"""
import json
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SHOT = os.path.join(HERE, '_shots')
A, B = 'qiangpi', 'custom_bright_20260921'


def load(tag):
    return np.asarray(Image.open(os.path.join(SHOT, 'TIER_%s.png' % tag)).convert('RGB')).astype(np.float64) / 255.0


def lum(a):
    return 0.2126 * a[:, :, 0] + 0.7152 * a[:, :, 1] + 0.0722 * a[:, :, 2]


def main():
    a0, a1 = load(A), load(B)
    if a0.shape != a1.shape:
        raise SystemExit('尺寸不同：%s vs %s' % (a0.shape, a1.shape))
    H, W, _ = a0.shape
    l0, l1 = lum(a0), lum(a1)
    sat0 = a0.max(axis=2) - a0.min(axis=2)
    dl = np.abs(l1 - l0)

    band = np.zeros((H, W), bool)
    band[int(H * 0.33):int(H * 0.62), int(W * 0.18):int(W * 0.85)] = True

    M = dl > 0.01                                     # 被 cube 改动的像素
    D = (sat0 < 0.55) & (l0 < 0.25)                   # 代理指标的「消色差暗」分子
    S = (l0 > 0.25) & (sat0 < 0.55)                   # 代理口径里的亮主体（分母里的另一半）

    def sh(mask, name, restricted=True):
        m = mask & band if restricted else mask
        return {'set': name, 'n_px_band': int(m.sum()),
                'share_of_band_pct': round(100.0 * m.sum() / max(band.sum(), 1), 2),
                'share_of_whole_frame_pct': round(100.0 * m.sum() / (H * W), 2),
                'dL_mean': round(float(dl[m].mean()), 5) if m.sum() else None,
                'dL_p50': round(float(np.percentile(dl[m], 50)), 5) if m.sum() else None,
                'dL_p95': round(float(np.percentile(dl[m], 95)), 5) if m.sum() else None,
                'dL_max': round(float(dl[m].max()), 5) if m.sum() else None,
                'frac_px_moved_gt_0.01_pct': round(float(100.0 * (dl[m] > 0.01).mean()), 2) if m.sum() else None,
                'lum0_p50': round(float(np.percentile(l0[m], 50)), 4) if m.sum() else None,
                'lum1_p50': round(float(np.percentile(l1[m], 50)), 4) if m.sum() else None}

    rep = {'compare': '%s -> %s' % (A, B), 'frame': [W, H],
           'band_n_px': int(band.sum()),
           'moved_anywhere': sh(M, 'M = |dL|>0.01 (全帧)', restricted=False),
           'moved_in_band': sh(M, 'M = |dL|>0.01 (带内)', restricted=True),
           'dark_achr_D': sh(D, 'D = 消色差且暗 (代理分子)'),
           'bright_achr_S': sh(S, 'S = 消色差且亮 (代理分母另一半)')}

    # 关键比例
    md = (M & D)
    dm = (M & band & D)
    Dband = (band & D)
    rep['reachability'] = {
        'D_px_total_whole_frame': int(D.sum()),
        'D_px_total_in_band': int(Dband.sum()),
        'D_px_moved_by_cube_anywhere': int(md.sum()),
        'D_px_moved_by_cube_and_in_band': int(dm.sum()),
        'D_frac_moved_by_cube_pct_whole_frame': round(100.0 * md.sum() / max(int(D.sum()), 1), 3),
        'D_frac_moved_by_cube_pct_in_band': round(100.0 * dm.sum() / max(int(Dband.sum()), 1), 3),
        'moved_px_that_are_D_pct': round(100.0 * md.sum() / max(int(M.sum()), 1), 3),
        'D_dL_mean': round(float(dl[D].mean()), 5) if D.sum() else None,
        'D_lum_change_mean': round(float((l1 - l0)[D].mean()), 5) if D.sum() else None,
        'S_dL_mean': round(float(dl[S].mean()), 5) if S.sum() else None,
        'S_lum_change_mean': round(float((l1 - l0)[S].mean()), 5) if S.sum() else None,
        'reading': ('D_frac_moved_by_cube_pct_in_band 很小 ⇒ 代理指标的「消色差暗」分子几乎不由 cube 驱动 '
                    '⇒ 换 cube **不可能**把它降 30pp（分母是暗背景，不是金属）'),
    }

    # D 的空间分布（把带切成 5 行 × 5 列，看它集中在哪）
    y0, y1 = int(H * 0.33), int(H * 0.62)
    x0, x1 = int(W * 0.18), int(W * 0.85)
    sub = D[y0:y1, x0:x1]
    rows = np.array_split(sub, 5, axis=0)
    rep['D_spatial'] = {
        'row_density_pct (top->bottom of band)': [round(100.0 * r.mean(), 2) for r in rows],
        'col_density_pct (left->right of band)': [round(100.0 * c.mean(), 2)
                                                  for c in np.array_split(sub, 5, axis=1)],
        'note': 'row/col = 带内 5 等分各自的 D 像素密度（%）；若普遍很高 ⇒ D 是**大面积背景**而非武器轮廓',
    }
    # 带内每行的平均亮度（看背景带在哪）
    rep['band_row_lum_p50_qiangpi'] = [round(float(np.percentile(l0[y0:y1][r], 50)), 4)
                                       for r in np.array_split(np.arange(y1 - y0), 5)]
    rep['band_row_lum_p50_custom'] = [round(float(np.percentile(l1[y0:y1][r], 50)), 4)
                                      for r in np.array_split(np.arange(y1 - y0), 5)]

    # 存一张差分可视化（放大 8× 便于人眼）
    vis = np.clip(dl * 8.0, 0, 1)
    Image.fromarray(np.repeat((vis * 255).astype(np.uint8)[:, :, None], 3, axis=2)).save(
        os.path.join(SHOT, 'DIFF_%s_vs_%s_x8.png' % (A, B)))
    dmask = np.zeros((H, W, 3))
    dmask[:, :, 0] = D * 1.0
    dmask[:, :, 1] = (M & band) * 1.0
    dmask[:, :, 2] = (M & D) * 1.0
    Image.fromarray((dmask * 255).astype(np.uint8), 'RGB').save(os.path.join(SHOT, 'MASKS_20260921.png'))

    json.dump(rep, open(os.path.join(HERE, '_diff_analysis_20260921.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
