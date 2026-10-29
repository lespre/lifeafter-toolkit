# -*- coding: utf-8 -*-
"""头像板资源统一回源：PE → PC 索引 → PC 校准表，三级回源。

为什么需要（2026-10-30）：
  · PE（安卓测试服）索引只覆盖部分资源；名片框/头像的 Spine 图集与高清边框图
    大量只存在于 **PC（正式服）** 包里。
  · PC 又有两种命中方式：
      1) fid 索引（pc_index.sqlite3）—— 路径哈希能对上时命中；
      2) **校准表**（pc_fid_calib/hit_table.csv）—— fid 对不上时的兜底，
         这张表是「路径 → (包,行)」的权威映射，名片框高清边框（1292×810）
         全部只能靠它命中（实测 fid 索引对 ui/mingpiankuang_icon/* 命中率极低）。
  · 校准表带同名跨目录污染的历史坑（见 pc_fetch.resolve_csv 的注释：
    「跨目录同名会把别的资源串进来（实测名片框串成场景截图）」），
    所以本模块的同名兜底**强制限定同目录**。

对外 API：
    R = Resolver()
    R.locate(logical_path)          → (tag, pack, row) | None
    R.payload(tag, pack, row)       → bytes | None
    R.image(tag, pack, row)         → PIL.Image(RGBA) | None
    R.fetch_text(logical_path)      → str | None
    R.fetch_png(logical_path, out)  → bool
"""
from __future__ import annotations

