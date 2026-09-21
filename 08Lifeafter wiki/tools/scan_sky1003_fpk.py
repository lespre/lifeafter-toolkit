# -*- coding: utf-8 -*-
"""倒序扫描 049..037.fpk 的解压帧，定位 sky1003 皮肤资源。"""
from __future__ import annotations

import io
import json
import re
import struct
import sys
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

# User-verified import path; keep source packages read-only.
CORE = Path(r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心")
UNPACKER = Path(r"E:\la拆包项目\01拆包器本体\工具库\01_核心解包器")
sys.path.insert(0, str(CORE))
sys.path.insert(0, str(UNPACKER))
from toolkit_core.fpk_frames import FpkFrameError, iter_fpk_frames
from lifeafter_unpacker_full import extract_fsb

SRC_ROOT = Path(r"E:\mrzh\res")
OUT_ROOT = Path(r"E:\la拆包项目\03拆包产物\sky1003")
WAV_ROOT = OUT_ROOT / "wav"
PACK_NUMBERS = list(range(49, 36, -1))
KEYWORDS = [b"skin_1003_010", b"guangying", b"yongtandiao"]
CONTEXT_RADIUS = 180
NEAR_RADIUS = 10
MAX_FRAMES = 60000
DDS_BC7_FORMATS = {98, 99}


def frame_kind(payload: bytes, reported: str) -> str:
    if payload.startswith(b"FSB5"):
        return "FSB5"
    if payload.startswith(b"DDS "):
        return "DDS"
    return reported


def safe_text(blob: bytes) -> str:
    text = blob.decode("utf-8", "replace")
    # Keep context readable while preserving replacement markers and punctuation.
    return "".join(ch if ch in "\t\r\n" or ord(ch) >= 0x20 else f"\\x{ord(ch):02x}" for ch in text)


def find_hits(payload: bytes) -> list[dict]:
    lower = payload.lower()
    hits = []
    for term in KEYWORDS:
        needle = term.lower()
        start = 0
        while True:
            pos = lower.find(needle, start)
            if pos < 0:
                break
            lo = max(0, pos - CONTEXT_RADIUS)
            hi = min(len(payload), pos + len(term) + CONTEXT_RADIUS)
            hits.append({
                "keyword": term.decode("ascii"),
                "payload_offset": pos,
                "context_range": [lo, hi],
                "context_text": safe_text(payload[lo:hi]),
                "context_hex": payload[lo:hi].hex(),
            })
            start = pos + max(1, len(needle))
    return hits


def save_dds(pack: str, frame_index: int, payload: bytes) -> dict:
    pack_dir = OUT_ROOT / Path(pack).stem
    pack_dir.mkdir(parents=True, exist_ok=True)
    stem = f"frame_{frame_index:05d}"
    dds_path = pack_dir / f"{stem}.dds"
    png_path = pack_dir / f"{stem}.png"
    dds_path.write_bytes(payload)
    converted = False
    verified = False
    verify_error = None
    decode_method = None
    width = height = dxgi_format = None
    try:
        from PIL import Image
        if len(payload) < 148 or not payload.startswith(b"DDS "):
            raise ValueError("not a DX10 DDS payload")
        # DDS stores height at 12 and width at 16; DXGI format is at 128.
        height, width = struct.unpack_from("<II", payload, 12)
        dxgi_format = struct.unpack_from("<I", payload, 128)[0]
        if dxgi_format in DDS_BC7_FORMATS:
            import texture2ddecoder
            # BC7 pixels begin at offset 148. Keep the decoded RGBA alpha.
            raw = texture2ddecoder.decode_bc7(payload[148:], width, height)
            im = Image.frombytes("RGBA", (width, height), raw)
            decode_method = "texture2ddecoder.decode_bc7"
        else:
            im = Image.open(io.BytesIO(payload)).convert("RGBA")
            decode_method = "Pillow-non-BC7-fallback"
        im.save(png_path)
        converted = True
        with Image.open(png_path) as check:
            check.load()
            verified = check.mode == "RGBA" and check.size == (width, height)
    except Exception as exc:
        verify_error = repr(exc)
    return {
        "frame_index": frame_index,
        "dds_path": str(dds_path),
        "png_path": str(png_path) if png_path.exists() else None,
        "png_converted": converted,
        "png_verified": verified,
        "png_verify_error": verify_error,
        "width": width,
        "height": height,
        "dxgi_format": dxgi_format,
        "decode_method": decode_method,
    }


def save_fsb(pack: str, frame_index: int, payload: bytes) -> dict:
    bank_dir = WAV_ROOT / Path(pack).stem / f"frame_{frame_index:05d}"
    bank_dir.mkdir(parents=True, exist_ok=True)
    fsb_path = bank_dir / f"frame_{frame_index:05d}.fsb"
    fsb_path.write_bytes(payload)
    wav_paths = []
    error = None
    try:
        wav_paths = [str(Path(p)) for p in extract_fsb(str(fsb_path), str(bank_dir))]
    except Exception as exc:
        error = repr(exc)
    return {
        "frame_index": frame_index,
        "fsb_path": str(fsb_path),
        "wav_paths": wav_paths,
        "extract_error": error,
    }


def scan_pack(path: Path) -> dict:
    recent = deque(maxlen=NEAR_RADIUS)
    hits = []
    seen = 0
    stopped_after = None
    captured = []
    try:
        for frame, payload in iter_fpk_frames(path):
            if frame.index >= MAX_FRAMES:
                break
            seen = frame.index + 1
            kind = frame_kind(payload, frame.output_magic)
            item = {"frame": frame, "payload": payload, "kind": kind}
            recent.append(item)
            frame_hits = find_hits(payload)
            if frame_hits and not hits:
                hits = [{
                    "pack": path.name,
                    "frame_index": frame.index,
                    "frame_offset": frame.offset,
                    "packed_size": frame.packed_size,
                    "output_size": frame.output_size,
                    "output_magic": frame.output_magic,
                    "storage": frame.storage,
                    "kind": kind,
                    **h,
                } for h in frame_hits]
                # Keep previous context and inspect a bounded forward neighborhood.
                captured = list(recent)
                stopped_after = frame.index + NEAR_RADIUS
            elif hits and frame.index <= stopped_after:
                captured.append(item)
            elif hits and frame.index > stopped_after:
                break
        # If the first hit was in the initial recent deque, remove duplicate identity.
        uniq = {}
        for item in captured:
            uniq[item["frame"].index] = item
        captured = [uniq[i] for i in sorted(uniq)]
    except FpkFrameError as exc:
        return {
            "pack": path.name,
            "path": str(path),
            "scanned_frames": seen,
            "hit": bool(hits),
            "hits": hits,
            "error": repr(exc),
        }

    nearby_dds = []
    nearby_fsb = []
    if hits:
        hit_indices = {h["frame_index"] for h in hits}
        # Capture only frames in the bounded neighborhood of the first hit.
        for item in captured:
            idx = item["frame"].index
            if any(abs(idx - hidx) <= NEAR_RADIUS for hidx in hit_indices):
                if item["kind"] == "DDS":
                    nearby_dds.append(save_dds(path.name, idx, item["payload"]))
                elif item["kind"] == "FSB5":
                    nearby_fsb.append(save_fsb(path.name, idx, item["payload"]))

    return {
        "pack": path.name,
        "path": str(path),
        "scanned_frames": seen,
        "scan_cap": MAX_FRAMES,
        "hit": bool(hits),
        "hits": hits,
        "first_hit_frame": min((h["frame_index"] for h in hits), default=None),
        "nearby_dds": nearby_dds,
        "nearby_fsb5": nearby_fsb,
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
            results.append({"pack": path.name, "path": str(path), "exists": False, "hit": False})
            print(f"{path.name}: missing (skipped)", flush=True)
            continue
        print(f"{path.name}: scanning first {MAX_FRAMES} verified frames", flush=True)
        result = scan_pack(path)
        result["exists"] = True
        results.append(result)
        print(json.dumps({
            "pack": result["pack"],
            "scanned_frames": result["scanned_frames"],
            "hit": result["hit"],
            "first_hit_frame": result.get("first_hit_frame"),
            "nearby_dds": len(result.get("nearby_dds", [])),
            "nearby_wav": sum(len(x.get("wav_paths", [])) for x in result.get("nearby_fsb5", [])),
            "error": result.get("error"),
        }, ensure_ascii=False), flush=True)
        if result.get("hit"):
            stopped_on = path.name
            break

    report = {
        "schema": "sky1003-fpk-search-v1",
        "generated": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "source_root": str(SRC_ROOT),
        "source_policy": "read_only",
        "pack_order": [f"{n:03d}.fpk" for n in PACK_NUMBERS],
        "scan_cap_per_pack": MAX_FRAMES,
        "keywords": [x.decode("ascii") for x in KEYWORDS],
        "neighborhood_radius_frames": NEAR_RADIUS,
        "stopped_on_first_hit": stopped_on,
        "results": results,
    }
    report_path = OUT_ROOT / "sky1003_fpk_search_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"REPORT={report_path}", flush=True)
    print(json.dumps({
        "packs_processed": len(results),
        "hits": sum(1 for x in results if x.get("hit")),
        "stopped_on_first_hit": stopped_on,
        "report": str(report_path),
    }, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
