# -*- coding: utf-8 -*-
"""裁剪改为「最大连通主体」：避免远处飞散粒子/光效把包围盒撑大、主体缩成一小块。

做法：在所有帧的 alpha 并集上做 1/4 降采样连通域，取最大连通块，映射回全分辨率 bbox，
再与现有覆盖率 bbox 取交集（连通块优先）。
"""
from __future__ import annotations

import pathlib

P = pathlib.Path("E:/la拆包项目/02_wiki/web/tools/spine_render_fix.py")

HELPER = '''

def _largest_component_box(mask):
    """mask: HxW bool（已降采样）。返回最大连通域的 bbox（含端点）或 None。"""
    H, W = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    best = None
    best_n = 0
    for y0 in range(H):
        row = mask[y0]
        for x0 in np.nonzero(row & ~seen[y0])[0]:
            if seen[y0, x0] or not mask[y0, x0]:
                continue
            stack = [(y0, int(x0))]
            seen[y0, x0] = True
            n = 0
            minx = maxx = int(x0)
            miny = maxy = y0
            while stack:
                y, x = stack.pop()
                n += 1
                if x < minx: minx = x
                if x > maxx: maxx = x
                if y < miny: miny = y
                if y > maxy: maxy = y
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < H and 0 <= xx < W and mask[yy, xx] and not seen[yy, xx]:
                        seen[yy, xx] = True
                        stack.append((yy, xx))
            if n > best_n:
                best_n = n
                best = (minx, miny, maxx, maxy)
    return best
'''

OLD = """        thr = max(1, int(round(len(frs) * 0.25)))
        ys, xs = np.nonzero(cnt >= thr)
        if xs.size == 0:
            ys, xs = np.nonzero(cnt >= 1)
        if xs.size:
            minx, maxx = int(xs.min()), int(xs.max())
            miny, maxy = int(ys.min()), int(ys.max())"""

NEW = """        thr = max(1, int(round(len(frs) * 0.25)))
        ys, xs = np.nonzero(cnt >= thr)
        if xs.size == 0:
            ys, xs = np.nonzero(cnt >= 1)
        if xs.size:
            minx, maxx = int(xs.min()), int(xs.max())
            miny, maxy = int(ys.min()), int(ys.max())
        # ★ 远端粒子/光效会把包围盒撑大 → 主体缩成一小块。
        #   在降采样并集上取最大连通域，把裁剪收回到主体。
        try:
            step = 4
            small = (cnt >= 1)[::step, ::step]
            box = _largest_component_box(small)
            if box:
                bx0, by0, bx1, by1 = box
                cx0, cy0 = bx0 * step, by0 * step
                cx1, cy1 = min(canvas - 1, bx1 * step + step), min(canvas - 1, by1 * step + step)
                # 只有当主体明显小于并集时才收紧，避免误裁
                if (cx1 - cx0) * (cy1 - cy0) < 0.85 * (maxx - minx) * (maxy - miny):
                    minx, maxx, miny, maxy = cx0, cx1, cy0, cy1
        except Exception:                              # noqa: BLE001
            pass"""


def main() -> int:
    s = P.read_text(encoding="utf-8")
    if "_largest_component_box" in s:
        print("已存在，跳过")
        return 0
    if OLD not in s:
        raise SystemExit("锚点未命中")
    s = s.replace(OLD, NEW, 1)
    anchor = "\ndef render_frames("
    s = s.replace(anchor, HELPER + anchor, 1)
    P.write_text(s, encoding="utf-8")
    print("已改：裁剪优先取最大连通主体")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
