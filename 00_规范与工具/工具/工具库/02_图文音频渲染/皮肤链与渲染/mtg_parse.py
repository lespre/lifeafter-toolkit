# -*- coding: utf-8 -*-
"""mtg_parse.py — NeoX `.mtg` 材质文档解析器（角色/时装侧）

为什么单独写（不复用 c159_pair）
--------------------------------
`.mtg` 与 `.c159` 共用同一个序列化容器头（`c1 59 41 0d`），名字表也用同一套
`AnimParam … Version` + `t_*/u_*` 编码；但**材料实例的命名与组织结构不同**：
  · `.c159` 材料名是 `skim_*/skin_*`，靠槽位组↔数值块配对反推参数；
  · `.mtg`   材料名是 `b_f_3715_high_0 … _fx04`，材料数 = 着色器数 = 贴图块数，
    且每材料一块**定长结构记录**，不需要配对算法。
直接复用 c159_pair 会得到 55 个组 / 15 个块的噪声（实测 b_f_3715a.mtg），
材料数识别为 0。故本工具按 `.mtg` 自身的结构标记解析，结果可逐条复核。

结构实证（b_f_3715a.mtg 21311B / b_f_3715a_1.mtg 6294B / b_f_3715a_link）
------------------------------------------------------------------
  0x00        magic `c1 59 41 0d`（与 .c159 一致）
  名字表      `AnimParam` … `Version`（37 个组件名）+ 参数名（t_/u_）+ RenderStates
  参数表      每参数一条序列化记录（2722B..4185B）
  材料表      17 条，每条前缀固定 `02 09 01` + `<材料实例名\\0>`
  着色器表    `shader\\<x>.fx::TShader` ×17，与材料**按文件序 1:1**
  贴图/宏块    每材料一块：块内贴图路径相邻（字符串间隔固定 6B），
              块间间隔 100~650B（实测 16 个块边界全部 >100）
  → 材料数 = 着色器数 = 贴图块数 = 子网格数（b_f_3715a.gim SubMesh 17 项）

用法
----
  python mtg_parse.py <file.mtg> [--json out.json]
库
  parse_mtg(path) -> dict
  material_texture_map(path, sub_names=None) -> {sub_index: material_dict}
"""
from __future__ import annotations

import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

try:
    from c159_pair import read_names, classify_c159
except Exception:  # pragma: no cover
    read_names = classify_c159 = None

MTG_MAGIC = b"\xc1\x59\x41\x0d"
MAT_NAME_MARK = b"\x02\x09\x01"
MAT_NAME_RE = re.compile(rb"\x02\x09\x01([\x20-\x7e]{2,})\x00")
SHADER_RE = re.compile(rb"shader\\[\w\.]+::TShader")
PATH_RE = re.compile(rb"[\x20-\x7e]{3,}")
MACRO_RE = re.compile(r"^[A-Z][A-Z0-9_]{2,}$")

TEX_EXTS = (".tga", ".dds", ".ktx", ".png", ".cube", ".hdr")
# 块内路径相邻间隔实测恒为 6B（`\x00` + 5B 定长字段）；块间最小 100B
BLOCK_GAP = 20

_KIND_SPECIAL = (
    ("caustic", "caustic"),
    ("reflection", "reflection"),
    ("crystal_bump", "normal_detail"),
)


def _classify_tex(path: str) -> str:
    """按文件名后缀推定贴图角色（a=basecolor / n=normal / m=param，含特例前缀）。

    实证命名约定（b_f_3715 系列 112 条路径全部命中）：
      `<base>001a`   → basecolor
      `<base>001m`   → param（金属/粗糙/遮罩打包，m 通道）
      `<base>001s_m` → param（次层/高光遮罩）
      `<base>_h_001n`→ normal（源网格法线）
      `common\\env_map\\*. cube` → 环境立方图 IBL
    """
    low = path.lower().replace("/", "\\")
    ext = os.path.splitext(low)[1]
    stem = os.path.splitext(os.path.basename(low))[0]
    if ext == ".cube":
        return "ibl_cube"
    for key, role in _KIND_SPECIAL:
        if key in stem:
            return role
    if stem.endswith("n"):
        return "normal"
    if "normal" in stem:
        return "normal_detail" if "detail" in stem else "normal"
    if stem.endswith("a"):
        return "basecolor"
    if stem.endswith("m"):
        return "param"
    return "other"


def _runs(b: bytes) -> list:
    return [(m.start(), m.end(), m.group().decode("latin1")) for m in PATH_RE.finditer(b)]


def _read_material_names(b: bytes) -> list:
    out = []
    for m in MAT_NAME_RE.finditer(b):
        name = m.group(1).decode("latin1")
        out.append({"name": name, "off": m.start(), "name_off": m.start() + 4})
    return out


