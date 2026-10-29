# -*- coding: utf-8 -*-
"""Spine 资源原始抓取（atlas / json / 贴图页）。

索引来源：01_索引与产物/10_索引/names/fid_to_path_v2.jsonl（path → container + row）
包体来源：E:/mrzh/<container 用 / 替换 \>

与 pe_fetch.export 的区别：pe_fetch 只按图解码，text(.atlas/.json) 取不到；本模块按行取原始 payload。
"""
from __future__ import annotations

import json
import pathlib
import sys

GAME = pathlib.Path(r"E:/mrzh")

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
IDX = PROJ / "01_索引与产物/10_索引/names/fid_to_path_v2.jsonl"

sys.path.insert(0, str(PROJ / "01_索引与产物/10_索引/热更检测"))
import pe_fetch as PE  # noqa: E402

AG = PE.AG

_MAP = None


def load_map() -> dict:
    """path -> (container, row)"""
    global _MAP
    if _MAP is not None:
        return _MAP
    m = {}
    with IDX.open("r", encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            try:
                r = json.loads(line)
            except Exception:
                continue
            p = (r.get("path") or "").replace("\\", "/").lstrip("/")
            if not p:
                continue
            m.setdefault(p, (r.get("container") or "", r.get("row")))
    _MAP = m
    return m


def pack_path(container: str) -> pathlib.Path | None:
    c = (container or "").replace("\\", "/").strip("/")
    if not c:
        return None
    f = GAME / c
    return f if f.is_file() else None


def find(path: str):
    """逻辑路径 → (pack_file, row) 或 None"""
    hit = load_map().get(path.replace("\\", "/").lstrip("/"))
    if not hit:
        return None
    pk = pack_path(hit[0])
    if not pk:
        return None
    return pk, hit[1]


def raw(path: str) -> bytes | None:
    r = find(path)
    if not r:
        return None
    pk, row = r
    for e in AG.iter_entries(str(pk)):
        if e["row"] != row:
            continue
        pl = e.get("payload") or b""
        # 文本类：gpk 里可能是裸文本，也可能是 bin 壳
        if path.lower().endswith((".atlas", ".json")):
            b = pl.lstrip(b"\x00")
            if b[:1] in (b"{", b"\n", b"\r") or b.lower().startswith(b"img"):
                return b
            return pl
        return pl
    return None


def save(path: str, out: pathlib.Path) -> bool:
    """文本三件套落盘（atlas/json）。返回是否成功。"""
    b = raw(path)
    if not b:
        return False
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(b)
    return True


def export_page(logical_base: str, out: pathlib.Path) -> bool:
    """贴图页：交给 pe_fetch（ktx/dds/bc7 → png）。"""
    return PE.export(logical_base, out)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        b = raw(p)
        print(p, "->", (len(b) if b else None), (b[:60] if b else b""))
