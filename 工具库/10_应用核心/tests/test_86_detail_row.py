"""0x86 detail-row decoding: optional_hd_exchange_shop item details.

Verified on optional_hd_exchange_shop_data (entry 2949): the 0x36 mapping
rows' vt=0x0b values jump to 0x86 rows. 0x86 rows are D6-style:
[86][uleb schema_ref][uleb bitmap_ref][bitmap bytes][value stream].
Schema @70: n=33, bits=23. Fields include uleb/bool/jump/f32/f64;
0x0b fields jump to 0x27 groups carrying item ids (e.g. [156182] or
[153036, count] price groups).
"""

from pathlib import Path
import struct

from toolkit_core.bindict_table import decode_table_rows, resolve_jump_group
from toolkit_core.bindict_rows import uleb
from toolkit_core.bindict_table import decode_86_row, decode_optional_hd_exchange_records


def _uleb_bytes(val):
    out = bytearray()
    while True:
        b = val & 0x7F
        val >>= 7
        out.append(b | (0x80 if val else 0))
        if not val:
            return bytes(out)


def _build_86_blob():
    """Blob: [de][86 detail][76 01 0b index with one 36 row? no — pure detail].

    decode_86_row works on a bare blob; test it directly without a table.
    """
    # schema @0: n=2, bits=0, (slot0, 0x01), (slot1, 0x22)
    schema = bytes([0x02, 0x00, 0x00, 0x01, 0x00, 0x22])
    # 86 row @6: schema_ref=0, bitmap_ref=0 (bits=0 -> 0 bytes), values: uleb 5, f64 3.5
    row = bytearray([0x86])
    row += _uleb_bytes(0)
    row += _uleb_bytes(0)
    row += _uleb_bytes(5)
    row += struct.pack("<d", 3.5)
    blob = schema + bytes(row)
    return blob, 6


def test_86_row_synthetic():
    blob, pos = _build_86_blob()
    d = decode_86_row(blob, pos)
    assert d["marker"] == "0x86"
    assert d["schema"] == 0
    assert d["values"] == {0: 5, 1: 3.5}


def test_86_row_rejects_wrong_marker():
    blob, pos = _build_86_blob()
    try:
        decode_86_row(blob, pos + 1)
        raise AssertionError("should reject non-0x86")
    except ValueError:
        pass


def test_real_optional_hd_exchange():
    """Integration: entry 2949 must decode 1368 0x86 details; find 156182 refs."""
    root = Path(r"E:\la拆包项目\03拆包产物\config_work\script_py314_docs_56def41376ed\entries")
    b = (root / "002949.bin").read_bytes()
    x = b.find(b"x{")
    ln = struct.unpack_from("<I", b, x + 2)[0]
    body = b[x + 6:x + 6 + ln]
    rows, unbound = decode_table_rows(body, [])
    assert not unbound, unbound
    assert len(rows) == 2
    cnt = struct.unpack_from("<I", body, 0)[0]
    blob = body[8 + 4 * cnt:]
    n86 = 0
    hit_refs = 0
    for r in rows:
        for _k, v in r.get("pairs", []):
            if not isinstance(v, str) or not v.startswith("jump:"):
                continue
            tgt = int(v.split(":")[1])
            if tgt >= len(blob) or blob[tgt] != 0x86:
                continue
            d = decode_86_row(blob, tgt)
            n86 += 1
            for _i, val in d["values"].items():
                g = resolve_jump_group(blob, val) if isinstance(val, int) else None
                if g and 156182 in g:
                    hit_refs += 1
                    break
    assert n86 == 1863  # 1063 + 800 pairs, every jump targets a 0x86 row
    assert hit_refs >= 100


def test_optional_exchange_keeps_duplicate_keys_and_resolves_anchor_groups():
    """Regression: mapping keys repeat across the two 0x36 maps.

    The old CSV built a dict keyed only by ``key`` and silently overwrote the
    real map-0 key=27 row (霓虹恶魔 / 稀世之证×450) with map-1 key=27.
    The export seam must retain mapping identity and recover 0x27 groups both
    from 0x0b references and scalar group offsets.
    """
    root = Path(r"E:\la拆包项目\03拆包产物\config_work\script_py314_docs_56def41376ed\entries")
    b = (root / "002949.bin").read_bytes()
    x = b.find(b"x{")
    ln = struct.unpack_from("<I", b, x + 2)[0]
    body = b[x + 6:x + 6 + ln]

    records = decode_optional_hd_exchange_records(body)
    assert len(records) == 1863
    assert sum(r["key"] == 27 for r in records) == 2

    def values(record):
        return {tuple(g["values"]) for g in record["resolved_groups"]}

    # 用户实机锚点：帝皇战翼交易盒=宸晶臻石×3，限购3。
    warwing = next(r for r in records if (r["mapping_row"], r["pair_index"]) == (0, 0))
    assert (153036, 3) in values(warwing)
    assert (139267, 1) in values(warwing)
    assert (3, 1) in values(warwing)

    # 用户截图锚点：幻紫晶芒时装=宸晶臻石×3，商品礼盒135848。
    purple = next(r for r in records if (r["mapping_row"], r["pair_index"]) == (0, 367))
    assert (153036, 3) in values(purple)
    assert (135848, 1) in values(purple)

    # 用户截图锚点：幻影狩蝎=宸晶臻石×1，商品1110013。
    scorpion = next(r for r in records if (r["mapping_row"], r["pair_index"]) == (0, 365))
    assert (153036, 1) in values(scorpion)
    assert (1110013, 1) in values(scorpion)