def _read_shaders(b: bytes) -> list:
    return [{"off": m.start(), "shader": m.group().decode("latin1")}
            for m in SHADER_RE.finditer(b)]


def _read_texture_blocks(b: bytes, tail_lo: int) -> list:
    paths = [r for r in _runs(b) if r[0] >= tail_lo and r[2].lower().endswith(TEX_EXTS)]
    blocks, cur, prev_end = [], [], None
    for st, en, s in paths:
        if prev_end is not None and (st - prev_end) > BLOCK_GAP:
            blocks.append(cur)
            cur = []
        cur.append({"path": s, "off": st, "role": _classify_tex(s)})
        prev_end = en
    if cur:
        blocks.append(cur)
    return blocks


def _read_macros(b: bytes, lo: int, hi: int) -> list:
    out = []
    for m in PATH_RE.finditer(b, lo, hi):
        s = m.group().decode("latin1")
        if MACRO_RE.match(s) and s not in out:
            out.append(s)
    return out


def parse_mtg(path: str) -> dict:
    b = open(path, "rb").read()
    if not b.startswith(MTG_MAGIC):
        raise ValueError("不是 mtg（magic=%r）" % b[:4].hex())
    ns = read_names(b) if read_names else {}
    mats = _read_material_names(b)
    if not mats:
        raise ValueError("未找到材料实例名标记 %r" % MAT_NAME_MARK)
    shaders = _read_shaders(b)
    # 贴图块起点 = 首个材料名之后（材料名区 4342..5084，贴图区 8637..）
    tail_lo = shaders[-1]["off"] + len(shaders[-1]["shader"]) if shaders else mats[-1]["off"]
    blocks = _read_texture_blocks(b, tail_lo)
    # 宏块区间：本块首路径 → 下一块首路径（末块到文件尾）
    starts = [blk[0]["off"] for blk in blocks] if blocks else []
    n = len(mats)
    warns = []
    if not (n == len(shaders) == len(blocks)):
        warns.append("数量不齐：材料 %d / 着色器 %d / 贴图块 %d" % (n, len(shaders), len(blocks)))
    out_mats = []
    for i, mat in enumerate(mats):
        sh = shaders[i]["shader"] if i < len(shaders) else None
        tex = blocks[i] if i < len(blocks) else []
        hi = starts[i + 1] if i + 1 < len(starts) else len(b)
        lo = tex[0]["off"] if tex else mat["off"]
        macros = _read_macros(b, min(lo, mat["off"]), hi) if tex else []
        out_mats.append({
            "index": i,
            "name": mat["name"],
            "material_off": mat["off"],
            "shader": sh,
            "shader_name": (os.path.basename(sh).split(".fx")[0].replace("shader\\", "")
                            if sh else None),
            "textures": tex,
            "roles": {r: [t["path"] for t in tex if t["role"] == r]
                      for r in sorted({t["role"] for t in tex})},
            "macros": macros,
        })
    return {
        "file": os.path.abspath(path),
        "size": len(b),
        "magic": b[:4].hex(),
        "kind": (classify_c159(b) if classify_c159 else "material"),
        "name_table": {
            "comp": (ns or {}).get("comp", []),
            "params": (ns or {}).get("params", []),
            "max_index": (ns or {}).get("max_index"),
        },
        "counts": {"materials": n, "shaders": len(shaders), "texture_blocks": len(blocks)},
        "materials": out_mats,
        "warnings": warns,
    }


def material_texture_map(path: str, sub_names=None) -> dict:
    """返回 {子网格序号: 材料}；sub_names 给出时按『子网格文件名后缀 ↔ 材料序号』核对。

    `.mtg` 材料与 `.gim` SubMesh / `.mesh` 子网格按文件序一一对应（实测三处计数一致）。
    sub_names 形如 ['b_f_3715a_0', 'b_f_3715a_1', ...]，用于把序号换成可读名。
    """
    A = parse_mtg(path)
    out = {}
    for i, m in enumerate(A["materials"]):
        key = sub_names[i] if sub_names and i < len(sub_names) else i
        out[key] = m
    return out


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return
    p = args[0]
    A = parse_mtg(p)
    print("== %s  %dB  材料=%d 着色器=%d 贴图块=%d ==" % (
        os.path.basename(p), A["size"], A["counts"]["materials"],
        A["counts"]["shaders"], A["counts"]["texture_blocks"]))
    for m in A["materials"]:
        print("[%2d] %-24s %-32s tex=%d" % (
            m["index"], m["name"], m["shader_name"] or "?", len(m["textures"])))
        for t in m["textures"]:
            print("      %-12s %s" % (t["role"], t["path"]))
        print("      macros: %s" % ", ".join(m["macros"]))
    for w in A["warnings"]:
        print("  ! " + w)
    if "--json" in args:
        out = args[args.index("--json") + 1]
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        json.dump(A, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("JSON ->", out)


if __name__ == "__main__":
    main()
