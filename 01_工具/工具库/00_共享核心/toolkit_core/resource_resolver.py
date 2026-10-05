# -*- coding: utf-8 -*-
"""明日之后资源读取兼容层（只读源文件）。

重要：新任务请使用 ``toolkit_core.unified_index.UnifiedFileIndex``。
本模块保留 AES/解压/DDS 等底层函数及旧调用兼容，不再是文件索引的权威入口。

当前已验证事实（2026-09-21）
--------------------------
1. NPK/FPK（魔数 NXPK，条目 48B）每条含
   ``fid(u64)=双Murmur3路径哈希, off, clen, olen, c1, c2, flag``。
   *fid 输入规范 = 原大小写、反斜杠、latin1 的逻辑资源路径*，例如
   ``weapon\\skin\\skin_1001_001\\skin_1001_001.gim``。
   - 高 32 位 = murmur3_x86_32(path, seed=0x77777777)
   - 低 32 位 = murmur3_x86_32(path, seed=0x66666666)
2. GPK 条目为完整 ``8×u32``：末两列 ``u6/u7`` 组成直接路径 fid；旧版只读
   前 6 列并用 ``c1/c2`` 桥接的结论已作废。多块 GPK 的载荷偏移还必须按块
   使用 ``block_base + off + 20``，不能固定写成 ``off`` 或 ``off+36``。
3. 统一索引保留一个 fid 的全部物理候选；本兼容层的 ``dict[fid]`` 会覆盖
   重复项，因此只适合旧的单包读取调用，不适合生产定位与证据记录。
4. flag：0=原始(AES-ECB 加密) / 2=lz4 block / 12=zstd。
5. .gim(c159 NeoX 对象) 内部以明文路径引用 lod/mesh/挂件等子资源，可递归
   ``path_id`` 定位直到 .mesh（几何）；材质 cgmat→dds 纹理同理。

典型用法
--------
>>> from toolkit_core.resource_resolver import ResourceResolver
>>> r = ResourceResolver(r"E:\\mrzh\\res").build_index()   # ~1-4s, 约207万条
>>> loc = r.locate(r"weapon\\skin\\skin_1001_001\\skin_1001_001.gim")
>>> data = r.read_path(r"weapon\\skin\\skin_1001_001\\skin_1001_001.gim")
>>> tree = r.resolve_tree(r"weapon\\skin\\skin_1001_001\\skin_1001_001.gim", depth=3)
"""
from __future__ import annotations

import argparse
import json
import re
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

from toolkit_core.path_fid import fid_of as _fid_of  # 路径→fid 的唯一实现
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

try:
    import zstandard as _zstd
except ImportError:  # pragma: no cover
    _zstd = None

KEY = bytes([0x60, 0x63, 0x08, 0xD8, 0xA3, 0x2C, 0x78, 0x20,
             0x13, 0xD2, 0x6C, 0x2F, 0x22, 0x6F, 0x68, 0x6D])

# ----------------------------------------------------------------------
# 基础算法
# ----------------------------------------------------------------------
def aes_ecb(data: bytes) -> bytes:
    usable = len(data) // 16 * 16
    if not usable:
        return data
    dec = Cipher(algorithms.AES(KEY), modes.ECB()).decryptor()
    return dec.update(data[:usable]) + dec.finalize() + data[usable:]


_GPKI_MOD = None


def _gpki():
    """惰性加载 06_皮肤定位链/gpk_npk_index.py（块链 GPK 读取器，已被 230 万行索引验证）。

    惰性而非模块级 import，原因有二：
      ① 它不在 toolkit_core 包内，是独立脚本，只能按路径加载；
      ② 只有真的要读 .gpk 时才付出这个加载代价（纯 .npk 场景不必）。
    路径从 toolkit_core.paths.PROJECT_ROOT 取，不手算 parents[N]（项目明文规定）。
    """
    global _GPKI_MOD
    if _GPKI_MOD is None:
        import importlib.util
        from toolkit_core.paths import PROJECT_ROOT
        p = PROJECT_ROOT / "01_工具" / "工具库"  / "02_图文音频渲染" / "皮肤链与渲染" / "gpk_npk_index.py"
        if not p.is_file():
            raise FileNotFoundError(f"GPK 读取器缺失：{p}")
        spec = importlib.util.spec_from_file_location("_gpki_for_resolver", p)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        _GPKI_MOD = m
    return _GPKI_MOD


