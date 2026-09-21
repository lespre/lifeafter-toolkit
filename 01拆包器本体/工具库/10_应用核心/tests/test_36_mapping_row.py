"""0x36 mapping row support: exchange shop style tables.

Verified on common_exchange_shop_data (entry 7767): rows are
[36][kt][vt][pair_count uleb][n x (key,value)] with no schema/bitmap.
vt=0x0b values are blob-offset jumps; kt=0x01 keys are ULEB.
"""

from pathlib import Path
import struct

from toolkit_core.bindict_table import decode_table_rows, parse_index
from toolkit_core.bindict_rows import uleb


def _build_blob(rows):
    """Build a minimal base_body: [count][reserved][blob].

    blob = [de u32][36 rows][76 01 0b index head][bucket of (key,row_start) pairs].
    """
    def uleb_bytes(val):
        out = bytearray()
        while True:
            b = val & 0x7F
            val >>= 7
            out.append(b | (0x80 if val else 0))
            if not val:
                return out

    payload = bytearray()
    starts = []
    for key, kt, vt, pairs in rows:
        starts.append(4 + len(payload))
        payload.append(0x36)
        payload.append(kt)
        payload.append(vt)
        payload += uleb_bytes(len(pairs))
        for k, v in pairs:
            payload += uleb_bytes(k)
            payload += uleb_bytes(v)
    de = 4 + len(payload)
    # bucket lives inside the index tail, after the node table
    bucket = bytearray()
    for (key, _kt, _vt, _pairs), st in zip(rows, starts):
        bucket += uleb_bytes(key)
        bucket += uleb_bytes(st)
    bucket_off = de + 3 + 1 + 8  # 76 01 0b + u8 count + one 8B node
    index = bytearray(b"\x76\x01\x0b")
    index.append(1)  # single bucket containing all rows
    index += struct.pack("<II", 1, bucket_off)
    index += bucket
    blob = bytearray(struct.pack("<I", de))
    blob += payload
    blob += index
    # wrap as base_body: [count u32][reserved u32][blob]
    return struct.pack("<II", 0, 0) + bytes(blob)


def test_36_row_two_pairs():
    blob = _build_blob([(7, 0x01, 0x0B, [(5, 16), (9, 32)])])
    rows, unbound = decode_table_rows(blob, [])
    assert not unbound, unbound
    assert len(rows) == 1
    row = rows[0]
    assert row["key"] == 7
    assert row["marker"] == "0x36"
    assert row["pairs"] == [(5, "jump:16"), (9, "jump:32")]


def test_36_row_multi_rows_and_types():
    blob = _build_blob([
        (1, 0x01, 0x0B, [(3, 100), (2, 200)]),
        (2, 0x01, 0x0B, [(9, 300)]),
    ])
    rows, unbound = decode_table_rows(blob, [])
    assert not unbound, unbound
    assert [r["key"] for r in rows] == [1, 2]
    assert rows[0]["pairs"] == [(3, "jump:100"), (2, "jump:200")]
    assert rows[1]["pairs"] == [(9, "jump:300")]


def test_real_common_exchange_shop():
    """Integration: entry 7767 must yield 70 rows, key=1 has 26 pairs."""
    root = Path(r"E:\la拆包项目\03拆包产物\config_work\script_py314_docs_56def41376ed\entries")
    b = (root / "007767.bin").read_bytes()
    x = b.find(b"x{")
    ln = struct.unpack_from("<I", b, x + 2)[0]
    body = b[x + 6:x + 6 + ln]
    rows, unbound = decode_table_rows(body, [])
    assert not unbound, f"unbound: {unbound[:3]}"
    assert len(rows) == 70
    r1 = next(r for r in rows if r["key"] == 1)
    assert len(r1["pairs"]) == 26
    assert r1["pairs"][0][0] == 130
    assert r1["pairs"][0][1].startswith("jump:")
