# -*- coding: utf-8 -*-
r"""带 H · 热更 overlay：客户端状态 → CDN 下载 → 解包 → 对本地行。

## 这是什么

2026-09-28 新打通的第四条热更定位路。与其它三条的分工：

    H-1 服务端清单 diff     → 【包哈希级】哪些包变了（741 包 / 210 前缀）
    ★ 本条（overlay）      → 【包级】本次热更覆盖了哪几个包 + 内容可下可解
    H-1+ pkg_N.pi diff      → 【文件级】多了哪 23,322 个 fid
    loose 层                → 【内容级】客户端落地的散文件
    H-2 快照 diff           → 【本地态】哪些容器内容真变了

## 发现链（全部实测）

    ① 客户端状态文件：E:\mrzh\Documents\local_state_314_lc
         —— 是 Python pickle（protocol 5），直接 pickle.load 就能读，不用逆格式
         → version_info.overlay_files_dict.files57_2
         → 【本次热更的 overlay 包名清单】（带统一时间戳，如 1790223366974）

    ② CDN 目录名也在同一个文件里（version_info 的 pkg_lst.name 那一行）：
         "20260917_015403_release_newpc/pkg_lst.pl" ⇒ 目录 = 20260917_015403_release_newpc

    ③ 下载：https://g66.gph.netease.com/<目录>/<包名>

    ④ 解包：[32 字节头] + zstd 流
         · 实测 zhutihuodong_v5 包：965,768 B → 2,513,652 B（DDS 1832×1372 BC7）
           解出的 MD5 = 291b37891df09a9da02008a0b7e2c29f
           ★ 精确对上本地 gres\0000.gpk 的 r6604 ⇒ 端到端可验证

## 实测数字（本次那个版本）

    11 个 overlay 包，合计 35,973,908 B ≈ 34.3 MB
    （对比主包总量 42 GB —— 这就是「热更」的实义）

    19,437,400 B  script.py314.lc.overlay3.<ts>.npk      ← 另一种包装（未解）
    11,403,888 B  video.layers.1.1.overlay.<ts>.npk      ← 内层是 MP4
     2,287,076 B  instance.layers.1.1.1.overlay.<ts>.npk ← 多段 zstd（未全解）
     1,600,060 B  instance.layers.1.1.overlay.<ts>.npk   ← 同上
       965,768 B  ui/zhutihuodong_v5.layers.1.1.overlay.<ts>.npk  ★ 可解
       251,364 B  sound.layers.1.1.overlay.<ts>.npk
        19,448 B  ui.layers.1.1.3.overlay.<ts>.npk
         5,056 B  effect.layers.1.1.overlay.<ts>.npk
         3,784 B  ui.layers.1.1.2.overlay.<ts>.npk
            32 B  ui.layers.1.1.overlay.<ts>.npk        ← 空包
            32 B  ui.layers.1.1.1.overlay.<ts>.npk      ← 空包

## 边界

★ 只读 E:\mrzh（读客户端状态是只读操作）；正式服 E:\LifeAfter 一律不碰。
★ 下载只走官方 CDN，不改服务端任何东西。
"""
from __future__ import annotations

import hashlib
import pickle
import re
import struct
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Iterable

BASE_CDN = "https://g66.gph.netease.com"
_UA = {"User-Agent": "lifeafter-toolkit/1.0"}

DEFAULT_CLIENT_ROOT = Path(r"E:\mrzh")
STATE_FILE = "local_state_314_lc"
HEADER_BYTES = 32                       # overlay 包固定 32 字节头（实测）
_PKG_RE = re.compile(r"^(?P<name>.+?)\.overlay\d?\.(?P<ts>\d+)\.npk$")

# ★ 帧切分用的魔数（实测）：帧之间是 3 字节 00 00 00 + zstd 魔数
_ZMAG = b"\x28\xb5\x2f\xfd"
_MARK_ZSTD = b"\x00\x00\x00" + _ZMAG

try:
    import zstandard as zstd
except ImportError:                      # pragma: no cover
    zstd = None

# ★ 稳健原语统一来源：zstd 切帧/解压、对齐探测、加密判据、文件名卫生
#   （这些坑本项目反复踩过，实现在 toolkit_core/robust_bytes.py，
#     并有 test_robust_bytes.py 钉住 —— 不要再在本文件里另写一份）
from . import robust_bytes as RB


# ══════════════════════════════════════════════════════════════════════════
# ① 读客户端状态
# ══════════════════════════════════════════════════════════════════════════

