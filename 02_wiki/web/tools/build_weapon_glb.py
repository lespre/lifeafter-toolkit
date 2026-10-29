# -*- coding: utf-8 -*-
"""武器本体网格 → GLB（几何 + UV + 计算法线，中性材质）。

用途：在贴图未下发时先看形体。真彩渲染仍需 mtg + 贴图链。
用法：python build_weapon_glb.py <in.mesh> <out.glb> [--white]
"""
from __future__ import annotations

import json
import struct
import sys
import pathlib

import numpy as np


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import TOOLKIT_DIR  # noqa: E402
sys.path.insert(0, str(TOOLKIT_DIR / "工具库/02_图文音频渲染/皮肤链与渲染"))
import mesh_parse2 as MP  # noqa: E402


def vertex_normals(P: np.ndarray, F: np.ndarray) -> np.ndarray:
    n = np.zeros_like(P, dtype=np.float64)
    tri = P[F]
    fn = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    for k in range(3):
        np.add.at(n, F[:, k], fn)
    ln = np.linalg.norm(n, axis=1, keepdims=True)
    ln[ln == 0] = 1.0
    return (n / ln).astype(np.float32)


def main() -> int:
    mesh, out = sys.argv[1], sys.argv[2]
    P, uv, F, meta = MP.parse_mesh2(mesh)
    P = np.asarray(P, dtype=np.float32)
    uv = np.asarray(uv, dtype=np.float32)
    F = np.asarray(F, dtype=np.uint32)
    N = vertex_normals(P, F)

    # 居中
    c = (P.min(0) + P.max(0)) / 2
    P = P - c

    bufs, views, accs, prims = [], [], [], []
    off = 0

    def add(arr: np.ndarray, target: int, ctype: int, typ: str, count: int):
        nonlocal off
        b = arr.tobytes()
        bufs.append(b)
        views.append({"buffer": 0, "byteOffset": off, "byteLength": len(b), "target": target})
        accs.append({"bufferView": len(views) - 1, "componentType": ctype,
                     "count": count, "type": typ,
                     **({"min": arr.min(0).tolist(), "max": arr.max(0).tolist()} if typ == "VEC3" and target == 34962 and arr.dtype == np.float32 and len(arr.shape) == 2 and arr.shape[1] == 3 and arr is P else {})})
        off += len(b)
        return len(accs) - 1

    # 只导出 POSITION / NORMAL / TEXCOORD_0 / indices
    aP = add(P, 34962, 5126, "VEC3", len(P))
    accs[aP]["min"] = P.min(0).tolist()
    accs[aP]["max"] = P.max(0).tolist()
    aN = add(N, 34962, 5126, "VEC3", len(N))
    aU = add(uv, 34962, 5126, "VEC2", len(uv))
    aI = add(F.astype(np.uint32), 34963, 5125, "SCALAR", F.size)

    prims.append({"attributes": {"POSITION": aP, "NORMAL": aN, "TEXCOORD_0": aU},
                  "indices": aI, "material": 0, "mode": 4})

    gltf = {
        "asset": {"version": "2.0", "generator": "la-weapon-geom"},
        "scene": 0, "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0, "name": pathlib.Path(mesh).stem}],
        "meshes": [{"primitives": prims}],
        "materials": [{"name": "neutral", "pbrMetallicRoughness": {
            "baseColorFactor": [0.72, 0.73, 0.75, 1.0],
            "metallicFactor": 0.15, "roughnessFactor": 0.75}, "doubleSided": True}],
        "buffers": [{"byteLength": sum(len(b) for b in bufs)}],
        "bufferViews": views, "accessors": accs,
        "extras": {"source_mesh": mesh, "verts": int(len(P)), "tris": int(len(F)),
                   "vertex_count": int(meta.get("tv", 0)), "subs": meta.get("subs"),
                   "note": "几何预览：法线由网格重算，贴图/材质未附带"},
    }
    js = json.dumps(gltf, ensure_ascii=False, separators=(",", ":")).encode()
    js += b" " * ((-len(js)) % 4)
    binb = b"".join(bufs)
    total = 12 + 8 + len(js) + 8 + len(binb)
    with open(out, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, total))
        f.write(struct.pack("<II", len(js), 0x4E4F534A)); f.write(js)
        f.write(struct.pack("<II", len(binb), 0x004E4942)); f.write(binb)
    print(json.dumps({"out": out, "bytes": pathlib.Path(out).stat().st_size,
                      "verts": int(len(P)), "tris": int(len(F))}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
