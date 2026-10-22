# -*- coding: utf-8 -*-
r"""PE（安卓测试服）取图器：路径 → (包,行) → PNG，与 pc_fetch.py 对齐。

用法：
  python pe_fetch.py check                     # 图鉴图在 PE 的覆盖率
  python pe_fetch.py resolve <路径>            # 单个路径 → 包/行
  python pe_fetch.py export <路径> <输出.png>   # 解出一张图
"""
from __future__ import annotations

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
IDX = PROJ / "01_索引与产物/30_分析/热更检测/pe_index.sqlite3"
PACKS = PROJ / "01_索引与产物/30_分析/热更检测/pe_packs"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "01_索引与产物/30_分析/热更检测/pe_icon_bind"))
from toolkit_core.path_fid import fid_of  # noqa: E402
from toolkit_core import android_gpk as AG  # noqa: E402

_PE_BIND = PROJ / "01_索引与产物/30_分析/热更检测/pe_icon_bind"
if _PE_BIND.is_dir() and str(_PE_BIND) not in sys.path:
    sys.path.insert(0, str(_PE_BIND))
import decoders as DEC  # noqa: E402

EXTS = (".ktx", ".dds", ".png", ".bc7")


def hx(v) -> str:
    return v if isinstance(v, str) else "%016X" % (v & 0xFFFFFFFFFFFFFFFF)


def con():
    return sqlite3.connect("file:%s?mode=ro" % str(IDX).replace("\\", "/"), uri=True, timeout=20)


def join(base: str, suffix: str) -> str:
    s = suffix or ""
    s = s if s.startswith("_") else ("_" + s if s else "")
    return base if (s and base.endswith(s)) else base + s


def resolve(base: str, suffix: str = "", c=None):
    """返回 (路径, 包, 行) 或 None；依次试扩展名与档位互换。"""
    c = c or con()
    stem = join(base, suffix)
    low = stem.lower()
    for _e in EXTS:                      # 调用方传了带扩展名的路径时先剥掉，避免 .ktx.ktx
        if low.endswith(_e):
            stem = stem[: -len(_e)]
            break
    stems = [stem]
    if stem.endswith("_b"):
        stems.append(stem[:-2] + "_s")
    elif stem.endswith("_s"):
        stems.append(stem[:-2] + "_b")
    for st in stems:
        for e in EXTS:
            p = st + e
            r = c.execute("select pack,row from rows where fid=? limit 1", (hx(fid_of(p)),)).fetchone()
            if r:
                return p, r[0], r[1]
    return None


def export(path: str, out: pathlib.Path) -> bool:
    pack_row = resolve(path)
    if not pack_row:
        return False
    _p, pack, row = pack_row
    for e in AG.iter_entries(str(PACKS / pack)):
        if e["row"] != row:
            continue
        pl = e.get("payload") or b""
        try:
            rgba = DEC.decode_compblks(pl) if pl.startswith(b"CompBlks") else None
            if rgba is None:
                rec = dict(e)
                rec["data"] = pl
                if e.get("kind") == "ktx":
                    rec["info"] = AG.parse_ktx(pl)
                rgba = AG.decode_image(rec)
            from PIL import Image
            out.parent.mkdir(parents=True, exist_ok=True)
            Image.fromarray(rgba, "RGBA").save(out)
            return True
        except Exception:
            return False
    return False


def check() -> None:
    c = con()
    total = hit = 0
    miss = []
    for bid in ("fashion_wardrobe", "vehicle_full", "tactical_chip_full", "mutation_core_full"):
        p = WEB / "data/boards" / (bid + ".json")
        if not p.is_file():
            continue
        for it in json.loads(p.read_text(encoding="utf-8"))["items"]:
            for im in ((it.get("_media") or {}).get("images") or []):
                b = im.get("base")
                if not b:
                    continue
                total += 1
                if resolve(b, im.get("suffix") or "", c):
                    hit += 1
                else:
                    miss.append(b)
    print("PE 图鉴图 %d 张 ｜ 命中 %d ｜ 缺 %d ｜ 覆盖 %.2f%%"
          % (total, hit, len(miss), hit * 100.0 / max(total, 1)))
    if miss:
        print("缺样例:", miss[:5])


def main() -> int:
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        return 2
    if a[0] == "check":
        check()
        return 0
    if a[0] == "resolve" and len(a) > 1:
        print(resolve(a[1]) or "未命中")
        return 0
    if a[0] == "export" and len(a) > 2:
        ok = export(a[1], pathlib.Path(a[2]))
        print("导出成功" if ok else "未命中或解码失败", a[2] if ok else "")
        return 0 if ok else 1
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
