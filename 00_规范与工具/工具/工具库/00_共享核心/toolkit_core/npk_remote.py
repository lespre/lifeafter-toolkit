# -*- coding: utf-8 -*-
r"""NPK 头/条目表读取：本地文件 或 **HTTP Range 远端**（CDN）。

★ 2026-10-01 头格式实测破解（与社区 neox_tools 对照后确认）：
```
头部 48 B → AES-ECB 解密 → [8:12]='NXPK' · [12:16]=version
                            [16:20]=table_offset · [20:24]=entry_count · [24:48]=其余 u32
条目表 = 文件 [table_offset : table_offset + count*48]，整块 AES-ECB 解密
条目 48 B：fid(u64) off(u32) packed(u32) decoded(u32) zcrc(u32) crc(u32)
           zipflag(u16) fileflag(u16) reserved(16)
★ NXFN 判据： slack = size - (table_offset + count*48)
   slack == 0 ⇒ 无 NXFN（实测 60/60 容器 + CDN 包全 0）
★ 远端只要 48 B 头 + count*48 B 条目表（几十 KB），**不用下整包**。
"""
from __future__ import annotations

import importlib.util
import json
import os
import struct
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional

HEADER_SIZE = 48
ENTRY_SIZE = 48
_CACHE: Dict[str, object] = {}


def _core():
    """项目里的 la_unpack_core（拿 AES 解密）。"""
    if "core" in _CACHE:
        return _CACHE["core"]
    p = (Path(__file__).resolve().parents[2] / "01_解码定位复原" / "解包与扫描"
         / "la_unpack_core.py")
    m = None
    if p.is_file():
        name = "_la_unpack_core_for_npk_remote"
        if name in sys.modules:
            m = sys.modules[name]
        else:
            spec = importlib.util.spec_from_file_location(name, p)
            m = importlib.util.module_from_spec(spec)
            sys.modules[name] = m
            spec.loader.exec_module(m)
    _CACHE["core"] = m
    return m


def _decrypt(b: bytes) -> bytes:
    c = _core()
    if c is not None:
        try:
            return c.aes_ecb_decrypt(b)
        except Exception:                                            # noqa: BLE001
            return b
    return b


def _fetch_range(url: str, start: int, end: int, timeout: int = 60) -> bytes:
    op = urllib.request.build_opener(urllib.request.ProxyHandler({
        "http": os.environ.get("http_proxy", "http://127.0.0.1:10808"),
        "https": os.environ.get("https_proxy", "http://127.0.0.1:10808"),
    }))
    req = urllib.request.Request(url, headers={"Range": "bytes=%d-%d" % (start, end)})
    with op.open(req, timeout=timeout) as r:
        data = r.read()
    return data


def _content_length(url: str, timeout: int = 60) -> Optional[int]:
    op = urllib.request.build_opener(urllib.request.ProxyHandler({
        "http": os.environ.get("http_proxy", "http://127.0.0.1:10808"),
        "https": os.environ.get("https_proxy", "http://127.0.0.1:10808"),
    }))
    req = urllib.request.Request(url, method="HEAD")
    try:
        with op.open(req, timeout=timeout) as r:
            cl = r.headers.get("Content-Length")
            return int(cl) if cl else None
    except Exception:                                                # noqa: BLE001
        return None


def read_header(target) -> dict:
    """本地路径或 URL → 头信息 dict（含 slack / nxfn_suspected）。"""
    t = str(target)
    out: Dict[str, object] = {"target": t, "remote": t.lower().startswith(("http://", "https://"))}
    if out["remote"]:
        size = _content_length(t)
        raw = _fetch_range(t, 0, HEADER_SIZE - 1)
        out["size"] = size
    else:
        p = Path(t)
        if not p.is_file():
            return {"target": t, "error": "文件不存在"}
        size = p.stat().st_size
        with p.open("rb") as fh:
            raw = fh.read(HEADER_SIZE)
        out["size"] = size
    h = _decrypt(raw)
    out["magic_ok"] = len(h) >= 24 and h[8:12] == b"NXPK"
    if not out["magic_ok"]:
        out["head_hex"] = h[:24].hex()
        return out
    out["version"] = struct.unpack_from("<i", h, 12)[0]
    toff = struct.unpack_from("<I", h, 16)[0]
    cnt = struct.unpack_from("<I", h, 20)[0]
    out["table_offset"] = toff
    out["entry_count"] = cnt
    out["tail_u32"] = list(struct.unpack_from("<IIIIII", h, 24)) if len(h) >= 48 else []
    if size:
        table_end = toff + cnt * ENTRY_SIZE
        out["table_end"] = table_end
        out["slack"] = int(size - table_end)
        out["nxfn_suspected"] = out["slack"] > 0
    return out


def read_entries(target, limit: Optional[int] = None) -> List[dict]:
    """条目表 → 条目列表（fid/off/packed/decoded/flags/reserved）。"""
    info = read_header(target)
    if not info.get("magic_ok"):
        return []
    toff, cnt = info["table_offset"], info["entry_count"]
    n = min(cnt, limit) if limit else cnt
    t = str(target)
    if info["remote"]:
        raw = _fetch_range(t, toff, toff + n * ENTRY_SIZE - 1)
    else:
        with Path(t).open("rb") as fh:
            fh.seek(toff)
            raw = fh.read(n * ENTRY_SIZE)
    tbl = _decrypt(raw)
    out = []
    for i in range(min(n, len(tbl) // ENTRY_SIZE)):
        b = i * ENTRY_SIZE
        fid, off, packed, decoded = struct.unpack_from("<QIII", tbl, b)
        zcrc, crc = struct.unpack_from("<II", tbl, b + 20)
        zf, ff = struct.unpack_from("<HH", tbl, b + 28)
        out.append({"index": i, "fid": "%016X" % fid, "offset": off, "packed": packed,
                    "decoded": decoded, "zcrc": zcrc, "crc": crc,
                    "zip_flag": zf, "file_flag": ff,
                    "reserved": tbl[b + 32:b + 48].hex()})
    return out


if __name__ == "__main__":
    for t in sys.argv[1:]:
        info = read_header(t)
        print(json.dumps(info, ensure_ascii=False, indent=1))
        for e in read_entries(t, 5):
            print("   ", e)
