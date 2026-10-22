# -*- coding: utf-8 -*-
r"""带 H · CDN 包清单（pkg_N.pi）：官方分发的 fid 清单 + fid 级 diff。

## 这是什么

官方 CDN 上，每个版本目录下除了包本体，还有一组**清单文件**：

    pkg_lst.pl      59 B   = 17 个包的顺序，形如 [2, 15, 13, 14, 16, 17, 1, ...]
    pkg_1.pi ...
    pkg_17.pi              = 每个包的文件清单

`pkg_N.pi` 的格式（实测逆向，机械可核）：

    [0:4]   uint32  条目数 n
    [4:8]   uint32  保留（= 0）
    [8:]    n × 8 B 64 位文件哈希 —— 与本项目索引的 fid 同一空间

    自检：441,979 × 8 + 8 = 3,535,840 = 文件大小（完全整除）
          条目 100% 唯一；熵 8.00/8.00 ⇒ 不是加密，是哈希表本来的高熵

## CDN 目录名怎么来

清单里**没有**直接给目录名，但 `pkg_lst` / `pkg_N.pi` 字段的 `name` 里带着：

    "pkg_lst": {"name": "20260917_015403_release_newpc/pkg_lst.pl", ...}
                                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ 就是目录名

    规律 = <时间戳>_<cloud_dir_name>

## 这条路的用途

    · H-1 升级：从「包哈希变了」升级到「fid 级新增/移除清单」
    · H-3：官方直接给「哪个 fid 属于哪个官方包」→ 不用再用前缀猜
    · 完整性：官方清单 vs 本地索引 → 能算「本地缺了什么」
    · 成本：17 × ~3.5 MB ≈ 18 MB/版本，而大包动辄 42 GB

★ 只读服务端（CDN），不碰任何本地客户端文件。
"""
from __future__ import annotations

import json
import struct
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Iterable

from .patch_delta import ENTRIES

BASE_CDN = "https://g66.gph.netease.com"
PKG_LST = "pkg_lst.pl"
PKG_MAX = 17
_UA = {"User-Agent": "lifeafter-toolkit/1.0"}


def _get(url: str, *, timeout: float = 60.0) -> bytes:
    req = urllib.request.Request(url, headers=_UA)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def cdn_dir_of(doc: dict) -> str | None:
    """从版本清单里取 CDN 目录名。

    不硬编码字段名：扫所有值，找形如 `<目录>/pkg_lst.pl` 或 `<目录>/pkg_N.pi` 的 name。
    """
    for v in doc.values():
        if isinstance(v, dict):
            nm = v.get("name")
            if isinstance(nm, str) and ("/pkg_lst.pl" in nm or "/pkg_" in nm and ".pi" in nm):
                return nm.split("/", 1)[0]
    return None


def fetch_pkg_lst(cdn_dir: str, *, timeout: float = 30.0) -> list[int]:
    """取包顺序表。"""
    raw = _get("%s/%s/%s" % (BASE_CDN, cdn_dir, PKG_LST), timeout=timeout)
    return json.loads(raw.decode("utf-8"))