import csv
import io
import pathlib
import sqlite3
import sys


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ, client_root  # noqa: E402
_TOOLS = PROJ / "00_规范与工具/工具/工具库"
for _p in (_TOOLS / "00_共享核心", _TOOLS / "01_解码定位复原/图集与取图"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from toolkit_core.path_fid import fid_of                    # noqa: E402
from toolkit_core import android_gpk as AG                  # noqa: E402

_DET = PROJ / "01_索引与产物/10_索引/热更检测"
_PE_IDX = _DET / "pe_index.sqlite3"
_PC_IDX = _DET / "pc_index.sqlite3"
_CALIB = _DET / "pc_fid_calib"
_PE_PACKS = PROJ / "01_索引与产物/源包/pe_gres_android"
if not _PE_PACKS.is_dir():
    _PE_PACKS = _DET / "pe_packs"
_PC_ROOTS = (pathlib.Path(client_root()), pathlib.Path(client_root() / "res"),
             pathlib.Path(client_root() / "Documents/gres"))

PE_EXTS = (".ktx", ".dds", ".png", ".bc7")
PC_EXTS = (".bc7", ".png", ".dds", ".ktx", ".jpg")
TEX_EXTS = (".bc7", ".png", ".jpg", ".ktx", ".dds")


def _hx(v) -> str:
    return v if isinstance(v, str) else "%016X" % (v & 0xFFFFFFFFFFFFFFFF)


def _strip_ext(stem: str) -> str:
    low = stem.lower()
    for e in (".ktx", ".dds", ".png", ".bc7", ".jpg"):
        if low.endswith(e):
            return stem[: -len(e)]
    return stem


class Resolver:
    """PE/PC 双库统一解析器（索引 + PC 校准表）。"""

    def __init__(self, use_calib: bool = True):
        self.pe_con = self._open(_PE_IDX)
        self.pc_con = self._open(_PC_IDX)
        self._calib = None
        if use_calib:
            self._load_calib()
        self._pe_pack_cache = {}
        self._pc_pack_cache = {}

    # ── 索引 ────────────────────────────────────────────────
    @staticmethod
    def _open(p: pathlib.Path):
        if not p.is_file():
            return None
        try:
            return sqlite3.connect("file:%s?mode=ro" % str(p).replace("\\", "/"),
                                   uri=True, timeout=20)
        except Exception:                                   # noqa: BLE001
            return None

    def _load_calib(self):
        """PC 校准表：路径 → (pkg,row)；同名索引只留同目录用。"""
        exact = {}
        by_name = {}
        for fn in ("hit_table.csv", "hit_table_extra.csv"):
            p = _CALIB / fn
            if not p.is_file():
                continue
            try:
                with p.open(encoding="utf-8-sig") as fh:
                    for r in csv.DictReader(fh):
                        path = (r.get("path") or "").replace("\\", "/")
                        if not path or r.get("pkg") is None or r.get("row") is None:
                            continue
                        try:
                            row = int(r["row"])
                        except (TypeError, ValueError):
                            continue
                        exact.setdefault(path, (r["pkg"], row))
                        by_name.setdefault(path.rsplit("/", 1)[-1], []).append(path)
            except Exception:                               # noqa: BLE001
                continue
        self._calib = (exact, by_name)

    # ── 定位 ────────────────────────────────────────────────
    def _idx(self, con, logical: str, exts):
        if con is None:
            return None
        stem = _strip_ext(logical)
        for e in exts:
            p = stem + e
            try:
                r = con.execute("select pack,row from rows where fid=? limit 1",
                                (_hx(fid_of(p)),)).fetchone()
            except Exception:                               # noqa: BLE001
                return None
            if r:
                return ("pe" if con is self.pe_con else "pc", r[0], int(r[1]))
        return None

    def _idx_exact(self, con, logical: str):
        """按原样路径（含 .atlas/.json 等扩展名）查索引 —— 文本资源走这条。"""
        if con is None:
            return None
        try:
            r = con.execute("select pack,row from rows where fid=? limit 1",
                            (_hx(fid_of(logical)),)).fetchone()
        except Exception:                                   # noqa: BLE001
            return None
        if r:
            return ("pe" if con is self.pe_con else "pc", r[0], int(r[1]))
        return None

    def _calib_hit(self, logical: str):
        if not self._calib:
            return None
        exact, by_name = self._calib
        stem = _strip_ext(logical)
        for e in TEX_EXTS:
            if stem + e in exact:
                pkg, row = exact[stem + e]
                return ("pc", pkg, int(row))
        # 同名兜底：强制同目录（历史坑：跨目录同名会把场景串成边框）
        name = stem.rsplit("/", 1)[-1]
        parent = stem.rsplit("/", 1)[0] if "/" in stem else ""
        for e in (".bc7", ".png", ".jpg"):
            cands = by_name.get(name + e) or []
            if parent:
                same = [c for c in cands if c.rsplit("/", 1)[0] == parent]
                if same:
                    pkg, row = exact[same[0]]
                    return ("pc", pkg, int(row))
                continue
            if len(cands) == 1:
                pkg, row = exact[cands[0]]
                return ("pc", pkg, int(row))
        return None

    def locate(self, logical: str):
        """逻辑路径 → (tag, pack, row)；tag ∈ {pe, pc}。找不到返回 None。"""
        logical = logical.replace("\\", "/").lstrip("/")
        # 1) 原样路径（文本资源 .atlas/.json 以及本身就是 .png 的）
        hit = (self._idx_exact(self.pe_con, logical)
               or self._idx_exact(self.pc_con, logical))
        if hit:
            return hit
        # 2) 剥扩展名后按图片扩展名试
        hit = (self._idx(self.pe_con, logical, PE_EXTS)
               or self._idx(self.pc_con, logical, PC_EXTS)
               or self._calib_hit(logical))
        return hit

    # ── 包文件 ──────────────────────────────────────────────
    def _pack_file(self, tag: str, pack: str):
        if tag == "pe":
            return _PE_PACKS / pack
        for root in _PC_ROOTS:
            p = root / pack
            if p.is_file():
                return p
        return None

    def _iter(self, tag: str, pack: str):
        key = (tag, pack)
        if key in self._pe_pack_cache:
            return self._pe_pack_cache[key]
        path = self._pack_file(tag, pack)
        if path is None or not path.is_file():
            self._pe_pack_cache[key] = []
            return []
        try:
            entries = list(AG.iter_entries(str(path)))
        except Exception:                                   # noqa: BLE001
            entries = []
        self._pe_pack_cache[key] = entries
        return entries

    # ── 取载荷 ──────────────────────────────────────────────
    def payload(self, tag: str, pack: str, row: int):
        for e in self._iter(tag, pack):
            if int(e.get("row", -1)) != int(row):
                continue
            return e.get("payload") or b""
        return None

    def image(self, tag: str, pack: str, row: int):
        """→ PIL.Image(RGBA) | None"""
        data = self.payload(tag, pack, row)
        if not data:
            return None
        try:
            if data.startswith(b"CompBlks"):
                sys.path.insert(0, str(_DET))
                import decoders as DEC                  # noqa: PLC0415
                rgba = DEC.decode_compblks(data)
                if rgba is None:
                    return None
                from PIL import Image                  # noqa: PLC0415
                return Image.fromarray(rgba, "RGBA")
            rec = dict(e=None)
            rec["data"] = data
            if data.startswith(b"\xabKTX"):
                rec["kind"] = "ktx"
                rec["info"] = AG.parse_ktx(data)
            elif data.startswith(b"DDS "):
                rec["kind"] = "dds"
            elif data.startswith(b"\x89PNG"):
                rec["kind"] = "png"
            else:
                return None
            if rec["kind"] == "dds":
                import tempfile                          # noqa: PLC0415
                d = _TOOLS / "02_图文音频渲染/皮肤链与渲染"
                if str(d) not in sys.path:
                    sys.path.insert(0, str(d))
                from dds_rgba_canonical import decode_dds_rgba_u8   # noqa: PLC0415
                with tempfile.NamedTemporaryFile(suffix=".dds", delete=False) as f:
                    f.write(data)
                    tmp = f.name
                rgba, _ = decode_dds_rgba_u8(tmp, verify_oiio=False)
                pathlib.Path(tmp).unlink(missing_ok=True)
                from PIL import Image                    # noqa: PLC0415
                return Image.fromarray(rgba, "RGBA")
            rgba = AG.decode_image(rec)
            if rgba is None:
                return None
            from PIL import Image                        # noqa: PLC0415
            return Image.fromarray(rgba, "RGBA")
        except Exception:                                   # noqa: BLE001
            return None

    # ── 便捷 ────────────────────────────────────────────────
    def fetch_text(self, logical: str):
        hit = self.locate(logical)
        if not hit:
            return None
        data = self.payload(*hit)
        if data is None:
            return None
        for enc in ("utf-8-sig", "utf-8", "latin1"):
            try:
                return data.decode(enc)
            except UnicodeDecodeError:
                continue
        return None

    def fetch_png(self, logical: str, out: pathlib.Path) -> bool:
        hit = self.locate(logical)
        if not hit:
            return False
        im = self.image(*hit)
        if im is None:
            return False
        out.parent.mkdir(parents=True, exist_ok=True)
        im.save(out)
        return True


if __name__ == "__main__":
    R = Resolver()
    for p in ("ui/mingpiankuang_icon/05/img_biankuang_05.png",
              "ui/mingpiankuang_icon/06/img_biankuang_06.png",
              "ui/mingpiankuang_icon/02/img_biankuang_02.png",
              "ui/spine/mingpiankuang/img_biankuang36.atlas",
              "ui/spine/mingpiankuang/img_biankuang39.atlas",
              "ui/spine/touxiang_ani/touxiang_ani_02.png"):
        print("%-52s -> %s" % (p, R.locate(p)))
