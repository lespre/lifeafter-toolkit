# -*- coding: utf-8 -*-
"""找音频：在客户端容器里扫音频签名（不依赖任何音频解码器）。

为什么要签名扫：磁盘上 0 个 .wem/.bnk/.ogg/.wav（`Documents\\voice` 还是空的），
说明声音要么在 `res.npk` / `res.gpk` / `compress_pc` 里，要么按需下载。

扫的签名：
  RIFF/RIFX  —— wav / Wwise .wem（Wwise 用 RIFF 容器，fmt 里是 Wwise 的 codec id）
  OggS       —— ogg / ogg-vorbis
  BKHD       —— Wwise SoundBank (.bnk)
  FSB5/FEV   —— FMOD
  ID3/0xFFFB —— mp3

大包只用 mmap 扫原始字节（快）；小包（<120MB）额外解一遍 zstd frame 再扫（因为
热更包里的资源是压过的）。

产物：analysis/audit/audio_signatures_in_client.json
用法：python tools/scan_client_for_audio.py
"""
from __future__ import annotations

import json
import mmap
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis" / "audit" / "audio_signatures_in_client.json"
MRZH = Path(r"E:\mrzh")
TARGETS = [MRZH / "res.npk", MRZH / "res.gpk",
           MRZH / "Documents" / "compress_pc",
           MRZH / "Documents" / "downloaded_packages"]
SIGS = {b"RIFF": "riff(wav/wem)", b"RIFX": "rifx", b"OggS": "ogg",
        b"BKHD": "wwise-bank", b"FSB5": "fmod-fsb5", b"FEV ": "fmod-fev",
        b"ID3\x03": "mp3-id3", b"\xff\xfb": "mp3-frame"}
ZSTD_MAGIC = bytes([0x28, 0xB5, 0x2F, 0xFD])


def scan_bytes(buf, label, hits, cap=60):
    for sig, name in SIGS.items():
        for m in re.finditer(re.escape(sig), buf):
            if len(hits) >= cap * 8:
                return
            hits.append({"container": label, "sig": name, "offset": m.start()})
            break  # 每个容器每类签名只记首个（够判断有无）


def main() -> int:
    hits, containers = [], []
    for t in TARGETS:
        if t.is_file():
            files = [t]
        elif t.is_dir():
            files = sorted(p for p in t.rglob("*") if p.is_file())[:40]
        else:
            containers.append({"path": str(t), "exists": False})
            continue
        for f in files:
            size = f.stat().st_size
            with f.open("rb") as fh:
                mm = mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ)
                try:
                    buf = mm
                    n0 = len(hits)
                    scan_bytes(buf, f.name, hits)
                    zframes = 0
                    if size < 120 * 1024 * 1024:
                        pos = 0
                        while True:
                            j = buf.find(ZSTD_MAGIC, pos)
                            if j < 0 or zframes > 4000:
                                break
                            zframes += 1
                            pos = j + 4
                            try:
                                import zstandard as zstd
                                blob = zstd.ZstdDecompressor().decompressobj().decompress(
                                    bytes(buf[j:j + 4 * 1024 * 1024]))
                                if blob:
                                    scan_bytes(blob, f.name + ":zstd", hits)
                            except Exception:
                                pass
                    containers.append({"path": str(f.relative_to(MRZH)), "bytes": size,
                                       "zstd_frames": zframes, "sig_hits": len(hits) - n0})
                    print(f"  {f.name}: {size/1e6:.1f}MB frames={zframes} 命中={len(hits)-n0}", flush=True)
                finally:
                    mm.close()
    by = Counter(h["sig"] for h in hits)
    doc = {"schema": "audio-signatures-in-client-v1",
           "generated": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
           "targets": [str(t) for t in TARGETS], "containers": containers,
           "total_sig_hits": len(hits), "by_sig": dict(by), "sample": hits[:80]}
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"containers": len(containers), "total_sig_hits": len(hits), "by_sig": dict(by)},
                     ensure_ascii=False))
    print("→", OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