def parse_pi(path: Path | str) -> list[int]:
    """解析一个 pkg_N.pi → 64 位哈希列表。"""
    b = Path(path).read_bytes()
    if len(b) < 8:
        return []
    n = struct.unpack_from("<I", b, 0)[0]
    body = b[8:8 + n * 8]
    if len(body) < n * 8:
        raise ValueError("%s: 声明 %d 条，实际只有 %d 条（文件被截断？）"
                         % (Path(path).name, n, len(body) // 8))
    return list(struct.unpack("<%dQ" % n, body))


def fetch(entry: str = "release", out_dir: Path | str | None = None, *,
          manifest: dict | None = None, timeout: float = 120.0,
          only: Iterable[int] | None = None, quiet: bool = False) -> dict:
    """下载一个入口的全部 pkg_N.pi（默认 1..17）。

    manifest: 已有的版本清单（省一次网络往返）；不给就现拉。
    """
    if entry not in ENTRIES:
        raise KeyError("未知入口 %r；可用：%s" % (entry, sorted(ENTRIES)))
    if manifest is None:
        from .patch_delta import fetch as _fetch_manifest
        manifest = _fetch_manifest(entry, timeout=30.0)

    cdn_dir = cdn_dir_of(manifest)
    if not cdn_dir:
        raise RuntimeError("清单里找不到 CDN 目录名（pkg_lst/pkg_N.pi 的 name 字段）")

    out = Path(out_dir) if out_dir else None
    if out:
        out.mkdir(parents=True, exist_ok=True)

    want = list(only) if only else list(range(1, PKG_MAX + 1))
    per: dict[str, int] = {}
    got: list[str] = []
    for n in want:
        name = "pkg_%d.pi" % n
        url = "%s/%s/%s" % (BASE_CDN, cdn_dir, name)
        try:
            raw = _get(url, timeout=timeout)
        except (urllib.error.URLError, OSError) as exc:
            per[name] = -1
            if not quiet:
                print("  ✗ %-12s %s" % (name, str(exc)[:60]))
            continue
        if out:
            (out / name).write_bytes(raw)
        per[name] = (len(raw) - 8) // 8 if len(raw) >= 8 else 0
        got.append(name)
        if not quiet:
            print("  ✓ %-12s %10d B  %8d 条" % (name, len(raw), per[name]))

    return {"entry": entry, "version": manifest.get("version"), "cdn_dir": cdn_dir,
            "cloud_dir_name": manifest.get("cloud_dir_name"),
            "per_pkg": per, "downloaded": got, "out_dir": str(out) if out else None}


def load_dir(d: Path | str) -> dict[str, set[int]]:
    """读一个目录下全部 pkg_N.pi → {pkg 名: 哈希集合}。"""
    out: dict[str, set[int]] = {}
    for p in sorted(Path(d).glob("pkg_*.pi")):
        if p.name == PKG_LST:
            continue
        try:
            vs = parse_pi(p)
        except ValueError as exc:
            print("  ✗ %s" % exc)
            continue
        if vs:
            out[p.stem] = set(vs)
    return out


def all_fids(d: Path | str) -> set[int]:
    """一个目录下全部 pkg_N.pi 的哈希并集。"""
    s: set[int] = set()
    for vs in load_dir(d).values():
        s |= vs
    return s


# ══════════════════════════════════════════════════════════════════════════
# H-3 包级归因（★ 2026-09-28 起用官方清单换掉「前缀猜包」）
#
# 旧做法：把服务端包名（如 res/character/players2021.layers.*.npk）按前缀匹配到
#         本地容器（character_05.gpk …），175/210 命中，但那是【猜】的，
#         而且一个前缀对多个容器，粒度粗。
#
# 新做法：官方 pkg_N.pi 直接给出「哪些 fid 属于哪个官方包」。
#         · pkg_N.pi 是【有序布局表】（按容器分段、段内行号递增）
#         · 所以既能反查「某 fid 属于哪个包」，也能给出「包内第几条」
#         实测：幻夜神谕立绘 7273DC844F76A954 → pkg_2 第 1144921 条
# ══════════════════════════════════════════════════════════════════════════

def build_fid_owner(d: Path | str) -> dict[int, tuple[str, int]]:
    """读一个版本目录 → {fid: (pkg名, 包内序号)}。

    ★ 只保留第一次出现的位置（fid 跨包重复时以顺序靠前的为准）。
    """
    out: dict[int, tuple[str, int]] = {}
    for p in sorted(Path(d).glob("pkg_*.pi")):
        try:
            vs = parse_pi(p)
        except ValueError:
            continue
        for i, v in enumerate(vs):
            if v not in out:
                out[v] = (p.stem, i)
    return out


def owner_of(d: Path | str, fids, *, cache: dict | None = None) -> dict[str, dict]:
    """查一批 fid 属于哪个官方包。返回 {fid_hex: {pkg, index} | None}"""
    own = cache if cache is not None else build_fid_owner(d)
    res = {}
    for f in fids:
        v = int(f, 16) if isinstance(f, str) else int(f)
        got = own.get(v)
        res["%016X" % v] = ({"pkg": got[0], "index": got[1]} if got else None)
    return res


def owner_summary(d: Path | str, fids) -> dict:
    """一批 fid 按官方包分布。"""
    own = build_fid_owner(d)
    import collections
    c = collections.Counter()
    miss = 0
    pos = {}
    for f in fids:
        v = int(f, 16) if isinstance(f, str) else int(f)
        got = own.get(v)
        if got:
            c[got[0]] += 1
            pos.setdefault(got[0], []).append(got[1])
        else:
            miss += 1
    return {"by_pkg": dict(c.most_common()), "not_found": miss,
            "index_range": {k: [min(v), max(v)] for k, v in pos.items()}}


def diff(dir_a: Path | str, dir_b: Path | str) -> dict:
    """两个版本目录做 fid 级 diff。"""
    a, b = all_fids(dir_a), all_fids(dir_b)
    return {"a_dir": str(dir_a), "b_dir": str(dir_b),
            "a_total": len(a), "b_total": len(b),
            "added": b - a, "removed": a - b, "common": a & b}


def render(report: dict, *, limit: int = 12) -> str:
    lines = []
    lines.append("══ fid 级差异（%s → %s）══" % (
        Path(report["a_dir"]).name, Path(report["b_dir"]).name))
    lines.append("  A 唯一 %d · B 唯一 %d" % (report["a_total"], report["b_total"]))
    lines.append("  ★ 新增 %d ｜ 移除 %d ｜ 共有 %d"
                 % (len(report["added"]), len(report["removed"]), len(report["common"])))
    if report["added"]:
        lines.append("  新增前 %d 个: %s" % (
            min(limit, len(report["added"])),
            " ".join("%016X" % v for v in sorted(report["added"])[:limit])))
    if report["removed"]:
        lines.append("  移除前 %d 个: %s" % (
            min(limit, len(report["removed"])),
            " ".join("%016X" % v for v in sorted(report["removed"])[:limit])))
    return "\n".join(lines)
