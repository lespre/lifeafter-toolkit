from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import zstandard as zstd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from toolkit_core.fpk_frames import FPK_HEADER_SIZE, iter_fpk_frames
from toolkit_core.fpk_raw import export_raw_entries
from toolkit_core.paths import DEFAULT_OUTPUT_ROOT


def load_fpk_toolkit():
    path = ROOT.parent / "02_FPK工具" / "fpk_toolkit.py"
    spec = importlib.util.spec_from_file_location("fpk_toolkit_under_test", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_fpk_toolkit_default_output_is_under_unified_artifact_root() -> None:
    assert load_fpk_toolkit().OUT == DEFAULT_OUTPUT_ROOT / "fpk"


def test_iter_fpk_frames_respects_real_frame_boundaries_and_zero_padding(tmp_path: Path) -> None:
    first_payload = b"first frame payload"
    second_payload = b"second frame payload"
    compressor = zstd.ZstdCompressor()
    first_frame = compressor.compress(first_payload)
    second_frame = compressor.compress(second_payload)
    source = tmp_path / "001.fpk"
    source.write_bytes(b"H" * FPK_HEADER_SIZE + first_frame + b"\x00\x00" + second_frame)

    frames = list(iter_fpk_frames(source, chunk_size=7))

    assert [frame.index for frame, _payload in frames] == [0, 1]
    assert [frame.offset for frame, _payload in frames] == [
        FPK_HEADER_SIZE,
        FPK_HEADER_SIZE + len(first_frame) + 2,
    ]
    assert [frame.packed_size for frame, _payload in frames] == [len(first_frame), len(second_frame)]
    assert [payload for _frame, payload in frames] == [first_payload, second_payload]


def test_fpk_toolkit_summary_uses_verified_sequential_frames(tmp_path: Path) -> None:
    compressor = zstd.ZstdCompressor()
    first_frame = compressor.compress(b"DDS " + b"\x00" * 124)
    second_frame = compressor.compress(b'{"skeleton":"test"}')
    source = tmp_path / "001.fpk"
    source.write_bytes(b"H" * FPK_HEADER_SIZE + first_frame + b"\x00" + second_frame)

    summary = load_fpk_toolkit().summarize_fpk_frames(source, chunk_size=9)

    assert summary["total_frames"] == 2
    assert summary["types"] == {"dds_0x0": 1, "json": 1}
    assert [row["off"] for row in summary["rows"]] == [
        FPK_HEADER_SIZE,
        FPK_HEADER_SIZE + len(first_frame) + 1,
    ]


def test_iter_fpk_frames_preserves_raw_json_between_verified_zstd_frames(tmp_path: Path) -> None:
    compressor = zstd.ZstdCompressor()
    first_payload = b"first"
    raw_json = b'{"render_path":"deferred"}'
    second_payload = b"second"
    first_frame = compressor.compress(first_payload)
    second_frame = compressor.compress(second_payload)
    source = tmp_path / "001.fpk"
    source.write_bytes(
        b"H" * FPK_HEADER_SIZE + first_frame + raw_json + b"\x00\x00" + second_frame
    )

    frames = list(iter_fpk_frames(source, chunk_size=9))

    assert [frame.storage for frame, _payload in frames] == ["zstd", "raw", "zstd"]
    assert [frame.offset for frame, _payload in frames] == [
        FPK_HEADER_SIZE,
        FPK_HEADER_SIZE + len(first_frame),
        FPK_HEADER_SIZE + len(first_frame) + len(raw_json) + 2,
    ]
    assert frames[1][0].padding_size == 2
    assert [payload for _frame, payload in frames] == [first_payload, raw_json, second_payload]


def test_fpk_summary_marks_stored_json_and_its_separator_padding(tmp_path: Path) -> None:
    compressor = zstd.ZstdCompressor()
    raw_json = b'{"render_path":"deferred"}'
    source = tmp_path / "001.fpk"
    source.write_bytes(
        b"H" * FPK_HEADER_SIZE
        + compressor.compress(b"first")
        + raw_json
        + b"\x00\x00"
        + compressor.compress(b"second")
    )

    summary = load_fpk_toolkit().summarize_fpk_frames(source, chunk_size=9)

    assert summary["rows"][1]["storage"] == "raw"
    assert summary["rows"][1]["padding_size"] == 2


def test_raw_export_writes_payloads_and_a_verifiable_index(tmp_path: Path) -> None:
    compressor = zstd.ZstdCompressor()
    raw_json = b'{"render_path":"deferred"}'
    raw_binary = b"\x01\x02raw-binary\x03"
    source = tmp_path / "001.fpk"
    source.write_bytes(
        b"H" * FPK_HEADER_SIZE
        + compressor.compress(b"first")
        + raw_json
        + b"\x00"
        + compressor.compress(b"second")
        + raw_binary
    )

    report = export_raw_entries(source, tmp_path / "raw_entries", chunk_size=9)

    assert report["raw_count"] == 2
    assert [row["content_kind"] for row in report["rows"]] == ["json", "other"]
    assert json.loads((tmp_path / "raw_entries" / "raw_00001.json").read_text(encoding="utf-8"))["render_path"] == "deferred"
    binary_row = report["rows"][1]
    assert (tmp_path / "raw_entries" / binary_row["payload_file"]).read_bytes() == raw_binary
    assert len(binary_row["sha256"]) == 64