def read_client_state(root: Path | str = DEFAULT_CLIENT_ROOT) -> dict:
    """读客户端的 local_state_314_lc（Python pickle）。

    ★ 客户端把热更状态直接用 pickle 存在盘上 —— 不用逆格式，直接 load。
    """
    p = Path(root) / "Documents" / STATE_FILE
    if not p.is_file():
        raise FileNotFoundError("找不到客户端状态文件：%s" % p)
    with p.open("rb") as fh:
        obj = pickle.load(fh)
    if not isinstance(obj, dict):
        raise ValueError("状态文件顶层不是 dict（实际 %s）" % type(obj).__name__)
    return obj


def _version_info(state: dict) -> dict:
    vi = state.get("version_info")
    if not isinstance(vi, dict):
        raise ValueError("状态文件里没有 version_info（键：%s）" % sorted(state)[:20])
    return vi


def cdn_dir(state: dict) -> str | None:
    """从状态文件里取 CDN 目录名（藏在 pkg_lst.name / pkg_N.pi.name 里）。

    不硬编码字段名：扫所有值，找形如 `<目录>/pkg_lst.pl` 或 `<目录>/pkg_N.pi` 的 name。
    """
    for v in _version_info(state).values():
        if isinstance(v, dict):
            nm = v.get("name")
            if isinstance(nm, str) and "/" in nm and ("pkg_lst" in nm or ".pi" in nm):
                return nm.split("/", 1)[0]
    return None


# ══════════════════════════════════════════════════════════════════════════
# ② 提取 overlay 清单
# ══════════════════════════════════════════════════════════════════════════

def overlay_list(state: dict) -> dict:
    """取出本次热更的 overlay 包清单。

    ★ 判据：overlay_files_dict.files57_2 里【只在覆盖层出现】的条目 = 本次覆盖的文件。
      为什么不是「主体 vs 覆盖层全量差」：
        主体的 files57_2 = 全量清单（1764 条）
        覆盖层的 files57_2 = 只列本次覆盖的（1067 条）+ 共有的 1056 条
        ⇒ 覆盖层清单里【独有】的才是本次新增；
          「只在主体」的 708 条不是被移除，而是覆盖层清单本来就不列没动的那些。

    返回 {timestamp, packages:[{name, size, hash, family, layer}]}
    """
    vi = _version_info(state)
    ov = vi.get("overlay_files_dict") or {}

    # 收集覆盖层里所有 "*.overlay<ts>.npk" 名字
    names: dict[str, dict] = {}
    for key, table in ov.items():
        if not isinstance(table, dict):
            continue
        for nm, val in table.items():
            if not isinstance(nm, str):
                continue
            m = _PKG_RE.match(nm)
            if not m:
                continue
            meta = val
            if isinstance(val, str):          # 有些表把 dict 存成了字符串
                names.setdefault(nm, {"_raw": val})
            elif isinstance(val, dict):
                names.setdefault(nm, dict(val))
    pkgs = []
    for nm, meta in sorted(names.items()):
        m = _PKG_RE.match(nm)
        pkgs.append({"name": nm, "ts": m.group("ts") if m else None,
                     "size": _to_int(meta.get("size")),
                     "hash": meta.get("hash") or meta.get("fhash") or meta.get("hash64"),
                     **({"extra": meta} if meta.get("_raw") else {})})
    ts = sorted({p["ts"] for p in pkgs if p["ts"]})
    return {"timestamp": ts[0] if len(ts) == 1 else ts, "n": len(pkgs), "packages": pkgs}


def _to_int(v) -> int | None:
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


# ══════════════════════════════════════════════════════════════════════════
# ③ 下载
# ══════════════════════════════════════════════════════════════════════════

def _get(url: str, *, timeout: float = 300.0) -> bytes:
    req = urllib.request.Request(url, headers=_UA)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def fetch(cdn_dir_name: str, names: Iterable[str], out_dir: Path | str | None = None,
          *, timeout: float = 300.0, quiet: bool = False) -> dict:
    """下载 overlay 包。已存在且大小吻合的跳过（幂等）。"""
    out = Path(out_dir) if out_dir else None
    if out:
        out.mkdir(parents=True, exist_ok=True)
    got, failed, total = [], [], 0
    for nm in names:
        url = "%s/%s/%s" % (BASE_CDN, cdn_dir_name, nm)
        dest = (out / Path(nm).name) if out else None
        if dest and dest.is_file() and dest.stat().st_size > 0:
            sz = dest.stat().st_size
            total += sz
            got.append({"name": nm, "bytes": sz, "cached": True})
            if not quiet:
                print("  = %-58s %12d B（已存在）" % (Path(nm).name[:58], sz))
            continue
        try:
            raw = _get(url, timeout=timeout)
        except (urllib.error.URLError, OSError) as exc:
            failed.append({"name": nm, "error": "%s: %s" % (type(exc).__name__, exc)})
            if not quiet:
                print("  ✗ %-58s %s" % (Path(nm).name[:58], str(exc)[:50]))
            continue
        if dest:
            dest.write_bytes(raw)
        total += len(raw)
        got.append({"name": nm, "bytes": len(raw), "md5": hashlib.md5(raw).hexdigest(),
                    "cached": False})
        if not quiet:
            print("  ✓ %-58s %12d B" % (Path(nm).name[:58], len(raw)))
    return {"cdn_dir": cdn_dir_name, "out_dir": str(out) if out else None,
            "n": len(got), "bytes": total, "packages": got, "failed": failed}


