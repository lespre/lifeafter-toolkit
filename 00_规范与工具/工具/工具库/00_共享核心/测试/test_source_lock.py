from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from toolkit_core.source_lock import (
    build_snapshot,
    compare_snapshots,
    create_snapshot_run,
    read_snapshot,
    write_snapshot,
)


def test_content_snapshot_ignores_mtime_only_change(tmp_path: Path) -> None:
    source = tmp_path / "mrzh" / "Documents" / "script.py314.lc.npk"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"same package bytes")

    baseline = build_snapshot(tmp_path / "mrzh")
    before = source.stat().st_mtime
    os.utime(source, (before + 3600, before + 3600))
    current = build_snapshot(tmp_path / "mrzh")

    delta = compare_snapshots(baseline, current)

    assert delta["content_added"] == []
    assert delta["content_changed"] == []
    assert delta["content_unchanged"] == ["Documents/script.py314.lc.npk"]
    assert delta["mtime_only_changed"] == ["Documents/script.py314.lc.npk"]


def test_written_snapshot_round_trips_without_losing_source_lock_fields(tmp_path: Path) -> None:
    source = tmp_path / "mrzh" / "res" / "ui.npk"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"ui bytes")
    snapshot = build_snapshot(tmp_path / "mrzh")
    destination = tmp_path / "output" / "source_lock.json"

    write_snapshot(snapshot, destination)

    assert read_snapshot(destination) == snapshot


def test_snapshot_can_scope_to_original_container_suffixes(tmp_path: Path) -> None:
    root = tmp_path / "mrzh"
    package = root / "res" / "001.fpk"
    sidecar = root / "Documents" / "file_hash_pack.bin"
    derivative = root / "logs" / "worker.log"
    package.parent.mkdir(parents=True)
    sidecar.parent.mkdir(parents=True)
    derivative.parent.mkdir(parents=True)
    package.write_bytes(b"fpk")
    sidecar.write_bytes(b"hash pack")
    derivative.write_text("not a source container", encoding="utf-8")

    snapshot = build_snapshot(root, include_suffixes={".fpk", ".bin"})

    assert [row["relative_path"] for row in snapshot["files"]] == [
        "Documents/file_hash_pack.bin",
        "res/001.fpk",
    ]


def test_snapshot_run_writes_content_delta_against_explicit_baseline(tmp_path: Path) -> None:
    root = tmp_path / "mrzh"
    package = root / "Documents" / "script.py314.lc.npk"
    package.parent.mkdir(parents=True)
    package.write_bytes(b"before")
    baseline_path = tmp_path / "baseline.json"
    write_snapshot(build_snapshot(root, include_suffixes={".npk"}), baseline_path)
    package.write_bytes(b"after")

    state = create_snapshot_run(
        root,
        tmp_path / "output" / "snapshot",
        baseline_path=baseline_path,
        include_suffixes={".npk"},
    )

    assert state["baseline_available"] is True
    assert state["delta"]["content_changed"] == ["Documents/script.py314.lc.npk"]
    assert (tmp_path / "output" / "snapshot" / "source_lock.json").is_file()
    assert (tmp_path / "output" / "snapshot" / "package_delta.json").is_file()
    assert (tmp_path / "output" / "snapshot" / "CURRENT_STATE.json").is_file()
