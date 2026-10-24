# -*- coding: utf-8 -*-
"""0x56 索引尾分派（2026-10-23）。

锁定三件事：
  1. ``parse_index`` 遇到 0x56 尾 → 走记录表（hash → triple 偏移），不再抛
     ``not a supported 0x76 index tail``；
  2. ``decode_table_rows`` 遇到 0x56 表体 → 单行、字段名全部来自 _chs 池；
  3. 非 0x56（0x76 / 0x66 …）行为不变 —— 0x66 仍抛原来那句错。
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from toolkit_core.bindict_table import (  # noqa: E402
    INDEX_TAIL_56,
    decode_table_rows,
    index_tail_family,
    is_56_tail,
    parse_index,
)

CDATA = Path(r"E:/la拆包项目/01_索引与产物/41_还原树/pe/配置_增量快照/com/cdata")


def _uleb(value: int) -> bytes:
    out = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        if value:
            out.append(byte | 0x80)
        else:
            out.append(byte)
            return bytes(out)


def _build_56_body(pool: list[str], fields: list[tuple[int, bytes]], tail_marker: int = INDEX_TAIL_56) -> bytes:
    """构造 0x56 表体：fields = [(field_idx, 三元组尾部字节)]。"""
    # 三元组区先拼好，才能算出记录里要填的 blob 偏移
    triples = b"".join(_uleb(idx) + rest for idx, rest in fields)
    de = 4
    nrec = len(fields)
    head_len = 3 + 8 * nrec
    offsets = []
    cursor = de + head_len
    for idx, rest in fields:
        offsets.append(cursor)
        cursor += len(_uleb(idx) + rest)
    tail = bytes([tail_marker, 0x05, nrec])
    for i, off in enumerate(offsets):
        tail += struct.pack("<II", 0x1000 + i, off)
    tail += triples
    blob = struct.pack("<I", de) + tail

    ends, acc = [], 0
    for s in pool:
        acc += len(s.encode("utf-8"))
        ends.append(acc)
    header = struct.pack("<II", len(pool), 0) + struct.pack("<%dI" % len(pool), *ends)
    return header + blob


POOL = ["a", "b", "c"]
FIELDS = [
    (0, b"\x01" + _uleb(7)),                      # uleb 7
    (1, b"\x12" + struct.pack("<f", 1.5)),        # f32
    (2, b"\x05" + _uleb(2)),                      # CHS 引用 → pool[2]
]
BODY_56 = _build_56_body(POOL, FIELDS)
BLOB_56 = BODY_56[8 + 4 * len(POOL):]


def test_tail_family_and_strict_check() -> None:
    assert index_tail_family(BLOB_56) == INDEX_TAIL_56
    assert is_56_tail(BLOB_56) is True


def test_parse_index_routes_0x56_to_record_table() -> None:
    assert parse_index(BLOB_56) == [(0x1000, 31), (0x1001, 34), (0x1002, 40)]


def test_decode_table_rows_0x56_single_row() -> None:
    rows, unbound = decode_table_rows(BODY_56, POOL)
    assert unbound == []
    assert len(rows) == 1
    row = rows[0]
    assert row["family"] == "0x56"
    assert row["marker"] == "0x56"
    assert row["nrec"] == 3
    assert row["values"] == {"a": 7, "b": 1.5, "c": "c"}


def test_other_tail_bytes_keep_old_behaviour() -> None:
    """0x66 尾不进分派 —— 仍是原来那句 ValueError。"""
    body66 = _build_56_body(POOL, FIELDS, tail_marker=0x66)
    blob66 = body66[8 + 4 * len(POOL):]
    assert index_tail_family(blob66) == 0x66
    assert is_56_tail(blob66) is False
    try:
        decode_table_rows(body66, POOL)
    except ValueError as exc:
        assert "not a supported 0x76 index tail" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("0x66 尾必须保持原来的报错")


def test_96_row_table_not_hijacked() -> None:
    """0x76 桶索引的普通表不能被 0x56 分派吃掉（de 处是 0x76）。"""
    body76 = _build_56_body(POOL, FIELDS, tail_marker=0x76)
    blob76 = body76[8 + 4 * len(POOL):]
    assert is_56_tail(blob76) is False
    assert index_tail_family(blob76) == 0x76


def test_real_vehicle_basic_conf() -> None:
    """实盘锚点：0x56 表 vehicle_basic_conf 单行、81 个字段有值且全命名。"""
    base = CDATA / "vehicle_basic_conf.py"
    chs = CDATA / "vehicle_basic_conf_chs.py"
    if not base.is_file() or not chs.is_file():
        return  # 还原树不在本机时跳过外部锚点
    raw = base.read_bytes()
    at = raw.find(b"x{")
    ln = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6:at + 6 + ln]
    from toolkit_core.bindict_table import parse_legacy_chs_pool

    pool = parse_legacy_chs_pool(chs.read_bytes())
    rows, unbound = decode_table_rows(body, pool)
    assert unbound == []
    assert len(rows) == 1
    row = rows[0]
    assert row["field_count"] == 83
    assert row["nrec"] == 81
    assert len(row["values"]) == 81
    assert not [n for n in row["values"] if n.startswith("<field_")]
