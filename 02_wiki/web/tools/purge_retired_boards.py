# -*- coding: utf-8 -*-
r"""清理已归档旧板：把 retired 状态的板块从站点移除（文件归档到 _备份归档，policy/导航清引用）。"""
from __future__ import annotations
import sys

import datetime
import json
import pathlib
import shutil

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import WEB  # noqa: E402

ARCH = WEB / "_备份归档" / ("deleted_boards_" + datetime.date.today().strftime("%Y%m%d"))
POL = WEB / "data/publication_policy.json"
TAX = WEB / "data/wiki_taxonomy.json"
STATUSES = ("retired",)


def main() -> int:
    pol = json.loads(POL.read_text(encoding="utf-8"))
    boards = pol["boards"]
    targets = [b for b, v in boards.items() if v.get("publication_status") in STATUSES]
    ARCH.mkdir(parents=True, exist_ok=True)

    moved = []
    for bid in targets:
        for ext in (".json", ".js"):
            f = WEB / "data/boards" / (bid + ext)
            if f.is_file():
                dst = ARCH / f.name
                if dst.exists():
                    dst.unlink()
                shutil.move(str(f), str(dst))
                moved.append(f.name)
        boards.pop(bid, None)

    POL.write_text(json.dumps(pol, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/publication_policy.js").write_text(
        "window.WIKI_PUBLICATION_POLICY = "
        + json.dumps(pol, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")

    tax = json.loads(TAX.read_text(encoding="utf-8"))
    removed_refs = []

    def walk(node):
        if not isinstance(node, dict):
            return
        if isinstance(node.get("boards"), list):
            keep = []
            for b in node["boards"]:
                if b in targets:
                    removed_refs.append(b)
                else:
                    keep.append(b)
            node["boards"] = keep
        for ch in (node.get("children") or []):
            walk(ch)

    for top in tax.get("树", []):
        walk(top)
    TAX.write_text(json.dumps(tax, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/wiki_taxonomy.js").write_text(
        "window.WIKI_TAXONOMY = " + json.dumps(tax, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8")

    # 导航里只剩空壳的节点删掉
    def prune(node):
        if not isinstance(node, dict):
            return None
        node["children"] = [c for c in (prune(ch) or [] for ch in (node.get("children") or [])) if c]
        if not node.get("children") and not node.get("boards") and not node.get("placeholder"):
            return None
        return node

    tax["树"] = [t for t in (prune(x) for x in tax.get("树", [])) if t]
    TAX.write_text(json.dumps(tax, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/wiki_taxonomy.js").write_text(
        "window.WIKI_TAXONOMY = " + json.dumps(tax, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8")

    print("删除 retired 板 %d 个 ｜ 归档文件 %d 个 → %s" % (len(targets), len(moved), ARCH.name))
    print("导航清理引用 %d 处" % len(removed_refs))
    print("剩余 policy:", len(boards), "块")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