# ══════════════════════════════════════════════════════════════════════════
# ④ 解包
# ══════════════════════════════════════════════════════════════════════════

def split_frames(raw: bytes) -> list[bytes]:
    """把 overlay 包的负载切成一个个 zstd 帧。

    实测结构：[32 字节头] + N 个 zstd 帧（帧间可能有 0~3 字节对齐填充）。

    ★★ 2026-09-28 修正（旧判据漏帧，实测漏掉 76%）：
      旧判据要求帧前有【3 个零】，实测只有 153/192 个魔数前面是 0。
      后果：instance.layers.1.1.1 实际 192 帧，旧算法只切出 45 帧
            （解出 320,755 B vs 正确 1,365,605 B，差 4.3 倍）

    现委托给 toolkit_core.robust_bytes.split_zstd_frames（唯一实现）：
      所有 zstd 魔数位置都当帧起点，帧尾剥掉 0 填充。
    实测帧数：instance.1.1.1=192 · instance.1.1=169 · zhutihuodong_v5=5 ·
              effect=2 · ui.1.1.3=2 · sound/ui.1.1.2=1
    """
    if len(raw) <= HEADER_BYTES:
        return []
    return RB.split_zstd_frames(raw[HEADER_BYTES:])


def unpack_frames(raw: bytes, *, quiet: bool = True) -> dict:
    """完整解包：切帧 → 逐帧 zstd 解（坏帧不终止）→ 抽清单。

    ★ 坑：旧实现「某帧失败即 return」会丢掉已解出的部分
      （effect 包前 2 帧解得开、第 3 帧坏 ⇒ 什么信息都没留下）。
      现走 robust_bytes.decompress_zstd_frames，返回里带 bad_frames。
    """
    frames = split_frames(raw)
    r = RB.decompress_zstd_frames(raw[HEADER_BYTES:]) if frames else {
        "n_frames": 0, "n_ok": 0, "bad_frames": [], "pieces": [], "data": b"", "bytes": 0,
        "ok": False}
    pieces = r["pieces"]
    blob = r["data"]
    names = _paths_of(blob)
    return {"ok": bool(pieces), "n_frames": r["n_frames"], "n_decoded": r["n_ok"],
            "bad_frames": r["bad_frames"],
            "pieces": pieces, "names": names or _paths_of(blob),
            "unpacked": len(blob), "data": blob, "inner_magic": magic_of(blob)}


_PATHY = re.compile(rb"^[\x20-\x7e]{3,300}$")


def _paths_of(b: bytes) -> list[str]:
    """从一个解码块的开头抽纯 ASCII 路径行（overlay 包自带的名字清单）。"""
    out, rest = [], b
    while True:
        i = rest.find(b"\n")
        if i < 0:
            break
        ln = rest[:i].rstrip(b"\r")
        if not _PATHY.match(ln) or b"\\" not in ln:
            break
        out.append(ln.decode("ascii", "replace"))
        rest = rest[i + 1:]
    return out


def unpack(raw: bytes, **kw) -> dict:
    """解一个 overlay 包（= unpack_frames 的别名，保持旧调用点可用）。"""
    return unpack_frames(raw, **kw)


def _legacy_unpack(raw: bytes, *, max_out: int = 1 << 30) -> dict:
    """旧路径：把负载当「一串 zstd 帧」连续解（保留给非 overlay 场景）。"""
    out = {"packed": len(raw), "header": raw[:HEADER_BYTES].hex() if len(raw) >= HEADER_BYTES else None}
    if len(raw) <= HEADER_BYTES:
        out.update({"ok": False, "reason": "空包（≤32 字节）", "segments": []})
        return out
    try:
        import zstandard as zstd
    except ImportError:
        out.update({"ok": False, "reason": "环境缺 zstandard"})
        return out

    body = raw[HEADER_BYTES:]
    segs: list[bytes] = []
    rest = body
    consumed = 0
    fail_reason: str | None = None
    while rest:
        try:
            dobj = zstd.ZstdDecompressor().decompressobj()
            # ★ zstandard 0.25 的 decompressobj().decompress() 只收 1 个参数，
            #   传 max_output_size 会 TypeError（旧写法在这里全包失败过）。
            piece = dobj.decompress(rest)
        except Exception as exc:
            fail_reason = "第 %d 段失败：%s" % (len(segs) + 1, str(exc)[:70])
            break
        segs.append(piece)
        nxt = getattr(dobj, "unused_data", b"") or b""
        consumed = len(body) - len(nxt)
        if not nxt or nxt == rest:
            rest = b""
            break
        rest = nxt
        if len(segs) > 100000:             # 防御：不让循环跑飞
            break

    blob = b"".join(segs)
    out.update({"ok": bool(segs), "reason": fail_reason,
                "segments": [len(s) for s in segs], "n_segments": len(segs),
                "unpacked": len(blob), "data": blob, "inner_magic": magic_of(blob),
                "tail_bytes": len(body) - consumed if consumed else len(body)})
    return out


