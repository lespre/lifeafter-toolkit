# -*- coding: utf-8 -*-
"""列出仍缺男图的卡（含现有图 base、model、部位），并写清单文件。"""
import json
import pathlib
import re

WEB = pathlib.Path("E:/la拆包项目/02_wiki/web")
OUT = pathlib.Path("E:/la拆包项目/01_索引与产物/30_分析/时装仍缺男图_20261025.md")


def main() -> int:
    d = json.loads((WEB / "data/boards/fashion_wardrobe.json").read_text(encoding="utf-8"))
    miss = []
    for it in d["items"]:
        imgs = [x for x in ((it.get("_media") or {}).get("images") or []) if isinstance(x, dict)]
        if not imgs:
            continue
        if any("男" in str(x.get("label", "")) for x in imgs):
            continue
        bases = [str(x.get("base", "")) for x in imgs]
        miss.append({
            "name": it["name"],
            "part": it.get("part_label") or it.get("part") or "未标",
            "model": it.get("model_id"),
            "grade": it.get("grade_level"),
            "bases": bases,
            "n_img": len(imgs),
        })

    print("仍缺男图 %d 张\n" % len(miss))
    for m in miss:
        print("%-24s ｜ %-6s ｜ model %-6s ｜ 品级 %-3s ｜ 现有图 %s"
              % (m["name"], m["part"], m["model"], m["grade"], ",".join(m["bases"])[:46]))

    lines = ["# 时装仍缺男图（2026-10-25）", "", "共 %d 张" % len(miss), ""]
    lines += ["| 名称 | 部位 | model | 品级 | 现有图 base |", "|---|---|---|---|---|"]
    lines += ["| %s | %s | %s | %s | %s |" % (m["name"], m["part"], m["model"], m["grade"], " / ".join(m["bases"]))
              for m in miss]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print("\n清单已写", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
