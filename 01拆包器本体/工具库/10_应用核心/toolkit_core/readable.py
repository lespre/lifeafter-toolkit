# -*- coding: utf-8 -*-
"""解包后自动转可读：图像（DDS/TGA/KTX）→ PNG；bin/二进制 → 字符串表。

纪律：原文件永不改动；产物只写目标目录下的 ``_readable/`` 镜像子树；
解码失败只记录并跳过（fail-soft），不伪造内容。
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable

IMAGE_EXTS = {".dds", ".tga", ".ktx"}
BIN_EXTS = {".bin", ".dat", ".bytes"}


def _strings(data: bytes, min_len: int = 4, cap: int = 20000) -> list[str]:
    import re
    out: list[str] = []
    seen: set[str] = set()
    pattern = r"[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef0-9A-Za-z_ \.\,\;\:\!\?\(\)\[\]\{\}<>/\\|\-\+\=\*&%\$#@~]{4,}"
    for enc in ("utf-8", "gbk", "utf-16-le"):
        try:
            text = data.decode(enc, errors="ignore")
        except Exception:
            continue
        for m in re.findall(pattern, text):
            m = m.strip()
            if len(m) < min_len:
                continue
            if not any("\u4e00" <= c <= "\u9fff" for c in m) and len(m) < 6:
                continue
            if m in seen:
                continue
            seen.add(m)
            out.append(f"[{enc}] {m}")
            if len(out) >= cap:
                return out
    return out


def _decode_image_dds(src: Path):
    try:
        from toolkit_core.resource_resolver import decode_bcn_dds
        im = decode_bcn_dds(src.read_bytes())
        if im is not None:
            return im
    except Exception:
        pass
    try:
        from PIL import Image
        im = Image.open(src)
        im.load()
        return im
    except Exception:
        return None


def _astcenc(toolkit_root: Path | None) -> Path | None:
    cands: list[Path] = []
    if toolkit_root is not None:
        cands.append(Path(toolkit_root) / "07_纹理转换" / "astcenc-avx2.exe")
    try:
        cands.append(Path(sys.executable).resolve().parent / "工具库" / "07_纹理转换" / "astcenc-avx2.exe")
    except Exception:
        pass
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        cands.append(Path(meipass) / "07_纹理转换" / "astcenc-avx2.exe")
    for c in cands:
        if c.is_file():
            return c
    return None


def _convert_image(src: Path, dst: Path, toolkit_root: Path | None) -> bool:
    ext = src.suffix.lower()
    if ext == ".ktx":
        tool = _astcenc(toolkit_root)
        if tool is None:
            return False
        import subprocess
        try:
            r = subprocess.run([str(tool), "-dl", str(src), str(dst)], capture_output=True, timeout=180)
        except Exception:
            return False
        return r.returncode == 0 and dst.exists() and dst.stat().st_size > 0
    im = None
    if ext == ".dds":
        im = _decode_image_dds(src)
    elif ext == ".tga":
        try:
            from PIL import Image
            im = Image.open(src)
            im.load()
        except Exception:
            im = None
    if im is None:
        return False
    try:
        if im.mode not in ("RGB", "RGBA"):
            im = im.convert("RGBA")
        dst.parent.mkdir(parents=True, exist_ok=True)
        im.save(dst, "PNG")
        return True
    except Exception:
        return False


def make_readable(root: Path | str, toolkit_root: Path | None, log: Callable[[str], None]) -> dict:
    """把 root 下的解包产物镜像转换成可读副本；返回计数（png/strings/skipped/errors）。"""
    root = Path(root)
    out_root = root / "_readable"
    counts = {"png": 0, "strings": 0, "skipped": 0, "errors": 0}
    files = [p for p in root.rglob("*")
             if p.is_file() and "_readable" not in p.parts and p.name != "line.json"]
    for i, src in enumerate(files, 1):
        rel = src.relative_to(root)
        ext = src.suffix.lower()
        dst = out_root / rel
        try:
            if ext in IMAGE_EXTS:
                dst = dst.with_suffix(".png")
                if _convert_image(src, dst, toolkit_root):
                    counts["png"] += 1
                else:
                    counts["skipped"] += 1
                    log(f"  ⤷ 跳过（无法解码）：{rel}")
            elif ext in BIN_EXTS or ext == "":
                text = _strings(src.read_bytes()[:20_000_000])
                if text:
                    dst = dst.with_suffix(".strings.txt")
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    dst.write_text("\n".join(text) + "\n", encoding="utf-8")
                    counts["strings"] += 1
                else:
                    counts["skipped"] += 1
            else:
                counts["skipped"] += 1
        except Exception as exc:
            counts["errors"] += 1
            log(f"  ⤷ 失败：{rel}（{exc}）")
        if i % 200 == 0 and i:
            log(f"  …可读化进度 {i}/{len(files)}")
    return counts