_MAGICS = {b"DDS ": "DDS", b"\x89PNG\r\n\x1a\n": "PNG", b"HPGF": "GPK", b"NXPK": "NPK",
           b"RIFF": "RIFF", b"FSB5": "FSB5", b"\x1bLua": "Lua", b"OCTL": "OCTL",
           b"CVIS": "CVIS", b"RGIS": "RGIS", b"\x00\x00\x00\x20ftyp": "MP4",
           b"PK\x03\x04": "ZIP", b"\x80\x05\x95": "pickle"}


def magic_of(b: bytes) -> str | None:
    for m, n in _MAGICS.items():
        if b.startswith(m):
            return n
    return None


def dds_info(b: bytes) -> dict | None:
    """给 DDS 读宽高/格式（不解像素）。"""
    if len(b) < 128 or b[:4] != b"DDS ":
        return None
    h, w = struct.unpack_from("<II", b, 12)
    fourcc = b[84:88]
    mips = struct.unpack_from("<I", b, 28)[0]
    return {"width": w, "height": h,
            "fourcc": fourcc.decode("latin1").strip("\x00") or "raw",
            "dxgi": struct.unpack_from("<I", b, 128)[0] if b[84:88] == b"DX10" and len(b) >= 132 else None,
            "mips": mips}


# ══════════════════════════════════════════════════════════════════════════
# ⑤ 对本地行（内容寻址）
# ══════════════════════════════════════════════════════════════════════════

def match_local(blob: bytes, index_db: Path | str, product_root: Path | str) -> list[dict]:
    """拿内容 MD5 去本地索引里找同尺寸的行，再逐行比 MD5 ⇒ 定位到「容器 + 行号」。

    ★ 不依赖名字 —— 对那 60% 无名文件是唯一可行路径。
    """
    import sqlite3
    md5 = hashlib.md5(blob).hexdigest()
    n = len(blob)
    con = sqlite3.connect("file:%s?mode=ro" % Path(index_db).as_posix(), uri=True)
    rows = con.execute(
        "SELECT container,row_index,decoded,fid_hex FROM entries WHERE decoded=?",
        (n,)).fetchall()
    root = Path(product_root)
    cache: dict[str, dict] = {}
    hits = []
    for cont, ri, de, fid in rows:
        stem = Path(cont.replace("\\", "/")).stem
        if stem not in cache:
            d = root / stem
            cache[stem] = ({int(p.stem): p for p in d.iterdir()
                            if p.is_file() and p.stem.isdigit()} if d.is_dir() else {})
        fp = cache[stem].get(ri)
        if fp is None:
            continue
        try:
            if hashlib.md5(fp.read_bytes()).hexdigest() == md5:
                hits.append({"container": cont, "row_index": ri, "fid": fid,
                             "decoded": de, "product": str(fp)})
        except OSError:
            continue
    return hits


# ══════════════════════════════════════════════════════════════════════════
# 自检
# ══════════════════════════════════════════════════════════════════════════

def selfcheck(root: Path | str = DEFAULT_CLIENT_ROOT, *, quiet: bool = False) -> dict:
    """读一次客户端状态并抽出 overlay 清单（不下载）。"""
    st = read_client_state(root)
    cd = cdn_dir(st)
    ol = overlay_list(st)
    rep = {"client_root": str(root), "cdn_dir": cd, "timestamp": ol["timestamp"],
           "n_packages": ol["n"], "total_bytes": sum(p["size"] or 0 for p in ol["packages"]),
           "packages": ol["packages"]}
    if not quiet:
        print("  客户端状态   %s" % (Path(root) / "Documents" / STATE_FILE))
        print("  CDN 目录     %s" % cd)
        print("  热更时间戳   %s" % ol["timestamp"])
        print("  ★ overlay 包 %d 个，合计 %.1f MB"
              % (ol["n"], rep["total_bytes"] / 1048576))
        for p in ol["packages"]:
            print("      %12s B  %s" % (p["size"], p["name"]))
    return rep
