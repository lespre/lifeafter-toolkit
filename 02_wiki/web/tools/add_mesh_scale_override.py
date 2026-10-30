# -*- coding: utf-8 -*-
"""给 spine_render_fix 加「骨架级 mesh 缩放还原」覆盖表。

背景（实测）：
  touxiang_ani_03 的 skinnedmesh 顶点看起来已把父级骨 'bone' 的 0.707 缩放烘焙进去，
  我们再按骨骼世界矩阵乘一次 ⇒ 角色只有应有尺寸的约 1/2（蓝框里缩成一小团）。
  实验：把该骨 scale 设为 1 后，角色正好撑满蓝框、与官方立绘比例一致。
  这类骨架按「NeoX 导出变体」处理：给一个骨架级系数 1/0.707，只影响 mesh 顶点。
"""
from __future__ import annotations

import pathlib

P = pathlib.Path("E:/la拆包项目/02_wiki/web/tools/spine_render_fix.py")

TABLE = '''

# ---------------------------------------------------------------- 骨架级覆盖
# NeoX 导出变体：部分骨架的 mesh 顶点已把父级骨的统一缩放烘焙进坐标，
# 渲染时再乘一次就会缩水（实测 touxiang_ani_03 角色只有应有尺寸的 ~1/2，
# 蓝框里缩成一小团；把 0.707 去掉后正好撑满，与官方立绘一致）。
# 只对 mesh/skinnedmesh 的顶点坐标生效，region 附件不受影响。
MESH_SCALE_OVERRIDE = {
    "touxiang_ani/touxiang_ani_03": 1 / 0.707,   # 可乐大亨（用户报错样本）
}


def mesh_scale_for(atlas_path) -> float:
    try:
        key = str(atlas_path).replace("\\\\", "/").split("/spine/")[-1].rsplit(".", 1)[0]
    except Exception:                                  # noqa: BLE001
        return 1.0
    return float(MESH_SCALE_OVERRIDE.get(key, 1.0))
'''


def main() -> int:
    s = P.read_text(encoding="utf-8")
    if "MESH_SCALE_OVERRIDE" in s:
        print("已存在覆盖表，跳过")
        return 0
    anchor = "# ---------------------------------------------------------------- IK 求解"
    if anchor not in s:
        raise SystemExit("锚点未命中")
    s = s.replace(anchor, TABLE.strip() + "\n\n\n" + anchor, 1)

    # _sample_vertices 增加 mesh_boost 参数
    s = s.replace("def _sample_vertices(att, bones_mat, slotmat, scale, off):",
                  "def _sample_vertices(att, bones_mat, slotmat, scale, off, mesh_boost=1.0):", 1)
    s = s.replace("            pts.append((sx * scale + off[0], -sy * scale + off[1]))",
                  "            pts.append((sx * scale * mesh_boost + off[0], -sy * scale * mesh_boost + off[1]))", 1)

    # draw_mesh 传入 mesh_boost
    s = s.replace("def draw_mesh(canvas, att_img, att, bones_mat, slotmat, scale, off, col=None):",
                  "def draw_mesh(canvas, att_img, att, bones_mat, slotmat, scale, off, col=None, mesh_boost=1.0):", 1)
    s = s.replace("    pts = _sample_vertices(att, bones_mat, slotmat, scale, off)",
                  "    pts = _sample_vertices(att, bones_mat, slotmat, scale, off, mesh_boost)", 1)

    # render_frame 里取 boost 并传给 draw_mesh
    s = s.replace("    for sname in order:\n        slot = smap.get(sname)",
                  "    boost = mesh_scale_for(atlas_path) if 'atlas_path' in locals() else 1.0\n"
                  "    for sname in order:\n        slot = smap.get(sname)", 1)
    s = s.replace("            draw_mesh(canvas, att_img, att, bones_mat, bm, scale, off, col)",
                  "            draw_mesh(canvas, att_img, att, bones_mat, bm, scale, off, col, boost)", 1)

    P.write_text(s, encoding="utf-8")
    print("已加：MESH_SCALE_OVERRIDE + mesh_boost 贯通")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
