# -*- coding: utf-8 -*-
r"""安卓《明日之后》热更 GPK（HPGF 块链）逐行载荷解码 + 贴图导出。

## 为什么单独一个模块（2026-10-18 实测裁定）

`gpk_npk_index._gpk_blockchain` 给的行 `off` 是**块内相对位移**，而统一索引
（`unified_index`）当年把 `off + (block_base + 20)` 直接当绝对偏移写库。对
**安卓热更包**来说块基址不是常数（0340_new 有 13 块，块基址 16 / 8744420 /
17372408 … / 253187176），所以「off + 常数」必然只在第 0 块对、在后续块全错。

本模块把 13 个块的 base 显式摊开，逐行按
``载荷绝对起点 = block_base + off + 20`` 计算，并用**行内 20 B 头**自校验：
``(packed@+0, decoded@+4, c1@+8, c2@+12, flag@+16)`` 必须与表里的
``(packed, decoded, _, _, flag)`` 逐字段相等 —— 0340_new 12325/12325、
0341 1745/1745、0339_new 4236/4236 全部通过（0341 另有 1662 行是 pk=0 的空槽）。

## 行内 20 B 头（字节证据，0340_new 行 0）

```
文件偏移 12096 (= block_base 16 + off 12080):
  a0 d7 2a 00  packed    = 2807712
  a0 d7 2a 00  decoded   = 2807712
  58 b3 c3 08  c1        (crc)
  58 b3 c3 08  c2        (crc)
  00 00 00 00  flag      = 0  (未压缩)
载荷 = 12116 起 2807712 B，头 4 字节 46 53 42 35 = "FSB5" (FMOD bank)
```

行 3（fl=12）：头里 packed=12062 / decoded=19280 / flag=0x0c，载荷
``28 b5 2f fd`` = zstd 帧。行 5/6/7 同。

## 压缩标记（flag）实测

| flag | 算法 | 判据 |
|---|---|---|
| 0 | 原样 | 载荷头直接是 DDS/KTX/FSB5/OCTL… |
| 2 | **LZ4 block** | 首字节 token：0xff + 0x12 ⇒ 15+18=33 字面量，恰为
  ``ui/ainpc/img_dinyue_1.png 260 76\n`` 的 33 字节；紧随 ``21 00`` 为匹配偏移 |
| 12 | **zstd 帧** | ``28 b5 2f fd`` |

（历史文档只说 fl=12 是 zstd、fl=2 未解；LZ4 由本模块补上，0339_new 行 0
解压后得 13,500,958 B 的 UI 图集清单，首行即上述 33 字节。）
"""
from __future__ import annotations

import importlib
import struct
from pathlib import Path

__all__ = [
    "KtxInfo", "open_blocks", "iter_entries", "iter_payloads", "list_images",
    "decode_image", "save_png", "parse_ktx", "decompress",
    "ICON_SIZES", "content_kind",
]

#: 本轮要找的图标尺寸（宽, 高）
ICON_SIZES = {(156, 80), (160, 84), (268, 120), (300, 152)}

KTX_ID = b"\xabKTX 11\xbb\r\n\x1a\n"

#: glInternalFormat → (knife, 块宽, 块高)
_ASTC = {0x93B0: (4, 4), 0x93B1: (5, 4), 0x93B2: (5, 5), 0x93B3: (6, 5),
         0x93B4: (6, 6), 0x93B5: (8, 5), 0x93B6: (8, 6), 0x93B7: (8, 8),
         0x93B8: (10, 5), 0x93B9: (10, 6), 0x93BA: (10, 8), 0x93BB: (10, 10),
         0x93BC: (12, 10), 0x93BD: (12, 12)}
#: KTX1 glInternalFormat 名字（只列本批出现过的 + 常见兜底）
GL_NAMES = {0x9272: "RG11_EAC", 0x9274: "RGB8_ETC2", 0x9278: "RGBA8_ETC2_EAC",
            0x8D64: "ETC1_RGB8", 0x83F1: "DXT1", 0x83F2: "DXT3", 0x83F3: "DXT5",
            0x8D64: "ETC1"}
for _k, (_bw, _bh) in _ASTC.items():
    GL_NAMES[_k] = "ASTC_%dx%d" % (_bw, _bh)


