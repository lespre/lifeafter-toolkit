# -*- coding: utf-8 -*-
u"""_encode_rgbm.py —— 为自造 cube 生成**与查看器源 shader 编码约定一致**的 RGBM 六面。

为什么必须要这一步（技术事实，不是修饰）：
  `weapon_skin_viewer.js` 的源 IBL 分支按 **asm 542-544** 解码环境立方体：
        q_L = pow( rgb * a * 16.0, 2.0 )          // L1662/L2076/L2104/L3631
  且源 cube 纹理显式 `t.colorSpace = T.NoColorSpace`（DDS 头 = B8G8R8A8_UNORM，无 sRGB 标志，L1799）
  ⇒ shader 拿到的是**存储字节原值**，**alpha 通道承载 RGBM 的乘子**。
  实测源六面：qiangpi alpha mean=0.015 / jiayuan02a alpha mean=0.028（RGBA，128×128）。
  本写手最初只输出 **RGB（无 alpha）** 的六面 ⇒ WebGL 里 a 恒为 1.0
  ⇒ 解码成 pow(rgb*16,2)，比源约定**亮约 3 个数量级**（(1/0.015)^2 ≈ 4400×）。
  实测后果：naive RGB 档读数 p50=0.7898 / >0.85=40.90%，**超过游戏参考目标**（0.7763/38.90%）
  —— 这**不是**环境内容更亮，纯粹是编码不符造成的假象。

本脚本把「交付用 sRGB 六面」编码成 RGBM，使查看器解码后**恰好还原**该面片的线性辐射：
        s   = sqrt(L) / 16          每个通道所需的乘积 (rgb*a)
        a   = clamp(max_channel(s), 1/255, 1)
        rgb = s / a
  其中 L = srgb_to_linear(交付面片值)   —— 物理正确的线性化，**不是**为了凑任何亮度指标。

⚠️ 仍然：**自造近似立方体，非游戏资产**。RGBM 只是编码格式对齐，不改变来源性质。

用法：
  $env:PYTHONIOENCODING='utf-8'
  & '<venv>\\python.exe' '<本文件>'
产出：rgbm/<name>_f{0..5}_m0.png（RGBA）+ 追加进 provenance.json 的 rgbm_faces
"""
import hashlib
import json
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PROV = os.path.join(HERE, 'provenance.json')
RGBM_DIR = os.path.join(HERE, 'rgbm')
NAME = 'custom_studio_20260920'


def srgb_to_linear(x):
    x = np.asarray(x, dtype=np.float64)
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)


def main():
    prov = json.load(open(PROV, encoding='utf-8'))
    os.makedirs(RGBM_DIR, exist_ok=True)
    rows = []
    for f in prov['faces']:
        p = os.path.join(HERE, f['file'])
        rgb = np.asarray(Image.open(p).convert('RGB')).astype(np.float64) / 255.0
        L = srgb_to_linear(rgb)                       # 目标线性辐射
        s = np.sqrt(L) / 16.0                         # 需要的 rgb*a
        a = np.clip(s.max(axis=2), 1.0 / 255.0, 1.0)  # 乘子 = 通道最大
        rgbm = np.clip(s / a[:, :, None], 0.0, 1.0)

        out = np.zeros(rgb.shape[:2] + (4,), dtype=np.uint8)
        out[:, :, :3] = np.clip(rgbm * 255.0 + 0.5, 0, 255).astype(np.uint8)
        out[:, :, 3] = np.clip(a * 255.0 + 0.5, 0, 255).astype(np.uint8)

        op = os.path.join(RGBM_DIR, f['file'])
        Image.fromarray(out, 'RGBA').save(op, optimize=True)

        # 回读校验：解码后应≈L
        back = np.asarray(Image.open(op).convert('RGBA')).astype(np.float64) / 255.0
        dec = (back[:, :, :3] * back[:, :, 3:4] * 16.0) ** 2
        err = float(np.abs(dec - L).max())
        rows.append({'file': 'rgbm/' + f['file'], 'axis': f['axis'], 'sha256': hashlib.sha256(open(op, 'rb').read()).hexdigest(),
                     'bytes': os.path.getsize(op), 'alpha_mean': round(float(back[:, :, 3].mean()), 5),
                     'alpha_max': round(float(back[:, :, 3].max()), 5),
                     'target_linear_mean': round(float(L.mean()), 6),
                     'decoded_linear_mean': round(float(dec.mean()), 6),
                     'decode_roundtrip_max_abs_err': round(err, 6)})
        print('  %-3s %-42s sha256=%s alpha_mean=%.5f decL=%.6f err=%.2e' % (
            f['axis'], 'rgbm/' + f['file'], rows[-1]['sha256'][:16], rows[-1]['alpha_mean'],
            rows[-1]['decoded_linear_mean'], err))

    prov['rgbm_faces'] = rows
    prov['rgbm_encoding'] = {
        'why': ('查看器源 IBL 分支按 asm 542-544 解码 pow(rgb*a*16,2)，且 cube 纹理 colorSpace=NoColorSpace；'
                '源六面 alpha mean 0.015(qiangpi)/0.028(jiayuan02a) 即 RGBM 乘子。'
                '最初只输出 RGB（a=1.0）⇒ 解码亮约 4400×，读数 p50=0.7898/>0.85=40.90% 属**编码假象**。'),
        'decode_in_viewer': 'q_L = pow(rgb * a * 16.0, 2.0)   /* asm 542-544 */',
        'texture_colorSpace': 'NoColorSpace (viewer L1799)',
        'encode': 's = sqrt(srgb_to_linear(rgb))/16 ; a = clamp(max_ch(s),1/255,1) ; rgb_out = s/a',
        'target_radiance': 'L = srgb_to_linear(交付 sRGB 面片值) —— 物理线性化，非为凑指标',
        'verified': 'RGBM PNG 回读解码与目标 L 的最大绝对误差见各面 decode_roundtrip_max_abs_err',
    }
    json.dump(prov, open(PROV, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('updated provenance.json with rgbm_faces')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
