# -*- coding: utf-8 -*-
"""FPK 工具包：64包概览扫描 + 单包真实 Zstd 帧扫描。

FPK 格式：32B 文件头 + 独立 Zstd 帧流；帧之间允许 1--3 字节 0x00 填充。
所有 Zstd 包必须按前一帧真实 eof 边界顺序读取，禁止全文件 magic 搜索。

用法：
  python fpk_toolkit.py overview
  python fpk_toolkit.py full <fpk文件>
  python fpk_toolkit.py probe <fpk文件>
"""
from __future__ import annotations

import json
import re
import struct
import sys
from pathlib import Path

APP_CORE = Path(__file__).resolve().parent.parent / "10_应用核心"
if str(APP_CORE) not in sys.path:
    sys.path.insert(0, str(APP_CORE))
from toolkit_core.fpk_frames import FPK_HEADER_SIZE, FpkFrameError, iter_fpk_frames
from toolkit_core.paths import DEFAULT_OUTPUT_ROOT

ROOT = Path(r"E:/mrzh/res")
OUT = DEFAULT_OUTPUT_ROOT / "fpk"
HEADER = FPK_HEADER_SIZE
MAGIC = b"\x28\xb5\x2f\xfd"


def frame_type(out: bytes) -> str:
    """Classify a successfully decompressed FPK frame without claiming semantic binding."""
    if out.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if out.startswith(b"DDS ") and len(out) >= 20:
        width, height = struct.unpack_from("<II", out, 12)
        return f"dds_{width}x{height}"
    if out[:1] in (b"{", b"["):
        return "json"
    if b"\nsize: " in out[:512] and b"\nformat:" in out[:512]:
        return "manifest"
    if out.startswith(b"\n"):
        return "manifest"
    return "other"


def parse_manifest(out: bytes) -> dict:
    """Extract limited Atlas metadata from a manifest frame."""
    text = out.decode("utf-8", "replace")
    atlas = re.search(r"([A-Za-z0-9_.\-]+\.png)\s*\nsize:\s*(\d+),(\d+)\s*\nformat:\s*(\S+)", text)
    names = re.findall(r"^([A-Za-z0-9_.\-]+)\s*$", text, re.M)
    return {
        "atlas": atlas.group(1) if atlas else None,
        "size": (int(atlas.group(2)), int(atlas.group(3))) if atlas else None,
        "format": atlas.group(4) if atlas else None,
        "sub_count": len(names) - (1 if atlas else 0),
        "names": names[:40],
    }


def _row(frame, out: bytes) -> dict:
    kind = frame_type(out)
    row = {
        "idx": frame.index,
        "off": frame.offset,
        "comp": frame.packed_size,
        "out": frame.output_size,
        "type": kind,
        "storage": frame.storage,
        "padding_size": frame.padding_size,
        "boundary_verified": True,
    }
    if kind == "manifest":
        row["manifest"] = parse_manifest(out)
    elif kind == "json":
        row["json_head"] = out[:300].decode("utf-8", "replace")
    return row


def summarize_fpk_frames(path: Path | str, *, chunk_size: int = 8 << 20) -> dict:
    """Return a manifest of only boundary-verified frames in one FPK stream."""
    source = Path(path)
    rows: list[dict] = []
    types: dict[str, int] = {}
    for frame, out in iter_fpk_frames(source, chunk_size=chunk_size):
        row = _row(frame, out)
        rows.append(row)
        types[row["type"]] = types.get(row["type"], 0) + 1
    return {
        "source": str(source),
        "frame_boundary_method": "sequential_decompressobj_eof_plus_zero_padding",
        "total_frames": len(rows),
        "types": types,
        "rows": rows,
    }


def scan_overview(path: Path | str, scan_limit: int = 8 << 20) -> list[dict]:
    """Read the first 40 real frames; ``scan_limit`` remains only for legacy callers."""
    del scan_limit
    frames: list[dict] = []
    try:
        for frame, out in iter_fpk_frames(path):
            frames.append(_row(frame, out))
            if len(frames) >= 40:
                break
    except FpkFrameError as exc:
        frames.append({"idx": len(frames), "error": str(exc), "boundary_verified": False})
    return frames


def _container_kind(path: Path) -> str:
    with path.open("rb") as handle:
        head = handle.read(HEADER + 64)
    payload = head[HEADER:]
    if payload[:4] == b"\x00\x00\x00\x14" and b"ftyp" in payload:
        return "mp4(isom)"
    if payload.startswith(b"FSB5"):
        return "fsb5_audio"
    if payload.startswith(MAGIC):
        return "zstd_stream"
    return "enc/unknown"


