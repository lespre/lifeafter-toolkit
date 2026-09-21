# -*- coding: utf-8 -*-
"""`.spr` 兄弟图集解析器（可复用工具）—— 把 `.spr` 声明的图集从容器里取出来。

规则（实测）：
  在 `res\\effect_01.gpk` / `res\\effect_02.gpk` 里，**`.spr` 描述符行 i 的图集 DDS = 行 i-1**。
  证据：`effect_01` 756/756、`effect_02` 192/192 前一行都是 DDS；`.spr` 声明的图集 W×H 与
  该 DDS 的 dims 精确相等（例 512↔512、256↔256）；目视核对（闪电/烟雾/辉光）。
  ⚠ 该规则**只在这两个 effect 容器成立**：gres 族容器里的 `.spr` 前一行不是 DDS（实测 0/835）。

`.spr` 明文格式：
  第 1 行 `<mode>[ <W> <H>]`   第 2 行 `<bpp>`   第 3 行 `<param>`
  其后 N 行 `<name>.tga x0 y0 x1 y1`  ← 该行给出图集的**原始源名**与**逐帧矩形**

用法：
  python spr_atlas_resolver.py --build                      # 建索引（缓存到 --cache）
  python spr_atlas_resolver.py --skin <皮肤目录> [--out <目录>] [--dry-run]
  python spr_atlas_resolver.py --all --root <weapon_skin 根> [--dry-run]

只读容器；只写 --out / --cache 指定的路径。
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import re
import struct
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
from gpk_npk_index import aes_ecb, unpack_entry  # noqa: E402

DEFAULT_CONTAINERS = [r"E:\mrzh\res\effect_01.gpk", r"E:\mrzh\res\effect_02.gpk"]
DEFAULT_CACHE = os.path.join(os.environ.get("TEMP", "."), "spr_atlas_index.json")

FRAME_RE = re.compile(r"^(\S+\.tga)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s*$")


# ─────────────────────────────────────────────────────────── 容器读取
def _iter_rows(path):
    """产出 (row_idx, base, off, comp, dec, flag)；不读载荷。"""
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        outer = aes_ecb(f.read(16))
        _z, masked, two, nb = struct.unpack("<IIII", outer)
        B = 16
        i = 0
        for _k in range(nb):
            f.seek(B)
            bh = aes_ecb(f.read(48))
            n1, bsize = struct.unpack_from("<II", bh, 4)
            cnt = n1 - 1
            f.seek(B + 48)
            tab = aes_ecb(f.read(cnt * 32))
            for j in range(cnt):
                o, cm, de, _c1, _c2, fl, _lo, _hi = struct.unpack_from("<IIIIIIII", tab, j * 32)
                yield i, B, o, cm, de, fl
                i += 1
            if bsize <= 0 or B + bsize > size:
                break
            B += bsize


def build_container_index(path, small_max=8192, verbose=True):
    """便宜扫法：只解 `dec` 小的行，识别 `.spr` 并记录其前一行的 DDS。"""
    entries = []
    with open(path, "rb") as f:
        rows = list(_iter_rows(path))
        for i, base, o, cm, de, fl in rows:
            if de < 8 or de > small_max:
                continue
            f.seek(base + o + 20)
            try:
                pay = unpack_entry(f.read(cm), de, fl)
            except Exception:
                continue
            if pay[:1] not in (b"0", b"1") or b".tga" not in pay[:65536]:
                continue
            rec = parse_spr(pay.decode("latin1"))
            if not rec or not rec["frames"]:
                continue
            entries.append({"container": path, "spr_row": i, "spr_bytes": len(pay),
                            "spr_sha16": hashlib.sha256(pay).hexdigest()[:16], **rec})
    if verbose:
        print("[%s] 行数 %d，识别 .spr %d" % (os.path.basename(path), len(rows), len(entries)))
    return entries


def parse_spr(text):
    lines = [l.strip() for l in text.replace("\r", "\n").split("\n")]
    lines = [l for l in lines if l]
    if not lines:
        return None
    t0 = lines[0].split()
    if not t0 or t0[0] not in ("0", "1"):
        return None
    rec = {"mode": int(t0[0]), "W": None, "H": None, "bpp": None, "param": None}
    if len(t0) >= 3:
        rec["W"], rec["H"] = int(t0[1]), int(t0[2])
    frames = []
    for k, l in enumerate(lines[1:]):
        fm = FRAME_RE.match(l)
        if fm:
            frames.append({"name": fm.group(1),
                           "rect": [int(fm.group(x)) for x in range(2, 6)]})
            continue
        if k == 0 and re.match(r"^\d+$", l):
            rec["bpp"] = int(l)
        elif k == 1 and re.match(r"^\d+$", l):
            rec["param"] = int(l)
    rec["frames"] = frames
    rec["n_frames"] = len(frames)
    rec["names"] = sorted({f["name"] for f in frames})
    if rec["W"] is None and frames:
        rec["W"] = max(f["rect"][2] for f in frames)
        rec["H"] = max(f["rect"][3] for f in frames)
        rec["dims_from_frames"] = True
    return rec


def extract_atlas(container, spr_row, out_png, spr_out=None):
    """取 `.spr` 行 spr_row 的图集（= 行 spr_row-1 的 DDS）并导出 PNG；返回 provenance。"""
    import numpy as np
    from PIL import Image
    from dds_rgba_canonical import decode_bcn_bytes_canonical
    rows = list(_iter_rows(container))
    byrow = {r[0]: r for r in rows}
    with open(container, "rb") as f:
        def load(i):
            _i, base, o, cm, de, fl = byrow[i]
            f.seek(base + o)
            _cm, de2, _c1, _c2, fl2 = struct.unpack("<IIIII", f.read(20))
            f.seek(base + o + 20)
            return unpack_entry(f.read(cm), de2, fl2)
        spr = load(spr_row)
        dds = load(spr_row - 1)
        if dds[:4] != b"DDS ":
            return None
        h, w = struct.unpack_from("<II", dds, 12)
        u8, _p = decode_bcn_bytes_canonical(dds)
        os.makedirs(os.path.dirname(out_png), exist_ok=True)
        Image.fromarray(np.asarray(u8), "RGBA").save(out_png)
        if spr_out and not os.path.exists(spr_out):
            open(spr_out, "wb").write(spr)
        return {"container": container, "spr_row": spr_row, "atlas_row": spr_row - 1,
                "atlas_dims": [w, h], "dds_sha16": hashlib.sha256(dds).hexdigest()[:16],
                "spr_sha16": hashlib.sha256(spr).hexdigest()[:16],
                "png": os.path.basename(out_png),
                "png_sha16": hashlib.sha256(open(out_png, "rb").read()).hexdigest()[:16],
                "dxgi_format": struct.unpack_from("<I", dds, 128)[0] if len(dds) > 132 else None}


# ─────────────────────────────────────────────────────────── 皮肤侧
NAME_RE = re.compile(r"([\w\\\.\-/]+\.(?:spr|tga|dds|png))")


def declared_names(skin_dir):
    out = set()
    for sub in ("sfx",):
        d = os.path.join(skin_dir, sub)
        if os.path.isdir(d):
            for fn in os.listdir(d):
                if fn.endswith(".sfx"):
                    out |= set(NAME_RE.findall(open(os.path.join(d, fn), "rb")
                                               .read().decode("gbk", "replace")))
    for fn in ("effects.json",):
        p = os.path.join(skin_dir, fn)
        if os.path.exists(p):
            out |= set(NAME_RE.findall(open(p, encoding="utf-8").read()))
    return sorted(out)


def stem_of(p):
    return os.path.splitext(os.path.basename(str(p).replace("/", "\\")))[0].lower()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--containers", nargs="*", default=DEFAULT_CONTAINERS)
    ap.add_argument("--cache", default=DEFAULT_CACHE)
    ap.add_argument("--skin")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--root", default=r"E:\la拆包项目\08Lifeafter wiki\assets\3d\weapon_skin")
    ap.add_argument("--out")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.build or not os.path.exists(args.cache):
        idx = []
        for c in args.containers:
            if os.path.exists(c):
                idx += build_container_index(c)
        # 补 atlas 信息（只对识别出的行取一次前一行头 + dims）
        for e in idx:
            pass
        json.dump({"containers": args.containers, "entries": idx}, open(args.cache, "w",
                  encoding="utf-8"), ensure_ascii=False)
        print("索引写出", args.cache, "条目", len(idx))
        if args.build and not (args.skin or args.all):
            return
    data = json.load(open(args.cache, encoding="utf-8"))
    by = {}
    for e in data["entries"]:
        for n in e.get("names", []):
            by.setdefault(stem_of(n), []).append(e)

    skins = []
    if args.skin:
        skins = [args.skin]
    elif args.all:
        skins = sorted(os.path.join(args.root, d) for d in os.listdir(args.root)
                       if os.path.isdir(os.path.join(args.root, d)))
    report = []
    for sk in skins:
        decl = declared_names(sk)
        sprs = [x for x in decl if x.lower().endswith(".spr")]
        hits = []
        for x in sprs:
            for e in by.get(stem_of(x), []):
                hits.append({"declared": x, "spr_row": e["spr_row"], "container": e["container"],
                             "sheet": [e.get("W"), e.get("H")], "n_frames": e["n_frames"],
                             "names": e["names"][:3]})
        rec = {"skin": sk, "declared": len(decl), "spr_declared": len(sprs),
               "resolved": len({h["declared"] for h in hits}), "hits": hits}
        report.append(rec)
        print("%-12s 声明 %3d | .spr %2d | 命中 %2d %s"
              % (os.path.basename(sk.rstrip("\\/")), len(decl), len(sprs),
                 rec["resolved"], [h["declared"].split("\\")[-1] for h in hits][:4]))
        if args.out and hits and not args.dry_run:
            sk_out = os.path.join(args.out, os.path.basename(sk.rstrip("\\/")))
            for h in hits:
                e = [x for x in by[stem_of(h["declared"])] if x["spr_row"] == h["spr_row"]][0]
                png = os.path.join(sk_out, "%s__atlas%d.png" % (stem_of(h["declared"]), h["spr_row"]))
                prov = extract_atlas(h["container"], h["spr_row"], png,
                                     os.path.join(sk_out, stem_of(h["declared"]) + ".spr"))
                h["atlas"] = prov
    if args.out:
        os.makedirs(args.out, exist_ok=True)
        json.dump(report, open(os.path.join(args.out, "spr_atlas_resolver_report.json"), "w",
                  encoding="utf-8"), ensure_ascii=False, indent=1)
        print("报告写出", os.path.join(args.out, "spr_atlas_resolver_report.json"))


if __name__ == "__main__":
    main()
