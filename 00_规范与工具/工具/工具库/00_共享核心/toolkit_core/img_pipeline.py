# -*- coding: utf-8 -*-
"""统一 2D 配图流水线：按板块给条目补图。

设计原则
--------
* **只认数据里写着的路径**（icon / image_path / resource_path / detail_bg / png 等字段），
  不按名字猜；没有字段就记「无图标字段」，不编路径。
* 取图走 `img_fetch.export`（PE `.ktx` → PC `.bc7` 兜底）。
* 结果落 `assets/img_cache/<board>/<item_id>.png`，并回写 `_media`。
* 每次运行产出覆盖率与缺口原因，便于逐板对账。

用法
----
    from toolkit_core import img_pipeline as IP
    rep = IP.fill_board("avatar_catalog")
    print(rep.summary())

    python la.py img fill avatar_catalog
"""
from __future__ import annotations

import json
import pathlib
from collections import Counter
from dataclasses import dataclass, field

_PKG = pathlib.Path(__file__).resolve()
PROJ = next((u for u in _PKG.parents if (u / "00_规范与工具").is_dir()), _PKG.parents[3])
WEB = PROJ / "02_wiki/web"
BOARDS = WEB / "data/boards"
CACHE = WEB / "assets/img_cache"

PATH_FIELDS = ("icon", "image_path", "resource_path", "detail_bg", "png", "icon_path", "frame_img_path")


@dataclass
class Report:
    board: str
    total: int = 0
    ok: int = 0
    missing: int = 0
    no_field: int = 0
    reasons: Counter = field(default_factory=Counter)
    samples: list = field(default_factory=list)

    def summary(self) -> str:
        return ("%s：%d 条 ｜ 补上 %d ｜ 缺 %d ｜ 无图标字段 %d ｜ 原因 %s"
                % (self.board, self.total, self.ok, self.missing, self.no_field,
                   dict(self.reasons)))


def _looks_like_sheet(path: pathlib.Path) -> bool:
    """导出后自检：宽高比异常 / 尺寸过大 → 多半是图集或零件页，不能当单图用。"""
    try:
        from PIL import Image
        w, h = Image.open(path).size
    except Exception:
        return False
    if h and w / h > 1.8:
        return True
    return max(w, h) > 1500


def _candidates(item: dict) -> list[str]:
    out = []
    for f in PATH_FIELDS:
        v = item.get(f)
        if isinstance(v, str) and v and not v.startswith("assets/"):
            out.append(v)
    for im in (item.get("_media") or {}).get("images") or []:
        base = im.get("base")
        if base:
            out.append(base)
    # 去重保序
    seen, uniq = set(), []
    for c in out:
        c = c.replace("\\", "/")
        for ext in (".png", ".ktx", ".dds", ".bc7", ".jpg"):
            if c.lower().endswith(ext):
                c = c[: -len(ext)]
                break
        if c not in seen:
            seen.add(c)
            uniq.append(c)
    return uniq


def _load_locks(board: str) -> set:
    f = WEB / "data/board_image_locks.json"
    if not f.exists():
        return set()
    try:
        return set((json.loads(f.read_text(encoding="utf-8")).get(board) or []))
    except Exception:
        return set()


def fill_board(board: str, limit: int | None = None, quiet: bool = False) -> Report:
    from . import img_fetch

    p = BOARDS / ("%s.json" % board)
    d = json.loads(p.read_text(encoding="utf-8"))
    items = d.get("items") or []
    rep = Report(board=board, total=len(items))
    outdir = CACHE / board
    outdir.mkdir(parents=True, exist_ok=True)

    locked = _load_locks(board)
    for idx, it in enumerate(items):
        if limit and idx >= limit:
            break
        if str(it.get("id")) in locked:
            rep.ok += 1
            rep.reasons["人工裁切锁定"] += 1
            continue
        cands = _candidates(it)
        if not cands:
            rep.no_field += 1
            rep.missing += 1
            rep.reasons["无图标字段"] += 1
            continue
        dst = outdir / ("%s.png" % it.get("id"))
        if dst.exists() and dst.stat().st_size > 0:
            rep.ok += 1
        else:
            hit = ""
            for c in cands:
                hit = img_fetch.export(c, dst)
                if hit:
                    break
            if hit and _looks_like_sheet(dst):
                add = img_fetch.export(cands[0], dst) if False else ""
                dst.unlink(missing_ok=True)
                rep.missing += 1
                rep.reasons["疑似图集/零件页（需裁切）"] += 1
                if len(rep.samples) < 5:
                    rep.samples.append((it.get("id"), cands[0]))
                continue
            if hit:
                rep.ok += 1
            else:
                rep.missing += 1
                rep.reasons["路径未命中（PE/PC 均无）"] += 1
                if len(rep.samples) < 5:
                    rep.samples.append((it.get("id"), cands[0]))
                continue
        m = it.setdefault("_media", {})
        images = [im for im in (m.get("images") or []) if im.get("label") != "图标"]
        images.insert(0, {"png": str(dst.relative_to(WEB)).replace("\\", "/"), "label": "图标"})
        m["images"] = images
        m["total"] = len(images)

    p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    if not quiet:
        print(rep.summary())
        for s in rep.samples:
            print("   缺图样例", s[0], s[1])
    return rep
