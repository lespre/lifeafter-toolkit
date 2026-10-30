# -*- coding: utf-8 -*-
"""给 spine_render_fix 加「骨架级 mesh 缩放还原」覆盖表（用模块级变量传递，避免改签名）。"""
from __future__ import annotations

import pathlib

P = pathlib.Path("E:/la拆包项目/02_wiki/web/tools/spine_render_fix.py")

TABLE = '''# ---------------------------------------------------------------- 骨架级覆盖
# NeoX 导出变体：部分骨架的 mesh 顶点已把父级骨的统一缩放烘焙进坐标，
# 渲染时再乘一次就缩水（实测 touxiang_ani_03：角色只有应有尺寸的 ~1/2，蓝框里缩成一小团；
# 把 0.707 去掉后正好撑满，与官方立绘比例一致）。
# 只对 mesh/skinnedmesh 顶点生效，region 附件不受影响。
MESH_SCALE_OVERRIDE = {
    "touxiang_ani/touxiang_ani_03": 1 / 0.707,      # 可乐大亨（用户报错样本）
}
_MESH_BOOST = 1.0


def mesh_scale_for(atlas_path) -> float:
    key = str(atlas_path).replace("\\\\", "/").split("/spine/")[-1].rsplit(".", 1)[0]
    return float(MESH_SCALE_OVERRIDE.get(key, 1.0))


'''


def main() -> int:
    s = P.read_text(encoding="utf-8")
    if "MESH_SCALE_OVERRIDE" in s:
        print("已存在，跳过")
        return 0

    anchor = "# ---------------------------------------------------------------- IK 求解"
    s = s.replace(anchor, TABLE + anchor, 1)

    s = s.replace("def _sample_vertices(att, bones_mat, slotmat, scale, off):",
                  "def _sample_vertices(att, bones_mat, slotmat, scale, off, mesh_boost=1.0):", 1)
    s = s.replace("            pts.append((sx * scale + off[0], -sy * scale + off[1]))",
                  "            pts.append((sx * scale * mesh_boost + off[0], -sy * scale * mesh_boost + off[1]))", 1)
    s = s.replace("def draw_mesh(canvas, att_img, att, bones_mat, slotmat, scale, off, col=None):",
                  "def draw_mesh(canvas, att_img, att, bones_mat, slotmat, scale, off, col=None):", 1)
    s = s.replace("    pts = _sample_vertices(att, bones_mat, slotmat, scale, off)",
                  "    pts = _sample_vertices(att, bones_mat, slotmat, scale, off, _MESH_BOOST)", 1)

    # render_frames 里设置 boost
    s = s.replace("    skel, pages, regions = load_atlas(atlas)\n    aname = aname or anim_name(skel)",
                  "    global _MESH_BOOST\n    skel, pages, regions = load_atlas(atlas)\n"
                  "    _MESH_BOOST = mesh_scale_for(atlas)\n    aname = aname or anim_name(skel)", 1)

    P.write_text(s, encoding="utf-8")
    print("已加 MESH_SCALE_OVERRIDE（模块级 _MESH_BOOST 传递）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