def murmur3_x86_32(data: bytes, seed: int) -> int:
    c1, c2 = 0xCC9E2D51, 0x1B873593
    h = seed & 0xFFFFFFFF
    end = len(data) & ~3
    for off in range(0, end, 4):
        k = int.from_bytes(data[off:off + 4], "little")
        k = (k * c1) & 0xFFFFFFFF
        k = ((k << 15) | (k >> 17)) & 0xFFFFFFFF
        k = (k * c2) & 0xFFFFFFFF
        h ^= k
        h = ((h << 13) | (h >> 19)) & 0xFFFFFFFF
        h = (h * 5 + 0xE6546B64) & 0xFFFFFFFF
    tail = data[end:]
    k = 0
    if len(tail) >= 3:
        k ^= tail[2] << 16
    if len(tail) >= 2:
        k ^= tail[1] << 8
    if tail:
        k ^= tail[0]
        k = (k * c1) & 0xFFFFFFFF
        k = ((k << 15) | (k >> 17)) & 0xFFFFFFFF
        k = (k * c2) & 0xFFFFFFFF
        h ^= k
    h ^= len(data)
    h ^= h >> 16
    h = (h * 0x85EBCA6B) & 0xFFFFFFFF
    h ^= h >> 13
    h = (h * 0xC2B2AE35) & 0xFFFFFFFF
    h ^= h >> 16
    return h & 0xFFFFFFFF


def path_id(logical_path: str) -> int:
    """逻辑资源路径 → 64 位 fid。委托给唯一实现 toolkit_core.path_fid。

    ★ 2026-09-26 修：原实现写死 latin1 ⇒ 含中文的路径直接抛 UnicodeEncodeError
      （实测：黑名单\\测试表.csv → 'latin-1' codec can't encode），
      其上层 texture_extractor 因此静默拿不到数据。
      现改为 utf-8 + 归一分隔符，与项目其余实现一致；纯 ASCII 路径结果逐位不变。
    """
    return _fid_of(logical_path, encoding="utf-8", normalize_sep=True)


def lz4_block(blob: bytes, expected: int) -> bytes:
    out = bytearray()
    cur = 0

    def extend(value: int) -> int:
        nonlocal cur
        if value == 15:
            while True:
                part = blob[cur]
                cur += 1
                value += part
                if part != 255:
                    break
        return value

    while cur < len(blob) and len(out) < expected:
        token = blob[cur]
        cur += 1
        lit_len = extend(token >> 4)
        out.extend(blob[cur:cur + lit_len])
        cur += lit_len
        if cur >= len(blob):
            break
        distance = blob[cur] | (blob[cur + 1] << 8)
        cur += 2
        if distance == 0 or distance > len(out):
            raise ValueError("lz4 invalid distance")
        match_len = extend(token & 15) + 4
        src = len(out) - distance
        for _ in range(match_len):
            out.append(out[src])
            src += 1
    return bytes(out)


def unpack_entry(packed: bytes, declared_size: int, flag: int) -> bytes:
    if flag == 2:
        return lz4_block(packed, declared_size)
    if flag == 12:
        if _zstd is None:
            raise RuntimeError("zstandard 未安装")
        return _zstd.ZstdDecompressor().decompress(packed, max_output_size=declared_size)
    if flag == 0:
        return aes_ecb(packed)
    return packed


# ----------------------------------------------------------------------
# 数据结构
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Entry:
    pkg: str          # 包文件名，如 003.fpk
    index: int        # 条目序号
    offset: int
    packed_size: int
    declared_size: int
    c1: int
    c2: int
    flag: int

    def cc(self) -> str:
        return f"{self.c1:08x}/{self.c2:08x}"


_NXPK_ENTRY = struct.Struct("<QIIIIIi")  # fid,off,clen,olen,c1,c2,flag
_DEP_RE = re.compile(rb"[A-Za-z0-9_\-\\/\.]{4,160}")
_DEP_EXT = re.compile(r"\.(gim|mesh|mtg|cgmat|mat|mtl|dds|tga|pvr|png|jpg|skeleton|anim|fx|cgfx)$", re.I)

