# -*- coding: utf-8 -*-
"""给热更新增时装找 2D 图：按命名规范猜候选 → pc_fetch 解析/导出 → 落 assets/fashion_posters/。

只读 PC 源（PE 没有这批），导出成 PNG，文件名后缀标 _pc。
"""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"))
import pc_fetch  # noqa: E402

WEB = ROOT / "02_wiki/web"
SRC = ROOT / "01_索引与产物/30_分析/pc_hotfix_new_fashion.json"
OUT = WEB / "assets/fashion_posters/pc_hotfix"

PART = {"cloth": "b", "hat": "h", "bag": "bag", "light": "light", "suit": "suit", "face": "face"}


def main() -> int:
    rows = json.loads(SRC.read_text(encoding="utf-8"))
    # 只保留永久款（去掉 -N天），按名字去重
    items = {}
    for r in rows:
        name = str(r.get("name") or "")
        if not name or "-" in name and name.rsplit("-", 1)[-1].endswith("天"):
            continue
        items.setdefault(name, r)

    OUT.mkdir(parents=True, exist_ok=True)
    hit = miss = 0
    report = {}
    for name, r in items.items():
        part = str(r.get("part_type") or "")
        code = PART.get(part)
        model = r.get("model_id")
        if not code or not model:
            miss += 1
            continue
        cands = []
        for g in ("f", "m"):
            for seq in ("001", "002", "003"):
                base = f"ui/item_icon/icon_{code}_{g}_{model}{seq}"
                for suf in ("_b", ""):
                    cands.append(base + suf)
        got = None
        for base in cands:
            dst = OUT / (base.rsplit("/", 1)[-1] + "_pc.png")
            try:
                if pc_fetch.export(base, dst):
                    got = dst
                    break
            except Exception:                            # noqa: BLE001
                continue
        if got:
            hit += 1
            report[name] = str(got.relative_to(WEB))
        else:
            miss += 1
    print("命中 %d ｜ 未命中 %d ｜ 共 %d 套" % (hit, miss, len(items)))
    for k, v in list(report.items())[:12]:
        print("   %-12s %s" % (k, v))
    (ROOT / "01_索引与产物/30_分析/pc_hotfix_new_fashion_imgs.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
