# -*- coding: utf-8 -*-
"""0x73 包装 bindict 表的回归测试（真值锚点，不是自证）。

真值来源：项目实测锚点（key 1110188/1110191/1110192 的字段值），
这些值**不经过本模块**产生，属于外部真值。
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]        # 00_共享核心
sys.path.insert(0, str(ROOT))

from toolkit_core import bindict_table as BT                        # noqa: E402
from toolkit_core.bindict_73 import (                               # noqa: E402
    Bindict73Error,
    decode_73_table,
    extract_body,
    load_pool_for,
    parse_index_73,
)

BASE = Path(r"E:/la拆包项目/01_索引与产物/41_还原树")
OLD = BASE / "script.py314.lc.npk/com/cdata/weapon_skin_data.py"
NEW = BASE / "Documents/script.py314.lc.npk/com/cdata/weapon_skin_data.py"

pytestmark = pytest.mark.skipif(
    not (OLD.is_file() and NEW.is_file()),
    reason="还原树不在本机（0x73 样例文件缺失）",
)


# ───────────────────────────────────────────── 容器 + 表体结构
def test_old_container_layout():
    rows, unbound, meta = decode_73_table(OLD)
    c, b, i = meta["container"], meta["body"], meta["index"]

    assert c["kind"] == "code_object"
    assert c["payload_off"] == 269            # `7b e6 00 00 00` 之后
    assert c["payload_len"] == 11584
    assert b["count"] == 233                  # 表体头 count
    assert b["reserved"] == 0
    assert b["ends_all_zero"] is True         # 基表 ends 全 0
    assert b["de"] == 8918                    # 索引尾相对 data 的偏移
    assert b["blob_off"] == 8 + 4 * 233       # = 940
    assert b["index_tag"] == "76 01 0b"

    assert i["bucket_count"] == 131
    assert i["bucket_count_encoding"] == "uleb"     # 0x83 0x01，不是 u8
    assert i["bucket_offset_base"] == "blob"
    assert i["node_records"] == 131
    assert i["bucket_offsets_are_node_starts"] is True
    assert i["hashes_sorted_ascending"] is True

    assert len(rows) == 131
    assert unbound == []
    assert meta["rows"]["decoded"] == 131
    assert meta["rows"]["unbound"] == 0


def test_pool_count_invariant():
    """表体 count == 配对 _chs 池条目数（旧 233、新 248）。"""
    for path, expect in ((OLD, 233), (NEW, 248)):
        pool = load_pool_for(path)
        _rows, _unb, meta = decode_73_table(path, pool=pool)
        assert len(pool) == expect
        assert meta["body"]["count"] == expect
        assert meta["pool_matches_count"] is True


def test_index_agrees_with_bindict_table():
    """本模块的 0x76 索引解与既有 bindict_table.parse_index 完全一致。"""
    for path in (OLD, NEW):
        _rows, _unb, meta = decode_73_table(path)
        assert meta["index_agrees_with_bindict_table"] is True

        body, _c = extract_body(path)
        blob = body[8 + 4 * int.from_bytes(body[:4], "little"):]
        mine, _imeta = parse_index_73(blob)
        assert sorted(mine) == sorted(BT.parse_index(blob))


def test_payload_offset_matches_marshal_const_table():
    """payload 偏移必须等于 marshal 常量表里那个 bytes 常量的载荷起点。"""
    sd = pytest.importorskip("toolkit_core.script_decode")
    reader, root, total = sd.load_module(str(OLD))
    assert total == OLD.stat().st_size          # 全文件解析终点吻合

    hits = []

    def walk(code):
        for const in code.consts or []:
            value = getattr(const, "v", None)
            if isinstance(value, (bytes, bytearray)) and len(value) > 100:
                hits.append((getattr(const, "off", None), len(value)))
            elif isinstance(value, sd.CodeObj):
                walk(value)

    walk(root)
    _body, meta = extract_body(OLD)
    # const.off 指向 tag(0x7b)+u32 长度，载荷在其后 5 字节
    assert (meta["payload_off"] - 5, meta["payload_len"]) in hits


# ───────────────────────────────────────────── 真值锚点
def _row(rows, key):
    for r in rows:
        if r["key"] == key:
            return r
    raise AssertionError("缺 key %d" % key)


def _val(row, name):
    return row["values"][name][1]


def test_anchor_1110188():
    """真值：weapon_type=1 level=5 charm=1000 sale_ts=1792598400
    camera_conf_id=1581 model_path 含 skin_1001_017 scale≈1.27"""
    rows, _unb, _meta = decode_73_table(NEW)
    r = _row(rows, 1110188)
    assert _val(r, "weapon_type") == 1
    assert _val(r, "level") == 5
    assert _val(r, "charm_value") == 1000
    assert _val(r, "sale_ts") == 1792598400
    assert _val(r, "camera_conf_id") == 1581
    assert "skin_1001_017" in _val(r, "model_path")
    assert _val(r, "model_extra_scale") == pytest.approx(1.27, abs=1e-6)


@pytest.mark.parametrize("key,weapon_type", [(1110191, 6), (1110192, 8)])
def test_anchor_weapon_type(key, weapon_type):
    """真值：1110191 是手枪(6)，1110192 是电磁机枪(8)。"""
    rows, _unb, _meta = decode_73_table(NEW)
    assert _val(_row(rows, key), "weapon_type") == weapon_type


def test_row_count_not_header_value():
    """行数来自索引，不是表头那个错位读出来的 1280。"""
    for path, expect in ((OLD, 131), (NEW, 141)):
        rows, _unb, _meta = decode_73_table(path)
        assert len(rows) == expect
        assert len(rows) != 1280


# ───────────────────────────────────────────── 回退路径 / 负例
def test_raw_body_passthrough():
    """直接喂表体（无 0x73 容器）应得到同一批行。"""
    body, cmeta = extract_body(NEW)
    assert cmeta["kind"] == "code_object"
    pool = load_pool_for(NEW)

    rows_a, _u1, meta_a = decode_73_table(NEW, pool=pool)
    rows_b, _u2, meta_b = decode_73_table(body, pool=pool)

    assert meta_b["container"]["kind"] == "raw_body"
    assert [r["key"] for r in rows_a] == [r["key"] for r in rows_b]
    assert meta_a["body"]["count"] == meta_b["body"]["count"]


def test_rejects_non_bindict_payload():
    """不是表体的字节要显式失败，不能返回空行糊过去。"""
    with pytest.raises(Bindict73Error):
        decode_73_table(b"\x00" * 512, pool=[])
