# -*- coding: utf-8 -*-
r"""解码产物 → 可解析形态的规范化层（需求：解码链不再丢出「奇怪格式」）。

设计约定
--------
解码器解出的每一个条目，在交给用户/落盘之前【必须】过一遍 :func:`normalize`。
它保证返回一个 :class:`Normalized`，里面至少有：

* ``kind``   —— 可解析类型之一：``text`` / ``json`` / ``paths`` / ``image`` /
  ``shader`` / ``audio`` / ``video`` / ``container`` / ``data`` / ``unknown``
* ``text``   —— 可直接读的文本（没有则为 None）
* ``paths``  —— 内嵌的【资源引用路径】（可为空表）
* ``meta``   —— 结构信息：魔数、字段名、尺寸、熵、可打印率等，全部是标量，便于序列化

设计原则
--------
1. **能读的就给文本**：``.c159`` / ``.bin`` 这类 NeoX 字段序列化，抽出字段名与内嵌路径，
   输出成 JSON 文本，而不是丢一个二进制块。
2. **能画的就是图**：DDS/PNG/JPG 不改内容，只报尺寸与格式，交给图像管线。
3. **不能读的要说清楚**：``.ccaa5566``（着色器字节码）明确标 ``shader`` +
   证据（``TEXCOORD`` / ``float4`` / ``SV_Position`` …），而不是叫它 ``bin``。
4. **不硬安名字**：认不出就 ``unknown``，并附熵与可打印率，方便下一步判断。

依据
----
* ``.c159``：取样 2,000 个 → 5,899 种路径串；撞库 400 条命中 308（77%）。
* ``.bin``：取样 12 个 → 5 个含路径，熵 5.32 / 可打印 36%（有结构明文容器）。
* ``.ccaa5566``：头 = 魔数 + u32 版本(2) + u32 版本(2) + 零填充；载荷内是 DXBC 级标识符。
* ``.octl`` / ``.cvis``：魔数统一，熵 6.01 / 4.22，无可提取路径 ⇒ 结构逆向待续。
"""

from __future__ import annotations

import json
import math
import re
import struct
import zlib
from collections import Counter
from dataclasses import dataclass, field, asdict
from typing import Any, Optional

from . import bulk

__all__ = ["Normalized", "normalize", "to_json", "IMAGE_EXTS", "TEXT_EXTS"]

IMAGE_EXTS = {".dds", ".png", ".jpg", ".jpeg", ".tga", ".webp", ".ktx", ".ktx2"}
TEXT_EXTS = {".text", ".txt", ".xml", ".json", ".ini", ".csv", ".atlas"}

# NeoX 字段序列化的字段名特征（c159 / bin 里成片出现）
_FIELD_NAME_RE = re.compile(rb"[A-Za-z_][A-Za-z0-9_]{2,40}")


def _entropy(b: bytes, cap: int = 65536) -> float:
    b = b[:cap]
    if not b:
        return 0.0
    c = Counter(b)
    n = len(b)
    return -sum((v / n) * math.log2(v / n) for v in c.values())


def _printable(b: bytes, cap: int = 65536) -> float:
    b = b[:cap]
    if not b:
        return 0.0
    return sum(1 for x in b if 32 <= x < 127 or x in (9, 10, 13)) / len(b)


@dataclass
class Normalized:
    """规范化后的解码产物。所有字段都可 JSON 序列化。"""

    kind: str
    ext: str = ""
    text: Optional[str] = None
    paths: list[str] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)
    note: str = ""

    def as_dict(self) -> dict:
        return asdict(self)


def _field_names(data: bytes, limit: int = 40) -> list[str]:
    """抽出 NeoX 字段序列化里成片出现的字段名（按出现频次降序、去重）。"""
    c: Counter[str] = Counter()
    for m in _FIELD_NAME_RE.finditer(data[:2_000_000]):
        s = m.group(0).decode("ascii", "ignore")
        if len(s) >= 3:
            c[s] += 1
    return [k for k, _ in c.most_common(limit)]


def _image_meta(data: bytes) -> Optional[dict]:
    if data[:4] == b"DDS " and len(data) >= 20:
        # ★ DDS_HEADER：偏移 12 = 高、偏移 16 = 宽（不是反过来）
        h = struct.unpack_from("<I", data, 12)[0]
        w = struct.unpack_from("<I", data, 16)[0]
        return {"format": "dds", "width": w, "height": h}
    if data[:8] == b"\x89PNG\r\n\x1a\n" and len(data) >= 24:
        w, h = struct.unpack_from(">II", data, 16)
        return {"format": "png", "width": w, "height": h}
    if data[:2] == b"\xff\xd8":
        return {"format": "jpeg"}
    return None


