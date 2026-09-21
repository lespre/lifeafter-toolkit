# -*- coding: utf-8 -*-
"""把**实机截图**按皮肤 ID 归档，并生成 Wiki 用的图片清单。

为什么需要它：客户端里没有"皮肤展示图"这一静态资源（图鉴那张是 `skin_*_mvp_*.gim`
模型实时渲染的）。所以展示图的唯一来源 = 实机截图。本工具负责：
  1. 扫 `E:\\la拆包项目\\03拆包产物\\skin_shots\\`（根目录）里的图片
  2. 从文件名里认皮肤 ID（如 1110184）或皮肤名（如 星火永传）→ 对到图鉴板条目
  3. 复制归位到 `已归档/<id>_<名字>.<ext>`（**原图保留，不删不改**）
  4. 写 `data/exports/skin_shot_manifest.json`（id → 文件/尺寸/sha256；认不出的进 unmatched）

用法：
    python tools/attach_skin_shots.py            # 归档 + 出清单
    python tools/attach_skin_shots.py --dry-run  # 只看匹配结果，不复制
    python tools/attach_skin_shots.py --board data/boards/weapon_skin_sfx_text_sources.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOTS_DIR = Path(r"E:\la拆包项目\03拆包产物\skin_shots")
ARCHIVE = SHOTS_DIR / "已归档"
OUT = ROOT / "data" / "exports" / "skin_shot_manifest.json"
DEFAULT_BOARD = "data/boards/weapon_skin_sfx_text_sources.json"
EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
ID_RE = re.compile(r"(11\d{5})")


def _walk_ids(node, acc: set[str]) -> None:
    """递归收集板里出现的 7 位皮肤 ID（容忍不同字段名/层级）。"""
    if isinstance(node, dict):
        for v in node.values():
            _walk_ids(v, acc)
    elif isinstance(node, list):
        for v in node:
            _walk_ids(v, acc)
    elif isinstance(node, str):
        acc.update(ID_RE.findall(node))


def _names(board: dict) -> dict[str, str]:
    """id -> 展示名（用于归档文件名）。"""
    out: dict[str, str] = {}
    for it in board.get("items", []):
        blob = json.dumps(it, ensure_ascii=False)
        ids = ID_RE.findall(blob)
        name = it.get("name") or it.get("display_name") or it.get("title") or ""
        for i in ids:
            if i not in out and name:
                out[i] = str(name)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--board", default=DEFAULT_BOARD)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    board_path = ROOT / a.board
    board = json.loads(board_path.read_text(encoding="utf-8")) if board_path.exists() else {}
    known: set[str] = set()
    _walk_ids(board, known)
    name_of = _names(board)

    files = sorted(p for p in SHOTS_DIR.iterdir() if p.is_file() and p.suffix.lower() in EXTS)
    entries, unmatched = [], []
    for f in files:
        stem = f.stem
        by_id = ID_RE.search(stem)
        sid = by_id.group(1) if by_id and by_id.group(1) in known else None
        if sid is None:
            for i, nm in name_of.items():
                if nm and nm in stem:
                    sid = i
                    break
        if sid is None:
            unmatched.append({"file": f.name, "reason": "文件名里没有可识别的皮肤 ID/名字"})
            continue
        try:
            from PIL import Image
            with Image.open(f) as im:
                w, h = im.size
        except Exception:
            w = h = None
        rec = {"skin_id": sid, "name": name_of.get(sid, ""), "file": f.name,
               "width": w, "height": h,
               "sha256": hashlib.sha256(f.read_bytes()).hexdigest()[:16]}
        if not a.dry_run:
            ARCHIVE.mkdir(parents=True, exist_ok=True)
            dest = ARCHIVE / f"{sid}_{name_of.get(sid,'') or 'shot'}{f.suffix.lower()}"
            if not dest.exists():
                shutil.copy2(f, dest)
            rec["archived"] = str(dest)
        entries.append(rec)

    doc = {"schema": "skin-shot-manifest-v1",
           "generated": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
           "shots_dir": str(SHOTS_DIR), "board": a.board,
           "board_known_ids": len(known), "count": len(entries),
           "entries": entries, "unmatched": unmatched}
    if not a.dry_run:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"shots": len(files), "matched": len(entries), "unmatched": len(unmatched),
                      "dry_run": a.dry_run}, ensure_ascii=False))
    for e in entries[:10]:
        print(f"  {e['skin_id']} {e['name']}  <-  {e['file']}")
    for u in unmatched[:5]:
        print(f"  ? {u['file']}  ({u['reason']})")
    if not a.dry_run:
        print("→", OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
