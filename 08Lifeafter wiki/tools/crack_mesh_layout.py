#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""破解 .mesh 顶点布局：用【尺度无关的包围盒比值判据】穷举候选布局。

判据来源：.c159 文档明文的 BoundingHalf（skin_1003_010 三级 LOD）
  lod01 = (0.33, 1.26, 2.47) → 归一化比值 0.134 : 0.510 : 1.000
  lod02 = (0.33, 1.26, 2.45)
  lod03 = (0.33, 1.05, 2.45)
比值与量化缩放无关，故对任意 int/float 布局都可比。

用法: python tools/crack_mesh_layout.py [--dir DIR] [--files a.mesh b.mesh] [--top 20]
"""
from __future__ import annotations
import argparse, json, pathlib, sys, time
import numpy as np

TARGETS = {
    'lod01': (0.33, 1.26, 2.47),
    'lod02': (0.33, 1.26, 2.45),
    'lod03': (0.33, 1.05, 2.45),
    'sub0':  (0.2773, 0.8943, 2.084),
    'sub1':  (0.2813, 1.0712, 2.0981),
    'sub2':  (0.1993, 0.8472, 0.5951),
}


def normalized(vals):
    s = sorted(vals)
    if s[2] <= 0:
        return None
    return np.array([x / s[2] for x in s])


TGTN = {k: normalized(v) for k, v in TARGETS.items()}

DTYPES = {'f32': '<f4', 'f16': '<f2', 'i16': '<i2', 'u16': '<u2', 'i8': 'i1'}
BYTES = {k: np.dtype(v).itemsize for k, v in DTYPES.items()}


def sample_matrix(d: bytes, start: int, stride: int, voff: int, dt: str, cap=60000):
    nb = BYTES[dt]
    need = 3 * nb
    if start + voff + need > len(d) or stride <= 0 or nb > stride:
        return None
    n = (len(d) - start - voff - need) // stride + 1
    if n < 300:
        return None
    n = min(n, cap)
    win = d[start + voff: start + voff + (n - 1) * stride + need]
    a = np.frombuffer(win, dtype=np.uint8)
    mat = np.lib.stride_tricks.as_strided(a, shape=(n, need), strides=(stride, 1))
    cols = []
    for k in range(3):
        seg = np.ascontiguousarray(mat[:, k * nb:(k + 1) * nb])
        if dt == 'i8':
            v = seg.reshape(-1).astype(np.int16)
            cols.append(np.where(v > 127, v - 256, v).astype(np.float64))
        elif dt == 'u8':
            cols.append(seg.reshape(-1).astype(np.float64))
        else:
            cols.append(seg.view(np.dtype(DTYPES[dt])).reshape(-1).astype(np.float64))
    return np.stack(cols, axis=1)


def locality(pts, k=400):
    """顶点局部性：网格中相邻顶点应彼此靠近（随机切片不满足）。返回中位跳距/对角线。"""
    q = pts[:min(len(pts), k)]
    if len(q) < 20:
        return 1e9
    step = np.linalg.norm(np.diff(q, axis=0), axis=1)
    diag = float(np.linalg.norm(q.max(0) - q.min(0))) or 1.0
    return float(np.median(step)) / diag


def judge(pts):
    if pts is None or pts.shape[0] < 200:
        return None
    finite = np.isfinite(pts).all(axis=1) & (np.abs(pts) < 1e6).all(axis=1)
    pts = pts[finite]
    if pts.shape[0] < 200:
        return None
    ext = pts.max(axis=0) - pts.min(axis=0)
    nrm = normalized(list(ext))
    if nrm is None:
        return None
    # 强判据①：顶点局部性（相邻顶点跳距 / 对角线）必须小
    loc = locality(pts)
    if loc > 0.12:
        return None
    best = None
    for k, t in TGTN.items():
        e = float(np.abs(nrm - t).sum())
        if best is None or e < best[0]:
            best = (e, k)
    return best[0], best[1], [round(float(v), 4) for v in nrm], int(pts.shape[0]), loc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', default=r'C:\Users\ADMINI~1\AppData\Local\Temp\gim__dyg5vsd')
    ap.add_argument('--files', nargs='*')
    ap.add_argument('--top', type=int, default=25)
    ap.add_argument('--out', default='analysis/audit/mesh_layout_crack.json')
    a = ap.parse_args()

    D = pathlib.Path(a.dir)
    files = [D / f for f in a.files] if a.files else sorted(D.glob('*.mesh'))
    print(f'扫描 {len(files)} 个 .mesh；判据 {len(TGTN)} 个；'
          f'目标比值示例 lod01={[round(float(x),3) for x in TGTN["lod01"]]}', flush=True)
    t0 = time.time()
    out = []
    for fi, p in enumerate(files):
        try:
            d = p.read_bytes()
        except Exception:                                # noqa: BLE001
            continue
        N = len(d)
        for start in range(36, 132, 4):
            for stride in (8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32,
                           36, 40, 44, 48, 52, 56, 60, 64):
                n = (N - start) // stride
                if n < 300 or n > 400000:
                    continue
                for voff in range(0, max(1, stride - 12), 2):
                    for dt in ('f32', 'i16', 'u16', 'f16', 'i8'):
                        nb = BYTES[dt]
                        if voff + 3 * nb > stride:
                            continue
                        pts = sample_matrix(d, start, stride, voff, dt)
                        r = judge(pts)
                        if r is None:
                            continue
                        err, key, nrm, cnt, loc_ok = r
                        if err < 0.02:
                            out.append({'file': p.name, 'size': N, 'start': start, 'stride': stride,
                                        'voff': voff, 'dtype': dt, 'n': cnt, 'err': round(err, 5),
                                        'target': key, 'ratios': nrm})
        if fi % 500 == 0:
            print(f'  [{fi}/{len(files)}] {p.name} 命中累计 {len(out)}  {time.time()-t0:.0f}s', flush=True)
        if len(out) > 4000:
            break
    out.sort(key=lambda x: x['err'])
    o = pathlib.Path(a.out); o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps({'targets': TARGETS, 'hits': out[:4000],
                             'elapsed_s': round(time.time() - t0, 1)},
                            ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'\n=== Top {a.top}（err 越小越像）=== 用时 {time.time()-t0:.0f}s')
    for h in out[:a.top]:
        print(f"  err={h['err']:.5f} {h['file']} start={h['start']} stride={h['stride']} "
              f"voff={h['voff']} {h['dtype']} n={h['n']} → {h['target']} {h['ratios']}")
    print('→', o)


if __name__ == '__main__':
    main()
