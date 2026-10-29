import sys
# -*- coding: utf-8 -*-
"""统计时装男图覆盖：已补 / 仍缺，并导出清单。"""
import collections
import json
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import ANALYSIS_ROOT, WEB  # noqa: E402

OUT = pathlib.Path(ANALYSIS_ROOT / "时装男图_清单_20261025.md")


def imgs(i):
    return [x for x in ((i.get("_media") or {}).get("images") or []) if isinstance(x, dict)]


def has_m(i):
    return any("男" in str(x.get("label", "")) for x in imgs(i))


def main() -> int:
    d = json.loads((WEB / "data/boards/fashion_wardrobe.json").read_text(encoding="utf-8"))
    items = d["items"]
    filled = [i for i in items if has_m(i)]
    missing = [i for i in items if imgs(i) and not has_m(i)]
    nopic = [i for i in items if not imgs(i)]
    print("总卡 %d ｜ 有图 %d ｜ 带男图 %d ｜ 有图缺男 %d ｜ 无图 %d"
          % (len(items), len(items) - len(nopic), len(filled), len(missing), len(nopic)))
    key = lambda x: x.get("part_label") or x.get("part") or "未标"
    print("带男图 部位:", collections.Counter(key(x) for x in filled).most_common(6))
    print("缺男图 部位:", collections.Counter(key(x) for x in missing).most_common(6))
    print("带男图 样例:", [x["name"] for x in filled[:8]])
    print("缺男图 样例:", [x["name"] for x in missing[:12]])

    lines = ["# 时装男图清单 2026-10-25", "",
             "总计 %d 卡 ｜ 有图 %d ｜ 带男图 %d ｜ 有图缺男 %d ｜ 完全无图 %d"
             % (len(items), len(items) - len(nopic), len(filled), len(missing), len(nopic)), "",
             "## 已补男图（%d）" % len(filled), ""]
    lines += ["- %s ｜ %s ｜ model %s" % (x["name"], key(x), x.get("model_id")) for x in filled]
    lines += ["", "## 有图但缺男图（%d）" % len(missing), ""]
    lines += ["- %s ｜ %s ｜ model %s" % (x["name"], key(x), x.get("model_id")) for x in missing]
    lines += ["", "## 完全无图（%d）" % len(nopic), ""]
    lines += ["- %s ｜ %s ｜ model %s" % (x["name"], key(x), x.get("model_id")) for x in nopic]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print("清单已写", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
