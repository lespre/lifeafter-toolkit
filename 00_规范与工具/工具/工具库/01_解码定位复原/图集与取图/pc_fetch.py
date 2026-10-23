# -*- coding: utf-8 -*-
"""PC 取图器：路径 → PC 落点（索引优先，CSV 兜底）。

PC 与 PE 的差别（实测）：
  · 命名后缀是 .bc7（不是 .ktx/.png）
  · 载荷是 DDS 容器 + BC7_UNORM（dxgi=98）
  · 索引含 gres 热更包，旧 CSV 只覆盖 ui_01..05 基础包

用法：
  python pc_fetch.py resolve <路径>
  python pc_fetch.py export <路径> <输出.png>
  python pc_fetch.py check            # 图鉴覆盖率
"""
from __future__ import annotations

import csv
import json
import pathlib
import sqlite3
import sys


def _project_root() -> pathlib.Path:
    """自动定位项目根：环境变量 LA_ROOT → 向上找 00_规范与工具/治理 与 00_规范与工具/工具。"""
    import os
    env = os.environ.get("LA_ROOT")
    if env:
        return pathlib.Path(env).expanduser().resolve()
    here = pathlib.Path(__file__).resolve()
    for up in here.parents:
        if (up / "00_规范与工具/治理").is_dir() and (up / "00_规范与工具/工具").is_dir():
            return up
    return here.parents[3]


PROJ = _project_root()
WEB = PROJ / "02_wiki/web"
DET = PROJ / "01_索引与产物/30_分析/热更检测"
IDX = DET / "pc_index.sqlite3"
CAL = DET / "pc_fid_calib/hit_table.csv"
EXTRA = DET / "pc_fid_calib/hit_table_extra.csv"

sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core.path_fid import fid_of          # noqa: E402
from toolkit_core import android_gpk as AG        # noqa: E402

EXTS = (".bc7", ".png", ".dds", ".ktx", ".jpg")
PACK_ROOTS = (pathlib.Path(r"E:/mrzh"), pathlib.Path(r"E:/mrzh/res"),
              pathlib.Path(r"E:/mrzh/Documents/gres"))


def hx(v) -> str:
    return v if isinstance(v, str) else "%016X" % (v & 0xFFFFFFFFFFFFFFFF)


def con():
    return sqlite3.connect("file:%s?mode=ro" % str(IDX).replace("\\", "/"), uri=True, timeout=20)


def has_index() -> bool:
    if not IDX.is_file():
        return False
    try:
        c = con()
        return bool(c.execute("select count(*) from rows").fetchone()[0])
    except Exception:
        return False


def _strip_ext(stem: str) -> str:
    low = stem.lower()
    for e in EXTS:
        if low.endswith(e):
            return stem[: -len(e)]
    return stem


def resolve_idx(base: str, suffix: str = "", c=None):
    """索引定位：(路径, 包, 行) 或 None。"""
    if not has_index():
        return None
    c = c or con()
    stem = _strip_ext(base if not suffix else base.rstrip("_") + "_" + suffix.lstrip("_"))
    for e in EXTS:
        p = stem + e
        r = c.execute("select pack,row from rows where fid=? limit 1", (hx(fid_of(p)),)).fetchone()
        if r:
            return p, r[0], r[1]
    return None


def pack_path(pack: str) -> pathlib.Path | None:
    for root in PACK_ROOTS:
        p = root / pack
        if p.is_file():
            return p
    return None


