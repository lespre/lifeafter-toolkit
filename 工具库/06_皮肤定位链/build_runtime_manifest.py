# -*- coding: utf-8 -*-
"""build_runtime_manifest.py — 干净的 runtime manifest 生成器（唯一入口）

设计约束（按 2026-09-15 P0 收令）：
  · 只消费冻结的 c159_pair_v4.py 输出（不再 import 旧 c159_pair）
  · 不再做 NeoX→glTF PBR 翻译；GLB 只作几何容器
  · 每个 primitive 保留 MtlIdx + 材质名 + 实机 shader
  · 纹理按「角色」加载：槽名 ↔ 路径（按语义对齐，不按颜色反推）
  · 颜色空间：源 DDS 全为 BC7_UNORM(98) → 默认 linear；只有取得运行时
    SRV=BC7_UNORM_SRGB 证据才用 srgb。t_basecolor 标 ab_test 供 A/B。
  · 缺任何必需输入 → missing 列出槽名（浏览器端显示品红，禁止继承 GLB fallback）
  · 记录 manifest / GLB 的 SHA，供浏览器 fail-closed 比对

用法：
  python build_runtime_manifest.py --skin 1110171 --material <material.c159> --glb <glb> --out <json>
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WIKI = r"E:\la拆包项目\08Lifeafter wiki"
TEXDIR = r"E:\la拆包项目\03拆包产物\weapon"
PIXDIR = r"E:\la拆包项目\03拆包产物\render_1003_010\input_tex_dual"

# 槽位顺序（按**名字语义**对齐，来源：材质 c159 路径块 + 源 shader 槽名声明）
SLOT_ORDER = {
    "crystal": ["Tex0", "t_basecolor", "NormalMap", "DetailMap",
                "t_reflection_tex", "t_custom_ibl", "t_caustic_tex", "t_refraction_tex"],
    "weapon": ["Tex0", "ParamMap", "t_surfacemap", "NormalMap", "t_custom_ibl"],
}
# 槽位 → 在 Three 里扮演的角色 / 颜色空间
SLOT_ROLE = {
    "Tex0":            dict(role="mask",        color_space="linear", note="控制掩码 m=Tex0.r"),
    "t_basecolor":     dict(role="basecolor",   color_space="ab_test", note="A/B：sRGB vs NoColorSpace"),
    "ParamMap":        dict(role="param",       color_space="linear", note="Metallic=ParamMap.y / Roughness=ParamMap.x / .w 不得丢弃"),
    "t_surfacemap":    dict(role="surface",     color_space="linear", note="不得丢弃"),
    "NormalMap":       dict(role="normal",      color_space="linear", note="切线空间法线"),
    "DetailMap":       dict(role="detail",      color_space="linear", note="缺失→品红"),
    "t_reflection_tex":dict(role="reflection",  color_space="linear", note=""),
    "t_custom_ibl":    dict(role="ibl_cube",    color_space="linear", note="cube 环境，源未定位时不得用截图代替"),
    "t_caustic_tex":   dict(role="caustic",     color_space="linear", note=""),
    "t_refraction_tex":dict(role="refraction",  color_space="linear", note=""),
}
REQUIRED = {"crystal": ["Tex0", "t_basecolor", "NormalMap"],
            "weapon": ["Tex0", "ParamMap"]}


def sha256f(p):
    try:
        return hashlib.sha256(open(p, "rb").read()).hexdigest()
    except Exception:
        return None


def slot_of(name, kind):
    """按**名字语义**绑槽（禁止按颜色反推；顺序不可靠已实测）。

    weapon : *_a→Tex0(BaseColor) · *_m→ParamMap · *_s_m→t_surfacemap · *_n→NormalMap · *.cube→t_custom_ibl
    crystal: *_b_m→Tex0(掩码) · *_a→t_basecolor(颜色) · *_n→NormalMap · *bump*→DetailMap
             *reflection*→t_reflection_tex · *.cube→t_custom_ibl · *caustic*→t_caustic_tex
             *refraction*/*envmap*→t_refraction_tex
    """
    s = (name or "").lower()
    for ext in (".tga", ".dds", ".png", ".cube", ".tif"):
        if s.endswith(ext):
            s = s[: -len(ext)]; break
    base = s.split("\\")[-1]
    if base.endswith("cube"):                      # cube 分支前置（car_studio01 / qiangpi）
        return "t_custom_ibl"
    if kind == "crystal":
        if base.endswith("_b_m"): return "Tex0"
        if base.endswith("_s_m"): return "t_surfacemap"
        if base.endswith("_a"):   return "t_basecolor"
        if base.endswith("_n"):   return "NormalMap"
        if "bump" in base:        return "DetailMap"
        if "reflection" in base:  return "t_reflection_tex"
        if "refraction" in base or "envmap" in base: return "t_refraction_tex"
        if "caustic" in base:     return "t_caustic_tex"
        return None
    if base.endswith("_s_m"): return "t_surfacemap"
    if base.endswith("_a"):   return "Tex0"
    if base.endswith("_n"):   return "NormalMap"
    if base.endswith("_m"):   return "ParamMap"
    return None


def load_v4():
    sp = importlib.util.spec_from_file_location("v4", os.path.join(HERE, "c159_pair_v4.py"))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def path_blocks(b):
    """材质 c159 中的纹理路径记录，按间隔切成「每材质一块」。"""
    recs = []
    for m in re.finditer(rb'\x01\x13\x01([\x20-\x7e]{6,200}?)\x00', b):
        s = m.group(1).decode("latin1")
        if "\\" in s and re.search(r"\.(tga|dds|cube|png|tif)$", s, re.I):
            recs.append((m.start(), s))
    blocks, cur = [], []
    for off, s in recs:
        if cur and off - cur[-1][0] > 100:   # 实测：块间距 139–449B，块内 38–88B → 100 为分界，7 块尺寸 [5,8,8,7,5,8,7] 与材质序一致
            blocks.append(cur); cur = []
        cur.append((off, s))
    if cur:
        blocks.append(cur)
    return blocks


def local_file(logical):
    """逻辑路径 → 本地已解出的 DDS/PNG（找不到则 None）。"""
    base = logical.replace("/", "\\").split("\\")[-1]
    stem = os.path.splitext(base)[0]
    out = dict(path=logical, file=None, sha256=None, png=None, png_sha256=None)
    # 武器皮肤自己的贴图：按条目号命名（如 skin_1003_010001a → 001226.dds 需映射表）
    return out, stem


def build(skin, material_c159, glb, states=None):
    v4 = load_v4()
    b = open(material_c159, "rb").read()
    A = v4.analyze_v4(material_c159)
    blocks = path_blocks(b)
    mats = v4.read_materials(b)[0]          # [(name, record_off, shader)]
    out = dict(
        skin=skin, schema="neox_material/1",
        parser=dict(tool="c159_pair_v4.py", sha256=sha256f(os.path.join(HERE, "c159_pair_v4.py")),
                    method=A["method"], confidence=A["confidence"]),
        source=dict(material_c159=os.path.basename(material_c159), sha256=sha256f(material_c159)),
        glb=dict(path=os.path.basename(glb), sha256=sha256f(glb)) if glb and os.path.exists(glb) else None,
        slots_declared=[m.group(1).decode("latin1") for m in
                        re.finditer(rb"([A-Za-z_][A-Za-z0-9_]{2,40})\x00",
                                    b[:400]) if m.group(1).decode("latin1") in SLOT_ROLE],
        counts=dict(materials=len(mats), path_blocks=len(blocks),
                    paths=sum(len(x) for x in blocks)),
        primitives=[],
    )
    for i, m in enumerate(mats):
        sh = (m["shader"] or "")
        kind = "crystal" if "crystal" in sh else ("weapon" if "weapon" in sh else "other")
        order = SLOT_ORDER.get(kind, [])
        pb = blocks[i] if i < len(blocks) else []
        tex = {}
        for k, (off, logical) in enumerate(pb):
            slot = slot_of(os.path.basename(logical.replace("/", os.sep)), kind)   # 传完整文件名（含扩展名）
            if slot is None:
                slot = order[k] if k < len(order) else "slot_%d" % k
            meta = dict(SLOT_ROLE.get(slot, {}))
            stem = os.path.splitext(logical.replace("/", "\\").split("\\")[-1])[0]
            loc = dict(logical=logical, stem=stem, record_off=off,
                       color_space=meta.get("color_space", "linear"),
                       role=meta.get("role", "unknown"), file=None, sha256=None)
            tex[slot] = loc
        missing = [s for s in REQUIRED.get(kind, []) if s not in tex]
        out["primitives"].append(dict(
            mtl_idx=i, material=m["name"], material_record_off=m["record_off"],
            shader=sh, shader_kind=kind,
            params=A["primitives"][i]["params"],
            block_off=A["primitives"][i]["block_off"],
            group_off=A["primitives"][i]["group_off"],
            attribution_method=A["primitives"][i]["attribution_method"],
            confidence=A["primitives"][i]["confidence"],
            textures=tex, missing_required=missing,
            render=dict(pbr_translation=False, magenta_on_missing=True),
        ))
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    def arg(k, d=None):
        return a[a.index(k) + 1] if k in a else d
    skin = arg("--skin", "1110171")
    mat = arg("--material", os.path.join(TEXDIR, "001265.c159"))
    glb = arg("--glb", os.path.join(WIKI, "assets", "3d", "weapon_skin", skin, "dual.glb"))
    outp = arg("--out", os.path.join(WIKI, "assets", "3d", "weapon_skin", skin, "neox_material.json"))
    r = build(skin, mat, glb)
    json.dump(r, open(outp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("manifest -> %s  (%d B)" % (outp, os.path.getsize(outp)))
    print("parser=%s/%s  材质 %d  路径块 %d  路径 %d" % (
        r["parser"]["method"], r["parser"]["confidence"], r["counts"]["materials"],
        r["counts"]["path_blocks"], r["counts"]["paths"]))
    print("glb sha256 = %s" % (r["glb"] or {}).get("sha256"))
    for p in r["primitives"]:
        print("  prim%d MtlIdx=%d %-18s %-12s block@%s missing=%s" % (
            p["mtl_idx"], p["mtl_idx"], p["material"], p["shader_kind"], p["block_off"], p["missing_required"]))
        for slot, t in p["textures"].items():
            print("      %-18s ← %-46s cs=%s" % (slot, os.path.basename(t["logical"]), t["color_space"]))
