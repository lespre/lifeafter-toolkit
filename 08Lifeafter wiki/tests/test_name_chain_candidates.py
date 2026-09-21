# -*- coding: utf-8 -*-

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_TOOLS = _ROOT / "tools"
for _p in (str(_ROOT), str(_TOOLS)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

_spec = importlib.util.spec_from_file_location(
    "build_name_chain_candidates", _TOOLS / "build_name_chain_candidates.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
build_candidate_records = _mod.build_candidate_records
build_summary = _mod.build_summary


def _rules() -> dict:
    return {
        "tables": [
            {
                "entry": 18005,
                "table": "items.py",
                "state": "verified",
                "schemas": [
                    {
                        "schema_ref": 7,
                        "state": "verified",
                        "fields": [
                            {
                                "slot": 3,
                                "type": "0x05",
                                "name": "name",
                                "state": "verified",
                            },
                            {
                                "slot": 4,
                                "type": "0x05",
                                "name": "display_name",
                                "state": "verified",
                            },
                            {
                                "slot": 5,
                                "type": "0x05",
                                "name": "title",
                                "state": "verified",
                            },
                            {
                                "slot": 6,
                                "type": "0x0b",
                                "name": "name_id",
                                "state": "verified",
                            },
                            {
                                "slot": 7,
                                "type": "0x05",
                                "name": "desc",
                                "state": "verified",
                            },
                        ],
                    }
                ],
            },
            {
                "entry": 16135,
                "table": "unsafe.py",
                "state": "unsafe",
                "schemas": [
                    {
                        "schema_ref": 9,
                        "state": "unsafe",
                        "fields": [
                            {
                                "slot": 1,
                                "type": "0x05",
                                "name": "name",
                                "state": "unsafe",
                            }
                        ],
                    }
                ],
            },
            {
                "entry": 20000,
                "table": "likely.py",
                "state": "likely",
                "schemas": [
                    {
                        "schema_ref": 11,
                        "state": "likely",
                        "fields": [
                            {
                                "slot": 1,
                                "type": "0x05",
                                "name": "name",
                                "state": "likely",
                            },
                            {
                                "slot": 2,
                                "type": "0x05",
                                "name": "short_name",
                                "state": "verified",
                            },
                        ],
                    }
                ],
            },
        ]
    }


def _sources() -> dict:
    return {
        "sources": [
            {
                "entry": 18005,
                "table": "items.py",
                "state": "verified",
                "category": "物品/装备",
            },
            {
                "entry": 16135,
                "table": "unsafe.py",
                "state": "unsafe",
                "category": "物品/装备",
            },
            {
                "entry": 20000,
                "table": "likely.py",
                "state": "likely",
                "category": "其他业务配置",
            },
        ]
    }


def _spec(entry: int, table: str, fid: str | None = None) -> dict:
    return {
        "source": table,
        "entry": entry,
        "FID": fid or f"FID-{entry}",
        "table": table,
    }


def test_18005_name_is_actual_chinese_verified_and_has_chs_slots() -> None:
    rows = [
        {
            "key": 18005,
            "start": 100,
            "schema": 7,
            "values": {
                "name": ("0x05", "铁手"),
            },
            "value_provenance": {
                "name": {
                    "field_chs_slot": 3,
                    "value_chs_slot": 22,
                    "scalar_type": "0x05",
                    "text": "铁手",
                }
            },
        }
    ]

    records = build_candidate_records(
        rows,
        _spec(18005, "items.py"),
        _rules(),
        _sources(),
    )

    assert len(records) == 1
    record = records[0]

    assert record["entry"] == 18005
    assert record["row_key"] == 18005
    assert record["field"] == "name"
    assert record["type"] == "0x05"
    assert record["text"] == "铁手"
    assert record["raw_text"] == "铁手"
    assert record["field_slot"] == 3
    assert record["value_chs_slot"] == 22
    assert record["entity_name_allowed"] is True
    assert record["isolated"] is False
    assert (
        record["provenance"]["decoder"]
        == "decode_table_rows_with_chs_slots"
    )


def test_16135_name_is_retained_but_unsafe_and_isolated() -> None:
    rows = [
        {
            "key": 16135,
            "start": 200,
            "schema": 9,
            "values": {
                "name": ("0x05", "危险名"),
            },
            "value_provenance": {
                "name": {
                    "field_chs_slot": 1,
                    "value_chs_slot": 2,
                    "scalar_type": "0x05",
                    "text": "危险名",
                }
            },
        }
    ]

    records = build_candidate_records(
        rows,
        _spec(16135, "unsafe.py"),
        _rules(),
        _sources(),
    )

    assert len(records) == 1
    record = records[0]

    assert record["entry"] == 16135
    assert record["text"] == "危险名"
    assert record["entity_name_allowed"] is False
    assert record["isolated"] is True
    assert record["provenance"]["safety_state"] == "unsafe"


def test_only_actual_present_fields_are_emitted_without_cartesian_product() -> None:
    rows = [
        {
            "key": 18005,
            "start": 300,
            "schema": 7,
            "values": {
                "name": ("0x05", "铁手"),
                "title": ("0x05", "称号"),
            },
            "value_provenance": {
                "name": {
                    "field_chs_slot": 3,
                    "value_chs_slot": 22,
                    "scalar_type": "0x05",
                    "text": "铁手",
                },
                "title": {
                    "field_chs_slot": 5,
                    "value_chs_slot": 23,
                    "scalar_type": "0x05",
                    "text": "称号",
                },
            },
        }
    ]

    records = build_candidate_records(
        rows,
        _spec(18005, "items.py"),
        _rules(),
        _sources(),
    )

    assert len(records) == 2
    assert {record["field"] for record in records} == {
        "name",
        "title",
    }
    assert all(record["row_key"] == 18005 for record in records)
    assert sum(
        record["entity_name_allowed"] for record in records
    ) == 1


def test_auxiliary_likely_numeric_and_forbidden_fields_are_not_entity_names() -> None:
    rows = [
        {
            "key": 18005,
            "start": 400,
            "schema": 7,
            "values": {
                "title": ("0x05", "称号"),
                "name_id": ("0x0b", 123),
                "desc": ("0x05", "仅供审计"),
            },
            "value_provenance": {
                "title": {
                    "field_chs_slot": 5,
                    "value_chs_slot": 30,
                },
                "name_id": {
                    "field_chs_slot": 6,
                    "value_chs_slot": None,
                },
                "desc": {
                    "field_chs_slot": 7,
                    "value_chs_slot": 31,
                },
            },
        }
    ]

    records = build_candidate_records(
        rows,
        _spec(18005, "items.py"),
        _rules(),
        _sources(),
    )

    assert len(records) == 3

    by_field = {record["field"]: record for record in records}

    assert by_field["title"]["role"] == "auxiliary"
    assert by_field["title"]["entity_name_allowed"] is False

    assert by_field["name_id"]["role"] == "numeric"
    assert by_field["name_id"]["decision"] == "unresolved"
    assert by_field["name_id"]["entity_name_allowed"] is False

    assert by_field["desc"]["role"] == "forbidden"
    assert by_field["desc"]["decision"] == "audit-only"
    assert by_field["desc"]["entity_name_allowed"] is False


def test_likely_source_is_never_allowed_and_server_branch_is_unresolved() -> None:
    rows = [
        {
            "key": 20000,
            "start": 500,
            "schema": 11,
            "values": {
                "name": ("0x05", "可能名称"),
                "short_name": ("0x05", "简称"),
            },
            "value_provenance": {
                "name": {
                    "field_chs_slot": 1,
                    "value_chs_slot": 40,
                },
                "short_name": {
                    "field_chs_slot": 2,
                    "value_chs_slot": 41,
                },
            },
        }
    ]

    records = build_candidate_records(
        rows,
        _spec(20000, "likely.py"),
        _rules(),
        _sources(),
    )
    summary = build_summary(records)

    assert len(records) == 2
    assert all(
        record["entity_name_allowed"] is False
        for record in records
    )
    assert summary["server_branch"] == "unresolved"
    assert summary["scope"]["cross_table_join"] is False
    assert summary["scope"]["category"] == "metadata-only"


def test_kj1_is_excluded() -> None:
    rows = [
        {
            "key": 10,
            "start": 600,
            "schema": 7,
            "values": {
                "name": ("0x05", "KJ1名称"),
            },
            "value_provenance": {
                "name": {
                    "field_chs_slot": 3,
                    "value_chs_slot": 50,
                }
            },
        }
    ]

    records = build_candidate_records(
        rows,
        _spec(
            10,
            r"com\cdata\oversea\items_auto_oversea_data_kj1.py",
        ),
        _rules(),
        _sources(),
    )

    assert records == []