def load_csv() -> tuple[dict, dict]:
    exact, by_name = {}, {}
    for src in (CAL, EXTRA):
        if not src.is_file():
            continue
        with src.open(encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                p = r["path"]
                exact[p] = (r["pkg"], int(r["row"]), r.get("kind"), r.get("dw"), r.get("dh"))
                by_name.setdefault(p.rsplit("/", 1)[-1], []).append(p)
    return exact, by_name


def join_path(base: str, suffix: str) -> str:
    s = suffix or ""
    s = s if s.startswith("_") else ("_" + s if s else "")
    return base if (s and base.endswith(s)) else base + s


def resolve_csv(stem: str, exact: dict, by_name: dict):
    for ext in EXTS:
        if stem + ext in exact:
            return stem + ext, "CSV"
    alt = None
    if stem.endswith("_b"):
        alt = stem[:-2] + "_s"
    elif stem.endswith("_s"):
        alt = stem[:-2] + "_b"
    if alt:
        for ext in EXTS:
            if alt + ext in exact:
                return alt + ext, "CSV档位"
    # ★ 同名兜底必须限定同目录：跨目录同名会把别的资源串进来（实测名片框串成场景截图）
    name = stem.rsplit("/", 1)[-1]
    parent = stem.rsplit("/", 1)[0] if "/" in stem else ""
    for ext in (".bc7", ".png", ".jpg"):
        cands = by_name.get(name + ext) or []
        if parent:
            same_dir = [c for c in cands if c.rsplit("/", 1)[0] == parent]
            if same_dir:
                return same_dir[0], "CSV同名(同目录)"
            continue
        if len(cands) == 1:
            return cands[0], "CSV同名(唯一)"
    return None


def resolve(base: str, suffix: str = ""):
    """统一入口：索引优先 → CSV 兜底。返回 (路径, 包/来源, 行) 或 None。"""
    stem = join_path(base, suffix) if suffix else _strip_ext(base)
    hit = resolve_idx(stem)
    if hit:
        return hit
    exact, by_name = load_csv()
    r = resolve_csv(_strip_ext(stem), exact, by_name)
    if r:
        pkg = exact[r[0]]
        return r[0], pkg[0], pkg[1]
    return None


def export(base: str, out: pathlib.Path) -> bool:
    hit = resolve(base)
    if not hit:
        return False
    path, pack, row = hit
    src = pack_path(pack)
    if not src:
        return False
    for e in AG.iter_entries(str(src)):
        if e["row"] != row:
            continue
        data = e.get("payload") or b""
        rec = dict(e)
        rec["data"] = data
        try:
            if data.startswith(b"\xabKTX"):
                rec["kind"] = "ktx"
                rec["info"] = AG.parse_ktx(data)
            elif data.startswith(b"DDS "):
                rec["kind"] = "dds"
            elif data.startswith(b"\x89PNG"):
                rec["kind"] = "png"
            else:
                return False
            if rec["kind"] == "dds":
                import tempfile
                d = str(PROJ / "00_规范与工具/工具/工具库/02_图文音频渲染/皮肤链与渲染")
                if d not in sys.path:
                    sys.path.insert(0, d)
                from dds_rgba_canonical import decode_dds_rgba_u8
                with tempfile.NamedTemporaryFile(suffix=".dds", delete=False) as f:
                    f.write(data)
                    tmp = f.name
                rgba, _prov = decode_dds_rgba_u8(tmp, verify_oiio=False)
                pathlib.Path(tmp).unlink(missing_ok=True)
            else:
                rgba = AG.decode_image(rec)
            from PIL import Image
            out.parent.mkdir(parents=True, exist_ok=True)
            Image.fromarray(rgba, "RGBA").save(out)
            return True
        except Exception:
            return False
    return False


def check() -> None:
    print("PC 索引 %s" % ("可用" if has_index() else "不可用"))
    total = hit = 0
    miss = []
    for bid in ("avatar_catalog", "fashion_wardrobe", "vehicle_full"):
        p = WEB / "data/boards" / (bid + ".json")
        if not p.is_file():
            continue
        for it in json.loads(p.read_text(encoding="utf-8"))["items"]:
            base = it.get("image_path") or ""
            for im in ((it.get("_media") or {}).get("images") or []):
                base = base or im.get("base") or ""
            if not base:
                continue
            total += 1
            if resolve(base):
                hit += 1
            else:
                miss.append(base)
    print("图鉴图 %d 张 ｜ 命中 %d ｜ 覆盖 %.2f%%" % (total, hit, hit * 100.0 / max(total, 1)))
    print("未命中样例:", miss[:5])


def main() -> int:
    if len(sys.argv) < 2:
        check()
        return 0
    act = sys.argv[1]
    if act == "resolve" and len(sys.argv) > 2:
        r = resolve(sys.argv[2])
        print(r if r else "未命中")
        return 0 if r else 1
    if act == "export" and len(sys.argv) > 3:
        ok = export(sys.argv[2], pathlib.Path(sys.argv[3]))
        print("导出", ok)
        return 0 if ok else 1
    check()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
