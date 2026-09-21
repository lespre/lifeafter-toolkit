# -*- coding: utf-8 -*-
"""按**UI 声明的路径**从资源包里挖图片（不用名字猜纹理）。

输入：analysis/audit/weapon_skin_ui_asset_paths.json 里的 ui/ 路径（图鉴/品级/放映图标）
做法：扫资源包（res.npk / res.gpk / Documents/gres/*.gpk）里的
  · Zstd frame（资源包主体，见交接日志第 23 节）
  · 直接内嵌的 PNG/DDS 签名
  匹配目标路径字面 → 命中即落盘（PNG 直存；DDS 用 Pillow 转 PNG）。

只读源包；产物落 03拆包产物/ui_assets_<date>/ + manifest.json。
用法：python tools/extract_ui_assets.py [--limit 40] [--packs N]
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import sys
import zlib
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "analysis" / "audit" / "weapon_skin_ui_asset_paths.json"
OUT = Path(r"E:\la拆包项目\03拆包产物") / f"ui_assets_{datetime.now():%Y%m%d}"
PACKS = [Path(r"E:\mrzh\res.npk"), Path(r"E:\mrzh\res.gpk")] + sorted(
    Path(r"E:\mrzh\Documents\gres").glob("*.gpk"))

ZSTD_MAGIC = b"\x28\xb5\x2f\xfd"
PNG_SIG = b"\x89PNG\r\n\x1a\n"
DDS_SIG = b"DDS "


def try_zstd(blob: bytes):
    try:
        import zstandard as zstd
    except ImportError:
        return None
    try:
        return zstd.ZstdDecompressor().decompressobj().decompress(blob)
    except Exception:
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=60)
    ap.add_argument("--packs", type=int, default=0, help="只扫前 N 个包（0=全部）")
    a = ap.parse_args()
    targets = json.loads(SRC.read_text(encoding="utf-8"))["ui_paths"]
    # 只取"文件名唯一"的目标，便于在包里按名字命中
    want: dict[str, str] = {}
    for p in targets:
        name = p.replace("\\", "/").rsplit("/", 1)[-1]
        if name.lower().endswith(".png") and name not in want:
            want[name] = p
    todo = list(want.items())[: a.limit]
    print(f"目标 {len(todo)} 个 png（来自 {len(targets)} 条 ui 路径）")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "files").mkdir(exist_ok=True)
    packs = PACKS[: a.packs] if a.packs else PACKS
    manifest, found = [], {}
    try:
        from PIL import Image
    except ImportError:
        Image = None
    for pk in packs:
        if not pk.exists() or len(found) >= len(todo):
            continue
        size = pk.stat().st_size
        print(f"== {pk.name} ({size/2**30:.2f} GB)")
        with pk.open("rb") as fh:
            data = fh.read()
        # (a) 直接内嵌 PNG
        for name, rel in todo:
            if name.encode() in found:
                continue
            i = data.find(name.encode())
            if i < 0:
                continue
            j = data.find(PNG_SIG, i, i + 4096)
            if j >= 0:
                end = data.find(b"IEND", j)
                blob = data[j:end + 8] if end > 0 else None
                if blob:
                    out = OUT / "files" / name
                    out.write_bytes(blob)
                    found[name] = {"pack": pk.name, "kind": "inline-png", "path": rel,
                                   "bytes": len(blob), "sha256": hashlib.sha256(blob).hexdigest()}
        # (b) Zstd frame（资源包主体）
        pos = 0
        frames = 0
        while True:
            k = data.find(ZSTD_MAGIC, pos)
            if k < 0:
                break
            blob = try_zstd(data[k:k + 8 * 1024 * 1024])
            pos = k + 4
            if not blob:
                continue
            frames += 1
            for name, rel in todo:
                if name in found:
                    continue
                if name.encode() in blob:
                    for sig, kind in ((PNG_SIG, "zstd-png"), (DDS_SIG, "zstd-dds")):
                        j = blob.find(sig)
                        if j >= 0:
                            out = OUT / "files" / (name if kind.endswith("png") else name + ".dds")
                            out.write_bytes(blob[j:] if kind.endswith("png") else blob[j:])
                            found[name] = {"pack": pk.name, "kind": kind, "path": rel,
                                           "bytes": len(blob) - j,
                                           "sha256": hashlib.sha256(blob[j:]).hexdigest()}
                            break
        print(f"   zstd frames 解出 {frames}；累计命中 {len(found)}/{len(todo)}")
        manifest.append({"pack": pk.name, "bytes": size, "zstd_frames": frames})
    # DDS → PNG
    if Image:
        for f in (OUT / "files").glob("*.dds"):
            try:
                im = Image.open(f)
                png = f.with_suffix(".png")
                im.save(png)
                f.unlink()
                found.setdefault(png.name, {})["converted_from"] = "dds"
            except Exception as exc:
                found.setdefault(f.name, {})["dds_error"] = str(exc)[:120]
    (OUT / "manifest.json").write_text(json.dumps(
        {"schema": "ui-assets-v1",
         "generated": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
         "targets": len(todo), "found": len(found), "packs": manifest, "assets": found},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"found": len(found), "of": len(todo), "out": str(OUT)}, ensure_ascii=False))
    for k in list(found)[:15]:
        print("  ✓", k)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
