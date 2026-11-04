# -*- coding: utf-8 -*-
"""取一份 PC csb 原文，与 PE npk 里的 CCB 载荷对比，判断 PE 载荷是否加密。"""
from __future__ import annotations

import sqlite3
import struct
import sys
from pathlib import Path

PROJ = Path(r"E:\la拆包项目")
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
from toolkit_core.path_fid import fid_of  # noqa: E402

RPMAP = PROJ / "01_索引与产物/10_索引/indexes/row_path_map.db"
MRZH = Path(r"E:\mrzh")
OUT = PROJ / "90_临时/_csb_probe"


def aes_ecb(b: bytes) -> bytes:
    from Crypto.Cipher import AES
    return AES.new(bytes.fromhex("606308d8a32c782013d26c2f226f686d"), AES.MODE_ECB).decrypt(b)


def gpk_row(path: Path, row: int) -> bytes | None:
    with open(path, "rb") as f:
        head = aes_ecb(f.read(4096))
        n = struct.unpack_from("<I", head, 20)[0]
        f.seek(64)
        table = aes_ecb(f.read(n * 32))
    off, packed, decoded = struct.unpack_from("<III", table, row * 32)
    with open(path, "rb") as f:
        f.seek(16 + off + 20)
        raw = f.read(packed)
    if raw[:4] == b"\x28\xb5\x2f\xfd":
        import zstandard as zstd
        return zstd.ZstdDecompressor().decompress(raw, max_output_size=decoded)
    if raw[:2] == b"\x04\x22":
        import lz4.block as lb
        try:
            return lb.decompress(raw, uncompressed_size=decoded)
        except Exception:
            return raw
    return raw


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    target = "ui/main_chenghao_xuancai_heitiane.csb"
    con = sqlite3.connect(f"file:{RPMAP.as_posix()}?mode=ro", uri=True)
    r = con.execute("select container,row_index from rows where fid_hex=? limit 1",
                    ("%016X" % fid_of(target),)).fetchone()
    print("row_path_map:", r)
    if not r:
        return 1
    container, row = r
    # container 形如 ui_01.gpk / Documents/res/gres/0000.gpk
    cand = [MRZH / container, MRZH / "Documents/res/gres" / Path(container).name,
            MRZH / "Documents/gres" / Path(container).name]
    path = next((c for c in cand if c.is_file()), None)
    print("包:", path)
    if not path:
        return 1
    data = gpk_row(path, row)
    print("载荷", len(data) if data else None)
    if data:
        (OUT / "pc_heitiane.csb").write_bytes(data)
        print("头 48B:", data[:48].hex())
        print("ascii :", "".join(chr(b) if 32 <= b < 127 else "." for b in data[:48]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
