# -*- coding: utf-8 -*-
"""资源格式识别：不看扩展名，看文件头 + 尺寸 + 边缘特征。

能识别的形态
------------
* ``png``        真 PNG（浏览器可直读）
* ``dds_bc7``    DDS 容器（BC7/BC5/BC1 等），需解码成 PNG
* ``ktx_etc2``   KTX 容器（ETC2_EAC 等），需解码
* ``atlas_page`` 图集页：多帧平铺（宽高比异常 或 单边 >1500）
* ``part_sheet`` 零件条：极扁（宽高比 >3）的小图，通常只有部件
* ``unknown``

用途：补图流水线在“导出之后”判断这张图能不能直接用，避免把图集当单图挂上去。
"""
from __future__ import annotations

import pathlib
from dataclasses import dataclass

PNG_MAGIC = b"\x89PNG"
DDS_MAGIC = b"DDS "
KTX_MAGIC = b"\xabKTX"
JPEG_MAGIC = b"\xff\xd8\xff"


@dataclass
class Probe:
    kind: str
    width: int = 0
    height: int = 0
    note: str = ""

    @property
    def aspect(self) -> float:
        return (self.width / self.height) if self.height else 0.0

    def usable_as_icon(self) -> bool:
        return self.kind in ("png", "jpeg")


def probe(path: str | pathlib.Path) -> Probe:
    p = pathlib.Path(path)
    try:
        head = p.read_bytes()[:16]
    except OSError:
        return Probe("unknown", note="读不到文件")

    kind = "unknown"
    if head.startswith(PNG_MAGIC):
        kind = "png"
    elif head.startswith(DDS_MAGIC):
        kind = "dds_bc7"
    elif head.startswith(KTX_MAGIC):
        kind = "ktx_etc2"
    elif head.startswith(JPEG_MAGIC):
        kind = "jpeg"

    w = h = 0
    try:
        from PIL import Image
        w, h = Image.open(p).size
    except Exception:
        pass

    if kind in ("png", "jpeg") and w and h:
        if h and w / h > 3:
            return Probe("part_sheet", w, h, "极扁，疑似零件条")
        if w / h > 1.8 or max(w, h) > 1500:
            return Probe("atlas_page", w, h, "尺寸异常，疑似图集页")
    return Probe(kind, w, h)
