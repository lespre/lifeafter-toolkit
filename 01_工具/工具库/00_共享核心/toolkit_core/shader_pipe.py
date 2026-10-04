# -*- coding: utf-8 -*-
r"""NeoX `.pipe` 编译着色器变体容器（魔数 `cc aa 55 66`，扩展名约 `.ccaa5566`）。

★ 实证来源（2026-09-28）
------------------------------------------------------------------
子代理独立调研 + 助手 400/400 复验，结论一致：

    外层 0x20 字节自定义头
        +0x00  u32   魔数 = cc aa 55 66（★ 4 字节二进制，别写成 8 字节 ASCII "ccaa5566"）
        +0x04  u32   = 2（版本）
        +0x08  u32   = 2（★ 实测 300/300 恒为 2，但不是 blob 个数 —— 见下）
        +0x0C  u32   = 0
        +0x10  16B   零填充
    之后是 1~2 个 blob，每个：
        u64  阶段标志（0=vertex / 1=pixel / 2=compute）
        u64  blob 长度
        blob 字节

    ★★ blob 个数【没有显式字段】—— 靠 blob 链走到文件末尾。实测 300/300 精确到 EOF。
    ★★ 内层 = 标准、未加密的 Microsoft DXBC（chunk 恒为 RDEF/ISGN/OSGN/SHEX/STAT）。
        实测 400 文件 / 800 blob：DXBC 100%，每文件恰好 2 个（vs + ps）。

全库 122,459 个 = `effect_cache.gpk` 97,590 + `gres\0000.gpk` 24,869。

用途：这是这台游戏**全部已编译好的 VS/PS/CS 着色器**，不是贴图、不是压缩包、不是加密数据。
      DXBC 可用微软 `fxc.exe` 原样反汇编，从 RDEF 反射块能读出常量缓冲名、全部 uniform
      变量名+偏移+大小、纹理与采样器槽名+寄存器号。
"""
from __future__ import annotations

import struct
from pathlib import Path

MAGIC = b"\xcc\xaa\x55\x66"
HEADER_SIZE = 0x20
STAGE_NAME = {0: "vertex", 1: "pixel", 2: "compute", 3: "geometry",
              4: "hull", 5: "domain"}
DXBC_CHUNKS = {b"RDEF": "resource_definition", b"ISGN": "input_signature",
               b"OSGN": "output_signature", b"SHEX": "shader_program",
               b"STAT": "statistics", b"DXIL": "dxil_program",
               b"PSG1": "patch_signature", b"RDAT": "runtime_data"}


def is_pipe(blk: bytes) -> bool:
    """按魔数判是不是 NeoX .pipe 容器。"""
    return blk[:4] == MAGIC


def parse_header(b: bytes) -> dict:
    """解析 0x20 字节外层头。★ 不假设 blob 个数。"""
    if not is_pipe(b):
        return {"ok": False, "error": "魔数不匹配（期望 cc aa 55 66）"}
    if len(b) < HEADER_SIZE + 16:
        return {"ok": False, "error": "文件太短（%d B）" % len(b)}
    ver, f8, f12 = struct.unpack_from("<III", b, 4)
    return {
        "ok": True,
        "version": ver,
        "f04": ver, "f08": f8, "f0c": f12,
        "zeros_ok": b[0x10:0x20] == b"\x00" * 16,
        "size": len(b),
    }


def parse_blobs(b: bytes) -> list:
    """按 blob 链解出所有 blob。★ 判据 = 走到文件末尾（精确自洽）。"""
    out = []
    off = HEADER_SIZE
    while off + 16 <= len(b):
        stage, ln = struct.unpack_from("<QQ", b, off)
        off += 16
        if ln <= 0 or off + ln > len(b):
            break
        blob = b[off:off + ln]
        off += ln
        info = {
            "index": len(out) + 1,
            "stage": stage,
            "stage_name": STAGE_NAME.get(stage, "unknown(%d)" % stage),
            "size": ln,
            "is_dxbc": blob[:4] == b"DXBC",
            "offset": off - ln,
        }
        if info["is_dxbc"]:
            info.update(dxbc_info(blob))
        out.append({"meta": info, "blob": blob})
        if off == len(b):
            break
    return out


def dxbc_info(blob: bytes) -> dict:
    """读 DXBC 的 chunk 列表与大小（不解析反射，只给骨架）。"""
    if len(blob) < 32 or blob[:4] != b"DXBC":
        return {}
    total_size, nchunk = struct.unpack_from("<II", blob, 24)
    d = {"dxbc_total_size": total_size, "chunk_count": nchunk, "chunks": []}
    for i in range(min(nchunk, 16)):
        p = 32 + 4 * i
        if p + 4 > len(blob):
            break
        off = struct.unpack_from("<I", blob, p)[0]
        if off + 8 > len(blob):
            continue
        tag = blob[off:off + 4]
        sz = struct.unpack_from("<I", blob, off + 4)[0]
        d["chunks"].append({
            "tag": tag.decode("ascii", "replace"),
            "name": DXBC_CHUNKS.get(tag, "?"),
            "size": sz,
        })
    return d


def parse_file(p) -> dict:
    """解析一个 .ccaa5566 文件。"""
    p = Path(p)
    b = p.read_bytes()
    h = parse_header(b)
    if not h.get("ok"):
        return {"path": str(p), **h}
    blobs = parse_blobs(b)
    return {"path": str(p), "header": h,
            "blobs": [x["meta"] for x in blobs], "raw": blobs,
            "self_consistent": bool(blobs)}


def export(p, out_dir, *, asm: bool = False, fxc: str | None = None) -> list:
    """把 .pipe 拆成 .dxbc（可选 .asm）。返回落盘的文件列表。

    ★ 不复制原始 .ccaa5566 —— 拆出来的 .dxbc 才是可用的东西。
    """
    p = Path(p); out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    r = parse_file(p)
    if not r.get("raw"):
        return []
    written = []
    for x in r["raw"]:
        if not x["meta"]["is_dxbc"]:
            continue
        st = x["meta"]["stage_name"]
        base = "%s_b%d_%s" % (p.stem, x["meta"]["index"], st)
        f = out_dir / (base + ".dxbc")
        f.write_bytes(x["blob"])
        written.append(f)
        if asm and fxc:
            import subprocess
            a = out_dir / (base + ".asm")
            try:
                pr = subprocess.run([fxc, "/nologo", "/dumpbin", str(f)],
                                    capture_output=True, timeout=60)
                if pr.returncode == 0 and pr.stdout:
                    a.write_bytes(pr.stdout)
                    written.append(a)
            except (OSError, subprocess.SubprocessError):
                pass
    return written


def iter_named(restore_root, pattern: str = "*.ccaa5566") -> list:
    """在还原树里找所有 .ccaa5566。"""
    return sorted(Path(restore_root).rglob(pattern))