def cmd_overview() -> None:
    """Create a bounded overview; non-Zstd packs are classified but not force-decoded."""
    out_dir = OUT / "overview"
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for path in sorted(ROOT.glob("*.fpk")):
        kind = _container_kind(path)
        frames = scan_overview(path) if kind == "zstd_stream" else []
        manifests = [frame for frame in frames if frame.get("type") == "manifest"]
        types: dict[str, int] = {}
        for frame in frames:
            if "type" in frame:
                types[frame["type"]] = types.get(frame["type"], 0) + 1
        row = {
            "name": path.name,
            "size": path.stat().st_size,
            "kind": kind,
            "frames_scanned": len(frames),
            "types": types,
            "atlas": manifests[0]["manifest"]["atlas"] if manifests else None,
            "sub": manifests[0]["manifest"]["sub_count"] if manifests else None,
            "errors": [frame["error"] for frame in frames if "error" in frame],
        }
        rows.append(row)
        print(f"{path.name:9s} {kind:14s} frames={len(frames):3d} types={types} atlas={row['atlas']} sub={row['sub']}")
    result = out_dir / "fpk_overview.json"
    result.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"\n结果已保存: {result}")


def cmd_full(fpk_path: str | None = None) -> None:
    """Write the complete verified frame manifest for one Zstd FPK package."""
    source = Path(fpk_path) if fpk_path else ROOT / "001.fpk"
    if not source.exists():
        print(f"文件不存在: {source}")
        return
    out_dir = OUT / source.stem
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"扫描: {source} ({source.stat().st_size // 1024 // 1024}MB)")

    rows: list[dict] = []
    types: dict[str, int] = {}
    for frame, out in iter_fpk_frames(source):
        row = _row(frame, out)
        rows.append(row)
        kind = row["type"]
        types[kind] = types.get(kind, 0) + 1
        if kind == "manifest":
            (out_dir / f"manifest_{frame.index:05d}.txt").write_bytes(out)
        elif kind == "json":
            (out_dir / f"skel_{frame.index:05d}.json").write_bytes(out)
        elif kind.startswith("dds_") and frame.index in (1, 2, 4):
            (out_dir / f"tex_{frame.index:05d}_{kind[4:]}.dds").write_bytes(out)
        if (frame.index + 1) % 5000 == 0:
            print(f"  进度: {frame.index + 1}")

    result = {
        "source": str(source),
        "frame_boundary_method": "sequential_decompressobj_eof_plus_zero_padding",
        "total_frames": len(rows),
        "types": types,
        "rows": rows,
    }
    (out_dir / "frames_full.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    manifests = [row for row in rows if row.get("manifest")]
    print(f"\n类型统计: {types}")
    print(f"manifest: {[row['manifest']['atlas'] for row in manifests]}")
    print(f"结果已保存: {out_dir}")


def cmd_probe(path: str = r"E:/mrzh/res/001.fpk") -> None:
    """Aggregate unclassified verified frames without emitting giant terminal lists."""
    import collections

    source = Path(path)
    patterns = collections.Counter()
    version_hits = collections.Counter()
    total = 0
    other = 0
    for _frame, out in iter_fpk_frames(source):
        total += 1
        if frame_type(out) == "other":
            other += 1
            patterns[out[:8].hex()] += 1
            version_hits[b"2.1.0.0" in out[:512]] += 1
    result = {
        "source": str(source),
        "total": total,
        "other": other,
        "head_patterns": patterns.most_common(30),
        "version_2_1_0_0": dict(version_hits),
        "frame_boundary_method": "sequential_decompressobj_eof_plus_zero_padding",
    }
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / "probe_other_frames.json"
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, ensure_ascii=False, indent=1))
    print("saved ->", target)


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        print("示例:")
        print("  python fpk_toolkit.py overview")
        print("  python fpk_toolkit.py full E:/mrzh/res/001.fpk")
        return
    command = sys.argv[1].lower()
    if command == "overview":
        cmd_overview()
    elif command == "probe":
        cmd_probe(sys.argv[2] if len(sys.argv) > 2 else r"E:/mrzh/res/001.fpk")
    elif command == "full":
        cmd_full(sys.argv[2] if len(sys.argv) > 2 else None)
    else:
        print(f"未知命令: {command}")
        print(__doc__)


if __name__ == "__main__":
    main()
