"""0x36 mapping row support: exchange shop style tables.

Verified on common_exchange_shop_data (entry 7767): rows are
[36][kt][vt][pair_count uleb][n x (key,value)] with no schema/bitmap.
vt=0x0b values are blob-offset jumps; kt=0x01 keys are ULEB.
"""

from pathlib import Path
import struct

from toolkit_core.bindict_table import decode_table_rows, parse_index
from toolkit_core.bindict_rows import uleb


FIXTURE_ENTRIES = Path(__file__).resolve().parent / "fixtures" / "script_py314_7767_2949" / "entries"


def _workcopy_entries() -> Path:
    """返回测试夹具目录（专属、可复现、带逐字节核验凭据）。

    ★ 为什么不继续去 config_work 里「挑 bin 最多的快照」：
      config_work 下并存多份快照，但它们来自【不同版本】的 script.py314.lc.npk。
      同一个编号在不同版本里指向不同内容（007767.bin 在不同快照里分别是
      316 / 1,599 / 1,062 / 483 字节），所以「挑最大的」是错的判据 —— 会挑到
      一个能解析但内容不对的版本，让测试永久红，而代码其实没坏。

    ★ 现方案：夹具是本目录下固定的重建副本，逐字节核验过：
      源包  02_资料/源包/热更历史容器_20260829-20260916/
            pre_update_20260831_182129/raw_priority/Documents/script.py314.lc.npk
            size 269,020,184   sha256 56def41376ed…（与历史清单完全一致）
      007767.bin  88,658 B  ✓ 尺寸与 sha256 均与清单一致
      002949.bin  81,534 B  ✓ 尺寸与 sha256 均与清单一致
      来源与核验记录：同目录 PROVENANCE.json
      重建方式：python tests/rebuild_fixtures.py
    """
    import pytest
    if not FIXTURE_ENTRIES.is_dir() or not any(FIXTURE_ENTRIES.glob("*.bin")):
        pytest.skip("测试夹具缺失；先跑 python tests/rebuild_fixtures.py 重建（缺数据不是代码缺陷）")
    return FIXTURE_ENTRIES


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
    root = _workcopy_entries()
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