# ----------------------------------------------------------------------
# .mtg 材质 / KPGF 分卷 gpk / BCn-DDS 解码（2026-08-31 第一项攻坚固化）
# ----------------------------------------------------------------------
# .mtg(c159 序列化的 NeoX 材质)内，贴图逻辑路径形如
#   weapon\skin\skin_1001_001\textures\skin_1001_001001a.tga
# 尾缀通道：a=albedo 主色 / n=normal 法线 / m=metallic 金属度 / s_m=smoothness
_TEX_PATH_RE = re.compile(rb"[A-Za-z0-9_\-\\/\.]{4,160}\.(?:tga|dds|png|pvr)")
_SHADER_RE = re.compile(rb"[A-Za-z0-9_\-\\/\.]{2,120}\.fx")


def parse_mtg(data: bytes) -> dict:
    """解析 .mtg 材质(c159 对象)，提取 shader 名与 PBR 贴图逻辑路径。

    返回 {"shader": str|None, "textures": [反斜杠逻辑路径...],
          "channels": {尾缀字母: 路径}}。通道仅对 ``xxx数字+字母.tga`` 命名生效。
    """
    sh = _SHADER_RE.search(data)
    texs, channels = [], {}
    for m in _TEX_PATH_RE.findall(data):
        s = m.decode("latin1").replace("/", "\\")
        if s not in texs:
            texs.append(s)
        stem = s.rsplit(".", 1)[0].rsplit("\\", 1)[-1]
        mm = re.search(r"(\d+)([a-z](?:_[a-z])?)$", stem)
        if mm:
            channels.setdefault(mm.group(2), s)
    return {"shader": sh.group(0).decode("latin1") if sh else None,
            "textures": texs, "channels": channels}


def iter_kpgf_entries(data: bytes):
    """解一个 KPGF 分卷 gpk 条目（36B 明文头 + 多帧 zstd），逐帧产出解压字节。

    textures.gpk 实测：条目 = 36B 头（[16]=clen,[20]=olen,[24]=c1,[28]=c2,
    [32]=flag）+ 一/多帧 zstd；用 read_across_frames 跨帧读全。仅 flag=12。
    """
    if _zstd is None:
        raise RuntimeError("zstandard 未安装")
    import io as _io
    dctx = _zstd.ZstdDecompressor()
    reader = dctx.stream_reader(_io.BytesIO(data[36:]), read_across_frames=True)
    chunks = []
    while True:
        b = reader.read(1 << 20)
        if not b:
            break
        chunks.append(b)
    out = b"".join(chunks)
    # 按 DDS 魔数切出多帧
    locs, i = [], 0
    while True:
        j = out.find(b"DDS ", i)
        if j < 0:
            break
        locs.append(j)
        i = j + 4
    for k, s in enumerate(locs):
        e = locs[k + 1] if k + 1 < len(locs) else len(out)
        yield out[s:e]


def decode_bcn_dds(dds: bytes):
    """BCn/DX10 DDS 主 mip -> PIL.Image（依赖 texture2ddecoder，缺失返回 None）。

    支持 DX10/BC7(98)、DXT5(BC3)、DXT1(BC1)；返回 RGBA Image，通道序 BGRA。
    """
    if len(dds) < 128:
        return None
    try:
        import texture2ddecoder as t2d
        from PIL import Image
    except ImportError:
        return None
    h, w = struct.unpack_from("<II", dds, 12)
    fourcc = dds[84:88]
    bw, bh = (w + 3) // 4, (h + 3) // 4
    try:
        if fourcc == b"DX10":
            dxgi = struct.unpack_from("<I", dds, 128)[0]
            if dxgi == 98:  # BC7_UNORM
                raw = t2d.decode_bc7(dds[148:148 + bw * bh * 16], w, h)
            elif dxgi == 83:  # BC5_UNORM
                raw = t2d.decode_bc5(dds[148:148 + bw * bh * 16], w, h)
            else:
                return None
        elif fourcc == b"DXT5":
            raw = t2d.decode_bc3(dds[128:128 + bw * bh * 16], w, h)
        elif fourcc == b"DXT1":
            raw = t2d.decode_bc1(dds[128:128 + bw * bh * 8], w, h)
        else:
            return None
        return Image.frombytes("RGBA", (w, h), raw, "raw", "BGRA")
    except Exception:
        return None