# ───────────────────────────────────────────── 容器 / 块链
def _reader():
    """复用已被 230 万行验证的块链读取器（不复制 AES/表解析逻辑）。"""
    mod = importlib.import_module("toolkit_core.unified_index")
    return mod.load_verified_index_module()


def open_blocks(path):
    """→ (rec, spans)；spans = [(row_lo, row_hi, block_base), ...]。"""
    rec, factory, _blocks = _reader()._gpk_blockchain(str(path))
    spans, acc = [], 0
    for b in rec["blocks"]:
        spans.append((acc, acc + int(b["entries"]), int(b["base"])))
        acc += int(b["entries"])
    return rec, spans, factory


def _base_of(spans, row):
    for lo, hi, base in spans:
        if lo <= row < hi:
            return base
    return spans[-1][2] if spans else 16


# ───────────────────────────────────────────── 解压
_ZSTD = None


def decompress(payload: bytes, flag: int, decoded_size: int) -> bytes | None:
    """按 flag 解压；解不出返回 None（不抛、不猜）。"""
    global _ZSTD
    if flag == 0:
        return payload
    if flag == 12:
        if payload[:4] != b"\x28\xb5\x2f\xfd":
            return None
        if _ZSTD is None:
            import zstandard as zstd
            _ZSTD = zstd.ZstdDecompressor()
        try:
            return _ZSTD.decompress(payload, max_output_size=max(decoded_size, 1) + 65536,
                                    allow_extra_data=True)
        except Exception:                                    # noqa: BLE001
            return None
    if flag == 2:
        import lz4.block
        for extra in (0, 64, -16):
            try:
                out = lz4.block.decompress(payload, uncompressed_size=max(decoded_size + extra, 1))
                if decoded_size in (0, len(out)):
                    return out
            except Exception:                                # noqa: BLE001
                continue
        return None
    return None


# ───────────────────────────────────────────── 内容识别
_MAGIC = [(b"\xabKTX", "ktx"), (b"DDS ", "dds"), (b"\x89PNG", "png"),
          (b"FSB5", "fmod-bank"), (b"OCTL", "mesh-octl"), (b"PK\x03\x04", "zip"),
          (b"\x1f\x8b", "gzip"), (b"<FxGroup", "fx-group"), (b"CVIS", "cvis"),
          (b"RIFF", "riff"), (b"OggS", "ogg"), (b"{\"", "json")]


def content_kind(data: bytes, flag: int = 0) -> str:
    """载荷内容格式标签（用魔数，不看扩展名）。"""
    for magic, name in _MAGIC:
        if data.startswith(magic):
            return name
    if data[:4] == b"\x0b\x00\x00\x00":
        return "anim?"
    if data[:4] == b"\xc1\x59\x41\x0d" or data[:4] == b"\x71\xc1\x59\x41":
        return "neox-name-table"
    if data[:4] in (b"\x4f\x43\x54\x4c",):
        return "mesh-octl"
    if len(data) > 8 and data[:4] == struct.pack("<I", len(data) - 8):
        return "neox-blob"
    return "bin"


# ───────────────────────────────────────────── 逐行
def iter_entries(path, *, include_empty: bool = False, verify: bool = False):
    """逐行产出 dict：row/fid/off/header_off/packed/decoded/flag/compression/payload/kind。

    payload 是**解压后**的字节；解压失败时 payload=None、error 里写原因。
    `verify=True` 时把行内 20 B 头与表字段比对，记进 header_ok。
    """
    rec, spans, factory = open_blocks(path)
    blob = Path(path).read_bytes()
    for row, fid, off, packed, decoded, flag in factory():
        if packed == 0 and not include_empty:
            continue
        base = _base_of(spans, row)
        h = base + off
        ent = {"row": row, "fid": fid, "off": off, "block_base": base,
               "header_off": h, "packed": packed, "decoded": decoded, "flag": flag}
        if packed == 0:
            ent.update(payload=b"", kind="empty", compression="none", header_ok=None)
            yield ent
            continue
        if h + 20 > len(blob):
            ent.update(payload=None, kind="oob", compression="none", header_ok=False,
                       error="header beyond EOF")
            yield ent
            continue
        hp, hd, c1, c2, hf = struct.unpack_from("<5I", blob, h)
        ent["header_ok"] = (hp == packed and hd == decoded and hf == flag)
        ent["c1"], ent["c2"] = c1, c2
        pay = blob[h + 20: h + 20 + packed]
        data = decompress(pay, flag, decoded)
        if data is None:
            ent.update(payload=None, kind="undecoded", compression="unknown",
                       error="decompress failed (flag=%d)" % flag)
            yield ent
            continue
        ent["compression"] = {0: "none", 2: "lz4", 12: "zstd"}.get(flag, "flag%d" % flag)
        ent["payload"] = data
        ent["kind"] = content_kind(data, flag)
        yield ent


