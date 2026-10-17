# -*- coding: utf-8 -*-
r"""VKPL = NeoX 的 **Vulkan SPIR-V 着色器容器**（PC 客户端走 Vulkan 后端时下发）。

定证（2026-10-17，`Documents\gres\0007.gpk` 本波 37,867 条逐条自检）：

```
头 0x24(36) 字节：
  0x00  'VKPL'                 magic
  0x04  u32 版本 = 1
  0x08  u32 模块数 N（实测 1..2）
  0x0C  u32 0
  0x10  u32 0
  0x14  u32 0
  0x18  u32 0
  0x1C  u32 附加标志（实测 0 或 2；不参与定位）
  0x20  u32 模块 1 的字节数
之后逐模块：
  [u32 尺寸][模块字节]       模块头恒为 SPIR-V magic 0x07230203
  模块之间再夹 4 字节（实测恒 = 1）；最后一个模块后面没有
```

⇒ 与 `.ccaa5566`（DXBC/D3D 后端）是同一件事的两条后端；模块内以 SPIR-V
`OpEntryPoint` 的执行模型可判阶段（0=Vertex 1=TessControl 2=TessEval 3=Geometry
4=Fragment 5=GLCompute 6=Kernel）。
"""
from __future__ import annotations

import struct
from pathlib import Path
from typing import Dict, List, Tuple

SPIRV_MAGIC = b"\x03\x02\x23\x07"          # 0x07230203 小端
STAGE_NAMES = {0: "vert", 1: "tesc", 2: "tese", 3: "geom", 4: "frag", 5: "comp", 6: "kern"}
OP_ENTRY_POINT = 15


def is_vkpl(buf: bytes) -> bool:
    return buf[:4] == b"VKPL"


def _scan_magics(buf: bytes) -> List[int]:
    out, i = [], buf.find(SPIRV_MAGIC)
    while i >= 0:
        out.append(i)
        i = buf.find(SPIRV_MAGIC, i + 1)
    return out


def stage_of(module: bytes) -> str | None:
    """从 SPIR-V 指令流里读 OpEntryPoint 的执行模型 → 阶段名。"""
    if not module.startswith(SPIRV_MAGIC) or len(module) < 20:
        return None
    off = 20                                     # 跳过 5 个 header word
    while off + 4 <= len(module):
        w = struct.unpack_from("<I", module, off)[0]
        wc, op = w >> 16, w & 0xFFFF
        if wc == 0:                              # 越界/畸形，别死循环
            return None
        if op == OP_ENTRY_POINT and off + 8 <= len(module):
            model = struct.unpack_from("<I", module, off + 4)[0]
            return STAGE_NAMES.get(model, "stage%d" % model)
        off += wc * 4
    return None


def parse(buf: bytes) -> dict:
    """解一条 VKPL → {ok, version, count, modules:[{offset,size,stage}], why}。

    两路取模（先按结构走，结构对不上再按 magic 扫描兜底），并给出自检字段：
    `struct_ok`（逐条尺寸自洽）/ `scan_ok`（magic 数 == 声明的模块数）。
    """
    if not is_vkpl(buf):
        return {"ok": False, "why": "magic 不是 VKPL"}
    ver, cnt = struct.unpack_from("<II", buf, 4)
    mods: List[dict] = []
    p = 0x20
    struct_ok = True
    for _ in range(cnt):
        if p + 4 > len(buf):
            struct_ok = False
            break
        (sz,) = struct.unpack_from("<I", buf, p)
        body = buf[p + 4: p + 4 + sz]
        if len(body) != sz or not body.startswith(SPIRV_MAGIC):
            struct_ok = False
            break
        mods.append({"offset": p + 4, "size": sz, "stage": stage_of(body)})
        p += 4 + sz + 4                          # 跳过模块间的 4 字节
    magics = _scan_magics(buf)
    scan_ok = len(magics) == cnt
    if not struct_ok or not mods:
        if scan_ok:                              # 兜底：按 magic 切（不含头尾夹字节）
            mods = []
            for k, m in enumerate(magics):
                end = magics[k + 1] - 4 if k + 1 < len(magics) else len(buf)
                body = buf[m:end]
                mods.append({"offset": m, "size": len(body), "stage": stage_of(body)})
        else:
            return {"ok": False, "why": "结构不符且 magic 数（%d）≠ 声明模块数（%d）" % (len(magics), cnt)}
    return {"ok": True, "version": ver, "count": cnt, "modules": mods,
            "struct_ok": struct_ok, "scan_ok": scan_ok, "bytes": len(buf)}


def extract(buf: bytes, out_dir: Path, stem: str, write: bool = True) -> List[dict]:
    """解一条 VKPL 并把模块落成 `.spv`（文件名带阶段）。返回条目清单。"""
    info = parse(buf)
    if not info.get("ok"):
        return []
    out_dir.mkdir(parents=True, exist_ok=True)
    res = []
    for k, m in enumerate(info["modules"]):
        ext = m["stage"] or "spv"
        fp = out_dir / ("%s_m%d.%s.spv" % (stem, k, ext))
        if write:
            fp.write_bytes(buf[m["offset"]:m["offset"] + m["size"]])
        res.append({"index": k, "stage": m["stage"], "size": m["size"],
                    "file": str(fp) if write else None})
    return res
