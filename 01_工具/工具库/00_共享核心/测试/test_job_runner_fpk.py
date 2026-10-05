from __future__ import annotations

import json
import sys
from pathlib import Path
from threading import Event

import zstandard as zstd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import toolkit_core.job_runner as job_runner
from toolkit_core.job_runner import PackageJob, run_package_jobs


def test_fpk_gui_job_uses_verified_frames_instead_of_legacy_backend(tmp_path: Path, monkeypatch) -> None:
    compressor = zstd.ZstdCompressor()
    source = tmp_path / "res" / "001.fpk"
    source.parent.mkdir()
    source.write_bytes(
        b"H" * 32
        + compressor.compress(b"first")
        + b"\x00\x00"
        + compressor.compress(b"second")
    )

    class LegacyBackend:
        @staticmethod
        def extract_fpk_full(*_args) -> None:
            raise AssertionError("GUI must not use legacy extract_fpk_full")

    monkeypatch.setattr(job_runner, "_load_backend", lambda: LegacyBackend())
    progress: list[tuple[int, int, str]] = []
    run_package_jobs(
        [PackageJob(source, tmp_path / "output")],
        pause_event=Event(),
        cancel_event=Event(),
        on_progress=lambda *args: progress.append(args),
        on_log=lambda _message: None,
    )

    manifest = tmp_path / "output" / "exports" / "fpk" / "001" / "frames_full.json"
    report = json.loads(manifest.read_text(encoding="utf-8"))
    assert report["total_frames"] == 2
    assert report["frame_boundary_method"] == "sequential_decompressobj_eof_plus_zero_padding"
    assert progress == [(1, 1, "001.fpk")]


def test_fpk_gui_manifest_marks_raw_json_between_zstd_frames(tmp_path: Path) -> None:
    compressor = zstd.ZstdCompressor()
    raw_json = b'{"render_path":"deferred"}'
    source = tmp_path / "res" / "001.fpk"
    source.parent.mkdir()
    source.write_bytes(
        b"H" * 32
        + compressor.compress(b"first")
        + raw_json
        + b"\x00\x00"
        + compressor.compress(b"second")
    )

    run_package_jobs(
        [PackageJob(source, tmp_path / "output")],
        pause_event=Event(),
        cancel_event=Event(),
        on_progress=lambda *_args: None,
        on_log=lambda _message: None,
    )

    manifest = tmp_path / "output" / "exports" / "fpk" / "001" / "frames_full.json"
    report = json.loads(manifest.read_text(encoding="utf-8"))
    assert report["rows"][1]["storage"] == "raw"
    assert report["rows"][1]["padding_size"] == 2
