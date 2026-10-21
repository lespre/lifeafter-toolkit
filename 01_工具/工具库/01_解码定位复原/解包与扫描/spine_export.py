# -*- coding: utf-8 -*-
"""Spine 三件套导出：.atlas + .json（树里已有）+ 贴图页（PE 源按 .ktx 取）。

用法：
  python spine_export.py --filter mingpiankuang --out <目录>
  python spine_export.py --limit 20            # 试跑
"""
from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import sys

def _project_root() -> pathlib.Path:
    """自动定位项目根：环境变量 LA_ROOT → 向上找 00_治理 与 01_工具。"""
    import os
    env = os.environ.get("LA_ROOT")
    if env:
        return pathlib.Path(env).expanduser().resolve()
    here = pathlib.Path(__file__).resolve()
    for up in here.parents:
        if (up / "00_治理").is_dir() and (up / "01_工具").is_dir():
            return up
    return here.parents[3]



PROJ = _project_root()
TREES = [PROJ / "03_执行/41_还原树"]
DET = PROJ / "03_执行/30_分析/热更检测"
sys.path.insert(0, str(DET))
import pe_fetch as PE  # noqa: E402
import pe_fetch_hires as H  # noqa: E402

OUT_DEFAULT = PROJ / "04_站点/web/assets/spine"
MIN_PAGE = 256


def logical_path(tree_path: pathlib.Path) -> str | None:
    """把还原树路径转成逻辑路径：从 ui/ 或 character/ 开始。"""
    parts = tree_path.as_posix().split("/")
    for i, p in enumerate(parts):
        if p in ("ui", "character", "effect", "model"):
            return "/".join(parts[i:])
    return None


def page_variants(name: str) -> list[str]:
    """页名容错：去掉尾部 _数字 / 换 _b / 用 atlas 主名。"""
    import re
    out = [name]
    stem = name.rsplit(".", 1)[0]
    m = re.match(r"^(.*)_(\d+)$", stem)
    if m:
        out.append(m.group(1))
    out.append(stem + "_b" if not stem.endswith("_b") else stem[:-2])
    out.append(stem + "_s" if not stem.endswith("_s") else stem[:-2])
    seen, uniq = set(), []
    for x in out:
        if x not in seen:
            seen.add(x)
            uniq.append(x)
    return uniq


def atlas_pages(atlas: pathlib.Path) -> list[str]:
    """读取 atlas 头部列出的贴图页文件名。"""
    pages = []
    for line in atlas.read_text(encoding="utf-8", errors="ignore").splitlines():
        s = line.strip()
        if not s:
            if pages:
                break
            continue
        if s.startswith(("size:", "format:", "filter:", "repeat:", "pma:")):
            break
        if s.lower().endswith((".png", ".jpg", ".ktx", ".webp")):
            pages.append(s)
    return pages


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--filter", default="", help="只处理路径含此关键词的 atlas")
    ap.add_argument("--out", default=str(OUT_DEFAULT))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--min-page", type=int, default=MIN_PAGE)
    a = ap.parse_args()

    out_root = pathlib.Path(a.out)
    atlases = []
    for t in TREES:
        atlases.extend(sorted(t.rglob("*.atlas")))
    if a.filter:
        atlases = [p for p in atlases if a.filter in p.as_posix()]
    if a.limit:
        atlases = atlases[: a.limit]
    print("atlas", len(atlases))

    ok = miss = skip = 0
    from PIL import Image
    for at in atlases:
        lp = logical_path(at)
        if not lp:
            skip += 1
            continue
        base_dir = lp.rsplit("/", 1)[0]
        pages = atlas_pages(at)
        if not pages:
            skip += 1
            continue
        dest_dir = out_root / base_dir
        dest_dir.mkdir(parents=True, exist_ok=True)
        got = 0
        for pg in pages:
            stem = pg.rsplit(".", 1)[0]
            lb = None
            for v in page_variants(stem):
                cand = H.candidates(base_dir + "/" + v)
                if cand:
                    lb = base_dir + "/" + v
                    break
            if not lb:
                miss += 1
                continue
            tmp = dest_dir / pg
            if not PE.export(lb, tmp):
                miss += 1
                continue
            try:
                with Image.open(tmp) as im:
                    if min(im.size) < a.min_page:
                        tmp.unlink()
                        skip += 1
                        continue
            except Exception:
                miss += 1
                continue
            got += 1
        if got:
            for ext in (".atlas", ".json"):
                src = at.with_suffix(ext)
                if src.is_file():
                    shutil.copy2(src, dest_dir / src.name)
            ok += 1
    print("整套完成 %d ｜ 贴图缺 %d ｜ 跳过 %d ｜ 输出 %s" % (ok, miss, skip, out_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
