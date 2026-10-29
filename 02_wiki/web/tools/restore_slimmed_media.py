# -*- coding: utf-8 -*-
"""恢复被「瘦身」删掉的卡片图：MVP 图标 / 异变核芯特技图标。

做法：以当前板数据为主，从旧版本（git 2088b447）里把 _media.images 逐条并回来，
只补「磁盘上确有文件 + 不是男款」的条目，然后把 slimmed 标记去掉。
"""
from __future__ import annotations

import json
import pathlib
import subprocess

WEB = pathlib.Path("E:/la拆包项目/02_wiki/web")
OLD_COMMIT = "2088b447"
BOARDS = ["kill_broadcast", "mutation_core_full"]
MALE_HINT = ("男款", "_nan", "male", "_m.")


def old_json(board: str) -> dict:
    raw = subprocess.run(["git", "show", f"{OLD_COMMIT}:02_wiki/web/data/boards/{board}.json"],
                         cwd=str(WEB.parents[1]), capture_output=True, text=True,
                         encoding="utf-8", errors="replace")
    if raw.returncode != 0:
        raise SystemExit("取旧版失败：%s %s" % (board, raw.stderr[:200]))
    return json.loads(raw.stdout)


def main() -> int:
    for b in BOARDS:
        cur_p = WEB / "data/boards" / (b + ".json")
        cur = json.loads(cur_p.read_text(encoding="utf-8"))
        old = old_json(b)
        old_map = {it.get("id"): it for it in old.get("items", [])}
        added = skipped = 0
        for it in cur.get("items", []):
            o = old_map.get(it.get("id"))
            if not o:
                continue
            have = {im.get("png") for im in ((it.get("_media") or {}).get("images") or [])}
            new_imgs = list((it.get("_media") or {}).get("images") or [])
            for im in ((o.get("_media") or {}).get("images") or []):
                png = im.get("png") or ""
                if not png or png in have:
                    continue
                label = str(im.get("label") or "")
                if any(h in label or h in png for h in MALE_HINT):
                    skipped += 1
                    continue
                if not (WEB / png).is_file():
                    skipped += 1
                    continue
                new_imgs.append(im)
                have.add(png)
                added += 1
            if new_imgs:
                it["_media"] = {**(it.get("_media") or {}), "images": new_imgs,
                                "total": len(new_imgs)}
                it["_media"].pop("slimmed", None)
        cur_p.write_text(json.dumps(cur, ensure_ascii=False, indent=1), encoding="utf-8")
        print("%-22s 补回图 %d 条，跳过 %d 条（男款/文件不存在）" % (b, added, skipped))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
