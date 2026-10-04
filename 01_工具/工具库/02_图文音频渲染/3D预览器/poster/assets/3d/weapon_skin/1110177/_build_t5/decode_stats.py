# -*- coding: utf-8 -*-
"""T5 step1：解码 029 候选 DDS 并用「项目既有内容签名」判定槽位。

依据（可复现）：
  · 1110171 的 ground truth 来自 03_执行\\30_分析/_known_loop/gpk_raw_8u32.json 的 label 字段
    （1224=010_b_m, 1225=010_s_m, 1226=010_a, 1227=010_n, 1228=010_m；
      1271=012_b_m, 1272=012_s_m, 1273=012_a, 1274=012_n, 1275=012_m）
    与 known_loop_report.json（entry_index 1226=001a / 1224=001b_m）
  · 同一 GPK 集群内贴图组顺序为 b_m, s_m, a, n, m, ...
本脚本：对每个候选算 mean/std/blue_dom/gray/grad/alpha_std，与上述 ground truth 比对。
只读源文件；输出写 _build_t5/。
"""
import os, sys, json, hashlib
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = r'E:\la拆包项目\01_工具\工具库\02_图文音频渲染\皮肤链与渲染'
sys.path.insert(0, TOOLS)
import dds_rgba_canonical as CAN

WDDS = r'E:\la拆包项目\03_执行\\20_提取\weapon'

# 1110171 ground truth（来自 gpk_raw_8u32.json 的 label）
GT = {
    '1224': '010_b_m', '1225': '010_s_m', '1226': '010_a', '1227': '010_n', '1228': '010_m',
    '1271': '012_b_m', '1272': '012_s_m', '1273': '012_a', '1274': '012_n', '1275': '012_m',
}
CAND = ['003991', '003992', '003993', '004009', '004010', '004011', '004012', '004013']


def stats(u8):
    a = u8.astype(np.float32)
    rgb, al = a[:, :, :3], a[:, :, 3]
    mean = rgb.reshape(-1, 3).mean(0)
    std = rgb.reshape(-1, 3).std(0)
    blue_dom = float(100.0 * ((rgb[:, :, 2] > rgb[:, :, 0] + 40) & (rgb[:, :, 2] > rgb[:, :, 1] + 40)).mean())
    mx = rgb.max(2); mn = rgb.min(2)
    gray = float(100.0 * ((mx - mn) < 12).mean())
    gx = np.abs(np.diff(rgb.mean(2), axis=1)).mean()
    gy = np.abs(np.diff(rgb.mean(2), axis=0)).mean()
    return dict(mean=[round(float(v)) for v in mean], std=[round(float(v)) for v in std],
                blue_dom=round(blue_dom, 1), gray=round(gray, 1),
                grad=round(float(gx + gy), 2), alpha_std=round(float(al.std()), 1),
                alpha_mean=round(float(al.mean()), 1))


def load(idx):
    p = os.path.join(WDDS, idx + '.dds')
    u8, prov = CAN.decode_dds_rgba_u8(p, verify_oiio=False)
    return u8, prov


def main():
    out = {}
    print('%-9s %-28s %-22s %-18s %s' % ('idx', 'mean', 'std', 'blue/gray', 'grad/alpha_std'))
    for idx in CAND + ['001224', '001226', '001227', '001228']:
        try:
            u8, prov = load(idx)
        except Exception as e:
            print(idx, 'DECODE FAIL', e); out[idx] = {'error': str(e)}; continue
        st = stats(u8)
        st['fmt'] = prov.get('fmt'); st['wh'] = [prov.get('width'), prov.get('height')]
        st['dds_sha256'] = prov.get('dds_sha256')
        st['canonical_pixel_sha256'] = prov.get('canonical_pixel_sha256')
        st['ground_truth_1110171'] = GT.get(str(int(idx)))
        out[idx] = st
        print('%-9s %-28s %-22s %-18s %s' % (
            idx, st['mean'], st['std'], '%s/%s' % (st['blue_dom'], st['gray']),
            '%s/%s' % (st['grad'], st['alpha_std'])))
    json.dump(out, open(os.path.join(HERE, '_t5_decode_stats.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('\n[saved] _t5_decode_stats.json')


if __name__ == '__main__':
    main()
