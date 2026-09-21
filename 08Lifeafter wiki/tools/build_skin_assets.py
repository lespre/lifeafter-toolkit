# -*- coding: utf-8 -*-
"""给**一个武器皮肤**构建完整素材（音效 + 图片）—— 单包作业，不搞全盘扫描。

选定目标：水金玫瑰（内部名 suijinmeigui/shuijinmeigui，音效已在 0045.gpk 拆到 12 个 WAV 并验证正确）
思路：音频和贴图往往在**同一个 gres 包**里（0045 的 bank 已证实），所以只解这一个包：
  1. extract_gpk 解包 → 2. DDS 按 BC7/DX10 正确解码(保 RGBA) → 3. 拼联系表 → 4. 写清单
用法：python tools/build_skin_assets.py --pack 0045 --out <目录>
"""
from __future__ import annotations

import argparse
import io
import json
import math
import shutil
import struct
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(r"E:\la拆包项目\01拆包器本体\工具库\01_核心解包器")))
import lifeafter_unpacker_full as m  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

GRES = Path(r"E:\mrzh\Documents\gres")


def decode_any(data: bytes) -> Image.Image | None:
    if data[:4] == b"DDS ":
        w, h = struct.unpack_from("<II", data, 12)
        if len(data) >= 132 and data[84:88] == b"DX10":
            fmt = struct.unpack_from("<I", data, 128)[0]
            body = data[148:]
            try:
                import texture2ddecoder
                if fmt in (98, 99):
                    return Image.frombytes("RGBA", (w, h), texture2ddecoder.decode_bc7(body, w, h))
                if fmt in (71, 72):
                    return Image.frombytes("RGBA", (w, h), texture2ddecoder.decode_bc1(body, w, h))
                if fmt in (77, 78):
                    return Image.frombytes("RGBA", (w, h), texture2ddecoder.decode_bc3(body, w, h))
                if fmt in (28, 29):
                    return Image.frombytes("RGBA", (w, h), body[:w * h * 4])
            except Exception:
                pass
    try:
        return Image.open(io.BytesIO(data)).convert("RGBA")
    except Exception:
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", default="0045")
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-thumb", type=int, default=220)
    a = ap.parse_args()
    out = Path(a.out)
    tex = out / "tex"
    tex.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix=f"skin_{a.pack}_"))
    t0 = time.time()
    m.extract_gpk(str(GRES / f"{a.pack}.gpk"), str(tmp))
    made = []
    for f in sorted(tmp.rglob("*")):
        if not f.is_file():
            continue
        data = f.read_bytes()
        im = decode_any(data)
        if im is None or im.width < 8 or im.height < 8:
            continue
        fn = tex / f"{f.stem}_{im.width}x{im.height}.png"
        im.save(fn)                     # ← 保 alpha
        made.append({"file": str(fn), "w": im.width, "h": im.height, "bytes": len(data)})
    shutil.rmtree(tmp, ignore_errors=True)
    # 联系表（棋盘底，透明可见）
    COLS, TH, PAD = 8, a.max_thumb, 12
    rows = max(1, math.ceil(len(made) / COLS))
    W, H = COLS * (TH + PAD) + PAD, rows * (TH + PAD + 18) + PAD
    sheet = Image.new("RGB", (W, H), (36, 36, 42))
    dr = ImageDraw.Draw(sheet)
    for yy in range(0, H, 16):
        for xx in range(0, W, 16):
            if (xx // 16 + yy // 16) % 2 == 0:
                dr.rectangle([xx, yy, xx + 15, yy + 15], fill=(64, 64, 70))
    for i, rec in enumerate(made):
        r, c = divmod(i, COLS)
        x, y = PAD + c * (TH + PAD), PAD + r * (TH + PAD + 18)
        try:
            im = Image.open(rec["file"]).convert("RGBA")
            im.thumbnail((TH, TH))
            sheet.paste(im, (x + (TH - im.width) // 2, y + (TH - im.height) // 2), im)
            dr.text((x + 2, y + TH + 2), f'{i}: {rec["w"]}x{rec["h"]}', fill=(225, 225, 225))
        except Exception:
            pass
    sp = out / "_contact_sheet.png"
    sheet.save(sp)
    doc = {"schema": "skin-assets-v1",
           "generated": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
           "pack": a.pack, "images": len(made), "rows": made,
           "contact_sheet": str(sp), "seconds": round(time.time() - t0, 1)}
    (out / "_manifest.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"pack": a.pack, "images": len(made), "seconds": doc["seconds"],
                      "sheet": str(sp)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
