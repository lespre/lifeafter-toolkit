#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""按「已知边界体的 float32 字节」在 model_*.gpk 里定位 .gim 模型本体。

依据：.c159 文档里 BoundingHalf 是裸 float32（实证 001212.c159 @265 解出 0.2533/1.4693）。
      skin_1003_010 三级 LOD 的 BoundingHalf（来自 .c159 明文）：
        lod01 = (0.33, 1.26, 2.47)
        lod02 = (0.33, 1.26, 2.45)
        lod03 = (0.33, 1.05, 2.45)
      子网格 Sub0/1/2 的半长：(0.2773,0.8943,2.084) / (0.2813,1.0712,2.0981) / (0.1993,0.8472,0.5951)
用法：python tools/find_gim_by_bounds.py [--packs model_01.gpk model_02.gpk ...]
"""
from __future__ import annotations
import argparse, json, pathlib, struct, sys, time

sys.path.insert(0, r'E:\la拆包项目\01拆包器本体\工具库\01_核心解包器')

TARGETS = {
    'half_lod01': (0.33, 1.26, 2.47),
    'half_lod02': (0.33, 1.26, 2.45),
    'half_lod03': (0.33, 1.05, 2.45),
    'sub0_half': (0.2773, 0.8943, 2.084),
    'sub1_half': (0.2813, 1.0712, 2.0981),
    'sub2_half': (0.1993, 0.8472, 0.5951),
    'center_lod01': (0.0, 0.3, 1.7),
}
PATS = {k: b''.join(struct.pack('<f', v) for v in vals) for k, vals in TARGETS.items()}
RES_DIR = pathlib.Path(r'E:\mrzh\res')


def packs(arg):
    if arg:
        return [RES_DIR / p for p in arg]
    return sorted(RES_DIR.glob('model_*.gpk'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--packs', nargs='*')
    ap.add_argument('--out', default='analysis/audit/gim_by_bounds.json')
    a = ap.parse_args()

    import tempfile, shutil
    import lifeafter_unpacker_full as m

    found, notes, scanned = [], [], 0
    t0 = time.time()
    for p in packs(a.packs):
        if not p.exists():
            notes.append(f'{p.name}: 不存在'); continue
        tmp = pathlib.Path(tempfile.mkdtemp(prefix='gim_'))
        t1 = time.time()
        try:
            m.extract_gpk(str(p), str(tmp))
        except Exception as e:                       # noqa: BLE001
            notes.append(f'{p.name}: 解包失败 {type(e).__name__}: {str(e)[:60]}')
            shutil.rmtree(tmp, ignore_errors=True); continue
        fs = [f for f in tmp.rglob('*') if f.is_file()]
        hit_here = 0
        for f in fs:
            scanned += 1
            try:
                d = f.read_bytes()
            except Exception:                        # noqa: BLE001
                continue
            for name, pat in PATS.items():
                if pat in d:
                    off = d.find(pat)
                    found.append({'pack': p.name, 'entry': f.name, 'size': len(d),
                                  'match': name, 'offset': off, 'head': d[:32].hex(' ')})
                    hit_here += 1
        notes.append(f'{p.name}: {len(fs)} 条目, 命中 {hit_here}, {time.time()-t1:.0f}s')
        print(notes[-1], flush=True)
        if found:
            shutil.rmtree(tmp, ignore_errors=True)
            break
        shutil.rmtree(tmp, ignore_errors=True)

    out = pathlib.Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({'scanned_entries': scanned, 'found': found, 'notes': notes,
                               'elapsed_s': round(time.time() - t0, 1)},
                              ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'\n扫描条目 {scanned}，命中 {len(found)}，用时 {time.time()-t0:.0f}s')
    for f in found[:20]:
        print(f"   {f['pack']} :: {f['entry']} ({f['size']:,}B) match={f['match']} @{f['offset']} head={f['head']}")
    print('→', out)


if __name__ == '__main__':
    main()
