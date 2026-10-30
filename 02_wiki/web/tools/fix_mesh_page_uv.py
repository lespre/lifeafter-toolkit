# -*- coding: utf-8 -*-
"""修 mesh/skinnedmesh 的贴图来源：Spine 的 mesh uvs 是【页归一化坐标】，
必须对整张页贴图采样，不能对「同名 region 裁出来的小图」采样。

原实现把 uvs 0..1 映射到 region 裁切图 → 当 mesh 覆盖整页时只剩一小块、还带出页背景色块
（用户反馈 da_450002 可乐大亨：主体缩在右下角、旁边一块蓝色）。
"""
from __future__ import annotations

import pathlib
import re

P = pathlib.Path("E:/la拆包项目/02_wiki/web/tools/spine_render_fix.py")

OLD = """            key = att.get("name") or name
            att_img = att_cache.get(key)
            if att_img is None:
                reg = regions.get(key)
                if not reg:
                    continue
                pg = reg.get("page")
                page_img = page_imgs.get(pg)
                if page_img is None:
                    continue
                att_img = _region_cache(page_img, reg)
                att_cache[key] = att_img
            draw_mesh(canvas, att_img, att, bones_mat, bm, scale, off, col)
            continue"""

NEW = """            key = att.get("name") or name
            reg = regions.get(key)
            if not reg:
                continue
            page_img = page_imgs.get(reg.get("page"))
            if page_img is None:
                continue
            # ★ Spine 的 mesh/skinnedmesh uvs 是【页归一化坐标】（0..1 覆盖整张页），
            #   不是 region 相对坐标。早期实现拿 region 裁切图当贴图，mesh 跨整页时
            #   只会采到裁切图的一角 → 主体缩在一角、并把页背景色块画出来。
            att_img = page_img
            draw_mesh(canvas, att_img, att, bones_mat, bm, scale, off, col)
            continue"""


def main() -> int:
    s = P.read_text(encoding="utf-8")
    if NEW.split("\n")[3].strip() in s:
        print("已经改过，跳过")
        return 0
    if OLD not in s:
        raise SystemExit("锚点未命中")
    s = s.replace(OLD, NEW, 1)
    P.write_text(s, encoding="utf-8")
    print("已改：mesh 贴图源 = 整张页贴图")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
