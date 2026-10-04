# -*- coding: utf-8 -*-
r"""container_probe.py — 容器/官方包清单探针（全量拆包复核 2026-09-28 逼出来的三条能力）。

为什么有这个模块（全部是「当时只能手写脚本」的具体场景）
--------------------------------------------------------
① **官方 ``pkg_N.pi`` 布局**：想做 release vs playertest 的「新增了哪些**有名有姓**的文件」，
   当时只能现写脚本读二进制。这里把布局实测固化成一条带自检的函数：
       ``[u64 count][count × u64 fid]``，文件长度必须等于 ``8 + 8*count``。
   ★ 自检是重点：不符合立刻报 ``layout_ok=False``，而不是静默少读几条。

② **overlay 包的条目级解包**：``delta overlay`` 只有 list/fetch/locate，没有 unpack；
   而且 locate 内部用「扫 zstd 魔数」切块 —— 实测**只覆盖了 1741 条里的 371 条**
   （instance.layers.1.1.1 声明 390 条，魔数只找到 192 个；flag=0 的原始条目一条都拿不到）。
   实测真相：**overlay 包就是普通 NPK 容器**（头 32 B 经 AES-ECB 解密后 offset 8 起是
   ``NXPK`` 魔数 + version=3），所以直接走 ``la_unpack_core.NpkArchive`` 就能拿全。
   这里把它做成 ``overlay_entries`` / ``overlay_unpack``。

③ **物理定位（容器 + 行号 → 产物文件）**：``artifact_locator.Locator.stem_of`` 用
   ``Path(...).stem``，把 ``res\script.py314.lc.npk`` 与 ``Documents\script.py314.lc.npk``
   折成同一个 ``script.py314.lc`` ⇒ 两个容器会互相串目录去查。实测产物目录其实是
   ``script.py314.lc`` 与 ``Documents__script.py314.lc``（见 restore_tree.container_dir_name）。
   这里用与之**同一套**命名规则，避免再串。

边界：本模块只读 ``E:\mrzh`` 之外的项目产物 + 只读索引库；不写任何源目录。
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import struct
import sys
from pathlib import Path
from typing import Any, Iterable, Optional

__all__ = [
    "PI_LAYOUT", "parse_pi", "pi_dir_fids", "pi_diff",
    "overlay_entries", "overlay_unpack", "classify_bytes",
    "container_dir_name", "Locator", "PRODUCT_ROOT", "unpack_core",
]

# 实测布局：8 字节小端 u64 条数 + 条数 × 8 字节小端 u64 fid
PI_LAYOUT = "u64_le count @0, then count * u64_le fid @8"
PI_HEADER_BYTES = 8
PI_RECORD_BYTES = 8

# ★ 2026-09-29：默认产物根改为【智能选】（载荷在就用载荷，已清则回退树）。
#   原因：S5 已按架构改造清掉 `20_提取/.../files` 载荷；写死路径会让
#   所有没显式传根的命令静默返回 0 结果（比报错更危险）。
def _default_product_root() -> Path:
    try:
        from toolkit_core import artifact_locator as _AL
        return _AL.default_product_root()
    except Exception:
        return Path(r"E:/la拆包项目/03_执行/41_还原树")


PRODUCT_ROOT = _default_product_root()
INDEX_DB = Path(r"E:/la拆包项目/03_执行/10_索引/indexes/lifeafter_files.sqlite3")


# ══════════════════════════════════════════════════════════════════════════
# ① 官方 pkg_N.pi
# ══════════════════════════════════════════════════════════════════════════

def parse_pi(path: str | os.PathLike) -> dict[str, Any]:
    """解析一个 ``pkg_N.pi`` → ``{"fids","count","actual_bytes","expected_bytes","layout_ok"}``。

    布局（实测，见 ``PI_LAYOUT``）：``[u64 count][count × u64 fid]``。
    长度不符时**如实报告** ``layout_ok=False``，不截断、不猜。
    """
    b = Path(path).read_bytes()
    out: dict[str, Any] = {"path": str(path), "actual_bytes": len(b), "fids": [],
                           "count": None, "expected_bytes": None,
                           "layout_ok": False, "error": None}
    if len(b) < PI_HEADER_BYTES:
        out["error"] = "文件比 8 字节头还短"
        return out
    n = struct.unpack_from("<Q", b, 0)[0]
    out["count"] = n
    out["expected_bytes"] = PI_HEADER_BYTES + n * PI_RECORD_BYTES
    if out["expected_bytes"] != len(b):
        out["error"] = ("声明 %d 条 ⇒ 应为 %d 字节，实际 %d 字节"
                        % (n, out["expected_bytes"], len(b)))
        return out
    out["fids"] = list(struct.unpack_from("<%dQ" % n, b, PI_HEADER_BYTES)) if n else []
    out["layout_ok"] = True
    return out


def pi_dir_fids(d: str | os.PathLike) -> dict[str, set[int]]:
    """一个目录下全部 ``pkg_N.pi`` → ``{pkg名: fid 集合}``；布局不符的包进 ``_bad``。"""
    out: dict[str, set[int]] = {}
    bad: dict[str, str] = {}
    for p in sorted(Path(d).glob("pkg_*.pi")):
        r = parse_pi(p)
        if r["layout_ok"]:
            out[p.stem] = set(r["fids"])
        else:
            bad[p.name] = r["error"] or "布局不符"
    if bad:
        out["_bad"] = bad  # type: ignore[assignment]
    return out


def pi_diff(dir_a: str | os.PathLike, dir_b: str | os.PathLike) -> dict[str, Any]:
    """两个版本的 ``pkg_N.pi`` 目录做 fid 级增删（**并集口径**，不是逐包比）。"""
    a = {k: v for k, v in pi_dir_fids(dir_a).items() if not k.startswith("_")}
    b = {k: v for k, v in pi_dir_fids(dir_b).items() if not k.startswith("_")}
    sa = set().union(*a.values()) if a else set()
    sb = set().union(*b.values()) if b else set()
    return {"a_dir": str(dir_a), "b_dir": str(dir_b),
            "a_pkgs": len(a), "b_pkgs": len(b),
            "a_total": len(sa), "b_total": len(sb),
            "added": sorted(sb - sa), "removed": sorted(sa - sb),
            "common": len(sa & sb)}


# ══════════════════════════════════════════════════════════════════════════
# ② overlay 包（= 普通 NPK 容器）
# ══════════════════════════════════════════════════════════════════════════

def _toolkit_root() -> Optional[Path]:
    here = Path(__file__).resolve()
    for up in here.parents:
        if (up / "01_解码定位复原" / "解包与扫描" / "la_unpack_core.py").is_file():
            return up
    return None


_CORE = None


def unpack_core():
    """惰性载入 ``01_解码定位复原/解包与扫描/la_unpack_core.py``（唯一 NPK 实现）。

    不手算 parents[N]：向上搜索含该文件的目录（层级搬迁过多次）。
    """
    global _CORE
    if _CORE is not None:
        return _CORE
    root = _toolkit_root()
    if root is None:
        raise ImportError("找不到 01_解码定位复原/解包与扫描/la_unpack_core.py")
    d = root / "01_解码定位复原" / "解包与扫描"
    if str(d) not in sys.path:
        sys.path.insert(0, str(d))
    import la_unpack_core as core        # noqa: PLC0415
    _CORE = core
    return core


def overlay_entries(path: str | os.PathLike) -> dict[str, Any]:
    """把一个 overlay ``.npk`` 当 NPK 容器读条目表。

    ★ 实测：overlay 包就是普通 NPK（32 B AES-ECB 头解密后 offset 8 起 ``NXPK`` + ver 3），
      所以条目表能完整读出；「扫 zstd 魔数」那条路只覆盖一部分条目。
    ``count == 0`` 的空包（``ui.layers.1.1.overlay`` 实测 32 字节）返回空表而非报错。
    """
    p = Path(path)
    out: dict[str, Any] = {"path": str(p), "bytes": p.stat().st_size,
                           "entries": [], "n": 0, "flags": {}, "error": None}
    try:
        core = unpack_core()
        with core.NpkArchive(p) as ar:
            ents = list(ar.iter_entries())
    except ValueError as exc:
        # 实测：count=0 的空容器会让 la_unpack_core 抛「NPK 表越界」
        if "count=0" in str(exc) or "表越界" in str(exc):
            out["empty"] = True
            out["error"] = str(exc)
            return out
        out["error"] = "%s: %s" % (type(exc).__name__, exc)
        return out
    except Exception as exc:                       # noqa: BLE001
        out["error"] = "%s: %s" % (type(exc).__name__, exc)
        return out
    flags: dict[str, int] = {}
    for e in ents:
        flags[str(e.flag)] = flags.get(str(e.flag), 0) + 1
        out["entries"].append({"index": e.entry_index, "fid": e.file_id_hex,
                               "offset": e.offset, "packed": e.packed,
                               "decoded": e.decoded, "flag": e.flag})
    out["n"] = len(ents)
    out["flags"] = flags
    return out


_MAGIC = ((b"DDS ", "dds"), (b"\x89PNG\r\n\x1a\n", "png"), (b"RIFF", "riff"),
          (b"NXPK", "npk"), (b"OggS", "ogg"), (b"<?xml", "xml"),
          (b"<FxGroup", "fx"), (b"ftyp", "mp4"), (b"BM", "bmp"),
          (b"KTX ", "ktx"), (b"\x1f\x8b", "gz"))


def classify_bytes(b: bytes) -> str:
    """载荷 → 类型短名。先试 NPK 内嵌逻辑路径（NPK 条目载荷以路径串开头），再退魔数。"""
    for magic, short in _MAGIC:
        if b.startswith(magic):
            return short
    if len(b) > 8 and b[4:8] == b"ftyp":
        return "mp4"
    if b[:1] == b"\x78" and b[1:2] in (b"\x01", b"\x9c", b"\xda"):
        return "zlib"
    try:
        core = unpack_core()
        p = core.parse_logical_path(b)
        if p:
            return "path+" + (p.rsplit(".", 1)[-1].lower() if "." in p else "bin")
    except Exception:                              # noqa: BLE001
        pass
    try:
        head = b[:200].decode("ascii")
        if head and all(32 <= ord(c) < 127 or c in "\r\n\t" for c in head):
            return "text"
    except UnicodeDecodeError:
        pass
    return "bin"


def overlay_unpack(paths, out_dir: str | os.PathLike, *,
                   write: bool = True, progress=None) -> dict[str, Any]:
    """overlay 包（一个文件或一个目录）→ 条目级全量解包 + 分类落盘。

    返回 ``{"n_pkgs","n_entries","ok","failed","types","entries":[...]}``。
    落盘命名 ``<包名去.overlay>/<fid>.<类型短名>``；空包不给文件。
    """
    out_root = Path(out_dir)
    if isinstance(paths, (str, os.PathLike)):
        p = Path(paths)
        files = sorted(p.glob("*.npk")) if p.is_dir() else [p]
    else:
        files = [Path(x) for x in paths]

    core = unpack_core()
    rep: dict[str, Any] = {"out": str(out_root), "n_pkgs": 0, "n_entries": 0,
                           "ok": 0, "failed": 0, "empty_pkgs": [], "types": {},
                           "entries": []}
    types: dict[str, int] = {}
    for fp in files:
        meta = overlay_entries(fp)
        if meta.get("error") and not meta["entries"]:
            rep["empty_pkgs"].append({"pkg": fp.name, "error": meta["error"]})
            continue
        rep["n_pkgs"] += 1
        sub = out_root / fp.stem.replace(".overlay", "_ov")
        if write:
            sub.mkdir(parents=True, exist_ok=True)
        with core.NpkArchive(fp) as ar:
            handle = ar._ensure_handle()
            for e in meta["entries"]:
                rep["n_entries"] += 1
                rec = {"pkg": fp.name, "index": e["index"], "fid": e["fid"],
                       "offset": e["offset"], "packed": e["packed"],
                       "decoded": e["decoded"], "flag": e["flag"]}
                handle.seek(e["offset"])
                packed = handle.read(e["packed"])
                try:
                    data = core.npk_decode_entry(packed, e["decoded"], e["flag"],
                                                 declared_packed=e["packed"])
                except Exception as exc:           # noqa: BLE001
                    rep["failed"] += 1
                    rec["error"] = "%s: %s" % (type(exc).__name__, exc)
                    rep["entries"].append(rec)
                    continue
                rep["ok"] += 1
                kind = classify_bytes(data)
                types[kind] = types.get(kind, 0) + 1
                rec["kind"] = kind
                rec["bytes"] = len(data)
                rec["sha256"] = hashlib.sha256(data).hexdigest()
                rec["md5"] = hashlib.md5(data).hexdigest()
                if write:
                    dest = sub / ("%s.%s" % (e["fid"], kind))
                    dest.write_bytes(data)
                    rec["file"] = str(dest)
                rep["entries"].append(rec)
                if progress and rep["n_entries"] % 200 == 0:
                    progress(rep["n_entries"])
    rep["types"] = types
    return rep


# ══════════════════════════════════════════════════════════════════════════
# ③ 物理定位：容器 + 行号 → 产物文件
# ══════════════════════════════════════════════════════════════════════════

def container_dir_name(container: str) -> str:
    r"""容器名 → 产物目录名。

    ★ 2026-09-28 统一：**委托给 `artifact_locator.dir_name_of`（唯一实现）**。
    历史上这里有一份硬编码 `script.py314.lc` 特例的版本，`restore_tree` 还有一份 ——
    三份行为不完全等价（实测 60 个容器上这份与 artifact_locator 结果一致，
    但硬编码特例对将来新增的「同名 stem」容器会失效）。
    规则：**「把分隔符换成 __ 的规范化名」存在就用它，否则退回 stem。**
    """
    from toolkit_core.artifact_locator import dir_name_of as _dn
    try:
        return _dn(container, PRODUCT_ROOT)
    except Exception:
        # 兜底：产物根不在时至少给出与旧实现一致的名字
        c = str(container).replace("/", "\\")
        parts = [p for p in c.split("\\") if p]
        if not parts:
            return str(container)
        base = parts[-1]
        stem = base.rsplit(".", 1)[0] if "." in base else base
        if stem == "script.py314.lc" and len(parts) >= 2:
            return "%s__%s" % (parts[-2], stem)
        return stem


class Locator:
    r"""容器 + 行号 → 产物 Path。

    ★ 2026-09-28 改为**继承 `artifact_locator.Locator`**：
      · 目录名规则走同一份实现（不再各写一套）
      · 顺带继承【磁盘缓存】—— 列一次大目录（0000/ 54,292 个、scene_03/ 79,161 个）
        的结果落到 `_product_row_cache/`，后续进程直接读。
        实测：这条让 `test_locator_known_rows_match_index_names` 从 142s 降到秒级。

    ★★ 2026-09-29（架构改造 S5）：`path()` 改为走 **`UnifiedResolver`（树优先、载荷回退）**。
      为什么：初拆载荷已被 S5 清掉；若仍只查载荷，所有调用方都会「静默返回 None」——
      那不报错但结果全空，比报错更危险。
      `root` 显式给了就只查那个根（保持老语义，测试/对照用）。
    """

    def __init__(self, root: str | os.PathLike | None = None):
        from toolkit_core import artifact_locator as _AL
        # ★ root 不给 → 智能（树优先 + 载荷回退）；给了 → 尊重调用方
        self._resolver = _AL.UnifiedResolver(
            source="auto" if root is None else "extract",
            extract_root=root)
        self._base = self._resolver.extract
        self.root = Path(root) if root else _AL.default_product_root()
        self._miss: list[str] = []

    def rows(self, container: str) -> dict[int, Path]:
        return self._resolver.rows(container)

    def path(self, container: str, row: int) -> Optional[Path]:
        p = self._resolver.path(container, row)
        if p is None:
            self._miss.append("%s r%s" % (container, row))
        return p

    def read(self, container: str, row: int, limit: int | None = None) -> Optional[bytes]:
        p = self.path(container, row)
        if p is None:
            return None
        if limit is None:
            return p.read_bytes()
        with p.open("rb") as fh:
            return fh.read(limit)

    def locate_fid(self, fid_hex: str, db: str | os.PathLike = INDEX_DB,
                   limit: int = 20) -> list[dict[str, Any]]:
        """fid（16 位大写 hex）→ 索引里的 [(容器, 行, 大小)] + 产物路径。"""
        import sqlite3
        rows = []
        con = sqlite3.connect("file:%s?mode=ro" % str(db).replace("\\", "/"), uri=True)
        try:
            for c, r, d in con.execute(
                    "SELECT container,row_index,decoded FROM entries WHERE fid_hex=? LIMIT ?",
                    (fid_hex.upper(), limit)):
                p = self.path(c, r)
                rows.append({"container": c, "row": r, "decoded": d,
                             "artifact": str(p) if p else None,
                             "exists": bool(p and p.is_file())})
        finally:
            con.close()
        return rows

    def stats(self) -> dict:
        # ★ 目录映射现在由基类持有（artifact_locator.Locator），这里转发
        s = dict(self._base.stats())
        s["misses"] = len(self._miss)
        s["miss_sample"] = self._miss[:5]
        return s
