# -*- coding: utf-8 -*-
"""扫全部 fpk 找「光影咏叹调」的资源（后台多进程，不受子代理迭代上限影响）。

关键词只用**高专指**的：`skin_1003_010`（模型/贴图 stem）、`yongtandiao`（咏叹调拼音尾部）。
**不用** `guangying` —— 实测它命中的是通用配置里的光影片段键（如
`"shuye_1ci":{"slots":{"guangying":{"color":...`），会淹掉真命中。

命中帧的处理：附近 3 帧内的 DDS 用正确管线导 RGBA PNG（BC7→texture2ddecoder，
禁 convert('RGB')）；FSB5 帧转 WAV。

用法：python tools/scan_fpk_sky1003.py [--packs 001,002] [--max-frames 60000] [--workers 6]
产物：03拆包产物/sky1003/{hits.json, hitctx/*.txt, tex/*.png, wav/*.wav}
"""
from __future__ import annotations

import argparse
import io
import json
import re
import struct
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLKIT = r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心"
sys.path.insert(0, TOOLKIT)
RES = Path(r"E:\mrzh\res")
OUT = Path(r"E:\la拆包项目\03拆包产物\sky1003b")
PATS = [b"skin_1003_0", b"skin_1003_01", b"1110171", b"yongtandiao"]


def _decode(dds: bytes):
    from PIL import Image
    if dds[:4] != b"DDS ":
        return None
    w, h = struct.unpack_from("<II", dds, 12)
    if len(dds) >= 132 and dds[84:88] == b"DX10":
        fmt = struct.unpack_from("<I", dds, 128)[0]
        body = dds[148:]
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
        return Image.open(io.BytesIO(dds)).convert("RGBA")
    except Exception:
        return None


def scan_pack(pack_name: str, max_frames: int) -> dict:
    sys.path.insert(0, TOOLKIT)
    from toolkit_core.fpk_frames import iter_fpk_frames
    PK = RES / f"{pack_name}.fpk"
    rec = {"pack": pack_name, "exists": PK.exists(), "frames": 0, "hits": [], "png": 0, "wav": 0, "seconds": 0}
    if not PK.exists():
        return rec
    t0 = time.time()
    recent: list[tuple[int, bytes]] = []
    atlas_txt = None
    for frame, data in iter_fpk_frames(PK):
        rec["frames"] += 1
        if rec["frames"] > max_frames:
            break
        mag = frame.output_magic
        if mag == "ATLAS":
            atlas_txt = data.decode("latin1", "ignore")
            continue
        for pat in PATS:
            j = data.find(pat)
            if j >= 0:
                ctx = data[max(0, j - 300):j + 500].decode("latin1", "replace")
                rec["hits"].append({"frame": frame.index, "magic": mag, "pat": pat.decode(),
                                    "len": len(data), "ctx": ctx})
                break
        if mag.startswith("DDS") or data[:4] == b"DDS ":
            recent.append((frame.index, data))
            if len(recent) > 3:
                recent.pop(0)
        elif data[:4] == b"FSB5":
            try:
                sys.path.insert(0, r"E:\la拆包项目\01拆包器本体\工具库\01_核心解包器")
                import lifeafter_unpacker_full as m
                wd = OUT / "wav"
                wd.mkdir(parents=True, exist_ok=True)
                bf = wd / f"{pack_name}_{frame.index}.fsb"
                bf.write_bytes(data)
                m.extract_fsb(str(bf), str(wd))
                rec["wav"] += 1
            except Exception:
                pass
    # 命中后：把最近几帧 DDS 导成 RGBA PNG
    if rec["hits"]:
        td = OUT / "tex"
        td.mkdir(parents=True, exist_ok=True)
        for fidx, dds in recent:
            im = _decode(dds)
            if im is None:
                continue
            im.save(td / f"{pack_name}_{fidx:06d}.png")   # 保 alpha
            rec["png"] += 1
        (OUT / "hitctx").mkdir(parents=True, exist_ok=True)
        (OUT / "hitctx" / f"{pack_name}.txt").write_text(
            "\n\n=====\n\n".join(h["ctx"] for h in rec["hits"]), encoding="utf-8")
    rec["seconds"] = round(time.time() - t0, 1)
    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--packs", default="")
    ap.add_argument("--max-frames", type=int, default=60000)
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    if a.packs:
        packs = [x.strip() for x in a.packs.split(",") if x.strip()]
    else:
        packs = [f"{i:03d}" for i in range(1, 65)]
    OUT.mkdir(parents=True, exist_ok=True)
    doc = {"schema": "sky1003-fpk-scan-v1",
           "generated": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
           "pats": [p.decode() for p in PATS], "packs": []}
    done = 0
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(scan_pack, p, a.max_frames): p for p in packs}
        for fut in as_completed(futs):
            rec = fut.result()
            doc["packs"].append(rec)
            done += 1
            mark = f"★命中 {len(rec['hits'])}" if rec["hits"] else ""
            print(f"[{done}/{len(packs)}] {rec['pack']}: 帧 {rec['frames']} / {rec['seconds']}s / png {rec['png']} {mark}",
                  flush=True)
            if rec["hits"]:
                for h in rec["hits"][:3]:
                    print("      hit:", h["pat"], "frame", h["frame"], "|", h["ctx"][:200].replace("\n", " "), flush=True)
            (OUT / "hits.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    tot = sum(len(p["hits"]) for p in doc["packs"])
    print(f"完成：{len(doc['packs'])} 包 / 命中帧 {tot} / 产物 {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