def normalize(data: bytes, ext: str = "") -> Normalized:
    r"""把解码产物规范化成【可解析形态】。

    :param data: 解码后的原始字节
    :param ext:  容器里推断出的扩展名（如 ``".c159"``），仅作提示
    :returns: :class:`Normalized`
    """
    ext = (ext or "").lower()
    if not data:
        return Normalized(kind="empty", ext=ext, note="空载荷")

    # ── 1. 先看是不是图（图不改内容，只报尺寸） ──
    im = _image_meta(data)
    if im:
        return Normalized(kind="image", ext=ext, meta=im, note="图像资源，交给图像管线")

    # ── 2. .c159：NeoX 字段序列化 → 抽字段名 + 内嵌路径 → 输出可读 JSON ──
    if data[:4] == b"\xc1\x59\x41\x0d":
        paths = bulk.extract_c159_paths(data)
        fields = _field_names(data)
        body = {
            "type": "neox_field_serialized",
            "magic": "c159410d",
            "fields": fields,
            "referenced_paths": paths,
            "path_count": len(paths),
            "bytes": len(data),
        }
        return Normalized(
            kind="json",
            ext=ext or ".c159",
            text=json.dumps(body, ensure_ascii=False, indent=1),
            paths=paths,
            meta={"magic": "c159410d", "fields": fields[:20], "path_count": len(paths)},
            note="NeoX 字段序列化文本：字段名 + 资源引用路径已抽出，原样内容不再是黑盒",
        )

    # ── 3. .ccaa5566：着色器字节码 → 明确标注，不叫 bin ──
    if data[:4] == b"\xcc\xaa\x55\x66":
        vers = []
        if len(data) >= 12:
            vers = list(struct.unpack_from("<II", data, 4))
        return Normalized(
            kind="shader",
            ext=ext or ".ccaa5566",
            meta={"magic": "ccaa5566", "versions": vers, "bytes": len(data),
                  "hint": "DXBC 级标识符：TEXCOORD / float4 / NeoxUBOLocal / SV_Position"},
            note="编译后的着色器字节码（GPU 程序），无路径信息、不做文件名复原",
        )

    # ── 4. .octl / .cvis：有魔数、无引用表 → 报结构，等结构逆向 ──
    if data[:4] == b"OCTL":
        return Normalized(kind="container", ext=ext or ".octl",
                          meta={"magic": "OCTL", "bytes": len(data),
                                "block_tags": "SP / LDGP / MH / LO"},
                          note="OCTL 分块容器（块标签已知，块内结构待逆向）")
    if data[:4] == b"CVIS":
        return Normalized(kind="container", ext=ext or ".cvis",
                          meta={"magic": "CVIS", "bytes": len(data),
                                "entropy": round(_entropy(data), 2)},
                          note="CVIS（未见文档；同容器内成片出现，待定）")

    # ── 5. .bin / 其它：通用路径提取 + 分类 ──
    paths = bulk.extract_bin_paths(data)
    ent = _entropy(data)
    pr = _printable(data)

    # 压缩流：认出来就说明白，并试着解开
    for name, head, fn in (
        ("zstd", b"\x28\xb5\x2f\xfd", None),
        ("zlib", b"\x78\xda", lambda b: zlib.decompress(b)),
        ("zlib", b"\x78\x9c", lambda b: zlib.decompress(b)),
        ("gzip", b"\x1f\x8b", lambda b: zlib.decompress(b, 16 + zlib.MAX_WBITS)),
    ):
        if data.startswith(head):
            meta = {"compression": name, "bytes": len(data)}
            if fn is not None:
                try:
                    out = fn(data)
                    inner = normalize(out, "")
                    meta["decompressed_bytes"] = len(out)
                    meta["inner_kind"] = inner.kind
                    return Normalized(kind=inner.kind if inner.kind != "unknown" else "data",
                                      ext=ext, text=inner.text, paths=inner.paths,
                                      meta=meta, note="解压后规范化：%s" % inner.kind)
                except Exception:
                    pass
            return Normalized(kind="data", ext=ext, meta=meta,
                              note="%s 压缩流（未解开）" % name)

    # 可读文本
    if pr >= 0.85 and len(data) > 16:
        try:
            txt = data.decode("utf-8")
        except UnicodeDecodeError:
            txt = data.decode("utf-8", "replace")
        if paths:
            return Normalized(kind="json", ext=ext or ".text", paths=paths,
                              text=json.dumps(
                                  {"type": "text_with_paths", "referenced_paths": paths},
                                  ensure_ascii=False, indent=1),
                              meta={"printable": round(pr, 3), "path_count": len(paths)},
                              note="可读文本 + 内嵌引用路径")
        return Normalized(kind="text", ext=ext or ".text", text=txt,
                          meta={"printable": round(pr, 3)}, note="可读文本")

    # 有结构、有路径 → 抽成 JSON 才是「可解析」
    if paths:
        body = {
            "type": "neox_binary_with_refs",
            "entropy": round(ent, 2),
            "printable": round(pr, 3),
            "referenced_paths": paths,
            "path_count": len(paths),
            "bytes": len(data),
        }
        return Normalized(kind="json", ext=ext or ".bin",
                          text=json.dumps(body, ensure_ascii=False, indent=1),
                          paths=paths,
                          meta={"entropy": round(ent, 2), "printable": round(pr, 3),
                                "path_count": len(paths)},
                          note="有结构二进制容器：内嵌引用路径已抽出成 JSON")

    # 最后兜底：不硬安名字，把可判断的量都报出来
    return Normalized(kind="unknown", ext=ext,
                      meta={"bytes": len(data), "entropy": round(ent, 2),
                            "printable": round(pr, 3),
                            "head_hex": data[:16].hex()},
                      note="未识别（已报熵/可打印率/头字节，供下一步判断）")


def to_json(n: Normalized, indent: int = 1) -> str:
    """把规范化结果序列化成 JSON 文本（落盘用）。"""
    return json.dumps(n.as_dict(), ensure_ascii=False, indent=indent)