def iter_payloads(path, **kw):
    """→ (row, fid, payload_bytes, kind)。空槽（pk=0）默认跳过。"""
    for e in iter_entries(path, **kw):
        yield e["row"], e["fid"], e["payload"], e["kind"]


# ───────────────────────────────────────────── KTX / 图片
class KtxInfo(dict):
    __getattr__ = dict.get


def parse_ktx(data: bytes):
    """KTX1 头解析 → KtxInfo（width/height/format/mips/faces/data_off/image_size）。"""
    if len(data) < 68 or not data.startswith(KTX_ID):
        return None
    (endian, gltype, typesize, glfmt, ifmt, basefmt, w, h, depth,
     arr, faces, mips, kv) = struct.unpack_from("<13I", data, 12)
    off = 64 + kv
    if off + 4 > len(data):
        return None
    img = struct.unpack_from("<I", data, off)[0]
    return KtxInfo(width=w, height=h, depth=depth, array=arr, faces=faces, mips=mips,
                   gl_type=gltype, gl_format=glfmt, gl_internal=ifmt,
                   fmt_name=GL_NAMES.get(ifmt, "0x%X" % ifmt),
                   data_off=off + 4, image_size=img, kv_bytes=kv, endian=endian)


def _ktx_rgba(data: bytes, info):
    """KTX mip0 → (h,w,4) uint8 RGBA。texture2ddecoder 输出 BGRA，这里换回 RGBA。"""
    import numpy as np
    import texture2ddecoder as t2d
    w, h, ifmt = info["width"], info["height"], info["gl_internal"]
    src = data[info["data_off"]: info["data_off"] + info["image_size"]]
    if ifmt in _ASTC:
        bw, bh = _ASTC[ifmt]
        raw = t2d.decode_astc(src, w, h, bw, bh)
        rgba = np.frombuffer(raw, np.uint8).reshape(h, w, 4)[..., [2, 1, 0, 3]]
        return rgba
    if ifmt == 0x9278:                      # ETC2 RGBA8 EAC（RGB 8B + EAC alpha 8B）
        # ★ 实测：decode_eacrg 把整块当「双 8B 通道」解，得到红绿花屏；
        #   正确入口是 decode_etc2a8（RGB 走 ETC2 + 后 8B 走 EAC alpha）。
        raw = t2d.decode_etc2a8(src, w, h)
    elif ifmt == 0x9274:                    # ETC2 RGB8
        raw = t2d.decode_etc2(src, w, h)
    elif ifmt == 0x9272:                    # RG11 EAC（双通道，法线/粗糙度）
        raw = t2d.decode_eacr(src, w, h)
        arr = np.frombuffer(raw, np.uint8)
        # texture2ddecoder 统一按 4 B/px 输出：解码出的两通道落在前两个字节
        arr = arr.reshape(h, w, arr.size // (w * h)) if arr.size % (w * h) == 0 else None
        if arr is None or arr.shape[2] < 2:
            raise ValueError("RG11_EAC 输出尺寸不自洽")
        rgba = np.empty((h, w, 4), np.uint8)
        rgba[..., 0] = arr[..., 0]
        rgba[..., 1] = arr[..., 1]
        rgba[..., 2] = 0
        rgba[..., 3] = 255
        return rgba
    elif ifmt == 0x8D64:                    # ETC1
        raw = t2d.decode_etc1(src, w, h)
    elif ifmt in (0x83F1, 0x83F2, 0x83F3):  # DXT1/3/5
        fn = {0x83F1: t2d.decode_bc1, 0x83F2: t2d.decode_bc3, 0x83F3: t2d.decode_bc3}[ifmt]
        raw = fn(src, w, h)
    elif info["gl_type"] == 0 and info["gl_format"] == 0:
        # 未压缩：按 bpp 猜（只信任尺寸自洽的）
        n = info["image_size"] // max(w * h, 1)
        arr = np.frombuffer(src[:w * h * n], np.uint8).reshape(h, w, n)
        rgba = np.empty((h, w, 4), np.uint8)
        rgba[..., :min(n, 3)] = arr[..., :min(n, 3)]
        rgba[..., 3] = arr[..., 3] if n >= 4 else 255
        return rgba
    else:
        raise ValueError("未支持的 KTX 格式 0x%X" % ifmt)
    arr = np.frombuffer(raw, np.uint8).reshape(h, w, 4)
    return arr[..., [2, 1, 0, 3]]           # BGRA → RGBA


def list_images(path, *, sizes=None):
    """扫一个包里的所有图片行 → dict(row,fid,kind,width,height,fmt,mips,data,...)。

    kind ∈ {'ktx','dds','png'}；sizes 给了 (w,h) 集合时只留命中的。
    DDS/PNG 的宽高从文件头取，KTX 从 KTX 头取。
    """
    for e in iter_entries(path):
        data = e.get("payload")
        if not data:
            continue
        rec = {"row": e["row"], "fid": e["fid"], "flag": e["flag"],
               "compression": e["compression"], "packed": e["packed"], "data": data}
        if data.startswith(b"\xabKTX"):
            info = parse_ktx(data)
            if not info:
                continue
            rec.update(kind="ktx", width=info["width"], height=info["height"],
                       fmt=info["fmt_name"], mips=info["mips"], info=info)
        elif data.startswith(b"DDS "):
            if len(data) < 24:
                continue
            h, w = struct.unpack_from("<II", data, 12)
            rec.update(kind="dds", width=w, height=h, fmt="dds")
        elif data.startswith(b"\x89PNG"):
            w, h = struct.unpack_from(">II", data, 16)
            rec.update(kind="png", width=w, height=h, fmt="png")
        else:
            continue
        if sizes and (rec["width"], rec["height"]) not in sizes:
            continue
        yield rec


def decode_image(rec):
    """图片记录 → (h,w,4) uint8 RGBA。"""
    data = rec["data"]
    if rec["kind"] == "ktx":
        return _ktx_rgba(data, rec["info"])
    if rec["kind"] == "dds":
        import sys
        d = str(Path(__file__).resolve().parents[2] / "02_图文音频渲染" / "皮肤链与渲染")
        if d not in sys.path:
            sys.path.insert(0, d)
        from dds_rgba_canonical import decode_dds_rgba_u8
        u8, _prov = decode_dds_rgba_u8(data, verify_oiio=False)
        return u8
    if rec["kind"] == "png":
        import io
        import numpy as np
        from PIL import Image
        return np.asarray(Image.open(io.BytesIO(data)).convert("RGBA"))
    raise ValueError("unknown kind %r" % rec["kind"])


def save_png(rec, out_path, *, background=(255, 255, 255, 255)):
    """RGBA → 白底合成 PNG（透明像素的 RGB 是垃圾，必须按 alpha 合成）。"""
    import numpy as np
    from PIL import Image
    rgba = decode_image(rec)
    a = rgba[..., 3:4].astype(np.uint16)
    bg = np.array(background[:3], np.uint16)
    rgb = (rgba[..., :3].astype(np.uint16) * a + bg * (255 - a) + 127) // 255
    img = Image.fromarray(np.dstack([rgb.astype(np.uint8), np.full_like(rgb[..., :1], 255, np.uint8)]))
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    return out_path


def dump_entry(e, out_dir, name=None):
    """单行载荷落盘（按内容格式挑扩展名）。"""
    ext = {"ktx": ".ktx", "dds": ".dds", "png": ".png", "zip": ".zip",
           "fmod-bank": ".fsb", "mesh-octl": ".octl", "fx-group": ".fxg",
           "json": ".json"}.get(e["kind"], ".bin")
    p = Path(out_dir) / (name or "%06d_%016X%s" % (e["row"], e["fid"], ext))
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(e["payload"])
    return p
