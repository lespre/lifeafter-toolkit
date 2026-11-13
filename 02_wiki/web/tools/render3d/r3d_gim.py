# -*- coding: utf-8 -*-
"""r3d_gim.py — NeoX / c159 描述符（.gim / .c159）解析器

★ 定位：.gim 与 .c159 同格式（magic c1 59 41 0d），是明日之后 NeoX 引擎的
  「对象/场景描述符」——字段名表 + 带 tag 的值流。绝大多数 .gim 是
  装配图（骨骼名、包围盒、LOD 引用、材质索引 MtlIdx、挂点 Socket→引用其他 .gim），
  几何体通常在同级 .mesh（已受 support）；少数大文件会内嵌顶点缓冲。
★ 本解析器职责（只读，不写盘）：
  ① 校验 magic / 声明长度；
  ② 抽取字段名表（兼容长度前缀与 NUL 终止两种写法）；
  ③ 走值流，按既定 tag 解 str / vec3[] / name / bool；
  ④ 扫描引用串（含 \\ 的反斜杠路径 / 以 .gim/.mesh/.mtg/.c159/.gis 结尾）——装配图核心；
  ⑤ 保守探测内嵌几何候选（数据中大块 u32 长度且为 12/32 的倍数）。
★ 纪律同 r3d_core：路径经 la_paths 派生，fail-closed，绝不伪造。
★ 用途：让流水线从「见 .gim 即 unresolved」升级为「解析装配图、正确引用同级 .mesh」。

用法：
  python r3d_gim.py <file.gim>            # 打印摘要
  python r3d_gim.py <file.gim> --json out.json
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import struct
import sys

MAGIC = bytes([0xC1, 0x59, 0x41, 0x0D])
IDSET = set(b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_")

# 引用串：反斜杠路径或已知扩展名结尾（装配图里指向子件 / LOD / 材质）
_REF = re.compile(rb'[A-Za-z0-9_ ./\\-]{3,200}?\.(?:gim|mesh|mtg|c159|gis|GIM|MESH|MTG|C159|GIS)')

# ── 名表定位 ───────────────────────────────────────────────────────────────
def find_data_off(d: bytes) -> int:
    """字段名表结束处（值流起点）。名表是连续的 NUL 终止 ASCII 串；
    可能以 0~2 字节前缀开头，先跳过非标识符字节，再读名直到出现二进制。"""
    i = 12
    # 跳过开头前缀（非标识符、非 NUL）
    while i < len(d) and d[i] not in IDSET and d[i] != 0:
        i += 1
    while i < len(d):
        b = d[i]
        if b == 0:
            i += 1
            continue
        if b in IDSET:
            j = i
            while j < len(d) and d[j] != 0:
                j += 1
            i = j + 1
            # 名后是 NUL 再接非标识符字节 ⇒ 二进制值流起点
            if i < len(d) and d[i] not in IDSET and d[i] != 0:
                return i
            continue
        return i  # 二进制起点（无前缀情况）
    return 12


# ── 值流遍历 ───────────────────────────────────────────────────────────────
def walk_values(d: bytes, off: int):
    """返回 (values, blobs)。values 为 (type, value)；blobs 为 (offset, tag, length)。"""
    values: list = []
    blobs: list = []
    i = off
    n = len(d)
    while i < n:
        t = d[i]
        # tag 0x03 -> 子tag(=01) + ASCII 串
        if t == 0x03 and i + 2 < n:
            j = d.find(b"\x00", i + 2)
            if j > i:
                s = d[i + 2:j]
                if all(32 <= c < 127 for c in s):
                    values.append(("str", s.decode("latin1")))
                    i = j + 1
                    continue
            i += 1
            continue
        # tag 0x06 -> u8 计数 + 0x03 + 每项(u32 0 + float32×3)  => vec3[]
        if t == 0x06 and i + 3 < n:
            cnt = d[i + 1]
            if 0 < cnt <= 4096 and d[i + 2] == 0x03:
                p = i + 3
                vs = []
                ok = True
                for _ in range(cnt):
                    if p + 16 > n:
                        ok = False
                        break
                    if struct.unpack_from("<I", d, p)[0] != 0:
                        ok = False
                        break
                    vs.append(struct.unpack_from("<fff", d, p + 4))
                    p += 16
                if ok and vs:
                    values.append(("vec3[]", [(round(x, 5) for x in v) for v in vs]))
                    i = p
                    continue
            i += 1
            continue
        # tag 0x07 -> 子tag(=01) + ASCII 名（子网格名等）
        if t == 0x07 and i + 2 < n:
            j = d.find(b"\x00", i + 2)
            if j > i:
                s = d[i + 2:j]
                if all(32 <= c < 127 for c in s):
                    values.append(("name", s.decode("latin1")))
                    i = j + 1
                    continue
            i += 1
            continue
        # tag 0x08 -> 子tag(=01) + true/false
        if t == 0x08 and i + 2 < n:
            j = d.find(b"\x00", i + 2)
            if j > i:
                s = d[i + 2:j]
                if s in (b"true", b"false"):
                    values.append(("bool", s.decode()))
                    i = j + 1
                    continue
            i += 1
            continue
        # 未知 tag：试探是否为「tag + u32 长度 + 裸缓冲」（几何候选）
        # ★ 仅当长度足够大（>=1024，排除 256B 等小结构误判）且为 vec3(12B)/顶点(32B) 步长倍数
        if t not in (0x01, 0x02, 0x04, 0x05) and i + 5 < n:
            L = struct.unpack_from("<I", d, i + 1)[0]
            if 1024 < L < (n - i) and L < 80_000_000 and (L % 12 == 0 or L % 32 == 0):
                blobs.append((i, t, L))
                i += 1 + L
                continue
        i += 1
    return values, blobs


# ── 引用扫描（装配图核心）─────────────────────────────────────────────────
def scan_references(d: bytes) -> list[str]:
    out = []
    seen = set()
    for m in _REF.finditer(d):
        s = m.group(0).decode("latin1").strip()
        if s and s not in seen:
            seen.add(s)
            out.append(s)
    return out


def normalize_ref(ref: str) -> str:
    """引用串 → character 下相对 posix 路径。剥离前导 character/ 与反斜杠。"""
    s = ref.replace("\\", "/").strip()
    if s.lower().startswith("character/"):
        s = s[len("character/"):]
    return s


def parse(path: pathlib.Path) -> dict:
    d = path.read_bytes()
    info = {
        "file": path.name, "size": len(d), "magic_ok": d[:4] == MAGIC,
        "declared_size": None, "names": [], "values": [], "blobs": [],
        "references": [], "note": "",
    }
    if not info["magic_ok"]:
        info["note"] = "magic 不是 c1 59 41 0d"
        return info
    if len(d) >= 8:
        info["declared_size"] = struct.unpack_from("<I", d, 4)[0]
    off = find_data_off(d)
    # 名表 = data_off 之前的 NUL 终止串
    head = d[12:off]
    names = [m.group(0).decode("latin1") for m in re.finditer(rb"[A-Za-z_][A-Za-z0-9_]{1,60}", head)]
    info["names"] = names
    values, blobs = walk_values(d, off)
    info["values"] = [{"type": t, "value": v} for t, v in values]
    info["blobs"] = [{"offset": o, "tag": t, "length": L} for o, t, L in blobs]
    info["references"] = scan_references(d)
    # 判定：是否含装配引用 / 内嵌几何
    has_ref = bool(info["references"])
    has_blob = bool(blobs)
    if has_blob:
        info["note"] = "含内嵌几何候选（裸缓冲）"
    elif has_ref:
        info["note"] = "场景/装配描述符（几何体在引用目标，如同级 .mesh）"
    else:
        info["note"] = "描述符（未见引用串/几何候选，可能简化节点）"
    return info


def main() -> int:
    ap = argparse.ArgumentParser(description="NeoX/c159 描述符解析器")
    ap.add_argument("file")
    ap.add_argument("--json")
    a = ap.parse_args()
    p = pathlib.Path(a.file)
    info = parse(p)
    print("文件 %s  %d B  magic=%s  声明长度=%s" % (
        p.name, info["size"], info["magic_ok"], info["declared_size"]))
    print("字段名 %d 个: %s" % (len(info["names"]), info["names"][:40]))
    print("值 %d 个（首 12）:" % len(info["values"]))
    for v in info["values"][:12]:
        val = v["value"]
        if isinstance(val, list):
            val = "vec3×%d 首=%s" % (len(val), val[0] if val else None)
        print("   %-7s %s" % (v["type"], val))
    print("内嵌几何候选 %d 个:" % len(info["blobs"]))
    for b in info["blobs"][:8]:
        print("   @%d tag=0x%02x len=%d" % (b["offset"], b["tag"], b["length"]))
    print("引用串 %d 个（装配图，首 12）:" % len(info["references"]))
    for r in info["references"][:12]:
        print("   %s" % r)
    print("判定: %s" % info["note"])
    if a.json:
        o = pathlib.Path(a.json)
        o.parent.mkdir(parents=True, exist_ok=True)
        o.write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
        print("→", o)
    return 0


if __name__ == "__main__":
    sys.exit(main())
