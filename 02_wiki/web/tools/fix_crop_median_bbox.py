# -*- coding: utf-8 -*-
"""裁剪改为「逐帧 bbox 取中位数」：动画里飞出去的粒子不该决定画幅。

原实现用所有帧的 alpha 并集 → 某一帧里粒子飞出很远，画幅被撑大、主体缩成小块
（da_450002 就是这样：setup pose 内容都在 422..978，动画中却有元素飞出）。
"""
from __future__ import annotations

import pathlib

P = pathlib.Path("E:/la拆包项目/02_wiki/web/tools/spine_render_fix.py")

OLD = """        cnt = None
        for f in frs:
            a = (np.asarray(f)[:, :, 3] > 4)
            cnt = a.astype(np.int16) if cnt is None else (cnt + a)
        thr = max(1, int(round(len(frs) * 0.25)))
        ys, xs = np.nonzero(cnt >= thr)
        if xs.size == 0:
            ys, xs = np.nonzero(cnt >= 1)
        if xs.size:
            minx, maxx = int(xs.min()), int(xs.max())
            miny, maxy = int(ys.min()), int(ys.max())"""

NEW = """        # ★ 逐帧算 bbox，再取「中位数」作为画幅：动画里偶发飞出去的粒子
        #   （只在一两帧出现在很远的地方）不该决定裁剪范围，否则主体被压成小块。
        boxes = []
        for f in frs:
            a = (np.asarray(f)[:, :, 3] > 4)
            ys, xs = np.nonzero(a)
            if xs.size:
                boxes.append((int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())))
        if boxes:
            med = lambda vals: sorted(vals)[len(vals) // 2]  # noqa: E731
            minx = med([b[0] for b in boxes])
            miny = med([b[1] for b in boxes])
            maxx = med([b[2] for b in boxes])
            maxy = med([b[3] for b in boxes])
        else:
            minx = miny = 0
            maxx = maxy = canvas - 1"""


def main() -> int:
    s = P.read_text(encoding="utf-8")
    if "逐帧算 bbox，再取「中位数」" in s:
        print("已改过，跳过")
        return 0
    if OLD not in s:
        raise SystemExit("锚点未命中")
    P.write_text(s.replace(OLD, NEW, 1), encoding="utf-8")
    print("已改：裁剪 bbox 取逐帧中位数")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
