# -*- coding: utf-8 -*-
"""宽扫资源包：找**任何**与皮肤相关的图片路径（不限于脚本表引用）。

动机：脚本包只声明了 UI 壳与 .gim 模型；皮肤"展示图"若存在，只可能在资源包
（gres/*.gpk、res.gpk）里以**具名文件**形式出现（先例：0058.gpk 里有
kaijiayongshi_box.png 这类具名 PNG）。此前的搜索只匹配"UI 清单里的名字"，
没做过"任意含 skin 的图片"宽扫。

做法：扫每包里的 Zstd frame + 内嵌 PNG/DDS 签名；用宽正则抓
  (a) 含 skin/weapon_skin 的图片或模型路径
  (b) 皮肤 stem（skin_XXXX_YYY）
命中即记录（不落盘大图；只记命中清单 + 前若干个小图预览）。

产物：analysis/audit/skin_assets_in_packs.json
用法：python tools/scan_packs_for_skin_assets.py [--packs N]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis" / "audit" / "skin_assets_in_packs.json"
PREVIEW_DIR = Path(r"E:\la拆包项目\03拆包产物\skin_assets_preview")
PACKS = [Path(r"E:\mrzh\res.gpk"), Path(r"E:\mrzh\res.npk")] + sorted(
    Path(r"E:\mrzh\Documents\gres").glob("*.gpk"))

ZSTD_MAGIC = bytes([0x28, 0xB5, 0x2F, 0xFD])  # zstd frame magic
PNG_SIG = b"\x89PNG\r\n\x1a\n"
DDS_SIG = b"DDS "
PATH_RE = re.compile(rb"[A-Za-z0-9_/.-]{3,160}\.(?:png|jpg|dds|tga|gim|prefab)", re.I)
SKINWORD = re.compile(rb"skin", re.I)


def iter_magic(data: bytes, needle: bytes = ZSTD_MAGIC):
    """用 bytes.find 扫描 magic（不要用 re：magic 里的 \x28 会被当成分组符）。"""
    pos = 0
    while True:
        j = data.find(needle, pos)
        if j < 0:
            return
        yield type("M", (), {"start": lambda self, _j=j: _j})()
        pos = j + 4


def zstd_decompress(blob: bytes):
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
    ap.add_argument("--packs", type=int, default=0)
    a = ap.parse_args()
    packs = PACKS[: a.packs] if a.packs else PACKS
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    hits: list[dict] = []
    per_pack = []
    saved = 0
    for pk in packs:
        if not pk.exists():
            continue
        data = pk.read_bytes()
        n_frame = 0
        for m in iter_magic(data):
            blob = zstd_decompress(data[m.start():m.start() + 8 * 1024 * 1024])
            if not blob:
                continue
            n_frame += 1
            if not SKINWORD.search(blob[:4_000_000]):
                continue
            for pm in PATH_RE.finditer(blob[:4_000_000]):
                p = pm.group(0).decode("utf-8", "ignore")
                if "skin" in p.lower():
                    hits.append({"pack": pk.name, "path": p})
            # 存前几个小图当预览
            if saved < 60:
                for sig, ext in ((PNG_SIG, ".png"), (DDS_SIG, ".dds")):
                    j = blob.find(sig)
                    if 0 <= j and len(blob) - j < 3_000_000:
                        name = hashlib.sha256(blob[j:j + 200]).hexdigest()[:10] + ext
                        (PREVIEW_DIR / name).write_bytes(blob[j:])
                        saved += 1
                        break
        per_pack.append({"pack": pk.name, "bytes": len(data), "zstd_frames": n_frame})
        print(f"  {pk.name}: frames={n_frame} 命中累计={len(hits)}", flush=True)
    cnt = Counter(h["path"] for h in hits)
    doc = {"schema": "skin-assets-in-packs-v1",
           "generated": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
           "packs": per_pack, "hit_rows": len(hits), "unique_paths": len(cnt),
           "by_ext": dict(Counter(p.rsplit('.', 1)[-1].lower() for p in cnt).most_common()),
           "paths": [{"path": p, "count": c} for p, c in cnt.most_common(600)],
           "preview_dir": str(PREVIEW_DIR), "preview_saved": saved}
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: doc[k] for k in ("hit_rows", "unique_paths", "by_ext", "preview_saved")}, ensure_ascii=False))
    print("样例路径:", [p["path"] for p in doc["paths"][:15]])
    print("→", OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
