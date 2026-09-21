# -*- coding: utf-8 -*-
"""从 fpk 主资源包导出贴图（含图集切片）——2026-09-13 定稿版。

这套链条是踩完两个坑后定下来的，**别改**：
  ① BC7 不能用 Pillow：fpk 里是 DX10 DDS（dxgiFormat=98 BC7_UNORM），Pillow 直开=花屏
     ⇒ `texture2ddecoder.decode_bc7(dds[148:], w, h)`
  ② 不能丢 alpha：图集透明背景占 70~82%，`.convert('RGB')` 会把透明区填成实色，
     表现为"部件对但上下有色块异常延伸" ⇒ 全程 RGBA，直接 im.save(png)
  ③ "组装/取图"不是自己拼像素：同帧附近的 ATLAS 帧是纯文本清单，含每个切片的
     名字 + xy/size 矩形 ⇒ 按矩形 crop 就是正确取图

DX10 头：dxgiFormat = u32@128；像素从 offset 148（128 标准头 + 20 DX10 扩展头）
  98/99=BC7、77/78=BC3、71/72=BC1、28/29=RGBA8、10=R16G16B16A16F、2=R32G32B32A32F

用法：
  python tools/export_fpk_textures.py --pack 001 --out <目录> [--sprites] [--max-frames 40000]
产物：<目录>/frame_00012.png（RGBA）+ <目录>/sprites/<名字>.png + <目录>/_manifest.json
"""
from __future__ import annotations

import argparse
import io
import json
import re
import struct
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心")))
from toolkit_core.fpk_frames import iter_fpk_frames  # noqa: E402
from PIL import Image  # noqa: E402

RES = Path(r"E:\mrzh\res")
BLOCK_RE = re.compile(r"\n([A-Za-z0-9_.]+)\n\s+rotate: \w+\n\s+xy: (\d+), (\d+)\n\s+size: (\d+), (\d+)")


def decode_dds(data: bytes) -> Image.Image | None:
    if data[:4] != b"DDS ":
        return None
    w, h = struct.unpack_from("<II", data, 12)
    if len(data) >= 132 and data[84:88] == b"DX10":
        fmt = struct.unpack_from("<I", data, 128)[0]
        body = data[148:]
        try:
            if fmt in (98, 99):  # BC7
                import texture2ddecoder
                return Image.frombytes("RGBA", (w, h), texture2ddecoder.decode_bc7(body, w, h))
            if fmt in (71, 72):  # BC1
                import texture2ddecoder
                return Image.frombytes("RGBA", (w, h), texture2ddecoder.decode_bc1(body, w, h))
            if fmt in (77, 78):  # BC3
                import texture2ddecoder
                return Image.frombytes("RGBA", (w, h), texture2ddecoder.decode_bc3(body, w, h))
            if fmt in (28, 29):  # RGBA8
                return Image.frombytes("RGBA", (w, h), body[:w * h * 4])
        except Exception:
            pass
    try:  # 兜底：Pillow（DXT1/3/5 等）
        return Image.open(io.BytesIO(data)).convert("RGBA")
    except Exception:
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", default="")
    ap.add_argument("--packs", default="")
    ap.add_argument("--out", required=True)
    ap.add_argument("--sprites", action="store_true")
    ap.add_argument("--max-frames", type=int, default=40000)
    a = ap.parse_args()
    names = [x.strip() for x in (a.packs or a.pack).split(",") if x.strip()]
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    doc = {"schema": "fpk-textures-v1",
           "generated": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
           "packs": []}
    for nm in names:
        pk = RES / f"{nm}.fpk"
        rec = {"pack": pk.name, "exists": pk.exists(), "atlas": 0, "png": 0, "sprites": 0, "errors": []}
        if not pk.exists():
            doc["packs"].append(rec)
            continue
        atlas_txt: str | None = None
        last_atlas_img: Image.Image | None = None
        n = 0
        for frame, data in iter_fpk_frames(pk):
            n += 1
            if n > a.max_frames:
                break
            if frame.output_magic == "ATLAS":
                rec["atlas"] += 1
                atlas_txt = data.decode("latin1", "ignore")
                continue
            if frame.output_magic.startswith("DDS") or data[:4] == b"DDS ":
                im = decode_dds(data)
                if im is None:
                    rec["errors"].append(f"frame {frame.index}: 解码失败")
                    continue
                fn = out / f"frame_{frame.index:05d}_{im.width}x{im.height}.png"
                im.save(fn)          # ← 直接存，保 alpha
                rec["png"] += 1
                if a.sprites and atlas_txt:
                    for name, x, y, w, h in BLOCK_RE.findall(atlas_txt):
                        try:
                            c = im.crop((int(x), int(y), int(x) + int(w), int(y) + int(h)))
                            sp = out / f"sprites_{nm}"
                            sp.mkdir(parents=True, exist_ok=True)
                            c.save(sp / f"{name}.png")
                            rec["sprites"] += 1
                        except Exception as e:  # noqa: BLE001
                            rec["errors"].append(f"sprite {name}: {type(e).__name__}")
                    atlas_txt = None
        rec["frames"] = n
        doc["packs"].append(rec)
        print(json.dumps({k: rec[k] for k in ("pack", "frames", "atlas", "png", "sprites")}, ensure_ascii=False))
        if rec["errors"][:3]:
            print("  错误样例:", rec["errors"][:3])
    (out / "_manifest.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print("→", out / "_manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