class ResourceResolver:
    """旧 NXPK 兼容读取器；生产定位请改用 ``UnifiedFileIndex``。"""

    def __init__(self, res_dir: Path | str = r"E:\mrzh\res"):
        self.res_dir = Path(res_dir)
        # fid(int) -> Entry
        self._by_fid: dict[int, Entry] = {}
        # 内容指纹 "c1/c2" -> fid(int)
        self._cc_to_fid: dict[str, int] = {}
        self.built = False

    # ----- 索引 -----
    def _scan_nxpk(self, path: Path) -> None:
        with path.open("rb") as f:
            header = aes_ecb(f.read(64))
            if header[8:12] != b"NXPK":
                return
            table_off, count = struct.unpack_from("<II", header, 16)
            f.seek(table_off)
            table = aes_ecb(f.read(count * 48))
        for i in range(count):
            fid, off, clen, olen, c1, c2, flag = _NXPK_ENTRY.unpack_from(table, i * 48)
            entry = Entry(path.name, i, off, clen, olen, c1, c2, flag)
            self._by_fid[fid] = entry
            self._cc_to_fid.setdefault(entry.cc(), fid)

    def _scan_gpk(self, path: Path) -> None:
        """扫描块链 GPK（新版 res 族容器）。

        ★ 为什么需要它：新版客户端把 res.npk / ui.npk 换成了一批 .gpk，
          而 _scan_nxpk 只认 NXPK 魔数（不符即 return，不报错）。
          此前 build_index 也只 glob *.npk / *.fpk ⇒ 在 E:/mrzh/res 上会建出
          【空索引】。调用方（texture_extractor 的 only_unique 判据）拿到空索引后
          所有 cc 查询都返回 None ⇒「只取独有贴图」静默退化成「取全部」——
          不报错、不警告，只是给错。

        格式与位移规则与 06_皮肤定位链/gpk_npk_index._gpk_blockchain 保持同源
        （该读取器已被 230 万行的统一索引验证），本函数只是把 c1/c2 也用起来。
        """
        mod = _gpki()
        _rec, rows, _blocks = mod._gpk_blockchain(str(path), with_crc=True)
        for i, fid, payload_off, packed, decoded, flag, c1, c2 in rows():
            entry = Entry(path.name, i, payload_off, packed, decoded, c1, c2, flag)
            self._by_fid[fid] = entry
            self._cc_to_fid.setdefault(entry.cc(), fid)

    def _scan_any(self, path: Path) -> None:
        """按魔数分派容器格式：NXPK（NPK）或块链 GPK。两者都不像则跳过。"""
        try:
            with path.open("rb") as f:
                head = aes_ecb(f.read(16))
        except OSError:
            return
        if len(head) >= 12 and head[8:12] == b"NXPK":
            self._scan_nxpk(path)
            return
        if len(head) >= 16:
            mod = _gpki()
            _zero, masked, two, nblocks = struct.unpack("<IIII", head)
            if two == 2 and (masked ^ mod.GPK_XOR_BLOCKS) == nblocks and 0 < nblocks < 100_000:
                self._scan_gpk(path)

    def build_index(self, include_ui_npk: bool = True,
                    recursive: bool = True) -> "ResourceResolver":
        """建立全局 fid 索引（NPK + 块链 GPK 一并扫描）。

        recursive=True（默认）递归扫描 res 下所有 .gpk / .fpk / .npk；
        False 只扫根目录一层。

        ★ 变更（2026-09-26）：原先只 glob *.fpk / *.npk，而新版客户端 res 族
          全是 .gpk ⇒ 在 E:/mrzh/res 上建出【空索引】且不报错（实测 0 条）。
          现已把 *.gpk 纳入，并按魔数分派 NPK / GPK 两种格式。

        include_ui_npk 已废弃：旧逻辑专门去找 res/ui.npk，该分支在 recursive=True
        （两个既有调用方都用默认值）下根本不可达；且 ui.npk 已被 ui_01~05.gpk 取代，
        这些 gpk 现在由上面的通配自然覆盖。参数保留仅为兼容旧调用签名。
        """
        self._by_fid.clear()
        self._cc_to_fid.clear()
        pkgs = []
        for pat in ("*.gpk", "*.fpk", "*.npk"):
            pkgs += sorted(self.res_dir.rglob(pat) if recursive
                           else self.res_dir.glob(pat))
        for pkg in pkgs:
            self._scan_any(pkg)
        self.built = True
        return self

    def find_unique_in_gpk(self, gpk_path: Path | str, exts=(".dds",)) -> dict:
        """已禁用：旧 c1/c2 桥会漏读 GPK 行末的真实 fid。"""
        raise RuntimeError(
            "find_unique_in_gpk 已作废：请先运行 run_all.py index build，"
            "再用 run_all.py find/extract 或 UnifiedFileIndex")

    def stats(self) -> dict:
        return {"fid_entries": len(self._by_fid), "unique_cc": len(self._cc_to_fid)}

    # ----- 路径变体 -----
    @staticmethod
    def _variants(path: str) -> Iterable[str]:
        yield path
        yield path.replace("/", "\\")
        yield path.replace("\\", "/")

    # ----- 定位 / 读取 -----
    def locate(self, path: str) -> Optional[Entry]:
        """逻辑路径 -> Entry（自动尝试正/反斜杠），找不到返回 None。"""
        for cand in self._variants(path):
            entry = self._by_fid.get(path_id(cand))
            if entry is not None:
                return entry
        return None

    def read_entry(self, entry: Entry) -> bytes:
        with (self.res_dir / entry.pkg).open("rb") as f:
            f.seek(entry.offset)
            packed = f.read(entry.packed_size)
        return unpack_entry(packed, entry.declared_size, entry.flag)

    def read_path(self, path: str) -> Optional[bytes]:
        entry = self.locate(path)
        return None if entry is None else self.read_entry(entry)

    # ----- gim 依赖 / 递归 -----
    @staticmethod
    def walk_dependencies(data: bytes) -> list[str]:
        """从 c159/gim 等对象里抽取它引用的子资源逻辑路径（统一成反斜杠）。"""
        out: set[str] = set()
        for m in _DEP_RE.findall(data):
            s = m.decode("latin1").replace("/", "\\")
            if _DEP_EXT.search(s):
                out.add(s)
        return sorted(out)

    def resolve_tree(self, root_path: str, depth: int = 3) -> dict:
        """递归定位一套资源（不落地大数据，只记录位置/大小/魔数）。"""
        seen: set[str] = set()
        nodes: dict[str, dict] = {}
        missing: list[str] = []
        queue = [(root_path, 0)]
        while queue:
            pth, lvl = queue.pop(0)
            if pth in seen:
                continue
            seen.add(pth)
            entry = self.locate(pth)
            if entry is None:
                missing.append(pth)
                nodes[pth] = {"found": False}
                continue
            info = {"found": True, "pkg": entry.pkg, "index": entry.index,
                    "size": entry.declared_size, "flag": entry.flag, "cc": entry.cc()}
            if lvl < depth:
                try:
                    data = self.read_entry(entry)
                    info["magic"] = data[:4].hex()
                    for child in self.walk_dependencies(data):
                        if child not in seen:
                            queue.append((child, lvl + 1))
                except Exception as exc:  # pragma: no cover
                    info["read_error"] = repr(exc)
            nodes[pth] = info
        return {"root": root_path, "visited": len(seen), "missing": missing, "nodes": nodes}

    # ----- GPK 匿名条目经 c1/c2 内容指纹桥接取名 -----
    def bridge_gpk(self, gpk_path: Path | str) -> dict:
        """已禁用：GPK 自带 fid，无需也不得再用 c1/c2 猜桥。"""
        raise RuntimeError(
            "bridge_gpk 已作废：GPK 32B 行必须按 8×u32 读取；"
            "请使用 UnifiedFileIndex")


# ----------------------------------------------------------------------
# CLI 演示
# ----------------------------------------------------------------------
def _main() -> None:
    """★ 2026-09-28：命令定义已收编进统一 CLI（`toolkit_cli.build_parser`），
    这里不再自带一份 argparse —— 否则同一能力两处定义、改一处另一处静默坏掉。
    保留 `python -m toolkit_core.resource_resolver ...` 作为薄转发入口。
    """
    import sys
    for base in Path(__file__).resolve().parents:
        cand = base / "命令行"
        if (cand / "toolkit_cli.py").is_file():
            if str(cand) not in sys.path:
                sys.path.insert(0, str(cand))
            break
    from toolkit_cli import main as _cli_main
    raise SystemExit(_cli_main(["resolver"] + sys.argv[1:]))


if __name__ == "__main__":
    _main()
