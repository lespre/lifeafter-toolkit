# -*- coding: utf-8 -*-
"""NPK 资源包探针 v2：32B 头（16B 魔数 + 16B 文件哈希?），payload 从偏移 32 开始。

只读 E:\\mrzh；产物写本目录。
"""
import json, hashlib
from pathlib import Path

SRC = Path(r"E:\mrzh\res")
OUT = Path(__file__).parent
MAGIC = bytes.fromhex("fe0eb04e2e149972c37c644bea50f715")
PROBES = [
    "ui\\huodong_icon.npk", "ui\\item_icon.npk", "ui\\all_pc.npk",
    "ui\\building_icon.npk", "ui\\haiyang.npk", "ui\\bigmap.npk",
    "ui\\all_txt_meishuzi_icon.npk", "model\\common.npk",
    "character\\players.npk", "building\\yingdi_gongneng.npk",
    "scene\\pve_new.npk",
]

def sniff(data: bytes) -> str:
    if data[:8] == b"\x89PNG\r\n\x1a\n": return "PNG"
    if data[:4] == b"ftyp": return "MP4"
    if data[:4] in (b"DDS ", b"DX10"): return "DDS"
    if data[:2] == b"\x76\x71": return "QOI"
    if data[:4] == b"PK\x03\x04": return "ZIP"
    if data[:10] == b"KTX  11\xdd\x88": return "KTX"
    if data[:16] == b"\x00\x01\x00\x00\x01\x00\x00\x00": return "KTX2-ish"
    if data[:4] == b"OGL ": return "OGL"
    if data[:6] in (b"ASTC", b"ETC1", b"Zstd"): return data[:4].hex()
    if data[:4] == b"\x28\xb5\x2f\xf8": return "Zstd"
    if data[:4] in (b"\x1f\x8b\x08\x00",): return "GZIP"
    if data[:2] == b"\x78\x9c" or data[:2] == b"\x78\x01" or data[:2] == b"\x78\xda": return "ZLIB"
    return "unknown"

report = {"magic": MAGIC.hex(), "header_size": 32, "probes": []}
for rel in PROBES:
    p = SRC / rel
    e = {"path": rel, "bytes": p.stat().st_size}
    with p.open("rb") as f:
        head = f.read(32)
        payload_head = f.read(64)
    e["magic_ok"] = head[:16] == MAGIC
    e["hash_field_hex"] = head[16:32].hex()
    e["payload_sig"] = sniff(payload_head)
    e["payload_head_hex"] = payload_head[:48].hex()
    e["payload_head_repr"] = repr(payload_head[:48])
    # PNG 时: 解析首 chunk 尺寸
    if e["payload_sig"] == "PNG":
        import struct
        w, h, bitdepth, colortype = struct.unpack_from(">IIBB", payload_head, 16)
        e["png_width"] = w
        e["png_height"] = h
        e["png_bitdepth"] = bitdepth
        e["png_colortype"] = colortype
    report["probes"].append(e)

out = OUT / "npkinspect_002.json"
out.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
for e in report["probes"]:
    print(f'{e["path"]:42s} {e["bytes"]:>12,}  magic_ok={e["magic_ok"]}  sig={e["payload_sig"]}  '
          f'wh={e.get("png_width","?")}x{e.get("png_height","?")}')
print("WROTE", out)
