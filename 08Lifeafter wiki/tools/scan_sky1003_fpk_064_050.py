# -*- coding: utf-8 -*-
"""倒序扫描 064..050.fpk，命中 sky1003 后停止并提取邻近 DDS/FSB5。"""
from __future__ import annotations

import io
import json
import struct
import sys
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

CORE = Path(r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心")
UNPACKER = Path(r"E:\la拆包项目\01拆包器本体\工具库\01_核心解包器")
sys.path.insert(0, str(CORE))
sys.path.insert(0, str(UNPACKER))

from toolkit_core.fpk_frames import FpkFrameError, iter_fpk_frames
from PIL import Image
import texture2ddecoder
from lifeafter_unpacker_full import extract_fsb

SRC_ROOT = Path(r"E:\mrzh\res")
OUT_ROOT = Path(r"E:\la拆包项目\03拆包产物\sky1003")
WAV_ROOT = OUT_ROOT / "wav"
PACK_NUMBERS = list(range(64, 49, -1))
KEYWORDS = (b"skin_1003_010", b"guangying", b"yongtandiao")
MAX_FRAMES = 60000
NEIGHBOR_RADIUS = 10
CONTEXT_RADIUS = 180


def safe_text(blob: bytes) -> str:
    text = blob.decode("utf-8", "replace")
    return "".join(
        ch if ch in "\t\r\n" or ord(ch) >= 0x20 else f"\\x{ord(ch):02x}"
        for ch in text
    )


def frame_kind(payload: bytes, reported: str) -> str:
    if payload.startswith(b"FSB5"):
        return "FSB5"
    if payload.startswith(b"DDS "):
        return "DDS"
    return reported


def find_hits(payload: bytes) -> list[dict]:
    lowered = payload.lower()
    hits = []
    for term in KEYWORDS:
        start = 0
        needle = term.lower()
        while True:
            pos = lowered.find(needle, start)
            if pos < 0:
                break
            lo = max(0, pos - CONTEXT_RADIUS)
            hi = min(len(payload), pos + len(term) + CONTEXT_RADIUS)
            hits.append(
                {
                    "keyword": term.decode("ascii"),
                    "payload_offset": pos,
                    "context_range": [lo, hi],
                    "context_text": safe_text(payload[lo:hi]),
                    "context_hex": payload[lo:hi].hex(),
                }
            )
            start = pos + len(needle)
    return hits


def save_dds(pack: str, frame, payload: bytes) -> dict:
    pack_dir = OUT_ROOT / Path(pack).stem
    pack_dir.mkdir(parents=True, exist_ok=True)
    stem = f"frame_{frame.index:05d}"
    dds_path = pack_dir / f"{stem}.dds"
    png_path = pack_dir / f"{stem}.png"
    dds_path.write_bytes(payload)

    result = {
        "frame_index": frame.index,
        "frame_offset": frame.offset,
        "output_size": frame.output_size,
        "dds_path": str(dds_path),
        "png_path": None,
        "decode": None,
        "width": None,
        "height": None,
        "dxgi_format": None,
        "alpha_mode": "preserved",
        "error": None,
    }
    try:
        if len(payload) < 148 or payload[:4] != b"DDS ":
            raise ValueError("not a complete DDS header")
        w, h = struct.unpack_from("<II", payload, 12)
        fmt = struct.unpack_from("<I", payload, 128)[0]
        result.update({"width": w, "height": h, "dxgi_format": fmt})
        if not w or not h:
            raise ValueError(f"invalid dimensions {w}x{h}")
        if fmt in (98, 99):
            # BC7: Pillow must not open this DDS; decode the payload explicitly.
            raw = texture2ddecoder.decode_bc7(payload[148:], w, h)
            im = Image.frombytes("RGBA", (w, h), raw)
            im.save(png_path)  # keep RGBA/alpha; do not convert to RGB
            result["decode"] = "texture2ddecoder.decode_bc7"
        else:
            with Image.open(io.BytesIO(payload)) as src:
                im = src.convert("RGBA")
                im.save(png_path)  # keep RGBA/alpha
            result["decode"] = "Pillow_non_BC7_RGBA"
        result["png_path"] = str(png_path)
        with Image.open(png_path) as check:
            check.load()
            result["png_mode"] = check.mode
            result["png_size"] = list(check.size)
    except Exception as exc:
        result["error"] = repr(exc)
    return result


def save_fsb(pack: str, frame, payload: bytes) -> dict:
    bank_dir = WAV_ROOT / Path(pack).stem / f"frame_{frame.index:05d}"
    bank_dir.mkdir(parents=True, exist_ok=True)
    fsb_path = bank_dir / f"frame_{frame.index:05d}.fsb"
    fsb_path.write_bytes(payload)
    result = {
        "frame_index": frame.index,
        "frame_offset": frame.offset,
        "fsb_path": str(fsb_path),
        "wav_paths": [],
        "error": None,
    }
    try:
        result["wav_paths"] = [str(Path(p)) for p in extract_fsb(str(fsb_path), str(bank_dir))]
    except Exception as exc:
        result["error"] = repr(exc)
    return result


def scan_pack(path: Path) -> dict:
    recent = deque(maxlen=NEIGHBOR_RADIUS)
    captured = []
    hits = []
    scanned = 0
    capture_until = None
    try:
        for frame, payload in iter_fpk_frames(path):
            if frame.index >= MAX_FRAMES:
                break
            scanned = frame.index + 1
            kind = frame_kind(payload, frame.output_magic)
            item = {"frame": frame, "payload": payload, "kind": kind}
            recent.append(item)
            frame_hits = find_hits(payload)
            if frame_hits and not hits:
                hits = [
                    {
                        "pack": path.name,
                        "frame_index": frame.index,
                        "frame_offset": frame.offset,
                        "packed_size": frame.packed_size,
                        "output_size": frame.output_size,
                        "output_magic": frame.output_magic,
                        "storage": frame.storage,
                        "kind": kind,
                        **hit,
                    }
                    for hit in frame_hits
                ]
                captured = list(recent)
                capture_until = frame.index + NEIGHBOR_RADIUS
            elif hits and frame.index <= capture_until:
                captured.append(item)
            elif hits and frame.index > capture_until:
                break
    except FpkFrameError as exc:
        return {
            "pack": path.name,
            "path": str(path),
            "scanned_frames": scanned,
            "scan_cap": MAX_FRAMES,
            "hit": bool(hits),
            "hits": hits,
            "error": repr(exc),
        }

    unique = {item["frame"].index: item for item in captured}
    captured = [unique[i] for i in sorted(unique)]
    nearby_dds = []
    nearby_fsb5 = []
    if hits:
        hit_indexes = {h["frame_index"] for h in hits}
        for item in captured:
            idx = item["frame"].index
            if not any(abs(idx - hit_idx) <= NEIGHBOR_RADIUS for hit_idx in hit_indexes):
                continue
            if item["kind"] == "DDS":
                nearby_dds.append(save_dds(path.name, item["frame"], item["payload"]))
            elif item["kind"] == "FSB5":
                nearby_fsb5.append(save_fsb(path.name, item["frame"], item["payload"]))

    return {
        "pack": path.name,
        "path": str(path),
        "scanned_frames": scanned,
        "scan_cap": MAX_FRAMES,
        "hit": bool(hits),
        "hits": hits,
        "first_hit_frame": min((h["frame_index"] for h in hits), default=None),
        "neighbor_radius_frames": NEIGHBOR_RADIUS,
        "nearby_dds": nearby_dds,
        "nearby_fsb5": nearby_fsb5,
        "error": None,
    }


def main() -> int:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    WAV_ROOT.mkdir(parents=True, exist_ok=True)
    results = []
    stopped_on = None
    for number in PACK_NUMBERS:
        path = SRC_ROOT / f"{number:03d}.fpk"
        if not path.exists():
            result = {"pack": path.name, "path": str(path), "exists": False, "hit": False}
            results.append(result)
            print(json.dumps(result, ensure_ascii=False), flush=True)
            continue
        print(f"{path.name}: scanning first {MAX_FRAMES} frames", flush=True)
        result = scan_pack(path)
        result["exists"] = True
        results.append(result)
        print(
            json.dumps(
                {
                    "pack": result["pack"],
                    "scanned_frames": result["scanned_frames"],
                    "hit": result["hit"],
                    "first_hit_frame": result.get("first_hit_frame"),
                    "nearby_dds": len(result.get("nearby_dds", [])),
                    "nearby_fsb5": len(result.get("nearby_fsb5", [])),
                    "wav": sum(len(x.get("wav_paths", [])) for x in result.get("nearby_fsb5", [])),
                    "error": result.get("error"),
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
        if result.get("hit"):
            stopped_on = path.name
            break

    report = {
        "schema": "sky1003-fpk-search-v2-bc7-rgba",
        "generated": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "source_root": str(SRC_ROOT),
        "source_policy": "read_only",
        "pack_order": [f"{n:03d}.fpk" for n in PACK_NUMBERS],
        "scan_cap_per_pack": MAX_FRAMES,
        "keywords": [term.decode("ascii") for term in KEYWORDS],
        "neighborhood_radius_frames": NEIGHBOR_RADIUS,
        "dds_bc7_rule": "dxgiFormat 98/99 -> texture2ddecoder.decode_bc7(data[148:],w,h)",
        "png_rule": "RGBA direct save; no RGB conversion",
        "stopped_on_first_hit": stopped_on,
        "results": results,
    }
    report_path = OUT_ROOT / "sky1003_fpk_search_064_050_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"REPORT={report_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
