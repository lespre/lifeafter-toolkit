# -*- coding: utf-8 -*-
"""fashion_glb.py — 时装静态 3D 原型（GLB + viewer.json）批量导出

链路: .mesh(网格) + .mtg(材料/贴图) → 每材料一套 PBR → GLB（纹理内嵌）
      + viewer.json（部件清单/来源/缺失项），供 fashion3d.html 组装查看。

依据:
  · mtg_parse.material_texture_map —— 材料↔子网格按文件序 1:1（已实证 17/17、21/21）
  · 角色/时装 .ktx = 标准 KTX 1.1 ETC2/EAC，ktx_to_png 已分支解码
  · 分件网格已在模型空间定位 ⇒ 不做骨骼变换，各部件同置原点即可合体

用法:
  python fashion_glb.py                 # 导出全部 5 套
  python fashion_glb.py --only 3715_f   # 只导一套
  python fashion_glb.py --list          # 只打印选型
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
from PIL import Image

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.join(os.path.dirname(_HERE), "纹理转换"))
import mtg_parse as MP            # noqa: E402
import mesh_parse2 as MS          # noqa: E402
import export_glb as EG           # noqa: E402
from ktx_to_png import ktx_to_png  # noqa: E402

RES_ROOT = r"e:\la拆包项目\01_索引与产物\41_还原树\pe\资源"
OUT_ROOT = r"e:\la拆包项目\02_wiki\web\assets\3d\fashion_3d"
CACHE_ROOT = r"e:\la拆包项目\01_索引与产物\30_分析\_fashion3d\texcache"

# 5 套主力款：2025 合体 ×2（f/m）+ 2021 分件 ×2 + 2021 整套 ×1
SPEC = [
    {
        "id": "3715_f", "series": "3715", "gender": "f",
        "label": "3715 · 女 · 2025 合体网格",
        "note": "players2025 重制款，_link 目录为全件合体（21 子网格含特效层）",
        "parts": [
            ("body", "衣服", "players2025/fas_f_3715/b_f_3715a_link/b_f_3715a.mesh"),
            ("hair", "头发", "players2025/fas_f_3715/h_f_3715a_link/h_f_3715a.mesh"),
        ],
    },
    {
        "id": "3640_m", "series": "3640", "gender": "m",
        "label": "3640 · 男 · 2025 合体网格",
        "note": "2025 重制男款，冰雪/晶体材质占比高",
        "parts": [
            ("body", "衣服", "players2025/fas_m_3640/b_m_3640a_link/b_m_3640a.mesh"),
            ("hair", "头发", "players2025/fas_m_3640/h_m_3640a_link/h_m_3640a.mesh"),
        ],
    },
    {
        "id": "3223_f", "series": "3223", "gender": "f",
        "label": "3223 · 女 · 2021 分件组合",
        "note": "衣服(4子网格)+外层件(1)+头发(2)+背包(2)，验证多文件并置",
        "parts": [
            ("body", "衣服", "players2021/b_f_3223/b_f_3223.mesh"),
            ("outer", "外层件", "players2021/b_f_3223/b_f_3223_1.mesh"),
            ("hair", "头发", "players2021/b_f_3223/h_f_3223.mesh"),
            ("bag", "背包", "players2021/bag_f_3223/bag_f_3223.mesh"),
        ],
    },
    {
        "id": "3245_f", "series": "3245", "gender": "f",
        "label": "3245 · 女 · 2021 分件组合",
        "note": "衣服(7子网格，含 transparent/rim_diss 层)+头发(3)+背包(3)",
        "parts": [
            ("body", "衣服", "players2021/b_f_3245/b_f_3245.mesh"),
            ("hair", "头发", "players2021/b_f_3245/h_f_3245.mesh"),
            ("bag", "背包", "players2021/bag_f_3245/bag_f_3245.mesh"),
        ],
    },
    {
        "id": "3301_f", "series": "3301", "gender": "f",
        "label": "3301 · 女 · 2021 整套 suit",
        "note": "suit_ 整套网格(3子网格)+背包，验证 suit 目录与 b_/h_ 的差异",
        "parts": [
            ("suit", "整套", "players2021/suit_f_3301/suit_f_3301.mesh"),
            ("bag", "背包", "players2021/bag_f_3301/bag_f_3301.mesh"),
        ],
    },
]

# glTF 只用一张法线：detail normal 先在切线空间合并进主法线（近似），再进 GLB
TEX_EXT_ORDER = (".ktx", ".png", ".dds", ".tga")
MAX_TEX = 1024         # 源贴图最高 1024，恢复原始分辨率；缓存目录按档位隔离，避免复用 512 旧图
DETAIL_STRENGTH = 0.5  # detail normal 叠加强度；同 UV 直叠会过猛，减半


def _resolve_tex(logical_path: str, res_root: str = RES_ROOT):
    """mtg 里的逻辑路径（.tga 占位）→ 实际文件（优先 .ktx）。

    ★ `_uvva` 是采样器/UV 动画标记，不总是磁盘文件名的一部分：
      实测 mtg 写 `effect\\textures\\veins\\tex_xingdian_01_uvva.tga`，
      磁盘只有 `tex_xingdian_01.ktx`（wenli01_lt_djs 同样）。故去掉该后缀再试一次。
    """
    stem = os.path.splitext(logical_path)[0]
    cands = [stem]
    if stem.lower().endswith("_uvva"):
        cands.append(stem[:-5])
    for st in cands:
        for ext in TEX_EXT_ORDER:
            fp = os.path.join(res_root, st + ext)
            if os.path.exists(fp):
                return fp.replace("\\", "/")
    # 同名兜底（同目录纹理目录下换扩展名 / 大小写差异）
    for st in cands:
        d = os.path.dirname(os.path.join(res_root, st))
        base = os.path.basename(st)
        if os.path.isdir(d):
            for fn in os.listdir(d):
                if os.path.splitext(fn)[0].lower() == base.lower():
                    return os.path.join(d, fn).replace("\\", "/")
    return None


def _shrink(png: str, max_dim: int = MAX_TEX):
    im = Image.open(png)
    if max(im.size) <= max_dim:
        return im.size
    im.thumbnail((max_dim, max_dim), Image.LANCZOS)
    im.save(png, optimize=True)
    return im.size


def _ensure_png(src: str, cache_dir: str):
    """任意源纹理 → PNG（GLB 内嵌用）。返回 (png_path, note)。"""
    ext = os.path.splitext(src)[1].lower()
    if ext == ".png":
        return src, "png 原样"
    os.makedirs(cache_dir, exist_ok=True)
    out = os.path.join(cache_dir, os.path.splitext(os.path.basename(src))[0] + ".png")
    if os.path.exists(out):
        _shrink(out)
        return out, "%s 已缓存" % ext
    if ext == ".ktx":
        ok, msg = ktx_to_png(src, out)
        if not ok:
            return None, "ktx 解码失败: %s" % msg
        return out, "ktx→png %s → %s" % (msg, _shrink(out))
    try:                                    # dds/tga: 交给 Pillow
        im = Image.open(src).convert("RGBA")
        im.save(out)
        return out, "%s→png (Pillow) → %s" % (ext, _shrink(out))
    except Exception as exc:
        return None, "%s 解码失败: %r" % (ext, exc)


def _pick_tex(mat: dict, role: str):
    lst = mat["roles"].get(role) or []
    if not lst:
        return None
    if role == "normal":
        # detail normal 已在 mtg_parse 里单独归为 normal_detail，这里取首个主法线
        return lst[0]
    if role == "param":
        # 参数图可能有多张（001m / 001s_m / 1001b_m …）：按 mtg 文件序取第一张
        # = 着色器首个 t_pbs_param 槽位（顺序即声明顺序）
        return lst[0]
    return lst[0]


def _alpha_info(png: str):
    im = Image.open(png).convert("RGBA")
    n = im.width * im.height
    h = im.getchannel("A").histogram()
    return {"min": next(i for i, v in enumerate(h) if v), "zero": h[0] / n,
            "low": sum(h[:128]) / n}


def _merge_normals(main_png: str, detail_png: str, out_png: str, strength: float = DETAIL_STRENGTH):
    """主法线 + detail normal 在切线空间近似合并（detail 未走第二 UV，按同 UV 减半叠加）。

    输入输出均为切线空间法线图（R=X, G=Y, B=Z，0.5 = 0）。
    合并式：n = normalize(n_main + [s·d.x, s·d.y, 0])，Z 取主法线，避免强凹凸互相抵消。
    """
    a = np.asarray(Image.open(main_png).convert("RGB"), np.float32) / 127.5 - 1.0
    di = Image.open(detail_png).convert("RGB")
    if di.size != (a.shape[1], a.shape[0]):
        di = di.resize((a.shape[1], a.shape[0]), Image.LANCZOS)
    d = np.asarray(di, np.float32) / 127.5 - 1.0
    n = a.copy()
    n[..., 0] += strength * d[..., 0]
    n[..., 1] += strength * d[..., 1]
    n /= np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-6)
    rgb = ((n * 0.5 + 0.5) * 255).clip(0, 255).astype(np.uint8)
    Image.fromarray(rgb, "RGB").save(out_png, optimize=True)
    return out_png


def _alpha_mode(sh: str, ai: dict | None):
    """按着色器语义决定 alphaMode，返回 (alphaMode, extras)。

    实证：时装底色的 alpha 通道并不总是"透明度"——
      · silk 白纱：alpha 大面积半透 → 必须 BLEND，否则变实体白塑
      · transparent：明确 BLEND
      · uber_fx 多层：加法发光层 → BLEND + viewer 侧加法混合
      · hair / billboard：用 alpha 挖洞 → MASK 更稳（避免排序穿帮）
    """
    ex = {}
    if "transparent" in sh:
        return "BLEND", ex
    if "fx" in sh:
        ex["blend_mode"] = "additive"
        return "BLEND", ex
    if any(k in sh for k in ("silk", "sss", "subsurface")):
        if ai and ai["low"] > 0.05:
            return "BLEND", ex
        return "OPAQUE", ex
    if any(k in sh for k in ("hair", "billboard")) and ai:
        if ai["zero"] > 0.02:
            return "MASK", ex
        if ai["low"] > 0.05:
            return "BLEND", ex
    return "OPAQUE", ex



def build_part(part_id: str, label: str, mesh_rel: str, outfit_id: str, out_dir: str):
    mesh_path = os.path.join(RES_ROOT, "character", mesh_rel)
    mtg_path = os.path.splitext(mesh_path)[0] + ".mtg"
    # 缓存按分辨率档位隔离：切到 1024 时不会复用旧 512 图
    cache_dir = os.path.join(CACHE_ROOT, "%s_%d" % (outfit_id, MAX_TEX))
    texmap_path = os.path.join(cache_dir, part_id + ".texmap.json")
    out_glb = os.path.join(out_dir, part_id + ".glb")
    rep = {"id": part_id, "label": label, "source_mesh": mesh_rel, "file": part_id + ".glb",
           "missing": [], "materials": [], "warnings": []}

    if not os.path.exists(mtg_path):
        rep["warnings"].append("无同名 .mtg，跳过材质（纯白模）")
        return rep
    A = MP.parse_mtg(mtg_path)
    n_mat = len(A["materials"])
    P, uv, idx, meta = MS.parse_mesh2(mesh_path)  # noqa: F841  仅取 meta 子网格区间
    n_sub = len(meta["sub_offsets"])
    if n_mat != n_sub:
        rep["warnings"].append("材料数 %d ≠ 子网格数 %d（按序号截断/补齐）" % (n_mat, n_sub))

    sets, opts, submap = {}, {}, []
    for i, m in enumerate(A["materials"]):
        sname = "%02d_%s" % (i, m["shader_name"] or "mat")
        ent = {}
        for slot, role in (("a", "basecolor"), ("n", "normal"), ("m", "param")):
            lp = _pick_tex(m, role)
            if not lp:
                continue
            src = _resolve_tex(lp)
            if not src:
                rep["missing"].append({"material": m["name"], "role": role, "path": lp})
                continue
            png, note = _ensure_png(src, cache_dir)
            if not png:
                rep["warnings"].append("%s: %s" % (lp, note))
                continue
            ent[slot] = png
        sets[sname] = ent
        mo = {}
        sh = (m["shader_name"] or "").lower()

        # detail normal：主法线存在时在切线空间近似合并（detail 的第二 UV 未定证，按同 UV 减半叠加）
        det = (m["roles"].get("normal_detail") or [None])[0]
        if det:
            dsrc = _resolve_tex(det)
            if dsrc:
                dpng, dnote = _ensure_png(dsrc, cache_dir)
                if dpng:
                    if "n" in ent:
                        merged = os.path.join(cache_dir, "%s_%s_nmerged.png"
                                              % (part_id, sname.replace("/", "_")))
                        _merge_normals(ent["n"], dpng, merged)
                        ent["n"] = merged
                        rep["warnings"].append("%s: detail normal 已合并(%s)" % (m["name"], os.path.basename(dsrc)))
                    else:
                        ent["n"] = dpng
                else:
                    rep["warnings"].append("%s: detail normal 解码失败 %s" % (m["name"], dnote))

        # ★ 角色底色的 alpha 通道并不总是"透明度"：按着色器语义判定，避免把布料挖空或把白纱变白塑
        ai = _alpha_info(ent["a"]) if "a" in ent else None
        amode, aex = _alpha_mode(sh, ai)
        mo["alphaMode"] = amode
        mo.update(aex)

        # metalness：param G 在引擎里更接近"高光/金属遮罩"，布料按 0.12 上限，晶体/珍珠保留金属感
        if "m" not in ent:
            mo.update(metallicFactor=0.0, roughnessFactor=0.75)
        elif any(k in sh for k in ("crystal", "pearl")):
            mo.update(roughnessFactor=1.0)
        else:
            mo.update(metallicFactor=0.12, roughnessFactor=1.0)

        # rim_diss / mask 是引擎侧边缘溶解特效壳，不是服装本体：
        #   它们没有独立底色（3245 直接无 a 图），当普通 PBR 导出会变成白色/碎片状外壳盖住衣服
        if "rim_diss" in sh or ("mask" in sh and "fx" not in sh):
            mo["hide"] = True
        opts[sname] = mo
        rep["materials"].append({"i": i, "name": m["name"], "shader": m["shader_name"],
                                 "slots": sorted(ent), "alphaMode": mo.get("alphaMode", "OPAQUE"),
                                 "metallicFactor": mo.get("metallicFactor")})
    for si in range(n_sub):
        submap.append(list(sets)[min(si, len(sets) - 1)] if sets else None)

    texmap = {"sets": sets}
    os.makedirs(cache_dir, exist_ok=True)
    json.dump(texmap, open(texmap_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    r = EG.build_glb(mesh_path, texmap_path, list(sets), out_glb,
                     label="%s_%s" % (outfit_id, part_id), center=False,
                     submap=submap, mat_opts=opts)
    rep.update({"vertices": r["vertices"], "faces": r["faces"], "submeshes": r["submeshes"],
                "materials_exported": r["materials"], "bytes": r["size"]})
    return rep


def build_outfit(spec: dict):
    out_dir = os.path.join(OUT_ROOT, spec["id"])
    os.makedirs(out_dir, exist_ok=True)
    parts = []
    for pid, label, rel in spec["parts"]:
        rep = build_part(pid, label, rel, spec["id"], out_dir)
        parts.append(rep)
        print("  %-6s %-52s v=%s subs=%s miss=%d" % (
            pid, rel.split("/")[-1], rep.get("vertices"), rep.get("submeshes"),
            len(rep["missing"])))
    vj = {
        "schema_version": 1,
        "outfit_id": spec["id"],
        "series": spec["series"],
        "gender": spec["gender"],
        "label": spec["label"],
        "note": spec["note"],
        "material": "approximate",
        "material_note": ("PBR 由 .mtg 材料/贴图直出；贴图 1024；detail normal 已按同 UV 近似合并；"
                          "alpha 按着色器语义（silk/transparent=BLEND，hair=MASK，fx=加法）；"
                          "IBL cube、第二 UV 集与 uber_fx 多层参数仍未进 GLB"),
        "center": "auto",
        "viewer": {"rotate_x_deg": 0, "up": "y"},
        "parts": parts,
    }
    json.dump(vj, open(os.path.join(out_dir, "viewer.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return vj


def main():
    args = sys.argv[1:]
    if "--list" in args:
        for s in SPEC:
            print(s["id"], s["label"])
            for pid, label, rel in s["parts"]:
                print("   ", pid, label, rel)
        return
    only = args[args.index("--only") + 1] if "--only" in args else None
    os.makedirs(OUT_ROOT, exist_ok=True)
    index = []
    for s in SPEC:
        if only and s["id"] != only:
            continue
        print("== %s %s" % (s["id"], s["label"]))
        index.append(build_outfit(s))
    if not only:
        json.dump({"outfits": index}, open(os.path.join(OUT_ROOT, "index.json"), "w",
                                           encoding="utf-8"), ensure_ascii=False, indent=1)
    print("完成 ->", OUT_ROOT)


if __name__ == "__main__":
    main()
